# Error Case Studies 5001-5500

- Source model: `configured-llm`
- Cases: `5001` to `5500`

### case_id=5001 FN partial_functionality

- 方法: `run` vs `seeURLConnection`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a text resource from the classpath, builds a string with line separators, and sets it to a GUI component, catching any exception.
- B 摘要: Reads HTML from an HTTP URL connection, builds a string without line separators, and logs it, propagating any exception.
- 静态失败原因: Static BERT/GraphCodeBERT models rely on token overlap and structural patterns; the low Jaccard similarity (0.29) and different surrounding context (GUI vs. logging) caused the model to miss the underlying I/O similarity, classifying it as non-clone.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often tags as clones when two functions share a core I/O pattern (read text line by line) even if sources and sinks differ, as this is considered Type-4 (functionally similar) in their annotation guideline.
- 共享行为: Reads line-oriented text from an input stream；Uses BufferedReader to read lines；Accumulates lines into a StringBuffer/StringBuilder；Closes the BufferedReader after reading
- 行为差异: Source of data: classpath resource vs. HTTP URL；Output: GUI text display vs. logging；Exception handling: silent catch vs. throw；Encoding: explicit UTF-8 vs. default
- 修正建议: Incorporate data flow analysis to capture common stream operations；Use contrastive learning on clone pairs with similar I/O patterns but different I/O sources；Add explicit feature for reading loop idioms (e.g., while((s=br.readLine())!=null))

### case_id=5002 FN benchmark_preference_bias

- 方法: `copyFromFileToFileUsingNIO` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.3`
- 推荐路线: `preference_memory_with_manual_audit`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Copies a file using NIO channels with FileInputStream and FileOutputStream.
- B 摘要: Builds an HTML site for editing by reading XML configuration, transforming with XSLT, and writing multiple pages.
- 静态失败原因: The model correctly identified the lack of semantic equivalence and low token overlap, but BCB's annotation prefers a broader notion of clone that includes file-handling functionality, leading to a false negative from the model's perspective.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may label this as a clone because both methods perform file I/O operations, which could be considered Type-4 (semantic) clones under a very broad interpretation of similarity, despite the vast difference in complexity and purpose.
- 共享行为: Both use FileInputStream/FileOutputStream for file I/O.；Both involve reading from a source and writing to a destination.
- 行为差异: A is a simple utility method; B is a complex, multi-step process.；A copies a single file; B generates many output files.；A uses NIO transfer; B uses character buffers and manual I/O.；B involves XML parsing, XSLT transformation, and string manipulation.
- 修正建议: The model likely should not change its prediction; this pair may be a mislabel in BCB.；If alignment with BCB is desired, incorporate broader structural patterns like 'file read-write' as weak clone indicators, but this may increase false positives.

### case_id=5003 FN benchmark_preference_bias

- 方法: `runScript` vs `getNetworkServersIPs`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Reads a script from a URL and returns its content as a string.
- B 摘要: Fetches server IPs from a URL by parsing lines starting with '!SERVERS' and extracting values.
- 静态失败原因: The low token overlap (0.203) and structural differences caused the model to reject the clone, but BCB's lenient criteria may have expected acceptance of partial similarity.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have considered both as network I/O operations returning data, but the specific parsing logic in B makes them functionally distinct.
- 共享行为: Both open a URL and read data from it.
- 行为差异: Function A reads raw bytes sequentially; Function B reads lines and parses patterns.；Function A returns the entire raw content; Function B returns a filtered vector of IPs.；Function A uses generic exception handling; Function B handles specific exceptions with stack traces.
- 修正建议: Re-evaluate BCB annotation for this pair; consider if partial functionality similarity is sufficient.；Improve model to recognize broader Type-3/Type-4 clones with shared I/O patterns even with different post-processing.

### case_id=5004 FN partial_functionality

- 方法: `doTransfer` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: This method acts as a proxy, forwarding an incoming HTTP request to another URL, transferring both request headers and body, and returning the response.
- B 摘要: This method downloads the content of a fixed URL (http://www.vogella.de) and prints it line by line to the console.
- 静态失败原因: Static BERT models like GraphCodeBERT may rely on token similarity and syntactic structure. The low Jaccard similarity and different method signatures (doTransfer vs main, different parameters) likely caused the model to miss the functional overlap. Additionally, the complex control flow and API usage in function A may have overshadowed the common URL reading behavior.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider them clones because the core functionality of fetching a URL and printing its content is present in both, with function A being a more elaborate version that includes additional features. This fits the broad Type-3/Type-4 category where partial functionality similarity is accepted.
- 共享行为: Both functions open an HTTP connection to a URL and read the response content, printing it to the console.
- 行为差异: Function A reads request parameters, forwards request headers and body, and handles response status codes, while function B only does a simple GET and ignores headers/status.；Function A is designed to be used as a servlet handler (doTransfer), whereas function B is a standalone main method.；Function A supports dynamic URL via request parameter, function B uses a hardcoded URL.；Function A sends output to response output stream in addition to console, function B only prints to console.
- 修正建议: Improve model sensitivity to shared functionality patterns even when code structure differs.；Use dataflow representations that capture the URL opening and reading sequences.；Include examples of broad clones (Type-4) in training data.

### case_id=5005 FP lexical_or_api_overlap

- 方法: `doVersionCheck` vs `getFullScreenUrl`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Checks for a new version of jEdit by downloading a version file and comparing build numbers.
- B 摘要: Extracts a fullscreen URL for a YouTube video by parsing HTML and constructing a video download URL.
- 静态失败原因: The model likely overemphasized the common structural patterns (URL, BufferedReader, while loop, try-catch) and missed the significant differences in purpose and logic. The low token Jaccard suggests the model relied on more abstract representations that still picked up on these shared API usage patterns.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the overall functionality is completely different (version check vs. video URL extraction), despite some superficial structural similarities. The annotation preference for broader clones usually requires at least partial semantic or functional similarity, which is absent here.
- 共享行为: Both open a URL connection and read lines from an input stream.；Both use a while loop to read lines and parse specific prefixes or patterns.；Both handle exceptions with try-catch blocks and have some form of progress indication (cursor or indeterminate progress).
- 行为差异: Function A checks for software version updates; Function B extracts YouTube video download URL.；Function A takes a View parameter and shows dialogs; Function B is an instance method with no parameters and returns a String.；Function A parses lines starting with '.version' and '.build'; Function B searches for 'fullscreenUrl' and then splits parameters.；Function A compares build numbers and shows messages; Function B constructs and returns a URL string.
- 修正建议: Incorporate method name semantics and overall function purpose into the model.；Use contrastive learning to teach the model that similar API usage does not imply semantic equivalence.；Include data flow analysis to differentiate how parsed results are used (e.g., build comparison vs. URL construction).；Leverage documentation or comments to understand intent.

### case_id=5006 FN boilerplate_overlap

- 方法: `moveFile` vs `modifyApplicationMessage`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.7`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a file byte by byte using streams and deletes the original.
- B 摘要: Modifies a specific entry in a properties file by reading, parsing, and writing back.
- 静态失败原因: Static BERT models often rely on lexical overlap and surface-level features; the low token Jaccard (0.126) and different method names likely caused a non-clone prediction, missing the underlying structural similarity in file I/O flow.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may label this as a clone because both functions exhibit a common pattern of file manipulation: reading from an input source and writing to an output destination, using a while loop to process data, which aligns with broad Type-3/Type-4 similarity criteria.
- 共享行为: Both perform file I/O operations (reading one file and writing to another) using streams and while loops；Both close opened streams after use；Both involve conditional logic around reading data
- 行为差异: Function A copies raw bytes; Function B reads lines, parses key-value pairs, and modifies a specific message；Function A deletes the original file; Function B does not delete the original file but may create a new file if not exists；Function A uses a fixed-size buffer; Function B uses character-based reading and writing
- 修正建议: Incorporate control flow graph or dataflow features that capture file I/O patterns；Use fine-grained AST matching for buffer/stream usage patterns；Augment training data with similar file manipulation examples

### case_id=5007 FP lexical_or_api_overlap

- 方法: `import_hints` vs `checkForUpgrade`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a file containing puzzle piece data (position, rotation) and places them as hints on a board.
- B 摘要: Checks for software upgrades by querying a database and remote server, then processes and stores upgrade information while updating the UI.
- 静态失败原因: Static BERT/GraphCodeBERT likely focused on the overlapping API usage (URL, BufferedReader, StringTokenizer) and similar loop structures, but failed to capture the entirely different semantic contexts and data flows. The model overemphasized lexical and structural similarities without understanding the high-level intent.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels functions as non-clones when their overall functionality and domain are completely different, even if they share trivial API usage patterns. The low Jaccard similarity (0.11) also supports a non-clone label.
- 共享行为: Use java.net.URL and java.io.BufferedReader to read data from a URL；Parse input lines using StringTokenizer or split()；Iterate over read data using loops；Handle IOException with try-catch blocks
- 行为差异: A deals with puzzle piece coordinates and hint placement; B deals with software upgrade versioning, licensing, and database/storage operations；A uses a local file or URL for puzzle data; B queries a remote server for upgrade metadata and performs database inserts；A returns boolean success/failure; B is void and manipulates UI components；B includes complex logic for license validation, upgrade type checking, and conditional UI visibility
- 修正建议: Incorporate method names and class context as additional features；Use data flow and dependency analysis to distinguish reading vs. processing purposes；Train on more diverse examples where API usage is decoupled from functional semantics；Apply contrastive learning to emphasize differences despite surface API overlap

### case_id=5008 FP long_range_semantics

- 方法: `readData` vs `testCopyUnknownSize`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `static_summary_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Reads and parses data from string fields and a file to populate sets, maps, and hash tables for Tibetan/Sanskrit processing.
- B 摘要: Tests that ExtraIOUtils.copy correctly copies InputStream to OutputStream when size is unknown (-1).
- 静态失败原因: The static model likely failed due to long-range semantic differences; it may have been misled by the presence of similar keywords like IOException or the general pattern of reading data, but the overall functionality is unrelated.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB labels as non-clone because the functions are from entirely different domains and have no semantic similarity, even under liberal Type-4 interpretation.
- 共享行为: No significant shared behavior.
- 行为差异: A parses structured data from strings and files, B copies bytes from an InputStream to an OutputStream.；A uses StringTokenizer and sets, B uses ByteArrayInputStream/OutputStream and assertions.；A is a private static method for initialization, B is a public test method.
- 修正建议: Incorporate structural information like control flow and data dependencies.；Improve training with more diverse negative pairs from different domains.；Use contrastive learning to better distinguish unique program semantics.

### case_id=5009 FP boilerplate_overlap

- 方法: `readData` vs `doPost`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Parses comma-separated strings into sets and maps for Tibetan script data initialization.
- B 摘要: Handles HTTP POST request to process a multipart form, fetch a web page or URL, and output a mailer.
- 静态失败原因: Likely confused by the presence of similar boilerplate patterns (try-catch, loops, I/O handling) and possibly common API tokens like 'InputStream', 'OutputStream', 'HashSet' leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clones when functions have completely different functionality, despite similar boilerplate like exception handling and loops.
- 共享行为: Both involve reading input data (strings vs HTTP request)；Both use try-catch for exception handling
- 行为差异: readData initializes static data structures; doPost handles HTTP request/response；readData parses local string variables; doPost reads from HTTP request streams；readData has no I/O output; doPost writes to response output stream；Different control flow and final purpose
- 修正建议: Improve model to focus on high-level semantic purpose rather than local lexical patterns；Incorporate data flow or control flow analysis to distinguish initialization from request processing

### case_id=5010 FN boilerplate_overlap

- 方法: `save` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Save method writes file contents to temporary files and then copies them with a package declaration to a target directory.
- B 摘要: Main method downloads a KMZ file from a URL and extracts its zip entries to the current directory.
- 静态失败原因: The static model relied on lexical and syntactic features (low Jaccard similarity, different method names and control flow), and failed to recognize the functional similarity in the file output pattern that BCB annotators deemed significant.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: None
- 共享行为: Both use FileOutputStream to write data；Both involve loops that process multiple data items
- 行为差异: A works with Java source files and adds a package header; B extracts zip entries；A uses both byte and character streams; B uses buffered streams and zip streams；A creates a directory structure; B does not；A reads from ArrayList and FileReader; B reads from URL and ZipInputStream
- 修正建议: Train on more examples that distinguish boilerplate similarity from true semantic clones；Incorporate data flow or control flow analyses to identify read-write patterns；Use method-level embeddings that capture both structure and purpose

### case_id=5011 FP boilerplate_overlap

- 方法: `issueCommandToServer` vs `loadURL`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Sends a command via HTTP POST to a server and returns the server response as a string.
- B 摘要: Loads a URL with optional basic authentication, writes the content line by line to a temporary file, and updates a status label with file size.
- 静态失败原因: The static model likely over-weighted the common boilerplate code (URLConnection, BufferedReader, InputStreamReader readLine) while missing the distinct control flow and purpose, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels clones as Type-3 (near miss) or Type-4 (semantic) only if there is substantial functional similarity; here, the core functionality (command dispatch vs file download) is unrelated despite shared HTTP boilerplate.
- 共享行为: Both open a URLConnection and read from its input stream line by line.；Both use BufferedReader and InputStreamReader for reading.
- 行为差异: Function A uses HTTP POST with request parameters; Function B uses HTTP GET with optional basic authentication.；Function A writes to the output stream and returns the response; Function B writes to a file and does not return a value.；Function B creates a temporary file, updates a UI label, and prints to console; Function A does not.；Function B handles authentication credentials; Function A does not.
- 修正建议: Incorporate dataflow analysis to distinguish between output stream writing and file writing.；Add attention to method return types and overall control flow (e.g., presence of authentication, file creation).；Use contrastive learning to emphasize functional differences over lexical overlap.

### case_id=5012 FP boilerplate_overlap

- 方法: `readData` vs `copyParseFileToCodeFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Initializes multiple sets and maps by parsing comma-separated strings, with validation and insertion into data structures for Tibetan transliteration.
- B 摘要: Copies content from one file to another using byte streams.
- 静态失败原因: The model may have been misled by the presence of common boilerplate constructs (e.g., while loop, read/write operations) or an unrelated embedding similarity, despite low Jaccard overlap.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would not label this as clone due to vastly different functionality, low token overlap, and different algorithmic intent.
- 共享行为: Both use loops and basic Java constructs.；Both have void return type.
- 行为差异: A parses strings and populates collections; B performs file I/O.；A uses StringTokenizer; B uses FileInputStream/FileOutputStream.；A has complex conditional logic (switch, if-else); B is a simple copy loop.；A manipulates multiple global sets/maps; B has no state modification beyond file copy.
- 修正建议: Improve training data to include more varied negative pairs with low token overlap but high functional divergence.；Enhance model sensitivity to overall program structure and data flow beyond local patterns.；Use graph-based representations to capture long-range dependencies and differentiate initialization from I/O.

### case_id=5013 FN partial_functionality

- 方法: `copyOverWarFile` vs `getFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a .war file from a local directory to the app data directory and extracts it.
- B 摘要: Downloads a WSDL file from a URL, modifies its endpoint attribute, and saves it to a temporary location.
- 静态失败原因: The model relied heavily on lexical overlap (token Jaccard 0.15) and method name similarity, which missed the functional commonality of file transfer operations due to different domain-specific terms (war vs wsdl, local vs remote).
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB annotators likely considered these Type-4 clones because both functions involve downloading or copying a file from a source to a destination with similar low-level I/O operations, despite differences in source type and additional processing.
- 共享行为: Check if a source file exists or list files；Create a new file if needed；Read from an input stream (file or URL) and write to an output stream；Use try-catch for exception handling and log messages
- 行为差异: Source: local directory vs. remote URL；File type: .war vs. .wsdl；Additional processing: extract vs. modify XML；Return type: void vs. String
- 修正建议: Train on structural representations (e.g., ASTs, data flow graphs) to capture functional patterns beyond vocabulary.；Use contrastive learning to emphasize similar behaviors despite different surface forms.

### case_id=5014 FN partial_functionality

- 方法: `main` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Tests StraightStreamReader by writing bytes to a file and reading them back with various buffered read methods.
- B 摘要: Builds a site for editing by reading XML and other files, transforming them, and writing output.
- 静态失败原因: Static BERT models may over-rely on token overlap (FileInputStream, char buffer, loops, exceptions) and miss the semantic divergence in overall program logic and data flow.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider them clones due to shared low-level file reading/writing patterns and use of buffers, despite different overall purposes, as a broad Type-4 similarity.
- 共享行为: Both involve file I/O operations (reading/writing).；Both use character buffers and loops to process data.；Both handle exceptions (IOException).
- 行为差异: Function A is a self-contained test for a specific reader; function B is a complex site generator.；A deals with byte-level data; B deals with strings and XML/HTML content.；A writes a single file and then reads it multiple times; B reads many files and writes one output per page.
- 修正建议: Improve model to capture global control flow and data dependencies.；Use contrastive learning with more diverse negative examples to distinguish low-level API reuse from semantic equivalence.

### case_id=5015 FN benchmark_preference_bias

- 方法: `copyFile` vs `doGet`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.6`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Copies a file from source to destination using a byte buffer.
- B 摘要: Handles an HTTP GET request to retrieve and render a page, with caching, authorization, and error handling.
- 静态失败原因: Static BERT/GraphCodeBERT correctly predicted non-clone due to low token overlap (Jaccard=0.053) and no structural similarity; the functions are semantically unrelated.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may label this as a clone under a very broad Type-4 interpretation, considering both functions involve file I/O (copyFile directly, doGet indirectly via caching) and stream operations, despite vast differences in purpose and complexity.
- 共享行为: Both involve reading from an input source and writing to an output destination using streams.
- 行为差异: copyFile is purely file I/O with no control flow beyond copying; doGet is a servlet with complex control flow including request handling, page retrieval, user authentication, caching, and response writing.；copyFile uses a simple 1024-byte buffer; doGet uses Writer and FileWriter for caching.；copyFile throws IOException; doGet throws ServletException and handles multiple exception types.；copyFile has no user interaction; doGet interacts with HTTP request/response and user permissions.
- 修正建议: Re-evaluate BCB annotation for this pair; it may be a false positive clone label.；If using BCB as ground truth, models should be trained to recognize such broadly similar functions, but it may harm precision.

### case_id=5016 FP lexical_or_api_overlap

- 方法: `populateResources` vs `downloadModel`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Populates local resources by reading template files and saving images with properties from JAR resources.
- B 摘要: Downloads an RDF model from a given URL over HTTP and returns it.
- 静态失败原因: Static BERT likely over-relied on lexical/syntactic overlaps (e.g., InputStream, try-catch, exception types) and missed the semantic differences in core logic (loop vs single download, local vs remote, saving vs returning).
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels this as non-clone because the functions have completely different intents and no functional overlap despite some shared boilerplate patterns.
- 共享行为: Both use InputStream for reading data；Both handle MalformedURLException and IOException in try-catch blocks；Both involve URL handling (though one is local resources, other is HTTP)
- 行为差异: A populates local resources and saves them; B downloads a remote model and returns it；A iterates over multiple templates and images; B handles a single URL；A saves data to database; B returns the model object；A uses local classpath resources; B uses HTTP connection with custom headers
- 修正建议: Train model to focus on core operations (e.g., loop bodies, return types) rather than boilerplate；Incorporate dataflow analysis to distinguish I/O sources and destinations；Enhance with type-aware embeddings for libraries (e.g., Model vs Resource/Image)

### case_id=5017 FP boilerplate_overlap

- 方法: `main` vs `copyFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Generates adapter classes from a Prolog file by parsing, processing with visitors, and writing output JAR.
- B 摘要: Copies a file from source to destination using NIO FileChannels.
- 静态失败原因: Static model likely overestimated lexical overlap from common tokens (File, try, catch, IOException) and ignored the vast semantic difference in purpose and logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would consider them non-clones because they have no overlapping functionality or similar structural patterns beyond generic file handling.
- 共享行为: Both involve file I/O operations；Both use try-catch or try-finally for resource management；Both create File objects
- 行为差异: Function A is a main method with complex business logic (parsing, code generation), while B is a simple utility copy；Function A processes multiple files and writes a JAR, B copies a single file；Function A uses many specialized classes (Parser, Visitor, ClassWriter), B uses only standard NIO；Function A has user interaction and command-line argument parsing, B does not
- 修正建议: Enhance model with control-flow and data-flow features to distinguish I/O boilerplate from core logic；Use contrastive learning to better separate methods with similar lexical but different semantic purpose

### case_id=5018 FP boilerplate_overlap

- 方法: `readTwitterFead` vs `addQDInformation`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a Twitter feed from a hardcoded URL using HttpClient and returns the content as a string.
- B 摘要: Updates internal QD information by reading a local file or downloading from a URL, parsing lines with specific prefixes.
- 静态失败原因: Static BERT models like GraphCodeBERT may overemphasize surface-level token overlaps (e.g., 'BufferedReader', 'while', 'try-catch', 'HttpClient'/'URL') and structural patterns, ignoring the distinct business logic and data processing steps.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels non-clones when core functionality differs significantly, despite similar I/O boilerplate. The essential semantics are unrelated, so BCB marks as non-clone.
- 共享行为: Both use BufferedReader to read lines from an input stream.；Both handle HTTP connections or file I/O with try-catch blocks.；Both involve while loops reading lines until null.
- 行为差异: Different purpose: fetching Twitter feed vs. updating QD information.；Different data sources: hardcoded URL vs. conditional local file or URL.；Different parsing: simple append vs. complex conditional parsing of line prefixes.
- 修正建议: Incorporate data flow analysis to differentiate between I/O setup and core logic.；Use contrastive learning to penalize similarity in boilerplate code when semantics diverge.；Enhance training with examples where shared I/O patterns exist but functionality differs.

### case_id=5019 FN partial_functionality

- 方法: `compressWithZip` vs `modifyApplicationMessage`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Compresses a list of files into a ZIP archive by reading each file and writing it to the archive.
- B 摘要: Modifies or adds a key-value pair in a locale-specific properties file, optionally creating the file from a template.
- 静态失败原因: Static BERT/GraphCodeBERT models rely on token overlap and control flow similarity; the low Jaccard and different domain-specific tokens (zip vs. properties) caused it to miss the supposed broad file-processing similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB might consider both as file manipulation utilities that follow a pattern: open file, read, process, write, close. This broad categorization could lead to a Type-4 clone label.
- 共享行为: Both involve file reading and writing operations；Both handle I/O exceptions；Both use loop constructs to process data
- 行为差异: One compresses files into a ZIP, the other edits a properties file；One works with binary data, the other with text；One processes multiple files, the other processes a single file；One creates a new archive, the other modifies an existing file
- 修正建议: Improve model's ability to recognize high-level functional categories beyond token overlap；Use code summarization or documentation to infer purpose

### case_id=5020 FP boilerplate_overlap

- 方法: `read` vs `getTicketsForQueue`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a skeleton file, splits into sections by '---', and validates section count.
- B 摘要: Retrieves open tickets for a queue via HTTP request, parses ticket IDs from response, and fetches each ticket.
- 静态失败原因: Static BERT models may over-rely on token overlap (e.g., 'BufferedReader', 'readLine', 'startsWith', exception handling) which is common boilerplate, ignoring the wider context and functional purpose.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB annotates functional clones; these functions have completely different purposes (file parsing vs. REST API query), so BCB would label them non-clones.
- 共享行为: Both use BufferedReader to read text line by line.；Both check each line using startsWith.；Both handle exceptions and use try-catch-finally for I/O resources.
- 行为差异: A reads from a local resource file; B makes HTTP requests to a remote server.；A splits lines into sections based on a delimiter; B parses ticket IDs from lines.；A validates expected number of sections; B iterates over ticket IDs to fetch individual tickets.；A throws generic Exception; B returns List<RTTicket> or null.
- 修正建议: Train on more diverse non-clone pairs with similar boilerplate but different semantics.；Incorporate dataflow or control flow analysis to differentiate structural patterns.；Use contrastive learning to penalize matches based solely on common API sequences.

### case_id=5021 FN boilerplate_overlap

- 方法: `doVersionCheck` vs `register`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Performs a version check by connecting to a URL and comparing version strings, displaying messages to the user.
- B 摘要: Registers a user by connecting to a phpBB forum URL, parsing the response to set the user's forum ID, persisting the user, and sending a confirmation email.
- 静态失败原因: The static BERT model likely captured the overall semantic difference and output non-clone. However, BCB's label is based on a broader notion of similarity that includes common utility patterns. The model failed because it could not recognize this boilerplate overlap as sufficient for clone classification, and it may have been overly strict due to training on more semantically aligned pairs.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB annotators may have considered these clones due to the shared pattern of connecting to a URL and reading lines, which is a recognizable boilerplate. In BCB, clones can be labeled based on partial functional similarity or shared sub-behaviors.
- 共享行为: Both open a URL connection and read line-by-line using BufferedReader；Both handle IOException
- 行为差异: Different purpose: version check vs user registration；Different output: void vs boolean；Different input: View vs Object；Different logic after reading: version comparison vs setting forum ID
- 修正建议: Incorporate a measure of structural commonality, such as AST-based or graph-based patterns, to capture shared boilerplate.；Use a broader training set that includes Type-3/Type-4 clones with utility code overlap.；Adjust the similarity threshold to accept partial functional similarity as in BCB annotations.

### case_id=5022 FN partial_functionality

- 方法: `main` vs `addQDInformation`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Main method that sends a POST request to RenRen API with preset parameters and prints the response.
- B 摘要: Private method that reads QD information from a local file or a URL, parses lines to update project info.
- 静态失败原因: Static BERT models rely on token embeddings and structural features. The low token Jaccard and very different method names and domain-specific constants likely led the model to deem them dissimilar. The model may have failed to capture the abstract shared pattern of network reading due to lexical differences. Also, the functional scope differs greatly: one is a main method, the other is a private method with conditional logic.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: The annotator may have considered both as performing network I/O (URL opening and line reading) as the core functionality, despite different purposes and details. BCB often treats partial functionality clones as clones if the shared behavior is significant enough.
- 共享行为: Both open a URL and read lines using BufferedReader
- 行为差异: A sends a POST request with hardcoded parameters, while B reads from a file or URL (GET-like)；A prints all response lines without parsing, whereas B parses specific line prefixes ('pg ', 'pt ') and updates data structures；A is a main method with no return, B updates internal fields and has side effects；A uses specific RenRen API constants, B uses file paths and a URL base
- 修正建议: Improve the model's ability to recognize structural patterns (e.g., URL opening, line-reading loop) even when surrounding code differs；Incorporate explicit API-call or I/O operation detection to group functions that perform similar resource access；Use data-flow analysis to capture the sequence of operations (URL creation, stream opening, reading) as a common template

### case_id=5023 FN lexical_or_api_overlap

- 方法: `getFile` vs `addToArchive`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Downloads a WSDL file from a URL, optionally modifies the endpoint in the XML, and saves the file to a temporary location, returning the file path.
- B 摘要: Adds an entry from an input stream to a zip archive, returning a URL for the entry within the pod.
- 静态失败原因: The static BERT model heavily relies on lexical and syntactic overlap, which is extremely low (Jaccard=0.069). It cannot infer the high-level functional similarity due to completely different token sets and control flow.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may broadly classify both as 'resource management' functions that acquire, process, and store external resources, despite vastly different specific tasks.
- 共享行为: Both involve reading from an I/O stream and writing to a storage destination (file or zip).；Both return a location (file path or URL) of the stored resource.；Both handle I/O exceptions.
- 行为差异: A performs XML parsing and attribute modification, while B does not process the data.；A downloads from a URL, while B takes an already open InputStream.；A uses NIO channels for file transfer, while B uses IOUtils.copy.；A has complex file existence checks and renaming, while B directly writes to ZipOutputStream.
- 修正建议: Use graph-based code representations that capture data and control dependencies.；Incorporate functional semantics through program analysis or contrastive learning on tasks.；Train on datasets with more diverse functional patterns to reduce reliance on surface forms.

### case_id=5024 FN benchmark_preference_bias

- 方法: `doTransfer` vs `downloadURLtoString`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `preference_memory_with_manual_audit`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: A servlet method that acts as an HTTP proxy, forwarding request headers and body to a remote URL, reading the response, and writing it to the client or sending an error.
- B 摘要: Reads content from a URL line by line and returns it as a String.
- 静态失败原因: Static BERT/GraphCodeBERT likely failed due to low token overlap (Jaccard 0.134) and significant structural and semantic differences. The model may have focused on the differing control flows and APIs, missing the common subset of URL reading behavior that the human annotator considered sufficient for clone labeling.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might consider them clones because both involve reading content from a URL via HTTP, despite the vast difference in scope and functionality. The broad Type-4 similarity (both perform URL data retrieval) may have led to a positive label.
- 共享行为: Both open a URL connection and read data from it.；Both handle IO operations with streams/buffers.
- 行为差异: Function A forwards HTTP headers and request body, sets request method, handles response status codes, and writes response to servlet output stream; Function B simply downloads and returns string.；Function A includes error handling with try-catch and sends error responses; Function B throws IOException and does not handle HTTP details.；Function A is more complex and multi-step; Function B is straightforward and single-purpose.
- 修正建议: Incorporate task-specific knowledge that data retrieval functions can be partial clones even if they differ in surrounding logic.；Use contrastive learning with broader clone definitions that allow partial functionality similarity.；Enrich training data with examples where the shared substring is small but the core operation is similar.

### case_id=5025 FN benchmark_preference_bias

- 方法: `copyResource` vs `convert`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Copies a resource from a URL or file path to a destination file by reading and writing bytes.
- B 摘要: Parses a DICOM file, validates and modifies metadata, and writes it out, potentially with pixel data manipulation.
- 静态失败原因: The static model likely failed due to low lexical overlap (Jaccard 0.1278) and different structures, but possibly captured common tokens like 'input', 'output', 'read', 'write', leading it to underestimate the semantic gap.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have considered both as 'resource/file conversion' tasks, or they may have applied a broad Type-4 category of 'stream copy', though the functional difference is substantial.
- 共享行为: Both read from an input stream and write to an output stream.；Both close the input and output streams after use.
- 行为差异: Function A is a simple byte copy; function B involves complex DICOM parsing, metadata injection, and pixel data handling.；Function B has many conditional checks and logging; function A has none.；Function A uses URL.openStream() if source is a URL; function B only handles files.；Function B writes DICOM tags and group lengths; function A just writes raw bytes.
- 修正建议: Increase diversity of non-clone pairs with similar file I/O patterns but very different domain logic.；Use contrastive learning with hard negatives that share stream handling but differ in core semantics.；Incorporate data flow or API call sequences to distinguish simple copy from complex transformation.

### case_id=5026 FP partial_functionality

- 方法: `readData` vs `addRecord`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Reads data from string constants and a file to populate various sets and maps used for Tibetan transliteration processing.
- B 摘要: Adds a record to a data store by copying an input stream to a file identified by its digest.
- 静态失败原因: Static models like GraphCodeBERT may be misled by the presence of file I/O patterns and exception handling, which occur in both functions, and by the truncation of function A which may obscure its true purpose. The low token Jaccard should have been a clue, but the model might have overgeneralized on the I/O template.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB typically labels non-clone when functions have entirely different functionality despite superficial I/O similarities. Here, the purposes are completely different (initialization vs. storage), so likely non-clone.
- 共享行为: Both use file I/O operations.；Both handle exceptions like IOException.
- 行为差异: Function A parses structured data from strings and a file into sets/maps, while B copies raw bytes to a file.；A is about building lookup tables, B is about content-addressable storage.；A uses StringTokenizer and manual parsing, B uses IOUtils.copyLarge and MessageDigest.；A has extensive initialization of multiple sets, B returns a DataRecord object.
- 修正建议: Improve training data to include more diverse I/O operations with distinct semantics.；Use data flow analysis to capture the purpose of data (e.g., building lookup vs storing).；Model should pay attention to the return type and method visibility.

### case_id=5027 FP lexical_or_api_overlap

- 方法: `getJSONData` vs `downloadModel`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.85`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches JSON data from a given URL using HttpClient and parses it into JSONObject.
- B 摘要: Downloads an RDF model from a given URL using URLConnection and loads it into a Model object.
- 静态失败原因: Static BERT models may over-rely on lexical and structural similarities such as try-catch blocks, InputStream usage, URL handling, and common variable names, failing to capture functional semantics.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels this as non-clone because the functions have fundamentally different domains (JSON vs RDF) and different return types and error handling, despite both being URL fetch operations.
- 共享行为: Both retrieve data from a URL via HTTP；Both use exception handling for network errors；Both read input stream from the connection
- 行为差异: Return type: JSONObject vs Model；HTTP client: Apache HttpClient vs Java URLConnection；Error handling: returns null vs throws RuntimeException；Purpose: JSON parsing vs RDF model loading
- 修正建议: Incorporate dataflow analysis to distinguish different return types and error propagation；Use more fine-grained functional labels or task-specific training；Add supervision on method-level purpose via documentation or method names

### case_id=5028 FN benchmark_preference_bias

- 方法: `main` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Tests StraightStreamReader by writing bytes to a file and reading them in multiple ways, checking for correctness.
- B 摘要: Retrieves a resource via URL, caches it locally, and returns a FileInputStream, with caching logic.
- 静态失败原因: The model correctly predicted non-clone (0) because the token Jaccard is low (0.17) and the structural patterns differ significantly. However, BCB labeled it as clone (1) due to preference for partial functionality similarity.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as clone due to both functions involving file I/O (read/write) and byte-level operations, which could be considered broad Type-3/Type-4 similarity despite overall different purposes.
- 共享行为: Both perform file I/O operations using FileInputStream and FileOutputStream；Both handle exceptions；Both involve reading/writing bytes
- 行为差异: A is a test harness with specific byte sequence checks; B is a caching proxy for remote resources；A writes bytes to a file, then reads them back; B reads from a network URL and caches to a file；A uses a custom StraightStreamReader class; B uses standard BufferedInputStream/OutputStream；A prints errors; B prints debug messages and caches results
- 修正建议: Refine BCB annotation guidelines to avoid overgeneralizing file I/O as clone；Use stricter criteria for Type-4 semantic clones；Incorporate broader context to distinguish test harnesses from production caching

### case_id=5029 FN partial_functionality

- 方法: `getResourceAsStream` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Retrieves a resource via URL, caches it locally, and returns an InputStream for the cached file.
- B 摘要: Copies a source file to a destination directory using NIO FileChannel.
- 静态失败原因: Low lexical overlap (token Jaccard 0.12) and different method names/APIs led static BERT to miss the high-level semantic similarity in file I/O logic; the model prioritized token-level differences over shared behavioral patterns.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considers them clones under broad Type-4 because both implement a common file transfer pattern (read from input, write to output) with similar resource management, despite different APIs and complexity.
- 共享行为: Both perform file I/O operations involving reading from a source and writing to a destination.；Both handle resource cleanup in finally blocks or similar exception handling.
- 行为差异: A handles HTTP connection, caching logic, and conditional caching; B is a straightforward file copy.；A returns an InputStream, while B returns void.；A uses BufferedInputStream/OutputStream, B uses FileChannel and transferFrom.
- 修正建议: Use code property graphs to capture structural and data flow similarities.；Train models on type-4 clone pairs to recognize semantically similar but syntactically different code.；Incorporate domain knowledge about common I/O idioms.

### case_id=5030 FN partial_functionality

- 方法: `executeHttpGet` vs `read`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Executes an HTTP GET request and returns the response as a JSONObject.
- B 摘要: Reads data from a file or URL and returns a status code, delegating to another read method.
- 静态失败原因: Static BERT models rely heavily on token overlap and syntactic similarity; here the token Jaccard is very low (0.0566) due to different API calls, variable names, and structures, causing the model to miss the deeper semantic similarity of data retrieval.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often considers Type-3/Type-4 clones where functions perform similar high-level functionality (e.g., retrieving data from a source) even if implementation details differ. Both functions read data from a remote or local source using buffered streams, sharing a common pattern.
- 共享行为: Both perform I/O to read data from an external source.；Both use buffered streams to read input.；Both eventually process the read data (A parses JSON, B delegates to read method).
- 行为差异: A returns a JSONObject, B returns an int status.；A specifically does HTTP GET, B handles both URLs and files.；A uses Apache HttpClient, B uses Java URL and FileInputStream.；A throws Exception, B catches IOException and sets status.
- 修正建议: Use graph-based code representation to capture data flow and API dependencies.；Incorporate documentation or functional summaries as additional features.；Train with augmented data that includes Type-3/Type-4 clones with low token overlap.

### case_id=5031 FN partial_functionality

- 方法: `doTransfer` vs `postRequest`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Forwards an HTTP request from a servlet to a specified URL, copying headers and body, and returns the response.
- B 摘要: Sends an HTTP POST request with URL-encoded form data from a HashMap and returns the response body as a string.
- 静态失败原因: Static BERT models rely on token-level patterns and may not capture the high-level semantic similarity of 'making an HTTP request'. They are sensitive to vocabulary differences (e.g., 'doTransfer' vs 'postRequest', 'HttpServletRequest' vs 'HashMap') and structural differences (e.g., loops, exception handling). The token Jaccard similarity is low (0.21), and embeddings may not align due to different contexts.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as 'HTTP request' functions, ignoring differences in input/output handling, focusing on the common pattern of opening a connection, writing data, and reading response. The broad Type-4 definition might include this pair despite different interfaces and specific operations.
- 共享行为: Both functions open a URL connection to an external resource.；Both set doOutput and doInput to true on the connection.；Both write data to the connection's output stream.；Both read data from the connection's input stream.
- 行为差异: Function A acts as a proxy forwarding the entire request, while B constructs and sends a specific POST request.；Function A copies all request headers and the request body; B encodes a HashMap into URL-encoded parameters.；Function A supports any HTTP method via a parameter; B is hardcoded to POST.；Function A writes the response back to the HttpServletResponse; B returns the response as a String.
- 修正建议: Improve training data to include more examples of partial functionality clones.；Use contrastive learning to better align representations of semantically similar but syntactically different code.；Incorporate data flow or control flow features to capture common patterns like 'open connection, write, read'.；Leverage graph-based models that can abstract over method signatures and variable names.

### case_id=5032 FP boilerplate_overlap

- 方法: `doRawRequest` vs `readUNI`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Sends an HTTP POST request with given data and returns the response body as a string.
- B 摘要: Reads a tab-separated file from a URL and populates a vector with ID-description pairs.
- 静态失败原因: Overlapping tokens (URL, openStream, IOException, readLine) and structural patterns (try-finally, close stream) dominated the representation, masking the core semantic difference.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically annotates functional similarity; these two methods perform completely different tasks despite sharing URL-reading boilerplate.
- 共享行为: Both use java.net.URL to access a remote resource；Both read input from the URL connection；Both handle IO operations and close streams；Both use IOException in error handling
- 行为差异: A sends POST data via OutputStreamWriter; B reads only (no output)；A returns the entire response string; B extracts specific fields from each line；A uses BufferedReader; B uses Scanner with tab delimiter；A expects a service URL; B expects a URL to a TSV file
- 修正建议: Incorporate method name and return type as strong signals；Model dataflow to detect whether output stream is written to；Use control flow to differentiate between reading all lines vs parsing specific fields；Augment training with negative pairs that share boilerplate but differ in functionality

### case_id=5033 FP boilerplate_overlap

- 方法: `perform` vs `toSHA1`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: A web action handler that validates session, processes form parameters, sends an HTTP POST request to a classification service, parses XML response, and stores results in session.
- B 摘要: A utility method that computes SHA-1 hash of an input string and returns the hexadecimal representation.
- 静态失败原因: The static model likely over-relied on superficial similarities such as both having exception handling (try-catch), return statements with null on error, and generic token patterns (e.g., 'String', 'byte[]') while missing the stark difference in overall functionality due to lack of deep semantic understanding or contextual awareness.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the functions have completely different purposes (web controller vs. hashing utility) and share no meaningful common functionality; the token Jaccard similarity is very low (0.055), and BCB annotations generally require substantial behavioral overlap.
- 共享行为: Both use try-catch blocks for exception handling；Both return a value (or null on failure)
- 行为差异: Function A deals with HTTP networking, session management, and XML parsing; Function B is a pure cryptographic hash computation；Function A has complex multi-step business logic; Function B is a single-purpose, self-contained transformation；Function A interacts with external services and state; Function B is stateless and deterministic
- 修正建议: Incorporate method-level context (e.g., class name, package, surrounding code) to capture domain；Use data-flow analysis to understand actual behavior beyond syntactic patterns；Enhance training with more diverse examples of non-clone pairs that share boilerplate

### case_id=5034 FP lexical_or_api_overlap

- 方法: `main` vs `createOutputStream`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: A main method that parses command line arguments, reads a Prolog file, generates adapter classes and JAR output.
- B 摘要: A method that copies entries from a ZIP file to a new ZIP file, skipping 'content.xml', then adds a new 'content.xml' entry and returns a BufferedWriter.
- 静态失败原因: Static BERT or GraphCodeBERT models may over-rely on token-level similarities such as common API calls (File, IOException, try-catch) and loops, ignoring the overall control flow and data dependencies that differentiate the methods.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as a non-clone because the methods have completely different purposes and logic, even though both use I/O streams. The annotation guidelines in BigCloneBench focus on functional similarity, which is absent here.
- 共享行为: Both use file I/O (File, FileInputStream, FileOutputStream).；Both handle exceptions with try-catch blocks.；Both involve creating output streams (OutputStream, BufferedWriter, ZipOutputStream).
- 行为差异: A is a main entry point; B is a helper method with parameters.；A processes Prolog files and generates Java classes; B manipulates ZIP entries.；A has complex control flow with multiple error checks; B has a simpler while loop for copying entries.；A returns void; B returns BufferedWriter.
- 修正建议: Incorporate control-flow or data-flow features into the model.；Use contrastive learning with hard negative pairs that have high API overlap but different semantics.；Add more diverse training examples of non-clones with similar token patterns.

### case_id=5035 FN partial_functionality

- 方法: `loadDefaultSettings` vs `modifyApplicationMessage`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Loads default settings by copying a default properties file from classpath to a specified file.
- B 摘要: Modifies an internationalization message in a locale-specific properties file, copying from English if needed and updating or adding a key-value pair.
- 静态失败原因: Low token overlap and different method signatures; static embeddings fail to capture the abstract pattern of reading resource and writing file across different implementations.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considers both as file I/O operations that read from classpath and write to file, handling configuration/message files, thus a Type-4 partial functionality clone.
- 共享行为: Both read from a classpath resource and write to a file system file.
- 行为差异: A copies an entire resource; B modifies a specific key-value pair.；A uses IOUtils.copy and closeQuietly; B uses manual character reading and writing.；A throws RuntimeException on error; B prints stack trace and does not rethrow.；A deals with binary/stream I/O; B deals with text/character I/O.
- 修正建议: Enhance models to recognize common I/O patterns despite lexical differences.；Incorporate control flow and data flow graphs to identify structural similarities.

### case_id=5036 FP partial_functionality

- 方法: `callService` vs `readScalarpvviewerDocument`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches HTTP response from a URL and returns the complete response as a string, handling network errors.
- B 摘要: Reads a configuration file from a URL, filters and parses lines into XML-like data to update UI components and application state.
- 静态失败原因: The static model likely focused on the common boilerplate (URL opening, BufferedReader, try-catch) and missed the complex parsing logic and drastically different output/side effects, leading to a false positive due to partial functionality overlap.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB labels non-clone because the functions have entirely different purposes: one is a generic HTTP fetcher, the other is a specific configuration parser for a scalar PV viewer. The low token Jaccard (0.1176) confirms minimal lexical overlap beyond the boilerplate URL reading pattern.
- 共享行为: Both use BufferedReader to read lines from an InputStream obtained via URL.openStream()；Both handle IOException
- 行为差异: Function A returns raw concatenated lines; Function B filters lines (ignores comments, stops at marker) and parses them into structured data；Function A sets a single answer field; Function B updates multiple UI components and calls other methods；Function A handles MalformedURLException; Function B does not；Function B uses XmlDataAdaptor for parsing; Function A does no parsing
- 修正建议: Use AST or control-flow features to capture structural differences beyond token sequences；Incorporate data-flow analysis to track how the read data is used；Apply function-level semantic similarity measures focusing on input-output behavior

### case_id=5037 FN lexical_or_api_overlap

- 方法: `getJSONData` vs `addIDs`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.6`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches JSON from a URL and returns a JSONObject.
- B 摘要: Fetches an HTML page from a URL, parses it for metabolite IDs, and updates a PeakListRow object.
- 静态失败原因: Static BERT models rely on token similarity and structural overlap; the low Jaccard index (0.1087) and different method names, control flow, and application logic caused the model to miss the high-level pattern of HTTP data retrieval.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely considers these clones because both implement a common pattern of fetching data from a URL and reading it line by line, despite different parsing goals. This is typical of Type-3/Type-4 clones where the structural skeleton is similar.
- 共享行为: Both perform an HTTP GET request to a URL.；Both read the response line by line using a BufferedReader.
- 行为差异: Different URL construction (direct vs concatenated).；Different parsing logic (JSON vs HTML with specific substring matching).；Different return types (JSONObject vs int score).；Function b has side effects on a PeakListRow object.
- 修正建议: Enhance model with abstract syntax tree (AST) patterns to capture API usage sequences.；Train on more diverse Type-3/Type-4 examples where the core data flow is similar but tokens differ.；Incorporate graph-based representations to model the control flow of HTTP requests and response processing.

### case_id=5038 FN partial_functionality

- 方法: `readRemoteFile` vs `runScript`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a remote file line by line, concatenates lines without newline separators, and returns the result as a string.
- B 摘要: Reads a URL byte by byte, preserves original formatting including newlines, and returns the data as a string, or 'error!' on exception.
- 静态失败原因: Low token overlap (0.24), different method names and API calls (BufferedReader vs BufferedInputStream), and different control flow (line reading vs byte reading) mislead BERT-based models into focusing on surface-level differences rather than functional similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often considers functions with the same high-level purpose (reading a URL and returning its content) as clones, even if implementation details differ (Type-4 clone).
- 共享行为: Both open a URL and read its content；Both return the content as a string；Both handle exceptions during reading
- 行为差异: readRemoteFile uses BufferedReader.readLine() and strips newlines; runScript uses BufferedInputStream.read() and preserves all bytes；readRemoteFile prints IO errors to stdout; runScript returns 'error!' on any exception；readRemoteFile has an explicit EOF flag; runScript uses a sentinel value -1
- 修正建议: Enhance model with dataflow analysis to identify that both functions ultimately read from a URL and produce a string；Incorporate structural abstraction, e.g., normalize stream reading patterns；Use semantic role labeling to capture input-output relations

### case_id=5039 FN boilerplate_overlap

- 方法: `readGeoParserResult` vs `doVersionCheck`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.65`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads geo-parser results from a remote service via XML request, parsing place names and gazetteer entries with retries.
- B 摘要: Checks for a new software version by fetching a version file from a URL, parsing lines for version/build numbers, and displaying messages.
- 静态失败原因: Static BERT models rely on token similarity and structural embedding; low Jaccard (0.14) and different method names/semantics lead to a non-clone prediction, missing the broad pattern similarity.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may consider them clones due to shared boilerplate of URL reading, stream handling, and error handling, which forms a common pattern across different applications.
- 共享行为: Both open a URL connection and read content line by line using BufferedReader.；Both handle IOException with error reporting.；Both parse string content from the stream.
- 行为差异: A sends an XML request and parses XML with multiple nested loops; B reads a simple text file and parses lines with prefix checks.；A retries up to 3 times on failure; B only attempts once.；A returns a collection of tuples; B returns void and shows UI messages.；A uses DocumentHelper for XML parsing; B uses simple string operations.
- 修正建议: Improve model's ability to recognize common I/O and error-handling patterns across different domains.；Use data flow or graph-based features that capture structural similarities beyond token overlap.；Incorporate API usage patterns to identify shared library operations.

### case_id=5040 FN partial_functionality

- 方法: `copyDeleting` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a file from source to destination using a buffer.
- B 摘要: Retrieves a resource as an InputStream with local caching and HTTP support.
- 静态失败原因: Low token Jaccard similarity (0.126) and different method names led the model to focus on surface features, missing the shared I/O read-write loop pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as I/O utility functions that perform stream copying, despite different contexts, fitting a broad Type-3/Type-4 clone definition.
- 共享行为: Both involve reading bytes from an input and writing to an output using a loop.
- 行为差异: Function A copies directly between files; function B handles URLs, caching, and HTTP.；Function A has no error handling; function B has extensive exception handling.；Function A is deterministic; function B has side effects including caching.；Function A returns void; function B returns an InputStream.
- 修正建议: Train model to recognize structural I/O patterns across different method names.；Incorporate data flow analysis to capture data movement from input to output.；Use bytecode or intermediate representation to abstract away surface details.

### case_id=5041 FN lexical_or_api_overlap

- 方法: `postData` vs `register`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.95`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends HTTP POST request with given data to a URL and reads the response, ignoring it.
- B 摘要: Registers a User object by setting properties, making an HTTP GET request to a PHP forum, persisting the user, and sending a confirmation email, returning success status.
- 静态失败原因: Static BERT/GraphCodeBERT models likely picked up on high lexical overlap (e.g., URL, URLConnection, BufferedReader, IOException, while loops) and similar API usage, but failed to capture the vastly different overall semantics and context (generic HTTP POST vs. specific user registration with multiple side effects).
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may label this as a clone because both functions involve opening a URLConnection, reading response, and share similar boilerplate code (URL, BufferedReader, IOException). The core action of making an HTTP request and reading the response is considered sufficient functional similarity for Type-4 broad clones.
- 共享行为: Open a URL connection；Read HTTP response via BufferedReader
- 行为差异: A uses POST with PrintStream, B uses GET without sending data；A does not modify input data, B encodes password, sets reg date, adds authority, computes hash；A has no return value (void), B returns boolean；B includes database persistence and email sending
- 修正建议: Improve representation of control flow and data dependencies beyond surface tokens.；Include task-specific context or functional annotations to distinguish utility functions from domain-specific operations.；Use contrastive learning to push apart pairs with similar API usage but different high-level purpose.

### case_id=5042 FN benchmark_preference_bias

- 方法: `getFile` vs `makeBackup`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies the SOAP address location, and saves it to a temporary file, returning the file path.
- B 摘要: Backs up files from a source directory to a destination directory, creating a subdirectory and copying each file byte by byte.
- 静态失败原因: The static model likely focused on high-level semantic differences (downloading vs. backing up) and the low token overlap (Jaccard 0.147). It failed to capture the underlying common pattern of file I/O operations (stream handling, existence checks) that BCB considered indicative of clone type.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might have labeled these as clones due to both being file manipulation utilities with similar structure: open streams, read/write, close, and handle exceptions. Their broad Type-4 category includes partial functional similarity where both functions ultimately transfer data from a source to a destination, even though the sources and destinations differ (network vs. local directory). However, the specific tasks are very distinct.
- 共享行为: Both perform file I/O operations: reading from a source and writing to a destination.；Both check file or directory existence before proceeding.；Both use System.getProperty to get file separator.；Both handle exceptions (I/O and others) with logging or printing.
- 行为差异: A downloads over HTTP, while B copies local files.；A modifies XML content (DOM manipulation), while B simply copies raw bytes.；A uses NIO channels for efficient transfer, while B uses byte-by-byte reading/writing.；A returns a file path string; B returns void.
- 修正建议: Enhance the model with abstract operation recognition (e.g., I/O operations) across diverse functional contexts.；Use data augmentation to include more varied file manipulation tasks.；Incorporate structural similarity measures that go beyond lexical tokens to capture common control flow patterns.

### case_id=5043 FN benchmark_preference_bias

- 方法: `doGet` vs `forBundle`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Handles HTTP GET request to display a page with permission checks, logging, and caching.
- B 摘要: Manipulates an OSGi bundle by creating a temporary jar with modified templates and reinstalling the plugin.
- 静态失败原因: Static BERT/GraphCodeBERT correctly predicted non-clone, agreeing with strict semantic analysis. The BCB label of 1 appears to be an annotation error or an overly broad interpretation, so the model did not fail in this case.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have considered them clones due to partial functionality such as both involving file handling and error logging, or due to a broad interpretation of Type-3/Type-4 similarity, but the overall semantics are entirely different.
- 共享行为: Both deal with file I/O operations；Both catch exceptions and log errors
- 行为差异: A is a servlet handling web requests; B is a private method for bundle manipulation；A retrieves and renders pages; B creates and installs OSGi plugins；A uses HTTP request/response; B uses ZipOutputStream and bundle APIs；A has extensive permission and caching logic; B focuses on plugin updates
- 修正建议: Re-evaluate BCB annotation for this pair to confirm if they are truly considered clones；If BCB annotation is erroneous, correct the dataset；If BCB intends to capture partial similarity, clarify criteria in benchmark guidelines

### case_id=5044 FP boilerplate_overlap

- 方法: `main` vs `runDynusT`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Parses a Prolog file and generates Java adapter classes and a serialized adapter layer.
- B 摘要: Copies executable and model files to a temporary directory, runs a DynusT traffic simulation, and optionally cleans up.
- 静态失败原因: The static model likely over-emphasized superficial similarities such as file handling (File, IOUtils), exception handling (try/catch), logging (log.info), and loops over arrays. These common Java boilerplate patterns caused a false positive despite vastly different semantics.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled non-clone because the two functions have entirely different purposes and no shared functionality beyond general programming constructs.
- 共享行为: Both perform file I/O operations (reading, writing, copying files).；Both use exception handling with try-catch blocks.；Both involve conditional logic based on parameters (debug flag, cleanUp flag).
- 行为差异: Function A processes Prolog source code and generates Java bytecode and serialized data, while Function B runs an external executable and manages simulation files.；Function A is a static main method with command-line arguments, while Function B is an instance method with a boolean parameter.；Function A uses reflection and class loading, while Function B uses direct file copying and process execution.；Their domains are completely different: code generation vs. traffic simulation execution.
- 修正建议: Enhance model with dataflow and control-flow analysis to distinguish between different types of file operations.；Incorporate type information and method call sequences to better capture domain-specific logic.；Use contrastive learning or structure-aware embeddings to reduce sensitivity to shared keywords.

### case_id=5045 FP lexical_or_api_overlap

- 方法: `actionPerformed` vs `testReadHelloWorldTxt`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Handles UI action commands to set file paths for GRAPHVIZ and IMAGEMAGICK, then processes various other preference settings like country code, date format, font size, look and feel, etc.
- B 摘要: Tests reading a text file from classpath, copying it to a temporary directory, and verifying content retrieval via a FSContentResolver with different path variations.
- 静态失败原因: The static BERT/GraphCodeBERT model likely misclassified due to lexical or API token overlap (e.g., File, String, null, path) despite low Jaccard similarity, perhaps because the model over-generalized from shared tokens and missed the different intents and structures.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would label as not clone because these functions have completely different purposes and domains (UI settings vs unit testing) with no overlapping functional semantics, even at a broad Type-4 level.
- 共享行为: Both use File objects；Both perform null checks
- 行为差异: Function A is an event-driven UI preference saving method; Function B is a unit test with assertions；Function A uses JFileChooser for file selection; Function B loads resources from classpath；Function A modifies global application state; Function B is self-contained and does not modify external state；Function A has multiple conditional branches for different commands; Function B has a linear sequence of operations
- 修正建议: Incorporate method name and class context to disambiguate purpose；Use more comprehensive semantic analysis that captures control flow and data dependencies；Apply domain-aware filtering to avoid false positives from common Java idioms

### case_id=5046 FP boilerplate_overlap

- 方法: `main` vs `main`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Generates adapter classes from a Prolog file using command-line arguments.
- B 摘要: Copies files from a source directory to a destination directory using NIO channels.
- 静态失败原因: The model may have been misled by superficial similarities: both are main methods, both use File, FileChannel, IOException, and loops. The model might have learned that such patterns often indicate clones, but here the semantics differ drastically.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would treat these as non-clones because their overall functionality is completely different; they are not even Type-4 clones.
- 共享行为: Both are public static void main methods；Both perform file I/O operations；Both use try-catch for IOException handling
- 行为差异: Function A generates code and writes JAR files; Function B simply copies files；Function A parses Prolog and uses complex libraries; Function B only copies bytes；Function A has command-line option parsing; Function B expects exactly two arguments
- 修正建议: Improve model's ability to understand long-range dependencies and task-level semantics；Incorporate dataflow analysis to distinguish between different I/O patterns；Add more negative training examples of different main methods

### case_id=5047 FN partial_functionality

- 方法: `modifyApplicationMessage` vs `encodeFileToFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Modifies a localized properties file by replacing or appending a key-value pair.
- B 摘要: Reads a file, base64 encodes it, and writes to an output file.
- 静态失败原因: Static BERT models rely on token overlap (low Jaccard=0.205) and may be misled by boilerplate patterns while missing semantic distinction.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label as clone due to similar file I/O template structure (read loop, write, close streams, error handling), which is common in Type-3 syntactic clones.
- 共享行为: Both perform file I/O with buffered streams；Both use try-catch-finally for exception handling；Both close streams in finally
- 行为差异: A operates on properties files (text, key-value pairs); B encodes arbitrary binary data；A has conditional logic based on locale and message existence; B is a straightforward transformation；Different return types: void vs boolean
- 修正建议: Incorporate data-flow analysis to differentiate transformation logic；Encode domain-specific operation types (e.g., property editing vs encoding)；Use larger context or call graph information

### case_id=5048 FP lexical_or_api_overlap

- 方法: `run` vs `doVersionCheck`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches a map tile from a data source, reads and parses it into a geometry collection, and adds it to a data loader for display.
- B 摘要: Checks for a new version of jEdit by reading a version file from a URL and comparing build numbers, then shows a message if a newer version exists.
- 静态失败原因: Static BERT models often over-rely on lexical and structural overlap (e.g., URL, BufferedReader, IOException, while loop) missing the distinct high-level purposes.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB annotation requires substantial functional similarity; superficial I/O patterns are insufficient for a clone label.
- 共享行为: Both open a URL and read lines from an InputStream using BufferedReader
- 行为差异: Function A processes tile data into geometry; Function B extracts version/build strings；Function A stores results in a data loader; Function B shows UI messages；Function A handles different URL protocols; Function B uses a fixed property URL；Function A includes synchronization and caching logic; Function B does not
- 修正建议: Incorporate data flow analysis to track how inputs are transformed into outputs；Use contrastive learning with functional summaries；Add a control-flow graph or abstract syntax tree component to capture overall intent

### case_id=5049 FP other

- 方法: `copyFile` vs `readData`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Copies a file from source to destination using NIO FileChannel.
- B 摘要: Parses comma-separated string fields into sets and maps to initialize character mappings, possibly reading from a configuration file.
- 静态失败原因: Low token overlap (0.0187) suggests the model may have been misled by common but irrelevant patterns (e.g., exception handling) or failed to capture the distinct high-level purposes.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB annotates as non-clone because the functions perform completely unrelated tasks with no semantic overlap.
- 共享行为: No shared behavior
- 行为差异: Different goals: file copy vs. data parsing/initialization；Different I/O: FileChannel vs. string tokenization and set/map population；Different outputs: file content transferred vs. internal data structures updated
- 修正建议: Ensure model training includes diverse tasks to distinguish file I/O from data parsing.；Use code summarization or semantic role labeling to capture overall intent.

### case_id=5050 FN boilerplate_overlap

- 方法: `copyFile` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a file from a source path to a destination directory using FileChannel transfer.
- B 摘要: Builds a site for editing by processing pages, transforming XML, inserting control files, and writing output files.
- 静态失败原因: Static BERT methods rely on token and structural similarity; the low token Jaccard (0.075) and different method names, parameters, and control flow led to a non-clone prediction, missing the potential file I/O pattern similarity.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB might consider them clones based on the shared file I/O boilerplate (open, read/write, close) and both being file manipulation methods, despite vastly different domain and complexity.
- 共享行为: Both use FileInputStream to read file content.；Both handle IOException and close streams in a finally block.
- 行为差异: A is a simple file copy; B is a complex multi-step site generation with XML transformations and string manipulations.；A uses FileChannel for efficient transfer; B uses standard Reader/Writer and custom file utilities.；A has straightforward error handling; B handles multiple exception types and has conditional logic.
- 修正建议: Incorporate data-flow analysis to capture shared I/O operations beyond lexical overlap.；Use a more fine-grained semantic comparison that weights boilerplate patterns appropriately.

### case_id=5051 FN partial_functionality

- 方法: `modifyApplicationMessage` vs `addToArchive`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Modifies a property in a localized properties file, creating the file from a template if needed.
- B 摘要: Adds a file from an input stream to a ZIP archive and returns its URL.
- 静态失败原因: The extremely low token Jaccard (0.04) and different API usage (Properties vs ZipOutputStream) caused the model to miss any high-level semantic similarity. The model likely relied on surface overlap, which was insufficient.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB might consider both as resource modification utilities (configuration vs. archive) under a broad Type-4 semantic clone category, where the common behavior is 'update a resource with given content'.
- 共享行为: Both operations involve reading input and writing output (streams/files).；Both manipulate a resource identified by a name (message name / filename).
- 行为差异: Function A specifically targets properties files (key=value format) and modifies/inserts a single entry.；Function B adds arbitrary binary data to a ZIP archive.；Function A involves complex text parsing and conditional logic; function B is a simple copy operation.；Function A handles file creation and line-by-line processing; function B only appends to an existing archive.
- 修正建议: Enhance model with dataflow or program dependency analysis to capture abstract manipulation patterns.；Increase training data for cross-API semantic clones.；Use concept-level embeddings for resource manipulation operations.

### case_id=5052 FN benchmark_preference_bias

- 方法: `convert` vs `modifyApplicationMessage`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Converts an ACRNEMA image file to DICOM format, adding UIDs and handling pixel data.
- B 摘要: Modifies a key-value pair in a localized .properties file, creating the file if missing.
- 静态失败原因: The static BERT model correctly predicted non-clone due to low token overlap and distinct API usage; it failed to match the potentially overly broad BCB label.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have considered them clones due to a high-level pattern of reading a source file, performing conditional transformations, and writing output, despite entirely different domains and data structures.
- 共享行为: Both read a file, process its contents, and write to an output file.
- 行为差异: Different file formats: one is image data (PXDATA), the other is text properties.；Different validation logic: checks for UIDs and pixel length vs. checks for existing keys.；Different transformation: inflates 12-bit pixel data vs. replaces/adds a configuration line.
- 修正建议: Review BCB annotations to avoid labeling unrelated file I/O tasks as clones.；Increase threshold for functional similarity in semantic clone detection.

### case_id=5053 FP dataflow_blindspot

- 方法: `executePost` vs `run`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.65`
- 推荐路线: `dynamic_rejection_with_trace`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Executes an HTTP POST request with parameters and returns the response body as a string.
- B 摘要: Reads data from a URL via HTTP GET, parses lines into fields, and notifies listeners on completion or error.
- 静态失败原因: Static models may have overemphasized the shared API usage (URL, HttpURLConnection, BufferedReader) and structural pattern (try-catch-finally) while missing the semantic differences in HTTP method, parameter handling, and post-processing.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 dataflow_trace_and_outputs。
- BCB 偏好解释: BCB typically marks non-clones when functions have different I/O behavior and purpose, despite sharing the general pattern of HTTP reading, as the specific functionality (POST vs GET, parsing vs returning) diverges significantly.
- 共享行为: Both perform HTTP requests (POST vs GET) and read the response line by line.；Both use try-catch-finally blocks for exception handling and resource cleanup.；Both utilize BufferedReader and InputStreamReader to read from an InputStream.
- 行为差异: Function A sends POST request with parameters; Function B uses implicit GET without parameters.；Function A returns the full response string; Function B parses specific lines into fields (version, url, informations).；Function A is a private method; Function B is a Runnable.run() and notifies listeners in finally.；Exception handling: A prints stack trace and returns null; B sets error flags, translates messages, and notifies listeners.
- 修正建议: Incorporate dataflow analysis to track how input parameters and return values are used.；Include method signature and return type information in the representation.；Use models that capture control flow and data dependencies beyond surface syntax.

### case_id=5054 FP lexical_or_api_overlap

- 方法: `getLinksFromURLFast` vs `downloadFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Extracts and returns links from a given URL's HTML page using regex.
- B 摘要: Downloads a file from a given URL to a local destination with progress tracking.
- 静态失败原因: Static BERT/GraphCodeBERT likely over-weighted the common URL handling preamble (URL, openConnection, InputStream) and missed the divergent post-processing logic, due to limited capacity for capturing long-range semantic intent.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would likely label as non-clone because the core functionality is completely different (link extraction vs file download), despite shared URL reading boilerplate.
- 共享行为: Both accept a URL as input；Both open a URLConnection and obtain an InputStream
- 行为差异: Function A extracts links and returns vectors; function B downloads file content to disk and returns boolean.；Function A reads HTML and parses it; function B reads raw bytes and writes to a file.；Function A uses regex for parsing; function B uses buffered streams.；Function A has debugging timers; function B updates a GUI progress bar.
- 修正建议: Incorporate control-flow and data-flow analysis to distinguish read vs. write operations.；Use contrastive learning on examples with similar boilerplate but different core logic.；Add attention to return types and output behavior.

### case_id=5055 FN benchmark_preference_bias

- 方法: `copyResource` vs `send`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Copies a resource from a URL or file to a destination file.
- B 摘要: Sends an email with various headers and attachments, saving a sent message.
- 静态失败原因: Static model correctly predicted non-clone likely because it captured the vast semantic difference despite low token overlap; the prediction is accurate.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have mistakenly labeled as clone due to both functions involving I/O and exception handling, or due to a labeling error in the benchmark.
- 共享行为: Both perform I/O operations；Both handle exceptions
- 行为差异: copyResource copies binary data; send constructs and sends an email；copyResource has no email logic; send has complex email construction and mailing；copyResource uses simple byte loop; send uses JavaMail API and threading
- 修正建议: Review and correct BCB annotation; likely a labeling error；Use more robust semantic models to avoid reliance on biased benchmarks

### case_id=5056 FP lexical_or_api_overlap

- 方法: `readTwitterFead` vs `getFullScreenUrl`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches Twitter timeline from a fixed URL using HttpClient and returns the raw response as a string.
- B 摘要: Given a YouTube URL, extracts video parameters from the page's HTML to construct a download URL.
- 静态失败原因: The static model likely overfit on lexical and structural similarities: both use HttpClient/HttpGet/URLConnection, BufferedReader, try-catch blocks, and return a String. The high overlap in API usage misled the model.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled these as non-clones because they perform distinct functionalities despite sharing boilerplate HTTP-reading code. BCB often treats such pairs as non-clones when the core logic differs significantly.
- 共享行为: Both make HTTP GET requests to retrieve web content.；Both read the response line by line using BufferedReader.；Both return a String as the result.
- 行为差异: Different target URLs and purposes (Twitter timeline vs. YouTube video URL extraction).；Different data extraction logic: A appends all lines; B searches for a specific line containing 'fullscreenUrl' and parses it.；Different error handling: A catches ClientProtocolException and IOException; B catches generic Exception.；Different output: A returns raw page content; B returns a constructed URL.
- 修正建议: Incorporate control flow or data dependency information to capture different extraction logic.；Use method name and domain context (e.g., Twitter vs YouTube) as features.；Train on harder negatives that share API usage but differ in semantics.

### case_id=5057 FP lexical_or_api_overlap

- 方法: `main` vs `copy`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Main method that reads a Prolog file, parses it, generates adapter classes, and writes output files.
- B 摘要: Utility method that copies a file using FileChannel.
- 静态失败原因: The model likely overgeneralized due to overlapping API terms like 'File', 'IOException', and 'try-catch' blocks, despite very low token Jaccard similarity.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would label these as non-clones because they have entirely different functionality and logic; there is no partial or Type-3 similarity.
- 共享行为: Both involve file I/O operations (reading/writing files).
- 行为差异: Function A performs complex parsing, code generation, and class writing; Function B is a simple file copy.；Function A handles command-line arguments, error messages, and multiple steps; Function B is straightforward.；Function A uses many third-party classes (Parser, FactVisitor, ClassWriter, etc.); Function B uses only java.io and java.nio.
- 修正建议: Incorporate structural features like control flow graphs or data flow to distinguish high-level logic.；Weight token overlap more carefully and reduce influence of common API boilerplate.

### case_id=5058 FN benchmark_preference_bias

- 方法: `persist` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Persists a FreeFormConfigurable object to a properties file by copying its input stream to a file output stream.
- B 摘要: Builds a site for editing by reading XML, applying XSLT transformations, processing pages, and writing output files with string manipulations.
- 静态失败原因: Static models like CodeBERT rely on token overlap and structural patterns. The low Jaccard (0.059) and different method signatures/code structures lead to low similarity embedding. The semantic commonality of file I/O is too shallow to overcome lexical differences.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might consider this a clone due to both methods ultimately writing to files (persistence behavior) and being part of a larger framework, but the functional purpose differs significantly.
- 共享行为: Both methods write data to files using output stream or file writing utilities.；Both handle exceptions during file operations.
- 行为差异: Function A is a simple stream copy; B involves complex XML parsing, XSLT transformations, and iterative page processing.；Function A uses IOUtils.copy; B uses custom FileSystem methods and string buffers.；Function A has a single output file; B writes multiple files for each page.；Function A is focused on configuration persistence; B is for generating editable HTML pages.
- 修正建议: Incorporate data flow analysis to detect underlying I/O operations.；Use contrastive learning with hard negatives to distinguish shallow I/O similarity from true semantic clones.；Include method-level documentation or intent analysis.

### case_id=5059 FN partial_functionality

- 方法: `getResourceAsStream` vs `execute`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Retrieves a resource via URL, caches it locally, and returns a FileInputStream to the cached file, with HTTP handling and cache management.
- B 摘要: Saves a HomeMap object to a database, then copies an uploaded image file to a directory using the saved ID as filename, and returns the result of a list method.
- 静态失败原因: The model likely relied on lexical and API token matching, which is very low (Jaccard 0.09). It failed to capture the abstract structural similarity in the file copying pattern due to surrounding diverse context and different method signatures.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label them as clones because they share a common sub-functionality of file copying with similar error handling, which qualifies as partial functionality similarity under Type-4 clone definition.
- 共享行为: Both functions involve reading from a source and writing to a file using FileInputStream/FileOutputStream；Both have try-catch blocks for I/O exceptions；Both perform stream copying operations
- 行为差异: Different sources: network URL (A) vs local file (B)；Different destinations: cache directory (A) vs specific directory (B)；Additional logic in A: HTTP connection handling, caching, cache expiry checks；Additional logic in B: database save operation, different return type
- 修正建议: Use graph-based code representations that capture data flow and I/O operations；Incorporate structural clone detection techniques that normalize variable names；Train on more diverse partial functionality examples

### case_id=5060 FP boilerplate_overlap

- 方法: `readData` vs `copyFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Reads and parses comma-separated strings to populate various sets and maps for Tibetan character processing.
- B 摘要: Copies a file using NIO FileChannel with proper resource management.
- 静态失败原因: Static BERT may have been misled by common boilerplate patterns like exception handling (try-catch) and resource management (closing channels), or by the presence of similar low-level API calls (StringTokenizer, FileChannel) that are actually used in distinct contexts. The high token overlap in the truncated part might also contribute.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clone because the functions perform completely different tasks with no overlapping functionality, even under a broad Type-3/Type-4 interpretation.
- 共享行为: Both handle I/O or resource cleanup (exception handling in readData, try-finally in copyFile).；Both use basic Java constructs like loops and conditionals.
- 行为差异: readData initializes data structures from tokenized strings; copyFile copies file contents.；readData is state-mutating and focuses on parsing; copyFile is a utility function for file transfer.；readData is much longer and more complex; copyFile is short and straightforward.；readData reads from static string fields; copyFile takes File parameters.
- 修正建议: Use contrastive learning with more hard negative examples that share API calls but differ in semantics.；Incorporate structure-aware encoders that capture control-flow and data-flow differences.；Provide explicit training on distinguishing utility functions from initialization logic.

### case_id=5061 FP boilerplate_overlap

- 方法: `copy` vs `readData`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Copies a file from source to destination using FileChannel.transferTo.
- B 摘要: Reads a configuration file, tokenizes comma-separated strings, and populates multiple HashSets and a HashMap.
- 静态失败原因: Static BERT likely over-weighted common I/O boilerplate (try-catch-finally, IOException) and method names implying I/O, ignoring semantic differences in the actual logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would label this as non-clone because there is no functional similarity; the tasks are completely different (file copy vs. data parsing) and token overlap is minimal (0.0487).
- 共享行为: Both involve file I/O operations.；Both handle IOException with try-catch-finally.
- 行为差异: A performs a file copy; B parses and populates data structures.；A returns a File; B returns void.；A uses FileChannel; B uses StringTokenizer and HashMap.；A is short and focused; B is long and complex with multiple loops and conditionals.
- 修正建议: Improve sensitivity to long-range semantics and dataflow.；Use AST-based features to distinguish different I/O patterns.；Downweight common exception handling patterns when they dominate similarity.

### case_id=5062 FP lexical_or_api_overlap

- 方法: `getVersion` vs `wordFrequency`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Gets version string from a remote URL by reading the first line of the response.
- B 摘要: Counts frequency of a word by querying a web service and parsing the response for a pattern.
- 静态失败原因: Static BERT may over-rely on lexical and API surface overlap (URL, BufferedReader, try-catch), ignoring differences in return types, input parameters, and core logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically considers Type-4 (semantically different) as non-clones. The high-level purposes (version retrieval vs word frequency) are distinct, despite sharing common I/O boilerplate.
- 共享行为: Open a URL connection；Read lines via BufferedReader；Handle IO exceptions
- 行为差异: Return type: String vs int；URL: fixed vs constructed with query parameter；Processing: read all lines vs pattern matching and extraction；Exception handling: return null vs print stack trace and return 0
- 修正建议: Incorporate data flow analysis to distinguish different processing pipelines.；Add attention to method signatures and return types.；Use code summarization or intent recognition to capture high-level purpose.

### case_id=5063 FP boilerplate_overlap

- 方法: `handleHandshake` vs `readUNI`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Validates a Minecraft handshake packet by checking username format and authenticating with a session server via HTTP.
- B 摘要: Reads a TSV file from a URL, parses lines to extract IDs and descriptions, and adds them to a vector.
- 静态失败原因: Static BERT/GraphCodeBERT likely overemphasized the shared structural patterns (URL.openStream, try-catch-finally, exception printing) and ignored the distinct high-level intents.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels these as non-clones because they perform vastly different domain-specific tasks despite sharing generic URL-reading boilerplate.
- 共享行为: Open a URL and read input from a stream；Handle exceptions with try-catch and print stack traces；Close the input stream in a finally block
- 行为差异: A handles Minecraft session authentication, while B parses a TSV database file；A sends network packets or shuts down the connection; B populates a vector of strings；A uses BufferedReader and checks for 'ok' response; B uses Scanner and tab delimiters
- 修正建议: Incorporate dataflow or program dependence analysis to differentiate core logic from boilerplate；Augment training data with non-clone pairs that share boilerplate but differ in semantics；Use control-flow-aware embeddings that capture branching and data processing intent

### case_id=5064 FN benchmark_preference_bias

- 方法: `readAndRewrite` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Reads a DICOM image file, parses it, reads pixel data, and writes to another file.
- B 摘要: Configures an Eclipse launch for a NexOpen project by processing POM files, setting Hibernate dialect, and managing reverse engineering files.
- 静态失败原因: The model correctly identified no clone due to very low lexical overlap (Jaccard=0.03) and completely different API usage; the false negative arises from a noisy BCB label.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB likely mislabeled this pair due to superficial similarity in file reading/writing, but the core functionality is entirely unrelated, and BCB's broad criteria still require some functional overlap.
- 共享行为: Both perform file I/O operations and use streams.
- 行为差异: Different domains: medical imaging vs. Eclipse plugin development.；Different purpose: copying image data vs. configuring project launch.；Different libraries and data formats: DICOM vs. Maven/Hibernate.；Different control flow and error handling.
- 修正建议: Review and correct the BCB label for this pair.；Focus on domain-specific functional equivalence rather than generic I/O patterns.

### case_id=5065 FP boilerplate_overlap

- 方法: `handleHandshake` vs `postXml`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Handles Minecraft handshake: validates username, optionally makes an HTTP GET to join server, and sends login or disconnect packet.
- B 摘要: Sends an HTTP POST request with XML data for SOAP calls and returns the response body.
- 静态失败原因: Static models over-emphasize shallow lexical and API usage overlap (URL, BufferedReader, try-catch) without understanding the distinct control flow and domain-specific semantics.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB annotates at function level and labels non-clones when functions serve entirely different purposes, even if they share low-level I/O patterns. Here the domain (Minecraft vs SOAP) and logic differ substantially.
- 共享行为: Both create a URL connection and use BufferedReader to read the response line by line.；Both handle network I/O within a try-catch block.
- 行为差异: handleHandshake uses HTTP GET; postXml uses HTTP POST with XML and SOAP headers.；handleHandshake has conditional logic for username validation and packet sending; postXml is a linear utility returning the raw response.；handleHandshake interacts with Minecraft session state; postXml is generic and stateless.
- 修正建议: Incorporate data-flow or control-flow features to capture high-level intent.；Train with contrastive examples of different functionality sharing API usage.；Use more abstract semantic representations like program dependency graphs.

### case_id=5066 FP boilerplate_overlap

- 方法: `main` vs `extractImage`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: A main function that generates adapter classes from a Prolog file and writes them to a JAR file.
- B 摘要: An image extraction function that processes an image from a file or STDIN, applies scaling/transforms, and writes output.
- 静态失败原因: The static model (e.g., GraphCodeBERT) might have over-relied on shared lexical patterns (e.g., 'File', 'IOException', 'try', 'catch') and ignored the entirely different domains, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the functions have entirely different purposes and domains, despite some superficial structural similarities like try-catch blocks and file I/O.
- 共享行为: Both read input data (file or STDIN) and write output to a file.；Both use try-catch blocks for exception handling.；Both involve File operations and IO streams.
- 行为差异: Function A is a code generation workflow from Prolog, while B processes image data.；A uses many domain-specific classes (PrologParser, FactVisitor, ClassWriter), B uses image processing classes.；A writes a JAR file, B writes an image file.；A has a complex sequence of steps (parsing, visitor, adapter generation), B is simpler (process, scale, write).
- 修正建议: Incorporate type and method signatures more explicitly.；Use contrastive learning to separate different domains.；Add attention to method names and class context.

### case_id=5067 FN benchmark_preference_bias

- 方法: `copyDeleting` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Copies a file from source to destination using a buffer.
- B 摘要: Builds a website for editing by processing multiple pages, reading XML, transforming, and writing output.
- 静态失败原因: Static BERT correctly predicted non-clone due to low token overlap and differing control flow; it did not fail.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have considered superficial file reading/writing as similar, but the overall functionality is completely different.
- 共享行为: Both perform file I/O operations.
- 行为差异: A is a simple file copy; B is a complex multi-step site generation.；A uses FileInputStream/FileOutputStream; B uses custom FileSystem and StringBuffer.；A has no loops; B iterates over pages.
- 修正建议: Re-evaluate BCB annotation; these functions are not clones.

### case_id=5068 FP lexical_or_api_overlap

- 方法: `downloadURLtoString` vs `handleHandshake`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads content from a URL and returns it as a string using BufferedReader.
- B 摘要: Handles a Minecraft handshake packet by validating username and performing server authentication.
- 静态失败原因: Static BERT models may over-rely on token-level similarity from common Java I/O patterns (BufferedReader, InputStreamReader) and surface-level syntactic structures, leading to a false positive despite low overall Jaccard similarity.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels this as non-clone because the functions serve entirely different purposes and have no semantic similarity in their core functionality.
- 共享行为: Both use BufferedReader and InputStreamReader to read from a network stream.；Both involve reading a line of text from an input source.
- 行为差异: downloadURLtoString simply downloads and returns content; handleHandshake performs complex authentication logic.；handleHandshake conditionally sends packets or shuts down the network; downloadURLtoString has no side effects.；The return types differ: String vs void.；The input parameters and overall purpose are completely different.
- 修正建议: Incorporate control-flow and data-flow graphs to capture structural differences.；Use contrastive learning that emphasizes functionality over API usage patterns.；Add explicit modeling of program side effects and return types.

### case_id=5069 FN partial_functionality

- 方法: `getFile` vs `setImg`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies its XML attribute, and saves to temp directory, returning the file path.
- B 摘要: Opens a file chooser to select an image, copies it to an images directory, and sets it as a background image.
- 静态失败原因: The low lexical similarity (0.13) and distinct method names (getFile vs setImg) misled the model to focus on surface tokens rather than the shared file-copying pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: None
- 共享行为: Both perform file I/O operations (read from source, write to destination)；Both check file existence before copying；Both handle exceptions with logging/error messages
- 行为差异: Different sources: URL vs file chooser；Different destinations: temp directory vs images directory；Different post-processing: XML modification vs setting image icon；Different return types: String vs void
- 修正建议: Incorporate structure-based features like data flow graphs or abstract syntax trees to capture file I/O patterns；Add training examples that demonstrate cross-domain file copy clones；Use attention mechanisms that focus on API calls and control flow rather than identifiers

### case_id=5070 FN lexical_or_api_overlap

- 方法: `read` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.3`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a camera log from a URL, parses each line into a CameraLogRecord object, handles parsing errors, sorts records, and logs progress.
- B 摘要: Constructs HTTP POST parameters for a RenRen API call, sends the request, reads the response line by line, and prints each line to console.
- 静态失败原因: The model likely relied on deep semantic understanding and low lexical overlap, leading it to classify the pair as non-clone, whereas BCB's annotation policy accepts broad functional similarity, resulting in a false negative.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may consider these clones under a very broad Type-4/partial functional similarity criterion, where both functions perform I/O reading from a URL and processing lines, despite completely different domain logic and output.
- 共享行为: Both use BufferedReader and InputStreamReader to read from a URL connection.；Both have a readLine loop to process each line.；Both handle IOException.
- 行为差异: A parses lines into domain-specific objects (CameraLogRecord) and adds to a list; B builds and sends an HTTP POST request.；A sorts the collection of records; B prints raw response lines.；A reads from a camera log URL; B constructs parameters and uses an API URL.；A uses a finally block to close the reader; B does not explicitly close (though it's inside a try-with-resources? Actually it's not, but B has no explicit close).
- 修正建议: Augment training data with more Type-4 examples to teach the model loose functional similarity.；Incorporate network I/O patterns as a discriminative feature.

### case_id=5071 FN benchmark_preference_bias

- 方法: `modifyApplicationMessage` vs `forBundle`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Reads a properties file for a given locale, updates or appends a message value.
- B 摘要: Finds .vm files in a bundle, packages them into a new jar, and installs it as a plugin.
- 静态失败原因: Static BERT likely correctly predicted non-clone due to low lexical overlap (Jaccard 0.13) and distinct method names.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might have considered both as resource modification tasks due to file reading/writing and resource management, but the domain and goal are entirely different.
- 共享行为: File I/O operations；Exception handling with printStackTrace
- 行为差异: A modifies properties files; B deploys plugins；A uses properties and reader/writer; B uses zip streams and bundle manipulation；A works on locale-specific files; B works on OSGi bundles；A has no dependency on plugins; B depends on BundleManipulator and plugin framework
- 修正建议: Review BCB annotation for this pair to correct mislabel；Consider adding domain context to avoid false positives

### case_id=5072 FN partial_functionality

- 方法: `getEncoding` vs `loadExistingAntlibs`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a URL's content to detect character encoding from HTTP headers or the body.
- B 摘要: Loads antlib definitions from classpath resources by reading lines from a URL.
- 静态失败原因: Static BERT/GraphCodeBERT models rely on token-level semantics and method names, which are very different here (getEncoding vs loadExistingAntlibs). The low token Jaccard (0.177) and distinct method names likely caused the model to predict non-clone. Also, the models may not capture the high-level structural similarity in loop patterns and I/O handling, focusing instead on distinct API calls and variable names.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: Despite different high-level purposes, both functions follow a similar structural pattern: open a connection/get a resource, create a BufferedReader, read lines in a loop, process each line, and close resources. BCB often annotates such structural clones as Type-3. Additionally, both can be seen as 'resource configuration parsers', which may be considered semantically similar at a high level.
- 共享行为: Both functions open a URL connection or resource and read lines using BufferedReader.；Both functions iterate over lines and process each line.；Both functions close the reader in a finally block or after usage.；Both functions handle IOException (though differently).
- 行为差异: Function A extracts encoding from headers and body; Function B loads Ant library URIs from lines.；Function A returns a String (encoding); Function B calls loadAntLib for each line and returns void.；Function A has a fallback to STANDARDENCODING; Function B throws RuntimeException on failure.；Function A opens a URLConnection from a URL; Function B gets URLs from classLoader or system resources.
- 修正建议: Train on more diverse clone types, especially Type-3 and Type-4 with structural similarity.；Incorporate structural code embeddings that capture loop and I/O patterns.；Use data augmentation to include pairs with low token similarity but high structural overlap.

### case_id=5073 FN benchmark_preference_bias

- 方法: `saveAttachmentBody` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Saves an email attachment body to a file and updates the database with its size and content URI.
- B 摘要: Builds a site for editing by processing multiple pages through XML transformation and file I/O operations.
- 静态失败原因: Static BERT correctly identified the low lexical overlap (Jaccard 0.058) and distinct code structures, leading to a non-clone prediction. The BCB label may be a false positive, so the static model did not fail but rather aligned with typical clone detection expectations.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled them as clones due to both performing file-based data processing, possibly under a broad category like 'file I/O with transformation', but this interpretation is weak and likely an annotation error.
- 共享行为: Both involve file input/output operations；Both use InputStream and FileOutputStream；Both handle exceptions
- 行为差异: Different purpose: attaching saving vs. site generation；Different input types and parameters；Different logic: simple copy vs. complex transformation with DOM and string replacement；Different output: single file with DB update vs. multiple output files
- 修正建议: Re-evaluate the BCB annotation for this pair to confirm if they truly represent a clone；Consider using more fine-grained clone detection that respects domain-specific functionality

### case_id=5074 FN benchmark_preference_bias

- 方法: `addIDs` vs `read`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `preference_memory_with_manual_audit`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Adds metabolite IDs to a PeakListRow by parsing HTML from a Golm database URL.
- B 摘要: Reads a file or URL into an input stream and returns a status code.
- 静态失败原因: Static BERT models rely on token and structure similarity; the low Jaccard (0.137) and different code patterns led to a non-clone prediction, missing the broader functional similarity.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider both as clones because they are both methods that fetch data from external sources (URL) and return an integer, representing a similar high-level task in the metabolomics domain.
- 共享行为: Both open a URL connection and read data；Both return an integer (score/status)；Both handle IOException
- 行为差异: A parses HTML and sets multiple fields on a row object; B only reads raw bytes and delegates；A uses BufferedReader; B uses BufferedInputStream；A has complex conditional parsing for multiple ID types; B has no content processing
- 修正建议: Add more data augmentation with varied implementations of similar tasks；Incorporate functional semantics via documentation or method names；Use heuristics to capture domain-specific patterns like network I/O and status return

### case_id=5075 FN partial_functionality

- 方法: `copyResource` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a single resource from a URL or file to a destination file using byte streams.
- B 摘要: Reads multiple input files line by line and writes them to an output file using Scanner and PrintWriter.
- 静态失败原因: Static BERT models rely on token overlap and structural similarity; low Jaccard similarity (0.175) and different API usage (URL/FileInputStream vs Scanner/PrintWriter) cause failure to capture behavioral similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this as a clone because both functions share the high-level purpose of copying data from input(s) to an output file, fitting Type-4 (similar functionality) despite implementation differences.
- 共享行为: Both copy data from input sources to an output file
- 行为差异: A copies a single source, B copies multiple sources；A reads bytes, B reads lines；A uses InputStream/OutputStream, B uses Scanner/PrintWriter；Different exception handling and method signatures
- 修正建议: Use data-flow or program-dependence graphs to capture source-sink relations；Incorporate functional similarity via code summarization or behavioral embeddings；Apply contrastive learning to align different implementations of same behavior

### case_id=5076 FN benchmark_preference_bias

- 方法: `execute` vs `doGet`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Processes class files to inject monitoring methods and calculates code size statistics.
- B 摘要: Handles HTTP GET requests to retrieve and render a portal page with caching and logging.
- 静态失败原因: Static BERT models likely focused on low token overlap and different API usage, correctly identifying non-clone despite BCB label.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have annotated as clone due to coarse-grained similarity in structure (loops, exception handling, logging) and both being 'execute' methods that process collections, but the domains are completely different.
- 共享行为: Both contain try-catch error handling；Both iterate over collections；Both perform logging
- 行为差异: Function A modifies bytecode; Function B generates HTML；A uses ClassReader/ClassWriter; B uses HttpServletRequest/Response；A deals with file I/O for .class files; B handles HTTP parameters and page rendering
- 修正建议: Increase threshold for token similarity；Add domain-specific filters；Incorporate data-flow analysis to distinguish bytecode manipulation from HTTP handling

### case_id=5077 FN boilerplate_overlap

- 方法: `getResourceAsStream` vs `encodeFileToFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches a resource from a URL, caches it locally, and returns an InputStream for the cached file.
- B 摘要: Reads a file, Base64 encodes it, and writes the encoded data to another file, returning a success flag.
- 静态失败原因: Static models rely on lexical and API token overlap; the low Jaccard (0.224) and different method names/APIs led to a non-clone prediction, missing the abstract I/O loop pattern shared by both.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may consider them clones because both implement a variant of the 'copy stream' pattern with similar boilerplate (try-catch-finally, stream management, loop for data transfer), despite different sources, sinks, and transformations.
- 共享行为: Both use buffered streams to read from an input source and write to an output sink；Both have try-catch-finally blocks for exception handling and stream cleanup；Both use a while loop to transfer data
- 行为差异: A fetches from a URL and caches; B reads a local file and encodes；A returns an InputStream; B returns a boolean；A copies byte-by-byte; B uses a buffer and reads in chunks；A uses URLConnection and caching logic; B uses Base64 encoding
- 修正建议: Train models to recognize abstract data-flow patterns (e.g., input->process->output) independent of specific API calls；Incorporate control-flow and data-dependency graphs to capture structural similarity；Use contrastive learning on pairs with similar I/O patterns but different domain-specific operations

### case_id=5078 FN boilerplate_overlap

- 方法: `getFile` vs `Converter`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies the 'wsdlsoap:address' endpoint in the XML, and saves it to a temporary file, returning the file location.
- B 摘要: Reads a file encoded in SJIS and writes it out encoded in UTF8, performing encoding conversion.
- 静态失败原因: Low token Jaccard similarity (0.1049) and different method names (getFile vs Converter) lead static models to miss the shared I/O boilerplate. The models focus on exact token and AST matches rather than high-level data flow.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may have labeled these as clones due to both implementing file read-write operations with stream handling, despite differing transformation purposes. The manual annotator might have considered them Type-3 or Type-4 clones because of similar I/O patterns.
- 共享行为: Both open an input stream and read data；Both write data to an output stream；Both handle IOExceptions；Both involve file I/O operations
- 行为差异: Function_a downloads from a network URL, while function_b reads a local file；Function_a checks file existence and modifies XML, while function_b does not；Function_a uses NIO channels, while function_b uses BufferedReader/BufferedWriter；Function_a has multiple exception types, function_b only catches IOException
- 修正建议: Train models to recognize common I/O patterns beyond exact token matches；Incorporate data flow and dependence graphs to capture stream read/write behavior；Add explicit positive examples of construction-like file conversion vs download-and-modify

### case_id=5079 FP lexical_or_api_overlap

- 方法: `handleHandshake` vs `getJSONData`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Handles Minecraft handshake by validating username and performing an HTTP GET to session server to verify session and send login packet.
- B 摘要: Fetches JSON data from a given URL via HTTP GET using HttpClient and parses it into a JSONObject.
- 静态失败原因: Static BERT likely focused on the lexical and API-level overlap (e.g., BufferedReader, InputStreamReader, URL, HttpGet) and similar exception handling, missing the deeper semantic differences in the purpose and processing of the response.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: Although both methods contain HTTP GET using similar APIs, the overall functionality differs significantly. BCB typically annotates non-clones when the methods have distinct domain-specific logic and output, as the partial overlap in HTTP request pattern is not sufficient for clone classification.
- 共享行为: Both perform an HTTP GET request.；Both read the response using BufferedReader line by line.；Both handle exceptions with printStackTrace.
- 行为差异: Code A has additional username validation and conditional logic.；Code A interacts with a fixed Minecraft session server; Code B takes arbitrary URL.；Code A reads only the first line and checks for 'ok'; Code B reads all lines and parses JSON.；Code A sends a Packet1Login or shuts down network; Code B returns a JSONObject.
- 修正建议: Incorporate data-flow analysis to trace how the response is used after reading.；Use context from the containing class or method name to disambiguate domain.；Train on examples with similar syntactic structures but different semantics.

### case_id=5080 FN long_range_semantics

- 方法: `doVersionCheck` vs `seeURLConnection`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a version-check URL, parses lines for build numbers, and calls an overloaded version check method, with cursor and error handling.
- B 摘要: Reads content from a hardcoded URL, concatenates all lines into a string, and logs it, without UI interaction.
- 静态失败原因: Static BERT likely focused on low token overlap (Jaccard 0.209), different method names and arguments, and distinct string literals, missing the underlying structural similarity of URL reading and line processing.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may consider both as URL reading tasks with similar loop structure and stream handling, thus labeling them as Type-3/4 clones despite different business logic.
- 共享行为: Both open a URL and read lines using BufferedReader；Both use while loop to read lines until null；Both close the BufferedReader after reading
- 行为差异: A parses lines for version info (prefixes .build, .stablebuild); B simply concatenates all lines；A shows/hides wait cursor on a View; B has no UI interaction；A handles IOException with an error dialog; B throws Exception without specific error handling；A uses a property-based URL; B uses a hardcoded URL
- 修正建议: Enhance model with control flow and data flow analysis to capture structural patterns like open-read-close；Incorporate API usage graphs to recognize common patterns (e.g., URL.openStream, BufferedReader)；Add training examples that are structurally similar but functionally different to reduce false negatives in BCB-style evaluation

### case_id=5081 FP boilerplate_overlap

- 方法: `loadURL` vs `parse`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Loads a URL with optional basic authentication, reads response line by line, writes to a temporary file, and updates a status label with file size.
- B 摘要: Parses a data file or URL into a DataSet object, handling headers, types, delimiters, and scientific notation.
- 静态失败原因: Static BERT/GraphCodeBERT may overemphasize lexical similarity of common I/O patterns (e.g., URLConnection, BufferedReader) and ignore the high-level semantic differences in control flow and data manipulation.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels non-clone because the functions accomplish fundamentally different tasks (download vs. parse) despite sharing I/O boilerplate. The core logic and purpose are distinct.
- 共享行为: Both open a URL and read data line by line using BufferedReader.；Both may write output (A to file, B to DataSet).；Both use exception handling and I/O streams.
- 行为差异: A only downloads and writes raw content; B parses structured data with tokenization and type conversion.；A includes UI update for progress; B does not.；A uses Base64 authentication; B does not.；B handles multiple delimiters, headers, and scientific notation; A does not.
- 修正建议: Incorporate method name and return type as features.；Use contrastive learning to distinguish similar API usage with different intents.；Add data flow analysis to capture how data is transformed (raw vs. parsed).

### case_id=5082 FP lexical_or_api_overlap

- 方法: `transformByMD5` vs `perform`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Computes MD5 hash of a password string and returns the hex-encoded digest.
- B 摘要: Processes an HTTP request in a Struts action, validates session, builds XML, sends HTTP POST to a URL, parses XML response, and stores results in session.
- 静态失败原因: The model likely focused on superficial lexical similarities (e.g., both use StringBuffer, getBytes, and try-catch blocks) and overlooked the vastly different control flow and external dependencies, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: None
- 共享行为: Both use StringBuffer to accumulate string output；Both include try-catch error handling
- 行为差异: Function A performs only MD5 hashing; Function B performs complex web request handling；Function A has no network I/O; Function B involves HTTP connection and XML parsing；Function A is single-purpose; Function B involves multiple steps including session management and parameter extraction
- 修正建议: Improve training with more negative examples that have lexical overlap but different semantics；Incorporate control flow and data flow analysis to distinguish trivial boilerplate from core functionality；Use longer-range dependency modeling to capture the overall purpose of each function

### case_id=5083 FN benchmark_preference_bias

- 方法: `doGet` vs `convert`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Handles HTTP GET requests to retrieve and display a page after validating user access and caching.
- B 摘要: Converts an ACRNEMA stream file to DICOM format by parsing pixel data and adding UIDs.
- 静态失败原因: The static BERT model correctly identified non-clone because the functions have very different method signatures, API calls, and domains; the BCB label may be an annotation error or based on a different interpretation of clone criteria.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might have mislabeled due to both containing conditional checks and early returns, but the overall functionality is entirely different; possibly an annotation error.
- 共享行为: Both perform conditional checks and early returns on failure conditions
- 行为差异: Function A is a web servlet handler dealing with HTTP requests, user permissions, and page rendering; Function B is a file format converter for medical images.；Function A interacts with a portal and user sessions; Function B reads and writes binary file streams.；Function A uses logging extensively; Function B prints to console.；Function A has complex caching logic; Function B has pixel data inflation.
- 修正建议: Improve the training data by removing mislabeled pairs.；Use fine-grained similarity metrics that consider specific functionality rather than generic patterns.

### case_id=5084 FP boilerplate_overlap

- 方法: `sendPost` vs `getFullScreenUrl`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Sends an HTTP POST request to a given URL with a parameter string and returns the response body.
- B 摘要: Retrieves a YouTube video's full screen URL by parsing the HTML response from a given YouTube URL.
- 静态失败原因: Static BERT or GraphCodeBERT may have been misled by the shared boilerplate code (URL, HttpURLConnection, BufferedReader, try-catch) and the similar structural skeleton, causing it to overlook the distinct semantic intents and different processing logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: None
- 共享行为: Both perform HTTP URL connection and read response using BufferedReader；Both handle exceptions by printing error messages
- 行为差异: sendPost performs a POST request with output; getFullScreenUrl performs a GET request without output；sendPost returns the entire response body; getFullScreenUrl extracts a specific parameter from a specific line；getFullScreenUrl includes GUI progress bar and additional parsing logic
- 修正建议: Improve model's ability to differentiate between boilerplate code and core logic, e.g., by focusing on the data processing part after the connection.

### case_id=5085 FP boilerplate_overlap

- 方法: `getLinksFromURLFast` vs `doVersionCheck`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Extracts links and anchor texts from an HTML page given a URL using regular expressions.
- B 摘要: Checks for a newer version of jEdit by reading version and build numbers from a remote file.
- 静态失败原因: The static model likely focused on the common structural pattern: URL opening, BufferedReader, while loop reading lines. It may have missed the semantic difference in what is done with the read data, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this non-clone because the overall functionality is entirely different: one is a link extractor, the other is a version checker. Although they share boilerplate for URL reading, the core logic and purpose diverge completely.
- 共享行为: Both open a URL connection and read lines of text using BufferedReader；Both perform string parsing on the read lines
- 行为差异: Function A returns parsed links/texts; Function B performs version comparison and shows GUI messages；Function A uses regex to match anchor tags; Function B uses line prefix matching；Function A handles relative URLs; Function B handles version strings and build comparisons；Function A returns a Vector array; Function B is void with side effects on GUI
- 修正建议: Improve training data to include more diverse examples where boilerplate is shared but functionality differs；Incorporate control-flow and data-flow analysis to distinguish output/effects；Use contrastive learning to penalize high similarity due to boilerplate only

### case_id=5086 FN benchmark_preference_bias

- 方法: `copyResource` vs `createButtonCopyToClipboard`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.0`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Copies a resource from a URL or file to a destination file.
- B 摘要: Creates a SWT button that copies a report to the clipboard when clicked.
- 静态失败原因: The model likely focused on structural and token-level differences (low Jaccard) and correctly identified no syntactic similarity, thus predicting non-clone. However, BCB's annotation may consider shared copying intent as sufficient for Type-4 clone, which the model missed.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled as clone due to broad 'copy' semantics and potential API level overlap like IOUtils.copyToClipboard vs FileOutputStream.write, but the functionalities are conceptually distinct.
- 共享行为: Both involve copying data to an output destination.
- 行为差异: Different output targets (file vs clipboard)；Different control flow (direct file I/O vs GUI event-driven)；Different context (standalone resource copy vs GUI component initialization)；Error handling present only in A
- 修正建议: Incorporate explicit annotation instructions to distinguish true partial functionality clones from coincidental term overlap.；Use hierarchical task clustering to better capture intent at different abstraction levels.

### case_id=5087 FP boilerplate_overlap

- 方法: `main` vs `main`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `1.0`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: AdapterGenerator main: reads Prolog file, generates adapter JAR with debug option.
- B 摘要: Test main: writes test file and validates StraightStreamReader read operations.
- 静态失败原因: Static BERT/GraphCodeBERT likely over-relied on shared tokens like 'File', 'IOException', 'main', 'System.err/out', and structural patterns (try-catch, loops) without capturing the distinct semantic goals.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB prefers non-clone because the functions have completely different high-level purposes and implementations; only superficial boilerplate is shared.
- 共享行为: Both are main-like entry points using standard input/output and file I/O.；Both use try-catch blocks for IOException.；Both check file existence or validity.
- 行为差异: Function A generates an adapter JAR; Function B tests a stream reader class.；Function A parses Prolog and uses complex class generation; Function B performs simple file read/write loops.；Function A outputs to System.out; Function B outputs to System.err.；Function A uses multiple external libraries; Function B is self-contained.
- 修正建议: Incorporate dataflow or call-graph information to distinguish unrelated tasks.；Use AST-based edit distance or control-flow features that capture high-level intent.；Add training examples where similar boilerplate code has different semantics.

### case_id=5088 FN boilerplate_overlap

- 方法: `getFile` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies the endpoint in the XML, and saves it to a temp directory.
- B 摘要: Reads a log file and writes every Nth line starting with a given token to a new file.
- 静态失败原因: The static model correctly identified the low lexical overlap (Jaccard 0.11) and distinct API usage, leading to a non-clone prediction; the model's embedding likely captured the semantic difference, disagreeing with BCB's broad annotation.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB might consider the common file I/O boilerplate as Type-3 or partial functionality similarity, but the core functionality is entirely different, making this an anomalous clone label.
- 共享行为: Both perform file I/O: open input/output streams, read/write data, close resources.；Both handle IOException with try-catch blocks.
- 行为差异: A downloads from a network URL and manipulates XML content; B reads a local file and filters lines by token.；A uses URL, Document, and Node APIs; B uses BufferedReader and BufferedWriter.；A returns a file path; B writes to a specific output file and exits.
- 修正建议: The static model prediction is reasonable; no fix needed.；If aligning with BCB, consider incorporating patterns of I/O boilerplate as clone indicators, but this may increase false positives.

### case_id=5089 FP boilerplate_overlap

- 方法: `get` vs `getRequestContent`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Opens HTTP connection with custom headers, reads all lines, filters comment lines, decodes each as GameRecord, returns array or null on failure.
- B 摘要: Opens HTTP connection, reads first line only, returns it as string, throws exception on failure.
- 静态失败原因: Static model overweighs lexical overlap in HTTP connection boilerplate and misses the critical difference in loop vs single-line read and data transformation.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this non-clone because despite shared HTTP GET boilerplate, the overall behavior and output type differ significantly; partial functionality similarity is weak.
- 共享行为: Both open HTTP GET connection via HttpURLConnection；Both use BufferedReader to read input stream
- 行为差异: A sets custom request headers (latitude, longitude, count); B does not；A reads all response lines; B reads only first line；A filters lines starting with '#'; B does not；A decodes lines into GameRecord objects; B returns raw string
- 修正建议: Incorporate data flow analysis to track how many lines are read and how they are processed；Use type information of return values (GameRecord[] vs String) to distinguish；Add attention to conditional branches and loops that shape the overall semantics

### case_id=5090 FP lexical_or_api_overlap

- 方法: `getUser` vs `PageLoader`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Loads a user from a DAO or parses a config file to create a User object.
- B 摘要: Constructor that loads a web page's content into a string field.
- 静态失败原因: The model overemphasized the lexical and structural overlap in URL opening and line reading, ignoring the distinct overall functionality and return types.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clones because the functions have entirely different purposes and outputs, despite sharing boilerplate URL reading code.
- 共享行为: Both use URL to open a stream and read with BufferedReader.；Both handle exceptions (A catches, B throws).
- 行为差异: A is a method returning a User; B is a constructor setting a field.；A conditionally reads a config file only if DAO fails; B always reads entire page.；A parses lines into tokens and creates objects; B concatenates lines into a single string.；A saves data to a DAO; B has no analogous operation.
- 修正建议: Incorporate semantic role labeling to distinguish method purpose.；Consider return type and data dependencies.；Increase attention to higher-level control flow and method signatures.

### case_id=5091 FP lexical_or_api_overlap

- 方法: `createHTML` vs `downloadModel`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Builds an HTML page string by loading a CSS resource and appending content based on a page type, including querying a database for dashboard content.
- B 摘要: Downloads an RDF model from a URL using HTTP connection and returns it, handling URL and I/O exceptions.
- 静态失败原因: Static BERT models likely focused on lexical and API-level similarities (URL, InputStream, IOException) and missed the different semantic intents and control flows.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB considers non-clones because the functions have completely different purposes (UI generation vs. model download) and different logic, despite superficial API overlaps.
- 共享行为: Both use InputStream to read data from a URL；Both have try-catch blocks for IOException
- 行为差异: Function A constructs HTML for UI; Function B downloads a data model；Function A uses database queries; Function B uses HTTP connection；Function A returns a String; Function B returns a Model object；Different purpose: presentation vs. data retrieval
- 修正建议: Incorporate control-flow and data-flow analysis to distinguish UI generation from data download；Use method names and more context to capture intent；Add negative sampling with similar APIs but different semantics

### case_id=5092 FN partial_functionality

- 方法: `getFile` vs `transport`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a given URL, optionally modifies an XML endpoint attribute, and returns the local file path.
- B 摘要: Recursively copies files from a source file or directory to a destination directory using NIO channels.
- 静态失败原因: The token Jaccard similarity is low (0.16), method names differ ('getFile' vs 'transport'), and the overall control flow and purpose are different. Static BERT models rely heavily on token overlap and surface-level patterns, missing the underlying shared behavior of NIO channel transfers.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considers both as clones because they share the core functionality of transferring data using NIO FileChannel over files, falling under Type-4 (functional similarity) despite different contexts and additional operations.
- 共享行为: Both use java.nio.channels.FileChannel to transfer bytes between channels.
- 行为差异: Function A downloads from a URL and modifies XML; Function B copies local files recursively.；Function A uses transferFrom; B uses transferTo.；Function A returns a String; B returns void.；Function A includes XML parsing and manipulation; B does not.
- 修正建议: Improve model's ability to recognize abstract dataflow patterns like channel-based I/O.；Incorporate API usage embeddings to capture shared library usage.

### case_id=5093 FN partial_functionality

- 方法: `copy` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.4`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a file from source to destination using FileChannel transfer.
- B 摘要: Retrieves a resource by name with caching, possibly downloading from URL and returning a FileInputStream.
- 静态失败原因: Static BERT/GraphCodeBERT likely focused on the low token overlap and syntactic differences, missing the broad semantic similarity in data copying that BCB annotators considered.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as implementing 'copying data from one location to another' at a high level, and the caching step in B is essentially a file copy, making them partial functionality clones.
- 共享行为: Both involve reading from an input source and writing to an output destination；Both use FileInputStream and FileOutputStream for I/O；Both copy data in a streaming manner
- 行为差异: A is a simple file-to-file copy; B is a resource retrieval with URL resolution, HTTP, and caching；B has complex caching logic and state management; A has none；B returns an InputStream; A has void return；B handles multiple exception scenarios and prints logs; A has minimal error handling
- 修正建议: Incorporate dataflow analysis to detect core copy loops common to both；Train on more diverse partial functionality examples；Use hierarchy-aware embeddings that capture high-level intent

### case_id=5094 FN partial_functionality

- 方法: `main` vs `copyFileTo`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Extracts all entries from a zip file downloaded from a given URL to the current directory.
- B 摘要: Copies a file from the current object's absolute path to a specified destination file using NIO channels.
- 静态失败原因: Token Jaccard similarity is very low (0.085), and the model relies heavily on lexical and surface-level features. The different APIs (ZipInputStream vs FileChannel) and method names obscure the underlying functional similarity in I/O operations.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider them Type-4 clones because both perform a data transfer from a source to a destination, a common I/O pattern that is functionally similar despite different implementations.
- 共享行为: Both involve reading from a source and writing to a destination.；Both close resources after use.；Both handle I/O exceptions.
- 行为差异: A processes multiple entries from a zip archive; B copies a single file.；A uses ZipInputStream and buffered streams; B uses FileChannel.transferFrom.；A decides protocol (file or http) for input; B directly reads from a file.
- 修正建议: Use abstract representations of I/O operations (e.g., read/write patterns).；Incorporate code summarization or intent classification to capture functional similarity.；Augment training data with diverse clones that share a common high-level behavior but differ in API usage.

### case_id=5095 FP boilerplate_overlap

- 方法: `main` vs `copyFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `1.0`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Main method that parses a Prolog file and generates adapter classes, writing them to a JAR.
- B 摘要: Utility method that recursively copies a file or directory from one location to another.
- 静态失败原因: The static model likely overfitted on common Java I/O patterns (FileInputStream, FileOutputStream, IOException) and missed the entirely different high-level functionality.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically annotates based on functional similarity; these functions have no overlapping purpose, so they are definitely non-clones.
- 共享行为: Both perform file I/O operations；Both handle exceptions
- 行为差异: Function A is a complex orchestration of Prolog parsing, class generation, and packaging; Function B is a simple recursive file copy；Function A uses command-line arguments; Function B takes File parameters；Function A involves object serialization and ASM bytecode writing; Function B only copies bytes
- 修正建议: Incorporate deeper structural information like method call graphs；Use semantic similarity models that capture intent rather than lexical patterns；Add a pre-filter based on method name/return type

### case_id=5096 FP lexical_or_api_overlap

- 方法: `populateResources` vs `getFrameworkFactory`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Loads template files and images from resource paths and saves them as database objects.
- B 摘要: Reads a service configuration file to instantiate and return an OSGi FrameworkFactory via reflection.
- 静态失败原因: The static model overemphasized lexical and API overlap: both methods use URL, BufferedReader, readLine, and loops, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB focuses on overall functionality; these methods have completely different purposes despite sharing some structural elements. The BCB label 0 indicates they are not considered clones under its annotation guidelines.
- 共享行为: Both open a URL and read lines using BufferedReader.；Both iterate over lines from an input stream.
- 行为差异: populateResources saves resources and images; getFrameworkFactory returns an object.；populateResources reads XML/TXT files from a specific template directory; getFrameworkFactory reads a single service registration file.；populateResources uses multiple file formats and handles images; getFrameworkFactory uses reflection for instantiation.；Error handling differs: one logs errors, the other throws an exception.
- 修正建议: Incorporate dataflow analysis to track how inputs are transformed to outputs.；Use semantic role labeling to distinguish between different tasks (e.g., saving vs. instantiating).；Leverage program slicing to compare only functionally relevant code segments.

### case_id=5097 FP lexical_or_api_overlap

- 方法: `doVersionCheck` vs `SRWGuiClient`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Checks for development and stable build versions from a remote file.
- B 摘要: Constructs a Swing browser GUI and displays transformed XML/HTML content.
- 静态失败原因: The model likely overemphasized the lexical and API overlap (e.g., URL, InputStream, BufferedReader) and missed the divergent semantic contexts and control flows.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB treats methods with distinct overall semantics as non-clones, even if they share some low-level API usage like URL opening.
- 共享行为: Both open a URL and read lines from it.
- 行为差异: Different overall purpose: version checking vs. GUI construction.；Different error handling: IOException vs. IOException and TransformerException.；Different control flow and output: one calls another method, the other builds UI components.；Different side effects: one shows error dialog, the other displays HTML content.
- 修正建议: Incorporate structural matching of control flow and data dependencies.；Use method name and class context as additional features.；Apply higher-level semantic analysis to distinguish different program intents.

### case_id=5098 FN benchmark_preference_bias

- 方法: `readData` vs `getNetworkServersIPs`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Parses a configuration file with multiple tokenized fields to populate various sets and maps for Tibetan language processing.
- B 摘要: Reads a URL, parses lines for server IPs after a '!SERVERS' header, and returns a vector of IP strings.
- 静态失败原因: Static BERT models rely heavily on lexical and structural overlap, which is very low (Jaccard=0.085). The high-level semantic similarity is not captured due to different APIs and data structures, and the long length of function_a may cause attention dilution.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may label this as a clone because both functions follow a common pattern of 'read data → parse → populate collections', ignoring domain specifics. This broad Type-4 similarity is sometimes accepted in BigCloneBench.
- 共享行为: Both read input from an external source (file or URL).；Both parse lines sequentially using tokenization or splitting.；Both populate collection data structures (sets or vector) with parsed results.
- 行为差异: Input source: local file vs. remote URL.；Parsing format: comma-separated tokens vs. colon-separated fields with header detection.；Data structures: multiple HashSets and a HashMap vs. a single Vector<String>.；Purpose: Tibetan language setup vs. network server IP retrieval.
- 修正建议: Improve training data with more diverse positive examples of broad semantic clones.；Incorporate higher-level program flow analysis beyond token matching.；Use contrastive learning to emphasize functional similarity over lexical overlap.

### case_id=5099 FP lexical_or_api_overlap

- 方法: `downloadURLtoString` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a URL and returns its content as a concatenated string.
- B 摘要: Performs a Google image search, parses HTML response for image URLs, and updates the UI with the first image.
- 静态失败原因: Static BERT/GraphCodeBERT may over-rely on lexical and API token overlap (BufferedReader, URL, readLine, etc.) and miss the semantic divergence due to different control flows, exception handling, and post-processing steps.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the functions have different overall purposes and only share generic URL-reading boilerplate, which is insufficient for Type-3 or Type-4 similarity.
- 共享行为: Both open a URL connection and read the response line by line.
- 行为差异: Function B constructs a search URL with query and uses HttpURLConnection with a User-Agent, while A uses URL.openStream().；Function B parses HTML to extract image URLs, whereas A simply concatenates all lines.；Function B updates UI components (JButton, JLabel) and handles exceptions with error dialogs.；Function A returns the string, while B is void and has side effects.
- 修正建议: Use data-flow analysis to distinguish reads from writes and output destinations.；Incorporate program dependency graphs to capture structural differences.；Increase sensitivity to library-specific semantics (e.g., ImageIcon vs. StringBuffer).

### case_id=5100 FN partial_functionality

- 方法: `retrieveQ` vs `File2String`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: retrieveQ fetches a URL and returns its content as a string, preserving newlines between lines.
- B 摘要: File2String reads a file or classpath resource and returns its content as a string without newlines, with error handling that exits the program.
- 静态失败原因: Low token overlap (24.7%) and different API usage (URL vs File) misled the static model; it lacks understanding of the high-level shared intent of reading text input.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often considers Type-3/Type-4 clones where both functions implement the same high-level task (reading text input and returning as string) despite differences in source, newline handling, and error handling.
- 共享行为: Reads text input (URL or file) and returns the content as a string；Uses BufferedReader to read lines；Appends lines to a buffer (StringBuilder or StringBuffer)；Closes the reader after reading
- 行为差异: Input source: URL vs file (or classpath resource)；Newline handling: retrieveQ adds newlines between lines, File2String does not；Error handling: retrieveQ throws exceptions, File2String prints messages and exits；Buffer type: StringBuilder vs StringBuffer
- 修正建议: Augment training data with more functional clones that differ in API details；Incorporate data-flow or control-flow graphs to capture structural similarities；Use code contrastive learning to focus on semantic equivalence rather than lexical overlap

### case_id=5101 FN benchmark_preference_bias

- 方法: `addIDs` vs `parse`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Fetches metabolite information from a remote database using a name query and populates a peak list row with various identifiers and properties.
- B 摘要: Parses a delimited data file or URL into a DataSet object, handling headers, types, and scientific notation.
- 静态失败原因: Static BERT likely correctly identified them as non-clones due to low lexical overlap and different semantics, but failed to align with BCB's broader criteria that may consider structural similarity or complexity as sufficient for clone labeling.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled these as clones because both are long, complex methods performing I/O, parsing, and data extraction, with similar structural features (loops, conditionals, exception handling). However, the domain-specific purpose and output differ entirely.
- 共享行为: Both read from an external source (URL or file) using BufferedReader；Both parse lines and extract data based on patterns or delimiters；Both handle exceptions with try-catch blocks
- 行为差异: Function A specifically queries a metabolite database and extracts biological identifiers for a row; Function B is a generic CSV/TSV parser that produces a DataSet；Function A returns an integer score; Function B returns a DataSet object；Function A has hardcoded URL and parses HTML-like content; Function B has configurable delimiters, headers, and handles scientific notation
- 修正建议: Use more accurate clone definitions focusing on semantic equivalence rather than structural similarity；Incorporate domain knowledge to distinguish between generic parsing and domain-specific extraction

### case_id=5102 FN lexical_or_api_overlap

- 方法: `copyResource` vs `readAndRewrite`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource from a URL or file to a destination file by reading byte by byte.
- B 摘要: Reads a DICOM file, parses its dataset, reads pixel data, and writes it to a new file.
- 静态失败原因: Static BERT/GraphCodeBERT models rely on token sequences and structural patterns. The low token Jaccard (0.1) indicates little lexical overlap, and the models fail to recognize the high-level semantic similarity due to entirely different APIs and domains.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely labels this as a clone because both functions perform a copy operation, which falls under the broad category of 'copy file or stream'. Despite differences in implementation and domain specificity, the core behavior of reading from a source and writing to a destination is shared.
- 共享行为: Both functions copy data from an input source to an output destination.
- 行为差异: Function A handles generic resources (URL or file) and copies raw bytes.；Function B specifically processes DICOM files with complex parsing and writing using DCM4CHE libraries.
- 修正建议: Incorporate data-flow analysis to capture input-output transformations.；Use program slicing to focus on core functionality.；Train on more diverse examples of copy operations.

### case_id=5103 FP boilerplate_overlap

- 方法: `load` vs `importSequences`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Downloads a pastebin text by ID, concatenates lines into a string, and returns it or shows error dialog.
- B 摘要: Reads DNA/protein sequences from a URL using ImportHelper, parses names and sequences, and stores them in class lists.
- 静态失败原因: Static BERT models may have overgeneralized from the shared structural pattern of URL opening and try-catch blocks, or misled by method names suggesting input operations, despite low token overlap.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clone because the functions have fundamentally different purposes (generic data retrieval vs. domain-specific sequence parsing) and different output behaviors, despite both involving URL reading.
- 共享行为: Both open a URL connection and read input streams.；Both use try-catch for IOException handling.
- 行为差异: A fetches generic text from pastebin; B parses structured sequence data with a specific delimiter ('>').；A returns a string; B populates class fields (names, sequences) and has no return value.；A uses BufferedReader and line-by-line concatenation; B uses custom ImportHelper for sequence parsing.；A pops up error dialog on failure; B prints stack trace or catches EOF silently.
- 修正建议: Include more diverse negative examples with similar IO patterns but different intent.；Focus training on functional equivalence, not just lexical or structural overlap.；Use dataflow analysis to differentiate between simple download and structured parsing.

### case_id=5104 FN partial_functionality

- 方法: `doTransfer` vs `doVersionCheck`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: HTTP request forwarding proxy that copies headers, request body, and response to a target URL specified by a parameter.
- B 摘要: Version check utility that reads build numbers from a remote URL and triggers an update dialog if new versions exist.
- 静态失败原因: The static model likely detected low token similarity (Jaccard=0.154) and different structural patterns (one uses HttpURLConnection with extensive setup, the other uses simple URL.openStream). It correctly identified the semantic mismatch and predicted non-clone.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have considered them clones due to both using URL.openStream() and reading line-by-line, as well as both being network I/O operations, but this is a very broad interpretation; the original annotation may be an error or a very lenient Type-4 clone.
- 共享行为: Both open a URL connection and read data from it；Both handle IOException with error printing or dialog
- 行为差异: Code A forwards the entire HTTP request and response, while Code B only reads and parses a specific file；Code A involves writing data to the URL connection (POST/PUT), Code B uses a simple GET；Code A manipulates headers and response status, Code B does not
- 修正建议: Improve modeling of long-range dependencies and data flow；Add a notion of task-level semantics (proxy vs. version check)；Use contrastive learning to differentiate between similar structural patterns but different high-level goals

### case_id=5105 FP lexical_or_api_overlap

- 方法: `moveFile` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Moves a file by copying its contents to a target and deleting the original.
- B 摘要: Handles GUI action events to set file paths and update application preferences.
- 静态失败原因: The static model likely misclassified due to lexical overlap of common terms (File, if, return) and the presence of file-related API calls (FileInputStream, FileOutputStream in A; JFileChooser in B) which triggered a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB considers them non-clones due to completely different functionality and low token overlap (Jaccard 0.052). The only commonality is usage of File class, but that is trivial.
- 共享行为: Both involve file operations (copying in A, selecting in B).
- 行为差异: A performs low-level file I/O; B handles GUI events and preference management.；A is a private utility method; B is a public action listener.；A copies and deletes files; B updates UI components and stores preferences.；No overlap in logic or control flow.
- 修正建议: Enhance training with more diverse non-clone pairs involving common APIs but different semantics.；Incorporate structural or control flow analysis to distinguish simple utility methods from event handlers.；Use dataflow or dependency analysis to capture the actual behavior beyond surface tokens.

### case_id=5106 FP boilerplate_overlap

- 方法: `sendPost` vs `parse`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Sends an HTTP POST request with parameters and returns the response body as a string.
- B 摘要: Parses a data file or URL into a DataSet using tokenization, handling headers and types.
- 静态失败原因: The model likely focused on common boilerplate patterns (BufferedReader, InputStreamReader, exception handling) and URL handling in both, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would consider these as non-clones because they have completely different functionalities despite some superficial I/O boilerplate.
- 共享行为: Both use BufferedReader and InputStreamReader for reading input；Both involve exception handling with try-catch；Both return a result object
- 行为差异: A performs HTTP POST networking; B parses local or remote data files；A returns String; B returns custom DataSet object；A uses HttpURLConnection and PrintWriter; B uses StreamTokenizer and complex parsing logic；B has extensive state management (headers, types, columns); A is stateless
- 修正建议: Incorporate AST or control-flow features to distinguish high-level semantics；Use dataflow analysis to capture the different purposes (network vs. file parsing)；Train on more diverse examples to reduce sensitivity to generic I/O patterns

### case_id=5107 FP partial_functionality

- 方法: `getRequestContent` vs `handledRun`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches the first line of content from a given URL.
- B 摘要: Checks for game data updates by reading a remote XML file header and optionally downloads the full file.
- 静态失败原因: Static BERT/GraphCodeBERT may have focused on the overlapping tokens (URL, BufferedReader, readLine, etc.) and missed the structural and semantic differences, especially the extensive additional logic and side effects in code B.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely labels this as not a clone because the overall functionality is different; code B performs a version check and download, while code A simply returns the first line.
- 共享行为: Opens a URL connection；Reads the first line from the input stream
- 行为差异: Code B also reads a second line and parses a version number；Code B conditionally downloads and saves the entire file if version is newer；Code B includes extensive error handling and logging；Code B loads game data in a finally block
- 修正建议: Improve model's ability to capture overall program purpose and side effects；Use dataflow analysis to distinguish between simple retrieval and complex update logic；Incorporate control flow depth and conditional structure differences

### case_id=5108 FN lexical_or_api_overlap

- 方法: `addIDs` vs `PhoneSetImpl`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Parses metabolite data from a GMD URL by reading HTML and extracting IDs, setting various fields on a PeakListRow, and returns a score.
- B 摘要: Reads phone set data from a URL line by line, skipping lines starting with '***', and calls parseAndAdd for each valid line to populate a map.
- 静态失败原因: The model may have relied on lexical overlap like 'BufferedReader', 'URL', 'readLine', and similar exception handling, while missing the distinct semantic purposes and data processing logic.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may consider them clones due to the shared pattern of reading from a URL and processing input, but the actual functionality is entirely different, making it a poor match under typical BCB criteria.
- 共享行为: Both open a URL and read from it using BufferedReader.；Both perform line-by-line reading in a loop.
- 行为差异: A parses HTML for specific metabolite IDs; B reads plain text lines.；A sets multiple fields on a PeakListRow; B calls parseAndAdd to populate a map.；A returns an integer score; B is a constructor with no return value.；A has extensive conditional logic for different ID types; B only checks line prefix.
- 修正建议: Incorporate data-flow analysis to track variable usage and assignments.；Use graph-based features that capture control flow and data dependencies beyond lexical tokens.；Train on more diverse examples of non-clones with similar API usage but different intent.

### case_id=5109 FP other

- 方法: `readData` vs `doUpload`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Parses multiple comma-separated string lists into Java collections (HashSet, HashMap) for Tibetan character data.
- B 摘要: Handles HTTP file upload requests: manages temporary directories, processes multipart parameters, and responds with redirect or XML output.
- 静态失败原因: The static BERT model likely over-generalized superficial structural similarities (e.g., both have loops, conditionals, and error handling) while ignoring the vastly different domain-specific APIs and overall purpose.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB labels these as non-clones because they perform entirely different tasks (data initialization vs. HTTP file upload) with no functional overlap.
- 行为差异: readData initializes static data structures from string tokens; doUpload manages HTTP sessions, file I/O, and servlet responses.；readData is a private static utility method; doUpload is a protected servlet method interacting with request/response objects.；readData uses StringTokenizer for parsing; doUpload uses ServletFileUpload and custom helper methods.；readData throws Error on invalid input; doUpload throws ServletException/IOException and handles errors with log messages.
- 修正建议: Improve model sensitivity to API usage and type information.；Incorporate data flow and control flow analysis to distinguish orthogonal functionality.；Use contrastive learning on pairs with low token overlap but high structural similarity.

### case_id=5110 FP boilerplate_overlap

- 方法: `callService` vs `getFrameworkFactory`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Calls a web service by constructing a URL, reading the response into a string buffer, and storing it in a field.
- B 摘要: Reads a configuration file from the classpath to instantiate an OSGi FrameworkFactory and returns it.
- 静态失败原因: The model likely over-relied on token overlap (e.g., 'URL', 'BufferedReader', 'readLine') and control flow similarity, failing to capture the distinct semantics of the external operations and return types.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels non-clone when the overall functionality is unrelated despite shared syntactic patterns like I/O boilerplate. Here, the purpose is completely different (service call vs. framework factory loading), so BCB correctly marks as non-clone.
- 共享行为: Both open a URL/input stream and read lines using BufferedReader.
- 行为差异: Function A makes an HTTP request to a remote service; function B reads a local classpath resource.；Function A returns void and stores result in a field; function B returns a FrameworkFactory object.；Error handling differs: A catches exceptions and sets error strings; B throws exceptions.；Function B includes filtering of comments and instantiates a class via reflection.
- 修正建议: Incorporate dataflow analysis to distinguish I/O sources (HTTP URL vs. classpath resource).；Include method signature and return type information in the embedding.；Train on more hard negative examples where boilerplate is similar but functionality differs.

### case_id=5111 FP lexical_or_api_overlap

- 方法: `populateResources` vs `loadURL`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Loads resource templates and images from classpath and saves them persistently.
- B 摘要: Downloads content from a URL with optional authentication and writes to a temporary file while updating a status label.
- 静态失败原因: Static BERT models may over-rely on lexical overlap (e.g., 'URL', 'BufferedReader', 'readLine', 'IOException') and miss the fundamental difference in program purpose and control flow.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would label them as non-clones because they perform completely different high-level tasks despite some shared API calls.
- 共享行为: Both open URLs and read lines of text using BufferedReader；Both handle text data and I/O operations
- 行为差异: Different purposes: local resource loading vs remote file download；Different inputs: no parameters vs URL, username, password, label；Different outputs: persistent save vs temporary file；Authentication handling only in B
- 修正建议: Train with more negative examples where API usage is similar but functionality differs；Incorporate structural features like method signature, number of parameters, and side-effect analysis

### case_id=5112 FP lexical_or_api_overlap

- 方法: `downloadURLtoString` vs `sendPost`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads content from a URL using GET and returns as string.
- B 摘要: Sends an HTTP POST request with parameters and returns the response as string.
- 静态失败原因: Static BERT models may have overemphasized the lexical overlap in variable names (BufferedReader, InputStreamReader, readLine, etc.) and the common pattern of reading from a stream, while missing the semantic difference in HTTP method and parameter handling.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB tends to label pairs as non-clones when the HTTP methods differ (GET vs POST) and the code structure is significantly different, despite both reading HTTP responses.
- 共享行为: Both open a URL connection and read line by line into a string buffer.；Both return the result as a String.
- 行为差异: Function A uses GET request without parameters; Function B uses POST request with parameters.；Function A does not set any request properties; Function B sets header and uses output stream to send parameters.；Function A throws IOException; Function B catches Exception and shows message.；Function A uses StringBuffer for efficiency; Function B concatenates strings with +=.
- 修正建议: Enhance model to capture HTTP method semantics (e.g., distinguish GET vs POST).；Incorporate control flow and data flow to detect differences in writing to output stream vs not.；Use more fine-grained API call patterns to differentiate between download and submit operations.

### case_id=5113 FP lexical_or_api_overlap

- 方法: `handleHandshake` vs `read`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Handles a Minecraft handshake packet by validating username and authenticating with session server.
- B 摘要: Reads a skeleton file from classpath, splitting it into sections by '---' markers.
- 静态失败原因: The model likely overemphasized the shared API calls (URL, BufferedReader, InputStreamReader, readLine) and similar structured control flow (try-catch, loops), mistaking boilerplate for semantic similarity.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clone because the functions have completely different purposes (handshake vs file parsing) and no shared business logic, despite similar I/O boilerplate.
- 行为差异: A handles network authentication; B reads and parses a resource file.；A uses conditional logic based on username; B uses loop to read lines until null.；A sends packets to network; B builds a list of strings.；A interacts with external URL; B accesses local classpath resource.
- 修正建议: Incorporate data flow analysis to track variable usage and transformations.；Use abstract syntax trees to capture higher-level structural differences.；Add context embeddings that distinguish network I/O from file I/O tasks.

### case_id=5114 FP partial_functionality

- 方法: `serialize` vs `main`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Serializes an IMSCP package to an output stream by parsing and copying a temporary file.
- B 摘要: Main method of a code generator that reads a Prolog file, parses it, generates adapter classes, and writes them to a JAR with serialized adapter layer.
- 静态失败原因: The static model may have been misled by the presence of similar API calls (e.g., FileInputStream, ObjectOutputStream) and the concept of serialization in both functions, despite the vastly different high-level semantics.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely labeled non-clone because the functions have entirely different purposes and logic, with no meaningful overlap except generic I/O operations.
- 共享行为: Both perform file I/O and use exception handling；Both involve serialization (one serializes package, the other serializes adapter layer map)
- 行为差异: Function A is a utility method for serializing a content package; Function B is the entry point for a complex code generation pipeline；Function A only copies a file; Function B reads, parses, generates classes, and writes multiple artifacts；Function A has no command-line argument handling; Function B parses arguments and produces debug output
- 修正建议: Enhance training with contrastive examples that have similar low-level operations but different intents；Incorporate code summarization or AST-based features to capture high-level purpose

### case_id=5115 FN benchmark_preference_bias

- 方法: `EncodeReturn` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: EncodeReturn encrypts download data and combines it with a return route file, returning the encoded result.
- B 摘要: buildSiteForEdit transforms XML pages via XSLT and writes the output files for a website.
- 静态失败原因: Static BERT/GraphCodeBERT models rely on token and structural overlap. With 3.4% token Jaccard and no shared identifiers, the model confidently predicted non-clone, failing to match BCB's overly broad Type-4 labeling.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled these as clones due to a very broad interpretation of Type-4 semantic clones, considering both as 'data transformation and file writing' tasks despite entirely different domains and algorithms.
- 共享行为: Both involve file I/O (read/write) and some form of data transformation.
- 行为差异: A performs cryptographic encoding; B performs XSLT-based web page generation.；A uses CryptoClient and specific encoding classes; B uses Transformer and FileSystem.；A returns a single file; B writes multiple output files and has no return value.；A is short and linear; B is long with loops, many parameters, and error handling.
- 修正建议: Re-annotate this BCB pair to ensure consistency with actual clone definitions.；Use semantic-aware embeddings that capture abstract behavior beyond token overlap.；Incorporate control-flow and data-flow features to detect true semantic similarity.

### case_id=5116 FP lexical_or_api_overlap

- 方法: `doVersionCheck` vs `getRequestContent`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Checks for a newer version by reading a remote file and comparing build numbers, with GUI feedback.
- B 摘要: Reads the first line from a URL and returns it as a string.
- 静态失败原因: A static BERT/GraphCodeBERT model likely overemphasized the lexical overlap (e.g., 'URL', 'BufferedReader', 'openStream', 'readLine') and missed the distinct control flow and purpose, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely considers these not clones because their overall functionality is different: one is a version-checking utility with UI, the other is a simple HTTP response reader. The shared URL-reading boilerplate is insufficient for clone classification under BCB's criteria, which require substantial functional overlap.
- 共享行为: Open a URL and create a BufferedReader from its input stream；Read lines from the stream
- 行为差异: A reads multiple lines looking for specific version and build information, while B reads only the first line；A includes GUI interaction (showing wait cursor, messages) and exception handling with user feedback, B throws exceptions and has no UI；A performs version comparison logic, B simply returns the line
- 修正建议: Incorporate data flow analysis to capture differences in how the input stream is processed (e.g., while loop vs single read).；Use method name semantics or context to distinguish high-level intent.；Train on pairs with similar API usage but different business logic to reduce reliance on surface-level token overlap.

### case_id=5117 FP lexical_or_api_overlap

- 方法: `getNetworkServersIPs` vs `downloadModel`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a network URL, parses lines to extract IP addresses after a '!SERVERS' marker, ignoring comment lines.
- B 摘要: Downloads an RDF model from a URL using HTTP headers and Jena API, then returns the model.
- 静态失败原因: Static models like GraphCodeBERT rely heavily on lexical and API-level overlap. Both functions use URLConnection, openStream, and similar exception handling, leading to high embedding similarity despite different semantics.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically requires strong functional similarity for Type-3/4 clones; here only the generic I/O pattern matches, not the core purpose.
- 共享行为: Open a URL connection and read input stream；Handle MalformedURLException and IOException
- 行为差异: Function A parses text lines to extract IPs; Function B reads and parses RDF data into a Model object；Function A returns a Vector of strings; Function B returns a Model；Function A has state-dependent parsing logic; Function B sets HTTP headers and uses Jena API；Function A does not close the reader explicitly; Function B closes the input stream explicitly
- 修正建议: Incorporate data flow analysis to track how the input stream is used (parsing vs. model loading)；Use type information (return type differentiates behavior)；Train on more diverse examples where similar API usage yields different functionality

### case_id=5118 FP lexical_or_api_overlap

- 方法: `createHTML` vs `getFullScreenUrl`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Builds an HTML page for different dashboard pages (logo, home) by reading CSS and querying database.
- B 摘要: Extracts a full-screen video URL from a YouTube page by parsing HTTP response for 'fullscreenUrl'.
- 静态失败原因: Static BERT/GraphCodeBERT models can be misled by shared API usage (URL, BufferedReader, try-catch) and similar boilerplate code, causing high embedding similarity despite different semantics.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB considers these non-clones because they have no functional similarity; one generates HTML, the other extracts a video URL.
- 共享行为: Both use URL, BufferedReader, InputStreamReader to read external resources.；Both handle exceptions with try-catch blocks.
- 行为差异: createHTML generates HTML content for a dashboard; getFullScreenUrl constructs a video download URL.；createHTML uses a switch on page type and database queries; getFullScreenUrl parses a web page for specific parameters.；Output formats and purposes are completely different.
- 修正建议: Incorporate data flow or control flow analysis to distinguish different operations.；Use task-specific embeddings that focus on functional behavior rather than API tokens.

### case_id=5119 FP lexical_or_api_overlap

- 方法: `loadSourceCode` vs `run`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Loads source code from a file, applies syntax highlighting, and returns an HTML string.
- B 摘要: Fetches tile data from a URL, builds geoJSON, and processes it into geometry for map display.
- 静态失败原因: Static models like CodeBERT rely heavily on lexical and structural overlap. The common pattern of URL, InputStream, BufferedReader, and while-readLine creates high similarity, masking the functional divergence.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels clones based on functional similarity. Despite both reading lines, the distinct purposes (code display vs. map rendering) and output processing lead BCB to annotate as non-clone.
- 共享行为: Reads lines from an input stream using BufferedReader；Uses URL and InputStream to open data source；Concatenates lines into a string；Handles exceptions with try-catch blocks
- 行为差异: A applies syntax highlighting; B processes geometries；A only loads from file resource; B handles file and HTTP protocols；B includes synchronization and duplicate check; A does not；A builds HTML; B builds geoJSON and adds to data loader
- 修正建议: Incorporate method name and class context；Add attention to method-level semantics beyond token overlap；Use data flow analysis to distinguish output types

### case_id=5120 FP other

- 方法: `DialogHelper` vs `readData`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Constructs a dialog to display an image and provides a save button that copies the image file to a chosen location, along with a close button.
- B 摘要: Reads comma-separated string constants into various sets and a hash map, performing extensive parsing to initialize character classification tables for a Tibetan transliteration system.
- 静态失败原因: The model likely misclassified due to noise or an artifact in the training data. The functions share no meaningful semantic similarity, and the token Jaccard is very low, so the false positive may stem from a random prediction error or the model picking up on rare shallow patterns (e.g., both contain 'JDialog'? Actually B does not). Alternatively, the severe truncation in the provided snippet of code_b may have confused the model if it saw incomplete code during inference, but the original full functions were likely used.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB labels this as non-clone because the functions have entirely different purposes, inputs, outputs, and control flow. The low token Jaccard (0.07) and lack of shared functionality reinforce that they are not clones under any type.
- 共享行为: Both involve file handling indirectly (A: file channel copy; B: file reading) but in completely different contexts and with no algorithmic overlap.
- 行为差异: A creates a GUI dialog with Swing components; B is a static data initialization method with no UI.；A handles user interaction via ActionListeners; B reads pre-defined string constants into data structures.；A deals with image file copying using FileChannel; B parses tokenized strings to populate character sets and validation maps.
- 修正建议: Improve training data quality and remove noisy false positives.；Implement better length normalization or attention mechanisms to handle long and truncated code snippets.；Use stricter thresholding for low similarity pairs to avoid random predictions.

### case_id=5121 FN partial_functionality

- 方法: `copy` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a file from source path to destination path with validation and buffer-based byte transfer.
- B 摘要: Builds a site for editing by processing pages with XSLT transformations and writing output files.
- 静态失败原因: Static models like BERT or GraphCodeBERT might have failed because they rely on token overlap and structural similarity. The token Jaccard is low (0.109), and the functions have different lengths and structures. The model might have missed the underlying shared I/O pattern due to lack of training on such diverse pairs, or it may have correctly identified them as non-clones.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this as a clone because both methods involve reading from a file and writing to another file, a common I/O pattern. The annotator might have considered them as 'file copy' operations at a high level.
- 共享行为: Both perform file I/O operations: reading from an input source and writing to an output destination using buffers.
- 行为差异: A is a simple file copy; B involves complex XML transformation and multiple file operations.；A works with bytes; B works with characters and strings.；A validates file existence and permissions; B does not (instead it throws exceptions).；A uses FileInputStream/FileOutputStream; B uses FileInputStream, FileWriter, and custom FileSystem methods.
- 修正建议: Use more refined semantic analysis focusing on the core I/O operations.；Incorporate data-flow analysis to detect common patterns like read-write loops.；Train on more diverse pairs with partial functional similarity.

### case_id=5122 FN lexical_or_api_overlap

- 方法: `writeData` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.65`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Writes mass spectrometry data to a text file with peak detection.
- B 摘要: Transforms XML pages into HTML output files using XSLT and string replacements.
- 静态失败原因: Low token Jaccard similarity (0.096) and distinct vocabulary caused static models to miss the broad 'file writing' similarity; they rely on lexical overlap rather than high-level functional abstraction.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may label them as clones because both are 'write' functions that take inputs and produce output files, sharing a generic file-writing pattern, despite vastly different domain logic.
- 共享行为: Both functions write data to output files using file writers.；Both involve loops over input items or pages.；Both have some debugging output.
- 行为差异: writeData outputs tabular scientific data; buildSiteForEdit outputs HTML pages.；writeData uses simple PrintWriter and date formatting; buildSiteForEdit uses complex XML/XSLT transformations.；Parameter types and overall structure are completely different.
- 修正建议: Incorporate data-flow or control-flow features to capture I/O patterns.；Use semantic role labeling to identify 'write to file' as common behavior.；Ensemble with heuristics that recognize generic template-like structures.

### case_id=5123 FP boilerplate_overlap

- 方法: `doRawRequest` vs `importSequences`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Sends POST data to a service URL and returns the response body as a string.
- B 摘要: Imports sequences from a URL in FASTA format, populating lists of names and sequences.
- 静态失败原因: The static BERT/GraphCodeBERT model likely overemphasized the lexical overlap in I/O API usage (URLConnection, InputStreamReader, StringBuffer) and the control flow pattern of opening a connection, reading lines, and building a string, ignoring the fundamental differences in data processing, output, and context. The low token Jaccard (0.15) was not enough to outweigh the strong signal from common boilerplate patterns.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels these as non-clones because they belong to different functional categories: one is a generic HTTP request utility, the other is a domain-specific sequence importer. The similarity in basic I/O patterns is insufficient for a clone annotation in BCB's classification.
- 共享行为: Both open a URL connection and read data from the input stream.；Both use StringBuffer or similar to accumulate string data.；Both involve I/O operations with streams.
- 行为差异: Function A writes postData to the output stream before reading, while B only reads.；Function A returns a single string concatenated from all lines; B parses a specific format with headers and sequences.；Function A uses generic URLConnection; B selects the URL from a GUI combo box.；Function A handles no exceptions (throws); B catches multiple exceptions including MalformedURLException and EOFException.
- 修正建议: Incorporate data-flow analysis to track how input data is used (e.g., postData is written in A but not in B).；Add task-type identification from method names and surrounding class context.；Use more sophisticated structural matching that distinguishes read-only vs. read-write operations and different output destinations.；Train with more diverse negative examples that share I/O patterns but have different semantics.

### case_id=5124 FN partial_functionality

- 方法: `runScript` vs `load`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches the content of a script file from an applet codebase by reading it byte by byte and returns it as a string, returning 'error!' on exception.
- B 摘要: Fetches the content of a pastebin document by its ID using a fixed URL, reading line by line, and returns the concatenated string, showing an error dialog on failure.
- 静态失败原因: A static BERT/GraphCodeBERT model might fail because it relies on token similarity and structural patterns. These functions have low token Jaccard (0.2096), different method names, and different control flow (byte vs line reading). The model may not capture the semantic similarity of the URL fetching pattern due to lack of API usage awareness and focus on surface form.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB might consider these clones because both functions implement the same high-level task: downloading text from a URL and returning it as a string. Despite implementation differences, the core behavior is similar enough to be considered a Type-3 or Type-4 clone.
- 共享行为: Both functions construct a URL based on input and open an HTTP connection to fetch textual content；Both read the content and accumulate it into a string；Both return the fetched string or handle errors by returning a default value (error!/empty string)
- 行为差异: A reads bytes one by one; B reads lines；A uses getCodeBase() for base URL; B uses a fixed pastebin URL pattern；A returns 'error!' on any exception; B shows a dialog and returns empty string；B has additional working flag manipulation and length check
- 修正建议: Use a clone detection method that recognizes common API usage patterns (e.g., URL.openStream, URLConnection) as evidence of functional similarity；Incorporate data flow analysis to identify that both functions have a similar sequence: construct URL, open stream, read, accumulate, return；Apply a learning method that can abstract away implementation differences like byte vs line reading and focus on intent

### case_id=5125 FP lexical_or_api_overlap

- 方法: `actionPerformed` vs `copyFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Event handler that processes various action commands by setting application preferences, such as file paths for Graphviz and ImageMagick, and UI settings.
- B 摘要: Utility method that copies a file from a source path to a destination directory using NIO FileChannels.
- 静态失败原因: The model likely over-emphasized superficial lexical similarities (e.g., both use 'File', exceptions) and / or misinterpretted the truncated lengthy code A as containing file-copy-like logic due to patterns seen in training data.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would not label these as clones because they perform entirely different tasks: one is a GUI event handler for setting preferences, the other is a file copy utility. Even under broad Type-4 (functional similarity), there is no shared behavior beyond trivial file usage.
- 共享行为: Both use the File class to represent file paths.；Both have exception handling for IO operations.
- 行为差异: Function A is a lengthy event handler with multiple branching actions and UI updates, while B is a focused file copy utility.；Function A interacts with user interface elements (JFileChooser, JTextField) and stores settings in a preferences system; B performs pure file I/O without any UI.；Function A uses java.io.File and JFileChooser; B uses java.io.File, FileInputStream, FileOutputStream, and java.nio.channels.FileChannel.
- 修正建议: Train the model with better example pairs that contrast GUI event handlers from utility functions.；Use function-level features such as method name, length, and call patterns to distinguish distinct roles.；Improve handling of truncated code to avoid partial pattern matching.

### case_id=5126 FN benchmark_preference_bias

- 方法: `writeFileType` vs `getEncoding`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Reads a file of URIs, for each URI fetches the content, checks for specific RDF/OWL namespaces in the first 100 lines, and writes the classification to an output file.
- B 摘要: Determines the character encoding of a URL by checking HTTP headers and then parsing the content for charset/encoding mentions.
- 静态失败原因: Static BERT likely predicted non-clone due to low lexical overlap and clear functional differences, but BCB's broad annotation preference expects a clone label; thus static BERT was too strict.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have considered both as involving URL content reading and line-by-line parsing for metadata extraction, viewing them as broad Type-4 clones despite different specific goals.
- 共享行为: Both open a URL connection and read lines from it.
- 行为差异: Function A processes multiple URIs from a file and writes results; Function B processes a single URL and returns a string.；Function A checks for OWL/RDFS/RDF namespaces; Function B checks for charset/encoding.；Function A has extensive error handling and logging; Function B returns a default encoding if not found.
- 修正建议: Adjust training to better capture broad semantic similarity beyond lexical overlap；Include contrastive examples where only high-level structure matches；Incorporate dataflow or structural graph features to detect common patterns

### case_id=5127 FP boilerplate_overlap

- 方法: `actionPerformed` vs `readAndRewrite`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Handles user preferences via action commands, opening file choosers and saving settings.
- B 摘要: Reads a DICOM image file and rewrites it to another file.
- 静态失败原因: The static model may have been misled by the presence of file-related method calls (e.g., getAbsolutePath, FileInputStream) and similar patterns like null checks, but missed the entirely different control flow and domain-specific logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels these as non-clones because they have completely different purposes and algorithm structures, with only superficial file handling overlap.
- 共享行为: Both involve file I/O operations
- 行为差异: Code A is a UI event handler for preferences; Code B is a DICOM file conversion utility.；Code A manipulates UI components and stores preferences; Code B performs pixel data reading and writing.；Code A uses JFileChooser and file filters; Code B uses ImageInputStream/ImageOutputStream and DICOM-specific APIs.
- 修正建议: Incorporate data flow analysis to differentiate event-handling from data-processing.；Leverage method name and context clues (e.g., actionPerformed vs. readAndRewrite).；Use a finer-grained tokenization that captures domain-specific vocabulary (e.g., DICOM, PixelData).

### case_id=5128 FN benchmark_preference_bias

- 方法: `writeData` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Writes tabular data to a file for mass spectrometry peaks.
- B 摘要: Launches a NexOpen project configuration in Eclipse, handling Maven POM files and Hibernate settings.
- 静态失败原因: The model correctly identified the lack of semantic similarity, as the token overlap is very low and the code structures are from different domains (data export vs. IDE launch).
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: Possibly BCB considered both as having loops and file-writing patterns, but the overall functionality is entirely different. The annotation might be an outlier.
- 行为差异: writeData writes a text file with timestamped data; launch configures and runs an Eclipse project build.；writeData uses simple file output; launch involves complex project resource handling and property manipulation.；writeData is for data export; launch is for IDE project launching.
- 修正建议: Review and possibly correct the BCB annotation for this pair.；Improve training data quality by filtering such low-similarity false positives.

### case_id=5129 FP partial_functionality

- 方法: `executePost` vs `run`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends an HTTP POST request to a target URL with URL-encoded parameters, reads the response line by line, and returns the response string.
- B 摘要: Sends an HTTP GET request with Basic Authentication to a URL, reads the response, stores it in an instance variable, and sets a finish flag.
- 静态失败原因: The static BERT model may have overemphasized common boilerplate patterns: HttpURLConnection, opening connection, reading response with BufferedReader, while missing subtle differences in method type, headers, and error handling. Structural similarity in control flow (try, connect, read, close) likely led to high representation similarity despite low token Jaccard.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB tends to label as clone only when functions are either syntactically similar or semantically equivalent in core functionality. Here, while both are HTTP request-response handlers, their specific operations differ: one is a POST utility, the other is a GET authentication routine. BCB likely considered them as different functional tasks, hence non-clone.
- 共享行为: Send HTTP request using HttpURLConnection；Open input stream and read response line by line using BufferedReader；Close resources (streams, connection) after use
- 行为差异: HTTP method: POST vs GET；Request headers: Content-Type/Length/Language vs Authorization；Output: sends body in POST vs no body in GET；Return: direct string vs storing in instance variable and setting finish flag
- 修正建议: Include attention to request method and header differences；Better distinguish between POST and GET patterns；Expand training data with more examples of HTTP utilities with different methods and authentication；Use flow-sensitive analysis to capture data dependencies on headers

### case_id=5130 FN partial_functionality

- 方法: `getContent` vs `httpRequestByPOST`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.95`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Executes a given HTTP request and returns the response body as a string, with fixed timeouts and throwing exceptions on failure.
- B 摘要: Sends an HTTP POST request to a given URL with parameters, returns the response body as a string, or null on error with side effect recording.
- 静态失败原因: Static BERT models like GraphCodeBERT rely heavily on token overlap and structural similarity; the relatively low token Jaccard (0.3125) and differences in method names, signatures, and error handling likely caused the model to miss the underlying functional similarity. The model may have focused on superficial differences rather than the common core behavior.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely labeled these as clones because both perform the core task of making an HTTP request and retrieving the response body, despite differences in input handling, error management, and timeout settings. The shared API usage (HttpClient, BufferedReader) and overall structure align with BCB's tolerance for Type-3/Type-4 partial functionality clones.
- 共享行为: Uses Apache HttpClient to execute an HTTP request；Reads the response entity line by line using BufferedReader；Returns the response body as a string
- 行为差异: Method A takes an HttpUriRequest; method B takes URL, timeout, and parameters to build a POST request；Method A has fixed timeouts; method B accepts a timeout parameter but does not set it on the connection；Method A throws Exception; method B catches exceptions and returns null, updating error codes；Method B checks HTTP status code and returns null for errors; method A does not check status code
- 修正建议: Enhance training with examples that vary in method signatures but share core logic；Incorporate API call sequence embeddings to capture functional similarity independent of variable/type names；Use data-flow-aware models that trace the transformation of inputs to outputs across different patterns

### case_id=5131 FN benchmark_preference_bias

- 方法: `doGet` vs `convert`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Handles HTTP GET request to retrieve a portal page, checks visibility, logs requests, and renders the page with caching and error handling.
- B 摘要: Converts an ACRNEMA medical image file to DICOM format, adding UIDs and handling pixel data with inflation and validation.
- 静态失败原因: Static BERT did not fail; it correctly predicted 0. The error type FN indicates the static model disagreed with the BCB label, which itself is questionable. The model likely detected the low token overlap and distinct token patterns, leading to a correct non-clone prediction.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled them as clones due to superficial structural similarities (e.g., try-catch, logging, conditional checks, output writing), but these are generic and not indicative of functional similarity. This is likely a labeling error or overly broad interpretation of clone types.
- 共享行为: Both involve reading input, performing condition checks, writing output, and using try-catch blocks with logging.
- 行为差异: Different input types: HTTP request vs file.；Different output types: HTTP response vs file.；Different domain: web portal vs medical imaging.；Different processing logic: page rendering vs DICOM conversion.
- 修正建议: Re-evaluate BCB annotation guidelines to require stronger functional or semantic similarity for clones.；Remove or relabel this pair in the benchmark to reduce noise.；Use domain-specific or structural similarity measures that go beyond generic patterns.

### case_id=5132 FP lexical_or_api_overlap

- 方法: `get` vs `getUser`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches game records from an HTTP server using lat/lon/count and returns an array of GameRecord objects.
- B 摘要: Loads a User object from a local config file or DAO based on user login, parses colon-delimited lines.
- 静态失败原因: Static BERT/GraphCodeBERT likely over-relied on lexical and API-level similarities (BufferedReader, readLine, while loop, try-catch) and method names sharing 'get', while missing the entirely different I/O sources (HTTP vs file) and domain objects (GameRecord vs User).
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled non-clone because the functions serve different purposes: one is for fetching game records online, the other for local user authentication. While both involve text parsing, the overall functionality is distinct, and BCB tends to annotate such pairs as Type-4 or non-clones.
- 共享行为: Both use BufferedReader and readLine to read input line by line.；Both have try-catch blocks and print stack traces on exception.；Both parse strings from lines and construct domain objects.；Both return null on failure.
- 行为差异: Function A makes an HTTP GET request; function B reads a local resource file.；Function A uses HttpURLConnection and custom headers; function B uses StringTokenizer.；Function A returns an array; function B returns a single User.；Function A reads from network; function B reads from classpath and also uses DAO.
- 修正建议: Incorporate type information (e.g., HttpURLConnection vs ClassLoader.getResource) into embeddings.；Use data flow analysis to distinguish different external data sources.；Add negative sampling with high lexical overlap but different semantics.

### case_id=5133 FP boilerplate_overlap

- 方法: `copy` vs `readData`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Copies a file byte by byte using FileReader and FileWriter.
- B 摘要: Reads configuration data by tokenizing strings and populating multiple sets and maps.
- 静态失败原因: The static model likely over-relied on shallow structural patterns like while loops and try-catch blocks, or misidentified the method name 'copy' vs 'readData' as similar, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB broad clones (Type-3/4) require some functional overlap, but these two methods share no common purpose or behavior, so BCB correctly labels them as non-clones.
- 共享行为: Both involve reading input and using while loops.；Both handle some I/O operations (one file, one string tokenization).
- 行为差异: Function A copies file content; Function B parses tokens and builds data structures.；Function A uses FileReader/FileWriter; Function B uses StringTokenizer and HashSet.；Function A is simple and generic; Function B is complex and domain-specific.；Function A operates on files; Function B operates on global string variables.
- 修正建议: Incorporate deeper semantic understanding beyond token overlap.；Use data flow analysis to distinguish different I/O operations.；Train on more diverse negative examples to avoid boilerplate false positives.

### case_id=5134 FP boilerplate_overlap

- 方法: `readTwitterFead` vs `createHTML`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a Twitter feed via HTTP GET and returns the raw response as a string.
- B 摘要: Generates an HTML page by reading a CSS file and database content based on the requested page type, returning the HTML string.
- 静态失败原因: Static BERT likely overweights common boilerplate patterns (BufferedReader, while-readLine, try-catch) and misses the broader semantic context (HTTP vs database, simple vs complex output).
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clone because the functions have low lexical similarity, different purposes, and are not functionally equivalent; the shared reading-and-looping pattern is insufficient for Type-3/4 clones.
- 共享行为: Both read input line by line using BufferedReader；Both build and return a string result；Both handle IO exceptions
- 行为差异: A performs a single HTTP request; B reads a resource file and executes SQL queries；A returns raw JSON; B returns formatted HTML with conditional logic；B uses string concatenation predominantly; A uses StringBuilder；B takes an enum parameter; A takes no parameters
- 修正建议: Incorporate structural decomposition to distinguish simple IO from complex business logic；Use data-flow analysis to track the origin and transformation of the result string；Improve representation of method signatures and external API calls

### case_id=5135 FP boilerplate_overlap

- 方法: `main` vs `decodeFileToFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Main method that parses a Prolog file, generates adapter classes, and writes them to a JAR file.
- B 摘要: Decodes a file from Base64 and writes the decoded content to another file.
- 静态失败原因: The static model likely focused on structural patterns like file reading/writing, try-catch, and buffered streams, ignoring the distinct semantic contexts (Prolog parsing vs Base64 decoding).
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB considers these non-clones because they perform completely different high-level tasks despite sharing low-level file I/O patterns.
- 共享行为: Both involve file input/output operations；Both use try-catch for exception handling
- 行为差异: Function A parses Prolog and generates Java bytecode; Function B decodes Base64 data；Function A is a command-line main method; Function B is a utility method returning success flag；Function A writes a JAR file with multiple resources; Function B writes a single decoded file
- 修正建议: Incorporate more semantic understanding of method names and domain-specific APIs；Add context about the overall algorithm (e.g., parsing vs encoding)

### case_id=5136 FN lexical_or_api_overlap

- 方法: `doFinishLoadAttachment` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.4`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Saves an email attachment to external storage or opens it in a viewer, using content URI and handling IO exceptions.
- B 摘要: Downloads a KMZ file from a URL, unzips its entries, and writes them to local files using stream I/O.
- 静态失败原因: Low token Jaccard (0.111), different method names, parameters, and domain-specific APIs caused the model to focus on surface differences rather than the abstract stream-copy pattern.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB considers broad Type-3/Type-4 clones acceptable; both functions implement a common pattern of reading from a stream and writing to files, despite different domains and APIs.
- 共享行为: Open an input stream from a remote source；Copy data to a file output stream；Flush and close streams；Handle IOException
- 行为差异: Source: content URI vs HTTP URL；Attachment is optionally saved or viewed; KMZ is always extracted；Single file vs multiple zip entries；Uses MediaScannerNotifier in A, not in B
- 修正建议: Use data-flow analysis to capture stream open-copy-close pattern；Train on abstracted AST or graph representations to ignore API specifics；Include more training examples of stream I/O in varied domains

### case_id=5137 FN partial_functionality

- 方法: `doGet` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Handles HTTP GET request to retrieve and serve a page, with optional caching to a temp file.
- B 摘要: Copies a file from source to destination using a buffer.
- 静态失败原因: The models rely on token overlap and overall structure, which are low. The file-writing similarity is a small fragment within a long method, making it hard to detect without subgraph analysis.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have annotated this as a clone because both functions contain a file-writing sub-task that creates/overwrites a file and writes data, which could be considered a partial functionality clone (Type-3/4) under BCB's guidelines for semantic similarity.
- 共享行为: Both write data to a file (doGet writes page output to a temp file, copyFile writes bytes to destination file).
- 行为差异: doGet involves HTTP request handling, authentication, page retrieval, logging; copyFile is a simple file copy without any web context.
- 修正建议: Use code fragment alignment to detect partial functionality clones；Incorporate dataflow analysis to identify I/O operations that are semantically equivalent across different APIs；Apply graph-based models that can focus on sub-patterns in long methods

### case_id=5138 FN benchmark_preference_bias

- 方法: `unzipModel` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Extracts a zip file to a temporary directory using ZipInputStream and BufferedOutputStream.
- B 摘要: Configures and launches an Eclipse project with Maven support, processing XML files and setting Hibernate properties.
- 静态失败原因: Static model correctly identified semantic dissimilarity under strict equivalence, but BCB's broad criteria may accept such pairs as partial clones.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may annotate as clone due to both being utility methods that handle file resources and throw exceptions, fitting a broad Type-4 category.
- 共享行为: Both perform file I/O operations；Both catch exceptions and throw custom errors
- 行为差异: Different core purpose: unzip vs. Eclipse launch configuration；Different control flow: sequential loop vs. conditional branching with callbacks
- 修正建议: Re-evaluate if BCB annotation is correct; if so, train model to recognize very abstract similarity patterns.；Alternatively, refine BCB guidelines to avoid such loose clone definitions.

### case_id=5139 FN partial_functionality

- 方法: `fileDownload` vs `getNetworkServersIPs`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a file from a URL and writes it to a local directory with a fixed name.
- B 摘要: Connects to a URL, parses lines to extract server IPs from a specific format, and returns them as a vector.
- 静态失败原因: The model relied on token-level overlap and functional semantics. Low Jaccard similarity (0.21) and clearly different purposes (download vs parse) led to non-clone prediction. It may not be trained to recognize such broad structural clones with low lexical overlap.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have considered both as 'URL reading' functions, emphasizing structural similarity of opening a connection and reading input, ignoring different purposes and outputs, aligning with a broad Type-4 clone definition.
- 共享行为: Open a URL connection and read input from it.
- 行为差异: A writes input to a file (download), B parses input to extract IPs and returns them.；A reads character-by-character, B reads line-by-line.；A uses fixed output filename, B returns dynamic collection.；Exception handling: A catches generic Exception, B catches specific exceptions.
- 修正建议: Use a clone detector that captures structural patterns beyond token overlap, e.g., AST-based or graph-based methods that consider control flow and data flow similarities.

### case_id=5140 FP partial_functionality

- 方法: `handleHandshake` vs `loadURL`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Handles Minecraft handshake by validating server key and performing login via HTTP request.
- B 摘要: Downloads a URL content to a temporary file, with optional HTTP authentication and progress display.
- 静态失败原因: The static model may have focused on common API calls (URL, BufferedReader, InputStreamReader) and ignored distinct control flow and purposes, leading to a false positive.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely considered these non-clones because although both use URL connections, their overall functionality (authentication vs. file download) and internal logic differ significantly; token similarity is low.
- 共享行为: Both open a HTTP URL connection and read response using BufferedReader.
- 行为差异: func_a reads a single line to check 'ok', then sends login packet or disconnects; func_b reads multiple lines and writes them to a file, updating a status label.
- 修正建议: Incorporate control flow and data flow analysis to capture task-level semantics.；Use graph-based representations to differentiate single-line vs. multi-line reading patterns.

### case_id=5141 FP boilerplate_overlap

- 方法: `addQDInformation` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Updates project information by reading a local or remote data file containing date and project value pairs.
- B 摘要: Fetches Google image URLs for a music track's artist and album by parsing HTML response.
- 静态失败原因: Static BERT relied on surface-level similarities like URL, BufferedReader, try-catch, and string parsing, which are common boilerplate patterns, and failed to capture the semantic difference.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clone because the functions serve completely different purposes (data update vs. web search) and the implementation details differ significantly beyond boilerplate.
- 共享行为: Both use URL connections and BufferedReader to read text data line by line；Both parse lines for specific patterns；Both handle exceptions with try-catch blocks
- 行为差异: A reads from a fixed URL/file with specific format (pg, pt lines); B constructs a dynamic URL and parses HTML anchors；A modifies internal project info objects; B adds URLs to a list；A handles local file fallback; B does not
- 修正建议: Use data flow or control flow analysis to differentiate boilerplate from core logic；Leverage method names and comments for semantic cues；Train with more negative examples that share API patterns but differ in purpose

### case_id=5142 FP lexical_or_api_overlap

- 方法: `readRemoteFile` vs `importSequences`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a remote file line by line and returns the entire content as a single concatenated string.
- B 摘要: Parses remote file content in FASTA format, extracting sequence names and sequences into separate lists.
- 静态失败原因: The static model likely overweights common structural patterns (URL.openStream, BufferedReader, try-catch) and fails to capture the divergent core logic (simple concatenation vs. format-specific parsing).
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels as clones only when functions exhibit substantial semantic similarity beyond shared API usage. Here, the overall functionality (reading vs. parsing) differs significantly, so BCB likely considers them non-clones.
- 共享行为: Both open a URL input stream and read data from it.；Both handle IOException and EOFException during reading.
- 行为差异: Function A returns a single string; Function B populates two lists and returns void.；Function A reads all lines unconditionally; Function B parses lines looking for '>' delimiters and uses an ImportHelper class.；Function A catches exceptions locally and prints a message; Function B catches exceptions and prints stack trace or ignores them.；Function A has a simple read loop; Function B has complex parsing logic with tokenization and sequence assembly.
- 修正建议: Incorporate data-flow analysis to track how input is transformed (string vs. structured lists).；Train on more diverse pairs with similar APIs but different semantics to reduce API-based false positives.；Use code summarization or contrastive learning to distinguish generic read from specific parsing.

### case_id=5143 FP lexical_or_api_overlap

- 方法: `handleHandshake` vs `lookupFutureEvents`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Handles Minecraft server handshake packet by validating server key and initiating login or disconnection.
- B 摘要: Retrieves future events from Meetup API via HTTP and parses JSON response into Event objects.
- 静态失败原因: The static model may have been misled by shared tokens like 'URL', 'BufferedReader', 'InputStreamReader', 'url.openStream()', 'readLine()', 'close()', exception handling patterns, and general boilerplate for reading from a URL.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled non-clone because the functionalities are entirely different (handshake vs event lookup). Even though both involve network I/O, the purpose and usage are unrelated.
- 共享行为: Both use URL and BufferedReader to read from a network stream (HTTP connection)；Both handle exceptions；Both involve parsing strings
- 行为差异: Different protocols (Minecraft vs Meetup API)；Different input parsing (hex vs JSON)；Different output (network packet vs list of Event objects)；Different logic (authentication vs data retrieval)
- 修正建议: Improve the model to better distinguish between similar boilerplate and actual functionality；Use control flow or data flow analysis；Consider adding type information or method names

### case_id=5144 FN benchmark_preference_bias

- 方法: `createFile` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Copies a file to a resource manager using file streams.
- B 摘要: Builds HTML pages for editing by transforming XML with XSLT and writing output files.
- 静态失败原因: Static BERT models rely on token overlap and structural similarity; the extremely low token Jaccard (0.0566) and vastly different code lengths caused the model to correctly predict non-clone. The BCB label is likely an annotation error or an overly lenient judgment.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled these as clones due to a very broad interpretation of Type-4 similarity, considering both as operations that read input and write output files, or perhaps due to both involving file I/O with streams. However, this is not typical for BigCloneBench, which usually requires more substantial functional overlap.
- 共享行为: Both read from a source and write to a destination.；Both handle IOException.；Both use InputStream and OutputStream for file I/O.
- 行为差异: Function A is a simple file copy; function B is a complex web site generation process.；Function B involves XSLT transformation, DOM parsing, and string manipulation; function A does not.；Function B writes multiple output files and processes many pages; function A writes a single file.；Function B has many parameters and conditionals; function A has few.
- 修正建议: Improve annotation consistency in benchmark by requiring clearer functional equivalence for clones.；Incorporate data flow or dynamic analysis to capture deeper semantic similarity beyond lexical overlap.；Use domain-specific features to recognize common I/O patterns when appropriate.

### case_id=5145 FN benchmark_preference_bias

- 方法: `modifyApplicationMessage` vs `createJAR`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `preference_memory_with_manual_audit`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Reads a localized properties file, modifies or adds a key-value pair for a message, and writes the file back.
- B 摘要: Creates a JAR file or directory, copies a resource JAR, serializes a document object into a file, and places it inside the JAR/directory.
- 静态失败原因: Static BERT models rely on token embeddings and may capture only surface-level commonalities. The low Jaccard similarity and distinct domain-specific operations (properties vs JAR) likely caused the model to deem them non-clones, missing the broad BCB definition.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might consider both as 'file modification' methods with similar boilerplate (file handling, error handling), leading to a Type-4 functional similarity despite different specific tasks.
- 共享行为: Both methods involve file I/O operations.；Both handle exceptions with try-catch and printStackTrace.；Both use File and FileOutputStream classes.
- 行为差异: Function a manipulates properties files (text-based key-value pairs), while function b creates JAR archives with serialized objects.；Function a modifies existing content; function b creates new files and directories.；Function a uses BufferedReader and StringBuilder; function b uses FileChannel and ObjectOutputStream.
- 修正建议: Introduce training examples that emphasize high-level functional similarity despite syntactic differences.；Incorporate task-specific features like file type or I/O patterns.；Use a more comprehensive semantic understanding, possibly through code summarization or API usage graphs.

### case_id=5146 FN partial_functionality

- 方法: `getWebPage` vs `seeURLConnection`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads web page from given URL and returns content as string, with error handling that throws Error.
- B 摘要: Reads web page from hardcoded URL, appends lines to StringBuffer, and logs the content, throwing Exception on failure.
- 静态失败原因: Static BERT models (e.g., GraphCodeBERT) rely heavily on token sequences, function signatures, and lexical overlap. The low Jaccard similarity (0.1236), different method names, return types, exception handling, and hardcoded URL vs parameter likely led to a false negative. The shared data flow pattern of reading and concatenating lines was not captured.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often annotates as clone when the core algorithm (reading web content line by line) is present, even if signatures, return types, or minor implementation details differ. The functional similarity in retrieving web content qualifies as a Type-3 clone.
- 共享行为: Both read from a URL line by line；Both concatenate lines into a string builder (StringBuffer/String concatenation)
- 行为差异: A returns the content as String; B logs the content and returns nothing.；A uses a URL parameter; B hardcodes a specific URL.；A throws Error on IOException; B throws Exception.；A uses openStream(); B uses URLConnection.getInputStream() and closes the BufferedReader.
- 修正建议: Augment training data with more Type-3/Type-4 clones that differ in syntactic form but share core behavior.；Incorporate data-flow analysis or control-flow graph features to capture structural similarities.；Use contrastive learning with positive pairs that have low token overlap but high semantic similarity.

### case_id=5147 FN partial_functionality

- 方法: `uploadFile` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.2`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Uploads a file to a target path by renaming or copying using stream I/O.
- B 摘要: Launches a NexOpen project configuration, processing Maven POM files and setting up Hibernate reverse engineering resources.
- 静态失败原因: Static BERT models rely on lexical/syntactic overlap and local patterns; the very low token Jaccard (0.07) and vastly different vocabulary led to a non-clone prediction, missing the sparse shared file I/O patterns that BCB considered sufficient.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled these as clones based on broad file I/O operations and boilerplate patterns like stream copying, despite drastically different high-level purposes.
- 共享行为: Both perform file I/O operations (read/write streams)；Both check file existence and create directories/files as needed
- 行为差异: Function A is a simple file upload; Function B is a complex Eclipse launch configuration setup；Function A uses standard Java IO; Function B uses Eclipse/IDE APIs and XML processing；Function B includes error handling with logging and rethrowing as RuntimeException；Function B interacts with project resources and persistent properties
- 修正建议: Incorporate cross-function structural alignment to detect shared low-level operations in diverse contexts；Use data augmentation to emphasize small behavioral clones amidst large unrelated code

### case_id=5148 FN partial_functionality

- 方法: `copyFile` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Copy contents of a source file to a destination file using byte streams.
- B 摘要: Build a website for editing by processing pages, transforming XML, reading and writing multiple files, and performing string replacements.
- 静态失败原因: The model likely relied on low token overlap and structural differences, missing the shared low-level file copy pattern due to the overwhelming complexity and length of the second function.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider this a clone because both functions involve file I/O with reading and writing, and the low-level copy operation appears within the larger method, albeit as a small part.
- 共享行为: Both read from a file using FileInputStream；Both write to a file using FileOutputStream
- 行为差异: copyFile simply copies bytes without any transformation；buildSiteForEdit applies XSLT, string replacements, loops over pages, and handles multiple files
- 修正建议: Use dataflow analysis to detect common I/O patterns；Focus on method-level semantic role rather than surface syntax；Incorporate call-graph information to match utility functions

### case_id=5149 FP lexical_or_api_overlap

- 方法: `getLinksFromURLFast` vs `createHTML`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Parses HTML from a URL to extract anchor links and their text into two parallel vectors.
- B 摘要: Builds an HTML page string for a dashboard, including CSS and dynamic content from a database query.
- 静态失败原因: Static models may focus on superficial token overlap (e.g., BufferedReader, InputStreamReader, string building) and miss semantic differences in purpose and logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels as non-clone because the functions perform completely different tasks with no shared core functionality.
- 共享行为: Both read input using BufferedReader and InputStreamReader；Both construct strings by appending lines
- 行为差异: Function A extracts links from external HTML; Function B generates HTML for UI；Function A uses regex to find links; Function B uses switch-case and database queries；Different input/output types and overall purpose
- 修正建议: Incorporate method name and input/output type analysis；Use control flow and data flow representations to distinguish different algorithms；Consider the overall task (extraction vs generation) as a discriminator

### case_id=5150 FP boilerplate_overlap

- 方法: `download` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Downloads a file from the classpath to a user-selected location using IOUtils.copy.
- B 摘要: Handles GUI action commands, including file selection and preference saving for a genealogy application.
- 静态失败原因: The static model likely overfitted on the shared boilerplate code (e.g., try-catch-finally for streams) and generic file-choice interactions, missing the vast difference in overall program logic and method names.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels these as non-clones because they implement entirely different functionalities despite sharing some boilerplate I/O patterns. BCB emphasizes semantic equivalence and core purpose over structural similarity.
- 共享行为: Both involve file I/O operations.；Both use try-catch-finally for stream/resource management.
- 行为差异: A is a focused download function; B is a large event handler with multiple conditional branches.；A uses Activator.showSaveDialog; B uses JFileChooser for file selection.；A copies a resource stream to a file; B saves user preferences and updates GUI components.；B contains extensive logic for different commands and UI updates, which A lacks.
- 修正建议: Enhance model with control-flow and data-flow analysis to distinguish core logic from boilerplate.；Incorporate method-level context such as method name and class membership.；Use AST-based differencing to ignore common structural patterns that do not affect semantics.

### case_id=5151 FN partial_functionality

- 方法: `doGet` vs `doGet`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Handles GET requests by retrieving a portal page by ID or name, checking user permissions, logging, rendering the page, and optionally caching the output.
- B 摘要: Handles GET requests by translating the request path to a file and streaming its entire content to the response.
- 静态失败原因: Static BERT/GraphCodeBERT relies on syntactic structure and token overlap, which are very different due to distinct API usage (Page vs File, logging vs none, complex vs simple control flow). It failed to capture the high-level semantic similarity of content-serving behavior.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as Type-4 semantic clones because they fulfill the same high-level functionality: processing an HTTP GET request by locating a resource and sending it to the client, with conditional checks for resource existence.
- 共享行为: Both are HTTP GET handlers that write content to the response output stream；Both retrieve a resource (Page or File) based on request information；Both conditionally handle resource unavailability (A sends error, B checks existence)
- 行为差异: A retrieves a Page object with authorization checks; B directly serves a file without authentication；A includes extensive logging and caching; B has no logging or caching；A handles multiple error scenarios (SC_NOT_FOUND, SC_FORBIDDEN); B only outputs nothing if file missing or throws IOException；A writes complex HTML output with timing info; B writes raw file bytes
- 修正建议: Train models to recognize method-level intent based on common patterns like 'read resource → output to response'；Incorporate method names and context (e.g., servlet environment) as features；Use contrastive learning on functional equivalence pairs

### case_id=5152 FN lexical_or_api_overlap

- 方法: `transformSingleFile` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.4`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Transforms X3D editor file to gzipped x3dv file, returning its absolute path.
- B 摘要: Retrieves a resource by name from cache or URL, returning an InputStream.
- 静态失败原因: Low token Jaccard (0.132) and different method names lead static BERT to classify as non-clone. It fails to capture structural similarities that BCB might consider.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB might consider them clones due to structural similarity: both methods read input, process byte by byte, write output, and handle errors. However, the functional purpose differs significantly.
- 共享行为: Both perform file I/O with streams and byte-level copying.；Both have try-catch blocks returning null on exception.；Both involve reading from a source and writing to a destination.
- 行为差异: A compresses with GZIP; B does HTTP caching without compression.；A uses editor-specific objects; B uses URL connections and cache.；A returns a file path string; B returns an InputStream.
- 修正建议: Increase sensitivity to structural patterns beyond lexical tokens.；Use graph-based representations to capture control flow similarities.

### case_id=5153 FN benchmark_preference_bias

- 方法: `main` vs `parseContent`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a URL, unzips it, and writes entries to files.
- B 摘要: Parses HTML content from a stream, extracts metadata, links, and language, and adds fields to a document.
- 静态失败原因: The static model correctly recognized the low token overlap (0.075) and the distinct functional purposes, leading to a non-clone prediction. It failed to match the BCB label, which may be considered erroneous from a strict semantic perspective.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as a clone due to both functions involving reading from an input stream and processing data, which could be considered a broad Type-4 clone (similar functionality at an abstract level). However, the functional similarity is very weak and likely a labeling error.
- 共享行为: Both read from an input stream and process data in a loop.；Both handle I/O operations and exceptions.
- 行为差异: A is specific to ZIP file extraction; B is for HTML parsing and metadata extraction.；A writes extracted entries to files; B adds fields to a document object.；B involves charset detection, meta tag parsing, and link extraction, which A does not.；B has complex logic for determining language and robot directives.
- 修正建议: Review BCB annotation guidelines to ensure consistent labeling, especially for functions that only share broad I/O operations.；Consider excluding trivial main functions from clone detection benchmarks.；Improve static models to be more robust against such annotation noise.

### case_id=5154 FP boilerplate_overlap

- 方法: `googleImageSearch` vs `startScript`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.85`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Performs a Google image search by fetching and parsing HTML to extract image URLs.
- B 摘要: Loads a script from a URL and appends it to a dialog script line by line.
- 静态失败原因: Static models like GraphCodeBERT may overemphasize the structural similarity of the URL-fetching and line-reading pattern, missing the context that the purpose and output processing are completely different.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled these as non-clones because despite the similar URL-reading boilerplate, the core functionality (image search vs. script loading) is entirely different and would not be considered semantically equivalent.
- 共享行为: Both open a URL and read its content line by line using BufferedReader.
- 行为差异: Function A constructs a search URL and parses HTML for image links; Function B simply reads and concatenates lines.；Function A has a condition check on artist; Function B has none.；Function A catches generic Exception; Function B catches IOException and exits.；Function A adds results to a list; Function B appends to a string.
- 修正建议: Train on tasks that require distinguishing task semantics even when boilerplate overlaps.；Use contrastive learning that emphasizes functional differences in processing beyond input/output.

### case_id=5155 FP lexical_or_api_overlap

- 方法: `makeBackup` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Backup files from a source directory to a destination directory, creating subdirectories and copying files.
- B 摘要: Handle action events in a configuration dialog, setting application preferences and updating UI components.
- 静态失败原因: Static BERT/GraphCodeBERT may have been misled by the presence of similar variable names (e.g., 'File', 'destinationFile', 'sourceFile', 'checkdir') and file I/O operations in both, but the context is different. The model might have overgeneralized I/O patterns without understanding the high-level intent. Also, both functions contain loops and exception handling, which are common boilerplate.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled non-clone because the functions are from completely different domains (file backup vs GUI event handling) with no semantic similarity. Even under broad Type-4, they serve different purposes.
- 共享行为: Both use File objects；Both have loops and conditional checks；Both involve file path construction
- 行为差异: Function A performs file copying for backup; Function B manages UI settings and preferences；Function A is a static utility method; Function B is an instance method overriding actionPerformed；Function A uses FileInputStream/FileOutputStream for byte copying; Function B uses Swing components and JFileChooser；Function A has no UI interaction; Function B interacts with UI components and shows dialogs
- 修正建议: Improve representation to capture high-level intent；Use control flow and data flow analysis to distinguish backup logic from UI event handling；Incorporate API usage patterns specific to domains (e.g., JFileChooser vs FileInputStream)

### case_id=5156 FN partial_functionality

- 方法: `setMembers` vs `read`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches a Trac ticket page and extracts options from two select elements (component and priority) using regex.
- B 摘要: Opens a URL or file input stream and reads data, returning a status code.
- 静态失败原因: Low token overlap (0.178) and different control flow structures; shared API calls (URL, openStream) were overshadowed by differing overall logic and variable names, leading the model to focus on surface-level differences.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB annotator may have considered both as operations that fetch data from a URL, thus sharing high-level behavior of URL-based data retrieval despite different specific processing.
- 共享行为: Both attempt to open a URL stream；Both handle IOException
- 行为差异: Code a parses HTML for specific select tags, code b just passes the stream to another read method；Code a populates class fields with string arrays, code b returns an integer status；Code a reads text line by line, code b uses BufferedInputStream；Code a uses regex for pattern extraction, code b does not
- 修正建议: Enhance model with dataflow or control-flow awareness to distinguish different processing intents；Use contrastive learning to teach model that similar API usage with different purposes is not a clone

### case_id=5157 FP lexical_or_api_overlap

- 方法: `handledRun` vs `getFullScreenUrl`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Downloads and updates gamedata XML from a remote URL if a newer version is available.
- B 摘要: Fetches a YouTube page to extract video metadata and constructs a download URL.
- 静态失败原因: Static BERT/GraphCodeBERT models rely heavily on lexical and structural patterns (e.g., URL, BufferedReader, try-catch), leading to false positive when two functions share common API usage but differ in logic and data flow.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels as non-clone (0) when functions have different high-level purposes despite superficial API overlap. Here, downloading game data and fetching YouTube URLs are distinct tasks, so BCB considers them non-clones.
- 共享行为: Both open a URL connection and read remote data via BufferedReader.；Both parse lines of text to extract information.；Both handle exceptions with try-catch blocks.；Both perform I/O operations on streams.
- 行为差异: Function A updates local game data files; Function B extracts YouTube video parameters to build a URL.；Function A writes to a file; Function B only reads and returns a string.；Function A uses version comparison; Function B parses specific patterns (e.g., video_id, t).；Function A has a finally block that reloads game data; Function B has no such cleanup.
- 修正建议: Introduce dataflow analysis to capture variable dependencies and control flow differences.；Use AST-based or program graph representations that distinguish between file writing and string construction.；Incorporate task-level or domain-specific knowledge via fine-tuning on similar clone benchmarks.

### case_id=5158 FP partial_functionality

- 方法: `main` vs `readAndRewrite`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Main method for a tool that generates adapter classes from Prolog files.
- B 摘要: Reads a DICOM image and rewrites it to another file.
- 静态失败原因: Static BERT models may overgeneralize on superficial patterns like file reading/writing, error handling, and common API calls, ignoring the distinct domain-specific logic and overall purpose.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB labels non-clone because the functions have no meaningful functional similarity beyond generic I/O, lacking even broad Type-3/Type-4 overlap.
- 共享行为: Both perform file I/O and output results
- 行为差异: Different domains (Prolog vs DICOM)；Different processing steps (parsing, class generation vs pixel data handling)；Different output types (JAR file vs image file)
- 修正建议: Incorporate domain-specific knowledge or method name embeddings；Enhance model's ability to capture long-range semantic structure；Use contrastive learning to differentiate between genuinely similar high-level patterns and coincidental lexical overlap

### case_id=5159 FN partial_functionality

- 方法: `saveAttachmentBody` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Saves an email attachment body to a file and updates the content provider with its size and URI.
- B 摘要: Downloads a KMZ file from a URL, extracts its zip entries, and writes each entry to a separate file.
- 静态失败原因: Static BERT/GraphCodeBERT models rely on lexical and structural overlap, which is very low (token Jaccard 0.12381). The models fail to recognize the high-level pattern of stream copying because the specific API calls (e.g., part.getBody() vs URL.openStream()) and control flow differ significantly. The model correctly predicted non-clone based on lack of observable similarity, but BCB considered them clones due to a broad functional interpretation.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled this as a clone based on a very broad interpretation of Type-4 (similar functionality, different context): both functions perform file I/O by reading from an input stream and writing to a file output stream, despite different domains and additional operations. However, the low lexical similarity and differing specifics suggest this is likely a boundary case or potential labeling error.
- 共享行为: Both read from an InputStream and write to a FileOutputStream.；Both involve file creation and stream closure.；Both handle IOException and possibly other exceptions.
- 行为差异: Function A writes a single file and updates a content provider with metadata; Function B writes multiple files from a zip archive.；Function A uses Part.getBody().getInputStream() as input source; Function B uses URL.openStream() or FileInputStream.；Function A includes database update operations; Function B does not.；Function B iterates over zip entries; Function A does not involve zip extraction.
- 修正建议: Enhance models to capture abstract I/O patterns beyond surface token overlap.；Include more robust dataflow analysis to identify similar input-output transformations.；Use contrastive learning with broader clone definitions to handle Type-4 clones.

### case_id=5160 FN benchmark_preference_bias

- 方法: `doGet` vs `createNew`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Handles an HTTP GET request to resolve a page, check visibility, render and optionally cache the output.
- B 摘要: Creates a new file resource by writing an input stream to a file if the user is the owner.
- 静态失败原因: Static BERT relies on lexical and structural overlap; the low token Jaccard (0.085) and different API usage led to a correct non-clone prediction under strict semantic criteria, but it missed the potential broad similarity BCB annotators may have seen.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have considered both as resource management functions with similar control flow patterns (if-else, error handling) despite different domains, reflecting a broad Type-4 similarity.
- 共享行为: Both involve I/O operations；Both include authorization checks (visibility/ownership)；Both use try-catch for error handling
- 行为差异: A is a web page handler with complex rendering and caching; B is a simple file writing method；A returns void; B returns Resource；A uses servlet API; B uses file I/O；A has multiple error handling branches; B has simple error logging
- 修正建议: Incorporate domain knowledge about resource creation and request handling；Use graph-based code representations to capture structural patterns；Train with more diverse examples of broad Type-4 clones

### case_id=5161 FN boilerplate_overlap

- 方法: `getHTML` vs `readGeoParserResult`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches HTML from a URL and optionally saves it to a file, returning the HTML string.
- B 摘要: Reads geo-parser result content, constructs an XML request to a GeoParser service, parses the response to extract place names and gazetteer IDs, with retry logic.
- 静态失败原因: The static model likely focused on the low token-level similarity (Jaccard=0.13) and the different method names, return types, and core logic. It may have missed the broader structural pattern that BCB annotators considered. The model may rely heavily on local lexical and syntactic features, failing to capture the abstract similarity of network IO boilerplate.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB annotators may have considered the overall structure of establishing a URL connection, reading line by line in a while loop, and returning a result as a common pattern. Despite different core logic, the skeleton of IO with error handling might be seen as a Type-3 clone with significant modifications. Additionally, both functions involve string building from network input.
- 共享行为: Both open a URL connection and read lines into a string using BufferedReader；Both handle exceptions with try-catch；Both return a result (String or Collection)；Both use encoding/character set
- 行为差异: A is a simple HTML fetch; B involves complex XML construction and parsing；A optionally writes to file; B has retry logic and conditional logic；B parses structured data (XML) and extracts specific fields; A just reads raw lines；A uses HttpURLConnection with User-Agent; B uses URL.openStream()
- 修正建议: Incorporate structural pattern matching that identifies common IO skeletons；Use graph-based representations to capture control flow and data flow similarities beyond tokens；Include features for exception handling patterns and resource management

### case_id=5162 FN partial_functionality

- 方法: `getNetworkServersIPs` vs `seeURLConnection`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads server IPs from a given URL by parsing lines after a marker.
- B 摘要: Connects to a fixed URL and logs all content read.
- 静态失败原因: The model likely focused on surface-level differences: return types, method names, parameters, and the added parsing logic in A, missing the common boilerplate of URL reading. It may not have recognized that the essential I/O pattern is identical.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider the common pattern of URL connection and line reading as the core behavior, viewing A's parsing as an extension of that base functionality, thus labeling them as clones (Type-4 or broad Type-3).
- 共享行为: Both connect to a URL and open an input stream.；Both use BufferedReader to read lines in a loop.；Both handle IO exceptions (one explicitly, one by throwing).
- 行为差异: A parses lines with conditional flags and splits by ':', extracting specific data; B simply appends all lines to a buffer.；A returns a Vector of IPs; B returns void and logs the result.；A takes a URL parameter; B uses a hardcoded URL.
- 修正建议: Train with more examples that vary in parsing logic but share common I/O patterns.；Use attention mechanisms that highlight common API calls (URL, URLConnection, BufferedReader).；Incorporate structural alignment to match loop and stream usage patterns.

### case_id=5163 FP lexical_or_api_overlap

- 方法: `readUNI` vs `retrieveTemplate`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Parses tab-delimited lines from a URL and collects id-description pairs into a vector.
- B 摘要: Reads entire content from a blog URL, caches it, and returns as a string.
- 静态失败原因: Static BERT models may have been fooled by lexical overlap (URL, openStream, line reading pattern, scanner/BufferedReader) and token Jaccard similarity of 0.21, which is moderate; they may not capture the difference in data processing logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labeled not clone because the functions have distinct high-level purposes: one is parsing structured data, the other is fetching raw content; the shared URL reading is too generic.
- 共享行为: Both open a URL stream and read line by line.
- 行为差异: Different parsing: tab-separated vs raw lines；Different output: populate vector vs return string；Different caching: none vs caching the result；Different exception handling: catches and ignores vs throws Exception
- 修正建议: Include structural differences in parsing logic；Consider data flow/output types；Use more detailed semantic analysis of the loop body

### case_id=5164 FP boilerplate_overlap

- 方法: `encodeFileToFile` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.99`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Encodes a file using Base64 and writes the result to another file, returning success status.
- B 摘要: Handles GUI action events, updating preferences and UI components based on the action command.
- 静态失败原因: The static model may have been misled by common structural patterns like try-catch-finally blocks and variable names (e.g., 'filename'), or it overgeneralized on the presence of file-related operations without capturing the distinct semantic contexts of file I/O vs. GUI event processing.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the functionalities are entirely different (file encoding vs. GUI action handling) with no semantic similarity, even under broad Type-3/Type-4 criteria.
- 共享行为: Both use try-catch for exception handling；Both involve file paths in some way (A: file I/O, B: file chooser)
- 行为差异: A performs base64 encoding file transformation; B is a GUI event handler；A returns a boolean; B is void；A has a single loop and simple I/O; B has multiple if-else branches and UI updates；B deals with user interface components (JFileChooser, JTextField, etc.); A does not
- 修正建议: Incorporate data flow analysis to distinguish actual file I/O from file path handling in GUI；Improve context awareness to differentiate between utility methods and event handlers；Use call graph information to understand method purpose

### case_id=5165 FP boilerplate_overlap

- 方法: `googleImageSearch` vs `checkForUpgrade`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Performs a Google image search by constructing a URL, fetching HTML, parsing image URLs, and displaying the first image on a UI component.
- B 摘要: Checks for software upgrades by querying a license server, parsing XML-like response, processing upgrade records, and updating UI components.
- 静态失败原因: The static BERT/GraphCodeBERT model likely overfitted on common structural patterns (URL connection, BufferedReader, try-catch) and ignored the high-level semantic differences. The token overlap is low, but the model might have been misled by similar API sequences.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the overall functionality is completely different, despite some shared patterns like HTTP connection and UI interaction. BCB's Type-3/Type-4 annotations still require significant semantic overlap, which is absent here.
- 共享行为: Both make HTTP URL connections and read responses line by line using BufferedReader.；Both handle exceptions and interact with UI components (showing dialogs or updating labels).
- 行为差异: Function A performs image search; Function B performs software upgrade checking.；Function A parses HTML to extract image URLs; Function B parses XML-like data to extract upgrade records.；Function A uses a list of images and a counter; Function B uses database operations and MAC address collection.
- 修正建议: Add more diverse training data with similar API sequences but different semantics; use contrastive learning to distinguish true functional similarity from superficial API overlap; incorporate program dependency graphs to capture control/data flow differences.

### case_id=5166 FN boilerplate_overlap

- 方法: `modifyApplicationMessage` vs `downloadFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Modifies a localized properties file by updating or adding a key-value pair for a given message name.
- B 摘要: Downloads a file from S3, decrypts and decompresses it, and moves it to a target location.
- 静态失败原因: Static BERT/GraphCodeBERT relies on lexical and structural token overlap, which is very low (0.14). The abstract semantic pattern of file I/O is not captured, leading to a non-clone prediction.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may consider both as 'file manipulation' tasks with similar control flow patterns (try-catch, streams, file creation), thus labeling them as broad Type-4 clones.
- 共享行为: Both perform file I/O operations with error handling and resource cleanup.
- 行为差异: A reads and writes properties files; B downloads and decrypts binary data.；A modifies existing content; B creates new file.；A uses properties-specific parsing; B uses IOUtils copy.；A has locale handling; B has encryption.
- 修正建议: Train models to recognize higher-level patterns like 'resource acquisition, processing, release' beyond exact token matches.；Incorporate data-flow and control-flow features to detect similar skeleton structures.

### case_id=5167 FN partial_functionality

- 方法: `readFixString` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a fixed-length string from an input stream using IOUtils.copy and returns it.
- B 摘要: Configures and launches a NexOpen project build, involving file reading and I/O operations.
- 静态失败原因: The low token Jaccard (0.072) and minimal lexical overlap caused static models to miss the partial functional pattern, focusing instead on the different vocabularies and structures.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considered the common pattern of IOUtils.copy usage and exception handling as sufficient functional overlap, accepting a broad Type-4 clone despite different overall purposes.
- 共享行为: Both use IOUtils.copy to read data from an input stream to an output.；Both catch IOException and wrap it in a RuntimeException.；Both perform I/O operations on streams or files.
- 行为差异: readFixString reads a fixed-length string and returns it; launch reads multiple files and performs project configuration.；readFixString is a simple utility; launch has complex logic with XML parsing, property setting, and job scheduling.；The input source in readFixString is a limited input stream; in launch it's project files based on configuration attributes.
- 修正建议: Incorporate API call awareness and functional patterns beyond lexical tokens.；Use graph-based models to capture data flow and common library usage.；Include training examples with partial functionality similarity.

### case_id=5168 FN benchmark_preference_bias

- 方法: `File2String` vs `run`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Reads a file from disk or classpath and concatenates all lines into a single string, exiting on error.
- B 摘要: Reads a URL, parses lines into version, URL, and information fields, handles errors with specific messages, and notifies listeners.
- 静态失败原因: Static models rely on token overlap and structure; low Jaccard index (0.1958) and different method names led to correct non-clone prediction, but BCB expected a clone due to abstract pattern similarity.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled as clone because both functions read lines from an input stream, a common pattern in text input processing, but overall functionality differs significantly.
- 共享行为: Both read lines from an input stream using BufferedReader
- 行为差异: Function A reads from a local file or classpath resource; Function B reads from a URL；Function A concatenates all lines; Function B parses lines into specific fields；Function A exits on error; Function B sets error flags and notifies listeners
- 修正建议: Improve BCB annotations to require more functional equivalence；Use dynamic analysis or data flow to capture I/O patterns

### case_id=5169 FN partial_functionality

- 方法: `addQDInformation` vs `seeURLConnection`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Updates project information by reading a data file either locally or from a URL, parsing lines with 'pg' and 'pt' prefixes to extract dates and project values.
- B 摘要: Opens a URL connection, reads the entire content, and logs it as a debug message.
- 静态失败原因: Static BERT models like CodeBERT rely on token-level similarity and may miss the structural I/O pattern overlap due to low token Jaccard and the presence of many distinctive tokens in A (e.g., 'qdinfo', 'pg', 'pt', 'projectNum', 'Information'), which overshadow the common URL-reading tokens.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider these clones due to the shared subroutine of opening a URL and reading lines, treating the additional functionality in A as context-specific modifications, especially since BCB often annotates Type-4 clones that have similar I/O operations despite different overall goals.
- 共享行为: Both open a URL connection and read data line by line using BufferedReader.
- 行为差异: Function A also handles local file, checks modification date, clears cached values, and parses structured lines; Function B simply concatenates all lines without parsing.
- 修正建议: Use dataflow analysis to detect similar I/O patterns; apply subgraph matching for common API call sequences; incorporate task-agnostic structural similarity measures beyond token overlap.

### case_id=5170 FN partial_functionality

- 方法: `readAndRewrite` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.4`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a DICOM file and rewrites it to another file with pixel data processing.
- B 摘要: Retrieves a resource by name, either from a cache or by downloading and caching it.
- 静态失败原因: The model relied on lexical overlap and structural similarity; low token Jaccard and different API usage led it to predict non-clone, missing the abstract I/O pattern that BCB may have valued.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have considered them clones due to shared low-level stream reading/writing patterns and exception handling, despite different high-level functionalities.
- 共享行为: Both use BufferedInputStream and BufferedOutputStream for file I/O；Both print progress messages to stdout；Both handle IOException with try-catch or throws
- 行为差异: A operates on DICOM medical images with specific parsing; B retrieves generic resources via HTTP；A writes pixel data; B caches downloaded resources；A uses ImageInputStream/OutputStream; B uses URLConnection；A is private static; B is public synchronized
- 修正建议: Incorporate representation of abstract file I/O operations beyond surface tokens；Better distinguish between domain-specific and generic I/O patterns；Use graph-based models that capture data flow and stream handling

### case_id=5171 FP lexical_or_api_overlap

- 方法: `readTwitterFead` vs `writeFileType`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Downloads a Twitter timeline from a fixed URL and returns the response body as a string.
- B 摘要: Reads a file of URIs, downloads each URI's content, classifies it by RDF keywords, and writes the classification to an output file.
- 静态失败原因: The static BERT model likely overfitted to lexical and API-level overlaps (e.g., BufferedReader, InputStream, HttpGet, URL) and failed to capture the distinct control flow and output behavior. The high token Jaccard (0.14) may have contributed, but the structural differences in loops, file I/O, and classification were ignored.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels these non-clones because the overall functionality is completely different: one is a simple HTTP GET returning a string, the other is a batch URI classifier that writes to a file. The only superficial similarity is the use of HTTP reading patterns, which is insufficient for Type-3/4 clones.
- 共享行为: Both use HTTP connections to read data from URLs.；Both read data line by line using BufferedReader.；Both handle exceptions (IOException, ClientProtocolException, or general Exception).
- 行为差异: A performs a single download from a fixed URL and returns the entire content; B processes multiple URIs from a file and writes results to an output file.；A does not classify or write output; B includes classification logic for OWL/RDFS/RDF keywords and writes tab-separated results.；A uses HttpGet and DefaultHttpClient; B uses URL and URLConnection.；B includes a counter, skips first num lines, and limits line count per URL to 100; A has no such logic.
- 修正建议: Incorporate data flow analysis to distinguish between return value and file output.；Use abstract syntax tree (AST) or program dependency graph (PDG) matching to capture structural differences.；Train on more diverse examples of HTTP usage to avoid overgeneralization.；Include task-level semantics (e.g., classification vs. extraction) in the model.

### case_id=5172 FN partial_functionality

- 方法: `copyResource` vs `copyOverWarFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a single resource (URL or file) to a destination file using low-level byte streams and throws exceptions on failure.
- B 摘要: Copies multiple .war files from a source directory to an apps data directory, skipping if files already exist, and then performs unzipping and extraction, with logging and system property changes.
- 静态失败原因: Static BERT models rely on lexical and structural overlap, which is low (Jaccard 0.13). They fail to capture the abstract concept of file copying across different APIs and lengths, and are misled by the differing control flow and additional operations.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled them as clones because both involve the core functionality of copying file content from an input to an output, which is a common pattern. However, given the significant additional behavior in B, many BCB annotators might not consider them clones under broader Type-3/4 criteria.
- 共享行为: Both copy file content using InputStream and OutputStream
- 行为差异: A copies only one resource; B copies multiple war files conditionally.；A uses byte-by-byte copying; B uses IOUtils.copy.；A has no extra processing; B includes logging, file filtering, unzipping, and system property setting.；A throws exception; B catches exceptions and logs them.
- 修正建议: Train models to decompose functions into sub-tasks (e.g., I/O operations) and compare at a higher abstraction level.；Incorporate data-flow analysis to identify core I/O patterns.；Use contrastive learning on BCB's specific annotation guidelines that accept partial functional similarity.；Improve handling of long-range dependencies by using graph-based models (e.g., CodeGraphBERT) that capture data flow.

### case_id=5173 FP lexical_or_api_overlap

- 方法: `readZoneIDs` vs `downloadModel`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads integer zone IDs from a resource file and returns them as a set.
- B 摘要: Downloads an RDF model from a URL with custom HTTP headers and returns the model.
- 静态失败原因: Static BERT may have been misled by shared tokens like 'URL', 'openStream', 'InputStream', 'try', 'catch', and similar structural patterns of opening a connection and reading, despite low Jaccard similarity.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clones when the core functionality differs significantly, even if there is some overlap in API usage. Here, the tasks (reading zone IDs vs. downloading an RDF model) are distinct.
- 共享行为: Both open a URL connection and read from an input stream.；Both use try-catch blocks to handle exceptions.
- 行为差异: Function A returns a set of integers; function B returns an RDF model.；Function A reads lines and parses integers; function B reads RDF data into a model.；Function A uses a resource from the classpath; function B accesses external URLs with HTTP headers.；Error handling: A prints stack trace; B throws RuntimeException after logging.
- 修正建议: Incorporate dataflow and control-flow analysis to distinguish different data transformations.；Use semantic role labeling to capture the purpose of the function beyond API sequence.；Train on more examples with such mismatched functionality to reduce overreliance on superficial token overlap.

### case_id=5174 FN partial_functionality

- 方法: `doTransfer` vs `getXML`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Proxies an incoming HTTP request to a target URL, forwarding headers and body, and returning the response.
- B 摘要: Fetches an XML document from a servlet URL using GET and returns its content as a string.
- 静态失败原因: The model likely focused on token-level differences (low Jaccard) and structural dissimilarity, missing the high-level semantic similarity in performing HTTP requests.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as 'HTTP client' functions that fetch data from URLs, despite different levels of complexity.
- 共享行为: Perform HTTP communication with a remote URL；Read data from an InputStream；Handle IOException and MalformedURLException
- 行为差异: A forwards the full request/response including headers and method, while B is a simple GET；A uses output streams and writes to response, B returns string；A includes error forwarding logic, B returns null on exceptions
- 修正建议: Incorporate broader context or API usage patterns to recognize common HTTP communication logic；Use graph representations that capture control and data flow related to URL opening and stream handling

### case_id=5175 FN benchmark_preference_bias

- 方法: `readAndRewrite` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Reads a DICOM file, parses it, reads pixel data, and writes the dataset to an output file.
- B 摘要: Generates an editable version of a website by transforming XML templates and writing output files for each page.
- 静态失败原因: The static BERT model correctly predicted non-clone due to low token overlap and vastly different structure. The failure is not in the model but in the BCB label; the model's prediction aligns with our judgment.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB likely labeled this as a clone based on a very broad interpretation of 'file reading and writing' functionality, ignoring the completely different domains and complexity. This is likely an annotation error.
- 共享行为: Both involve file I/O operations (reading input and writing output)；Both use exceptions like IOException
- 行为差异: One is specialized for DICOM medical image format; the other is a generic web site builder；One uses specific DICOM libraries (DcmParser, PixelDataReader/Writer); the other uses XML transformers and file utilities；One is a short static method with linear flow; the other is a long public method with loops, conditionals, and many parameters；One operates on pixel data; the other on HTML/XML pages
- 修正建议: Re-evaluate BCB annotation for this pair; likely non-clone；Ensure annotators do not label general I/O tasks as clones across domains

### case_id=5176 FP lexical_or_api_overlap

- 方法: `copy` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Copies a file from source to destination using byte streams.
- B 摘要: Handles UI action events, updating settings and interacting with file choosers.
- 静态失败原因: The static model likely misclassified due to lexical overlap (e.g., both use 'File', 'IOException' or similar tokens) or because it was fooled by the common 'try-finally' pattern in function A and similar patterns in function B (though not present). The low Jaccard similarity (0.073) suggests the model may have relied on other spurious features.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels them as non-clones because they have no functional similarity: one is a utility file copy, the other is a GUI event handler with entirely different purpose and structure.
- 共享行为: Both involve file-related operations (file reading/writing vs file selection).
- 行为差异: Function A performs a simple file copy using InputStream/OutputStream; Function B is a complex event handler that updates UI settings and opens file choosers for multiple commands.；Function A has no UI interaction; Function B is deeply tied to a GUI framework.；Function A is short and focused; Function B is long and handles many different commands.
- 修正建议: Train models to better recognize structural differences and method purpose.；Incorporate method name and context (e.g., class hierarchy) to distinguish utility functions from event handlers.；Use dataflow analysis to detect different I/O directions (reading vs writing) or different roles of file objects.

### case_id=5177 FN partial_functionality

- 方法: `importRoles` vs `httpRequestByPOST`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.75`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads XML from a URL and parses RoleName elements into a list.
- B 摘要: Sends an HTTP POST request and returns the response body as a string.
- 静态失败原因: Static models like GraphCodeBERT often rely on token and structure similarity; here the Jaccard similarity is low (0.27) and the loops differ significantly (one checks for a closing tag, the other just appends). The model likely focused on these differences and missed the abstract commonality.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as Type-3/4 clones because they share the high-level pattern of 'fetch data from URL and process lines', even though the processing details differ.
- 共享行为: Both open a connection to a URL and read response line by line using BufferedReader；Both accumulate lines into a StringBuffer and return the processed result；Both handle IOExceptions
- 行为差异: A uses HTTP GET (via URL.openStream) while B uses HTTP POST；A parses XML to extract RoleName objects, B returns raw response string；B sets instance variables on error and returns null, A silently catches exceptions；B includes timeout and parameters parameters, A does not
- 修正建议: Include more training examples of tasks with similar I/O patterns but different inner logic；Use dataflow or program dependence features to capture high-level intent；Incorporate heuristics that recognize common boilerplate for HTTP requests

### case_id=5178 FP lexical_or_api_overlap

- 方法: `copy` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Copies a file character by character using FileReader and FileWriter.
- B 摘要: Handles action events to set application preferences like paths for external tools and UI settings.
- 静态失败原因: The static model likely over-relied on lexical features like 'File', 'filename', 'getAbsolutePath' which appear in both, and missed the structural and semantic differences due to the truncated code in B and the different method signatures.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would label as non-clone because the functions perform entirely different tasks (file copy vs. event-driven preference management) with no semantic overlap.
- 共享行为: Both involve file input/output operations；Both use File and file path strings
- 行为差异: Method A is a simple file copy; Method B is an event handler for multiple commands；Method A has no UI interaction; Method B uses JFileChooser and updates UI components；Method A terminates after copying; Method B may prompt for restart and shows dialogs；Method A has no user preferences; Method B reads/writes preferences
- 修正建议: Improve model to capture global program structure and control flow；Incorporate method signature and context (e.g., method name, class) to disambiguate；Use dataflow analysis to distinguish file I/O from preference setting

### case_id=5179 FN benchmark_preference_bias

- 方法: `doGet` vs `copy`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Handles HTTP GET request for a page: retrieves selected page parameter, looks up page by ID or name, checks user visibility, logs requests, renders page output, and handles caching and error responses.
- B 摘要: Recursively copies a file or directory from source to destination using FileChannel for efficient I/O.
- 静态失败原因: The static BERT/GraphCodeBERT model correctly predicted non-clone (0) due to very low token overlap (0.108), different method signatures, and distinct API usage. It failed to match the BCB label because the BCB label appears to be a misannotation. The model's prediction aligns with the expected behavior for non-clones.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as a clone under a very broad interpretation of Type-4 (semantic) clones, perhaps because both functions involve checking conditions (file/directory existence vs. page existence), handling null/error cases, and performing some logging. However, the core functionalities are entirely different.
- 共享行为: Both use Java exception handling (IOException, etc.)；Both have conditional logic and logging (myLogger.info/warning)
- 行为差异: Function A is a servlet method processing HTTP requests and interacting with a portal framework; Function B is a static utility for file system copying.；Function A involves page retrieval, user permissions, caching, and HTML output; Function B directly manipulates files and directories.；Function A relies on external classes like PortalRequest, Page, Property; Function B uses standard Java I/O classes (File, FileChannel).；Function A has complex control flow with multiple try-catch blocks and error handling specific to web server; Function B has a simple recursive structure.
- 修正建议: Re-evaluate BCB annotation for this pair; consider removing or correcting the label.；Use domain-specific embeddings that capture functional semantics beyond lexical overlap.

### case_id=5180 FN partial_functionality

- 方法: `copyResource` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource (from URL or file) to a destination file using single-byte reads and closes streams.
- B 摘要: Copies a source file to a destination file using a 1024-byte buffer and closes streams.
- 静态失败原因: The model likely focused on surface-level differences (method name, parameters, URL handling logic, exception types) and low token overlap (Jaccard=0.3125), failing to capture the common I/O pattern of read-write-close.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels file copying functions as clones despite differences in buffer size and source type because the core functionality (copying bytes from one location to another) is functionally similar under a broad Type-4 definition.
- 共享行为: Both copy data from an input stream to an output stream.；Both close the input and output streams after copying.
- 行为差异: A handles both URL and file sources; B only handles file sources.；A reads one byte at a time; B uses a 1024-byte buffer.；A throws generic Exception; B throws IOException.；A has no parameters and uses instance fields; B takes two File arguments.
- 修正建议: Train models to recognize common I/O patterns (e.g., open, read/write loop, close) as semantically equivalent.；Use data-flow analysis to abstract away buffer sizes and source types.；Enhance embeddings with structural information about stream copying operations.

### case_id=5181 FP lexical_or_api_overlap

- 方法: `actionPerformed` vs `recurseFiles`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `1.0`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Handles UI events for a configuration dialog, including file chooser and settings persistence.
- B 摘要: Recursively traverses directories and adds non-zip files to a ZipArchiveOutputStream.
- 静态失败原因: The static BERT model likely relied on lexical overlap (e.g., 'File', 'filename', 'if-else') and structural patterns present in both functions, but failed to capture the distinct semantic contexts and overall functionality differences.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB required Type-1 to Type-4 clones with significant semantic overlap; these functions share no common functionality beyond trivial use of Java File APIs.
- 共享行为: Both use File objects and file path strings
- 行为差异: Function A is a long UI event handler with multiple conditional branches; Function B is a short file compression utility；Function A interacts with user interface components and settings; Function B performs I/O with no user interaction；Function A handles actions for different commands; Function B is recursive and processes all files in a directory
- 修正建议: Enhance training with more examples of long and short functions to improve context discrimination；Incorporate data-flow and control-flow analysis to distinguish different execution paths

### case_id=5182 FN boilerplate_overlap

- 方法: `login` vs `run`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Logs into LOLA by sending a POST request with email and password, extracts session ID, sets session, and returns the session ID.
- B 摘要: Reads the content of a local JSP page line by line without any authentication or processing, discarding all lines.
- 静态失败原因: Static BERT models rely heavily on token overlap and surface forms; low Jaccard similarity (0.179) and different method names ('login' vs 'run') caused it to miss the structural similarity in HTTP request handling.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may consider both as performing HTTP communication via URLConnection and BufferedReader, and both have similar boilerplate code, leading to a broad Type-4 clone label despite different specific behaviors.
- 共享行为: Both open a URL connection and read from an input stream using BufferedReader；Both handle exceptions with try-catch blocks
- 行为差异: A uses POST with form data encoding and writes to output stream; B uses GET with no output；A extracts and sets session ID; B discards all read lines；A returns a non-void value; B returns void；A uses specific URL with login endpoint; B uses a different URL and no authentication
- 修正建议: Incorporate data flow analysis or graph-based representations to capture shared I/O patterns；Use models that handle long-range dependencies and partial functionality similarity；Augment training data with more Type-4 clone examples

### case_id=5183 FN partial_functionality

- 方法: `doVersionCheck` vs `seeURLConnection`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a version check URL, parses lines for .version and .build, compares build with current jEdit build, and notifies user of new version or up-to-date status, with error handling.
- B 摘要: Opens a URL, reads all lines into a string buffer, and logs the result, throwing exceptions outward.
- 静态失败原因: The static model likely focused on the low token overlap (Jaccard 0.194) and lexical differences (different method names, different URL strings, presence of UI-related code), missing the semantic similarity in the URL reading boilerplate. The model may have been misled by domain-specific terms and the distinct error handling patterns.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this as a clone because both functions share the core pattern of connecting to a URL, reading lines, and processing them via loops, which is a common boilerplate for network I/O tasks; the additional logic in one is seen as an extension of the shared functionality.
- 共享行为: Both open a URL connection；Both read lines using BufferedReader in a while loop；Both close the reader after reading
- 行为差异: doVersionCheck parses lines for specific prefixes (.version, .build) and compares build numbers; seeURLConnection simply appends all lines to a StringBuffer；doVersionCheck updates UI with new version or up-to-date message; seeURLConnection logs the content；doVersionCheck handles IOException with error message; seeURLConnection throws Exception；doVersionCheck manages wait cursor; seeURLConnection does not
- 修正建议: Train model to recognize common subpatterns like opening a URL and reading lines；Incorporate structural similarity of loop constructs；Use dataflow analysis to identify shared I/O operations；Include more examples of Type-4 clones with divergent additional logic

### case_id=5184 FN benchmark_preference_bias

- 方法: `copyFileByNIO` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Copies a file using NIO FileChannel from source to destination.
- B 摘要: Retrieves a resource InputStream via URL, with caching to a local file and HTTP conditional GET.
- 静态失败原因: The low token Jaccard (0.09) and large difference in structure and length likely led the model to correctly reject the pair; it did not fail but disagreed with the BCB label.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: Perhaps the BCB annotator considered both as 'file copy/transfer' operations, but the functionality is fundamentally different; this may be a labeling error or a very broad Type-4 interpretation.
- 共享行为: Both perform file I/O operations；Both deal with input/output streams
- 行为差异: A copies entire file via FileChannel.transferTo; B fetches resource over network；A uses NIO channels; B uses streams and URLConnection；B has caching logic, HTTP response handling, and prints debug info; A does not；B returns InputStream; A is void
- 修正建议: Review BCB annotation for this pair; likely a false positive in the benchmark；Use semantic similarity models that capture high-level intent beyond token overlap；Include context about method signatures and external library usage

### case_id=5185 FN benchmark_preference_bias

- 方法: `getResourceAsStream` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Retrieves a resource by name with caching, downloading if necessary, and returns an InputStream.
- B 摘要: Main method that parses command line arguments, reads an input file with encoding conversion, and writes to an output file.
- 静态失败原因: The static model likely focused on token-level differences, method name mismatch, and distinct library usage, correctly identifying non-clone nature.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider the shared boilerplate patterns (stream handling, try-catch, file operations) as sufficient for a Type-4 clone despite different functionality.
- 共享行为: Both use file I/O streams and buffers；Both have try-catch blocks with exception printing；Both create File objects and handle paths
- 行为差异: A involves HTTP URL connection and caching logic; B involves command-line parsing and encoding conversion；A returns an InputStream; B writes to an output file；A uses HttpURLConnection; B uses CmdLineParser and various reader/writer classes
- 修正建议: Increase weighting on high-level semantic purpose；Filter out boilerplate I/O and error handling patterns；Use dynamic analysis or trace information

### case_id=5186 FP long_range_semantics

- 方法: `actionPerformed` vs `handle`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `static_summary_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Handles GUI action commands for setting Graphviz/ImageMagick paths and other preferences, updating UI components.
- B 摘要: Handles log file rotation, compression with GZIP, and archiving of old log files.
- 静态失败原因: Static BERT may overemphasize lexical overlap (e.g., common keywords like 'File', 'if', 'try') and large method length, missing the distinct domain-specific logic and control flow of each function.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB labels non-clone because the two functions have entirely different purposes and implementations, despite both performing file I/O. The semantic gap is too large for any Type-3/4 similarity.
- 行为差异: Function A deals with GUI preference settings and file selection for external tools.；Function B deals with log file rotation, compression, and archival cleanup.；Different control flows: A uses event dispatch and multiple conditionals; B uses file channels and timestamps.
- 修正建议: Improve model capacity for long-range dependencies and better representation of method structure.；Incorporate structural features like AST or dataflow graphs.

### case_id=5187 FP boilerplate_overlap

- 方法: `main` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Signs a PDF document using iText library and verifies signatures with keystore and certificates.
- B 摘要: Handles action events to save user preferences for external tool paths and application settings in a GUI.
- 静态失败原因: The model likely overfitted on common API usage patterns (e.g., 'FileInputStream', 'FileOutputStream', try-catch) and ignored the high-level semantic differences, mistaking boilerplate code for functional similarity.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clone because the functions serve completely different purposes and share no functional similarity; they are from distinct application domains (PDF signing vs. GUI settings).
- 共享行为: Both use try-catch blocks for exception handling；Both involve file operations (reading/writing files)
- 行为差异: Function A focuses on PDF signing and verification with cryptographic operations；Function B manages GUI preferences for external tools and UI settings；Different libraries used (iText vs. Swing/Suku)；Different control flow (sequential signing vs. event-driven settings)
- 修正建议: Incorporate data-flow analysis to trace actual data transformations and distinguish different business logic.；Use program dependency graphs to capture semantic intent beyond surface syntax.；Train on more diverse examples to reduce reliance on boilerplate patterns.

### case_id=5188 FP lexical_or_api_overlap

- 方法: `sendPost` vs `handler`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Sends an HTTP POST request with parameters and returns the response body as a string.
- B 摘要: Reads a URL's content and parses lines to extract substrings based on target configuration, updating a map.
- 静态失败原因: Static BERT likely over-indexed on lexical and structural overlap (URL, BufferedReader, line reading, try-catch) while missing critical semantic differences in request method, output handling, and processing logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clone because the functions have completely different purposes (sending a POST vs parsing HTML), even under broad Type-4 similarity.
- 共享行为: Both use URL to establish a network connection；Both read input line by line using BufferedReader
- 行为差异: Function A performs a POST request with output; Function B performs a GET request without output；Function A returns the full response string; Function B updates a map with parsed substrings；Function A sets request properties and handles exceptions with a message; Function B catches exceptions silently；Function A writes request body; Function B does not
- 修正建议: Incorporate dataflow analysis to track variable usage and output types；Use control flow to distinguish POST vs GET and output vs side-effect patterns；Train on diverse IO examples with emphasis on different request methods and processing logic

### case_id=5189 FN partial_functionality

- 方法: `doTransfer` vs `fetchUrl`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Transfers HTTP request/response by proxying to a remote URL, copying headers, method, and body.
- B 摘要: Fetches the content of a URL as a string using a simple GET request.
- 静态失败原因: Static BERT/GraphCodeBERT may have focused on the shared key tokens like 'URL', 'openStream', 'read', 'while' loops, and ignored the structural differences in stream handling and request/response details. The low token Jaccard suggests limited lexical overlap, but the model might have relied on API-level similarity (e.g., URL, InputStream) without understanding the broader control flow.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled it as clone because both functions ultimately 'fetch data from a URL' and share the basic URL opening pattern. The annotation might consider partial functionality similarity (Type-4) where only a subset of behaviors overlap, or they may have missed the additional complexity in A.
- 共享行为: Both create a URL object and open an input stream to read data from the given URL.
- 行为差异: A acts as a full HTTP proxy, copying request headers, method, and body, and handling response status codes; B is a simple GET fetch with no header manipulation or error code handling.；A writes output to an HttpServletResponse; B returns a string.；A handles both input and output streams; B only reads input.；A uses HttpURLConnection with output enabled; B uses URL.openStream().
- 修正建议: Improve representation of control flow and data dependencies to capture the full scope of operations.；Incorporate more detailed API usage context, such as distinguishing between simple fetching and proxy behavior.；Use semantic analyses that differentiate between reading input and output writing.

### case_id=5190 FN lexical_or_api_overlap

- 方法: `login` vs `read`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Logs in to LOLA service by sending POST request with email and password, retrieves session ID from response, and returns it.
- B 摘要: Reads data from a file or URL stream by name, sets status based on success/failure, and returns status code.
- 静态失败原因: Static BERT/GraphCodeBERT likely relied on token overlap and API similarity; low Jaccard (0.149) and different API calls led to non-clone prediction, missing the abstract I/O pattern that BCB might have considered.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may have considered both as performing I/O operations with URL handling and exception management, viewing them as functionally similar under a broad Type-4 definition.
- 共享行为: Open a URL connection；Read from input stream；Handle exceptions with try-catch；Return a value from network I/O
- 行为差异: A writes form data to connection then reads; B only reads；A returns String session ID; B returns int status；A uses URLEncoder and OutputStreamWriter; B uses BufferedInputStream and FileInputStream；A's URL is fixed; B's URL is parameterized name
- 修正建议: Incorporate higher-level I/O pattern features (e.g., URL opening, stream reading)；Train on Type-4 examples with partial functionality similarity；Use dataflow analysis to capture control-flow structure

### case_id=5191 FP partial_functionality

- 方法: `doVersionCheck` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Checks for software version information from a remote URL and displays an error if reading fails.
- B 摘要: Performs a Google image search for a music track's artist and album, then parses image URLs from the response.
- 静态失败原因: Static BERT/GraphCodeBERT likely over-relied on surface-level structural similarities (e.g., both use URL, BufferedReader, while loop, try-catch) while ignoring the distinct method names and domain-specific logic, leading to a false positive.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB typically requires significant functional similarity for clones; these two methods share only common HTTP read patterns but perform entirely different tasks, so BCB labels them as non-clones.
- 共享行为: Both open an HTTP connection to a URL and read lines from the input stream.；Both use BufferedReader and InputStreamReader to read the response.；Both handle exceptions with a try-catch block.
- 行为差异: Different overall purpose: version checking vs. image search.；Different URL construction and response parsing logic.；Different error handling: IOException vs. generic Exception.；Function A shows/hides a wait cursor and calls another method; Function B has a condition on artist change and adds results to a list.
- 修正建议: Incorporate method name semantics and alert on mismatched high-level tasks.；Use dataflow analysis to track how inputs are transformed to outputs, capturing differences in parsing and result handling.；Consider the broader context (class, imports) to disambiguate HTTP operations.

### case_id=5192 FN benchmark_preference_bias

- 方法: `save` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: A utility that saves a list of byte arrays as files and copies them to a package directory while prepending a package declaration.
- B 摘要: A complex method that builds edited HTML pages by transforming XML with XSLT, concatenating control files, and writing output to a specified path.
- 静态失败原因: The static BERT model correctly identified the low lexical overlap (token Jaccard 0.107) and structural differences, leading to a non-clone prediction. The model did not fail; it disagreed with a likely erroneous BCB label.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled these as clones due to a broad interpretation of 'file writing functionality', possibly considering both as examples of saving data to files. However, the core logic and purpose are vastly different, suggesting a potential annotation error.
- 共享行为: Both involve writing files to disk based on input data.；Both use file I/O streams and handle file paths.；Both contain loops over a collection (A: file lists; B: pages).
- 行为差异: A is a simple file copy with package prepend; B involves XML parsing, XSLT transformation, and string manipulation.；A writes to a single base directory; B writes to an output path with filenames derived from page titles.；A uses byte arrays for content; B uses character buffers and string builders.；A has no error handling beyond exceptions; B includes detailed debugging and multiple exception types.
- 修正建议: Re-evaluate the BCB annotation for this pair to confirm if it truly meets clone criteria.；If the label is incorrect, update the dataset to remove this false positive.

### case_id=5193 FP lexical_or_api_overlap

- 方法: `handleHandshake` vs `doVersionCheck`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Handles Minecraft client handshake by validating server key and joining session.
- B 摘要: Checks for a newer version of jEdit by fetching a version file from a URL.
- 静态失败原因: Static BERT models may overemphasize lexical overlap of common API calls (URL, BufferedReader, readLine) while missing the different semantic contexts and control flow structures.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would not consider these clones because they belong to different application domains, have different control flow and domain-specific constants, and the shared use of URL/BufferedReader is a generic pattern insufficient for clone classification.
- 共享行为: Both open a URL and read from it line by line；Both parse the response to decide next action
- 行为差异: Different URL construction and target (session.minecraft.net vs jEdit property-based URL)；Different parsing logic (hash check vs version/build extraction)；Different resulting actions (send login packet vs notify version or error)
- 修正建议: Incorporate more structural features like control flow graphs；Use data flow analysis to distinguish different data transformations；Add domain-specific patterns or context awareness

### case_id=5194 FN partial_functionality

- 方法: `main` vs `setPayload`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a URL and extracts its zip entries to files.
- B 摘要: Appends a fixed file (HeadlessData) to multiple destination files using FileChannel, then recursively processes payloads.
- 静态失败原因: Static BERT/GraphCodeBERT relies heavily on token overlap and syntactic structure; low Jaccard (0.114) and different control flow/API usage caused the model to miss the vague file I/O similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may view both as 'file writing operations' at a high level, accepting broad Type-4 semantic similarity despite very different contexts and low lexical overlap.
- 共享行为: Both use FileOutputStream to write to files.；Both handle IOException.；Both involve reading from an input source.
- 行为差异: A downloads from network; B uses local files.；A extracts zip entries; B copies entire file content.；A is a static main method; B is an instance method with class fields.；B includes a recursive call to another overloaded setPayload method.
- 修正建议: Use program embeddings that capture high-level intent (e.g., API call sequences, resource usage patterns).；Include data flow graphs to identify common stream processing patterns.；Apply clustering on I/O operations to identify Type-4 clones.

### case_id=5195 FP partial_functionality

- 方法: `fetchUrl` vs `getTicketsForQueue`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches the content of a URL as a string, reading all lines and returning concatenated result, or empty string on error.
- B 摘要: Queries a bug tracker for open tickets in a queue, parses ticket IDs from the response, fetches each ticket, and returns a list of tickets.
- 静态失败原因: Static BERT/GraphCodeBERT models may over-rely on overlapping API tokens (e.g., BufferedReader, readLine, HTTP classes) and exception handling structure, leading to false positive prediction despite different overall semantics.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB typically labels as non-clone when functions differ in core functionality despite sharing low-level I/O patterns. The token Jaccard is low, and the purpose is distinct.
- 共享行为: Both perform an HTTP GET request to retrieve data from a server.；Both read the response line by line using BufferedReader.；Both handle exceptions related to I/O and HTTP.
- 行为差异: fetchUrl returns the entire response body as a string; getTicketsForQueue parses specific lines to extract ticket IDs.；fetchUrl makes a single HTTP request; getTicketsForQueue makes multiple requests (one query, then per-ticket fetches).；fetchUrl returns empty string on error; getTicketsForQueue returns null or throws custom exceptions.；fetchUrl is a generic utility; getTicketsForQueue is domain-specific with query parameter construction and session handling.
- 修正建议: Incorporate dataflow analysis to capture the return type and subsequent processing of the HTTP response.；Train with more examples that distinguish between generic fetchers and domain-specific parsers.；Use control-flow and call-graph features to differentiate single-request vs multi-request patterns.

### case_id=5196 FP boilerplate_overlap

- 方法: `postRequest` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Sends an HTTP POST request with form-encoded parameters and returns the response body as a string.
- B 摘要: Performs a Google image search via HTTP GET, parses HTML to extract image URLs, and updates a UI component with the first result.
- 静态失败原因: Static BERT/GraphCodeBERT likely focused on the shared lexical tokens such as URL, openConnection, BufferedReader, and the while-read loop, overlooking the broader semantic differences in method signature, HTTP method, and post-processing.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled this as non-clone because the functions have entirely different purposes, input/output signatures, and post-processing logic, despite sharing low-level HTTP boilerplate.
- 共享行为: Both open an HTTP connection and read the response line by line into a string.；Both use similar boilerplate for URL and connection handling.；Both catch exceptions and handle errors (though differently).
- 行为差异: postRequest uses POST method with encoded parameters; googleImageSearch uses GET with query in URL.；postRequest returns a string; googleImageSearch returns void and updates UI and a list.；postRequest is generic; googleImageSearch is specific to Google Images with HTML parsing.；Error handling: postRequest returns null; googleImageSearch shows error dialog and continues.
- 修正建议: Incorporate method return type and parameter types as features.；Include call graph context to differentiate side-effect vs pure functions.；Use control-flow or data-flow to capture post-processing differences.；Train on more diverse examples of HTTP client functions with different purposes.

### case_id=5197 FP lexical_or_api_overlap

- 方法: `readZoneIDs` vs `main`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: reads integers from a resource file URL and returns them as a HashSet
- B 摘要: reads lines from a web URL and prints them to standard output
- 静态失败原因: high lexical overlap (URL, openStream, readLine, InputStreamReader) misled the model into thinking they are similar
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically requires semantic equivalence or near-equivalence; these functions have different inputs, outputs, and purposes, so they are non-clones
- 共享行为: use URL to open a stream；read lines from a stream；handle exceptions via printStackTrace or throws
- 行为差异: function A returns a HashSet<Integer>; function B prints lines and returns void；function A reads from a class resource; function B from a web URL；function A uses LineNumberReader; function B uses BufferedReader
- 修正建议: train on more diverse pairs to reduce API similarity bias；incorporate dataflow or control flow analysis to differentiate output usage

### case_id=5198 FN benchmark_preference_bias

- 方法: `decodeFileToFile` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Decodes a Base64-encoded file and writes the decoded content to an output file.
- B 摘要: Launches a NexOpen project configuration by processing XML files, setting properties, creating resources, and executing an install action.
- 静态失败原因: Static BERT/GraphCodeBERT likely predicted non-clone because the token overlap is very low (0.071) and the semantic contexts differ widely. The model correctly identified them as non-clones based on lexical and syntactic features.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as a clone due to both methods involving file I/O and stream handling, which might be considered similar under a broad Type-4 category focusing on utility functions. However, the methods have distinct purposes and contexts.
- 共享行为: Both involve file I/O operations (reading and writing streams).
- 行为差异: Function A decodes Base64; Function B does project launch setup.；Function A is simple and generic; Function B is complex and Eclipse-specific.；Function A returns a boolean success flag; Function B does not return a value (void).
- 修正建议: Ensure benchmark annotations are consistent with strict semantic equivalence criteria.；Add more contextual information or domain-specific knowledge to models to avoid over-generalizing BCB labels.

### case_id=5199 FN benchmark_preference_bias

- 方法: `compress` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Concatenates multiple input files into a single output file and optionally compresses the output using YUI Compressor.
- B 摘要: Configures and launches a NexOpen Eclipse project, including handling POM files, setting Hibernate dialect, generating reverse engineering files, and triggering an install action.
- 静态失败原因: Static BERT did not fail; it correctly predicted non-clone due to low lexical overlap and distinct semantics.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: The BCB annotation likely considered both as involving file processing or build-related steps, but this is too broad; the functionalities are unrelated.
- 共享行为: Both involve file I/O operations.
- 行为差异: Function A reads and concatenates files directly; Function B operates on Eclipse resources and project configuration.；Function A optionally uses an external compressor; Function B integrates with Eclipse and Maven/SDK.；Their goals are entirely different: file concatenation/compression vs. project setup and launch.
- 修正建议: Review BCB annotation to confirm if it's an error.；Refine criteria for what constitutes a clone in evaluation datasets.

### case_id=5200 FP boilerplate_overlap

- 方法: `sendRequest` vs `checkForUpgrade`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Sends an HTTP request with XML data to a configurable server and parses the response.
- B 摘要: Checks for software upgrades by querying a remote server and updating a local database.
- 静态失败原因: Static BERT likely overemphasized the overlapping API usage (URLConnection, InputStream) and similar control flow structure, overlooking the distinct functional intents.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would label as non-clone because the functions have entirely different purposes and logic, despite generic HTTP communication patterns.
- 共享行为: Both open a URL connection and read input stream；Both parse response data (one as JDOM document, other as string split)；Both use try-catch for error handling
- 行为差异: A sends XML data; B receives and processes upgrade records；A configures server URL via UI dialog; B queries database for version；A compresses output with GZIP; B does not compress；A returns empty string; B updates UI and database
- 修正建议: Improve training with more diverse negative examples that share API usage but differ in goal；Incorporate dataflow or semantic analysis to distinguish purpose beyond surface patterns

### case_id=5201 FP lexical_or_api_overlap

- 方法: `getFrameworkFactory` vs `getXML`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a service configuration file from the classpath to instantiate a FrameworkFactory.
- B 摘要: Fetches XML content from a given servlet URL and returns it as a string.
- 静态失败原因: Static BERT/GraphCodeBERT models may be misled by high token overlap in URL-reading boilerplate code and similar control flow structure.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB considers functional equivalence; these functions have different purposes and outputs, so they are not clones.
- 共享行为: Both open a URL and read lines using BufferedReader and InputStreamReader
- 行为差异: A returns a FrameworkFactory instance, B returns a String；A reads from classpath resource, B fetches from remote servlet；A processes lines to find a class name, B appends all lines to a buffer；Error handling differs: A throws exception, B returns null on failure
- 修正建议: Incorporate dataflow analysis to distinguish processing logic；Use contrastive learning with negative examples having similar boilerplate but different semantics

### case_id=5202 FN partial_functionality

- 方法: `modifyApplicationMessage` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Modifies a properties file for a given locale by conditionally copying a base file, then reading, updating, and writing a key-value pair.
- B 摘要: Copies a file from source to destination using FileChannel transfer.
- 静态失败原因: Static BERT/GraphCodeBERT likely relied on token-level similarity and method names, which are very different (Jaccard=0.129), missing the high-level pattern of file I/O shared across the functions.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have annotated these as clones due to both being file manipulation operations, considering Type-4 broad semantic similarity despite differing core purposes.
- 共享行为: Both perform file I/O operations (read/write).
- 行为差异: A does multiple file operations (copy, read, modify, write) with specific properties file logic; B is a simple binary file copy.；A uses character streams and line-by-line processing; B uses NIO channels and transfer.；A includes conditional copy and key-value modification; B is unconditional.
- 修正建议: Enhance representation with data flow and API usage graphs to capture sub-tasks like file copying within a larger function.；Use models that better abstract intent (e.g., sequence of file operations) rather than surface tokens.

### case_id=5203 FP lexical_or_api_overlap

- 方法: `importSequences` vs `fetchUrl`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Imports biological sequences from a URL by parsing FASTA format, extracting sequence names and data.
- B 摘要: Fetches the entire content of a URL as a string by reading all lines.
- 静态失败原因: High lexical overlap (URL, openStream, IOException, etc.) and similar control flow (try-catch, while loop) caused the model to overestimate similarity, ignoring the distinct parsing logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically does not consider functions clones if their core functionality differs, even with similar I/O boilerplate; Type-4 clones require semantic equivalence, which is lacking here.
- 共享行为: Both open a URL stream and read text；Both handle IOException and MalformedURLException
- 行为差异: Function A parses FASTA format (looking for '>', tokenizing names, reading sequences until '>'), Function B simply concatenates all lines；Function A stores results in lists, Function B returns a string；Function A uses a combo box index to select URL, Function B takes URL as parameter
- 修正建议: Incorporate dataflow analysis to differentiate actual data processing；Use contrastive learning on tasks with similar boilerplate but different semantics；Add attention to the core logic beyond I/O patterns

### case_id=5204 FN benchmark_preference_bias

- 方法: `modifyApplicationMessage` vs `parseContent`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.85`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Modifies a property value in a localized properties file, creating the file if missing by copying from English defaults.
- B 摘要: Parses HTML content from a stream to extract metadata, links, language, and body text, handling charset detection.
- 静态失败原因: Static BERT likely correctly identified no semantic equivalence, but BCB's lenient annotation was not captured because the functions share only generic boilerplate (try-catch, file reading) and have low token overlap.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled as clone based on very broad similarity: both functions 'process content with file I/O and string manipulation'. However, the tasks are fundamentally different.
- 共享行为: Both perform file/stream I/O operations；Both involve reading and writing data
- 行为差异: A operates on property files for localization; B parses HTML for web crawling；A modifies a single key-value pair; B extracts multiple fields and links；A writes back to the same file; B adds fields to an index document
- 修正建议: Improve model to recognize that generic I/O patterns do not imply clones；Use finer-grained semantic clustering or domain-specific features

### case_id=5205 FN lexical_or_api_overlap

- 方法: `getResourceAsStream` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Downloads and caches a resource from a URL, returning an InputStream.
- B 摘要: Generates edited HTML pages for a site by applying XSLT transformations and including control files.
- 静态失败原因: Static models may overemphasize lexical overlaps (e.g., InputStream, FileInputStream, try-catch) and ignore structural and semantic differences.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely mislabeled this pair; they share no meaningful semantic or syntactic similarity beyond generic I/O patterns.
- 共享行为: Both perform file I/O operations；Both handle exceptions with try-catch；Both use debug output statements
- 行为差异: Different core purposes: caching vs. site generation；Different inputs and outputs；Different external APIs: HTTP vs. XSLT/DOM；Different control flow and algorithms
- 修正建议: Enhance model with data flow analysis；Use a larger context window to capture function logic；Incorporate control flow graphs for better distinction

### case_id=5206 FP lexical_or_api_overlap

- 方法: `run` vs `doVersionCheck`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches a tile from a URL, parses GeoJSON into vector geometries, and adds them to a data loader.
- B 摘要: Checks for a new version by reading a version file from a URL and comparing versions.
- 静态失败原因: The model likely focused on the boilerplate code pattern (URL open, BufferedReader) that appears in both, and neglected the rest of the function body which is more specific; the high token Jaccard (0.203) and similar API sequence misled the model.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels non-clones because the overall functionality is completely different, despite some shared API usage; the intent and output are distinct.
- 共享行为: Open URL and read lines using BufferedReader；Handle IOException
- 行为差异: Function A processes tile geometries and adds to layer; Function B compares version strings and shows GUI message；Function A uses synchronization for deduplication; Function B shows wait cursor；Function A extracts geometry data; Function B extracts version/build strings
- 修正建议: Include structural embeddings that capture control flow and data dependencies beyond API call sequences；Weight the unique parts of the function higher or use sequence alignment to focus on differences；Use contrastive learning with hard negative mining to discourage matching based on boilerplate alone

### case_id=5207 FN partial_functionality

- 方法: `writeFileType` vs `postRequest`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads URIs from a file, fetches each web page, checks for ontology patterns, and writes classification to an output file.
- B 摘要: Sends an HTTP POST request with form parameters from a HashMap and returns the response body as a string.
- 静态失败原因: Static BERT models rely on token and structural similarity; low Jaccard (0.23) and different method names, parameters, and logic led to a non-clone prediction, missing the high-level semantic overlap in HTTP operations.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label these as clones because both involve making HTTP connections and reading responses, fitting a broad Type-4 category of 'network I/O' operations, despite different specific purposes.
- 共享行为: Both create URL objects and open URLConnections；Both read from an InputStream using BufferedReader；Both handle exceptions with printStackTrace
- 行为差异: A reads input URIs from a file, B takes URL and data as arguments；A writes classification results to a file, B returns the response string；A checks for specific ontology keywords in the response, B does not；A uses GET (default), B uses POST with doOutput
- 修正建议: Train the model with more Type-4 clone examples that have low syntactic similarity but share higher-level functionality；Incorporate data flow or control flow features to capture common I/O patterns；Use program dependency graphs or context-aware embeddings to recognize similar tasks

### case_id=5208 FP boilerplate_overlap

- 方法: `downloadURLtoString` vs `downloadFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Downloads a URL's content into a String using BufferedReader.
- B 摘要: Downloads a file from a URL to a local file with progress reporting using BufferedInputStream and BufferedOutputStream.
- 静态失败原因: Static BERT/GraphCodeBERT may have focused on overlapping API tokens (URL, openStream, InputStream, read loop) and boilerplate I/O patterns, overlooking the semantic differences in output handling and side effects.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clone because the functions have different return types, different output destinations (String vs file), and different side effects (progress reporting vs simple read). Although both involve downloading from a URL, the core purpose and behavior are distinct.
- 共享行为: Open a URL and read data from its input stream；Use buffered I/O；Close streams after reading
- 行为差异: Function A returns the content as a String; Function B writes to a file and returns boolean；Function B tracks download progress and updates a UI component (MessageFrame)；Function B uses byte array buffer and handles file creation/deletion；Exception types differ: IOException vs Exception
- 修正建议: Improve model's ability to distinguish side effects (writing to file vs returning string)；Add attention to method return types and output variables；Incorporate dataflow analysis to track how downloaded data is used (consumed vs stored)

### case_id=5209 FN partial_functionality

- 方法: `copyResource` vs `extractFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource from a URL or local file to a destination file using byte-by-byte reading.
- B 摘要: Extracts a file by reading from an input file using a buffered byte array and writing to an output file.
- 静态失败原因: Low token Jaccard and syntactic differences (byte-by-byte vs buffered, custom FileReader usage) cause static BERT to miss the semantic equivalence of the copy operation.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB labels this as clone because both functions perform the same high-level task of copying from a source to an output file, considered a Type-3 clone with structural differences.
- 共享行为: Both functions copy bytes from a source to a file output stream.；Both use read/write loops and close streams.
- 行为差异: code_a reads byte-by-byte without buffer; code_b uses a 512-byte buffer.；code_a supports URL and file sources; code_b only reads from a file via FileReader.；Exception handling and method signatures differ.
- 修正建议: Improve sensitivity to I/O copy patterns and dataflow.；Train on diverse implementations of file copy.；Incorporate abstract syntax tree features highlighting copy loops.

### case_id=5210 FN benchmark_preference_bias

- 方法: `createSettingsIfNecessary` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Creates a settings file by copying from a resource if it doesn't exist.
- B 摘要: Launches a NexOpen project by validating project structure, handling POM files, configuring properties, and scheduling an install action.
- 静态失败原因: The static model (e.g., GraphCodeBERT) likely focused on the large structural and semantic differences, low token overlap, and distinct method signatures. It correctly judged them as non-clones under strict equivalence, but failed to recognize the partial functional overlap that BCB considered clone-worthy.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled these as clones due to the shared pattern of checking file existence and copying from a resource stream, a common utility operation. Their broader Type-4 criteria often accept partial functional similarity even when overall semantics differ.
- 共享行为: Both check file existence before proceeding.；Both copy from a resource input stream to an output stream using IOUtils.copy in at least one branch.；Both use logging for informational or error messages.；Both handle exceptions in a try-finally or try-catch block.
- 行为差异: Function A is a simple single-purpose method; Function B is a complex multi-step launch procedure with many conditional branches.；Function A deals only with one settings file; Function B manages multiple POM files, properties, and reverse engineering files.；Function A has no dependencies on Eclipse/JDT; Function B heavily uses Eclipse workspace, launch configuration, and project APIs.；Function A throws IOException; Function B throws CoreException and takes additional parameters (launch, mode, monitor).
- 修正建议: Train models with a mix of strict and relaxed clone labels, possibly using hierarchical or partial clone detection.；Incorporate fine-grained subroutine similarity detection to capture partial functionality overlaps.；Use data augmentation to expose models to Type-4 clones with low token overlap but similar subroutines.

### case_id=5211 FN benchmark_preference_bias

- 方法: `getFile` vs `sendErrorMessage`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies its endpoint address, and returns the local file path.
- B 摘要: Sends an error message by zipping a log file and emailing it to recipients.
- 静态失败原因: Static BERT models like CodeBERT rely on token-level and graph-level patterns. While they correctly identified low lexical overlap, they might have been too sensitive to common patterns (e.g., try-catch, FileOutputStream) and missed the overall functional difference, or conversely, if they predicted 0, they actually succeeded. However, the BCB label indicates a clone, so the model's failure is that it did not recognize the broad similarity that BCB saw, possibly due to insufficient understanding of high-level functionality from limited context.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might have considered these clones due to structural similarity in exception handling and file I/O, interpreting both as 'perform I/O and handle errors', but this is a very broad interpretation that likely overextends the Type-4 definition.
- 共享行为: Both use FileOutputStream for file output；Both have try-catch exception handling blocks；Both perform logging or error reporting
- 行为差异: getFile downloads and transforms a WSDL file, sendErrorMessage sends an email with attachment；getFile returns a String, sendErrorMessage is void；getFile throws AxisFault, sendErrorMessage throws custom messaging exceptions；getFile interacts with network via URL, sendErrorMessage interacts with mail system
- 修正建议: Improve model understanding of functional purpose beyond structural patterns；Incorporate semantic role labeling or data flow analysis to distinguish different types of I/O operations；Re-evaluate BCB annotations for consistency in Type-4 clone criteria

### case_id=5212 FN partial_functionality

- 方法: `doTransfer` vs `getPagina`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Forwards an HTTP request to a specified URL, copying headers and method, and streaming the response back.
- B 摘要: Fetches the content of a URL and returns it as a string.
- 静态失败原因: Static BERT models rely on token embeddings and miss structural/flow similarities due to low token overlap, different method names, and distinct signatures (HttpServletRequest vs String).
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: Both functions perform HTTP GET to retrieve remote content, with similar stream reading patterns, which BCB may consider as Type-3 clone (partial functionality similarity).
- 共享行为: Open an HTTP connection to a URL；Read input stream from the connection；Handle IOException and MalformedURLException
- 行为差异: A forwards request headers and method; B does not；A writes response to output stream; B concatenates lines into string；A handles HTTP status codes; B does not；A has more complex I/O with request body forwarding
- 修正建议: Incorporate dataflow/graph-based features to capture common sub-patterns like URL fetching；Add training examples of partial functionality clones with low token overlap；Use method-level functional summarization to highlight shared behavior

### case_id=5213 FN benchmark_preference_bias

- 方法: `main` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Tests a custom StraightStreamReader by writing bytes to a file and reading them back with various read methods.
- B 摘要: Retrieves a resource from a URL, caches it locally, and returns a FileInputStream.
- 静态失败原因: Static BERT did not fail; it correctly predicted non-clone due to low token similarity (0.17) and distinct code structures. The BCB label seems incorrect.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might label them as clones due to both involving stream manipulation and file I/O, possibly considering them functionally similar under a broad Type-4 category, but they are semantically unrelated.
- 共享行为: Both involve file I/O and stream operations；Both handle exceptions (IOException or Exception)；Both use FileInputStream and FileOutputStream
- 行为差异: One is a test for a specific stream reader, the other is a general resource fetching with caching；Different control flow: sequential test steps vs. conditional caching logic；Different purpose: verification vs. retrieval
- 修正建议: Re-evaluate BCB label for this pair；Consider semantic similarity beyond token overlap；Focus on functional intent rather than superficial I/O operations

### case_id=5214 FN benchmark_preference_bias

- 方法: `copyFile` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.4`
- 推荐路线: `preference_memory_with_manual_audit`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Copies a local file to another local file using FileChannel, creating parent directories and destination file if needed.
- B 摘要: Retrieves a resource (potentially remote) as an InputStream, caching it locally after downloading via HTTP and returning a FileInputStream.
- 静态失败原因: The static BERT model likely focused on low token overlap (Jaccard=0.14) and different method names and logic (local copy vs. remote caching), missing the abstract file I/O similarity that BCB considers.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as a clone due to both involving file I/O operations (read from source, write to destination) and similar boilerplate for directory creation and stream management, accepting broad Type-4 similarity.
- 共享行为: Both involve reading from an input source and writing to a file；Both create directories if parent does not exist；Both handle stream closure in finally blocks
- 行为差异: A operates on local files only; B handles remote URLs with HTTP；A uses FileChannel for efficient copy; B uses BufferedStreams；B implements caching and HTTP response handling; A does not；B returns an InputStream; A has void return type
- 修正建议: Improve model to capture abstract functionality like file I/O patterns；Use data augmentation with functional labels；Incorporate code structure or data flow analysis to detect similar I/O operations

### case_id=5215 FN partial_functionality

- 方法: `copyResource` vs `test`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource from a URL or file to a destination file by byte-by-byte streaming.
- B 摘要: Tests the StorageStringWriter class by writing and reading data, including exception handling and stream copying.
- 静态失败原因: Static BERT models often rely on token overlap and structural similarity. Here, token Jaccard is low (0.1389), and the functions have different control flow (while loop vs. try-catch with method calls). The model likely focused on the different method names, different classes, and the test-specific assertions, leading to a non-clone prediction.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider them clones due to the presence of an InputStream-to-OutputStream copy operation, which is a common functional pattern. The similarity might be interpreted as Type-4 (semantic) because both involve data transfer from input to output, even though the context differs.
- 共享行为: Both involve reading from an InputStream and writing to an OutputStream (or Writer) in a copy operation.
- 行为差异: Function A is a simple utility copying bytes; Function B is a multi-step test with assertions and exception handling.；Function A uses a while loop; Function B uses IOUtils.copy.；Function A copies to a file; Function B copies to a StringWriter.；Function A lacks any testing logic; Function B is a JUnit test.
- 修正建议: Improve model's ability to detect shared subroutines or dataflow patterns even when overall structure differs.；Incorporate data flow analysis to recognize that both functions perform an input-to-output copy.

### case_id=5216 FP lexical_or_api_overlap

- 方法: `get` vs `readURL`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Performs an HTTP GET request with custom headers, reads lines from the response, filters out lines starting with '#', decodes each line into a GameRecord, and returns an array of GameRecords.
- B 摘要: Opens a URL, reads all lines from the input stream, and prints each line to the console.
- 静态失败原因: Static BERT models (like GraphCodeBERT) likely over-relied on overlapping lexical tokens and API sequences (URL, BufferedReader, readLine, while loop, e.printStackTrace), missing the semantic differences in return types and conditional logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically considers non-clones when functions have different output types and purposes, even if they share common I/O patterns. The core functionality differs significantly (parsing game records vs. printing lines), so BCB labels it as non-clone.
- 共享行为: Both open a URL and read lines from the input stream using a BufferedReader.；Both use a while loop to read lines until null.；Both catch exceptions and print stack traces.
- 行为差异: Function A returns a GameRecord array; function B prints lines and has no return value (void).；Function A sets custom request headers (latitude, longitude, count) and uses HttpURLConnection; function B uses URL.openStream() with no headers.；Function A filters lines starting with '#' and decodes them; function B prints all lines as-is.；Function A does not properly close streams in a finally block; function B closes streams in finally.
- 修正建议: Incorporate structural information like data flow and control dependencies beyond token sequences.；Add attention to method signatures and return types.；Use contrastive learning to separate functions with similar IO templates but different purposes.

### case_id=5217 FN partial_functionality

- 方法: `modifyApplicationMessage` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Modifies a properties file for a given locale, optionally copying from the English file if the locale file does not exist.
- B 摘要: Copies a file from source to destination using FileChannel.
- 静态失败原因: Static BERT models rely heavily on token overlap (Jaccard=0.075) and fail to capture the structural similarity of the file-copying suboperation due to different API usage and conditional context.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this as clone due to Type-4 partial functional similarity: both functions perform file copying, and Code A includes a file copy step (copying English file to locale file) as part of its logic, which aligns with the core behavior of Code B.
- 共享行为: Both involve file copy operations from a source to a destination.
- 行为差异: Code A is more complex with conditional logic and property modification; Code B is a straightforward copy.；Code A uses stream-based copy with FileReader/FileWriter; Code B uses NIO FileChannel.；Code A processes properties file content; Code B does not interpret the file content.
- 修正建议: Use dataflow analysis to identify common suboperations like file copy across different APIs.；Incorporate task-specific fine-tuning on partial clone detection.；Enhance embeddings with structural code representations (e.g., AST subtrees) to capture partial functionality.

### case_id=5218 FP partial_functionality

- 方法: `getVersion` vs `handledRun`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches a version string from a URL and returns it.
- B 摘要: Downloads updated game data from a URL if a newer version is available, then loads the game database.
- 静态失败原因: Static BERT/GraphCodeBERT may have over-relied on the common API tokens (URL, BufferedReader, InputStreamReader) and the initial line-by-line reading pattern, ignoring the later parts that change the semantics completely. The model might also lack understanding of the conditional logic and file I/O differences.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely considered these non-clones because the overall purpose and functionality differ significantly (fetch version vs. update game data). The structural similarity in the initial lines is outweighed by the divergent logic and different outcomes.
- 共享行为: Both open a URL and read lines using BufferedReader/InputStreamReader.
- 行为差异: Function A returns a single line (version string); Function B reads two lines, parses a version number, and conditionally downloads data.；Function A does not modify any files; Function B writes to a file and updates game database.；Function A has simple error handling (returns null); Function B has multiple error handling blocks and user interaction.；Function A is a simple getter; Function B is a multi-step update procedure.
- 修正建议: Enhance the model to consider the entire function body, especially the later parts that define the core behavior.；Incorporate data flow analysis to track how variables like 'version' vs 'lastversion' are used differently.；Use attention mechanisms that better capture long-range dependencies and structural differences.

### case_id=5219 FN partial_functionality

- 方法: `doTransfer` vs `addDataFromURL`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Forwards an HTTP request to a URL specified in request parameter, including headers and body, and returns the response.
- B 摘要: Reads text content from a URL and appends it line by line to a StringBuilder.
- 静态失败原因: The model relied on lexical and syntactic similarity (token Jaccard 0.16) and lacked understanding of high-level functional intention, resulting in a non-clone prediction.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have considered both as fetching data from a URL (Type-4 functional similarity), overlooking the significant differences in complexity and context.
- 共享行为: Both open a connection to a URL and read data from it.；Both handle IO exceptions.
- 行为差异: doTransfer copies request headers, sends request body, handles HTTP status codes, and writes to the HTTP response output stream.；addDataFromURL only reads text lines using URL.openStream() and appends them to a local buffer.；doTransfer uses HttpURLConnection with full control; addDataFromURL uses simpler URL.openStream().
- 修正建议: Enhance model with capabilities to recognize abstract patterns like 'URL data retrieval' across different implementations.；Incorporate broader context (e.g., servlet vs. standalone) and API usage patterns.

### case_id=5220 FN partial_functionality

- 方法: `doGet` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Handles HTTP GET request by retrieving a page, checking permissions, rendering HTML, and optionally caching the page output to a file.
- B 摘要: Copies the content of a source file to a destination file using a byte buffer.
- 静态失败原因: Static methods like BERT or GraphCodeBERT rely heavily on token/lexical overlap and structural similarity. The low Jaccard similarity (0.04898) and very different API calls and control flows led the model to predict non-clone. Additionally, the model may lack the ability to abstract the common low-level copying behavior from the high-level contextual differences.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider this a clone because both functions perform a similar low-level operation: copying data from an input stream to an output stream. The functional similarity in the data transfer aspect, albeit in different contexts, could be classified as a Type-4 (semantic) clone under a broad interpretation of partial functionality similarity.
- 共享行为: Both involve reading from an input source and writing to an output destination.；Both use stream-based I/O to transfer data.；Both handle IOException through exceptions.
- 行为差异: Function A is an HTTP servlet handler with complex logic; Function B is a simple file copy utility.；Function A writes to a file only conditionally; Function B always copies.；Function A uses character streams (FileWriter); Function B uses byte streams.；Function A relies on many external dependencies; Function B is self-contained.
- 修正建议: Enhance model to recognize sub-functionality or compositional structure.；Use data-flow analysis to detect common patterns like read-write loops.；Incorporate program slicing to isolate relevant sub-behaviors.；Use contrastive learning with positive pairs that have low lexical overlap but similar semantics.

### case_id=5221 FN partial_functionality

- 方法: `copyResource` vs `copy`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.95`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a single resource (URL or file) to a destination file using byte-by-byte I/O.
- B 摘要: Recursively copies a file or directory to a destination, with error logging and directory handling.
- 静态失败原因: Low token Jaccard (0.207) due to different variable names, lack of URL handling in B, and the recursive structure in B likely misled the model. The model may have focused on syntactic differences and missed the semantic overlap in the byte-copy loop.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels pairs as clones if they share core functionality (copying data via byte-by-byte loop) and have similar structure, even if one is more general. The recursive directory handling is an extension, but the core file copy logic is present in both.
- 共享行为: Both read bytes from a source and write them to a destination.；Both use a while loop reading one byte at a time until -1.；Both close input and output streams after copying.
- 行为差异: Function A only copies a single resource, while B recursively copies directories.；Function A handles URL sources; B only handles file sources.；Function A throws an exception on missing source; B logs errors and continues.；Function B uses a char buffer (though not effectively) and includes error handling for file operations.
- 修正建议: Train on more examples where a more complex function subsumes a simpler one (e.g., recursive copy vs. single file copy).；Use cross-function similarity that detects identical substructures like the read-write loop.；Incorporate dataflow analysis to identify that both functions perform the same core I/O operation.

### case_id=5222 FP partial_functionality

- 方法: `get` vs `downloadModel`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches game records from a URL by sending a GET request with location and count headers, parses each line not starting with '#' as a GameRecord, and returns an array.
- B 摘要: Downloads an RDF model from a URL by opening a connection, setting Accept headers, reading the input stream, and parsing it as an RDF model.
- 静态失败原因: Static BERT/GraphCodeBERT may have been misled by the common pattern of opening HTTP connection, reading input stream, and handling exceptions, and by the similarity in method names (both involve 'get' or download). The low token overlap suggests the model relied on structural similarities rather than semantic differences.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB typically labels as non-clone when functions have different domain-specific parsing and different return types, despite sharing an HTTP connection pattern, because the core functionality differs.
- 共享行为: Both open an HTTP connection to a given URL；Both read input from the connection's input stream；Both handle IOExceptions
- 行为差异: Function A sets custom headers for latitude, longitude, and game count; function B sets Accept and Accept-Language headers；Function A parses lines as GameRecord objects; function B parses an RDF model；Function A returns an array or null; function B returns a Model or throws RuntimeException；Function A prints error message on non-OK response; function B throws RuntimeException on errors
- 修正建议: Focus training on distinguishing domain-specific parsing logic；Use data flow analysis to track how input is transformed；Incorporate return type and method signature matching

### case_id=5223 FP other

- 方法: `actionPerformed` vs `streamContains`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Handles UI action commands for various settings (e.g., file paths, database view, look-and-feel) and updates preferences.
- B 摘要: Reads an InputStream, converts it to a UTF-8 string, and asserts that it contains a given substring.
- 静态失败原因: The static model likely over-generalized from a small token overlap (e.g., both mention 'String' and file-related classes like 'File' or 'InputStream') or misjudged length-matched patterns, leading to a false positive despite radically different semantics.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BigCloneBench labels non-clones when functions have distinct high-level behaviors even if some low-level tokens coincide; here one is a settings action handler, the other a stream test utility.
- 共享行为: Both methods involve basic file/stream I/O operations.
- 行为差异: Function A is a large event handler (~200 lines) that updates numerous GUI components and preferences; Function B is a short utility (~10 lines) that checks stream content.；Function A deals with user commands and file choosers; Function B deals with assertion testing.；Function A has side effects on global state (preferences, GUI), Function B is pure assertion.；Their control flow and data structures are entirely different.
- 修正建议: Improve training with more diverse negative pairs that have generic token overlap but distinct purposes.；Add contrastive learning that focuses on high-level semantic similarity rather than lexical or structural heuristics.

### case_id=5224 FP lexical_or_api_overlap

- 方法: `run` vs `PhoneSetImpl`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches tile geometry from a URL, processes it, and adds to a data loader.
- B 摘要: Reads phone set data from a URL, parses lines, and builds a hashmap.
- 静态失败原因: Likely due to lexical overlap of URL and BufferedReader patterns, causing a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clones based on overall functionality, not just shared I/O patterns.
- 共享行为: Both read from a URL using openStream and a BufferedReader
- 行为差异: Different domain: tile fetching vs phone set parsing；Different output: geometry collection vs hashmap；Different control flow and error handling
- 修正建议: Incorporate dataflow analysis to distinguish core logic from boilerplate；Train on more diverse examples of URL reading

### case_id=5225 FN partial_functionality

- 方法: `testNetworkHTTP` vs `callApiPost`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Test method that performs multiple HTTP GET requests to predetermined URLs and reads response lines without processing them.
- B 摘要: Utility method that performs a single HTTP POST request with configurable parameters, sets timeouts and headers, and returns an InputStream of the response.
- 静态失败原因: The static model relied on token overlap and structural similarity, which are low (Jaccard 0.124). It failed to recognize the high-level semantic category of HTTP networking, possibly due to lack of training on such abstract clone pairs where functionality is similar but implementation details differ.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considers both as 'network communication' functions that use HttpURLConnection, thus a broad Type-4 clone based on high-level purpose and API usage, ignoring differences in request type, URL cardinality, and return value.
- 共享行为: Both use HttpURLConnection to establish HTTP connections；Both open input streams from the connection；Both handle IOException during network operations
- 行为差异: Function A makes multiple GET requests with hardcoded URLs; B makes a single POST request with a parameterized URL；Function A discards response content; B returns an InputStream for downstream processing；Function A does not set timeouts, headers, or check response codes; B does all of these；Function A has void return type; B returns InputStream
- 修正建议: Incorporate API call patterns as features to capture high-level semantics；Use contrastive learning on pairs with similar I/O operations but different control flow；Add attention to data flow paths involving network streams

### case_id=5226 FP lexical_or_api_overlap

- 方法: `getWebPage` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches the entire content of a given URL as a single string, throwing a verbose error on failure.
- B 摘要: Searches Google Images for the current track's artist and album, fetches the results page, extracts image URLs, and adds them to a list.
- 静态失败原因: The model likely over-focused on the structural and lexical similarity of the URL reading pattern (URLConnection, BufferedReader, while-loop), ignoring the different functional contexts, method names, and overall behavior. This is a common false positive due to boilerplate I/O code overlap.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically considers non-clones when overall functionality differs, even if low-level I/O patterns are similar. The methods have distinct purposes, inputs, outputs, and side effects, so BCB would label them as non-clones.
- 共享行为: Both open a URL connection and read lines of text from the response using BufferedReader and InputStreamReader.；Both use a while loop to concatenate lines into a string.
- 行为差异: getWebPage is a generic utility fetching any URL's content; googleImageSearch is a domain-specific method for Google Image search.；Different URL construction: getWebPage takes a URL object; googleImageSearch constructs a specific Google Images query URL.；Different error handling: getWebPage throws an Error with a humorous message; googleImageSearch catches Exception and shows an error dialog.；Different post-processing: getWebPage returns the raw content; googleImageSearch parses the HTML to extract image URLs and populates a list.
- 修正建议: Utilize data-flow analysis to track how the fetched content is used (e.g., returned vs. parsed for image URLs).；Incorporate method name and signature information to distinguish generic utilities from specialized search methods.；Train on more diverse examples where I/O patterns appear in different functional contexts to reduce over-reliance on API sequences.

### case_id=5227 FN partial_functionality

- 方法: `testCopy_readerToOutputStream_Encoding` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: A test method that copies a reader to an output stream with encoding conversion and verifies content equality.
- B 摘要: A main method that downloads a KMZ file from a URL, reads its zip entries, and writes each entry to a file using a byte-copy loop.
- 静态失败原因: Static model relies on surface-level token overlap, method names, and API calls; these differ significantly. It fails to recognize the underlying byte-copy semantic similarity without explicit dataflow or control-flow cues.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this as a Type-4 clone due to the semantically equivalent core operation of copying bytes from an input to an output, even though the surrounding context differs. The manual copy loop in B mirrors the library call in A.
- 共享行为: both read data from an input source and write bytes to an output destination；both involve copying bytes in a loop or via library call
- 行为差异: different overall purpose: unit test vs. file extraction program；different I/O types: Reader/OutputStream vs. ZipInputStream/FileOutputStream；encoding handling only in function A；output verification only in function A
- 修正建议: augment training data with Type-4 clones where core functionality is abstracted；use dataflow analysis or program slicing to capture I/O transformation patterns；incorporate graph-based representations that highlight stream copy operations

### case_id=5228 FN benchmark_preference_bias

- 方法: `truncate` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Archives and deletes old log files by compressing them into a zip backup, with error handling and date formatting.
- B 摘要: Configures and launches a Maven/Hibernate-based NexOpen project in Eclipse, including XML processing, reverse engineering, and resource manipulation.
- 静态失败原因: Static BERT did not fail; it correctly predicted non-clone (0). The error type is FN, meaning the model disagreed with BCB label. The model likely captured the lack of semantic overlap and low token similarity.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as clone (Type-4) due to broad structural similarity: both are long methods with nested try-catch, file handling, and stream usage. However, the functional domains are entirely unrelated, which is atypical for BCB clones. This could be a labeling error.
- 共享行为: Both involve file I/O operations (reading files, streams).；Both use exception handling with try-catch-finally blocks.；Both acquire system resources and perform cleanup.
- 行为差异: Function A performs log compression/deletion; B performs project build configuration.；A uses ZipOutputStream and CRC checksum; B uses Eclipse launch configuration, Maven POMs, Hibernate dialect.；A is concerned with backup management; B with IDE project setup and execution.；A has no dependencies on Eclipse or Maven; B heavily depends on Eclipse and Maven APIs.
- 修正建议: Re-examine BCB label for this pair; consider it a false positive in the benchmark.；If BCB annotation criteria are too lenient, refine guidelines to avoid unrelated functions.

### case_id=5229 FN benchmark_preference_bias

- 方法: `testNetworkHTTP` vs `parse`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.6`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Test method that sends device info via multiple HTTP GET requests and discards responses.
- B 摘要: Parses a dataset from a file or URL, handling headers, types, and delimiters, and returns a DataSet.
- 静态失败原因: The static BERT model correctly identified very low token similarity (Jaccard=0.072) and lack of functional equivalence, leading to a non-clone prediction. The failure is actually that the BCB label is likely incorrect, so the model's performance is not at fault.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: Given the broad scope of Type-4 clones, the BCB annotators may have considered both functions as 'functions that read from a URL via HTTP' and thus similar in high-level behavior, but the actual intent and implementation are drastically different, likely making this an erroneous annotation.
- 共享行为: Both use BufferedReader to read from a URL or file；Both handle I/O exceptions；Both involve some form of data reading
- 行为差异: Function A is a void test method that leaks device info; Function B returns a DataSet after parsing structured data.；Function A does not process the read data; Function B parses columns, types, and handles scientific notation.；Function A uses multiple fixed URLs; Function B uses configurable URL or file path.；Function B has a complex state machine for parsing; Function A just reads lines in a loop.
- 修正建议: Improve dataset annotation consistency to avoid overly broad Type-4 labels；Train models to better distinguish between superficial I/O similarity and core functionality

### case_id=5230 FN partial_functionality

- 方法: `doRawRequest` vs `readGeoParserResult`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends HTTP POST with given data and returns the response body.
- B 摘要: Sends HTTP GET to a geo-parsing service with XML content, parses XML response to extract place names and IDs, with retry logic.
- 静态失败原因: Low token overlap (0.10) and many unique tokens in B (XML parsing, retry logic, constants) overshadow the shared pattern, causing the model to miss the functional similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label them as clones because both implement a common pattern of making an HTTP request and reading the response line by line, and both are from similar network communication domains, accepting broad Type-4 similarity.
- 共享行为: Both open a URL connection；Both read the response line by line into a StringBuffer
- 行为差异: A uses POST, B uses GET；A has no retry logic, B retries up to 3 times；A returns raw string, B parses XML and extracts structured data；B constructs a complex XML request and URL query string
- 修正建议: Incorporate data-flow analysis to detect shared API usage (URL, BufferedReader)；Improve handling of long-range structural patterns；Use semantic similarity based on common I/O operations

### case_id=5231 FP lexical_or_api_overlap

- 方法: `googleImageSearch` vs `CheckUrl`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.85`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Performs a Google image search for an artist and album, parses HTML to extract image URLs, and adds them to a list.
- B 摘要: Given a URL, opens an HTTP connection, reads the first line of the response, and returns it.
- 静态失败原因: The model likely overweights the common API usage (URL, HttpURLConnection, BufferedReader) and structural patterns (try-catch, loop), neglecting semantic differences in input, output, and overall intent.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would likely label these as non-clones because the functions have fundamentally different purposes and logic, despite sharing low-level HTTP operations.
- 共享行为: Both open an HTTP connection using HttpURLConnection；Both read from an input stream using BufferedReader；Both handle exceptions with try-catch
- 行为差异: A constructs a specific Google search URL; B takes a URL argument；A reads multiple lines and parses HTML for image links; B reads only the first line；A is void and modifies a list; B returns a String；A has condition on artist change; B is static and stateless
- 修正建议: Incorporate method-level semantics from method names and comments；Use dataflow analysis to distinguish state-modifying vs. pure functions；Train with contrastive examples of similar-looking non-clones

### case_id=5232 FP lexical_or_api_overlap

- 方法: `run` vs `createHTML`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Downloads a tile from a URL, parses GeoJSON, creates geometry collection, and adds it to a data source.
- B 摘要: Generates HTML content for different page types by reading a CSS file and building HTML with optional database queries.
- 静态失败原因: Static BERT likely relied on token-level overlap (e.g., 'URL', 'BufferedReader', 'IOException', 'while' loop) and missed the high-level semantic divergence because it lacks understanding of control flow and data dependencies.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB considers these non-clones because they have entirely different semantics: one loads vector tiles, the other creates dashboard HTML. Despite superficial structural similarities in reading streams, their purpose and data handling differ completely.
- 共享行为: Both read from a URL/stream using BufferedReader and concatenate lines into a string.；Both handle IOException with try-catch and logging.；Both use String concatenation in a loop.
- 行为差异: Function A processes geospatial data (GeoJSON, geometries), while B generates HTML/CSS for user interface.；A runs in a thread with synchronization, B is a private method returning a String.；A interacts with a tile data source and layer, B queries a database and uses switch-case for page types.
- 修正建议: Incorporate data flow and control flow features to distinguish between data processing pipelines.；Use contrastive learning with hard negatives that share API usage but differ in functionality.；Add a broader context window or use a graph-based model to capture overall method purpose.

### case_id=5233 FP boilerplate_overlap

- 方法: `readData` vs `buildDeb`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Parses comma-separated token strings and a configuration file to populate sets and maps for Tibetan character processing.
- B 摘要: Writes a Debian package archive by embedding control and data files into a .deb file format.
- 静态失败原因: The model likely focused on superficial patterns like file reading/writing and blocks of set manipulation, missing the high-level semantic divergence due to limited context or overreliance on boilerplate structures.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB non-clone label is correct because the functions serve entirely different purposes (data initialization vs. file archiving) with minimal overlap in functionality.
- 共享行为: Both perform file I/O operations.；Both handle IOException by catching or throwing.
- 行为差异: Function A reads and parses multiple string sources and a file, function B writes a binary archive.；Function A builds in-memory data structures for character mapping, function B outputs a packaged file.；Function A has complex conditional logic for parsing wylie and Sanskrit, function B has straightforward file copying.
- 修正建议: Enhance training with contrastive examples that differentiate boilerplate from core functionality.；Use longer-range attention or structure-aware embeddings to capture functional intent.；Incorporate domain-specific knowledge about common library usage patterns.

### case_id=5234 FP lexical_or_api_overlap

- 方法: `actionPerformed` vs `copyFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Handles GUI action events to update various preference settings (GraphViz, ImageMagick, etc.) and persists them, optionally prompting a restart.
- B 摘要: Copies a file from source to destination using FileChannel transferFrom.
- 静态失败原因: The static model likely over-relied on superficial token overlaps (e.g., 'File', 'IOException', 'return') and common API calls, missing the vast semantic difference in control flow and purpose. The low Jaccard index (0.02) should have prevented the false positive, but the model may have been biased by training data where such lexical patterns appear in true clones.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels are based on functional equivalence; these functions serve entirely different purposes (configuration UI vs. file copy), so they are non-clones even under a broad Type-4 interpretation.
- 共享行为: Both methods involve file operations (setting file paths vs. copying a file)；Both use Java File API
- 行为差异: Function A is a complex GUI event handler with multiple conditional branches; function B is a simple, deterministic file copy.；Function A interacts with UI components and a controller; function B has no UI or state side effects.；Function A can trigger dialog boxes and restarts; function B is a pure I/O operation.
- 修正建议: Use whole-method embeddings that capture global structure and control flow.；Enhance negative sampling with pairs that share API calls but have different functionality.；Incorporate data-flow or program dependency graphs to distinguish methods with similar token usage but divergent semantics.

### case_id=5235 FP lexical_or_api_overlap

- 方法: `downloadURLtoString` vs `executePost`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.85`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Downloads content from a given URL via GET and returns it as a string.
- B 摘要: Executes an HTTP POST request with parameters, reads the response, and returns it as a string or null on error.
- 静态失败原因: The static BERT/GraphCodeBERT model likely relied on high lexical overlap (common API usage: BufferedReader, InputStreamReader, StringBuffer, while-read loop) and overlooked the differences in HTTP method, parameter handling, and error management.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically treats functions that perform different HTTP methods (GET vs POST) and have distinct error handling as non-clones, prioritizing syntactic and structural similarity in the BigCloneBench annotation process.
- 共享行为: Both perform HTTP requests and read the response line by line using BufferedReader and StringBuffer.；Both return the response body as a String.
- 行为差异: Method A uses GET, method B uses POST with parameters.；Method A has no error handling, method B handles exceptions and returns null on failure.；Method B sets up HttpURLConnection with headers and output stream, and disconnects in a finally block.；Method B appends carriage return after each line in the response.
- 修正建议: Add training examples that distinguish between GET and POST operations with similar I/O patterns.；Incorporate data-flow analysis to differentiate the flow of parameters and connection configuration.；Use method-level semantics such as HTTP method type and exception handling as discriminative features.

### case_id=5236 FP lexical_or_api_overlap

- 方法: `handleHandshake` vs `callApiPost`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Validates a Minecraft handshake packet and contacts session server to authenticate.
- B 摘要: Performs a generic HTTP POST API call with parameters and returns the response stream.
- 静态失败原因: Static BERT or GraphCodeBERT may overemphasize lexical/structural overlap (URL, IOException, InputStream, etc.) and miss semantic differences in purpose and control flow.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels non-clone due to very different high-level functionality despite both involving HTTP.
- 共享行为: Both make HTTP requests to a remote server
- 行为差异: Different domains: Minecraft authentication vs generic API call；Different HTTP methods: GET (via URL.openStream) vs POST；Different response handling: single line 'ok' check vs status code and stream；Different input parameters: handshake packet vs URL, headers, parameters, expected code
- 修正建议: Add fine-grained structural analysis to distinguish domain-specific logic from generic boilerplate；Incorporate data-flow or context beyond local tokens

### case_id=5237 FN partial_functionality

- 方法: `init` vs `seeURLConnection`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Loads controller classes by reading class names from a registry file obtained via class loader URLs.
- B 摘要: Reads content from a specific URL and logs the concatenated string.
- 静态失败原因: Static BERT models may miss the structural similarity because the token overlap is low (0.2027) and the method names differ significantly. The model may have focused on the different domain-specific terms (e.g., 'loadClass' vs 'append') and missed the common pattern of URL connection and line-by-line reading.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled this as a clone because both functions involve connecting to a URL, reading lines, and processing each line, representing a similar I/O pattern and control flow, albeit with different processing logic.
- 共享行为: Both open a URL connection and read lines using BufferedReader；Both use logging for debugging
- 行为差异: Function a loads classes from classpath; function b fetches content from a fixed URL；Function a processes each line as a class to load; function b appends lines to a StringBuffer；Function a catches exceptions and logs them; function b declares throws Exception；Function a uses getResources(REGISTRY_FILENAME) to find multiple URLs; function b uses a single hardcoded URL
- 修正建议: Improve representation of control flow and I/O patterns；Use data flow analysis to capture common subroutines like URL reading；Train on more diverse Type-3/Type-4 examples to recognize partial similarity

### case_id=5238 FP boilerplate_overlap

- 方法: `readData` vs `init`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Initializes multiple sets from comma-separated strings and reads a configuration file to populate mappings and character sets.
- B 摘要: Initializes a report file for batch processing, including backup and recovery of completed documents from a previous run.
- 静态失败原因: The model likely overemphasized superficial structural similarities (e.g., both have while loops, try-catch, file reading) or common API tokens (FileInputStream, StringTokenizer, etc.), ignoring the domain-specific semantics.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels as non-clone because the functions have completely different purposes and no partial functionality overlap.
- 共享行为: Both involve file I/O operations；Both use loops to process data；Both handle exceptions
- 行为差异: readData parses static string tokens and a config file; init manages report file lifecycle and XML writing；readData populates data structures for Tibetan/sanskrit encoding; init manages batch job restart logic；readData is static and non-returning; init is instance method with side effects
- 修正建议: Improve training data to reduce weight of common API boilerplate；Incorporate functional similarity metrics beyond token overlap

### case_id=5239 FN boilerplate_overlap

- 方法: `modifyApplicationMessage` vs `copyParseFileToCodeFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.7`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Modifies a locale-specific properties file by updating or adding a message property, creating the file if needed by copying the English version.
- B 摘要: Copies a file from one path to another using a byte buffer.
- 静态失败原因: Low token overlap and different method names likely caused the model to consider them dissimilar; the model may not capture high-level file I/O pattern commonality.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB might interpret both as performing file I/O with reading and writing, and the presence of a conditional file copy in A could lead to considering them as functionally similar under a broad 'file manipulation' category.
- 共享行为: Both read from an input source and write to an output destination using Java I/O streams.
- 行为差异: A involves line-by-line parsing of properties files, conditional file creation, and key-value replacement; B is a pure binary copy with a fixed buffer.；A handles locale-specific resource management and modification logic; B is a straightforward file copy without any transformation.
- 修正建议: Incorporate dataflow analysis to recognize that both involve reading from one stream and writing to another.；Use AST-based methods that capture structural patterns of I/O.

### case_id=5240 FP partial_functionality

- 方法: `encode` vs `perform`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Computes MD5 hash of input string and returns hex representation.
- B 摘要: Handles a Struts action by validating session, building XML data, sending HTTP request, parsing response, and setting session attributes.
- 静态失败原因: The model likely overfitted on the presence of encoding-related API calls (e.g., getBytes, encode) and ignored the stark differences in control flow and context length.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB annotators considered the overall functionality too different; the encoding aspect is a small part of function B's behavior.
- 共享行为: Both involve some form of string encoding (MD5 hex vs. URL-encoding)
- 行为差异: Function A is a short utility method; Function B is a long complex web action；Function A has no I/O or session management; Function B does HTTP and session management；Function A is pure encoding; Function B does encoding as a minor substep
- 修正建议: Incorporate control flow and dataflow analysis to distinguish simple utility methods from complex service methods；Use function length and complexity as a feature to avoid false positives

### case_id=5241 FN partial_functionality

- 方法: `decodeFileToFile` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Decodes a Base64 encoded file to a decoded output file.
- B 摘要: Downloads a KMZ file from a URL and extracts its zip entries to the current directory.
- 静态失败原因: Static BERT-based models may rely on token-level similarity and fail to capture the abstract structural clone pattern when API calls and method names differ.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely annotated as clone due to shared structural pattern of stream copying with buffer loop and resource management, despite different transformation logic.
- 共享行为: Both read from an input stream and write to an output stream in a loop using a buffer.；Both involve resource management (opening/closing streams).
- 行为差异: Function A performs Base64 decoding; Function B performs zip extraction.；Function A reads from a local file; Function B reads from a URL.；Function A writes a single output file; Function B writes multiple extracted files.；Function A returns boolean; Function B returns void.
- 修正建议: Incorporate graph-based representations that capture I/O operations and loop structures.；Train on more diverse clone types including structural similarities with different API calls.

### case_id=5242 FP boilerplate_overlap

- 方法: `getLinksFromURLFast` vs `getVersion`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Parses HTML from a URL and extracts links and link text using regex, returning two vectors.
- B 摘要: Fetches the first line of a remote version file from a URL and returns it as a string.
- 静态失败原因: The static model likely overemphasized the shared boilerplate pattern (URL, BufferedReader, while-read) and ignored the distinct computational logic and output types.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the functions have entirely different goals and outputs, despite sharing similar boilerplate I/O code.
- 共享行为: Both open a URL connection and use BufferedReader to read lines from the input stream.
- 行为差异: Function A extracts and processes multiple pieces of data (links and texts) from HTML content; Function B simply reads and returns the first line.；Function A uses regex to parse the page and constructs multiple vectors; Function B only reads until end of stream and returns the last read line.
- 修正建议: Incorporate data flow analysis to distinguish different operations on the read data.；Use control flow graph features that capture the functional intent beyond I/O setup.

### case_id=5243 FP long_range_semantics

- 方法: `loadDefaultSettings` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `static_summary_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Loads default settings by copying a resource from classpath to a file.
- B 摘要: Handles user action events to set various application preferences (e.g., Graphviz path) and update UI components.
- 静态失败原因: Static BERT/GraphCodeBERT likely failed due to the long-range nature of function B (truncated input causing loss of context) and possible lexical overlap in keywords like 'default', 'settings', or common Java constructs (try-catch), leading to a false positive.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB labels these as non-clones because they have no functional similarity; one is a file copy utility, the other is a UI event handler for multiple settings.
- 行为差异: Function A performs file I/O copying a default config file; Function B handles GUI events and updates preferences.；Function A uses IOUtils for input/output streams; Function B uses JFileChooser, Swing components, and preference storage.；Function A is a simple private utility; Function B is a complex public action handler with many conditional branches.
- 修正建议: Improve handling of long functions by using better truncation or hierarchical representations.；Incorporate dataflow analysis to distinguish file I/O from UI event handling.；Use type-aware embeddings to differentiate utility methods from event handlers.

### case_id=5244 FN partial_functionality

- 方法: `downLoadZippedFile` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a zipped file from a URL, extracts it to a destination directory, and returns the directory URL.
- B 摘要: Retrieves a resource stream with caching, returning an InputStream for reading the resource content.
- 静态失败原因: Static BERT/GraphCodeBERT models rely on lexical and syntactic similarity; the low token Jaccard (0.18) and different method signatures led to a non-clone prediction, missing the shared functionality and structural patterns.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB labels this as a clone because both functions share the core concept of downloading a resource from a URL and storing it locally, with similar resource management patterns, despite differences in caching and post-processing.
- 共享行为: Both open a URLConnection to a remote resource；Both obtain an InputStream and copy data to a local file；Both manage stream closures in finally blocks
- 行为差异: Function A unzips the downloaded file; function B does not；Function A uses a temporary file and deletes it; function B uses a persistent cache；Function A returns a directory URL; function B returns an InputStream；Function A is private static; function B is public synchronized
- 修正建议: Improve training data with more examples of partial functionality clones；Incorporate dataflow or control-flow analysis to capture similar I/O patterns；Use contrastive learning with functional similarity rather than just lexical overlap

### case_id=5245 FN lexical_or_api_overlap

- 方法: `sendRequest` vs `invoke`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends an HTTP request with GZIP-compressed XML, reads response, builds JDOM Document, and returns an empty string.
- B 摘要: Invokes a remote method via HTTP POST with JSON payload, reads JSON response, deserializes it, and returns the result with retry on timeout.
- 静态失败原因: Low token Jaccard (0.076) and very different API usage (URLConnection vs HttpClient) misled the static model to classify as non-clone, but the BCB label was also incorrect.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may have labeled them as clones because both are HTTP client methods that send data and receive responses, but this seems like a mislabel given the substantial differences.
- 共享行为: Both perform HTTP requests and read responses
- 行为差异: Different data formats (XML vs JSON)；Different compression (GZIP vs none)；Different return types (String vs Object)；Error handling (retry logic in B, dialog in A)
- 修正建议: Improve model sensitivity to high-level functional patterns beyond lexical overlap；Incorporate API knowledge or control-flow abstraction

### case_id=5246 FN partial_functionality

- 方法: `loadSourceCode` vs `login`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.2`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Loads source code from a file resource, applies syntax highlighting, and builds an HTML string.
- B 摘要: Performs HTTP login to LOLA service, sends credentials, reads response, and returns session ID.
- 静态失败原因: The model likely failed due to low lexical overlap and focused on method names and specific operations, missing the abstract similarity of URL-based I/O pattern that BCB considers clone-worthy.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider them clones because both exhibit a common pattern of reading from a URL and processing lines, which aligns with Type-4 semantic clone criteria where overall structure is similar despite different specific purposes.
- 共享行为: Both open a URL and read lines via BufferedReader；Both use try-catch for exception handling；Both build a string result from read data
- 行为差异: A reads from local resource, B sends POST to remote server；A loops through all lines, B reads only the first line；A applies syntax highlighting, B extracts session ID from line；A is void and sets instance variable, B returns String
- 修正建议: Enhance model with structural pattern recognition for common I/O sequences；Incorporate API call context to capture network I/O as a feature；Use contrastive learning to better distinguish different I/O tasks

### case_id=5247 FP boilerplate_overlap

- 方法: `readData` vs `_checkLanguagesFiles`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Parses multiple comma-separated static strings into various sets and reads a configuration file to populate mapping structures for Tibetan transliteration.
- B 摘要: Checks existence of language-specific properties files in global and temp directories, creates them if missing, and copies content from global to temp.
- 静态失败原因: Static BERT/GraphCodeBERT may have been misled by the presence of common boilerplate patterns (file I/O, try-catch, loops) and the truncated code A's later file reading part, causing a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone due to extremely low token Jaccard similarity (0.059) and clearly different functionality, despite some shared file I/O boilerplate.
- 共享行为: Both perform file I/O operations.；Both use loops to iterate over collections.；Both handle IOException.
- 行为差异: Function A focuses on parsing and populating data structures; Function B focuses on file existence checks and copying.；Different domains: Tibetan transliteration initialization vs. CMS language file management.；Function A has complex conditional logic; Function B is a straightforward loop with simple file operations.；Function A uses StringTokenizer and hash maps; Function B uses FileChannel for copying.
- 修正建议: Use data flow analysis to distinguish between parsing and file copying.；Incorporate API call sequences to capture finer-grained behavior.；Train with more diverse examples of file processing to avoid overfitting on boilerplate.

### case_id=5248 FP lexical_or_api_overlap

- 方法: `readPage` vs `getVersion`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads all lines from a URL, optionally ignoring comment lines starting with '#', and returns concatenated string.
- B 摘要: Reads the first (or last) line from a specific version URL and returns it as a version string; returns null on failure.
- 静态失败原因: Static BERT models rely heavily on token overlap and common API usage patterns. Both functions share boilerplate code for URL reading, leading to lexical similarity despite different intents and logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically requires significant functional overlap for Type-3/Type-4 clones; these functions serve distinct purposes (general page reading vs. specific version retrieval), so they are not considered clones.
- 共享行为: Both open a URL connection and use BufferedReader to read lines.；Both return a String (or null in case of failure).
- 行为差异: A is generic page reader with optional comment filtering; B is specific version fetcher with no filtering.；A throws Exception; B catches Exception and returns null.；A concatenates all lines; B only keeps the last line read.；A requires a boolean parameter; B has no parameters.
- 修正建议: Incorporate data flow analysis to distinguish between different operations on the read data.；Use contrastive learning that emphasizes functional similarity over lexical overlap.；Include control flow and structural comparisons to capture conditional logic differences.

### case_id=5249 FP lexical_or_api_overlap

- 方法: `retrieveQ` vs `checkForUpgrade`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Retrieves the entire content of a URL as a string.
- B 摘要: Performs a software upgrade check by querying a remote license server and updating the local database and UI accordingly.
- 静态失败原因: The static model likely overemphasized common API usage patterns (e.g., URL, URLConnection, BufferedReader, while loop) and overlooked the larger functional context, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels non-clones when functions differ significantly in purpose and structure, despite minor syntactic overlaps. The low token Jaccard and distinct overall functionality likely led to the non-clone label.
- 共享行为: Open an HTTP URL connection and read response into a string using BufferedReader.
- 行为差异: Function A is a generic URL content fetcher; B is a complex upgrade routine with database queries and UI manipulation.；A returns a string; B returns void and has no meaningful return value.；A prints the HTTP response message; B does not.；B includes SQL operations, XML parsing, and conditional UI visibility changes; A has none.
- 修正建议: Incorporate graph-based representations to capture control and data flow beyond lexical tokens.；Use contrastive learning or improve handling of long-range semantics.；Add a module to detect boilerplate I/O patterns and reduce their influence on similarity.

### case_id=5250 FN benchmark_preference_bias

- 方法: `createNew` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Creates a file resource with name from input stream, handling special names '.request' and '.tokens', and returns a file object or null.
- B 摘要: Launches an Eclipse launch configuration by processing pom.xml files, setting Hibernate dialect, copying reverse engineering file, and scheduling an install action.
- 静态失败原因: The static model correctly predicted non-clone due to low token overlap (Jaccard 0.074) and different domains; the BCB label is likely incorrect, so the model did not fail but rather disagreed with a possibly erroneous annotation.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB label may be erroneous; possibly a random mislabeling or based on superficial similarity like both checking conditions and writing to files.
- 共享行为: Both involve file I/O operations (reading/writing files).；Both check conditions before proceeding (allowedClient vs. isNexOpenProject).
- 行为差异: Function A is a simple file creation with owner permission check; Function B is a complex Eclipse plugin launch sequence.；Function A handles only two specific filenames; Function B processes XML documents and sets persistent properties.；Function A returns a Resource object or null; Function B is void and throws CoreException.；Function A uses FileOutputStream and IOUtils.copy; Function B uses ContentHandlerTemplate and ByteArrayOutputStream.
- 修正建议: Re-examine BCB annotation for this pair to verify if it is a labeling error.；If annotation is correct, consider adding domain-specific features to capture deeper semantic differences.

### case_id=5251 FN benchmark_preference_bias

- 方法: `modifyApplicationMessage` vs `setPayload`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Modifies a locale-specific properties file by replacing or adding a key-value pair for a given message name.
- B 摘要: Copies the content of a headless data file into a header file using file channels and recurses to process next header.
- 静态失败原因: Static BERT likely correctly identified the low token overlap and different control flow, but BCB's annotation may be erroneous due to over-broad functionality grouping.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might consider both as 'file modification' or 'data writing' operations, overemphasizing the generic file I/O aspect and ignoring the entirely different logic and data structures.
- 共享行为: Both perform file I/O operations involving reading and writing files.
- 行为差异: Function A deals with properties file content manipulation (string replacement, line-by-line), while Function B does binary file copying using FileChannel.transferTo.；Function A handles multiple file existence checks and creation, Function B assumes files exist and focuses on transfer.；Function A modifies a single file per call, Function B operates on an array of headers and recurses.
- 修正建议: Re-evaluate BCB annotation for this pair to ensure it is not a false positive clone label.；Improve benchmark definition to exclude such pairs with only generic file I/O as common behavior.

### case_id=5252 FN benchmark_preference_bias

- 方法: `read` vs `readURL`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `preference_memory_with_manual_audit`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Reads from a URL or file, returns a status code.
- B 摘要: Reads from a URL and prints each line to stdout.
- 静态失败原因: Static models may have focused on token-level differences (low Jaccard) and missed the partial functional overlap; they predicted non-clone due to different control flow and output behavior, whereas BCB's lenient labeling considered them acceptable Type-4 clones.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB likely considered both as reading from a URL/input resource and processing, with leniency toward partial functionality and output differences.
- 共享行为: Both open a stream from a URL；Both handle exceptions (IOException/Exception)；Both involve reading input data
- 行为差异: A returns an int status, B returns void and prints；A also handles local files, B only URLs；A does not close streams, B closes in finally；A delegates to another read method, B reads lines itself
- 修正建议: Incorporate dataflow and behavioral similarity beyond exact token matching；Adjust threshold to accept partial clones with different outputs but similar I/O patterns；Use contrastive learning with BCB-style annotations to capture lenient clone definitions

### case_id=5253 FP boilerplate_overlap

- 方法: `doVersionCheck` vs `get`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Checks for new version of jEdit by reading a version file from a URL and comparing build numbers.
- B 摘要: Fetches an array of GameRecord objects from a URL using HTTP GET with custom headers.
- 静态失败原因: Static BERT/GraphCodeBERT may have been misled by the overlapping boilerplate code (try-catch with BufferedReader, while loop, string parsing) and the presence of common API calls (URL, openConnection, etc.), while lacking deeper semantic understanding of the overall task.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the functions have distinct high-level purposes (version check vs data retrieval) despite sharing a common I/O pattern. The similarity is considered superficial and not indicative of functional equivalence.
- 共享行为: Both open a URL and read data line by line using BufferedReader；Both handle IOException；Both parse each line with conditional checks；Both use standard Java I/O classes
- 行为差异: Different HTTP method: doVersionCheck uses default GET, get explicitly sets GET；Different parsing: doVersionCheck looks for .version and .build prefixes, get skips lines starting with '#' and decodes GameRecord；Different output: doVersionCheck returns void and shows UI messages, get returns GameRecord array or null；Different error handling: doVersionCheck shows error dialog, get prints to stdout/stderr
- 修正建议: Incorporate method name and surrounding context to infer purpose；Use data flow analysis to capture differences in processing logic；Integrate type information (return types, parameter types) more explicitly；Add contrastive training with more diverse non-clone pairs sharing only I/O structure

### case_id=5254 FN benchmark_preference_bias

- 方法: `gerarTutorialPage` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Generates a tutorial website by creating directories, copying CSS files, and writing HTML pages.
- B 摘要: Retrieves a resource as a cached InputStream from a URL, handling HTTP connections and file caching.
- 静态失败原因: The static BERT model correctly predicted non-clone; the BCB label appears to be a false positive, so the model did not fail.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as clone due to superficial similarity: both have file copy operations and exception handling, but the core functionality is completely unrelated.
- 共享行为: Both perform file I/O operations；Both handle exceptions with try-catch；Both output log messages
- 行为差异: Function A creates a whole website; function B retrieves a single resource；Function A uses FileChannel to copy files; function B uses Buffered streams；Function A has no networking; function B makes HTTP requests；Function A returns boolean; function B returns InputStream or null
- 修正建议: Re-evaluate the BCB label for this pair; consider removing from clone set；Improve benchmark annotation guidelines to avoid superficial matches

### case_id=5255 FP boilerplate_overlap

- 方法: `copy` vs `readData`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Copies a file from source to destination using buffered I/O with resource cleanup.
- B 摘要: Reads and parses a large configuration file (tibetan transliteration data) into multiple sets and maps with error handling.
- 静态失败原因: The static model likely overfitted to superficial similarities like 'static void', 'IOException', 'while' loops, and try-catch/finally blocks, ignoring the vastly different goals and data flows. The long span of code_b may have caused the model to misjudge overall semantics.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels it non-clone because the functionalities are completely different: file copy vs. data initialization. There is no partial functional overlap that BCB typically accepts for Type-3/Type-4 clones.
- 共享行为: Both are static void methods that handle I/O operations with try-catch or finally.；Both use loops to process data sequentially.
- 行为差异: A copies byte streams; B parses tokenized strings into data structures.；A has a single loop over a file stream; B has many loops over tokenized comma-separated values.；A uses FileInputStream/FileOutputStream; B uses StringTokenizer and modifies global sets/maps.；B has extensive conditional logic and error handling; A has simple null checks.
- 修正建议: Improve training with more diverse negative pairs having similar boilerplate but different semantics.；Incorporate AST or data-flow features to capture structural differences.；Use code summarization or function naming to distinguish high-level intent.

### case_id=5256 FN partial_functionality

- 方法: `runScript` vs `runInternal`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a script from a URL and returns its content as a string, with basic error handling.
- B 摘要: Handles HTTP connection to download books or parse OPDS catalog entries, with complex error handling, redirects, and partial loading.
- 静态失败原因: The low token overlap and significantly different control flow and structure likely caused the model to predict non-clone, missing the broad functional similarity in opening a URL connection.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider this a clone because both functions perform an HTTP GET operation and read data from a URL, albeit with different purposes and complexity levels.
- 共享行为: Both open a URL connection and read input from the stream.
- 行为差异: Function A is a simple synchronous read returning a string; Function B is a void method with multiple stages, conditionals, and side effects.；Function A has minimal error handling (only 'error!'); Function B has detailed error handling, timeouts, and progress reporting.；Function B includes additional logic like handling Content-Disposition, response codes, content types, and optional downloading.；Function A reads a single script file; Function B deals with OPDS catalog browsing and book downloads.
- 修正建议: Enhance the model to recognize behavioral patterns at a higher level, such as 'URL reading' as a common sub-function.；Incorporate data flow analysis to abstract away details like variable names and specific error handling.

### case_id=5257 FN benchmark_preference_bias

- 方法: `run` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Reads a file input stream, optionally wraps with diagnostic counting readers/writers, then pumps data to an output file.
- B 摘要: Launches a Maven build configuration for a NexOpen project, checking for pom files, processing XML profiles, and scheduling a project install with reverse engineering setup.
- 静态失败原因: In this case, the static model correctly predicted non-clone (0). The model likely failed to detect a clone only if BCB's ground truth is considered; from an independent analysis, the functions are not clones, so the model did not actually fail.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might have incorrectly labeled this as a clone due to a partial similarity in the concept of 'running/launching' something, or due to annotation noise. There is no significant behavioral overlap even at Type-4 level.
- 共享行为: Both perform operations on input/output streams, but with completely different purposes and contexts.
- 行为差异: Function A is a simple file copy with optional byte counting.；Function B is a complex Eclipse plugin launch handler involving project validation, XML processing, property handling, and job scheduling.；Function A has no dependency on Eclipse or Maven; Function B is tightly coupled to Eclipse workspace and Maven.；Function A uses anonymous inner classes for diagnostic; Function B uses callback and handles CoreException.
- 修正建议: Re-evaluate BCB annotation for this pair; likely a false positive in the benchmark.；If BCB label is deemed correct, improve model to consider high-level functional roles, but current evidence suggests label error.

### case_id=5258 FP boilerplate_overlap

- 方法: `main` vs `convert`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Parses a Prolog file and generates adapter classes, serialized metadata, and a JAR file with debug support.
- B 摘要: Reads an ACRNEMA stream file, validates and augments DICOM metadata, and writes a DICOM file with optional pixel data inflation.
- 静态失败原因: The static model likely overemphasized structural similarities such as common Java API usage (e.g., File, InputStream, FileInputStream, BufferedOutputStream, try-finally) and control flow patterns (if-return, try-catch), ignoring the distinct domain logic and intent.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels as non-clone because the functions have completely different high-level purposes and domain-specific algorithms, despite sharing some low-level I/O patterns.
- 共享行为: Both read input files and write output files using streams；Both perform conditional checks and error handling with early returns；Both use Java I/O classes (File, InputStream, OutputStream, etc.)
- 行为差异: Different domains: Prolog adapter generation vs. medical image format conversion；Different parsing logic: Prolog parser vs. DICOM parser；Different output: JAR file vs. DICOM file；Different processing steps: code generation vs. pixel data manipulation
- 修正建议: Use code representation that captures high-level semantics, such as AST-based embeddings with control flow abstraction.；Incorporate domain knowledge or code summarization to distinguish different application contexts.；Train on more diverse and balanced clone pairs to reduce bias toward common API patterns.

### case_id=5259 FN partial_functionality

- 方法: `getFile` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies its endpoint XML attribute, and saves it to a temporary location.
- B 摘要: Reads a dataset from a zip file, extracts rule files, evaluates performance, and prints results.
- 静态失败原因: The low token Jaccard similarity (0.08) and lack of overlapping keywords made the model confident they are different. The model likely missed the abstract I/O pattern that BCB annotators considered as partial functionality clone.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB annotators may have considered the common pattern of reading from an input source (URL or zip) and writing to a file, along with temporary file creation, as a partial functionality similarity, thus labeling them as Type-3/Type-4 clones.
- 共享行为: Both perform file I/O operations using streams.；Both create or use temporary files during processing.
- 行为差异: Code A downloads a file from a URL; Code B reads from a local zip file.；Code A manipulates XML content; Code B parses rules and evaluates performance.；Code A returns a file path; Code B outputs results to console.；Code A has multiple exception handling for specific exceptions; Code B throws generic Exception.
- 修正建议: Include dataflow analysis to capture high-level I/O operations.；Add semantic role labeling to identify input/output sources.

### case_id=5260 FP dataflow_blindspot

- 方法: `readData` vs `readAndRewrite`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_with_trace`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Parses multiple comma-separated string constants into sets and a map for Tibetan transliteration.
- B 摘要: Reads a DICOM image file and rewrites it to another file after processing pixel data.
- 静态失败原因: Static BERT/GraphCodeBERT may have been misled by the common method name prefix 'read' and the presence of common Java constructs like StringTokenizer or file I/O, but the underlying semantics are entirely different. The low token Jaccard suggests the model might have relied on structural patterns or embedding similarity that erroneously matched due to unrelated API usage.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 dataflow_trace_and_outputs。
- BCB 偏好解释: BCB typically labels non-clones when functions have completely different functionality and data sources, even if both are 'read' operations. This pair is clearly non-clone.
- 共享行为: Both involve reading and processing data from some source.
- 行为差异: Function A parses predefined string constants into sets; Function B reads binary DICOM files and writes them back.；Function A builds static data structures for transliteration; Function B processes medical image data with pixel reading/writing.；Function A uses StringTokenizer; Function B uses complex DICOM libraries.
- 修正建议: Improve model's ability to distinguish data sources and output targets.；Incorporate more robust semantic understanding of method signatures and domain contexts.

### case_id=5261 FP lexical_or_api_overlap

- 方法: `import_hints` vs `getVersion`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Imports hints from a URL or file, parsing integers for piece placement on a board.
- B 摘要: Retrieves a version string from a fixed URL using HTTP connection.
- 静态失败原因: Static BERT likely overemphasized the common API sequence (URL, BufferedReader, try-catch) leading to a false positive despite different semantics.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels based on overall functionality; these functions serve distinct purposes with no overlap in core logic.
- 共享行为: Both open a URL and read data using BufferedReader
- 行为差异: Different return types (boolean vs String)；Different parsing logic (hints with multiple fields vs single line version)；Different actions on data (place piece vs return string)；Different URL sources and error handling scope
- 修正建议: Incorporate dataflow or control flow features to capture semantic intent beyond API usage；Add contrastive training examples that contain similar boilerplate but different logic

### case_id=5262 FP lexical_or_api_overlap

- 方法: `readPage` vs `executePost`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a web page via GET, optionally skipping comment lines starting with '#'.
- B 摘要: Executes an HTTP POST request with parameters and returns the response string.
- 静态失败原因: Static BERT models may have focused on the common lexical pattern of opening a URL, reading lines, and returning a string, overlooking the critical differences in HTTP method and parameter handling.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels as non-clone because the methods have different HTTP methods (GET vs POST), different parameter handling, and the presence of comment filtering in A makes them functionally distinct despite both reading from URLs.
- 共享行为: Both open a URL connection；Both read the response line by line using BufferedReader；Both return the response content as a string
- 行为差异: A uses HTTP GET (default), B uses HTTP POST；A has optional comment line filtering, B does not；B sends URL parameters via output stream, A does not；B includes exception handling and connection disconnect, A does not
- 修正建议: Incorporate explicit features for HTTP method；Highlight the presence/absence of output writing；Use dataflow analysis to distinguish input and output streams；Include method signature context (method name and parameters)

### case_id=5263 FN partial_functionality

- 方法: `fileDownload` vs `postRequest`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a file from a URL and writes it to a local file.
- B 摘要: Sends an HTTP POST request with data and returns the response as a string.
- 静态失败原因: The model may have been misled by low token overlap (0.29), different method names, and different output handling (file vs string), failing to recognize the underlying commonality of URL-based I/O.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considers both as network I/O operations that involve reading from a URL, thus sharing partial functionality of 'fetching data from a URL', which aligns with broad Type-3/Type-4 clone criteria.
- 共享行为: Both open a URLConnection to a given URL；Both read input from the connection's input stream；Both use basic I/O streams and exception handling
- 行为差异: fileDownload writes the response directly to a file, while postRequest returns the response as a string；postRequest sends data via POST using PrintWriter, while fileDownload does not send data；fileDownload uses read() char by char, postRequest uses readLine()
- 修正建议: Incorporate dataflow or program dependency information to capture semantic similarities in I/O patterns；Use contrastive learning to better distinguish between truly different tasks and those sharing partial functionality；Augment training data with examples of partial functional clones that differ in output handling

### case_id=5264 FN partial_functionality

- 方法: `modifyApplicationMessage` vs `createNew`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Modifies or adds a property in a locale-specific .properties file, creating a copy of an English template if the target file does not exist.
- B 摘要: Creates a new file from an InputStream in the current directory, only if the user is the owner of the folder.
- 静态失败原因: Low token Jaccard (0.12) and different method names/parameters; static BERT models rely on token overlap and structural similarity, which are insufficient to capture the broad BCB notion of functional similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB might consider these as Type-3/Type-4 clones due to shared file-writing patterns and dataflow (read from source, write to destination) despite different contexts.
- 共享行为: Both involve file I/O operations (reading and writing files).；Both check conditions before writing (file existence check in A, ownership check in B).；Both use try-catch or try-finally blocks for error handling.
- 行为差异: A reads and manipulates a properties file (key-value pairs), B copies raw binary data from an InputStream.；A has locale-specific logic and property name matching; B has ownership and name restrictions.；A creates a locale file by copying English template if missing; B handles different file names with special cases.；A appends a new key-value if not found; B returns a Resource object or null.
- 修正建议: Incorporate data flow analysis to distinguish property manipulation from generic file copy.；Use fine-grained semantic role labeling to capture method purpose beyond I/O boilerplate.；Include more training examples of partial-functionality clones with low token overlap.

### case_id=5265 FP boilerplate_overlap

- 方法: `copy` vs `readData`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Copies a file or directory from a Hadoop filesystem to a local destination, optionally deleting the source.
- B 摘要: Reads a configuration file to initialize various sets and hash maps for processing Tibetan transliteration.
- 静态失败原因: The static model may have been misled by the presence of common programming constructs (e.g., loops, conditional statements) and possibly the method names 'copy' and 'readData' both being common I/O related names, but they share no semantic similarity. The model likely overfitted to superficial patterns and failed to capture the deep semantics due to the long and complex nature of function B.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would not consider these clones because they perform completely different tasks: one is a generic file copy utility, the other is a domain-specific configuration parser for Tibetan transliteration. There is no partial functional overlap.
- 共享行为: Both functions contain loops and conditional logic, but their purposes are entirely different.
- 行为差异: copy performs file system operations (HDFS to local)；readData parses string tokens and populates data structures；copy uses Hadoop FileSystem API；readData uses StringTokenizer and HashSet
- 修正建议: Improve model training to distinguish between generic boilerplate and domain-specific logic；Incorporate structural information like data flow to recognize different operations；Use attention mechanisms that can focus on key API calls (e.g., FileSystem.open vs StringTokenizer)

### case_id=5266 FN dataflow_blindspot

- 方法: `copyResource` vs `copy`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `dynamic_equivalence_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Copies a source (URL or file) to a destination file using InputStream reading byte-by-byte.
- B 摘要: Copies a source file to a destination file using FileChannel and memory-mapped buffer.
- 静态失败原因: Static models rely on lexical and structural similarity; low Jaccard (0.218) and different APIs (InputStream vs FileChannel) mask the semantic equivalence of file copying.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行价值高：该样本可能是 API 写法不同但行为等价的漏报。建议测试目标为 input_output_equivalence。
- BCB 偏好解释: BCB often labels Type-4 clones where functions perform the same high-level operation (copying a file or resource) regardless of API differences.
- 共享行为: Copy entire content from a source to a destination file；Close the input/output streams/channels after copying
- 行为差异: Source type: A supports both URL and file; B only file；I/O method: A uses InputStream.read() loop; B uses FileChannel and MappedByteBuffer；Error handling: A throws Exception; B throws IOException with try-finally
- 修正建议: Incorporate program analysis to detect I/O operations and data flow to files；Use contrastive learning with aligned I/O pairs；Augment training data with semantically similar but syntactically diverse examples

### case_id=5267 FP partial_functionality

- 方法: `getWebPage` vs `getLinksFromURLFast`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads the entire content of a URL and returns it as a single string.
- B 摘要: Reads a URL, extracts hyperlinks and their anchor texts using regex, and returns them as two vectors.
- 静态失败原因: The model likely overemphasized the common pattern of opening a URL, reading with BufferedReader, and appending lines, while ignoring the significant additional logic (regex parsing, vector construction) that differentiates the functions. The low token Jaccard suggests limited lexical overlap, but the structural similarity in the reading loop may have misled the model.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB typically labels functions as non-clones when they perform different high-level tasks, even if they share some boilerplate. Here, getWebPage is a simple fetcher, while getLinksFromURLFast is a link extractor, so they are not considered clones.
- 共享行为: Open a URL connection；Read lines from the URL input stream；Concatenate lines into a buffer
- 行为差异: Function A returns raw page content; Function B returns structured link and text vectors；Function B uses regular expressions to parse HTML anchor tags；Function B includes time checks and additional utility calls；Function B has a different exception handling signature (throws Exception vs catch IOException)
- 修正建议: Incorporate dataflow analysis to recognize that the second function processes the page content differently；Train on more examples that distinguish simple fetching from parsing/extraction tasks；Use contrastive learning to emphasize differences in output types and post-processing logic

### case_id=5268 FN benchmark_preference_bias

- 方法: `getWebByUrl` vs `register`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a web page from a given URL, saves it to a file, and recursively extracts URLs for further crawling.
- B 摘要: Registers a user by validating input, encoding password, creating a hash, making an HTTP request to a forum for registration, persisting the user, and sending a confirmation email.
- 静态失败原因: The static BERT/GraphCodeBERT model likely relied on the low token similarity and the stark difference in method names, return types, and logic, correctly predicting non-clone under strict semantics. The failure is due to benchmark preference bias where the BCB annotation may have been overly broad.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might consider this pair as clones because both functions involve opening a URL connection and reading the input stream, which is a common pattern labeled as Type-3 or Type-4 in some benchmarks. However, the overall functionality differs vastly, so this interpretation is weak.
- 共享行为: Both open a URL connection and read input line by line using BufferedReader；Both contain try-catch blocks for exception handling；Both perform some form of logging or output (print statements in A, logger in B)
- 行为差异: A writes the retrieved content to a local file and recursively processes URLs, while B performs user registration with multiple steps including password encoding, hash generation, and database persistence；A returns void, while B returns a boolean indicating success/failure；B includes validation of input object and uses dependency injection (entityManager, passwordEncoder), whereas A has no such dependencies；B makes an HTTP POST/GET to an external forum URL, while A simply reads a URL without writing to it
- 修正建议: Improve the model's ability to differentiate shared boilerplate patterns from semantically equivalent functionality；Incorporate more fine-grained functional semantics or program analysis to avoid false negatives caused by overly broad clone definitions

### case_id=5269 FN partial_functionality

- 方法: `writeFileType` vs `CheckUrl`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads URIs from a file, connects to each URL, checks first 100 lines for RDF keywords, and writes classification to an output file.
- B 摘要: Connects to a single URL and returns its first line as a string.
- 静态失败原因: The model likely relied on low token overlap (Jaccard 0.17) and different method names and overall structure, missing the shared URL-reading pattern. Static embeddings may not capture data flow or API call sequences effectively.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled this as a clone due to both functions sharing the core behavior of opening a URL connection and reading content, which is a common API usage pattern. In BigCloneBench, broad Type-3/Type-4 clones often accept such partial functionality similarity.
- 共享行为: Both open a URL and read content using BufferedReader.
- 行为差异: A processes multiple URIs from a file; B handles a single URL.；A writes results to a file; B returns a string.；A checks for specific keywords and classifies; B just returns the first line.；A reads up to 100 lines; B reads only first line.
- 修正建议: Train model on more diverse clone pairs with low lexical but high semantic similarity.；Incorporate API call sequence similarity.；Use graph-based representations capturing data flow.

### case_id=5270 FP lexical_or_api_overlap

- 方法: `getLinksFromURLFast` vs `main`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Extracts hyperlinks and their text from a given URL's HTML content using regular expressions.
- B 摘要: Reads the content of a URL and prints each line to standard output.
- 静态失败原因: Static models may focus on token overlap (URL, BufferedReader, readLine) and miss the high-level semantic difference.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels non-clone because the methods have different purposes and outputs; the shared reading part is a common boilerplate not sufficient for clone detection.
- 共享行为: Open a URL and read its content line by line using BufferedReader
- 行为差异: Method A parses and extracts links; Method B simply prints lines.；Method A uses regex to parse link tags; Method B does not parse.；Method A returns a Vector array; Method B is void.；Method A includes debug prints; Method B does not.
- 修正建议: Include data flow analysis to track how the read content is used.；Require functional similarity beyond common API sequences.；Use a model that captures program output or transformation purpose.

### case_id=5271 FN partial_functionality

- 方法: `copyResource` vs `transformSingleFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource from a URL or file to a destination file byte by byte.
- B 摘要: Transforms an X3D file to a gzipped VRML file, with UI messages and error handling.
- 静态失败原因: The model relied on token overlap and structure, which are low, missing the abstract similarity of the I/O streaming loop. It did not recognize that both functions implement a copy loop from input to output.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels as clones functions that perform the core operation of copying data between streams, even if the specific source, destination, or compression differ. The while-loop pattern of read and write is a common functional fragment.
- 共享行为: Both read from an input stream and write to an output stream in a loop.；Both handle file I/O and close streams.
- 行为差异: A copies raw data; B applies gzip compression.；A reads byte-by-byte; B uses buffered reads.；B includes multiple preprocessing steps (getting file, calling another transform, UI messages).；A throws an exception on failure; B catches exception and returns null.
- 修正建议: Train on more examples of stream-copy patterns with different APIs.；Incorporate program analysis to identify read-write loops as a functional signature.；Use a model that captures higher-level dataflow or common abstract operations.

### case_id=5272 FN benchmark_preference_bias

- 方法: `createButtonCopyToClipboard` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Creates a button that copies an environment report to clipboard when selected.
- B 摘要: Builds a site for editing by processing pages, applying XML transformations, and writing output files.
- 静态失败原因: Given the extremely low token Jaccard (0.018) and lack of shared structure or API usage, a static BERT model correctly predicted non-clone; this suggests the BCB label is erroneous, so the model did not fail from a semantic viewpoint.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have mislabeled this pair due to annotation error or overly broad interpretation of 'partial functionality' (e.g., both are 'builder' methods), but no clear semantic overlap exists.
- 行为差异: Function A is a short UI setup method; B is a long, complex file processing and transformation method.；A uses SWT widgets and clipboard operations; B uses file I/O, XML parsing, transformers, and string manipulation.；A has no parameters; B has eight parameters and multiple throws declarations.；B includes loops, conditionals, error handling, and multiple sub-steps absent in A.
- 修正建议: Review and correct the ground-truth label for this pair in the benchmark.；Ensure annotation guidelines require clear functional overlap for clone labeling.；Use cross-validation with multiple annotators to reduce false positives.

### case_id=5273 FP lexical_or_api_overlap

- 方法: `run` vs `getRequestContent`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches a tile from a URL, reads its entire GeoJSON content, parses it into geometries, and loads the result into a data structure.
- B 摘要: Opens a URL connection and reads a single line of content, returning it as a string.
- 静态失败原因: The static model likely focused on shared API tokens (URL, BufferedReader, InputStreamReader) and the overall structure of opening a connection and reading lines, ignoring the drastic difference in scope and data flow.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically treats broad Type-3/Type-4 as clones only if the core functionality is similar. Here, one is a complex tile-loading pipeline, the other is a trivial HTTP line reader. The high-level purpose and output are distinct, so BCB would label as non-clone.
- 共享行为: Both open a URL and use BufferedReader to read text from an InputStream
- 行为差异: A reads the full file content into a string; B reads only the first line.；A processes the content into a VectorTile and GeometryCollection; B simply returns the raw line.；A includes caching via synchronized set and error handling for multiple protocols; B only handles HTTP and has minimal error handling.；A ultimately updates the data loader; B just returns the string.
- 修正建议: Incorporate data-flow analysis to capture the full data transformation chain.；Use contrastive learning to penalize functions with similar API usage but very different semantics.

### case_id=5274 FP boilerplate_overlap

- 方法: `populateResources` vs `getFullScreenUrl`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Loads templates and images from classpath resources and saves them as persistent resources.
- B 摘要: Extracts video ID and timestamp from a YouTube URL to construct a full-screen video URL.
- 静态失败原因: The model likely overemphasized the common I/O boilerplate (URL connection, BufferedReader, try-catch) and missed the distinct high-level functionality due to lack of deep semantic understanding.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels as non-clone because the functions have completely different purposes and only share generic I/O boilerplate, which is insufficient for semantic equivalence.
- 共享行为: Both open URL connections and read data line by line using BufferedReader；Both use try-catch for exception handling；Both perform string parsing on read data
- 行为差异: Function A loads and saves template resources and images, while Function B extracts and constructs a YouTube video URL；Function A uses multiple resource types (templates, images), Function B focuses solely on parsing one stream；Function A saves data to persistent storage, Function B returns a string
- 修正建议: Incorporate data flow analysis to differentiate data processing paths；Use code summarization or docstring embeddings to capture overall function goal；Apply fine-grained token-level attention to distinguish boilerplate from core logic

### case_id=5275 FN partial_functionality

- 方法: `main` vs `saveProject`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a HeartShapedIsland.kmz file from a URL and extracts its contents to the local file system.
- B 摘要: Saves a project including geospatial layers, databases, and trajectories to a zip file, creating directory structure and XML files.
- 静态失败原因: Static BERT models rely on lexical overlap (token Jaccard 0.109) and structural similarity, which are low here. They miss the high-level semantic domain alignment (geospatial data processing) that BCB considers.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider them clones because both operate on geospatial compressed files (KMZ/KML) and perform file extraction/creation operations, which is a broad semantic similarity in the context of geographic data handling.
- 共享行为: Both handle geospatial data (KMZ/KML) files；Both involve zip compression/decompression；Both perform file I/O operations
- 行为差异: Code_a downloads a single file from a hardcoded URL; Code_b processes multiple input sets and creates a complex project structure；Code_a only extracts; Code_b creates directories, writes version, copies databases, and generates multiple XML files；Code_a is a void main; Code_b returns a boolean and has many parameters
- 修正建议: Incorporate domain-specific embeddings or retrieval of similar API usage patterns；Use data flow analysis to detect shared high-level operations like 'read from zip' and 'write to zip'；Fine-tune on geospatial code to capture domain similarity

### case_id=5276 FP lexical_or_api_overlap

- 方法: `doFinishLoadAttachment` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Loads an attachment, optionally saving it to external storage or opening it via an intent.
- B 摘要: Handles various command actions in a settings dialog, including file choosers for executables and UI preferences.
- 静态失败原因: The model likely over-relied on superficial lexical overlap (e.g., common Java keywords, File, Intent) or boilerplate patterns (try-catch, Toast) while ignoring the overall semantic structure and domain context.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would not consider these clones because they have entirely different functionality and no significant overlapping behavior; they are clearly distinct in domain and implementation.
- 行为差异: Different purposes: attachment handling vs. GUI settings；Different APIs: Android content providers vs. Swing JFileChooser；Different control flow: single conditional branch vs. multiple command handling
- 修正建议: Incorporate AST or dataflow features to capture structural differences；Use contrastive learning with hard negative mining to discourage false positives；Enrich training data with more diverse non-clone pairs

### case_id=5277 FP lexical_or_api_overlap

- 方法: `load` vs `getFrameworkFactory`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches and returns the raw XML content from a pastebin URL given an id.
- B 摘要: Loads a framework factory class from a service configuration file using reflection.
- 静态失败原因: Static BERT/GraphCodeBERT likely over-indexed on lexical overlap (e.g., URL, BufferedReader, readLine) and structural similarity, missing the semantic divergence.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this non-clone because the functions have completely different purposes and outputs despite sharing some I/O patterns.
- 共享行为: Both open a URL or resource and read lines using BufferedReader and InputStreamReader.；Both have exception handling, though different approaches.
- 行为差异: A returns concatenated string of all lines; B instantiates a class from the first non-comment line.；A makes network request to pastebin; B reads from classpath resource.；A shows dialog on error; B throws exception.；A has input length check; B checks URL nullity.
- 修正建议: Incorporate data flow analysis to distinguish output types.；Use contrastive learning to emphasize semantic differences despite API similarity.；Include execution traces or more detailed semantic role labeling.

### case_id=5278 FN partial_functionality

- 方法: `modifyApplicationMessage` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Modifies a properties file for a given locale by copying an English file if needed and replacing a message value.
- B 摘要: Copies a file from one location to another using NIO channels.
- 静态失败原因: Static BERT-based models like GraphCodeBERT rely heavily on surface-level syntax and token patterns. The functions have low token overlap (Jaccard 0.0989), so syntactic similarity is low. The shared functionality of file copying is embedded within larger context in A and uses different API calls (Reader/Writer vs. FileChannel). Static models may not capture this deeper I/O behavior, especially when it's a small part of A. The model likely focused on method names and overall structure, which differ significantly.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider this a Type-4 clone because both functions perform file-to-file copy operations, which is a core functional similarity, despite differences in purpose and method. The initial copy step in A (the while loop reading and writing characters) is functionally analogous to copying a file.
- 共享行为: Both read from a source file and write to a destination file.
- 行为差异: Function A conditionally copies a file and then modifies a specific property, while Function B simply copies the entire file without modification.；Function A uses character-by-character copy for the initial file copy, while Function B uses NIO transferTo for efficient copy.；Function A handles properties parsing and line-by-line processing, while Function B just transfers bytes.
- 修正建议: Use more fine-grained semantic or behavioral embeddings that capture I/O operations.；Incorporate structural information like data flow to identify file copy patterns across different implementations.；Enhance training data with examples of partial functionality similarity.

### case_id=5279 FP boilerplate_overlap

- 方法: `getLinksFromURLFast` vs `doRawRequest`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches a webpage from a given URL, extracts all hyperlinks and their text using regex, and returns them as two vectors.
- B 摘要: Sends a POST request with data to a fixed service URL, reads the response body, and returns it as a string.
- 静态失败原因: GraphCodeBERT likely focused on overlapping API calls (URL, URLConnection, BufferedReader, StringBuffer, readLine) and structural patterns, ignoring the different overall tasks and output types.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels clones based on overall functional similarity, not just common boilerplate. Here the core functionality differs fundamentally (HTML parsing vs. POST request), so it is not a clone.
- 共享行为: Both create a URLConnection, read the response line-by-line with a BufferedReader, and accumulate lines into a StringBuffer.
- 行为差异: Function A uses GET (default) and parses HTML for links; function B uses POST with output data.；Function A returns parsed link/text vectors; function B returns raw response string.；Function A includes regex parsing and time checks; function B does not.
- 修正建议: Improve training to distinguish boilerplate from core functionality.；Add contrastive examples where shared patterns lead to different semantics.

### case_id=5280 FN boilerplate_overlap

- 方法: `sendExceptionToServer` vs `invoke`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends exception details to a server via HTTP POST with a fixed set of parameters.
- B 摘要: Invokes a remote method by serializing arguments and handling retries via HTTP POST.
- 静态失败原因: Low token Jaccard similarity (0.14) and different method names/parameter types led the static model to treat them as unrelated, missing the structural overlap.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may consider them clones because both follow a similar HTTP POST boilerplate pattern, despite differing semantic purposes.
- 共享行为: Both perform HTTP POST requests；Both build request data (URL-encoded or JSON)；Both read HTTP response
- 行为差异: Different intent: error reporting vs. method invocation；Different data construction: hardcoded parameters vs. dynamic serialization；Different response handling: A checks for 'success', B deserializes JSON；Different error handling: A prints to console, B retries and throws
- 修正建议: Incorporate AST-based or structural similarity metrics；Use methods that capture API usage patterns；Include method-level documentation or context

### case_id=5281 FN partial_functionality

- 方法: `executeHttpGet` vs `httpRequestByPOST`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends an HTTP GET request, reads the response line by line, and returns it as a JSONObject.
- B 摘要: Sends an HTTP POST request with parameters, reads the response if status < 400, returns the response string, or sets error fields and returns null.
- 静态失败原因: Static BERT methods rely on token embeddings and structure; they may focus on specific API calls (HttpGet vs HttpPost) and differences in error handling/return type, leading to low similarity (token Jaccard 0.22973). BCB's broader clone definition is not captured by token-level overlap.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB labels these as clones because they share the core behavior of performing an HTTP request and reading the response into a string, a common Type-3/Type-4 clone pattern where the overall functionality is considered similar despite differences in HTTP method and error handling.
- 共享行为: Both use Apache HttpClient to execute an HTTP request；Read response content using BufferedReader and append lines to a string buffer；Return the result (either as JSONObject or String)
- 行为差异: A uses GET, B uses POST；A returns JSONObject, B returns String；A throws Exception on failure, B handles errors by setting fields and returning null；B checks status code and has timeout parameter
- 修正建议: Train with more Type-3/Type-4 examples；Use semantic role labeling to abstract API calls；Incorporate dataflow information to capture similar patterns；Use contrastive learning with functional similarity

### case_id=5282 FN partial_functionality

- 方法: `getFile` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies its endpoint, saves to temporary directory, and returns the file path.
- B 摘要: Copies a file from source to destination using NIO FileChannel transfer.
- 静态失败原因: The model likely focused on overall semantic differences (download vs copy) and low token overlap, missing the shared sub-behavior of file copying via channels. GraphCodeBERT may not capture partial functionality similarity well.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider this a clone because both functions perform file copying via NIO channels, and A's primary action is to download and save a file, which includes a copying step similar to B. The partial overlap in file I/O behavior aligns with Type-4 clone criteria.
- 共享行为: Both use Java NIO channels to copy data from an input source to an output file.
- 行为差异: Function A downloads from a URL and processes XML, while B copies a local file.；A includes error handling, logging, and file deletion/renaming; B is a straightforward copy.
- 修正建议: Incorporate sub-graph matching or dataflow analysis to detect common I/O patterns.；Use multi-level embeddings that capture both global and local semantics.；Train with annotated partial clone pairs to learn such patterns.

### case_id=5283 FN library_context_missing

- 方法: `httpRequestByPOST` vs `callApiPost`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `context_recovery_then_expert`；动态可解性: `low`；执行优先级: `medium`
- A 摘要: Makes HTTP POST using Apache HttpClient, returns response string on success, sets error codes and returns null on failure.
- B 摘要: Makes HTTP POST using HttpURLConnection, returns InputStream on success, throws custom exception on failure.
- 静态失败原因: Static BERT/GraphCodeBERT methods rely heavily on token overlap and API names; low lexical similarity (Jaccard 0.155) and different library APIs (HttpClient vs HttpURLConnection) caused it to miss the semantic similarity.
- 静态 case study: 该类错误缺少关键上下文或需要深层语义，纯静态方法不可靠。
- 动态 case study: 动态执行价值较低：样本可能依赖库、框架、网络、GUI、数据库或项目上下文，需要先恢复环境或 mock 依赖。
- BCB 偏好解释: BCB often annotates functions with similar core functionality (HTTP POST) as Type-3/Type-4 clones despite differences in implementation details, error handling, and libraries.
- 共享行为: Both perform HTTP POST requests with parameters
- 行为差异: Different HTTP client libraries (Apache HttpClient vs HttpURLConnection)；Return type: String vs InputStream；Error handling: null return vs exception throwing；Parameter encoding: UrlEncodedFormEntity vs manual PrintStream
- 修正建议: Incorporate cross-library API mappings；Use dependency-aware embeddings that recognize functionally similar API calls；Add training examples of Type-4 clones with varied implementations

### case_id=5284 FP other

- 方法: `encrypt` vs `perform`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Encrypts a plaintext string using SHA-1 digest and Base64 encoding.
- B 摘要: Handles a web request for concept classification, builds XML, sends HTTP POST, parses response, and sets session attributes.
- 静态失败原因: The model likely focused on superficial commonalities like 'public', 'throws', 'String', and 'return', while missing the entirely different domain and logic. Low token Jaccard (0.035) suggests the model may have over-relied on learned patterns that conflate generic method structure with semantic equivalence.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB labels these as non-clones because they implement completely different functionalities (encryption vs. web controller) with no structural or behavioral overlap beyond trivial Java boilerplate.
- 共享行为: Both are public methods that may throw exceptions.；Both return a String or ActionForward.；Both use String concatenation or manipulation.
- 行为差异: Function A performs cryptographic hashing; Function B handles web request lifecycle.；Function A has no side effects; Function B modifies session and interacts with external URL.；Function A is simple (7 lines); Function B is complex (100+ lines).；Function A uses MessageDigest and BASE64Encoder; Function B uses Struts, HttpSession, URLConnection, etc.
- 修正建议: Enrich training data with more diverse negative pairs from different domains.；Use structural features like AST or control-flow graphs instead of token embeddings alone.；Incorporate data flow or dependency information to distinguish cryptographic operations from web request handling.

### case_id=5285 FN benchmark_preference_bias

- 方法: `encodeFileToFile` vs `modifyApplicationMessage`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Base64 encodes an input file and writes to an output file.
- B 摘要: Modifies a localized properties file by replacing or appending a key-value pair.
- 静态失败原因: The model captured low token similarity (Jaccard=0.205) and functional difference, but BCB's annotation preference accepts boilerplate overlap as clones, causing a mismatch.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may label as clone due to high structural similarity in file I/O boilerplate (stream handling, loops, try-catch-finally), favoring broad Type-3 or partial functionality overlap.
- 共享行为: Both use file streams (FileInputStream/FileOutputStream) with buffering；Both have a read-write loop (while loop)；Both use try-catch-finally with exception handling；Both close streams in finally blocks
- 行为差异: Function A performs Base64 encoding; Function B modifies properties files；Function A returns boolean; Function B returns void；Function B involves reading properties, parsing lines, and handling locales
- 修正建议: Incorporate semantic understanding of core functionality；Treat boilerplate code as non-informative for clone detection；Use task-specific fine-tuning to align model with BCB annotation criteria

### case_id=5286 FP boilerplate_overlap

- 方法: `readData` vs `extractImage`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Reads configuration data from string constants and a file, parsing tokens into sets and maps.
- B 摘要: Extracts an image from an input file, applies scaling and transforms, and writes to an output file.
- 静态失败原因: The static BERT model likely overemphasized superficial boilerplate patterns (try-catch, File, IOException) and ignored the distinct domain-specific operations, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would consider these non-clones because they perform entirely different tasks (data initialization vs. image extraction) with no shared functionality beyond generic boilerplate.
- 共享行为: Both use file I/O；Both include exception handling with try-catch
- 行为差异: A parses tokens and populates data structures; B processes images；A is batch initialization; B is single image conversion；A uses StringTokenizer and regular file reading; B uses BufferedImage and image-specific operations
- 修正建议: Train the model to focus on core functional logic, not just syntactic templates；Incorporate data flow or call graph features to capture actual behavior；Add a preprocessing step to filter out generic boilerplate code

### case_id=5287 FN benchmark_preference_bias

- 方法: `getFile` vs `encodeFileToFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies an XML attribute, and saves the result to a temporary file.
- B 摘要: Reads a file, Base64 encodes the content, and writes the encoded data to another file.
- 静态失败原因: If a static model predicted non-clone (0), it likely captured the clear semantic differences in method names, parameters, and specific operations (network I/O vs Base64 encoding). The model did not fail; rather, BCB's label may be too broad.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled them as clones because both are file-processing utilities that read from a source and write to a file, and they share a similar top-level structure (try-catch-finally with stream handling). However, the core functionality is entirely different.
- 共享行为: Both use file I/O streams to read and write data；Both have try-catch blocks for exception handling
- 行为差异: A involves network download, XML parsing, and attribute modification; B is a simple encoding transformation；A has multiple specific exception catches; B catches only IOException；A returns a file path; B returns a boolean success flag；A uses NIO channels and XML utilities; B uses Base64 encoding stream
- 修正建议: Use more precise semantic features beyond token overlap and boilerplate patterns；Incorporate data flow and API call sequences to distinguish file transformation types；Consider method signatures and return types as discriminative clues

### case_id=5288 FN partial_functionality

- 方法: `fetchURLData` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches data from a URL (with proxy support) and returns as byte array.
- B 摘要: Retrieves a resource as InputStream with caching to local file system.
- 静态失败原因: Static BERT models rely on surface token overlap (Jaccard=0.128) and may miss the deeper functional similarity in URL fetching and stream handling, leading to false negative.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this as clone due to both functions sharing the high-level purpose of fetching data from a URL, despite low lexical similarity and differing implementations (Type-4 similarity).
- 共享行为: Open a URL connection and read input stream；Handle HTTP connections and I/O；Return data from a network resource
- 行为差异: A returns byte array, B returns InputStream；B implements caching with local files, A does not；B uses synchronized and prints debug info, A does not；A supports file:// URLs and proxy configuration
- 修正建议: Train models on pairs with low lexical but high semantic similarity；Incorporate dataflow or graph-based representations to capture I/O patterns；Use contrastive learning to emphasize functional equivalence over lexical overlap

### case_id=5289 FP lexical_or_api_overlap

- 方法: `main` vs `internalCopy`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Generates adapter code from a Prolog file and writes to a JAR.
- B 摘要: Copies a file from source to destination, skipping Thumbs.db.
- 静态失败原因: The model likely focused on shared tokens like 'File', 'InputStream', 'OutputStream', 'System.out.println', and 'IOException', leading to a high similarity score despite fundamental behavioral differences.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB annotation typically flags non-clones when functions have completely different functionality, even if they share some API calls. Here, the purposes are entirely different.
- 共享行为: Both perform file I/O operations；Both use System.out.println for progress messages
- 行为差异: Function A is a complex multi-step code generation pipeline; Function B is a simple byte copy；Function A includes parsing, class generation, and serialization; Function B has no such logic；Function A has command-line argument parsing; Function B does not；Function A handles many exceptions and multiple files; Function B handles only two files
- 修正建议: Train with more contrastive examples of I/O heavy but functionally different code；Use dataflow or control flow features to distinguish simple copy from complex code generation；Add negative mining to focus on functional purpose rather than surface API usage

### case_id=5290 FP lexical_or_api_overlap

- 方法: `actionPerformed` vs `copyFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `1.0`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Event handler that processes GUI commands (e.g., setting paths for Graphviz, ImageMagick, scale image, date format, look-and-feel) and saves preferences.
- B 摘要: Utility method that copies a file from source to destination using FileChannel.
- 静态失败原因: The static model likely overfit to token-level similarities such as common Java keywords (e.g., 'if', 'null', 'File'), method calls (e.g., 'putPref' vs 'transferTo' - low similarity), or general boilerplate structures (e.g., try-finally). The large size of function A and truncation may have caused the model to ignore semantics and focus on superficial patterns.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clones when functions have completely different purposes despite sharing some Java boilerplate (e.g., exception handling).
- 行为差异: Function A is a large GUI event handler with multiple conditional branches; Function B is a simple file-copy utility.；Function A interacts with UI components and preferences; Function B performs pure I/O.；Function A may trigger UI updates and restart prompts; Function B has no side effects beyond file copying.
- 修正建议: Improve model's ability to capture long-range dependencies and overall function purpose.；Introduce training with more diverse negative examples that have overlapping tokens but different semantics.；Use structure-aware features like abstract syntax trees or control flow graphs to distinguish behaviors.

### case_id=5291 FP lexical_or_api_overlap

- 方法: `getDatasetsList` vs `executePost`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Retrieves a list of dataset names from a server using a GET request to a URL with parameter "?server=list", caching the results.
- B 摘要: Executes an HTTP POST request to a target URL with given parameters and returns the response body as a string.
- 静态失败原因: The static BERT model likely focused on superficial lexical and syntactic similarities (e.g., URL, BufferedReader, IOException, try-catch-finally) and missed deeper semantic differences such as HTTP method, return type, caching, and error handling.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the functions have distinct purposes, signatures, and overall behavior, despite sharing some common boilerplate code for network I/O.
- 共享行为: Both open network connections and read from BufferedReader；Both use try-catch-finally blocks for exception handling；Both handle IO-related exceptions
- 行为差异: Different HTTP methods: GET vs POST；Different return types: List<String> vs String；Caching implemented in A but not in B；Error handling: A throws RuntimeException, B returns null
- 修正建议: Incorporate AST-based features to differentiate control flow and data flow；Use contrastive learning on pairs with similar API usage but different semantics；Add attention to method signatures and return types；Include dataflow analysis to capture differences in variable dependencies

### case_id=5292 FN benchmark_preference_bias

- 方法: `getResourceAsStream` vs `copy`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `preference_memory_with_manual_audit`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Retrieves a resource (possibly remote) as an InputStream, with local caching and HTTP conditional GET.
- B 摘要: Copies a file from source path to destination path using FileChannel and MappedByteBuffer.
- 静态失败原因: Static BERT/GraphCodeBERT likely focused on the low token overlap and distinct method names, and the overall structure and control flow differences, missing the high-level similarity of file copying.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have considered these Type-4 clones due to their shared core functionality of copying data from an input to a file, despite differences in source type and additional caching/HTTP logic.
- 共享行为: Both perform file I/O using FileInputStream and FileOutputStream；Both read from an input source and write to an output sink；Both handle resource cleanup in finally or catch blocks
- 行为差异: Function A reads from a URL (remote or local) while B reads from a local file；Function A has caching logic and HTTP conditional requests, B does not；Function A copies byte-by-byte using BufferedStreams, B uses NIO MappedByteBuffer；Function A is synchronized instance method, B is static method
- 修正建议: Improve model to recognize functional similarity beyond token overlap；Use contrastive learning with BCB annotations to capture Type-4 clones；Incorporate dataflow or high-level API usage patterns

### case_id=5293 FN benchmark_preference_bias

- 方法: `login` vs `doVersionCheck`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.6`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Logs into a service by sending credentials via HTTP POST and extracting session ID.
- B 摘要: Checks for a software version update by reading a remote version file and comparing build numbers.
- 静态失败原因: Static BERT models often rely on semantic similarity and may correctly judge these as dissimilar in purpose, but BCB's broader definition allows for structural similarity. The model missed the clone due to the benchmark's preference for structural pattern similarity over strict semantics.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled these as clones because they share a common boilerplate structure of opening a URL, reading data, parsing lines, and handling exceptions, which is a recurring pattern in network I/O functions.
- 共享行为: Both open a URL and read lines from the input stream；Both parse lines for specific string tokens；Both handle exceptions and output messages
- 行为差异: login() does not show wait cursor；doVersionCheck() shows wait cursor and hides it；login() uses POST method and writes data to output stream；doVersionCheck() uses GET method (openStream) and does not write
- 修正建议: Incorporate structural pattern recognition for common I/O sequences；Use contrastive learning with both semantic and structural alignment；Fine-tune on BCB-style annotations to capture broader clone definitions

### case_id=5294 FN benchmark_preference_bias

- 方法: `decodeFileToFile` vs `doGet`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Decodes a Base64-encoded input file and writes the decoded content to an output file, returning success status.
- B 摘要: Handles an HTTP GET request to display a portal page, including user permission checks, logging, caching, and rendering response.
- 静态失败原因: The static BERT model correctly identified no semantic similarity due to very low token overlap and entirely different domains, so it failed to match the potentially erroneous BCB label.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as a clone due to a broad interpretation of 'file I/O' or 'stream processing' similarity, but this is likely an annotation error or outlier in the benchmark.
- 行为差异: Function A performs file I/O and Base64 decoding; Function B handles HTTP request/response and portal page rendering.；Function A has a simple boolean return; Function B returns void and throws ServletException/IOException.；Function A reads from a file input stream; Function B reads from HTTP request parameters.；Function A writes to a file output stream; Function B writes to HTTP response output stream.
- 修正建议: Review BCB annotation for this pair to confirm if it is a clone; likely it should be labeled non-clone.；If maintaining BCB labels, consider adding more context or filtering such outliers during training.

### case_id=5295 FN benchmark_preference_bias

- 方法: `doGet` vs `patch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Handles HTTP GET requests to serve portal pages with authentication, caching, and logging.
- B 摘要: Patches the Minecraft jar by copying it to a backup and opening it for modification.
- 静态失败原因: Static BERT likely correctly predicted non-clone due to low lexical overlap and different domain-specific vocabulary, but BCB label is inconsistent with expected clone criteria.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as a clone due to a annotation error or a very broad interpretation that both perform file-related actions, but the functions are fundamentally different.
- 共享行为: Both involve file I/O operations
- 行为差异: Different input/output: HTTP request/response vs file streams；Different purpose: page serving vs jar patching；Different domains: web portal vs Minecraft；Different complexity: A is large with many steps, B is short
- 修正建议: Verify the BCB annotation for potential error；If annotation is correct, consider that BCB accepts partial functionality similarity, but here even partial functionality is minimal.

### case_id=5296 FP long_range_semantics

- 方法: `copyFile` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `static_summary_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Copies a file from input to output using NIO FileChannel transferTo.
- B 摘要: Handles various GUI action events for settings, including file selection for external tools and saving preferences.
- 静态失败原因: The static model likely only processed a prefix of the very long function B (due to token limits), which includes file chooser code that shares some boilerplate tokens with A (e.g., 'File', 'IOException', 'try', 'catch'), leading to a false positive. The model failed to capture the overall semantic context of B.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB would not label this as clone because the functions are semantically unrelated, with different purposes, control flow, and I/O patterns. The low token similarity and distinct method names further support non-clone.
- 共享行为: Both involve file operations in some way (copying vs. selecting with JFileChooser).
- 行为差异: A performs a single file copy using NIO channels; B is a large event handler with multiple conditional branches.；A has no user interaction; B relies on UI components and user input.；A uses FileChannel transferTo; B uses JFileChooser and file path retrieval.；A throws IOException; B catches exceptions and logs warnings.
- 修正建议: Use whole-function representations or sliding window with aggregation for long functions.；Increase token similarity threshold or add structural matching.；Incorporate dataflow analysis to distinguish file copy from GUI event handling.

### case_id=5297 FP other

- 方法: `actionPerformed` vs `copyFiles`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.2`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Handles UI action events to update various application preferences, including file paths, look-and-feel settings, and other configurations.
- B 摘要: Recursively copies files or directories using file channels, supporting both directory and file copy operations.
- 静态失败原因: The static BERT/GraphCodeBERT model likely misclassified due to weak lexical or API overlap (use of File, file paths, and I/O classes) combined with insufficient context understanding of the complex UI event handler, leading it to incorrectly infer functional similarity.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB would label this as non-clone because the functions have no significant functional overlap: one is a UI event handler managing preferences, the other is a utility for file copying.
- 共享行为: Both involve file system operations (file chooser vs. file copy)；Both use File class and handle file paths
- 行为差异: Function A is an event handler processing multiple commands and updating UI preferences; Function B is a utility for copying files/directories recursively；Function A has complex UI logic with several conditional branches; Function B is a straightforward recursive copy with no UI interaction；Function A uses JFileChooser, Suku controller, and other GUI components; Function B only uses standard Java I/O (File, FileChannel)；Function A may trigger restart prompts and other dialogs; Function B silently copies files and throws Exception
- 修正建议: Improve model's ability to distinguish between UI event handlers and utility functions by incorporating more structural or data-flow analysis；Enhance training data with more diverse examples of UI- versus I/O-centric functions；Use cross-file context or method-level dependency graphs to better capture semantics

### case_id=5298 FP boilerplate_overlap

- 方法: `sendPost` vs `readVersion`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Sends an HTTP POST request with parameters and returns the response body as a string.
- B 摘要: Reads version, revision, and date from a properties file on the classpath and sets corresponding instance variables.
- 静态失败原因: The model likely overemphasized the lexical and structural overlap of the common I/O pattern (URL opening, BufferedReader loop, try-catch-finally) and ignored the different APIs and purpose.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB considers these non-clones because the core functionality differs significantly (HTTP client vs resource file parser), despite sharing boilerplate I/O code.
- 共享行为: Both open a URL and read content line by line using BufferedReader and InputStreamReader.；Both close the reader in a finally block to ensure resource release.
- 行为差异: A uses HttpURLConnection for HTTP POST; B uses ClassLoader.getSystemResource to read a local resource.；A returns the concatenated response string; B sets instance variables and returns void.；A writes request parameters; B only reads and parses specific key-value pairs.；A handles exceptions by calling MsgPrint.showMsg; B prints stack trace and has a finally block.
- 修正建议: Incorporate API-level features (e.g., HttpURLConnection vs ClassLoader) to distinguish similar I/O patterns.；Use data flow analysis to track how read data is used (returned vs assigned to fields).；Include method name and return type as explicit features.

### case_id=5299 FP boilerplate_overlap

- 方法: `getUser` vs `postData`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.98`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Retrieves a user from a DAO or parses a configuration file to create and save a user object.
- B 摘要: Posts data to a specified URL using HTTP POST with configurable protocol, host, and form parameters.
- 静态失败原因: Static BERT likely relied on overlapping tokens like 'URL', 'BufferedReader', 'openConnection', and 'getInputStream' while ignoring the distinct control flows and overall semantics.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically marks non-clones when functions have different core purposes, even with some lexical overlap; these functions perform completely unrelated tasks (user retrieval vs HTTP POST).
- 共享行为: Both use URL and BufferedReader for I/O operations.；Both involve reading from a network resource.
- 行为差异: Function A loads a user by login; Function B posts data to a URL.；Function A returns a User object; Function B returns void.；Function A includes parsing of a configuration file; Function B sends data and reads response.；Function A handles exceptions by printing stack trace; Function B declares throws Exception.
- 修正建议: Incorporate structural features capturing control flow and data dependencies.；Add attention to return types and method signatures.；Use training data that distinguishes between common library usage and actual semantic equivalence.

### case_id=5300 FN partial_functionality

- 方法: `fileDownload` vs `getXML`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a file from a URL and writes it to a local file (download.pdf) using byte reading.
- B 摘要: Sends HTTP request to a servlet URL, reads response lines, and returns the concatenated string.
- 静态失败原因: Static BERT models (like CodeBERT) rely on token-level representations and may focus on lexical overlap (low Jaccard) and different API calls (FileOutputStream vs. StringBuffer), missing the higher-level semantic similarity in URL reading.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often considers functions that download or fetch content from URLs as clones under Type-4 (semantic) because they share the core behavior of reading from a URL, even if output handling differs.
- 共享行为: Both open a URL connection and read input from it；Both handle I/O exceptions；Both close the input stream
- 行为差异: Function A writes bytes to a file, while Function B returns a string；Function A uses fixed filename, Function B flexible；Function A uses BufferedReader and FileOutputStream, Function B uses URL.openStream() and StringBuffer；Function A reads by bytes, Function B reads by lines
- 修正建议: Use data-flow analysis to track that both functions open a URL and read input；Incorporate type-level reasoning to recognize common patterns；Enhance with task embeddings that capture 'download' vs 'fetch' as similar

### case_id=5301 FN partial_functionality

- 方法: `getFile` vs `getZipAsFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies its XML to update an endpoint location, and saves it to a temporary directory.
- B 摘要: Extracts a file from a DigitalObject's content (likely a zip) and writes it to a temporary directory.
- 静态失败原因: Static BERT models rely on token-level similarity and local syntactic patterns; the low Jaccard similarity (0.0889) and domain-specific vocabulary (WSDL, AxisFault vs DigitalObject, FileUtils) cause the model to treat them as unrelated, missing the shared high-level intent of file retrieval and local storage.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely labeled these as clones (Type-4) because both implement the high-level functionality of 'obtain a file from an external source and save it to a local temporary directory,' despite different input/output specifics and processing steps. The broad Type-4 definition accepts partial functional similarity.
- 共享行为: Both functions retrieve a file from a source (network stream or digital object) and write it to a local temporary location.；Both handle I/O exceptions (IOException).；Both use FileOutputStream and write streams to file.
- 行为差异: Function A downloads from a specific URL and performs XML parsing and modification; function B extracts from a DigitalObject without XML processing.；Function A returns a String (file path); function B returns a File object.；Function A includes specific error handling for AxisFault; function B uses generic printStackTrace.；Function A checks for file existence and re-downloads only if not present; function B always creates a new file.
- 修正建议: Use graph-based or data-flow models that capture the sequence of I/O operations (open stream, write to file, close).；Incorporate structural information about resource handling and temporary file creation.；Augment training data with semantically similar pairs that have low token overlap but share high-level intent.

### case_id=5302 FN partial_functionality

- 方法: `File2String` vs `doVersionCheck`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a file from disk or classpath, concatenates all lines into a single string, and returns it; exits on error.
- B 摘要: Fetches a version file from a URL, parses version and build numbers, and shows a dialog if a newer version is available.
- 静态失败原因: Low token Jaccard (0.2159) and divergent semantics after the read loop; the model likely focused on the different overall purpose and error handling.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider this clone due to the shared pattern of reading text from a stream line-by-line, which is a common idiom, even though the surrounding logic differs.
- 共享行为: Open an InputStream；Wrap in BufferedReader and read lines until null；Close the stream；Catch IOException
- 行为差异: Input source: local file vs URL；Processing of lines: concatenation vs parsing；Output: return string vs UI feedback；Error handling: system exit vs GUI error message
- 修正建议: Train model to recognize common subroutines across different applications；Use graph-based representations to capture data flow and control flow patterns

### case_id=5303 FN partial_functionality

- 方法: `getFile` vs `download`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, optionally modifies its endpoint, and saves to a temporary file, returning the file path.
- B 摘要: Downloads a resource file from the classpath and saves it to a user-selected file path via a save dialog, without returning anything.
- 静态失败原因: Low lexical overlap (token Jaccard 0.0895) and length disparity caused the static model to miss the high-level semantic similarity of 'download file' due to different API usage and control flow patterns.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB tends to consider functions as clones if they share a core functionality (downloading a file to local storage) despite differences in source, processing, and error handling, which aligns with Type-3/Type-4 clone categorization.
- 共享行为: Both download a file from a remote source and write it to the local file system using stream I/O；Both close input and output streams after use；Both handle exceptions during I/O operations
- 行为差异: Function A gets input from a URL and can modify XML content, while Function B gets input from the classpath and does not modify content；Function A uses NIO channels and direct buffer transfer, while Function B uses IOUtils.copy；Function A returns the file path, while Function B is void and shows a save dialog；Function A throws AxisFault on error, while Function B shows an exception dialog
- 修正建议: Include more diverse training examples of file download functions with varying sources (URL, classpath) and processing steps；Use contrastive learning to emphasize shared I/O patterns；Incorporate data flow analysis to detect read-write sequences

### case_id=5304 FN boilerplate_overlap

- 方法: `readGeoParserResult` vs `run`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads XML content from a URL, parses it with retries, and returns a collection of place name entries with associated gazetteer IDs.
- B 摘要: Fetches a URL, reads lines sequentially, sets version and url fields from first two lines, accumulates rest into an information string, then notifies listeners; handles IO exceptions.
- 静态失败原因: Static BERT likely correctly identified the functions as semantically distinct, but BCB's broader clone definition may have favored boilerplate overlap; the model failed to align with BCB's lenient criteria.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may have considered both functions as 'network I/O with text processing', but this interpretation is too broad and overlooks fundamental differences in data transformation and control flow.
- 共享行为: Opens a URL and reads lines using BufferedReader；Handles IOException with exception handling；Uses try-catch-finally structure
- 行为差异: A returns a structured collection; B sets instance fields and notifies listeners；A performs XML parsing with DocumentHelper; B does simple line parsing with switch；A includes retry logic and a testing branch; B does not；A handles multiple element types and builds tuples; B only reads and accumulates lines
- 修正建议: Increase weight on structural and semantic differences；Incorporate control-flow and data-flow analysis to distinguish different output behaviors；Use finer-grained functional similarity measures

### case_id=5305 FN benchmark_preference_bias

- 方法: `getResourceAsStream` vs `readAndRewrite`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.2`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Reads a resource from a URL, optionally caches it locally, and returns an InputStream to the resource, handling HTTP connections and caching.
- B 摘要: Reads a DICOM file, parses its header, reads pixel data, and writes the dataset to an output file using DICOM libraries.
- 静态失败原因: Static BERT/GraphCodeBERT likely correctly identified the low lexical and semantic similarity given the very different domain-specific operations and low token overlap.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as a clone based on a high-level interpretation that both functions 'read input and write output' with similar error handling and progress printing, potentially ignoring domain-specific differences as partial functionality similarity.
- 共享行为: Both perform file I/O operations using buffered streams；Both print progress messages to System.out；Both handle input and output streams
- 行为差异: A involves HTTP connections and caching; B uses DICOM-specific libraries；A returns an InputStream; B is void；A has caching logic; B does not；A uses a byte-by-byte copy loop; B uses library methods for pixel data reading/writing
- 修正建议: Incorporate domain-specific knowledge or API embeddings to distinguish different domains；Use fine-grained semantic analysis to capture exact functional equivalence；Adjust Type-4 clone detection threshold to require stronger semantic alignment

### case_id=5306 FP lexical_or_api_overlap

- 方法: `generate` vs `perform`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.98`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Generates a UUID-like string using MD5 hash of host, time, and random long.
- B 摘要: Performs a Struts action to classify a concept, including session checks, parameter handling, HTTP communication, and XML parsing.
- 静态失败原因: False positive likely due to lexical overlap of common API usage (StringBuffer, try-catch, loops) and the presence of a similar code pattern (digest update, byte processing) but without semantic alignment.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clones due to completely different functionality and minimal structural similarity.
- 行为差异: Function A generates a short random identifier; Function B handles a multi-step web request with business logic.；Function A uses MD5 and simple string formatting; Function B uses HTTP connections, XML parsing, and session management.；Function A returns a formatted UUID string; Function B returns an ActionForward based on processing status.；Function A is static and standalone; Function B is an instance method with dependencies on request/response objects.
- 修正建议: Improve model's ability to distinguish boilerplate code from actual logic.；Incorporate dataflow analysis to capture vastly different control flow and data dependencies.；Use function renaming or abstraction to reduce reliance on superficial token matches.

### case_id=5307 FN lexical_or_api_overlap

- 方法: `runScript` vs `seeURLConnection`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a script from a URL constructed from codebase, byte by byte, and returns the content as a string.
- B 摘要: Reads content from a fixed URL using BufferedReader, builds a string, and logs it.
- 静态失败原因: Low token overlap and different API usage (InputStream vs Reader) cause the model to miss the semantic similarity.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB sees both as performing the core task of fetching data from a URL and accumulating it into a string, despite differences in return type and reading style.
- 共享行为: Both open a URL and read its content into a string
- 行为差异: Different return types (String vs void)；Different exception handling (caught vs thrown)；Different reading mechanisms (byte-by-byte vs line-by-line)；Different URL sources (parameter vs hardcoded)
- 修正建议: Use graph-based representations to capture common patterns like URL reading loops；Incorporate data flow to detect read-all behavior

### case_id=5308 FN partial_functionality

- 方法: `getFile` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies the endpoint address in the XML, and saves to a temp directory.
- B 摘要: Copies a file from source to destination using a buffer, with optional overwrite.
- 静态失败原因: Low token overlap (0.176) and different method names led the model to predict non-clone. Long-range dependencies and nested logic in A may not be captured well by static BERT, which struggles with structural patterns across different contexts.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: None
- 共享行为: Both read from an input stream and write to an output stream to transfer data.；Both handle file I/O and ensure streams are closed.
- 行为差异: A involves network download, XML parsing and modification, and multiple file operations; B is a simple file copy.；A checks length and existence of file before copying; B checks destination existence and force flag.；A uses channel transfer and additional renaming; B uses byte buffer loop.
- 修正建议: Enhance model with data flow analysis to identify common I/O patterns.；Use contrastive learning on core functional subroutines across different implementations.；Incorporate structural similarity beyond token overlap, e.g., graph-based representations of API calls.

### case_id=5309 FN benchmark_preference_bias

- 方法: `testReadPerMemberSixSmall` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Tests reading six small GZIP members sequentially with EOF per member.
- B 摘要: Retrieves a resource as an InputStream by URL, caching it locally.
- 静态失败原因: The static model likely failed due to low lexical overlap and correctly identified them as non-clones under strict semantics, but BCB expects a broader interpretation.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may label this as clone because both involve copying from an input stream to an output stream, a common I/O pattern, but this interpretation is too broad.
- 共享行为: Both copy data from an InputStream to an OutputStream
- 行为差异: A is a test method with assertions and count expectations, B retrieves resources with caching and HTTP handling；A uses GZIPMembersInputStream and NullOutputStream, B uses URLConnection and file streams；A loops over multiple members, B handles a single resource
- 修正建议: Use a more nuanced definition of clone for evaluation；Incorporate broader semantics for I/O patterns without overgeneralization

### case_id=5310 FN benchmark_preference_bias

- 方法: `copy` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Copies a local file to another location using FileChannel transfer.
- B 摘要: Downloads a KMZ file from a URL, extracts zip entries, and saves them to files.
- 静态失败原因: The model correctly identified low token overlap and distinct control flows, but missed the potential for high-level functional similarity considered by BCB annotators.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as a clone focusing on the broad category of 'file copy' operations, ignoring the additional complexity of zip extraction and different sources.
- 共享行为: Both read from a source and write data to files；Both use file output streams
- 行为差异: Different source: local file vs URL；Different operation: direct copy vs zip extraction；Different output: single file vs multiple files；Different error handling and resource management
- 修正建议: Incorporate task-level or domain-specific understanding；Use graph-based representations to capture data flow similarities；Train on BCB-specific annotation guidelines to match human preferences

### case_id=5311 FP lexical_or_api_overlap

- 方法: `readZoneIDs` vs `CheckUrl`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads all lines from a classpath resource file and returns a set of integers parsed from each line.
- B 摘要: Opens a URL connection, reads the first line of the response, and returns it as a string.
- 静态失败原因: Static BERT models may rely on token overlap and structural similarity. Shared tokens like 'URL', 'openStream', 'readLine', 'try', 'catch', 'Exception', and 'printStackTrace' led to a false positive, ignoring differences in output types and input handling.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled non-clones because the functions have different input/output semantics and data types, and the shared structural patterns (URL, reading, try-catch) are not sufficient for functional equivalence even in a broad Type-4 sense.
- 共享行为: Both use URL objects to open connections and read data line-by-line；Both handle exceptions with printStackTrace
- 行为差异: Input type: resource name vs full URL；Output type: HashSet<Integer> vs String；Number of lines read: all vs first only；Parsing: integer parsing vs raw string
- 修正建议: Incorporate type information for output and input；Use dataflow analysis to track how read data is processed；Increase sensitivity to the number of lines read and parsing logic

### case_id=5312 FN partial_functionality

- 方法: `doRawRequest` vs `getEncoding`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends a POST request with given data to a fixed URL and returns the entire response body as a string.
- B 摘要: Opens a URL connection and extracts the character encoding from response headers or body, returning the encoding string or a default.
- 静态失败原因: The static BERT model likely focused on high token overlap (e.g., 'URLConnection', 'BufferedReader', 'readLine', 'IOException') and structural similarity, but missed the semantic divergence in purpose—one performs a generic HTTP POST and returns all content, while the other detects encoding. The model's limited capacity for long-range semantics and lack of data flow understanding led to underestimating the functional difference, causing a false negative.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this as a clone because both functions involve reading from a URL connection line by line, sharing a common structure of opening a connection, reading lines, and handling exceptions. The overall pattern of URL response handling is similar, and the differences in specific processing might be considered as variants of that pattern.
- 共享行为: Both open a URLConnection and obtain an input stream.；Both read from the input stream line by line.；Both close resources (reader/writer) after use.；Both throw IOException.
- 行为差异: A writes POST data to the output stream; B does not write anything.；A returns the full response body; B returns an encoding string.；A uses a fixed URL constant; B uses a member variable url.；B inspects header fields for content-type; A does not.
- 修正建议: Incorporate data flow analysis to distinguish output purpose and side effects.；Use AST-based features to capture method-level structural differences, e.g., presence of write operations vs. only reads.；Train with more diverse examples of similar patterns (e.g., HTTP response processing) with different intents to improve discrimination.；Employ contrastive learning to enhance separation of semantically different pairs.

### case_id=5313 FN partial_functionality

- 方法: `CopyTo` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a file character by character to a destination using FileReader and FileWriter.
- B 摘要: Downloads a KMZ file from a URL, extracts ZIP entries, and writes each entry to a file.
- 静态失败原因: The model likely focused on the different API calls (FileReader vs ZipInputStream, URL) and method names (CopyTo vs main), leading to low token overlap and no semantic match, missing the abstract pattern of copying.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider the core algorithmic behavior (copying data from input to output) as similar enough for a Type-4 clone, focusing on the structural pattern of reading and writing in a loop, ignoring specific types and higher-level functionality.
- 共享行为: Both read from an input source and write to an output file in a loop until end-of-stream
- 行为差异: A uses char-based I/O (Reader/Writer), B uses byte-based I/O (InputStream/OutputStream)；B involves network download and ZIP decompression, A is purely local file copy；B writes to multiple files (ZIP entries), A writes to a single destination
- 修正建议: Incorporate more abstract representation of I/O operations, e.g., data-flow graphs or program slicing to capture read-write patterns.；Use contrastive learning to recognize similar control flow despite different APIs.

### case_id=5314 FP partial_functionality

- 方法: `SRWGuiClient` vs `startScript`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Constructs a browser-like GUI window that loads and displays HTML content from a provided URL, optionally applying XSLT transformation.
- B 摘要: Reads a script from a URL and appends it to a dialog's script buffer, handling I/O errors.
- 静态失败原因: Static BERT models may over-rely on token-level overlap (e.g., 'URL', 'BufferedReader', 'InputStreamReader') and code structure patterns (e.g., try-catch around URL reading), leading to a false positive even though the semantic contexts diverge greatly.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely considers these non-clones because the overall functionality (GUI construction vs script loading) is vastly different, despite a small shared pattern of URL reading. The clone annotation guidelines prioritize overall semantic equivalence.
- 共享行为: Both read from a URL using BufferedReader and InputStreamReader；Both handle IOException
- 行为差异: A creates and configures a complex GUI with many components; B only reads a script and appends to a buffer；A performs XML parsing and optional XSLT transformation; B does not parse XML, just reads lines；A sets up a JEditorPane and scroll pane; B does not involve any UI；A has extensive error handling and error messages; B exits on error
- 修正建议: Train models to better distinguish high-level intent (constructor vs private helper) and to weight overall program functionality more than shared low-level patterns.；Incorporate method-level or class-level context, such as method name and class name, to disambiguate.

### case_id=5315 FP lexical_or_api_overlap

- 方法: `getJSONData` vs `downloadFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches JSON data from a URL and parses it into a JSONObject.
- B 摘要: Downloads a file from a URL to a local destination, reporting progress.
- 静态失败原因: The model may have focused on overlapping tokens like 'url', 'InputStream', 'Buffered', and exception handling, missing the core semantic difference between JSON parsing and file download.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels as non-clones when functions have different return types and perform distinct operations despite sharing some HTTP utility steps.
- 共享行为: Both connect to a URL over HTTP；Both read data from an InputStream；Both handle exceptions
- 行为差异: A returns a JSONObject; B returns a boolean；A parses data as JSON; B writes data to a file；B tracks download progress via MessageFrame; A does not；A uses Apache HttpClient; B uses URLConnection
- 修正建议: Incorporate structural features like return type and output operations；Add contrastive learning examples for functions that share API calls but differ in purpose；Use data flow analysis to track what happens to fetched data

### case_id=5316 FP boilerplate_overlap

- 方法: `main` vs `tail`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Main method for an adapter generator from Prolog files, involving parsing, class generation, and serialization.
- B 摘要: Implementation of a tail command for Hadoop file system, reading last bytes of a file with optional follow mode.
- 静态失败原因: The model likely relied on superficial similarities such as long method bodies, common control flow patterns (try-catch, while loops), and file-related operations, overlooking the domain-specific semantic differences.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would not consider these clones because they implement entirely different functionality from different domains, with no overlap in their core logic despite some structural similarities.
- 共享行为: Both perform file I/O and handle errors with print statements
- 行为差异: Function A generates JAR files from Prolog parsing; Function B reads and outputs file content；Function A has complex multi-step generation pipeline; Function B is a simple file tail operation；Function A uses domain-specific classes (PrologParser, FactVisitor, ClassWriter); Function B uses general FileSystem API
- 修正建议: Incorporate method-level and class-level context embeddings；Use domain-aware tokenization or identifier type information；Train with more negative examples that share structure but differ in semantics

### case_id=5317 FN lexical_or_api_overlap

- 方法: `getHTML` vs `loadExistingAntlibs`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.6`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Gets HTML from a URL using HTTP connection and optionally writes it to a file, returning the content as a string.
- B 摘要: Loads antlib definitions from classpath resources by reading URL streams, parsing package names, and loading each antlib via loadAntLib.
- 静态失败原因: The models rely heavily on lexical and token-level similarity, which is low (Jaccard 0.17). The functions use different domain-specific identifiers (e.g., 'pageURL', 'encoding' vs 'antlib', 'classLoader') and have different control flow structures. The shared abstract pattern of reading lines from a stream is not captured by static embeddings without deeper semantic understanding.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may consider these clones because both functions perform a 'data loading' task: they read lines from a URL/resource stream and process each line. Under a high-level functional similarity of 'input-stream line processing', they could be Type-4 clones with similar algorithmic structure despite different domains.
- 共享行为: Both read lines from an InputStream obtained from a URL；Both use BufferedReader to read lines in a loop；Both handle IOException and have finally block for cleanup
- 行为差异: A downloads external HTML content via HTTP; B loads internal classpath resources；A writes output to file and returns string; B does not return anything but calls loadAntLib for each line；A uses HttpURLConnection; B uses ClassLoader.getResources；A processes lines by appending to StringBuilder; B processes lines as package names for antlib loading
- 修正建议: Improve models to capture abstract control flow patterns like 'while loop reading lines from stream' across different domains；Use dataflow analysis to identify common I/O patterns；Incorporate functional similarity based on high-level task categories

### case_id=5318 FP lexical_or_api_overlap

- 方法: `getUser` vs `startScript`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Loads a user from a DAO or a config file if not found, then returns the user.
- B 摘要: Reads a script from a URL and appends it to a dialog, then ends the script.
- 静态失败原因: The static model likely overemphasized the lexical overlap of common I/O structures (BufferedReader, InputStreamReader, openStream, readLine) and missed the semantic gap due to different method names, return types, and overall purpose.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels pairs with distinct overall functionality as non-clones despite shared low-level I/O patterns. The functional intent is too different.
- 共享行为: Both use BufferedReader and InputStreamReader to read from a URL/stream.；Both have exception handling and read line by line.
- 行为差异: Function A deals with user authentication and persistence; Function B deals with script loading for a dialog.；Different return types and inputs: A returns User; B returns void and takes Attributes.；Error handling differs: A prints stack trace; B prints IO error and exits.；Function A may save data to a DAO; Function B only reads and appends.
- 修正建议: Incorporate method names and signatures as additional features.；Use data flow analysis to distinguish reading for different outcomes.；Train on more diverse examples where I/O patterns appear in different contexts.

### case_id=5319 FP boilerplate_overlap

- 方法: `getURLContent` vs `getFrameworkFactory`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Opens a URL connection, reads its content line by line, and returns the full text as a String.
- B 摘要: Loads an OSGi service descriptor from classpath, reads lines to find a class name, and returns a FrameworkFactory instance via reflection.
- 静态失败原因: The static model (e.g., CodeBERT) may over-rely on token overlap (URL, BufferedReader, readLine, try, finally, close) and structural similarity, missing the distinct high-level semantics (fetching web content vs. loading OSGi service).
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely considers these non-clones because they have different purposes and return types; the I/O pattern is common boilerplate but does not define functional equivalence.
- 共享行为: Both open a URL and read lines using BufferedReader；Both use try-finally to close the reader；Both perform I/O on a URL resource
- 行为差异: A returns entire content as String; B returns a FrameworkFactory object by loading a service class；A takes a URL string as input; B uses classloader to get a resource from classpath；A appends newlines to the output; B does not；B parses lines to find a class name and instantiates it via reflection; A simply accumulates text
- 修正建议: Enhance model to distinguish between different API usage patterns (e.g., URL.openStream vs URLConnection)；Incorporate return type and method signature information to differentiate functionality；Use dataflow analysis to understand the transformation of data (gathering text vs. instantiating object)

### case_id=5320 FN benchmark_preference_bias

- 方法: `main` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.85`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Main method that parses command-line flags, optionally loads or creates an Experiment object, displays a GUI, waits, saves the experiment if requested, and exits.
- B 摘要: Launch method that processes Maven POM files, configures Hibernate dialect, and sets up a NexOpen project build environment.
- 静态失败原因: Static BERT/GraphCodeBERT correctly predicted non-clone because the code structures and API usage, despite some superficial overlap, differ significantly in logic and purpose. The model was not misled by lexical similarities.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might have labeled these as clones due to shared use of file I/O, anonymous classes, and similar structural patterns (e.g., reading/writing objects or files), but the overall semantics are completely different.
- 共享行为: Both methods handle exceptions with try-catch blocks.；Both perform file I/O operations.；Both use anonymous inner classes for event handling or callbacks.
- 行为差异: Function A is a GUI application entry point for a machine learning experiment framework.；Function B is an Eclipse plugin launch configuration handler for a Maven-based project.；Function A uses serialization (ObjectInputStream/OutputStream) while B uses XML processing and file resource management.；Function A includes threading (sleep) and GUI lifecycle; B includes project building and profile management.
- 修正建议: Review BCB annotation guidelines to avoid labeling non-clones based on low-level API similarity alone.；Use semantic or functional similarity measures that consider domain and purpose.

### case_id=5321 FN partial_functionality

- 方法: `sendExceptionToServer` vs `callService`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.65`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends exception details to a server via HTTP POST and prints success/failure.
- B 摘要: Calls a generic service via HTTP GET and stores the response in a variable.
- 静态失败原因: Low token Jaccard similarity (0.206) and different method names, parameters, and internal logic (POST vs GET) caused the model to focus on the differences rather than the overarching similar pattern of HTTP request with response reading.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider these clones because both are network I/O functions with similar structure (URL construction, buffer reading, exception handling), sharing the concept of making an HTTP request and processing the response.
- 共享行为: Both perform HTTP requests；Both read response from server；Both handle IOException
- 行为差异: HTTP method: POST vs GET；Purpose: exception reporting vs generic service call；Result handling: prints vs stores in variable
- 修正建议: Use data augmentation to include more diverse HTTP request functions as clones；Incorporate method-level context (class name, surrounding methods) to understand purpose；Use contrastive learning to focus on structural similarities

### case_id=5322 FN partial_functionality

- 方法: `getFile` vs `copyFromFileToFileUsingNIO`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL using NIO, modifies XML content, and saves to a local temp file.
- B 摘要: Copies a local file to another file using NIO transfer.
- 静态失败原因: The low token Jaccard (0.14) and surface-level differences in method signatures, extra logic, and exception handling likely misled the model, preventing it from recognizing the shared NIO transfer pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely judged them as clones because both implement a file copy using NIO channels, which is a shared functional pattern, despite the additional operations in function A.
- 共享行为: Both use Java NIO channels to transfer bytes from an input source to an output file.
- 行为差异: Function A involves URL connection, downloading, XML parsing, and attribute modification; Function B is a simple file copy.；Function A handles multiple exceptions and logging; Function B only throws exceptions.
- 修正建议: Enhance representation to capture data flow and structural similarities like NIO channel usage.；Incorporate AST-based features to highlight similar loop/transfer patterns.；Use contrastive learning on pairs with partial functional overlap.

### case_id=5323 FP lexical_or_api_overlap

- 方法: `readRemoteFile` vs `getLinksFromURLFast`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a remote file line by line and concatenates into a single string.
- B 摘要: Fetches a URL, parses HTML for anchor links and text, returns two vectors of links and texts.
- 静态失败原因: The model may have been misled by lexical overlap (e.g., URL, BufferedReader, readLine) and the general pattern of reading from a URL, failing to capture the distinct post-processing and output structures.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels as non-clone because the core functionality differs significantly: one is a simple file reader, the other is an HTML link extractor. Despite common URL-reading steps, the outputs and algorithms are distinct.
- 共享行为: Both open a URL and read input using BufferedReader
- 行为差异: Function A returns a concatenated string of all lines; Function B returns vectors of parsed links and texts.；Function B uses regular expressions to extract anchor tags and resolve absolute URLs; Function A has no parsing logic.；Function B includes timing/debug output; Function A catches EOFException and prints IO errors.；Function B is static and takes a URL string; Function A is non-static and uses a fixed remote file URL.
- 修正建议: Incorporate structural features like control flow and data flow.；Use a model sensitive to semantic purpose beyond token overlap.；Add negative examples with high API overlap but different functionality during training.

### case_id=5324 FN partial_functionality

- 方法: `runScript` vs `doVersionCheck`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.4`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a script file from the codebase URL and returns its content as a string, returning 'error!' on failure.
- B 摘要: Fetches version information from a remote URL, parses build versions, and calls another method to perform version check, with UI feedback.
- 静态失败原因: The low token overlap and different method names/signatures likely led the model to predict non-clone, missing the broad URL-reading pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB might consider them clones due to the shared pattern of opening a URL and reading input, but the overall functionality is quite different, making this a borderline case.
- 共享行为: Both open a URL and read data from an InputStream.；Both handle exceptions (though differently).
- 行为差异: A returns the entire content as a string; B parses specific lines for version info and calls another method.；A has no UI side effects; B shows and hides a wait cursor and displays error dialogs.；A is an instance method; B is a static method.；A catches generic Exception; B catches IOException.
- 修正建议: Incorporate higher-level semantic patterns like URL opening combined with data processing.；Use graph-based representations that capture control and data flow to identify common subroutines.

### case_id=5325 FN partial_functionality

- 方法: `createFile` vs `doGet`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Copies a file to a named resource using InputStream and OutputStream, handling ResourceManagerException.
- B 摘要: Handles HTTP GET request by retrieving a page, checking permissions, logging, and rendering, with optional caching to a temp file.
- 静态失败原因: The static BERT model likely correctly identified the semantic mismatch but the BCB label is anomalous; the model may have missed the limited file-writing overlap that BCB considered.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled these as clones based on the presence of file writing and exception handling, accepting broad Type-4 similarity despite different overall functionality.
- 共享行为: Both perform file output operations.；Both catch and log exceptions.；Both use try-catch-finally pattern for stream handling.
- 行为差异: Function A is a simple file copy; Function B is a complex servlet with conditional logic.；Function A has no web-related logic; Function B handles HTTP requests, user permissions, and page rendering.；Function B includes logging and caching; Function A does not.
- 修正建议: Improve detection of partial functionality clones by focusing on common local patterns.；Use hierarchical or multi-level analysis to capture both global semantics and local behavior.

### case_id=5326 FN partial_functionality

- 方法: `copyResource` vs `createOutputStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource from a URL or file to a destination file byte-by-byte.
- B 摘要: Creates a BufferedWriter for writing to a zip file, reading from a zip input and skipping all entries except the final content.xml.
- 静态失败原因: Static BERT likely relied on token overlap (low Jaccard) and structural patterns; the functions have different APIs, method names, and control flow, obscuring the abstract copy similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as 'copying resources' because they share high-level I/O copy behavior, despite different implementations and contexts.
- 共享行为: Both read from an input source and write to an output stream；Both use buffered I/O (byte vs char)；Both handle exceptions
- 行为差异: A copies any resource; B specifically processes zip files with entry management；A writes to a raw FileOutputStream; B writes to a ZipOutputStream；A reads byte-by-byte; B reads char buffers；A closes streams; B returns an open BufferedWriter
- 修正建议: Train with more diverse I/O copy patterns；Incorporate abstract semantic features like 'input-to-output transfer'；Use data augmentation with wrapped I/O operations

### case_id=5327 FN partial_functionality

- 方法: `copyResource` vs `copy`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource (URL or file) to a destination file using single-byte streaming.
- B 摘要: Copies a file to another file using a buffered byte array.
- 静态失败原因: Low token Jaccard (0.2778), different method names, control flow (URL check vs direct file), and single-byte vs buffered read reduce surface similarity, causing the model to miss semantic equivalence.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often considers file copy utilities as clones despite differences in source type or buffer size, focusing on the core copying functionality.
- 共享行为: Both copy data from a source to a destination file；Both use FileInputStream and FileOutputStream；Both close streams in finally block equivalent；Both throw exceptions on missing source
- 行为差异: Source can be URL or file in A, only file in B；A reads byte-by-byte, B uses 1024-byte buffer；A has conditional source resolution, B directly uses file path；Error messages differ
- 修正建议: Enhance model with dataflow information to capture IO patterns；Use API sequence embeddings focusing on common read-write-close pattern；Include more structural alignment for loops with different read strategies

### case_id=5328 FN benchmark_preference_bias

- 方法: `internalCopy` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: InternalCopy copies a single file byte-by-byte from source to destination, skipping Thumbs.db.
- B 摘要: BuildSiteForEdit processes a whole site by iterating over pages, performing XML transformations, and writing multiple output files.
- 静态失败原因: Static model correctly predicted non-clone due to low lexical overlap (Jaccard 0.0679) and dramatically different semantics.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider both as involving file I/O with a similar buffer pattern, but the functional difference is too large for a Type-4 clone.
- 共享行为: Both use a buffer of size 8192 for I/O operations.；Both write data to output files.
- 行为差异: A is a simple file copy; B is a complex multi-file site generation with XML parsing and transformation.；A handles a single file; B loops over many pages and performs numerous operations per page.；A has no error handling beyond exceptions; B includes extensive debugging, property handling, and exception types.；A works with raw bytes; B works with characters and strings.
- 修正建议: Ensure BCB annotations consistently require meaningful functional similarity beyond trivial I/O patterns.；Re-evaluate this pair's clone label in the benchmark.

### case_id=5329 FP long_range_semantics

- 方法: `perform` vs `getRandomGUID`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `1.0`
- 推荐路线: `static_summary_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Processes an HTTP request to classify a concept by building XML data, sending it to a URL, parsing the result, and storing it in the session, then forwarding to a JSP.
- B 摘要: Generates a random GUID using MD5 hash of system time, random number, and a static identifier.
- 静态失败原因: Static BERT/GraphCodeBERT may have overfitted on trivial code fragments like try-catch blocks, StringBuffer usage, and Java syntax, ignoring the high-level semantics. The model might have been misled by the presence of common Java idioms and control structures, failing to capture the domain-specific goal of each method.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely labels these as non-clones because they have fundamentally different purposes (Struts action vs. GUID generation) and no overlap in functionality or output.
- 共享行为: Both use StringBuffer for string building；Both handle exceptions with try-catch
- 行为差异: Function A performs HTTP communication and session management; Function B does not；Function A processes user input and classification logic; Function B generates a random identifier；Function A interacts with external URL and parses XML; Function B computes MD5 hash locally；Function A sets session attributes and forwards to JSP; Function B only assigns to instance variables
- 修正建议: Improve model training with more diverse examples of methods with similar lengths but different purposes.；Incorporate dataflow analysis to understand the input-output behavior.；Use function call graphs to recognize framework-specific patterns.；Train with contrastive examples of non-clones that share boilerplate code but differ in core logic.

### case_id=5330 FN benchmark_preference_bias

- 方法: `doGet` vs `copy`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Handles HTTP GET requests for a page, retrieves page by ID or name, checks visibility, renders page, and optionally caches output to a temporary file.
- B 摘要: Copies a file from source path to destination path using NIO channels and memory-mapped buffers.
- 静态失败原因: The functions have very low token overlap and are from different domains (web vs file I/O). The static model correctly predicted non-clone because they share few tokens; the BCB label is likely incorrect.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider them clones because both perform some form of data copying (A caches page output to a file, B copies a file) and both involve file I/O, but this is extremely weak and likely a misannotation.
- 共享行为: both involve reading a source and writing to a destination；both use file I/O operations
- 行为差异: A is a complex web request handler with many branches (page lookup, permissions, caching); B is a simple static file copy；A uses multiple libraries (HttpServletRequest, Page, Property, MBeans); B uses only java.io and java.nio；A writes to a specific temporary file if conditions met; B writes to a specified destination
- 修正建议: Re-evaluate BCB annotation for this pair; it should likely be non-clone.

### case_id=5331 FP lexical_or_api_overlap

- 方法: `main` vs `hyperlinkUpdate`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Generates adapter classes from a Prolog file and writes them to a JAR file.
- B 摘要: Handles hyperlink activation in a GUI by opening the URL, reading its content, and displaying it in a dialog.
- 静态失败原因: Static BERT/GraphCodeBERT likely relied on overlapping tokens such as 'URL', 'IOException', 'try', 'stream', 'close', leading to false positive due to lexical and API usage similarity.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels this as non-clone because the two functions have entirely different business logic and outputs, despite some superficial API overlap.
- 共享行为: Both use try-catch blocks to handle IOException.；Both use URL and I/O streams to read data.；Both call stream.close() in a finally block.
- 行为差异: Function A is a command-line main method that generates JAR files; Function B is a GUI event handler that displays web content.；Function A involves complex class generation and file writing; Function B only reads and displays content.；Function A uses multiple external libraries (e.g., ClassWriter, ObjectOutputStream); Function B uses Swing components.
- 修正建议: Incorporate dataflow or control flow graphs to capture semantic differences.；Use models that differentiate between command-line and GUI contexts.；Add more negative examples of similar API usage but different semantics.

### case_id=5332 FP lexical_or_api_overlap

- 方法: `handleHandshake` vs `run`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Handles Minecraft handshake by validating username and performing HTTP authentication via session.minecraft.net.
- B 摘要: Loads a vector tile from a URL (file or HTTP), parses GeoJSON, constructs geometries, and adds them to a data loader.
- 静态失败原因: Static models may overweigh lexical and structural overlap in common API usage (URL, BufferedReader, try-catch) and miss the semantic difference in domain and overall functionality.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB annotators consider these non-clones because they perform fundamentally different tasks with distinct logic and outputs, despite sharing some IO boilerplate.
- 共享行为: Both use URL and BufferedReader to read from an input stream；Both handle IO exceptions
- 行为差异: Different overall purpose: handshake vs tile loading；Different data processing: string validation vs GeoJSON parsing and geometry creation；Different output: network packet vs geometry collection addition
- 修正建议: Train on examples emphasizing task-level semantics over API sequences；Use contrastive learning with diverse negative pairs sharing boilerplate；Incorporate data flow or dependency analysis to distinguish core logic from scaffolding

### case_id=5333 FN partial_functionality

- 方法: `copyResource` vs `copy`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource (URL or local file) to a destination file by reading bytes one-by-one and writing them.
- B 摘要: Copies a file or directory from a Hadoop FileSystem to a local file, with optional deletion and recursive directory handling.
- 静态失败原因: Static BERT models rely on token and structural similarity; the low Jaccard similarity (0.118) and different control flow caused the model to miss the functional overlap.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels broad Type-4 clones where functions share the same high-level purpose (copying) despite different implementations and additional features.
- 共享行为: Both read bytes from a source and write them to a file output stream；Both open input and output streams, and close them after operation；Both handle exceptions during copying
- 行为差异: copyResource handles URL and local file; copy handles Hadoop FileSystem paths；copyResource copies a single file; copy copies directories recursively；copy has an option to delete the source after copying；copy uses IOUtils.copyBytes; copyResource uses a manual byte loop
- 修正建议: Incorporate data flow analysis to detect shared I/O operations；Use code summarization or documentation to capture intent；Train with contrastive learning on function purpose rather than surface form

### case_id=5334 FN partial_functionality

- 方法: `copyResource` vs `readAndRewrite`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.75`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource from a URL or local file to a destination file by reading and writing bytes.
- B 摘要: Reads a DICOM file, parses it, and rewrites the pixel data to an output file.
- 静态失败原因: Static BERT models rely heavily on lexical and syntactic overlap (token Jaccard 0.1), missing the abstract functional similarity in data transfer.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider these Type-4 clones because both functions perform the high-level task of copying data from an input to an output, despite different domains and implementations.
- 共享行为: Read data from an input source；Write data to an output file；Handle input/output streams
- 行为差异: Function A copies raw bytes; function B processes DICOM metadata and pixel data；Function A uses generic InputStream/OutputStream; function B uses DICOM-specific APIs；Function B includes debugging print statements; function A does not；Function B handles chunked pixel data; function A does a simple byte-by-byte copy
- 修正建议: Incorporate dataflow or control flow abstractions；Use code summarization or function name embedding to capture high-level intent；Train on functional clone detection with abstract semantics

### case_id=5335 FP other

- 方法: `actionPerformed` vs `patch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.2`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Handles GUI actions for setting file paths and preferences, including GRAPHVIZ, IMAGEMAGICK, and other settings.
- B 摘要: Creates a backup of the Minecraft jar file and opens it for patching if mods are present.
- 静态失败原因: The static model likely predicted clone due to over-reliance on shallow API matches like FileInputStream and File, and possibly was misled by the truncated and long code of function A, missing its high-level GUI semantics.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB labels non-clone because the functions have entirely different purposes and no semantic overlap beyond superficial file I/O.
- 共享行为: Both involve file I/O operations
- 行为差异: A is an event handler for multiple GUI commands; B is a standalone method for patching.；A modifies GUI components and updates preferences; B does not interact with GUI.；A uses JFileChooser for file selection; B uses hardcoded paths.；A handles many different actions; B handles only one action (patch).
- 修正建议: Improve model's ability to capture overall program purpose, not just local API patterns.；Use longer context or hierarchical representations to distinguish GUI event handling from file patching.；Incorporate domain-specific features or pre-training on diverse Java methods.

### case_id=5336 FN benchmark_preference_bias

- 方法: `process` vs `modifyApplicationMessage`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Processes a template (Freemarker, XSLT, or copy) to generate an output file at a computed destination path with directory creation and error handling.
- B 摘要: Modifies or adds a key-value pair to a locale-specific properties file for internationalization, copying from an English file if needed.
- 静态失败原因: Static BERT correctly identified low token similarity (Jaccard=0.12) and distinct APIs, so it predicted non-clone. The 'failure' is that it disagreed with the BCB annotation, which may be erroneous or too liberal.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may label this as a clone due to shared high-level structure of file processing and output generation, but this is overly broad and not typical for BCB's usual Type-3/Type-4 criteria.
- 共享行为: Both perform file I/O operations (read/write) and handle exceptions.；Both use conditional logic and loops.；Both involve writing output to files based on input parameters.
- 行为差异: A handles multiple template engines (Freemarker, XSLT, copy) with complex processing; B only modifies properties files.；A computes destination path based on template attributes and package name; B computes path based on locale and fixed resource path.；A uses a Document model and xsltParam for transformation; B uses simple string replacement for message key-value pairs.；A has custom exception types; B uses generic Exception.
- 修正建议: Re-evaluate BCB annotation for this pair; consider removing if not functionally similar.；Use semantic or dataflow analysis to capture intended functionality beyond API sequences.；Ensure annotation guidelines emphasize functional equivalence over superficial file I/O patterns.

### case_id=5337 FP partial_functionality

- 方法: `executePost` vs `getXML`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends an HTTP POST request with URL parameters and returns the response body as a string.
- B 摘要: Sends an HTTP GET request to a URL with a query parameter and returns the response body as a string.
- 静态失败原因: The model may have focused on similar boilerplate code (URL, BufferedReader, readLine) and missed the key difference in HTTP method and data transmission.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely considered these non-clones because the HTTP method and request construction are fundamentally different, despite both fetching data.
- 共享行为: Both establish an HTTP connection；Both read the response line by line；Both return the concatenated response as a string
- 行为差异: HTTP method: POST vs GET；Request data: written in body vs appended to URL；Header setting: explicit vs none
- 修正建议: Train on more diverse examples of HTTP requests to distinguish POST from GET；Incorporate control flow and method call differences

### case_id=5338 FP long_range_semantics

- 方法: `actionPerformed` vs `descargarArchivo`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `static_summary_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Handles UI events to set various application preferences using file choosers and updates UI components.
- B 摘要: Copies a file from one location to another using file channels.
- 静态失败原因: The model likely failed due to long-range semantics: function A is very long and its overall intent is obscured, leading the model to focus on superficial similarities (e.g., presence of file-related classes) rather than the core behavior.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB labels this as non-clone because the functions have completely different purposes and functionalities, with no meaningful semantic overlap.
- 共享行为: Both involve file-related operations, but at different abstraction levels (file selection vs. file copying).
- 行为差异: Function A is an event handler for configuration changes; Function B is a utility for file copying.；Function A is long and complex with multiple branches; Function B is short and straightforward.；Function A interacts with UI components and preferences; Function B has no UI interaction.；Function A uses JFileChooser for user interaction; Function B directly reads and writes files.
- 修正建议: Improve long-range dependency modeling in the static analysis.；Incorporate function-level summarization or code structure awareness.；Use hierarchical representations to capture high-level semantics.

### case_id=5339 FN partial_functionality

- 方法: `runScript` vs `handler`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.4`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a script file from the applet's codebase URL, reads all bytes sequentially, and returns the content as a string; returns 'error!' on exception.
- B 摘要: Reads a web page from a given URL line by line, searches for a specific substring using target.getInclude() and extracts a substring based on delimiters, then updates a map entry; catches exceptions silently.
- 静态失败原因: Static models like GraphCodeBERT focus on lexical tokens and control flow; the low token similarity (0.19) likely led to a non-clone prediction. The model may require more explicit structural alignment, which is lacking here. The partial functionality overlap is subtle and not captured by surface-level features.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as implementing a 'URL reading and processing' task, a common high-level pattern. However, the specific processing differs greatly, and the low token similarity suggests they are not syntactically similar. Possibly the annotator considered them Type-4 clones due to the shared high-level concept of fetching a resource from a URL.
- 共享行为: Both open a URL, read input stream data, and handle I/O exceptions.
- 行为差异: Function A reads raw bytes, returns entire content; Function B reads lines, performs pattern extraction, modifies a map, and does not return anything.；Different loop structures: A uses a do-while byte-by-byte; B uses while readLine.；Different exception handling: A catches generic Exception and returns error string; B catches specific exceptions and does nothing.；Function A's input is a script name; B's input is a map and a TargetPage object.
- 修正建议: Use dataflow analysis to capture the broader pattern of URL I/O.；Incorporate task-level abstraction or semantic role labeling.；Use a model that can recognize high-level functionality even if implementation differs.

### case_id=5340 FN benchmark_preference_bias

- 方法: `unzipModel` vs `doGet`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.1`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Unzips a zip file to a specified temporary directory.
- B 摘要: Handles an HTTP GET request to retrieve and serve a web page, with caching and access control.
- 静态失败原因: Static embeddings likely captured low token-level similarity (Jaccard 0.09) and different API usage, leading to a correct non-clone prediction; the BCB label appears to be a false positive.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this pair as clone due to both using file I/O, try-catch blocks, and similar token patterns like 'FileOutputStream', 'BufferedOutputStream', but this is a weak and likely erroneous annotation.
- 行为差异: Different input/output: A reads a zip file and writes files; B reads HTTP request and writes HTTP response.；Different control flow: A loops over zip entries; B has conditional page retrieval and permission checks.；Different exception handling: A throws EDITSException; B throws ServletException and IOException.
- 修正建议: Re-examine BCB ground truth for this pair; consider relabeling as non-clone.；Improve BCB annotation guidelines to avoid over-generalization from superficial I/O patterns.

### case_id=5341 FN boilerplate_overlap

- 方法: `sendExceptionToServer` vs `getEncoding`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends exception details to a server via HTTP POST, building a URL-encoded data string and reading the response.
- B 摘要: Extracts character encoding from HTTP response headers or body by opening a URLConnection and reading lines.
- 静态失败原因: The static model likely relied on token overlap and syntactic structure, missing the abstract shared pattern of URLConnection usage due to low Jaccard similarity and different method names.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may consider both as network utility functions involving URLConnection and stream I/O, but this is too broad for a typical clone.
- 共享行为: Both open a URLConnection；Both handle IO including reading from streams；Both use try-catch for IOException
- 行为差异: A writes data to the server via OutputStreamWriter; B only reads data；A constructs a query string with multiple parameters; B does not；A prints response messages; B returns an encoding string；A has no return value; B returns a String
- 修正建议: Incorporate data flow analysis to distinguish send vs. receive behavior；Use semantic role labeling to capture intent；Enhance with API call sequences rather than just token matching

### case_id=5342 FN partial_functionality

- 方法: `sendExceptionToServer` vs `read`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends exception details to a server via HTTP POST and processes the response.
- B 摘要: Reads a camera log from a URL, parses each line into records, and sorts them.
- 静态失败原因: The static model focused on overall semantic equivalence and missed the partial functional similarity in the reading loop, leading to a false negative.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB annotators likely considered the common pattern of reading lines from a URL as sufficient functional overlap, labeling this as a Type-4 clone despite overall semantic differences.
- 共享行为: Both use BufferedReader to read lines from a URL connection
- 行为差异: A encodes parameters and writes to the server before reading, B does not；A parses the server response for success/failure, B parses each line into CameraLogRecord；A uses URLConnection with explicit output, B uses url.openStream() directly；A prints messages to stdout, B uses logging framework
- 修正建议: Incorporate sub-task or pattern recognition for common I/O operations；Use data-flow analysis to identify shared reading patterns across functions

### case_id=5343 FP lexical_or_api_overlap

- 方法: `actionPerformed` vs `saveFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Handles action events to set various application preferences (Graphviz path, ImageMagick path, date format, look and feel) and updates UI components accordingly.
- B 摘要: Saves current UI state (toolbars, window positions, sound settings, internal windows) to an XML configuration file persistently.
- 静态失败原因: Static models may have been misled by lexical overlap in tokens like 'LookAndFeel', 'UIManager', 'Suku.kontroller.putPref' vs 'uiElement.setAttribute', and the general theme of configuration. The long length and structural patterns (loops, conditionals) could also contribute to false correlation.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the functions have distinct purposes despite both dealing with settings. BCB's annotation style typically requires more functional overlap than just topical similarity.
- 共享行为: Both functions involve application configuration and settings.；Both reference look and feel through UIManager.
- 行为差异: Function A is an event handler that updates in-memory preferences and UI interactively; Function B serializes state to a file.；Function A uses JFileChooser for file selection; Function B uses XML serialization with DOM and XMLOutputter.；Function A modifies multiple preference keys via Suku.kontroller; Function B writes a structured XML document.
- 修正建议: Improve training with more negative examples that have topical similarity but different semantics.；Incorporate dataflow or control flow analysis to distinguish between event handling and file output.

### case_id=5344 FN benchmark_preference_bias

- 方法: `doGet` vs `transport`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Handles HTTP GET request for page display, including authentication and caching.
- B 摘要: Recursively copies a file or directory to a destination directory using FileChannel.
- 静态失败原因: Static BERT correctly predicted non-clone; the error is in BCB label, not the model.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB likely mislabeled this pair; no meaningful similarity exists.
- 行为差异: Entirely different domain: HTTP request handling vs file I/O；Different control flow: complex servlet logic vs simple recursion；Different input/output: HttpServletRequest/Response vs File
- 修正建议: Review BCB annotation for false positives；Remove this pair from clone set

### case_id=5345 FP lexical_or_api_overlap

- 方法: `doVersionCheck` vs `SRWGuiClient`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Check for software version update by reading a URL and comparing build numbers.
- B 摘要: Initialize a GUI browser that reads a URL, optionally processes XML/XSLT, and displays HTML content.
- 静态失败原因: Static BERT/GraphCodeBERT likely relied on token overlap and common API sequences (URL, BufferedReader, try-catch) which are boilerplate, causing it to overestimate similarity and produce a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels as non-clone because the functions implement entirely different high-level functionalities (version check vs. browser GUI), despite sharing low-level I/O patterns.
- 共享行为: Both read from a URL using URL, InputStream, and BufferedReader.；Both use try-catch for IOException.；Both read input line by line in a while loop.
- 行为差异: Function A is static and handles version checking; B is a constructor setting up a whole GUI.；A parses specific key-value lines (.version, .build); B processes XML/XSLT for transformation.；A shows dialogs; B creates GUI components (JEditorPane, JScrollPane, etc.).；A has no GUI setup; B sets layout, size, and visibility.
- 修正建议: Use models that capture method-level semantics and control flow (e.g., code graphs).；Incorporate method name and class context to disambiguate purpose.；Apply contrastive learning with examples of API-sharing but semantically different code.

### case_id=5346 FN partial_functionality

- 方法: `login` vs `lookupFutureEvents`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Logs into LOLA using HTTP POST with email and password, extracts session ID from response, and returns it.
- B 摘要: Fetches events from Meetup API using HTTP GET, parses JSON response, creates Event objects with multiple fields, and returns a list.
- 静态失败原因: Static BERT/GraphCodeBERT models rely heavily on token overlap and surface-level patterns; the low token Jaccard (0.09589) and different method names led it to predict non-clone, missing the broader functional similarity that BCB might accept.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as clones because they both involve making HTTP requests to external APIs and handling responses, which falls under similar network I/O functionality, even though the business logic differs significantly.
- 共享行为: Both perform HTTP requests to external APIs.；Both use BufferedReader to read response lines.；Both handle exceptions (though differently).
- 行为差异: HTTP method: POST vs GET.；Authentication: includes credentials in POST data vs API key in URL.；Response handling: extracts single session ID vs parses JSON into multiple Event objects.；Return type: String vs List<Event>.
- 修正建议: Improve detection of semantic similarity in network I/O operations across different APIs.；Incorporate structural patterns like URL opening and response parsing to capture partial functional equivalence.

### case_id=5347 FN partial_functionality

- 方法: `main` vs `sendRequest`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.5`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends a hardcoded POST request to RenRen API and prints the response.
- B 摘要: Sends a GZIP-compressed XML request to a configurable servlet and builds an XML document from the response.
- 静态失败原因: Low token Jaccard (0.09) and different API vocabularies (RenRen vs. GZIP/JDOM) cause the model to focus on lexical differences rather than the common HTTP communication pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considers both as Type-4 functional clones because they both implement the overall behavior of sending an HTTP request and receiving a response, despite differences in parameters and processing.
- 共享行为: Both create HTTP URL connections；Both set doOutput to true；Both write data to the output stream；Both read response from input stream
- 行为差异: Code_a hardcodes parameters using RenRen classes; Code_b reads server URL from preferences and compresses request；Code_a prints response line by line; Code_b parses response as XML with JDOM；Code_a is a main method; Code_b is a reusable sendRequest method；Error handling differs (Code_a uses simple throws vs Code_b catches exceptions and shows dialogs)
- 修正建议: Include more diverse HTTP client examples in training；Use structure-aware models (e.g., AST) to capture common control flow patterns；Add data augmentation with token substitution while preserving functionality

### case_id=5348 FN benchmark_preference_bias

- 方法: `copyFile` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Copies a file using FileChannel from input to output.
- B 摘要: Launches a NexOpen project configuration by reading pom files, setting properties, and managing profiles.
- 静态失败原因: Static BERT correctly predicted non-clone due to extremely low token Jaccard similarity (0.052) and no shared API or structural patterns, indicating no semantic equivalence.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have considered both as file-handling utilities with similar error handling patterns, but this is a weak basis for clone classification.
- 共享行为: Both methods deal with file I/O operations.；Both include resource management (closing channels, handling streams).
- 行为差异: copyFile performs a single file copy; launch performs complex configuration validation and setup.；copyFile uses NIO FileChannel; launch uses multiple file reads, XML handling, and property setting.；copyFile has no conditional logic; launch has many conditionals and error handling.；copyFile is generic file copy; launch is specific to a project framework.
- 修正建议: Re-validate BCB annotation for this pair to ensure correctness.；Consider removing or correcting mislabeled pairs in the benchmark.

### case_id=5349 FP lexical_or_api_overlap

- 方法: `loadSourceCode` vs `getTicketsForQueue`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a file from resources, applies syntax highlighting, and generates HTML source code display.
- B 摘要: Queries a remote ticket tracking API for open tickets in a queue, parses response, and returns list of ticket objects.
- 静态失败原因: Static BERT/GraphCodeBERT may have focused on lexical and structural similarities (both use try-catch, BufferedReader, readLine), missing the semantic intent difference due to limited context and dataflow understanding.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled non-clone because the functions have entirely different purposes and no shared functionality beyond basic I/O patterns.
- 共享行为: Both use BufferedReader and InputStreamReader to read lines from a data source.
- 行为差异: Function A reads from a local file resource; Function B reads from an HTTP response.；Function A generates HTML string for display; Function B parses ticket IDs and fetches ticket details.；Function A has no return value; Function B returns a List<RTTicket>.；Error handling differs: A sets a string on error; B throws or returns null.
- 修正建议: Enhance model with dataflow analysis to understand that the data sources and outputs are different.；Incorporate more training examples of false positives where I/O patterns appear similar but semantics differ.；Use method name and class context to disambiguate functionality.

### case_id=5350 FP lexical_or_api_overlap

- 方法: `getUser` vs `getNetworkServersIPs`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Loads a user by login from a DAO or falls back to parsing a configuration file with colon-delimited lines.
- B 摘要: Connects to a URL and parses lines following a marker to extract network server IPs using colon delimiter.
- 静态失败原因: Static BERT likely overemphasized lexical and API-level similarities (e.g., BufferedReader, URL, colon parsing) and structural patterns, missing the broader semantic difference in intent and data flow.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clones as 0 for functionally unrelated tasks; these methods serve entirely different purposes despite some structural overlap.
- 共享行为: Both use BufferedReader to read line by line from a stream.；Both parse lines using a colon delimiter.；Both have try-catch blocks for exception handling.
- 行为差异: Input type: userlogin (String) vs netaddress (URL as String).；Data source: classpath file vs remote URL.；Parsing logic: exact token matching vs state machine with a flag.；Purpose: user authentication vs network server IP extraction.
- 修正建议: Incorporate method names and signatures into the model input explicitly.；Use graph-based code representations that capture data and control dependencies.；Train with contrastive examples that penalize false positives from similar lexical patterns but different semantics.

### case_id=5351 FP boilerplate_overlap

- 方法: `encodeFileToFile` vs `readData`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Encodes a file to another file using Base64 encoding.
- B 摘要: Parses configuration strings into multiple HashSets and maps for Tibetan transliteration.
- 静态失败原因: Static BERT may have been misled by common Java boilerplate (try-catch, loops, variable declarations) and the long, truncated nature of code_b, causing it to overlook the fundamental semantic difference.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels as non-clone because the functions have entirely different purposes and implementations; only incidental structural similarities exist.
- 共享行为: Both use try-catch-finally for resource handling.；Both involve loops iterating over input data.
- 行为差异: encodeFileToFile performs I/O and Base64 encoding; readData parses and populates data structures.；encodeFileToFile returns a boolean success flag; readData is void and modifies static fields.；encodeFileToFile processes a single file; readData processes multiple string tokens and file lines.；readData has complex branching and state manipulation; encodeFileToFile is straightforward copy with encoding.
- 修正建议: Train on more diverse examples to emphasize functional semantics over syntactic patterns.；Use dataflow or control-flow analysis to capture core logic differences.；Consider method name and call context as additional signals.

### case_id=5352 FN partial_functionality

- 方法: `getResourceAsStream` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.95`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a remote resource via URL with caching and returns an InputStream.
- B 摘要: Copies a file using NIO FileChannel transferTo.
- 静态失败原因: The token Jaccard similarity is low (0.102), and the literal code structure differs significantly. A static BERT model would likely focus on the surface tokens and AST structure, missing the high-level behavioral similarity that BCB considers. The model may have learned to reject pairs with low token overlap and different method names.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider them clones because both implement a form of data copying from an input source to an output destination, albeit with different mechanisms (stream vs channel) and different sources (URL vs local file). The overarching pattern of 'read from source, write to destination' aligns with Type-4 semantic clone category.
- 共享行为: Both involve reading from a source and writing to a destination using streams/channels.；Both handle file I/O operations.
- 行为差异: Function A performs network operations, caching, and HTTP conditional checks; B is just a simple file copy.；Function A has complex error handling and logging; B uses exceptions and no logging.；Function A returns an InputStream; B is void.
- 修正建议: Incorporate behavior-level features, such as identifying common I/O patterns (e.g., read from InputStream, write to OutputStream) beyond exact code structure.；Use scenario-based matching that considers the functional context, e.g., both as 'copy' operations.；Augment training with examples where method names differ but core behavior (like copying) is similar.

### case_id=5353 FN dataflow_blindspot

- 方法: `main` vs `getEncoding`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.75`
- 推荐路线: `dynamic_equivalence_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: A main method that sends a hardcoded POST request to RenRen API and prints the response.
- B 摘要: A private method that extracts the character encoding from a URL response by examining headers and body.
- 静态失败原因: The models likely relied on token-level and structural similarity, which is low (Jaccard 0.126). The high-level semantic similarity of 'reading from a URL' is not captured due to differences in method names, parameters, and control flow, leading to a false negative.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行价值高：该样本可能是 API 写法不同但行为等价的漏报。建议测试目标为 input_output_equivalence。
- BCB 偏好解释: BCB may label these as clones because both involve network I/O operations reading from a URL connection, which aligns with a broad Type-4 clone definition focusing on similar high-level behavior despite different specific purposes.
- 共享行为: Both use URLConnection to read from a URL；Both use BufferedReader to read lines from an input stream；Both handle IOException
- 行为差异: A sends a POST request with specific parameters; B reads headers to find charset；A prints each response line; B extracts encoding from lines；A uses hardcoded values; B is generic and reusable；A's goal is to demonstrate API call; B's goal is to extract encoding
- 修正建议: Incorporate higher-level API usage patterns (e.g., URLConnection + BufferedReader) as features；Use data flow analysis to capture the sequence of I/O operations；Train on examples of broad semantic clones with low lexical overlap

### case_id=5354 FP lexical_or_api_overlap

- 方法: `run` vs `loadExistingAntlibs`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Runnable that loads a tile from a URL, parses its geometry, and adds it to a data source layer.
- B 摘要: Loads existing Antlibs from classpath resources by reading resource URLs and calling loadAntLib for each package.
- 静态失败原因: The model likely over-weighted the common I/O tokens (BufferedReader, readLine, InputStream) and missed the distinct semantic objects and method calls that differentiate the functions.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels non-clones when the overall functionality and domain-specific logic differ, despite structural similarities in I/O boilerplate.
- 共享行为: Open an InputStream from a URL；Use BufferedReader to read lines；Loop reading lines until null；Handle IOException with try-catch
- 行为差异: A uses synchronization on lauchedHTTPRequests; B does not；A checks for duplicate keys; B does not；A processes geometric data (GeometryCollection, VectorTile); B processes ant library package names；A writes to data source; B calls loadAntLib
- 修正建议: Incorporate data flow analysis to track how inputs are used；Enhance representation of method names and API calls；Use contrastive learning with functional differences

### case_id=5355 FP lexical_or_api_overlap

- 方法: `getURLContent` vs `SRWGuiClient`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches the content of a URL and returns it as a string.
- B 摘要: Constructs a GUI browser window, reading and processing URL content for display.
- 静态失败原因: The model likely overemphasized the lexical overlap (e.g., URL creation, BufferedReader, readLine, appending) and ignored the broader structural and semantic differences, especially the GUI setup and conditional processing in function B.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically annotates non-clones when functions have different signatures and purposes despite shared sub-tasks. The low token Jaccard and contrasting overall behavior indicate they are not functionally similar even under relaxed Type-3/4 criteria.
- 共享行为: Both open a URL and read its content line by line using BufferedReader.；Both accumulate the read lines into a StringBuilder/StringBuffer.
- 行为差异: getURLContent returns the content string; SRWGuiClient is a constructor with no return value and sets up a GUI.；SRWGuiClient performs XML/stylesheet transformation and displays content; getURLContent only returns raw text.；SRWGuiClient handles exceptions with warnings and includes extensive GUI initialization; getURLContent throws IOException.；SRWGuiClient does not explicitly close the reader; getURLContent closes it in a finally block.
- 修正建议: Incorporate AST or control flow features to distinguish different function signatures and overall structure.；Use a code representation that captures the full function semantics, including all statements and their roles.；Train with more negative examples that have lexical overlap but different functionality.

### case_id=5356 FN benchmark_preference_bias

- 方法: `recurseFiles` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Recursively traverses a directory and writes non-zip files into a ZipArchiveOutputStream.
- B 摘要: Iterates over a list of pages, reads XML and control files, performs XSLT transformations, and writes the output to files.
- 静态失败原因: The static BERT model correctly predicted non-clone due to very low token Jaccard similarity (0.067) and lack of shared code structure, but it failed to align with BCB's overly broad functional category that the annotator might have used.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB annotator might have considered both as file-processing utilities that generate output, possibly due to a very broad interpretation of Type-4 (semantic) clones where the task is seen as 'reading input and writing output'.
- 共享行为: Both perform file I/O operations, including reading and writing files
- 行为差异: Function A uses recursion for directory traversal, while Function B iterates over a pre-built page list；Function A creates ZIP archives, whereas Function B performs XSLT transformations and string replacements；Function A filters out .zip/.ZIP files; Function B does not filter files based on extension；Function B involves HTML/XML DOM manipulation and uses multiple configuration parameters; Function A has simple filename logic
- 修正建议: Incorporate task-level semantics or documentation to distinguish generic file I/O from specific processing tasks；Use dynamic analysis to capture actual behavior differences

### case_id=5357 FP lexical_or_api_overlap

- 方法: `readVersion` vs `getFullScreenUrl`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a version resource file from classpath and extracts version, revision, and compile date into fields.
- B 摘要: Fetches a YouTube webpage, parses the fullscreenUrl parameter, extracts video_id and t, and constructs a fullscreen video URL.
- 静态失败原因: The model likely overemphasized lexical and API-level overlap (URL, BufferedReader, while loop, split('=')) without capturing the different functional intents and data transformations.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clone because functions have distinct domain-specific purposes and output types, even though they share generic I/O and parsing patterns.
- 共享行为: Both use URL and BufferedReader to read data from a stream.；Both parse lines with contains/startsWith and split on '='.；Both catch IOException and print error messages.
- 行为差异: Different data sources: classpath resource vs HTTP URL.；Different output: stores fields vs returns a constructed URL.；B includes UI progress updates and debug prints; A does not.；Parse logic: A uses simple key-value extraction; B extracts from a specific line then further splits by '&'.
- 修正建议: Incorporate method-level context (class name, method signature) into representation.；Use dataflow analysis to distinguish different variable dependencies.；Train on pairs with high lexical but low semantic similarity as negative examples.

### case_id=5358 FN partial_functionality

- 方法: `runInternal` vs `doVersionCheck`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Connects to an HTTP URL, parses OPDS catalog with pagination, and either downloads a book or processes entries.
- B 摘要: Fetches a version file from a URL, parses version/build numbers, and displays update message.
- 静态失败原因: The model likely focused on lexical and structural differences (low token Jaccard, different length) and missed the abstract functional similarity of network I/O and text parsing.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considers both as Type-4 semantic clones because they perform the same high-level pattern: make an HTTP GET request, parse the response text, and respond to results. The specific parsing details and purpose are secondary in this broad labeling.
- 共享行为: Both open HTTP connections to URLs and read textual data；Both parse the response to extract structured information；Both handle errors with user feedback
- 行为差异: A uses detailed HTTP setup (timeouts, headers, redirects); B uses simple URL.openStream()；A may download binary streams or parse XML with pagination; B parses simple key-value lines；A returns data via callback; B shows dialog directly；A is significantly longer and more complex
- 修正建议: Improve abstraction of network operations (e.g., recognize URL.open() patterns)；Incorporate data flow for response handling (reading streams, parsing)；Use code summarization or API call graphs to capture high-level intent

### case_id=5359 FN partial_functionality

- 方法: `addIDs` vs `executeHttpGet`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches metabolite data from a web service by constructing a URL, parsing HTML to extract IDs and molecular weight, and setting them on a PeakListRow object.
- B 摘要: Executes an HTTP GET request to a given URI and returns the response as a JSONObject.
- 静态失败原因: Low token-level similarity and different method names/return types cause static embeddings to miss the shared abstract pattern of HTTP request-response processing.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels as clone when both functions perform the same high-level operation (HTTP GET and read response) despite differences in details, considering it a Type-4 semantic clone.
- 共享行为: Both perform an HTTP GET request to a remote server；Both read the response line by line using BufferedReader
- 行为差异: The HTTP client implementation differs: A uses java.net.URL, B uses Apache HttpClient；Parsing logic: A parses HTML to extract specific metabolite fields, B parses the entire response as JSON；Return type: A returns an int (score), B returns a JSONObject；Error handling: A catches IOException and returns 0, B throws Exception
- 修正建议: Use data-flow or graph-based models that capture high-level control flow patterns like HTTP request handling；Incorporate code summarization or documentation to infer intent

### case_id=5360 FN partial_functionality

- 方法: `createSettingsIfNecessary` vs `getFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.75`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Creates a settings file from a bundled resource if it does not already exist.
- B 摘要: Downloads a WSDL file from a URL, modifies its endpoint address, and saves it locally if not already present.
- 静态失败原因: Static BERT/GraphCodeBERT likely relied on lexical and syntactic similarity, which is low (Jaccard 0.1357). The functions share common API calls (File, InputStream, FileOutputStream, close) but differ in structure and control flow. The model may have been misled by the low overall token overlap and the presence of XML manipulation in B, leading it to predict non-clone.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as instances of the 'download file if missing' pattern, with variations in source and additional processing, fitting Type-3/Type-4 broad similarity.
- 共享行为: Both check if a file exists and create it via copying from an input stream to an output stream if not present.
- 行为差异: Function A copies from a bundled resource stream; Function B downloads from a URL then modifies XML content.；Function A has no return value; Function B returns the file path.；Function B has extensive error handling and multiple catch blocks; Function A only throws IOException.；Function B uses NIO channels for efficient transfer; Function A uses IOUtils.copy.
- 修正建议: Include data-flow analysis to capture the similarity of file-existence check followed by stream copy.；Enhance models to recognize high-level semantic patterns like 'conditional file download' even with varying preprocessing steps.

### case_id=5361 FP partial_functionality

- 方法: `getRequestContent` vs `downloadFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads the first line from a URL and returns it as a string.
- B 摘要: Downloads a file from a URL to a local file with progress tracking, returns boolean true.
- 静态失败原因: Static BERT models may overemphasize the shared API calls (URL, URLConnection, InputStream) and miss the fundamentally different end behavior and output.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB typically labels as non-clone when functions have different input/output and high-level purpose, even if they share some low-level API usage.
- 共享行为: Both open a URL connection and read from an input stream.；Both use java.net.URL and URLConnection classes.
- 行为差异: Function A reads only the first line, while Function B reads the entire stream and writes to a file.；Function A returns the line read; Function B returns boolean true.；Function B includes progress reporting and file I/O operations.
- 修正建议: Train the model to focus on the overall return type and side effects (e.g., file writing vs. reading one line).；Include more discriminative examples of similar API usage but different functionality.

### case_id=5362 FN benchmark_preference_bias

- 方法: `readData` vs `lookupFutureEvents`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Parses static string constants and a file to populate sets and hash tables for Tibetan transliteration mapping.
- B 摘要: Fetches upcoming events from Meetup API, parses JSON response, and returns a list of Event objects.
- 静态失败原因: Static BERT/GraphCodeBERT would see very low token overlap and different API calls (StringTokenizer vs URLConnection, JSON parsing), so it correctly predicted non-clone. The error is in BCB label, not static prediction.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might consider both as data parsing/loading operations, but the input sources and data types are completely different. Possibly the truncation in A hides additional parsing that resembles B? But likely BCB annotation is an error.
- 共享行为: Both read data and populate collections.
- 行为差异: Function A reads from internal string constants and a local file; Function B makes an HTTP request to an external API.；Function A processes data for Tibetan transliteration; Function B processes event data from Meetup.；Function A uses StringTokenizer and manual parsing; Function B uses JSON parsing and URL connection.
- 修正建议: Re-evaluate BCB annotation for this pair; consider correcting the label to 0.

### case_id=5363 FN partial_functionality

- 方法: `sendExceptionToServer` vs `handledRun`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends exception details to a remote server via HTTP POST with multiple encoded parameters.
- B 摘要: Downloads and updates game data file from a remote server if a newer version is available.
- 静态失败原因: Static BERT/GraphCodeBERT likely focused on low token overlap (Jaccard 0.1458) and distinct method names, missing the structural similarity in network I/O patterns. The model may not capture long-range semantic equivalence of network operations.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as network data transfer operations with similar structural patterns (URL, streams, exception handling), classifying them as Type-3/Type-4 clones despite different domain logic.
- 共享行为: Both perform network I/O using URL and streams；Both use try-catch for error handling；Both read from and/or write to network resources
- 行为差异: A sends data (POST) while B downloads data (GET via openStream)；A encodes parameters and sends a request, B checks version and conditionally overwrites a file；A outputs to console, B shows dialog and logs errors
- 修正建议: Incorporate structural similarity features for network I/O patterns；Use AST-based or control-flow similarity to capture boilerplate；Include data flow analysis for stream handling

### case_id=5364 FP lexical_or_api_overlap

- 方法: `importSequences` vs `retrieveTemplate`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads FASTA sequences from a URL and stores names and sequences.
- B 摘要: Reads a blog template from a URL and caches it.
- 静态失败原因: Static BERT may have focused on lexical and API overlaps (URL, openStream, readLine, try-catch) and missed the different data processing logic and output types.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled 0 because the functions have distinct purposes (importing sequences vs. retrieving a template) despite sharing URL I/O, which does not constitute a clone even under lenient Type-3/4 criteria.
- 共享行为: Both open a URL and read input streams.；Both use InputStreamReader/BufferedReader to read lines.；Both handle IOException and read until some condition.
- 行为差异: Function A parses FASTA format with headers (>), while Function B reads all lines into a single string.；Function A stores parsed names and sequences into lists; Function B returns a cached string.；Function A has more complex tokenization and sequence reading logic.；Error handling differs: Function A catches specific exceptions, Function B throws Exception.
- 修正建议: Enhance training with examples emphasizing data flow and output semantics.；Use graph-based models that capture control and data dependencies.；Incorporate type information and method signatures for better differentiation.

### case_id=5365 FP lexical_or_api_overlap

- 方法: `readIntoList` vs `SRWGuiClient`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads lines from a URL and creates JMenuItem objects with action commands to populate a map.
- B 摘要: Constructs a GUI browser, reads a URL, processes XML/XSLT, and displays transformed content in a JEditorPane.
- 静态失败原因: Static BERT overemphasized common API tokens (URL, BufferedReader, readLine, InputStreamReader) and the try-catch structure, ignoring high-level semantic differences in program intent.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clones when functions differ significantly in purpose and output, even if they share low-level I/O patterns.
- 共享行为: Both open a URL stream and read lines using BufferedReader and InputStreamReader.
- 行为差异: A builds a menu of JMenuItems; B builds a full GUI browser.；A adds action listeners to set text field; B handles hyperlinks and displays HTML.；B performs XML/XSLT transformation; A does not.；B handles stylesheets and transformer caching; A does not.
- 修正建议: Incorporate data flow or control flow analysis to distinguish functions with similar I/O but different logic.；Enhance model with longer-range context or graph-based representations to capture overall program structure.

### case_id=5366 FP lexical_or_api_overlap

- 方法: `main` vs `createJAR`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: A main method that parses a Prolog file, generates adapter classes, and packages them into a JAR along with metadata.
- B 摘要: A utility method that creates a JAR file by copying a resource JAR or creates a directory, then writes a serialized document object into it.
- 静态失败原因: Static BERT/GraphCodeBERT likely focused on lexical and API-level similarities (e.g., 'FileOutputStream', 'ObjectOutputStream', 'jar', 'adapter') and structural patterns like try-catch blocks, ignoring the higher-level semantic differences in the overall algorithm.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled as non-clone because the functions have vastly different purposes and control flow, even though they share some low-level file operations. BCB requires significant functional overlap, which is absent here.
- 共享行为: Both create JAR files；Both use FileOutputStream and ObjectOutputStream；Both handle exceptions and print stack traces；Both involve file I/O operations
- 行为差异: A's logic is a complex pipeline of parsing, code generation, and packaging; B's logic is simple copying and serialization；A uses class loading, AST visitors, and annotation generation; B does not；A writes multiple classes and resources; B writes a single serialized object；A checks for command line arguments; B takes parameters directly
- 修正建议: Improve training with more negative examples of functions sharing APIs but different semantics；Incorporate dataflow analysis to distinguish between different sequences of operations；Use graph-based representations that capture control flow and data dependencies

### case_id=5367 FP lexical_or_api_overlap

- 方法: `actionPerformed` vs `readData`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `None`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Reads a gzipped file, extracts rs IDs, queries NCBI E-utility via HTTP POST, and prints response to stderr.
- B 摘要: Reads a configuration file, parses comma-separated values into sets and maps for Tibetan Wylie transliteration processing.
- 静态失败原因: The model likely overemphasized the presence of similar lexical items like 'new HashSet()', 'StringTokenizer', 'while loop with hasMoreTokens()', and exception handling blocks, ignoring the core behavioral differences. The long and complex code of B may have caused the model to latch onto reusable patterns.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels non-clones when functions have completely different purposes despite superficial structural similarities. Both functions involve file I/O and tokenization but achieve entirely different goals.
- 共享行为: Both involve reading data from a file；Both use tokenization to split strings；Both handle IOException
- 行为差异: Function A performs a network request (HTTP POST) to an external API; Function B only populates in-memory data structures；Function A filters tokens by prefix 'rs'; Function B processes tokens unconditionally into multiple sets；Function A writes to System.err; Function B has no output；Function A uses GZIPInputStream; Function B does not
- 修正建议: Improve sensitivity to semantic role of tokenization/IO operations；Incorporate control-flow or data-flow analysis to distinguish data loading from network interaction；Increase diversity of negative training examples with similar boilerplate but different algorithms

### case_id=5368 FN partial_functionality

- 方法: `copyResource` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a single resource (URL or local file) to a destination file using byte-by-byte stream.
- B 摘要: Copies all files from a source directory to a destination directory using FileChannel and ByteBuffer.
- 静态失败原因: Static BERT models may focus on syntactic structure and token overlap, missing the high-level functional similarity due to low Jaccard similarity (0.164) and different APIs.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considered both as file copying operations, fulfilling the same high-level purpose, thus a Type-4 clone.
- 共享行为: Both copy file contents from a source to a destination.
- 行为差异: A copies a single resource; B copies all files in a directory.；A uses byte-by-byte stream copy; B uses channel and buffer.；A throws exception on missing resource; B catches IOException and ignores.；A is private; B is public static void main.
- 修正建议: Improve semantic embeddings to capture task-level similarity.；Incorporate method name and API call context for better functional understanding.

### case_id=5369 FP partial_functionality

- 方法: `run` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches a tile from a data source and processes GeoJSON response to create geometry objects for rendering.
- B 摘要: Searches Google Images for a query and parses HTML to extract image URLs, updating a UI component.
- 静态失败原因: Static BERT models often rely on lexical and structural overlap, and may be misled by the common tokens (URL, BufferedReader, readLine, try-catch) and the overall fetch-and-parse pattern, ignoring the critical semantic differences in the processing logic and output.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB typically labels as clones only if the core functionality (input->output) is substantially similar. Here both functions fetch and parse HTTP responses but the parsing and output are entirely different domains (mapping vs image search), so BCB would likely consider them non-clones despite shared I/O patterns.
- 共享行为: Both open HTTP connections to retrieve content from a URL.；Both use BufferedReader to read lines of text and concatenate into a single string.；Both include exception handling for I/O errors.
- 行为差异: Function A uses a synchronized block to manage duplicate requests, while B does not.；Function A parses GeoJSON data and creates geometry objects; B parses HTML and extracts image URLs.；Function A adds results to a data loader and triggers caching; B updates a UI label with an image icon.；Function A has different URL construction (from data source) compared to B (fixed Google Images URL with query).
- 修正建议: Incorporate data flow analysis to track how the fetched content is processed and used downstream.；Use graph-based code representations that capture control and data dependencies beyond token sequences.；Train with contrastive learning that emphasizes functional equivalence over lexical similarity.

### case_id=5370 FN partial_functionality

- 方法: `getHTML` vs `readRemoteFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches HTML content from a URL with specified encoding, optionally writes to a file, and returns the content as string with newlines.
- B 摘要: Reads a remote file from a fixed URL and returns its content as a single string without newlines or encoding specification.
- 静态失败原因: Static models like GraphCodeBERT may rely heavily on token overlap and surface-level structure; low Jaccard (0.24) and different method signatures/control flow cause it to miss the semantic similarity. The model fails to abstract away details like encoding and file I/O that are not central to the core functionality.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels functions as clones if they share the same high-level task (reading remote content into a string) despite minor implementation details like encoding, headers, or file writing, which are considered Type-4 partial functionality.
- 共享行为: Both establish HTTP connections to fetch remote resources；Both read line by line and accumulate into a string；Both return the fetched content as a string
- 行为差异: A uses HttpURLConnection with User-Agent header; B uses URL.openStream()；A supports encoding; B does not；A appends newlines between lines; B does not；A optionally writes to file; B does not
- 修正建议: Use dataflow-aware models that capture reads from URL and string accumulation；Incorporate task-level annotations or API usage patterns；Apply code summarization to match abstract behavior

### case_id=5371 FN benchmark_preference_bias

- 方法: `genCustRatingFileAndMovieIndexFile` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Reads a binary movie ratings file and generates separate index and rating files using FileChannel and ByteBuffer.
- B 摘要: Builds a website by transforming XML pages with XSLT, reading control files, and writing output HTML files.
- 静态失败原因: The model correctly predicted non-clone due to low lexical overlap and different API usage; it did not recognize the vague file I/O similarity that BCB considered.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as a clone due to broad Type-4 similarity: both functions read from one file and write to multiple output files, sharing a dataflow pattern of reading input and generating outputs.
- 共享行为: Both perform file I/O operations and write output files.
- 行为差异: Different input formats (binary vs XML)；Different processing logic (binary record parsing vs XSLT transformation)；Different output generation (binary index/rating files vs HTML pages)；Different error handling and complexity
- 修正建议: Review BCB annotation for potential mislabeling；If BCB label is correct, incorporate dataflow analysis to detect shared input-output patterns；Increase training data for broad Type-4 clones

### case_id=5372 FP boilerplate_overlap

- 方法: `compressWithZip` vs `readData`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Compresses a list of files into a zip archive by iterating over file names and writing zip entries.
- B 摘要: Reads and parses multiple comma-separated string fields to populate various sets and a hash map, with additional file parsing logic.
- 静态失败原因: The model may have been misled by superficial similarities such as the use of while loops, string manipulation, and methods like 'nextToken', despite low Jaccard similarity. Long-range semantic differences and lack of dataflow awareness could also contribute.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the functions perform entirely different tasks with no shared functionality beyond basic programming constructs.
- 共享行为: Both use while loops to iterate over data.；Both manipulate strings (e.g., substring, tokenization).
- 行为差异: compressWithZip handles file I/O and ZIP compression; readData parses configuration data into in-memory collections.；compressWithZip writes to a file; readData does not produce any output file.；compressWithZip uses FileInputStream and ZipOutputStream; readData uses StringTokenizer and HashSet.；readData has complex conditional logic and error handling; compressWithZip is simpler.
- 修正建议: Incorporate control-flow and data-flow analysis to distinguish I/O operations from in-memory processing.；Use function-level summarization to capture overall purpose rather than local code patterns.

### case_id=5373 FN partial_functionality

- 方法: `getEncoding` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Extracts charset encoding from a URL's HTTP headers or HTML body.
- B 摘要: Fetches a web page and prints its content line by line.
- 静态失败原因: Low token Jaccard similarity (0.18) and different method signatures/return types likely caused the static model to miss the shared API usage pattern (URL, BufferedReader, readLine loop). The model may be overly sensitive to lexical and structural differences.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider this a Type-4 clone because both functions implement the fundamental pattern of reading a URL line by line, even though they process the lines differently. The additional encoding extraction in A is seen as an extension of the shared URL reading task.
- 共享行为: Open a URL connection and create a BufferedReader from the input stream.；Read lines from the input stream in a loop.
- 行为差异: Function A searches for charset encoding in headers and body; function B does not.；Function A returns a String (encoding); function B is void and prints output.；Function A processes header fields; function B does not.
- 修正建议: Incorporate dataflow analysis to detect common API usage patterns (e.g., URL.openStream, BufferedReader.readLine).；Use graph-based representations that capture control flow and data dependencies around stream operations.；Train on more diverse examples of partial functional similarity.

### case_id=5374 FN partial_functionality

- 方法: `encodeFileToFile` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Encodes a file to another file using Base64 encoding via stream copy.
- B 摘要: Downloads a KMZ file from a URL, extracts ZIP entries, and writes each entry to a file.
- 静态失败原因: Low token overlap and different APIs (Base64 vs Zip) caused the model to miss the abstract stream copy pattern; it focused on surface-level tokens.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider them clones due to the common streaming copy pattern with buffer, which is a Type-3 structural similarity despite different surrounding logic.
- 共享行为: Both open input and output streams；Both use a buffer to copy data in a read-write loop；Both close streams in a finally-like manner
- 行为差异: Different input sources: file vs URL；Different output: single file vs multiple files from ZIP；Base64 encoding in A vs no encoding but ZIP extraction in B
- 修正建议: Improve representation of I/O patterns using data-flow or AST-based structures；Use fine-tuning with examples of streaming copy clones；Incorporate library context for common stream APIs

### case_id=5375 FP lexical_or_api_overlap

- 方法: `doVersionCheck` vs `getTicketsForQueue`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Checks for a new version of jEdit by reading version and build numbers from a URL and comparing with current build.
- B 摘要: Retrieves open tickets for a given queue from a Request Tracker API by parsing ticket IDs and fetching each ticket.
- 静态失败原因: Static BERT models rely on token similarity and API sequences; both functions contain common Java I/O patterns (URL, BufferedReader, while loop, readLine), causing a false positive due to lexical and API overlap.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would not consider these clones because the overall functionality and purpose differ completely (version check vs ticket retrieval), despite sharing some I/O boilerplate.
- 共享行为: Both open an HTTP connection to a URL；Both read lines from a BufferedReader；Both parse lines using String.startsWith；Both handle exceptions
- 行为差异: Function A reads version/build info; Function B reads ticket IDs；Function A compares build versions; Function B retrieves full ticket objects；Different URL construction and parameter handling；Different error messages and UI interactions vs logging
- 修正建议: Incorporate control-flow and data-flow analysis to distinguish different behaviors；Use AST-based or dependency-graph features to capture semantics beyond API sequences；Train on more diverse non-clone pairs with similar boilerplate

### case_id=5376 FP lexical_or_api_overlap

- 方法: `execute` vs `main`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Executes method injection into class files and updates a CallStack file.
- B 摘要: Generates adapter classes from a Prolog file and writes them to a JAR.
- 静态失败原因: The model likely over-weighted the lexical similarity from common ASM API calls (ClassReader, ClassWriter, InputStream, OutputStream) and the method name 'execute' vs 'main' both containing common Java patterns, ignoring the completely different program logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clones when functions have distinct high-level purposes and only share generic library usage patterns.
- 共享行为: Both use ClassReader and ClassWriter from the ASM library.；Both involve reading and writing class files or resources.；Both have try-catch blocks for IOException.
- 行为差异: Function A injects methods into existing class files; Function B generates new adapter classes.；Function A processes a predefined list of class files; Function B parses a Prolog file and uses visitor pattern.；Function A updates a CallStack file; Function B creates a JAR file with multiple resources.；Function A uses MethodInjector and PushMethodGenerator; Function B uses FactVisitor and AdapterAnnotationGenerator.
- 修正建议: Improve training data to include more diverse negative examples with API overlap but different semantics.；Use graph-based representations that capture control and data flow more accurately.；Enhance model to focus on method-level purpose rather than token-level similarities.

### case_id=5377 FP lexical_or_api_overlap

- 方法: `load` vs `checkForUpgrade`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Downloads XML content from pastebin via HTTP and returns it as a string.
- B 摘要: Checks for software upgrades by querying a license server, processes upgrade data, and updates UI accordingly.
- 静态失败原因: The static BERT model likely overemphasized the lexical overlap of common HTTP reading patterns (URL, BufferedReader, while loop) and failed to capture the fundamentally different semantics and control flows of the two functions.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels these as non-clones because they have entirely different purposes and logic, despite sharing some boilerplate HTTP reading code.
- 共享行为: Both open a URL connection and read lines from an HTTP response stream.；Both concatenate lines read from the stream into a single string.
- 行为差异: Function A is a straightforward HTTP download; function B performs database queries, license validation, and UI updates.；Function A has a simple return type (String); function B returns void and throws an exception.；Function A handles only pastebin URLs; function B constructs complex query parameters for a license server.；Function B involves conditional logic based on parsed XML-like responses, whereas function A does no parsing.
- 修正建议: Incorporate dataflow analysis to distinguish functional purpose beyond API sequences.；Use structure-based features that capture high-level control flow and operation types.；Train with harder negative examples that share API calls but differ in overall behavior.

### case_id=5378 FN boilerplate_overlap

- 方法: `sendExceptionToServer` vs `doVersionCheck`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.7`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends exception details to a server via HTTP POST with URL-encoded parameters.
- B 摘要: Checks for new version by reading a version file from a URL and comparing build numbers.
- 静态失败原因: Low token overlap (0.22) and different keywords (e.g., sendException vs doVersionCheck) caused the model to miss the structural similarity in network I/O pattern.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may consider them clones due to the common boilerplate of opening a URL, reading/writing streams, and handling IOExceptions, fitting broad Type-3/Type-4 similarity.
- 共享行为: Both open a URL and perform network I/O；Both read from an input stream using BufferedReader；Both handle IOException
- 行为差异: A writes data to the server (POST), B only reads data (GET)；A sends exception and system info, B retrieves version info；A uses URLConnection with explicit output, B uses openStream() without output
- 修正建议: Incorporate structural patterns like URL opening, stream handling, and error handling；Use data flow or graph-based representations to capture I/O operations；Train on more diverse network-related function pairs

### case_id=5379 FP boilerplate_overlap

- 方法: `googleImageSearch` vs `downloadModel`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Performs a Google image search for current track's artist and album, then extracts image URLs from the HTML response.
- B 摘要: Downloads an RDF model from a given URL by opening an HTTP connection and reading the response.
- 静态失败原因: The model likely overemphasized the overlapping token patterns such as 'URL', 'HttpURLConnection', 'openConnection', and 'getInputStream', which are common boilerplate in network I/O methods, and missed the semantic context of what is done with the read data.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB marks non-clone because the two functions have entirely different purposes (image search vs. model download), despite sharing low-level HTTP reading boilerplate.
- 共享行为: Open an HTTP connection to a URL；Read data from the input stream of the connection
- 行为差异: A parses HTML to extract image URLs; B reads RDF data into a Model object；A updates a global list (googleImages); B returns a Model；A checks a condition on artist name; B does not；A shows an error dialog; B throws a RuntimeException
- 修正建议: Enhance the model to capture the functional purpose of the method beyond low-level I/O operations.；Incorporate data-flow analysis to track how the read data is used (e.g., stored in list vs. returned as model).；Improve tokenization to distinguish domain-specific terms like 'googleImages' and 'model'.

### case_id=5380 FN partial_functionality

- 方法: `addIDs` vs `run`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Makes HTTP request to GMD service, parses HTML to extract metabolite IDs and a score, and updates a PeakListRow object.
- B 摘要: Makes HTTP GET request with basic authentication, reads entire response line by line, and stores the concatenated result in a field.
- 静态失败原因: Static BERT/GraphCodeBERT likely over-focused on token overlap (which is low) and missed the structural similarity in the HTTP-reading boilerplate. The long and partially truncated code in A also may have confused the model, causing it to treat them as distinct.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have considered them clones due to the shared high-level pattern of performing an HTTP GET request, reading the response with a BufferedReader, and similar error handling, despite different domain-specific logic. This aligns with Type-3/Type-4 broad similarity in BCB.
- 共享行为: Both open an HTTP connection and read lines using BufferedReader.；Both handle IOException/Throwable in try-catch blocks.
- 行为差异: A parses specific HTML patterns (Metabolites, Analytes) to extract IDs; B reads all lines without parsing.；A returns an integer score; B stores the response string in a field and sets a finish flag.；A uses no authentication; B uses Basic Auth.；A may break early upon finding a match; B reads all lines.
- 修正建议: Use a model that captures control flow structure rather than just token overlap.；Incorporate type information or data flow to recognize similar I/O patterns.；Fine-tune on BCB's annotation criteria which may consider broad functional similarity.

### case_id=5381 FN partial_functionality

- 方法: `readVersion` vs `File2String`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a version resource file and extracts version, revision, compile date fields.
- B 摘要: Reads a file (filesystem or classpath) and returns its entire content as a single string.
- 静态失败原因: Static BERT/GraphCodeBERT models rely on token sequence and structural similarity. The token Jaccard of 0.34 is moderate, and the model may have focused on differing keywords (like 'Version=' vs 'append') and return types, missing the common IO boilerplate pattern. The fallback logic and System.exit in B further differentiate the tokens, leading to a non-clone prediction.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often annotates Type-3 or Type-4 clones where the core operation (reading a text file line-by-line) is similar, even if the exact processing differs. The IO boilerplate and resource loading pattern are strong indicators of a clone in BCB's judgment.
- 共享行为: Reads a text file line by line using BufferedReader and InputStreamReader；Handles IOException with printStackTrace；Uses ClassLoader.getSystemResource to locate resource；Closes reader in finally block or after loop
- 行为差异: A parses specific key-value lines and sets class variables; B concatenates entire file into a single string；A returns void; B returns String；B has fallback logic to try directory/filename if initial File fails; A always uses system resource；B calls System.exit(-1) on failure; A does not exit
- 修正建议: Increase sensitivity to IO boilerplate patterns common in Type-4 clones；Incorporate code structure features like AST or CFG to capture the overall reading loop；Train on more examples where functionality diverges after a shared reading pattern；Use dataflow analysis to recognize that both functions read from a stream and iterate

### case_id=5382 FN lexical_or_api_overlap

- 方法: `doTransfer` vs `writeFileType`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.1`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Forwards an HTTP request to another URL, copying headers, body, and returning the response.
- B 摘要: Reads URIs from a file, fetches each URI's content, checks for OWL/RDFS/RDF namespaces in first 100 lines, and writes classification to an output file.
- 静态失败原因: Static BERT/GraphCodeBERT likely focused on lexical and API overlaps like 'URL', 'openConnection', 'getInputStream', 'BufferedReader', and try-catch blocks, ignoring the completely different control flow and data transformations.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may have considered both functions as involving URL connections and I/O, and possibly saw a pattern of reading from a source and writing to a destination, but this is too broad for a semantic clone.
- 共享行为: Both use URL connections to fetch data from remote URLs.；Both perform I/O operations (reading input and writing output).
- 行为差异: Input source: HTTP request vs. file containing URIs.；Output destination: HTTP response vs. file.；Core logic: proxy/forwarding vs. content classification based on namespace detection.
- 修正建议: Incorporate dataflow analysis to track how data is transformed.；Train on more diverse I/O patterns to distinguish proxy vs. crawler behavior.；Use program slicing to focus on core functional logic rather than boilerplate I/O.

### case_id=5383 FN partial_functionality

- 方法: `PageLoader` vs `readGeoParserResult`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads the entire content from a given URL and stores it in a field.
- B 摘要: Sends an XML query to a geo-parsing service, reads and parses the XML response, and returns a collection of place names with optional gazetteer IDs.
- 静态失败原因: Static BERT/GraphCodeBERT models rely heavily on token similarity and structural overlap. The Jaccard similarity is very low (0.076) due to different method names, long strings in B, and different identifiers. The model likely focused on the overall difference in length and content, missing the shared I/O pattern because it is overshadowed by the complex XML construction and parsing in B. The model may have been biased by the large amount of unique tokens in B, causing it to classify as non-clone.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider this a clone due to the shared pattern of opening a URL and reading lines into a buffer, which is a common core behavior. Despite the differences in surrounding logic and purpose, the essential I/O pattern is similar, aligning with broad Type-3/Type-4 clone acceptance.
- 共享行为: Both open a URL and read its content line by line using BufferedReader and InputStreamReader；Both close the reader after reading
- 行为差异: Function A only reads raw text; Function B constructs an XML request, sends it to a service, and parses the XML response.；Function A stores output in a field; Function B returns a structured collection.；Function B includes retry logic and a testing shortcut; Function A does not.；Function B has much more complex logic including XML parsing and iteration over elements.
- 修正建议: Improve model's ability to recognize shared sub-patterns even when overall code is different；Incorporate dataflow or control flow analysis to identify common I/O operations；Use graph-based representations to capture structural similarities like URL opening and line reading

### case_id=5384 FP boilerplate_overlap

- 方法: `readData` vs `encodeFileToFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Parses a configuration file into sets and maps for Tibetan transliteration.
- B 摘要: Encodes a file to Base64 and writes it to another file.
- 静态失败原因: Static BERT likely over-relied on boilerplate code patterns (try-catch-finally, file I/O, while loops) and ignored the distinct semantic intent of each method.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB requires functional similarity; these functions serve entirely different purposes, so BCB would label them as non-clones.
- 共享行为: Both involve reading from file input and handling I/O exceptions.
- 行为差异: A parses structured text data into collections; B encodes binary data.；A uses StringTokenizer and populates multiple sets; B uses Base64 encoding and writes to an output file.；A has complex conditional parsing logic; B has a simple read-write loop.
- 修正建议: Leverage method names and signatures to distinguish semantics.；Incorporate dataflow or graph representations to capture actual operations.；Use more training data with diverse file-processing functions to reduce boilerplate bias.

### case_id=5385 FN partial_functionality

- 方法: `sendRequest` vs `register`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.75`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends an HTTP request to a servlet, compressing the XML payload with GZIP, and reads the response.
- B 摘要: Registers a User object by hashing password, creating a forum account via URL, persisting to database, and sending confirmation email.
- 静态失败原因: Static BERT models rely on token overlap and surface-level similarity; the very low Jaccard (0.095) and different method names/semantics cause low embedding similarity, missing the broad functional pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label them as clones due to the common pattern of URL connection setup and I/O handling, considering Type-4 functional similarity in network communication.
- 共享行为: Both open a URL connection and read input stream.；Both handle IO exceptions.；Both use StringBuilder for constructing URLs.
- 行为差异: Function A sends a generic request to a servlet and returns empty string; Function B performs user registration and returns boolean.；Function A compresses data with GZIP and uses XML parsing; Function B hashes password and interacts with a database.；Function B includes multiple additional steps like setting authorities, generating hash, and sending email.
- 修正建议: Incorporate dataflow or control-flow analysis to capture the shared I/O pattern.；Use contrastive learning with coarse-grained clone labels to better recognize partial functional similarity.；Add attention to structural (AST) features to abstract away specific entity names.

### case_id=5386 FP lexical_or_api_overlap

- 方法: `getVersion` vs `run`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Retrieves the version string from a remote URL and returns it, returning null on failure.
- B 摘要: Reads a remote URL content line by line, extracting version, URL, and additional info into fields, and notifies listeners; handles specific IO exceptions with French error messages.
- 静态失败原因: The static model likely focused on structural similarities such as both having a try block with BufferedReader, InputStreamReader, URL, and readLine() loop, and both closing the buffer. These API-level overlaps may have misled the model into thinking they are similar, despite different purposes and outputs.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled as non-clone because the functions have different method signatures, different return types, and different overall functionality beyond just reading from a URL. BCB typically requires significant semantic overlap for Type-3/4 clones.
- 共享行为: Both read from a URL using BufferedReader；Both catch exceptions during IO
- 行为差异: Function A returns a single string; Function B populates multiple fields and has side effects；Function A catches generic Exception; Function B catches IOException and processes specific error messages；Function B has a finally block that triggers listeners; Function A does not；Function A is static; Function B is an instance method overriding Runnable.run()
- 修正建议: Incorporate more semantic features like method signature, return type, and data flow；Use a model that captures long-range dependencies to distinguish different uses of the same APIs；Add contrastive training examples where similar API usage corresponds to different intents

### case_id=5387 FN partial_functionality

- 方法: `copyResource` vs `doRequest`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource (file or URL) to a destination file by streaming bytes.
- B 摘要: Handles an HTTP request by streaming a resource to the response output stream.
- 静态失败原因: The model likely relied on lexical overlap (low Jaccard) and structural differences (different control flow, exception handling, and method signatures), missing the high-level functional similarity of stream copying. The core behavior is implemented differently (while loop vs IOUtils), making it hard for structure-based models.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB labels this as clone because both methods share the core pattern of opening a resource input stream and copying it to an output stream, despite contextual differences. This reflects BCB's acceptance of partial functionality similarity.
- 共享行为: Both open an input stream from a resource；Both copy the input stream to an output stream
- 行为差异: A writes to a local file, B writes to HTTP response；A uses byte-by-byte loop, B uses IOUtils.copyAndClose；A throws generic Exception, B throws ServletException；B includes alias checking and MIME type setting
- 修正建议: Enhance models with dataflow analysis to recognize stream copy patterns；Incorporate call-graph context to identify common utility operations；Use subgraph matching for I/O-related behaviors

### case_id=5388 FN benchmark_preference_bias

- 方法: `main` vs `startScript`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Constructs a POST request with parameters to a RenRen API and prints the response.
- B 摘要: Reads a script from a URL and appends it to a dialog object.
- 静态失败原因: The model likely focused on the different APIs (RenRen vs URL) and control flow, missing the underlying pattern; low token overlap also hindered similarity.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may label as clone due to similar structure of opening a URL, reading lines, and handling IO, despite different purposes (Type-4 clone).
- 共享行为: Both open a URL and read lines from its input stream
- 行为差异: Function A sends a POST request with many parameters; Function B just reads a URL；Function A prints the response; Function B appends to a dialog script；Function A uses explicit HTTP connection and POST method; Function B uses URL.openStream()
- 修正建议: Train with more diverse Type-4 examples；Incorporate high-level semantic abstractions like 'URL reading'

### case_id=5389 FN benchmark_preference_bias

- 方法: `modifyApplicationMessage` vs `buildDeb`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Modifies a locale-specific properties file by updating or adding a key-value pair.
- B 摘要: Constructs a deb archive file by writing header entries and copying control and data files.
- 静态失败原因: The model correctly identified non-clone; the BCB label appears to be an outlier, making this a false positive in the benchmark rather than a model failure.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have incorrectly considered both as 'file manipulation' tasks with similar control flow, or there may be a labeling error in the benchmark.
- 共享行为: Both perform file I/O operations (read, write)；Both use InputStream/OutputStream and loops for data transfer
- 行为差异: A processes text lines with string splitting and substitution; B writes binary archive headers and raw file contents；A handles missing files by copying a template; B does not handle missing files；A throws Exception; B throws IOException；A is instance method; B is static
- 修正建议: Review BCB annotation for this pair; if confirmed non-clone, remove from positive set.；If keeping, consider as Type-4 but clearly document the rationale.

### case_id=5390 FN partial_functionality

- 方法: `main` vs `copyLogic`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a URL and extracts all zip entries to files.
- B 摘要: Copies a single class file from one path to another using FileChannel.
- 静态失败原因: Static BERT likely focused on low token overlap and different API calls (ZipInputStream vs FileChannel), missing the high-level semantic equivalence of copying data from input to output.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as 'copy file' operations despite different sources and methods, emphasizing functional similarity over API details.
- 共享行为: Both read data from an input source and write it to an output file.；Both perform file I/O operations with exception handling.
- 行为差异: A reads from a network URL and processes a zip archive, while B reads from a local file and copies a single file.；A uses ZipInputStream and writes multiple files, B uses FileChannel.transferTo for a single copy.；A prints extraction progress, B updates state machine states.
- 修正建议: Enhance model to recognize high-level data flow patterns like 'read from input, write to output'.；Incorporate program dependency graphs or dataflow analysis to abstract away API specifics.

### case_id=5391 FP lexical_or_api_overlap

- 方法: `run` vs `downloadFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.85`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads lines from a URL, parses first two lines as version and url, appends rest to information string, and notifies listeners.
- B 摘要: Downloads a file from a URL to a destination path, writing bytes in buffer and reporting progress via MessageFrame.
- 静态失败原因: The model likely relied on lexical and API-level overlap (URL, InputStream) and ignored the divergent data flow and output behavior, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely considered them non-clones because the core functionalities are distinct (metadata parsing vs file download) despite sharing URL reading. The partial overlap is too generic for a Type-4 clone.
- 共享行为: Both open a URL connection and read data from it
- 行为差异: A parses text lines into fields; B writes binary data directly to a file；A updates internal fields and notifies listeners; B reports download progress and returns boolean；A handles specific errors with localized messages; B throws Exception on error
- 修正建议: Include data flow analysis to distinguish reading vs writing operations；Use graph-based models to capture control flow and output dependencies；Augment training with examples that have similar APIs but different semantics

### case_id=5392 FN partial_functionality

- 方法: `loadDefaultSettings` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Loads default configuration from classpath resource and writes it to a specified file.
- B 摘要: Downloads a KMZ file from a URL, extracts its zip entries, and writes each entry to the filesystem.
- 静态失败原因: Static models rely on token overlap and method names; the low Jaccard score and different identifiers overshadow the abstract stream-copy pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as stream-based I/O operations that transfer data from a source to a destination, accepting broad Type-3 or Type-4 similarity despite different domain logic.
- 共享行为: Both functions read from an input stream and write to an output stream；Both involve stream I/O and closing streams
- 行为差异: A copies a single stream to a file; B extracts multiple zip entries；A uses IOUtils.copy; B manually reads chunks；A has try-catch-finally; B throws Exception without finally；A reads from classpath; B reads from HTTP URL
- 修正建议: Incorporate dataflow or control flow features to capture abstract I/O patterns；Use structure-based metrics like AST or graph similarity

### case_id=5393 FN benchmark_preference_bias

- 方法: `downloadFile` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a file from S3, decompresses and decrypts it, saves to a temp file, then moves to target.
- B 摘要: Handles Eclipse launch configuration for a NexOpen project, validates project structure, processes pom.xml files, sets properties, and schedules an install action.
- 静态失败原因: Static model likely correctly predicted non-clone; BCB label may be erroneous due to benchmark preference bias.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have considered them clones due to superficial similarity like both using IOUtils.copy and exception handling, or due to annotation error.
- 共享行为: Both involve file I/O operations using IOUtils.；Both handle IOException and use try-finally for cleanup.
- 行为差异: Different domains: S3 file download vs Eclipse project launch configuration.；Different operations: decompression/decryption vs XML parsing and project management.；Different control flows and external dependencies.
- 修正建议: Review BCB annotation guidelines for consistency.；Improve static model to better capture benchmark biases.

### case_id=5394 FN benchmark_preference_bias

- 方法: `doGet` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Handles HTTP GET request to display a portal page, including page lookup, authorization, logging, and caching response to a file.
- B 摘要: Copies a file to a destination directory using a buffer.
- 静态失败原因: Static models like CodeBERT rely on token and structure similarity; low Jaccard (0.075) and different control flow lead to a non-clone prediction. The model correctly identifies the semantic difference, so this is a case where the BCB label itself is questionable.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might consider the file caching step in A as similar to file copying, but this is a minor sub-task in A's overall functionality. Typically BCB would not deem such a mismatch as a clone, so the label may be an annotation error or a very broad Type-4 interpretation.
- 共享行为: Both perform file I/O operations (reading/writing files).；Both include exception handling with logging or error messages.
- 行为差异: Function A is a complex web request handler with business logic (page retrieval, permissions, caching), while B is a simple file copy utility.；Function A deals with HTTP requests, user sessions, and page objects; B only handles file streams.
- 修正建议: Consider that the BCB label may be incorrect; re-evaluate annotation guidelines.；Incorporate high-level semantic understanding (e.g., program tasks) to handle cases with minimal token overlap but shared sub-functionality.；Use dynamic analysis or documentation to capture true intent.

### case_id=5395 FN benchmark_preference_bias

- 方法: `doGet` vs `getFileContentAsString`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.6`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Handles HTTP GET request to retrieve and render a page with logging, permission checks, and caching.
- B 摘要: Reads a file from classpath or filesystem and returns its content as a string.
- 静态失败原因: The static BERT model correctly predicted non-clone because the token Jaccard is very low (0.044) and the API usage patterns diverge significantly, leading to a low similarity score.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled as clone due to superficial similarities like both using try-catch, handling I/O, and being part of a web application, but the core functionality is completely different.
- 共享行为: Both involve reading some input (page parameter vs file path)；Both have exception handling；Both produce a string output (one writes to response, one returns)
- 行为差异: Function A is a complex servlet doGet method with page rendering logic；Function B is a simple utility to read file content into string；Function A includes user permission checks, caching, and statistics; function B does not；Function A outputs to HTTP response; function B returns a string
- 修正建议: Validate BCB annotations with human judgment for pairs with low lexical overlap；Incorporate behavioral analysis beyond lexical and syntactic matching

### case_id=5396 FN partial_functionality

- 方法: `modifyApplicationMessage` vs `persist`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.4`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Modifies or adds a message in a locale-specific properties file, creating the file if needed.
- B 摘要: Persists the input stream of a FreeFormConfigurable to a file with a given relative path.
- 静态失败原因: Static models rely on lexical and structural similarity; low token Jaccard and different method names/parameters led to a non-clone prediction, missing the broad file-writing commonality.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this as a clone due to both functions ultimately writing to a file, accepting Type-4 similarity where high-level functionality (file output) overlaps despite different details.
- 共享行为: Both write data to a file on the filesystem.
- 行为差异: Code A reads and parses a properties file, Code B just copies a stream.；Code A handles locale-specific file creation and message modification, Code B is generic persistence.；Code A involves reading and writing text lines, Code B uses binary stream copy.
- 修正建议: Incorporate high-level I/O operation detection (e.g., writing to file) beyond exact token matching.；Use flow-aware features to recognize that both functions write to files using different mechanisms.；Add training data with partial similarity labels to capture such cases.

### case_id=5397 FN benchmark_preference_bias

- 方法: `copy` vs `modifyApplicationMessage`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Copies a file from source to destination using a buffer.
- B 摘要: Modifies a specific message in a locale-specific properties file, creating it from a template if needed.
- 静态失败原因: Static BERT/GraphCodeBERT models likely relied on low token overlap (Jaccard 0.18) and different method names, correctly predicting non-clone under strict semantics, but missing BCB's broad interpretation.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may label this as a clone due to both functions performing file I/O operations with similar loop structures (read-write), despite different purposes.
- 共享行为: Both involve reading from a file and writing to a file
- 行为差异: Function A is a generic file copy; Function B is a context-specific property modification；Function B has conditional logic to create a file if missing and to update a specific key-value pair；Function B uses string tokenization and line-by-line processing; Function A uses byte buffer
- 修正建议: Incorporate more abstract function-level semantics beyond token overlap；Use dataflow analysis to distinguish generic I/O from specific property modification

### case_id=5398 FN partial_functionality

- 方法: `copyResource` vs `doImageProcess`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource from a URL or file to a local destination file using byte-by-byte stream copying.
- B 摘要: Processes an HTTP image request by copying an image stream to the response output stream, optionally resizing the image.
- 静态失败原因: Static BERT models rely on token overlap and surface-level API patterns. Here token Jaccard is low (0.208), and the functions use different APIs (e.g., IOUtils.copy vs byte loop, FileOutputStream vs response.getOutputStream), obscuring the underlying semantic similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels pairs as clones if they share core stream-copying functionality, even with different contexts (file vs HTTP). Broad functional similarity (Type-4) is accepted.
- 共享行为: Both read from an input stream (from a URL or file) and write to an output stream (file or response).；Both throw exceptions when the source cannot be opened.；Both close the streams after copying.
- 行为差异: A writes to a file output stream; B writes to an HTTP response output stream.；A copies byte-by-byte; B uses IOUtils.copy or byte array conversion with optional resizing.；B sets HTTP response headers (content type, content length) and may resize images.；B flushes the output stream after writing; A does not flush explicitly.
- 修正建议: Use dataflow analysis to abstract stream-copying patterns regardless of specific APIs.；Train with contrastive examples of stream-copying in different contexts (file, network, HTTP).；Incorporate program slicing to isolate the core copying logic from non-essential processing.

### case_id=5399 FN partial_functionality

- 方法: `read` vs `read`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a camera log from a URL, parses each line into a CameraLogRecord, adds to a list, sorts the list, and logs progress.
- B 摘要: Reads from a URL or file, opens an input stream, delegates reading to another method, and returns a status code.
- 静态失败原因: Static BERT models rely on token overlap and structural similarity; low Jaccard (0.25) and different method signatures/control flows led to predicting non-clone, missing the conceptual URL reading similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as functions that read from a URL, a common core operation, and ignore the differing downstream processing, thus labeling them as clones.
- 共享行为: Both read data from a URL；Both use try-catch for IOException；Both use logging for info messages
- 行为差异: A parses each line into CameraLogRecord; B delegates reading to another method；A sorts the records after reading; B returns a status int；B supports file input in addition to URL；A logs bad records individually; B sets a status on error
- 修正建议: Incorporate data flow analysis to capture shared API calls like url.openStream()；Use abstract representations of I/O operations；Train on broader clone types including partial functionality matches

### case_id=5400 FN benchmark_preference_bias

- 方法: `copyFile` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Copies a file from source to target using FileChannel.transferTo.
- B 摘要: Builds a site for editing by reading XML, transforming it with XSLT, and writing multiple output files with additional processing.
- 静态失败原因: Static BERT models rely on token overlap and local context; with a very low Jaccard similarity (0.048) and function B being extremely long with complex control flow, the model likely failed to recognize any semantic relationship, defaulting to non-clone.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB likely labeled this as a clone based on a broad interpretation of Type-4 (functional similarity) where both involve file copying operations, but this is weak; the labeling may be erroneous or due to annotation bias.
- 共享行为: Both perform file I/O operations (read and write files)；Both throw IOException
- 行为差异: A is a simple single-file copy; B is a complex multi-file site generation with XML transformation and string manipulation；A uses NIO FileChannel; B uses FileInputStream, FileWriter, and custom file system utilities；B includes extensive error handling, debugging traces, and parameter handling absent in A；The overall functionality and purpose are completely different
- 修正建议: Consider using semantic-based clone detection that captures functional similarity beyond token overlap；Incorporate hierarchical or structural matching to identify partial functionality clones；Use data-flow analysis to detect common I/O patterns

### case_id=5401 FP boilerplate_overlap

- 方法: `run` vs `postData`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Downloads a tile from a URL, parses GeoJSON, extracts geometries, and adds them to a data source.
- B 摘要: Sends a POST request with data to a URL and discards the response.
- 静态失败原因: Static BERT may have over-weighted common API calls (URL, openStream, BufferedReader) and structural patterns (try-catch, read loop), ignoring the different HTTP methods and the presence of geometry processing in A. The model likely considered the I/O boilerplate as strong evidence of similarity.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled as non-clone because the core functionality is entirely different: A is a tile loader with geometry processing, B is a generic HTTP POST utility. Despite shared I/O patterns, the semantic purpose and data handling are distinct, fitting Type-4 or non-clone.
- 共享行为: Both open URL connections and read input streams；Both handle URLs and use BufferedReader；Both may perform network I/O
- 行为差异: A performs a GET request (implicitly), B performs a POST request with output；A processes and uses the response (parses GeoJSON), B discards the response；A has synchronization and key management, B does not；A includes complex geometry processing, B is simple
- 修正建议: Incorporate detection of HTTP method (GET vs POST) as a feature；Analyze whether the response is consumed or discarded；Consider data flow beyond I/O to distinguish data processing logic；Use control flow and data dependency graphs to differentiate

### case_id=5402 FP lexical_or_api_overlap

- 方法: `callApiPost` vs `SRWGuiClient`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Sends an HTTP POST request to a given API URL with parameters, checks response code, and returns the response stream.
- B 摘要: Constructs a Swing GUI browser window that fetches an XML/HTML page from a URL, optionally transforms via XSLT, and displays it.
- 静态失败原因: The static model likely overfitted on surface-level lexical overlaps such as 'URL url = new URL(...)', 'IOException', 'BufferedReader', and try-catch structures, ignoring the vast differences in logic and purpose. The model may lack understanding of long-range semantic context and the different roles of the functions.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone (0) because the functions have no functional similarity; one is an HTTP client method and the other is a GUI constructor. Despite both using URL and I/O, the overall purposes are completely different.
- 共享行为: Both use URL to open connections and handle I/O exceptions；Both involve reading data from a URL；Both have try-catch blocks for IOException
- 行为差异: Function A performs an HTTP POST request with parameters; Function B constructs a GUI and reads/processes HTML/XML content；Function A checks response code and throws exception on mismatch; Function B displays content in JEditorPane and handles TransformerException；Function A writes to output stream; Function B reads from input stream and processes lines；Function A returns InputStream; Function B returns void and sets up GUI
- 修正建议: Improve training with more diverse negative pairs that share API usage but differ in intent；Incorporate structural or data flow analysis to distinguish between different high-level tasks；Use contrastive learning to better separate functions with similar low-level operations but different goals

### case_id=5403 FN benchmark_preference_bias

- 方法: `getEncoding` vs `httpRequestByPOST`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Opens a URL connection, inspects headers and HTML content to extract and return the character encoding, with fallback to a default.
- B 摘要: Performs an HTTP POST request with parameters, reads and returns the response body as a string, handling errors by setting instance fields and returning null.
- 静态失败原因: The static model correctly identified the pair as non-clones due to low lexical and semantic overlap, but the BCB benchmark labeled them as clones. This discrepancy suggests benchmark bias or annotation error in BCB.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: Might be considered clones under a very broad interpretation of 'HTTP-related I/O operations' but the core functionality (encoding detection vs. generic POST response retrieval) is distinct. The BCB annotation may have been based on superficial structural overlap (try-finally, BufferedReader read loop) rather than semantic equivalence.
- 共享行为: Both involve opening an HTTP connection and reading from an InputStream using BufferedReader.；Both handle IOException and close resources.
- 行为差异: Function A reads headers and scans HTML for encoding; Function B sends a POST request and reads the entire response.；Function A returns a single encoding string; Function B returns the full response body or null on error.；Function A uses URLConnection (typically GET); Function B explicitly uses HTTP POST.；Function A throws IOException; Function B catches and records errors via instance fields.
- 修正建议: Ignore this pair as a BCB false positive; include more diverse non-clone pairs in training to avoid over-generalizing HTTP boilerplate.；Enhance model sensitivity to functional purpose vs. structural patterns.

### case_id=5404 FN lexical_or_api_overlap

- 方法: `sendExceptionToServer` vs `fetchUrl`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.6`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends exception details to a server via HTTP POST and prints the server response.
- B 摘要: Fetches the content of a URL via HTTP GET and returns it as a string.
- 静态失败原因: Low syntactic overlap (token Jaccard 0.21) and different control flow (POST vs GET, writing before reading) cause the model to focus on surface-level differences. The constant strings and API calls in A not present in B dilute similarity. The model fails to abstract the shared high-level I/O pattern.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely labels this as a clone due to broad Type-4 semantic similarity: both perform network I/O to interact with a server, read response line by line, and use a common pattern (URL, BufferedReader, StringBuilder, try-catch). Despite different purposes, the core pattern of opening a connection and reading lines is shared.
- 共享行为: Open a URL connection；Read lines using BufferedReader；Use StringBuilder to accumulate text；Handle IOException with try-catch
- 行为差异: A uses POST with URL-encoded parameters; B uses GET without parameters；A writes data to output stream before reading; B only reads；A has conditional parameters for config and problem; B has no parameters；A prints to console and returns void; B returns the fetched content
- 修正建议: Use dataflow-aware models that capture common I/O patterns；Augment training with semantically similar but syntactically diverse network operations；Incorporate structural abstractions for URL handling and line reading

### case_id=5405 FP lexical_or_api_overlap

- 方法: `readRemoteFile` vs `downloadFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a remote file from a hardcoded URL and returns its content as a string, line by line.
- B 摘要: Downloads a file from a given URL to a local destination file with progress reporting, returning success status.
- 静态失败原因: Static BERT/GraphCodeBERT may have been misled by lexical overlap of terms like 'URL', 'InputStream', 'read', etc., and the overall 'download' concept, ignoring the distinct output behaviors and control flow differences.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels functions as clones only when they perform essentially the same task. Here, one reads a remote file into a string (in-memory) and the other downloads to a file (persistent storage). Despite similar API usage, the high-level functionality differs significantly, so BCB annotators judged them non-clones.
- 共享行为: Both open a connection to a remote URL；Both read data from the input stream；Both handle IO exceptions
- 行为差异: Function A returns the file content as a string; Function B writes the content to a file；Function A reads text line-by-line; Function B reads binary in buffers；Function B reports download progress; A does not；Different input parameters and return types
- 修正建议: Enhance model to consider output types and side effects；Incorporate data-flow analysis to distinguish between returning content vs. writing to file

### case_id=5406 FN partial_functionality

- 方法: `httpRequestByPOST` vs `readURL`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends an HTTP POST request with parameters, reads the response lines into a string, returns the string or null with error codes.
- B 摘要: Opens a URL connection, reads lines and prints them to stdout, handles exceptions and closes streams.
- 静态失败原因: Low token Jaccard (0.2) and different API calls (HttpPost vs URL.openStream) mislead the model; it lacks understanding that both are URL reading tasks.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider them similar because both perform the high-level task of reading data from a URL line by line, despite different HTTP methods, error handling, and output.
- 共享行为: Both read lines from a URL-based input stream using BufferedReader
- 行为差异: A uses HTTP POST, B uses GET (via openStream)；A returns the concatenated response string, B prints lines to console；A sets error fields and returns null on failure, B prints stack trace；B has finally block for stream cleanup, A does not close all resources in finally
- 修正建议: Improve semantic matching of URL reading across different APIs；Incorporate dataflow analysis to identify shared I/O patterns；Use API mapping or synonym detection for HTTP client vs URL.openStream

### case_id=5407 FN partial_functionality

- 方法: `copy` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a file from source to destination using NIO FileChannel, with null checks and stream closing.
- B 摘要: Builds a website for editing by processing multiple XML files, applying XSLT transformations, and writing output files, with extensive error handling.
- 静态失败原因: Static models like GraphCodeBERT rely on lexical and structural similarity; the low token Jaccard (0.087), different method names, and vastly different code lengths caused the model to predict non-clone.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have incorrectly labeled as clone due to superficial similarity in using FileInputStream and exception handling, despite radically different overall functionality.
- 共享行为: Both use FileInputStream to read files.；Both throw IOException.；Both have try-finally blocks for resource cleanup.
- 行为差异: A performs a simple file copy; B is a complex iterative site builder.；A uses FileChannel.transferFrom; B uses FileReader/FileWriter and custom file system operations.；A has null checks for parameters; B does not.；B involves multiple files, string transformations, and conditional logic; A is straightforward.
- 修正建议: Incorporate dataflow analysis to distinguish simple file copy from complex transformations.；Use semantic similarity models that capture long-range dependencies and overall purpose.

### case_id=5408 FN lexical_or_api_overlap

- 方法: `combineJs` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.6`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Combines multiple JavaScript files from URLs into a single minified/concatenated file and updates an HTML element's src attribute.
- B 摘要: Retrieves a resource by name, caching it locally, and returns an InputStream to the cached file.
- 静态失败原因: Static BERT models may overemphasize token overlap of common API calls (URL, File, InputStream) while missing the distinct control flows and return types that differentiate the functions.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may have labeled this as a clone due to shared low-level operations (URL handling, file I/O) and the overall theme of downloading and storing web resources, despite different high-level purposes.
- 共享行为: Both open URL connections and read input streams.；Both write data to local files.；Both use temporary or cache directories and handle file creation.；Both include exception handling and resource cleanup.
- 行为差异: A combines multiple files and optionally minifies JavaScript; B retrieves a single resource and caches it.；A returns an Element with updated src; B returns an InputStream.；A uses JavaScriptCompressor and modifies DOM; B uses HTTP caching logic with If-Modified-Since.；A processes a list of Node elements; B takes a single resource name string.
- 修正建议: Incorporate method signature and return type information into the model.；Focus on high-level task identification rather than just API usage patterns.；Use data augmentation with diverse semantic clones to reduce reliance on lexical overlap.

### case_id=5409 FN boilerplate_overlap

- 方法: `fileDownload` vs `scrapeForIsbns`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.55`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a file from a given URL and saves it to a specified directory.
- B 摘要: Scrapes a URL for ISBN-10 patterns, counts matches, and returns the count.
- 静态失败原因: Static BERT/GraphCodeBERT likely relied on low lexical overlap (token Jaccard 0.14) and different method names, missing the shared boilerplate code structure.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may have labeled this as a clone due to the common pattern of reading from a URL via input stream, despite different final purposes.
- 共享行为: Both open a URL and read input via BufferedReader using InputStreamReader
- 行为差异: Function A writes bytes to a file; Function B reads lines and applies regex；Function A has no retry logic; Function B retries on connection exceptions；Function A returns void; Function B returns an integer count；Function A takes a String URL; Function B takes a URL object
- 修正建议: Incorporate structural similarity features；Add context-aware representations that capture common I/O patterns

### case_id=5410 FN boilerplate_overlap

- 方法: `getEncoding` vs `invoke`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Extracts character encoding from an HTTP response by checking headers and body content.
- B 摘要: Invokes a remote service method via HTTP POST and deserializes the JSON response.
- 静态失败原因: Static models may focus on token overlap (e.g., BufferedReader, line) and miss high-level semantic differences, classifying them as non-clones when they are actually semantically distinct.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely considered the broad Type-4 clone category due to both methods involving HTTP I/O and line-by-line reading, despite fundamentally different functionality.
- 共享行为: Both involve making HTTP connections and reading response streams.；Both use BufferedReader to read lines from an InputStream.；Both handle I/O exceptions.
- 行为差异: getEncoding parses HTTP headers and body for charset information; invoke sends a POST request and processes the response body as JSON.；getEncoding returns a String encoding; invoke returns a deserialized Object and includes retry logic.；getEncoding does not modify the request; invoke constructs an HTTP POST with entity and sets encoding explicitly.
- 修正建议: Incorporate data-flow analysis to capture the purpose of data processing (e.g., extracting a substring vs. deserializing).；Use attention mechanisms that better capture structural differences in control flow.；Enrich training data with more examples of I/O operations with different end goals.

### case_id=5411 FN partial_functionality

- 方法: `main` vs `encodeFileToFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Extracts files from a ZIP stream obtained from a URL and saves them to local files.
- B 摘要: Base64-decodes a file and writes the decoded content to another file.
- 静态失败原因: Static BERT/GraphCodeBERT may have missed this due to low token overlap (0.226), different method names and comments, and different import patterns (URL vs Base64). The models may rely on lexical similarity and may not capture the abstract stream copy pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider these clones because they are both instances of a general pattern: reading data from a source, applying a transformation, and writing to a destination. They share structural similarity in stream handling, buffer copying, and resource management, which fits broad Type-3/Type-4 clone definitions.
- 共享行为: Both read bytes from an input stream and write to an output stream.
- 行为差异: Different input sources: URL vs file；Different transformations: ZIP extraction vs Base64 decoding；Different output destinations: entry-based vs fixed output file；Different error handling: throws exceptions vs returns boolean with try-catch
- 修正建议: Improve representation of structural stream processing patterns；Use graph-based models that capture control flow and data flow；Incorporate knowledge of common transformations like encoding/compression

### case_id=5412 FP boilerplate_overlap

- 方法: `actionPerformed` vs `downloadFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Handles UI action commands for setting GraphViz, ImageMagick paths, and various preferences using file choosers and saving to a controller.
- B 摘要: Downloads a file from S3, decompresses and decrypts it, then copies to a local target file, with error handling.
- 静态失败原因: Static BERT/GraphCodeBERT may have focused on common API tokens like File, IOException, try-catch, and file chooser usage, overlooking the different overall semantics and control flow, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BigCloneBench typically labels non-clones for functionally unrelated methods; this pair has no shared functionality beyond basic file/IO operations, so BCB correctly marks non-clone.
- 共享行为: None significant
- 行为差异: Different purpose: UI event handling vs. file download from S3；Different logic: file chooser dialogs vs. stream decryption and copy；Different scope: large method with many UI updates vs. small focused method；Different input/output: ActionEvent and side effects vs. File and S3 key, returns void but writes file
- 修正建议: Incorporate data flow analysis to distinguish event-driven UI updates from data processing pipelines；Train on more diverse examples to reduce bias towards common IO patterns；Use contrastive learning to emphasize functional differences

### case_id=5413 FN partial_functionality

- 方法: `getFile` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies its wsdlsoap:address element, and saves it to a temp directory, returning the file path.
- B 摘要: Copies a file from source to destination using FileChannel.
- 静态失败原因: Static BERT models may have been misled by the presence of common I/O keywords like FileChannel, transferTo, openStream, etc., without understanding the higher-level task differences.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB labeled it as clone possibly due to both using FileChannel transfer, but this overlooks the vast differences in purpose and context.
- 共享行为: Both perform file I/O operations using streams and channels.
- 行为差异: Function_a downloads from URL and modifies XML, while Function_b merely copies a local file.；Function_a returns a String, Function_b returns void.；Function_a has extensive logging and exception handling, Function_b only prints stack trace.；Function_a checks file existence and renames temporary files, Function_b does not.
- 修正建议: Incorporate structural and semantic understanding of the overall method intent.；Use dataflow analysis to capture the full purpose.

### case_id=5414 FN benchmark_preference_bias

- 方法: `readData` vs `File2String`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.4`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Initializes multiple hash sets and a hash map from comma-separated strings stored in global variables.
- B 摘要: Reads a file from the file system or classpath and returns its complete content as a single string.
- 静态失败原因: The static model correctly identified the significant structural and semantic differences, but BCB's annotation may have been overly lenient, classifying this as a false negative relative to the benchmark label.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider both as 'data loading' utility methods under a broad Type-4 clone definition, ignoring the vast implementation differences and focusing on the abstract goal of reading and organizing data.
- 共享行为: Both involve processing input data to populate data structures.
- 行为差异: Function A operates on in-memory string tokens with no I/O; Function B handles file I/O and resource loading.；Function A modifies global state; Function B returns a value and exits on failure.；Function A uses StringTokenizer; Function B uses BufferedReader and InputStream.；Function A has a large truncated section with complex parsing logic; Function B is relatively simple.
- 修正建议: Re-evaluate the BCB label to ensure it aligns with standard Type-3/Type-4 criteria; consider adding additional context or narrowing clone definition.

### case_id=5415 FP boilerplate_overlap

- 方法: `run` vs `import_hints`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.85`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Loads tile data from a URL or file, parses geometric features, and adds them to a data source for map rendering.
- B 摘要: Imports puzzle hints from a file or URL, parsing integer tokens to place and rotate pieces on a board.
- 静态失败原因: Static models like BERT or GraphCodeBERT may over-rely on lexical and structural overlap (common tokens like 'URL', 'BufferedReader', 'InputStream', 'readLine', 'IOException') and miss the semantic divergence in the functional core after the initial IO setup.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the core functionality is completely different (map tile loading vs puzzle hint importing), despite some boilerplate IO similarity. The annotations in BCB generally require significant functional overlap, which is absent here.
- 共享行为: Both read from a URL or file using InputStream and BufferedReader.；Both parse input line by line and handle IOException.；Both have try-catch blocks for IO errors.
- 行为差异: Function A deals with tile geometry (VectorTile, GeometryCollection), while B deals with puzzle pieces and board placement.；A uses synchronized blocks for managing HTTP requests; B does not.；A returns void; B returns boolean true/false.；A has multiple catch blocks (FileNotFoundException, IOException); B has a single IOException catch.
- 修正建议: Use data-flow analysis to distinguish between boilerplate IO code and domain-specific processing.；Incorporate type or API-level semantics to differentiate geometry vs puzzle operations.；Train or fine-tune on more diverse clones to reduce weight on common library usage patterns.

### case_id=5416 FP lexical_or_api_overlap

- 方法: `getUser` vs `readReferenceText`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Loads user from DAO, or parses configuration file to find and persist user if not in DAO.
- B 摘要: Reads a reference text file from a bundle URL and returns its content as a string.
- 静态失败原因: Static BERT may have overemphasized lexical and API overlap (URL, BufferedReader, readLine) and similar control flow, missing the semantic differences in data processing and overall goal.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this non-clone because the functions have distinct purposes (user lookup vs text reading) and different return types and error semantics, despite sharing a common I/O pattern.
- 共享行为: Both open a URL and read lines using BufferedReader；Both iterate over lines until null
- 行为差异: A writes to DAO if user found; B builds string buffer；A returns User or null; B returns String or throws exception；A uses StringTokenizer with colon delimiter; B does not parse tokens；Error handling differs: A catches generic Exception and prints stack trace; B catches specific exceptions and logs
- 修正建议: Incorporate data flow and type information；Train on more diverse examples emphasizing semantic purpose over surface syntax

### case_id=5417 FN benchmark_preference_bias

- 方法: `main` vs `runDynusT`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `preference_memory_with_manual_audit`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Downloads a KMZ file from a URL and extracts its zip entries to the current directory.
- B 摘要: Copies required executable and model files to a temporary directory, runs the DynusT simulation, and optionally cleans up executables.
- 静态失败原因: The static model likely focused on low token overlap (0.059 Jaccard) and different domain-specific APIs (Zip vs ExeRunner), missing the abstract structural similarity in file handling loops that BCB prioritizes.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB often marks as clones when both functions exhibit similar high-level structural patterns like file I/O in loops, even if the specific file types and operations differ. The presence of loops, file copying/writing, and resource cleanup aligns with Type-3 or Type-4 clone definitions in BigCloneBench.
- 共享行为: Both perform file I/O operations in loops (iteration over zip entries or file lists).；Both involve file creation or copying with resource management (stream closing or file deletion).；Both output progress information (printing to console or logging).
- 行为差异: A deals with zip extraction from a remote URL; B copies local files and runs an external process.；A writes decompressed entries; B copies files and executes an executable.；A has no cleanup step; B optionally deletes exe files after execution.；A uses standard output; B uses a logger.
- 修正建议: Incorporate AST or control-flow-based features to capture structural patterns beyond lexical tokens.；Fine-tune the model on BCB's annotation guidelines that accept broad Type-3/4 clones.；Use dataflow analysis to detect common patterns like file I/O loops.

### case_id=5418 FN partial_functionality

- 方法: `read` vs `getNetworkServersIPs`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Opens a file or URL and reads its content, returning a status code.
- B 摘要: Connects to a URL, reads lines, and extracts server IP addresses from a specific format, returning a vector of IPs.
- 静态失败原因: Static BERT models like GraphCodeBERT rely heavily on token overlap and syntactic structure, which are low here (token Jaccard 0.204). The model likely focused on the different return types and detailed logic, missing the broader shared network I/O functionality.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label them as clones because both involve the common pattern of opening a URL, reading input, and processing it, which is considered a Type-4 semantic clone despite different specific purposes.
- 共享行为: Both open a URL connection and read input data from the network.
- 行为差异: Return type differs: int vs Vector<String>；Parsing logic differs: function A just reads all content, function B parses lines for specific markers.；Error handling differs: function A sets status variable, function B prints stack traces.；Input format handling differs: function A handles local files or URLs, function B only handles URLs with a specific format.
- 修正建议: Incorporate abstract API usage patterns (e.g., URL.openConnection, BufferedReader) as features.；Use data flow analysis to track that both involve reading from a network source.；Increase weight of structural similarities in exception handling and stream usage.

### case_id=5419 FN benchmark_preference_bias

- 方法: `readData` vs `postData`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Parses multiple comma-separated string variables into sets and a map for Tibetan transliteration initialization.
- B 摘要: Sends an HTTP POST request to a specified URL with given data and reads response.
- 静态失败原因: The static model correctly identified non-clone; the BCB label appears incorrect.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: Possible annotation error; the two functions share no meaningful similarity in purpose or logic.
- 行为差异: Function A initializes internal data structures from static strings; function B performs network I/O.；Function A has no parameters; function B takes parameters for URL and data.；Function A is static and modifies global state; function B is instance method and uses connection objects.；Function B handles protocol, host, form, data; function A parses tokens into categorized sets.
- 修正建议: Re-annotate the pair as non-clone.；If BCB label is considered ground truth, investigate whether there is hidden shared functionality (e.g., both process strings) but that seems insufficient.

### case_id=5420 FN boilerplate_overlap

- 方法: `getHTML` vs `parse`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.85`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Fetches HTML content from a given URL and optionally writes it to a file, returning the HTML string.
- B 摘要: Parses a dataset from a file or URL using tokenization, handling headers, types, and returns a DataSet object.
- 静态失败原因: The static BERT model likely focused on the low lexical overlap (Jaccard 0.103) and structural differences, missing the superficial similarity in using BufferedReader for I/O. It failed to recognize the broad functional similarity that BCB might have overemphasized.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may consider them clones because both involve reading from an external source and processing lines, which could be seen as a broad Type-4 (partial functionality) similarity, though the actual data processing and outputs are very different.
- 共享行为: Both read from an external source (URL or file) using BufferedReader.
- 行为差异: A reads raw text line-by-line; B uses StreamTokenizer for tokenized parsing.；A returns a raw HTML string; B returns a structured DataSet.；A optionally writes to a file; B does not write to a file.；B includes complex parsing logic (numbers, scientific notation, quotes); A simply appends lines.
- 修正建议: Incorporate dataflow analysis to identify common I/O patterns.；Use graph-based representations (e.g., AST with data edges) to capture similarities in external resource access.；Train with more diverse examples of partial functionality clones to balance lexical and semantic cues.

### case_id=5421 FN partial_functionality

- 方法: `truncate` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.75`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Compresses and archives an old log file into a zip backup, then deletes the original.
- B 摘要: Builds an HTML site for editing by transforming XML pages with XSLT and writing the output to files.
- 静态失败原因: Static BERT/GraphCodeBERT models rely on token overlap and structural patterns. The low Jaccard similarity and very different API calls (zip vs. XSLT) likely caused the model to predict non-clone. The model correctly identified the distinct semantics.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as file processing functions that read input and produce output, with similar boilerplate patterns like file stream handling, buffer usage, and logging, thus classifying as Type-4.
- 共享行为: Read and write files；Use try-catch-finally for resource management；Use buffers for I/O；Logging/debugging output
- 行为差异: Purpose: archiving vs. site generation；Input: single file vs. multiple pages and parameters；Output: zip file vs. multiple HTML files；Process: compression vs. XSLT transformation
- 修正建议: Include domain-specific context or high-level intent；Improve detection of functional differences beyond syntactic patterns

### case_id=5422 FN partial_functionality

- 方法: `doRawRequest` vs `runScript`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Makes a POST request with postData to a service URL and returns the response body as a string, reading line by line.
- B 摘要: Makes a GET request to a script URL relative to the applet codebase and returns the content as a string, reading byte by byte with error handling.
- 静态失败原因: The model saw low lexical overlap (token Jaccard 0.138) and focused on syntactic differences like different classes (URLConnection vs URL.openStream), different stream types, and different control flow. It likely missed the high-level semantic similarity of fetching URL content.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often considers Type-4 clones where the core task of fetching remote text content via URL is the same, tolerating differences in HTTP method, I/O details, and error handling.
- 共享行为: Both open a URL connection and read the entire response into a string.；Both perform network I/O to fetch text data from a URL.；Both return the fetched content as a String.
- 行为差异: A uses POST method with a payload; B uses GET without payload.；A reads line by line with BufferedReader; B reads byte by byte with BufferedInputStream.；A throws IOException; B catches all exceptions and returns 'error!'.；A uses StringBuilder; B uses string concatenation in a loop.
- 修正建议: Use contrastive learning to embed similar network I/O patterns closer.；Incorporate data-flow analysis to abstract away I/O details (e.g., treat any URL-to-string pattern as similar).；Generate training examples that pair GET and POST variants of the same base operation.

### case_id=5423 FN benchmark_preference_bias

- 方法: `doGet` vs `readAndRewrite`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Handles HTTP GET request to retrieve and display a portal page, with visibility checks, logging, and caching.
- B 摘要: Reads a DICOM image file, parses pixel data, and writes it to a new file with encoding.
- 静态失败原因: The static BERT/GraphCodeBERT model correctly predicted non-clone because of very low lexical overlap (Jaccard=0.039) and no shared semantic intent. The BCB label appears to be a misannotation.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as a clone based on a very broad interpretation of 'file I/O' or 'resource handling', but the functions are fundamentally different in domain and logic.
- 行为差异: Code A processes HTTP requests and responds with HTML; Code B processes DICOM image files.；Code A involves user authentication, page caching, and statistics; Code B involves pixel data reading/writing.；Code A uses Servlet API and portal-specific classes; Code B uses DICOM-specific libraries (DcmParser, Dataset, etc.).
- 修正建议: Re-evaluate BCB label for this pair; likely a false positive clone annotation.；Improve benchmark consistency by ensuring only semantically similar functions are labeled as clones.

### case_id=5424 FN partial_functionality

- 方法: `getResourceAsStream` vs `unzip`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a resource from a URL, caches it locally, and returns an InputStream.
- B 摘要: Extracts entries from a zip file to a target directory.
- 静态失败原因: Low token overlap (0.149), different vocabulary and structure; the model relies on lexical matching and local context, missing the high-level I/O pattern similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as 'file retrieval and storage' tasks, or annotators might have labeled based on broad Type-4 semantic similarity involving I/O patterns.
- 共享行为: Both perform file I/O: read from an input stream and write to output streams；Both create directories if they do not exist；Both use buffered streams
- 行为差异: Different data sources: network (HTTP) vs local zip file；Output is a single file vs multiple files；Function A includes caching logic; function B does not；Exception handling and logging differ
- 修正建议: Enhance model with data flow analysis to capture read-write operations；Use API call sequence embedding to detect similar I/O patterns；Incorporate control flow graph features for long-range dependencies

### case_id=5425 FN benchmark_preference_bias

- 方法: `writeFileType` vs `File2String`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.2`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Reads a file of URIs, skips initial lines, then for each URI fetches the web page content up to 100 lines, checks for ontology keywords, and writes classification to output file.
- B 摘要: Reads a file from filesystem or classpath and returns its entire content as a single string.
- 静态失败原因: Static BERT models focus on token-level overlap and local syntactic patterns; low Jaccard similarity (0.16) and lack of common key phrases led to prediction of non-clone, but BCB label expects a clone, so the model failed to capture potential deep semantic similarity based on file reading boilerplate.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider them clones due to broad Type-4 semantic similarity where functions share common I/O patterns and exception handling, but the core functionality differs significantly.
- 共享行为: Both use BufferedReader to read lines from an input source.；Both handle IOExceptions with try-catch blocks.；Both involve file I/O operations.
- 行为差异: A processes multiple URIs from an input file; B reads a single file.；A opens URL connections and checks for ontology keywords; B simply concatenates all lines.；A writes output to a file; B returns a string.；A has nested loops and conditional branching for ontology detection; B has a single read loop.
- 修正建议: Use dataflow analysis to differentiate core functionality from boilerplate.；Incorporate task-specific semantics via comment or method name understanding.；Training on broader definition of functional similarity may help.

### case_id=5426 FN boilerplate_overlap

- 方法: `register` vs `getXML`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Registers a user by encoding password, creating a forum user via HTTP request, persisting to DB, and sending confirmation email.
- B 摘要: Fetches XML from a servlet URL by making an HTTP request and reading the response line by line into a string.
- 静态失败原因: Token overlap is low (0.165), so static BERT likely focused on syntactic differences and missed the structural similarity in the I/O pattern that BCB annotators considered important.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: Despite different high-level functionality, both functions share a common I/O pattern (URL connection, BufferedReader read loop) that BCB may consider as Type-4 clone or partial functionality similarity.
- 共享行为: Both make HTTP requests and read response line by line using BufferedReader
- 行为差异: Different overall purposes: user registration vs XML retrieval；Different error handling (returns false/null vs throws exceptions)；One has database persistence and email sending, the other just returns a string
- 修正建议: Use models that capture control flow or data flow to recognize common patterns beyond token overlap；Incorporate structural similarity measures like AST path similarity

### case_id=5427 FP other

- 方法: `plainToMD` vs `perform`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Computes MD5 hash of an input string and returns its hexadecimal representation.
- B 摘要: Handles a web request to classify a concept, managing session, parameters, and external XML communication.
- 静态失败原因: The static model may have been misled by superficial structural similarities (e.g., both have loops, string building, exception handling) and lack of deep semantic understanding, leading to a false positive.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely labeled non-clone because the functions have completely different domains and no shared algorithmic behavior beyond trivial Java constructs.
- 共享行为: Both have loops and string concatenation operations；Both use try-catch for exception handling
- 行为差异: Function A performs cryptographic hashing; Function B performs web request processing and classification logic；Function A returns a hash string; Function B returns an ActionForward for request routing；Function A uses MessageDigest; Function B uses URL connections, session attributes, and multiple beans
- 修正建议: Incorporate more domain-aware training or contrastive learning to distinguish unrelated functionalities；Use longer-range context or whole-function graph representations to capture semantic intent

### case_id=5428 FN partial_functionality

- 方法: `doVersionCheck` vs `runScript`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a version check file from URL, parses version and build, compares with current build, and shows UI message.
- B 摘要: Downloads a script file from URL as a string and returns it; on failure returns error string.
- 静态失败原因: Static BERT/GraphCodeBERT likely focused on token-level differences (low Jaccard similarity) and missed the abstract structural similarity. The different method names, variable names, and processing logic obscured the common I/O pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considers this a Type-3 or Type-4 clone because both functions share the overall structure of fetching URL content and reading input stream, despite different specific data processing. The common pattern of try-catch, URL, InputStream, and reading loop is typical for broad clone annotation.
- 共享行为: Open URL connection；Read from input stream；Handle IO exceptions with catch block
- 行为差异: A reads lines with BufferedReader and parses specific properties; B reads raw bytes with BufferedInputStream and concatenates to string.；A performs version comparison and shows UI messages; B simply returns the data.；A closes the stream explicitly; B does not close the stream.；A takes a View parameter for UI interactions; B is a simple string method.
- 修正建议: Use abstract syntax tree (AST) or program dependency graph (PDG) to capture structural patterns.；Incorporate dataflow analysis to recognize common I/O operations.；Train on clone pairs with partial functional similarity to improve recognition of broad clones.

### case_id=5429 FP long_range_semantics

- 方法: `copy` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `static_summary_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Copy data from an InputStream to an OutputStream, handling exceptions and closing streams.
- B 摘要: Handle GUI action events to set various application preferences via a settings panel.
- 静态失败原因: Likely due to the extreme length of function B causing truncation or loss of semantic context, and possibly the presence of common boilerplate (e.g., try-catch, null checks) leading to false positive.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB labels these as non-clones because they perform entirely different tasks (stream copy vs. GUI event handling) with no shared functionality beyond basic Java constructs.
- 共享行为: Both are Java methods that handle exceptions (try-catch) and perform I/O operations (streams in A, file chooser in B).
- 行为差异: Function A copies stream data; Function B handles GUI events and updates preferences.；Function A is short and focused; Function B is long and handles multiple commands.；Function A uses IOUtils; Function B uses Swing components and custom preference API.
- 修正建议: Ensure proper truncation or chunking for long methods.；Use dataflow-based analysis to capture the overall intent.；Increase weight on structural differences.

### case_id=5430 FN partial_functionality

- 方法: `readData` vs `issueCommandToServer`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Reads comma-separated token lists from static strings and a file to populate sets and maps for Tibetan character processing.
- B 摘要: Sends an HTTP command with a JSON payload to a server and returns the response as a string.
- 静态失败原因: Static BERT models rely on token overlap and syntactic structure, which are very low (Jaccard 0.05) and semantically unrelated API calls, leading to a correct non-clone prediction despite BCB's broad labeling.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB annotators may have considered these clones as Type-4 because both functions read and process input data, albeit from different sources, fitting a broad partial functionality similarity.
- 共享行为: Both read input data from an external source (static strings/file vs HTTP response)；Both process input line by line (file reading in A, HTTP response in B)
- 行为差异: Source of input differs: static strings and local file vs remote HTTP server；Processing logic: populating multiple data structures vs returning a single response string；Return type: void vs String；Error handling: custom errors with File vs IOException
- 修正建议: Better to treat this as non-clone; if BCB style allows very broad Type-4, add more explicit annotation guidelines to avoid such pairs.；Use dataflow or semantic features to distinguish between file I/O and network I/O.

### case_id=5431 FP boilerplate_overlap

- 方法: `createPseudoUUID` vs `perform`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Generates a pseudo UUID by hashing a UID and local host address with MD5 and formatting as a hex string.
- B 摘要: Processes a Struts action request, builds XML data, sends it via HTTP, parses the response, and sets session attributes for display.
- 静态失败原因: The model likely overfocused on common boilerplate patterns (try-catch, StringBuffer, method length) and missed the completely different semantic intent due to limited representation of long-range dependencies or API usage.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would not consider them clones because they solve entirely different tasks with no functional overlap.
- 共享行为: Both use StringBuffer for string construction.；Both include try-catch blocks for exception handling.；Both involve I/O operations (network/file) but at a high level.
- 行为差异: A is a static utility for UUID generation; B is an action handler with complex web workflow.；A uses MessageDigest and hex conversion; B involves HTTP, XML parsing, and session management.；A returns a string; B returns an ActionForward based on status.；A has no external dependencies; B uses Struts, HTTP, and XML parsing.
- 修正建议: Incorporate data flow or program dependency analysis to distinguish core logic from boilerplate.；Train with more diverse negative examples that share syntactic structure but differ semantically.；Use graph-based representations (like AST or CFG) to capture structure rather than surface tokens.

### case_id=5432 FN partial_functionality

- 方法: `copyIconFiles` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies icon files (16x16 and 32x32) from local paths to a resources directory based on class annotations.
- B 摘要: Downloads a KMZ file from a URL, opens it as a ZIP archive, and extracts all entries to the current directory.
- 静态失败原因: Static BERT models rely heavily on token overlap and local syntax patterns; the low Jaccard similarity (0.1087) and different method names likely caused a non-clone prediction, missing the abstract I/O copying pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label as clone because both functions perform file copying/extraction using Java I/O streams, albeit with different sources and destinations, which could be considered Type-4 (functionally similar) under a loose interpretation.
- 共享行为: Both open input streams and output streams；Both copy data from an input source to an output destination；Both close streams after copying
- 行为差异: A copies from local files, B downloads from a remote URL；A uses FileChannel and file streams, B uses ZipInputStream and buffered streams；A copies two specific icon files, B extracts multiple archive entries；A constructs destination paths dynamically, B uses entry names directly
- 修正建议: Enhance model with data flow analysis to capture I/O operations；Include structural similarity focusing on stream usage patterns；Use fine-tuning on BCB's annotation criteria to better recognize functional similarity

### case_id=5433 FP boilerplate_overlap

- 方法: `main` vs `main`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Parses a Prolog file and generates adapter JAR for Prolog facts with command-line options.
- B 摘要: Compresses a file using GZip and produces a .gz file via command line.
- 静态失败原因: Static BERT models may focus on token-level similarities like the identical method signature, if-check for args, println usage, and try-catch patterns, overlooking the entirely different core functionality.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically requires significant functional overlap beyond boilerplate; the core logic differs entirely, so BCB likely considers this non-clone despite shared command-line structure.
- 共享行为: Both are command-line tools that check argument count and print usage on invalid input；Both read a file and handle IOExceptions with error messages
- 行为差异: Function A generates a JAR with adapter classes; Function B compresses a file to GZip format；Function A uses complex logic with parser, visitors, and class writing; B has simple read-write loop；Function A supports debug option; B has no options；Function A outputs multiple artifacts; B outputs one compressed file
- 修正建议: Incorporate dataflow or program dependence analysis to highlight core logic differences；Use detection methods that differentiate between boilerplate and domain-specific code

### case_id=5434 FP lexical_or_api_overlap

- 方法: `readData` vs `createButtonCopyToClipboard`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Initializes multiple hash sets and a map by tokenizing static string fields and reading a configuration file to populate various data structures for Tibetan and Sanskrit character handling.
- B 摘要: Creates a button in an SWT shell, configures its text and layout, and attaches a selection listener that copies an environment report to the clipboard.
- 静态失败原因: The low token Jaccard suggests the model did not rely on lexical overlap. The false positive may stem from both functions containing Java boilerplate (object creation, method calls on standard library classes) which confused the model into detecting spurious similarity in structure or API usage.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels emphasize functional equivalence or significant overlap. These two functions have no shared functionality or purpose, so BCB would clearly label them as non-clones.
- 行为差异: One function initializes character set data, the other creates a GUI button.；Function A performs I/O and complex data loading; Function B only creates and configures a widget.；Function A is static and works on static fields; Function B is an instance method modifying instance variables.；Function A involves loops and parsing; Function B has no loops and no parsing.
- 修正建议: Incorporate data-flow analysis to distinguish different API usage patterns.；Use graph-based models that capture the overall task (e.g., data initialization vs. GUI construction).；Apply thresholding on token Jaccard or syntactic structure to filter obvious non-clones.

### case_id=5435 FN benchmark_preference_bias

- 方法: `main` vs `doGet`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: A test method that reads and verifies bytes from a file using StraightStreamReader.
- B 摘要: A servlet doGet method that processes HTTP requests to retrieve and render a page, with caching and file I/O.
- 静态失败原因: The static BERT model correctly identified low lexical overlap (Jaccard 0.099) and different semantic structures, so it did not fail; it predicted 0, matching the non-clone reality. The failure is on BCB's side for labeling it as a clone.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have considered these clones due to both functions performing file I/O and having try-catch blocks for IOException, even though their overall purposes diverge significantly. This suggests a broad Type-4 or partial functionality similarity annotation.
- 共享行为: Both methods involve file input/output operations (File, FileInputStream, FileOutputStream, FileWriter).；Both methods handle IOException in catch blocks.
- 行为差异: Function A is a standalone test for a custom stream reader, while Function B is a web request handler with authentication and caching logic.；A writes a fixed sequence of bytes to a file and then reads it back, comparing values; B dynamically constructs HTML and may write to temporary files for caching.；A has no servlet context, HTTP parameters, or user permissions; B heavily depends on HTTP request/response and portal-specific objects.
- 修正建议: Adopt stricter semantic criteria for clone labeling, requiring stronger functional equivalence.；Avoid labeling based solely on shared API usage (e.g., file I/O) if the core behavior differs.；Use functional decomposition to ensure only comparable functionalities are considered clones.

### case_id=5436 FP partial_functionality

- 方法: `callApiPost` vs `loadURL`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Performs an HTTP POST request with parameters, checks response code, and returns the response input stream.
- B 摘要: Loads a URL with optional basic authentication, reads the response, writes it to a temporary file, and updates a status label with file size.
- 静态失败原因: The static model may have focused on the common patterns of opening a URL, setting properties, and handling streams, missing the overall semantic differences.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely labels this as non-clone because despite both using URLConnection, the functionalities are distinct: one is a generic post with error checking, the other is a download with file writing and UI update.
- 共享行为: Both open a URL connection and use input streams from the connection.
- 行为差异: Different HTTP methods (POST vs GET default).；Different return types (InputStream vs void).；Authentication method differs (headers vs Basic Auth).；Output handling differs (return stream vs write to file).
- 修正建议: Incorporate method signature and return type into representation.；Train on more diverse examples to distinguish similar structural patterns with different purposes.；Use data flow analysis to capture output behavior.

### case_id=5437 FN partial_functionality

- 方法: `runScript` vs `scrapeForIsbns`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a script file from a URL and returns its entire content as a string.
- B 摘要: Scrapes ISBN-10 numbers from a URL by reading lines, regex matching, counting, and storing with retry logic.
- 静态失败原因: Static BERT/GraphCodeBERT likely failed due to low token overlap and different structural patterns (e.g., regex, retries, logging) that outweigh the common URL reading pattern, leading to a non-clone prediction which is correct for strict semantics.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this as clone due to both performing I/O from a URL, despite different core functionalities and output semantics.
- 共享行为: Both open a URL and read from an InputStream
- 行为差异: A reads entire file into a string without parsing; B reads line-by-line and applies regex；A has no retry logic; B retries on connection failure；A returns the whole content or 'error!'; B returns count of matches and stores them；A does not use logging; B uses extensive logging
- 修正建议: Improve models to distinguish between data retrieval vs. data processing intent；Incorporate higher-level semantic understanding of the function's purpose beyond I/O patterns

### case_id=5438 FN partial_functionality

- 方法: `copyFile` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a file from a source to a destination directory using a byte buffer.
- B 摘要: Builds a site for editing by processing multiple pages, reading XML, performing XSLT transformations, and writing output files.
- 静态失败原因: GraphCodeBERT likely focused on the high-level semantic differences (different method names, different overall task) and the low token overlap, resulting in a non-clone prediction. It failed to recognize the shared low-level I/O pattern as a basis for clone annotation.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled this as a clone due to the presence of a common file I/O pattern (FileInputStream, FileOutputStream, read/write loop) which some annotators consider a sufficient basis for partial functionality similarity.
- 共享行为: Both perform file I/O operations (reading and writing files).；Both use a buffer to read data in chunks.
- 行为差异: Function A is a simple file copy; B is a complex site generation process.；B involves XML parsing, XSLT transformation, string manipulation, and property handling.；B operates on multiple pages in a loop, while A copies a single file.；B has many more parameters and dependencies.
- 修正建议: Train the model with more examples of partial-functionality clones.；Incorporate subgraph-based pattern matching for common I/O operations.；Use data augmentation to emphasize that shared sub-behaviors can indicate clones even if overall function differs.

### case_id=5439 FN partial_functionality

- 方法: `runScript` vs `loadMFileViaWeb`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches script content from a URL and returns it as a raw string, with error fallback.
- B 摘要: Loads a .m file from a URL, reads its content line by line, parses it into a UserFunction object, and returns it.
- 静态失败原因: Low token overlap (0.19) and different method signatures, return types, and additional parsing in B likely caused the model to miss the shared web-fetching behavior. Static models struggle with partial functionality overlap when surface form diverges.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often marks Type-3/4 clones where core functionality (fetching from web and reading content) is shared, even if output and post-processing differ. The broad similarity in the main loop and error handling supports a clone rating.
- 共享行为: Both open a URL and read its content via an InputStream；Both build a string by concatenating read data；Both handle exceptions in a try-catch block
- 行为差异: A uses BufferedInputStream byte-by-byte reading; B uses BufferedReader line-by-line reading；A returns raw string or 'error!'; B returns a parsed UserFunction object；B has additional parsing step (FunctionParser) and sets function name；B takes more parameters (codeBase, directoryAndFile, mFileName) vs A takes scriptName
- 修正建议: Use dataflow analysis to detect shared I/O patterns (URL open, stream read)；Apply heuristic that ignores differences in return type and post-processing for clone detection；Train on examples where only a common subtask is cloned

### case_id=5440 FN benchmark_preference_bias

- 方法: `doGet` vs `testLoadSource`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `1.0`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Handles HTTP GET request to retrieve and display a web page, including logging, caching, and error handling.
- B 摘要: JUnit test that loads an article source from arXiv and verifies its content contains a specific string.
- 静态失败原因: The static model correctly predicted non-clone because there is no lexical or structural similarity; it did not fail, but BCB label is incorrect.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: Likely a BCB annotation error or a rare case where they considered both methods as 'processing a resource' at a very abstract level, but no meaningful similarity exists.
- 行为差异: One method is a servlet handling HTTP requests; the other is a unit test.；Code A involves page retrieval, user authentication, and caching; Code B simply loads a source and checks content.；Code A has extensive logging and error handling; Code B uses assertions for testing.；Code A interacts with multiple server components; Code B is isolated test logic.
- 修正建议: Re-evaluate BCB annotation for this pair; likely should be non-clone.；Ensure benchmark consistency by ignoring this false positive in evaluation.

### case_id=5441 FN partial_functionality

- 方法: `main` vs `cpFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a URL and extracts its zip entries to local files.
- B 摘要: Copies a file from source to target with options for overwriting and buffer size.
- 静态失败原因: The low token overlap and different method names/signatures likely caused the static BERT model to focus on surface-level differences, missing the underlying I/O loop pattern that BCB considers clone-worthy.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled them as clones due to the shared generic I/O pattern (reading bytes from an InputStream and writing to an OutputStream with buffer), which is considered Type-4 semantic similarity despite different sources and purposes.
- 共享行为: Reads from an InputStream and writes to an OutputStream using a byte buffer；Uses a while loop to read data chunks until end of stream；Flushes and closes output streams
- 行为差异: Code A reads from a ZipInputStream and extracts multiple entries; Code B reads a single file from FileInputStream；Code A obtains input from a URL; Code B from a local file；Code A does not handle file existence or overwriting; Code B has logic for target file naming and overwrite
- 修正建议: Increase sensitivity to generic I/O patterns；Incorporate control flow abstraction that captures byte copying loops；Add features like stream type usage

### case_id=5442 FP boilerplate_overlap

- 方法: `readZoneIDs` vs `getPagina`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads zone IDs from a resource file, parsing each line as an integer and returning a set of integers.
- B 摘要: Fetches a web page content by reading lines from a URL and concatenating them into a single string.
- 静态失败原因: High token overlap (0.34) and similar boilerplate code (URL, InputStreamReader, readLine) mislead static models into focusing on lexical similarity rather than semantic differences in data processing.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels as non-clone when functions have different return types and distinct output processing, despite similar boilerplate for reading lines.
- 共享行为: Both open a URL and read lines using InputStreamReader and BufferedReader/LineNumberReader.；Both handle exceptions with try-catch blocks.
- 行为差异: A reads from a resource file path; B reads from a URL string.；A returns a HashSet of integers; B returns a concatenated string.；A parses each line as integer; B concatenates lines as is.；A does not set authenticator; B sets a custom authenticator.
- 修正建议: Incorporate data flow analysis to track how read data is used (e.g., parsed vs concatenated).；Consider output types and return value semantics.

### case_id=5443 FN benchmark_preference_bias

- 方法: `execute` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Transforms Java class files by injecting method analysis and code instrumentation.
- B 摘要: Builds editable HTML pages from XML and template files using XSLT transformations.
- 静态失败原因: Static BERT models likely captured the low token overlap and recognized the distinct library calls (ASM vs XSLT), correctly predicting non-clone. However, BCB's broader standard considers structural and conceptual similarity, which the model overlooked. The model failed to align with BCB's preference for partial functionality or structural clones.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may label them as clones due to superficial structural similarities: both have a loop over resources, read-transform-write pattern, and similar boilerplate code (streams, exception handling). This aligns with a broad Type-4 (semantic) clone view where both are 'file processing/transformation' utilities, despite different domains.
- 共享行为: Both iterate over a collection of items (class files / pages).；Both read input files and write output files.；Both use try-catch for exception handling.
- 行为差异: Function A operates on bytecode (Java class files) using ASM library; Function B operates on XML/HTML with XSLT and string manipulation.；Function A modifies and rewrites class files; Function B generates new HTML pages from templates.；Different data types and processing libraries (ClassReader vs Transformer).；Function A includes statistics logging about injection; Function B includes debug tracing and property handling.
- 修正建议: Review BCB annotation guidelines to ensure consistency in clone labeling, especially for cross-domain functional similarities.；Augment training data with harder non-clone pairs that share boilerplate but differ in core semantics.；Incorporate domain-specific knowledge (e.g., bytecode vs HTML processing) to better capture functional equivalence.

### case_id=5444 FN partial_functionality

- 方法: `getFile` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies an attribute in the XML, and returns the file path.
- B 摘要: Copies a file from source to target using NIO FileChannel.
- 静态失败原因: The static BERT model likely failed due to very low token similarity (Jaccard 0.08871) and different method names, control flow, and exception handling. It did not capture the underlying shared FileChannel usage pattern because it is a small portion of getFile and the overall tasks appear distinct.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this as a clone because both functions perform a file transfer using FileChannel (transferFrom/transferTo), which is a distinctive I/O pattern. The broad Type-4 criteria might accept partial functional similarity based on this common core operation, even though the surrounding functionality differs significantly.
- 共享行为: Both use FileChannel for efficient file data transfer.；Both close the channels after transfer.；Both involve file I/O operations.
- 行为差异: getFile downloads from a URL, copyFile reads from a local source.；getFile includes XML parsing and attribute modification, copyFile does not.；getFile has conditional logic to skip download if file exists, copyFile does not.；getFile returns a String file location, copyFile returns void.
- 修正建议: Incorporate data flow analysis to detect similar I/O patterns.；Train or fine-tune on a broader set of clone types including partial functionality.；Use graph-based representations that highlight API call sequences.

### case_id=5445 FN benchmark_preference_bias

- 方法: `modifyApplicationMessage` vs `extractUninstallFiles`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Modifies a locale-specific properties file by replacing or adding a key-value pair for internationalization messages.
- B 摘要: Extracts and copies uninstall files for a software upgrade, handling jar extraction and property updates.
- 静态失败原因: Static BERT likely correctly predicted non-clone (0) due to low token overlap (0.191) and clear semantic difference; the BCB label here may be a mislabel.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as a clone due to superficial similarity in using file I/O and Properties, possibly under a broad Type-4 category, but the functionalities are entirely different.
- 共享行为: Perform file I/O operations；Manipulate java.util.Properties objects
- 行为差异: Different high-level purpose (i18n message editing vs uninstall extraction)；Different file operations (properties file modification vs jar extraction and directory management)；Different control flow and error handling
- 修正建议: Re-evaluate BCB annotation for this pair to ensure consistent clone definition；Consider adding more context or domain-specific negative samples in training

### case_id=5446 FN lexical_or_api_overlap

- 方法: `sendExceptionToServer` vs `postRequest`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Send exception details to a server via HTTP POST with URL-encoded parameters.
- B 摘要: Send generic key-value data via HTTP POST and return the response as a string.
- 静态失败原因: Low lexical overlap (Jaccard=0.25) and different method names, variable names, and control flow structures caused the static BERT model to miss the semantic similarity in the core API usage pattern.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB considers broad Type-3/Type-4 clones where two functions performing the same high-level task (HTTP POST with URL-encoded data) are labeled as clones despite differences in parameter handling and output behavior.
- 共享行为: Both perform HTTP POST requests with URL-encoded form data.；Both use URLConnection with setDoOutput(true) to write parameters.；Both read the server response using BufferedReader.
- 行为差异: Code A constructs a fixed set of parameters for exception reporting; Code B accepts an arbitrary HashMap.；Code A prints the response to stdout; Code B returns the response string.；Code A uses OutputStreamWriter; Code B uses PrintWriter.；Code A checks for a specific success response; Code B returns all lines concatenated.
- 修正建议: Incorporate structural features like API call sequences (e.g., URLConnection, setDoOutput, getOutputStream, BufferedReader).；Use data flow analysis to capture encoding and writing of parameters.；Normalize method names and variable names to reduce surface variation.

### case_id=5447 FN benchmark_preference_bias

- 方法: `login` vs `readVersion`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Logs into LOLA by sending email/password via HTTP POST and extracting a session ID from the response.
- B 摘要: Reads version information from a system resource file and parses it into internal fields.
- 静态失败原因: Static BERT/GraphCodeBERT likely relied on token overlap (low at 0.1625) and different method names, correctly identifying semantic dissimilarity, but the BCB label disagrees, causing a false negative. The model failed to align with a potentially erroneous BCB annotation.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB likely misannotated this pair; under typical Type-3/Type-4 definitions, these functions do not implement the same functionality. The annotation may be an error in the dataset.
- 共享行为: Both open a URL/stream and read lines via BufferedReader；Both use try-catch for exception handling；Both involve reading and parsing string data from an input source
- 行为差异: login sends data via POST and reads a remote response; readVersion reads a local file；login returns a session ID; readVersion sets fields and returns void；login catches Exception broadly; readVersion catches only IOException；login uses URLConnection with output; readVersion uses ClassLoader.getSystemResource
- 修正建议: Verify BCB annotations for potential mislabels in this case；Incorporate training examples that distinguish between high-level tasks (e.g., login vs. resource reading)；Improve model to ignore boilerplate patterns (like BufferedReader usage) when determining clones

### case_id=5448 FN partial_functionality

- 方法: `getResourceAsStream` vs `convert`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Caches and retrieves resources from a remote URL, using HTTP and local file caching.
- B 摘要: Converts ACRNEMA medical image files to DICOM format, adding metadata and handling pixel data.
- 静态失败原因: Static BERT likely focused on the low token overlap (Jaccard=0.1348) and different method names, but failed to recognize any potential partial similarity in I/O patterns that BCB annotators might have considered important.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB might have misinterpreted the common use of I/O streams and file operations as similar functionality, but the core logic differs significantly.
- 共享行为: Both use InputStream and OutputStream；Both write to files using buffered streams；Both have byte-by-byte loops for reading/writing；Both print messages to console
- 行为差异: A is for resource downloading and caching; B is for medical image conversion；A uses HTTP connections; B uses DICOM parsing；A has caching logic with cache hashtable; B adds UIDs and handles inflation；A returns an InputStream; B writes to a destination file
- 修正建议: Improve semantic understanding with control flow analysis；Incorporate data-flow to distinguish different processing pipelines

### case_id=5449 FN partial_functionality

- 方法: `postRequest` vs `invoke`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends HTTP POST request with URL-encoded parameters and returns concatenated response string, returning null on any exception.
- B 摘要: Sends HTTP POST request with JSON-serialized arguments, handles response deserialization and retries on ConnectTimeoutException.
- 静态失败原因: Static BERT models rely heavily on lexical overlap and surface structure. The low token Jaccard (0.1667) and different API usage (URLConnection vs HttpClient) lead to low similarity scores. The common high-level behavior of HTTP POST is not captured due to lack of semantic abstraction.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely labels them as clones because both implement the core functionality of an HTTP POST client: constructing a request, sending data, and reading a response. The differences in encoding, library, and error handling are considered superficial for Type-3/Type-4 clone detection.
- 共享行为: Both perform an HTTP POST request to a URL.；Both send data in the request body.；Both read the HTTP response body line by line.
- 行为差异: A uses standard Java URLConnection, B uses Apache HttpClient.；A sends URL-encoded form data, B sends JSON.；A returns raw concatenated string, B optionally deserializes JSON.；A catches all exceptions and returns null, B retries on ConnectTimeoutException.
- 修正建议: Incorporate API call sequence abstraction or flow-based analysis to recognize common HTTP operations across different libraries.；Use code summarization or documentation embeddings to capture intent similarity.；Train on transformed versions that normalize library-specific calls to generic HTTP actions.

### case_id=5450 FN partial_functionality

- 方法: `doFinishLoadAttachment` vs `modifyApplicationMessage`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Handles finishing loading an attachment by saving it to external storage or opening it with an intent.
- B 摘要: Modifies a localized properties file by reading, updating, or adding a key-value pair.
- 静态失败原因: Low token overlap and different method names/purpose cause static models to miss the abstract file I/O similarity; models focus on surface form rather than common boilerplate patterns.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label these as clones because both involve file reading/writing with exception handling, fitting a broad Type-4 category of file manipulation, despite differing application domains.
- 共享行为: Both perform file I/O operations (reading/writing)；Both handle exceptions with try-catch；Both work with file paths and URIs
- 行为差异: One handles email attachments; the other handles localization properties；One uses Android-specific APIs (Intent, Toast); the other uses pure Java I/O；One conditionally saves or views; the other updates a properties file line-by-line
- 修正建议: Use data-flow or graph-based models to capture I/O patterns；Include task-agnostic file manipulation examples in training；Incorporate functional role annotations

### case_id=5451 FN benchmark_preference_bias

- 方法: `getResourceAsStream` vs `convert`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Retrieves a resource via URL with caching, returning an InputStream.
- B 摘要: Converts a DICOM file to another format, manipulating pixel data and writing to a destination file.
- 静态失败原因: The model correctly identified the low syntactic overlap and domain-specific differences, predicting non-clone. It did not fail; rather, the BCB label likely over-generalizes.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled them as clones incorrectly due to an overly broad Type-4 semantic similarity, possibly considering both as 'file I/O with buffered streams' despite entirely different purposes.
- 行为差异: Function A is for resource caching with HTTP, while B is for DICOM conversion.；Different input parameters: String vs File.；Different output: returns InputStream vs void.；Domain-specific logic: A uses URL connections and caching, B parses DICOM headers and transforms pixel data.
- 修正建议: Review and tighten BCB Type-4 criteria to avoid labeling fundamentally different functions as clones.；Re-annotate this pair as non-clone.

### case_id=5452 FN partial_functionality

- 方法: `truncate` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Creates a ZIP archive of a log file for backup, with date-based naming.
- B 摘要: Downloads a ZIP file from a URL and extracts its contents to the current directory.
- 静态失败原因: Static BERT models capture token-level co-occurrence but miss the semantic direction of data flow (write vs read). Overlap in ZIP-related API names (ZipInputStream, ZipOutputStream, ZipEntry) and structural patterns (while loop with buffer) mislead the model into thinking they are more similar than they are.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label as a Type-4 clone because both involve ZIP file processing with similar API usage patterns (ZipEntry, buffer loops), even though one compresses and the other decompresses. The dataset often considers partial functional similarity, especially in I/O-heavy code.
- 共享行为: Both use ZIP stream operations (ZipEntry, buffer reading/writing).；Both involve file I/O with close/cleanup in finally blocks.；Both use a while loop to read data in chunks.
- 行为差异: Function A writes (compresses) to a ZIP; function B reads (decompresses) from a ZIP.；Function A operates on a local file; function B fetches from a URL.；Function A includes backup directory creation and file deletion; function B does not.；Function A checks file age; function B does not.
- 修正建议: Incorporate data flow analysis to distinguish creation vs extraction.；Add summarization of overall purpose (e.g., compress vs decompress) as a distinguishing feature.；Use program slicing to focus on core I/O operations and ignore boilerplate.

### case_id=5453 FP lexical_or_api_overlap

- 方法: `readReferenceText` vs `executePost`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a reference text from a file resource using URL and returns its content as a string, throwing an exception on failure.
- B 摘要: Executes an HTTP POST request with parameters, reads the response, and returns the response string, returning null on failure.
- 静态失败原因: Static BERT models may have focused on the shared lexical tokens (URL, InputStream, BufferedReader, StringBuffer, while loop) and the similar structure of reading lines, ignoring the different setup and purpose.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely considers them non-clones because they perform fundamentally different operations (resource reading vs HTTP POST), even though they share a common I/O pattern.
- 共享行为: Both create a URL object and open an InputStream；Both use BufferedReader to read lines；Both accumulate lines into a StringBuffer；Both return the accumulated string
- 行为差异: A reads from a file resource; B sends an HTTP POST request with parameters；A sets HTTP method and headers; A does not；B writes data to output stream; A does not；B handles connection disconnection in finally; A does not
- 修正建议: Incorporate data flow and control flow dependencies；Use a model that captures method-level semantics beyond token overlap；Add attention to method names and exception handling patterns

### case_id=5454 FN partial_functionality

- 方法: `copyResource` vs `extractZipFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource (URL or file) to a destination file byte by byte.
- B 摘要: Extracts all entries from a zip file to a destination directory, writing each entry as a file or directory.
- 静态失败原因: Low token overlap (0.25) and different method names, structures, and API calls caused the model to miss the high-level similarity of reading from an input and writing to an output.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as file copying operations with similar I/O patterns, thus a Type-3 clone despite different source types and buffering.
- 共享行为: Both read from an input source and write to an output file stream；Both close streams after processing；Both handle I/O exceptions
- 行为差异: copyResource reads byte-by-byte; extractZipFile reads in 1024-byte buffers；extractZipFile handles zip entries, directories, and progress updates; copyResource does not；copyResource uses InputStream and FileOutputStream; extractZipFile uses ZipInputStream and FileOutputStream for each entry
- 修正建议: Improve representation to capture I/O patterns and stream handling；Add training data with varied file copy/extraction scenarios；Use data flow or graph-based features to link input-to-output operations

### case_id=5455 FP partial_functionality

- 方法: `callService` vs `downloadModel`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Makes an HTTP GET request to a constructed URL, reads response line by line, and stores the entire response as a string in a class field, handling MalformedURLException and IOException.
- B 摘要: Downloads an RDF model from a given URL by opening a connection (with HTTP header customization), reading the stream into a Jena Model object, and returning it, wrapping exceptions in RuntimeException.
- 静态失败原因: The model may have been misled by high token overlap in boilerplate patterns (URL, try-catch, IOException, openStream) and similar method length, ignoring the fundamental difference in return type and purpose.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely labels this as non-clone because the high-level functionality differs significantly: one is a generic HTTP GET to store a string, the other is a library-specific model download. Despite shared boilerplate, the semantics and output types are distinct.
- 共享行为: Both open a URL and read an input stream；Both handle MalformedURLException and IOException
- 行为差异: A is a private void method that sets a field; B is a public static method that returns a Model；A does not set HTTP headers; B sets Accept and Accept-Language headers；A reads text lines; B reads an RDF model using Jena；A catches exceptions and sets an answer string; B catches and throws RuntimeException
- 修正建议: Incorporate method signature and return type features；Use data flow analysis to distinguish reading text vs model；Include library-specific API calls (Jena) as discriminative features

### case_id=5456 FN partial_functionality

- 方法: `copyFile` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a file from source to destination using buffered input/output streams.
- B 摘要: Retrieves a resource as an InputStream by URL, with caching to a local file system.
- 静态失败原因: Static BERT methods rely on token overlap and structural similarity, which are low here (token Jaccard 0.1386). The model likely failed to recognize the broad functional similarity that BCB considers, leading to a false negative prediction.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label these as clones due to the shared core behavior of reading from an input stream and writing to an output stream, which is considered a basic functional similarity despite the high-level differences.
- 共享行为: Both read from an InputStream and write to an OutputStream in a loop.；Both close streams after use.
- 行为差异: Method A is a straightforward file copy; Method B involves URL fetching, caching, and HTTP connection handling.；Method A takes two File arguments; Method B takes a String resource name and returns an InputStream.；Method B has complex error handling and uses a cache; Method A has simple error propagation.；Method B is synchronized; Method A is not.
- 修正建议: Train the model with more examples of partial functional similarity (Type-3/Type-4 clones) to capture broader patterns.；Incorporate higher-level API usage or data flow features to detect common I/O patterns.

### case_id=5457 FN partial_functionality

- 方法: `copyResource` vs `init`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource from a URL or file to a destination file byte by byte.
- B 摘要: Initializes a report file by creating directories, backing up existing reports via file copy, and starting XML writing; also recovers completed documents from backups.
- 静态失败原因: Low token overlap (Jaccard 0.146) and different method names lead to low similarity scores. Static BERT models rely on lexical and syntactic overlap, which this pair lacks.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB might have labeled this as a clone due to the presence of a file copy operation in both functions, considering it as partial functional similarity. However, the overall purposes are very different.
- 共享行为: Both involve reading from an input source and writing to an output file.
- 行为差异: Function A is solely a resource copy; Function B has multiple steps including directory creation, XML writing, and document recovery.；Function B's copy is a backup sub-step; Function A's copy is the entire purpose.；Function B uses buffered streams and fixed-length blocks; Function A uses single-byte read/write.；Function B handles complex XML parsing and state recovery; Function A does not.
- 修正建议: Use models that capture long-range semantic context and distinguish primary vs. secondary functionality.；Incorporate data flow and dependency analysis to identify when a shared pattern is only a small part of one function.

### case_id=5458 FN partial_functionality

- 方法: `getHTML` vs `run`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches HTML from a URL, optionally writes to file, returns the HTML string.
- B 摘要: Reads lines from a URL, parses first two lines as version and url, stores rest, handles errors notifies listeners.
- 静态失败原因: Static BERT/GraphCodeBERT likely failed due to low token overlap (0.223), different method names and I/O patterns, missing the shared URL-reading boilerplate that BCB considers clone-worthy.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label these as clones because both are core networking logic for reading a URL line by line, a common pattern with similar structure and purpose despite different post-processing.
- 共享行为: Both open a URL connection and read lines using BufferedReader and InputStreamReader；Both iterate over lines until null；Both catch IOException
- 行为差异: A returns the entire HTML content; B parses line indices 0,1,default；A has optional file writing; B has no file I/O；B has custom error handling for specific exceptions and notifies listeners；B sets instance fields (version, url, informations); A builds a StringBuilder
- 修正建议: Incorporate URL reading patterns as a clone signal；Use structural similarity of try-catch-finally with BufferedReader/InputStreamReader；Relax exact match requirements for post-processing steps

### case_id=5459 FP lexical_or_api_overlap

- 方法: `main` vs `testReadHelloWorldTxt`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Parses command line arguments to read a Prolog file and generate adapter classes and resources.
- B 摘要: Tests that a FSContentResolver can retrieve file content using various path formats.
- 静态失败原因: The model likely focused on superficial lexical overlap (e.g., FileUtils, IOUtils) and generic method structure, missing the deep semantic difference between a generator main method and a unit test.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labeled as non-clone because the functions have completely different purposes and minimal structural similarity, even under broad Type-3/4 definitions.
- 共享行为: Both perform file I/O operations；Both use utility classes like FileUtils；Both have try-catch or exception handling
- 行为差异: Function A is a program entry point with complex generation logic; Function B is a test method with assertions；Function A writes output files; Function B reads and asserts file content；Different control flow and error handling
- 修正建议: Incorporate function role detection (main vs test)；Use abstract syntax tree (AST) or control flow graph to capture structural intent；Add training on functional grouping based on method purpose

### case_id=5460 FP boilerplate_overlap

- 方法: `readUNI` vs `run`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a tab-separated file from a URL, extracts the first and third columns, and adds concatenated id and description to a provided vector.
- B 摘要: Opens a connection to a fixed URL and reads all lines without processing them, essentially discarding the content.
- 静态失败原因: Static BERT/GraphCodeBERT models rely on token overlap and structural patterns. These functions share many tokens (URL, openStream, try-catch, while loop) leading to high similarity, but the model misses the critical difference in data usage because it lacks dataflow awareness.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically requires similar input/output behavior and data transformation. Here, one function reads and discards, the other reads, parses, and stores data, which are semantically different tasks.
- 共享行为: Open a URL connection and read lines；Handle MalformedURLException and IOException；Close the stream/reader after reading
- 行为差异: A reads from a parameterized source URL, B uses a hardcoded URL；A parses each line and populates a vector, B does nothing with the lines；A uses Scanner with delimiter, B uses BufferedReader；A adds to a passed parameter vector, B has no output
- 修正建议: Incorporate dataflow analysis to track how read data is used；Consider method signatures and parameters as strong signals；Use control-flow and data-dependency graphs to distinguish processing from discard

### case_id=5461 FP lexical_or_api_overlap

- 方法: `callService` vs `SRWGuiClient`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a URL and stores the entire response as a string.
- B 摘要: Constructs a GUI web browser, reads a URL, optionally transforms XML with XSLT, and displays the content.
- 静态失败原因: Static BERT/GraphCodeBERT likely over-relied on the lexical overlap of the URL reading pattern (URL, BufferedReader, InputStreamReader, readLine) and missed the overall structure and purpose differences.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: None
- 共享行为: Both read from a URL using URL.openStream() and BufferedReader.readLine()
- 行为差异: Function A is a simple fetch; Function B sets up a full GUI, processes XML/XSLT, and displays content
- 修正建议: Incorporate structural awareness (e.g., AST differences) or use graph-based representations that capture data flow and control flow more globally.；Distinguish between boilerplate and core functionality.

### case_id=5462 FP lexical_or_api_overlap

- 方法: `downloadURLtoString` vs `getVersion`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Downloads entire content from a given URL as a string.
- B 摘要: Fetches a version string from a hardcoded URL, with error handling.
- 静态失败原因: Static BERT over-relied on high lexical overlap and similar structural patterns, ignoring the semantically different output generation and parameterization.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels as non-clone because despite similar boilerplate, the functions serve different purposes (download full content vs. extract version). The semantic intent diverges.
- 共享行为: Both open a URL connection and read lines using BufferedReader；Both return a string obtained from the URL content；Both close the reader after reading
- 行为差异: A takes URL as parameter; B hardcodes URL；A reads all lines and appends them; B overwrites variable to store only the last line；A has no exception handling; B catches exceptions and returns null
- 修正建议: Incorporate data-flow analysis to trace how variables are constructed (e.g., appending vs. overwriting)；Use entity recognition to distinguish parameterized vs. hardcoded inputs；Add type-4 clone detection heuristics for functional differences

### case_id=5463 FP lexical_or_api_overlap

- 方法: `readUNI` vs `readVersion`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a tab-separated file from a URL and adds ID-description pairs to a vector.
- B 摘要: Reads a version file from the classpath and extracts version, revision, and date fields.
- 静态失败原因: The model likely over-relied on lexical overlap (Scanner/BufferedReader, try-catch-finally) and ignored the divergent semantic goals and data flows.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels them not clones because the purpose and output are distinct, despite similar boilerplate.
- 共享行为: Both open a URL stream and read lines sequentially；Both parse each line using delimiters or string splitting；Both handle IO exceptions and close the stream in a finally block
- 行为差异: readUNI reads from an arbitrary URL passed as parameter; readVersion reads from classpath resource；readUNI outputs to a vector; readVersion sets instance fields；Parsing logic differs: tab-separated vs key-value with specific prefixes
- 修正建议: Incorporate data flow analysis to track output vs side effects；Use control-flow and semantic embeddings that capture the task-specific logic；Include type information of used methods and fields

### case_id=5464 FN boilerplate_overlap

- 方法: `decodeFileToFile` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.4`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Decodes a Base64-encoded file and writes the decoded content to an output file.
- B 摘要: Retrieves a resource from a URL, optionally caching it locally, and returns a FileInputStream to the cached or remote file.
- 静态失败原因: The model likely captured the large semantic gap due to different method names (decode vs getResource) and different API calls (Base64 vs HTTP), but missed the low-level I/O pattern overlap that could suggest a clone under BCB guidelines.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may have labeled these as clones due to the shared boilerplate of buffered stream copying and exception handling, which are common patterns in I/O operations, and BCB's broad type-3/4 definition sometimes overlooks high-level functional differences.
- 共享行为: Both use buffered streams for I/O operations.；Both implement read-write loops to copy bytes.；Both handle IOException with try-catch-finally and close streams in finally blocks.
- 行为差异: Function A decodes Base64; Function B does not perform any decoding.；Function A reads from a local file; Function B reads from a network URL.；Function A writes to a file; Function B returns an InputStream (the cached file).；Function B includes HTTP caching logic (headers, cache file management); Function A does not.
- 修正建议: Incorporate data-flow analysis to distinguish core transformations (Base64 decode vs HTTP caching).；Use API call embeddings to better capture the functional purpose beyond stream handling.；Fine-tune on examples where structural similarity exists but semantics differ to reduce false positives from boilerplate.

### case_id=5465 FP lexical_or_api_overlap

- 方法: `handleHandshake` vs `issueCommandToServer`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Validates handshake username and optionally sends HTTP request to Minecraft session server to authenticate.
- B 摘要: Sends a command to a server via HTTP POST and returns the response.
- 静态失败原因: Static models may overemphasize lexical overlap of common Java I/O classes (URLConnection, BufferedReader, InputStreamReader) and similar control flow, ignoring the different domain logic and error handling.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels as non-clone because the functions serve entirely different purposes despite sharing HTTP I/O boilerplate; the similarity is superficial.
- 共享行为: Both perform an HTTP request and read the response line by line.
- 行为差异: A is void and shuts down network on failure; B returns string response.；A uses GET request with query parameters; B uses POST request with form data.；A includes user session validation and Minecraft protocol; B is generic.；A has try-catch exception handling; B throws IOException.
- 修正建议: Add attention to domain-specific context；Improve handling of method signatures and return types；Use dataflow analysis to distinguish different request methods and error handling patterns.

### case_id=5466 FP boilerplate_overlap

- 方法: `handleHandshake` vs `doVersionCheck`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Validates a handshake packet by checking username and performing a HTTP session validation, then either sending a login or disconnecting.
- B 摘要: Checks for a new version of jEdit by reading a version URL and comparing build numbers, displaying a message.
- 静态失败原因: Static models like GraphCodeBERT overemphasize shared API calls (URL, BufferedReader) and control flow structure (try-catch, if-else), missing the divergent business logic and purpose.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the functional semantics are entirely different despite shared boilerplate I/O code; partial functionality similarity is not sufficient for Type-3/4 clones.
- 共享行为: Opens a URL and reads its content line by line using BufferedReader；Handles IOExceptions and performs conditional logic based on parsed data
- 行为差异: Function A validates a game session using a server response, while B checks for software version updates；Different parsing: A looks for "ok" string, B looks for ".version" and ".build" prefixes；Different outcomes: A sends network packets or disconnects, B shows GUI messages
- 修正建议: Incorporate dataflow analysis to track variable usage and distinguish different operations on parsed data；Use contrastive learning with examples that have similar structure but different domain logic

### case_id=5467 FP boilerplate_overlap

- 方法: `copy` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Recursively copies a file or directory using FileChannel.
- B 摘要: Handles GUI action events to set application preferences via file choosers.
- 静态失败原因: Static BERT models rely heavily on token overlap and may be misled by common boilerplate tokens (File, if, null) and lack understanding of long-range semantic structure.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels clones based on overall functionality; these two functions have completely different purposes (file copy vs. GUI event handling), so they are not clones.
- 共享行为: Both use File objects；Both have exception handling
- 行为差异: A performs file I/O copying; B updates GUI preferences；A is recursive; B is event-driven with multiple command branches；A requires source and target; B selects files via chooser
- 修正建议: Incorporate dataflow analysis；Use type-aware embeddings；Train on functional similarity rather than lexical overlap

### case_id=5468 FP long_range_semantics

- 方法: `createOutputStream` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.98`
- 推荐路线: `static_summary_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Decompress a ZIP file except for a specific entry, then add a new entry with UTF-8 encoding and return a BufferedWriter.
- B 摘要: Handle GUI action events to update application settings like file paths, image scaling, and look-and-feel, potentially prompting a restart.
- 静态失败原因: The static BERT model likely failed due to the long-range semantic structure: both functions are lengthy and contain many Java keywords (e.g., File, String, if, return) that may have misled the model into thinking there is structural similarity, while the actual logic is entirely different.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely labeled as non-clone because the functions have completely different purposes (file I/O vs. GUI event handling) with minimal syntactic overlap.
- 共享行为: Both use conditional logic to handle different cases.；Both involve file I/O operations (reading/writing files).
- 行为差异: Function A processes ZIP files, while Function B handles GUI events.；Function A returns a BufferedWriter, Function B has void return and mutates UI state.；Function A uses ZipInputStream/OutputStream, Function B uses JFileChooser and Swing components.；Function A has a loop over ZIP entries; Function B has a series of if-statements for different commands.
- 修正建议: Incorporate data flow analysis to capture variable dependencies.；Use larger context windows or hierarchical models to better understand overall function purpose.；Add negative sampling with diverse functional patterns during training.

### case_id=5469 FN benchmark_preference_bias

- 方法: `doGet` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.2`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Handles HTTP GET requests, retrieves a page, checks permissions, and optionally caches output to a file.
- B 摘要: Copies a file from source to destination using file channels.
- 静态失败原因: The static BERT model correctly identified the low lexical and structural similarity, so it did not fail; the prediction of 0 aligns with strict semantic non-clone. The discrepancy arises from a questionable BCB label.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as a clone based on a very broad interpretation of 'file I/O', but the functional overlap is minimal and not sufficient for a typical BCB clone annotation.
- 共享行为: Both involve file I/O operations (reading/writing files), but in doGet it is a minor secondary action.
- 行为差异: doGet handles HTTP requests and responses, while copyFile only deals with file paths.；doGet includes authentication, logging, and page rendering logic; copyFile is a simple utility method.；doGet is long and complex, copyFile is short and straightforward.
- 修正建议: Review the BCB annotation for possible mislabeling.；If the BCB label is considered correct, the model should be trained on broader semantic categories, but this seems unjustified.

### case_id=5470 FN benchmark_preference_bias

- 方法: `testCopy_readerToOutputStream_Encoding` vs `modifyApplicationMessage`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.6`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Tests copying data from a reader to an output stream with encoding conversion and verifies content equality.
- B 摘要: Reads a properties file for a locale, modifies or adds a property value, and writes back to the file.
- 静态失败原因: The static model correctly identified these as non-clones based on lack of functional similarity. Its prediction aligns with strict semantic judgment but disagrees with the BCB annotation. The error (false negative) arises from a mislabeled ground truth in BCB, not from model failure.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB likely labeled this as a clone due to both methods involving I/O stream copying and file handling, despite having different high-level purposes. The annotation may have been overly broad, focusing on low-level operations rather than functional equivalence.
- 共享行为: Both involve file I/O operations using streams；Both read from an input source and write to an output destination；Both handle exceptions
- 行为差异: Function A is a unit test for a copy utility; Function B is a production method for modifying properties files；Function A copies binary data with encoding conversion; Function B reads, edits, and writes text properties；Function A uses byte arrays and assertions; Function B uses Properties and string manipulation；Function A does not modify the data; Function B conditionally modifies or adds a property
- 修正建议: Re-evaluate BCB annotation for this pair to ensure consistency with typical clone criteria；Improve training data by filtering overly broad annotations

### case_id=5471 FP lexical_or_api_overlap

- 方法: `doVersionCheck` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches version info from a URL and checks for updates.
- B 摘要: Fetches Google image search results and extracts image URLs.
- 静态失败原因: Static models overemphasize lexical and API-level overlap (URL, BufferedReader, try-catch) and miss the distinct semantic goals and data processing.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels as non-clones when functions have different domain-specific logic, even if they share common I/O patterns.
- 共享行为: Open a URL connection；Read lines from input stream；Handle exceptions
- 行为差异: Purpose: version checking vs. image search；Output: UI message vs. image icon setting；Parsing: version/build strings vs. image URL extraction
- 修正建议: Incorporate data flow and control flow analysis to capture what the functions actually compute；Use graph representations that model variable dependencies beyond API calls

### case_id=5472 FN partial_functionality

- 方法: `hyperlinkUpdate` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.4`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Handles hyperlink activation by fetching URL content and displaying it in a text pane dialog.
- B 摘要: Retrieves a resource as an InputStream with caching and HTTP handling.
- 静态失败原因: Static BERT likely over-weighted the shared lexical tokens (URL, stream, IOException) and missed the distinct application contexts (GUI vs caching).
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label them as clones due to overlapping use of URL, InputStream, and I/O exception handling, even though the overall functionality differs.
- 共享行为: Both open URL connections and read input streams
- 行为差异: Function A displays content in a GUI, while function B caches the stream to file and returns an InputStream；Function B includes caching logic and HTTP condition checks, which A does not
- 修正建议: Incorporate data-flow analysis to distinguish high-level intent；Add attention to method signatures and control flow patterns

### case_id=5473 FP boilerplate_overlap

- 方法: `loadBinaryStream` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Loads a binary stream from an InputStream into an HTTP response output stream, setting headers and closing streams.
- B 摘要: Handles action events to configure application settings (e.g., file paths for external tools, look and feel) via file choosers and UI updates.
- 静态失败原因: The model may have been misled by low-level API commonalities (e.g., IOUtils, BufferedOutputStream) or was confused by the truncated code_b, interpreting it as similar to stream handling due to incomplete context.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels these as not clones because they have entirely different functionality, data flow, and purpose, despite both being part of larger applications.
- 共享行为: Both are void methods that perform I/O operations (A: network I/O, B: file I/O) and use try-catch-finally or conditional blocks.
- 行为差异: A functions as a utility for binary stream transfer; B handles GUI event-driven configuration.；A is short and focused; B is long with multiple conditional branches for different settings.；A uses HTTP request/response; B interacts with Swing components and preferences storage.
- 修正建议: Use a more robust model that captures high-level semantics rather than token overlap.；Improve data preprocessing to avoid truncated code snippets.；Train with more diverse negative pairs that share low-level APIs but differ in purpose.

### case_id=5474 FP boilerplate_overlap

- 方法: `perform` vs `md5`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Processes a form submission to classify a concept by sending XML to a remote service, parsing the result, and forwarding to appropriate view.
- B 摘要: Computes MD5 digest of a string, returning either hex or base64 encoded string.
- 静态失败原因: Static model may have been misled by overlapping structural patterns (try-catch, URLConnection, StringBuffer) and generic API usage, ignoring the vast functional difference.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely rejected due to completely different overall semantics and purpose; shared low-level patterns like exception handling and I/O are insufficient for clone label.
- 共享行为: Both involve string manipulation and handling of byte arrays.
- 行为差异: Function A is a web controller with complex session, form, and networking logic; Function B is a standalone cryptographic utility.；Function A has side effects (session attributes, forwarding); Function B is pure computation.；Function A handles HTTP connections; Function B does not.；Function A uses multiple external classes; Function B uses only standard libraries.
- 修正建议: Enhance training with more diverse negative pairs that share syntactic patterns but differ semantically.；Incorporate data flow analysis to capture actual behavior differences.；Use AST or graph-based models to better represent control flow and dependencies.

### case_id=5475 FN partial_functionality

- 方法: `invoke` vs `doVersionCheck`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Invokes a remote method via HTTP POST with retry logic and deserializes JSON response.
- B 摘要: Checks for version updates by reading a version file from a URL and parsing build numbers.
- 静态失败原因: Low token overlap and different high-level semantics misled the model into predicting non-clone.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considers broad Type-4 clones based on shared I/O pattern and exception handling, despite different domain logic.
- 共享行为: Both read from a network URL using BufferedReader and InputStreamReader.；Both parse lines from the input stream.；Both handle IOException (or subclass).
- 行为差异: A uses HTTP POST with request body; B uses URL.openStream() for GET.；A has retry logic on ConnectTimeoutException; B does not.；A deserializes JSON response; B parses specific text patterns (.build, .stablebuild).；A returns a deserialized object; B calls another method and shows UI.
- 修正建议: Incorporate task-level context or code summarization to capture shared I/O patterns.；Use data augmentation to include more examples with similar low-level patterns but different purposes.；Train with contrastive learning emphasizing structural similarity over token overlap.

### case_id=5476 FN benchmark_preference_bias

- 方法: `modifyApplicationMessage` vs `testCopyUnknownSize`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Modifies a locale-specific properties file by reading, editing, or appending a message entry.
- B 摘要: Tests copying data from an input stream to an output stream of unknown size using ExtraIOUtils.copy.
- 静态失败原因: Static BERT/GraphCodeBERT likely correctly identified the lack of semantic similarity, influenced by low token overlap (0.09) and different method names; the erroneous BCB label may stem from over-generalization or annotation noise.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled these as clones due to a very broad interpretation of Type-4 semantic similarity (both perform I/O data copying), but this seems inconsistent with typical BCB annotations requiring more substantial functional overlap.
- 共享行为: Both involve basic I/O stream operations (read/write).
- 行为差异: Function A manipulates property files with locale-specific logic; Function B tests a utility copy method.；Function A modifies file content based on locale and message name; Function B compares byte arrays for correctness.；Function A handles file existence and copying; Function B uses ByteArray streams and asserts equality.；Function A throws Exception and prints stack trace; Function B declares IOException and uses JUnit assertions.
- 修正建议: Improve BCB annotation consistency for Type-4 clones by requiring stronger functional commonality.；Add more contextual features like method purpose and data flow to avoid false positives.

### case_id=5477 FP lexical_or_api_overlap

- 方法: `mysqlPasswordHash` vs `perform`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Computes MySQL password hash using SHA1 and formatting.
- B 摘要: Handles HTTP request in web application for classification logic.
- 静态失败原因: Possible over-reliance on common Java syntax (e.g., try-catch, loops) or token overlap from similar method/field names, despite low Jaccard similarity.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels as non-clone because functions have completely different semantics and no significant functional overlap.
- 共享行为: Both involve cryptographic operations? No, only A.
- 行为差异: Different purpose: password hashing vs web request handling；Different APIs: SHA1 vs URL connections and session management；Different output: String hash vs ActionForward
- 修正建议: Increase token frequency awareness；Incorporate better structural abstractions；Train with more diverse negative samples

### case_id=5478 FN benchmark_preference_bias

- 方法: `read` vs `read`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.7`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Reads a skeleton file from classpath, splits into sections by '---', and validates section count.
- B 摘要: Opens a file or URL, reads it via another method, and returns a status code.
- 静态失败原因: The static BERT model likely relied on low token overlap (Jaccard=0.147) and different control flow, missing the high-level I/O similarity that BCB might emphasize.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider both as 'read' methods performing I/O operations from a source, which might be seen as functionally similar under a broad Type-4 interpretation, though the actual logic differs significantly.
- 共享行为: Both methods take a string parameter (filename or name) and read from an input source.；Both use streams and handle I/O exceptions (though A throws, B catches).
- 行为差异: A reads from classpath resources; B reads from filesystem or URL.；A parses lines and builds sections; B delegates to another read method.；A validates the number of sections; B returns a status code.；A throws Exception on errors; B catches IOException and sets status.
- 修正建议: Improve static model to recognize broad functional similarities beyond token overlap, e.g., by learning I/O patterns.；Use a more fine-grained clone type classification to avoid false negatives on weak functional similarities.

### case_id=5479 FN partial_functionality

- 方法: `run` vs `postRequest`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: A Runnable that performs a GET request with Basic authentication and reads the response line-by-line, storing the result in instance variables.
- B 摘要: A static method that performs a POST request with URL-encoded form data and returns the response body as a string.
- 静态失败原因: Static BERT models rely on surface token overlap (Jaccard=0.23), missing the semantic similarity in overall HTTP communication behavior due to different method signatures, HTTP method strings, and utility classes.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considers both as HTTP request/response handling functions, focusing on the common pattern of opening a connection and reading the response, treating differences in HTTP method and parameters as superficial.
- 共享行为: Both open an HTTP URL connection；Both set request properties (headers or output mode)；Both read the response via BufferedReader line-by-line；Both handle exceptions
- 行为差异: A uses GET method; B uses POST method；A includes an Authorization header; B sends form data in the request body；A appends newlines to the response; B does not；A updates side-effect variables (lastIteraction, finish); B returns a string
- 修正建议: Use models that capture abstract execution patterns via API call sequences；Incorporate data flow and control flow graphs；Augment training data with more HTTP client examples

### case_id=5480 FP partial_functionality

- 方法: `copyIconFiles` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Copies icon files (16 and 32 pixel) for a UML class if icon annotations are present, using file channel transfer.
- B 摘要: Handles actionPerformed events for various UI commands (e.g., setting paths for Graphviz, ImageMagick, database fonts, look-and-feel) by opening file choosers and updating preferences.
- 静态失败原因: Static BERT/GraphCodeBERT may have overemphasized common structural patterns such as if-blocks, try-catch, and file-related API calls (FileInputStream, FileChannel), while missing the high-level semantic intent and control flow differences. The token Jaccard similarity is low (0.053), so the models likely relied on rare but overlapping keywords ('if', 'try', 'File', 'catch') and graph structures that look similar in code snippets.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely labels this as non-clone because the overall functionality is entirely different: one is about copying icon resources, the other is about UI event handling for application settings. The structural similarities (conditionals, file I/O) are superficial and do not indicate semantic equivalence or even partial functionality overlap.
- 共享行为: Both contain conditional blocks (if statements).；Both perform file-related operations (file input/output, file chooser).；Both use try-catch blocks for exception handling.；Both have repeated code patterns for different cases.
- 行为差异: Function A copies icon files; Function B handles UI action commands and updates settings.；Function A uses FileChannel with FileInputStream/FileOutputStream; Function B uses JFileChooser and manipulates UI components.；Function A deals with image file types; Function B deals with executable paths, database settings, look-and-feel, etc.；Function A is a private helper; Function B is an ActionListener override with a long sequence of unrelated commands.
- 修正建议: Incorporate data flow and call context to distinguish between file copying and UI event handling.；Use more discriminative features like method names, variable types, and library imports to capture domain differences.；Train on more diverse examples of non-clones with similar syntactic structures but different semantics.；Apply contrastive learning to push apart embeddings of functionally unrelated code.

### case_id=5481 FP lexical_or_api_overlap

- 方法: `main` vs `parse`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: AdapterGenerator main method that reads a Prolog file, parses it, generates adapter classes and serializes the adapter layer to a JAR file.
- B 摘要: Parse method that extracts a resource name from metadata and either copies the input stream to a file or delegates parsing to a downstream parser.
- 静态失败原因: Static BERT might have been fooled by the presence of common APIs like FileOutputStream, IOUtils, or similar exception handling, but overall structure differs.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled as non-clone because the functions have completely different purposes and logic, only sharing trivial I/O patterns.
- 共享行为: Both involve file I/O and error handling.
- 行为差异: Different overall goals; main is a CLI entry point for code generation, parse is a Tika parser that conditionally extracts or passes through.
- 修正建议: Add more training examples with diverse structures；Improve handling of long-range semantic dependencies；Focus on control flow similarity rather than API usage

### case_id=5482 FP lexical_or_api_overlap

- 方法: `read` vs `executePost`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a skeleton file from classpath, parses sections delimited by '---', and validates section count.
- B 摘要: Executes an HTTP POST request with parameters and returns the response body.
- 静态失败原因: The model likely overfitted on common token sequences like 'BufferedReader', 'readLine', 'InputStreamReader', and 'url.openConnection()' without capturing the distinct domain logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clones when functions have different overall purpose, even if they share some boilerplate I/O code.
- 共享行为: Both use BufferedReader to read line by line；Both read from an input stream obtained from a URL
- 行为差异: Function A reads a local resource file, Function B sends an HTTP request；Function A parses and validates sections, Function B just returns raw response；Error handling differs: A throws exceptions, B catches and returns null
- 修正建议: Enhance model with structural information like control flow and data dependencies；Include more context on method names and surrounding code；Apply contrastive learning to distinguish similar boilerplate with different semantics

### case_id=5483 FN partial_functionality

- 方法: `doVersionCheck` vs `addIDs`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches version check data from a URL and extracts development and stable build numbers.
- B 摘要: Fetches chemical IDs from a web service based on a name and populates a peak list row with various ID types.
- 静态失败原因: Static BERT methods rely on lexical and structural overlap; low Jaccard and highly specialized domain-specific code prevented recognizing the high-level pattern, but that pattern is too generic to be meaningful.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as network I/O methods that fetch and parse data, thus broad partial functionality similarity, but the specifics are entirely unrelated.
- 共享行为: Both open a URL, read lines, and parse data from the lines.
- 行为差异: Different URL construction and query parameters；Different parsing logic (prefix matching vs HTML pattern matching)；Different outputs (void vs int, different fields set)；Different error handling (GUI dialog vs logging)
- 修正建议: Incorporate higher-level semantic understanding of the method's purpose；Use task-specific pre-training or domain adaptation；Disregard very broad I/O patterns that are common across many methods

### case_id=5484 FN benchmark_preference_bias

- 方法: `uncaughtException` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Handles uncaught exceptions by displaying an error dialog with an option to submit a bug report and launches the browser to the issue tracker.
- B 摘要: Launches a build configuration for a NexOpen project by reading Maven pom files, setting Hibernate properties, and executing an install project action.
- 静态失败原因: The static BERT model correctly predicted non-clone (0) due to very low token Jaccard similarity (0.0595) and different vocabulary. The failure is actually a discrepancy with BCB label; the model aligned with semantic intuition.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might consider them clones due to both methods being in the same Eclipse environment, using similar patterns (try-catch, logging, IOUtils), and possibly a broad interpretation of Type-4 (conceptual similarity) where both involve 'launch' operations.
- 共享行为: Both use exception handling and logging；Both contain I/O operations (IOUtils.copy, file access)；Both involve launching something (URL or build job)
- 行为差异: Different domains: error reporting UI vs project build automation；Different external APIs (SWT MessageBox vs Eclipse launch configuration)；Different complexity and business logic；No overlapping functionality in core purpose
- 修正建议: Re-evaluate BCB annotation for this pair to ensure consistency；Provide clearer guidelines for Type-3/Type-4 clones to avoid false positives；For static models, incorporate structural or control-flow features to reduce reliance on token overlap

### case_id=5485 FP lexical_or_api_overlap

- 方法: `authenticate` vs `perform`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Authenticates a module using a random challenge and MD4 hashed password from a secrets file.
- B 摘要: Processes a Struts action to classify a concept by sending XML over HTTP and parsing the result.
- 静态失败原因: Likely due to lexical or API overlap: both use I/O streams, error checking, and similar control structures (if-return, try-catch). The model may focus on overlapping patterns like 'Util.writeASCII' and 'return false' etc., ignoring domain differences.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB label is 0 because these functions clearly perform different tasks: authentication of a module vs processing a web classification request. They share no meaningful functionality.
- 共享行为: Both handle authentication/authorization checks；Both can report errors and set status；Both use streams for I/O
- 行为差异: Function A is a private authentication method for a network protocol; function B is a public Struts action for a web application.；A uses secure random and cryptographic hash; B uses HTTP connection and XML parsing.；A returns boolean; B returns ActionForward object.；A has completely different control flow and data structures.
- 修正建议: Improve training data diversity for web vs network protocols；Explicitly encode domain-specific keywords (like challenge, MD4, secretsFile for crypto; vs ActionMapping, HttpServletRequest for web)；Use type information or method signatures more heavily.

### case_id=5486 FN partial_functionality

- 方法: `copyResource` vs `saveFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Copies a resource from a URL or file to a destination file using byte-by-byte streaming.
- B 摘要: Saves UI settings to an XML file, including building an XML document, copying a DTD resource, and writing the XML to a file.
- 静态失败原因: Static BERT/GraphCodeBERT models rely heavily on token overlap and syntactic structure. The low token Jaccard (0.068) and divergent control flow caused the model to miss the underlying shared behavior of copying from input to output. It failed to recognize the partial functional overlap.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label these as clones because both functions contain a 'copy resource' subtask (reading from an input stream and writing to a file output stream), which aligns with broad Type-4 semantic similarity on partial functionality.
- 共享行为: Both write data to a file via FileOutputStream.；Both involve reading from an InputStream (URL.openStream, FileInputStream, or getResourceAsStream).；Both copy bytes from input to output (in function B, IOUtils.copy copies a DTD file; in function A, a manual loop copies bytes).
- 行为差异: Function A is a generic copy; function B is specific to UI settings with XML construction.；Function A reads from either URL or file; function B reads a fixed DTD resource.；Function A uses a simple while loop; function B uses XMLOutputter and IOUtils.copy.；Function B includes error handling and logging; function A throws exception to caller.
- 修正建议: Train models on dataflow or control-flow graphs to capture shared subroutines.；Use attention mechanisms that can focus on small but semantically important regions like IOUtils.copy statements.；Incorporate pre-training objectives that emphasize functional similarity over lexical similarity.

### case_id=5487 FN benchmark_preference_bias

- 方法: `main` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a URL and extracts its zip entries to the filesystem.
- B 摘要: Tests a custom StraightStreamReader by writing 256 bytes to a file and reading them back with various read methods.
- 静态失败原因: Static BERT predicted non-clone (0), which aligns with our analysis; BCB label (1) seems incorrect, so the model did not fail here.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might consider them clones due to both being 'main' methods with similar boilerplate (stream handling, loops) and overall file I/O, but the actual functional purpose is very different.
- 共享行为: Both use file I/O and streams；Both have a try-catch structure for IOException；Both iterate over data using loops
- 行为差异: A downloads from a URL and unzips; B writes and reads a local test file；A uses ZipInputStream; B uses StraightStreamReader；A writes extracted files; B only writes and reads for verification；A has no verification logic; B has extensive correctness checks
- 修正建议: Re-evaluate BCB label for this pair；Improve annotation guidelines to focus on functional equivalence rather than structural similarity；Consider using semantic-based features to distinguish test code from utility code

### case_id=5488 FN benchmark_preference_bias

- 方法: `readPage` vs `login`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.7`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Reads a webpage line by line, optionally skipping comment lines starting with '#', and returns the content as a string.
- B 摘要: Logs into a service by sending a POST request with credentials, reads the response to extract a session ID, and returns it.
- 静态失败原因: The static BERT model likely detected low token similarity (Jaccard 0.157) and significant structural differences, so it correctly identified them as non-clones under strict semantics. However, it did not capture the broad functional similarity that BCB uses, leading to a false negative.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may label these as clones because both functions operate on URL streams, read lines from an HTTP response, and return a string. The broad category of 'network I/O' could be considered a functional similarity.
- 共享行为: Both use URL connections to access a web resource.；Both read data from an input stream using BufferedReader.
- 行为差异: Function A only reads; Function B writes data before reading.；Function A returns the full page content; Function B returns a session ID.；Function A has conditional logic to skip commented lines; Function B does not.；Function B sets a session variable; Function A does not.
- 修正建议: Incorporate training examples that are functionally similar but lexically different, e.g., diverse implementations of network I/O operations.；Use a broader definition of clone during training that includes Type-4 clones with different logic but same I/O patterns.

### case_id=5489 FP other

- 方法: `writeConfiguration` vs `readData`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.85`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Copies a configuration resource content to a Writer, handling null resource and closing stream.
- B 摘要: Reads from a file (or string) to populate multiple HashSets and a HashMap with parsed tokens, handling various columns and errors.
- 静态失败原因: The model may have been misled by the presence of I/O operations in both functions, or due to the long and complex nature of function B causing the model to incorrectly detect vague structural similarities.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB labels as non-clone because functions have entirely different purposes and implementations, with no overlap in semantics or logic.
- 共享行为: Both involve input/output operations (file/stream reading/writing)
- 行为差异: Function A writes configuration to output; function B reads and processes data into collections.；Function A uses IOUtils.copy; function B uses StringTokenizer and manual parsing.；Function A is simple; function B is long and complex with many states.
- 修正建议: Improve model to focus on overall functionality rather than superficial I/O presence.；Use data-flow and control-flow analysis to distinguish writing from reading.；Include more negative training samples with similar I/O but different logic.

### case_id=5490 FP boilerplate_overlap

- 方法: `main` vs `createTar`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Parses a Prolog file and generates adapter Java classes into a JAR file based on annotations.
- B 摘要: Creates a tar archive from all files in a given directory, handling null checks and overwriting.
- 静态失败原因: Static BERT/GraphCodeBERT models often over-rely on lexical or API-level overlap (e.g., File, IO streams, loops) and miss the high-level semantic difference of the overall task.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would label these as non-clones because they implement completely different functionalities and algorithms, despite sharing some I/O boilerplate.
- 共享行为: Both deal with file I/O operations；Both include null/argument validation and error handling；Both use logging or console output for status messages；Both iterate over collections (files or adapters)
- 行为差异: A generates Java bytecode and metadata; B creates tar archives；A uses Prolog parsing, class loading, and bytecode writing; B uses file reading and tar output streams；A is a main method entry point; B is a utility method；A produces a JAR and serialized object; B produces a single tar file
- 修正建议: Add contrastive training with hard negatives that share API but differ in goal；Incorporate structural or dataflow analysis to distinguish high-level intent；Use longer-range context or task-specific representations

### case_id=5491 FP lexical_or_api_overlap

- 方法: `readData` vs `copyFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Reads and parses multiple comma-separated strings into sets and maps for character/vowel/punctuation/syllable processing.
- B 摘要: Copies a file from source to destination using NIO channels.
- 静态失败原因: The static model likely overfitted to superficial patterns like common Java I/O keywords (e.g., 'IOException', 'File'), exception handling structures, or similar method declaration style, despite the extremely low token Jaccard.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels as non-clone because the functions have completely different purposes, code lengths, and logic, with minimal token overlap (Jaccard 0.018).
- 共享行为: Both involve I/O operations (file reading/writing).；Both handle exceptions (IOException).
- 行为差异: A is a large, complex parsing and initialization method; B is a simple file copy.；A reads and processes many static strings into various collections; B copies bytes from one file to another.；A has no file copying functionality; B has no string parsing or set population.
- 修正建议: Increase the token overlap threshold for clone detection.；Use graph-based representations (e.g., AST, data flow) to capture structural differences.；Train on more diverse negative samples to discourage matching on rare API co-occurrences.

### case_id=5492 FN benchmark_preference_bias

- 方法: `copy` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Recursively copies files from a Hadoop filesystem to a local directory, optionally deleting the source.
- B 摘要: Builds HTML pages for editing by transforming XML with XSLT, reading templates and writing output to files.
- 静态失败原因: Static BERT/GraphCodeBERT correctly predicted non-clone (0) due to very low token overlap (0.074) and vastly different code structure, so it did not fail.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as a clone due to both functions using 'FileSystem' and performing file operations, but this is a superficial similarity; the actual logic and purpose are entirely different.
- 共享行为: Both involve file I/O operations.
- 行为差异: Function A is a utility for file copying between filesystems.；Function B is a complex web page generation method with many parameters.；Function A uses recursion and handles directories.；Function B processes pages from a vector and uses XSLT transformation.
- 修正建议: Re-evaluate BCB label for this pair; likely a false positive in the benchmark.；If retaining as non-clone, use as a negative example for training.

### case_id=5493 FN partial_functionality

- 方法: `getHTML` vs `getXML`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches HTML from a URL, optionally writes to file, returns content as string.
- B 摘要: Fetches XML from a servlet URL, returns response as string, returns null on error.
- 静态失败原因: Static BERT relies on lexical overlap and syntactic patterns; low token Jaccard (0.246) and differing method names (getHTML vs getXML) or structures (HttpURLConnection vs openStream) caused it to miss the semantic similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB considers them as Type-4 clones because the core purpose (fetching URL content) is identical, and implementation differences like error handling and file writing are considered non-critical variations.
- 共享行为: Both fetch a web resource over HTTP；Both read the response line by line and accumulate into a string buffer；Both return the accumulated string
- 行为差异: getHTML writes to file if dirPath is provided; getXML does not；getXML URL-encodes the request parameter and appends to URL; getHTML does not；Error handling: getHTML prints stack trace and returns possibly empty string; getXML returns null；getHTML uses HttpURLConnection with a User-Agent header; getXML uses url.openStream() directly
- 修正建议: Use code structure (AST) or data flow graphs to capture semantics beyond token overlap；Augment training data with more semantically similar but lexically diverse pairs；Incorporate task-specific features like URL handling patterns

### case_id=5494 FN partial_functionality

- 方法: `getWebPage` vs `runScript`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches content from a given URL as a string using BufferedReader, throws Error on failure.
- B 摘要: Fetches content from a script file relative to code base as a string using byte reading, returns 'error!' on failure.
- 静态失败原因: The static model likely focused on low token overlap (0.125) and different method names and error handling patterns, missing the semantic similarity of retrieving URL content.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: Under BigCloneBench's broad Type-3/Type-4 clone definition, both functions implement the same high-level functionality: downloading a web resource as a string, despite differences in input, reading technique, and error handling.
- 共享行为: Open a URL connection and read all data into a string
- 行为差异: Input type: URL vs String；Reading method: line-by-line vs byte-by-byte；Error handling: throw Error vs return 'error!'
- 修正建议: Improve model's understanding of high-level I/O patterns (URL reading) and recognize that different reading loops can be semantically equivalent.；Use dataflow or graph-based representations that capture the resource flow.

### case_id=5495 FN lexical_or_api_overlap

- 方法: `doVersionCheck` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Checks for a new version by reading a version file from a URL, parsing version and build numbers, and comparing with the current build.
- B 摘要: Makes a POST request to a social network API with hardcoded parameters and prints the response.
- 静态失败原因: Model likely over-relied on lexical overlap of common API calls (URL, BufferedReader, readLine) and ignored the distinct semantic contexts and data handling logic.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB might have labeled as clone due to superficial similarities in network I/O boilerplate (URL, BufferedReader, readLine), but the overall functionality differs significantly.
- 共享行为: Both open a URL connection；Both read input line by line using BufferedReader；Both handle IOException
- 行为差异: Different HTTP methods: GET vs POST；Different data parsing and logic；Different output: message dialog vs console printing；Different parameter handling (property-based vs hardcoded)
- 修正建议: Incorporate data flow or control flow analysis；Train on more diverse examples to reduce reliance on surface-level patterns；Use contrastive learning to distinguish similar APIs with different semantics

### case_id=5496 FN partial_functionality

- 方法: `CheckUrl` vs `postXml`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches first line of HTTP GET response from a URL, returns empty string on error.
- B 摘要: Sends SOAP XML via HTTP POST with custom headers and reads full response, throws RuntimeException on error.
- 静态失败原因: Static BERT likely focused on low token overlap (Jaccard 0.22) and syntactic differences, missing the high-level intent due to different method names and code structure.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this as a clone because both functions perform HTTP requests and read the response, considering broad Type-4 functional similarity of 'making an HTTP request and retrieving the response'.
- 共享行为: Both open a URL connection and read the response using BufferedReader.；Both use HttpURLConnection when the URL protocol is HTTP.
- 行为差异: HTTP method: GET (A) vs POST (B).；Input: none (A) vs XML string and SOAPAction (B).；Output: first line only (A) vs entire response (B).；Error handling: prints stack trace and returns empty string (A) vs throws RuntimeException (B).
- 修正建议: Incorporate dataflow analysis to capture shared API usage patterns (URL, HttpURLConnection, BufferedReader).；Use AST-based or graph-based models to recognize similar control flow despite different method signatures.；Train with more examples of partial functional clones to learn broad equivalence.

### case_id=5497 FP boilerplate_overlap

- 方法: `googleImageSearch` vs `postXml`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Performs a Google image search via HTTP GET, downloads HTML, and extracts image URLs.
- B 摘要: Sends an XML SOAP request via HTTP POST and returns the response as a string.
- 静态失败原因: The static model likely overemphasized overlapping API calls (HttpURLConnection, BufferedReader) and structural patterns (try-catch, while loop), ignoring the semantic differences in HTTP method, data processing, and purpose.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically considers non-clones when functionality differs semantically, even if API usage is similar. Here, the purposes (image search vs XML POST) are distinct.
- 共享行为: Both use HttpURLConnection to make HTTP requests.；Both set request properties (User-Agent, Content-Type, etc.).；Both read response line by line using BufferedReader.；Both handle IOException.
- 行为差异: HTTP method: GET vs POST.；A sends no body, B sends XML payload.；A parses HTML for image URLs, B returns raw response.；A is void and populates a list, B returns a string.
- 修正建议: Incorporate method signatures and parameters into the representation.；Use dataflow analysis to capture how data is transformed (e.g., parsing vs forwarding).；Augment training data with diverse HTTP patterns to avoid overfitting on common boilerplate.

### case_id=5498 FP boilerplate_overlap

- 方法: `main` vs `readData`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Main function that creates a signed PDF using iText, loading a keystore and setting signature appearance.
- B 摘要: ReadData function that parses a configuration file to initialize sets and hash tables for Tibetan Wylie transliteration.
- 静态失败原因: Static BERT/GraphCodeBERT likely over-relied on lexical and API overlap (e.g., both use FileInputStream, try-catch blocks) and was misled by boilerplate code, ignoring the overall difference in high-level purpose.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would label non-clone because the two functions perform entirely different tasks with no semantic overlap.
- 共享行为: Both use file I/O and exception handling；Both iterate over tokenized data
- 行为差异: Function A signs a PDF; Function B initializes data structures for transliteration；Function A uses iText API; Function B uses StringTokenizer and HashSet
- 修正建议: Enhance model to capture program semantics beyond lexical similarity；Incorporate data-flow or control-flow embeddings；Use larger context windows to understand full function purpose

### case_id=5499 FP partial_functionality

- 方法: `doExecute` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Processes a multipart HTTP request to parse form fields and file attachments, then sends an email using a Send instance.
- B 摘要: Handles GUI action events for setting preferences like Graphviz path, image scaling, date format, and look-and-feel, updating UI components and storing preferences.
- 静态失败原因: The model likely over-relied on surface-level similarities such as common API calls (e.g., request, response, setAttribute), exception handling patterns, and long code blocks with multiple branches. It may have mistakenly grouped them as 'event handling' or 'data processing' functions.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely labels these as non-clones because they serve entirely different purposes (email sending vs. GUI settings), have different method signatures, and share no common functionality. The low token Jaccard supports this.
- 行为差异: Function A processes HTTP requests; function B handles GUI events.；Function A sends emails; function B updates application settings.；Function A uses Struts ActionForward; function B uses Swing components and JOptionPane.；Function A deals with file uploads and multipart content; function B deals with file choosers for exe paths.
- 修正建议: Incorporate structural matching (e.g., control flow graphs) to distinguish different logic paths.；Use method signature and class context to filter unrelated functions.；Train on more diverse examples to reduce overfitting on common API tokens.

### case_id=5500 FP lexical_or_api_overlap

- 方法: `main` vs `writeFileToFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Parses command-line arguments, reads a Prolog file, processes it to generate adapter classes and a JAR file.
- B 摘要: Copies the contents of one file to another using NIO FileChannels with optional append.
- 静态失败原因: The static model may have been misled by overlapping lexical tokens like 'File', 'IOException', 'try-catch', and 'return', which are common in many Java I/O functions, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels as non-clone because there is no functional overlap; even broad Type-4 requires some common purpose, which is absent here.
- 共享行为: Both perform file I/O operations (read and write).；Both handle IOException.
- 行为差异: Function A is a command-line entry point with complex workflow; B is a simple utility.；Function A parses Prolog, generates Java bytecode, and creates a JAR; B only copies raw bytes.；Function A depends on many external libraries; B uses only standard NIO.；Function A has conditional debug output; B has no such feature.
- 修正建议: Use data-flow-aware representations (e.g., graph neural networks)；Incorporate control flow and call dependencies.；Apply contrastive learning to distinguish similar boilerplate but different semantics.
