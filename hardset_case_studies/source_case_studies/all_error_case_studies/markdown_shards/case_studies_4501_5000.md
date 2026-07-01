# Error Case Studies 4501-5000

- Source model: `configured-llm`
- Cases: `4501` to `5000`

### case_id=4501 FN partial_functionality

- 方法: `copyResource` vs `writeConfiguration`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource from a URL or file to a destination file, throwing an exception if the resource is not found.
- B 摘要: Writes configuration to a Writer, either an error message if the resource is null or copying the resource's content from its URL using IOUtils.
- 静态失败原因: Static BERT/GraphCodeBERT likely failed due to low token overlap (Jaccard 0.196), different method names, use of external library (IOUtils) in B, and different control flow (byte loop vs bulk copy). The model may miss the abstract functional similarity because of surface-level divergence.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considers this a clone because both functions share the core pattern of reading from a resource URL and writing to an output, despite differences in output type and error handling. The high-level semantic similarity (resource copying) justifies a Type-3 clone label.
- 共享行为: Both obtain an InputStream from a URL.；Both copy data from the InputStream to an output (binary stream or Writer).；Both close the InputStream after copying.
- 行为差异: Output type: A writes to a FileOutputStream, B writes to a Writer.；Copying method: A uses a byte-by-byte loop, B uses IOUtils.copy.；Error handling: A throws exception if resource not found, B writes an error message on null or missing resource.；A also supports file-based source, B only URL from a configured resource.
- 修正建议: Use dataflow analysis to detect common patterns like 'open InputStream -> copy to OutputStream/Writer'.；Incorporate abstract code representations or AST-based features that capture data flow regardless of specific API calls.；Train models with contrastive learning on pairs that share partial functionality but differ in implementation details.

### case_id=4502 FP partial_functionality

- 方法: `doVersionCheck` vs `checkForUpgrade`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Checks for a new version of jEdit by reading a version file from a URL and comparing build numbers.
- B 摘要: Checks for software upgrades by querying a remote license/upgrade server, handling database records, MAC addresses, and multiple upgrade types, then updating UI components.
- 静态失败原因: The static model likely over-generalized based on superficial similarities: both functions use URL connections, BufferedReader, and have phrases like 'new version' and 'upgrade'. The model may have been misled by a common 'update checking' pattern without capturing the distinct processing logic and side effects.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB labels pairs as non-clones when they exhibit different control flows, data dependencies, and overall logic despite both being 'update check' functions. The significant behavioral differences and lack of common low-level semantics lead to a non-clone annotation.
- 共享行为: Both functions check for updates/upgrades by opening a URL connection and reading input；Both use BufferedReader and InputStreamReader to parse response；Both perform some conditional logic based on parsed data to decide whether an update is available
- 行为差异: Function A only reads two fields (version, build) from a simple text file; function B reads complex XML-like data and processes multiple upgrade records；Function A only compares build numbers; function B interacts with a database (TBLINSTALLATION) and handles license validation；Function B manipulates UI components (showing/hiding) and gathers MAC addresses and UNITID; function A only shows wait cursor and messages；Function B has exception handling that returns early; function A catches IOException and shows error messages
- 修正建议: Improve representation to capture data flow and control dependencies, not just token sequences；Use graph-based models that can differentiate simple version check from complex DB-backed upgrade process；Include more contextual training examples that contrast similar high-level tasks with different implementations

### case_id=4503 FN partial_functionality

- 方法: `getContent` vs `CheckUrl`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches the complete content of an HTTP response as a string using HttpClient.
- B 摘要: Fetches the first line of an HTTP response from a URL using HttpURLConnection.
- 静态失败原因: Static BERT methods rely on lexical and syntactic similarity, which is low here (token Jaccard 0.169). The different APIs (HttpClient vs HttpURLConnection) and different reading patterns (all lines vs one line) cause the model to miss the functional overlap.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels methods that share the high-level task of fetching HTTP content as clones, even if implementation details and output granularity differ, considering them as partial functionality clones.
- 共享行为: Both perform an HTTP GET request；Both read text from the HTTP response
- 行为差异: A reads all lines of the response; B reads only the first line；A uses HttpClient API; B uses HttpURLConnection API；A returns the full response body; B returns only one line or empty string on error；A throws exceptions; B catches and prints stack trace
- 修正建议: Incorporate data-flow analysis to capture the complete reading loop versus single read；Use abstract representations of HTTP fetch patterns；Consider input-output specifications to match methods with similar high-level goals

### case_id=4504 FP lexical_or_api_overlap

- 方法: `getLinksFromURLFast` vs `postRequest`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Parses HTML links from a URL using regex and returns vectors of links and texts.
- B 摘要: Performs an HTTP POST request with form data and returns the response as a string.
- 静态失败原因: Static BERT/GraphCodeBERT may have been misled by high lexical overlap (URL, URLConnection, BufferedReader, readLine) and similar control flow structure, ignoring the semantic difference in data processing.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels as non-clone because the functions have distinct goals and output types; the similarity is limited to common API usage patterns, not functional equivalence.
- 共享行为: Open a URL connection；Read from an input stream line by line；Handle IO exceptions
- 行为差异: getLinksFromURLFast extracts hyperlinks from HTML content；postRequest sends form data via POST method；Return types differ: Vector[] vs String
- 修正建议: Incorporate data flow or program dependence graphs；Use contrastive learning to penalize superficial API similarities；Add method signature and return type information

### case_id=4505 FN partial_functionality

- 方法: `doGet` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.5`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Handles HTTP GET requests for a portal page, including page retrieval, permissions check, logging, caching, and writing page output to a temporary file under certain conditions.
- B 摘要: Copies a file from source to destination using FileChannel transfer.
- 静态失败原因: Static BERT/GraphCodeBERT methods heavily rely on token overlap and structural similarity, which are extremely low (token Jaccard 0.033). The long and complex code in A with many external references (HttpServletRequest, PortalRequest, Property) has minimal lexical overlap with the short, straightforward copyFile. The model likely classified them as non-clone because they look completely different at the surface level.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled this as a clone due to a focus on the common file I/O behavior (writing to a temp file in A and copying a file in B), possibly considering both as 'file writing' operations. However, this is a very broad interpretation, and the overall functionality is vastly different.
- 共享行为: Both involve file I/O operations (writing or copying files).
- 行为差异: Function A is a complex servlet handler with many dependencies and side effects (session, logging, caching), whereas Function B is a simple utility.；Function A's file write is conditional and part of a larger workflow; Function B's sole purpose is file copy.；Function A throws ServletException and IOException; Function B only throws IOException.；Function A uses FileWriter; Function B uses FileChannel.
- 修正建议: Incorporate more robust dataflow analysis to detect similar I/O operations even when the overall function is different.；Use functional similarity measures that consider small code fragments within functions.；Improve representation learning to capture long-range semantic dependencies and side effects.

### case_id=4506 FN library_context_missing

- 方法: `callService` vs `httpRequestByPOST`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.95`
- 推荐路线: `context_recovery_then_expert`；动态可解性: `low`；执行优先级: `medium`
- A 摘要: Sends an HTTP GET request using URL.openStream() and reads the response line by line into a StringBuffer, storing the result in an instance field 'answer'.
- B 摘要: Sends an HTTP POST request using Apache HttpClient with form parameters, reads the response line by line if status code is <400, returns the response string or null on failure, and sets error fields.
- 静态失败原因: Static BERT/GraphCodeBERT likely failed due to low token overlap (Jaccard ~0.23) and surface-level differences in APIs (URL.openStream vs HttpClient), method signatures (private void vs public String with parameters), and error handling patterns. The model may not have captured the shared intent of HTTP response reading because it lacks understanding of library mappings and functional equivalence across different implementations.
- 静态 case study: 该类错误缺少关键上下文或需要深层语义，纯静态方法不可靠。
- 动态 case study: 动态执行价值较低：样本可能依赖库、框架、网络、GUI、数据库或项目上下文，需要先恢复环境或 mock 依赖。
- BCB 偏好解释: BCB likely considers these Type-3 clones because both functions perform the core task of making an HTTP request and reading the response line by line, despite differences in request method (GET vs POST), parameter handling, error management, and library usage. The high-level purpose (HTTP communication and response capture) is similar enough for a broad clone annotation.
- 共享行为: Both initiate an HTTP connection to a given URL；Both read the response line by line using BufferedReader；Both append lines to a StringBuffer to construct the full response；Both handle IOException on network errors
- 行为差异: A uses GET implicitly via URL.openStream(); B uses POST explicitly with HttpClient；A sends no parameters; B sends a list of NameValuePair as form data；A stores output in a field (void method); B returns a String output；A handles MalformedURLException separately; B does not
- 修正建议: Augment training data with examples of functionally similar code using different libraries (e.g., java.net vs Apache HttpClient)；Use graph-based models that capture data flow and control flow rather than relying solely on token sequences；Include more Type-3/Type-4 clone pairs in training to teach the model broader functional similarity；Add a preprocessing step that abstracts API calls (e.g., URL.openStream → HTTP_READ) to reduce lexical gap

### case_id=4507 FN benchmark_preference_bias

- 方法: `createOutputStream` vs `doGet`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Creates a BufferedWriter to write a ZIP file, skipping the 'content.xml' entry from input and adding a new one.
- B 摘要: Handles HTTP GET request to retrieve and render a page, including permission checks and optional caching to a file.
- 静态失败原因: The static model correctly predicted non-clone (0) because there is no real semantic similarity. The BCB label might be an error.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might have annotated this as clone due to both functions writing to files (output stream) and both handling exceptions, but the core functionality is entirely different. Possibly the annotator focused on the technical similarity of 'creating an output stream' vs 'writing output'.
- 共享行为: Both perform I/O operations；Both use BufferedWriter/FileWriter for writing to files；Both handle exceptions
- 行为差异: Function A transforms a ZIP file by copying entries except one; Function B renders a web page and may cache HTML output.；Function A is purely file-based; Function B is HTTP request handling with servlet context.；Function A uses ZipInputStream/ZipOutputStream; Function B uses response object and Page objects.
- 修正建议: Re-annotate this pair as non-clone in BCB；Train models to disregard superficial API overlap

### case_id=4508 FP lexical_or_api_overlap

- 方法: `handledRun` vs `downloadModel`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Downloads updated game data XML from a fixed URL, compares version, and writes new file if newer.
- B 摘要: Downloads an RDF model from a given URL and returns it as a Model object.
- 静态失败原因: Static models like GraphCodeBERT rely heavily on token and structure similarity; the high overlap of standard Java library calls (URL, InputStream, IOException) misled the model into thinking they are similar.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels as non-clone because the functions have different purposes (game data update vs. RDF model download), different outputs, and only superficial API overlap.
- 共享行为: Both involve opening a URL connection and reading data from it.；Both handle IO exceptions (MalformedURLException, IOException).
- 行为差异: A writes to a file, B returns a Model object.；A checks version and conditionally downloads, B always downloads.；A uses BufferedReader and byte-level writing, B uses InputStream and Jena model reader.；A has additional UI interaction (JOptionPane) and game database operations.
- 修正建议: Incorporate data flow analysis to distinguish output types and final operations.；Add semantic features like method purpose (e.g., via docstrings or comment embedding).；Use contrastive learning to penalize functional differences despite API overlap.

### case_id=4509 FN boilerplate_overlap

- 方法: `addIDs` vs `getPagina`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.75`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Constructs a metabolite query URL, parses HTML response to extract various IDs and molecular weight, and populates a data row object.
- B 摘要: Fetches the entire content of a given URL as a string using a default authenticator.
- 静态失败原因: The model likely focused on overlapping tokens (URL, BufferedReader, readLine, IOException, return) and the overall structure of a web request, missing the detailed business logic in function A that makes it functionally different.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB annotator might have considered both as 'web data fetching' operations and overlooked the distinct data processing logic, possibly due to the common I/O pattern and the presence of similar catch blocks.
- 共享行为: Both open a URL and read its content line by line.
- 行为差异: A extracts specific fields from HTML and sets them on an object; B concatenates all lines and returns raw string.；A returns an integer score; B returns the whole response string.；A sets various properties; B does no parsing.；A handles only one specific domain; B is generic.
- 修正建议: Enhance training with more examples that distinguish simple I/O from complex parsing; incorporate data flow analysis or control flow graph features.

### case_id=4510 FN boilerplate_overlap

- 方法: `doVersionCheck` vs `addIDs`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Checks for a new version of jEdit by fetching a version file from a URL and comparing build numbers.
- B 摘要: Parses HTML from a web service to extract metabolite IDs and molecular weight data, setting them on a PeakListRow.
- 静态失败原因: Static BERT/GraphCodeBERT likely failed to recognize them as clones under BCB's broader criteria because it overfits to lexical overlap and specific API calls, missing the abstract structural similarity that BCB annotators considered. The model predicted non-clone (0) due to low token Jaccard (0.17) and different method names and logic, while BCB considered the identical I/O pattern as sufficient for Type-3/Type-4 clone.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may label these as clones due to shared boilerplate: both methods open a URL, wrap InputStream in BufferedReader, read lines in a while loop, and handle IOException. This structural similarity in exception handling and I/O could lead to overestimation of clone relatedness, especially if annotators focused on the code pattern rather than domain-specific logic.
- 共享行为: Both open a URL and read lines using BufferedReader；Both handle IOException with error logging or user messages；Both parse lines using string operations
- 行为差异: doVersionCheck checks version/build numbers and shows UI messages; addIDs extracts various metabolite IDs and numeric scores from HTML and stores them in a data row.；doVersionCheck is simple and short; addIDs is long with multiple parsing branches and database-like operations.；doVersionCheck returns void; addIDs returns an int score.
- 修正建议: Incorporate semantic information about the operations performed, not just the I/O pattern.；Use finer-grained program analysis to distinguish between different data processing tasks.；Consider domain-specific context (version checking vs. bioinformatics data extraction).

### case_id=4511 FN partial_functionality

- 方法: `getXML` vs `seeURLConnection`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Retrieves an XML response from a configurable URL by encoding a request and reading the response line by line, returning the content as a string or null on error.
- B 摘要: Reads the content of a hardcoded URL and logs the response string to debug output, without returning a value.
- 静态失败原因: The model likely focused on token-level differences such as different method signatures, return types, and exception handling, missing the structural similarity in the core I/O loop.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often considers functions that perform the core task of reading from a URL and accumulating lines as clones, even if parameterization, error handling, and output differ, as these are considered Type-3 or Type-4 clone variations.
- 共享行为: Both open a URL connection and read input line by line into a StringBuffer.
- 行为差异: A has configurable URL and request encoding, B uses a fixed URL.；A returns the content, B logs it.；A handles specific exceptions, B throws all exceptions.
- 修正建议: Incorporate structural comparison of the core I/O loop using abstract syntax tree or control flow graph matching.；Use data flow analysis to detect similar read-write patterns.；Ignore differences in URL construction and error handling for broad clone detection.

### case_id=4512 FP lexical_or_api_overlap

- 方法: `callApiPost` vs `getFullScreenUrl`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Sends an HTTP POST request to an API with parameters, checks expected response code, and returns the response InputStream.
- B 摘要: Connects to a YouTube URL, reads and parses the page to extract video parameters, then constructs and returns the fullscreen URL.
- 静态失败原因: Static BERT likely over-relied on lexical and API-level overlap (e.g., URL, openConnection, InputStream, IOException) without capturing the distinct control-flow and data-flow semantics, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically requires significant functional overlap for clones; despite both using HTTP connections, the core tasks (generic API POST vs. specific YouTube URL parsing) are too dissimilar for a Type-3/4 clone label.
- 共享行为: Both use URL and URLConnection to open network connections；Both handle IOException/Exception；Both involve reading from input streams
- 行为差异: A uses POST method with parameters; B uses GET (implicitly) and reads HTML；A checks response code and throws custom exception; B parses response for specific strings；A returns InputStream; B returns a constructed URL string；A sets timeouts and headers; B does not
- 修正建议: Incorporate data-flow and structural information (e.g., program graphs) to distinguish different usage contexts of same APIs；Use contrastive learning to push apart pairs with similar APIs but different overall tasks；Increase diversity of negative training examples that share API calls but differ in business logic

### case_id=4513 FN partial_functionality

- 方法: `addIDs` vs `doVersionCheck`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Retrieves metabolite IDs and scores from a web API and populates a PeakListRow object with various properties.
- B 摘要: Checks for software version updates by reading a version URL and triggers a version check dialog.
- 静态失败原因: Static BERT models rely on token overlap; low Jaccard similarity (0.16) and different domain-specific terms (e.g., PeakListRow vs. View) lead to poor similarity representation.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this as clone because both functions follow a common pattern of opening a URL, reading lines, and performing conditional parsing, which is a broad Type-4 semantic clone.
- 共享行为: Open an HTTP connection to a URL；Read lines using BufferedReader；Parse lines based on string patterns；Handle IOException
- 行为差异: Different purpose: metabolomics data retrieval vs. version checking；Different output: returns int (score) vs. void；Different data structures populated: PeakListRow vs. View and version strings；Different error handling: logging vs. GUI error dialog
- 修正建议: Use graph-based or dataflow-aware models to capture shared structure beyond tokens.；Incorporate broader context like method names and surrounding code.；Train on more diverse cross-domain clone pairs.

### case_id=4514 FN partial_functionality

- 方法: `addRecord` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.35`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies an input stream to a temporary file, computes a digest for deduplication, and manages file storage with collision detection.
- B 摘要: Handles a launch configuration for an Eclipse plugin, processes Maven POM files, sets Hibernate properties, and manages project resources.
- 静态失败原因: The model likely focused on lexical and structural differences (low Jaccard similarity) and missed the high-level similarity in stream processing and file management, which BCB accepts as partial functionality.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider these clones due to broad Type-4 partial functionality: both perform stream-based I/O, file creation, and error handling, despite different domains.
- 共享行为: Both use IOUtils.copy for stream copying；Both involve file existence checks；Both use try-catch-finally for resource cleanup
- 行为差异: addRecord focuses on data storage with collision avoidance; launch configures and executes a build process；addRecord uses digest hashing and temporary file renaming; launch uses XML handling and persistent properties；addRecord is IO-bound with file system operations; launch is UI-plugin-oriented with project model interactions
- 修正建议: Incorporate explicit modeling of file/stream I/O patterns as a clone signature；Use contrastive learning with positive pairs of partial clones sharing I/O and resource management；Augment training data with Type-4 examples that differ in domain but share core patterns

### case_id=4515 FN benchmark_preference_bias

- 方法: `doGet` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Handles an HTTP GET request for a page, involving authentication, logging, and caching.
- B 摘要: Copies a file from source to destination using NIO channels with error handling.
- 静态失败原因: The static model correctly predicted non-clone because of low token overlap and clear functional divergence; it did not fail.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have erroneously labeled this pair as clones due to superficial similarity in error handling and logging patterns, which is not sufficient for functional similarity.
- 共享行为: Both use try-catch blocks for error handling；Both log exceptions or informational messages
- 行为差异: Function A processes HTTP requests and page logic, while Function B performs file I/O；Function A has complex control flow with multiple conditions, Function B is linear；Function A interacts with servlet API and persistence, Function B is a utility method
- 修正建议: Re-evaluate BCB label for this pair; likely a labeling error；Increase threshold for boilerplate similarity in clone detection benchmarks

### case_id=4516 FN benchmark_preference_bias

- 方法: `doGet` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Handles HTTP GET request to retrieve a page parameter, look up the page, check user visibility, log request, and render the page with caching and statistics.
- B 摘要: Writes license information of JAR libraries in a directory to a text file by reading metadata files.
- 静态失败原因: The static BERT model correctly identified the low token overlap and semantic dissimilarity, but the BCB label contradicts this; the model's prediction aligns with the apparent lack of clone relation.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have considered them clones based on a very broad notion of 'output generation' or 'file/resource handling', but the differences in context and functionality are significant.
- 共享行为: Both functions write formatted output to a stream；Both iterate over collections (pages or files)；Both use string building and concatenation
- 行为差异: Function A is a servlet method with request/response objects, while B is a standalone main method；A involves user authentication and page access control, B does not；A writes HTML to HTTP response, B writes text to a file；A has complex caching and error handling logic, B is straightforward
- 修正建议: Review BCB annotation guidelines to ensure consistency；Consider using additional context or deeper semantic analysis；Adjust detection thresholds to avoid false negatives in clearly non-clone pairs

### case_id=4517 FN benchmark_preference_bias

- 方法: `readAndRewrite` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Reads a DICOM file, parses its metadata and pixel data, then writes the dataset to an output file with specific encoding.
- B 摘要: Builds an editable HTML site by reading XML/XSL sources, transforming each page, and writing the output to files with string replacements.
- 静态失败原因: Static BERT methods rely on token and structural similarity, which are very low here (Jaccard=0.036). They likely correctly identified the functions as non-clones. The BCB label appears to be an outlier or reflects a broad functional similarity definition not captured by lexical/structural features.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider both as clone Type-4 because they share a high-level read-process-write pattern and both involve file I/O. However, the low token overlap and completely different domains suggest this is a borderline or erroneous annotation.
- 共享行为: Both read from an input source (file or stream) and write to an output file.；Both use Java I/O streams (FileInputStream, FileOutputStream, etc.) and perform file operations.；Both involve processing data before writing (parsing/transforming).
- 行为差异: Function A processes DICOM medical images with specific pixel data handling; Function B processes XML/XSL for web page generation.；Function A has a fixed pipeline (parse, read pixels, write); Function B iterates over pages, applies XSLT, and does string replacements.；Function A uses DICOM-specific libraries (DcmParser, DcmEncodeParam); Function B uses DOM, transformers, and file system utilities.；Function B has complex error handling and debugging output; Function A is simpler and more linear.
- 修正建议: Use domain-specific semantic models (e.g., code summarization) to detect functional similarity beyond I/O patterns.；Incorporate dataflow and program dependence graphs to capture true behavioral equivalence.；Re-evaluate BCB annotations for Type-4 clones to ensure they reflect meaningful functional overlap.

### case_id=4518 FN partial_functionality

- 方法: `main` vs `addToArchive`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Extracts all entries from a zip file downloaded from a URL and writes them to disk.
- B 摘要: Adds a single entry from an InputStream to a ZipOutputStream, associating it with a filename and returning a URL.
- 静态失败原因: A static BERT/GraphCodeBERT model might fail due to low token overlap (0.12) and focus on lexical differences (e.g., 'ZipInputStream' vs 'ZipOutputStream', 'FileOutputStream' vs 'IOUtils.copy'), missing the conceptual similarity of zip entry processing. Also, the model may be misled by the different method signatures and the main method wrapper.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider this a clone because both methods perform operations on zip archives (extraction vs addition) using similar ZipEntry and stream patterns, and BCB's Type-3/4 criteria tolerate differences in direction (extract vs add) as long as the core zip handling logic is present.
- 共享行为: Both perform zip entry processing (reading/writing entries)；Both use ZipEntry objects；Both involve stream handling (InputStream/OutputStream)
- 行为差异: A extracts from a zip, B adds to a zip；A writes entries to files, B writes to an archive stream；A is a main method, B is a utility method taking parameters；A reads from URL or file, B takes source InputStream
- 修正建议: Enhance model with structural similarity (e.g., AST or graph-based methods) to capture zip entry processing patterns；Incorporate dataflow analysis to recognize similar stream operations；Use contrastive learning with zip-related examples to teach similarity across extract/add directions

### case_id=4519 FP lexical_or_api_overlap

- 方法: `getLinksFromURLFast` vs `load`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Connects to a URL, reads the HTML page, extracts all hyperlinks and their anchor texts using regex, and returns two Vectors of links and texts.
- B 摘要: Connects to a pastebin URL given an ID, reads the raw content line by line, and returns it as a single string.
- 静态失败原因: The model likely overfitted on the common pattern of opening a URL, creating a BufferedReader, and reading lines, which are present in both functions. Despite low token overlap (0.196), the sequence of API calls (URL, URLConnection, BufferedReader, while read loop) is similar, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled as non-clone because the functions have fundamentally different outputs and purposes: one is a link extractor, the other is a raw text fetcher. Even for Type-4 partial functionality, the core behavior differs significantly.
- 共享行为: Both open a URL connection and use BufferedReader to read the response line by line.；Both handle network I/O and can throw or catch exceptions.
- 行为差异: A parses HTML to extract links; B returns raw content unchanged.；A returns an array of two Vectors; B returns a single String.；A uses multiple regex patterns and prints debug info; B does not parse the content.；A takes a full URL; B constructs URL from an ID.
- 修正建议: Incorporate data flow analysis to capture how the input is processed and what output is produced.；Use structure-aware representations (e.g., AST or dataflow) to distinguish between different operations on the read data (regex extraction vs. simple concatenation).；Train the model to recognize that similar I/O patterns with different post-processing constitute different semantics.

### case_id=4520 FN partial_functionality

- 方法: `doVersionCheck` vs `seeURLConnection`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Checks for new version of jEdit by reading a version file from a URL and comparing build numbers.
- B 摘要: Fetches content from a hardcoded URL and logs the entire response.
- 静态失败原因: Static BERT models may have missed the structural similarity due to low token overlap and presence of UI-specific tokens in A, while the core I/O pattern is similar.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considers both as 'reading from URL via BufferedReader' which is a common I/O pattern, and may ignore differences in URL source and output handling.
- 共享行为: Both open a URL and create a BufferedReader from its input stream；Both read lines in a while loop；Both close the BufferedReader after reading
- 行为差异: A uses a configurable URL from property, B uses a hardcoded URL；A parses lines for version/build, B concatenates all lines；A shows UI messages and error dialogs, B logs output；A catches IOException and shows error, B throws Exception
- 修正建议: Incorporate data-flow analysis to identify common I/O operations；Use code structure similarity beyond token overlap；Add features capturing I/O patterns like openStream, BufferedReader, readLine

### case_id=4521 FP boilerplate_overlap

- 方法: `readReferenceText` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a text file from a bundle resource given an identifier, returning its content as a string, and throws an exception if not found.
- B 摘要: Performs a Google image search for the current track's artist and album, parses the HTML response to extract image URLs, and adds them to a list, showing an error dialog on failure.
- 静态失败原因: Static BERT-based models often rely on token overlap and structural patterns; both functions share common API usage patterns (URL, BufferedReader, try-catch) leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled non-clone because the functions have completely different semantics and no shared functionality beyond basic I/O boilerplate.
- 共享行为: Open a URL connection；Read input using BufferedReader；Read lines in a loop；Handle exceptions
- 行为差异: Different purposes: read local resource vs web search；Different outputs: return string vs modify a list；Different exception handling: throw vs show dialog；Different URL construction and parsing logic
- 修正建议: Incorporate method name and return type as semantic signals；Use graph-based models that capture data flow and call graph differences；Train with contrastive examples that distinguish file I/O from network I/O

### case_id=4522 FN partial_functionality

- 方法: `getResourceAsStream` vs `createTempFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Returns an InputStream for a resource, with caching and HTTP support.
- B 摘要: Creates a temporary file from a classpath resource and copies its contents.
- 静态失败原因: Low token overlap (0.09) and different code structures due to caching and HTTP handling in A; the model fails to recognize the shared intent of loading a resource.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB's broad annotation style accepts partial functional similarity as a clone; both functions perform resource loading and I/O, which is considered functionally related.
- 共享行为: Both read a resource by name from the classpath；Both handle InputStreams and can fail if the resource is missing
- 行为差异: A returns an InputStream, B writes to a file and returns void；A has caching logic and handles HTTP connections, B does not；A uses manual byte-by-byte copying, B uses IOUtils.copyLarge；A is synchronized, B is not
- 修正建议: Incorporate high-level intent or API usage patterns (e.g., getResourceAsStream) to capture functional similarity；Use AST-based or control-flow analysis to ignore implementation details and focus on core behavior

### case_id=4523 FN lexical_or_api_overlap

- 方法: `sendExceptionToServer` vs `handler`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends exception details to a server via an HTTP POST request with URL-encoded parameters.
- B 摘要: Parses an HTTP response line by line to extract substrings and update a map based on target configuration.
- 静态失败原因: The low token Jaccard (0.16) and different API usage (URLEncoder vs substring) caused the model to focus on lexical differences rather than the abstract I/O pattern; static BERT models often miss functional similarities when surface tokens diverge.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may have labeled this as a clone due to the shared high-level pattern of network I/O (open URL, read lines, process) and exception handling, considering it a Type-3 clone despite low token overlap.
- 共享行为: Both open a URL and read lines from an HTTP response using a BufferedReader.；Both handle IOException with try-catch blocks.；Both process lines in a while loop.
- 行为差异: A sends a POST request with URL-encoded data; B uses GET-like openStream without sending data.；A writes request parameters and reads server response; B only reads and parses the response.；A uses URLEncoder and StringBuilder for string building; B uses substring and indexOf for pattern extraction.；A outputs to console; B updates the input map and does not print.
- 修正建议: Incorporate data flow or control flow features that capture I/O patterns.；Use graph-based models or AST differencing to detect structural similarities.；Include training examples of functions with diverse APIs but similar high-level behavior.；Implement a retriever that groups functions by network I/O operations.

### case_id=4524 FP boilerplate_overlap

- 方法: `executePost` vs `getPagina`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: executes an HTTP POST request with parameters and returns the response as a string, or null on failure
- B 摘要: performs an HTTP GET request and returns the page content as a string, or the exception message on failure
- 静态失败原因: The static BERT/GraphCodeBERT model likely overemphasized the common boilerplate (URL, BufferedReader, while loop, try-catch) and failed to capture the semantic differences in HTTP method and error handling
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labeled non-clone because the functions differ in HTTP method, error handling, and response format, making them not interchangeable despite shared HTTP boilerplate
- 共享行为: both perform HTTP requests；both read response line by line and return a string
- 行为差异: HTTP method: POST vs GET；error handling: returns null vs returns exception string；response building: appends carriage return vs concatenates directly；parameter handling: sends URL parameters in body vs no parameters
- 修正建议: incorporate features that distinguish HTTP method (e.g., setRequestMethod)；consider error handling patterns；capture presence of request body parameters

### case_id=4525 FP long_range_semantics

- 方法: `actionPerformed` vs `unzipEntry`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `static_summary_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Handles various GUI action commands to set application preferences and update UI components.
- B 摘要: Unzips a single entry from a zip file to a specified output directory, creating intermediate directories if needed.
- 静态失败原因: The static model likely failed due to long-range semantics: function A is very long with many branches, making it hard to capture overall intent. Additionally, the model might have been misled by superficial similarities like file-related operations (e.g., File objects) or exception handling patterns.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely labels non-clone because the functions share no common purpose or behavior; one is GUI event handling, the other is file I/O utility.
- 行为差异: Function A deals with GUI events and preference settings, while B handles file extraction.；A uses file choosers and preference storage; B uses zip input/output streams.；A has multiple conditional branches for different commands; B is a straightforward sequential process.；A modifies UI state; B writes to the filesystem.
- 修正建议: Train on more structured representations like ASTs or data-flow graphs to capture function purpose.；Use sequence length limits and attention mechanisms that better handle long methods.；Include method signature and context (e.g., class name) to disambiguate different domains.

### case_id=4526 FP partial_functionality

- 方法: `doVersionCheck` vs `checkForUpgrade`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Checks for a new version of jEdit by reading a URL and parsing build numbers.
- B 摘要: Checks for upgrades of a telecom system by querying a license server and processing upgrade data into a database.
- 静态失败原因: Static BERT may have been misled by the common API usage (URL.openStream, BufferedReader) and the general theme of version checking, ignoring the diverging control flow, database interactions, and UI manipulations.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB would likely label these as non-clones due to low lexical similarity (token Jaccard 0.098) and distinct implementations; the shared high-level goal of version checking is too broad to override the structural differences.
- 共享行为: Both functions check for updates from a remote server via URL；Both read lines from an input stream and parse version/status information
- 行为差异: Function A is simple and stateless, while Function B involves database operations and UI management；Different URL query parameters and response formats；Function B has complex error handling with multiple specific messages, Function A only catches IOException；Function B manipulates UI components and database entries
- 修正建议: Train with more examples emphasizing that shared API usage alone does not imply clone；Incorporate dataflow analysis to differentiate side-effect-heavy functions from simple ones；Consider structural similarity metrics beyond token overlap

### case_id=4527 FP boilerplate_overlap

- 方法: `getMD5` vs `perform`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Computes MD5 hash of input string and returns hex string.
- B 摘要: Handles a web classification action, processes form parameters, communicates with an external service, and returns an ActionForward.
- 静态失败原因: Static BERT/GraphCodeBERT may have been misled by superficial similarities such as both using loops, character arrays, and string concatenation, despite vastly different purposes and APIs. The low token Jaccard suggests the model relied on weak embedding features.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clones for totally different functionality, even if both have some generic boilerplate (try/catch) and string operations.
- 共享行为: Both use try-catch for exception handling；Both build a string from multiple parts
- 行为差异: Function a is a standalone utility for MD5 hashing; Function b is a complex web request handler with session management and external data exchange；Function a has a single input parameter (String) and returns a String; Function b has multiple parameters (ActionMapping, ActionForm, etc.) and returns an ActionForward；Function a uses java.security.MessageDigest; Function b uses Struts and HTTP/URLConnection
- 修正建议: Incorporate data-flow or call-graph information to distinguish utility functions from complex business logic.；Use contrastive learning to push apart embeddings of semantically different functions even if they share common programming idioms.

### case_id=4528 FN benchmark_preference_bias

- 方法: `parseContent` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.65`
- 推荐路线: `preference_memory_with_manual_audit`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Parses HTML content from an input stream, extracting metadata like charset, HTML provider, links, and body text.
- B 摘要: Launches a Maven-based Eclipse project build, handling configuration, pom files, and Hibernate reverse engineering.
- 静态失败原因: The token overlap is very low (0.063) and method names differ entirely. Static BERT/GraphCodeBERT rely on lexical and structural patterns; the different API calls (HTML parsing vs Eclipse launch) and domains produce dissimilar embeddings, leading to false negative.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider these as clones due to similarity in high-level structure: both perform resource acquisition, conditional checks, and multiple steps of processing with I/O operations, common in many Java enterprise applications (Type-4).
- 共享行为: Both use IOUtils.copy to copy streams.；Both involve checking resource existence and processing configuration.；Both have error handling via exceptions (IOException, CoreException).
- 行为差异: parseContent processes HTML for content extraction; launch manages project build lifecycle.；parseContent operates on a stream and adds fields to a document; launch uses Eclipse launch configuration and project resources.；parseContent focuses on charset detection and HTML parsing; launch focuses on Maven pom.xml handling and Hibernate setup.
- 修正建议: Include training examples of broad Type-4 clones with low lexical overlap but similar control flow patterns.；Enhance model with ability to recognize abstract patterns like 'resource setup then process'.；Use data augmentation by generating synthetic clones with swapped domain-specific terms.

### case_id=4529 FN partial_functionality

- 方法: `main` vs `getPagina`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends a specific POST request to RenRen API with hardcoded parameters and prints the response.
- B 摘要: Fetches the content of a given URL (GET request) and returns it as a string with error handling.
- 静态失败原因: Low token Jaccard similarity (0.138) and differing method names (main vs getPagina) led the static model to miss the clone; it could not capture the high-level semantic similarity of fetching a URL due to reliance on lexical overlap and structural patterns.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider them clones because both involve fetching content from a URL via HTTP, sharing the core pattern of opening a connection and reading lines, despite differences in parameters, output handling, and error handling.
- 共享行为: Both open a URL connection and read lines from the input stream using BufferedReader and InputStreamReader.
- 行为差异: Function A is a main method with no return; B returns a string.；A uses POST with many hardcoded parameters; B uses GET with a URL parameter.；A prints the response; B returns it.；A throws IOException; B catches exceptions and returns error strings.
- 修正建议: Use dataflow-based models that capture input-output behavior.；Train with more diverse examples of URL fetching.；Consider method name and signature normalization.

### case_id=4530 FP lexical_or_api_overlap

- 方法: `perform` vs `getMessageDigest`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Performs an HTTP request handling for classifying concepts, involving session management, URL connection, and XML parsing.
- B 摘要: Computes SHA-1 message digest of an array of input strings.
- 静态失败原因: Static BERT/GraphCodeBERT likely overemphasized the presence of common Java API tokens (e.g., 'String', 'session', 'getBytes', 'InputStreamReader') and structural patterns like loops and try-catch, leading to a false positive. The models may have captured superficial lexical overlap without understanding the distinct domain contexts.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would not consider these as clones because they have entirely different purposes and semantics. BCB's Type-3/4 still require some functional similarity or common utility, which is absent here.
- 共享行为: Both have loops；Both have conditional statements；Both have try-catch blocks
- 行为差异: Function A handles HTTP requests and session management, while B computes a hash.；A uses URL connections and XML parsing, B uses MessageDigest.；A returns an ActionForward, B returns a String.；A has extensive business logic, B is a utility method.
- 修正建议: Improve model's ability to capture semantic differences by incorporating more structural or dataflow analysis.；Use more contextualized embeddings that differentiate between web request handling and cryptographic operations.；Add more negative examples for unrelated pairs during training.

### case_id=4531 FP boilerplate_overlap

- 方法: `main` vs `main`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Generates adapter classes from a Prolog file and outputs them as a JAR.
- B 摘要: Compresses or decompresses a file using GZIP based on its extension.
- 静态失败原因: Static BERT models likely over-relied on surface-level similarities such as common tokens (main, args, File, IOException, System.out, try, catch, return) and similar boilerplate structure (argument checking, error handling, file I/O). The low Jaccard similarity (0.12) suggests they are not lexically close, but the model may have been misled by overlapping API calls and control flow patterns.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clones when functions perform fundamentally different tasks, even if both are 'main' programs with similar boilerplate. The core functionality (code generation vs. file compression) is unrelated, so BCB correctly marks them as not clones.
- 共享行为: Both are command-line utilities with a main method that processes arguments.；Both perform file I/O operations and handle exceptions.；Both use standard Java constructs like File, IOException, and try-catch.
- 行为差异: A parses Prolog and generates Java adapter classes; B performs gzip compression/decompression.；A uses complex custom classes (Parser, FactVisitor, AdapterAnnotationGenerator, etc.); B only uses standard Java I/O classes.；A outputs a JAR file with generated classes and serialized data; B outputs a decompressed or compressed file.；A has lengthy logic for class loading and assembly; B has a simple read-write loop.
- 修正建议: Incorporate domain-specific contextual embeddings or type information to detect distinct libraries (e.g., PrologParser vs. GZIPInputStream).；Use data flow analysis to capture the core transformation (code generation vs. data compression).；Train with more negative examples that share boilerplate but differ in functionality.

### case_id=4532 FN boilerplate_overlap

- 方法: `addIDs` vs `postData`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.3`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches metabolite information from a web service by name and populates a PeakListRow with various identifiers and properties, returning a score.
- B 摘要: Posts form data to a specified URL and discards the response, for generic HTTP POST operations.
- 静态失败原因: Static BERT models like GraphCodeBERT rely on lexical and structural similarity; with low token Jaccard (0.118), it correctly identified them as different. It missed the broader web I/O pattern that BCB might consider relevant.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may consider both as doing web I/O and processing streams, thus partial Type-4 clones, despite different purposes.
- 共享行为: Both use URL and URLConnection to communicate over HTTP；Both use BufferedReader to read from input stream；Both handle I/O streams and close connections
- 行为差异: A reads and parses HTML content to extract metabolite data; B writes data to output stream and discards response；A sets multiple fields on a row object and returns an integer; B returns void；A has complex conditional parsing for different HTML patterns; B has no parsing logic；A fetches data via GET-like query; B sends data via POST
- 修正建议: Incorporate data-flow analysis to distinguish between read/write operations；Use dynamic or execution-based features to capture intent；Adjust for benchmark preference bias by aligning with BCB's broad clone definition

### case_id=4533 FN benchmark_preference_bias

- 方法: `saveFile` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Saves UI configuration to an XML file, including window positions, toolbar visibility, look and feel, volume, and internal window states.
- B 摘要: Retrieves a resource from a URL with caching, returning an InputStream or null; handles HTTP connections and local caching.
- 静态失败原因: Static BERT/GraphCodeBERT relies on token overlap and syntactic similarity (Jaccard=0.098), which is low; however, BCB label suggests broader similarity that the model missed, possibly because the model cannot capture the high-level conceptual relation of configuration handling in a UI framework.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled them as clones due to overall structural similarity (both have try-catch-finally, file I/O, and are part of the same project handling configuration files), even though their functionality is opposite (save vs. load).
- 共享行为: Both involve file I/O operations；Both use try-catch-finally for exception handling；Both manage streams (FileOutputStream, InputStream, Buffered streams)
- 行为差异: A writes XML configuration; B reads and caches from remote URL and local file system；A uses XML Document/Element APIs; B uses URLConnection and HTTP；A saves to a file; B returns an InputStream or null；A has no caching logic; B implements a cache with hashtable
- 修正建议: Incorporate dataflow analysis to track data transformations；Use functional abstraction to detect high-level intent (save vs. load)；Consider project-level context to identify configuration handling patterns

### case_id=4534 FN partial_functionality

- 方法: `getButtonSonido` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Creates a GUI button that opens a file chooser to select a sound file, copies it to a project directory, and updates the button icon and plays audio.
- B 摘要: Retrieves a resource as an InputStream, optionally caching it locally from a URL with HTTP conditional GET and file copy.
- 静态失败原因: Static BERT may have focused on low token overlap and dissimilar high-level semantics, missing the partial file I/O similarity that BCB might consider sufficient for a clone.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled as clone due to both using file I/O streams and exception handling patterns, but the overall functionality is very different.
- 共享行为: Both perform file I/O operations (FileInputStream, FileOutputStream)；Both handle exceptions with printStackTrace；Both use System.out.println for debugging
- 行为差异: A is UI-focused (JButton, ActionListener); B is resource retrieval；A copies a local file; B downloads from URL with caching；A uses JFileChooser for user input; B uses URLConnection；A does not involve HTTP; B does
- 修正建议: Train model to recognize partial functionality clones based on shared I/O patterns；Incorporate file operation similarity measures into the clone detection model

### case_id=4535 FN benchmark_preference_bias

- 方法: `getResourceAsStream` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.2`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Retrieves a resource by name, downloading from URL if not cached, and returns an InputStream with caching logic.
- B 摘要: Copies a file from source to destination using FileChannels in Java NIO.
- 静态失败原因: The static BERT model likely correctly predicted non-clone due to extremely low token overlap (0.0588) and completely different method names and logic; it failed to override its learned similarity threshold for a false positive BCB label.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might consider these as clones based on a very loose interpretation of both being I/O utility methods that copy data (URL to file vs file to file), but this is a stretch and likely a misannotation in the dataset.
- 共享行为: Both perform file I/O operations (reading and writing).
- 行为差异: A involves URL connection, HTTP requests, and caching; B is a simple file copy.；A returns an InputStream; B is void.；A handles exceptions by printing stack trace; B throws IOException.；A is much longer and more complex.
- 修正建议: Review BCB labels for consistency in such low-similarity cases.；Improve model robustness to handle potential dataset noise.

### case_id=4536 FN benchmark_preference_bias

- 方法: `readAndRewrite` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Reads a DICOM file, parses pixel data, and writes the dataset to an output file.
- B 摘要: Builds an editable HTML site by transforming XML pages with XSLT, reading control files, and writing output files.
- 静态失败原因: The static model correctly predicted non-clone (0) due to low lexical overlap (token Jaccard 0.0359) and distinct API usage. The BCB label being 1 likely confused evaluation, but the model's prediction aligns with semantic dissimilarity.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled these as clones based on a loose similarity: both involve reading input, processing, and writing output, but the domains and logic are entirely different. This appears to be an annotation error or an extremely broad Type-4 interpretation.
- 共享行为: Both perform file I/O operations (reading and writing files)；Both use streams and buffers
- 行为差异: Function A processes DICOM medical images with pixel data; Function B processes web pages with XML/XSLT；Function A uses DICOM-specific libraries; Function B uses general XML and string manipulation；Function A has a simple linear flow; Function B has complex loops and conditional inclusion of control files
- 修正建议: Re-evaluate BCB label for this pair; likely a false positive in the benchmark；If strict semantic equivalence is desired, exclude pairs with too different application domains

### case_id=4537 FP long_range_semantics

- 方法: `readData` vs `convert`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `static_summary_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: readData initializes various sets and hash maps by parsing comma-separated token strings for Tibetan transliteration processing.
- B 摘要: convert converts an ACRNEMA stream file to DICOM format, handling pixel data and UIDs.
- 静态失败原因: The model likely over-generalized from high-level structural patterns (e.g., loops, conditionals, try-catch) and missed the fundamentally different semantics due to lack of domain understanding and long-range dependencies.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB labels non-clone because the functions have entirely different purposes and operate on different data domains, despite some superficial structural similarities.
- 共享行为: Both parse input (string tokens vs file stream) and populate data structures using loops and conditionals.
- 行为差异: Different domains: Tibetan transliteration vs medical image conversion.；readData uses static fields and no file I/O; convert performs file I/O and DICOM-specific operations.；Different target structures: sets/hash maps vs DICOM dataset and output stream.；Different input parsing: StringTokenizer vs DcmParser.
- 修正建议: Incorporate type and domain information.；Use attention mechanisms that better capture long-range semantic intent.；Train on more diverse negative examples to reduce structural overfitting.

### case_id=4538 FN lexical_or_api_overlap

- 方法: `testNetworkHTTP` vs `getContent`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Test method that makes multiple HTTP GET requests to hardcoded URLs, reading and discarding response lines.
- B 摘要: Utility method that executes an HTTP request and returns the response content as a string.
- 静态失败原因: Low token overlap (0.117) and different API classes (HttpURLConnection vs HttpClient) and different control flow patterns cause the static model to miss the functional similarity.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB labels as clone because both functions perform the high-level task of making HTTP requests and reading response content, despite differences in API and output handling.
- 共享行为: Both perform HTTP GET requests and read response lines using BufferedReader.
- 行为差异: A makes multiple requests and discards output; B makes a single request and returns output.；A uses HttpURLConnection; B uses Apache HttpClient.；A is void; B returns a string.；A hardcodes URLs with device data; B accepts a parameter.
- 修正建议: Use data flow analysis to capture I/O patterns.；Incorporate API mapping or abstraction.；Use models that understand high-level semantics from control flow structure.

### case_id=4539 FP lexical_or_api_overlap

- 方法: `createHTML` vs `SRWGuiClient`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Generates HTML page content for different page types (logo, home) by reading a CSS file and querying a database.
- B 摘要: Constructor for a Swing-based web browser that parses XML/XSLT from a URL and displays formatted HTML in a GUI window.
- 静态失败原因: Static BERT/GraphCodeBERT may have overemphasized lexical overlap (URL handling, BufferedReader, HTML strings) and missed the distinct control flow and purpose due to long/truncated code.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BigCloneBench typically marks non-clones when functions have different overall purpose despite some low-level similarities; here, one is a server-side HTML builder, the other a GUI browser constructor.
- 共享行为: Both read from a URL using BufferedReader and InputStreamReader.；Both build HTML strings by appending lines read from streams.；Both handle exceptions related to I/O.
- 行为差异: Function A is a private method returning an HTML string; Function B is a constructor initializing a GUI component.；Function A generates HTML based on a page type enum and database content; Function B reads an XML/XSLT URL and applies transformation.；Function A focuses on HTML generation for specific sections; Function B sets up a full browser window with navigation and styling.
- 修正建议: Incorporate structural similarity metrics like AST or CFG matching.；Use a model that captures global context and API call sequences rather than just token overlap.；Add attention to method signatures and surrounding class context.

### case_id=4540 FP lexical_or_api_overlap

- 方法: `googleImageSearch` vs `SRWGuiClient`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Searches Google Images for artist and album and extracts image URLs.
- B 摘要: Constructs a Swing browser GUI and loads/transforms XML content from a URL.
- 静态失败原因: The model likely over-focused on the common API usage patterns (URL, BufferedReader, InputStreamReader) and the similar structure of reading data line by line, while ignoring the overall purpose and context of the functions.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled not clones because the core functionality differs entirely, and the shared URL reading pattern is a common boilerplate that does not indicate meaningful similarity.
- 共享行为: Both open a URL and read its content using BufferedReader and InputStreamReader.；Both handle exceptions with try-catch blocks.
- 行为差异: Function A is a method for image search; Function B is a constructor for a GUI browser.；Function A parses HTML to extract image links; Function B handles XML/XSLT transformation and displays content in a JEditorPane.；Function A uses HttpURLConnection with User-Agent; Function B uses URL.openStream() and Swing components.；Function A has conditional execution based on artist change; Function B sets up full GUI layout and window sizing.
- 修正建议: Incorporate structural analysis to distinguish boilerplate from core logic.；Use abstract syntax tree (AST) matching to ignore common library usage patterns.；Train with more negative examples that share API usage but differ in functionality.

### case_id=4541 FN partial_functionality

- 方法: `testNetworkHTTP` vs `setBundleInfoName`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.75`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: A test method that performs multiple HTTP GET requests to various URLs, reading response lines without processing.
- B 摘要: A utility method that reads a configuration file from a URL, parses key-value pairs, and updates bundle names in a list.
- 静态失败原因: Static BERT models rely on token-level embeddings and may lack understanding of functional purpose beyond lexical similarity; low Jaccard similarity and different variable names/logic inside loops caused confusion.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as network I/O tasks that read from URLs, overlooking specific usage of data and focusing on similar control flow of URL opening and line reading.
- 共享行为: Both open a URL and read lines sequentially using BufferedReader.；Both handle IOException by printing stack trace.
- 行为差异: A sends multiple requests with different parameters; B makes a single request.；A discards all read lines; B parses each line to extract key-value pairs.；A returns void; B returns a boolean and modifies input list.
- 修正建议: Use data flow analysis to detect network I/O operations.；Incorporate task-level similarity (e.g., both are network read operations).；Use graph-based models that capture control and data flow.

### case_id=4542 FN partial_functionality

- 方法: `copy` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a file from source to destination using byte streams.
- B 摘要: Downloads a KMZ file from a URL and extracts its zip entries to files.
- 静态失败原因: Static BERT models rely heavily on token overlap (Jaccard 0.2857) and syntactic features. The different method names, signatures, and APIs (especially ZipInputStream) cause the model to treat them as different tasks, missing the underlying generic copy loop.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely labels this as a clone because both functions implement the core pattern of reading from an input stream and writing bytes to an output stream, which is considered a common I/O operation. BCB accepts broad Type-3/4 clones based on structural similarity.
- 共享行为: Read from an input stream and write bytes to an output stream in a loop using a buffer
- 行为差异: A is a simple file copy; B handles zip entries and multiple output files；B uses ZipInputStream and URL connection; A uses FileInputStream/FileOutputStream；B prints entry names; A does not
- 修正建议: Use data augmentation with diverse function pairs that share core patterns；Train on code clone detection with attention to substructure or data flow graphs；Incorporate examples of Type-3/4 clones from BCB

### case_id=4543 FP partial_functionality

- 方法: `doVersionCheck` vs `checkForUpgrade`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.85`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Checks for newer version of jEdit by comparing build numbers from a remote URL.
- B 摘要: Checks for software upgrades by querying a license server, parsing license status, and inserting upgrade records into a database.
- 静态失败原因: The model may have overgeneralized the 'version check' theme and focused on superficial similarities like using URL, BufferedReader, and showing messages, missing the deeper differences in data handling and side effects.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely considered them non-clones because they have distinct project-specific APIs, different control flow, and different side effects (one is a simple version check, the other involves license validation and database updates).
- 共享行为: Both fetch data from a remote URL via HTTP；Both read and parse lines from a BufferedReader；Both show messages to the user based on the check result
- 行为差异: doVersionCheck only compares build numbers; checkForUpgrade does license validation and database operations；doVersionCheck uses jEdit's property for URL; checkForUpgrade constructs URL with client version, MAC, unit ID；checkForUpgrade manages UI component visibility and interacts with a database；checkForUpgrade handles multiple upgrade entries and inserts them into a database table
- 修正建议: Improve training data with more negative examples of similar-themed functions with different implementations；Incorporate dataflow analysis to capture database interactions and UI changes；Use contrastive learning to distinguish between similar-looking but semantically different code

### case_id=4544 FN partial_functionality

- 方法: `testNetworkHTTP` vs `wordFrequency`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Performs multiple HTTP GET requests to various URLs and reads response lines without processing.
- B 摘要: Queries a web service for word frequency by replacing a placeholder and parsing the response for a numeric pattern.
- 静态失败原因: Static BERT/GraphCodeBERT likely focused on low token overlap (0.22), different method signatures, and distinct control flow (multiple loops vs conditional parsing), missing the higher-level functional commonality of HTTP reading.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label these as clones because both involve HTTP communication and reading from URLs, which falls under a broad 'network I/O' functionality type, accepting Type-4 or partial similarity.
- 共享行为: Both create URL objects from strings.；Both open HTTP connections and use BufferedReader to read response lines.；Both handle IOException and MalformedURLException.
- 行为差异: A performs multiple requests; B performs a single request.；A does not parse or return any data; B parses response for a pattern and returns an integer.；A is void; B has a return value.；A does not use regular expressions; B uses regex to match a pattern.
- 修正建议: Enhance model with dataflow analysis to capture shared network I/O operations.；Incorporate domain knowledge about common HTTP patterns.；Use hierarchical embeddings to represent functional roles like 'network reader'.

### case_id=4545 FN long_range_semantics

- 方法: `main` vs `callService`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.8`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Constructs a POST request with hardcoded parameters to RenRen API and prints the response.
- B 摘要: Makes a GET request using instance fields and stores the response in a field.
- 静态失败原因: Static BERT/GraphCodeBERT relies on token embeddings and low Jaccard similarity (0.117) fails to capture the functional similarity due to very different API calls and structure.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may consider both clones as they implement the same high-level behavior of making an HTTP request and reading the response, despite differences in HTTP method, parameter handling, and context.
- 共享行为: Both perform an HTTP request to a URL and read the response line by line.
- 行为差异: A uses POST, B uses GET.；A has hardcoded parameters, B uses instance fields.；A prints output, B stores in a field.；A does not handle exceptions, B catches MalformedURLException and IOException.
- 修正建议: Enhance model to recognize common web service patterns (e.g., HTTP request + read response) across different API usages.；Incorporate dataflow analysis to trace the sequence of operations like URL creation, connection, and reading.

### case_id=4546 FP lexical_or_api_overlap

- 方法: `getJSONData` vs `SRWGuiClient`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches JSON data from a URL using HTTP client and returns parsed JSONObject.
- B 摘要: Constructor for a Swing browser GUI that reads XML/HTML from a URL, optionally applies XSLT transformation, and displays it.
- 静态失败原因: Static BERT models may have been misled by common patterns such as opening URLs, reading lines, using BufferedReader, and exception handling. The overlapping API usage (e.g., URL, BufferedReader) could trigger a false positive even though the overall logic differs.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels these non-clones because the functionalities are entirely different: one is a JSON fetching utility, the other is a GUI browser constructor. Despite both involving URL reading, the core purpose and implementation are distinct.
- 共享行为: Both accept a URL string as input.；Both perform network I/O to read content from the URL.；Both read content line by line using BufferedReader.
- 行为差异: A returns a JSONObject; B is void and sets up a GUI.；A uses Apache HttpClient; B uses java.net.URL.；A parses JSON; B parses XML/HTML and applies XSLT.；A is a static utility method; B is a constructor of a GUI class.
- 修正建议: Use abstract syntax tree differencing to capture structural differences.；Incorporate data flow analysis to distinguish between JSON fetching and GUI construction.；Consider method signatures and class context for better differentiation.

### case_id=4547 FN partial_functionality

- 方法: `readGeoParserResult` vs `readReferenceText`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends an XML request to a geospatial service, parses the response, and returns a collection of place names with associated gazetteer IDs.
- B 摘要: Reads a reference text file from a plugin resource URL and returns its entire content as a string.
- 静态失败原因: Low lexical overlap (Jaccard 0.1377) and different method signatures, API calls, and return types prevent static token-based models from recognizing the shared I/O pattern. The models lack reasoning about control flow and common boilerplate structures.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider these clones because they share a common structural pattern of reading from a URL line-by-line and buffering content, which is a typical Type-4 similarity for I/O operations despite different specific processing and return types.
- 共享行为: Both open a URL stream and read lines using BufferedReader.；Both accumulate lines into a StringBuffer.；Both handle exceptions with logging or error output.
- 行为差异: Function A builds and sends an XML request, whereas B directly reads a file URL.；Function A parses XML to extract structured data; B returns raw text.；Function A returns a collection of tuples; B returns a single string.；Function A has retry logic; B throws a custom exception on failure.
- 修正建议: Enhance modeling with data flow or control flow graphs to capture structural patterns.；Incorporate API call sequences as features.；Add more training examples of I/O boilerplate clones with varied domain logic.

### case_id=4548 FN lexical_or_api_overlap

- 方法: `lookupFutureEvents` vs `CheckUrl`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.7`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches and parses Meetup events from a given group identifier, constructing Event objects.
- B 摘要: Fetches the first line of a given URL and returns it as a string.
- 静态失败原因: Static BERT / GraphCodeBERT likely focused on overlapping API tokens (URL, BufferedReader, etc.) but missed high-level semantic difference: one is a structured data fetcher/parser, the other is a simple URL checker.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may consider them clones due to similar boilerplate of HTTP GET and line-by-line reading, treating them as Type-3/4 partial functionality clones despite different overall goals.
- 共享行为: Opens an HTTP connection to a URL；Reads data using BufferedReader from InputStream；Uses similar Java networking and I/O classes
- 行为差异: A parses JSON into multiple Event objects; B returns raw string from first line only；A handles multi-line response; B only reads one line；A throws custom exception; B catches Exception and prints stack trace；A processes many JSON fields; B has no parsing logic
- 修正建议: Incorporate data-flow and control-flow to capture overall function purpose；Train on more diverse examples where API usage differs in intent；Use contrastive learning to separate similar API usage with different goals

### case_id=4549 FP boilerplate_overlap

- 方法: `getWebPage` vs `handleHandshake`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches the content of a web page as a string by reading line by line.
- B 摘要: Handles a Minecraft handshake packet by validating the username and potentially making an HTTP request to join a server.
- 静态失败原因: The static model likely overfitted on common API patterns (URL, BufferedReader) and exception handling structures, ignoring the high-level semantic difference.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would label this as a non-clone because the functions have entirely different purposes and control flow, despite sharing low-level I/O boilerplate.
- 共享行为: Both use URL.openStream() to open a network stream；Both read from the stream using BufferedReader
- 行为差异: Function A returns the concatenated content of the web page, while Function B performs validation and network shutdown decisions；Function A is a static utility method that throws an Error on failure; Function B is an instance method that handles exceptions locally and interacts with a network manager；Function B includes complex conditional logic and multiple paths for different username cases, which is absent in Function A
- 修正建议: Incorporate data flow and control flow features into the model；Use graph-based representations that capture the structure beyond token sequences

### case_id=4550 FN partial_functionality

- 方法: `getFile` vs `doCopyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies an endpoint in the XML, and saves it to a temporary file using NIO channels.
- B 摘要: Copies a file from source to destination using NIO FileChannel.transferFrom, with optional preservation of the file date.
- 静态失败原因: Low lexical overlap (0.134) due to different domain-specific strings, and the common transferFrom pattern is overshadowed by boilerplate, causing the model to miss the semantic similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels pairs with shared core file-copy logic as Type-4 clones, ignoring peripheral operations like download and XML modification.
- 共享行为: Both use FileChannel.transferFrom to copy file contents.
- 行为差异: Function A involves downloading WSDL from a URL and XML manipulation; B is purely local file copy.；Function A handles network and XML exceptions; B only handles IOException.；Function B optionally preserves the last-modified date; A does not.
- 修正建议: Use structure-based matching (e.g., AST or PDG) to isolate the file-copy subgraph.；Incorporate data-flow analysis to track channel usage.；Augment training with more NIO-centric positive examples.

### case_id=4551 FP lexical_or_api_overlap

- 方法: `handleHandshake` vs `fetchUrl`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Handles Minecraft handshake packet by validating username and contacting authentication server to join server.
- B 摘要: Generic utility to fetch entire content from a URL as a string, returning empty on failure.
- 静态失败原因: Static BERT/GraphCodeBERT may overemphasize lexical and API overlap (e.g., URL, BufferedReader, try-catch) and common programming patterns, missing the high-level semantic differences in purpose and data flow.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely annotates as non-clone because the functions serve entirely different purposes (authentication vs. generic URL fetching) and have distinct control flows, despite sharing some API calls.
- 共享行为: Both open a URL connection and read from it using BufferedReader；Both perform network I/O and handle exceptions
- 行为差异: handleHandshake performs authentication logic specific to Minecraft; fetchUrl is generic；handleHandshake reads only one line and checks if it equals 'ok'; fetchUrl reads all lines and concatenates；handleHandshake sends additional packets based on result; fetchUrl simply returns the content；Exception handling differs: fetchUrl suppresses exceptions silently; handleHandshake prints stack trace and shuts down network
- 修正建议: Incorporate data flow and call graph information to distinguish application logic；Use larger context of the containing class or project to infer intent；Train with more negative examples that share API calls but differ in functionality

### case_id=4552 FP boilerplate_overlap

- 方法: `copyFile` vs `readData`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.99`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Copies a file from source to destination using FileChannel.transferFrom.
- B 摘要: Reads and processes comma-separated string data to populate sets, maps, and internal structures for a Tibetan Wylie transliteration system.
- 静态失败原因: The static model likely focused on shared syntactic patterns (e.g., nested try-catch-finally, closing streams) and ignored the semantic gap, misclassifying due to boilerplate overlap.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically rejects clones that differ in input/output behavior and intention; here, A reads and writes files, B populates sets/maps, so they are not similar in functionality.
- 共享行为: Both use Java I/O and try-finally blocks for resource management
- 行为差异: Function A performs file copying; B initializes data structures from string fields；Function A operates on files; B operates on stored strings；Function A has a simple linear flow; B has complex multi-step parsing and conditional logic；Function A is stateless; B modifies several instance-level collections
- 修正建议: Improve token embeddings to distinguish between file I/O and data parsing；Add data-flow analysis to capture actual operations；Use control-flow structure but weight semantics more

### case_id=4553 FN partial_functionality

- 方法: `getResourceAsStream` vs `Converter`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a resource from a URL, caches it locally, and returns an InputStream, with conditional caching logic and HTTP handling.
- B 摘要: Reads a file in SJIS encoding and writes it to another file in UTF8 encoding, performing character encoding conversion.
- 静态失败原因: The token-level Jaccard similarity is low (0.19), so the model likely focused on token overlap and missed the structural similarity in the I/O loop. Static BERT/GraphCodeBERT models may not capture long-range structural patterns or partial functionality clones well, especially when the surrounding code (e.g., caching, HTTP) is very different.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label them as clones because both functions share a common pattern of reading from a stream and writing to another stream using buffered I/O, which is a typical Type-4 (similar functionality) scenario in BigCloneBench. The structural similarity in the core data copy loop and the use of similar APIs (BufferedInputStream/OutputStream, FileInputStream/OutputStream) outweighs the high-level semantic differences.
- 共享行为: Both read from an input stream (file or network) and write to an output stream (file).；Both use buffered streams and copy data in a loop.；Both close streams in a finally-like manner (try-catch).
- 行为差异: Function A handles URL fetching, caching, and HTTP responses; Function B does not deal with networking or caching.；Function A returns an InputStream; Function B is a constructor with no return value.；Function B explicitly specifies character encodings (SJIS and UTF8); Function A does not involve encoding conversion.；Function A has complex caching logic and multiple fallback paths; Function B is a straightforward file copy with encoding conversion.
- 修正建议: Train the model to recognize common I/O patterns (e.g., read-write loop, stream closing) even when the surrounding context differs.；Incorporate control-flow and data-flow features that capture the sequence of stream operations.；Use data augmentation to create more examples of partial functionality clones with different surrounding code.；Fine-tune on a dataset that includes Type-4 clones with varying high-level semantics but similar low-level stream handling.

### case_id=4554 FP lexical_or_api_overlap

- 方法: `createDialogArea` vs `getTicketsForQueue`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Creates a dialog area for displaying license text using a browser or text widget.
- B 摘要: Fetches open tickets for a given queue from a REST API and returns a list of tickets.
- 静态失败原因: The model likely focused on shared lexical patterns (e.g., BufferedReader, try-catch-finally) and ignored the overall semantic difference in purpose and data flow, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled these as non-clones because they have completely different functionality, despite some shared I/O patterns, and BCB generally requires significant overlap in purpose or behavior to consider Type-3/Type-4 clones.
- 共享行为: Both use BufferedReader to read input streams line by line.；Both include try-catch-finally blocks for resource management.；Both handle IOExceptions and other exceptions.
- 行为差异: Function A creates a GUI dialog area; Function B performs an HTTP GET request and parses ticket IDs.；Function A returns a Control (UI component); Function B returns a List<RTTicket>.；Function A reads from a local file (license.html/txt); Function B reads from an HTTP response.；Function A uses SWT GUI components; Function B uses Apache HttpClient and URL encoding.
- 修正建议: Incorporate data flow analysis to distinguish I/O boilerplate from core logic.；Use higher-level semantic features like method names, return types, and called APIs.；Increase training data with examples where shared boilerplate does not indicate clones.

### case_id=4555 FP lexical_or_api_overlap

- 方法: `readRemoteFile` vs `readZoneIDs`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: readRemoteFile reads a remote file and concatenates all lines into a single string.
- B 摘要: readZoneIDs reads integer IDs from a resource file and returns a HashSet of them.
- 静态失败原因: The model likely focused on overlapping API tokens (URL, openStream, readLine, IOException) and ignored the different data processing logic, causing a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would label as non-clone because the output type and functionality differ significantly, despite similar I/O setup. The core semantics (string concatenation vs integer collection) are distinct.
- 共享行为: Both read from a URL/resource line by line；Both use BufferedReader/LineNumberReader to read lines；Both handle exceptions
- 行为差异: readRemoteFile returns a concatenated string; readZoneIDs returns a set of integers；readRemoteFile reads first line separately and handles EOFException separately; readZoneIDs reads all lines in a loop and catches generic Exception；readRemoteFile appends lines to response string; readZoneIDs parses integers and adds to set
- 修正建议: Enhance model to capture data flow beyond API calls；Include type information of return values and processing steps；Use structural heuristics to distinguish boilerplate from core logic

### case_id=4556 FN benchmark_preference_bias

- 方法: `testReadPerMemberSixSmall` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Tests reading of GZIP members from a compressed byte array, verifying correct member counts and EOF behavior.
- B 摘要: Builds a website for editing by transforming XML pages, processing control files, and writing output files.
- 静态失败原因: The static model correctly identified non-clone; the BCB label is likely incorrect. If considered a failure, the model's low token overlap and clear semantic difference led to a correct non-clone prediction against a flawed annotation.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: The BCB annotation likely labels these as clones due to both involving I/O operations and loops, but this is a very broad interpretation; the functions have no functional overlap and belong to entirely different domains, so the BCB label appears erroneous.
- 共享行为: Both involve loops (one for members, one for pages)；Both use I/O streams (GZIPInputStream vs. FileInputStream)
- 行为差异: Function A is a unit test for GZIP member reading; function B is a site builder with complex file and XML transformations.；Function A uses a fixed byte array and NullOutputStream; function B reads from files, transforms XML, and writes to output paths.；Function A checks member counts; function B performs string replacement, debug tracing, and error handling.；Function A is short and straightforward; function B is long (truncated) and complex.
- 修正建议: Review BCB annotation for this pair; likely a labeling error.；Improve BCB guidelines to avoid over-generous cloning based on trivial I/O usage.

### case_id=4557 FN partial_functionality

- 方法: `downloadURLtoString` vs `fileDownload`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads content from a URL and returns it as a string.
- B 摘要: Downloads content from a URL and writes it to a file on disk.
- 静态失败原因: Static BERT methods like GraphCodeBERT rely heavily on lexical token overlap and shallow structural patterns. The functions have low token Jaccard (0.1667), different method signatures, return types, and additional file I/O in B, leading the model to miss the underlying common behavior of URL downloading.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this as a clone because both functions perform the core operation of downloading content from a URL, even though the output method (return vs. file) differs. The broad Type-3/Type-4 criteria often accept partial functionality similarity when the main logic is shared.
- 共享行为: Both open a URL connection and read data from it.
- 行为差异: A returns the content as a String; B writes the content to a file.；A reads using readLine and appends to StringBuffer; B reads using read and writes to OutputStream.；A has no error handling; B catches exceptions and logs them.；A takes a URL object; B takes a string address and parses it.
- 修正建议: Train models with more examples of partial functionality clones where output format differs.；Incorporate dataflow or dependency analysis to capture shared I/O patterns.；Use contrastive learning or specialized representations for I/O operations.

### case_id=4558 FN benchmark_preference_bias

- 方法: `runInternal` vs `readURL`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Reads an OPDS catalog from an HTTP URL with pagination, progress, and error handling.
- B 摘要: Reads lines from a URL and prints them to standard output.
- 静态失败原因: Low token overlap (Jaccard=0.084) and different method names likely caused the model to miss any semantic similarity, while BCB may have considered the shared I/O behavior as sufficient.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB annotators may have overemphasized the common action of reading from a URL, ignoring the vastly different purposes and complexities.
- 共享行为: Both open a URL and read textual data from it
- 行为差异: A handles HTTP headers, redirects, authentication, parses XML, and manages pagination; B only reads lines and prints.；A has complex error handling and progress updates; B has basic exception printing.；A uses callbacks and multiple components; B is a simple sequential reader.
- 修正建议: Improve annotation guidelines to avoid labeling semantically different functions as clones.；Use hierarchical or multi-level clone types to separate partial from full semantic clones.；Increase contextual understanding in models by considering data flow and method purposes beyond shared operations.

### case_id=4559 FN benchmark_preference_bias

- 方法: `readData` vs `load`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Reads configuration strings, tokenizes them, and populates multiple HashSet collections and a HashMap.
- B 摘要: Downloads XML from a URL and returns it as a concatenated string.
- 静态失败原因: The model correctly identified the lack of syntactic and semantic similarity (Jaccard=0.076). The false negative arises because the model's prediction (not clone) disagrees with a likely incorrect BCB label.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as a clone due to a broad interpretation of 'data loading' functionality, disregarding the specific I/O source and processing logic, or due to an annotation error.
- 共享行为: Both involve reading data from an external source.；Both handle IOException via catch blocks.
- 行为差异: readData parses local string tokens into structured sets, while load fetches network data and returns raw text.；readData populates multiple mutable static collections; load returns a string without side effects on global state.；readData operates on hardcoded global string variables; load takes a URL id parameter.；readData has complex parsing logic for multiple categories; load simply reads lines and appends.
- 修正建议: Re-annotate the pair in BCB to reflect true non-clone status.；Improve annotation guidelines to avoid overly broad functional equivalence.

### case_id=4560 FN benchmark_preference_bias

- 方法: `run` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Parses an XML input to build a XUL Firefox extension, creating a ZIP archive with chrome content, manifest, and icon.
- B 摘要: Builds HTML output for site editing by reading pages and applying XSLT transformations, writing results to files.
- 静态失败原因: A static BERT model likely failed to recognize the high-level structural similarity that BCB annotators might have considered (e.g., both are long methods with XML processing loops). However, given the low token Jaccard, the model correctly identified non-clone.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled them clones due to generic similarity (both process XML and write output), but the actual functionality and output are entirely different, and token overlap is very low.
- 共享行为: Both involve reading and writing files；Both perform XML parsing；Both handle exceptions from I/O operations
- 行为差异: Function A produces a ZIP archive; Function B writes individual files；Function A targets Firefox extension packaging; Function B targets CMS page rendering；Function A has a fixed set of outputs; Function B iterates over a dynamic page list；Function A uses DOM parsing; Function B uses XSLT transformations
- 修正建议: Improve training data to avoid labeling based on generic I/O patterns；Use more fine-grained semantic analysis to distinguish different transformation tasks

### case_id=4561 FN partial_functionality

- 方法: `copy` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a file from source path to destination path using FileInputStream and FileOutputStream.
- B 摘要: Retrieves a resource as an InputStream, with caching, HTTP URL handling, and fallback to a local file cache.
- 静态失败原因: Static BERT models rely on token-level similarities and structural features; the low token Jaccard and different method names, control flow, and complexity led the model to predict non-clone, missing the subtle shared IO pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have considered the generic stream-copying pattern as sufficient for a Type-4 clone, viewing function B as an enhanced version of function A. However, the overall semantics diverge significantly.
- 共享行为: Both use a while loop to copy bytes from an input stream to an output stream.；Both have try-finally blocks to close streams.；Both handle I/O operations.
- 行为差异: Function A performs a simple file copy; function B retrieves a resource from a URL or cache and returns an InputStream.；Function B includes HTTP connection, caching, and conditional logic based on file modification times.；Function B has multiple print statements for debugging; function A has none.；Function A writes to a specified destination file; function B writes to a cache file and returns a stream to the original resource or cache.
- 修正建议: Incorporate dataflow analysis to detect stream-copying subroutines.；Use partial clone detection techniques that match common subgraphs.；Improve representation of nested functionality and long-range dependencies.

### case_id=4562 FN lexical_or_api_overlap

- 方法: `modifyApplicationMessage` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.8`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Modify a properties file for a given locale by adding or updating a message key-value pair.
- B 摘要: Parse command-line arguments and convert an input file to an output file with specified encoding and format.
- 静态失败原因: Low token Jaccard (0.2049) and different API usage (Properties vs CmdLineParser, etc.) cause GraphCodeBERT to miss the structural similarity in file read-write patterns.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may label as clone due to high-level similarity in file I/O structure, both performing 'modify file' operations with missing file handling, despite different domains.
- 共享行为: Read from files and write to files；Handle missing files by creating or falling back；Use try-catch blocks with printStackTrace exception handling
- 行为差异: A operates on properties files; B operates on arbitrary files with format conversion；A modifies a specific key-value pair; B transforms file content；A copies a template file if locale file missing; B creates output file if missing；A writes back to the same file; B writes to a different output file
- 修正建议: Incorporate data-flow and control-flow graphs to capture file I/O structure；Use models that abstract over specific APIs to focus on general operations like file reading/writing

### case_id=4563 FN other

- 方法: `forBundle` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Manipulates OSGi bundles by finding .vm files, creating a JAR, and installing it as a plugin.
- B 摘要: Builds a website for editing by processing pages, applying XSLT transformations, and writing output files.
- 静态失败原因: The static model likely relied on token overlap and API usage, which are very different, so it correctly predicted non-clone. However, BCB labels it as clone, so the static method did not capture the broad BCB sentiment.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB might have considered both as involving file processing and resource iteration, but the specific functionality is entirely different.
- 共享行为: Both use file I/O and streams；Both use loops to process collections
- 行为差异: One operates on OSGi bundles and plugin installation; the other on website page rendering；Different libraries and APIs (BundleManipulator vs XSLT transformers)；Different output (JAR file vs HTML file)
- 修正建议: Improve annotation consistency in BCB；Use finer-grained functional similarity measures

### case_id=4564 FN benchmark_preference_bias

- 方法: `doGet` vs `streamContains`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Handles HTTP GET requests to retrieve and render a portal page with permission checks, logging, and caching.
- B 摘要: Checks if a given string is contained within an InputStream's UTF-8 content, used for testing.
- 静态失败原因: The static model failed to detect a non-existent clone; its prediction of 0 (non-clone) is actually correct given the low similarity and unrelated functionality, but the benchmark considered it a false negative due to a likely mislabeled ground truth.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have incorrectly labeled this as a clone due to a systematic annotation error or overly broad interpretation of Type-4 clones, possibly considering both as 'data processing' functions, but the actual behaviors are entirely unrelated.
- 共享行为: Both involve reading or processing data streams indirectly?
- 行为差异: Function A is a servlet handler managing HTTP requests, user permissions, and page rendering; Function B is a test utility for string containment.；Function A has complex control flow with multiple exception handlers and conditional logging; Function B is a simple utility with a single assertion.；Token Jaccard similarity is extremely low (0.028) indicating negligible lexical overlap.
- 修正建议: Review and verify BCB annotations for this pair to correct potential labeling errors.；Use ensemble or cross-validation of multiple clone detection tools to validate ground truth.

### case_id=4565 FN partial_functionality

- 方法: `main` vs `loadBinaryStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a ZIP file from a given URL and extracts its entries to local files.
- B 摘要: Copies an input stream to an HTTP response output stream, setting content headers.
- 静态失败原因: Static models may have focused on the different method signatures, variable names, and high-level API calls (ZipInputStream vs BufferedOutputStream, URL vs HttpServletResponse), missing the abstract stream-copying pattern. The low token overlap also misled the model to consider them dissimilar.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considered both as instances of 'copying a binary stream from input to output', a common semantic pattern, ignoring the specific protocols and file extraction logic.
- 共享行为: Both read from an InputStream and write to an OutputStream using buffered streams.；Both close the input and output streams after use.
- 行为差异: Function A extracts ZIP entries, while Function B simply copies the raw stream.；Function A handles URL protocols and file I/O, while Function B sets HTTP response headers.；Function A writes to multiple local files, while Function B writes to a single HTTP response.
- 修正建议: Incorporate structural alignment to abstract common I/O patterns.；Use data-flow analysis to identify that both involve reading and writing streams.；Include more examples of stream-copy clones with different APIs.

### case_id=4566 FN benchmark_preference_bias

- 方法: `main` vs `addRecord`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.7`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a specific KMZ file from a URL and extracts its zip entries to files.
- B 摘要: Reads an InputStream, copies it to a temporary file while computing a digest, and stores the data in a deduplicated file store.
- 静态失败原因: The token overlap is very low (Jaccard 0.132) and the API usage differs significantly (ZipInputStream vs DigestOutputStream). Static BERT models likely failed due to lack of understanding of the broad functional similarity in data copying, focusing instead on the distinct domain-specific keywords (e.g., 'kmz', 'zip' vs 'digest', 'datastore').
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as a clone because both functions perform streaming copy from an input to an output, a common low-level pattern considered Type-4 partial functionality similarity, despite different high-level purposes.
- 共享行为: Both read from an InputStream；Both write to an OutputStream using buffering；Both handle IO exceptions；Both involve file I/O operations
- 行为差异: Function A is a main method with hardcoded URL; B is a method taking an InputStream；A specifically processes ZipEntries; B handles raw bytes and uses hashing for deduplication；B includes collision detection and file renaming logic not present in A；A extracts multiple files; B stores a single record with integrity check
- 修正建议: Incorporate control flow and data flow analysis to capture common patterns like input-to-output copying；Use code summarization to extract high-level intent；Train with more diverse clone pairs that include partial functionality similarities

### case_id=4567 FN benchmark_preference_bias

- 方法: `main` vs `copy`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a URL and extracts the entries of the zip archive to files.
- B 摘要: Copies a file from a source path to a destination path using NIO FileChannel and memory-mapped buffer.
- 静态失败原因: The static model likely relied on lexical and syntactic overlap, which is low (token Jaccard 0.189). It failed to recognize any potential high-level similarity that BCB might have assumed because the code structures and APIs are completely different.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have considered both as file copying or data transfer utilities, but the actual tasks are fundamentally different. This pair might be an annotation error or an overly broad interpretation.
- 共享行为: Both perform file I/O operations involving reading and writing data.
- 行为差异: Code a reads from a URL and extracts a zip archive; code b copies a single file.；Code a uses zip streams; code b uses FileChannel and MappedByteBuffer.；Code a writes multiple output files; code b writes a single output file.；Code a includes print statements; code b does not.
- 修正建议: Incorporate high-level task descriptions or functional signatures into the model.；Use contrastive learning with broader clone definitions to capture abstract similarity.；Include more diverse examples of Type-4 clones.

### case_id=4568 FN boilerplate_overlap

- 方法: `main` vs `extractFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a URL, unzips each entry, and writes them to separate files.
- B 摘要: Reads the entire contents of a source file and writes them to a destination file.
- 静态失败原因: Static BERT/GraphCodeBERT likely failed due to low token overlap (Jaccard 0.216) and different method names ('main' vs 'extractFile'), causing the model to underestimate the structural similarity. The model may rely heavily on surface-level tokens and miss the shared stream-processing pattern.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely labels this as a clone because both functions perform a generic 'stream copy' pattern: reading bytes from an input source and writing them to an output destination, despite the different sources and the unzipping step in function a. BCB often accepts Type-3/4 clones with similar algorithmic structure and I/O handling.
- 共享行为: Both use buffered I/O to read from an input stream and write to an output stream byte by byte.；Both involve file output operations.；Both handle streaming data with a loop that reads and writes chunks.
- 行为差异: Function a downloads from a URL and unzips; function b reads a local file directly.；Function a produces multiple output files (one per zip entry); function b produces a single output file.；Function a uses ZipInputStream; function b uses FileReader (which wraps FileInputStream).；Function a includes URL protocol handling; function b does not.
- 修正建议: Use data augmentation to emphasize I/O boilerplate patterns as clone indicators.；Incorporate structural features like control-flow graph or data-flow dependencies to capture the read-write loop.；Introduce a specialized token for stream copy idioms.

### case_id=4569 FN partial_functionality

- 方法: `read` vs `retrieveTemplate`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a file or URL by name and returns a status code indicating success or failure.
- B 摘要: Retrieves a cached template string from a fixed URL, returning the content or throwing an exception.
- 静态失败原因: The low token Jaccard (0.17), different method names, parameter lists, return types, and control flow caused static models to miss the shared URL-reading behavior, as they rely heavily on lexical and structural similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely labeled this as clone because both functions involve reading data from a URL, which is a high-level functional similarity considered in Type-3/Type-4 clones, despite differences in input, output, and implementation details.
- 共享行为: Both can read content from a URL using URL.openStream()；Both use input streams to read data
- 行为差异: A returns an integer status code, B returns a string；A handles both file and URL inputs, B only URL；A does not cache results, B caches the template；A uses BufferedInputStream (binary), B uses BufferedReader (text)
- 修正建议: Enhance model to recognize common API usage patterns (e.g., URL.openStream()) as indicators of similar functionality.；Incorporate dataflow or control-flow analysis to capture high-level intent beyond lexical tokens.；Train on more diverse semantic clone examples with low lexical similarity.

### case_id=4570 FN boilerplate_overlap

- 方法: `doVersionCheck` vs `invoke`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Checks for a new software version by fetching a version file from a URL and comparing build numbers, showing a UI message.
- B 摘要: Invokes a remote service method via HTTP POST, reads and deserializes the JSON response, with retry on timeout.
- 静态失败原因: Static BERT/GraphCodeBERT likely failed due to low token overlap (Jaccard=0.16) and different method names/types, missing the structural boilerplate similarity.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may consider them Type-3 clones because both implement a common pattern of network I/O with text parsing and error handling, despite different domains.
- 共享行为: Both open an HTTP connection and read lines from a BufferedReader.；Both handle IO exceptions with error reporting or throwing.；Both use InputStreamReader and read lines in a while loop.
- 行为差异: A uses GET request (URL.openStream), B uses POST with JSON payload.；A compares version strings and shows UI dialogs; B deserializes JSON and returns an object.；A has no retry logic; B has retry on ConnectTimeoutException with service discovery.；A is static and takes a View; B is instance method and takes MethodInvocation and retry count.
- 修正建议: Use dataflow analysis to capture the common URL reading pattern.；Train on clone pairs with low token similarity but high structural similarity.；Incorporate control-flow or API usage graphs to detect boilerplate clones.

### case_id=4571 FN benchmark_preference_bias

- 方法: `getFile` vs `buildDeb`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies an XML attribute to set an endpoint, and saves it to a temporary directory.
- B 摘要: Builds a Debian package (.deb) by writing a header and copying control and data files into an archive file.
- 静态失败原因: Static BERT models rely on surface-level token and structural patterns; the low token overlap (0.095) and completely different domain-specific vocabulary (WSDL vs. Debian) likely caused the false negative. The models may lack understanding of long-range semantic intent.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have considered both as clones because they involve file I/O with similar stream-handling patterns (reading/writing files, using FileInputStream/FileOutputStream). However, this is too broad and not typical Type-3/4 similarity.
- 共享行为: Both perform file I/O operations using streams and channels.；Both handle IOException and involve temporary file manipulation.
- 行为差异: Function A downloads content from a remote URL and processes XML, while Function B simply copies local files into an archive.；Function A modifies XML attributes and validates existing files; Function B has no conditional file existence logic.；The overall purpose (web service client vs. package creation) is completely different.
- 修正建议: Incorporate deeper semantic understanding of the task (e.g., using code summarization or API call intent).；Augment training with more examples where functions have low lexical overlap but are actually non-clones.

### case_id=4572 FN partial_functionality

- 方法: `readGeoParserResult` vs `fetchUrl`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads geo-parser results by constructing an XML request, sending it to a URL, parsing the XML response, and extracting place names with optional gazetteer IDs, with retries on failure.
- B 摘要: Fetches the content of a URL as a single string, returning empty string on error.
- 静态失败原因: Static BERT methods rely on token-level similarity; the low Jaccard index (0.1458) and different method names likely caused a non-clone prediction, while BCB considers the shared URL-reading subpattern as sufficient for clone classification.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this as a Type-4 clone because both functions share a core pattern of reading from a URL line by line, which is a common functionality despite differences in input/output and additional processing.
- 共享行为: Both open a URL connection and read lines using BufferedReader
- 行为差异: A constructs an XML request and parses the response; B simply returns the raw string.；A has retry logic (up to 3 times) and error logging; B has no retry and minimal error handling.；A returns a Collection of Tuples; B returns a String.；A has a testing mode that returns a dummy result; B does not.
- 修正建议: Incorporate functional subgraph matching to detect common patterns like URL reading.；Use a model that can learn hierarchical functional similarity, not just lexical overlap.；Consider multi-level clone detection that allows partial functionality clones.

### case_id=4573 FN partial_functionality

- 方法: `main` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from an HTTP URL and extracts its entries to files.
- B 摘要: Copies a file from one location to another using FileChannel.
- 静态失败原因: Static models rely on token overlap and structural similarity; these functions have low token Jaccard (0.173) and different control flows, so the model likely saw insufficient similarity to predict a clone.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as file transfer/copy operations with different sources and mechanisms, labeling as Type-4 clone due to shared high-level functionality.
- 共享行为: Both read from an input source and write to an output file.；Both involve file I/O operations.
- 行为差异: A involves downloading from a URL and unzipping; B copies a local file.；A handles multiple entries from a ZipInputStream; B handles a single file via FileChannel.；A uses streams; B uses channels.；A prints progress; B does not.
- 修正建议: Improve model's ability to recognize abstract functional similarity beyond lexical overlap.；Use dataflow or dependency graphs to capture common I/O patterns.

### case_id=4574 FN partial_functionality

- 方法: `copyResource` vs `loadDefaultSettings`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource from a URL or file to a destination file using a byte-by-byte loop.
- B 摘要: Copies a default configuration file from the classpath to a file using IOUtils.copy.
- 静态失败原因: Low token overlap (0.14), different method names, and distinct API usage (manual loop vs IOUtils) misled the static embedding into treating them as unrelated, missing the semantic similarity in dataflow.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels partial functionality similarity as clones, especially when core behavior (stream copy) is shared, despite differences in source and error handling.
- 共享行为: Both copy data from an input stream to an output stream；Both handle closing streams (manually or via IOUtils)；Both produce a file as output
- 行为差异: Source retrieval: URL/file vs classpath resource；Error handling: throws Exception vs catch/log/wrap；Copy implementation: manual loop vs IOUtils.copy
- 修正建议: Incorporate dataflow analysis to capture stream copy pattern；Use contrastive learning on functional behaviors rather than surface tokens；Add synthetic examples of variant implementations of the same operation

### case_id=4575 FP long_range_semantics

- 方法: `readData` vs `displayDiffResults`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.2`
- 推荐路线: `static_summary_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Parses and initializes data structures (sets and maps) from comma-separated value strings and file input.
- B 摘要: Generates an HTML report of file difference metrics and displays it in a browser.
- 静态失败原因: Despite low token overlap, the model may have been misled by superficial structural patterns like nested loops and conditionals, or it failed to capture the long-range semantic context.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB labeled this as non-clone because the functions have entirely different semantics and no functional overlap.
- 共享行为: Both involve string manipulation and I/O operations；Both have loops and conditionals
- 行为差异: Completely different purposes: one reads and stores data, one writes formatted HTML output；Different I/O patterns: A uses StringTokenizer and file input, B uses BufferedWriter and file output；Different data structures: A manipulates HashSets and HashMaps, B generates HTML tables
- 修正建议: Improve model to capture high-level semantics via graph-based or hierarchical representations；Use contrastive learning with better negative examples

### case_id=4576 FP lexical_or_api_overlap

- 方法: `populateResources` vs `readScalarpvviewerDocument`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.99`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Loads template files and images from resources, creates and saves resource objects.
- B 摘要: Reads a scalar PV viewer document from a URL, parses XML to configure viewer settings.
- 静态失败原因: Static BERT or GraphCodeBERT likely over-emphasized the lexical and API-level similarities (e.g., both use BufferedReader, openStream, readLine, try-catch) while ignoring the high-level semantics and different domain contexts (resources vs. viewer configuration).
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the functions have distinct purposes and very low token overlap (0.125). Despite both performing file I/O, their semantic roles are unrelated.
- 共享行为: Both open and read from a URL stream；Both use BufferedReader to read lines；Both handle IOException
- 行为差异: Function A loads and saves templates and images, while B parses an XML configuration file to set up a viewer；Function A iterates over templates and processes .xml/.txt files, B specifically parses XML with predefined structure for scalars and UI；Function A creates Resource, Image, and Property objects, while B sets UI components like title, font, panel titles, and updates controllers；Function A is static and throws BasicException, B is an instance method and catches IOException with a different error message
- 修正建议: Incorporate structure-aware representations (e.g., data flow, control flow) to distinguish different business logic；Use contrastive learning to reduce false positives from boilerplate API usage；Enhance training with more diverse non-clone pairs that share common libraries but differ in intent

### case_id=4577 FN partial_functionality

- 方法: `copy` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Copies a file from source to destination using NIO FileChannel and MappedByteBuffer.
- B 摘要: Launches a NexOpen project configuration, which includes copying a reverse engineering file from a bundle resource to the project directory.
- 静态失败原因: Static BERT/GraphCodeBERT models likely failed because the token overlap is very low (0.059), the methods have different names, and the length disparity is huge. The shared sub-functionality (copy) is dwarfed by the surrounding code and domain-specific APIs, making it hard for the model to detect the semantic similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this as a clone because both functions perform a file copy operation, even though the contexts differ significantly and function B's copy is a minor part of a larger task. BCB's Type-4 (partial similarity) tolerance allows such broad functional overlap to be considered a clone.
- 共享行为: Both involve copying file content from a source to a destination (function A copies an entire file; function B copies a resource file to a project directory).；Both use finally blocks to ensure resources are closed (e.g., closing channels, setting persistent properties).
- 行为差异: Function A is a simple, isolated file copy. Function B is a complex launch procedure for an Eclipse project with many environment checks, property handling, and XML processing.；Function A uses direct NIO mapping; Function B uses IOUtils.copy from InputStream to ByteArrayOutputStream then to file.；Function B has many additional side effects like setting project persistent properties, checking for project type, and handling exceptions.
- 修正建议: Use dataflow-aware or graph-based models that can capture common subroutines even in vastly different contexts.；Consider augmenting training with partial functionality examples or using clone detection that focuses on subgraph matching.

### case_id=4578 FN benchmark_preference_bias

- 方法: `doGet` vs `WebmillDeploy`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.85`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Handles HTTP GET requests to retrieve and display a portal page based on a parameter, with access control and caching.
- B 摘要: Constructor that reads a WAR/JAR file, parses XML configurations (web.xml, portlet.xml), and creates a new WAR file for deployment.
- 静态失败原因: The models likely relied on token similarity and API usage, which are low (Jaccard=0.128). The BCB label may be an annotation error or reflect a very lenient clone definition, causing a false negative.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: Although functionally very different, both functions involve I/O and are from the same general web application domain, which might lead BCB annotators to consider them as partial clones under a broad interpretation (Type-4).
- 共享行为: Both involve input-output operations and error handling
- 行为差异: Function A is a servlet method handling HTTP requests; Function B is a constructor for file transformation.；A deals with page rendering and user permissions; B deals with XML parsing and JAR file manipulation.；A uses HttpServletRequest/Response; B uses FileChannels and JarOutputStream.；A has extensive logging and caching logic absent in B.
- 修正建议: Verify BCB annotation for correctness; consider using domain-specific or functionality-aware features beyond token overlap.

### case_id=4579 FP partial_functionality

- 方法: `addDataFromURL` vs `loadURL`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads URL content and appends each line to a text field with basic error handling.
- B 摘要: Reads URL content with optional authentication, writes to a temporary file, and updates a status label.
- 静态失败原因: Static BERT/GraphCodeBERT likely relied on lexical and API overlap (e.g., URL, BufferedReader, readLine, try-catch) and the similar control flow of reading lines, ignoring the divergent functional context like file writing, authentication, and UI updates.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely classified as non-clone because the core behavior differs significantly: one accumulates data in memory, the other writes to file with authentication and progress updates. The shared reading loop is a common sub-task but not sufficient for clone classification.
- 共享行为: Both open a URL stream and read lines using BufferedReader and readLine loop.；Both handle newlines by appending "\n" to each line.
- 行为差异: Function A appends to a field (thetext); Function B writes to a temporary file.；Function B includes optional HTTP Basic authentication; Function A does not.；Function B updates a UI status label with file size; Function A does not.；Function B throws IOException; Function A catches Exception and prints to stdout.
- 修正建议: Incorporate dataflow analysis to track how the read data is used (appended vs written to file).；Use graph models that capture method calls and their parameters (e.g., FileWriter, setRequestProperty).；Include token-level attention to distinguish between different output destinations.

### case_id=4580 FN partial_functionality

- 方法: `copyResource` vs `convert`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource from a URL or file to a destination file by reading byte by byte.
- B 摘要: Converts a DICOM file by parsing it, checking conditions, and writing a modified DICOM file with pixel data handling.
- 静态失败原因: Static BERT/GraphCodeBERT likely focused on the low lexical overlap and the domain-specific terms in function B (DICOM, pixel data), missing the common I/O pattern. The long length and complexity of function B may have diluted the representation of the shared byte-copying loop.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as Type-4 clones because they share the high-level functionality of reading from a source and writing to a destination, despite the detailed differences. The annotation guidelines often accept broad functional similarity, especially for file I/O operations.
- 共享行为: Both read from an input stream and write to an output stream.；Both close streams after operation.；Both handle IOException.
- 行为差异: A does simple byte copy; B performs DICOM-specific parsing and conditional conversion.；B checks file format, UIDs, and pixel data length; A has no such checks.；B may inflate 12-bit pixel data to 16-bit; A does not transform data.；B writes additional metadata (StudyInstanceUID, etc.); A does not.
- 修正建议: Incorporate structural features like AST-based data flow to capture the read-write loop.；Use a model that better handles long-range dependencies to see the overall purpose.；Augment training data with pairs that have low lexical overlap but high functional similarity.

### case_id=4581 FN boilerplate_overlap

- 方法: `login` vs `loadMFileViaWeb`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Logs into LOLA by sending credentials via HTTP POST and returns the session ID.
- B 摘要: Loads a .m file from a URL, reads its content line by line, parses it into a UserFunction object.
- 静态失败原因: Static BERT/GraphCodeBERT may have focused on functional purpose and return types, missing the shared I/O boilerplate due to low lexical overlap and emphasis on semantic roles.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely considers these clones due to structural similarity in HTTP/URL I/O patterns (URL, BufferedReader, try-catch), which qualifies as a Type-3 or Type-4 clone under their annotation guidelines.
- 共享行为: Both open a URL and read data using BufferedReader.；Both use try-catch for exception handling.；Both include debug logging statements.
- 行为差异: Function A writes POST data, Function B only reads.；Function A extracts a session ID from the first line; Function B accumulates all lines.；Return types differ: String vs UserFunction.；Exception handling: A returns empty string, B throws custom exception.
- 修正建议: Incorporate structural similarity metrics like control flow graphs.；Use dataflow analysis to detect common I/O patterns.；Train on diverse examples of boilerplate code to recognize cross-functional similarities.

### case_id=4582 FN partial_functionality

- 方法: `unJarStart` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Extracts jar entries starting with a given prefix to a local directory.
- B 摘要: Builds a web site for editing by processing XML and files, performing transformations and writing output files.
- 静态失败原因: The low token Jaccard (0.05) and vastly different method names and code structures mislead static models into predicting non-clone, as they cannot abstract to the high-level file processing pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider these Type-4 clones because both are file processing methods that read input, transform, and write output, sharing a high-level pattern despite very different low-level implementations.
- 共享行为: Both read from a source (jar or filesystem) and write files to a target directory.；Both loop over a collection of items (jar entries or pages).；Both perform file I/O operations (creating directories, copying/writing files).
- 行为差异: A iterates over jar entries, B iterates over pages and performs complex XML transformations.；A uses JarFile and IOUtils, B uses FileSystem, DOM, and XSLT.；B has many parameters and extensive error handling and debugging output.；B writes files with dynamic names and options, A uses entry names directly.
- 修正建议: Train models on more abstract representations like API call sequences or data flow graphs.；Incorporate file I/O and loop patterns as features.；Use graph-based models that capture high-level control flow similarities.

### case_id=4583 FN dataflow_blindspot

- 方法: `copy` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `dynamic_equivalence_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Copies a file to another file using FileChannel transferTo.
- B 摘要: Retrieves a resource as an InputStream from a URL, caching it locally if not already cached.
- 静态失败原因: The model likely relied on lexical token overlap, which is low, and did not capture the abstract dataflow similarity. It may have been misled by different method signatures, control flow, and exception handling patterns.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行价值高：该样本可能是 API 写法不同但行为等价的漏报。建议测试目标为 input_output_equivalence。
- BCB 偏好解释: BCB may label this as clone because both perform data transfer from an input to a file, which could be considered a Type-4 semantic clone. However, the functionalities are quite different in purpose and complexity.
- 共享行为: Both involve reading from an input source and writing bytes to a file output.
- 行为差异: A directly copies one file to another; B retrieves from URL, handles HTTP, checks cache, and returns an InputStream.；B has caching logic and network handling; A is purely local file copying.；B returns an InputStream, A returns a File object.
- 修正建议: Enhance models with dataflow analysis to detect common I/O patterns.；Use program dependency graphs to capture long-range data transfers.；Incorporate method-level documentation or functional annotations.

### case_id=4584 FP lexical_or_api_overlap

- 方法: `handleHandshake` vs `getVersion`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Processes a handshake packet by validating a username and optionally making an HTTP request to session.minecraft.net to authenticate the session.
- B 摘要: Fetches the latest version string from a remote URL (kmttg.googlecode.com) and returns it.
- 静态失败原因: The model likely relied on superficial lexical overlap (URL, BufferedReader, try-catch) and missed the broader semantic context and differing goals.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clones when functions have distinct purposes despite shared API usage; the overall functionality and control flow are too different.
- 共享行为: Both open HTTP connections and read from URLs using BufferedReader.
- 行为差异: handleHandshake performs handshake validation with side effects (sending packets, shutting down); getVersion simply returns a version string.；handleHandshake has complex conditional logic and multiple network interactions; getVersion is a straightforward fetch.；handleHandshake depends on external state (mc.session); getVersion is stateless.
- 修正建议: Train with more contrasting examples to distinguish shared I/O patterns from semantic similarity.；Incorporate structural or dataflow analysis to capture function-level intent.

### case_id=4585 FN benchmark_preference_bias

- 方法: `doGet` vs `getResponse`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Handles HTTP GET request for portal pages with complex logic including page retrieval, visibility checks, logging, caching, and error handling.
- B 摘要: Parses a raw HTTP GET request byte array and returns the requested static resource as a byte array response.
- 静态失败原因: The static model likely focused on the low lexical overlap (token Jaccard 0.077) and different method signatures, missing the high-level functional similarity of HTTP request handling.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might label these as clones under a broad Type-4 interpretation because both functions handle HTTP GET requests and produce responses, despite differing in domain and complexity.
- 共享行为: Both extract a resource identifier from an HTTP GET request；Both generate HTTP responses including status codes and content；Both handle cases where the resource is not found
- 行为差异: Code A operates in a servlet context with session, permissions, and portal-specific logic; Code B is standalone static file serving；Code A writes to an HttpServletResponse object; Code B returns a byte array；Code A includes extensive logging, caching, and page visibility checks; Code B is minimal
- 修正建议: Include functional abstraction features such as API call sequences or control flow patterns；Train with broader clone definitions that allow for domain differences

### case_id=4586 FP boilerplate_overlap

- 方法: `sendPost` vs `scrapeForIsbns`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Sends an HTTP POST request with parameters and returns the response body as a string.
- B 摘要: Scrapes a URL for ISBN-10 patterns, counting matches and storing them, with retry logic.
- 静态失败原因: The model likely overemphasized the overlapping boilerplate code (opening a URL, creating BufferedReader, reading lines) and common API classes (URL, BufferedReader, InputStream, etc.), leading it to ignore the functional differences in I/O direction and logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the functions have distinct purposes (send vs scrape), different return types (String vs int), and fundamentally different control flow despite shared boilerplate for reading from a URL.
- 共享行为: Both open a URL connection and read lines from an input stream.；Both use BufferedReader to read data.；Both handle exceptions (though differently).
- 行为差异: sendPost writes parameters to the output stream (POST request), while scrapeForIsbns only reads (GET request).；sendPost returns the entire response as a string, scrapeForIsbns returns an integer count of matched patterns.；scrapeForIsbns includes retry logic for connection failures; sendPost does not.；scrapeForIsbns uses regex to parse lines; sendPost does not.
- 修正建议: Incorporate data-flow analysis to track whether output streams are used (distinguishing send vs receive).；Use method signatures and return types as additional features.；Add attention to exception handling patterns and retry logic.

### case_id=4587 FN partial_functionality

- 方法: `login` vs `executeHttpGet`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Logs into a service by sending POST credentials, reads response to extract session ID, and handles errors by returning empty string.
- B 摘要: Executes an HTTP GET request to a given URI and returns the response body parsed as JSON, propagating exceptions.
- 静态失败原因: Static BERT/GraphCodeBERT relies on token overlap and structural similarity; with a token Jaccard of only 0.09 and different APIs (URLConnection vs HttpClient) and distinct processing logic, the model easily distinguishes them as non-clones, missing the broader functional similarity that BCB might accept.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as HTTP client operations that open a connection, read response data, and return a result, emphasizing the common functional goal despite different API usage and processing details.
- 共享行为: Both perform an HTTP request (POST vs GET)；Both read the response line by line using BufferedReader
- 行为差异: Different HTTP methods: POST vs GET；Different response processing: extract session ID vs parse JSON；Different error handling: catch return empty string vs throw Exception；Different HTTP APIs: URLConnection vs HttpClient
- 修正建议: Include more training examples of functional clones with low lexical overlap but similar intent (e.g., different HTTP libraries).；Incorporate code summarization or high-level semantic embeddings to capture shared behavior.；Use dataflow or control-flow graphs to abstract API-specific details.

### case_id=4588 FN partial_functionality

- 方法: `copyResource` vs `CopyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.95`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource from URL or file to a destination file using byte-by-byte stream copy.
- B 摘要: Copies a file from source path to destination path using NIO FileChannel, with directory creation and error logging.
- 静态失败原因: Low token Jaccard (0.125) and reliance on surface forms; cannot capture high-level semantic similarity when API usage differs (stream vs channel).
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB treats functions performing the same high-level operation (file copy) as clones, even if implementation details differ, prioritizing functional similarity.
- 共享行为: Both copy file content from source to destination using Java I/O
- 行为差异: A uses InputStream/OutputStream byte-by-byte; B uses FileChannel.transferFrom；A handles source via URL or file; B only file path；A does not create directories; B creates parent directories；A returns void; B returns destination path
- 修正建议: Use data augmentation with program transformation to learn functional equivalence across different I/O APIs；Employ graph-based models that capture data flow and resource handling

### case_id=4589 FN benchmark_preference_bias

- 方法: `modifyApplicationMessage` vs `getZipAsFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Modifies a properties file by updating or adding a key-value pair for a specific locale, creating a locale-specific file if missing.
- B 摘要: Converts a DigitalObject's content into a temporary zip file and returns the file.
- 静态失败原因: Static BERT model correctly identified low token and API overlap, but BCB's annotation is likely a false positive, so the model didn't actually fail; it correctly predicted non-clone.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled as clone due to both being file utility methods with similar exception handling, but this is too broad and not functional equivalence.
- 共享行为: Both involve file creation and I/O operations.；Both handle exceptions using try-catch blocks.
- 行为差异: Different inputs and outputs (void vs File).；Different file formats: properties vs zip.；A reads from resource and writes properties; B reads from input stream and writes binary.
- 修正建议: Re-evaluate BCB annotation for this pair.；Consider using functional similarity metrics beyond token overlap.

### case_id=4590 FP lexical_or_api_overlap

- 方法: `decodeFileToFile` vs `readData`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Decodes a Base64-encoded file and writes the decoded content to an output file.
- B 摘要: Parses a configuration file to populate various sets and lookup tables for Tibetan Wylie transliteration.
- 静态失败原因: The static model likely relied on superficial lexical overlap (e.g., 'FileInputStream', 'IOException', 'BufferedOutputStream') and similar control flow (try-catch, while loops), ignoring the stark difference in domain and functionality.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled as non-clone because the functions have completely different purposes and no meaningful semantic overlap; any similarity in file I/O patterns is incidental.
- 共享行为: Both perform file I/O operations；Both use try-catch to handle IOException
- 行为差异: Function A copies and decodes a file; Function B initializes multiple data structures for transliteration；Function A returns a boolean success flag; Function B returns void；Function A uses Base64 decoding; Function B uses StringTokenizer and HashMap parsing；Function A is a generic utility; Function B is domain-specific initialization
- 修正建议: Train the model to distinguish functional intent beyond token overlap；Incorporate more structural or dataflow analysis to capture actual semantics；Increase training data diversity with non-clone pairs sharing low-level I/O patterns but differing goals

### case_id=4591 FP lexical_or_api_overlap

- 方法: `run` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Opens a URL to localhost, reads all lines but discards them, closes stream, catches exceptions.
- B 摘要: Constructs a Google Images search URL, fetches HTML, parses image URLs, stores them, and updates a UI component with the first image.
- 静态失败原因: Static BERT models may over-rely on lexical and structural overlap of common I/O patterns (URL, BufferedReader, readLine) and generic method names, missing the semantic gap between a no-op read and a full image search with parsing and UI interaction.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clones because the functions have fundamentally different purposes: one is a dummy fetch with no side effects, the other performs a complex web search and UI update. The high-level behavior is entirely dissimilar despite shared boilerplate.
- 共享行为: Both use URL and HttpURLConnection/URL to open streams.；Both read lines from a BufferedReader.；Both close the stream in a finally-like manner.；Both catch exceptions gracefully.
- 行为差异: Function A ignores the read data; Function B processes it to extract image URLs.；Function A uses a fixed localhost URL; Function B constructs a dynamic Google Images URL.；Function B performs additional UI updates (enable button, set icon); Function A does not.；Function B includes specific parsing logic for image links; Function A has no parsing.
- 修正建议: Focus on data flow: check whether read data is actually used.；Consider method signatures and context (e.g., parameters, return type).；Incorporate higher-level intent via natural language descriptions or API call patterns.；Use models that better capture semantic purpose beyond token overlap.

### case_id=4592 FN benchmark_preference_bias

- 方法: `main` vs `streamContains`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a URL, unzips it, and writes each entry to a file.
- B 摘要: Reads an InputStream, converts its content to a UTF-8 string, and asserts it contains a given substring.
- 静态失败原因: Static prediction correctly identified non-clone (0) due to low token Jaccard (0.092) and very different structures. The BCB label is likely erroneous, so the static model did not fail.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled them as clones due to a broad interpretation of 'stream processing' or because both involve reading from an InputStream and converting to bytes, but this is a very generic similarity.
- 共享行为: Both use InputStream and read data；Both handle IOException；Both use Java I/O streams
- 行为差异: A writes files, B only reads and asserts；A uses ZipInputStream, B uses IOUtils.copy and ByteArrayOutputStream；A is a main method, B is a test utility method；A downloads from a specific URL, B takes arbitrary InputStream
- 修正建议: Review BCB annotation guidelines to reduce false positive clones；Consider multi-modal features (e.g., data flow) to avoid over-generalization

### case_id=4593 FN partial_functionality

- 方法: `copyResource` vs `run`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a single resource (URL or local file) to a destination file byte by byte.
- B 摘要: Copies all files from a Hadoop directory to a local output file using Hadoop FileSystem API.
- 静态失败原因: Low token Jaccard (0.1429) due to different APIs (HDFS vs URL/File) and control structures. Static models rely on surface similarity, missing the abstract semantic commonality of copying data streams.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels as clones if the core functionality (copying data from input to output) is similar, even with different sources and error handling. Both achieve file copying, so broad Type-4 clone.
- 共享行为: Both involve reading from an input source and writing to an output file；Both handle file I/O with streams；Both close streams after copying
- 行为差异: copyResource copies a single resource; run copies multiple files from a directory；run includes Hadoop-specific configuration and directory listing; copyResource uses simple URL/FileInputStream；run has error handling for missing arguments and non-directory input；copyResource throws Exception on missing resource; run returns error codes
- 修正建议: Improve model to recognize abstract patterns like 'read from source, write to destination' even with different I/O libraries；Add training on I/O patterns across different contexts；Use data-flow analysis to capture stream copying operations

### case_id=4594 FN partial_functionality

- 方法: `getFile` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies the wsdlsoap:address location, and saves to local temp file.
- B 摘要: Copies source files to target destinations with optional SVN operations and deletion of old files.
- 静态失败原因: Low token overlap and distinct method names lead to low similarity in token-level models; GraphCodeBERT might miss the conceptual link of file copying due to different contexts and control flows.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as file-copy operations using NIO channels, thus partial functionality similarity qualifies as a Type-4 semantic clone.
- 共享行为: Both use FileChannel to transfer data between streams.；Both perform file I/O with FileInputStream and FileOutputStream.；Both output debug/info messages.
- 行为差异: A handles WSDL-specific XML parsing and endpoint modification; B does not.；B involves command-line argument parsing and SVN integration; A does not.；A downloads from a URL; B copies local files.；A returns a file path; B exits the JVM.
- 修正建议: Incorporate task-level semantics and documentation embeddings.；Use data flow analysis to detect shared I/O patterns beyond surface tokens.

### case_id=4595 FP lexical_or_api_overlap

- 方法: `main` vs `testCopyUnknownSize`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Generates Java adapters by parsing a Prolog file and writing class files.
- B 摘要: Tests copying an InputStream to an OutputStream with unknown size.
- 静态失败原因: The static method (e.g., GraphCodeBERT) likely overestimated similarity due to the presence of common I/O-related tokens (e.g., 'IOException', 'InputStream') despite very low Jaccard similarity (0.07). The model may have been biased by the shared lexical items and failed to capture the entirely different high-level tasks.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels this as non-clone because the functions are completely different in purpose and functionality. There is no significant semantic overlap; the only superficial similarity is the use of I/O operations, which is insufficient for a clone annotation.
- 共享行为: Both use Java I/O classes (e.g., InputStream, OutputStream, File).
- 行为差异: Function A is a complex main method with multiple steps; function B is a simple unit test.；Function A parses Prolog and generates adapters; function B copies bytes between streams.；Function A writes class files; function B asserts byte array equality.；Function A has extensive error handling and file I/O; function B uses JUnit assertions.
- 修正建议: Improve model training with more negative examples that share low-level API calls but differ in functionality.；Incorporate higher-level semantic features (e.g., data flow, control flow) to distinguish different tasks.；Use more comprehensive negative sampling to reduce false positives from incidental API overlap.

### case_id=4596 FN benchmark_preference_bias

- 方法: `copy` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Copies a source file to a destination file using FileChannel.
- B 摘要: Retrieves a resource as an input stream, downloading via HTTP if not cached, and caches locally.
- 静态失败原因: Static BERT did not fail; it correctly predicted non-clone. The BCB label is likely a false positive in the benchmark.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB likely labeled this as a 'broadly similar' clone due to both involving file copying/storage, but the functionalities are fundamentally different.
- 共享行为: Both perform file I/O operations；Both use FileInputStream and FileOutputStream
- 行为差异: A copies local file to local file; B fetches from URL and caches；A uses FileChannel for zero-copy transfer; B uses byte-by-byte copying with BufferedStreams；B involves network interaction, caching logic, and HTTP headers; A does not；B has complex error handling and fallback; A throws IOException
- 修正建议: Re-evaluate BCB annotation; consider this pair as non-clone；If BCB intends partial similarity, refine guidelines to avoid overbroad labeling

### case_id=4597 FP lexical_or_api_overlap

- 方法: `setMembers` vs `importSequences`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Parses HTML from a Trac URL to extract component and priority options from select elements.
- B 摘要: Imports DNA/protein sequences from a URL by parsing FASTA-like format and storing names and sequences.
- 静态失败原因: The false positive (static predicted 1) likely due to overlap in URL handling, token patterns like 'URL', 'openStream', 'BufferedReader/InputStreamReader', and exception handling. Static models may focus on API usage and lexical similarity, overlooking high-level semantics.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled as non-clone because the overall functionality and output are completely different; the URL reading is a common pattern but not enough for Type-3/4.
- 共享行为: Both read from a URL using URL.openStream()；Both use input stream readers (BufferedReader/InputStreamReader)；Both iterate over lines of input；Both catch MalformedURLException and IOException
- 行为差异: Different parsing logic: HTML select elements vs FASTA-like sequence format；Different data structures: array fields (m_strComponents, m_strPriorities) vs ArrayList (names, sequences)；Different exception handling: System.out.println vs e.printStackTrace；setMembers uses regular expressions to extract option values; importSequences uses StringTokenizer and a helper object
- 修正建议: Incorporate more structural or data flow analysis to differentiate domain-specific parsing；Use context-aware embeddings to capture overall functionality；Train on more diverse examples to reduce sensitivity to common boilerplate patterns

### case_id=4598 FN benchmark_preference_bias

- 方法: `modifyApplicationMessage` vs `createTar`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Modifies a properties file for a given locale by updating or adding a message key-value pair.
- B 摘要: Creates a tar archive from all files in a directory.
- 静态失败原因: The static BERT model correctly predicted non-clone due to low lexical overlap and different API usage; the BCB label being 1 suggests benchmark inconsistency.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as clone due to both involving file reading/writing operations, but the core semantics and domain are completely different; likely an annotation error.
- 共享行为: Both perform file I/O operations with streams and buffers
- 行为差异: A processes text properties files; B processes binary files to create tar archives；A modifies key-value pairs; B compresses directory structure；A uses Properties and BufferedReader; B uses TarOutputStream and FileInputStream；A handles missing file by copying; B skips certain files like itself
- 修正建议: Improve annotation guidelines to avoid labeling semantically unrelated functions as clones；Use more rigorous semantic analysis or human review for ambiguous cases

### case_id=4599 FP boilerplate_overlap

- 方法: `writeFileType` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads URIs from a file, skips to a specified line, then for each subsequent URI fetches content, checks for RDF/OWL namespaces within first 100 lines, and writes the URI with a type label to an output file.
- B 摘要: Performs a Google image search for the current artist and album, fetches the HTML, extracts image URLs from href attributes, and adds them to a list, only if the artist differs from the previous one.
- 静态失败原因: Static models like BERT may be misled by lexical overlap in boilerplate code (URL connection, BufferedReader, exception handling) and fail to capture the distinct semantic goals and data flows.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels clones based on overall functionality similarity, not just shared API calls. These functions serve entirely different purposes, so BCB correctly labels them as non-clones.
- 共享行为: Both use URL connections (URL.openConnection) to fetch content from the web.；Both read lines from an input stream using BufferedReader.；Both have exception handling with try-catch blocks.
- 行为差异: Different overall goals: one classifies URIs into RDF types, the other searches for album images.；Different inputs: A reads from a file and skips lines, B uses instance variables (artist, currentTrack).；Different outputs: A writes to a file, B populates a list (googleImages) and has a side effect of setting a static variable.；Different parsing logic: A checks for specific substrings, B splits strings and extracts URLs from a specific pattern.
- 修正建议: Incorporate dataflow analysis to track how inputs are used and outputs are produced.；Use method-level semantic embeddings that capture the overall purpose, not just token sequences.；Consider class and field context to understand side effects.

### case_id=4600 FP boilerplate_overlap

- 方法: `readData` vs `cpFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Reads and parses tokenized strings to populate hash sets and maps, and processes a file with wylie/tibetan data.
- B 摘要: Copies a file from source to target with configurable buffer size and replacement policy.
- 静态失败原因: The model likely made a false positive due to boilerplate overlap (e.g., both use IOException and file-related terms in truncated code) or insufficient focus on high-level semantics.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would not consider these as clones because they perform entirely different tasks; no functional similarity even under broad Type-4 criteria.
- 行为差异: Completely different purposes: data initialization vs file copying；Different I/O patterns and data structures；No overlap in core functionality
- 修正建议: Improve model's ability to focus on core logic rather than boilerplate patterns；Use finer-grained representations like data flow or control flow to differentiate functions

### case_id=4601 FN partial_functionality

- 方法: `readPage` vs `testNetworkHTTP`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.4`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a URL's content, optionally skipping lines starting with '#', and returns the concatenated string.
- B 摘要: Tests network HTTP by making multiple requests to various URLs, reading response lines without processing them, and logging.
- 静态失败原因: Low token Jaccard (0.1449) indicates little lexical overlap; static BERT models rely on surface tokens and likely missed the semantic similarity of the network I/O pattern due to different variable names, method names, and control flow.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB annotators may have considered the core 'reading from URL' pattern as sufficient for a Type-4 clone, despite differences in return type, multiple URLs, and additional logic.
- 共享行为: Both open HTTP connections using URL and openStream；Both use BufferedReader to read lines；Both close the connection or stream
- 行为差异: Function A returns the full content; Function B does not return anything；Function A handles a single URL; Function B makes multiple connections to different URLs；Function A has conditional logic to ignore comment lines; Function B does not；Function B includes logging and catches IOException; Function A throws Exception
- 修正建议: Augment training data with diverse implementations of common I/O patterns；Use models that capture API-level semantics, e.g., graph-based representations；Train with contrastive examples that emphasize functional similarity despite lexical differences

### case_id=4602 FP partial_functionality

- 方法: `SRWGuiClient` vs `PhoneSetImpl`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Constructs a GUI browser window, loads XML or HTML from a URL, transforms it, and displays the result.
- B 摘要: Constructs a phone set map by reading lines from a URL resource, skipping comment lines, and parsing each line into the map.
- 静态失败原因: Static BERT models might overemphasize the lexical overlap of 'URL', 'BufferedReader', and 'readLine()', and the syntactic structure of both being constructors, while missing the vast semantic divergence in the rest of the code.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely labeled 0 because the functions are fundamentally different: one is a GUI browser initializer, the other is a data loader. The only commonality is a trivial opening and reading of a URL, which is insufficient for clone identification under BCB guidelines.
- 共享行为: Both open a URL and create a BufferedReader to read lines.；Both are constructors that take a URL-related parameter.
- 行为差异: A builds a full GUI with panels, buttons, and an HTML pane, while B only reads data into a map.；A performs XML transformation and handles stylesheets, which B does not.；B closes the reader after reading, whereas A does not explicitly close the reader.；A sets up window listeners and look-and-feel, B has no UI components.
- 修正建议: Improve model attention to capture high-level semantic intent beyond initial boilerplate.；Incorporate richer structural information, such as data flow and control flow graphs, to distinguish different processing pipelines.

### case_id=4603 FP lexical_or_api_overlap

- 方法: `actionPerformed` vs `readAndRewrite`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Handles various GUI preferences and settings, saving them via a controller.
- B 摘要: Reads a DICOM file, parses it, and writes the pixel data to an output file.
- 静态失败原因: The model likely focused on shared file-related API tokens (e.g., 'File', 'InputStream', 'OutputStream') and sequential file processing patterns, ignoring the vastly different contexts and purposes.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would not label these as clones because they perform completely different tasks with no functional overlap beyond generic file handling.
- 共享行为: Both involve file I/O operations.；Both use Java IO classes (File, InputStream, OutputStream).
- 行为差异: A is an event-driven UI handler for application preferences; B is a standalone utility for DICOM file processing.；A includes GUI components (JFileChooser, JOptionPane); B has no UI.；A saves settings to a controller; B reads and writes pixel data.；Their logic and control flow are entirely unrelated.
- 修正建议: Incorporate higher-level semantics via data flow analysis or context embeddings.；Use function renaming or documentation to disambiguate purposes.；Train on more diverse examples to avoid over-reliance on surface-level API similarity.

### case_id=4604 FP partial_functionality

- 方法: `import_hints` vs `downloadModel`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a file containing puzzle hint pieces from URL or local file, parses piece IDs, coordinates, rotations, and places them on a board.
- B 摘要: Downloads an RDF/XML model from a given URL, sets HTTP headers, reads the stream, and parses it into a Model object.
- 静态失败原因: Static BERT/GraphCodeBERT models may rely on surface-level code structure and common API usage (URL, InputStream, try-catch) to infer similarity, missing the deep semantic difference in data processing and final purpose.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB typically requires strong functional similarity. These functions share only a superficial I/O pattern but differ entirely in domain and output semantics. BCB would consider them non-clones due to lack of core functional overlap.
- 共享行为: Both use URL to open a connection and read data from an InputStream.；Both handle IOException with error handling.；Both involve reading and parsing data from an input source.
- 行为差异: Function A parses puzzle pieces and places them on a board; Function B parses RDF model data.；Function A returns boolean; Function B returns Model object.；Error handling: A returns false; B throws RuntimeException.；Function A has a hardcoded flag to always use URL; Function B always uses URL.
- 修正建议: Train on more diverse examples to recognize domain-specific logic differences.；Incorporate data flow analysis to distinguish different processing pipelines.；Add negative examples with similar I/O but different semantics to improve discrimination.

### case_id=4605 FN partial_functionality

- 方法: `run` vs `runInternal`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a resource file from the classpath and sets its content as text in a GUI component.
- B 摘要: Downloads an OPDS catalog or book from HTTP, parses entries or downloads the file, handles pagination and callbacks.
- 静态失败原因: The static BERT model likely focused on the low token overlap (0.098) and the different APIs (getResource vs. openConnection, StringBuilder vs. SAX parser), missing the high-level semantic similarity of I/O + GUI update that BCB annotators consider.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may accept a broad Type-4 clone based on the high-level pattern of 'reading data from an input source and then updating a user interface', despite vastly different sources and processing logic.
- 共享行为: Reads from an input stream；Closes streams after reading；Catches exceptions without recovery；Updates GUI after reading via invokeLater or callback
- 行为差异: Resource source: local classpath vs. remote HTTP；GUI update: direct text setting vs. callback with parsed entries；Complexity: simple read vs. HTTP headers, redirects, pagination, content negotiation；Exception handling: silent ignore vs. logging and error callback
- 修正建议: Incorporate high-level functional abstraction (e.g., classify methods by I/O operation and GUI update)；Use call-graph or program dependence analysis to capture similar data flow patterns；Train with more examples of broad behavioral similarity (Type-4) to reduce over-reliance on lexical overlap

### case_id=4606 FN benchmark_preference_bias

- 方法: `runScript` vs `loadExistingAntlibs`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Reads a script from a URL and returns its content as a string, with error handling returning 'error!'.
- B 摘要: Loads Antlib definitions from classpath resources by reading URLs line by line and resolving each to load an antlib.
- 静态失败原因: The static model correctly identified them as non-clones due to low token overlap (Jaccard=0.14) and different method signatures and purposes, but BCB's label was likely an anomaly; the model did not fail but the benchmark label may be erroneous.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might have considered them clones due to the common pattern of opening a URL, using InputStream, and reading data in a while loop, possibly categorizing them as Type-3/Type-4 based on similar structural fragments despite different overall functionality.
- 共享行为: Both open a URL stream and read data in a loop；Both handle IOException
- 行为差异: A returns a String, B is void；A reads a single script, B iterates over multiple resources；A reads raw bytes and concatenates to a string, B reads lines using BufferedReader；B performs additional URI resolution and calls another method (loadAntLib)
- 修正建议: Use more context-aware modeling considering overall method semantics；Incorporate dataflow analysis to differentiate reading for return vs. processing；Enhance evaluation benchmarks to avoid labeling such dissimilar functions as clones

### case_id=4607 FP lexical_or_api_overlap

- 方法: `readZoneIDs` vs `scrapeForIsbns`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a resource file line by line, parses each line as an integer, and returns a set of integers.
- B 摘要: Reads from a URL with retry and error handling, extracts ISBN-10 patterns using regex, stores them externally, and returns the count of matches.
- 静态失败原因: The static model likely over-relied on the overlapping I/O API calls (openStream, InputStreamReader, BufferedReader, readLine) and the loop structure, ignoring the distinct semantic purposes and subsequent processing.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels non-clones when the functionality differs significantly, such as one reading zone IDs and the other scraping ISBNs, despite sharing I/O boilerplate.
- 共享行为: Both open an input stream and create a BufferedReader via InputStreamReader.；Both read lines in a while loop until null.
- 行为差异: Code A reads from a local resource file; Code B reads from a URL with retry logic.；Code A parses lines as integers; Code B applies regex to find ISBN-10 strings.；Code A returns a HashSet of integers; Code B returns an integer count and writes to an external map.；Code B includes extensive error handling for ConnectException, IOException, InterruptedException; Code A catches generic Exception and prints stack trace.
- 修正建议: Incorporate data-flow analysis to capture how lines are processed after reading.；Use method name embeddings or other semantic signals.；Focus on the transformation pipeline rather than just structural similarity.

### case_id=4608 FN benchmark_preference_bias

- 方法: `getFile` vs `doRequest`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.2`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies the endpoint attribute in the XML, and saves it to a temporary file, returning the file path.
- B 摘要: Handles an HTTP request by retrieving an internal resource, setting its MIME type, and copying the resource stream to the response output stream, returning a boolean.
- 静态失败原因: The model likely relied on low lexical overlap and different API sequences, failing to recognize the abstract stream-copying pattern as a partial functional similarity. The distinct control flows and lack of common tokens led to a non-clone prediction.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might have considered both functions as performing a similar high-level task of 'downloading/serving a resource via HTTP and streaming it to an output', overlooking detailed differences due to broad Type-4 annotation criteria.
- 共享行为: Open an input stream from a URL or resource；Copy data from input stream to an output stream；Involve file/resource I/O operations
- 行为差异: Function A modifies XML content before saving, Function B does not modify data；Function A writes to a file, Function B writes to an HTTP response；Function A returns a file path, Function B returns a boolean；Function A has specific WSDL handling logic, Function B handles request path and MIME type
- 修正建议: Incorporate data flow analysis to detect stream copying patterns；Use graph-based representations to capture high-level I/O operations；Include training examples of Type-4 clones with minimal lexical overlap

### case_id=4609 FP lexical_or_api_overlap

- 方法: `run` vs `importRoles`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches a tile from a data source, processes its geometry, and adds it to a layer.
- B 摘要: Imports role names from a URL by parsing XML-like content and returns a list of RoleName objects.
- 静态失败原因: Static BERT likely over-relied on lexical and structural overlaps (URL, BufferedReader, while loop, try-catch) without capturing the high-level semantic differences in data processing and output.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels as non-clone because the overall functionality and output are entirely different, despite sharing some I/O boilerplate patterns.
- 共享行为: Reads data from a URL using URL and BufferedReader；Uses try-catch to handle MalformedURLException and IOException；Reads input line by line in a while loop
- 行为差异: Function A processes tile geometries; function B parses role XML fragments；Function A adds data to a layer; function B returns a list of RoleName；Function A has complex synchronization and multiple data structures; function B is simpler；Error handling differs: A has specific warnings, B has empty catch blocks
- 修正建议: Incorporate dataflow analysis to differentiate how data is processed after reading；Use more context-aware models that understand the specific domain (tile vs role) or output type；Add negative examples with similar I/O but different core logic during training

### case_id=4610 FP boilerplate_overlap

- 方法: `import_hints` vs `downloadFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a hint file from a URL or local path, parses piece data, and places puzzle pieces on a board.
- B 摘要: Downloads a file from a URL to a local destination, writing bytes in chunks and reporting progress.
- 静态失败原因: The static model likely overemphasized structural overlap (URL opening, buffered reading, boolean returns) and ignored the fundamentally different data processing and output behavior. The low token Jaccard was not enough to override the structural pattern similarity seen in training.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically annotates clones based on functional similarity beyond just I/O patterns. Since these functions have entirely different purposes (game hint import vs. file download), BCB correctly labeled them as non-clones.
- 共享行为: Both open a URL stream to read data；Both use buffered I/O；Both return a boolean indicating success or failure；Both handle I/O exceptions (one returns false, the other throws)
- 行为差异: Function A parses text tokens for puzzle pieces and modifies a game board; Function B writes raw bytes to a file.；Function A supports both URL and local file; Function B only supports URL.；Function A returns false on IOException; Function B throws Exception.；Function A prints debug info; Function B updates a progress bar via MessageFrame.
- 修正建议: Improve training with more negative examples that share boilerplate but differ in core logic.；Incorporate data-flow analysis or abstract syntax tree (AST) differences to capture operation semantics.；Use contrastive learning to distinguish similar wrappers with different internals.

### case_id=4611 FN lexical_or_api_overlap

- 方法: `getHTML` vs `setBundleInfoName`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches HTML content from a URL and optionally writes it to a file, returning the HTML as a string.
- B 摘要: Reads a properties file from a URL, parses key-value pairs, and updates a list of BundleInfo objects, returning a boolean success status.
- 静态失败原因: Static BERT/GraphCodeBERT models rely heavily on token overlap and local syntactic patterns; the low token Jaccard (0.26) and differing variable names, string literals, and API calls (e.g., HttpURLConnection vs url.openStream) cause the model to miss the overarching structural similarity of the URL-reading loop.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may deem this a Type-3 clone because both functions implement a common pattern of reading from a URL line-by-line and processing each line, with differences only in line processing and return type; such broad structural similarity often qualifies as a clone in BCB annotations.
- 共享行为: Both open a URL and read lines using BufferedReader；Both handle IOException by printing stack trace；Both use a loop to read lines until null
- 行为差异: Function A fetches and returns the entire content; Function B parses lines for key-value pairs and updates a data structure；Function A optionally writes to a file; Function B does not；Function A uses HttpURLConnection with a User-Agent header; Function B uses url.openStream() directly；Function A returns the HTML string; Function B returns a boolean
- 修正建议: Enhance model to capture control-flow structure (e.g., graph-based representations) rather than purely lexically；Use data-flow analysis to recognize common patterns like 'open connection, read lines, handle exception'；Train with more diverse examples of structural clones to learn to generalize beyond lexical overlap

### case_id=4612 FN benchmark_preference_bias

- 方法: `modifyApplicationMessage` vs `internalCopy`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Modifies a locale-specific properties file by adding or updating a message key-value pair, copying from English file if needed.
- B 摘要: Copies a file from source to destination using a buffer, excluding Thumbs.db.
- 静态失败原因: Static BERT/GraphCodeBERT models rely on token and AST similarity; low token Jaccard (0.155) and different syntactic structures lead to low embedding similarity, correctly predicting non-clone from strict viewpoint but failing to capture BCB's broad criteria.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider both as file I/O operations with processing (modify vs copy), possibly under Type-4 semantic clone based on similar overall data flow (read-process-write). However, the functionality is quite distinct.
- 共享行为: Both involve reading a file and writing to another file using streams；Both use while loops for reading/writing
- 行为差异: Function A performs key-value replacement and conditional file creation; function B does simple byte copy；Function A reads text lines with BufferedReader; function B reads byte arrays；Function A handles missing locale file by copying from English; function B skips specific file names；Function A catches Exception and prints stack trace; function B throws specific exceptions
- 修正建议: Enhance training data with more semantic clone pairs having low lexical overlap；Incorporate high-level functional similarity through program analysis or flow-aware representations

### case_id=4613 FN benchmark_preference_bias

- 方法: `CopyFile` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Copies a file from source to destination, creating parent directories if needed, using NIO FileChannel.
- B 摘要: Launches a NexOpen Eclipse project configuration, processes pom.xml files, sets Hibernate properties, and schedules an install job.
- 静态失败原因: Static BERT predicted non-clone correctly due to low token overlap and distinct APIs; the BCB label is likely erroneous.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have mislabeled due to broad interpretation of type-3/4 or an annotation error; the functions share no meaningful semantic similarity.
- 行为差异: Function A performs file copying only；Function B performs Eclipse project launch with XML processing, job scheduling, and persistent properties
- 修正建议: Review and correct BCB annotations for this pair；Consider excluding such clearly dissimilar pairs from clone evaluation

### case_id=4614 FN partial_functionality

- 方法: `testCopyUnknownSize` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Tests copying an InputStream to a ByteArrayOutputStream using a utility method and verifies correctness.
- B 摘要: Launches a NexOpen project configuration, including file handling, properties, and copying a resource file to a ByteArrayOutputStream.
- 静态失败原因: The static BERT/GraphCodeBERT model likely focused on overall token similarity and structure, which are very low (Jaccard 0.06). It failed to recognize the small overlapping API usage (IOUtils.copy) as evidence of partial semantic equivalence, leading to a false negative prediction.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled them as clones because both include the sub-functionality of copying an InputStream to a ByteArrayOutputStream, which could be considered a Type-4 semantic clone (same function with different contexts).
- 共享行为: Both involve copying an InputStream to a ByteArrayOutputStream via IOUtils.copy (or similar).
- 行为差异: A is a simple test method with no side effects; B is a complex method with many preconditions, file operations, and state changes.；A uses fixed test data; B reads from a plugin resource and modifies the content before copying.；A verifies the copy result; B does not verify and continues with other operations.
- 修正建议: Incorporate fine-grained API usage patterns and dataflow analysis to detect partial functionality overlap.；Train on examples where a method subsumes another's behavior, even if syntactically distinct.

### case_id=4615 FP lexical_or_api_overlap

- 方法: `DialogHelper` vs `main`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Constructs a GUI dialog that displays an image and provides a Save As button to copy the image file to a chosen destination.
- B 摘要: Main method of a command-line tool that reads a Prolog file, parses it, and generates adapter code and resources for a framework.
- 静态失败原因: The static BERT method likely overemphasized the presence of common Java API tokens (File, IOException, try-catch) and nested control structures, ignoring the vast semantic difference in domain and functionality.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would consider these non-clones because they have entirely different functionality and purpose, with no significant overlap in logic or I/O behavior beyond generic file handling.
- 共享行为: Both perform file I/O operations and handle IOException.；Both utilize conditional logic and loops.
- 行为差异: Function A is a GUI constructor for image saving; Function B is a CLI tool for code generation.；A uses Swing components (JDialog, JLabel, JScrollPane); B uses file parsing and class generation libraries.；A handles user interaction via dialogs; B processes command-line arguments.；A saves a single image file; B produces multiple artifacts (JAR, classes, serialized data).
- 修正建议: Incorporate functional role classification (GUI vs CLI) into the model.；Use embeddings that capture high-level task semantics beyond token overlap.；Apply supervision with contrastive learning on diverse functional domains.

### case_id=4616 FN partial_functionality

- 方法: `getFile` vs `modifyApplicationMessage`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies the SOAP address location, saves to temp, and returns the file path.
- B 摘要: Modifies a locale-specific properties file by replacing or adding a message key-value pair, copying from an English file if the locale file doesn't exist.
- 静态失败原因: Low token overlap (0.1337) and different domain-specific vocabulary (WSDL vs properties) misled the model; it missed the abstract control-flow and dataflow pattern shared between the functions.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: Both functions implement a high-level pattern: 'fetch or copy a configuration file, modify a specific element, and save it back'. This abstract structural similarity is considered a Type-4 clone in BCB annotations.
- 共享行为: Check if a target file exists and create/retrieve it if needed；Read file content, modify a specific value (SOAP address or message value), and write back；Use file I/O streams and handle exceptions
- 行为差异: A uses URL download to fetch source content; B copies from a local English file；A modifies XML attribute (wsdlsoap:address); B modifies key-value pair in properties file；A returns the file path; B returns void；A handles specific exceptions (MalformedURLException, IOException, etc.); B catches generic Exception
- 修正建议: Enhance model with abstract syntax tree (AST) or control-flow graph (CFG) features to capture structural similarities；Use code summary embeddings that focus on high-level intent rather than exact tokens；Include more Type-3/Type-4 clone examples in training data to learn broader functional equivalence

### case_id=4617 FN benchmark_preference_bias

- 方法: `copyResource` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Copies a resource from a URL or file to a destination file using byte streams.
- B 摘要: Main method that sets up a GUI for a Weka experiment, optionally reading/writing serialized experiment objects.
- 静态失败原因: Static BERT correctly predicted non-clone because token Jaccard is very low (0.089) and the code structures differ significantly; the BCB label is likely erroneous.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as a clone due to both functions containing common file I/O patterns (FileInputStream, FileOutputStream) and exception handling, but this is too weak a similarity; the overall behaviors are completely different.
- 共享行为: Both perform file I/O (reading and writing streams).；Both handle exceptions with try-catch or throws.
- 行为差异: copyResource is a utility method for resource copying; main is a GUI application entry point.；copyResource uses byte streams (InputStream/OutputStream); main uses object streams (ObjectInputStream/ObjectOutputStream).；copyResource has a simple byte-by-byte copy loop; main has complex GUI setup, event handling, and serialization.；copyResource is private; main is public static.
- 修正建议: Re-evaluate this pair in BCB as a likely false positive clone label.；Improve clone detection to require stronger semantic similarity beyond common API usage.

### case_id=4618 FN partial_functionality

- 方法: `readAndRewrite` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a DICOM file, parses it, reads pixel data, and writes it to an output file.
- B 摘要: Retrieves a resource from a URL or cache, caches it locally if needed, and returns an InputStream.
- 静态失败原因: Static BERT models rely on lexical and syntactic overlap, which is low here (token Jaccard 0.0786). They miss abstract structural similarities like the 'read-process-write' pattern due to domain-specific terminology and different API usage.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled these as clones based on the broad category of 'file handling/reading and writing' or because both exhibit similar control flow (open, read, process, write) and use common I/O stream classes.
- 共享行为: Both perform I/O operations involving reading from a source and writing to a destination；Both use BufferedInputStream/OutputStream for stream handling；Both print status messages during execution
- 行为差异: Function A is specific to DICOM image processing with pixel data; Function B is a generic resource caching mechanism；Function A writes pixel data and header; Function B writes raw bytes to a cache file and returns an InputStream；Function A uses DICOM-specific libraries; Function B uses URL/HTTP connections and caching logic；Function A operates on local files; Function B can operate on remote URLs and local cache
- 修正建议: Incorporate abstract representations such as control flow graphs or data flow diagrams to capture structural patterns；Use hierarchical or contrastive learning to recognize broader functional categories；Augment training data with examples of partial functional clones to improve model sensitivity

### case_id=4619 FN boilerplate_overlap

- 方法: `doGet` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Handles HTTP GET request, retrieves a page, checks permissions, logs, and optionally writes page to a file cache.
- B 摘要: Copies a file from source to destination using byte buffer and handles IOExceptions.
- 静态失败原因: The static BERT model predicted non-clone correctly as it captured the vast difference in functionality and code structure; however, BCB label is likely an annotation error, making the static prediction appear as a false negative.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may have labeled this as clone due to superficial similarity involving I/O operations and exception handling, which might be considered as partial functionality overlap by some annotators, but this is against typical BCB guidelines which require more substantial semantic equivalence.
- 共享行为: Both perform I/O operations (reading/writing files or streams)；Both use try-catch blocks for exception handling；Both close resources in finally blocks
- 行为差异: Function A is an HTTP servlet handler for web page requests; Function B is a simple file copy utility；Function A involves complex logic: page retrieval, user permissions, logging, caching; Function B has straightforward sequential copy；Different input/output types: A takes HttpServletRequest/Response, B takes File in/out；Different control flow: A has multiple nested conditions and loops; B has a simple for-loop
- 修正建议: Review BCB annotation for this pair to correct label；Use more strict semantic criteria in benchmark to avoid boilerplate similarities；Improve clone detection models to ignore common I/O boilerplate

### case_id=4620 FP lexical_or_api_overlap

- 方法: `run` vs `SRWGuiClient`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: An HTTP GET request with Basic authentication that reads the response into a string.
- B 摘要: A GUI constructor for a simple web browser that fetches an XML/XSL URL, transforms it, and displays the result.
- 静态失败原因: The static model may have been misled by overlapping API calls (URL, BufferedReader, InputStreamReader, StringBuffer) and similar variable names, despite low token Jaccard. The truncated code in B might contain additional similar patterns, but overall the functions are structurally and semantically distinct.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled 0 because the two functions perform fundamentally different tasks: one is a simple HTTP client, the other is a GUI application for browsing and transforming XML content. Their only commonality is reading from a URL, which is too generic to consider them clones even under broad Type-4.
- 共享行为: Both open a URL and read content using BufferedReader and InputStreamReader；Both read lines and append to a StringBuffer；Both use URL objects to fetch remote data
- 行为差异: A uses HttpURLConnection with authentication; B uses URL.openStream() without authentication；A is a Runnable intended for background execution; B is a constructor that sets up UI；B parses XML, applies XSLT transformations, and renders HTML; A just stores raw response；A has a loop updating lastIteraction time; B does not
- 修正建议: Increase sensitivity to distinct control flow and API usage patterns；Incorporate task-level semantic analysis (e.g., does it create GUI, does it handle authentication)；Use longer-range context or function-level classification rather than snippet matching

### case_id=4621 FP boilerplate_overlap

- 方法: `getUser` vs `scrapeForIsbns`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Loads a User from a DAO or from a config file by parsing lines with colon delimiter.
- B 摘要: Scrapes a URL for ISBN-10 patterns using regex with retry logic.
- 静态失败原因: The static BERT/GraphCodeBERT model may have overemphasized common boilerplate patterns (BufferedReader, InputStreamReader, readLine loop, try-catch) and missed the deep semantic differences in purpose, data parsing, and return types.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the functions perform completely different tasks (authentication vs. scraping) with different outputs and domain logic, despite superficial similarity in stream reading boilerplate.
- 共享行为: Both use BufferedReader and InputStreamReader to read from a stream.；Both loop over lines read from the stream.；Both use try-catch blocks for exception handling.
- 行为差异: Function A reads from a classpath resource for user authentication; Function B reads from a remote URL for ISBN scraping.；Function A parses lines with StringTokenizer and colon delimiter; Function B uses regex pattern matching.；Function A returns a User object or null; Function B returns an integer count.；Function B includes retry logic with sleep and multiple catch blocks; Function A does not.
- 修正建议: Incorporate structural features like method signature, return type, and control flow beyond token sequences.；Use data-flow analysis to distinguish different uses of stream data (parsing vs. pattern matching).；Train with contrastive examples that penalize superficial boilerplate similarity.

### case_id=4622 FN benchmark_preference_bias

- 方法: `copyFile` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Copies a file from source to destination using FileChannel.transferTo.
- B 摘要: Launches an Eclipse launch configuration for a NexOpen project, processing POM files and setting up Hibernate reverse engineering.
- 静态失败原因: The model correctly identified low token similarity (Jaccard=0.037) and distinct functionality; it failed to replicate BCB's potentially erroneous clone label.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have considered both methods as file-related or part of the same project, leading to a broad Type-4 annotation despite no semantic equivalence.
- 共享行为: Both perform file I/O operations.；Both use InputStream/OutputStream-like APIs.
- 行为差异: Code A is a simple file copy; Code B is a complex multi-step launch process.；Code A uses NIO channels; Code B uses XML parsing and property configuration.；Code B involves Eclipse-specific APIs and project management; Code A is generic.
- 修正建议: Re-evaluate this pair for correctness; if BCB label is wrong, remove from clone set.；If label is correct, model needs to capture high-level semantic similarity like file operations context.

### case_id=4623 FN boilerplate_overlap

- 方法: `addIDs` vs `createDialogArea`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Connects to a remote web service, scrapes metabolite IDs and molecular weights, and sets fields on a PeakListRow object.
- B 摘要: Creates a SWT dialog area, reads a license file from the bundle, and displays its text content in a browser or text widget.
- 静态失败原因: Static BERT/GraphCodeBERT likely focused on the overall functional semantics and domain-specific vocabulary, which are highly dissimilar, leading to a non-clone prediction. The model failed to recognize the superficial I/O pattern that BCB considered as evidence of cloning.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB might consider them clones due to the shared boilerplate pattern of opening a stream, reading lines, and handling exceptions, even though the functional purpose is completely different. The annotation may have prioritized structural similarity over semantic difference.
- 共享行为: Both open a BufferedReader to read lines from an input stream.；Both iterate line by line using a while loop.；Both close resources in finally blocks or implicitly.
- 行为差异: Function A connects to a remote URL and parses HTML; Function B reads a local resource file.；Function A extracts and processes specific metabolite data; Function B simply displays the entire file content.；Function A returns an integer (score); Function B returns a Composite control.；Function A uses domain-specific classes (GCGCColumnName, PeakListRow); Function B uses SWT widgets.
- 修正建议: Incorporate structure-aware features (e.g., control flow graphs) to capture common patterns across different domains.；Use contrastive learning to better separate boilerplate similarity from true semantic cloning.；Re-evaluate BCB annotations to ensure consistency with functional equivalence.

### case_id=4624 FP lexical_or_api_overlap

- 方法: `readTwitterFead` vs `checkForUpgrade`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `1.0`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a Twitter timeline JSON feed via HTTP GET and returns the response as a string.
- B 摘要: Checks for available software upgrades by querying a local database and a remote server, then updates UI components.
- 静态失败原因: Static BERT/GraphCodeBERT likely over-emphasized the lexical overlap of HTTP client setup and line-by-line reading, treating them as evidence of similarity while ignoring the different intents and surrounding code.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the functions have fundamentally different purposes and behavior, despite sharing a common HTTP reading pattern.
- 共享行为: Both perform an HTTP GET request and read the response line by line.
- 行为差异: readTwitterFead is a simple read-only operation; checkForUpgrade involves database queries, UI manipulation, and upgrade logic.；readTwitterFead returns a string; checkForUpgrade is void and updates UI.；checkForUpgrade has complex control flow with loops and conditionals; readTwitterFead has a simple try-catch with a single GET.；checkForUpgrade handles license and error states; readTwitterFead only logs exceptions.
- 修正建议: Incorporate data flow analysis to distinguish side-effect-free reads from state-modifying operations.；Use method name and context (e.g., surrounding class, imports) to infer purpose.；Apply whole-program analysis to capture differences in control flow and external interactions.

### case_id=4625 FN partial_functionality

- 方法: `copyResource` vs `saveProject`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource from a URL or file to a destination file byte by byte.
- B 摘要: Saves a project by creating directory structure, copying database files, saving various layer data, and packaging into a zip file.
- 静态失败原因: The static BERT model likely focused on the overall syntactic structure and method length, which differ significantly. The low token Jaccard similarity and different method names led to a non-clone prediction. The model failed to recognize the shared copying sub-functionality due to the high-level semantic abstraction required.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider these clones because both involve copying data from a source to a destination using Java I/O streams. The core functionality of file copying is present in both, albeit at different scales and contexts.
- 共享行为: Both perform file I/O operations.；Both read from a source and write to a destination.
- 行为差异: copyResource is a simple single-file copy; saveProject is a multi-step project save with many sub-operations.；copyResource uses byte-by-byte reading; saveProject uses FileChannel for bulk copying.；saveProject includes database queries, XML serialization, and directory management.
- 修正建议: Use data-flow analysis to capture read-write patterns across methods.；Incorporate structural matching of I/O operations regardless of surrounding code.

### case_id=4626 FN benchmark_preference_bias

- 方法: `readData` vs `GetResponse`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.7`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Parses a configuration file to populate various sets and maps used for Tibetan transliteration.
- B 摘要: Performs an HTTP GET request and returns the response body as a string.
- 静态失败原因: Static models may focus on superficial cues like method names ('readData' vs 'GetResponse' both implying data retrieval) and common control flow patterns (try-catch, read loop), missing the deep semantic divergence.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might consider both as 'reading input' functions under a very broad Type-4 semantic similarity, but this is tenuous and likely a mislabel.
- 共享行为: Both retrieve textual data from an external source (file vs HTTP).
- 行为差异: Source: local file parsing vs HTTP request；Parsing logic: complex tokenization and conditional processing vs simple line concatenation；Output: populates multiple data structures vs returns a single string；Error handling: throws errors on malformed data vs catching exceptions and returning null
- 修正建议: Require functional similarity beyond generic I/O operations；Use semantic role labeling to capture distinct intents；Augment training data with fine-grained categories for I/O types

### case_id=4627 FN partial_functionality

- 方法: `read` vs `wordFrequency`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Read a file or URL and return status code indicating success or error.
- B 摘要: Query a web service to get word frequency from HTML content, return an integer frequency.
- 静态失败原因: Static BERT models rely heavily on token overlap and method signature similarity. Here, token Jaccard is low (0.3125), method names differ, and code structure appears different at surface level. The shared URL/I/O patterns are not sufficiently captured due to low token overlap and different control flow (while loop vs sequential).
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often annotates clones based on structural and API-level similarity even if high-level functionality differs. Both functions exhibit a common pattern of opening a URL/stream, reading data, handling exceptions, and returning an int. This aligns with Type-3/4 clone categories in BCB.
- 共享行为: Both take a String parameter and use it to open a URL or file.；Both use try-catch blocks to handle IOException.；Both return an int value.；Both use buffered I/O streams.
- 行为差异: Function A reads entire input and returns a status; Function B reads line by line to match a pattern and extract numeric frequency.；Function A handles both local files and URLs; Function B only uses URLs.；Function A sets a status field and returns it; Function B returns directly computed frequency or 0.；Function A has no string parsing logic; Function B uses regex and pattern matching.
- 修正建议: Improve model sensitivity to structural patterns like try-catch blocks combined with I/O API usage.；Augment training with more examples of partial functionality clones where core logic differs but API skeleton is similar.；Use dataflow or control flow features to capture abstract behavior beyond token overlap.

### case_id=4628 FN benchmark_preference_bias

- 方法: `copyFile` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Copies a file from source to destination using NIO FileChannel.
- B 摘要: Builds a site for editing by processing pages, reading and transforming files, and writing output.
- 静态失败原因: The static model correctly identified non-clone; BCB label is likely a false positive (annotation error), so the model did not fail.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled as clone due to both performing file I/O, possibly considering Type-4 (functionally similar) but the high-level functionality is significantly different.
- 共享行为: Both involve file I/O operations (reading and writing files).
- 行为差异: A is a simple file copy; B is a complex site-building method with many steps.；A uses NIO channels; B uses traditional IO and string manipulation.；B includes XML/HTML processing, DOM, and property handling.
- 修正建议: Re-evaluate BCB annotation for this pair; focus on high-level semantics rather than low-level I/O patterns.；Encourage models to capture overall purpose and control flow beyond common I/O operations.

### case_id=4629 FN benchmark_preference_bias

- 方法: `main` vs `getFileContentAsString`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.7`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a URL, decompresses it as a zip, and extracts all entries to the file system.
- B 摘要: Reads a file from the classpath or file system and returns its content as a string.
- 静态失败原因: Static BERT likely focused on the low token-level similarity (Jaccard=0.15) and distinct method names, missing the high-level structural pattern of stream usage. It also may have failed to capture the functional overlap that BCB annotators considered important.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may label these as clones due to a broad interpretation of 'file I/O' or 'resource reading' commonality, emphasizing shared stream opening and closing patterns over specific processing logic.
- 共享行为: Both open an InputStream from a URL or file.；Both close the input stream after use.
- 行为差异: A extracts zip entries and writes to files; B reads text content and returns a string.；A uses ZipInputStream and FileOutputStream; B uses StringWriter and IOUtils.copy.；A deals with binary data and archives; B deals with text and encoding.
- 修正建议: Use a model that can capture broader functional categories like 'stream processing'.；Incorporate control-flow or data-flow analysis to detect similar I/O patterns.；Fine-tune on BCB's specific annotation guidelines to mimic human leniency.

### case_id=4630 FP partial_functionality

- 方法: `main` vs `copy`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Main method that parses command line arguments, reads a Prolog file, parses it, generates adapter classes using FactVisitor, writes them to a JAR, and handles errors.
- B 摘要: Static method that recursively copies a file or directory from source to destination using FileInputStream/FileOutputStream, with error logging.
- 静态失败原因: Static BERT/GraphCodeBERT models may overemphasize lexical and structural overlap, such as common API usage (File, IOException) and control flow patterns (loops, conditionals), while missing high-level semantic differences. The low token Jaccard suggests limited lexical similarity, but the model might pick up on shared patterns like file reading/writing and exception handling.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB (BigCloneBench) typically labels non-clones when functions have entirely different purposes and only share generic programming patterns. Here, the overall goal and domain are completely different, so BCB correctly annotated as non-clone.
- 共享行为: Both perform file I/O operations (reading/writing files).；Both handle exceptions (IOException, FileNotFoundException).；Both use loops (while loop in B, iterator loop in A).；Both check conditions (if-else) to decide actions.
- 行为差异: A parses Prolog code and generates adapters; B copies files and directories.；A uses command-line arguments; B uses File parameters.；A writes classes and resources to a JAR; B copies raw bytes.；A involves complex domain-specific logic (Prolog parser, FactVisitor, ClassWriter); B is a straightforward file copy utility.
- 修正建议: Incorporate dataflow analysis to better capture program semantics and distinguish different high-level goals.；Use contrastive learning with more diverse negative samples to reduce sensitivity to common boilerplate patterns.；Include method names and comments as explicit features to capture intent.

### case_id=4631 FN benchmark_preference_bias

- 方法: `doGet` vs `extractFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Handles HTTP GET requests to retrieve and serve a page, with user visibility checks and caching.
- B 摘要: Copies a file from an input path to an output path using file streams.
- 静态失败原因: Static BERT correctly predicted non-clone because the lexical and structural overlap is minimal, but BCB label may be erroneous.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled them as clones due to both involving 'extracting' or 'retrieving' data (page vs file), but the contexts are entirely different.
- 共享行为: Both perform I/O operations (file or network)
- 行为差异: Function A processes HTTP requests and involves complex business logic; function B simply copies a file.；Function A has exception handling and logging; function B has no exception handling.；Function A interacts with a database and user sessions; function B does not.
- 修正建议: Review BCB label for correctness; these functions are not semantically similar.；Improve benchmark consistency by removing ambiguous pairs.

### case_id=4632 FN partial_functionality

- 方法: `getFile` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies the endpoint in the XML, and saves to a temporary file.
- B 摘要: Copies a file from one location to another using NIO FileChannel.
- 静态失败原因: Static BERT likely relied on token-level similarity and structural patterns; the low token overlap (0.1157) led it to predict non-clone, but BCB's label suggests a deeper similarity that static models may miss. However, in this case, the static model's prediction aligns with semantic judgment.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have considered the shared use of FileChannel for data transfer as a sufficient commonality, or the annotation may be an error in the dataset.
- 共享行为: Both use Java NIO FileChannel to transfer data between streams.
- 行为差异: Function A involves network I/O, XML parsing, and multiple file operations; B is a simple file copy.；Function A has extensive error handling and logging; B has minimal exception handling.；Function A creates and deletes temporary files; B only copies existing files.
- 修正建议: Improve detection of partial functionality clones by considering subgraph matching or functional decomposition.；Incorporate data flow analysis to identify common sub-operations like file channel transfer.

### case_id=4633 FN partial_functionality

- 方法: `doExecute` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Handles multipart form data and sends an email with attachments.
- B 摘要: Builds an editable site by transforming XML pages and writing output files.
- 静态失败原因: GraphCodeBERT likely failed due to low token overlap (Jaccard 0.063) and lack of shared identifiers; it may have missed the abstract structural pattern that BCB annotators might see.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB might consider these as Type-4 clones due to shared high-level structure: both loop over input items, perform transformations, and handle errors, though the domains differ. However, the semantic gap is large.
- 共享行为: Both iterate over collections of items (attachments/pages)；Both perform file I/O operations；Both include error handling with try-catch blocks
- 行为差异: Function A is an action handler for email sending; B is a site builder；A processes HTTP form data; B reads XML and writes HTML files；A uses web framework (Struts) objects; B uses custom file and DOM utilities
- 修正建议: Improve training data with more Type-4 clone examples；Enhance model to capture abstract control flow patterns beyond lexical similarity

### case_id=4634 FP lexical_or_api_overlap

- 方法: `sendPost` vs `executeHttpGet`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Sends HTTP POST with parameters, reads response as string, handles exceptions by showing message.
- B 摘要: Executes HTTP GET request, returns response as JSONObject, throws exceptions.
- 静态失败原因: Static BERT may have over-relied on common lexical patterns (BufferedReader, readLine, while loop) and missed differences in HTTP method and library usage.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels as non-clone due to low structural similarity and significant functional differences in HTTP method, library, and error handling.
- 共享行为: Both perform HTTP request and read response line by line.
- 行为差异: HTTP method: POST vs GET；Library: HttpURLConnection vs Apache HttpClient；Exception handling: caught and shown vs thrown；Return type: String vs JSONObject
- 修正建议: Train model to better distinguish different HTTP methods and libraries；Incorporate dataflow or dependency analysis to capture different error handling；Use contrastive learning on similar but functionally different code pairs

### case_id=4635 FP lexical_or_api_overlap

- 方法: `main` vs `patch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.98`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Main method that parses a Prolog file and generates adapter code, writing output to a JAR file.
- B 摘要: Method that backs up a Minecraft jar file by copying and then opening it.
- 静态失败原因: The model likely relied on superficial lexical overlap (e.g., 'File', 'JarFile', 'IOException', 'return') or similar control flow patterns, missing the deep semantic difference between generating adapters and backing up a game jar.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would label these as non-clones because they perform completely different tasks with no functional similarity, even though both use file I/O.
- 共享行为: Both perform file I/O operations；Both handle exceptions
- 行为差异: Function A is a complex adapter generation pipeline; Function B is a simple backup and open of a jar file；Function A involves parsing, class loading, and writing multiple resources; Function B only copies and opens a jar；Function A has a main method signature; Function B is a public instance method
- 修正建议: Incorporate more task-specific features like method purpose classification；Use contrastive learning to distinguish methods with similar APIs but different intents；Add training examples with low token overlap but high semantic difference

### case_id=4636 FN partial_functionality

- 方法: `copyResource` vs `save`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a single resource (URL or file) to a destination file using byte stream.
- B 摘要: Saves multiple files from byte arrays to a directory and then copies them to a package directory while prepending a package declaration.
- 静态失败原因: Low token overlap (0.1975) and different method signatures/names mislead static BERT; it cannot capture the underlying functional similarity of file copying due to surface-level differences.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considers both as 'copy data to files' tasks, focusing on the common I/O pattern rather than specific parameters or extra steps, thus labeling them as Type-4 clones.
- 共享行为: Performs file copying operations (read from source, write to destination).
- 行为差异: A copies a single source; B handles multiple files and adds a package header.；A uses only byte-level I/O; B uses both byte and character I/O.；B creates directories and performs an additional copy step with modification.
- 修正建议: Enhance model with data flow analysis to recognize common I/O patterns.；Use graph-based models that abstract operations like read/write.；Include more diverse training examples of partial functionality clones.

### case_id=4637 FN library_context_missing

- 方法: `copyResource` vs `writeFileToFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `context_recovery_then_expert`；动态可解性: `low`；执行优先级: `medium`
- A 摘要: Copy resource from URL or file to a destination file using byte-by-byte streaming.
- B 摘要: Copy a file to another file using NIO FileChannel transferTo, with optional append.
- 静态失败原因: Static BERT-based models rely heavily on token overlap and structural similarity. The low Jaccard similarity (0.18) and different API usage (InputStream vs FileChannel) likely caused the model to miss the underlying semantic similarity, leading to a false negative.
- 静态 case study: 该类错误缺少关键上下文或需要深层语义，纯静态方法不可靠。
- 动态 case study: 动态执行价值较低：样本可能依赖库、框架、网络、GUI、数据库或项目上下文，需要先恢复环境或 mock 依赖。
- BCB 偏好解释: BCB often labels functions as clones if they perform the same high-level task (copying a file/resource to a file), accepting significant syntactical and implementation differences (Type-3/Type-4).
- 共享行为: Both copy data from a source to a destination file.；Both involve opening input and output streams/channels and closing them after use.
- 行为差异: copyResource supports URL sources; writeFileToFile only accepts File objects.；copyResource uses InputStream/OutputStream; writeFileToFile uses FileChannel.；writeFileToFile has an append parameter; copyResource does not.；copyResource throws generic Exception; writeFileToFile throws specifically IOException.
- 修正建议: Enhance training data with diverse I/O implementation patterns.；Incorporate data flow analysis to abstract over concrete API calls.；Use contrastive learning on functionally similar but syntactically different pairs.

### case_id=4638 FP lexical_or_api_overlap

- 方法: `loadMFileViaWeb` vs `getFrameworkFactory`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Loads a MATLAB function file from a web URL and parses it into a UserFunction.
- B 摘要: Reads an OSGi service configuration file from classpath to instantiate a FrameworkFactory.
- 静态失败原因: The static BERT model likely overfocused on the lexical and API overlap (e.g., URL, BufferedReader, readLine, while, try-catch) and ignored the differences in overall purpose, return type, and how the read data is used.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically annotates non-clones when two functions have different domain-specific purposes and output types, even if they share some structural patterns like reading lines from a stream. Here, the functionality is completely different (loading user functions vs. OSGi factory), so BCB would likely label as non-clone.
- 共享行为: Both open a stream from a URL and read lines using BufferedReader.；Both process each line in a loop (concatenate vs. check for non-comment).；Both handle exceptions or closing of resources.
- 行为差异: A reads from an arbitrary web URL; B reads from a classpath resource.；A concatenates all lines into a single string; B only uses the first non-comment line to load a class.；A returns a UserFunction; B returns a FrameworkFactory.；A logs debug information; B does not.
- 修正建议: Incorporate return type and method signature similarity.；Use dataflow analysis to capture how the read lines are used.；Fine-tune on a more diverse set of negative examples with similar APIs but different semantics.

### case_id=4639 FN partial_functionality

- 方法: `copyResource` vs `patch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource from a URL or file path to a destination file using byte-by-byte stream copying.
- B 摘要: Copies the Minecraft JAR file to a backup path if modifications exist, then opens the JAR file for further processing.
- 静态失败原因: Static BERT models like GraphCodeBERT rely on lexical and syntactic patterns, but these functions have low token overlap (Jaccard=0.14), different method names, and different control structures (while loop vs. library call). The model missed the semantic similarity of stream copying due to sparse lexical cues and lack of dataflow insight.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BigCloneBench includes Type-4 clones where the core functionality (copying a file via I/O streams) is semantically similar, even if the surrounding logic differs. The shared core behavior of copying from a source to a destination qualifies as a functional clone.
- 共享行为: Both perform file copying from a source to a destination using Java I/O streams.；Both handle exceptions (IOException or Exception).
- 行为差异: copyResource uses a while loop for byte-by-byte transfer; patch uses IOUtils.copy (likely buffered).；copyResource handles both URL and local file sources; patch uses a fixed file path for the Minecraft JAR.；patch has a guard clause checking if modifications are empty, and after copying it opens a JarFile; copyResource does none of these.；The destinations and error handling messages differ.
- 修正建议: Enrich training data with more variations of file-copying patterns (byte-by-byte, buffered, using libraries).；Incorporate dataflow analysis to identify input/output streams and their transformations.；Use type-aware embeddings to recognize InputStream/OutputStream usage regardless of implementation details.；Add unsupervised pretraining on code with similar I/O operations to learn functional similarity.

### case_id=4640 FN boilerplate_overlap

- 方法: `getJSONData` vs `login`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.6`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches JSON data from a given URL via HTTP GET and returns a JSONObject.
- B 摘要: Logs into a service by sending credentials via HTTP POST and returns the session ID.
- 静态失败原因: Static BERT models rely on token-level similarity. The low token Jaccard (0.18) and distinct vocabulary (e.g., 'JSONObject', 'JSONTokener' vs 'URLEncoder', 'sessid') caused the model to focus on surface differences, missing the structural similarity in network communication pattern.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may label this as a clone due to the shared boilerplate pattern of opening an HTTP connection, reading data, and handling errors, which is considered a Type-3/Type-4 clone under broad criteria.
- 共享行为: Performs HTTP network communication with a server；Reads the response stream line by line；Uses BufferedReader and InputStreamReader；Handles exceptions with try-catch
- 行为差异: HTTP method: GET (A) vs POST (B)；Return type: JSONObject (A) vs String (B)；Input: URL parameter (A) vs no parameter, uses hardcoded URL (B)；Response processing: parses entire JSON (A) vs extracts session ID from first line (B)
- 修正建议: Use a model that captures structural patterns, such as AST-based or dataflow-based models.；Increase training data with more network IO clones to help the model recognize the pattern.；Add features that recognize common boilerplate patterns like HTTP request-response.

### case_id=4641 FP long_range_semantics

- 方法: `readData` vs `doCopyFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `static_summary_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Parses hardcoded string constants to populate various character sets and mappings for Tibetan/Sanskrit linguistic processing.
- B 摘要: Copies a file from source to destination using NIO channels, verifying completeness and optionally preserving file date.
- 静态失败原因: Static model likely focused on superficial similarities like exception handling (IOException), try-catch-finally structure, and general Java boilerplate, missing the distinct high-level purposes due to lack of deep semantic understanding.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB requires functional similarity; these two functions perform completely different tasks (data initialization vs. file copy), so they are correctly labeled as non-clones.
- 行为差异: Reads static strings vs. reads/writes files；Populates data structures in memory vs. transfers bytes between channels；No file I/O vs. extensive file I/O with resource management；No error handling on missing files vs. throws IOException for directory destination or incomplete copy
- 修正建议: Incorporate structure-aware representations that capture high-level intent；Improve training with more diverse negative examples contrasting different functionalities；Use more fine-grained tokenization or additional context to differentiate API usage patterns

### case_id=4642 FP long_range_semantics

- 方法: `actionPerformed` vs `copyFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `static_summary_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Handles various GUI action commands by opening file choosers, setting preferences, and updating UI components.
- B 摘要: Copies a file from source to destination using NIO FileChannel transfer.
- 静态失败原因: The model likely overfitted to the presence of file-related keywords (e.g., 'File', 'FileChannel', 'InputStream') in both snippets, combined with the truncation of the long code A losing its overall GUI context, leading to a false positive.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB would not consider these clones because they have entirely different functionality, inputs, outputs, and side effects, with no meaningful semantic overlap.
- 行为差异: A is an event handler for GUI actions; B is a utility function for file I/O.；A modifies application preferences and UI state; B only copies file contents.；A has complex control flow with multiple conditions; B is straightforward sequential code.；A does not perform file copying; B does not interact with GUI.
- 修正建议: Improve handling of long functions by splitting or using hierarchical representations to capture full semantics.；Incorporate better detection of functional purpose beyond local lexical cues.

### case_id=4643 FN partial_functionality

- 方法: `modifyApplicationMessage` vs `getFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Modifies a localized properties file by updating or adding a key-value pair, creating the file from an English template if missing.
- B 摘要: Retrieves a file from the user directory, copying it from a classpath resource if it does not already exist.
- 静态失败原因: Static BERT models often rely on token-level overlap and surface structure. Here, the Jaccard similarity is low (0.156), but the model might have been misled by common API calls like File, InputStream, and FileWriter. However, the semantic purpose differs significantly, which a static encoder without execution may not capture.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled this as a clone due to the overlapping file I/O pattern and resource copying, which is common in utility methods. The annotator might have focused on the similar high-level task of 'ensuring a file is available' and 'handling file operations'.
- 共享行为: Both check if a file exists and optionally create it from a classpath resource.；Both use File, InputStream, and file writing operations.；Both handle IOException-like exceptions (A catches Exception, B throws IOException).
- 行为差异: A specifically modifies properties content (key-value updates), B only copies the entire file.；A involves reading and rewriting a properties file in a line-by-line manner, B uses bulk copy via IOUtils.；A takes parameters for locale, message name, and value; B has no parameters and derives filename from a method call.；A returns void, B returns a File object.
- 修正建议: Enhance model with dataflow analysis to distinguish write vs copy operations.；Use contrastive learning on pairs with similar I/O patterns but different intents.；Incorporate method signature and context (e.g., class name, method name embeddings).

### case_id=4644 FN partial_functionality

- 方法: `copyFile` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a file from source to destination using FileChannel transferTo.
- B 摘要: Retrieves a resource as an InputStream, with HTTP caching logic that downloads and caches the resource locally.
- 静态失败原因: Low token Jaccard similarity and divergent surface structures (different method names, parameter types, control flow) led the static model to overlook the underlying shared I/O behavior.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider this a Type-4 clone because both functions implement data transfer from an input source to a file, a common I/O pattern, despite differing in complexity and specific domain.
- 共享行为: Both perform file I/O operations involving reading from an input source and writing to an output file.；Both handle streams with try-catch-finally for resource cleanup.
- 行为差异: A is a simple file copy; B involves URL connection, HTTP status checking, and caching logic.；A throws IOException; B catches all exceptions and returns null.；A is not synchronized; B is synchronized.；A uses FileChannel; B uses BufferedInputStream/BufferedOutputStream.
- 修正建议: Enhance model to recognize higher-level I/O patterns through graph-based dataflow analysis.；Include more training examples of I/O pairs with varying complexity.；Use contrastive learning to focus on functional similarity beyond lexical overlap.

### case_id=4645 FP lexical_or_api_overlap

- 方法: `loadExistingAntlibs` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Loads ant library definitions from classpath resources by reading a resource listing and resolving URIs.
- B 摘要: Performs a Google image search by constructing a URL, fetching the page, and extracting image URLs.
- 静态失败原因: Static BERT/GraphCodeBERT likely overemphasized the common boilerplate (URL opening, BufferedReader) and missed the semantic divergence in what they do with the data.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely considers them non-clones because the overall functionality and intent are entirely different despite some shared I/O patterns.
- 共享行为: Both open a URL connection and read text line by line；Both use BufferedReader and InputStreamReader；Both catch exceptions and handle them
- 行为差异: Different purpose: loading antlibs vs. image search；Different URL construction and data extraction logic；Different error handling: A throws RuntimeException, B shows error dialog
- 修正建议: Incorporate more abstract semantic features like method purpose；Use data flow analysis to differentiate data processing；Train on more diverse examples to reduce boilerplate bias

### case_id=4646 FP boilerplate_overlap

- 方法: `copyOverWarFile` vs `readData`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Copies a WAR file from one directory to another and moves/unzips it.
- B 摘要: Reads and parses a configuration file, populating multiple sets and hash maps for Tibetan transliteration.
- 静态失败原因: Possible model confusion due to both involving file I/O, loops, and exception handling, despite low token overlap.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB correctly labels non-clone because the functions serve completely different purposes with no shared functionality.
- 共享行为: Both use file I/O operations；Both employ loops and conditional logic
- 行为差异: Function A copies a single file type; Function B parses complex data structures；Function A writes a file; Function B reads and processes text；Function B initializes many string sets and hash maps; Function A does not
- 修正建议: Enhance training data with more diverse non-clone pairs；Use graph-based representations to capture data flow differences；Incorporate method-level semantic summaries from code documentation

### case_id=4647 FP lexical_or_api_overlap

- 方法: `main` vs `copyFromTo`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Main method for an adapter generator that reads a Prolog file, parses it, generates adapter classes, and packages them into a JAR file.
- B 摘要: Static method that copies a file from a source to a destination using FileChannel, with error handling and preservation of last modified timestamp.
- 静态失败原因: The static model likely overemphasized lexical and API-level overlaps such as common imports (File, FileInputStream/OutputStream), exception handling patterns (try-catch blocks with print statements), and similar structural elements (e.g., System.out.println), leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would label these as non-clones because they perform entirely different tasks with no overlap in functionality beyond basic file I/O, which is too generic to be considered a clone.
- 共享行为: Both perform file I/O operations；Both handle exceptions (IOException, etc.)；Both print messages to console
- 行为差异: Function A generates code and creates a JAR file, while function B simply copies a file；Function A involves parsing, code generation, and class loading; function B does not；Function A has complex control flow with multiple file and class manipulation steps; function B is linear copy
- 修正建议: Incorporate data flow analysis to distinguish actual file operations；Use a model that captures higher-level semantics or task-specific patterns；Add features that measure behavioral similarity beyond surface syntax

### case_id=4648 FN partial_functionality

- 方法: `getDatasetsList` vs `File2String`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches a list of dataset names from a remote server URL, caches the result, and returns the list.
- B 摘要: Reads the entire content of a file (from filesystem or classpath) and returns it as a single string.
- 静态失败原因: Static BERT models rely heavily on token overlap and local structural patterns; the low Jaccard similarity (0.256) and different return types, method names, and caching logic cause the model to miss the shared core I/O pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this as a clone because both functions follow the same high-level pattern: read lines from an external source, accumulate them (list vs string buffer), and handle I/O exceptions, which is considered a Type-3/Type-4 clone despite different return types and sources.
- 共享行为: Both open an input stream from an external source (URL or file).；Both use BufferedReader to read lines of text.；Both handle IO exceptions with catch blocks.；Both close the reader in a finally-like manner (though B closes inside try).
- 行为差异: A returns List<String>; B returns String (concatenated lines).；A caches results in a HashMap; B does not cache.；A reads from a URL with query parameter; B reads from a local file or classpath resource.；A uses synchronization; B does not.
- 修正建议: Enrich training data with more examples of I/O reading patterns with varied output types.；Incorporate control flow graph or data flow features to capture similar loop structures.；Use models that better understand high-level intent, such as code summarization or API usage patterns.

### case_id=4649 FN lexical_or_api_overlap

- 方法: `sendExceptionToServer` vs `readRemoteFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.6`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends an exception report to a server via HTTP POST and prints the response.
- B 摘要: Reads a remote file via HTTP GET and returns its content as a string.
- 静态失败原因: Static models rely on lexical and structural similarities; the high overlap of API calls (URL, BufferedReader, readLine) and exception handling may mislead them into predicting clone, but the model predicted non-clone, indicating it captured semantic differences? Actually the model predicted 0 (non-clone) but BCB says 1; so the model correctly identified differences. However, the error is FN meaning model missed a clone; here I think model was correct. So rephrase: Static BERT likely failed because it over-relied on lexical overlap patterns, not capturing the overall semantic intention mismatch.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB might consider the common URL-reading boilerplate as sufficient for a Type-4 clone, overlooking the different purposes and data flows.
- 共享行为: Both open a URL connection and read input using BufferedReader.；Both handle IOException.
- 行为差异: A writes data to the connection (POST), B only reads (GET).；A includes extensive parameter encoding and sends a multi-field form, B does not.；A prints the response and does not return, B returns the concatenated response.；A checks for 'success' response, B reads until EOF.
- 修正建议: Incorporate dataflow analysis to distinguish read-only vs. read-write operations.；Use models that capture function intent rather than API usage patterns.；Consider function signatures and return types as discriminative features.

### case_id=4650 FP lexical_or_api_overlap

- 方法: `main` vs `SRWGuiClient`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: A main method that fetches a URL and prints its contents line by line to the console.
- B 摘要: A GUI browser constructor that fetches a URL, optionally transforms XML/XSLT, and displays the result in an editor pane.
- 静态失败原因: Static models like BERT or GraphCodeBERT may over-rely on lexical overlap and API usage (e.g., URL, BufferedReader, readLine). Both functions share similar API calls, leading to a false positive even though the overall semantics diverge.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels Type-4 (similar but not equivalent) as clones only when the shared functionality is the primary intent. Here, the URL reading is a minor part of B; the overall functionalities are fundamentally different (console vs GUI, simple vs complex), so BCB likely considers them non-clones.
- 共享行为: Both open a URL；Both read input line by line using BufferedReader；Both handle IOException
- 行为差异: A is a simple command-line program; B is a GUI constructor with window setup and complex UI；B includes XSLT transformation logic; A does not；B outputs to a JEditorPane; A prints to System.out；B has error handling for TransformerException; A does not
- 修正建议: Incorporate function-level context such as method type (main vs constructor) and surrounding class structure；Use dataflow or control-flow features to distinguish simple reading from complex processing；Apply a clone detection threshold that penalizes disproportionate size differences

### case_id=4651 FN partial_functionality

- 方法: `getHTML` vs `callService`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches HTML content from a URL and optionally writes it to a file.
- B 摘要: Fetches service response from a URL and stores it in an instance variable.
- 静态失败原因: Static BERT models rely on token overlap and surface structure; low Jaccard similarity (0.27) and different API usage (HttpURLConnection vs URL.openStream) cause it to miss the semantic similarity of the core task.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels pairs as clones if they perform the same high-level operation (fetching a URL's content) even if implementation details vary, accepting Type-3/4 clones.
- 共享行为: Both open a URL, read content line by line, and accumulate into a string buffer.
- 行为差异: A returns the content as a String and may write to file; B stores in instance variable and does not write to file.；A sets User-Agent header; B does not.；A uses HttpURLConnection with explicit connect/disconnect; B uses url.openStream().；A throws IOException; B catches exceptions internally and sets error message.
- 修正建议: Use contrastive learning with functional labels.；Augment training with semantic role labeling or program analysis to identify common subtasks.

### case_id=4652 FN lexical_or_api_overlap

- 方法: `copyResource` vs `copyFileTo`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource (URL or local file) to a destination file using byte-by-byte reading.
- B 摘要: Copies a file from source path to destination path with buffered reading.
- 静态失败原因: Low token overlap (0.25) and differing signatures/instance variables cause the model to miss semantic similarity.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB often labels similar file-copying functions as clones even with different source handling and error types, considering the core functionality same.
- 共享行为: Both copy an input stream to an output stream；Both involve file system operations；Both close streams after copying
- 行为差异: Source: URL+file vs only file；Error handling: generic Exception vs specific exceptions；Read method: byte-by-byte vs buffered；Method signature: private non-static vs public static
- 修正建议: Include token-level synonym replacement；Use AST-based features to capture structural similarity；Add training data with varied implementations of same functionality

### case_id=4653 FN benchmark_preference_bias

- 方法: `write` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Writes a JAR output stream by aggregating entries from included JAR files, skipping manifest and zero-size entries.
- B 摘要: Launches a NexOpen project configuration, processing pom.xml files, setting Hibernate properties, and scheduling an install action.
- 静态失败原因: The static model did not fail; it correctly predicted non-clone (0). The error is a false negative in BCB's annotation.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: The BCB label of 1 appears to be an annotation error, as the two functions share no common functionality or partial similarity.
- 行为差异: Function A writes a JAR file; function B launches a project configuration.；A uses JarOutputStream and IOUtils.copy; B uses ContentHandlerTemplate, Properties, and InstallProjectAction.；A iterates over jar entries; B handles Maven POM files and Hibernate dialect.；A has no project or launch context; B is Eclipse-related with ILaunchConfiguration and IProgressMonitor.
- 修正建议: Re-evaluate the BCB label for this pair; it should be corrected to non-clone.；Consider adding more filtering rules to avoid unrelated functions being paired.

### case_id=4654 FP boilerplate_overlap

- 方法: `postData` vs `SRWGuiClient`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Posts form data to a URL via HTTP POST and reads the response.
- B 摘要: Constructs a Swing browser GUI that fetches an initial URL, parses XML with optional XSLT, and displays HTML.
- 静态失败原因: The model likely overfocused on common lexical tokens (URL, BufferedReader, InputStreamReader, IOException) and similar boilerplate I/O patterns, while ignoring the larger context such as method signature, return type, GUI construction, and XML processing. Static BERT-based models often suffer from this token-level overemphasis, leading to false positives when code shares library usage but differs in purpose.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels these as non-clones because their overall functionality is entirely different: one is a simple HTTP POST utility, the other is a complex GUI browser constructor. Despite sharing some low-level I/O library calls, the semantic intent and behavior are not functionally similar. BCB's annotation preference for Type-3/4 clones still requires a core functional similarity, which is absent here.
- 共享行为: Both open a URL connection and read input using BufferedReader and InputStreamReader.；Both handle IOException via try-catch (though B also catches TransformerException).；Both use the java.net.URL class to create URL objects.
- 行为差异: Function A sends HTTP POST (with output stream and request properties); function B performs HTTP GET (URL.openStream).；Function A writes data to the output stream; function B does not write any data.；Function B sets up a full Swing GUI window with panels, buttons, and text fields; function A has no GUI.；Function B involves XML parsing and optional XSLT transformation to produce HTML; function A does not handle XML.
- 修正建议: Incorporate method signature (name, parameters, return type) as a stronger signal.；Use graph-based representations that capture control and data flow to distinguish utility methods from constructors.；Add training examples where common I/O patterns appear in functionally unrelated methods.；Include attention to long-range dependencies and unique operations (e.g., Swing components, XSLT) to penalize false matches.

### case_id=4655 FN partial_functionality

- 方法: `handler` vs `read`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Opens a URL, reads lines, and extracts substrings to update a map based on target page configuration.
- B 摘要: Opens a stream from a name (URL or file) and delegates reading to another method, returning a status code.
- 静态失败原因: Static BERT/GraphCodeBERT likely focused on low token overlap (0.236) and surface-level differences like method names, parameter types, and control flow, missing the shared core of URL stream opening and exception handling.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considers them clones due to partial functionality similarity: both involve opening a URL stream and handling IO exceptions, a common pattern even though the subsequent processing differs.
- 共享行为: Both open a URL stream using URL.openStream()；Both catch IOException
- 行为差异: A modifies a map entry per line; B returns status and calls another read method；A only handles URL; B also handles file input；A uses BufferedReader for line-by-line reading; B uses BufferedInputStream and delegates；A extracts substrings based on markers; B has no substring extraction
- 修正建议: Incorporate functional role detection to identify common IO operations；Use graph representations that capture data flow from stream opening；Train on more Type-3/Type-4 examples to learn partial similarity patterns

### case_id=4656 FN benchmark_preference_bias

- 方法: `main` vs `PhoneSetImpl`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Sends a POST request to RenRen API with hardcoded parameters and prints the HTTP response.
- B 摘要: Constructs a PhoneSetImpl by reading lines from a URL, parsing each non-header line into a map.
- 静态失败原因: The model likely relied on token-level similarity (Jaccard=0.16) which is low, so it correctly predicted non-clone; it failed to align with BCB's broad annotation that treats this as a clone.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as a clone due to the common I/O pattern of reading from a URL line by line, which is a superficial structural similarity, but the overall functionality differs significantly.
- 共享行为: Both open a URL connection and read lines using BufferedReader
- 行为差异: A sends a POST request before reading; B reads directly from the URL stream；A prints the response; B parses and stores data；A is a static main with hardcoded parameters; B is a constructor taking a URL
- 修正建议: Use functional signature or semantic role detection to distinguish network I/O patterns；Incorporate control flow analysis to separate data processing logic from I/O boilerplate

### case_id=4657 FN partial_functionality

- 方法: `getContent` vs `login`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Executes an HTTP request and returns the response body as a string.
- B 摘要: Performs a login by sending a POST request with encoded credentials and returns a session ID.
- 静态失败原因: Static BERT models rely heavily on token-level similarity and may miss the abstract HTTP I/O pattern due to low Jaccard similarity and different variable/method names, leading to a false negative.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often annotates Type-3/4 clones based on partial functional similarity, and both functions share the core pattern of executing an HTTP request and reading the response line by line.
- 共享行为: Both use BufferedReader to read HTTP response lines；Both perform HTTP communication (request/response)；Both have exception handling
- 行为差异: A receives an HttpUriRequest object; B creates a URL connection manually；A returns the full response body; B extracts and returns a session ID；A sets connection and socket timeouts; B does not；B includes specific login logic (encoding parameters, parsing session ID)
- 修正建议: Use a code representation that captures control/data flow (e.g., AST with edges) to recognize common I/O patterns；Incorporate API usage features (e.g., uses BufferedReader, HttpResponse)；Apply a more lenient threshold for structural matching when high-level behavior overlaps

### case_id=4658 FP boilerplate_overlap

- 方法: `populateResources` vs `executePost`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Loads template files and images from resources, reads content, and saves them as Resource, Image, and Property objects.
- B 摘要: Executes an HTTP POST request to a given URL with parameters and returns the response as a string.
- 静态失败原因: The static BERT model likely overemphasized the shared API calls (URL, openStream, BufferedReader, StringBuffer) and exception handling structure, ignoring the fundamental difference in overall functionality.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clones because the methods have completely different purposes (file/resource initialization vs. HTTP POST), despite some superficial similarities in boilerplate code.
- 共享行为: Both use URL to open connections/streams；Both use BufferedReader and InputStreamReader to read line-by-line；Both use StringBuffer to accumulate lines；Both handle exceptions with try-catch
- 行为差异: populateResources deals with static resource loading and saving; executePost performs dynamic HTTP communication；populateResources writes to Resource objects and saves; executePost writes to an HTTP output stream and returns a string；populateResources loops over multiple URLs; executePost handles a single URL；populateResources has no return value; executePost returns the response string
- 修正建议: Incorporate data-flow analysis to distinguish between reading from a local resource vs. writing to an HTTP connection；Include method-level context (e.g., class name, method name, surrounding code) to capture domain differences；Use graph-based representations that capture the sequence of operations and data dependencies

### case_id=4659 FP lexical_or_api_overlap

- 方法: `callService` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Makes a generic HTTP GET request to a composed URL and stores the raw response body in a field.
- B 摘要: Fetches Google image search results for a track's artist and album, parses the HTML to extract image URLs, and adds them to a list.
- 静态失败原因: The static model likely over-weighted the structural commonality of URL reading boilerplate (URL, BufferedReader, while loop, readLine, close) and missed the semantic divergence in data handling and output.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically considers pairs with strong lexical similarity but different semantics as non-clones. Here the core reading pattern is similar, but the purpose and result processing are entirely different, so BCB labeled 0.
- 共享行为: Both open an HTTP URL connection；Both read the response line by line using BufferedReader；Both close the reader in try-catch block；Both handle IO exceptions
- 行为差异: Function A is a generic web service caller; Function B specifically queries Google Images；Function A stores raw response as string; Function B extracts image URLs from HTML；Function B includes additional string manipulation and conditionals；Function B uses HttpURLConnection with User-Agent; Function A uses simple URL.openStream()
- 修正建议: Incorporate data-flow or control-flow differences；Use graph-based features that capture variable usage paths；Add negative training examples of boilerplate-only pairs

### case_id=4660 FN partial_functionality

- 方法: `doGet` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.5`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Handles HTTP GET requests to retrieve and render a portal page, with error handling and caching logic.
- B 摘要: Copies a file from one location to another starting at a given offset, with input validation and error handling.
- 静态失败原因: Static BERT models rely on lexical and structural overlap, which is low (token Jaccard 0.08). They fail to recognize high-level semantic parallels like input validation and error handling patterns.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as entry-point methods that process user input and perform a task with error reporting, aligning with Type-4 functional similarity.
- 共享行为: Parse numbers from strings with NumberFormatException handling；Output error messages on invalid input；Use try-catch blocks for I/O exceptions
- 行为差异: Function A is a web request handler with complex page visibility and caching; Function B is a simple file copy utility；Function A uses HTTP response and servlet context; Function B uses command-line arguments and file streams；Function A involves logging, property lookups, and rendering; Function B involves byte-by-byte copying
- 修正建议: Enhance models with semantic understanding of program intention；Use AST or graph-based representations to capture control flow and data flow；Incorporate domain-specific knowledge (e.g., web vs. file I/O) to distinguish functionalities

### case_id=4661 FN benchmark_preference_bias

- 方法: `copyResource` vs `tail`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Copies a resource (from URL or file) to a destination file byte by byte.
- B 摘要: Implements the Unix 'tail' command: reads the last 1024 bytes of a file and optionally follows new content with a loop and sleep.
- 静态失败原因: The static model correctly identified them as non-clones (prediction=0) because of very different control flow and purpose. The BCB label likely reflects a more lenient or error-prone annotation, so the model did not fail—it disagreed with a potentially incorrect gold label.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider both as 'resource copying' or 'I/O utility' functions due to their similar low-level stream handling, despite the significant algorithmic differences. Alternatively, this could be a labeling error or an example of broad Type-4 semantic similarity.
- 共享行为: Both read bytes from a source (file or stream) and write to an output stream；Both handle IOExceptions and close streams；Both use basic byte-by-byte or buffered copy operations
- 行为差异: copyResource copies the entire source; tail copies only the last 1024 bytes (with offset seek)；tail includes command-line parsing, file system checks, and a loop for follow mode；copyResource writes to a FileOutputStream; tail writes to System.out；tail uses seek and has sleep-based polling
- 修正建议: Review BCB annotation for this pair; if it's an error, correct the label；Add negative examples with similar low-level I/O but different high-level functionality to improve model robustness

### case_id=4662 FN library_context_missing

- 方法: `doRawRequest` vs `httpRequestByPOST`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `context_recovery_then_expert`；动态可解性: `low`；执行优先级: `medium`
- A 摘要: Sends a POST request with raw data via URLConnection and returns the response body as a string.
- B 摘要: Sends a POST request with form parameters via HttpClient, handles HTTP errors, and returns the response body or null on failure.
- 静态失败原因: Static BERT/GraphCodeBERT likely relied on token overlap (20%) and syntactic structure; the different libraries and low shared vocabulary masked the semantic similarity of the HTTP POST pattern.
- 静态 case study: 该类错误缺少关键上下文或需要深层语义，纯静态方法不可靠。
- 动态 case study: 动态执行价值较低：样本可能依赖库、框架、网络、GUI、数据库或项目上下文，需要先恢复环境或 mock 依赖。
- BCB 偏好解释: BCB often labels Type-3 or Type-4 clones as positive, focusing on core functionality (sending POST and reading response) rather than exact API or error handling details.
- 共享行为: Both perform HTTP POST requests to a server.；Both read the response line by line and accumulate into a StringBuffer.；Both return the response body as a string (in successful cases).
- 行为差异: Different HTTP libraries: URLConnection vs HttpClient.；Input type: raw string data vs list of NameValuePair form parameters.；Error handling: A throws IOException; B returns null and sets error fields for non-2xx or exceptions.；URL source: hardcoded constant vs method parameter.
- 修正建议: Normalize library-specific API calls to a common representation (e.g., generic 'httpPost' operation).；Incorporate knowledge of HTTP client patterns to recognize functionally equivalent code using different libraries.；Use dataflow-aware models to track that both write to output stream and read from input stream.

### case_id=4663 FN boilerplate_overlap

- 方法: `convert` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Converts ACRNEMA stream files to DICOM format, handling pixel data and UID generation.
- B 摘要: Retrieves a resource by name, caching it locally from a URL, and returns an InputStream.
- 静态失败原因: Static BERT/GraphCodeBERT likely relied on token overlap and common I/O patterns, missing the distinct semantic intent (DICOM conversion vs. resource caching). The long and complex code may have caused attention dilution.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may have mislabeled this pair due to superficial token overlap (e.g., BufferedInputStream, FileOutputStream) and similar control flow patterns, despite lack of functional similarity.
- 共享行为: Use of I/O streams (FileInputStream, BufferedInputStream, FileOutputStream)；Print statements for progress/debugging；Try-finally blocks for resource cleanup
- 行为差异: Function A processes DICOM medical image data; Function B retrieves and caches remote resources；Function A writes output to a file; Function B returns an InputStream from cache or remote；Different domain-specific operations (UID generation, pixel inflation vs. HTTP requests, caching)
- 修正建议: Incorporate semantic role labeling or domain-specific embeddings；Use call graph or API usage patterns to differentiate library functions；Apply attention to unique identifiers and domain-specific terms (e.g., DcmParser, PixelData, URLConnection)

### case_id=4664 FN partial_functionality

- 方法: `copyResource` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource from a URL or file to a destination file by reading bytes and writing to an output stream.
- B 摘要: Tests a StraightStreamReader by writing 256 bytes to a file and reading them back using various read methods to verify correctness.
- 静态失败原因: Static BERT/GraphCodeBERT likely failed due to low lexical overlap (Jaccard=0.18) and large differences in length and structure, missing the high-level functional similarity in I/O operations.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider this a Type-4 clone because both functions perform file I/O operations (reading from input, writing to output) and share a core pattern of copying data, even though the purposes differ.
- 共享行为: Both open file input and output streams；Both read bytes in loops；Both close streams；Both check file existence
- 行为差异: A reads from URL or file; B writes then reads；A has a single read-write loop; B has multiple loops with different read methods；A throws exception on missing resource; B throws exception if file already exists；B uses a custom StraightStreamReader; A uses generic InputStream
- 修正建议: Incorporate structural AST matching for I/O patterns；Use data-flow analysis to detect reading and writing cycles；Consider domain-specific knowledge about file copying

### case_id=4665 FN lexical_or_api_overlap

- 方法: `sendExceptionToServer` vs `getURLContent`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.55`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends exception details to a remote server via HTTP POST and prints the response.
- B 摘要: Fetches the content of a URL as a string via HTTP GET.
- 静态失败原因: Static BERT/GraphCodeBERT likely overemphasized the lexical and API token overlap (URL, URLConnection, BufferedReader, StringBuilder) while missing the divergent control flow and data manipulation (POST vs GET, parameter encoding, conditional writing).
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB annotators may consider these clones due to overlapping URL connection and reading boilerplate, accepting broad Type-3/4 similarity where only part of the functionality (reading from URLConnection) is shared.
- 共享行为: Both open a URL connection and read lines from the response using BufferedReader
- 行为差异: Function A writes POST data to the output stream; function B only reads；Function A includes error handling and prints status; function B returns the content；Function A builds complex encoded parameters; function B uses default encoding
- 修正建议: Improve sensitivity to data flow (e.g., presence of OutputStreamWriter indicates write operation)；Incorporate more robust structural matching that distinguishes between read-only and read-write URL connections

### case_id=4666 FP lexical_or_api_overlap

- 方法: `readZoneIDs` vs `SRWGuiClient`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads integers from a resource file line by line and returns them as a set.
- B 摘要: Constructs a GUI browser that fetches a URL, parses XML, applies XSLT transformation, and displays the result.
- 静态失败原因: Static BERT models likely overfocused on shared lexical patterns like 'URL', 'openStream', 'BufferedReader', 'try-catch', and 'InputStreamReader', ignoring the drastic difference in overall functionality and control flow.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would label these as non-clones because they perform entirely different high-level tasks (simple utility vs. GUI browser) and the code structures are vastly different despite some superficial API similarities.
- 共享行为: Both open a URL stream and read input line by line.；Both use try-catch blocks for exception handling.；Both use InputStreamReader and BufferedReader/LineNumberReader.
- 行为差异: Function A is a static method that returns a set of integers; function B is a constructor with no return value.；Function A has no GUI components; function B builds a complete Swing GUI.；Function A only parses integers; function B parses XML, applies XSLT, and handles stylesheets.；Function A reads from a class resource; function B reads from a network URL.
- 修正建议: Incorporate control flow and data flow graph features to distinguish different program structures.；Use graph-based models that capture broader context and function signatures.；Train models with more diverse negative examples to reduce false positives from API overlap.

### case_id=4667 FN partial_functionality

- 方法: `getDatasetsList` vs `testNetworkHTTP`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Synchronized method to fetch and cache a list of dataset names from a remote server via HTTP GET with a query parameter.
- B 摘要: Test method that performs multiple HTTP GET requests to hardcoded URLs, reading and discarding response lines.
- 静态失败原因: Low token overlap (0.17), different method signatures, and distinct control flow (caching vs. multiple requests) likely caused the model to focus on surface-level differences, ignoring the shared network I/O pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label these as clones because both share the core pattern of network I/O: creating a URL, opening a stream, wrapping in BufferedReader, reading lines in a loop, and handling exceptions. The structural similarity in resource management and I/O operations is sufficient under broad Type-3/4 definitions.
- 共享行为: Both open HTTP connections and read lines using BufferedReader.；Both handle IOException with logging or printing.；Both perform cleanup in a finally block (close reader or disconnect).
- 行为差异: A caches results in a HashMap; B does not cache.；A returns a List<String>; B is void.；A uses a single dynamic URL; B uses multiple hardcoded URLs.；A throws RuntimeException on error; B prints stack trace.
- 修正建议: Incorporate data flow analysis to detect common I/O patterns.；Use larger context or graph representations sensitive to resource lifecycle.；Train with more examples of partial functional similarity.

### case_id=4668 FN partial_functionality

- 方法: `File2String` vs `GetResponse`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a file from local filesystem or classpath and returns its content as a single string, with error handling that prints to stdout and exits on failure.
- B 摘要: Performs an HTTP GET request to a URL and returns the response body as a single string, with minimal error handling.
- 静态失败原因: Low lexical overlap (token Jaccard 0.239) and different API calls (FileInputStream vs HttpURLConnection) likely caused the model to miss the underlying structural similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often annotates broad Type-3 clones as positive, focusing on the core algorithmic pattern of reading and concatenating text lines, even if input sources and error handling differ.
- 共享行为: Both read text line by line from an input source；Both concatenate lines into a single string；Both return the resulting string or null on failure
- 行为差异: Input method: file path vs URL；Error handling: prints and exits vs silent；Source of data: local file/system resource vs HTTP response
- 修正建议: Use AST-based or dataflow features that abstract away concrete API calls；Normalize I/O operations into generic 'readLines' patterns；Incorporate structural matching techniques like tree-edit distance

### case_id=4669 FN boilerplate_overlap

- 方法: `getHTML` vs `testNetworkHTTP`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches HTML from a given URL with specified encoding and optionally saves to a file, returning the HTML content.
- B 摘要: Test method that performs multiple HTTP GET requests to send sensitive device data via query parameters and discards the responses.
- 静态失败原因: Static BERT/GraphCodeBERT models likely focused on lexical differences and low token overlap (0.275), missing the broader structural similarity in HTTP connection handling. The models may have been misled by the distinct method signatures, return types, and hardcoded URLs in function B.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may have labeled these as clones due to the common pattern of HTTP GET requests using HttpURLConnection, despite the different purposes and data flows. The structural similarity in connection setup and read loop might be considered sufficient for a Type-3 clone.
- 共享行为: Both use HttpURLConnection to open connections；Both read lines from input stream using BufferedReader；Both catch IOException and print stack trace；Both disconnect the connection in finally block
- 行为差异: Function A takes parameters for URL, encoding, and file path; Function B uses hardcoded URLs and no parameters；Function A returns fetched HTML; Function B is void and discards all data；Function A optionally writes to file; Function B has no such behavior；Function B sends sensitive data via query parameters; Function A does not
- 修正建议: Improve representation to better capture API usage patterns and control flow；Incorporate data flow analysis to distinguish between reading vs. discarding data；Use graph-based models that can match subgraph patterns of HTTP connections

### case_id=4670 FN partial_functionality

- 方法: `doGet` vs `copyJar`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Handles HTTP GET request for a page, including page lookup, permissions, rendering, logging, caching, and statistics.
- B 摘要: Copies a file from source to destination using Java NIO FileChannel.
- 静态失败原因: The model correctly predicted non-clone based on low token overlap and different syntactic structure. However, it failed to recognize the abstract I/O pattern that BCB might have used, possibly due to lack of training on such weak semantic similarities.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have considered them clones because both involve file I/O operations with similar error handling patterns (try-catch-finally, logging severity). The partial functional similarity in resource management and writing to files could be seen as Type-4 or broad Type-3 clone.
- 共享行为: Both perform file I/O operations with exception handling and logging.；Both have a try-catch-finally structure for resource management.
- 行为差异: A is a complex web request handler with multiple branches, permissions, caching, and statistics; B is a straightforward file copy.；A uses FileWriter, B uses FileChannel.transferFrom.；A has extensive logging and error handling for various scenarios; B has minimal error handling with only a catch and finally.；A writes HTML content, B copies binary content.
- 修正建议: Incorporate dataflow and control flow analysis to detect similar I/O resource patterns.；Train on more examples where functional similarity is based on behavior rather than token overlap.；Use graph-based representations that capture resource acquisition and release patterns.

### case_id=4671 FP lexical_or_api_overlap

- 方法: `readTwitterFead` vs `handleHandshake`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a Twitter feed via HTTP GET and returns the response body as a string.
- B 摘要: Handles a Minecraft handshake packet by validating the server key and possibly joining a session.
- 静态失败原因: Static BERT models often rely on token-level overlap and structural patterns. Here, both functions use common vocabulary (BufferedReader, InputStream, try-catch, etc.) and have similar control flow (conditional checks, loops, exception handling), leading to high similarity in embeddings despite different semantics.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled non-clone because the functions serve entirely different purposes and share only generic I/O patterns, which BCB typically does not consider as clones.
- 共享行为: Both use BufferedReader and InputStreamReader to read input.；Both handle exceptions with try-catch and print stack traces.；Both involve network communication (HTTP vs Minecraft protocol).
- 行为差异: Function A fetches a fixed Twitter URL, Function B processes a Minecraft packet with conditional logic.；Function A returns the downloaded content, Function B sends packets and shuts down network on failure.；Function B has complex authentication logic (parsing hex, checking server response), Function A is a simple HTTP GET.；The network protocols, endpoints, and data formats are completely different.
- 修正建议: Incorporate dataflow or control-flow analysis to distinguish genuine I/O boilerplate from domain-specific logic.；Use contrastive learning with more diverse negative samples that share boilerplate but differ in purpose.；Add a pre-filter to discard pairs with very low semantic overlap (e.g., method name similarity or external API usage).

### case_id=4672 FP boilerplate_overlap

- 方法: `getUser` vs `getFrameworkFactory`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Loads a user from a DAO, falling back to parsing a configuration file if not found.
- B 摘要: Loads an OSGi framework factory from a service file by reading the first non-comment line.
- 静态失败原因: The model overemphasized the common API sequence (getResource, BufferedReader, readLine) and ignored the distinct semantics inside the loop and the different return handling.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely relies on overall functionality rather than shared boilerplate; two functions with entirely different purposes (user management vs OSGi service loading) are not considered clones.
- 共享行为: Both retrieve a resource URL from the classpath；Both open a BufferedReader on the resource stream；Both read lines in a loop
- 行为差异: Function A parses colon-delimited fields to create a User object; Function B uses the line as a class name to instantiate via reflection；Function A saves the user to a DAO; Function B returns an instantiated factory；Function A prints stack trace and returns null on error; Function B throws an exception；Function A handles missing user by searching a file; Function B fails if the file does not contain a valid entry
- 修正建议: Incorporate dataflow analysis to track how read content is processed；Use type-aware representations to differentiate return types and error paths；Employ contrastive learning on pairs with similar boilerplate but different semantics

### case_id=4673 FN partial_functionality

- 方法: `login` vs `readIntoList`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Logs in to a service by sending POST request with email and password, reads session ID from response, and returns it.
- B 摘要: Reads HTML from a URL, parses anchor tags to extract link text and create JMenuItems with action commands, and populates a map.
- 静态失败原因: Low token similarity (0.156) and different vocabulary (e.g., 'login', 'URLEncoder' vs 'JMenuItem', 'ActionListener') caused the model to miss the shared pattern of URL reading and line processing. Static BERT relies heavily on lexical overlap, which is minimal here.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as clones under a broad Type-4 category of 'methods that perform network communication and parse response line by line', ignoring differences in request method and parsing logic due to high-level functional overlap.
- 共享行为: Both open a URL connection and read lines from an input stream using BufferedReader and InputStreamReader；Both use try-catch for exception handling；Both involve closing the reader after processing
- 行为差异: Function A sends a POST request with encoded parameters; Function B only reads (GET)；Function A extracts a single session ID from the first line; Function B parses each line for HTML anchor tags and creates multiple menu items；Function A modifies session state and returns a string; Function B is void and populates a map with GUI components；Function A adds action listeners to created items; Function B does not
- 修正建议: Use graph-based models that capture control flow and data dependencies (e.g., AST, CFG) to abstract away syntactic differences；Incorporate explicit semantics of library calls (e.g., URLConnection, BufferedReader) as features；Train on functional similarity tasks that emphasize shared subroutines rather than overall equivalence

### case_id=4674 FP boilerplate_overlap

- 方法: `populateResources` vs `getTicketsForQueue`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.98`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Loads templates and images from resource paths and saves them as persistent objects.
- B 摘要: Fetches open tickets for a given queue from a Request Tracker REST API and returns a list.
- 静态失败原因: The model likely focused on common boilerplate patterns (BufferedReader readLine loop, try-catch blocks, logging) and ignored the substantive differences in API usage and purpose.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely considers these non-clones because they perform completely different tasks (resource initialization vs ticket retrieval) with no shared high-level semantics.
- 共享行为: Both read data line by line using BufferedReader
- 行为差异: A loads local resources and saves to database; B queries remote API and returns results；A is static void; B is instance method returning List<RTTicket>；Different exception handling and error logging；Different API calls and data types used
- 修正建议: Focus on method signature and return type；Incorporate external library calls (e.g., HttpGet vs URL.openStream) as distinguishing features；Use data flow analysis to capture what the function computes

### case_id=4675 FP lexical_or_api_overlap

- 方法: `getTicketsForQueue` vs `doVersionCheck`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches open tickets for a queue from a Request Tracker server, parses ticket IDs from response, then retrieves each ticket.
- B 摘要: Fetches and parses a version check file from a URL to get development and stable build versions, then invokes another method with those versions.
- 静态失败原因: Static BERT/GraphCodeBERT may have overemphasized overlapping tokens like 'BufferedReader', 'InputStreamReader', 'readLine', 'startsWith', and the try-catch pattern for IOException, missing the semantic differences in data processing and overall goal.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels as non-clone because the functions have entirely different domain purposes (ticket retrieval vs version checking) and different output/usage patterns, despite some shared HTTP reading boilerplate.
- 共享行为: Both establish an HTTP connection to a URL；Both read lines from a BufferedReader wrapping an InputStreamReader；Both handle IOException with logging/error display；Both use a while loop to parse lines with prefix checks
- 行为差异: Function A queries for specific queue and ticket status; Function B fetches a generic version check file.；Function A processes ticket IDs and fetches individual tickets; Function B extracts build version strings and calls another method.；Function A has nested HTTP calls and error handling for ticket retrieval; Function B is a single HTTP read.；Function A returns a list; Function B does not return a value and shows/hides wait cursor.
- 修正建议: Improve representation of control flow and data dependencies beyond token sequences.；Incorporate more structural information like AST or data flow to distinguish between different parsing tasks.

### case_id=4676 FP lexical_or_api_overlap

- 方法: `getFrameworkFactory` vs `SRWGuiClient`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Loads an OSGi framework factory by reading a service file and instantiating the specified class.
- B 摘要: Constructs a Swing browser GUI that fetches and renders XML/XSLT content from a URL.
- 静态失败原因: Static BERT/GraphCodeBERT may have been misled by the common API calls (BufferedReader, InputStreamReader, URL.openStream()) and the try-catch structure, causing a false positive based on lexical or API overlap despite low token Jaccard.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB correctly labels this as non-clone because the functionalities are entirely different, one being a framework factory loader and the other a GUI browser constructor.
- 共享行为: Both use BufferedReader and InputStreamReader to read from a URL.；Both handle I/O exceptions.
- 行为差异: Function A loads a class from a service file; Function B processes XML and displays HTML.；Function A is static and throws an exception; Function B is a constructor that sets up a GUI.；Function A has no GUI or user interaction; Function B involves complex UI and event handling.；Function A is short and focused; Function B is long and involves multiple sub-tasks.
- 修正建议: Incorporate deeper semantic understanding that differentiates between loading a class and rendering web content.；Use control flow and data flow analysis to capture the overall purpose rather than just API usage.；Train on more diverse pairs that have similar API patterns but different high-level tasks.

### case_id=4677 FN benchmark_preference_bias

- 方法: `readData` vs `importRoles`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Initializes various sets and hash maps from static comma-separated strings and reads a configuration file to populate data structures.
- B 摘要: Fetches XML from a URL and parses it into a list of RoleName objects.
- 静态失败原因: The model correctly predicted non-clone due to very low lexical token overlap (Jaccard 0.09) and different method names; it did not find the highly abstract functional similarity that BCB might have assumed.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled as clone based on a broad 'reading data and populating collections' similarity, but this is too abstract and likely a mislabel.
- 共享行为: Both read textual input line by line；Both parse lines to extract tokens and populate collections
- 行为差异: Different sources: static strings and a local file vs. a URL；Different output: global collections vs. return list of objects；Different parsing logic: tokenizer on commas vs. detecting specific tag；Different purpose: initialization of character sets vs. import of role names
- 修正建议: Verify BCB label quality: these two functions have little in common semantically.；If BCB label is an error, ignore; if BCB intended Type-4, it is too broad and not useful.

### case_id=4678 FP partial_functionality

- 方法: `actionPerformed` vs `copyFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Handles various GUI action commands to set application preferences such as Graphviz path, ImageMagick path, date format, look and feel, and other settings.
- B 摘要: Copies a file from source to destination using FileChannel.
- 静态失败原因: The model may have been misled by shared lexical tokens like File, filename, and common Java idioms (try-finally, null checks), despite different functionality. Low Jaccard similarity but presence of file-related code could cause false positive.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB typically labels clones as true only if they share a common functionality. Here, one function handles GUI preferences and the other copies files; no overlapping purpose. Thus BCB labels as non-clone.
- 共享行为: Both methods involve file operations: A uses JFileChooser to select a file, B copies file content.
- 行为差异: A is an event handler for GUI actions; B is a static utility method.；A manipulates UI components and stores preferences; B performs pure file I/O.；A has complex conditional logic and multiple branches; B has a single straightforward file copy.；A interacts with external classes like Suku.kontroller and Resurses; B has no such dependencies.
- 修正建议: Improve training data to include more diverse non-clone pairs with overlapping tokens but different semantics.；Incorporate control-flow and data-flow analysis to distinguish GUI event handling from file I/O.；Use better embeddings that capture long-range semantic context.

### case_id=4679 FN benchmark_preference_bias

- 方法: `doVersionCheck` vs `httpRequestByPOST`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.3`
- 推荐路线: `preference_memory_with_manual_audit`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Reads a version-check URL, parses version and build info, and compares with current build to notify user.
- B 摘要: Performs an HTTP POST request, reads the response body, handles status codes and errors, and returns the response string.
- 静态失败原因: The model likely focused on surface features like different API calls (URL.openStream vs HttpClient), method names, and low token overlap, missing the underlying structural similarity of the reading loop and error handling that BCB considered clone-worthy.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might consider them Type-3 clones due to similar I/O reading loops and error handling boilerplate, and both involve network requests to fetch data, despite different protocols and purposes.
- 共享行为: Both open an input stream to read text data line by line using BufferedReader；Both handle IOException with error handling
- 行为差异: A uses URL.openStream (GET request); B uses HttpClient/HttpPost (POST request)；A parses specific lines (.version, .build); B appends all lines to a buffer；A compares build numbers and shows UI messages; B returns response string or sets error fields；A uses a View parameter for cursor and messages; B has no UI and returns String
- 修正建议: Incorporate more global context to distinguish between specific application logic and generic I/O boilerplate；Use control flow and data dependency analysis to capture deeper similarity beyond token overlap

### case_id=4680 FP long_range_semantics

- 方法: `readData` vs `main`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `static_summary_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Reads and parses predefined string constants and a file to initialize various sets and hash maps used for Tibetan Wylie transliteration.
- B 摘要: Main method that reads a dataset, processes zip file entries, parses rules, evaluates performance using PooledPRCurveMeasure, and prints results.
- 静态失败原因: The static model may have focused on similar API tokens (e.g., StringTokenizer, while, HashSet, System.out.println) and structural patterns of reading and looping without capturing the high-level semantic differences. The long length and truncation of function A likely caused the model to lose the overall context, leading to a false positive.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB would label this as non-clone because the functions have entirely different purposes and operate on different data domains; the only commonality is generic parsing patterns, which is insufficient for a clone annotation.
- 共享行为: Both use while loops to iterate over tokens or entries.；Both write to System.out.；Both may throw exceptions.
- 行为差异: Function A initializes data structures for Tibetan script; Function B evaluates rule performance.；Function A processes strings from global variables; Function B reads command-line args and zip entries.；Function A uses StringTokenizer; Function B uses BufferedReader, ZipFile, and BufferedInputStream.；Function A has no return value and is private static; Function B is public static void main with System.exit.
- 修正建议: Improve model's ability to capture high-level intent by using more context-aware embeddings or incorporating method-level summaries.；Increase training data with diverse long functions to better learn semantic boundaries.；Use graph-based representations that capture data flow and call relationships.

### case_id=4681 FP partial_functionality

- 方法: `doVersionCheck` vs `loadURL`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.85`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Opens a version check URL, reads lines, extracts build numbers, and calls another version check method.
- B 摘要: Opens a URL with optional authentication, reads content, writes it to a temporary file, and updates a status label.
- 静态失败原因: The model likely over-weighted the common patterns (URL, BufferedReader, while loop) and missed the different semantic contexts and distinct method calls (jEdit properties vs file writing), leading to a false positive.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely labels this as non-clone because the overall functionality is different (version check vs file download) despite some structural overlap; they share only a common reading pattern but diverge significantly in purpose and post-processing.
- 共享行为: Both open a URL and read lines using BufferedReader.
- 行为差异: A parses specific version patterns, while B writes all content to a file.；A includes authentication handling, B does not.；A uses jEdit properties, B uses a temporary file.；A shows wait cursor, B updates a label with file size.
- 修正建议: Enhance model to consider the complete call graph or data flow, not just local token sequences.；Incorporate method-level context such as called methods and variable usages.；Use graph neural networks that capture structural dependencies beyond sequential tokens.

### case_id=4682 FN partial_functionality

- 方法: `getFile` vs `saveAttachmentBody`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies its endpoint attribute, and saves to a temporary file.
- B 摘要: Saves an email attachment body to a file and updates the database with size and content URI.
- 静态失败原因: Low lexical overlap (Jaccard 0.10), different method names, and distinct domain-specific APIs (AxisFault vs MessagingException) caused the model to miss the broad functional similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider these as Type-4 clones because both core operations involve downloading/saving file content from a stream, despite different domains and additional processing.
- 共享行为: Open an input stream from a source (URL or part body)；Create a new file or ensure file exists；Write stream content to a file output stream；Close streams and handle I/O exceptions
- 行为差异: Source of data: URL vs email part；Post-processing: XML modification vs database update；Return value: file path vs void；Error handling: AxisFault vs MessagingException/IOException
- 修正建议: Incorporate data flow analysis to recognize the common pattern of stream-to-file transfer；Use a model that captures high-level semantics of resource retrieval and persistence；Include more training examples of Type-4 cross-domain clones

### case_id=4683 FN partial_functionality

- 方法: `modifyApplicationMessage` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Modifies a locale-specific properties file by optionally copying a default English file and then updating or adding a key-value pair.
- B 摘要: Copies a source file to a destination directory using a buffer.
- 静态失败原因: Static BERT models often rely on token similarity and structural overlap; the token Jaccard is low (0.16) and the overall functionality appears different; the file copy part is a small portion of A and may not be captured as the dominant behavior; the model may focus on the method names and overall structure which are dissimilar.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider them clones because both contain a common file copy pattern (read-until-end and write) which is a well-known idiom; even though the contexts differ, the core I/O loop is similar and could be considered a Type-3 clone.
- 共享行为: Both read from an input stream and write to an output stream in a loop until end of stream；Both handle file I/O exceptions
- 行为差异: A's copy is character-based using FileReader/FileWriter while B uses byte array；A's copy is conditional and only for default file；A also includes property modification logic；B is purely file copy
- 修正建议: Use dataflow-aware models that can detect sub-patterns；Augment training with examples of partial functionality similarity；Consider using code summarization to identify common sub-tasks

### case_id=4684 FP boilerplate_overlap

- 方法: `executeHttpGet` vs `getFrameworkFactory`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Executes an HTTP GET request and returns the response as a JSONObject.
- B 摘要: Loads an OSGi framework factory from a service configuration file.
- 静态失败原因: The static model likely overemphasized the common code structure (BufferedReader loop) and missed the distinct API usage and return types.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would not consider these as clones because they perform entirely different functions (HTTP communication vs service loading) despite sharing trivial I/O boilerplate.
- 共享行为: Both use BufferedReader to read line by line from an input stream；Both contain a while loop that reads until null；Both throw Exception as a checked exception
- 行为差异: A makes a network request (HTTP GET) while B reads a local classpath resource；A returns a JSONObject, B returns a FrameworkFactory；A uses Apache HttpClient, B uses Class.forName and newInstance
- 修正建议: Incorporate dataflow analysis to distinguish API call semantics；Add attention to return types and external utility classes；Use control flow and data dependency graphs to differentiate similar-looking loops

### case_id=4685 FN benchmark_preference_bias

- 方法: `readRemoteFile` vs `readData`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.75`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Reads a remote file line by line and returns the concatenated content as a string, handling I/O errors.
- B 摘要: Reads a local configuration file, parses tokenized lines, and populates multiple sets and maps for Tibetan/Sanskrit glyph data.
- 静态失败原因: The functions are syntactically very different with low token overlap, and B is much longer. Static BERT likely focused on surface tokens and missed the broad functional similarity that BCB considers.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may label as clone because both functions involve reading input data from some source (file/URL) and performing string processing; they share a high-level 'read data' purpose, which BCB often accepts as Type-4 functional similarity.
- 共享行为: Both read from an external source (file/URL) and process text lines.
- 行为差异: A uses URL connection and BufferedReader; B uses file reading via StringTokenizer.；A concatenates lines into one string; B extracts tokens and populates many data structures.；A returns a string; B has void return and updates global variables.；A handles EOFException and IOException locally; B has a single try-catch for IOException at the end.
- 修正建议: Train models on broader functional similarity examples；Incorporate dataflow or program dependence graph features to capture I/O patterns；Use hierarchical representations to handle long functions

### case_id=4686 FP lexical_or_api_overlap

- 方法: `read` vs `getRequestContent`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads all lines from a URL, parses each into CameraLogRecord, collects them, sorts, and logs progress.
- B 摘要: Opens a URL connection, reads the first line, and returns it.
- 静态失败原因: High lexical overlap (URL, openConnection, BufferedReader, readLine) and similar boilerplate structure caused the model to overgeneralize.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB considers them non-clones because they perform fundamentally different tasks: one processes entire file into records, the other only retrieves a single line.
- 共享行为: Both open a URL and read text lines using BufferedReader
- 行为差异: A reads all lines, B reads only first line；A parses lines into objects and sorts, B returns raw string；A uses try-finally to close, B closes directly；A has logging, B does not
- 修正建议: Incorporate method signature and return type information；Use dataflow analysis to detect loop vs single readLine；Add contrastive examples with similar API usage but different semantics

### case_id=4687 FN benchmark_preference_bias

- 方法: `runInternal` vs `File2String`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads and parses OPDS catalog entries from HTTP URLs, iterating over pages and downloading books if not a catalog.
- B 摘要: Reads a file from the local filesystem or classpath resource and returns its content as a string.
- 静态失败原因: Static BERT/GraphCodeBERT correctly identified the lack of semantic and syntactic similarity, predicting non-clone. The BCB label appears to be a misannotation or an overly lenient interpretation.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have considered them clones based on a very broad notion of both being functions that retrieve textual content from a source (HTTP vs file). However, the functionality is too different, and typical BCB annotations for BigCloneBench would not consider such dissimilar functions as clones.
- 共享行为: Both involve reading data from some source (network vs file) and handling I/O exceptions.
- 行为差异: A uses HTTP networking with complex pagination, while B uses simple file I/O.；A invokes callbacks and manages progress, while B just returns a string.；A parses OPDS XML and downloads books, while B is a straightforward file read.；A has a loop for loading multiple parts, whereas B is a single call.
- 修正建议: Review BCB annotation for this pair to ensure consistency with typical Type-3/Type-4 criteria.；No change needed for static detection model; it correctly predicted non-clone.

### case_id=4688 FP lexical_or_api_overlap

- 方法: `readTwitterFead` vs `lookupFutureEvents`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a fixed Twitter timeline JSON from a URL and returns the raw string content.
- B 摘要: Fetches events JSON from Meetup API, parses it into Event objects, and returns a list of events.
- 静态失败原因: Static BERT may have focused on structural overlap (StringBuilder, BufferedReader, while loops) and ignored semantic differences in return type and post-processing.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this non-clone because the functions accomplish different tasks (generic fetch vs. specific API client), and similarities are common I/O boilerplate with low token overlap.
- 共享行为: Both use StringBuilder to accumulate lines from HTTP response；Both read line by line using BufferedReader；Both handle IOException
- 行为差异: A returns raw JSON string without parsing, B parses JSON into domain objects；A uses HttpClient, B uses URL.openStream；A has error logging, B throws custom exception；A has fixed URL, B constructs URL dynamically
- 修正建议: Incorporate data-flow analysis to distinguish raw string accumulation from object creation；Consider return types and type information；Detect presence of JSON parsing and object mapping steps

### case_id=4689 FP boilerplate_overlap

- 方法: `decodeFileToFile` vs `readData`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Decodes a Base64-encoded file and writes the decoded bytes to an output file, returning success status.
- B 摘要: Reads a data file and populates multiple HashSets and maps with tokenized strings for Tibetan transliteration processing.
- 静态失败原因: The model likely focused on superficial structural similarities such as loop constructs (while), try-catch blocks, and file I/O API usage. It may have overlooked the distinct data operations and domain-specific logic, leading to a false positive due to boilerplate overlap.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would label as non-clone because the functions have completely different purposes: one is a file decoding utility, the other is a domain-specific data loader. They lack significant overlap in functionality, and the high-level behavior is unrelated.
- 共享行为: Both methods involve file reading；Both use loops to process data；Both have try-catch-finally or exception handling；Both use buffers or tokenizers to read
- 行为差异: A performs Base64 decoding; B performs string tokenization and set population；A writes to output file; B does not write any file；A has a single output file; B updates multiple internal data structures；A is generic; B is specific to Tibetan Wylie processing
- 修正建议: Augment training data with non-clone pairs that share common boilerplate but have different semantics；Incorporate deeper semantic analysis (e.g., data flow, API call patterns) in the model；Use token-level contrastive learning to distinguish functions with similar control flow but different purposes

### case_id=4690 FN partial_functionality

- 方法: `main` vs `copy`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a URL, unzips it, and extracts each entry to a file.
- B 摘要: Copies the contents of a source file to a destination file.
- 静态失败原因: Low lexical overlap (token Jaccard 0.24) due to different API calls (ZipInputStream vs FileInputStream) and additional logic in A. Static models often miss abstract semantic similarity when specific tokens differ, failing to recognize the shared stream-copy pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as 'copying data from input to output' with similar loop structure (open streams, read-write buffer), thus a Type-3 clone despite different input sources and additional unzipping in A.
- 共享行为: Reads binary data from an input stream；Writes data to a file output stream using a buffered loop
- 行为差异: A handles HTTP and file protocols; B only uses local file；A unzips the input stream; B copies directly without decompression；A extracts multiple entries; B copies a single file
- 修正建议: Incorporate dataflow analysis to detect read-write loops across different stream types；Train on more Type-4 examples where functionality partially overlaps；Use code representation that captures high-level I/O patterns

### case_id=4691 FP lexical_or_api_overlap

- 方法: `import_hints` vs `SRWGuiClient`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Imports puzzle hints from a file or URL and places them on a board.
- B 摘要: Constructs a GUI web browser window that fetches and displays XML/HTML content.
- 静态失败原因: The model was misled by lexical and API overlap (URL, BufferedReader, try-catch) and potentially by similar control flow patterns, ignoring the completely different semantic goals.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled non-clone because the functions have different purposes and very different code structure despite some API overlap.
- 共享行为: Both use URL and BufferedReader to read data from a URL or file.
- 行为差异: A reads specific puzzle hint format and updates game board; B sets up a Swing GUI and displays web content.；A returns boolean; B is a constructor with no return.；A uses StringTokenizer; B uses XSLT transformation and string parsing.
- 修正建议: Incorporate deeper semantic analysis (e.g., AST or data flow) to distinguish different uses of shared APIs.；Train with more diverse non-clone examples that share API calls but differ in functionality.

### case_id=4692 FP boilerplate_overlap

- 方法: `getRequestContent` vs `readVersion`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Opens HTTP connection to given URL, reads first line, and returns it.
- B 摘要: Reads version resource from classpath, parses lines with Version=, Revision=, Date=, and sets corresponding fields.
- 静态失败原因: Static model likely overfitted on lexical overlap (URL, BufferedReader, InputStreamReader, readLine, close) and missed semantic differences in control flow and data usage.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels as non-clone because the functions have different purposes and I/O signatures; they are only superficially similar due to common boilerplate.
- 共享行为: Both use BufferedReader and InputStreamReader to read from a URL source；Both read lines using readLine()；Both close the reader after use
- 行为差异: A takes URL as parameter; B uses hardcoded classpath resource；A returns a String; B returns void and sets fields；A reads only first line; B reads all lines and parses prefixes；A uses HttpURLConnection; B uses URL.openStream()
- 修正建议: Incorporate dataflow/control-flow analysis to distinguish reading modes；Add attention to return types and method signatures；Train on more diverse examples with similar boilerplate but different logic

### case_id=4693 FP lexical_or_api_overlap

- 方法: `getURLContent` vs `downloadFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.85`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads the entire content of a URL and returns it as a string, appending newlines between lines.
- B 摘要: Downloads the content of a URL to a local file with progress reporting and returns a boolean success flag.
- 静态失败原因: The model likely over-relied on overlapping API tokens (URL, openConnection, getInputStream, while-read loop, close) and structural similarities (try-finally, buffered streams) without capturing the distinct output and side-effect semantics, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled 0 (non-clone) because the functions differ in return type, side effects (file writing vs. string creation), and additional operations (progress reporting, file management). The shared URL-reading pattern is generic and insufficient for semantic equivalence under strict BCB guidelines.
- 共享行为: Both open a URL connection and read from its input stream.；Both use a while loop to read data until end of stream.；Both close the streams after reading.
- 行为差异: Function A returns the content as a string; Function B writes to a file and returns a boolean.；Function A uses BufferedReader with a specified encoding; Function B uses BufferedInputStream with a 100-byte buffer.；Function B includes progress reporting via MessageFrame and handles file creation/deletion; Function A does not.；Exception handling differs: A throws IOException, B throws Exception and has no local catch.
- 修正建议: Incorporate dataflow analysis to track return values and side effects (e.g., file writes, UI updates).；Use bytecode or symbolic execution to compare functional behavior beyond token patterns.；Enrich training data with non-clone pairs that share API usage but have different overall purposes.；Apply method-level documentation or name embeddings to capture intent.

### case_id=4694 FP boilerplate_overlap

- 方法: `getUser` vs `doVersionCheck`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Retrieves a user by login name from a database or a config file, parsing colon-separated values.
- B 摘要: Checks for software version updates by reading a version file from a URL and parsing build numbers.
- 静态失败原因: The static model may have been misled by the structural similarity: both functions open a URL, read lines with BufferedReader, and parse tokens. The token overlap is low (0.2179), but the model might rely on control flow patterns like try-catch with URL and BufferedReader. Additionally, the functions are both relatively long and have multiple branching, which can confuse the model into thinking they are similar because of the shared API usage (URL, BufferedReader, InputStreamReader).
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels as non-clone because the overall functionality is completely different: one is user management, the other is version checking, despite some structural overlap in file reading.
- 共享行为: Both open a URL, read lines from a stream, and parse tokens from lines.
- 行为差异: Function A loads a user object and saves it; function B performs version check and calls another method.；Function A handles null user fallback to config file; function B has no such fallback.；Function A uses StringTokenizer with colon delimiter; function B uses line prefix checks.；Function A returns a User object; function B is void and manipulates a View.
- 修正建议: Improve the model's ability to distinguish between similar boilerplate code and actual semantic behavior by incorporating more semantic-aware features or using contrastive learning on function purposes.；Add more training examples where the same boilerplate is used for different tasks to teach the model that structural similarity does not imply functional similarity.

### case_id=4695 FN partial_functionality

- 方法: `getFile` vs `getFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies the SOAP address endpoint, and returns the file path.
- B 摘要: Copies a resource file from the classpath to the user directory if not already present, returns the File object.
- 静态失败原因: Static BERT models rely heavily on lexical and syntactic similarity; low token Jaccard (0.19) and different method signatures, library calls, and control flow led to a non-clone prediction. The model missed the abstract functional similarity in downloading/copying a file.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider these clones as they both implement 'getting a file' via network/copy, which falls under similar functionality (Type-4) despite differences in specifics and implementation details.
- 共享行为: Both check if a local file exists before downloading or copying.；Both open an input stream from a URL/resource and write to a local file.；Both use file I/O with try-catch-finally or explicit close.
- 行为差异: Function a downloads from a remote URL and modifies XML content; function b copies from classpath resource without modification.；Function a returns a file path string; function b returns a File object.；Function a includes complex error handling for multiple exceptions and logging; function b has simpler error handling.；Function a uses NIO channels and has a temporary file renaming step; function b uses buffered streams.
- 修正建议: Enhance model with dataflow analysis to capture core I/O patterns.；Use API-level tokenization to abstract over specific library calls.；Incorporate functional clustering or semantic role labeling for file operations.

### case_id=4696 FN benchmark_preference_bias

- 方法: `writeFileType` vs `readGeoParserResult`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.65`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Reads a list of URIs from a file, fetches each URI, checks its content for RDF/OWL/RDFS namespaces, and writes the classification to an output file.
- B 摘要: Sends a geospatial record content to a remote parser service via XML request, parses the response XML to extract place names and associated gazetteer IDs, returning a collection of tuples.
- 静态失败原因: Static BERT/GraphCodeBERT likely failed to capture the broad functional similarity that BCB considered, focusing instead on token-level and structural differences, leading to a non-clone prediction consistent with strict semantic equivalence but against BCB's broader annotation.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled them as clones due to both involving reading from a network source and writing/extracting structured data, following a similar 'read-parse-extract' pattern, albeit for different domains.
- 共享行为: Both use BufferedReader to read input line by line.；Both handle exceptions with try-catch.；Both perform network I/O via URL connections.
- 行为差异: Function A reads from a file of URIs and processes multiple remote resources; function B processes a single input string against a fixed service.；Function A writes results to an output file; function B returns a collection.；Function A classifies by checking for specific ontology namespaces; function B extracts geographic entities from XML.；Function B includes retry logic and XML parsing; function A does not use XML.
- 修正建议: Incorporate functional abstraction or domain-specific knowledge to recognize high-level patterns like 'fetch and parse'.；Use representation learning that captures intent beyond lexical and syntactic overlap.

### case_id=4697 FP boilerplate_overlap

- 方法: `getSHA256Checksum` vs `perform`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Computes the SHA-256 checksum of a given string.
- B 摘要: Handles a web request for concept classification in a Struts action.
- 静态失败原因: Static BERT/GraphCodeBERT likely relied on structural or lexical similarities such as try-catch blocks, loops, and string building, which are common in many Java functions, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would label these as non-clones because they perform entirely different functionalities despite sharing some boilerplate code patterns.
- 共享行为: Both use loops to process data；Both build strings using StringBuffer；Both catch exceptions
- 行为差异: Function A is a utility for hashing; Function B is a web controller；A uses MessageDigest; B uses HTTP and session objects；A outputs a hex string; B returns an ActionForward and sets session attributes
- 修正建议: Incorporate more semantic-aware representations；Use contrastive learning to distinguish different tasks；Add data-level filtering for common boilerplate patterns

### case_id=4698 FN benchmark_preference_bias

- 方法: `buildSiteForEdit` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Builds a site for editing by processing pages, applying XSLT transformations, and writing output files.
- B 摘要: Copies a file from source to destination using FileChannel.
- 静态失败原因: The model likely correctly identified the large semantic difference and low token overlap, but the BCB label may be a false positive outlier.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled these as clone due to a broad interpretation of similarity involving file I/O, but the overall functionality is too different to be considered a Type-4 clone.
- 共享行为: Both involve file I/O operations (reading and writing files).
- 行为差异: A is a large method with many parameters, loops, error handling, and multiple file operations; B is a small utility.；A processes XML and applies transformations; B just copies bytes.；A writes multiple files; B copies one file.；A involves string replacements and complex logic; B is straightforward.
- 修正建议: Re-evaluate BCB annotation for this pair; likely a false positive.

### case_id=4699 FP boilerplate_overlap

- 方法: `readData` vs `copy`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Reads tokenized strings and populates multiple sets and a hash map for validation, with a secondary file parsing section.
- B 摘要: Recursively copies a file or directory, skipping .svn, and avoiding rewrite if timestamps match.
- 静态失败原因: The static model likely over-generalized based on common programming patterns (nested loops, conditionals, exception handling) and method length, ignoring the distinct API usage and overall goal.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would not classify these as clones because they perform completely different functionalities with no overlap in purpose or output.
- 共享行为: Both involve loops and conditional logic.；Both handle IOException.
- 行为差异: Function A parses string tokens into data structures; Function B copies files/directories.；Function A operates on string and collection objects; Function B operates on files and streams.；Function A includes a large commented-out block; Function B is concise and focused.
- 修正建议: Incorporate API usage vectors into embeddings.；Use control flow analysis to differentiate data processing from file I/O.；Train with more diverse non-clone pairs that share structure but differ semantically.

### case_id=4700 FN partial_functionality

- 方法: `doVersionCheck` vs `httpRequestByPOST`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Retrieves version information from a URL by reading and parsing text lines, showing wait cursor, and handling errors with dialog.
- B 摘要: Sends an HTTP POST request with parameters, reads the response line by line, returns the response string or sets error fields.
- 静态失败原因: Static BERT/GraphCodeBERT models rely heavily on token similarity and structural overlap. The low token Jaccard (0.2247) and different APIs (URL vs HttpClient) likely caused the model to overlook the shared I/O pattern. The model also may have been distracted by unique tokens like 'jEdit', 'version-check.url', and specific parsing logic.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this as a clone because both methods perform an HTTP request and read the response line by line, which is a common functional pattern. The broad Type-3/Type-4 criteria in BCB often accept such partial functionality similarity despite differences in HTTP method, parsing, and error handling.
- 共享行为: Both open a network connection and read text lines from an input stream using BufferedReader.
- 行为差异: A uses HTTP GET, B uses HTTP POST.；A parses specific tags (e.g., .build), B returns the entire response.；A shows/hides wait cursor, B does not.；A returns void, B returns a String.
- 修正建议: Use dataflow-aware models that capture the sequence of operations (open connection, read lines, close).；Train on more cross-project clones with different HTTP libraries.；Incorporate semantic features like 'HTTP request' and 'line-by-line reading'.

### case_id=4701 FN benchmark_preference_bias

- 方法: `doTransfer` vs `createDialogArea`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Transfers an HTTP request to another URL by forwarding headers and body, returning the response.
- B 摘要: Creates a SWT dialog area displaying a license file read from a bundle resource.
- 静态失败原因: Static model likely relied on low token overlap (15.5%) and structural differences, correctly predicting non-clone despite BCB's broad label.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled as clone due to both involving I/O operations (stream reading/writing) and exception handling, despite different contexts.
- 共享行为: Both open input streams to read data；Both handle IOException with printStackTrace；Both close streams in finally blocks
- 行为差异: Domain: servlet forwarding vs SWT UI creation；Data source: incoming HTTP request vs bundle resource file；Output: HTTP response vs SWT Browser or Text widget；Purpose: HTTP proxy-like relay vs license display
- 修正建议: Verify BCB annotation consistency；Use domain-aware token embeddings；Incorporate code structure and purpose filtering

### case_id=4702 FN lexical_or_api_overlap

- 方法: `copy` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.4`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Recursively copies a file or directory from source to destination using FileChannel.
- B 摘要: Retrieves a resource as an InputStream, caching it locally via HTTP if needed.
- 静态失败原因: Low token overlap and different method names indicate distinct lexical content; static models may miss the broad I/O theme due to focus on local patterns.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may have labeled as clone due to both functions involving file I/O, resource management, and similar exception handling patterns, despite different high-level purposes.
- 共享行为: Both perform file I/O operations with streams and channels；Both handle file existence checks；Both close resources in finally blocks
- 行为差异: A copies files locally; B downloads from network with caching；A handles directories recursively; B handles single resources；A uses MappedByteBuffer for efficient copy; B uses BufferedStreams for byte-by-byte copy；B has HTTP connection handling and cache management; A does not
- 修正建议: Improve training to recognize abstract I/O operations；Incorporate structural similarity of resource handling blocks；Use data flow analysis to capture shared use of FileInputStream, FileOutputStream, etc.

### case_id=4703 FP lexical_or_api_overlap

- 方法: `getJSONData` vs `importSequences`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches JSON data from a URL via HTTP GET and parses it into a JSONObject.
- B 摘要: Imports biological sequences from a URL by parsing a FASTA-like format and populating lists.
- 静态失败原因: Static models like BERT overemphasized lexical/API overlaps (URL, InputStream, try-catch) and missed the distinct parsing semantics and control flow.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would label this as non-clone because the functions have fundamentally different purposes and logic, despite sharing boilerplate stream reading and exception handling.
- 共享行为: Both open a URL and read from an InputStream；Both handle exceptions with try-catch
- 行为差异: Different data formats (JSON vs. FASTA-like sequences)；Different parsing logic (JSONTokener vs ImportHelper)；Different return types (JSONObject vs void with side effects on class fields)；Different error handling (generic vs specific exceptions)
- 修正建议: Incorporate dataflow analysis to distinguish different parsing patterns；Use type-aware embeddings to differentiate object types；Augment training with contrastive examples that penalize boilerplate overlap

### case_id=4704 FP lexical_or_api_overlap

- 方法: `actionPerformed` vs `convert`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Handles UI action events (GRAPHVIZ, IMAGEMAGICK, etc.) to set file paths and update preferences.
- B 摘要: Converts an ACRNEMA file to DICOM format, handling pixel data and UID generation.
- 静态失败原因: Static model may have over-generalized common Java constructs (e.g., try-finally, loops, conditionals) or mistakenly considered both as file processing tasks.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clone because functions have entirely different purposes and domain-specific logic.
- 共享行为: Both perform conditional checks and file I/O operations
- 行为差异: Function A updates UI and preferences based on user actions；Function B converts medical image file formats with pixel data manipulation
- 修正建议: Enhance training with more diverse non-clone pairs；Incorporate dataflow or structural analysis to differentiate unrelated functionality

### case_id=4705 FP boilerplate_overlap

- 方法: `getLinksFromURLFast` vs `run`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.85`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Extracts hyperlinks and anchor texts from a URL's HTML content using regex and returns them as two vectors.
- B 摘要: Fetches a URL with HTTP basic authentication, reads the entire response into a string, and sets a finish flag.
- 静态失败原因: The static BERT model likely focused on the similar structural patterns (URLConnection, BufferedReader, StringBuffer) and ignored the functional differences in regex extraction and return types, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely considered these non-clones because the functions have distinct high-level purposes (link extraction vs. authenticated data download), despite sharing common HTTP-reading boilerplate.
- 共享行为: Open an HTTP URL connection；Read lines from the response using BufferedReader；Use StringBuffer to accumulate the content
- 行为差异: A uses regex to extract specific link and text patterns, while B stores the entire response string；A does not include authentication, B uses Basic Auth with credentials；A returns two vectors of links and texts; B sets a result string and finish flag；A throws Exception generically, B catches Throwable
- 修正建议: Incorporate data-flow analysis to track how the read content is processed (e.g., regex extraction vs. full storage).；Use functional summarization to capture the core purpose (e.g., link extraction vs. downloading).；Reduce weight on common boilerplate I/O patterns.

### case_id=4706 FP partial_functionality

- 方法: `readData` vs `save`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Reads tokenized strings from class fields and file data to populate sets and maps for parsing Tibetan and Sanskrit characters.
- B 摘要: Copies a byte array to a file, creating parent directories and closing streams safely.
- 静态失败原因: The static BERT model likely overemphasized the presence of common API calls like 'new StringTokenizer', 'new HashSet', and file I/O patterns, mistaking broad structural similarities for functional equivalence despite low token overlap.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB would not label this as a clone because the functionalities are completely different: one is a complex parsing and data loading routine, the other is a simple file copy utility. Even Type-4 requires similar input/output behavior, which is absent here.
- 共享行为: Both involve file I/O operations (A reads from a file, B writes to a file).
- 行为差异: A parses complex tokenized data into multiple sets and a hash map; B simply copies bytes.；A has extensive stateful side effects on many class fields; B is stateless and returns an integer.；A is long and complex with nested loops and conditionals; B is short and straightforward.
- 修正建议: Train with more negative examples of I/O functions having different purposes.；Incorporate dataflow analysis to distinguish read vs write operations.；Focus on semantic similarity beyond lexical tokens.

### case_id=4707 FN partial_functionality

- 方法: `getFile` vs `createNew`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies the endpoint in the XML, and returns the local file path.
- B 摘要: Creates a new resource by writing an InputStream to a file in a directory, subject to ownership verification.
- 静态失败原因: The static model likely focused on the low token Jaccard (0.138) and different method names/structures, but BCB's broad annotation preference for partial file-writing functionality caused the label mismatch.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider them clones because both perform file creation and use FileOutputStream, possibly overlooking the distinct high-level purposes and domain-specific logic.
- 共享行为: Both write data to files using FileOutputStream.；Both handle IOException.
- 行为差异: Function A downloads from a URL and modifies XML; B copies an input stream directly.；Function A involves complex error handling for multiple exception types; B has an ownership check.；Function A uses NIO channels for transfer; B uses IOUtils.copy.；Function A returns a String; B returns a Resource object.
- 修正建议: Use a model that captures high-level intent and domain-specific operations, not just lexical overlap.；Incorporate data flow and context beyond basic IO operations.；Consider binary-level features like file operations vs. network operations.

### case_id=4708 FP boilerplate_overlap

- 方法: `get` vs `doVersionCheck`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Retrieves game records via HTTP GET with custom headers, parses lines not starting with '#', returns array or null on failure.
- B 摘要: Performs version check by reading a URL, parsing lines for build versions, and invoking another method; shows/hides wait cursor and handles errors with dialog.
- 静态失败原因: Static BERT may have been misled by overlapping boilerplate (try-catch, BufferedReader, readLine loop) and similar structural patterns, ignoring the distinct semantic goals and output differences.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely considers these non-clones because the functions serve entirely different purposes (fetching game records vs. version checking) despite sharing a common boilerplate pattern of reading from a URL.
- 共享行为: Open a URL and read lines from input stream；Use BufferedReader and InputStreamReader；Filter lines based on prefix (startsWith) ；Handle IOException with catch block
- 行为差异: Function A returns GameRecord array; function B returns void and calls another function；A uses HttpURLConnection with GET method and custom headers; B uses URL.openStream()；A filters lines starting with '#'; B filters lines starting with '.build' or '.stablebuild'；A prints error message to console; B shows error dialog and updates cursor
- 修正建议: Incorporate data-flow analysis to track output types and return values；Use models that capture functional purpose, not just token sequences；Add attention to method signatures and variable usage patterns

### case_id=4709 FP lexical_or_api_overlap

- 方法: `doVersionCheck` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a version-check URL, parses version and build numbers, and notifies user if a newer version exists.
- B 摘要: Searches Google Images for a given query, parses image URLs, displays the first image on a UI label.
- 静态失败原因: The model likely over-generalized from common API sequence (URL, BufferedReader, parse, catch) and structural similarity, ignoring semantic differences in data handling and purpose.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically annotates as non-clone when functions perform distinct high-level tasks, despite low-level IO similarities.
- 共享行为: Open a URL connection and read input stream；Use BufferedReader and InputStreamReader；Parse string data line by line；Handle exceptions with error dialogs
- 行为差异: Different URLs and data parsing logic (version info vs image URLs)；Different output: user notification vs image display；Different parameters and UI interactions；One uses URL.openStream(); the other uses HttpURLConnection with User-Agent
- 修正建议: Incorporate type and method call context to distinguish tasks；Use dataflow analysis to capture actual data transformations；Train with contrastive examples that share API but differ in intent

### case_id=4710 FN benchmark_preference_bias

- 方法: `getWebPage` vs `readData`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Reads the content of a URL and returns it as a string.
- B 摘要: Parses multiple comma-separated string fields to populate sets and lookup tables.
- 静态失败原因: Static BERT correctly identified they are not clones; it did not fail; the BCB label appears incorrect.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have considered both as 'reading data' functions, but the functionality is entirely different; likely a labeling error.
- 共享行为: No shared behavior
- 行为差异: One performs I/O to fetch web page, the other parses static string data.；One returns a string, the other is void and populates data structures.；Error handling differs significantly.
- 修正建议: Re-evaluate BCB label for this pair; likely should be non-clone.

### case_id=4711 FP lexical_or_api_overlap

- 方法: `downloadURLtoString` vs `downloadModel`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads lines from a URL and concatenates them into a single string.
- B 摘要: Downloads an RDF model from a URL with HTTP headers and returns a Model object.
- 静态失败原因: Static BERT models may over-rely on lexical overlap (e.g., 'URL', 'openStream', 'InputStream') and miss the semantic divergence in return type and data processing, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels non-clones when functions have different output types and distinct processing steps beyond the initial data retrieval, which is insufficient for functional equivalence.
- 共享行为: Both perform HTTP requests to download data from a URL.；Both open an InputStream from the URL connection.
- 行为差异: Function A returns a plain String; function B returns a parsed RDF Model.；Function A throws IOException; function B catches exceptions and wraps them in RuntimeException.；Function A reads lines manually; function B uses model.read() to parse RDF.；Function B sets HTTP headers (Accept, Accept-Language); function A does not.
- 修正建议: Include data flow information to distinguish different output transformations.；Add training examples with similar download patterns but distinct final purposes.；Use type-aware embeddings to capture return type differences.

### case_id=4712 FP partial_functionality

- 方法: `getPagina` vs `SRWGuiClient`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches and returns the entire content of a URL as a string, returning error messages on failure.
- B 摘要: Constructs a Swing browser window that fetches and displays XML-transformed HTML content from a URL.
- 静态失败原因: The static model likely overemphasized the lexical similarity of the common URL-reading code block (opening URL, reading lines) and ignored the extensive surrounding code that defines the different behaviors.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely labeled non-clone because the functions have distinct overall purposes despite a common sub-step; the overall functionality (get a page vs build a browser) is considered different.
- 共享行为: Both open a URL and read its content line by line using BufferedReader.
- 行为差异: A returns the raw page content as a string; B processes XML, applies XSLT transformations, and displays the result in a GUI.；A is a simple utility; B is a complex GUI constructor with multiple UI components and event handling.
- 修正建议: Include more global context to capture the overall method purpose.；Use graph-based representations that model control/data flow to differentiate start-to-end behaviors.；Add training examples that penalize over-reliance on common sub-sequences.

### case_id=4713 FP lexical_or_api_overlap

- 方法: `readData` vs `copyFromFileToFileUsingNIO`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Parses token sets from string fields and a file, populating multiple sets and maps for a Tibetan transliteration system.
- B 摘要: Copies a file's content to another file using NIO channels.
- 静态失败原因: The static model may have been misled by overlapping Java keywords (static, void, IOException) and the presence of exception handling, despite low token similarity.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clone because these functions share no functional similarity; one is a parser/initializer, the other a file copier.
- 共享行为: Both are static methods.；Both can throw IOException (though A catches it locally).
- 行为差异: A performs complex parsing and state initialization; B performs file I/O copy.；A manipulates multiple data structures; B transfers bytes between channels.；A reads from static strings and a file; B reads and writes files via channels.；A has extensive conditional logic and error handling; B has simple try-finally.
- 修正建议: Incorporate AST-based structural comparison.；Use data flow analysis to detect different operations.；Train on more diverse non-clone pairs with low lexical overlap.

### case_id=4714 FP lexical_or_api_overlap

- 方法: `getUser` vs `importRoles`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Gets a User by login, loading from database or parsing a config file from URL and saving to database.
- B 摘要: Imports a list of RoleName objects from an XML file at a given URL by reading and parsing lines.
- 静态失败原因: Static BERT models relied heavily on token-level overlap and common API calls (URL, BufferedReader, InputStreamReader, readLine), which led to a false positive. The lexical similarity is about 29% but the API usage pattern is similar enough to mislead surface-level matching.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clone because the functions have different return types, different data processing logic (one handles user credentials with tokenization, the other parses XML roles), and different purposes (user retrieval vs role import). Even BCB's broad Type-3/4 would require more functional similarity.
- 共享行为: Both read content from a URL using BufferedReader；Both process input line by line；Both handle IOException with try-catch
- 行为差异: A writes to database (userDAO.save); B only collects results in list；A returns a single User or null; B returns ArrayList<RoleName>；A compares tokens with StringTokenizer; B parses XML tags；A has fallback to config file when DB fails; B always reads from URL
- 修正建议: Incorporate data-flow analysis to distinguish different output types and operations；Use abstract syntax tree (AST) or control flow graph (CFG) to capture structural differences；Add semantic role labeling to identify function purpose (e.g., fetching vs parsing vs transforming)

### case_id=4715 FN partial_functionality

- 方法: `main` vs `doPost`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a URL, extracts its ZIP entries, and saves them to disk.
- B 摘要: Handles a multipart HTTP POST request, parses uploaded file or URL, and writes processed content to response.
- 静态失败原因: Low token overlap (Jaccard=0.136) and different API usage patterns led the static model to predict non-clone, despite some shared I/O patterns.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB might consider both as reading from a URL and writing to an output stream, but the specific functionalities (ZIP extraction vs multipart upload handling) are too different to qualify as a clone even under broad Type-3/Type-4 definitions.
- 共享行为: Read from an input stream and write to an output stream
- 行为差异: A extracts ZIP entries; B handles multipart form data；A uses ZipInputStream; B uses ServletFileUpload；A has no error handling; B has try-catch-finally；A writes to files; B writes to HTTP response
- 修正建议: Incorporate data flow and control flow analysis to capture high-level I/O patterns；Use graph-based representations to model stream operations

### case_id=4716 FN boilerplate_overlap

- 方法: `sendExceptionToServer` vs `retrieveQ`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends an exception report to a server by building a POST request with URL-encoded parameters and reading the response.
- B 摘要: Retrieves the content of a given URL by reading it line by line and returning the concatenated string.
- 静态失败原因: Static BERT/GraphCodeBERT likely focused on token-level patterns and detected the large structural difference (POST vs GET, different parameters and return types) and low token Jaccard (0.23), missing the underlying shared boilerplate.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB often marks as clone when there is high structural similarity in boilerplate code, such as the URL connection and reading pattern, tolerating differences in additional functionality like sending data.
- 共享行为: Both open a URL connection and read input via BufferedReader；Both use similar boilerplate for reading lines from an InputStream
- 行为差异: Function A sends data via POST (writes to output stream), while B only reads；Function A ignores the 'server' parameter, B uses the URL argument；Function A returns void and prints responses, B returns the string；Function A catches IOException, B throws it
- 修正建议: Use structural analysis that captures common patterns like URL reading boilerplate；Incorporate data flow to distinguish core reading loop from ancillary code；Adjust similarity threshold to allow for partial functionality overlap

### case_id=4717 FN benchmark_preference_bias

- 方法: `getFile` vs `bootKernel`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.3`
- 推荐路线: `preference_memory_with_manual_audit`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file, modifies its SOAP address location, and saves it locally.
- B 摘要: Loads a configuration from an Android asset, copies embedded files to SD card, and boots a kernel via reflection.
- 静态失败原因: The low token Jaccard (0.083) and different method names misled the model. The shared NIO channel usage is a low-level detail that static BERT might not capture as a strong semantic signal.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BigCloneBench may consider these as Type-4 clones because both involve file copying and manipulation using similar NIO APIs, and both have a setup-and-process structure, despite different domain goals.
- 共享行为: Both perform file I/O operations；Both use NIO channels for file transfer (transferFrom / transferTo)；Both handle exceptions with catch blocks
- 行为差异: Function A downloads a file from a URL and modifies XML; Function B reads assets and copies them to external storage.；Function A processes WSDL files; Function B loads a kernel class and boots it.；Different target platforms: Function A is generic Java; Function B is Android-specific.；Function A returns a file path; Function B performs a boot process and finishes on error.
- 修正建议: Incorporate structure-aware features like control flow graphs or data flow to detect common I/O patterns.；Use fine-tuning on more diverse clone types including cross-domain file I/O tasks.；Increase weight of API usage sequences (e.g., transferFrom/transferTo) in similarity computation.

### case_id=4718 FN partial_functionality

- 方法: `copy` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Recursively copies a file or directory using NIO FileChannel.
- B 摘要: Launches an Eclipse launch configuration for a NexOpen project, which includes copying a reverse engineering file as a sub-step.
- 静态失败原因: Static BERT models rely on token-level similarity and whole-function structure. The low token Jaccard (0.064) and different API vocabularies (Eclipse vs NIO) prevent it from recognizing the embedded file copying commonality. The model cannot decompose function B to detect the partial overlap.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB's broad clone annotation often accepts Type-3/4 partial functionality clones. Here, function B contains a file copy sub-task that matches the entire functionality of function A, so under BCB's lenient criteria, this qualifies as a clone.
- 共享行为: Both perform file copying operations (A wholly, B as part of its workflow).
- 行为差异: A is a general-purpose file copy utility; B is a complex Eclipse launch method with many Eclipse-specific API calls.；A uses NIO FileChannel; B uses IOUtils.copy and FileLocator within an Eclipse context.；B includes validation, XML processing, property setting, and project installation not present in A.
- 修正建议: Use program slicing to isolate sub-behaviors within functions.；Train on more partial clone examples or incorporate call-graph alignment.；Employ hierarchical matching that identifies structural similarity in sub-tasks.

### case_id=4719 FN lexical_or_api_overlap

- 方法: `internalCopy` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Copies a file from source to destination, skipping a file named Thums.db.
- B 摘要: Launches a complex Eclipse project configuration, involving Maven pom files, Hibernate properties, and reverse engineering file handling.
- 静态失败原因: Static BERT/GraphCodeBERT models rely heavily on token overlap and structural similarity. The extremely low Jaccard similarity (0.044) and different API usage prevent the model from recognizing any functional similarity, leading to a false negative.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: Despite low lexical overlap, BCB may consider both as methods performing file I/O using streams, thus sharing core functionality. However, the overall task and complexity are vastly different, making this a borderline or erroneous annotation.
- 共享行为: Both perform file input/output using streams and buffers.；Both handle IO-related exceptions.
- 行为差异: Function A is a simple file copy with only one skip condition.；Function B is a complex multi-step launch procedure with many conditional operations.；Function B interacts with Eclipse workspace, projects, and Hibernate, while A does not.；Function B uses framework-specific classes (e.g., ILaunchConfiguration, ContentHandlerTemplate).
- 修正建议: Incorporate dataflow analysis to capture shared I/O patterns.；Use abstract syntax tree (AST) based features to compare control flow structure.；Train on broader Type-4/functional clone examples that focus on semantic equivalence despite low lexical overlap.

### case_id=4720 FP lexical_or_api_overlap

- 方法: `getUser` vs `loadMFileViaWeb`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Load a user by login from a database or a config file by reading and parsing colon-separated fields.
- B 摘要: Load a Matlab (.m) file from a web URL by reading lines and parsing into a UserFunction object.
- 静态失败原因: Static BERT likely focused on the lexical overlap of common API calls (URL, openStream, readLine) and missed the semantic gap because it did not capture the overall intent or long-range dependencies of the code.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB considers them non-clones because the functions are semantically unrelated despite sharing a common I/O pattern; the overall functionality and domain are completely different.
- 共享行为: Both open a URL and read lines sequentially using similar Java I/O patterns (URL, openStream, BufferedReader, readLine).
- 行为差异: Purpose: authentication/user loading vs. remote file loading for parsing Matlab code.；Parsing logic: colon-delimited tokenization vs. entire code concatenation and function parsing.；Return type: User object vs. UserFunction object.；Error handling: print stack trace vs. throw custom exception.
- 修正建议: Incorporate data flow and control flow graphs.；Use method names as additional context.；Train with more diverse negative examples that share API patterns but differ in semantics.

### case_id=4721 FN partial_functionality

- 方法: `copyResource` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.95`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource (from URL or local file) to a destination file, throwing exception if not found.
- B 摘要: Returns an InputStream for a resource, with caching and HTTP handling; returns null on failure.
- 静态失败原因: Low token overlap (0.18) and stark syntactic differences (length, control structures, API usage) caused the model to misclassify as non-clone, failing to capture the shared IO behavior.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considers both as 'resource copying/reading' functions that read from a source and produce output, even though the output is different (file vs. stream) and B adds caching. The core IO pattern qualifies as Type-3/Type-4 partial functionality.
- 共享行为: Get a resource via URL or local file；Open an input stream from the resource；Read data from the input stream；Write/forward the data to a destination (file or cached file)
- 行为差异: A writes to a file; B returns an InputStream；B includes caching logic and HTTP support; A does not；A throws exception on missing resource; B returns null；B is synchronized and uses Buffered streams; A does not
- 修正建议: Incorporate data-flow or control-flow graphs to capture shared IO subgraphs；Use code summarization or functional embedding to detect high-level similarity；Train on more varied clone types with less lexical overlap

### case_id=4722 FN partial_functionality

- 方法: `getFile` vs `cpFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies an XML attribute, and saves it to a temporary directory.
- B 摘要: Copies a source file to a target file, with options to replace or avoid overwriting by renaming.
- 静态失败原因: Static BERT models rely heavily on token and API surface similarity; the low Jaccard (0.157) and different API calls (URLConnection vs FileInputStream) led the model to miss the underlying shared data-copying behavior.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both functions as implementing a file transfer operation (from source to destination), and the additional XML processing in A is viewed as an extension rather than a core difference. The presence of file existence checks and stream-based I/O aligns with typical Type-4 clone criteria in BigCloneBench.
- 共享行为: Both check existence of a source before proceeding.；Both perform file I/O operations involving reading from an input stream and writing to an output stream.；Both handle IOException.
- 行为差异: Function A downloads from a network URL, while Function B copies from a local file.；Function A parses and modifies XML content, which Function B does not.；Function A has multiple error handlers (AxisFault), while Function B only throws IOException.；Function B implements a complex naming scheme to avoid overwriting, absent in Function A.
- 修正建议: Incorporate structural AST features that capture data-flow patterns like stream copying.；Use contrastive learning to focus on high-level functional equivalence rather than exact token matching.；Add domain-specific knowledge of common I/O idioms to the model.

### case_id=4723 FN partial_functionality

- 方法: `File2String` vs `postRequest`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a file from filesystem or classpath resource and returns its content as a string, with error handling that exits the program.
- B 摘要: Sends an HTTP POST request with parameters and returns the response body as a string, returning null on exception.
- 静态失败原因: Static BERT/GraphCodeBERT models rely on lexical and structural features; the low token Jaccard (0.21) and differing API calls (File vs URL, PrintWriter vs FileInputStream) caused it to miss the shared reading-loop pattern. The model may not capture abstract semantic similarity across different I/O contexts.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considers them Type-4 clones because both implement the pattern 'read all lines from an input stream into a string'—a common data retrieval idiom—despite different I/O sources and error handling. The core while-loop logic is structurally identical.
- 共享行为: Both open an input stream, read lines in a while loop, append to a string buffer, close resources, and return the accumulated string.
- 行为差异: A reads from local file or classpath resource; B sends HTTP POST to remote server.；A prints messages and calls System.exit on failure; B prints stack trace and returns null.；A has a fallback mechanism to load from classpath; B does not.
- 修正建议: Train with more diverse examples of the 'read all lines' pattern across different I/O sources.；Use data-flow analysis to abstract the core while-loop structure.；Incorporate function-level semantic embeddings that focus on control flow and data transformation rather than exact API names.

### case_id=4724 FN benchmark_preference_bias

- 方法: `testLoadSource` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Tests loading an arXiv article source stream and checks that the content contains a specific string.
- B 摘要: Launches a NexOpen Eclipse plugin project by configuring Maven POM files and Hibernate dialect properties.
- 静态失败原因: Static BERT did not fail; it correctly predicted non-clone, but the BCB label is 1 (clone). The model recognized the large semantic gap, so its prediction disagrees with the benchmark.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as a clone due to both functions involving stream I/O, exception handling, and resource loading, but the functional contexts are entirely different; this is likely an annotation error or an overly broad interpretation of Type-3/Type-4 similarity.
- 共享行为: Both use IOUtils.copy for stream copying；Both handle IOException (though in different ways)
- 行为差异: A is a unit test retrieving an arXiv source via a DAO facade; B is a complex launch configuration handler for an Eclipse plugin；A uses StringWriter; B uses ByteArrayOutputStream；A checks content for a specific substring; B sets persistent properties and schedules a job；B involves file existence checks, document handling, and Hibernate dialect configuration; A does not
- 修正建议: Re-evaluate BCB annotation for this pair to correct the false positive；Use functional classification to avoid grouping disparate tasks；Consider adding domain-specific filtering in clone detection

### case_id=4725 FN partial_functionality

- 方法: `main` vs `runScript`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Builds a POST request with predefined parameters to a social media API and prints the response.
- B 摘要: Downloads a script file from a URL by opening a stream and returns its content as a string.
- 静态失败原因: Static BERT-based models rely on token overlap and structural similarity, which are minimal here (Jaccard=0.069). They cannot capture the high-level functional similarity of 'reading from a URL' that BCB might have considered.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider these clones under a loose Type-4 interpretation because both involve network I/O to fetch data from a URL, even though the detailed implementations and protocols differ significantly.
- 共享行为: Both create a URL object and open a connection to read data from a network resource.
- 行为差异: Function A sends a POST request with multiple parameters; function B performs a simple GET (via openStream) with no parameters.；Function A prints the response line by line; function B concatenates bytes into a string and returns it.；Function A explicitly sets request method and handles HTTP response codes; function B does not.；Function A uses HttpURLConnection; function B uses URL.openStream().
- 修正建议: Incorporate data flow and API call sequence features.；Use contrastive learning with positive pairs sampled at behavior level.；Enrich training with function purpose labels or comments.

### case_id=4726 FN library_context_missing

- 方法: `readRemoteFile` vs `File2String`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `context_recovery_then_expert`；动态可解性: `low`；执行优先级: `medium`
- A 摘要: Reads a remote file from a URL and returns its contents as a concatenated string, with error handling that prints messages but continues.
- B 摘要: Reads a file from local filesystem or classpath (fallback) and returns its contents as a concatenated string, exiting on errors.
- 静态失败原因: Low lexical overlap (token Jaccard 0.27) and different control structures and APIs (URL vs File/ClassLoader) mask the semantic similarity.
- 静态 case study: 该类错误缺少关键上下文或需要深层语义，纯静态方法不可靠。
- 动态 case study: 动态执行价值较低：样本可能依赖库、框架、网络、GUI、数据库或项目上下文，需要先恢复环境或 mock 依赖。
- BCB 偏好解释: BCB often labels Type-4 clones where core functionality (reading a textual resource into a string) is the same despite different APIs and error handling.
- 共享行为: Read text from an input source and concatenate all lines into a single string without line separators.
- 行为差异: Input source: A uses URL, B uses local file or classpath.；Error handling: A prints and continues, B prints and exits.；Control flow: A uses eof flag, B uses null check.；B has debug print and fallback logic, A does not.
- 修正建议: Abstract different I/O APIs to a common 'read stream' representation.；Use graph-based models that capture data flow and control flow similarities.；Augment training data with functionally similar code using different libraries.

### case_id=4727 FP lexical_or_api_overlap

- 方法: `createDialogArea` vs `downloadFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Creates a dialog area displaying license text from a local resource, using either a browser or text widget.
- B 摘要: Downloads a file from a remote URL to a local destination with progress reporting.
- 静态失败原因: The model likely over-relied on lexical and API overlap (e.g., InputStream, URL, try-catch-finally, reading loops) and ignored the different functional contexts (UI vs. networking).
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the functions have entirely different purposes (UI display vs. file download) and implementations, despite superficial API overlap.
- 共享行为: Both use I/O streams to read data (InputStream, BufferedInputStream) and handle exceptions.
- 行为差异: A reads from a local resource, B from a remote URL.；A displays text in a UI, B writes to a file.；A involves UI creation, B involves progress tracking.；A returns a Control, B returns a boolean.
- 修正建议: Incorporate type and method call context to distinguish UI vs. networking operations.；Use graph-based representations capturing data flow and control flow more accurately.；Train on task-specific objectives that penalize superficial API matches when semantics differ.

### case_id=4728 FN partial_functionality

- 方法: `readRemoteFile` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a remote file line by line and concatenates content into a single string with error handling.
- B 摘要: Constructs a URL with POST parameters, sends an HTTP POST request, and prints each line of the response.
- 静态失败原因: Static BERT models rely on token surface overlap and may miss abstract functional similarity like 'read from URL line by line' due to low token Jaccard and different API usage.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as 'reading from remote resource' under Type-4 semantic similarity, ignoring the differences in I/O method and HTTP verb.
- 共享行为: Both open a URL connection to a remote resource；Both read input line by line using BufferedReader；Both handle IO exceptions (though in different ways)
- 行为差异: A returns concatenated string; B prints lines to stdout；A uses InputStream from URL.openStream; B uses HttpURLConnection with POST method；A includes explicit EOF handling and EOFException catch; B throws IOException；B constructs complex URL with many parameters; A uses a single static URL
- 修正建议: Enhance training data with more diverse URL reading examples；Use graph-based code representations (e.g., GraphCodeBERT) that capture data flow and structural patterns；Incorporate pre-training on remote I/O operations

### case_id=4729 FN partial_functionality

- 方法: `copyFile` vs `getFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a file from source to destination using a byte buffer and streams.
- B 摘要: Downloads a WSDL file from a URL, optionally modifies its endpoint XML, and saves it locally, with extensive error handling.
- 静态失败原因: Low token overlap (Jaccard 0.11) and different structures mask the shared copy subtask; static models lack deep semantic understanding of partial functionality.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have considered the core file-copying operation in B as semantically equivalent to A, accepting broad Type-4 similarity despite syntactic differences.
- 共享行为: Both perform a copy operation from an input stream to an output stream.
- 行为差异: A is a simple file-to-file copy; B downloads from network, checks file existence, and manipulates XML.；A uses a byte buffer; B uses NIO channels for transfer.；A has no error handling; B catches multiple exceptions and logs extensively.；A returns void; B returns the file path string.
- 修正建议: Use graph-based or AST-based methods to detect common subpatterns.；Train on contrastive learning objectives focusing on partial functionality clones.；Incorporate data flow analysis to identify I/O operations.

### case_id=4730 FN benchmark_preference_bias

- 方法: `doGet` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Handles HTTP GET request: retrieves a page, logs requests, and caches the rendered page to a temporary file.
- B 摘要: Copies a file from source to destination using NIO channels.
- 静态失败原因: It didn't fail; it correctly predicted non-clone due to low token overlap and different functionality. The BCB label is likely a false positive.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might have considered the file I/O portion in A (caching to disk) as similar to B's file copy, but this ignores the main functionality of A.
- 共享行为: Both functions perform file I/O operations (reading/writing files).
- 行为差异: Function A is a complex HTTP servlet handler with user authentication, page retrieval, and caching logic.；Function B is a simple utility method for file copying with no HTTP or user interaction.；Different input parameters (HttpServletRequest vs File).；Different output (HTTP response vs file copy).
- 修正建议: Re-evaluate BCB annotations for this pair.；Consider domain-specific context to avoid over-generalizing partial functionality.

### case_id=4731 FP boilerplate_overlap

- 方法: `main` vs `convert`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Parses Prolog file and generates adapter classes packaged into a JAR.
- B 摘要: Converts an ACRNEMA stream file to DICOM format with pixel data handling.
- 静态失败原因: Static models may have focused on structural similarities (e.g., both have loops, conditionals, file I/O) and ignored the lack of semantic overlap, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely considers them non-clones as they perform entirely different tasks with no functional similarity.
- 共享行为: Both use file I/O；Both print messages to console；Both have try-catch-finally blocks；Both contain loops
- 行为差异: Completely different domains (Prolog vs DICOM)；Different input/output formats；Different libraries and classes used；Different error handling specifics
- 修正建议: Improve model sensitivity to domain-specific code；Use richer representation of program semantics；Incorporate type and library usage patterns

### case_id=4732 FN partial_functionality

- 方法: `copyResource` vs `createTempFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.95`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource from a URL or local file to a specified destination file using byte-by-byte stream copy.
- B 摘要: Copies a resource from the classpath to a temporary file using IOUtils.copyLarge.
- 静态失败原因: Static BERT/GraphCodeBERT models rely on token and structural similarity. The low token Jaccard (0.19) and different API calls (openStream vs getResourceAsStream, FileOutputStream vs createTempFile) push the embedding apart, missing the high-level semantic equivalence of resource copying.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels Type-3/Type-4 clones where high-level functionality (copying a resource to a file) is similar despite differences in source type, destination, and error handling. The core I/O operation is the same.
- 共享行为: Both copy a resource (file or classpath resource) to a file output.；Both handle input/output streams.；Both ultimately produce a file containing the resource content.
- 行为差异: Source retrieval: A uses URL or local file; B uses classpath resource.；Output destination: A uses a specific destination file; B creates a temporary file.；Error handling: A throws Exception after trying both sources; B calls fail() on missing resource.；Copy implementation: A uses a manual while loop; B uses IOUtils.copyLarge.
- 修正建议: Incorporate dataflow analysis to capture I/O behavior like stream creation and copying.；Use type-3 clone detection with AST-based differencing and semantic relaxation.；Augment training with examples of same high-level operation implemented with different APIs.

### case_id=4733 FP lexical_or_api_overlap

- 方法: `getRequestContent` vs `startScript`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Opens a URL connection, reads the first line from the input stream, and returns that line.
- B 摘要: Starts a script by reading the entire content from a URL specified in attributes and appending it to dialog.script, with error handling and exit on failure.
- 静态失败原因: The static BERT model might have been misled by the lexical overlap of 'BufferedReader', 'URL', 'readLine()', and 'InputStreamReader' patterns, which are common in many URL-reading functions. The model may have focused on the shared API usage without capturing the different control flows and side effects.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would likely label this as non-clone because the overall functionality is different: one reads a single line and returns it, the other reads all lines into a buffer and has side effects (dialog.script). The structural similarity is minimal, and the functions serve different purposes.
- 共享行为: Both use BufferedReader to read text from a URL via an InputStream.
- 行为差异: Function a returns the first line; Function b concatenates all lines and appends to dialog.script.；Function a throws exception; Function b catches IOException and exits.；Function a takes a String URL; Function b takes a wabclient.Attributes object and extracts src.；Function a disconnects the connection; Function b does not explicitly disconnect.
- 修正建议: Improve models to consider overall control flow and return behavior, not just API calls.；Add negative sampling with similar API usage but different functionality.；Use program dependence graphs or data-flow analysis to distinguish between single-line read and full-file read.

### case_id=4734 FP lexical_or_api_overlap

- 方法: `executePost` vs `downloadModel`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Sends an HTTP POST request with form-encoded parameters and returns the response body as a string.
- B 摘要: Downloads an RDF model from a URL via HTTP and returns the parsed Model object.
- 静态失败原因: Static BERT/GraphCodeBERT likely over-focused on lexical and API token overlap (e.g., URL, HttpURLConnection, setRequestProperty, getInputStream) and structural similarity (try-catch pattern), missing the semantic differences in data flow and overall goal.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the high-level functionality differs significantly despite sharing common HTTP boilerplate. The functions serve different purposes (sending data vs downloading model) and have different signatures.
- 共享行为: Both open an HTTP connection；Both set request properties；Both get an InputStream from the connection；Both handle IOExceptions
- 行为差异: Different HTTP methods: POST vs implicit GET；Different input: url and parameters vs single URL；Different output: response string vs Model object；Different error handling: print stack trace and return null vs log debug and throw RuntimeException
- 修正建议: Incorporate data flow analysis to distinguish parameter manipulation and output type；Use type signatures (return type, parameters) as additional features；Train on more diverse examples to reduce bias towards common API patterns

### case_id=4735 FN benchmark_preference_bias

- 方法: `modifyApplicationMessage` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Modifies a property in a locale-specific properties file, copying English file if missing.
- B 摘要: Processes a zip file containing rule outputs, evaluates performance of rule lists.
- 静态失败原因: The static model correctly predicted non-clone due to low token overlap and distinct API usage; it did not fail.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might consider them clones due to superficial I/O similarity, but this seems like a mislabel; they are not functionally similar.
- 共享行为: Both perform file I/O operations；Both read lines using BufferedReader；Both use FileReader/FileWriter
- 行为差异: Completely different purpose: i18n modification vs. rule evaluation；Different data formats: .properties vs. .zip/.out；Different inputs and outputs: locale/message vs. dataset/zip
- 修正建议: Review BCB label for correctness；If BCB label is correct, consider adding domain-specific features to model

### case_id=4736 FN partial_functionality

- 方法: `sendExceptionToServer` vs `readVersion`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends exception details to a server via HTTP POST with various encoded parameters.
- B 摘要: Reads version, revision, and date from a resource file by parsing key-value lines.
- 静态失败原因: Low token overlap (0.21) and different method names; static models may not capture the semantic similarity of I/O patterns without deeper understanding.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB might consider them clones due to shared patterns of URL handling and I/O operations, but the overall purpose and data flow are very different, making this a borderline Type-4 clone at best.
- 共享行为: Both use URL and BufferedReader for I/O；Both handle IOException
- 行为差异: A performs HTTP POST to send data; B reads from a local resource；A constructs and writes a query string; B parses lines for specific prefixes；A uses URLConnection with output; B uses ClassLoader.getSystemResource；A writes to OutputStream; B reads from InputStream
- 修正建议: Use data flow analysis to compare the actual transformation of data；Require models to differentiate between input and output operations

### case_id=4737 FP lexical_or_api_overlap

- 方法: `main` vs `loadBinaryStream`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Main method that reads a Prolog file, parses it, generates adapter classes and resources, and writes them to a JAR file.
- B 摘要: Private method that copies binary stream data to HTTP response output stream and manages content headers.
- 静态失败原因: Static BERT likely overemphasized common API terms (e.g., IOException, File, stream, close) and error handling patterns, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels as non-clone (0) because the functions have entirely different high-level functionality despite some shared I/O patterns.
- 共享行为: Both involve I/O operations and handle exceptions.；Both use try-catch or try-finally blocks.
- 行为差异: Function A is a complex Prolog-to-Java adapter generator; Function B is a simple HTTP stream copier.；Function A has extensive logic for parsing, reflection, class generation; Function B only stream copies.；Function A writes to files; Function B writes to HTTP response.
- 修正建议: Incorporate method signatures and class context to capture semantics.；Use dataflow or control-flow analysis beyond token matching.；Train on more diverse examples to reduce sensitivity to boilerplate I/O patterns.

### case_id=4738 FN partial_functionality

- 方法: `doVersionCheck` vs `httpRequestByPOST`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Checks for new version by reading a version URL and extracting build numbers, then displays error on failure.
- B 摘要: Performs HTTP POST request with parameters and returns response body as string, with error handling.
- 静态失败原因: Static models like CodeBERT may over-rely on lexical overlap and common API sequences (e.g., InputStream, BufferedReader). The high structural similarity in reading lines might cause false positive prediction (BCB label 1) but here the static prediction is 0 (FN). Actually, static_prediction=0 means it missed a clone. So the model failed to recognize the similarity in the I/O reading pattern? Or it correctly distinguished them? Since BCB label=1, model predicted 0 (no clone). So the model correctly identified they are not clones. But the case says error_type=FN (false negative) from BCB perspective? Actually BCB label is ground truth; so model predicted 0 but BCB says 1. So model missed a clone. The static model might have been too strict, focusing on method names and overall logic, missing the shared pattern of reading from a URL line by line. Or the model might have been misled by differences in method signatures and library usage.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled these as clones because both involve reading from a URL line by line using similar I/O patterns, possibly considering it a Type-3 clone with small changes (different URL access method, different processing of lines). However, the overall functionality is different.
- 共享行为: Both open an input stream from a URL and read lines of text；Both use BufferedReader and InputStreamReader；Both have try-catch for IOException
- 行为差异: Function A is void and calls another method with extracted versions; Function B returns String or null；Function A reads URL via URL.openStream() (GET); Function B uses HttpClient POST；Function A shows error dialog; Function B sets error fields and returns null；Function A has cursor wait indicators; Function B does not
- 修正建议: Incorporate more structural similarity on common sub-patterns；Use dataflow analysis to capture shared I/O operations；Consider BCB's labeling criteria more explicitly during training

### case_id=4739 FP long_range_semantics

- 方法: `decodeFileToFile` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `static_summary_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Decodes a Base64 encoded file and writes the decoded content to an output file.
- B 摘要: Handles various UI actions such as setting Graphviz and ImageMagick paths, displaying file chooser dialogs, and updating preferences.
- 静态失败原因: The static BERT/GraphCodeBERT model likely overemphasized superficial token overlap (e.g., 'File', 'InputStream', 'OutputStream') and failed to capture the long-range semantic structure of function B, which is dominated by UI event handling rather than file I/O. The model may also be misled by the presence of try-catch-finally blocks in both, but they are used for completely different reasons.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB typically labels clones only if they share significant functional similarity, such as implementing the same algorithm or logic. These two functions have entirely different purposes and only share trivial file-handling APIs, so BCB would correctly label them as non-clones.
- 共享行为: Both use File I/O operations (reading/writing files) and exception handling.
- 行为差异: Function A performs a well-defined file decoding task with a clear success/failure return.；Function B is a lengthy event handler managing multiple GUI interactions and preference updates with no return value (void).；Function A uses Base64 decoding; Function B does not involve any encoding/decoding.；Function B has complex conditional logic for different commands; Function A has a simple linear flow.
- 修正建议: Improve model's ability to capture overall program semantics through graph-based representations or control flow analysis.；Incorporate task-oriented embeddings that distinguish between data processing and UI control flows.；Use contrastive learning to emphasize functional similarity over lexical overlap.

### case_id=4740 FN other

- 方法: `readData` vs `postXml`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Parses static string constants into sets and maps for data initialization.
- B 摘要: Sends an HTTP POST request with SOAP action and returns the response as a string.
- 静态失败原因: The model correctly predicted non-clone; no failure occurred.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB label may be erroneous or based on incomplete context; functions are semantically unrelated.
- 行为差异: Different I/O: readData uses StringTokenizer on static strings, postXml uses HTTP connection.；Different return types: void vs String.；Different data processing: building sets/hashes vs sending/receiving XML.；No common algorithmic steps.

### case_id=4741 FN partial_functionality

- 方法: `copyResource` vs `hyperlinkUpdate`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource from a URL or file path to a destination file.
- B 摘要: Handles hyperlink activation by fetching URL content and displaying it in a dialog.
- 静态失败原因: Static BERT methods rely on token overlap and structural similarity; low Jaccard (0.104) and different method names, control flow, and library usage caused it to miss the semantic similarity in the I/O pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider this a Type-4 clone because both functions share the core operation of opening a URL stream and copying its contents to an output, a common resource-handling pattern, even though the output destinations and surrounding code differ.
- 共享行为: Both open an InputStream from a URL；Both copy the stream data to an output (file stream or StringWriter)；Both close the input stream after copying
- 行为差异: Function A writes to a file; Function B writes to a StringWriter and displays it in a GUI；Function A uses manual byte-by-byte copy; Function B uses IOUtils.copy；Function B includes UI creation (JEditorPane, JDialog) and additional error handling
- 修正建议: Incorporate data flow analysis to detect stream-copy patterns；Add API usage similarity (e.g., openStream, copy, close)；Consider partial functionality matching for I/O operations

### case_id=4742 FN benchmark_preference_bias

- 方法: `readVersion` vs `invoke`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Reads a version properties file from classpath and parses version, revision, and compile date.
- B 摘要: Invokes a remote HTTP POST method with JSON payload, reads response, and deserializes it to the return type, with retry on connect timeout.
- 静态失败原因: The static model correctly predicted non-clone; BCB label may be erroneous.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have considered both as reading input streams and parsing lines, but that is too superficial; likely a benchmark labeling error.
- 共享行为: Both use BufferedReader to read lines from an input stream.；Both handle IOException in a general manner.
- 行为差异: A reads local classpath resource; B makes remote HTTP call.；A parses prefix-based key-value lines; B parses JSON.；A has no retry; B has retry logic.；A returns void and sets fields; B returns deserialized object.
- 修正建议: Review BCB ground truth for this pair; likely it should be non-clone.；Static model does not need fixing.

### case_id=4743 FN partial_functionality

- 方法: `callApiPost` vs `invoke`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Makes an HTTP POST request with parameters, checks response code against expected value, and returns an InputStream.
- B 摘要: Invokes a remote service method via HTTP POST with JSON payload, retries on timeout, and returns deserialized object.
- 静态失败原因: Static BERT methods may rely on token overlap and structural similarity; here token Jaccard is low (0.0986) and code structures differ significantly (different libraries, error handling, retry logic). The shared patterns (HTTP POST, response handling) are not captured by static models due to different vocabulary and control flow.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels clones based on high-level functional similarity (both are HTTP POST methods) even if implementations differ, falling under Type-3 or Type-4.
- 共享行为: Both perform HTTP POST requests；Both check HTTP response status；Both handle errors by throwing exceptions
- 行为差异: Different HTTP client libraries (java.net vs Apache HttpClient)；Different input formats (parameters map vs MethodInvocation)；Different output types (InputStream vs deserialized object)；Different error handling (expected code check vs status code >=300, with retry logic)
- 修正建议: Use dataflow analysis to capture shared dataflow (e.g., HTTP request/response cycle)；Incorporate API usage patterns and high-level intent via code summarization；Reduce reliance on exact token matches; use synonym or functional embedding.

### case_id=4744 FN lexical_or_api_overlap

- 方法: `getZipAsFile` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.3`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Extracts the content of a DigitalObject as a temporary zip file.
- B 摘要: Builds an HTML site for editing by transforming XML pages and writing output files.
- 静态失败原因: The static BERT model likely relied on low lexical/API overlap (Jaccard 0.036) and different method names, failing to capture the broad functional similarity in file I/O operations.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may consider them clones due to the shared pattern of reading from an input stream and writing to a file output stream, a common I/O operation pattern that is considered a broad Type-3/Type-4 clone.
- 共享行为: Both perform file I/O operations (reading input streams, writing to files)；Both handle I/O exceptions
- 行为差异: Different input parameters and output purposes；Function A is a simple utility; Function B is a complex page-building process；Different processing logic and error handling
- 修正建议: Incorporate longer-range context or structural patterns；Use data-flow analysis to detect similar I/O patterns；Improve handling of truncated code

### case_id=4745 FN benchmark_preference_bias

- 方法: `readData` vs `readVersion`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Initializes multiple character sets and mapping structures from string tokens and a file containing Tibetan/Sanskrit character data.
- B 摘要: Reads version information from a classpath resource file and sets version, revision, and compileDate fields.
- 静态失败原因: Static BERT models rely on token overlap and syntactic structure; with Jaccard similarity of 0.08, the model correctly identified them as non-clones, but BCB's label may be considered a misannotation from a more lenient clone perspective.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled these as clones due to both being private methods that read and parse data from external sources during initialization, but the actual functionality is entirely different.
- 共享行为: Both read input from external sources (strings or files) and parse lines
- 行为差异: readData builds complex data structures (sets, hash maps) while readVersion just sets a few fields；readData handles multiple token types and file I/O with error handling; readVersion only reads one file；readData has much larger scope and side effects
- 修正建议: Re-evaluate BCB label for this pair as likely false positive；Improve model to recognize that broad functional similarity (both 'reading' something) is insufficient for clone detection without deeper semantic matching

### case_id=4746 FP lexical_or_api_overlap

- 方法: `importSequences` vs `doVersionCheck`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Imports sequences from a URL by parsing FASTA-like format, extracting names and sequence strings.
- B 摘要: Performs version check by reading version info from a URL and delegating to another method.
- 静态失败原因: Static BERT models may have been misled by the common lexical tokens (URL, InputStream, IOException, readLine) and the general pattern of reading from a URL and parsing lines, causing a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels non-clone because the domain-specific logic (FASTA parsing vs version parsing) is not functionally equivalent, and the overall structure is not similar enough for a broad clone despite shared I/O boilerplate.
- 共享行为: Open a URL stream and read lines；Parse lines conditionally；Handle IOException
- 行为差异: Different parsing patterns (FASTA header vs build version prefix)；Different output (populating lists vs calling another method)；Use of different utility classes (ImportHelper vs BufferedReader)
- 修正建议: Incorporate structural matching that focuses on core logic beyond boilerplate I/O；Use data-flow analysis to differentiate parsing logic；Add negative weighting for common API usage patterns

### case_id=4747 FN benchmark_preference_bias

- 方法: `modifyApplicationMessage` vs `tail`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.95`
- 推荐路线: `preference_memory_with_manual_audit`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Modifies a properties file by updating or adding a message key-value pair for a given locale.
- B 摘要: Implements the tail command to output the last 1024 bytes of a file, with optional follow mode.
- 静态失败原因: Static BERT models often rely on token overlap and syntactic similarity; here token Jaccard is low (0.159) and the model correctly identified them as different under strict semantics, failing to match BCB's broader clone definition.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider these as Type-3 clones due to similar control flow patterns (while loop, if-else, try-catch) and file I/O operations, despite different domains and purposes.
- 共享行为: Both functions involve reading from a file, processing data, and writing to an output (file or stdout).；Both use while loops and conditionals to control flow.；Both handle exceptions with try-catch.
- 行为差异: Function A modifies a specific key in a properties file; Function B outputs raw file content to console.；Function A works with property files and locale-specific paths; Function B works with Hadoop file system and arbitrary files.；Function A may append a new key if not found; Function B implements tail logic with offset tracking.；Function B has an optional follow mode that loops indefinitely with sleep; Function A is a single pass.
- 修正建议: Incorporate BCB-style annotations during training or fine-tuning.；Use functional similarity metrics that capture intent rather than only syntax.；Adjust clone detection threshold to align with BCB's broad criteria.

### case_id=4748 FP boilerplate_overlap

- 方法: `doVersionCheck` vs `getFullScreenUrl`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Performs a version check by reading a remote file and extracting build numbers.
- B 摘要: Retrieves the full screen URL of a YouTube video by parsing the page source.
- 静态失败原因: Static BERT may have over-relied on lexical and structural overlap of common I/O boilerplate (URL, BufferedReader, while loop, try-catch) while missing the semantic differences in parsing and output.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB considers functional similarity; these functions have distinct core logic and domain, so they are non-clones.
- 共享行为: Both open a URL, read lines, parse for specific keywords, and handle exceptions.
- 行为差异: Different purpose: version check vs video URL extraction；Different UI feedback (wait cursor vs progress bar)；Different parsing logic and output
- 修正建议: Use dataflow analysis to capture differences in specific string patterns and outputs；Incorporate domain knowledge or fine-tune on functional semantics

### case_id=4749 FN partial_functionality

- 方法: `copy` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a source file to a destination file using FileChannel transferFrom, ensuring parent directories exist and closing streams in finally.
- B 摘要: Launches a NexOpen project configuration by checking Maven poms, processing XML profiles, setting Hibernate properties, and running an install action, which includes copying a resource file via IOUtils.copy.
- 静态失败原因: Low token overlap (0.07) and large difference in length and method names led the model to classify as non-clone, missing the shared sub-task of file copying due to its embedded nature in a larger method.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may accept these as Type-4 clones because both functions contain a file-copying sub-operation and similar resource management patterns, considering them partially functionally similar.
- 共享行为: Both involve copying data from an input source to an output destination.；Both check for file existence or validate inputs before operations.；Both use try-finally for resource cleanup.
- 行为差异: Code A is a generic file copy utility; Code B is a complex Eclipse plugin launch handler.；Code B includes XML parsing, project property management, and job scheduling unrelated to A.；The copying in B is a minor sub-step, whereas A performs only copying.
- 修正建议: Enhance model to detect sub-function similarities, e.g., via code summarization or attention over key subgraphs.；Use block-level or flow-based representations to capture common I/O patterns across different contexts.

### case_id=4750 FN partial_functionality

- 方法: `save` vs `doGet`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Saves a set of files into a package directory by first writing raw content to a base directory, then copying each file into the package directory while prepending a package declaration.
- B 摘要: Handles HTTP GET request for a page, manages page lookup, authorization, caching, and renders response, optionally writing cached output to a file.
- 静态失败原因: The model likely focused on the file I/O API usage (File, FileWriter, flush, close) and missed the overall context and purpose. The low token Jaccard indicates minimal lexical overlap, but the model may have over-weighted the shared API calls.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB might have considered both functions as involving file writing operations and exception handling, leading to a broad Type-4 classification, though the core functionality differs significantly.
- 共享行为: Both involve file I/O operations (writing to files using FileWriter).；Both use try-catch for exception handling.；Both perform sequential steps with directory/file existence checks.
- 行为差异: A is a static utility for saving files; B is a servlet method handling user requests.；A writes byte arrays; B writes HTML strings.；A creates directories; B handles permissions, caching, and logging.；A uses BufferedReader/Writer for copying; B uses response object for output.
- 修正建议: Incorporate control flow and data flow analysis to capture overall program behavior.；Use more contextual embeddings that understand servlet vs. utility patterns.；Add specialized features for distinguishing file I/O utilities from web request handlers.

### case_id=4751 FP lexical_or_api_overlap

- 方法: `main` vs `transformSingleFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Parse Prolog file, generate adapter JAR with classes and serialized data.
- B 摘要: Transform X3D editor file to compressed gzipped VRML file.
- 静态失败原因: The model likely over-relied on common API calls (File, FileInputStream, FileOutputStream, try-catch patterns) and ignored the distinct domain-specific logic, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would not consider them clones because they have different functionality and low token similarity; BCB typically requires significant behavioral overlap or similar syntactic structure.
- 共享行为: Both perform file I/O operations；Both handle exceptions with error messages and early return/null
- 行为差异: Different problem domains (adapter generation vs file compression)；Different output formats (JAR with classes vs gzipped .x3dv)；Different input handling (command-line args vs editor data object)
- 修正建议: Improve training data with more diverse non-clone pairs sharing only boilerplate；Enhance model to focus on core algorithmic logic rather than common API usage；Use attention masking to reduce weight of common error-handling patterns

### case_id=4752 FN partial_functionality

- 方法: `read` vs `doVersionCheck`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a file or URL and returns an integer status code by calling an internal read method, handling IOException.
- B 摘要: Performs a version check by reading a URL, parsing build version lines, and calling another method, with wait cursor and error handling.
- 静态失败原因: Static BERT models like GraphCodeBERT rely on token sequences and structural patterns. The low token overlap (0.25) and different method names, control flow, and overall purpose likely cause the model to miss the shared URL-reading pattern. The model may be biased towards syntactic similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as clones because they share the core behavior of opening a URL, reading data, and handling IO exceptions, which is a typical pattern for network-related functions. The annotators might overlook the different surrounding logic and focus on the similar IO skeleton.
- 共享行为: Both open an InputStream from a URL.；Both handle IOException with error reporting.；Both involve reading from an external resource.
- 行为差异: Function A supports both local files and URLs, while B only reads from a URL.；Function A returns a status code, while B has void return and calls another method.；Function B parses lines for specific prefixes and shows/hides a wait cursor, which A does not do.
- 修正建议: Incorporate call graph information to identify common library usage patterns.；Use data augmentation that creates positive pairs with similar IO skeletons but different logic.；Fine-tune on more challenging Type-3/Type-4 clone pairs from BigCloneBench.

### case_id=4753 FP boilerplate_overlap

- 方法: `perform` vs `encrypt`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Handles a Struts action for concept classification, builds XML data, sends HTTP request, parses result, and manages session attributes.
- B 摘要: Computes a hash digest using a given algorithm, salt, and password, returning hex string.
- 静态失败原因: The static model likely overemphasized surface-level similarities like try-catch blocks, StringBuffer usage, and generic method structures, ignoring the vast semantic gap in intent and behavior.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clone because the functions have completely different purposes and functionality, despite sharing some generic Java patterns.
- 共享行为: Both perform string manipulation and use try-catch blocks for exception handling.
- 行为差异: Function A is a web controller with complex state management and HTTP communication; function B is a cryptographic hash utility.；Inputs and outputs are entirely different: A takes Struts objects and returns ActionForward; B takes algorithm, password, seed and returns hex string.；Control flow: A has session checks, loops, and URL connection; B has only digest computation.
- 修正建议: Incorporate control-flow and data-flow analysis to distinguish tasks.；Use program dependence graphs or abstract syntax tree differences.；Train with more diverse negative examples to avoid boilerplate false positives.

### case_id=4754 FP lexical_or_api_overlap

- 方法: `executePost` vs `sendRequest`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.85`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Sends an HTTP POST request with URL-encoded parameters and returns the response body as a string.
- B 摘要: Sends an HTTP request to a servlet with XML content using GZIP compression and checksum, parses response as XML, but returns an empty string.
- 静态失败原因: Static BERT models rely on token embeddings and may over-focus on common HTTP-related keywords (e.g., 'URL', 'HttpURLConnection', 'setRequestProperty') while missing the structural and semantic differences in data handling and return values.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled non-clone because while both methods send HTTP requests, they differ in input format, output handling, and additional setup logic. BCB requires functional similarity, not just shared API usage.
- 共享行为: Both perform HTTP POST requests.；Both set output and input on the connection.；Both write data to an output stream.；Both read the response from an input stream.
- 行为差异: Function A uses URL-encoded parameters via DataOutputStream; B uses XML with GZIP compression and checksum.；Function A returns the response body; B always returns an empty string after parsing but discarding the result.；Function B includes a UI dialog for server URL/port configuration; A uses a direct target URL.；Function B uses applet context and system preferences; A does not.
- 修正建议: Incorporate structural and data-flow features to differentiate I/O handling.；Use contrastive learning to emphasize semantic differences over lexical overlap.；Add summarization-based features to capture overall intent and return value behavior.

### case_id=4755 FN partial_functionality

- 方法: `buildDeb` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Builds a Debian package by writing archive header and copying control and data files.
- B 摘要: Configures and launches a NexOpen project, handling XML profiles and reverse engineering files.
- 静态失败原因: Static BERT models rely heavily on token-level similarity; low Jaccard (0.05) and no overlapping key phrases would lead to a non-clone prediction.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: None
- 共享行为: Both perform file I/O operations.
- 行为差异: Function A writes a Debian archive format; Function B manages Eclipse launch configuration and Maven pom files.；Function A is a static utility; Function B is an instance method with complex Eclipse/plugin context.；Function A has no external dependencies; Function B uses many Eclipse and Maven classes.
- 修正建议: Improve model to understand high-level purpose rather than token overlap.；Use structural embeddings or CFG-based similarity.

### case_id=4756 FP boilerplate_overlap

- 方法: `getContent` vs `sendPost`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Executes an HTTP request using Apache HttpClient and returns the response body as a string.
- B 摘要: Sends an HTTP POST request using java.net.HttpURLConnection with parameters and returns the response body as a string.
- 静态失败原因: The model may have been misled by the boilerplate code common to reading HTTP responses (BufferedReader, InputStreamReader, readLine) and the structural similarity of both being static methods returning String. It failed to recognize the distinct library usage and the difference in HTTP method intent.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely considered these non-clones because they use different HTTP libraries, different input parameters, and different HTTP methods (generic vs. POST). While both read HTTP responses, the core functionality (sending data vs. not) and API usage differ significantly.
- 共享行为: Both make an HTTP request and read the response body line by line.；Both return the response content as a String.
- 行为差异: Method A uses Apache HttpClient and takes an HttpUriRequest; method B uses java.net.HttpURLConnection and takes a URL string and parameter string.；Method A does not send any data; method B sends POST data to the output stream.；Method A throws Exception; method B catches Exception and shows a message.；Method A appends lines with newline; method B concatenates lines directly.
- 修正建议: Improve training data to include more examples with different HTTP libraries and methods.；Enhance model to capture higher-level intent differences, such as sending vs. not sending data.；Use data-flow analysis to distinguish between output and input handling patterns.

### case_id=4757 FP boilerplate_overlap

- 方法: `getJSONData` vs `getFrameworkFactory`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Downloads JSON from a URL using HttpClient and parses it into a JSONObject.
- B 摘要: Reads a service configuration file from classpath and instantiates a FrameworkFactory via reflection.
- 静态失败原因: The model likely overemphasized the shared boilerplate pattern (BufferedReader + readLine loop) and missed the critical API differences that define the functions' distinct behaviors.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB assigns non-clone because the functions have entirely different purposes and use distinct APIs (HttpClient vs URL/Class.forName).
- 共享行为: Use BufferedReader to read lines from an InputStream；Loop over lines until null
- 行为差异: Source of data: HTTP response vs classpath resource；Return type: JSONObject vs FrameworkFactory；Exception handling: catch Exception vs throws Exception and try-finally；Post-processing: JSON parsing vs class loading and instantiation
- 修正建议: Incorporate data-flow analysis to track data sources and sinks.；Train with more emphasis on API calls and their context.；Use contrastive learning to differentiate similar boilerplate with different purposes.

### case_id=4758 FP lexical_or_api_overlap

- 方法: `googleImageSearch` vs `getFrameworkFactory`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Searches Google Images using HTTP and parses HTML to extract image URLs.
- B 摘要: Loads an OSGi FrameworkFactory from a service configuration file using classpath resources.
- 静态失败原因: The static model overemphasized lexical and API overlap (URL, BufferedReader, try-catch) and missed the semantic mismatch, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled non-clone because the functions have completely different purposes (image search vs. OSGi service loading) and only share superficial I/O patterns, which is insufficient for even broad Type-3/4 similarity under their benchmark.
- 共享行为: Both use URL and BufferedReader for input/output.；Both include exception handling (try-catch or try-finally).
- 行为差异: A performs an HTTP image search, B reads a local service configuration file.；A parses HTML response, B reads a properties-like file with comments.；A uses HttpURLConnection with User-Agent, B uses ClassLoader.getResource.；A adds multiple extracted URLs to a list, B returns a single object instance.
- 修正建议: Incorporate data-flow and control-flow analysis to capture program semantics.；Use call-graph or API usage context to distinguish different libraries.；Include functional behavior modeling, such as intent classification, to reduce false positives.

### case_id=4759 FN partial_functionality

- 方法: `copyResource` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource file from a URL or local file to a destination file using single-byte read-write.
- B 摘要: Compresses a file using GZIP by reading in chunks and writing to a GZIP output stream.
- 静态失败原因: Static BERT models rely heavily on token overlap and structural patterns. Low Jaccard (0.2), different method names, and distinct API calls (e.g., GZIPOutputStream vs FileOutputStream) obscured the shared stream-copy semantics.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely labels this as a clone because both functions implement a core data transfer loop from input to output, which is a common functional pattern. The differences in chunk size, compression, and error handling are considered minor variations in a broad Type-3/Type-4 category.
- 共享行为: Read from an input stream and write to an output stream until end of stream.
- 行为差异: copyResource reads byte-by-byte; main reads in larger chunks.；copyResource performs raw copy; main compresses using GZIP.；copyResource handles both URL and local files; main only handles local files.；Error handling differs: copyResource throws exception; main prints messages.
- 修正建议: Use data-flow or graph-based representations to capture stream operations.；Incorporate functional similarity metrics beyond token overlap.；Train with contrastive learning to align similar semantics with different surface forms.

### case_id=4760 FP boilerplate_overlap

- 方法: `main` vs `loadURL`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a URL's content line by line and prints each line to standard output.
- B 摘要: Reads a URL with optional HTTP Basic authentication, saves content to a temporary file, and updates a progress label.
- 静态失败原因: The static model likely over-focused on the common boilerplate pattern (URL, BufferedReader, while loop) and missed the significant differences in authentication, file I/O, and UI interaction.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BigCloneBench annotations typically require a stronger functional similarity; the shared URL-reading pattern is considered boilerplate rather than core functionality, leading to a non-clone label.
- 共享行为: Open a URL and read lines using BufferedReader
- 行为差异: Code_a prints lines to console; Code_b writes to a file and updates a UI label；Code_b handles authentication and creates a temporary file；Code_b includes UI progress updates
- 修正建议: Incorporate dataflow or control flow analysis to capture I/O differences；Use contrastive learning to distinguish similar boilerplate with different side effects；Pay attention to method signatures and all API calls beyond the common pattern

### case_id=4761 FP lexical_or_api_overlap

- 方法: `getDatasetsList` vs `importSequences`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Retrieves a list of dataset names from a URL, caching results.
- B 摘要: Imports biological sequences from a URL, parsing FASTA format.
- 静态失败原因: Static BERT likely overfitted to common API tokens (URL, InputStream, IOException) and similar try-catch structure, ignoring the semantic domain difference.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clone because functions have distinct domain-specific purposes and control flow, despite sharing I/O patterns.
- 共享行为: Both read input from a URL；Both use InputStreamReader；Both handle IO exceptions；Both store data in collections
- 行为差异: Different data formats (lines vs FASTA with '>' delimiters)；A caches results, B does not；A is synchronized, B is not；Different exception handling (A throws RuntimeException, B prints stack traces and catches EOFException)
- 修正建议: Incorporate structure-aware modeling (e.g., AST or dataflow)；Use domain-specific fine-tuning or contrastive learning on BCB；Add sensitivity to method names and high-level purpose

### case_id=4762 FP dataflow_blindspot

- 方法: `readZoneIDs` vs `getXML`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_with_trace`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a list of zone IDs from a resource file and returns them as a set of integers.
- B 摘要: Fetches XML content from a URL and returns it as a concatenated string.
- 静态失败原因: The model likely over-relied on structural similarities (both use URL.openStream(), readLine loop, and similar try-catch blocks) without capturing the differing return types and data processing logic.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 dataflow_trace_and_outputs。
- BCB 偏好解释: BCB typically labels clones based on overall functional similarity. Here, the functions have completely different purposes (one reads numeric IDs, the other fetches XML text), so they are not clones.
- 共享行为: Both open a URL to read data.；Both use BufferedReader/LineNumberReader to read lines.；Both handle exceptions during I/O.
- 行为差异: Function A reads from a class resource, while B reads from a constructed URL.；A returns a HashSet<Integer>, B returns a String.；A parses each line as an integer, B concatenates lines.；A catches generic Exception, B catches specific exceptions and returns null.
- 修正建议: Consider return types and type transformations in the representation.；Incorporate data flow analysis to distinguish between integer parsing and string concatenation.；Use contrastive learning with negative examples that have similar structure but different semantics.

### case_id=4763 FP lexical_or_api_overlap

- 方法: `copyFile` vs `main`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Copies a source file to a destination file using FileChannel.transferTo and returns boolean success.
- B 摘要: Main method that parses command-line arguments, reads a Prolog file, and generates adapter classes and resources.
- 静态失败原因: The model may have been misled by overlapping keywords like 'FileInputStream', 'FileOutputStream', 'File', 'IOException', and common try-catch structure, even though the actual logic is entirely different.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clones when methods have no common functionality or similar logic. Despite both dealing with files, one is a straightforward copy and the other is an elaborate adapter generator, which are semantically unrelated.
- 共享行为: Both involve file I/O operations；Both use try-catch for IOException handling
- 行为差异: First function is a simple file copy; second is a complex code generation pipeline；First returns boolean; second produces output files and prints messages；First uses FileChannel; second uses many custom classes for parsing and generation
- 修正建议: Increase training data with diverse file-handling examples；Incorporate structural features like AST or control flow graphs；Use contrastive learning to better distinguish low-similarity pairs

### case_id=4764 FN partial_functionality

- 方法: `startScript` vs `seeURLConnection`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a URL from an attribute, opens a stream, reads lines, appends to dialog script, and ends the script.
- B 摘要: Opens a connection to a hardcoded URL, reads lines, appends to a string buffer, and logs the result.
- 静态失败原因: The static model likely focused on syntactic differences such as different method names, error handling, and output mechanisms. The low token Jaccard similarity (0.1875) suggests it missed the underlying semantic similarity of the URL reading pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider these clones because they share the core functionality of reading from a URL line by line and accumulating the content. Differences in error handling, output, and URL source are considered secondary for broad Type-3/Type-4 clone annotation.
- 共享行为: Both open a URL connection and read lines via BufferedReader.；Both concatenate the read lines into a string buffer/accumulator.
- 行为差异: Source of URL: attribute vs hardcoded.；Error handling: exits on IOException vs throws Exception.；Output destination: dialog.script vs log.；Loop structure: while(true) with break vs while((s=readLine())!=null).
- 修正建议: Incorporate structural patterns like 'read from URL' into the model.；Use dataflow analysis to track the URL opening and reading operations.；Train on broader clone types (Type-3/Type-4) to recognize functional similarity despite syntactic differences.

### case_id=4765 FN benchmark_preference_bias

- 方法: `getFile` vs `actionPerformed`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.8`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies an XML endpoint attribute, and saves it with temporary file handling.
- B 摘要: Reads a gzipped file of rs IDs, constructs an HTTP POST to NCBI Entrez to fetch SNP data, and copies the response to stderr.
- 静态失败原因: Static BERT models like GraphCodeBERT rely heavily on token and syntactic similarity; the token Jaccard is very low (0.11) and the structures, while both involving try-catch and URL connections, differ significantly in length and specific operations, causing the model to correctly classify them as non-clones in a strict sense.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider these as broad Type-3 clones because both follow a pattern of 'network I/O with error handling and stream processing', even though the specific protocols, data formats, and purposes differ.
- 共享行为: Both use URL and URLConnection for network I/O；Both handle IOException with try-catch；Both read from input streams and write to output streams
- 行为差异: A downloads a specific WSDL file via GET; B queries NCBI via POST；A modifies XML and saves to a file; B outputs raw XML to stderr；A manages temporary files and deletion; B reads local gzip file for input
- 修正建议: Incorporate data flow and API usage patterns to capture abstract behavioral similarities；Use a more fine-grained clone classification that distinguishes strict from broad clones

### case_id=4766 FN lexical_or_api_overlap

- 方法: `copyResource` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource (URL or file) to a destination file using byte-wise stream copy.
- B 摘要: Copies a file to another file using FileChannel transfer.
- 静态失败原因: Low token Jaccard similarity (0.14) and different API usage (InputStream vs FileChannel) lead GraphCodeBERT to classify as non-clone, as it relies on lexical and structural overlap.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB often considers functions that achieve the same end goal (copying data to a file) as clones, even if implementation details differ, especially across different projects.
- 共享行为: Both copy data from a source to a destination file.
- 行为差异: Source type: resource URL/file vs file only；Copy method: byte-by-byte InputStream/OutputStream vs FileChannel transfer；Exception handling: throws Exception vs IOException；Method visibility: private vs public static
- 修正建议: Incorporate data-flow analysis to capture semantic intent；Use graph-based representations or abstract syntax trees；Consider method name and comment similarity；Train on functional clone benchmarks like BigCloneBench

### case_id=4767 FN partial_functionality

- 方法: `testNetworkHTTP` vs `readURL`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Tests network connectivity by making multiple HTTP GET requests to specific URLs and discarding responses.
- B 摘要: Reads content from a given URL and prints each line to standard output.
- 静态失败原因: Static BERT models rely on lexical overlap and structural similarity; the low token Jaccard (0.27) and different method names, number of URL accesses, and output handling caused the model to miss the underlying semantic similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label them as clones because both methods perform the core operation of reading from a URL over HTTP, which is a common functional pattern (Type-4 clone). The differences in number of requests and output handling are considered minor in the context of semantic similarity.
- 共享行为: Open a URL connection；Read response line by line using BufferedReader；Handle exceptions with printStackTrace；Close resources in finally block
- 行为差异: A uses hardcoded URLs and makes multiple requests; B uses a parameter URL and makes one request；A discards read lines; B prints them to System.out；A uses HttpURLConnection; B uses URL.openStream()；A catches IOException only; B catches Exception
- 修正建议: Incorporate data flow and control flow analysis to identify common I/O patterns；Use AST-based or graph-based representations to capture essence of URL reading；Train on examples that embed similar functionality in different contexts

### case_id=4768 FN benchmark_preference_bias

- 方法: `testAddLinkToImage` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: A test method that copies image files from classpath to a temporary folder and adds report links to them.
- B 摘要: A method that builds a site for editing by reading XML, transforming content, and writing output files.
- 静态失败原因: Static BERT/GraphCodeBERT models likely predicted non-clone correctly because token Jaccard is very low (0.056) and the overall structure and length differ significantly, resulting in low embedding similarity.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled these as clones due to both methods involving file I/O and using the file separator, possibly considering partial functionality overlap in file handling, but the methods are semantically and structurally very different.
- 共享行为: Use System.getProperty("file.separator")；Perform file I/O operations (read/write streams)；Operate on files with paths
- 行为差异: Function A is a simple test with fixed resources; B is a complex site builder with many parameters and XML processing.；Function A uses a report object to add links; B writes entire HTML pages using transformers and FTP.；Function A has no loops or conditionals; B has loops over pages and conditional logic.；Function A has a single output folder; B takes multiple path parameters and writes to a specific output path.
- 修正建议: Improve training data to reduce reliance on superficial file I/O overlap;；Incorporate semantic understanding of method purpose (e.g., test vs. production code);；Use contrastive learning to separate methods with different overall tasks even if they share low-level operations.

### case_id=4769 FN lexical_or_api_overlap

- 方法: `doVersionCheck` vs `readGeoParserResult`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches a version check file from a URL, parses lines for version and build numbers, and notifies user if a new version is available.
- B 摘要: Sends a record content as XML to a geo parser service, parses the response to extract place names and optional gazetteer IDs, with retry logic.
- 静态失败原因: Static BERT models may over-rely on lexical and API-level overlaps (URL, BufferedReader, while loop) and ignore the broader context and semantic differences, leading to a false negative (predicting non-clone when actually clone? Actually here static predicted 0 meaning non-clone, but BCB said clone, so the model failed to detect a clone? Wait: The error_type is FN, meaning BCB label is 1 (clone) and static_prediction is 0 (non-clone), so the model missed it. But we think it's not a clone. So the model actually correctly predicted non-clone? That's a contradiction: BCB label may be wrong. In this case, the static model failed by not agreeing with the (possibly incorrect) BCB label. The failure is that the model didn't match the benchmark's labeling. So why_static_bert_failed should explain why the model didn't pick up the spurious similarities that led BCB to label them as clones.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may have labeled as clone due to superficial similarities like URL opening and line-by-line reading, which are common boilerplate in Java I/O. However, the overall functionality and structure are very different, so it should not be considered a clone even under broad Type-4.
- 共享行为: Open a URL and read lines via BufferedReader；Use try-catch for exception handling
- 行为差异: Domain: version checking vs geo parsing；Input parsing: simple line prefix vs XML；Output: void with GUI messages vs collection of tuples；Error handling: single catch vs retry loop
- 修正建议: Incorporate more semantic features like method purpose classification or domain analysis.；Use data flow or call graph to differentiate between different types of URL reading tasks.；Adjust training to penalize over-reliance on common I/O patterns.

### case_id=4770 FP lexical_or_api_overlap

- 方法: `getRequestContent` vs `postXml`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Performs a simple HTTP GET request to a URL and returns the first line of response.
- B 摘要: Performs an HTTP POST with XML payload and SOAP header, reads entire response multiline, and returns it as a string.
- 静态失败原因: Over-emphasized lexical and API surface overlap (URL, HttpURLConnection, BufferedReader, readLine) and boilerplate code pattern (try, open, read, close), ignoring the different request methods, data flow (input vs output), and response handling granularity.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels as non-clone when functions implement different API usage patterns and serve distinct purposes, even if they share common boilerplate (URL connection, reading). Here the high-level intent (GET vs POST, single line vs full response) differs significantly.
- 共享行为: Open HTTP connection to a URL；Read response using BufferedReader；Return a String derived from response
- 行为差异: Method A uses default GET request; Method B explicitly sets POST method with custom headers and SOAPAction.；Method A reads only the first line; Method B reads all lines and concatenates.；Method B sends XML data via OutputStream; Method A does not send any data.；Method A does not set timeouts or content-type; Method B sets connection/read timeouts and XML content-type.
- 修正建议: Incorporate dataflow analysis to distinguish read-only vs read-write connections.；Capture request-method setting (POST vs default GET) as a critical differentiating feature.；Consider loop structure (readLine for full response vs single readLine) as a behavioral signal.

### case_id=4771 FN partial_functionality

- 方法: `copyOverWarFile` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a WAR file from a local directory to the apps data directory and extracts it, while setting system properties.
- B 摘要: Downloads a KMZ file from a URL and extracts its zip entries to the local file system.
- 静态失败原因: Static BERT models rely on token and structural similarity. The functions differ in method names, libraries used (IOUtils vs raw streams), and control flow. The high-level similarity in archive extraction is not evident from token overlap (Jaccard=0.162) or surface syntax.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels functions with similar low-level I/O patterns (stream handling, archive extraction) as broad clones, even if the high-level task differs, treating them as Type-3/Type-4 clones.
- 共享行为: Both involve opening an input stream to read a compressed archive (WAR/ZIP format).；Both extract the archive contents to output files using Java I/O streams.
- 行为差异: A copies a local file, B downloads from a URL.；A uses IOUtils.copy for bulk copy, B uses manual buffer loop.；A specifically targets WAR files, B targets KMZ/ZIP files.；A includes additional tasks like setting system properties and JFileChooser.
- 修正建议: Incorporate dataflow analysis to detect common operations like reading from an InputStream and writing to FileOutputStream.；Use API-level abstraction to identify archive extraction patterns (e.g., ZipInputStream usage).；Augment training with examples of partial functionality clones across different application domains.

### case_id=4772 FN benchmark_preference_bias

- 方法: `createButtonCopyToClipboard` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Creates a SWT button that copies an environment report to clipboard on click.
- B 摘要: Launches a NexOpen project configuration, processes Maven pom files, sets up Hibernate dialect and reverse engineering files, and triggers an install action.
- 静态失败原因: The static model correctly predicted non-clone (0); it did not fail in this case. The discrepancy arises because BCB's ground truth label is likely incorrect for this pair.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB label of 1 may be an annotation error or due to a very loose interpretation of partial functionality (e.g., both methods perform some kind of 'setup' operation). However, the functional semantics are entirely disjoint.
- 行为差异: Function A is a simple UI button creation with clipboard operation, while B is a complex launch configuration with file I/O and project management.；A has no parameters; B takes configuration, mode, launch, and monitor parameters.；A involves SWT GUI components; B involves Eclipse workspace resources, XML parsing, and property handling.；The token Jaccard similarity is very low (0.0225), indicating almost no textual overlap.
- 修正建议: Review BCB annotation for correctness; consider removing this pair or re-annotating as non-clone.

### case_id=4773 FP boilerplate_overlap

- 方法: `hashStringMD5` vs `perform`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Computes MD5 hash of input string and returns hexadecimal representation.
- B 摘要: Processes a classification request in a Struts web application, validating session, updating beans, and communicating with a classify service.
- 静态失败原因: Static BERT models may overemphasize common boilerplate patterns (e.g., StringBuffer, loops) and miss the semantic gap due to lack of understanding of overall program intent.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB correctly labels as non-clone because the functions serve entirely different purposes with no shared functionality beyond generic coding patterns.
- 共享行为: Both use StringBuffer for string construction；Both contain loops that iterate over arrays；Both handle exceptions
- 行为差异: Function A is a simple utility for hashing; Function B is a complex web request handler with session and HTTP communication；Different inputs and outputs: A (String -> String), B (ActionMapping, ActionForm, etc. -> ActionForward)；Function B involves multiple conditional branches and external service calls; A is deterministic
- 修正建议: Incorporate method name embeddings and high-level API usage to infer intent；Use graph-based representations capturing control and data flow to distinguish utility from complex workflow；Add attention to external library calls (e.g., MessageDigest vs. ActionForward) to highlight different domains

### case_id=4774 FN lexical_or_api_overlap

- 方法: `addIDs` vs `File2String`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Extracts metabolite IDs and scores from a remote database by parsing HTML and updates a PeakListRow object.
- B 摘要: Reads a file from filesystem or classpath and returns its content as a string.
- 静态失败原因: The static model correctly identified the low token similarity (Jaccard 0.158) and distinct control flow patterns, thus predicting non-clone. The model did not fail; the BCB label is inconsistent with semantic analysis.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may have labeled these as clones due to superficial similarities: both use BufferedReader, InputStream, URL handling, and appear to read data line by line. In BigCloneBench, Type-4 clones can be functionally similar, but here the functionality is entirely different. This is likely a mislabel.
- 共享行为: Both use BufferedReader to read text line by line.；Both include try-catch blocks for IOException.；Both return a value (int vs String).
- 行为差异: Function A performs web scraping and HTML parsing; Function B reads a local file.；Function A sets variables on an external PeakListRow object; Function B simply returns the file content.；Function A has complex conditional logic for parsing metabolite IDs; Function B has straightforward concatenation.；Function A returns an integer score; Function B returns a String.
- 修正建议: Ignore this pair as a false positive in BCB; it is not a valid clone.；Improve static models to leverage deeper semantic understanding beyond I/O pattern overlap.

### case_id=4775 FN partial_functionality

- 方法: `copyFileTo` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Copies a file from source path to destination path using byte streams.
- B 摘要: Launches a NexOpen project configuration, including a sub-step that copies a resource file from a bundle to the project.
- 静态失败原因: Static BERT/GraphCodeBERT models rely on token or AST overlap; the low Jaccard similarity (0.051) caused the model to miss the partial functional similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider these clones due to the shared behavior of copying stream data, treating the copy subfunction as a semantic clone even though overall methods differ in purpose.
- 共享行为: Both perform a stream copy of binary data from an input source to an output destination.
- 行为差异: Function A is solely a file copy; Function B is a complex launch method with many additional steps.；Function B's copy step is a small part and uses IOUtils.copy, while Function A uses a manual read/write loop.；Function B writes to a ByteArrayOutputStream and then creates a file from the bytes; Function A writes directly to a FileOutputStream.
- 修正建议: Enhance model with subgraph matching or program slicing to detect shared behavior even in large methods.；Use contrastive learning to focus on functional semantics rather than lexical overlap.

### case_id=4776 FN boilerplate_overlap

- 方法: `addIDs` vs `issueCommandToServer`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches metabolite data from a remote service by name, parses HTML to extract IDs and scores, and sets multiple properties on a PeakListRow.
- B 摘要: Sends a command and a JSON capsule to a server via HTTP POST, reads the response, and returns it as a string.
- 静态失败原因: Static models like GraphCodeBERT rely on token overlap and structural patterns. Despite low token Jaccard, the model may have been confused by shared API tokens (URL, BufferedReader, IOException) and the general structure of try-catch with I/O, overlooking the entirely different core algorithms.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may consider both as 'web service client' tasks, focusing on the shared pattern of making HTTP requests and handling I/O, thus labeling them as Type-4 (partial functional similarity).
- 共享行为: Both establish HTTP connections using URL/URLConnection.；Both read from a BufferedReader to handle server responses.；Both catch IOException and return a value (int or String).
- 行为差异: A parses HTML to extract specific data (metabolite IDs, molecular weight, scores) and populates multiple fields; B simply returns the raw response string.；A involves complex conditional logic for different ID types (ChEBI, KEGG, etc.); B has a straightforward request-response pattern.；A writes to an OutputStream (implied by URL.openStream for reading) but does not send any data; B explicitly writes a command and capsule to an OutputStream.
- 修正建议: Incorporate more semantic analysis focusing on the main task logic rather than I/O boilerplate.；Use domain-specific features (e.g., presence of HTML parsing, conditional data extraction) to distinguish.；Add training data with more diverse functional patterns to avoid overgeneralizing from shared API usage.

### case_id=4777 FN benchmark_preference_bias

- 方法: `doGet` vs `gerarTutorialPage`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `preference_memory_with_manual_audit`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Handles HTTP GET request to retrieve and render a portal page, with logging and caching.
- B 摘要: Generates a static tutorial website by creating directories and copying CSS files, then writing HTML pages.
- 静态失败原因: Static BERT methods rely on token overlap and structural similarity; low Jaccard (0.0789) and different API usage (servlet vs file I/O) led to non-clone prediction, missing the broad semantic link.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may accept broad semantic similarity: both methods are considered 'page generation' despite different contexts and implementations, fitting Type-4 (semantic) clone criteria.
- 共享行为: Both involve creating or serving a web page；Both use file-like output (response output stream vs file writing)；Both have error handling with logging or user messages
- 行为差异: A is an HTTP servlet handler; B is a standalone method generating files；A retrieves dynamic page content; B creates static site from templates；A contains caching logic; B does not；B creates directory structure and copies files; A does not
- 修正建议: Train with more diverse examples of Type-4/semantic clones；Incorporate higher-level semantic understanding of domain (e.g., web page generation)；Use cross-context matching based on method purpose rather than exact tokens

### case_id=4778 FP long_range_semantics

- 方法: `readData` vs `copyLogic`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `static_summary_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Reads and parses multiple string token lists and a configuration file to populate various data structures for Tibetan character processing.
- B 摘要: Copies a .class file from one location to another using FileChannel, while managing state transitions.
- 静态失败原因: Given the low token Jaccard, it is surprising that the model predicted clone. Possibly the model was misled by common structural patterns like try-catch blocks around file I/O, or the model may have been trained on data where such patterns indicate clone. The truncation of code_a may also have caused the model to see only a portion that resembles file I/O, but overall, the false positive likely stems from a bias towards common I/O patterns and long-range semantics.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB would consider these non-clones because they have no functional similarity; one is a data loading routine while the other is a file copy utility.
- 共享行为: Both involve file I/O operations；Both catch IOException
- 行为差异: A is a complex data initialization routine parsing many token lists and a config file; B is a simple file copy with state management；A populates sets and hashes; B transfers bytes between channels；A has extensive error handling with custom throw statements; B prints stack traces；A is much longer and more complex than B
- 修正建议: Improve understanding of the overall function purpose rather than local patterns；Use better tokenization to capture long-range dependencies；Consider control flow and data flow analysis to distinguish similar I/O operations

### case_id=4779 FP boilerplate_overlap

- 方法: `doVersionCheck` vs `run`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Checks for a newer version of jEdit by reading a version file from a URL and comparing build numbers.
- B 摘要: Loads a tile from a data source by reading a URL (file or HTTP), constructs geometry, and adds it to a data loader.
- 静态失败原因: Static BERT overfocused on the common I/O pattern (URL opening, BufferedReader, while loop) and ignored the surrounding context that defines distinct functionality.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would likely label these as non-clones because they perform entirely different high-level tasks, despite sharing some low-level I/O boilerplate.
- 共享行为: Both open a URL and read its contents line by line；Both handle IOExceptions
- 行为差异: Different URL sources and protocols；Different parsing logic (version fields vs plain text concatenation)；Different post-processing (version comparison vs geometry construction)
- 修正建议: Enhance the model to capture task-level semantics beyond local code patterns；Incorporate data flow or control flow graphs to distinguish different algorithms

### case_id=4780 FN partial_functionality

- 方法: `copyResource` vs `convert`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource (URL or file) to a destination file byte by byte.
- B 摘要: Converts a DICOM file by parsing, validating, and writing pixel data with optional inflation.
- 静态失败原因: Static model correctly identified low lexical similarity and different method names/parameters, but BCB overrides with a broad Type-4 clone definition that is not captured by the model.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label as clone due to broad interpretation of 'copying data from input to output', considering both as data transfer operations despite vastly different domain logic.
- 共享行为: Both read from an input source and write to an output file.；Both use InputStream and OutputStream.；Both close streams after use.
- 行为差异: A handles URL or file paths; B only local files.；A copies all bytes; B parses DICOM structure, checks UIDs, handles pixel data and inflation.；B performs complex data validation and transformation; A is a simple byte copy.；B writes additional metadata and pixel data in a specific format; A writes raw bytes.
- 修正建议: Incorporate more fine-grained structural and semantic similarity metrics.；Adjust threshold for Type-4 clone acceptance based on domain knowledge.；Use dataflow analysis to capture shared I/O behavior while ignoring internal transformations.

### case_id=4781 FP boilerplate_overlap

- 方法: `main` vs `init`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Main method that parses a Prolog file and generates an adapter JAR using a class writer and assembler.
- B 摘要: Init method that sets up a report file, handles restarting from a backup, and resumes processing XML documents from a previous run.
- 静态失败原因: Static BERT/GraphCodeBERT likely overemphasized lexical and API overlaps (e.g., File, IOException, try-catch, FileOutputStream) and structural patterns (loops, conditional checks) while missing the distinct semantic contexts and domain-specific operations.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clone because the functions have completely different purposes and domain logic; shared boilerplate patterns do not constitute functional similarity.
- 共享行为: Both functions perform file existence checks and file I/O operations with error handling.；Both use try-catch blocks for IOException and other exceptions.；Both involve reading from or writing to files using streams.
- 行为差异: Function A is a command-line entry point for generating adapters from Prolog; Function B initializes a batch processing report system.；Function A parses Prolog code and generates Java bytecode; Function B reads XML events and writes XML output.；Function A handles JAR file assembly; Function B manages backup files and restart logic.；Function A uses PrologParser, FactVisitor, and ClassWriter; Function B uses StAX XMLStreamWriter and XMLEventReader.
- 修正建议: Incorporate data flow analysis to track how variables are used across the function.；Use control flow graph or abstract syntax tree structural matching to differentiate generic boilerplate from core logic.；Train on more diverse examples to discourage reliance on common Java idioms.；Add attention to method names and comments for semantic cues.

### case_id=4782 FP boilerplate_overlap

- 方法: `wordFrequency` vs `loadURL`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Retrieves word frequency from a web query by replacing a placeholder and parsing lines matching a pattern.
- B 摘要: Downloads a URL's content to a temporary file with optional authentication and updates a status label with progress.
- 静态失败原因: Focused on overlapping lexical items (URL, BufferedReader, readLine) and common structural patterns, missing the divergent functional intents and data flows.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled non-clone because the core functionality (frequency extraction vs. file download) is completely different despite shared URL-reading boilerplate.
- 共享行为: Open a URL connection and read input line by line using BufferedReader
- 行为差异: A returns an integer frequency; B writes to a file and updates UI；A uses pattern matching to find specific lines; B writes all lines；A handles errors with return 0; B throws IOException；B implements HTTP Basic authentication; A does not
- 修正建议: Incorporate control-flow and data-flow analysis to differentiate side effects and return values；Use AST-based differencing to isolate unique logic outside common boilerplate；Increase weight on method signatures and external behavior

### case_id=4783 FN partial_functionality

- 方法: `getURLContent` vs `seeURLConnection`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads the content of a given URL and returns it as a string, appending newlines.
- B 摘要: Reads content from a hardcoded URL and logs the result without returning.
- 静态失败原因: Static BERT/GraphCodeBERT likely focused on syntactic differences like method signature, return type, and literal values, missing the semantic similarity due to differing method names and output behavior.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB considers these clones because they perform the same essential task (retrieving URL content via HTTP) with only minor variations in parameterization and output handling, which is typical for Type-3/4 clones.
- 共享行为: Open a URL connection；Read content line by line using BufferedReader；Append lines to a StringBuffer/StringBuilder
- 行为差异: A takes a URL string parameter; B uses a hardcoded URL；A returns the content; B logs it and returns void；A appends a newline after each line; B does not
- 修正建议: Train models on more diverse Type-3/4 examples to recognize functional similarity despite syntactic variations.；Incorporate data-flow analysis to capture behavior beyond token overlap.；Use code summarization or contrastive learning to align embeddings based on purpose.

### case_id=4784 FN benchmark_preference_bias

- 方法: `getFile` vs `copyToDir`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `preference_memory_with_manual_audit`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies its endpoint attribute, saves it to a temporary directory, and returns the file path.
- B 摘要: Copies a file to a specified directory, creating the directory if needed, and updates the internal file reference.
- 静态失败原因: The static BERT model correctly detected non-clone based on strict semantics and low token overlap (0.1397), but BCB's annotation is lenient, so the model 'failed' to match the benchmark's preference for broad Type-4 clones.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may label this as a clone (Type-4) because both functions perform file I/O operations that read from an input source and write to an output file, and BCB's annotation preference sometimes accepts broad functional similarity in file manipulation tasks.
- 共享行为: Both create new files and write data using FileOutputStream；Both involve closing streams (InputStream, OutputStream)；Both handle IOException
- 行为差异: A downloads from a network URL; B copies from a local file；A parses and modifies XML; B uses byte buffer for copying；A uses NIO channels; B uses traditional byte array；A returns a String; B is void and updates an instance field
- 修正建议: Train with more Type-4 clone examples that share partial functionality；Incorporate features like file I/O operations to capture broader similarity；Adjust threshold or use ensemble methods to align with BCB's labeling criteria

### case_id=4785 FN benchmark_preference_bias

- 方法: `saveFile` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Serializes UI window and tool settings into an XML configuration file with a specific DTD.
- B 摘要: Generates HTML pages for editing a site by processing page definitions, applying XSLT transformations, and performing string replacements.
- 静态失败原因: The model correctly identified the semantic dissimilarity, but BCB's annotation may be biased towards broad structural patterns like file output loops, causing a false negative relative to the benchmark label.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have considered both as 'file generation with XML' tasks, overlooking the entirely different application domains and data transformations.
- 共享行为: Both write output to files.；Both use XML-related libraries (JDOM vs. XSLT/Transformer).；Both iterate over collections (internal frames vs. pages).；Both handle IO exceptions.
- 行为差异: A writes a single configuration file; B writes multiple HTML page files.；A serializes UI state; B transforms site content.；A uses JDOM for direct XML creation; B uses XSLT transformations.；A's data source is runtime UI components; B's is a static site model.
- 修正建议: Incorporate task-level context (e.g., method purpose) beyond local tokens.；Use additional features like method name embeddings or API call patterns.；Align with explicit BCB guidelines to reduce annotation ambiguity.

### case_id=4786 FN partial_functionality

- 方法: `copyFile` vs `copyResource`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a file to another using FileChannel transferTo, returns boolean success flag.
- B 摘要: Copies a resource (URL or file) to a destination file using byte-by-byte stream copy, throws exceptions.
- 静态失败原因: Low token overlap (0.107) and different API usage (FileChannel vs streams) caused the model to miss the functional similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often considers broad Type-4 functional similarity: both methods achieve file copying, regardless of I/O API or error handling differences.
- 共享行为: Both copy data from a source to a destination file.
- 行为差异: A uses NIO FileChannel.transferTo; B uses InputStream/OutputStream with a read-write loop.；A returns boolean and silently catches exceptions; B is void and throws exceptions.；A only handles File sources; B handles both URLs and local files.
- 修正建议: Incorporate dataflow analysis to recognize common data transformation patterns.；Use high-level API semantics (e.g., 'copy' operation) rather than low-level syntax.；Consider that exception-handling differences may be considered minor in clone detection.

### case_id=4787 FN benchmark_preference_bias

- 方法: `main` vs `testReadHelloWorldTxt`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads and extracts a KMZ zip file from a URL to local files.
- B 摘要: Tests a content resolver by copying a resource file to a temp directory and verifying retrieval of its content via various path formats.
- 静态失败原因: Static BERT (or GraphCodeBERT) likely correctly identified them as non-clones due to low token overlap and different control flow; however, BCB labeled them as clones, so the model's prediction is considered incorrect against the benchmark.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have considered them clones due to both performing file read/write operations and using standard Java I/O classes, but the actual tasks are completely different; BCB's broad criteria for Type-3/Type-4 clones might overgeneralize common I/O boilerplate.
- 行为差异: Function A downloads and extracts a zip archive; Function B copies a resource and tests a content resolver.；Function A uses ZipInputStream and writes multiple entries; Function B uses IOUtils.copy and asserts content.；Function A works with network streams; Function B works with classpath resources and local files.
- 修正建议: Use more precise cloning criteria to avoid overgeneralization of common I/O patterns.；Incorporate functional semantics beyond lexical and syntactic similarity.

### case_id=4788 FN partial_functionality

- 方法: `runInternal` vs `getNetworkServersIPs`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: This function creates an HTTP connection to download and parse an OPDS catalog XML, handling pagination and possibly downloading books.
- B 摘要: This function opens a URL connection to read a text file and extracts server IPs after a '!SERVERS' marker.
- 静态失败原因: Static BERT/GraphCodeBERT models rely on code structure and token sequences. They likely detected significant differences in control flow (e.g., do-while vs while loops, XML parsing vs line splitting), API usage (HttpURLConnection with many settings vs simple URLConnection), and output types (void with callback vs returning Vector). These differences overshadow the superficial connection-opening boilerplate, leading to a non-clone prediction.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled this as a clone (Type-4) because both functions perform network I/O to retrieve data from a URL and parse the response into structured data. Despite different specific protocols (HTTP vs generic URL), both share a high-level pattern of connecting, reading, and parsing. BCB's annotation guidelines sometimes accept broad functional similarity.
- 共享行为: Both open a URLConnection to fetch data from a network resource.
- 行为差异: Function A handles HTTP-specific features like redirects, cookies, and content types; B does not.；Function A parses XML (OPDS) with SAX handler; B parses plain text line by line.；Function A has complex pagination logic; B has simple state machine for server lines.；Function A can download files; B only returns a Vector of IP strings.
- 修正建议: Improve model's ability to recognize partial functional similarity by augmenting training with Type-3/Type-4 clones that share only network I/O patterns.；Incorporate task-level features like 'reads from URL' or 'parses response' into the representation.；Use contrastive learning to emphasize shared sub-patterns while tolerating differences in details.

### case_id=4789 FP boilerplate_overlap

- 方法: `main` vs `convert`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Parses command line arguments, reads a Prolog file, generates adapter classes, and writes them to a JAR file.
- B 摘要: Converts an ACRNEMA medical image file to DICOM format, handling pixel data and metadata.
- 静态失败原因: Static model likely focused on common boilerplate tokens (e.g., 'if', 'try', 'File', 'System.out.println') and ignored domain-specific context, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB correctly labeled non-clone due to vastly different functionalities and low token overlap (Jaccard=0.08871), despite some boilerplate similarity.
- 共享行为: Both perform file I/O operations；Both print diagnostic messages to System.out；Both use try-catch-finally for error handling
- 行为差异: Different input/output formats and domains；Completely different core logic and data processing；Function A generates code; Function B transforms image data
- 修正建议: Incorporate dataflow or API-call analysis to capture domain-specific operations；Increase training data diversity to reduce sensitivity to boilerplate；Use structural differencing to highlight unique control flow patterns

### case_id=4790 FP lexical_or_api_overlap

- 方法: `readZoneIDs` vs `issueCommandToServer`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a set of integers from a resource file using URL and LineNumberReader.
- B 摘要: Sends an HTTP POST command to a server with a JSON payload and returns the response string.
- 静态失败原因: The static BERT/GraphCodeBERT model likely over-focused on common I/O-related tokens like 'URL', 'BufferedReader', 'InputStreamReader', and 'readLine', ignoring the distinct overall semantics. The low token Jaccard (0.108) suggests minimal overlap, but the model may have been misled by the presence of these API calls in both functions.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would label these as non-clones because they perform entirely different functionalities: one is a file parsing utility, the other is a network communication method. The shared use of I/O classes is superficial and not indicative of functional equivalence.
- 共享行为: Both use URL/URLConnection to read data from a remote or local source.
- 行为差异: A reads integers from a file; B sends a command and reads a string response.；A writes nothing; B writes HTTP request content.；A returns HashSet<Integer>; B returns String.；A catches exceptions and prints stack trace; B throws IOException.
- 修正建议: Include more negative training examples with lexical overlaps but different semantics.；Utilize graph-based representations that capture data flow and control flow to better distinguish I/O patterns.；Incorporate task-specific heuristics (e.g., file reading vs. network communication) as features.

### case_id=4791 FN partial_functionality

- 方法: `callService` vs `File2String`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads from a URL and stores the content into an instance field, with error handling that sets error messages.
- B 摘要: Reads from a file or classpath resource and returns the content as a string, exiting on critical errors.
- 静态失败原因: Static BERT models rely on token-level similarity and syntactic structure; the low Jaccard similarity (0.29) combined with different APIs (URL vs File) and error handling code result in low embedding similarity, missing the high-level semantic equivalence.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely labels this as a clone because both methods implement the same algorithmic pattern of reading all lines from a text input stream into a string, which is considered a broad Type-3/Type-4 clone despite syntactic differences in input source and error handling.
- 共享行为: Open a text stream；Read lines using BufferedReader；Concatenate all lines into a StringBuffer；Close the stream
- 行为差异: Source: A uses URL (based on instance variables), B uses file or classpath resource；Return: A sets a field (void), B returns the string；Error handling: A sets error message and returns, B prints and calls System.exit；A fails silently with error string, B terminates program on failure
- 修正建议: Use graph-based models that capture data flow and control flow；Incorporate program slicing focusing on I/O operations；Augment training data with more diverse API usage for same semantic behavior

### case_id=4792 FP partial_functionality

- 方法: `getPagina` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Retrieves the entire HTML content of a given URL as a string, with authentication and exception handling.
- B 摘要: Searches Google Images for a specific artist and album, extracts image URLs from the response, and adds them to a list.
- 静态失败原因: Static BERT may have focused on the lexical overlap of URL opening and line reading, ignoring the distinct surrounding logic and domain-specific processing, leading to a false positive.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely labels this non-clone because the functions have different purposes and overall structure; the common URL-reading portion is a small, generic pattern that does not constitute significant functional similarity.
- 共享行为: Both open a URL and read lines from the input stream.
- 行为差异: Function A returns the raw HTML as a string; function B returns void and populates a list.；Function A sets an Authenticator; function B sets a User-Agent header.；Function B performs complex parsing to extract image URLs; function A does not parse.；Exception handling differs: A returns error string, B shows a dialog.
- 修正建议: Improve model ability to distinguish generic utility functions from domain-specific ones.；Incorporate functional context such as return types, side effects, and overall algorithm structure.；Augment training data with non-clones that share lexical patterns but differ in functionality.

### case_id=4793 FP lexical_or_api_overlap

- 方法: `doVersionCheck` vs `downloadModel`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Checks for new jEdit version by reading version/build from a URL and comparing build numbers.
- B 摘要: Downloads an RDF model from a URL by opening a connection, setting HTTP headers, and reading into a Model object.
- 静态失败原因: Static model likely overemphasized common API tokens (URL, InputStream, IOException) and missed the different overall logic and intent.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clone because the functions have distinct high-level functionality and low token overlap (0.19), despite both using URL/InputStream.
- 共享行为: Both open a URL and read an InputStream；Both handle IOException
- 行为差异: Different input parameters: View vs URL string；Different outputs: void vs Model；Different exception handling: error message vs RuntimeException；Different purpose: version checking vs model download
- 修正建议: Incorporate control flow or data flow analysis；Use semantic embeddings that capture method purpose

### case_id=4794 FN benchmark_preference_bias

- 方法: `main` vs `convert`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.1`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a URL and extracts its zip entries to local files.
- B 摘要: Converts an ACRNEMA stream to DICOM format, handling pixel data and metadata.
- 静态失败原因: Static BERT correctly predicted non-clone based on low token Jaccard similarity (0.152) and distinct API usage; it did not fail.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB label likely erroneous; there is no meaningful functional similarity. It may have been annotated due to superficial overlap in I/O patterns or boilerplate exception handling, but that is too weak for Type-3/4 clone.
- 共享行为: Both read from input streams and write to output streams.
- 行为差异: Code A extracts zip entries from a remote URL; Code B parses medical imaging data and writes DICOM with pixel data transformation.；Code A involves file I/O and zip extraction; Code B involves DICOM parsing and metadata manipulation.；Code A is a main method with hardcoded URL; Code B is a method with parameters for source and destination files.
- 修正建议: Review and correct BCB annotation for this pair.；Ensure clone detection model uses semantic understanding beyond lexical overlap.

### case_id=4795 FP lexical_or_api_overlap

- 方法: `readData` vs `main`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Parses configuration strings and a file to populate multiple HashSets and maps for Tibetan character processing.
- B 摘要: Reads .meta and .extra files for each jar in a directory and writes their license information to an output file.
- 静态失败原因: The model may have over-relied on superficial similarities such as use of File I/O, StringTokenizer, or HashSet, and the truncated code might have misled the model into thinking the structures are similar.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels these as non-clones because they have completely different domains and purposes, despite both using I/O.
- 共享行为: Both functions perform file I/O and use data structures like HashSet and Map.
- 行为差异: Function A processes Tibetan character sets and maps; Function B processes library license metadata.；Function A reads from static strings and a file; Function B reads from .meta and .extra files.；Function A builds complex internal data structures; Function B writes a text file with license info.
- 修正建议: Train with more diverse negative examples to reduce false positives from shared APIs.；Incorporate structural or semantic features that capture the overall purpose, not just local patterns.

### case_id=4796 FP lexical_or_api_overlap

- 方法: `readTwitterFead` vs `load`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.85`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches a Twitter JSON timeline from a fixed URL using Apache HttpClient and returns the response as a string.
- B 摘要: Fetches an XML document from a Pastebin URL constructed from an input ID using java.net URL and returns the content as a string.
- 静态失败原因: Static BERT models likely overemphasized the common structural pattern (try-catch, BufferedReader loop) and common tokens (reader, line, append, IOException) while ignoring the fundamental differences in HTTP client libraries and URL semantics.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled non-clone because the methods have different functionality (Twitter feed vs Pastebin content) and different API usage, exceeding the typical Type-3/Type-4 similarity accepted only for structurally similar implementations with the same purpose.
- 共享行为: Both perform an HTTP GET request；Both read the response line by line using BufferedReader；Both return the concatenated response as a String
- 行为差异: Different HTTP libraries (Apache HttpClient vs java.net URL)；Different target URLs (fixed vs parameterized)；Different error handling (logging vs dialog)；Code B has a guard clause on input length and uses a 'working' flag
- 修正建议: Include dataflow analysis to differentiate between different HTTP libraries；Add token-level embeddings that capture domain-specific vocabulary (e.g., 'httpget', 'pastebin')；Incorporate method-level context like input/output types and external calls

### case_id=4797 FN partial_functionality

- 方法: `copyResource` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource (URL or file) to a destination file using byte-by-byte stream reading.
- B 摘要: Copies a file to another file using NIO FileChannel transfer.
- 静态失败原因: Low token-level similarity (Jaccard 0.17) due to different API calls (FileChannel vs InputStream/OutputStream) and method signatures; the model likely focused on surface form rather than abstract behavior of copying data.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels pairs as clones if they share similar high-level functionality (copying data from input to output) despite different APIs and parameter types, treating them as Type-3 or Type-4 clones.
- 共享行为: Both copy content from a source to a destination file；Both create and close output streams/channels；Both read from an input source and write to an output file
- 行为差异: A supports URL sources, B only accepts File objects；A reads byte-by-byte with InputStream, B uses FileChannel.transferTo for bulk transfer；A throws generic Exception, B throws IOException；A uses instance variables (source, destinationFile()), B uses explicit parameters
- 修正建议: Increase training data with diverse APIs performing the same core operation；Incorporate dataflow or program graph representations to capture semantics；Use code summarization or high-level intent classification

### case_id=4798 FP lexical_or_api_overlap

- 方法: `googleImageSearch` vs `doVersionCheck`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Performs a Google image search by fetching HTML, parsing image URLs, and displaying the first image.
- B 摘要: Checks for software version updates by fetching a version file, parsing build numbers, and performing version check.
- 静态失败原因: The static model likely relied on syntactic and API-level similarities (e.g., URL, BufferedReader, while loop) and missed the semantic differences due to limited context understanding or overemphasis on common patterns.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled this as non-clone because despite shared boilerplate, the core functionality (image search vs. version check) is entirely different, and the overall program logic is distinct.
- 共享行为: Both open a URL connection and read lines from an input stream.；Both handle exceptions with try-catch blocks.；Both use BufferedReader to read line by line.；Both perform some parsing of the fetched content.
- 行为差异: Function A parses image URLs from HTML; Function B parses version build numbers.；Function A interacts with UI components (setting an icon); Function B shows/hides wait cursor and calls another method.；Function A uses HttpURLConnection with User-Agent; Function B uses URL.openStream().；Different error handling: A shows error dialog, B shows error via GUIUtilities.error.
- 修正建议: Incorporate better understanding of data flow and function purpose.；Use more fine-grained representation that captures domain-specific semantics.；Include additional context like method names or broader program analysis.

### case_id=4799 FN partial_functionality

- 方法: `doRawRequest` vs `register`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends HTTP POST data to a fixed service URL and returns the response body as a string.
- B 摘要: Registers a user by validating input, encoding password, setting metadata, creating a forum user via HTTP request, persisting to database, and sending confirmation email.
- 静态失败原因: The static model primarily relies on surface-level lexical and structural features. The low token Jaccard (0.14) and different method names/control flow likely caused the model to treat them as non-clones. The model failed to recognize the partial functional overlap in the HTTP request-response pattern due to lack of semantic decomposition.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: Both functions perform an HTTP request and read the response, which BCB considers a core functional similarity. Despite differing contexts and additional logic, the shared sub-behavior of making a URL connection and processing input line-by-line leads BCB to label them as Type-4 clones.
- 共享行为: Open a URL connection to an external service；Read response from the input stream line by line until null；Close the reader
- 行为差异: A writes POST data to the output stream; B does not write to the connection；B includes extensive user registration logic (validation, password encoding, base64 hash, logging, exception handling)；B persists user entity to database and handles multiple exception types；B returns boolean based on email result; A returns entire response string
- 修正建议: Incorporate AST-based or graph-based representations that capture data flow and control flow subgraphs (e.g., identifying common I/O patterns).；Use contrastive learning with partial behavioral similarity to recognize when a sub-task of one function matches another's core behavior.；Augment training data with examples of Type-4 clones where only a subset of functionality overlaps.

### case_id=4800 FN partial_functionality

- 方法: `read` vs `addIDs`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a camera log from a URL, parses each line into CameraLogRecord objects, adds them to a list, and sorts the list.
- B 摘要: Queries the GMD metabolite database by name, parses the HTML response to extract metabolite IDs and metadata, and sets various properties on a PeakListRow object.
- 静态失败原因: The model likely relied on lexical and structural similarities, which are low (token Jaccard 0.15). The functions share only generic I/O boilerplate and differ significantly in domain-specific logic and output. However, BCB's broader notion of semantic equivalence accepts this as a partial clone, which the model missed.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider them Type-4 clones because both involve fetching data from a URL and parsing it into structured objects, albeit with different schemas. The broader task of 'read web resource and parse into model objects' could be seen as functionally similar at a high level.
- 共享行为: Both read data from a URL using BufferedReader and InputStreamReader.；Both parse data line by line.；Both handle IOExceptions and close the reader in a finally block.；Both use logging for traceability.
- 行为差异: Function A is a simple log reader; function B is a complex web scraper with conditional HTML parsing.；Function A outputs a sorted list of CameraLogRecord objects; function B returns an integer score and mutates a PeakListRow object.；Function A has no parameters (reads from instance variable URL); function B takes a row and a name as parameters.；Function B has far more conditional branches and data extraction logic.
- 修正建议: Incorporate global-context embeddings or program flow analysis to capture high-level intent.；Use data-flow-sensitive representations to understand that both functions ultimately transform web data into internal objects.；Train with more examples of Type-3/Type-4 clones that share only abstract patterns.

### case_id=4801 FP boilerplate_overlap

- 方法: `doRawRequest` vs `downloadModel`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Sends a POST request with given data and returns the response as a string.
- B 摘要: Downloads an RDF model from a URL and returns the model object.
- 静态失败原因: The static BERT model likely over-relied on surface-level similarities like 'URL', 'URLConnection', 'InputStream', and the common pattern of opening a connection and reading, ignoring the different I/O direction and distinct return types and method purposes.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely considers these not clones because they perform different high-level tasks (sending POST data vs. downloading a model) despite sharing some HTTP boilerplate.
- 共享行为: Both open a URLConnection.；Both handle input streams (InputStream/Reader).；Both use try-catch for IOException (implicitly or explicitly).
- 行为差异: A writes to an output stream (POST), B only reads (GET).；A returns a String, B returns a Model object.；A sets doOutput and uses OutputStreamWriter; B sets request properties and reads model directly.；A throws IOException, B catches and wraps in RuntimeException.
- 修正建议: Incorporate dataflow analysis to distinguish write-then-read vs. read-only patterns.；Add function name and return type features to capture semantic intent.；Use deeper semantic models that understand method purpose beyond token overlap.

### case_id=4802 FP boilerplate_overlap

- 方法: `postXml` vs `downloadModel`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Sends an XML POST request to a URL with SOAP action and returns the response body as a string.
- B 摘要: Downloads an RDF model from a URL using GET and returns a Model object.
- 静态失败原因: The static model likely overemphasized lexical overlap (e.g., URLConnection, HttpURLConnection, setRequestProperty, IOException, RuntimeException) and structural similarity (try-catch, connection open, error handling), missing the semantic difference in HTTP method and data flow (output stream vs. model reading).
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the core functionality differs significantly: one is a SOAP XML client, the other is an RDF model downloader. Despite shared URL connection boilerplate, the methods have distinct purposes and data processing.
- 共享行为: Open a URL connection and cast to HttpURLConnection if applicable；Set request headers (Content-Type, Accept, etc.)；Read input stream and handle IO exceptions；Wrap exceptions in RuntimeException
- 行为差异: A uses POST method; B uses default GET；A writes XML to output stream; B only reads input stream；A returns response string; B returns RDF Model object；A sets connection/read timeouts; B does not
- 修正建议: Incorporate data flow analysis to detect presence of output stream writing vs. only input reading；Consider HTTP method (GET vs POST) and content type as distinguishing features；Use AST-based differencing to highlight structural differences in try-catch blocks and variable usage

### case_id=4803 FP boilerplate_overlap

- 方法: `load` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Downloads and returns the raw text content from a Pastebin URL.
- B 摘要: Searches Google Images for a music artist/album and extracts image URLs.
- 静态失败原因: The static model over-relied on lexical and API overlap (URL, BufferedReader, while readLine concatenation) and missed the distinct control flow and domain-specific logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels them non-clones because they perform fundamentally different tasks despite sharing boilerplate I/O code. The high-level semantics (pastebin retrieval vs image search) are not equivalent.
- 共享行为: Both open a URL connection and read lines from an input stream.；Both concatenate lines into a single string using a while loop.
- 行为差异: Different URL construction and purpose (pastebin download vs google image search).；Different data processing: function a returns raw text, function b parses HTML to extract image URLs.；Different error handling: JOptionPane dialog vs custom error dialog.；Different method signatures (static vs void, return type).
- 修正建议: Incorporate data-flow analysis to distinguish different URL construction and downstream data usage.；Train on a more diverse set of functions that share boilerplate but differ in purpose.；Use graph-based models that capture structural differences in control and data dependencies.

### case_id=4804 FP boilerplate_overlap

- 方法: `handleHandshake` vs `importRoles`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Handles Minecraft client handshake by validating username and authenticating with session server.
- B 摘要: Imports roles by parsing an XML-like response from a URL.
- 静态失败原因: The model likely focused on the common URL-reading pattern and exception handling, ignoring the distinct high-level semantics and logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would not consider them clones because they solve different problems; the shared API usage is incidental boilerplate.
- 共享行为: Both open a URL and read from it using BufferedReader；Both use try-catch for exception handling
- 行为差异: A validates username and performs server authentication, B parses XML tags and collects RoleName objects；A has side effects like sending packets and network shutdown, B returns a list；Different input parameters and output types
- 修正建议: Incorporate data flow and control flow analysis to distinguish core functionality from boilerplate；Use domain-specific features or fine-tune on more diverse examples to avoid over-reliance on API calls

### case_id=4805 FP lexical_or_api_overlap

- 方法: `handleHandshake` vs `handledRun`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Handles Minecraft client handshake by validating server key and optionally authenticating via session server.
- B 摘要: Downloads and updates game data from a URL if local version is outdated.
- 静态失败原因: The static model likely over-relied on lexical and API-level similarities (URL, BufferedReader, etc.) and the presence of exception handling structures, ignoring the distinct business logic and purpose of each function.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled these as non-clones because they perform completely different high-level tasks: one is handshake/authentication, the other is data update. The shared I/O boilerplate is insufficient for functional similarity.
- 共享行为: Both open a URL and read from it using BufferedReader/InputStreamReader.；Both have try-catch blocks for exceptions.；Both involve network I/O operations.
- 行为差异: Function A performs authentication and login, while function B updates game data.；Function A uses a web service endpoint, function B downloads an XML file.；Function A writes to network queue, function B writes to local file.；Function A has complex conditional logic based on handshake parameters, function B compares versions and conditionally downloads.
- 修正建议: Incorporate control-flow and data-flow analysis to differentiate distinct logic paths.；Use graph-based representations that capture program dependence and domain context.；Train with more diverse negative samples that have similar API usage but different functionality.

### case_id=4806 FP boilerplate_overlap

- 方法: `main` vs `addFileToTarGz`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Main method that parses a Prolog file, generates adapter classes, and writes them into a JAR file.
- B 摘要: Private method that adds a file (or recursively adds files) to a TarGz archive.
- 静态失败原因: The model likely over-relied on lexical overlap of common boilerplate tokens (File, IOException, try-catch, System.out.println) and API class names, ignoring the overall algorithmic structure.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clone because the functions have different APIs, logic, and purposes; even broad Type-4 similarity would require some shared functionality, which is absent.
- 共享行为: Both involve file system operations (File, I/O).；Both use exception handling (IOException, try-catch).
- 行为差异: Function A is a command-line entry point with argument parsing; Function B is a utility for archive creation.；Function A performs Prolog parsing and class generation; Function B writes to a TarArchiveOutputStream.；Function A writes to a JAR file; Function B writes to a tar.gz archive.；Function A involves reflection and class loading; Function B does not.
- 修正建议: Incorporate structural analysis (e.g., control flow graphs, data flow) to distinguish different algorithms.；Use code representation that captures high-level intent (e.g., API call sequences, abstract syntax trees).；Add context about function roles (e.g., main vs utility method).

### case_id=4807 FN benchmark_preference_bias

- 方法: `readAndRewrite` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Reads a DICOM image file, parses it, and writes pixel data to an output file.
- B 摘要: Configures and launches a NexOpen project, handling Maven POM files and Hibernate dialect settings.
- 静态失败原因: Static BERT relies on token overlap and structural similarity. With a very low token Jaccard (0.03) and different vocabulary, it correctly identified them as non-clones, but failed to align with BCB's possibly incorrect annotation.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled these as clones due to both being multi-step I/O-intensive operations that read from one source and write to another, but the domains and exact semantics differ significantly. This appears to be a benchmark annotation error or overly broad interpretation.
- 共享行为: Both perform file I/O operations；Both handle exceptions with try-catch or throws；Both use multiple steps with variable assignments
- 行为差异: A operates on DICOM medical images; B operates on Eclipse project configuration.；A uses DICOM-specific libraries; B uses Eclipse and Maven-specific APIs.；A reads and writes binary pixel data; B modifies XML files and project properties.；The overall purpose and output are completely different.
- 修正建议: Re-annotate the BCB label for this pair to 0 (non-clone) if not intended.；Improve training data quality by filtering out semantically unrelated pairs.；Consider using dynamic or context-aware models to recognize functional similarity beyond token overlap.

### case_id=4808 FN partial_functionality

- 方法: `main` vs `getURLContent`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Main method that constructs a POST request to RenRen API with hardcoded parameters and prints the response.
- B 摘要: Utility method that fetches content from a URL and returns it as a string.
- 静态失败原因: Static BERT models rely on token overlap and structural similarity; low Jaccard similarity (0.17) and different method names and parameter lists likely caused the model to miss the shared IO pattern. The model may have been misled by the long, specific parameter construction in A.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider them clones due to the common pattern of reading from a URL connection, which is a distinct subfunctionality, despite differences in the rest.
- 共享行为: Both open a URL connection；Both read lines from the input stream using BufferedReader
- 行为差异: A uses hardcoded parameters for a specific API, B takes a URL string parameter；A uses POST method, B uses default GET；A prints output, B returns StringBuilder；A includes specific RenRen parameter construction, B is generic
- 修正建议: Improve model's ability to detect shared subroutines even when overall structure differs；Use graph-based representations to capture data flow of URL reading pattern；Enhance training with pairs that have low token overlap but share common IO patterns

### case_id=4809 FN benchmark_preference_bias

- 方法: `copy` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Copies a local file to another local file with validation and buffered stream copy.
- B 摘要: Downloads a resource from a URL with caching and returns an InputStream from the cached file.
- 静态失败原因: The model likely relied on lexical overlap and API similarity, which are low (Jaccard 0.17). It correctly identified the significant semantic differences in purpose, source, and return type, leading to a non-clone prediction that conflicts with BCB's lenient annotation.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider them Type-4 clones because both perform file I/O with stream copying, focusing on the shared core behavior of reading from an input and writing to a file, despite different contexts and additional logic.
- 共享行为: Both read from an input source and write to a file using streams.；Both handle stream closing in finally or catch blocks.
- 行为差异: A copies between local files; B downloads from remote URLs with caching logic.；A returns void; B returns an InputStream.；A uses a buffer size of 4096 bytes; B reads byte by byte.；B includes HTTP request handling, cache checking, and conditional return of cached or newly downloaded file.
- 修正建议: Review BCB annotation guidelines for partial functionality clones to ensure consistency.；Consider training the model with more Type-4 examples or adjusting the similarity threshold to match BCB's preferences.；Alternatively, refine the model to ignore high-level task differences and focus on low-level stream operations if aiming for BCB agreement.

### case_id=4810 FP lexical_or_api_overlap

- 方法: `setMembers` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Parses HTML from a Trac ticket page to extract component and priority options into class arrays.
- B 摘要: Searches Google Images for an artist and album, extracting image URLs into a list.
- 静态失败原因: Static BERT/GraphCodeBERT may have overemphasized surface-level similarities such as the use of URL, BufferedReader, while loop reading lines, try-catch, and string manipulation. The token overlap (Jaccard=0.1637) is low but the common API pattern creates misleading similarity.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone (0) because the functions perform entirely different tasks despite sharing some boilerplate code patterns. They are not functionally similar even at a high level.
- 共享行为: Both make HTTP connections to external URLs；Both read HTML content line by line；Both use string/regex pattern matching to extract data from HTML
- 行为差异: Function A extracts option values from select tags for Trac components/priorities; B extracts image URLs from Google search results；Function A uses Pattern/Matcher with regex; B uses String.split and substring；Function A populates class-level String arrays; B adds to a list of strings；Function A has different error handling: prints messages; B shows error dialog or ignores exception
- 修正建议: Incorporate data-flow or control-flow awareness to distinguish functional purpose；Use method names and comments as additional features；Train with more examples that have similar API usage but different semantics

### case_id=4811 FP boilerplate_overlap

- 方法: `getLinksFromURLFast` vs `setBundleInfoName`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Extracts all hyperlinks and their text from a given URL, returning a vector array of links and texts.
- B 摘要: Reads a configuration file from a URL, parses key-value pairs, and updates bundle names in a list of BundleInfo objects.
- 静态失败原因: Static BERT/GraphCodeBERT models may rely on token overlap and syntactic structures; both functions have similar boilerplate code (URL, BufferedReader, while loop), leading to a false positive clone prediction despite different semantics.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clone because the functions have different end goals and outputs; they only share superficial structural patterns like URL opening and line reading, which are not sufficient for functional similarity.
- 共享行为: Both open a URL and read line by line using BufferedReader；Both perform string manipulation and parsing on each line
- 行为差异: Function A extracts links using regex; Function B parses '=' separated key-value pairs；Function A returns two Vectors; Function B returns a boolean and modifies a list；Function A uses multiple regex patterns; Function B does not use regex；Function A throws Exception; Function B catches IOException and returns false on failure
- 修正建议: Incorporate data-flow analysis to distinguish different output behaviors；Use type-aware embeddings to capture different return types and method signatures；Train on more diverse non-clone pairs with similar boilerplate to reduce false positives

### case_id=4812 FP lexical_or_api_overlap

- 方法: `run` vs `getVersion`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a local classpath resource file and displays its text content in a GUI component.
- B 摘要: Fetches a version string from a remote URL and returns it.
- 静态失败原因: Static BERT/GraphCodeBERT likely overemphasizes lexical overlap and API usage patterns (URL, BufferedReader, InputStreamReader) while missing the semantic intent difference, common in Type-4 false positives.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would likely label non-clone because the functions have different overall purposes (local resource display vs remote version retrieval) and significant differences in output and side effects, despite sharing some boilerplate I/O code.
- 共享行为: Open a URL or URLConnection；Use BufferedReader and InputStreamReader to read text；Read lines in a loop；Handle exceptions silently with try-catch
- 行为差异: A reads from classpath resource; B reads from remote HTTP URL；A appends all lines with line breaks; B overwrites variable and returns last line；A updates a GUI; B returns a string；A is a Runnable; B is a static method
- 修正建议: Add contrastive learning tasks focusing on return type and side effects；Incorporate dataflow analysis to distinguish local vs remote resource access；Train on more examples with similar API calls but different functionality

### case_id=4813 FP lexical_or_api_overlap

- 方法: `handleHandshake` vs `callService`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Handles Minecraft handshake by validating username and optionally performing an HTTP request to session server.
- B 摘要: Generic HTTP GET call that reads a URL and stores the response.
- 静态失败原因: The model likely over-relied on the lexical overlap of URL opening and reading boilerplate, ignoring the surrounding logic and structural differences.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely marked non-clone because the two functions have entirely different purposes and control flow, despite sharing a common API usage pattern.
- 共享行为: Both create a URL object；Both open an InputStream via URL.openStream()；Both read lines from the stream using BufferedReader；Both close the BufferedReader
- 行为差异: Function A has complex conditional logic for username validation and different actions based on username value；Function A sends network packets (Packet1Login) or shuts down connection；Function B is a straightforward utility that stores the entire response in a string；Function A handles exception with stack trace print and custom shutdown message
- 修正建议: Incorporate control-flow and data-flow features to distinguish different program logic；Add attention on broader context beyond local API sequences；Use finer-grained structural matching (e.g., AST sub-tree comparison) to avoid false positives from common patterns

### case_id=4814 FN benchmark_preference_bias

- 方法: `getFile` vs `getResponse`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies its content, and returns the local file path.
- B 摘要: Parses an HTTP GET request, serves a static resource, and returns the HTTP response as a byte array.
- 静态失败原因: Static model correctly predicted non-clone due to low lexical and structural similarity; BCB label is overly broad.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB likely annotated as clones due to both being network-related utilities with I/O operations and exception handling, despite different functionality.
- 共享行为: Both perform file I/O operations；Both use streams and exception handling
- 行为差异: A downloads and modifies a remote WSDL; B serves a local static resource；Different input/output types and logic
- 修正建议: Focus on functional purpose rather than low-level I/O patterns；Use finer-grained semantic annotations

### case_id=4815 FP boilerplate_overlap

- 方法: `handleHandshake` vs `populateResources`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Handles Minecraft client handshake by validating server key and performing session authentication via HTTP request.
- B 摘要: Loads default template files and images from classpath and saves them as persistent resources.
- 静态失败原因: The static model likely overfitted to common API usage patterns (URL, BufferedReader, InputStreamReader, try-catch) and ignored the distinct algorithmic logic and domain context. The sequence of API calls is similar, leading to a high embedding similarity despite semantic difference.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would not consider these clones because they have completely different functionality and domain. Even though both involve I/O, the high-level purpose is unrelated. BCB typically requires at least partial functionality similarity, which is absent here.
- 共享行为: Use URL and openStream to read data；Use BufferedReader to read lines；Handle exceptions with try-catch blocks
- 行为差异: Different domain: network authentication vs resource loading；Function A sends packets and shuts down connection; function B saves resources to database；Function A's logic depends on handshake packet content; function B iterates over fixed template file list and predefined images；Function A interacts with an external server; function B only uses local classpath resources
- 修正建议: Improve model to incorporate data-flow analysis and semantic understanding beyond API call sequences；Use contrastive learning to distinguish between different use cases of same APIs；Include type information and variable names more effectively；Increase dataset diversity to avoid overfitting to boilerplate patterns

### case_id=4816 FP boilerplate_overlap

- 方法: `loadMFileViaWeb` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Loads a MATLAB file from a web URL, reads its content line by line, parses it into a UserFunction, and returns it.
- B 摘要: Performs a Google image search by reading HTML from an HTTP connection, extracts image URLs, and updates a UI with the first image.
- 静态失败原因: Static models like GraphCodeBERT may over-rely on local syntactic patterns (e.g., opening a URL, reading lines) and miss the broader semantic divergence. The high token overlap in boilerplate misleads the model into predicting a clone despite different purposes.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB considers these non-clones because the overall functionality is entirely different: one loads scientific code, the other performs web searching and UI interaction. The few shared patterns are common Java boilerplate for reading from URLs, not indicative of semantic clone status.
- 共享行为: Opens a URL connection and reads the content using BufferedReader in a while loop.；Concatenates lines into a single string.；Wraps I/O operations in try-catch blocks.
- 行为差异: A uses URL.openStream() with generic URL, B uses HttpURLConnection with custom User-Agent.；A parses the content into a UserFunction via FunctionParser, B splits HTML strings to extract image URLs.；A returns a UserFunction, B updates a UI and sets button enabled state.
- 修正建议: Incorporate method names and class context to capture domain semantics.；Use dataflow analysis to distinguish how the read data is processed downstream.；Fine-tune with more negative examples of boilerplate-only similarity.

### case_id=4817 FN boilerplate_overlap

- 方法: `buildSiteForEdit` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Builds a site by transforming XML pages and writing output files.
- B 摘要: Launches a NexOpen project by processing Maven pom files and configuring Hibernate.
- 静态失败原因: The static model likely focused on low token overlap and domain-specific keywords, missing the high-level structural similarity that BCB might have used.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may have labeled these as clones due to superficial similarities like using file I/O, XML processing, and property handling, which might be considered broad Type-4 similarity.
- 共享行为: Both involve file I/O for reading and writing files.；Both use XML parsing and processing.；Both handle properties and configuration.
- 行为差异: Function A focuses on site generation from page templates; Function B initializes an Eclipse plugin project.；Function A uses Transformer and XSLT; Function B uses ContentHandlerTemplate and Maven-specific API.；Function A writes multiple output files; Function B sets up Hibernate and schedules a job.；Different error handling patterns and library dependencies.
- 修正建议: Incorporate finer-grained semantic features specific to functionality rather than just token overlap.；Use cross-domain embeddings to capture abstract similarities in workflows.

### case_id=4818 FN partial_functionality

- 方法: `sendRequest` vs `httpRequestByPOST`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends HTTP POST request with GZIP-compressed XML, parses response as JDOM document, with UI for server configuration.
- B 摘要: Sends HTTP POST request with URL-encoded form parameters, returns response string, handles error codes.
- 静态失败原因: Low token overlap and different API usage (GZIP, JDOM vs HttpClient) caused the model to miss the shared functionality.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels clones based on high-level functional similarity, such as both being HTTP POST request methods, ignoring differences in data format, UI, and error handling.
- 共享行为: Both perform HTTP POST requests.；Both read the response from the server.；Both use standard Java I/O and networking libraries.
- 行为差异: A uses GZIP compression and XML payload; B uses URL-encoded form data.；A includes UI dialog for server configuration; B does not.；A returns empty string; B returns the response content as a string.；A parses response into JDOM Document; B reads response as plain text.
- 修正建议: Train with examples of partial clones where only the core functionality matches.；Use graph-based or flow-based models to capture data flow similarities.；Incorporate method-level semantic embeddings that abstract API specifics.

### case_id=4819 FP lexical_or_api_overlap

- 方法: `readPage` vs `downloadFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a web page and returns its content as a string, optionally skipping lines starting with '#'.
- B 摘要: Downloads a file from a URL to a local destination, reporting download progress.
- 静态失败原因: The model likely overemphasized the shared pattern of opening a URL, reading in a loop with InputStream/Reader, and throwing exceptions. The low token Jaccard (0.23) suggests the model relied on functional API calls rather than overall semantics.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels as non-clone when functions have different outputs and side effects, despite sharing low-level URL reading boilerplate. Here, one produces a string and the other writes a file, so they are functionally distinct.
- 共享行为: Both open a URL and read data from it.；Both use loops to read data sequentially.；Both handle IO and may throw exceptions.
- 行为差异: A returns the page content as a string; B writes bytes to a file and returns a boolean.；A filters comments based on '#' prefix; B has no filtering but tracks download progress.；A uses BufferedReader for text; B uses BufferedInputStream/BufferedOutputStream for binary data.
- 修正建议: Incorporate output type and side-effect analysis (e.g., return type, file writes).；Focus on high-level purpose rather than low-level IO patterns.；Use data-flow analysis to distinguish between reading vs. writing data.

### case_id=4820 FP partial_functionality

- 方法: `getDatasetsList` vs `readZoneIDs`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches and caches a list of dataset names from a remote server URL.
- B 摘要: Reads a set of zone IDs from a classpath resource file.
- 静态失败原因: The model may have overemphasized the common 'read lines from URL' boilerplate and ignored key differences in URL construction, return type, and caching logic, leading to a false positive.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely considers these non-clones because the core functionality differs (remote dataset listing vs local zone ID reading) and the caching mechanism adds a significant structural difference.
- 共享行为: Both open a URL connection and read lines of text.；Both populate a collection with parsed data.；Both handle exceptions and close resources.
- 行为差异: A appends a query parameter to the URL; B uses a class resource path.；A caches results in a HashMap; B does no caching.；A returns a List<String>; B returns a HashSet<Integer>.；A is synchronized; B is static.
- 修正建议: Incorporate deeper structural features like data dependencies and control flow.；Add type-aware encodings for return types and data structures.；Use graph-based representations to capture divergent branching patterns.

### case_id=4821 FP boilerplate_overlap

- 方法: `readIntoList` vs `checkForUpgrade`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads an HTML list from a URL and populates a map of JMenuItems with action commands and listeners.
- B 摘要: Checks for software upgrades by querying a remote server, processes license and upgrade information, and updates UI components accordingly.
- 静态失败原因: Static BERT/GraphCodeBERT models may overemphasize common API usage patterns (e.g., BufferedReader, URL, while loop) and structural similarities (sequential steps), while missing the semantic context and overall goal. They may treat the shared I/O code as a strong indicator of clone, leading to false positives when the core logic diverges.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB prefers semantic similarity of the core functionality. Here, both functions read from a URL, but their purposes are entirely different. BCB would likely not consider this a clone because the high-level behavior (menu building vs. upgrade checking) is dissimilar, and the shared pattern is a common boilerplate (reading from URL). BCB annotations often require more than just lexical overlap.
- 共享行为: Both open a URL connection and read lines using BufferedReader.
- 行为差异: Function A builds a menu UI from parsed HTML; Function B performs upgrade checking and database operations.；Function A uses JMenuItem and action commands; Function B uses SQL queries and UI component visibility toggling.；Function A processes each line into a menu item; Function B aggregates lines and then splits into records.；Function A has a simpler structure; Function B has complex error handling and database interactions.
- 修正建议: Improve model's ability to capture high-level semantics beyond local patterns.；Incorporate task-specific context or control-flow dependencies.；Use contrastive learning that penalizes matches on boilerplate alone.

### case_id=4822 FP boilerplate_overlap

- 方法: `ExternalDecoder` vs `readData`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.99`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Constructor that sets up a thread to copy an input stream to a process output stream.
- B 摘要: Static method that parses several comma-separated string variables into sets and reads a configuration file to populate a hash table.
- 静态失败原因: Static BERT models may over-rely on surface features like common Java API tokens (InputStream, IOException, StringTokenizer) and repeated patterns (while loops, if statements), causing false positives especially when one function is very long (B) and contains many boilerplate structures.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels this as non-clone because the functions have completely different purposes and minimal structural similarity. The BCB guidelines for Type-4 require semantic similarity, which is absent here.
- 共享行为: Both involve some I/O operations (InputStream in A, file reading in B).；Both may throw or catch IOException.
- 行为差异: A is a constructor; B is a static void method.；A initializes a process pipeline; B initializes lookup sets from static strings and a file.；A uses threading; B does not.；The core functionality (copying stream vs. parsing tokens and building a dictionary) is entirely different.
- 修正建议: Improve token-level attention to distinguish between API usage patterns and core logic.；Use cross-contextual embeddings that capture functional flow rather than surface tokens.；Incorporate structural features like dataflow or control-flow graphs to detect true semantic similarity.

### case_id=4823 FN partial_functionality

- 方法: `doRawRequest` vs `read`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends an HTTP POST request to a fixed service URL with given post data and returns the response body as a string.
- B 摘要: Opens a URL or file specified by name, reads its content via an overloaded read method, and returns a status code indicating success or error.
- 静态失败原因: Low token Jaccard (0.111) and different method names (doRawRequest vs read) likely led the static model to treat them as unrelated. It may have missed the structural similarity of opening a URL and reading a stream due to reliance on lexical overlap.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB might label these as clones because both functions involve opening a URL and reading input, a common pattern in network I/O. Despite differences in request method and return type, they share the core data retrieval pattern.
- 共享行为: Both open a URL connection and read from its input stream.
- 行为差异: Function A performs an HTTP POST with writing data; function B only reads (GET or file).；Function A returns the full response body as a String; function B returns an integer status code.；Function B can also read from local files; function A only uses a fixed SERVICE_URL.
- 修正建议: Incorporate abstract syntax tree (AST) or control-flow graph (CFG) features to capture structural I/O patterns.；Use a model that can learn from broader API usage contexts rather than token-level similarity.

### case_id=4824 FN benchmark_preference_bias

- 方法: `modifyApplicationMessage` vs `fetchURLData`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Modifies a properties file for a given locale by updating or adding a message key-value pair.
- B 摘要: Fetches data from a URL, optionally via a proxy, and returns the data as a byte array.
- 静态失败原因: Static BERT models rely on token overlap and structural similarity; low Jaccard (0.12) and differing AST patterns lead to non-clone prediction, which aligns with semantic dissimilarity but contradicts the BCB label.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider both as I/O methods that read data from a source and process it, but this is too broad for typical BCB clones.
- 共享行为: Both use InputStream and handle I/O exceptions；Both use try-catch blocks
- 行为差异: A operates on local properties files; B fetches from network URLs；A modifies and writes to a file; B reads and returns byte array；A handles locale-specific properties; B handles HTTP connection and proxy settings
- 修正建议: Refine clone annotation guidelines to exclude such unrelated I/O methods；Improve model to capture deeper semantic differences through dataflow or functional signatures

### case_id=4825 FN partial_functionality

- 方法: `copyResource` vs `runDynusT`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.5`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Copies a resource from a URL or file to a destination file using byte-level I/O.
- B 摘要: Sets up a temporary directory, copies multiple required files, runs the DynusT simulation executable, and optionally cleans up.
- 静态失败原因: Static BERT models rely on token overlap and surface-level structural similarity, which is low (Jaccard 0.062). The models likely did not recognize the underlying file-copy pattern shared by both methods, especially since one method is a simple utility and the other is a complex domain-specific method.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider them clones because both methods perform file copying operations, even though runDynusT has additional functionality. The partial functional similarity in the copying aspect might justify a Type-4 clone label.
- 共享行为: Both involve copying files from a source to a destination；Both check for file existence；Both perform I/O operations on files
- 行为差异: copyResource copies a single source file; runDynusT copies multiple files and also runs an external program；copyResource uses low-level InputStream/OutputStream; runDynusT uses IOUtils.copyFile；runDynusT has logging, cleanup, and command execution; copyResource is a simple copy
- 修正建议: Use code graph representations (e.g., CFG, data flow) to capture semantic similarities beyond surface tokens；Train with examples of partial functional similarity where one method is a subset of another；Improve attention to common API patterns like file I/O, even when embedded in larger contexts

### case_id=4826 FP partial_functionality

- 方法: `sendPost` vs `main`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends an HTTP POST request with parameters and returns the response body.
- B 摘要: Fetches a URL via GET and prints each line to standard output.
- 静态失败原因: Static BERT or GraphCodeBERT likely over-focused on the lexical and API overlap (e.g., URL, BufferedReader, while-loop pattern) and ignored the semantic differences in request method and return value usage.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely considers these non-clones because the overall functionality is different (POST vs GET, returning vs printing), despite the shared HTTP reading boilerplate.
- 共享行为: Both open a URL connection；Both read lines using BufferedReader；Both close the reader
- 行为差异: A uses POST with output stream to send parameters, B uses GET via openStream；A returns the response as a string, B prints lines to console；A handles exceptions with MsgPrint, B throws IOException
- 修正建议: Incorporate dataflow analysis to distinguish between different HTTP methods (POST vs GET)；Consider the method signature and return type to capture intent；Add contrastive examples where similar boilerplate has different functionality

### case_id=4827 FP boilerplate_overlap

- 方法: `run` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.85`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Performs an HTTP GET request with Basic Authentication, reads the entire response, and stores it.
- B 摘要: Performs an HTTP GET request to Google Images, parses the HTML response to extract image URLs, and sets a GUI icon with the first image.
- 静态失败原因: The static model likely picked up on the shared boilerplate of HTTP connection and BufferedReader reading, and the overall try-catch structure, but failed to distinguish the different headers, response handling, and post-processing logic. The token overlap is low but the structural pattern is common.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the functions have different purposes and output behaviors; one is a generic HTTP client with auth, the other is a specific web scraping method with GUI side effects. The similarity is limited to boilerplate HTTP reading.
- 共享行为: Both open an HTTP connection and read the response line by line using BufferedReader.
- 行为差异: Function A uses Basic Authentication, while Function B uses a User-Agent header.；Function A stores the entire response as a string, while Function B parses the response to extract image URLs.；Function A records timing and sets a finish flag; Function B updates GUI components and adds to a list.；Function B has post-processing (splitting, filtering) and GUI interaction, which Function A lacks.
- 修正建议: Improve model ability to distinguish different response processing logic beyond just reading.；Pay attention to specific HTTP headers and the nature of the data being read.；Incorporate more fine-grained semantic understanding of the post-read operations.

### case_id=4828 FP boilerplate_overlap

- 方法: `readData` vs `convert`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Parses multiple comma-separated string variables into various sets and a mapping of valid input sequences.
- B 摘要: Converts an ACRNEMA stream file to DICOM format, handling pixel data and UIDs.
- 静态失败原因: The model likely focused on boilerplate structures like try-catch blocks, loops, and output statements, while missing the distinct semantic contexts of parsing vs. DICOM conversion.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would label this as non-clone (Type-0) because the two functions have completely different functionality and no partial similarity.
- 行为差异: Function A initializes sets and a hash map from string tokens; function B performs file I/O and DICOM conversion.；Function A operates on class-level string fields; function B reads from a File source and writes to a File destination.；Function A has no exception handling beyond a generic catch; function B has specific IOException handling and DICOM-specific logic.
- 修正建议: Train model to better distinguish domain-specific operations from generic control flow.；Incorporate structural alignment and dataflow analysis to detect mismatched logic.；Use longer context windows to capture overall function purpose.

### case_id=4829 FP lexical_or_api_overlap

- 方法: `getDatasetsList` vs `loadURL`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Retrieves and caches a list of datasets from a server by appending '?server=list' and reading lines.
- B 摘要: Downloads a VRML file from a URL with optional authentication and writes to a temp file while updating a progress label.
- 静态失败原因: The model likely overemphasized lexical and API overlap (URL, BufferedReader, readLine, IOException) and similar boilerplate for opening connections, ignoring the semantic differences in high-level functionality.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled non-clone because the functions have different purposes (list retrieval vs file download), different signatures, and different side effects (caching vs file writing), making them not similar even under broad Type-4 criteria.
- 共享行为: Both open a URL and read lines from it using BufferedReader.
- 行为差异: A caches results in a HashMap and returns a list; B writes to a file and does not return.；A uses a specific query parameter; B supports authentication.；A is synchronized and handles exceptions by logging and throwing RuntimeException; B throws IOException.；B updates a UI label and prints to console; A does not.
- 修正建议: Incorporate data flow analysis to distinguish return types and side effects.；Use method signature and purpose classification to separate retrieval from download.；Train on more diverse pairs that share API usage but have different intents.

### case_id=4830 FP lexical_or_api_overlap

- 方法: `handleHandshake` vs `getTicketsForQueue`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Handles a Minecraft handshake packet by validating a server key and making an HTTP request to authenticate the session.
- B 摘要: Retrieves tickets for a queue from a RequestTracker system by making an HTTP GET request and parsing the response.
- 静态失败原因: The static model might have over-weighted the similar use of Java I/O classes (URL, BufferedReader, try-catch) and network communication patterns, ignoring the distinct domain-specific logic and method names.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels these as non-clones because the semantics are completely different despite some superficial API similarity.
- 共享行为: Both perform HTTP requests；Both read responses line by line using BufferedReader；Both handle exceptions with try-catch
- 行为差异: Different domain: Minecraft authentication vs. ticket tracking；Different request construction and parameter handling；Different response parsing logic and conditions；Different error handling messages and actions
- 修正建议: Incorporate method names and class context as features；Use dataflow analysis to distinguish variable roles；Train on more diverse examples of unrelated functions with similar API usage

### case_id=4831 FN partial_functionality

- 方法: `main` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a file line by line, applies title case and wrapping filters, and writes to another file.
- B 摘要: Retrieves a resource by URL, caches it locally, and returns an InputStream for the cached or remote file.
- 静态失败原因: Static models like BERT rely on lexical overlap and token embeddings; the low Jaccard similarity and different method names/signatures led to a non-clone prediction, missing the partial structural similarity of the I/O loop.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have considered the common read-write loop as a clone, overlooking the vast difference in overall functionality.
- 共享行为: Both perform file I/O using buffered streams；Both contain a while loop that reads and writes data
- 行为差异: Function A does text transformation; Function B does not；Function B handles HTTP, caching, and resource retrieval; Function A does not；Function A uses character streams; Function B uses byte streams；Function A writes to a file; Function B returns an InputStream
- 修正建议: Incorporate data-flow analysis to detect the core copying pattern；Use structure-based features like AST or control flow graphs to capture similarities in loops；Apply contrastive learning to focus on shared I/O patterns

### case_id=4832 FP partial_functionality

- 方法: `readRemoteFile` vs `readScalarpvviewerDocument`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: reads a remote file from a URL and returns its content as a single string
- B 摘要: reads an XML document from a URL, parses it, and updates application UI components and data structures
- 静态失败原因: Static BERT may overemphasize the overlapping URL reading pattern and ignore the distinct subsequent operations and different return types, leading to a false positive
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely labels this as non-clone because the functions diverge significantly after the initial read loop; the extensive post-processing in B changes the overall purpose from simple file reading to complex application configuration loading
- 共享行为: both open a URL stream and use BufferedReader to read lines；both have a while loop that reads lines until null；both concatenate strings from lines read
- 行为差异: function B includes XML parsing and UI updating after reading；function B has additional loop termination condition based on line content；function A returns the concatenated string; function B returns void and modifies application state；function B writes to multiple UI components and data adaptors
- 修正建议: Enhance model with dataflow analysis to track variable usage beyond initial I/O operations；Incorporate method-level semantic embeddings that capture overall method purpose；Use cross-function attention to compare entire method bodies, not just local patterns

### case_id=4833 FN partial_functionality

- 方法: `login` vs `postRequest`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.95`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Logs into LOLA by posting email and password, extracts session ID from first line of response, and sets it internally.
- B 摘要: Performs a generic HTTP POST request with key-value pairs from a HashMap, reads entire response, and returns it as a string.
- 静态失败原因: The model likely focused on lexical and structural differences (different method names, different data construction, different I/O patterns, different helper calls). The presence of specific identifiers (LOLA, FILE_LOGIN) and different control flow (only reading one line vs all lines) may have caused the model to predict non-clone. Static models may miss the underlying common HTTP POST pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB annotators may view these as clones because both perform an HTTP POST with form-encoded data, read the response, and handle errors. The specific implementation (A) is a concrete case of the generic pattern (B). BCB's guidelines often accept such pairs as Type-3/Type-4 clones (broad functionality similarity) even if semantic equivalence is not exact.
- 共享行为: Both open a URL and set DoOutput to true.；Both construct a URL-encoded query string and write it to the connection output stream.；Both read the response from the input stream.；Both handle exceptions with basic error reporting.
- 行为差异: A is specialized for login (specific URL, fixed fields, session extraction); B is generic (any URL, any parameters, returns all response lines).；A uses OutputStreamWriter; B uses PrintWriter.；A only reads first line of response; B reads all lines.；A sets session internally; B just returns data.
- 修正建议: Use models that can learn abstract API usage patterns (e.g., graph-based models capturing data flow).；Augment training with function summaries or comments.；Use contrastive learning to encourage similarity of functions that share common tasks despite surface differences.；Combine static analysis with dynamic tracing to identify common network operations.

### case_id=4834 FN partial_functionality

- 方法: `httpRequestByPOST` vs `loadExistingAntlibs`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Makes an HTTP POST request and reads the response line by line, returning the response string or null on error.
- B 摘要: Loads antlib definitions from classpath resources by reading lines from a resource file and processing each line.
- 静态失败原因: Static BERT models may have focused on the shared lexical patterns (BufferedReader, readLine, try-catch) and missed the distinct functional contexts (HTTP vs classpath loading).
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as examples of reading and processing line-oriented data from I/O streams, despite different input sources and output actions.
- 共享行为: Both use try-catch for IOException；Both read lines from an InputStream using BufferedReader；Both close streams after reading
- 行为差异: Function A performs HTTP POST request; Function B iterates over classpath resources；Function A returns response string; Function B has void return and loads antlibs as side effect；Function A handles HTTP status codes; Function B handles URI resolution and antlib loading
- 修正建议: Improve model's ability to distinguish high-level semantics beyond common I/O patterns；Incorporate type information or method signatures to differentiate API usage

### case_id=4835 FN partial_functionality

- 方法: `testReadHelloWorldTxt` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: A test method that reads a resource file from classpath, copies it to a temporary directory, and verifies content retrieval via FSContentResolver with various URI formats.
- B 摘要: A method that builds a static site for editing by iterating over pages, performing XSL transformations, reading control paths, and writing output files with string replacements.
- 静态失败原因: Static BERT/GraphCodeBERT methods rely heavily on token overlap and structural patterns. The extremely low Jaccard similarity (0.05) and lack of shared method names, long parameter lists, and differing code structures likely caused the model to classify these as non-clones. The model failed to capture the abstract similarity in file I/O behavior that BCB may have considered.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled this as a clone due to the broad interpretation of Type-4 (similar functional behavior) where both methods perform file reading and writing operations, even though the overall context and purpose are entirely different. The presence of common I/O APIs and string handling could sway BCB toward a positive annotation.
- 共享行为: Both involve file input/output operations；Both use UTF-8 encoding for reading/writing；Both handle InputStream/FileInputStream
- 行为差异: Function A is a simple unit test with assertions; Function B is a complex production method with loops and exception handling；Function A reads a single file and verifies content; Function B processes multiple pages with XML transforms and string manipulation；Function A uses standard Java I/O classes; Function B uses custom FileSystem utility and external library calls；Function A has no parameters; Function B has seven parameters and many local variables
- 修正建议: Enhance models with data-flow analysis to detect shared subroutines like file copying or stream handling；Incorporate API usage patterns and context-aware embeddings to recognize similar I/O operations across different methods；Use a hierarchical approach that first identifies core functional blocks before comparing entire methods

### case_id=4836 FP lexical_or_api_overlap

- 方法: `doVersionCheck` vs `downloadModel`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a version check URL, parses build numbers, and invokes another method for the check.
- B 摘要: Downloads an RDF/XML model from a given URL using HTTP headers and returns the model.
- 静态失败原因: Static BERT/GraphCodeBERT likely focused on lexical/API overlap (URL, InputStream, IOException) and common control flow (try-catch), ignoring the distinct problem domains and data processing logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB prefers functional similarity; these two functions perform completely different tasks (version checking vs model downloading), so they are not clones even if they share some I/O boilerplate.
- 共享行为: Both open a URL and read an input stream.；Both handle IOException.
- 行为差异: Function A parses lines for specific prefixes; Function B reads entire stream into a model.；Function A shows/hides wait cursor; Function B does not.；Function A calls another method conditionally; Function B returns a Model or throws RuntimeException.；Function B sets HTTP request properties; Function A does not.
- 修正建议: Improve representation to capture problem-specific semantics (e.g., using data flow or more detailed AST).；Include method-level context like class/method name embeddings.

### case_id=4837 FP boilerplate_overlap

- 方法: `googleImageSearch` vs `parse`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Searches Google Images for album art using HTTP GET request and parses HTML to extract image URLs.
- B 摘要: Parses a delimited data file from URL or file, handling headers, types, and scientific notation, returning a DataSet.
- 静态失败原因: Static BERT models may over-generalize from shared lexical patterns like 'BufferedReader', 'URL', 'try-catch', and 'while' loops, mistaking boilerplate I/O code for functional similarity.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels strict non-clones (Type-4) as non-clones because functions must have similar functionality beyond just reading input. These two functions serve entirely different purposes, so BCB correctly labels them as non-clones.
- 共享行为: Both read input from an external source (URL or file) using BufferedReader.；Both handle exceptions with try-catch and throw custom exceptions.；Both perform some string or token processing on the input.
- 行为差异: A is specifically for image search from Google; B is a generic data parsing function.；A uses simple string substitution and splitting; B uses a StreamTokenizer with configurable delimiters and type handling.；A focuses on extracting image URLs from HTML; B constructs a DataSet with columns and rows.；A modifies a global list; B returns a new DataSet object.
- 修正建议: Improve model sensitivity to method names and domain-specific operations.；Enhance training with more examples of non-clones that share I/O patterns but differ in core logic.；Incorporate data flow analysis to distinguish reading from different sources with different processing.

### case_id=4838 FN partial_functionality

- 方法: `copy` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: A utility method that copies an InputStream to an OutputStream using IOUtils.copyLarge, with error logging and stream closing.
- B 摘要: A complex Eclipse launch configuration method that validates inputs, reads project files, manipulates XML, copies a resource file using IOUtils.copy, and triggers an install action.
- 静态失败原因: The static model (e.g., GraphCodeBERT) likely relied on whole-function embeddings and token overlap (Jaccard=0.056), missing the small shared pattern inside the much larger function B, thus treating them as semantically distinct.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled this as a clone due to the shared use of IOUtils.copy and exception handling, considering it a Type-4 (functionally similar) clone where both perform I/O copying with error handling, despite the overall context difference.
- 共享行为: Both use IOUtils.copy or copyLarge to transfer bytes from an InputStream to an OutputStream.；Both log exceptions and handle them with similar patterns.
- 行为差异: Function A is purely a stream copy utility; function B is a multi-step project launch routine.；Function A has a single-purpose try-catch-finally; function B has conditional logic, file checks, XML handling, and property sets.；Function B is much longer and uses many Eclipse/plugin APIs not present in function A.
- 修正建议: Enhance model to detect local API usage patterns and exception handling idioms, even in long functions.；Use hierarchical or multi-resolution representations that capture both global and local semantic similarity.；Incorporate dataflow or call-graph information to identify common subroutines.

### case_id=4839 FN benchmark_preference_bias

- 方法: `convert` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Converts ACRNEMA medical image files to DICOM format, handling pixel data and UIDs.
- B 摘要: Builds a website for editing by transforming XML files and writing output pages.
- 静态失败原因: Static BERT models may have correctly identified the low lexical overlap and domain-specific APIs, leading to a non-clone prediction, but BCB's annotation considered high-level semantic similarity.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled these as clones due to low-level similarity in file I/O operations and the 'conversion' or 'building' nature, but the functional domains are entirely different, making it a likely false positive in BCB annotations.
- 共享行为: Both functions perform file I/O operations (read and write files).；Both involve loops over data elements.
- 行为差异: Function A converts medical image formats, while B transforms web page content.；A uses DICOM-specific tags and pixel data manipulation; B uses XML/XSLT and string manipulation.；A has specific logic for inflating 12-bit pixel data; B has logic for replacing URLs and handling properties.；The output of A is a DICOM file; B outputs multiple HTML pages.
- 修正建议: Incorporate domain-specific embeddings to capture medical image processing vs. web development context.；Use code summarization to capture high-level intent and separate by application domain.；Adjust clone detection thresholds to require more than generic I/O similarity.

### case_id=4840 FP lexical_or_api_overlap

- 方法: `getFrameworkFactory` vs `CheckUrl`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a service file to load an OSGi framework factory class dynamically.
- B 摘要: Opens an HTTP connection to a URL and returns the first line of the response.
- 静态失败原因: Static model likely overfitted to overlapping tokens (URL, BufferedReader, InputStreamReader, readLine, etc.) and missed the distinct high-level semantics.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB requires high behavioral similarity; these functions have different purposes and logic, so BCB labels non-clone.
- 共享行为: Both use java.net.URL and BufferedReader to read text data from a stream.
- 行为差异: getFrameworkFactory reads from a classpath resource file and instantiates a class; CheckUrl reads from an HTTP response and returns a string.；getFrameworkFactory throws an exception if no factory found; CheckUrl catches all exceptions and prints stack trace.；getFrameworkFactory uses a service loader pattern; CheckUrl performs a network request.
- 修正建议: Improve model to weight structural differences more heavily.；Incorporate control-flow or data-flow analysis to distinguish between reading a local resource vs. making network request.；Use contrastive learning with more negative examples showing similar API usage but different semantics.

### case_id=4841 FN long_range_semantics

- 方法: `getFile` vs `doGet`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies an endpoint attribute, and saves to temporary directory.
- B 摘要: Serves a static file from the file system in response to an HTTP GET request.
- 静态失败原因: The model likely focused on low lexical overlap and distinct control flow structures, missing the high-level semantic difference in purpose and context.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may have considered the shared file I/O and exception handling as similar, or labeled based on partial functional overlap (both read and output file content).
- 共享行为: Both involve file I/O and handle IOException.
- 行为差异: Different purposes: one downloads and modifies a remote WSDL, the other serves a local file over HTTP.；Different inputs: A takes serviceName, wsdlLocation, endpoint; B takes HttpServletRequest/Response.；Different outputs: A returns a file path; B writes to response stream.；A uses XML parsing and URL connections; B uses simple file streaming.
- 修正建议: Incorporate functional annotation or code summarization to capture intent.；Use whole-program analysis to understand the role of each function.

### case_id=4842 FP lexical_or_api_overlap

- 方法: `main` vs `transport`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Main method that reads a Prolog file, parses it, generates adapter classes and resources, and writes them to a JAR file.
- B 摘要: Recursively copies files from a given file or directory to a destination directory using FileChannel.
- 静态失败原因: Static model may have been misled by both methods containing file-related API calls (File, FileChannel, IOException) and similar control flow patterns (if-else, try-catch), despite low token overlap. This is a classic case of API/lexical overlap without semantic match.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled non-clone because the overall functionality is entirely different: one is a generator main, the other is a file copier. Even broad Type-4 similarity does not apply.
- 共享行为: Both involve file I/O operations.；Both handle potential IOException.
- 行为差异: Function A is a complex main driver with multiple sub-steps; Function B is a simple recursive copy.；A deals with Prolog parsing and bytecode generation; B only copies files.；A writes a JAR; B writes to a single directory.；A uses loops; B uses recursion.
- 修正建议: Incorporate AST-based or data-flow features to distinguish simple file copy from complex multi-step generation.；Use method signatures and invocation context (main vs transport) as discriminative features.；Add negative examples with similar API usage but different semantics.

### case_id=4843 FN partial_functionality

- 方法: `postData` vs `invoke`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends an HTTP POST request with form data, reads and discards the response.
- B 摘要: Sends an HTTP POST request with JSON data, reads response, deserializes it, and retries on timeout.
- 静态失败原因: Low token overlap (Jaccard 0.136) and different API usage (java.net vs Apache) misled the static model; it failed to recognize the high-level functional similarity of both being HTTP POST methods.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB annotates broad Type-3/Type-4 clones where core functionality (HTTP POST data transfer) is shared, even if implementations differ significantly.
- 共享行为: Both perform an HTTP POST request.；Both set content-type and content-length headers.；Both write data to the output stream.；Both read the response line by line and close streams.
- 行为差异: Different HTTP libraries (java.net.URLConnection vs Apache HttpClient).；Different content types (form-urlencoded vs JSON).；Different error handling (none vs retry on timeout).；Different return types (void vs Object with deserialization).
- 修正建议: Train with more diverse type-3/4 clone examples.；Use dataflow or graph-based representations to capture semantics beyond token overlap.；Incorporate knowledge of API equivalence (e.g., different HTTP clients).

### case_id=4844 FN partial_functionality

- 方法: `copyResource` vs `bootKernel`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource from a URL or local file to a destination file using byte-by-byte reading and writing.
- B 摘要: Loads configuration from Android assets, copies asset files to sdcard, then loads and boots a kernel class.
- 静态失败原因: Static BERT models rely on token overlap and structural patterns; the token Jaccard is very low (0.083), and the functions use different APIs and control flows, making it difficult to capture the high-level semantic similarity of 'copying resources'.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label these as Type-4 clones because both perform file copying from an input to an output, ignoring the additional boot kernel logic as secondary. The annotators might have considered the copying behavior as the primary functional similarity.
- 共享行为: Both read data from an input source and write to a file.
- 行为差异: copyResource uses simple byte-by-byte copy; bootKernel uses FileChannel transferTo for efficient copy.；bootKernel copies multiple assets and includes additional logic (loading properties, reflection, kernel boot).；copyResource throws exceptions; bootKernel catches exceptions, logs, and calls finish().；bootKernel is Android-specific, using AssetManager and Log; copyResource is generic Java.
- 修正建议: Train with examples of partial functionality clones across different domains.；Use code summarization or intent detection to capture high-level goals.；Incorporate contrastive learning that focuses on semantic intent rather than lexical overlap.

### case_id=4845 FP lexical_or_api_overlap

- 方法: `main` vs `copyIconFiles`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Main method that parses a Prolog file and generates adapter code into a JAR file.
- B 摘要: Private method that copies icon files (16x16 and 32x32) for a UML class based on annotations.
- 静态失败原因: The model likely overemphasized the lexical match on file I/O APIs (FileChannel, FileInputStream, FileOutputStream) and exception handling boilerplate, while ignoring the high-level semantic difference.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would label this as non-clone because the functions have entirely different purposes and logic, despite some superficial API overlap.
- 共享行为: Both perform file I/O using FileChannel.；Both catch exceptions and print stack traces.
- 行为差异: Function A parses Prolog and generates Java adapter code; Function B copies image files.；Function A writes to a JAR file; Function B writes to a directory.；Function A involves complex class loading and code generation; Function B is straightforward file copy.
- 修正建议: Train models to differentiate between core logic and boilerplate code.；Incorporate data flow or control flow analysis to capture high-level semantics.；Use AST-based or graph-based representations that better capture functionality.

### case_id=4846 FN benchmark_preference_bias

- 方法: `main` vs `readData`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.4`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Sends an HTTP POST request to RenRen API with hardcoded parameters and prints the response.
- B 摘要: Parses configuration strings into sets and maps for Tibetan transliteration data, likely reading from a file.
- 静态失败原因: Static BERT/GraphCodeBERT models rely on token overlap and surface-level similarity; here token Jaccard is very low (0.0645) and code structures are completely different, so the model correctly predicts non-clone. The BCB label of 1 suggests a preference for broad functional similarity not captured by lexical cues.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider both as 'initialization' routines that set up data for further processing, though they target different domains. Possibly the full B includes network/file I/O similar to A, but given truncated code, the similarity is not justified.
- 行为差异: Function A performs network I/O and prints output; Function B parses local string data into collections.；Function A has no parameter passing or data structure initialization like B; B uses multiple HashSets and HashMaps.
- 修正建议: Improve model's ability to capture semantic similarity beyond lexical overlap, possibly using graph-based representations or cross-modal embeddings.；Train on more diverse clone types including type-4 to recognize broad functional similarity.

### case_id=4847 FN benchmark_preference_bias

- 方法: `loadExistingAntlibs` vs `read`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Loads antlib definitions from classloader resources by reading a resource file line by line and constructing URIs for each package.
- B 摘要: Reads a file or URL given by name and returns a status code indicating success or error.
- 静态失败原因: Static BERT/GraphCodeBERT correctly predicted non-clone (0) given low token overlap and distinct semantics; BCB label 1 is questionable.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have annotated as clone due to superficial commonality in using URL, streams, exception handling, and reading input, despite fundamentally different functionality.
- 行为差异: Different input types (ClassLoader vs String)；Different purpose (load antlibs vs read file/URL and return status)；Different output (void vs int)；A uses classloader resources, B uses direct file/URL streams
- 修正建议: Re-evaluate BCB annotation for this pair; it may be a false positive label.；Improve model robustness to ignore superficial API overlaps.；Incorporate structural and dataflow analysis to separate resource loading from file reading.

### case_id=4848 FN partial_functionality

- 方法: `modifyApplicationMessage` vs `saveProject`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Modifies a specific key-value pair in a locale-specific properties file, copying from English if needed.
- B 摘要: Exports a project to a zip file by creating a directory structure and saving various data (types, images, trajectories, XML files).
- 静态失败原因: The model likely focused on lexical and syntactic differences (token Jaccard low) and missed the high-level functional similarity in file persistence. The functions use different libraries (Properties vs. FileChannel, etc.) and have different structures, but both are about saving state to disk. The model might have been misled by the specific domain terms (locale vs. project) and didn't generalize to 'file I/O' functionality.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: Both are file-based persistence operations, which BCB may consider functionally similar at a high level (Type-4 similarity). They share common patterns like reading/writing files and handling I/O exceptions.
- 共享行为: Both perform file writing operations.；Both check file existence and handle I/O exceptions.；Both use File and stream classes for I/O.
- 行为差异: A modifies a single properties file; B creates multiple files and directories and zips them.；A focuses on text manipulation of property entries; B handles binary file copying, XML serialization, and zip creation.；A handles a single locale; B handles multiple types of data.；A is a simple update; B is a complex export with many sub-steps.
- 修正建议: Improve the model's ability to recognize high-level functional similarity based on I/O patterns.；Incorporate training on more Type-4 clones that share only abstract behavior.；Use abstract flow analysis to capture 'writing data to files' as a common operation.

### case_id=4849 FN partial_functionality

- 方法: `fileDownload` vs `importRoles`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a file from a URL and saves it to a local directory as download.pdf, with logging of exceptions.
- B 摘要: Downloads role data from a URL, parses XML-like format to produce a list of RoleName objects, catching specific exceptions silently.
- 静态失败原因: Static BERT models rely on token similarity and AST patterns; the low Jaccard similarity (0.18) and differing method signatures, return types, and API calls (e.g., FileOutputStream vs. StringBuffer) led to a non-clone prediction. The model did not capture the broader functional similarity of the URL-to-processing pipeline.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB annotators likely considered both as instances of the 'URL retrieval and processing' pattern, emphasizing the common structural template of opening a URL and reading input, while tolerating differences in output and exception handling.
- 共享行为: Both open a URL and read input using BufferedReader；Both use try-catch for IO exceptions；Both process input in a loop
- 行为差异: A writes raw bytes to a file; B extracts structured data from lines；A returns void; B returns ArrayList<RoleName>；A logs exceptions; B catches and ignores exceptions；A uses FileOutputStream; B uses StringBuffer and conditional parsing
- 修正建议: Inject data-flow analysis to recognize the read-from-URL-and-process pattern；Use contrastive learning with BCB-style partial clones as positive examples；Employ AST pattern matching to detect common I/O skeletons

### case_id=4850 FN boilerplate_overlap

- 方法: `login` vs `getWebByUrl`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Logs in to LOLA by sending a POST request with email and password, extracts session ID from response.
- B 摘要: Fetches a web page by URL, reads its content, writes it to a file, and recursively processes links.
- 静态失败原因: Static BERT models rely on token matching and had low Jaccard similarity (0.25). They likely focused on dissimilar method names and specific logic, missing the broad functional overlap in HTTP boilerplate code.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB often considers functions as clones if they share a common algorithmic pattern, such as network communication setup, even if the specific task differs. The structural similarity of opening a URL, reading/writing streams, and exception handling leads to a positive clone label.
- 共享行为: Both establish URL connections and handle input/output streams；Both use try-catch blocks for exception handling；Both print status messages to console
- 行为差异: login() sends data via POST request; getWebByUrl() reads data via GET request；login() returns a session ID; getWebByUrl() writes to a file and has no return value；getWebByUrl() has recursive URL processing; login() does not；login() uses URLEncoder; getWebByUrl() does not
- 修正建议: Incorporate data flow analysis to match similar connectivity patterns；Use graph-based embeddings that capture control flow and API call sequences；Combine static predictions with functional similarity measures based on common subroutines

### case_id=4851 FP boilerplate_overlap

- 方法: `getUser` vs `retrieveQ`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Loads a user from a DAO, or reads from a config file if not found, and saves to DAO.
- B 摘要: Fetches content from a URL and returns it as a string.
- 静态失败原因: The static BERT model likely over-relied on token overlap from common I/O patterns (URL, BufferedReader, readLine) and failed to capture the semantic differences in data source and output intent.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled as non-clone because the functions have distinct purposes (user authentication vs. generic URL retrieval) and different outputs, despite sharing some I/O boilerplate.
- 共享行为: Both use URL, BufferedReader, and InputStream for reading data.；Both read line by line using readLine().
- 行为差异: A reads from a local file; B reads from a remote URL.；A returns a User object; B returns a String.；A saves data to a DAO; B does not.；A catches and prints exceptions; B throws them.
- 修正建议: Incorporate data flow and type information to distinguish different sources and outputs.；Use graph-based code representations that capture long-range dependencies and control flow.；Train on more diverse examples to reduce sensitivity to boilerplate patterns.

### case_id=4852 FP partial_functionality

- 方法: `sendPost` vs `doVersionCheck`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends an HTTP POST request with parameters and returns the response body as a string.
- B 摘要: Fetches version information from a remote URL via HTTP GET, parses it, and proceeds with version check logic.
- 静态失败原因: The static BERT/GraphCodeBERT model likely over-relied on overlapping API sequences (URL, openStream, BufferedReader, while line read) and common patterns (try-catch). Despite low token Jaccard, these sequences triggered a false positive by ignoring the distinct control flow, data usage, and overall purpose (POST vs GET version check).
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely considers these non-clones because the overall functionality differs drastically: one is a generic HTTP POST utility, the other is a specific version-check routine with structured parsing of response lines. The shared I/O boilerplate is not enough to outweigh the different goals.
- 共享行为: Both open network connections and read line-by-line from an InputStream using BufferedReader.
- 行为差异: A sends POST data (PrintWriter), B does not.；A returns the response string, B returns void and calls another method.；A concatenates all lines; B parses specific lines for version strings.；A catches generic Exception; B catches IOException.
- 修正建议: Train with more diverse examples of network I/O that differ in purpose (e.g., POST vs GET, file download vs API call).；Incorporate functional semantics like return type, method signature, and parameter usage.；Use control-flow and data-flow analysis to differentiate between writing (POST) and reading (GET) operations.；Add attention to method names and comments for better context understanding.

### case_id=4853 FN benchmark_preference_bias

- 方法: `doGet` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Handles HTTP GET requests to retrieve and display a portal page, including permission checks, logging, and caching page output to a file.
- B 摘要: Copies a file from source to destination using NIO FileChannel.
- 静态失败原因: The static model correctly identified the low lexical and semantic similarity, but BCB's broad annotation scheme may classify them as clones due to a loose interpretation of functionality overlap, leading to a false negative relative to the benchmark label.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might have considered both functions as 'file-manipulating' under a very broad Type-4 clone definition, focusing on the shared file I/O aspect despite vast differences in context and purpose.
- 共享行为: Both involve file I/O operations (writing/reading files)
- 行为差异: Function A is a servlet method handling web requests with complex logic, while Function B is a simple utility for file copying.；Function A includes logging, user permission checks, and statistics, absent in Function B.；Function A writes a cached page to a temporary file only under certain conditions, whereas Function B always copies a file.
- 修正建议: Re-evaluate the BCB annotation for this pair; it may be a mislabel.；Train the model to better capture nuanced functional categories beyond surface-level I/O operations.；Introduce a threshold for functional granularity to avoid overly broad clone classes.

### case_id=4854 FN partial_functionality

- 方法: `fetchUrl` vs `invoke`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches entire content from a URL as a string, reading line by line.
- B 摘要: Invokes a remote method via HTTP POST, deserializes response, and supports retries on timeout.
- 静态失败原因: Static models rely on token overlap and syntactic structure, which are low (Jaccard 0.19). The common I/O pattern is embedded in different APIs and control flow, so the model fails to recognize the partial semantic equivalence.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely labels this as a clone (Type-3) because both functions share the core functionality of reading an HTTP response via BufferedReader/StringBuilder loop, despite different surrounding context and complexity.
- 共享行为: Both open an HTTP connection and read the response using BufferedReader and StringBuilder
- 行为差异: Function A uses GET request and returns raw string; Function B uses POST with JSON serialization and returns deserialized object；Function A has simple error handling returning empty string; Function B has retry logic and throws exceptions；Function B constructs URL dynamically and uses HttpClient library; Function A uses standard URL class
- 修正建议: Incorporate dataflow analysis to detect common I/O idioms；Train on more pairs with partial or embedded functionality similarity；Use graph-based representations to capture shared subgraph patterns

### case_id=4855 FP boilerplate_overlap

- 方法: `googleImageSearch` vs `getFullScreenUrl`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.85`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Performs a Google image search by constructing a query URL, fetching the HTML, extracting image URLs from 'href="/imgres?imgurl=..."' patterns, and displaying the first image in a UI component.
- B 摘要: Fetches a YouTube page to extract video metadata (video_id, t, title) from lines containing 'fullscreenUrl', then constructs a video download URL.
- 静态失败原因: Static BERT models may focus on surface-level lexical and structural similarities (e.g., HTTP connection, BufferedReader, exception handling) and miss the semantic differences in the parsing logic and overall purpose.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels as non-clone if the core function is different, even if some structural patterns overlap. Here, the output and specific parsing logic are domain-specific, so they are not considered clones under BCB's Type-4 definition.
- 共享行为: Both open HTTP connections to fetch web content；Both use BufferedReader to read the response line by line；Both perform string parsing to extract specific patterns；Both handle exceptions with catch blocks
- 行为差异: Method A searches Google images, method B fetches YouTube video details；Method A extracts image URLs from anchor tags, method B extracts video parameters from a specific line；Method A updates UI components (sets icon), method B returns a constructed URL；Method A sets a button enabled, method B manages progress bar
- 修正建议: Train on more diverse examples to distinguish domain-specific parsing from generic boilerplate；Incorporate data flow analysis to track how variables are computed and used；Add attention to the high-level method purpose and output types

### case_id=4856 FN partial_functionality

- 方法: `testNetworkHTTP` vs `doVersionCheck`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Makes multiple HTTP GET requests to various URLs, reads and discards response lines, likely for data exfiltration.
- B 摘要: Performs a version check by reading a version file from a URL, parsing version and build strings, and comparing with current build.
- 静态失败原因: Static BERT/GraphCodeBERT models rely heavily on token overlap (Jaccard=0.195) and syntactic similarity. The functions have different lengths, identifiers, and control flow, causing low similarity scores. The model missed the abstract behavioral overlap of performing an HTTP GET and reading lines, which requires understanding data flow and common patterns rather than exact token matches.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels Type-3/Type-4 clones where functions share a common algorithmic pattern, such as 'make HTTP GET request and read lines from response'. Despite different specific data processing, both functions implement that pattern, so BCB likely considered them clones.
- 共享行为: Both open a URL and read lines from the response using BufferedReader.；Both handle IOException by printing or showing an error.；Both close the stream or disconnect after reading.
- 行为差异: A makes multiple requests to different URLs; B makes a single request.；A discards all read lines; B parses the lines to extract version and build.；A uses HttpURLConnection with explicit disconnect; B uses URL.openStream() with close.；B updates a View with wait cursor and user messages; A has no UI interaction.
- 修正建议: Train models with examples of partial functionality similarity, focusing on common I/O patterns.；Incorporate data flow analysis to identify sequences of operations like 'open URL -> read lines -> handle exception'.；Use contrastive learning to bring representations of functions with similar high-level behavior closer together.

### case_id=4857 FP lexical_or_api_overlap

- 方法: `issueCommandToServer` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Sends a command and a change capsule via HTTP POST to a server and returns the response string.
- B 摘要: Performs a Google image search via HTTP GET, parses the HTML response to extract image URLs, and adds them to a list.
- 静态失败原因: Static models like BERT/GraphCodeBERT rely heavily on token overlap and common code patterns (e.g., BufferedReader, URLConnection), which are present in both functions, causing a false positive for clone detection.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would likely label as non-clone because the overall functionality and purpose are distinct, despite sharing common HTTP boilerplate code.
- 共享行为: Open HTTP connection using URL and set properties；Read response line by line using BufferedReader；Close reader and writer streams
- 行为差异: A uses POST method with parameters, B uses GET method with query in URL；A returns response as string, B parses HTML to extract image URLs；A has no conditional execution based on state, B checks if artist changed；A writes command and capsule, B reads image search results
- 修正建议: Incorporate context-aware representations that capture the intent of the function beyond API calls.；Use data flow analysis to differentiate how the response is processed (string building vs. HTML parsing).

### case_id=4858 FN partial_functionality

- 方法: `createJavaProject` vs `createJCoPluginProject`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Creates a Java project for testing with source folders, classpath, and bin folder.
- B 摘要: Creates a JCo plugin project by extracting archive, generating manifest and build properties, and setting classpath.
- 静态失败原因: Static BERT/GraphCodeBERT likely fails due to low token overlap (Jaccard 0.18) and different method names, focusing on surface-level tokens and missing the structural similarity in the Eclipse API usage pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label these as clones because both implement the common pattern of creating a project with Java nature, setting classpath, and creating directories, which is considered partial functionality similarity (Type-4).
- 共享行为: Both create an IProject and set its description with JavaCore.NATURE_ID；Both create folders (e.g., bin), set output location, and configure classpath；Both use Eclipse's IProject and IJavaProject API to manage project structure
- 行为差异: B deletes existing project before creation, while A does not；B reads an archive file and extracts contents, A does not；B sets both Java and plugin natures, A sets only Java nature；B generates MANIFEST.MF and build.properties, A does not
- 修正建议: Use graph-based code representation capturing structural patterns like API call sequences；Employ bytecode or abstract syntax tree features to match similar control and data flow；Consider renaming method names or using alias detection

### case_id=4859 FN partial_functionality

- 方法: `main` vs `readAndRewrite`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a URL and extracts its contents using a ZipInputStream.
- B 摘要: Reads a DICOM file, parses its header and pixel data, and writes the processed data to another file.
- 静态失败原因: Static BERT models rely heavily on lexical and syntactic overlap, which is low here (token Jaccard=0.118). The method names and API calls are completely different, so the model likely focused on surface-level features and missed the abstract I/O pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider these as Type-3/Type-4 clones since both perform a data reading, transformation, and writing pipeline using I/O streams, despite different domains and specific APIs. The broad pattern of 'read input, process, write output' is shared.
- 共享行为: Both open input streams from files or URLs.；Both process data by reading chunks and writing to output streams.；Both use buffered streams and handle IOException.
- 行为差异: Function A deals with ZIP extraction from a KMZ file; Function B deals with DICOM medical image format.；Function A writes extracted entries to separate files; Function B writes a single processed output file.；Function A uses ZipInputStream/FileOutputStream; Function B uses DICOM-specific APIs (DcmParser, PixelDataReader).
- 修正建议: Incorporate dataflow analysis to capture high-level I/O operations.；Use graph-based models that can represent control flow and data dependencies.；Train with more diverse examples of abstract behavioral patterns.

### case_id=4860 FN benchmark_preference_bias

- 方法: `readData` vs `postRequest`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Parses CSV configuration strings into sets and hash maps for Tibetan character processing.
- B 摘要: Sends an HTTP POST request with form parameters from a HashMap and returns the response as a string.
- 静态失败原因: Static models rely on token overlap and structural similarity; with very low Jaccard (0.086) and no significant API overlap, they correctly predicted non-clone.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have considered both as 'data processing' or 'string tokenization' tasks, or the annotation might be erroneous due to broad Type-4 similarity.
- 共享行为: Both methods use loops and string manipulation；Both involve handling of key-value data (trimmed toHashKey vs URL-encoded form data)
- 行为差异: Code A reads from static strings and populates data structures; Code B sends network request and returns response；Code A is a void method modifying global state; Code B returns a String；Code A uses StringTokenizer; Code B uses URLConnection and PrintWriter；Code A has complex parsing logic with many fields; Code B is simple HTTP client
- 修正建议: Remove this pair from clone set as they are functionally unrelated；Re-evaluate BCB labeling for similar pairs to ensure consistency

### case_id=4861 FP partial_functionality

- 方法: `downloadURLtoString` vs `get`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads all lines from a URL and returns them as a single string.
- B 摘要: Sends an HTTP GET request with specific headers, reads lines from the response, filters out comment lines, decodes each line into a GameRecord, and returns an array of GameRecords; or null on failure.
- 静态失败原因: Static BERT-based models may rely on structural similarities like the common pattern of opening a connection, using BufferedReader, and reading lines in a loop. The model may have been misled by the similar local variable names ('br', 'line', 'str') and the overall read-loop pattern, without capturing the different context (headers, filtering, parsing) and output type. Also, the model might have limited ability to distinguish between a generic string accumulation and a domain-specific object parsing.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely labels this as non-clone because the functions have fundamentally different purposes: one is a generic URL-to-string utility, the other is a specific game record fetcher with custom HTTP parameters and structured output. The token Jaccard is low (0.1667) indicating little lexical overlap. Although both read from URLs, the overall functionality and output types differ significantly, making Type-4 (semantic) clone unlikely.
- 共享行为: Both open a connection to a URL and read lines using BufferedReader.；Both use InputStreamReader to convert input stream to reader.；Both read all lines in a while loop.
- 行为差异: Function A returns a concatenated string of all lines; Function B returns an array of GameRecord objects after filtering and parsing.；Function B sets HTTP request method and custom headers; Function A just uses URL.openStream() default GET.；Function B checks response code and handles errors; Function A throws IOException.；Function B filters lines starting with '#'; Function A includes all lines.
- 修正建议: Train model to better differentiate between generic I/O utilities and domain-specific data extraction functions.；Incorporate more structural features like method signatures and return types.；Use data flow analysis to track how read data is processed (string vs. object).；Increase emphasis on API calls like HttpURLConnection, setRequestMethod, setRequestProperty vs plain URL.openStream.

### case_id=4862 FP long_range_semantics

- 方法: `actionPerformed` vs `getResponse`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `static_summary_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Handles UI action commands by opening file choosers and saving preferences for various settings like Graphviz path, image scaling, date format, etc.
- B 摘要: Parses an HTTP GET request from a byte array, retrieves a resource from classpath, and returns an HTTP response as byte array.
- 静态失败原因: The static BERT model likely failed due to the extreme length and complexity of function A, which may have obscured its actual semantics; it may have picked up on superficial patterns like try-catch blocks and string operations, leading to a false positive.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB typically marks non-clones when functions have unrelated functionality and low code similarity; here the methods are completely different in purpose and implementation.
- 共享行为: No shared behavior; both are void methods that perform I/O but in entirely different domains.
- 行为差异: Function A is an event-driven UI handler that updates GUI components and saves preferences; Function B is an HTTP request handler that constructs and returns a response.；A uses Swing and file choosers; B uses byte streams and HTTP protocol.；A modifies global state (e.g., kontroller, owner); B is self-contained and returns a byte array.
- 修正建议: Improve model's ability to handle long functions via hierarchical encoding or chunking.；Incorporate program structure (e.g., control flow, data flow) to better distinguish unrelated functionalities.

### case_id=4863 FN partial_functionality

- 方法: `copyResource` vs `getButtonSonido`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource from a URL or file to a destination file using byte-wise stream copying.
- B 摘要: Creates a JButton that, when clicked, opens a file chooser, copies the selected file to a directory using FileChannel, and updates the UI.
- 静态失败原因: The static model relied on token overlap (Jaccard=0.109) and structural similarity, which are low. It failed to recognize the underlying file copy pattern because the GUI and action listener code in function B dominated the representation, masking the I/O operations.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely labels this as a clone due to the shared core file copying functionality using streams, despite the significant differences in context and additional code. This fits the Type-4 (high-level semantic similarity) category.
- 共享行为: Both open a FileInputStream and a FileOutputStream to copy data；Both perform file copying from a source to a destination
- 行为差异: A copies from a URL or file; B copies from a user-chosen file via file chooser；A uses simple byte-by-byte read/write; B uses FileChannel.transferTo for efficient copy；A is a standalone copy; B is part of a GUI button initialization with action listener；A throws Exception; B catches IOException and handles UI updates
- 修正建议: Incorporate dataflow analysis to detect stream read/write operations；Use a graph representation that captures I/O operations regardless of surrounding code；Train on more examples of Type-4 clones where core behavior is embedded in larger methods

### case_id=4864 FP lexical_or_api_overlap

- 方法: `importSequences` vs `getPagina`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Parses sequences from a URL in a FASTA-like format, storing names and sequences in lists.
- B 摘要: Fetches the entire content of a web page as a string.
- 静态失败原因: Static BERT likely over-weighted token overlaps (URL, openStream, IOException, MalformedURLException) and the similar try-catch structure, ignoring the different core logic and data handling.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels as non-clone because the functions perform distinct tasks despite sharing common I/O patterns; partial functionality similarity is insufficient for Type-3/4.
- 共享行为: Open a URL and read from its input stream；Handle MalformedURLException and IOException
- 行为差异: A expects a specific format with '>' delimiters, B does not parse format；A stores data into lists, B concatenates lines into a string；A does not use Authenticator, B does；A returns void, B returns String
- 修正建议: Incorporate data flow analysis to distinguish parsing from simple fetching；Use graph-based representations to capture structural differences

### case_id=4865 FP boilerplate_overlap

- 方法: `retrieveQ` vs `loadURL`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads content from a URL and returns it as a string, without authentication.
- B 摘要: Reads content from a URL with optional basic authentication and writes it to a temporary file while updating a UI label.
- 静态失败原因: Static BERT/GraphCodeBERT may have been misled by the high overlap in boilerplate code (URL, URLConnection, BufferedReader, readLine) and ignored the higher-level functional differences (return vs file write, authentication, UI update).
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels these as non-clones because the overall functionality is different: one is a utility to fetch content as a string, the other downloads to a file with authentication and UI feedback. The shared URL reading pattern is insufficient to consider them functionally similar.
- 共享行为: Both open a URL connection；Both read lines from an input stream；Both handle IOException
- 行为差异: A returns the content as a string; B writes to a file；A does not handle authentication; B adds Basic Auth header；A prints response message to stderr; B prints progress to stdout and updates a UI label；A has void return type (but returns String); B is void and modifies instance state
- 修正建议: Incorporate dataflow information to distinguish output destinations (return vs file write)；Consider parameter and return type differences；Use abstract syntax tree (AST) based features that capture structural differences beyond lexical tokens

### case_id=4866 FP boilerplate_overlap

- 方法: `createHTML` vs `readUNI`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Generates an HTML string by reading a CSS resource and constructing page-specific content based on requestPage parameter.
- B 摘要: Reads a TSV file from a URL and populates a vector with concatenated id and desc fields.
- 静态失败原因: The static model likely over-weighted the common API usage patterns (URL, openStream, try-catch) and superficial structural similarities while missing the distinct semantic intent and data transformation.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely considers these non-clones because the high-level purpose and output differ significantly, despite sharing some I/O boilerplate.
- 共享行为: Both use URL to open an InputStream and read line by line.；Both handle IOException and close resources in finally block.；Both loop over input lines.
- 行为差异: createHTML outputs an HTML string; readUNI populates a vector with no return value.；createHTML has complex logic based on enum parameter; readUNI simply parses tab-separated data.；createHTML involves database queries for PAGE_HOME; readUNI does not.；readUNI skips header line and uses Scanner with delimiter; createHTML uses BufferedReader.
- 修正建议: Incorporate data-flow or control-flow analysis to distinguish functional semantics.；Train on larger variety of clone types to avoid false positives from common I/O patterns.；Use contrastive learning to emphasize functional equivalence over lexical overlap.

### case_id=4867 FN partial_functionality

- 方法: `doGet` vs `getZipAsFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Handles HTTP GET request to retrieve, render, and potentially cache a portal page with access control.
- B 摘要: Writes the content of a DigitalObject to a temporary zip file and returns the file handle.
- 静态失败原因: The static BERT/GraphCodeBERT model likely relied on low token overlap and structural differences, correctly rejecting the pair. It failed to capture the abstract functional similarity that BCB may have seen, possibly due to limited training on such broad analogies or lack of cross-context semantic understanding.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled these as clones based on a very high-level similarity: both functions 'get' a resource (page or digital object) and write it to an output (response or file). This aligns with a broad Type-4 functional similarity, despite major differences in implementation and context.
- 共享行为: Both perform I/O operations (response output or file writing).；Both use try-catch blocks for error handling.；Both log or print error messages.
- 行为差异: Function A is a servlet method handling HTTP requests; function B is a utility for file creation.；Function A involves page lookup, user authentication, and caching logic; function B simply copies a stream to a file.；Different input types and purpose (web vs file system).；Function A is much longer and complex.
- 修正建议: Incorporate control-flow and data-flow analysis to identify abstract patterns like 'get-and-output'.；Use contrastive learning with high-level task labels.；Improve handling of long-range dependencies by graph-based models.

### case_id=4868 FP partial_functionality

- 方法: `readData` vs `main`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Parses multiple comma-separated string fields into sets and a map, encoding Tibetan transliteration data.
- B 摘要: Reads lines from an input file and writes them to an output file after applying wrapping and title case filters.
- 静态失败原因: The static model likely over-generalized based on surface-level patterns such as loops and string processing, failing to capture the critical differences in data sources and overall goals. The long and complex nature of code_a may have caused the model to focus on local similarities while missing the global semantic mismatch.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB labels these as non-clones because they serve entirely different purposes with no meaningful functional overlap beyond generic programming constructs.
- 共享行为: Both use loops to iterate over tokens/lines；Both perform string operations；Both involve some form of data processing
- 行为差异: Different input sources: static string fields vs command-line file arguments；Different outputs: in-memory data structures vs a file；Different purposes: data initialization vs file copy/filter；Vast difference in complexity and length
- 修正建议: Incorporate data flow analysis to track input and output sources；Enhance model with global context aggregation to understand overall purpose；Use contrastive learning to distinguish between different high-level tasks；Consider adding program analysis features like call graph or type information

### case_id=4869 FN benchmark_preference_bias

- 方法: `copy` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Copies a source file to a destination file using Java NIO channels.
- B 摘要: Builds an editable website by reading XML, applying transformations, and writing output files.
- 静态失败原因: Static BERT/GraphCodeBERT relies on token similarity and structural overlap; the low Jaccard index (0.04) and vastly different method signatures and code length caused the model to miss the potential abstract functionality similarity perceived by BCB annotators.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might consider both as 'file copy' operations because they both read from a source and write to a destination, ignoring the substantial transformation logic in B. This is a typical Type-4 broad functionality match.
- 共享行为: Both involve reading from a file and writing to a file.；Both throw IOException.
- 行为差异: A is a simple, direct file copy while B performs complex XML parsing, DOM manipulation, and transformations.；B includes multiple file I/O operations with different paths, loop over pages, and additional error handling.；A uses NIO channels; B uses traditional streams and char buffers.；B has extensive logging and configuration handling; A has none.
- 修正建议: Incorporate functional similarity metrics (e.g., data flow or abstract syntax tree alignment).；Use models that can handle long-range dependencies and high-level semantics.；Consider ensemble methods with domain-specific heuristics for file I/O patterns.

### case_id=4870 FN partial_functionality

- 方法: `main` vs `GetResponse`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Constructs and sends an HTTP POST request with specific parameters to a RenRen API endpoint and prints the URL and response.
- B 摘要: Sends an HTTP GET request to a given URL and returns the response body as a string.
- 静态失败原因: Low token overlap (Jaccard 0.18) and significant syntactic differences caused the static model to miss the underlying HTTP request/response pattern. The model may not capture long-range API call sequences or high-level semantics.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: Both functions perform an HTTP request and read the response, which is a core functionality pattern. BCB may consider them as Type-4 clones due to this common semantic behavior despite differences in method, parameters, and output.
- 共享行为: Open HTTP connection；Set request method；Read response line by line using BufferedReader；Use HttpURLConnection
- 行为差异: HTTP method: POST vs GET；Parameter construction vs direct URL；Output: print to console vs return string；Error handling: throws IOException vs catch and ignore
- 修正建议: Use code graph representations that capture API call sequences (e.g., AST with data flow)；Train on pairs with diverse syntactic forms but similar semantic patterns (e.g., different HTTP methods)；Incorporate documentation or type information to recognize common library usage patterns

### case_id=4871 FN partial_functionality

- 方法: `getHTML` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches HTML from a given URL, optionally writes to file, and returns the content as a string.
- B 摘要: Constructs a specific POST request to RenRen API with hardcoded parameters, sends it, and prints the response to stdout.
- 静态失败原因: Static BERT/GraphCodeBERT likely focused on token sequences and structural overlap, which are low (Jaccard 0.15). It may have missed the high-level semantic similarity due to different method signatures, parameter lists, and concrete API usage.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considers both as examples of HTTP client code that read response lines, thus sharing core functionality despite different specifics. The common pattern of opening connection and reading lines may be viewed as Type-4 clone.
- 共享行为: Both open HTTP connections using HttpURLConnection；Both read response lines in a while loop using BufferedReader；Both use similar try-catch or throws IOException
- 行为差异: A is a private method with parameters; B is a public static main method；A uses GET (default) while B uses POST；A optionally writes to a file; B prints to console；A returns the HTML string; B returns void
- 修正建议: Incorporate API call graph or dataflow analysis to capture HTTP request/response patterns；Use code summarization or semantic embedding that abstracts away method signatures and specific constants；Train on pairs that share partial functionality but differ in surrounding code

### case_id=4872 FN benchmark_preference_bias

- 方法: `getFile` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Retrieves a File by checking user directory, then falls back to classpath resource and copies it to home if missing.
- B 摘要: Builds a website for editing by reading XML pages, applying XSLT transformations, and writing output files.
- 静态失败原因: Static BERT models rely on lexical overlap (Jaccard 0.08) and structural similarity, which are low. They fail to capture broad functional similarity that BCB might accept.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have considered both as file I/O utilities due to shared patterns of reading/writing streams, but the overall functionality is very different.
- 共享行为: Both involve file existence checks and I/O operations (reading from InputStream, writing to OutputStream).
- 行为差异: Function A is short and returns a single File; function B is large, processes multiple pages, and returns void.；Function A copies a resource from classpath; function B transforms XML with XSLT and handles many parameters.；Function A has no DOM or XSLT; function B handles DOM, Transformer, and FTP.
- 修正建议: Use a model that captures higher-level semantics, such as data flow or control flow.；Incorporate domain knowledge to distinguish file retrieval from site generation.

### case_id=4873 FP boilerplate_overlap

- 方法: `main` vs `convert`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Command-line tool to generate Java adapter classes from Prolog files and package them into a JAR.
- B 摘要: Converts ACRNEMA stream files to DICOM format, adding required UIDs and handling pixel data inflation.
- 静态失败原因: The model likely over-relied on lexical and structural similarities (e.g., similar control flow, try-catch blocks, and output statements) while ignoring the fundamentally different domain semantics and API usage.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clones when functions have entirely different purposes and domain logic, even if they share generic programming patterns.
- 共享行为: Both perform file I/O operations and print diagnostic messages.
- 行为差异: Function A processes Prolog files and generates Java adapters; Function B processes image files and converts to DICOM.；Function A uses a complex adapter generation framework; Function B uses DICOM-specific parsing and writing.；Function A handles command-line arguments; Function B uses fixed file parameters.；Function A writes output as a JAR; Function B writes a modified file.
- 修正建议: Improve training data to include more diverse non-clone pairs with low lexical overlap but high structural similarity.；Incorporate domain-specific knowledge or API embeddings to distinguish different functionality.

### case_id=4874 FP long_range_semantics

- 方法: `actionPerformed` vs `EncodeReturn`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `static_summary_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Handles various action commands to set application preferences for tools like Graphviz and ImageMagick, and updates UI components accordingly.
- B 摘要: Encodes data using a crypto client, combines encoded files via channel transfer, deletes temporary files, and returns the resulting route file.
- 静态失败原因: The model likely produced a false positive due to the extreme length of function A (which is truncated) and the presence of some generic tokens like 'file', 'return', and exception handling, causing the model to overestimate semantic similarity due to limited context or attention span.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB would label this as non-clone because the two methods have completely different purposes and functionalities, even under broad Type-3/4 criteria.
- 行为差异: Function A processes GUI events and updates preferences; Function B performs cryptographic encoding and file I/O.；Function A has no return value; Function B returns a File.；Function A interacts with UI components; Function B performs low-level file channel operations.
- 修正建议: Improve handling of long functions by truncating or segmenting them；Use a model with a larger context window；Incorporate structural information like AST or control flow to better capture differences

### case_id=4875 FP boilerplate_overlap

- 方法: `readData` vs `copyFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Parses multiple comma-separated string constants to populate sets and maps for Tibetan transliteration initialization.
- B 摘要: Copies a file from source to destination using a byte buffer with error handling.
- 静态失败原因: The model likely focused on superficial boilerplate (try-catch for IOException) and ignored the core logic due to the extreme length and truncation of Code A, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would label these non-clones because they have no functional similarity; one is data parsing/initialization, the other is file copying, with no overlap in purpose or logic.
- 共享行为: Both handle IOException using try-catch blocks.；Both are static methods.
- 行为差异: Code A parses string data and builds data structures; Code B performs file I/O copy.；Code A is long and complex with multiple steps; Code B is short and straightforward.；Code A uses StringTokenizer and HashSet/Map; Code B uses FileInputStream/FileOutputStream.；Code A has no return value; Code B returns a boolean indicating success.
- 修正建议: Improve handling of long sequences to avoid truncation loss.；Incorporate data flow or control flow analysis to distinguish file I/O from data parsing.；Require stronger evidence of functional similarity beyond exception handling patterns.

### case_id=4876 FP lexical_or_api_overlap

- 方法: `actionPerformed` vs `copyFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Handles user actions on a settings dialog, including file path selection for external tools and various configuration updates.
- B 摘要: Copies a file from source to destination using a buffer, with optional overwrite.
- 静态失败原因: The static model likely overfitted to lexical cues such as 'File', 'IOException', and 'logger' appearing in both methods, or to the general theme of file handling, missing the vast difference in overall semantics (event-handling vs utility method).
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels this as non-clone because the two functions have entirely different purposes: one is a settings dialog action listener, the other is a file copy utility. There is no partial functionality overlap or structural similarity.
- 共享行为: Both involve file-related operations (file selection vs file copying), but at different abstraction levels.
- 行为差异: Function A is a complex GUI event handler with many conditional branches; Function B is a straightforward I/O utility.；Function A interacts with UI components and saves preferences; Function B performs low-level byte copying.；Function A has side effects on application state; Function B returns void and only writes to a file.
- 修正建议: Train models to recognize broader context like method length and control structure diversity.；Incorporate data flow analysis to differentiate file selection from file I/O.；Use contrastive learning with hard negatives that have lexical overlap but different semantics.

### case_id=4877 FP lexical_or_api_overlap

- 方法: `actionPerformed` vs `_checkLanguagesFiles`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.98`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Handles multiple UI action commands (GRAPHVIZ, IMAGEMAGICK, etc.) by opening file choosers and updating preferences and UI components.
- B 摘要: Checks for language-specific property files and copies them if they do not exist, using file channels.
- 静态失败原因: The model likely focused on superficial structural similarities (e.g., both contain file handling operations, use File objects, have loops/conditionals) and ignored the semantic context and overall purpose. The high-level action names and API calls differ but some token overlap (e.g., 'File', 'getAbsolutePath', 'Suku') could mislead the model.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labeled non-clone because these functions serve entirely different purposes: one is a UI event handler for settings, the other is a backend file management method. They share no meaningful functional overlap.
- 行为差异: A processes UI events and updates GUI state, B manipulates language files for a web portal.；A handles multiple distinct commands with file choosers, B iterates over a list of languages and copies files.；A uses JFileChooser and UI components, B uses file I/O with channels.；A writes preferences and updates UI elements, B only ensures file existence and copies.
- 修正建议: Improve training with harder negative examples that share API calls but differ in intent.；Incorporate broader context like method signatures and surrounding class structure.；Use contrastive learning that emphasizes overall function semantics over local token matches.

### case_id=4878 FN partial_functionality

- 方法: `executeHttpGet` vs `invoke`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Executes an HTTP GET request to a given URI and returns the response body as a JSONObject.
- B 摘要: Invokes a remote method via HTTP POST, handles retries on timeout and returns the deserialized response object.
- 静态失败原因: Low token overlap (0.1636) and differences in control flow, error handling, and input types caused the model to miss the underlying semantic similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB considers them clones because the core functionality (making an HTTP request and parsing JSON) is semantically similar, even though the implementation details differ.
- 共享行为: Both functions perform an HTTP request and read the response；Both parse the response body as JSON
- 行为差异: HTTP method: GET vs POST；Input: URI string vs MethodInvocation object；Error handling and retries present only in B；Return type: specific JSONObject vs generic Object
- 修正建议: Improve model's ability to recognize core behavior despite different wrappers；Use dataflow analysis to capture common operations like HTTP request, response reading, and JSON parsing

### case_id=4879 FN benchmark_preference_bias

- 方法: `extractZipFile` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Extracts a zip file by reading entries and writing them to disk, updating a progress text component.
- B 摘要: Launches a NexOpen project by validating configuration, processing pom.xml files, setting up Hibernate dialect, and running a build action.
- 静态失败原因: The static model likely predicted non-clone because the token overlap is very low and the functions are from different contexts. The model correctly identified they are not semantically equivalent. The failure is due to BCB label being incorrect, not a model error.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as clone due to both methods involving file I/O and stream handling, and perhaps both have a similar structure of opening resources, processing, and closing. However, the semantics are completely different. Possibly BCB's annotation guidelines are broad and consider 'similar functionality' at a high level like 'handling files'? But that seems unlikely.
- 共享行为: Both perform file-related operations using streams.
- 行为差异: Function A extracts a zip archive; Function B configures and builds a Maven project.；Function A has a simple loop over zip entries; Function B has complex conditional logic with multiple file existence checks.；Function A uses JTextPane for progress; Function B uses IProgressMonitor and Eclipse APIs.；Function B involves Eclipse plugin specific types while A uses standard Java I/O.
- 修正建议: Re-evaluate BCB label for this pair; they are not clones even under broad Type-4.；Improve training data by removing or correcting mislabeled pairs.；Consider that static models may be more accurate than BCB annotations in some cases.

### case_id=4880 FN benchmark_preference_bias

- 方法: `modifyApplicationMessage` vs `copy`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Modifies or creates a locale-specific properties file by copying from an English template and updating a message entry.
- B 摘要: Copies a file from source to destination using a byte buffer.
- 静态失败原因: The static BERT model correctly identified the functions as non-clones based on low lexical overlap and different control flow. Its 'failure' reflects disagreement with a questionable BCB label.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB likely considered the file-copy sub-operation in A as sufficient for a Type-3/4 clone label, but the overall functionality is too distinct.
- 共享行为: Both involve file I/O operations (reading and writing files).
- 行为差异: A performs conditional file copy and line-by-line properties modification; B is a straightforward file copy.；A uses character streams and handles multiple file paths; B uses byte streams and is generic.；A is specific to localization properties; B is a general-purpose utility.；A catches exceptions and prints stack trace; B throws exceptions.
- 修正建议: Re-evaluate BCB labels for pairs with low token similarity and distinct core functionality.；Remove or correct this pair in the benchmark to avoid misleading evaluation.；Use stricter clone definitions requiring substantial semantic equivalence.

### case_id=4881 FN benchmark_preference_bias

- 方法: `getFile` vs `addFileToTarGz`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies its soap:address endpoint, and saves it to a temporary directory.
- B 摘要: Recursively adds files or directories to a tar.gz archive output stream.
- 静态失败原因: Static BERT did not fail; it correctly predicted non-clone. The BCB label appears to be a false positive, possibly due to annotator bias towards file-handling functions.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled these as clones based on broad Type-4 similarity (both perform file I/O operations) or due to annotator oversight, as the functions have very different purposes.
- 行为差异: A downloads and modifies XML; B archives files.；A uses URL and HTTP connection; B uses TarArchiveOutputStream.；A modifies XML attributes; B does no XML processing.；A returns a file path string; B is void.
- 修正建议: Use stricter semantic analysis to avoid false positive clones from BCB.；Incorporate more structural and functional similarity measures.；Re-evaluate BCB annotations for low token similarity pairs.

### case_id=4882 FP boilerplate_overlap

- 方法: `actionPerformed` vs `WebmillDeploy`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Handles ActionEvent to set paths for external tools (Graphviz, ImageMagick) and update application preferences.
- B 摘要: Constructor that deploys a web application by parsing WAR file XML and creating a new WAR with modified descriptors.
- 静态失败原因: The model likely overemphasized structural similarities (nested try-catch, file handling) and ignored the distinct APIs and overall goals due to long-range semantics and boilerplate overlap.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would not consider these clones because the methods serve entirely different purposes with no shared functionality, despite some boilerplate overlap.
- 共享行为: Both use file I/O operations；Both employ try-catch-finally exception handling；Both update some configuration or output state
- 行为差异: Function A is event-driven UI interaction; B is a batch processing constructor；A deals with user preferences and UI components; B deals with JAR/WAR file transformation；A uses JFileChooser and text fields; B uses JarFile, XML parsers, and FileChannel
- 修正建议: Enhance training with functionally diverse examples that share boilerplate；Incorporate API usage features or call graph information；Use hierarchical attention or curriculum learning to focus on critical operations

### case_id=4883 FP lexical_or_api_overlap

- 方法: `doRawRequest` vs `loadURL`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Sends a POST request to a fixed URL and returns the response body as a string.
- B 摘要: Downloads content from a given URL with optional basic authentication, saves it to a temporary file, and updates a UI label with progress.
- 静态失败原因: Static BERT models may rely heavily on lexical and API overlap (e.g., URLConnection, BufferedReader, readLine) and miss the critical differences in output handling, authentication, and UI interaction. The structural and semantic variations are not captured by token-level similarity alone.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the overall functionality and side effects differ significantly: one is a simple POST request returning a string, the other is a file download with authentication and UI feedback. The shared URL reading pattern is too small relative to the differences.
- 共享行为: Both open an HTTP URL connection and read the response line by line using BufferedReader.
- 行为差异: A uses POST by setting doOutput and writing data; B uses GET (default) without writing request body.；A returns the concatenated response as a String; B writes each line to a temporary file and does not return anything.；B handles basic authentication and updates a JLabel with file size; A does not.
- 修正建议: Incorporate dataflow analysis to track return values vs. side effects (e.g., file writes, UI updates).；Use control flow to distinguish POST vs. GET patterns.；Add attention to exception handling and method signatures (return type, parameters).

### case_id=4884 FN partial_functionality

- 方法: `login` vs `runScript`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Logs into LOLA by sending email and password via HTTP POST and returns session ID.
- B 摘要: Reads the content of a script from a URL via HTTP GET and returns it as a string.
- 静态失败原因: Low lexical overlap (Jaccard 0.169) and different method names, URL construction (URLEncoder vs getCodeBase()), and control flow (while loop vs readLine) caused the model to miss the abstract similarity of network fetching.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB considers them clones because both are functions that fetch data from a remote URL and return a string, matching a common high-level pattern (Type-4 semantic clone).
- 共享行为: Both perform network I/O via URL connections and read input streams.；Both return a string, handling exceptions by returning an empty or error string.
- 行为差异: Different HTTP methods (POST vs GET) and URL construction.；Different data extraction: A extracts sessid from first line, B concatenates bytes to string.；Different default return values ("" vs "error!").
- 修正建议: Train with more examples of semantically similar but lexically diverse functions.；Incorporate features like API call sequences (e.g., URL.openConnection, InputStream) and data flow patterns.

### case_id=4885 FN partial_functionality

- 方法: `getJSONData` vs `read`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.65`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches JSON from a URL using HttpClient and parses it into a JSONObject, returning the JSONObject or null on failure.
- B 摘要: Opens a buffered input stream from a URL or file path and delegates to another read method, returning an integer status code.
- 静态失败原因: Static BERT/GraphCodeBERT models rely heavily on lexical and structural features such as token overlap, method names, and API usage. The low token Jaccard (0.129), different return types, and different libraries (HttpClient vs. URL) caused the model to miss the broader semantic similarity in the data retrieval pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely labels this as a Type-4 semantic clone because both functions perform network I/O to retrieve data from a URL and handle exceptions, representing a similar high-level intent despite different detailed implementations and return types.
- 共享行为: Both functions handle I/O from a URL source；Both include try-catch for exception handling；Both involve reading data from an external source
- 行为差异: A returns a parsed JSONObject, B returns an integer status；A uses Apache HttpClient, B uses URL.openStream or FileInputStream；A only handles URLs, B handles both URLs and file paths；A parses JSON, B does not parse content
- 修正建议: Incorporate data flow analysis to capture shared I/O operations；Abstract return types to consider high-level intent；Use graph representations that connect external resource access patterns

### case_id=4886 FN partial_functionality

- 方法: `getWebPage` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.5`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a URL's content line by line and returns it as a single string.
- B 摘要: Sends a POST request to the RenRen API with specific parameters and prints the response.
- 静态失败原因: Static BERT or GraphCodeBERT models rely on token similarity and structural context. The low token Jaccard (0.098) indicates little lexical overlap. The models may have missed the shared high-level concept of reading web content because of the very different API calls (URL.openStream vs HttpURLConnection) and the presence of many unique tokens in code B (RenRen constants, PostParameter, etc.). The models likely classified these as non-clones due to low surface similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have considered both as 'web page retrieval' tasks due to the pattern of opening a URL and reading lines, despite different HTTP methods and output handling. They might have focused on the shared I/O pattern while overlooking the differing setup and return/print behavior.
- 共享行为: Both open a URL connection and read the response line by line using BufferedReader；Both handle I/O (though A throws Error, B throws IOException)
- 行为差异: A returns the page content; B prints to stdout and does not return；A uses URL.openStream() (GET implicit); B uses HttpURLConnection with POST method；A has minimal setup; B builds many PostParameters；A throws Error on exception; B declares IOException
- 修正建议: Improve model ability to recognize functional patterns despite different API choices (e.g., using URL.openStream vs HttpURLConnection)；Incorporate more semantic representation of I/O operations and HTTP methods；Use program slicing or abstract syntax trees to capture core data flow (reading from URL) rather than exact tokens

### case_id=4887 FP lexical_or_api_overlap

- 方法: `sendRequestObjectResponse` vs `loadURL`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Sends an XML request to a server via HTTP, saves the response to a file based on content type, and opens the file in a browser, returning the file path.
- B 摘要: Downloads content from a URL with optional basic authentication, writes it to a temporary file, and updates a status label with download progress; returns void.
- 静态失败原因: Static BERT may have been misled by similar API usage (URLConnection, streams) and structural patterns (open, read/write, close) common in network I/O code, without capturing the different intent and data flow.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels these as non-clones because they perform different high-level tasks: one is a request-response operation with file saving, the other is a download with progress tracking. The low token Jaccard and differing method signatures support this.
- 共享行为: Both open a URLConnection and write response to a file；Both use input/output streams for data transfer；Both include error handling with printStackTrace
- 行为差异: A sends XML data with compression; B only reads without sending data；A returns the file path; B is void；B supports basic authentication; A does not；A saves to a specific directory under OSRoot; B saves to a temporary file
- 修正建议: Include data flow analysis to distinguish send vs receive；Add control flow or semantic features like method return type；Augment with comments or documentation embedding

### case_id=4888 FP lexical_or_api_overlap

- 方法: `getLinksFromURLFast` vs `executePost`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Extracts hyperlinks and link text from a web page given a URL using regex.
- B 摘要: Sends an HTTP POST request with parameters and returns the response body as a string.
- 静态失败原因: Static models like GraphCodeBERT may rely heavily on overlapping API sequences (URL, openConnection, BufferedReader, StringBuffer) and structural patterns (while read loop) without deeply understanding the overall goal, leading them to overestimate similarity.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB annotation typically requires functional equivalence or near-equivalence in purpose. These two functions have entirely different objectives (link extraction vs. POST execution) so they are correctly labeled as non-clones.
- 共享行为: Both use URL to open a connection to a web resource；Both read the response stream using BufferedReader and append lines to a StringBuffer；Both involve basic HTTP communication boilerplate
- 行为差异: Function A parses HTML to extract links and texts; function B does not parse output at all；Function A only uses GET (default); function B explicitly uses POST method；Function A returns two Vectors; function B returns a String；Function A includes timing/debug statements; function B includes exception handling and cleanup
- 修正建议: Train on more diverse examples of non-clone pairs with similar boilerplate but different purposes；Incorporate dataflow analysis to distinguish between output data transformations (extract links vs. return response string)；Add attention to high-level semantics like method names and return types

### case_id=4889 FN lexical_or_api_overlap

- 方法: `addQDInformation` vs `httpRequestByPOST`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads local or remote QD info file and updates internal project information structures.
- B 摘要: Performs an HTTP POST request and returns the response body as a string.
- 静态失败原因: Static BERT may have been misled by overlapping API usage (BufferedReader, InputStreamReader) and similar control flow patterns (try-catch, while loop), ignoring the distinct high-level purposes.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB might have labeled it as clone due to broad Type-4 similarity based on shared I/O patterns and exception handling, but the functionalities are too different for typical BCB annotation.
- 共享行为: Both read input line by line using BufferedReader；Both handle IOException
- 行为差异: A reads from file or URL, B sends HTTP POST；A updates internal state, B returns a string；A parses lines for specific prefixes, B appends all lines；A has conditional local/remote logic, B handles HTTP status codes
- 修正建议: Incorporate data flow analysis to distinguish write vs return；Use higher-level semantic embeddings that capture method purpose；Add context-aware features like method name and return type

### case_id=4890 FN partial_functionality

- 方法: `populateResources` vs `seeURLConnection`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Loads templates and images from URLs and saves them as resources.
- B 摘要: Opens a URL connection to a fixed address and reads its content into a string for logging.
- 静态失败原因: Low token Jaccard (0.149) and different method names/structures likely caused the model to miss the shared I/O idiom, as the overlap is small compared to total code size.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider the identical reading pattern (openStream, BufferedReader, readLine, StringBuffer) as sufficient functional similarity, accepting a broad Type-3/Type-4 clone despite different overall purposes.
- 共享行为: Both open a URL stream and read lines using BufferedReader into a StringBuffer.
- 行为差异: A loads multiple templates and images, saving them as persistent resources; B simply reads one URL and logs the content.；A handles file filtering by extension and loops over multiple URLs; B uses a single hardcoded URL.；A catches specific exceptions; B throws Exception.
- 修正建议: Encourage models to recognize common I/O patterns via subgraph matching or code summarization.；Add training examples that capture partial functionality clones with low lexical overlap.

### case_id=4891 FN boilerplate_overlap

- 方法: `getFile` vs `encodeFileToFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies it by updating an endpoint attribute, and returns the local file path.
- B 摘要: Reads a file, Base64-encodes it, and writes the encoded data to another file, returning success boolean.
- 静态失败原因: The static BERT model likely focused on token-level differences (low Jaccard 0.145) and recognized the distinct domain-specific terms (AxisFault, WSDL, Base64) leading to a non-clone prediction. It did not consider high-level structural similarity of file I/O boilerplate, which BCB may have considered sufficient for a Type-4 clone.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may have labeled this as a clone because both functions are file-to-file transfer operations with similar boilerplate (open stream, read, write, close) and both involve file I/O, which could be considered a Type-4 clone under a very broad category of 'file copy with transformation'.
- 共享行为: Both perform file I/O operations (reading from a source and writing to a destination).；Both use InputStream and OutputStream.；Both have try-catch-finally or similar exception handling patterns.
- 行为差异: Function A downloads from a URL and involves XML parsing and manipulation; Function B does not.；Function A writes to a temporary directory and modifies the file; Function B encodes the content.；Function A returns a file path; Function B returns a boolean.；Function A handles multiple exceptions; Function B only catches IOException.
- 修正建议: Incorporate structural similarity features beyond token overlap.；Use data flow analysis to capture common patterns of stream usage.；Train on examples where boilerplate code dominates to learn that shared I/O patterns are not enough for clone detection without shared semantics.

### case_id=4892 FN partial_functionality

- 方法: `fileDownload` vs `PageLoader`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a file from a URL and saves it to a local file.
- B 摘要: Reads the entire content of a web page from a URL into a string.
- 静态失败原因: The model likely focused on the low lexical overlap (token Jaccard 0.207) and structural differences in output handling (FileOutputStream vs string concatenation), missing the shared core of URL opening and data reading. It may not capture high-level semantic similarity across different APIs.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider these clones because both functions fundamentally retrieve content from a URL via HTTP, which is a common pattern. The difference in output handling (file versus string) is often treated as superficial in broad clone detection.
- 共享行为: Open a URL connection；Use BufferedReader to read data from the URL
- 行为差异: A writes data to a file, B stores data in a string；A reads byte by byte using read(), B uses readLine() with ready() check；A handles exceptions with logging, B throws Exception
- 修正建议: Enhance training with more Type-4 semantic clones that share intermediate data flows；Incorporate graph-based representations to capture common dataflow patterns (URL -> read -> output, regardless of output sink)；Use contrastive learning to emphasize semantic similarity despite low token overlap

### case_id=4893 FP lexical_or_api_overlap

- 方法: `readUNI` vs `wordFrequency`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads tab-separated descriptions from a URL and adds them to a vector.
- B 摘要: Fetches a webpage, searches for a pattern matching a word, and returns the frequency if found.
- 静态失败原因: The model likely over-relied on lexical and structural similarities (e.g., URL, openStream, while loop, exception handling) and failed to capture the semantic difference in return type and overall task.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clone because the functions have distinct purposes and outputs, despite sharing some structural boilerplate.
- 共享行为: Both open a URL and read data from it.；Both use try-catch for exception handling.；Both read input line by line.；Both parse lines to extract specific information.
- 行为差异: Function A populates a vector with description strings; Function B returns an integer frequency.；Function A expects a tab-separated format; Function B uses regex pattern matching.；Function A consumes a source URL directly; Function B constructs URL by replacing a placeholder.；Function A ignores the first line; Function B does not.
- 修正建议: Incorporate dataflow analysis to track how input/output types affect behavior.；Add attention to function signatures and return types.；Use contrastive learning to distinguish tasks with similar boilerplate but different semantics.

### case_id=4894 FP lexical_or_api_overlap

- 方法: `run` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Performs an authenticated HTTP GET request, reads the entire response as a string, and signals completion.
- B 摘要: Performs an HTTP GET request to Google Images for album art, parses the HTML to extract image URLs, and stores them in a list.
- 静态失败原因: The model likely focused on the structural similarity (HTTP connection, BufferedReader, while loop) and common API calls, ignoring the semantic differences in authentication, HTML parsing, and overall purpose. The high token overlap in boilerplate code may have misled the embedding.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely considered these non-clones because the core functionality (authenticated generic HTTP fetch vs. Google image search with HTML parsing) is distinct. The shared HTTP GET boilerplate is not sufficient for clone labeling in BCB's broad Type-3/Type-4 criteria.
- 共享行为: Both open HTTP connections using HttpURLConnection；Both read response line by line with BufferedReader and InputStreamReader；Both use try-catch for error handling
- 行为差异: A includes Basic authentication header; B does not；B parses HTML to extract image URLs; A simply stores the whole response；A updates a timestamp during reading; B does not；A catches Throwable; B catches Exception and shows a dialog
- 修正建议: Incorporate method-level context (e.g., method name, surrounding class) to disambiguate purpose；Use dataflow analysis to capture differences in post-processing of response data；Train on more diverse pairs to avoid overreliance on common API sequences

### case_id=4895 FN partial_functionality

- 方法: `addIDs` vs `readGeoParserResult`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Adds chemical compound IDs to a PeakListRow by querying a metabolite database via URL and parsing HTML response.
- B 摘要: Reads geographic place names and gazetteer IDs by querying a geo-parser service via URL with XML requests and parsing XML responses.
- 静态失败原因: The models rely heavily on token and structural overlap, which is very low (Jaccard 0.123). The different domains, method names, and API calls obscure the shared abstract pattern of URL fetching and parsing.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considers both as Type-4 clones because they share a common high-level behavioral pattern: 'retrieve data from a URL and parse it to extract identifiers', which is a recognized functional category in BigCloneBench.
- 共享行为: Make HTTP requests to external services；Read response line by line using BufferedReader；Parse response (HTML or XML) to extract ID strings；Handle exceptions with try-catch and logging
- 行为差异: Domain: chemical metabolite IDs vs. geographic place names；Parsing: HTML string splitting vs. XML DOM using DocumentHelper；Return type: int score vs. Collection<Tuple<String, ArrayList<String>>>；Side effect: modifies input row object vs. purely functional return
- 修正建议: Augment training data with Type-4 clones that have low lexical overlap but similar control-flow and I/O patterns.；Incorporate data-flow analysis to detect URL connection and response parsing sequences.；Use graph-based models that can capture the structure of while loops and try-catch blocks regardless of variable names.；Apply contrastive learning to bring embeddings of functions with similar external interaction patterns closer.

### case_id=4896 FN benchmark_preference_bias

- 方法: `main` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Parses command line arguments to determine file paths and character encodings, reads an input file, and writes the content to an output file with the specified encoding.
- B 摘要: Launches a NexOpen project by processing Maven pom.xml files, configuring Hibernate dialect, and performing reverse engineering file setup within an Eclipse launch configuration.
- 静态失败原因: Static BERT/GraphCodeBERT did not fail; it correctly predicted non-clone. The static model succeeded in distinguishing the two functions.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB likely mislabeled as clone due to superficial similarity in exception handling and file operations, but the overall functionality is completely different.
- 共享行为: Both involve file I/O operations
- 行为差异: Function A is a standalone command-line utility for file encoding conversion；Function B is an Eclipse plugin launch handler for project configuration and Maven setup；Different frameworks: A uses standard Java I/O, B uses Eclipse and Maven APIs；Different error handling: A prints stack traces, B throws runtime exceptions
- 修正建议: Review BCB ground truth labels for this pair to correct the mislabeling；Consider adjusting clone detection threshold to avoid false negatives from benchmark bias

### case_id=4897 FP boilerplate_overlap

- 方法: `sendPost` vs `fetchUrl`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Sends an HTTP POST request with a parameter and returns the response body as a string.
- B 摘要: Fetches the content of a URL via HTTP GET and returns it as a string.
- 静态失败原因: The model was misled by high lexical overlap (URL, BufferedReader, readLine) and similar structure, missing the implicit difference in HTTP method (openConnection vs openStream) and the presence/absence of output writing.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled as non-clone because the functions have different HTTP methods (POST vs GET) and different parameter counts, leading to different core functionality despite shared boilerplate.
- 共享行为: Both open a URL connection and read the response line by line using BufferedReader.；Both return the concatenated response as a string.；Both catch exceptions and return an empty string on failure.
- 行为差异: Method A uses POST and sends a parameter; method B uses GET with no parameters.；Method A sets a request header and explicit I/O modes; method B does not.；Method A uses PrintWriter to write the parameter; method B does not write anything.；Error handling differs: A catches Exception and displays a message; B catches specific exceptions silently.
- 修正建议: Incorporate understanding of HTTP method semantics (e.g., differentiate openConnection from openStream).；Add data-flow analysis to track whether parameters are sent to the output stream.；Use more context or API-specific knowledge to distinguish POST from GET.

### case_id=4898 FN boilerplate_overlap

- 方法: `modifyApplicationMessage` vs `execute`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Modifies a locale-specific properties file by updating or adding a message key-value pair.
- B 摘要: Reads a source file and writes its content to a destination file after applying a conversion process.
- 静态失败原因: Static BERT models rely heavily on token-level similarity; the high overlap of common Java I/O tokens (FileReader, FileWriter, try, catch, e.printStackTrace) and similar control flow structures led to a false negative.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may have labeled this as a clone due to the shared boilerplate of file reading/writing and exception handling, which could be seen as partial functionality similarity (Type-4) under a very broad interpretation.
- 共享行为: Both use FileReader and FileWriter for file I/O.；Both handle exceptions with e.printStackTrace().；Both close file streams in try-catch-finally blocks.
- 行为差异: Function A edits properties files for internationalization; Function B performs file conversion.；Function A manipulates key-value pairs with custom logic; Function B delegates conversion to another method.；Function A creates files if not exist; Function B relies on parent directory creation.；Function A uses BufferedReader and StringBuilder; Function B uses only FileReader and Writer.
- 修正建议: Incorporate structural features like AST or control flow graph distances.；Train with contrastive learning to distinguish between functional core and boilerplate.；Use data flow analysis to capture semantic differences in variable usage.

### case_id=4899 FN benchmark_preference_bias

- 方法: `upload` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Copies an image file to a fixed destination using IOUtils.copy and returns a string.
- B 摘要: Launches an Eclipse NexOpen project by validating configuration, processing pom.xml files, setting Hibernate dialect, and scheduling an install job.
- 静态失败原因: The model correctly predicted non-clone due to very low token overlap (Jaccard 0.046) and structural differences; it did not fail but rather aligns with our analysis.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled these as clones due to both methods containing IOUtils.copy and exception handling, leading to a superficial Type-4 similarity annotation.
- 共享行为: Both methods perform file I/O operations using IOUtils.copy.；Both handle exceptions with printStackTrace or logging.
- 行为差异: Method A is a simple file copy, while B is a complex multi-step configuration launch.；A uses FileInputStream/FileOutputStream, B uses ByteArrayOutputStream, IFile, Document, and XML handling.；A returns a fixed string "show", B returns void.；A is a web upload action, B is an Eclipse plugin launch configuration for a specific framework.
- 修正建议: Re-evaluate BCB annotations for pairs with low lexical overlap to ensure consistency.；Incorporate domain-specific knowledge to avoid over-generalizing I/O utility usage.；Use fine-grained semantic analysis to distinguish between simple file operations and complex project configuration.

### case_id=4900 FN partial_functionality

- 方法: `copyResource` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource (URL or file) to a destination file using byte-by-byte stream I/O; throws exception on failure.
- B 摘要: Copies a file using NIO FileChannel.transferFrom; returns boolean success and logs exceptions.
- 静态失败原因: The low token Jaccard (0.123) indicates low lexical overlap. Static BERT models rely on surface token similarity and cannot abstract away different API implementations (stream vs. channel) and error handling patterns, leading to a false negative prediction.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB considers this a clone because both functions achieve the same high-level goal: copying a file/resource to a destination. Despite differences in I/O API and error handling, they are functionally similar (Type-3/4) and are labeled as clones in benchmark.
- 共享行为: Both copy data from a source to a destination file.；Both use file output streams to write the destination.；Both close input and output resources after copying.
- 行为差异: A uses InputStream/OutputStream byte-by-byte copy; B uses FileChannel.transferFrom for bulk transfer.；A reads from a URL or a file; B reads only from a file.；A throws Exception on failure; B returns false and logs the exception.；A has no return value; B returns a boolean indicating success.
- 修正建议: Train models to recognize high-level semantic equivalence by using dataflow or program dependency information.；Augment training data with diverse I/O patterns and error handling styles.；Use contrastive learning to push representations of functionally similar but lexically different code closer.

### case_id=4901 FN partial_functionality

- 方法: `doTransfer` vs `callApiPost`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Forwards an incoming HTTP request to another URL, copying headers and body, and relays the response back.
- B 摘要: Sends a POST request to a given API with specified parameters and headers, and returns the response stream, throwing an exception on unexpected status.
- 静态失败原因: The token Jaccard similarity is low (0.246), and the methods differ in naming, control flow, and error handling, causing a BERT-based model to miss the underlying structural similarity in HTTP connection setup.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider these as clones because both are HTTP client methods that send a request and process a response, falling under a broad category of 'HTTP request handling' with Type-4 similarity.
- 共享行为: Both open an HTTP URL connection using HttpURLConnection.；Both set request headers and output mode.；Both write a request body to the connection output stream.；Both read the response input stream.
- 行为差异: A receives the source request from HttpServletRequest; B directly takes URL and parameters map.；A copies headers from the incoming request; B uses a fixed set of headers from a member field.；A reads the body from the incoming request's input stream; B constructs the body from a parameters map.；A supports any HTTP method via parameter; B is hardcoded to POST.
- 修正建议: Include dataflow analysis to capture the shared sequence of opening connection, setting headers, writing body, reading response.；Use graph-based models that abstract over specific variable names and method signatures.；Leverage large language models fine-tuned on clone detection for better robustness to variable renaming and structural variations.

### case_id=4902 FN benchmark_preference_bias

- 方法: `doGet` vs `fetchURLData`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.5`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Handles HTTP GET requests for a portal page, fetching page data based on parameter, checking visibility, caching, and logging.
- B 摘要: Fetches data from a given URL via HTTP or file protocol, returning the content as a byte array.
- 静态失败原因: Low token overlap (0.069) suggests no lexical similarity; static model may have missed semantic essence due to long-range dependencies in code_a (truncated) and different API usage; possibly trained on biased BCB labels.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider both as 'HTTP-related' or 'network I/O' at a very broad level, but functionally they are very different; likely a labeling error or bias towards high-level similarity.
- 共享行为: Both involve HTTP protocol handling；Both handle input parameters (request parameter vs URL)；Both may deal with network I/O
- 行为差异: A is a void servlet method that writes response to an HttpServletResponse, B is a utility that returns raw bytes；A involves page-specific logic (visibility, caching, logging), B is generic URL fetching；A uses HttpServletRequest/Response, B uses HttpURLConnection；A has complex error handling for page not found, forbidden; B has basic IOException
- 修正建议: Improve model to consider deeper semantic and dataflow context；Filter out pairs with very low token overlap and high behavioral differences；Use graph-based or dataflow representations to capture actual I/O and control flow

### case_id=4903 FN benchmark_preference_bias

- 方法: `copyFile` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Copy a file from input to output using FileChannel transfer.
- B 摘要: Launch a NexOpen project configuration by processing pom.xml files, setting Hibernate properties, and managing project resources.
- 静态失败原因: The model correctly predicted non-clone due to low token overlap and different structure; the error is a benchmark labeling bias.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB annotators may have considered both as utility methods that involve file operations, but this is too broad and likely a labeling error.
- 共享行为: Both perform file I/O operations.
- 行为差异: Function A is a simple file copy; Function B is a complex multi-step launch procedure.；Function A uses FileChannel; Function B uses ByteArrayOutputStream, XML parsing, and project resource handling.；Function A has no dependencies; Function B depends on Eclipse/Java development APIs and external libraries.
- 修正建议: Re-examine BCB label for this pair; it should be non-clone.；Improve annotation guidelines to avoid overbroad similarity judgments.

### case_id=4904 FP partial_functionality

- 方法: `actionPerformed` vs `unzip`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Handles GUI action events to set various preferences and update UI components.
- B 摘要: Extracts a zip file by reading its entries and writing them to the filesystem.
- 静态失败原因: The model may have been misled by the presence of common API calls like File and BufferedInputStream in both functions, or by the similar structure of conditionals and loops, but it failed to capture the overall semantic purpose.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB annotates based on functional similarity; these functions have no common task (GUI event handling vs. file extraction), so they are clearly non-clones.
- 共享行为: Both functions perform file-related operations (A uses file chooser to get file path, B reads zip entries and writes files).；Both use conditional logic and loops (A has many if-else blocks, B has while loop).
- 行为差异: A is an event handler for a GUI preferences dialog, while B is a utility function for unzipping files.；A does not write to files; it reads file paths and stores preferences, while B writes file contents to disk.；A interacts with UI components and a controller, B does not have any UI interaction.；A has multiple branches for different commands, B has a single loop processing zip entries.
- 修正建议: Improve training data to include more diverse functional patterns.；Use type-aware embeddings or data flow analysis to distinguish file I/O operations from GUI event handling.；Incorporate method name and surrounding context (e.g., class name) to better disambiguate.

### case_id=4905 FP other

- 方法: `actionPerformed` vs `copy`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Handles GUI action events by opening file choosers, setting preferences, and updating UI components based on the command string.
- B 摘要: Copies the contents of a source file to a destination file character by character using FileReader and FileWriter.
- 静态失败原因: The low token Jaccard (0.0526) suggests the model did not rely on lexical similarity. The false positive may arise from the model overgeneralizing the 'File' and 'IOException' tokens, or from the truncated long method causing the model to miss the overall semantic context.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely labels non-clone because the functions are semantically unrelated: one is a GUI event handler with diverse operations, the other is a straightforward file copy utility. There is no partial functionality overlap.
- 共享行为: Both functions involve file operations (File class usage).
- 行为差异: A is an event-driven GUI method with complex conditional logic, while B is a simple static utility method.；A interacts with user via dialogs and updates preferences/UI; B performs pure file I/O without user interaction.；A has multiple branches for different commands; B has a linear flow.；A uses JFileChooser and SettingFilter; B uses FileReader/FileWriter.
- 修正建议: Incorporate structural features (e.g., AST, control flow) to distinguish GUI event handlers from simple utilities.；Use function signature and method name semantics more explicitly.；Apply thresholding on method length or complexity to avoid matching short helper functions with long event handlers.

### case_id=4906 FN partial_functionality

- 方法: `modifyApplicationMessage` vs `makeBackup`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Modifies a message in a locale-specific properties file by reading, editing, and writing the file.
- B 摘要: Creates a backup of files from a source directory to a destination directory, including setting timestamps.
- 静态失败原因: The models likely see low token overlap (0.212) and different method names/parameters, leading to low similarity scores. They may not capture the high-level semantic similarity of file copying due to lack of understanding of the context.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB annotators likely considered these clones due to shared file I/O operations and similar control flow (check existence, create, copy loop, catch Exception). The partial functionality of copying bytes from an input stream to output stream is common.
- 共享行为: Both perform file I/O with byte-by-byte copy loops；Both check file existence and create files/directories as needed；Both handle exceptions with e.printStackTrace()
- 行为差异: A modifies a single property in a properties file; B copies multiple files；A parses and rewrites lines in a properties file; B does not parse content；B sets file timestamps; A does not；Different parameters and overall goal
- 修正建议: Improve model's ability to recognize common sub-patterns like file I/O loops；Use graph-based representations to capture data flow of stream operations；Incorporate API call embeddings to better capture shared functionality

### case_id=4907 FP boilerplate_overlap

- 方法: `init` vs `executePost`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Loads controller classes from a registry file into a ServletContext.
- B 摘要: Executes an HTTP POST request to a given URL with parameters and returns the response string.
- 静态失败原因: Static BERT models may have focused on overlapping API calls (URL, InputStream, BufferedReader) and exception handling patterns, leading to a false positive due to boilerplate code similarity.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the two functions have completely different purposes and logic, despite some shared I/O boilerplate.
- 共享行为: Both use BufferedReader and InputStreamReader for I/O operations.；Both implement try-catch exception handling with logging.；Both open a URL or resource to read data.
- 行为差异: A reads class names from a file and loads them via reflection; B sends an HTTP POST request.；A is a void method for initialization; B returns a String from HTTP response.；A uses ServletContext and class loading; B uses HttpURLConnection for networking.
- 修正建议: Incorporate dataflow analysis to distinguish initialization from HTTP communication.；Use structural similarity focusing on control flow graphs or abstract syntax trees.；Consider method signatures and purpose via natural language comments or names.

### case_id=4908 FN partial_functionality

- 方法: `sendExceptionToServer` vs `load`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends an exception report to a server via HTTP POST with encoded parameters.
- B 摘要: Loads a document from pastebin.com via HTTP GET and returns its content.
- 静态失败原因: The low token overlap (0.215686) and different domain-specific words (exception, config, pastebin, etc.) caused the model to miss the common pattern of URL-based I/O. The model may have focused on lexical differences rather than structural similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considers these clones due to similar structure: establishing URL connection, reading/writing streams, exception handling, despite different purposes and data manipulation. This fits Type-3/4 broad clone category.
- 共享行为: Both open a URL connection；Both read from the connection stream；Both handle IOException with error logging/message；Both use java.net.URL, URLConnection, BufferedReader, InputStreamReader
- 行为差异: A sends data to server (POST), B fetches data from server (GET)；A builds complex query string, B uses simple ID in URL；A conditionally adds config and problem parameters, B does not；A writes to server output stream, B only reads
- 修正建议: Use AST-based or graph-based features that capture control flow and data flow patterns；Incorporate API usage sequences (e.g., URLConnection operations) as features；Consider method-level structural similarity beyond token overlap

### case_id=4909 FN partial_functionality

- 方法: `fetchUrl` vs `seeURLConnection`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads content from a given URL string and returns it as a string, with silent exception handling.
- B 摘要: Reads content from a hardcoded URL and logs it, throwing exceptions upward.
- 静态失败原因: Static models may misclassify due to low token Jaccard similarity (0.304), different method signatures, return types, and exception handling patterns, leading the model to focus on surface-level differences rather than the shared core logic.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB annotations often treat Type-3/Type-4 clones as positive, especially when the core algorithmic structure (open URL, read lines, concatenate) is identical, despite differences in signature, exception handling, or minor I/O details.
- 共享行为: Both create a URL object；Both open a stream/buffered reader from the URL；Both read lines and append them to a string buffer；Both close the reader
- 行为差异: fetchUrl accepts a URL string parameter; seeURLConnection uses a hardcoded URL；fetchUrl returns the content as a string; seeURLConnection is void and logs the content；fetchUrl catches MalformedURLException and IOException silently; seeURLConnection throws Exception；fetchUrl returns empty string on failure; seeURLConnection has no return on success or failure
- 修正建议: Enhance training with more diverse Type-3/Type-4 examples that vary in signatures and exception handling；Incorporate structural alignment or data-flow analysis to recognize shared patterns despite different variable names；Use contrastive learning to emphasize behavioral equivalence over lexical similarity

### case_id=4910 FN benchmark_preference_bias

- 方法: `doGet` vs `getProjectTreeData`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Servlet doGet method that processes HTTP GET requests for portal pages, handling page retrieval, access control, logging, and caching.
- B 摘要: Method that retrieves project tree data by downloading and parsing an XML file from a URL, then returning a 2D array.
- 静态失败原因: The model correctly identified low token overlap and lack of semantic similarity, but BCB's label was based on broad domain-level similarity, leading to the false negative.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled these as clones due to both being part of a web application and using HTTP, but the functional similarity is too weak; this is likely a mislabel.
- 共享行为: Both involve HTTP communication；Both handle exceptions
- 行为差异: A is a servlet handler; B is a data retrieval method；A processes user requests and generates HTML; B downloads and parses XML；A has complex page rendering and caching logic; B focuses on file I/O and XML parsing；Different data structures and outputs
- 修正建议: Re-evaluate BCB annotation for this pair；Use more strict functional similarity criteria；Train models to ignore superficial API overlap in favor of behavioral equivalence

### case_id=4911 FP lexical_or_api_overlap

- 方法: `main` vs `run`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Generates a JAR file of adapter classes from a Prolog program, using command-line arguments for file paths and debug mode.
- B 摘要: Copies input file to output file with optional diagnostic byte counting, using command-line arguments.
- 静态失败原因: Static models like CodeBERT rely heavily on token overlap; both functions share common tokens like 'args', 'File', 'IOException', 'System.out.println', and error handling idioms, causing overestimation of similarity despite different semantics.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels non-clones when functions have different high-level purposes, even if they share boilerplate patterns. Here, one is a code generator and the other is a file copier, so BCB correctly labeled non-clone.
- 共享行为: Both parse command-line arguments and handle invalid usage.；Both perform file I/O operations.；Both use standard Java libraries for file access and exception handling.
- 行为差异: A generates adapter classes and JAR file; B merely copies a file.；A involves complex code generation and visitor pattern; B uses simple stream pump.；A writes multiple class files and resources; B writes a single output file.；A uses reflection and classloading; B does not.
- 修正建议: Incorporate data-flow analysis to capture distinct program states and transformations.；Use control-flow graphs to differentiate file generation vs. file copy logic.；Leverage method names and import statements for semantic context.

### case_id=4912 FN partial_functionality

- 方法: `readRemoteFile` vs `fileDownload`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: reads a remote file from a static URL and returns its content as a concatenated string.
- B 摘要: downloads a file from a given URL to a local directory, writing bytes to a file.
- 静态失败原因: Static BERT likely focused on the low token overlap (Jaccard=0.1625) and method signature differences (return type, parameters), missing the high-level semantic similarity of reading from a URL. The model may not capture partial functionality or structural alignment in dataflow.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often considers functions that perform network I/O from URLs as similar, especially those sharing the pattern of opening a stream and reading via BufferedReader. The core similarity (reading from a URL) outweighs differences in output handling, leading to a Type-3/Type-4 clone label.
- 共享行为: Both open a URL and get an input stream via URLConnection.；Both use BufferedReader and InputStreamReader to read data.
- 行为差异: readRemoteFile returns a String; fileDownload writes to a file and returns void.；readRemoteFile reads line-by-line; fileDownload reads byte-by-byte using read().；readRemoteFile has no parameters and uses a static URL; fileDownload takes URL and destination directory as parameters.；Exception handling differs: readRemoteFile catches specific EOF and IO exceptions; fileDownload catches generic Exception.
- 修正建议: Incorporate structural alignment (e.g., AST subgraph matching) to detect shared sub-patterns.；Use contrastive learning with positive pairs from partial functionality overlap.；Improve representation of control flow and data dependencies, especially around I/O operations.

### case_id=4913 FN partial_functionality

- 方法: `copy` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a local file from one path to another by reading and writing byte chunks.
- B 摘要: Retrieves a resource by URL with caching, returning a local FileInputStream if cached, otherwise downloading and caching the resource.
- 静态失败原因: Static BERT/GraphCodeBERT models rely heavily on lexical and structural similarity; the token Jaccard is very low (0.12), and the functions differ greatly in length, complexity, and API usage. The model failed to abstract to the high-level similarity of reading and writing byte streams.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels pairs as clones if they share core functionality, even with different implementations. Both functions perform byte-level copying from a source to a file, which aligns with Type-4 semantic clone criteria.
- 共享行为: Reads bytes from an input source and writes them to an output file destination
- 行为差异: Function_a copies from a local file; function_b retrieves from a URL with caching logic；Function_a returns void; function_b returns an InputStream or null；Function_b includes HTTP handling, cache lookup, and multiple stream management；Function_b prints debugging output
- 修正建议: Use data-flow graphs or program dependence graphs to capture core I/O patterns；Integrate code summarization to match high-level intent；Train on examples of Type-4 clones with disparate surface forms

### case_id=4914 FP partial_functionality

- 方法: `main` vs `copyFileChannel`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Generates adapter classes from a Prolog file and writes them into a JAR.
- B 摘要: Copies a file using FileChannel, optionally preserving modification time.
- 静态失败原因: Static BERT may have been misled by common keywords (File, IOException, try-catch) and structural patterns, interpreting both as file manipulation functions despite very different high-level goals. Low token overlap (0.08) suggests the model might have relied on coarse-grained semantic embeddings that conflated file I/O operations.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely labels this as non-clone because the functionalities are completely different: one is a code generator and the other is a file copier. BCB emphasizes semantic similarity of the core purpose, not superficial patterns.
- 共享行为: Both involve file I/O operations；Both use try-catch or try-finally for resource management；Both handle exceptions
- 行为差异: Function A implements complex code generation and JAR building, while B simply copies file bytes；Function A uses many external libraries (Prolog parser, ASM, etc.), B only uses standard NIO；Function A is a main entry point with command-line parsing, B is a utility method；Function A writes many output artifacts, B writes only one output file
- 修正建议: Incorporate data flow analysis to distinguish between different sink operations；Use contrastive learning with harder negative examples that share boilerplate but differ in purpose；Add heuristics to detect when code is a main method vs. utility function

### case_id=4915 FN benchmark_preference_bias

- 方法: `login` vs `createHTML`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Logs into a service by sending an HTTP POST request and returns the session ID.
- B 摘要: Constructs an HTML page by reading a CSS file and optionally querying a database for dashboard content.
- 静态失败原因: The model correctly identified them as non-clones based on low token overlap and functional dissimilarity; the failure is due to a likely mislabeled ground truth in the benchmark.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: The BCB label may be an error; the functions are too functionally dissimilar to be considered even partial clones. The dataset might have mislabeled this pair due to superficial similarity in I/O usage.
- 共享行为: Both use I/O operations (BufferedReader, InputStreamReader) to read data.；Both handle exceptions with try-catch blocks.；Both return a String value.
- 行为差异: One performs authentication via HTTP POST, the other generates HTML using local resources and database queries.；One has no input parameters, the other takes a PAGE_TYPE enum.；One returns a session ID, the other returns an HTML string.；One involves network communication, the other is local resource loading and database access.
- 修正建议: Review and correct the ground truth label for this pair to reflect functional dissimilarity.；Improve consistency in benchmark annotations to avoid labeling unrelated functions as clones.

### case_id=4916 FP lexical_or_api_overlap

- 方法: `callService` vs `importSequences`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Opens a URL, reads the entire response line by line into a single string, and stores it in the 'answer' field.
- B 摘要: Opens a URL stream, parses sequences in FASTA-like format using ImportHelper, and populates 'names' and 'sequences' lists.
- 静态失败原因: Static BERT/GraphCodeBERT likely focused on lexical and API-level overlap (URL.openStream(), similar exception handling, try-catch structure) and missed the semantic differences in data processing. The model lacks sensitivity to the different purposes and the specific parsing logic, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels as non-clone because the functions perform fundamentally different tasks: one is a generic HTTP response fetcher, the other is a domain-specific sequence importer. Despite similar API usage, the output and processing logic are distinct, so BCB considers them not semantically equivalent even under broad Type-4 interpretations.
- 共享行为: Both open a URL stream in a try-catch block；Both handle MalformedURLException and IOException；Both read data from the stream
- 行为差异: callService reads all lines into a single StringBuffer; importSequences parses structured data into lists；callService uses BufferedReader; importSequences uses ImportHelper for specific format parsing；Different error handling: importSequences catches EOFException silently, callService returns error strings
- 修正建议: Incorporate dataflow or program dependence graphs to distinguish different data transformations；Train with more negative examples where API usage is similar but task semantics differ；Use structure-aware embeddings that capture loops and conditional logic beyond lexical tokens

### case_id=4917 FN benchmark_preference_bias

- 方法: `main` vs `readAndRewrite`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.4`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a URL and extracts its ZIP entries to local files.
- B 摘要: Reads a DICOM file, parses its metadata, and rewrites it to another file.
- 静态失败原因: Static BERT/GraphCodeBERT correctly predicted non-clone under strict semantic equivalence, but BCB's annotation reflects a preference for broad functional similarity that is not captured by the model's strict matching.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may label these as clones due to both being 'file processing' functions that involve reading, transforming, and writing data, which aligns with a broad Type-3/Type-4 functional similarity criterion.
- 共享行为: Both read data from an input source；Both write data to an output file；Both use buffered streams and handle I/O exceptions
- 行为差异: Input source differs: HTTP URL vs. local file；Data format differs: KMZ (ZIP) vs. DICOM；Processing logic differs: ZIP extraction vs. DICOM parsing and rewriting；Output structure differs: multiple extracted files vs. single output file
- 修正建议: Clarify annotation guidelines to distinguish between broad functional similarity and strict semantic cloning；Use domain-specific features to differentiate data formats；Train with more examples of dissimilar functions with superficial I/O similarity to reduce false positives from BCB-style annotation

### case_id=4918 FP lexical_or_api_overlap

- 方法: `main` vs `DecodeMapFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.99`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Main method that reads a Prolog file, parses it, and generates adapter classes and a lookup file.
- B 摘要: Method that decodes a map file by XORing each byte with a changing key and writes to output.
- 静态失败原因: The static BERT/GraphCodeBERT model likely overemphasized superficial lexical overlaps such as common API calls (e.g., FileInputStream, FileOutputStream, try-catch) and similar structural patterns (while loop, byte array), leading to a false positive despite vastly different semantics.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would label this as non-clone because the two functions have completely different purposes: one is a code generation tool, the other is a file decryption utility. They do not share any meaningful functional similarity.
- 共享行为: Both involve file I/O (reading and writing files).；Both have loops for processing data.；Both have error handling using try-catch blocks.
- 行为差异: Function A performs complex code generation and parsing; Function B performs simple XOR decryption.；Function A generates multiple outputs (jar, serialized data); Function B writes a single decoded file.；Function A uses many library-specific classes; Function B uses only basic Java I/O.
- 修正建议: Train on more diverse negative examples that have similar API usage but different overall functionality.；Incorporate higher-level semantic features such as data flow or program logic summaries.

### case_id=4919 FN benchmark_preference_bias

- 方法: `extractFile` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Extracts a single file from a zip input to an output file by copying bytes from an input stream to an output stream.
- B 摘要: Builds a website for editing by reading XML, performing XSLT transformations, processing multiple pages, reading control files, and writing transformed content to output files.
- 静态失败原因: A static BERT model likely over-relied on lexical overlap and structural similarity, which are very low (token Jaccard 0.05). The model correctly judged them as non-clones from a semantic perspective, but this contradicts the BCB label, which may be considered an annotation error or based on a broader, more permissive clone definition.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled these as clones due to superficial similarity in performing file I/O (reading from one source and writing to another) and both being categorized as 'data transformation' tasks, even though the complexity and logic are vastly different.
- 共享行为: Both involve reading from an input source and writing to an output file.
- 行为差异: Function A is a simple byte stream copy, while Function B involves complex XML processing, XSLT transformation, and multiple file operations.；Function B has extensive error handling, debugging, and iteration over pages, which Function A lacks.；Function A operates on a single file, while Function B processes a collection of pages with many parameters.
- 修正建议: Consider that the BCB label may be unreliable for this pair; incorporate behavioral similarity measures beyond lexical matching.；Use functional flow analysis to differentiate simple I/O from complex processing.

### case_id=4920 FN benchmark_preference_bias

- 方法: `testNetworkHTTP` vs `read`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Tests network connectivity by making multiple HTTP GET requests to predefined URLs and discarding the responses.
- B 摘要: Reads content from a given URL or file path by opening a stream and delegating to another read method, returning a status code.
- 静态失败原因: Low token Jaccard (0.136) and structural differences cause static models to miss the weak semantic similarity that the BCB annotator considered.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might have labeled this as a clone because both functions utilize HttpURLConnection or URL.openStream() to read from network URIs, focusing on the common web I/O pattern rather than specific logic.
- 共享行为: Both involve opening HTTP connections and reading input streams
- 行为差异: A makes multiple connections with hardcoded URLs, uses BufferedReader; B opens single stream based on parameter, uses BufferedInputStream and calls another read method；A discards lines, B processes via read; A has finally block to disconnect, B does not
- 修正建议: Incorporate API usage patterns as features；Use dataflow analysis to detect similar I/O operations；Fine-tune on BCB's broad annotations to capture Type-4 clones

### case_id=4921 FN partial_functionality

- 方法: `modifyApplicationMessage` vs `copy`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Modifies or adds a property in a locale-specific properties file, copying a template file if needed.
- B 摘要: Copies a file from source to destination using NIO channels.
- 静态失败原因: Static BERT/GraphCodeBERT models rely on token-level embeddings and structural patterns; the token Jaccard is low, and the overall semantics (property modification vs file copy) are distinct, leading to low similarity scores.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled this as a clone because both functions perform file copying as a key operation, and they consider functional similarity (Type-4) even if one function's primary purpose includes other tasks.
- 共享行为: Both functions involve copying a file from a source to a destination.
- 行为差异: Function A performs property file parsing, modification, and writing, while Function B only copies files.；Function A handles locale-specific file existence and creates missing files by copying a template.；Function B uses NIO memory-mapped buffer for efficient copy, while Function A uses traditional stream copy.；Function A includes error handling with exception printing, Function B declares IOException.
- 修正建议: Incorporate dataflow analysis to detect shared subroutines.；Use contrastive learning on subgraph patterns.；Evaluate clone detection at granularity of functional blocks rather than whole methods.

### case_id=4922 FN partial_functionality

- 方法: `getHTML` vs `wordFrequency`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches HTML from a URL and optionally writes it to a file.
- B 摘要: Computes word frequency by querying a web service and parsing the response.
- 静态失败原因: Low token Jaccard similarity and different method names/signatures cause static BERT to miss the shared web-fetching structure and semantic similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely classifies this as a clone due to similar control flow and I/O patterns (web access with line-by-line reading), which aligns with Type-3 or Type-4 clone definitions.
- 共享行为: Both open a URL connection to fetch web content.；Both read the response line by line using a BufferedReader.；Both handle I/O exceptions with try-catch.
- 行为差异: Function A builds a complete HTML string, while Function B searches for a specific pattern to extract an integer.；Function A optionally writes to a file, Function B does not.；Function A uses HttpURLConnection, Function B uses URL.openStream().；Function A returns a String, Function B returns an int.
- 修正建议: Use dataflow or control flow analysis to capture structural similarity.；Incorporate API usage patterns to identify common libraries.；Train on diverse semantic clone pairs to improve generalization.

### case_id=4923 FP lexical_or_api_overlap

- 方法: `readUNI` vs `downloadModel`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a tab-separated file from a URL and appends formatted entries to a vector.
- B 摘要: Downloads an RDF model from a URL using HTTP headers and returns the model.
- 静态失败原因: Static BERT/GraphCodeBERT models may have been misled by lexical and API overlap (e.g., 'URL', 'openStream', 'InputStream', 'MalformedURLException', 'IOException', 'finally' block). These common patterns in network I/O code trigger similarity signals despite different high-level semantics.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically treats two functions as clones only if they are functionally similar or share a significant portion of behavior. Here, despite similar boilerplate (URL opening, InputStream, exception handling), the core functionality differs: one parses TSV lines into a list, the other downloads an RDF model. The low token Jaccard (0.18) and different method names/purposes lead BCB to label it non-clone.
- 共享行为: Open a URL connection and get an InputStream；Handle MalformedURLException and IOException；Close the InputStream after use
- 行为差异: Function A parses TSV lines and modifies an input vector; Function B reads RDF data into a Model object and returns it.；Function A catches Exception broadly and prints stack trace; Function B catches specific exceptions and rethrows as RuntimeException.；Function A uses a Scanner with delimiter; Function B uses model.read() with no manual parsing.；Function A does not set HTTP headers; Function B sets Accept and Accept-Language headers.
- 修正建议: Incorporate data flow analysis to track how inputs/outputs are used (e.g., one returns a Model, the other modifies a Vector).；Use control flow graphs to distinguish parsing loops from model reading.；Train on more diverse examples to reduce reliance on common API sequences.

### case_id=4924 FP boilerplate_overlap

- 方法: `readData` vs `copy`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Parses multiple comma-separated string constants to initialize sets and a mapping for Tibetan character processing, including file reading logic.
- B 摘要: Copies a file from source to destination using NIO FileChannel with null checks and exception handling.
- 静态失败原因: The model likely overemphasized the shared IOException handling and static method signatures, missing the starkly different core functionalities. The truncation of A may also have caused the model to focus on local lexical patterns rather than the overall semantic intent.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would label as non-clone because the functions have entirely different purposes and implementation, despite some superficial I/O-related boilerplate.
- 共享行为: Both have static method signature；Both contain try-catch blocks for IOException
- 行为差异: A initializes data structures for character sets; B performs file I/O copying；A uses StringTokenizers and HashSets; B uses FileInputStream and FileChannel；A has complex conditional logic; B is straightforward sequential
- 修正建议: Incorporate global method-level semantics via dataflow analysis；Use method renaming or signature-aware models to discount common boilerplate；Train on diverse datasets to reduce reliance on superficial patterns

### case_id=4925 FN benchmark_preference_bias

- 方法: `fileDownload` vs `postXml`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `preference_memory_with_manual_audit`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a file from a URL and saves it to a local directory.
- B 摘要: Sends an XML POST request to a URL with SOAP action and returns the response as a string.
- 静态失败原因: The static BERT/GraphCodeBERT model likely relied on token overlap (low Jaccard) and structural differences (different method signatures, different control flow), failing to recognize the underlying common pattern of URL communication. It may not have learned the high-level behavioral similarity from limited training data.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB labels these as clones because both perform network I/O via URLConnection, reading from an InputStream, and the core pattern of opening a connection, reading data, and handling exceptions is similar. This falls under broad Type-3/Type-4 partial functionality similarity, focusing on the shared pattern of URL-based data transfer.
- 共享行为: Both involve opening a URLConnection to a remote server.；Both read from an InputStream obtained from the connection.；Both handle IOException and use similar try-catch structures.
- 行为差异: Function A writes the response to a file on disk; Function B returns the response as a string.；Function A performs a generic download (GET-like); Function B explicitly sets request method to POST and includes SOAP XML payload.；Function B sets HTTP headers (Content-Type, SOAPAction) and uses HttpURLConnection; Function A uses plain URLConnection without custom headers.；Function A reads byte by byte (int); Function B reads line by line and builds a StringBuilder.
- 修正建议: Augment training data with more examples of URL-based I/O operations that are functionally different but share the same pattern.；Use contrastive learning to emphasize pattern similarity over token overlap.；Incorporate control-flow or data-flow abstractions that capture network I/O patterns.

### case_id=4926 FN boilerplate_overlap

- 方法: `copyFile` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.7`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copy a file from source to destination with a given buffer size, optionally force overwrite.
- B 摘要: Build a website for editing by transforming XML pages and writing output files with file I/O operations.
- 静态失败原因: Static BERT models rely on token embeddings and may miss the structural I/O pattern due to low lexical overlap (token Jaccard 0.09) and different method names; they focus on local token similarity rather than the high-level I/O structure shared by the functions.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may label these as clones because both contain a common pattern of file I/O with buffer usage, which qualifies as Type-3/4 clone under BCB's broad criteria for functional similarity in file operations, even though the overall purpose differs.
- 共享行为: Both use FileInputStream to read files.；Both involve writing data to output files using FileOutputStream or similar.；Both use a buffer (byte[] or char[]) for reading/writing.；Both include logging statements (though different logging frameworks).
- 行为差异: copyFile copies a single file; buildSiteForEdit generates multiple output files from an XML site structure.；copyFile is a generic utility; buildSiteForEdit is specific to a CMS page transformation workflow.；buildSiteForEdit includes XML parsing, XSLT transformation, and string manipulation absent in copyFile.；copyFile handles overwrite logic with a force flag; buildSiteForEdit does not handle such conflict resolution.
- 修正建议: Incorporate data flow analysis to capture the I/O operations as a recurring pattern.；Use models that consider control flow or abstract syntax trees to identify structural similarities in resource handling.；Train on more diverse examples of file I/O clones to improve generalization.

### case_id=4927 FP lexical_or_api_overlap

- 方法: `writeFileToFile` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Copies a file from one location to another using NIO FileChannel.
- B 摘要: Handles action events to configure various settings (graphviz, imagemagick, etc.) and update UI and preferences.
- 静态失败原因: Static BERT methods may have been misled by lexical overlap (e.g., 'File', 'IOException', 'try', 'finally') or structural patterns despite low Jaccard similarity; the extreme length of function b may also cause poor representation.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically annotates clones based on functional similarity; since these functions share no common functionality, BCB correctly marked them as non-clones.
- 共享行为: Both involve file objects (FileInputStream/FileOutputStream vs JFileChooser and file paths)
- 行为差异: a is a simple file copy utility; b is a complex event handler with no file copying functionality
- 修正建议: Incorporate data-flow analysis to distinguish file copy from configuration handling；Use method-level semantic embeddings with length normalization

### case_id=4928 FN lexical_or_api_overlap

- 方法: `addIDs` vs `populateResources`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches metabolite data from a remote web service and updates a PeakListRow with various identifiers.
- B 摘要: Loads template resources and default images from classpath and saves them to a persistent storage.
- 静态失败原因: Static BERT models may rely heavily on token-level overlap and lexical patterns, and the presence of common API identifiers (URL, BufferedReader, readLine) can mislead it into considering them similar.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB might label this as a clone due to structural similarity in I/O boilerplate (URL opening, buffered reading) and some token overlap, despite completely different functionality.
- 共享行为: Both read from URLs using BufferedReader and InputStreamReader.；Both iterate over input lines and perform string manipulation.
- 行为差异: Function A performs network I/O to query a specific metabolite database, while Function B reads local resources.；Function A updates a mutable row object with scientific identifiers, whereas Function B creates and saves new Resource and Image objects.；Function A returns an integer score; Function B is void and throws an exception.；The logic for parsing and processing data is entirely different: one deals with metabolite IDs, the other with template and image file names.
- 修正建议: Incorporate dataflow analysis to track how inputs and outputs are used.；Add context from method signatures and surrounding code to distinguish external vs. local data sources.；Use functional similarity metrics that consider the overall purpose rather than just API calls.

### case_id=4929 FP lexical_or_api_overlap

- 方法: `populateResources` vs `run`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Populates database with template resources and image properties from predefined URLs.
- B 摘要: Fetches and processes vector tile data from a URL and adds it to the map data loader.
- 静态失败原因: The model was misled by overlapping API usage patterns (URL, InputStream, BufferedReader) and similar exception handling, while missing the semantic context difference.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely saw two distinct application-specific functionalities (setup vs. runtime tile loading) and judged non-clone.
- 共享行为: Both open URL streams and read line by line；Both handle IOException and MalformedURLException
- 行为差异: Function A saves Resource and Image objects; Function B parses GeoJSON and adds to data loader；Function A is a static initialization method; Function B is a Runnable run()；Function B has duplicate request tracking; Function A does not
- 修正建议: Include more context about the class and method purpose；Use dataflow or control flow analysis to distinguish different operations

### case_id=4930 FN library_context_missing

- 方法: `sendExceptionToServer` vs `getJSONData`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `context_recovery_then_expert`；动态可解性: `low`；执行优先级: `medium`
- A 摘要: Sends an exception report to a server via HTTP POST with URL-encoded parameters and prints the response.
- B 摘要: Fetches JSON data from a URL via HTTP GET using Apache HttpClient and returns a JSONObject.
- 静态失败原因: Low token overlap (0.19) and different library usage (URLEncoder vs HttpClient) led the model to focus on lexical differences rather than the shared HTTP request pattern.
- 静态 case study: 该类错误缺少关键上下文或需要深层语义，纯静态方法不可靠。
- 动态 case study: 动态执行价值较低：样本可能依赖库、框架、网络、GUI、数据库或项目上下文，需要先恢复环境或 mock 依赖。
- BCB 偏好解释: BCB may consider both as 'making an HTTP request and reading response', a common pattern, and accept as Type-3/4 clone despite library and purpose differences.
- 共享行为: Both open an HTTP connection to a URL；Both read the response line by line using BufferedReader；Both handle exceptions with try-catch
- 行为差异: Function A uses POST with data in body, function B uses GET with no body；Function A uses URLConnection, function B uses Apache HttpClient；Function A constructs a query string with specific parameters, function B just fetches a URL；Function A prints results to console, function B returns a parsed JSON object
- 修正建议: Incorporate data flow or control flow graphs to capture high-level I/O patterns；Use models that abstract API calls into general operations like 'send HTTP request'；Include more training examples of cross-library HTTP communication

### case_id=4931 FN benchmark_preference_bias

- 方法: `DecodeMapFile` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Reads a map file and writes decoded bytes using XOR with an incrementing magic key.
- B 摘要: Builds an editable site by transforming XML templates, performing XSLT and string replacements, and writing output files.
- 静态失败原因: The static BERT model correctly identified low token overlap and distinct method signatures/structures, leading to a non-clone prediction. However, BCB's broad preference may consider the shared I/O pattern as sufficient for a clone label, causing the model to appear to fail.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may label these as clones based on broad Type-4 similarity, such as both performing file I/O with reading/writing loops and exception handling, ignoring the vastly different logic and purpose.
- 共享行为: Both perform file I/O operations (FileInputStream, FileOutputStream/FileWriter).；Both contain try-catch blocks for exception handling.；Both use loops to read/write data in chunks.
- 行为差异: A is a simple single-pass byte transformation; B is a complex multi-step process with XML parsing, XSLT, and string substitutions.；A has no external dependencies beyond file streams; B relies on many utility classes and properties.；A uses a fixed XOR key; B dynamically generates content based on many configuration parameters.；The overall functionality and output are entirely different: A decodes a file; B generates web pages.
- 修正建议: Incorporate control-flow and data-flow analysis to capture deeper functional semantics beyond token overlap.；Use graph-based representations (e.g., AST or CFG) to distinguish between simple I/O utilities and complex business logic.；Adjust the clone definition threshold to align with BCB's broad preferences if required, or re-annotate ambiguous cases.

### case_id=4932 FP boilerplate_overlap

- 方法: `main` vs `main`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Main method for an adapter generator that reads a Prolog file, generates adapter layers, and writes output classes.
- B 摘要: Main method for a Weka experiment setup that parses flags, loads or creates an experiment, displays a GUI, and saves results.
- 静态失败原因: The model may have been misled by the common boilerplate of a main method (argument checking, try-catch, object initialization) and the presence of similar keywords like 'File' and 'IOException', but failed to capture the deep semantic difference in domain-specific operations.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely considers these non-clones because they perform entirely different functions with no overlap in problem domain or core logic, despite both being main methods.
- 共享行为: Both parse command-line arguments；Both use try-catch for error handling；Both produce output (console or file)
- 行为差异: Completely different application domains (Prolog adapter generation vs. ML experiment setup)；Different specific argument parsing and options；Different core logic: generating adapters vs. GUI-based experiment editing；Different libraries and API calls
- 修正建议: Improve semantic understanding by focusing on core logic and domain-specific terms；Use more robust representation that captures function purpose beyond structural patterns

### case_id=4933 FN benchmark_preference_bias

- 方法: `copyFile` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Copies a file from one location to another using NIO channels.
- B 摘要: Launches a NexOpen project configuration by processing XML files and setting up Hibernate reverse engineering.
- 静态失败原因: Static BERT did not fail; it correctly predicted non-clone. The mismatch is due to a likely incorrect BCB label.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled these as clones due to a broad functional similarity of 'processing something' or due to annotation error, as they share no meaningful common behavior.
- 共享行为: Both are void methods that can throw exceptions；Both may close resources
- 行为差异: copyFile performs simple file copy; launch performs complex project setup；copyFile uses NIO channels; launch uses XML processing, properties, and Eclipse API；copyFile has no configuration or conditional logic; launch has extensive branching and error handling
- 修正建议: Verify and correct BCB labels for such obvious non-clones；Implement additional filtering based on method length and complexity

### case_id=4934 FN partial_functionality

- 方法: `main` vs `getContent`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Constructs RenRen API parameters, sends a POST request, and prints the response to stdout.
- B 摘要: Executes an HTTP request using HttpClient and returns the response body as a string.
- 静态失败原因: GraphCodeBERT likely failed due to low lexical overlap and distinct method names, missing the high-level semantic similarity of HTTP response reading.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB considers both as performing the core behavior of HTTP request execution and response reading, regarding differences in library/UI as minor.
- 共享行为: Both execute an HTTP request and read the response line by line.
- 行为差异: Function A includes URL construction and parameter encoding; Function B expects a pre-built request.；Function A prints to console; Function B returns the response string.；Function A uses HttpURLConnection; Function B uses HttpClient.
- 修正建议: Enhance model with abstract representations of common operations (e.g., HTTP GET/POST).；Incorporate control-flow or data-flow to bridge library-specific APIs.

### case_id=4935 FN partial_functionality

- 方法: `setBundleInfoName` vs `httpRequestByPOST`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a URL containing key=value lines and updates bundle names in a list.
- B 摘要: Sends an HTTP POST request with parameters and returns the response body string.
- 静态失败原因: Low token overlap and different API calls (URL.openStream vs HttpClient) mislead static models; they focus on lexical similarity rather than higher-level functional pattern of network input reading.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as 'reading data from a URL' functions due to shared network I/O structure, even though protocols and processing differ.
- 共享行为: Both perform HTTP I/O operations.；Both use BufferedReader to read lines from an input stream.；Both handle IOException with try-catch.
- 行为差异: A uses GET (URL.openStream), B uses POST with parameters.；A parses key=value pairs and modifies object fields, B returns raw response text.；A returns boolean, B returns String or null.；A reads from a URL without sending data, B sends URL-encoded form data.
- 修正建议: Use data-flow analysis to identify network I/O operations.；Incorporate API call semantics (e.g., any URL reading or HTTP request).；Train with contrastive learning on functional similarity.

### case_id=4936 FP boilerplate_overlap

- 方法: `run` vs `getNetworkServersIPs`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Downloads a tile from a data source, parses it into geometries, and adds them to a data loader.
- B 摘要: Reads a network configuration file from a URL, extracts server IPs from lines after a marker, and returns them as a vector.
- 静态失败原因: Static BERT models may have been misled by the high overlap in URL opening and BufferedReader usage, ignoring the distinct post-processing steps.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels non-clones when functions implement different business logic despite sharing some boilerplate I/O code.
- 共享行为: Both open a URL connection and read its content line by line using BufferedReader
- 行为差异: Function A reads tile data and constructs geometry objects; Function B reads configuration data and extracts IP strings；Function A handles file protocol and HTTP; Function B only handles HTTP；Function A uses synchronization to avoid duplicate requests; Function B does not；Function A handles MalformedURLException and FileNotFoundException separately; Function B catches both as IOException
- 修正建议: Increase weight on the core logic parts of the function during embedding；Use attention masks to focus on tokens after the I/O setup；Incorporate structural information like method dependencies or output types

### case_id=4937 FN partial_functionality

- 方法: `postXml` vs `seeURLConnection`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.65`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends an HTTP POST request with XML body and SOAP action, reads and returns the response.
- B 摘要: Opens a URL connection to a fixed address, reads the response and logs it.
- 静态失败原因: Static BERT/GraphCodeBERT may have failed because it focused on low token overlap and different method names, missing the structural similarity in the reading loop. It might be misled by the different API calls (e.g., setRequestMethod, setConnectTimeout) appearing only in A.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label it as a clone because both implement the common pattern of reading from a URL connection using BufferedReader and StringBuilder, which is a non-trivial code fragment. Even though the setup differs, the core reading loop is identical in structure.
- 共享行为: Both open a URL connection；Both read the input stream line by line；Both accumulate lines into a string buffer
- 行为差异: A uses POST method; B uses default GET；A sets headers and writes request body; B does not；A returns the response string; B logs it and returns void；A wraps exceptions in RuntimeException; B declares throws Exception
- 修正建议: Use dataflow analysis to detect that both functions fetch from URL even if differently；Incorporate graph representations that capture the control flow of URL open-read pattern

### case_id=4938 FN partial_functionality

- 方法: `invoke` vs `register`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends HTTP POST request based on method invocation, handles response and retries on timeout.
- B 摘要: Registers a User object by encoding password, creating forum user via HTTP, persisting, and sending email.
- 静态失败原因: Static BERT models rely on low-level lexical and structural features; low token Jaccard and different method logic likely caused it to miss the broad functional overlap that BCB might capture via task-level similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have considered these clones due to shared high-level pattern of HTTP interaction (POST, read response, exception handling) despite different domains, possibly as a Type-4 clone (functional similarity).
- 共享行为: Both perform HTTP requests and read response lines；Both handle exceptions (timeout/IO) and return a value
- 行为差异: Different overall purposes (generic RPC invoker vs user registration)；Different HTTP libraries (Apache HttpClient vs URLConnection)；Different exception handling (retry logic vs fail-fast)；Different data processing (JSON parsing vs User object manipulation)
- 修正建议: Incorporate higher-level program semantics (e.g., API call patterns)；Use graph representations that capture control-flow and data-flow more abstractly；Combine static features with learned task embeddings

### case_id=4939 FN partial_functionality

- 方法: `runScript` vs `executeHttpGet`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches content from a URL as a string, returning 'error!' on failure.
- B 摘要: Performs an HTTP GET request and returns the response body parsed as JSONObject, throwing exceptions on failure.
- 静态失败原因: Low token overlap (0.107), different method names, unfamiliar library APIs, and distinct error handling caused the model to miss the high-level semantic similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels such pairs as clones (Type-4) because both perform network resource retrieval and string building, despite different libraries and return types.
- 共享行为: Both retrieve data from a network resource (URL/URI).；Both read response content into a string buffer.；Both use buffered input streams.
- 行为差异: Function A uses URL/InputStream (raw), Function B uses Apache HttpClient (HTTP-specific).；Function A returns a raw string; Function B parses response to JSONObject.；Function A catches all exceptions returning 'error!'; Function B throws exceptions.；Function A reads byte-by-byte; Function B reads line-by-line.
- 修正建议: Incorporate high-level task descriptions (e.g., 'fetch URL content').；Use data-flow analysis to capture similar I/O patterns.；Expand training data with more cross-library network retrieval examples.

### case_id=4940 FN partial_functionality

- 方法: `copyResource` vs `testReadPerMemberSixSmall`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource from a URL or file to a local file by reading and writing bytes.
- B 摘要: Tests reading a multi-member GZIP stream, copying each member to NullOutputStream and verifying byte counts.
- 静态失败原因: Static BERT models rely on token and structural similarity; the low token overlap (0.079) and different method names, APIs, and control flow cause a non-clone prediction, missing the abstract stream-copying pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as Type-4 clones because they share the high-level functionality of copying data from an input stream to an output stream, even though the specifics differ.
- 共享行为: Both read from an InputStream and write to an OutputStream；Both involve copying bytes from source to destination
- 行为差异: A writes to a real file; B writes to NullOutputStream；A handles two source types (URL or file); B uses a fixed byte array；A is a utility method without assertions; B is a test with assertions；A does not handle GZIP; B specifically uses GZIPMembersInputStream
- 修正建议: Include more diverse examples of stream-copying in training data；Incorporate dataflow analysis to recognize I/O operations；Use semantic role labeling to identify shared actions across disparate implementations

### case_id=4941 FN benchmark_preference_bias

- 方法: `testCopy_readerToWriter_nullIn` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Unit test that verifies IOUtils.copy throws NullPointerException when reader is null.
- B 摘要: Complex launch method that configures and runs a project build, including file copying with IOUtils.copy.
- 静态失败原因: The static model correctly judged no semantic equivalence, but the BCB label is lenient. The model did not fail; it disagreed with the BCB label.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB likely mislabeled this pair; the sole overlap using IOUtils.copy is insufficient to qualify as a broad Type-3/Type-4 clone. Possibly the annotation was automated or erroneous.
- 共享行为: Both use IOUtils.copy in some form
- 行为差异: A is a simple null-pointer test; B is a multi-step launch process；A deals with Reader/Writer; B deals with InputStream/OutputStream and many other operations；A has no side effects beyond throwing exception; B has significant side effects on project files and resources
- 修正建议: Re-evaluate the BCB label for this pair; likely a false positive in the benchmark.

### case_id=4942 FN benchmark_preference_bias

- 方法: `convert` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.85`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Converts an ACRNEMA stream file to DICOM format, performing validation and pixel data handling.
- B 摘要: Retrieves a resource as an InputStream, optionally caching it from a URL with HTTP handling.
- 静态失败原因: Static model correctly identified semantic dissimilarity; BCB's label likely reflects a preference for very broad functional overlap (Type-4) that typical static models ignore.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have considered both as 'I/O stream processing functions' with similar boilerplate (stream wrapping, reading/writing, error handling), leading to a broad Type-4 clone annotation.
- 共享行为: Both use InputStream/OutputStream for I/O operations；Both have try-catch-finally for resource cleanup；Both print logging messages to System.out
- 行为差异: Purpose: DICOM conversion vs. resource retrieval with caching；Input: File pair vs. String name；Logic: Complex DICOM-specific checks vs. HTTP caching logic
- 修正建议: Train with more nuanced partial functionality similarity examples；Incorporate task-specific context to avoid over-generalizing I/O patterns

### case_id=4943 FN partial_functionality

- 方法: `main` vs `copyFiles`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a URL, unzips it, and extracts each entry to a local file.
- B 摘要: Recursively copies files or directories from a source path to a destination path using NIO channels.
- 静态失败原因: Static models like BERT may over-rely on surface-level similarities such as common APIs (FileInputStream, FileOutputStream) and loop structures, missing the fundamental differences in data sources and transformation logic.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled it a clone because both functions perform file copying, but the mechanisms and purposes are too distinct for a broad Type-4 clone.
- 共享行为: Both read input and write output to files；Both involve file I/O operations
- 行为差异: Different input sources: HTTP URL vs local file system；One extracts zip entries, the other copies files as-is；Recursive vs non-recursive; different exception handling patterns
- 修正建议: Incorporate more contextual information like method names and comments；Use control-flow or data-flow analysis to differentiate source and sink operations；Train on more diverse negative examples with similar API usage but different semantics

### case_id=4944 FP boilerplate_overlap

- 方法: `main` vs `descargarArchivo`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.98`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Main method that parses a Prolog file and generates adapter code and serialized objects.
- B 摘要: Method that copies a file from a source path to a destination path using FileChannel.
- 静态失败原因: The model likely overgeneralized from similar syntactic patterns (e.g., try-catch, FileInputStream/FileOutputStream) or got confused by the presence of file I/O operations, missing the semantic context difference.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically does not consider these clones because they perform completely different tasks; the token overlap is low and the functionality is unrelated.
- 共享行为: Both handle file I/O；Both use try-catch for exception handling
- 行为差异: Function A is a complex pipeline involving parsing, code generation, and resource writing; Function B is a simple file copy；Function A uses multiple libraries (Prolog parser, ASM, etc.), Function B uses basic Java I/O；Function A has extensive conditional logic and error messages; Function B has a single catch block
- 修正建议: Improve model's ability to distinguish between code generation and simple file operations；Add training examples with similar boilerplate but different semantics；Enhance context-aware embeddings to capture high-level purpose

### case_id=4945 FP lexical_or_api_overlap

- 方法: `getUser` vs `run`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Loads a user from a DAO or parses a configuration file to create a user if not found.
- B 摘要: Fetches a map tile's GeoJSON data from a URL, processes it into geometry objects, and adds them to a data loader.
- 静态失败原因: Static BERT/GraphCodeBERT likely overemphasized the lexical and API overlap (URL, BufferedReader, InputStreamReader) while missing the distinct high-level semantics and data flow differences.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: None
- 共享行为: Both use BufferedReader and InputStreamReader to read from URLs or files.；Both handle I/O exceptions with try-catch blocks.
- 行为差异: A loads user authentication data; B loads geographic tile data.；A parses colon-delimited lines with StringTokenizer; B concatenates all lines without parsing.；A saves user via DAO; B processes tile and adds to data loader.；A returns a User object; B is void.
- 修正建议: Incorporate data flow and type information to distinguish output semantics.；Use AST or program dependency graph features to capture structural differences.；Train on harder negative examples with similar API usage but different tasks.

### case_id=4946 FN partial_functionality

- 方法: `copyResource` vs `parse`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource from a URL or file path to a destination file by reading bytes one by one.
- B 摘要: Parses an InputStream; if a resource name is in a wanted map, copies the stream to a file; otherwise delegates to a downstream parser.
- 静态失败原因: Low token overlap (0.169) and different API usage (while loop vs IOUtils.copy, URL vs InputStream) cause the model to miss the shared copy behavior. The model is sensitive to exact keywords and control flow rather than high-level I/O operations.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels Type-4 clones where core functionality (stream copy) is identical even if surrounding logic differs. The shared stream-to-file copy pattern outweighs syntactic differences.
- 共享行为: Read from an InputStream and write to a FileOutputStream
- 行为差异: Function A always copies; Function B only copies conditionally based on a map lookup.；Function A determines the output file via destinationFile(); Function B uses a path from the wanted map.；Function A reads input from a URL or File; Function B receives an already open InputStream.；Function B has a fallback to parse the stream; Function A throws an exception if resource is not found.
- 修正建议: Incorporate dataflow analysis to detect that both functions perform a stream copy operation.；Augment training data with examples of stream copy in varied contexts.；Use semantic embeddings that capture I/O patterns beyond lexical tokens.

### case_id=4947 FN benchmark_preference_bias

- 方法: `doGet` vs `convert`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Handles HTTP GET request to display a portal page with authentication, caching, and error handling.
- B 摘要: Converts an ACRNEMA image file to DICOM format, validating UIDs and pixel data.
- 静态失败原因: Static BERT correctly identified non-clone due to low lexical overlap and clear domain differences; BCB label appears to be a misannotation.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have considered broad I/O and error handling patterns, but the semantic gap is too large for clone annotation.
- 共享行为: Both involve input processing and conditional logic
- 行为差异: Domain: HTTP server vs file conversion；Core logic: page rendering vs medical image format conversion；Libraries: servlet vs DICOM；Error handling: specific to web vs file
- 修正建议: Re-evaluate BCB annotation for this pair；Use domain-aware filtering to exclude such dissimilar pairs

### case_id=4948 FP boilerplate_overlap

- 方法: `readData` vs `getResponse`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Initializes multiple sets and maps from tokenized strings of character categories.
- B 摘要: Parses an HTTP GET request and returns an HTTP response with the requested resource.
- 静态失败原因: The model may have been misled by common Java boilerplate (try-catch, I/O streams) and similar control structures (loops, conditionals) without recognizing the distinct high-level purposes.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would likely not consider these clones because the overall functionality is completely different despite some superficial structural similarities.
- 共享行为: Both read input data and process it using loops
- 行为差异: A initializes static data structures, B generates dynamic HTTP responses；A has no return value, B returns byte array；A uses global string fields, B uses method parameters and classpath resources；A processes multiple token sets, B processes HTTP request lines
- 修正建议: Incorporate dataflow analysis to trace variable dependencies；Train on more diverse examples with similar structure but different semantics；Use attention mechanisms that better capture high-level intent

### case_id=4949 FN benchmark_preference_bias

- 方法: `File2String` vs `register`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.2`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Reads a file from filesystem or classpath and returns its content as a concatenated string.
- B 摘要: Registers a user by encoding password, setting metadata, making HTTP request to external forum, processing response, persisting user, and sending email, returning success/failure.
- 静态失败原因: Static BERT models may focus on lexical overlap and structural similarity. Here, token overlap is low, and the model correctly identified the semantic mismatch.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled as clone due to the shared pattern of reading from a stream line by line, which is a common I/O idiom. However, the methods are otherwise completely different, making this likely an annotation error.
- 共享行为: Both use BufferedReader to read lines from an InputStream and concatenate them.；Both handle IOException.
- 行为差异: Different inputs: file path vs User object.；Different outputs: String vs boolean.；Different side effects: file reading vs database persist, email, HTTP request.；Different error handling: System.exit vs throw RuntimeException.
- 修正建议: Re-evaluate BCB label: such weak structural similarity should not be considered a clone.；If retaining BCB label, models should capture broad Type-4 clones; but this may increase false positives.

### case_id=4950 FP lexical_or_api_overlap

- 方法: `sendRequestObjectResponse` vs `checkForUpgrade`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Sends an HTTP request with compressed XML to a server and saves the response as a file, returning the file path.
- B 摘要: Checks for software upgrades by querying a remote server, parsing license and upgrade information, and updating the local database and UI.
- 静态失败原因: The static model likely over-emphasized surface-level API overlap (URL, URLConnection, I/O streams) and structural patterns (try-catch, loops) while missing the high-level semantic difference. The model may have been fooled by common boilerplate in network communication code.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels based on overall functionality. These two functions serve entirely different purposes (one is a generic HTTP request/response handler for XML, the other is a specific upgrade check with license validation). Low token overlap and distinct logic lead to a non-clone label.
- 共享行为: Both use URL/URLConnection to make HTTP requests；Both handle I/O streams；Both have error handling with try-catch
- 行为差异: A sends compressed XML and writes response to file; B parses license and upgrade data and updates database；A returns a file name; B updates UI components and database records；A focuses on request-response cycle for XML; B focuses on version checking and license validation；A uses GZIP compression; B uses simple text parsing
- 修正建议: Incorporate data-flow and control-flow analysis to distinguish different uses of network APIs；Improve training data with more negative examples that share API usage but differ in intent；Use contrastive learning to force separation of functionally different code even with similar low-level operations

### case_id=4951 FN partial_functionality

- 方法: `login` vs `handledRun`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Logs into LOLA service by sending email and password via HTTP and returns session ID.
- B 摘要: Downloads and updates local game data file from remote XML URL if newer version available.
- 静态失败原因: The static model likely predicted non-clone due to low token overlap and distinct functionality, failing to match BCB's broader similarity criterion.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB might label them as clones due to shared general pattern of URL connection, data I/O, and exception handling, despite different purposes.
- 共享行为: Both open URL connections；Both read from streams；Both handle exceptions
- 行为差异: A performs authentication; B performs version checking and file download；A sends data via OutputStreamWriter; B writes to file via BufferedOutputStream；A returns session ID; B updates local files and logs；A catches Exception and returns empty string; B catches specific exceptions with different handling
- 修正建议: Use semantic similarity models that capture broader functional patterns；Incorporate task-specific knowledge (e.g., login vs. download) to improve clone detection

### case_id=4952 FN partial_functionality

- 方法: `login` vs `run`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Logs into a service via HTTP POST, extracts session ID, and stores it.
- B 摘要: Fetches data from a URL via HTTP GET, parses lines into version/url/info, and notifies listeners.
- 静态失败原因: Static BERT/GraphCodeBERT likely focused on token overlap and high-level structure; low Jaccard and different control flow (switch vs. sequential) caused non-clone prediction, missing the shared network reading intent.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label as clone due to similar network I/O patterns and exception handling, considering broad functional similarity (both read from URLs) as Type-4.
- 共享行为: Open URL connection；Read lines from stream；Handle exceptions with try-catch；Use BufferedReader and InputStreamReader
- 行为差异: A uses POST method with form data; B uses GET；A extracts and returns session ID; B parses structured data into fields；A modifies internal session state; B sets error flags and notifies listeners；A has no listener notification; B has finally block for listeners
- 修正建议: Enhance model to capture shared intent despite different APIs (POST vs GET)；Use graph representations to highlight common dataflow patterns (open connection, read lines)；Include control-flow abstraction to match similar try-catch patterns

### case_id=4953 FN benchmark_preference_bias

- 方法: `modifyApplicationMessage` vs `test`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Modifies a locale-specific properties file by replacing or adding a message key-value pair.
- B 摘要: Executes a traffic simulation loop for 10 minutes using an XML configuration.
- 静态失败原因: Static BERT likely correctly identified the lack of functional similarity and low lexical overlap, thus predicting non-clone; BCB label appears to be an annotation error.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have mistakenly considered both as 'resource file processing' examples, but the core logic is unrelated.
- 共享行为: both use InputStream to read resource files from classpath
- 行为差异: different domains: localization vs traffic simulation；different operations: property replacement vs simulation stepping；different output: writing to file vs console printing
- 修正建议: Re-evaluate BCB annotation for this pair to correct label；Improve annotation guidelines to avoid overgeneralizing common I/O operations

### case_id=4954 FN benchmark_preference_bias

- 方法: `modifyApplicationMessage` vs `sendErrorMessage`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Modifies a locale-specific properties file by updating or adding a key-value pair.
- B 摘要: Sends an error email with a zipped log file to technical recipients.
- 静态失败原因: The model correctly predicted not clone (0) because functions are semantically different; BCB label is incorrect.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider both as file I/O operations with error handling, but that is too broad; likely a misannotation.
- 行为差异: A modifies property files; B sends emails；A reads and writes text properties; B compresses a log file and emails it；A is for internationalization; B is for error notification
- 修正建议: Re-evaluate BCB annotation; these are not clones；Use more strict semantic matching

### case_id=4955 FN partial_functionality

- 方法: `copyResource` vs `downloadFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource from a URL or local file to a destination file using byte-by-byte stream copying.
- B 摘要: Downloads data from S3, decrypts and decompresses it, writes to a temporary file, then moves it to the target file, with robust error handling and resource cleanup.
- 静态失败原因: Static BERT/GraphCodeBERT models may rely heavily on lexical and structural similarity. Here, token Jaccard is low (0.16), method names differ (copyResource vs downloadFile), and the code structure is quite different (one uses byte loop, the other uses IOUtils.copy; one has inline stream creation, the other has wrapped streams). The model likely focused on these surface differences and missed the underlying semantic similarity of 'copy input to file'.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as instances of 'copy resource to file' behavior, despite different source types and additional processing in downloadFile, because the core functionality of reading input and writing to a file is present. The inclusion of decryption and compression may be viewed as minor extensions.
- 共享行为: Both read data from a source (URL/file vs S3) and write it to a file destination.；Both close streams after use.；Both handle resource not found by throwing an exception.
- 行为差异: copyResource reads from URL or local file; downloadFile reads from S3 with decryption and decompression.；copyResource writes directly to the destination file; downloadFile writes to a temporary file and then moves it.；downloadFile deletes the target if it exists; copyResource does not explicitly handle target existence.；copyResource uses a simple byte-by-byte copy loop; downloadFile uses IOUtils.copy for efficient copying.
- 修正建议: Improve training data to include more diverse examples of semantic clones with different APIs.；Use models that capture higher-level intent (e.g., data flow or task descriptions).；Incorporate data flow analysis to recognize that both ultimately write to a file from an input stream.

### case_id=4956 FP boilerplate_overlap

- 方法: `lookupFutureEvents` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches future events from Meetup API and parses JSON into Event objects.
- B 摘要: Searches Google Images and parses HTML to extract image URLs, then updates a UI component.
- 静态失败原因: The model likely over-weighted the common structural pattern (URL opening, BufferedReader loop) and ignored the divergent parsing and output semantics.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels as non-clones when functions perform distinct domain-specific tasks despite sharing boilerplate I/O code.
- 共享行为: Both make HTTP GET requests to external web APIs.；Both read the response line by line using BufferedReader.；Both parse the response (JSON or HTML) to extract structured data.
- 行为差异: Different API endpoints (Meetup vs Google Images) and response formats (JSON vs HTML).；Different output: A returns a List<Event>; B updates a static list (googleImages) and a UI label.；Different error handling: A throws GtugsException; B shows error dialog via MusicBoxView.showErrorDialog.；Different parsing logic: A extracts event details; B extracts image URLs from href attributes.
- 修正建议: Incorporate data-flow analysis to track how parsed data is used.；Use API-specific context (e.g., method names, return types) to disambiguate.；Train on more diverse examples to reduce sensitivity to I/O boilerplate.

### case_id=4957 FP boilerplate_overlap

- 方法: `getWebByUrl` vs `getTicketsForQueue`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Downloads a web page from a URL, saves it to a file, and recursively processes embedded URLs.
- B 摘要: Queries a REST API for open tickets in a queue, parses ticket IDs, and retrieves each ticket, returning a list.
- 静态失败原因: The model may have been misled by overlapping API terms (e.g., BufferedReader, InputStreamReader, URL, Exception) and similar try-catch reading loops, overlooking the distinct high-level functionality.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this non-clone because the functions have entirely different purposes and algorithms, despite sharing low-level boilerplate for network I/O.
- 共享行为: Both perform HTTP requests to retrieve data from a remote server.；Both read the response line by line using BufferedReader.；Both handle exceptions and log errors.
- 行为差异: A writes the response to a file, while B collects ticket IDs and fetches additional data.；A recursively processes embedded URLs in the response, while B parses ticket IDs and retrieves each ticket.；A uses URLConnection, B uses HttpClient with HttpGet.；A outputs progress to console and a report, B returns a list of RTTicket objects.
- 修正建议: Incorporate method names and comments as additional features.；Use graph-based representations (e.g., data flow, control flow) to distinguish file writing vs. list collection.；Train on more diverse examples to reduce over-reliance on common library usage patterns.

### case_id=4958 FP lexical_or_api_overlap

- 方法: `main` vs `EncodeReturn`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Generates adapter classes and JAR files from a Prolog file using a parser and class generation infrastructure.
- B 摘要: Encodes a file using cryptographic operations and concatenates the result with other encoded data.
- 静态失败原因: Static BERT models may have focused on API-level overlap (File, FileInputStream, etc.) and similar control flow structures, while missing the high-level semantic difference.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB considers these non-clones because they implement entirely different algorithms with no shared functionality beyond trivial file handling.
- 共享行为: Both perform file I/O operations；Both use try-catch for error handling
- 行为差异: Function A parses Prolog and generates Java classes; Function B encodes files cryptographically；Function A uses class loader and adapter generation; Function B uses crypto clients and channel transfers
- 修正建议: Enhance model with more structural understanding of data flow and method purpose；Include task-specific pre-training on fine-grained function-level semantics

### case_id=4959 FP lexical_or_api_overlap

- 方法: `getFrameworkFactory` vs `readURL`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a specific OSGi service resource file, parses it to find a class name, and instantiates a FrameworkFactory.
- B 摘要: Reads any URL, prints its content line by line to standard output.
- 静态失败原因: Static BERT models often rely on token overlap and surface-level API similarity (URL, BufferedReader, readLine) without capturing deep semantic intent, leading to false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically does not label functionally different methods as clones even if they share similar IO boilerplate; the distinct purposes lead to a Type-4 (non-clone) annotation.
- 共享行为: Both open a URL stream and read lines using BufferedReader；Both use try-finally blocks to close streams
- 行为差异: Function a parses service file for a class name and creates an instance; function b prints each line；Function a throws exception if no factory found; function b catches all exceptions and prints stack trace；Function a reads from a classpath resource; function b reads from any arbitrary URL
- 修正建议: Add data-flow aware features to distinguish output-generating code from parsing code；Incorporate control-flow or semantic role labeling to differentiate reading vs. using content

### case_id=4960 FN benchmark_preference_bias

- 方法: `main` vs `logging`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Download a KMZ file from a URL and extract its ZIP entries to files.
- B 摘要: Log the content and headers of an inbound SOAP message.
- 静态失败原因: Static model correctly predicted non-clone; the benchmark label appears to be an overextension of clone criteria.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled as clone due to both using InputStream and file I/O patterns, but this is too generic for meaningful similarity.
- 行为差异: Function A downloads and extracts a ZIP file from a URL; Function B logs message content.；Function A writes to files; Function B writes to a logger.；Function A handles ZIP entry iteration; Function B handles message encoding and headers.
- 修正建议: Re-evaluate BCB label for this pair as non-clone.；Ensure clone definitions require substantial functional overlap.

### case_id=4961 FN partial_functionality

- 方法: `extractUninstallFiles` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Extracts uninstall files, handling backup of previous version and selective deletion of files.
- B 摘要: Builds a site for editing by transforming XML pages and writing output files.
- 静态失败原因: Low token Jaccard (0.118) indicates little lexical overlap. The model likely relied on surface tokens and missed the deeper structural similarity in file I/O patterns.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled as clone because both functions involve substantial file I/O, directory creation, and error handling, which can be seen as a shared 'file management' functionality under a loose Type-4 annotation.
- 共享行为: Perform file and directory I/O operations；Handle IOException and other exceptions；Use system properties like file.separator
- 行为差异: A manages backup and conditional file deletion; B performs XML transformation and writes multiple output files；A focuses on uninstall logic; B focuses on page rendering；A uses ZipEntry and CRC; B uses Transformer and DOM
- 修正建议: Incorporate structural or control-flow features to capture shared file I/O patterns；Use graph-based representations to highlight common substructures；Increase training data for partial functionality clones

### case_id=4962 FP lexical_or_api_overlap

- 方法: `getJSONData` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches JSON data from a given URL using Apache HttpClient and parses it.
- B 摘要: Performs Google image search by constructing URL, reading HTML response, extracting image URLs, and updating a GUI.
- 静态失败原因: The model likely focused on overlapping API usage (HTTP connection, BufferedReader, exception handling) and method name similarity ('get' and 'search' both imply data retrieval), ignoring the distinct parsing and output behaviors.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would not label these as clones because despite both involving HTTP requests, their core functionality is different: one is a generic JSON data fetcher, the other is a specific image search with side effects on UI.
- 共享行为: Both perform HTTP GET requests；Both read response line by line using BufferedReader；Both have exception handling
- 行为差异: One uses Apache HttpClient (DefaultHttpClient, HttpGet), the other uses HttpURLConnection；One parses JSON, the other extracts URLs from HTML by splitting on a pattern；One returns a JSONObject, the other updates a GUI and returns void；One takes a URL string, the other takes a search query and start parameter to construct a URL
- 修正建议: Include negative examples with similar boilerplate but different functionality in training；Add context-aware embeddings that capture method purpose and return type；Use dataflow analysis to differentiate between output types (JSON vs UI update)

### case_id=4963 FN boilerplate_overlap

- 方法: `getFile` vs `encodeFileToFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies its endpoint in XML, and saves it to a temporary file.
- B 摘要: Reads a file and encodes it to Base64, writing to another file.
- 静态失败原因: Static BERT/GraphCodeBERT likely focused on lexical and structural similarities like file stream usage, buffer loops, and exception handling, ignoring the distinct API calls (URL, XML, Base64) and overall purpose.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB might have labeled them as clones due to shared file I/O boilerplate and similar structure (method signature, exception handling), but the core functionality is entirely different, making them non-clones even under broad Type-4.
- 共享行为: Both perform file I/O operations using Java streams.；Both use try-catch blocks for exception handling.；Both involve reading and writing files with buffers.
- 行为差异: Function A downloads content from a URL, while B reads from a local file.；Function A parses and modifies XML, B performs Base64 encoding.；Function A returns a file path, B returns a boolean success flag.；Function A has multiple exception types and logging, B has minimal logging.
- 修正建议: Incorporate API call aware embeddings.；Use contrastive learning to differentiate functions with similar I/O patterns but different semantics.；Add attention to method names and import statements.

### case_id=4964 FN partial_functionality

- 方法: `readPage` vs `seeURLConnection`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a URL's content line by line, optionally skipping lines starting with '#', and returns the concatenated HTML string with newlines.
- B 摘要: Opens a fixed URL connection, reads all lines and appends them without newlines into a StringBuffer, then logs the result.
- 静态失败原因: Static BERT models like GraphCodeBERT rely on token-level and structural similarity. The low token Jaccard (0.27) and different method signatures (parameter, return type, fixed URL) likely cause the model to classify as non-clone. Additionally, the model may not capture the high-level semantic similarity of reading URL content.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider them clones because both perform the same core task of reading all lines from a URL, which is a common I/O pattern. The differences in output handling (return vs log) and comment filtering might be considered superficial in BCB's broad Type-3/Type-4 annotation.
- 共享行为: Both read from a URL via BufferedReader；Both iterate over all lines until null；Both close the reader after reading
- 行为差异: A returns the string, B logs it and returns void；A has an option to ignore comment lines (starting with '#'), B does not；A adds newline characters between lines, B does not；A uses String concatenation, B uses StringBuffer
- 修正建议: Augment training data with more I/O patterns where the core task is the same but output handling differs；Incorporate data flow analysis to identify that both read all lines from a URL；Use contrastive learning to learn that API usage patterns (e.g., BufferedReader + readLine) indicate similar functionality even with different parameters

### case_id=4965 FP boilerplate_overlap

- 方法: `main` vs `encodeFileToFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Generates adapter JAR from a Prolog file using command-line arguments.
- B 摘要: Encodes a file to Base64 and writes to another file.
- 静态失败原因: Static BERT model likely overestimated similarity due to common boilerplate code (try-catch, file streams, buffer usage) and lacked understanding of the high-level task divergence.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB correctly labels as non-clones because the functions serve entirely different purposes and have no semantic overlap beyond basic I/O patterns.
- 共享行为: Both perform file I/O operations；Both use try-catch-finally for exception handling；Both use buffered streams
- 行为差异: Function A parses Prolog and generates adapters; B does Base64 encoding；A has complex logic with multiple class loaders and visitors; B is a simple copy with encoding；A uses command-line arguments; B takes two file path parameters
- 修正建议: Incorporate dataflow analysis to distinguish operations on data；Use method name embeddings to capture intent；Add task-specific tokens (e.g., 'encode', 'generate adapter')

### case_id=4966 FN benchmark_preference_bias

- 方法: `readData` vs `startScript`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.85`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Reads data from multiple comma-separated string constants and populates various sets and a map for Tibetan/Sanskrit character processing.
- B 摘要: Fetches a script from a URL via HTTP and appends it to a dialog script buffer.
- 静态失败原因: Static BERT models rely on token overlap and structural similarity. The token Jaccard is very low (0.09), and the vocabularies are dissimilar. However, the model predicted non-clone, which aligns with low similarity. But BCB says clone, so the model failed to identify a clone that BCB thought exists. Could be due to the model not capturing the high-level concept of 'reading input data' that BCB might consider.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may label this as a clone if they consider both as 'data reading' or 'initialization' functions, despite very different specifics. However, with such low token overlap, it's unlikely; the BCB label might be an error in the benchmark.
- 共享行为: Both read textual input；Both use try-catch for IOException (implied in A)；Both populate data structures (sets/map vs dialog.script)
- 行为差异: A processes multiple static string fields with comma-separated tokens, B fetches a remote resource via URL；A populates multiple sets and a map, B appends to a script string；A is static and has no parameters, B is instance method with Attributes parameter；A has complex initialization logic for character sets, B is simple reading and appending
- 修正建议: Improve model with semantic understanding of input/output behavior；Use dynamic analysis or control-flow graph to identify common patterns like reading lines；Increase training data for partial functionality clones

### case_id=4967 FN partial_functionality

- 方法: `getPagina` vs `register`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches the entire content of a web page as a string from a given URL, returning either the concatenated content or an error message.
- B 摘要: Registers a user by encoding password, setting default authorities, creating a forum user via an HTTP request, persisting the user to the database, and sending a confirmation email, returning a boolean indicating email success.
- 静态失败原因: Static BERT models rely on token-level similarity and may not capture the high-level semantic difference. The shared boilerplate code (URL, BufferedReader, readLine, catch IOException) creates token overlap, but the model predicted non-clone, indicating it was sensitive to the different overall structures. However, it failed to recognize the clone as defined by BCB's broader criteria, possibly because it lacked understanding of the partial functional overlap.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this as a clone due to the shared pattern of opening a URL, reading lines, and handling IO exceptions, which is considered a partial functionality overlap (Type-3/Type-4). The core behavior of reading from a URL is common, so under a broad annotation preference, they are considered clones.
- 共享行为: Both open a URL connection and read lines from the input stream using BufferedReader.；Both handle IOException and catch exceptions related to URL operations.；Both use a StringBuilder or string concatenation to accumulate response data.
- 行为差异: Function A only retrieves webpage content; function B performs multiple additional steps (password encoding, authority assignment, database persistence, email sending).；Function A returns a String (content or error); function B returns a boolean based on email success.；Function A handles MalformedURLException and generic Exception; function B handles NumberFormatException and throws RuntimeException.；Function B constructs a URL with query parameters; function A uses the given URL directly.
- 修正建议: Use a model that incorporates data flow or program dependence graphs (e.g., GraphCodeBERT) to better capture shared sub-computations.；Train with contrastive learning on pairs that have partial functional similarity to improve recognition of Type-3/Type-4 clones.；Include example pairs of URL reading boilerplate clones in the training set to increase sensitivity.

### case_id=4968 FN boilerplate_overlap

- 方法: `getEncoding` vs `postRequest`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Extracts character encoding from HTTP response headers or body.
- B 摘要: Sends an HTTP POST request with data and returns the response body.
- 静态失败原因: Static models might focus on common API calls (openConnection, BufferedReader) and ignore the control flow difference.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may label this as clone due to structural similarity in URL handling and stream reading, but the functionality is distinct.
- 共享行为: Both open a URLConnection and read from an InputStream using BufferedReader.
- 行为差异: Function A reads headers and body to extract encoding; Function B writes data to output stream and reads response as a string.；Function A does not send any data; Function B sends POST data.；Function A returns a String (encoding); Function B returns the full response.；Function A uses try-finally; Function B uses try-catch.
- 修正建议: Include data flow analysis to distinguish input vs output operations.；Consider functional semantics beyond API call sequences.

### case_id=4969 FN benchmark_preference_bias

- 方法: `main` vs `encodeFileToFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a URL and extracts its zip entries to files.
- B 摘要: Encodes a file to Base64 and writes the encoded data to another file.
- 静态失败原因: The static model likely failed to predict clone because it focused on the different method names, signatures, and core logic, missing the shared I/O pattern that BCB considered clone-worthy under lenient criteria.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider these clones because both involve file I/O with buffered streams and similar exception handling, even though the core functionality differs. This could be a broad interpretation of Type-4 clones (semantic similarity in I/O patterns).
- 共享行为: Both read from an InputStream and write to an OutputStream using a buffer.；Both handle exceptions with printStackTrace.
- 行为差异: Function A extracts a zip archive while Function B encodes data in Base64.；Function A deals with network URL and zip entries; Function B deals with Base64 encoding of a file.
- 修正建议: Include I/O streaming patterns as potential weak clones in training.；Adjust model threshold to better match BCB's broad annotation style.

### case_id=4970 FN benchmark_preference_bias

- 方法: `getProjectTreeData` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads an XML file from a server and parses it into a 2D string array of project tree data.
- B 摘要: Builds a site for editing by reading XML, applying XSLT transformations, and writing output files for each page.
- 静态失败原因: The static model correctly identified the low lexical overlap and structural differences, leading to a non-clone prediction, which contradicts the BCB label. The error is likely due to the BCB label being a misclassification.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as a clone due to both functions being in the web/XML domain and sharing common technical patterns (URL handling, file streams, XML parsing), but the core functionality is entirely different.
- 共享行为: Both involve XML processing (parsing/transformation).；Both perform file I/O operations.；Both handle exceptions with try-catch blocks.
- 行为差异: A retrieves data from a remote server and returns a simple data structure; B performs complex transformation and writes multiple files.；A uses DOM parsing with a consistent schema; B uses XSLT and string manipulation for dynamic content.；B involves iteration over pages and multiple file operations, while A is a single request-response flow.
- 修正建议: Re-examine and correct the BCB label for this pair.；Ensure that clone annotations reflect true semantic or functional similarity, not just domain overlap.

### case_id=4971 FP partial_functionality

- 方法: `fetchUrl` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.98`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches the content of a given URL and returns it as a string.
- B 摘要: Searches Google Images for the current music track's artist and album, and populates a list of image URLs.
- 静态失败原因: The static model may have focused on the lexical overlap of reading from a URL, using similar constructs like BufferedReader, URL, etc., and missed the broader context and specific purpose of function B.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely labeled it as non-clone because the functions serve entirely different purposes; one is a generic utility, the other is a domain-specific method with complex logic beyond just fetching a URL. The overlapping code is only a small portion of the overall functionality.
- 共享行为: Both open a URL connection and read the response line by line.
- 行为差异: A takes a URL as parameter; B constructs a URL based on object state.；A returns the content; B stores parsed image URLs in a list and has side effects.；B includes HTTP header setting, HTML parsing, and conditional execution based on artist change.；A has simple exception handling returning empty string; B catches Exception and shows error dialog.
- 修正建议: Use a model that better captures the overall function purpose, possibly by incorporating flow awareness or a graph representation.；Increase the weight of function signatures and return types.；Consider the data flow: A returns value, B modifies a list and has conditional logic.；Use a model that can discriminate based on the task (generic vs specific).

### case_id=4972 FN partial_functionality

- 方法: `readGeoParserResult` vs `executeHttpGet`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.4`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends an XML SOAP-like request to a geo parser service, parses the XML response, and returns a collection of place names with optional gazetteer IDs, with retry on failure.
- B 摘要: Executes an HTTP GET request to a given URI, reads the response line by line, and returns the response body as a JSONObject.
- 静态失败原因: GraphCodeBERT likely failed due to low token overlap (Jaccard 0.09) and highly different vocabulary (XML tags, HttpClient classes). The model may not recognize the structural similarity of HTTP request-response cycle across different APIs and parsing logic.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label them as clones because both implement the core behavior of making an HTTP request and reading the response, a common reusable pattern. BCB tends to accept partial functionality similarity and may ignore differences in parsing, error handling, and return types.
- 共享行为: Both make HTTP GET requests to a remote server.；Both read the HTTP response line by line using BufferedReader.；Both use StringBuilder to accumulate the response content.
- 行为差异: Function A constructs a custom XML request body and URL-encodes it, while B takes a raw URI.；Function A uses java.net.URL, while B uses Apache HttpClient.；Function A parses XML with Dom4j to extract data, while B parses the entire response as JSON.；Function A handles errors with retries (up to 3), while B throws exception.
- 修正建议: Incorporate dataflow analysis to capture shared patterns like HTTP request construction and response reading.；Use program slicing to isolate the common I/O behavior.；Train on cross-library API usage patterns.

### case_id=4973 FP lexical_or_api_overlap

- 方法: `simulate` vs `readData`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Reads a file of simulation data, calls remote services to rate users and obtain reputation, prints results, and asserts outcomes.
- B 摘要: Parses token strings and a file to initialize sets and maps for Tibetan character transliteration.
- 静态失败原因: The static model overgeneralized due to shared boilerplate patterns (file reading, loops, try-catch, method calls) and ignored the entirely different domain-specific operations (remote service calls vs. token parsing and map population), relying on token-level similarities without understanding high-level semantics.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled these as non-clones because the functionalities are completely different: one is a simulation test with remote calls, the other a data initialization routine for a transliteration system; no partial functional overlap exists.
- 共享行为: Both use file I/O (reading files)；Both use loops to process data；Both use try-catch for exceptions；Both populate data structures (maps/sets)
- 行为差异: A makes remote service calls and assertions; B only builds local data structures；A has complex control flow with nested try-catch and multiple service calls; B has nested conditionals on column indices；A writes debug output to file and console; B throws errors but prints only on exception；A processes simulation request lines; B processes Tibetan character definitions
- 修正建议: Improve model to focus on core logic rather than boilerplate I/O patterns；Use data-flow analysis to distinguish different API call sequences；Incorporate type information of variables and method signatures

### case_id=4974 FN benchmark_preference_bias

- 方法: `gerarTutorialPage` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Generates a tutorial website by creating directories, copying CSS files, and writing HTML pages.
- B 摘要: Downloads a KMZ file from a URL and extracts its contents to disk.
- 静态失败原因: Static BERT missed the potential high-level similarity due to low token overlap, different method names, and focus on surface syntax.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may label it as a clone based on high-level type-4 similarity of 'copying files using streams', but the functional purposes are entirely distinct.
- 共享行为: Both perform file I/O operations (reading and writing files).；Both involve directory creation and stream copying.
- 行为差异: Function A generates a static website; Function B extracts a compressed archive.；Function A uses local resources; Function B fetches from a remote URL.；Different error handling: A returns boolean with message dialogs; B throws exceptions.；Different output: A creates multiple HTML/CSS files; B extracts arbitrary files from a zip.
- 修正建议: Incorporate dataflow analysis to capture structural similarities.；Use code summarization models to compare semantic intent.；Adjust benchmark to focus on core functionality rather than I/O patterns.

### case_id=4975 FN benchmark_preference_bias

- 方法: `sendExceptionToServer` vs `getNetworkServersIPs`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.6`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Sends exception details to a remote server via HTTP POST with URL-encoded parameters.
- B 摘要: Fetches a list of server IP addresses from a network resource by parsing lines for '!SERVERS' markers.
- 静态失败原因: The static model likely captured the low lexical overlap (Jaccard=0.2) and different control/data flow; it correctly identified them as non-clones, but BCB's label may be an outlier or annotator preference.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might consider both as 'network communication' utilities, ignoring the specific logic and data flow direction; however, this is a very broad interpretation likely not standard for Type-3/Type-4.
- 共享行为: Both use URL and URLConnection to establish an HTTP connection；Both read from an input stream via BufferedReader；Both catch IOException
- 行为差异: A writes output to the server (POST); B only reads (GET-like)；A encodes and sends multiple parameters; B parses lines for a specific pattern；A checks response for 'success'; B returns a Vector of IPs；A sends exception/reporting data; B retrieves configuration data
- 修正建议: Re-evaluate BCB label: consider if network utilities with opposite data flow should be clones；If BCB label is correct, incorporate broader network-operation similarity features；Otherwise, accept that static model correctly rejects this pair

### case_id=4976 FN partial_functionality

- 方法: `copy` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.95`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copy a file from source to destination with validation and buffer-based I/O.
- B 摘要: Launch a NexOpen project by configuring launch settings, validating project structure, and performing file operations including copying a resource file.
- 静态失败原因: Static BERT/GraphCodeBERT likely focused on the overall method signature and high-level purpose (copy vs launch), which are distinct. The shared file copy sub-functionality is a small part of Function B and was overshadowed by the dominant launch logic. Low token overlap (0.0875) also hindered lexical matching.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this as a Type-4 (semantic) clone because both functions contain a core file copy behavior, even though the overall functionality differs. The annotation policy often accepts partial functionality similarity, especially when the copied code segment is nontrivial.
- 共享行为: Both perform file copy operations (reading from a source and writing to a destination).；Both use try-catch-finally blocks for resource management.；Both check preconditions (e.g., file existence, project properties) before proceeding.
- 行为差异: Function A is exclusively a file copy utility; Function B is a project launch method with many additional responsibilities like XML parsing, property setting, and invoking build actions.；Function A operates on generic File objects; Function B operates on Eclipse workspace resources and ILaunchConfiguration.；Function A is a static method; Function B is an instance method with complex dependencies.
- 修正建议: Use dataflow analysis to detect file copy patterns spanning multiple statements.；Incorporate call-graph information to identify common utility operations.；Employ code summarization techniques that capture sub-task descriptions.

### case_id=4977 FN benchmark_preference_bias

- 方法: `extractResourceToFile` vs `doGet`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Extracts a classpath resource to a file using I/O copy.
- B 摘要: Handles a servlet GET request for a page, with permission checks, logging, and optional caching to a temporary file.
- 静态失败原因: The static model correctly predicted non-clone, so it did not fail; the BCB label appears to be an annotation error or overly broad interpretation.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled them as clones due to both containing file output operations, but the core functionality and context are vastly different.
- 共享行为: Both involve writing data to a file.
- 行为差异: Code A is a simple utility for copying a resource stream to a file without any business logic.；Code B performs complex request handling, page retrieval, visibility checks, and conditional file caching.
- 修正建议: Re-evaluate BCB annotation guidelines to avoid labeling pairs with only superficial similarity.；Use stricter criteria for Type-3/Type-4 clones requiring shared functional intent.

### case_id=4978 FN partial_functionality

- 方法: `register` vs `retrieveTemplate`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Registers a user by encoding password, setting authorities and hash, persisting to database, and creating a phpBB forum user via URL connection.
- B 摘要: Retrieves a cached template by reading content from a URL over HTTP and caching the result.
- 静态失败原因: Static BERT models rely on token embeddings and structure, but the high-level semantics differ drastically. The models may fail to capture the true intent due to the limited context and inability to infer long-range side effects.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider them clones due to the structural similarity of URL connection and line-by-line reading, which is a common pattern in Type-3/Type-4 clones even if the surrounding logic differs.
- 共享行为: Both open a URL and read lines via BufferedReader from a URLConnection.；Both use a while loop to read lines from the input stream.；Both close the BufferedReader after reading.
- 行为差异: Function A has many side effects (password encoding, authority setting, persist, email) while B only returns a string.；A involves exception handling for IOException and NumberFormatException; B throws Exception and has no try-catch.；A writes to persistent storage and external system; B only caches and returns a local string.；A modifies the input user object; B is purely functional.
- 修正建议: Incorporate dataflow analysis to track side effects and state modifications.；Use AST-based models that can distinguish between methods with different high-level goals despite similar low-level code snippets.；Add more training examples of non-clones with overlapping I/O operations but different semantics.

### case_id=4979 FP lexical_or_api_overlap

- 方法: `setBundleInfoName` vs `executePost`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a URL, parses key-value pairs, and updates bundle names in a list.
- B 摘要: Executes an HTTP POST request and returns the response body as a string.
- 静态失败原因: Static BERT models (like GraphCodeBERT) likely relied on high lexical overlap (both use URL, BufferedReader, try-catch, while loop reading lines) and similar control flow structure, ignoring the semantic differences between opening a stream for reading versus executing an HTTP POST with request properties and output stream.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would label these as non-clones because their core functionality is entirely different: one is data parsing/updating, the other is HTTP communication. The shared boilerplate of reading from a URL does not imply clone-level similarity.
- 共享行为: Both use URL and BufferedReader to read from a network resource；Both handle IOException via try-catch and print stack trace；Both have a while loop reading lines
- 行为差异: Function A updates a list of objects; Function B sends an HTTP POST request；Function A returns boolean; Function B returns response string or null；Function A reads from URL.openStream(); Function B uses HttpURLConnection with POST method
- 修正建议: Incorporate dataflow analysis to distinguish when URL.openStream() is used for read-only vs. when HttpURLConnection is used for POST with output；Add focus on method-level semantic roles (e.g., setter vs. request executor) beyond token sequences；Include fine-grained API usage patterns that differentiate network read vs. write

### case_id=4980 FP lexical_or_api_overlap

- 方法: `main` vs `fetchURLData`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: A CLI tool that reads a Prolog file, parses it, generates adapter code and writes a JAR file with adapter metadata.
- B 摘要: A utility that fetches data from a URL (HTTP or file) using optional proxy and returns the content as a byte array.
- 静态失败原因: The static BERT model likely relied on token overlap (e.g., 'File', 'URL', 'IOException', 'return') and similar structural patterns (try-catch, I/O), failing to capture the distinct task semantics.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clones when functions have fundamentally different purposes and only superficial token overlap, even if both use common libraries.
- 共享行为: Both involve I/O operations (file/network).；Both use try-catch-finally for error handling.；Both handle Exceptions with print/output messages.
- 行为差异: Purpose: code generation vs. data fetching.；Logic: complex adapter generation pipeline vs. simple HTTP request.；Output: writes JAR/resource files vs. returns byte[].；Dependencies: uses Prolog parser, ASM, etc. vs. HTTPURLConnection.
- 修正建议: Incorporate data flow or control flow analysis to distinguish different logic paths.；Train on more diverse non-clone pairs with similar tokens but different behaviors.；Use larger context or cross-function attention to capture purpose beyond local API usage.

### case_id=4981 FN lexical_or_api_overlap

- 方法: `GetResponse` vs `invoke`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Makes an HTTP GET request to a URL and returns the response body as a string, with minimal error handling.
- B 摘要: Invokes a remote method via HTTP POST, serializes arguments as JSON, reads and deserializes the response, with retry on timeout.
- 静态失败原因: Token Jaccard is very low (0.14). The functions use different HTTP libraries (HttpURLConnection vs HttpClient), different method names, and different parameter types. The model likely relied on lexical overlap and saw them as very different, missing the underlying I/O pattern similarity.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may consider both as 'HTTP client methods that read response line by line' and overlook differences in method type, serialization, and retry because the core pattern of opening a connection, reading lines, and returning content is present.
- 共享行为: Both perform HTTP requests and read the response line by line using BufferedReader.；Both return a string representation of the response body (A raw, B deserialized).；Both use similar I/O pattern: open connection, read lines, close resources.
- 行为差异: A uses GET, B uses POST.；A returns raw string, B returns deserialized object or null.；A has no retry, B has retry logic with recursion.；A has no service discovery, B does.
- 修正建议: Incorporate dataflow or graph-based features to capture similar I/O patterns despite different APIs.；Increase training data with diverse HTTP client implementations.；Use contrastive learning to recognize similar structures with low lexical overlap.

### case_id=4982 FN partial_functionality

- 方法: `testNetworkHTTP` vs `setMembers`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: A test method that makes multiple HTTP connections to send device data and discard responses.
- B 摘要: A method that fetches a web page and parses HTML to extract component and priority lists.
- 静态失败原因: Low token Jaccard similarity (0.156) and different surface-level details (e.g., HTML parsing, Recoder calls) caused the model to miss the shared underlying network I/O pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as performing network I/O (URL, BufferedReader, InputStreamReader) and reading lines, thus categorizing as a broad Type-3 clone with similar high-level functionality.
- 共享行为: Both perform HTTP GET requests and read line-by-line from the response stream.
- 行为差异: A sends data via URL parameters and ignores response content; B fetches a specific page and parses HTML for select elements.；A uses multiple URLs; B uses one.；A logs via Log.v; B prints to console using System.out.println.
- 修正建议: Incorporate structural features that capture high-level operations like network I/O sequences.；Use graph-based representations that abstract away specific string patterns.

### case_id=4983 FP lexical_or_api_overlap

- 方法: `import_hints` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Parses a hint file from URL or file system and places pieces on a puzzle board.
- B 摘要: Searches Google Images for a query, extracts image URLs, and displays the first image.
- 静态失败原因: Static BERT/GraphCodeBERT may have been misled by high lexical overlap of common I/O patterns (URL, BufferedReader, readLine) and token similarity, failing to capture the distinct overall semantics and control flow.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled this as non-clone because despite superficial API overlap (URL, BufferedReader), the core logic and output are entirely different; one is a data import routine, the other is a web search and UI update.
- 共享行为: Both use URL and BufferedReader to read data from an external source.
- 行为差异: A returns boolean and processes puzzle hints with piece IDs; B is void and updates UI with images.；A handles IOException; B catches Exception and shows error dialog.；A uses byurl flag to decide file/URL; B always uses HTTP connection.；A reads numeric tokens for piece placement; B parses HTML for image URLs.
- 修正建议: Train models to distinguish boilerplate I/O from domain-specific logic.；Incorporate dataflow analysis to track how read data is used.；Use graph-based representations that capture dependencies beyond token sequences.

### case_id=4984 FP boilerplate_overlap

- 方法: `get` vs `loadExistingAntlibs`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Makes an HTTP GET request with custom headers, reads response lines, decodes GameRecord objects, and returns an array or null on error.
- B 摘要: Loads Ant libraries by reading a resource file listing package names, resolving antlib.xml URIs, and loading each Ant library.
- 静态失败原因: GraphCodeBERT may have been misled by common API usage (URL, BufferedReader, InputStreamReader) and similar loop structure, ignoring the distinct high-level purpose and different data flow.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clones when functions have completely different purposes, even if they share some I/O boilerplate. This pair has no significant functional similarity.
- 共享行为: Both use URL and open an InputStream via URL.openStream() or similar.；Both read lines with BufferedReader and InputStreamReader.
- 行为差异: Function A fetches game records from a remote server; Function B loads Ant libraries from classpath resources.；Function A sends HTTP GET with specific headers, Function B reads static resource files.；Function A returns an array of GameRecord; Function B returns void and calls loadAntLib for each found URL.；Error handling differs: A prints stack trace and returns null; B throws RuntimeException.
- 修正建议: Incorporate task-specific semantics (e.g., distinguish HTTP client vs. resource loader).；Weigh API usage less when it is generic I/O boilerplate.；Use control flow and data flow analysis to separate different program intents.

### case_id=4985 FN lexical_or_api_overlap

- 方法: `main` vs `copyFileChannel`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a URL via HTTP or file protocol, extracts ZIP entries, and writes each entry to a file with the entry's name.
- B 摘要: Copies a file from source to destination using FileChannel transferTo, optionally preserving the source file's last modification time.
- 静态失败原因: Static BERT models may rely heavily on token overlap and common API patterns. Both functions use FileInputStream, FileOutputStream, and similar variable names (e.g., 'count', 'data'), leading to false positive clone detection despite different high-level semantics.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely labeled this as a clone because both methods perform file I/O and copy data, which might be considered 'broad Type-3' with similar control flow (read loop, write). However, the differences in source type, compression, and purpose are significant.
- 共享行为: Both involve reading from an input source and writing to an output destination.；Both use file-related I/O classes (FileInputStream, FileOutputStream).；Both handle I/O exceptions (throws clause).
- 行为差异: A reads from a URL (HTTP or file) and decompresses ZIP entries; B reads from a local file and copies raw bytes using FileChannel.；A writes multiple entries to separate files; B writes a single file.；A lacks proper resource cleanup on exception; B uses try-finally to close channels.；A uses ZipInputStream and BufferedOutputStream; B uses FileChannel transferTo.
- 修正建议: Incorporate structural information like method name, comments, and call graph.；Use dataflow analysis to distinguish between compression/decompression and plain copy.；Train on more diverse examples to avoid over-attention to common stream classes.

### case_id=4986 FP lexical_or_api_overlap

- 方法: `perform` vs `SHA`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.85`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Struts Action method that handles user request to classify a concept by sending XML to a remote service and parsing the response.
- B 摘要: Utility method to compute SHA hash of a string and return hex-encoded result.
- 静态失败原因: The static BERT model may have produced a false positive due to lexical overlap in common Java boilerplate (e.g., method signature elements like 'throws', 'IOException', 'String', 'public') and the presence of similar patterns like try-catch blocks, despite the extremely low token Jaccard similarity (0.04). Alternatively, the model may have been confused by the truncated middle of code_a, causing it to rely on less discriminative features.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB annotates non-clone because the two functions serve completely different purposes (web action vs. cryptographic utility) with no shared functionality.
- 共享行为: Both involve string manipulation and return a result；Both use try-catch for exception handling
- 行为差异: Function A performs HTTP communication, session management, and XML parsing; Function B is a pure cryptographic hash.；Function A has complex control flow with multiple conditionals; Function B is linear.；Function A interacts with multiple external objects; Function B is self-contained.
- 修正建议: Improve training data to include more diverse non-clone pairs with low token overlap but common syntactic patterns.；Consider using AST-based features or dataflow analysis to distinguish control flow complexity.；Implement length-based filtering to avoid comparing very long functions with short ones where token overlap is dominated by common keywords.

### case_id=4987 FN partial_functionality

- 方法: `getHTML` vs `readReferenceText`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads HTML from an HTTP URL with specified encoding and optionally saves to a file.
- B 摘要: Reads reference text from a bundle resource URL using UTF-8 encoding and returns it.
- 静态失败原因: Low token Jaccard similarity (0.235) due to different variable names, method signatures, and API calls (HttpURLConnection vs URL.openStream). The static model relies on surface-level lexical overlap and misses the conceptual similarity of reading from a URL.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB considers both as implementing the same core functionality: reading text from a URL and returning the content, ignoring differences in optional file writing, specific URL source type, and error handling.
- 共享行为: Both read text from a URL line by line；Both accumulate lines into a string buffer；Both handle character encoding；Both return the constructed string
- 行为差异: A uses HttpURLConnection and sets User-Agent; B uses URL.openStream()；A optionally writes to a file; B does not；A uses different error handling (prints stack trace); B logs and throws NoContentException；A uses StringBuilder and "\r\n"; B uses StringBuffer and "\n"
- 修正建议: Train with more diverse examples of URL reading patterns covering both HTTP and resource streams；Incorporate abstract syntax tree or data flow features to capture common I/O patterns；Use code normalization or transformation to highlight structural similarities；Add augmented samples where variable names are randomized but behavior is preserved

### case_id=4988 FN partial_functionality

- 方法: `copyFile` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Copies a file from a source path to a destination directory using NIO FileChannels.
- B 摘要: Configures a Maven-based project launch in Eclipse, which includes copying a reverse-engineering resource file to the project directory.
- 静态失败原因: Static BERT/GraphCodeBERT models rely on token-level similarity and global structural embeddings. They tend to focus on the overall method body and high-level semantics. The low token overlap (0.065) and dramatically different contexts (simple utility vs. complex launch) led the model to classify them as different. The model fails to recognize that a shared subprocess (file copying) constitutes a clone under BCB's broader criteria, because it does not decompose methods into sub-functionalities or detect partial semantic matches.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB's annotation guidelines often consider Type-4 (functional) clones, where two methods share a significant subprocess even if overall context differs. Here, both methods perform file copying, which is a core functionality. BCB likely views the file copy operations as equivalent behavior, despite differences in surrounding code.
- 共享行为: File copying operation: both methods copy a file from one location to another.
- 行为差异: Method A is a simple, standalone file copy; method B is a complex launch procedure that includes file copy as a small part.；Method A uses NIO FileChannel; method B uses IOUtils.copy and ByteArrayOutputStream.；Method A deals with arbitrary source and destination; method B copies a specific resource file (revengFile) from the bundle to the project.；Method B includes many other tasks like XML handling, property setting, and job scheduling, which are absent in A.
- 修正建议: Improve model to detect shared subroutines or sub-functionalities across methods.；Incorporate finer-grained semantic decomposition, e.g., extracting method-level functionalities or using program slicing.；Use contrastive learning that emphasizes partial semantic similarity.；Consider cross-method attention mechanisms to capture similar code fragments.

### case_id=4989 FN partial_functionality

- 方法: `doExecute` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Processes a multipart HTTP request to parse email fields and attachments, then sends an email using a Send instance.
- B 摘要: Launches a Hibernate code generation configuration by reading Maven POM files, setting Hibernate dialect properties, and handling reverse engineering files.
- 静态失败原因: Low token Jaccard (0.066) and no overlapping library/API calls, making it hard for lexical models to detect any similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as Type-4 clones due to high-level similarity in being long, complex methods that orchestrate multiple subtasks with error handling, despite different domains.
- 共享行为: Both read configuration or data input (HTTP request fields vs. launch configuration attributes)；Both perform file I/O (attachments vs. POM files)；Both include error handling and exception logging
- 行为差异: Domain: email sending vs. Eclipse plugin project setup；Data parsing: multipart form vs. XML document handling；Output: sending an email vs. modifying project resource properties
- 修正建议: Incorporate AST-based or dataflow analysis to capture structural patterns beyond tokens；Use domain-independent semantic embedding techniques

### case_id=4990 FP lexical_or_api_overlap

- 方法: `run` vs `importSequences`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a text resource from classpath and displays it in a GUI text area.
- B 摘要: Parses sequence data from a URL in FASTA format and stores names and sequences.
- 静态失败原因: Static BERT was misled by shared structural patterns (InputStream, readLine, try-catch) and high API token overlap, ignoring semantic intent.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB annotators consider these as functionally different (display vs parse), thus non-clone.
- 共享行为: Both read from an InputStream；Both process text line by line
- 行为差异: Different output: code_a sets GUI text, code_b stores lists；Different input source: classpath vs URL；Different parsing logic: plain text vs FASTA format；Exception handling: silent vs specific
- 修正建议: Enhance model with dataflow to track variable usage and output semantics；Incorporate API usage patterns that distinguish I/O for display vs parsing

### case_id=4991 FN partial_functionality

- 方法: `copyResource` vs `testCopy_inputStreamToOutputStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource from a URL or file to a destination file using manual byte-by-byte copy.
- B 摘要: Tests the IOUtils.copy method by copying from an input stream to an output stream and verifying the copy with assertions.
- 静态失败原因: Static BERT/GraphCodeBERT models rely heavily on lexical token overlap and local syntax, which is low here (Jaccard 0.114). They fail to recognize the high-level functional similarity of stream copy due to different APIs (manual byte read vs IOUtils.copy), different method names, and test wrapper code.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely labels these as clones because both implement the core functionality of copying data from an input stream to an output stream, which is a common utility pattern. The test function (B) is a direct test case for the copy operation, and the private method (A) is a concrete usage of stream copy.
- 共享行为: Both copy bytes from an input stream to an output stream
- 行为差异: Function A resolves the input from a URL or file path, while Function B uses pre-created streams.；Function A writes to a file, while Function B writes to a ByteArrayOutputStream and includes assertions.
- 修正建议: Use data-flow analysis or graph-based representations that capture stream copy patterns.；Train on clone pairs that share functional intent but differ in API usage and surrounding context.；Incorporate test-case awareness to recognize that a test method and a helper method may share core behavior.

### case_id=4992 FN partial_functionality

- 方法: `addIDs` vs `handledRun`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Adds metabolite IDs from a web database to a PeakListRow by parsing HTML and setting various fields.
- B 摘要: Downloads an updated game data XML file from a remote server and loads it into the game database.
- 静态失败原因: The low token Jaccard (0.135) indicates little lexical overlap, so a static model correctly predicted non-clone under strict criteria; it failed to recognize any broad semantic similarity that BCB might have seen.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have considered these as functional clones because both involve network I/O and data processing, but the specific functionalities are very different.
- 共享行为: Both open a URL and read data using BufferedReader；Both handle IOException
- 行为差异: Function A parses HTML for metabolite IDs and molecular weight, while Function B parses XML version headers；Function A sets fields on a PeakListRow, while Function B writes to a file and loads a game database；Function A returns an integer score, while Function B returns void；Function A handles multiple ID types (PubChem, ChEBI, etc.), while Function B only checks version
- 修正建议: Incorporate dataflow analysis to capture the purpose of the function beyond token overlap；Use task-specific fine-tuning on BCB with more emphasis on Type-4 clones；Add features for API usage patterns and I/O behavior

### case_id=4993 FP lexical_or_api_overlap

- 方法: `getUser` vs `getWebByUrl`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Loads a user from database or config file by login, creating and saving user if not found.
- B 摘要: Downloads web page content to a file and recursively processes links up to a depth limit.
- 静态失败原因: Static BERT likely overemphasized lexical overlap (e.g., URL, BufferedReader) and common try-catch patterns, ignoring the distinct high-level semantics and data flow.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labeled non-clone because the overarching functionality (user retrieval vs. web scraping) is entirely different, and shared I/O boilerplate is insufficient for clone classification.
- 共享行为: Both use URL to open a stream；Both use BufferedReader to read line-by-line；Both handle exceptions with try-catch
- 行为差异: Function A returns a User object, Function B returns void；Function A reads from local config file, Function B reads from remote URL；Function A parses tokenized lines, Function B writes raw content to file and recursively crawls
- 修正建议: Train the model on more diverse non-clone pairs with high token overlap but different semantics；Incorporate data flow analysis or graph representations to capture program semantics beyond surface syntax

### case_id=4994 FN partial_functionality

- 方法: `sendExceptionToServer` vs `read`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends exception details to a server via HTTP POST with parameter encoding and response handling.
- B 摘要: Reads a skeleton file from classpath, parses sections delimited by '---', and validates section count.
- 静态失败原因: Low token Jaccard (0.198) and different method names/parameters mislead static models. The common IO pattern (URL → BufferedReader → readLine → StringBuilder) is not lexically prominent and requires deeper semantic understanding.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label as clone due to shared pattern of opening a URL, reading lines with BufferedReader, and using StringBuilder to accumulate content, considered Type-4 (partial similarity) or Type-3 with substantial modifications.
- 共享行为: Both open a URL resource and read lines using BufferedReader.；Both use StringBuilder to accumulate string data from the read lines.；Both handle IO-related resources and errors (though differently).
- 行为差异: Function A writes data to the server before reading; Function B only reads.；Function A encodes multiple parameters; Function B only splits lines by a delimiter.；Function A prints messages to System.out; Function B throws exceptions.；Function A has a loop to read response; Function B reads all lines and accumulates sections.
- 修正建议: Use data flow analysis to detect reading loops from URL resources.；Incorporate fine-grained API usage patterns (e.g., BufferedReader.readLine) into model features.；Train with contrastive learning that emphasizes shared subroutines over top-level functionality.

### case_id=4995 FN benchmark_preference_bias

- 方法: `testCopy_readerToOutputStream_Encoding` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Test method that copies a reader to an output stream using a specific encoding and asserts content equality.
- B 摘要: Launch method that processes an Eclipse launch configuration for a Maven project, involving file operations, XML handling, property setting, and resource management.
- 静态失败原因: The static model correctly predicted non-clone because the functions have low token overlap and distinct semantics; it did not fail in this case; the BCB label appears to be a mislabel.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as a clone due to the shared use of IOUtils.copy and ByteArrayOutputStream, possibly considering it a Type-3 (semantic) clone, but the functional contexts are entirely different.
- 共享行为: Both use IOUtils.copy to copy stream data；Both instantiate a ByteArrayOutputStream
- 行为差异: Different overall purposes: testing vs. project launch；Different input types: Reader vs. InputStream；Different output usage: assertion vs. file creation and property manipulation；Function B has complex error handling, XML parsing, and configuration management absent in A
- 修正建议: Verify BCB label for this pair; likely should be non-clone；If keeping BCB label, improve model to recognize that stream utility usage alone does not imply clone

### case_id=4996 FP lexical_or_api_overlap

- 方法: `doVersionCheck` vs `downloadFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads version information from a remote URL and triggers a UI-based version check.
- B 摘要: Downloads a file from a URL to a local file with progress tracking.
- 静态失败原因: Static BERT models likely overemphasized the lexical overlap of URL/stream handling code and the similar while-loop reading pattern, while ignoring the overall functional goal and return types.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would label this as non-clone because the functions serve completely different purposes despite a superficial similarity in opening a URL stream.
- 共享行为: Both open a URL connection and read from an InputStream
- 行为差异: Function A reads lines of text and extracts version strings; function B reads binary data and writes to a file.；Function A includes UI interaction (showing wait cursor, error dialog); function B has no UI.；Function A returns void; function B returns boolean.；Function A calls another method (doVersionCheck) after parsing; function B does not.
- 修正建议: Incorporate dataflow analysis to track where data goes (e.g., written to file vs. parsed)；Consider method signatures and return types as discriminative features；Use higher-level semantic embeddings that capture program intent

### case_id=4997 FP lexical_or_api_overlap

- 方法: `readTwitterFead` vs `populateResources`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a Twitter timeline from a fixed URL using HTTP client and returns the response as a string.
- B 摘要: Loads template resources and images from classpath, reads their content, and saves them as persisted entities.
- 静态失败原因: Static BERT may have over-weighted common API tokens (BufferedReader, InputStreamReader, while, readLine) and missed the different method purpose and external dependencies (HTTP vs classpath).
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled non-clone because the overall functionality is entirely different (one is a network fetch, the other is resource initialization) despite sharing some IO boilerplate.
- 共享行为: Both use BufferedReader to read lines from an InputStream；Both use StringBuilder/StringBuffer to accumulate lines；Both handle IOException and similar exception patterns
- 行为差异: A performs a single HTTP GET request and returns the response; B reads multiple resources from classpath and saves them；A has no side effects; B saves template texts and images to a persistence layer；A returns a String; B is void and modifies state
- 修正建议: Incorporate call-graph analysis to distinguish HTTP client usage from file/resource reading；Add attention to method signature (return type, exceptions, static vs instance) and context (imports, class name)；Use data flow analysis to capture that A builds a string and returns it, while B saves objects

### case_id=4998 FN partial_functionality

- 方法: `getFile` vs `encodeFileToFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies the endpoint, and saves it to temp directory, returning the file path.
- B 摘要: Base64 encodes an input file and writes the encoded data to an output file, returning success.
- 静态失败原因: Static BERT likely focused on the distinct API calls (XML, URL, Base64) and low token overlap, missing the underlying structural similarity of file I/O operations.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as file transformation utilities sharing the common pattern of reading and writing files, despite different specific transformations, aligning with broad Type-3/Type-4 acceptance.
- 共享行为: Both read from an input source and write to an output file using Java I/O streams.
- 行为差异: A involves network download, XML parsing, and endpoint modification; B is a straightforward Base64 encoding and file copy.；A has complex error handling with multiple exception types; B has simple IOException handling.；A uses NIO channels for transfer; B uses traditional byte buffer loop.
- 修正建议: Include more training examples of diverse I/O tasks to learn abstract file processing patterns.；Use structural features like AST or dataflow to capture read-write operations regardless of specific transformations.

### case_id=4999 FP lexical_or_api_overlap

- 方法: `importRoles` vs `getRequestContent`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads an XML file from a URL, accumulates lines until a closing tag, and parses each role name to return a list.
- B 摘要: Opens a URL connection, reads the first line of content, and returns it as a string.
- 静态失败原因: The model was misled by the high lexical and structural overlap in the URL-reading boilerplate code, ignoring the distinct parsing logic and return type differences.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BigCloneBench annotations focus on functional similarity; these two functions perform entirely different tasks (parsing roles vs. retrieving raw content), so they are correctly labeled as non-clones.
- 共享行为: Both open a URL connection；Both create a BufferedReader from an InputStream；Both read at least one line from the stream
- 行为差异: A reads multiple lines and accumulates them, B reads only the first line；A parses XML to extract role names, B returns raw text；A returns a list of RoleName objects, B returns a single String；A has extensive exception handling, B throws Exception
- 修正建议: Incorporate data-flow analysis to distinguish between reading for accumulation vs. single-line retrieval；Add contrastive training on pairs with similar boilerplate but different core functionality；Increase sensitivity to control flow patterns like loops and conditional parsing

### case_id=5000 FP lexical_or_api_overlap

- 方法: `main` vs `importSequences`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Downloads a web page from a fixed URL and prints its content line by line to standard output.
- B 摘要: Imports DNA/protein sequences from a URL selected in a combo box, parsing FASTA format into internal lists.
- 静态失败原因: Static BERT overemphasized lexical overlap in common API calls (e.g., openStream, InputStreamReader, readLine, IOException) and failed to capture the high-level semantic difference in data processing (printing vs. parsing sequences).
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels as non-clone because the functions perform fundamentally different tasks (web page printing vs. sequence parsing) despite sharing URL reading API usage; BCB favors functional similarity over lexical overlap.
- 共享行为: Both open a URL stream and read data from it；Both use try-catch for IOException；Both use InputStreamReader
- 行为差异: Function a prints to console with no storage; function b stores parsed data in lists；Function a reads from a fixed URL; function b reads from user-selected URL；Function a reads lines as text; function b parses structured FASTA format；Function a has no tokenization or sequence handling; function b uses ImportHelper
- 修正建议: Train models with more contrastive examples that have similar API usage but different business logic；Incorporate AST-based difference features to detect structural divergence；Use program slicing or data flow analysis to distinguish output/state changes
