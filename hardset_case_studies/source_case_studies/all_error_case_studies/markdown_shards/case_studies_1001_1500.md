# Error Case Studies 1001-1500

- Source model: `configured-llm`
- Cases: `1001` to `1500`

### case_id=1001 FP boilerplate_overlap

- 方法: `main` vs `getTicketsForQueue`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a URL and prints its content line by line.
- B 摘要: Fetches open tickets for a given queue name by making an HTTP GET request, parsing ticket IDs, and retrieving each ticket.
- 静态失败原因: The model likely overemphasized the overlapping API tokens (BufferedReader, InputStreamReader, URL, HttpGet, etc.) and the line-by-line reading loop, ignoring the distinct high-level logic and return types. Low token Jaccard suggests limited direct overlap, but the structural similarity in the reading portion might have misled the model.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels clones based on functional similarity. These two functions have completely different purposes (simple URL content reader vs. complex ticket retrieval system), so BCB correctly marks them as non-clones despite some common I/O patterns.
- 共享行为: Both use BufferedReader to read input line by line.；Both perform HTTP-like network I/O (URL.openStream vs HttpGet).；Both use try/catch for exceptions.
- 行为差异: A is a main method that simply prints output; B returns a list of RTTicket objects.；B constructs a query with queue name and status, parses ticket IDs, and fetches individual tickets.；B includes extensive error handling and logging, while A has minimal error handling.；A uses URL.openStream synchronously; B uses Apache HttpClient with status code checking.
- 修正建议: Incorporate semantic role labeling to distinguish main methods from API wrappers.；Use control flow and data flow analysis to capture the purpose of data consumption (print vs. parse and aggregate).；Add method name and signature features to emphasize different intents.；Train on a more balanced set of negatives with similar I/O but different semantics.

### case_id=1002 FN partial_functionality

- 方法: `runScript` vs `register`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a script file from the server and returns its content as a string, with an error fallback.
- B 摘要: Registers a new user by encoding password, setting metadata, calling a remote phpBB forum registration URL, persisting the user, sending confirmation email, and returning boolean success.
- 静态失败原因: The model likely focused on the high-level semantic differences (task, return type, side effects) and overlooked the lower-level shared pattern of URL connection reading, which is a minor part of function B.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider them clones because both functions involve fetching data from a URL and handling I/O exceptions, which is a common functional pattern of 'network resource retrieval with error handling', and BCB often accepts partial functional similarity.
- 共享行为: Both open a URL connection and read data from the stream；Both handle IOExceptions with error handling or fallback
- 行为差异: runScript reads a file and returns its content; register performs complex user registration with multiple side effects；runScript returns String; register returns boolean；runScript has no input validation; register has null/type checks；register writes to database and sends email; runScript has no side effects
- 修正建议: Enhance the model to detect fine-grained behavioral similarities, such as using graph-based representations that capture subgraph patterns like URL open-read-exception handling；Incorporate multi-level semantic abstraction to recognize common I/O patterns across different tasks

### case_id=1003 FN boilerplate_overlap

- 方法: `testNetworkHTTP` vs `populateResources`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Tests network HTTP by making GET requests to external URLs and reading response lines without storing them.
- B 摘要: Loads template resources and images from classpath, reads content line by line, and saves them as persistent objects.
- 静态失败原因: The static BERT model likely focused on token-level differences and low Jaccard similarity, failing to recognize the shared I/O boilerplate pattern that BCB considers clone-worthy.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely annotates this pair as a clone because both functions exhibit the same structural pattern of reading from a URL-derived stream line by line with similar exception handling, despite different purposes. BCB's broad interpretation may accept this as a Type-3 near-miss clone.
- 共享行为: Both read lines from an InputStream using BufferedReader；Both handle IOException with try-catch；Both use URL objects to obtain input streams
- 行为差异: A makes HTTP connections to external servers; B reads local classpath resources；A discards all read data; B stores lines in a StringBuffer and saves；A uses HttpURLConnection; B uses URL.openStream()；A performs multiple sequential connections; B iterates over a list of templates then an array of images
- 修正建议: Incorporate structural similarity metrics like tree or data flow alignment；Train on BCB-style labels to adapt to their broad clone definition；Use contrastive learning to capture partial functionality similarity

### case_id=1004 FN benchmark_preference_bias

- 方法: `main` vs `addFileToTarGz`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a zip file from a URL and extracts its entries to local files.
- B 摘要: Adds a local file (or directory) to a tar.gz archive, recursively including subdirectories.
- 静态失败原因: Static BERT/GraphCodeBERT correctly predicted non-clone because the token overlap is low (Jaccard=0.14) and the methods perform fundamentally different operations (extraction vs. compression) on different archive formats (zip vs. tar).
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as a clone due to the presence of similar boilerplate code for stream chaining and archive handling, even though the high-level functionality (extraction vs. compression) is opposite. Broad Type-4 criteria might consider both as 'archive I/O' operations.
- 共享行为: Both involve reading from an input stream and writing to an output stream；Both use buffered I/O and handle byte data
- 行为差异: Code A extracts from a compressed archive (zip), while Code B creates a compressed archive (tar.gz)；Code A reads from a URL/network source, Code B reads from a local file；Code A writes multiple separate files, Code B writes a single archive file；Code B recursively processes directories, Code A only extracts flat entries
- 修正建议: Re-evaluate BCB label: these functions are not semantically similar; consider removing from clone benchmark or reclassifying as non-clone.；Use more precise semantic similarity measures that distinguish between compression and decompression operations.

### case_id=1005 FP partial_functionality

- 方法: `copyFile` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Copies a file from source to destination using NIO FileChannel.
- B 摘要: Handles action events in a GUI to update preferences and UI components.
- 静态失败原因: Likely due to partial functionality overlap (file handling in both) and long-range semantics in function B confusing the model.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB expects semantic similarity in functionality; here the functions are completely unrelated, so non-clone is correct.
- 共享行为: No shared behavior
- 行为差异: One performs file I/O, the other handles GUI events；Different control flows: simple sequential vs. complex conditional；Different inputs and outputs
- 修正建议: Improve model handling of long sequences；Focus on core functionality rather than lexical overlap；Incorporate dataflow or structure information

### case_id=1006 FN partial_functionality

- 方法: `addIDs` vs `doVersionCheck`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches metabolite data from a web service, parses HTML to extract various IDs and molecular weight, and stores them in a PeakListRow object.
- B 摘要: Fetches version information from a URL, parses lines for version and build numbers, and displays update messages or errors.
- 静态失败原因: The model likely focused on the low token Jaccard (0.17) and different domain-specific terms, causing it to miss the shared high-level I/O pattern that BCB considers sufficient for a clone.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as 'fetch and parse data from URL' tasks, and the structural similarity (try-catch with URL, BufferedReader, while loop) is high enough to be a clone despite different domains and specific parsing logic.
- 共享行为: Open URL and create InputStream；Read lines with BufferedReader in a loop；Parse each line for specific prefixes；Handle IOException with error handling
- 行为差异: A parses HTML anchors while B uses line.startsWith；A extracts multiple ID types and sets row fields; B extracts only version/build and shows UI messages；A returns an int score; B returns void；Different error handling: A logs and returns 0; B shows error dialog
- 修正建议: Incorporate high-level intent features such as API call sequences；Use control flow or data flow abstractions；Train on pairs with similar I/O patterns but different domains

### case_id=1007 FP lexical_or_api_overlap

- 方法: `readTwitterFead` vs `doVersionCheck`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a Twitter JSON feed using HttpClient and returns the content as a string.
- B 摘要: Checks for a new version by reading a URL, parsing version/build lines, and displaying appropriate messages.
- 静态失败原因: The static model likely overemphasized lexical/syntactic overlap such as BufferedReader, InputStream, try-catch patterns, and the while((line=...) != null) loop, ignoring the distinct functional purposes.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically marks as non-clones unless functions perform the same high-level task; here the tasks (Twitter feed reading vs version check) are completely different, despite some boilerplate similarities.
- 共享行为: Both read from an InputStream using BufferedReader line by line；Both use try-catch to handle IOException；Both involve URL-based network requests
- 行为差异: One uses HttpClient/HttpGet; the other uses URL.openStream()；One returns the concatenated content; the other parses specific lines and shows UI messages；One is private and non-static; the other is public and static
- 修正建议: Incorporate more semantic features, such as method name and return type context；Use dataflow analysis to distinguish different IO processing logic；Train on more diverse negative examples to reduce false positives from boilerplate sharing

### case_id=1008 FN benchmark_preference_bias

- 方法: `copy` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Copies a file from source to destination using NIO FileChannel and MappedByteBuffer.
- B 摘要: Builds a site for editing by processing XML, performing XSLT transformations, and writing multiple output files.
- 静态失败原因: The static model correctly identified them as non-clones due to low lexical overlap and different functionality, but BCB label says clone, so the model is considered to fail from the benchmark perspective.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as a clone due to a broad interpretation of Type-4 (functionally similar) clones, considering both involve file I/O, but this is a stretch and likely a benchmark error.
- 共享行为: Both perform file I/O operations (read and write files).；Both use FileInputStream and close streams in finally blocks.
- 行为差异: Function A is a simple file copy; Function B is a complex multi-step site builder.；Function A uses memory-mapped buffer; Function B uses character arrays and multiple file reads/writes.；Function A handles only two file paths; Function B takes many parameters and processes a vector of pages.
- 修正建议: Re-evaluate the BCB label for this pair; it is likely a mislabel.；Use stricter clone detection criteria that consider semantic equivalence.

### case_id=1009 FN partial_functionality

- 方法: `getFile` vs `execute`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Downloads a WSDL file from a URL, modifies the XML endpoint, and saves it to the temp directory.
- B 摘要: Saves an uploaded image file to a server directory using a database-generated ID and returns a list.
- 静态失败原因: The low token Jaccard similarity (0.06) and different method names led the model to focus on surface-level differences, ignoring the underlying file I/O pattern that BCB considered sufficient for a clone annotation.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled these as clones due to the shared high-level pattern of 'download/upload a file from an input source to a local file system' and similar boilerplate exception handling, despite vastly different domain-specific operations.
- 共享行为: Both read from an input stream and write to an output stream (file I/O)；Both handle file-related exceptions (IOException, FileNotFoundException)
- 行为差异: Function A specifically downloads and manipulates WSDL/XML content, while Function B saves an image file and interacts with a database (HomeMap)；Function A uses NIO channels for file transfer, Function B uses Apache Commons IOUtils.copy；Function A includes logging and multiple exception types; Function B prints stack traces and returns a list from a persistent layer
- 修正建议: Enhance model with data-flow analysis to capture common file I/O patterns；Use structural matching beyond token overlap, e.g., AST or control-flow graph similarity；Incorporate annotation guidelines to distinguish between generic file operations and domain-specific logic

### case_id=1010 FN partial_functionality

- 方法: `main` vs `resolvePlugins`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a KMZ (zip) file from a hardcoded URL and extracts all entries to the current directory.
- B 摘要: Downloads a plugins.xml from a URL if not cached, then resolves plugins.
- 静态失败原因: Low token overlap (0.10) and different method names/structures caused the model to miss the abstract similarity of the download-and-save pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as 'download from URL and save to disk' tasks, or the annotation might be a false positive due to noise.
- 共享行为: Both open a URL stream and write data to a file；Both involve HTTP downloads；Both use try-catch for exception handling
- 行为差异: A extracts multiple files from a zip archive; B writes a single XML file；A uses ZipInputStream with a loop; B uses IOUtils.copy；A does not check for existing files; B checks cache before download；A is a static main method; B is an instance method that calls another method
- 修正建议: Train on API-level usage patterns or data flow；Augment data with more varied download examples；Use code graphs that capture I/O operations

### case_id=1011 FP boilerplate_overlap

- 方法: `getUser` vs `lookupFutureEvents`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Retrieves a User by login from a DAO or a config file.
- B 摘要: Fetches and parses a list of future events from a Meetup API.
- 静态失败原因: Static models may over-rely on surface-level similarities such as the use of URL, BufferedReader, and looping constructs, ignoring the distinct semantic contexts and data processing logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels as non-clone because the functions have completely different purposes and only share trivial boilerplate code.
- 共享行为: Both perform I/O operations (URL/file reading).；Both use BufferedReader and InputStreamReader.；Both handle exceptions.；Both return an object (User vs List<Event>).
- 行为差异: A reads from a local config file or database; B calls a remote API.；A parses colon-delimited lines; B parses JSON.；A returns a single User; B returns a List of Events.；A handles multiple lines with StringTokenizer; B builds JSON and then parses it.
- 修正建议: Train with more diverse examples that distinguish boilerplate from core logic.；Incorporate data flow or control flow awareness to differentiate I/O patterns.；Use longer-range semantics or attention to capture overall method intent.

### case_id=1012 FP partial_functionality

- 方法: `retrieveQ` vs `getRequestContent`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads entire content of a URL as a string.
- B 摘要: Reads only the first line of a URL.
- 静态失败原因: Static BERT may have focused on API usage similarity (URL, URLConnection, BufferedReader) and structural pattern, missing the critical difference in loop vs single read.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely considers them non-clones because they have different outputs and use cases; one gets complete resource, the other gets only first line.
- 共享行为: Both open a URL connection and read from its input stream.
- 行为差异: Function A reads all lines and joins with newline; B reads only one line.；Function A prints response message to stderr; B does not.；Function A returns full content; B returns only first line.
- 修正建议: Train with more varied examples where control flow differs even with similar APIs.；Incorporate data-flow analysis to track how many times readLine is called.

### case_id=1013 FP lexical_or_api_overlap

- 方法: `actionPerformed` vs `copy`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Event handler that processes various UI commands to set preferences like Graphviz path, image scaling, date format, look-and-feel, etc.
- B 摘要: Recursively copies a file or directory using NIO FileChannel and MappedByteBuffer.
- 静态失败原因: The static BERT/GraphCodeBERT model may have been misled by the presence of common Java keywords (e.g., File, IOException, null checks) and the sheer length of function A (which was truncated in the dataset). It might have picked up on the file path handling in A and superficially matched it to B's file operations, ignoring the overall semantic context.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled this as non-clone because the functions have completely different purposes: one is a UI configuration handler, the other is a file copy utility. They share no meaningful functionality.
- 共享行为: Both deal with File objects, but with different purposes (configuration vs copying).
- 行为差异: A is a UI event handler for saving preferences; B is a file copy utility.；A interacts with a GUI (JFileChooser, Swing components); B is a static utility method with no UI.；A involves many configuration settings; B only copies files.；A has conditional branches for different commands; B has recursive directory handling.
- 修正建议: Improve model's ability to distinguish UI event handling from file utility functions.；Use better tokenization or AST-based features to capture structural differences.；Add more negative examples with trivial lexical overlap but different semantics.

### case_id=1014 FN benchmark_preference_bias

- 方法: `encodeFileToFile` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Encodes a file to Base64 and writes to another file, returning success status.
- B 摘要: Retrieves a resource as an InputStream, with caching that downloads and caches files locally.
- 静态失败原因: Static BERT models likely correctly identified the distinct method names and logically different operations (encoding vs. caching), resulting in a non-clone prediction.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider both as performing file I/O with similar boilerplate (stream handling, buffer copying, error handling), leading to a broad clone annotation.
- 共享行为: Both use InputStream/OutputStream for I/O；Both read and write bytes in loops；Both handle exceptions and close streams in finally blocks
- 行为差异: A encodes data using Base64; B does not encode；A reads from a file; B reads from a URL；A writes to output file directly; B caches to file and returns a FileInputStream；A uses a 64KB buffer; B reads byte by byte
- 修正建议: Clarify BCB annotation guidelines to avoid over-general similarity based on I/O boilerplate；Focus on substantial functional overlap rather than generic patterns

### case_id=1015 FN benchmark_preference_bias

- 方法: `register` vs `handledRun`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Registers a user by hashing password, storing in database, and creating a phpBB forum account via HTTP request.
- B 摘要: Downloads updated gamedata from a URL if a newer version is available, writing to a file.
- 静态失败原因: The static model correctly predicted non-clone because token-level overlap is low and semantic differences are clear. It did not fail; the BCB label is likely incorrect.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB annotators may have considered this a Type-4 clone due to superficial structural similarities (both use URLs, streams, and exception handling), despite different core functionalities.
- 共享行为: Both perform network I/O using URL connections and read data using BufferedReader；Both include try-catch blocks for exception handling
- 行为差异: Function A sends user registration data to a forum, Function B downloads XML gamedata；Function A persists user in database, Function B updates local game data file；Function A sends confirmation email, Function B does not；Function A uses password encoding, Function B uses version comparison
- 修正建议: Re-evaluate BCB annotation for this pair to confirm if it truly should be a clone；Increase training data with non-clone pairs that share I/O structures but differ in purpose

### case_id=1016 FP long_range_semantics

- 方法: `readData` vs `copyFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `static_summary_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Parses tokenized string inputs to populate various sets and maps for Tibetan text processing.
- B 摘要: Copies a file from source to destination using NIO FileChannel.
- 静态失败原因: The model likely failed due to the long and complex nature of readData, causing it to miss the overall semantics and over-rely on superficial patterns like method structure or common keywords (e.g., 'throw', 'try-catch'). The token Jaccard similarity is low, but the model's embeddings may have placed them close due to similar syntactic constructions (e.g., multiple variable declarations, loops).
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB would not consider these clones because their functionality is completely different; they perform distinct tasks (initialization vs. file copy) with no overlap in logic or purpose.
- 共享行为: Both are static methods that perform some operation with input data, but the operations are entirely different.
- 行为差异: readData parses tokens and populates data structures; copyFile performs file copying using channels.；readData has complex conditional logic for parsing; copyFile has straightforward transfer logic.；readData modifies static global state; copyFile returns a boolean result.；readData may throw errors; copyFile catches and logs exceptions.
- 修正建议: Incorporate dataflow analysis to distinguish between data initialization and file I/O.；Use graph-based representations that capture method-level control and data dependencies.；Include method name embeddings to leverage semantic intent.

### case_id=1017 FP lexical_or_api_overlap

- 方法: `getJSONData` vs `run`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches JSON data from a URL using HTTP and returns the parsed JSONObject.
- B 摘要: Overrides Runnable.run to load tile data from a URL, parse it, and process geometry for map display.
- 静态失败原因: Static BERT models may over-rely on lexical and API overlap (e.g., BufferedReader, InputStream, URL) and miss the distinct control flow and output behavior.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels non-clone because the functions have different purposes and the shared URL reading pattern is a common utility not sufficient for functional similarity.
- 共享行为: Both read data from a URL over HTTP using InputStream and BufferedReader.；Both handle exceptions and print stack traces.
- 行为差异: Function A simply returns a JSONObject; Function B updates data structures and processes geometry.；Function B includes duplicate request checking, URL construction, and protocol handling (file vs http).；Function B has additional logic for vector tiles and geometry collection creation.
- 修正建议: Incorporate structural features like method signatures and return types.；Use data-flow analysis to distinguish side effects.；Add training on more diverse negative examples with similar boilerplate.

### case_id=1018 FP lexical_or_api_overlap

- 方法: `postRequest` vs `getFrameworkFactory`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Sends HTTP POST request with form data and returns response body as string.
- B 摘要: Reads a service file to load and instantiate an OSGi FrameworkFactory.
- 静态失败原因: Static BERT likely overfocused on lexical overlap (e.g., 'URL', 'BufferedReader', 'readLine') and common boilerplate (try-catch, stream operations), missing the high-level semantic divergence between network communication and class loading.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would not consider these clones because they solve entirely different tasks, with different input/output signatures and distinct logic, despite sharing some boilerplate I/O patterns.
- 共享行为: Both use URL to open a connection or stream.；Both use BufferedReader to read text input.；Both handle exceptions with try-catch or throws.；Both involve string processing and closing resources.
- 行为差异: Function A sends data over network via HTTP POST, while B reads a local classpath resource.；A uses PrintWriter to write form-encoded parameters; B uses no output.；A returns a response string; B returns a FrameworkFactory object.；A returns null on exception; B throws an exception.
- 修正建议: Incorporate task-level intent or API call patterns to distinguish similar boilerplate from core logic.；Use data flow analysis to capture the purpose of data (e.g., sending vs reading).；Train on more diverse examples to reduce bias toward common Java I/O idioms.

### case_id=1019 FN partial_functionality

- 方法: `addIDs` vs `getContent`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.75`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches metabolite IDs from a web service by constructing a URL, parsing HTML, and setting fields on a PeakListRow object, returning a score.
- B 摘要: Executes an HTTP request and returns the response body as a string by reading lines with BufferedReader.
- 静态失败原因: Low token Jaccard (0.09) and significant structural differences cause static BERT models to focus on lexical mismatches and the dominant parsing logic in A, missing the underlying shared HTTP reading behavior.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels pairs with core behavior of fetching and reading web content as Type-4 clones, even if one is a generic utility and the other is a specialized parser, emphasizing the shared HTTP response reading pattern.
- 共享行为: Both perform HTTP GET requests to retrieve web content.；Both read the HTTP response line by line using BufferedReader.；Both handle IO operations and exceptions.
- 行为差异: A uses URL.openStream; B uses HttpClient and HttpUriRequest.；A parses HTML for specific patterns and extracts multiple fields; B only concatenates all lines.；A returns an int score; B returns a String.；A modifies a PeakListRow object; B has no side effects.
- 修正建议: Incorporate high-level code summarization to capture overall intent.；Use data flow and control flow graphs (e.g., GraphCodeBERT) to recognize shared IO patterns.；Train with contrastive learning to identify similar functionality despite low token overlap.

### case_id=1020 FN partial_functionality

- 方法: `getHTML` vs `importRoles`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches HTML from a URL and optionally saves to a file, returning the HTML content as string.
- B 摘要: Reads an XML-like structure from a URL, parsing role names and returning a list of RoleName objects.
- 静态失败原因: Static BERT models rely heavily on token similarity and structural embeddings. The low Jaccard index (0.26) and different method names, output types, and processing logic cause the model to underestimate functional similarity, missing the shared underlying behavior of URL reading and line processing.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considers these Type-4 clones because both perform network I/O and line-oriented processing, despite different return types and parsing logic. The partial functional overlap in reading from a URL and processing lines may be considered sufficient for clone annotation.
- 共享行为: Both open a URL and read content line by line；Both use BufferedReader and InputStreamReader for reading；Both accumulate lines in a buffer/StringBuilder/StringBuffer
- 行为差异: Code A returns a String of full HTML; Code B returns a list of parsed RoleName objects；Code A can write the HTML to a file; Code B does not write to any file；Code A does not parse XML tags; Code B parses until a specific closing tag；Code A appends newline after each line unconditionally; Code B appends a newline only between tags
- 修正建议: Incorporate higher-level semantic abstractions that capture common operations like network I/O and line iteration.；Use graph-based representations to model control and data flow, highlighting shared I/O patterns.；Train on a broader set of partial-functionality clone pairs to improve recognition of Type-4 clones.

### case_id=1021 FN partial_functionality

- 方法: `copy` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a file from source to destination with validation and stream handling.
- B 摘要: Builds a site for editing by reading XML and other files, processing them, and writing output files.
- 静态失败原因: Static BERT likely relied on lexical overlap and short-range patterns; with a low token Jaccard of 0.11 and the second function being much longer and truncated, it failed to detect the underlying file I/O similarity that BCB considered.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have considered both as involving file reading and writing with error handling, viewing the second function's core data transfer as conceptually similar to a copy operation, despite the additional complexity.
- 共享行为: Perform file I/O operations (reading and writing)；Handle IOException and other exceptions；Use stream-based reading and writing
- 行为差异: copy is a simple file duplication with no transformation；buildSiteForEdit involves complex multi-step site generation with XML transformation and multiple file operations；buildSiteForEdit has a significantly larger scope and many additional parameters and logic
- 修正建议: Incorporate dataflow analysis to identify common I/O patterns；Use structural embeddings that capture high-level operations like file reading/writing；Consider methods that compare functionality at a coarse granularity

### case_id=1022 FP lexical_or_api_overlap

- 方法: `doVersionCheck` vs `loadURL`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Checks for a newer version of jEdit by downloading a version file from a URL and comparing build numbers.
- B 摘要: Downloads a file from a URL with optional HTTP Basic authentication, writes it to a temporary file, and updates a status label with progress.
- 静态失败原因: Static models may have been misled by high lexical overlap of common patterns like opening a URL, BufferedReader, and reading lines, failing to capture the high-level semantic intent difference without deeper understanding of surrounding API calls (jEdit properties vs. file writing).
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled as non-clone because the functions serve entirely different purposes despite sharing low-level I/O patterns; the core functionality (version check vs. file download) is distinct.
- 共享行为: Both open a URL and read lines from an input stream using BufferedReader；Both handle IOException
- 行为差异: A parses lines for version/build info; B writes all lines to a temporary file；A compares versions and shows UI messages; B updates a status label with file size；B includes authentication logic; A does not；A shows/hides wait cursor; B does not hide cursor
- 修正建议: Incorporate semantic features such as API call contexts (e.g., jEdit-specific calls vs. file writing)；Use graph-based representations that capture data flow differences (e.g., writing to file vs. comparing strings)；Train on more diverse examples to distinguish utility functions

### case_id=1023 FN partial_functionality

- 方法: `main` vs `httpRequestByPOST`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Main method that sends a hardcoded POST request to RenRen API and prints the response.
- B 摘要: Generic method that sends a POST request with given parameters and returns the response as a string, with error handling.
- 静态失败原因: Static BERT models rely on token-level similarity; low Jaccard (0.096) and different vocabulary (e.g., HttpURLConnection vs HttpClient, RenRenPostParameters vs NameValuePair) caused the model to miss the abstract functional similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label these as clones because both implement the core pattern of sending an HTTP POST request and reading the response, accepting differences in libraries and parameter handling as broad Type-3/Type-4 similarity.
- 共享行为: Both perform HTTP POST requests；Both read the response line by line using BufferedReader；Both set request method to POST
- 行为差异: A is a static void main method; B is a non-static method returning String；A uses HttpURLConnection; B uses Apache HttpClient；A has hardcoded parameters; B accepts parameters via List<NameValuePair>；A prints response to console; B returns response string or null
- 修正建议: Add training examples with diverse implementations of HTTP POST；Incorporate data flow analysis to identify common patterns；Use API call aware embeddings to generalize across different libraries

### case_id=1024 FP lexical_or_api_overlap

- 方法: `getPasswordMD5` vs `perform`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Computes MD5 hash of the password field and returns it as a hex string.
- B 摘要: Processes a Struts action form for classification, handling session attributes, request parameters, and XML communication.
- 静态失败原因: The static BERT model likely overemphasized superficial lexical overlaps (e.g., 'StringBuffer', 'return null', 'try-catch') and missed the vast semantic gap due to lack of dataflow understanding.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels based on strict semantic equivalence; these functions have entirely different purposes and logic, so they are not clones.
- 共享行为: Both use try-catch blocks for exception handling.；Both contain loops (for, while).；Both use StringBuffer to build strings.
- 行为差异: Function A is a simple password hashing method; Function B is a complex web action with multiple steps.；Function A has no parameters; Function B takes ActionMapping, ActionForm, HttpServletRequest, HttpServletResponse.；Function A uses MessageDigest; Function B uses URLConnection, BufferedReader, etc.；Function A returns a String or null; Function B returns an ActionForward.
- 修正建议: Incorporate structural or dataflow analysis to distinguish different functionality.；Use type-aware features (e.g., method signatures, class context) to avoid matching across domains.；Train on more diverse cross-project data to reduce false positives from common API usage patterns.

### case_id=1025 FP lexical_or_api_overlap

- 方法: `read` vs `getFrameworkFactory`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads camera log from a URL, parses each line into CameraLogRecord objects, and sorts the records.
- B 摘要: Loads a FrameworkFactory from a META-INF resource by reading a line containing class name and instantiating it.
- 静态失败原因: The static BERT model likely focused on overlapping API sequences (BufferedReader, URL, readLine, try-finally) and structural similarity, missing the distinct semantic purposes and return types.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels as non-clone because although both read from URL, their high-level functionality and output differ completely; one is for log processing, the other for OSGi service loading.
- 共享行为: Both open a URL and read lines using BufferedReader；Both use try-finally to close the BufferedReader
- 行为差异: Code A processes camera log records; Code B retrieves a framework factory；Code A outputs void (adds to records list); Code B returns a FrameworkFactory；Code A parses and catches LogParseException; Code B instantiates via Class.forName；Code A sorts records; Code B has no sorting
- 修正建议: Incorporate method-level semantic features like purpose or domain；Use data flow analysis to track output types and exception handling；Add attention to method names and comments for context

### case_id=1026 FP lexical_or_api_overlap

- 方法: `getUser` vs `handledRun`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Loads a user by login from database or config file, parsing colon-delimited fields.
- B 摘要: Downloads gamedata XML from a URL, checks version, and updates local file if newer.
- 静态失败原因: Static BERT model likely overemphasized lexical and API surface overlap (e.g., URL, BufferedReader, try-catch, InputStream) while missing the high-level semantic difference in purpose.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clones because the overall functionality is dissimilar: one is for user authentication, the other for game update; shared I/O patterns are incidental.
- 共享行为: Opens a URL and reads data using BufferedReader；Handles exceptions with try-catch blocks；Uses InputStreamReader and URL.openStream()
- 行为差异: Function A reads user credentials from a config file; Function B downloads and writes XML game data.；Function A uses StringTokenizer for parsing; Function B uses String.split and writes to file.；Function A saves user to DAO; Function B updates game database version.；Function B has a finally block to reload game data; Function A does not.
- 修正建议: Enhance training with more diverse negative examples that share API calls but differ in task.；Incorporate functional role or project context information.；Use flow-sensitive or dataflow features to capture I/O direction (read vs. write).

### case_id=1027 FN partial_functionality

- 方法: `execute` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Executes file conversion by reading from a source file and writing to a destination file using a delegate method, with resource cleanup.
- B 摘要: Builds a website for editing by processing pages, transforming XML, and writing output files, with extensive debugging and error handling.
- 静态失败原因: Static BERT models like GraphCodeBERT rely heavily on token overlap and local structure; the low Jaccard similarity (0.068) and different method names led to a non-clone prediction, missing the abstract functional similarity of file I/O patterns.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely labels this as a Type-4 clone because both functions perform core file transformation tasks (read, transform, write) with similar resource management patterns, despite different application contexts.
- 共享行为: Both involve file I/O operations (reading and writing).；Both manage resources (streams, readers, writers) with try-catch-finally.；Both handle exceptions (IOException, etc.) and close resources in finally.
- 行为差异: A is a simple file conversion wrapper; B is a complex site generation with multiple transformations.；A uses FileReader/FileWriter; B uses many different stream types and transformers.；B has extensive debugging and logging; A has minimal logging.；B iterates over multiple pages and uses properties; A handles a single file pair.
- 修正建议: Enhance model with dataflow analysis to capture read/write operations across different APIs.；Use function-level decompilation to abstract I/O patterns.；Incorporate external knowledge about common boilerplate code (e.g., try-catch-finally with streams).

### case_id=1028 FP lexical_or_api_overlap

- 方法: `readPage` vs `sendPost`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a web page line by line, optionally skipping comment lines starting with '#', and returns the content as a string.
- B 摘要: Sends an HTTP POST request with parameters to a URL and returns the response body as a string.
- 静态失败原因: The model likely overemphasized the common boilerplate code for reading from a URL (BufferedReader, InputStreamReader, while loop) and ignored the distinct HTTP method and parameter handling. This is a typical failure due to lexical or API overlap dominating the representation.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labeled these as non-clones because the core functionality differs (GET vs POST, with additional parameter handling in B). Even under broad Type-3/4 similarity, the behavioral differences in network I/O and logic outweigh the superficial shared pattern of reading from a URL.
- 共享行为: Reads from a URL connection using BufferedReader and InputStreamReader；Concatenates lines read from the stream into a result string；Returns the concatenated string
- 行为差异: Function A performs a simple GET request via url.openStream(); Function B performs an HTTP POST request with parameters；Function A optionally ignores lines starting with '#'; Function B does not filter lines；Function B sets request properties and writes the parameter to the output stream; Function A has no output；Function B catches exceptions and prints a message; Function A throws exceptions
- 修正建议: Enhance the model to distinguish between different HTTP methods (GET vs POST) and data flow (output streams vs input-only).；Incorporate method signature and static/instance context as additional features.；Use graph-based representations that capture the order and purpose of API calls (e.g., URLConnection vs HttpURLConnection).

### case_id=1029 FP lexical_or_api_overlap

- 方法: `doVersionCheck` vs `importSequences`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Checks for a newer version of the application by fetching and parsing a remote version file.
- B 摘要: Imports biological sequences from a URL by parsing a FASTA-like format.
- 静态失败原因: Overemphasized lexical and API overlap (URL, InputStream, IOException, line reading) and similar control flow structure (try-catch, while loop), missing the domain-specific semantics.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clone because functions have completely different purposes and logic, with only shallow I/O similarities.
- 共享行为: Both open an InputStream from a URL and read line-based data；Both handle IOException
- 行为差异: Different domain: version checking vs. sequence import；Different parsing logic: key-value lines vs. FASTA parsing；Different outputs: UI messages vs. sequence storage；Different exception handling: only IOException vs. multiple exceptions
- 修正建议: Incorporate method names and class context as features；Use data flow analysis to identify different data transformations；Add domain-specific keywords or constants to distinguish tasks

### case_id=1030 FP boilerplate_overlap

- 方法: `read` vs `getFrameworkFactory`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a skeleton file from classpath, splits it into sections by '---' markers, and validates the section count.
- B 摘要: Reads a service configuration file from classpath, locates the first non-comment line, and instantiates a class named by that line as a FrameworkFactory.
- 静态失败原因: The model may have over-relied on the shared boilerplate pattern (getResource, BufferedReader, InputStreamReader, throw Exception) and missed the diverging core logic, indicating a failure to capture long-range semantic dependencies.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB annotates based on functional similarity, and these two functions have clearly different purposes (parsing vs. class loading), so they are not considered clones even under broad Type-4 criteria.
- 共享行为: Both load a resource from the classpath using getResource()；Both open a BufferedReader on an InputStreamReader from the URL's input stream；Both read lines sequentially in a loop；Both handle exceptions and throw a general Exception on failure
- 行为差异: Function A builds string sections and checks section count; Function B instantiates a class from a line；Function A uses StringBuilder to accumulate lines; Function B only processes the first valid non-comment line；Function A expects multiple '---' separators; Function B ignores comment lines (starting with '#')；Function A throws an exception if section count doesn't match; Function B throws if no factory is found
- 修正建议: Incorporate dataflow analysis to track the actual operations on the read data；Use structure-aware features that distinguish different control flows after common preamble；Train on functional summaries rather than raw code tokens

### case_id=1031 FN benchmark_preference_bias

- 方法: `copyFile` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Copies a file from input to output with error handling and stream closing.
- B 摘要: Launches a NexOpen project configuration by processing pom files, generating resources, and scheduling install actions.
- 静态失败原因: The static BERT model correctly predicted non-clone because the functions are distinct; token overlap is low and semantics differ. So it didn't fail; instead, the BCB label is likely incorrect.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: The BCB label may be erroneous, or perhaps it considers that both involve stream copying and file operations, but the contexts are too dissimilar to be considered clones.
- 共享行为: Both perform file I/O operations (stream reading/writing) but at very different scales and contexts.
- 行为差异: Completely different inputs (File vs ILaunchConfiguration)；Different purposes (file copy vs project launch)；Different complexity (simple copy vs multi-step configuration)；Different error handling (return boolean vs throw exceptions)
- 修正建议: Investigate BCB annotation for this pair; possibly re-label as non-clone；Ensure benchmark labels reflect functional equivalence

### case_id=1032 FN lexical_or_api_overlap

- 方法: `runDynusT` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.2`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Runs DynusT simulation by copying executable and model files to a temp directory, executing the program with a timeout, and optionally cleaning up.
- B 摘要: Builds a website for editing by processing pages with XML transformations, reading/writing files via FTP, and applying string replacements to generate output files.
- 静态失败原因: Static BERT/GraphCodeBERT models rely heavily on token overlap and local syntactic patterns. The very low token Jaccard (0.049) and distinct vocabularies (simulation vs. web editing) led the model to correctly predict no clone, but this contradicts the BCB label, likely due to the model's inability to capture abstract workflow similarities.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may have labeled as clone due to both functions being complex orchestrations of file operations and process execution, possibly viewed as high-level workflow clones (Type-4) despite different domains.
- 共享行为: Both involve file I/O operations (copying, reading, writing)；Both iterate over collections of items (files or pages)；Both have conditional logging/debugging statements；Both throw exceptions on error conditions
- 行为差异: A runs an external executable with timeout; B performs in-memory XML transformations；A only copies files; B reads, transforms, and writes files with complex string operations；A has an optional cleanup step; B does not clean up；A works with a fixed set of files; B processes a variable number of pages with dynamic content
- 修正建议: Incorporate higher-level program structure or workflow embeddings；Use cross-domain semantic similarity learning；Fine-tune on BCB's specific annotation preferences

### case_id=1033 FN benchmark_preference_bias

- 方法: `sendExceptionToServer` vs `PageLoader`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.6`
- 推荐路线: `preference_memory_with_manual_audit`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Sends exception details to a server via HTTP POST and prints the response.
- B 摘要: Fetches the contents of a web page via HTTP GET and stores it in a field.
- 静态失败原因: The static model likely focused on token-level differences (low Jaccard) and structural differences (different HTTP methods, different parameter handling), missing the high-level semantic similarity of performing HTTP I/O. The model may be biased towards lexical overlap and syntactic similarity.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: None
- 共享行为: Both use java.net.URL to open HTTP connections；Both read from an input stream；Both handle I/O (close streams)
- 行为差异: Function A uses HTTP POST to send data, while Function B uses HTTP GET to receive data；Function A builds a complex query string with encoded parameters, Function B simply reads all lines；Function A handles response and prints status, Function B does not process response beyond storing it
- 修正建议: Incorporate semantic similarity measures that capture high-level intent (e.g., using code embeddings that understand API usage patterns)；Use a model that considers function-level semantics rather than token overlap.

### case_id=1034 FP boilerplate_overlap

- 方法: `getVersion` vs `startScript`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Retrieves the latest version string from a hardcoded URL by reading the first line.
- B 摘要: Fetches a script from a URL attribute and appends its content to a dialog buffer.
- 静态失败原因: The model likely overfitted to the common URL-reading boilerplate (BufferedReader, InputStreamReader, readLine) and ignored method signatures, return types, and side effects. It mistook structural similarity for semantic equivalence.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the functions serve distinct high-level purposes (version retrieval vs script loading) despite sharing a low-level I/O pattern. The annotation prefers semantically equivalent or highly similar functionality, not just common idioms.
- 共享行为: Both open a URL connection and read lines using BufferedReader and InputStreamReader.；Both use a while loop to read lines from the stream.；Both handle exceptions (generic Exception in A, IOException in B).
- 行为差异: A returns a String version; B is void and modifies dialog.script.；A uses a fixed URL; B gets URL from an attribute.；A catches Exception and returns null; B catches IOException and exits the program.；A is static; B is instance method with side effects (dialog.beginScript/endScript).
- 修正建议: Include method names, return types, and parameter types in the representation.；Use data flow analysis to differentiate outputs and side effects.；Add negative examples of similar boilerplate with different semantics.

### case_id=1035 FN lexical_or_api_overlap

- 方法: `copyResource` vs `copy`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.95`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource (URL or file path) to a destination file using byte streams.
- B 摘要: Copies a source file to a destination file using character streams.
- 静态失败原因: Low token Jaccard (0.295) due to different method names, I/O class names (FileReader vs FileInputStream, FileWriter vs FileOutputStream), and different parameter signatures, causing the static model to miss the structural similarity.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB often labels Type-3/Type-4 clones as positive, and both functions perform the same high-level task of copying data from input to output, despite differences in source type and stream type.
- 共享行为: Both read from an input source and write to an output file；Both use a read-write loop until end of stream；Both close the input and output streams after copying
- 行为差异: Function A handles both URL and file sources, while B only handles file sources；Function A uses byte streams (InputStream/OutputStream), B uses character streams (FileReader/FileWriter)；Function A has different exception handling (throws Exception), B also throws Exception but with different signature；Function A takes no parameters (uses instance fields), B takes two File parameters
- 修正建议: Normalize API calls to abstract I/O operations；Use structural or semantic embeddings that focus on control flow rather than lexical tokens；Incorporate variable renaming and API mapping in preprocessing

### case_id=1036 FN benchmark_preference_bias

- 方法: `copyResource` vs `doExecute`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Copies a resource from a URL or file to a destination file.
- B 摘要: Processes an HTTP multipart request to send an email, handling file uploads and form fields.
- 静态失败原因: The model correctly predicted non-clone because token and structure overlap are minimal (Jaccard ~0.05) and method names/signatures differ significantly.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as a clone based on very broad criteria like 'both involve I/O and exception handling', which is a weak overlap but could be considered Type-4 under some interpretations.
- 共享行为: Both read from an input stream and write to an output stream；Both include exception handling and stream closing
- 行为差异: A performs a simple file copy; B performs complex email sending with form processing；A has no conditional logic for file type; B parses multipart content and builds attachments；A is a short utility method; B is a long controller method in a web framework
- 修正建议: Re-evaluate BCB label for this pair; if it is a false positive, remove it from clone set；Improve annotation guidelines to avoid overly broad Type-4 classifications

### case_id=1037 FP partial_functionality

- 方法: `getWebByUrl` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches a web page by URL, writes its HTML content to a local file, and recursively processes links.
- B 摘要: Performs a Google image search, parses the HTML response to extract image URLs, and updates a GUI with the first image.
- 静态失败原因: Static BERT likely over-relied on lexical overlap of URL opening and BufferedReader pattern, missing the semantic divergence in data processing and final output.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB labeled these as non-clones because their core functionality is different (web page saving vs. image search) despite shared boilerplate.
- 共享行为: Opens a URL connection and reads response using BufferedReader
- 行为差异: A writes page content to a file; B extracts image URLs and updates GUI；A recursively processes links; B does not；A uses URLConnection; B uses HttpURLConnection with User-Agent；B parses HTML with string splitting; A only reads lines
- 修正建议: Train with more emphasis on functional output and purpose；Incorporate data-flow or post-processing steps to distinguish final use of fetched data

### case_id=1038 FP boilerplate_overlap

- 方法: `doBody` vs `readData`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Writes file content to HTTP response output stream using IOUtils.copy.
- B 摘要: Parses static string constants and a file to populate multiple sets and mappings for Tibetan transliteration initialization.
- 静态失败原因: The model likely overgeneralized from common boilerplate patterns like try-catch-finally and I/O stream usage, ignoring the distinct core logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB annotates based on semantic similarity of overall functionality; here functions perform entirely different tasks (web response vs. data loading), so they are clearly non-clones.
- 共享行为: None
- 行为差异: Purpose: HTTP response handling vs. data initialization；Input: request/response objects vs. static strings and file；Output: writes to response stream vs. populates in-memory data structures；Algorithm: simple stream copy vs. complex tokenization and mapping
- 修正建议: Train the model to focus on task-specific logic rather than structural boilerplate；Incorporate dataflow or dependency analysis to capture semantic differences

### case_id=1039 FP partial_functionality

- 方法: `read` vs `readUNI`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads camera log from URL, parses each line into CameraLogRecord, adds to list, sorts, and logs.
- B 摘要: Reads tab-delimited data from URL, parses each line to extract id and description, and adds them to a vector.
- 静态失败原因: Static BERT/GraphCodeBERT models may overweigh lexical and API overlap (e.g., URL, openStream, while loop, try-finally) and miss the semantic differences in parsing logic and output behavior, leading to a false positive.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely labels non-clone because the functions have different input/output parameters, different parsing formats, and different exception handling, despite sharing a high-level read-from-URL pattern.
- 共享行为: Both read from a URL；Both open a stream and read line by line；Both parse each line and collect results into a collection；Both close the stream in a finally block
- 行为差异: A parses into CameraLogRecord object; B concatenates id and desc as string；A sorts the records list; B does not sort；A logs info messages; B does not log；A throws IOException; B catches MalformedURLException and Exception
- 修正建议: Incorporate data flow analysis to track how parsed data is used；Consider method signatures and parameter types；Use AST-based differencing to capture structural differences；Include context like imports or class names

### case_id=1040 FP boilerplate_overlap

- 方法: `getLinksFromURLFast` vs `createDialogArea`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Extracts hyperlinks from a web page given a URL.
- B 摘要: Creates a dialog area for displaying license text in an SWT application.
- 静态失败原因: Static BERT models may rely on token similarity and structural patterns. Both methods have similar boilerplate code (URL, BufferedReader, StringBuffer) and control flow (while loop reading lines). The model might have been misled by the similar I/O structure and overlooked the completely different domain logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely considers these non-clones because the main functionality is entirely different (web scraping vs. GUI creation), even though they share common I/O patterns.
- 共享行为: Both use URL to open a stream and read lines with BufferedReader.；Both build a string from the read lines using StringBuffer.
- 行为差异: A parses HTML for links and returns vectors of links and texts; B displays the text in a GUI widget and returns a Composite.；A uses regex for pattern matching; B uses Browser or Text widget.；A has performance tracking; B has error handling and resource cleanup.
- 修正建议: Incorporate semantic understanding of the overall goal, not just token-based similarity.；Use dependency analysis to differentiate between web scraping and GUI building.；Consider the method's return type and usage context.

### case_id=1041 FN benchmark_preference_bias

- 方法: `loadExistingAntlibs` vs `register`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Loads ant library definitions from classloader resources by reading URLs line by line.
- B 摘要: Registers a user by encoding password, setting authorities, creating a forum user via HTTP, persisting to database, and sending confirmation email.
- 静态失败原因: Static BERT/GraphCodeBERT models rely on token overlap and local context; the low token Jaccard (0.13) indicates little lexical similarity, so the model correctly identified them as non-clones. The model failed to match BCB's lenient partial functionality standard because it lacks understanding of abstract behavioral patterns.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled these as clones due to superficial structural similarity (both reading from streams, looping, exception handling) and both being part of 'load/register' operations in a framework context, but the actual functionality is entirely different, making it an overly broad Type-4 annotation.
- 共享行为: Both use BufferedReader to read lines from an input stream (URL or resource).；Both catch IOException and throw RuntimeException.；Both have a while loop reading lines until null.
- 行为差异: Function A loads antlib definitions; Function B registers a user with multiple steps.；Function A reads from classloader resources; Function B reads from a remote URL.；Function A processes each line as a package name; Function B processes a single line as a forum ID.；Function B performs many side effects (password encoding, persistence, email) not present in A.
- 修正建议: Improve model to recognize high-level structural patterns (like stream reading + exception handling) as clone indicators.；Train with a more diverse set of Type-4 examples where functionality differs but control flow is similar.；Incorporate data flow or program dependency graphs to distinguish genuine behavioral similarity from coincidental structural overlap.

### case_id=1042 FP lexical_or_api_overlap

- 方法: `readUNI` vs `parse`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Reads tab-separated lines from a URL and extracts id and description, adding them as concatenated strings to a provided vector.
- B 摘要: Parses a data file from a URL or local file, handling configurable delimiters, headers, type conversion, and returns a DataSet object.
- 静态失败原因: Static BERT models may have been misled by overlapping keywords such as 'URL', 'openStream', 'while', and try-catch patterns, while missing the substantial differences in method signature, return type, and overall logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this pair as non-clone because the methods have distinct signatures, different levels of complexity, and serve fundamentally different purposes beyond the shared I/O boilerplate.
- 共享行为: Both read data from an external source (URL or file).；Both iterate over lines of input.；Both use try-catch-finally for resource management and error handling.
- 行为差异: Function A only reads from URL; B can read from URL or local file.；Function A uses tab delimiter exclusively; B supports configurable delimiters.；Function A appends to an external list; B returns a new DataSet.；Function A has no header handling or type conversion; B handles headers and converts types.
- 修正建议: Incorporate method signature and return type as features.；Use structure-based embeddings (e.g., AST or data-flow graphs) to capture semantic differences beyond surface API usage.；Train on datasets with fine-grained clone types to penalize boilerplate-only similarities.

### case_id=1043 FN benchmark_preference_bias

- 方法: `doGet` vs `checkInputStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.2`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Handles HTTP GET requests to retrieve and serve a portal page with permission checks and logging.
- B 摘要: Compares an InputStream's content to a byte array for testing purposes.
- 静态失败原因: Static model correctly identified non-clone due to low token overlap and distinct APIs; error is dataset noise.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB label may be an error or based on an extremely broad notion of 'reading and validating input', which is not standard.
- 共享行为: Both involve reading and processing data, but at a very abstract level.
- 行为差异: Different domain: HTTP request handling vs. unit test utility.；No common I/O or processing logic.；Different error handling and output.
- 修正建议: Verify BCB annotation for correctness.；Improve filtering of trivial pairs with no functional similarity.

### case_id=1044 FP lexical_or_api_overlap

- 方法: `test` vs `readData`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Test method that reads an XML file, initializes a traffic simulation engine, runs simulation steps, and prints vehicle dynamics.
- B 摘要: Private static method that parses string lists via StringTokenizer to populate various sets and maps for Tibetan transliteration, including file reading and error handling.
- 静态失败原因: Static BERT may have overemphasized lexical similarities such as repeated use of 'HashSet', 'StringTokenizer', and loop structures, while missing the distinct semantic contexts (traffic simulation vs. transliteration setup).
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels as non-clone because the functions have entirely different purposes and contexts, with no meaningful functional overlap beyond trivial use of common Java constructs.
- 共享行为: Both involve parsing and processing data inputs.；Both use collections like HashSet and Map.；Both have loops for iteration.
- 行为差异: A is a unit test for traffic simulation; B is a data initialization routine for Tibetan transliteration.；A uses InputStream and XML reading; B uses string tokens and file reading.；A outputs simulation results; B populates lookup structures.；A is short and focused; B is long and complex with multiple branches.
- 修正建议: Incorporate dataflow analysis to trace how inputs are used across the function.；Use graph-based representations that capture control dependencies and external API calls.；Add a lightweight semantic filter, e.g., check if functions belong to same domain (test vs. utility).

### case_id=1045 FN long_range_semantics

- 方法: `main` vs `loadMFileViaWeb`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Main method that constructs hardcoded API parameters, sends POST request to RenRen, and prints response.
- B 摘要: Loads a MATLAB file from a URL, reads content line by line, parses into UserFunction, and returns it.
- 静态失败原因: The low token Jaccard similarity (0.0948) and surface-level differences in API usage (PostParameter vs FunctionParser) and method signatures caused the model to miss the structural I/O pattern, which is not captured by token-level features.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely considered them clones because both implement a common pattern of reading data from a URL line by line using standard Java I/O, which qualifies as broad Type-3/Type-4 similarity despite different purposes.
- 共享行为: Opens a URL connection；Creates InputStream and wraps in BufferedReader；Reads lines in a while loop；Handles IOException (though differently)
- 行为差异: A uses HttpURLConnection with POST and many parameters; B uses URL.openStream() (GET)；A prints response; B returns a parsed UserFunction；A is main method with hardcoded data; B is a utility method with parameters；Different error handling: A throws IOException; B catches Exception and logs
- 修正建议: Incorporate data flow and control flow analysis to capture I/O pipelines；Use graph-based code representations (e.g., AST or PDG) to highlight structural similarities；Leverage method-level semantics via API role embeddings

### case_id=1046 FN benchmark_preference_bias

- 方法: `copyResource` vs `onlyFileCopy`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `preference_memory_with_manual_audit`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Copies a resource (URL or file) to a destination file using byte stream.
- B 摘要: Copies a file to another file using NIO FileChannel for efficient bulk transfer.
- 静态失败原因: Static BERT relies on lexical and API-level similarity; the low token Jaccard and very different API calls (InputStream vs FileChannel) cause it to miss the functional equivalence.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB likely labels this as clone (Type-4) because both functions perform the same core functionality of copying data from an input source to an output file, despite different APIs and input handling.
- 共享行为: Both copy content from an input source to an output file.；Both close streams/channels after copying.
- 行为差异: A accepts URL or file source, B only accepts File source.；A uses byte-by-byte stream, B uses NIO channel with chunked transfer.；A throws generic Exception, B throws IOException.；A copies entire content in one loop, B handles large files in chunks.
- 修正建议: Incorporate data-flow analysis to detect that both functions read and write bytes.；Add training on more Type-4 functional clone pairs with low syntactic similarity.；Use graph-based representations that capture I/O operations and data flow.

### case_id=1047 FP lexical_or_api_overlap

- 方法: `readUNI` vs `main`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.85`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads tab-separated lines from a URL and stores selected fields into a vector.
- B 摘要: Reads all lines from a URL and prints each to standard output.
- 静态失败原因: A static BERT model may over-rely on lexical and API-level overlap (both use URL, openStream, and loops over lines), ignoring the distinct data processing logic and output behavior.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the functions perform different tasks: one extracts structured data for storage, the other outputs raw lines. Despite similar I/O patterns, the core functionality differs.
- 共享行为: Both open a URL and read lines from it.
- 行为差异: Function A parses tab-separated fields and stores them in a vector; Function B prints each line as-is.；Function A expects a specific format with three fields per line; Function B does not parse content.；Function A handles exceptions silently; Function B throws IOException.；Function A is an instance method; Function B is static main.
- 修正建议: Incorporate data flow analysis to distinguish parsing versus simple output.；Use contrastive learning on pairs that share API usage but differ in semantics.

### case_id=1048 FP partial_functionality

- 方法: `getLinksFromURLFast` vs `getContent`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Takes a URL string, fetches the HTML page, extracts all anchor links and their text using regex, and returns a Vector array containing the lists of links and texts.
- B 摘要: Takes an HttpUriRequest, executes it, reads the response content line by line, and returns the full content as a String.
- 静态失败原因: The static BERT model likely overemphasized common structural elements (reading loop, use of StringBuffer, exception handling) and superficial API overlap (URL, InputStream, BufferedReader), while missing the distinct output types and the regex-based parsing in A.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely labels this as non-clone because the core purpose differs: A is for hyperlink extraction, B is for content retrieval. Even by relaxed standards, the functional divergence is too significant.
- 共享行为: Both open an HTTP connection；Both read response line by line；Both append lines to a StringBuffer
- 行为差异: A parses HTML to extract links and texts; B returns raw content；A returns Vector[] of links and texts; B returns a single String；A uses URLConnection; B uses HttpClient；A uses custom RE class for regex; B uses standard BufferedReader and InputStreamReader
- 修正建议: Incorporate dataflow analysis to track how the read data is processed (e.g., regex matching vs plain concatenation)；Train on examples that differentiate content retrieval from link extraction；Add structural supervision on return types and intermediate operations

### case_id=1049 FN benchmark_preference_bias

- 方法: `doGet` vs `copyToDir`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.5`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Handles HTTP GET request to retrieve and render a web page, with optional caching to a file.
- B 摘要: Copies a file to a specified directory using file streams.
- 静态失败原因: Static BERT/GraphCodeBERT models rely on token-level overlap and structural similarity; the low token Jaccard (0.098) and very different control flows lead to a correct non-clone prediction, but BCB's unconventional labeling causes a misclassification.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled as clone due to presence of file writing in both functions (A caches page to file, B copies file), considering it a partial functionality overlap (Type-4).
- 共享行为: Both involve file I/O operations (writing to a file)；Both include try-catch blocks for IOException
- 行为差异: A primarily deals with HTTP request handling, page rendering, and user permissions; B purely copies a file；A has complex logic for page lookup, caching, and statistics; B is straightforward file copy；A writes generated page content to a temp file; B copies an existing file to a new location
- 修正建议: Re-evaluate BCB labels for such pairs to ensure consistency with broad clone definitions；Enhance models with dataflow analysis to detect shared subfunctionality like file I/O；Consider using fine-grained clone detection that can recognize partial functionality clones

### case_id=1050 FN lexical_or_api_overlap

- 方法: `doGet` vs `createOutputStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.2`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Handles HTTP GET requests for pages: resolves page ID, checks permissions, logs page access, and handles caching.
- B 摘要: Creates a BufferedWriter from a ZIP file by copying all entries except 'content.xml', then adding a new content.xml entry with UTF8 encoding.
- 静态失败原因: Static BERT relies on lexical and syntactic overlap; the token Jaccard is very low (0.0746), and there is no semantic similarity captured by pre-trained embeddings, so it correctly predicted non-clone, but BCB label might be incorrect.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may have labeled as clone due to both being I/O-intensive methods from the same project, or due to benchmark annotation errors, as there is no functional similarity.
- 共享行为: Both use exception handling (IOException)；Both involve file I/O operations (one HTTP response, one file streams)
- 行为差异: Function A processes HTTP requests; B processes ZIP files.；A includes user permission checks; B does not.；A uses logging extensively; B does not.；A has complex caching logic; B has simple streaming.
- 修正建议: Include data flow analysis to detect remote semantic similarities；Use graph-based models like CodeGraphNet to capture implicit relations；Cross-validate BCB annotations to reduce noise

### case_id=1051 FP lexical_or_api_overlap

- 方法: `read` vs `downloadFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a camera log from a URL, parses each line into CameraLogRecord objects, and stores them in a sorted list.
- B 摘要: Downloads a file from a URL to a local destination with progress tracking and returns success status.
- 静态失败原因: The static model likely overemphasized the lexical and API overlap (both use URL, openStream, read loops) and similar control flow, while missing the semantic differences in data processing (parsing vs writing) and final outputs (list vs file). The model is not sensitive to dataflow and output types.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels these as non-clones because the overall functionality differs fundamentally: one is for parsing log files, the other for downloading files. The small lexical and structural overlap does not imply clone status in BCB's task-oriented annotation.
- 共享行为: Both read data from a URL using input streams.；Both use a while loop to read data until end of stream.；Both close the stream after reading.
- 行为差异: A parses lines into structured objects, B writes raw bytes to a file.；A sorts the parsed records, B does not sort.；A logs progress, B updates a progress bar via MessageFrame.；A returns void, B returns boolean.
- 修正建议: Incorporate dataflow analysis to distinguish between different output sinks (collection vs file).；Include high-level task classification (parsing vs download) as additional features.；Train on more diverse pairs to reduce false positives from common I/O patterns.

### case_id=1052 FP lexical_or_api_overlap

- 方法: `executePost` vs `load`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Sends an HTTP POST request with parameters and returns the response body.
- B 摘要: Loads content from a pastebin URL using HTTP GET and returns the response as a string.
- 静态失败原因: High lexical overlap (URL, openConnection, BufferedReader, readLine) and similar structure misled the model into predicting a clone despite behavioral differences.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels non-clones when functions have distinct input/output behavior and purpose, despite shared patterns; here the methods differ in HTTP method and parameter handling.
- 共享行为: Both open a URL connection and read the response using BufferedReader.
- 行为差异: A uses POST with request body; B uses GET without body.；A sets multiple HTTP headers; B does not.；A returns null on error; B returns empty string and shows dialog.；A disconnects connection in finally; B does not explicitly disconnect.
- 修正建议: Increase weighting of control/data flow differences.；Incorporate check of HTTP method or parameter usage.；Use finer-grained AST comparison to distinguish setup code.

### case_id=1053 FN partial_functionality

- 方法: `copyResource` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource (URL or file) to a destination file using byte-by-byte copying.
- B 摘要: Copies a file to another file using buffered I/O with error handling.
- 静态失败原因: Low token Jaccard similarity (0.228) due to different APIs, variable names, and error handling patterns misled the model; it likely lacked understanding of high-level I/O semantics.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels functions as clones if they perform the same high-level task despite differences in implementation details; both functions aim to copy a resource to a file.
- 共享行为: Both copy data from a source to a destination file using InputStream and OutputStream.
- 行为差异: Function A can read from a URL or a local file, while B only reads from a local file.；Function A copies byte by byte; B uses an intermediate buffer for efficiency.；Function A throws a checked Exception; B catches specific exceptions and throws an unchecked runtime exception.；Function A is an instance method relying on instance fields; B is a static method taking parameters.
- 修正建议: Use data augmentation to create variants with diverse APIs but same functionality.；Incorporate AST or data-flow features to capture structural similarities independent of surface tokens.；Train with contrastive learning on BigCloneBench to emphasize shared overall behavior over exact code match.

### case_id=1054 FN benchmark_preference_bias

- 方法: `modifyApplicationMessage` vs `convert`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.6`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Reads a properties file for a given locale, updates or appends a message entry, and writes back.
- B 摘要: Converts an ACRNEMA stream file to DICOM format by parsing, adding UIDs, and handling pixel data with optional inflation.
- 静态失败原因: The static BERT model correctly identified these as non-clones based on semantic dissimilarity, but the BCB label contradicts this, indicating a possible benchmark annotation mistake.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB likely labeled this as a clone due to broad Type-4 similarity (both involve file transformation with conditional logic), but the functional purposes are entirely distinct, so it may be a labeling error.
- 共享行为: Both perform file I/O (read and write) with conditional processing.
- 行为差异: Different domains: properties file management vs. medical image conversion.；Different file formats and parsing logic.；Different output generation: text properties vs. binary DICOM with pixel data.；Different error handling and checks.
- 修正建议: Review and correct the BCB annotation for this pair.；Include more contextual clues to distinguish domain-specific operations.

### case_id=1055 FN benchmark_preference_bias

- 方法: `getFile` vs `forBundle`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, optionally modifies its endpoint, and writes to a local file.
- B 摘要: Retrieves Velocity template files from a bundle, packages them into a JAR with a manifest, and installs the plugin.
- 静态失败原因: Low token overlap (0.0889) and different control structures led the model to correctly predict non-clone; the BCB label is likely an annotation error.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have considered both as resource retrieval and processing involving file I/O and stream copying, but the functional purpose is very different.
- 共享行为: Both use file I/O operations；Both use try-catch for error handling；Both create temporary files
- 行为差异: getFile downloads from a remote URL; forBundle reads from a local bundle；getFile modifies XML; forBundle creates Zip entries；getFile returns a file path; forBundle installs a plugin；Different error handling styles (throw AxisFault vs printStackTrace)
- 修正建议: Re-evaluate BCB annotation for this pair; consider excluding if no clear semantic similarity

### case_id=1056 FP lexical_or_api_overlap

- 方法: `readVersion` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a version property file from system resources to extract version, revision, and compile date.
- B 摘要: Performs a Google image search for the current track and parses image URLs from the HTTP response.
- 静态失败原因: Static BERT models like CodeBERT may over-rely on token overlap (e.g., 'URL', 'BufferedReader', 'readLine', 'catch') and structural patterns, leading to high similarity scores despite divergent functionality. The model likely captured the common API usage and control flow but missed the distinct parsing logic and domain-specific operations.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels non-clones when functions have different purposes and output semantics, despite similar IO boilerplate. Here, one reads local version info, the other does web image search, so they are functionally distinct.
- 共享行为: Both open a URL connection and read data line-by-line using BufferedReader.；Both parse each line for specific patterns and extract substrings.；Both use try-catch-finally for resource management and error handling.；Both set instance variables as a side effect.
- 行为差异: Function A reads from a local resource; Function B makes an HTTP network request.；A parses key-value pairs with '=' separator; B splits on a complex regex and handles URL encoding.；A stores three scalar values; B accumulates a list of image URLs.；A uses URL.openStream(); B uses HttpURLConnection with custom headers.
- 修正建议: Incorporate data-flow analysis to track variable dependencies and distinguish different output structures.；Use contrastive learning with more diverse negative examples that share API usage but differ in functional role.；Add attention to domain-specific tokens (e.g., 'version', 'image') to differentiate purpose.

### case_id=1057 FP boilerplate_overlap

- 方法: `main` vs `copy`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Parses a Prolog file, generates adapter classes and annotations, and writes them into a JAR file.
- B 摘要: Copies a file from source to destination using NIO FileChannel.
- 静态失败原因: The model may have been misled by shared boilerplate patterns (e.g., try-catch-finally, File I/O, IOException) and common Java idioms, ignoring the vastly different high-level purposes and code lengths.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels these as non-clones (0) because they have no semantic overlap; BCB-style annotation requires some functional similarity, which is absent.
- 行为差异: Function A performs complex transformation of Prolog data into Java classes; B performs simple byte-level file copy.；Function A involves multiple I/O operations, class loading, and serialization; B uses direct channel transfer.；Function A has conditional debug output and prints messages; B is silent.；Function A returns void but may exit early with print statements; B throws IOException.
- 修正建议: Incorporate function name or signature features to capture intent.；Improve detection of high-level semantic roles via summarization or API call patterns.；Use more discriminative negative sampling to reduce false positives from boilerplate.

### case_id=1058 FN partial_functionality

- 方法: `copyResource` vs `streamContains`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copy a resource from a URL or file to a destination file by reading byte-by-byte.
- B 摘要: Assert that an InputStream contains a given string by reading the stream into a byte array and checking.
- 静态失败原因: Low token Jaccard (0.113) indicates little lexical overlap; static BERT models rely on lexical and structural similarity and may miss the abstract IO copy pattern due to different APIs and logic.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label as clone because both functions involve reading from an InputStream and writing to an OutputStream, which is a common IO pattern, but the overall functionality differs significantly.
- 共享行为: Read from an InputStream；Write to an OutputStream
- 行为差异: copyResource writes to a file and handles source existence; streamContains writes to a ByteArrayOutputStream and performs a string assertion；copyResource reads byte-by-byte; streamContains uses IOUtils.copy for bulk transfer；Different parameters and overall purpose
- 修正建议: Use dataflow-aware models to capture the data transfer pattern；Incorporate functional semantics or intent understanding；Consider models that focus on IO operations and resource handling

### case_id=1059 FN benchmark_preference_bias

- 方法: `writeConfiguration` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Writes a configuration resource to a Writer, copying the content from a URL stream.
- B 摘要: Builds a website for editing by reading XML, performing XSLT transformations, string replacements, and writing output files for each page.
- 静态失败原因: The static BERT model correctly predicted non-clone (0) due to low token overlap (Jaccard 0.065) and vastly different semantics, so it did not fail; the BCB label is likely erroneous.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB likely labeled this as a clone due to both methods performing I/O and 'writing' to output, but this is too broad and not representative of functional similarity.
- 共享行为: Both perform I/O operations involving reading from streams and writing to outputs
- 行为差异: Function A is a simple resource copy; Function B involves XML parsing, XSLT transformation, string replacement, file system operations, and complex control flow over multiple pages.
- 修正建议: Re-examine BCB annotation for this pair; consider removing or correcting the label to non-clone.

### case_id=1060 FP lexical_or_api_overlap

- 方法: `readZoneIDs` vs `load`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a local resource file containing zone IDs and returns a set of integers.
- B 摘要: Downloads XML content from a pastebin URL given an ID and returns it as a concatenated string.
- 静态失败原因: Static BERT/GraphCodeBERT likely over-relied on token overlap (URL, openStream, readLine) and boilerplate structure, ignoring the fundamental difference in data types and remote vs local access.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels as non-clone when functions perform distinct domain-specific tasks, even if they share boilerplate I/O patterns.
- 共享行为: Both open a URL/stream；Both read lines in a loop；Both return a collection/string built from lines
- 行为差异: Input: A takes a zone file name; B takes a string ID；Source: A reads local resource; B fetches from remote HTTP；Output: A returns HashSet<Integer>; B returns String；Processing: A parses each line to integer; B concatenates lines as strings
- 修正建议: Enhance training data with examples that distinguish boilerplate from semantics；Incorporate data flow analysis to track how variables are used (e.g., Integer vs String)；Add negative examples with high lexical but low semantic similarity

### case_id=1061 FP boilerplate_overlap

- 方法: `createDialogArea` vs `readUNI`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Creates a dialog area, reads a license file from a bundle resource, and displays it in a browser or text widget.
- B 摘要: Reads a tab-separated file from a URL, parses lines, and adds ID-description pairs to a vector.
- 静态失败原因: Static BERT models rely heavily on lexical and structural token patterns; the shared boilerplate of opening a URL, reading lines, exception handling, and closing streams created high token overlap, obscuring the semantic differences.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled non-clone because the methods have different names, different contexts (UI vs data parsing), and different overall functionality, despite sharing some I/O boilerplate.
- 共享行为: Open an InputStream from a URL；Read lines from the stream；Handle IOException with try-catch-finally；Close the stream in finally block
- 行为差异: Method A sets up a UI dialog area; method B is a data parsing utility；A uses BufferedReader; B uses Scanner with tab delimiter；A outputs to UI widget; B adds to a vector；Different method signatures and return types
- 修正建议: Incorporate method signature and return type into the representation；Use dataflow analysis to distinguish UI setup from data parsing；Apply task-aware embeddings that capture the method's role in the class

### case_id=1062 FN boilerplate_overlap

- 方法: `decodeFileToFile` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Decodes a Base64 input file into an output file using buffered stream I/O.
- B 摘要: Builds a website for editing by transforming XML and writing output files with debug tracing.
- 静态失败原因: The static model likely relied on token overlap and method signatures, which are very different, leading it to correctly classify them as non-clones; the low Jaccard and distinct functionality made it miss the potential boilerplate-based clone.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may have labeled them as clones due to the generic pattern of reading from an input stream and writing to an output stream with buffering and exception handling, which can be considered a broad Type-3/4 clone.
- 共享行为: Both perform file input/output operations with buffered streams；Both use try-catch-finally for error handling and close streams in finally blocks
- 行为差异: A is a simple Base64 decode and copy; B involves complex XML transformation and property handling；A returns a boolean success flag; B throws exceptions and returns void；B uses DOM, Transformer, and loops over multiple pages; A has none of that
- 修正建议: Train model to distinguish core functionality from common I/O boilerplate；Incorporate data flow analysis to capture the actual transformation logic；Use larger context or call graph to understand method purpose

### case_id=1063 FN benchmark_preference_bias

- 方法: `doGet` vs `copy`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Handles HTTP GET requests to retrieve and render a page based on the SelectedPage parameter, with permission checks and caching.
- B 摘要: Copies a file from a source to a destination using FileChannel transfer, creating parent directories if needed.
- 静态失败原因: Static BERT correctly predicted non-clone (0), so it did not fail; the BCB label is mistaken.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB label (1) is likely a dataset error; there is no functional similarity between HTTP page serving and file copying, even under broad Type-4 clone definitions.
- 共享行为: None; the functions are completely unrelated in purpose and operation.
- 行为差异: A is an HTTP servlet handler with complex business logic; B is a simple file copy utility.；A interacts with a web request/response, portal objects, and properties; B only handles file I/O.；A has extensive error handling, logging, and caching; B has minimal exception handling.
- 修正建议: Verify BCB ground truth labels for this pair; if confirmed as error, correct the dataset.；Improve clone detection benchmarks to avoid spurious positives from unrelated functions.

### case_id=1064 FP boilerplate_overlap

- 方法: `readData` vs `copyFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Reads and parses configuration strings (tops, lefts, etc.) into various sets and validates input sequences for a Tibetan/Sanskrit text processing system.
- B 摘要: Recursively copies a file or directory using file I/O streams.
- 静态失败原因: The model likely focused on generic programming structures (loops, try-catch) or incorrectly matched boilerplate patterns, ignoring the completely different semantics.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels as non-clone because the functions have no functional overlap; one is a data initialization routine and the other is a file system utility.
- 行为差异: Function A initializes data structures from string tokens; Function B copies files/directories.；Function A uses StringTokenizer and HashSet; Function B uses File, FileInputStream, FileOutputStream.；Function A involves complex validation logic; Function B is straightforward file copying.；No common domain or purpose.
- 修正建议: Improve training data diversity to reduce false positives from unrelated functions.；Incorporate control-flow and data-flow analysis to capture semantic intent.；Use more robust tokenization that distinguishes domain-specific APIs (e.g., StringTokenizer vs. FileInputStream).

### case_id=1065 FP lexical_or_api_overlap

- 方法: `getFrameworkFactory` vs `getFullScreenUrl`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Loads an OSGi FrameworkFactory from a META-INF/services configuration file using classpath resource and reflection.
- B 摘要: Extracts a fullscreen video URL from a YouTube page by parsing the HTML response for specific parameters.
- 静态失败原因: Static BERT/GraphCodeBERT models are sensitive to lexical and structural overlap. Both functions share common API calls (URL, BufferedReader, readLine, try-catch) leading to high embedding similarity, but they fail to capture the distinct semantic intents.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BigCloneBench typically labels pairs as non-clones when the core functionality differs significantly, even if there is structural similarity in the I/O boilerplate. Here, one loads a service provider and the other scrapes a web page, so they are considered functionally distinct.
- 共享行为: Both open a URL connection and read lines using BufferedReader；Both parse input lines to extract relevant information；Both return a string or throw an exception on failure
- 行为差异: Function A uses reflection to instantiate a class; B extracts video parameters and constructs a URL；Function A throws an exception if no factory is found; B returns an empty string on failure；Function A reads from a classpath resource; B reads from a web URL；Function A has no GUI side effects; B modifies progress bar and prints debug output
- 修正建议: Integrate data-flow or control-flow analysis to differentiate reading from classpath vs. network；Use type information to distinguish reflection vs. string manipulation；Include comment or method name semantics more heavily

### case_id=1066 FP boilerplate_overlap

- 方法: `readData` vs `copyFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.99`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Parses multiple comma-separated strings into sets and maps and reads a configuration file to populate data structures for Tibetan/Sanskrit processing.
- B 摘要: Copies a file from source to destination using NIO FileChannel with proper resource management.
- 静态失败原因: The model may have been misled by the overlapping keywords (try, catch, IOException, finally, null) present in both functions, despite their low token Jaccard.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would likely not consider these as clones since they have different method names, parameters, and overall logic; only superficial similarity in exception handling pattern.
- 共享行为: Both use try-catch/finally blocks；Both involve file I/O operations；Both are static methods
- 行为差异: readData parses strings and populates data structures; copyFile does not；readData reads configuration data; copyFile copies file content；readData uses StringTokenizer and multiple collections; copyFile uses FileChannel；readData has no parameters; copyFile takes two File parameters
- 修正建议: Incorporate data flow and control flow analysis to distinguish different operations；Use model that captures method-level semantics beyond token overlap；Consider method length and complexity divergence

### case_id=1067 FN partial_functionality

- 方法: `testNetworkHTTP` vs `run`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Makes multiple HTTP GET requests to external URLs, sending sensitive data via query parameters, and reads responses.
- B 摘要: Makes a single HTTP GET request to a local URL and reads the response.
- 静态失败原因: The model likely relies on token-level overlap (Jaccard=0.262) and may not capture the common pattern of HTTP request and streaming read. The differences in method names, variable names, and specific URL strings cause low similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB considers the core functionality of making an HTTP GET request and consuming the response as sufficient for clone classification, ignoring differences in specific URLs, parameters, and minor implementation details.
- 共享行为: Opens an HTTP connection to a URL；Reads response line by line using BufferedReader until null
- 行为差异: Number of requests: multiple vs one；URLs and parameters differ (sensitive data vs local)；Error handling: code A catches IOException only, code B catches MalformedURLException and IOException；Connection management: code A uses HttpURLConnection and disconnects in finally, code B uses URL.openStream() and closes reader in try block
- 修正建议: Use representation that captures API call sequences and data flow, e.g., graph-based models；Augment training data with functionally similar but lexically diverse examples；Incorporate knowledge of common programming patterns (like HTTP GET clones)

### case_id=1068 FN benchmark_preference_bias

- 方法: `doGet` vs `testCodingEmptyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Handles HTTP GET request to retrieve and serve a web page with caching and logging.
- B 摘要: Tests that a LengthDelimitedEncoder correctly encodes data when transferring from an empty file.
- 静态失败原因: Static BERT/GraphCodeBERT likely focused on low token overlap (0.0478) and different method names, correctly predicting non-clone.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as clone due to both involving file creation and stream operations, but functionality is very different; possibly an annotation error.
- 共享行为: both create temporary files
- 行为差异: A is a servlet handler for pages with permission checks; B is a unit test for an encoder；A uses HTTP request/response; B uses streams and channels；A has complex page rendering logic; B is a simple test assertion
- 修正建议: Re-annotate this pair as non-clone；Improve benchmark consistency by cross-checking with human experts

### case_id=1069 FP boilerplate_overlap

- 方法: `readUNI` vs `importSequences`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads tab-separated descriptions from a URL and adds them to a vector.
- B 摘要: Imports sequences from a URL in FASTA-like format into lists.
- 静态失败原因: The model over-relied on token and structural overlap (e.g., InputStream, URL, openStream, while loop, Scanner) and failed to capture the distinct semantic intents due to limited context understanding.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled non-clone because the functions have different domain-specific tasks (description extraction vs sequence import) with different parsing logic, despite sharing boilerplate I/O patterns.
- 共享行为: Both open a URL stream and read input；Both use try-catch for exception handling；Both parse input line by line
- 行为差异: ReadUNI parses tab-separated fields and extracts id+description；ImportSequences parses sequence headers and reads sequence data；Different output data structures (Vector<String> vs ArrayList<String>)；Different input formats (tab-separated vs FASTA-like)
- 修正建议: Incorporate data flow and control flow analysis to distinguish parsing logic；Use code summarization to capture high-level intent；Increase training on diverse tasks to reduce boilerplate bias

### case_id=1070 FN lexical_or_api_overlap

- 方法: `copyResource` vs `copyResourceToFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copy a resource (URL or file) to a destination file using a byte-by-byte loop, with minimal error handling.
- B 摘要: Copy a resource file to a destination file using a utility method and robust try-finally resource management.
- 静态失败原因: Static BERT models rely on token overlap (Jaccard 0.2075) and surface forms. The low lexical overlap and different API calls (URL.openStream vs MatsimResource.getAsInputStream, manual loop vs IOUtils) likely cause the model to miss the semantic equivalence. Additionally, the difference in exception handling patterns (missing finally vs robust finally) further misleads the model.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB considers these Type-3 clones because both implement the same core functionality—copying a resource to a file—despite differences in source resolution, error handling, and copy implementation. The conceptual similarity overrides implementation details.
- 共享行为: Both copy a resource (source) to a file (destination).；Both use InputStream and OutputStream to perform the copy.；Both close streams after copying.
- 行为差异: Source resolution: A uses getResource (URL or file), B uses MatsimResource.getAsInputStream (library-specific).；Copy method: A uses manual byte reading/writing, B uses IOUtils.copyStream (likely buffered).；Error handling: A throws Exception with no finally, B throws IOException with finally block and printStackTrace.；Parameterization: A has no parameters (uses instance fields), B takes resource and destination filenames as parameters.
- 修正建议: Use AST-based or data-flow based representations to capture structural similarities.；Increase training data with Type-3/Type-4 clones having different APIs but same intent.；Incorporate control-flow and exception-handling patterns into the model.

### case_id=1071 FP lexical_or_api_overlap

- 方法: `sendRequest` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Sends a compressed XML request via HTTP to a configurable server and returns an empty string.
- B 摘要: Fetches Google Images search results for an artist/album and extracts image URLs into a list.
- 静态失败原因: Static BERT likely overfocused on common HTTP keywords (URL, HttpURLConnection, InputStream) and missed the vast differences in data flow and intent.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would label as non-clone because the functions have distinct purposes and only share superficial HTTP boilerplate; the token Jaccard is low (0.0988).
- 共享行为: Both open an HTTP connection；Both read from an InputStream；Both handle exceptions
- 行为差异: A sends a compressed request, B performs a GET；A uses GZIP compression, B does not；A returns a String, B returns void and populates a list；A parses XML with JDOM, B parses HTML with string splitting
- 修正建议: Incorporate data flow analysis to distinguish different request-response patterns；Use models that capture project-specific or domain-specific knowledge；Add structural features like method signature, return type, and external dependencies

### case_id=1072 FP boilerplate_overlap

- 方法: `main` vs `buildDeb`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Parses a Prolog file, generates adapter classes and resources, and assembles them into a JAR.
- B 摘要: Creates a Debian package archive from control and data files using the 'ar' format.
- 静态失败原因: The static model likely over-relied on surface-level I/O operations (FileInputStream, OutputStream, read/write loops) and missed the distinct domain-specific logic and library calls.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB annotates based on high-level functional equivalence; these two functions perform entirely different tasks (adapter generation vs package building) despite sharing low-level I/O patterns.
- 共享行为: Both read input files using FileInputStream；Both write to an output file using OutputStream；Both use buffered I/O with byte arrays
- 行为差异: A parses Prolog and generates Java classes; B creates an ar archive with specific entries；A uses complex framework classes (PrologParser, ClassWriter, etc.); B uses only standard I/O；A involves multiple phases and error handling; B is a straightforward file copy
- 修正建议: Incorporate program structure or control flow graphs to capture task-level semantics；Use type-aware representations to distinguish between different library/framework usage；Add negative sampling for pairs with similar I/O but different high-level functionality

### case_id=1073 FN boilerplate_overlap

- 方法: `doVersionCheck` vs `File2String`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Checks for a new version of jEdit by reading a version file from a URL and comparing build numbers.
- B 摘要: Reads a file either from local disk or classpath and returns its content as a string.
- 静态失败原因: Static BERT/GraphCodeBERT likely over-relied on token overlap and structural patterns (e.g., BufferedReader, readLine, catch blocks) without capturing the high-level semantic goal, leading to a false negative.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may have labeled as clone due to similar boilerplate I/O code (reading lines, handling exceptions) and both being utility methods, but the functional intent is entirely different.
- 共享行为: Both open an input stream and read lines using BufferedReader；Both handle I/O exceptions with try-catch blocks
- 行为差异: Input source: URL vs local file/classpath；Output: void (displays GUI message) vs String (returns file contents)；Error handling: shows GUI message vs prints to stderr and exits；Purpose: version checking vs file reading to string
- 修正建议: Incorporate method-level context like names and comments；Use data-flow or control-flow graphs to differentiate purposes；Train with contrastive learning on functional semantics

### case_id=1074 FP boilerplate_overlap

- 方法: `executePost` vs `getRequestContent`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Executes an HTTP POST request with parameters, reads the entire response, handles exceptions by returning null, and disconnects in a finally block.
- B 摘要: Performs an HTTP GET request and returns only the first line of the response, throwing exceptions and disconnecting after reading.
- 静态失败原因: A static BERT/GraphCodeBERT model may rely on token overlap and structural patterns. Both functions share common boilerplate (URL, HttpURLConnection, BufferedReader, getInputStream) which the model might interpret as similar, while missing the semantic differences in HTTP method and response length. The model can be biased toward the presence of API calls rather than their specific configuration.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels these as non-clones because the functions have significantly different HTTP methods (POST vs GET), response processing (full vs first line), error handling, and parameter handling. The low token Jaccard (0.21) and distinct functional behavior make them a non-clone in BCB's judgment.
- 共享行为: Both open an HTTP connection to a URL using HttpURLConnection.；Both read from the input stream using BufferedReader and InputStreamReader.；Both close the reader and disconnect the connection.
- 行为差异: Function A uses POST method and sends URL parameters; function B uses GET method without parameters.；Function A reads the entire response line by line appending carriage returns; function B reads only the first line.；Function A handles exceptions by printing stack trace and returning null; function B throws exceptions.；Function A has a finally block to disconnect; function B disconnects outside finally.
- 修正建议: Incorporate data flow analysis to distinguish between POST (output stream used) and GET (input only).；Add attention to method signatures and parameters, such as the presence of urlParameters.；Train on finer-grained distinction of HTTP operations, e.g., by including request method strings and response reading loops.

### case_id=1075 FN partial_functionality

- 方法: `getEncoding` vs `File2String`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Extracts character encoding from a URL by examining HTTP headers and HTML content.
- B 摘要: Reads the entire content of a file (from filesystem or classpath) into a string.
- 静态失败原因: The static BERT/GraphCodeBERT model likely failed due to low token overlap (Jaccard 0.20) and a focus on distinct API calls (e.g., getHeaderFields vs. FileInputStream) and return types (String encoding vs. String content). The model missed the abstract stream-reading pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely labels this as a Type-4 (semantic) clone based on the shared high-level pattern: reading from an input stream, processing text, and returning a derived string. The specific output (encoding vs. full content) is considered a minor difference under broad semantic similarity.
- 共享行为: Both open an input stream and read lines using BufferedReader and InputStreamReader.；Both handle I/O exceptions and close resources.
- 行为差异: Function A returns only the encoding (or default), while Function B returns the entire file content.；Function A uses URLConnection and parses headers; Function B uses FileInputStream or ClassLoader.；Function A may stop early upon finding encoding; Function B reads all lines and concatenates.；Function B prints to stdout and calls System.exit on failure; Function A does not.
- 修正建议: Train models to recognize high-level I/O patterns and abstract data flow, e.g., by augmenting with program slicing or using graph representations that capture control-flow structure.；Increase training data with pairs that share partial functionality but differ in specifics.

### case_id=1076 FP boilerplate_overlap

- 方法: `executeHttpGet` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Execute HTTP GET request and return the response as a JSONObject.
- B 摘要: Perform Google image search, parse HTML to extract image URLs, and update UI with first image.
- 静态失败原因: The model may have focused on the common boilerplate pattern (HttpURLConnection, BufferedReader, while loop) and ignored the differing high-level functionality and data flow.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely considers these non-clones because their overall purpose and behavior differ significantly; one is a generic JSON fetcher, the other is a specific image search with UI updates.
- 共享行为: Both perform HTTP GET request and read response line by line using BufferedReader.
- 行为差异: executeHttpGet returns a JSONObject, googleImageSearch is void and updates UI.；googleImageSearch parses HTML to extract image URLs, while executeHttpGet returns raw response as JSON.；googleImageSearch has side effects (modifies global list and UI), executeHttpGet is side-effect-free.；Error handling: executeHttpGet throws exception, googleImageSearch catches and shows dialog.
- 修正建议: Train model to recognize functional purpose beyond common API usage patterns.；Incorporate control flow and data flow analysis to differentiate utility functions from domain-specific ones.

### case_id=1077 FN lexical_or_api_overlap

- 方法: `byReference` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.4`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Creates a temporary file from an InputStream and returns a DigitalObjectContent wrapping it.
- B 摘要: Builds a website for editing by reading XML, transforming it, and writing output files using multiple configuration parameters.
- 静态失败原因: Very low token Jaccard similarity (0.0545) and large disparity in code length (small vs. long) likely caused the model to miss any latent semantic connection.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may label this as a clone due to both functions performing file I/O with streams, a broad Type-4 similarity, but the functional purposes are entirely different.
- 共享行为: Both involve reading from an InputStream and writing to a file
- 行为差异: Function A is a small utility returning an object; Function B is a large void method performing site generation；Function A handles exceptions by printing stack trace and throwing IllegalStateException; Function B throws multiple declared exceptions and has complex control flow；Function A uses temporary files; Function B writes to specified output paths
- 修正建议: Incorporate structural or control flow similarity metrics；Use code summarization or abstract syntax tree (AST) matching to capture high-level intent；Improve handling of long methods with better positional encoding in transformer models

### case_id=1078 FN partial_functionality

- 方法: `getFile` vs `unJarStart`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Downloads a WSDL file from a URL, modifies an XML attribute, and saves it to a temporary location.
- B 摘要: Extracts files from a JAR archive that match a starting path prefix and writes them to a directory.
- 静态失败原因: Low token overlap and different API usage (URL vs JarFile) mislead the model into predicting non-clone.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider these as Type-4 semantic clones under a broad definition of 'retrieve and save file' despite different sources and processing.
- 共享行为: Both perform file I/O: reading from a source and writing to a file.；Both create directories or files as needed.；Both use try-catch error handling.
- 行为差异: Source type: URL vs JarFile.；Operation: XML modification vs simple copy.；Output: single file vs multiple files.；Error handling: throws AxisFault vs prints stack trace.
- 修正建议: Enhance model with I/O operation patterns (e.g., read-modify-write vs read-copy).；Include context of file source (remote vs archive).；Use data flow analysis to capture high-level intention.

### case_id=1079 FN lexical_or_api_overlap

- 方法: `main` vs `run`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Builds an API request with multiple parameters, sends it via HTTP POST, and prints the response line by line.
- B 摘要: Opens a connection to a fixed local URL via HTTP GET, reads the response line by line into a variable without using it, and handles exceptions silently.
- 静态失败原因: The static BERT/GraphCodeBERT method likely relied on token and structural similarity, which is low (Jaccard 0.13). It failed to capture the high-level functional similarity due to different API usage, variable names, and lack of data flow abstraction.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB often considers Type-3/Type-4 clones where two functions perform the same high-level task (HTTP request and response reading) despite differences in details, and may annotate such pairs as clones.
- 共享行为: Creates a URL object；Opens an HTTP connection or stream；Reads the response line by line；Involves standard Java I/O operations
- 行为差异: HTTP method: POST vs GET；URL construction: dynamic with parameters vs fixed hardcoded URL；Parameter handling: uses PostParameter objects vs none；Output: prints response lines vs silently discards
- 修正建议: Incorporate data flow analysis to identify common I/O patterns；Use graph-based representations to abstract control and data flow；Apply API-level mapping to recognize equivalent operations；Include high-level semantics from method names or documentation

### case_id=1080 FN partial_functionality

- 方法: `runInternal` vs `invoke`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads OPDS catalogs and books over HTTP with pagination and partial loading.
- B 摘要: Invokes a remote method via HTTP POST with JSON serialization and retry logic.
- 静态失败原因: Low token overlap (0.11) and long code length; static models may miss high-level structural similarity in HTTP handling patterns.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider them clones due to both implementing HTTP client patterns with request/response handling, despite different domain specifics.
- 共享行为: Both make HTTP requests and handle response codes；Both read response body content；Both handle exceptions and errors
- 行为差异: A focuses on OPDS catalog parsing and book download, B on RPC invocation with JSON；A uses HttpURLConnection, B uses Apache HttpClient；A includes content-disposition parsing and partial loading, B includes retry and service discovery
- 修正建议: Use data-flow or control-flow features to capture shared HTTP handling patterns；Include more examples of broad clones with low lexical similarity in training

### case_id=1081 FP lexical_or_api_overlap

- 方法: `getRequestContent` vs `getVersion`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads the first line from a given URL using HTTP.
- B 摘要: Reads the last line from a fixed URL to get version, with error handling.
- 静态失败原因: High lexical overlap (similar code structure with URL, BufferedReader, etc.) led the model to focus on structural similarity, ignoring semantic differences in parameterization and line reading logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely considered them non-clones because the input parameter vs fixed URL and different reading behavior (first line vs last line) indicate distinct functionality.
- 共享行为: Both open a URL connection；Both read input using BufferedReader；Both return a string read from the URL
- 行为差异: A reads only the first line; B reads all lines and returns the last；A takes a URL parameter; B uses a hardcoded URL；A throws Exception; B catches Exception and returns null on failure
- 修正建议: Incorporate data flow analysis to distinguish parameter vs constant URL；Add semantic aware features to differentiate reading first vs all lines；Use graph-based representations that capture control flow differences

### case_id=1082 FN partial_functionality

- 方法: `retrieveQ` vs `httpRequestByPOST`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Performs a GET request via URLConnection, reads response line by line with newline separators, prints response message to stderr, and returns the content.
- B 摘要: Performs a POST request via HttpClient with parameters, reads response if status code < 400, otherwise returns null and sets error fields, and returns the response body without newline separators.
- 静态失败原因: Low token overlap and different API usage (URLConnection vs HttpClient) and method signatures led the model to miss the higher-level functional similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB labels them as clones because both implement the core functionality of making an HTTP request and reading the response body, which is a typical broad Type-3/Type-4 clone in code clone benchmarks.
- 共享行为: Both fetch an HTTP response and read it line by line into a string buffer；Both return the response body as a string
- 行为差异: A uses GET (URLConnection) while B uses POST (HttpClient with params)；A throws exceptions on error, B catches and returns null；A inserts newlines between lines, B does not；A prints to stderr, B does not
- 修正建议: Use models that capture semantic intent, such as code2seq or AST-based models；Include data augmentation to recognize similarity across different HTTP libraries；Incorporate type information or dataflow analysis

### case_id=1083 FN partial_functionality

- 方法: `doVersionCheck` vs `register`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Checks for a new version by fetching and parsing a version file from a URL.
- B 摘要: Registers a user by encoding password, creating hash, calling a phpBB forum URL, persisting the user, and sending a confirmation email.
- 静态失败原因: Static BERT models rely on method names and overall semantics; the method names 'doVersionCheck' and 'register' are dissimilar, and the token Jaccard is low, causing the model to miss the shared I/O pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels as clones pairs that share significant code structure, such as the URL I/O pattern, even if the overall functionality differs, treating it as a Type-3 or Type-4 clone.
- 共享行为: Both open a URL connection and read input lines using BufferedReader；Both handle IOException in a try-catch block；Both perform some logging or user feedback
- 行为差异: A checks version/build strings; B processes user data and persists to database；B includes password encoding, hash creation, and email sending；B has additional error handling for NumberFormatException and MailException
- 修正建议: Train on data with more emphasis on structural or subgraph similarity；Use graph-based models that capture control flow and data flow；Incorporate data flow analysis to identify common I/O patterns

### case_id=1084 FP boilerplate_overlap

- 方法: `actionPerformed` vs `resolvePlugins`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Handles various UI command actions (e.g., setting GraphViz path, ImageMagick path, scale image, default country, date format, look-and-feel, etc.) by opening file choosers, updating preferences, and restarting UI.
- B 摘要: Resolves plugins by downloading a plugins.xml file from a remote URL if not already cached, then delegates to another resolvePlugins method.
- 静态失败原因: The model likely focused on common API mentions (File, IOUtils, try-catch) and ignored the vastly different control flows and contexts. The low Jaccard suggests the model may have used embedding artifacts that over-emphasized code patterns like file I/O boilerplate, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels as non-clone because the functions have entirely different purposes: one is a UI event handler with complex branching, the other is a utility to download a config file. They share no semantic equivalence.
- 共享行为: Both involve file operations (opening/reading files).；Both use try-catch blocks for exception handling.
- 行为差异: Function A is a lengthy event handler processing many distinct UI commands with different logic; Function B is a short method specifically for downloading and resolving plugin configuration.；Function A manipulates UI components (e.g., setting text fields, enabling buttons, updating UI); Function B does not interact with UI.；Function A stores preferences via a controller; Function B writes a file to cache and calls another method.
- 修正建议: Increase emphasis on control flow structure and function length differences.；Use graph-based representations (e.g., CFG, AST) to capture semantic intent rather than surface-level API usage.；Apply thresholding on token/embedding similarity to flag low overlap cases as non-clones.

### case_id=1085 FN partial_functionality

- 方法: `readReferenceText` vs `File2String`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.95`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a reference text from a bundle URL by identifier, reads lines with newlines, logs errors and throws NoContentException.
- B 摘要: Reads a file or classpath resource as a string, concatenates lines without newlines, prints errors and exits on failure.
- 静态失败原因: Low token overlap (0.23) and differences in API usage (URL vs File/ClassLoader) and error handling patterns cause static model to miss high-level semantic similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB considers reading a file to string a common functionality, labeling as clone despite structural differences in I/O and error handling.
- 共享行为: Both read text from a file/resource and return it as a string
- 行为差异: Newline handling: A appends newline after each line, B does not；Error handling: A logs and throws exception, B prints and exits；Resource loading: A uses bundle URL, B uses FileInputStream then classpath fallback
- 修正建议: Use data augmentation with varied I/O and error handling patterns；Incorporate control-flow and data-flow awareness (e.g., graph-based models)；Employ contrastive learning to map similar functionality despite surface differences

### case_id=1086 FN boilerplate_overlap

- 方法: `main` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a zip file from a URL and extracts its entries to files.
- B 摘要: Copies a file from one path to another, creating directories if needed.
- 静态失败原因: Static BERT models likely relied on token/API overlap (FileInputStream, FileOutputStream, while loop pattern) and missed the higher-level semantic difference (zip extraction vs file copy). The similar boilerplate and variable names misled the model.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may consider both as file I/O operations and possibly label as clone due to common byte-copy loop patterns and stream usage, but the overall functionality is too different for typical BCB Type-3/4 clone.
- 共享行为: Both use FileInputStream and FileOutputStream for I/O；Both contain while loops reading bytes and writing to output；Both handle exceptions (one throws, one catch-and-log)
- 行为差异: A reads from a URL (possibly HTTP) and processes ZIP archive; B reads from local file path；A extracts multiple files (zip entries); B copies a single file；A does not create directories; B creates parent directory if missing；A uses ZipInputStream and ZipEntry; B uses plain FileInputStream
- 修正建议: Incorporate data flow or control flow graphs to capture program semantics beyond lexical tokens；Use models that consider method names and comments for intent；Train with more examples distinguishing similar I/O patterns with different intents

### case_id=1087 FP boilerplate_overlap

- 方法: `writeFileType` vs `getUser`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads URIs from a file, fetches each URI's content via HTTP, checks for OWL/RDFS/RDF keywords in first 100 lines, and writes classification to an output file.
- B 摘要: Loads a user from a DAO by login, and if not found, reads a config file to parse user credentials and saves a new user.
- 静态失败原因: The static model likely over-relied on lexical overlaps such as 'BufferedReader', 'URL', 'Exception', 'printStackTrace', and common Java I/O patterns, which are boilerplate in many file-processing functions. The model failed to capture the distinct functional intents due to similar control flow structures and exception handling.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the functions serve entirely different purposes: one is a batch URI classification tool, the other is a user authentication helper. Despite sharing some I/O boilerplate, the core logic and outcomes are unrelated.
- 共享行为: Both read from a file using BufferedReader；Both use URL and URLConnection to open streams；Both involve parsing lines of text；Both handle exceptions with e.printStackTrace()
- 行为差异: Function A writes results to an output file, while B returns a User object；Function A processes multiple URIs in a loop, B processes only one userlogin；Function A checks for specific ontology keywords, B matches user credentials；Function A uses HTTP connections to external URLs, B reads a local config resource from classpath
- 修正建议: Improve training with more diverse non-clone pairs that share I/O boilerplate；Add attention to unique method-level semantics beyond common patterns；Incorporate dataflow analysis to distinguish different data transformations

### case_id=1088 FN partial_functionality

- 方法: `getFile` vs `decodeFileToFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, optionally modifies its endpoint address, and saves it to a temporary directory, returning the file path.
- B 摘要: Decodes a Base64-encoded input file and writes the decoded content to an output file, returning success status.
- 静态失败原因: Static BERT/GraphCodeBERT likely failed due to low token overlap (Jaccard=0.145) and superficial lexical differences like method names and specific API calls (URL vs Base64 stream), missing the abstract similarity in data flow and I/O handling.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this as a clone because both functions are file transfer utilities with similar structural patterns (open streams, transfer data, close streams), which could be considered Type-4 semantically similar clones in the BigCloneBench framework.
- 共享行为: Both functions open an input stream and an output stream to transfer data.；Both functions handle I/O exceptions and close streams in a finally block.；Both functions perform file I/O operations involving reading from a source and writing to a destination.
- 行为差异: Function A reads from a URL (HTTP) and writes to a file, including optional XML manipulation.；Function B reads from a file using Base64 decoding and writes the decoded bytes to another file.；Function A returns the file path, while Function B returns a boolean success flag.；Function A has additional logic for checking file existence and modifying XML content.
- 修正建议: Use data-flow-aware representations that capture abstract I/O patterns.；Incorporate byte-level or stream-level cloning heuristics.；Train on more diverse partial functionality pairings.

### case_id=1089 FN partial_functionality

- 方法: `copyLogic` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Copies a class file from source to destination using FileChannel, with state machine transitions.
- B 摘要: Launches a Maven-based Eclipse project by processing pom files and setting Hibernate configuration, including copying a reverse engineering file if needed.
- 静态失败原因: The static model relies on lexical and structural overlap; token Jaccard is extremely low (0.05) and APIs differ. It correctly predicted no clone from that perspective, but missed the broad type-4 partial similarity that BCB might accept.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled this as a clone due to partial functionality similarity (both involve file copying), but the overall functions are very different in purpose and structure.
- 共享行为: Both perform a file copy operation from a source to a destination.
- 行为差异: Copy method: FileChannel.transferTo vs IOUtils.copy from bundle resource.；Overall purpose: simple file copy vs complex launch configuration setup.；Context: copyLogic is part of a state machine; launch is an Eclipse extension.；Additional operations in launch: XML parsing, property setting, job scheduling.
- 修正建议: Enhance model with data flow analysis to detect I/O operations even when APIs differ.；Consider functional-level embeddings that capture high-level program semantics.

### case_id=1090 FN boilerplate_overlap

- 方法: `loadSourceCode` vs `readGeoParserResult`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Loads a source code file, reads it line by line, applies syntax highlighting, and returns HTML-wrapped code.
- B 摘要: Sends an XML request to a geoserver URL for parsing geographic data, reads the XML response, extracts place names and gazetteer IDs, with retry logic and exception handling.
- 静态失败原因: Static models like GraphCodeBERT may over-rely on lexico-syntactic structures such as 'BufferedReader', 'readLine()', 'while' loops, and try-catch blocks, which are present in both, leading to a false similarity judgment despite low token overlap.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may label this as a clone due to shared structural patterns (stream reading, line-by-line iteration, exception handling) despite vastly different domain purposes, reflecting broad Type-3/Type-4 criteria where partial functionality or similar control flow suffices.
- 共享行为: Both open an input stream (from file or URL)；Both use InputStreamReader and BufferedReader to read lines；Both loop over lines until null；Both have try-catch for exceptions
- 行为差异: Function A reads from a local file; function B makes a web service call；Function A produces HTML with syntax highlighting; function B parses XML and extracts structured data；Function B constructs XML request, encodes parameters, handles multiple XML elements and retries; function A does not；Function B uses DocumentHelper and XPath-like iteration; function A uses a CodeViewer for syntax highlighting
- 修正建议: Incorporate data flow and semantic understanding to distinguish reading from file vs. network；Use contrastive learning with negative samples that share API usage but have different goals；Enhance representation with high-level intent via code summarization or documentation embeddings

### case_id=1091 FN boilerplate_overlap

- 方法: `main` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Creates and verifies digital signatures on PDF documents using iText library.
- B 摘要: Builds an editable HTML site by transforming XML with XSLT, reading control files, and writing output pages.
- 静态失败原因: The low token Jaccard (0.0779) indicates minimal lexical overlap; the model likely focused on domain-specific tokens (PDF, signature, KeyStore vs. Transformer, XML, Page) and missed the structural similarity in I/O patterns.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may consider them clones due to similar code structure: both use FileInputStream, FileOutputStream, char/byte buffers, loops, and extensive exception handling, which could be seen as a Type-3 clone with significant syntactic similarity despite different domains.
- 共享行为: Both perform file I/O operations (reading input files and writing output files) within loops.
- 行为差异: Different purposes (PDF signing vs. site building)；Different libraries used (iText vs. XSLT/Transformer)；Different data processing logic (signatures vs. XML transformations)
- 修正建议: Use techniques that capture structural patterns like loops and I/O operations；Consider code structure graphs to identify control flow similarities；Acknowledge that BCB annotations may be noisy in cases of boilerplate overlap

### case_id=1092 FP partial_functionality

- 方法: `run` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.75`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads from a URL, parsing lines to extract version, URL, and additional information, then notifies listeners.
- B 摘要: Performs a Google image search by constructing a URL, reading and parsing the HTML response to extract image URLs, and updates the UI with an image.
- 静态失败原因: Static BERT/GraphCodeBERT may have been misled by overlapping I/O boilerplate (BufferedReader, URL, IOException) and structural similarity of try-catch loops, ignoring the significantly different data processing logic.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely labeled as not clone because the two methods have distinct overall functionalities despite sharing low-level I/O patterns; BCB focuses on semantic similarity of the whole function.
- 共享行为: Both open a URL connection and read lines using BufferedReader；Both use try-catch for IOException handling
- 行为差异: Function A parses lines in a specific order (version, url, rest) while B reads all lines into one string and splits for image URLs；Function A notifies listeners after execution; B updates UI components and sets button enabled；Function A sets error flags; B shows error dialogs
- 修正建议: Train model to emphasize the entire algorithm rather than common I/O patterns；Incorporate data flow analysis to track how read data is processed；Use contrastive learning with examples where I/O is similar but logic diverges

### case_id=1093 FP lexical_or_api_overlap

- 方法: `downLoadZippedFile` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Downloads a zipped file from a URL, saves to a temp file, unzips it to a destination directory, and returns the local URL.
- B 摘要: Handles actions from a settings dialog, updating various preferences like graphviz path, image magick, date format, look and feel, etc., using file choosers and UI components.
- 静态失败原因: The static model likely overestimated similarity due to common tokens like 'File', 'InputStream', 'null', leading to a false positive despite low Jaccard similarity.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clones when functions have completely different purposes and no shared functionality beyond trivial lexical elements.
- 行为差异: Function A performs network download and file decompression; Function B updates UI preferences.；Function A uses URLConnection and IOUtils; Function B uses JFileChooser and direct file path setting.；Function A has a single focused task; Function B handles multiple commands with complex conditional logic.
- 修正建议: Improve contextual understanding of API usage and overall program flow.；Incorporate control-flow and data-flow analysis to distinguish different file handling patterns.；Use larger context (entire method body) with attention to high-level purpose.

### case_id=1094 FP lexical_or_api_overlap

- 方法: `perform` vs `generate`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Struts action that processes a form to classify a concept by sending XML data to a remote service and handling the response.
- B 摘要: Utility method that computes the SHA-1 hash of a given string and returns its hex representation.
- 静态失败原因: The model likely focused on superficial features like common keywords (e.g., 'String', 'IOException', 'session') or structural patterns (e.g., method start with public) but ignored the vast semantic gap.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clones for functions with completely different purposes and minimal semantic overlap; these functions share no meaningful functionality.
- 行为差异: Function A handles HTTP requests, session management, and complex data processing; function B performs a simple cryptographic hash.；Function A has extensive control flow with error handling and external I/O; function B is a straightforward algorithm.；Function A interacts with multiple external systems (database, URL connection); function B has no dependencies beyond standard library.
- 修正建议: Improve model's ability to distinguish boilerplate from core logic.；Incorporate more structural or dataflow features to capture actual semantics.；Use contrastive learning or hard negative mining for non-clones with low lexical similarity.

### case_id=1095 FP boilerplate_overlap

- 方法: `getLinksFromURLFast` vs `startScript`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Extracts all hyperlinks and their texts from a given URL by reading the HTML content and using regular expressions, returning them as two vectors.
- B 摘要: Loads a script from a URL specified in an attribute and appends it line by line to a dialog's script buffer, handling I/O errors by exiting.
- 静态失败原因: The static BERT model may have been misled by the lexical overlap of URL opening, BufferedReader usage, and line-by-line reading, treating the I/O boilerplate as a strong signal of clone, while missing the critical semantic differences in the subsequent processing and output.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled this as non-clone because the high-level functionality is completely different (link extraction vs script loading), despite sharing a low-level I/O pattern. The clone benchmark typically requires more than just similar I/O boilerplate.
- 共享行为: Both open a URL, create a BufferedReader from its input stream, and read the content line by line.
- 行为差异: Purpose: A extracts links, B loads a script.；Output: A returns vectors, B modifies dialog.script.；Processing: A uses regex to parse HTML, B just concatenates lines.；Error handling: A throws Exception, B catches IOException and exits.
- 修正建议: Incorporate structural analysis of the function's main processing logic beyond common I/O.；Use dataflow analysis to differentiate between reading for extraction vs reading for concatenation.；Train to recognize that boilerplate I/O patterns are not sufficient for clone detection.

### case_id=1096 FP lexical_or_api_overlap

- 方法: `run` vs `SRWGuiClient`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Runnable that reads from a hardcoded URL and discards all input.
- B 摘要: Constructor for a Swing browser that reads from a provided URL, processes XML with optional stylesheet transformation, and displays the result in a GUI.
- 静态失败原因: Static BERT likely relied on overlapping API tokens (URL, BufferedReader, openStream, readLine) and syntactic patterns, missing the semantic gap between a trivial loop that does nothing and a complex processing pipeline.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would not consider these clones because despite similar API usage, the core functionality is completely different: one is a no-op, the other is a complex GUI constructor. The behavioral difference is significant, aligning with Type-4 semantic non-clones.
- 共享行为: Both open a URL stream and create a BufferedReader.；Both read lines in a while loop.
- 行为差异: Function A discards all read data; function B processes and displays it.；Function B includes extensive GUI setup and XML transformation; A has no GUI.；Function A is a simple run() method; B is a constructor with complex logic.；Function B has error handling and user interaction; A has empty catch blocks.
- 修正建议: Incorporate data-flow analysis to track whether read data is used or discarded.；Include structural features that capture control flow complexity and depth.；Use contrastive learning with hard negative examples that share API calls but differ in purpose.

### case_id=1097 FP lexical_or_api_overlap

- 方法: `executePost` vs `getFullScreenUrl`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Sends an HTTP POST request with parameters and returns the full response body.
- B 摘要: Sends an HTTP GET request to a YouTube URL, extracts video parameters from a specific line, and constructs a download URL.
- 静态失败原因: The model likely over-relied on lexical and API overlap (URL, URLConnection, BufferedReader, while loop, try-catch) and overlooked differences in method signatures, parameters, and the actual processing logic. Static models may not capture the data flow differences (sending vs receiving data) and domain-specific parsing.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled non-clone because the functions have different input/output signatures, different HTTP methods, and fundamentally different post-processing logic. Despite shared HTTP boilerplate, the core functionality (generic POST vs. specific YouTube GET with parsing) is distinct.
- 共享行为: Both open an HTTP connection (URL, URLConnection) and read the response via BufferedReader.；Both use try-catch blocks to handle exceptions and include a finally block for cleanup.；Both return a string (response or constructed URL) or null/empty on failure.
- 行为差异: executePost uses POST method with parameters in request body; getFullScreenUrl uses GET with no body.；executePost returns raw response; getFullScreenUrl parses response for specific content (fullscreenUrl) and builds a new URL.；getFullScreenUrl updates UI (progress bar) and class fields (ytTitle); executePost has no side effects beyond connection.；executePost takes parameters; getFullScreenUrl uses a class field (ytUrl) as input.
- 修正建议: Incorporate method-level features like parameters, return type, and method name semantics.；Use dataflow analysis to distinguish between writing to and reading from connections.；Improve model's ability to recognize domain-specific logic (e.g., parsing for a specific keyword like 'fullscreenUrl').；Train on more diverse examples of non-clones that share API usage but differ in behavior.

### case_id=1098 FP boilerplate_overlap

- 方法: `readData` vs `copy`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Reads comma-separated tokens from several string fields and populates various sets and maps, likely for a character encoding or input validation dictionary.
- B 摘要: Recursively copies a file or directory from source to destination using file I/O streams.
- 静态失败原因: The model may have been misled by superficial similarities such as both containing while loops, try-catch blocks, and string manipulation (e.g., read(), write()), despite the completely different intent. Low token Jaccard suggests the model relied on structural pattern matching rather than semantic understanding.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clone because the functions have fundamentally different purposes—one is data initialization, the other is file copying—with no shared functionality beyond trivial loops.
- 行为差异: Function A operates on string data in memory, parsing tokens; Function B performs file system operations.；Function A populates data structures (HashSets, HashMap) for later use; Function B creates directories and copies file contents.；Function A uses StringTokenizer and loops over pre-defined string fields; Function B uses FileInputStream/FileOutputStream and handles directory recursion.；Function A is static private with no parameters; Function B is static public with two File parameters.
- 修正建议: Increase training data variety for non-clone pairs with similar control flow but different functionality.；Incorporate task-specific embeddings or domain knowledge to distinguish between data parsing and file I/O.；Use a more robust model that captures long-range dependencies and high-level semantics, such as GraphCodeBERT with enhanced dataflow analysis.

### case_id=1099 FP boilerplate_overlap

- 方法: `md5String` vs `perform`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Computes MD5 hash of input string and returns hex string.
- B 摘要: Handles HTTP request in Struts action: validates session, processes form data, calls external XML service, and returns ActionForward.
- 静态失败原因: The static model likely over-relied on common boilerplate patterns: both functions have exception handling, loops, string concatenation, and similar variable names like 'status', 'buf', 'res'. The model may have missed the very different overall logic due to lack of understanding of framework-specific semantics.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically marks non-clones when functions have entirely different purpose and API usage, even if both involve loops and string building. This pair is clearly non-clone.
- 共享行为: Both use StringBuffer to build result；Both handle exceptions and return null or alternative status；Both involve string encoding/decoding (implicitly in B's URL encoding)
- 行为差异: A is a pure data transformation; B is a web framework controller with side effects；A returns a hex string; B returns an ActionForward；A uses MessageDigest; B uses many external classes (HttpSession, ReportingBean, URLConnection)；B involves I/O and network calls; A is local computation
- 修正建议: Improve model's ability to distinguish framework-level code vs utility functions；Incorporate more type/API usage information to capture functional differences；Add attention to method signatures and class context

### case_id=1100 FP boilerplate_overlap

- 方法: `readData` vs `copyTo`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Parses comma-separated strings to populate sets and maps, then reads a file to build additional mappings and hash tables.
- B 摘要: Recursively copies files or directories from source to destination using file channels.
- 静态失败原因: The model likely overgeneralized from superficial similarities such as common Java patterns (e.g., try-catch blocks, method signatures) or was biased by the presence of common keywords like 'static', 'void', and 'IOException'.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would not consider these clones because they are completely unrelated in functionality; the functions serve different high-level tasks.
- 共享行为: Both use try-catch for IOException handling
- 行为差异: Different purposes: data initialization vs file copying；Different data structures: sets/maps vs files/channels；Different control flow: loops for tokenization vs recursion for directory traversal
- 修正建议: Enhance training with diverse non-clone pairs that have overlapping boilerplate；Incorporate semantic flow analysis to distinguish different high-level tasks；Use cross-file or dependency context to understand functional roles

### case_id=1101 FN benchmark_preference_bias

- 方法: `doGet` vs `readAndRewrite`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Handles HTTP GET request to display a portal page with authentication, caching, and logging.
- B 摘要: Reads a DICOM image file and rewrites it to another file with pixel data processing.
- 静态失败原因: The static BERT model likely correctly predicted non-clone due to low lexical overlap and different AST structures; the error is due to BCB label being inconsistent with semantic similarity.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as a clone based on an overly broad interpretation of 'read and write' functionality, ignoring domain and API differences.
- 共享行为: Both perform input/output operations
- 行为差异: Different input/output paradigms: HTTP request/response vs. file I/O；Different domains: web portal vs. medical image processing；A includes authentication and caching logic; B does not；A uses logging; B uses console output
- 修正建议: Review BCB annotation guidelines to ensure clone labels require meaningful functional similarity；Add more stringent criteria for partial functionality clones

### case_id=1102 FP lexical_or_api_overlap

- 方法: `run` vs `executePost`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a resource file from the classpath and sets its content in a Swing text component.
- B 摘要: Sends an HTTP POST request with parameters and returns the response string.
- 静态失败原因: The model likely focused on common boilerplate patterns (URL, InputStream, BufferedReader, while loop, StringBuilder) and ignored the different contexts (classpath resource vs. HTTP POST), leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels as non-clone because the core functionality (reading a local resource vs. making an HTTP request) is fundamentally different, despite some superficial I/O similarities.
- 共享行为: Both open a URL connection and obtain an InputStream.；Both read the stream line by line using BufferedReader.；Both append lines to a StringBuilder/StringBuffer.；Both close resources in a try-catch block.
- 行为差异: A reads a local resource from classpath, B performs an HTTP POST request.；A updates a Swing UI component, B returns the response string.；A uses anonymous Runnable class, B is a standalone method.；A catches and ignores exceptions silently, B prints stack trace.
- 修正建议: Include control flow and data flow features that distinguish local resource access from HTTP requests.；Use more training examples that differentiate similar boilerplate with different semantics.；Incorporate higher-level API understanding (e.g., classloader vs. HttpURLConnection).

### case_id=1103 FP dataflow_blindspot

- 方法: `readData` vs `createOutputStream`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `dynamic_rejection_with_trace`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Reads string tokens from multiple fields to populate sets and maps for Tibetan transliteration data.
- B 摘要: Copies all entries from a zip input file to a zip output file except 'content.xml', and returns a BufferedWriter for further output.
- 静态失败原因: The model likely overfitted to structural patterns like multiple while loops and set additions, ignoring the vast semantic difference in I/O and data processing. Low token overlap (0.054) suggests the model failed to utilize similarity signals and made a random false positive.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 dataflow_trace_and_outputs。
- BCB 偏好解释: BigCloneBench labels non-clones for functionally unrelated methods. readData is a configuration loader, createOutputStream is a zip copy utility. No shared functionality or control flow.
- 行为差异: readData populates data structures from tokenized strings; createOutputStream performs file I/O with zip compression.；readData has no file output; createOutputStream returns a BufferedWriter.；readData handles multiple token streams and tracks lengths; createOutputStream copies byte buffers.；readData uses StringTokenizer; createOutputStream uses BufferedReader/InputStreamReader and ZipInputStream/ZipOutputStream.
- 修正建议: Improve training data diversity to reduce false positives on low-similarity pairs.；Enhance model's understanding of data flow and I/O operations.；Add negative downsampling for pairs with low token overlap.

### case_id=1104 FN partial_functionality

- 方法: `File2String` vs `run`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.75`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a file from local filesystem or classpath, concatenates lines into a string, prints diagnostics, and exits on error.
- B 摘要: Reads a URL and discards all lines, silently catching exceptions.
- 静态失败原因: Static BERT models typically rely on surface-level token overlap and syntactic structure. Here token Jaccard is low (0.212), and syntax differs significantly (A has multiple try-catch blocks, return statements, and exit calls; B is simple). The model missed the abstract functional similarity in I/O processing due to lack of dataflow awareness.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider this a Type-3 clone because both functions follow a common pattern of 'reading lines from an input stream using BufferedReader' despite differences in source (file vs URL), output (return vs void), and error handling. The annotators likely prioritized the structural similarity of the line-reading loop.
- 共享行为: Both open an input stream and create a BufferedReader；Both read lines in a while loop using readLine()；Both close the reader after reading
- 行为差异: A accumulates lines into a StringBuffer and returns the full string; B discards lines and returns void；A has complex error handling with System.exit; B catches exceptions silently without action；A supports fallback to classpath loading; B only uses a fixed HTTP URL；A prints diagnostic messages; B has no output
- 修正建议: Use dataflow analysis or abstract syntax trees to capture common I/O patterns；Incorporate a model that recognizes method-level functional equivalence, e.g., by summarizing the core behavior (e.g., 'read lines')；Enhance training data with more Type-3/4 clones that have low lexical overlap

### case_id=1105 FN lexical_or_api_overlap

- 方法: `main` vs `convert`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a URL and extracts its contents to files.
- B 摘要: Converts an ACRNEMA/DICOM file by parsing pixel data, adding UIDs, and writing a new DICOM file.
- 静态失败原因: Static BERT/GraphCodeBERT likely relied on token overlap and similar API usage (FileInputStream, FileOutputStream, BufferedInputStream, etc.) and control flow patterns, failing to capture the fundamentally different data processing semantics.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may consider them clones due to superficial similarities: both are file I/O routines with stream handling, loops, and try-finally blocks. However, the domain-specific operations in B are entirely different, so BCB's label appears erroneous.
- 共享行为: Both read from an input stream and write to an output stream.；Both use buffered I/O and handle file exceptions.；Both print status messages during processing.
- 行为差异: Function A downloads and unzips a KMZ file; function B processes medical image format.；Function A reads from a URL; function B reads from a local file.；Function B performs complex pixel data manipulation and metadata insertion; function A simply extracts zip entries.；Function B has conditional logic for DICOM-specific tags; function A does not.
- 修正建议: Incorporate dataflow analysis to distinguish between different manipulation operations.；Use models that better capture domain-specific operations and structure.；Include more diverse training examples that distinguish between generic I/O and specialized processing.

### case_id=1106 FN partial_functionality

- 方法: `fileDownload` vs `load`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a file from a given URL and writes it to a local file, with error logging.
- B 摘要: Reads XML content from a Pastebin URL and returns it as a string, with error dialog.
- 静态失败原因: Static models rely on lexical tokens and see different method names, output types, and low Jaccard similarity, missing the higher-level semantic similarity of URL reading.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often groups functions that perform URL reading/downloading tasks, even if the output method differs, considering them functionally similar.
- 共享行为: Open a URL connection；Read input using BufferedReader and InputStreamReader；Handle exceptions
- 行为差异: fileDownload writes to a file, load returns a string；fileDownload reads byte-wise, load reads line-wise；Error handling: logging vs dialog
- 修正建议: Use data flow analysis to capture common API usage patterns (URL, URLConnection, BufferedReader)；Increase sensitivity to similar IO patterns and exception handling；Incorporate graph-based representations to model control and data flow

### case_id=1107 FP boilerplate_overlap

- 方法: `readData` vs `copyFromTo`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Reads and parses configuration strings and a file to populate character sets and lookup tables for Tibetan transliteration.
- B 摘要: Copies a file from source to destination using FileChannel, handling exceptions and preserving timestamps.
- 静态失败原因: Static BERT models may overemphasize superficial similarities like common try-catch patterns, System.out.println, and file I/O keywords, missing the radical difference in core logic and domain-specific structures.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the two functions have completely different purposes: one is about data parsing and initialization, the other about file copying.
- 共享行为: Both perform file I/O operations；Both use try-catch blocks and print error messages
- 行为差异: Function A parses structured input into domain-specific data structures；Function B copies entire file content；Function A has complex column-parsing logic and error handling for invalid lines；Function B uses FileChannel.transferTo for efficient copying
- 修正建议: Incorporate AST or data-flow features to distinguish variable usage and data transformations；Use domain-aware tokenization to capture rare domain terms；Train on more diverse negative pairs to reduce false positives from shared boilerplate

### case_id=1108 FN partial_functionality

- 方法: `readGeoParserResult` vs `issueCommandToServer`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends an XML request to a geo-parsing service, retries on failure, and parses the response to extract place names and gazetteer IDs.
- B 摘要: Sends an HTTP POST command to a server with a ChangeCapsule object and returns the response as a string.
- 静态失败原因: Static BERT/GraphCodeBERT likely focused on the exact code semantics and found significant differences in data structures, error handling, and input/output types, missing the broad functional similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider these as Type-4 clones because both implement the high-level task of 'send a request to a server and process the response', even though the details differ.
- 共享行为: Both functions send an HTTP request to a remote server.；Both functions read the response line by line using BufferedReader.
- 行为差异: Function A constructs an XML payload and parses an XML response, while Function B uses URL-encoded form parameters and returns a plain string.；Function A has retry logic and a testing mode, Function B does not.；Function A returns a collection of tuples, Function B returns a single string.；Function A uses different HTTP methods (GET vs POST) and different content types.
- 修正建议: Incorporate coarser-grained program analysis to capture high-level intent.；Use graph-based features that model data flow and control flow at a higher level of abstraction.

### case_id=1109 FN partial_functionality

- 方法: `getResourceAsStream` vs `copy`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Retrieves a resource via URL, caches it locally, and returns an InputStream, with HTTP conditional checks.
- B 摘要: Copies a file from source to destination using FileChannel, with parent directory creation.
- 静态失败原因: Low token overlap and different method names/APIs (e.g., BufferedStream vs FileChannel) caused the model to miss the shared file-copy sub-functionality.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considers FileChannel transfer and BufferedInputStream/BufferedOutputStream copying as functionally similar file copy operations, despite different contexts.
- 共享行为: Both perform file copying from a source to a destination；Both use input and output streams/channels；Both handle exceptions and close resources
- 行为差异: A includes HTTP connection handling and caching logic；B is a straightforward file copy using FileChannel；A returns an InputStream or null; B is void；A prints debug messages; B does not
- 修正建议: Train on paired examples with partial functional overlap；Incorporate data-flow or AST-based features to detect read-write patterns；Use contrastive learning with functional similarity labels

### case_id=1110 FN partial_functionality

- 方法: `decodeFileToFile` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Decodes a Base64 encoded input file and writes the decoded content to an output file.
- B 摘要: Launches a NexOpen project configuration by processing Maven POM files and Hibernate settings.
- 静态失败原因: Static BERT models rely heavily on lexical and structural similarity; the low token Jaccard (0.0667) and vastly different structures caused it to miss the subtle shared subtask, leading to a false negative.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider these clones under Type-4 partial functionality because both methods contain a common sub-pattern of copying data from an InputStream to an OutputStream, even though their overall purposes differ.
- 共享行为: Both methods involve reading from an input stream and writing to an output stream.；Both use try-catch-finally blocks for resource management and exception handling.
- 行为差异: Function A performs Base64 decoding; Function B handles project configuration and launch logic.；Function B interacts with Eclipse workspace, Maven POM files, and Hibernate dialect, while Function A is standalone file I/O.；Function B includes complex conditional logic and multiple file operations, whereas Function A is a simple copy loop.
- 修正建议: Enhance models to detect common sub-patterns (e.g., copy loop) even when overall context differs.；Incorporate dataflow analysis to identify isomorphic I/O patterns.；Use contrastive learning with annotated partial functionality pairs.

### case_id=1111 FN benchmark_preference_bias

- 方法: `trainClassifier` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Trains a classifier by executing an external command and capturing its output streams.
- B 摘要: Retrieves a resource as an InputStream with caching, HTTP conditional GET, and fallback to local cache.
- 静态失败原因: The low token Jaccard (0.086) and lack of structural or semantic overlap likely caused the model to predict non-clone correctly, but BCB label considered them clones possibly due to a broad interpretation of Type-4 or annotation error.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have considered both as involving file I/O and stream handling, but the overall functionality is entirely different.
- 共享行为: Both use I/O streams (InputStream/OutputStream) and System.out.println for logging or output.
- 行为差异: A executes an external process; B performs HTTP requests and file caching.；A writes to System.out and System.err; B primarily writes to cache files and returns streams.；A is a simple synchronous command execution; B involves complex caching logic with URL connections.
- 修正建议: Re-annotate the pair as non-clone to correct BCB label.；Improve model robustness by focusing on precise behavioral matching rather than broad API usage.

### case_id=1112 FN benchmark_preference_bias

- 方法: `doGet` vs `compress`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Handles HTTP GET request for a page, checking visibility, logging, caching, and writing response.
- B 摘要: Concatenates a list of files into one output file and optionally compresses it using an external tool.
- 静态失败原因: Static BERT likely used low token overlap and clear semantic mismatch to correctly predict non-clone, but BCB label is erroneous.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled these as Type-4 clone based on very broad 'file output' functionality, which is not typical for BigCloneBench.
- 共享行为: Both involve writing output to a stream (response or file)；Both use logging (PrintWriter or myLogger)
- 行为差异: A is a web servlet method; B is a file compression utility；A deals with HTTP request/response, user permissions, and session; B deals with file I/O and external process；A conditionally caches output to a temp file; B always writes to a specified file and may invoke YUI compressor
- 修正建议: Verify BCB annotation for this pair; likely a labeling error.；Use more precise functional clustering to avoid overly broad clone categories.

### case_id=1113 FN lexical_or_api_overlap

- 方法: `testNetworkHTTP` vs `loadMFileViaWeb`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Performs multiple HTTP GET requests to various URLs and discards responses, used for testing.
- B 摘要: Loads a .m file from a URL, reads its content, and parses it into a UserFunction object.
- 静态失败原因: The model likely overemphasized syntactic differences (different method signatures, control flow, and variable names) and the low token overlap, missing the common underlying I/O pattern shared by both functions.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB often classifies pairs as clones if they share similar API usage patterns, such as URL opening and line-by-line reading, regardless of higher-level purpose.
- 共享行为: Both open a URL connection；Both read data using BufferedReader.readLine()；Both catch exceptions from I/O operations
- 行为差异: Function A sends multiple HTTP requests to different URLs; Function B only reads from one URL.；Function A discards all received data; Function B concatenates lines and parses the result.；Function A has no return value; Function B returns a UserFunction.；Function A is a test method; Function B is a utility method for loading files.
- 修正建议: Incorporate API call sequence similarity as a feature；Use contrastive learning to focus on shared structural subgraphs；Increase weight on common library usage patterns

### case_id=1114 FP boilerplate_overlap

- 方法: `doVersionCheck` vs `getFrameworkFactory`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Checks for a newer version of jEdit by reading a version file from a URL and comparing build numbers.
- B 摘要: Loads an OSGi FrameworkFactory by reading a service configuration file from the classpath and instantiating the specified class.
- 静态失败原因: Static BERT may over-rely on token-level overlap like URL, BufferedReader, readLine, and control flow, ignoring semantic differences in data processing and final output.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels as non-clone because functions have distinct purposes and outputs; shared I/O patterns are superficial.
- 共享行为: both open a URL/resource and read lines with BufferedReader
- 行为差异: different purposes: version check vs framework loading；different input sources: dynamic URL vs fixed classpath resource；different outputs: UI messages vs return instance or throw exception；error handling: IOException caught vs Exception thrown
- 修正建议: train on more diverse pairs with similar boilerplate but different semantics；incorporate data flow analysis to distinguish reading from processing；use contrastive learning to emphasize output differences

### case_id=1115 FP boilerplate_overlap

- 方法: `perform` vs `getMD5Hash`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: A Struts action handler that processes form data, builds XML, sends an HTTP POST, parses the response, and updates session attributes.
- B 摘要: A utility that computes the MD5 hash of a string and returns it as a hexadecimal string.
- 静态失败原因: The model likely overgeneralized from surface-level similarities (e.g., both use StringBuffer and exceptions) and failed to capture the drastically different semantics and control flow. The long and complex nature of Function A may have caused the model to focus on local patterns rather than overall function.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels these as non-clones because they perform fundamentally different tasks and have no functional overlap.
- 共享行为: Both use StringBuffer to build strings.；Both have try-catch blocks for exception handling.；Both return a string value.
- 行为差异: Function A is a web action handler with session management and HTTP requests; Function B is a simple hashing method.；Function A deals with XML parsing and URL connections; Function B performs cryptographic hashing.；Function A has a complex control flow with multiple conditional branches; Function B has a straightforward sequential flow.；Function A interacts with external resources (URL, session); Function B has no side effects.
- 修正建议: Increase training data with diverse long-range dependencies.；Incorporate dataflow or control flow graph features to distinguish side-effect-heavy code from pure functions.；Use contrastive learning to better separate non-clones with shared boilerplate.

### case_id=1116 FN benchmark_preference_bias

- 方法: `doExecute` vs `modifyApplicationMessage`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Processes multipart form data to send an email with attachments and handles errors.
- B 摘要: Reads a locale-specific properties file and modifies or adds a message key-value pair.
- 静态失败原因: Static model correctly predicted non-clone due to very low token overlap (0.0837) and different APIs, but BCB label (1) suggests BCB considered them clones under some loose criteria.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled as clone based on a broad Type-4 interpretation of both functions performing 'data processing with I/O', but the functional purposes are entirely different.
- 共享行为: Both use try-catch for exception handling；Both involve file I/O operations；Both perform string manipulation
- 行为差异: Domain: email sending vs properties file editing；Libraries: Struts, Mail, FileUpload vs Properties, FileReader；Outcome: sends email vs modifies configuration file
- 修正建议: Re-evaluate BCB annotation guidelines to avoid overly broad Type-4 labeling；Improve automated labeling consistency

### case_id=1117 FN partial_functionality

- 方法: `login` vs `sendRequestObjectResponse`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Logs into LOLA by sending email and password via HTTP POST and returns session ID.
- B 摘要: Sends an XML request to a servlet via HTTP POST with GZIP compression and saves response to a file based on content type, returning the file path.
- 静态失败原因: Static BERT models rely on token and structural overlap; the low Jaccard similarity (0.15) and different method signatures, API calls (e.g., GZIP, file handling), and control flow obscure the shared HTTP request pattern, leading to a false negative.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB annotates these as clones because both follow the same pattern of establishing an HTTP POST connection, sending data, and processing the response, which qualifies as a Type-3 clone (similar structure with modifications).
- 共享行为: Both open an HTTP URL connection with doOutput set to true；Both write data to the connection's output stream；Both read the response from the input stream；Both handle exceptions with error messages
- 行为差异: A sends login credentials (email, password) as form data; B sends XML data with GZIP compression；A returns a session ID string; B saves the response to a file and returns the file path；A uses simple BufferedReader for reading; B uses streams and writes to a file with content-type logic；B includes additional setup for server URL via preferences and dialog
- 修正建议: Use dataflow analysis to capture the common pattern of URLConnection usage；Abstract the HTTP request/response handling into a higher-level representation；Incorporate program dependence graphs to identify similar control/data flow regardless of surface form

### case_id=1118 FP other

- 方法: `testLoadSource` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.99`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Tests loading an arXiv article source and verifies its content.
- B 摘要: Handles GUI action events to set application preferences like paths for external tools.
- 静态失败原因: The model likely failed due to a spurious correlation or error; token overlap is extremely low (0.0239), and there is no obvious lexical or syntactic similarity. The false positive may stem from the model's inability to correctly distinguish unrelated functions in a long-tail distribution or a bug in the prediction pipeline.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB requires functional similarity or common intent, which is absent; these functions are completely unrelated in purpose and behavior.
- 行为差异: Function A performs a unit test on data access; Function B handles user interface events.；Function A reads a remote resource and asserts content; Function B updates GUI components and preferences.；Function A has a single clear purpose; Function B contains a long chain of conditional branches for various commands.
- 修正建议: Improve model's ability to capture high-level semantic intent, possibly via contrastive learning or better representation of program structure.；Use data augmentation to reduce false positives from unrelated pairs with low token overlap.

### case_id=1119 FN partial_functionality

- 方法: `createTempFile` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Creates a temporary file and copies a classpath resource into it.
- B 摘要: Launches a NexOpen project by setting up Maven profiles, handling Hibernate configuration, and copying a reverse engineering file from bundle to project.
- 静态失败原因: Static models like GraphCodeBERT rely on token sequences and AST structures; the low Jaccard similarity (0.065) and vastly different method sizes/structures likely led to a low similarity score. The model may not capture the partial functional overlap (stream copying) as significant, especially since it is a small part of Function B. Additionally, the long length of Function B may have caused truncation, losing context.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely annotated this as a Type-4 clone because both methods share the core functionality of copying an InputStream to an OutputStream, albeit for different purposes. The BCB annotation guidelines consider functional similarity at a high level, even if the methods differ significantly in context and complexity.
- 共享行为: Both involve copying data from an input stream to an output stream using IOUtils.copy or similar.；Both handle I/O exceptions appropriately.
- 行为差异: Function A is a simple utility focused solely on copying a resource to a temp file, while Function B is a complex Eclipse launch handler with many additional steps like project validation, profile management, property setting, and job scheduling.；Function B uses a much wider range of APIs (Eclipse, Maven, Hibernate) and includes complex control flow like conditionals, try-finally blocks, and anonymous inner classes.；The overall purpose and context are completely different: one is for testing temporary file creation, the other for launching a specific IDE project type.
- 修正建议: Improve detection of partial functionality by using dataflow analysis to identify common I/O patterns.；Use contrastive learning to emphasize shared substructures across methods.；Consider chunking long methods to avoid truncation and preserve semantics.

### case_id=1120 FP lexical_or_api_overlap

- 方法: `get` vs `getNetworkServersIPs`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Retrieves GameRecord objects from a URL by sending GET request with location and count headers, parsing lines not starting with '#'.
- B 摘要: Retrieves server IP addresses from a remote resource by reading lines and extracting portions after a trigger line.
- 静态失败原因: The model likely overemphasized the syntactic overlap of URL opening and BufferedReader usage, ignoring the semantic differences in parsing and data handling.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely considered these as non-clones due to different I/O behavior and parsing semantics, despite similar boilerplate of opening URL and reading lines.
- 共享行为: Open URL connection；Read lines from input stream；Parse lines based on conditions；Return results from parsed data
- 行为差异: Different input parameters (lat, lon, count vs netaddress only)；Different output types (GameRecord[] vs Vector<String>)；Different parsing logic (ignore '#' vs toggle flag and parse with ':')；Different error handling (returns null on failure vs returns partial result)
- 修正建议: Train model to better distinguish between boilerplate code and actual algorithmic similarity；Incorporate data flow analysis to capture divergence in variable usage and control flow

### case_id=1121 FP lexical_or_api_overlap

- 方法: `actionPerformed` vs `copy`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Handles various UI action events for setting preferences (e.g., GRAPHVIZ, IMAGEMAGICK, date format, look and feel) by opening file choosers, storing settings, and updating UI components.
- B 摘要: Copies a file from source to destination using a fixed-size buffer, throwing an IOException if the source does not exist.
- 静态失败原因: The static BERT/GraphCodeBERT model likely overfitted to surface-level API usage (e.g., File, FileInputStream, IOException) or was confused by the large size of Function A, focusing on a small snippet that resembles file handling.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB annotations prioritize functional equivalence; these functions have completely different high-level purposes and are not semantically equivalent, so they are correctly labeled as non-clones.
- 共享行为: Both involve file system operations (reading/writing files)
- 行为差异: Function A is a large, complex event handler managing multiple UI settings; Function B is a simple utility function for file copying.；Function A contains conditional branches for different commands and extensive preference saving; Function B is linear and performs only file I/O.；The overall purpose and context of the two functions are entirely different (UI configuration vs file copy).
- 修正建议: Incorporate features to capture overall method purpose (e.g., method name, class context, length).；Use dataflow analysis or a larger context window to distinguish between UI event handlers and utility functions.；Improve training data to include more diverse non-clone pairs with low token overlap but high-level semantic differences.

### case_id=1122 FP long_range_semantics

- 方法: `actionPerformed` vs `copyFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `static_summary_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Handles UI events for configuring settings like GRAPHVIZ path, IMAGEMAGICK path, and other preferences.
- B 摘要: Recursively copies files or directories from source to destination.
- 静态失败原因: The model likely relied on superficial token overlap (e.g., 'File', 'if', 'return') and missed the overall semantic structure due to the extreme length of function A, causing it to incorrectly predict a clone.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB would not label these as clones because they perform completely different tasks: one is a UI event handler for settings, the other is a file copy utility. No functional overlap even under broad type-3/4.
- 共享行为: Both use java.io.File objects
- 行为差异: A deals with UI event handling and preference storage; B performs file I/O with streams.；A is very long and includes many conditional branches for different settings; B is a concise utility function.；A does not copy files; B does not handle UI.
- 修正建议: Improve handling of long functions by truncation or hierarchical representations.；Incorporate structural awareness to differentiate UI event handling from file I/O utilities.

### case_id=1123 FN benchmark_preference_bias

- 方法: `getResourceAsStream` vs `run`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Caches and retrieves a remote resource via URL, returning an InputStream.
- B 摘要: Reads message files, applies pseudolocalization pipeline, and writes transformed output.
- 静态失败原因: Static BERT models rely on token overlap and structural patterns; these functions have very low token Jaccard (0.14) and distinct APIs (URL vs. pseudolocalization), leading to a non-clone prediction.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might consider both as 'resource processing' functions (read, process, write) at a high abstraction level, or this could be an annotation error due to vague similarity guidelines for Type-4 clones.
- 共享行为: Both perform file-like I/O operations using InputStream/OutputStream.；Both handle exceptions and use System.out for logging.；Both create or open files and write data.
- 行为差异: A deals with remote resources (URL, HTTP), B deals with local files.；A implements caching and conditional retrieval; B applies a pseudolocalization pipeline.；A returns an InputStream; B is void and writes to files or stdout.；A copies bytes; B processes structured messages.
- 修正建议: Improve training data to reduce mislabelings in BCB for broad Type-4 clones.；Use dataflow analysis to capture high-level I/O patterns (read, transform, write).；Incorporate abstract syntax tree (AST) or program dependency graphs (PDG) to detect structural similarities beyond token overlap.

### case_id=1124 FP lexical_or_api_overlap

- 方法: `handleHandshake` vs `getWebByUrl`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Handles Minecraft handshake by validating username and authenticating via HTTP session server.
- B 摘要: Downloads web page content from a URL, saves to file, and recursively extracts links.
- 静态失败原因: Static BERT models may overweigh lexical and API overlaps (URL, BufferedReader, InputStream, try-catch) while missing the different dataflow and final usage of the read data.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels non-clone because the functions have distinct high-level purposes (authentication vs. generic web scraping) despite sharing low-level I/O patterns.
- 共享行为: Both open a URL connection and read from an input stream using BufferedReader；Both handle exceptions with try-catch
- 行为差异: A validates a specific response ('ok') from the server; B writes all content to a file；A constructs a URL from handshake parameters; B takes any arbitrary URL；A sends network packets for login/shutdown; B does not；B recursively processes extracted URLs; A does not
- 修正建议: Incorporate method names and broader context into the model；Use dataflow analysis to distinguish how the URL content is processed；Add training examples that differentiate authentication logic from generic I/O

### case_id=1125 FN partial_functionality

- 方法: `copyResource` vs `handle`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource from a URL or file to a destination file using byte-by-byte I/O.
- B 摘要: Performs log file rotation: compresses or moves the log file, deletes old logs, and archives them based on date.
- 静态失败原因: Static BERT/GraphCodeBERT models rely heavily on token overlap and structural similarity. The token Jaccard is only 0.127, the method names differ, and Function B is much longer with many unrelated tokens. The model likely missed the shared I/O pattern due to low lexical similarity and the overwhelming presence of log-specific code in Function B.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BigCloneBench may consider these clones because both contain a core file copy loop (read-write bytes) and the overall task involves file I/O. The partial functionality similarity (copying data) might be considered enough for a Type-3 or Type-4 clone annotation, even though Function B does much more.
- 共享行为: Both read bytes from an input source and write them to an output file using a loop.
- 行为差异: Function A is a generic resource copy; Function B is a specialized log rotation handler with compression, archiving, and deletion.；Function B has many additional operations (file renaming, directory creation, archive creation, conditional logic based on configuration).；Function A's source can be a URL; Function B's source is always a local file.；Function B writes to a compressed (GZIP) or renamed file; Function A writes directly to a destination file.
- 修正建议: Use dataflow analysis to detect the core read-write loop pattern.；Incorporate task-specific filtering to isolate common I/O operations.；Train with more representative negative samples that have low token overlap but similar semantics.；Use graph-based representations (e.g., AST-based) to capture structural commonality.

### case_id=1126 FP long_range_semantics

- 方法: `getButtonSonido` vs `main`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `static_summary_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Creates a JButton with a file chooser dialog that copies a selected sound file.
- B 摘要: Main method for an adapter generator that reads a Prolog file, parses it, and generates Java adapter classes.
- 静态失败原因: Static BERT models may focus on local syntactic patterns (e.g., try-catch, file I/O) shared across many Java methods, missing the long-range semantic context that distinguishes these two very different programs.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB would classify as non-clone due to entirely different functionality and no semantic overlap.
- 行为差异: Completely different overall purposes: UI component setup vs. command-line code generation；Different control flow: event-driven vs. sequential argument parsing；Different I/O operations: file copy vs. parsing and class writing
- 修正建议: Incorporate data flow or control flow graphs into the model；Train on distinguishing overall method purpose rather than local token patterns；Use contrastive learning to separate methods with different high-level goals

### case_id=1127 FP lexical_or_api_overlap

- 方法: `addDataFromURL` vs `getVersion`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads from a given URL and appends each line to a member variable thetext, handling exceptions by printing and appending the URL string.
- B 摘要: Fetches a version string from a hardcoded URL by reading the first line and returning it, returning null on exception.
- 静态失败原因: The static model likely over-relied on high token-level overlap (URL, openConnection, BufferedReader, InputStreamReader, while, try-catch) and the similar control flow, ignoring the different return types, side effects, and method signatures. This suggests a weakness in capturing functional semantics beyond API usage.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically annotates clones only when functions exhibit the same core functionality. Here, one function is designed to accumulate content from a URL into a buffer, while the other retrieves a single version string. The semantic purpose is distinct, so BCB correctly labels them as non-clones despite shared API usage.
- 共享行为: Both open a URL connection and read lines from it using BufferedReader and InputStreamReader.；Both use a while loop to read lines.；Both have try-catch blocks to handle exceptions during I/O.
- 行为差异: Function A takes a URL parameter; function B uses a hardcoded URL.；Function A appends all lines to a buffer and returns void; function B returns the first line as a String.；Function A has a side effect on thetext; function B has no side effects.；Exception handling differs: A prints exception and appends URL; B returns null.
- 修正建议: Incorporate data flow analysis to distinguish between void methods that modify state and methods that return values.；Use type information (return type, signatures) as additional features.；Train on contrastive pairs that emphasize functional purpose over structural similarity.

### case_id=1128 FN benchmark_preference_bias

- 方法: `main` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a ZIP file from a URL and extracts its entries to files using stream-based processing.
- B 摘要: Copies a file to a destination using NIO FileChannel transferTo.
- 静态失败原因: Static BERT likely correctly predicted non-clone due to low token overlap and distinct control flows; the BCB label is likely a false positive in the benchmark.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might have labeled these as clones based on a broad interpretation of 'copying data from input to output' or possible annotation error due to both involving file streams and buffers.
- 共享行为: Both involve reading from an input source and writing to an output destination.；Both use file I/O operations (InputStream/OutputStream or FileChannel).
- 行为差异: A handles HTTP connection and ZIP extraction; B is a simple file copy.；A extracts multiple entries; B copies a single file.；A uses traditional streams; B uses NIO channels.；A has no file overwrite handling; B uses FileOutputStream which overwrites.
- 修正建议: Re-evaluate BCB annotation for this pair to verify if it truly represents clone functionality.；If considered clone, define clearer criteria for partial functionality similarity to avoid over-generalization.

### case_id=1129 FP lexical_or_api_overlap

- 方法: `copyFile` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Copies a file from source to destination using buffered I/O streams.
- B 摘要: Handles action events from UI components, managing file chooser dialogs and configuration preferences for various tools.
- 静态失败原因: Static BERT/GraphCodeBERT models may have false-positively predicted clone due to superficial API overlap (e.g., 'File', 'InputStream', 'FileOutputStream' in A vs. 'JFileChooser', 'File' in B). The model likely captured common file-related tokens but ignored the vast difference in control flow, UI interaction, and overall semantics.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels this as non-clone because the functions have completely different purposes (file copy vs. UI event handling) and minimal lexical overlap (token Jaccard 0.063). The broad similarity in BCB Type-3/Type-4 would require partial functional similarity, which is absent here.
- 共享行为: Both involve file paths and I/O (A: file copy, B: file selection via JFileChooser)
- 行为差异: A is a simple utility for file copying without UI interaction; B is a complex UI event handler with branching logic and preference storage.；A performs deterministic I/O with FileInputStream/FileOutputStream; B involves JFileChooser dialogs, UI updates, and preference persistence via Suku.kontroller.；A has no conditional logic apart from the loop; B contains many if-else branches and checks for null/empty strings.
- 修正建议: Incorporate structural features like method length, nesting depth, and number of statements to distinguish utility functions from complex event handlers.；Use fine-grained API categorization (e.g., UI vs. I/O) to prevent overreliance on common tokens.；Employ contrastive learning with negative pairs that have high token overlap but different semantics.

### case_id=1130 FN partial_functionality

- 方法: `runScript` vs `sendRequest`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a script file from the applet's codebase and returns its content as a string.
- B 摘要: Sends an HTTP request with XML payload to a remote servlet, receives compressed XML response, parses it, and returns an empty string.
- 静态失败原因: A static BERT model likely focused on low token overlap and API-level differences (e.g., use of GZIP, JDOM) while missing the higher-level functional similarity in network I/O patterns, leading to a false negative.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider these Type-4 clones because both perform network I/O to retrieve data (one loads a script, one sends a request and gets a response) and are part of an applet's communication layer, despite differences in protocol and data handling.
- 共享行为: Both open a URL and read data from an input stream.；Both handle exceptions with error messages.
- 行为差异: Function A reads a local script file, while B sends a request to a remote servlet.；A uses simple byte-by-byte reading, B uses compressed streams and XML parsing.；A returns file content, B returns empty string after parsing response.；B involves preference retrieval and UI dialogs, A does not.
- 修正建议: Incorporate higher-level functionality representations, e.g., via API call sequences or data flow analysis.；Use graph-based models that capture control and data dependencies beyond tokens.；Consider applet context or method-level comments to infer domain similarity.

### case_id=1131 FN benchmark_preference_bias

- 方法: `doGet` vs `readAndRewrite`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Handles HTTP GET request to display a portal page with authentication, logging, and caching.
- B 摘要: Reads a DICOM image file and rewrites it to another file.
- 静态失败原因: Static BERT model likely correctly identified them as non-clones due to very low token overlap (0.039) and distinct API usage (servlet vs DICOM). The model did not fail; the BCB label appears to be a false positive.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as clone due to both functions involving reading input and writing output, albeit in completely different domains and implementations. This likely reflects a broad Type-4 semantic similarity bias in BCB annotations.
- 行为差异: Function A is a servlet handler; B is a static file conversion method.；A deals with HTTP requests/responses; B deals with DICOM image I/O.；A involves user permissions, logging, and caching; B does pure data transformation.；A writes HTML output; B writes binary image data.
- 修正建议: Re-examine BCB annotation for this pair; likely should be non-clone.；If keeping as clone, require at least some shared functionality or domain.；Use dataflow analysis to confirm no functional overlap.；Train with contrastive learning to reduce sensitivity to superficial I/O patterns.

### case_id=1132 FN benchmark_preference_bias

- 方法: `moveFile` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.75`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Moves a file by reading its bytes into a buffer and writing to a target file, then deletes the original.
- B 摘要: Builds a website for editing by reading XML files, performing XSLT transformations, and writing generated pages to disk.
- 静态失败原因: Static BERT models rely heavily on token overlap and structural similarity; the low Jaccard similarity (0.05) and vastly different token sets caused it to predict non-clone. The model failed to recognize the broad file I/O pattern that BCB annotators might consider as clone.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: None
- 共享行为: Both read from a file using an input stream and write to a file using an output stream.；Both use a buffer array (byte or char) to read data in chunks.；Both involve file I/O operations.
- 行为差异: moveFile operates on a single file; buildSiteForEdit processes multiple files and directories.；moveFile performs a simple byte copy; buildSiteForEdit involves XML parsing, XSLT transformation, and string manipulation.；moveFile deletes the source file after copying; buildSiteForEdit does not delete source files.；moveFile has no error handling beyond throwing IOException; buildSiteForEdit has extensive error handling and logging.
- 修正建议: Include more examples of broad functional similarities in training data.；Use contrastive learning to differentiate between incidental I/O overlap and true functional equivalence.；Incorporate data flow or behavioral embeddings to capture high-level operations like file copying.

### case_id=1133 FN partial_functionality

- 方法: `copyResource` vs `extractUninstallFiles`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource from a URL or file to a destination file by reading byte by byte and writing to an output stream.
- B 摘要: Extracts uninstall files handling upgrades, directory management, copying old classes, processing jar entries, and writing properties.
- 静态失败原因: Static BERT models rely on lexical and structural overlap; the low token Jaccard similarity (0.118) and differing context led to a non-clone prediction, failing to capture the perceived low-level similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled it as clone due to shared low-level I/O patterns (byte copying loop) despite different high-level purposes, reflecting broad Type-4 similarity acceptance.
- 共享行为: Both perform file I/O operations；Both read input streams and write output；Both include byte-by-byte copy loops
- 行为差异: Function A is a simple single-file copy; B performs complex extraction with directory creation, deletion, and conditional logic；B handles upgrades, backups, and jar manipulation; A does not；B writes to multiple files and includes property file handling; A writes to one file only
- 修正建议: Improve capture of high-level intent through graph or dataflow analysis；Incorporate broader context understanding to differentiate specific versus general file copy operations

### case_id=1134 FP lexical_or_api_overlap

- 方法: `main` vs `copyFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Main method that parses a Prolog file, generates adapter classes, and writes them to a JAR file.
- B 摘要: Utility method that copies a file from source to destination using FileChannel.
- 静态失败原因: Static BERT/GraphCodeBERT may have been misled by the presence of file-related keywords and method calls common in I/O operations, or by the token overlap (though Jaccard is low). Possibly the model overgeneralized based on the fact that both methods contain 'File' and 'IOException' etc.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled this as non-clone because the two functions have entirely different purposes and implementations. Even though both involve file I/O, the core functionality is completely different.
- 共享行为: Both involve file I/O operations
- 行为差异: Code A performs complex parsing and code generation, while Code B simply copies a file.；Code A is a main method with argument handling; Code B is a private helper.；Code A has many steps and error handling; Code B is straightforward.
- 修正建议: Improve training data to include more negative pairs with similar APIs but different purposes.；Use dataflow or structure-aware models that capture the global logic.

### case_id=1135 FP boilerplate_overlap

- 方法: `getHashedPassword` vs `perform`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.98`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Returns MD5 hash of a password as uppercase hex string.
- B 摘要: Processes a web form action, handling session, XML building, HTTP request, and classification result.
- 静态失败原因: Likely due to lexical overlap of common Java keywords (String, null, Exception) and boilerplate patterns (try-catch, return) that misled the shallow model.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB annotates based on functional similarity; these functions have no common purpose, hence non-clone.
- 行为差异: One hashes a string; the other handles a multi-step web request.；One returns a formatted hex string; the other returns an ActionForward.；One is a utility method; the other is a controller action.；One has simple error handling; the other has complex session and business logic.
- 修正建议: Improve model sensitivity to overall structure and length differences.；Use AST or data-flow features to capture true semantic content.；Apply clone-specific fine-tuning with contrastive learning.

### case_id=1136 FN partial_functionality

- 方法: `createOutputStream` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Creates a BufferedWriter for output by copying all entries from an input ZIP to an output ZIP except content.xml, then opens a new content.xml entry with UTF-8 encoding and returns the writer.
- B 摘要: Builds a site for editing by transforming XML pages with XSLT, replacing strings, and writing the results to output files.
- 静态失败原因: Static BERT models rely on lexical and structural patterns; the shared API tokens (FileInputStream, BufferedWriter, etc.) and I/O boilerplate dominate, obscuring the distinct high-level semantics. The long and complex code in B also challenges the model's ability to capture overall purpose.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider them clones based on broad functional similarity in file manipulation patterns (read, transform, write) despite different domains (ZIP vs. XML site generation). The low token overlap suggests Type-4 semantic clone annotation.
- 共享行为: Both perform file I/O operations with buffered streams；Both use character arrays for reading data；Both write content to output files
- 行为差异: A operates on ZIP archives and returns a writer; B processes multiple XML files and writes to multiple output files；A filters out one entry (content.xml) while B processes all pages with transformations；A uses compression (ZLIB), B does not；B involves DOM and XSLT transformations, A does not
- 修正建议: Incorporate dataflow analysis to differentiate between ZIP archiving and XML transformation；Use method signatures and documentation for semantic cues；Train on clones with diverse domain-specific operations but similar I/O structure

### case_id=1137 FN partial_functionality

- 方法: `copyResource` vs `decodeFileToFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource (URL or file) to a destination file byte by byte.
- B 摘要: Decodes a Base64-encoded input file to an output file using buffered streams.
- 静态失败原因: Static models rely on token overlap and structural patterns; low Jaccard similarity (0.194) and differences in method signatures, exception handling, and the presence of Base64 decoding reduce perceived similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this as a clone due to the similar overall structure of file-to-file copying and resource handling, accepting broad Type-3/4 similarity even though the core operations differ (raw copy vs Base64 decode).
- 共享行为: Both copy data from an input source to an output file；Both use InputStream/OutputStream for I/O；Both close streams after operations
- 行为差异: A does no encoding transformation; B decodes Base64；A reads/writes single bytes; B uses buffered bulk read/write；A throws exceptions on failure; B returns boolean success/failure；A does not use finally block for resource cleanup; B does
- 修正建议: Use semantic models that capture higher-level intent, such as data flow and abstract operations；Incorporate type information and API calls to recognize I/O patterns；Apply contrastive learning to distinguish similar I/O patterns with different transformations

### case_id=1138 FN partial_functionality

- 方法: `modifyApplicationMessage` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Modifies a properties file for a given locale by replacing or adding a message key-value pair.
- B 摘要: Copies a file from a given input file to an output file starting from a specified byte position.
- 静态失败原因: Static BERT models rely on lexical token overlap and syntax; low Jaccard (0.126) and different method signatures likely caused failure, as they cannot capture high-level functional similarity beyond token matching.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled this as clone due to broad Type-4 similarity: both are file processing functions that read, transform, and write files with error handling and sequential data processing.
- 共享行为: Both read from an input source；Both write to a file output；Both use try-catch for exceptions；Both involve loops over data
- 行为差异: Function A processes text lines and modifies a specific key-value; Function B copies binary bytes unchanged；Function A may create a new file if not exist; Function B always overwrites；Function A uses character streams; Function B uses byte streams；Function A's input is a locale and message name; Function B's input is file paths and offset
- 修正建议: Enhance model with control-flow and data-flow analysis；Use graph-based representations to capture structural patterns；Incorporate domain knowledge about file I/O patterns；Train on more diverse clone types including Type-4

### case_id=1139 FN partial_functionality

- 方法: `makeBackup` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies files from a source directory to a timestamped backup directory, excluding subdirectories.
- B 摘要: Builds an edited version of a website by processing pages, applying transformations, and writing output files.
- 静态失败原因: The static BERT/GraphCodeBERT model likely relied on token overlap and structural patterns, which are low here (Jaccard=0.104). The model may have been misled by the common file I/O boilerplate but lacked understanding of the distinct semantics.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this as a clone due to both functions involving file reading and writing (Type-4 partial functionality similarity) despite different high-level purposes.
- 共享行为: Both perform file I/O operations, specifically reading from input files and writing to output files.
- 行为差异: Function A is a simple backup utility, while Function B is a complex site-building routine involving XML processing and multiple dependencies.；Function A has a single loop over files in a directory, whereas Function B has nested loops and conditional logic for page rendering.；Function B uses additional libraries (DOM, XSLT, FTP) and handles multiple exceptions, whereas Function A only catches generic Exception.
- 修正建议: Enhance models with program dependency analysis to differentiate between core logic and boilerplate I/O.；Incorporate higher-level semantic representations (e.g., API call intent summarization).；Use contrastive learning on pairs with similar file I/O but different tasks.

### case_id=1140 FN partial_functionality

- 方法: `sendExceptionToServer` vs `getPagina`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `1.0`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends exception details to a server via HTTP POST, encoding various parameters and reading the response.
- B 摘要: Fetches the content of a webpage via HTTP GET and returns it as a string, handling exceptions.
- 静态失败原因: Static models like GraphCodeBERT may focus on surface-level lexical matches (URL, BufferedReader, IOException) but fail to capture the distinct functional intents (sending vs fetching) and the significant differences in data flow and output.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled this as a clone due to both functions involving HTTP communication, error handling, and similar structural patterns (URL, try-catch, read lines), despite different purposes.
- 共享行为: Both functions perform HTTP requests using URL and BufferedReader.
- 行为差异: A sends exception data via POST with URL encoding, B fetches a page via GET without encoding.；A returns void and prints response, B returns the fetched content as a string.；A includes complex parameter building, B simply reads and concatenates lines.
- 修正建议: Incorporate more training examples with contrasting functional roles (e.g., send vs receive) but similar code structure.；Use a model that captures high-level program semantics, such as dataflow or API call sequences.；Apply contrastive learning to separate functions with different I/O behaviors.

### case_id=1141 FP lexical_or_api_overlap

- 方法: `run` vs `fetchUrl`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Downloads tile data from a URL, synchronizes requests, parses the response into VectorTile, extracts geometries, and updates data source.
- B 摘要: Fetches content from a URL and returns it as a string, handling exceptions silently.
- 静态失败原因: The static BERT/GraphCodeBERT model likely focused on the overlapping API usage (URL, BufferedReader, InputStreamReader, readLine) and structural patterns, ignoring the broader context and control flow differences. It may have missed the additional logic in function A such as synchronization, protocol branching, and geometry processing.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled non-clone because the overall functionality differs significantly: one is a complex download-and-parse operation with side effects, the other is a simple URL reader. BCB considers Type-4 (functionally similar but different implementation) as clones only when the core functionality is the same, which is not the case here.
- 共享行为: Both open a URL and read its content line by line, concatenating the result.
- 行为差异: Function A has state management (synchronized list for request tracking) and supports file:// protocol.；Function A parses the fetched data into VectorTile and geometry collections, then interacts with a data source.；Function B is a simple utility that only returns the raw string content.；Function A does exception handling with logging for specific protocol issues; B catches and ignores all exceptions.
- 修正建议: Incorporate data flow analysis to distinguish simple utilities from complex orchestrations.；Use argument structure and return type to capture method purpose (void vs returning String).；Consider learning-based models that combine AST with control flow and token sequences to better capture semantic differences.

### case_id=1142 FN partial_functionality

- 方法: `issueCommandToServer` vs `invoke`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Issues a command to a server using URLConnection, sending form-urlencoded parameters and returning the response as a string.
- B 摘要: Invokes a remote method via HTTP POST using HttpClient, sending JSON-encoded arguments, checking status, and parsing JSON response, with retry on timeout.
- 静态失败原因: Static BERT/GraphCodeBERT models rely on lexical and structural overlap, which is low (Jaccard 0.119). They fail to capture the abstract semantic similarity of the HTTP request-response pattern, especially with different APIs and control flow.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considers these clones as Type-4 due to the shared high-level functionality of performing an HTTP request and processing the response, despite significant differences in libraries, data formats, and error handling.
- 共享行为: Both perform an HTTP request to a remote server.；Both write data to the request body.；Both read the response line by line and return the response as a string.
- 行为差异: Different HTTP client libraries (URLConnection vs HttpClient).；Different request data format (form-urlencoded vs JSON).；Different error handling (none vs status code check and retry on timeout).；Different response processing (plain string vs JSON deserialization based on return type).
- 修正建议: Train on more diverse semantic clones with different API usages.；Incorporate dataflow or API call sequence embeddings.；Use contrastive learning to align representations of similar high-level patterns.

### case_id=1143 FN partial_functionality

- 方法: `login` vs `getPagina`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Logs into LOLA by sending email and password via POST, extracts session ID from response, and returns it.
- B 摘要: Fetches the content of a given URL via GET, reads all lines, and returns the concatenated string.
- 静态失败原因: Low token overlap (0.2239) and distinct domain-specific terms (e.g., 'email', 'pw', 'LOLA' vs 'Authenticator') caused static models to underestimate similarity, missing the abstract I/O pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely labels this as a clone because both functions follow a common pattern of performing an HTTP request, reading the response, and returning a string, with similar control flow and exception handling, matching Type-3/Type-4 clone categories.
- 共享行为: Both create a URL object and open a connection to read data.；Both use BufferedReader to read the response.；Both handle exceptions and return a string result.；Both involve HTTP communication.
- 行为差异: A uses POST with URL-encoded parameters; B uses GET without parameters.；A extracts a specific session ID from a single line; B returns full page content.；A sets session ID in an object; B sets an Authenticator.；A is instance method; B is static.
- 修正建议: Incorporate data flow analysis to detect common I/O operations.；Use API-level abstraction to recognize URL reading patterns.；Leverage method name embeddings to capture intent.；Train with contrastive learning on functional similarity.

### case_id=1144 FN partial_functionality

- 方法: `callService` vs `seeURLConnection`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Constructs URL from fields, opens stream, reads lines, stores in answer field, handles exceptions.
- B 摘要: Opens connection to hardcoded URL, reads lines, logs output, throws exceptions.
- 静态失败原因: Low token Jaccard similarity (0.28), different method names, different exception handling patterns, and different API usage (URL.openStream vs URLConnection) likely caused the static model to classify as non-clone.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels as clone when methods share the same core algorithm (here: fetch URL content line by line), even though error handling and output destinations differ. The structural similarity in the reading loop is high.
- 共享行为: Open a URL and read lines of text into a StringBuffer；Use BufferedReader and InputStreamReader；Loop to read until null；Close the reader
- 行为差异: URL construction: dynamic fields vs hardcoded string；Error handling: caught and stored in field vs propagated as exception；Output: sets answer field vs logs to debug；Uses URL.openStream() vs URLConnection.getInputStream()
- 修正建议: Use graph-based or flow-aware models that capture I/O patterns rather than exact tokens；Normalize API names (e.g., treat 'openStream' and 'getInputStream' as similar)；Add structural similarity based on loop and I/O patterns；Incorporate data flow to see both methods read from URL and accumulate string

### case_id=1145 FP lexical_or_api_overlap

- 方法: `readZoneIDs` vs `PageLoader`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads zone IDs from a resource file, parsing each line as an integer, and returns a set of integers.
- B 摘要: Constructor that reads the entire content of a web page into a string field, throwing an exception on failure.
- 静态失败原因: Static BERT/GraphCodeBERT likely relied on surface-level lexical and structural similarities (e.g., both use URL, InputStreamReader, readLine, similar control flow) without capturing the semantic difference in data processing (parsing integers vs. concatenating strings) and output behavior.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BigCloneBench typically requires functional equivalence or near-identical functionality; these functions have different purposes and outputs, so they are not considered clones.
- 共享行为: Both open a URL stream and read lines of text
- 行为差异: A parses each line as an integer and returns a set; B concatenates lines into a single string with no return value；A uses LineNumberReader, B uses BufferedReader；A catches exceptions silently, B propagates them
- 修正建议: Incorporate data-flow analysis to track how each token is transformed and used；Add contrastive learning on output types and error handling patterns

### case_id=1146 FN benchmark_preference_bias

- 方法: `compressWithZip` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.6`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Compresses a list of files into a single zip archive.
- B 摘要: Builds a website for editing by reading XML, performing XSLT transformations, and writing output files.
- 静态失败原因: Static BERT/GraphCodeBERT models rely on token and structural similarity; the low token Jaccard and distinct API usage (ZipOutputStream vs XSLT) correctly led to a non-clone prediction, but it disagreed with BCB label. The model might have failed to recognize a very high-level similarity that BCB annotators saw.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might have labeled these as clones based on the presence of file I/O loops and buffer usage, considering them as both data processing routines. Alternatively, this might be an annotation error.
- 共享行为: Both iterate over a collection of items (files/pages) and perform file I/O operations.；Both use byte/char buffers for reading input.
- 行为差异: Function A creates a zip archive; Function B generates HTML pages with transformations.；Function A uses ZipOutputStream; Function B uses StreamResult and StringBuffer for output.；Function B involves DOM, XSLT, property files, error handling, FTP, etc. completely absent in A.
- 修正建议: Improve annotation consistency in benchmark；Focus on high-level semantic similarity beyond file I/O；If BCB intends partial functionality, include examples.

### case_id=1147 FN partial_functionality

- 方法: `main` vs `copy`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a URL, decompresses it, and extracts its entries to files.
- B 摘要: Copies a file from source to destination by reading and writing bytes.
- 静态失败原因: The functions have low lexical overlap (Jaccard 0.239) and different method names, and static models focus on token-level similarity or API calls. While both use FileInputStream/FileOutputStream, A also uses URL, ZipInputStream, etc., causing the model to see them as different.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often classifies clones based on common I/O patterns, especially the read-write buffer loop, which is present in both. The high-level functionality of transferring bytes from input to output is similar despite different sources/targets.
- 共享行为: Both read bytes from an input stream and write them to an output stream using a buffer loop.
- 行为差异: A involves URL handling, ZIP decompression, and multiple entries; B is a simple file copy with explicit file streams.
- 修正建议: Train models to recognize common patterns like read-write buffer loops even when embedded in different contexts.；Use dataflow analysis to abstract the core I/O operations.

### case_id=1148 FP boilerplate_overlap

- 方法: `import_hints` vs `getTicketsForQueue`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a file containing puzzle hints and places them on a board.
- B 摘要: Fetches open tickets for a queue from a RequestTracker API and returns them as a list.
- 静态失败原因: Model likely overemphasized the shared I/O boilerplate (BufferedReader, InputStream, reading lines, try-catch) and loop structure, ignoring the completely different domain and purpose.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB correctly labels as non-clone because functions are unrelated in domain and functionality.
- 共享行为: Both read input line by line using BufferedReader；Both parse tokens from lines；Both handle I/O exceptions
- 行为差异: A reads from a file or URL; B makes an HTTP GET request；A places pieces on a board; B collects ticket IDs and retrieves tickets；A returns boolean; B returns a list of tickets or null；A uses StringTokenizer; B uses contains() and startsWith() for parsing
- 修正建议: Use data flow analysis to distinguish different data manipulations；Incorporate semantic role labeling of method calls；Fine-tune with more diverse non-clone pairs having similar boilerplate but different intent

### case_id=1149 FN partial_functionality

- 方法: `copyOverWarFile` vs `doGet`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies .war files from a source directory to the apps data directory and extracts them.
- B 摘要: Handles HTTP GET requests to retrieve and render a page, with caching to file and access control.
- 静态失败原因: Static BERT/GraphCodeBERT correctly predicted non-clone likely due to very low token Jaccard (0.099) and distinct method names and control structures, but missed the partial file I/O overlap that BCB might consider.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider these clones due to partial overlap in file manipulation (both write files using similar Java I/O patterns), and they may be viewed as Type-4 (semantic) based on shared API usage despite different high-level purposes.
- 共享行为: Both perform file I/O operations (reading, writing, creating files)；Both use File, FileInputStream, FileOutputStream, and similar file handling APIs
- 行为差异: Method A is a standalone static utility for copying war files; Method B is a servlet request handler with HTTP context.；Method B has complex page access control, logging, and caching logic; Method A has no such logic.；Method A changes the current working directory; Method B operates on a response object.
- 修正建议: Improve detection of partial functionality clones by incorporating finer-grained API usage patterns.；Use dynamic analysis to capture I/O side effects.；Consider functional role of methods beyond lexical similarity.

### case_id=1150 FP boilerplate_overlap

- 方法: `readTwitterFead` vs `retrieveTemplate`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a Twitter feed using Apache HttpClient, checks HTTP status, and returns the response body as a string.
- B 摘要: Retrieves a cached template from a URL using java.net.URL, reads it line by line, and returns the content as a string; throws an exception if any I/O error occurs.
- 静态失败原因: Static BERT models may have overemphasized the common boilerplate pattern of reading lines and appending to StringBuilder, while ignoring the significant differences in HTTP client, error handling, and caching. The shared tokens (StringBuilder, BufferedReader, readLine) and similar control flow (while loop) may have led to a high embedding similarity, causing a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled this as non-clone because the implementations differ in HTTP client usage, error handling, and caching, despite both performing a similar high-level task of reading from a URL. The low token similarity also suggests they are not structurally similar enough for a Type-3 clone.
- 共享行为: Both functions connect to a remote URL and read its content.；Both use a BufferedReader to read the stream line by line.；Both append each line to a StringBuilder and eventually return the concatenated string.
- 行为差异: Function A uses Apache HttpClient (HttpGet) while Function B uses java.net.URL.；Function A checks HTTP status code (200) and logs an error if not 200; Function B does not check status and throws exceptions on errors.；Function B caches the result in a field (cachedTemplate); Function A does not cache.；Function A catches specific exceptions (ClientProtocolException, IOException); Function B throws Exception.
- 修正建议: Incorporate data flow analysis to differentiate API calls and error handling.；Use AST-based differencing to capture structural dissimilarities like different exception handling or method calls.；Apply contrastive learning or hard negative mining to reduce false positives on boilerplate-heavy code.

### case_id=1151 FP boilerplate_overlap

- 方法: `doRawRequest` vs `readZoneIDs`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Sends HTTP POST request and returns response body as string.
- B 摘要: Reads integers from a resource file and returns them as a set.
- 静态失败原因: Static BERT may have been misled by similar structural patterns (URL connection, line reading loop) and API tokens (URL, readLine, close). The lexical overlap in boilerplate IO code caused a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would likely label non-clone because the core functionalities are different: A is a generic HTTP POST client, B parses a resource file for zone IDs. Although both involve reading lines from a URL, the intent and output types are distinct, making it not a clone per BCB guidelines.
- 共享行为: Open a URL connection；Read lines from an input stream；Handle IO resources (close streams)
- 行为差异: Function A writes data to the connection (POST), while B only reads；Function A returns a concatenated string, B returns a HashSet of integers；Function A throws IOException, B catches Exception and prints stack trace；Function A uses OutputStreamWriter and BufferedReader, B uses LineNumberReader
- 修正建议: Include functional purpose into representation (e.g., via method name or comment embedding)；Differentiate between write-and-read vs read-only patterns；Incorporate output type information to disambiguate

### case_id=1152 FP boilerplate_overlap

- 方法: `copy` vs `readData`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Copies a file from source to destination using NIO channels with proper resource cleanup.
- B 摘要: Reads configuration strings and a file to populate multiple sets and maps for Tibetan transliteration processing.
- 静态失败原因: The static BERT model likely focused on boilerplate patterns (e.g., nested try-catch-finally blocks) common to both functions, missing that the core operations are entirely different.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would not consider these clones because they have completely different purposes and no shared functionality, even under broad Type-3/Type-4 definitions.
- 行为差异: Function A performs file copy; Function B parses configuration data and populates data structures.；A uses FileInputStream/FileOutputStream and FileChannel; B uses StringTokenizer and file parsing with error handling.；A takes two string parameters; B has no parameters and relies on class fields.
- 修正建议: Enhance model to distinguish between boilerplate and core logic using data-flow analysis.；Train on contrastive examples where resource management patterns are present but semantics differ.

### case_id=1153 FN partial_functionality

- 方法: `run` vs `invoke`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a resource file from classpath and sets its content into a JTextArea on the Event Dispatch Thread.
- B 摘要: Makes an HTTP POST call, reads the response body, deserializes JSON into an object of the method's return type, and retries on connection timeout with service discovery.
- 静态失败原因: The model likely overemphasized low lexical overlap and different high-level context (GUI vs. HTTP client), failing to recognize the structural I/O pattern that BCB considers as partial functionality similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this as a clone because both functions involve the common I/O pattern of opening an input stream, reading lines, building a string, and closing resources, which is considered Type-3/4 similarity despite different high-level purposes.
- 共享行为: Both read lines from an InputStream using BufferedReader；Both build a StringBuilder from the lines；Both close streams and readers
- 行为差异: A reads a local resource file; B makes an HTTP call；A updates a GUI component; B returns a deserialized object；B includes JSON deserialization and retry logic for connection timeouts；B uses HTTP client libraries and handles status codes
- 修正建议: Train the model to recognize structural patterns like stream reading and string building even when surrounding code differs；Incorporate code abstraction or data-flow analysis to capture common I/O idioms；Use token abstraction techniques to normalize I/O patterns

### case_id=1154 FP lexical_or_api_overlap

- 方法: `callService` vs `loadURL`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a URL constructed from fields and stores the entire response as a string in an instance variable.
- B 摘要: Reads a URL with optional basic auth, writes the content to a temp file while updating a status label, throws IOException.
- 静态失败原因: The static model likely overemphasized the lexical overlap (both use URL, BufferedReader, while loop reading lines) and similar boilerplate for HTTP data retrieval, missing the distinct overall purposes and output behaviors.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB considers them non-clones because the overall functionality differs: one is a simple service caller that returns a string, the other is a file downloader with authentication and progress reporting.
- 共享行为: Both open a URL；Both use BufferedReader to read lines；Both handle the input stream
- 行为差异: A uses url.openStream() directly, B uses URLConnection with optional auth；A concatenates all lines into a single string buffer, B writes each line to a file and updates GUI；A handles exceptions locally, B throws IOException；A stores result in field 'answer', B writes to temp file
- 修正建议: Incorporate more global context or task-level semantics；Use features like method signature, field usage, and exception handling to differentiate；Consider data flow and output behavior

### case_id=1155 FN partial_functionality

- 方法: `getFile` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.65`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies the endpoint attribute in the XML, and saves it to a temporary location.
- B 摘要: Copies a file from an input stream to an output stream using a buffer.
- 静态失败原因: The static BERT model likely focused on the low token Jaccard similarity (0.1567) and the obvious difference in method names and overall purpose (download vs copy). It may not capture the deeper structural similarity of the file I/O pattern (stream creation, buffer loop, error handling) that BCB considered as partial functional overlap.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled these as clones because both implement file copying as a core sub-task, and the 'copyFile' function is essentially a reusable file copy utility that appears within the larger 'getFile' function. Under a broad Type-4 (semantic) clone definition, shared functionality like file I/O with buffered copying could be considered clone-worthy even if the overall context differs.
- 共享行为: Both perform file I/O operations using streams.；Both handle IOException and close streams in finally blocks.；Both use FileInputStream/FileOutputStream or similar stream classes.
- 行为差异: Function A downloads from a network URL, while B copies a local file.；Function A parses and modifies XML, B does not.；Function A creates and manages temporary files and renaming, B does not.；Function A returns a file path string, B returns a boolean success flag.
- 修正建议: Enhance model with subgraph matching that identifies common I/O patterns.；Incorporate data-flow analysis to recognize similarly structured stream operations.；Use contrastive learning with BCB's broad clone definitions to adapt to partial functionality overlap.

### case_id=1156 FN benchmark_preference_bias

- 方法: `sendExceptionToServer` vs `PhoneSetImpl`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Sends exception details to a server via HTTP POST with encoded parameters and prints server response.
- B 摘要: Constructs a PhoneSetImpl object by reading lines from a URL and parsing them into a map, ignoring comment lines.
- 静态失败原因: The model correctly identified the low token overlap and distinct functional purposes (send vs. parse), leading to a non-clone prediction; however, BCB's lenient annotation based on broad network I/O similarity was not captured by the model.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have considered both as network I/O functions that read from a URL and process lines, categorizing them as Type-4 clones due to similar high-level structure despite different specific operations.
- 共享行为: Both use URL to connect to a network resource；Both use BufferedReader and InputStreamReader to read lines；Both have while loops that read lines until null；Both handle IOException (one catches, one throws)
- 行为差异: Function A performs HTTP POST with parameters; Function B performs HTTP GET without sending data；Function A sends encoded exception details and checks for 'success' response; Function B parses lines into a map based on '***' prefix；Function A catches IOException and prints error; Function B declares throws IOException；Function A is a private static utility; Function B is a constructor initializing a map
- 修正建议: Use functional semantics rather than lexical overlap；Incorporate API call patterns to distinguish send vs. receive；Align training labels with more strict functional equivalence criteria

### case_id=1157 FN partial_functionality

- 方法: `getWebPage` vs `fileDownload`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Returns the string content of a web page given a URL.
- B 摘要: Downloads a file from a URL to a local directory.
- 静态失败原因: Static BERT models rely heavily on token overlap and method name similarity, which are low here (Jaccard 0.111, different names). They missed the structural similarity of the reading loop and URL handling context.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this as a clone because both functions perform similar core operations of opening a URL and reading data line by line, even though the output handling differs. In BigCloneBench, Type-3/4 clones with partial functionality similarity are often accepted.
- 共享行为: Both open a URL connection and read content line by line；Both use BufferedReader and InputStreamReader；Both handle IOException (though differently)
- 行为差异: Function A returns the content as a String, while B writes it to a file；Function A throws an Error on exception, B logs the exception；Function B extracts filename from the URL and uses FileOutputStream；Function A appends lines to a string, B writes each character to output stream
- 修正建议: Use graph-based models that capture control/data flow；Incorporate code structures like AST or data flow edges；Leverage fine-tuning on clone detection datasets with partial functionality clones

### case_id=1158 FP partial_functionality

- 方法: `run` vs `GetResponse`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads tile data from a URL or file, parses JSON into geometries, and adds to display cache.
- B 摘要: Performs HTTP GET request and returns the response content as a string.
- 静态失败原因: Static models may focus on token overlap (URL, BufferedReader, while loop) and miss the larger context and semantic differences. The common pattern of reading from URL may have triggered a false positive.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely annotates as non-clone because the overall functionality differs significantly; the shared URL reading loop is insufficient to consider them clones given A's additional processing and side effects.
- 共享行为: Both open a URL connection and read lines from an input stream into a string.
- 行为差异: B only handles HTTP; A handles both file and HTTP protocols.；A processes the downloaded string into GeoJSON geometries and updates data structures.；A uses synchronization and locking; B does not.；A has side effects on external caches; B only returns a string.
- 修正建议: Incorporate dataflow analysis to track that the downloaded content in A is further transformed.；Include method signatures and call context to distinguish utility functions from domain-specific operations.；Increase sensitivity to method length and side effects.

### case_id=1159 FN benchmark_preference_bias

- 方法: `sendExceptionToServer` vs `importRoles`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Sends exception details to a remote server via HTTP POST.
- B 摘要: Imports role names from an XML file accessed via URL.
- 静态失败原因: Low lexical overlap and different method names caused the model to correctly reject strict equivalence, but it missed the broad BCB annotation goal.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have considered both as performing 'network I/O' tasks, a broad functional category, ignoring specific details.
- 共享行为: Both open a URL and read from it using BufferedReader；Both handle IOException；Both use while loop to read lines
- 行为差异: A uses POST to send data, B uses GET to read data；A constructs a complex query string, B parses XML；A returns void, B returns a list of RoleName objects；A writes to output stream, B only reads
- 修正建议: Fine-tune with BCB-style labels that allow broad functional similarity；Use dataset-specific similarity thresholds for partial functionality

### case_id=1160 FP lexical_or_api_overlap

- 方法: `convert` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Converts an ACRNEMA stream file to DICOM format by adding UIDs and handling pixel data.
- B 摘要: Handles UI action commands to set external tool paths and apply settings, with a long block of preference updates.
- 静态失败原因: Static BERT likely overemphasized superficial token overlap (e.g., 'File', 'InputStream', 'OutputStream') and structural patterns like try-finally, while ignoring the distinct semantic contexts and control flows.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically requires high functional similarity; these two functions have completely different purposes and logic, so they are correctly labeled non-clone.
- 共享行为: Both use File objects for file selection/writing；Both involve conditional checks and loops
- 行为差异: A performs binary file conversion with pixel data manipulation; B handles GUI events and stores user preferences；A reads from input stream and writes to output stream; B uses JFileChooser and updates UI components；A has system output for progress; B uses dialog messages and preference storage
- 修正建议: Incorporate function signature matching (name, parameters, return type)；Use control flow graph or data flow analysis to compare high-level behavior；Train with more diverse negative examples to reduce false positives

### case_id=1161 FN benchmark_preference_bias

- 方法: `copyResource` vs `forBundle`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.6`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Copies a resource from a URL or file to a local file byte by byte.
- B 摘要: Processes a bundle by reading template files and manifest, creating a zip jar, and installing it as a plugin.
- 静态失败原因: Static BERT/GraphCodeBERT relies on token overlap and structural similarity; the low Jaccard similarity (0.147) and distinct code structures led to a correct non-clone prediction under strict semantics, but failed to capture the broader, partial functionality similarity that BCB might accept.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this a clone due to the common I/O pattern of opening an input stream from a URL and writing to an output stream, possibly considering both as 'resource copying' tasks despite vastly different overall purposes.
- 共享行为: Both open input streams from URLs.；Both perform copying from input to output streams.
- 行为差异: A copies a single resource to a file; B processes multiple files and creates a zip.；B involves bundle manipulation, plugin installation, and package refresh; A has no such functionality.；A is a simple file copy; B is a complex multi-step process.
- 修正建议: Train models with Type-3/Type-4 clone examples to recognize partial functionality similarity.；Incorporate functional similarity metrics beyond lexical overlap, such as data flow or API usage patterns.

### case_id=1162 FN benchmark_preference_bias

- 方法: `doGet` vs `run`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Handles HTTP GET request to retrieve and display a page, with visibility checks and caching.
- B 摘要: Generates a XUL Firefox extension package by parsing XML and writing zip entries.
- 静态失败原因: Static BERT/GraphCodeBERT likely correctly identified the low token and syntactic similarity, correctly predicting non-clone, but BCB's label is questionable here.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled these as clones due to a very broad interpretation of 'input-processing-output' pattern with exception handling, or possibly a mislabeling given the low token overlap and lack of clear shared functionality.
- 行为差异: One is a servlet handling HTTP request/response; the other is a utility method for file generation.；Function A deals with web page retrieval and user permissions; Function B deals with XML parsing and zip creation.；Different error handling: A uses servlet-specific exceptions; B uses SAX and IO exceptions.；Different output: A writes HTML to response; B writes a zip archive to output stream.
- 修正建议: Review BCB label for potential mislabeling; if accepted, incorporate high-level semantic patterns beyond lexical overlap.

### case_id=1163 FN partial_functionality

- 方法: `getResourceAsStream` vs `run`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Retrieves a resource by name, caching the result locally after downloading via HTTP if necessary.
- B 摘要: Downloads all files from a Hadoop filesystem directory into a single local file.
- 静态失败原因: The two functions have low token overlap (0.157), different method names, and distinct control structures. Static BERT-based models rely heavily on lexical and syntactic cues and lack the ability to infer deep semantic similarity across different APIs (HTTP vs Hadoop).
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB annotators may have considered both as 'download' operations, focusing on the common pattern of opening a remote connection and writing to a local file, ignoring differences in protocol and data aggregation.
- 共享行为: Both involve reading data from a remote source and writing to local storage using streams.
- 行为差异: Function A uses HTTP URL connections and caching; function B uses Hadoop FileSystem API.；Function A handles a single resource; function B handles multiple files from a directory.；Function A returns an InputStream; function B returns an exit code.
- 修正建议: Improve training data with more Type-3/Type-4 clones that share high-level purpose but differ in implementation details.；Use data flow analysis to capture I/O patterns across different APIs.；Incorporate knowledge of common library APIs (e.g., HTTP, Hadoop) to abstract away specifics.

### case_id=1164 FP lexical_or_api_overlap

- 方法: `addDataFromURL` vs `handleHandshake`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads content from a given URL line by line and appends it to a text buffer.
- B 摘要: Handles a Minecraft handshake packet by validating the username, performing session authentication via HTTP, and sending appropriate packets or disconnecting.
- 静态失败原因: Static embedding models often rely on token overlap and common API patterns; both functions use URL and BufferedReader, leading to high similarity in token embeddings.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels non-clones when functions have completely different purposes despite superficial API overlap.
- 共享行为: Both use URL and BufferedReader for network I/O
- 行为差异: Function A simply downloads and stores data; Function B validates identity and manages game protocol；Function A appends all lines to a buffer; Function B conditionally sends packets or shuts down connection；Function B has complex branching based on username validation and server response
- 修正建议: Enhance models to capture program control flow and data dependencies beyond API usage；Include structural context like method names and surrounding code

### case_id=1165 FP boilerplate_overlap

- 方法: `get` vs `setMembers`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Sends HTTP GET request with game query parameters, parses response lines, and returns array of GameRecord objects.
- B 摘要: Fetches HTML from a Trac URL, extracts component and priority options from select elements, and stores them in class member arrays.
- 静态失败原因: Static BERT/GraphCodeBERT models may over-rely on surface-level patterns like HTTP connection setup, BufferedReader usage, and while-loop reading. The high overlap in API calls (URL, BufferedReader, try-catch) can mislead the model into ignoring the fundamentally different processing logic inside the loop.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB considers Type-3/4 clones as those with similar functionality. Despite similar boilerplate (HTTP read loop), the core logic and purpose differ significantly: one is a game record API fetcher, the other a Trac ticket system component parser. BCB would not label these as clones because the behavioral similarity is superficial.
- 共享行为: Both make HTTP connections and read input streams line by line；Both use BufferedReader and try-catch for IOException；Both involve parsing response data (lines vs HTML)；Both return or store results in arrays
- 行为差异: Function A returns an array of GameRecord objects; Function B sets class members (m_strComponents, m_strPriorities)；Function A uses custom headers and query parameters; Function B parses HTML select tags with regex；Function A ignores lines starting with '#'; Function B processes HTML content；Function A has a return null on failure; Function B has no return value (void)
- 修正建议: Include dataflow analysis to track how input streams are processed；Use structure-aware attention to differentiate between similar API usage patterns and actual logic；Add negative sampling with boilerplate-only pairs to reduce false positives；Incorporate functional semantics via method name and return type analysis

### case_id=1166 FP lexical_or_api_overlap

- 方法: `extractUninstallFiles` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Extracts uninstall files, manages backup and directory operations for upgrade.
- B 摘要: Handles user action events in settings UI, updates preferences and components.
- 静态失败原因: The model likely overemphasized common structural elements (try-catch, file operations, loops) and overlooked the distinct method names and overall functional purpose.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels these as non-clones because they perform completely different tasks (uninstall management vs. UI event handling) despite sharing some generic file handling patterns.
- 共享行为: Both use File objects and file operations；Both contain conditional logic and exception handling
- 行为差异: A is about uninstall file extraction; B is about UI event handling；A returns a File; B is void；A deals with jar entries and directories; B deals with file choosers and preferences；A has upgrade logic; B has no upgrade concept
- 修正建议: Incorporate method name more strongly into the representation；Use graph-based or dataflow analysis to capture semantic intent；Train with more diverse examples to reduce bias towards boilerplate patterns

### case_id=1167 FP boilerplate_overlap

- 方法: `main` vs `copyFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Generates adapters from a Prolog file and writes them to a JAR with annotations.
- B 摘要: Copies a file from input to output using a buffered stream.
- 静态失败原因: The model likely focused on the overlapping file I/O API calls (e.g., FileInputStream, IOException) and exception handling patterns, ignoring the disparate high-level logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the functions serve completely different purposes despite sharing generic file I/O boilerplate; the core semantics are unrelated.
- 共享行为: Both perform file I/O operations.；Both handle IOException with try-catch.；Both use InputStream and OutputStream classes.
- 行为差异: Code A is a code generation tool; Code B is a simple file copy.；Code A reads entire file as string for parsing; Code B reads in chunks.；Code A writes to a JAR file; Code B writes to a plain file.；Code A has complex logic with parsing and class generation; Code B is straightforward I/O.
- 修正建议: Train models to weight structural differences more heavily than common library usage.；Incorporate control-flow or data-flow analysis to distinguish algorithmic patterns.；Use fine-tuning with examples that penalize boilerplate overlap.

### case_id=1168 FN partial_functionality

- 方法: `getResourceAsStream` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Retrieves a resource as an InputStream, using a local cache and handling HTTP connections to download the resource if not already cached.
- B 摘要: Copies a file from source to destination using file streams and a buffer, returning a boolean success flag.
- 静态失败原因: Static BERT models rely on token and structural similarity; the low Jaccard similarity (0.2075) and different method names, parameter types, and control flow caused the model to miss the underlying shared stream I/O behavior. The model likely focuses on surface-level differences rather than abstract functional similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as instances of a common 'stream copy' pattern, where data is read from an input source and written to an output destination, despite differences in source/destination types and additional logic. This fits Type-3/Type-4 clone criteria where partial functionality similarity is accepted.
- 共享行为: Both read from an InputStream and write to an OutputStream；Both close streams in finally blocks；Both handle I/O exceptions
- 行为差异: Method A involves HTTP connection, caching logic, and URL handling; Method B is a straightforward file copy；Method A returns an InputStream; Method B returns a boolean；Method A has conditional cache checks and multiple file operations; Method B writes directly
- 修正建议: Use data-flow-aware models like GraphCodeBERT that capture stream operations；Train with more diverse Type-4 clones to recognize abstract patterns；Incorporate code simplification or normalization to highlight common I/O patterns

### case_id=1169 FP boilerplate_overlap

- 方法: `getVersion` vs `run`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches a version string from a remote URL and returns it.
- B 摘要: Reads a webpage from a localhost URL and discards all content.
- 静态失败原因: Static BERT models may over-rely on common API patterns (URL, BufferedReader, readLine) and lexical overlap, missing the critical semantic difference of how the read data is used (return vs. discard).
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clone because the core functionality differs: one retrieves and returns a string, the other reads and discards without output. The method signatures and contexts are also different.
- 共享行为: Both open a URL and use BufferedReader to read lines.；Both handle exceptions silently.
- 行为差异: A returns the read data; B discards it.；A uses a public URL; B uses a localhost URL.；A is private static with a return value; B is public void.；A returns null on failure; B just catches exceptions.
- 修正建议: Incorporate dataflow analysis to track usage of read data.；Increase sensitivity to return types and method signatures.；Use dynamic analysis or IO-aware features.

### case_id=1170 FN lexical_or_api_overlap

- 方法: `checkInputStream` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Checks if an InputStream's content matches a given byte array.
- B 摘要: Builds a site for editing by transforming XML and writing output files.
- 静态失败原因: Low token Jaccard (0.052) and no structural similarity; potential false positive due to rare shared tokens like 'InputStream' and 'IOException' triggering lexical overlap bias.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may have mislabeled due to superficial API usage overlap (e.g., InputStream, IOException) or a mistaken belief that both perform some file I/O, but the behaviors are fundamentally different.
- 共享行为: Both involve InputStream reading
- 行为差异: A is a simple comparison helper, B is a complex multi-step build process；A has no XML or file writing, B has extensive XML and file operations；A is private, B is public；A has no dependencies on external properties, B uses environment and user properties
- 修正建议: Improve training data with more negative examples that share API terms but differ semantically；Incorporate dataflow or control-flow features to distinguish simple helpers from complex build methods

### case_id=1171 FN partial_functionality

- 方法: `copy` vs `doGet`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.5`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a file from source to destination with comprehensive error checks and stream handling.
- B 摘要: Handles an HTTP GET request for a portal page, including page retrieval, caching, and response generation.
- 静态失败原因: Static BERT models rely on token and structure similarity, which is very low here (Jaccard=0.1379). They cannot infer high-level behavioral overlap like file I/O from a small subcomponent.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider them clones due to the shared file I/O operations and similar validation patterns, albeit in very different contexts, reflecting a broad Type-4 or partial functionality similarity.
- 共享行为: Both perform file I/O operations (reading/writing files)；Both check file/directory existence and permissions；Both handle exceptions and errors
- 行为差异: Function A is solely a file copy utility, while B is a web request handler；Function A uses FileInputStream/FileOutputStream, B uses FileWriter and response streams；Function B involves complex business logic (page retrieval, user permissions, caching) absent in A
- 修正建议: Improve detection of partial functionality by incorporating subgraph matching or code summarization；Use dynamic analysis or execution trace similarity to capture I/O patterns；Refine BCB labeling criteria to avoid over-broad clone definitions

### case_id=1172 FP lexical_or_api_overlap

- 方法: `doVersionCheck` vs `readScalarpvviewerDocument`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Checks for a new version of jEdit by reading a remote properties file and comparing build numbers.
- B 摘要: Reads a configuration file for a scalar PV viewer, parsing XML-like data to restore application state.
- 静态失败原因: The model likely over-relied on lexical and API overlaps (URL, BufferedReader, while loop, IOException) common in many I/O routines, ignoring the distinct domain-specific logic and different output behaviors.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels as non-clone because the functions have entirely different purposes and only share generic I/O patterns, which is insufficient for clone annotation in BigCloneBench.
- 共享行为: Both read lines from a URL via BufferedReader；Both catch IOException
- 行为差异: Different parsing logic: property extraction vs. XML-like configuration parsing；Different outcomes: version check message vs. restoring viewer state；Different structure: one uses simple key-value extraction, the other uses multiple adaptors for nested config
- 修正建议: Use dataflow analysis to capture semantic differences in variable usage and control flow；Incorporate structural similarity measures that penalize generic boilerplate；Apply context-aware embeddings that distinguish domain-specific operations

### case_id=1173 FN partial_functionality

- 方法: `copyFile` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a source file to a destination file using FileChannel.
- B 摘要: Downloads a KMZ file from a URL and extracts its entries to files.
- 静态失败原因: Static BERT/GraphCodeBERT models rely heavily on token overlap and syntax structure; low Jaccard similarity and different method signatures led the model to miss the underlying functional commonality in file I/O operations.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels as clones when both functions belong to the same high-level functional category (e.g., File-Input/Output) despite implementation differences, reflecting broad Type-4 similarity.
- 共享行为: Both perform file I/O operations involving reading and writing data.；Both use stream/channel resources and ensure proper cleanup.；Both write output to disk.
- 行为差异: Input source: local file (A) vs remote URL (B).；Output: single file copy (A) vs extraction of multiple zip entries (B).；Processing: direct channel copy (A) vs buffered stream extraction (B).
- 修正建议: Augment training data with functional category labels.；Incorporate control-flow or data-flow features.；Use models that capture high-level semantics beyond token overlap.

### case_id=1174 FN benchmark_preference_bias

- 方法: `getFile` vs `unzip`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies an XML attribute, and saves it to a temporary directory.
- B 摘要: Extracts the contents of a ZIP file into a directory, creating subdirectories as needed.
- 静态失败原因: The static BERT model correctly identified the low token overlap and different semantics, predicting non-clone. It did not 'fail' except relative to the possibly erroneous BCB label. The model's prediction aligns with a reasonable interpretation of clone detection.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might label these as clones based on a very loose interpretation of 'file processing' or 'stream I/O', but this is inconsistent with typical BCB Type-3/4 criteria which require stronger semantic or structural similarity.
- 共享行为: Both use file I/O streams and handle IOException.；Both involve file creation and temporary storage.
- 行为差异: Function A downloads over HTTP and parses/modifies XML; Function B decompresses a ZIP archive.；Function A writes a single file with XML manipulation; Function B extracts multiple files and directories.；Function A uses NIO channels for data transfer; Function B uses traditional buffered streams.；Function A has complex error handling for multiple exception types; Function B only handles ZipException and IOException.
- 修正建议: Review and correct the BCB annotation for this pair.；Consider that token-based models may be too conservative for low-similarity non-clones.；Use semantic analysis to confirm the lack of shared functionality.

### case_id=1175 FN partial_functionality

- 方法: `main` vs `getXML`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.75`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: main method that constructs and sends a POST request to RenRen API with predefined parameters and prints the response.
- B 摘要: getXML method that performs an HTTP GET request to a given servlet URL with a request parameter and returns the response as a string.
- 静态失败原因: The token Jaccard is low (0.144), and the functions have different method names, different number of statements, and different APIs used (PostParameter, Utils, RenRenPostParameters vs URLEncoder, StringBuffer). A static BERT model might focus on token-level overlap and not capture the high-level similarity in HTTP request-response pattern. Also, model may be misled by the large amount of boilerplate in A (many PostParameter additions) which is not present in B.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider them clones because both are HTTP client functions that retrieve data from a URL and process the response line by line, representing a common programming pattern. The differences in protocol and parameter building are considered variant implementations of the same core task.
- 共享行为: Opens a URL；Reads input line by line；Handles IOException
- 行为差异: A uses POST, B uses GET；A constructs parameters with Utils, B encodes request but doesn't use；A prints to console, B returns string；A has specific API keys and session tokens, B is generic
- 修正建议: Use dataflow or graph representations to capture the network I/O intent；Augment training with examples that have low token overlap but similar control flow；Employ contrastive learning with functional equivalence

### case_id=1176 FP dataflow_blindspot

- 方法: `readData` vs `run`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_with_trace`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Parses comma-separated string fields to populate sets and maps for Tibetan transliteration data.
- B 摘要: Downloads all files from an HDFS directory to a local file by concatenating them.
- 静态失败原因: Static BERT models may rely on token-level patterns and may be misled by common keywords like 'while', 'try', 'IOException', and 'String', or by the presence of multiple loops in both functions. They may fail to capture the deep semantic differences in dataflow and domain-specific operations.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 dataflow_trace_and_outputs。
- BCB 偏好解释: BCB annotators likely judged these as non-clones because they have entirely different functionality, different purpose, different I/O patterns, and no shared underlying algorithm. The low token Jaccard (0.07) also supports non-clone status.
- 共享行为: None; functions are unrelated
- 行为差异: A uses StringTokenizer to parse configuration strings; B uses FileSystem API to read files.；A populates multiple in-memory data structures (HashSet, HashMap); B writes to an OutputStream.；A operates on global static fields; B takes arguments and returns an int status.；A has complex logic for handling tokens and building lookup tables; B is a simple loop copying bytes.
- 修正建议: Incorporate dataflow analysis or program dependence graphs into the model.；Use more fine-grained token embeddings that capture API-level semantics.；Train on a more diverse set of non-clone pairs to reduce overgeneralization of loop-heavy patterns.

### case_id=1177 FN partial_functionality

- 方法: `getHTML` vs `loadMFileViaWeb`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads HTML from a URL and optionally writes it to a file.
- B 摘要: Downloads MATLAB M-file source code from a URL and parses it into a UserFunction object.
- 静态失败原因: The static model likely relied on token-level features and method signatures, which differ significantly (different method names, return types, and API calls). The low token Jaccard (0.2289) and different exception handling patterns may have misled the model into considering them non-clones, despite the shared URL reading pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels Type-3/Type-4 clones where the core functionality (downloading text from URL) is similar, even if the surrounding code and purpose differ. The structural similarity in the URL reading loop is sufficient for a clone label.
- 共享行为: Establish a URL connection and read content line by line using BufferedReader；Handle exceptions with try-catch and close resources in finally；Concatenate lines into a single string
- 行为差异: getHTML returns raw HTML string, loadMFileViaWeb returns a parsed UserFunction object；getHTML optionally writes the content to a file, loadMFileViaWeb parses the content using FunctionParser；getHTML uses HttpURLConnection with custom User-Agent header, loadMFileViaWeb uses URL.openStream()；Exception handling differs: getHTML prints stack trace, loadMFileViaWeb throws a custom exception
- 修正建议: Incorporate AST or control flow graph information to capture structural similarity beyond tokens；Use data-flow analysis to identify common I/O patterns；Train on more examples of URL reading functions with varying API usage to generalize the pattern

### case_id=1178 FN partial_functionality

- 方法: `runScript` vs `retrieveQ`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a script file from the applet's codebase and returns its content as a string, with error fallback.
- B 摘要: Retrieves content from a given URL and returns it as a string, preserving line breaks, and prints connection response message.
- 静态失败原因: Static BERT models rely on lexical and syntactic overlap; the low Jaccard similarity (0.17) and significant differences in method signatures, control flow, and API usage caused the model to miss the high-level semantic similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB labels these as clones because both implement the core functionality of fetching a resource from a URL and returning its textual string representation, which is a common pattern, despite differences in implementation details.
- 共享行为: Both open a URL and read its textual content；Both return the content as a string
- 行为差异: Different URL construction (codebase vs direct URL)；Different reading method (byte-by-byte vs line-by-line)；Error handling (return error string vs throw exceptions)；Side effect (none vs stderr output)
- 修正建议: Use program analysis to abstract away implementation details and focus on input-output behavior；Augment training data with diverse implementations of the same functionality；Incorporate code summarization or functional representation learning

### case_id=1179 FN partial_functionality

- 方法: `writeFileType` vs `read`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads URIs from a file, fetches each URI's content, checks for RDF/OWL namespaces, and writes classification tags (OWL, RDFS, RDF, UNKNOWN, BROKEN) to an output file.
- B 摘要: Reads a resource from a given name (URL or file path), opens a stream, calls another read method, and returns a status code.
- 静态失败原因: Low token overlap and different method signatures (void vs int, extra parameters) likely caused the model to see them as unrelated, missing the shared URL-reading core.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as 'reading from URLs' and enough functional overlap despite different purposes, or the annotation guidelines accept broad Type-3/Type-4 with partial functionality.
- 共享行为: Both open a URL connection to read content from a remote resource.
- 行为差异: A processes multiple URIs from a file with classification; B reads a single resource and returns status.；A writes to an output file; B returns an integer status.；A has custom error handling that writes 'BROKEN'; B returns STATUS_OPEN_ERROR.；A reads line-by-line with a 100-line limit; B uses BufferedInputStream and delegates reading.
- 修正建议: Incorporate data-flow or control-flow graphs to capture shared substructures.；Use contrastive learning with functional equivalence labels.；Enhance model with code docstrings or comments to infer intent.

### case_id=1180 FP lexical_or_api_overlap

- 方法: `startScript` vs `downloadModel`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Start script by downloading text from a URL line by line and appending to dialog buffer; exits on IO error.
- B 摘要: Download an RDF model from a URL by reading HTTP response and parsing as RDF; wraps exceptions in RuntimeException.
- 静态失败原因: Static models may rely on shallow patterns like URL.openStream, BufferedReader, and IOException, causing false positive when code snippets share common API usage but different data processing.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely treats these as non-clones because their core functionality differs: one is a script loader, the other a model downloader. The similar I/O pattern is not enough to overcome the semantic gap.
- 共享行为: Both open a URL and read data from an input stream；Both handle IOException
- 行为差异: A reads text lines and concatenates; B reads binary/XML and parses into Model object；A exits on IO error; B rethrows as RuntimeException；B sets HTTP headers; A does not
- 修正建议: Train with more discriminative features capturing data type transformations；Incorporate long-range semantics or data flow analysis to distinguish text vs model parsing；Use contrastive learning to emphasize functional differences despite similar I/O wrappers

### case_id=1181 FN partial_functionality

- 方法: `copyResource` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource (URL or file) to a destination file using byte-by-byte streaming without error checks or user interaction.
- B 摘要: Copies a file to a destination with permission checks, overwrite prompt, and progress indicator using buffered I/O.
- 静态失败原因: Low lexical overlap (token Jaccard 0.18) and focus on surface-level differences (e.g., error handling, user prompts) caused the model to miss the core functional similarity in copying input to output.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BigCloneBench may consider this a Type-4 clone because both functions perform the essential task of copying data from an input to an output file, even though the implementations and additional functionality differ significantly.
- 共享行为: Both copy bytes from an input source to an output file using streams；Both close the input and output streams after copying
- 行为差异: A reads from URL or file; B only from file；A reads byte by byte; B uses buffered read；B has extensive error checking and user interaction for overwrite；B displays progress indicators
- 修正建议: Enhance model with AST-based features to capture structural similarity；Use contrastive learning to emphasize core I/O operations；Augment training data with diverse implementations of the same functional task

### case_id=1182 FN partial_functionality

- 方法: `login` vs `callApiPost`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Logs into LOLA service by sending HTTP POST with email and password, then extracts and returns session ID.
- B 摘要: Calls a generic POST API with given URL and parameters, returning an InputStream after checking response status.
- 静态失败原因: Static BERT models likely focus on lexical overlap and high-level semantic meaning, missing the structural commonality of HTTP POST due to different method names, return types, and error handling.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB considers both as implementing the common pattern of making an HTTP POST request with parameters, which is a core shared functionality despite differences in specifics.
- 共享行为: Both perform HTTP POST requests to a URL；Both set connection output to true and write data to output stream；Both flush the output stream before reading response；Both read from the input stream after request
- 行为差异: A is specific to login with hardcoded fields; B is generic with parameters map；A returns a session ID string; B returns an InputStream；A catches broad Exception and returns empty string on error; B catches IOException and throws custom exception；A uses URLConnection; B uses HttpURLConnection with additional settings (timeout, headers, method)
- 修正建议: Incorporate data-flow analysis to capture common API usage patterns；Use fine-tuning on BCB-style labels to learn preference for partial functionality similarity；Add attention to method-level behavior rather than token-level

### case_id=1183 FN partial_functionality

- 方法: `getHTML` vs `getWebByUrl`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches HTML content from a URL using HTTP, optionally writes to file, and returns the content as string.
- B 摘要: Fetches web content from a URL, writes to file with logging, and recursively extracts URLs from the page if within depth limit.
- 静态失败原因: The model likely focused on token overlap (low Jaccard) and structural differences (return type, extra loops, method calls), missing the semantic similarity of core data fetching and writing due to partial functionality overlap.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considered these clones because the core functionality of retrieving a web page and saving its content is present in both; the additional logging and recursion are seen as extensions or minor variations.
- 共享行为: Both fetch web page content from a given URL；Both read the content line by line；Both save the content (A optionally to file, B always to file)
- 行为差异: B includes recursive URL extraction and logging, A does not；A returns the HTML string; B returns void；A uses encoding parameter; B ignores charset in stream reader；A uses HttpURLConnection with User-Agent; B uses URLConnection
- 修正建议: Train with more examples of Type-3/Type-4 clones where one function is a superset of the other；Incorporate dataflow analysis to identify core operations (URL open, read, write)；Use models that can learn to ignore peripheral code like logging and recursion

### case_id=1184 FN partial_functionality

- 方法: `copyResource` vs `setImg`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource from a URL or file to a destination file using a byte-by-byte stream copy.
- B 摘要: Opens a file chooser, copies a selected image file to a local images directory if different, and updates the UI with the image.
- 静态失败原因: The low token Jaccard (0.1778) and different method names ('copyResource' vs 'setImg') and high-level purposes mislead static BERT models that rely on lexical similarity and overall context, missing the structural similarity of the inner copying block.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider these clones because the core file copying logic (InputStream/OutputStream loop) is nearly identical and constitutes a significant portion of the functionality, even though the surrounding context differs. This aligns with Type-4 semantic clones where overall behavior partially overlaps.
- 共享行为: Both functions contain a file copying loop that reads bytes from an input stream and writes them to an output stream, closing streams afterwards.
- 行为差异: Function A copies a generic resource (URL or file) to a destination file, while function B copies an image file after user selection.；Function B involves GUI components (JFileChooser, JOptionPane) and image loading, which are absent in A.；Function A throws an exception if resource not found, while B catches exceptions and logs errors.；Function B also updates member variables (bckImg) and sets a path.
- 修正建议: Enhance model to detect structural clones by focusing on shared data-flow patterns (e.g., file copy loop), not just token overlap.；Incorporate dependency graph or AST-based features to isolate common subroutines.

### case_id=1185 FN benchmark_preference_bias

- 方法: `doGet` vs `setup`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Handles HTTP GET request to retrieve and display a page, with access control, logging, and caching.
- B 摘要: Extracts native libraries from a JAR file and adds them to the library path based on OS architecture.
- 静态失败原因: Static BERT/GraphCodeBERT likely failed because of low token overlap (Jaccard 0.106) and completely different domain-specific APIs (servlet vs ZIP extraction), leading to low similarity embedding.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled these as clones based on very broad Type-4 commonalities like performing setup tasks with file I/O and error handling, or due to annotation error in the benchmark.
- 共享行为: Both involve file I/O operations；Both handle exceptions and log messages；Both use conditional logic based on environment properties
- 行为差异: Different primary purpose: page serving vs library extraction；Different control flow: HTTP request processing vs JAR extraction loop；Different data handling: user requests vs binary archive contents；Different output: HTTP response vs library path modification
- 修正建议: Re-verify BCB label for this pair; likely should be non-clone；If retaining, add more explicit shared patterns for models；Use dataflow analysis to capture different semantics

### case_id=1186 FP boilerplate_overlap

- 方法: `main` vs `MotixFileItem`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Main method that parses a Prolog file, generates adapters, and writes them to a JAR file with class loading and bytecode generation.
- B 摘要: Constructor that reads an InputStream, copies its contents, optionally extracts an image, and stores the stream for later use.
- 静态失败原因: The model likely overemphasized the shared I/O boilerplate pattern (try-catch with IOUtils, ByteArrayOutputStream) and possibly similar method names (read, write, copy), ignoring the overall purpose and context.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB annotates as non-clone because the functions have no semantic overlap beyond trivial I/O operations; they belong to completely different application domains (code generation vs file handling).
- 共享行为: Both read from an input source (file vs InputStream)；Both use try-catch-final blocks with IOUtils；Both handle IO exceptions
- 行为差异: A is a static main with command-line arguments; B is an instance constructor.；A performs complex code generation and writes to JAR; B initializes fields for a file item.；A uses multiple libraries (Prolog parser, ASM); B uses commons-io and imaging.；A writes output to files; B stores data in memory.
- 修正建议: Improve model sensitivity to high-level function semantics by incorporating program dependency or dataflow information.；Increase training data variety to avoid overfitting to common I/O patterns.；Use contrastive learning to distinguish between syntactically similar but semantically different functions.

### case_id=1187 FP lexical_or_api_overlap

- 方法: `readTwitterFead` vs `sendPost`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a Twitter feed using Apache HttpClient with a GET request to a hardcoded URL.
- B 摘要: Sends an HTTP POST request with parameters using HttpURLConnection and returns the response.
- 静态失败原因: The static model likely overemphasized the overlapping tokens and control-flow patterns common to HTTP clients, such as 'BufferedReader', 'readLine', 'try-catch', and string building, while missing the critical differences in HTTP method and parameter usage.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this non-clone because the functions have different input parameters, different HTTP methods, different libraries, and different error handling.
- 共享行为: Both perform HTTP requests and read the response line by line into a string buffer.
- 行为差异: Function A uses Apache HttpClient and a hardcoded GET request; function B uses HttpURLConnection and a parameterized POST request.；Error handling differs: A uses Log.e, B uses MsgPrint.showMsg.；Function A returns builder.toString(), function B returns a concatenated result string.
- 修正建议: Incorporate explicit analysis of HTTP method and parameter usage.；Differentiate between different HTTP client libraries.；Consider function signatures.

### case_id=1188 FN benchmark_preference_bias

- 方法: `copy` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Copies a file character by character using FileReader and FileWriter.
- B 摘要: Builds a site for editing by reading XML templates and transforming them for each page, writing multiple output files.
- 静态失败原因: Static BERT did not fail; it correctly predicted non-clone due to low token similarity and clear semantic difference. The failure is in the BCB annotation, which seems incorrect.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled these as clones based on a very broad notion of both functions performing file copying or writing, but this ignores the substantial differences in purpose and complexity.
- 共享行为: Both read from an input file and write to an output file using file I/O streams.
- 行为差异: Function A is a simple character-by-character file copy; function B involves XML parsing, multiple file reads/writes, string transformations, and a loop over pages.；Function A has no parameters or complex logic; function B has 8 parameters and handles exceptions, debugging traces, and file system components.；Function A operates on a single file; function B processes many files and generates web pages.
- 修正建议: Re-annotate this pair as non-clone in the benchmark to reflect true semantic dissimilarity.；Use more stringent criteria for clone labeling, avoiding overly broad partial functionality matches.

### case_id=1189 FN partial_functionality

- 方法: `getResourceAsStream` vs `copyTextFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Retrieves a resource via URL with caching and returns an InputStream to the local cache file.
- B 摘要: Copies the content of a source file to a destination file using buffered streams.
- 静态失败原因: The models rely heavily on token overlap and syntactic similarity; the low Jaccard (0.1869) and different method names/structures overshadowed the shared byte-copying behavior.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often annotates as clone when there is a shared core I/O pattern (buffered read-write loop) despite differing contexts and additional logic.
- 共享行为: Both read data from an input stream and write it to an output stream using buffered streams.
- 行为差异: Function A involves URL connection, HTTP handling, and cache logic; B only handles local files.；Function A returns an InputStream; B returns a boolean.；A uses single-byte read/write; B uses a 1024-byte buffer.；A has extensive error handling with multiple close attempts; B has a simple try-catch.
- 修正建议: Incorporate data flow or control flow graph information to capture the common I/O pattern.；Use contrastive learning to focus on semantic similarity beyond lexical overlap.；Train on diverse clone types with partial functionality similarity.

### case_id=1190 FP boilerplate_overlap

- 方法: `doVersionCheck` vs `getVersion`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Checks for a new version of jEdit by reading a version file from a URL and comparing build numbers, displaying appropriate messages to the user.
- B 摘要: Retrieves the current version string from a remote URL, returning it or null on failure.
- 静态失败原因: The static method may have focused on lexical overlap (URL, BufferedReader, while loop) and missed high-level semantic differences such as side effects, return type, and specific logic. The token Jaccard is low, but the model may have overfitted on common boilerplate patterns.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely considers these non-clones because they have different purposes and outputs; one is a void check with UI, the other is a utility returning a string. Despite similar URL-reading code, their overall functionality is not equivalent.
- 共享行为: Both open a URL connection；Both read lines using BufferedReader；Both extract version information
- 行为差异: A has UI side effects (show/hide cursor, message dialogs); B returns a string.；A reads two fields (.version and .build); B reads the entire last line as version.；A uses jEdit properties and version comparison; B is standalone.；A returns void; B returns String.
- 修正建议: Incorporate training examples that distinguish functions by side effects and return types.；Use data flow analysis to capture differences in outputs and state modifications.；Focus on the core task rather than common IO boilerplate.

### case_id=1191 FP lexical_or_api_overlap

- 方法: `downloadModel` vs `retrieveTemplate`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Downloads an RDF model from a URL with HTTP headers and returns a Model object.
- B 摘要: Retrieves a blog template from a URL by reading lines and caching the result, returns a String.
- 静态失败原因: Static BERT likely overemphasized lexical and API overlap (URL, InputStream, IOException) and the control flow structure, ignoring the semantic purpose and return types.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels as non-clone because the high-level functionality differs significantly (downloading a model vs retrieving a template) and the data processing is distinct, despite sharing a URL reading pattern.
- 共享行为: Both open a URL connection and read from an input stream
- 行为差异: A sets HTTP Accept headers, B does not；A reads RDF/XML using Model.read(), B reads lines with BufferedReader；A returns a Model, B returns a String；B caches the result, A does not
- 修正建议: Include semantic context like return type and method name；Consider task-specific data flow differences (RDF vs text line reading)

### case_id=1192 FP lexical_or_api_overlap

- 方法: `handleHandshake` vs `createDialogArea`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Validates a handshake packet by checking username format and performing server-side session verification via HTTP.
- B 摘要: Creates a dialog area for a license agreement, displaying HTML or text content from a bundled resource.
- 静态失败原因: The model likely relied on lexical overlap of common patterns like 'BufferedReader', 'InputStreamReader', 'URL', 'try-catch', and 'finally', which are present in both functions but used in completely different contexts. This led to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels this as non-clone because the functions have completely different purposes and functionality, despite sharing some common API usage patterns. The token Jaccard is low (0.132), indicating low lexical similarity.
- 共享行为: Both use BufferedReader and InputStreamReader to read from a stream.；Both use try-catch for exception handling.；Both close streams in a finally block.
- 行为差异: Function A performs network handshake validation; Function B creates a UI dialog.；Function A uses URL to connect to an external server; Function B reads from a local bundle resource.；Function A sends packets over network; Function B displays content in a browser or text widget.；Function A parses a hex string and checks for 'ok' response; Function B reads a license file and sets text in UI.
- 修正建议: Incorporate structural or dataflow analysis to distinguish different use cases of similar APIs.；Improve handling of boilerplate code by weighting unique functional code higher.；Use control flow graphs to capture the overall logic and purpose.

### case_id=1193 FN partial_functionality

- 方法: `createDialogArea` vs `seeURLConnection`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Creates a dialog area with a Browser or Text widget and populates it with a license file read from a plugin resource URL.
- B 摘要: Opens a URL connection to a hardcoded URL and reads the response into a StringBuffer, then logs it.
- 静态失败原因: The static model likely focused on method signatures, return types, and high-level structure (UI vs. non-UI), missing the identical I/O sub-pattern due to low token overlap and different surrounding context.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this as a clone because the core I/O pattern (open URL, BufferedReader, readLine, StringBuffer, close) is identical and constitutes a significant functional fragment, fitting broad Type-3/4 clone definitions.
- 共享行为: Both open a URL and create a BufferedReader from its input stream；Both read lines into a StringBuffer using a while loop；Both close the BufferedReader and handle closing exceptions
- 行为差异: Function A creates UI composites and handles fallback from Browser to Text widget；Function B is void and logs the result instead of displaying it；Function A catches and prints IOException, while B throws Exception；Function A returns a Control, B has no return value
- 修正建议: Use sub-functional clone detection that identifies common I/O patterns；Incorporate data-flow analysis to capture variable usage across the reading loop；Consider method-level embedding that focuses on semantic similarity of code fragments

### case_id=1194 FN partial_functionality

- 方法: `getZipAsFile` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Creates a temporary file from the input stream of a DigitalObject's content and returns the file.
- B 摘要: Downloads a resource from a URL, caches it locally, and returns a FileInputStream to the cached file.
- 静态失败原因: Low token overlap (0.111) and very different API calls, control flow, and data structures. BERT-based models rely on surface similarity and fail to capture abstract functional equivalence.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often considers functions with similar high-level I/O tasks (reading from a source and persisting to a file) as Type-4 clones, even if APIs and details differ.
- 共享行为: Both read data from a source and write it to a local file.
- 行为差异: Input types differ: DigitalObject vs URL string.；Return types differ: File vs InputStream.；B implements caching and HTTP handling; A does not.；A uses random folder; B uses structured cache directory.
- 修正建议: Incorporate dataflow analysis to detect reading-writing patterns.；Use graph-based representations that abstract API specifics.；Train on more diverse I/O patterns to recognize common resource retrieval patterns.

### case_id=1195 FN partial_functionality

- 方法: `runScript` vs `getURLContent`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a script file from a URL based on code base and returns its content as a string, returning 'error!' on exception.
- B 摘要: Fetches content from a given URL and returns it as a string, preserving line breaks, throwing IOException on failure.
- 静态失败原因: Static BERT models likely focused on lexical differences (low Jaccard similarity of 0.186) and structural differences (different I/O classes, exception handling, loop style) leading to a non-clone prediction, missing the abstract functional similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often annotates pairs as clones if they perform the same core task (reading URL content) despite differences in implementation details like encoding or error handling; the functional overlap is high.
- 共享行为: Both fetch content from a URL；Both read data until end of stream；Both return the content as a string
- 行为差异: Exception handling: A returns 'error!', B throws IOException；Encoding: A uses default, B uses specified encoding；Reading method: A reads byte by byte, B reads lines；Resource management: A does not close stream, B closes in finally
- 修正建议: Enhance training with abstract representations focusing on core functionality (e.g., 'read URL content')；Incorporate dataflow analysis to recognize that both functions ultimately read and return text from a URL；Use contrastive learning to emphasize semantic similarity despite syntactic differences

### case_id=1196 FP partial_functionality

- 方法: `readTwitterFead` vs `GetResponse`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a hardcoded Twitter timeline JSON using HttpClient and returns content as string, empty on error.
- B 摘要: Reads a URL's response using HttpURLConnection and returns content as string, null on error.
- 静态失败原因: Static BERT models may overemphasize the common HTTP GET pattern and ignore differences in error handling and API details, leading to false positive.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely labels non-clone due to significant differences in error handling (null vs empty string) and API choice, which affect functional equivalence.
- 共享行为: Both perform HTTP GET request；Check status code 200；Read lines from response stream；Return content string
- 行为差异: A uses Apache HttpClient, B uses HttpURLConnection；A returns empty string on error, B returns null；A logs non-200 status, B silent；A handles ClientProtocolException, B handles MalformedURLException
- 修正建议: Train with more diverse error handling patterns；Incorporate dataflow analysis to distinguish return value semantics

### case_id=1197 FN partial_functionality

- 方法: `readData` vs `parse`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Reads comma-separated string fields and a configuration file to populate sets and maps for Tibetan/Sanskrit character processing.
- B 摘要: Parses a delimited data file (CSV-like) with headers and types to create a DataSet object.
- 静态失败原因: Static BERT models rely on surface-level token similarity and structural patterns; the low Jaccard similarity (0.14) and different method names, variable names, and control flow obscure the semantic overlap. The model likely focuses on the distinct lexical items (e.g., StringTokenizer vs StreamTokenizer, HashSet vs DataSet) and fails to infer the common parsing behavior.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB labels these as clones because both functions share the high-level concept of 'reading and parsing input data into structured internal representations', despite differences in input source, tokenization method, and output. This aligns with Type-4 semantic clone criteria accepted in BCB.
- 共享行为: Both parse textual input (strings or files) using tokenization.；Both populate data structures (sets, maps, or DataSet) with parsed values.；Both handle errors and exceptions during parsing.；Both involve loops to process multiple tokens or lines.
- 行为差异: A populates multiple static sets and maps; B returns a DataSet instance.；A uses StringTokenizer on static strings and then reads a file; B uses StreamTokenizer on a file or URL.；A is tailored for Tibetan/Sanskrit data; B handles generic types and scientific notation.；A is void and modifies static state; B is an instance method returning an object.
- 修正建议: Enhance models with high-level semantic representations, e.g., using program embeddings that capture data-flow and goal-level similarities.；Incorporate task-oriented code summarization to compare functional intent rather than low-level tokens.；Use graph-based models that abstract over tokenization patterns and focus on the structure of parsing loops and data population.

### case_id=1198 FN lexical_or_api_overlap

- 方法: `load` vs `register`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.85`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Loads XML content from a pastebin URL and returns it as a string.
- B 摘要: Registers a new user by persisting to database and optionally creating a phpBB forum account via URL call.
- 静态失败原因: Static BERT models often rely on lexical overlap and API sequence; here the shared API (URL, URLConnection, BufferedReader) may have caused false similarity, but the model correctly predicted non-clone due to low token Jaccard (0.19). The error is a false negative for BCB label, meaning the static model missed a BCB-labeled clone.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may have labeled this as clone due to both implementing network I/O with similar boilerplate code (opening URL, reading lines), despite completely different business logic.
- 共享行为: Both use URL, URLConnection, BufferedReader to read from a remote server
- 行为差异: Function A is a simple XML fetcher; Function B is a complex user registration with database persistence and email sending；Function A returns the raw XML; Function B returns a boolean indicating success；Function A uses pastebin URL pattern; Function B uses a configurable forum URL with query parameters
- 修正建议: Incorporate structural and semantic analysis beyond simple API call sequences；Use data-flow analysis to understand different data transformations；Train with more diverse negative examples to reduce over-reliance on boilerplate patterns

### case_id=1199 FN partial_functionality

- 方法: `run` vs `File2String`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a text resource from classpath line by line, appends newlines, and sets the result to a GUI text component, silently catching exceptions.
- B 摘要: Reads a file (or classpath resource) line by line into a string, printing error messages and exiting on failure, then returns the string.
- 静态失败原因: Static BERT models may focus on API token overlap (e.g., BufferedReader, readLine) but are misled by the low Token Jaccard (0.2169) and the presence of unique constructs like SwingUtilities.invokeLater and System.exit, causing a false negative.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels Type-3/Type-4 clones based on similar core functionality (reading text line by line into a string) even when error handling, output, and context differ widely.
- 共享行为: Reads text line by line using BufferedReader and InputStreamReader；Builds a string from the lines read
- 行为差异: A reads only from classpath via context classloader; B tries filesystem first then classpath；A appends "\r\n" after each line; B does not add newlines；A catches all exceptions silently; B handles specific exceptions with output and System.exit；A updates a GUI component via SwingUtilities.invokeLater; B returns the string
- 修正建议: Enhance model to recognize patterns of reading resources line-by-line despite different surrounding context (GUI vs. console).；Use dataflow analysis to understand that both functions eventually produce a string from line reading.

### case_id=1200 FN partial_functionality

- 方法: `PageLoader` vs `read`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.75`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads the entire contents of a URL as text and stores it in a field.
- B 摘要: Reads from a URL or file using an InputStream and returns a status code after processing via another read method.
- 静态失败原因: Low token Jaccard (0.194) and significant structural differences (constructor vs method, different reading patterns, exception handling) caused the model to miss the functional similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label these as clones because both perform the essential task of reading data from a URL (Type-4 functional similarity), and structural differences are acceptable under broad clone types.
- 共享行为: Both open a connection to a URL and read data from it.
- 行为差异: Function A only handles URLs, function B also handles local files.；Function A reads text line by line and concatenates, function B uses InputStream and delegates.；Function A throws exceptions, function B handles them internally and returns a status.；Function A is a constructor, function B is a regular method.
- 修正建议: Use dataflow-aware models that capture the intent of reading from a URL.；Incorporate exception handling patterns into representations.；Use contrastive learning with functional categories to improve semantic understanding.

### case_id=1201 FP lexical_or_api_overlap

- 方法: `sendPost` vs `loadURL`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Sends an HTTP POST request with parameters and returns the response string.
- B 摘要: Loads URL content with optional basic authentication into a temporary file while updating a UI status label.
- 静态失败原因: Static BERT/GraphCodeBERT may have focused on shared API calls (HttpURLConnection, BufferedReader, InputStreamReader) and similar loop structure for reading lines, while missing important differences in output handling, authentication, and side effects. The low token Jaccard (0.17) suggests limited lexical overlap, but the common API patterns might have been enough to trigger a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels clones based on functional similarity. Here, sendPost is a general-purpose POST utility, while loadURL is a specialized URL loader that writes to file and updates UI. Despite both using URL connections, their overall functionality and side effects are distinct, so BCB would likely label them as non-clones.
- 共享行为: Open a URL connection；Read input stream line by line using BufferedReader
- 行为差异: sendPost writes POST data (param) to output stream; loadURL does not write any output.；sendPost returns the response as a String; loadURL writes response to a temporary file and does not return the content.；loadURL handles authentication (Base64 encoding) and updates a JLabel with file size; sendPost does none of these.；Error handling: sendPost catches Exception and shows message; loadURL throws IOException.
- 修正建议: Include method name and return type in the representation to capture intent.；Use dataflow analysis to distinguish between writing to network vs writing to file.；Train on more diverse examples of HTTP-related functions to learn that different output behaviors imply different semantics.；Incorporate side-effect awareness (e.g., UI updates, file creation) into the model.

### case_id=1202 FP lexical_or_api_overlap

- 方法: `populateResources` vs `get`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Loads template files and image resources from the classpath and saves them to a database.
- B 摘要: Makes an HTTP GET request, reads response lines, decodes them into GameRecord objects, and returns an array.
- 静态失败原因: Static BERT/GraphCodeBERT likely overemphasized the lexical overlap of BufferedReader and while loop patterns, and ignored the broader context of method names, parameter lists, and the overall data flow. The shared boilerplate of reading lines from a stream may have misled the model into thinking they are similar.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would likely label these as non-clones because they perform fundamentally different tasks: one is about initializing local resources (templates/images), the other is about fetching remote game records. Even though both involve reading lines, the domain and purpose are completely different.
- 共享行为: Both use BufferedReader to read lines from an input stream；Both handle exceptions with try-catch blocks；Both involve reading data line by line
- 行为差异: Function A reads from local resource files, Function B reads from an HTTP response；Function A saves data to a database, Function B returns an array of objects；Function A processes templates and images, Function B parses game records from lines；Function A uses URL from classpath, Function B uses a URL provided as parameter
- 修正建议: Include method name and more context in the input representation；Add a contrastive learning objective that penalizes high similarity for methods with different parameter signatures and return types；Use data flow analysis to distinguish local resource access from network I/O

### case_id=1203 FN partial_functionality

- 方法: `runInternal` vs `run`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: This method opens an HTTP connection to an OPDS catalog URL, handles pagination, and either downloads a book or parses catalog entries with error handling.
- B 摘要: This method reads a simple configuration from a URL, parsing three fields (version, url, informations), and notifies listeners on completion or error.
- 静态失败原因: Static BERT/GraphCodeBERT models rely heavily on token-level similarity and structural patterns. Here, the token Jaccard is low (0.127), and the code structures differ (loop vs. no loop, different API calls). The model likely missed the semantic similarity in the high-level task of 'fetching and processing URL content', which BCB considers a clone.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels pairs as clones if they share a common high-level purpose (e.g., 'URL reading' or 'network I/O'), even if implementations differ significantly. Both functions fetch content from a URL, parse it, and handle errors, which fits the broad Type-3/Type-4 clone definition.
- 共享行为: Both open a URL connection and read data from it；Both handle exceptions (IOException)；Both are runnable tasks that fetch content from a network URL
- 行为差异: A handles HTTP-specific features (redirects, headers, content-type) and OPDS catalog pagination, while B uses simple URL.openStream() and reads line by line；A can download files or parse complex XML/Atom, while B only reads plain text configuration；A has a loop for pagination, B is a single-pass read；A uses callback and progress display, B uses ActionListener notification
- 修正建议: Incorporate semantic similarity measures that capture high-level intent (e.g., using docstrings or function names)；Use data augmentation with partially similar functions to teach models about Type-4 clones；Consider adding a pre-classification step that groups functions by broader I/O or network operations

### case_id=1204 FN lexical_or_api_overlap

- 方法: `getHTML` vs `run`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches HTML from a given URL with custom encoding and optionally writes it to a file, returning the content.
- B 摘要: Reads and discards content from a fixed local URL, performing no further action.
- 静态失败原因: The low token Jaccard similarity (0.215) and different method signatures (name, parameters) led the static model to focus on surface-level differences, missing the underlying semantic similarity of web fetching. The model could not infer that reading from a URL is a common behavior despite structural disparities.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely considers this as a clone because both functions perform the core task of retrieving HTML content from a URL via HTTP, which is the main semantic goal. The differences in parameters, output, and error handling are treated as minor variations, and one function is a subset of the other's functionality.
- 共享行为: Open an HTTP connection to a URL；Read lines from the response using BufferedReader
- 行为差异: A uses HttpURLConnection with custom headers and encoding; B uses URL.openStream()；A has optional file output; B has none；A returns the fetched HTML string; B is void and discards data；A handles exceptions by printing stack trace and disconnects connection; B catches exceptions silently
- 修正建议: Train models to better recognize API usage patterns and data flow (e.g., URL opening and stream reading) as key indicators of functional similarity.；Integrate graph-based representations of code that capture data dependencies and control flow to identify shared behavior beyond token overlap.；Use contrastive learning to distinguish between functionally similar but lexically different code.

### case_id=1205 FN benchmark_preference_bias

- 方法: `addToArchive` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Adds an input stream as a new entry to a zip archive output stream associated with a pod.
- B 摘要: Retrieves a resource by name from a URL, caches it to a local file, and returns a file input stream, with conditional HTTP caching.
- 静态失败原因: Static BERT models often rely on token-level patterns; here token Jaccard is very low, so it correctly identified non-clone. The failure is from BCB's perspective, where the model disagreed with a possibly overbroad annotation.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may label this as a clone due to broad overlap in I/O stream manipulation and possible partial functionality similarity in handling resources, despite differing high-level tasks.
- 共享行为: Both involve reading from an InputStream and writing to an OutputStream.；Both perform file I/O operations (ZipOutputStream vs FileOutputStream).
- 行为差异: Function A writes directly to a zip archive stream; Function B conditionally downloads and caches from a URL.；Function A returns a URL; Function B returns an InputStream.；Function B has extensive caching logic and HTTP handling, absent in A.；Function A is synchronous and simple; Function B has complex error handling and resource management.
- 修正建议: Incorporate task-level semantics through data flow analysis.；Use graph-based representations capturing control and data dependencies beyond surface tokens.；Train on finer-grained clone labels that distinguish partial functionality from full semantic equivalence.

### case_id=1206 FP boilerplate_overlap

- 方法: `get` vs `handler`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches game records from an HTTP endpoint by setting query parameters and reading lines, parsing each line into GameRecord objects and returning an array.
- B 摘要: Handler that reads a URL page, extracts substrings based on target patterns, and updates a map with the extracted values.
- 静态失败原因: The static model may have overemphasized the structural similarity of having a try-catch block with URL opening and line reading, leading to false positive due to boilerplate overlap.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the functions have entirely different purposes and logic, despite sharing the pattern of reading from a URL.
- 共享行为: Both open a URL connection and read lines from an input stream using BufferedReader；Both handle IOException
- 行为差异: Function A explicitly sets HTTP method, headers, checks response code; B does not；Function A parses lines into GameRecord objects; B extracts substrings using indexOf and updates a map；Function A returns an array or null; B modifies input map and returns void；Function A prints error messages; B catches exceptions silently
- 修正建议: Include more structural features to differentiate processing logic (e.g., data transformations, output types)；Incorporate data flow analysis to capture how input streams are processed；Leverage type information and method signatures to distinguish different behaviors

### case_id=1207 FN partial_functionality

- 方法: `createHTML` vs `invoke`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Builds an HTML page by reading CSS from a resource and appending content based on a page type (logo or home/dashboard with database queries) and returns the HTML string.
- B 摘要: Sends an HTTP POST request using a service URL, reads the response, deserializes JSON, and returns the result, with retry logic on timeout.
- 静态失败原因: The static BERT/GraphCodeBERT correctly identified the lack of semantic equivalence due to low token overlap (Jaccard 0.097) and different overall control flow (switch vs retry). It likely considered the functions non-clones, which aligns with strict semantic analysis.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB might have labeled them as clones due to the common pattern of reading from a stream line by line, which is a frequent boilerplate operation, but the overall functionality is very different, so this annotation likely reflects a broad interpretation of similarity.
- 共享行为: Both use BufferedReader to read lines from a stream (one from a file, one from an HTTP response) and concatenate them into a string.
- 行为差异: Function A builds HTML using a switch-case with database queries; Function B sends HTTP requests with retries and reflection.；Function A returns a string; Function B returns a deserialized object.；Function A reads from a classpath resource; Function B reads from an HTTP response.；Function B has exception handling with retry logic; Function A logs and catches IOException or SQLException.
- 修正建议: Incorporate higher-level semantic understanding of method purpose, such as using method name and return type context.；Focus on the overall algorithm rather than low-level I/O patterns.；Use type information to differentiate between UI generation and remote invocation.

### case_id=1208 FP lexical_or_api_overlap

- 方法: `getWebByUrl` vs `getFrameworkFactory`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Downloads a web page from a URL and saves it to a file, recursively processing links.
- B 摘要: Reads a service configuration file and instantiates an OSGi FrameworkFactory via reflection.
- 静态失败原因: The model likely over-weighted the shared use of URL, BufferedReader, and InputStream, treating them as indicators of semantic similarity, while ignoring the distinct high-level tasks (file download vs. service loading).
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled non-clone because the overall intent differs completely despite sharing common Java I/O patterns; BCB prioritizes functional similarity over structural overlap.
- 共享行为: Both open a URL and read from it using BufferedReader and InputStream；Both perform string trimming and length checks on read lines；Both handle exceptions (though differently)
- 行为差异: A saves web content to a file while B returns a reflective object；A recursively calls another method based on depth, B does not；A uses PrintWriter for output, B uses class loading and instantiation；A catches exceptions and logs, B throws exceptions
- 修正建议: Incorporate control flow and data dependency information to distinguish different purposes；Use method name and comment embeddings to capture intent；Apply graph-based models that model semantic roles of variables

### case_id=1209 FN partial_functionality

- 方法: `testNetworkHTTP` vs `getPagina`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Performs multiple hardcoded HTTP GET requests to transmit device data, discarding all responses.
- B 摘要: Fetches and returns the full content of a given URL with authentication.
- 静态失败原因: Static models rely on token overlap and method signature similarity, which are low here; they miss the shared structural pattern of HTTP GET due to differences in URLs, multiple requests, and return types.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels Type-3/4 clones when core functionality (e.g., HTTP GET and line-by-line reading) is shared, even if purpose and details differ.
- 共享行为: Both open an HTTP connection and read response line by line using BufferedReader and InputStreamReader.
- 行为差异: A makes multiple requests with hardcoded URLs; B takes a dynamic URL.；A ignores the response content; B accumulates and returns it.；A does not set authentication; B sets a default authenticator.；A explicitly disconnects in finally; B closes the stream inside try.
- 修正建议: Train on more diverse Type-3 clone examples with partial functionality overlap.；Incorporate data flow or control flow graphs to capture common sequences like URL → openConnection → BufferedReader → readLine.；Use contrastive learning that emphasizes structural similarity over lexical overlap.

### case_id=1210 FP lexical_or_api_overlap

- 方法: `main` vs `downloadFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a Prolog file, parses it, and generates adapter JAR and lookup classes.
- B 摘要: Downloads an S3 object, decrypts and decompresses it, and saves it to a local file.
- 静态失败原因: The model likely overemphasized lexical/structural similarities such as try-catch blocks, file operations (File, FileOutputStream, IOUtils), and exception handling (IOException), ignoring the entirely different algorithmic intent.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely marks as non-clone because the overall functionality and domain are completely different despite some superficial file handling patterns.
- 共享行为: Both perform file I/O operations；Both handle exceptions and clean up resources
- 行为差异: A generates code (adapter generation), B downloads and decrypts data；A uses Prolog parser and class writer, B uses S3 service and crypto streams；A has command-line argument parsing, B has no user interaction
- 修正建议: Increase sensitivity to domain-specific APIs (e.g., PrologParser vs S3Service)；Use graph-based or dataflow representations to capture semantic intent；Enhance training data with diverse file I/O examples that differ in core logic

### case_id=1211 FP dataflow_blindspot

- 方法: `actionPerformed` vs `unJar`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `dynamic_rejection_with_trace`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Handles action commands to configure application settings like Graphviz path and UI preferences.
- B 摘要: Extracts a file from a JAR archive to a specified directory.
- 静态失败原因: Static BERT may have been misled by common vocabulary like 'File' and 'JarFile' (if present in truncated part), or by the shared use of try-catch and file operations, failing to understand the different high-level purposes.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 dataflow_trace_and_outputs。
- BCB 偏好解释: BCB would not consider them clones because they perform entirely different tasks with no semantic overlap.
- 行为差异: Function A is a GUI event handler with multiple branches; function B is a utility for file extraction.；Function A reads and writes preferences; function B reads from a JAR and writes to disk.；Function A has many conditional branches and UI updates; function B has straightforward sequential logic.
- 修正建议: Train on more diverse non-clone pairs with low token overlap.；Use control flow and data flow graphs to capture high-level semantics.；Increase the weight of functional purpose in representation learning.

### case_id=1212 FN partial_functionality

- 方法: `modifyApplicationMessage` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Modifies a key-value pair in a locale-specific properties file, copying from a default English file if the target file does not exist.
- B 摘要: Copies a file from source to destination using NIO channels, creating parent directories if necessary.
- 静态失败原因: Low token overlap and different syntactic structures mislead the static model, which fails to capture the partial functional similarity of file copying.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB annotators may have focused on the file copy sub-operation, considering both as file manipulation utilities with partial semantic similarity, accepting broad Type-4 clone.
- 共享行为: Copy a file from one location to another
- 行为差异: A uses character streams for copy; B uses NIO FileChannel.；A conditionally copies only if target missing; B always copies.；A reads and modifies properties; B does not modify content.；A writes properties file; B writes binary/any file.
- 修正建议: Incorporate dataflow analysis to detect shared sub-tasks.；Train on examples of partial functionality clones.；Use contrastive learning to recognize structural patterns beyond token overlap.

### case_id=1213 FP partial_functionality

- 方法: `readPage` vs `downloadModel`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads HTML content from a URL line by line, optionally skipping lines that start with '#', and returns concatenated string.
- B 摘要: Downloads an RDF model from a URL by setting HTTP headers, reading input stream into a Model object, and returning it.
- 静态失败原因: Static BERT/GraphCodeBERT may have been misled by the common pattern of opening a URL and reading input, overgeneralizing the 'read from URL' intent while ignoring the distinct output types and processing logic.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB annotators likely consider these non-clones because the functionality is different: one returns raw text, the other returns an RDF model with specific content type handling.
- 共享行为: Both open a connection to a URL and read input stream
- 行为差异: Different output types (String vs Model)；Different processing (line-by-line vs model.read)；Different error handling (A throws Exception, B catches and throws RuntimeException)；A has optional comment filtering, B sets HTTP headers
- 修正建议: Incorporate return type information in embeddings；Add attention to data transformation steps (e.g., line filtering vs model parsing)；Train on more diverse examples of URL reading with different purposes

### case_id=1214 FN partial_functionality

- 方法: `runInternal` vs `read`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.5`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Opens an HTTP connection to a URL, downloads and parses an OPDS catalog, handles pagination, and optionally downloads a book.
- B 摘要: Reads a skeleton file from the classpath via URL, splits it into sections by a delimiter, and validates the section count.
- 静态失败原因: The token overlap is extremely low (0.095), and the syntactic structures are vastly different. Static BERT models rely heavily on surface-level similarities, which are absent here. The high-level semantic similarity is too abstract for the model to infer without more explicit patterns.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider these as Type-4 clones because both methods share the high-level goal of reading data from a URL and processing it into a structured form, despite very different low-level implementations.
- 共享行为: Both open a URL to read data from a stream.；Both parse the read content into structured data (OPDS entries vs text sections).；Both check for some condition (response code vs section count) and throw an error or stop.
- 行为差异: Function A uses HTTP network protocol; B uses classpath resource loading.；A handles pagination and multiple requests; B reads a single file once.；A parses XML/OPDS format; B splits on delimiter and validates count.；A has complex error handling and callbacks; B throws exceptions directly.
- 修正建议: Incorporate training data with diverse implementations of common tasks like URL reading and parsing.；Use contrastive learning to encourage representation of functional similarity over lexical similarity.；Integrate global graph structures (e.g., data flow) to capture I/O patterns.

### case_id=1215 FN partial_functionality

- 方法: `copyFile` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: A utility function that copies the contents of a source file to a destination file using a buffer.
- B 摘要: An Eclipse launch method that sets up a project by reading and processing configuration files, generating resource files, and scheduling project installation.
- 静态失败原因: The static model likely relied on lexical overlap, which is low (token Jaccard 0.09), and predicted non-clone. However, BCB's broader clone criteria may have accepted the structural similarity in stream copying operations, leading to a false negative for the model.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled these as clones due to the presence of common stream I/O patterns and exception handling structures, which are typical in code that manipulates files. Under a lenient Type-3/Type-4 definition, partial similarity in data transfer logic could be considered a clone.
- 共享行为: Both perform file I/O operations.；Both read from an input stream and write to an output stream.；Both handle exceptions and close streams properly.
- 行为差异: Function A is a simple file copy with no project or configuration context.；Function B is a complex Eclipse plugin launch involving XML handling, Maven project setup, error logging, and persistence of properties.；Function A does not have any Eclipse-specific dependencies or GUI integration.；Function B truncates in the middle but clearly has a different overall purpose.
- 修正建议: Train models to recognize higher-level semantic patterns beyond lexical similarity, e.g., by using data-flow graphs that capture stream operations.；Incorporate task-specific context (e.g., file I/O vs. project launch) to distinguish partial functionality clones.

### case_id=1216 FN partial_functionality

- 方法: `getResourceAsStream` vs `readAndRewrite`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Retrieves a resource from a URL with caching and file I/O.
- B 摘要: Reads a DICOM file and rewrites it to another file using DICOM-specific APIs.
- 静态失败原因: Static BERT models rely on lexical and structural similarity, which is very low (token Jaccard 0.078). They failed to capture the high-level functional similarity of reading from one source and writing to another, and were misled by different API usage and domains.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider them clones due to both performing read-write operations on files/streams with progress printing, despite different domains. Broad Type-4 similarity (both process input to output) might be considered.
- 共享行为: Both perform file I/O operations (reading and writing)；Both use BufferedInputStream/BufferedOutputStream；Both print progress to console using System.out.println
- 行为差异: Function A handles HTTP connections, caching, and generic resource loading; Function B is specialized for DICOM medical image processing；A returns an InputStream; B is void and writes to an output file；A has caching logic; B does not；A uses URL/URLConnection; B uses DICOM-specific classes
- 修正建议: Incorporate broader functional semantics via code summarization or cross-domain representation；Use a model that focuses on intent rather than implementation details；Improve training with Type-4 examples that share high-level behavior despite different APIs

### case_id=1217 FP boilerplate_overlap

- 方法: `testSimpleQuery` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Tests a JCR query by setting up nodes, executing an XPath query, and verifying results.
- B 摘要: Handles various action commands in a settings dialog, updating preferences and UI components.
- 静态失败原因: The model may have been misled by generic Java boilerplate (e.g., method calls, null checks) or by token frequency of common keywords like 'if', 'return', but the actual semantics are unrelated. Low token overlap suggests the error is due to model's inability to differentiate domain-specific context.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels as non-clone because the functions have no meaningful semantic overlap; they perform entirely different tasks.
- 共享行为: Both are public void methods.
- 行为差异: Different domains: JCR query testing vs UI event handling.；Different control flow: sequential test steps vs conditional dispatcher.；Different I/O: uses InputStream/OutputStream vs file chooser and preferences.
- 修正建议: Improve model's ability to capture task-specific semantics, e.g., by using program flow or data dependency features.；Increase training data diversity to reduce false positives on unrelated methods.

### case_id=1218 FP boilerplate_overlap

- 方法: `main` vs `copyFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: This main method processes a Prolog file to generate Java adapter classes and writes them to a jar file, with debug options.
- B 摘要: This method copies the content of one file to another using NIO file channels.
- 静态失败原因: The static BERT model may have been misled by the presence of common file I/O related tokens and API calls, despite very low Jaccard similarity, or it might have over-generalized from the training data that any two functions with file I/O are similar.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels these as non-clones because they implement completely different high-level functionalities; the file I/O is incidental and not the core purpose.
- 共享行为: Both perform file I/O operations.
- 行为差异: A is a complex main method that parses Prolog, generates code, and writes a jar; B is a simple file copy utility.
- 修正建议: Improve model's ability to ignore boilerplate tokens and focus on higher-level semantics.；Incorporate structural information like control flow or data flow.

### case_id=1219 FN partial_functionality

- 方法: `getFile` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.75`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies XML content, and saves to temp directory.
- B 摘要: Copies a file from source path to destination path, creating directories if needed.
- 静态失败原因: Static BERT models rely on token-level overlap and high-level semantics. The low token Jaccard and different method names ('getFile' vs 'copyFile') caused the model to miss the underlying I/O pattern similarity. The model likely focused on the distinct high-level tasks (download+XML vs copy) rather than the common low-level file copy idiom.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled this as clone due to the shared pattern of copying bytes from a source to a destination file, considering the copy functionality as a subset of getFile's behavior (Type-3/Type-4 partial functionality).
- 共享行为: Both open InputStream and OutputStream to perform file copying；Both close streams after copying；Both use FileInputStream and FileOutputStream
- 行为差异: getFile downloads from a URL and modifies XML, copyFile only copies local file；getFile uses NIO channels (ReadableByteChannel, FileChannel) for zero-copy, copyFile uses traditional read-write loop；copyFile creates parent directories if missing, getFile does not；getFile returns the file path, copyFile is void
- 修正建议: Enhance model with dataflow or structural analysis to recognize common patterns like file copying；Include more training examples of partial functionality clones；Use AST-based features to detect shared control flow structures

### case_id=1220 FN partial_functionality

- 方法: `runInternal` vs `fetchUrl`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Complex HTTP connection handler that downloads books or parses OPDS catalogs with progress reporting and error handling.
- B 摘要: Simple function that fetches the content of a URL as a string by reading lines.
- 静态失败原因: The static BERT model likely relied on token overlap (very low) and structural differences, missing the abstract shared behavior of URL fetching.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB might label this as a Type-4 clone because both functions share the high-level goal of fetching data from a URL via HTTP, even though the implementations differ significantly in complexity and scope.
- 共享行为: Both functions open a URL and read data over HTTP.
- 行为差异: Function A uses full HttpURLConnection with custom headers and timeouts, while B uses URL.openStream() directly.；Function A handles redirects, response codes, content types, and download logic; B only reads text.；Function A includes progress reporting and OPDS catalog parsing; B has none.
- 修正建议: Train models with more abstract semantic representations or data-flow graphs.；Include examples of partial functionality clones where only a sub-part of the code is similar.

### case_id=1221 FN benchmark_preference_bias

- 方法: `doGet` vs `testStandardTee`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Handles HTTP GET request to retrieve and render a portal page, with permission checks and caching.
- B 摘要: Tests that a TeeWriter copies input to two outputs correctly.
- 静态失败原因: Static BERT correctly predicted non-clone, so it did not fail. The failure is in the BCB label being a false positive.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as a clone due to both methods involving writing/output operations (response output vs. TeeWriter), but this is a weak similarity and likely a labeling error.
- 行为差异: Code A is a servlet handler; Code B is a unit test.；Code A involves HTTP request/response, database, page rendering; Code B is a simple I/O test.；Code A has complex control flow and error handling; Code B is straightforward.
- 修正建议: Re-evaluate BCB labeling for this pair; it appears to be an error.

### case_id=1222 FP partial_functionality

- 方法: `sendPost` vs `getRequestContent`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends an HTTP POST request with parameters to a URL and returns the full response body as a string, catching and printing exceptions.
- B 摘要: Makes an HTTP GET request to a URL and returns only the first line of the response body, throwing exceptions.
- 静态失败原因: Static BERT/GraphCodeBERT models rely on token overlap and structural similarities; both functions use similar API calls (URL, HttpURLConnection, BufferedReader) and have similar control flow, leading the model to overlook semantic differences like POST vs GET and reading all lines vs one line.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely labels this as not a clone because the functions perform different HTTP methods and have different response handling; they are only superficially similar in using URL/HttpURLConnection.
- 共享行为: Both create a URL object, open an HttpURLConnection, read from the input stream, and return a string extracted from the response.
- 行为差异: Function A uses POST method and sends parameters; function B uses GET method and sends no parameters.；Function A reads all lines of the response; function B reads only the first line.；Function A catches exceptions and prints them; function B throws exceptions.
- 修正建议: Improve model's understanding of HTTP method semantics (e.g., presence of doOutput/write indicates POST).；Incorporate deeper semantic analysis of I/O behavior, not just API call sequence.；Use contrastive learning to better discriminate similar-looking but semantically different functions.

### case_id=1223 FN partial_functionality

- 方法: `getFile` vs `getProjectTreeData`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a given URL, optionally modifies its 'wsdlsoap:address' location attribute, saves it to a temporary directory, and returns the file path.
- B 摘要: Downloads an XML file containing project tree data from a URL, saves it locally, parses it to extract project IDs and parent IDs into a 2D string array, and returns that array.
- 静态失败原因: The static BERT/GraphCodeBERT model likely failed due to low token overlap (Jaccard 0.162), different method names and return types, and distinct control flow after the download step, causing it to miss the underlying common semantic pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB's annotation guidelines accept broad functional similarity (Type-3/Type-4), so both methods are considered clones because they share the high-level pattern of 'download XML from URL, parse, and handle errors' despite different application-specific details.
- 共享行为: Both involve downloading a file from a URL using java.net.URL and saving it to a local file.；Both parse XML content (using DOM or similar) after downloading.；Both handle exceptions such as MalformedURLException, IOException, and ParserConfigurationException.；Both write to a temporary file and then read it back for processing.
- 行为差异: getFile returns a String (file path) while getProjectTreeData returns a 2D String array.；getFile modifies the downloaded XML (changes an attribute) before saving; getProjectTreeData only reads existing elements.；getFile uses logging (mLog) whereas getProjectTreeData uses System.out for error output.；The specific XML tags and structure processed are different (wsdlsoap:address vs. proj, pid, ppid, p).
- 修正建议: Enhance model with dataflow analysis to capture shared I/O and XML processing sequences.；Include type information for parameters and return values to recognize structural patterns.；Use contrastive learning on pairs with high-level functional similarity but surface differences.；Incorporate intermediate representations like program dependence graphs to abstract away local variable names.

### case_id=1224 FN partial_functionality

- 方法: `read` vs `invoke`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads data from a local file or URL and returns a status code.
- B 摘要: Invokes a remote HTTP service, processes JSON response, handles retries on timeout, and returns the deserialized object.
- 静态失败原因: The static BERT/GraphCodeBERT model likely relied on lexical and syntactic features (low token Jaccard) and saw very different APIs (FileInputStream vs. HttpClient) and control flow, missing the abstract semantic similarity of data retrieval operations.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider these clones as broad Type-4 (semantic) clones because both implement the high-level concept of 'retrieve data from a source' with similar I/O and error handling patterns, despite different low-level implementations.
- 共享行为: Both perform I/O operations to retrieve data from an external source.；Both handle exceptions (I/O or timeout) and return a result.；Both involve reading data (one from file/URL stream, the other from HTTP response).
- 行为差异: Function A reads from local file or URL directly; Function B makes an HTTP POST request.；Function A returns an int status (success/error); Function B returns an Object (deserialized result or null).；Function B includes retry logic and service discovery; Function A has no retry.；Function A delegates to another read() method after opening stream; Function B processes response inline.
- 修正建议: Enhance model with data flow analysis to identify I/O operations and resource access patterns.；Use contrastive learning to learn higher-level functional similarity beyond lexical overlap.；Incorporate structural information about exception handling and resource management.

### case_id=1225 FP lexical_or_api_overlap

- 方法: `readPage` vs `SRWGuiClient`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a web page content as a string, with an option to skip lines starting with '#'.
- B 摘要: Constructor for a GUI browser that fetches an XML URL, applies XSLT transformation, and displays the result.
- 静态失败原因: The model likely overemphasized lexical overlap (BufferedReader, URL, openStream, readLine) and ignored high-level functional disparity. It may have been misled by the presence of similar API calls in both functions.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would not label these as clones because the overall functionality is vastly different: one is a simple HTML fetcher, the other is a GUI browser constructor with XML processing. The token Jaccard similarity is low (0.12), and BCB annotators would consider the high-level purpose more than shared I/O patterns.
- 共享行为: Both open a URL and read lines using BufferedReader.
- 行为差异: Function A returns a String; Function B sets up a GUI and does not return a value.；Function A may filter out comment lines; Function B processes XML and XSLT.；Function B involves GUI creation and event handling, which A lacks.；Function B handles complex XML parsing and transformation, while A simply concatenates lines.
- 修正建议: Incorporate more structural or semantic features to distinguish simple I/O utilities from complex GUI constructors.；Use abstracted function purpose classification or program dependency graphs to capture higher-level behavior.

### case_id=1226 FP lexical_or_api_overlap

- 方法: `getLinksFromURLFast` vs `getRequestContent`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches a web page and extracts all hyperlinks and their display texts, returning them as two vectors.
- B 摘要: Fetches a web page and returns the first line of its content as a string.
- 静态失败原因: Overlapping lexical tokens and API calls (URL, openConnection, BufferedReader, InputStreamReader) mislead the model into focusing on the shared structure, while ignoring the divergent post-processing and return types.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely considers the overall functionality different: one is a link extractor, the other a simple content fetcher. Despite shared initial steps, the outputs and purposes diverge, so it's not a clone.
- 共享行为: Both open a URL from a string parameter.；Both create a URL connection and obtain an input stream.；Both use BufferedReader to read from the stream.
- 行为差异: Function A reads the entire page into a buffer and uses regex to extract links and texts, returning a Vector array.；Function B reads only the first line and returns it as a String, then closes the connection.；Function A includes time-check logging, Function B does not.；Function A explicitly parses the URL to get directory and root, Function B does not.
- 修正建议: Incorporate dataflow analysis to track how the input is transformed into the output.；Enhance the model to better differentiate based on return types and method signatures.；Add training examples with functions that share initial steps but differ in later logic.

### case_id=1227 FN partial_functionality

- 方法: `getResourceAsStream` vs `copyJar`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Retrieves a resource by URL, caches it locally, and returns an InputStream, with HTTP handling and caching logic.
- B 摘要: Copies a file from one local path to another using FileChannel.
- 静态失败原因: Low token overlap (0.083) and completely different syntactic structures caused static BERT models to miss the high-level semantic similarity of data transfer.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider these clones under a broad Type-4 semantic interpretation: both methods ultimately transfer data from a source to a local file system, representing a similar high-level operation despite different implementation details.
- 共享行为: Both read from a source and write to a destination；Both use try-catch for exception handling
- 行为差异: Function A works with remote URLs, HTTP, and caching; B works with local files；Function A returns an InputStream; B writes to a file；Function A has complex conditional logic and multiple stream closures; B is straightforward with a finally block；Function A handles HTTP status codes; B does not
- 修正建议: Use data-flow-aware models that capture transfer-of-data semantics；Incorporate structural similarity on control-flow graphs for I/O operations

### case_id=1228 FN partial_functionality

- 方法: `runScript` vs `readReferenceText`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a script from a URL byte by byte and returns the content as a string, returning 'error!' on exception.
- B 摘要: Reads reference text from a URL using UTF-8 encoding line by line and returns the content as a string, throwing NoContentException on failure.
- 静态失败原因: Low lexical overlap (token Jaccard 0.183) and different method names, control structures, and API usage mislead the model into viewing them as unrelated, despite shared high-level purpose.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels Type-3/Type-4 clones based on functional similarity, tolerating differences in I/O handling and error management as long as the core task (reading text from a URL) is the same.
- 共享行为: Both functions read text content from a URL resource and return it as a string.
- 行为差异: Error handling: A returns 'error!' on any exception; B logs and throws NoContentException.；Encoding: A uses default charset (char conversion from bytes); B uses UTF-8.；Reading method: A reads byte-by-byte in a loop; B reads line-by-line using BufferedReader.；A uses BufferedInputStream; B uses InputStreamReader and BufferedReader.
- 修正建议: Enhance training data with more diverse I/O patterns that are semantically similar.；Incorporate data flow or program dependence graphs to capture resource usage and output relations.；Use contrastive learning to focus on functional intent rather than surface form.

### case_id=1229 FN partial_functionality

- 方法: `read` vs `readGeoParserResult`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads camera log lines from a URL, parsing each into a CameraLogRecord, handling parse errors, and sorting the records.
- B 摘要: Queries a geo-parser service by constructing an XML request, reading the XML response, extracting place names and gazetteer IDs, with retries on failure.
- 静态失败原因: Static models like BERT rely heavily on token overlap and surface syntax; the low Jaccard index (0.123) and distinct domain-specific terms (CameraLogRecord vs XML/GeoParser) likely caused the model to miss the shared I/O pattern. Additionally, the complex XML construction in B and the simple line reading in A obscured their behavioral similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this as a clone (Type-4) because both functions follow a common 'fetch from URL and parse' pattern, even though the data formats and details differ. The high-level task of reading external data and transforming it into structured objects might be considered semantically similar.
- 共享行为: Both read data from a URL using BufferedReader and InputStreamReader；Both parse the retrieved content (lines vs XML) and extract structured information；Both handle exceptions (LogParseException vs generic Exception)；Both use logging to report progress and errors
- 行为差异: A inputs a URL and outputs void (adds to list), B inputs string and boolean and returns a collection；A constructs no request, B builds an XML request with custom parameters；A reads line-by-line and parses each line individually, B reads entire response and parses XML DOM；A performs sorting, B does not sort
- 修正建议: Enhance training data with more Type-4 clone examples that share high-level I/O patterns but differ in specific APIs；Incorporate graph-based representations (e.g., AST or dataflow) to capture structural similarities like open-stream-read-parse-close；Use contrastive learning to focus on behavior-level features rather than token overlap；Add features for resource handling patterns (e.g., try-finally closing) and retry logic

### case_id=1230 FN benchmark_preference_bias

- 方法: `createFile` vs `getFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Copies content from a source file to a resource file identified by filename using file resource manager.
- B 摘要: Downloads a WSDL file from a URL, optionally modifies the endpoint, and returns the local file path.
- 静态失败原因: The static BERT model likely failed because it relied on low token overlap and different method signatures, correctly predicting non-clone, but did not account for any potential high-level semantic similarity that BCB might have annotated. The low Jaccard similarity (0.084) supports the model's decision.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may label this as a clone due to both methods involving reading and writing files, but the specific functionality (copy vs download+modify) is distinct and does not meet typical BCB Type-3/4 criteria of similar behavior.
- 共享行为: Both involve file I/O operations, including reading from an input source and writing to a file output.；Both handle exceptions related to I/O or resource management.
- 行为差异: Different input parameters: local file vs URL and string parameters.；Different main operations: copying file content vs downloading, parsing, modifying XML, and renaming.；Different return types: void vs String.；Different error handling: logging vs throwing AxisFault.
- 修正建议: Re-evaluate BCB annotation for this pair; it may be a false positive in the benchmark.；If BCB considers such pairs clones, the model needs to capture broader file I/O contexts beyond token matching.

### case_id=1231 FP lexical_or_api_overlap

- 方法: `sendPost` vs `startScript`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Sends an HTTP POST request with parameters and returns the response body as a string.
- B 摘要: Loads a script from a URL and appends its content to a dialog's script buffer.
- 静态失败原因: Static BERT likely overemphasized the overlapping tokens (BufferedReader, URL, readLine, InputStreamReader) and missed the distinct I/O patterns, method names, error handling, and data flow, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels non-clones when the overlap is only in common boilerplate (reading from URL) but the overall functionality and purpose are different, as in sending POST vs loading a script.
- 共享行为: Open a URL connection and read lines via BufferedReader
- 行为差异: A uses HttpURLConnection with POST settings and sends data via PrintWriter; B uses direct URL.openStream() without sending data；A returns concatenated response string; B appends lines to dialog.script and calls dialog.endScript()；A catches generic Exception and shows message; B catches IOException and exits program
- 修正建议: Incorporate data flow analysis to distinguish POST sending from plain reading；Consider method name and parameter types to capture intent；Include structural differences like presence of PrintWriter and dialog object

### case_id=1232 FP boilerplate_overlap

- 方法: `read` vs `getUser`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads camera log records from a URL, parses each line into CameraLogRecord objects, adds them to a list, and sorts the list.
- B 摘要: Loads a User by login from a DAO; if not found, reads a configuration file from a URL, parses lines to create a User, saves it to the DAO, and returns the User.
- 静态失败原因: Static BERT models can be misled by overlapping I/O-related tokens (BufferedReader, InputStreamReader, url.openStream, readLine, while loop) and structural patterns, overlooking the semantic differences in parsing and purpose.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically treats functions with different input/output signatures and domain logic as non-clones despite sharing generic I/O boilerplate, hence the true label is 0.
- 共享行为: Both open a URL stream and use BufferedReader to read lines；Both parse each line in a loop；Both catch exceptions and log or print errors
- 行为差异: Function A has no return value; Function B returns a User object；Function A takes no parameters; Function B takes a userlogin string；Function A parses into CameraLogRecord; Function B parses into User with StringTokenizer；Function A sorts the records; Function B saves the user to a DAO
- 修正建议: Incorporate method signatures (return type, parameters) as features；Use structural or data-flow analysis to distinguish data usage patterns；Train on datasets that penalize pure boilerplate similarity

### case_id=1233 FN partial_functionality

- 方法: `CopyFile` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Copies a file from source to destination using NIO FileChannel.
- B 摘要: Launches a NexOpen project configuration by processing XML files, setting up properties, and running an install action.
- 静态失败原因: The static model likely failed due to the extreme difference in token sets (low Jaccard) and the long, complex structure of Function B, which obscures the shared file-copying sub-task. The model may not capture the semantic similarity of file I/O operations across vastly different contexts.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB might consider these as clones because both perform file copying operations as part of their functionality, with Function B including a file copy step (reverse engineering file creation). However, the overall purpose and complexity are very different, making the clone label questionable.
- 共享行为: Both involve file I/O operations, including reading and writing files.
- 行为差异: Function A is a straightforward file copy; Function B is a complex launch sequence with multiple steps, error handling, and Eclipse-specific APIs.；Function A operates on two file paths; Function B operates on project resources and configuration attributes.；Function A has no dependencies; Function B depends on Eclipse and NexOpen libraries.
- 修正建议: Train models to recognize common sub-tasks (e.g., file copying) within larger methods.；Use dataflow analysis to identify similar I/O operations.；Incorporate method summarization or semantic role labeling to bridge gaps in granularity.

### case_id=1234 FN benchmark_preference_bias

- 方法: `main` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a URL, unzips it, and writes each entry to a local file.
- B 摘要: Copies a file from a source path to a target path using FileChannel.transferTo.
- 静态失败原因: Static BERT model likely relied on low token overlap and different control flow, missing the broad I/O similarity that BCB may have considered; however, the strict semantics differ, so the model's prediction was actually correct for strict equivalence.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might consider both as file I/O operations that transfer data from input to output, possibly within the same project context, but the functionality difference is significant.
- 共享行为: Both involve reading from a source and writing to a target on the filesystem.
- 行为差异: A downloads from a URL and unzips; B only copies a single file.；A writes multiple entries; B writes one file.；A uses InputStream and ZipInputStream; B uses FileChannel.；A's source is a URL; B's source is a file path.
- 修正建议: Use models that incorporate data flow and control flow graphs.；Include broader project context to detect partial functionality clones.；Fine-tune with BCB-style annotations to capture broad semantic similarity.

### case_id=1235 FN benchmark_preference_bias

- 方法: `doGet` vs `Converter`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Handles HTTP GET request to retrieve, check permissions, and render a page, with file caching and logging.
- B 摘要: Constructor that reads a file in SJIS encoding and writes it to another file in UTF8 encoding.
- 静态失败原因: The static model likely did not fail; it correctly predicted non-clone (0). The low token Jaccard (0.083) and structural differences made it easy to distinguish.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might label this as clone if the annotator focused solely on the file I/O aspect present in both functions, ignoring the vastly different contexts and purposes. The broad Type-4 category could encompass functions that both involve reading and writing data streams, but this seems overly broad and likely a misannotation.
- 共享行为: Both perform file I/O operations (reading/writing files).；Both use try-catch blocks to handle IOException.；Both involve input and output streams.
- 行为差异: A deals with HTTP request/response and server-side page management; B is a standalone file conversion.；A includes complex logic for page lookup, user permission checks, and caching; B is a straightforward encoding conversion.；A writes to a temporary file under certain conditions; B writes directly to a specified output file.；A logs extensively; B only prints an error message.
- 修正建议: Review BCB annotation guidelines to ensure consistency; this pair likely should be labeled non-clone.；Consider using functional abstraction or API call analysis to better capture semantic similarity beyond lexical overlap.；Include more context about the overall method purpose to avoid overemphasizing surface-level I/O similarities.

### case_id=1236 FN lexical_or_api_overlap

- 方法: `copyResource` vs `WebmillDeploy`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource (URL or file) to a destination file using byte-by-byte I/O.
- B 摘要: Processes a JAR file, parses XML configurations, rewrites them, and creates a new WAR file.
- 静态失败原因: Static BERT/GraphCodeBERT may have incorrectly considered these as clones due to lexical overlap of common I/O terms like 'InputStream', 'OutputStream', 'File', 'close', etc., or because both functions have similar control flow of try-finally or reading loops.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may have labeled this as clone due to both functions performing file I/O and having similar structure of reading and writing streams, but the overall functionality is completely different.
- 共享行为: Reads input streams；Writes output streams；Uses file I/O
- 行为差异: copyResource copies a single resource; WebmillDeploy processes multiple entries from a JAR；copyResource has no XML parsing; WebmillDeploy parses and rewrites XML；WebmillDeploy includes complex error handling and cleanup; copyResource is simple；WebmillDeploy is a constructor; copyResource is a private method
- 修正建议: Increase sensitivity to high-level semantics；Better differentiate simple I/O copy from complex processing；Use abstract syntax tree comparison to capture structure；Add training data with contrasting examples

### case_id=1237 FP boilerplate_overlap

- 方法: `main` vs `main`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Generates adapter JAR files from Prolog source code, handling command-line options, parsing, and bytecode generation.
- B 摘要: Copies files from source to multiple targets with optional SVN add/delete operations.
- 静态失败原因: The static BERT model likely overfocused on common lexical elements (e.g., 'main', 'argv', 'File', 'System.out.printf') and similar structural patterns (if-else, try-catch, loops), mistaking boilerplate for semantic equivalence.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would likely label this non-clone because the core functionality is entirely different (Prolog-to-JAR adapter generation vs file synchronization). The shared boilerplate (argument parsing, error handling) is insufficient for Type-3/4 similarity.
- 共享行为: Both are static void main methods that check argument length and print usage information.；Both check file existence and handle file I/O operations.；Both print progress messages and error stack traces.；Both use loops to iterate over collections of files.
- 行为差异: Code A parses Prolog files and generates adapter JARs, while Code B copies files using FileChannel.transferTo.；Code A uses complex libraries (PrologParser, ASM ClassWriter), while Code B uses simple file I/O and SVN commands.；Code A generates output in JAR format, while Code B updates files in place.；Code A has a debug mode toggle, while Code B does not.
- 修正建议: Incorporate data flow analysis to track the actual transformations applied to data.；Use program summarization techniques to capture high-level intent.；Train with more diverse examples to reduce reliance on boilerplate patterns.；Apply API-level abstraction (e.g., categorize operations as 'file copy' vs 'code generation').

### case_id=1238 FP lexical_or_api_overlap

- 方法: `handler` vs `SRWGuiClient`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads URL content, parses lines to extract substrings based on target markers, and updates a map.
- B 摘要: Constructor of a Swing browser that reads URL content, optionally transforms XML using XSLT, and displays HTML in a GUI.
- 静态失败原因: Static BERT/GraphCodeBERT models may over-rely on surface-level API token similarities ('URL', 'BufferedReader', 'InputStream') and miss the distinct program structures and goals.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely considers overall functionality and intent, which differ significantly despite shared URL-reading boilerplate.
- 共享行为: Both read from a URL using BufferedReader and InputStreamReader.
- 行为差异: Function A is a simple data extraction method, while B is a full GUI constructor.；A uses target parameters for parsing logic; B sets up UI components and handles XML transformation.；A updates a map; B displays content in a JEditorPane.；B includes window setup, action listeners, and error handling specific to GUI.
- 修正建议: Incorporate structural analysis like control flow graphs or data flow to differentiate simple parsing from GUI construction.；Use models that capture long-range dependencies and overall program purpose.

### case_id=1239 FN benchmark_preference_bias

- 方法: `getFile` vs `extractImage`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.6`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies its endpoint location, and saves it as a local file.
- B 摘要: Extracts an image from input, optionally applies scaling/transform, and writes to output file.
- 静态失败原因: Static BERT models rely on token overlap and structural similarity; the low Jaccard similarity (0.145) and different vocabularies (WSDL, AxisFault vs Djatoka, BufferedImage) made it unlikely to detect a clone. The model correctly identified as non-clone based on semantics.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have considered both as 'resource processing' functions that follow a common pattern of fetching/reading input, processing, and saving output, with similar error handling and logging. However, the domain (WSDL vs image) and specific operations are completely different, so likely a mislabel.
- 共享行为: Both perform file I/O operations；Both create temporary files；Both handle exceptions with custom exception types；Both use streams for reading/writing
- 行为差异: A downloads over network, B processes local or stdin input；A modifies XML content, B applies image transformations；A returns a file path, B writes to output file directly；A uses DOM parsing, B uses BufferedImage
- 修正建议: Train on a more diverse set of non-clones to avoid over-generalization of I/O patterns；Incorporate domain-specific knowledge to distinguish between unrelated file processing tasks

### case_id=1240 FN partial_functionality

- 方法: `testNetworkHTTP` vs `handler`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.75`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: A test method that performs multiple HTTP GET requests to fixed URLs, sending device identifiers and discarding the response.
- B 摘要: A handler that parses a web page from a given URL, extracts substrings based on configured patterns, and stores results in a map.
- 静态失败原因: Static BERT models (e.g., GraphCodeBERT) rely on token-level similarity and structural patterns. The low token Jaccard (0.22) and different method signatures (parameter differences, hardcoded vs. parameterized URLs) cause the model to miss the abstract network I/O pattern. The model may be distracted by unique string literals and method name differences.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely labels this as a clone because both methods perform an HTTP GET request and read the response, using similar boilerplate code (URL, BufferedReader, while readLine). This is considered a Type-4 semantic clone in BigCloneBench, where the core behavior of network I/O is shared despite differing specific purposes.
- 共享行为: Both open an HTTP connection and read the response line by line using BufferedReader.；Both use a while loop to read until null.；Both handle IOException with empty catch blocks (A logs, B catches without action).
- 行为差异: A sends data via URL parameters; B does not send data but receives and parses response.；A ignores all read lines; B extracts substrings and stores them in a map.；A uses multiple hardcoded URLs; B uses a single URL from parameter.；A uses HttpURLConnection; B uses URL.openStream directly.
- 修正建议: Incorporate data-flow or API call sequence abstractions that capture the 'open URL, read lines' pattern.；Apply normalization of string literals and method names to reduce surface-level differences.；Use graph-based features that include control flow and external API calls, not just token sequences.

### case_id=1241 FP lexical_or_api_overlap

- 方法: `readData` vs `saveFileData`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Initializes multiple character sets and a validation map by parsing comma-separated strings and a configuration file for Tibetan/Sanskrit text processing.
- B 摘要: Copies a file to a destination and overwrites the original with new data, updating image dimensions and deleting associated thumbnails.
- 静态失败原因: The model likely matched on superficial similarities like both having long methods with loops, exception handling, and some reference to 'file' or 'set', despite low token overlap.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB consistently labels these as non-clones because they have completely different purposes and no shared functionality beyond being static methods.
- 共享行为: Both are static methods.；Both handle some form of data processing (file I/O vs. string parsing).
- 行为差异: Function A parses string tokens into sets and maps; Function B performs file copy and overwrite operations.；Function A uses StringTokenizer and HashSet; Function B uses FileChannel and file I/O.；Function A deals with character classification; Function B deals with file versioning and thumbnails.；Function A reads configuration data; Function B writes and manages file content.
- 修正建议: Increase sensitivity to method purpose and high-level behavior via dataflow analysis.；Train on more diverse negative pairs with low token similarity but different semantics.；Use graph-based representations to capture structural differences.

### case_id=1242 FN partial_functionality

- 方法: `main` vs `createTar`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Extracts all entries from a KMZ (ZIP) file from a URL to the current directory.
- B 摘要: Creates a tar archive from all files in a given directory.
- 静态失败原因: Static BERT-like models rely on token-level overlap and API call similarity. The low Jaccard similarity (0.124) and completely different library APIs (ZipInputStream vs TarOutputStream) lead the model to treat them as distinct, missing the higher-level conceptual similarity that BCB may have considered.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled this as a clone under a broad Type-4 (similar functionality) interpretation, considering both as 'archive manipulation' tasks that involve reading/writing file entries with buffered streams, despite the opposite directions (extract vs. create).
- 共享行为: Both use buffered I/O to read and write byte arrays.；Both iterate over a collection of file entries (ZIP entries or directory files).；Both write data to an output stream in chunks.
- 行为差异: Function A downloads and extracts a ZIP file; Function B creates a TAR file from local files.；Function A uses ZipInputStream; Function B uses TarOutputStream.；Function A writes to individual files; Function B writes to a single archive file.；Function B includes extensive null/condition checking and logging; Function A has none.
- 修正建议: Incorporate data-flow analysis to recognize common I/O patterns.；Use dynamic analysis or execution traces to detect behavioral symmetry.；Consider abstract syntax tree (AST) or graph-based representations to capture structural similarities in loop and stream operations.

### case_id=1243 FP lexical_or_api_overlap

- 方法: `doRequest` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Serves a static resource from an HTTP request by resolving an internal path and copying its input stream to the response output stream.
- B 摘要: Handles GUI action events by updating application settings based on the action command and showing dialogs for file selection and preferences.
- 静态失败原因: A static BERT or GraphCodeBERT model might have misclassified this pair as clones due to overlapping tokens like 'if', 'String', 'return', and 'null' as well as similar syntactic patterns (e.g., conditionals, assignments, and method calls). The model may have relied on surface-level lexical similarity or boilerplate code patterns without understanding the distinct domain-specific APIs and overall functionality.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would label this as non-clone because the two functions have entirely different purposes and domain contexts, despite some superficial structural similarities. The semantic equivalence is low, and the functions implement different functionalities in different environments.
- 共享行为: Both functions contain conditional checks and assignments to variables.；Both functions involve reading some input (HTTP request path / GUI action command) and producing some output (HTTP response / GUI updates).；Both functions use standard Java constructs like if-else and try-catch.
- 行为差异: Function A operates in a servlet/HTTP context, while Function B operates in a desktop GUI context.；Function A deals with file I/O and MIME types, while Function B deals with application preferences and UI components.；Function A has a simple control flow with a single path, while Function B has multiple conditional branches handling different action commands.；Function A returns a boolean, while Function B is void and does not return a value.
- 修正建议: Enhance the model to incorporate program dependency graphs (PDG) or data flow analysis to capture semantic roles of variables and method calls.；Include API-level features that distinguish between different frameworks (e.g., javax.servlet vs javax.swing).；Use attention mechanisms that can differentiate between core logic and boilerplate code.

### case_id=1244 FN partial_functionality

- 方法: `getFile` vs `internalCopy`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, optionally modifies XML endpoint addresses, saves to temp directory, and returns the file path.
- B 摘要: Copies a file from source to destination using buffered streams, skipping files named 'Thumbs.db'.
- 静态失败原因: Static BERT models rely on token embeddings and lexical similarity, which is low (Jaccard 0.132). They fail to capture high-level functional similarity due to differing API calls and control flow. The model likely focuses on distinct operations (network vs local, XML parsing) and misses the shared abstract file copy behavior.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may accept this as a Type-4 clone because both implement a core file copy pattern (reading from a source and writing to a file). The additional functionality in A (download, XML processing) is considered an extension, and the underlying behavior overlaps enough to be considered similar under broad functional similarity.
- 共享行为: Both involve reading from an input source and writing to an output file.；Both use file I/O streams (InputStream/OutputStream) and handle exceptions.
- 行为差异: A involves network download and XML parsing; B is a simple local file copy.；A has conditional logic based on file existence and length; B skips only on filename.；A returns a String file path; B returns void.；A handles multiple specific exception types; B throws generic FileNotFoundException and IOException.
- 修正建议: Incorporate data-flow analysis to detect core I/O patterns.；Abstract functions by input-output behavior (e.g., source-to-target copy).；Use type information to recognize similar stream usage.；Train on more Type-4 clones with partial functional overlap.

### case_id=1245 FN partial_functionality

- 方法: `getContent` vs `readGeoParserResult`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Executes an HTTP request and returns the response body as a string.
- B 摘要: Sends an XML query to a geo-parsing service, parses the XML response, and returns a collection of place names and gazetteer IDs.
- 静态失败原因: Static BERT/GraphCodeBERT relies on token and structural overlap, which is low (Jaccard 0.14). The methods have different names, different control flow, and different post-processing, so the model likely focused on the local differences and missed the high-level commonality of HTTP response reading.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels pairs as clones if they share a core functional pattern, such as 'read HTTP response line by line and accumulate into a string', even if the surrounding logic and output types differ. This pair fits that broad Type-4 similarity.
- 共享行为: Both methods read from an HTTP response stream line by line.；Both use BufferedReader and StringBuffer to accumulate the response text.；Both handle exceptions, though in different ways (throws vs. try-catch with retry).；Both involve network I/O to fetch data from a remote source.
- 行为差异: Function A returns the raw response string; Function B returns a structured collection after XML parsing.；Function B includes retry logic (up to 3 attempts) and a testing mode early exit.；Function B constructs an XML request dynamically based on input parameters.；Function A uses HttpClient; Function B uses URL.openStream.
- 修正建议: Incorporate control-flow and data-flow analysis to capture functional similarity beyond token overlap.；Use graph-based models that abstract I/O operations and highlight shared patterns like 'read stream line by line'.；Train on broader clone categories that include similar functional behavior despite different data processing steps.

### case_id=1246 FP lexical_or_api_overlap

- 方法: `encryptPassword` vs `perform`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Encrypts a password using SHA-1 and returns hexadecimal string.
- B 摘要: Handles a web request for concept classification, including session validation, parameter extraction, XML building, HTTP POST, and parsing results.
- 静态失败原因: Static model likely focused on surface-level similarities like exception handling, StringBuffer usage, and loops, ignoring domain-specific APIs and overall control flow.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clone because functions have no semantic overlap; encryptPassword is a utility function, perform is a Struts action handler.
- 共享行为: Both use StringBuffer to build strings；Both have try-catch blocks for exception handling
- 行为差异: One performs cryptographic hashing; the other processes HTTP requests and XML；Different method signatures and return types；Different libraries and APIs used
- 修正建议: Train on more diverse examples with similar boilerplate but different semantics；Incorporate finer-grained token embeddings to distinguish API calls；Use program dependency graphs to capture data flow intentions

### case_id=1247 FN benchmark_preference_bias

- 方法: `main` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Decompresses a .gz file from command-line argument by reading from GZIPInputStream and writing to FileOutputStream, with standard resource cleanup.
- B 摘要: Launches a NexOpen Eclipse project configuration by validating and processing Maven POM files, setting Hibernate properties, and managing project resources.
- 静态失败原因: Static BERT/GraphCodeBERT methods rely on token-level embeddings and local dependencies; they correctly identified the low token overlap (Jaccard=0.079) and distinct API usage, leading to a non-clone prediction. However, BCB's label suggests a different similarity standard, so the model's failure is actually a disagreement with the benchmark's annotation rather than a missed true clone.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled these as clones due to superficial structural similarity: both methods have a conditional check, then process files (read/write), and wrap operations in try-catch-finally. The broad Type-4 annotation criteria sometimes accept such high-level structural patterns even when semantics differ greatly.
- 共享行为: Both perform file I/O operations (reading from input streams and writing to output streams).；Both use try-catch-finally blocks for resource management and exception handling.
- 行为差异: Function A is a simple standalone gzip decompressor; Function B is a complex Eclipse framework method with multiple preconditions and configuration steps.；Function A handles only one file format (.gz); Function B handles Maven POMs, Hibernate dialects, and project metadata.；Function A takes command-line args; Function B takes Eclipse launch configuration objects.；Function A has no internal state; Function B interacts with Eclipse workspace and project resources.
- 修正建议: Improve annotation consistency in BCB: avoid labeling structurally similar but semantically unrelated functions as clones.；Use semantic-focused models that better capture task-specific behavior rather than generic IO patterns.；Incorporate explicit control-flow and data-flow analysis to distinguish real program transformations from boilerplate.

### case_id=1248 FN benchmark_preference_bias

- 方法: `split` vs `doGet`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Splits a large FASTA file into multiple smaller files based on size constraints (maxUnitBases, maxUnitEntries) using file channels and FASTA parsing.
- B 摘要: Handles an HTTP GET request to retrieve and display a web page, checking visibility, permissions, and optionally caching the output.
- 静态失败原因: Static BERT (GraphCodeBERT) correctly predicted non-clone (0), disagreeing with the BCB label. The 'failure' reflects benchmark preference bias: the model accurately captured the lack of semantic equivalence, while BCB annotation is likely incorrect.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB likely mislabeled this pair; there is no apparent functional or syntactic similarity to justify a Type-3 or Type-4 clone. Possibly annotation error or superficial pattern matching in control flow or error handling.
- 行为差异: One method performs file splitting and FASTA parsing; the other handles HTTP requests and web page rendering.；Code A involves low-level I/O with ByteBuffer and FileChannel; Code B uses Servlet API and domain-specific page objects.；No overlapping data structures, algorithms, or side effects.
- 修正建议: Re-annotate this pair in BCB as non-clone to correct the false positive.；Improve BCB annotation guidelines to avoid labeling functionally unrelated methods as clones.；Consider using multiple annotators or automated functional clustering for consistency.

### case_id=1249 FN benchmark_preference_bias

- 方法: `ExternalDecoder` vs `doGet`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Constructor that copies an InputStream to a process's stdin in a background thread.
- B 摘要: HTTP GET handler that retrieves a page, checks permissions, renders it, and optionally caches the output.
- 静态失败原因: The static BERT model correctly predicted non-clone due to very low lexical overlap (Jaccard=0.04) and clear domain difference; it disagreed with BCB's likely incorrect label.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as a Type-4 clone based on vague functional similarity (both involve I/O operations), or it could be a labeling error in the dataset.
- 共享行为: Both involve reading input and writing output
- 行为差异: A is for process I/O, B is for web serving；A uses threads and streams, B uses servlet API；A is simple copy, B has complex logic for page lookup, access control, and caching
- 修正建议: Verify BCB labels for this pair; improve clone detection by incorporating domain-specific semantics or functional behavior classification

### case_id=1250 FN lexical_or_api_overlap

- 方法: `getResourceAsStream` vs `descargarArchivo`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a resource from a URL with caching and returns an InputStream.
- B 摘要: Copies a local file from a source path to a destination path using FileChannels.
- 静态失败原因: Static BERT likely relied on token overlap and structural similarity, which are low (Jaccard=0.088). It missed the broad functional category of file copy/download that BCB annotators might have used.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may have considered both as file download/copy utilities, ignoring the differences in source (remote vs local) and caching, focusing on the core I/O pattern.
- 共享行为: Both use FileInputStream and FileOutputStream for file I/O；Both handle exceptions with try-catch blocks
- 行为差异: Function A performs HTTP requests and caching; B does not；Function A returns an InputStream; B is void；Function A writes to a cache file; B writes to a user-specified destination；Function A has complex conditional logic based on cache state; B is straightforward
- 修正建议: Increase sensitivity to functional category matching；Use AST or data flow to capture I/O patterns beyond surface tokens

### case_id=1251 FP lexical_or_api_overlap

- 方法: `run` vs `loadURL`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a fixed URL and discards the response, ignoring errors.
- B 摘要: Authenticates to a URL, reads the response, writes to a temporary file, and updates a status label with progress.
- 静态失败原因: The model was misled by lexical overlap of URL reading patterns and ignored significant differences in data processing and side effects.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels as non-clone because the functions have different overall functionality despite some shared HTTP reading boilerplate.
- 共享行为: Both open a URL connection and read lines via BufferedReader
- 行为差异: Code_a does nothing with read data and has no authentication；Code_b writes data to file and updates UI with progress
- 修正建议: Enhance model to consider data flow and output；Incorporate comparison of I/O operations and side effects

### case_id=1252 FN benchmark_preference_bias

- 方法: `main` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a URL and extracts its zip entries to local files.
- B 摘要: Reads a log file, filters lines by token and line interval, and writes selected lines to a new file.
- 静态失败原因: The static model correctly predicted non-clone based on low token overlap (0.195) and different API usage (ZipInputStream vs BufferedReader). If BCB labels them as clones due to high-level I/O similarity, the model failed to capture that because it focuses on execution semantics rather than coarse task-level similarity.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB annotators may have viewed both as 'utility programs that read input and write output using I/O streams', considering them Type-4 clones despite completely different functionality.
- 共享行为: Both are main methods that read from an input source and write to output files using buffered streams.
- 行为差异: Input source: URL (A) vs local file path (B).；Processing: unzip archive (A) vs line-based text filtering (B).；Output: multiple extracted files (A) vs single filtered file (B).；Error handling: throws Exception (A) vs try-catch (B).
- 修正建议: No fix needed for this pair as static model correctly identifies non-clones. To align with BCB, incorporate coarse task-level similarity via pre-training on diverse tasks or using program summaries.

### case_id=1253 FN partial_functionality

- 方法: `readPage` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a web page from a URL, optionally filtering lines starting with '#', and returns the content as a concatenated string.
- B 摘要: Sends a POST request to a RenRen API with predefined parameters, prints the request URL, and prints the response line by line to stdout.
- 静态失败原因: Static BERT/GraphCodeBERT models rely on lexical and structural similarity; the low token Jaccard (0.14) and different method signatures/control flow led the model to focus on surface differences (POST vs GET, printing vs returning) and miss the underlying semantic similarity of URL reading.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this as a clone because both functions share the core behavior of reading data line-by-line from a URL via HTTP, a common data retrieval pattern. Despite differences in HTTP method, parameter handling, and output, the essential functionality is similar enough for a broad Type-4 clone.
- 共享行为: Both establish an HTTP connection to a URL；Both read the response line by line using a BufferedReader
- 行为差异: Function A uses GET (url.openStream), while Function B uses POST with HttpURLConnection；Function A returns the content as a String, Function B prints to stdout and returns void；Function A has optional comment filtering, Function B builds complex parameters；Function A is a helper method, Function B is the main entry point with command-line arguments
- 修正建议: Augment training data with diverse URL reading patterns across different APIs；Incorporate AST-based features to capture structural I/O patterns；Use contrastive learning to emphasize behavioral similarity over lexical overlap

### case_id=1254 FN benchmark_preference_bias

- 方法: `main` vs `tail`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a URL, unzips it, and writes each entry to a file.
- B 摘要: Implements a tail command for HDFS, reading the last 1024 bytes of a file and optionally following it.
- 静态失败原因: Static BERT methods rely on token overlap and structural similarity; the low Jaccard and distinct functionality led to correct non-clone prediction, but BCB's label may be erroneous in this case.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as a clone due to both methods performing file I/O with buffered streams, which is a very broad Type-4 similarity, but likely a mislabel.
- 共享行为: Both involve reading from a stream and writing to an output.
- 行为差异: Different domain (HTTP vs HDFS)；Different purpose (extract vs tail)；Different structure (unzip vs seek and copy)
- 修正建议: Re-evaluate BCB annotation for this pair; likely should be non-clone.

### case_id=1255 FP lexical_or_api_overlap

- 方法: `getVersion` vs `downloadModel`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Downloads a version string from a fixed URL via HTTP and returns it, returning null on failure.
- B 摘要: Downloads an RDF model from a given URL via HTTP with custom headers, reads it into a Model object, and returns it, throwing RuntimeException on error.
- 静态失败原因: The static BERT method likely over-emphasized the lexical overlap (URLConnection, InputStream, try-catch structure) and API usage similarity, while missing the semantic difference in term of purpose and return type. It may also fail to capture the context that method A is a simple version checker and method B is a model downloader.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BigCloneBench likely labels this as non-clone because the functionalities are fundamentally different: one retrieves a version string, the other downloads a model. Although both involve HTTP connections, the data usage and error handling differ sufficiently to be considered distinct clones.
- 共享行为: Both open a URLConnection to an HTTP URL.；Both obtain an InputStream from the connection.；Both read data from the stream.；Both close the InputStream in a finally block (implicitly via try-with-resources? actually no, they use manual close).
- 行为差异: Return type: String vs Model.；Source URL: fixed string vs parameter.；Error handling: returns null vs throws RuntimeException.；HTTP headers: not set vs set Accept and Accept-Language.
- 修正建议: Incorporate method signatures and return types as features.；Use data flow analysis to trace how the input stream is processed.；Include domain-specific context (e.g., version vs model) from comments or naming.

### case_id=1256 FP lexical_or_api_overlap

- 方法: `getTicketsForQueue` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Retrieves tickets for a queue from a RequestTracker server via HTTP GET and parses ticket IDs.
- B 摘要: Searches Google Images for album art via HTTP GET and extracts image URLs.
- 静态失败原因: The model likely over-relied on the shared use of HTTP GET, BufferedReader, and try-catch patterns, mistaking boilerplate similarity for semantic equivalence.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels non-clones when functions have completely different domains and outputs, despite similar boilerplate code for HTTP communication.
- 共享行为: Both perform HTTP GET requests；Both read and parse HTTP response using BufferedReader
- 行为差异: Function A returns a List<RTTicket>; Function B returns void and populates a global list；Function A is for ticket retrieval; Function B is for image search；Function A uses Apache HttpClient; Function B uses HttpURLConnection；Function A has structured error handling with logging; Function B shows error dialog on exception
- 修正建议: Improve model to distinguish between boilerplate and core logic；Use dataflow or abstract syntax tree to separate API calls from business logic；Fine-tune on more diverse semantic pairs to reduce over-reliance on lexical cues

### case_id=1257 FN boilerplate_overlap

- 方法: `loadDefaultSettings` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.4`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Loads a default config file from classpath and copies it to a specified file.
- B 摘要: Retrieves a resource by name with caching, downloading and returning a file input stream.
- 静态失败原因: Low token overlap (Jaccard 0.097) and differing control flow caused the model to focus on surface-level differences, missing the broad semantic commonality of resource loading.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may consider both as resource loading methods with similar I/O patterns, potentially labeling them as Type-4 semantic clones despite functional differences.
- 共享行为: Both involve reading from a resource；Both handle I/O streams with try-catch
- 行为差异: A writes to a file, B returns an InputStream；A uses classpath, B uses URL (HTTP)；B has caching logic, A does not；Different exception handling styles
- 修正建议: Incorporate high-level resource loading semantics；Use functional alignment to match I/O patterns；Train on more diverse resource-loading examples

### case_id=1258 FP library_context_missing

- 方法: `addQDInformation` vs `getVersion`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `context_recovery_then_dynamic`；动态可解性: `low`；执行优先级: `medium`
- A 摘要: Reads QuickDraw data from a local file or remote URL and updates internal project information objects.
- B 摘要: Fetches a version string from a remote URL and returns it.
- 静态失败原因: The model likely overemphasized the common structural pattern of URL connection and line reading, missing the semantic difference in what is done with the data and the overall goal of each method.
- 静态 case study: 该类错误缺少关键上下文或需要深层语义，纯静态方法不可靠。
- 动态 case study: 动态执行价值较低：样本可能依赖库、框架、网络、GUI、数据库或项目上下文，需要先恢复环境或 mock 依赖。
- BCB 偏好解释: BCB likely labels this non-clone because the high-level functionality and purpose are completely different, despite sharing boilerplate HTTP reading code.
- 共享行为: Both use URL and BufferedReader to read data from HTTP sources；Both handle I/O exceptions by catching them
- 行为差异: addQDInformation modifies multiple internal fields and loops over project info; getVersion simply returns a string；addQDInformation supports both local file and remote URL; getVersion only remote；addQDInformation parses specific line formats; getVersion reads entire response as a single line
- 修正建议: Incorporate method signature and class context information；Train on more examples that share API usage but differ in purpose；Use control-flow and data-flow analysis to distinguish state-modifying vs. simple return methods

### case_id=1259 FP boilerplate_overlap

- 方法: `getDatasetsList` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches a list of dataset names from a server URL with caching, returning the list.
- B 摘要: Searches Google Images for a query, parses image URLs, and updates a UI component with an image.
- 静态失败原因: Static BERT/GraphCodeBERT may be misled by lexical and structural overlap from common Java I/O boilerplate (URL, BufferedReader, readLine) and exception handling, ignoring semantic differences.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels non-clone because the core functionality and domain differ significantly despite sharing common I/O patterns.
- 共享行为: Both open HTTP connections and read data from input streams.；Both handle exceptions (IOException or Exception).
- 行为差异: Different APIs: one accesses a custom server with query parameter, the other accesses Google Images with User-Agent.；Different outputs: A returns a List<String>, B returns void and updates UI.；Different error handling: A throws RuntimeException, B shows error dialog.；A has caching mechanism, B does not.
- 修正建议: Incorporate method names and comments as semantic hints.；Use data flow analysis to distinguish different data transformations.；Train on more diverse examples to avoid over-reliance on token patterns.

### case_id=1260 FN partial_functionality

- 方法: `doVersionCheck` vs `fileDownload`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.75`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Checks for version updates by reading a URL and parsing version strings.
- B 摘要: Downloads a file from a URL to a local directory and saves it as download.pdf.
- 静态失败原因: Static BERT models may focus on token overlap and method names, but the high-level structure of URL reading and BufferedReader usage may not be sufficiently captured due to different method names and different string literals. The models may be biased by surface tokens like 'version-check' vs 'download'.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as URL reading operations with similar structure (open URL, read loop, close), which qualifies as a Type-3/Type-4 clone due to shared functionality pattern.
- 共享行为: Both open a URL and read from its input stream using a BufferedReader.；Both handle exceptions (IOException or general Exception).；Both use a loop to read data line-by-line or character-by-character until end of stream.
- 行为差异: Purpose: A checks version strings, B downloads file content.；Output: A calls another method after parsing, B writes to a file.；UI interaction: A shows/hides wait cursor, B does not.；Exception handling: A catches IOException specifically, B catches Exception broadly.
- 修正建议: Use dataflow-aware models that track the sequence of operations.；Incorporate abstract syntax tree (AST) or control flow graph (CFG) patterns to capture structural clones.；Consider method purpose analysis or semantic role labeling.

### case_id=1261 FN benchmark_preference_bias

- 方法: `addIDs` vs `PageLoader`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.6`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Fetches and parses HTML from a Golm Metabolome Database URL to extract metabolite and chemical IDs, setting them on a PeakListRow and returning a match score.
- B 摘要: Reads the entire content of a web page into a string field.
- 静态失败原因: The static BERT model correctly recognized low lexical similarity (Jaccard=0.105) and different method signatures, but BCB's label 1 suggests a preference for broad functional similarity that the model did not capture.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might have labeled them as clones due to the shared web scraping pattern (opening URL, reading with BufferedReader), considering them Type-3 clones with similar I/O structure and variable manipulation.
- 共享行为: Both open a URL and create a BufferedReader.；Both read lines from the input stream.；Both close the input stream.
- 行为差异: A parses specific HTML patterns to extract metabolite IDs and chemical identifiers, while B simply concatenates all lines.；A performs conditional logic based on link types and sets multiple fields on a PeakListRow object.；A returns an integer (score), while B is a constructor with no return.；A handles exceptions and logs errors; B throws Exception.
- 修正建议: Improve model to consider functional roles beyond token overlap.；Use data-flow or API usage patterns to detect higher-level similarity.

### case_id=1262 FN partial_functionality

- 方法: `getFile` vs `copy`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, optionally modifies the endpoint, and saves it to a local temporary file, returning the file path.
- B 摘要: Copies a file from a source path to a destination path, performing validity checks on both files.
- 静态失败原因: Static pre-trained models like CodeBERT or GraphCodeBERT rely heavily on lexical overlap and structural similarity; the low token Jaccard (0.154) and different API usage (URL vs File) caused the model to miss the deep functional similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considers both as file copying operations, despite different sources and additional logic, because the core behavior (reading input and writing to a file) is similar, fitting a broad Type-4 clone definition.
- 共享行为: Both read data from an input source and write it to an output file.；Both handle file I/O exceptions.；Both close streams after use.；Both perform some file existence or validity checks before copying.
- 行为差异: getFile reads from a URL (network) whereas copy reads from a local file.；getFile modifies XML content during the copy; copy does not.；getFile returns a String (file path), copy returns void.；getFile uses NIO channels; copy uses byte buffer.
- 修正建议: Incorporate dataflow analysis to abstract the source and destination types.；Use library-specific knowledge to recognize that URL.openStream() and FileInputStream both produce input streams.；Train on more diverse clone pairs with low lexical similarity but high functional similarity.

### case_id=1263 FP lexical_or_api_overlap

- 方法: `run` vs `checkForUpgrade`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Makes an HTTP GET request with basic authentication and reads the response line by line, storing it as a string.
- B 摘要: Checks for software upgrades by querying a database, constructing a URL with client info, fetching license/upgrade data from a remote server, parsing the response, and updating UI components.
- 静态失败原因: The model likely overfocused on the shared lexical patterns like URL.openConnection(), BufferedReader, and while loop for reading, ignoring the surrounding context that shows vastly different functionality.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled non-clone because the functions have entirely different purposes and structures; the shared HTTP reading pattern is a generic library usage, not indicative of semantic equivalence.
- 共享行为: Both open an HTTP connection and read the response line by line using BufferedReader.
- 行为差异: function_a only performs a simple HTTP GET with authentication and stores the response.；function_b involves database queries, URL parameter construction, XML parsing, UI updates, and multiple conditional branches.
- 修正建议: Improve model to capture control flow and data dependencies.；Use function-level embeddings that consider method signature and overall structure.；Weigh common utility patterns less.；Increase training data diversity.

### case_id=1264 FP lexical_or_api_overlap

- 方法: `actionPerformed` vs `copyToDir`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Handles various GUI action commands to set preferences like file paths for external tools.
- B 摘要: Copies a file to a specified directory, creating the directory if needed.
- 静态失败原因: The static model likely over-relied on superficial similarities like use of File objects, JFileChooser, exception handling, or common API calls (e.g., FileOutputStream, FileInputStream) and missed the overall semantic difference. It failed to capture that the high-level purpose is completely different.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: None
- 共享行为: none
- 行为差异: Different overall purpose: event handler vs file copy；Function A is long with multiple conditional branches; Function B is a simple sequential process；Function A interacts with GUI components and preferences; Function B operates solely on files；Function A handles many different action commands; Function B has a single focused goal
- 修正建议: Train model to recognize that high-level purpose (event handling vs file copying) outweighs low-level API overlaps.；Use contrastive learning with negative samples that have similar API but different intents.；Incorporate more structural or flow-based features to distinguish event-driven branching from sequential logic.

### case_id=1265 FN benchmark_preference_bias

- 方法: `loadMFileViaWeb` vs `httpRequestByPOST`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Loads a MATLAB function file from a URL and parses it into a UserFunction object.
- B 摘要: Sends an HTTP POST request with parameters and returns the response body as a string, with error handling.
- 静态失败原因: Static BERT/GraphCodeBERT likely focused on the low token overlap (0.18), different method names, return types, and the presence of domain-specific code (FunctionParser vs HttpClient/HttpPost), leading to a non-clone prediction. It failed to recognize the broad boilerplate similarity that BCB considers clone.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might label this as a clone due to the shared pattern of network I/O reading (URL connection, InputStream, BufferedReader, while loop), which is common in Type-3/4 clones where structural similarity outweighs semantic differences.
- 共享行为: Both open a URL/HTTP connection and read lines from an InputStream using BufferedReader.；Both return a result after reading all lines.
- 行为差异: A reads a .m file and parses it as a MATLAB function; B sends POST request with form parameters and returns raw string.；A returns a UserFunction object; B returns a String or null on error.；B handles HTTP status codes and sets error fields; A catches generic Exception and throws a custom exception.；A uses URL.openStream() (implicit GET); B explicitly uses HttpPost.
- 修正建议: Use a hybrid approach that combines lexical similarity with structural or API usage patterns.；Fine-tune on BCB-style labels to capture broad Type-4 clones with similar I/O boilerplate.；Adjust detection threshold to be more lenient for functions with shared network I/O patterns.

### case_id=1266 FN benchmark_preference_bias

- 方法: `write` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Writes entries from a set of JAR files into a single JAR output stream, excluding manifest files and zero-size entries.
- B 摘要: Retrieves a resource by name, caching it locally if necessary, using HTTP conditional GET and file-based caching.
- 静态失败原因: Static BERT correctly predicted non-clone due to low token overlap and different functionality; the failure is due to BCB's loose labeling rather than model error.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might have considered both as I/O utility methods that manage resources, but this is a very loose interpretation and likely a mislabel.
- 共享行为: Both involve reading input streams and writing to output streams；Both handle IOException
- 行为差异: Function A writes to a JarOutputStream; Function B reads from a URL and caches to files；Function A uses IOUtils.copy; Function B uses a manual copy loop with Buffered streams；Function A processes multiple JAR files; Function B handles a single resource with caching logic
- 修正建议: Improve BCB annotation guidelines to exclude such dissimilar functions；Use stricter criteria for Type-4 clones to avoid false positives

### case_id=1267 FN benchmark_preference_bias

- 方法: `copyFile` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Copies a file from source to destination with optional overwrite and buffer size.
- B 摘要: Launches a NexOpen project configuration, handling Maven profiles and Hibernate setup.
- 静态失败原因: The static model correctly predicted non-clone (low token overlap and no structural similarity), so it did not fail. The BCB label appears to be a false positive.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as a clone due to superficial similarity in using I/O streams and exception handling, or due to broad Type-4 criteria that accept partial functionality like data transfer from one source to another.
- 共享行为: Both use InputStream/OutputStream for copying data.；Both include exception handling and logging.
- 行为差异: copyFile is a simple file copy utility; launch orchestrates complex build configuration for a specific framework.；copyFile uses FileInputStream/FileOutputStream; launch handles project resources, DOM parsing, and Properties.；copyFile is static; launch is an instance method with multiple parameters.；copyFile has a loop to read and write in chunks; launch does not perform continuous I/O but uses IOUtils.copy once.
- 修正建议: Reevaluate BCB annotations for pairs with low token similarity and unrelated method names.；Use domain-specific knowledge or method names as additional signal.；Implement hierarchical analysis to distinguish utility functions from configuration workflows.

### case_id=1268 FN partial_functionality

- 方法: `runScript` vs `read`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a script file from a URL byte by byte, concatenates into a string, returns it or 'error!' on exception.
- B 摘要: Reads a skeleton file from classpath, parses lines into sections delimited by '---', validates section count, throws exceptions on errors, stores sections in a list.
- 静态失败原因: Static BERT/GraphCodeBERT likely focused on low token overlap (0.15) and differences in return type, exception handling, and loop structure, failing to recognize the broad I/O similarity that BCB values.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled as clone due to both being file-reading methods that open a URL and read content, focusing on the general I/O functionality rather than specific processing logic.
- 共享行为: Open a URL connection to read a file；Use Java I/O streams；Handle reading in a loop
- 行为差异: A returns concatenated content; B parses into sections and validates；A catches all exceptions; B throws them；A reads bytes; B reads lines with BufferedReader；A returns String; B returns void, modifies internal state
- 修正建议: Incorporate type and signature information；Use models that capture high-level intent, e.g., graph-based with dataflow；Fine-tune with BCB annotation preferences that allow Type-4 clones

### case_id=1269 FN benchmark_preference_bias

- 方法: `callService` vs `runInternal`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Makes a simple HTTP GET request and stores the response string.
- B 摘要: Fetches and processes an OPDS catalog with pagination, download, and GUI updates.
- 静态失败原因: The static model correctly predicted non-clone due to low lexical and structural similarity, so it did not fail; the BCB label is likely erroneous.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB annotators might have considered the core HTTP request/response as the shared functionality, ignoring the vast differences in purpose and complexity.
- 共享行为: Both open a URL connection and read from the input stream.
- 行为差异: Simple synchronous GET vs. complex HTTP handling with redirects, timeouts, content types.；One stores response as a string; the other processes catalog entries, handles pagination, and downloads files.；Error handling is minimal in A; B has extensive error handling and progress reporting.
- 修正建议: Re-annotate this pair as non-clone.；Apply stricter functional equivalence criteria to avoid overly broad cloning.

### case_id=1270 FN benchmark_preference_bias

- 方法: `encodeFileToFile` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Encodes an input file to an output file using Base64 encoding and returns success boolean.
- B 摘要: Downloads a resource from a URL, caches it locally, and returns an InputStream; includes handling of HTTP connections and caching logic.
- 静态失败原因: Static BERT likely failed because it correctly identified the low token overlap (Jaccard 0.224) and different method names, leading to a non-clone prediction. From BCB's perspective, the model failed to recognize the shared boilerplate I/O pattern that BCB considered as clone. However, the model's prediction aligns with semantic analysis.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have considered both functions as Type-4 (semantic) clones because they both involve reading from an input stream and writing to an output stream in a loop, with similar resource management. However, the core functionality (encoding vs. caching) is entirely different, so BCB's label of 1 is questionable.
- 共享行为: Both use InputStream and OutputStream for I/O operations.；Both read bytes in a loop and write to an output stream.；Both have try-catch-finally blocks with resource cleanup.；Both print stack traces on exception.
- 行为差异: Function A performs Base64 encoding; B does not encode.；Function A writes to a file; B returns an InputStream after caching.；Function B involves URL fetching, caching, HTTP headers, and conditional logic; A is straightforward file copy with encoding.；Function A returns boolean; B returns InputStream or null.
- 修正建议: Reconsider BCB labels for pairs with only superficial I/O pattern similarity but different high-level functionality.；Improve data preprocessing to filter out pairs where the shared behavior is only boilerplate.；Incorporate higher-level semantic understanding beyond token sequences.

### case_id=1271 FP long_range_semantics

- 方法: `writeConfiguration` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `static_summary_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Writes a configuration resource to a Writer by copying from a URL input stream, with null handling.
- B 摘要: Handles GUI action events to set user preferences like file paths, dates, look-and-feel, and may restart application.
- 静态失败原因: GraphCodeBERT likely overfitted to common API sequences like 'if (x == null) return' or 'JFileChooser' usage patterns, but missed the higher-level semantic difference due to long-range dependencies and lack of context about the GUI event framework vs. I/O utility.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB marks non-clone because the functions are semantically unrelated: one is a generic I/O utility, the other is a domain-specific GUI event handler with no shared functionality beyond trivial null checks.
- 行为差异: Function A performs a simple I/O copy from URL to Writer; Function B is a complex GUI event handler with multiple condition branches.；Function A has no user interaction; Function B involves file chooser dialogs and updates UI components.；Function A is short and linear; Function B is long with many nested if-blocks and side effects on application state.；Function A's output is a Writer; Function B's output is modifications to system preferences and UI.
- 修正建议: Enhance model with data flow analysis to distinguish I/O streams from GUI events.；Use larger context windows or hierarchical attention for long functions.；Incorporate type information and method signatures (e.g., Writer vs. ActionEvent) as features.

### case_id=1272 FN partial_functionality

- 方法: `copyResource` vs `copyFileTo`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource from a URL or local file to a destination file using byte-by-byte streaming.
- B 摘要: Copies a file to a specified destination using FileChannel transferFrom.
- 静态失败原因: The model focused on lexical and structural differences (different I/O classes, method signatures, logging) and missed the shared high-level behavior due to low token overlap (Jaccard=0.16) and lack of dataflow understanding.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB annotators often consider functions that perform the same high-level operation (copying a file/resource) as clones, even when implementation details differ, as long as the core purpose matches.
- 共享行为: Copy a source to a destination file；Close streams/channels after copying；Handle I/O exceptions
- 行为差异: A supports URL sources; B only local file source；A uses byte-by-byte write loop; B uses channel transfer (more efficient)；A uses InputStream/OutputStream; B uses FileChannel；B includes logging; A does not
- 修正建议: Incorporate dataflow analysis to detect read-from-source and write-to-destination patterns；Use program slicing to extract core copying logic；Augment training data with diverse implementations of common tasks like file copying

### case_id=1273 FP other

- 方法: `main` vs `copyFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Main method that generates adapter JAR files from a Prolog file.
- B 摘要: Utility method that copies a file using FileChannel.
- 静态失败原因: The model may have been misled by superficial similarities such as use of File, try-catch-finally blocks, and IOException, failing to distinguish the vastly different high-level semantics.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely labels these as non-clones because they perform completely different tasks with no functional overlap.
- 行为差异: Function A is a complex code generation pipeline involving parsing, code generation, and multiple IO operations; Function B is a simple file copy.；Function A handles adapter layer generation and serialization; Function B only transfers file content.
- 修正建议: Improve model's ability to capture high-level program intent beyond local patterns.；Incorporate task-specific or domain-specific semantic analysis.

### case_id=1274 FN benchmark_preference_bias

- 方法: `modifyApplicationMessage` vs `copy`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Modifies a properties file for a given locale by updating or adding a key-value pair.
- B 摘要: Copies data from an InputStream to an OutputStream using IOUtils.
- 静态失败原因: The static model correctly predicted non-clone (0); it did not fail from an objective standpoint, but the BCB label is inconsistent.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: Unlikely to be considered a clone under BCB criteria as they implement completely different functionality; the BCB label of 1 may be an annotation error.
- 共享行为: Both perform I/O operations
- 行为差异: Different purposes: properties file modification vs. stream copy；Different input/output types: String locale/messageName vs. InputStream/OutputStream；Different error handling: prints stack trace vs. throws FaultException and logs；Different complexity: multi-step file handling vs. single utility call
- 修正建议: Review and correct benchmark annotations for this pair；Improve annotation guidelines to avoid false positives due to unclear criteria

### case_id=1275 FP lexical_or_api_overlap

- 方法: `readData` vs `copyFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Parses multiple comma-separated strings and populates various sets and hash maps for Tibetan language processing.
- B 摘要: Copies a source file to a destination file using FileChannel.
- 静态失败原因: The static model likely focused on overlapping keywords like 'HashSet', 'StringTokenizer', 'IOException', 'try', 'catch', 'finally', and similar control flow patterns, misleading it to predict a clone despite different semantics.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would not consider these clones because they have completely different purposes and functionality, even under broad Type-3/4 criteria.
- 共享行为: Both use try-catch-finally blocks for exception handling；Both involve reading data (A from global strings, B from source file)；Both use loops (A uses while loops, B uses no explicit loop but relies on transferFrom)
- 行为差异: Function A populates sets and maps for data initialization, while Function B copies a file；Function A uses StringTokenizer and HashSet; Function B uses FileChannel and FileInputStream/OutputStream；Function A's output is side effects on global data structures; Function B's output is a new file at destination
- 修正建议: Improve model's ability to capture long-range dependencies and overall program semantics rather than local patterns；Use data flow and control flow graphs to distinguish different operations；Incorporate more diverse negative examples with similar lexical features but different functionality

### case_id=1276 FN partial_functionality

- 方法: `gerarTutorialPage` vs `modifyApplicationMessage`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Generates a tutorial website by creating directories, copying multiple CSS files, and writing HTML and other page files.
- B 摘要: Modifies a locale-specific properties file, creating it from a default English file if needed, and updates or adds a message key-value pair.
- 静态失败原因: Static BERT models like GraphCodeBERT rely heavily on lexical and syntactic similarity. The low token Jaccard (0.119) and different method signatures led to a non-clone prediction. The model failed to capture the underlying structural similarity in file I/O patterns and exception handling that human annotators might value.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BigCloneBench annotators might consider these as Type-4 clones because both are complex file manipulation routines with similar structural patterns (try-catch, file I/O, resource management) and both serve configuration/setup purposes within a larger system, despite different specific functionalities.
- 共享行为: Both perform file I/O operations including reading and writing files.；Both use try-catch blocks to handle exceptions.；Both close resources (streams, writers) in the normal flow.
- 行为差异: Function A creates directories and copies multiple CSS files; function B only operates on properties files.；Function A writes HTML content; function B reads and modifies key-value pairs in a properties file.；Function A returns a boolean; function B returns void.；Function A uses FileChannel for copying; function B uses Reader/Writer streams.
- 修正建议: Incorporate dataflow analysis to detect common patterns of file operations.；Use structural AST-based features to capture similar control flow and I/O sequences.；Train with more Type-4 clone examples that have low lexical but high structural similarity.

### case_id=1277 FN partial_functionality

- 方法: `read` vs `register`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.4`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a skeleton file from classpath, parses lines into sections separated by '---', validates section count.
- B 摘要: Registers a User object by encoding password, setting properties, creating phpBB forum user via URL, persisting, and sending confirmation email.
- 静态失败原因: Static model likely focused on low token overlap and distinct semantics, missing the partial structural similarity that BCB annotators valued.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider them Type-4 clones due to structural similarity of reading from URL and processing lines, ignoring different contexts.
- 共享行为: Both open a URL and read lines using BufferedReader and InputStreamReader；Both use while loop to read input line by line
- 行为差异: Entirely different purposes: file parsing vs user registration；Different processing of read lines: building sections vs setting forum ID；Different exception handling: throws Exception vs catching IOException；B has many additional operations not present in A
- 修正建议: Improve detection of structural patterns even with low lexical overlap；Consider configurable thresholds for Type-4 clones

### case_id=1278 FN partial_functionality

- 方法: `main` vs `downloadFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a URL, unzips it, and extracts entries to current directory.
- B 摘要: Downloads a file from S3, decrypts and decompresses it, then moves it to a target location.
- 静态失败原因: Low token-level overlap and different API calls (URL vs S3, Zip vs Inflater) cause the model to miss the abstract similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels pairs as clones if they share high-level functionality like downloading and writing files, even if protocols and processing differ.
- 共享行为: Both retrieve a remote file and save it locally.
- 行为差异: A uses HTTP URL, B uses S3 with custom cipher and inflater.；A unzips archive entries, B handles a single file with decryption.；A is a main method, B is a private helper with exception handling.
- 修正建议: Use data-flow or control-flow graph similarity.；Incorporate API purpose embeddings or abstract operations.

### case_id=1279 FN partial_functionality

- 方法: `modifyApplicationMessage` vs `convert`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.2`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Modifies a properties file for i18n by replacing or adding a key-value pair for a given locale.
- B 摘要: Converts an ACRNEMA format file to DICOM by adding UIDs and optionally inflating pixel data.
- 静态失败原因: The model relied on lexical and structural overlap, which is very low (token Jaccard 0.1279). It did not recognize the abstract file transformation pattern that BCB might have considered.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB might consider both as 'file transformation' operations with similar high-level structure (read, process, write), which could be seen as a Type-4 clone (semantic similarity despite different domains).
- 共享行为: Both read from a file, process data (lines or bytes), and write to another file.；Both use try-catch or try-finally for resource handling.
- 行为差异: One processes text properties files; the other processes binary medical image data.；One modifies existing key-value pairs; the other transforms file format and adds metadata.；One uses Java Properties and Buffered stream for text; the other uses DICOM-specific parsing and pixel manipulation.
- 修正建议: Incorporate method-level semantic embeddings from documentation or comments.；Use task-level classification (e.g., 'file modification' vs 'file conversion') to identify abstract similarities.

### case_id=1280 FP boilerplate_overlap

- 方法: `hash` vs `perform`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.85`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Performs repeated hashing of content with salt using MessageDigest.
- B 摘要: Processes an HTTP request to classify a concept and returns an ActionForward.
- 静态失败原因: The static BERT model likely relied on surface-level token overlap (e.g., common keywords like 'return', 'null', 'String', 'if', 'for') or structural patterns like loops and conditionals, ignoring the completely different API usage and domain semantics. The long code B may have overwhelmed the model's attention, causing it to generalize poorly.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labeling is 0 because these two functions have no functional overlap; one is a utility hash method and the other is a Struts action handler. BCB typically requires at least partial functional similarity for a positive label.
- 行为差异: Function A performs cryptographic hashing, whereas function B processes a web request.；Function A is purely computational with no side effects; function B interacts with session, HTTP connections, and I/O.；Function A returns a byte array; function B returns an ActionForward object.；Function A handles exceptions via throws; function B catches exceptions and sets error status.
- 修正建议: Incorporate data-flow or control-flow features to capture actual semantics.；Use type information or API call sequences to distinguish domains.；Train with contrastive learning to reduce sensitivity to boilerplate tokens.；Consider hierarchical or graph-based models for long-range semantics.

### case_id=1281 FP lexical_or_api_overlap

- 方法: `SRWGuiClient` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Constructor for a Swing browser that loads a URL, optionally transforms XML with XSLT, and displays the resulting HTML.
- B 摘要: Method that fetches Google Images search results, parses image URLs, and updates a GUI with the first image.
- 静态失败原因: The model likely overemphasized the overlapping API calls (URL, BufferedReader, reading lines) and ignored the distinct high-level functionality, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would not label as clone because the functions perform entirely different tasks, despite sharing some low-level API usage.
- 共享行为: Both use URL and BufferedReader to read from a URL；Both involve GUI components (Swing)；Both handle exceptions
- 行为差异: Function A builds a browser GUI and processes XML/XSLT; Function B scrapes image search results and updates album art；Different URL construction and response parsing；Different error handling (warnUser vs showErrorDialog)
- 修正建议: Incorporate task-level semantics or control flow analysis；Use data flow to differentiate reading vs parsing vs GUI setup

### case_id=1282 FP lexical_or_api_overlap

- 方法: `readPage` vs `readScalarpvviewerDocument`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a web page from a URL, optionally ignoring lines starting with '#', and returns the content as a string.
- B 摘要: Reads a specific XML configuration file from a URL, filters lines starting with '%', parses the XML, and sets up a GUI viewer with various parameters.
- 静态失败原因: Static BERT models may have over-relied on lexical overlap of common Java I/O patterns (e.g., 'BufferedReader', 'InputStreamReader', 'readLine', 'url.openStream()') and the structural similarity of the while loop, ignoring the significant semantic differences in data processing and side effects.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled this pair as non-clone because the functions serve very different purposes and have distinct outputs; the shared I/O pattern is a common boilerplate that BCB typically excludes from clone annotations.
- 共享行为: Both read from a URL using BufferedReader and InputStreamReader；Both iterate through lines, filtering out lines starting with a special character ('#' or '%') and concatenating valid lines；Both close the reader after processing
- 行为差异: Function A ignores a single comment character '#', while Function B ignores '%' but uses '%=%' as a stop marker；Function A has an optional comment filtering mode (ignoreComments parameter), Function B always filters；Function A trivially concatenates lines into a string, Function B performs extensive XML parsing and GUI configuration；Function A returns a string, Function B returns void and updates UI components
- 修正建议: Incorporate dataflow analysis to track how the read data is used after collection；Use models that focus on method signatures and return types to distinguish final outputs；Add contrastive training examples that differ only in the post-processing logic

### case_id=1283 FN partial_functionality

- 方法: `read` vs `run`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.75`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads from a file or URL by name, returns status code indicating success or error.
- B 摘要: Connects to a fixed URL and reads all lines discarding them, returns void.
- 静态失败原因: Low token overlap (0.238) and different method signatures led the model to focus on syntactic differences, missing the underlying similar I/O pattern of URL reading and input consumption.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as functions that open a network resource and read from it, a common pattern for fetching data, treating parameterization and return type differences as minor in Type-4 clones.
- 共享行为: Open a URL connection and read from it；Catch IOException；Ignore or discard read content
- 行为差异: A takes a String parameter for resource name; B uses a hardcoded URL；A returns int status; B returns void；A handles file input; B only handles URL；A catches IOException and sets status; B catches MalformedURLException and IOException silently
- 修正建议: Use context-aware models that can capture semantic patterns like URL reading；Incorporate data flow and control flow analysis to match I/O operations；Enrich training data with more Type-4 clone examples

### case_id=1284 FN lexical_or_api_overlap

- 方法: `doTransfer` vs `getDatasetsList`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.3`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Forwards an incoming HTTP request to a target URL and relays the response back to the original response.
- B 摘要: Fetches a list of dataset names from a server URL with caching.
- 静态失败原因: The low token overlap (0.113) and dissimilar method names/control flow led the model to predict non-clone, while BCB considered the shared network I/O pattern sufficient for a clone.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may consider both as network data retrieval functions with similar steps (open URL, read stream), despite different high-level purposes.
- 共享行为: Both functions make an HTTP request to a URL and read data from the response stream.
- 行为差异: Function A forwards request headers and body, then relays the response; Function B only reads a line-oriented list and caches results.；Function A handles HTTP methods and status codes; Function B appends '?server=list' to the URL and reads lines.；Function A is a proxy servlet; Function B is a caching data loader.
- 修正建议: Enhance model with semantic-aware representations that capture higher-level intent like 'network communication' rather than just token overlap.；Use dataflow analysis to detect common patterns like URL opening and stream reading across different implementations.

### case_id=1285 FN partial_functionality

- 方法: `runInternal` vs `getWebByUrl`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Runs internal network operation for OPDS catalog reading with pagination.
- B 摘要: Downloads a web page and saves to file, recursively crawling links.
- 静态失败原因: Low lexical overlap; BERT models may rely on surface-level patterns and miss higher-level semantic differences in purpose.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as functions that fetch content from a URL over HTTP, thus broadly similar.
- 共享行为: Both open an HTTP URL connection and read input stream
- 行为差异: A handles OPDS-specific content, pagination, and download triggering; B writes to file and recursively processes links
- 修正建议: Incorporate dataflow analysis to distinguish specific operations like parsing vs. file writing；Use graph representations that capture control flow and data dependencies

### case_id=1286 FP lexical_or_api_overlap

- 方法: `doVersionCheck` vs `getFrameworkFactory`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads version and build numbers from a remote URL and compares with current build to notify user.
- B 摘要: Reads an OSGi service configuration from classpath and loads the FrameworkFactory class via reflection.
- 静态失败原因: Static BERT models often rely on token similarity and control flow structure; these methods share many API tokens (BufferedReader, URL, readLine, trim) and a similar read-loop pattern, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels as non-clone because the methods have distinct high-level functionality and domain context, despite sharing low-level I/O patterns.
- 共享行为: Open an input stream from a URL or classpath resource；Use BufferedReader to read lines；Check each line for a specific prefix；Trim and process matching lines
- 行为差异: Different overall purpose: version checking vs. framework loading；Different input source: remote URL vs. classpath resource；Different output: void and UI interaction vs. return a FrameworkFactory instance；Different exception handling: catch IOException vs. throw generic Exception
- 修正建议: Incorporate method signature and return type into representation；Use dataflow analysis to capture semantic differences (e.g., one method produces a UI action, the other returns an object)；Train with more negative examples that have high lexical overlap but different semantics；Add attention to domain-specific constants like 'version-check.url' vs 'META-INF/services/...'

### case_id=1287 FN partial_functionality

- 方法: `login` vs `getXML`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Logs in to LOLA by sending credentials via POST and returning session ID.
- B 摘要: Fetches XML from a servlet via GET and returns the full response string.
- 静态失败原因: Static BERT models rely heavily on surface-level token overlap and may miss deeper structural similarity. Here token overlap is low (0.246), and the methods have different names and argument structures, leading the model to classify them as non-clones. However, BCB recognizes the shared HTTP communication pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider these clones because they share the core pattern of making an HTTP request, encoding parameters, and reading the response. The boilerplate code for network I/O (URL encoding, opening connection, reading lines) is similar despite differences in HTTP method and output extraction.
- 共享行为: Encode a request string to UTF-8；Open a URL connection；Read response line by line from an input stream；Catch exceptions and return a default value on error
- 行为差异: A uses POST with OutputStream, B uses GET with url.openStream()；A reads only first line and extracts session ID, B reads all lines into buffer；A has generic Exception handling, B catches specific exceptions (MalformedURL, UnsupportedEncoding, IOException)；A returns empty string on error, B returns null
- 修正建议: Incorporate AST or control flow graph features to capture structural similarity；Use contrastive learning on pairs with low lexical overlap but high structural similarity；Add domain-specific knowledge about common API usage patterns (e.g., HTTP requests) to the model

### case_id=1288 FP lexical_or_api_overlap

- 方法: `getProjectTreeData` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Retrieves project tree data from a server URL, parses XML, and returns a 2D string array of project IDs.
- B 摘要: Handles UI action commands like GRAPHVIZ and IMAGEMAGICK by opening file choosers and storing preferences, also handles other settings.
- 静态失败原因: Static BERT models may over-rely on surface-level token overlap (e.g., common APIs like File, String, try-catch) and fail to capture the distinct application logic, especially when the functions are long and have different control flows.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clones because the functions have different names, different overall behavior, and only minimal lexical overlap; BCB's annotation guidelines would not consider these as clones even under broad Type-4 similarity.
- 共享行为: Both use File and InputStream/OutputStream classes；Both involve handling of filenames and paths
- 行为差异: A fetches data from a remote server and parses XML; B responds to UI events and updates application preferences；A returns a 2D array; B returns void and modifies UI state；A has extensive XML parsing; B has no XML parsing
- 修正建议: Improve model training with more diverse negative examples；Incorporate structural features like abstract syntax trees or control flow graphs；Use contrastive learning to distinguish semantically different functions

### case_id=1289 FN partial_functionality

- 方法: `copyResource` vs `getFileContentAsString`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource (URL or file) to a destination file by reading bytes.
- B 摘要: Reads a file path (URL or file) and returns its content as a string.
- 静态失败原因: Static BERT methods rely heavily on token similarity and surface-level features; low Jaccard similarity (0.24) and different method names, library calls, and output handling likely caused the model to miss the structural parallelism in the input-handling logic.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels Type-3/Type-4 clones that share a core algorithmic structure, even if the output or helper libraries differ. Here, the essential logic of locating a resource and reading its stream is identical.
- 共享行为: Both attempt to open an input stream from a URL first, falling back to a file.；Both close the input stream after reading.；Both perform I/O operations on a resource identified by a string.
- 行为差异: Function A writes the stream to a file; Function B converts the stream to a string and returns it.；Function A uses manual byte-by-byte copying; Function B uses IOUtils.copy.；Function A does not handle encoding; Function B accepts an encoding parameter.；Function A throws Exception; Function B throws IOException.
- 修正建议: Train on functional semantics using data-flow and control-flow graphs.；Incorporate API usage patterns (e.g., URL.openStream paired with FileInputStream).；Use contrastive learning with positive pairs based on shared I/O patterns.

### case_id=1290 FN partial_functionality

- 方法: `getHTML` vs `startScript`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches HTML content from a URL and optionally writes it to a file.
- B 摘要: Loads a script from a URL and appends it to a dialog script buffer.
- 静态失败原因: Static models like GraphCodeBERT rely heavily on token overlap and structural similarity, which are low between these two functions (Jaccard=0.2467). The core similarity is buried in a common subsequence of API calls, but the different method names, parameter lists, and surrounding logic (file writing vs. dialog scripting) cause the model to focus on dissimilar aspects. The model likely did not capture the semantic equivalence of the URL reading loop due to insufficient training on such subtle functional patterns.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels pairs as clones if they perform the same core operation (here, reading a URL line by line), even if the surrounding code, method signatures, and secondary behavior differ. This pair likely qualifies as a Type-3 or Type-4 clone because both implement the same algorithmic pattern of fetching remote content line by line.
- 共享行为: Both read text from a URL line by line using BufferedReader and accumulate the lines into a string.
- 行为差异: A returns the fetched HTML string; B does not return a value but updates an object.；A includes optional file writing; B does not write to file.；B calls System.exit(0) on IOException; A only prints stack trace.；A sets User-Agent header and uses HttpURLConnection; B uses URL.openStream() directly.
- 修正建议: Enhance models with data-flow analysis to identify common API usage patterns.；Use contrastive learning with functional similarity pairs.；Incorporate token-level attention to common sequences like 'new BufferedReader(new InputStreamReader(new URL(…).openStream()))'.

### case_id=1291 FN partial_functionality

- 方法: `modifyApplicationMessage` vs `run`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.4`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Modifies a specific key-value pair in a Java properties file for internationalization, reading from an English base file and writing to a locale-specific file.
- B 摘要: Processes pseudolocalization on message catalog files, reading input files, transforming messages through a pipeline, and writing output files with a suffix.
- 静态失败原因: Static models likely overemphasized token overlap and method name differences, missing the high-level I/O and resource processing pattern that BCB considers as partial functionality similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this as a clone due to the broad similarity in file-based localization resource manipulation, focusing on the read-modify-write pattern rather than specific content transformation.
- 共享行为: Read input files (properties or message catalog) and write output files；Handle file existence checks and I/O exceptions；Process string content and output modified versions
- 行为差异: A modifies a single message; B transforms all messages via a pipeline；A targets a specific locale and message name; B processes arbitrary files with a variant suffix；A uses hardcoded paths; B uses command-line arguments；B supports interactive mode and multiple input files; A processes only one locale at a time
- 修正建议: Incorporate structural patterns like file I/O sequences in training；Use dataflow analysis to detect read-process-write chains；Augment benchmarks with more Type-3/Type-4 partial functionality clones

### case_id=1292 FN partial_functionality

- 方法: `main` vs `byReference`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.75`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a URL and extracts its zip entries to files.
- B 摘要: Copies an input stream to a temporary file and returns it as a DigitalObjectContent.
- 静态失败原因: GraphCodeBERT likely focused on method signatures, imports, and control flow differences, missing the underlying IO pattern similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider the common InputStream-to-FileOutputStream copy pattern as a Type-4 clone, despite different contexts.
- 共享行为: Both read from an input stream and write to a FileOutputStream.
- 行为差异: A handles HTTP protocol and zip entries; B is generic.；A extracts multiple files; B creates a single temp file.；A prints progress; B catches IOException and throws IllegalStateException.
- 修正建议: Use subgraph matching for common IO idioms.；Incorporate task-level context (main vs utility method).；Focus on API usage patterns rather than whole-function semantics.

### case_id=1293 FP partial_functionality

- 方法: `load` vs `downloadModel`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Loads raw XML content from pastebin by ID, concatenates lines, and returns as string; shows error dialog on failure.
- B 摘要: Downloads an RDF model from a URL using HTTP headers and Jena's model reader; throws runtime exception on failure.
- 静态失败原因: Static BERT/GraphCodeBERT models are sensitive to surface-level token overlap (URL, URLConnection, try-catch, InputStream) and structural similarity, failing to distinguish semantic differences in data handling and return types.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB typically considers functional equivalence; here the output types and processing differ significantly (raw string vs RDF model), despite similar URL reading boilerplate.
- 共享行为: Both open a URL connection and read data from an HTTP source；Both use try-catch for IOException；Both close the input stream after reading
- 行为差异: Function A returns a String; function B returns a Model object；A concatenates lines manually; B uses model.read() to parse RDF；A uses a fixed pastebin URL pattern; B accepts any URL and sets HTTP headers；Error handling: A shows a dialog and returns empty string; B throws RuntimeException
- 修正建议: Incorporate return type and data flow analysis；Use abstract syntax tree or data dependence graphs to differentiate output transformations；Train models to recognize that similar I/O boilerplate does not imply semantic equivalence

### case_id=1294 FN partial_functionality

- 方法: `run` vs `read`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.5`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a classpath resource as text and sets it on a UI panel.
- B 摘要: Reads from a URL or file into a buffer and returns a status code.
- 静态失败原因: Low token overlap (0.14) and differing method names/structures, with long-range semantic differences (UI update vs status return) not captured.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label as clone because both methods perform a 'read from URL' operation with similar I/O exception handling, fitting a broad Type-4 partial functionality similarity.
- 共享行为: Both open an input stream from a URL and read data.；Both handle exceptions with try-catch blocks.
- 行为差异: A uses classpath resource; B uses arbitrary URL or file.；A reads text lines; B reads raw bytes.；A updates UI; B returns integer status.；A is a Runnable; B is a regular method returning int.
- 修正建议: Use dataflow-aware models that track I/O operations and error handling patterns.；Incorporate structural similarity metrics beyond token overlap.；Consider benchmarking with contrastive examples of broad I/O clones.

### case_id=1295 FP lexical_or_api_overlap

- 方法: `actionPerformed` vs `copyFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Action event handler that opens file choosers for executable selection and manages multiple GUI preferences.
- B 摘要: Utility method that copies a file from source to destination using FileChannel with exception logging.
- 静态失败原因: The model likely overfitted on common file-related tokens (e.g., 'File', 'InputStream', 'Exception') and logging patterns, ignoring the overall control flow and purpose. The length of code A may have caused the model to miss the fundamental difference.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would label this as non-clone because the functions perform entirely different tasks: one is a GUI event handler for settings, the other is a file copy utility. There is no functional similarity even at a high level.
- 行为差异: A is a complex GUI event handler with multiple conditional branches; B is a simple file I/O utility.；A involves user interaction via file chooser dialogs; B operates on pre-supplied file paths.；A updates application preferences and UI state; B returns a boolean success flag.
- 修正建议: Incorporate semantic role labeling or high-level intent detection to distinguish event handlers from utilities.；Use graph-based representations that capture control flow and data dependencies to avoid being misled by shared APIs.；Add training examples with long functions to improve handling of such cases.

### case_id=1296 FN benchmark_preference_bias

- 方法: `modifyApplicationMessage` vs `doPost`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Modifies a property value in a locale-specific .properties file, copying from English file if missing.
- B 摘要: Handles HTTP POST multipart form to receive a webpage or URL and generate a mailer page output.
- 静态失败原因: A static BERT/GraphCodeBERT model likely failed (predicted non-clone) because it captured the low token-level and syntactic similarity (Jaccard 0.125) and distinguished the different program contexts and purposes. Since the functions are truly different semantically, the model correctly predicted non-clone, but this contradicts BCB's labeling. The model's failure here is actually a correct prediction, but the benchmark considers it an FN because of BCB's erroneous clone label.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as a clone due to superficial similarities in structure: both have a try-catch block, file I/O operations, and loops. However, the overall semantics are entirely different. This could be an example of benchmark preference bias where high-level similarity in control flow or I/O patterns is considered sufficient for Type-4 clone classification.
- 共享行为: Both use file I/O streams (InputStream/OutputStream) and try-catch blocks.；Both involve reading line by line from a source (file or stream).；Both use StringBuilder or similar for building output.
- 行为差异: Function A deals with configuration properties files; function B handles HTTP file upload and mailer generation.；Function A writes to a file; function B writes to HTTP response output stream.；Function A modifies existing content; function B creates new content from uploaded data.；Function A uses Properties and BufferedReader; function B uses ServletFileUpload and IOUtils.
- 修正建议: Improve training data quality by removing or correcting such false positive BCB labels.；Incorporate more detailed semantic annotations to distinguish general I/O patterns from specific domain operations.

### case_id=1297 FN partial_functionality

- 方法: `main` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a zip file from a hardcoded URL and extracts all entries to files.
- B 摘要: Reads a zip file, processes .out entries to parse probabilistic rules, evaluates them, and prints performance.
- 静态失败原因: Static BERT/GraphCodeBERT likely focused on lexical token overlap (low Jaccard) and divergent control flows, missing the shared structural pattern of zip iteration and stream handling.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often accepts broad Type-4 clones where both functions share a common high-level pattern of iterating over zip entries and performing I/O, even if the specific processing differs.
- 共享行为: Both are main methods that throw Exception.；Both iterate over entries in a zip file using while loops.；Both use BufferedInputStream/OutputStream to read/write zip entry data.
- 行为差异: Function A reads from a URL; Function B reads from a local zip file.；Function A extracts all entries; Function B only processes .out entries.；Function B performs complex rule parsing and evaluation; Function A simply writes entry contents.；Function B requires command-line arguments; Function A uses a hardcoded URL.
- 修正建议: Use a model that captures structural and dataflow similarity, such as a graph-based model or contrastive learning on method-level embeddings.；Incorporate information about overall method purpose, e.g., via documentation or method names.

### case_id=1298 FN benchmark_preference_bias

- 方法: `copyFiles` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Recursively copies files or directories from source to destination using file channels.
- B 摘要: Launches a NexOpen project by validating Maven pom.xml files, setting Hibernate dialect properties, and triggering an install project action.
- 静态失败原因: The static model correctly identified no semantic equivalence (low token Jaccard, different method names, completely different logic) but BCB label is 1, so the model 'failed' to match the erroneous benchmark label.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB likely mislabeled this pair, possibly due to both methods containing file I/O operations and conditionals, but they have no functional overlap. The annotation may be an error.
- 共享行为: Both perform file system operations (reading/writing files).
- 行为差异: copyFiles focuses solely on file/directory copying without any project configuration.；launch handles complex Eclipse launch configuration, project validation, XML manipulation, and Hibernate setup.；copyFiles is recursive while launch uses iteration and conditional logic for different project structures.；copyFiles uses NIO FileChannel for efficient copying; launch uses streams and property files.
- 修正建议: Review BCB annotation for this pair; consider correcting label to 0.；If BCB intends Type-4 clones, ensure explicit criteria for such broad similarity.

### case_id=1299 FN benchmark_preference_bias

- 方法: `doGet` vs `DecodeMapFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Handles HTTP GET requests, retrieves a page by ID or name, checks user visibility, renders the page with optional caching to a temp file.
- B 摘要: Decodes a map file by reading it as bytes, applying XOR with an incrementing key, and writing the result to an output file.
- 静态失败原因: Static BERT correctly predicted non-clone due to low token overlap and distinct contexts; the model did not fail.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have considered the broad Type-4 similarity as both functions involve file I/O and data transformation, but this is too generic; likely a mislabel.
- 共享行为: Both involve reading some input and writing output.；Both use try-catch for error handling.；Both may create files conditionally.
- 行为差异: doGet is a web servlet handler dealing with HTTP requests and page objects; DecodeMapFile is a static utility for file decoding.；doGet has complex control flow with multiple conditions, logging, and page caching; DecodeMapFile has a simple loop for byte transformation.；The core logic (page rendering vs. XOR decoding) is completely different.
- 修正建议: Review BCB annotations for this pair to verify correctness.；If BCB label is incorrect, update the benchmark.；Ensure training data includes diverse examples to avoid such biases.

### case_id=1300 FP lexical_or_api_overlap

- 方法: `getUser` vs `retrieveTemplate`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Loads a user from database; if not found, reads from a config file and saves to database.
- B 摘要: Retrieves a web template from a URL, caches it, and returns the string.
- 静态失败原因: Static BERT likely overemphasized the lexical overlap of URL, BufferedReader, InputStreamReader, and while loop patterns, missing the functional context and different goal/return types.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clone because functions have entirely different high-level purposes (user authentication vs template retrieval) despite some low-level I/O overlap.
- 共享行为: Both read from a URL stream line by line；Both use BufferedReader and InputStreamReader
- 行为差异: A takes a userlogin parameter; B takes no input；A reads from a local config file or database; B reads from a remote URL；A returns a User object; B returns a String；A catches and prints exception; B throws Exception
- 修正建议: Add dataflow analysis to distinguish data sources；Use broader context (e.g., method name, class fields)；Adjust threshold for low Jaccard similarity pairs

### case_id=1301 FN benchmark_preference_bias

- 方法: `main` vs `testStandardTee`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `preference_memory_with_manual_audit`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a URL, reads its ZIP entries, and extracts each entry to a file.
- B 摘要: Tests that a TeeWriter correctly duplicates data by copying a string to two StringWriters and verifying equality.
- 静态失败原因: The low token Jaccard similarity and different method names, library usage, and control flow structures make it hard for static models to detect the high-level semantic similarity.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider both as implementing a 'copy stream' pattern: reading from an input stream and writing to output stream(s), with resource management, making them Type-4 semantic clones.
- 共享行为: Both read from an input source and write to one or more output destinations using stream/buffer operations.；Both close resources after use.
- 行为差异: Function A deals with network I/O and ZIP extraction; Function B is a unit test with in-memory streams.；Function A writes to files; Function B writes to StringWriters.；Function A has no assertions; Function B has assertions.；Function A uses ZipInputStream; Function B uses TeeWriter and IOUtils.copy.
- 修正建议: Use graph-based models that capture data flow and resource usage.；Incorporate library function semantics and context.

### case_id=1302 FP lexical_or_api_overlap

- 方法: `readData` vs `test`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Parses comma-separated strings and a file to populate hash sets and a map for Tibetan transliteration.
- B 摘要: Tests the write, close, input/output stream, and copy behavior of StorageStringWriter.
- 静态失败原因: The model may have been misled by lexical overlap in exception handling (IOException) and general string use, or by structural similarities in error handling patterns despite low token Jaccard.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely classified as non-clone because functions have completely different purposes and no shared functionality beyond basic string operations.
- 共享行为: Both involve string manipulation
- 行为差异: Function A initializes data structures for Tibetan transliteration；Function B tests a utility class for storage；Different inputs and outputs；Different control flow (loops vs linear)
- 修正建议: Improve model's ability to capture higher-level intent via method names and dataflow；Use a more robust structural matching that distinguishes initialization from testing；Include method name embeddings to disambiguate

### case_id=1303 FN benchmark_preference_bias

- 方法: `copyResource` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Copies resource from URL or file to a destination file.
- B 摘要: Generates a license file by writing hardcoded strings and metadata from library files.
- 静态失败原因: The static model correctly predicted non-clone due to low token overlap and different structure; it did not fail in this case.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might have considered both as file-writing operations, but the semantics are completely different; likely a false positive annotation.
- 共享行为: Both use FileOutputStream to write data to a file
- 行为差异: A reads from a single input source and writes all bytes; B constructs strings and writes them, processing multiple files；A has error handling for missing resource; B does not；A is a private method; B is a public static main method
- 修正建议: Re-annotate this pair as non-clone; refine BCB guidelines to avoid superficial I/O overlap

### case_id=1304 FN benchmark_preference_bias

- 方法: `doGet` vs `doPost`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.1`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Handles HTTP GET request for displaying a page, handling different page lookup methods and permissions.
- B 摘要: Handles HTTP POST request for uploading a webpage file via multipart form and converting it using ToMailerDelegate.
- 静态失败原因: Static BERT/GraphCodeBERT methods might miss long-range semantic differences and rely on local context, but here the shared servlet boilerplate is minimal; low token Jaccard and different method names likely led to correct non-clone prediction.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled as clone due to both being servlet methods with similar boilerplate (try-catch, logging, response handling) and both dealing with 'page' concepts, but functionality differs significantly.
- 共享行为: Both are servlet methods processing HTTP requests；Both handle request/response objects and may send errors
- 行为差异: doGet retrieves and displays existing pages based on parameter or home page；doPost uploads a file or URL and converts it to a mailer output；doGet involves page visibility checks and caching, doPost does not；doPost uses multipart parsing and file streams, doGet does not
- 修正建议: Re-evaluate BCB annotation to ensure it aligns with functional similarity criteria；Improve BCB guidelines to avoid labeling servlet boilerplate as clones

### case_id=1305 FN benchmark_preference_bias

- 方法: `getHTML` vs `populateResources`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads HTML from a URL and optionally saves it to a file.
- B 摘要: Loads template files and images from classpath resources and saves them to a database.
- 静态失败原因: Static BERT models rely on lexical overlap and syntactic patterns; with a token Jaccard of 0.16 and completely different method names and API calls, the model correctly predicted non-clone. The BCB label appears to be a false positive, so the model actually succeeded in this case.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might consider these as clones due to broad Type-4 similarity: both involve reading from an input stream, processing lines, and writing output to a persistent storage (file vs database). Annotators may have focused on the generic I/O pattern rather than the specific domain.
- 共享行为: Reads from an input stream line by line using BufferedReader；Appends lines to a string buffer；Handles IO exceptions
- 行为差异: A reads from HTTP connection, B reads from classpath resources；A writes to a file, B writes to a database via Resource/Image/Property save methods；A takes parameters (URL, encoding, dirPath), B has no parameters；A returns the HTML string, B returns void
- 修正建议: Consider whether BCB annotation guideline aligns with this pair; if not, correct the dataset.；Improve model robustness by focusing on semantic similarity beyond token overlap.；Use more abstract representations like dataflow or control flow graphs to capture shared patterns.

### case_id=1306 FP boilerplate_overlap

- 方法: `PageLoader` vs `SRWGuiClient`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Opens a URL and reads its entire content into a single string variable.
- B 摘要: Constructs a Swing browser GUI, reads URL content, processes XML with optional XSLT transformation, and displays HTML.
- 静态失败原因: Static BERT models may overemphasize the overlapping API calls (URL, BufferedReader, InputStreamReader) as a strong signal, ignoring the large structural and functional differences.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely rejected the clone because the shared URL reading boilerplate is too small relative to the vastly different overall functionality and purpose.
- 共享行为: Both open a URL stream using BufferedReader and InputStreamReader
- 行为差异: A is a simple URL content loader; B builds a full GUI window；A concatenates all lines until ready; B handles XML, stylesheets, and transforms；B includes exception handling and UI setup; A has none
- 修正建议: Incorporate structural or dataflow analysis to distinguish boilerplate from core logic；Use long-range attention mechanisms to capture context differences；Post-filter low similarity pairs with high API overlap but low semantic similarity

### case_id=1307 FN partial_functionality

- 方法: `getFile` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies its endpoint, and returns the local file path.
- B 摘要: Copies a source file to a destination file using FileChannel, returns success status.
- 静态失败原因: Low token Jaccard (0.11) and surface-level dissimilarity caused the model to miss the shared FileChannel API usage, which requires structural understanding of API call sequences.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider them clones due to shared low-level file I/O pattern (FileChannel), even though the high-level functionality differs, reflecting a Type-4 semantic clone.
- 共享行为: Use FileChannel.transferFrom for efficient data transfer
- 行为差异: Different input types (URL vs File)；Different output (String path vs boolean)；Error handling: throws AxisFault vs returns false；getFile modifies XML content; copyFile does not
- 修正建议: Encode API call sequences as features；Use AST-based embedding to capture shared I/O patterns；Add data-flow analysis for file operations

### case_id=1308 FN boilerplate_overlap

- 方法: `testNetworkHTTP` vs `addIDs`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Test method that performs multiple HTTP GET requests to various URLs and reads responses line by line without further processing.
- B 摘要: Method that queries a chemical database via HTTP, parses HTML response to extract metabolite IDs and related data, and populates fields of a PeakListRow object.
- 静态失败原因: Static BERT/GraphCodeBERT models rely on token-level patterns and may be misled by the boilerplate HTTP setup and error handling which are common across many methods, while missing the semantic specificity of the post-retrieval processing. The low token Jaccard suggests the model correctly saw low overlap, but BCB's label (1) indicates a semantic match that the model failed to capture, likely because the model is not sensitive enough to the functional similarity of 'retrieve data from web' vs. 'test network connectivity'.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may consider this pair as Type-3/Type-4 clones because both involve the same underlying pattern of opening an HTTP connection, reading from it, and handling exceptions. The high-level behavior of 'network data retrieval' is considered similar enough for broad clone detection, even though the data processing differs significantly.
- 共享行为: Both make HTTP GET requests using java.net.URL and HttpURLConnection；Both read the response line by line using BufferedReader and InputStreamReader；Both handle IOException by printing/logging stack trace
- 行为差异: Function A discards all read data, while B parses HTML and extracts specific patterns；Function A disconnects the connection in finally block, B closes the reader inline；Function A makes multiple sequential requests unconditionally, B conditionally breaks out of loop based on content；Function B returns an integer (score), A returns void
- 修正建议: Incorporate structural similarity like API call sequences and control flow graphs to recognize common patterns beyond exact token matches；Use contrastive learning with positive pairs that are semantically similar but token-diverse；Add attention to the purpose of the method by considering method names and surrounding context

### case_id=1309 FN other

- 方法: `readData` vs `CheckUrl`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Parses multiple static string fields and a configuration file to populate sets and hash maps for Tibetan/Wylie transliteration.
- B 摘要: Fetches the first line of a given URL using HTTP connection.
- 静态失败原因: Static BERT model likely correctly classified as non-clone due to low token overlap and distinct syntactic and semantic structures.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may have labeled this as clone due to both functions involving input reading and data extraction, but the contexts and implementations are entirely different.
- 共享行为: Both perform input reading and string processing.
- 行为差异: A reads from internal strings and a file; B reads from a URL via HTTP.；A populates multiple data structures; B returns a single string.；A has complex parsing logic; B simply reads the first line.；A handles exceptions locally; B catches Exception broadly.
- 修正建议: Re-evaluate BCB annotation for this pair; functions are not semantically similar.；Consider that the low Jaccard similarity and different API usage strongly indicate non-clone.

### case_id=1310 FN partial_functionality

- 方法: `copyResource` vs `actionPerformed`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource from a URL or file to a destination file using byte-by-byte I/O.
- B 摘要: Reads lines from a gzipped file and sends them as parameters to a web service via a URL POST, then copies the response to standard error.
- 静态失败原因: Low token overlap (Jaccard 0.12) and different method names led the model to focus on syntactic differences, missing the high-level similarity in I/O streaming operations.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this as a clone because both functions perform a 'copy' operation from an input source to an output destination using streams, sharing a common I/O pattern despite different specific tasks.
- 共享行为: Both open a URL connection and use I/O streams to read and write data.；Both handle exceptions (A throws, B catches).；Both close resources after use.
- 行为差异: A copies byte-by-byte; B reads lines, processes tokens, and writes to URL output stream.；A writes to a local file; B writes to a URL output stream and System.err.；B uses GZIP compression for reading; A does not.；B filters and transforms input data; A does not.
- 修正建议: Train the model to recognize common I/O patterns even when variable names and specific implementations differ.；Incorporate dataflow analysis to identify input-to-output copying regardless of intermediate processing.；Use code summarization to compare high-level intent.

### case_id=1311 FN benchmark_preference_bias

- 方法: `doGet` vs `encodeFileToFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.6`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Handles HTTP GET requests to serve a portal page, including user permission checks, logging, and optional caching to a temp file.
- B 摘要: Encodes a source file to Base64 and writes the result to a destination file, with basic error handling.
- 静态失败原因: The static BERT-based model likely focused on the overall high-level semantics and API usage, correctly identifying that the primary purposes are unrelated. It may have missed the small overlapping file I/O pattern because the token Jaccard similarity is very low and the functions have different structural contexts.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled these as clones due to the presence of try-catch-finally and the file-writing segment in doGet, interpreting both as file I/O operations with error handling, which fits a broad Type-4 (partial functionality) clone definition.
- 共享行为: Both use try-catch-finally blocks for exception handling and resource cleanup.；Both involve reading from an input source (HTTP request/Base64 input stream) and writing to an output (response/temp file/Base64 output stream).
- 行为差异: doGet handles web requests and user sessions, while encodeFileToFile is a pure file conversion utility.；doGet has complex logic for page retrieval, user visibility, and caching, whereas encodeFileToFile is a straightforward encoding loop.；The file I/O in doGet is a small, conditional part of its overall logic, whereas encodeFileToFile's sole purpose is file I/O.；doGet uses servlet-specific APIs (HttpServletRequest, HttpServletResponse), while encodeFileToFile uses standard Java I/O.
- 修正建议: Increase the diversity of BCB annotations to avoid pairing functions with only incidental similarities.；Improve model sensitivity to partial functional overlaps by incorporating hierarchical or hierarchical functional decomposition.

### case_id=1312 FP boilerplate_overlap

- 方法: `getTicketsForQueue` vs `loadURL`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Queries a request tracker API for open tickets in a queue and returns a list of ticket objects after fetching each ticket individually.
- B 摘要: Opens a URL connection with optional authentication, reads the content line by line, writes it to a temporary file, and updates a status label with download progress.
- 静态失败原因: The static BERT model likely overvalued the common structural boilerplate (HTTP connection, BufferedReader, try-catch) and ignored the different semantics and API usage, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would label this as non-clone because the functions perform distinct high-level tasks (ticket retrieval vs URL download) with different APIs and output, despite sharing a common I/O pattern.
- 共享行为: Both perform an HTTP GET request and read lines from the response stream.；Both use a BufferedReader to read input and handle I/O operations.；Both have logic to conditionally process each line.
- 行为差异: A queries a specific REST API endpoint for tickets, B loads any URL content to a file.；A parses ticket IDs from lines, B writes every line to a file.；A has error handling that returns null or throws exceptions, B throws IOException.；A uses HttpClient (HttpGet/HttpResponse), B uses URLConnection.
- 修正建议: Incorporate features that capture the semantic purpose, such as method name embeddings, API call sequences, and output types.；Use dataflow analysis to distinguish different data transformations.；Augment training data with more pairs that share I/O patterns but different intents.

### case_id=1313 FP lexical_or_api_overlap

- 方法: `handleHandshake` vs `setBundleInfoName`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Handles a Minecraft handshake packet by validating a server key and performing an HTTP session join request.
- B 摘要: Reads a URL content line by line, parses key-value pairs, and updates bundle names in a list.
- 静态失败原因: The static model was misled by shared structural elements like URL, BufferedReader, readLine, and printStackTrace, focusing on API usage rather than core semantics.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely sees no functional similarity; the only overlap is generic I/O patterns which are too trivial for clone labeling.
- 共享行为: Both use URL and BufferedReader to read from a URL；Both call printStackTrace on exception；Both have try-catch for IOException
- 行为差异: A validates input and performs authentication logic; B parses key-value pairs and updates objects；A sends network packets; B returns a boolean；A has multiple conditional branches; B has a single loop
- 修正建议: Train model to distinguish between core logic and peripheral I/O patterns；Incorporate dataflow analysis to understand how data is transformed；Use control flow structure differences to separate these functions

### case_id=1314 FN partial_functionality

- 方法: `modifyApplicationMessage` vs `save`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Modifies or adds a property in a locale-specific properties file, handling file creation and character encoding.
- B 摘要: Writes a byte array to a file, creating parent directories and ensuring resource cleanup.
- 静态失败原因: Static BERT likely focused on low token overlap (0.101) and different API calls, failing to capture the high-level functional similarity in file I/O patterns that BCB annotators considered.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as file-writing functions that handle resource management and file existence, thus labeling as a broad Type-4 clone despite low lexical overlap.
- 共享行为: Both write data to files；Both ensure file existence before writing；Both manage I/O streams with close operations
- 行为差异: A reads, parses, and modifies a properties file; B writes raw bytes without parsing；A targets specific property keys; B writes entire byte array；A involves locale-specific file selection; B is generic file output；A uses character streams; B uses byte streams
- 修正建议: Include structural matching for file I/O boilerplate patterns；Incorporate control-flow analysis to distinguish writing vs. reading+modifying；Use data-flow to track whether bytes are transformed before writing

### case_id=1315 FP long_range_semantics

- 方法: `copyFile` vs `readData`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `static_summary_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Copies a file from source to destination using byte streams.
- B 摘要: Parses comma-separated tokens from multiple string variables and populates several sets and a hash map, with additional validation and error handling.
- 静态失败原因: The static model likely overfitted to the presence of while loops and I/O-related method names (e.g., 'read'), or the long length of readData confused the model, leading to a false positive.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB would label these as non-clones due to completely different purposes and low lexical and structural similarity.
- 共享行为: Both involve reading input and iterating over elements in a loop.
- 行为差异: copyFile does file I/O with streams; readData does string tokenization and collection population.；copyFile is short and simple; readData is very long and complex with multiple nested loops and conditionals.；copyFile has no error handling; readData has exception handling and throws errors for invalid input.；copyFile writes to an output file; readData writes to in-memory data structures.
- 修正建议: Incorporate data flow analysis to distinguish file I/O from string parsing.；Use control flow graph similarity with higher threshold for long functions.；Apply dynamic analysis or test input-output behavior to confirm semantic equivalence.

### case_id=1316 FN benchmark_preference_bias

- 方法: `modifyApplicationMessage` vs `decodeBody`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Modifies a locale-specific properties file by replacing or adding a message key-value pair.
- B 摘要: Decodes an input stream based on content transfer encoding (quoted-printable or base64) and returns a BinaryTempFileBody.
- 静态失败原因: Static model correctly identified non-clone; it did not fail. The error type FN is based on BCB label, which is likely incorrect.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB likely mislabeled this pair; there is no apparent functional similarity. Possibly due to a mistake in the dataset or a very broad interpretation of both modifying/processing content.
- 共享行为: Both perform I/O operations
- 行为差异: Function A writes to a properties file; Function B returns a Body object；Function A manipulates string key-value pairs; Function B decodes binary content；Function A handles file existence and copying; Function B handles encoding types；Function A uses Properties and BufferedReader; Function B uses InputStream and OutputStream
- 修正建议: Review BCB label for this pair; it is likely a false positive clone.；Improve dataset consistency, perhaps by removing pairs with low token similarity and no semantic overlap.

### case_id=1317 FN partial_functionality

- 方法: `login` vs `httpRequestByPOST`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Logs into LOLA by sending email and password via HTTP POST and extracting the session ID from the first line of response.
- B 摘要: Sends a generic HTTP POST request with a list of parameters and returns the full response body, with error handling via status codes.
- 静态失败原因: Static BERT models rely on token overlap and structure. Low token Jaccard (0.167) and different API calls (URLConnection vs HttpClient) obscure the shared pattern, and the model fails to generalize the abstract HTTP POST behavior.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels broad Type-3/Type-4 clones where functions share a common high-level pattern like 'HTTP POST and read response', even if libraries, parameterization, and exact return values differ.
- 共享行为: Both perform an HTTP POST request and read the response stream.
- 行为差异: Function A uses URLConnection, is hardcoded for login, reads only first line, returns session ID, and returns empty string on error.；Function B uses HttpClient, is generic, reads entire response, returns full response string, and returns null with error codes on error.
- 修正建议: Enhance the model with dataflow analysis to capture core operations like 'send data over HTTP' independent of library.；Include more training examples of HTTP communication clones with varying APIs.；Use API abstraction layers or semantic parsing to normalize different HTTP client implementations.

### case_id=1318 FN benchmark_preference_bias

- 方法: `main` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a hardcoded URL, extracts all zip entries, and writes each entry to a file.
- B 摘要: Copies a portion of an input file to an output file starting from a given offset, using command-line arguments.
- 静态失败原因: Static BERT likely relied on token and structural similarity, which is low (Jaccard 0.226), leading it to predict non-clone; it did not capture the broad behavioral similarity BCB used.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider both as clones because they share a high-level pattern: a main method that reads data from an input source (URL or file) and writes it to an output file using buffered streams, despite different specific tasks.
- 共享行为: Both are main methods using Java I/O streams to read from a source and write to a destination.
- 行为差异: A handles HTTP download and ZIP extraction; B handles file offset.；A uses hardcoded URL; B uses command-line arguments.；A processes multiple files (zip entries); B copies a single file.；A does not handle offsets; B does not handle ZIP.
- 修正建议: Align model training with BCB's annotation guidelines by incorporating more varied clone pairs with partial functionality similarity.；Use data augmentation to include pairs that share high-level I/O patterns but differ in details.

### case_id=1319 FN partial_functionality

- 方法: `getFile` vs `processAddByURLSubmit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.4`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies its endpoint attribute, and saves it to a temporary file.
- B 摘要: Fetches RDF/DOAP content from a URL and processes it via processSubmittedDoap, without saving to file.
- 静态失败原因: Static models like CodeBERT rely on surface-level token overlap and API usage patterns; low Jaccard similarity (0.074) and different method signatures likely caused the false negative.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as 'download from URL and process' tasks, accepting broad semantic similarity despite different output and specific processing.
- 共享行为: Both open a URL stream to read data from a remote resource；Both handle IO exceptions and log errors
- 行为差异: A writes to a file and modifies XML; B processes in-memory string；A uses NIO channels for copying; B uses IOUtils.copy；A handles multiple exception types (MalformedURLException, ParserConfigurationException, SAXException); B only handles FileNotFoundException and IOException；A returns a file path; B returns void
- 修正建议: Enhance representation to capture data flow and task structure beyond lexical tokens；Incorporate program analysis to detect shared behavior like URL reading and exception handling

### case_id=1320 FN partial_functionality

- 方法: `getURLContent` vs `runInternal`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches entire URL content as a string via BufferedReader.
- B 摘要: Downloads and processes an OPDS catalog from a URL, handling redirects, errors, and callbacks, potentially downloading a book.
- 静态失败原因: Static BERT models likely failed due to low token overlap (0.11) and different method names, focusing on surface form rather than the shared pattern of URL connection and input reading.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider them clones because both involve opening a URL and reading its content, viewing Function A as a simplified version of the core task in Function B (reading URL content).
- 共享行为: Both open a URL connection；Both read from an InputStream
- 行为差异: Function A returns the full content as a string; Function B processes the stream as XML or downloads a file.；Function B includes error handling for non-HTTP, redirects, timeouts; Function A has minimal error handling.；Function B includes progress updates and callbacks; Function A does not.；Function A is static and standalone; Function B is an instance method with state.
- 修正建议: Improve models to recognize core functional patterns despite differing API usage and control flow.；Focus on data flow: both methods obtain an InputStream from a URLConnection.

### case_id=1321 FP lexical_or_api_overlap

- 方法: `SRWGuiClient` vs `CheckUrl`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Constructor that initializes a Swing browser, fetches XML from a URL, optionally applies XSLT transformation, and displays the result.
- B 摘要: Static method that fetches the first line from a given URL via HTTP connection.
- 静态失败原因: The model likely focused on token overlap of common API calls like 'URL', 'BufferedReader', 'InputStreamReader', and 'readLine', missing the high-level semantic difference in overall functionality.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels based on functional similarity; despite shared URL reading, the purposes (GUI browser vs. simple URL checker) are too distinct for a Type-3/Type-4 clone annotation.
- 共享行为: Both open a URL connection；Both read input using BufferedReader
- 行为差异: A is a constructor with GUI setup; B is a static utility method；A reads entire content and optionally transforms XML; B reads only the first line；A uses URL.openStream; B uses HttpURLConnection；A performs complex XML/XSLT processing; B does not
- 修正建议: Incorporate AST or dataflow features to capture structural differences；Use contrastive learning with examples that share API tokens but differ in intent；Enhance training set with more diverse function pairs having similar low-level operations but different high-level goals

### case_id=1322 FP lexical_or_api_overlap

- 方法: `get` vs `getFullScreenUrl`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches game records from a URL using HTTP GET with custom headers, returning an array of GameRecord.
- B 摘要: Extracts fullscreen video URL from a YouTube page by parsing the response for 'fullscreenUrl', returning a string.
- 静态失败原因: Static BERT models may have focused on shared API calls (HttpURLConnection, BufferedReader) and boilerplate pattern (while loop reading lines) to erroneously predict clone, ignoring the distinct return types and domain-specific parsing logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled non-clone due to low token Jaccard (0.217) and overall different purpose: one is a generic HTTP GET for game records, the other is YouTube-specific URL extraction. Partial overlap in HTTP reading pattern is insufficient for Type-3/4 clone under BCB guidelines.
- 共享行为: Both open an HTTP connection using URL and URLConnection/HttpURLConnection.；Both read lines from the input stream using BufferedReader.；Both use try-catch for IOException handling.
- 行为差异: Return type: GameRecord[] vs String.；Function_a uses custom request headers (latitude, longitude, count) while function_b does not.；Function_b searches for a specific substring 'fullscreenUrl' and parses query parameters; function_a filters lines by '#' prefix and decodes GameRecord.；Function_b manipulates UI elements (progressDown) and updates field ytTitle; function_a is static and pure data retrieval.
- 修正建议: Incorporate semantic analysis of method return types and parameter names.；Use AST-based differences to detect structural variations beyond API usage.；Train on more diverse non-clone examples with overlapping API usage but different functionality.；Consider context like method visibility and surrounding class fields (e.g., ytTitle, progressDown).

### case_id=1323 FP boilerplate_overlap

- 方法: `getLinksFromURLFast` vs `scrapeForIsbns`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Extracts hyperlinks and their text from an HTML page using regex and returns them as two vectors.
- B 摘要: Scrapes ISBN-10 numbers from a web page using regex, counts matches, and stores them with retry on connection failure.
- 静态失败原因: Boilerplate code (URL opening, BufferedReader, regex loops) dominates the representations, making them appear similar despite different semantics.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically requires substantial functional similarity; these tasks are too different in specific output and purpose.
- 共享行为: Both open a URL connection, read lines with BufferedReader, and apply regex to parse content.
- 行为差异: Different regex patterns: one for links, one for ISBNs.；Different output: vector of links vs count of ISBNs.；Error handling: B has retry logic; A does not.；Logging: different levels and messages.
- 修正建议: Enhance model to focus on task-specific operations beyond boilerplate.；Incorporate dataflow or program dependence information to distinguish I/O patterns.

### case_id=1324 FN boilerplate_overlap

- 方法: `main` vs `doVersionCheck`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Constructs parameters and sends a POST request to RenRen API, then prints the response.
- B 摘要: Opens a version-check URL, reads lines to extract version and build info, and displays update message or error.
- 静态失败原因: The low token Jaccard similarity (0.139) and different library/API calls caused Static BERT to miss the structural similarity in the network I/O pattern, focusing on lexical differences.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may have labeled these as clones due to shared structural pattern of network I/O (URL opening, BufferedReader, while loop) and similar control flow, which qualifies as a Type-3 near-miss clone under their broad criteria.
- 共享行为: Both open a URL and read data using BufferedReader in a while loop；Both use InputStream from URL.openStream()；Both handle IOException
- 行为差异: Function A sends a POST request with multiple parameters; Function B only GETs；Function A prints raw response; Function B parses specific lines and shows GUI messages；Function A uses specific RenRen library classes; Function B uses jEdit utilities；Function A is a main method; Function B is a helper method with a view parameter
- 修正建议: Enhance model with structural AST-based features to capture common I/O patterns；Use data flow analysis to identify similar sequences of operations；Include heuristics for boilerplate code patterns that often appear in clones

### case_id=1325 FN partial_functionality

- 方法: `register` vs `doVersionCheck`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Registers a user by encoding password, setting registration date, creating hash, making HTTP request to phpBB, persisting user, and sending confirmation email.
- B 摘要: Performs version check by fetching a URL, parsing lines to get build versions, and calling another method.
- 静态失败原因: Static BERT likely correctly identified the high-level semantic difference (registration vs. version check) and low token overlap, but the BCB label may be an outlier or mislabel; alternatively, the model may have missed the superficial I/O similarity that BCB might emphasize.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB might consider these as clones due to the shared pattern of opening a URL, reading lines, and handling exceptions, viewing them as functionally similar network I/O tasks, though the overall purposes differ significantly.
- 共享行为: Both open a URL connection and read lines from the input stream；Both handle IOException and perform exception logging
- 行为差异: A performs multiple user registration steps (password encoding, date setting, hash creation, database persistence, email sending) while B only parses version numbers；A writes to database and sends email, B does not；A uses a specific phpBB URL, B uses a configurable property
- 修正建议: Incorporate additional context about the overall method purpose beyond local token patterns；Use fine-grained program analysis to distinguish between true functional equivalence and superficial I/O code similarity

### case_id=1326 FN partial_functionality

- 方法: `loadMFileViaWeb` vs `runInternal`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Loads a MATLAB file from a web URL and parses it into a UserFunction object.
- B 摘要: Fetches and parses an OPDS catalog feed from an HTTP server, handling pagination and book downloads.
- 静态失败原因: The model may have relied on superficial API overlap (URL, openStream) and missed the distinct semantics, or the low token Jaccard made it predict non-clone correctly.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as 'web-based file loading' tasks, but the specific goals and implementations are very different; this pair likely is a false positive in BCB annotations.
- 共享行为: Both open a URL connection and read input data；Both handle exceptions during network I/O
- 行为差异: Function A loads a single file; Function B processes a paginated catalog with multiple states；Function A returns a UserFunction; Function B has side effects and calls callbacks；Function B uses HTTP headers, redirects, timeouts, and content-type handling; Function A does not
- 修正建议: Enhance semantic understanding of method purpose beyond shared I/O boilerplate；Incorporate domain-specific context or method name semantics；Use finer-grained control flow analysis to distinguish different algorithms

### case_id=1327 FN boilerplate_overlap

- 方法: `fileDownload` vs `callApiPost`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.7`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a file from a given URL and saves it to a local directory.
- B 摘要: Sends an HTTP POST request with parameters and returns the response input stream.
- 静态失败原因: The static model likely relied on low token overlap (Jaccard 0.13) and lexical differences in method signatures, failing to capture the underlying structural similarity in URL connection handling and I/O boilerplate.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB might have labeled this as clone due to the similar boilerplate pattern of opening a URL connection, handling streams, and exception handling, which aligns with broad Type-3/Type-4 similarity guidelines.
- 共享行为: Both open a URL connection；Both read from an input stream；Both catch IOException and handle exceptions
- 行为差异: A writes downloaded content to a file, B returns an InputStream；A uses GET-like default, B explicitly uses POST；B sets request headers, timeouts, and checks response code; A does not；A uses character streams (BufferedReader/Writer), B uses byte streams with PrintStream
- 修正建议: Incorporate structural features like AST or data flow to capture common I/O patterns；Use contrastive learning to emphasize functional similarity despite lexical differences；Enhance training data with more diverse examples of network I/O operations

### case_id=1328 FP lexical_or_api_overlap

- 方法: `run` vs `SRWGuiClient`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Loads a resource file from classpath and sets its content as text in a UI component.
- B 摘要: Constructs a Swing browser GUI, reads and optionally transforms XML from a URL, and displays HTML content.
- 静态失败原因: Static BERT/GraphCodeBERT likely overfitted to overlapping API tokens (e.g., URL, BufferedReader, InputStreamReader, try-catch) and structural patterns (while loop reading lines), ignoring the broader context and distinct purposes.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB annotates non-clone because the two functions implement entirely different functionalities: one is a simple resource loader and the other is a full browser constructor with XML processing. The shared API calls are superficial and not indicative of semantic similarity.
- 共享行为: Both read data from a URL or input stream using BufferedReader and InputStreamReader.；Both use try-catch for exception handling.
- 行为差异: A is a short anonymous Runnable that reads a static resource; B is a long constructor that initializes a full GUI and processes XML/XSLT.；A only appends lines and sets text; B handles XML parsing, stylesheet transformation, and complex UI setup.；A runs on the event dispatch thread via SwingUtilities.invokeLater; B directly manipulates GUI components.；A has no UI creation logic; B creates panels, buttons, and scroll panes.
- 修正建议: Incorporate AST-based features to capture structural differences.；Use control flow and data flow analysis to distinguish simple sequential reading from complex branching and transformations.；Train with more negative samples that share APIs but differ in intent.

### case_id=1329 FN boilerplate_overlap

- 方法: `getHTML` vs `doVersionCheck`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a web page from a URL, optionally writes it to a file, and returns the page content.
- B 摘要: Fetches a version file from a URL, parses version and build info, and displays a message if a new version is available.
- 静态失败原因: Static models rely heavily on token overlap and surface-level similarity; the low Jaccard similarity and different method names/return types cause them to miss the shared URL-reading pattern. They may also be misled by the different error handling and UI calls in function B.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB often classes clones based on shared fundamental behavior such as URL reading and line processing, even if the post-processing differs; the boilerplate pattern of opening a connection and reading lines is considered a clone type under their broad definition.
- 共享行为: Open URL connection and read lines using BufferedReader；Process the read lines in a while loop
- 行为差异: A returns the entire HTML content; B does not return the content but shows UI messages；A optionally writes to a file; B does not write to a file；A uses HttpURLConnection with custom User-Agent; B uses URL.openStream()；A handles exceptions by printing stack trace; B shows error dialog
- 修正建议: Improve model to recognize URL reading and line processing as a reusable pattern independent of downstream logic.；Use data augmentation to create more pairs where the URL reading boilerplate is shared but post-processing differs.；Incorporate control flow and data flow graphs to track the common I/O operations.

### case_id=1330 FN partial_functionality

- 方法: `main` vs `read`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a fixed URL and prints each line to console.
- B 摘要: Reads from a URL or file based on input string and returns a status code after processing the stream.
- 静态失败原因: Low token Jaccard (0.17) and different method names, API usage (BufferedReader vs BufferedInputStream), and control flow made the model miss the underlying URL reading similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as cloning because they share the core pattern of opening a URL and reading input, despite differences in output handling and source selection.
- 共享行为: Both can open a URL stream and read input data.
- 行为差异: A prints each line to System.out; B does not print but returns a status.；A always reads a fixed URL; B reads from varying sources (URL or file) based on parameter.；A uses BufferedReader/InputStreamReader; B uses BufferedInputStream and delegates to another read method.；A does not handle exceptions; B catches IOException and sets error status.
- 修正建议: Improve model sensitivity to common patterns like URL reading even with different stream wrappers.；Incorporate data flow and semantic role labeling to recognize input/output operations.；Use contrastive learning on pairs with partial functional overlap.

### case_id=1331 FN lexical_or_api_overlap

- 方法: `copyResource` vs `CopyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource (from a URL or file) to a destination file using InputStream and OutputStream with byte-by-byte copying.
- B 摘要: Copies a source file to a destination file using NIO FileChannel with transferTo for bulk transfer.
- 静态失败原因: Low token Jaccard (0.16) and different API vocabulary (InputStream vs FileChannel) led the model to focus on superficial lexical differences, missing the core semantic similarity of copying data from source to destination.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely considers both as file copy utilities, viewing the differences in I/O API and source type (URL vs file) as implementation details, thus labeling as Type-3 or Type-4 clone.
- 共享行为: Both read data from a source and write to a destination file；Both handle file output creation
- 行为差异: A supports URL sources, B only file sources；A reads byte by byte, B uses bulk transfer via FileChannel；A uses InputStream/OutputStream, B uses FileChannel；Different exception handling (A throws Exception, B throws Exception but different signatures)
- 修正建议: Use dataflow or control-flow graphs to capture the core copy operation；Train on more diverse code transformations to recognize semantic equivalence despite API differences；Incorporate higher-level program representations like abstract syntax trees with structural alignment

### case_id=1332 FP lexical_or_api_overlap

- 方法: `postData` vs `importSequences`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Sends an HTTP POST request to a URL with form data and discards the response.
- B 摘要: Imports biological sequences from a URL by parsing a FASTA-like format and storing names and sequences.
- 静态失败原因: The model likely overfitted on the shared lexical tokens (URLConnection, InputStream, Reader) without capturing the distinct control flows and external API calls, causing a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: The functions have completely different purposes and logic; BCB typically labels such pairs as non-clones unless there is extensive structural or behavioral overlap.
- 共享行为: Both open a URL connection；Both read input streams
- 行为差异: A writes data to output stream; B reads data from input stream；A uses HTTP headers; B uses a helper class for parsing；A sends a request; B processes a response；A discards response; B stores parsed data
- 修正建议: Incorporate data flow analysis to distinguish write vs read operations；Use contrastive learning to penalize superficial API token matches；Add a global encoding of method purpose

### case_id=1333 FN benchmark_preference_bias

- 方法: `getResourceAsStream` vs `recurseFiles`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Loads a resource from a URL with HTTP caching and returns an InputStream.
- B 摘要: Recursively traverses a directory and adds non-zip files to a ZipArchiveOutputStream.
- 静态失败原因: Static BERT correctly identified the mismatch due to low token overlap and different functionality, but BCB label was 1, indicating a false negative.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have considered both as file I/O related, but this is a very broad interpretation and likely an annotation error.
- 共享行为: Both perform file I/O operations
- 行为差异: Function A handles HTTP connections and caching; Function B does not；Function A returns an InputStream; Function B writes to a ZipArchiveOutputStream；Function A does not traverse directories; Function B recursively traverses；Function A uses URLConnection and HttpURLConnection; Function B uses ZipArchiveEntry and IOUtils
- 修正建议: Review BCB annotation for this pair；Improve model to consider broader similarity if BCB standard is consistently this broad

### case_id=1334 FP lexical_or_api_overlap

- 方法: `loadSourceCode` vs `executePost`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Loads source code from a file resource, applies syntax highlighting, and builds an HTML string.
- B 摘要: Executes an HTTP POST request with parameters and returns the response body as a string.
- 静态失败原因: The static model likely over-emphasized the lexical overlap of common Java I/O patterns (BufferedReader, while-loop, try-catch) and missed the distinct method names, different API calls (getResource vs. URL connection), and the contrasting core logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB annotates clones based on semantic similarity of core functionality. These functions have completely different purposes: file I/O vs. network communication. The shared boilerplate (reading lines) is not sufficient for a clone label, especially Type-4, as the overall behavior differs.
- 共享行为: Both open an InputStream and wrap it in an InputStreamReader and BufferedReader；Both read lines in a while loop；Both handle exceptions with try-catch blocks
- 行为差异: A reads from a local file resource via getResource; B sends an HTTP POST request to a remote URL；A uses CodeViewer.syntaxHighlight on each line; B writes POST data and sets HTTP headers；A concatenates lines into an HTML string; B appends lines to a StringBuffer with carriage returns；A does not return a value; B returns the response or null
- 修正建议: Include method name embeddings to capture purpose；Use dataflow analysis to differentiate stream sources (local resource vs. HTTP connection)；Augment training data with non-clone pairs that share boilerplate but differ in core functionality

### case_id=1335 FN boilerplate_overlap

- 方法: `sendExceptionToServer` vs `register`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.7`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends exception details to a remote server via HTTP POST and prints the result.
- B 摘要: Registers a user by encoding password, creating a forum user via HTTP GET, persisting to database, and sending confirmation email.
- 静态失败原因: Static BERT models rely on token overlap and may treat the boilerplate network I/O code as a strong signal, but low Jaccard similarity (0.16) leads to false negative; they fail to recognize the deeper semantic similarity in the communication pattern.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may consider both as Type-3/Type-4 clones because they share the common pattern of remote server communication (URL construction, connection, response reading, error handling), despite different business logic.
- 共享行为: Both build a URL with query parameters and open a URLConnection；Both read the server response line by line using BufferedReader；Both handle IOException with error logging or printing
- 行为差异: Function A sends exception trace data; function B sends user registration data；Function A uses POST; function B uses GET；Function A only prints response; function B parses response as integer and persists user；Function B includes database persistence and email sending
- 修正建议: Add training data that distinguishes core functionality from boilerplate；Incorporate data flow or program dependence to capture the purpose of network calls；Use graph-based models to represent the structure of the code

### case_id=1336 FN boilerplate_overlap

- 方法: `getFile` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.2`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies its XML content to update an endpoint, and saves it to a temporary directory.
- B 摘要: Generates a license file by reading metadata from jar files and writing formatted license information to a text file.
- 静态失败原因: The static model likely relied on surface-level lexical and method name similarity, which is very low (token Jaccard 0.11), failing to detect the boilerplate overlap that might have influenced the BCB annotator.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may have labeled this as a clone due to overlapping file I/O boilerplate, such as using FileOutputStream, File, and System.getProperty, despite vastly different core functionality.
- 共享行为: Both use FileOutputStream to write data to files；Both use File objects to represent files；Both use System.getProperty to access system properties
- 行为差异: A downloads remote content via URL, B reads local files；A modifies XML content, B writes predefined text；A has complex error handling with multiple catch blocks, B throws all exceptions；A writes to a temporary file, B writes to a specific output file
- 修正建议: Incorporate structural similarity, such as control flow and data flow graphs, to capture boilerplate patterns；Use clone detection models that are robust to low token overlap but high structural similarity；Consider adding features for file I/O operations and exception handling patterns

### case_id=1337 FN partial_functionality

- 方法: `getHTML` vs `doVersionCheck`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches HTML content from a URL with custom encoding and optionally writes to a file.
- B 摘要: Checks for software version updates by reading a version file from a URL and invoking a version check dialog.
- 静态失败原因: GraphCodeBERT likely focused on low token overlap (Jaccard 0.217) and different method names/contexts (e.g., jEdit-specific APIs), missing the abstract functional similarity of URL reading and line processing.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB labels this as clone (Type-4) because both functions share the core algorithmic pattern of opening a URL, reading lines, and processing them, despite different inputs/outputs and specific purposes.
- 共享行为: Opens a URL connection；Reads lines using BufferedReader in a while loop；Handles IOException (A: Exception) in try-catch
- 行为差异: A returns fetched HTML; B returns void and performs UI actions；A uses HttpURLConnection with User-Agent header; B uses url.openStream()；A optionally writes to file; B uses jEdit-specific properties and GUIUtilities；A catches general Exception; B catches only IOException
- 修正建议: Augment training data with more Type-4 clones that share algorithmic structure but differ in specific operations；Incorporate I/O flow patterns into model representations；Use contrastive learning to emphasize similar control-flow patterns

### case_id=1338 FN boilerplate_overlap

- 方法: `scrapeForIsbns` vs `seeURLConnection`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Scrapes ISBN numbers from a web page with retry and exception handling.
- B 摘要: Reads entire content of a URL connection and logs it.
- 静态失败原因: Static BERT likely focused on method names and unique tokens (ISBN vs URLConnection) and missed the shared structural pattern of URL reading and logging.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may label as clone due to high boilerplate overlap: both functions open a URL, read lines, log output, and handle exceptions, despite different core purposes.
- 共享行为: Open URL stream；Read lines from input；Log output；Handle exceptions
- 行为差异: A uses regex to match ISBN pattern；B appends all lines to StringBuffer；A has retry logic on connection；A populates output map
- 修正建议: Add dataflow features to capture shared stream-read-log pattern；Include structural similarity over control flow；Use token-level attention with AST integration

### case_id=1339 FN partial_functionality

- 方法: `getDatasetsList` vs `httpRequestByPOST`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Retrieves a list of dataset names from a server via HTTP GET with caching.
- B 摘要: Sends an HTTP POST request with parameters and returns the concatenated response string.
- 静态失败原因: Low lexical overlap (token Jaccard 0.18) and significant structural differences (different HTTP clients, data structures, and control flow) led the model to focus on surface-level mismatches rather than the shared I/O pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often annotates Type-4 clones where core functionality of making an HTTP request and processing lines is similar, even with differing HTTP methods, return types, and error handling.
- 共享行为: Both perform an HTTP request and read the response line by line using BufferedReader.
- 行为差异: HTTP method: GET vs POST；Return type: List<String> vs String；Caching: present vs absent；Error handling: throws RuntimeException vs sets error codes and returns null
- 修正建议: Train model to recognize common I/O patterns like reading HTTP responses line-by-line across different APIs.；Use dataflow-sensitive embeddings that capture core operations like BufferedReader.readLine() and URL/HttpClient calls.

### case_id=1340 FP lexical_or_api_overlap

- 方法: `getWebByUrl` vs `checkForUpgrade`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Downloads a web page from a URL and saves it to a local file, with recursive URL extraction capped by depth.
- B 摘要: Checks for software upgrades by querying a remote license service and inserting upgrade records into a database, updating UI components accordingly.
- 静态失败原因: The model likely over-weighted shared API usage (URL, URLConnection, BufferedReader) and similar control flow patterns (try-catch, while loop), ignoring the distinct purpose and data handling.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB generally labels Type-3/4 clones as non-clones when the overall functionality differs significantly, despite API overlap. Here, the tasks are unrelated (web scraping vs. upgrade management), so BCB correctly marks them as non-clones.
- 共享行为: Both open a URL connection and read lines from an input stream；Both handle exceptions with try-catch；Both use BufferedReader and URL/URLConnection APIs
- 行为差异: Function A writes web content to a file; Function B processes upgrade metadata and interacts with a database；Function A recursively fetches additional URLs; Function B queries MAC addresses and SQL commands；Function B manipulates UI components and shows messages; Function A only outputs to console and file
- 修正建议: Incorporate data-flow or program dependence features to capture semantic intent；Use contrastive learning with API-usage vs. task-specific embeddings；Add training examples that contrast similar API usage with different goals

### case_id=1341 FP lexical_or_api_overlap

- 方法: `actionPerformed` vs `displayDiffResults`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Handles ActionEvent commands to set various application preferences (Graphviz, ImageMagick, font size, look-and-feel) and saves them using Suku.kontroller.putPref.
- B 摘要: Generates an HTML diff report from added/modified/deleted file tables and launches it in a browser.
- 静态失败原因: The model likely focused on superficial similarities like file I/O operations and preference-saving patterns in the truncated code, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB annotations typically require semantic similarity or shared functionality. These functions serve entirely different purposes (UI preferences vs. diff report generation), so they would not be considered clones even under broad Type-3/Type-4 criteria.
- 行为差异: Function A is an event handler for UI actions; function B is a private method for generating and displaying diff results.；Function A modifies application preferences; function B creates and writes to an HTML file.；Function A uses file choosers and sets UI components; function B uses file streams and writes HTML content.；Function A has no return value; function B throws IOException.
- 修正建议: Improve model sensitivity to overall program structure and task-specific logic vs. boilerplate patterns.；Use longer context or full function representations to avoid truncation artifacts.；Enhance training data with more diverse non-clone pairs having low lexical overlap.

### case_id=1342 FP lexical_or_api_overlap

- 方法: `importSequences` vs `startScript`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Imports sequences from a URL in FASTA-like format, parsing headers and sequences, storing them in lists.
- B 摘要: Reads a script from a URL specified by an attribute, appends lines to a dialog script buffer.
- 静态失败原因: Static BERT/GraphCodeBERT might have overemphasized the lexical overlap of common API calls like openStream(), readLine(), and IOException handling, while missing the distinct semantic contexts and data transformations.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB tends to label pairs as non-clones when the overall functionality and output are significantly different, even if they share some I/O patterns. Here, one is for sequence import with specific format parsing, the other for script loading, so BCB likely considered them non-clones.
- 共享行为: Both open a URL input stream and read text line by line；Both handle IOException；Both use standard Java I/O classes
- 行为差异: Function A uses ImportHelper to parse structured sequence data with delimiters, while B simply reads lines and appends；Function A stores parsed data in separate lists, B appends to a single string；Function A handles multiple entries with '>' delimiters, B reads one script file；Error handling differs: A prints stack trace and continues, B prints error and exits
- 修正建议: Train with more diverse negative examples that share API calls but differ in functionality；Incorporate data-flow or program-dependency information to capture structural differences；Use contrastive learning to penalize high similarity based on superficial API usage

### case_id=1343 FP lexical_or_api_overlap

- 方法: `handler` vs `checkForUpgrade`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Handles HTTP response by extracting values from HTML lines based on target configuration and updating a map.
- B 摘要: Checks for software upgrades by querying a license server, processing XML response, and updating database/UI.
- 静态失败原因: Static BERT likely over-relied on lexical overlap of common I/O patterns (URL, BufferedReader, while-loop) and ignored the distinct task-specific identifiers and overall semantic structure.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would label non-clone because the methods have entirely different purposes and implementations, despite sharing some I/O boilerplate.
- 共享行为: Both perform HTTP GET requests；Both read response line by line using BufferedReader；Both use InputStream and URL objects；Both catch IOException and MalformedURLException
- 行为差异: A is a generic content extraction handler; B is a specific upgrade checking logic；A updates a map with extracted substrings; B does UI visibility, database operations, license validation；A has no conditional branching beyond loop; B has multiple if-else conditions and loops；A is short and focused; B is very long with many statements
- 修正建议: Use method names and variable names to distinguish high-level intent；Incorporate data flow analysis to capture differences in operations；Add more discriminative features like database/UI operations；Train on harder negative examples with similar boilerplate but different semantics

### case_id=1344 FP boilerplate_overlap

- 方法: `main` vs `readAndRewrite`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Main method that reads a Prolog file, parses it, generates adapter classes and serialized data, and writes them to a JAR file.
- B 摘要: Method that reads a DICOM file, parses pixel data, and writes the processed image to another file.
- 静态失败原因: The model may have overgeneralized from common boilerplate patterns (file handling, try-catch, output streams) and ignored the domain-specific semantic content, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as not a clone because the overall functionality is completely different despite both being file I/O pipelines; the domain-specific logic is distinct.
- 共享行为: Both read a file from disk；Both perform domain-specific processing；Both write output to a file
- 行为差异: Different input formats: Prolog vs DICOM；Different processing logic: adapter generation vs pixel data handling；Different output: JAR with classes vs image file
- 修正建议: Incorporate domain-specific embeddings or task-aware features；Increase training data diversity to avoid false positives on I/O boilerplate；Use graph-based representations to capture data flow differences

### case_id=1345 FN partial_functionality

- 方法: `modifyApplicationMessage` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Modifies a properties file for a given locale by copying the English file if missing, then parsing lines to replace or append a message.
- B 摘要: Copies a file from source to destination using NIO FileChannel transferTo.
- 静态失败原因: Static BERT models rely on token-level similarity and method name; low Jaccard and different API usage (FileReader vs FileChannel) lead to a low score despite shared file copy sub-functionality.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as file manipulation utilities and the copy step in modifyApplicationMessage aligns with copyFile's primary function, making them a broad Type-4 clone.
- 共享行为: Both involve copying a file from one location to another
- 行为差异: modifyApplicationMessage includes complex logic for reading, parsing, and modifying properties file content；copyFile performs only a straightforward file copy with no content manipulation；modifyApplicationMessage uses old I/O streams while copyFile uses NIO channels
- 修正建议: Incorporate sub-function detection or hierarchical similarity measures；Use data augmentation to highlight cases where one method contains a sub-routine of another

### case_id=1346 FN boilerplate_overlap

- 方法: `getFile` vs `gerarTutorialPage`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads and modifies a WSDL file from a URL, saving to temp directory and returning its path.
- B 摘要: Generates a tutorial website by creating directory structure, copying CSS files, and writing HTML pages.
- 静态失败原因: Static BERT/GraphCodeBERT correctly predicted non-clone due to low token overlap (0.0979), different method names, and distinct overall functionality.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may have annotated as clone due to overlapping use of file I/O operations (FileChannel.transferFrom) and exception handling patterns, which are common boilerplate in Java file manipulation.
- 共享行为: Both use FileChannel.transferFrom for file copying
- 行为差异: A downloads file from network and modifies XML; B copies local CSS files and creates HTML；A returns file path; B returns boolean and shows dialogs；A handles specific exceptions (MalformedURLException, SAXException); B catches generic Exception
- 修正建议: Improve annotation guidelines to avoid labeling as clone when only low-level I/O patterns are shared；Use semantic similarity metrics that capture higher-level behavior

### case_id=1347 FN partial_functionality

- 方法: `writeFileType` vs `runInternal`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.4`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads URIs from a file, fetches each document, checks for RDF/OWL/RDFS keywords in first 100 lines, and writes the URI and classification type to an output file, handling errors by marking as BROKEN.
- B 摘要: Downloads and parses an OPDS catalog from a URL, handling redirects, timeouts, and errors, and either loads catalog entries or downloads a book file, with support for pagination.
- 静态失败原因: The functions have low token Jaccard similarity (0.11588) and belong to different projects (one general utility, one Android app). Static models rely heavily on lexical overlap and may miss higher-level structural or behavioral similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as 'network-based file reading/writing with error handling' tasks, ignoring domain-specific processing, due to broad Type-3/4 clone definition.
- 共享行为: Both open URL connections and read data from the network.；Both handle exceptions and write output (to file or callback).；Both use BufferedReader and do line-by-line reading.
- 行为差异: A classifies documents by RDF keywords; B downloads and parses OPDS catalog or books.；A writes to a file; B updates UI and calls callback with parsed data.；A reads URIs from a file; B uses a fixed URL or next links.；B has complex HTTP handling (redirects, timeouts, content-type) absent in A.
- 修正建议: Incorporate data-flow analysis to capture common patterns like URL connection + read + write.；Use method-level embeddings that capture semantic structure rather than exact tokens.；Include functional role annotations (e.g., 'download', 'classify') to disambiguate.

### case_id=1348 FP lexical_or_api_overlap

- 方法: `init` vs `perform`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Initializes a socket connection by performing an MD5-based handshake with a slave server, validates the slave response, and adds the slave to the connection manager.
- B 摘要: Processes an HTTP request in a Struts action to classify a concept by building XML, making an HTTP URL connection to another server, parsing the XML result, and forwarding to a success or failure view.
- 静态失败原因: The model likely overemphasized overlapping API calls (e.g., BufferedReader, InputStreamReader, loops, string manipulations) and failed to capture the high-level semantic difference between a socket-based authentication protocol and a Struts action for concept classification.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels these as non-clones because they have different method signatures, different domains (network initialization vs web request handling), and no shared functionality beyond common Java boilerplate.
- 行为差异: Function A performs network handshake and authentication; function B processes a web request for concept classification.；Function A uses sockets and MD5; function B uses URLConnection and XML parsing.；Function A initializes a slave connection; function B handles a form submission and forwards to a JSP.；Function A returns void; function B returns an ActionForward.
- 修正建议: Improve training with more diverse examples to reduce reliance on surface-level API tokens.；Incorporate control flow and data flow features that differentiate network I/O from HTTP-based I/O.；Use more sophisticated semantic similarity measures that account for method intent, not just token overlap.

### case_id=1349 FN partial_functionality

- 方法: `runScript` vs `PageLoader`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a file from a URL byte by byte and returns its content as a string, returning 'error!' on exception.
- B 摘要: Reads from a URL line by line and stores the concatenated lines into an instance variable, throwing an exception on failure.
- 静态失败原因: Low token overlap (Jaccard=0.195), different method signatures (return vs void), and different reading patterns (byte vs line) make it hard for static models lacking deep semantic understanding.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: Both functions achieve the same high-level goal: fetching web content into a string, with differences in I/O granularity and error handling considered minor for a Type-3 clone.
- 共享行为: Open a URL connection；Read entire content from URL；Produce a single string from the content
- 行为差异: A reads byte-by-byte, B reads line-by-line；A returns the string, B assigns to a field；A handles errors by returning an error string, B throws exception
- 修正建议: Train on more diverse I/O patterns with varying granularity；Incorporate dataflow analysis to capture URL reading intent；Consider broader context like class fields or usage patterns

### case_id=1350 FN boilerplate_overlap

- 方法: `login` vs `load`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.6`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Logs into LOLA service by sending email and password via POST, returns session ID.
- B 摘要: Loads XML data from pastebin via GET using an ID, returns XML string.
- 静态失败原因: Low token similarity (0.2) and different method names/domain keywords caused the model to miss the structural similarity in the HTTP request pattern.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may consider them clones due to shared boilerplate of URL connection and BufferedReader usage, despite different domain-specific operations.
- 共享行为: Both perform HTTP requests；Both read response line by line；Both handle exceptions
- 行为差异: Login uses POST with URL-encoded parameters, load uses GET；Login extracts session ID from first line, load concatenates all lines；Login sets internal session variable, load does not
- 修正建议: Train on Type-3 clones with low token overlap but similar control flow；Incorporate data flow graphs to capture I/O patterns

### case_id=1351 FP other

- 方法: `main` vs `test`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.98`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Main method that reads a Prolog file, parses it, generates adapter classes, and writes them to a JAR file.
- B 摘要: Test method that reads an XML traffic model, initializes a simulation engine, runs it for 10 minutes, and prints vehicle states.
- 静态失败原因: Static BERT/GraphCodeBERT likely failed due to focusing on superficial lexical cues (e.g., common Java idioms like try-catch, System.out.println, loops) while missing the deep semantic mismatch. The very low token Jaccard (0.069) suggests the prediction was a random or noise-driven false positive.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely labeled as non-clone because the functions have completely different purposes, no overlapping domain logic, and only trivial structural similarities (loops, I/O).
- 共享行为: Both involve file I/O；Both contain loops；Both use try-catch error handling；Both print output to console
- 行为差异: Domain: code generation vs. traffic simulation；Input: Prolog file vs. XML resource；Output: JAR file vs. console output；Logic: complex parser/class generation vs. simulation stepping
- 修正建议: Improve model sensitivity to low token overlap；Incorporate structural or data-flow analysis；Use domain-specific knowledge to distinguish functional purpose

### case_id=1352 FN partial_functionality

- 方法: `copyFile` vs `getFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a local file to another local file using NIO FileChannel transferTo and returns success flag.
- B 摘要: Downloads a WSDL file from a URL, modifies its wsdlsoap:address location, saves it locally, and returns the file path; throws AxisFault on errors.
- 静态失败原因: The static model likely focused on differences in method signature, return type, function length, and overall different functionality (copy vs. download+modify), missing the low-level I/O pattern similarity that BCB considered.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considers both as file copying/downloading operations that use similar NIO channel transfer mechanics, thus labeling as Type-4 clone based on shared file I/O pattern.
- 共享行为: Both use FileChannel to transfer data between input and output streams.；Both handle IOException (though differently).
- 行为差异: A copies between two local files; B downloads from URL to local file and then modifies XML.；A returns boolean; B returns String.；A catches exceptions silently; B logs and throws AxisFault.；A is private; B is public static.
- 修正建议: Train on finer-grained semantic roles or sub-patterns like file transfer.；Use graph-based representations capturing data flow of I/O operations.；Incorporate domain knowledge of common I/O patterns.

### case_id=1353 FP lexical_or_api_overlap

- 方法: `handleHandshake` vs `GetResponse`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Validates a Minecraft handshake packet by checking username and optionally contacting a session server to decide on login or shutdown.
- B 摘要: Reads an HTTP GET response from a URL and returns the content as a string.
- 静态失败原因: Static BERT models may overemphasize lexical overlap (URL, BufferedReader, InputStream) and the general pattern of reading from a URL, ignoring the distinct control flow and domain-specific operations.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would not consider them clones because they implement entirely different business logic despite sharing some API usage patterns.
- 共享行为: Both use URL and BufferedReader/InputStreamReader for HTTP data retrieval；Both include try-catch for IOException
- 行为差异: A has multiple control flow branches (validation, login, shutdown), B returns a string or null；A contacts a specific Minecraft session server with query parameters, B takes any URL；A has side effects (sending packets, network shutdown), B is a pure getter
- 修正建议: Incorporate control flow and dataflow analysis into the model；Use graph-based representations like AST or CG；Train on more diverse examples with similar API usage but different semantics

### case_id=1354 FP lexical_or_api_overlap

- 方法: `getVersion` vs `PhoneSetImpl`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches a version string from a hardcoded URL by reading the last line.
- B 摘要: Constructor that reads a URL to parse phone-set entries, filtering lines starting with '***'.
- 静态失败原因: The model over-relied on lexical overlap (e.g., 'BufferedReader', 'URL', 'readLine') and structural similarity (while loop, try-catch) while ignoring semantic differences in purpose, return type, and data handling.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clone because the methods serve entirely different purposes (version retrieval vs. phone-set construction) with distinct data processing logic, despite shared I/O boilerplate.
- 共享行为: Both read from a URL using BufferedReader and InputStreamReader.；Both loop over lines with readLine() until null.；Both close the reader after reading.
- 行为差异: A returns a String (version), B is a constructor that populates a HashMap.；A reads only the last line, B processes every non-ignored line via parseAndAdd.；A has exception handling returning null, B throws IOException.；A uses a hardcoded URL, B takes URL as parameter.
- 修正建议: Incorporate control-flow and data-flow analysis to differentiate operations on read lines.；Use method name, return type, and exception handling as additional features.；Train on broader context including surrounding code or method signatures.

### case_id=1355 FP partial_functionality

- 方法: `postData` vs `loadURL`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends POST data to a specified URL and discards the response.
- B 摘要: Loads content from a URL optionally with authentication, writes to a temporary file while updating a status label.
- 静态失败原因: The static model may have overemphasized the common subsequence (openConnection, BufferedReader, reading lines) and missed the differing I/O operations (output stream vs. file writing) and side effects (UI update), leading to a false positive.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely considers these non-clones because their core purposes differ (posting data vs. loading URL content to file) and the structural similarity is limited, despite some shared I/O patterns.
- 共享行为: Both open a URL connection and read the response via BufferedReader.
- 行为差异: A sends data via POST, B does not.；A discards response, B writes to a file.；B handles authentication and UI update; A does not.；A uses default parameters for protocol, host, form; B takes URL directly.
- 修正建议: Incorporate dataflow analysis to track whether the connection is used for input or output.；Add pre-training on tasks that distinguish data sending from data receiving.；Use more fine-grained structural matching that considers method purpose and side effects.

### case_id=1356 FN partial_functionality

- 方法: `copyFile` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a local file using FileChannel.
- B 摘要: Downloads a KMZ file from a given URL and extracts its ZIP entries to files.
- 静态失败原因: The model relied on lexical and structural overlap, which is very low (token Jaccard=0.0886), and failed to capture the high-level semantic similarity of file copying, leading to a false negative.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considered these as clones because both perform file I/O operations that transfer bytes from a source to a destination, a high-level functional similarity that fits Type-4 clone criteria.
- 共享行为: Both read data from an input source and write to an output file using streams.
- 行为差异: A uses FileChannel.transferTo for efficient copying, B uses manual buffer read/write with ZipInputStream.；A copies a single local file, B downloads from a URL and extracts multiple files from a ZIP archive.；A handles only local files, B handles HTTP URLs and ZIP decompression.
- 修正建议: Incorporate code summarization or high-level functional abstractions.；Use data-flow analysis to detect common I/O patterns.；Train on more diverse clone examples that include Type-4 functional similarity.

### case_id=1357 FN benchmark_preference_bias

- 方法: `loadMFileViaWeb` vs `invoke`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Loads a MATLAB function file from a web URL by reading the content and parsing it into a UserFunction object.
- B 摘要: Invokes a remote method via HTTP POST, reads the JSON response, and deserializes it into the expected return type, with retry on connection timeout.
- 静态失败原因: Static BERT/GraphCodeBERT likely correctly identified the functional dissimilarity based on low token overlap and distinct operations, thus predicting non-clone, which disagrees with BCB's broad label.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have considered these clones due to the common boilerplate pattern of network I/O and string building, overlooking the significant differences in data processing and purpose.
- 共享行为: Both open an HTTP connection to read data；Both read input line by line using BufferedReader；Both build a string from the read lines；Both handle exceptions
- 行为差异: A uses simple URL.openStream (GET-like), B uses HTTP POST with JSON body；A parses content as MATLAB code, B deserializes JSON；A returns a UserFunction, B returns generic Object；B includes retry logic on ConnectTimeoutException, A does not
- 修正建议: Re-evaluate BCB annotation for this pair; consider if Type-4 clone criteria are too broad.；For model improvement, use hierarchical similarity thresholds that allow acceptance of Type-4 clones when overall data flow patterns match.

### case_id=1358 FP boilerplate_overlap

- 方法: `getWebPage` vs `readZoneIDs`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a web page from a URL and returns its content as a concatenated string.
- B 摘要: Reads a zone file resource, parses each line as an integer, and returns a set of those integers.
- 静态失败原因: The static BERT model likely overfit to the common boilerplate pattern of opening a URL stream and reading lines, ignoring the semantic differences in input/output types and line processing logic. The low token Jaccard suggests lexical overlap is low, but the structural API sequence (URL.openStream, readLine) may have triggered a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB annotations focus on functional equivalence. Despite structural overlap in reading lines, the functions serve entirely different purposes (web scraping vs configuration parsing) and produce different output types, so BCB would label them as non-clones.
- 共享行为: Both open an InputStream from a URL and use a reader to read lines in a while loop；Both catch exceptions during I/O operations
- 行为差异: Return type differs: String vs HashSet<Integer>；Input type differs: URL object vs String filename；Line processing differs: concatenation vs integer parsing；Error handling differs: throws Error vs prints stack trace
- 修正建议: Enhance training with more diverse examples that share boilerplate but differ in semantics；Incorporate type information and method signatures as features；Use dataflow analysis to capture how variables are used (e.g., concatenation vs parsing)；Employ contrastive learning to differentiate similar-but-different functionalities

### case_id=1359 FP boilerplate_overlap

- 方法: `getLinksFromURLFast` vs `postXml`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Parses HTML from a URL to extract hyperlinks and anchor texts.
- B 摘要: Sends an HTTP POST request with XML content and returns the response body.
- 静态失败原因: The static model likely over-weighted common boilerplate tokens like 'URLConnection', 'BufferedReader', 'StringBuilder', and 'getInputStream', causing it to miss the fundamental semantic difference between data extraction and data posting.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels non-clone when the functions have distinctly different high-level purposes, even if they share boilerplate I/O patterns. Here, one is a web scraper for links, the other is an XML poster, so BCB correctly assigns non-clone.
- 共享行为: Both open a URLConnection to a given URL.；Both read from an input stream using BufferedReader.；Both use StringBuilder to accumulate the response content.
- 行为差异: Function A uses regex to parse HTML and extract links and texts, while Function B sends XML data via POST.；Function B sets request properties (Content-Type, Accept, SOAPAction) and enables output, while A only reads.；A returns a Vector array of links and texts; B returns a String response.；A includes timing checks and prints debug info; B does not.
- 修正建议: Incorporate method-level semantic context (e.g., method name embeddings) to distinguish high-level tasks.；Use control flow and API call patterns (e.g., presence of 'setRequestMethod', 'setDoOutput', regex parsing) to differentiate.；Train with more diverse examples that separate I/O boilerplate from core functionality.

### case_id=1360 FP boilerplate_overlap

- 方法: `createHTML` vs `getFrameworkFactory`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Builds an HTML page for different request types, reading CSS from a resource and processing dashboard content.
- B 摘要: Loads the OSGi framework factory from a service resource file and instantiates it via reflection.
- 静态失败原因: Overlap in tokens (BufferedReader, URL, getResource) and similar control flow (resource loading loop) led the model to falsely consider them similar.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels these as non-clones because their high-level functionality differs significantly, despite sharing a common resource-reading boilerplate pattern.
- 共享行为: Both read a resource file line by line using BufferedReader and InputStreamReader.；Both use getClassLoader().getResource() to obtain a URL to a resource file.
- 行为差异: Function A constructs and returns an HTML string; Function B returns a FrameworkFactory instance.；Function A handles multiple page types with a switch statement; Function B parses a service file for a class name.；Exception handling differs: A logs errors, B throws an exception.；The content and structure of the read files are entirely different.
- 修正建议: Incorporate semantic role labeling to distinguish resource-reading as boilerplate vs. core logic.；Use dataflow analysis to capture the purpose of the extracted data (HTML vs class name).；Train on more diverse non-clone pairs with similar boilerplate to reduce false positives.

### case_id=1361 FP lexical_or_api_overlap

- 方法: `actionPerformed` vs `copyFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Handles GUI events for a settings dialog, including file choosers and preference updates for various tools like Graphviz and ImageMagick.
- B 摘要: Copies a file from a source path to a destination path, creating parent directories if necessary.
- 静态失败原因: The model likely focused on lexical overlap (e.g., both contain 'File', 'Exception', try-catch) and missed the vast difference in overall purpose and control flow. The long length of code_a may have caused the model to lose context, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB's annotation guidelines typically require similar functionality for clones; these two functions have no overlapping behavior beyond basic file operations, which is too broad. The low token jaccard (0.095) and different method names further support non-clone.
- 行为差异: code_a is a GUI event handler; code_b is a file I/O utility.；code_a involves user interaction via file chooser; code_b reads and writes bytes.；code_a updates UI components and stores preferences; code_b has no UI interaction.；code_a handles many commands; code_b performs a single task.
- 修正建议: Incorporate method names and class context into the model.；Use structural features like control flow graphs to distinguish GUI event handlers from utility methods.；Improve handling of long functions with better attention mechanisms or hierarchical representation.

### case_id=1362 FN partial_functionality

- 方法: `sendExceptionToServer` vs `issueCommandToServer`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends exception details (stack trace, version, user info) to a remote server via HTTP POST and prints the outcome.
- B 摘要: Sends a command and a change capsule to a remote server via HTTP POST and returns the server response.
- 静态失败原因: The low token Jaccard (0.25) and different method names, parameter names, and internal logic cause the model to focus on lexical differences, missing the structural similarity of the HTTP POST pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels as clones when functions share the same high-level task (sending data to a server via HTTP POST) even if payload and response handling differ, as seen in Type-3/Type-4 clone annotations.
- 共享行为: Both open an HTTP URLConnection；Both write URL-encoded parameters to the output stream；Both read the server response from the input stream
- 行为差异: A sends multiple fixed parameters including secret and exception details; B sends only command and capsule parameters；A does not return a value but prints based on response; B returns the response string；A catches IOException and prints error; B throws IOException
- 修正建议: Use a model that captures API call sequences and control flow, e.g., graph-based models or AST-based models with data flow；Include features like connection setup, write, and read operations as indicators of similar behavior；Train on pairs with low lexical overlap but high behavioral similarity (e.g., different parameter names but same pattern)

### case_id=1363 FN benchmark_preference_bias

- 方法: `createOutputStream` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Creates a BufferedWriter that writes a zip file from an input zip, skipping 'content.xml' entry and appending it at the end.
- B 摘要: Launches a NexOpen project configuration, processing Maven pom files, setting Hibernate properties, and triggering a build action.
- 静态失败原因: The model correctly predicted non-clone (token Jaccard 0.049), but BCB label is 1. The failure is a benchmark annotation inconsistency, not a model error.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled it a clone due to both methods using streams and file operations, but the overall functionality is completely different.
- 共享行为: Both involve file I/O using Java streams.
- 行为差异: Function A processes zip files (reading and writing compressed entries).；Function B manages Eclipse project launch configurations, validates project structure, and executes build actions.；Function A returns a BufferedWriter; Function B returns void.；Function B interacts with Eclipse workspace, plugins, and Maven; Function A is standalone file processing.
- 修正建议: Re-evaluate BCB annotation for this pair; it appears to be a false positive clone annotation.；Ensure benchmark guidelines are strictly applied to avoid over-generalization.

### case_id=1364 FN benchmark_preference_bias

- 方法: `modifyApplicationMessage` vs `getProjectTreeData`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.6`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Modifies a localized properties file by replacing or appending a message key-value pair.
- B 摘要: Downloads an XML file from a server, parses it, and extracts project tree data into a 2D array.
- 静态失败原因: Static BERT/GraphCodeBERT models rely on token embeddings and may capture surface-level similarities but not deep semantic intent. Given the low token Jaccard and different method signatures, the model correctly identified them as non-clones. The mismatch with BCB label suggests the BCB annotation may be a false positive.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled these as clones due to superficial structural similarities: both open input streams, read data, process it line-by-line or node-by-node, and write output. Despite different domains and data formats, the high-level pipeline of input-process-output might be considered Type-4 by some annotators.
- 共享行为: Both perform file I/O operations (reading/writing files).；Both use try-catch blocks for exception handling.
- 行为差异: Function A modifies an existing properties file; Function B downloads and parses XML.；Function A writes back changes to the file; Function B returns a String array.；Function A deals with localization strings; Function B deals with project hierarchy data.；Function A uses BufferedReader for line-by-line reading; Function B uses DOM parser for XML.
- 修正建议: Improve training data by filtering out false positive clones from benchmark.；Incorporate task-specific semantic understanding, e.g., through data flow analysis or API call sequences.

### case_id=1365 FN partial_functionality

- 方法: `readPage` vs `register`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a URL and returns its content as a string, optionally filtering out lines starting with '#'.
- B 摘要: Registers a user by validating input, encoding password, setting metadata, calling a PHPBB URL for forum user creation, persisting via entityManager, and sending a confirmation email.
- 静态失败原因: Low token Jaccard and differing control flows; the shared subpattern is a small portion of B, so attention-based models likely did not capture it as semantically equivalent.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have considered the common pattern of opening a URL and reading lines as a Type-4 clone, but this is a minor part of B's functionality, making the label questionable.
- 共享行为: Both open a URL connection and read lines from a BufferedReader.
- 行为差异: Function A only reads and returns page content; B performs many unrelated steps like password encoding, database persistence, email sending.；A has an optional comment filtering; B has complex error handling and multiple side effects.；The scale and purpose differ vastly: simple retrieval vs. multi-step registration.
- 修正建议: Use data-flow-aware embeddings to detect similar subsequences.；Incorporate structure-based matching for common I/O idioms.

### case_id=1366 FP partial_functionality

- 方法: `readRemoteFile` vs `readUNI`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads remote file line by line and returns concatenated string.
- B 摘要: Reads remote tab-delimited file, parses each line, and populates a vector with id and description.
- 静态失败原因: Static BERT models may over-rely on common boilerplate patterns (URL opening, InputStream, line reading) and miss the significant difference in data processing logic (concatenation vs tab parsing). The token overlap is low but the structural similarity of the I/O pattern could mislead the model.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB typically requires strong Type-3/Type-4 semantic similarity; these functions have fundamentally different output behaviors (string concatenation vs structured parsing), so they are considered non-clones.
- 共享行为: Both read from a URL via InputStream；Both iterate over lines；Both handle exceptions
- 行为差异: Function A returns a concatenated string; Function B returns void and populates a vector；Function A uses BufferedReader; Function B uses Scanner with delimiter parsing；Function A concatenates all lines; Function B parses tab-separated values；Function A has different exception handling (EOFException, IOException prints); Function B catches MalformedURLException and generic Exception with printStackTrace
- 修正建议: Incorporate dataflow analysis to distinguish between concatenation and parsing operations；Train on more diverse examples with varying output semantics；Consider method signature information (return type, parameters) as additional features

### case_id=1367 FN benchmark_preference_bias

- 方法: `doGet` vs `run`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Handles HTTP GET request for a portal page, retrieves page by ID or name, checks user visibility and editability, logs request, and renders HTML output with caching.
- B 摘要: Downloads files from a Hadoop distributed filesystem directory to a local file output stream, iterating over files and copying bytes.
- 静态失败原因: The static BERT model failed to recognize the broad structural similarity that BCB considers, focusing instead on the clear semantic differences in domain and logic, leading to a non-clone prediction.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may label these as clones due to structural similarity in the 'fetch and output' pattern, common use of I/O streams and try-catch blocks, and potential classification as Type-3/Type-4 clones based on partial functionality overlap.
- 共享行为: Both perform file I/O operations (reading files and writing to streams).；Both use try-catch-finally for resource management.；Both check conditions (null checks, directory check) and report errors.；Both have logging (System.err or myLogger).
- 行为差异: Different domain: web vs Hadoop.；Different input: HTTP request parameters vs command line arguments.；Different output: HTTP response vs local file output stream.；Different error handling: HTTP error codes vs exit codes and stderr.
- 修正建议: Incorporate domain-agnostic structural patterns for Type-3/Type-4 clone detection.；Use contrastive learning to balance strict and broad similarity definitions.；Evaluate model on BCB annotations to align with their preference.

### case_id=1368 FN benchmark_preference_bias

- 方法: `copy` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Copy a file character by character using FileReader and FileWriter.
- B 摘要: Launch a NexOpen Eclipse plugin configuration, handling pom.xml files and Hibernate settings.
- 静态失败原因: The static model relied on lexical and structural features, which showed very low token overlap (Jaccard 0.047) and different method names, leading to a non-clone prediction. It failed to capture the abstract commonality of file I/O that BCB annotators might have considered.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB annotators may have considered both functions as 'copying' or 'writing' data from one source to another, thus labeling them as Type-4 semantic clones despite low lexical overlap.
- 共享行为: Both perform file I/O operations: reading a file and writing to an output stream or file.
- 行为差异: Function A is a simple file copy with no error handling; Function B is a complex launch method with XML processing, property setting, project management, and multiple error conditions.；Function A has a single loop; Function B has nested conditionals, callbacks, and resource management.
- 修正建议: Incorporate higher-level semantic abstractions, such as recognizing common I/O patterns across different contexts.；Use data-flow analysis to detect similar operations on streams and files.

### case_id=1369 FN partial_functionality

- 方法: `modifyApplicationMessage` vs `cpFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Modifies a Properties file for internationalization, copying a default English file if necessary and updating a specific message key-value pair.
- B 摘要: Copies a source file to a target file with options to handle directory targets, replace existing files, and use a custom buffer size.
- 静态失败原因: Static models like BERT or GraphCodeBERT may rely on lexical overlap and overall function signature; the low token Jaccard (0.207) and differing method names suggest non-clone, but they miss the shared sub-behavior of file copy due to limited ability to abstract subroutines.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider these as clones due to the common file copying sub-operation (the copy of the English file in A parallels the core of B), and both are file-oriented utility methods with similar structure (open streams, read/write, close), fitting Type-4 semantic similarity.
- 共享行为: Both perform file copying operations using input/output streams；Both check file existence before operations；Both handle exceptions related to file I/O
- 行为差异: Function A modifies file content (properties parsing and rewriting), while Function B only copies bytes verbatim；Function A writes modified content back, whereas Function B simply duplicates file；Function A includes logic for appending missing keys, absent in B
- 修正建议: Incorporate data-flow analysis to detect subroutines like file copy；Use graph representations that capture control and data dependencies；Include explicit annotations for common I/O patterns

### case_id=1370 FN benchmark_preference_bias

- 方法: `doGet` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Handles HTTP GET request for a portal page, including authentication, logging, and optional caching of rendered output to a file.
- B 摘要: Copies a source file to a destination file using Java NIO.
- 静态失败原因: The static model correctly predicted non-clone because the functions have very low token overlap and distinct control flows; the BCB label seems erroneous.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as clone due to both functions performing some file reading/writing, but the context and primary functionality are completely different.
- 共享行为: Both involve file I/O operations.
- 行为差异: Function A is an HTTP servlet handler with complex logic including user authentication, page retrieval, logging, and conditional caching.；Function B is a simple utility to copy a file using NIO channels.；Function A's file writing is only a small conditional part, while Function B's entire purpose is file copying.
- 修正建议: Review BCB annotation guidelines and possibly correct the label.；Use more representative examples for evaluating clone detection models.

### case_id=1371 FN partial_functionality

- 方法: `sendExceptionToServer` vs `getContent`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends an exception report to a server via HTTP POST and prints the server's response.
- B 摘要: Executes an HTTP request and returns the response body as a string.
- 静态失败原因: Static BERT models rely heavily on lexical and token-level similarity; the low Jaccard similarity (0.168), different method names, different HTTP libraries (URLConnection vs HttpClient), and distinct control flow structures likely caused the model to miss the underlying functional similarity in HTTP communication.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this as a clone because both functions perform HTTP requests and process the response, sharing a common sub-task of reading an HTTP response, which is considered a partial functionality similarity under broad Type-3/Type-4 criteria.
- 共享行为: Both involve HTTP communication and reading the response line by line.
- 行为差异: Function A sends a POST request with URL-encoded data; function B executes a generic request (likely GET).；Function A outputs results via System.out; function B returns the response string.；Function A includes specific error-reporting logic; function B is a generic content fetcher.；Function A uses URLConnection; function B uses HttpClient.
- 修正建议: Incorporate structural features like control-flow graphs or data-flow graphs to capture shared sub-patterns.；Use API usage patterns (e.g., reading from an HTTP response) as features rather than relying solely on tokens.；Train with more diverse examples of HTTP-related clones to improve generalization.

### case_id=1372 FP long_range_semantics

- 方法: `main` vs `readData`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `static_summary_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Copies a file from source to destination using NIO channels.
- B 摘要: Reads and parses configuration data from a file, populating various sets and hash maps.
- 静态失败原因: The model likely focused on superficial syntactic similarities (while loop, I/O methods) and missed the vast semantic difference due to the length and complexity of function B, leading to a false positive.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB would label as non-clone because the functions serve completely different purposes: file copy vs. data initialization/parsing.
- 共享行为: Both use I/O operations；Both contain while loops
- 行为差异: A simply copies bytes from one file to another；B reads and parses structured data, builds multiple data structures；A is short and straightforward, B is long and complex
- 修正建议: Improve model's capability to handle long-range dependencies；Incorporate data flow analysis to differentiate I/O patterns

### case_id=1373 FN benchmark_preference_bias

- 方法: `gzip` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.2`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Compresses files from a directory into a GZIP file using fixed paths.
- B 摘要: Launches a Maven-based Eclipse project configuration, handling XML profiles, properties, and reverse engineering file setup.
- 静态失败原因: The static BERT model correctly predicted non-clone given the low token Jaccard (0.0448) and vastly different semantics; the BCB label likely represents an annotation error or a very lenient clone criterion.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled these as clones due to superficial similarities in using file streams and performing file operations, accepting broad Type-4 functional similarity.
- 共享行为: Both use file I/O streams (FileInputStream, FileOutputStream, ByteArrayOutputStream)；Both perform file creation or writing operations
- 行为差异: Code a is a simple, static gzip compression routine with fixed file paths; code b is a complex, instance method for Eclipse plugin launch configuration；Code a uses GZIP compression; code b does not involve compression；Code b includes conditional logic, XML handling, property files, and project workspace interactions; code a has no such complexity；Code a is buggy (reading a directory as FileInputStream); code b is well-structured for its purpose
- 修正建议: Re-evaluate the BCB annotation for this pair to confirm if it truly represents a clone under their guidelines；Improve static models to ignore shallow file I/O token overlap and focus on deeper semantics

### case_id=1374 FP partial_functionality

- 方法: `readReferenceText` vs `SRWGuiClient`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a text file from a URL and returns its content as a string.
- B 摘要: Constructs a GUI browser window that reads and optionally transforms XML from a URL and displays HTML content.
- 静态失败原因: The model likely focused on the lexical overlap of reading from URL, using BufferedReader, and similar control flow, missing the semantic context: one is a simple reader, the other is a GUI constructor with extensive UI and XML processing.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely labeled this as non-clone because the overall functionality is entirely different. The commonality of reading from a URL is incidental and not sufficient for clone classification.
- 共享行为: Both open a URL and read input line by line using BufferedReader.；Both handle IOExceptions with error logging.
- 行为差异: Function A is a simple file reader returning a string; Function B sets up a complex GUI and displays content in a JEditorPane.；Function B performs XML parsing and XSLT transformation; Function A does not.；Function A throws NoContentException on failure; Function B catches exceptions and shows a warning.；Function B includes extensive UI setup and event handling; Function A has none.
- 修正建议: Incorporate structural analysis (e.g., AST-based) to differentiate between a simple utility method and a complex constructor.；Use longer context or explicit semantic role detection.；Train with hard negatives that have high lexical overlap but different functionality.

### case_id=1375 FN partial_functionality

- 方法: `testNetworkHTTP` vs `addQDInformation`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: A test method that makes multiple HTTP GET requests to various URLs and reads response lines without processing them.
- B 摘要: A method that reads a local or remote data file (qdinfo.dat) via HTTP, parses lines starting with 'pg' or 'pt', and updates internal project information.
- 静态失败原因: Static BERT models like CodeBERT rely heavily on lexical overlap and may miss the high-level structural similarity due to low token Jaccard (0.17) and differences in variable names and specific URL strings.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considers this a clone due to the shared pattern of network I/O, reading lines from HTTP responses, and similar structural elements like URL creation and BufferedReader usage, accepting broad Type-3/Type-4 similarity.
- 共享行为: Both use HTTP connections to fetch data from URLs.；Both read lines using BufferedReader in a loop.；Both handle IOException.
- 行为差异: A makes multiple requests to different hardcoded URLs; B makes at most one request to a specific constructed URL.；A does not parse or use the read data; B parses lines and updates internal state.；A is a test method with no side effects; B modifies internal fields (_qdDate, _qdValue).
- 修正建议: Use a model that captures control and data flow, such as graph-based representations (e.g., AST, CFG).；Incorporate structural similarity metrics that are tolerant to lexical variations.；Train with more diverse examples of Type-3/Type-4 clones that share partial functionality.

### case_id=1376 FP lexical_or_api_overlap

- 方法: `callApiPost` vs `downloadFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Makes an HTTP POST request with parameters, checks expected response code, and returns the response InputStream.
- B 摘要: Downloads a file from a URL to a local file path, tracking download progress, and returns a boolean success flag.
- 静态失败原因: The model likely overemphasized lexical overlap (e.g., URL, HttpURLConnection, InputStream) and the sequential structure of opening a connection and reading data, missing the high-level semantic difference.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB considers these non-clones because they have completely different functional purposes (API call vs file download) despite sharing common networking boilerplate.
- 共享行为: Both use URL connections and stream I/O；Both handle IOExceptions
- 行为差异: A is for API calls with POST and custom headers/timeouts; B is for file download with GET and progress updates；A returns an InputStream; B returns boolean and writes to file；A checks response code and throws specific exception; B uses generic Exception and returns true on success
- 修正建议: Incorporate control-flow or data-flow analysis to capture structural differences；Use higher-level semantic embeddings that better represent intent；Add training examples with fine-grained functional distinctions

### case_id=1377 FN partial_functionality

- 方法: `addIDs` vs `getURLContent`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches HTML from a specific database URL to extract metabolite information and updates a PeakListRow object, returning a score.
- B 摘要: Fetches the content of a given URL and returns it as a string.
- 静态失败原因: Static models like CodeBERT rely on token similarity and overall code structure. Here, token Jaccard is low (0.14) and control flow differs greatly (A has many conditionals and API calls). The model focused on the distinct high-level logic and failed to recognize the shared URL reading sub-pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB annotators often consider functional similarity in terms of overall task (both involve fetching data from a URL and reading it). Even though A does additional processing, the core sub-task of downloading URL content is present in both, making them Type-4 clones.
- 共享行为: Both create a URL object, open a connection, and read lines using BufferedReader.
- 行为差异: A returns an integer score after complex parsing and updating a row; B returns the entire raw content as a string.；A contains specific HTML parsing logic for multiple ID formats; B is a simple read and concatenate.；A is bound to a particular website and data schema; B is generic.
- 修正建议: Train models with contrastive learning on cloned sub-tasks.；Use data flow graphs to capture common sub-computations.；Incorporate clone annotations that consider partial functionality.

### case_id=1378 FP lexical_or_api_overlap

- 方法: `getRequestContent` vs `main`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `1.0`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads the first line from a given URL and returns it as a string.
- B 摘要: Reads all lines from a hardcoded URL and prints each line to standard output.
- 静态失败原因: The model likely overemphasized lexical and structural overlap (similar API sequences: URL, BufferedReader, InputStreamReader, readLine, close) while ignoring differences in return type, control flow, and output usage.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would label as non-clone because the functions have different signatures, control flow, output behavior, and input handling, despite sharing core URL-reading API calls. Type-4 requires high input-output similarity, which is absent.
- 共享行为: Both open an HTTP URL and read textual content line by line using BufferedReader and InputStreamReader.
- 行为差异: Function A takes a URL parameter and returns the first line; Function B uses a hardcoded URL, reads all lines, and prints them, returning void.；Function A uses HttpURLConnection with explicit connect/disconnect; Function B uses URL.openStream().；Function A reads only one line; Function B reads all lines in a while loop.
- 修正建议: Incorporate dataflow analysis to track variable usage and output behavior.；Train model to differentiate method signatures and return types.；Add contrastive examples with similar API usage but different semantics.

### case_id=1379 FN benchmark_preference_bias

- 方法: `unzipModel` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Unzips a zip archive to a specified directory using ZipInputStream.
- B 摘要: Builds a website for editing by processing page templates and transforming XML to HTML files.
- 静态失败原因: The static model correctly identified low lexical overlap (Jaccard=0.09) and structural dissimilarity, leading to a non-clone prediction. It failed to match the BCB label because the label itself may be erroneous or based on subjective interpretation.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled both as clones due to broad Type-4 similarity in file processing and exception handling, despite vastly different algorithms and purposes.
- 共享行为: Both involve reading from input streams and writing to output streams；Both use file I/O operations and handle exceptions
- 行为差异: A is a simple extraction of a zip file; B is a complex multi-step process involving DOM parsing, XSL transformations, and string replacements；A handles only one zip entry at a time; B iterates over a vector of pages and processes each with many sub-steps；A writes to a single file per entry; B writes to multiple output files with additional post-processing
- 修正建议: Re-evaluate BCB label for this pair to ensure it aligns with functional equivalence or Type-3/Type-4 clone definitions；Improve annotation consistency by providing clearer guidelines for partial functionality clones；Consider using code-level semantic similarity metrics beyond simple token overlap

### case_id=1380 FN partial_functionality

- 方法: `doGet` vs `save`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Handles HTTP GET request to retrieve a page, check visibility, log, render, and optionally cache the output to a file.
- B 摘要: Saves a byte array to a file, creating parent directories and using try-finally for stream cleanup.
- 静态失败原因: Static BERT/GraphCodeBERT models rely heavily on token overlap and syntactic similarity, which are very low (Jaccard 0.0486). They miss the abstract commonality of file I/O operations due to different contexts and method signatures.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may classify this as a Type-4 clone because both functions involve writing data to a file with proper resource cleanup, and b's behavior is a simplified subset of a's file-writing segment.
- 共享行为: Both write data to a file (a writes cached HTML, b writes arbitrary bytes)；Both use try-catch-finally blocks for resource management
- 行为差异: Different inputs: HttpServletRequest vs byte[]；Different outputs: HTTP response vs file；a involves page retrieval, authorization, logging, and multiple error paths; b is a simple file copy；a's file writing is conditional and part of a larger workflow; b is the entire function
- 修正建议: Enhance model with data-flow analysis to detect similar I/O patterns；Incorporate structural matching of file operations across different contexts；Use graph-based representations that abstract away method names and parameter types

### case_id=1381 FN partial_functionality

- 方法: `saveAttachmentBody` vs `modifyApplicationMessage`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Saves an attachment body by reading from a Part's input stream, writing to a file, and updating a database record with size and content URI.
- B 摘要: Modifies a properties file for a given locale by reading it, updating or appending a key-value pair, and writing back to disk.
- 静态失败原因: The model likely focused on the low lexical overlap (token Jaccard 0.11) and recognized the distinct APIs and domains, correctly predicting non-clone. However, BCB expected a clone due to high-level structural pattern common in file manipulation routines, which static BERT models may miss because they rely on surface tokens and not inferred abstract patterns.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this as a clone due to broad Type-4 (semantic) similarity where both functions involve file handling, stream closing, and error handling patterns, despite different data and domains. The overall structure of 'check file existence, create if needed, read/write, close resources' might be considered similar enough under a relaxed annotation policy.
- 共享行为: Both perform file I/O operations (check existence, create files, write data).；Both handle exceptions and close streams/files.
- 行为差异: Function A deals with binary data (input stream from Part) and updates a database; Function B deals with text properties files and does string manipulation.；Function A writes a single file; Function B reads an existing file, modifies content, and writes back.；Function A uses ContentValues and ContentResolver; Function B uses BufferedReader and FileWriter.；The file formats and purposes are completely different (attachment storage vs. localization properties).
- 修正建议: Train models on abstracted execution traces or program dependency graphs to capture structural similar operations.；Use data augmentation with API sequence abstraction (e.g., replace specific file paths with placeholders).；Incorporate more diverse clones in training to recognize broad Type-4 patterns.

### case_id=1382 FN benchmark_preference_bias

- 方法: `copy` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Copies a file from source path to destination path using a simple byte buffer.
- B 摘要: Reads multiple XML files, performs XSLT transformations, and writes the output as a static website.
- 静态失败原因: Static BERT probably correctly predicted non-clone due to low token overlap and very different code structures, so it did not fail.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as a clone due to broad Type-4 criteria where common low-level file I/O operations are considered similar, but the high-level semantics are entirely different.
- 共享行为: Both use FileInputStream and FileOutputStream for file I/O；Both read and write data in buffer chunks
- 行为差异: Function A is a simple file copy; Function B is a complex site builder with XML transformation；Function A has a single input-output pair; Function B processes multiple files and properties；Function B includes DOM parsing, XSLT, and string manipulation; Function A does no such processing
- 修正建议: Review BCB annotation; consider if this is a labeling error；If confirming non-clone, use this as a hard negative for training

### case_id=1383 FP lexical_or_api_overlap

- 方法: `readData` vs `readFixString`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Initializes multiple static sets and a map by tokenizing string constants and parsing a configuration file.
- B 摘要: Reads a fixed-length string from an input stream using IOUtils and returns the string.
- 静态失败原因: The model likely over-relied on lexical overlap (e.g., 'read', 'String', 'IOException') and did not capture the deep semantic difference in functionality and context.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labeled non-clone because the two functions have completely different purposes and implementations; one is a static initialization routine, the other is a stream reading utility.
- 共享行为: Both involve string processing and I/O operations.
- 行为差异: Function A populates static data structures from tokenized strings and a file; Function B reads bytes from a stream and converts to a string.；Function A has no return value and modifies global state; Function B returns a String.；Function A uses StringTokenizer and manual parsing; Function B uses IOUtils and limited input stream.；Function A handles many different tokens and builds multiple sets; Function B reads exactly len characters.
- 修正建议: Incorporate data-flow and control-flow features to distinguish between initialization and stream I/O.；Use method-level context (e.g., class, field access) to better separate concerns.

### case_id=1384 FN benchmark_preference_bias

- 方法: `write` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.2`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Writes a JAR file by iterating over included JARs and copying their entries, excluding manifest and empty entries.
- B 摘要: Builds a site for editing by transforming XML pages and writing the results to output files, with extensive error handling and debugging.
- 静态失败原因: Static BERT correctly predicted non-clone; the BCB label appears to be a false positive, so the model did not fail but disagreed with a potentially erroneous annotation.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled them as clones due to both being 'write' operations that produce output, possibly under a very broad Type-4 functional similarity, but the actual functionality is entirely different.
- 共享行为: Both involve writing data to output streams/files
- 行为差异: A writes a JAR archive; B writes HTML/text files.；A copies raw zip entries; B performs XML transformations and string manipulations.；A is short and focused; B is long with many parameters and complex logic.；A uses JarOutputStream; B uses FileWriter and custom file system methods.
- 修正建议: Re-evaluate BCB annotation for this pair; it may be an error.；Improve model robustness against overly broad BCB preferences by focusing on semantic equivalence rather than shallow I/O similarity.

### case_id=1385 FN partial_functionality

- 方法: `copyResource` vs `decodeFileToFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copy a resource (URL or local file) to a destination file by reading and writing bytes one at a time.
- B 摘要: Decode a Base64-encoded file to an output file using buffered reading and writing.
- 静态失败原因: The token Jaccard similarity is low (0.19697), and the method names differ; static models often rely on lexical and API overlap, missing the structural similarity of the I/O pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label them as clones (Type-3 or Type-4) because both perform a stream copy from input to output with stream handling, and the Base64 decoding is seen as a functionally similar transformation of the data.
- 共享行为: Read from an input source (URL, file, or input stream)；Write to a file output stream；Close input and output streams after copying
- 行为差异: Function A copies raw bytes, while function B decodes Base64-encoded data.；Function A reads byte by byte; function B uses a buffer and reads/writes in chunks.；Function A throws an exception on failure; function B returns a boolean and prints stack trace.；Function A uses different input sources (URL or file) based on availability; function B always uses a file input stream with Base64 decoding.
- 修正建议: Use a model that incorporates data flow or control flow graphs to capture I/O patterns.；Augment training data with pairs that share high-level functionality but differ in data transformation.；Consider embedding-based similarity that abstracts away specific content (e.g., Base64) and focuses on structure.

### case_id=1386 FP lexical_or_api_overlap

- 方法: `getLinksFromURLFast` vs `init`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Extracts hyperlinks and their text from a given URL's HTML content.
- B 摘要: Loads class names from a configuration file on the classpath and registers them via addClass.
- 静态失败原因: Static BERT or GraphCodeBERT models may have focused on the lexical overlap of common API calls (URL, BufferedReader, InputStreamReader, readLine) and the loop structure, ignoring the distinct high-level purposes and data flows.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would not consider these clones because the overall functionality is completely different—one extracts hyperlinks from a webpage, the other loads Java classes from a resource file. The only overlap is generic I/O boilerplate, which BCB typically ignores.
- 共享行为: Both use BufferedReader and InputStreamReader to read text line by line from a URL-based source.
- 行为差异: Function A parses HTML to extract hyperlinks, while Function B reads class names and loads classes.；Function A returns vectors of links and texts, while Function B modifies internal state via addClass.；Function A uses regex to match HTML tags, while Function B simply reads lines and checks conditions.
- 修正建议: Incorporate data-flow analysis to capture variable dependencies and output behavior.；Use contrastive learning to emphasize semantic differences despite shared I/O patterns.；Include method names and class context in embeddings to disambiguate purposes.

### case_id=1387 FP boilerplate_overlap

- 方法: `sendPost` vs `getNetworkServersIPs`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Sends an HTTP POST request to a given URL with parameters and returns the response as a string.
- B 摘要: Connects to a URL, reads lines, and extracts server IPs from lines following a '!SERVERS' marker, returning a vector of strings.
- 静态失败原因: The model was likely misled by the common boilerplate code for URL reading (opening connection, BufferedReader, while loop reading lines, try-catch) and similar variable names ('url', 'connection', 'reader', 'line'), leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the functions have entirely different purposes (sending data vs. parsing a configuration) despite sharing URL-reading boilerplate.
- 共享行为: Both open a URL connection and read from it line by line；Both use try-catch exception handling for IO errors
- 行为差异: Function A sends data via POST; function B only reads；Function A returns a concatenated string; function B returns a vector of extracted IPs；Function A sets output mode and encoding; function B does not；Function A parses no content; function B implements a state machine for parsing
- 修正建议: Use dataflow-aware models that track how results are constructed (string vs vector) and what operations are performed (sending vs parsing)；Incorporate method name and parameter types as features to distinguish networking operations；Train on more negative examples with similar boilerplate but different semantics

### case_id=1388 FN partial_functionality

- 方法: `addRecord` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Adds a record to a data store by copying input to a file, computing a digest for deduplication, and returning a DataRecord.
- B 摘要: Retrieves a resource as an InputStream, caching the remote file locally to avoid redundant downloads.
- 静态失败原因: Static models like GraphCodeBERT rely on token overlap and structural similarity, which is low; they fail to capture the high-level semantic similarity of caching/deduplication.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both functions as Type-4 semantic clones because they share the high-level purpose of storing/retrieving data with deduplication and caching using file operations.
- 共享行为: Both use file I/O to manage persistent storage；Both implement deduplication/caching to avoid redundant storage；Both use synchronization for thread safety
- 行为差异: A computes a message digest for unique identification, while B uses URL-based caching with modification timestamps；A returns a DataRecord object, B returns an InputStream；A always writes to a new temporary file, B conditionally downloads from a remote URL
- 修正建议: Improve training data with more Type-4 clone examples；Use data flow analysis to identify higher-level patterns like caching；Incorporate goal-oriented semantics via code summarization

### case_id=1389 FP boilerplate_overlap

- 方法: `googleImageSearch` vs `getFullScreenUrl`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Public void method that performs a Google image search for the current track's artist and album, parsing HTML to extract image URLs.
- B 摘要: Private method that retrieves the full screen URL for a YouTube video by parsing the page for 'fullscreenUrl' and extracting parameters.
- 静态失败原因: The static model likely relied on surface-level lexical and structural overlap (e.g., both use URL, URLConnection, BufferedReader, while loops) and ignored the distinct semantics, such as the specific URL strings, the data being parsed, and the method signatures.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BigCloneBench typically considers functions with completely different domain and purpose as non-clones, even if they share common programming patterns. These methods serve entirely different functionalities despite similar boilerplate.
- 共享行为: Establish HTTP connection and read response line by line；Use try-catch for exception handling；Manipulate strings to extract desired data
- 行为差异: Different search domains: Google Images vs YouTube；Different output: void, populating a list of image URLs vs returning a single video URL string；Different parsing logic: splitting on HTML href vs searching for specific line and splitting on '&'；One depends on artist state, the other sets progress bar state
- 修正建议: Incorporate data-flow analysis to highlight differences in constants and string operations；Use attention to method signatures and return types as strong indicators；Add domain-specific features like URL hostnames and parameter names

### case_id=1390 FN partial_functionality

- 方法: `main` vs `invoke`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads HTML from a fixed URL and prints each line to standard output.
- B 摘要: Invokes a remote service method via HTTP POST, parses JSON response, and returns deserialized result, with retry logic on timeout.
- 静态失败原因: The model likely focused on the overall structure and method signatures which are very different, missing the partial overlap in HTTP reading; static BERT models often rely on local context and may not capture high-level program semantics like 'makes an HTTP request'.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider them clones because both perform HTTP communication and read response content line-by-line, a common pattern that aligns with broad Type-3/Type-4 partial functionality similarity.
- 共享行为: Both use BufferedReader to read line-by-line from an InputStream obtained from an HTTP connection.
- 行为差异: code_a is a static main method with no error handling or output processing; code_b is an instance method with dynamic URL construction, JSON parsing, exception handling, and retries.；code_a uses GET (URL.openStream) while code_b uses POST with parameters.；code_a prints to console; code_b returns a deserialized object or null.
- 修正建议: Incorporate dataflow or control-flow graphs to capture high-level I/O patterns.；Use pre-training tasks that emphasize network interactions and stream processing.；Include attention mechanisms that relate distant code segments sharing common APIs.

### case_id=1391 FN partial_functionality

- 方法: `copyFile` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a file from source to destination using buffered I/O with optional force overwrite.
- B 摘要: Transforms XML and writes multiple HTML pages for a site editing system, involving complex file I/O and string processing.
- 静态失败原因: Static BERT models rely heavily on token overlap and lexical similarity, which is very low (0.095). The huge difference in length, complexity, and the presence of many unrelated tokens in B likely caused the model to miss the underlying I/O similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this as a clone because both methods involve buffered file I/O, and under broad Type-4 criteria, sharing a common I/O pattern might be considered sufficient functional similarity.
- 共享行为: Both perform file copy-style I/O operations: read from an input stream and write to an output stream using a buffer.
- 行为差异: Function A is a simple, single-purpose file copy; B is a large, multi-step process including XML transformation, page iteration, and multiple file writes.；B uses many additional libraries (Transformer, DOM, FTP) and has complex control flow.；B's I/O is part of a larger workflow, not the primary functionality.
- 修正建议: Incorporate data flow analysis to identify shared I/O patterns even when code structure differs.；Use graph-based representations (e.g., AST, CFG) to capture the core operations better.；Train on more diverse clones, including those with low lexical overlap but similar behavior.

### case_id=1392 FP boilerplate_overlap

- 方法: `main` vs `checkForUpgrade`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches and prints content from a fixed URL.
- B 摘要: Performs an upgrade check by querying a remote license server, processing the response, updating a database, and updating UI components.
- 静态失败原因: The static model likely overemphasized the lexical overlap of URL, BufferedReader, InputStreamReader, and while loop pattern, ignoring the broader context and functionality.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB annotations prioritize overall functional similarity; the shared URL reading is a trivial boilerplate pattern not defining the core functionality. The vast difference in purpose and complexity justifies a non-clone label.
- 共享行为: Both use URL and BufferedReader to read lines from a remote resource.
- 行为差异: Function A is a standalone main method; function B is an event handler with complex business logic.；Function A simply prints lines; function B processes server responses, queries/updates a database, and manipulates UI visibility.；Function A has no error handling; function B includes multiple error checks and user messages.；Function B involves database operations, license validation, and UI updates, none of which exist in A.
- 修正建议: Incorporate dataflow analysis to distinguish simple I/O from complex processing.；Use semantic features like method length, API call diversity, and external dependencies.；Train on larger context or use contrastive learning to penalize superficial similarities.

### case_id=1393 FN partial_functionality

- 方法: `doGet` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Proxies an HTTP GET request by forwarding to another URL and copying the response.
- B 摘要: Launches a build configuration for a NexOpen project, checking files and managing resources.
- 静态失败原因: Static BERT focuses on token and structural similarity; low Jaccard and different syntax caused it to miss the abstract stream-copying pattern that BCB may have considered semantically equivalent.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled them as clones due to partial similarity in stream copying (IOUtils.copy), despite vastly different contexts, possibly considering it a Type-4 semantic clone.
- 共享行为: Both use IOUtils.copy to copy streams
- 行为差异: Different domains: HTTP proxy vs Eclipse plugin launch；Different error handling and control flow；Different overall purpose
- 修正建议: Enhance model to recognize abstract data flow patterns like stream copy；Incorporate fine-grained API usage and data flow analysis

### case_id=1394 FN partial_functionality

- 方法: `copyResource` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.95`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource (URL or file) to a destination file byte by byte.
- B 摘要: Copies a source file to a destination directory using a buffer.
- 静态失败原因: Static BERT models rely on lexical and structural overlap; low token Jaccard (0.24) and different signatures, control flow (single-byte vs buffer), and parameter patterns made the model perceive them as dissimilar, lacking understanding of shared high-level intent.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considers both as implementing the high-level task of copying a file/resource, tolerating differences in source type, I/O granularity, error handling, and parameterization as non-essential variations.
- 共享行为: Read data from an input source；Write data to an output file；Close streams after copying
- 行为差异: Source type: A supports URL and file; B only file；I/O method: A reads single bytes; B reads chunks via buffer；Error handling: A throws generic Exception; B catches IOException and prints error；Destination determination: A writes to a fixed destination; B writes to destDir with same filename
- 修正建议: Use contrastive learning with semantic clone pairs to capture high-level similarity；Incorporate dataflow or I/O operation abstraction；Augment training data with Type-3/4 clones that vary in implementation details

### case_id=1395 FN benchmark_preference_bias

- 方法: `getFile` vs `setPayload`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies a specific attribute, and saves to temp directory, returning the file path.
- B 摘要: Appends content from a headless data file to another file, then recursively processes the next header, returning success boolean.
- 静态失败原因: Static BERT/GraphCodeBERT correctly predicted non-clone due to low lexical overlap; BCB label likely an annotation error or bias towards common I/O idiom, causing the model to be penalized for a false negative.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled these as clones due to the shared use of NIO channels for file transfer, considering them as broad Type-4 clones with similar low-level I/O pattern, despite different high-level purpose.
- 共享行为: Both use FileChannel to transfer data between streams/files；Both involve file I/O with FileOutputStream and FileInputStream；Both handle IOException
- 行为差异: A downloads from URL and modifies XML; B copies local file and recurses；A returns file path string; B returns boolean；A uses exception handling with multiple catch blocks; B only throws IOException；A has a loop over XML nodes; B has recursion
- 修正建议: Re-evaluate BCB label for this pair to ensure consistency with clone definition；Incorporate data-flow analysis to distinguish different source/destination semantics；Add method-level context (e.g., parameters, return type) to reduce false negatives from lexical mismatches

### case_id=1396 FN boilerplate_overlap

- 方法: `addIDs` vs `readIntoList`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.7`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Adds metabolite IDs from a remote GMD database to a row object, parsing HTML to extract scores and molecular weights.
- B 摘要: Reads a list of room names from a URL and populates a map with JMenuItem objects for a popup menu.
- 静态失败原因: Static BERT/GraphCodeBERT models often rely on surface-level token overlap and control flow structure. Both functions share a similar boilerplate of URL opening, BufferedReader, while loop, and string parsing, which may have led the model to overestimate similarity and miss the fundamentally different data transformations and outputs.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may have labeled this as a clone due to the common pattern of reading from a URL and parsing HTML, considering it a Type-3 clone where the core functionality (URL reading and line parsing) is similar despite different post-processing.
- 共享行为: Both open a URL and read lines using BufferedReader；Both parse HTML lines using indexOf/substring；Both use a while loop to process lines；Both close the reader
- 行为差异: Function A extracts metabolite IDs and scores, setting multiple properties on a row object; Function B extracts command names and creates JMenuItem objects with action listeners；Function A returns an integer score; Function B returns void and populates a map；Error handling differs: Function A logs and returns 0; Function B prints stack trace；HTML parsing patterns differ (e.g., searching for 'Metabolites/' vs '>')
- 修正建议: Incorporate dataflow analysis to track how the parsed data is used (e.g., row.setVar vs map.put)；Use context-aware embeddings that capture method-level purpose (e.g., return type, class dependencies)；Augment training with examples where similar structure but different domain logic leads to non-clones

### case_id=1397 FP lexical_or_api_overlap

- 方法: `copyFileChannel` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Copies a file using FileChannel, optionally preserving modification time.
- B 摘要: Handles action events in a GUI, opening file choosers and updating preferences for various settings.
- 静态失败原因: Static BERT/GraphCodeBERT might have been misled by common tokens like 'File', 'inputChannel', 'outputChannel', and 'filename', as well as similar control flow structures (try-finally, while loop) appearing in both. The model may have focused on surface-level lexical overlap without understanding the overall semantic purpose.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the functions serve entirely different purposes: file copying vs. GUI event handling. Even under broad Type-4 similarity, there is no shared functionality.
- 共享行为: Both involve file-related operations (one copies files, the other opens file choosers).
- 行为差异: copyFileChannel performs file copying via NIO channels; actionPerformed handles GUI events and modifies application settings.；copyFileChannel is a utility function; actionPerformed is an event callback.；copyFileChannel has no user interaction; actionPerformed relies on user interaction.
- 修正建议: Improve contextual embedding to capture high-level intent beyond API names.；Incorporate training data with diverse program structures to reduce reliance on token-level matches.；Use code structure features like data flow or control flow to distinguish different behaviors.

### case_id=1398 FN partial_functionality

- 方法: `DecodeMapFile` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Decodes a map file by XORing each byte with an incrementing key and writes to output file.
- B 摘要: Retrieves a resource via URL with caching, returning an InputStream of the resource.
- 静态失败原因: Low token overlap (0.156), distinct domain vocabulary (XOR vs. URL/cache), and large length disparity cause the model to rely on lexical rather than structural patterns.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as file I/O operations with stream copying and error handling, possibly classifying them as Type-4 due to broad functional similarity (reading and writing data), despite differing specific purposes.
- 共享行为: Both read from an input source and write to an output file/stream；Both include exception handling with try-catch blocks；Both close streams after use
- 行为差异: A performs a specific XOR transformation per byte; B does no transformation (pure copy)；B involves URL connection, caching logic, and conditional cache validation；B is significantly longer and more complex than A；A writes to a specified output file; B writes to a cache file and returns a stream
- 修正建议: Incorporate structural features like data flow and control flow graphs；Use contrastive learning on pairs with similar I/O patterns but different transformations

### case_id=1399 FN partial_functionality

- 方法: `read` vs `seeURLConnection`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a properties skeleton file from classpath, parses sections delimited by '---', and validates the number of sections.
- B 摘要: Opens a hardcoded URL connection, reads the entire response line by line, and logs the content.
- 静态失败原因: Static BERT/GraphCodeBERT likely overemphasized lexical overlap (e.g., 'URL', 'BufferedReader', 'readLine', 'while ((s = br.readLine()) != null)') and missed the distinct high-level semantics: one is a file parser with validation, the other is a simple HTTP downloader. The model lacks understanding of the different control flows and data dependencies.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB might label them as clones due to superficial structural similarity: both use URL, InputStream, BufferedReader, readLine loop, and StringBuilder/StringBuffer. The token Jaccard similarity is low, but the BCB annotation may consider broad Type-4 clones where overall semantics differ but share similar I/O patterns. However, this seems too broad for typical BCB standards.
- 共享行为: Both use URL to open a stream；Both read lines using BufferedReader；Both accumulate read content into a buffer
- 行为差异: Input source: classpath resource vs hardcoded HTTP URL；Processing: section parsing vs plain concatenation；Error handling: custom exceptions for missing/wrong resources vs no explicit error handling；Output: stores sections in a list vs logs the entire content
- 修正建议: Incorporate control-flow and data-flow features to distinguish reading from different sources (classpath vs URL).；Use abstract syntax tree (AST) or program dependency graph (PDG) to capture structural differences in loops and operations.；Add token-level attention to distinguish API calls (getResource vs URL constructor) and processing (sections vs log).；Train with more examples of non-clones that share I/O patterns but differ in functionality.

### case_id=1400 FN benchmark_preference_bias

- 方法: `createNew` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.4`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Creates a new file from an InputStream, but only for specific names and if the user is allowed.
- B 摘要: Retrieves a resource by URL, caching it locally and returning an InputStream.
- 静态失败原因: The model likely relied on token overlap and structural patterns, which are low, and did not capture the high-level resource-access similarity that BCB might have seen.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might consider both as resource-handling methods that return a resource-like object, possibly overlooking the distinct write vs. read and local vs. network contexts.
- 共享行为: Both handle file and stream operations；Both may return null on failure
- 行为差异: A writes to a new file, B reads from a cached file；A uses local file system, B downloads from URL；A checks user permissions, B implements caching logic；A only processes specific file names, B handles any name
- 修正建议: Train with broader functional similarity examples including Type-4 clones；Incorporate data flow analysis to detect common resource handling patterns

### case_id=1401 FP boilerplate_overlap

- 方法: `callApiPost` vs `getTicketsForQueue`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Generic HTTP POST utility that sends parameters and returns input stream, with timeout and header settings.
- B 摘要: Specific function to query a Request Tracker API for open tickets in a queue using HTTP GET, parsing ticket IDs and fetching full tickets.
- 静态失败原因: Model likely overfitted on common HTTP boilerplate (open connection, set method, check status) and missed the semantically distinct business logic, data flow, and output types.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels as non-clone because the overall functionality and data flow are entirely different beyond the superficial HTTP interaction.
- 共享行为: Both perform HTTP requests and check response status codes.
- 行为差异: HTTP method differs (POST vs GET)；Different return types (InputStream vs List<RTTicket>)；Different parameter handling (output stream vs URL encoding)；Different error handling (throws exception vs returns null)
- 修正建议: Train on more diverse non-clone pairs that share common API usage patterns but differ in intent；Incorporate data flow analysis to distinguish different processing pipelines；Use attention mechanisms that capture long-range semantic context beyond local tokens

### case_id=1402 FN boilerplate_overlap

- 方法: `read` vs `httpRequestByPOST`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a skeleton file from the classpath and parses it into sections separated by '---'.
- B 摘要: Sends an HTTP POST request and reads the response line by line, returning the concatenated response string or null on error.
- 静态失败原因: Static BERT models rely heavily on token or API overlaps; the low Jaccard (0.177) and different method names/API calls cause the model to miss the underlying structural similarity of the I/O loop pattern.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB often labels as clones when two functions share a significant structural pattern like the BufferedReader readLine loop, even if the surrounding context (e.g., HTTP vs file I/O) differs, considering it a Type-3 clone.
- 共享行为: Both read text line by line using BufferedReader and a while loop.；Both append each line to a buffer (StringBuilder/StringBuffer).；Both use InputStreamReader to decode bytes to characters.；Both handle exceptions (IOException or broader exception).
- 行为差异: Source: one reads a local classpath resource, the other reads an HTTP response.；Error handling: A throws Exception, B returns null and sets error codes.；Output: A is void (saves sections in member), B returns String.；Functionality: A parses sections with '---' separator, B just concatenates lines.
- 修正建议: Use graph-based or AST-based models that abstract away specific API calls to capture structural patterns like while-readLine loops.；Include dataflow information to recognize that both functions transform an input stream into a string buffer.；Train with contrastive examples that emphasize shared control structures over lexical differences.

### case_id=1403 FP boilerplate_overlap

- 方法: `readUNI` vs `load`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a tab-separated file from a URL and populates a vector with ID and description pairs.
- B 摘要: Downloads a pastebin document by ID and returns its content as a single string.
- 静态失败原因: The static model likely relied on surface-level similarities such as URL opening, while loops, and exception handling, ignoring the distinct data processing logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the functions have fundamentally different purposes (structured data extraction vs. raw download), and the similarity is limited to boilerplate I/O code.
- 共享行为: Both open a URL and read its content line by line.；Both handle I/O exceptions and close streams in a finally block.
- 行为差异: Function A parses tab-delimited fields, while function B simply concatenates all lines.；Function A writes to an external Vector; function B returns a string.；Function A uses Scanner with delimiters; function B uses BufferedReader.；Function B shows a dialog on error and uses a global working flag; function A only prints stack trace.
- 修正建议: Increase sensitivity to data transformation logic beyond I/O boilerplate.；Incorporate data flow analysis to distinguish field-parsing vs. raw concatenation.

### case_id=1404 FN lexical_or_api_overlap

- 方法: `setBundleInfoName` vs `readData`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Reads a configuration file from a URL, parses key-value lines, and updates the names of bundle items in a list.
- B 摘要: Reads string token lists and a configuration file, parses various columns, and populates multiple sets and maps for Tibetan script processing.
- 静态失败原因: Static BERT models focus on lexical and structural tokens; the low token Jaccard (0.116) and dissimilar API calls (URL vs StringTokenizer) caused the model to miss the high-level semantic similarity. The model likely saw no overlapping method calls or control flow patterns.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely considered both as Type-4 clones due to high-level semantic similarity of reading and parsing configuration to populate data structures, despite different specific operations.
- 共享行为: Both read input (stream or file) and parse lines/tokens to initialize internal data structures.
- 行为差异: Function A updates specific fields of existing objects in a list; function B builds new sets and maps from scratch.；Input sources differ (URL vs. file and string constants).；Parsing logic and output collections are entirely different.
- 修正建议: Incorporate data-flow analysis to capture shared I/O patterns；Use representation learning that abstracts common tasks like 'parse input and initialize data'；Add training examples with broad Type-4 clones

### case_id=1405 FN partial_functionality

- 方法: `doTransfer` vs `doRawRequest`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Transfers HTTP request to another URL by reading request parameters, setting headers, copying body, and returning response to client.
- B 摘要: Sends a raw POST request to a fixed service URL with given data and returns the response as a string.
- 静态失败原因: Low token overlap (0.196) and different structural patterns; static analysis misses the shared HTTP connection core due to lexical and control flow differences.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considers both as HTTP request/response patterns, accepting broad Type-3/4 similarity despite contextual differences.
- 共享行为: Create HTTP connection；Set output mode；Write data to output stream；Read response from input stream
- 行为差异: A reads URL from request parameter, B uses constant URL；A copies request headers, B does not；A handles different HTTP methods, B only POST；A reads request body from input stream, B from string parameter
- 修正建议: Incorporate data-flow analysis to track API usage patterns；Use dynamic analysis or runtime traces to capture execution behavior；Leverage method naming and surrounding context to infer intent

### case_id=1406 FN benchmark_preference_bias

- 方法: `login` vs `fetchUrl`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `preference_memory_with_manual_audit`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Logs in to LOLA by sending POST request with email and password, extracts session ID from response, and returns it.
- B 摘要: Fetches the content of a given URL using GET request and returns it as a string.
- 静态失败原因: Static BERT models like GraphCodeBERT rely on lexical and syntactic features. The token Jaccard is low (0.212), and the functions have different method names and distinct logic (POST vs GET, session handling vs generic fetch). The model likely focused on these differences and correctly identified non-clone. However, it failed to recognize the broad Type-3 similarity that BCB considers.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BigCloneBench often considers functions with similar structure (open URL, read stream, return string) as clones, especially if they share common utility patterns, even if the specific protocol or data extraction differs. The login function is essentially a specialized URL fetch with POST and session handling, so BCB may view it as a variant of URL fetching.
- 共享行为: Both open a URL connection；Both read lines from the input stream；Both catch exceptions and return empty string on failure
- 行为差异: Function A uses POST with form data; B uses GET；Function A extracts a session ID from the first line; B concatenates all lines；Function A sets a session field; B does not；Function A uses URLConnection with DoOutput; B uses url.openStream()
- 修正建议: Incorporate structural similarity features like common API usage patterns；Use data-flow or control-flow graphs to identify shared utility patterns；Train with BCB-style labels to learn broader clone definitions；Add attention to I/O patterns and exception handling as clone indicators

### case_id=1407 FP boilerplate_overlap

- 方法: `googleImageSearch` vs `downloadFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Searches Google Images for the current track artist/album and collects image URLs into a list.
- B 摘要: Downloads a file from a given URL to a local destination with progress reporting.
- 静态失败原因: Overlapped on common API calls (URL, openConnection, getInputStream, BufferedReader) and exception handling pattern, ignoring differences in control flow and output.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: None
- 共享行为: Both open URL connections and read from input streams；Both use try-catch for exception handling
- 行为差异: A parses HTML to extract image links; B writes binary data to a file；A is void and depends on instance variables; B is static and returns boolean；A does not write to disk; B saves file locally
- 修正建议: Train with contrastive learning on pairs with similar I/O but different functionality；Incorporate data flow analysis to distinguish read vs. write operations

### case_id=1408 FP lexical_or_api_overlap

- 方法: `populateResources` vs `sendPost`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Loads templates and default images from classpath resources and saves them.
- B 摘要: Sends an HTTP POST request and returns the response string.
- 静态失败原因: Static BERT/GraphCodeBERT may have been misled by overlapping tokens like URL, BufferedReader, InputStreamReader, try-catch, and the general pattern of opening a stream and reading lines. Without understanding the broader context (populating resources vs. sending HTTP), it falsely detected a clone.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the overall functionality is completely different despite some boilerplate code similarities. BCB Type-4 (semantic similarity) requires functional relatedness, which is absent here.
- 共享行为: Both use I/O streams (InputStream, BufferedReader) to read data line by line.；Both have try-catch blocks for exceptions.；Both create URL objects (though different usage).
- 行为差异: Function A reads from classpath resources and saves to local storage; Function B sends HTTP POST to remote server and returns response.；Function A deals with text templates and images; Function B sends request parameters and receives HTTP response.；Function A has multiple resource types (Resource, Image, Property); Function B only does HTTP communication.
- 修正建议: Incorporate control flow and data flow analysis to distinguish between local resource loading and remote HTTP communication.；Use graph-based representations that capture the overall data flow (e.g., saving to local vs. sending over network).；Add awareness of method signatures (void vs. String return) and exception handling patterns.

### case_id=1409 FN partial_functionality

- 方法: `read` vs `doVersionCheck`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Opens a URL or file and reads its content, returning a status code indicating success or failure.
- B 摘要: Performs a version check by reading build numbers from a remote URL, showing a wait cursor, and showing errors via GUI.
- 静态失败原因: The model likely focused on surface-level tokens and control flow which differ significantly (different method signatures, one has file vs URL conditional, the other has a while loop). Low token Jaccard (0.254) and different method names caused the model to miss the abstract similarity of 'URL read with exception handling'.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely labels them as clones because both functions share the core pattern of opening a URL, reading data, and handling exceptions, which is considered a common structural similarity even though the specific purposes differ. BCB's broad criteria often accept Type-3/Type-4 clones with partial functionality overlap.
- 共享行为: Open a URL connection and read from an InputStream；Catch IOException and handle it
- 行为差异: A can read from either URL or file; B only reads from URL；A returns an int status; B is void and uses GUI feedback；A reads entire stream via a method call; B reads line by line looking for specific prefixes；A does not manage cursor; B shows/hides wait cursor
- 修正建议: Train with data augmentation that pairs functions with shared subfunctionality but different overall goals；Incorporate code summarization or flow-based representations to capture high-level behavior；Use contrastive learning with positive pairs that have low token overlap but similar abstract patterns

### case_id=1410 FN partial_functionality

- 方法: `init` vs `read`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Loads controller classes by reading class names from a registry file found in classpath resources.
- B 摘要: Reads a file from a URL or local path into a buffered stream and returns a status code.
- 静态失败原因: Low token overlap (0.17) and different method names/intents caused the model to miss the common pattern of URL streaming and error handling.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may accept this as a Type-4 (partial functionality) clone because both functions involve opening a URL stream and processing input with similar exception handling, despite different high-level purposes.
- 共享行为: Open a URL stream and read input；Handle IOException with logging and error printing；Use stream/reader classes (BufferedReader, BufferedInputStream)
- 行为差异: A reads text line by line and loads classes; B reads binary data and returns status；A uses ClassLoader; B uses FileInputStream for local files；A iterates over multiple URLs; B handles a single resource；A has nested loops; B uses a conditional for URL vs file
- 修正建议: Incorporate structural patterns like 'open stream -> read process -> handle exceptions' into clone detection training；Use data augmentation with partial clones to improve recognition of shared sub-functionality；Enhance model with control-flow or data-flow awareness to capture common I/O idioms

### case_id=1411 FN benchmark_preference_bias

- 方法: `modifyApplicationMessage` vs `byReference`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Modifies a locale-specific properties file by updating or adding a message name-value pair.
- B 摘要: Copies an InputStream to a temporary file and returns an ImmutableContent object referencing it.
- 静态失败原因: Static BERT correctly predicted non-clone because of low token overlap and clear semantic differences; it did not fail in this case.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as a clone due to superficial similarity in using file I/O and exception handling, but the functions have no common functionality.
- 共享行为: Both perform file I/O operations.；Both handle exceptions by printing stack traces.
- 行为差异: Different overall purpose: modifying properties vs. creating temporary file from stream.；Different input parameters and return types.；Different file operations: one reads and writes properties files, the other copies an InputStream to a temp file.
- 修正建议: Review the BCB annotation for this pair to confirm it is a mislabel.；Consider removing or correcting this pair in the benchmark.

### case_id=1412 FN benchmark_preference_bias

- 方法: `main` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `preference_memory_with_manual_audit`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a ZIP file from a URL and extracts its entries to the local filesystem.
- B 摘要: Copies a file from a source path to a destination path using FileChannel.
- 静态失败原因: Low lexical overlap and divergent API usage (URL/ZipInputStream vs FileChannel) likely caused the model to miss abstract similarity in data transfer functionality.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider both as 'file I/O' or 'data transfer' operations, accepting broad Type-4 similarity despite different sources and destinations.
- 共享行为: Both read data from a source (URL or file) and write to a destination (local filesystem).；Both perform I/O operations and close resources.
- 行为差异: Function A fetches data over HTTP and decompresses ZIP; function B copies a local file directly.；Function A writes multiple entries; function B writes a single file.；Function A uses InputStream/OutputStream; function B uses FileChannel.；Function A is a main method; function B is a utility method.
- 修正建议: Incorporate data flow analysis to capture 'read from source, write to destination' pattern.；Train on more diverse representations of I/O operations.；Use task-oriented embeddings focusing on functional behavior rather than API tokens.

### case_id=1413 FN partial_functionality

- 方法: `save` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Saves multiple byte arrays as files in a directory and adds a package declaration header.
- B 摘要: Retrieves a resource from a URL, caches it locally if not fresh, and returns an InputStream.
- 静态失败原因: Low token Jaccard similarity (0.137) and different method signatures/names led the model to focus on surface-level differences, missing the shared file I/O patterns.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as 'file I/O with stream operations' under a broad Type-4 category, even though their core purposes differ (saving local files vs. caching remote resources).
- 共享行为: Both perform file I/O operations (read/write streams).；Both create directories if needed.；Both handle exceptions with try-catch.
- 行为差异: Function A writes byte arrays to files and then adds a package line; Function B reads from a URL and writes to a cache file.；Function A is static and synchronous; Function B is synchronized and instance-level.；Function B includes HTTP connection handling and caching logic; Function A does not.
- 修正建议: Incorporate dataflow analysis to track file and stream manipulations.；Use a more semantically aware model that maps API usage to high-level operations (e.g., 'file write', 'stream copy').

### case_id=1414 FP boilerplate_overlap

- 方法: `readZoneIDs` vs `parse`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Reads a file of zone IDs (one per line) and returns a HashSet of integers.
- B 摘要: Parses a complex data file with headers, types, and multiple delimiters, handling scientific notation and header lines, returning a DataSet object.
- 静态失败原因: The static model likely over-relied on lexical or API-level similarities (e.g., both use openStream, BufferedReader, readLine) without capturing the vast difference in overall logic and output. The low token Jaccard (0.074) suggests the model may have been misled by the boilerplate I/O pattern common to many file-reading functions.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels this as non-clone (0) because the functions have completely different purposes and levels of complexity. Even under broad Type-3/Type-4 criteria, they are not functionally similar.
- 共享行为: Both read from an input source (file/URL) using InputStreamReader and BufferedReader derivatives.；Both handle IOExceptions within try-catch blocks.；Both involve reading lines or tokens from input.
- 行为差异: Code A reads only integer lines and builds a simple set; Code B parses structured data with headers, types, and scientific notation.；Code A returns a HashSet<Integer>; Code B returns a DataSet object with column names and row data.；Code A is short and straightforward; Code B is long and complex with many conditionals and state management.；Code B includes dry-run mode, URL/file support, pre/post header line skipping, and tokenizer configuration; Code A has none of this.
- 修正建议: Incorporate dataflow analysis to track how inputs are processed and what outputs are produced.；Use control flow structure matching to distinguish simple loops from complex state machines.；Train with more diverse negative examples that share I/O patterns but differ in functionality.

### case_id=1415 FP boilerplate_overlap

- 方法: `get` vs `postRequest`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Performs HTTP GET request with custom headers to fetch game records, filtering comments and decoding each line into GameRecord objects, returning an array.
- B 摘要: Performs HTTP POST request with URL-encoded form data from a HashMap, reads the response and concatenates all lines into a single string, returning that string.
- 静态失败原因: Static BERT models like GraphCodeBERT may overemphasize the surface similarity of common API usage patterns (HTTP connection, BufferedReader) and ignore the semantic differences in HTTP method, request crafting, and response parsing. The code structure is similar but the actual computation is different.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the functions perform different HTTP methods and handle responses differently; they are not even Type-3 since the algorithmic logic differs significantly beyond just variable renames or statement reordering.
- 共享行为: Both make HTTP requests to a URL；Both read response line by line using BufferedReader；Both handle IOException/Exception and print stack trace；Both return null on failure
- 行为差异: Function A uses GET method with custom headers; Function B uses POST method with URL-encoded data in body；Function A filters lines starting with '#' and decodes GameRecord objects; Function B concatenates all lines into one string；Function A returns an array of GameRecord; Function B returns a single String；Function A takes latitude, longitude, count parameters; Function B takes a HashMap of data
- 修正建议: Train on more diverse examples that distinguish GET vs POST and different response parsing；Incorporate data flow analysis to track how input parameters are used and output types；Use contrastive learning to emphasize differences in request method and response handling

### case_id=1416 FP boilerplate_overlap

- 方法: `perform` vs `getRandomGUID`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Handles a web request to classify a concept, processes form parameters, and sends an HTTP POST to an external service.
- B 摘要: Generates a random GUID using MD5 hashing of system time and random numbers.
- 静态失败原因: The static model likely over-generalized from superficial common elements like try-catch blocks, StringBuffer usage, and the presence of exception handling, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically considers these non-clones because they perform completely different high-level tasks with no functional overlap.
- 共享行为: Both use try-catch blocks for exception handling；Both manipulate strings with StringBuffer
- 行为差异: Function A is a web request handler with session management and external HTTP calls; B is a local GUID generator；A uses various domain-specific beans and utilities; B uses MD5 and random number generators；A returns an ActionForward and modifies session; B modifies instance variables and has no return
- 修正建议: Improve training data to emphasize functional semantics over boilerplate patterns；Incorporate structural or control-flow analysis to distinguish domain-specific logic

### case_id=1417 FP lexical_or_api_overlap

- 方法: `setMembers` vs `SRWGuiClient`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.05`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Parses HTML from a Trac URL to extract component and priority options into static arrays.
- B 摘要: Constructs a Swing browser GUI that fetches and displays an XML/HTML page, optionally applying XSLT transformation.
- 静态失败原因: Static BERT/GraphCodeBERT models often rely on token-level similarity and API usage patterns. Both functions share common Java I/O APIs (URL, BufferedReader, InputStreamReader), try-catch blocks, and similar code structure for reading lines. The model may have overweighted these superficial similarities while ignoring the entirely different high-level semantics and control flow.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels Type-4 clones only if the overall behavior is similar (e.g., both fetch data from a URL and process it). Here, A is a parsing utility, B is a GUI initializer with rendering; their functionalities are too distinct to be considered clones even under relaxed Type-4 criteria.
- 共享行为: Both read from a URL using BufferedReader and InputStreamReader；Both handle IOException with catch blocks；Both use URL and InputStream-related classes
- 行为差异: Purpose: A is a static utility to populate arrays; B is a GUI constructor for a web browser；Functionality: A extracts HTML form select values; B reads XML/XSLT and renders HTML；Side effects: A sets global variables; B creates and displays a JFrame；Use of regex: A uses Pattern/Matcher; B does not
- 修正建议: Incorporate structural information like method signatures and call graphs；Use data flow analysis to distinguish different data processing paths；Train on more diverse examples where I/O boilerplate is not indicative of clonehood

### case_id=1418 FN benchmark_preference_bias

- 方法: `doGet` vs `encodeFileToFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Handles HTTP GET request, retrieves a page, checks user permissions, logs requests, and optionally caches the page output to a file for non-editable users.
- B 摘要: Encodes a source file to a destination file using Base64 encoding, with standard file I/O and error handling.
- 静态失败原因: The static model correctly identified the lack of semantic similarity, but the BCB label is likely an annotation error or overly broad interpretation. The model did not fail; instead, the benchmark annotation is questionable.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: The BCB annotation likely considers both functions as involving file operations and exception handling, and may classify them as Type-4 semantic clones due to the broad 'file processing' theme, though this is a very loose interpretation.
- 共享行为: Both involve file I/O operations (writing to files)；Both use try-catch blocks for exception handling
- 行为差异: Function A is a servlet handler for HTTP requests with complex logic for page retrieval, user authentication, and logging; Function B is a simple utility for Base64 file encoding；Function A includes networking, session management, and caching; Function B is purely file-based；The file write in A is conditional and part of a larger caching mechanism; in B it is the core purpose；Function A outputs HTML; Function B outputs binary data
- 修正建议: Re-evaluate the BCB label for this pair; it may be a misannotation；Consider using more robust semantic similarity measures that account for functional equivalence rather than superficial I/O patterns

### case_id=1419 FP lexical_or_api_overlap

- 方法: `getUser` vs `handler`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Loads a user from a database or creates a new user by parsing a configuration file.
- B 摘要: Extracts substrings from a web page based on target parameters and updates a result map.
- 静态失败原因: The model overemphasized lexical overlaps like 'URL url', 'BufferedReader', 'readLine()', and loop structure, ignoring the distinct semantics of the surrounding operations and method signatures.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely considers them non-clones because the core functionality differs significantly (user management vs HTML scraping) despite similar I/O boilerplate.
- 共享行为: Both open an input stream and read lines in a loop；Both parse each line using string tokenization or substring extraction
- 行为差异: A handles user authentication; B handles web scraping；A reads from a local resource file; B reads from a remote URL；A returns a User object; B returns void and updates a map；Different parameter lists and logic for parsing delimiters
- 修正建议: Incorporate dataflow analysis to track how parsed data is used (e.g., creating User vs updating map).；Use method-level semantics like return type and parameter roles to disambiguate.；Enhance with type-aware embeddings for domain-specific objects (User vs Map).

### case_id=1420 FP boilerplate_overlap

- 方法: `loadDefaultSettings` vs `readData`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.98`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Copies a default configuration resource file to a specified file path.
- B 摘要: Parses string constants and a configuration file to populate various data structures (sets, maps) for mapping Wylie to Tibetan characters.
- 静态失败原因: The model likely overfitted to boilerplate patterns such as 'private static void', 'try { ... } catch (Exception e) { ... }', and similar method length, ignoring the completely different operations and data flows.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels non-clone because the functions share no semantic similarity: one is simple file copy, the other is complex data parsing/initialization for a Tibetan text transliteration system.
- 共享行为: Both are private static void methods with a try-catch block.；Both perform initialization of some resources.
- 行为差异: Function A copies file contents; B does not write any files.；Function B parses strings and a file into multiple collections; A uses IOUtils.copy.；Function A throws RuntimeException on error; B throws Error and prints to stdout.；Function A uses IOUtils.closeQuietly; B does not use IOUtils.
- 修正建议: Enhance model with dataflow analysis to track core operations (e.g., I/O, string parsing).；Use syntactic and semantic abstraction to distinguish boilerplate from core logic.；Include negative sampling with high lexical overlap but different semantics.

### case_id=1421 FP lexical_or_api_overlap

- 方法: `run` vs `readScalarpvviewerDocument`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: A runnable that loads a text resource from a URL and sets it in a main panel's source text area.
- B 摘要: Reads and parses an XML document from a URL to configure a scalar PV viewer application.
- 静态失败原因: The static BERT model likely overfitted to lexical overlap patterns like 'URL', 'BufferedReader', 'try-catch', and simple loop structure, ignoring deeper semantic differences. The similar I/O boilerplate and exception handling triggered a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clone because the functions have entirely different domain purposes: one is a generic text loader, the other is a specific configuration reader for a scientific visualization tool. The token overlap is low (0.116), and the control flow and data dependencies diverge significantly.
- 共享行为: Both read data from a URL；Both use BufferedReader and InputStreamReader；Both handle IO exceptions
- 行为差异: A merely loads and displays raw text; B parses XML and updates many UI components；A is a Runnable intended for background loading; B is a method called directly；A appends carriage return/newline; B uses system line separator；B has extensive XML parsing and configuration logic absent in A
- 修正建议: Incorporate data flow or program dependency features to distinguish different post-processing paths.；Use structure-aware embeddings that capture the overall intent (e.g., text loading vs. XML parsing).；Fine-tune on a broader set of non-clone pairs that share I/O patterns but differ in semantics.

### case_id=1422 FN benchmark_preference_bias

- 方法: `modifyApplicationMessage` vs `createButtonCopyToClipboard`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Modify a locale-specific properties file by updating or adding a message key-value pair.
- B 摘要: Create an SWT button that copies environment report to clipboard on click.
- 静态失败原因: The static model correctly predicted no clone (consistent with strict judgment). It did not fail; the BCB label appears incorrect for this pair.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have mislabeled due to superficial similarity (both involve 'application message' vs 'clipboard'?), or benchmark bias toward labeling as clone when both are utility methods. However, no real functional similarity exists.
- 共享行为: Both are void methods.
- 行为差异: A performs file I/O on properties files; B creates a GUI button.；A handles localization logic; B handles clipboard copy.；A uses Properties, FileReader, FileWriter; B uses SWT, SelectionAdapter.；A has error handling with catch; B has no exception handling.
- 修正建议: Re-evaluate BCB label for this pair; likely a false positive in the benchmark.；Improve training data quality to avoid such mismatches.

### case_id=1423 FN partial_functionality

- 方法: `getFile` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies its endpoint, and saves to temp directory, returning the file path.
- B 摘要: Copies the content of a source file to a destination file using a byte buffer.
- 静态失败原因: Static BERT/GraphCodeBERT likely focused on low token-level similarity (Jaccard 0.10) and method name/structural differences, missing the underlying semantic similarity of the copying sub-task.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as file transfer utilities with similar core I/O logic, focusing on the semantic similarity of copying bytes from source to destination, which is a Type-4 clone pattern.
- 共享行为: Both open an input stream and output stream to transfer bytes.；Both read bytes from a source and write them to a destination.；Both close streams after operation.
- 行为差异: getFile downloads from a URL; copyFile reads from a local file.；getFile performs XML modification; copyFile does not.；getFile returns a String; copyFile returns void.；getFile handles multiple exceptions; copyFile only throws IOException.
- 修正建议: Incorporate sub-function detection to identify common I/O patterns.；Use dataflow analysis to track stream creation and transfer operations.；Train on more diverse partial functionality clones to capture such cases.

### case_id=1424 FP dataflow_blindspot

- 方法: `parse` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_with_trace`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Parses an InputStream by either copying stream content to a file based on a metadata key lookup or delegating to a downstream parser.
- B 摘要: Handles UI action events by performing various configuration tasks (e.g., setting file paths for Graphviz/ImageMagick, adjusting date format, look-and-feel) and persisting preferences.
- 静态失败原因: The small token overlap (0.05) suggests low lexical similarity, but the model may have been misled by common control flow patterns (if statements, string comparisons) or generic method names (parse/actionPerformed) without understanding domain-specific semantics.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 dataflow_trace_and_outputs。
- BCB 偏好解释: BCB labeled non-clone because the two functions have entirely different purposes and code structures, with no significant overlap in functionality.
- 行为差异: Function A deals with file stream I/O and parsing, while Function B handles UI event-driven configuration.；Function A has a conditional branch based on a map lookup; Function B has a long chain of command string comparisons.；Function A manipulates InputStream and Metadata; Function B manipulates UI components and preferences.；Function A is concise and focused; Function B is lengthy with multiple unrelated sub-tasks.
- 修正建议: Incorporate dataflow analysis or abstract syntax tree representations to differentiate I/O parsing from UI event handling.；Increase training data diversity with non-clone pairs that have low token but high structural similarity to avoid false positives.

### case_id=1425 FP other

- 方法: `actionPerformed` vs `copyLogic`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Handles GUI preference changes for various settings (e.g., Graphviz path, image scaler, date format) and saves them via a controller.
- B 摘要: Copies a .class file from a source path to a destination path using file channels, with state management.
- 静态失败原因: Given very low token Jaccard (0.056), the false positive likely stems from limitations in the model's ability to process long ranges (Function A is truncated but very long) or from misinterpreting rare pattern matches; however, the reason remains unclear as there is no apparent lexical similarity.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB labels non-clone because the functions have no semantic overlap in purpose, input/output, or behavior.
- 行为差异: Function A is an event handler managing multiple GUI preferences with file choosers and UI updates; Function B is a file copy operation with state transitions.；Function A involves user interaction and saving preferences; Function B is a simple I/O operation.；Function A is very long and complex; Function B is short and straightforward.
- 修正建议: Improve long-range dependency handling in models.；Incorporate structural or data-flow analysis to distinguish different tasks.；Use finer-grained alignment methods to avoid false positives in low-similarity cases.

### case_id=1426 FN partial_functionality

- 方法: `sendExceptionToServer` vs `retrieveTemplate`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends exception details to a server via HTTP POST and reads the response.
- B 摘要: Retrieves a web template from a URL via HTTP GET and caches it.
- 静态失败原因: Low lexical overlap (Jaccard 0.208), different method names and API usage (POST vs GET), and additional encoding logic obscured the common URL reading sub-pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often annotates pairs with similar resource usage patterns (URL reading) as clones, even if the overall functionality differs.
- 共享行为: Both open a URL connection and read response content line by line into a StringBuilder.
- 行为差异: A sends a POST request with encoded form data; B performs a simple GET.；A includes error handling for IOException; B throws Exception.；A does not cache; B caches the result.；A performs extensive URL encoding; B does not.
- 修正建议: Enhance model with dataflow analysis to identify common sub-patterns like URL connection + read lines.；Use graph-based representations to capture control flow and data dependencies.

### case_id=1427 FN partial_functionality

- 方法: `getFile` vs `decodeFileToFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies its endpoint attribute in XML, and saves it to a temporary directory, returning the file path.
- B 摘要: Reads a Base64-encoded file and decodes it, writing the output to another file, returning a boolean success flag.
- 静态失败原因: Low token Jaccard (0.14) and distinct API tokens (URL, WSDL, XML vs Base64, decode) likely caused the model to focus on surface-level differences, missing the shared high-level I/O pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled them as Type-4 clones because both are file I/O utilities performing a transformation (download/modify vs decode) on input and writing to output, despite different specific operations.
- 共享行为: Both perform file I/O with streams (input reading and output writing).；Both involve file creation and stream closure in try-catch blocks.；Both handle IOException.
- 行为差异: A reads from a network URL; B reads from a local file.；A modifies XML content; B decodes Base64 encoding.；A returns a String (file location); B returns a boolean.；A has multiple exception types; B only catches IOException.
- 修正建议: Incorporate program analysis to detect common I/O patterns across diverse APIs.；Use data flow analysis to highlight input-output relationships and transformation steps.；Augment training data with more semantically similar yet lexically diverse pairs.

### case_id=1428 FN partial_functionality

- 方法: `copyResource` vs `copy`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource (URL or file) to a destination file; may throw Exception if resource not found.
- B 摘要: Copies a file to another file with extensive validation and error messages; throws IOException.
- 静态失败原因: The low token Jaccard (0.23) and different method signatures (private vs public, different parameter types) likely caused GraphCodeBERT to miss the shared byte-copying loop, as static models rely heavily on token overlap and structural patterns.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider these clones because the core functionality is copying data from input to output, and the structural similarity in the while loop pattern is enough for broad Type-3/4 clone annotation.
- 共享行为: Both copy data from an input source to an output file；Both use a loop to read and write bytes；Both close input and output streams
- 行为差异: copyResource accepts resource via string (URL or file path); copy only accepts File objects；copy performs many pre-checks (existence, readability, directory, etc.); copyResource only checks if URL non-null or file exists；copy uses buffered reading (4KB buffer); copyResource reads single byte at a time；copy has robust finally block to close streams; copyResource closes sequentially without null checks
- 修正建议: Increase training data with diverse file copy implementations；Incorporate dataflow analysis to capture the core copy loop；Use AST alignment to identify common subgraphs despite different wrappers

### case_id=1429 FN partial_functionality

- 方法: `serialize` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Serializes an IMS content package to an OutputStream by creating a temporary file and copying its contents.
- B 摘要: Retrieves a resource as an InputStream, caching it locally from a URL if not already cached.
- 静态失败原因: Low token Jaccard (0.084) and distinct method names prevented lexical overlap; static embeddings likely captured different API usage patterns leading to prediction of non-clone.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have considered them clones due to broad Type-4 similarity as both are I/O utility functions dealing with files and streams, but the functionality is fundamentally different.
- 共享行为: Both involve file I/O and stream handling；Both create or use temporary files；Both handle exceptions with try-catch
- 行为差异: A writes to an OutputStream; B returns an InputStream；A works with a local package; B fetches from a remote URL；A includes parsing; B includes caching logic；A deletes previous temp file; B checks cache for existing file
- 修正建议: Incorporate control-flow and data-flow analysis to distinguish different I/O patterns；Use graph-based representations like code property graphs；Train on more diverse non-clone pairs with similar surface tokens

### case_id=1430 FN boilerplate_overlap

- 方法: `readGeoParserResult` vs `import_hints`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads geo parser result from a URL, parses XML to extract place names and gazetteer entries, with retry logic.
- B 摘要: Reads puzzle hints from a file or URL, parses space-separated tokens to place pieces on a board, returning success boolean.
- 静态失败原因: Low token-level overlap (Jaccard 0.1257) and different domain-specific keywords caused the model to focus on surface differences, missing the abstract I/O pattern that suggests functional similarity.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may label these as clones because both are data import/parsing routines with a similar overall structure (open stream, read, parse, handle exceptions), considered Type-4 (functionally similar) based on the abstract I/O pattern.
- 共享行为: Open a URL connection or file stream；Read input line by line；Parse the input (XML or tokenized lines)；Handle exceptions with try-catch
- 行为差异: Input format: XML vs space-separated text；Output: returns a collection of tuples vs boolean success；Actions: builds data structures vs mutates board state；Retry logic present in A, absent in B
- 修正建议: Use dataflow analysis to detect common I/O patterns across different domains；Incorporate AST-based features that abstract variable names and specific API calls；Train with more diverse data to recognize abstract functionality rather than lexical similarity

### case_id=1431 FP partial_functionality

- 方法: `actionPerformed` vs `encodeFileToFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Handles GUI action commands, opens file choosers, and updates UI preferences.
- B 摘要: Encodes an input file to an output file using Base64 encoding.
- 静态失败原因: The model may have been misled by the presence of file-related terms (file, stream, buffer) in both functions, despite the vast difference in overall functionality. Additionally, code_a's length and truncation may have caused the model to miss its core event-handling logic.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely marks them as non-clones because they are functionally unrelated; one is a GUI event handler, the other a file encoding utility. Even though both involve files, the semantics and complexity are entirely different.
- 共享行为: Both involve file operations (reading/writing)；Both use InputStream/OutputStream (though in different contexts)
- 行为差异: Function A is a GUI event handler with multiple command branches; Function B is a static utility for base64 encoding；Function A updates UI components and preferences; Function B performs file encoding and returns success；Function A has complex conditional logic and user interaction; Function B has straightforward stream reading/writing
- 修正建议: Improve model's ability to understand the high-level purpose of functions despite API-level similarities；Use longer context or attention to capture the core logic (e.g., GUI event handling vs. data encoding)；Include structural information like control flow to differentiate between event dispatch and sequential processing

### case_id=1432 FP boilerplate_overlap

- 方法: `main` vs `decodeFileToFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `1.0`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Parses a Prolog file and generates Java adapter classes and a JAR file based on configuration.
- B 摘要: Decodes a Base64 encoded file to a plain file.
- 静态失败原因: The model likely overemphasized surface-level similarities like common I/O boilerplate (File, IOException, try-catch, finally) and missed the entirely different core logic and library-specific operations.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clones as 0; these functions have completely different purposes (code generation vs Base64 decoding) and low token similarity, so they are correctly labeled as non-clones.
- 共享行为: Both read from a file and write to a file；Both use I/O streams and handle exceptions；Both print stack traces on errors
- 行为差异: A is a complex code generator; B is a simple decoding utility；A writes a JAR file; B writes a plain file；A uses many specific libraries (Parser, ClassWriter); B uses Base64 library；A has conditional logic for debug mode; B has no such branching
- 修正建议: Incorporate more robust semantic analysis to distinguish core functionality from boilerplate；Use context-aware models that capture long-range dependencies and library-specific semantics；Include fine-tuning with examples that have similar boilerplate but different semantics

### case_id=1433 FN partial_functionality

- 方法: `setBundleInfoName` vs `register`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Updates bundle names in a list by parsing key-value pairs from a URL's content.
- B 摘要: Registers a new user by encoding password, setting attributes, creating a phpBB forum user via URL call, persisting user entity, and sending confirmation email.
- 静态失败原因: Static models like BERT or GraphCodeBERT may have difficulty capturing the overall semantic purpose and depend more on token-level similarity. The low Jaccard and different method names likely led the model to predict non-clone; however, both share a structural pattern that might be overlooked by models that focus on surface tokens.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this as a clone (Type-3) because both functions follow a common pattern: opening a URL, reading lines, and returning boolean, with similar exception handling structure. The overall flow is comparable despite different domain logic.
- 共享行为: Both open a URL and read lines from its input stream using BufferedReader；Both handle IOException and return a boolean status
- 行为差异: Function A parses 'key=value' lines to update existing BundleInfo objects, while Function B creates a new User, interacts with a phpBB forum, persists to database, and sends emails；Function A has a simple loop updating a list, whereas Function B has multiple steps: password encoding, authority assignment, hash generation, URL construction, forum registration, entity persist, email sending
- 修正建议: Incorporate structural or flow-based features (e.g., control flow graphs) to recognize common patterns beyond token overlap；Use a model that can capture intent, such as code summarization or contrastive learning on functional similarity

### case_id=1434 FN partial_functionality

- 方法: `doVersionCheck` vs `seeURLConnection`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Checks version by reading a URL and parsing specific fields.
- B 摘要: Reads content from a hardcoded URL and logs it.
- 静态失败原因: Static BERT/GraphCodeBERT models often rely on lexical and structural features. The token Jaccard is low (0.2089), indicating low lexical overlap. The models may have focused on the distinct method names and unique strings (e.g., 'version-check.url' vs 'wantmeet.iptime.org') and the different processing logic (parsing vs. appending). Additionally, the functions have different signatures and control flow (e.g., error handling with try-catch). The model likely saw them as too different due to these surface-level differences.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider this a Type-3 clone because both functions share the core behavior of reading lines from a URL via BufferedReader, which is a common functional pattern. The differences in URL source, data processing, and error handling are considered superficial variations.
- 共享行为: Open a URL, get input stream, wrap in BufferedReader, read lines until null, close reader.
- 行为差异: A uses configurable URL from property, B uses hardcoded URL; A parses lines for version info, B concatenates all lines; A handles IOException with error dialog, B throws Exception; A shows/hides wait cursor on View, B does not; A calls another method after reading, B only logs.
- 修正建议: Train models to recognize high-level API usage patterns, e.g., URL open -> BufferedReader -> readLine -> close.；Use dataflow or control flow graphs to capture common I/O patterns.；Incorporate method-level similarity based on API call sequences.

### case_id=1435 FN partial_functionality

- 方法: `doTransfer` vs `handledRun`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: HTTP request forwarding proxy that reads incoming request, copies headers and body to a new URL connection, and returns the response.
- B 摘要: Downloads a gamedata XML file from a remote URL, checks version, and updates local file if outdated.
- 静态失败原因: Static BERT/GraphCodeBERT methods often rely on token overlap and structural patterns; here the token Jaccard is low (0.14) and the method signatures are different. The model likely focused on the different method names, different exception handling, and different overall purpose, missing the high-level semantic similarity of URL I/O operations.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as Type-4 semantic clones because they both perform network I/O operations: opening a URL, reading data, and writing to an output. The core functionality of transferring data from a URL to a stream is shared, even though the context and specific handling differ.
- 共享行为: Both open a URL connection and read data from it；Both write data to an output stream；Both use try-catch for IO exceptions
- 行为差异: A is a generic HTTP proxy, B is a specific version-checking downloader；A copies request headers, B does not；A forwards request body, B only writes file data；A handles HTTP response codes, B does not
- 修正建议: Improve representation learning to capture high-level behavioral patterns beyond token overlap；Incorporate data-flow analysis to detect common I/O operations；Use contrastive learning on pairs with low lexical but high semantic similarity

### case_id=1436 FN lexical_or_api_overlap

- 方法: `getFile` vs `readAndRewrite`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.3`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies its endpoint, and saves it to a temporary file, returning the file path.
- B 摘要: Reads a DICOM image file, parses its pixel data, and writes it to another file (no return value).
- 静态失败原因: Static BERT/GraphCodeBERT likely relied on lexical and structural token overlap, which is very low (Jaccard 0.072). The models failed to recognize the abstract pattern of 'read-process-write' common to both functions, instead focusing on specific API calls (Axis vs DICOM) and returning different types.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may consider both as 'file download/transform' operations broadly, or may have annotated based on partial functionality of reading input, transforming data, and writing output (Type-4 clone). The low lexical overlap is outweighed by the high-level structural similarity in file I/O flow.
- 共享行为: Both involve reading from an external source (URL/file) and writing to a file；Both use I/O streams and exception handling (IOException derived)；Both perform some data transformation before writing output
- 行为差异: Input source: URL (a) vs File (b)；Return type: String (file path) (a) vs void (b)；Data processing: XML endpoint replacement (a) vs DICOM pixel data copying (b)；Libraries: Axis/XML utilities (a) vs DICOM/ImageIO (b)
- 修正建议: Train models on abstract syntax trees or data-flow graphs to capture high-level functional patterns；Incorporate information retrieval style features (e.g., topic modeling) to identify broader semantic categories；Use domain adaptation or fine-tuning on specific clone benchmark types (Type-3/Type-4) to learn functional similarity beyond lexical overlap

### case_id=1437 FN benchmark_preference_bias

- 方法: `copyResource` vs `convert`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Copies a resource from a URL or file to a destination file byte by byte.
- B 摘要: Converts an ACRNEMA/DICOM file to DICOM format, adding UIDs and handling pixel data inflation.
- 静态失败原因: The static BERT model correctly identified low token overlap (Jaccard 0.12782) and semantic dissimilarity, leading to a non-clone prediction. It likely did not fail; the BCB label appears incorrect.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have considered both as 'resource transfer' operations, interpreting the broader category of file I/O as functional similarity, but this seems overly broad and inconsistent with typical Type-4 annotations.
- 共享行为: Both open an input stream and write to an output stream.
- 行为差异: A is generic file copy; B is specific DICOM conversion with complex metadata manipulation.；B involves parsing, conditionals on DICOM tags, and pixel data transformation; A does not.；B handles inflation and file format detection; A does not.
- 修正建议: Re-evaluate BCB annotation for this pair; the functions differ significantly in purpose and complexity.

### case_id=1438 FN benchmark_preference_bias

- 方法: `doGet` vs `decodeBody`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Handles HTTP GET request for a portal page, including parameter parsing, permission checks, logging, and response writing.
- B 摘要: Decodes an input stream body based on Content-Transfer-Encoding (quoted-printable or base64) and returns a BinaryTempFileBody.
- 静态失败原因: The low token Jaccard (0.052) and very different code structures likely caused the static model to correctly predict non-clone. The failure is on the BCB side, not the model.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as a false positive (1) due to an error in the benchmark annotation; there is no apparent functional similarity even under broad Type-3/Type-4 definitions.
- 行为差异: A is an HTTP servlet method; B is a utility method for stream decoding.；A involves multiple database/property lookups and user permissions; B only handles encoding conversion and I/O copying.；A writes to HTTP response; B writes to a temporary file body.；A has extensive logging and error handling for page retrieval; B throws IOException only.
- 修正建议: Re-annotate this pair as non-clone in BigCloneBench.；Improve BCB annotation consistency for unrelated functions.

### case_id=1439 FP partial_functionality

- 方法: `sendPost` vs `doVersionCheck`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends an HTTP POST request with parameters and returns the response body as a string.
- B 摘要: Checks for software version updates by reading a remote version file and comparing with current version, displaying appropriate dialogs.
- 静态失败原因: Static models may rely on token and structural overlap (e.g., URL, BufferedReader, readLine) and miss the semantic difference in intent, output, and API usage (POST vs GET, return vs void with UI).
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB typically annotates clones based on functional similarity. Here, the core functionality is fundamentally different (generic POST utility vs specific version check), so BCB likely considers them non-clones despite shared low-level I/O patterns.
- 共享行为: Both open a URL and read lines from an input stream using BufferedReader；Both use a while loop to read lines；Both handle exceptions and display messages
- 行为差异: A performs HTTP POST with custom parameters; B performs HTTP GET to a hardcoded URL；A returns the concatenated response; B parses specific lines and updates UI；A uses MsgPrint for messages; B uses jEdit GUI utilities；A has no view parameter; B uses view for cursor and dialogs
- 修正建议: Incorporate data-flow analysis to distinguish between POST and GET requests；Improve understanding of API calls and their side effects (e.g., return type vs UI updates)；Add more training examples that differentiate generic utilities from specific applications

### case_id=1440 FN partial_functionality

- 方法: `fileDownload` vs `postData`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a file from a URL and saves it to a local directory, hardcoding the output filename as download.pdf.
- B 摘要: Posts data to a web server using HTTP POST, setting necessary request properties and discarding the response.
- 静态失败原因: Static BERT/GraphCodeBERT models rely on lexical and structural similarities; the low Jaccard similarity (0.2069) and different method names and stream classes likely caused the model to miss the underlying semantic similarity of HTTP-based data transfer.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely labels this as a clone because both functions perform network I/O operations via URLConnection, which is a common pattern considered semantically similar in BigCloneBench (Type-4).
- 共享行为: Both use URLConnection to interact with remote servers.；Both open a connection and perform I/O operations: reading from an input stream and writing to an output stream.；Both handle some form of data transfer over HTTP.
- 行为差异: Direction of data transfer: A downloads (reads from server, writes to file), B uploads (writes to server, reads response).；Exception handling: A catches and logs exceptions; B throws them to the caller.；Stream types: A uses BufferedReader/BufferedWriter for character I/O; B uses PrintStream for output and BufferedReader for input.；Parameterization: A takes a single URL and destination directory; B takes protocol, host, form, and data.
- 修正建议: Enhance models to recognize abstract network I/O patterns beyond exact token matches.；Incorporate data-flow analysis to capture connections between URL creation, stream opening, and read/write operations.；Use domain-specific pre-training or knowledge of common network programming idioms (e.g., URLConnection usage).

### case_id=1441 FN partial_functionality

- 方法: `addIDs` vs `addQDInformation`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Queries a web service with a metabolite name and parses HTML to extract and set various IDs (PubChem, ChEBI, etc.) on a PeakListRow, returning a score.
- B 摘要: Reads a local file or remote URL to update project information (qdDate and qdValue) by parsing lines that start with 'pg ' or 'pt '.
- 静态失败原因: Low token overlap (0.196) and different variable names, methods, and control flow led the model to emphasize syntactic differences, missing the abstract functional similarity that BCB might recognize.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as 'data retrieval and population' functions, viewing them as Type-4 clones despite different domains due to similar high-level purpose.
- 共享行为: Both read from external sources (HTTP URL or file) using BufferedReader.；Both parse lines conditionally and set fields in data objects.；Both handle exceptions (IOException).
- 行为差异: Different data structures: PeakListRow vs Information objects.；Different URL/file formats and parsing logic.；Return type: int vs void.；Different domains: metabolite IDs vs project QD info.
- 修正建议: Use functional summarization or program slicing to capture high-level similarity.；Incorporate domain knowledge or API usage patterns.；Train on broader function-level semantics rather than token-level.

### case_id=1442 FN partial_functionality

- 方法: `main` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a file from source to destination using NIO FileChannel and ByteBuffer.
- B 摘要: Retrieves a resource from a URL, caches it to a local file if not already cached, and returns an InputStream to the local file.
- 静态失败原因: Static BERT models rely heavily on token overlap and structural patterns; the low Jaccard similarity (0.158) and different method signatures/semantics made the model see them as non-clone, missing the broad functional similarity in the I/O loop.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB Type-4 cloning tolerates different implementations that achieve similar functionality; both functions perform file copying (one direct file copy, one URL-to-file caching), sharing the core I/O pattern.
- 共享行为: Both involve reading data from a source and writing to a file/stream.；Both use a while-loop to copy bytes.
- 行为差异: A uses FileChannel and ByteBuffer; B uses BufferedInputStream and byte-by-byte copy.；A does not handle caching or HTTP connections; B does.；A exits on wrong arguments; B returns null on error.
- 修正建议: Enhance model with data-flow analysis to detect common I/O patterns.；Use contrastive learning on partial functional similarity.

### case_id=1443 FN partial_functionality

- 方法: `copyOverWarFile` vs `modifyApplicationMessage`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies war files from a source directory to theAppsDataDir and extracts them.
- B 摘要: Modifies a localized properties file by replacing or adding a key-value pair.
- 静态失败原因: Static BERT models rely on token overlap and structural patterns; the token Jaccard is low (0.146), method signatures differ, and the high-level 'copy then modify' semantic similarity is not captured by surface-level features. The model likely saw them as unrelated due to different API calls and variable names.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely views both as Type-4 semantic clones because they share a high-level pattern: copy a configuration/resource file and then apply transformations. The differences in file type and specific operations are considered incidental.
- 共享行为: Both copy a resource file to a destination and then modify it；Both involve file I/O with exception handling；Both are used in application configuration or deployment
- 行为差异: A copies binary war files; B copies and modifies text properties files；A has no parameters; B takes locale, messageName, messageValue；A uses IOUtils.copy for binary copy; B uses character-by-character copy；A calls moveUnzipAndExtract after copy; B modifies properties content directly
- 修正建议: Train models to recognize high-level program intent using functional summaries；Use contrastive learning on Type-4 clones that vary in surface form but share intent；Incorporate data-flow or control-flow graphs that abstract away specific file types

### case_id=1444 FN benchmark_preference_bias

- 方法: `sendExceptionToServer` vs `createHTML`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Sends exception report to a remote server via HTTP POST.
- B 摘要: Generates HTML page by reading CSS and querying database.
- 静态失败原因: Static BERT predicted non-clone correctly based on low token overlap and different control flow; BCB annotation appears erroneous.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled as clone due to superficial overlap in using URL, BufferedReader, and exception handling, despite no functional similarity.
- 共享行为: Both handle IOException with try-catch；Both use BufferedReader and InputStreamReader
- 行为差异: Different purposes: sending data vs. generating HTML；Different inputs/parameters；Different output: void vs. HTML string；Different I/O targets: remote server vs. local resource
- 修正建议: Re-evaluate BCB annotation for this pair；Use functional semantics beyond syntactic patterns

### case_id=1445 FP partial_functionality

- 方法: `readZoneIDs` vs `getVersion`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads integers from a classpath resource file and returns them as a HashSet.
- B 摘要: Fetches a version string from a remote HTTP URL and returns it.
- 静态失败原因: The static BERT model likely overemphasized the superficial structural similarity of URL opening and line reading, ignoring the critical semantic differences in data source and processing.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB typically considers non-clones when functions have different purposes, input sources, or output types, even if the structural skeleton is similar.
- 共享行为: Both open a URL and read lines from an input stream.；Both use try-catch to handle exceptions.；Both return a value that is populated from the read lines.
- 行为差异: readZoneIDs reads from a local classpath resource; getVersion reads from a remote HTTP URL.；readZoneIDs parses each line as an integer and adds to a set; getVersion stores only the first line as a string.；Return types differ: HashSet<Integer> vs String.；Different error handling: readZoneIDs prints stack trace; getVersion sets version to null.
- 修正建议: Incorporate data flow and type information into the embedding.；Use contrastive learning with hard negatives that share structure but differ in semantics.；Add attention to variable usage and method signatures.

### case_id=1446 FP lexical_or_api_overlap

- 方法: `getRequestContent` vs `getEncoding`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Gets the first line of content from a URL.
- B 摘要: Extracts the character encoding from HTTP response headers or content.
- 静态失败原因: Static BERT/GraphCodeBERT likely focused on the high lexical overlap of common HTTP I/O patterns (URLConnection, BufferedReader, readLine) and missed the distinct functional logic and output.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels these as non-clones because they serve different purposes (returning content vs. encoding) and the similarity is only in boilerplate HTTP I/O code.
- 共享行为: Both use URLConnection to open a connection；Both read from an input stream using BufferedReader
- 行为差异: getRequestContent returns the first line of the response body; getEncoding returns the detected encoding or a default.；getRequestContent only reads one line; getEncoding may read many lines to find charset.；getEncoding parses HTTP headers for Content-Type; getRequestContent does not.；getRequestContent closes connection; getEncoding does not explicitly disconnect.
- 修正建议: Incorporate training examples with similar API usage but different semantics to reduce reliance on lexical overlap.；Use data flow or control flow features to distinguish different intents.；Add attention mechanisms that highlight distinct identifiers and method names.

### case_id=1447 FP boilerplate_overlap

- 方法: `readZoneIDs` vs `executeHttpGet`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads zone IDs from a local resource file line by line, parsing each as an integer into a HashSet.
- B 摘要: Performs an HTTP GET request and returns the response body as a JSONObject.
- 静态失败原因: The static model likely relied on lexical and structural overlap like 'while ((... = ...readLine()) != null)' and exception handling, ignoring the distinct data sources and output transformations.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clone because the functions have fundamentally different purposes (file I/O vs HTTP client), different return types, and only superficial structural overlap (readLine loop). BCB prioritizes functional relevance over boilerplate patterns.
- 共享行为: Both read lines from an input stream using a while loop；Both use InputStreamReader and BufferedReader-like constructs
- 行为差异: A reads from a local file resource, B from an HTTP response；A returns a HashSet<Integer>, B returns a JSONObject；A catches Exception and prints stack trace, B throws Exception；A uses LineNumberReader, B uses BufferedReader
- 修正建议: Incorporate data-flow analysis to trace dependencies from input to output；Use type information to distinguish return types and source types；Add control-flow context such as method names or external library usage

### case_id=1448 FP lexical_or_api_overlap

- 方法: `readUNI` vs `sendRequestObjectResponse`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a tab-separated values file from a URL and parses it to populate a list of descriptions.
- B 摘要: Sends an XML request to a servlet, receives the response, saves it to a file based on content type, and opens it in a browser, returning the filename.
- 静态失败原因: Static BERT/GraphCodeBERT may have been misled by common API usage (URL, InputStream, exception handling) and overall structure (try-catch-finally), ignoring the distinct functional logic and control flow. The model may have overestimated similarity due to overlapping tokens and boilerplate code.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled as non-clone because the two functions have entirely different purposes: one is for data ingestion (parsing a remote TSV file) and the other is for sending a request and handling response (invoking a servlet and storing results). Even broad Type-4 does not consider them functionally similar.
- 共享行为: Both open a network connection (URL, InputStream)；Both use try-catch for exception handling；Both involve reading from an InputStream
- 行为差异: readUNI parses a TSV file line by line and populates a list; sendRequestObjectResponse sends an XML request and saves the response to a file；readUNI returns void; sendRequestObjectResponse returns a filename string；readUNI has no output side effects; sendRequestObjectResponse writes to file system and opens browser；readUNI uses Scanner for parsing; sendRequestObjectResponse uses GZIP compression and URLConnection with output
- 修正建议: Train model with more emphasis on functional semantics vs. surface API similarity；Incorporate data flow or program dependency analysis；Use contrastive learning to distinguish similar-looking but different-purpose functions

### case_id=1449 FN lexical_or_api_overlap

- 方法: `copyResource` vs `internalCopy`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource from a URL or local file to a destination file using byte-by-byte streaming, closing streams after.
- B 摘要: Copies a source file to a destination file using buffered streaming with an 8KB buffer, skipping files named 'Thums.db' and printing a copying message.
- 静态失败原因: Static BERT models rely heavily on token overlap and surface-level patterns. The token Jaccard similarity is low (0.27). The models may not capture the abstract streaming copy pattern due to different API usage (read() vs read(byte[])) and different control flow, leading to a false negative.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB often treats partial functionality similarity as a clone, especially when the core behavior (copying) is identical. The differences (buffering, skipping, printing) are considered minor, and the broad Type-3/Type-4 clone classification accepts such variations.
- 共享行为: Both copy data from an input source to an output file using Java I/O streams.；Both read and write until the end of the stream, then close the streams.；Both throw exceptions on I/O errors.
- 行为差异: A can handle URLs as source; B only handles files.；A reads byte-by-byte; B reads in 8KB chunks using a buffer.；B skips files named 'Thums.db'; A does not skip any files.；B prints a message during copying; A does not.
- 修正建议: Incorporate data-flow or program dependency analysis to capture the streaming copy pattern.；Train on more diverse examples of file copy functions with varying implementations.；Use graph-based representations (e.g., AST or CFG) to better match high-level semantics.

### case_id=1450 FN partial_functionality

- 方法: `getContent` vs `seeURLConnection`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches content from an HTTP request using HttpClient, reads line by line, and returns the accumulated string.
- B 摘要: Opens a URL connection, reads the input stream line by line, appends to a StringBuffer, and logs the result (no return).
- 静态失败原因: Static BERT/GraphCodeBERT models rely heavily on lexical overlap and surface structure. The two functions have low token Jaccard (0.26), different method names, different API classes (HttpClient vs URLConnection), and different return types. The model likely focused on these differences and missed the higher-level semantic similarity of fetching and reading HTTP content.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often accepts Type-3/Type-4 clones where both functions perform the same overall task (fetching URL content) despite differences in API usage, return behavior, or minor control flow. The core goal—reading HTTP content line by line—is shared, so BCB labels it a clone.
- 共享行为: Both fetch content from a remote endpoint via HTTP；Both read the content line by line using BufferedReader；Both use StringBuffer to accumulate the lines
- 行为差异: Function A uses HttpClient with timeout settings; B uses URLConnection without explicit timeouts；Function A returns the result as a String; B logs it and returns void；Function A reads line breaks into the buffer; B does not；Function A and B have different method signatures and exception handling
- 修正建议: Incorporate dataflow analysis to identify I/O operations and their destinations；Use graph-based representations that capture the sequence of I/O (open, read, close) rather than exact API calls；Train on positive examples with low lexical overlap but similar functional intent (e.g., different client libraries)；Add awareness of common programming idioms (e.g., downloading content) that are independent of the exact library

### case_id=1451 FP boilerplate_overlap

- 方法: `getJSONData` vs `loadURL`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches JSON from a URL using HttpClient and parses it into a JSONObject.
- B 摘要: Downloads a URL's content to a temporary file with optional HTTP authentication and updates a GUI label with progress.
- 静态失败原因: Static BERT models may overemphasize lexical/structural similarities like 'BufferedReader', 'InputStream', and common HTTP code patterns, while ignoring semantic differences in output, side effects, and method signatures.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically requires a strong functional similarity (e.g., same core task) to label as clone; these functions have different purposes (JSON retrieval vs. file download with UI), so they are likely labeled non-clone.
- 共享行为: Both read HTTP response content line by line using BufferedReader
- 行为差异: Function A returns a JSONObject for further processing; function B writes to a file and updates a GUI label.；Function A uses HttpClient and handles exceptions by returning null; function B uses URLConnection and throws IOException.；Function B includes authentication support and progress reporting; function A does not.；Function A parses the response as JSON; function B does not parse the content, just writes raw lines.
- 修正建议: Incorporate method signature and return type information into the model.；Use dataflow analysis to distinguish between parsing and file-writing behavior.；Apply contrastive learning with examples that have boilerplate overlap but different intents.

### case_id=1452 FP boilerplate_overlap

- 方法: `doPost` vs `perform`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: doPost updates user profile from request parameters, hashes password, sets visibility, persists user via JPA, and redirects.
- B 摘要: perform classifies a concept by sending XML to a remote service, parsing the result, and storing it in session.
- 静态失败原因: Static BERT/GraphCodeBERT likely overemphasized structural patterns like request/response parameter handling, session usage, exception blocks, and redirects, while failing to capture the completely different data processing tasks.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clones when functions perform distinct tasks despite superficial structural similarities. Here, the core logic is completely unrelated.
- 共享行为: Both are HTTP request handlers extracting parameters from request.；Both use session to store/retrieve attributes.；Both perform redirects or forward on error/success.
- 行为差异: A updates user details and persists to database; B performs a classification via external XML service.；A uses MD5 hashing for password; B sends XML over HTTP connection and parses response.；A uses JPA entity manager; B uses custom beans and XML property handler.；Error handling strategies differ: A redirects to error.jsp; B uses mapping.findForward with status strings.
- 修正建议: Incorporate contrastive learning to distinguish between structurally similar but semantically different functions.；Use data augmentation to reduce reliance on common boilerplate patterns.

### case_id=1453 FN boilerplate_overlap

- 方法: `decodeFileToFile` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Decodes a Base64-encoded file and writes decoded bytes to an output file, returning success status.
- B 摘要: Retrieves a resource by name, caches it locally with HTTP support, and returns an InputStream to the resource.
- 静态失败原因: Static BERT/GraphCodeBERT likely relied on lexical/syntactic features and low token overlap, missing the structural boilerplate similarity that BCB values.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may consider these clones due to high structural similarity in the stream copy pattern and exception handling, typical of Type-3 clones where the same template is reused with different core operations.
- 共享行为: Both use InputStream/OutputStream for reading and writing data.；Both use buffered streams for efficiency.；Both have try-catch-finally blocks for resource cleanup.；Both read data in a loop and write it to an output.
- 行为差异: A decodes Base64, B does not.；A writes decoded data to a file, B returns an InputStream or null.；B includes caching logic, HTTP connections, and conditional file existence checks.；A returns a boolean indicating success, B returns an InputStream or null.
- 修正建议: Incorporate structural features like control flow graphs or data flow to capture similar I/O patterns.；Add training data that emphasizes boilerplate overlaps as potential Type-3 clones.

### case_id=1454 FN benchmark_preference_bias

- 方法: `setPayload` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: setPayload copies data from a headless data file to a header file and advances an index, returning true if successful.
- B 摘要: buildSiteForEdit processes a site for editing by iterating over pages, reading XML, performing transformations, and writing output files.
- 静态失败原因: The static model correctly identified low similarity (Jaccard 0.04) and predicted non-clone, which aligns with semantic analysis. The apparent failure is due to BCB's possibly erroneous label, not the model's fault.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as a clone due to a broad interpretation of file manipulation or because both functions contain file reading/writing patterns, but the overall functionality and structure are vastly different, indicating a likely labeling error.
- 共享行为: Both methods involve file I/O (reading and writing files).
- 行为差异: setPayload is a simple file copy with index tracking; buildSiteForEdit is a complex multi-step site generation.；setPayload has a loop over headers; buildSiteForEdit loops over pages and performs XML transformations.；setPayload uses FileChannel transferTo; buildSiteForEdit uses various file and string processing utilities.
- 修正建议: Re-evaluate BCB labels for this pair to ensure ground truth accuracy.；Improve model to handle extremely low lexical overlap and disregard spurious common keywords.

### case_id=1455 FN benchmark_preference_bias

- 方法: `convert` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Converts ACRNEMA stream files to DICOM format by parsing and adding UIDs.
- B 摘要: Builds web pages for editing using XSLT transformations and file inclusion.
- 静态失败原因: Static BERT/GraphCodeBERT correctly identified them as non-clones due to very low token overlap and disparate domain-specific vocabulary; the failure is that BCB label is erroneous, so the model's prediction aligns with intuition.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled these as clones due to very broad similarity as file-processing utilities with loops and I/O, but the actual semantics are entirely different, making this likely a benchmark annotation error.
- 共享行为: Both perform file I/O operations；Both use try-finally for resource management；Both involve loops iterating over data
- 行为差异: Different domains: DICOM conversion vs web page generation；Different data formats: binary pixel data vs XML/text；Different parameters and processing logic；Function A is self-contained; function B depends on many external objects and properties
- 修正建议: Re-evaluate BCB label for this pair; consider removing from clone set；If retaining as clone, clarify criteria for Type-4 clones at extreme abstraction

### case_id=1456 FP lexical_or_api_overlap

- 方法: `getLinksFromURLFast` vs `sendPost`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Parses HTML from a URL to extract hyperlinks and their text.
- B 摘要: Sends an HTTP POST request with parameters and returns the response body.
- 静态失败原因: The static model likely over-indexed on overlapping API usage (URL, BufferedReader, reading lines) and ignored the distinct parameter handling, regex parsing, and output types, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clones for functions with different core functionality, even if they share some API patterns. The extraction vs. posting distinction is fundamental.
- 共享行为: Both use URL and URLConnection to access a resource over HTTP；Both read lines from an input stream using BufferedReader；Both handle exceptions (though differently)
- 行为差异: A extracts links from HTML; B sends POST data and reads response；A uses regex to parse anchor tags; B sends form parameters via POST；A returns two vectors; B returns a single string；A has time-checking and debugging output; B does not
- 修正建议: Incorporate data-flow analysis to track how input parameters are used；Add attention to method names and return types；Use type-aware embeddings to differentiate HTML parsing from HTTP post

### case_id=1457 FP lexical_or_api_overlap

- 方法: `actionPerformed` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.85`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads SNP IDs from a gzipped file and sends them to NCBI E-Utilities via HTTP POST, outputting the response to stderr.
- B 摘要: Handles various user interface commands for a genealogy application's settings dialog, updating preferences and UI components.
- 静态失败原因: Static BERT/GraphCodeBERT may have been misled by the similar boilerplate (actionPerformed, try-catch, IOException, reader, close) and the presence of common keywords like 'url', 'inputstream', 'outputstream' in code A and 'file' in code B. The model may not have captured the overall semantic context sufficiently.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels as non-clone because despite same method signature, the functionality is completely different and not even partially similar.
- 共享行为: Both are actionPerformed methods that handle ActionEvent；Both use try-catch for IOException
- 行为差异: Code A performs a network request to an external service; Code B updates local UI and preferences.；Code A processes SNP IDs; Code B processes settings commands.；Code A writes to stderr; Code B displays dialogs and updates UI.；Code A uses GZIPInputStream; Code B uses JFileChooser and Swing.
- 修正建议: Improve training to handle more diverse semantics in same boilerplate methods；Incorporate longer range dependencies and dataflow information；Use graph-based representations to distinguish control flow and data dependencies

### case_id=1458 FP partial_functionality

- 方法: `handleHandshake` vs `checkForUpgrade`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Handles a Minecraft client handshake by validating the server key and performing session authentication via HTTP request.
- B 摘要: Checks for software upgrades by querying a remote license server, parsing the response, and updating local database with upgrade records.
- 静态失败原因: The static model likely overfitted to lexical and structural overlap (e.g., URL, BufferedReader, if-else blocks) that appear frequently in network-related code. It missed the semantic difference in the purpose and data flow, leading to a false positive.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB labels non-clone because the functions serve entirely different high-level purposes and belong to distinct projects. Although they share a common pattern of HTTP request and response parsing, the overall functionality is not similar enough to be considered a clone under BCB's criteria.
- 共享行为: Both make HTTP requests to remote servers.；Both read responses using BufferedReader from URL connections.；Both have conditional logic to handle server response outcomes.
- 行为差异: Different application domains: Minecraft vs. TobeOS upgrade.；Different error handling: shutdown connection vs. show UI messages.；Different data processed: username/handshake vs. version/MAC/license.；Different side effects: send login packet vs. update database and UI.
- 修正建议: Train models with more diverse data to reduce reliance on boilerplate patterns.；Use dataflow analysis to distinguish how data retrieved from HTTP is used differently.；Incorporate task-specific or domain-aware embeddings to capture high-level intent.

### case_id=1459 FP lexical_or_api_overlap

- 方法: `run` vs `loadURL`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a URL, parses lines into version, url, and additional info, handles errors with custom messages, and notifies listeners.
- B 摘要: Reads a URL with optional authentication, writes content to a temporary file while updating a progress label, and throws IOException.
- 静态失败原因: Static BERT models may over-rely on lexical overlap and common API patterns (URL, BufferedReader, while readLine), ignoring deeper semantic differences in the loop body and error handling.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels non-clone because the functions have distinct purposes (information retrieval vs. file download with progress) and different output behaviors (internal state setting vs. file writing).
- 共享行为: Open a URL connection and read lines using BufferedReader
- 行为差异: Function A parses lines by index into separate fields, while B writes all lines to a file；Function A handles errors and notifies listeners, B propagates exceptions and does not handle errors internally；Function B includes authentication handling and progress updates, A does not
- 修正建议: Increase sensitivity to structural differences in the loop body；Incorporate dataflow analysis to distinguish variable usage patterns；Use contrastive learning to separate boilerplate from core logic

### case_id=1460 FP lexical_or_api_overlap

- 方法: `sendRequestObjectResponse` vs `getFullScreenUrl`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Sends an XML request to a configurable server with compression, saves the response to a file, and returns the file path.
- B 摘要: Parses a YouTube page to extract video parameters and constructs a URL for video download.
- 静态失败原因: The model likely over-emphasized overlapping API calls (e.g., URLConnection, BufferedReader) and error handling patterns, while missing the distinct semantic goals.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled non-clone because the functions have entirely different high-level functionalities despite some superficial API overlap, and the token Jaccard is low.
- 共享行为: Both use java.net.URLConnection to make HTTP requests
- 行为差异: Different overall purpose (generic request vs YouTube-specific)；Different input handling (XML request vs HTML parsing)；Different output (file path vs URL string)；Different use of compression and file saving
- 修正建议: Incorporate method name or context embeddings to capture purpose；Use graph-based representations to distinguish data flow and control flow differences

### case_id=1461 FN partial_functionality

- 方法: `getFile` vs `hyperlinkUpdate`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a given URL, optionally modifies the SOAP address endpoint, and returns the local file path.
- B 摘要: Handles hyperlink activation events by fetching the URL content and displaying it in a dialog window.
- 静态失败原因: The functions have very low token overlap (0.0875) and differ in domain and structure, making it hard for lexical-based models to recognize the abstract similarity of URL reading. The models likely rely on surface features and miss the high-level functional commonality.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label as clone because both functions share the core behavior of fetching content from a URL via an InputStream, which is considered a functional similarity (Type-4 clone).
- 共享行为: Both open a URL stream, read data from it, and handle IOException；Both use try-catch for error handling；Both involve closing the input stream after reading
- 行为差异: Function A writes data to a file and modifies XML, while function B displays content in a UI dialog；Function A has extensive logging and throws custom exception, function B uses printStackTrace；Function A is static and returns a String, function B is void and instance method
- 修正建议: Incorporate dataflow analysis to capture stream opening and closing patterns；Use graph-based representations that abstract away domain-specific details；Train on more diverse Type-4 clones with low lexical overlap

### case_id=1462 FP lexical_or_api_overlap

- 方法: `get` vs `importSequences`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Makes an HTTP GET request with game-specific headers (latitude, longitude, count), reads response line by line, filters out comment lines, decodes and returns an array of GameRecord objects.
- B 摘要: Reads sequences from a URL-based data source using ImportHelper, parses FASTA-like format (lines starting with '>'), extracts names and sequences, and stores them in class fields.
- 静态失败原因: The static BERT model likely over-relied on shallow API overlap (URL connections, line reading, try-catch, while loops) and similar control flow structure, ignoring the distinct domain-specific logic and data formats.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels non-clones when functions perform fundamentally different tasks. Here, one is about game records via HTTP, the other about biological sequence import. Even though both read from URLs, the intent and data processing are completely different, hence BCB labels as non-clone.
- 共享行为: Both open a connection to a URL and read textual data line by line.；Both use try-catch for IOException handling.；Both involve parsing lines with tokenization or string processing.
- 行为差异: Function A uses HTTP GET with custom request properties; Function B directly opens an InputStream from a URL.；Function A reads lines filtering those starting with '#'; Function B reads until encountering '>', then parses tokens from that line, and reads sequences until next '>'.；Function A returns a GameRecord array; Function B populates member lists (names, sequences).；Function A is static and generic; Function B is an instance method tied to a GUI component (urlComboBox).
- 修正建议: Incorporate deeper semantic understanding of the operations (e.g., recognizing HTTP headers vs direct stream, parsing format differences).；Use more context about the surrounding class and method signatures to disambiguate.；Train or finetune on larger, more diverse data to reduce sensitivity to generic API patterns.

### case_id=1463 FN benchmark_preference_bias

- 方法: `getResponse` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Parses an HTTP request byte array, extracts the resource path, and returns an HTTP response (200, 404, or 400) as bytes.
- B 摘要: Builds an entire website for editing by transforming XML with XSLT, reading control files, and writing output pages to disk, with extensive error handling and debugging.
- 静态失败原因: The static BERT/GraphCodeBERT model correctly predicted non-clone (0) because the functions are semantically and syntactically very different in terms of purpose and complexity, with low token overlap (0.0837). The model likely captured the lack of shared structure.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have considered them clones due to both containing I/O boilerplate (InputStream/OutputStream, IOUtils.copy, readLines) and exception handling patterns, perhaps under a lenient Type-4 functional similarity based on 'reading input and producing output'.
- 共享行为: Both read from an InputStream and write to an OutputStream；Both use IOUtils for stream copying；Both handle exceptions with AssertionError or IOException
- 行为差异: Function A is a simple, self-contained HTTP response generator; Function B is a large, multi-step site builder with XML transformation, file system operations, and complex string processing；Function A returns a byte array; Function B returns void and writes files；Function B has many parameters and uses properties, while Function A has none；Function B includes DOM and XSLT transformations; Function A does not
- 修正建议: Review BCB annotation criteria to avoid labeling I/O boilerplate as clone；Use stricter semantic equivalence definitions that focus on functional purpose rather than shared library usage

### case_id=1464 FN other

- 方法: `getFile` vs `testTrainingBackprop`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `1.0`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Downloads a WSDL file from a URL, modifies its endpoint attribute, and returns the file path.
- B 摘要: Creates a temporary file with training data, builds a neural network, trains it using backpropagation, and asserts the final error is low.
- 静态失败原因: The static BERT model correctly identified non-clone based on low token overlap and distinct semantic structures. The model's prediction is accurate, but the BCB label is inconsistent; thus the model did not fail but rather disagreed with a potentially erroneous annotation.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may have labeled this as a clone based on broad type-4 criteria that consider high-level file I/O and exception handling as similar, or due to an annotation error. However, the overall functionality is completely different, and under reasonable BCB guidelines this should not be a clone.
- 共享行为: Both use temporary files and file I/O operations；Both involve exception handling (IOException)
- 行为差异: Function A performs XML parsing and manipulation; Function B constructs and trains a neural network；Function A returns a file path; Function B performs assertions with no return value；Function A catches multiple specific exception types; Function B declares IOException only
- 修正建议: Remove this mislabeled pair from the benchmark；Re-evaluate BCB annotation criteria to ensure functional equivalence；Use manual review for ambiguous cases

### case_id=1465 FN boilerplate_overlap

- 方法: `modifyApplicationMessage` vs `run`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.8`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Modifies a locale-specific properties file by replacing or appending a key-value pair.
- B 摘要: Parses an XML menu definition and generates a ZIP archive containing Firefox extension files.
- 静态失败原因: Static BERT models are sensitive to token overlap and structural similarity. The low Jaccard and distinct method names/signatures led the model to correctly predict non-clone, but BCB's label requires broader semantic matching.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may view both as 'resource configuration modification' due to the broad Type-4 category, but the specific domains (i18n properties vs extension packaging) are very different.
- 共享行为: Both perform file I/O operations；Both read from classpath resources；Both handle exceptions with try-catch
- 行为差异: A works with properties files (key-value lines); B works with XML and generates a ZIP archive；A modifies an existing file; B creates a new archive from scratch；A's output is a single properties file; B's output is a multi-entry ZIP containing various file types
- 修正建议: Increase sensitivity to high-level resource processing patterns；Incorporate semantic role labeling to distinguish different types of I/O operations

### case_id=1466 FN partial_functionality

- 方法: `copyResource` vs `DecodeMapFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies an input resource to an output file without modification.
- B 摘要: Decodes a map file by XORing each byte and writes the result to an output file.
- 静态失败原因: GraphCodeBERT likely focused on token-level differences such as the XOR operation, different method names, and lower Jaccard similarity, missing the high-level structural similarity of the stream-copy pattern. The model may not capture long-range semantic equivalence when core behavior is hidden by additional operations.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider these clones because both implement the same core pattern of stream-based file copying with a loop, and the XOR transformation is seen as a minor variation that does not change the overall structure. The similarity in I/O pattern and resource handling aligns with Type-3 or Type-4 clone definitions in BCB.
- 共享行为: Both open an input stream and an output stream；Both loop reading from input and writing to output；Both close streams after operation
- 行为差异: Function A does no data transformation, while Function B applies XOR decryption；Function A reads byte-by-byte, Function B reads in 2048-byte chunks；Function A handles URL sources, Function B only handles files；Function A's exception handling is simpler, Function B catches and rethrows with a custom message
- 修正建议: Improve training data with more diverse Type-4 clones；Incorporate control flow and data flow features to abstract away local transformations；Use a larger context or AST-based matching to identify high-level patterns

### case_id=1467 FN partial_functionality

- 方法: `copyResource` vs `DialogHelper`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource from a URL or file to a destination file using byte-by-byte stream copying.
- B 摘要: Constructs a JDialog to display an image and allows saving the image file via FileChannel copy on button click.
- 静态失败原因: Static BERT models rely on token overlap and syntactic structure; these functions have low token Jaccard (0.1186) and very different lengths and structures, causing the model to miss the underlying semantic similarity in file copying.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB labels as clone because both functions perform file copying from a source to a destination, which is a core shared behavior despite different contexts and implementations, fitting Type-3/Type-4 clone criteria.
- 共享行为: Both copy a file from a source (URL/file) to a destination file；Both handle file existence/error scenarios
- 行为差异: Function A uses InputStream/OutputStream byte-by-byte copying; Function B uses FileChannel.transferTo；Function A is a standalone method; Function B is a constructor with UI and event handling；Function A throws exception on failure; Function B shows dialog warnings；Function A reads from URL or file; Function B reads from URL only
- 修正建议: Incorporate data-flow analysis to capture file I/O operations；Use graph-based models that model control and data dependencies；Train with contrastive learning on BCB labels to learn partial functionality clones

### case_id=1468 FN benchmark_preference_bias

- 方法: `modifyApplicationMessage` vs `createOutputStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Modifies a locale-specific properties file by updating or adding a key-value pair for internationalization.
- B 摘要: Creates a BufferedWriter that writes to a zip output stream, excluding an existing 'content.xml' entry and then adding a new one.
- 静态失败原因: The static model correctly identified the lack of syntactic and structural similarity, but failed to recognize a potential high-level functional similarity that BCB annotators might consider, leading to a false negative relative to the BCB label.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled these as clones due to a broad interpretation of Type-4 semantic similarity, considering both as file processing functions that transform an input file into an output file with similar buffered I/O patterns.
- 共享行为: Both involve file I/O operations with readers and writers.；Both handle text data (properties and XML).；Both use try-catch or throws IOException for exception handling.
- 行为差异: Method A modifies a .properties file for i18n; Method B creates a zip output stream for XML file processing.；Method A reads and writes plain text files; Method B deals with zip entries and compression.；Method A updates a specific key-value pair; Method B copies all zip entries except one, then adds a new entry.；Method A uses BufferedReader with line-by-line parsing; Method B uses ZipInputStream and ZipOutputStream with buffer reading.
- 修正建议: Use a more flexible threshold for semantic similarity that captures abstract data transformation tasks.；Incorporate task-level embeddings or domain knowledge about common file processing patterns.；Consider multi-level granularity: lexical, structural, and semantic.

### case_id=1469 FP lexical_or_api_overlap

- 方法: `executePost` vs `doVersionCheck`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Sends an HTTP POST request with parameters and returns the response body as a string.
- B 摘要: Checks for a newer version of jEdit by fetching a version file from a URL and comparing build numbers, showing UI dialogs.
- 静态失败原因: Static BERT/GraphCodeBERT may over-rely on lexical and API-level overlap (URL, InputStream, BufferedReader, while loop) and similar control flow, failing to capture the distinct purposes and the specific domain logic (POST parameters vs version parsing and UI interaction).
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB considers this a non-clone because the core functionalities are entirely different (HTTP POST vs version check), despite sharing boilerplate I/O code. The semantic intent outweighs structural similarity.
- 共享行为: Both open a URL connection and read lines from an InputStream using BufferedReader；Both use try-catch for exception handling
- 行为差异: A performs POST; B performs GET (implicitly via openStream)；A sends parameters; B does not send data；A returns response string; B shows dialogs and does not return data；A explicitly sets connection properties; B does not
- 修正建议: Encode functional semantics, e.g., distinguish HTTP methods (POST vs GET) and parameters；Identify domain-specific patterns (e.g., version parsing, UI calls) and treat them as different from generic I/O；Use data flow analysis to track how input/output values are produced and consumed

### case_id=1470 FN partial_functionality

- 方法: `main` vs `modifyApplicationMessage`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies source files to target files using FileChannel, then optionally deletes or SVN deletes and SVN adds.
- B 摘要: Modifies a locale-specific properties file by reading, replacing or appending a message key-value pair.
- 静态失败原因: The static model over-relied on token-level overlap (Jaccard=0.21) and method names (main vs. modifyApplicationMessage), failing to capture the abstract functional similarity of file updating that BCB recognized.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considered both functions as 'file update' operations with similar high-level intent (updating data in files) and shared control flow patterns (read-iterate-write with exception handling), classifying them as a Type-4 semantic clone.
- 共享行为: Both perform file update operations；Both use try-catch for exception handling；Both iterate over collections (files for A, lines for B)；Both output status or error messages
- 行为差异: A copies binary files using transferTo, B reads and writes text properties；A involves deletion and SVN operations, B modifies a single property or appends new one；A operates on multiple target files per source, B on a single locale file；A uses FileChannel, B uses FileReader/Writer and BufferedReader
- 修正建议: Train models to recognize high-level task intents (e.g., file update) beyond syntactic similarity；Use program dependency graphs or dataflow to identify core I/O operations；Enhance training data with more Type-4 clone examples

### case_id=1471 FN benchmark_preference_bias

- 方法: `createHTML` vs `register`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.6`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Generates an HTML page by loading a CSS file and appending content based on the page type, with optional database query for dashboard content.
- B 摘要: Registers a user by encoding password, setting authorities, creating a hash, interacting with a phpBB forum via HTTP, and persisting the user entity.
- 静态失败原因: Static BERT/GraphCodeBERT relies heavily on token overlap and local syntax, which is very low (Jaccard=0.0995). It failed to recognize the broad structural pattern that BCB annotators considered clone-worthy, possibly because the model cannot abstract to high-level behavioral patterns.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled these as clones due to structural similarity in the I/O pattern: both open a URL, read lines, and handle exceptions. The overall control flow is similar enough to be considered a Type-3 near-miss clone, despite different purposes.
- 共享行为: Both use URL to open a stream and read line by line with BufferedReader；Both have try-catch blocks for IOException；Both involve string building (result in a, URL string in b)；Both have a similar control flow pattern: setup, read loop, exception handling
- 行为差异: Purpose: HTML generation vs user registration；Input: PAGE_TYPE enum vs Object (User)；Output: String vs boolean；Processing logic: switch on page type vs conditional checks and multiple steps
- 修正建议: Incorporate abstract dataflow or API usage patterns to capture structural clones beyond lexical similarity；Re-evaluate ground truth annotations to ensure consistency；Use global context or program slicing to identify common I/O patterns

### case_id=1472 FP lexical_or_api_overlap

- 方法: `importRoles` vs `SRWGuiClient`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Imports role names by parsing XML from a URL, extracting <RoleName> elements.
- B 摘要: Constructs a Swing GUI browser that reads XML from a URL, optionally applies XSLT transformation, and displays HTML.
- 静态失败原因: Static BERT models may over-rely on lexical/API overlap (URL, BufferedReader, readLine) and miss the starkly different overall semantics and control flow.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels non-clones when the shared functionality is only a common I/O pattern, without significant functional overlap in task-specific logic.
- 共享行为: Both open a URL and read lines using BufferedReader
- 行为差异: A only parses specific XML tags for roles; B performs XSLT transformation and GUI initialization；A returns a list of RoleName; B sets up a browser window with HTML content；A is a static method; B is a constructor with extensive GUI setup
- 修正建议: Use data-flow-aware models that track variable usage beyond API calls；Incorporate structural analysis to differentiate short utility patterns from core logic

### case_id=1473 FP lexical_or_api_overlap

- 方法: `handleHandshake` vs `doVersionCheck`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Validates server handshake by checking username and making HTTP request to Minecraft session server.
- B 摘要: Checks application version by reading version info from a URL and updating view.
- 静态失败原因: Static BERT/GraphCodeBERT may have over-weighted lexical and API overlap (URL, BufferedReader, InputStream) and ignored the functional context and domain differences.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the functions serve entirely different purposes despite shared API usage; the behavioral similarity is only superficial boilerplate.
- 共享行为: Both open a URL and read from it using BufferedReader.；Both handle IOExceptions.
- 行为差异: Different input types and contexts: one is a network game handshake, the other is a GUI version check.；Different URL construction and parsing logic.；Different error handling: one shuts down network connection, the other shows error dialog.；Different outcome: one sends login packet, the other calls another method to display version info.
- 修正建议: Improve model to consider method-level semantics and domain context.；Use dataflow analysis to differentiate URL construction and conditional logic.；Incorporate type information to distinguish different input/output patterns.

### case_id=1474 FN partial_functionality

- 方法: `read` vs `register`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads content from a file or URL into a buffer and returns a status code.
- B 摘要: Registers a user by encoding password, persisting to database, connecting to a forum URL to register the user, and sending a confirmation email, returning a boolean success.
- 静态失败原因: Low token overlap (0.094) and dissimilar method names and overall structure lead the static model to miss the abstract similarity of URL reading.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considers the shared partial functionality of opening a URL and reading input as sufficient for Type-4 clone, given both involve I/O and error handling.
- 共享行为: Both open a URL connection and read from its input stream.；Both handle IO exceptions with error logging or status setting.
- 行为差异: A reads data from file or URL, B only from URL.；A returns an int status, B returns a boolean.；B performs multiple additional steps (password encoding, database persistence, email sending) beyond reading.；A has no user interaction or data transformation; B modifies user object and persists.
- 修正建议: Enhance model to recognize subtask similarity, e.g., via abstract I/O pattern representation.；Use data-flow analysis to identify common suboperations like URL connection and stream reading.；Incorporate larger context or call graphs to see if one function delegates to another.

### case_id=1475 FN partial_functionality

- 方法: `runScript` vs `readURL`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.75`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a script from a URL character by character and returns its content as a string, returning 'error!' on failure.
- B 摘要: Reads a URL line by line and prints each line to stdout, closing streams in finally block, with stack trace on failure.
- 静态失败原因: Static BERT models rely on token and surface-level features; low Jaccard similarity and differing method signatures (return type, name) likely caused the false negative. The model missed the high-level semantic overlap of URL reading.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely labels this as clone because both functions fundamentally perform 'reading from a URL' and share structural patterns (try-catch, InputStream). The differences in output and resource handling are considered secondary, fitting a broad Type-3/Type-4 clone definition.
- 共享行为: Both open a URL stream and read content from it.；Both use try-catch to handle exceptions.
- 行为差异: A returns a string; B is void and prints lines.；A reads char by char; B reads line by line.；A has no resource cleanup; B properly closes streams in finally.；A returns 'error!' on exception; B prints stack trace.
- 修正建议: Incorporate control-flow and data-flow analysis to identify common I/O operations.；Use graph-based representations that capture overall intent (e.g., URL content retrieval) rather than exact output.；Add more training examples of diverse URL-reading functions to improve semantic understanding.

### case_id=1476 FN partial_functionality

- 方法: `main` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies source files to multiple targets, deletes sources, and optionally handles SVN operations.
- B 摘要: Launches a NexOpen project configuration, processes pom.xml files, sets up Hibernate properties, and copies a resource file to the project if needed.
- 静态失败原因: Low token overlap (Jaccard=0.0785) and different API vocabulary (FileChannel vs Eclipse-specific classes) cause static models to miss the underlying file-copying behavior embedded in distinct contexts.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider the core file-copying functionality as sufficient semantic similarity for a Type-4 clone, ignoring the domain-specific differences.
- 共享行为: Both include file copying logic: A copies source to targets via FileChannel.transferTo; B copies a bundle resource to a project file using IOUtils.copy and stream manipulation.；Both use try-finally blocks for resource cleanup.；Both print/log status messages.
- 行为差异: A is a standalone command-line utility; B is an Eclipse RCP launch handler.；A handles file deletion and SVN integration; B handles XML configuration and persistent properties.；A iterates over multiple source and target files; B operates on fixed pom.xml files and a specific reverse engineering file.
- 修正建议: Inject dataflow-aware embeddings to capture file operations across different abstractions.；Incorporate API mapping or domain adaptation training for Eclipse vs. standard Java APIs.

### case_id=1477 FN boilerplate_overlap

- 方法: `loadExistingAntlibs` vs `invoke`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Loads antlib resources from classpath by reading lines from resource files and resolving URIs.
- B 摘要: Invokes a remote method via HTTP POST, reads JSON response, and retries on connection timeout.
- 静态失败原因: Static BERT / GraphCodeBERT likely focused on low lexical overlap (Jaccard = 0.157) and distinct semantic embeddings (one loads antlib, one invokes remote method), correctly predicting non-clone, but failing to match BCB's broad annotation that considered boilerplate I/O as sufficient similarity.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may have labeled as clone due to shared I/O boilerplate pattern (BufferedReader, readLine, close), considering both as 'resource reading' tasks, though functionality differs greatly.
- 共享行为: Both use BufferedReader to read lines from an InputStream；Both close reader and stream after reading；Both handle IOException in try-catch blocks
- 行为差异: A loads Ant library definitions from classpath resources; B performs HTTP RPC calls；A iterates over multiple resources; B reads a single HTTP response；A resolves URIs and loads antlib; B deserializes JSON and returns typed object；B has retry logic on timeout; A has no retry
- 修正建议: Augment training with functional similarity goals beyond lexical/embedding overlap；Use dataflow or API sequence differences to filter out boilerplate-only clones；Incorporate benchmark preference analysis to handle annotation bias

### case_id=1478 FP boilerplate_overlap

- 方法: `readData` vs `copyFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Parses comma-separated string constants to populate multiple sets and a mapping for valid input sequences, and reads a file to build lookup tables for Tibetan transliteration.
- B 摘要: Copies a file from source to destination using NIO FileChannel.
- 静态失败原因: The static BERT/GraphCodeBERT model likely mispredicted due to lexical or API overlap (e.g., both use 'throw' and 'catch', or both involve stream-like operations), but the token Jaccard is very low, suggesting potential overfitting or attention to irrelevant tokens.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels these as non-clones because there is no functional similarity; one is data loading/initialization, the other is file I/O utility.
- 共享行为: None
- 行为差异: readData initializes data structures from string constants and file I/O; copyFile transfers bytes between files.；readData involves parsing and mapping logic; copyFile is a straightforward file copy.；readData uses StringTokenizer and HashMap; copyFile uses FileChannel and streams.；readData has complex error handling with throw statements; copyFile throws Exception.
- 修正建议: Incorporate dataflow analysis to distinguish I/O operations from data structure initialization.；Improve representation learning to capture long-range semantic differences.；Enhance training data with more such non-clone pairs to reduce false positives.

### case_id=1479 FN partial_functionality

- 方法: `addIDs` vs `scrapeForIsbns`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Opens a URL based on a compound name, reads HTML lines, extracts metabolite identifiers and properties, and stores them in a PeakListRow object, returning a score.
- B 摘要: Opens a given URL, reads lines, extracts ISBN-10 codes using regex, counts matches and stores them in a collection, returning the count.
- 静态失败原因: Static BERT/GraphCodeBERT may have failed because the functions have low token Jaccard (0.1338) and share little lexical overlap; the abstract pattern of web scraping is not captured by token-level similarity. Models likely rely on surface-level features and miss the structural similarity in control flow.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this as a clone because both functions are web scrapers that read HTML lines, apply pattern matching to extract identifiers, and accumulate results in data structures, representing a common high-level template for data extraction from web pages.
- 共享行为: Both functions open a URL and read its content line by line.；Both use pattern matching (string contains or regex) to extract specific identifiers from each line.；Both have error handling for IOExceptions.；Both return an integer count (score/matches).
- 行为差异: Function A extracts multiple types of chemical identifiers (metabolite, PubChem, ChEBI, etc.) and sets them on a row object; Function B extracts only ISBN-10 codes and stores them in a set.；Function A constructs its URL from a parameter; Function B takes the URL directly.；Function A does not have retry logic; Function B retries on connection failures.；Function A's parsing is more complex, handling multiple HTML patterns; B uses a single regex.
- 修正建议: Use code structure embeddings that capture control flow and data flow patterns.；Incorporate program dependence graphs or AST-based features to detect similar structures.；Use models with attention to long-range dependencies to capture the reading-loop pattern.

### case_id=1480 FP lexical_or_api_overlap

- 方法: `copy` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Recursively copies a file or directory from source to destination using FileChannels.
- B 摘要: Handles action events to configure application settings like file paths and display options.
- 静态失败原因: Static BERT/GraphCodeBERT likely relied on lexical and API overlaps (File, null checks, file paths) and structural patterns (if-else, loops) but missed the entirely different semantics and contexts.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labeled non-clone because the functions have no meaningful functional overlap despite shared API usage.
- 共享行为: Both use java.io.File for file path operations；Both perform null checks on file objects
- 行为差异: Function A is a file copy utility; Function B is a UI event handler；A uses FileChannel for efficient transfer; B uses JFileChooser for user selection；A recurses through directories; B processes multiple unrelated commands；A has simpler control flow; B has complex branching and UI updates
- 修正建议: Incorporate method-level semantics via abstract syntax trees or control flow graphs；Use method names and surrounding class context as features；Train with hard negative mining that emphasizes semantic dissimilarity despite API overlap

### case_id=1481 FP lexical_or_api_overlap

- 方法: `populateResources` vs `getVersion`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Populate resources by loading templates from a locale-specific directory and saving them, then loading a set of images and saving them with properties.
- B 摘要: Fetch a version string from a remote URL and return it.
- 静态失败原因: Static BERT models may over-rely on token-level similarity and structural patterns (try-catch with URL/BufferedReader) without understanding semantic intent. The high overlap in API usage (URL, BufferedReader, InputStreamReader) and exception handling tricks the model into thinking they are similar, but they perform entirely different tasks.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the two functions have completely different purposes (populating resources vs. fetching a version) and no overlap in core functionality, even though they share some boilerplate I/O patterns.
- 共享行为: Both use URL objects to read from external sources；Both use BufferedReader and InputStreamReader to read line by line；Both handle exceptions with catch blocks
- 行为差异: Function A modifies database (saves resources and images), while B returns a string；A loads multiple files (templates and images) from classpath, B fetches a single remote URL；A deals with XML/text files and image files, B deals with a plain text version string；A throws exception, B returns null on error
- 修正建议: Improve training to focus on task-level semantics beyond API usage；Incorporate data-flow analysis to track how variables are used；Add negative examples with similar I/O patterns but different goals

### case_id=1482 FP lexical_or_api_overlap

- 方法: `save` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Saves multiple files to a package directory with added package declaration.
- B 摘要: Handles UI action commands for setting preferences like graphviz and imagemagick paths.
- 静态失败原因: Likely due to lexical overlap of common Java API terms like File, FileOutputStream, etc., and the presence of exception handling, causing the model to overestimate similarity.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB annotation would not consider these clones due to completely different intents and operations despite some superficial file-related terms.
- 行为差异: Function A writes byte arrays to files and then copies with package line; function B uses file chooser dialogs and sets preferences.；Function A operates on a list of file contents/names; function B responds to specific command strings.；No common functionality or semantics.
- 修正建议: Incorporate data flow and control flow analysis to distinguish writing files from UI event handling.；Use AST-based or semantic role features to capture the purpose of the function.

### case_id=1483 FN benchmark_preference_bias

- 方法: `main` vs `CopyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a URL and extracts its contents to the current directory using ZipInputStream.
- B 摘要: Copies a source file to a destination file, creating parent directories if necessary, using FileChannel.
- 静态失败原因: The functions have low lexical overlap (token Jaccard 0.117), different method names and structures, and only superficial similarity in using FileInputStream/FileOutputStream, which a static BERT model interprets as distinct semantics.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider both as file manipulation utilities that copy data from an input source to an output file, overlooking the distinct operations (download+unzip vs simple copy).
- 共享行为: Both perform file I/O operations using streams/channels；Both handle exceptions via throws clause
- 行为差异: A downloads from a remote URL and handles ZIP extraction; B copies a local file without ZIP handling；A does not create directories; B creates parent directories of the destination；A prints extraction progress; B returns the destination file path
- 修正建议: Include data-flow analysis to trace byte-level transfer operations；Use program slicing to isolate core copying behavior；Incorporate functional categorization beyond token-level similarity

### case_id=1484 FP lexical_or_api_overlap

- 方法: `getVersion` vs `doVersionCheck`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.85`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches a version string from a hardcoded URL and returns it.
- B 摘要: Checks for a new version by parsing a remote file for version and build info, then displays appropriate UI messages.
- 静态失败原因: Static BERT/GraphCodeBERT likely overemphasized lexical and API overlap (URL, BufferedReader, readLine, while loop, try-catch) while ignoring the semantic differences in return types, control flow, and overall purpose.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the methods have different signatures, different purposes (getter vs. UI method), different parsing logic, and different exception handling, despite sharing low-level API usage.
- 共享行为: Both open an HTTP connection to a URL；Both read lines using BufferedReader；Both close the reader
- 行为差异: A returns a version string; B performs UI actions and returns void；A uses a hardcoded URL; B uses a configurable property；A treats the entire line as version; B parses specific prefixes (.version, .build)；B compares build numbers and shows dialogs; A does not
- 修正建议: Incorporate data-flow analysis to detect different return types and side effects；Use contrastive learning to distinguish methods with similar API usage but different goals

### case_id=1485 FP lexical_or_api_overlap

- 方法: `actionPerformed` vs `createButtonCopyToClipboard`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Handles multiple UI actions (graphviz, imagemagick, scaling, etc.) and saves preferences.
- B 摘要: Creates a button and sets up a listener to copy environment report to clipboard.
- 静态失败原因: Static BERT may have overfitted to common UI-related tokens like 'setText', 'chooser', 'button', or 'owner' and 'shell', but in different contexts. The long truncated code may also confuse the model.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB annotation typically labels non-clones (non-functional) correctly; these two functions have no overlap in functionality.
- 行为差异: Function A is a large event handler for UI preferences; Function B is a small UI creation method.；Function A uses Swing (JFileChooser, etc.) while B uses SWT.；Function A has multiple conditions and preference saving; B has a single widgetSelected listener.
- 修正建议: Improve training with better negative sampling to avoid false positives on low similarity pairs.；Use dataflow or structural analysis to capture deeper semantic differences.

### case_id=1486 FP boilerplate_overlap

- 方法: `readTwitterFead` vs `setMembers`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Downloads Twitter timeline JSON from a fixed URL and returns it as a String.
- B 摘要: Parses an HTML page from a Trac URL to extract component and priority names into static arrays.
- 静态失败原因: The model likely overemphasized common I/O boilerplate (BufferedReader, try-catch) and ignored the distinct domain-specific operations and different intents.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically requires functional similarity; these functions have different purposes, inputs, and outputs, so they would not be considered clones despite structural overlap.
- 共享行为: Both perform HTTP GET requests and read line-by-line using BufferedReader.；Both handle I/O exceptions with try-catch blocks.
- 行为差异: A fetches JSON from Twitter API; B fetches HTML from Trac.；A simply appends lines to a StringBuilder; B uses regex to parse HTML select options.；A returns a String; B modifies static fields (m_strComponents, m_strPriorities).；A logs on non-200 status; B does not check HTTP status.
- 修正建议: Incorporate dataflow analysis to differentiate data transformation paths.；Add attention to method names and return types.；Use task-specific features like API calls and string literals.

### case_id=1487 FN boilerplate_overlap

- 方法: `main` vs `doVersionCheck`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.4`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends a POST request to the RenRen API with several parameters and prints the response.
- B 摘要: Checks for a new version of jEdit by reading a version file from a URL and displays a message or new version dialog.
- 静态失败原因: The static model likely focused on low token overlap and different method names/purposes, missing the structural and behavioral similarity in the URL reading and line processing pattern.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may have labeled these as clones due to the shared boilerplate pattern of opening a URL, reading lines, and processing output, despite different intents. The structural similarity in the while-loop reading from BufferedReader is a common Type-3 near-miss clone pattern.
- 共享行为: Both open a URL connection；Both read lines from a BufferedReader over an InputStream；Both use a while loop to process each line；Both output information (console or GUI)
- 行为差异: A sends a POST request with parameters; B only performs a GET request；A prints the HTTP response code and message; B parses version/build strings and conditionally shows dialogs；A lacks error handling; B has try-catch for IOException and shows error message；A sets HttpURLConnection properties (DoOutput, request method); B uses URL.openStream() directly
- 修正建议: Incorporate structural clone detection (e.g., AST or graph matching) to capture shared I/O patterns；Enhance model with functional similarity across different method names and contexts；Consider training with more diverse examples of partial functionality clones

### case_id=1488 FN partial_functionality

- 方法: `doGet` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.5`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Handles HTTP GET requests to retrieve a page by ID or name, checks user permissions, logs requests, and caches page output to a temporary file.
- B 摘要: Copies a file from source to destination using FileChannels and returns success status.
- 静态失败原因: Static BERT models rely on token overlap and syntactic similarity; token Jaccard is very low (0.058). The model correctly identified them as non-clones based on surface features, but BCB labeled as clone, suggesting the model ignored the semantic file I/O overlap.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB might consider both functions as involving file writing/copying, thus classifying them as Type-4 (partial functionality) clones. However, the contexts are very different, and the file operation in A is a small part of a much larger task.
- 共享行为: Both involve file I/O operations: function A writes to a temporary file; function B copies a file.
- 行为差异: Function A is a complex servlet handler with HTTP request processing, page retrieval, user authentication, logging, and conditional caching; function B is a simple utility that copies a file.；Function A writes HTML content to a file; function B copies an existing file.；Function A has multiple exception handlers and branching logic; function B has a single try-catch.；Function A depends on many external classes (HttpServletRequest, Response, Page, Property, etc.); function B only uses java.io.
- 修正建议: If BCB intends to capture partial functionality clones, the model should be trained to recognize shared low-level operations like I/O across different high-level tasks.；Alternatively, evaluate the model on more strict definitions.

### case_id=1489 FN partial_functionality

- 方法: `PageLoader` vs `register`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Constructs PageLoader by fetching and concatenating all lines from a URL.
- B 摘要: Registers a User object, including password encoding, setting metadata, and making a URL call to create a phpBB forum user, then persisting and sending confirmation email.
- 静态失败原因: Low token Jaccard (0.1) and long, structurally different functions cause static models to miss the partial behavioral overlap.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider the overlapping URL reading pattern as a Type-4 semantic clone, despite the vast difference in overall functionality.
- 共享行为: Both open a URL and read data using BufferedReader.
- 行为差异: Function A is a constructor that simply reads and stores page content.；Function B performs complex user registration with multiple steps beyond URL reading.；Function B handles exceptions, logs, and interacts with a database and email service.
- 修正建议: Use graph-based models to capture subgraph similarities like URL opening.；Incorporate semantic role labeling for common I/O operations.；Consider fine-tuning on BCB's annotation bias for partial functionality clones.

### case_id=1490 FN benchmark_preference_bias

- 方法: `simulate` vs `modifyApplicationMessage`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.85`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Simulates a reputation system by reading requests from a file, calling remote services, and validating responses with assertions.
- B 摘要: Modifies a localized properties file by reading key-value pairs and updating or appending a specific message.
- 静态失败原因: Static BERT model likely predicted non-clone correctly due to low token overlap (Jaccard 0.15) and distinct API usage, so it did not fail; the discrepancy arises from a possibly incorrect BCB annotation.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled these as clones due to superficial structural similarity (both have a file-reading loop with line-by-line processing) despite completely different semantics and domains, indicating a possible annotation error or overly broad Type-3/Type-4 interpretation.
- 共享行为: Both perform file I/O using BufferedReader and read lines in a loop.；Both handle exceptions with try-catch.
- 行为差异: Function A involves remote service calls and assertions; Function B only modifies a properties file.；Function A writes a header to an output file and uses multiple file streams; Function B creates a copy of a file if missing.；Function A's loop processes each line by calling a service; Function B's loop parses and replaces a specific key-value pair.
- 修正建议: Re-evaluate the clone label for this pair; consider removing from clone set if they are not semantically or functionally related.；Improve annotation guidelines to avoid labeling based on generic boilerplate patterns like file input/output loops.

### case_id=1491 FN boilerplate_overlap

- 方法: `login` vs `doVersionCheck`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Logs into a LOLA service by sending email and password via HTTP POST and returns a session ID.
- B 摘要: Checks for software version updates by fetching a URL and parsing build numbers, then delegating to another method.
- 静态失败原因: Static BERT models rely heavily on lexical and surface-level token overlap, which is low (Jaccard 0.16). They miss the high-level structural and functional similarity in the network I/O steps due to poor generalization to different contexts and method names.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may consider these clones as both are network I/O tasks that read from a URL, which qualifies as partial functional similarity (Type-4). The common pattern of opening a connection and processing lines is deemed sufficient for clone annotation.
- 共享行为: Opens a URL and reads lines from it using BufferedReader；Performs network I/O and handles exceptions
- 行为差异: A sends data via POST; B only reads GET-like；A returns a session ID; B returns void and calls another method；A uses URLConnection; B uses URL.openStream()；Error handling differs: A prints and returns empty string; B shows error dialog via GUIUtilities
- 修正建议: Incorporate structure-aware encoding (e.g., AST or dataflow) to capture common I/O patterns；Use contrastive learning with positive pairs of such boilerplate clones；Enhance model with functional similarity heuristics beyond token overlap

### case_id=1492 FN partial_functionality

- 方法: `getHTML` vs `invoke`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches HTML from a URL using HTTP GET and optionally writes to a file.
- B 摘要: Invokes a remote method via HTTP POST with JSON, deserializes response, and retries on timeout.
- 静态失败原因: Low token overlap and different method names and overall logic; BERT missed the shared HTTP reading pattern due to lack of dataflow or API sequence awareness.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider the common pattern of HTTP request and line-by-line response reading as sufficient structural similarity for a Type-3 clone.
- 共享行为: Makes HTTP request；Reads response line by line into StringBuilder
- 行为差异: HTTP method (GET vs POST)；JSON handling and retry logic in B；Optional file writing in A
- 修正建议: Incorporate control-flow and dataflow analysis to detect common API usage patterns；Use AST-based matching for structural clones

### case_id=1493 FN benchmark_preference_bias

- 方法: `copyJar` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Copies a file from source to destination using FileChannel.
- B 摘要: Launches a NexOpen project configuration by checking project files, handling pom.xml, setting properties, and scheduling a build job.
- 静态失败原因: Static BERT correctly predicted non-clone due to low token overlap and no meaningful functional equivalence. The BCB label is inconsistent, so the model's prediction is actually correct, and the failure is in the benchmark label.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: The BCB label is likely an annotation error, as the two functions have minimal semantic similarity beyond basic file operations; the label may arise from a broad interpretation of 'file-related' activities but does not align with typical BCB clone criteria.
- 共享行为: Both perform file I/O operations (reading and writing files)；Both use exception handling with try-catch-finally
- 行为差异: copyJar is a simple utility for copying a single file; launch is a complex method with multiple conditional checks and sub-tasks；copyJar uses FileChannel transferFrom; launch uses streams, document handling, and resource management；launch involves Eclipse API, progress monitors, and persistence properties; copyJar has no such dependencies
- 修正建议: Re-evaluate the BCB annotation for this pair; consider relabeling as non-clone.

### case_id=1494 FN partial_functionality

- 方法: `File2String` vs `retrieveTemplate`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a local file or classpath resource line by line and returns its content as a string, terminating the program on failure.
- B 摘要: Reads a URL line by line, caches the result, and returns the content as a string, throwing an exception on failure.
- 静态失败原因: The model likely focused on low token overlap (0.2969), different method names, and the presence of System.exit and print statements in A but not B, missing the conceptual similarity of the read-append loop.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels pairs that perform the same high-level operation (reading a text resource into a string) as clones, even if the source or error handling differs, considering them Type-4 functional clones.
- 共享行为: Both open a text resource and read it line by line into a buffer；Both return the concatenated string content
- 行为差异: File2String reads from a local file or classpath; retrieveTemplate reads from a URL；File2String prints messages and calls System.exit on errors; retrieveTemplate throws Exception；File2String does not cache; retrieveTemplate caches the result in a field；File2String uses StringBuffer; retrieveTemplate uses StringBuilder
- 修正建议: Use dataflow analysis to identify the core loop pattern (read line, append to string builder/buffer) as a structural clone signature；Normalize API calls for reading (e.g., FileInputStream vs URL.openStream) to a generic 'open stream' concept；Abstract away error handling (System.exit vs throw) and caching to focus on the main functionality

### case_id=1495 FN benchmark_preference_bias

- 方法: `addIDs` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.85`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Adds metabolite IDs and molecular weights to a peak list row by querying a remote GMD database via HTTP.
- B 摘要: Sends a test HTTP POST request to the RenRen API with predefined parameters and prints the response.
- 静态失败原因: The low token Jaccard (0.08) indicates little lexical overlap, but the model might have been biased by the presence of common API elements (e.g., 'URL', 'BufferedReader', 'readLine'). However, the model correctly predicted non-clone (0), so it did not fail; instead, the BCB label appears to be a false positive. If the model failed to detect the clone (as per BCB), it's because the semantic gap is too wide and the token-level similarity is too low for models like static BERT to consider them clones.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as a clone due to the superficial similarity of both functions opening a URL and reading lines with BufferedReader, despite completely different domains and purposes. The annotation might have been based on the shared pattern of HTTP client code, which is a common 'Type-3' (near-miss) clone in some benchmarks.
- 共享行为: Both use HTTP connections (URL, HttpURLConnection/BufferedReader).；Both read from an input stream line by line.；Both have error handling (try-catch or throws IOException).
- 行为差异: Function A is a private method manipulating a PeakListRow object; Function B is a public static main method with no return value.；Function A parses HTML/XML to extract metabolite IDs; Function B sends a fixed API request and prints the response.；Function A returns an integer score; Function B returns void.；Function A uses multiple conditional branches for different tag types; Function B has a linear sequence of parameter additions.
- 修正建议: Re-examine BCB annotation for this pair; likely a mislabel due to over-generalizing HTTP usage as a clone pattern.；Use more fine-grained clone types (e.g., Type-1/2 vs Type-4) to avoid grouping unrelated functionalities.；Train models to recognize that HTTP boilerplate alone does not imply semantic equivalence.

### case_id=1496 FP lexical_or_api_overlap

- 方法: `doVersionCheck` vs `readScalarpvviewerDocument`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Checks version info from a URL by parsing specific lines.
- B 摘要: Reads a scalarpvviewer document from a URL, parses XML, and configures UI components.
- 静态失败原因: The model may have been misled by the lexical overlap of common patterns like opening a URL, using BufferedReader, and handling IOException, ignoring the vastly different semantic content.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as not a clone because the functions have completely different purposes and outputs, despite sharing a common I/O pattern.
- 共享行为: Both open a URL and read lines using BufferedReader and InputStreamReader.；Both handle IOException with error messages.
- 行为差异: Function A parses only lines starting with '.build' or '.stablebuild' to get version strings.；Function B parses XML data, extracts many parameters, and sets up GUI elements like fonts, panels, and charts.；Function A calls another method 'doVersionCheck(view, stableBuild, develBuild)' after parsing, while B updates UI and loads data structures.；Function A is static and takes a View parameter, B is an instance method and takes a URL.
- 修正建议: Incorporate structural or data-flow analysis to distinguish different processing logic.；Use more comprehensive training examples where similar I/O patterns lead to different high-level behaviors.

### case_id=1497 FN partial_functionality

- 方法: `unzipEntry` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.2`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Unzips a single entry from a zip file to a file, creating directories as needed.
- B 摘要: Builds a set of HTML pages from XML templates and properties, involving file reading, XSL transformation, and string replacement.
- 静态失败原因: The static model likely focused on low token overlap and very different method signatures, missing the broad functional similarity of file I/O operations that BCB considered.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled these as clones due to both involving file I/O and stream copying at a high level, considering them type-4 clones (functional similarity) where both output files from input data. However, the specific operations are very different.
- 共享行为: Both perform file I/O operations (reading and writing files).；Both use input streams and output streams.
- 行为差异: Purpose: one is unzipping, the other is building a website.；Complexity: unzipEntry is simple and focused; buildSiteForEdit is complex with many steps.；Parameters: unzipEntry takes three parameters; buildSiteForEdit takes many.；Error handling: different exception types.
- 修正建议: Incorporate domain knowledge about file I/O patterns.；Use a more abstract representation of operations (e.g., flow of data from input to output).；Train on a broader set of clone types including type-4 functional clones.

### case_id=1498 FN partial_functionality

- 方法: `copyResource` vs `decodeFileToFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource (URL or file) to a destination file byte by byte.
- B 摘要: Decodes a Base64-encoded file to an output file using buffered I/O.
- 静态失败原因: Static BERT/GraphCodeBERT relies on lexical and structural patterns; low token Jaccard (0.19), different method names, and distinct I/O details (byte-by-byte vs. buffered, exception handling) cause it to miss the underlying semantic similarity of input-to-output data transfer.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as file copying functions with similar overall structure (open streams, loop, close), regarding the transformation (decode vs. raw copy) as a minor functional variation within Type-4 semantic clones.
- 共享行为: Both read from an input source and write to an output file；Both close streams after operation
- 行为差异: Code A copies raw bytes; Code B performs Base64 decoding during copy；Code A reads single bytes; Code B reads buffered chunks；Code A throws exception on failure; Code B returns boolean and prints stack trace；Code A gets source via getResource; Code B takes explicit file paths
- 修正建议: Incorporate data flow analysis to abstract I/O operations；Enrich training with examples of semantically similar but lexically different copy/transform functions；Use bytecode or IR-level features to capture input-output dependency patterns

### case_id=1499 FP partial_functionality

- 方法: `callService` vs `getRequestContent`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads all lines from a URL and stores the result in a field, with error handling returning error messages.
- B 摘要: Reads only the first line from a URL and returns it as a string, throwing exceptions upward.
- 静态失败原因: The models may have focused on the similar API usage (URL, BufferedReader, InputStreamReader) and overlooked the differences in loop structure and error handling. Token-level overlap is low (0.18), but the pattern of opening a URL and reading is common, leading to false positive.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely labels these as non-clones because they differ significantly in behavior: one reads all lines, the other only the first line; error handling strategy is completely different; and they have different return types and signatures.
- 共享行为: Both create a URL object and open a connection to read content.；Both use BufferedReader to read from an InputStream.；Both close the reader after reading.
- 行为差异: function_a reads all lines into a StringBuffer, function_b reads only the first line.；function_a stores the result in a field (answer), function_b returns the result.；function_a catches exceptions and sets answer to error messages, function_b throws exceptions.；function_b uses HttpURLConnection and disconnects it, function_a uses URL.openStream() without explicit disconnect.
- 修正建议: Improve sensitivity to control flow differences, such as loop vs no-loop.；Better distinguish error handling patterns (try-catch vs throws).；Incorporate return type and field usage information into similarity computation.

### case_id=1500 FP partial_functionality

- 方法: `readUNI` vs `fetchUrl`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a tab-separated file from a URL, skips header, and populates a vector with concatenated id and description.
- B 摘要: Fetches entire content from a URL as a single concatenated string.
- 静态失败原因: Static BERT/CodeBERT likely over-relied on token overlap and structural similarity from common I/O boilerplate (URL, openStream, exception handling), while missing the semantic difference in data processing (parsing vs. concatenation).
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB typically requires similar core functionality; here one is for parsing structured data, the other for generic content retrieval, so they are not considered clones.
- 共享行为: Open URL stream；Read lines from stream；Handle MalformedURLException and IOException
- 行为差异: A parses tab-separated fields; B returns raw text；A outputs to a vector; B returns a string；A skips first line; B does not；A uses Scanner with delimiters; B uses BufferedReader
- 修正建议: Incorporate data flow analysis to capture how input is transformed.；Enhance attention to string manipulation and output structure differences.；Use code summarization to contrast high-level intent.
