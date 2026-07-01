# Error Case Studies 3001-3500

- Source model: `configured-llm`
- Cases: `3001` to `3500`

### case_id=3001 FP lexical_or_api_overlap

- 方法: `getLinksFromURLFast` vs `downloadModel`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Extracts all hyperlinks and their text from an HTML page given a URL, using regular expressions and returning two Vectors.
- B 摘要: Downloads an RDF model from a URL using Apache Jena, handling HTTP headers and exceptions.
- 静态失败原因: The static BERT/GraphCodeBERT model likely overemphasized lexical and structural overlap (e.g., both use URL, openConnection, getInputStream) and ignored the different post-processing and return types, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels non-clones when functions perform different tasks despite sharing a common high-level pattern (e.g., network I/O). Since extracting links vs. loading an RDF model are distinct operations, BCB assigns label 0.
- 共享行为: Open URL connection and obtain InputStream；Read data from the web
- 行为差异: Different output types: Vector[] of links/texts vs. Model；A parses HTML for links using regex, B reads RDF model using Jena；A includes timing/debug output, B sets HTTP headers；A throws Exception, B catches specific exceptions and wraps as RuntimeException
- 修正建议: Train model to focus on operations after reading input stream (e.g., regex parsing vs. model loading)；Incorporate return type information into embeddings；Use data flow analysis to track how the input stream is processed further

### case_id=3002 FP lexical_or_api_overlap

- 方法: `import_hints` vs `getFrameworkFactory`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Imports hint pieces from a file or URL, parsing tokens and placing them on a game board.
- B 摘要: Retrieves and instantiates a FrameworkFactory by reading a service configuration file from the classpath.
- 静态失败原因: Static BERT/GraphCodeBERT models may have been misled by the structural similarity of using BufferedReader with URL and try-catch, focusing on token-level patterns without understanding the distinct semantic intents.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled non-clone because the functions have entirely different purposes and contexts, despite sharing some low-level I/O patterns. BCB prefers semantic similarity at a higher level, not just API usage.
- 共享行为: Both read from a URL or file using BufferedReader；Both iterate over lines and parse strings；Both use try-catch or exception handling
- 行为差异: A modifies game board state; B returns an object；A uses StringTokenizer; B uses string trimming and character checks；A has conditional URL/File reading; B always uses classloader resource；A returns boolean success/failure; B returns factory or throws exception
- 修正建议: Incorporate data flow or control flow analysis to capture functional intent；Use more diverse training examples with similar API sequences but different purposes；Enhance model understanding of high-level semantics through contrastive learning

### case_id=3003 FN partial_functionality

- 方法: `fileDownload` vs `loadMFileViaWeb`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a file from a URL and saves it to a hardcoded local file 'download.pdf'.
- B 摘要: Loads a MATLAB .m file from a URL, reads its content, parses it into a UserFunction, and returns it.
- 静态失败原因: Static BERT models rely on lexical overlap and structural similarity; the low token Jaccard (0.186) and differing method names, API calls, and overall purpose caused the model to miss the shared URL reading pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider them clones because the core functionality of opening a URL and reading its content is identical, and the additional processing (writing to file vs. parsing) is viewed as secondary in a broad Type-4 sense.
- 共享行为: Both open a URL connection and create an InputStream and BufferedReader；Both read data from the URL stream
- 行为差异: A writes raw bytes to a file; B concatenates lines into a string and parses as MATLAB code；A reads character-by-character; B uses readLine()；A returns void; B returns a UserFunction object；Error handling differs: A logs an exception; B throws a custom exception
- 修正建议: Use finer-grained sub-function matching to detect shared IO operations；Incorporate data flow analysis to identify common reading patterns；Train with contrastive examples that emphasize shared behavior despite different overall goals

### case_id=3004 FN partial_functionality

- 方法: `setBundleInfoName` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Updates BundleInfo names by reading key-value pairs from a configuration file at a given URL.
- B 摘要: Sends a fixed RenRen API POST request and prints the response.
- 静态失败原因: The static model relied on low token overlap and different method names/purposes, thus predicting non-clone, while BCB's label emphasized the shared I/O pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled as clone due to broad Type-4 similarity in the pattern of opening a URL, reading lines, and processing them in a loop, despite different purposes.
- 共享行为: Both open a URL connection and read lines using BufferedReader.
- 行为差异: Function A modifies a list passed as input; Function B prints output and does not modify inputs.；Function A returns a boolean; Function B returns void.；Function A parses lines for key-value pairs; Function B does not parse response lines for data extraction.
- 修正建议: Incorporate structural patterns like URL reading and line processing as clone indicators.

### case_id=3005 FP lexical_or_api_overlap

- 方法: `readTwitterFead` vs `getRequestContent`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads entire Twitter timeline JSON from a hardcoded URL using HttpClient and returns it as a string.
- B 摘要: Performs an HTTP GET request to a given URL and returns only the first line of the response.
- 静态失败原因: The static model likely over-relied on overlapping API tokens (BufferedReader, InputStreamReader, HttpGet, etc.) and the overall structure of HTTP GET, ignoring the critical semantic difference in how the response is consumed.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically requires functional equivalence or near equivalence for clone labeling. Despite both doing HTTP GET, the output differs fundamentally (full response vs first line), leading to a non-clone label.
- 共享行为: Both perform an HTTP GET request to retrieve remote content.；Both use BufferedReader and InputStreamReader to read the response.
- 行为差异: A uses Apache HttpClient, B uses java.net.HttpURLConnection.；A reads all lines and returns full content, B reads only the first line.；A handles errors with catch blocks, B throws Exception.；A uses a hardcoded URL, B takes URL as parameter.
- 修正建议: Enrich training data with pairs that share similar API usage but differ in output semantics.；Incorporate dataflow analysis to capture how response content is processed.；Fine-tune with contrastive examples where output length or transformation differs.

### case_id=3006 FN partial_functionality

- 方法: `readIntoList` vs `lookupFutureEvents`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads HTML from a URL, parses hyperlinks to create JMenuItem objects with action commands, and populates a Map.
- B 摘要: Reads JSON from a Meetup API, parses it to extract event details, creates Event objects, and returns a list.
- 静态失败原因: Static BERT models heavily rely on token-level similarity, which is very low here due to different vocabulary (HTML/JSON keys, JMenuItem vs Event). The structural similarity at a higher level (URL reading, line processing) is not captured by token-based embeddings.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider these clones because both functions follow a common 'read from URL, parse lines, and populate objects' pattern, ignoring specific domain logic. This aligns with Type-3/Type-4 clone acceptance of partial functionality similarity.
- 共享行为: Both open a URL and read lines using BufferedReader.；Both parse each input line to extract information.；Both populate data structures with parsed data.；Both handle exceptions with try-catch blocks.
- 行为差异: Input format: HTML vs JSON.；Output: Map<String, JMenuItem> vs List<Event>.；Parsing logic: extracting from HTML tags vs JSON keys.；Exception handling: prints stack trace vs throws custom exception.
- 修正建议: Incorporate structural features like AST or control-flow graph similarity.；Use data flow analysis to detect common read-parse-write patterns.；Train with contrastive learning that emphasizes high-level structural clones.

### case_id=3007 FP boilerplate_overlap

- 方法: `hash` vs `perform`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Computes MD5 hash of a string and returns hex encoded digest.
- B 摘要: Handles a web form action to classify a concept, involving session management, HTTP connection, and parsing XML.
- 静态失败原因: The static BERT/GraphCodeBERT likely overestimated similarity due to both functions containing try-catch blocks, error handling, and string manipulation, despite having completely different semantics and very low token overlap.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels non-clones when functions have no significant overlapping functionality, even if they share some superficial patterns like try-catch blocks or error logging.
- 行为差异: Function A is a utility hashing method; Function B is a web request handler.；Function A uses MessageDigest; Function B uses HttpSession, URLConnection, and XML parsing.；Function A is static and synchronized; Function B is an instance method of an Action class.；Function A returns a String; Function B returns an ActionForward.
- 修正建议: Enhance training with more diverse negative examples that include common boilerplate.；Incorporate dataflow analysis to distinguish utility functions from IO-heavy business logic.；Use method-level context like class hierarchy or API usage fingerprints.

### case_id=3008 FN benchmark_preference_bias

- 方法: `modifyApplicationMessage` vs `copyFileTo`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Modifies a properties file for a specific locale by reading, editing a property value, and writing back.
- B 摘要: Copies a file from source to destination using byte buffer.
- 静态失败原因: Static models rely heavily on lexical and structural similarity; the low token Jaccard (0.147) and different method names, control flow, and specific APIs lead to a non-clone prediction. They fail to capture the abstract high-level I/O similarity that the benchmark might emphasize.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may label this as a clone because both functions are file I/O operations that read input and write output, potentially falling under a broad 'file copy/modify' category in the benchmark's annotation guidelines, despite differing specific functionalities.
- 共享行为: Both perform file I/O: reading from a file and writing to a file.；Both use while loops to process data until end of stream.；Both involve handling of I/O exceptions (though A catches Exception broadly).
- 行为差异: A reads text lines and modifies based on key-value pairs; B copies raw bytes.；A has complex logic for property replacement, locale-specific file handling, and appending if not found; B is a straightforward copy.；A writes back to the original file (overwrites), while B writes to a different destination file.
- 修正建议: Incorporate functional hierarchy or topic modeling to recognize high-level I/O operations.；Use representations that capture intent (e.g., comment analysis, method summary).；Fine-tune on benchmark-specific clone definitions to align with annotation preferences.

### case_id=3009 FP partial_functionality

- 方法: `setBundleInfoName` vs `getFullScreenUrl`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a URL mapping bundle symbolic names to names and updates a list of BundleInfo objects.
- B 摘要: Reads a YouTube page to extract video parameters from a fullscreenUrl line and constructs a download URL.
- 静态失败原因: Static models may focus on overlapping tokens (URL, BufferedReader, readLine, try-catch) and similar structure, missing the semantic difference in purpose and return type.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB annotation likely considers them as different functionalities (update bundle names vs. extract YouTube video URL) and thus non-clone.
- 共享行为: Both open a URL and read lines via BufferedReader；Both parse lines for specific content；Both handle IOException with exception printing
- 行为差异: Function a returns boolean, function b returns String；Function a updates a parameter list, function b sets instance variables；Function a parses 'key=value' lines, function b searches for substring and splits on '&'；Input: a takes a location parameter, b uses an instance variable ytUrl
- 修正建议: Include function signature (return type, parameters) in input representation；Use data flow analysis to differentiate how results are used；Train with contrastive learning on functional behavior

### case_id=3010 FN partial_functionality

- 方法: `addDataFromURL` vs `runInternal`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads content from a URL line by line and appends to a text buffer.
- B 摘要: Downloads OPDS catalog or book from a URL with progress, error handling, and parsing.
- 静态失败原因: Static BERT models like GraphCodeBERT rely heavily on token overlap and structural similarity; the low Jaccard index and different control flow likely led to a false negative prediction.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considers both as 'URL content fetchers' despite implementation differences, viewing them as Type-4 clones with similar functionality.
- 共享行为: Both open a URL connection and read input data from it
- 行为差异: code_a appends lines to a single text buffer; code_b handles OPDS parsing, book downloading, progress, and callbacks；code_a has minimal error handling; code_b has extensive error handling and retry logic；code_a is synchronous and simple; code_b is asynchronous and complex
- 修正建议: Enhance model with data flow analysis to capture shared I/O behavior；Use contrastive learning on partial functionality patterns；Incorporate call graph or API usage similarity for URL connection patterns

### case_id=3011 FN partial_functionality

- 方法: `doTransfer` vs `run`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Acts as an HTTP proxy, forwarding client requests to a target URL and streaming the response back.
- B 摘要: Reads a URL's response line by line, parses the first two lines as version and URL, and stores the rest as a string.
- 静态失败原因: Static BERT models rely on syntactic and lexical overlap, which is low here (Jaccard 0.164). The methods differ significantly in structure, API calls, and control flow, leading the model to miss the shared high-level semantic of HTTP resource fetching.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considers these clones because both perform HTTP GET-like fetching of a URL resource and process the response, a common high-level functionality pattern that BCB sometimes labels as Type-4 clones despite syntactic differences.
- 共享行为: Both open an HTTP connection and read the response stream；Both handle IOException by printing stack trace
- 行为差异: Only A sets request headers and body and sends a full HTTP request; B only reads from a URL；A forwards the response to the client output stream; B parses specific lines and notifies listeners；A supports any HTTP method; B implicitly uses GET；A handles response codes and errors; B only checks for specific exceptions
- 修正建议: Enhance the model with data-flow analysis to detect common network I/O patterns；Incorporate functional similarity metrics that recognize overlapping sub-tasks；Augment training data with more diverse Type-4 clone examples

### case_id=3012 FP lexical_or_api_overlap

- 方法: `loadMFileViaWeb` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Loads a MATLAB function file from a URL and parses it into a UserFunction object.
- B 摘要: Searches Google Images for album art and extracts image URLs from the HTML response.
- 静态失败原因: Static BERT/GraphCodeBERT likely overemphasized lexical overlap in URL-opening and stream-reading patterns (e.g., 'URL url = new URL', 'BufferedReader', 'readLine'), treating this boilerplate as evidence of semantic similarity while ignoring the distinct core logic and method purpose.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled as non-clone because the functions perform completely different tasks; the only overlap is generic I/O boilerplate, which is insufficient for clone classification under BCB's emphasis on functional similarity.
- 共享行为: Both open a URL connection；Both read lines from the response and concatenate them into a string；Both use exception handling (try-catch)
- 行为差异: Different URL construction (one uses URL with codeBase, the other uses HttpURLConnection with user-agent)；Different parsing of response data (one reads plain text, the other parses HTML for image links)；Different outputs (one returns a UserFunction, the other modifies a list of images)；B checks conditional (artist changed) before executing; A does not
- 修正建议: Incorporate dataflow and structural information to distinguish core logic from boilerplate；Use method name, parameters, and return type as semantic clues；Train with more negative examples containing similar I/O patterns but different functionality

### case_id=3013 FN benchmark_preference_bias

- 方法: `doGet` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Handles HTTP GET request to display a portal page, with authentication, logging, and caching.
- B 摘要: Copies a file from source to destination using NIO FileChannel.
- 静态失败原因: Static BERT did not fail; it correctly predicted non-clone, agreeing with the analysis that these are not similar.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled as clone due to both functions containing file writing logic (e.g., FileWriter in A vs FileOutputStream in B), but the overall functionality is vastly different.
- 共享行为: Both involve file operations (reading/writing) but in entirely different contexts.
- 行为差异: Function A is a web servlet handler with complex control flow; Function B is a simple utility for file copying.；Function A uses file I/O only as a minor caching side-effect; Function B's sole purpose is file copying.；Function A depends on HTTP request/response objects and portal framework; Function B has no such dependencies.；The APIs and data types used are completely different.
- 修正建议: Re-evaluate BCB label; these functions are not clones under any reasonable definition.；Ensure benchmark annotations are consistent and not overly broad.

### case_id=3014 FN partial_functionality

- 方法: `testTrainingBackprop` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Tests neural network backpropagation training using FANN library with incremental algorithm and checks mean squared error.
- B 摘要: Launches a NexOpen Eclipse project configuration, setting up Maven POMs and Hibernate dialect, then runs an install action.
- 静态失败原因: Static BERT models rely heavily on token overlap and structural similarity. The low Jaccard similarity (0.04661) and the difference in domain-specific APIs (FANN vs. Eclipse) led the model to assign a low similarity score. The model failed to capture the abstract shared behavior of file I/O and property setting because it lacks understanding of high-level functional roles.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as sharing the high-level pattern of 'file I/O and configuration setup' even though they belong to different domains, thus labeling them as Type-4 clone due to partial functional similarity in resource management.
- 共享行为: Both use IOUtils.copy to copy data from input stream to output stream；Both create files (temporary or project files) and handle file existence；Both set configuration properties (FANN training algorithm vs. Hibernate dialect)；Both handle exceptions (throws IOException or catches CoreException)
- 行为差异: Function A is a unit test for neural network training; Function B is an Eclipse launch configuration handler for Maven project setup；A uses FANN library-specific API; B uses Eclipse and Maven APIs；A is concise with a linear flow; B has multiple nested conditionals and callbacks；A's purpose is to verify training error; B's purpose is to modify project files and trigger build
- 修正建议: Incorporate graph-based code representations (e.g., dataflow or control flow graphs) to capture structural patterns beyond token sequences.；Use transfer learning on tasks that emphasize functional roles, such as code summarization or API usage pattern recognition.；Augment training data with more Type-4 examples that share only partial semantics.

### case_id=3015 FN benchmark_preference_bias

- 方法: `runInternal` vs `PhoneSetImpl`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `preference_memory_with_manual_audit`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Handles HTTP connection, parses OPDS catalog, and downloads books with pagination.
- B 摘要: Reads a phone list from a URL, parses lines, and builds a map.
- 静态失败原因: Static BERT/GraphCodeBERT relies heavily on token overlap and structural similarity; the low Jaccard similarity (0.058) and different method names led to a non-clone prediction, but BCB considers broader functional similarity.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may label this as a Type-3 clone because both methods involve reading from a URL and processing lines, despite vastly different functionality and complexity.
- 共享行为: Both open a URL connection and read data；Both parse lines of input；Both ignore certain lines (A uses handler, B skips lines starting with ***)
- 行为差异: A handles HTTP redirects, timeouts, and content types; B does not；A downloads files; B only reads text；A uses complex pagination; B processes all lines sequentially；A has extensive error handling and progress reporting; B has minimal error handling
- 修正建议: Train with more examples of broad functional clones；Incorporate higher-level semantic features like API usage and data flow；Use contrastive learning to capture abstract similarity

### case_id=3016 FP lexical_or_api_overlap

- 方法: `main` vs `copyFileByNIO`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: A main method that parses command line arguments, reads a Prolog file, and generates adapter classes into a JAR file.
- B 摘要: A utility method that copies a file using NIO FileChannels.
- 静态失败原因: The model likely over-relied on lexical overlap of common words like 'File', 'IOException', and 'static void', along with similar method signatures, ignoring the entirely different program logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB requires functional similarity for clone labeling; these two methods perform entirely different tasks (code generation vs. file copy), so they are clearly non-clones.
- 共享行为: Both are public static void methods that perform file I/O operations.
- 行为差异: Function A parses arguments, reads and parses Prolog code, generates adapter classes, and writes multiple JAR entries; Function B simply copies a single file.；A uses Apache Commons IO and ASM libraries; B uses only standard NIO.；A has complex error handling and debug output; B throws IOException on failure.
- 修正建议: Incorporate dataflow analysis to distinguish core functionality.；Use control flow graph similarity that captures structural differences.；Add attention to method-level semantics rather than token-level matching.

### case_id=3017 FN boilerplate_overlap

- 方法: `extractResourceToFile` vs `modifyApplicationMessage`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.6`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Extracts a classpath resource to a file by copying bytes using IOUtils.copy.
- B 摘要: Modifies an internationalization properties file by replacing or adding a key-value pair.
- 静态失败原因: Static BERT/CodeBERT models rely on token embeddings and may focus on common boilerplate code (try-finally, stream opening/closing) while missing the distinct core semantics. The low token Jaccard suggests limited lexical overlap, but the structural patterns are common across Java functions, leading to false negative.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may consider these clones due to overlapping file I/O structure and resource handling patterns, despite different core logic. The annotation guidelines might accept broad Type-3/Type-4 similarity where both functions perform resource extraction and file writing.
- 共享行为: Open input stream from classpath resource；Open output stream to file；Copy data from input to output；Close streams in finally blocks
- 行为差异: Function A copies bytes verbatim; function B reads lines, parses key-value pairs, and modifies content.；Function A uses IOUtils.copy for bulk copy; function B uses manual line-by-line reading and writing.；Function B conditionally copies an English file if locale-specific file missing; function A does not.；Function B writes modified properties back; function A writes exact resource content.
- 修正建议: Incorporate dataflow analysis to track actual data transformations and distinguish boilerplate from core logic.；Use contrastive learning or augmented training with negative examples that share structural boilerplate but differ in semantics.；Enhance model with representation of control flow and data dependencies, not just token sequences.

### case_id=3018 FN benchmark_preference_bias

- 方法: `testSimpleQuery` vs `getFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.1`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: A test method that sets up JCR data, runs an XPath query, and verifies the result.
- B 摘要: A utility method that downloads a WSDL file from a given URL, modifies its SOAP address, and saves it to a temporary location.
- 静态失败原因: The static model correctly identified these as non-clones due to low token overlap and distinct API usage; the L0 token Jaccard of 0.054 strongly indicates no clone.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: The BCB annotation may be erroneous or based on very broad criteria that consider any I/O or stream usage as similar, which is unlikely.
- 行为差异: testSimpleQuery tests a JCR repository query; getFile downloads and modifies a WSDL file.；testSimpleQuery writes XML content to JCR sources; getFile reads a WSDL from a URL and writes to disk.；testSimpleQuery uses JCR API; getFile uses Java I/O and XML DOM manipulation.；testSimpleQuery has no file handling or network operations; getFile explicitly handles URLs, file channels, and XML parsing.
- 修正建议: Review BCB annotation for this pair; likely a labeling error.；Use a more rigorous semantic matching threshold or human verification for edge cases.

### case_id=3019 FN benchmark_preference_bias

- 方法: `decodeFileToFile` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Decodes a Base64 encoded file and writes the decoded content to an output file, returning success status.
- B 摘要: Launches a configuration for a NexOpen project in Eclipse, processing XML files, setting properties, and handling project resources.
- 静态失败原因: Static BERT methods rely on token overlap and AST patterns; the low Jaccard similarity (0.06) and vastly different domains led to a correct non-clone prediction, but BCB's label is erroneous.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled these as clones due to both containing try-catch-finally blocks, file stream handling, and similarity in variable names like 'in', 'out', 'buffer', but this interpretation is weak and not justified.
- 共享行为: Both involve file I/O operations with error handling.
- 行为差异: Function A decodes Base64 data; Function B does not.；Function A returns boolean success; Function B returns void.；Function B reads and modifies project configuration and XML; Function A only copies decoded bytes.；Function B uses Eclipse framework and Maven structures; Function A is standalone.
- 修正建议: Re-evaluate BCB annotation for this pair; likely a false positive in BCB rather than a model error.；If maintaining BCB label, improve model to capture broader patterns like generic I/O error handling, but this is not recommended.

### case_id=3020 FN lexical_or_api_overlap

- 方法: `updateFile` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.4`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a file to a new location after manipulating its path.
- B 摘要: Retrieves a resource by URL, caches it locally, and returns an InputStream.
- 静态失败原因: Low token overlap (Jaccard 0.13) and different vocabulary (e.g., FileChannel vs HTTPConnection) mislead the model to focus on surface-level differences.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may consider them clones because both perform data transfer from a source to a local file, with similar exception handling and resource management patterns.
- 共享行为: Both involve file I/O operations；Both create directories if needed；Both close streams/channels in finally block
- 行为差异: updateFile copies between local files; getResourceAsStream may fetch over network；updateFile uses NIO FileChannel; getResourceAsStream uses BufferedInputStream/OutputStream；getResourceAsStream has caching logic; updateFile does not；Return types differ: void vs InputStream
- 修正建议: Incorporate structural similarity like control flow graphs；Use models that capture file I/O patterns beyond token overlap

### case_id=3021 FP lexical_or_api_overlap

- 方法: `writeFileType` vs `checkForUpgrade`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads URIs from a file, fetches their content, classifies as OWL/RDFS/RDF/UNKNOWN/BROKEN, and writes results to an output file.
- B 摘要: Checks for software upgrade by querying database and remote server, processes license validation, and updates UI and database with upgrade records.
- 静态失败原因: The static model likely over-relied on surface-level API similarities (URL, URLConnection, BufferedReader, try-catch) and common boilerplate for network I/O, ignoring high-level semantic differences.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labeled non-clone because overall functionality is completely different; low token Jaccard and differing purposes outweigh API-level similarities.
- 共享行为: Both use java.net.URL and URLConnection to open HTTP connections.；Both use BufferedReader to read from input streams.；Both use try-catch blocks for exception handling.；Both involve loops and string manipulation.
- 行为差异: A processes URIs to classify RDF data; B checks for software upgrades via HTTP and database.；A writes classification results to a file; B updates UI components and database records.；A has simple boolean checks; B includes complex business logic (license validation, upgrade management).
- 修正建议: Train on hard negative pairs with similar API usage but different semantics.；Use contrastive learning to emphasize functional purpose over boilerplate.；Incorporate dataflow or abstract semantic representations.

### case_id=3022 FN partial_functionality

- 方法: `fileDownload` vs `run`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.75`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a file from a given URL and writes it to a fixed filename 'download.pdf' in a specified directory.
- B 摘要: Downloads content from a URL with basic authentication, reads lines, and accumulates the response into a string, updating state fields.
- 静态失败原因: Static BERT models rely heavily on token overlap and surface syntax; with a low Jaccard similarity (0.1685) and different method names ('fileDownload' vs 'run'), the model fails to capture the deeper functional similarity of URL downloading. The differing API usage (FileOutputStream vs base64) further distracts the model.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely labels this as a clone because both functions perform the high-level task of downloading content from a URL, a common pattern in Java. The differences in authentication, output method, and reading granularity are considered acceptable variations for a Type-4 semantic clone.
- 共享行为: Both open an HTTP connection to a URL and read the response stream.；Both use BufferedReader to read the response content.；Both handle IOException by catching exceptions.
- 行为差异: A writes bytes to a file; B reads lines into a StringBuffer.；B includes HTTP basic authentication; A does not.；A uses a fixed output filename; B stores result in a field.；A reads bytes (int) from BufferedReader; B reads lines of text.
- 修正建议: Train with data flow graphs that capture I/O operations and their destinations.；Use code summarization to abstract idioms like 'download content from URL'.；Incorporate functional labels from code comments or method names via cross-modal learning.

### case_id=3023 FP lexical_or_api_overlap

- 方法: `doImageProcess` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Processes an HTTP request to serve an image, optionally resizing it.
- B 摘要: Handles GUI action events for setting preferences like executable paths and display options.
- 静态失败原因: The model likely overemphasized overlapping tokens like 'image', 'File', 'OutputStream' and similar control flow structures, ignoring the different domains and purposes.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would not label this as a clone because there is no semantic similarity; the functions perform entirely different tasks.
- 共享行为: Both functions involve input/output operations (stream vs. file chooser) and conditional logic.
- 行为差异: Function A is server-side image processing; Function B is client-side GUI event handling.；Function A deals with HTTP response output streams; Function B deals with file chooser dialogs and UI updates.；Function A has no user interaction; Function B has extensive user interaction through Swing components.
- 修正建议: Improve model's ability to distinguish domain-specific contexts.；Incorporate data flow and program dependency graphs to capture semantic differences.

### case_id=3024 FN benchmark_preference_bias

- 方法: `doGet` vs `gzip`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.3`
- 推荐路线: `preference_memory_with_manual_audit`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Handles HTTP GET requests for portal pages with permission checks, caching, and logging.
- B 摘要: Compresses a file from a directory into a GZIP archive.
- 静态失败原因: Low lexical overlap (token Jaccard 0.07) and different method lengths, plus heavy use of servlet-specific APIs in A vs. standard Java I/O in B, caused the model to predict non-clone.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as a clone based on a high-level similarity in data processing and output generation, considering both as Type-4 semantic clones despite vastly different domains.
- 共享行为: Both perform I/O operations；Both handle exceptions
- 行为差异: A is a web request handler, B is a file compression utility；A involves complex control flow with multiple conditions, B is a straightforward sequential read-write；A uses servlet-specific APIs, B uses standard Java I/O
- 修正建议: Enhance model to capture abstract dataflow patterns；Incorporate type-aware embeddings to recognize common I/O operations

### case_id=3025 FN benchmark_preference_bias

- 方法: `fileDownload` vs `readData`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Downloads a file from a URL and saves it to a local directory.
- B 摘要: Reads configuration data, tokenizes comma-separated strings, and populates multiple sets and maps for Tibetan text processing.
- 静态失败原因: The static model correctly identified non-clone based on low lexical overlap and different functionality; it failed to match the BCB label, which appears to be based on non-functional or project-level similarity.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as clone due to both functions involving I/O operations (reading from URL/file) or being from the same project, despite completely different domain-specific functionality.
- 行为差异: Function A performs a simple file download from a URL; function B performs complex parsing of configuration data with multiple tokenizations and set population.；A uses URLConnection and BufferedReader/Writer; B uses StringTokenizer and manages multiple domain-specific sets (topSet, leftSet, etc.).；A outputs to a file; B builds internal data structures with no file output.；A has minimal error handling (catch Exception); B has detailed error handling with domain-specific exceptions.
- 修正建议: If the goal is to match BCB annotations, incorporate project-level or meta-information into the model to capture broad similarity criteria.；Alternatively, if the goal is functional equivalence, the model is correct and BCB labeling may be noisy.

### case_id=3026 FN partial_functionality

- 方法: `getHTML` vs `getURLContent`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches HTML from a URL with specified encoding and optional file writing.
- B 摘要: Fetches URL content as a string, detecting encoding automatically.
- 静态失败原因: Static BERT/GraphCodeBERT likely focused on lexical differences such as method name, parameters, connection type, and file I/O, missing the core behavior of reading URL content line by line.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB typically treats two functions as clones if they share the same core functionality (fetching URL content into a string) despite minor differences in parameterization, connection handling, or optional file I/O.
- 共享行为: Open a URL connection；Read lines from input stream；Build a string buffer with lines；Return the content as a string
- 行为差异: A uses HttpURLConnection and sets User-Agent; B uses URLConnection；A appends "\r\n"; B appends '\n'；A optionally writes to a file; B does not；A has exception handling (printStackTrace); B uses try-finally for closing reader
- 修正建议: Incorporate data-flow analysis to capture core data transformations；Train on more diverse Type-3/Type-4 clones with varied API usage；Use contrastive learning to emphasize shared algorithm over surface differences

### case_id=3027 FP boilerplate_overlap

- 方法: `readUNI` vs `doVersionCheck`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads tab-separated lines from a URL and adds concatenated id and description to a vector.
- B 摘要: Checks for a new version by reading version and build numbers from a URL and displays appropriate messages.
- 静态失败原因: Static BERT/GraphCodeBERT likely overweights the lexical overlap of URL, openStream, readLine, and close, plus the looping structure, while missing the semantic differences in parsing logic and output usage.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled non-clone because the overall functionality is distinct (generic data reading vs. version check), despite shared IO boilerplate. BCB often requires behavioral similarity beyond superficial patterns.
- 共享行为: Both open a URL input stream；Both read lines of text from the stream；Both parse each line to extract specific data；Both close the stream in a finally block
- 行为差异: A uses Scanner to split on tabs; B uses BufferedReader and checks string prefixes；A extracts three fields (id, skip, desc); B extracts version and build；A outputs to a Vector; B displays GUI messages；Error handling: A swallows exceptions and prints stack trace; B shows error dialog
- 修正建议: Incorporate dataflow analysis to track how parsed data is used；Use fine-grained API call sequence matching beyond IO setup；Include models that capture variable types and method signatures

### case_id=3028 FP other

- 方法: `readData` vs `testStandardTee`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Parses and initializes multiple sets and maps from tokenized strings for Tibetan transliteration processing.
- B 摘要: Unit test that copies a string to two writers using TeeWriter and verifies equality and byte count.
- 静态失败原因: The model likely produced a false positive due to spurious correlation, possibly from common Java API tokens like 'StringTokenizer' or 'HashSet' appearing in both, despite vastly different contexts.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB non-clone label is correct because the functions have completely different purposes, inputs, outputs, and logic; they are not functionally related.
- 共享行为: No shared behavior
- 行为差异: Function A is a complex data initialization method with error handling; Function B is a simple test case.；Function A reads from static string fields; Function B creates a StringReader.；Function A uses StringTokenizer; Function B uses IOUtils.copy.；Function A modifies multiple global collections; Function B checks output and length.
- 修正建议: Improve training data with more diverse negative pairs to avoid spurious matches.；Add more emphasis on structural and dataflow differences.

### case_id=3029 FN library_context_missing

- 方法: `addIDs` vs `load`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.75`
- 推荐路线: `context_recovery_then_expert`；动态可解性: `low`；执行优先级: `medium`
- A 摘要: Parses HTML from a metabolomics website to extract and set various IDs and scores onto a PeakListRow.
- B 摘要: Downloads XML from pastebin using an ID and returns the content as a string.
- 静态失败原因: Static BERT embeddings rely on token overlap and surface form similarity, which is low (Jaccard 0.169) due to different domain-specific terms (Metabolites, Analytes vs pastebin). It missed the underlying pattern of HTTP GET and buffered reading.
- 静态 case study: 该类错误缺少关键上下文或需要深层语义，纯静态方法不可靠。
- 动态 case study: 动态执行价值较低：样本可能依赖库、框架、网络、GUI、数据库或项目上下文，需要先恢复环境或 mock 依赖。
- BCB 偏好解释: BCB may view both as 'download data from URL and process lines', considering them functionally similar at a high level despite different specifics.
- 共享行为: Both open a URL connection and read lines with BufferedReader；Both handle IOException via try-catch
- 行为差异: Function a parses HTML with specific patterns (href, td) to extract multiple fields and sets them on a row; function b simply concatenates all lines without parsing；Function a returns an integer score; function b returns a concatenated string；Function a modifies a PeakListRow object externally; function b has no side effects
- 修正建议: Use code representation that captures API call sequences and control flow structure；Augment training with functional-level clone examples sharing structural patterns despite different variable names

### case_id=3030 FN benchmark_preference_bias

- 方法: `getFile` vs `testLoadSource`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Downloads a WSDL file from a URL, modifies its endpoint attribute, and returns the local file path.
- B 摘要: Loads an article source from a Data Access Object for a given metadata id, reads it, and asserts that the content contains a specific string.
- 静态失败原因: The static model correctly predicted non-clone based on low token overlap and clear task differences; the false negative arises from BCB's possibly overbroad annotation.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled them as clones due to both involving resource downloading/loading and stream handling, but the overall functionality is distinct.
- 共享行为: Both involve accessing remote resources (URL vs DAO) and handling input streams.
- 行为差异: Different domain: WSDL service vs arXiv article.；Different output: returns a file path vs void test method with assertions.；Function A includes XML manipulation and file operations; Function B only reads and asserts content.
- 修正建议: Use fine-tuned classifiers on domain-specific datasets.；Incorporate structural information like AST or data flow to capture divergent logic.

### case_id=3031 FP boilerplate_overlap

- 方法: `createDialogArea` vs `downloadModel`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Creates a dialog area for a license dialog, reads a license file from a bundle resource, and displays it in a browser or text widget.
- B 摘要: Downloads an RDF model from a URL via HTTP, reads the model from an InputStream, and returns it.
- 静态失败原因: The static BERT model likely overemphasized the common boilerplate patterns (InputStream, try-catch-finally, IOException handling) and missed the distinct high-level intents and data types. It may have also failed to leverage method names or class contexts that clearly differentiate the tasks.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically annotates clones as similar in functionality. Here, the functions have entirely different purposes (UI layout vs data retrieval) and produce different types of outputs. The shared low-level I/O patterns are not sufficient for BCB to consider them clones, as the high-level semantics differ completely.
- 共享行为: Both open an InputStream and read data.；Both handle IOExceptions and close streams in finally blocks.
- 行为差异: A builds a UI composite with widgets; B returns a Model object.；A reads from a local bundle resource; B reads from a URL connection with HTTP headers.；A sets text on a widget; B reads the stream into a model and returns it.；A handles multiple widget creation and browser fallback; B handles HTTP connection setup and different error handling (throws RuntimeException).
- 修正建议: Incorporate method name and class context into the representation.；Use dataflow analysis to track the types and purposes of variables (e.g., Composite vs Model).；Train on more diverse examples of non-clones with shared low-level patterns to reduce false positives.

### case_id=3032 FP lexical_or_api_overlap

- 方法: `scrapeForIsbns` vs `getTicketsForQueue`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Scrapes ISBN-10 codes from a URL's HTML content using regex pattern matching.
- B 摘要: Retrieves open tickets for a given queue from a REST API, parsing response lines for ticket IDs.
- 静态失败原因: Static BERT/GraphCodeBERT likely focused on superficial lexical and API overlaps (BufferedReader, line reading, error handling) without capturing the distinct high-level goals.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically requires functional similarity (Type-3/4) to label as clone; these functions perform entirely different tasks despite some structural overlap.
- 共享行为: Both use BufferedReader to read line by line from a remote resource.；Both parse each line to extract specific data patterns.；Both involve network I/O and handle exceptions.
- 行为差异: Function A opens a URL stream directly; Function B constructs an HTTP GET request with query parameters.；Function A matches regex for ISBN-10; Function B checks for lines starting with 'ticket/'.；Function A stores matches in a set and counts; Function B accumulates ticket IDs then fetches each ticket via another call.；Function A has retry logic for connection; Function B has different error handling patterns.
- 修正建议: Incorporate data flow analysis to capture the different output types and processing pipelines.；Use structural similarity that emphasizes method names and comments.；Augment training data with more non-clone pairs that share common I/O patterns but differ in purpose.

### case_id=3033 FP lexical_or_api_overlap

- 方法: `getRequestContent` vs `lookupFutureEvents`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `1.0`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches a single line from a given URL and returns it.
- B 摘要: Fetches JSON from a Meetup API, parses it, and constructs a list of Event objects.
- 静态失败原因: Static BERT likely focused on overlapping API calls (URL, BufferedReader) and ignored the divergent control flow and data processing.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels as non-clone because the functions have completely different purposes and output types.
- 共享行为: Both use URL and BufferedReader to read from a URL.
- 行为差异: A reads one line and returns it; B reads multiple lines and parses JSON.；B performs complex data extraction and object mapping; A does not.
- 修正建议: Use graph-based code representations that capture dataflow and control dependencies.；Train on function-level semantics rather than token sequences.

### case_id=3034 FP boilerplate_overlap

- 方法: `handler` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a web page and extracts substrings based on configurable include and delimiter strings, updating a map.
- B 摘要: Searches Google Images, parses image URLs from the response, and updates a UI component with an image.
- 静态失败原因: The static model likely focused on lexical and structural similarities (try-catch, URL, BufferedReader, while loop) and missed the distinct functional semantics and different data flows.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labeled as non-clone because the two functions have entirely different purposes and core logic, despite sharing boilerplate networking code.
- 共享行为: Both open a URL connection；Both read input line by line using BufferedReader；Both catch exceptions
- 行为差异: Different input parameters (Map+TargetPage vs search string+start index)；Different parsing logic (substring extraction per map entry vs regex split for image URLs)；Different output (update map vs update UI and list)；Function B includes UI interaction and image loading, not present in A
- 修正建议: Incorporate dataflow analysis to track variable usage and output differences；Train on more diverse examples to reduce weight of common boilerplate patterns；Consider method signatures and return types as additional features

### case_id=3035 FN partial_functionality

- 方法: `readRemoteFile` vs `runInternal`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a remote file line by line and returns concatenated string.
- B 摘要: Opens an HTTP connection to download or parse OPDS catalog entries with pagination and callbacks.
- 静态失败原因: Static BERT/GraphCodeBERT probably relied on token overlap and control flow structure, which are very different; it missed the high-level semantic similarity of the URL reading loop.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely views both as Type-4 clones because they share the core pattern of reading from a URL connection in a loop until EOF, despite large differences in complexity and purpose.
- 共享行为: Open a URL connection；Read data in a loop until completion；Handle IO exceptions
- 行为差异: A returns a simple string; B triggers callbacks and downloads files；A only reads text; B handles HTTP headers, status codes, content types；A has no pagination; B implements pagination and conditional loading；A is a utility method; B is part of an Android GUI with progress updates
- 修正建议: Enhance models to detect shared I/O loop patterns via data-flow or control-flow graphs；Include training examples of partial functionality clones where one function is a subset of another；Use abstract representations of HTTP read operations

### case_id=3036 FP partial_functionality

- 方法: `run` vs `load`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a tile from a URL, parses it into vector geometries, and adds them to a data layer.
- B 摘要: Downloads XML content from a hardcoded pastebin URL and returns it as a string.
- 静态失败原因: Static BERT models may over-rely on structural similarity in the URL reading code (BufferedReader, while loop, line concatenation) while ignoring the divergent context and purpose of the two functions.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB typically requires more substantial functional overlap; the URL-reading pattern is generic and common to many programs, so it alone is insufficient for a clone label.
- 共享行为: Both open a URL and read its content line by line into a string.
- 行为差异: Function A processes the downloaded data into geometry objects and adds them to a layer; Function B simply returns the raw XML string.；Function A uses synchronization and a key-based deduplication mechanism; Function B uses a static working flag.；Function A handles multiple protocols (file, http); Function B only uses http.；Function A integrates with a data loader and display cache; Function B shows a dialog on error.
- 修正建议: Improve models to consider higher-level semantics beyond common I/O patterns.；Incorporate method context (class, surrounding methods) to differentiate utilities from specialized processing.

### case_id=3037 FN partial_functionality

- 方法: `httpRequestByPOST` vs `run`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends HTTP POST request with parameters, reads response body, returns response string or null on error.
- B 摘要: Opens HTTP connection to fixed URL, reads and discards response lines, catches exceptions, no return value.
- 静态失败原因: Low token overlap (Jaccard 0.19) and structural differences (different method signatures, API classes used) caused the model to miss the broad functional similarity of performing an HTTP request and reading the response.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often treats any HTTP request with response reading as functionally similar (Type-4 clone), even if methods differ in request type, parameters, and return value.
- 共享行为: Both perform an HTTP request and read the response via BufferedReader.
- 行为差异: A uses POST with parameters; B uses GET to a fixed URL.；A returns a response string; B returns void.；A checks HTTP status code and handles errors; B only catches exceptions without status checking.；A has a timeout parameter; B does not.
- 修正建议: Incorporate semantic graph or AST-based flow analysis to detect common patterns like HTTP request-response.；Leverage API usage embedding to recognize similar library calls (e.g., HttpClient vs URL.openStream).；Use contrastive learning with pairs that are functionally similar but syntactically different.

### case_id=3038 FN benchmark_preference_bias

- 方法: `modifyApplicationMessage` vs `WebmillDeploy`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Modifies a locale-specific properties file by adding or updating a message key-value pair.
- B 摘要: Deploys a web application by processing a WAR file, rewriting XML configurations, and creating a new WAR.
- 静态失败原因: The static model correctly identified the low lexical overlap and distinct domain-specific APIs, but it failed to recognize the broad similarity in file-processing structure that BCB might have considered.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled these as clones due to a subjective interpretation of both methods performing 'file modification' involving reading, processing, and writing, despite vast differences in purpose and domain.
- 共享行为: Both perform file I/O operations involving reading and writing files.
- 行为差异: Code A handles properties files for localization; Code B handles JAR/WAR files for web deployment.；Code A modifies a single key-value pair; Code B parses and rewrites multiple XML files.；Code A uses Properties and BufferedReader; Code B uses JarFile, JarOutputStream, and Document parsing.；Code A's output is a modified properties file; Code B's output is a new WAR file.
- 修正建议: Incorporate structural or behavioral clone detection to capture high-level file-processing patterns.；Re-evaluate BCB labels for consistency against explicit clone definitions.；Use data-flow analysis to differentiate between unrelated file operations.

### case_id=3039 FN lexical_or_api_overlap

- 方法: `copyResource` vs `execute`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copy resource from a URL or file to a destination file using byte streams.
- B 摘要: Read a source file, optionally create parent directories, and write converted content to a destination file using character streams with logging and error handling.
- 静态失败原因: Low token Jaccard (0.156), different method names, and structural differences such as try-catch blocks cause the model to miss the common file copying pattern.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may consider both as file copying operations despite differences in stream types and additional functionality, treating them as semantically similar (broad Type-4 clone).
- 共享行为: Both read from a source and write to a destination file；Both open input and output streams；Both close streams after copying
- 行为差异: A uses byte streams, B uses character streams；A can read from URL or file, B only from file；B includes conversion logic and logging；B has more extensive error handling and cleanup
- 修正建议: Enhance representation to capture common IO patterns (e.g., read-write loops)；Include dataflow analysis to track source-destination relationships；Use fine-tuning with more diverse file-copy examples

### case_id=3040 FN partial_functionality

- 方法: `testNetworkHTTP` vs `register`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Tests multiple HTTP GET requests to external URLs and discards responses.
- B 摘要: Registers a user by encoding password, setting properties, calling a PHPBB forum via HTTP, persisting user, and sending email.
- 静态失败原因: Static methods likely focused on low token similarity (0.12) and structural mismatch, missing the partial functional overlap that BCB recognizes.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider them clones because they share the common code pattern of HTTP connection setup and reading response, which is a significant functional overlap despite differing overall purposes.
- 共享行为: Both open HTTP connections and read response lines via BufferedReader
- 行为差异: Function a is a test with no side effects; function b performs registration with database persistence and email sending
- 修正建议: Incorporate functional context or use fine-grained similarity metrics that capture common code fragments.；Train with multi-level clone labels to handle partial overlap.

### case_id=3041 FP lexical_or_api_overlap

- 方法: `perform` vs `MD5`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Processes an HTTP request to classify a concept by sending XML data to a remote service and parsing the result.
- B 摘要: Computes the MD5 hash of a given string and returns its hexadecimal representation.
- 静态失败原因: Static models like GraphCodeBERT may rely on lexical overlap and structure. Here, despite low token Jaccard, the model might have been misled by common Java constructs such as 'StringBuffer', 'BufferedReader', and 'getBytes', or by the presence of exception handling patterns. The model may have overgeneralized from training data where such API usage patterns were associated with clones.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB annotation guidelines typically consider Type-1 through Type-3 clones but exclude functions that only share common API usage without shared functionality. Since these two methods have completely different purposes and no overlapping logic, BCB would label them as non-clones.
- 共享行为: Both involve byte array manipulation (e.g., getBytes, digest, or reading from stream).
- 行为差异: Code A is a complex web request handler with session management and HTTP communication; Code B is a simple cryptographic hash function.；Code A modifies session attributes and returns an ActionForward; Code B returns a hexadecimal string.；Code A has extensive error handling and conditional logic; Code B has a straightforward computation with exception declaration.
- 修正建议: Improve handling of API-level overlap by incorporating more semantic understanding, e.g., through data flow analysis or program dependency graphs.；Use type-specific heuristics to distinguish web request handlers from utility functions.；Introduce contrastive learning to penalize high overlap in boilerplate code.

### case_id=3042 FP boilerplate_overlap

- 方法: `getPagina` vs `checkForUpgrade`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches the content of a URL as a string, handling exceptions.
- B 摘要: Checks for software upgrades by querying a remote server, parsing the response, updating the UI and database.
- 静态失败原因: Static BERT models often rely on structural and lexical patterns; both functions have a common pattern of opening a URL, reading lines, and concatenating them, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would label as non-clone because the functions have entirely different purposes and logic; the shared URL-reading boilerplate is insufficient to consider them clones.
- 共享行为: Open an HTTP connection and read lines from the response
- 行为差异: A simply returns the entire page content; B parses the response, interacts with UI components, updates database, and handles multiple conditions.；A is a generic URL fetcher; B is a specific upgrade check with complex logic.；A handles exceptions by returning error strings; B throws exceptions and uses conditional logic for UI feedback.
- 修正建议: Incorporate dataflow analysis to distinguish between simple data fetching and complex processing.；Consider the broader context or method names to capture intent.；Use token-level diff or semantic role labeling to detect that the response is used differently.

### case_id=3043 FN benchmark_preference_bias

- 方法: `convert` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.6`
- 推荐路线: `preference_memory_with_manual_audit`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Converts an ACRNEMA stream to DICOM format by parsing, validating, adding UIDs, and writing pixel data with optional inflation.
- B 摘要: Builds a site for editing by applying XSLT transformations to pages, replacing strings, and writing output files.
- 静态失败原因: Static BERT models rely heavily on lexical overlap and syntactic structure; this pair has low token Jaccard (0.09) and distinct domain-specific keywords (DICOM vs XSLT), causing the model to miss the broad functional similarity considered by BCB.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may label them as Type-4 clones because both are file conversion routines that read input, transform, and write output, sharing a high-level functional similarity despite different domains.
- 共享行为: Read from input file and write to output file；Perform validation or transformation before writing；Handle I/O exceptions
- 行为差异: Different data formats: DICOM vs HTML/XML；Different processing: DICOM tag manipulation vs XSLT transformation；Different output writing patterns: binary pixel data vs string concatenation
- 修正建议: Incorporate data flow or program dependency graphs to capture high-level I/O patterns；Use contrastive learning with functional rather than lexical labels；Include domain-agnostic transformation patterns in training

### case_id=3044 FN partial_functionality

- 方法: `doTransfer` vs `populateResources`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Forwards an incoming HTTP request to an external URL, copying request headers and body, and returning the response.
- B 摘要: Loads template resources and images from classpath directories and saves them as persistent objects.
- 静态失败原因: Low token overlap (Jaccard=0.14) and distinct domain-specific keywords led BERT to focus on surface differences, missing the abstract 'data transfer via streams' similarity that BCB annotators may have emphasized.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider them clones because both involve reading from a URL, processing I/O streams, and transferring data to a destination, even though the contexts differ widely. Broad Type-4 similarity could be assigned due to shared I/O patterns.
- 共享行为: Both open a URL connection and read an InputStream.；Both use BufferedReader or similar to read data.；Both handle MalformedURLException and IOException.
- 行为差异: A is an HTTP proxy forwarding request/response; B is a resource initializer.；A uses HttpURLConnection and servlet objects; B uses local classpath resources and custom model classes.；A writes to an OutputStream (response); B writes to Resource/Image objects with save() calls.
- 修正建议: Incorporate dataflow analysis to recognize shared I/O patterns (read-process-write).；Use contrastive learning with BCB's broad annotations to learn functional similarity beyond lexical overlap.；Enhance model with structural information like control flow graphs to capture common exception handling and stream usage.

### case_id=3045 FP lexical_or_api_overlap

- 方法: `get` vs `run`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Sends an HTTP GET request with game-specific headers, reads response lines, decodes non-comment lines into GameRecord objects, and returns an array.
- B 摘要: Loads a tile from a URL or file while avoiding duplicate HTTP requests, reads the entire response into a string, parses it as GeoJSON to build a VectorTile, extracts geometries, and adds them to the data source.
- 静态失败原因: The model may have been misled by the lexical overlap of HTTP reading code (URL, BufferedReader, IOException) and similar structure, ignoring the different domain-specific parsing and broader context.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled non-clone because the methods have different purposes, return types, and data processing; the similarity in HTTP reading is superficial.
- 共享行为: Both open a URL connection and read input using BufferedReader.；Both handle IOException and other exceptions.
- 行为差异: A reads lines and decodes each as a GameRecord, while B concatenates all lines into a JSON string.；B includes duplicate request prevention logic using a synchronized set.；A returns an array of GameRecord objects; B is void and updates a data structure.；A uses game-specific headers; B handles http and file protocols.
- 修正建议: Incorporate control flow and data flow analysis to differentiate processing steps.；Use method signature and return type as features.；Consider domain or purpose via class context or documentation.；Add negative examples with similar I/O but different logic.

### case_id=3046 FN benchmark_preference_bias

- 方法: `File2String` vs `doVersionCheck`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `preference_memory_with_manual_audit`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Reads a file from either a local path or classpath resource and returns its content as a string.
- B 摘要: Fetches a version check URL, parses version and build numbers, and updates the UI if a new version is available.
- 静态失败原因: Static BERT/GraphCodeBERT likely focused on functional semantics and method names, missing the structural I/O pattern overlap. The low token Jaccard (0.2159) and different high-level goals caused the model to classify them as non-clones, while BCB annotation values structural similarity.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may label these as Type-3/Type-4 clones because both functions follow the same high-level algorithmic pattern: open an input stream, read lines with BufferedReader, and process the lines. Despite different purposes, the structural similarity in I/O handling and line-by-line reading is considered a clone in broad BCB annotation.
- 共享行为: Both open an InputStream (FileInputStream or URL.openStream)；Both use BufferedReader to read lines in a loop；Both close the reader after reading
- 行为差异: Function A returns file content as string; Function B updates UI and does not return string.；Function A has fallback to classpath resource; Function B does not.；Function A uses System.exit on errors; Function B shows GUI error messages.；Function B parses specific .version and .build prefixes; Function A simply concatenates all lines.
- 修正建议: Include more examples of structural clones (Type-3/4) in training data；Use dataflow-aware models that capture I/O patterns regardless of surrounding logic；Incorporate method name anonymization to reduce bias from naming

### case_id=3047 FN partial_functionality

- 方法: `getResourceAsStream` vs `encodeFileToFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.65`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Gets a resource via HTTP, caches it locally, and returns a FileInputStream.
- B 摘要: Reads a file, Base64 encodes it, and writes to another file, returning success.
- 静态失败原因: Static BERT relies on lexical and surface-level features, which are very different between the two functions (low Jaccard similarity). It missed the underlying structural I/O pattern due to different API calls and method names.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considers these Type-4 clones due to the shared stream I/O pattern, buffer usage, and exception handling structure, despite different high-level purposes.
- 共享行为: Both open input and output streams；Both copy data in a loop from input to output；Both have try-catch-finally blocks with stream closing；Both use buffered streams
- 行为差异: Function A uses HTTP connections and caching logic；Function B performs Base64 encoding；Function A reads byte-by-byte, Function B uses a buffer；Function A returns an InputStream, Function B returns a boolean
- 修正建议: Use AST-based or dataflow-aware models that capture structural I/O patterns；Train on more diverse I/O clone pairs；Incorporate control-flow and data-dependency features

### case_id=3048 FN benchmark_preference_bias

- 方法: `doTransfer` vs `readGeoParserResult`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.8`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Acts as an HTTP proxy by forwarding request data to a target URL and streaming the response back.
- B 摘要: Parses a record content by sending an XML request to a geo-parsing service and returns extracted place names and gazetteer IDs.
- 静态失败原因: The static model likely relied on lexical overlap (token Jaccard only 0.10) and structural features, which are low due to different APIs and logic, so it predicted non-clone. However, BCB's broad clone definition (including Type-4) may consider them similar, which the model failed to capture due to lack of deep semantic understanding of the overarching network communication pattern.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider both as 'network I/O with data transformation' clones (Type-4), focusing on the high-level similarity of fetching data from a URL and processing it, despite different specific purposes.
- 共享行为: Both open a URL connection to retrieve or send data；Both read from input streams and handle I/O exceptions；Both involve try-catch blocks for network errors
- 行为差异: Function A acts as a full HTTP proxy copying headers and body bidirectionally, while B builds an XML request and parses XML response；A writes directly to the HTTP response, while B returns a collection of tuples；B includes retry logic (up to 3 attempts), while A does not；A uses HttpURLConnection, B uses URL.openStream() and DocumentHelper
- 修正建议: Include more training examples with diverse network I/O patterns to help models recognize high-level functional similarity despite low lexical overlap；Use contrastive learning with augmented pairs that share abstract behavior (e.g., 'fetch and process') but differ in implementation details

### case_id=3049 FN partial_functionality

- 方法: `unJar` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Extracts a specific file from a JAR archive and writes it to a local directory.
- B 摘要: Downloads a resource from a URL with caching, returning a local file input stream.
- 静态失败原因: Low token overlap (0.12) and different API usage (JarFile vs URLConnection) misled the model; it did not detect the shared byte-copying dataflow pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as 'obtain a resource and save to local file' despite different sources, which is a Type-4 partial functionality similarity.
- 共享行为: Both copy bytes from an input stream to a local file；Both create parent directories before writing
- 行为差异: A extracts from a local JAR, B downloads from a remote URL；A does not cache, B implements caching with HTTP conditional requests；A returns a file path, B returns an InputStream；B has complex HTTP and cache logic, A is straightforward
- 修正建议: Train models on dataflow or abstract syntax tree (AST) paths capturing I/O operations；Include more Type-4 clone examples with different APIs but similar data-transfer behavior

### case_id=3050 FP lexical_or_api_overlap

- 方法: `handleHandshake` vs `sendRequestObjectResponse`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Handles Minecraft handshake by validating session via HTTP call to session.minecraft.net.
- B 摘要: Sends an XML request to a configurable server, receives response, saves to file, and returns filename.
- 静态失败原因: Static BERT/GraphCodeBERT may focus on token-level API usage (URL, exception handling) and miss the distinct semantic contexts.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels as non-clone due to completely different functionality despite superficial API overlap.
- 共享行为: Both open HTTP connections using java.net.URL；Both handle exceptions with printStackTrace；Both perform string validation and conditional logic
- 行为差异: A validates a handshake packet username; B sends arbitrary XML requests；A uses hardcoded URL to Minecraft session server; B constructs URL from preferences；A sends login packets; B saves response to file and returns filename；A uses BufferedReader; B uses GZIP compression and OutputStream
- 修正建议: Incorporate semantic role labeling or data flow analysis；Use function-level context like class or package names；Apply domain-specific filtering for common networking patterns

### case_id=3051 FN partial_functionality

- 方法: `runScript` vs `readIntoList`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.65`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a script from a URL and returns its content as a string.
- B 摘要: Reads HTML content from a URL, parses it to extract command names, and populates a map with JMenuItems.
- 静态失败原因: The model focused on the differing API calls and structural complexity of B (e.g., JMenuItem, parsing) and the low lexical overlap, missing the common core of URL reading.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider this a clone because both functions share the high-level task of reading data from a URL and handling network I/O, which is a Type-4 semantic similarity despite different detailed logic.
- 共享行为: Both open a URL and read from an input stream.；Both handle IOExceptions with a try-catch block.
- 行为差异: A reads byte-by-byte and concatenates into a single string; B reads line-by-line and parses HTML tags.；A returns the raw data; B populates a map with UI components and sets action commands.；A returns 'error!' on exception; B prints the stack trace.
- 修正建议: Incorporate abstract syntax tree or control flow analysis to identify common I/O patterns.；Use contrastive learning on pairs that share high-level intent but differ in implementation.；Add metadata about method purpose (e.g., 'reading from URL') during training.

### case_id=3052 FN lexical_or_api_overlap

- 方法: `modifyApplicationMessage` vs `CopyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Modifies a properties file for a given locale by reading, updating or adding a key-value pair, and writing back.
- B 摘要: Copies a file from source to destination using NIO channels.
- 静态失败原因: Static BERT models rely on token and surface-level similarity; the low Jaccard index (0.11) and different API usage (Properties vs FileChannel) caused it to miss the underlying I/O pattern.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may consider both as file I/O operations involving reading and writing, and the broad Type-3/Type-4 criteria might accept this as a partial clone due to the shared pattern of file content transfer.
- 共享行为: Both read from an input file and write to an output file
- 行为差异: Function A handles properties file format, parses lines, and modifies based on message name; function B transfers bytes directly.；Function A has more complex error handling and uses character streams; function B uses NIO channels.；Function A creates output file from English template if missing; function B does not.
- 修正建议: Use data flow or program dependence graphs to capture the read-write pattern；Incorporate structural similarity beyond token overlap；Consider semantic role labeling of I/O operations

### case_id=3053 FP lexical_or_api_overlap

- 方法: `run` vs `getFrameworkFactory`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Downloads a vector tile from a URL, parses it into geometries, and adds it to a data loader.
- B 摘要: Reads a service configuration file to instantiate an OSGi FrameworkFactory.
- 静态失败原因: The model likely overvalued the superficial structural similarity (URL opening, BufferedReader reading) and missed the profound difference in the surrounding logic and domain.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels based on overall semantic functionality; these methods have entirely different purposes despite sharing some I/O patterns.
- 共享行为: Both open a URL and read lines using BufferedReader；Both use try-catch or exception handling
- 行为差异: A downloads and processes geographic tile data; B reads a service configuration to load a class；A is part of a tile rendering pipeline; B is a utility for OSGi initialization；A is void; B returns an object；A uses synchronization; B does not
- 修正建议: Incorporate data flow or control flow features to distinguish I/O utilities from domain-specific processing；Use identifier names or comment embeddings to capture semantic intent

### case_id=3054 FN partial_functionality

- 方法: `getResourceAsStream` vs `copy`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Retrieves a resource by URL, caches it locally, and returns an InputStream to the cached file.
- B 摘要: Copies a source file to a destination file with validation.
- 静态失败原因: Low token overlap (0.169) and different method signatures led the model to perceive them as unrelated, while the underlying byte-copy loop is a shared subtask.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider them clones because both contain a core file copy operation (reading from input and writing to output with a buffer), which is a common reusable pattern, and both are categorized under file I/O operations.
- 共享行为: Both read from an input source and write to an output file using a buffer loop.；Both close streams in finally or catch blocks.
- 行为差异: A includes HTTP connection, caching logic, and conditional cache update; B is a simple file copy with file validation.；A returns an InputStream; B writes directly to a file and returns void.；A uses BufferedInputStream/BufferedOutputStream; B uses a byte array buffer without wrapping.
- 修正建议: Incorporate program slicing or data flow analysis to detect subfunction similarity.；Augment training data with more partial clones where only a subtask overlaps.

### case_id=3055 FN benchmark_preference_bias

- 方法: `execute` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.6`
- 推荐路线: `preference_memory_with_manual_audit`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Executes bytecode injection on class files to add method logging and statistics.
- B 摘要: Retrieves a resource from a URL, caches it locally, and returns an InputStream.
- 静态失败原因: Static BERT models rely on token and structural overlap, which are low (Jaccard=0.13), failing to capture high-level functional similarity that BCB accepts.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider both as 'resource loading and processing' methods, accepting broad Type-4 similarity despite different domains.
- 共享行为: Both read an InputStream from a source (class file or URL) and process its contents.；Both may write data to an OutputStream (class file output or cache file).；Both handle exceptions and close streams in finally blocks.
- 行为差异: A manipulates bytecode using ASM library; B caches remote files with HTTP conditional GET.；A iterates over multiple class files and applies various transformers; B handles caching logic and cache lookup.；A's output is modified bytecode; B's output is a cached file or direct InputStream.
- 修正建议: Incorporate high-level function semantics via code summarization or intent classification.；Align training data with BCB's broad annotation guidelines, possibly using data augmentation with functionally similar but structurally different pairs.

### case_id=3056 FP boilerplate_overlap

- 方法: `createSettingsIfNecessary` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Creates a default settings file if it does not exist, using a template from classpath.
- B 摘要: Handles action events from a settings dialog, saving various preferences like Graphviz path, ImageMagick path, scaling, etc.
- 静态失败原因: The model likely relied on superficial signals like both having try-finally blocks with file I/O (OutputStream, InputStream, FileOutputStream) and the word 'settings'. The token overlap is low but the structural pattern of resource handling may have misled it.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically requires significant functional overlap. Here, one function initializes a settings file from a template, while the other handles a wide range of user preference changes. They share only a vague 'settings' theme, not enough for clone labeling.
- 共享行为: Both involve configuration or preferences management.；Both may perform file I/O (A writes file, B may indirectly save preferences).
- 行为差异: A is a one-time initialization method; B is an interactive event handler.；A has a simple try-finally with a single file copy operation; B has multiple conditional branches for different settings.；A uses a hardcoded source path; B uses user input from UI components.；B triggers UI updates and may ask for restart; A does not involve UI.
- 修正建议: Incorporate more global context or longer-range dependencies to capture overall purpose.；Use data-flow analysis to distinguish between initialization and interactive event handling.；Enhance training with examples that have similar low-level patterns but different high-level intents.

### case_id=3057 FN benchmark_preference_bias

- 方法: `copyOverWarFile` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Copies a WAR file from current directory to apps data directory, then unzips and extracts it.
- B 摘要: Builds HTML pages from XML files using transformations and writes them to an output path.
- 静态失败原因: The static BERT model correctly predicted non-clone due to extremely low lexical overlap (Jaccard 0.0769) and completely different method signatures and logic. The BCB label is likely an annotation error.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have considered them clones due to both methods performing file-based operations involving copying or building, possibly under a broad 'file deployment' category, but this is a stretch.
- 共享行为: Both involve file I/O operations；Both use logging or printing
- 行为差异: Function A is a simple static utility for copying a single file type；Function B is a complex instance method with many parameters for building a website；Function A uses IOUtils.copy, while B uses custom file reading and writing；Function B has extensive error handling and DOM/XML processing
- 修正建议: Re-examine BCB annotation for potential mislabeling；If the label is correct, consider higher-level semantic features capturing deployment tasks

### case_id=3058 FN partial_functionality

- 方法: `getWebPage` vs `login`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Gets the entire content of a web page as a string given a URL.
- B 摘要: Performs HTTP POST login to a web service, returns a session ID.
- 静态失败原因: Static BERT models rely on token-level similarity; low Jaccard (0.12) and different method names/literals discouraged a positive prediction, missing the shared network I/O pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this as clone because both functions perform HTTP network communication, opening a URL and reading response lines, which is a shared higher-level behavior despite different endpoints and output extraction.
- 共享行为: Both use java.net.URL and open a connection；Both read lines via BufferedReader/InputStreamReader；Both handle IOException in a catch block
- 行为差异: getWebPage performs a GET request; login performs a POST with form data；getWebPage concatenates all lines; login reads only first line and extracts session ID；login encodes parameters and sends output via OutputStreamWriter
- 修正建议: Incorporate control and data flow features that capture API usage sequences like URLConnection open, stream read, and close.；Use contrastive learning to improve recognition of partial functional similarity.；Increase training data diversity for Type-4 semantic clones.

### case_id=3059 FN boilerplate_overlap

- 方法: `main` vs `modifyApplicationMessage`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.85`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Test harness that writes bytes 0x00-0xFF to a file and verifies reads using various StraightStreamReader methods.
- B 摘要: Method that modifies or adds a property in a localized properties file by reading, parsing, and writing lines.
- 静态失败原因: The model likely relied on low token overlap and distinct method names/parameters, correctly identifying them as non-clones despite some I/O similarities.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB annotation may have considered the common file I/O boilerplate and loops as sufficient structural similarity for a broad Type-3/Type-4 clone, even though the core logic differs completely.
- 共享行为: Both use File and file I/O streams to read from and write to files.；Both have try-catch blocks for IOException handling.；Both loop over read operations (byte-wise or line-wise).；Both close file streams after use.
- 行为差异: Function A is a unit test for a specific stream reader; Function B is a configuration file updater.；Function A writes raw bytes; Function B writes character data (properties).；Function A checks correctness via assertions; Function B modifies file content based on parameters.；Error handling differs: A prints to System.err, B prints stack trace.
- 修正建议: Use a clone detector that focuses on semantic similarity of core logic rather than surface-level I/O patterns.；Train with explicit negative examples of boilerplate-only similarities.；Incorporate data flow analysis to distinguish between test and application logic.

### case_id=3060 FP boilerplate_overlap

- 方法: `run` vs `sendRequestObjectResponse`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Loads a map tile from a URL (file or HTTP), parses GeoJSON into vector geometries, and adds them to a data loader.
- B 摘要: Sends an HTTP POST request with XML data to a servlet, receives the response, saves it to a file, and displays the file in a browser.
- 静态失败原因: Static BERT models may rely on token-level similarities such as common API calls (URL, InputStream, BufferedReader) and structural patterns (try-catch blocks, URL creation) which are present in both. However, they lack understanding of the high-level intent and the different data flows (A reads and processes, B sends then receives). The lexical overlap is low (Jaccard 0.10177), but the model might have been fooled by the presence of similar boilerplate code for I/O.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled this as non-clone because the two methods serve entirely different purposes: one is a tile loading routine for map rendering, the other is a generic servlet communication method for a library system. Despite shared URL/IO patterns, their core functionality and output differ significantly.
- 共享行为: Both involve creating a URL and opening an input stream to read data from the URL.
- 行为差异: A reads data from a URL and processes it into vector tiles; B sends data to a URL and reads the response.；A returns void; B returns a filename string.；A uses synchronization for request tracking; B does not.；A supports both file and HTTP protocols; B only HTTP.
- 修正建议: Introduce control-flow or data-flow features that distinguish reading vs. writing to URL.；Use graph-based representations that capture the direction of data movement.；Train on more diverse non-clone pairs that share I/O patterns but differ in purpose.

### case_id=3061 FP other

- 方法: `copy` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Copies a file using FileChannel transfer.
- B 摘要: Handles action events for setting various application preferences, including file selections.
- 静态失败原因: Despite low token Jaccard similarity (0.037), the model may have been misled by the presence of 'File' operations in both functions, or due to a biased training set that overemphasizes file-related operations. Alternatively, the prediction might be an outlier caused by model limitations.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB typically labels non-clones when functions have entirely different functionalities, even if they share some common API usage. Here, there is no functional overlap.
- 共享行为: None
- 行为差异: Different purposes: file copy vs. UI event handling.；Different inputs/outputs: file streams vs. action events and UI components.；Different control flow: simple sequential vs. complex conditional branching.；Different side effects: file copying vs. updating application state and UI.
- 修正建议: Improve model to better recognize functional differences, not just token overlap.；Use more robust semantic representations like code structure or data flow.；Adjust prediction threshold to reduce false positives for such dissimilar functions.

### case_id=3062 FN partial_functionality

- 方法: `addIDs` vs `loadMFileViaWeb`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads and parses metabolite data from a web service to populate a peak list row with molecular weight and chemical IDs.
- B 摘要: Downloads a MATLAB-like function file from a web source, parses it into a UserFunction object, and returns it.
- 静态失败原因: Low lexical overlap (Jaccard 0.12) and distinct domain-specific vocabulary; static BERT models rely on local token similarity and miss the abstract structural pattern of web loading. The long code in A with many unique identifiers distracts from the shared API-level behavior.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as 'web data loading and parsing' tasks, sharing a common pattern of URL connection, buffered reading, and parsing, thus classifying them as broad Type-3/Type-4 clones despite different domains and specific outputs.
- 共享行为: Both perform HTTP requests to download data from URLs；Both read the response line by line using BufferedReader；Both parse the downloaded content to extract structured information
- 行为差异: Function A extracts specific metabolite identifiers and updates a row data structure; Function B concatenates all lines and parses the entire content as a function definition；Function A returns an integer score; Function B returns a UserFunction object；Function A contains multiple condition checks for different identifier types; Function B has no such conditional parsing
- 修正建议: Incorporate program flow or dataflow analysis to capture high-level API usage patterns；Use contrastive learning with pairs that share abstract behavior but differ in tokens；Enhance model with longer-range semantic representations or graph-based code embeddings

### case_id=3063 FN benchmark_preference_bias

- 方法: `main` vs `getFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `1.0`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Tests StraightStreamReader by writing bytes to a file and reading them back in multiple ways
- B 摘要: Downloads a WSDL file from a URL, modifies the endpoint in the XML, and saves it to a temporary location
- 静态失败原因: Static model likely correctly identified non-clone due to low lexical overlap and different semantics; BCB label may be erroneous
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have incorrectly labeled as clone due to broad file I/O theme, but under typical BCB guidelines they are not semantically similar
- 共享行为: Both involve file I/O operations
- 行为差异: Purpose: test vs. download/modify；Different classes and methods used；Different control flow and error handling；No overlap in core logic
- 修正建议: Review BCB annotation for this pair；Ensure that only functions with similar functionality are labeled as clones

### case_id=3064 FP lexical_or_api_overlap

- 方法: `main` vs `copyFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Complex main method that parses a Prolog file, generates adapter classes, and writes output to a jar.
- B 摘要: Simple utility function that copies the contents of one file to another using FileChannel.
- 静态失败原因: Static BERT models likely over-relied on common tokens like 'File', 'IOException', 'catch', and ignored the vast structural and semantic differences.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would not label these as clones because they perform completely different tasks; only superficial API overlap exists.
- 共享行为: Both handle files and IOException；Both use exception printing (printStackTrace)；Both involve File objects
- 行为差异: A is an entire program entry point with multiple complex steps; B is a one-purpose helper；A generates Java classes and serialized data; B only copies bytes；A has conditional logic and command-line parsing; B has none
- 修正建议: Incorporate data-flow or control-flow graph features to capture program semantics；Use contrastive learning to distinguish boilerplate from core logic；Augment training data with pairs that share common APIs but differ in purpose

### case_id=3065 FN benchmark_preference_bias

- 方法: `getResourceAsStream` vs `convert`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Fetches a remote resource via URL, caches it locally, and returns an InputStream.
- B 摘要: Reads a medical image file, processes it for DICOM conversion, and writes a new file.
- 静态失败原因: The token Jaccard similarity is very low (0.13), and the syntactic structures differ significantly. GraphCodeBERT relies on local token patterns and graph structures, which may not capture the abstract I/O pattern shared across domains.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider them clones due to the shared high-level pattern of reading and writing data streams, but the domain-specific logic is entirely different, making this a weak alignment.
- 共享行为: Both read from an input stream and write to an output stream；Both use buffered streams for I/O；Both handle exceptions with try-catch-finally blocks
- 行为差异: Domain: resource caching vs medical image format conversion；Function A involves URL fetching and caching logic; Function B involves DICOM parsing and metadata manipulation；Function A returns an InputStream; Function B has void return type
- 修正建议: Incorporate data flow analysis to capture input-output transformations；Train on cross-domain clone pairs with high-level functional similarity；Use contrastive learning to better generalize abstract patterns

### case_id=3066 FN partial_functionality

- 方法: `main` vs `internalCopy`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a URL, opens a ZipInputStream, and extracts all entries to files.
- B 摘要: Copies a source file to a destination file with a condition to skip 'Thums.db'.
- 静态失败原因: Low token Jaccard (0.27) and significant API-level differences (ZipInputStream vs BufferedInputStream, URL vs File) caused the model to miss the underlying data-flow similarity of reading and writing bytes in a loop.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels as clones any pair that performs an I/O copy loop with buffer, ignoring differences in source/destination types and additional logic, considering them Type-3/4 clones due to similar structural pattern.
- 共享行为: Both use a loop to read bytes from an input stream and write to an output stream using a buffer.
- 行为差异: A handles URL download and zip extraction; B is a plain file copy.；A writes to multiple files per zip entries; B writes to a single file.；A uses ZipInputStream and FileOutputStream; B uses BufferedInputStream and BufferedOutputStream.；Method names and contexts differ (main vs private helper).
- 修正建议: Use data-flow-aware models that abstract I/O operations.；Include program dependence graphs to capture core loop semantics.；Augment training with more diverse buffer copy patterns.

### case_id=3067 FP lexical_or_api_overlap

- 方法: `fetchUrl` vs `downloadModel`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches URL content as a string, returning empty string on failure.
- B 摘要: Downloads an RDF model from a URL, throwing RuntimeException on failure.
- 静态失败原因: Static BERT may have overemphasized overlapping API tokens (URL, openStream, catch, IOException) and missed semantic differences in return type and data processing, leading to a false positive clone classification.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels non-clone because the functions serve fundamentally different purposes (text retrieval vs RDF model download) despite sharing URL opening patterns, and BCB typically requires functional similarity beyond just input/output structure.
- 共享行为: Both open a URL connection and read from an input stream；Both catch MalformedURLException and IOException
- 行为差异: Return type differs: String vs Model；Processing differs: plain text concatenation vs RDF model parsing；Error handling differs: silent empty return vs logging and throwing RuntimeException
- 修正建议: Include type signatures and return type analysis；Incorporate data flow to distinguish string building from model parsing；Consider error handling patterns (silent vs throwing) as differentiating features

### case_id=3068 FP lexical_or_api_overlap

- 方法: `run` vs `loadURL`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Makes an HTTP GET with basic auth, reads response line by line into a StringBuffer, stores result and timestamp.
- B 摘要: Makes an HTTP GET with basic auth, reads response line by line, writes to a temp file, updates a progress label and prints.
- 静态失败原因: The model heavily relied on lexical overlap (BASE64Encoder, URLConnection, BufferedReader, line-by-line reading loop) and ignored data flow and side effects, causing a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB usually labels as non-clone when the overall goal differs despite similar API usage; here one stores data in memory, the other writes to file with progress feedback.
- 共享行为: Creates HTTP connection with basic authentication via Authorization header；Reads response line by line using BufferedReader
- 行为差异: A stores response in a StringBuffer and sets a finish flag; B writes to a temporary file and updates a UI label；A updates lastIteraction timestamp; B prints file size and writes to console；A catches all Throwables; B throws IOException
- 修正建议: Add data-flow analysis to track how the HTTP response is consumed (stored vs. written to file)；Include side-effect detection (file I/O, UI updates) to differentiate behaviors

### case_id=3069 FN benchmark_preference_bias

- 方法: `doGet` vs `decodeFileToFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Handles HTTP GET requests to render a portal page, including authentication, caching, and logging.
- B 摘要: Decodes a Base64-encoded input file and writes the decoded content to an output file.
- 静态失败原因: Static BERT model correctly identified that these functions have different purposes and low token overlap, predicting non-clone. The BCB label is questionable, making this a likely benchmark annotation error.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled it as clone due to both methods performing file I/O operations (reading and writing), despite the different context. However, this is unlikely given the large functional difference; possibly a misannotation.
- 共享行为: Both involve reading data from an input source and writing to an output destination；Both use try-catch-finally blocks for resource management
- 行为差异: Code A handles HTTP request/response and multiple business logic paths；Code B is a simple file conversion with no user interaction；Code A includes authentication, logging, and caching; Code B has none；Code A writes HTML to response; Code B writes binary data to file
- 修正建议: Review BCB annotation for consistency；If annotation is correct, consider expanding clone definition to include very high-level functional overlap

### case_id=3070 FN partial_functionality

- 方法: `testNetworkHTTP` vs `postData`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Test method that makes multiple HTTP GET requests to various URLs and reads responses until end.
- B 摘要: Utility method that sends an HTTP POST request with form data and reads the response.
- 静态失败原因: Static BERT models rely on token overlap and code structure; low Jaccard similarity (0.15) and different control flow (e.g., multiple loops vs single, parameters vs none) likely caused low similarity. The model failed to capture the common high-level pattern of HTTP request/response due to different API usage (HttpURLConnection vs URLConnection with setDoOutput) and missing dataflow context.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely labeled this as a clone because both methods perform HTTP communication, involving opening a connection, reading response data, and are part of the same domain (network operations). They consider the broad functionality of 'making an HTTP request and reading the response' as similar enough for a Type-4 (semantic) clone.
- 共享行为: Both use URL and URLConnection to establish HTTP connections；Both use BufferedReader to read InputStream from the connection；Both read lines until null (end of stream)
- 行为差异: Method A uses GET requests (no data sent); method B uses POST and sends data；Method A performs multiple sequential requests; method B performs a single request；Method A has no parameters and fixed URLs; method B takes parameters for protocol, host, form, data；Method A catches IOException and disconnects; method B throws Exception and does not explicitly disconnect
- 修正建议: Incorporate semantic features like API call patterns and dataflow；Use models that capture intent from method names or comments；Add more training examples of Type-4 clones with low token overlap；Consider structural similarity of HTTP request handling logic

### case_id=3071 FP boilerplate_overlap

- 方法: `doGet` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Handles HTTP GET requests by forwarding them to a Fedora repository and copying the response.
- B 摘要: Handles action events in a GUI to configure settings like graphviz path, image scaling, and look-and-feel.
- 静态失败原因: The static model likely overfitted to common structural patterns like try-catch blocks, loops, and conditional statements, ignoring the domain-specific semantics. It may have been misled by the presence of method calls like logger.debug and similar control flow, but the actual functionality is entirely different.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would not consider these as clones because they perform completely different tasks in different domains (web vs GUI) with no functional overlap.
- 行为差异: Function A is a servlet request handler; Function B is a GUI event handler.；A deals with HTTP and URL connections; B deals with file choosers and UI updates.；A copies streams and headers; B updates preferences and UI components.
- 修正建议: Improve model's ability to capture domain-specific semantics beyond syntactic patterns.；Use contrastive learning to enforce separation of unrelated functions.；Incorporate awareness of method name and class context to distinguish web vs GUI.

### case_id=3072 FN benchmark_preference_bias

- 方法: `doGet` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Handles HTTP GET requests to retrieve and display a portal page, with caching and logging.
- B 摘要: Copies a file from source to destination using NIO FileChannel, ensuring directories exist.
- 静态失败原因: The model correctly predicted non-clone based on low token overlap and different semantics, but BCB's annotation is likely based on broad structural patterns that static BERT models do not capture, leading to a false negative according to BCB.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled it a clone due to superficial structural similarities such as multiple try-catch-finally blocks and usage of File-related I/O operations, even though the overall functionality is entirely different.
- 共享行为: Both involve file I/O operations (writing to a file in doGet, copying in copyFile)；Both use multiple nested try-finally blocks for resource management
- 行为差异: doGet is a servlet method handling web requests with parameter parsing, page retrieval, user permissions, and HTML output; copyFile is a utility for file copying without web context；doGet has complex logic for page loading, caching, and logging; copyFile is straightforward file copy
- 修正建议: Incorporate functional semantics beyond token overlap, e.g., using control flow graphs or data flow；Train on BCB's annotation criteria to recognize partial functionality similarity

### case_id=3073 FN partial_functionality

- 方法: `httpRequestByPOST` vs `getXML`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends an HTTP POST request with form parameters using Apache HttpClient, reads the response line by line, and returns the response body string, handling HTTP errors and IOExceptions by setting error fields and returning null.
- B 摘要: Sends an HTTP GET request to a URL with an encoded query string using java.net.URL, reads the response line by line, and returns the response body string, returning null on various exceptions.
- 静态失败原因: The token Jaccard similarity is low (0.27) due to different library names, API calls, and parameter handling. Static BERT-based models rely heavily on lexical overlap and may not capture the semantic intent shared by both functions, especially when libraries and error handling diverge.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB tends to label as Type-3/Type-4 clones if the core functionality (fetching an HTTP resource and returning its content as a string) is the same, even if the underlying libraries, method signatures, or parameter handling differ.
- 共享行为: Both perform an HTTP request to a given URL and return the response body as a string.；Both read the response line by line using a BufferedReader.；Both return null on failure (exceptions or non-success status).；Both use UTF-8 encoding.
- 行为差异: A uses HTTP POST with form parameters; B uses HTTP GET with a query string.；A uses Apache HttpClient; B uses java.net.URL.；A sets class-level error fields (lastErrorCode, lastErrorMessage) on failure; B does not.；A checks HTTP status code (<400); B only catches exceptions, no explicit status check.
- 修正建议: Incorporate semantic similarity over program dependence graphs or AST paths.；Use models trained on function-level semantics rather than token overlap.；Consider abstracting library-specific calls to their generic purpose (e.g., HTTP GET/POST to 'performRequest').

### case_id=3074 FP lexical_or_api_overlap

- 方法: `main` vs `copyDeleting`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Parses a Prolog file and generates adapter code and resources.
- B 摘要: Copies a file from source to destination using a buffer.
- 静态失败原因: The model likely overemphasized shared tokens like 'File', 'IOException', 'try', 'finally', and common IO operations, ignoring the vast difference in overall structure and purpose.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB requires significant functional similarity; these functions have completely different purposes and logic, so they are not clones.
- 共享行为: Both perform file I/O operations.
- 行为差异: A is a complex multi-step generation process; B is a simple file copy.；A uses many external libraries and classes; B uses only basic Java IO.
- 修正建议: Train with more contrastive examples of simple IO vs complex workflows.；Incorporate structural similarity metrics.；Use code graph representations that capture control flow complexity.

### case_id=3075 FN partial_functionality

- 方法: `doGet` vs `encodeFileToFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Handles HTTP GET request to display a page, with caching to a file.
- B 摘要: Encodes a file to another file using Base64 encoding.
- 静态失败原因: The model likely focused on the overall method signature and high-level semantics (HTTP vs file encoding), missing the partial file I/O similarity that BCB considers. The low token Jaccard (0.083) led the model to confidently reject the pair, but it failed to detect the underlying shared file-writing behavior.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider them clones due to partial functionality similarity: both functions have a file writing component (Function A writes a cache file, Function B writes an encoded file). Additionally, both transform data from one form to another (HTTP response to cached file, raw file to encoded file). This aligns with BCB's broad Type-4 semantic clone category.
- 共享行为: Both involve file I/O operations (reading/writing files).；Both handle exceptions with try-catch blocks.
- 行为差异: Function A is a servlet handler with complex logic for page retrieval, user permissions, and caching.；Function B is a simple file encoding utility with a straightforward read-write loop.；Function A uses HTTP request/response context; Function B operates on file paths.；Function A includes logging, statistics, and permission checks; Function B does not.
- 修正建议: Incorporate more fine-grained analysis of code regions to detect partial functionality overlaps.；Use dataflow analysis to identify common I/O patterns even if the rest of the code differs.；Train on examples where functions share only a small portion of behavior.

### case_id=3076 FN benchmark_preference_bias

- 方法: `serialize` vs `getFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Serializes a parsed content package to an output stream using a temporary file.
- B 摘要: Downloads a WSDL file from a URL, optionally modifies its endpoint, and returns the local file path.
- 静态失败原因: Low token Jaccard similarity (0.083) and minimal syntactic overlap make it unlikely for a static model to recognize any clone relationship, especially if the model relies on surface-level features.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider them clones under a broad Type-4 view because both perform file I/O operations with error handling and temporary files, but this interpretation seems too loose and not typical of BCB annotations.
- 共享行为: Both involve reading from an input (file or network) and writing to an output (file or stream)；Both use exception handling and temporary file creation
- 行为差异: Input sources differ: serialized package (A) vs. remote WSDL (B)；Output destinations differ: output stream (A) vs. local file (B)；Function A does not modify content, unlike B which modifies endpoint attribute；Return types differ: void (A) vs. String (B)
- 修正建议: Use semantic embeddings that capture functional similarity beyond lexical overlap；Incorporate data flow analysis to understand input/output transformations

### case_id=3077 FP boilerplate_overlap

- 方法: `readData` vs `copyFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Parses string constants and a file to populate various sets and maps for Tibetan character processing.
- B 摘要: Copies a file from source to destination using FileChannel transferTo.
- 静态失败原因: The static BERT model may have been misled by overlapping boilerplate elements like IOException, try-catch blocks, and file-related variable names, causing it to overlook the fundamental difference in functionality.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB annotators would likely label these as non-clones because they perform completely different tasks (data parsing vs. file copying) with very low token overlap and no functional similarity.
- 共享行为: Both perform file I/O operations.
- 行为差异: Function A reads and parses data into multiple data structures; Function B copies file content.；Function A involves complex string tokenization and dictionary building; Function B is a straightforward file copy.；Function A has extensive nested conditionals and loops; Function B has simple sequential code with exception handling.
- 修正建议: Enhance training data to include more diverse file I/O tasks and reduce weight on common exception handling patterns.；Incorporate data flow or structural analysis to distinguish between reading/parsing and writing/copying operations.

### case_id=3078 FP lexical_or_api_overlap

- 方法: `getUser` vs `checkForUpgrade`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Retrieves a user by login from a database, falling back to parsing a configuration file if not found.
- B 摘要: Checks for available software upgrades by querying a remote server and updating the database/UI accordingly.
- 静态失败原因: Static models like BERT may rely on surface-level token overlap (URL, BufferedReader, while loops, try-catch) and similar code structure, missing the semantic divergence.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely considered the overall distinct purposes (user authentication vs upgrade checking) as non-clone, despite some API-level similarities.
- 共享行为: Both open a URL and read from it using BufferedReader.；Both parse input lines (using StringTokenizer or split) in a loop.
- 行为差异: Function A loads user data for authentication; Function B checks for upgrades.；Function A interacts with DAO and local file; Function B interacts with remote server and database.；Function A has no UI involvement; Function B manipulates UI components.；Function A returns a User object; Function B is void and may show messages.
- 修正建议: Use data-flow or control-flow analysis to capture the high-level intent.；Incorporate domain knowledge (e.g., library calls like UserDAO vs UiUtil) to distinguish applications.

### case_id=3079 FN benchmark_preference_bias

- 方法: `sendRequestObjectResponse` vs `seeURLConnection`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.8`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Sends an XML request to a server via HTTP, compresses it, saves the response to a file, and opens it in a browser.
- B 摘要: Retrieves content from a hardcoded URL and logs the response.
- 静态失败原因: Static BERT likely learned to require high structural/API similarity; low token Jaccard and different control flow caused it to miss the functional similarity BCB accepted.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider both as 'HTTP client reading response' and overlook peripheral details, labeling them as Type-4 clones despite low syntactic overlap.
- 共享行为: Both open an HTTP URL connection；Both read from the connection's input stream
- 行为差异: Function A sends data (request) and compresses it, while B only reads；Function A saves the response to a file and opens it, B just logs；Function A handles configuration via preferences and error dialogs, B does not；Function A has parameters, B uses a hardcoded URL
- 修正建议: Incorporate functional role classification (e.g., 'HTTP client')；Use data flow analysis to identify common I/O patterns；Balance strict semantic equivalence with BCB's broader clone definition

### case_id=3080 FP boilerplate_overlap

- 方法: `readData` vs `copyFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Parses multiple comma-separated string fields into sets and maps for storing configuration data.
- B 摘要: Copies the contents of a source file to a destination file using byte streams.
- 静态失败原因: The static model likely over-relied on superficial structural elements like while loops, try-catch blocks, and variable initializations, overlooking the critical difference in the types of operations (string parsing vs. file I/O). The low token Jaccard should have indicated low similarity, but the model may have been misled by common Java idioms.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would label this as non-clone because the two functions have entirely different purposes: one loads configuration data from string arrays, the other copies files. Even under broad Type-4 similarity, they are not functionally similar.
- 共享行为: Both are static Java methods.；Both may handle exceptions.
- 行为差异: A manipulates string tokens and populates data structures; B copies raw bytes.；A does not perform any file I/O; B exclusively deals with file streams.；A has complex nested logic with many sets and maps; B is a simple copy loop.；A modifies class-level variables; B only uses local variables.
- 修正建议: Improve the model's ability to distinguish between different domains of operations (string processing vs. I/O).；Incorporate dataflow analysis to differentiate between manipulation of in-memory strings and file streams.；Increase weight on token-level dissimilarity and reduce influence of common structural patterns.

### case_id=3081 FN partial_functionality

- 方法: `getResourceAsStream` vs `testReadHelloWorldTxt`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Custom resource caching method that fetches a resource via URL, caches it to disk, and returns an InputStream, with HTTP conditional GET and directory-based caching.
- B 摘要: Test method that reads a resource from the classpath, writes it to a temporary file, then uses a FSContentResolver to read and assert the file content multiple times with various paths.
- 静态失败原因: Static BERT/GraphCodeBERT models rely heavily on token overlap and structural similarity, which is low (Jaccard 0.0625). The shared semantic behavior of resource retrieval is not captured by static features, and the model likely focused on the different method names, control flow, and library calls, missing the abstract commonality.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled this as a clone because both functions retrieve a resource from some source (URL or classpath) and read it as a stream, broadly matching Type-4 semantic clone criteria where the high-level goal of reading a resource is similar, despite different implementations.
- 共享行为: Both involve reading data from a resource (URL or classpath) and obtaining an InputStream.
- 行为差异: Function A implements a generic caching mechanism for any URL, while B is a specific test for a content resolver.；Function A returns an InputStream; B asserts the content equals 'Hello World' and does not return anything.；Function A uses HTTP conditional GET and file caching; B uses ClassLoader.getResourceAsStream and IOUtils.copy.；Function A has complex error handling and cleanup; B has no error handling (throws Exception).
- 修正建议: Incorporate data flow and resource access patterns into the model.；Use method-level semantics like API call sequences (e.g., getResourceAsStream, FileOutputStream) to capture high-level intent.；Augment training with more diverse Type-4 clone examples that share only abstract behavior.

### case_id=3082 FN partial_functionality

- 方法: `convert` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Converts a medical image file to DICOM format by parsing and writing pixel data with headers.
- B 摘要: Retrieves a resource from a URL, caches it to a local file, and returns an InputStream.
- 静态失败原因: Static models like GraphCodeBERT focus on token-level and syntactic similarities, which are low here; they miss the high-level semantic pattern of stream copying due to different API calls and context.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as stream copy functions that read from a source and write to a destination with error handling, fitting Type-4 semantic similarity.
- 共享行为: Both read from an input stream and write to an output stream using buffered I/O.；Both handle exceptions and close streams in finally blocks.；Both use conditional checks to decide whether to write data.
- 行为差异: A manipulates DICOM metadata and pixel data; B handles HTTP caching and URL connections.；A writes specific DICOM tags; B checks cache freshness and creates directories.；A includes a complex inflation loop; B uses a simple byte copy loop.
- 修正建议: Improve model's ability to recognize abstract I/O patterns.；Add data augmentation with semantically similar but syntactically different stream-copy functions.

### case_id=3083 FN benchmark_preference_bias

- 方法: `trainClassifier` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Trains a classifier by executing an external command with training data and model file paths.
- B 摘要: Builds a website for editing by processing XML, applying XSLT transformations, and writing output files.
- 静态失败原因: The static BERT model correctly predicted non-clone; the error is a false negative because the BCB label (1) is likely erroneous. The model recognized the lack of semantic and lexical similarity, which disagrees with the benchmark.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have incorrectly labeled this pair as a clone due to broad categorization of both as 'processing' methods that perform file I/O and manipulate data, but the functional overlap is minimal.
- 共享行为: Both methods involve file I/O operations and command-line argument handling.
- 行为差异: Purpose: trainClassifier (machine learning) vs buildSiteForEdit (web page generation)；Inputs: trainClassifier takes a directory and arguments; buildSiteForEdit takes multiple path strings and properties；Process: trainClassifier runs an external process; buildSiteForEdit performs in-memory XML and string transformations；Output: trainClassifier outputs to stdout/stderr; buildSiteForEdit writes to files
- 修正建议: Review and correct the BCB label for this pair to reflect true non-clone status.；Improve benchmark annotation guidelines to avoid such misclassifications.

### case_id=3084 FN partial_functionality

- 方法: `callService` vs `readData`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Makes an HTTP request to a URL and reads the response line by line into a string buffer, storing the result in an answer field, with exception handling for malformed URL and I/O errors.
- B 摘要: Reads configuration data from comma-separated strings and a file, parsing tokens into multiple sets and arrays via StringTokenizer and BufferedReader, with error handling for I/O and data format issues.
- 静态失败原因: Static BERT/GraphCodeBERT models rely on token overlap and surface patterns; the Jaccard similarity is very low (0.078), and the API calls (URL vs. StringTokenizer) and variable names are completely different, making it hard to capture the abstract commonality. The model failed to recognize the shared 'read-and-process' pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: None
- 共享行为: Both read text input line by line using BufferedReader.；Both use while loops to process each line.；Both catch IOException and handle it gracefully.；Both involve string manipulation and storing results in data structures.
- 行为差异: Source of input: URL (A) vs. file and in-memory strings (B).；Destination: single string (A) vs. multiple HashSets and arrays (B).；Error handling: MalformedURLException and IOException (A) vs. IOException and custom errors (B).；Complexity: A is simple, B is highly complex with many loops and conditionals.
- 修正建议: Use dataflow and control flow features to abstract away concrete API calls.；Train on a broader set of clone examples with diverse lexical choices but similar semantics.；Incorporate contrastive learning objectives that align functions with similar high-level behavior.；Consider hierarchical representations that capture input-output patterns.

### case_id=3085 FN benchmark_preference_bias

- 方法: `getResourceAsStream` vs `parseContent`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.4`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Retrieves a local or remote resource as an InputStream, with caching and HTTP conditional GET.
- B 摘要: Parses HTML content from an InputStream, extracts charset, provider, links, body text, and language.
- 静态失败原因: Static models may overgeneralize based on shared structural patterns (e.g., method length, stream handling, try-catch blocks) and fail to capture the distinct semantics. Low Jaccard suggests limited lexical overlap, but the models might still be confused by the common use of InputStream/File I/O.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as clone due to both being part of a broader web crawling pipeline (both handle HTTP streams and file I/O), but the actual functionality is entirely different. The annotation may be an error or reflect very high-level Type-4 similarity.
- 共享行为: Both involve reading from an input stream；Both use try-catch for exception handling
- 行为差异: Function A downloads and caches files; Function B parses HTML and extracts metadata；Function A returns an InputStream; Function B adds parsed fields to a document；Function A uses HTTP URL connections; Function B uses HTML parsing libraries；Function A has caching logic; Function B has charset detection and provider selection
- 修正建议: Improve model understanding of overall program purpose beyond local patterns；Incorporate higher-level semantic features like method name and context；Use a more holistic representation capturing I/O direction and data transformation

### case_id=3086 FN partial_functionality

- 方法: `run` vs `readData`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Reads a resource file from classpath and sets its text into a JTextArea.
- B 摘要: Initializes various sets and maps from string fields and parses a file to build Tibetan character mappings.
- 静态失败原因: Static BERT models rely on lexical and structural similarity, which is very low here (token Jaccard=0.075). The models lack understanding of high-level functionality and data flow, missing the shared I/O pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider these Type-4 clones because both are data reading and processing routines with similar I/O patterns, even though the specifics differ.
- 共享行为: Both methods read input data and iterate over lines/tokens.；Both handle exceptions with try-catch.
- 行为差异: Different input sources: URL resource vs string fields/file.；Different outputs: setting UI text vs populating data structures.；Different error handling: silent catch vs printing to stdout.；Different control flow complexity: simple loop vs complex switching.
- 修正建议: Incorporate data flow analysis to detect I/O and processing patterns.；Use code summarization to capture high-level purpose.；Consider multi-modal embeddings that combine structural and semantic information.

### case_id=3087 FN boilerplate_overlap

- 方法: `testNetworkHTTP` vs `doVersionCheck`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.85`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: A test method that makes multiple HTTP GET requests to various URLs with device data as parameters, discarding all responses.
- B 摘要: A method that fetches a version check file from a URL, parses version and build numbers, and displays an update message if newer version is available.
- 静态失败原因: Static BERT models rely heavily on token similarity; here the token overlap is low (Jaccard 0.195) due to different method names, variable names, constants, and UI code. The model likely focused on lexical differences and missed the shared high-level structural pattern of HTTP I/O. The embedding may not capture the common boilerplate due to differing context.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may label as clone because both functions share the core pattern of establishing an HTTP connection, reading a stream with BufferedReader, and iterating over lines, which constitutes a common functional subtask of 'reading from a URL', even if the specific processing differs. BCB's Type-4 annotation accepts such partial functional similarity.
- 共享行为: Both execute HTTP GET requests；Both read response streams line-by-line using BufferedReader；Both handle IOException with error handling
- 行为差异: code_a makes six requests sending sensitive device data; code_b makes one request for version info；code_a discards all response data; code_b parses lines for version and build strings；code_a has no UI; code_b shows wait cursor and user messages；code_a uses Log.v; code_b uses GUIUtilities for user interaction
- 修正建议: Use program dependency graphs or dataflow analysis to capture structural I/O patterns；Train with contrastive objectives that emphasize functional similarity over lexical similarity；Augment training data with more diverse Type-3/4 clones that share network I/O patterns but differ in logic

### case_id=3088 FN benchmark_preference_bias

- 方法: `handler` vs `invoke`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Reads a URL, extracts a substring between markers from lines containing a specific include string, and sets that substring as the value for every entry in a map.
- B 摘要: Sends an HTTP POST request with JSON body to a service endpoint, reads and deserializes the response, with retry logic on connection timeout.
- 静态失败原因: From BCB perspective, the static model failed to recognize broad similarity in network I/O pattern and exception handling, but correctly identified semantic difference in data extraction vs. RPC logic.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB likely labeled these as clones due to both being network-handler methods with similar boilerplate (BufferedReader, streams, exception handling), focusing on broad 'network I/O' category rather than specific functionality.
- 共享行为: Both perform network I/O using URL connections.；Both read response line-by-line with BufferedReader.；Both handle IOException.
- 行为差异: A uses GET request; B uses POST request.；A extracts a substring from a specific range; B parses JSON response.；A writes to a map; B returns a deserialized object.；B includes retry logic; A does not.
- 修正建议: Treat BCB labels with caution when token similarity is low.；Incorporate task-specific context (e.g., method name semantics) to differentiate.；Use fine-grained functional classification to avoid over-generalizing network I/O patterns.

### case_id=3089 FN boilerplate_overlap

- 方法: `doVersionCheck` vs `testNetworkHTTP`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Checks for software version updates by reading a remote version file.
- B 摘要: Performs multiple HTTP requests to exfiltrate device information to remote servers.
- 静态失败原因: Static BERT/GraphCodeBERT models rely on token-level patterns and code structure. The low token Jaccard (0.207) and differing method names and URL strings likely led to a non-clone prediction. The model may not recognize the common boilerplate pattern as sufficiently similar due to different variable names, multiple URLs in B, and absence of UI elements.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely considers this clone due to structural similarity: both functions follow the same pattern of URL connection, buffered reading, and error handling, despite different purposes. BCB's annotation guidelines allow broad Type-3/Type-4 clones that share significant control flow and I/O boilerplate.
- 共享行为: Opens a URL connection；Reads lines from an input stream using BufferedReader；Uses while loop to read lines；Handles IOException with catch block
- 行为差异: Function A reads a single URL and processes two specific fields; Function B reads multiple URLs and discards all lines.；Function A checks for version strings; Function B sends sensitive data (IMEI, phone, installed apps).；Function A uses view wait cursor; Function B has no UI interaction.；Function A has additional logic to call another method based on parsed values; Function B is a standalone test.
- 修正建议: Improve model's ability to recognize I/O boilerplate patterns even with different token distributions.；Incorporate more structural AST similarity features that capture common control flow like try-catch with URL read loops.；Use data augmentation to emphasize common boilerplate patterns across different tasks.

### case_id=3090 FP lexical_or_api_overlap

- 方法: `getRequestContent` vs `run`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.85`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Opens HTTP connection to a URL, reads first line, returns it.
- B 摘要: Sends HTTP GET request with Basic Authentication, reads all lines from response, stores full result in an instance variable.
- 静态失败原因: Static BERT models may rely too heavily on token overlap from common HTTP-related classes and methods, overlooking the differences in logic flow and returned data.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB tends to require functional similarity beyond shared API usage; here the functions differ in return value semantics and overall purpose.
- 共享行为: Both open an HTTP connection using HttpURLConnection；Both read the response using BufferedReader and InputStreamReader
- 行为差异: Function A returns only the first line; Function B reads and accumulates all lines；Function B performs Basic Authentication while A does not；Function B is a runnable, setting completion flags; A is a synchronous method；Function B handles errors with a stack trace; A throws exception
- 修正建议: Train with more diverse negative examples that share API calls but differ in logic；Incorporate control flow and data flow features；Use contrastive learning to emphasize behavioral differences

### case_id=3091 FP boilerplate_overlap

- 方法: `read` vs `downloadFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a skeleton file from classpath using a URL stream, parses sections separated by '---', and validates the expected number of sections.
- B 摘要: Downloads a file from a given URL to a local file with progress tracking using a buffered stream.
- 静态失败原因: The static BERT model likely overfitted to common I/O boilerplate patterns (e.g., opening streams, reading loops, closing) and the presence of similar API calls (e.g., URL, BufferedInputStream), despite the low token overlap. It failed to capture the distinct high-level intents.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels this as non-clone because the functions have fundamentally different purposes: one is for reading configuration resources, the other for downloading files with progress feedback. They lack sufficient behavioral overlap even at a broad Type-3/4 level.
- 共享行为: Both open an input stream from a URL；Both read data in a loop；Both close streams after reading
- 行为差异: A reads from classpath resource; B downloads from arbitrary URL；A parses lines into sections; B writes raw bytes to file；A validates section count; B reports download progress；A uses BufferedReader for text; B uses BufferedInputStream for binary
- 修正建议: Incorporate dataflow analysis to distinguish read-from-resource vs. download-to-file；Add functional context features like method name, class hierarchy, and high-level I/O patterns；Train on more diverse negative examples with shared API usage but different purposes

### case_id=3092 FP boilerplate_overlap

- 方法: `readTwitterFead` vs `doVersionCheck`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads Twitter timeline from a hardcoded URL and returns the response as a string using HttpClient.
- B 摘要: Checks for version updates by reading a version file from a URL and triggers a version check dialog.
- 静态失败原因: Static BERT may have overemphasized the common I/O boilerplate (try-catch, BufferedReader while loop) and ignored the divergent API calls and semantic intent.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely considers these non-clones because their purposes are unrelated (Twitter timeline vs version check) and they have different output behavior and library usage.
- 共享行为: Open a URL and read line by line using BufferedReader；Handle IOException
- 行为差异: A returns concatenated lines; B parses specific lines and calls another method；A uses HttpClient; B uses URL.openStream()；A is Android-specific; B is jEdit-specific with UI interaction
- 修正建议: Incorporate API call and library usage features；Use graph-based models to capture data flow differences；Add type information for input/output (String return vs void)

### case_id=3093 FP lexical_or_api_overlap

- 方法: `getLinksFromURLFast` vs `readIntoList`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Extracts all hyperlinks and their text from a given URL using regex, returning two vectors of links and texts.
- B 摘要: Reads an HTML page from a URL line by line, parses anchor tags to create JMenuItems for a chat application, adding them to a map with action commands.
- 静态失败原因: Static BERT/GraphCodeBERT may have over-relied on lexical overlap (e.g., 'BufferedReader', 'InputStreamReader', 'URL', 'readLine') and similar control flow (while loop reading, parsing HTML tags). It likely missed the high-level semantic difference in purpose and data transformation.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled this as non-clone because the functions serve different overall purposes (general link extraction vs. building a GUI menu) and have different return types and side effects. Even though both parse HTML links, the context and output differ significantly.
- 共享行为: Both read a URL using BufferedReader and InputStreamReader；Both parse HTML anchor tags to extract link information
- 行为差异: A uses regex to find all matches at once; B uses substring parsing line by line；A returns a Vector array of links and texts; B populates a Map with JMenuItems and adds action listeners；A is a general-purpose link extractor; B is specific to building a GUI menu for a chat application；A includes time checking; B has exception handling and GUI action listener setup
- 修正建议: Incorporate data-flow analysis to track how parsed data is used (e.g., returned vs. stored in GUI map)；Use finer-grained representations that distinguish side effects and output types；Include global context about surrounding class or method purpose

### case_id=3094 FN partial_functionality

- 方法: `copyFile` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a file byte by byte from source to destination using a buffer.
- B 摘要: Builds a website for editing by processing pages with XML transformations and writing output files.
- 静态失败原因: Static BERT models likely failed due to very low lexical overlap (token Jaccard 0.09) and the huge structural differences. The model may have missed the underlying file I/O pattern because it is buried in complex unrelated code, and the embedding might focus on token-level differences rather than high-level semantic similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this as a clone because both functions involve reading a file and writing its content to another file, representing a common I/O pattern. Despite the vast difference in overall complexity, the core file-reading and writing loops might be considered semantically similar under a loose Type-4 or partial functionality view.
- 共享行为: Both read from a file using FileInputStream.；Both write to files (output stream or FileWriter).；Both use a buffer for reading data.
- 行为差异: copyFile is a straightforward file copy; buildSiteForEdit is complex with XML transformation, DOM traversal, property handling, and multiple file writes per page.；copyFile uses byte array buffer; buildSiteForEdit uses char array buffer and StringBuffer.；copyFile has minimal error handling; buildSiteForEdit handles FTP exceptions, DOM exceptions, and transforms.；copyFile operates on a single file pair; buildSiteForEdit processes a collection of pages.
- 修正建议: Improve detection of partial functionality clones by using dataflow analysis to extract common I/O operations.；Use hierarchical representations that capture nested loops and file handling patterns.

### case_id=3095 FN partial_functionality

- 方法: `getFile` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, optionally modifies the endpoint location in the XML, and returns the local file path.
- B 摘要: Copies a source file to a destination file using FileChannels and returns success.
- 静态失败原因: The model likely relied on low token overlap and method name/return type differences, missing the shared low-level I/O pattern that BCB considers significant.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may annotate as clones because both functions perform file transfer operations using NIO FileChannel, a specific I/O pattern that some annotators consider a Type-4 partial functionality clone despite different high-level purposes.
- 共享行为: Uses FileChannel for file I/O；Opens input and output streams；Handles IOException；Transfers data between channels
- 行为差异: A downloads from network vs B copies locally；A modifies XML content, B does not；A returns file path string, B returns boolean；A deletes temporary files, B does not
- 修正建议: Incorporate fine-grained I/O operation detection (e.g., FileChannel usage)；Use code structure analysis to identify common subfunctions；Consider broad Type-4 clone definitions that allow partial functional similarity

### case_id=3096 FP partial_functionality

- 方法: `getRequestContent` vs `getPagina`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Opens an HTTP connection to a URL and returns the first line of the response.
- B 摘要: Fetches the entire content of a URL page, concatenating all lines, with authentication and exception handling.
- 静态失败原因: Static BERT may have been misled by lexical overlap (URL, BufferedReader, readLine, etc.) and structural similarity (open, read, close), overlooking the loop versus single read and the exception handling differences.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely labeled 0 because the functions have different output semantics (first line vs full content) and different error handling, which are significant behavioral differences even for broad Type-3/4 clone detection.
- 共享行为: Both retrieve content from a URL using HTTP.；Both use BufferedReader to read from an InputStream.
- 行为差异: A returns only the first line; B returns all lines concatenated.；A throws Exception; B catches exceptions and returns an error string.；B sets a default authenticator; A does not.；A uses HttpURLConnection; B uses URL.openStream().
- 修正建议: Incorporate dataflow analysis to track what and how many lines are read.；Use more precise semantic matching that considers error handling patterns.；Train on more examples that distinguish complete vs partial reads.

### case_id=3097 FN partial_functionality

- 方法: `read` vs `load`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a file or URL into an input stream and returns a status code.
- B 摘要: Loads an XML string from a specific pastebin URL and returns the XML content.
- 静态失败原因: The low token Jaccard (0.189) and different method signatures cause static embedding models to miss the broad functional overlap. The models rely on surface-level similarity and cannot capture abstract commonality.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BigCloneBench may accept Type-4 (functional similarity) because both methods involve reading data from a URL or file and returning a result, despite differences in return type and specific I/O logic.
- 共享行为: Both open a URL (or file) connection and handle IOExceptions.；Both return a value indicating success or failure.
- 行为差异: A handles both file and URL; B only handles a hardcoded pastebin URL.；A returns integer status; B returns XML string.；A uses BufferedInputStream and delegates reading; B uses BufferedReader and reads lines.；B shows a JOptionPane dialog on error; A sets a status field.
- 修正建议: Incorporate control flow and data flow analysis to detect abstract I/O patterns.；Use similarity metrics that consider high-level intent like reading from external resource.

### case_id=3098 FP boilerplate_overlap

- 方法: `addFileToTarGz` vs `readData`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Adds a file to a tar.gz archive recursively.
- B 摘要: Reads configuration tokens into sets and maps for character encoding.
- 静态失败原因: Static BERT likely relied on superficial similarities like common Java keywords (File, IOException, StringTokenizer) or similar control flow structures (while loops, try-catch), despite low token Jaccard similarity.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB correctly labels them as non-clones because they perform entirely different tasks with no semantic overlap.
- 共享行为: Both involve loops and conditional logic；Both use I/O (FileInputStream vs StringTokenizer)；Both handle exceptions
- 行为差异: A handles file compression, B parses configuration strings；A writes to a TarArchiveOutputStream, B populates HashSets and HashMaps；A is recursive, B is a single sequential method；A deals with file system, B deals with string tokenization
- 修正建议: Incorporate deeper semantic understanding of API usage and data flow；Use graph-based code representations to capture structural differences；Train on more diverse negative pairs with low lexical but high structural similarity

### case_id=3099 FP other

- 方法: `actionPerformed` vs `createTempFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Handles action events to set preferences for various tools (Graphviz, ImageMagick, etc.) and updates UI components.
- B 摘要: Creates a temporary file from a resource input stream for testing purposes.
- 静态失败原因: Static BERT models may over-rely on token overlap or API usage; despite low Jaccard, the model might have been misled by the presence of 'File' and 'IOException' tokens, or by the truncation of the large method in A causing some spurious similarity.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely labeled this as not a clone because the functions have completely different purposes, sizes, and contexts; they are not functionally similar even under relaxed standards.
- 共享行为: Both involve file handling but at different levels: A uses file chooser dialogs, B creates temp files.
- 行为差异: A is a large event handler with multiple conditional branches; B is a simple utility method.；A interacts with UI components and persistence; B only performs file I/O.；A handles multiple commands; B has a single purpose.；A is tied to a specific GUI framework; B is a test helper.
- 修正建议: Improve model to capture control flow and data dependencies beyond surface-level tokens.；Use graph-based representations to distinguish large UI event handlers from small utility methods.；Incorporate length and complexity as features to avoid false positives on very different function sizes.

### case_id=3100 FN benchmark_preference_bias

- 方法: `sendExceptionToServer` vs `getWebPage`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Sends exception details encoded as HTTP POST data to an error server and prints the response.
- B 摘要: Retrieves the content of a web page given a URL and returns it as a string, throwing an error on failure.
- 静态失败原因: The static model likely relied on low token overlap and correctly predicted non-clone; the 'error' arises from a potentially erroneous BCB label, not a model deficiency.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider both as 'network communication' or 'HTTP handling' functions, accepting broad functional similarity based on common API usage, which is overly broad.
- 共享行为: Both use URL and BufferedReader to handle HTTP communications；Both catch IOException
- 行为差异: A sends data via POST while B reads via GET；A returns void and prints messages, B returns a string；A encodes multiple parameters, B just reads lines；Error handling differs: A prints, B throws Error
- 修正建议: Re-evaluate BCB label for this pair; consider stricter functional criteria.；Improve model to detect broad functional categories only when high-level behavior matches.

### case_id=3101 FP library_context_missing

- 方法: `copyFile` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `context_recovery_then_dynamic`；动态可解性: `low`；执行优先级: `low`
- A 摘要: Copies a file from source to destination using NIO FileChannel.
- B 摘要: Handles GUI action events for a settings dialog, processing commands like GRAPHVIZ, IMAGEMAGICK, etc.
- 静态失败原因: The static BERT model likely over-relied on superficial features such as the presence of 'File' and common Java keywords, failing to capture the semantic difference between a file copy utility and a GUI event handler. The long length of function B may have caused the model to lose context.
- 静态 case study: 该类错误缺少关键上下文或需要深层语义，纯静态方法不可靠。
- 动态 case study: 动态执行价值较低：样本可能依赖库、框架、网络、GUI、数据库或项目上下文，需要先恢复环境或 mock 依赖。
- BCB 偏好解释: BCB labels these as non-clones because they have completely different purposes and logic, with no significant shared functionality.
- 共享行为: Both are Java methods.；Both may throw exceptions (IOException or Exception).
- 行为差异: Function A performs file copy; Function B handles GUI events.；Function A is a static utility; Function B is an instance method overriding ActionListener.；Function A uses NIO channels; Function B uses Swing components.；Function A is short and focused; Function B is long with multiple conditional branches.
- 修正建议: Train with more diverse examples that distinguish between file I/O and GUI event handling.；Incorporate type and API usage information to better differentiate library contexts.；Use graph-based models such as CodeBERTa or graph neural networks that capture structural and data flow differences.

### case_id=3102 FN partial_functionality

- 方法: `combineJs` vs `modifyApplicationMessage`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Combines multiple JavaScript files from URLs into a single file with optional minification and updates an HTML element.
- B 摘要: Modifies or adds a key-value pair in a locale-specific properties file, creating the file from an English template if needed.
- 静态失败原因: Static BERT models rely on token/API overlap and structural similarity; the low Jaccard score (0.167) and different domain-specific APIs (e.g., JavaScriptCompressor vs Properties) likely prevented detection of abstract semantic similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB annotators may have considered both as 'resource file processing' utilities with similar boilerplate code structures, accepting them as Type-4 (semantic) clones under a broad interpretation.
- 共享行为: Both perform file I/O with readers and writers；Both handle exceptions and use try-catch；Both manipulate textual content
- 行为差异: Function A downloads and merges multiple JS files; Function B reads and edits a single properties file；Function A involves minification and concatenation; Function B involves key-value replacement or addition；Function A updates an HTML element; Function B does not return or modify external state apart from file
- 修正建议: Incorporate higher-level semantic understanding of file processing patterns；Use context-aware embeddings that capture underlying purpose beyond surface syntax；Fine-tune on broader clone types including Type-4 with diverse domains

### case_id=3103 FP lexical_or_api_overlap

- 方法: `executePost` vs `main`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Executes an HTTP POST request with parameters and returns the response as a string.
- B 摘要: Reads from a URL and prints each line to the console (HTTP GET equivalent).
- 静态失败原因: Static BERT/GraphCodeBERT likely relied on lexical overlap (URL, BufferedReader, readLine) and similar API calls, ignoring deeper semantic differences in method type and output handling.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels as non-clone because the functions have distinct purposes (POST vs GET, return vs print) despite sharing common HTTP boilerplate.
- 共享行为: Both use URL and BufferedReader to read HTTP response.
- 行为差异: Function A uses POST method and sends parameters; Function B uses GET without parameters.；Function A returns the response; Function B prints to console.；Function A handles exceptions with try-catch; Function B throws IOException.；Function A has output stream for writing parameters; Function B does not.
- 修正建议: Incorporate dataflow analysis to track whether output is returned or printed.；Distinguish between POST and GET HTTP methods.；Add control-flow features capturing exception handling vs throws.

### case_id=3104 FN benchmark_preference_bias

- 方法: `doGet` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Handles HTTP GET by translating path, reading local file, and copying bytes to response stream.
- B 摘要: Retrieves resource by name, caches it locally from network, and returns cached or downloaded InputStream.
- 静态失败原因: Static model correctly identified low token overlap and structural differences, but BCB label considers them clones under broad Type-4 criteria.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might annotate as clone based on high-level pattern of reading a file and providing content, ignoring caching and network details as accidental complexity.
- 共享行为: Both read file contents and output via streams
- 行为差异: A is simple file serving without caching; B implements caching, network download, and conditional cache update
- 修正建议: Re-evaluate BCB annotation: these functions serve different purposes and are not semantically equivalent even under broad Type-4 definition.；Alternatively, increase token overlap by normalizing API names if the goal is to capture caching pattern.

### case_id=3105 FP boilerplate_overlap

- 方法: `loadSourceCode` vs `downloadFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Loads source code from a file, applies syntax highlighting line by line, and stores the result as an HTML string.
- B 摘要: Downloads a file from a URL to a local destination with progress reporting, using buffered streams.
- 静态失败原因: The model likely overemphasized the shared boilerplate of stream I/O (open, read loop, close) and common API calls (URL, InputStream, File), leading to a false positive. The token overlap, though low, may still capture these structural patterns, and the model may lack sensitivity to the high-level semantic differences in input, output, and side effects.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels this as non-clone because the methods serve fundamentally different purposes: one is for displaying highlighted source code, the other for downloading files. Despite structural similarities in stream handling, the functional intent and output are distinct, aligning with BCB's emphasis on semantic similarity in purpose.
- 共享行为: Both open a stream to read data (InputStream or URLConnection).；Both use a loop to read data and handle potential exceptions.；Both close the stream after reading.；Both involve file-related operations (File, FileOutputStream).
- 行为差异: A reads text lines and applies syntax highlighting; B reads bytes and writes to a file.；A sets a string field (sourceCode) with no return; B returns a boolean and has side effects (download progress, file creation).；A uses BufferedReader and InputStreamReader; B uses BufferedInputStream and BufferedOutputStream.；B has progress reporting via MessageFrame; A does not.
- 修正建议: Train on more examples that pair different functions with similar low-level I/O patterns.；Incorporate data-flow analysis to distinguish variable usage and output behavior.；Use method name and parameter/return type embeddings to capture high-level purpose.；Consider class-level context to understand the role of the method within its class.

### case_id=3106 FN lexical_or_api_overlap

- 方法: `addIDs` vs `retrieveTemplate`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Parses HTML from a metabolite database URL to extract IDs and molecular weight, updating a PeakListRow object with various identifiers.
- B 摘要: Reads a blog URL and caches the full HTML content as a string for later use.
- 静态失败原因: The functions have very low token Jaccard (0.15) and only share boilerplate code (URL, BufferedReader, readLine). Static models like GraphCodeBERT rely on surface form and structural patterns, failing to capture the vastly different purposes and data processing logic.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may label this as a clone due to the broad similarity of both functions performing a web request and reading data, which could be considered Type-4 semantic similarity under lenient criteria.
- 共享行为: Both open a URL and read lines using BufferedReader.；Both handle I/O operations.；Both use similar boilerplate code for opening streams.
- 行为差异: A parses specific HTML patterns and extracts multiple data fields; B simply concatenates all lines without parsing.；A updates many fields on a row object; B caches the entire result as a string.；A returns an integer score; B returns a string template.；A has error handling returning 0; B throws an exception.
- 修正建议: Incorporate data-flow analysis to trace how variables (e.g., row vs. cachedTemplate) are used after reading.；Use type information (return types: int vs. String) to disambiguate.；Analyze control flow depth and conditional complexity.

### case_id=3107 FN benchmark_preference_bias

- 方法: `serialize` vs `modifyApplicationMessage`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Serializes an IMS content package to an output stream using a parser.
- B 摘要: Modifies a key-value pair in a locale-specific properties file, creating the file from an English default if missing.
- 静态失败原因: Static BERT likely correctly predicted non-clone based on low token overlap and clear semantic difference; the BCB label appears to be an outlier.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have considered this a clone due to broad Type-4 structural similarity (both involve reading from a file and writing to a stream/file) or a misannotation in the dataset.
- 共享行为: Both perform file I/O operations.；Both may write data to a file or output stream.
- 行为差异: Different domains: package serialization vs. properties file editing.；Different data structures: parser vs. Properties object.；Different parameters: OutputStream vs. locale, name, value.；Function A reads a temporary file, Function B reads and writes a properties file with conditional creation.
- 修正建议: Review BCB annotation for this pair to ensure consistency with clone definitions.；Enhance training data by filtering out low-confidence labels.

### case_id=3108 FP lexical_or_api_overlap

- 方法: `createHTML` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: This method generates an HTML page for a UI dashboard, either displaying a logo or fetching dashboard content from a database.
- B 摘要: This method performs a Google image search by sending an HTTP request, parsing the HTML response, and extracting image URLs.
- 静态失败原因: Static BERT embeddings may overemphasize shallow lexical overlap (e.g., 'BufferedReader', 'InputStreamReader', 'URL') and miss deep semantic differences due to different control flows and external API usage (database vs HTTP).
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this pair as non-clone because the methods serve entirely different purposes: one is UI generation with database access, the other is web scraping. Their only overlap is using standard Java IO, which does not imply functional similarity.
- 共享行为: Both use BufferedReader to read from an input stream obtained from a URL.；Both handle potential IOExceptions.
- 行为差异: Method A builds an HTML string for internal UI rendering, while Method B fetches external image URLs and stores them in a list.；Method A uses database queries and conditional logic based on an enum, Method B uses HTTP connection and string parsing.；Method A has multiple output cases, Method B has a single action.
- 修正建议: Include structural features like control flow graphs and data flow analysis to differentiate UI generation from HTTP scraping.；Use contrastive learning to emphasize functional uniqueness rather than shared utility classes.；Enhance training data with more non-clone pairs that share common IO patterns but different purposes.

### case_id=3109 FN partial_functionality

- 方法: `copyResource` vs `transferWSDL`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource from a URL or local file to a destination file by reading byte by byte.
- B 摘要: Downloads a WSDL from a URL via HTTP with optional authentication, handles errors, and saves to a temporary file with generated name, returning the file path.
- 静态失败原因: Static BERT likely focused on lexical and syntactic differences, noting low token Jaccard similarity (0.175) and different method names, missing the high-level semantic similarity of copying stream to file due to long-range dependencies and structural differences.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB labels them as clones because both functions perform the core task of copying data from a source to a file output; differences in source type, error handling, and output file setup are considered non-essential under broad Type-3/Type-4 clone definitions.
- 共享行为: Both read data from a source (URL or file) and write it to an output file.
- 行为差异: Function B uses HTTP connection with headers and authentication; function A supports only direct URL stream or local file.；Function B handles error streams and throws specific WiseConnectionException; function A throws generic Exception.；Function B uses IOUtils.copyStream (buffered) while A reads byte by byte.；Function B generates a temporary file name with a unique ID; function A uses a fixed destination file path.
- 修正建议: Improve training data with diverse implementations of the same high-level task (e.g., copy stream to file).；Incorporate dataflow or program dependence graphs to capture the core 'copy' pattern.；Use contrastive learning with positive pairs having low token overlap but similar semantics.

### case_id=3110 FN benchmark_preference_bias

- 方法: `main` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a URL, reads it as a ZIP archive, and extracts all entries to files.
- B 摘要: Copies a source file to a target file using FileChannel.transferTo.
- 静态失败原因: The low token Jaccard (0.14) and distinct APIs (ZipInputStream vs FileChannel) likely led the model to correctly predict non-clone; the BCB annotation appears over-broad, causing a false negative error from the model's perspective.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have annotated these as clones due to a very broad interpretation of 'file copying' or 'I/O operations', but the actual functionality differs significantly in scope and complexity.
- 共享行为: Both involve reading from an input source and writing to a file output
- 行为差异: Function A handles network I/O, ZIP decompression, and multiple output files; Function B handles only local file copy with a single output；Function A uses ZipInputStream and BufferedOutputStream; Function B uses FileChannel；Function A extracts multiple entries; Function B copies a single file
- 修正建议: Improve functional decomposition to distinguish between diverse I/O tasks；Incorporate task-level classification to avoid over-generalization

### case_id=3111 FN partial_functionality

- 方法: `copyFile` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Copies a file to a destination file using buffered streams.
- B 摘要: Configures and launches a project by processing POM files, setting Hibernate dialect, and copying a reverse engineering file from the bundle.
- 静态失败原因: Static BERT likely predicted non-clone because of low lexical overlap, different method names, and distinct overall functionality; it may not have recognized the partial file copy similarity that BCB considered.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have considered the shared file copy sub-task as sufficient for Type-4 clone, despite the overall functions having different purposes.
- 共享行为: Both involve reading from an input source and writing to an output destination (file copy).
- 行为差异: Function A is a simple, standalone file copy; Function B is a complex project setup method with many additional steps.；Function A returns the destination file or null; Function B returns void and throws CoreException.；Function A operates on two File parameters; Function B takes ILaunchConfiguration, String, ILaunch, IProgressMonitor.；Function A uses FileInputStream and FileOutputStream; Function B uses InputStream from bundle and ByteArrayOutputStream.
- 修正建议: Incorporate sub-task or partial functional similarity detection, possibly using graph-based or flow-based analysis to capture shared operations within larger functions.

### case_id=3112 FN benchmark_preference_bias

- 方法: `main` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: A test method that writes known byte values to a file and uses a custom StraightStreamReader to read back and verify correctness across various read methods.
- B 摘要: A launch method that configures and executes an Eclipse launch configuration for a NexOpen project, handling Maven POM files and Hibernate dialect properties.
- 静态失败原因: The model correctly identified low token overlap (0.072) and no semantic equivalence, so it predicted non-clone. The failure is not in the model but in the BCB annotation, which appears inconsistent.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: The annotator may have considered both as involving file I/O and exception handling, or perhaps a broad Type-4 semantic similarity, but in practice they are completely different in purpose and functionality.
- 行为差异: One is a unit test for I/O reading; the other is an IDE launch configuration setup.；A deals with raw byte streams; B deals with XML, properties, and project resources.；A is self-contained; B depends on Eclipse framework and external bundles.；Exception handling differs: A catches IOException; B wraps CoreException in RuntimeException.
- 修正建议: Review BCB annotation guidelines to ensure consistency across different domains.；Consider whether partial functionality clones should include such disparate methods.；If BCB intended these as non-clones, the model is correct; if BCB intended them as clones, the model needs to capture very abstract similarities.

### case_id=3113 FN partial_functionality

- 方法: `main` vs `register`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends a POST request to RenRen API with feed publishing parameters and prints the response.
- B 摘要: Registers a user by encoding password, creating a forum account via HTTP request, persisting user, and sending confirmation email.
- 静态失败原因: Static BERT/GraphCodeBERT relies on token-level overlap (low Jaccard 0.09) and may miss high-level structural patterns; different method names and domains cause negative prediction.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB considers Type-4 clones where functions share a common pattern (HTTP request/response reading) even if high-level semantics differ; structural similarity in I/O operations leads to clone label.
- 共享行为: Both construct URLs；Both open HTTP connections；Both read response lines from BufferedReader；Both involve I/O operations
- 行为差异: Function A is a static void main, B is a boolean method；Different business logic: feed publishing vs. user registration；Different error handling: A prints, B catches exceptions and wraps；A uses hardcoded parameters, B uses dynamic user object
- 修正建议: Incorporate structural features like AST or graph matching to capture I/O patterns；Use models that focus on sequence of operations rather than exact tokens；Add domain-specific features for HTTP communication patterns

### case_id=3114 FP boilerplate_overlap

- 方法: `actionPerformed` vs `bootKernel`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Handles various UI action commands (GRAPHVIZ, IMAGEMAGICK, etc.) by opening file chooser dialogs, saving preferences, and updating UI components.
- B 摘要: Boots a kernel by reading configuration from assets, copying sdcard assets, loading a kernel class via reflection, and invoking its boot method.
- 静态失败原因: Static BERT may have been misled by overlapping boilerplate elements (try-catch, file I/O, logging) and the presence of common keywords like 'file', 'if', 'return', causing it to overgeneralize patterns.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled non-clone because the functions have completely different purposes, domains, and syntax, with no meaningful functional overlap beyond generic programming constructs.
- 共享行为: Both perform file I/O operations (reading files/assets).；Both have exception handling (try-catch) and logging.
- 行为差异: Function A is UI-centric with multiple branches for different action commands; function B has a linear flow for kernel initialization.；Function A updates user preferences and UI state; function B copies assets to sdcard and loads a kernel class.；Function A targets desktop Swing; function B targets Android.；Function A handles user interaction via dialog boxes; function B is automated without user input.
- 修正建议: Incorporate domain-specific training data to distinguish UI event handling from system initialization.；Use dataflow or control-flow analysis to capture actual program behavior beyond surface tokens.；Focus on method-level semantic representations that capture purpose and side effects.

### case_id=3115 FP lexical_or_api_overlap

- 方法: `get` vs `import_hints`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Makes HTTP GET request with game headers, reads and decodes GameRecord objects from response lines.
- B 摘要: Reads hint pieces from a URL file, parses integers, and places pieces on a board.
- 静态失败原因: The model likely over-relied on similar API sequences (URL, openConnection, BufferedReader, readLine) and try-catch structure, ignoring the distinct semantics and method purpose.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB considers non-clone because the overall functionality and data processing are entirely different; the shared pattern is only common boilerplate for network I/O.
- 共享行为: Open URL connection and read lines with BufferedReader；Handle IOException；Parse tokens from lines
- 行为差异: A returns an array of GameRecord; B returns a boolean；A filters lines starting with '#'; B expects specific token format；A includes custom request headers; B does not；A prints error message on non-OK response; B returns false on exception
- 修正建议: Use dataflow or control-flow analysis to separate core logic from boilerplate；Incorporate method name and context embeddings to emphasize purpose；Train on tasks that require distinguishing superficial API similarity from semantic difference

### case_id=3116 FN partial_functionality

- 方法: `testNetworkHTTP` vs `doVersionCheck`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends multiple hardcoded HTTP GET requests and reads responses line by line without processing, primarily for logging/testing.
- B 摘要: Sends a single HTTP GET request to a configurable version check URL, parses the response for version and build info, and displays a message to the user based on the result.
- 静态失败原因: Static BERT models like CodeBERT rely on token overlap and syntactic similarity; here token Jaccard is low (0.195). They may fail to recognize the coarse-grained structural pattern of 'open connection - read lines - close' across different APIs and incidental details like URL construction and response processing.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often considers Type-4 clones where the overall pattern of network communication and line-by-line reading is present, even if the specific usage of the read data differs. The shared structure of URL.openStream(), BufferedReader, and while loop suggests a common template for HTTP response reading.
- 共享行为: Both open an HTTP URL connection and read data line by line using BufferedReader；Both handle IOException with try-catch；Both use InputStreamReader to decode the input stream；Both perform some form of network I/O
- 行为差异: Function A makes multiple requests (6) with hardcoded URLs; Function B makes one request with a dynamic URL from configuration；Function A does not parse or process the response lines; Function B parses lines for version and build strings；Function A logs to console or prints stack trace; Function B interacts with a View and shows messages to the user；Function A uses finally block to disconnect HttpURLConnection; Function B closes the stream and does not explicitly disconnect
- 修正建议: Incorporate dataflow or control-flow representations to capture the sequence of network I/O operations；Use graph-based models (e.g., GraphCodeBERT) that better capture structural similarities；Augment training with examples that have partial functional overlap to learn broad clone types

### case_id=3117 FP lexical_or_api_overlap

- 方法: `main` vs `createOutputStream`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.97`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Main method that generates adapter classes from a Prolog file using a framework.
- B 摘要: Creates a BufferedWriter that copies entries from an input ZIP to output ZIP, skipping content.xml, then adds a new content.xml with UTF-8 encoding.
- 静态失败原因: Static BERT models may focus on overlapping token sequences (e.g., 'new File', 'FileOutputStream', 'BufferedWriter', 'IOException') and common structural patterns (e.g., try-catch, loops) while missing the fundamentally different control and data flow. The low token Jaccard (0.059) suggests the model might have been misled by rare but shared API calls or accidentally learned a superficial similarity.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clones when functions have completely different high-level purposes, even if they share some low-level API usage. Here, one is a code generator and the other is a file compressor, so BCB correctly marks them as non-clones.
- 共享行为: Both involve file I/O operations with reading and writing files.
- 行为差异: Different input/output: A takes command-line arguments and generates Java classes; B takes two file paths and produces a compressed output.；Different logic: A parses Prolog, generates adapters, and writes multiple resources; B exclusively handles ZIP stream copying with filtering.；Different error handling: A uses broad exception handling; B does not handle exceptions (throws IOException).；Different output type: A is void and writes to a .jar file; B returns a BufferedWriter for streaming.
- 修正建议: Incorporate dataflow and control-flow analysis to distinguish high-level intent.；Use function-level context (method name, parameters, return type) as additional features.；Train on a more diverse set of non-clones to reduce sensitivity to generic API usage.

### case_id=3118 FN benchmark_preference_bias

- 方法: `testNetworkHTTP` vs `postXml`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Test method that makes multiple HTTP GET requests to various URLs and reads responses without using them.
- B 摘要: Utility method to send an HTTP POST request with XML content, set headers, write request body, read response, and return it as a string.
- 静态失败原因: Static BERT/GraphCodeBERT might have failed because it focused on lexical/token overlap (which is low at 0.184) and missed the structural similarity in HTTP request pattern; or it might have correctly identified them as non-clones but BCB labeled them as clone due to broad criteria.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might consider both as HTTP client operations that open a connection, read input, and handle exceptions, thus partial functional similarity despite differing HTTP methods and purpose.
- 共享行为: Both use HttpURLConnection to make HTTP requests；Both read the response using BufferedReader and InputStreamReader；Both handle IOException
- 行为差异: Function A makes multiple GET requests; Function B makes a single POST request；Function A does not write any request body; Function B writes XML to output stream；Function A discards the response; Function B returns the response as a string；Function A disconnects in finally; Function B does not explicitly disconnect
- 修正建议: Improve detection of Type-4 clones by considering API usage patterns beyond exact tokens；Incorporate control flow and data flow analysis to distinguish between GET and POST；Use graph-based representations to capture structural similarity of HTTP request handling

### case_id=3119 FN partial_functionality

- 方法: `readRemoteFile` vs `register`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.75`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a remote file from a URL and returns its contents as a string, handling EOF and IO exceptions.
- B 摘要: Registers a user by validating, encoding password, setting registration date, adding default authority, creating hash, calling an external forum URL to create a forum user, persisting the user, and sending a confirmation email, returning success/failure.
- 静态失败原因: Static BERT models like GraphCodeBERT rely on token and surface-level features; the low token Jaccard (0.174) and differing method names and overall structure (return type, exception types, auxiliary operations) likely led to a non-clone prediction despite the shared URL-reading logic being semantically significant but overshadowed by different contexts.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may classify these as clones because both contain a similar code pattern of opening a URL, reading lines, and handling IO exceptions, which qualifies as a Type-3/Type-4 clone under broad partial-functionality similarity.
- 共享行为: Opens a URL connection and reads data line by line using BufferedReader.；Uses InputStream and InputStreamReader to read from the URL.；Handles IOException during the network read.
- 行为差异: Function A's sole purpose is to read a file; Function B performs complex user registration with multiple steps.；Function A returns a concatenated string; Function B returns a boolean.；Function B includes extensive logging, error handling with RuntimeException, and database persistence.；Function A uses a fixed URL from StaticData; Function B constructs a dynamic URL with parameters.
- 修正建议: Incorporate structural matching that identifies shared code fragments even when embedded in larger functions.；Use graph-based representations to capture data flow and control flow similarities beyond token overlap.；Train or adapt models to recognize common subroutines (e.g., URL reading) across vastly different functions.

### case_id=3120 FN benchmark_preference_bias

- 方法: `doGet` vs `modifyApplicationMessage`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Handles HTTP GET request to retrieve and render a portal page, managing visibility, caching, and statistics.
- B 摘要: Modifies a locale-specific properties file by reading, updating or appending a message key-value pair.
- 静态失败原因: The static model correctly identified them as non-clones due to low token overlap (Jaccard 0.14) and completely different contexts, so it did not fail; the BCB label is likely erroneous.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled these as clones due to both having try-catch blocks, logging, and possibly similar patterns of resource access and error handling, but this is a very broad interpretation and likely a labeling error.
- 行为差异: Function A handles HTTP requests and serves web pages; Function B modifies properties files without any web interaction.；Function A involves page rendering and caching; Function B involves file I/O for localization.；Function A uses servlet API and portal context; Function B uses Java file and properties classes.；The core logic and data flow are entirely different.
- 修正建议: Review BCB annotation guidelines to ensure consistency in labeling broad Type-3/4 clones.；Consider adding more context or domain-specific features to detect accidental similarities.

### case_id=3121 FP lexical_or_api_overlap

- 方法: `createHTML` vs `getVersion`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Creates an HTML page by loading a CSS file and generating dynamic content based on a page type, including database queries.
- B 摘要: Retrieves the latest version string from a remote URL by reading the first line of the response.
- 静态失败原因: The static model likely focused on the similar high-level structural overlap (URL, BufferedReader, readLine, catch) and ignored the large difference in the actual data processing and output, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB annotators considered the overall functionality rather than lower-level I/O patterns; the functions have completely different purposes (HTML generation vs. version fetching), so they are not clones.
- 共享行为: Both open a URL to read a resource using BufferedReader and readLine() in a loop.；Both catch exceptions (IOException/Exception) and handle errors similarly.；Both return a String that is built from remote or resource content.
- 行为差异: Function A generates a complete HTML page with CSS and dynamic database content; Function B simply returns a version string.；Function A uses a switch-case on page type; Function B has no branching logic beyond null assignment.；Function A reads from a classpath resource; Function B reads from an HTTP URL.；Function A uses multiple try-catch blocks and database query; Function B is simpler with a single catch.
- 修正建议: Incorporate global context such as method names and surrounding code to capture intent.；Use dataflow analysis to identify how the read data is used (e.g., building HTML vs. returning a simple string).；Improve training with examples that have similar I/O patterns but different semantics to reduce bias.

### case_id=3122 FN benchmark_preference_bias

- 方法: `extractUninstallFiles` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Extracts uninstall files during application upgrade, managing directories and copying old setup classes.
- B 摘要: Launches a Maven-based NexOpen project configuration within Eclipse, handling POM files and reverse engineering resources.
- 静态失败原因: Static BERT did not fail; it correctly predicted 0 (non-clone), which aligns with the actual semantic mismatch. The error is a BCB annotation error (false negative from the detector's perspective).
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB likely mislabeled this pair as clone due to superficial similarity in handling files and streams, or due to both being part of larger installation/setup context in the codebase. However, their functionality is distinct, and standard Type-3/Type-4 criteria would not deem them clones.
- 共享行为: Both involve file I/O operations and directory/resource management.
- 行为差异: Purpose: Function A handles uninstall/upgrade for a desktop application; Function B sets up an Eclipse launch configuration for a Maven project.；Algorithm: A uses complex file copying and deletion with version checks; B uses XML parsing, property files, and resource stream copying.；Return: A returns a File; B returns void.；Context: A is part of a software installer; B is part of an IDE plugin for business project management.
- 修正建议: Verify BCB annotation for this pair; likely an annotation mistake.；If not a mistake, consider that BCB may have broader Type-4 criteria that include any file-manipulation methods, but that is overly loose.

### case_id=3123 FN benchmark_preference_bias

- 方法: `parse` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Parses an input stream, optionally copying it to a file if a resource name is in a desired list, otherwise delegates to a downstream parser.
- B 摘要: Launches a NexOpen project by checking project attributes, processing Maven POM files, configuring Hibernate dialect, and setting up reverse engineering files.
- 静态失败原因: Static BERT likely correctly predicted non-clone due to very low token Jaccard (0.059) and differences in structure and length, so it did not fail but was overridden by BCB's broad annotation.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider them clones due to both implementing a form of 'conditional processing with delegation' and sharing the use of IOUtils.copy, despite vastly different domains and complexity.
- 共享行为: Both involve conditional logic based on some configuration or metadata.；Both use IOUtils.copy for file/stream copying.；Both include fallback or logging when conditions are not met.
- 行为差异: Function A is a simple I/O filter; Function B is a complex Eclipse launch workflow involving multiple files and external resources.；Function A operates on a generic InputStream; Function B operates on Eclipse IProject and ILaunchConfiguration.；Function A's condition is based on a resource name lookup; Function B's condition is based on project type and existence of specific files.；Function A delegates to another parser; Function B performs extensive project setup and job scheduling.
- 修正建议: Re-evaluate BCB label for this pair; consider stricter semantic criteria.；Include domain-specific or structural features to avoid overgeneralizing shared utility patterns.

### case_id=3124 FN boilerplate_overlap

- 方法: `sendExceptionToServer` vs `createDialogArea`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.3`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends an exception report to a server by building HTTP POST data.
- B 摘要: Creates a dialog area reading a license file from a bundle resource.
- 静态失败原因: Static BERT likely relied on low token overlap and failed to recognize the shared I/O patterns that BCB annotators considered similar.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may consider them clones due to similar I/O structure and exception handling patterns, despite different purposes.
- 共享行为: Both use URL and I/O streams；Both handle exceptions with try-catch
- 行为差异: A sends data to server; B reads resource and displays UI；A constructs POST parameters; B reads text from file；B creates UI widgets; A does not
- 修正建议: Incorporate data flow analysis to distinguish send vs receive operations；Add representation of resource usage and network direction

### case_id=3125 FP lexical_or_api_overlap

- 方法: `readUNI` vs `doVersionCheck`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a TSV file from a URL and populates a vector with concatenated id and description.
- B 摘要: Reads a version file from a URL to extract build numbers and perform a version check.
- 静态失败原因: The model likely overemphasized token overlap from common I/O patterns (URL, openStream, Scanner, BufferedReader) and structural similarity (try-catch, line reading), leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels true clones when functions share a high-level functional goal, but here the tasks (population of a collection vs. version check) are fundamentally different despite similar I/O patterns.
- 共享行为: Both open a URL and read from an InputStream；Both iterate over lines of text；Both handle IOException with exception handling；Both use try-catch blocks
- 行为差异: readUNI parses tab-separated values; doVersionCheck checks line prefixes；readUNI adds data to a Vector; doVersionCheck calls another method based on extracted values；Different error handling: readUNI swallows MalformedURLException; doVersionCheck shows error dialog；readUNI returns void; doVersionCheck is void but performs conditional version check
- 修正建议: Incorporate dataflow or control-flow analysis to distinguish output usage；Enhance training data with non-clones that share I/O boilerplate；Use task-specific embeddings that capture functional intent

### case_id=3126 FN benchmark_preference_bias

- 方法: `doGet` vs `copy`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Handles HTTP GET request to retrieve and serve a web page with access control, logging, and caching.
- B 摘要: Copies a file from one path to another using NIO FileChannel.
- 静态失败原因: Static BERT model correctly predicted non-clone due to low lexical overlap and distinct API usage; conflicting with possibly noisy BCB label.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB label 1 likely a misannotation; possibly due to both methods having similar try-catch-finally structure and performing I/O operations, but functional similarity is low.
- 共享行为: Both involve reading and writing data；Both use I/O streams/channels；Both perform some error handling
- 行为差异: A is a web servlet handler; B is a file copy utility；A involves authentication, logging, caching; B does not；A uses HttpServletRequest/Response; B uses File I/O；A has complex control flow with multiple nested exceptions; B is straightforward
- 修正建议: Re-annotate this pair as non-clone in BCB；Use functional similarity metrics rather than structural heuristics

### case_id=3127 FN partial_functionality

- 方法: `transferWSDL` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL and saves it to a temporary file, returning the file path.
- B 摘要: Builds a site for editing by processing multiple pages with XML transformations and writing output files.
- 静态失败原因: The static method likely relied on token overlap and API similarity, which are low here (Jaccard=0.1185). It failed to capture the higher-level I/O pattern shared between the two functions.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label them as clones under a broad Type-4 classification because both involve reading from an external source and writing to a file, but the overall functionality is quite different.
- 共享行为: Both perform file I/O operations.；Both handle exceptions and use streams.
- 行为差异: transferWSDL downloads a single file via HTTP; buildSiteForEdit processes multiple pages with XML transformations.；transferWSDL returns a file path; buildSiteForEdit is void and writes multiple files.；buildSiteForEdit involves complex string manipulation and property handling; transferWSDL is straightforward.
- 修正建议: Incorporate dataflow analysis to detect common I/O operations.；Use program slicing to isolate core behavior.；Train on more diverse functional clones with low lexical overlap.

### case_id=3128 FP lexical_or_api_overlap

- 方法: `copyFile` vs `main`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Copies a file from input to output using Java NIO FileChannel.
- B 摘要: Main method that parses command-line arguments, reads a Prolog file, and generates adapter classes and resources.
- 静态失败原因: Static BERT/GraphCodeBERT may have been misled by common tokens like 'File', 'IOException', 'close', or method signature patterns, but the overall semantics are very different.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels as non-clone because the functions have entirely different purposes and logic, despite both being file-related. The partial functionality overlap is minimal.
- 共享行为: Both use File objects；Both handle IOException；Both involve file I/O operations
- 行为差异: Function A is a simple file copy; Function B is a complex workflow with argument parsing, file reading, parsing, class generation, and serialization.；Function A has no command-line interaction; Function B prints usage and debug output.；Function A operates on two files; Function B operates on multiple files and generates output.
- 修正建议: Improve handling of global context and function purpose；Use more advanced code representation that captures control flow and data dependencies；Incorporate documentation or comments to distinguish trivial I/O utilities from complex business logic

### case_id=3129 FP lexical_or_api_overlap

- 方法: `read` vs `checkForUpgrade`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a skeleton file from the classpath, parses lines into sections separated by '---', validates the number of sections, and throws an exception if mismatch.
- B 摘要: Handles an upgrade check event: hides UI components, queries a license server, processes upgrade records, inserts them into a database, and updates UI visibility based on results.
- 静态失败原因: Static BERT/GraphCodeBERT likely relied heavily on token overlap (e.g., 'BufferedReader', 'InputStreamReader', 'URL', 'readLine', 'while', 'null') and the common loop structure, ignoring the broader semantic context. The model may have been misled by the superficial syntactic similarity of reading lines, while missing the fundamentally different business logic and data flow.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB (BigCloneBench) labels non-clones when functions have entirely different purposes, even if they share low-level I/O patterns. Here, the core logic is unrelated: one is a file parser with validation, the other is an upgrade manager with network queries and UI interaction. The partial overlap in reading lines is incidental and not enough to consider them functionally similar under BCB's Type-3/4 criteria.
- 共享行为: Both use BufferedReader to read lines from a URL or stream.；Both use InputStreamReader with an input stream from URL.；Both have a while loop reading lines until null.
- 行为差异: Method A reads a local resource file for skeleton loading; method B reads from a remote HTTP URL for upgrade check.；Method A validates section count; method B performs complex license and upgrade logic with database operations and UI updates.；Method A throws an exception on mismatch; method B shows UI messages and returns.；Method A is instance method; method B is static.
- 修正建议: Incorporate structural features like control flow graphs or data flow to distinguish trivial I/O patterns from core functionality.；Add attention to function-level context (e.g., method name, class context) to disambiguate similar API usage.；Use contrastive learning to penalize pairs with high API overlap but low semantic similarity.；Enhance training data with more examples of non-clones that share common idioms but differ in goal.

### case_id=3130 FP lexical_or_api_overlap

- 方法: `sendPost` vs `get`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Sends an HTTP POST request with a parameter string and returns the concatenated response body.
- B 摘要: Sends an HTTP GET request with geographic and count headers, decodes response lines into GameRecord objects, and returns an array.
- 静态失败原因: The static model likely overemphasized boilerplate patterns (HttpURLConnection, BufferedReader, while loop) and token overlap, while missing key semantic differences like HTTP method, parameters, and response processing logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels functional similarity, and these functions serve distinct purposes (generic POST vs specific GET for game records), so BCB correctly labels them as non-clones.
- 共享行为: Both use HttpURLConnection for HTTP communication；Both set request properties；Both read the response line by line with BufferedReader；Both handle exceptions
- 行为差异: HTTP method: POST vs GET；Parameters: single string vs lat/lon/count；Response processing: concatenate all lines vs filter and decode lines into objects；Return type: String vs GameRecord[]
- 修正建议: Add explicit detection of HTTP method (POST vs GET)；Analyze data dependencies to distinguish writing to output stream vs not；Compare result types and processing logic beyond surface tokens；Incorporate method name and parameter types as distinguishing features

### case_id=3131 FN partial_functionality

- 方法: `getHTML` vs `getNetworkServersIPs`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches HTML content from a URL, optionally writes it to a file, and returns the HTML string.
- B 摘要: Fetches a list of server IPs from a network address file by parsing lines after the '!SERVERS' marker, returning them as a Vector.
- 静态失败原因: Static BERT models rely heavily on token similarity and syntactic structure; here token Jaccard is only 0.2958, indicating low lexical overlap. The model likely missed the shared high-level pattern of URL reading and line processing, focusing instead on different variable names, method names, and parsing logic. The different return types and method names also contributed to the false negative.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considers these clones because both functions perform URL-based data retrieval and line-by-line reading, sharing a high-level pattern of connecting, reading, and processing input. This partial functionality overlap fits Type-3/Type-4 criteria despite different specific outputs.
- 共享行为: Both open a URL and establish a connection；Both read input line by line using BufferedReader；Both process lines to extract content；Both return a collection of strings (String or Vector<String>)
- 行为差异: getHTML returns the entire HTML content as a single string, while getNetworkServersIPs returns a list of IPs parsed from specific formatted lines；getHTML optionally writes the HTML to a file; getNetworkServersIPs does not；getHTML handles a specific encoding parameter; getNetworkServersIPs does not；getHTML sets a User-Agent header; getNetworkServersIPs does not
- 修正建议: Improve the model's ability to recognize structural patterns like URL connection and line-by-line reading even when variable names and specific processing differ；Incorporate graph-based features to capture control flow and data flow similarities, e.g., try-catch with URL opening, BufferedReader, while loop, and return；Use functional similarity metrics that generalize beyond token overlap

### case_id=3132 FP lexical_or_api_overlap

- 方法: `readReferenceText` vs `checkForUpgrade`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a reference text file from a bundle resource and returns its content as a string.
- B 摘要: Checks for software upgrades by querying a remote server, parsing license and upgrade data, and updating the database and UI accordingly.
- 静态失败原因: The static BERT model likely over-emphasized the lexical overlap of common API calls (URL, BufferedReader, reading lines) and ignored the distinct high-level semantics and contexts (local resource vs. remote upgrade). The token Jaccard similarity is low but the presence of similar code patterns may mislead the model.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels clones based on functional similarity; these two functions have entirely different purposes (file reading vs. upgrade checking) and only share superficial I/O boilerplate, so BCB would likely label them as non-clones.
- 共享行为: Both use URL and BufferedReader to read data line by line；Both build strings by appending lines in a loop；Both handle exceptions
- 行为差异: Function A reads from a local bundle resource; Function B reads from a remote HTTP URL；Function A returns the file content; Function B performs database operations and UI updates；Function B contains complex conditional logic and loops over upgrade records; Function A has a simple linear read
- 修正建议: Incorporate data flow or control flow features to differentiate I/O patterns from business logic；Use more representative training data with diverse functional contexts；Add attention to method names and comments to capture intent

### case_id=3133 FN benchmark_preference_bias

- 方法: `doGet` vs `uncaughtException`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Handles HTTP GET requests to serve a page, with logging and error handling.
- B 摘要: Handles uncaught exceptions in a SWT thread by showing a message box and launching a bug report.
- 静态失败原因: Static model correctly identified them as non-clones due to low lexical overlap and different API usage, aligning with our judgment.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: Likely misannotation; BCB might have considered them both as error-handling routines, but this is too broad.
- 共享行为: Both involve logging errors
- 行为差异: Different functionality: HTTP request handling vs. exception handling；Different APIs: Servlet vs. SWT；Different control flow and logic
- 修正建议: Re-evaluate BCB label for this pair；Use more specific semantic criteria

### case_id=3134 FP lexical_or_api_overlap

- 方法: `handleHandshake` vs `doRawRequest`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Handles Minecraft handshake by validating username and making an HTTP request to authenticate the server session.
- B 摘要: Performs a raw HTTP POST request with given data and returns the response string.
- 静态失败原因: The model likely over-relied on API-level similarities (URL, URLConnection, BufferedReader) and possibly the phrase 'readLine' which appeared in both, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clone because the functions have distinct high-level purposes and are from different domains (Minecraft client vs generic HTTP client), despite sharing some network I/O boilerplate.
- 共享行为: Both use URLConnection to open network connections；Both use BufferedReader and InputStreamReader to read response；Both involve reading lines from an HTTP response
- 行为差异: Function A has authentication logic and side effects (sending packets, shutting down network); Function B returns the response string only；Function A uses GET request to a specific URL; Function B performs POST request to a configurable service URL；Function A handles exceptions internally; Function B declares IOException；Function A writes to an output stream? (No, only reads in A; B writes to output stream)
- 修正建议: Incorporate control flow and data flow analysis to distinguish different intents；Use method name and context embedding to capture purpose beyond lexical tokens；Apply contrastive learning to reduce weight of common API patterns

### case_id=3135 FP lexical_or_api_overlap

- 方法: `doVersionCheck` vs `checkForUpgrade`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Checks jEdit's version by reading a URL and extracting build numbers.
- B 摘要: Performs upgrade check with license validation, database updates, and UI changes.
- 静态失败原因: The model likely overemphasized common lexical elements (URL, BufferedReader, while loop) and missed the vastly different logic and dataflow.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the functions have different purposes and implementations, despite both involving URL reading.
- 共享行为: Both open a URL and read lines of text；Both parse key-value pairs from the response
- 行为差异: A only handles version strings; B handles license, database, and UI；B includes MAC address collection and SQL queries; A does not；B updates UI components based on upgrade availability; A shows wait cursor
- 修正建议: Include more context from the function (e.g., function names, surrounding code)；Increase emphasis on data flow and control flow differences

### case_id=3136 FP lexical_or_api_overlap

- 方法: `encodeFileToFile` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Encodes a file to another file using Base64 encoding.
- B 摘要: Handles GUI action events to set various preferences like paths for external tools and UI settings.
- 静态失败原因: The model likely overemphasized common API tokens like 'FileInputStream', 'FileOutputStream', 'JFileChooser', and try-catch boilerplate, ignoring the overall semantics and control flow differences.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clones because the two methods have entirely different purposes and no functional overlap beyond trivial file I/O patterns.
- 共享行为: Both involve file I/O operations (reading/writing files)
- 行为差异: Function A is a self-contained utility for Base64 encoding of files; Function B is an event handler that updates GUI state and preferences.；Function A uses simple while loop to copy bytes; Function B contains complex conditional logic for different commands and switches look-and-feel.；Function A returns a boolean success flag; Function B is void and interacts with UI components and a controller.
- 修正建议: Improve model sensitivity to overall function purpose by using more discriminative features or context.；Incorporate control flow graph analysis to differentiate simple I/O copy vs. complex event handling.；Augment training data with more examples of GUI event handlers to reduce false positives.

### case_id=3137 FN benchmark_preference_bias

- 方法: `getFile` vs `checkInputStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.0`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies its endpoint, and saves it to a temporary file.
- B 摘要: Reads an InputStream into a byte array and compares it byte-by-byte with an expected array.
- 静态失败原因: Static model likely correctly identified the low lexical overlap and distinct behavior; the BCB label may be an annotation error, so the model did not fail in a semantic sense.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: It is unclear why BCB labeled this as a clone; possibly due to both functions involving I/O stream handling or being part of a larger test harness, but the functionalities are fundamentally different.
- 行为差异: getFile performs file download, XML modification, and file system operations; checkInputStream only reads a stream and compares bytes.；getFile returns a file path string; checkInputStream is void and throws IOException.；getFile handles multiple exception types (MalformedURLException, IOException, etc.) with logging; checkInputStream only throws IOException.
- 修正建议: Verify the BCB annotation for this pair, as it may be a false positive.；If the intent is to detect clones under broad Type-4, consider whether there is any functional equivalence beyond shallow I/O usage.

### case_id=3138 FN partial_functionality

- 方法: `doGet` vs `recurseFiles`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Handles HTTP GET request to retrieve and display a page with permission checks, logging, and caching.
- B 摘要: Recursively traverses a directory tree and adds non-zip files to a zip archive output stream.
- 静态失败原因: Static BERT models rely on lexical and syntactic similarities, which are low here (Jaccard 0.067). They fail to capture the high-level abstract I/O pipeline that BCB annotators considered as semantic clone.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label them as clones under Type-4 semantic similarity because both functions perform a 'read-process-write' pattern with conditional logic and error handling, even though the specific domains and APIs differ.
- 共享行为: Both perform I/O operations: reading from a source and writing to an output stream.；Both include exception handling and conditional checks based on permissions or file properties.
- 行为差异: A handles HTTP request/response; B handles file system recursion.；A uses servlet API and web application context; B uses file I/O and zip streams.；A has extensive logging and caching; B is simpler and focuses on archive creation.
- 修正建议: Enhance model with data flow analysis to identify abstract I/O chains.；Use code summarization to capture intent.；Incorporate API-level similarity for common I/O patterns.

### case_id=3139 FP lexical_or_api_overlap

- 方法: `readUNI` vs `handledRun`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a tab-separated file from a URL and extracts id and description pairs into a vector.
- B 摘要: Downloads an XML game data file from a URL and updates local file if version is newer.
- 静态失败原因: The static model may have been confused by the common pattern of URL opening, stream reading, and try-catch-finally, leading to feature overlap.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels as non-clone because the core functionality (parsing vs downloading) is different; superficial URL-reading boilerplate does not constitute clone under BCB guidelines.
- 共享行为: Both open a URL connection and read data from the stream；Both use try-catch-finally with stream closing
- 行为差异: readUNI parses tab-separated lines into descriptions; handledRun downloads entire XML file and writes to disk；handledRun has version checking and file creation logic not present in readUNI；Exception handling differs: readUNI silently catches MalformedURLException, handledRun logs and shows dialogs
- 修正建议: Include more context about the overall purpose of the functions；Use data flow analysis to differentiate between reading for extraction vs downloading for file storage；Focus on functional signatures and output usage rather than just API calls

### case_id=3140 FP lexical_or_api_overlap

- 方法: `main` vs `downLoadZippedFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Generates adapter classes from Prolog files and writes them to a JAR.
- B 摘要: Downloads a zipped file from a URL and unzips it to a local directory.
- 静态失败原因: Likely due to lexical overlap in common Java library calls (File, URL, streams) and similar exception handling structure, misleading the model into false similarity.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB requires substantial behavioral overlap; these functions share only trivial API usage, not core functionality.
- 共享行为: Both use File and URL operations.；Both handle IO exceptions.
- 行为差异: Function A reads local files and generates code; Function B downloads from network.；Function A writes to JAR; Function B extracts ZIP to directory.；Different method signatures and purposes.
- 修正建议: Incorporate data-flow analysis to distinguish local file processing from network downloads.；Add features capturing high-level purpose or method name semantics.

### case_id=3141 FP lexical_or_api_overlap

- 方法: `readTwitterFead` vs `getJSONData`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Hardcoded HTTP GET to fetch Twitter timeline as raw string.
- B 摘要: Generic HTTP GET to fetch JSON data from given URL, parsing it into JSONObject.
- 静态失败原因: Static BERT models may over-rely on lexical and API overlap (HttpClient, HttpGet, BufferedReader, while-loop pattern) and miss semantic differences in purpose, parameterization, and return type.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels non-clone when functions differ in core functionality (specific vs generic) and return type, despite similar networking boilerplate.
- 共享行为: Both use HttpClient, HttpGet to perform an HTTP GET request.；Both read the response line by line and append to a StringBuilder.
- 行为差异: Function A has a hardcoded URL; Function B takes a URL parameter.；Function A returns raw String; Function B parses JSON and returns JSONObject.；Function A logs errors; Function B prints stack traces.；Function B has a fixed buffer size (8192) and closes reader; Function A does not.
- 修正建议: Incorporate dataflow or type information to distinguish variable usage.；Train on more diverse examples to avoid boilerplate false positives.；Use contrastive learning with harder negatives that share API calls but differ in intent.

### case_id=3142 FP boilerplate_overlap

- 方法: `actionPerformed` vs `unJarStart`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Handles various action commands in a settings dialog, such as opening file choosers for Graphviz/ImageMagick, and updating UI preferences for appearance and behavior.
- B 摘要: Extracts files from a JAR archive that match a given entry prefix and copies them to a target directory path.
- 静态失败原因: The static model might have been misled by the presence of common Java library classes (File, JFileChooser, JarFile, etc.) and similar error handling patterns (try-catch), but the overall semantics and structure are unrelated. The model may have overgeneralized based on API usage.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would label this as non-clone because the functions perform completely different tasks (UI settings management vs. JAR extraction) with no semantic overlap and low lexical similarity.
- 共享行为: Both involve file system operations and exception handling
- 行为差异: Function a is a UI event handler with multiple conditional branches; function b is a linear extraction routine.；Function a interacts with Swing components and preferences; function b uses JarFile and IOUtils.；Function a has complex logic for updating UI and restarting; function b simply copies files.
- 修正建议: Improve model's ability to distinguish between UI event handlers and utility functions using high-level context, such as class name or method signature.；Incorporate structural information like control flow graphs to capture different intents.

### case_id=3143 FP boilerplate_overlap

- 方法: `handleHandshake` vs `doVersionCheck`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Handles server handshake by validating username and sending login packet.
- B 摘要: Performs version check by reading a version file from URL and comparing builds.
- 静态失败原因: Static model overemphasizes structural similarity (URL, InputStream, BufferedReader) and ignores semantic gap in domain and logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels non-clone due to distinct functionality and low token overlap (0.179), despite shared I/O patterns.
- 共享行为: Open a URL and read lines using BufferedReader；Handle IOException with error reporting
- 行为差异: Different purpose: handshake validation vs version checking；Different validation logic: username parsing vs build version comparison；Different actions: send login packet vs call doVersionCheck with versions
- 修正建议: Incorporate data-flow or control-flow analysis to distinguish different logic；Train with more diverse negative examples to avoid false positives from common library usage

### case_id=3144 FN benchmark_preference_bias

- 方法: `doTransfer` vs `doVersionCheck`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.7`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Acts as an HTTP proxy by forwarding a request to a target URL, copying headers and body.
- B 摘要: Checks for software version by fetching a text file from a URL and parsing build numbers.
- 静态失败原因: Static BERT likely captured the low token overlap and disparate control structures, predictively labeling as non-clone, but BCB's broad Type-4 annotation may have been overlooked due to insufficient training on such vague similarities.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have interpreted both as network I/O functions that open a URL and read data, potentially labeling as Type-4 functional similarity despite different purposes and control flows.
- 共享行为: Both open a URL connection and read input streams；Both handle IOException
- 行为差异: A writes to output streams and sets request properties; B does not；A performs bidirectional data transfer; B reads a single file and extracts version info；A uses HttpURLConnection with request/response; B uses URL.openStream for download；B calls a helper method doVersionCheck with arguments; A does not
- 修正建议: Use more focused function similarity metrics that consider purpose and outcome；Train with fine-grained annotations that distinguish proxy vs. download tasks；Incorporate domain knowledge to avoid over-generalizing network I/O operations

### case_id=3145 FP library_context_missing

- 方法: `main` vs `testTrainingBackprop`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `context_recovery_then_dynamic`；动态可解性: `low`；执行优先级: `low`
- A 摘要: Generates adapter classes from a Prolog file given command-line arguments.
- B 摘要: Tests backpropagation training of a neural network on XOR data.
- 静态失败原因: Static BERT/GraphCodeBERT may have been misled by overlapping vocabulary (e.g., 'File', 'IOException', 'try-catch') and similar structural patterns (loops, conditionals) without understanding the domain-specific semantics of Prolog adapter generation vs. neural network training.
- 静态 case study: 该类错误缺少关键上下文或需要深层语义，纯静态方法不可靠。
- 动态 case study: 动态执行价值较低：样本可能依赖库、框架、网络、GUI、数据库或项目上下文，需要先恢复环境或 mock 依赖。
- BCB 偏好解释: BCB likely considers these non-clones because they have completely different program logic and purpose, despite both being Java methods.
- 行为差异: Function A processes command-line arguments and generates Java bytecode from Prolog, while Function B trains a neural network and asserts error rate.；Function A uses Prolog parser and class file generation; Function B uses Fann library for neural network training.；Function A involves file I/O for reading Prolog and writing JAR; Function B involves file I/O for temporary data file.
- 修正建议: Incorporate API documentation or type-level semantics to distinguish libraries.；Use data flow analysis to capture the actual operations performed.；Expand training data with more diverse non-clone pairs with low similarity.

### case_id=3146 FN benchmark_preference_bias

- 方法: `run` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads all files from a HDFS directory to a local file.
- B 摘要: Configures and launches a NexOpen IDE project, including Maven POM handling and reverse engineering setup.
- 静态失败原因: The static model correctly predicted non-clone; it did not fail. The misclassification arises from a potentially incorrect BCB label.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled as clone due to overlapping low-level file I/O operations, but the overall functionality is entirely different, making it an unlikely clone under typical Type-3/4 criteria.
- 共享行为: Both use IOUtils.copyBytes for I/O operations.；Both read from sources and write to output streams.
- 行为差异: Function A is a simple file downloader; Function B is a complex IDE launch handler.；Function A works solely with Hadoop FileSystem; Function B works with Eclipse workspaces and XML configuration.；Function B performs project checks, XML parsing, and Maven actions, while A does not.
- 修正建议: Re-evaluate the BCB label for this pair as it seems to be a false positive.；Improve dataset curation to avoid such low-similarity false clones.

### case_id=3147 FN benchmark_preference_bias

- 方法: `decodeBody` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Decodes an input stream based on content transfer encoding and copies to a temporary file body.
- B 摘要: Builds a site for editing by processing pages, XML transformations, and file I/O with complex control flow.
- 静态失败原因: Static BERT correctly identified non-clone because of very low lexical similarity (Jaccard=0.0553) and distinct code structures, but BCB's ground truth misled the evaluation.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as a clone due to superficial overlap in I/O stream usage and file copying, despite completely different functionality and context.
- 共享行为: Both methods perform I/O operations using InputStream and OutputStream；Both involve string manipulation and file handling
- 行为差异: decodeBody decodes email body content; buildSiteForEdit builds a website from page definitions；decodeBody is short and focused (10 lines); buildSiteForEdit is long and complex (over 100 lines)；decodeBody returns a body object; buildSiteForEdit returns void and writes files；Different input parameters and exception handling
- 修正建议: Re-label this pair as non-clone in the dataset；Improve annotation guidelines to avoid false positives based on generic I/O patterns

### case_id=3148 FN partial_functionality

- 方法: `doTransfer` vs `getContent`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Forwards an incoming HTTP request to a target URL and sends the response back to the original servlet response.
- B 摘要: Executes an HttpUriRequest using Apache HttpClient and returns the response body as a string.
- 静态失败原因: The low token Jaccard (0.095) and different API packages (javax.servlet vs Apache HttpClient) misled the model into focusing on lexical dissimilarity, while ignoring the high-level semantic similarity of HTTP request/response handling.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels Type-4 clones where functions implement similar high-level HTTP client behavior, even if the surrounding context differs. The core task of executing an HTTP request and reading the response is shared.
- 共享行为: Both perform HTTP requests and read the response body.
- 行为差异: Function A is a servlet proxy that forwards requests and copies headers/body bidirectionally; Function B is a standalone utility that executes a pre-built request and returns a string.；Function A uses HttpURLConnection and servlet APIs; Function B uses Apache HttpClient.；Function A writes to a ServletOutputStream; Function B returns a string.；Function A has complex error handling with multiple streams; Function B is straightforward with a BufferedReader.
- 修正建议: Use data augmentation that pairs functions with similar high-level tasks but different API implementations.；Incorporate API usage context or abstract representations of HTTP operations.；Include examples of Type-4 clones in training data to teach the model to ignore surface differences.

### case_id=3149 FP lexical_or_api_overlap

- 方法: `doPost` vs `perform`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Handles user login by hashing password with MD5, verifying credentials against database, and redirecting based on success.
- B 摘要: Handles concept classification by processing form data, sending XML to a remote service, and forwarding to success or failure page.
- 静态失败原因: The model likely overfocused on superficial API similarities (HttpServletRequest, HttpSession, request.getParameter, response.sendRedirect) and common patterns of web request handlers, ignoring the distinct core logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BigCloneBench generally requires functional similarity beyond common boilerplate; these are different tasks (login vs. classification), so BCB likely labels as non-clone.
- 共享行为: Both are HTTP request handlers that use request parameters and HttpSession.；Both perform conditional branching and redirect/forward responses.
- 行为差异: Authenticates users vs. classifies concepts via remote XML call.；Uses MD5 hashing and database query vs. external URL connection and XML parsing.；Redirects to index or referer with message vs. forwards to Struts action mappings.；Error handling differs: logs NoSuchAlgorithmException vs. logs and sets reporting bean.
- 修正建议: Include structural or dataflow representations to capture semantic differences.；Increase sensitivity to domain-specific function signatures (e.g., doPost vs. perform) and task context.；Use contrastive learning to differentiate functionally similar vs. coincidental API pattern overlap.

### case_id=3150 FP boilerplate_overlap

- 方法: `googleImageSearch` vs `getXML`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches Google image search results for a given artist/album and extracts image URLs into a list.
- B 摘要: Fetches XML from a servlet by URL-encoding a request and returning the response as a string.
- 静态失败原因: The static BERT model likely overfitted to the common boilerplate code (URL opening, BufferedReader, while loop) and ignored the differing core logic and output. The structural similarity in the I/O portion caused a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels non-clones when functions have different purposes and outputs, even if they share common I/O patterns. Here, A performs an image search and parsing, while B retrieves generic XML; thus BCB considers them not clones.
- 共享行为: Both open a URL connection and read the response line by line into a string.；Both use BufferedReader and InputStreamReader for reading.；Both handle general I/O exceptions.
- 行为差异: A is void and populates a global list; B returns the response string.；A includes additional HTML parsing to extract image URLs; B simply returns the raw response.；A uses a hardcoded Google search URL; B uses a parameterized URL.；A sets a User-Agent header; B does not.
- 修正建议: Incorporate data-flow analysis to track how the fetched data is used.；Include method signature information (return type, parameters) in the representation.；Use abstract syntax trees to distinguish core logic from boilerplate.

### case_id=3151 FP lexical_or_api_overlap

- 方法: `get` vs `createHTML`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches game records from a remote HTTP server using custom headers and returns an array of GameRecord objects.
- B 摘要: Generates HTML for a dashboard page by reading a CSS file and querying a database to dynamically build content.
- 静态失败原因: The model likely overemphasized the lexical and structural similarity of the common I/O pattern (opening a URL, reading with BufferedReader, while readLine) and ignored the completely different data usage and return types.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels non-clones for functions with completely different purposes and only boilerplate overlap; these functions have no shared domain or data transformation logic.
- 共享行为: Both open an input stream and read lines using BufferedReader；Both handle IOException with logging or printing；Both use conditional logic (if/switch) to control flow
- 行为差异: A performs network I/O to retrieve data; B reads from local file and queries a database；A returns an array of custom objects (GameRecord); B returns an HTML string；A uses specific headers for location; B uses an enum to decide page type；A builds a list and converts to array; B concatenates strings to build HTML
- 修正建议: Use type information and method signatures more strongly to distinguish return types；Incorporate data flow analysis to track how read data is used (network response vs local file vs DB query)；Add attention to domain-specific constants and method names

### case_id=3152 FP boilerplate_overlap

- 方法: `getUser` vs `load`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Retrieves a user by login using DAO and fallback to parsing users.cfg file.
- B 摘要: Downloads an XML string from a pastebin URL using an ID.
- 静态失败原因: Overemphasized shared structural patterns (URL, BufferedReader) while ignoring semantic context and domain differences.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels as non-clone due to entirely different functionality and low token overlap.
- 共享行为: Reads line by line from a URL stream using BufferedReader and InputStreamReader
- 行为差异: Different domains: user model vs XML string；A parses local config file, B downloads remote resource；A uses StringTokenizer and DB save, B handles HTTP connection and sets static flags；A returns User or null, B returns String
- 修正建议: Train with more diverse non-clone pairs sharing common API calls but different semantics；Incorporate dataflow or type information to distinguish；Use contrastive learning with hard negatives

### case_id=3153 FN benchmark_preference_bias

- 方法: `doTransfer` vs `init`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.8`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Performs HTTP request forwarding by creating a new connection to a target URL, copying request headers and body, and returning the response.
- B 摘要: Loads controller classes from a registry file by reading URLs from classpath and instantiating each class.
- 静态失败原因: Static BERT correctly identified non-clone due to low token overlap and different APIs, so it did not fail; the BCB label is questionable.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might consider both as 'reading from a URL and processing input', sharing the same high-level pattern of reading from an InputStream and handling exceptions, thus broad Type-3/Type-4 clone.
- 共享行为: Both read from an InputStream obtained from a URL；Both use loops to process data；Both handle IOException
- 行为差异: A forwards HTTP requests; B loads classes for registration；A writes HTTP output; B reads configuration lines；A uses HttpURLConnection; B uses classLoader.getResources
- 修正建议: Re-evaluate BCB annotation for this pair considering functional orthogonality；Use more fine-grained clone categories to distinguish forwarding from configuration loading

### case_id=3154 FP long_range_semantics

- 方法: `readData` vs `copy`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `static_summary_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Reads configuration data from global strings and a file, populating various sets and maps for Tibetan transliteration.
- B 摘要: Recursively copies a file or directory using NIO FileChannel and MappedByteBuffer.
- 静态失败原因: Model likely focused on superficial commonalities (e.g., both have try-catch blocks, loops, and use classes like HashSet or FileChannel) while missing the distinct high-level purposes due to long and complex code.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB would label these as non-clones because they perform entirely different tasks with no overlapping functionality or similar logic.
- 行为差异: Function A parses configuration data; Function B copies files.；Function A uses StringTokenizer to tokenize strings; Function B uses FileChannels.；Function A populates data structures; Function B creates directories and copies bytes.；Function A is private and takes no parameters; Function B is public and takes two File parameters.
- 修正建议: Train with more diverse non-clone pairs that share structural patterns but differ in intent.；Incorporate control-flow and data-flow analysis to capture functional semantics.；Use execution traces or abstract interpretation to understand actual behavior.

### case_id=3155 FP lexical_or_api_overlap

- 方法: `googleImageSearch` vs `doVersionCheck`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Performs a Google image search based on the current track and album, collecting image URLs.
- B 摘要: Checks for new versions of jEdit by reading build numbers from a version-check URL.
- 静态失败原因: Static BERT/GraphCodeBERT may have been misled by the lexical and structural similarities (URL opening, while loop with readLine) and overlooked the domain-specific differences in parsing and purpose.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels as non-clone because the functions serve completely different application purposes despite sharing a common boilerplate pattern of reading from a URL.
- 共享行为: Open a URL and establish an HTTP connection；Read input line by line using BufferedReader；Parse each line for specific patterns；Handle exceptions generically
- 行为差异: Different URL construction (hardcoded vs property-based)；Different parsing logic (image URLs vs build numbers)；Different output (store in list vs invoke another method)；Different usage of result (UI dialog vs image collection)
- 修正建议: Incorporate finer-grained semantic representations that capture the intent of the code beyond API usage；Use contrastive learning with hard negative pairs that share API patterns but differ in objective；Add task-specific features or pre-training objectives that emphasize functionality over boilerplate

### case_id=3156 FP boilerplate_overlap

- 方法: `loadSourceCode` vs `get`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Loads a source file from the classpath, applies syntax highlighting, and returns it as HTML.
- B 摘要: Makes an HTTP GET request to retrieve game records based on location and count, filtering and decoding lines.
- 静态失败原因: Static BERT likely overemphasized the shared boilerplate (BufferedReader, readLine, exception handling) and ignored the distinct API calls and data transformations.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labeled non-clone because the functions serve completely different purposes despite sharing common I/O boilerplate.
- 共享行为: Reads text line by line using BufferedReader；Handles exceptions
- 行为差异: Data source: local classpath resource vs. HTTP URL；Line processing: syntax highlighting vs. filtering/decoding；Output: HTML string vs. GameRecord array；Error handling: sets field vs. prints stack trace and returns null
- 修正建议: Use flow-aware matching that focuses on API calls and data flow；Incorporate domain knowledge to distinguish generic I/O from specific behavior；Train on more diverse pairs to avoid overfitting to common patterns

### case_id=3157 FN partial_functionality

- 方法: `copyResource` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource (URL or file path) to a destination file using byte-by-byte I/O.
- B 摘要: Copies a source file to a destination file using NIO FileChannel transferTo.
- 静态失败原因: Low token Jaccard (0.22) and different API choices (InputStream vs FileChannel) mislead models that rely on surface-level similarity, missing the shared core functionality.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB considers functional similarity for file-copy operations, accepting variations in API and source type as Type-3/4 clones.
- 共享行为: Both copy data from a source to a destination file；Both handle exceptions；Both close the underlying I/O resources
- 行为差异: Function A supports URL and file sources; Function B only files；Function A uses InputStream/OutputStream byte-by-byte; Function B uses FileChannel transferTo；Function A throws Exception if source not found; Function B relies on FileNotFoundException
- 修正建议: Incorporate dataflow or program dependence graphs to capture data movement；Train on I/O operation variations with API mapping；Use contrastive learning on functionally similar but syntactically different pairs

### case_id=3158 FP lexical_or_api_overlap

- 方法: `gerarTutorialPage` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Generates a tutorial web page by creating directory structure, copying CSS files, and writing HTML; returns boolean success.
- B 摘要: Handles action events to set user preferences for file paths (e.g., GRAPHVIZ, IMAGEMAGICK) and UI settings; interacts with dialogs and preferences.
- 静态失败原因: Static BERT model likely overfitted on common API tokens (File, JOptionPane, try-catch) and the presence of exception handling patterns, ignoring the broader semantic context and control flow differences.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clone because the functions have completely different purposes (site generation vs UI event handling) and only superficial API overlap; partial functionality similarity is absent.
- 共享行为: Both use File and JOptionPane classes；Both have try-catch for exception handling；Both involve some form of file path handling (A: copying files, B: selecting file paths)
- 行为差异: A creates directories and copies multiple CSS files; B merely reads selected file paths；A writes HTML content; B updates UI components and preferences；A is a standalone generation method; B is an event handler responding to user actions；A returns boolean; B returns void
- 修正建议: Enhance model with control-flow or data-flow features to distinguish core behavior；Use more sophisticated AST or graph-based embeddings that capture method purpose；Increase training diversity with examples that have API overlap but different semantics

### case_id=3159 FN lexical_or_api_overlap

- 方法: `decodeFileToFile` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Decodes a Base64-encoded file and writes the decoded content to another file, returning success status.
- B 摘要: Builds a website for editing by processing XML templates, reading control files, and writing rendered pages to output files.
- 静态失败原因: Static BERT models rely on token overlap and syntactic patterns; both codes share many I/O-related tokens (InputStream, FileInputStream, read, write, buffer, finally) leading to high similarity, but the overall goal and context differ, causing false negative classification due to lexical/API overlap without capturing semantic intent.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may label this as a clone because both functions involve common file I/O boilerplate (open streams, read/write loop, close) and are classified as 'Utility' or 'File I/O' operations, which are often considered functionally similar under broad Type-3/Type-4 criteria.
- 共享行为: Read from an input stream and write to an output stream using a buffer loop；Handle IOExceptions and close streams in finally blocks；Use FileInputStream and FileOutputStream (or similar) for file I/O
- 行为差异: A is a simple decoding utility; B is a complex site builder with many parameters and transformations；A returns a boolean; B has a void return and throws multiple checked exceptions；B does XML processing, transformer usage, and file system operations beyond simple copy
- 修正建议: Incorporate dataflow or control-flow analysis to distinguish simple utility from complex application logic；Use graph-based representations (e.g., AST or CFG with node types) to capture structural differences；Train with more diverse examples of non-clones that share API usage but have different purposes

### case_id=3160 FP lexical_or_api_overlap

- 方法: `readTwitterFead` vs `loadMFileViaWeb`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a Twitter user timeline JSON from a fixed URL using HttpClient and returns the raw JSON string.
- B 摘要: Loads a MATLAB m-file from a given URL using URL.openStream, parses it into a UserFunction object, and returns it.
- 静态失败原因: The model likely over-weighted the common code patterns (BufferedReader, InputStreamReader, while loop, try-catch) that appear in both functions, leading to a false positive. It failed to recognize the semantic differences in the HTTP request specifics and the different post-processing of the fetched content.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels as non-clones because despite the common I/O boilerplate, the core functionality (what is done with the fetched data) is completely different, and the overall purpose differs significantly.
- 共享行为: Both fetch data from a URL via HTTP.；Both use BufferedReader and InputStreamReader to read lines.；Both build a string from the lines (with slight variations).
- 行为差异: Function A uses Apache HttpClient with explicit HTTP GET; Function B uses URL.openStream.；Function A returns the raw string (JSON); Function B parses the string into a UserFunction object.；Function A checks HTTP status code 200; Function B does not check HTTP status (relies on exception).；Function A appends lines directly; Function B appends lines with newline characters.
- 修正建议: Incorporate data flow analysis to track how the fetched data is used (e.g., returned vs. parsed).；Use attention mechanisms that can distinguish between boilerplate and task-specific code.；Include more granular API usage context (e.g., HttpClient vs. URL.openStream).；Add control flow features to capture conditional checks (HTTP status code).

### case_id=3161 FP lexical_or_api_overlap

- 方法: `actionPerformed` vs `buildDeb`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Handles GUI action events to set various application preferences and settings.
- B 摘要: Builds a Debian package file by writing archive entries from control and data files.
- 静态失败原因: The model likely overgeneralized from overlapping low-level I/O patterns (stream reading/writing) and boilerplate code, missing the distinct high-level purposes.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB considers these non-clones because they perform completely different tasks with no shared functionality beyond superficial I/O APIs.
- 共享行为: Both use File and streams for I/O operations
- 行为差异: Different purpose: event handling vs. package building；Different control flow and data manipulation；Different inputs and outputs
- 修正建议: Train on more diverse examples to distinguish boilerplate from core logic；Incorporate structural or semantic matching to capture overall function purpose

### case_id=3162 FN partial_functionality

- 方法: `main` vs `createJAR`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a URL and extracts its zip entries to the current directory.
- B 摘要: Creates a JAR file by copying a resource jar or creates a directory, then writes a serialized document object to a file.
- 静态失败原因: Low token overlap (0.155) and different syntactic structure; static BERT models rely on surface forms and may miss high-level functional similarity due to distinct APIs and control flow.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as 'copying data from an input stream to output files' under a broad functional category, despite different specifics.
- 共享行为: Both involve file I/O, use FileOutputStream, and write data to files.
- 行为差异: Different input sources (URL vs resource jar)；Different output purposes (zip extraction vs jar creation and serialization)；Different method signatures and control flow
- 修正建议: Enhance model with functional taxonomy or data flow analysis；Incorporate knowledge of input-output patterns and stream operations

### case_id=3163 FN boilerplate_overlap

- 方法: `readGeoParserResult` vs `CheckUrl`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a record content, sends it to a geo-parser service via an XML request, and extracts place names and gazetteer IDs from the response with retries.
- B 摘要: Takes a URL, performs an HTTP GET request, and returns the first line of the response as a string.
- 静态失败原因: Static BERT models rely on token overlap and structural similarity; low Jaccard (0.10) and distinct control flows (A has loops, retries, XML parsing) led to low predicted similarity. The model failed to recognize the faint behavioral overlap of URL reading.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may have labeled them as clones due to both involving network I/O (reading from a URL) and exception handling, considering broad Type-4 similarity for 'functions that fetch data from a URL'.
- 共享行为: Both open a URL connection to retrieve data；Both use BufferedReader and InputStreamReader to read the response；Both handle exceptions by printing error information
- 行为差异: A constructs an XML payload and parses XML response; B does not use XML；A has retry logic for failures; B does not；A returns a collection of tuples; B returns a single string；A iterates through multiple elements; B reads only the first line
- 修正建议: Use a more context-aware representation that captures high-level intent (e.g., retrieving data from a URL) rather than syntax.；Incorporate functional type information (e.g., signature similarity, I/O behavior).；Train with more examples of broad semantic clones.

### case_id=3164 FP lexical_or_api_overlap

- 方法: `main` vs `copy`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: A main method that parses a Prolog file, generates adapter classes and resources, and writes them to a JAR file.
- B 摘要: A static method that copies a file using NIO FileChannels with proper null checks and resource cleanup.
- 静态失败原因: The model likely relied on lexical overlap of common Java I/O APIs (File, IOException, try-catch, close) and the presence of a main method, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the functions have very low syntactic overlap and serve completely different purposes; the shared file I/O is too generic to indicate a true clone.
- 共享行为: Both perform file I/O operations；Both handle exceptions with try-catch blocks
- 行为差异: Function A is a complex code generation pipeline involving parsing, class loading, and writing multiple resources；Function B is a simple file copy utility using NIO channels；Function A has command-line argument parsing and conditional debug output；Function B only copies a single file
- 修正建议: Incorporate structural information like control flow and data dependencies；Use more fine-grained token embeddings that capture semantic differences；Add a threshold for code length or complexity differences

### case_id=3165 FN partial_functionality

- 方法: `getContent` vs `fileDownload`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Gets HTTP response content as a string using HttpClient.
- B 摘要: Downloads a file from a URL to a local directory using URLConnection.
- 静态失败原因: Low token Jaccard (0.1279) and different method signatures caused the model to miss the high-level semantic similarity of reading HTTP response data.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considers both as 'download web content' tasks, focusing on the common pattern of reading HTTP responses rather than the specific output.
- 共享行为: Both perform HTTP requests and read response data.
- 行为差异: A uses HttpClient, B uses URLConnection.；A returns a string, B writes to a file.；A reads lines, B reads characters.；A throws exceptions, B catches and logs.
- 修正建议: Incorporate abstract API call patterns (e.g., open connection, read input).；Use dataflow analysis to detect similar I/O operations.；Enhance training with more diverse Type-3/Type-4 examples.

### case_id=3166 FN benchmark_preference_bias

- 方法: `downloadFile` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Downloads a file from S3, decrypts and decompresses it, and saves it to a local target file with error handling and stream cleanup.
- B 摘要: Builds a site for editing by iterating over pages, reading XML, performing XSLT transformations, string replacements, and writing output files, with extensive error handling and debugging.
- 静态失败原因: Static BERT methods like CodeBERT rely on token-level embeddings and may not capture the deep semantic difference, but here the prediction 0 was correct; the BCB label is likely an annotation error.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might have labeled as clone due to the presence of similar boilerplate code patterns (e.g., stream handling, file copying) and error handling structure, despite vastly different overall functionality.
- 共享行为: Both involve file I/O operations (reading input streams, writing output files)；Both use temporary files or output paths；Both handle exceptions and close streams explicitly
- 行为差异: Function A is a simple download with decryption/decompression；Function B is a complex site builder with XML transformations, property handling, and looping over multiple pages；Function A deals with a single file; Function B deals with multiple files and page objects；Function A uses S3 and cryptography; Function B uses local files, FTP, and DOM
- 修正建议: Review BCB annotation guidelines to avoid false positives from boilerplate similarity；Improve dataset consistency by removing pairs with only superficial commonality

### case_id=3167 FN benchmark_preference_bias

- 方法: `copyFile` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.75`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Copies a file from source to destination using FileChannel.
- B 摘要: Builds an editable HTML site by reading XML, transforming it, and writing output files.
- 静态失败原因: Static BERT did not fail; it correctly predicted non-clone (0) due to low lexical overlap and distinct contexts. The error is a BCB false positive (FN in static prediction).
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB likely mislabeled due to both functions performing file I/O operations, but the overall functionality is vastly different; this may be a Type-4 false positive.
- 行为差异: Function A is a simple file copy using NIO channels.；Function B is a complex multi-step site generation process involving XML parsing, XSLT transformation, and file writing.；Function B has numerous parameters and extensive debugging code.；Function A throws a RuntimeException on IOException, while B declares multiple checked exceptions.
- 修正建议: Improve BCB annotation consistency to avoid labeling functionally unrelated methods as clones.；Use more discriminative clone detection thresholds that consider semantic equivalence over shared low-level operations.

### case_id=3168 FN partial_functionality

- 方法: `getFile` vs `writeData`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies its soap:address endpoint, saves to temp directory, and returns the file path.
- B 摘要: Writes tab-separated data including timestamps and peak values to a text file.
- 静态失败原因: The static model correctly identified low lexical and structural similarity (token Jaccard 0.11), but BCB's lenient criteria allowed this pair as a clone; the model failed to match BCB's expectation because it does not recognize high-level I/O similarity as sufficient for cloning.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled these as clones due to a broad notion of 'file writing' functionality, considering both as I/O operations, despite vastly different specific tasks.
- 共享行为: Both functions perform file I/O (creating/writing to files).
- 行为差异: getFile downloads remote content; writeData writes locally generated data.；getFile reads and parses XML; writeData formats numerical data into tabs.；getFile returns a String path; writeData returns void.；getFile involves network I/O and error handling for network exceptions; writeData does not.
- 修正建议: Incorporate high-level I/O operation awareness into the model while ensuring distinct workflows are separable.；Use clone type definitions aligned with BCB's annotation guidelines to reduce benchmark bias.；Add training examples that explicitly distinguish between different file-handling tasks.

### case_id=3169 FN boilerplate_overlap

- 方法: `doRawRequest` vs `runInternal`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Makes an HTTP POST request with given data and returns the response body as a string.
- B 摘要: Downloads or parses OPDS catalog pages via HTTP GET, handling redirects, timeouts, errors, and progress updates in a loop.
- 静态失败原因: Static BERT/GraphCodeBERT models may have been misled by overlapping API calls (URLConnection, openConnection, getInputStream) and boilerplate code, while failing to capture the contrasting control flow and overall semantics due to low token overlap and long code length.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB might have considered both as performing HTTP request-response with URLConnection, possibly focusing on the common pattern of opening a connection and reading input, but overlooked the significant differences in method, complexity, and purpose.
- 共享行为: Both use URLConnection to make HTTP requests.；Both handle input/output streams.；Both set some connection properties.
- 行为差异: A uses POST with data in body, B uses GET without request body.；A is a simple synchronous request, B is complex with multiple connections, pagination, and error handling.；B includes progress reporting, file download, and callback invocation; A does not.；B handles response codes, content-disposition, and content encoding; A does not.
- 修正建议: Incorporate dataflow or control flow analysis to differentiate simple from complex HTTP interactions.；Use models that capture higher-level program structure beyond token sequences.

### case_id=3170 FP long_range_semantics

- 方法: `write` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `static_summary_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Writes a JAR file by copying entries from included JARs, excluding manifest and zero-size entries.
- B 摘要: Handles UI action commands (e.g., GRAPHVIZ, IMAGEMAGICK) by opening file choosers and updating preferences.
- 静态失败原因: The low token Jaccard (0.060) suggests the model might have relied on superficial structural patterns (e.g., similar control flow or common API names like 'Jar' vs 'File') or was confused by the truncation in code_b, leading to a false positive.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB annotations typically require significant behavioral overlap or shared functionality; these two functions have no common purpose, so they are correctly marked as non-clones even under broad Type-4 criteria.
- 行为差异: Function A performs file I/O for JAR creation; Function B handles GUI events and preference storage.；Function A uses JarOutputStream and InputStream; Function B uses JFileChooser and UI components.；Function A iterates over JAR entries; Function B responds to action commands with conditional branches.；Function A has no user interaction; Function B shows dialogs and updates UI elements.
- 修正建议: Improve model's ability to capture global program semantics beyond local token overlap.；Use contrastive learning with hard negatives to better distinguish unrelated functions.；Incorporate structural features like control flow graphs or data dependencies.

### case_id=3171 FN partial_functionality

- 方法: `getJSONData` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Retrieves JSON data from a given URL via HTTP GET and returns it as a JSONObject.
- B 摘要: Sends a POST request to the RenRen API with pre-defined parameters and prints the response.
- 静态失败原因: Low lexical overlap (Jaccard 0.12) and different method names/APIs (HttpClient vs HttpURLConnection) misled the static model; it did not capture the abstract similarity of 'HTTP networking'.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider them clones because both involve the high-level pattern of sending an HTTP request and processing the response, sharing structural elements like URL handling and BufferedReader, despite different APIs and purposes.
- 共享行为: Both perform HTTP requests to fetch data from a URL；Both read the response content as string using BufferedReader
- 行为差异: A uses HttpClient with GET; B uses HttpURLConnection with POST；A parses JSON response; B prints raw response lines；A returns a JSONObject; B returns void；A is a reusable utility; B is a specific main method with hardcoded parameters
- 修正建议: Use a model that understands high-level API semantics (e.g., all HTTP requests are similar)；Incorporate control-flow and data-flow graphs to capture structural patterns；Add function-level comments or method name embeddings to bridge semantic gaps

### case_id=3172 FP lexical_or_api_overlap

- 方法: `sendPost` vs `getTicketsForQueue`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Sends an HTTP POST request with given parameters and returns the response body as a string.
- B 摘要: Retrieves tickets from a queue by performing an HTTP GET request, parsing ticket IDs, and fetching each ticket's details.
- 静态失败原因: The static model likely overemphasized common tokens (e.g., 'BufferedReader', 'line', 'try', 'catch') and the general structure of HTTP request handling, ignoring the distinct functional goals, data flow, and API differences.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clones based on functional dissimilarity. Despite both using HTTP, the purposes are entirely different: one is a generic POST helper, the other is a specific ticket query with subsequent data processing, so BCB correctly marks them as non-clones.
- 共享行为: Both functions make HTTP requests (POST vs GET) and read the response line by line using BufferedReader.
- 行为差异: Function A is a generic HTTP POST utility; Function B is a domain-specific GET query for ticket IDs and then retrieves individual tickets.；Function A returns the raw response string; Function B returns a list of RTTicket objects after processing.；Function B includes error handling that returns null for specific responses (e.g., 'does not exist') and throws custom exceptions.；Function A uses HttpURLConnection; Function B uses Apache HttpClient (HttpGet, HttpResponse).
- 修正建议: Incorporate structural or dependency-graph features that capture the overarching intent (e.g., method name, return type).；Train with contrastive examples of similar HTTP setups but different business logic.；Use code summarization or name embeddings (e.g., method name 'sendPost' vs 'getTicketsForQueue') to disambiguate.

### case_id=3173 FN benchmark_preference_bias

- 方法: `doGet` vs `copyFileTo`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: HTTP servlet doGet method that retrieves a page, checks permissions, and optionally writes a cached HTML file.
- B 摘要: Private method that copies the current file to a destination using FileChannel.
- 静态失败原因: The static model correctly predicted non-clone (0), so it did not fail; the BCB annotation appears to be a false positive.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled them as clones due to superficial similarity in file I/O and logging, considering them Type-4 (functionally similar) even though the overall logic differs.
- 共享行为: Both perform file I/O operations (writing/copying).
- 行为差异: Function A handles HTTP requests, session management, and page rendering; Function B only copies a file.；Function A writes HTML content to a temporary file conditionally; Function B copies a binary file unconditionally.；Function A uses logging and exception handling for web context; Function B uses logging for file operations.；Function A involves property lookups and user permission checks; Function B does not.
- 修正建议: Re-evaluate the BCB annotation for this pair.；Consider removing or correcting the clone label due to lack of semantic or functional similarity.

### case_id=3174 FP boilerplate_overlap

- 方法: `genRandomGUID` vs `perform`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Generates a random GUID by computing MD5 hash of current time and random number.
- B 摘要: Processes an HTTP request to classify a concept and returns an ActionForward.
- 静态失败原因: The static BERT model likely overfitted to common Java boilerplate patterns (e.g., StringBuffer, try-catch, loops) present in both functions, neglecting the distinct semantics. Low token Jaccard (0.095) suggests the false positive arises from structural rather than lexical similarity.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels as non-clone because the two functions have entirely different purposes (GUID generation vs. web request processing) and no meaningful functional overlap, even under broad Type-4 criteria.
- 共享行为: Both use StringBuffer for string concatenation；Both use try-catch blocks for exception handling；Both iterate over arrays using loops
- 行为差异: Function a generates a cryptographic hash for a GUID; function b performs web request handling and parsing；Function a has no input-output network communication; function b sends HTTP POST and reads response；Function a returns a String; function b returns an ActionForward object；Function a uses MessageDigest and MD5; function b uses URLConnection, BufferedReader, and XML parsing
- 修正建议: Use dataflow-sensitive models that track how variables are used across operations；Include contrastive training examples with similar boilerplate but different semantics；Add task-specific pre-training on API usage patterns

### case_id=3175 FP long_range_semantics

- 方法: `actionPerformed` vs `save`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `static_summary_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Handles action events for various settings commands, updating UI components and saving preferences.
- B 摘要: Writes a byte array to a file using streams and closes resources.
- 静态失败原因: The static model may have been misled by common Java patterns like file I/O or actionPerformed naming, or it may have overgeneralized from partial token overlap (e.g., both use File). The model might not capture the full context of the long method in code A.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB would not treat these as clones because they have completely different purposes and functionality. Code A is a long UI event handler for preferences, Code B is a file save utility. There is no meaningful semantic similarity.
- 共享行为: Both involve file operations in some way.
- 行为差异: Code A is UI event-driven with many conditional branches for different preferences; Code B is a static utility that simply writes bytes to a file.；Code A uses JFileChooser and preferences; Code B uses byte array and FileOutputStream.；Code A has side effects on UI; Code B has no UI interaction.
- 修正建议: Improve model to capture long-range dependencies and global method purpose.；Use graph-based representations that condense high-level semantics.；Add negative sampling of similar-looking but functionally different code.

### case_id=3176 FP lexical_or_api_overlap

- 方法: `getContent` vs `getFullScreenUrl`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Makes an HTTP request and returns the entire response body as a string.
- B 摘要: Fetches a YouTube page, parses it to extract video_id and t, then constructs and returns a fullscreen video URL.
- 静态失败原因: The static BERT model likely over-relied on lexical and API overlap (HttpURLConnection, BufferedReader, readLine) and the general 'read from URL' pattern, ignoring the distinct intents.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB considers semantic equivalence; these two functions serve different purposes (generic content retrieval vs. specific URL extraction), so they are not clones.
- 共享行为: Both read data from a URL using Java I/O (BufferedReader, InputStreamReader).；Both return a string derived from the HTTP response.
- 行为差异: A uses Apache HttpClient; B uses URLConnection.；A reads all lines and appends to a buffer; B searches for a specific line containing 'fullscreenUrl' and then parses parameters.；A is generic; B is specific to YouTube video page extraction.；B modifies UI (progressDown) and prints debug output; A does not.
- 修正建议: Include more training examples where similar API usage leads to different semantic outcomes.；Incorporate task-level or purpose-aware features (e.g., function name, comments) to distinguish generic HTTP fetching from domain-specific extraction.；Use contrastive learning to differentiate functions that share low-level constructs but differ in high-level purpose.

### case_id=3177 FN benchmark_preference_bias

- 方法: `readData` vs `fetchUrl`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.1`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Parses multiple comma-separated string fields and a configuration file to populate character sets and mappings for Tibetan/Sanskrit text processing.
- B 摘要: Fetches the content of a URL as a string, handling malformed URL and IO exceptions.
- 静态失败原因: The model likely relied on token overlap, which is low, leading to a non-clone prediction, while the BCB label may reflect an over-generalized similarity.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB likely labels this as a clone due to a very broad interpretation of 'reading data', but the functions have minimal functional similarity.
- 共享行为: Both are static methods；Both read data from a source；Both involve looping through tokens or lines；Both catch IOException
- 行为差异: Different input sources (string fields vs URL)；Different output (void vs String)；Different data structures manipulated；Different complexity and purpose
- 修正建议: Re-evaluate BCB annotation for consistency；Incorporate method purpose understanding via comments or context；Use dataflow analysis to see both functions involve reading and processing input

### case_id=3178 FP boilerplate_overlap

- 方法: `readData` vs `copyTextFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Reads and parses initialization data from string constants and a file to populate sets and maps.
- B 摘要: Copies a text file from source to destination using buffered streams.
- 静态失败原因: Likely due to superficial lexical overlap from common Java I/O patterns (try-catch, FileInputStream, BufferedReader) causing the model to judge them as clones.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clone because the functions perform completely different tasks despite both using file I/O, which is not sufficient for functional similarity.
- 共享行为: Both involve file I/O operations；Both use try-catch for IOException handling
- 行为差异: A parses structured data and modifies multiple global data structures; B performs binary copy and returns boolean；A is complex and long; B is simple and short
- 修正建议: Train with more diverse examples that emphasize functional logic over boilerplate；Incorporate structural or semantic features beyond token overlap

### case_id=3179 FN partial_functionality

- 方法: `main` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Decompresses a .gz file from command line arguments using GZIPInputStream and copies to a destination file.
- B 摘要: Retrieves a resource as InputStream from a URL, with caching to local file system and conditional fetching.
- 静态失败原因: Static BERT/GraphCodeBERT models rely on token-level similarity and syntactic structure. The low token Jaccard (0.16) and different method names ('main' vs 'getResourceAsStream') likely led to a non-clone prediction. The models may not capture the abstract data flow pattern of stream copying that BCB annotators consider semantically similar.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as clones because they share the core pattern of reading from an input stream and writing to an output stream with buffering, which is a common I/O transformation task. The high-level functionality of copying data from one source to another, along with similar error handling, could be seen as type 4 clone (similar semantics despite different contexts).
- 共享行为: Both use InputStream and OutputStream for reading/writing data；Both copy data in a loop using a buffer；Both have try-catch-finally blocks for resource management and exception handling；Both close streams in finally blocks
- 行为差异: A is a main method for gzip decompression; B is a method for resource retrieval with caching；A uses GZIPInputStream; B uses URLConnection and handles HTTP responses；B has cache logic (checking last modified, caching to file); A has no caching；B prints debug information; A only prints error messages
- 修正建议: Incorporate control flow graph (CFG) similarity focusing on I/O patterns；Use data flow analysis to identify stream copy operations；Add training examples that pair functions with different high-level tasks but similar core I/O transformation logic

### case_id=3180 FN benchmark_preference_bias

- 方法: `doGet` vs `parse`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.2`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Handles HTTP GET request to retrieve a page, check visibility, log and cache the response.
- B 摘要: Parses an InputStream using Tika, optionally saving to file or delegating.
- 静态失败原因: The low token Jaccard similarity (0.056) and lack of shared vocabulary/logic made it easy for the static model to correctly classify them as non-clones, so the model did not fail; rather, the BCB label is likely incorrect.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled these as clones due to a very broad interpretation of 'data processing' or a benchmark annotation error, as the functions share no meaningful partial functionality.
- 共享行为: Both methods involve conditional processing based on input parameters or metadata.
- 行为差异: Different domains (web vs. document parsing)；Different input/output types (HttpServletRequest vs. InputStream, HttpServletResponse vs. ContentHandler)；Different operations and libraries used
- 修正建议: Re-evaluate the BCB annotation for consistency.；Consider adding more context or domain-specific rules.；Improve the benchmark to avoid overly broad clone labels.

### case_id=3181 FN benchmark_preference_bias

- 方法: `copy` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Recursively copies a file or directory from a Hadoop FileSystem to a local destination, optionally deleting the source after copying.
- B 摘要: Downloads a KMZ (zip) file from a URL and extracts its entries to the current directory.
- 静态失败原因: The static model (e.g., CodeBERT) likely recognized the low token overlap (Jaccard 0.12) and dissimilar syntactic structure (recursive directory handling vs. sequential zip extraction), correctly identifying them as non-clones. The false negative arises from the BCB label being overly broad.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might label this as a clone due to the broad shared pattern of reading bytes from an input source and writing to a file, considering both as 'copy' operations at a high level, despite different contexts and intents.
- 共享行为: Reads from an input stream and writes to an output stream；Involves file I/O operations；May create new files on the local filesystem
- 行为差异: A operates on Hadoop FileSystem, B on a URL；A recursively copies directories, B extracts a flat zip (no subdirectories)；A optionally deletes the source, B does not；A uses IOUtils.copyBytes, B manually buffers and writes
- 修正建议: Re-evaluate BCB annotation for this pair; consider functional intent rather than generic I/O patterns；Improve benchmark consistency by requiring more specific behavioral alignment

### case_id=3182 FP boilerplate_overlap

- 方法: `read` vs `importSequences`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a skeleton file, splits content into sections delimited by '---', and validates the number of sections.
- B 摘要: Imports biological sequences from a URL by parsing FASTA-like format, extracting names and sequences.
- 静态失败原因: The model likely overfitted to common boilerplate patterns (e.g., reading from URL, BufferedReader, while loops, exception handling) and ignored the distinctive core logic, leading to a false positive clone detection.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would label this as non-clone because the functions perform entirely different domain-specific tasks with no semantic equivalence, even under broad Type-3/4 criteria.
- 共享行为: Both open an InputStream from a URL and read lines using a BufferedReader/InputStreamReader.；Both perform string processing on each line read.；Both handle potential I/O exceptions.
- 行为差异: Function A splits a file into sections based on '---' markers, while B parses sequence data based on '>' delimiters.；Function A accumulates entire sections into a list, whereas B reads sequences with a helper and stores names separately.；Function A validates the number of sections against an expected size; B does not have such validation.；Function B uses a custom ImportHelper for reading, while A uses standard BufferedReader.
- 修正建议: Enhance model training with more diverse examples to reduce sensitivity to boilerplate.；Incorporate structural features that capture task-specific control flow and data dependencies.；Use contrastive learning to distinguish between similar boilerplate but different semantics.

### case_id=3183 FP lexical_or_api_overlap

- 方法: `read` vs `downloadModel`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a skeleton file from classpath, splits it into sections by '---' delimiters, and validates the number of sections.
- B 摘要: Downloads an RDF model from a given URL using HTTP connection, reads the response into a Model object, and returns it.
- 静态失败原因: The model likely over-relied on superficial lexical or API overlap (e.g., URL, InputStream, BufferedReader, exception handling patterns) while ignoring the fundamental difference in functionality.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would not consider these clones because they perform completely different tasks (loading a config file vs downloading a remote model). Even under broad Type-4, there is no functional similarity.
- 共享行为: Both involve reading data from a stream (file or network).
- 行为差异: Function A reads from a resource file on classpath; Function B downloads from a remote URL over HTTP.；Function A splits content by '---' and collects sections; Function B parses RDF data into a Model object.；Function A throws Exception on missing resource or section count mismatch; Function B catches MalformedURLException and IOException and throws RuntimeException.；Function A returns void and populates a list; Function B returns a Model object.
- 修正建议: Improve model's ability to capture high-level program semantics beyond API sequences.；Incorporate data flow and control flow analysis to distinguish reading from different sources.；Use contrastive learning with more diverse non-clone pairs that share API calls but differ in purpose.

### case_id=3184 FP lexical_or_api_overlap

- 方法: `addQDInformation` vs `readUNI`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads qdinfo data from local file or URL, parses lines starting with 'pg' and 'pt', updates internal project information.
- B 摘要: Reads tab-separated UNI data from a URL, extracts id and description, adds them to a vector.
- 静态失败原因: Static BERT/GraphCodeBERT likely overemphasized lexical and API-level similarity (URL, openStream, reading lines, parsing) and missed semantic differences due to limited understanding of control flow and data dependencies.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically marks non-clones when functions have different input/output behavior and data manipulation, despite similar I/O patterns.
- 共享行为: Both open a URL stream to read data.；Both read lines and parse them.；Both handle IOException with try-catch.
- 行为差异: A may read from local file, B only from URL.；A parses specific prefixes 'pg' and 'pt', B parses tab-separated fields.；A updates internal object fields, B adds to a passed vector.；A has a conditional based on file modification date, B does not.
- 修正建议: Incorporate dataflow analysis to distinguish how parsed data is used.；Add attention to method signatures and parameter/return types.；Use contrastive learning with hard negative mining on similar but different I/O patterns.

### case_id=3185 FN benchmark_preference_bias

- 方法: `encodeFileToFile` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.2`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Reads a file, Base64 encodes it, writes to another file, and returns success flag.
- B 摘要: Launches a NexOpen project by managing Maven pom.xml files, handling XML documents, and configuring Hibernate reverse engineering.
- 静态失败原因: The static model correctly predicted non-clone based on low token overlap and dissimilar structure; it did not fail from our perspective.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled as clone due to both involving file operations and stream handling, but the functionalities are entirely different.
- 行为差异: Function A performs file I/O with Base64 encoding; Function B manages Eclipse project launch configurations.；Function A uses InputStream/OutputStream; Function B uses IProject, IFile, Document, Properties.；Function A returns boolean; Function B returns void and throws CoreException.；Domain: Function A is general-purpose; Function B is Eclipse plugin-specific.
- 修正建议: Re-evaluate BCB annotation for this pair; it appears to be an erroneous clone label.；If BCB intends partial functionality, clarify criteria for I/O-based tasks; otherwise, remove from clone set.

### case_id=3186 FP boilerplate_overlap

- 方法: `readZoneIDs` vs `read`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a file containing integer zone IDs, one per line, and returns them as a set.
- B 摘要: Reads a skeleton file, splits into sections delimited by '---', validates count, and throws exceptions on errors.
- 静态失败原因: The model likely over-relied on the common structural pattern of resource loading and line reading, overlooking the entirely different core data processing logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled non-clone because the overall functionality (integer parsing vs section splitting) is distinct despite shared I/O boilerplate.
- 共享行为: Both use getResource to load a file from classpath；Both open an InputStream and wrap with InputStreamReader/BufferedReader；Both iterate lines in a while loop
- 行为差异: A parses each line as an integer; B splits lines by a marker and builds sections；A returns a HashSet; B is void and populates a list；A catches all exceptions silently; B throws specific exceptions on missing file or wrong section count
- 修正建议: Enrich model with data-flow analysis to track how each line is transformed；Use contrastive learning to differentiate boilerplate from core functionality；Incorporate type information (return type, parameter types) into representation

### case_id=3187 FP lexical_or_api_overlap

- 方法: `main` vs `fileCopy`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: A main method that parses command-line arguments, reads a Prolog file, generates adapter code, and writes a JAR file.
- B 摘要: A file copy method that copies a file from source to destination with various checks.
- 静态失败原因: The static BERT/GraphCodeBERT model likely over-relied on lexical and API-level overlap (e.g., File, IOException, try-catch) and missed the overall semantic difference in program logic and purpose.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels non-clones for functions with completely different purposes, even if they share some common library calls. The high-level functionality of generating adapters vs. copying files is sufficiently distinct to be a non-clone.
- 共享行为: Both handle file operations and IOException；Both use File and FileInputStream/FileOutputStream classes；Both have error handling via try-catch or try-finally
- 行为差异: Function A is a complex multi-step code generation pipeline; B is a simple file copy；A reads and parses Prolog, generates adapters, writes JAR; B reads raw bytes and writes to a new file；A has command-line argument parsing; B has no arguments beyond source and destination；A uses many domain-specific classes (Parser, FactVisitor, etc.); B uses only standard I/O
- 修正建议: Incorporate data flow or control flow analysis to distinguish different algorithmic intents；Use task-specific fine-tuning to recognize that file copy and code generation are different tasks；Augment training with more negative examples that have high API overlap but different semantics

### case_id=3188 FP boilerplate_overlap

- 方法: `handler` vs `readUNI`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `1.0`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a URL line by line and extracts substrings based on include/from/to strings into a map.
- B 摘要: Reads tab-separated data from a URL source and populates a vector with id and description.
- 静态失败原因: The static model likely focused on common boilerplate tokens (URL, InputStream, MalformedURLException, readLine) and missed the core semantic differences in parsing logic and output handling.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically annotates clones based on functional similarity. These functions perform distinct data extraction tasks, so they are not considered clones.
- 共享行为: Both open a URL and read input from it；Both handle MalformedURLException；Both read line by line or token by token
- 行为差异: Different output data structures: Map vs Vector；Different parsing logic: substring/indexOf vs tab-delimited Scanner；Different input: TargetPage object vs string source
- 修正建议: Incorporate dataflow analysis to capture core data transformations；Weigh functional logic tokens more heavily than boilerplate tokens；Use graph-based representations to distinguish different control flows

### case_id=3189 FN benchmark_preference_bias

- 方法: `handle` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Handles log file rotation, compression, and archiving of old files based on time thresholds.
- B 摘要: Launches a NexOpen project configuration by processing pom files, setting Hibernate properties, and installing the project.
- 静态失败原因: This is a false negative where the model correctly identified no semantic equivalence, but BCB's label suggests otherwise; the low token overlap and different domains likely caused correct non-clone prediction.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled these as clones based on a very broad interpretation of 'file management' or 'configuration tasks', but the functional purposes are entirely different.
- 共享行为: Both perform file I/O operations and handle exceptions.
- 行为差异: A deals with log rotation and compression; B deals with project configuration and deployment.；A uses file channels and GZIP; B uses Eclipse resources and XML processing.；A archives old files; B creates reverse engineering files.；A runs a scheduled task; B runs as a launch configuration.
- 修正建议: Re-evaluate BCB annotation for this pair; consider it a non-clone.；If model must match BCB, incorporate higher-level semantic features like task category.

### case_id=3190 FN benchmark_preference_bias

- 方法: `decodeFileToFile` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Decodes a Base64-encoded input file and writes the decoded data to an output file.
- B 摘要: Builds a website for editing by processing XML, transforming it, and writing multiple pages to output files.
- 静态失败原因: Static BERT/GraphCodeBERT likely correctly identified non-clone due to low token Jaccard (0.0667) and different method signatures/content, so it did not fail
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might have labeled this as a clone due to both methods involving file I/O and exception handling, focusing on the superficial similarity in I/O patterns
- 共享行为: Both methods read from a file and write to a file；Both use buffered I/O and handle exceptions
- 行为差异: decodeFileToFile performs a single file-to-file transformation with Base64 decoding；buildSiteForEdit performs complex multi-step site generation with XML parsing, transformation, and multiple file writes；The purpose and complexity of the methods are vastly different
- 修正建议: Re-evaluate BCB annotation for this pair; consider removing or correcting based on semantic mismatch；Improve clone detection benchmarks to avoid labeling dissimilar functions as clones due to trivial I/O overlap

### case_id=3191 FN partial_functionality

- 方法: `main` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a URL and extracts its zip entries to the local file system.
- B 摘要: Recursively copies a file or directory from one location to another.
- 静态失败原因: Static BERT likely focused on the structural similarity of the while loops reading and writing bytes, overlooking the semantic difference in data sources (URL vs local file) and the unzipping process, leading to a false negative.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have considered the similar use of FileOutputStream and BufferedOutputStream and the general file-copying pattern as sufficient for a Type-3 or Type-4 clone, despite the different inputs and additional unzipping logic.
- 共享行为: Both perform file I/O operations involving reading from an input stream and writing to an output stream.；Both use buffers for efficient I/O.
- 行为差异: Function A reads from a network URL and unzips, while Function B copies local files/directories.；Function A handles only a single zip file, while Function B handles directories recursively.；Function A writes entries to the current directory, whereas Function B copies to a specified destination.
- 修正建议: Incorporate data flow analysis to distinguish input sources (URL, local file, zip stream).；Improve understanding of overall algorithm purpose beyond low-level I/O patterns.；Use control flow and API call context more explicitly.

### case_id=3192 FP boilerplate_overlap

- 方法: `run` vs `getXML`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Downloads a GeoJSON tile from a URL, parses it into geometries, and adds them to a data loader.
- B 摘要: Fetches XML content from a URL and returns it as a string.
- 静态失败原因: The static BERT/GraphCodeBERT method likely overemphasized the high token overlap in the URL reading boilerplate (opening streams, reading lines, handling exceptions). The similar structure of opening a URL, reading lines, and catching IOException caused the model to classify them as clones, ignoring the substantial differences in post-processing and overall purpose.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled this as non-clone because the functions have different purposes: one is a specific tile downloader with geometry processing, the other is a generic XML fetcher. Despite sharing the boilerplate of reading URL content, the core functionality and output differ significantly. BCB's annotation prefers functional similarity over syntactic overlap.
- 共享行为: Both open a URL connection, read lines using BufferedReader, and build a string by concatenating lines.；Both handle MalformedURLException and IOException.
- 行为差异: A additionally checks a cache (lauchedHTTPRequests set) to avoid duplicate requests, while B does not.；A processes the downloaded data into geometric objects (VectorTile, GeometryCollection) and adds them to a data loader, while B simply returns the raw string.；A supports both file and HTTP protocols, B only HTTP.；A returns void and side-effects data structures, B returns a String.
- 修正建议: Use data flow analysis to differentiate side effects and return types.；Incorporate method name and context (e.g., class name, method override annotations) into the model.

### case_id=3193 FP lexical_or_api_overlap

- 方法: `importRoles` vs `getFullScreenUrl`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Downloads and parses XML-style role data from a URL, returning a list of RoleName objects.
- B 摘要: Downloads a YouTube page, extracts fullscreen URL parameters, and returns a constructed video download URL.
- 静态失败原因: Static BERT/GraphCodeBERT models may over-rely on surface-level lexical and API similarities (e.g., URL, BufferedReader, while loop) and miss the semantic intent difference due to limited reasoning about long-range dependencies and dataflow.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels clones only if they share significant functional behavior. These functions have different purposes (parsing roles vs extracting video URLs) and different output types, so they are not clones even under a relaxed interpretation.
- 共享行为: Both read from a URL using BufferedReader and InputStreamReader.；Both use a while loop to read lines of text.；Both catch exceptions (IOException etc.).
- 行为差异: Function A parses XML tags to create RoleName objects; function B searches for a specific keyword and splits strings.；Function A appends all lines and segments on '</RoleName>'; function B processes only lines containing 'fullscreenUrl'.；Function A returns a list of role names; function B returns a single fullscreen URL string.；Function B updates UI (progressDown) and prints debug output; function A does not.
- 修正建议: Use dataflow or program dependency analysis to distinguish different data transformations.；Incorporate abstract syntax tree (AST) or control-flow graph distances to capture structural differences.；Add attention to output types and method signatures to penalize mismatched return types.；Train with more diverse negative examples that have similar API usage but different semantics.

### case_id=3194 FN partial_functionality

- 方法: `copyResource` vs `decodeFileToFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource (URL or file) to a destination file byte by byte, throwing exception on missing resource.
- B 摘要: Decodes a file from Base64 and writes the decoded bytes to an output file using buffered streams, returning success boolean.
- 静态失败原因: The model likely overemphasized lexical differences (low token overlap, distinct API calls like Base64.InputStream) and functional differences (decoding, return value), failing to abstract the common stream-copying structure.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider them Type-4 clones because both implement the fundamental 'copy stream' pattern, and differences in encoding, buffering, and error handling are viewed as non-functional variations.
- 共享行为: Both open an input stream to read data.；Both open an output stream to write data.；Both loop reading bytes from input and writing to output.；Both close the input and output streams after copying.
- 行为差异: A reads a URL or file directly, while B decodes Base64 from a file.；A reads one byte at a time, B uses a 64KB buffer.；A throws an exception on failure, B returns false and prints stack trace.；A is void, B returns a boolean success flag.
- 修正建议: Use dataflow analysis to identify input-to-output byte stream patterns.；Abstract away specific API calls and focus on the I/O loop pattern.；Incorporate structural similarity measures like AST or CFG matching.

### case_id=3195 FN partial_functionality

- 方法: `readGeoParserResult` vs `doVersionCheck`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a geo-parser result from a remote service via HTTP, parses XML, and returns a collection of place names with associated gazetteer IDs, with retries on failure.
- B 摘要: Checks for a newer version of the application by fetching a remote file, parsing lines for build numbers, and invoking an update method if both devel and stable builds are found.
- 静态失败原因: Static BERT models rely heavily on token overlap and surface-level syntax. These functions have very low token Jaccard (0.127), different method names, and different domain vocabulary. The model likely failed to recognize the abstract structural similarity of the network I/O pattern because it was overwhelmed by the lexical and syntactic differences.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BigCloneBench's Type-4 annotation may consider these as clones because both are 'network I/O with text parsing' routines that follow a similar structure: create URL, open stream, buffer, read lines, handle exceptions. The shared pattern of connecting to a remote resource and processing line-by-line could be seen as functionally equivalent at a high abstraction level, despite different domain-specific details.
- 共享行为: Both open a URL and read lines from an InputStream using BufferedReader.；Both handle IOException with error logging or user notification.；Both have a similar while loop pattern to read lines until null.
- 行为差异: Function A sends a custom XML request, parses complex XML with element traversal, and returns a collection of Tuples; Function B reads a simple text format and calls another method.；Function A includes a retry mechanism with a maximum of 3 attempts; Function B has no retries.；Function A has conditional logic based on a boolean parameter; Function B uses jEdit property and shows/hides wait cursor on the View.；The parsing logic inside the loop is entirely different: extracting TermName and entryID from XML vs. checking line prefixes for build strings.
- 修正建议: Incorporate data flow or control flow graphs to capture high-level patterns like URL opening, buffered reading, and exception handling.；Use contrastive learning on pairs that share abstract behavior but differ in domain terms.；Add attention to structural commonalities (e.g., while loop reading lines) rather than token overlap.

### case_id=3196 FN partial_functionality

- 方法: `copyFileTo` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.4`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Copies a file from the current path to a destination file using FileChannel transferFrom.
- B 摘要: Builds a website for editing by reading XML, transforming, and writing output files for each page.
- 静态失败原因: The model likely focused on token-level similarity (low Jaccard) and failed to recognize that the high-level file I/O could be considered a partial clone. Alternatively, the model may have been confused by the length and complexity of buildSiteForEdit.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled this as a clone due to shared file I/O patterns (both use FileInputStream, FileOutputStream) and the presence of file transfer operations, considering broad Type-4 or partial functionality similarity.
- 共享行为: Both perform file input/output operations using FileInputStream and FileOutputStream.
- 行为差异: copyFileTo is a simple file copy; buildSiteForEdit involves complex XML transformation, string replacement, and looping over pages.；copyFileTo has minimal error handling; buildSiteForEdit has extensive error handling and logging.；buildSiteForEdit has many parameters and dependencies (e.g., DOM, Transformers); copyFileTo has only a destination parameter.
- 修正建议: Improve the model to capture functional intent beyond token overlap.；Incorporate control and data flow analysis to distinguish simple file copy from complex site generation.；Use a more robust representation that captures the overall goal of the method.

### case_id=3197 FN partial_functionality

- 方法: `sendExceptionToServer` vs `login`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends exception details to a server via HTTP POST, logs success or failure.
- B 摘要: Logs in to LOLA by sending email and password via HTTP POST, returns a session ID.
- 静态失败原因: The model likely focused on the surface-level semantic difference (exception reporting vs login) and the different variable/function names, missing the underlying structural commonality in the HTTP communication pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider these clones due to high structural similarity in the HTTP POST pattern, despite different domain logic, as they often accept broad Type-3/Type-4 clones with similar control flow and API usage.
- 共享行为: Builds URL-encoded data string；Opens HTTP connection with URLConnection；Writes data to output stream；Reads response from input stream
- 行为差异: Different data parameters (exception info vs login credentials)；Response processing: prints response in A, extracts session ID in B；Return type: void in A, String in B；Error handling: catches IOException in A, catches generic Exception in B
- 修正建议: Train model to recognize common code patterns (e.g., HTTP request handling) beyond specific tokens.；Incorporate structural features like control flow graphs or data flow graphs.；Use a clone detector that explicitly matches API usage sequences.

### case_id=3198 FP lexical_or_api_overlap

- 方法: `readZoneIDs` vs `wordFrequency`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a list of integers from a resource file and returns them as a HashSet.
- B 摘要: Fetches a web page, extracts a word frequency value by pattern matching, and returns the integer frequency or 0.
- 静态失败原因: The static BERT/GraphCodeBERT model likely over-relied on lexical and structural overlaps such as URL, InputStreamReader, readLine, try-catch, and printStackTrace, missing the fundamental semantic differences in data processing and return types.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels this as non-clone because the functions have entirely different purposes and outputs, despite sharing common I/O boilerplate. The structural similarity is low, and the core logic differs completely.
- 共享行为: Both use URL, InputStreamReader, and readLine to read text line-by-line.；Both use try-catch blocks catching exceptions and printing stack traces.；Both return a simple type after processing input (HashSet<Integer> vs int).
- 行为差异: Function A reads from a local resource file; Function B constructs a URL and fetches from the web.；Function A parses each line as an integer; Function B matches lines against a regex pattern.；Function A accumulates all integers into a set; Function B returns the first match found.；Error return: A returns empty set; B returns 0.
- 修正建议: Incorporate dataflow analysis to track how input is transformed into output.；Use contrastive learning with negative samples having high lexical overlap but different semantics.；Add type and API usage graphs to distinguish different usage patterns.

### case_id=3199 FN partial_functionality

- 方法: `main` vs `unzipEntry`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a remote KMZ file and extracts all entries to the current directory.
- B 摘要: Extracts a single ZIP entry from a local ZipFile to a specified output directory.
- 静态失败原因: The low token Jaccard similarity (0.1358) and different method signatures (main vs private static) likely led the model to miss the core shared behavior. The URL handling in code_a may have distracted the model from the ZIP extraction logic.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BigCloneBench may label this as a clone because both functions perform ZIP entry extraction, a common functionality pattern, even though the context and granularity differ.
- 共享行为: Both functions read data from a ZIP entry and write it to a file using buffered streams.
- 行为差异: Code_a handles multiple entries from an online ZIP file, while code_b handles a single entry from a local ZipFile.；Code_a creates FileOutputStream for each entry inside a while loop, while code_b uses IOUtils.copy with try-finally for resource management.；Code_a includes URL handling and protocol detection, code_b does not.
- 修正建议: Train on more partial-functionality clones or use semantic embeddings that capture I/O patterns.；Incorporate structural matching that can identify loops vs single calls with similar core operations.

### case_id=3200 FN benchmark_preference_bias

- 方法: `doGet` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Reads a local file from a given path and writes its content to the HTTP response output stream.
- B 摘要: Launches a configuration for a NexOpen project, checking project files, processing XML profiles, handling reverse engineering files, and triggering an install project action.
- 静态失败原因: Static BERT/GraphCodeBERT models may have correctly predicted non-clone due to low token overlap (Jaccard 0.05) and lack of shared API calls beyond IOUtils. The model's prediction of 0 aligns with the true functional dissimilarity.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might consider these Type-4 clones because both involve reading files using IOUtils and dealing with input streams, but the overall functionality is completely different. However, given BCB's typical focus on functional similarity, they likely would not label these as clones. The given BCB label of 1 may be an annotation error or due to very loose criteria.
- 共享行为: Both involve file I/O operations；Both use IOUtils for copying streams
- 行为差异: Function A is a simple HTTP file serving; Function B is a complex Eclipse launch with multiple file checks, XML parsing, and property handling；Function A has no error handling; Function B has exception handling and logging；Function A is a servlet; Function B is an Eclipse plugin launch delegate；Function A works with HttpServletRequest/Response; Function B works with ILaunchConfiguration, IProgressMonitor, etc.
- 修正建议: Ensure annotation guidelines are clear about functional equivalence vs. superficial I/O similarity；Use more precise clone benchmarks like CodeXGLUE that focus on exact or near-exact clones

### case_id=3201 FP boilerplate_overlap

- 方法: `readData` vs `main`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Parses multiple comma-separated configuration strings into sets and a map, then reads a file to populate Tibetan transliteration lookup tables.
- B 摘要: Reads a log file and writes every Nth line starting with a given token to a new file.
- 静态失败原因: The model likely over-relied on the common file-reading boilerplate (BufferedReader, FileReader, while loop, IOException) and missed the fundamental difference in data processing logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would label this as non-clone because the functions have completely different purposes and outputs, lacking functional similarity even at Type-4 level.
- 共享行为: Both read from files using BufferedReader.；Both use try-catch blocks for IOException.；Both use a while loop to iterate over lines.
- 行为差异: Function A parses configuration strings with StringTokenizer; B filters lines based on line number and prefix.；Function A builds multiple sets and a map; B writes filtered lines to a new file.；Function A has complex logic for populating tibHash, charSet etc.; B has simple line selection.；Function A's file reading is part of a larger initialization; B's entire purpose is file filtering.
- 修正建议: Incorporate dataflow analysis to distinguish core transformations.；Use program dependence graphs to capture the actual computation rather than surface I/O patterns.；Enhance training data with negative examples that share I/O patterns but differ in semantics.

### case_id=3202 FN partial_functionality

- 方法: `modifyApplicationMessage` vs `saveFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Modifies a specific message in a localized properties file by reading, editing, and rewriting the file.
- B 摘要: Saves the current UI window state (toolbars, windows, volumes) to an XML configuration file.
- 静态失败原因: Low token Jaccard (0.1077) and different API calls (Properties vs XML libraries) mislead the model into focusing on lexical mismatch rather than the high-level goal of file persistence.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as 'saving configuration to a file' operations, thus a weak Type-4 clone, despite different file formats and detailed logic.
- 共享行为: Both functions write data to a file after processing input.；Both use try-catch blocks for exception handling.；Both involve file I/O operations (reading and writing).
- 行为差异: Function A modifies an existing properties file line-by-line; Function B constructs an XML document from scratch.；Function A targets a specific key-value pair; Function B serializes entire UI state.；Input types differ: locale/messageName/messageValue vs MainWindow.；Function A uses BufferedReader and FileWriter; Function B uses XMLOutputter and OutputStreamWriter.
- 修正建议: Incorporate data flow analysis to detect file output operations.；Train on diverse examples of file-writing functions to generalize across different file formats.；Use contrastive learning to distinguish specific implementation details from overall goal.

### case_id=3203 FN partial_functionality

- 方法: `resolvePlugins` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Resolves and caches a plugins.xml file from a URL if not already cached.
- B 摘要: Launches a NexOpen project configuration, ensuring necessary Maven profile and Hibernate reverse engineering files exist, then schedules a build action.
- 静态失败原因: Static models like GraphCodeBERT rely on token-level similarity and syntactic structure. The two functions have very low token Jaccard (0.059) and different method names, so the model likely saw no semantic similarity. Additionally, the shared sub-behavior is buried within larger, context-heavy functions, and static models may not capture deep partial functional patterns without training on such nuanced similarities.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label these as clones because both functions contain a similar sub-pattern: checking if a file exists, and if not, creating it by copying from a resource (URL for A, bundle for B) using IOUtils.copy. This partial behavioral overlap may be considered a Type-4 clone under BCB's broad criteria.
- 共享行为: Both functions involve checking for the existence of a file and creating/obtaining it if missing；Both use IOUtils.copy for streaming data；Both handle exceptions (though differently)
- 行为差异: Function A is a simple one-step cache operation; Function B is a multi-step launch process involving project configuration, Maven profiles, Hibernate settings, and job scheduling；Function A deals with a simple plugins.xml from a fixed URL; Function B deals with multiple project-specific files including pom.xml and reverse engineering files；Function A is part of a plugin management system; Function B is part of an Eclipse launch configuration for a specific framework
- 修正建议: Train a model to recognize partial behavioral clones where only a sub-task is shared；Use dataflow analysis to detect common operations like 'ensure file exists'；Incorporate functional call graph information to identify common utility patterns

### case_id=3204 FP lexical_or_api_overlap

- 方法: `readData` vs `setImg`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Parses comma-separated strings to initialize various sets and a valid input map, and reads a configuration file to populate translation tables.
- B 摘要: Opens a file chooser to select an image, copies it to a local directory, and sets it as a background image.
- 静态失败原因: The low Jaccard similarity suggests limited lexical overlap, but the static model may have been misled by a few common patterns (e.g., File operations, try-catch, variable initialization) or failed to capture the overall semantic context due to the large length difference and truncated code_a.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would label as non-clone because the functions are completely unrelated in functionality; one is a data loader for a text conversion system, the other is a GUI image setter.
- 共享行为: Both perform file I/O operations
- 行为差异: Different purposes: data initialization vs. GUI image setting；Different input sources: string tokens vs. file chooser；Different outputs: internal state vs. file copy and ImageIcon
- 修正建议: Improve handling of long-range dependencies；Incorporate structural or dataflow analysis；Enhance sensitivity to function purpose

### case_id=3205 FN partial_functionality

- 方法: `File2String` vs `invoke`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a file from filesystem or classpath and returns its content as a string, exiting on failure.
- B 摘要: Performs an HTTP POST invocation, reads response, deserializes JSON, and supports retry on timeout.
- 静态失败原因: Static BERT likely learned that the high-level method signatures and overall structure are too different, and token overlap is low.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label as clone due to overlapping pattern of reading input stream and concatenating lines, ignoring the broader context and purpose.
- 共享行为: Both use BufferedReader to read lines and build a StringBuilder；Both handle IOException
- 行为差异: Method A reads local files; Method B makes HTTP request and parses JSON；Method A exits on error; Method B throws exceptions or retries；Method B involves reflection and serialization
- 修正建议: Include more global context to distinguish different I/O operations；Add functional role detection beyond code patterns

### case_id=3206 FN benchmark_preference_bias

- 方法: `readData` vs `callApiPost`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Parses multiple comma-separated strings to populate sets and maps for Tibetan transliteration, and reads a file with complex parsing logic.
- B 摘要: Sends an HTTP POST request with parameters and returns the response InputStream after checking status code.
- 静态失败原因: The static BERT model correctly identified the lack of semantic and syntactic similarity, resulting in a non-clone prediction, but this conflicts with BCB's overly broad annotation preference.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may label this as clone due to an extremely broad interpretation of Type-4 (semantic similarity) where both are considered 'data retrieval' methods, despite major differences in domain and implementation.
- 共享行为: Both methods handle IO exceptions.
- 行为差异: A populates multiple in-memory data structures from hardcoded string fields; B makes external network call.；A involves parsing and tokenizing strings; B sends HTTP request and returns stream.；A has complex file parsing logic; B is a straightforward API call.
- 修正建议: Train with explicit negative examples of procedural vs. non-procedural methods.；Incorporate data flow analysis to distinguish between local setup and external IO.

### case_id=3207 FN benchmark_preference_bias

- 方法: `getFile` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies its wsdlsoap:address endpoint, and saves it to a temporary file, returning the file path.
- B 摘要: Configures and launches a Hibernate-based Maven project in Eclipse, handling pom.xml processing and reverse engineering setup.
- 静态失败原因: Static BERT methods rely on token and structural overlap; they correctly identified low similarity and predicted non-clone, disagreeing with the BCB annotation which may be an error or based on overly broad criteria.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might consider these clones due to both having similar structural patterns (e.g., Document handling, file I/O, logging) and being in the same broad category of 'resource management' or 'configuration', but the actual functionality is entirely different.
- 共享行为: Both involve file I/O operations；Both process XML documents；Both include error handling with logging；Both use try-catch blocks for exception handling
- 行为差异: A downloads from a URL and modifies XML; B configures project files and Hibernate dialect；A returns a string (file path); B returns void and modifies Eclipse workspace state；A focuses on WSDL retrieval and endpoint replacement; B focuses on Maven project setup and reverse engineering；A uses temporary files and channels; B uses Eclipse project resources and properties
- 修正建议: Improve annotation guidelines to avoid overgeneralization of Type-4 clones；Use domain-specific models to differentiate between generic I/O patterns and specific business logic；Incorporate more contextual abstraction to avoid false positives due to incidental similarities

### case_id=3208 FP lexical_or_api_overlap

- 方法: `loadMFileViaWeb` vs `readUNI`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Loads a MATLAB .m file from a URL, reads its content line by line, concatenates into code string, parses to create a UserFunction.
- B 摘要: Reads a TSV file from a URL, parses tab-separated fields, extracts id and description, adds them to a vector of strings.
- 静态失败原因: The model likely overemphasized the common API usage pattern (URL, openStream, readLine/scanner loop) leading to lexical/structural similarity detection, but missed the different data processing logic and output types.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels as non-clone unless there is significant functional similarity or they are part of a similar task. Here the overall goal (loading code vs. parsing tabular data) differs, so non-clone.
- 共享行为: Both open a URL connection and read input stream line by line；Both iterate over lines until end-of-file
- 行为差异: A constructs a code string and parses it into a UserFunction; B builds a vector of concatenated id-description strings；A uses BufferedReader and manual line concatenation; B uses Scanner with tab delimiter；A sets the function name from parameter; B adds processed entries to an external vector；A throws a MathLibException on error; B catches exceptions with printStackTrace or swallow
- 修正建议: Train or fine-tune with contrastive learning on data where API usage alone is not indicative of clone；Incorporate type or output analysis (e.g., void vs UserFunction) to break false positives；Use models that better capture long-range data flow and result usage

### case_id=3209 FP boilerplate_overlap

- 方法: `actionPerformed` vs `writeData`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Handles user interface actions for setting file paths and configuration preferences.
- B 摘要: Writes experimental data (peaks) to a file in tabular format.
- 静态失败原因: Likely misled by superficial similarities such as both containing file-related operations (JFileChooser vs PrintWriter) and common tokens like 'file', 'print', 'if', but the overall semantics differ greatly.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels as non-clones because the methods have entirely different purposes, signatures, and only trivial overlap in using common Java libraries.
- 行为差异: Function A handles UI events and user interaction; B writes data to a file.；A uses JFileChooser for file selection; B uses PrintWriter for file output.；A sets application preferences; B formats and outputs numeric data.；A contains extensive branching based on action commands; B has nested loops for data processing.
- 修正建议: Incorporate method signature and return type into the model.；Use contrastive learning with hard negative mining to differentiate such pairs.；Add a global code graph representation to capture long-range dependencies and overall purpose.

### case_id=3210 FN benchmark_preference_bias

- 方法: `main` vs `readAndRewrite`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a URL and extracts its contents to local files.
- B 摘要: Reads a DICOM file, parses pixel data, and writes it to another DICOM file.
- 静态失败原因: GraphCodeBERT likely focused on lexical tokens and API usage, which have low overlap (Jaccard 0.118). The model correctly identified them as non-clones, disagreeing with BCB's questionable label.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled these as clones due to structural similarities in I/O handling (opening streams, buffering, closing resources) and the overall pattern of 'read input, process, write output'. However, this interpretation is overly broad and likely a labeling error.
- 共享行为: Both open input streams and output streams；Both use buffered I/O；Both have a loop-like structure to process data
- 行为差异: Function A downloads from a URL; Function B reads from a local file；Function A handles ZIP decompression; Function B handles DICOM medical image parsing；Function A writes multiple output files; Function B writes a single output file；Completely different domain-specific APIs and data formats
- 修正建议: Re-evaluate BCB label for this pair; consider it a false positive in the benchmark.；If using BCB-style evaluation, incorporate functional similarity thresholds beyond I/O patterns.；For model training, use domain-aware features to distinguish different file processing tasks.

### case_id=3211 FN benchmark_preference_bias

- 方法: `doGet` vs `createTar`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.85`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Handles HTTP GET request for a page: retrieves page, checks permissions, renders and sends response, with caching and logging.
- B 摘要: Creates a tar archive from a directory: validates inputs, collects files, writes each file into a tar output stream with compression.
- 静态失败原因: Static models rely on surface-level features and global code structure; they correctly identified low similarity (0.12 Jaccard) and predicted non-clone, aligning with strict equivalence but disagreeing with BCB's broad annotation.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider these clones due to both being 'service' methods that perform I/O with error handling and logging, despite different domains, under a very broad Type-4 (functional similarity) criterion.
- 共享行为: Both perform file I/O operations；Both include logging of progress or errors；Both handle exceptions and ensure resource cleanup
- 行为差异: doGet is an HTTP request handler; createTar is a file archiving utility；doGet involves user permission checks and HTML rendering; createTar involves tar entry creation and stream management；doGet outputs to an HTTP response; createTar outputs to a tar file
- 修正建议: Re-evaluate BCB annotation for this pair; consider if partial functionality overlap is warranted.；If BCB label is correct, improve model to capture abstract high-level patterns (e.g., 'resource management' structure) via contrastive learning on broad clone categories.

### case_id=3212 FN benchmark_preference_bias

- 方法: `modifyApplicationMessage` vs `unzip`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Modifies a properties file by updating or adding a key-value pair for a given locale.
- B 摘要: Extracts a zip archive into a directory, creating necessary subdirectories.
- 静态失败原因: The low token overlap (Jaccard 0.17) and different method names ('modifyApplicationMessage' vs 'unzip') lead the static model to predict non-clone, as there is no strong lexical or structural similarity.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as a clone (Type-4) because both functions involve generic file manipulation: reading input, processing, and writing output, despite very different domain-specific logic.
- 共享行为: Both perform file I/O operations (reading and writing files).；Both handle exceptions with try-catch or throws.
- 行为差异: A reads and writes text properties files line by line; B reads binary zip entries.；A modifies a specific property; B extracts all entries from a zip.；A copies a default file if the locale file doesn't exist; B creates subdirectories for output.
- 修正建议: Incorporate higher-level semantic understanding of program goals beyond syntactic patterns.；Use program dependency graphs or dataflow analysis to capture functional purpose.

### case_id=3213 FN partial_functionality

- 方法: `modifyApplicationMessage` vs `copy`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a locale-specific properties file, updates or adds a message key-value pair, and writes back; if the locale file does not exist, it first copies the English properties file as a template.
- B 摘要: Copies a file from source to destination using NIO FileChannels and memory-mapped buffers.
- 静态失败原因: Static BERT models may have focused on low token overlap and different method signatures, missing the shared file copying behavior. Additionally, long-range dependencies in function A (conditional copy then modify) might not be captured.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider the shared file copying subtask as sufficient for a partial functionality clone, despite the overall different purposes.
- 共享行为: Both involve file copying (A copies a template file if needed; B always copies).
- 行为差异: A's main purpose is to modify a properties file; B's sole purpose is to copy.；A uses character-by-character I/O for copy; B uses NIO channels.；A reads, parses, modifies, and writes properties; B just copies bytes.
- 修正建议: Improve training to recognize shared sub-tasks (e.g., file copy) across different overall functions.；Incorporate data-flow or control-flow analysis to identify common patterns.

### case_id=3214 FN partial_functionality

- 方法: `getFile` vs `copy`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, possibly modifies its endpoint, and saves it to a temp directory.
- B 摘要: Recursively copies a file or directory from source to destination using FileChannel.
- 静态失败原因: The model relied on token overlap (low Jaccard) and surface-level API usage, missing the underlying I/O pattern shared by both functions.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider the shared use of FileChannel.transferFrom for file output as a partial functionality similarity, labeling as Type-4 clone despite different overall tasks.
- 共享行为: Both use FileChannel.transferFrom to copy data into a file.
- 行为差异: Function A downloads from a network URL and modifies XML, while Function B copies local files/directories.；Function A has complex error handling throwing AxisFault, Function B prints errors and exits.；Function A returns a file path, Function B returns void.
- 修正建议: Train on more diverse Type-4 examples that emphasize common algorithmic patterns over token overlap.；Incorporate structural or dataflow analysis to capture shared low-level operations like channel transfers.

### case_id=3215 FN partial_functionality

- 方法: `copy` vs `getFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a file from source to destination using file channels and transferTo.
- B 摘要: Downloads a WSDL file from a URL, optionally modifies its endpoint, and saves it to a temporary file.
- 静态失败原因: Static models rely on lexical and structural similarity but the token overlap is low (0.1066), method names differ, code lengths differ greatly, and the overall structure is dissimilar. The model likely learned that such differences indicate non-clone.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considers this a clone because both functions share the core functionality of copying data from one source to another using FileChannel, and the additional operations in B are considered extensions or variations of the same basic functionality.
- 共享行为: Both functions perform a data transfer from an input source to an output destination using Java NIO FileChannel operations.
- 行为差异: Function A is a simple file copy; Function B involves network download, XML parsing, conditional file existence check, and exception handling for multiple types.
- 修正建议: Improve the model to recognize common sub-patterns (e.g., FileChannel operations) even in different contexts.；Use code summarization or semantic embeddings that capture high-level intent.；Incorporate data flow analysis to detect similar I/O operations.

### case_id=3216 FN benchmark_preference_bias

- 方法: `getFile` vs `copy`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.6`
- 推荐路线: `preference_memory_with_manual_audit`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies its endpoint attribute, and saves it to a temporary location.
- B 摘要: Copies a file from a source path to a destination path using byte stream.
- 静态失败原因: Static BERT-based models rely on token similarity and structural overlap; the low Jaccard similarity (0.112) and different method names ('getFile' vs 'copy') likely caused it to miss the high-level file I/O commonality that BCB annotators may have considered.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB likely considered both as 'file copying' operations broadly defined (copying from a source to a destination), and the presence of similar boilerplate (temporary file creation, stream handling, error logging) may have led to a Type-4 clone label despite semantic differences.
- 共享行为: Both perform file I/O operations: read from an input source and write to an output file.；Both handle IOException.
- 行为差异: Function A downloads from a remote URL, while function B reads from a local file.；Function A modifies XML content (replaces endpoint attribute) before writing; function B writes raw bytes without modification.；Function A uses NIO channels and explicit URL connection; function B uses byte buffer and FileStream.；Function A has complex error handling for multiple exception types; function B only throws IOException.
- 修正建议: Incorporate higher-level task abstraction (e.g., file I/O operations) into the representation.；Add contrastive learning with positive pairs based on task similarity rather than exact implementation.；Use data augmentation to teach models that downloading and local copying can be clones under broad definitions.

### case_id=3217 FN partial_functionality

- 方法: `main` vs `createOutputStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a URL and extracts all entries to the current directory.
- B 摘要: Copies a ZIP file, skipping 'content.xml', then adds a new entry and returns a BufferedWriter for it.
- 静态失败原因: Static BERT models may have focused on the high API overlap (ZipInputStream, getNextEntry, buffer reads) and token similarity, but missed the global functional differences due to limited context understanding and lack of data flow analysis.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely labeled this as a clone because both functions follow a similar pattern of reading ZIP entries and copying data, which is considered Type-3 similarity despite different output behavior and overall purpose.
- 共享行为: Open a ZipInputStream to read entries from a ZIP file；Iterate over entries using getNextEntry()；Read data from entries and write to output streams；Use buffers for reading/writing data
- 行为差异: Function A extracts entries to individual files; Function B copies entries to another ZIP file；Function A reads from a URL; Function B reads from a local file；Function A does not modify entries; Function B skips one entry and adds a new one；Function B returns a BufferedWriter; Function A has no return value
- 修正建议: Incorporate data-flow and control-dependency information；Add more training examples with nuanced functional differences；Use AST-based or graph-based models to capture structural differences；Include return type and method signature context

### case_id=3218 FP lexical_or_api_overlap

- 方法: `get` vs `createDialogArea`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Makes an HTTP GET request with custom headers, reads response lines, skips comments, decodes GameRecord objects, and returns an array.
- B 摘要: Creates a dialog area with a browser or text widget, reads a license file from a bundle resource, and displays its content.
- 静态失败原因: The model likely overemphasized token overlap (BufferedReader, InputStreamReader, readLine, IOException, e.printStackTrace()) and similar control flow structure, missing the vast semantic difference in purpose and external interactions.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled as non-clone because the functions are from different problem domains (network vs. UI) and share only trivial I/O patterns.
- 共享行为: Both read text line by line from an input stream using BufferedReader
- 行为差异: Purpose: network client vs. UI dialog；A sends HTTP request; B reads local resource file；A parses lines as GameRecord; B concatenates lines as plain text；A uses HttpURLConnection; B uses SWT controls
- 修正建议: Incorporate global context like method signature and surrounding code (class name, imports)；Use a model that captures full semantics beyond token overlap；Add a domain classification step to avoid cross-domain matches

### case_id=3219 FP boilerplate_overlap

- 方法: `getLinksFromURLFast` vs `loadMFileViaWeb`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Opens a URL, reads HTML content, extracts hyperlink URLs and their text using regex, returns two vectors.
- B 摘要: Opens a URL to download a MATLAB script file, reads content line by line, parses it into a UserFunction object, returns it.
- 静态失败原因: Static models like CodeBERT often over-rely on token sequence overlap, especially on common I/O patterns (URL, BufferedReader, readLine), missing the substantial difference in overall function goal.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would not consider these clones because the functional purpose (extracting hyperlinks vs loading a MATLAB function) is fundamentally different, and the code similarity is limited to common I/O boilerplate.
- 共享行为: Both use URL to open a connection；Both use BufferedReader to read lines from the stream；Both perform some post-processing on the read content
- 行为差异: Different input parameters (one URL string vs three parameters)；Different output types and semantics (vectors of links vs UserFunction)；Core logic differs: regex extraction vs function parsing；Error handling: A throws Exception, B catches and logs
- 修正建议: Incorporate global structural features such as method signature, return type, and class context.；Use graph-based models that capture data flow and control flow to distinguish boilerplate from core logic.；Apply contrastive learning to emphasize semantic differences over syntactic similarities.

### case_id=3220 FN partial_functionality

- 方法: `modifyApplicationMessage` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Modifies a specific message in a locale-specific properties file, conditionally copying the English file to the locale file if it does not exist.
- B 摘要: Copies a file from source to destination with a given buffer size and overwrite option.
- 静态失败原因: Low token overlap (0.25) and different method names and overall purposes mask the shared substructure. The copy routine in Function A is a small embedded part, easily overshadowed by the rest of the code. Static models lack the decomposition to recognize the isolated file-copying sub-behavior.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this as a clone because both functions contain a prominent file copy routine that reads from one file and writes to another, which is a common pattern and considered a partial functionality clone. The shared I/O code, though not identical, is similar enough under broad Type-3 criteria.
- 共享行为: Both involve reading input from one file and writing output to another file using streams.；Both close I/O streams in a finally block or after use.
- 行为差异: Function A copies char-by-char using FileReader/FileWriter, whereas Function B copies in byte buffer chunks.；Function A only copies conditionally (if locale file does not exist), while Function B always copies.；Function A then modifies properties file content, Function B does no modification.；Function A uses a specific encoding (characters), Function B is binary-safe.
- 修正建议: Use techniques that decompose functions into smaller operations and compare subroutines.；Incorporate dataflow analysis to identify I/O patterns independent of surrounding logic.；Train models to detect common idioms like file copying across different contexts.

### case_id=3221 FN benchmark_preference_bias

- 方法: `simulate` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Reads a simulation file and processes each line by making SOAP calls to rate users and obtain reputations, printing results and writing to output.
- B 摘要: Downloads a KMZ file from a URL and extracts its contents (unzips) to the local filesystem.
- 静态失败原因: Static model predicted 0 (non-clone), which appears correct; it failed to match BCB's possibly erroneous positive label. If BCB expects a clone, the model may have missed the superficial IO boilerplate similarity.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have considered both as 'file processing with loops' but the functional difference is large; likely a BCB annotation error or extremely broad interpretation.
- 共享行为: Both read from an input stream；Both loop over entries/lines and perform operations；Both close resources after processing
- 行为差异: A's input is a text file of simulation calls; B's input is a zip file from a URL；A makes remote web service calls; B just extracts files locally；A writes a TSV output; B writes extracted files；A uses assertEquals and fail for testing; B does not
- 修正建议: Improve BCB annotation consistency；Re-evaluate if IO boilerplate alone justifies clone

### case_id=3222 FP lexical_or_api_overlap

- 方法: `md5Hash` vs `perform`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.99`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Computes MD5 hash of input string and returns hex string, or null on exception.
- B 摘要: Handles a Struts action to classify a concept via HTTP request, session management, and XML parsing.
- 静态失败原因: Likely due to both functions using try-catch with generic Exception, a common pattern; token overlap is very low but the model may have been misled by shallow syntactic similarity.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clones when functions have no common purpose or behavioral overlap; these two are entirely different tasks.
- 行为差异: Function A is a simple hashing utility; Function B is a complex web request handler.；Function A never uses HTTP, sessions, or XML; Function B uses all of these.；Function B involves multiple external dependencies and data processing; A is self-contained.
- 修正建议: Improve training with more diverse non-clone pairs that share only trivial patterns.；Use dataflow or structure-aware features to differentiate helper utilities from complex controllers.

### case_id=3223 FN partial_functionality

- 方法: `modifyApplicationMessage` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Modifies a properties file for a given locale, copying from English if missing, then updates or adds a message key-value pair.
- B 摘要: Copies a file from input to output using byte streams, returning success status.
- 静态失败原因: The model likely focused on the high-level functionality (modify vs copy) and saw low token overlap (0.21) and different method names, missing the shared file copy sub-task. Static models often fail to recognize partial functionality clones when overall purpose diverges.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB annotators may have considered the file copy sub-operation as sufficient functional similarity, labeling them as Type-4 clones (semantic clones) since both involve reading from one file and writing to another.
- 共享行为: Both perform file copying operations using streams (character/byte).
- 行为差异: A's file copy is conditional and uses character streams; B's copy is unconditional and uses byte streams.；A then modifies properties file content; B just copies bytes.；A writes to a properties file with specific formatting; B writes raw bytes.；A does not return a boolean; B returns success flag.
- 修正建议: Improve model to detect common sub-operations even when embedded in different contexts.；Use data augmentation that creates pairs where one function is a sub-task of the other.；Incorporate bytecode or dataflow analysis to identify file I/O patterns.

### case_id=3224 FN boilerplate_overlap

- 方法: `getFile` vs `saveProject`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies the soap address endpoint, and returns the file path.
- B 摘要: Saves a project by creating directories, copying files, writing metadata, and compressing into a zip.
- 静态失败原因: Static BERT/GraphCodeBERT models rely on token-level similarity and lexical overlap, which is low (Jaccard=0.103). They fail to capture high-level structural patterns like file I/O boilerplate that are not lexically identical. Additionally, long code and different domain-specific APIs confuse the model.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely considers these clones under Type-4 (functional similarity) due to shared file management and I/O patterns, despite different domain purposes. The annotation guidelines may accept broad structural or behavioral overlaps.
- 共享行为: Performs file I/O operations including creating files, reading/writing streams, and deleting temporary files.；Uses FileChannel and FileOutputStream for efficient data transfer.；Handles exceptions with custom error messages.；Concludes with cleanup or finalization steps.
- 行为差异: A downloads and modifies a remote WSDL file; B saves a local project with multiple components.；A returns a String (file path); B returns a boolean (success indicator).；A modifies XML content; B writes many object types to files and creates a zip archive.；A uses URL connection; B interacts with database and multiple layers.
- 修正建议: Use dataflow or control-flow based embeddings to capture I/O patterns.；Incorporate structural similarity via AST or graph features.；Train with contrastive learning on function-level tasks to improve semantic generalization.

### case_id=3225 FN partial_functionality

- 方法: `testNetworkHTTP` vs `startScript`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Test method that makes multiple HTTP requests to various URLs, reading and discarding response lines, with logging.
- B 摘要: Private method that loads a remote script from a URL by reading its lines and appending them to a dialog string.
- 静态失败原因: The low token Jaccard (0.16) and different API usage (openConnection vs openStream), variable names, and surrounding contexts (test vs. dialog) likely caused the model to miss the partial functional similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider the shared pattern of opening a URL, reading lines, and handling IOException as a sufficient functional similarity despite different purposes and multiple vs. single connection.
- 共享行为: Both open a URL and read lines via BufferedReader.；Both handle IOException.
- 行为差异: A makes multiple sequential HTTP connections; B makes only one.；A discards the read data; B accumulates it into a string.；A uses HttpURLConnection with explicit disconnect; B uses URL.openStream() and closes BufferedReader.；A logs and prints stack trace; B prints error and exits.
- 修正建议: Incorporate API call sequence embeddings to capture I/O patterns.；Use graph-based features like control-data flow graphs to highlight structural similarities.；Train on clone pairs with low lexical but high functional similarity.

### case_id=3226 FP boilerplate_overlap

- 方法: `getTicketsForQueue` vs `readURL`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Queries a ticket tracking system for open tickets in a queue, parses ticket IDs from response, and retrieves each ticket.
- B 摘要: Reads a URL and prints its content line by line to standard output.
- 静态失败原因: The static model may have focused on the common boilerplate pattern (try-catch with BufferedReader) and ignored the significant differences in purpose, input/output, and logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels these as non-clones because they perform entirely different tasks despite superficial structural overlap; one is a specific business-logic method, the other is a generic I/O utility.
- 共享行为: Both read data from a network source using a BufferedReader；Both use try-catch-finally for exception handling and stream closing
- 行为差异: Function A constructs and executes an HTTP GET request; Function B directly opens a URL stream；Function A parses lines to extract ticket IDs and ignores non-matching lines; Function B prints every line；Function A makes additional method calls (getTicket) and returns a list; Function B has no return value
- 修正建议: Incorporate method signature and return type information；Use data flow analysis to differentiate core logic from boilerplate；Train on more diverse non-clone pairs with similar structure but different semantics

### case_id=3227 FP lexical_or_api_overlap

- 方法: `doVersionCheck` vs `loadURL`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a version check URL, parses .version and .build lines, and compares with current build to notify user of updates.
- B 摘要: Reads a URL with optional basic authentication, writes content to a temporary file, and updates a status label with file size.
- 静态失败原因: Static BERT models may rely on lexical/API token overlap (e.g., 'URL', 'BufferedReader', 'readLine') and miss the divergent program logic and side effects.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically classifies clones based on overall functional similarity; these two methods have different goals (version checking vs. file downloading) despite sharing URL reading boilerplate, so likely non-clone.
- 共享行为: Open a URL connection；Create BufferedReader from InputStream；Read lines in a while loop
- 行为差异: A parses version and build info; B writes to file and updates status；B handles HTTP basic authentication; A does not；A shows dialog messages; B does not interact with user beyond status label；A deals with version comparison; B deals with file I/O
- 修正建议: Incorporate AST or dataflow representations；Use contrastive learning that penalizes high token overlap but divergent semantics；Include method-level documentation or purpose embeddings

### case_id=3228 FP partial_functionality

- 方法: `getVersion` vs `getPagina`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.85`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches the latest version string from a hardcoded SVN URL.
- B 摘要: Fetches and concatenates all lines from a given URL, returning the full page content.
- 静态失败原因: Static BERT models focus on token sequence and structural patterns, missing the semantic difference in how the read variable is used (overwritten vs concatenated). The high structural similarity and partial token overlap misled the model into classifying as clone.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely labels non-clone because the two functions serve different logical purposes (version retrieval vs generic page fetch) and the output logic differs significantly (single line concatenation vs assignment).
- 共享行为: Both open a URL connection and read lines in a loop.；Both use BufferedReader and InputStreamReader.；Both close the reader in a try block.；Both handle exceptions and return a string.
- 行为差异: getVersion uses a hardcoded URL; getPagina takes a URL parameter.；getVersion overwrites the version variable with each line, returning only the last non-null line; getPagina concatenates all lines into one string.；getVersion returns null on exception; getPagina returns the exception string.；getPagina sets a default Authenticator.
- 修正建议: Incorporate data-flow analysis to track variable usage.；Use contrastive learning on structurally similar but semantically different pairs.；Add heuristics for detecting hardcoded vs parameterized URLs and output construction patterns.

### case_id=3229 FN partial_functionality

- 方法: `main` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a URL, unzips it, and extracts each entry to a file.
- B 摘要: Copies a file from source path to destination path using FileChannel.
- 静态失败原因: Static BERT models rely heavily on token-level overlap (Jaccard 0.14) and structural similarity; the low lexical overlap and different method signatures led to a non-clone prediction, missing the high-level semantic concept of file I/O.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BigCloneBench may consider these clones as both perform file transfer (input to output) operations, accepting partial functionality similarity under Type-4 (semantic) clones.
- 共享行为: Both involve reading from an input source and writing to an output destination.；Both use FileOutputStream for writing.；Both handle exceptions and close streams.
- 行为差异: A downloads from a URL, B copies from a local file.；A processes a zip archive (multiple entries), B copies a single file.；A writes to files named by entry, B writes to a specified destination.；A uses byte-by-byte copying via buffer, B uses FileChannel.transferFrom.
- 修正建议: Incorporate dataflow analysis to track that both functions ultimately copy bytes from input to output.；Use API usage patterns (e.g., InputStream, FileOutputStream) as features.；Train with contrastive learning on positive pairs with low lexical but high semantic similarity.

### case_id=3230 FP lexical_or_api_overlap

- 方法: `actionPerformed` vs `main`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Handles user actions in a GUI settings dialog, updating preferences via file choosers and UI components.
- B 摘要: Reads a file, applies line wrapping and title case filtering, and writes to another file.
- 静态失败原因: The model probably overemphasized common Java APIs (File, IOException) and trivial patterns (return, null checks), mistaking superficial lexical overlap for semantic similarity.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely considers these non-clones due to distinct contexts (GUI settings vs. text filtering) and no functional overlap.
- 共享行为: Both involve file operations (file chooser in A, direct file I/O in B)
- 行为差异: A is a GUI event handler with multiple branches; B is a simple batch filter.；A modifies global preferences and UI; B is stateless.；A interacts with user; B processes arguments.；A has complex conditional logic; B is linear.
- 修正建议: Incorporate control flow and data flow analysis.；Use contrastive learning with hard negatives like this.；Weight API usage context rather than raw token overlap.

### case_id=3231 FP lexical_or_api_overlap

- 方法: `main` vs `test`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Main method that generates Java adapter classes from a Prolog file using a specific framework.
- B 摘要: Test method that verifies the behavior of a StorageStringWriter class, including writing, reading, and exception handling.
- 静态失败原因: Static BERT models may have been misled by shared keywords like 'IOException', 'File', or 'getWriter' which appear in both, but the context and overall purpose are entirely different.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels these as non-clones because they perform completely different tasks with no overlapping semantics or functionality.
- 行为差异: Function A performs code generation, file parsing, and class writing; Function B tests a string storage utility.；Function A has complex control flow with multiple exception handlers and file I/O; Function B is a straightforward unit test.；Function A interacts with Prolog parsing, class loaders, and JAR writing; Function B only uses standard I/O streams and assertions.
- 修正建议: Improve model's ability to understand high-level intent rather than local token overlap.；Use graph-based representations that capture control flow and data dependencies beyond surface tokens.

### case_id=3232 FN benchmark_preference_bias

- 方法: `getFile` vs `copy`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, optionally modifies an XML attribute, and saves it to a temporary location, returning the file path.
- B 摘要: Copies a file from a source path to a destination path using a memory-mapped buffer and FileChannel.
- 静态失败原因: The static BERT model likely relied on token-level and structural similarity, which is low (Jaccard 0.128). It correctly judged non-clone based on lexical differences, but BCB's annotation might have expected recognition of a shared high-level I/O pattern that static models miss without semantic understanding of file copy operations.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider both as performing a 'copy' operation (source to destination) using FileChannel, viewing the network download in A as just an alternative source. This broad Type-4 interpretation focuses on the core I/O pattern rather than the overall functionality.
- 共享行为: Both create File objects and use FileChannel for file I/O；Both handle IOException (though A wraps it in AxisFault)；Both involve reading from an input source and writing to an output file
- 行为差异: A downloads from a network URL; B copies from a local file；A includes XML parsing and attribute modification; B does not；A creates temporary files and uses multiple exception handlers; B is simpler；A returns a String; B is void
- 修正建议: Incorporate data-flow analysis to detect source-to-destination transfer operations；Use program slicing to isolate core I/O patterns；Train on more nuanced partial functionality clone pairs

### case_id=3233 FP lexical_or_api_overlap

- 方法: `SRWGuiClient` vs `checkForUpgrade`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.99`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Constructor for SRWGuiClient that sets up a web browser GUI, loads XML from a URL, optionally applies XSLT transformation, and displays the result.
- B 摘要: Static method that checks for software upgrades by querying a remote server, parsing license and upgrade information, updating a local database, and showing download/restart UI.
- 静态失败原因: Static BERT/GraphCodeBERT likely relied on lexical overlap of common Java networking APIs (URL, BufferedReader, InputStream) and structural patterns (opening connection, reading lines) without capturing the divergent intent and behavior.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels non-clones when functions have completely different high-level purposes and only share superficial API usage. Here, A is a browser GUI constructor, B is an upgrade checker, so they are not functionally similar.
- 共享行为: Both use URL, URLConnection, and BufferedReader to read data from a remote server；Both parse lines of input using while loops；Both manipulate UI components
- 行为差异: Function A is a constructor initializing a browser GUI, while Function B is a static method for upgrade checking；A performs XML and XSLT processing, B parses license and upgrade data；B executes SQL queries and updates a database, A does not；A sets up a JEditorPane with HTML, B hides/shows specific UI components and shows messages
- 修正建议: Incorporate method and class name embeddings to capture domain context；Use more comprehensive semantic features like data flow and call graph；Train on more diverse examples of similar API usage with different semantics

### case_id=3234 FP lexical_or_api_overlap

- 方法: `doRawRequest` vs `get`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Sends a POST request with raw data and returns the response body as a string.
- B 摘要: Sends a GET request with custom headers, parses the response into GameRecord objects, and returns an array or null on failure.
- 静态失败原因: The static model relied on surface-level lexical overlap (e.g., 'URL', 'openConnection', 'BufferedReader', 'readLine') and common boilerplate patterns, ignoring the semantic differences in HTTP method and data handling.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically treats Type-4 clones as functionally similar. While both make HTTP requests, the differences in HTTP method, parameterization, and output processing make them functionally distinct, so BCB labels them as non-clones.
- 共享行为: Both open an HTTP connection to a URL.；Both read the response line-by-line with a BufferedReader.
- 行为差异: Method A uses POST; method B uses GET.；Method A sends arbitrary data; method B sets specific headers.；Method A returns the raw response string; method B parses lines into GameRecord objects.；Method A has no error handling; method B checks HTTP_OK and catches exceptions.
- 修正建议: Incorporate data-flow analysis to distinguish HTTP methods.；Use more diverse training data with varied HTTP usage.；Add attention mechanism to focus on method-specific keywords like 'GET' vs 'POST'.

### case_id=3235 FN partial_functionality

- 方法: `main` vs `write`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Extracts all entries from a remote ZIP file to local files.
- B 摘要: Writes a JAR file by combining entries from multiple JAR files, filtering out manifest and zero-size entries.
- 静态失败原因: The static model likely focused on low token overlap (0.14) and different method names/signatures, missing the high-level structural similarity of archive entry processing.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considers both as archive manipulation tasks (zip/jar entry iteration and copying), which are considered clones under broad Type-3/Type-4 similarity for partial functionality.
- 共享行为: Iterate over entries in a ZIP/JAR archive；Copy entry data to an output stream
- 行为差异: A extracts individual files to disk; B aggregates entries into a single JAR output stream；A does not filter entries; B filters out MANIFEST.MF and zero-size entries；A reads from a single URL; B reads from multiple JAR files
- 修正建议: Increase training data with archive entry processing variations；Use a model that captures structural patterns like loops and I/O operations

### case_id=3236 FN partial_functionality

- 方法: `runInternal` vs `postRequest`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads and parses OPDS catalog or book from a URL, with pagination and progress tracking.
- B 摘要: Sends an HTTP POST request with form data and returns the response as a string.
- 静态失败原因: Static BERT models like GraphCodeBERT rely on token-level similarity and may have been misled by the low token Jaccard (0.13) and different API usage patterns, failing to recognize the high-level functional similarity of HTTP communication.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as clones because they are both HTTP request functions that perform network I/O, set up connections, and read responses, aligning with Type-4 (functionally similar but syntactically different) criteria.
- 共享行为: Both open a URLConnection to communicate over HTTP；Both read input from the connection's input stream；Both handle exceptions with try-catch blocks
- 行为差异: A uses HTTP GET (implied), B uses HTTP POST with output；A handles redirects, content disposition, and pagination, B does not；A interacts with a complex handler for parsing, B returns raw string；A runs in a do-while loop for multiple pages, B is single request
- 修正建议: Enhance training data with diverse pairs of HTTP/network operations；Incorporate data flow or control flow features to capture high-level behavior；Use contrastive learning to focus on functional similarity over syntactic overlap

### case_id=3237 FN benchmark_preference_bias

- 方法: `doGet` vs `fileCopy`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Handles HTTP GET requests to retrieve and display a page, with logging, permission checks, and optional caching.
- B 摘要: Copies a file from source to destination, with validation of file existence and permissions.
- 静态失败原因: The model likely correctly predicted non-clone due to low token overlap and different domains; the BCB label may be an error or bias.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as a clone due to the presence of file I/O operations in both functions (e.g., writing to a temporary file in doGet), but the overall functionality is drastically different.
- 共享行为: Both perform input/output operations
- 行为差异: doGet is a web request handler; fileCopy is a file utility；doGet involves complex business logic with page properties and user permissions; fileCopy is straightforward file I/O；doGet uses HTTP request/response objects; fileCopy uses FileInputStream/FileOutputStream
- 修正建议: Incorporate domain-specific knowledge；Use finer-grained semantic similarity measures；Require functional pipeline matching instead of surface-level I/O patterns

### case_id=3238 FN partial_functionality

- 方法: `register` vs `postXml`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Registers a user by encoding password, setting metadata, calling a phpBB registration URL, persisting to database, and sending confirmation email.
- B 摘要: Sends an XML SOAP request over HTTP POST and returns the response string.
- 静态失败原因: Static BERT/GraphCodeBERT models rely on token overlap and local structural patterns. The low Jaccard similarity (0.185) and different method names, parameters, and domain-specific logic lead to a low similarity score, missing the broad functional similarity BCB considers.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this as clone due to both functions involving HTTP requests and reading responses, considering it a broader functional similarity (Type-4) despite different domains.
- 共享行为: Both open a URL connection and read the response line by line.；Both handle IOException.
- 行为差异: A performs user registration logic (password encoding, date setting, authority, hash generation), while B is a generic SOAP client.；A modifies persistent state (database and email), B returns a string with no side effects.；A uses HTTP GET (via URL parameters), B uses HTTP POST with headers.；A includes error handling for MailException and NumberFormatException, B only for IOException.
- 修正建议: Incorporate high-level functional semantics (e.g., 'makes HTTP call') via code summarization or API usage patterns.；Use data flow analysis to match I/O behavior (e.g., URL connections, streams) across functions.；Augment training data with examples of functional clones with low lexical overlap.

### case_id=3239 FN partial_functionality

- 方法: `extractResourceToFile` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Extracts a resource from classpath to a destination file by copying the input stream to a file output stream.
- B 摘要: Retrieves a resource as an InputStream with local caching, HTTP support, and fallback to cached file if available.
- 静态失败原因: Low token overlap (Jaccard=0.13) and differing control flow structures; static models may miss long-range dependencies and the overall behavioral difference due to high lexical variance.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label as clone due to both being resource-loading utilities, possibly considering them as Type-4 (functionally similar) even though their implementations and signatures differ significantly.
- 共享行为: Both involve accessing a resource from a classpath or remote URL.；Both use streams to read resource data.
- 行为差异: Function A writes resource to a file; function B returns an InputStream (or null).；Function B implements caching logic and HTTP conditional GET; function A does not.；Function B has much more complex control flow (HTTP status checking, cache lookup).；Function A uses IOUtils.copy; function B manually reads bytes in a loop.
- 修正建议: Incorporate structural features like control flow graph diffs.；Use contrastive learning on method signatures and return types.；Leverage code summarization to capture high-level intent.

### case_id=3240 FP lexical_or_api_overlap

- 方法: `loadSourceCode` vs `sendPost`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a file from a resource, applies syntax highlighting, and builds an HTML preformatted string.
- B 摘要: Sends an HTTP POST request with parameters and returns the response body as a string.
- 静态失败原因: Static BERT may have overemphasized shared API tokens (URL, BufferedReader, InputStreamReader) and structural similarity (try-catch, while loop with readLine), ignoring the distinct functional contexts (local resource vs. HTTP connection).
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clone because the high-level functionality is completely different: one is for source code display, the other for HTTP client operations. Common I/O boilerplate does not justify a clone label.
- 共享行为: Both use BufferedReader to read lines from an input stream in a loop.；Both use try-catch blocks to handle exceptions.；Both build a result string by concatenating lines.
- 行为差异: A reads from a local file/resource, B reads from an HTTP response.；A produces HTML output, B returns plain text.；A uses URL.openStream(), B uses HttpURLConnection with POST.；A has void return, B returns the result string.
- 修正建议: Incorporate broader context such as method name and return type.；Use data flow analysis to distinguish the origin of the input stream.；Add negative sampling with similar boilerplate but different functionality.

### case_id=3241 FP lexical_or_api_overlap

- 方法: `callApiPost` vs `getFrameworkFactory`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Makes an HTTP POST request to a given URL with parameters and returns the response input stream.
- B 摘要: Loads an OSGi FrameworkFactory from a service configuration file and returns an instance.
- 静态失败原因: Static models like GraphCodeBERT may over-rely on token overlap (e.g., 'URL', 'InputStream', 'IOException', 'BufferedReader') and structural patterns (try-catch, loops) without capturing semantic context. The model likely saw similar API usage patterns and incorrectly classified them as clones.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels true clones only when functions share substantial functional similarity (e.g., both implement similar algorithms or I/O patterns with same intent). Here the functions serve completely different purposes despite some lexical overlap, so BCB correctly labels them as non-clones.
- 共享行为: Both use URL and handle input streams；Both perform resource reading and exception handling
- 行为差异: Different network operations: POST request vs file reading；Different return types: InputStream vs FrameworkFactory；Different error handling: custom BingMapsException vs generic Exception；Different purpose: API call vs service loader
- 修正建议: Incorporate semantic role labeling or domain knowledge；Enhance training with more diverse non-clone pairs that share API tokens but differ in behavior；Use graph representation that captures data flow differences (e.g., POST vs getResource)

### case_id=3242 FP lexical_or_api_overlap

- 方法: `readZoneIDs` vs `fetchUrl`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads integers from a resource file and returns a set.
- B 摘要: Fetches the content of a URL and returns the concatenated lines as a string.
- 静态失败原因: Static BERT/GraphCodeBERT likely relied on surface-level token overlap (URL, readLine, InputStreamReader) and structural pattern similarity (try-catch, loop), but missed the semantic difference in output type and transformation.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clones when functions have different output types and different logical transformations, despite sharing I/O boilerplate. Here, extracting integer IDs vs fetching raw text are different functionalities.
- 共享行为: Both open an input stream from a URL.；Both read lines in a loop until null.；Both use similar exception handling (catch Exception / catch MalformedURLException, IOException).
- 行为差异: Function A returns a HashSet of integers, Function B returns a StringBuilder-concatenated string.；Function A reads integers from each line, Function B appends raw line strings.；Function A uses LineNumberReader, Function B uses BufferedReader.
- 修正建议: Train with more emphasis on output type and final transformation.；Incorporate data flow analysis to distinguish integer parsing vs string concatenation.；Use contrastive learning with pairs that have similar I/O structure but different semantics.

### case_id=3243 FN benchmark_preference_bias

- 方法: `main` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a URL and extracts its zip entries to files in the current directory.
- B 摘要: Copies a single file from source to destination using NIO FileChannel with synchronization.
- 静态失败原因: Static BERT/GraphCodeBERT models rely on token overlap and structural similarity. The low token Jaccard (0.116) indicates very few shared tokens. Additionally, the functional difference (zip extraction vs. file copy) may be lost on static models that focus on local patterns. The model correctly predicted non-clone based on low similarity, but BCB's broader annotation favors I/O pattern similarity.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as a clone because both functions perform file I/O operations (reading and writing) and use similar low-level APIs like InputStream, OutputStream, FileChannel, and close resources. The general pattern of opening, transferring, and closing could be considered a broad Type-3 or Type-4 clone.
- 共享行为: Both perform file I/O operations involving reading from a source and writing to a destination.；Both handle file system resources and close them.
- 行为差异: Function A downloads from a URL and handles zip extraction; function B copies a single file.；Function A uses ZipInputStream with multiple entries; function B uses FileChannel for direct transfer.；Function A prints progress; function B returns boolean.
- 修正建议: Incorporate high-level functional categories (e.g., file I/O, data transfer) into model training.；Use semantic embeddings that capture overall purpose rather than token-level similarity.；Consider API-level abstraction to group similar operations.

### case_id=3244 FN partial_functionality

- 方法: `main` vs `register`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Opens a hardcoded URL and prints its content line by line.
- B 摘要: Registers a user by validating input, encoding password, setting metadata, connecting to a phpBB forum URL to create the user, persisting the user, and sending a confirmation email.
- 静态失败原因: Static BERT models like GraphCodeBERT rely on token sequences and structure; the low token Jaccard (0.117) and vastly different contexts caused the model to miss the shared URL-reading snippet. The model likely over-generalized differences in overall semantics.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BigCloneBench often annotates clones based on shared functionality fragments. Even though the overall purposes differ, both functions contain a similar pattern of opening a URL, reading lines, and closing, which is a non-trivial commonality. This qualifies as a Type-4 clone under BCB's broad criteria.
- 共享行为: Both open a URL and read lines using BufferedReader.；Both close the reader after reading.
- 行为差异: A is a main method with no return; B is a registration method that returns a boolean.；B includes extensive validation, password encoding, database persistence, and email sending.；A uses a fixed URL; B constructs a dynamic URL with user parameters.；B handles multiple exceptions and logs errors; A does not.
- 修正建议: Incorporate subgraph or sub-sequence matching to detect common API usage patterns.；Use dataflow analysis to identify similar I/O patterns even when surrounding code differs.；Train with partial clone examples that share functionality but differ in context.

### case_id=3245 FN partial_functionality

- 方法: `process` vs `doGet`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Generates files from templates based on destination (target/source/redora) and type (freemarker/xslt/copy), with error handling and logging.
- B 摘要: Handles HTTP GET requests to retrieve a page by name or ID, checks user permissions, logs requests, and renders the page with caching.
- 静态失败原因: Static BERT models rely on token similarity and local context. They may have picked up on common tokens like 'try', 'catch', 'IOException', 'logger', 'file', 'page', and 'Property', leading to misleading similarity. The models lack understanding of the larger program logic and domain-specific semantics (template generation vs HTTP handling).
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB might have labeled as clone because both methods have a similar structure: a sequence of conditional branches, IO operations, and error handling. However, the core functionality is entirely different, so this broad structural overlap likely led to a false positive clone annotation.
- 共享行为: Both involve reading configuration: template destination vs page properties.；Both write output: to file vs HTTP response.；Both handle exceptions and log errors.；Both have conditional logic and loops.
- 行为差异: A generates code files from templates; B serves web pages via HTTP.；A uses template engines (FreeMarker, XSLT, copy); B uses page objects and user permissions.；A deals with file paths and package names; B deals with request parameters and response objects.；A has no user authentication; B has visibility and permission checks.
- 修正建议: Incorporate dataflow analysis to track the core data transformations (template to file vs request to page).；Use type information to distinguish file operations from HTTP operations.；Add domain-specific features such as API calls (e.g., 'getTemplate', 'getPage') to differentiate.；Consider call graphs or API-level embeddings that capture purpose.

### case_id=3246 FN benchmark_preference_bias

- 方法: `main` vs `readAndRewrite`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `preference_memory_with_manual_audit`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a URL and extracts its Zip entries to files.
- B 摘要: Reads a DICOM image file, parses it, and rewrites it to a new file.
- 静态失败原因: Static BERT models rely on token overlap and syntactic similarity; low Jaccard index and different API calls (ZipInputStream vs DcmParser) yielded low similarity, missing abstract functional commonality.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may label them as Type-4 clones because both follow a generic 'read-process-write' pattern with I/O streams and console logging, despite different domains.
- 共享行为: Both read from an input stream；Both write output to files；Both use buffered streams；Both print progress messages
- 行为差异: Input source: URL vs local file；File format: KMZ/Zip vs DICOM；Processing: extract entries vs parse and re-encode；Output: multiple extracted files vs single rewritten file
- 修正建议: Incorporate dataflow analysis to capture abstract I/O patterns；Use clone detection that explicitly targets Type-4 or functional similarity；Augment training with examples of structurally different but functionally similar code

### case_id=3247 FN partial_functionality

- 方法: `transformSingleFile` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Transforms an X3D file by compressing it into GZIP format, handling exceptions and user feedback.
- B 摘要: Builds a website for editing by processing multiple pages, applying XSLT-like transformations, and writing output files with error handling.
- 静态失败原因: The static BERT model correctly predicted non-clone based on very low token Jaccard similarity (0.06) and distinct method names, but failed to capture the broad functional similarity in file I/O and transformation tasks that BCB may have overestimated. The model likely relied on lexical and structural overlap, which was insufficient to recognize a clone under BCB's lenient criteria.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled this as a clone due to both methods being 'transformation' actions that involve reading input files, writing output files, and handling I/O exceptions. The presence of common Java I/O classes (FileInputStream, FileOutputStream) and structural patterns (try-catch, loops over buffers) could lead BCB to consider them Type-3/Type-4 clones with partial functional similarity, despite different domains.
- 共享行为: Both functions perform file I/O operations (reading input, writing output) using Java streams.；Both involve exception handling with try-catch blocks.；Both use debugging/tracing messages.；Both manipulate string buffers or byte buffers.
- 行为差异: Function A processes a single file with GZIP compression; Function B processes multiple pages with site-building logic.；Function A uses GZIPOutputStream and byte buffers; Function B uses StringWriter, char buffers, and XML/HTML transformations.；Function A returns a file path; Function B is void and throws exceptions.；Function A has a listener for progress messages; Function B uses a DebugFile for tracing.
- 修正建议: Incorporate data flow analysis to detect shared patterns in I/O operations and exception handling.；Use semantic role labeling or method-level embeddings to capture high-level purpose (e.g., 'transform file') beyond API calls.；Calibrate model threshold for Type-3/Type-4 clones by training on BCB's broad annotations.

### case_id=3248 FN partial_functionality

- 方法: `copyFile` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.2`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Copies a file from source to destination using NIO channels.
- B 摘要: Launches an Eclipse launch configuration for a NexOpen project, involving reading/modifying XML, setting properties, copying a resource file, and scheduling an install action.
- 静态失败原因: Static BERT/GraphCodeBERT models rely on lexical and syntactic overlap, and this pair has very low token similarity (Jaccard 0.028). The models fail to capture the semantic similarity of file copying because the code structures are completely different.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider that both functions perform file copying as a key behavior, and in clone detection, if a function A does X and function B does X as part of its task, they could be considered partial functionality clones.
- 共享行为: Both involve file operations, specifically copying a resource file from a bundle to a project directory.
- 行为差异: A solely copies a file; B has many other steps including XML processing, property setting, and project installation.；A uses NIO channels; B uses streams and string replacement.；A is generic; B is specific to Eclipse/NexOpen context.；A returns void; B is void but throws CoreException.
- 修正建议: Improve tokenization to capture high-level semantics like file operations.；Use graph-based models to capture data flow of file creation/copying.；Include more training data with partial functionality clones.

### case_id=3249 FP partial_functionality

- 方法: `main` vs `downloadModel`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads content from a URL and prints each line to console.
- B 摘要: Downloads an RDF model from a URL, handling HTTP headers, and returns the model.
- 静态失败原因: Static BERT likely over-focused on lexical and API-level overlap (URL, InputStream, readLine vs read) and failed to capture the differing purposes and result types.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB labels this as non-clone because the high-level functionality differs: one prints web content, the other downloads a structured RDF model.
- 共享行为: Both open a URL connection and read from an input stream
- 行为差异: A prints lines to console; B returns a Model object；A uses URL.openStream() directly; B sets HTTP request properties and handles connection types；A has no error handling; B catches MalformedURLException and IOException
- 修正建议: Incorporate data-flow analysis to distinguish output consumption；Train on more diverse negative examples with similar API usage but different intent

### case_id=3250 FP boilerplate_overlap

- 方法: `handleHandshake` vs `readZoneIDs`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Handles handshake by validating username and performing HTTP authentication with Minecraft session server.
- B 摘要: Reads zone IDs from a resource file and returns a set of integers.
- 静态失败原因: GraphCodeBERT likely over-emphasized the overlapping boilerplate code (try-catch with printStackTrace, URL.openStream, readLine) and ignored the different overall functionality, method names, and class contexts.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled non-clone because the two functions have completely different purposes and contexts, despite superficial structural similarities like try-catch and URL usage.
- 共享行为: Both use URL.openStream() to read data from a stream；Both have try-catch blocks that call printStackTrace() on exception；Both read lines from the input stream
- 行为差异: Function A performs network authentication; Function B reads a local resource file；Function A uses a handshake packet as input; Function B uses a file name string；Function A returns void and potentially sends packets; Function B returns a HashSet<Integer>；Function A has validation logic and conditional branching; Function B has a simple loop
- 修正建议: Enhance model to consider method and class names for context；Incorporate data flow analysis to distinguish different data manipulations；Train on more diverse examples to reduce sensitivity to common boilerplate patterns

### case_id=3251 FN partial_functionality

- 方法: `runInternal` vs `doVersionCheck`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads and processes OPDS catalog items from a URL, handling pagination and various content types.
- B 摘要: Fetches a version file from a URL and checks if a new build is available.
- 静态失败原因: Low token overlap (Jaccard 0.12) and different method names/contexts cause static models to rely on lexical similarity, missing the shared network I/O semantics.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely labels these as Type-4 clones because both functions encapsulate the high-level pattern of 'fetch data from URL and process text', despite significant differences in specific logic and purpose.
- 共享行为: Both open a URL connection to retrieve remote data.；Both read an input stream and parse text content line by line.；Both perform actions based on the parsed content (e.g., displaying results or updating UI).
- 行为差异: A handles HTTP redirects, content-disposition, and complex pagination; B does not.；A supports multiple content types (e.g., OPDS, downloads); B only reads a simple version file.；A includes progress indicators and error handling for missing resources; B uses a simpler error dialog.
- 修正建议: Incorporate dataflow analysis to detect common API usage patterns (e.g., URL.openStream, BufferedReader).；Use code summarization or abstraction techniques to capture high-level intent beyond syntax.

### case_id=3252 FN lexical_or_api_overlap

- 方法: `doGet` vs `readAndRewrite`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.1`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Handles HTTP GET requests to retrieve a page by ID or name, applies access control, logs requests, and writes the rendered page output, with caching.
- B 摘要: Reads a DICOM image file, parses its dataset up to PixelData, then writes the dataset and pixel data to an output file.
- 静态失败原因: The model correctly identified non-clone; it failed in the sense of BCB's label, likely due to low token overlap and different API usage, but this is actually correct behavior.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may label this as a Type-4 clone based on a very broad interpretation of 'reading and writing data' or 'I/O operations', but the functions share no meaningful functional similarity.
- 共享行为: Both involve reading input and writing output, but with different data types and protocols.
- 行为差异: Different domains: web server vs. medical image processing.；Different I/O: HTTP request/response vs. file streams.；Different data formats: HTML/HTTP vs. DICOM.；Different error handling: extensive try-catch in A, none shown in B.
- 修正建议: No fix needed; the model prediction is accurate.

### case_id=3253 FN benchmark_preference_bias

- 方法: `save` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Writes byte array to a file using IOUtils.copy and handles cleanup.
- B 摘要: Builds a site for editing by transforming XML pages and writing multiple output files.
- 静态失败原因: The static model correctly identified them as non-clones due to low lexical overlap (Jaccard=0.051) and different structure; the model did not fail; the BCB label is questionable.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled as clone due to both performing file output operations (Type-4 similarity), but this is a very broad interpretation; likely an annotation error.
- 共享行为: Both involve writing data to files；Both handle IOException
- 行为差异: Function A is a simple static utility; B is a complex instance method with many parameters；A writes a single file; B writes multiple files after extensive processing；A uses IOUtils; B uses custom FileSystem and XML transformers；A has no loops or conditionals; B has loops over pages and multiple conditions
- 修正建议: Review BCB annotation for potential mislabeling；Ensure clone pairs require more meaningful semantic overlap

### case_id=3254 FP boilerplate_overlap

- 方法: `readData` vs `upload`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Reads configuration data from static strings and a file to initialize various sets and maps for Tibetan transliteration processing.
- B 摘要: Uploads an image file to a destination directory and returns 'show'.
- 静态失败原因: The model likely overfitted on boilerplate tokens like 'File', 'IOException', 'try', 'catch', 'new', and 'String', which appear in both functions, despite very low token overlap (Jaccard 0.0327). The long and complex nature of function A may have caused the model to latch onto superficial similarities.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would label these as non-clones because they serve entirely different functional purposes. Even broad Type-4 similarity requires some common behavioral goal, which is absent here; only trivial boilerplate (file I/O, exception handling) overlaps.
- 共享行为: Both involve file I/O with exception handling (try-catch for IOException)
- 行为差异: A initializes multiple data structures from tokenized strings and a formatted file; B simply copies a file stream.；A has extensive parsing logic with loops and conditionals; B has minimal logic.；A modifies global static state; B does not alter state beyond file copy.；A returns void; B returns a String.
- 修正建议: Incorporate control-flow or data-flow features to distinguish parsing-heavy code from simple I/O.；Use structure-aware embeddings (e.g., GraphCodeBERT) that capture richer semantic roles beyond token co-occurrence.；Add global context or method-level summary to reduce sensitivity to minor local patterns.

### case_id=3255 FN benchmark_preference_bias

- 方法: `modifyApplicationMessage` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Reads or creates a locale-specific properties file, searches for a message key, and modifies or appends the key-value pair.
- B 摘要: Copies a file from source to destination using FileChannel for efficient I/O.
- 静态失败原因: Static BERT models may rely on lexical overlap, which is very low here. They likely correctly identified this as non-clone due to distinct method names and low token similarity, but the BCB label contradicts.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled these as clones due to both being file manipulation routines, but the functional purpose and complexity differ substantially. This appears to be a potential annotation error.
- 共享行为: Both perform file I/O operations；Both handle file resources (open/close channels/streams)
- 行为差异: Function A reads/parses a properties file and modifies a specific entry; Function B simply copies the entire file；Function A involves conditional logic and string manipulation; Function B uses a direct transfer；Function A handles multiple file streams and character encoding; Function B uses binary channel transfer
- 修正建议: Review BCB annotation to verify if these truly should be clones；If not, update the benchmark to remove this false positive；Improve model robustness against functional dissimilarity despite same-domain I/O

### case_id=3256 FN partial_functionality

- 方法: `modifyApplicationMessage` vs `getFileContentAsString`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Modify a locale-specific properties file by updating or adding a message entry.
- B 摘要: Read a file from classpath or filesystem and return its content as a string.
- 静态失败原因: Static BERT models like GraphCodeBERT rely on token-level and structural patterns. Despite low Jaccard similarity, both snippets contain common I/O boilerplate (InputStream, FileReader, try-catch) and classloader calls, which can mislead the model into thinking they are similar. However, the model correctly predicted non-clone (0), indicating it captured the semantic difference.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider them clones due to both involving file I/O operations and classpath resource loading, which is a common pattern. However, the functional purpose differs significantly; BCB's criteria might be too broad here or the label is a benchmark error.
- 共享行为: Both read files from classpath or filesystem.；Both use InputStream and handle exceptions related to file I/O.；Both involve resource loading using class loaders.
- 行为差异: Function A modifies and writes to properties files, while B only reads.；A is specific to configurations and locale handling; B is generic file reading.；A copies a default file if the target doesn't exist; B does not.；A parses and modifies lines in a file; B just copies raw bytes.
- 修正建议: Train the model on more examples that distinguish file reading from file modification.；Incorporate richer semantic context beyond token overlap, such as data-flow analysis or distinguishing between read and write operations.

### case_id=3257 FN benchmark_preference_bias

- 方法: `convert` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Converts an ACRNEMA stream file to DICOM format, handling pixel data and UIDs.
- B 摘要: Launches a NexOpen project configuration in Eclipse, processing Maven pom.xml files and setting up Hibernate.
- 静态失败原因: Static BERT likely correctly identified low token overlap (Jaccard=0.058) and domain differences, so it predicted non-clone. The error is likely a mislabel in BCB rather than a model failure.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled as clone due to both functions being file-processing utilities with similar control flow patterns (e.g., try-finally, conditional branches), but this is a weak analogy.
- 共享行为: Both perform file I/O operations；Both use conditionals and loops；Both handle exceptions
- 行为差异: Function A is a DICOM conversion; Function B is an Eclipse launch configuration；Function A writes binary pixel data; Function B modifies XML and properties；Function A has no UI dependency; Function B relies on Eclipse workspace
- 修正建议: Ensure BCB annotation guidelines are consistently applied；Cross-check with domain experts for ambiguous pairs

### case_id=3258 FN benchmark_preference_bias

- 方法: `convert` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Converts ACRNEMA stream files to DICOM format by parsing pixel data and adding UIDs.
- B 摘要: Launches a NexOpen project by configuring Maven POMs and Hibernate dialect for reverse engineering.
- 静态失败原因: Static BERT/GraphCodeBERT likely predicted non-clone due to low lexical overlap (Jaccard 0.058) and completely different API calls (DICOM vs Eclipse/Hibernate), indicating it correctly identified functional dissimilarity.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as clone due to both functions involving file processing and I/O operations, such as reading from input streams and writing to output streams, and using try-finally blocks, which could be seen as Type-4 semantic similarity (similar I/O patterns) despite different domains.
- 共享行为: Both involve file I/O operations (reading input, writing output).；Both use try-finally for resource cleanup.
- 行为差异: A is a DICOM conversion tool; B is an IDE launch configuration handler.；A manipulates binary pixel data; B manipulates XML and project properties.；A uses DICOM-specific tags and formats; B uses Maven and Hibernate-specific APIs.；A has no external dependencies besides DICOM library; B depends on Eclipse and NexOpen frameworks.
- 修正建议: Improve BCB annotation guidelines to exclude such broad I/O similarity as clones.；Incorporate domain-specific knowledge to distinguish between different application contexts.

### case_id=3259 FN partial_functionality

- 方法: `executeHttpGet` vs `seeURLConnection`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Executes an HTTP GET request using Apache HttpClient and returns the response as a JSONObject.
- B 摘要: Opens a URL connection to a hardcoded URL, reads the response line by line, and logs it to debug.
- 静态失败原因: Static models may focus on token-level differences (e.g., different API imports, return types, hardcoded URL vs parameter) and miss the underlying shared behavior pattern, leading to a non-clone prediction.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often considers partial functionality similarity, such as the core pattern of 'HTTP GET and read response', as sufficient for a clone label despite differences in output and API used.
- 共享行为: Both perform an HTTP GET request and read the response line by line into a buffer.
- 行为差异: A uses Apache HttpClient, B uses java.net.URLConnection；A returns JSONObject, B logs and returns void；A takes a URI parameter, B uses a hardcoded URL；B closes the BufferedReader, A does not
- 修正建议: Train models to recognize common functional patterns across different APIs and return types；Incorporate abstract representations (e.g., data flow graphs) that capture the core behavior；Use data augmentation with similar tasks to improve generalization

### case_id=3260 FP boilerplate_overlap

- 方法: `getWebByUrl` vs `getFullScreenUrl`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Downloads a web page from a URL and saves it to a local file, with deep crawling of links.
- B 摘要: Extracts a fullscreen video URL from a YouTube page by parsing specific parameters.
- 静态失败原因: Static BERT models rely on lexical and structural overlap; both functions share boilerplate code (URL, URLConnection, BufferedReader, try-catch) leading to high similarity in token sequences despite different functionalities.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels non-clone because the functions have distinct semantic goals: one downloads and saves web pages, the other extracts YouTube video metadata.
- 共享行为: Open URL connections and read input streams；Use BufferedReader and InputStreamReader；Set URLConnection doOutput to true；Catch exceptions with try-catch blocks
- 行为差异: Function A writes to a file and performs deep crawling; Function B returns a constructed URL；Function A processes all lines; Function B searches for a specific line containing 'fullscreenUrl'；Function A uses external fields like fPath, deepUrls, webDepth; Function B uses ytUrl, progressDown, ytTitle；Return type: void vs String
- 修正建议: Integrate dataflow and control-flow features to distinguish generic I/O patterns from specific business logic；Include method signature and field usage in embeddings；Train on more diverse examples to reduce bias towards common API usage patterns

### case_id=3261 FN partial_functionality

- 方法: `getFile` vs `copy`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.65`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies an XML attribute, and saves to temp directory, with error handling.
- B 摘要: Recursively copies a file or directory to a destination, skipping .svn subdirectories and using last-modified check to skip unchanged files.
- 静态失败原因: The low token Jaccard similarity (0.136) and lack of overlapping key identifiers or control flow patterns caused the model to confidently classify as non-clone, missing the possibly intended broad functional similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this as a Type-4 clone based on a very broad theme of 'data transfer/copy' operations, ignoring the specific contexts (network download vs file copy) and divergent internal logic.
- 共享行为: Both perform file I/O operations (reading from a source and writing to a destination).；Both involve copying data from one location to another (network to file vs file to file).
- 行为差异: A downloads from a network URL and modifies XML; B copies local files/directories recursively.；A includes XML parsing and attribute modification; B does not.；A uses NIO channels and streams; B uses byte array buffered streams.；A has extensive exception handling for malformed URL, IO, parser, SAX; B only throws IOException.
- 修正建议: Incorporate functional semantics via code summarization or AST-based features to capture high-level intent (e.g., both 'download' and 'copy' are 'data transfer').；Use fine-tuning with BCB's Type-4 labels to learn broader notions of clone.

### case_id=3262 FN boilerplate_overlap

- 方法: `wordFrequency` vs `seeURLConnection`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches a web page, replaces a placeholder with a given word, searches for a line matching a pattern, and extracts an integer frequency.
- B 摘要: Fetches a hardcoded web page and logs the entire response as a string.
- 静态失败原因: The token Jaccard similarity is low (0.2069) because the specific keywords (replaceFirst, matches, pattern, etc. vs. logging) differ. Static BERT/GraphCodeBERT models heavily rely on token overlap and may miss high-level structural similarity that BCB favors.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB often labels Type-3 clones where two methods share a common boilerplate pattern, even if the core functionality differs. Both functions perform a URL connection and line-by-line reading, which is a recognizable pattern.
- 共享行为: Both open a URL connection and create a BufferedReader to read lines；Both read lines in a while loop；Both potentially handle or declare IOExceptions
- 行为差异: A uses dynamic URL replacement based on input word; B uses a fixed URL；A searches for a specific pattern and returns an integer; B simply concatenates all lines into a StringBuffer and logs it；A returns 0 on failure; B has void return and throws Exception；A uses try-catch blocks; B throws exception out
- 修正建议: Use a clone detector that focuses on control flow or data flow graphs rather than pure token overlap；Incorporate structural similarity metrics like tree-based matching or graph kernels；Normalize boilerplate code (e.g., URL reading patterns) before token comparison

### case_id=3263 FN partial_functionality

- 方法: `doGet` vs `logging`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.2`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Handles HTTP GET requests to retrieve and render a portal page, including access control, logging, and caching.
- B 摘要: Logs inbound SOAP message details (encoding, headers, content) with optional truncation and temporary file storage.
- 静态失败原因: A static BERT/GraphCodeBERT model likely correctly predicted non-clone because the token overlap is very low (Jaccard 0.09) and the overall semantics diverge significantly. The model was not misled by boilerplate because the code structures are quite different.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled these as clones due to superficial similarities: both methods involve logging, exception handling, and stream operations. The annotation guidelines for BigCloneBench sometimes accept Type-3/Type-4 clones where the core functionality (e.g., 'logging') is shared, even if the overall purpose differs. However, in this case, the shared behavior is minimal and not the primary functionality.
- 共享行为: Both perform logging using a logger instance.；Both handle I/O operations (stream copying, writing to buffers).；Both use try-catch blocks to handle exceptions.
- 行为差异: Function A is a servlet handler that processes page requests and renders HTML; Function B is a logging interceptor for SOAP messages.；Function A involves page retrieval, user authorization, and caching; Function B only captures and logs message details.；Function A writes response output and manages cache entries; Function B does not generate any response.；Function A has complex control flow with multiple conditions and error paths; Function B is linear and simpler.
- 修正建议: Improve token-level matching to avoid false positives from incidental common operations like logging.；Incorporate structural or dataflow analysis to distinguish primary functionality from auxiliary operations.；For BCB-style evaluation, consider refining the definition of 'partial functionality' to require a more substantial overlap.

### case_id=3264 FP boilerplate_overlap

- 方法: `doExecute` vs `readData`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Processes a multipart HTTP request to parse email fields and attachments, then sends the email.
- B 摘要: Initializes multiple sets and hash maps from static comma-separated strings and a configuration file for character mapping.
- 静态失败原因: The model likely overfitted to generic boilerplate patterns (try-catch, loops, method length) and may have been misled by common Java API tokens such as String, HashSet, or Exception, despite the low Jaccard similarity.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels as non-clone because the functions have no semantic or structural similarity; low token overlap and completely different domains.
- 共享行为: Both use loops and conditionals；Both handle exceptions with try-catch blocks
- 行为差异: A handles HTTP request and email sending; B reads static data and file for linguistic setup.；A uses FileUpload, MailPartObj, and Send; B uses StringTokenizer, HashSet, and custom data structures.；A's control flow depends on multipart detection; B's flow is sequential initialization.
- 修正建议: Enhance model to incorporate data-flow and API-level semantics rather than surface token patterns.；Use longer-range context or graph-based representations to distinguish different application domains.；Apply clone detection with domain-specific knowledge filtering.

### case_id=3265 FP lexical_or_api_overlap

- 方法: `getLinksFromURLFast` vs `CheckUrl`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Extracts all hyperlinks and anchor texts from an HTML page by fetching the entire page content and applying regex.
- B 摘要: Returns the first line of the HTTP response body from a given URL.
- 静态失败原因: Static BERT models may over-rely on lexical and API-level overlaps (e.g., URL, openConnection, BufferedReader, InputStreamReader) and miss the structural and logical differences in control flow and data manipulation.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone (0) because the functions have different core purposes: one is for link extraction, the other for simple HTTP response retrieval. Even though both use similar I/O patterns, the functional semantics diverge significantly.
- 共享行为: Open an HTTP connection to the given URL；Use BufferedReader to read the input stream；Return data from the web page
- 行为差异: A reads the whole page into a buffer, while B reads only the first line；A extracts multiple links and texts using regex, B returns the raw first line string；A returns an array of Vectors, B returns a single String；A converts relative URLs to absolute, B does no URL transformation
- 修正建议: Incorporate data flow or control flow features to distinguish parsing vs. simple reading；Train on more diverse patterns to reduce false positives from boilerplate HTTP code；Use fine-grained semantic similarity metrics that compare loop/iteration behavior and regex usage

### case_id=3266 FP boilerplate_overlap

- 方法: `loadExistingAntlibs` vs `getFrameworkFactory`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Loads antlib definitions from resource files using classloader, iterates over lines, and loads each antlib.
- B 摘要: Reads a service file to obtain an OSGi framework factory class name, instantiates it, and returns the factory.
- 静态失败原因: The model overemphasized the structural and lexical overlap of reading resources (BufferedReader, URL, InputStream) and missed the distinct business logic and output types.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels non-clone because the functions have entirely different semantics despite sharing a boilerplate pattern of reading a resource line by line.
- 共享行为: Both read a resource via classloader；Both use BufferedReader to read lines；Both iterate over lines and trim them
- 行为差异: Different resource paths and file purposes；Different processing: A creates URIs and loads antlibs, B loads a class and instantiates it；Different return types: void vs FrameworkFactory；Different error handling: A throws RuntimeException, B throws Exception
- 修正建议: Incorporate method names and comments into the embedding；Train on more diverse functional signatures to avoid boilerplate bias

### case_id=3267 FN lexical_or_api_overlap

- 方法: `invoke` vs `sendRequestObjectResponse`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Generic RPC invocation method that sends HTTP POST with JSON, handles response, and retries on timeout.
- B 摘要: Application-specific method that sends HTTP request with XML, saves response to a file, and shows result via browser.
- 静态失败原因: Static models like GraphCodeBERT rely heavily on token overlap and structural similarity; the low Jaccard score (0.10) and different API usage (HttpClient vs URLConnection) caused it to miss the functional similarity.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may label these as clones because both implement HTTP client functionality with request/response handling, which aligns with their broad Type-3/Type-4 criteria that accept partial functionality similarity even when implementation details differ.
- 共享行为: Both establish HTTP connections to a server, send a request payload, and read the response.
- 行为差异: A uses HttpPost and HttpClientUtils; B uses URLConnection and custom dialogs.；A constructs URL from service URL and method name; B constructs from preferences and applet codebase.；A returns deserialized object or null; B returns file path string.；A includes retry logic with service discovery; B includes UI interaction and file saving.
- 修正建议: Use data-flow or control-flow graphs to abstract away specific API names.；Incorporate cross-project patterns to recognize HTTP request-response architectures.；Train on more diverse pairs to learn that different libraries can serve the same purpose.

### case_id=3268 FN partial_functionality

- 方法: `testNetworkHTTP` vs `read`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Test function that performs multiple HTTP GET requests to various endpoints, reads and discards response lines, and logs activity.
- B 摘要: Reads a camera log from a single URL, parses each line into CameraLogRecord objects, collects them, and sorts the list.
- 静态失败原因: Static BERT models like GraphCodeBERT rely on token-level similarity and syntactic overlap; the low Jaccard similarity (0.22) and different variable names, URLs, and additional logic (parsing, logging) mask the underlying shared behavior of URL reading.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider the core behavior of reading lines from a URL via a buffered reader as a clone (Type-3), despite differences in parsing, multiple requests, and error handling, because the structural skeleton (try-finally, while loop) is similar and both involve network I/O.
- 共享行为: Both read lines from a URL using BufferedReader and InputStreamReader；Both handle IO exceptions and ensure stream/connection closure
- 行为差异: A makes multiple HTTP requests to different URLs; B reads only one URL；A does not parse or store read lines; B parses and stores records；A uses HttpURLConnection and disconnects; B uses url.openStream() and closes reader；A is void with no return; B implicitly returns via side-effect on records list
- 修正建议: Enhance model to recognize common API usage patterns (e.g., reading from URL) even when surrounding code differs；Use data flow or control flow subgraph matching to identify shared I/O operations；Train with contrastive learning on partial clones where only a subset of behavior matches

### case_id=3269 FN partial_functionality

- 方法: `executeHttpGet` vs `File2String`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Executes an HTTP GET request and returns the response body as a JSONObject.
- B 摘要: Reads a file's content into a string, with fallback to classpath and error handling.
- 静态失败原因: Static BERT likely over-relied on low token overlap (Jaccard 0.1667) and different API calls (HttpGet vs FileInputStream), missing the abstract semantic pattern of stream reading and string building.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB considers clones with similar algorithmic patterns (e.g., reading input stream line by line) even if input sources differ, as Type-3/4 clones.
- 共享行为: Both read text input line by line and concatenate to build a complete string.
- 行为差异: A uses HTTP client to fetch data, B uses file I/O.；A returns JSONObject, B returns String.；B includes fallback and system exit on error; A throws exception.
- 修正建议: Use models that capture structural patterns (e.g., AST or data-flow graphs).；Augment training data with pairs having low token similarity but similar abstract semantics.

### case_id=3270 FN partial_functionality

- 方法: `runScript` vs `httpRequestByPOST`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a script file from the applet's codebase via HTTP GET and returns its content as a string, or returns 'error!' on failure.
- B 摘要: Sends an HTTP POST request with form parameters, reads the response body line by line, and returns it as a string, or returns null and sets error fields on failure.
- 静态失败原因: Static BERT models like GraphCodeBERT rely heavily on lexical and structural surface patterns. The very low token Jaccard similarity (0.1667), different method names, distinct API usage (URL vs HttpClient), and different control structures (do-while vs while) led the model to classify these as non-clones, missing the deeper semantic commonality of HTTP request-response handling.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often considers Type-4 clones (semantic clones) where the overall purpose is the same (fetching remote resource and returning as string), despite differences in HTTP method, reading style, and error handling. The high-level similarity in intent justifies a clone label under BCB's broad criteria.
- 共享行为: Both functions perform an HTTP request to a remote server；Both read the response body and return it as a string；Both handle exceptions by returning an error indicator
- 行为差异: Function A uses HTTP GET, while B uses HTTP POST；A reads raw bytes sequentially, while B reads lines using BufferedReader；A returns 'error!' on any exception, B returns null and sets error fields；A is applet-context specific with getCodeBase(), B is generic
- 修正建议: Train models to recognize high-level program intent via intermediate representations like data flow or code summarization；Use contrastive learning on pairs with similar functionality but different surface forms；Incorporate knowledge of common web request patterns to group GET/POST and different reading styles

### case_id=3271 FP partial_functionality

- 方法: `readAndRewrite` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Reads a DICOM file, parses it, and writes out the pixel data to another file.
- B 摘要: Handles GUI action commands to set application preferences (e.g., external tool paths, UI settings) and update the user interface.
- 静态失败原因: The static model likely overgeneralized from superficial similarities (e.g., both involve 'File' objects and some output operations) but missed the fundamentally different algorithmic purposes.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB typically labels non-clones when functions have entirely different domains and no functional overlap, even under lenient Type-3/Type-4 criteria.
- 行为差异: Function A performs file I/O with DICOM medical images, while B manages GUI settings and user interactions.；Function A uses specialized libraries (ImageIO, DcmParser, PixelDataReader/Writer) absent in B.；Function B handles multiple command strings and updates UI components; A has a single linear workflow.；Function A throws IOException; B catches and handles exceptions internally.
- 修正建议: Incorporate structural and dependency analysis to differentiate file-oriented I/O from GUI event handling.；Use higher-level semantic representations (e.g., program slices) to capture core functionality rather than token overlap.；Train with more diverse negative examples to reduce false positives from unrelated but lexically similar pairs.

### case_id=3272 FN boilerplate_overlap

- 方法: `main` vs `execute`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a URL, extracts its zip entries, and writes each entry to a file.
- B 摘要: Reads a source file, converts it to HTML using given parameters, and writes the result to a destination file.
- 静态失败原因: Static BERT models rely on token and AST similarity; the low token Jaccard (0.10) and structurally different ASTs led the model to correctly predict non-clone from its perspective, missing the potential abstract clone if BCB intended.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may have considered the shared file I/O and exception handling as a Type-4 semantic clone, but the overall functionality differs significantly.
- 共享行为: Both perform file I/O with exception handling and resource closing.
- 行为差异: Code A extracts a zip archive; Code B converts file content to HTML.；Code A reads from a URL; Code B reads from a local file.；Code A uses ZipInputStream; Code B uses FileReader/FileWriter.；Code A does not create directories; Code B creates destination directory if needed.
- 修正建议: Incorporate data flow analysis to abstract common I/O patterns.；Use higher-level semantic representation focusing on the core transformation rather than exact API calls.

### case_id=3273 FN benchmark_preference_bias

- 方法: `doGet` vs `readAndRewrite`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: HTTP servlet handler that retrieves a page, checks visibility, logs, and writes HTML response.
- B 摘要: Utility method that reads a DICOM file, parses pixel data, and writes to another file.
- 静态失败原因: Low token overlap and different API usage led static model to correctly identify them as non-clones; BCB label may be an annotation error or overly broad.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have considered these as clones due to generic I/O processing and exception handling patterns, but the functional overlap is minimal.
- 共享行为: Both involve reading input and writing output
- 行为差异: Different domains: web portal vs DICOM image processing；A has complex conditional logic, B is linear；A uses HTTP request/response, B uses file streams；A has extensive logging, B uses System.out.println
- 修正建议: Improve tokenization to capture domain-specific terms；Incorporate control flow and data flow similarity；Use semantic role labeling to distinguish different tasks

### case_id=3274 FP boilerplate_overlap

- 方法: `googleImageSearch` vs `getXML`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Performs Google image search, parses HTML to extract image URLs, and updates UI components.
- B 摘要: Fetches XML content from a given URL and returns it as a string.
- 静态失败原因: The model likely overemphasized the common structural pattern of opening a URL, reading lines, and appending strings, while ignoring the distinct domain-specific processing and side effects. The lexical overlap is low, but the model may have been trained on many similar boilerplate patterns that are actually clones, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: The two functions share a boilerplate pattern of reading from a URL but have fundamentally different purposes and behaviors. BCB likely considered the specific tasks (image search vs. generic XML fetch) as too dissimilar to be clones, and the side effects and output types differ.
- 共享行为: Both open an HTTP URL and read the response line by line into a string buffer.
- 行为差异: Function A has side effects (modifies global list and UI); Function B returns a string with no side effects.；Function A parses HTML to extract image URLs; Function B returns raw content.；Function A handles errors by showing a dialog; Function B returns null on specific exceptions.；Function A builds a specific Google image search URL; Function B takes servletURL and request as parameters.
- 修正建议: Incorporate dataflow and side-effect analysis to distinguish functions that modify global state vs. pure data retrieval.；Use higher-level semantic understanding of the task (image search vs. generic fetch).；Include more diverse negative examples with similar boilerplate but different tasks.

### case_id=3275 FP lexical_or_api_overlap

- 方法: `get` vs `main`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Helper function that sends an HTTP GET request with specific headers, reads lines, filters out comments, decodes GameRecord objects, and returns an array.
- B 摘要: Main method that reads a web page line by line from a fixed URL and prints each line to stdout.
- 静态失败原因: Static BERT models likely over-relied on lexical and API token overlap (HttpURLConnection, BufferedReader, readLine) and structural patterns (while loop reading lines), missing the semantic divergence in headers, filtering, decoding, and error handling.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels these as non-clones because the core functionality (retrieving game records vs. printing web content) is distinct, despite both using HTTP reading patterns. The partial overlap in reading lines is insufficient for a clone rating under BCB's criteria.
- 共享行为: Both open an HTTP URL and read lines using BufferedReader.
- 行为差异: A sends custom headers (latitude, longitude, count) while B uses default request.；A filters lines starting with '#' and decodes GameRecord objects; B prints all lines.；A returns an array or null; B has no return value and prints to console.；A handles HTTP response codes and errors; B does not check response code.
- 修正建议: Incorporate control-flow or data-flow analysis to distinguish simple printing vs. structured data extraction.；Model the full request setup and response processing (headers, response codes) to differentiate.；Use longer-range context or API-specific embeddings for HTTP methods and headers.

### case_id=3276 FP boilerplate_overlap

- 方法: `getServerHash` vs `perform`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Computes SHA-256 hash of password hash with salt and returns hex string.
- B 摘要: Processes HTTP request to classify a concept by building XML and sending it to a URL.
- 静态失败原因: The static model likely over-relied on superficial common patterns like try-catch blocks and string encoding, ignoring the distinct high-level semantics.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB correctly labels them as non-clones because they have completely different purposes and logic.
- 共享行为: Both involve exception handling.；Both use string/byte manipulation.
- 行为差异: Function A is a cryptographic hashing utility; function B is an HTTP request handler.；Function A has no I/O beyond algorithm; function B performs URL connection and session management.；Function A returns a string; function B returns an ActionForward object.
- 修正建议: Incorporate semantic similarity based on data flow or API usage context.；Adjust confidence threshold for low token Jaccard cases.；Use method name and signature as additional features.

### case_id=3277 FP lexical_or_api_overlap

- 方法: `main` vs `readData`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Main method that concatenates multiple input files into an output file.
- B 摘要: Private method that initializes sets and maps from string constants and then reads a tab-separated file to populate a transliteration data structure.
- 静态失败原因: The static model may have been misled by lexical overlap of common Java API tokens (e.g., HashSet, StringTokenizer, while loops) and structural patterns, without capturing the semantic difference in purpose.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely considers them non-clones because they perform distinct tasks with no functional overlap; code_a is a utility main method, code_b is domain-specific initialization.
- 共享行为: Both involve reading and processing data in loops.
- 行为差异: Code_a is a simple file copy; Code_b performs complex parsing and data structure population.；Code_a writes output; Code_b builds in-memory maps and sets.；Code_b has extensive error handling and special case logic; Code_a does not.；Code_b uses StringTokenizer and multiple custom fields; Code_a uses Scanner and PrintWriter.
- 修正建议: Include method names and class context as input features.；Train on dataflow or program dependence graphs to distinguish utility code from complex logic.；Use contrastive learning to emphasize semantic differences beyond token overlap.

### case_id=3278 FP lexical_or_api_overlap

- 方法: `readData` vs `main`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `1.0`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Initializes several sets and maps from tokenized string fields and reads a configuration file to populate data structures.
- B 摘要: Copies a file from one location to another, skipping a given number of bytes from the start.
- 静态失败原因: Static BERT models may overemphasize lexical tokens like 'new', 'IOException', 'FileInputStream', etc., and ignore the high-level algorithmic differences and overall purpose.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels as non-clone because the functions have no overlap in functionality; one is a multi-purpose initialization routine, the other is a specific file copy utility.
- 行为差异: Function A performs complex data parsing and initialization; Function B performs a simple file copy.；Function A has many loops and conditional logic for set/map population; Function B has a single loop for byte copying.；Function A involves I/O from a file with column parsing; Function B involves I/O with skip and write.；Function A manages multiple data structures (HashSet, HashMap); Function B manages streams.
- 修正建议: Incorporate dataflow analysis to capture variable dependencies and side effects.；Use control flow graphs to distinguish loops and condition structures.；Train on larger variety of non-clone pairs with similar API usage but different semantics.；Consider the method name and surrounding context to infer purpose.

### case_id=3279 FN benchmark_preference_bias

- 方法: `updateFile` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.4`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Copies a file from one location to another using FileChannel.
- B 摘要: Downloads a KMZ file from a URL, unzips it, and extracts its entries to the current directory.
- 静态失败原因: Static BERT/GraphCodeBERT likely focused on the low token Jaccard similarity (0.148) and different method names/main functionality, missing any structural overlap that BCB might recognize.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider these clones due to both involving file copying and similar structural patterns (e.g., stream handling, resource cleanup), despite different high-level functionality.
- 共享行为: Both perform file I/O operations and handle streams/channels with try-finally blocks.
- 行为差异: One copies a single file, the other downloads and extracts a zip archive.；One uses FileChannel for copying, the other uses ZipInputStream and FileOutputStream for extraction.
- 修正建议: Train on more diverse partial-functionality clone pairs to capture structural similarity beyond token overlap.；Incorporate data flow or API usage patterns to detect underlying I/O operations.

### case_id=3280 FN benchmark_preference_bias

- 方法: `simulate` vs `getFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.2`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Simulates user reputation by reading a file, making web service calls, and writing results to an output file.
- B 摘要: Downloads a WSDL file from a URL, modifies its endpoint, and saves it to a temporary file, returning its location.
- 静态失败原因: Static BERT/GraphCodeBERT likely focused on low token overlap and different method names, leading to correct non-clone prediction; BCB's label may be an annotation bias.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: Possibly BCB considered the file I/O boilerplate and exception handling as sufficient structural similarity for a broad Type-4 clone, despite the distinct domain-specific logic.
- 共享行为: Both perform file I/O (open streams, read/write, flush, close).；Both handle exceptions with try-catch and logging.
- 行为差异: Code A processes reputation data via remote calls; Code B downloads and modifies XML.；Different data sources: local file vs URL.；Different outputs: writing to a file vs saving a downloaded file.；Code A has a loop; Code B has conditional logic based on file existence.
- 修正建议: Use dynamic analysis to confirm functional similarity.；Adjust annotation guidelines to avoid over-broad Type-4 labels.

### case_id=3281 FN benchmark_preference_bias

- 方法: `doGet` vs `copyDeleting`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Handles HTTP GET request to retrieve and serve a portal page with access control, caching, and logging.
- B 摘要: Copies a source file to a destination file using a byte buffer.
- 静态失败原因: Static BERT did not fail; it correctly identified the pair as non-clones due to vastly different semantics and low lexical overlap.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might have labeled as clone due to a mistaken assumption of functional similarity, perhaps based on both functions involving reading input and writing output, but the contexts are completely different.
- 行为差异: Function A is a servlet handling HTTP requests; B is a file copy utility.；Function A involves user authentication, page visibility checks, caching, and logging; B is a straightforward I/O copy.；Function A outputs to an HTTP response; B outputs to a file.
- 修正建议: Re-evaluate BCB annotation for this pair; likely a label error.；For future benchmark creation, ensure diverse functionality is not considered similar.

### case_id=3282 FN partial_functionality

- 方法: `runInternal` vs `readReferenceText`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads and parses OPDS catalog from an HTTP URL, handling pagination and error recovery.
- B 摘要: Reads a reference text file from a plugin bundle URL and returns its content as a string.
- 静态失败原因: Static BERT/GraphCodeBERT likely relied on token overlap and structural patterns, which are low (Jaccard 0.075). The methods share only generic terms like 'URL', 'InputStream', 'try-catch', but the high-level semantics differ significantly. The model missed the conceptual similarity of reading from a URL stream.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this as a clone because both methods read data from a URL source, involve stream I/O, and handle exceptions, thus exhibiting Type-4 functional similarity despite different specific tasks.
- 共享行为: Open a URL connection；Read input stream；Handle exceptions (IOException, etc.)；Use conditional logic for processing
- 行为差异: A performs HTTP-specific setup (user-agent, redirects, timeouts); B uses basic URL.openStream；A parses OPDS XML catalog entries and handles pagination; B reads lines of text；A has progress reporting and callback execution; B simply returns string；A handles multiple iterations (pagination); B is a single read
- 修正建议: Improve training data with more abstract semantic alignments across different domains；Incorporate data flow and control flow features that capture I/O operations and resource handling patterns；Use contrastive learning to differentiate between Type-4 clones and non-clones

### case_id=3283 FP lexical_or_api_overlap

- 方法: `run` vs `getPagina`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches tile data from a URL, parses it into geometry objects, and adds to a data loader with synchronization and multi-protocol support.
- B 摘要: Fetches a webpage from a URL and returns its content as a string, or an error message on failure.
- 静态失败原因: Static BERT/GraphCodeBERT likely overemphasized the lexical overlap of the URL reading pattern (BufferedReader, URL, openStream, readLine, concatenation) and ignored the larger structural and semantic differences in the methods' purposes and data flow.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB annotates non-clones because the overall functionality is distinct: one is a map tile loader with complex post-processing, the other is a simple HTTP GET utility. The shared URL reading code is considered boilerplate.
- 共享行为: Both read data from a URL using BufferedReader and openStream；Both iterate through lines and concatenate them into a single string；Both handle MalformedURLException and IOException
- 行为差异: Function A uses synchronization to manage concurrent requests; B does not；Function A handles file:// protocol and unsupported protocols; B does not；Function A parses the content into geometric objects and adds to a data structure; B returns the raw content string；Function A returns void; B returns a String
- 修正建议: Incorporate data-flow analysis to distinguish boilerplate from core functionality；Use contrastive learning that penalizes superficial lexical similarity without semantic alignment；Add positional encoding to capture method-level structure beyond API sequences

### case_id=3284 FP lexical_or_api_overlap

- 方法: `actionPerformed` vs `copyFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Handles GUI action events to set and save various application preferences.
- B 摘要: Copies a file from source to destination using FileChannel.
- 静态失败原因: Likely due to lexical overlap from common Java boilerplate (e.g., null checks, file I/O keywords) and the long length of function A causing the model to miss the semantic divergence.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would not consider these clones because they perform fundamentally different tasks with no meaningful functional similarity.
- 共享行为: Both involve file-related operations (A for selecting executables, B for copying files).
- 行为差异: A processes GUI events and updates UI; B is a standalone utility method.；A handles many different settings (graphviz, imagemagick, scale, etc.); B performs a single file copy.；A interacts with external state (preferences, UI components); B has no side effects beyond copying.
- 修正建议: Improve representation to capture high-level intent using AST or control flow graphs.；Use dataflow analysis to distinguish event handling from file operations.

### case_id=3285 FP boilerplate_overlap

- 方法: `loadMFileViaWeb` vs `executePost`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Loads a .m file from a URL and parses it into a UserFunction.
- B 摘要: Sends an HTTP POST request with parameters and returns the response string.
- 静态失败原因: The model likely over-weighted common API usage patterns (URL, BufferedReader, readLine) and failed to capture the semantic difference in input/output handling and final return type.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels this as non-clone because the core functionality is completely different (file parsing vs HTTP POST), despite some shared boilerplate I/O code.
- 共享行为: Both create a URL object and open a connection/stream；Both use BufferedReader and InputStreamReader to read line by line；Both handle exceptions with try-catch
- 行为差异: Function A reads a file (GET-like) while function B writes parameters (POST) then reads response；Function A returns a UserFunction after parsing, function B returns the raw response String；Function A sets the function name, function B does not have a similar step
- 修正建议: Incorporate method name and return type as strong features；Distinguish between read-only and read-write I/O patterns；Use data flow analysis to identify that one function writes to the connection and the other does not

### case_id=3286 FP partial_functionality

- 方法: `fetchUrl` vs `downloadFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches URL content and returns it as a string, with error handling returning empty string.
- B 摘要: Downloads a file from a URL to a local destination with progress tracking, returns boolean success, throws Exception on error.
- 静态失败原因: The model may have focused on the superficial structural similarity of opening a URL and reading streams, while ignoring the distinct return types, error handling patterns, and side effects (file creation, progress updates).
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely labels non-clone because the functions perform fundamentally different tasks (string retrieval vs file download with UI feedback), despite both involving URL reading.
- 共享行为: Both open a URL connection and read data from it.
- 行为差异: a returns content as string; b saves to file and returns boolean.；a reads line by line; b reads raw bytes in chunks.；b includes progress reporting via MessageFrame; a does not.；b creates and writes to a file; a only reads.
- 修正建议: Enhance model to consider method signature and return type.；Incorporate dataflow analysis to distinguish reading vs writing operations.；Add training examples with similar API usage but different overall behavior.

### case_id=3287 FN partial_functionality

- 方法: `serialize` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Serializes a content package to an output stream via a temporary file.
- B 摘要: Downloads a KMZ file from a URL and extracts its entries to the local file system.
- 静态失败原因: Static models like BERT rely on token sequences and method names; the low token overlap, different method names ('serialize' vs 'main'), and structural differences lead to a non-clone prediction. They miss the shared streaming idioms because they lack deeper semantic understanding.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as examples of 'stream copying' or 'file I/O', which could be seen as a broad Type-4 clone due to similar low-level I/O patterns, despite different high-level functionality.
- 共享行为: Both use InputStream and OutputStream for data transfer；Both perform file I/O operations
- 行为差异: Different overall purpose: serialize vs. download and extract；Different data sources: in-memory package vs. remote URL；Different output destinations: output stream parameter vs. local file system；Different processing: single serialized object vs. multiple zip entries
- 修正建议: Incorporate data flow and control flow graphs to capture structural similarities in I/O patterns；Use contrastive learning with positive pairs that share partial functional equivalence；Focus on API sequence similarities beyond exact token matches

### case_id=3288 FP lexical_or_api_overlap

- 方法: `downloadModel` vs `checkForUpgrade`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Downloads an RDF model from a given URL over HTTP.
- B 摘要: Checks for software upgrades by querying a remote license server and updating the local database.
- 静态失败原因: Static BERT/GraphCodeBERT likely over-emphasized lexical and API-level overlaps (e.g., URL, openConnection, InputStream), ignoring the completely different overall purpose and data processing logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically requires significant behavioral overlap for a clone label; the shared URL-reading pattern is too trivial and does not constitute meaningful functional similarity.
- 共享行为: Both open a URL connection and read from an InputStream
- 行为差异: Function A downloads and parses RDF data into a Model object; Function B sends a license query and parses XML-like responses
- 修正建议: Incorporate data flow analysis to distinguish different data transformations；Use higher-level semantic representations (e.g., abstract syntax trees with type information)；Include context-aware embeddings that capture the function's role in the program

### case_id=3289 FN partial_functionality

- 方法: `doGet` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Handles HTTP GET request to retrieve and serve a web page, including page lookup, permission checks, caching, and logging.
- B 摘要: Tests functionality of a custom StraightStreamReader by writing bytes to a file and reading them back with varying buffer offsets and sizes.
- 静态失败原因: The functions have very low token overlap (Jaccard=0.099) and different domain-specific vocabularies (HTTP vs I/O testing), leading static models to assign low similarity. The models may lack understanding of high-level semantics and over-rely on surface forms.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB might consider them clones due to both functions containing file creation, writing, reading, and exception handling, but the overall purpose and structure are too different; the low Jaccard similarity (0.099) suggests they are not even Type-4 clones.
- 共享行为: Both perform file I/O operations (write/read).；Both handle IOExceptions via try-catch blocks.；Both use loops to process data.；Both involve checking file existence or creation.
- 行为差异: Code A is a web servlet serving dynamic content; Code B is a standalone test harness.；Code A uses file I/O for caching HTML output; Code B tests stream reading correctness.；Code A involves user authentication and page visibility; Code B has no such logic.；Error handling differs: Code A returns HTTP error codes; Code B prints to stderr.
- 修正建议: Incorporate data flow and control flow graph features to capture functionality beyond tokens.；Use API call sequences as a representation to abstract away domain-specific terms.；Train on more diverse labeled clone pairs to learn functional similarity across different contexts.

### case_id=3290 FN partial_functionality

- 方法: `copyResource` vs `convert`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource (from URL or file) to a destination file by byte-by-byte streaming.
- B 摘要: Converts a DICOM file by parsing, validating metadata, and writing pixel data with optional inflation.
- 静态失败原因: The model relied on lexical and structural token overlap (Jaccard 0.1278) and was misled by the common I/O patterns, failing to abstract the shared functional purpose due to low token similarity and domain-specific API differences.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label them as clones because both achieve the high-level goal of reading data from one location and writing to another, viewing the core functionality as data transfer despite different domain specifics.
- 共享行为: Both read from an input source and write to an output file；Both use InputStream and OutputStream；Both handle I/O operations with exception handling
- 行为差异: copyResource is a generic resource copy; convert is a domain-specific DICOM format conversion；copyResource uses simple byte copy; convert includes metadata injection and pixel data transformation；convert has complex validation logic (UIDs, pixel length) absent in copyResource
- 修正建议: Enhance model to recognize functional similarity beyond token overlap, e.g., by using graph representations that capture I/O flows；Incorporate task-level semantics or program summaries to bridge domain-specific gaps

### case_id=3291 FP boilerplate_overlap

- 方法: `createDialogArea` vs `importSequences`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Creates a dialog area with a browser or text widget and loads license text from a resource URL.
- B 摘要: Imports biological sequences from a URL, parsing a FASTA-like format and collecting names and sequences into lists.
- 静态失败原因: The static model likely overfitted on lexical and API-level similarities (both using InputStream, BufferedReader, try-catch) and ignored the drastically different semantic contexts (UI versus sequence parsing). The low token Jaccard suggests the model relied on structural patterns rather than token overlap.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled non-clone because the functions serve entirely different purposes (UI vs data import), with no shared functionality beyond trivial I/O boilerplate. BCB annotations generally require significant behavioral overlap, which is absent here.
- 共享行为: Both open an InputStream from a URL.；Both read line-oriented text input.；Both use try-catch for IOException and print stack traces.；Both close streams in finally blocks.
- 行为差异: Function A creates a UI dialog; Function B parses sequence data.；Function A displays text in a browser or text widget; Function B stores data in ArrayLists.；Function A handles SWT GUI components; Function B uses a custom ImportHelper.；Function A returns a Control; Function B is void and populates class fields.
- 修正建议: Incorporate data-flow analysis to track how inputs and outputs are used differently.；Add semantic role labeling to distinguish UI creation from data processing.；Use program summarization to capture overall intent rather than local patterns.

### case_id=3292 FN benchmark_preference_bias

- 方法: `test` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Test method that reads a traffic model XML, initializes a simulation engine, and runs a 10-minute simulation printing vehicle positions.
- B 摘要: Method that builds an HTML site for editing by reading XML configuration, transforming pages, and writing output files with file I/O and string processing.
- 静态失败原因: The static BERT/GraphCodeBERT model correctly predicted non-clone (0), so it did not fail. The failure is in BCB labeling; the model agrees with strict semantics.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as a clone due to both functions reading XML files and performing some transformation, albeit with entirely different domains and outputs. This could be a false positive in the dataset where broad partial functionality (XML processing) was overvalued.
- 共享行为: Both perform file reading via InputStream；Both may involve XML content (reading/transforming)；Both use loops to process data
- 行为差异: Function A is a test that simulates traffic dynamics for a fixed duration; Function B builds and writes web pages with complex string manipulation；Function A uses a simulation engine and prints debug output; Function B involves file system operations, FTP, and transformer configuration；Function A has no I/O except reading a static resource; Function B has extensive I/O for multiple files and paths；Function A is short and focused; Function B is long with many parameters and error handling
- 修正建议: Re-evaluate the BCB annotation to correct potential false positive；Ensure clone annotations require stronger functional similarity, not just shared library usage

### case_id=3293 FP other

- 方法: `readData` vs `saveFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Parses comma-separated configuration strings to populate various sets and maps for Tibetan character processing.
- B 摘要: Serializes the UI window state (position, visibility, etc.) to an XML configuration file.
- 静态失败原因: GraphCodeBERT may have been misled by the presence of loops and string operations in both functions, ignoring the distinct domain logic and long-range dependencies.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB typically labels as non-clone when functions have entirely different purposes and no shared behavior, even if both involve data processing.
- 行为差异: readData initializes internal data structures from static strings; saveFile writes UI state to a file.；readData uses StringTokenizer and set operations; saveFile uses JDOM XML building and file I/O.；readData is static and operates on class-level variables; saveFile is instance method using a MainWindow parameter.；readData has no output parameters; saveFile produces a file as side effect.
- 修正建议: Improve training to distinguish between data parsing and UI serialization tasks.；Use more fine-grained representations that capture API-level semantics (e.g., JDOM vs StringTokenizer).；Incorporate control-flow and data-flow graphs to differentiate operations on local vs external state.

### case_id=3294 FN boilerplate_overlap

- 方法: `main` vs `readVersion`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends a POST request to RenRen API with multiple parameters and prints the response.
- B 摘要: Reads a version resource file from classpath and parses version, revision, and date fields.
- 静态失败原因: The model likely relied on low token similarity (0.13) and differences in method names, parameter setup, and output processing. It failed to recognize the shared I/O pattern as a cloning signal, possibly because the semantic context (API call vs. resource reading) diverges significantly.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may consider this a clone due to the shared boilerplate of opening a URL and reading lines with BufferedReader, which is a common but generic I/O pattern. Under BCB's broad criteria for Type-3/Type-4 clones, such structural similarity might be deemed sufficient for a positive label.
- 共享行为: Open a URL and create a BufferedReader to read input；Read lines in a while loop；Handle IOException
- 行为差异: Function A makes an HTTP POST request; Function B reads a local resource file；Function A constructs and sends parameters; Function B parses key-value lines；Function A prints response to stdout; Function B stores parsed values in fields；Function A uses HttpURLConnection; Function B uses ClassLoader.getSystemResource
- 修正建议: Incorporate dataflow analysis to distinguish API calls from local file reads；Add a check for functional purpose beyond I/O setup；Adjust similarity thresholds for boilerplate code

### case_id=3295 FN partial_functionality

- 方法: `httpRequestByPOST` vs `doVersionCheck`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends HTTP POST request with parameters, reads response body, returns it as string, or sets error fields and returns null on failure.
- B 摘要: Performs a version check by fetching a URL (GET), parsing version and build from lines, and displaying appropriate UI message; returns void.
- 静态失败原因: Static BERT-based models rely on token surface forms and local context; low Jaccard similarity (0.2258) and different API calls (HttpPost vs URL, params vs property) lead to classification as non-clone, missing the shared high-level semantics of HTTP request handling.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this as clone because both functions share the common pattern of making an HTTP request, reading the response with BufferedReader, parsing lines, and handling IOExceptions, representing partial functionality similarity.
- 共享行为: Both perform HTTP requests；Both read response content line by line using BufferedReader；Both handle IOException by showing error (set fields vs UI message)；Both involve buffered reading from an input stream
- 行为差异: Different HTTP methods: POST vs GET；Different return types: String vs void；Different error handling: sets instance fields vs shows dialog；Different purpose: generic web request vs version check
- 修正建议: Use dataflow analysis to capture that both functions open network connections and read data.；Incorporate API call patterns and high-level intent (e.g., 'HTTP GET/POST').；Train on more diverse Type-4 clones where only core behavior matches.

### case_id=3296 FN benchmark_preference_bias

- 方法: `copy` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.7`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Copies a file from source to destination using a 1024-byte buffer.
- B 摘要: Launches a complex configuration process that includes XML file handling, property setting, and resource copying for a NexOpen project.
- 静态失败原因: The static model correctly identified the low lexical overlap and functional mismatch, but BCB's label suggests a different similarity criterion that the model did not capture, such as high-level file processing patterns.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as a clone due to a broad Type-3/Type-4 interpretation where both functions involve file I/O and exception handling, despite vastly different overall purpose and length.
- 共享行为: Both involve file operations and throw exceptions on missing files.
- 行为差异: Function A is a simple file copy; Function B performs many steps like XML parsing, property setting, and project management.；Function B uses multiple libraries, callbacks, and persistent properties, while A does not.
- 修正建议: Refine BCB annotations to exclude such dissimilar pairs.；Incorporate more nuanced semantic understanding in models to align with benchmark preferences.

### case_id=3297 FP boilerplate_overlap

- 方法: `addQDInformation` vs `importSequences`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a local or remote QD info file and updates project information with parsed date and value data.
- B 摘要: Reads a FASTA-like sequence file from a URL and imports sequence names and data into local lists.
- 静态失败原因: The model likely focused on common boilerplate (try-catch-IOException, InputStream, Reader) and ignored the distinct parsing logic and domain-specific semantics, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the functions have completely different purposes and output structures, despite sharing basic I/O patterns.
- 共享行为: Both use I/O streams to read text data and handle IOException.
- 行为差异: Function A parses specific 'pg ' and 'pt ' lines to update project dates and values; function B parses '>' delimited FASTA sequences.；Function A manages a list of Information objects; function B populates string lists for names and sequences.；Function A supports both local file and remote URL; function B only reads from a URL selected from a combo box.
- 修正建议: Improve semantic understanding of parsing logic and data structures.；Incorporate method name or domain context.；Use fine-grained tokenization that captures unique identifiers and literals.

### case_id=3298 FN benchmark_preference_bias

- 方法: `modifyApplicationMessage` vs `download`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Modifies a locale-specific properties file by searching for a key and updating its value, or adding a new key-value pair.
- B 摘要: Copies a resource file from the classpath to a user-chosen file path using a save dialog.
- 静态失败原因: The model may have focused on the low structural similarity (different method names, different logic) and low token overlap, correctly predicting non-clone, but BCB labeled it as clone due to broad functional similarity in terms of file I/O; the model did not fail from our perspective.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have considered both as 'file operation' functions, or possibly due to lexical overlap in handling resources and IO streams, but this is a stretch.
- 共享行为: Both involve file I/O operations；Both handle exceptions；Both close streams
- 行为差异: One modifies text properties, the other copies binary files；One has complex string parsing, the other uses IOUtils.copy；One operates on multiple locale files, the other on a single file
- 修正建议: Review BCB annotation for this pair；Clarify clone definition for Type-4 or partial functionality；Use more semantic-aware models that distinguish specific operations

### case_id=3299 FP other

- 方法: `perform` vs `getHashedID`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Handles a web request to classify a concept, manages session, builds XML, sends HTTP request, parses result, and forwards to a JSP.
- B 摘要: Computes MD5 hash of an input string and returns a fixed-size byte array.
- 静态失败原因: The false positive likely arises from superficial pattern matching on common Java boilerplate (e.g., try-catch, loops, string operations) or misinterpretation of shared API usage (e.g., byte arrays), despite low lexical overlap.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB would not annotate these as clones because they perform entirely different tasks with no overlap in functionality; even broad Type-4 similarity is absent.
- 共享行为: Both are Java methods that may throw exceptions.
- 行为差异: Function A handles HTTP request/response and session management; function B computes a hash.；Function A builds XML, makes URL connections, and parses XML; function B uses MessageDigest for MD5.；Function A has complex control flow with multiple conditions and loops; function B has a single try-catch with simple loop.；Function A interacts with external resources (URL, session); function B is self-contained computation.
- 修正建议: Improve model to capture overall function semantics and task-level intent.；Incorporate more discriminative features like method name, control flow structure, and external API calls.；Use graph-based representations that capture data flow and dependencies.；Increase training data with more diverse non-clone pairs to reduce false positives.

### case_id=3300 FP lexical_or_api_overlap

- 方法: `load` vs `SRWGuiClient`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Loads text content from a pastebin URL and returns it as a string.
- B 摘要: Constructs a GUI browser window that fetches an XML URL, applies XSLT transformation, and displays the result as HTML.
- 静态失败原因: The model likely over-weighted the common API token sequences (URL, BufferedReader, InputStreamReader, readLine, while) and boilerplate patterns, ignoring the vast structural and semantic differences in the rest of the code.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clone because the functions have entirely different purposes (data retrieval vs GUI construction) and different output behaviors, despite sharing some API calls.
- 共享行为: Both create a URL object from a string.；Both open an InputStream via url.openStream() and wrap it in BufferedReader.；Both read lines in a while loop until null.
- 行为差异: A returns a string; B builds a GUI and sets up event handlers.；A reads all lines without processing; B parses XML, handles stylesheets, and transforms content.；A is a static method; B is a constructor.；A uses JOptionPane for error handling; B uses warnUser and prints stack traces.
- 修正建议: Use structure-aware models that capture control flow and data dependencies, not just token co-occurrence.；Train on tasks that emphasize functional equivalence, e.g., input-output pairs or execution traces.；Incorporate type signatures and method purposes (static vs constructor) as discriminators.

### case_id=3301 FN boilerplate_overlap

- 方法: `loadMFileViaWeb` vs `register`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.6`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Loads a MATLAB .m file from a URL, reads its content, parses it into a UserFunction, and returns it.
- B 摘要: Registers a new user by validating, encoding password, setting authorities, creating a forum user via URL, persisting, and sending confirmation email, returning boolean success.
- 静态失败原因: Static BERT likely focused on overall low token overlap and different return types, missing the shared URL reading boilerplate pattern.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB might have labeled it a clone due to shared structural pattern of reading from a URL line by line, considering it a Type-3 clone with similar control flow fragments.
- 共享行为: Both open a URL connection, read lines via BufferedReader in a while loop.
- 行为差异: Function A parses a file into a UserFunction; Function B registers a user with database and email operations.；Function A returns a UserFunction; Function B returns boolean.；Function B performs additional tasks: password encoding, authority assignment, email hash, database persist, email sending.；Different error handling: A logs and throws MathLibException; B logs and throws RuntimeException.
- 修正建议: Incorporate structural similarity detection for common I/O patterns.；Use subgraph matching to identify shared code fragments beyond lexical overlap.；Consider partial functionality similarity for cases with distinct core logic but identical utility blocks.

### case_id=3302 FP boilerplate_overlap

- 方法: `doBody` vs `main`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a file from the request and copies its content to the HTTP response output stream, then flushes and closes streams.
- B 摘要: Parses a Prolog file, generates Java adapter classes and metadata, and writes them into a JAR file, with extensive command-line argument handling.
- 静态失败原因: The static BERT model likely over-weighted common boilerplate patterns (try-catch, stream usage, file I/O) and ignored the vast difference in core logic, possibly due to token-level overlap and the model's inability to capture long-range semantic differences.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would label these as non-clones because they have entirely different purposes: one is a simple HTTP response writer, the other is a complex adapter generator. Even under broad Type-3/4 similarity, the semantic gap is too large to consider them clones.
- 共享行为: Both use buffered I/O streams (BufferedInputStream, BufferedOutputStream).；Both perform file reading and writing operations.；Both have try-catch-finally blocks for exception handling and resource cleanup.
- 行为差异: A is a simple file-to-response copy; B is a complex code generation pipeline with parsing, class writing, and serialization.；A has no conditionals or loops; B has many if statements, loops, and method calls to various custom classes.；A uses IOUtils.copy; B uses custom Writers, Visitors, and ClassLoaders.；A handles a single file; B handles command-line arguments, multiple file operations, and JAR creation.
- 修正建议: Improve the model to distinguish boilerplate from core functionality by incorporating more task-specific attention.；Use contrastive learning to reduce false positives from similar syntactic structures with different semantics.；Enhance the model with longer context windows or hierarchical encoding to capture the deep structural differences.

### case_id=3303 FP lexical_or_api_overlap

- 方法: `doVersionCheck` vs `SRWGuiClient`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Checks for a new version of jEdit by fetching and parsing a version file from a URL.
- B 摘要: Constructor for SRWGuiClient that initializes a Swing browser, fetches XML from a URL, optionally transforms it with XSLT, and displays it as HTML.
- 静态失败原因: The model likely focused on lexical overlap ('URL', 'BufferedReader', 'readLine', 'InputStream') and the structural pattern of opening a URL and reading in a loop, ignoring the vastly different surrounding context and purpose.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely considered these as non-clones because the core functionality (version checking vs GUI construction) is completely different, despite both using URL reading as a minor common step.
- 共享行为: Open a URL and read lines from it using BufferedReader
- 行为差异: A only reads version/build info and shows a dialog; B builds a full GUI, processes XML, applies XSLT, and displays HTML.；A is a static version check; B is a constructor with complex UI setup and transformation logic.
- 修正建议: Incorporate structural information like control flow and data dependencies to differentiate between a simple version checker and a complex GUI builder.；Use more global context, such as method name and surrounding class context.；Train on pairs that include such boilerplate but different semantics to reduce sensitivity to common I/O patterns.

### case_id=3304 FN benchmark_preference_bias

- 方法: `copy` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.2`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Copies an InputStream to an OutputStream, logging errors and closing streams.
- B 摘要: Reads XML files, performs XSLT transformations, and writes output files to build a site for editing.
- 静态失败原因: Static BERT/GraphCodeBERT models rely heavily on lexical and structural similarity; the token Jaccard is very low (0.0469) and the methods differ greatly in length and control flow, so the model correctly identified them as different. The BCB label appears to be an outlier or error.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might have considered these clones due to both involving stream I/O (InputStream/OutputStream) and similar error-handling patterns (logging and throwing), despite vastly different overall functionality. However, this interpretation is weak and likely a mislabel.
- 共享行为: Both perform file I/O operations
- 行为差异: Function A is a simple stream copy utility; Function B is a complex site-building method with many parameters and steps.；Function A handles IOException by logging and throwing a FaultException; Function B throws multiple exception types and handles specific FTP exceptions.；Function A uses IOUtils helper methods; Function B uses custom FileSystem, XML transformers, and string manipulation.
- 修正建议: Improve the BCB annotation consistency by ensuring clones reflect meaningful functional similarity.；Use data filtering to remove unlikely clone pairs based on token Jaccard threshold.

### case_id=3305 FP lexical_or_api_overlap

- 方法: `postData` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Function to send HTTP POST data to a specified URL with configurable protocol, host, form, and data payload.
- B 摘要: Function to perform a Google image search for the current track's artist and album, parse the response to extract image URLs, and add them to a list.
- 静态失败原因: Static models like CodeBERT rely on lexical and structural overlap. Both functions use similar API sequences (URL, openConnection, BufferedReader, etc.) and have analogous control flow (create URL, open, read, close), causing the model to overestimate similarity despite different intents.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because despite superficial API overlap, the functions have distinct purposes (generic POST vs. specific image search) and different data handling, which BCB considers in its functional similarity criteria.
- 共享行为: Both open HTTP connections using URL and URLConnection；Both read input streams with BufferedReader；Both close streams after reading
- 行为差异: A uses POST method, B uses GET；A sends data in request body, B parses HTML response；A has configurable parameters, B is hardcoded to Google Images；A does not process response content, B extracts image URLs
- 修正建议: Incorporate data flow and control flow analysis to distinguish different operations (e.g., POST vs. GET, writing vs. parsing)；Use graph-based models that capture semantic roles of API calls and their dependencies；Train with negative pairs that share API sequences but differ in functionality

### case_id=3306 FP boilerplate_overlap

- 方法: `executePost` vs `handledRun`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Sends an HTTP POST request with parameters and returns the response as a string.
- B 摘要: Downloads game data from a URL, checks version, and updates a local file if newer.
- 静态失败原因: The static model likely overfit on common boilerplate patterns (URL, BufferedReader, exception handling, finally) and ignored the different overall logic and data flow.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels this as non-clone because the two functions have distinct purposes and algorithms; they are not functionally similar.
- 共享行为: Both use URL to open network connections.；Both use BufferedReader to read input streams.；Both have try-catch-finally exception handling.；Both perform I/O operations with streams.
- 行为差异: Function A uses POST method and sends parameters; Function B uses GET implicitly via URL.openStream().；Function A returns the response string; Function B writes data to a file.；Function A handles a generic target URL; Function B uses a fixed URL for game data.；Function A has version checking logic; Function B does not.
- 修正建议: Incorporate dataflow analysis to distinguish between sending data and receiving/saving data.；Use graph-based models that model control and data dependencies more explicitly.；Augment training data with similar boilerplate but different semantics to reduce false positives.

### case_id=3307 FP long_range_semantics

- 方法: `copyFile` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `static_summary_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Copies a file from source to destination using FileChannel.
- B 摘要: Handles GUI action events to set various application preferences like file paths, look and feel, and other settings.
- 静态失败原因: The static model likely relied on superficial lexical or API overlaps (e.g., both involve File) and did not capture the overall semantic structure and control flow differences.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB labels them as non-clones because they perform completely different tasks and have no functional overlap.
- 共享行为: Both use File objects and handle IO (though B does not perform file copy).
- 行为差异: A performs actual file copy; B configures GUI and saves preferences.；A is short and focused; B is long with multiple conditional branches.；A returns boolean; B has no return value.；A does not involve UI; B heavily uses Swing components.
- 修正建议: Improve model's ability to capture long-range dependencies and control flow.；Incorporate structural information like AST or dataflow to distinguish between file copy and config handling.

### case_id=3308 FN benchmark_preference_bias

- 方法: `modifyApplicationMessage` vs `extractZipFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Reads a properties file for a given locale, updates or adds a key-value pair, and writes back.
- B 摘要: Extracts all entries from a zip file to a destination directory, with progress updates.
- 静态失败原因: Static model likely correctly predicted non-clone due to low lexical overlap and distinct semantics; the BCB label appears to be a mislabel or overly broad.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might consider them Type-4 clones due to both being file-processing utilities with similar control flow, despite different domains.
- 共享行为: Both perform file I/O operations with a loop reading entries/lines and writing output
- 行为差异: Different input formats (properties vs zip)；Different processing logic (string replacement vs decompression)；Different output structure (single file vs multiple files)；Different error handling (catch Exception vs throws)
- 修正建议: Re-evaluate BCB annotation for this pair; likely should be non-clone.；If maintaining broad BCB style, improve static model to capture abstract I/O patterns.

### case_id=3309 FN benchmark_preference_bias

- 方法: `downLoadZippedFile` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.1`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Downloads a file from a URL to a temporary file, unzips it into a destination directory, and returns the local URL of the unzipped content.
- B 摘要: Launches a NexOpen Eclipse launch configuration by validating project structure, processing pom.xml files, handling profiles, and scheduling an install action.
- 静态失败原因: The static model correctly predicted non-clone, but failed to align with BCB's likely erroneous label; the model's low token similarity and lack of deep semantic understanding led it to deem them unrelated, which is actually correct.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have erroneously labeled these as clones due to the superficial similarity of using IOUtils.copy and stream handling, but the functions are fundamentally unrelated.
- 共享行为: Both use IOUtils.copy for stream copying；Both contain try-finally blocks for resource cleanup
- 行为差异: Different overall purposes: file download/unzip vs. Eclipse launch configuration；Different domains: generic Java utility vs. Eclipse plugin specific；Different control flow and error handling；A returns a URL, B returns void
- 修正建议: Improve BCB annotation consistency by removing such false positive labels；Use more robust semantic features to avoid superficial stream-copying matches

### case_id=3310 FP boilerplate_overlap

- 方法: `copyFile` vs `main`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Copies a source file to a destination file using FileChannel, handling file creation and resource cleanup.
- B 摘要: Main method of an AdapterGenerator that parses command-line arguments, reads a Prolog file, generates adapter code, and writes output to a JAR file.
- 静态失败原因: The static BERT model likely overemphasized common tokens like 'File', 'IOException', and 'try'/'catch' patterns, leading to false positive due to boilerplate overlap.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels this as non-clone because the functions have completely different purposes and implementations, with only trivial overlap in using File and IOException. Even under broad Type-4 clone criteria, the semantic similarity is negligible.
- 行为差异: Function A is a simple file copy utility; Function B is a complex program entry point for code generation.；Function A operates on two file paths; Function B parses arguments, reads files, parses Prolog, generates adapters, and writes JARs.；Function A has no console output; Function B prints usage and error messages.；Function A uses FileChannel for efficient transfer; Function B uses various libraries (e.g., FileUtils, parser, ClassWriter).
- 修正建议: Train the model to better understand overall program structure and purpose beyond local token patterns.；Incorporate method-level semantic embeddings that capture the high-level task (e.g., file copy vs. code generation).；Use control flow and data flow features to differentiate trivial I/O usage from core functionality.

### case_id=3311 FN benchmark_preference_bias

- 方法: `main` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a hardcoded URL, reads it as a zip stream, and extracts all entries to the local filesystem.
- B 摘要: Launches a NexOpen project configuration by validating project files, processing pom.xml files with handlers, setting Hibernate dialect properties, and scheduling an install project action.
- 静态失败原因: The static model correctly identified the lack of lexical and structural similarity (token Jaccard 0.084) and predicted non-clone. The model did not fail; the BCB label is inconsistent with semantic equivalence.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: The BCB label may be a benchmark annotation error or reflect an overly broad notion of functional similarity that groups any functions dealing with file/resource processing as clones, which is not justified here.
- 共享行为: Both involve file I/O operations (reading from streams, writing to files).
- 行为差异: Different domains: simple zip extraction vs. complex Eclipse launch configuration.；Different control flow: sequential while loop vs. conditional handling and method calls.；Different APIs used: ZipInputStream, FileOutputStream vs. ContentHandlerTemplate, Properties, Eclipse resources.；No shared algorithmic logic or data processing pattern.
- 修正建议: Review and correct the BCB label for this pair to reflect true non-clone status.；If aligning with BCB, the model needs to be trained to recognize high-level conceptual similarities like 'entry-point resource processing', but this would likely increase false positives.

### case_id=3312 FN partial_functionality

- 方法: `readGeoParserResult` vs `lookupFutureEvents`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads geographic entity records from a remote geo-parser service via XML request and returns a collection of place names with gazetteer IDs.
- B 摘要: Fetches future events from the Meetup API via HTTP GET and returns a list of Event objects with details.
- 静态失败原因: Static BERT/GraphCodeBERT models rely on token-level and structural similarity. The low token overlap (0.12) and different API calls (XML vs JSON, different field names) cause the model to perceive them as different. The model does not capture the higher-level pattern of HTTP request + response parsing as a shared semantic concept, especially when the domain-specific details diverge.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider these as Type-4 semantic clones because both functions perform the task of fetching data from a remote service, parsing structured data, and extracting specific fields into a collection. Although the domain and output types differ, the overall behavior pattern is very similar.
- 共享行为: Constructs a URL with parameters；Opens an HTTP connection and reads the response stream line by line；Parses the response (XML or JSON) into an internal structure；Extracts specific fields from parsed elements and populates a collection
- 行为差异: Input parameters differ (recordContent and boolean vs groupIdentifier)；Output type differs (Tuple<String, ArrayList<String>> vs List<Event>)；Response format differs (XML vs JSON)；Data extraction logic is completely different (place name/gazetteer entries vs event fields)
- 修正建议: Use data-flow analysis to capture the I/O and network operation patterns；Train on semantic clones that share high-level structure despite different APIs；Incorporate program dependence graphs to highlight similar control flow (URL open, read, parse, iterate, extract)；Use transfer learning on tasks that understand web API interaction patterns

### case_id=3313 FN partial_functionality

- 方法: `copyResource` vs `unzipEntry`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource from a URL or local file to a destination file using a byte-by-byte loop.
- B 摘要: Extracts a zip entry to a file in an output directory, creating parent directories and using IOUtils.copy to transfer bytes.
- 静态失败原因: Static BERT models rely on token overlap and structural similarity, which are low here (Jaccard 0.15). The different method names, parameter types, and library calls (URL, ZipFile) obscure the shared semantic pattern of IO copy. The model may not have learned to abstract away from surface forms to recognize the common byte-copying behavior.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels Type-4 clones where the core functionality (copying bytes) is the same, even if the context, error handling, and specific APIs differ. Both functions ultimately achieve the same abstract task of streaming data from a source to a file.
- 共享行为: Both copy bytes from an input source to an output file；Both close streams after copying
- 行为差异: Different input methods (URL/file vs. zip entry)；Different error handling (Exception vs. IOException)；A uses manual byte loop, B uses IOUtils.copy utility；B handles directory entries; A does not
- 修正建议: Use data augmentation to include more IO copy variants with different APIs；Incorporate semantic-level features or graph representations that capture data flow；Train models to recognize abstract operations like 'copy stream' rather than specific library calls

### case_id=3314 FP partial_functionality

- 方法: `run` vs `loadURL`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.85`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a classpath resource line by line and sets its content as text in a JTextArea on the EDT.
- B 摘要: Downloads a URL with optional basic authentication, writes the content line by line to a temporary file, and updates a status label with file size.
- 静态失败原因: The model may have been misled by similar API usage (BufferedReader, InputStreamReader, URL) and the common pattern of reading line-by-line and updating UI. The lexical overlap is low, but structural similarity in the I/O and UI update pattern could cause overgeneralization.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely considers these non-clones because the core functionalities are different: one is for local resource loading into a UI text component, the other is for remote file download to disk with progress reporting. Although both involve stream reading, the high-level purpose and data flow diverge significantly.
- 共享行为: Both read from an input stream line by line.；Both use BufferedReader and InputStreamReader for reading.；Both have a UI update component (setting text or updating label).
- 行为差异: A reads from a classpath resource (getResource), B reads from a network URL (openConnection).；A writes to a JTextArea, B writes to a temporary file.；A uses UTF-8 encoding, B uses default encoding.；A catches all exceptions silently, B declares IOException and does not catch.
- 修正建议: Train the model to distinguish between reading local resources and downloading over the network.；Incorporate data flow analysis to capture the different destinations (memory vs. file) and authentication handling.；Use contrastive learning examples where similar I/O patterns have different high-level semantics.

### case_id=3315 FN partial_functionality

- 方法: `processAddByURLSubmit` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Reads DOAP data from a URL, converts to string, and processes it, with error handling.
- B 摘要: Builds an HTML site by reading XML files, applying XSLT transformations, and writing output files, with extensive I/O and exception handling.
- 静态失败原因: Static models like GraphCodeBERT rely on token and AST similarity; the low Jaccard index (0.05) and vastly different code structures led to a non-clone prediction. The semantic overlap is too abstract for the model to capture.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this as a Type-4 semantic clone because both functions involve a common high-level pattern: reading input from an external source, processing it, and handling errors, even though the specifics differ greatly.
- 共享行为: Both perform I/O operations to read external data；Both handle IOException and other exceptions；Both process read data in some way (A: DOAP, B: XML transformations)
- 行为差异: A is short and simple; B is very long and complex with loops and many parameters；A reads from a single URL; B reads multiple files and does transformations；A outputs to a StringWriter for further processing; B writes directly to files；A focuses on DOAP submission; B focuses on site generation
- 修正建议: Incorporate data-flow and control-flow graphs to capture behavioral patterns；Augment training with examples of long-range semantic clones with low token overlap

### case_id=3316 FN partial_functionality

- 方法: `getFileContentAsString` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a file from classpath or filesystem and returns its content as a string.
- B 摘要: Retrieves a resource as an InputStream, with HTTP caching and local file caching.
- 静态失败原因: Low token overlap (Jaccard=0.12) and significant structural differences likely caused the model to miss the high-level semantic similarity. The model may lack awareness of common resource-loading patterns across different APIs.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider them Type-4 clones because both ultimately load a resource and read its content, sharing a high-level semantic goal of resource retrieval despite vastly different implementations and additional functionality in B.
- 共享行为: Both involve opening a stream to read a resource (file or URL)；Both handle IO exceptions and close streams；Both use URL-related methods to locate resources
- 行为差异: A returns a String after reading the entire stream; B returns an InputStream directly with caching logic；B includes HTTP connection handling, request methods, and response code checks；B maintains a cache of remote URLs to local files and uses Buffered streams for copying；B prints debugging output; A does not
- 修正建议: Incorporate data flow analysis to connect resource acquisition and usage；Use models pretrained on code summarization or clone detection with broader context；Include heuristics for resource loading patterns

### case_id=3317 FP partial_functionality

- 方法: `readZoneIDs` vs `doVersionCheck`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads zone IDs from a resource file and returns a set of integers.
- B 摘要: Checks version information from a remote URL and updates the view accordingly.
- 静态失败原因: Static BERT/GraphCodeBERT likely focused on shared API calls (URL.openStream, BufferedReader, readLine) and loop structure, missing semantic differences in data processing and output.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely labels this non-clone because the functions differ in purpose, output, and control flow despite sharing some API usage.
- 共享行为: Both open a URL, read lines in a loop, and parse each line.
- 行为差异: Function A returns a set of parsed integers, while B modifies UI and checks version strings; different error handling; different output.
- 修正建议: Incorporate type and return type matching；Use control flow difference features；Add data flow analysis to distinguish parsing logic

### case_id=3318 FN benchmark_preference_bias

- 方法: `compressWithZip` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `preference_memory_with_manual_audit`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Creates a zip file from a list of files.
- B 摘要: Extracts entries from a zip file (from URL) to disk.
- 静态失败原因: Static BERT likely emphasized the semantic direction (compress vs decompress) and predicted non-clone, whereas BCB's broader criteria accept such structural similarity as a clone.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider structural similarity (while loops reading/writing bytes, use of ZipEntry/ZipOutputStream, stream closing patterns) sufficient for a Type-3 clone, ignoring the compression/decompression direction.
- 共享行为: Both use buffer I/O to process zip entries；Both close streams after processing；Both handle file I/O exceptions
- 行为差异: A compresses files, B decompresses a zip；A reads from local files, B reads from a URL；A outputs a zip file, B outputs extracted files
- 修正建议: Include more diverse Type-3 clone examples in training；Incorporate BCB annotation guidelines to adjust model threshold for structural clones

### case_id=3319 FN partial_functionality

- 方法: `read` vs `runScript`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a camera log from a URL, parses lines into CameraLogRecord objects, adds them to a list, and sorts the records.
- B 摘要: Reads a script file from a URL as a raw string by reading bytes one by one and concatenating them.
- 静态失败原因: Static BERT models rely on token sequences and have low overlap (Jaccard=0.1875). They focus on syntactic differences like BufferedReader vs BufferedInputStream and while vs do-while, missing the shared semantic concept of URL reading.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider this a clone because both functions perform the high-level task of reading data from a URL via input stream, which is a common functionality. The differences in parsing and output format are considered acceptable for Type-4 (semantic) clones.
- 共享行为: Open a URL connection to read data；Use InputStream-based reading loop
- 行为差异: A reads line-by-line with BufferedReader; B reads byte-by-byte with BufferedInputStream；A parses lines into structured objects; B concatenates bytes into a string；A sorts the resulting records; B does not sort；A logs progress and handles parse errors; B catches all exceptions and returns 'error!'
- 修正建议: Train models to recognize high-level functional similarities like URL reading patterns；Use graph-based representations to capture data flow and control flow；Incorporate code documentation or comments to infer intent

### case_id=3320 FP boilerplate_overlap

- 方法: `readData` vs `copyFiles`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Reads and parses configuration data from string fields and a file, populating multiple sets and maps.
- B 摘要: Recursively copies files or directories using NIO file channels.
- 静态失败原因: Static BERT may have focused on superficial similarities (static void, file I/O, exception handling) and overlooked the completely different logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically requires some shared algorithmic or functional similarity for Type-3/Type-4; here there is none.
- 共享行为: Both are private static void methods；Both involve file I/O operations
- 行为差异: Purpose: data parsing vs. file copying；Data structures: sets and maps vs. file channels；Algorithm: tokenization and parsing vs. recursive directory traversal and channel transfer
- 修正建议: Augment training data with more contrasting examples；Incorporate dataflow or structural similarity metrics；Downweight boilerplate tokens in attention

### case_id=3321 FN benchmark_preference_bias

- 方法: `copyFile` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Copies a file using NIO FileChannel, performing a simple file copy operation.
- B 摘要: Launches an Eclipse launch configuration for a NexOpen project, processing XML files, setting Hibernate dialect, and handling reverse engineering setup.
- 静态失败原因: The static model correctly identified non-clone due to low lexical overlap (token Jaccard 0.038) and no clear semantic similarity; it did not fail, as the BCB label appears erroneous.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: The BCB label of 1 is likely a false positive, possibly due to both methods using file I/O or exception handling, but the overall functionality differs significantly.
- 行为差异: Function A performs a basic file copy, while B executes a complex Eclipse project setup.；A uses NIO channels; B uses Eclipse APIs, XML processing, and I/O streams.；A has no external dependencies; B heavily depends on Eclipse and Hibernate libraries.；A is a utility method; B is part of a launch configuration handler.
- 修正建议: Re-evaluate BCB annotation consistency for this pair.；Implement manual validation or cross-referencing for ambiguous cases.；Consider filtering out pairs with very low lexical similarity from clone ground truth.

### case_id=3322 FP lexical_or_api_overlap

- 方法: `SRWGuiClient` vs `getNetworkServersIPs`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Constructs a Swing browser GUI, reads XML from a URL, applies XSLT transformation, and displays HTML.
- B 摘要: Parses a network server list from a URL, extracting IP addresses after '!SERVERS' lines and returning them as a vector.
- 静态失败原因: The static BERT model likely over-relied on the overlapping API calls (URL, BufferedReader, InputStreamReader) and the general pattern of reading from a URL, ignoring the disparate high-level semantics and control flow.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically avoids labeling as clone when overall functionality differs significantly, even if there is some low-level API overlap (e.g., URL reading). Low token Jaccard supports this.
- 共享行为: Both open a URL and read its content line by line using BufferedReader.；Both handle IOException and MalformedURLException.；Both use URL and URLConnection classes.
- 行为差异: A builds a GUI with JFrame, JPanel, JEditorPane, etc.; B returns a Vector<String> with no GUI.；A performs complex XML parsing and XSLT transformation; B uses simple line-by-line parsing with a state machine.；A outputs to console and displays HTML; B only returns a vector of IP addresses.；A has extensive error handling with user warnings; B prints stack traces.
- 修正建议: Train the model to focus on the overall structure and data flow rather than surface-level API usage.；Incorporate control flow graph or data flow embeddings to differentiate patterns.；Use negative examples with similar API sequences but different goals.

### case_id=3323 FN partial_functionality

- 方法: `copyResource` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource (URL or file) to a destination file using single-byte I/O.
- B 摘要: Copies a file to another file with buffered I/O and optional overwrite control.
- 静态失败原因: Static BERT models rely on token and shallow syntactic similarity; the functions have moderate token overlap (Jaccard 0.33) and differ in control flow (single-byte vs buffered loop, try-finally), method names, and exception types, leading the model to underestimate their functional similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels as clones when two functions perform the same core operation (copying data from input to output) despite differences in buffering, error handling, or source specification.
- 共享行为: Both copy data from an input source to an output file；Both use InputStream and OutputStream；Both close streams after copying
- 行为差异: copyResource reads single bytes; copyFile uses a buffer；copyResource can read from URL or file; copyFile only reads from File；copyResource has no overwrite control; copyFile has a force flag；Exception handling differs (Exception vs IOException, try-finally vs no try-finally)
- 修正建议: Incorporate data flow analysis to highlight the essential input-to-output transfer；Train on varied copying implementations to generalize beyond surface form；Use graph-based models that capture program semantics such as control and data dependencies

### case_id=3324 FN benchmark_preference_bias

- 方法: `doGet` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Handles HTTP GET request to retrieve and display a web page, with access control and caching logic.
- B 摘要: Compresses a file using GZip in a command-line utility.
- 静态失败原因: It correctly identified no semantic similarity; the low token Jaccard and distinct API usage (servlet vs. file streams) likely led to a non-clone prediction.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB label may be a false positive; possibly annotators considered both as 'request processing' but that is too broad. Alternatively, it could be an annotation error.
- 共享行为: Both involve file I/O (reading/writing), but in completely different contexts.
- 行为差异: Function A is a servlet method dealing with HTTP requests and page rendering; Function B is a standalone main method for file compression.；Function A interacts with web containers, user permissions, and caching; Function B only reads a file and writes a compressed version.；Function A has complex control flow for page visibility and fallback logic; Function B has a simple linear flow for reading and compressing.；The exception handling and logging differ significantly (servlet errors vs. console output).
- 修正建议: Review BCB annotation for this pair to confirm if it's a mislabel.；Improve static model to handle such false positives by requiring stronger semantic overlap.

### case_id=3325 FP lexical_or_api_overlap

- 方法: `run` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches and processes geospatial tile data from a URL, parsing GeoJSON into geometry collections.
- B 摘要: Searches Google Images for album art based on current track, extracting image URLs from HTML response.
- 静态失败原因: The static model likely focused on overlapping API tokens (URL, BufferedReader, openConnection) and missed the high-level semantic divergence due to lack of deeper semantic understanding.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically does not annotate such pairs as clones because the core functionality is entirely different, despite sharing trivial HTTP reading boilerplate.
- 共享行为: Both open an HTTP connection to a URL and read the response line by line.；Both build a string from the read lines.；Both contain error handling for IOExceptions.
- 行为差异: Function A deals with vector tile data and geometry parsing; Function B deals with image search and HTML parsing.；Function A uses a thread-safe request deduplication mechanism; Function B does not.；Function A processes the response into a data loader; Function B stores image URLs in a list.；Function A has protocol handling for file and HTTP; Function B only uses HTTP.
- 修正建议: Increase training data with diverse tasks to reduce reliance on shallow token overlap.；Incorporate data flow or control flow features to capture program intent.；Use contrastive learning to penalize pairs with only superficial API similarity.

### case_id=3326 FP boilerplate_overlap

- 方法: `handleHandshake` vs `scrapeForIsbns`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Handles Minecraft server handshake by validating server ID and performing session authentication via HTTP.
- B 摘要: Scrapes a URL for ISBN-10 patterns and stores matches, returning the count.
- 静态失败原因: Static BERT models often rely on token-level embeddings and may overemphasize common boilerplate (e.g., 'URL', 'BufferedReader', 'InputStreamReader', 'try-catch'), causing false positive similarity despite completely different domain logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically requires similar functionality or structural similarity. Despite both using network I/O, the core purposes are entirely different (game authentication vs. ISBN scraping), so BCB correctly labels as non-clone.
- 共享行为: Both open a URL and read lines using BufferedReader and InputStreamReader.；Both handle IOException and other exceptions.
- 行为差异: Function A validates a server ID and authenticates a Minecraft session; Function B extracts ISBN patterns.；Function A only reads one line; Function B reads multiple lines and uses regex.；Function A sends packets or disconnects; Function B stores results and returns count.；Function A has retry logic for connection attempts; Function B does not (it has a single attempt).
- 修正建议: Incorporate data-flow or control-flow analysis to differentiate core logic from IO scaffolding.；Add domain-specific features (e.g., pattern of method names, API calls) to disambiguate.；Use aspect-level matching that considers the semantic goal of the function, not just token co-occurrence.

### case_id=3327 FP lexical_or_api_overlap

- 方法: `getTicketsForQueue` vs `startScript`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Queries a REST API for open tickets in a queue, parses ticket IDs from response lines, and retrieves each ticket.
- B 摘要: Reads a script from a URL and appends lines to a dialog buffer.
- 静态失败原因: Static BERT/GraphCodeBERT likely overemphasized superficial structural similarities (e.g., try-catch, BufferedReader, readLine loop) and common vocabulary, while missing the semantic mismatch in purpose and output.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically requires similar high-level functionality. These functions only share a common low-level I/O pattern; their business logic and context are entirely different, so BCB would likely label them as non-clones.
- 共享行为: Both make an HTTP request and read the response line by line using BufferedReader.
- 行为差异: Different purpose: ticket retrieval vs. script loading；Different API usage: HTTPGet vs. URL.openStream()；Different output: returns list of RTTicket objects vs. modifies dialog.script；Different error handling: returns null or throws exception vs. prints error and exits
- 修正建议: Incorporate program dependency analysis to capture data flow and intent.；Use contrastive learning with negative examples that share low-level patterns but differ in high-level semantics.；Augment model with type and API usage context.

### case_id=3328 FN partial_functionality

- 方法: `doVersionCheck` vs `register`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Checks for a new version by reading a version file from a URL and comparing build numbers, showing GUI messages.
- B 摘要: Registers a user by encoding password, constructing a forum registration URL, reading response to set forum ID, persisting to database, and sending confirmation email.
- 静态失败原因: Low token Jaccard (0.14) and different method names/domain keywords caused the model to rely on surface forms, missing the structural similarity in control flow and API usage.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considers these Type-3 clones due to the shared structural pattern of opening a URL, reading input, processing lines, and exception handling, despite differing domain logic.
- 共享行为: Both open a URL connection, read lines using BufferedReader, and parse each line for specific information.；Both handle IOException with error logging or user-facing messages.
- 行为差异: A is a version check; B is a user registration with database persistence and email sending.；A uses GUI interactions; B uses logging and returns a boolean.；A reads a fixed property URL; B constructs a URL with query parameters.；Error handling: A shows error dialog; B throws RuntimeException or returns false.
- 修正建议: Incorporate structural or control flow graph similarity.；Enhance model with data flow patterns that capture URL reading loops.；Use contrastive learning on BCB-style clones to recognize structural templates.

### case_id=3329 FP lexical_or_api_overlap

- 方法: `postData` vs `checkForUpgrade`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Sends HTTP POST data to a specified URL by opening a connection, writing data to output stream, and reading the response.
- B 摘要: Checks for software upgrades by querying a remote server, parsing license and upgrade data, updating a database, and showing UI messages.
- 静态失败原因: The static BERT/GraphCodeBERT model likely overemphasized the shared API usage (URLConnection, BufferedReader) and ignored the surrounding different logic, leading to a false positive clone prediction.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels pairs as non-clones when they serve distinct high-level purposes, even if they share common boilerplate like HTTP connection handling. Here, the functions are semantically unrelated.
- 共享行为: Both open a URLConnection and use BufferedReader to read input stream.；Both close the input stream after reading.
- 行为差异: Function A writes data to the output stream; Function B does not.；Function B interacts with UI components and database; Function A does not.；Function B parses complex responses and loops through upgrade items; Function A simply discards the response.；Function A is a generic utility; Function B is a specific business logic method.
- 修正建议: Include features that capture higher-level semantics beyond API call sequences.；Use data flow analysis to distinguish between writing vs. reading patterns.；Train on more diverse negatives to reduce sensitivity to shared boilerplate.

### case_id=3330 FN benchmark_preference_bias

- 方法: `doGet` vs `saveFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Handles an HTTP GET request to retrieve and display a page, with caching and logging.
- B 摘要: Saves UI settings (window sizes, positions) to an XML configuration file.
- 静态失败原因: The model correctly identified non-clone based on low token overlap and different APIs; it failed to match BCB's label because that label is likely an overgeneralization.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as a clone due to both functions involving file writing and error handling, possibly viewed as a broad Type-4 similarity.
- 共享行为: Both perform file I/O operations with try-catch and logging.
- 行为差异: Function A is a web servlet handling page requests; Function B saves GUI state.；Function A uses Property lookups and Page objects; Function B uses Document and Element XML construction.；Function A outputs HTML; Function B outputs XML.
- 修正建议: Review BCB annotation for accuracy; consider refining clone definition.；If BCB intends broad similarity, incorporate higher-level behavioral abstraction.

### case_id=3331 FN partial_functionality

- 方法: `getHTML` vs `addDataFromURL`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches HTML from a URL using HttpURLConnection with specified encoding, optionally writes to file, and returns the content as a string.
- B 摘要: Fetches data from a URL using URL.openStream and appends each line to a StringBuilder member variable, with exception handling that appends the URL on failure.
- 静态失败原因: Static BERT models often rely on token-level overlap and syntactic structure, which are low (Jaccard 0.2857). The different API usage (HttpURLConnection vs URL.openStream), distinct method signatures (return type, parameters), and extra conditional logic (file writing in A) cause the model to miss the underlying functional similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB considers this a Type-3 clone because both methods download URL content and accumulate text, despite differences in HTTP library, encoding, and return type. The core functionality is highly similar.
- 共享行为: Both read from a URL using BufferedReader line by line；Both accumulate the content into a string/StringBuilder；Both use try-catch for exceptions
- 行为差异: A uses HttpURLConnection with User-Agent header; B uses URL.openStream；A handles encoding character set; B does not；A can write to a file; B does not；A returns the string; B appends to a member variable and returns void
- 修正建议: Train with more examples of methods that achieve the same goal via different APIs；Use code representations that capture dataflow or program dependence (e.g., graph-based models)；Incorporate contrastive learning to pull together functionally similar functions

### case_id=3332 FN partial_functionality

- 方法: `testAddLinkToImage` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: A test method that copies image files from classpath resources to a test folder and adds links to them in a report.
- B 摘要: A main method that downloads a KMZ file from a URL, unzips it, and extracts all entries to files.
- 静态失败原因: Static BERT models rely on token-level and surface syntax, which differ significantly between the two functions (method names, identifiers, library calls), causing it to miss the high-level I/O pattern similarity that BCB might recognize.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may view both as file copy operations from a source to destination, considering the core I/O pattern as a Type-3/4 clone despite different contexts.
- 共享行为: Both read from an input stream and write to file output streams
- 行为差异: A uses IOUtils.copy for specific resources; B manually reads buffer and handles ZIP extraction；A adds links to a report; B only extracts files；A is a test method; B is a main entry point
- 修正建议: Use dataflow or control flow analysis to detect similar I/O patterns；Incorporate API call sequences and abstract away specific resource names

### case_id=3333 FN benchmark_preference_bias

- 方法: `main` vs `doGet`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Copies a file from source to destination using NIO FileChannels in a main method.
- B 摘要: Handles HTTP GET requests for a page, including authentication, logging, and caching, writes HTML response.
- 静态失败原因: Static BERT models rely heavily on token-level overlap and structural similarity; the low Jaccard similarity (0.06) and lack of shared vocabulary or API calls cause them to predict non-clone. They cannot capture the vague abstract similarity BCB might have used.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled these as clones based on a very abstract similarity: both functions perform input-to-output transfer (file read/write vs HTTP request/response handling). However, this is an overly broad interpretation that likely mislabels the pair.
- 共享行为: Both involve I/O operations (reading and writing data)；Both use exception handling with try-catch
- 行为差异: Different input/output (file vs HTTP request/response)；Function A is simple file copy; B is complex with multiple conditional branches, database queries, authentication；Different method signatures: main vs doGet；Function A uses NIO ByteBuffer; B uses PrintWriter and servlet API
- 修正建议: Improve BCB annotation quality to avoid such ambiguous labels；Focus on functional equivalence rather than vague I/O similarity；Use domain-specific filtering to exclude unrelated code pairs

### case_id=3334 FN benchmark_preference_bias

- 方法: `runScript` vs `addQDInformation`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Reads a script file from a URL and returns its content as a string.
- B 摘要: Reads a local or remote data file (qdinfo.dat) and parses it to update project information timestamps and quality values.
- 静态失败原因: Static BERT models likely relied on token-level similarity (Jaccard=0.1589) and structural differences, correctly identifying them as non-clones. The error is that BCB labeled them as clones, not that the static model failed.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might label these as clones because both involve reading data from a URL and use similar I/O patterns (InputStream, try-catch), possibly from the same project, leading to a broad Type-4 similarity judgment despite different functionality.
- 共享行为: Both open a URL or file input stream；Both use try-catch for I/O exceptions；Both involve reading data from an external source
- 行为差异: A reads raw bytes and concatenates into a single string; B reads lines and parses structured prefixes (pg, pt)；A returns the data string; B updates internal state (_qdDate, info objects) without returning anything；A has a simple loop; B has complex parsing logic with multiple conditions and updates
- 修正建议: Incorporate project context to disambiguate different data access patterns；Use data-flow analysis to capture different post-read processing (return vs. state update)

### case_id=3335 FP lexical_or_api_overlap

- 方法: `doVersionCheck` vs `getUser`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.85`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Checks for software version updates by fetching a URL and parsing build numbers.
- B 摘要: Retrieves a user by login from a DAO or falls back to parsing a config file.
- 静态失败原因: The model likely over-emphasized lexical overlap (URL, BufferedReader, try-catch, readLine) and ignored the distinct task semantics and data flow.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically annotates clones when functions share significant functional similarity beyond boilerplate I/O; here the tasks are entirely different, so non-clone.
- 共享行为: Both open a URL or input stream；Both use BufferedReader to read lines；Both parse lines with simple tokenization；Both handle exceptions with try-catch
- 行为差异: Purpose: version check vs. user retrieval；Parsing logic: '.build' and '.stablebuild' prefixes vs. colon-separated fields；Output: triggers another version check method vs. returns a User object；Error handling: specific IOException vs. generic Exception
- 修正建议: Incorporate data flow or control flow graphs to capture functional logic；Use contrastive learning with functional semantics；Leverage method name and domain context

### case_id=3336 FN benchmark_preference_bias

- 方法: `modifyApplicationMessage` vs `displayDiffResults`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Modifies a properties file by updating or adding a key-value pair for a given locale.
- B 摘要: Generates an HTML report of file differences and launches a browser.
- 静态失败原因: Static BERT models like GraphCodeBERT typically rely on token overlap and API-level patterns. With low token Jaccard (0.11) and different method names, the model likely recognized the semantic difference and correctly predicted non-clone. However, if misclassified as FN, it suggests the model failed to align with the erroneous BCB label.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled as clone due to superficial similarity in file I/O patterns (FileReader, FileWriter, BufferedWriter, InputStream) and string building, which are common boilerplate. However, the two functions serve entirely different purposes, so BCB likely made an error.
- 共享行为: Both perform file I/O operations (reading and writing files).；Both use BufferedWriter/FileWriter and InputStream/FileInputStream.；Both handle exceptions (A catches Exception, B throws IOException).
- 行为差异: Different purpose: properties file modification vs diff report generation.；Different input parameters: locale, messageName, messageValue vs no parameters.；Different output: modified properties file vs HTML file shown in browser.；Different logic: search and replace key-value vs building HTML tables with metrics.
- 修正建议: Re-evaluate BCB label; these functions are not semantic clones.；Improve model to better distinguish superficial API overlap from true semantic equivalence.

### case_id=3337 FP long_range_semantics

- 方法: `getDigest` vs `perform`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `static_summary_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Computes an MD5 digest for HTTP Digest authentication using a series of hashing steps.
- B 摘要: Processes a Struts classify action by handling session, parameters, constructing XML, posting to a URL, parsing result, and forwarding based on outcome.
- 静态失败原因: The static BERT model likely missed the long-range semantic disparity and may have been misled by vague similarities such as both containing try-catch blocks and string building, but the token Jaccard similarity is very low (0.045), suggesting a systematic error in capturing overall program intent.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB annotators likely saw no semantic or structural similarity; these functions serve entirely distinct purposes with no shared functionality, thus labeled non-clone.
- 行为差异: One function performs cryptographic hashing; the other handles web request processing and classification.；Different inputs: authentication parameters vs. HTTP request/session objects.；Different outputs: a hex string vs. an ActionForward.；Different operations: MD5 digests vs. HTTP communication, XML parsing, and session management.
- 修正建议: Improve model's ability to capture global program semantics via graph-based or flow-sensitive representations.；Incorporate contrastive learning with hard negative pairs.；Use code summarization or documentation to enrich semantic understanding.

### case_id=3338 FP boilerplate_overlap

- 方法: `cpFile` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Copies a file from source to target with optional overwrite and buffer size.
- B 摘要: Handles UI action events to set application preferences and update interface components.
- 静态失败原因: The model likely misclassified due to lexical overlap (both mention File and IOException) and the presence of boilerplate file-handling code in both, despite radically different overall behavior.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would not label these as clones because they have no functional similarity; one is a file copy utility, the other is a UI event handler.
- 行为差异: Function A performs file I/O copying bytes; Function B updates UI and preferences.；Function A has a single purpose; Function B is a large event dispatcher for multiple commands.；Function A throws IOException; Function B handles exceptions internally and logs warnings.
- 修正建议: Incorporate method-level semantic summaries or documentation embeddings.；Use AST-based features to distinguish control flow and data manipulation patterns.；Train on more diverse negative examples to reduce false positives from boilerplate code.

### case_id=3339 FP lexical_or_api_overlap

- 方法: `retrieveQ` vs `downloadModel`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Retrieves the string content of a text resource from a given URL.
- B 摘要: Downloads an RDF model from a given URL and returns the model object.
- 静态失败原因: Static BERT/GraphCodeBERT likely over-indexed on overlapping API tokens (URL, URLConnection, InputStream) and the similar control flow (open, read, close), missing the deeper semantic difference in the reading and returning logic. The model may have been biased by lexical similarity of structural patterns.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled non-clone because the core functionality is different: one is generic text retrieval, the other is domain-specific RDF model loading. Despite sharing boilerplate URL connection code, the semantic purpose and output types are distinct, so BCB considers them non-clones.
- 共享行为: Both open a URL connection and get an input stream；Both read from the input stream and close it；Both use similar exception handling structure (though A throws, B catches)
- 行为差异: A returns a String built from lines; B returns an RDF Model object；A appends newlines between lines; B reads model directly from input；B sets HTTP request properties (Accept, Accept-Language); A does not；B catches exceptions and wraps in RuntimeException; A throws them
- 修正建议: Incorporate dataflow analysis to track how input is processed and what is returned；Use type information to distinguish return types (String vs Model)；Add contrastive training with examples of similar API usage but different semantics

### case_id=3340 FN partial_functionality

- 方法: `doVersionCheck` vs `seeURLConnection`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Checks for a new version by reading a version file from a URL and displays UI dialogs accordingly.
- B 摘要: Reads content from a URL and logs it to debug output.
- 静态失败原因: Static models rely on token overlap and surface-level patterns; low Jaccard similarity (0.194) and different method names, error handling, and post-processing led to a non-clone prediction, missing the abstract functional similarity in URL reading.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as implementing the common pattern of fetching and parsing text from a URL, thus focusing on the shared I/O structure rather than the disparate application logic.
- 共享行为: Both open a URL connection and read lines via BufferedReader；Both close the reader after reading
- 行为差异: A performs version comparison and shows UI dialogs; B logs the content；A handles IOException with error dialog; B throws Exception outward；A shows and hides a wait cursor
- 修正建议: Incorporate dataflow analysis to capture common I/O patterns；Use contrastive learning to recognize abstract structural clones；Enhance training with examples of partially overlapping functionality

### case_id=3341 FP lexical_or_api_overlap

- 方法: `handledRun` vs `checkForUpgrade`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Downloads game data XML from a URL, compares version numbers, and if newer, downloads and saves the data file.
- B 摘要: Checks for software upgrades by querying a remote server for license and available versions, then updates database and UI accordingly.
- 静态失败原因: The model likely overfitted to shared API patterns (URL, BufferedReader, version comparison) and the high-level concept of 'updating', ignoring deeper semantic differences.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled as non-clone because despite both being update routines, the domain, data, and overall functionality are very different, with low lexical similarity (Jaccard 0.092).
- 共享行为: Both perform version checking and potentially download/update from a remote server.
- 行为差异: Different targets (game data vs. software upgrade with license management)；Different data formats and sources；Different error handling and UI interactions；Database operations present only in B
- 修正建议: Improve model's ability to distinguish domain and context；Incorporate more structural or data-flow information；Use task-specific fine-tuning on clone detection datasets with diverse semantics

### case_id=3342 FP lexical_or_api_overlap

- 方法: `actionPerformed` vs `convert`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Handles action events to configure GUI settings like file paths for Graphviz and ImageMagick, date format, look and feel, etc.
- B 摘要: Converts an ACRNEMA medical image file to DICOM format by parsing and writing pixel data.
- 静态失败原因: Static BERT models may have been misled by the presence of common Java constructs (e.g., try-finally, if blocks with multiple conditions) or token similarities like 'File' and 'InputStream' that appear in both, but the actual logic is unrelated.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would mark as non-clone because the functions have completely different semantics and no partial functionality overlap.
- 共享行为: No shared behavior
- 行为差异: Function A is a GUI event handler for saving preferences; Function B is a file format converter.；Different domains: desktop application configuration vs. medical image conversion.；No common APIs beyond basic Java I/O (File, InputStream, OutputStream) but used in entirely different ways.
- 修正建议: Improve training data to include more diverse non-clone pairs with low token similarity.；Use structure-aware models like GraphCodeBERT that better capture data flow and control flow differences.；Add attention to method names and domain-specific APIs (e.g., DICOM tags vs GUI components).

### case_id=3343 FP lexical_or_api_overlap

- 方法: `getVersion` vs `getFullScreenUrl`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Downloads a version string from a remote URL.
- B 摘要: Parses a YouTube page to extract video parameters and constructs a download URL.
- 静态失败原因: Static BERT models like GraphCodeBERT rely on token-level features and may overemphasize overlapping API calls (URL, URLConnection, BufferedReader) while missing the semantic context that the operations are fundamentally different.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically requires high functional similarity; these functions have different purposes (version retrieval vs. URL construction) and only share boilerplate I/O code, so BCB labels as non-clone.
- 共享行为: Open URL connection；Read lines from input stream；Use BufferedReader and InputStreamReader
- 行为差异: Different input: getVersion uses hardcoded URL, getFullScreenUrl uses instance variable ytUrl；Different output: getVersion returns the first line of the response, getFullScreenUrl constructs a URL from parsed parameters；Different processing: getVersion just reads first line, getFullScreenUrl searches for specific substring and parses multiple fields；Different error handling: getVersion returns null on error, getFullScreenUrl prints error and returns empty string
- 修正建议: Increase weight on structural logic beyond API calls；Incorporate dataflow analysis to distinguish variable usage patterns；Train on more discriminative examples that share API but differ in logic

### case_id=3344 FP lexical_or_api_overlap

- 方法: `encriptPassword` vs `perform`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Hashes a password string using MD5 and returns the hex string.
- B 摘要: Processes an HTTP request to classify a concept, involving session management, form parameter extraction, XML creation, HTTP POST, and result parsing.
- 静态失败原因: The static model likely overestimated similarity due to superficial lexical overlap (e.g., 'String', 'Exception', 'catch') or may have been confused by the annotation '@Digester' which hints at encryption, but the functions are structurally and semantically unrelated.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB correctly labels this as non-clone because the functions have completely different purposes and no significant shared functionality.
- 行为差异: Function A is a simple one-line encryption; B is a long multi-step Struts action.；A returns a hex string or null; B returns an ActionForward for navigation.；A uses only standard Java security libraries; B uses a web framework, HTTP connections, and custom beans.；A has no side effects; B modifies session attributes and performs I/O.
- 修正建议: Incorporate deeper structural analysis using AST or CFG.；Use contrastive learning to emphasize semantic differences.；Reject pairs with very low token Jaccard and high length disparity.

### case_id=3345 FN partial_functionality

- 方法: `modifyApplicationMessage` vs `copy`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Modifies a specific message in a locale-specific properties file, copying the English file if needed.
- B 摘要: Copies a file from source to destination using a byte buffer.
- 静态失败原因: Static models like GraphCodeBERT may focus on overall control flow and purpose, which differ significantly; the low token Jaccard (0.165) also indicates low lexical overlap, causing the model to miss the partial file copy similarity embedded within A.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely labeled as clone due to the presence of file copying subroutines in both functions, considering them similar under broad Type-3/4 partial functionality criteria.
- 共享行为: Both perform file copying from one location to another.；Both use I/O streams for reading and writing.；Both check for file existence before operation.
- 行为差异: A operates on properties files with key-value format and modifies or adds a specific message; B is a generic byte-level copy.；A handles character encoding (Reader/Writer) while B uses byte streams (InputStream/OutputStream).；A includes error handling with printStackTrace; B throws IOException.；A has logic to add missing message; B does not.
- 修正建议: Train with more emphasis on subgraph matching or weakly labeled partial clones.；Incorporate AST-based diff techniques to detect similar code fragments within different contexts.

### case_id=3346 FN benchmark_preference_bias

- 方法: `copyToDir` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Copies a file to a specified directory.
- B 摘要: Launches a Hibernate configuration for a NexOpen project in Eclipse.
- 静态失败原因: Static BERT/GraphCodeBERT likely correctly identified no semantic similarity due to low token Jaccard and different API usage; the model did not make an error here, but the BCB label is incorrect. The static prediction of non-clone is correct.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have considered both functions as involving file operations (A copies files; B writes to files like pom.xml and reveng file), but the core functionality is entirely different. The annotation likely mislabeled this as clone due to superficial file-related I/O.
- 行为差异: Function A performs file I/O (copying a single file).；Function B orchestrates a multi-step Eclipse launch involving XML parsing, property handling, and project lifecycle.；A is simple and self-contained; B is complex with many dependencies on Eclipse and Hibernate APIs.；A handles IOExceptions; B handles CoreExceptions and uses progress monitors.
- 修正建议: Review BCB annotation for this pair; it appears to be a false positive in the benchmark.；Consider filtering pairs with very low token overlap and no clear functional similarity.；Train models with richer semantic understanding to ignore superficial API overlaps.

### case_id=3347 FN partial_functionality

- 方法: `modifyApplicationMessage` vs `handle`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Modifies a localized properties file by updating or adding a key-value pair for a specific locale.
- B 摘要: Handles log file rotation by compressing, archiving, and deleting old log files based on configuration.
- 静态失败原因: The model correctly predicted non-clone (0) because it likely captured the distinct semantic intents and high-level operations (i18n vs. log rotation) despite lexical overlap. The BCB label may be an annotation error or a result of overly broad clone criteria.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled these as clones due to superficial structural similarities (file reading/writing, try-catch, loops) and perhaps a broad interpretation of 'file modification' functionality, but they serve entirely different purposes and are not semantically equivalent.
- 共享行为: Both involve file I/O operations (reading/writing files) and use try-catch for exception handling.
- 行为差异: Function A modifies i18n properties files; Function B rotates and compresses log files.；Function A reads a base English file and creates a locale file if missing; Function B handles compression, archiving, and deletion of old logs.；Function A updates a specific key-value pair; Function B manages file rotation schedules and cleanup.
- 修正建议: Re-examine BCB annotation for this pair; it may be a mislabel.；If BCB label is correct, improve model to ignore low-level I/O patterns and focus on high-level semantics.

### case_id=3348 FP lexical_or_api_overlap

- 方法: `loadSourceCode` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Loads and syntax-highlights source code from a resource file into HTML.
- B 摘要: Performs Google image search, parses HTML to extract image URLs, and sets an album art icon.
- 静态失败原因: Static BERT/GraphCodeBERT likely over-relied on lexical and API-level overlap (e.g., URL, BufferedReader, try-catch) and similar method length, mistaking surface-level patterns for semantic similarity.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels as not clone because the functions have entirely different purposes and no shared functionality beyond trivial boilerplate.
- 共享行为: Uses try-catch for exception handling；Reads from a URL via BufferedReader or InputStreamReader
- 行为差异: Function A reads local file resources; Function B makes HTTP requests to Google；Function A applies syntax highlighting; Function B extracts image URLs from HTML；Function A returns nothing but sets a class field; Function B updates GUI components
- 修正建议: Train with more diverse non-clone pairs that share common APIs but different semantics；Incorporate control-flow and data-flow analysis to distinguish different data transformations；Use attention masking to focus on semantic intent rather than boilerplate

### case_id=3349 FN benchmark_preference_bias

- 方法: `upload` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Copies an image file to a hardcoded destination and returns 'show'.
- B 摘要: Builds a website for editing by processing pages, transforming XML, and writing output files.
- 静态失败原因: Static BERT/GraphCodeBERT models rely heavily on token overlap and API usage; both use FileInputStream/FileOutputStream, but the low Jaccard similarity (0.041) made the model correctly predict non-clone, contradicting the BCB label which may be erroneous.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB likely mislabeled this pair as clones due to superficial file I/O overlap, but the functions lack any meaningful functional similarity.
- 共享行为: Both perform file I/O operations using FileInputStream and FileOutputStream.
- 行为差异: Code A is a simple, single file copy; Code B is a complex multi-file processing and transformation pipeline.；Code A returns a constant string; Code B modifies files and has no return value.；Code A has no parameters; Code B has 8 parameters and uses numerous external libraries.；Code A is very short (15 lines); Code B is extremely long (truncated but clearly hundreds of lines).
- 修正建议: Re-evaluate the BCB annotation for this pair to ensure correctness.；Incorporate structural and complexity features to distinguish simple from complex file operations.；Use data flow analysis to capture the different computational purposes.

### case_id=3350 FN partial_functionality

- 方法: `getFile` vs `downLoadZippedFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, optionally modifies its endpoint, and saves it to a local temporary file, returning the file path as a String.
- B 摘要: Downloads a zipped file from a URL, extracts it to a destination directory, and returns the directory as a URL.
- 静态失败原因: Static BERT models rely on lexical and structural similarity; low token Jaccard and different method names, APIs (NIO vs IOUtils), and error handling patterns likely obscured the shared downloading behavior.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as instances of 'downloading a file from a URL and storing it locally', deeming additional processing (XML modification vs unzipping) as non-essential to the core clone relationship.
- 共享行为: Both open a URL connection and download content from a remote URL.；Both write the downloaded content to a local file.；Both close resources after use.
- 行为差异: A downloads a WSDL file and may modify XML before saving; B downloads a zip file and unzips it.；A uses NIO channels and explicit file checking; B uses IOUtils.copy and temp file management.；A returns a String path; B returns a URL.；A has structured exception handling for AxisFault; B throws generic Exception.
- 修正建议: Incorporate dataflow analysis to identify common I/O patterns (open stream -> write).；Enhance training with diverse Type-3/Type-4 clones emphasizing core semantic actions.；Utilize semantic role labeling or abstract syntax tree paths to capture high-level intent.

### case_id=3351 FP lexical_or_api_overlap

- 方法: `main` vs `decodeFileToFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Generates adapter code from a Prolog file and writes it to a JAR file.
- B 摘要: Decodes a Base64 encoded file and writes the decoded content to another file.
- 静态失败原因: Static model over-relied on common lexical tokens (File, IOException, try, catch, while, read, write) and structural similarity, overlooking the semantic divergence in purpose and logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels as non-clone because core functionalities are completely different; only superficial boilerplate patterns (file I/O, exception handling) overlap, not the actual computation.
- 共享行为: Both involve file I/O with try-catch blocks；Both use input and output streams；Both handle exceptions with printStackTrace
- 行为差异: Different main purpose (adapter generation vs. Base64 decoding)；Different input/output types (Prolog file to JAR vs. Base64 file to decoded file)；A is a void main method, B returns boolean success；A performs complex parsing and code generation, B does simple stream copy
- 修正建议: Use dataflow-aware models to track variable transformations and types；Incorporate method-level context (name and signature)；Add contrastive training for distinguishing boilerplate from substantive behavior

### case_id=3352 FN benchmark_preference_bias

- 方法: `doBody` vs `doGet`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.85`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Reads a file from the filesystem and copies its contents to the HTTP response output stream, with error logging and stream cleanup.
- B 摘要: Handles an HTTP GET request by retrieving a page parameter, looking up a page object, checking user visibility, rendering the page to the response, caching if not editable, and logging request details.
- 静态失败原因: The model likely correctly predicted non-clone because the token overlap is very low (0.043) and the functions differ significantly in length and semantics. However, if the model uses only structural features, it may have missed that both involve writing to an HTTP response; but here it correctly rejected the pair.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might have labeled these as clones due to both being HTTP response handlers that use similar boilerplate (streams, try-catch), despite vastly different business logic. BCB sometimes accepts broad type-4 similarity if the core purpose of serving a response is seen as equivalent.
- 共享行为: Both write data to the HTTP response；Both use try-catch-finally for resource management；Both are part of Java servlet-like request handling
- 行为差异: A simply streams a static file; B involves dynamic page lookup, authentication, logging, and caching；A has minimal control flow (if any); B has multiple branches for missing page, forbidden access, caching conditions；A uses IOUtils.copy; B writes HTML output and handles various errors with different status codes
- 修正建议: Re-evaluate BCB label for this pair; consider if it is a mislabel；In training, incorporate more fine-grained semantic similarity rather than broad task-level similarity；For models, ensure they capture functional differences beyond API usage

### case_id=3353 FP lexical_or_api_overlap

- 方法: `setBundleInfoName` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a configuration file from URL and updates bundle names in a list based on key-value pairs.
- B 摘要: Fetches Google image search results and extracts image URLs into a list.
- 静态失败原因: The model overemphasized common API usage (URL, BufferedReader, readLine) and exception handling patterns, leading to a high similarity score even though the semantic goal is different.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB disregards common boilerplate; the core functionality is entirely different, so they are not clones.
- 共享行为: Both read from a URL using BufferedReader；Both handle IO exceptions
- 行为差异: Different parsing logic (key-value vs regex split)；Different output (updates list vs returns boolean)；Different purpose
- 修正建议: Improve model to distinguish between boilerplate and core logic；Use dataflow analysis to capture different data transformations

### case_id=3354 FP boilerplate_overlap

- 方法: `readData` vs `tail`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Reads configuration strings and a file (tibwn.ini) to populate various character sets and hash maps for Tibetan transliteration.
- B 摘要: Implements the Unix tail command with -f option to display the last 1024 bytes of a file and optionally follow new data.
- 静态失败原因: The static BERT/GraphCodeBERT model likely over-prioritized superficial similarities such as common I/O related tokens (IOException, file, close, Path, etc.) and ignored the overall semantic difference.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled this as non-clone because the functions have completely different purposes and only share trivial I/O boilerplate; they are not semantically related.
- 共享行为: Both read from files using Java I/O；Both use try-catch for IOException
- 行为差异: Function A populates multiple data structures (sets, maps) from tokenized strings and a file with specific column format; Function B reads a file from an offset and outputs bytes to stdout；Function A involves parsing many string tokens and building look-up tables; Function B is a simple file reading and copying utility；Function A uses StringTokenizer and maps; Function B uses FSDataInputStream and seeks；Function A has complex column-based processing; Function B has simple byte copying
- 修正建议: Train on more diverse negative examples that share I/O boilerplate but differ in logic；Incorporate structure-aware features like data flow or call graph；Use contrastive learning to penalize spurious correlations from common library usage

### case_id=3355 FP partial_functionality

- 方法: `getRequestContent` vs `GetResponse`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches only the first line of content from a URL using HTTP GET and throws exceptions.
- B 摘要: Fetches entire content from a URL using HTTP GET with response code check and exception handling.
- 静态失败原因: Static models like BERT rely on lexical and structural similarity; both functions share API calls (HttpURLConnection, BufferedReader) and similar control flow, causing false positive despite semantic difference in reading behavior.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: None
- 共享行为: Both perform HTTP GET request；Both open HttpURLConnection and read from input stream；Both return a String with content
- 行为差异: A reads only first line; B reads all lines；A throws Exception; B catches exceptions and returns null；A takes URL as String; B takes URL object；A does not set request method or check response code; B sets GET method and checks HTTP_OK
- 修正建议: Incorporate data flow analysis to distinguish single read vs loop；Use more fine-grained semantic matching that captures output differences；Add training examples with similar API but different reading patterns

### case_id=3356 FN benchmark_preference_bias

- 方法: `testNetworkHTTP` vs `readIntoList`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.8`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Opens multiple HTTP connections and reads lines to consume response bodies, no processing.
- B 摘要: Reads HTML from a single URL, parses it to extract command names, creates menu items with action listeners.
- 静态失败原因: Static BERT likely relied on token-level similarity and structural features, correctly identifying low overlap (Jaccard=0.186) and different method signatures, thus predicting non-clone, missing the potentially intended broad clone relationship.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled these as clones due to broad Type-3/4 criteria: both perform HTTP GET and line-by-line reading via BufferedReader, despite different purposes and processing.
- 共享行为: Both use BufferedReader to read lines from a URL stream；Both catch exceptions and print stack traces；Both involve HTTP connections
- 行为差异: Function A reads from multiple URLs and discards data; Function B reads from one URL and processes data；Function A has a finally block to disconnect; Function B closes the reader in try block；Function B creates UI components and registers event listeners; Function A has no side effects beyond I/O；Function B parses HTML using string index operations; Function A does no parsing
- 修正建议: Improve training data to include more Type-4 clones with similar roles but different implementations；Use data-flow and API usage patterns (e.g., 'openStream', 'readLine') as additional features；Consider functional role annotations (e.g., 'network I/O') to group such functions

### case_id=3357 FP lexical_or_api_overlap

- 方法: `actionPerformed` vs `upload`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Handles UI action events to set file paths and preferences for Graphviz, ImageMagick, and other settings, with UI updates.
- B 摘要: Uploads an image file to a fixed directory by copying it using IOUtils and returns a navigation string.
- 静态失败原因: The static model may have been misled by overlapping use of file I/O classes (File, FileOutputStream) and similar API calls (e.g., getSelectedFile, getAbsolutePath), causing false positive due to lexical or API overlap.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels these as non-clones because they perform entirely different high-level tasks (UI event handling vs file upload), despite sharing some low-level I/O operations.
- 共享行为: Both perform file system operations (reading/writing files).；Both use Java I/O classes (File, FileOutputStream, etc.).
- 行为差异: Function A is a complex event handler with multiple conditional branches and extensive UI interactions.；Function B is a simple file copy operation with no UI or branching.；Function A interacts with UI components and stores preferences; Function B is a web-like upload returning a string.；Function A uses JFileChooser and sets UI state; Function B directly uses file streams.
- 修正建议: Improve model to consider broader context and semantic role of I/O operations.；Add more diverse negative examples with similar API usage but different intent.；Use control flow or data flow features to distinguish event handlers from simple utility functions.

### case_id=3358 FP boilerplate_overlap

- 方法: `getPasswordHash` vs `perform`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Computes MD5 hash of a password string.
- B 摘要: Performs a Struts action for classification, involving network I/O and session management.
- 静态失败原因: Static BERT likely overgeneralized from common Java boilerplate patterns (StringBuffer, try-catch, getBytes) and missed the radical difference in API usage and control flow complexity.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels these as non-clones because they perform entirely different tasks: one is a cryptographic utility, the other is a web application controller. No meaningful functional overlap.
- 共享行为: Both use StringBuffer to accumulate string output.；Both have try-catch blocks for exception handling.；Both iterate over arrays or collections.
- 行为差异: Function A is a simple hashing function; Function B is a complex web action handler.；Function B involves network communication (URLConnection), session attributes, and multiple parameter handling.；Function A has no conditional branching beyond exception; Function B has multiple conditionals and error paths.；Function B uses many external libraries and classes (Struts, logging, XML parsing) absent in A.
- 修正建议: Incorporate data-flow analysis to distinguish simple data transformation from complex control flow.；Use structural or graph-based features that capture unique API call sequences.；Increase sensitivity to functional purpose by analyzing method signatures and external library usage.

### case_id=3359 FN benchmark_preference_bias

- 方法: `main` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.75`
- 推荐路线: `preference_memory_with_manual_audit`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Downloads a KMZ file from a URL and extracts its ZIP entries to the current directory.
- B 摘要: Copies a source file to a destination file using FileChannel.
- 静态失败原因: Static models rely on token/structural similarity (Jaccard 0.0625) and miss the broader functional overlap that BCB annotators might consider as semantically similar.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider both as file copying operations under broad Type-4 similarity, as both transfer data from a source to a destination with I/O handling, even though implementations differ significantly.
- 共享行为: Both perform file I/O operations involving reading from an input source and writing to an output destination.；Both use streams/channels for data transfer.
- 行为差异: A fetches data from a URL and handles ZIP extraction; B copies a single file directly.；A throws exceptions and does not return a status; B catches exceptions and returns a boolean success indicator.；A prints progress messages; B does not.
- 修正建议: Incorporate lightweight functional flow analysis to detect high-level I/O operations.；Use graph-based representations to capture data flow similarities.；Train on BCB-specific annotation biases.

### case_id=3360 FN partial_functionality

- 方法: `main` vs `copy`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a hardcoded URL, unzips it, and writes each entry to a file.
- B 摘要: Recursively copies a file or directory from source to destination using NIO FileChannel and MappedByteBuffer.
- 静态失败原因: The model likely relied on low token overlap and different API usage (zip vs NIO), missing the high-level similarity in file copying behavior. It also overfitted to method names and structure.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels Type-4 clones based on common file I/O functionality. Both methods ultimately copy data from one location to files, albeit with different sources and techniques.
- 共享行为: Both involve reading from an input source and writing to output files.；Both handle I/O exceptions.；Both use buffering mechanisms.
- 行为差异: A reads from a network URL and unzips; B reads from local filesystem.；A writes multiple files from zip entries; B copies a single file or directory structure.；A uses ZipInputStream and FileOutputStream; B uses FileChannel and MappedByteBuffer.；A is a main method with hardcoded URL; B is a reusable utility method with two File parameters.
- 修正建议: Incorporate dataflow analysis to capture the read-process-write pattern.；Use higher-level semantic embeddings that abstract over specific APIs.；Train with more Type-4 examples from BCB to learn weak functional similarity.

### case_id=3361 FN benchmark_preference_bias

- 方法: `getFile` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.8`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies the endpoint attribute in the XML, and saves it to a temporary file, returning the file path.
- B 摘要: Reads a text file, applies a line-wrap filter and a title-case filter, then writes the result to another file.
- 静态失败原因: Low token overlap (8%) and differing method signatures/names likely caused the model to focus on lexical differences rather than any abstract structural similarity, leading to a non-clone prediction.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have considered both as 'file manipulation' utilities that read from a source, apply a transformation, and write to a file, despite the completely different domains and logic.
- 共享行为: Both perform file I/O operations (read/write) using streams
- 行为差异: Source of data: URL vs local file；Processing: XML manipulation vs text filtering；Output: returns file location vs void；Error handling: multiple catch blocks vs throws IOException
- 修正建议: Improve annotation consistency by clarifying that domain-specific transformations (XML vs text) are not considered similar；Train models to recognize broader I/O patterns only if explicitly required

### case_id=3362 FP boilerplate_overlap

- 方法: `send` vs `main`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Sends an email with configurable options such as HTML, charset, headers, priority, and attachments, using JavaMail and Hibernate for persistence.
- B 摘要: Reads a Prolog file, parses it to generate adapter classes, writes them into a JAR file, and handles command-line arguments.
- 静态失败原因: The static BERT/GraphCodeBERT model likely falsely predicted a clone due to over-reliance on common Java boilerplate patterns (e.g., try-catch, File, IOException) and insufficient emphasis on high-level semantics and method purpose.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would label these as non-clones because they perform completely different tasks with no shared functionality; token Jaccard similarity is very low (0.08) and any overlap is purely boilerplate (e.g., exception handling, variable declarations).
- 共享行为: Both use try-catch blocks for exception handling.；Both perform I/O operations (email sending vs file processing).
- 行为差异: Method a focuses on email composition and sending with various headers and priority.；Method b focuses on parsing Prolog code and generating Java class files.；Different method signatures and purposes (instance vs static main).；No overlap in core functionality.
- 修正建议: Augment training data with more diverse examples to reduce sensitivity to boilerplate patterns.；Incorporate method name and class context as additional features to distinguish functional differences.；Use contrastive learning to push apart embeddings of functionally different methods even if they share syntactic patterns.

### case_id=3363 FN partial_functionality

- 方法: `runScript` vs `run`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads the content of a script file from a URL and returns it as a string, with error handling returning 'error!' on failure.
- B 摘要: Performs an HTTP GET request with basic authentication to a URL, reads the response line by line, and stores the result in a field, also tracking time and setting a finish flag.
- 静态失败原因: The model likely focused on low token overlap and different method signatures, missing the high-level similarity of URL reading due to superficial differences in implementation and error handling.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label these as clones because both involve reading from a URL over HTTP and returning/using the text content, which is a commonly seen Type-3/Type-4 pattern where partial functionality similarity is accepted.
- 共享行为: Both open a URL connection and read the content into a string.
- 行为差异: Function A returns the content as a String, while Function B stores it in a field and has void return.；Function A reads byte by byte using BufferedInputStream, Function B reads line by line using BufferedReader.；Function B includes HTTP authentication and additional side effects (finish flag, timestamp), Function A does not.；Error handling: A returns 'error!' string, B stores exception in a field without returning.
- 修正建议: Incorporate data flow analysis to detect common I/O patterns.；Use structural features that capture high-level API calls (URL, InputStream) rather than exact token matches.；Train on more diverse examples of URL reading functions.

### case_id=3364 FN benchmark_preference_bias

- 方法: `modifyApplicationMessage` vs `saveFileData`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.2`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Modifies a localized properties file by updating or adding a message key-value pair.
- B 摘要: Saves file data by copying file channels, handling image metadata, and cleaning up thumbnail files.
- 静态失败原因: The static model likely failed to detect the clone because it relied on lexical overlap and code structure, but the two functions have low token Jaccard (0.13) and different APIs (Properties vs FileChannel), so it correctly predicted non-clone; BCB's label is questionable.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might consider them clones due to both being file-manipulation utilities with exception handling and resource management, but this is a very broad interpretation.
- 共享行为: Both involve file I/O operations
- 行为差异: A manipulates properties files for i18n; B copies file channels and handles images；A reads and writes text lines; B uses FileChannel and BufferedImage；A focuses on locale-specific message editing; B on saving asset files with versioning
- 修正建议: Improve models to ignore superficial file I/O similarity and focus on core functionality

### case_id=3365 FP lexical_or_api_overlap

- 方法: `readRemoteFile` vs `executePost`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a remote file content via HTTP GET (URL.openStream) and returns concatenated string.
- B 摘要: Executes an HTTP POST request with parameters and returns the response body as string.
- 静态失败原因: Static BERT/GraphCodeBERT may overemphasize the structural similarity of URL opening, BufferedReader, and while-loop reading lines, while missing the crucial difference in HTTP method and the presence of output stream writing in executePost.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels these as non-clones because they perform different HTTP methods and have distinct I/O operations (one only reads, the other writes). The core functionality differs significantly despite some shared boilerplate.
- 共享行为: Both open a URL connection；Both read response content using BufferedReader；Both build a response string from lines
- 行为差异: Function A is read-only (GET), Function B sends POST parameters；Function A uses URL.openStream, Function B uses HttpURLConnection with POST method；Function B writes data to the output stream, Function A does not；Error handling differs: A continues on IOException, B returns null on exception
- 修正建议: Enhance model to distinguish HTTP methods (GET vs POST) and differentiate between read-only and write operations；Incorporate data flow analysis to track whether output is written to the connection

### case_id=3366 FN lexical_or_api_overlap

- 方法: `main` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a dataset and zip file, parses rules from .out entries, evaluates performance, and prints average.
- B 摘要: Retrieves a resource by URL, caches it locally, and returns an InputStream, with caching logic and HTTP handling.
- 静态失败原因: The model focused on low token overlap (Jaccard 0.14) and failed to capture the high-level functional similarity of stream manipulation that BCB annotators considered, leading to a false negative.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may have labeled this as clone due to overlapping I/O operations and stream handling, possibly considering both as file/resource manipulation functions under broad Type-4 functional equivalence, or it could be an annotation error.
- 共享行为: Both read from input streams；Both write to output streams；Both use buffered I/O；Both handle exceptions with try-catch
- 行为差异: A evaluates machine learning models; B caches remote resources；A processes multiple zip entries; B handles a single resource；A uses RuleParser and ProbabilisticRuleList; B uses URLConnection and HTTP；A outputs performance metrics; B returns an InputStream
- 修正建议: Improve annotation guidelines to avoid labeling I/O-similar but semantically different functions as clones；Use more structured semantic matching beyond token overlap；Incorporate data flow and control flow analysis to distinguish file processing from resource caching

### case_id=3367 FP boilerplate_overlap

- 方法: `doRawRequest` vs `getRequestContent`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Sends POST request with given data to a fixed URL, reads entire response line by line, returns full response as string.
- B 摘要: Opens a connection to given URL (GET), reads first line of response, returns that line.
- 静态失败原因: Static BERT models may over-rely on token similarity (URL, openConnection, BufferedReader) and miss structural differences like output stream usage and loop vs single read.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels non-clone due to different HTTP methods and output handling; the core functionality differs significantly despite shared URL connection boilerplate.
- 共享行为: Both open an HTTP URL connection；Both read from input stream using BufferedReader；Both return a string
- 行为差异: Function A uses POST with output stream (writes data), B uses GET without writing；Function A reads all lines in a loop, B reads only the first line；Function A has fixed URL, B has parameterized URL；Function A closes writer and reader, B disconnects instead of closing writer
- 修正建议: Incorporate dataflow analysis to detect write operations；Add attention to control flow structures (loops, conditionals)；Use graph neural networks that capture AST structures with node types for I/O operations

### case_id=3368 FN partial_functionality

- 方法: `getResourceAsStream` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a resource from a URL or retrieves from cache, returning an InputStream.
- B 摘要: Copies a source file to a destination file using FileChannel.
- 静态失败原因: The static BERT/GraphCodeBERT model likely relied on token-level or structural similarity, which is low (Jaccard 0.08). It may not have captured the high-level semantic pattern of data transfer because the APIs and control flow differ significantly. The model might have been distracted by the complex conditional logic and HTTP-specific code in A, leading to a prediction of non-clone.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB might have considered these as Type-4 clones because both implement a common pattern of reading data from a source and writing to a destination, albeit with different sources/destinations and additional logic. The broad functionality of 'transferring data from one location to another' might be seen as semantically similar.
- 共享行为: Both involve reading from an input source and writing to an output destination；Both handle file I/O operations；Both use streams or channels for data transfer
- 行为差异: A handles HTTP connections, caching, and conditional updates; B is a simple file copy；A returns an InputStream; B returns void and writes directly to file；A has extensive error handling with try-catch; B throws IOException；A uses multiple I/O classes (BufferedInputStream, BufferedOutputStream, FileInputStream, FileOutputStream); B uses FileChannel
- 修正建议: Improve model's ability to recognize high-level semantic patterns across different interfaces；Incorporate data flow analysis to identify common I/O patterns；Use contrastive learning with hard negatives that share only partial functionality

### case_id=3369 FP partial_functionality

- 方法: `actionPerformed` vs `copy`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: GUI event handler that processes various action commands (e.g., GRAPHVIZ, IMAGEMAGICK) by opening file chooser dialogs and saving user preferences.
- B 摘要: Utility method to copy a file using FileChannel and MappedByteBuffer.
- 静态失败原因: Static BERT/GraphCodeBERT may have over-emphasized common structural patterns (e.g., try-finally, File operations) or was misled by the large context of Function A which contains file-related operations, while lacking understanding of the high-level purpose.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB marks this as non-clone because the functions have completely different purposes and code structures; one is a GUI event handler, the other a file copy utility.
- 共享行为: Both interact with files, but at low level and different purpose
- 行为差异: Function A is a complex GUI event handler with conditional logic; Function B is a simple file copy utility；Function A saves preferences and updates UI; Function B performs pure I/O；Function A uses JFileChooser and Swing; Function B uses NIO channels；Function A has side effects on global state; Function B has no side effects beyond file I/O
- 修正建议: Improve model's ability to distinguish between different high-level tasks (GUI event handling vs. utility function)；Add more negative examples with similar low-level operations but different purposes；Incorporate structural context (e.g., method name, class context) to disambiguate

### case_id=3370 FP lexical_or_api_overlap

- 方法: `postRequest` vs `loadURL`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Sends an HTTP POST request with URL-encoded form data and returns the response body as a string.
- B 摘要: Downloads content from a URL with optional Basic authentication, writes it to a temporary file, and updates a UI label with download progress.
- 静态失败原因: A static BERT model likely over-relied on common API sequence (URLConnection, BufferedReader, readLine) and similar control flow, ignoring the distinct parameters and output destinations.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels as non-clones when methods differ in HTTP method, data transmission, output handling, and user interaction, despite sharing the pattern of reading an HTTP response.
- 共享行为: Both open a URLConnection to a remote resource.；Both read the response line by line using BufferedReader.；Both handle I/O through streams.
- 行为差异: A uses POST method (setDoOutput(true)) and sends form data; B uses GET (no output) and may include Basic auth header.；A returns the response body as a string; B writes response to a temporary file and updates a UI label.；A handles exceptions by returning null; B throws IOException.；A accepts a URL string and a HashMap; B accepts a URL object, username, password, and a JLabel.
- 修正建议: Incorporate dataflow analysis to distinguish output sinks (string vs file).；Add attention to method signatures and parameter types.；Use graph-based representations that capture request properties and authentication details.

### case_id=3371 FN benchmark_preference_bias

- 方法: `sendExceptionToServer` vs `loadSourceCode`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.1`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Sends exception details to a remote server via HTTP POST and prints the response.
- B 摘要: Loads source code from a file, applies syntax highlighting, and stores as HTML.
- 静态失败原因: The static model correctly identified the significant structural and semantic differences due to low token overlap (0.148) and different methods and purposes. It did not consider them clones, which aligns with functional analysis but not with the BCB label.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as a clone based on a broad interpretation of Type-4 functional similarity, such as 'I/O operations' or 'network communication', but the actual functionality is very different. The low token overlap suggests it is likely a labeling error in BCB.
- 共享行为: Both use URL, InputStream, InputStreamReader, BufferedReader, and read lines.；Both handle I/O exceptions with try-catch blocks.；Both involve reading from a stream (though different purposes).
- 行为差异: sendExceptionToServer writes data to a server and reads the response; loadSourceCode only reads from a resource.；sendExceptionToServer builds a URL-encoded query string; loadSourceCode reads lines and applies syntax highlighting.；sendExceptionToServer handles an exception object; loadSourceCode accesses a file resource.；Output is printed in sendExceptionToServer; output is stored in a member variable in loadSourceCode.
- 修正建议: Re-evaluate BCB annotation for this pair to confirm if it is a mislabel.；If BCB label is correct, the model needs to capture very abstract shared behavior like 'I/O with readers', but this is too general for clone detection.；Improve model robustness to noisy labels by using confidence calibration or noise-tolerant training.

### case_id=3372 FP lexical_or_api_overlap

- 方法: `run` vs `readVersion`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Downloads and parses a vector tile from a URL, constructs geometry collection, and adds to data loader.
- B 摘要: Reads a resource file 'version', extracts Version, Revision, and Date fields, and sets instance variables.
- 静态失败原因: Static BERT models like GraphCodeBERT can be misled by high lexical overlap (common API calls: URL, BufferedReader, readLine, openStream, IOException, close) and similar boilerplate (try-catch, while loop), ignoring the distinct semantics and data flow.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels non-clones when functions have completely different high-level functionality, even if they share low-level I/O patterns. Here, one is about tile fetching/processing, the other about version info extraction, so no functional similarity.
- 共享行为: Both open a URL connection and read lines with BufferedReader
- 行为差异: Purpose: A builds tile data for map rendering; B reads version metadata；Output: A produces geometry collection and adds to data structures; B sets three string/date fields；Parsing: A concatenates all lines into one JSON string; B parses key=value lines；Error handling: A has multiple return points and synchronization; B uses try-catch-finally with printStackTrace
- 修正建议: Add more training examples that contrast similar I/O patterns but different high-level functionality；Incorporate control flow and data flow analysis to distinguish variable usage and output；Use task-specific fine-tuning with clone pairs that emphasize functional purpose over token similarity

### case_id=3373 FN partial_functionality

- 方法: `copy` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a local file character by character using FileReader and FileWriter.
- B 摘要: Downloads a KMZ file from a URL, opens a ZipInputStream, and extracts each entry to a local file.
- 静态失败原因: Static BERT models rely on token embeddings and have low token overlap (Jaccard 0.17). They may not capture the abstract structural similarity of the read-write loop, especially when function names and method signatures differ (copy vs main). The model might be misled by the different APIs (FileReader vs ZipInputStream) and the presence of URL handling in B.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider this a Type-4 clone because both implement a common pattern of reading and writing data streams in a loop, despite different sources and purposes.
- 共享行为: Both read from an input source and write to an output destination using a while loop until end of stream.
- 行为差异: Function A uses character streams on plain text files; Function B uses byte streams on compressed zip files.；Function A reads from a local file; Function B reads from a URL.；Function A writes to a single output file; Function B extracts multiple entries.
- 修正建议: Use dataflow-based methods that capture control flow and data dependencies.；Augment training with more abstract patterns of I/O loops.；Use graph-based models that represent read-write loops.

### case_id=3374 FP boilerplate_overlap

- 方法: `main` vs `main`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Copies a file using FileChannel and ByteBuffer, requiring exactly two command-line arguments.
- B 摘要: Generates adapter classes from a Prolog file based on command-line arguments, writing them to a JAR.
- 静态失败原因: The model likely overfitted on lexical overlap (common main method boilerplate like 'if (args.length...', 'System.out.println') and ignored the core functional differences, especially given the low token Jaccard indicating overall dissimilarity.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the two functions perform entirely different tasks despite sharing the main method boilerplate, and BCB emphasizes whole-function semantic similarity.
- 共享行为: Both are main methods that check argument length and print usage messages.；Both use command-line arguments for input/output file paths.
- 行为差异: Function A performs a simple file copy; Function B performs complex code generation with multiple steps.；Function A uses NIO channels; Function B uses various file I/O, parsing, and class writing libraries.；Function A has minimal error handling; Function B has extensive error handling and conditional logic.；Function B's output is a JAR file with generated classes; Function A's output is a direct copy of the source file.
- 修正建议: Enhance model to distinguish boilerplate from core logic through structural or dataflow analysis.；Incorporate type and method invocation context to capture functional intent.；Use graph-based representations (e.g., CFG, PDG) to compare actual operations performed.；Weight token-level features by importance, downplaying common Java keywords.

### case_id=3375 FN benchmark_preference_bias

- 方法: `gerarTutorialPage` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Generates a tutorial website by creating directories, copying CSS files, and writing HTML pages.
- B 摘要: Launches a NexOpen project in Eclipse by validating configuration, handling Maven pom files, setting Hibernate properties, and scheduling a project installation action.
- 静态失败原因: The static BERT model likely correctly predicted non-clone due to extremely low token overlap and completely different contexts; however, BCB's label indicates a false negative error, possibly because the model failed to recognize vague semantic similarities that BCB annotators considered.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as clone due to a broad interpretation of Type-4 semantic similarity, considering both functions as performing high-level setup tasks involving file operations and error handling, despite no meaningful functional overlap.
- 共享行为: Both perform file operations and handle exceptions
- 行为差异: Different purpose: website generation vs. Eclipse project launch；Different context: standalone application vs. Eclipse plugin；Different inputs/outputs: no parameters and returns boolean vs. takes multiple parameters and returns void；Different error handling: prints stack trace and shows dialogs vs. throws CoreException and logs
- 修正建议: Re-examine BCB annotation for this pair to ensure consistency；Use human evaluation to validate borderline cases；Incorporate more structural or semantic features to capture high-level similarities

### case_id=3376 FN partial_functionality

- 方法: `loadBinaryStream` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Loads a binary stream into an HTTP response by copying an input stream to the output stream.
- B 摘要: Retrieves a resource via URL, caches it to a local file, and returns a FileInputStream.
- 静态失败原因: Static BERT likely focused on the high-level semantic differences, such as different method signatures and API usage, missing the shared low-level stream copying behavior that BCB considers significant.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as stream copying utilities, where the core operation of reading from an InputStream and writing to an OutputStream is considered equivalent, despite different targets and additional caching logic.
- 共享行为: Both copy an InputStream to an OutputStream.；Both use buffered streams for efficiency.；Both close streams after use.
- 行为差异: A outputs to an HTTP response; B outputs to a local file cache.；B includes network retrieval and caching logic; A does not.；A returns void; B returns an InputStream.
- 修正建议: Layer the comparison: first identify shared I/O patterns, then distinguish contextual differences.；Include functional similarity measures that capture sub-task equivalence.

### case_id=3377 FN partial_functionality

- 方法: `actionPerformed` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads rs IDs from a gzipped file and sends them as POST parameters to NCBI E-utils, outputting the response to System.err.
- B 摘要: Retrieves a resource from a URL with caching: if already cached, returns a FileInputStream from cache; otherwise downloads and caches the resource, then returns a new FileInputStream from the cached file.
- 静态失败原因: The static model likely focused on structural and syntactic differences (e.g., POST vs GET, loop vs conditional caching) and low token overlap, leading it to predict non-clone. However, BCB's broad Type-4 interpretation may consider them similar due to the shared abstract pattern of network I/O and stream handling.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled this as a clone due to similar I/O patterns (URLConnection, stream reading/writing) and use of java.net and java.io classes, possibly considering them as Type-4 semantic clones of 'network resource access with caching' though the actual caching is very different.
- 共享行为: Both open a URLConnection and read from an InputStream；Both close streams in finally-like blocks；Both use try-catch for IOException
- 行为差异: Function A sends a POST request with dynamically constructed parameters, Function B performs a GET request (or defaults) and caches responses；Function A writes the response to System.err, Function B returns an InputStream and caches to a local file；Function A reads from a local gzipped file for input, Function B reads from a URL；Function A implements a batch query loop, Function B implements caching logic with conditional requests
- 修正建议: Incorporate higher-level functional flow analysis that recognizes common I/O patterns；Use contrastive learning on abstract task descriptions to capture partial functionality similarity

### case_id=3378 FN lexical_or_api_overlap

- 方法: `httpRequestByPOST` vs `seeURLConnection`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.95`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Performs an HTTP POST request with parameters using HttpClient, reads response line by line, returns response string or sets error fields on failure.
- B 摘要: Performs an HTTP GET request to a hardcoded URL using URLConnection, reads response line by line, logs the response and throws Exception on failure.
- 静态失败原因: Static BERT/GraphCodeBERT models rely on lexical overlap and API tokens; the low Jaccard similarity (0.179) and different APIs (HttpClient vs URLConnection), method names, parameter patterns, and control flow caused the model to miss the shared high-level functionality.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may label this as a clone because both functions achieve the high-level goal of making an HTTP request and reading the response, which aligns with Type-4 clone annotation (similar functionality despite different APIs and details).
- 共享行为: Both open a connection to a URL and read the HTTP response line by line using BufferedReader.；Both accumulate line data into a StringBuffer.；Both involve reading an HTTP response body.
- 行为差异: A uses HttpClient with HttpPost for POST with parameters; B uses URLConnection for GET with no parameters.；A returns the response string (or null on error); B is void and logs the response.；A has explicit error handling for status codes and IOExceptions; B throws Exception and has no custom error handling.；A takes parameters (url, timeout, params); B uses a hardcoded URL and no parameters.
- 修正建议: Incorporate API abstraction layers to recognize different HTTP libraries as similar.；Enhance training with more Type-4 clone pairs that share only high-level semantics.；Use graph-based representations that capture data flow and control flow across different APIs.

### case_id=3379 FN benchmark_preference_bias

- 方法: `copyParseFileToCodeFile` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Copies a file to another using a byte buffer.
- B 摘要: Builds HTML site files by reading XML, XSLT transformation, and writing output per page.
- 静态失败原因: The static model correctly identified low lexical overlap and different semantics, leading to a non-clone prediction; the error is from the BCB label.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider them clones due to both involving file I/O operations, but the functional difference is too large; likely a mislabel.
- 共享行为: Both use FileInputStream to read from a file.；Both write output to files.
- 行为差异: A is a simple file copy; B involves complex XML processing, string manipulation, and multiple output files.；A uses a fixed 1024-byte buffer; B uses a 8192-char buffer and also reads XML into a stream for transformation.；A has no error handling beyond throwing IOException; B handles multiple exception types and has logging.
- 修正建议: Re-evaluate the BCB annotation for this pair to ensure consistency.；If BCB label is incorrect, update the ground truth.

### case_id=3380 FP lexical_or_api_overlap

- 方法: `getTicketsForQueue` vs `GetResponse`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Retrieves a list of tickets from a RequestTracker queue by performing an HTTP GET query, parsing the response to extract ticket IDs, and fetching each ticket individually.
- B 摘要: Performs an HTTP GET request to a given URL and returns the response content as a concatenated string.
- 静态失败原因: The static BERT/GraphCodeBERT method likely over-emphasized the lexical and structural overlap of the HTTP request and response reading pattern (e.g., HttpURLConnection/HttpGet, BufferedReader, while loops reading lines), while ignoring the higher-level semantics and data transformation differences.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because despite sharing the HTTP GET boilerplate, the overall functionality and output types are completely different; one is a specialized ticket retrieval with multiple steps, the other is a simple content fetcher.
- 共享行为: Both perform an HTTP GET request；Both read the response line by line；Both handle HTTP status codes (checking for OK)；Both use BufferedReader and InputStreamReader
- 行为差异: Function A parses specific ticket IDs from the response and then retrieves detailed ticket objects, whereas Function B just concatenates raw lines into a string；Function A interacts with a specific REST API (RequestTracker), while Function B is generic；Function A has separate logic for iterating over ticket IDs and fetching each ticket, Function B just reads and returns the raw content；Function A includes specific error handling for 'does not exist' strings and logging, Function B only prints stack traces
- 修正建议: Train models to distinguish between generic HTTP boilerplate and specific business logic；Incorporate data flow analysis to track how the response is processed (e.g., parsed as ticket IDs vs. raw string)；Use contrastive learning with negative examples that share low-level patterns but differ in functionality

### case_id=3381 FN benchmark_preference_bias

- 方法: `getFile` vs `saveFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.6`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies a specific endpoint attribute in the XML, and returns the file path.
- B 摘要: Saves UI configuration (window positions, toolbars, etc.) as an XML file to a configuration directory.
- 静态失败原因: The model correctly identified the lack of functional similarity, but failed to align with the potentially erroneous BCB label. The low token Jaccard and different API usage (e.g., URL vs. Document building) supported a non-clone prediction.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled these as clones due to both involving file I/O and XML processing, but this is a very broad interpretation. Typical BCB annotations require more specific functional similarity, so this label is likely an anomaly or error.
- 共享行为: Both write XML content to files using file output streams.；Both handle exceptions and log errors.
- 行为差异: A downloads and modifies an external WSDL file; B builds an XML document from scratch based on UI state.；A returns a String file path; B is void.；A uses network I/O and specific XML parsing; B uses DOM building and XMLOutputter.；Error handling differs: A throws AxisFault; B logs and swallows exceptions.
- 修正建议: Review the BCB label for possible misannotation; if correct, adjust model to accommodate very broad Type-4 clones based on high-level operation (e.g., file saving with XML).；Incorporate more training data with similar broad clone pairs.

### case_id=3382 FN partial_functionality

- 方法: `run` vs `invoke`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.4`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads lines from a URL, extracts version and URL from first two lines, appends rest to a string, and notifies listeners after completion.
- B 摘要: Sends HTTP POST to invoke a remote method, reads JSON response, deserializes to expected type, and retries on connection timeout.
- 静态失败原因: The static BERT/GraphCodeBERT model likely correctly identified low semantic and structural overlap, focusing on detailed logic differences rather than the superficial pattern of network I/O. BCB's label may be a false positive due to overly broad similarity criteria.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled these as clones due to broad Type-4 similarity: both involve fetching data from a network URL, reading lines, and handling exceptions. However, the specific processing logic and purpose are very different, so it's ambiguous.
- 共享行为: Both read text line by line from a network source using BufferedReader in a while loop.；Both have try-catch blocks to handle I/O exceptions.
- 行为差异: A processes lines by index with a switch statement; B accumulates all lines then deserializes JSON.；A sets error flags and notifies listeners; B implements retry logic and returns deserialized object.；A writes to instance fields; B returns a value of generic type.；B constructs HTTP POST request with JSON body; A just opens a URL stream.
- 修正建议: Increase weight on detailed data flow and control flow differences.；Incorporate method name and purpose context to disambiguate generic I/O patterns from specific business logic.；Use a more nuanced tokenization that captures structural patterns rather than just surface-level loop and I/O presence.

### case_id=3383 FN partial_functionality

- 方法: `downloadURLtoString` vs `register`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.35`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads the content of a URL and returns it as a string.
- B 摘要: Registers a user by encoding password, setting details, creating a forum user via URL request, and persisting to database.
- 静态失败原因: A static BERT/GraphCodeBERT method likely failed because it focused on the overall token-level similarity and method name, which are very different (downloadURLtoString vs register). It did not capture the shared I/O sub-pattern due to low lexical overlap (Jaccard=0.13) and the overshadowing of the unique tokens in function B.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may annotate this as a clone because both functions involve the same core I/O pattern of reading from a URL via BufferedReader, and the BCB annotation guidelines for Type-4 (semantic) clones can be lenient when there is a significant shared sub-functionality, even if overall purpose differs.
- 共享行为: Both contain a while loop reading lines from a BufferedReader over a URL connection.；Both close the reader after reading.
- 行为差异: Function A returns the entire content as a single string; function B only reads the first line to set an integer field.；Function B performs numerous additional operations (password encoding, authority setting, hash generation, database persistence, email sending) not present in A.；Function B has error handling for IOException and NumberFormatException, while A only throws IOException without catching.；Function A is a utility method; function B is a complex business logic method.
- 修正建议: Use a graph-based representation that can capture the shared subgraph of URL reading and buffered reading.；Train with a contrastive objective that emphasizes structural commonalities over lexical overlap.；Incorporate a data-flow analysis to identify I/O patterns that are reused across methods.

### case_id=3384 FN benchmark_preference_bias

- 方法: `readAndRewrite` vs `modifyApplicationMessage`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Reads a DICOM medical image file, parses it, reads pixel data, and writes it to an output file.
- B 摘要: Modifies a key-value pair in a localized properties file, creating the file from an English template if needed.
- 静态失败原因: The model correctly detected low token overlap (Jaccard 0.05) and domain-specific APIs, so it predicted non-clone; it did not fail but matched strict semantic judgment.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider both as read-modify-write file operations, ignoring the completely different data formats and processing logic, thus labeling them as broad Type-4 clones.
- 共享行为: Both perform file I/O operations (reading from one file and writing to another).
- 行为差异: Domain: DICOM medical imaging vs. localization properties files.；Processing: binary pixel data handling vs. string/line manipulation.；Error handling: throws IOException vs. catches Exception.；Output encoding: binary vs. text with specific formatting.
- 修正建议: Revisit BCB annotation guidelines to require more semantic similarity for clones.；Consider domain-specific context to avoid over-generalization of file I/O patterns.

### case_id=3385 FN lexical_or_api_overlap

- 方法: `getFile` vs `handle`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.7`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies its XML content, and saves to a temporary file.
- B 摘要: Handles log file rotation by compressing, renaming, deleting old logs, and archiving them based on age.
- 静态失败原因: Static BERT/GraphCodeBERT models may have focused on overlapping API tokens (e.g., FileChannel, FileInputStream, FileOutputStream) and structural patterns, but missed the semantic gap in purpose and data flow. The token Jaccard similarity is low (0.163), but the presence of shared I/O idioms may have misled the model into non-clone prediction due to lack of high-level understanding.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may label this as a clone because both functions are complex file I/O utilities with similar structural patterns (try-catch blocks, file channels, temporary files). BCB's broad Type-3/Type-4 criteria accept partial functionality similarity, especially in the context of utility functions.
- 共享行为: Both use FileChannel and Stream I/O for file operations；Both involve creating, reading, and writing files；Both have error handling with exceptions
- 行为差异: Function A downloads a file from a URL; Function B rotates local log files；Function A involves XML parsing and attribute modification; Function B involves GZIP compression and archiving；Function A has a specific endpoint parameter to set in XML; Function B has configuration for rotation days and compression；The purpose and output are entirely different: one returns a file location, the other performs log maintenance
- 修正建议: Incorporate program dependence analysis to capture data flow and control flow differences；Use contrastive learning with better negative sampling focusing on functional semantics；Add explicit representation of method purpose (e.g., docstring or intent embedding)

### case_id=3386 FP lexical_or_api_overlap

- 方法: `loadSourceCode` vs `downloadModel`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Loads source code from a file resource, applies syntax highlighting, and sets the result as an HTML string.
- B 摘要: Downloads an RDF model from a URL and returns it.
- 静态失败原因: The model likely over-emphasized lexical overlap (URL, InputStream, IOException, try-catch structure) and missed key semantic differences like the specific processing functions (syntaxHighlight vs model.read) and return type (void vs Model).
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely considers these non-clones because they serve completely different purposes: one is a source code viewer utility, the other is an RDF model downloader. Despite similar I/O patterns, the data processing and return types are distinct.
- 共享行为: Open URL connection；Read from InputStream；Handle exceptions
- 行为差异: A modifies instance variable; B returns Model；A reads lines with BufferedReader and syntax highlights; B reads RDF data into model；Different exception handling: A catches SecurityException then generic Exception; B catches MalformedURLException and IOException
- 修正建议: Use data flow analysis to track output types and method calls；Incorporate code summarization to capture intent；Enhance training with more diverse I/O-based tasks to distinguish different post-processing

### case_id=3387 FN partial_functionality

- 方法: `getContent` vs `runInternal`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Executes an HTTP request and returns the entire response body as a string.
- B 摘要: Handles complex HTTP download of OPDS feeds or books with progress, error handling, redirects, and pagination.
- 静态失败原因: The low token Jaccard similarity (0.0625) and divergent API usage (HttpClient vs HttpURLConnection) obscure the common HTTP fetching pattern. B's method is far more complex and contains many distracting code elements unrelated to the simple fetch operation.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as 'fetch content via HTTP' despite the vast difference in complexity, interpreting runInternal as an extended version of getContent's core functionality.
- 共享行为: Both make an HTTP GET request to a URL.；Both set connection timeout and read timeout.；Both read from the HTTP response input stream.
- 行为差异: getContent returns the full string content; runInternal may download a file or parse OPDS catalog entries.；getContent uses Apache HttpClient; runInternal uses java.net.HttpURLConnection.；runInternal handles redirects, content disposition, content type, user agent, and referer.；runInternal includes progress reporting, error callbacks, and pagination support.
- 修正建议: Use dataflow analysis to detect that both functions eventually read from an HTTP response stream.；Train on more examples where a simple utility is embedded in a larger complex method.；Incorporate structural similarity measures that are robust to library differences.

### case_id=3388 FN boilerplate_overlap

- 方法: `writeFileType` vs `lookupFutureEvents`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads URIs from a file, fetches each web page, examines first lines for RDF namespaces, and writes classification to another file.
- B 摘要: Fetches events from the Meetup API for a given group, parses JSON response, and returns a list of Event objects.
- 静态失败原因: Static BERT/GraphCodeBERT models rely on lexical and syntactic patterns; despite low Jaccard similarity, both functions share common API usage (URL, BufferedReader, try-catch) that could have been misaligned with BCB's broad clone definition, but the model correctly predicted non-clone under strict semantics unlike BCB's annotation.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may have labeled this as a clone due to shared low-level I/O patterns (URL, BufferedReader, while-loop reading) and exception handling, considering them as structural or boilerplate clones, but the functional purposes are entirely different.
- 共享行为: Both open a URL connection and read data line by line using BufferedReader；Both handle exceptions (print stack trace or throw custom exception)
- 行为差异: Function A writes output to a file; Function B returns a list of objects；Function A processes multiple URIs from a file; Function B processes a single API call；Function A checks for RDF namespaces in content; Function B parses JSON and builds Event objects
- 修正建议: Incorporate higher-level semantic understanding (e.g., API call sequences and data dependencies)；Use dataflow analysis to capture distinct functional behaviors

### case_id=3389 FN benchmark_preference_bias

- 方法: `readData` vs `doVersionCheck`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Parses comma-separated tokens from static strings to populate various character sets and builds a hash map for valid input sequences.
- B 摘要: Performs a version check by fetching a URL, reading lines to extract version and build information, and displaying update status.
- 静态失败原因: The static BERT/GraphCodeBERT likely correctly predicted non-clones due to low token overlap (0.104), different method names, and unrelated contexts. The model may have been penalized for disagreeing with a potentially incorrect BCB label.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might have labeled these as clones due to superficial structural similarities (loops reading lines, try-catch, token/line processing) or a broad interpretation of 'read data' functionality. However, this appears to be a mislabel.
- 共享行为: Both involve reading input line by line from some source (strings in a, URL stream in b).；Both use tokenization/line processing (StringTokenizer vs BufferedReader).；Both handle I/O exceptions.
- 行为差异: code_a parses static internal data; code_b fetches remote URL.；code_a populates sets and maps for later use; code_b compares version strings and shows message.；code_a involves complex error handling on file parsing; code_b simple URL read.
- 修正建议: Reevaluate BCB annotation for this pair; consider whether they truly share functionality.；Improve dataset consistency by removing such outliers or refining clone definitions.

### case_id=3390 FN benchmark_preference_bias

- 方法: `modifyApplicationMessage` vs `EncodeReturn`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Modify a properties file for a given locale by replacing or adding a message key-value pair.
- B 摘要: Encrypt a download file using a crypto client and append it to a piggyback route file, then return the combined route file.
- 静态失败原因: Static BERT/GraphCodeBERT correctly predicted non-clone because the token overlap is very low (Jaccard 0.05) and the semantics are entirely different. The model failed in the sense that it disagreed with the BCB label, which is likely a misannotation.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB likely labeled this as a clone due to a very broad interpretation of Type-4 similarity, where both functions involve file processing with error handling. However, this seems inconsistent with typical BCB annotations, suggesting possible annotation noise or an overly permissive threshold.
- 共享行为: Both perform file I/O operations (read/write files).；Both handle exceptions (try-catch in A, throws in B).；Both use streams or channels for file operations.
- 行为差异: Function A manipulates a properties file for internationalization; Function B performs encryption and file concatenation.；Function A modifies a specific property in place; Function B creates new temporary files and deletes intermediate files.；Function A uses BufferedReader and StringBuilder for line processing; Function B uses FileChannel and CryptoClient for encoding.；The domain and purpose are completely different (UI configuration vs. secure file transport).
- 修正建议: Review BCB annotations for this pair to ensure consistency with clone definitions.；Use more fine-grained semantic similarity measures to avoid considering generic file I/O as a clone signal.；Consider filtering out pairs with very low token overlap if they are not structurally similar.

### case_id=3391 FP lexical_or_api_overlap

- 方法: `PageLoader` vs `getVersion`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.85`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Constructor that reads the entire content of a webpage from a given URL into an instance variable.
- B 摘要: Static method that fetches a version string from a fixed URL and returns it.
- 静态失败原因: The static BERT model likely relied on token-level overlap (e.g., URL, BufferedReader, readLine, close) and similar control flow, overlooking the difference in method purpose, output handling, and error handling. The high lexical similarity misled the model into predicting a clone.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels these as non-clones because they have different functionalities (loading a page vs. fetching a version), different method signatures (constructor vs. static getter), and different output behaviors (side effect vs. return value). Although they share the same I/O pattern, the purpose and overall behavior are distinct.
- 共享行为: Both open a URL；Both create a BufferedReader from an InputStream；Both read lines using readLine()；Both close the BufferedReader
- 行为差异: A reads all lines and concatenates them; B reads only the first line as version；A is a constructor with side effect (assigns to instance variable); B is a static method returning a value；A uses url.openStream() directly; B uses URLConnection and getInputStream()；A has no exception handling; B catches Exception and returns null on failure
- 修正建议: Incorporate data flow analysis to track how the read data is used (concatenated vs. assigned to version).；Add semantic features like method signature (constructor vs. static, return type) to the model.；Use graph representations like AST or CFG to capture structural differences (e.g., loop vs. single read).

### case_id=3392 FN benchmark_preference_bias

- 方法: `addFileToTarGz` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Adds a file or directory to a TAR archive by creating entries and copying data using TarArchiveOutputStream.
- B 摘要: Retrieves a resource as an InputStream from a URL, with caching mechanism and HTTP conditional GET support.
- 静态失败原因: The static model likely correctly identified non-clone because the token overlap is low (Jaccard 0.068) and the code structure, API usage, and control flow are very different. The model's prediction aligns with our analysis; it's BCB annotation that seems incorrect.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as a clone due to superficial similarity in using streams and file I/O, possibly considering them as Type-4 (semantic) clones where both perform resource acquisition and caching. However, the overall functionality is vastly different.
- 共享行为: Both perform I/O operations using streams (FileInputStream, BufferedInputStream, etc.)；Both involve file handling (creating File objects, reading/writing files)
- 行为差异: A writes to a tar archive; B reads from a URL and caches to a local file.；A is recursive for directories; B is not recursive.；B involves URL handling, HTTP connections, caching logic; A does not.；B uses synchronization; A does not.
- 修正建议: Consider re-evaluating BCB labels for this pair; manual inspection suggests they are not functionally similar.；Improve BCB annotation guidelines to avoid overly broad Type-4 classification based on common I/O operations.

### case_id=3393 FN partial_functionality

- 方法: `testNetworkHTTP` vs `doVersionCheck`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Tests HTTP connectivity by sending various device data to multiple hardcoded URLs and discarding the responses.
- B 摘要: Checks for a newer version of jEdit by fetching a version file from a configurable URL and comparing version strings.
- 静态失败原因: Static BERT/GraphCodeBERT had low token overlap (0.195) due to different method names, packages, and constant strings. It likely failed to recognize the high-level structural pattern of HTTP I/O because the API usage differs (HttpURLConnection vs URL.openStream) and the surrounding business logic is different (test vs version check).
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considers these Type-3 clones because both follow the same core pattern: open HTTP URL, read lines with BufferedReader, and catch IOException. The structural similarity in I/O operations outweighs differences in purpose and response processing.
- 共享行为: Both open an HTTP connection to a URL and read content line by line using BufferedReader；Both handle IOException with error handling
- 行为差异: A sends data via query parameters and discards responses; B parses specific lines for version comparison；A uses HttpURLConnection explicitly; B uses URL.openStream()；A performs multiple sequential requests; B does one；A is a test method with no UI; B manipulates UI and shows messages
- 修正建议: Enhance model to recognize shared I/O patterns regardless of specific API constants；Use graph representations that capture control flow and data flow sequences like open-read-catch；Incorporate contrastive learning to pair functions with similar sub-behaviors even if from different domains

### case_id=3394 FN benchmark_preference_bias

- 方法: `copyFile` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Copies a file from source to destination using FileChannel.
- B 摘要: Builds a website for editing by reading XML, applying XSLT transformation, and writing output files with string replacements.
- 静态失败原因: The model correctly predicted 'not clone' due to low token overlap (0.067) and lack of structural similarity. It failed to match the BCB label because the label itself is likely an error or an outlier in the benchmark.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB likely labeled this as a clone due to a very broad interpretation of 'file manipulation' or because both functions use FileInputStream/FileOutputStream. However, the functionalities are too dissimilar for typical BCB Type-3/Type-4 clones.
- 共享行为: Both perform file I/O operations (reading and writing files).
- 行为差异: Function A is a simple, generic utility for copying a file; function B is a large, domain-specific method for generating HTML pages.；Function A uses FileChannel for efficient transfer; function B uses FileReader/FileWriter and custom file system operations.；Function B involves XML parsing, XSLT transformation, string manipulation, and multiple file writes; function A performs a single file copy.；Function B has extensive error handling and debugging output; function A has minimal exception handling.
- 修正建议: Re-evaluate the BCB label for this pair; consider removing it if it does not reflect reasonable clone criteria.；Improve benchmark consistency by ensuring labels align with commonly accepted clone types (Type-1 to Type-4).

### case_id=3395 FP lexical_or_api_overlap

- 方法: `sendPost` vs `PhoneSetImpl`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Sends an HTTP POST request to a URL with parameters and returns the response body as a string.
- B 摘要: Constructs a PhoneSetImpl by reading lines from a URL, skipping comment lines, and populating a phone set map.
- 静态失败原因: Static BERT/GraphCodeBERT likely overfitted on shared tokens like 'URL', 'BufferedReader', 'readLine', and similar control flow structures, missing the critical difference in data flow (write vs. read-only) and overall purpose.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would not consider these clones because their core functionality is entirely different: one is an HTTP client utility, the other is a constructor for a phone set that reads and parses data. They share only superficial API usage (BufferedReader, URL).
- 共享行为: Both involve opening a URL and reading lines from it using BufferedReader.
- 行为差异: A sends POST data to the URL before reading; B only reads without sending any data.；A returns the concatenated response string; B does not return a value (constructor).；A handles exceptions by printing a message; B throws IOException.；A uses HttpURLConnection with output enabled; B uses URL.openStream() directly.
- 修正建议: Incorporate data flow analysis to distinguish write vs. read operations.；Include method signature and return type information.；Train on more diverse pairs to reduce sensitivity to common API sequences.

### case_id=3396 FN partial_functionality

- 方法: `modifyApplicationMessage` vs `copy`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Modifies a properties file for a given locale by updating or adding a message key-value pair, with a fallback to copy an English template file if the locale file does not exist.
- B 摘要: Copies a source file to a destination using NIO FileChannel, creating parent directories as needed.
- 静态失败原因: Static BERT/GraphCodeBERT likely missed the clone due to low token overlap (Jaccard 0.144) and because the shared file-copy behavior is only a small part of modifyApplicationMessage, causing the model to focus on overall semantic differences and classify as non-clone.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: None
- 共享行为: Both perform file I/O operations involving reading and writing files.；Both include error handling for file existence or null arguments.
- 行为差异: Primary purpose: modifyApplicationMessage is for properties file manipulation; copy is for generic file copying.；modifyApplicationMessage has logic to parse and modify properties content; copy does not.；File copy in modifyApplicationMessage is a fallback (character-by-character) and not the main operation; copy is solely dedicated to efficient file copying using NIO.；modifyApplicationMessage is instance method tied to configuration; copy is static utility.
- 修正建议: Increase sensitivity to partial functionality via subgraph matching or hierarchical encoding.；Use program slicing to extract relevant subroutines.；Incorporate dataflow or control-flow analysis to identify shared low-level operations like file copy.

### case_id=3397 FP lexical_or_api_overlap

- 方法: `createNew` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Creates a new resource file under a given realFile, handling .request and .tokens files specially.
- B 摘要: Handles GUI action events for configuring various settings like GRAPHVIZ path, IMAGEMAGICK path, etc.
- 静态失败原因: The static model likely relied on superficial similarities such as use of File objects, conditional checks (if statements), and possibly the presence of 'if (cmd == null) return;' pattern resembling early returns. It missed the fundamental difference in purpose and context.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels this as non-clone because the functions perform entirely different tasks (file creation vs GUI event handling) and only have trivial overlap in using File objects, which is insufficient for clone detection.
- 共享行为: No meaningful shared behavior.
- 行为差异: Function A creates files and returns Resource objects; Function B handles GUI events and updates preferences.；Function A checks for allowed client and specific file names; Function B checks action commands and opens file choosers.；Function A uses InputStream and length; Function B uses ActionEvent and GUI components.
- 修正建议: Improve attention mechanisms to capture high-level semantics.；Incorporate data flow and control flow features.；Utilize method names and surrounding context for better disambiguation.；Train on more diverse examples to reduce reliance on lexical overlap.

### case_id=3398 FP lexical_or_api_overlap

- 方法: `readPage` vs `handleHandshake`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a URL and returns its content as a string, optionally skipping lines starting with '#'.
- B 摘要: Handles Minecraft handshake by validating a username and performing an HTTP request to verify the server.
- 静态失败原因: The model likely relied on surface-level token overlaps such as 'BufferedReader', 'InputStreamReader', 'url.openStream()', and exception handling patterns, while ignoring the overall logic and context differences.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically requires significant semantic overlap or shared functionality to label as clones; these functions share only trivial API usage and have entirely different purposes.
- 共享行为: Both use BufferedReader and InputStreamReader to read from a URL stream.
- 行为差异: Function A reads all lines and returns them; function B reads only one line and uses it for a conditional check.；Function A is a simple utility; function B involves validation, multiple branches, and network error handling.；Function A ignores comment lines; function B does not ignore any lines.
- 修正建议: Incorporate structural features like control flow graphs or data flow analysis.；Use function length and complexity metrics to distinguish utilities from complex handlers.；Train on more diverse negative examples with API overlap but semantic difference.

### case_id=3399 FP lexical_or_api_overlap

- 方法: `handler` vs `loadURL`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads lines from a URL and extracts substrings to update a map entry.
- B 摘要: Reads lines from a URL with optional authentication, writes them to a temporary file, and updates a status label with file size.
- 静态失败原因: Static BERT/GraphCodeBERT likely overemphasized the lexical overlap of common APIs (URL, BufferedReader, InputStreamReader) and the loop structure, failing to distinguish the different data usage and output behaviors.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labeled as non-clone because the functions serve completely different purposes despite sharing a common URL reading pattern. The core functionality (map update vs. file write + UI update) is distinct, and the token similarity is low.
- 共享行为: Both open a URL connection and read lines using BufferedReader.；Both handle IOException with try-catch or throws.；Both iterate over lines until null.
- 行为差异: Function A extracts substrings based on pattern matching and modifies a map; B writes entire lines to a file and updates a UI label.；Function A does not handle authentication; B does basic authentication.；Function A does not create files; B creates a temporary file and writes to it.；Function A uses parameters Map and TargetPage; B uses URL, username, password, and JLabel.
- 修正建议: Incorporate data-flow analysis to track how read data is used.；Add training examples with similar structural patterns but different semantics.；Use type information or context to distinguish between output destinations (e.g., map vs. file).

### case_id=3400 FN benchmark_preference_bias

- 方法: `copy` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.35`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Recursively copies a file or directory using FileChannel with memory-mapped I/O.
- B 摘要: Builds a website for editing by reading XML templates, transforming them with gadgets, and writing output files to disk.
- 静态失败原因: Static BERT/GraphCodeBERT models rely heavily on lexical tokens and structural patterns; the low token Jaccard (0.089) and completely different method names indicate very different code, so it correctly predicted non-clone. The BCB label likely stems from a more lenient interpretation of clone (e.g., Type-4 partial functionality), which static models are not designed to capture.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled these as clones based on broad semantic similarity (both involve file reading and writing), but the actual functionalities differ significantly: one is pure file copying, the other is a complex transformation and generation process.
- 共享行为: Both perform file I/O operations (read from input, write to output).；Both handle IOException and use try-finally or similar for resource management.
- 行为差异: Function A copies files verbatim (binary or directory structure); Function B transforms XML to HTML and writes multiple files.；Function A uses memory-mapped I/O (MappedByteBuffer); Function B uses character-based buffered I/O and string manipulation.；Function A is recursive and handles directories; Function B loops over a list of pages.；Function A is a generic utility method; Function B is specific to site building with many parameters and configuration.
- 修正建议: Incorporate dataflow or high-level I/O operation detection to identify similar input-output patterns.；Use semantic role labeling to understand the 'source-destination' relationship.；Consider that BCB annotations may include broad Type-4 clones; train on such annotations with contrastive learning for semantic similarity.

### case_id=3401 FN long_range_semantics

- 方法: `copyResource` vs `copy`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource (URL or local file) to a destination file using byte-by-byte I/O.
- B 摘要: Copies a local source file to a destination file using NIO FileChannel transfer.
- 静态失败原因: The model likely relied on low token overlap (0.167) and syntactic differences such as method name, parameter list, and I/O classes, failing to capture the semantic similarity of the overall task.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB often classifies Type-3/Type-4 clones as positive, and here the core functionality of file copying is preserved despite differences in I/O mechanism and source input handling.
- 共享行为: Both copy data from a source to a destination file
- 行为差异: Function A accepts URL or local file as source; function B only accepts local file as source；Function A uses byte-by-byte streaming; function B uses NIO FileChannel；Function A uses implicit member variables; function B uses explicit parameters；Function A throws generic Exception; function B throws IOException
- 修正建议: Use models that incorporate data-flow or control-flow to capture semantic equivalence；Train on examples of diverse I/O patterns performing the same task；Incorporate function-level summaries or high-level intent understanding

### case_id=3402 FN partial_functionality

- 方法: `main` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a hardcoded URL, extracts all zip entries, and writes each entry to a file.
- B 摘要: Copies a given source file to a destination directory using a buffer.
- 静态失败原因: Low token Jaccard (0.247), different method names and signatures, and differing overall tasks cause static BERT models to overlook the shared I/O loop pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this as a clone (Type-4) because both functions perform a generic 'copy data from source to file' operation using similar read-write buffer pattern, despite different source types and specific tasks.
- 共享行为: Both read bytes from an input stream and write to an output stream using a buffer in a loop.
- 行为差异: Function A fetches data from a URL and unzips multiple entries; Function B copies a single file from filesystem.；Function A uses ZipInputStream and writes entry names; Function B copies file to destDir with same filename.；Function A has no error handling; Function B catches IOException and prints an error message.；Function A is a main method with hardcoded source; Function B is a reusable utility with parameters.
- 修正建议: Incorporate dataflow analysis to capture read-write loop patterns independent of specific APIs.；Abstract over I/O operations to recognize common buffered copy logic.；Use code representation that separates boilerplate from core task logic.

### case_id=3403 FN partial_functionality

- 方法: `readGeoParserResult` vs `getXML`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Constructs an XML request, sends it to a geo parser service, parses the response into a collection of place names with gazetteer IDs, with retries.
- B 摘要: Fetches XML content from a given URL via HTTP GET and returns the raw response string.
- 静态失败原因: Static BERT/GraphCodeBERT models may emphasize lexical and syntactic differences, such as different method names, return types, and additional code blocks, leading to a low similarity score. The models fail to recognize the high-level shared intent of fetching XML data from a web service.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considers both as 'XML fetching' functions, focusing on the common pattern of opening a URL, reading the response, and returning content, while ignoring differences in request construction and response parsing as inessential details.
- 共享行为: Both perform HTTP GET requests to a URL；Both read the response line by line using BufferedReader；Both use URL and InputStreamReader
- 行为差异: A constructs the request XML dynamically, B takes request as parameter；A includes retry logic and error handling, B returns null on first error；A parses the response XML into a structured collection, B returns raw string；A uses ISO8859-1 encoding for URL encoding, B uses UTF-8
- 修正建议: Increase training data with Type-3/4 clones that share a core pattern but differ in periphery；Incorporate code summarization or intent-aware embeddings；Use contrastive learning to emphasize structural similarity over lexical overlap；Add data augmentation by extracting common subpatterns (e.g., HTTP GET) as clone indicators

### case_id=3404 FN partial_functionality

- 方法: `login` vs `runInternal`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends HTTP POST with email and password to login endpoint and returns session ID
- B 摘要: Downloads and parses OPDS catalog entries via HTTP GET with pagination, error handling, and callback
- 静态失败原因: Static models rely on token overlap and structural similarity; the functions share very few tokens (Jaccard 0.09) and have different lengths and control flow, leading to low similarity score
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled these as clones due to both being network I/O functions that use URLConnection and read HTTP responses, but the functional purpose and complexity differ vastly
- 共享行为: Both use URLConnection to perform HTTP requests；Both read from InputStream and handle exceptions
- 行为差异: A is a simple POST login; B is a complex GET with pagination and content processing；A returns a session string; B calls a callback with parsed catalog entries；B has extensive error handling, timeouts, user-agent, redirects; A has minimal error handling
- 修正建议: Add functional annotations or API usage patterns to capture broader I/O intent；Use data-flow analysis to distinguish different HTTP methods (POST vs GET)；Incorporate semantic embeddings from method-level contexts

### case_id=3405 FN partial_functionality

- 方法: `httpRequestByPOST` vs `File2String`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Performs an HTTP POST request and reads the response line by line into a string, returning null on error with error code set.
- B 摘要: Reads a file from filesystem or classpath line by line into a string, exiting the program on error.
- 静态失败原因: The static BERT model likely failed because it relied on token-level overlap and API similarity, which are low (Jaccard 0.215). The model did not abstract the common reading pattern due to different surface forms (HttpClient vs FileInputStream) and different control flow.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled these as clones due to the shared pattern of reading lines into a string, which is a common utility functionality. However, the overall tasks (network vs. file) and error handling are too different for a reasonable clone annotation.
- 共享行为: Both read line by line from an input stream and append lines to a StringBuffer
- 行为差异: Function A makes an HTTP request; Function B reads a local file；Function A returns null on error; Function B calls System.exit()；Function A sets error codes; Function B prints stack traces；Function A uses HttpClient API; Function B uses FileInputStream and URL.openStream()
- 修正建议: Enhance model with dataflow or control-flow representations to capture abstract patterns；Use contrastive learning to improve robustness to API variation；Incorporate structural correspondence analysis

### case_id=3406 FP partial_functionality

- 方法: `run` vs `loadMFileViaWeb`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads tile data from a URL, processes geometry, and loads it into a data source.
- B 摘要: Loads an M-file from a web URL, reads its code, and parses it into a UserFunction object.
- 静态失败原因: Static BERT likely overemphasized the lexical similarity of URL opening and line-reading patterns, ignoring the divergent subsequent processing and domain-specific operations (tile vs M-file).
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: Despite structural overlap in URL reading, the overall functionality, data types, and purpose are entirely different; BCB favored distinct functionality over partial overlap.
- 共享行为: Both open a URL, read input stream line by line, and concatenate into a string.
- 行为差异: A handles multiple protocols, synchronizes HTTP requests, creates VectorTile and geometry objects; B appends newlines, parses code with FunctionParser, returns UserFunction.
- 修正建议: Incorporate structural features like control flow and data flow beyond token overlap.；Use type and dependency information to differentiate high-level operation semantics.；Include method name and context clues to disambiguate functional goals.

### case_id=3407 FN partial_functionality

- 方法: `File2String` vs `postXml`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a file from local filesystem or classpath resource and returns its contents as a string, with error handling that prints messages and exits.
- B 摘要: Sends an HTTP POST request with XML content and returns the response body as a string, with error handling that throws a RuntimeException.
- 静态失败原因: Static BERT/GraphCodeBERT likely focused on the low token overlap (Jaccard 0.204) and different API calls (FileInputStream vs HttpURLConnection), leading to a non-clone classification without recognizing the abstract pattern of reading lines and concatenating.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled this as a clone due to the high-level similarity of reading text input and returning it as a string, considering it a Type-4 clone with partial functionality overlap, despite differences in I/O sources and error handling.
- 共享行为: Both open an input stream to read data；Both read lines using BufferedReader；Both concatenate lines into a string buffer (StringBuffer/StringBuilder)；Both return the concatenated string
- 行为差异: A reads from a file or classpath resource; B sends an HTTP POST request to a URL；A prints messages to System.out and calls System.exit on error; B throws a RuntimeException；A has nested try-catch blocks; B has a single try-catch；A uses StringBuffer; B uses StringBuilder
- 修正建议: Incorporate program analysis to detect abstract I/O patterns；Use data flow graphs to identify common subsequences like read lines and concatenate；Train on more diverse Type-4 examples with low lexical but high structural similarity

### case_id=3408 FN other

- 方法: `copyParseFileToCodeFile` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `1.0`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Copies a file from filenameParse to filenameMisc using a byte buffer.
- B 摘要: Validates a NexOpen project, processes pom.xml files, sets Hibernate dialect properties, and executes an install action for the project.
- 静态失败原因: The static model did not fail; it correctly predicted non-clone. The BCB label is likely erroneous.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may have incorrectly labeled this pair as a clone due to a potential annotation error, as they are semantically unrelated with very low lexical overlap.
- 共享行为: Both perform file I/O operations.
- 行为差异: Function A is a simple byte-level file copy; Function B involves project configuration, XML parsing, property setting, and resource management.；Function A has no exception handling; Function B has extensive exception handling and progress monitoring.；Function A reads and writes files directly; Function B interacts with Eclipse platform resources and launch configurations.
- 修正建议: Verify BCB annotations for correctness; consider filtering out low-similarity pairs.；If the model still must align with BCB, incorporate more nuanced structural and semantic analysis to detect accidental similarities.

### case_id=3409 FP partial_functionality

- 方法: `SHA1` vs `perform`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Computes SHA-1 hash of a given string and returns it as hex.
- B 摘要: Processes a form submission in a Struts action, builds XML, sends HTTP request to a classification service, parses response, and forwards to appropriate page.
- 静态失败原因: The model likely captured superficial syntactic overlap (e.g., method signatures, try-catch, string operations) but failed to understand the high-level semantic difference due to the large length and complexity of function B, leading to a false positive.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB labels non-clones when functions have completely different purposes; these two share no meaningful functional similarity despite both being Java methods.
- 共享行为: Both are Java methods that perform some computation and return a value.；Both use try-catch for exception handling.
- 行为差异: A is a simple cryptographic hash function; B is a complex web request handler with multiple nested operations.；A operates on a single string input; B operates on multiple request parameters, session, and external HTTP calls.；A returns a String; B returns an ActionForward for navigation.
- 修正建议: Improve model's ability to capture long-range dependencies and overall method intent.；Incorporate data flow analysis to distinguish between different external API interactions.；Use contrastive learning with clear non-clone pairs having high syntactic overlap.

### case_id=3410 FN partial_functionality

- 方法: `copyFileTo` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Copies a file from its absolute path to a destination file using FileChannel.
- B 摘要: Retrieves a resource as an InputStream, with caching to a local file if needed.
- 静态失败原因: Low lexical and API overlap; static models miss high-level semantic intent of both involving data copying.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as 'file I/O' operations that copy data from a source to a file destination, especially since getResourceAsStream caches to a file.
- 共享行为: Both involve file I/O operations (opening streams, reading/writing data, closing streams).
- 行为差异: copyFileTo is a simple file copy; getResourceAsStream handles URL connections, caching logic, and returns an InputStream.
- 修正建议: Include data flow analysis to capture read/write operations；Use contrastive learning on functional similarity beyond token overlap

### case_id=3411 FN benchmark_preference_bias

- 方法: `main` vs `compress`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a URL and extracts its Zip entries to individual files.
- B 摘要: Concatenates multiple input files into one output file, optionally compressing it with an external tool.
- 静态失败原因: The static BERT model likely over-relied on token overlap (low Jaccard) and did not capture the broad conceptual similarity that BCB annotators might have perceived. It correctly identified the differences in high-level purpose and structure but missed the potential BCB label due to overly strict semantic matching.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have considered both as file I/O operations with stream reading/writing and buffer usage, perhaps viewing them as Type-4 clones (similar high-level behavior of processing files). The presence of compression in B and decompression in A might have been seen as related tasks.
- 共享行为: Both use file input/output streams to read and write data.；Both use byte buffers to process data in chunks.；Both handle exceptions with throws Exception.
- 行为差异: A reads a ZipInputStream and extracts multiple files; B reads multiple input files and writes them sequentially to one output.；A downloads from a URL; B reads local files.；B optionally invokes an external compression tool and logs progress; A does not.；A writes multiple output files; B writes a single output file (and potentially compresses it).
- 修正建议: Incorporate task-level semantics to distinguish decompression from file concatenation.；Fine-tune with more examples of Type-4 clones to recognize broad functional similarities.；Use contrastive learning to better capture the distinction between partial functionality and full equivalence.

### case_id=3412 FN partial_functionality

- 方法: `getResourceAsStream` vs `copy`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Retrieves a resource via URL, caches it locally, and returns an InputStream to the cached file.
- B 摘要: Copies a file from source to destination using NIO FileChannel and MappedByteBuffer.
- 静态失败原因: Static BERT models rely on lexical and syntactic similarity, which is very low (Jaccard 0.144). They fail to capture high-level semantic similarity across different APIs (URL vs file) and are misled by the long, complex code in function A.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considered both as 'copying' operations, possibly Type-4 semantic clone because both copy data from a source to a destination, albeit different sources (URL vs file).
- 共享行为: Both read from an input source and write to a file；Both close streams/channels in finally block；Both handle IO operations
- 行为差异: A handles URLs, HTTP, caching logic; B is a plain file copy；A returns an InputStream; B returns void；A uses BufferedInputStream/OutputStream; B uses FileChannel and MappedByteBuffer；A has extensive error handling and print statements; B has minimal error handling
- 修正建议: Use data augmentation with semantic labels for high-level functional similarity；Incorporate graph-based representations that capture data flow and high-level intent；Train on examples with low lexical but high semantic similarity

### case_id=3413 FP lexical_or_api_overlap

- 方法: `read` vs `getFullScreenUrl`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a skeleton properties file from classpath, splits it into sections by '---', and validates the section count.
- B 摘要: Fetches a YouTube video page, parses out video_id, t, and title, and constructs a full download URL.
- 静态失败原因: The static model likely over-relied on lexical and API overlap (e.g., URL, BufferedReader, while readLine loop) and structural patterns, ignoring the distinct domain logic and purposes.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would likely not label these as clones because they solve completely different problems, despite sharing some I/O boilerplate. The annotation guidelines emphasize functional similarity.
- 共享行为: Both use BufferedReader to read line by line from an InputStream obtained via URL connection.
- 行为差异: Different purpose: A loads skeleton file; B fetches YouTube video info.；A throws exception if sections mismatch; B returns empty string on error.；A appends lines to StringBuilder sections; B looks for specific substring and then parses via string splitting.；A uses ClassLoader.getResource; B uses direct URL connection.
- 修正建议: Incorporate data flow analysis to trace variable dependencies and output types.；Use graph-based models capturing entity relationships and call contexts.；Include type information and return types to distinguish side-effect functions.

### case_id=3414 FN benchmark_preference_bias

- 方法: `readData` vs `getXML`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Parses configuration strings and file data to populate character sets and mappings for Tibetan transliteration.
- B 摘要: Fetches XML content from a URL by making an HTTP GET request and returns the response as a string.
- 静态失败原因: The static model (e.g., GraphCodeBERT) correctly predicted non-clone based on low token overlap and structural differences, but BCB's label is likely a false positive due to overly broad annotation guidelines.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might have considered both as 'data loading' methods, but this is too broad; the actual functionality and implementation are entirely different.
- 共享行为: Both involve reading input data (A from static strings and a file, B from a URL).
- 行为差异: Different input sources (local config vs remote URL)；Different output (populates internal data structures vs returns XML string)；Different error handling (A prints stack traces and uses checked exceptions, B returns null on exceptions)；A has complex multi-step parsing and initialization; B is a simple HTTP client request
- 修正建议: Re-evaluate BCB annotation to ensure consistency and avoid overly broad categories.；Train models with more diverse examples to recognize functional similarity at a higher level, but this pair is likely a true non-clone.

### case_id=3415 FP partial_functionality

- 方法: `getWebPage` vs `executePost`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a URL's content by opening a stream and reading lines, returning the concatenated content or throwing an Error on IOException.
- B 摘要: Performs an HTTP POST request with parameters, reads the response lines with carriage returns appended, returns the response string or null on exception.
- 静态失败原因: The static BERT model likely overfitted on the common API call sequence (openStream, BufferedReader, readLine) and ignored the different HTTP method (GET vs POST) and error handling semantics. The low token Jaccard should have indicated dissimilarity, but the model might have been fooled by the shared pattern of reading lines.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB typically requires functional equivalence or near-identical behavior for Type-1 to Type-3 clones. These methods differ in HTTP method, error handling, I/O patterns, and response formatting, so BCB correctly labels them as non-clones.
- 共享行为: Both open a URL and read the response line by line using BufferedReader.；Both concatenate lines into a string/buffer.；Both use try-catch for exception handling.
- 行为差异: Method A does a simple GET; Method B does a POST with headers and output data.；Method A throws an Error on failure; Method B prints stack trace and returns null, with a finally block to disconnect.；Method A returns content without carriage returns; Method B appends '\r' after each line.；Method A takes a URL object; Method B takes two strings for URL and parameters.
- 修正建议: Add more robust training data with explicit differentiation of GET vs POST and error handling patterns.；Incorporate structural features like method signatures, exception handling types, and HTTP method constants.；Use dataflow analysis to capture the input-output behavior differences.

### case_id=3416 FP lexical_or_api_overlap

- 方法: `retrieveQ` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Retrieves the entire content of a given URL as a string.
- B 摘要: Searches Google Images for album art and extracts image URLs into a list.
- 静态失败原因: The model likely overemphasized lexical and API overlap (e.g., URL, BufferedReader, readLine) while ignoring the distinct high-level behavior and method context.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this pair as non-clone because the methods serve fundamentally different purposes (generic data retrieval vs. specific image search), despite sharing low-level I/O patterns.
- 共享行为: Both open HTTP connections and read response content using BufferedReader and InputStream.
- 行为差异: retrieveQ returns the entire content as a string; googleImageSearch extracts image URLs and adds to a list.；retrieveQ uses generic URLConnection; googleImageSearch uses HttpURLConnection with custom User-Agent.；retrieveQ prints response message to stderr; googleImageSearch catches exceptions and shows error dialog.；googleImageSearch has conditional logic based on instance state; retrieveQ is static and parameterized.
- 修正建议: Incorporate higher-level semantic understanding of method purposes.；Use control-flow and data-flow analysis to distinguish return vs. side-effect processing.；Consider method signature and instance variable usage.

### case_id=3417 FN benchmark_preference_bias

- 方法: `loadSourceCode` vs `httpRequestByPOST`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.85`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Reads a source code file from the classpath, applies syntax highlighting, and returns an HTML string.
- B 摘要: Sends an HTTP POST request and returns the response body as a string, handling HTTP status codes and errors.
- 静态失败原因: The static model correctly recognized the semantic difference in purpose (file reading vs HTTP request) and the different APIs, leading to a non-clone prediction. It may not have considered the generic stream-reading pattern sufficient for a clone under a strict definition.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may label these as clones due to the broad structural similarity of reading lines from a stream, which could be considered Type-3 or Type-4 under very loose criteria, though the functionality differs significantly.
- 共享行为: Both open an input stream and create a BufferedReader；Both read lines in a loop and accumulate them into a string
- 行为差异: Source of data: file resource vs HTTP response；Error handling: silent catch vs setting error codes and returning null；Additional processing: syntax highlighting and HTML wrapping vs no extra processing；Return type: void (modifies field) vs String
- 修正建议: Improve the model's ability to recognize high-level similarity when control flow patterns match, even if APIs differ.

### case_id=3418 FN partial_functionality

- 方法: `downloadURLtoString` vs `runInternal`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Downloads content from a URL and returns it as a string.
- B 摘要: Handles an HTTP connection to download a book or catalog from a URL, including error handling, progress updates, and pagination.
- 静态失败原因: The static BERT model likely focused on low lexical overlap (high Jaccard) and structural differences (one function is short, the other is very long with many API calls), causing it to classify as non-clone. It may not capture the high-level semantic similarity of 'downloading from URL'.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as implementations of 'downloading content from a URL' despite vastly different complexity, adhering to a broad Type-3/Type-4 similarity based on shared overall goal.
- 共享行为: Open a URL connection；Read data from the connection；Handle IOExceptions
- 行为差异: B handles HTTP-specific details (redirection, timeouts, headers, response codes) while A does not；B writes received data to a file and manages UI progress, while A only returns a string；B supports pagination and OPDS catalog processing, A does not；B is significantly longer and more complex than A
- 修正建议: Incorporate task-specific heuristics or call graph analysis to recognize common high-level behavior；Use hierarchical or multi-granularity embeddings that capture functional roles；Train with more diverse examples of Type-3/Type-4 clones with low lexical overlap

### case_id=3419 FN benchmark_preference_bias

- 方法: `uncaughtException` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Handles uncaught exceptions in a GUI application by showing an error dialog and optionally opening an issue tracker URL.
- B 摘要: Retrieves a resource as an InputStream, with caching to local files, using URL connections and HTTP response handling.
- 静态失败原因: The functions have very low lexical overlap (token Jaccard 0.046) and different API usage. Static models like BERT may rely on representation similarity; here they are dissimilar so the model correctly predicted non-clone. However, the BCB label says clone, so the model 'failed' by not matching BCB's annotation; but actual semantics are different.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have considered both involve error handling and I/O, but that is too superficial. Possibly they are from the same project and both handle exceptions, but functionality is completely different. The low token Jaccard suggests BCB labeling is likely a false positive.
- 共享行为: Both involve exception handling (catch blocks)；Both involve I/O operations (A: Program.launch, IOUtils; B: file and network I/O)
- 行为差异: A is a GUI error handler that interacts with user via MessageBox; B is a resource loading method with caching and HTTP handling；A uses SWT and Program.launch; B uses file streams, HTTP connections, and caching；A does not return a value; B returns an InputStream
- 修正建议: Ensure that benchmark annotations are accurate; re-annotate this pair as non-clone if necessary. If the model is to match BCB, it would need to learn broader similarity criteria, but that would increase false positives.

### case_id=3420 FN partial_functionality

- 方法: `MotixFileItem` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: This constructor reads an input stream, copies it to a byte array, optionally reads an image from it, and sets instance fields.
- B 摘要: This main method downloads a file from a URL, reads it as a zip archive, and extracts each entry to a file.
- 静态失败原因: The models likely rely on lexical and structural similarity which are low (Jaccard 0.117). They missed the abstract similarity of stream reading/writing, possibly because the tokens and control flow are dissimilar.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as 'I/O stream processing' clones due to common use of InputStream and stream copying patterns, despite different specific tasks and output.
- 共享行为: Both functions process input streams and copy data to another format (byte array or file).
- 行为差异: A outputs in-memory representation (buffered image) and sets object fields; B writes zip entries to disk files.；A handles image detection and uses a specific imaging library; B handles HTTP connection and zip decompression.；A's stream is parameter; B creates its own stream from a hardcoded URL.
- 修正建议: Incorporate data flow information to identify common I/O patterns.；Use program slicing to isolate core stream handling logic.；Add more training examples of cross-application I/O clones.

### case_id=3421 FN partial_functionality

- 方法: `copyResource` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.95`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copy a resource (URL or local file) to a destination file using byte stream I/O.
- B 摘要: Copy a file to another file using NIO FileChannel transferFrom.
- 静态失败原因: Static BERT/GraphCodeBERT models rely on lexical and API surface similarity; here token overlap is low (0.19) and APIs differ (InputStream vs FileChannel), leading to false negative.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often considers functions that copy data as functionally similar clones (Type-4), even if implementations differ, because the core task is identical.
- 共享行为: Both copy data from a source to a destination file.
- 行为差异: copyResource supports URL sources and throws generic Exception; copyFile only handles File sources and throws IOException.；copyResource reads byte-by-byte; copyFile uses channel transfer for efficiency.；copyResource includes a fallback to FileInputStream if URL fails; copyFile assumes source is File.
- 修正建议: Incorporate data-flow analysis to recognize the common copy pattern despite different I/O mechanisms.；Use graph-based representations that abstract control and data dependencies.；Train on more diverse examples of I/O operations to learn functional equivalence beyond surface APIs.

### case_id=3422 FN partial_functionality

- 方法: `httpRequestByPOST` vs `postData`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends HTTP POST with form parameters using Apache HttpClient, returns response body or null on error.
- B 摘要: Sends HTTP POST with a string data using URLConnection, reads and discards response, throws Exception on error.
- 静态失败原因: Static models like GraphCodeBERT may focus on token overlap and surface syntax, which are low (Jaccard 0.13), and miss the underlying semantic similarity of HTTP POST operations.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as HTTP POST implementations despite different libraries, return types, and error handling, focusing on the common goal of posting data.
- 共享行为: Both send HTTP POST requests；Both set content type to application/x-www-form-urlencoded；Both read the response input stream
- 行为差异: Different libraries: Apache HttpClient vs URLConnection；A takes NameValuePair list, B takes plain string data；A returns response string or null, B is void；A handles errors via fields and null, B throws exceptions
- 修正建议: Include data flow analysis to track network I/O operations；Use API sequence embeddings to capture high-level behavior；Train on more diverse clone types including library-specific implementations

### case_id=3423 FP lexical_or_api_overlap

- 方法: `SRWGuiClient` vs `doVersionCheck`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Constructor that builds a Swing browser GUI, reads XML from a URL, optionally transforms it with XSLT, and displays the result as HTML.
- B 摘要: Static method that fetches a version check URL, reads lines to extract build numbers, and calls another method to compare versions.
- 静态失败原因: Static BERT/GraphCodeBERT models may have focused on overlapping tokens like 'URL', 'BufferedReader', 'InputStreamReader', 'readLine', etc., and missed the larger structural and semantic differences. The models may not capture the overall intent and control flow differences, especially when there is boilerplate code for I/O.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels non-clone because the functions have entirely different purposes and contexts: one is a GUI browser constructor, the other is a static version check utility. They share only trivial reading from a URL, which is a common idiom.
- 共享行为: Both open a URL and read lines from it using BufferedReader.
- 行为差异: Function A is a constructor setting up a GUI and performing XSLT transformation; Function B is a static utility for version checking without GUI.；Function A handles XML parsing and XSLT transformation; Function B parses specific build version strings.；Function A uses JEditorPane to display HTML; Function B calls another method doVersionCheck with arguments.；Function A involves user interaction and layout; Function B shows/hides wait cursor.
- 修正建议: Improve model's ability to distinguish different program purposes despite overlapping I/O patterns.；Include more data-flow or control-flow features.；Use contrastive learning to separate these patterns.

### case_id=3424 FN partial_functionality

- 方法: `runInternal` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.4`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Sets up HTTP connection with custom headers, downloads OPDS catalog, handles pagination, and downloads books or calls callback.
- B 摘要: Opens a URL and prints its content to standard output.
- 静态失败原因: Low lexical overlap (token Jaccard 0.0567) and different code structure led static model to predict non-clone, while BCB may consider broader semantic similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label as clone due to broad functional overlap of 'reading from a URL', but this is a stretch given significant differences.
- 共享行为: Both open an HTTP URL and read the response.
- 行为差异: A uses advanced connection configuration (user-agent, referer, timeout, follow redirects), handles different content types (OPDS vs book download), manages pagination, and uses callbacks; B simply reads lines and prints to console.
- 修正建议: Incorporate data-flow analysis to detect URL reading operations；Use models that capture long-range dependencies and high-level semantics

### case_id=3425 FN partial_functionality

- 方法: `copyResource` vs `getResponse`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource from a URL or file to a destination file.
- B 摘要: Parses an HTTP GET request, loads a resource from classpath, and returns an HTTP response with the resource content.
- 静态失败原因: The model relies on token and structural similarity, which is low. It misses the abstract read-copy-write pattern due to different API calls, control flow, and overall purpose.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considers this a Type-4 clone because both methods perform the core operation of reading a resource and copying it to an output stream, even though the context (file copy vs HTTP response) and error handling differ.
- 共享行为: Both open an input stream from a resource (URL/file or classpath).；Both read the input stream and write its contents to an output stream (file or ByteArrayOutputStream).
- 行为差异: A writes to a file; B returns a byte array as HTTP response.；A obtains resource location from a source field; B parses an HTTP request to get the resource path.；B includes HTTP status lines and error handling for 400/404; A throws an exception if resource not found.；B uses IOUtils.readLines and IOUtils.copy; A uses manual byte-by-byte copy.
- 修正建议: Incorporate data-flow analysis to detect resource copying patterns.；Train on more examples of Type-4 clones with different contexts.；Use higher-level abstractions like 'resource copying' as a feature.

### case_id=3426 FP boilerplate_overlap

- 方法: `createCipher` vs `perform`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Creates a PBE cipher using PBEWithMD5AndDES for encryption/decryption.
- B 摘要: Handles an HTTP request for concept classification in a web application using Struts, XML, and URL connections.
- 静态失败原因: The model likely overgeneralized from superficial patterns like exception handling and loop structures, ignoring the vast difference in domain-specific APIs and logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would label as non-clone because the functions have entirely different purposes and implementations, with no meaningful semantic overlap.
- 共享行为: Both use try-catch for exception handling；Both involve byte array manipulation (A: salt, B: reading response)
- 行为差异: A performs cryptographic key generation and cipher initialization; B manages HTTP session, form data, and remote API calls；A is stateless and returns a Cipher object; B is stateful and returns an ActionForward；A uses MD5 digest; B uses URL connections and XML parsing；A has no I/O beyond internal byte operations; B performs HTTP I/O
- 修正建议: Include more context-aware features like API call sequences；Train with contrastive learning on long-range dependencies；Incorporate structural differencing of call graphs

### case_id=3427 FN benchmark_preference_bias

- 方法: `saveFileData` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Saves file data by potentially copying from a working file to a destination and updating with new content, followed by thumbnail cleanup.
- B 摘要: Builds a site for editing by iterating over pages, applying XSLT transformations, and writing output files with various replacements.
- 静态失败原因: The static BERT/GraphCodeBERT method likely relied on syntactic structure and token overlap (very low Jaccard=0.084), missing the high-level conceptual similarity that BCB considers based on overall domain and file operations.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may label as clone due to both functions performing file I/O within the same content management system, accepting broad functional similarity under Type-4 (e.g., 'file modification').
- 共享行为: Both involve file I/O operations；Both handle exceptions；Both use FileInputStream/FileOutputStream/FileChannel
- 行为差异: Function A focuses on file copy, truncation, image dimension extraction, and thumbnail deletion; Function B performs XSLT transformation, page iteration, and property handling；Different overall purpose: asset file maintenance vs site generation；Function A is static utility; Function B is instance method with multiple parameters
- 修正建议: Incorporate domain-specific heuristics or contextual embeddings；Use a classifier trained on BCB annotations to capture broad functional categories；Combine structural and semantic analysis with a broader notion of similarity

### case_id=3428 FP lexical_or_api_overlap

- 方法: `getWebByUrl` vs `getVersion`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Downloads a web page content and saves it to a file, with logging and recursive URL extraction.
- B 摘要: Fetches a version string from a specific URL and returns it, with minimal logging.
- 静态失败原因: The model likely overweighed lexical and API overlap (URL, URLConnection, BufferedReader, while-readline pattern), ignoring the broader functional context and output differences.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled non-clone because the functions have distinct purposes (web page download vs version retrieval) and significantly different output handling, despite some shared API usage.
- 共享行为: Both open a URL connection and read lines from an input stream using BufferedReader.
- 行为差异: A saves content to a file; B returns a string.；A uses PrintWriter and FileOutputStream; B does not write to file.；A includes logging and recursive URL fetching; B does not.；B has a specific hardcoded URL; A takes URL as parameter.
- 修正建议: Incorporate dataflow analysis to distinguish output handling.；Use contrastive learning on pairs with high lexical but low semantic similarity.

### case_id=3429 FN partial_functionality

- 方法: `readGeoParserResult` vs `getWebByUrl`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Queries a geo-parser web service with XML, parses response to extract place names and gazetteer IDs, returns collection of tuples, with retry on failure.
- B 摘要: Downloads a web page from a URL, writes it to a file, recursively explores URLs found on the page, logs progress.
- 静态失败原因: Low token overlap (0.146) and different method names, return types, and specific processing logic led the model to miss the higher-level functional similarity. The model likely relied on surface-level features rather than recognizing the shared pattern of URL fetching and line reading.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label as clone because both functions perform HTTP GET requests, read responses line by line, and handle I/O exceptions, representing the common pattern of 'fetching data from a URL'.
- 共享行为: Open a URL connection and read input line by line using BufferedReader；Use StringBuffer to accumulate lines；Handle I/O exceptions with try-catch
- 行为差异: Function A constructs an XML request and sends it; B directly opens URL；A parses XML response; B writes raw lines to a file；A implements retry loop; B recursively processes embedded URLs；A returns a Collection of tuples; B returns void and writes to file
- 修正建议: Augment training data with diverse implementations of web fetching；Use code representation that captures control flow and data flow (e.g., graph-based models)；Incorporate token-level similarity with synonym or paraphrase detection

### case_id=3430 FN lexical_or_api_overlap

- 方法: `doTransfer` vs `executeHttpGet`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Forwards an incoming HTTP request to a target URL, copying headers and body, and returns the response.
- B 摘要: Executes an HTTP GET request to a URI and returns the response body parsed as a JSONObject.
- 静态失败原因: Low token overlap (0.078) and different method signatures/names made the model miss the semantic similarity. The model likely relies on lexical/structural features and fails to recognize cross-library HTTP client functionality as equivalent.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB often labels Type-4 semantic clones based on shared high-level functionality, such as 'performing an HTTP request and processing the response', even if the libraries and detailed steps differ.
- 共享行为: Both make an HTTP request to a remote server；Both read and process the HTTP response
- 行为差异: A uses HttpURLConnection, B uses Apache HttpClient；A is a full proxy handling both request and response streams, B only performs a GET and returns JSON；A sets request method dynamically from input, B always uses GET；A returns nothing directly (writes to response), B returns a JSONObject
- 修正建议: Use API sequence or call-graph embeddings to capture functional similarities across different libraries；Incorporate synonym or library-aware embeddings to match java.net.HttpURLConnection with org.apache.http.client.HttpClient；Train models with more examples of cross-library semantic clones

### case_id=3431 FP boilerplate_overlap

- 方法: `readVersion` vs `downloadFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads version, revision, and date from a local 'version' resource file and updates member variables.
- B 摘要: Downloads a file from a given URL to a destination path, with progress reporting via a GUI.
- 静态失败原因: The static BERT model likely over-weighted the overlapping structural patterns (URL connection, buffered streams, try-catch-finally) while ignoring the distinct semantic goals and data processing logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels require similar functionality; these two methods perform completely different tasks and only share boilerplate stream handling, so they are not clones.
- 共享行为: Both open a URL and read from an input stream；Both handle IO exceptions and close streams in finally blocks
- 行为差异: One reads metadata from a local resource file; the other downloads and saves a binary file；One parses key-value pairs; the other writes bytes to a file；One updates internal state; the other returns a boolean and updates UI progress
- 修正建议: Incorporate dataflow analysis to capture variable-level semantics；Add attention to method name and return type to distinguish purpose；Train on more diverse examples of boilerplate vs. actual functionality

### case_id=3432 FP other

- 方法: `readData` vs `unJar`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Reads and processes various tokenized string constants into sets and a hash map for Tibetan transliteration data.
- B 摘要: Extracts a specific entry from a JAR file and writes it to a file on the filesystem.
- 静态失败原因: The static model likely overfit on trivial surface features such as both containing loops or the word 'String', leading to a false positive despite very low token overlap.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB correctly labeled these as non-clones because they perform entirely different tasks with no functional overlap.
- 行为差异: Function A parses comma-separated tokens into set structures; function B extracts a JAR entry.；Function A manipulates string sets and maps; function B performs I/O operations with files and JAR archives.；Function A does not return a value; function B returns a file path string.
- 修正建议: Improve model sensitivity to high-level semantic differences through better training data or contrastive learning.；Incorporate control flow and data flow analysis to distinguish I/O operations from string parsing.

### case_id=3433 FP lexical_or_api_overlap

- 方法: `readData` vs `main`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Parses tokenized strings and a file to populate various sets and a map for a Tibetan transliteration system.
- B 摘要: Sets up a Weka experiment GUI, including loading/saving experiment objects and handling window events.
- 静态失败原因: The static BERT/GraphCodeBERT model likely overestimated similarity due to lexical overlapping tokens (e.g., 'try', 'catch', 'IOException', 'FileInputStream', 'ObjectInputStream') and common boilerplate patterns like reading files and parsing lines, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the functions have completely different high-level purposes (data initialization vs. GUI setup), despite some shared low-level constructs like try-catch and file I/O.
- 共享行为: Both contain try-catch blocks for exception handling.；Both perform file I/O operations (file reading/writing).；Both use StringTokenizer-like parsing (A uses StringTokenizer, B uses StreamTokenizer via ObjectInputStream).
- 行为差异: A initializes static data structures from tokenized strings and a file; B sets up a GUI application with experiment management.；A populates many HashSets and a HashMap; B creates a JFrame and handles user interaction.；A processes internal configuration; B interacts with command-line arguments and serialized objects.
- 修正建议: Incorporate dataflow analysis to distinguish initialization from GUI setup.；Use control-flow graphs to compare high-level structure rather than token sequences.；Train on more diverse examples of non-clone pairs with API overlap to reduce false positives.

### case_id=3434 FN benchmark_preference_bias

- 方法: `modifyApplicationMessage` vs `createOutputStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Modifies a locale-specific .properties file by updating or adding a key-value pair, creating the file if missing by copying from English version.
- B 摘要: Reads a zip file, copies all entries except 'content.xml', then returns a BufferedWriter for a new 'content.xml' entry.
- 静态失败原因: The static BERT model did not fail; it correctly predicted non-clone (0) due to low token overlap and clear semantic differences. The misclassification is due to the BCB annotation being erroneous or overly broad.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as a clone due to both functions involving extensive file I/O, reading and writing with streams, and similar structural patterns (try-catch, loops, file manipulation). Under a very broad Type-4 definition, they could be considered semantically similar as 'file modification utilities', but this interpretation is overly loose.
- 共享行为: Both perform file I/O operations using character streams and buffering；Both involve reading a file and writing to another file
- 行为差异: Function A modifies a key-value pair in a properties file; Function B processes a zip archive and returns a writer；Function A creates a properties file if it doesn't exist; Function B always expects input file to exist；Function A uses Properties class and explicit line-by-line parsing; Function B uses ZipInputStream/ZipOutputStream；Function A's output is a properties file; Function B's output is a BufferedWriter for a zip entry
- 修正建议: Re-evaluate BCB annotation for this pair; consider correcting label to non-clone；Focus on core functional similarity rather than generic I/O patterns；Improve benchmark consistency by requiring more specific semantic equivalence criteria

### case_id=3435 FP lexical_or_api_overlap

- 方法: `doVersionCheck` vs `downloadModel`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Checks for a new version of jEdit by fetching a version file from a URL and comparing the build number.
- B 摘要: Downloads an RDF model from a given URL by opening an HTTP connection and reading the input stream into a model object.
- 静态失败原因: The static model likely over-emphasized surface-level API usage (URL, InputStream, BufferedReader, IOException) and control-flow similarity (try-catch-IO), missing the semantic intent difference and the distinct post-processing logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels as non-clone when the overall functionality differs significantly, even if some structural patterns overlap. Here the tasks are distinct (version checking vs. model downloading), so BCB correctly marks as non-clone.
- 共享行为: Both open a URL connection and obtain an InputStream；Both parse or process the input stream；Both handle IOException
- 行为差异: Function A reads lines and checks version/build strings; Function B reads RDF data into a model；Function A sets no HTTP headers; Function B sets Accept and Accept-Language headers；Function A returns void; Function B returns a Model；Exception handling differs: A shows dialogs; B logs and throws RuntimeException
- 修正建议: Train on pairs that highlight overall functionality rather than just API calls；Add dataflow or graph representations to capture the purpose of data transformation；Include more diverse non-clone pairs with similar API usage but different goals

### case_id=3436 FN partial_functionality

- 方法: `getHTML` vs `lookupFutureEvents`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches HTML from a given URL using HttpURLConnection, optionally saves to file, and returns the page HTML as a string.
- B 摘要: Fetches JSON data from a Meetup API, parses it into a list of Event objects, and returns the list.
- 静态失败原因: Static BERT models like GraphCodeBERT rely heavily on token overlap and structural similarity. The low Jaccard similarity (0.168) and different return types, method names, and additional logic in function B (JSON parsing, object creation) likely led the model to classify them as different. The model might not capture the abstract similarity of the HTTP fetch pattern due to the disparate surrounding code.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB annotators might consider these clones because both functions perform a common underlying task of fetching data from a URL and reading it line by line into a string, which is a recognizable pattern. The differences in output processing (file writing vs. JSON parsing) might be considered secondary, especially under Type-4 (functionally similar but different logic). The annotation likely focused on the core networking and I/O pattern.
- 共享行为: Both open a URL connection to fetch remote data；Both read the response line by line into a StringBuilder；Both use BufferedReader and InputStreamReader；Both handle IOException
- 行为差异: A returns raw HTML string, B returns parsed List<Event>；A optionally writes to file, B does not；B performs JSON parsing and object construction, A does not；A uses HttpURLConnection with custom headers, B uses URL.openStream()
- 修正建议: Improve training data to emphasize partial functionality clones；Use code representation that captures control and data flow of the common subpattern；Train with objective that focuses on I/O patterns

### case_id=3437 FN partial_functionality

- 方法: `copyFile` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a local file to another local file using a buffer.
- B 摘要: Fetches a resource from a URL, caches it locally, and returns an InputStream, with HTTP and caching logic.
- 静态失败原因: The model failed to recognize the clone because it focused on the overall different logic and low token overlap (0.168), missing the high-level similarity in the read-write loop that BCB considered.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled these as clones due to the presence of a common read-write loop and file I/O operations, considering them as Type-4 (similar functionality) because both transfer data from a source to a destination.
- 共享行为: Both read data from an input stream and write to an output stream in a loop.；Both use try-finally for resource cleanup.
- 行为差异: Different sources and destinations (file vs. URL).；Different error handling (propagates exception vs. catches and returns null).；Different control flow (caching, HTTP status checks, etc.).；Different output (void vs. InputStream).
- 修正建议: Enhance models to detect partial functional similarity beyond token overlap.；Incorporate intermediate representations that capture common sub-patterns like read-write loops.

### case_id=3438 FN partial_functionality

- 方法: `readGeoParserResult` vs `run`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Parses geolocation data by sending an XML request to a geo service and extracting place names and gazetteer IDs.
- B 摘要: Executes an HTTP GET request with basic authentication and stores the entire response as a string.
- 静态失败原因: The models likely rely on token overlap and structural similarity, which is low (Jaccard=0.118). They failed to capture the functional similarity of the HTTP request-response pattern due to large differences in tokens and API calls.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider them Type-3 clones because both involve the core pattern of opening an HTTP connection, reading lines, and appending to a buffer, despite differences in surrounding code.
- 共享行为: Both functions make HTTP requests and read the response line by line using BufferedReader.
- 行为差异: Function a has retry logic, error handling, XML request construction and response parsing.；Function b does not have retries and only stores raw text.；Function a returns a structured collection; function b sets internal fields and stores a string.；Function a uses URL directly; function b uses HttpURLConnection.
- 修正建议: Improve model's ability to identify common programming patterns (e.g., HTTP IO pattern) via dataflow or control flow analysis.；Incorporate source code semantics at higher abstraction levels, like using code summarization or program slicing.

### case_id=3439 FN benchmark_preference_bias

- 方法: `getEncoding` vs `doVersionCheck`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `preference_memory_with_manual_audit`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Extracts character encoding from HTTP response headers or body.
- B 摘要: Checks for newer software version by reading version info from a URL.
- 静态失败原因: Static BERT models rely on token-level representations and may focus on low lexical overlap (Jaccard 0.186) and structural differences, failing to capture the high-level functional similarity that BCB's broad annotation accepts.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB likely labels as clone because both functions perform the common task of fetching data from a URL and extracting information by parsing lines, considering this a Type-4 (functionally similar) clone despite different specific extraction logic.
- 共享行为: Open a URL connection；Read lines from input stream using BufferedReader；Parse each line for specific patterns；Extract a value (encoding or version/build)
- 行为差异: A looks for charset in headers then body; B looks for .version and .build lines；A returns encoding or default; B compares version and shows messages；A uses URLConnection and getHeaderFields; B uses openStream directly；A has try-finally with reader close; B has try-catch with exception handling and cursor management
- 修正建议: Incorporate functional similarity detection by using abstract syntax trees or control flow graphs；Use contrastive learning with positive pairs of Type-4 clones to capture partial functional overlap；Augment training data with BCB-style annotations to align with benchmark preferences

### case_id=3440 FN partial_functionality

- 方法: `doVersionCheck` vs `invoke`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Checks for a newer version by fetching a version file from a URL and comparing build numbers.
- B 摘要: Invokes a remote HTTP service method by sending a POST request with JSON arguments and parsing the response.
- 静态失败原因: Static BERT models rely on token-level similarity and semantic embeddings. The low token Jaccard similarity (0.16) and different vocabulary (version/build vs invoke/HTTP/JSON) cause the model to judge them as non-clones. The abstract pattern of network I/O is not captured due to concrete token differences.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label these as Type-4 clones because both implement a network-based data retrieval and line-by-line parsing pattern, even though the specific data and purpose differ. The overall structure of opening a stream, reading lines, parsing, and error handling is similar enough for a broad clone definition.
- 共享行为: Both open a URL and create an InputStream.；Both use BufferedReader to read lines from the stream.；Both parse each line for specific patterns.；Both handle exceptions (IOException or ConnectTimeoutException).
- 行为差异: A is a read-only version check; B sends a POST request with arguments.；A displays UI messages; B returns an object for further use.；A uses view cursor wait indicators; B does not.；B includes retry logic on timeout; A does not retry.
- 修正建议: Use structure-aware embeddings or program dependency graphs to capture common I/O patterns.；Train on a broader set of clone types that include abstract dataflow patterns.；Incorporate API call sequences or control flow graphs to detect similar structural behavior despite different tokens.

### case_id=3441 FN partial_functionality

- 方法: `createNew` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Creates a file by writing an input stream to a destination, with ownership check and logging.
- B 摘要: Builds a site for editing by reading XML, applying XSLT transformations, and writing multiple output files with string manipulations and file I/O.
- 静态失败原因: The model failed due to low lexical overlap (token Jaccard 0.069) and the large size of function B, causing the model to focus on surface-level differences and miss the underlying functional similarity in file output. Additionally, function B was truncated, which may have obscured the full context.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely labeled them as clones due to shared file writing functionality and similar resource management patterns, accepting broad Type-3/Type-4 similarity based on common I/O operations.
- 共享行为: Both write data to files using output streams or writers.；Both use try-finally or try-catch blocks for resource management.；Both include logging statements for debugging.
- 行为差异: Function A writes a single file from an InputStream; Function B writes multiple files from XML transformations.；Function A has an ownership check; Function B does not but includes extensive DOM parsing and XSLT.；Function A is short and simple; Function B is long and complex with many parameters and nested loops.
- 修正建议: Improve detection of partial functional similarities by incorporating control flow and data flow features.；Use code summarization or high-level purpose extraction to capture shared behaviors.；Handle long functions with better attention mechanisms or hierarchical representations.

### case_id=3442 FP lexical_or_api_overlap

- 方法: `run` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a file input stream, optionally applies diagnostic readers/writers, and pumps data to an output file.
- B 摘要: Handles GUI action events for setting file paths for Graphviz and ImageMagick executables, and updates UI preferences.
- 静态失败原因: The static BERT/GraphCodeBERT method likely relied on superficial token similarities (e.g., both use 'File', 'String', 'if') or could not capture the high-level purpose difference due to limited context or training data bias.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: None
- 共享行为: No shared behavior
- 行为差异: One performs file I/O pumping with optional diagnostics；The other handles GUI event handling and preference setting；Different method signatures and control flow；Different APIs (streams vs Swing)
- 修正建议: Improve model to consider overall program structure and data flow；Use control flow and data dependency features；Enhance training with more diverse negative examples

### case_id=3443 FN boilerplate_overlap

- 方法: `main` vs `doVersionCheck`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Constructs and sends a hardcoded POST request to the RenRen API, printing the response.
- B 摘要: Connects to a version-check URL, reads build information, and triggers an update check if applicable.
- 静态失败原因: The model likely focused on lexical similarities in boilerplate network I/O code, missing the significant differences in purpose, data handling, and overall logic.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may have labeled as clone due to overlapping boilerplate of network I/O loops (URL, BufferedReader, readLine) despite different semantics.
- 共享行为: Open a URL connection；Read lines from an input stream using BufferedReader；Loop until end of stream
- 行为差异: Function A uses POST with multiple hardcoded parameters; Function B uses GET with no parameters.；Function A prints raw response; Function B parses lines for build numbers and calls another method.；Error handling: A throws IOException; B catches and shows an error dialog.；Purpose: A is a one-off API test; B is a plugin version check.
- 修正建议: Incorporate dataflow analysis to track how input/output are used.；Consider method names, parameters, and call context as signals.；Use type-aware dependency graphs to distinguish different API usages.

### case_id=3444 FP lexical_or_api_overlap

- 方法: `sendPost` vs `addQDInformation`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Sends an HTTP POST request with parameters and returns the response body as a string.
- B 摘要: Reads a local or remote file containing update information and updates internal project data structures.
- 静态失败原因: Static BERT models may overweigh lexical and API-level overlaps (e.g., BufferedReader, URL, try-catch) while missing the high-level semantic difference: one is a general-purpose HTTP POST, the other is a domain-specific data loader. The model may have been confused by the similar loop structure and exception handling boilerplate.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels non-clones when functions have entirely different purposes, even if they share some common I/O patterns. The low token Jaccard (0.14) and different method names argue against similarity. BCB would likely consider this a true non-clone.
- 共享行为: Both use BufferedReader to read lines from an input stream.；Both have try-catch blocks for I/O exceptions.；Both use URL class to handle network resources.
- 行为差异: A performs an HTTP POST; B performs an HTTP GET or file read.；A is stateless and returns a string; B modifies instance fields (_qdDate, _qdValue).；A is a utility function with parameters; B is a private method with no parameters, relying on instance state.；A's main purpose is communication; B's main purpose is parsing a specific file format to update project information.
- 修正建议: Incorporate data-flow and control-flow features to distinguish different high-level intents.；Use method names and documentation as additional signals to disambiguate purpose.；Train on a more diverse set of non-clone pairs with similar API usage but different semantics.

### case_id=3445 FN partial_functionality

- 方法: `addQDInformation` vs `File2String`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a local or remote file 'qdinfo.dat', parses lines with 'pg ' and 'pt ' prefixes to update internal project dates and values.
- B 摘要: Reads a file from local filesystem or system resource, concatenates all lines into a single string and returns it.
- 静态失败原因: Static BERT models rely heavily on token overlap and may miss the structural similarity in file-reading boilerplate; low Jaccard (0.2586) and different method names lead to non-clone prediction.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider them Type-4 clones because both involve reading a text file line by line with similar I/O boilerplate (try-catch, BufferedReader), despite different parsing and output.
- 共享行为: Both open a file (or URL) and read lines using BufferedReader
- 行为差异: Function A modifies internal state (project info), Function B returns a concatenated string；Function A parses lines with specific prefixes, Function B simply appends all lines；Function A may read from local file or HTTP URL, Function B may read from local file or classpath；Function A handles multiple project entries, Function B reads a single file
- 修正建议: Add features capturing common I/O patterns (e.g., file read, BufferedReader usage)；Consider control flow and data flow similarities beyond surface tokens

### case_id=3446 FN dataflow_blindspot

- 方法: `getFile` vs `writeFileToFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.65`
- 推荐路线: `dynamic_equivalence_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Downloads a WSDL file from a URL, optionally modifies an XML attribute, and saves the result to a temporary file.
- B 摘要: Copies the entire content of one file to another file using FileChannel, with optional append mode.
- 静态失败原因: Static BERT models like GraphCodeBERT rely on token-level and structural patterns, but the token overlap is low (0.13). They may miss the subtle functional similarity of FileChannel usage because the rest of the code (URL handling, XML parsing) is very different and dominates the representation.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行价值高：该样本可能是 API 写法不同但行为等价的漏报。建议测试目标为 input_output_equivalence。
- BCB 偏好解释: BCB may label them as clones due to the shared use of FileChannel for bulk data transfer, which is a relatively distinctive pattern. The functions are Type-4 similar in that they achieve data transfer via channels, even if the overall purpose differs.
- 共享行为: Both use FileChannel to transfer data between streams；Both involve file I/O operations
- 行为差异: Function A fetches data from a URL and modifies XML; Function B only copies local files；Function A handles multiple exceptions and logging; Function B is simpler；Function A processes WSDL-specific modifications; Function B is a generic file copy
- 修正建议: Increase sensitivity to common library usage patterns like FileChannel；Use dataflow-aware models that capture I/O operations；Incorporate functional semantics through program slicing or API call sequences

### case_id=3447 FP boilerplate_overlap

- 方法: `main` vs `dump`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Parses a Prolog file and generates adapter classes, lookup tables, and writes them into a JAR file.
- B 摘要: Copies the contents of a source file to a target file using buffered streams.
- 静态失败原因: The static model may have been misled by overlapping boilerplate tokens (e.g., 'File', 'IOException', 'return', try-catch structure) and common API usage, despite very low Jaccard similarity.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the functions have entirely different purposes and no shared algorithmic functionality, even under broad Type-4 semantic clone definition.
- 共享行为: Both perform file I/O operations；Both handle IOException via try-catch
- 行为差异: A has complex parsing, class generation, and serialization; B only copies bytes；A uses many external libraries (PrologParser, FactVisitor, etc.); B uses only standard Java I/O；A generates output as a JAR with multiple entries; B produces an identical copy；A operates as a command-line tool; B is a utility method
- 修正建议: Enhance model to distinguish domain-specific operations from generic I/O；Incorporate dataflow analysis to capture data transformations；Add more negative training examples of simple file utilities vs complex generators

### case_id=3448 FN partial_functionality

- 方法: `getHTML` vs `read`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches HTML content from a URL using HttpURLConnection, reads lines, optionally writes to a file, and returns HTML string.
- B 摘要: Reads from a URL or file using BufferedInputStream and returns a status code after processing via internal read method.
- 静态失败原因: Low token Jaccard (0.1667) and different method signatures, return types, and API usage (HttpURLConnection vs BufferedInputStream) make them appear distinct; model lacks high-level functional understanding.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as functions that fetch data from a URL, focusing on shared input-output pattern of reading from a URL despite differences in return type and processing details.
- 共享行为: Both read data from a URL；Both handle I/O exceptions
- 行为差异: A returns content as string; B returns integer status；A uses BufferedReader and StringBuilder; B uses BufferedInputStream；A optionally writes to file; B does not；A sets User-Agent header; B does not
- 修正建议: Enhance model with structural or data flow representations；Use intermediate representation like control flow graphs；Consider renaming or parameter normalization；Incorporate functional semantics via call hierarchy or documentation embeddings

### case_id=3449 FN partial_functionality

- 方法: `copyResource` vs `copy`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.95`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource from a URL or local file to a destination file using single-byte reads.
- B 摘要: Copies a file to another file using buffered reads.
- 静态失败原因: Static BERT/GraphCodeBERT models often rely on lexical overlap and syntactic patterns; the low token Jaccard (0.23) and different APIs (URL vs File, single-byte vs buffer) cause the model to miss the functional similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB labels both as clones (Type-4) because they perform the same core functionality—copying bytes from source to destination—despite differences in input handling and buffering.
- 共享行为: Both copy byte streams from a source to a destination file.；Both use InputStream and OutputStream to perform I/O.；Both close the streams after copying.
- 行为差异: Function A supports both URL and local file sources; Function B only handles File objects.；Function A reads one byte at a time; Function B uses a 1024-byte buffer.；Function A throws a generic Exception if resource not found; Function B declares FileNotFoundException and IOException.；Function A does not use try-finally for stream closing; Function B uses try-finally block.
- 修正建议: Use dataflow analysis to track the core I/O operations (read, write, close).；Normalize variable names and API calls to abstract file copying.；Train on more functional-level clone pairs with low lexical similarity.；Incorporate structural patterns like stream lifecycle detection.

### case_id=3450 FP partial_functionality

- 方法: `getRequestContent` vs `postRequest`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Opens an HTTP GET connection to a given URL, reads the first line of the response, and returns it; throws an exception on error.
- B 摘要: Opens an HTTP POST connection to a given URL, sends form-encoded key-value pairs from a HashMap as the request body, reads the entire response line by line, concatenates it, and returns the result; returns null on any exception.
- 静态失败原因: Static BERT/GraphCodeBERT may have focused on the high structural overlap (URL, HttpURLConnection, BufferedReader, readLine) and overlooked the crucial differences in HTTP method and data handling, leading to a false positive.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely classifies these as non-clones because they have distinct HTTP methods (GET vs POST) and different return behaviors (first line vs full body), making them functionally dissimilar despite sharing some low-level HTTP handling code.
- 共享行为: Both use URL and URLConnection to make HTTP requests；Both read from an InputStream using BufferedReader；Both return a String from the response
- 行为差异: Function A performs a GET request; Function B performs a POST request with data；Function A returns only the first line of the response; Function B returns the entire response body；Function A declares 'throws Exception'; Function B catches exceptions and returns null；Function B takes an additional HashMap parameter for request data
- 修正建议: Incorporate explicit features for HTTP method (GET/POST) and whether data is sent；Use more fine-grained control flow analysis to distinguish between reading first line vs full response；Leverage method signatures (parameter types) and exception handling patterns

### case_id=3451 FP partial_functionality

- 方法: `decodeFileToFile` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Decodes a Base64-encoded input file and writes the decoded content to an output file, returning success status.
- B 摘要: Handles action commands from a GUI, typically opening file choosers and updating preferences and UI components based on user selection.
- 静态失败原因: The provided code for Function B is truncated (contains '... TRUNCATED MIDDLE ...'), so the model may have only seen partial code leading to misinterpretation. Additionally, both functions contain common Java idioms (try-catch, File usage) that could cause superficial similarity.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB would label these as non-clones because they perform completely different tasks (file decoding vs. GUI event handling), with no shared functionality beyond trivial lexical overlaps.
- 共享行为: Both involve file paths in some way (one reads/writes files, the other opens file chooser to select a file).
- 行为差异: Function A performs actual file I/O for Base64 decoding; Function B is a GUI event handler that sets preferences and updates UI.；Function A has a loop reading and writing 64KB buffers; Function B has no I/O loop.；Function A returns a boolean; Function B returns void.；Function B uses multiple conditional branches based on command strings; Function A has no conditionals on input.
- 修正建议: Ensure full function code is available without truncation.；Improve model sensitivity to overall task structure vs. local patterns.；Incorporate explicit dataflow or call-graph analysis to distinguish I/O from GUI logic.

### case_id=3452 FP lexical_or_api_overlap

- 方法: `readScalarpvviewerDocument` vs `addQDInformation`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads an XML configuration from a URL and applies it to a scalar PV viewer UI.
- B 摘要: Reads project information from a local or remote file and updates internal project data structures.
- 静态失败原因: Static BERT models might focus on surface-level syntactic patterns like try-catch, while loops, BufferedReader usage, and line reading, missing the semantic differences in data format and output.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely considers these as non-clones because they operate on completely different data formats and produce entirely different outputs, even though the high-level pattern of reading and parsing is similar.
- 共享行为: Both read data from a URL or file using BufferedReader；Both parse lines sequentially；Both handle IO exceptions
- 行为差异: A parses XML using XmlDataAdaptor; B parses custom text format；A configures UI components; B updates internal project data；A has complex multi-level parsing; B uses simple line prefix matching；A has more extensive error handling and UI updates
- 修正建议: Improve model's ability to distinguish between different parsing logic and data formats；Incorporate data flow analysis to understand how input is transformed into output；Enhance training with more diverse examples of file reading vs data processing

### case_id=3453 FP lexical_or_api_overlap

- 方法: `getWebPage` vs `getRequestContent`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches entire webpage content by reading all lines and returns as a single string, throwing an Error on IOException.
- B 摘要: Fetches only the first line of the HTTP response content, closing resources and throwing Exception on failure.
- 静态失败原因: The model likely relied on overlapping API calls (URL, BufferedReader, InputStreamReader) and similar control flow (try-catch, while loop) without capturing the critical difference in the number of lines read, which changes the output semantics.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels non-clones when functions differ in core behavior (e.g., reading all vs. one line). The difference in return value completeness likely outweighs the structural similarity.
- 共享行为: Both fetch content from a URL using HTTP.；Both use BufferedReader and InputStreamReader to read the response.；Both return a String containing the fetched content.
- 行为差异: getWebPage reads all lines and concatenates them; getRequestContent reads only the first line.；getWebPage wraps IOException in an Error with a verbose message; getRequestContent throws Exception directly.；getWebPage does not explicitly close the stream; getRequestContent closes the reader and disconnects.；getWebPage takes a URL object; getRequestContent takes a URL string and creates a new URL object.
- 修正建议: Enhance model to differentiate between partial vs. full content retrieval.；Incorporate data-flow analysis to track how the content is accumulated (e.g., concatenation vs. single line).；Use more fine-grained structural matching to catch differences in loop behavior and resource management.

### case_id=3454 FN partial_functionality

- 方法: `File2String` vs `wordFrequency`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a file from local path or classpath and returns its entire content as a single string.
- B 摘要: Reads a web page by constructing a URL with a query word, searches lines for a frequency pattern, and returns the integer frequency or 0 if not found.
- 静态失败原因: Static BERT/GraphCodeBERT models rely on token overlap and surface-level syntax. The low Jaccard similarity (0.246), different return types, and different control flow (concatenation vs. pattern matching) cause the model to miss the shared I/O pattern. The model fails to abstract the common sub-task of reading lines from a stream.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB considers both as reading text input line-by-line from an external source, which falls under a common functional category (e.g., 'text file input processing') despite different output semantics. The broader clone definition includes Type-4 (functional similarity) where the core structure of reading lines is similar.
- 共享行为: Both open an input stream from an external source (file or URL).；Both read lines using BufferedReader in a while loop.；Both handle IOException via try-catch blocks.；Both return a value (String vs int) after processing input.
- 行为差异: A concatenates all lines into one string; B searches each line for a regex pattern.；A uses FileInputStream with fallback to ClassLoader; B uses URL.openStream.；A exits on failure; B returns 0 on failure.；A returns null on error; B returns 0.
- 修正建议: Incorporate program slicing to focus on shared I/O operations.；Use fine-grained structural representations like AST subtrees for reading loops.；Train with contrastive examples that emphasize functional similarity despite different outputs.

### case_id=3455 FP boilerplate_overlap

- 方法: `readData` vs `copyFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Parses multiple comma-separated initialization strings into various sets and a map, with optional file-based loading for Tibetan transliteration data.
- B 摘要: Copies a file from source to destination using NIO FileChannel with synchronized locking and proper resource cleanup.
- 静态失败原因: The model likely over-relied on common structural patterns (private static void, exception handling with try-catch-finally, I/O related imports) and failed to capture the distinct high-level semantics of the two methods.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB annotates 0 because these functions serve entirely different purposes (data initialization vs file copy) and are not functionally similar even at a broad level.
- 共享行为: Both handle IOException；Both use Java I/O-related classes
- 行为差异: readData initializes data structures from strings and possibly a file; copyFile transfers file content；readData populates sets and maps; copyFile returns boolean success；readData is private, no parameters; copyFile is public, takes two File parameters；readData uses StringTokenizer; copyFile uses FileChannel
- 修正建议: Improve model's ability to distinguish boilerplate from core functionality；Incorporate more detailed program analysis (e.g., dataflow, API usage patterns) to differentiate I/O utility from data parsing

### case_id=3456 FP lexical_or_api_overlap

- 方法: `readPage` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a URL's content line by line, optionally skipping lines starting with '#', and returns the concatenated HTML string.
- B 摘要: Searches Google Images for artist and album, downloads and parses the HTML to extract image URLs, and adds them to a list.
- 静态失败原因: The static model likely overemphasized the lexical and API-level overlap (URL, BufferedReader, while-readline pattern) while ignoring the deeper semantic differences in data processing and overall goal.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the high-level functionality is entirely different: one is a generic page reader, the other is a specific image search. Despite shared I/O boilerplate, the core purpose and output differ significantly.
- 共享行为: Open an HTTP URL connection using java.net.URL；Read input line by line using BufferedReader；Concatenate lines into a single string
- 行为差异: Function A returns the entire HTML content; Function B extracts specific image URLs from the HTML；Function A has an option to ignore comment lines; Function B does not；Function A does not parse or extract data; Function B performs string splitting and pattern matching；Function B uses HttpURLConnection and adds a User-Agent header; Function A uses plain URL.openStream()
- 修正建议: Incorporate structural awareness of the entire method body beyond I/O boilerplate；Use control-flow and data-flow analysis to capture divergent transformations of the input data；Enhance training with contrastive examples that share API usage but have different semantics

### case_id=3457 FP lexical_or_api_overlap

- 方法: `readUNI` vs `loadExistingAntlibs`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `1.0`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a tab-separated file from a URL and adds id and description pairs to a vector.
- B 摘要: Loads antlib resources from classpath, reads package names, and loads corresponding antlib XML files.
- 静态失败原因: The model likely focused on lexical and API-level similarities (e.g., URL, openStream, Scanner/BufferedReader, while loop) and overlooked the different semantics of the parsed data and the overall functionality.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels non-clone because the two functions have fundamentally different purposes and operate on different data structures, despite sharing a similar I/O pattern.
- 共享行为: Both open an InputStream from a URL or resource；Both read lines from the stream in a loop；Both handle exceptions and close the stream in finally
- 行为差异: Input source: URL vs classpath resources；Parsing logic: tab-separated fields vs package names；Purpose: collecting descriptions vs loading antlib definitions；Output: vector of strings vs calling loadAntLib for each package
- 修正建议: Incorporate domain-specific knowledge or data flow analysis to differentiate parsing tasks；Use contrastive learning to emphasize functional purpose over surface syntax；Train on more diverse examples where I/O patterns differ in semantics

### case_id=3458 FN partial_functionality

- 方法: `doVersionCheck` vs `read`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Performs a version check by reading a URL from jEdit property, parsing lines for build numbers, and invoking another method.
- B 摘要: Reads data from a file or URL, converting to BufferedInputStream, and delegates to another read method.
- 静态失败原因: Static BERT likely focused on method names ('doVersionCheck' vs 'read') and overall semantics, missing the structural I/O pattern and delegation. Low token overlap (0.25) also contributed to non-clone prediction.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely labels this as a clone because both functions follow the same pattern: open a URL, read input, handle IOException, and delegate to a method with similar name. The structural similarity in I/O handling and exception management is considered a Type-4 clone.
- 共享行为: Both open a URL stream and read input；Both handle IOException by setting error status or showing error dialog；Both call another overloaded method to continue processing
- 行为差异: A parses version-specific lines while B reads generic input；A uses BufferedReader with InputStreamReader, B uses BufferedInputStream；A shows error dialog, B returns integer status code；A manages cursor display, B does not
- 修正建议: Incorporate structural features like AST subtree matching；Use data flow analysis to capture common I/O patterns；Train on examples with similar I/O structure but different method names

### case_id=3459 FP lexical_or_api_overlap

- 方法: `readTwitterFead` vs `getEncoding`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a Twitter user timeline JSON from a fixed URL using HttpClient and returns the full content as a string.
- B 摘要: Opens a URL connection, parses HTTP headers and content to extract the charset encoding name, returning it or a default.
- 静态失败原因: The static BERT model likely overfocused on lexical and structural overlap (both use BufferedReader, readLine, try-catch, return String) and missed the semantic intent difference. It classified based on surface-level API similarity and standard I/O patterns.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels non-clones when functions have entirely different purposes and outputs, even if they share I/O boilerplate. Here, one fetches feed content, the other extracts encoding, so they are not even partial clones.
- 共享行为: Both use network I/O to retrieve data from a URL；Both read lines from a BufferedReader；Both return a String result
- 行为差异: A retrieves Twitter feed content; B extracts encoding name；A uses HttpClient; B uses URLConnection；A logs errors; B throws IOException；A appends all lines; B searches for charset patterns
- 修正建议: Incorporate data flow analysis to track how input is transformed；Use type information of return values to distinguish content from metadata；Include task-specific embeddings that capture high-level goals

### case_id=3460 FP lexical_or_api_overlap

- 方法: `populateResources` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Loads resource templates and default images from classpath and saves them to a database.
- B 摘要: Searches Google Images for album art and collects image URLs.
- 静态失败原因: Static BERT may have been misled by lexical and API overlap (e.g., URL, BufferedReader, InputStreamReader) without understanding the distinct semantic contexts and final purposes.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB considers these non-clones because their overall functionality is entirely different, despite superficial API overlap.
- 共享行为: Both use URL to open an input stream；Both read lines from a BufferedReader；Both handle exceptions with try-catch
- 行为差异: Different source URLs: local classpath vs. HTTP；Different output: saving resources vs. collecting URLs；Different data processing: template text and images vs. HTML parsing
- 修正建议: Incorporate dataflow or control-flow features to distinguish similar API usage patterns with different intents.；Use contrastive learning to better separate functionally distinct pairs sharing low-level I/O operations.

### case_id=3461 FN partial_functionality

- 方法: `login` vs `postData`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Logs into a specific service LOLA by sending email and password via HTTP POST, extracts session ID from response, and returns it.
- B 摘要: Generic HTTP POST method that sends arbitrary data to a given URL, ignoring the response content.
- 静态失败原因: Static BERT/GraphCodeBERT models may have focused on token-level differences (e.g., URLEncoder vs. null checks, OutputStreamWriter vs. PrintStream) and missed the high-level similarity of the HTTP POST pattern. The model might have been misled by the different method names, return types, and exception handling, resulting in a false negative.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considers them clones because both implement the same core functionality: sending HTTP POST requests and reading responses. The differences are in specific details like response handling and error management, but the underlying algorithm and structure are similar, fitting a broad Type-3/Type-4 clone classification.
- 共享行为: Both perform HTTP POST requests using URLConnection；Both set doOutput to true and write data to the output stream；Both read the response from the input stream
- 行为差异: Function A is specialized for LOLA login; B is generic with configurable parameters；A extracts and returns a session ID; B discards all response data；A handles exceptions locally and returns empty string on failure; B throws exceptions；A uses OutputStreamWriter; B uses PrintStream
- 修正建议: Improve training with examples that share partial functionality but differ in specific details；Use data-flow and control-flow analysis to recognize common I/O patterns；Incorporate method-level context (e.g., overall purpose) rather than only token-level features

### case_id=3462 FP lexical_or_api_overlap

- 方法: `getUser` vs `wordFrequency`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Retrieves a User by login from a DAO, falling back to parsing a config file if not found, and saves new user to DAO.
- B 摘要: Fetches a web page by replacing a placeholder in a URL, reads lines, and returns the frequency of a word using regex pattern matching.
- 静态失败原因: The static model likely over-weighted common API tokens like 'URL', 'BufferedReader', 'InputStreamReader', and 'e.printStackTrace()', leading to a high similarity score despite the lack of semantic alignment.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the two functions have entirely different purposes (user authentication vs word frequency), and BCB focuses on functional similarity rather than superficial API usage patterns.
- 共享行为: Both use URL and BufferedReader to read from a data source.；Both catch exceptions and print stack traces.；Both return a value (User or int) after processing input.
- 行为差异: Function A handles user authentication and persistence; Function B performs word frequency lookup from a web service.；Function A reads from a local config file or DAO; Function B reads from a dynamically constructed URL.；Function A uses StringTokenizer for parsing; Function B uses regex pattern matching.；Return types and semantics are completely unrelated (User vs int).
- 修正建议: Incorporate data flow or control flow analysis to differentiate semantically distinct operations.；Train with more negative examples that share API tokens but differ in task.；Use a model that captures the overall purpose, e.g., by considering method names and documentation.

### case_id=3463 FN partial_functionality

- 方法: `main` vs `WebmillDeploy`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a URL and extracts its contents to files.
- B 摘要: Processes a WAR file for Webmill deployment, reading and transforming XML, and creating a new WAR.
- 静态失败原因: Static models rely on token overlap and structural patterns; these functions have low Jaccard similarity (0.14), different APIs (ZipInputStream vs JarFile), and different control flow, leading to correct non-clone prediction. The BCB label itself may be questionable.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider them clones due to the shared boilerplate pattern of iterating over archive entries and copying data, even though the overall functionality is different. This is a broad Type-4 clone.
- 共享行为: Iterate over entries in an archive (ZIP/JAR)；Read each entry's data from an input stream；Write data to an output stream
- 行为差异: A extracts to files; B writes to a new JAR output stream；A does simple byte copying; B includes XML parsing and conditional logic；A uses URL and ZipInputStream; B uses JarFile and JarOutputStream；B has error handling and resource cleanup; A does not
- 修正建议: Use a model that captures intent or goal, not just structural similarity；Incorporate data flow analysis to distinguish extraction from transformation；Consider domain-specific knowledge (deployment vs. simple extraction)

### case_id=3464 FN partial_functionality

- 方法: `getFile` vs `copyResourceToFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, optionally modifies XML content, and saves to a temporary file.
- B 摘要: Copies a resource file from the classpath to a destination file using stream copying.
- 静态失败原因: Static BERT methods rely on token-level similarities and the token Jaccard is very low (0.083), so the model saw little lexical overlap and predicted non-clone, missing the underlying common purpose.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely labels this as a clone because both methods perform the high-level task of 'copying data from a source to a file,' which fits Type-4 functional similarity where structure differs but purpose aligns.
- 共享行为: Both involve reading from an input source and writing to an output file.；Both handle I/O streams and close them.；Both are utility methods for file operations.
- 行为差异: A downloads from a URL; B reads from a classpath resource.；A may modify XML content; B does not.；A handles multiple exception types; B only IOException.；A creates files conditionally; B always overwrites.
- 修正建议: Use a model that learns functional semantics beyond lexical tokens (e.g., graph-based or contrastive learning).；Augment training data with more Type-4 clone examples that have low lexical overlap.；Incorporate data flow or control flow information to capture shared I/O patterns.

### case_id=3465 FN partial_functionality

- 方法: `fetchURLData` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches data from a URL with optional proxy, handling file and HTTP protocols, and returns the content as a byte array.
- B 摘要: Launches a NexOpen project configuration by validating project structure, processing pom.xml files, setting properties, and scheduling an install action.
- 静态失败原因: Static BERT/GraphCodeBERT likely failed due to low lexical overlap (token Jaccard 0.0866) and different domain contexts (network vs Eclipse plugin). The model may have focused on syntactic similarity and missed any deep semantic connection.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label as clone because both functions involve reading input streams, copying to ByteArrayOutputStream, and managing resources, which might be considered a common pattern under Type-4 (semantically similar but syntactically different). However, the overall task is vastly different.
- 共享行为: Both use java.io.ByteArrayOutputStream to accumulate data；Both use org.apache.commons.io.IOUtils.copy to copy streams；Both handle exceptions and close resources
- 行为差异: A's purpose is network data retrieval, B's is project launch and configuration；A deals with HTTP connections and proxies, B deals with Eclipse workspace projects and XML parsing；A returns byte array of fetched data, B returns void and modifies project state
- 修正建议: Improve model's ability to recognize high-level functional similarity beyond lexical overlap；Incorporate structural information like control flow and data flow to detect shared I/O patterns；Augment training with examples of Type-4 clones that have low lexical similarity

### case_id=3466 FP boilerplate_overlap

- 方法: `populateResources` vs `readUNI`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Loads predefined templates and images from resources and saves them to database.
- B 摘要: Reads tab-separated data from a URL and populates a list of descriptions.
- 静态失败原因: Static models may over-rely on lexical overlap (e.g., URL, InputStream, MalformedURLException) and ignore the distinct control flows and data manipulations.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels as non-clone because the functions have completely different purposes and data handling, despite shared low-level URI reading boilerplate.
- 共享行为: Both open a URL stream and read line-oriented data.；Both handle MalformedURLException.
- 行为差异: A saves resources to database; B adds strings to a vector.；A deals with XML/txt templates and images; B reads tab-separated UNI data.；A uses BufferedReader; B uses Scanner.；A does not close streams; B closes in finally.
- 修正建议: Incorporate data flow analysis to distinguish resource saving vs. list population.；Use larger context windows or abstract syntax trees to capture high-level intent.

### case_id=3467 FP lexical_or_api_overlap

- 方法: `getRequestContent` vs `callApiPost`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Gets a single line from a URL using HTTP GET.
- B 摘要: Makes an HTTP POST request with parameters, checks response code, and returns an InputStream.
- 静态失败原因: Static BERT/GraphCodeBERT may have focused on the lexical overlap of URL, HttpURLConnection, getInputStream, etc., and missed the semantic differences due to the different HTTP methods and data flow. The model might have been misled by the common pattern of opening a connection and reading input, ignoring the distinct parameters and control flow.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB may label this as non-clone because the functions have different method signatures, different HTTP methods, and different return types, indicating distinct functional purposes. The overlap in HTTP connection boilerplate is not sufficient to consider them clones under BCB's guidelines for functional similarity.
- 共享行为: Both use java.net.URL and HttpURLConnection to make HTTP requests.；Both connect to a URL and handle input streams.
- 行为差异: A uses GET method; B uses POST method.；A returns a single line (String); B returns an InputStream.；A has no error handling; B has error handling and checks response code.；A does not send request body; B sends parameters as POST body.
- 修正建议: Train with more diverse examples of HTTP request patterns to differentiate GET vs POST.；Incorporate data flow analysis to track how parameters are passed and used.；Add features that consider method signatures and return types.

### case_id=3468 FP lexical_or_api_overlap

- 方法: `doVersionCheck` vs `readTwitterFead`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Checks for new version of jEdit by fetching and parsing a version file from a URL, updating UI cursor.
- B 摘要: Fetches Twitter user timeline JSON via HTTP GET and returns the response as a string.
- 静态失败原因: Static BERT models likely overemphasized lexical and API-level overlaps (e.g., both use URL, InputStream, BufferedReader, while loop readLine) and control flow similarity, missing the semantic difference in overall functionality and return type.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels these as non-clones because they have different purposes (version check vs. Twitter feed), different I/O patterns, and different output types (void vs. String). The structural overlap is not enough to be considered a clone under BCB guidelines, which require more significant similarity in functionality.
- 共享行为: Both open a URL/HTTP connection；Both read input line by line using BufferedReader；Both handle IOException
- 行为差异: A updates UI (wait cursor) and calls another method; B returns a string；A parses specific version tags; B appends all lines to StringBuilder；A uses URL.openStream; B uses Apache HttpClient；A's error handling shows a GUI error; B logs and prints stack trace
- 修正建议: Incorporate method name and return type into input representation；Use contrastive learning on semantically different pairs with high API overlap；Add functional role labeling (e.g., reading vs. writing, UI interaction) as features

### case_id=3469 FN boilerplate_overlap

- 方法: `readIntoList` vs `postRequest`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads HTML from a URL, parses anchor tags to create JMenuItems, and populates a given map with them.
- B 摘要: Sends an HTTP POST request with parameters from a HashMap, reads the response, and returns it as a string.
- 静态失败原因: Static BERT/GraphCodeBERT models may have been misled by the common I/O and exception handling boilerplate, failing to capture the distinct semantic purposes (parsing HTML vs. sending POST data).
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may consider these as clone due to their shared structure of opening a URL, reading lines, and exception handling, which fits broad Type-3/Type-4 clone criteria focusing on partial functionality similarity.
- 共享行为: Both open a URL connection and read input line by line using BufferedReader；Both handle exceptions by printing stack traces；Both use PrintWriter (or similar) for output
- 行为差异: readIntoList parses HTML for anchor tags and creates GUI menu items; postRequest sends data and returns the response；readIntoList uses InputStream only; postRequest uses OutputStream for sending data；readIntoList populates a Map<String, JMenuItem>; postRequest returns a String
- 修正建议: Enhance training data with diverse examples that distinguish between different web tasks；Incorporate dataflow analysis to capture the transformation of input/output data；Use contrastive learning to emphasize functional purpose over structural similarity

### case_id=3470 FN benchmark_preference_bias

- 方法: `doGet` vs `write`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Handles HTTP GET request to retrieve and serve a web page after permission checks, with logging and caching.
- B 摘要: Writes a JAR file by copying entries from specified JARs, optionally expanding dependencies.
- 静态失败原因: The static model correctly identified low token overlap and different overall structure, predicting non-clone; it 'failed' only relative to the BCB label, which likely reflects an excessively broad annotation.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might label this as clone under a very broad interpretation of 'writing output' since both write to an output stream (HTTP response vs JAR), but this is not functionally equivalent even at Type-4 level.
- 共享行为: Both perform I/O operations using output streams；Both involve conditional checks before executing actions
- 行为差异: Function A is a servlet method processing HTTP requests and rendering HTML; Function B is a utility method for JAR file creation；Function A involves page lookup, permission checks, and caching; Function B involves iterating over JAR entries and copying
- 修正建议: Re-evaluate the ground truth label for this pair to ensure consistency with clone definitions；Provide clearer annotation guidelines to avoid overly broad functional equivalence

### case_id=3471 FN benchmark_preference_bias

- 方法: `copy` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.75`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Recursively copies a file or directory using NIO file channels and memory-mapped buffers.
- B 摘要: Launches a NexOpen project build configuration, processing XML files, setting Hibernate properties, and triggering an install action.
- 静态失败原因: The static BERT/GraphCodeBERT model likely misclassified this as a non-clone because of low token overlap (Jaccard 0.084) and different structures. However, if it had been a false positive, it might have seen common exception handling or I/O APIs. But here it is a false negative (model predicted 0, BCB says 1), meaning the model failed to see the similarity BCB annotators perceived. The similarity is likely only at a very abstract level (both do file operations), which is not captured by token-level or structural matching.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB typically labels Type-3/4 clones only if there is significant structural or behavioral overlap. Here, the only commonality is file I/O, which is too broad for a clone annotation in BCB's standard practice.
- 共享行为: Both involve file I/O operations；Both handle exceptions (IOException, CoreException)
- 行为差异: Function A is a generic file copy utility; Function B is a specific Eclipse launch configuration handler；Function A has no external dependencies; Function B relies on Eclipse, Hibernate, and NexOpen libraries；Function A's output is a copied file; Function B modifies project configuration and triggers a build
- 修正建议: Increase sensitivity to high-level I/O patterns；Add training examples of broad Type-4 clones that share only file/resource handling purpose；Incorporate human annotation guidelines that accept abstract behavioral similarity

### case_id=3472 FP partial_functionality

- 方法: `readTwitterFead` vs `issueCommandToServer`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.85`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a Twitter feed from a fixed URL using HTTP GET.
- B 摘要: Sends a command and capsule to a server using HTTP POST and reads the response.
- 静态失败原因: Static BERT models may overgeneralize based on shared structural patterns and keywords (e.g., BufferedReader, while loop, StringBuilder), ignoring differences in HTTP client types, method signatures, and parameter handling.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely labeled non-clone because the functions serve different purposes (Twitter feed retrieval vs server command) and have significant implementation differences in HTTP method, parameters, and error handling, despite sharing a common pattern of reading network responses.
- 共享行为: Both perform an HTTP request and read the response body line by line into a string builder.
- 行为差异: HTTP method: A uses GET, B uses POST.；URL and parameters: A has a fixed URL, B uses dynamic command and capsule parameters.；HTTP client: A uses HttpClient, B uses URLConnection.；Error handling: A catches exceptions internally and logs, B propagates IOException.
- 修正建议: Incorporate data flow analysis to distinguish parameterized requests from fixed ones.；Use type-aware analysis to differentiate HttpClient from URLConnection.；Consider control flow and exception handling differences.

### case_id=3473 FP lexical_or_api_overlap

- 方法: `main` vs `writeData`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Parses a Prolog file and generates adapter classes and writes them to a JAR file.
- B 摘要: Writes time-stamped peak data to a text file with a specific format.
- 静态失败原因: Static BERT/GraphCodeBERT models may have been misled by lexical similarities such as common API calls (e.g., File, PrintWriter, file operations) and similar structural patterns (loops, conditionals), but failed to capture the deep semantic differences in the overall task.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled this as not clones because the functions have entirely different purposes and semantics, even though both involve file I/O.
- 行为差异: Function A is a complex main method that orchestrates multiple steps including parsing, code generation, and file writing; Function B is a straightforward data writing method.；Function A handles error conditions and uses multiple classes; Function B has a simple loop structure.；Function A writes binary (JAR) and serialized objects; Function B writes text (tab-separated).
- 修正建议: Improve training data to include more diverse non-clone pairs with API overlap.；Incorporate control flow and data flow analysis to capture program semantics.

### case_id=3474 FP lexical_or_api_overlap

- 方法: `doVersionCheck` vs `importSequences`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Checks for software version updates by reading a version file from a URL.
- B 摘要: Imports biological sequences from a URL by reading a FASTA-like file.
- 静态失败原因: Static BERT/GraphCodeBERT models may rely heavily on lexical and API-level similarities, such as URL.openStream, IOException handling, and while loops, leading to false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels clones as 0 (non-clone) when the functions have different domain-specific purposes, even if there is some structural similarity. Here, version checking and sequence importing are unrelated tasks.
- 共享行为: both open an InputStream from a URL；both read line by line using a reader；both handle IOException
- 行为差异: function A checks version strings and calls another version check method; function B parses sequence data and stores names and sequences；function A uses BufferedReader, function B uses custom ImportHelper；function A's parsing is simple (startsWith), function B's parsing is more complex (tokenizer and sequence reading)
- 修正建议: Include task-specific context or domain knowledge in the embedding；Use dataflow or dependence graphs to distinguish different processing logic；Train with more functionally diverse negative examples

### case_id=3475 FN partial_functionality

- 方法: `testNetworkHTTP` vs `runInternal`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: A test method that makes several HTTP GET requests to fixed URLs, reads and discards the response lines, and disconnects.
- B 摘要: A method that downloads OPDS catalog or book content via HTTP, handling pagination, progress, errors, and disconnects.
- 静态失败原因: Static models rely heavily on token overlap and structure, which is low (Jaccard 0.09) due to different lengths and complexity; they miss the higher-level functional similarity of making HTTP requests, leading to a false negative.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels Type-3/Type-4 clones for functions that share the same core task (HTTP GET requests) despite differences in implementation details; both methods perform network I/O using HttpURLConnection, which is a common clone pattern.
- 共享行为: Both open HttpURLConnection to URLs and read input streams.；Both disconnect the connection in a finally block.；Both handle exceptions (IOException or Exception) with logging.
- 行为差异: Function A is a simple test that discards all read data; Function B processes data and has complex control flow.；Function A performs multiple fixed URL requests sequentially; Function B dynamically loads pages based on content and pagination.；Function B includes progress indicators, callbacks, content-type detection, and user-facing error messages; Function A only prints stack trace.
- 修正建议: Incorporate API call sequence matching to identify common patterns like HTTP GET operations.；Use semantic embeddings that capture intent (e.g., 'download from URL') rather than exact code.；Apply structural abstraction to normalize loops and error handling.；Consider partial functionality clones where one function is a simpler version of another.

### case_id=3476 FN partial_functionality

- 方法: `getDatasetsList` vs `read`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Retrieves a list of dataset names from a given URL with caching and synchronization.
- B 摘要: Opens a file or URL stream and reads its content via another method, returning a status code.
- 静态失败原因: The static model correctly identified low token overlap and distinct control flow/return types, so it did not 'fail' but disagreed with the BCB annotation; the divergence stems from BCB's broad Type-4 interpretation.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled as clone due to the common presence of opening a URL stream and IOException handling, overlooking the different return types and overall purpose (retrieving a list vs reading arbitrary data).
- 共享行为: Both open a URL stream using URL.openStream()；Both handle IOException with logging or error status
- 行为差异: Return type: List<String> vs int；Function A caches results in a HashMap; B has no cache；A reads lines with BufferedReader; B uses BufferedInputStream and delegates to another read method；A throws RuntimeException on IOException; B sets a status field and returns it
- 修正建议: Include additional context from the enclosing class to infer overall module semantics；Use a graph-based model that captures API call sequences rather than just lexical tokens

### case_id=3477 FP partial_functionality

- 方法: `getTicketsForQueue` vs `getXML`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Retrieves open tickets for a given queue by querying the RT REST API, parsing ticket IDs, and fetching each ticket.
- B 摘要: Fetches an XML string from a given servlet URL by reading the entire response line by line.
- 静态失败原因: The static model likely overemphasized the lexical and structural similarities in the HTTP reading sequence (BufferedReader, while loop, reading lines) and missed the semantic differences in the post-processing logic and overall purpose. The token Jaccard is low, but the model may have been misled by common API words like 'BufferedReader' and 'readLine'.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely labels this non-clone because the core functionality differs: A is specific to ticket retrieval, B is generic XML retrieval. The shared HTTP reading code is common boilerplate and not sufficient for clone detection in BCB's functional granularity.
- 共享行为: Both make HTTP GET requests；Both read response line by line using BufferedReader；Both return null on certain error conditions
- 行为差异: Function A parses specific ticket ID patterns from the response and fetches additional data; B returns raw response text；Function A uses Apache HttpClient with parameter building; B uses java.net.URL；Function A has complex error handling and logging; B has simple exception catches；Function A's purpose is to retrieve tickets for a queue; B's purpose is to get generic XML
- 修正建议: Improve training data to include more discriminative features beyond boilerplate patterns；Use attention mechanisms to focus on the core logic rather than I/O setup；Incorporate structural information or method call sequences to differentiate functionality

### case_id=3478 FP lexical_or_api_overlap

- 方法: `getRequestContent` vs `getTicketsForQueue`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Opens an HTTP connection from a URL and reads a single line from the response.
- B 摘要: Queries a REST API for open tickets in a queue, parses ticket IDs from the response, fetches each ticket, and returns a list of tickets.
- 静态失败原因: The model likely focused on lexical and API-level similarities (both use URL/HTTP, BufferedReader) while ignoring the significant differences in purpose, complexity, and control flow, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB annotates these as non-clones because they perform completely different tasks; despite both using HTTP, the functionality and output differ fundamentally.
- 共享行为: Both use HTTP to communicate with a server；Both read lines from a BufferedReader
- 行为差异: A returns a single string line; B returns a list of RTTicket objects；A has no query parameters or filtering; B builds a query string and parses structured data；A has minimal error handling; B has extensive exception handling and logging；A is a simple utility; B is a complex business logic method
- 修正建议: Incorporate graph-based representations to model data flow and control dependencies；Use contrastive learning with hard negative pairs that share API calls but differ in functionality；Enhance models with long-range contextual awareness to differentiate simple from complex uses

### case_id=3479 FP lexical_or_api_overlap

- 方法: `getRequestContent` vs `getNetworkServersIPs`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.98`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Opens a URL connection, reads the first line of content, and returns it as a string.
- B 摘要: Opens a URL connection, reads lines, parses the '!SERVERS' section to extract IP addresses, and returns them as a vector.
- 静态失败原因: Static BERT models may over-rely on lexical and API surface overlap (e.g., URL, URLConnection, BufferedReader, readLine) without capturing the distinct control flow and data processing logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels based on whole-function semantic equivalence; these functions perform different transformations on the data, so they are not clones.
- 共享行为: Both open a URL connection and read lines from an InputStream using a BufferedReader.
- 行为差异: Function A returns only the first line; Function B iterates over all lines and parses specific patterns.；Function A returns a single String; Function B returns a Vector<String> of parsed IPs.；Function B includes error handling for MalformedURLException and IOException; Function A throws Exception.
- 修正建议: Enhance model to better distinguish between similar API usage with different control flows and output types.；Incorporate data-flow analysis or structure-aware attention to differentiate reading vs. parsing patterns.

### case_id=3480 FP partial_functionality

- 方法: `readData` vs `processAddByURLSubmit`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Reads and parses a configuration file to initialize character sets and mappings for Tibetan/Sanskrit processing.
- B 摘要: Processes a submitted DOAP URL by reading its content and handling errors.
- 静态失败原因: The model likely overfitted on common I/O patterns (try-catch, InputStream) and neglected the overall semantic context and domain-specific logic, leading to a false positive.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely labeled non-clone because the methods are from entirely different application domains and perform distinct tasks despite superficial I/O similarities.
- 共享行为: Both perform I/O operations (file reading vs URL stream reading)；Both have try-catch blocks for IOException
- 行为差异: A parses static configuration data; B processes user-submitted web content；A populates multiple data structures (sets, maps); B writes to a StringWriter and calls processSubmittedDoap；A has complex tokenization and state machine; B is a simple fetch-and-process flow；Error handling differs: A throws Errors, B logs and sets error page
- 修正建议: Enhance training with more diverse I/O patterns to avoid superficial boilerplate matching；Incorporate method-level semantic embedding that captures intent beyond syntax；Use cross-file or cross-project context to recognize domain differences

### case_id=3481 FN partial_functionality

- 方法: `copyResource` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource from a URL or existing file to a destination file using byte-by-byte streaming.
- B 摘要: Decompresses a .gz file to a destination file using buffered streaming with error handling and proper stream closure.
- 静态失败原因: Static BERT models relied on lexical and syntactic features (method name, arguments, error handling, GZIPInputStream) and low token Jaccard, failing to capture the underlying semantic similarity of the stream-copying pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often considers functions that perform stream copying as clones regardless of source format or error handling, focusing on the core semantic similarity of copying data from an input to an output stream.
- 共享行为: Open an input stream and an output stream；Read bytes from input and write to output in a loop；Close both streams after copying
- 行为差异: Source type: A handles URL or file; B only file with .gz decompression；Reading method: A reads byte-by-byte; B reads in buffered chunks；Error handling: A throws Exception; B catches IOException and prints error；Output destination: A uses a method; B uses command-line argument
- 修正建议: Incorporate structural patterns like 'while loop reading from input and writing to output' as clone features.；Use dataflow analysis to identify equivalence of stream copy operations across disparate APIs.；Relax sensitivity to error handling and source type differences when detecting stream copy clones.

### case_id=3482 FP lexical_or_api_overlap

- 方法: `main` vs `copy`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: AdapterGenerator main method that reads a Prolog file, parses it, generates adapter JAR with classes and serialized data.
- B 摘要: Recursively copies a file or directory using FileChannel and MappedByteBuffer for efficient I/O.
- 静态失败原因: Static model likely focused on overlapping tokens like File, IOException, and exception handling, missing the distinct high-level purposes.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB considers these non-clones because they share no meaningful functionality beyond basic file handling; the overall task and logic are entirely different.
- 共享行为: Both use file I/O operations (File, FileInputStream, FileOutputStream, IOException)；Both are static methods；Both handle exceptions
- 行为差异: Function A is a complex multi-step program generator; Function B is a simple recursive file copy；Function A reads and writes structured data (Prolog, JAR, serialized objects); Function B copies raw bytes；Function A uses many external classes (Parser, FactVisitor, etc.); Function B uses only standard Java I/O
- 修正建议: Add more negative examples with similar API usage but different semantics；Incorporate program dependency graphs to capture control and data flow differences；Use fine-tuning with contrastive learning on clone benchmarks

### case_id=3483 FP boilerplate_overlap

- 方法: `downloadURLtoString` vs `getFullScreenUrl`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Downloads the entire content of a URL as a string.
- B 摘要: Extracts video parameters from a YouTube page and constructs a fullscreen URL.
- 静态失败原因: Static BERT models likely over-relied on the common code pattern of opening a URL and reading lines, disregarding the different post-processing and functionality. The lexical overlap of API calls (BufferedReader, InputStreamReader, readLine) dominated the embedding.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels as non-clone because the functions have entirely different purposes and outputs, despite sharing the URL reading boilerplate. The similarity is superficial and does not indicate functional equivalence or even partial functionality overlap.
- 共享行为: Both read from a URL using BufferedReader and InputStreamReader.；Both use a while loop with readLine() to read lines.
- 行为差异: A returns all concatenated content; B parses specific fields and constructs a new URL.；A takes a URL parameter; B uses a class field ytUrl.；B includes GUI progress updates (progressDown) and extensive logging.；B only processes lines containing 'fullscreenUrl', while A processes all lines.
- 修正建议: Incorporate dataflow analysis to distinguish between simple content download and conditional extraction.；Use method-level context (e.g., method name, surrounding class) to differentiate generic utilities from domain-specific logic.；Augment training data with more examples of non-clone pairs that share boilerplate but differ in semantics.

### case_id=3484 FN benchmark_preference_bias

- 方法: `copy` vs `getFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Copies a file or directory from a Hadoop FileSystem to a local destination, recursively copying subdirectories and optionally deleting the source.
- B 摘要: Downloads a WSDL file from a URL, modifies the wsdlsoap:address endpoint attribute, and returns the local file path, handling various exceptions.
- 静态失败原因: Static BERT correctly predicted non-clone because it captured the lack of semantic similarity; the low token Jaccard (0.1469) indicates little lexical overlap.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled as clone due to both functions performing file I/O operations and being static utility methods, but this is a very broad and likely erroneous interpretation.
- 共享行为: Both use File, InputStream, and OutputStream for file I/O.；Both involve reading from a source and writing to a destination.
- 行为差异: Function A copies from a distributed filesystem to local; function B downloads from a URL.；Function A operates on directories and files; function B modifies XML content.；Function A has optional deletion of source; function B handles temporary files and renaming.；Error handling differs: function A throws IOException; function B wraps multiple exceptions into AxisFault.
- 修正建议: Re-examine BCB annotation for potential mislabel.；Use more discriminative features beyond file I/O presence.；Consider adding negative sampling with similar token patterns but different semantics.

### case_id=3485 FP lexical_or_api_overlap

- 方法: `sendPost` vs `doVersionCheck`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.98`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Sends an HTTP POST request to a given URL with a parameter string and returns the response body.
- B 摘要: Reads a version-check URL from jEdit properties, parses lines for build numbers, and triggers a version check if both devel and stable builds are found.
- 静态失败原因: The static BERT/GraphCodeBERT model likely overemphasized the overlapping API usage (URL, BufferedReader, InputStream) and the structural pattern of try-catch with while readLine loop. It may have also been misled by the presence of similar variable names like 'line', 'in', etc., and ignored the overall purpose and different data flow (POST vs GET, parameter writing vs parsing).
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled this as non-clone because the methods have completely different purposes: one is a generic HTTP POST function, the other is a specific version-check function. BCB's annotation preference typically considers functional similarity, and here the only similarity is using standard Java I/O classes, which is too superficial.
- 共享行为: Both use URL, InputStream, BufferedReader to read from a network resource.；Both handle exceptions (one catches Exception and shows message, the other catches IOException and shows error dialog).
- 行为差异: A performs HTTP POST by setting output mode and writing parameters; B performs HTTP GET by opening a stream directly.；A returns the concatenated response body; B does not return a value (void) and instead calls another method.；A uses 'MsgPrint.showMsg' for error; B uses 'GUIUtilities.error' and hides/shows wait cursor.；B parses specific lines for version information; A does not parse content.
- 修正建议: Improve training data with more diverse non-clone pairs that share API usage but differ in intent.；Incorporate data flow analysis to distinguish between writing to output stream (POST) vs reading from input stream (GET).；Add features that capture method-level semantics like return type, parameter types, and method name context.

### case_id=3486 FP lexical_or_api_overlap

- 方法: `writeConfiguration` vs `main`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Writes configuration resource to a Writer, handling resource absence.
- B 摘要: Main method for adapter generation from Prolog files, involving parsing, class loading, and file writing.
- 静态失败原因: The model may have been misled by shared API calls (e.g., IOUtils.copy, FileUtils.readFileToString, url.openStream) and common boilerplate (try-finally, IOException), leading to a false positive despite different semantics.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clone because the functions have distinct purposes and structures; token similarity is extremely low, and they are not semantically related.
- 共享行为: Both involve I/O operations (reading/writing files/streams)；Both use try-catch for exception handling
- 行为差异: Entirely different functionalities: configuration output vs. adapter generation；Different inputs: Writer vs. command-line arguments；Different output types: configuration text vs. jar file with generated classes
- 修正建议: Enhance training with more negative examples of dissimilar functions that share low-level API calls；Incorporate method-level context or structural embeddings to capture overall semantics；Use attention mechanisms that focus on method signatures and control flow

### case_id=3487 FN partial_functionality

- 方法: `modifyApplicationMessage` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Modify a property in a locale-specific properties file by reading, parsing, and writing lines.
- B 摘要: Copy a file from source to destination using a byte buffer with optional force overwrite.
- 静态失败原因: Low token Jaccard (0.23), different method names, and distinct control flows caused the model to overlook the common file I/O sub-task.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider the file copy subtask in A as a partial functionality match with B, accepting broad Type-3/Type-4 similarity due to shared I/O pattern.
- 共享行为: Both functions read from an input source and write to an output destination using file I/O.；Both close input and output streams in a safe manner.
- 行为差异: Function A manipulates properties file content (key-value pairs), while Function B only copies raw bytes.；Function A conditionally copies a file only if it doesn't exist, while Function B always copies.；Function A uses character-based I/O (FileReader/Writer), while Function B uses byte-based I/O with a buffer.；Function A parses lines, searches for a key, and modifies or appends values; Function B has no such logic.
- 修正建议: Enhance model to recognize subtask composition and shared I/O patterns.；Incorporate dataflow analysis to detect read-write chains irrespective of surrounding logic.

### case_id=3488 FN benchmark_preference_bias

- 方法: `main` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: A test method that writes 256 bytes to a file and reads them back using StraightStreamReader to verify correct read operations.
- B 摘要: An Eclipse plugin launch method that processes a NexOpen project's pom.xml files, configures Hibernate properties, and schedules an install action.
- 静态失败原因: Static BERT correctly identified non-clone because token overlap is very low (Jaccard 0.072) and the functional contexts are entirely different; the model did not fail.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have incorrectly labeled this pair as clone due to superficial lexical similarities (both have loops, try-catch, file existence checks) or a potential annotation error.
- 共享行为: Both methods perform file I/O operations and handle exceptions with try-catch blocks.
- 行为差异: Function A is a unit test for a stream reader; Function B is a launch configuration handler for a specific IDE framework.；Function A reads and writes raw bytes; Function B manipulates XML files, properties, and project resources.；Function A has no project or plugin context; Function B is deeply integrated with Eclipse and Maven.；The control flow and data structures are completely different.
- 修正建议: Re-evaluate BCB annotation for this pair; consider removing or correcting label.；Improve static model to handle such cases, but it already does correctly.

### case_id=3489 FN benchmark_preference_bias

- 方法: `invoke` vs `doVersionCheck`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Generic HTTP RPC invocation with retry on timeout and JSON deserialization.
- B 摘要: Version check utility that reads a URL and parses build numbers from a text file.
- 静态失败原因: Static BERT likely considered the low token overlap (0.14) and different method names, correctly identifying they are not clones; thus it did not fail but the BCB annotation is questionable.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled them clones due to superficial structural similarity (both perform HTTP-like reads and error handling), overlooking the distinct application domains and overall functionality.
- 共享行为: Both open a connection to a URL and read lines from an input stream.；Both use BufferedReader and InputStreamReader for reading.；Both handle exceptions (ConnectTimeoutException vs IOException).
- 行为差异: A is generic and part of a service framework; B is a static utility for version checking.；A includes retry logic; B does not retry.；A deserializes JSON; B parses specific line prefixes.；B shows a wait cursor and error dialogs; A does not have UI interaction.
- 修正建议: Re-evaluate BCB annotation for this pair; consider if broad Type-4 similarity is justified.；Improve static model by incorporating functional semantics beyond token overlap.

### case_id=3490 FN partial_functionality

- 方法: `writeFileType` vs `fileDownload`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads URIs from an input file, fetches each URI's content, classifies it by semantic patterns (OWL, RDFS, RDF), and writes the URI with its classification to an output file.
- B 摘要: Downloads a file from a given URL and saves it to a local directory as 'download.pdf'.
- 静态失败原因: Low token overlap (0.20) and different method names caused the model to focus on lexical differences rather than the shared I/O pattern. Static models may miss structural similarity when token n-grams are dissimilar.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considers them clones due to the shared high-level structure of reading from a URL connection and writing to a file, common in network I/O utilities, even though the detailed business logic differs.
- 共享行为: Establish URL connection and open input stream；Read data from the input stream；Write data to an output file
- 行为差异: A reads multiple URIs sequentially; B handles a single URL；A classifies content based on RDF/OWL patterns; B does no classification；A outputs a tab-separated classification line per URI; B outputs raw file content；A has error handling for broken URIs; B does not
- 修正建议: Enrich training data with more examples of partial functional similarity；Use graph-based code representations to capture data flow patterns；Incorporate contrastive loss to learn common I/O structures

### case_id=3491 FP lexical_or_api_overlap

- 方法: `main` vs `doRequest`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.98`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: A main method that generates adapter classes from a Prolog file, writing them to a JAR and handling errors.
- B 摘要: A method that handles an HTTP request by serving a static resource from a web context, returning the content.
- 静态失败原因: The static BERT model may have been misled by overlapping vocabulary (e.g., 'File', 'InputStream', 'OutputStream', 'IOException') and common programming patterns like try-catch, leading to a false positive due to lexical and API-level similarities.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB annotators would likely mark as non-clone because the functions have completely different purposes and functionality, despite some superficial similarities in error handling and I/O usage.
- 共享行为: Both perform I/O operations and handle exceptions
- 行为差异: Function A is a command-line entry point for code generation；Function B is a servlet request handler for serving static resources；Different inputs: command-line arguments vs HTTP request/response objects；Different outputs: generated JAR file vs HTTP response stream
- 修正建议: Incorporate data flow or control flow analysis to distinguish high-level intent；Use models with better long-range semantic understanding；Add training examples with diverse tasks to reduce reliance on API token overlap

### case_id=3492 FP lexical_or_api_overlap

- 方法: `load` vs `getFullScreenUrl`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `1.0`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Downloads content from Pastebin given an ID and returns the concatenated XML string.
- B 摘要: Extracts video_id and t parameters from a YouTube page to construct a fullscreen video URL.
- 静态失败原因: The model likely relied on high structural similarity (both use URL, URLConnection, BufferedReader, while loop reading lines) and overlooked the distinct purposes and parsing logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically requires substantial functional similarity beyond common I/O patterns; here the purposes differ significantly, so BCB correctly labels as non-clone.
- 共享行为: Both open a URL connection and read line by line using BufferedReader.
- 行为差异: Different URL sources (pastebin vs youtube)；Different parsing logic (simple concatenation vs extraction of specific parameters)；Different return values (raw XML vs constructed full URL)；Different error handling (JOptionPane vs System.err)
- 修正建议: Incorporate more data flow analysis to distinguish different end goals；Use finer-grained tokenization to capture domain-specific terms like 'pastebin' vs 'youtube'

### case_id=3493 FN boilerplate_overlap

- 方法: `addIDs` vs `seeURLConnection`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.85`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Parses HTML from the Golm Metabolome Database to extract molecular weight and various database IDs, setting them on a PeakListRow.
- B 摘要: Opens a URL connection to a hardcoded URL and logs the entire response as a string.
- 静态失败原因: Static BERT/GraphCodeBERT likely failed because the token Jaccard similarity is low (0.102) and the code structures are very different. The model may have focused on the overall token-level disparity and missed the abstract commonality of the I/O pattern, which BCB considered sufficient for a clone.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may label this as a clone due to the shared boilerplate pattern of opening a URL, creating a BufferedReader, and reading lines, which constitutes a common I/O idiom. Even though the overall functionality is different, BCB's broad criteria for Type-3/Type-4 clones sometimes accept such partial functional similarity.
- 共享行为: Both use URL, URLConnection, BufferedReader, InputStreamReader to fetch content from a URL.；Both use a while loop to read lines from the BufferedInputStream.
- 行为差异: addIDs dynamically constructs the URL based on input name; seeURLConnection uses a hardcoded URL.；addIDs parses the HTML response to extract specific fields and sets them on an object; seeURLConnection reads all lines without parsing.；addIDs returns an integer score; seeURLConnection returns void and logs the result.；addIDs has complex conditional logic for different types of IDs; seeURLConnection has no branching logic.
- 修正建议: Train the model with more examples of boilerplate I/O patterns to recognize them as shared behavior.；Incorporate data-flow or control-flow analysis that captures sequences of API calls (e.g., URL construction, openConnection, BufferedReader, readLine).；Use a graph-based representation that abstracts common library usage patterns.

### case_id=3494 FP lexical_or_api_overlap

- 方法: `getDatasetsList` vs `checkForUpgrade`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Retrieves a list of dataset names from a server URL with caching.
- B 摘要: Checks for software upgrades by querying a license server, updating a database, and updating UI elements.
- 静态失败原因: Static models like CodeBERT may over-rely on token overlap, including common API calls (URL, BufferedReader, InputStreamReader), leading to spurious similarity in embeddings.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB considers functional similarity; these functions are unrelated in purpose and behavior, so they are correctly labeled non-clones despite shared boilerplate I/O.
- 共享行为: Both open a URL connection and read lines using BufferedReader.
- 行为差异: A returns a cached list of dataset names; B performs upgrade logic with database queries, license validation, and UI manipulation.；A uses a simple list cache; B uses multiple database tables and UI components.；A's error handling wraps IOException into RuntimeException; B handles various error conditions with UI messages.；A's scope is limited to reading a single URL per dataset; B involves a complex loop over upgrade items and conditional visibility toggling.
- 修正建议: Incorporate control flow and data flow analysis to distinguish common library usage from actual semantic equivalence.；Use graph-based models that capture structural dependencies beyond token sequences.；Increase context beyond single methods (e.g., class-level info, imports) to disambiguate library classes.

### case_id=3495 FN partial_functionality

- 方法: `copyResource` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource (URL or local file) to a destination file using byte-by-byte stream I/O.
- B 摘要: Copies a file to another file using NIO FileChannel and transferTo.
- 静态失败原因: Static BERT models rely heavily on lexical overlap, which is very low (token Jaccard=0.13). The different API names ('InputStream' vs 'FileChannel') and control flow patterns cause the model to miss the high-level semantic similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB labels these as clones because they both perform the core task of copying a file, even though they use different APIs (streams vs. NIO) and have slight differences in error handling and source types. BCB often accepts broad Type-3/Type-4 similarity.
- 共享行为: Both copy data from a source to a destination file.；Both involve opening input and output streams/channels.；Both close resources after copying.
- 行为差异: Function A supports URL sources and throws Exception; Function B only handles File and catches IOException.；Function A uses byte-by-byte read/write; Function B uses transferTo for efficient copying.；Function A does not use NIO; Function B uses FileChannel.
- 修正建议: Use models that capture semantic similarity via code structure, e.g., graph-based or AST-based models.；Incorporate data flow analysis to identify equivalent input-output transformations.；Fine-tune on datasets with diverse API usage to learn functional equivalence.

### case_id=3496 FP lexical_or_api_overlap

- 方法: `PageLoader` vs `loadURL`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads entire web page content from a URL into a string without authentication.
- B 摘要: Downloads a URL's content to a temporary file with optional authentication and progress display.
- 静态失败原因: Static model may have focused on lexical overlap like 'BufferedReader', 'readLine', 'url.openStream'/'connection.getInputStream', and ignored differing control flows and side effects.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels as non-clone because the functions have different input/output requirements and side effects; they are not functionally equivalent or similar in high-level purpose.
- 共享行为: Both open a URL and create a BufferedReader from an InputStream
- 行为差异: B uses URLConnection with authentication, writes to file instead of storing in memory, updates status label, uses different read loop, adds newlines, handles file creation.
- 修正建议: Use data flow analysis to track output destinations；Incorporate structural features like number of method calls, control flow complexity；Train with contrastive examples that distinguish reading vs. writing

### case_id=3497 FP other

- 方法: `readData` vs `unzip`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Reads and parses string tokens from predefined constants to populate multiple sets and a hash map.
- B 摘要: Extracts a ZIP file to a directory, creating directories and writing file contents.
- 静态失败原因: Likely a false positive due to limited training data or model misinterpreting common Java boilerplate (e.g., loops, exception handling) as similar, despite low token overlap.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB annotated as non-clone because the two methods perform fundamentally different tasks with no algorithmic overlap.
- 共享行为: None; completely different functionality
- 行为差异: A processes string tokens; B processes zip entries；A builds in-memory data structures; B writes files to disk；A has no file I/O; B performs file I/O
- 修正建议: Improve negative sampling with more diverse non-clone pairs；Enhance model understanding of high-level semantics beyond structure

### case_id=3498 FP partial_functionality

- 方法: `readTwitterFead` vs `downloadModel`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a fixed Twitter timeline JSON from a hardcoded URL using HttpClient, logs errors, and returns the content as a string.
- B 摘要: Downloads an RDF model from a given URL using URLConnection, sets HTTP headers, and returns the parsed Model object, throwing RuntimeException on error.
- 静态失败原因: The static model likely relied on surface-level API calls (HttpGet, HttpClient, URLConnection) and control-flow patterns (try-catch, InputStream reading), which overlap, without capturing the deeper semantic differences in return type, purpose, and error handling philosophy.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB judges these as non-clones because they have different return types, different exception handling semantics, and serve distinct purposes (one is a simple text fetcher, the other is a RDF model downloader). The shared HTTP GET pattern is too generic to override their functional mismatch.
- 共享行为: Both perform an HTTP GET request to a URL.；Both read input stream content.；Both handle IOException and similar exceptions.
- 行为差异: Function A has a hardcoded URL; Function B takes a parameter.；Function A uses Apache HttpClient; Function B uses URLConnection/HttpURLConnection.；Function A returns a concatenated string; Function B returns a parsed RDF Model.；Function A logs errors and returns empty string; Function B wraps exceptions in RuntimeException.
- 修正建议: Incorporate return type and data usage into the representation (e.g., type-aware graph or dataflow).；Include semantic roles of identifiers (e.g., 'twitter', 'model', 'rdf') to distinguish domain-specific functionality.；Use contrastive learning on pairs with similar APIs but different semantics.

### case_id=3499 FP lexical_or_api_overlap

- 方法: `perform` vs `encryptPassword`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Performs a web action to classify a concept, involving session management, HTTP POST to an external URL, XML parsing, and forwarding to a result page.
- B 摘要: Encrypts a plaintext password using MD5 and returns the hexadecimal representation.
- 静态失败原因: Static BERT may have overemphasized lexical overlaps like 'getBytes', 'StringBuffer', and common API patterns (e.g., catch(Exception ex)) while ignoring the high-level method purpose and context.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would not consider these clones because they have entirely different purposes and functionality: one is a web action handler, the other is an encryption utility. The structural similarity is minimal, and the semantic gap is large.
- 共享行为: Both use try-catch blocks for exception handling；Both manipulate strings (StringBuffer, getBytes)
- 行为差异: Function A handles a web request with multiple dependencies (session, beans, URL connection); Function B is a standalone utility；Function A performs I/O (URL connection, XML parsing); Function B performs only in-memory computation；Function A has complex control flow with conditional checks and loops; Function B is a simple sequential method
- 修正建议: Incorporate method-level context (e.g., package, class name, method name significance)；Use data flow or dependency analysis to distinguish I/O-heavy vs. computation-only methods；Enhance training with negative examples of similar string operations but different semantics

### case_id=3500 FP boilerplate_overlap

- 方法: `main` vs `testCopy_readerToWriter_nullIn`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: A main method that generates adapter code from a Prolog file, handling command line options and file I/O.
- B 摘要: A unit test that verifies copying a null reader to a writer throws NullPointerException.
- 静态失败原因: Both methods contain exception handling (try-catch) and I/O-related classes, which may have caused the static model to overestimate similarity, ignoring the vast differences in logic and purpose.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB annotations typically require high syntactic and semantic similarity, which is absent here; the token Jaccard is very low (0.05) and the functions serve entirely different purposes.
- 共享行为: Both catch exceptions (IOException or NullPointerException) and terminate or fail.
- 行为差异: One is a standalone utility with complex I/O and logic, the other is a simple test checking null argument behavior.；Different method signatures and annotations (main vs @Test).；Completely different domains: adapter generation vs I/O utility testing.
- 修正建议: Improve model's ability to distinguish boilerplate code patterns from true functional overlap.；Incorporate dataflow or control-flow features to differentiate method-level behaviors.
