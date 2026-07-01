# Error Case Studies 2001-2500

- Source model: `configured-llm`
- Cases: `2001` to `2500`

### case_id=2001 FN partial_functionality

- 方法: `addIDs` vs `sendRequestObjectResponse`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Queries a Golm database by building a URL from a name, parses HTML to extract metabolite data and stores it in a PeakListRow, returning an integer score.
- B 摘要: Sends an XML request to a servlet via HTTP with GZIP compression, reads the response, saves it to a file, and returns the absolute file path.
- 静态失败原因: Static BERT models may focus on overlapping tokens like 'URL', 'openStream', 'InputStream' and common error handling patterns, missing the high-level semantic difference in purpose.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled this as clone due to both functions involving HTTP communication and stream handling, but the high-level semantic goals are very different; this is likely a false positive in BCB.
- 共享行为: Both open HTTP connections；Both handle input/output streams；Both have try-catch error handling
- 行为差异: A parses HTML to extract specific data and sets properties on a custom object; B sends data via output stream and reads file content；A returns an integer score; B returns a file path string；A uses a fixed URL pattern; B uses configurable server URL and port
- 修正建议: Incorporate data flow analysis to track the transformation of data through the functions；Use domain-specific knowledge or function naming to disambiguate intent

### case_id=2002 FN benchmark_preference_bias

- 方法: `truncate` vs `modifyApplicationMessage`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Compresses a log file into a zip archive if the file is older than the JVM start time, then deletes the original.
- B 摘要: Reads a locale-specific properties file, modifies or adds a message property, and writes it back.
- 静态失败原因: The model correctly predicted non-clone (FN from BCB perspective) because it likely recognized the distinct semantic purposes despite shared boilerplate.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled them as clones due to superficial similarity in file manipulation, stream handling, and exception management, which are common boilerplate patterns.
- 共享行为: Both perform file I/O operations；Both handle exceptions with try-catch
- 行为差异: A compresses and deletes files; B edits properties files；A uses ZipOutputStream; B uses Properties and FileWriter；A checks file age; B checks file existence and copies from English file if missing
- 修正建议: Re-evaluate BCB annotation to ensure clone labels reflect genuine semantic similarity；Use more fine-grained clone type definitions that distinguish boilerplate from true functionality

### case_id=2003 FP lexical_or_api_overlap

- 方法: `main` vs `encodeFileToFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Main method that reads a Prolog file, parses it, generates adapter classes, and writes them to a JAR file.
- B 摘要: Encodes a source file to a destination file using Base64 encoding.
- 静态失败原因: Static BERT/GraphCodeBERT models may have been misled by lexical and API overlap (e.g., File, InputStream, OutputStream, IOException, try-catch-finally), and the models often rely on surface-level similarity rather than deep semantics.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled non-clone because the functions have completely different purposes and logic, despite sharing some I/O boilerplate.
- 共享行为: Both perform file-to-file I/O operations with exception handling.
- 行为差异: A handles multiple arguments and options; B takes exactly two filenames.；A parses Prolog and generates Java bytecode; B performs Base64 encoding.；A writes to a JAR file with additional resources; B writes to a simple output file.
- 修正建议: Enhance training with data flow and control flow graphs to distinguish different program structures.；Incorporate task-specific context or intent recognition.；Use contrastive learning to push apart semantically different functions with similar API usage.

### case_id=2004 FN boilerplate_overlap

- 方法: `doVersionCheck` vs `invoke`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Checks jEdit version by fetching a URL and parsing version/build lines.
- B 摘要: Invokes a remote method via HTTP POST, deserializing JSON response, with retry on timeout.
- 静态失败原因: Static BERT/CodeBERT models rely on token sequences and may not capture the overall semantic difference. The code shares common boilerplate (try-catch, BufferedReader, while loop) which can lead to false negatives when the core logic differs.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may have considered them clones due to the shared pattern of network I/O: opening a URL, reading lines, and handling exceptions. The structural similarity in the loop reading lines could be seen as Type-3 clone at a coarse level.
- 共享行为: Both open an InputStream to a URL and read lines using BufferedReader.
- 行为差异: doVersionCheck uses HTTP GET and parses specific key-value pairs; invoke uses HTTP POST and parses JSON.；doVersionCheck is a void method that shows UI messages; invoke returns an Object and handles retries.；Different error handling: doVersionCheck catches IOException; invoke catches ConnectTimeoutException and retries.
- 修正建议: Incorporate data flow analysis to distinguish between distinct operations on the read data.；Use method name and signature as additional signals.；Train with contrastive learning to separate boilerplate from core functionality.

### case_id=2005 FP boilerplate_overlap

- 方法: `readZoneIDs` vs `loadMFileViaWeb`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads integer zone IDs from a resource file by parsing each line as an integer.
- B 摘要: Loads a MATLAB function file from a web URL, concatenates lines, and parses into a UserFunction object.
- 静态失败原因: Static BERT may have overemphasized the token-level overlap (e.g., 'URL', 'openStream', 'InputStreamReader', 'readLine') and missed the semantic difference in data handling and return type.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the functions have entirely different purposes and output types, despite sharing boilerplate IO code.
- 共享行为: Both open a URL stream and read lines using BufferedReader/LineNumberReader.
- 行为差异: A extracts integer IDs; B concatenates lines into code and parses it as a MATLAB function.；A returns HashSet<Integer>; B returns UserFunction.；A uses resource URL; B constructs URL from parameters.；B includes logging and error handling specific to MFile loading.
- 修正建议: Incorporate type information and data flow analysis to distinguish different output types.；Add attention to function signatures and return types.；Use contrastive learning with negative examples that share boilerplate but differ in semantics.

### case_id=2006 FP lexical_or_api_overlap

- 方法: `SRWGuiClient` vs `doVersionCheck`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Constructs a Swing browser GUI that loads and displays an XML/XSLT-processed document from a given URL.
- B 摘要: Reads a version check file from a URL to extract development and stable build numbers for jEdit.
- 静态失败原因: The static BERT model likely overfitted to the shared lexical tokens (URL, BufferedReader, readLine, IOException) and caught the structural overlap in the try-catch block, ignoring the divergent overall functionality.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB annotates based on functional similarity; despite similar I/O patterns, these methods serve entirely different purposes (GUI initialization vs version check), so they would be considered non-clones.
- 共享行为: Open a URL using standard Java networking classes；Read lines from the URL input stream using BufferedReader；Handle IOException with a try-catch block
- 行为差异: A creates a full GUI with panels, buttons, and HTML display; B only performs a version check and calls another method；A parses XML and optionally applies XSLT transformation; B parses lines starting with specific prefixes；A sets up layout and displays the GUI; B shows/hides wait cursor and does not involve GUI components
- 修正建议: Incorporate method-level semantic embeddings that capture intent rather than local token patterns；Use dataflow or graph-based representations to distinguish different control flows and data transformations；Augment training with pairs that have similar API usage but different purposes

### case_id=2007 FN partial_functionality

- 方法: `main` vs `parse`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Extracts all files from a KMZ archive (ZIP) downloaded via HTTP or file protocol and saves them to disk.
- B 摘要: Parses an input stream: if the resource name is in a list of wanted files, copies the stream to that file; otherwise passes parsing to a downstream parser.
- 静态失败原因: Static BERT/GraphCodeBERT likely failed due to low token Jaccard (0.1625) and heavy lexical differences (different method names, variable names, and control flow), causing the model to focus on surface forms rather than the underlying shared pattern of stream copying.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely labeled these as clones because both functions take an input stream and write it to a file via FileOutputStream, which can be seen as a Type-4 (functional similarity) clone where the core operation 'stream to file' is shared, despite different contexts and additional logic.
- 共享行为: Both write data from an input stream to a FileOutputStream.
- 行为差异: Function A always decompresses a ZIP archive and extracts all entries; Function B conditionally copies the raw stream without decompression.；Function A is a standalone main method; Function B is part of a parsing pipeline with a downstream parser fallback.；Function A handles multiple protocols (file, http); Function B does not.
- 修正建议: Incorporate data-flow analysis to identify I/O operations commonality.；Use graph-based models that capture structural patterns like stream-to-file writing.；Augment training data with functional similarity examples beyond lexical overlap.

### case_id=2008 FN benchmark_preference_bias

- 方法: `encodeFileToFile` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Encodes a file to another file using Base64 encoding, with standard stream copying.
- B 摘要: Launches a NexOpen project configuration by setting up Maven POMs, handling profiles, and scheduling an install action.
- 静态失败原因: The static model correctly predicted non-clone due to very low token Jaccard (0.067) and clearly different semantics; however, the benchmark mislabeled them as clones.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled these as clones due to both performing file I/O operations (reading and writing files) and the presence of stream handling, leading to a broad type-4 partial functionality similarity.
- 共享行为: Both functions involve file I/O operations (reading from and writing to files).
- 行为差异: Function A is a simple file copy with encoding; Function B is a complex project configuration and launch handler.；Function A returns a boolean success flag; Function B returns void and can throw CoreException.；Function A handles generic file paths; Function B operates within Eclipse workspace resources and specific project structures.；Function B uses XML parsing, property files, and persistence; Function A has none of that.
- 修正建议: Improve benchmark labeling to avoid false positives based on generic I/O similarity.；Enhance models with deeper semantic understanding to recognize such unrelated functionality.

### case_id=2009 FP lexical_or_api_overlap

- 方法: `getUser` vs `issueCommandToServer`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Loads a user from a DAO or reads user data from a config file and saves it.
- B 摘要: Sends a command to a server via HTTP POST and returns the response.
- 静态失败原因: Static BERT may have been misled by the shared use of common Java I/O classes (BufferedReader, InputStreamReader, URL) and the presence of I/O-related code blocks, despite low token-level overlap.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labeled 0 because the functions perform entirely different tasks (user authentication vs command execution) with no meaningful structural or behavioral similarity.
- 共享行为: Both use BufferedReader for reading input.；Both involve I/O operations (file vs network).
- 行为差异: Function A reads from a local config file; Function B sends data via HTTP and reads response.；Function A populates a user object; Function B builds a string response.；Function A handles exceptions by printing stack trace; Function B throws IOException.；Function A parses colon-separated tokens; Function B URL-encodes parameters.
- 修正建议: Incorporate method name embedding for better semantic differentiation.；Use data flow or control flow analysis to capture the distinct logic purpose.；Add context-aware training with more negative pairs that share API tokens but differ in intent.

### case_id=2010 FP boilerplate_overlap

- 方法: `readData` vs `trainClassifier`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Parses multiple comma-separated strings into HashSets and a HashMap for Tibetan character mapping.
- B 摘要: Trains a classifier by executing an external command and handling its I/O streams.
- 静态失败原因: Static BERT/GraphCodeBERT may have been misled by common boilerplate structures (loops, conditionals) in both functions, failing to capture the distinct high-level purposes due to limited context or token-level overlap.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels non-clones when functions perform completely different tasks, even if they share superficial syntactic patterns. Here, the semantic gap is vast.
- 行为差异: readData populates in-memory data structures (sets, maps) from string tokens; trainClassifier executes an external process.；readData has complex tokenization and error handling for specific format; trainClassifier is a simple wrapper around Runtime.exec.；readData is private static; trainClassifier is a public overridden instance method.；readData deals with language-specific character sets; trainClassifier deals with machine learning model files.
- 修正建议: Incorporate data-flow analysis to distinguish local data manipulation from external process invocation.；Use graph representations that highlight method call dependencies and external interactions.；Increase training data for diverse real-world I/O operations.

### case_id=2011 FN benchmark_preference_bias

- 方法: `readGeoParserResult` vs `run`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.8`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Reads geo parser results by constructing an XML request, sending it to a web service, parsing the response to extract place names and gazetteer IDs, with retry logic.
- B 摘要: Opens a hardcoded local URL and reads the response line by line, discarding all content, without any processing or error recovery.
- 静态失败原因: Static BERT likely predicted non-clone correctly by recognizing the significant difference in overall logic, despite API-level overlaps. The model's prediction aligns with functional semantics, but BCB's annotation is questionable, making this a false negative relative to the benchmark.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled them as clones due to superficial lexical overlap (URL, BufferedReader, while loop reading lines) and the broad Type-3/Type-4 criteria that accept partial functional similarity, though the overall purposes differ greatly.
- 共享行为: Both open a URL and read lines from the input stream using BufferedReader.
- 行为差异: Function A constructs a complex XML request and sends it, while B sends a simple GET to a static URL.；Function A parses XML response to extract structured data; B does no parsing.；Function A includes retry logic on failure; B has no retry and empty catch blocks.；Function A is a static method returning a collection; B is a void run method.
- 修正建议: Re-evaluate the BCB annotation for this pair; consider excluding it from benchmarks due to low semantic similarity.；Improve training data quality by removing such borderline or erroneous annotations.

### case_id=2012 FN partial_functionality

- 方法: `getJSONData` vs `invoke`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads JSON data from a given URL using HTTP GET and parses it into a JSONObject, with minimal error handling.
- B 摘要: Invokes a remote method via HTTP POST, reads and parses JSON response, supports retry on connection timeout and error handling.
- 静态失败原因: Static BERT/GraphCodeBERT likely failed due to low lexical overlap (token Jaccard=0.234), different method signatures, and different libraries and error handling patterns, making it miss the semantic similarity of the core HTTP+JSON pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB labels this as clone likely because both functions implement the same high-level task: make an HTTP request and parse JSON from the response, which is considered a Type-4 (semantic) clone despite differences in HTTP method, error handling, and retry logic.
- 共享行为: Both make HTTP requests to a URL；Both read the response content line by line using BufferedReader；Both parse JSON from the response string
- 行为差异: HTTP method: A uses GET, B uses POST；Error handling: A prints stack trace, B throws RuntimeException on bad status and retries on timeout；Return type: A returns JSONObject, B returns generic Object based on method return type；Retry logic: A has none, B retries on ConnectTimeoutException
- 修正建议: Use models that capture high-level intent, like code summarization or graph-based representations；Incorporate data flow analysis to recognize the common pattern of HTTP request-response and JSON parsing；Train or fine-tune on examples with similar core functionality but varied implementations

### case_id=2013 FN lexical_or_api_overlap

- 方法: `copy` vs `modifyApplicationMessage`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a file from source to destination with validation checks.
- B 摘要: Modifies a locale-specific properties file by reading, updating, or adding a key-value pair.
- 静态失败原因: Static BERT models rely heavily on token overlap and lexical patterns; both functions share many common tokens (e.g., File, InputStream, IOException, while, read, close) and structural similarity in exception handling, leading to a false negative misclassification.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely considers them clones because both involve file I/O operations with similar boilerplate (existence checks, stream handling, try-finally), and B includes a file copy step when the locale file is missing, mirroring A's core functionality.
- 共享行为: Both perform file existence checks and handle missing files.；Both open input and output streams for reading and writing.；Both read data in a loop and write to output.；Both close resources in finally blocks with exception handling.
- 行为差异: A copies raw bytes; B reads lines and modifies content based on key-value parsing.；A is a generic file copy; B is specific to properties file maintenance for localization.；A uses FileInputStream/FileOutputStream; B uses FileReader/FileWriter, BufferedReader, and InputStream.；B conditionally copies a default file if the locale file does not exist; A always copies the source file.
- 修正建议: Incorporate dataflow analysis to distinguish byte copy from line-based content transformation.；Use control flow and operation type awareness to differentiate generic file copy from property file modification.；Add representation of key semantic operations (e.g., token replacement vs. exact copy).

### case_id=2014 FP long_range_semantics

- 方法: `readData` vs `setup`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `static_summary_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Reads configuration strings and a data file to populate various sets and hash maps for Tibetan language processing.
- B 摘要: Extracts native libraries from a JAR file to a temporary directory and sets the library path for a webcam application.
- 静态失败原因: The model likely overemphasized structural patterns (loops, conditionals, exception handling) common in long methods, failing to capture the distinct domain-specific goals and data flows.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB would label this as non-clone because the functions implement entirely different functionality, even at a high level of abstraction.
- 共享行为: Both are static private methods.；Both involve file I/O operations.
- 行为差异: Function A initializes sets from configuration strings and parses a structured data file; B extracts JAR entries and determines system architecture.；Function A builds multiple hash maps and sets with specific domain meaning; B copies native library files and adds a library path.；The overall purpose and output are completely different.
- 修正建议: Incorporate method name and documentation embeddings.；Use graph-based representations that capture data dependencies across long ranges.；Train with more diverse non-clone pairs to avoid learning spurious structural correlations.

### case_id=2015 FN benchmark_preference_bias

- 方法: `setBundleInfoName` vs `invoke`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.6`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Reads a URL, parses lines for key-value pairs, and updates bundle names in a list.
- B 摘要: Invokes a remote method via HTTP POST, reads JSON response, and returns deserialized object, with retry on timeout.
- 静态失败原因: The static model correctly predicted non-clone; this is actually a false positive in BCB annotation, not a model failure.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might have considered these as Type-4 clones due to both involving network I/O and line-by-line processing, despite completely different business logic.
- 共享行为: Both use BufferedReader to read text line by line from an input stream
- 行为差异: Function A is a configuration updater; B is an RPC invocation method；A uses URL.openStream() to read a file; B uses HttpClient to make an HTTP request；A returns boolean; B returns deserialized object；B has retry logic; A does not
- 修正建议: Revisit BCB annotation guidelines to ensure semantic equivalence is not overly broad；Use a more fine-grained clone type classification that distinguishes partial functionality

### case_id=2016 FP partial_functionality

- 方法: `copyFile` vs `readData`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Copies a file from source to destination using NIO FileChannel.
- B 摘要: Parses configuration data to populate various sets and maps with tokens.
- 静态失败原因: The static model likely focused on superficial similarities like the presence of 'IOException' and file-related operations, without understanding the core semantic difference between file copying and data parsing.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB would consider these non-clones because they have entirely different purposes and implementations, even though both involve I/O. BCB typically requires substantial semantic overlap for a Type-3/Type-4 clone, which is absent here.
- 共享行为: Both are static methods.；Both may throw or handle IOException.
- 行为差异: copyFile copies file content verbatim; readData parses tokens and populates data structures.；copyFile takes two File objects as input; readData reads from class-level string fields and writes to class-level collections.；copyFile uses sequential byte transfer; readData uses line-by-line tokenization.
- 修正建议: Enhance training data with more non-clones that share I/O exception handling but differ in core functionality.；Incorporate data flow and control flow features to distinguish file copying from token parsing.；Use method-level context (e.g., method name and surrounding code) to reduce false positives from lexical I/O hints.

### case_id=2017 FN benchmark_preference_bias

- 方法: `saveProject` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Saves a multi-component project (types, images, trajectories, databases) to a zip file, involving directory creation, database queries, and file I/O.
- B 摘要: Retrieves a resource as an InputStream with caching, handling HTTP URLs and local file operations.
- 静态失败原因: Static BERT/GraphCodeBERT likely failed because it relied on token similarity and semantic embeddings, which correctly identified the low lexical overlap (Jaccard 0.1) and distinct method names. However, it may have missed a supposed similarity in I/O patterns that BCB regarded as clone-worthy. Alternatively, the model might have been too strict, but in this case it seems correct.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have considered these clones due to both involving file I/O streams, error handling, and similar structural patterns (e.g., creating files, reading/writing with buffers) despite entirely different high-level purposes. This is a very broad Type-4 interpretation that is not typical.
- 共享行为: Both use File, InputStream, OutputStream, and try-catch blocks for I/O exceptions；Both create File objects and manipulate file paths；Both close streams in finally blocks or catch clauses
- 行为差异: saveProject writes multiple files and directories; getResourceAsStream reads a single resource；saveProject involves database operations and zip creation; getResourceAsStream handles HTTP cache logic；saveProject returns boolean; getResourceAsStream returns InputStream；saveProject is not synchronized; getResourceAsStream is synchronized
- 修正建议: Improve clone detection to consider method-level semantics and purpose beyond low-level I/O patterns；Use additional features like method name similarity or call graphs to disambiguate；Re-evaluate BCB labeling for this pair to ensure consistency with typical Type-4 guidelines

### case_id=2018 FN benchmark_preference_bias

- 方法: `copy` vs `doGet`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Copies a file from source to destination using NIO FileChannel.
- B 摘要: Handles an HTTP GET request for a portal page with retrieval, authorization, logging, and file caching.
- 静态失败原因: The static model correctly predicted non-clone based on low token similarity and lack of semantic overlap; it did not fail but disagreed with the erroneous BCB label.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB likely mislabeled this pair as a clone, possibly due to both methods containing file operations, but the semantics are completely different.
- 共享行为: Both involve file I/O operations (read/write)
- 行为差异: Code A is a simple file copy utility; Code B is a complex servlet handler with request processing, page retrieval, authentication, caching, and error handling.；Code A uses FileChannel for efficient transfer; Code B uses FileWriter for caching output.
- 修正建议: Remove this pair from the clone set as it is a false positive in BCB annotation.；Re-annotate with clear guidelines to avoid labeling unrelated code as clones.

### case_id=2019 FN partial_functionality

- 方法: `doVersionCheck` vs `File2String`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.65`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Checks for software version update by reading a URL and parsing version/build lines.
- B 摘要: Reads a file or classpath resource into a string, printing errors and exiting on failure.
- 静态失败原因: Static models like BERT may have focused on lexical dissimilarities (different method names, different constants, different control flow) and low token overlap (0.216), thus failing to recognize the shared IO reading pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considered both as Type-4 (semantic) clones because they share the pattern of reading an input stream line by line and processing each line, which is a common boilerplate task.
- 共享行为: Both read lines from an input stream using BufferedReader and InputStreamReader；Both handle IOException with try-catch blocks
- 行为差异: Method A uses URL input and compares build versions; method B uses file/classpath input and concatenates lines into a string；Method A is void with UI feedback and cursor changes; method B returns a string and uses System.exit on errors；Method A has no return value; method B returns the file content
- 修正建议: Improve models to recognize common boilerplate patterns like reading lines from a stream regardless of the specific processing logic；Incorporate more structural matching of input/output patterns

### case_id=2020 FN benchmark_preference_bias

- 方法: `doBody` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Reads a file and copies its contents to an HTTP response output stream.
- B 摘要: Retrieves a resource by name, downloads and caches it locally, then returns an InputStream to the cached file.
- 静态失败原因: The static prediction correctly identified them as non-clones, but BCB ground truth called them clones, likely due to preferential bias for broad I/O usage similarity. The model failed to align with that bias.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have considered them clones due to the shared high-level pattern of reading from an input source and writing to an output stream, despite very different specifics and purposes.
- 共享行为: Use of BufferedInputStream and BufferedOutputStream for I/O operations；Exception handling that closes streams in finally blocks
- 行为差异: A writes directly to an HTTP response; B caches to a local file and returns a stream；A does not implement caching; B has complex caching logic；A uses a fixed file path from loadData; B resolves URLs and handles HTTP connections
- 修正建议: Include more detailed semantic annotations about the overall data flow and purpose；Reduce reliance on superficial I/O pattern similarity in ground truth labeling

### case_id=2021 FN partial_functionality

- 方法: `copyResource` vs `copy`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a single resource (URL or file) to a destination file using byte-by-byte streaming.
- B 摘要: Copies a file or directory to a target, handling recursion for directories and using file channels for file copies.
- 静态失败原因: Low token overlap (0.19697) and different API usage (URL vs File, NIO vs IO) led to focus on differences, missing the high-level semantic similarity of copying.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often considers functions performing the same high-level task (copying resources/files) as clones, even with different implementations and scope.
- 共享行为: Both copy data from a source to a destination；Both handle file sources；Both create output files if needed；Both close streams
- 行为差异: B supports directory recursion, A does not；B uses NIO FileChannel for file copy, A uses byte-by-byte；B checks source/target type consistency, A does not；B handles non-existing target creation, A does not
- 修正建议: Incorporate high-level task recognition via AST or program dependence graphs；Use functional similarity detection based on input-output behavior；Train with more diverse pairs that vary in API and structure

### case_id=2022 FN partial_functionality

- 方法: `copyResource` vs `getFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource (from URL or file) to a destination file, throwing Exception on failure.
- B 摘要: Returns a file from user directory or copies it from a resource if not found locally, throwing IOException or IllegalStateException.
- 静态失败原因: Low token overlap (0.24), different method names, and distinct control flow (e.g., file existence check) misled the static model, which relies heavily on lexical and structural similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels as clone when functions share core functionality (copying a resource to a file), even with varying details, as Type-4 clones.
- 共享行为: Both open an input stream from a resource (URL or file) and write to a file output stream.
- 行为差异: copyResource does not check for existing file; getFile checks and returns existing file.；copyResource writes to a destination file; getFile writes to a file in the user directory.；getFile returns the created/existing file; copyResource returns void.；copyResource reads byte by byte; getFile uses IOUtils.copy.
- 修正建议: Incorporate high-level semantic patterns like 'read input stream, write to output stream'.；Use dataflow or program dependency graph features to capture functional similarity.；Train on more varied clone types (Type-4) to recognize partial functionality clones.

### case_id=2023 FN benchmark_preference_bias

- 方法: `doVersionCheck` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.6`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Checks for version updates by reading a URL and parsing build lines.
- B 摘要: Sends an HTTP POST request to a social network API with predefined parameters and prints the response.
- 静态失败原因: Static BERT/GraphCodeBERT likely failed because it recognized the low lexical overlap and distinct API usage, correctly predicting non-clone; but BCB would consider it a clone, so the model underperformed relative to BCB label.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as a clone due to both functions involving URL-based I/O and line reading, which could be seen as a broad Type-4 semantic clone pattern: 'fetch data from URL and process lines'.
- 共享行为: Both open a URL and read lines from an input stream using BufferedReader.
- 行为差异: Function A performs a version check and calls a helper; Function B constructs a POST request and prints results.；Function A uses InputStream from URL, Function B uses HttpURLConnection with POST method.；Function A handles exceptions with error dialog; Function B throws IOException and prints output.
- 修正建议: Improve BCB annotation consistency to avoid overly broad Type-4 clones.；Enhance model to better capture functional equivalence beyond lexical similarity.

### case_id=2024 FP boilerplate_overlap

- 方法: `googleImageSearch` vs `handledRun`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Searches Google Images for album art and extracts image URLs.
- B 摘要: Downloads updated game data XML from a server and saves it to a file.
- 静态失败原因: Static BERT models may be misled by the shared boilerplate pattern (try-catch, URL, BufferedReader, readLine) and similar exception handling, causing overestimated similarity despite low token Jaccard.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels these as non-clones because they serve completely different purposes (image search vs. game data update), despite sharing some structural boilerplate.
- 共享行为: Both perform an HTTP GET request using URL and BufferedReader.；Both handle exceptions with logging or error dialogs.；Both read from an input stream line by line.
- 行为差异: A fetches image search results, B fetches game data XML.；A adds URLs to a list, B writes data to a file.；A conditionally executes only if artist changed, B always runs with version check.；A replaces spaces with + in URL, B does not.
- 修正建议: Incorporate data-flow analysis to distinguish how read data is used.；Use contrastive learning with more diverse negative pairs.；Include method and class names as additional context.

### case_id=2025 FN partial_functionality

- 方法: `downloadURLtoString` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads URL content and returns it as a string.
- B 摘要: Sends an HTTP POST request with hardcoded parameters and prints the response.
- 静态失败原因: The low Jaccard similarity (0.133) and different API calls (openStream vs HttpURLConnection) caused the model to classify them as non-clones. The model likely missed the shared reading loop due to the surrounding code.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB annotators may have considered them Type-4 clones because both involve reading from a URL line-by-line, ignoring the differences in HTTP method and output handling.
- 共享行为: Both open a URL connection and read lines using BufferedReader until null
- 行为差异: Function A uses GET (url.openStream) and returns the string; Function B uses POST and prints output.；Function B includes extensive parameter setup and connection configuration.
- 修正建议: Enhance the model to recognize common sub-patterns like URL reading loops even when the rest of the function differs.；Use data flow analysis to match input/output patterns.

### case_id=2026 FN partial_functionality

- 方法: `doGet` vs `upload`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Handles HTTP page requests by parsing parameters, querying pages, checking permissions, logging, rendering output, and caching.
- B 摘要: Uploads an image file from a source to a destination directory.
- 静态失败原因: Low lexical and structural overlap, different method names and contexts, and focus on overall function rather than partial file I/O similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB might have considered both as file I/O operations, but this is too broad and typical BCB annotation does not consider such high-level similarity as a clone.
- 共享行为: Both write data to files (A writes HTML cache, B writes uploaded file)
- 行为差异: A involves complex web request handling, database lookups, authorization, logging, statistics; B is a simple file copy with no business logic.；A uses servlet context; B is a standalone method.
- 修正建议: Enhance model to capture file I/O operations as a common pattern even in different contexts.；Use program slicing to isolate common sub-behaviors.

### case_id=2027 FN partial_functionality

- 方法: `doGet` vs `createOutputStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Handles HTTP GET request, retrieves a page, checks permissions, logs and outputs page HTML, with optional caching to a temp file.
- B 摘要: Reads a zip file, copies all entries except content.xml, then adds a new content.xml entry, returning a BufferedWriter.
- 静态失败原因: Static BERT/GraphCodeBERT fails due to very low token overlap (Jaccard 0.0746) and domain-specific vocabularies, making it difficult to capture the abstract similarity in output generation logic that BCB might have considered.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled them as clones due to both involving output generation with file I/O, error handling, and stream management, even though the overall functionality differs significantly.
- 共享行为: Both involve file I/O and output stream handling；Both use exception handling and logging；Both manage resources like files and streams
- 行为差异: Function A is a servlet handler; function B is a utility method for zip processing；Function A operates on HTTP request/response; function B operates on files；Function A writes HTML content; function B writes zip entries；Function A has conditional caching logic; function B is deterministic
- 修正建议: Improve semantic understanding by incorporating dataflow or program dependence information；Use finer-grained clone detection that focuses on smaller functional slices rather than whole functions；Enhance training data with more diverse semantic pairs to recognize broad similarity patterns

### case_id=2028 FN benchmark_preference_bias

- 方法: `getFile` vs `doPost`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `preference_memory_with_manual_audit`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies an XML attribute, and saves it to a temporary file.
- B 摘要: Handles a POST request by parsing multipart form data, fetching a webpage from a file upload or URL, and writing email content to the response.
- 静态失败原因: Static BERT/GraphCodeBERT models rely on token overlap and local context; the very low Jaccard similarity (0.12) and distinct method names/structures led to a non-clone prediction, missing the broader shared I/O pattern.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB likely labeled these as clones because they share a broad Type-3 pattern: both download content from URLs, handle streams, and have similar exception handling structures, even though their high-level purpose differs.
- 共享行为: Both open URL connections and read input streams；Both write to output streams (file or response)；Both use try-catch for IO exception handling；Both involve copying data between streams
- 行为差异: Function A is a static utility returning a file path; Function B is a servlet method writing to HTTP response；Function A modifies XML and handles WSDL-specific logic; Function B processes file uploads and generates email content；Function A uses FileChannel for efficient transfer; Function B uses IOUtils.copy and ByteArrayOutputStream
- 修正建议: Incorporate structural features like control flow and data flow graphs to capture similar patterns despite different tokens.；Use graph-based models that can abstract common sub-patterns like 'URL.openStream() -> copy to output stream'.

### case_id=2029 FP lexical_or_api_overlap

- 方法: `getRequestContent` vs `wordFrequency`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Opens a URL connection and returns the first line of the response.
- B 摘要: Opens a URL, reads lines, and returns the frequency of a word by matching a regex pattern.
- 静态失败原因: Static BERT/GraphCodeBERT likely over-relied on lexical and API-level overlap (URL, BufferedReader, InputStreamReader) and similar structural patterns (try-catch in B), ignoring the distinct control flow and data dependencies.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels non-clones when functions have different purposes (one retrieves raw line, the other performs text mining). The broad Type-3/4 acceptance requires partial functionality similarity, but here the core logic differs.
- 共享行为: Both use URL and BufferedReader to read from a URL.；Both connect to a network endpoint via HTTP.
- 行为差异: A returns the first line of the response; B searches for a pattern across multiple lines and returns an integer frequency.；A does not handle exceptions; B catches MalformedURLException and IOException.；A explicitly disconnects the HttpURLConnection; B does not disconnect.；A returns a String; B returns an int.
- 修正建议: Incorporate data-flow analysis to distinguish variable usage (e.g., line vs inputLine matching pattern).；Use abstract syntax trees with attention to method return types and exception handling differences.；Train on more diverse examples where API usage alone is misleading.

### case_id=2030 FP partial_functionality

- 方法: `main` vs `readData`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Demonstrates FileChannel operations for writing and reading text with different encodings.
- B 摘要: Parses comma-separated tokens from strings and populates several sets and maps for further processing.
- 静态失败原因: The model may have been misled by common boilerplate (e.g., file reading) or token names, but token overlap is low; possibly a random error or sensitivity to specific patterns.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely judged non-clone because the functions have completely different purposes and minimal semantic overlap.
- 行为差异: Function A performs file I/O with ByteBuffer and encodings; Function B parses token strings and fills data structures.；Function A focuses on character encoding demonstration; Function B is part of a larger initialization routine.；Control flow in A is linear with file operations; B has loops and conditional parsing logic.
- 修正建议: Improve training data to reduce false positives on unrelated functions that share generic I/O patterns.；Incorporate dataflow or structural information to differentiate trivial boilerplate from core logic.

### case_id=2031 FN partial_functionality

- 方法: `readIntoList` vs `runInternal`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads HTML from a URL and populates a map of JMenuItems with action commands.
- B 摘要: Downloads and parses OPDS catalog entries from a URL, handling pagination and book downloads.
- 静态失败原因: Static models rely on token overlap and API similarity; the functions share only generic URL and I/O tokens, while domain-specific terms (JMenuItem vs. OPDS, etc.) differ significantly, causing a false negative.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider them as Type-4 clones because both perform reading from a URL and processing input, but the processing is vastly different; the low overlap suggests this labeling might be an error.
- 共享行为: Both open a URL connection；Both read input line by line；Both use try-catch for exceptions；Both involve network I/O
- 行为差异: A creates JMenuItems for GUI; B handles HTTP/OPDS specifics and file downloads；A parses simple HTML tags; B parses structured XML/Atom feeds with pagination；A sets action listeners; B manages progress and callbacks
- 修正建议: Include more diverse Type-3/Type-4 training examples；Use graph-based models that capture abstract I/O patterns；Incorporate higher-level semantics like 'read from URL and process'

### case_id=2032 FN benchmark_preference_bias

- 方法: `doVersionCheck` vs `httpRequestByPOST`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `preference_memory_with_manual_audit`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Fetches a URL to check for newer version and displays GUI messages accordingly.
- B 摘要: Sends an HTTP POST request and returns the response body as a string, handling errors via status codes.
- 静态失败原因: The static model likely failed because it learned a stricter definition of clones based on token overlap and structural similarity. The low Jaccard similarity (0.2258) and distinct method names and logic caused it to predict non-clone, while BCB's broader interpretation considers the underlying I/O pattern sufficient for a clone label.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB likely labeled these as clones due to broad Type-4 semantic similarity: both involve network I/O, reading lines from a stream, and processing lines. Despite functional differences, the shared pattern of HTTP communication and line-based reading may align with BCB's acceptance of partial functionality overlap.
- 共享行为: Both open a network connection to a URL.；Both read input line by line using BufferedReader.
- 行为差异: A uses GET (url.openStream) while B uses HTTP POST with parameters.；A parses lines for '.version' and '.build' prefixes; B appends all lines to a buffer.；A returns void and shows dialogs; B returns String and sets error codes.；Error handling differs: A shows error messages via GUIUtilities, B sets instance fields.
- 修正建议: Train models with BCB-style annotations that emphasize functional similarity over exact syntax.；Incorporate high-level semantic features like API usage patterns or intent recognition.；Use data augmentation to include examples of partial functionality clones.

### case_id=2033 FN partial_functionality

- 方法: `main` vs `copy`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a URL and extracts its ZIP entries to disk.
- B 摘要: Copies a file from source to destination using NIO memory-mapped buffer.
- 静态失败原因: Low token overlap (0.197) and different API calls make it hard for static BERT to recognize the high-level I/O pattern; it focuses on local tokens rather than the abstract data flow.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have considered both as data transfer operations from input to output, thus labeling as a Type-4 (semantic) clone despite differing input sources and processing details.
- 共享行为: Both perform file I/O: reading from an input source and writing to an output file.；Both use buffered or efficient I/O mechanisms.
- 行为差异: A involves network download and ZIP extraction; B is a local file copy.；A processes multiple ZIP entries; B copies a single file.；A uses ZipInputStream; B uses FileChannel and MappedByteBuffer.；A prints progress; B does not.
- 修正建议: Incorporate dataflow analysis or program dependency graphs.；Use code summarization to capture abstract behavior.；Include task-specific typology for I/O operations.

### case_id=2034 FN benchmark_preference_bias

- 方法: `doImageProcess` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Processes an HTTP image request by optionally resizing and writing image data to the response stream.
- B 摘要: Builds an editable site by reading XML, transforming it with XSLT, and writing output files for each page.
- 静态失败原因: The static BERT model likely correctly identified the low lexical overlap (Jaccard 0.078) and different API usage, thus predicting non-clone. It did not fail; it correctly distinguished the methods' semantics.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have considered these clones due to both being I/O heavy operations that read input and write output, but this is a very broad interpretation that ignores domain specificity.
- 共享行为: Both involve reading from input streams and writing to output streams；Both handle IOException
- 行为差异: Method A is specific to image processing and HTTP servlet response; Method B handles XML transformation and file system operations for site generation；Method A uses a simple if-else for resizing; Method B has complex loops, string replacement, and multiple I/O operations；Method A is short and focused; Method B is long and involves many parameters and steps
- 修正建议: Review BCB annotation guidelines to ensure such cases are not considered clones；Improve model to ignore boilerplate I/O patterns and focus on core functionality

### case_id=2035 FN benchmark_preference_bias

- 方法: `ExternalDecoder` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Constructor that copies input stream to process output stream in a separate thread.
- B 摘要: Method that builds a site for editing by processing pages with XSLT transformations and file I/O.
- 静态失败原因: Static BERT actually predicted correctly (non-clone) because token Jaccard is very low and no structural similarity; the model did not fail.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have mislabeled due to some vague similarity like both use InputStream or process streams, but this is insufficient for a clone even under broad criteria.
- 共享行为: Both involve I/O streams but at a very basic level
- 行为差异: A is a small constructor for starting a thread to copy stream; B is a large method for site editing；A has no page processing, XML transformations, or file system operations beyond stream copy; B does all those；A deals with process I/O; B deals with page rendering and file writing
- 修正建议: Re-evaluate BCB annotation for this pair; likely it is not a clone.；Improve benchmark curation to avoid such mismatches.

### case_id=2036 FP boilerplate_overlap

- 方法: `readData` vs `copyResourceToFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Parses a set of comma-separated string constants into various HashSets and a map of valid input sequences.
- B 摘要: Copies a resource file to a destination file using I/O streams with proper cleanup.
- 静态失败原因: Static model likely overfitted to superficial similarities like 'IOException' or 'try-catch' boilerplate, ignoring the drastically different core logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clones due to completely different functionality; they share no meaningful common behavior.
- 共享行为: Both handle I/O exceptions (though in different styles).
- 行为差异: Function A parses and populates data structures; Function B copies file content.；Function A uses StringTokenizer and HashSet; Function B uses InputStream, OutputStream, and IOUtils.；Function A has complex conditional logic and multiple loops; Function B is a straightforward copy.；Function A is static; Function B is instance method.
- 修正建议: Train with more diverse negative samples that share boilerplate but differ in semantics.；Incorporate dataflow or control-flow analysis to better capture function purpose.

### case_id=2037 FN partial_functionality

- 方法: `modifyApplicationMessage` vs `resolvePlugins`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Modifies a localized properties file by updating or adding a property value.
- B 摘要: Downloads and caches a remote plugins XML file then resolves plugins locally.
- 静态失败原因: Static BERT models rely on token sequences and structural patterns. The low token Jaccard (0.126) indicates low lexical overlap, but the model may have been misled by the shared control flow pattern (file existence check, creation, processing) and the common error-handling idiom, causing it to classify as non-clone due to lack of semantic understanding.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this as a clone due to the structural similarity: both functions have a try-catch block, check file existence, conditionally create the file from a source, then perform file processing. The overall pattern of file-based caching or fallback is considered a clone under broad Type-3/Type-4 criteria.
- 共享行为: Both check if a file exists and create it from a default source if missing；Both use try-catch for error handling with printStackTrace
- 行为差异: A manipulates properties file content line by line; B downloads from a URL without content manipulation.；A is locale-specific and updates message values; B is about plugin resolution and delegation.；A involves reading and writing properties; B involves network I/O and file copy.
- 修正建议: Incorporate dataflow analysis to understand the different purposes of file sources and manipulation.；Use more detailed semantic representation like program dependency graphs to capture distinct functionality.；Train on more diverse clone types to avoid over-reliance on structural overlap.

### case_id=2038 FN benchmark_preference_bias

- 方法: `main` vs `convert`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a URL, unzips it, and saves each entry as a file.
- B 摘要: Converts an ACRNEMA medical image file to DICOM format, handling pixel data and metadata.
- 静态失败原因: Static BERT models rely on token overlap (Jaccard=0.15) and surface syntax, which are too low here. They miss the high-level behavioral similarity that BCB annotators might see.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might consider these clones due to both being I/O-intensive file processing utilities with stream handling and byte-level operations, falling under a lenient Type-4 interpretation.
- 共享行为: Both read from an input stream and write to an output file；Both use while loops to process data byte by byte；Both perform file I/O operations
- 行为差异: Different input formats: ZIP vs. DICOM/ACRNEMA；Different processing logic: extracting vs. pixel data transformation；One handles network URLs, the other local files；One outputs multiple files, the other a single file
- 修正建议: Add training examples of broad Type-4 clones；Use representation learning for program workflow instead of token sequences；Incorporate I/O and file-processing patterns

### case_id=2039 FN partial_functionality

- 方法: `main` vs `getNetworkServersIPs`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends a POST request with multiple parameters to RenRen API and prints the response.
- B 摘要: Reads a list of server IPs from a URL by parsing lines starting with "!SERVERS".
- 静态失败原因: Static BERT/GraphCodeBERT likely relied on token overlap (low Jaccard) and distinct method names/parameters, failing to abstract the shared network I/O pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider this a Type-3 clone because both functions share the boilerplate pattern of opening a URL, reading lines via BufferedReader, and processing input, despite different domain-specific logic.
- 共享行为: Open a URL connection；Read lines from an input stream using BufferedReader
- 行为差异: Function A sends a POST request with many parameters; B reads a GET response and parses for a specific format.；A outputs to console; B returns a Vector of IPs.；A uses HttpURLConnection with POST method; B uses URLConnection (GET).；A builds URL with query parameters; B uses the netaddress directly.
- 修正建议: Train with augmented pairs that capture common I/O idioms as clone indicators.；Incorporate data flow or control flow graphs to detect structural similarity beyond tokens.；Use method-level context to recognize boilerplate patterns.

### case_id=2040 FN partial_functionality

- 方法: `httpRequestByPOST` vs `getNetworkServersIPs`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.65`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends an HTTP POST request and returns the response body as a string, with error handling.
- B 摘要: Connects to a URL, reads lines, and extracts server IPs from lines starting with '!SERVERS', returning them in a vector.
- 静态失败原因: Static BERT models rely heavily on token overlap and surface-level structure, which are low here (Jaccard 0.22). The model missed the abstract semantic similarity of network I/O pattern due to different method names, return types, and specific constants.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels Type-4 clones based on common high-level behavior, such as network I/O and line processing, even when specific functionality differs.
- 共享行为: Both open network connections and read input streams；Both use BufferedReader to read lines；Both handle IOException
- 行为差异: Function A uses HTTP POST with parameters; function B uses a simple URL GET；Function A returns a single string; function B returns a vector of strings；Function A parses response status codes; function B parses specific line patterns
- 修正建议: Enhance model with data flow or control flow graphs to capture shared I/O patterns；Use contrastive learning to emphasize abstract semantic similarity over lexical overlap

### case_id=2041 FP boilerplate_overlap

- 方法: `readReferenceText` vs `downloadModel`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a reference text from a URL resolved from an identifier, returning the content as a string.
- B 摘要: Downloads an RDF model from a URL using HTTP headers, returning a Model object.
- 静态失败原因: The static model likely overemphasized the shared boilerplate pattern (URL.openStream, InputStream, try-catch) and ignored the semantic differences in return types and content processing.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically requires functional similarity; both involve URL reading but have distinct purposes (text retrieval vs RDF model download), so they are not considered clones.
- 共享行为: Both open a URL and read from an InputStream；Both handle IOException and MalformedURLException；Both use a try-catch block for I/O operations
- 行为差异: Different return types: String vs Model；readReferenceText resolves an identifier to a filename, downloadModel takes a direct URL；readReferenceText reads text line by line, downloadModel reads into an RDF model；Different exception handling: NoContentException vs RuntimeException
- 修正建议: Incorporate return type and method signature semantics；Distinguish between text reading and structured model parsing；Consider the specific purpose of the method (e.g., reading reference text vs downloading RDF model)

### case_id=2042 FN benchmark_preference_bias

- 方法: `doGet` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Handles an HTTP GET request by forwarding the request to another URL and copying the response headers and body back.
- B 摘要: Builds a site for editing by iterating over pages, performing XSLT transformations, and writing output files.
- 静态失败原因: The static model likely correctly identified the lack of semantic similarity due to low token overlap (Jaccard=0.056) and different API usage; it did not fail but rather correctly predicted non-clone.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might have labeled these as clones due to a superficial similarity in handling URLs or I/O, but the core functionality is entirely different; the annotation likely errs on the side of broad Type-4 inclusion.
- 共享行为: Both involve I/O operations (reading/writing streams or files)
- 行为差异: Function A is a simple HTTP proxy/forwarder；Function B is a complex site generation process with multiple file operations；Function A deals with HTTP request/response objects；Function B deals with XML, properties, and file system abstraction
- 修正建议: Re-evaluate this pair with a stricter annotation policy；Remove or relabel the pair in the benchmark to avoid biasing models

### case_id=2043 FP lexical_or_api_overlap

- 方法: `readUNI` vs `doVersionCheck`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads tab-separated lines from a URL, extracting id and description, and adds them to a vector.
- B 摘要: Checks for software version update by reading a version file from a URL and comparing build numbers.
- 静态失败原因: Static BERT/GraphCodeBERT might have focused on the lexical overlap of opening URL and reading lines, ignoring the broader functional difference. The token Jaccard is 0.24, which is low, but the model might have been fooled by the structural similarity of the try-catch-finally and loop pattern.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels as non-clone because the two functions have different inputs, outputs, and business logic, even though they share a common I/O pattern.
- 共享行为: Open a URL and read lines；Use try-catch for I/O exceptions；Process each line in a loop
- 行为差异: Different parsing logic (tab-separated vs. key-value prefix)；Different output (populate vector vs. show messages)；Different method signatures and additional GUI interactions in B
- 修正建议: Include more context about the overall function purpose；Train with contrastive examples that share API usage but differ in logic；Use data flow analysis to distinguish different processing paths

### case_id=2044 FN benchmark_preference_bias

- 方法: `main` vs `modifyApplicationMessage`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Copies a file from source to destination using FileChannel and ByteBuffer in a main method.
- B 摘要: Modifies a locale-specific application message properties file, creating it from an English template if missing, then updating or adding a key-value pair.
- 静态失败原因: Static BERT/GraphCodeBERT correctly predicted non-clone because the token and structural similarity are very low (Jaccard=0.17) and the functionalities are clearly different. The model did not fail; it disagreed with the BCB label.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may label this as a clone due to broad Type-3/Type-4 criteria, interpreting both as 'file copying' operations (one copies a file entirely, the other copies a template file before modification), or due to the presence of common file I/O boilerplate (while loops reading/writing).
- 共享行为: Both perform file I/O operations (reading and writing)；Both use standard Java IO classes
- 行为差异: Function A copies an entire file byte-by-byte; Function B modifies specific properties file content with key-value replacement；Function A uses FileChannel and ByteBuffer; Function B uses FileReader/FileWriter, BufferedReader, and Properties；Function A is a main method with command-line arguments; Function B is a non-static method with locale, messageName, messageValue parameters；Function A does not handle properties, localization, or conditional file creation
- 修正建议: Re-evaluate BCB labeling guidelines for partial functionality similarity to avoid false positives.；Incorporate data flow analysis to distinguish file copy from property modification.；Use functional semantics rather than surface-level I/O patterns.

### case_id=2045 FN benchmark_preference_bias

- 方法: `convert` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Converts an ACRNEMA stream file to DICOM format, validating and writing pixel data with optional bit inflation.
- B 摘要: Builds a site for editing by reading XML, applying XSLT transformations, and writing generated pages with control file integration.
- 静态失败原因: The static BERT model correctly identified the lack of semantic similarity due to very low lexical overlap (Jaccard 0.09) and different API usage; the model's prediction of non-clone is consistent with a strict semantic interpretation, but the BCB ground truth label may be erroneous or based on an overly broad criterion.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may label this as a clone due to very broad Type-4 semantic similarity (both read, transform, and write data), but the domains and specific operations are entirely different. Alternatively, this could be a labeling error.
- 共享行为: Both read from input streams and write to output streams.；Both perform data transformation and output file generation.
- 行为差异: Function A deals with medical image format conversion (ACRNEMA to DICOM), while Function B handles web page generation from XML.；Function A uses DICOM-specific tags and pixel data manipulation; Function B uses XSLT transformers, DOM, and string replacement.；Function A has low-level byte manipulation for pixel data; Function B operates on higher-level strings and XML nodes.；Function A has a single source file and destination; Function B processes multiple pages with multiple configuration files.
- 修正建议: Re-evaluate the ground truth label for this pair; it may be a misannotation.；If BCB labels are considered correct, the model needs to capture high-level workflow similarities beyond lexical matches, but in this case, the functions are truly unrelated.

### case_id=2046 FP lexical_or_api_overlap

- 方法: `sendRequest` vs `SRWGuiClient`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Sends an XML request to a server via HTTP with GZIP compression and builds a JDOM document from the response.
- B 摘要: Constructs a Swing browser GUI that fetches and displays an XML/XSL page after optional XSL transformation.
- 静态失败原因: The static BERT model likely focused on overlapping tokens like 'URL', 'BufferedReader', 'InputStreamReader', 'url.openStream()', etc., and missed the overall control flow and distinct functionality.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels as non-clone because the functions have completely different purposes and behaviors despite some shared low-level APIs.
- 共享行为: Both use HTTP connections to fetch data from URLs；Both read from input streams；Both handle exceptions
- 行为差异: Function A sends a request (output) then reads response; Function B only reads (no request body)；Function A compresses output with GZIP; Function B does not send data；Function A builds a JDOM document; Function B displays HTML in a JEditorPane；Function A is a method for sending requests; Function B is a constructor setting up a browser
- 修正建议: Enhance the model to incorporate control flow and dataflow features；Use graph-based representations to capture structure and not just token sequences；Include functional summarization to distinguish different high-level behaviors

### case_id=2047 FN partial_functionality

- 方法: `File2String` vs `getNetworkServersIPs`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a file from a given filename or classpath and returns its content as a single string, terminating on failure.
- B 摘要: Fetches a URL, parses lines for server markers, and returns a vector of server IPs.
- 静态失败原因: Static BERT likely focused on low token similarity (0.24) and differences in method names, variables, and strings, missing the high-level structural similarity of reading and processing lines.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as functions that read from a resource and return extracted data, seeing them as broad Type-3 clones due to similar structural pattern (open stream, read lines, return result) despite different specifics.
- 共享行为: Both open an input stream (file or URL) and use BufferedReader to read lines.；Both handle IOException using try-catch blocks.
- 行为差异: Input source: file system/classpath vs URL.；Output type: single String vs Vector<String>.；Processing: simple line concatenation vs parsing for '!SERVERS' and lines starting with ';'.；Error handling: System.exit on failure in A vs print stack trace in B.
- 修正建议: Incorporate more structure-aware features like data flow graphs.；Train on examples of common I/O patterns across different resources.；Use contrastive learning to emphasize structural similarity over lexical differences.

### case_id=2048 FN partial_functionality

- 方法: `addDataFromURL` vs `fileDownload`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads text from a URL line by line and appends to an internal string buffer, with fallback appending the URL string on error.
- B 摘要: Downloads raw bytes from a URL and writes them to a local file, logging errors.
- 静态失败原因: The model likely focused on lexical differences such as method names, variable names, output targets (string vs file), and low token Jaccard. It failed to capture the high-level semantic similarity of 'fetching content from a URL' due to differing subsequent operations.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels as clones if the core functionality is similar, even if the output medium and data format differ. Both functions are centered on downloading content from a URL, which BCB could consider Type-4 (functionally similar).
- 共享行为: Both fetch content from a URL using a network connection.；Both handle I/O exceptions with try-catch blocks.；Both use BufferedReader and InputStreamReader to read the input stream.
- 行为差异: A reads line-by-line (text-oriented), while B reads byte-by-byte (binary-oriented).；A appends lines to a string buffer, B writes bytes to a file.；A falls back by appending the URL string on error, B logs the error via Logger.；A appends newlines after each line, B does not modify the data.
- 修正建议: Train the model with more examples of partial functionality clones where the core operation is similar but post-processing differs.；Incorporate graph-based representations to highlight data flow from URL input to stream consumption.；Use contrastive learning to emphasize shared subgoals over surface-level differences.

### case_id=2049 FP lexical_or_api_overlap

- 方法: `getRequestContent` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches and returns the first line from a given URL.
- B 摘要: Searches Google Images for a query, parses image URLs from the response, and updates UI components.
- 静态失败原因: Static BERT models rely heavily on token overlap and may be misled by common API sequences like HttpURLConnection and BufferedReader, treating them as indicative of clone behavior despite overall functional divergence.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels these as non-clones because they have different signatures and perform fundamentally different tasks despite sharing HTTP boilerplate. The clone definition in BigCloneBench requires more than trivial API overlap.
- 共享行为: Both open an HTTP connection and read from the input stream using BufferedReader.
- 行为差异: Function A returns a single line; Function B processes the entire response.；Function B has side effects (populates a list and updates UI); Function A has none.；Function B adds a User-Agent header and handles URL encoding; Function A does not.；Function A is generic; Function B is specific to Google Images.
- 修正建议: Incorporate function signature and return type into the model.；Use dataflow or graph-based representations to distinguish control flow patterns beyond boilerplate.；Train on negative examples with high API similarity but different semantics.

### case_id=2050 FP boilerplate_overlap

- 方法: `writeFileType` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads URIs from a file, fetches each document, checks for RDF/OWL keywords in first 100 lines, writes type classification to output file.
- B 摘要: Searches Google Images, parses image URLs from HTML response, adds to list, displays first image in a GUI.
- 静态失败原因: Overlap in common Java I/O and networking boilerplate (URL, BufferedReader, try-catch) likely caused the model to mistakenly infer similarity.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels non-clones when functions have completely different purposes, even if sharing some API usage patterns.
- 共享行为: Both use URL and URLConnection to fetch web resources；Both read from BufferedReader；Both handle exceptions with try-catch
- 行为差异: writeFileType classifies documents by content type; googleImageSearch retrieves image URLs；writeFileType reads multiple URIs from a file and writes results; googleImageSearch processes a single search query and updates GUI；writeFileType only reads first 100 lines; googleImageSearch reads entire response；writeFileType outputs to file; googleImageSearch manipulates GUI components
- 修正建议: Add structure-aware features that capture high-level control flow and data dependencies；Train to distinguish boilerplate patterns from core functionality

### case_id=2051 FN partial_functionality

- 方法: `doGet` vs `dump`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Handles HTTP GET requests to render a portal page based on a request parameter, including page lookup, visibility checks, logging, and caching to files for non-editable pages.
- B 摘要: Copies the contents of a source file to a target file using buffered I/O streams, returning true on success and false on failure.
- 静态失败原因: The static model likely focused on lexical and structural similarity, which is extremely low (token Jaccard 0.0697), and correctly identified them as non-clones; the model did not err but rather BCB may have applied a lenient clone definition.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider these as Type-4 clones due to shared high-level I/O operations and exception handling, overlooking the vast difference in application context and complexity.
- 共享行为: Both perform I/O operations that may throw IOException.；Both write output (one to HTTP response, one to a file).
- 行为差异: Function A is an HTTP servlet handler with complex logic including page management and user permissions; function B is a simple file copy utility.；Function A does not return a value but sends error codes; function B returns a boolean.；Function A reads from HTTP request parameters and portal context; function B reads from a file.；Function A has extensive error recovery and caching; function B has minimal error handling.
- 修正建议: Consider removing such pairs from the benchmark if they are not semantically equivalent.；For models, incorporate high-level functional information (e.g., API calls) to better align with BCB preferences.

### case_id=2052 FP boilerplate_overlap

- 方法: `downloadURLtoString` vs `run`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Downloads the content of a given URL and returns it as a string.
- B 摘要: Fetches a tile from a data source, reads its content, parses it into vector tile geometries, and adds it to a data loader while managing concurrent requests.
- 静态失败原因: The static BERT model likely overemphasized the lexical overlap in the BufferedReader reading loop, which is a common pattern, and failed to capture the vast differences in the rest of the functions. It may have been misled by the token-level similarity of the while loop without understanding the broader semantics.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the shared read-loop is a common boilerplate pattern, and the functions have different overall purposes and contexts (different method names, classes, and projects). The similarity is too incidental for a clone under BCB guidelines.
- 共享行为: Both read lines from an input stream using BufferedReader and concatenate them into a string.
- 行为差异: A simply returns the downloaded string; B performs complex tile processing and caching.；B manages a set of launched requests to avoid duplicate downloads.；B handles file and HTTP protocols separately.；B parses the downloaded content into geometric objects and stores them.
- 修正建议: Incorporate method-level context such as method name, class, and surrounding code.；Use graph-based representations that capture control flow and data flow differences.；Train with negative samples that have similar boilerplate but different semantics.；Leverage contrastive learning to distinguish fine-grained functional differences.

### case_id=2053 FN benchmark_preference_bias

- 方法: `modifyApplicationMessage` vs `patch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Modifies a locale-specific properties file by setting a given message key to a new value, creating the file from the English version if missing.
- B 摘要: Copies the Minecraft jar file to a backup location if there are pending modifications, then prepares to patch the jar.
- 静态失败原因: The static model predicted non-clone because token overlap is extremely low (0.0526) and control flow differs significantly; BCB's annotation likely relies on broader functional goals rather than concrete behavioral similarity.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might label this as clone due to both functions involving file modification operations (read/write), and possibly because both are part of a larger framework that deals with configuration or resources. However, the actual semantics are entirely different.
- 共享行为: Both perform file I/O operations.
- 行为差异: Function A manipulates key-value pairs in properties files for internationalization, while function B deals with patching a Minecraft jar file.；Function A creates or updates a properties file; function B copies a jar file and opens it for modification.；Function A has complex logic for reading line by line and modifying specific entries; function B is a stub that only copies and opens.
- 修正建议: Re-evaluate BCB annotation manually for this pair; suggest removing from clone set.

### case_id=2054 FN library_context_missing

- 方法: `getHTML` vs `getContent`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `context_recovery_then_expert`；动态可解性: `low`；执行优先级: `medium`
- A 摘要: Fetches HTML content from a given URL using HttpURLConnection, optionally writes it to a file, and returns the content as a string.
- B 摘要: Fetches content from an HTTP request using Apache HttpClient and returns it as a string.
- 静态失败原因: The model likely focused on lexical and syntactic differences (different method names, different HTTP client usage, different parameters) and did not capture the underlying semantic equivalence of fetching and returning HTTP content as a string. The low token Jaccard similarity (0.2125) indicates little lexical overlap, which may cause the model to miss the clone relation.
- 静态 case study: 该类错误缺少关键上下文或需要深层语义，纯静态方法不可靠。
- 动态 case study: 动态执行价值较低：样本可能依赖库、框架、网络、GUI、数据库或项目上下文，需要先恢复环境或 mock 依赖。
- BCB 偏好解释: BCB often labels pairs performing the same high-level operation (e.g., HTTP fetch returning string) as Type-4 clones, even if the exact API and parameters differ, as long as the core logic is similar.
- 共享行为: Both read HTTP response line by line and append to a buffer；Both return the full content as a string；Both handle exceptions (though differently)
- 行为差异: Function A uses java.net.HttpURLConnection, while Function B uses Apache HttpClient；Function A optionally writes content to a file, Function B does not；Function A specifies encoding and User-Agent; Function B sets timeouts；Function A appends carriage return and newline, Function B appends only newline
- 修正建议: Improve training data with more diverse API usages for common operations；Add data flow analysis to track that both functions read from HTTP and return the content；Incorporate external knowledge about library equivalence

### case_id=2055 FN benchmark_preference_bias

- 方法: `getFile` vs `compress`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies its endpoint attribute, and saves it to a temporary directory.
- B 摘要: Concatenates multiple input files into one output file and optionally compresses it using an external tool.
- 静态失败原因: The static BERT model correctly predicted non-clone due to very low token overlap (Jaccard = 0.1046) and distinct APIs; it did not fall for superficial I/O patterns.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have considered both as 'Type-4' (semantic similarity) due to both being utility methods that manipulate files with streams and logging, despite completely different purposes.
- 共享行为: Both perform file I/O operations using streams.；Both include logging statements.
- 行为差异: Function A downloads and modifies an XML file; Function B concatenates and optionally compresses files.；Function A returns a file path; Function B is void and writes to a PrintWriter log.；Function A handles multiple specific exceptions; Function B throws a generic Exception.；Function A uses NIO channels and URL connections; Function B uses standard byte buffers and a ProcessBuilder.
- 修正建议: Review BCB annotation: functional dissimilarity suggests mislabel.；Use more discriminative features like method name, parameter types, and core purpose.；Incorporate control-flow and data-flow analysis to better capture semantics.

### case_id=2056 FN partial_functionality

- 方法: `getFile` vs `copyParseFileToCodeFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies its endpoint, and saves it to a temporary directory.
- B 摘要: Copies content from one file to another using a fixed buffer size.
- 静态失败原因: Static BERT correctly identified the low lexical and structural similarity (token Jaccard=0.102), leading to a non-clone prediction, which aligns with a strict semantic analysis but contradicts the BCB label.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled this as a clone due to both functions involving file I/O operations (input/output streams), but the annotation is likely erroneous as their overall behavior and purpose are fundamentally different.
- 共享行为: Both perform file I/O operations involving reading from an input source and writing to an output file.
- 行为差异: Function A includes network download, XML parsing, and endpoint modification, while B is a simple file copy.；Function A is significantly more complex with error handling and conditional logic, whereas B is straightforward.；Function A returns a file location string; B returns void.
- 修正建议: Improve BCB annotation guidelines to avoid overgeneralizing file I/O as a clone indicator.；Use more fine-grained clone types that distinguish between simple file copy and complex processing.

### case_id=2057 FN partial_functionality

- 方法: `readData` vs `readURL`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Reads comma-separated input strings into sets and reads a file to populate several data structures.
- B 摘要: Reads lines from a URL and prints them to console.
- 静态失败原因: Static BERT models rely on token overlap and structural similarity; the low token Jaccard (0.084) and very different method signatures, parameter types, and internal operations lead to a low similarity score, causing the model to miss the broad functional commonality that BCB might recognize.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB might consider these as clones due to a common pattern of reading line-by-line from an external source, disregarding the different specifics of data processing and output.
- 共享行为: Both read line-oriented input using BufferedReader；Both use a while loop to process lines
- 行为差异: A reads from static string fields and a file; B reads from a URL parameter；A populates internal maps and sets; B prints to console；A performs complex parsing and conditional logic; B has no processing；A uses StringTokenizer; B does not
- 修正建议: Enhance model with data flow analysis to capture I/O patterns；Include abstract representation of reading and processing loops；Use contrastive learning to identify partial clones with low lexical overlap

### case_id=2058 FN benchmark_preference_bias

- 方法: `readAndRewrite` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.6`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Reads a DICOM image file, parses the dataset, and writes it to another file using pixel data reading and writing.
- B 摘要: Configures and launches a NexOpen project by processing Maven pom.xml files, setting Hibernate dialect, and performing reverse engineering if needed.
- 静态失败原因: The static model relied heavily on token overlap and structural similarity, both of which are very low (Jaccard=0.03). It missed the high-level file I/O pattern that BCB annotators might have considered clone-worthy.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled these as clones based on a very broad Type-4 interpretation where both functions involve reading from one file and writing to another, despite completely different contexts and logic.
- 共享行为: Both perform file I/O operations (reading and writing files).
- 行为差异: Different domains: DICOM medical imaging vs. Eclipse project configuration.；Completely different APIs and libraries used.；readAndRewrite is a simple file copy with parsing; launch involves project validation, property setting, and external tool invocation.
- 修正建议: Incorporate higher-level task semantics or API usage patterns.；Consider using a more robust representation that captures abstract functionality beyond token sequences.

### case_id=2059 FP lexical_or_api_overlap

- 方法: `lookupFutureEvents` vs `checkForUpgrade`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches future events from Meetup API and parses JSON into Event objects.
- B 摘要: Checks for software upgrades by querying a remote server and managing installation records.
- 静态失败原因: The model likely focused on token overlap (URL, BufferedReader, while-loop) and structural similarities, ignoring the distinct domain and purpose of each function.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB considers high-level functionality: one is a calendar event fetcher, the other is a software updater; despite similar I/O patterns, they are semantically unrelated.
- 共享行为: Both open an HTTP connection and read response line by line；Both parse a structured format (JSON vs custom field-separated data)；Both iterate over a list of parsed items to extract fields
- 行为差异: A queries Meetup API for events; B queries a license/upgrade server；A constructs Event objects; B updates a database table and UI components；A handles date parsing and time zone; B handles license validation and UI visibility
- 修正建议: Incorporate data flow analysis to distinguish different object types and method calls；Use contrastive learning with functional labels；Add task-specific features like API endpoint names or database operations

### case_id=2060 FP lexical_or_api_overlap

- 方法: `main` vs `streamContains`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Main method that parses a Prolog file and generates adapter code into a JAR file.
- B 摘要: Private test helper that checks if a string is contained in an input stream.
- 静态失败原因: Static BERT models may have been misled by common Java API tokens (e.g., String, IOException, File) and the presence of try-catch blocks, causing a false positive despite low token Jaccard similarity.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels non-clone because the functions have completely different purposes and levels of complexity, with no functional overlap.
- 行为差异: Function A is a complex main method with multiple steps; Function B is a simple assertion utility.；Function A writes to a JAR file; Function B reads from a stream and tests a condition.；Function A handles command-line arguments and debug options; Function B has no such logic.
- 修正建议: Improve model sensitivity to overall program structure and high-level semantics.；Incorporate data-flow analysis to distinguish between different operations on similar types.；Use contrastive learning to penalize false positives with low functional similarity.

### case_id=2061 FN partial_functionality

- 方法: `sendExceptionToServer` vs `fileDownload`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends exception details to a remote server via HTTP POST and checks for success response.
- B 摘要: Downloads a file from a remote URL and saves it to a local directory.
- 静态失败原因: Static models like BERT rely on token-level overlap and syntactic similarity. The code tokens differ significantly (different method names, variable names, string literals), and the Jaccard similarity is low (0.2). The model failed to recognize the higher-level structural similarity of network communication patterns.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considers these clones because both are network I/O functions that follow a similar pattern: open a URL connection, handle streams, catch exceptions, and interact with remote servers. The overarching functionality of remote communication is shared even if the specific data transfer direction and content differ.
- 共享行为: Both use URLConnection to communicate with a remote server；Both handle I/O exceptions；Both involve opening a URL and processing streams
- 行为差异: A sends data (POST) while B receives data (download)；A builds a query string with multiple parameters, B does not；A reads response and prints messages, B writes to file；A uses OutputStreamWriter, B uses BufferedReader and FileOutputStream
- 修正建议: Enhance models with graph-based representations to capture structural patterns like URL connections and stream handling；Use dataflow analysis to highlight common operations (open, read/write, close)；Incorporate domain knowledge about common network I/O patterns

### case_id=2062 FP lexical_or_api_overlap

- 方法: `createHTML` vs `getRequestContent`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Builds an HTML page by reading a CSS resource and appending content based on page type, optionally querying a database.
- B 摘要: Fetches and returns the first line of content from a given URL via HTTP.
- 静态失败原因: The model likely overemphasized the lexical and API overlap (URL, BufferedReader, readLine) and the sequential line-reading loop, ignoring the higher-level semantic difference in the end-to-end functionality. It may also have been misled by the similar exception handling structure.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically requires significant functional overlap or shared data flow. While both involve reading stream data, the overall purposes (HTML generation vs. HTTP fetching) are too distinct, and the common I/O pattern is too shallow to be considered a Type-3/4 clone.
- 共享行为: Both use URL, InputStreamReader, and BufferedReader to read data from a stream.；Both read lines sequentially using readLine().；Both involve I/O operations and handle resources.
- 行为差异: A builds a complete HTML string; B returns a single line from HTTP response.；A reads from a local classpath resource and optionally queries a database; B sends HTTP request to a remote URL.；A has complex logic for different page types; B has simple linear flow.；A has detailed exception handling with logging; B throws Exception generically.
- 修正建议: Incorporate data-flow analysis to track how the read content is used.；Add method-level context such as surrounding code or callers.；Use contrastive learning that penalizes pairs with different high-level goals despite similar API usage.；Improve representation of long-range dependencies to capture the full function logic.

### case_id=2063 FN partial_functionality

- 方法: `GetResponse` vs `seeURLConnection`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Opens an HTTP GET connection to a given URL, reads response lines if HTTP_OK, and returns the concatenated content as a string, returning null on failure.
- B 摘要: Opens a URL connection to a hardcoded URL, reads all lines from the input stream, concatenates them, logs the result, and returns void, propagating exceptions.
- 静态失败原因: Low token Jaccard (0.24) means little lexical overlap. The model likely missed the conceptual commonality because variable names, control flow (if-else vs while), and error handling differ. Static models struggle when shared behavior is not reflected in surface tokens.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often annotates as clone pairs that share core functionality despite differences in method signature, error handling, or return type, especially when the data flow (reading URL content) is similar.
- 共享行为: Both open a URL connection；Both read input stream line by line using BufferedReader；Both concatenate the lines into a single string
- 行为差异: Function A takes a URL parameter, function B uses a hardcoded URL；Function A checks HTTP response code, function B does not；Function A returns content string, function B logs and returns void；Error handling differs: A catches exceptions silently, B throws Exception
- 修正建议: Augment training with functional abstractions that ignore method signature and error handling；Use dataflow analysis to identify common I/O patterns (open stream, read lines, close)；Incorporate knowledge of Java standard library usage (URLConnection, BufferedReader)

### case_id=2064 FN partial_functionality

- 方法: `getPagina` vs `invoke`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches the content of a URL as a string via HTTP GET.
- B 摘要: Invokes a remote method via HTTP POST, sending JSON arguments and returning deserialized result, with retry logic.
- 静态失败原因: Static models like BERT or GraphCodeBERT may overly rely on lexical overlap (e.g., URL, BufferedReader, InputStream) and common boilerplate code, missing the larger semantic differences in method signature, HTTP method, request construction, and response handling. The retry and serialization logic in B is distinctive but not captured by static embeddings.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have considered both as HTTP request-response reading functions, but the overall functionality and intent differ significantly. The shared pattern of reading an HTTP response is generic, but the methods serve different purposes and have different interfaces.
- 共享行为: Both perform HTTP requests and read the response line by line using BufferedReader.
- 行为差异: HTTP method: GET vs POST；Request construction: static URL vs dynamic URL with service and method；Response handling: raw string concatenation vs JSON deserialization to specific type；Error handling: simple exception string return vs retry with service discovery
- 修正建议: Incorporate method signature and type information.；Use data flow analysis to trace input/output transformations.；Train on more diverse examples with clear functional boundaries.；Consider control flow and exception handling patterns.

### case_id=2065 FP partial_functionality

- 方法: `readTwitterFead` vs `getXML`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a hardcoded Twitter feed URL using HttpClient, checks status code, and returns the response as a string.
- B 摘要: Reads a configurable URL using URL.openStream() and returns the response as a string, or null on error.
- 静态失败原因: Static BERT may have been misled by the overall structural similarity (try-catch, read loop, string building) and the common pattern of fetching HTTP content, while overlooking the critical differences in API usage, error handling, and parameterization.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely considers these non-clones because the methods differ in input parameters, HTTP client API, error handling, and return behavior on failure, which amount to a significant difference in functionality.
- 共享行为: Both perform HTTP GET requests and read the response line by line into a string buffer.；Both return the accumulated string.
- 行为差异: A uses a hardcoded URL; B takes URL and request as parameters.；A uses Apache HttpClient; B uses Java URL.openStream().；A checks HTTP status code (200); B does not.；A returns empty string on non-200; B returns null on exceptions.
- 修正建议: Train with more negative examples that share similar control flow but differ in API or error handling.；Incorporate data flow analysis to distinguish hardcoded vs parameterized inputs.；Use contrastive learning to emphasize functional differences over syntactic similarities.

### case_id=2066 FN partial_functionality

- 方法: `copyFile` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a file from source to destination, optionally overwriting, using a buffer.
- B 摘要: Retrieves a resource via URL, caches it locally, and returns an InputStream, with fallback to existing cache.
- 静态失败原因: Static BERT/GraphCodeBERT likely focused on token overlap and structural similarity; low Jaccard similarity (0.18) and different API calls caused it to miss the underlying common I/O copy pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both Type-3/Type-4 clones because they share the core I/O copy loop pattern, even though the overall functionality differs.
- 共享行为: Both read from an input stream and write to an output stream in a loop.；Both use byte buffers for copying data.；Both close streams in finally blocks.
- 行为差异: Function A copies directly from FileInputStream to FileOutputStream; Function B handles URL connections, caching, and returns an InputStream.；Function A has explicit force overwrite logic; Function B checks cache validity and HTTP responses.；Function B uses System.out.println for debugging; Function A uses logging.
- 修正建议: Improve representation of control flow data dependencies across long ranges.；Incorporate I/O operation abstractions.；Use graph-based models that capture data flow between input and output streams.

### case_id=2067 FP boilerplate_overlap

- 方法: `execute` vs `perform`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Unlocks an encrypted quiz bank by prompting for a password and verifying its MD5 digest.
- B 摘要: Handles a web form submission for classifying a concept by sending data to a remote server and parsing the result.
- 静态失败原因: The static BERT model likely overemphasized common boilerplate patterns (try-catch, null checks, session attribute retrieval) and ignored the radical difference in functionality and context, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the two functions have completely different domains (Eclipse RCP vs. Struts), different data sources (local folder vs. remote server), and no shared functional behavior beyond generic method structure.
- 共享行为: Both are command-like methods executing in response to a user action；Both use try-catch blocks for exception handling
- 行为差异: Code_a operates on a local Eclipse RCP view with a password dialog; Code_b handles HTTP requests in a Struts web application；Code_a checks folder encryption and unlocks it; Code_b processes form parameters and invokes a remote classification service；Code_a uses MD5 hashing; Code_b uses URL connections and XML parsing
- 修正建议: Increase representation of domain-specific APIs in training；Incorporate data flow analysis to distinguish local vs. remote operations；Use contrastive learning to separate methods with different intents

### case_id=2068 FN benchmark_preference_bias

- 方法: `modifyApplicationMessage` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Modifies a properties file for a given locale by updating an existing key or appending a new key-value pair.
- B 摘要: Writes library license information and metadata from jar files' .meta and .extra files into a text file.
- 静态失败原因: Static BERT correctly predicted non-clone based on low token overlap and different method names/contexts; the 'error' arises from BCB's broader clone definition, not from a model flaw.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled them as clones due to both being file-processing functions with similar structural patterns (open file, read, process, write), despite different domains, which fits a broad Type-3/Type-4 interpretation in BigCloneBench.
- 共享行为: Both perform file I/O operations；Both use String building (StringBuilder, String concatenation)；Both handle exceptions with try-catch or throws；Both write to a file using FileWriter/FileOutputStream
- 行为差异: A modifies an existing properties file; B creates a new output file from scratch；A uses locale-specific file copying; B enumerates files in a directory；A deals with .properties format; B deals with custom .meta/.extra file formats；A has logic for missing key; B has no such concept
- 修正建议: Use a stricter clone definition focusing on semantic equivalence rather than structural similarity；Incorporate domain-specific features to differentiate file-processing tasks；Re-evaluate BCB labels for such pairs to ensure consistency

### case_id=2069 FP lexical_or_api_overlap

- 方法: `lookupFutureEvents` vs `downloadModel`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches and parses Meetup events JSON from a URL.
- B 摘要: Downloads an RDF model from a URL.
- 静态失败原因: Overlap in common API calls (URL, InputStream) and sequential I/O pattern misled the model into seeing partial similarity.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely considers these non-clones because the high-level purpose (events vs. model) and output types differ significantly, despite both performing network I/O.
- 共享行为: Both open a URL connection and read input stream.；Both handle IOExceptions by throwing exceptions.
- 行为差异: A parses JSON into Event objects; B reads RDF data into a Model.；A processes a list of events with date formatting; B only reads a single model.；A implements complex error handling and data extraction; B is simpler.
- 修正建议: Use dataflow analysis to trace how input is transformed and output is used.；Incorporate program dependence graphs to capture semantic intent.；Include type information of return values.

### case_id=2070 FP lexical_or_api_overlap

- 方法: `getRequestContent` vs `checkForUpgrade`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Gets the first line from a URL by opening an HTTP connection and returning the line as a string.
- B 摘要: Checks for software upgrades by querying a remote server, parsing license information, updating database records, and showing UI messages.
- 静态失败原因: Static BERT models may overemphasize lexical overlap from common API tokens like 'URL', 'openConnection', 'BufferedReader', 'InputStreamReader', and 'readLine', while missing the structural and semantic differences in control flow, data processing, and side effects.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would likely label this non-clone because the functions have completely different purposes despite sharing a trivial boilerplate pattern of opening a URL and reading. The shared pattern is a common idiom and not indicative of semantic cloning.
- 共享行为: Both open a URL connection and read text from the input stream using BufferedReader.
- 行为差异: Function A returns the first line read; Function B reads all lines and processes them into a combined string.；Function A has no side effects; Function B performs database operations and UI updates.；Function A is simple and single-purpose; Function B is complex and involves multiple steps including license validation and upgrade installation.
- 修正建议: Incorporate method-level semantic embeddings that capture the overall purpose and data flow.；Use graph-based models that consider control and data dependencies to differentiate simple reading from complex processing.；Integrate method name similarity or topic modeling to disambiguate functions with different objectives.

### case_id=2071 FN partial_functionality

- 方法: `getResourceAsStream` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.95`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Retrieves a resource as an InputStream, possibly from a local cache or by downloading from a URL, with caching logic.
- B 摘要: Copies a source file to a destination file using a buffer.
- 静态失败原因: Low token overlap (0.16) and significant differences in control flow, API usage, and method signatures caused the model to miss the underlying stream copy commonality.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often considers functions that share a core algorithmic pattern (stream copy) as clones, even if one has additional complexity, aligning with Type-3/Type-4 broad similarity.
- 共享行为: Both read from an input stream and write to an output stream using a loop；Both manage resources with try-catch and close streams
- 行为差异: A involves URL connection, caching, and conditional logic; B is a simple file copy；A returns an InputStream; B is void and throws IOException；A is synchronized and has extensive error handling; B has simpler exception handling
- 修正建议: Use a dataflow-aware model like GraphCodeBERT to capture the common I/O loop structure；Add training examples of partial clones with varying complexity；Incorporate structural similarity metrics like AST or CFG matching

### case_id=2072 FP lexical_or_api_overlap

- 方法: `getPagina` vs `getFullScreenUrl`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Downloads entire web page content as a string from a given URL.
- B 摘要: Parses a YouTube page to extract video parameters and constructs a download URL.
- 静态失败原因: High API overlap (URL, BufferedReader, InputStreamReader) led to a false positive; the model likely overemphasized the common code pattern of reading from a URL without recognizing the different control flow and output construction.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would not consider these clones because the core functionality is entirely different: one is a generic web page fetcher, the other is a specialized YouTube URL extractor.
- 共享行为: Both open a URL connection and read lines from the input stream；Both catch IOException and general Exception
- 行为差异: Function A reads all lines and concatenates; Function B only reads until finding a specific line and then extracts substrings；Function A returns raw page content; Function B returns a constructed URL；Function A uses an Authenticator; Function B sets progress bars and prints debug output；Function A takes a URL argument; Function B uses a class variable
- 修正建议: Incorporate dataflow analysis to track output construction and distinguish between raw content and derived values；Use control flow graph differences to detect that one loops over all lines while the other breaks early；Add features capturing the method's return type and purpose

### case_id=2073 FP boilerplate_overlap

- 方法: `run` vs `downloadModel`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads lines from a URL, parses first two lines as version and url, accumulates rest, handles errors, and notifies listeners.
- B 摘要: Downloads an RDF model from a URL with HTTP headers, handles errors by logging and rethrowing as RuntimeException.
- 静态失败原因: The model may have focused on common boilerplate (try-catch with URL, IOException) and missed the distinct data handling and purpose.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled non-clone due to entirely different functionality: one is a generic text-line reader, the other is a specific RDF model downloader.
- 共享行为: Open a URL connection；Read from the connection；Catch IOException
- 行为差异: Parsing: A reads text lines, B reads RDF model；Error handling: A sets flags, B logs and rethrows；Output: A updates fields and notifies, B returns a Model；Method type: A instance, B static
- 修正建议: Improve training to differentiate detailed logic inside try blocks；Use data flow or type information to distinguish data transformations；Add more negative examples with similar API usage but different semantics

### case_id=2074 FP boilerplate_overlap

- 方法: `getLinksFromURLFast` vs `loadURL`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Parses HTML from a URL to extract links and anchor texts.
- B 摘要: Loads content from a URL with optional HTTP authentication and writes it to a temporary file with progress display.
- 静态失败原因: The static model may have been fooled by the shared boilerplate of opening a URL connection and reading lines, plus similar method signatures (both take URL strings/URLs and throw IOException). The token Jaccard is low (0.17) but the structure might still overlap enough for a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB prefers functional similarity; these two have different output and purpose, so likely labeled 0.
- 共享行为: Open URL connection；Read lines from input stream；Use BufferedReader and InputStreamReader
- 行为差异: A extracts links from HTML using regex; B writes entire response to a file；B supports HTTP Basic authentication; A does not；B updates a status label and manages temporary file; A returns parsed data as Vectors；A uses GNU regexp library; B uses standard Java
- 修正建议: Improve training to distinguish when shared code is just boilerplate vs core functionality；Add contrastive examples of similar-looking but functionally different pairs；Incorporate data flow analysis to detect differing post-processing steps

### case_id=2075 FN partial_functionality

- 方法: `readData` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Reads data from multiple string fields and a file to initialize various sets and maps for Tibetan transliteration.
- B 摘要: Reads content from a URL and prints each line to standard output.
- 静态失败原因: Low token overlap and different APIs; static model likely focuses on lexical/structural patterns, missing high-level semantic analogy.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as 'data reading' functions that iterate over input lines, thus broad Type-4 clone.
- 共享行为: Both read input line by line
- 行为差异: Function A reads from internal strings and a file, while B reads from a URL；A populates a complex data structure, B only prints；A includes tokenization and error handling, B has none
- 修正建议: Include program analysis to recognize common I/O loops；Use data flow analysis to capture line-by-line reading pattern

### case_id=2076 FN partial_functionality

- 方法: `sendExceptionToServer` vs `doRawRequest`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Builds URL-encoded exception details and sends them to a server via HTTP POST, then reads the response and prints success or failure.
- B 摘要: Sends arbitrary postData via HTTP POST and returns the response as a string.
- 静态失败原因: Static models may focus on token-level or AST-level similarity; the low Jaccard similarity (0.3068) and different method names/signatures mislead them. They may not capture the shared sub-pattern due to the surrounding differences.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels as clones pairs that share a significant common sub-pattern (Type-3/Type-4), even if one function adds extra logic. Here, the core HTTP POST logic is nearly identical, so BCB likely considers them clones.
- 共享行为: Both open an HTTP connection, set doOutput=true, write data to the output stream, read the response via BufferedReader, and close streams.
- 行为差异: Function A internally builds the post data from exception and system info, while B receives postData as a parameter.；Function A does additional URL encoding and conditional appending of optional fields.；Function A prints to console based on the response, while B returns the response string.；Function A catches IOException and prints an error, while B throws IOException.
- 修正建议: Use clone detectors that handle partial functionality (e.g., subgraph matching).；Incorporate data-flow analysis to identify common sub-patterns.；Train models with more examples of partial clones or use contrastive learning.

### case_id=2077 FN partial_functionality

- 方法: `doVersionCheck` vs `seeURLConnection`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a version check URL to retrieve development and stable build versions.
- B 摘要: Reads content from a hardcoded URL and logs the entire response.
- 静态失败原因: Static BERT models rely heavily on lexical and token overlap; the low Jaccard similarity (0.21) and different method names/body structure caused the model to miss the shared underlying I/O pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considers both as clones because they perform the core pattern of reading from a URL line by line, and the differences (UI, specific parsing) are considered secondary for partial similarity.
- 共享行为: Both create a URL and open an input stream；Both read lines using BufferedReader；Both close the reader after reading
- 行为差异: A includes UI wait cursor and error dialog, B does not；A reads specific lines with prefixes, B reads all lines；A calls another method for version check, B logs output；A uses property-based URL, B uses hardcoded URL
- 修正建议: Enhance models with dataflow or structural information；Use contrastive learning to recognize common I/O patterns；Include program slicing to isolate core subfunctions

### case_id=2078 FN partial_functionality

- 方法: `getFile` vs `testCopy_readerToWriter_nullIn`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Downloads a WSDL file from a URL, optionally modifies the endpoint XML, and returns the file location.
- B 摘要: Tests that IOUtils.copy throws NullPointerException when given a null Reader.
- 静态失败原因: The static model likely relied on lexical or syntactic similarity, which is low here, and failed to capture the broad I/O-themed similarity that BCB might have considered.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled this as a clone based on a broad I/O utility category, considering both functions deal with streams or writers, or due to partial functionality overlap in handling I/O resources.
- 共享行为: Both involve I/O operations (streams/writers) and exception handling.
- 行为差异: A performs actual file download and XML modification; B is a null-check test expecting an exception.；A has complex control flow with multiple conditions and loops; B is a simple try-catch block.；A returns a String; B has no return value.
- 修正建议: Incorporate broader semantic categories during training to recognize partial functional overlap.；Use data augmentation with pairs that share only high-level operations like I/O handling.

### case_id=2079 FN partial_functionality

- 方法: `modifyApplicationMessage` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Modifies a locale-specific properties file by updating or adding a message key-value pair, and if the locale file does not exist, it first copies the English properties file as a template.
- B 摘要: Copies a file from source to destination using FileChannel.transferTo.
- 静态失败原因: Static BERT/GraphCodeBERT models rely heavily on token-level and syntactic similarity. The token Jaccard is very low (0.06), and the code structures differ significantly. The file copy sub-operation in function A is a small part of the code and may be overlooked by the model. The model likely failed to capture the functional similarity due to low lexical overlap and the dominance of different tokens (property parsing vs. channel transfer).
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider this a clone because both functions involve a file copying operation; function A includes a file copy as a subtask, which is functionally equivalent to function B. BCB's annotation style often accepts partial functionality similarity (Type-4 clones), so even though the overall purposes differ, the shared file copy logic suffices for a clone label.
- 共享行为: Both perform file I/O operations；Both involve reading from a source file and writing to a destination file；In function A, the sub-step of copying the English file to locale file is functionally similar to function B's copy operation
- 行为差异: Function A modifies properties content line by line, while B does a raw binary copy；Function A has error handling and additional logic for parsing properties, while B is straightforward；Function A's main purpose is to update a properties file, whereas B only copies files
- 修正建议: Train models to be aware of sub-task similarity and partial functional equivalence；Incorporate semantic understanding of file I/O operations beyond literal code tokens；Use functional call graph analysis to detect similar sub-operations；Employ data flow analysis to identify identical I/O patterns

### case_id=2080 FP lexical_or_api_overlap

- 方法: `doVersionCheck` vs `downloadModel`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Function A opens a URL to a version check file, reads lines to extract version and build numbers, compares with current build, and shows appropriate UI messages.
- B 摘要: Function B opens a URL connection to download an RDF model, sets HTTP headers, reads the model from the input stream, and returns it or throws an exception.
- 静态失败原因: Static BERT/GraphCodeBERT models often rely on lexical and structural similarity. Here, both functions have high API overlap (URL, InputStream, IOException, try-catch, close) and similar control flow (open stream, read, close, handle exception). The model may be misled by these common patterns and overlook the distinct data processing and return types.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this pair as not clones because the core functionality differs: one is for version checking with UI interaction, the other is for model download with data parsing. The shared URL/IO pattern is generic and not sufficient for clone classification.
- 共享行为: Both open a URL and obtain an InputStream；Both handle IOException with try-catch；Both close the input stream after reading；Both perform some I/O operation on the stream content
- 行为差异: A reads text lines and parses version info; B reads binary RDF/XML into a Model object；A shows UI messages (wait cursor, dialogs); B returns a Model or throws RuntimeException；A uses URL from jEdit properties; B uses URL passed as argument；A sets HTTP request properties for HTTP connections; A does not
- 修正建议: Incorporate data flow analysis to distinguish parsing logic；Use function-level semantic embeddings that capture method names and overall intent；Add attention to return types and final operations；Include program dependency graphs to differentiate similar structures with different semantics

### case_id=2081 FP boilerplate_overlap

- 方法: `getMessageDigest` vs `perform`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Computes a SHA1 message digest over sorted nodes and externals, caching the result.
- B 摘要: Handles an HTTP request to classify a concept by building XML, sending it to a URL, parsing the response, and setting session attributes.
- 静态失败原因: A static BERT/GraphCodeBERT model may have been misled by the presence of similar keywords (e.g., 'digest', 'update', 'nodes') in both functions? Actually B does not have those. More likely the model learned to associate certain boilerplate patterns (like the try-catch with message resources) with clones, or it overestimated similarity based on method length or structure. The low Jaccard suggests token-level similarity is low, so the error might be due to the model's inability to capture long-range semantics and focusing on surface-level features like method signatures or import-like tokens within the code.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clones because the functions have entirely different purposes and no meaningful algorithmic overlap, even though they share generic Java constructs like try-catch and loops.
- 共享行为: Both use try-catch blocks for exception handling；Both contain loops over collections
- 行为差异: Function A computes a cryptographic hash; Function B processes an HTTP request and manages web session state；Function A is short and deterministic; Function B is long and relies on external web resources and session；Function A returns a hex string; Function B returns an ActionForward；Function A has caching; Function B does not
- 修正建议: Improve the model's ability to distinguish between domain-specific logic and generic boilerplate；Add training examples that differentiate cryptographic operations from web request handling；Incorporate more structural features like control flow or data flow graphs to capture actual functional similarity rather than lexical overlap

### case_id=2082 FP lexical_or_api_overlap

- 方法: `sendPost` vs `run`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Sends an HTTP POST request with parameters and returns the response body as a string.
- B 摘要: Fetches a tile (via HTTP or file) as GeoJSON, parses it into geometries, and adds them to a data source.
- 静态失败原因: Static BERT may have over-weighted the lexical overlap of 'URL', 'BufferedReader', 'readLine', and the 'while ((line = in.readLine()) != null)' pattern, missing the larger context of completely different logic (POST vs GET, with parameters, return vs parsing).
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clones because the functions have different high-level purposes: one is a generic HTTP POST utility, the other is a map tile loading and parsing routine. The similarity in reading from a URL is incidental and not enough for Type-3/Type-4.
- 共享行为: Both open a URL and read lines using BufferedReader.；Both handle exceptions (though differently).
- 行为差异: A uses HttpURLConnection with POST; B uses URL.openStream() (GET) or file I/O.；A sends parameters; B does not.；A returns the response string; B processes GeoJSON and populates a data structure.；B has synchronization and tile-specific logic not in A.
- 修正建议: Improve model's ability to distinguish between different HTTP methods and data processing patterns.；Include call graph or data flow information to differentiate side effects.；Add negative examples of functions sharing I/O patterns but different semantics.

### case_id=2083 FP lexical_or_api_overlap

- 方法: `sendPost` vs `getXML`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Sends a POST request with parameters and returns the response body.
- B 摘要: Sends a GET request with a parameter appended to the URL and returns the response body.
- 静态失败原因: Static models rely on token similarity and API overlap; both functions use common classes like URL, BufferedReader, and IOException, leading the model to overlook the semantic difference in HTTP method based on the presence of setDoOutput and PrintWriter.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels as non-clone because the functions implement different HTTP methods (POST vs GET) and parameter handling, which are significant behavioral differences despite both returning a string from a URL.
- 共享行为: Both make an HTTP request to a URL；Both read the response line by line；Both return the response body as a string
- 行为差异: A uses POST method; B uses GET method；A sends parameters in the request body; B appends to URL；A sets request properties; B does not；A is static; B is an instance method
- 修正建议: Incorporate data flow analysis to detect output stream usage；Add more training examples distinguishing HTTP methods；Use method name and parameter types for additional context

### case_id=2084 FP long_range_semantics

- 方法: `actionPerformed` vs `copyJar`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `static_summary_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Handles GUI actions to configure application settings (e.g., file paths, look and feel) and saves preferences.
- B 摘要: Copies a file from source to destination using FileChannel with error logging.
- 静态失败原因: The static BERT model likely misclassified due to the long length of function A, causing it to lose context and focus on superficial similarities like file-related API calls and exception handling patterns, leading to a false positive.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB would label as non-clone because the functions have completely different purposes and no shared functionality: one is a complex event handler for settings, the other is a simple file copy utility.
- 共享行为: Both use Java I/O classes (File, FileChannel, InputStream, OutputStream)；Both include exception handling with logging
- 行为差异: Function A is a long GUI event handler with multiple conditional branches; Function B is a short file copy utility.；Function A updates UI components and saves preferences; Function B performs a single file operation.；Function A interacts with user through dialogs; Function B has no user interaction.
- 修正建议: Improve handling of long methods by truncation or hierarchical embeddings.；Incorporate control flow or data flow features to distinguish different behaviors.；Increase training data with similar non-clone pairs to reduce false positives.

### case_id=2085 FN boilerplate_overlap

- 方法: `fileDownload` vs `createDialogArea`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a file from a given URL to a local directory.
- B 摘要: Creates a dialog area, reads a license file from a plugin resource, and displays it in a browser or text widget.
- 静态失败原因: The model likely focused on the shared structural pattern of URL opening and buffered reading, which is common boilerplate, and ignored the divergent overall functionality.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may have labeled them clones due to superficial similarity in reading from a URL/stream, which is a common boilerplate pattern, but the overall functionality is completely different.
- 共享行为: Both open a URL connection and read from an InputStream using a BufferedReader
- 行为差异: A writes downloaded data to a file; B constructs a UI composite and displays text；A reads character-by-character; B reads line-by-line；A's URL comes from a parameter; B's URL comes from a plugin resource；A does not explicitly close resources in a finally block; B does
- 修正建议: Incorporate higher-level semantic understanding of method purpose (e.g., by analyzing method names and surrounding calls)；Use context from callers or class-level info to distinguish file download from UI creation

### case_id=2086 FP lexical_or_api_overlap

- 方法: `get` vs `read`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Makes an HTTP GET request to a URL, reads the response, decodes lines into GameRecord objects, and returns them as an array.
- B 摘要: Reads a resource file, parses it into sections separated by '---' markers, and adds them to a list; throws exception if section count does not match expected size.
- 静态失败原因: The static BERT model likely over-weighted token overlap (e.g., 'URL', 'BufferedReader', 'readLine', 'line.startsWith') and the shared I/O pattern, while failing to capture the semantic context of the entire function (HTTP request vs resource parsing) and different output types.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically requires functional similarity; these functions have completely different purposes (data retrieval vs file parsing) and outputs, so they are not considered clones even with relaxed Type-3/4. The only commonality is basic I/O boilerplate.
- 共享行为: Both open a URL and read lines using BufferedReader.readLine()；Both skip or process lines based on prefix (# or ---)；Both use try-catch (implicitly in B? Actually B throws Exception)
- 行为差异: A makes an HTTP request and handles response codes; B reads a local resource file；A returns an array of GameRecord; B populates a list of strings and checks size；A ignores lines starting with '#'; B uses lines starting with '---' as section delimiters；A uses custom headers; B does not
- 修正建议: Improve model's ability to distinguish shared boilerplate from core business logic；Add more contextual information or dataflow analysis；Train on more diverse examples of false positives with high API similarity but different semantics

### case_id=2087 FN partial_functionality

- 方法: `getDatasetsList` vs `seeURLConnection`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Retrieves a cached list of dataset names from a server by appending '?server=list' to the given URL.
- B 摘要: Opens a hardcoded URL and reads the entire response content, logging it.
- 静态失败原因: The static model likely focused on significant differences in method signature, control flow, caching logic, and low token overlap, missing the shared core of URL reading.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider the common I/O pattern (URL opening and line reading) sufficient for clone labeling, especially if focusing on functionality reuse or similar code structure despite differing purposes.
- 共享行为: Both open a URL and create a BufferedReader from an InputStream.；Both read lines from the response using readLine() in a loop.
- 行为差异: A uses caching (HashMap) with parameterized URL, while B has no caching and uses a hardcoded URL.；A has error handling with logging and rethrow as RuntimeException, while B throws Exception without handling.；A returns a List<String>, while B returns void and logs the entire response.；A is synchronized, B is not.
- 修正建议: Improve model to recognize shared I/O patterns even when overall purpose differs.；Incorporate dataflow analysis to detect core operations like URL opening and line reading.；Use contrastive learning to better capture partial functionality clones.

### case_id=2088 FP boilerplate_overlap

- 方法: `logging` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Logs inbound message details including encoding, headers, and payload, with optional truncation and error handling.
- B 摘要: Handles UI action events to configure application settings such as file paths, date formats, look-and-feel, and other preferences, with restart prompts.
- 静态失败原因: Static BERT likely relied on superficial lexical and structural overlaps (e.g., many try-catch blocks, if-else, method calls like setText) that are common in Java boilerplate, ignoring domain-specific semantics.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB annotates as non-clone because the functions serve entirely different purposes with no functional overlap; BCB favors Type-3/4 similarity only when significant behavior is shared.
- 共享行为: Both use conditional blocks and exception handling patterns common in Java.
- 行为差异: Function A deals with network message logging; Function B deals with UI configuration and preferences.；Function A throws a Fault on IOException; Function B uses dialogs and logs warnings.；Function A uses CXF interceptor APIs; Function B uses Swing/AWT and custom preference APIs.
- 修正建议: Use dataflow analysis to differentiate I/O operations from UI updates.；Train on more diverse examples to reduce sensitivity to generic patterns.

### case_id=2089 FN benchmark_preference_bias

- 方法: `send` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Sends an email with attachments, headers, and priority using JavaMail.
- B 摘要: Downloads a KMZ file from a URL and extracts its contents to local files.
- 静态失败原因: The static model correctly predicted non-clone because token Jaccard similarity is very low (0.087) and code structures are entirely different; the model did not fail.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may label these as clones due to a very broad interpretation of partial functionality (both involve I/O streams), but this is not typical BCB practice; likely an annotation error.
- 共享行为: Both involve network I/O but at different abstraction levels
- 行为差异: Function A sends email with complex email headers and attachments; Function B downloads and unzips a file；Function A uses JavaMail API; Function B uses URL, ZipInputStream, and FileOutputStream；Function A has many parameters; Function B has none (main method)；Error handling and resource management differ completely
- 修正建议: Re-evaluate BCB annotation for this pair; likely a false positive clone label.；Consider adding more context or filtering out such clearly different pairs

### case_id=2090 FN benchmark_preference_bias

- 方法: `getFile` vs `testReadPerMemberSixSmall`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Downloads a WSDL file from a URL, optionally modifies its endpoint, and returns the file path.
- B 摘要: Tests reading a multi-member GZIP stream by counting bytes copied to null output.
- 静态失败原因: The model correctly predicted non-clone given the low token similarity and distinct APIs; it did not fail—the BCB label is likely a misannotation.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: The BCB label might be erroneous, possibly due to both functions involving I/O stream operations, but the semantic gap is too large for BCB-style clones.
- 行为差异: A performs network I/O and XML manipulation; B performs GZIP decompression.；A writes to a file and returns a path; B writes to a null output and asserts counts.；A uses NIO channels and file streams; B uses GZIPMembersInputStream and IOUtils.copy.；A includes extensive error handling; B throws IOException only.
- 修正建议: Re-examine the BCB ground truth for correctness.；Use dataflow or dependency analysis to confirm lack of semantic equivalence.

### case_id=2091 FN benchmark_preference_bias

- 方法: `main` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.7`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a URL, extracts its ZIP entries, and writes each entry to a local file.
- B 摘要: Copies a file from a source path to a destination directory using NIO FileChannel.
- 静态失败原因: Static BERT/GraphCodeBERT methods rely heavily on lexical and syntactic similarity, which is low (token Jaccard 0.16). They fail to capture high-level semantic similarity like 'copying data', especially when APIs differ significantly (ZipInputStream vs FileChannel).
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB annotators may have considered both as Type-4 clones because they fundamentally perform data transfer from input to output with similar resource management, despite different APIs and specific tasks.
- 共享行为: Both involve file I/O operations: opening input/output streams or channels, reading data, writing data, and closing resources.
- 行为差异: A downloads from HTTP, handles ZIP format, and iterates over multiple entries; B copies a single file using FileChannel.transferFrom.；A uses ZipInputStream and BufferedOutputStream; B uses FileChannel.；A's output destination is determined by entry name; B takes explicit destination path.
- 修正建议: Incorporate program semantics via data-flow analysis to identify read-write operations.；Use coarse-grained function summarization to match higher-level purposes.；Fine-tune on BCB's annotation guidelines to learn broad Type-4 clones.

### case_id=2092 FN partial_functionality

- 方法: `modifyApplicationMessage` vs `loadBinaryStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Modify a message in a locale-specific properties file, creating the file from a template if missing.
- B 摘要: Load a binary stream and copy it to an HTTP response, setting content type and disposition headers.
- 静态失败原因: Static BERT models rely on token sequences and syntactic patterns; the functions have very low token Jaccard and no overlapping key APIs, so the model correctly judged them as non-clones. However, BCB's ground truth labeled them as clones, causing a false negative error relative to that label.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have considered both as 'resource loading/modifying' operations, or perhaps due to a too broad Type-4 category that groups any I/O-related functions without regard to specific functionality.
- 共享行为: Both involve I/O operations (reading/writing streams)
- 行为差异: Method A manipulates properties files for internationalization, while method B serves binary content over HTTP.；Method A reads and writes files on the server, method B writes to an HTTP response output stream.；Method A has complex logic to parse and modify key-value pairs, method B simply copies raw bytes.；Method A catches exceptions and prints stack trace, method B throws IOException and uses Apache Commons IOUtils.
- 修正建议: Improve BCB annotation guidelines to avoid overgeneralizing partial functionality similarity.；Use models that capture high-level semantics or API call sequences to distinguish different I/O patterns.

### case_id=2093 FP boilerplate_overlap

- 方法: `perform` vs `kodetu`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.85`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Processes a web request to classify a concept by sending XML data to a URL and parsing the response.
- B 摘要: Computes the SHA hash of a string and returns the Base64 encoded hash.
- 静态失败原因: The static model likely identified superficial similarities such as exception handling patterns, presence of encoding operations, and generic Java boilerplate, while missing the vast difference in overall functionality.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labeled non-clone because the two functions have completely different purposes and functionality, even under broad Type-4 similarity, as they do not share any meaningful behavioral or structural similarity.
- 共享行为: Both use try-catch blocks for exception handling.；Both involve encoding (URL encoding vs Base64 encoding).；Both are Java methods that take parameters and return a value.
- 行为差异: A handles HTTP session and web requests; B does not.；A parses XML and builds a result; B computes a cryptographic hash.；A is a Struts action method with complex control flow; B is a simple utility function.；A uses multiple external beans and configuration files; B uses only standard Java libraries.
- 修正建议: Incorporate control flow or data flow analysis to distinguish different functionalities.；Use more diverse training data to reduce bias towards common Java patterns.；Apply functional similarity measures that consider the entire behavior rather than token overlap.

### case_id=2094 FN partial_functionality

- 方法: `CheckUrl` vs `seeURLConnection`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads the first line from a given URL's HTTP response and returns it, catching exceptions.
- B 摘要: Reads all lines from a hardcoded URL's HTTP response into a buffer and logs the result, throwing exceptions.
- 静态失败原因: Static models like CodeBERT rely on token overlap and structural patterns. The low Jaccard similarity (0.27) and differences in method signature, control flow (read first vs all lines), error handling, and return type cause the model to miss the shared core behavior of URL reading and line processing.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BigCloneBench often considers pairs with partial functional similarity (Type-3/4) as clones. Both functions perform URL connection and line reading, differing only in input source, output handling, and exception management, which are considered semantic modifications rather than entirely different behaviors.
- 共享行为: Both open an HTTP connection to a URL.；Both use BufferedReader to read from the connection's input stream.；Both read lines of text from the HTTP response.
- 行为差异: Function A takes a URL parameter; Function B uses a hardcoded URL.；Function A returns only the first line; Function B reads all lines.；Function A returns the first line as a String; Function B logs the entire response.；Function A catches and prints exceptions; Function B throws Exception.
- 修正建议: Use data-flow analysis to capture I/O behaviors.；Incorporate control-flow abstraction to generalize line-reading patterns.；Enhance training with more Type-3/Type-4 clone examples.；Consider dynamic or execution-based features for similarity.

### case_id=2095 FP lexical_or_api_overlap

- 方法: `getUser` vs `doVersionCheck`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Loads a User from database or from a configuration file by parsing colon-separated lines.
- B 摘要: Checks for a newer version of jEdit by reading a version file from a URL and comparing build numbers.
- 静态失败原因: Static models like GraphCodeBERT likely focused on the surface-level similarity of reading from a URL and parsing lines, ignoring the distinct domain-specific semantics and control flow (e.g., database operations, version comparison).
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels these as non-clones because they perform entirely different tasks (user management vs. version checking) with no overlap in intended functionality, even though they share common I/O patterns.
- 共享行为: Both open a URL and read lines using BufferedReader and InputStreamReader.；Both handle exceptions with printStackTrace or catch blocks.
- 行为差异: Function A loads a user entity and interacts with a database; Function B does not involve databases.；Function A parses colon-separated fields; Function B parses lines starting with '.version' or '.build'.；Function A saves a new user to database; Function B only displays messages.；Function A returns a User object; Function B is void and uses a View parameter for UI feedback.
- 修正建议: Train with more diverse negative examples that share API calls but differ in purpose.；Incorporate higher-level semantic features like method names, class context, or data flow tracking.

### case_id=2096 FP boilerplate_overlap

- 方法: `main` vs `copy`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Generates adapter classes from a Prolog file and packages them into a JAR.
- B 摘要: Copies a file using NIO mapped byte buffer.
- 静态失败原因: Static BERT/GraphCodeBERT likely relied on token or API overlap (e.g., File, IOException, try-catch), which are common boilerplate, and missed the semantic difference.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labeled non-clone because the functions have vastly different purposes and little code similarity beyond common Java idioms.
- 共享行为: Both involve file I/O operations
- 行为差异: A is a complex multi-step adapter generation tool; B is a simple file copy；A writes to a JAR and uses many external library classes; B copies bytes directly；A parses Prolog and generates Java bytecode; B does not parse or generate code
- 修正建议: Use structural or dataflow analysis to differentiate high-level purpose；Incorporate control-flow and call-graph features；Fine-tune on tasks that penalize superficial API overlap

### case_id=2097 FP boilerplate_overlap

- 方法: `copy` vs `readData`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Recursively copy a file or directory using FileChannel.
- B 摘要: Initialize multiple sets and maps from hardcoded string tokenizations and optionally parse a configuration file.
- 静态失败原因: Static BERT models may rely on superficial lexical cues like 'try-catch', 'IOException', and 'System.out.println', which both functions contain, leading to a false positive prediction despite drastically different semantics.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels non-clones when functions have entirely different purposes and low token overlap, as here.
- 共享行为: Both handle IOExceptions with catch blocks.
- 行为差异: Function A performs file I/O copy; function B initializes data structures from strings and may parse files.；Function A operates on specific source/destination files; function B operates on static class-level fields and internal token sets.
- 修正建议: Enhance model sensitivity to core computational logic vs. boilerplate patterns.；Incorporate data flow or control flow analysis to distinguish different I/O operations.

### case_id=2098 FN benchmark_preference_bias

- 方法: `modifyApplicationMessage` vs `bootKernel`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.7`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Modifies a properties file for a given locale by adding or updating a key-value pair.
- B 摘要: Loads a kernel configuration from an asset file, copies assets to SD card, and boots a kernel.
- 静态失败原因: The model relied on lexical and API token overlap (low Jaccard) and focused on surface-level differences, missing the potential clone label assigned by BCB due to shared configuration-handling theme.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have considered both as configuration management tasks involving Properties and file I/O, despite very different high-level functionality. This is a borderline Type-4 clone based on broad similarity in domain and structure.
- 共享行为: Both use Properties class to handle configuration；Both involve file I/O operations；Both have try-catch exception handling
- 行为差异: A writes to a properties file; B reads an asset and copies files to SD card；A performs text replacement; B loads classes and boots a kernel；A is a standalone method; B is part of an Android activity and finishes on failure；A uses Java file I/O; B uses Android AssetManager and NIO channels
- 修正建议: Incorporate more abstract representations of program behavior；Consider domain-specific configuration handling patterns；Adjust clone detection threshold to allow broader semantic similarity

### case_id=2099 FN partial_functionality

- 方法: `httpRequestByPOST` vs `invoke`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends HTTP POST with form parameters and returns response body as string, setting error codes on failure.
- B 摘要: Sends HTTP POST with JSON payload for method invocation and returns deserialized result, with retry on timeout.
- 静态失败原因: Low token Jaccard similarity (0.276) due to different method names, libraries, and additional logic (retry, deserialization) caused the model to miss the underlying common HTTP POST and response reading pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB labels as positive because both functions implement the core pattern of sending an HTTP POST and reading the response, which is considered a Type-3/4 clone despite differences in error handling and retry logic.
- 共享行为: Both perform HTTP POST requests using HttpClient libraries；Both check HTTP status codes and read response body using BufferedReader；Both handle potential errors in HTTP communication
- 行为差异: Different error handling: A returns null and sets error fields, B throws RuntimeException；Different threshold for success: A uses <400, B uses <300；Retry logic present only in B；Output type differs: String vs Object (deserialized JSON)
- 修正建议: Use data flow analysis to capture the common HTTP request-response flow；Incorporate structure-based matching beyond token overlap

### case_id=2100 FN partial_functionality

- 方法: `doVersionCheck` vs `fileDownload`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Checks for new version of jEdit from a URL by parsing version and build numbers.
- B 摘要: Downloads a file from a URL and saves it to a destination directory as 'download.pdf'.
- 静态失败原因: Static models like GraphCodeBERT may have focused on the structural pattern of opening URL, reading input, and catching exception, ignoring the distinct intent and control flow differences. Also the variable names and method names differ, but the model might have been misled by similar API sequences.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely labeled this as clone due to both methods performing network I/O with URL and BufferedReader, possibly considered Type-3 (functional similarity with limited differences). However, the core functionality is quite different: version checking vs. file downloading.
- 共享行为: Both open a URL and read data from an InputStream using BufferedReader.
- 行为差异: doVersionCheck parses specific lines for version/build info and displays messages; fileDownload writes all read data to a file.；doVersionCheck shows/hides wait cursor; fileDownload does not.；doVersionCheck uses jEdit properties for URL; fileDownload takes URL as parameter.
- 修正建议: Improve model sensitivity to method purpose and output handling.；Use contrastive learning to distinguish between network I/O tasks with different objectives.；Incorporate data flow analysis to track how read data is used.

### case_id=2101 FN benchmark_preference_bias

- 方法: `modifyApplicationMessage` vs `addFileToTarGz`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Modifies a locale-specific properties file by updating or adding a key-value pair for a message.
- B 摘要: Adds a file or directory to a tar.gz archive recursively.
- 静态失败原因: The static BERT model likely correctly identified them as non-clones due to very low token overlap (Jaccard=0.083) and distinct functionality, but BCB's lenient annotation leads to a false negative error.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as a clone due to broad 'file manipulation' category, or mistakenly considered both as resource writing operations.
- 共享行为: Both methods perform file I/O operations using streams and File objects.
- 行为差异: One manipulates properties file content for localization; the other creates tar.gz archives.；Different data formats: properties vs. tar entries.；Different control flow: line-by-line string processing vs. recursive file traversal and archiving.
- 修正建议: Use stricter functional similarity criteria for clone annotation.；Ensure that clones require significant overlap in logic or purpose, not just common I/O patterns.

### case_id=2102 FN partial_functionality

- 方法: `onlyFileCopy` vs `modifyApplicationMessage`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a file using FileChannel transferTo in chunks with exception handling.
- B 摘要: Modifies a properties file for a given locale, copying from English file if missing, parsing lines to find and update a key-value pair, and writing back.
- 静态失败原因: Static BERT/GraphCodeBERT may have focused on the different method names, control flow, and high-level operations (properties manipulation vs. pure copy), missing the shared file copy sub-functionality. The token overlap is low, and the overall structure differs, leading to a non-clone prediction.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considers this a clone because both functions contain a file copy operation as a core or sub-operation. Under broad semantic clone criteria (Type-4), implementing the same functionality (file copy) in different ways qualifies as a clone, despite the additional unrelated functionality in B.
- 共享行为: Both perform file I/O operations；Both involve copying a file from one location to another (A does full file copy, B conditionally copies a reference file)；Both handle exceptions in file operations
- 行为差异: A only copies raw bytes; B reads and writes text properties with key-value logic；A uses NIO FileChannel for efficiency; B uses basic Reader/Writer streams；B has conditional logic for file existence and line parsing; A has no such logic；B writes a modified properties file; A creates an identical copy
- 修正建议: Incorporate structural or control-flow graph matching that can identify shared sub-graphs (e.g., both have a file read-write loop)；Use dataflow to trace the core I/O operations；Augment training with pairs where one function contains the other's functionality as a subset

### case_id=2103 FN partial_functionality

- 方法: `getDatasetsList` vs `runInternal`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Retrieves a list of dataset names from a server URL and caches it.
- B 摘要: Reads an OPDS catalog from a URL, either parsing entries or downloading a book, with pagination and error handling.
- 静态失败原因: Static BERT methods like GraphCodeBERT may overemphasize the similar API usage (e.g., URL, BufferedReader) and miss the large semantic and structural differences in the control flow and overall purpose.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely labeled as clone due to both methods involving URL reading and handling IO, but the overall functionalities are vastly different; this may be a borderline Type-4 if considered 'same goal' of retrieving data from URLs, but the goals differ.
- 共享行为: Both open a URL connection and read input from it.
- 行为差异: A is a simple cache-based list retrieval; B is a complex multi-functional method with catalog parsing, pagination, book download, and callback.；A uses synchronized caching; B uses visited set and progress tracking.；A has simple error logging; B has detailed error handling with user messages and fallbacks.
- 修正建议: Incorporate method-level semantic embeddings that capture overall behavior beyond API sequences.；Use delta-aware or contrastive learning to distinguish similar APIs serving different purposes.

### case_id=2104 FN partial_functionality

- 方法: `getFile` vs `copy`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, optionally modifies the endpoint address in the XML, and saves it to a local temporary file.
- B 摘要: Copies a file from one location to another using NIO FileChannel transfer.
- 静态失败原因: Model relied on lexical/syntactic overlap (low Jaccard 0.15) and surface differences (method names, comments, control flow) but missed the underlying shared channel-based transfer pattern due to lack of deep dataflow understanding.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label these as clones because the core data transfer using NIO channels is functionally similar (copying content from source to sink). The broad Type-4 criterion accepts partial functionality similarity, even when overall tasks differ.
- 共享行为: Both perform file I/O using NIO FileChannel for data transfer.；Both handle IOException and close channels in a finally block.
- 行为差异: A downloads from a network URL and processes XML, while B only copies a local file.；A uses transferFrom from ReadableByteChannel to FileChannel, B uses transferTo between two FileChannels.；A involves temporary files and renaming; B does not.；A has extensive logging and multiple exception types; B only logs IOException.
- 修正建议: Enhance model to recognize functional similarity despite different contexts, e.g., by incorporating data flow or abstract semantics of channel operations.；Add training examples pairing functions that share a sub-computation even if overall purpose differs.；Use graph-based representations that highlight shared subgraphs like NIO channel transfers.

### case_id=2105 FN lexical_or_api_overlap

- 方法: `doBody` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a file from a request and copies its content to the response output stream.
- B 摘要: Downloads a KMZ file from a URL and extracts its zip entries to files.
- 静态失败原因: Low token Jaccard (0.12), different APIs (IOUtils.copy vs ZipInputStream), and structural differences (direct copy vs while loop) caused the model to miss the abstract stream-copy similarity.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB often considers functions that share a high-level I/O pattern (open stream, copy, close) as clones, even with different specifics like source/destination or compression.
- 共享行为: Both open an input stream and an output stream, copy data, flush, and close streams in a finally block.
- 行为差异: A copies entire file to response; B extracts zip entries to separate files.；A uses IOUtils.copy (single bulk copy); B uses a while loop with buffer.；A logs errors; B throws Exception.
- 修正建议: Use graph-based representations capturing data flow and stream operations.；Train on diverse I/O patterns to generalize beyond lexical similarity.；Include type information to recognize abstract stream copy.

### case_id=2106 FN partial_functionality

- 方法: `main` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Reads a zip file of evaluation results, parses rule files, and computes performance metrics, printing them.
- B 摘要: Launches an Eclipse Maven build for a NexOpen project by validating configuration, manipulating pom.xml files, and setting up Hibernate dialect.
- 静态失败原因: Low lexical overlap (Jaccard 0.062) and different domain-specific terms; the model likely did not capture the high-level architectural similarity if any.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have overgeneralized both as 'main-like entry points with file I/O', but they lack sufficient functional overlap.
- 共享行为: Both perform input validation at the start.；Both read and process files based on configuration.；Both involve file I/O and exception handling.
- 行为差异: Code_a processes zip entries and evaluates rule-based models; Code_b handles Eclipse project setup and Maven build.；Code_a is a standalone command-line tool; Code_b is an Eclipse UI launch handler.；Different domains: evaluation vs. project building.
- 修正建议: Enhance training to focus on semantic role of methods rather than lexical overlap.；Use methods like data-flow analysis or AST-based features to capture structural patterns.

### case_id=2107 FN partial_functionality

- 方法: `copyResource` vs `EncodeReturn`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.65`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource (URL or file) to a destination file byte by byte.
- B 摘要: Encrypts data and merges multiple files into a single output file, returning it.
- 静态失败原因: Low token Jaccard (0.08) and different code structures (simple loop vs. NIO channels) caused the model to miss the high-level functional similarity, as static models often rely on surface-level features and fail to capture broad Type-4 clones.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as 'file copying' methods, where the additional steps in B (encryption, merging) are viewed as modifications (Type-3) or partial functional similarity. The annotators likely focused on the common I/O pattern.
- 共享行为: Both read from a source and write to an output file.；Both handle file I/O with streams/channels.
- 行为差异: A is a simple byte copy; B involves encryption, multiple file operations, and uses NIO channels.；B returns a file while A is void.；B uses custom exceptions; A throws generic Exception.
- 修正建议: Use data augmentation with functional transformations to teach models to recognize partial functionality.；Incorporate API call semantics or high-level data flow graphs.；Train on broad clone types like Type-4 with diverse implementations.

### case_id=2108 FN partial_functionality

- 方法: `login` vs `postXml`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Logs into a service by sending a POST request with email and password, extracts session ID from the first line of response.
- B 摘要: Sends an XML POST request with SOAP action headers and returns the full response body.
- 静态失败原因: Static BERT models like GraphCodeBERT rely heavily on token-level overlap and local context. The token Jaccard is low (0.276) due to different variable names and structures. Moreover, the differences in headers, data format, and exception handling may dominate the representation, causing the model to miss the high-level functional similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels Type-4 semantic clones where two functions perform the same abstract operation (HTTP POST) with similar structure, even if specific details differ. The core pattern of opening connection, writing data, reading response is shared.
- 共享行为: Both perform an HTTP POST request using URLConnection；Both set doOutput to true and write data to the output stream；Both read the response using BufferedReader and close resources
- 行为差异: Function A is specific to login with email/password; B is generic XML/SOAP；A uses URL-encoded form data; B uses raw XML；A extracts and returns only session ID; B returns entire response；A handles exceptions by returning empty string; B throws RuntimeException
- 修正建议: Use data-flow or structural features that capture the connection open-write-read pattern；Incorporate contrastive learning on semantic clones with low token overlap；Add explicit representation of HTTP operations and I/O patterns

### case_id=2109 FP boilerplate_overlap

- 方法: `run` vs `handler`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Downloads a tile from a URL, parses it to extract geometries, and adds them to a data source.
- B 摘要: Reads a URL, searches for patterns in each line, and updates a result map with extracted substrings.
- 静态失败原因: The model likely overfitted on common I/O patterns (URL, BufferedReader, exception handling) and ignored the unique core logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically requires functional similarity beyond I/O boilerplate; the core purposes (tile loading vs. text pattern extraction) are unrelated, so non-clone.
- 共享行为: Both open URLs and read lines using BufferedReader；Both catch MalformedURLException and IOException
- 行为差异: Function A processes geometry data and manages a cache; Function B extracts text patterns and updates a map；Function A uses synchronization and state management; Function B has no synchronization；Function A has complex geometry object creation; Function B has simple string manipulation
- 修正建议: Train with more emphasis on the actual data processing logic rather than just I/O structure；Use dataflow analysis to capture transformations on data read from URLs

### case_id=2110 FP boilerplate_overlap

- 方法: `setBundleInfoName` vs `loadURL`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Downloads and parses a key-value file from a URL to update bundle names in a given list.
- B 摘要: Downloads a file from a URL, optionally with authentication, writes it to a temporary file, and updates a status label with file size.
- 静态失败原因: Likely due to overlapping API calls (URL, BufferedReader, readLine) and I/O boilerplate that misled the static model into seeing structural similarity.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB considers core functionality (bundle name update vs file download and UI update) as fundamentally different, thus not clone.
- 共享行为: Open a URL connection and read lines using BufferedReader
- 行为差异: A updates BundleInfo objects in a list; B writes to a temporary file and updates a GUI label.；A returns boolean; B returns void and throws IOException.；B includes optional Basic Authentication and writes content with line-by-line progress.；A parses lines for key-value pairs; B writes entire lines to file.
- 修正建议: Incorporate data-flow analysis to distinguish variable usage patterns.；Use broader context (e.g., surrounding code) to infer actual purpose.；Add training examples that penalize boilerplate-only similarity.

### case_id=2111 FN partial_functionality

- 方法: `main` vs `run`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a ZIP file from a specific URL and extracts its contents to the current directory.
- B 摘要: Copies file content from input to output using Jif-based pumps, with optional diagnostic byte counting.
- 静态失败原因: Static BERT methods rely heavily on token/syntax overlap and short-range patterns; this pair has low token Jaccard and different control flow, so the model missed the high-level functional similarity that BCB may consider.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB might label them as clones because both are stream-based data transfer operations, despite different sources and destinations, possibly considering them Type-4 (functionally similar) due to the input-process-output pattern.
- 共享行为: Both perform file I/O operations using streams；Both involve reading data from a source and writing to a destination
- 行为差异: A extracts a remote ZIP archive; B copies a local file；A writes multiple files (ZIP entries); B writes a single output file；A uses URL and ZipInputStream; B uses Jif framework constructs；B has a diagnostic mode that counts bytes; A does not
- 修正建议: Incorporate data flow or control flow analysis to capture stream processing patterns；Use a model that can abstract away specific APIs and focus on input-output behavior；Train on broader clone definitions including Type-4

### case_id=2112 FP partial_functionality

- 方法: `readData` vs `createTempFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Reads CSV-like strings from fields, parses tokens, and populates multiple sets and maps for Tibetan transliteration data.
- B 摘要: Creates a temporary file by copying a resource stream to a file output stream.
- 静态失败原因: The model likely relied on surface-level similarities such as the presence of IOException, catch blocks, and file-related variable names, despite the different core logic.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB typically labels non-clones for methods with entirely different functionality and low structural similarity; here both methods are unrelated, so non-clone is correct.
- 共享行为: Both involve file I/O exception handling (IOException)
- 行为差异: A parses string tokens and builds data structures; B copies a stream to a file.；A operates on in-memory strings; B performs file I/O.；A has complex conditional logic and error handling for file parsing; B has simple stream copy.；A is private static with no return; B is public void and creates a file.
- 修正建议: Increase negative examples with similar I/O patterns but different semantics.；Incorporate control flow and data dependency analysis to distinguish token parsing from stream copying.

### case_id=2113 FN partial_functionality

- 方法: `readIntoList` vs `httpRequestByPOST`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.5`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads from a URL, parses HTML anchor tags, and creates JMenuItems with action listeners, adding them to a map.
- B 摘要: Performs an HTTP POST request, reads the response line by line, concatenates them, and returns the response string, with error handling.
- 静态失败原因: The model likely focused on low token overlap (19%) and distinct APIs (JMenuItem vs HttpClient), failing to recognize the shared pattern of URL reading as a partial functional similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider these clones under Type-4 semantics because both functions involve reading from a URL line by line, which is a common partial functionality, despite major differences in purpose and processing.
- 共享行为: Both open an InputStream from a URL and read lines using BufferedReader.；Both have try-catch exception handling.；Both process lines in a while loop.
- 行为差异: A parses HTML to extract anchor text and attributes; B does no parsing, just concatenates lines.；A creates GUI components (JMenuItem); B returns a String and sets error codes.；A uses URL.openStream() (GET); B uses HttpClient POST.；A does not return a value; B returns a String or null on failure.
- 修正建议: Enhance model with structural features capturing I/O patterns.；Use data-flow analysis to identify common stream-processing templates.；Incorporate domain knowledge that functions reading from URLs often share clone-like patterns even if high-level purpose differs.

### case_id=2114 FN partial_functionality

- 方法: `testNetworkHTTP` vs `importRoles`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: A test method that makes several hardcoded HTTP GET requests to specific URLs and discards the response, logging the activity.
- B 摘要: A method that reads XML role names from a given URL, parsing the response to produce a list of RoleName objects.
- 静态失败原因: Static BERT models may have focused on syntactic token overlap (Jaccard=0.219) and structural differences (multiple vs single request, different exception handling), causing them to miss the broader functional similarity that BCB annotators considered sufficient for clone status. The model likely treated the differences as too substantial to override the shared pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled this as a clone because both functions perform HTTP GET requests and read response lines, which is a shared high-level behavior. However, the specific purpose and data processing are completely different, so this would be a very broad Type-4 clone at best, but likely an annotation error.
- 共享行为: Both open an HTTP connection using java.net.URL；Both use BufferedReader and InputStreamReader to read the response line by line；Both handle IOException
- 行为差异: Function A makes multiple hardcoded requests with different URL parameters (IMEI, phone, etc.) and discards all data; Function B makes a single request to a dynamically provided URL and parses XML to extract RoleName objects；Function A returns void; Function B returns an ArrayList<RoleName>；Function A logs messages; Function B does not；Function A catches only IOException; Function B catches MalformedURLException, IOException, and ParsingException
- 修正建议: Improve training to recognize broader functional similarities even when syntactic details differ；Use data-flow analysis to identify shared I/O patterns；Incorporate task-level analogies (e.g., both are network operations)

### case_id=2115 FN partial_functionality

- 方法: `modifyApplicationMessage` vs `copyJar`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.2`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Modifies a specific message in a localized properties file by copying the English file if missing, then reading and updating the target key.
- B 摘要: Copies a file from source to destination using NIO FileChannel transferFrom.
- 静态失败原因: Static BERT/GraphCodeBERT correctly predicted non-clone due to low token overlap (0.09) and disparate syntactic structures; from BCB's perspective, it failed to recognize partial functionality similarity in file I/O patterns.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled these as clones due to the shared file copy substep in function A, which is a small part of its overall behavior, broad Type-3/Type-4 tolerance, or a mislabeling in the benchmark.
- 共享行为: Both perform file I/O operations (reading/writing files).；Both handle exceptions and close resources in a finally block.
- 行为差异: A operates on text properties files with locale-specific logic; B performs binary file copy.；A creates a new file if the locale file is missing; B assumes destination can be created.；A uses Reader/Writer and InputStream; B uses FileChannel.；A involves string parsing and replacement; B is a straightforward data transfer.
- 修正建议: Improve detection of partial functional similarity by focusing on shared subroutines or data flow.；Use finer-grained token matching over API calls and resource handling patterns.

### case_id=2116 FN partial_functionality

- 方法: `moveFile` vs `getFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Moves a file by copying its contents to a new file and deleting the original.
- B 摘要: Downloads a WSDL file from a URL, modifies its XML content, saves it locally, and returns the file path.
- 静态失败原因: The static model (e.g., GraphCodeBERT) likely focused on the low token Jaccard (0.08) and the large difference in method names and overall structure, leading to a non-clone prediction. It did not capture the high-level file I/O pattern similarity that BCB annotators might have considered.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have considered both as 'file copying' tasks, where getFile's core part of downloading and writing to file is similar to moveFile's copy operation, despite the additional XML manipulation. Also, both use FileOutputStream and stream patterns, which may align with BCB's broad Type-4 clone definition.
- 共享行为: Both perform file I/O: read from a source and write to a file using output streams.
- 行为差异: moveFile copies a local file to another local file, then deletes the source; getFile downloads from a URL, modifies XML, and does not delete any source.；getFile includes XML DOM manipulation and multiple exception handling; moveFile has no XML handling.；getFile returns a String (file path); moveFile returns void.；getFile uses NIO channels for efficient transfer; moveFile uses a small byte buffer.
- 修正建议: Improve model to recognize high-level functionality patterns like file copying across different contexts.；Use dataflow analysis to detect common I/O patterns.；Incorporate method-level semantic embeddings that capture the essence of the operation.

### case_id=2117 FP boilerplate_overlap

- 方法: `main` vs `main`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Parses Prolog file to generate adapter classes and write them to a JAR with serialized object.
- B 摘要: Reads an input file and converts it to a specified format with character encoding handling.
- 静态失败原因: Model likely misled by structural boilerplate (argument parsing, file checks, try-catch) and common tokens (main, File, IOException, System.out.println), ignoring semantic differences.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clone because the functions have entirely different core logic and purpose, despite common boilerplate. The low token overlap (0.17) further supports this.
- 共享行为: Both parse command-line arguments and check file existence.；Both use try-catch for exception handling and print stack traces.；Both print usage/error messages to standard output.
- 行为差异: Domain: Prolog adapter generation vs. file format conversion.；Libraries: PrologParser, FactVisitor vs. CmdLineParser, HtmlEntityDecoderReader.；Output: JAR file with classes vs. converted file via character stream.；Error handling: usage of return vs. printUsage method.
- 修正建议: Incorporate call graph or dependency analysis to distinguish domain-specific libraries.；Use contrastive learning with negative samples that share boilerplate but different semantics.；Add attention to method-level purpose via function summaries or docstrings.

### case_id=2118 FN lexical_or_api_overlap

- 方法: `doVersionCheck` vs `login`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.65`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Checks for a new version of jEdit by downloading a version file from a URL and comparing build numbers.
- B 摘要: Logs into a web service (LOLA) by sending credentials via HTTP POST and extracting a session ID from the response.
- 静态失败原因: Static BERT models rely on token-level embeddings and are sensitive to low lexical overlap (token Jaccard = 0.18). The token sequences differ significantly (different method names, variable names, and API calls like jEdit vs get_email), causing the model to miss the structural similarity. Static models struggle to generalize across different domain-specific vocabularies even when the I/O pattern is analogous.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may label this as a clone because both functions are network I/O routines that share a similar structure: open URL, read with BufferedReader, parse lines, and handle exceptions. The broad Type-4 definition often accepts partial functional similarity where the core pattern (network communication with line parsing) is preserved despite different specific tasks.
- 共享行为: Both perform HTTP requests to a remote server；Both read the response line by line using BufferedReader；Both parse strings (version/build or session ID) from the response；Both use try-catch blocks to handle IOExceptions
- 行为差异: A uses GET request (no output), B uses POST request with URL-encoded form data；A reads multiple lines to find .version and .build, B reads only the first line for session ID；A compares build numbers and shows UI messages, B extracts and returns session ID；A relies on jEdit properties for URL, B uses hardcoded constants
- 修正建议: Use graph-based or tree-based representations (e.g., AST, CFG) to capture structural patterns；Incorporate data flow analysis to recognize common I/O patterns；Apply contrastive learning with functional similarity rather than surface form；Augment training data with more diverse token-level variations of similar I/O routines

### case_id=2119 FN benchmark_preference_bias

- 方法: `hyperlinkUpdate` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Handles hyperlink activation by fetching URL content and displaying it in a dialog.
- B 摘要: Builds an edit site by processing XML and text files, transforming content, and writing output files.
- 静态失败原因: Static BERT likely failed because it detected low token overlap (Jaccard 0.089) and no structural similarity, correctly predicting non-clone.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: Unlikely to be considered a clone even under BCB's broad Type-4 criteria; both functions have entirely different purposes and structures.
- 共享行为: Both use InputStream to read data from URLs or files
- 行为差异: A is a simple event handler; B is a complex site generation method；A reads a single URL and shows content; B processes multiple pages with transformations；A uses JEditorPane and JDialog; B uses FileSystem, Transformer, and writes files
- 修正建议: Consider that BCB may have mislabeled this pair; verify with domain experts；Improve BCB annotation guidelines to avoid labeling such dissimilar functions as clones

### case_id=2120 FN benchmark_preference_bias

- 方法: `doGet` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `1.0`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Handles HTTP GET request to serve a web page, with page lookup, permission checks, caching, and logging.
- B 摘要: Decompresses a .gz file by reading it with GZIPInputStream and writing to an output file.
- 静态失败原因: The static model correctly predicted non-clone; the error is a false negative in BCB annotation, not a model failure.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as a clone due to both methods involving I/O operations and exception handling, despite fundamentally different functionality, reflecting broad Type-4 similarity.
- 共享行为: Both perform I/O operations using streams；Both handle exceptions with try-catch-finally blocks
- 行为差异: code_a is a servlet handler for web requests, code_b is a command-line utility for file decompression；code_a uses HTTP-specific objects and logging, code_b uses file streams and system error output；code_a has complex logic for page visibility and caching, code_b is a simple copy loop
- 修正建议: Re-evaluate BCB annotation for this pair to ensure consistent clone criteria；Consider filtering out pairs with low token overlap (Jaccard < 0.1) to reduce noise

### case_id=2121 FN benchmark_preference_bias

- 方法: `readAndRewrite` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Reads a DICOM image file and rewrites it to another file.
- B 摘要: Launches an Eclipse configuration by processing Maven project files and Hibernate settings.
- 静态失败原因: Static BERT correctly predicted non-clone due to low token overlap and distinct contexts, but the BCB label suggests a false negative.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have considered both as file read/write operations, leading to a broad Type-4 partial functionality similarity, but this is too loose.
- 共享行为: Both involve file I/O operations
- 行为差异: Different domains (medical imaging vs. IDE plugin)；Different libraries and APIs；Different control flow and error handling
- 修正建议: Re-evaluate BCB label for this pair; likely a mislabel

### case_id=2122 FN benchmark_preference_bias

- 方法: `main` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a URL and extracts its contents to files using ZipInputStream.
- B 摘要: Demonstrates file I/O with FileChannel and ByteBuffer, writing and reading 'data2.txt' in various encodings.
- 静态失败原因: Static BERT models correctly identified the functions as non-clones based on low token Jaccard and distinct semantics, but BCB's label diverges; the model fails to align with BCB's potentially overly broad clone criteria.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB likely labeled this as a clone due to both being file I/O examples and having similar method structure, but such broad similarity is atypical for BCB clones; the label may be erroneous or based on very loose Type-4 criteria.
- 共享行为: Both use file I/O streams (FileOutputStream, FileInputStream).；Both are main methods that throw Exception.
- 行为差异: A involves network download and zip extraction; B is purely local file I/O with encodings.；A processes multiple zip entries; B processes a single file repeatedly.；A uses ZipInputStream; B uses FileChannel and ByteBuffer.
- 修正建议: Use task-specific fine-tuning with clearer clone definition.；Incorporate additional context like method purpose or API usage patterns.

### case_id=2123 FN partial_functionality

- 方法: `getHTML` vs `login`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches HTML content from a given URL and optionally saves it to a file.
- B 摘要: Performs a login request to a service by sending credentials and retrieves a session ID.
- 静态失败原因: Static BERT/GraphCodeBERT may fail due to low lexical overlap (token Jaccard 0.195) and different variable names and comments; it focuses on token-level similarity rather than high-level semantic patterns like HTTP request structure. The model may not capture that both involve similar I/O operations because the method names and specific API calls differ (e.g., getHTML vs login, URL vs URLConnection).
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considers the core pattern of network communication (establish HTTP connection, read response, return string) as similar enough to be a Type-4 clone, despite differences in request method and specific data handling.
- 共享行为: Both open an HTTP connection to a URL.；Both read from the connection's input stream using BufferedReader.；Both handle IOException via try-catch and print error messages.；Both return a string derived from the HTTP response.
- 行为差异: Function A uses GET request; Function B uses POST request.；Function A optionally writes response to a file; Function B does not.；Function B sends encoded form data and extracts a session ID from the response; Function A reads the entire page.；Function A takes parameters for URL, encoding, and directory; Function B has no parameters and uses class fields.
- 修正建议: Increase training data with diverse method names but similar structural patterns.；Use data-flow analysis to identify common I/O patterns.；Incorporate graph representations that capture control flow of network operations.

### case_id=2124 FN benchmark_preference_bias

- 方法: `modifyApplicationMessage` vs `write`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.1`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Modifies a properties file by updating or adding a key-value pair for internationalization.
- B 摘要: Performs SSL encryption on ByteBuffer arrays, handling handshake and data wrapping.
- 静态失败原因: Static BERT correctly identified no semantic equivalence; it was not fooled by superficial overlaps.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB label might be an error, or based on a very broad interpretation of 'modify/write' operations, but no meaningful semantic similarity exists.
- 共享行为: Both read/write data in a loop
- 行为差异: A works with text properties files; B works with binary ByteBuffer/SSL；A modifies file content; B encrypts network data；A uses file I/O; B uses SSL engine and buffer concatenation
- 修正建议: Verify BCB annotation for this pair; likely a false clone label；Improve BCB annotation guidelines to exclude unrelated functions

### case_id=2125 FN partial_functionality

- 方法: `copyIconFiles` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies icon files (16x16 and 32x32) from annotation paths to a resources output directory.
- B 摘要: Retrieves a resource by name with network download and caching, returning an InputStream.
- 静态失败原因: Static BERT models rely on token-level and structural similarity; the low Jaccard index and distinct method names, parameter types, and control flow caused the model to predict non-clone, missing the potential broad functional similarity that BCB annotators might consider.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB might consider both as 'resource copying' methods that read from a source and write to a destination, treating them as functionally similar under a broad Type-4 clone category.
- 共享行为: Both perform file I/O operations (read from source, write to destination).；Both use try-catch blocks for exception handling.；Both involve resource handling (closing streams).
- 行为差异: Function A copies local icon files based on annotations; Function B downloads and caches remote resources.；Function A uses FileChannel for efficient copying; Function B uses Buffered streams.；Function B has caching logic and URL connection handling; A does not.；Different input types (UmlClass vs String) and output (void vs InputStream).
- 修正建议: Incorporate higher-level semantic representations of resource handling and file I/O.；Use program analysis to capture data flow and common patterns like read-write-chaining.

### case_id=2126 FN benchmark_preference_bias

- 方法: `init` vs `register`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Loads controller classes listed in a registry file from classpath and registers them via addClass().
- B 摘要: Registers a new User by setting properties, creating a phpBB forum account via HTTP, persisting the user, and sending a confirmation email.
- 静态失败原因: Static BERT models rely on token/embedding similarity and low Jaccard (0.14) and different method names ('init' vs 'register') correctly indicated non-clone. The model correctly predicted non-clone.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as a clone due to superficial similarity in reading from a stream line by line and processing, which is a common pattern. However, this is a very broad match and likely a false positive in BCB.
- 共享行为: Both read from an external resource (file/URL) line by line and process each line.；Both use logging and handle I/O exceptions.
- 行为差异: Different input types: ServletContext vs User object.；Different output: void vs boolean.；Core functionality: class loading and registration vs user attribute setting, remote registration, persistence, and email sending.；One is initialization, the other is user registration with external service dependency.
- 修正建议: Improve clone detection to focus on functional purpose rather than code patterns.；Incorporate high-level semantics via program analysis or documentation.

### case_id=2127 FP boilerplate_overlap

- 方法: `getContent` vs `getFrameworkFactory`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Retrieves HTTP response content as a string by executing an HTTP request and reading the response body line by line.
- B 摘要: Loads an OSGi FrameworkFactory instance by reading a service configuration file from the classpath and instantiating the specified class.
- 静态失败原因: The model likely overestimated the similarity due to high lexical overlap in boilerplate code (BufferedReader, readLine, close, etc.) and similar structural patterns, ignoring the distinct domain-specific logic and method names.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clones because the functions have completely different purposes (HTTP response retrieval vs. OSGi service loading) despite sharing a common I/O pattern. BCB focuses on functional similarity, which is absent here.
- 共享行为: Both use BufferedReader to read lines from a stream until null；Both close the reader after reading
- 行为差异: Function A executes an HTTP request and reads from the response entity; Function B reads from a classpath resource URL；Function A returns the entire response content as a string; Function B returns a FrameworkFactory object or throws an exception；Function A sets connection and socket timeouts; Function B does not；Function A handles line ending by appending newline; Function B does not modify lines except trimming and skipping comments
- 修正建议: Incorporate method name and class context into embeddings；Use a model that captures semantic role of the function (e.g., API calls, return type)；Augment training data with more diverse examples of non-clones sharing I/O patterns

### case_id=2128 FP lexical_or_api_overlap

- 方法: `DialogHelper` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Constructs a dialog to display an image and provide save as and close buttons.
- B 摘要: Handles action commands to set various preferences (e.g., GraphViz path, ImageMagick path, scale, date format) via file choosers and updates UI.
- 静态失败原因: Static models like GraphCodeBERT may have been misled by overlapping API calls (e.g., JFileChooser, file operations) and boilerplate code (e.g., try-catch blocks) that appear in both functions, causing a false positive prediction.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: Under BCB guidelines, these functions are not clones because they have entirely different functionality and structure. BCB typically requires some semantic similarity in terms of input-output behavior or algorithmic steps, which is absent here.
- 行为差异: Different purposes: A is for saving an image file, B is for setting application preferences.；Different UI structure: A creates a JDialog with image and buttons, B is an actionPerformed method for multiple commands.；Different file operations: A copies an image file, B selects executable files for tool paths.；Different context: A is part of a dialog helper, B is part of a preferences settings controller.
- 修正建议: Improve model capacity to distinguish general-purpose API usage from specific task semantics.；Incorporate more structural or dataflow information to capture overall intent rather than local token overlap.；Use contrastive learning or negative sampling to reduce false positives from common but unrelated boilerplate.

### case_id=2129 FP partial_functionality

- 方法: `decodeFileToFile` vs `readData`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Reads a Base64-encoded file and decodes it to an output file, returning success status.
- B 摘要: Parses multiple comma-separated string fields into sets and a hash map, and reads a configuration file to build lookup tables.
- 静态失败原因: The model may have been misled by the truncated middle of function B, which contains a large block of file-reading code, causing superficial similarity in I/O patterns (try-catch, while loop) despite different purposes.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB would not consider these as clones because the overall functionality is completely different: one is a Base64 decode/encode utility, the other is a data initialization routine for a Tibetan/Unicode system.
- 行为差异: Function A performs file-to-file Base64 decoding; B parses string tokens and reads a config file.；Function A returns a boolean; B is void and modifies global state.；Function A uses InputStream and OutputStream; B uses StringTokenizer and BufferedReader.；Function A has simple loop copying bytes; B has complex parsing logic with multiple tokens and conditionals.
- 修正建议: Use cross-function dataflow analysis to capture actual variable usage and transformations.；Improve handling of truncated code to avoid focusing on incomplete patterns.；Incorporate overall method signature and return-type analysis.

### case_id=2130 FN benchmark_preference_bias

- 方法: `copy` vs `modifyApplicationMessage`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Copies a file from source to destination using FileChannel transferTo.
- B 摘要: Modifies a localized properties file: ensures locale file exists by copying from English file, then reads the properties file and updates or adds a key-value pair.
- 静态失败原因: The static model likely predicted non-clone due to very low token Jaccard similarity (0.075), different method names ('copy' vs 'modifyApplicationMessage'), and significant structural differences. The model may have over-relied on lexical and syntactic cues, missing the potential semantic overlap in file I/O operations that BCB considered.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled these as clones under a very broad interpretation of Type-4 (semantic similarity) because both functions perform file I/O and involve reading/writing file content. However, the core functionalities are distinct: one is a generic file copy, the other is a locale-specific properties file modifier. This labeling seems inconsistent with typical BCB guidelines.
- 共享行为: Both involve reading from a file and writing to a file.；Both use Java I/O classes (FileInputStream/FileOutputStream or FileReader/FileWriter).
- 行为差异: A copies entire file byte-by-byte; B reads text lines and modifies content.；A uses FileChannel transferTo for efficient copying; B uses BufferedReader and manual line handling.；A operates on two files (source, destination); B reads from one file and writes to the same or another file conditionally.；B includes locale handling, exception handling, and conditional file creation; A is straightforward.
- 修正建议: Train models with more diverse clone types to avoid bias towards broad file-I/O similarities.；Incorporate explicit data flow analysis to distinguish between copy and modification operations.；Use contrastive learning to penalize high-level functional differences despite overlapping low-level I/O patterns.

### case_id=2131 FN partial_functionality

- 方法: `getFile` vs `byReference`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies the SOAP address endpoint, and returns the local file path.
- B 摘要: Copies an InputStream to a temporary file and returns a DigitalObjectContent wrapping that file.
- 静态失败原因: Static BERT models likely focused on the different method names and token sequences (low Jaccard similarity), missing the structural similarity in the temp-file writing pattern and the shared boilerplate of I/O operations.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely labels them as Type-3 clones because both implement a pattern of reading data from a source and writing to a temporary file with exception handling, despite different high-level functions.
- 共享行为: Both create temporary files；Both write data to output streams；Both handle IOException；Both close streams after writing
- 行为差异: A downloads from network, B reads from an InputStream；A modifies XML, B does not；A returns a String path, B returns a DigitalObjectContent；A has multiple exception types, B only IOException
- 修正建议: Incorporate control flow graph or data flow analysis to detect common sub-patterns like 'write to temp file'；Use graph-based representation to capture structural similarities beyond lexical tokens；Add attention to exception handling blocks as a signal for similar boilerplate

### case_id=2132 FP benchmark_preference_bias

- 方法: `readData` vs `hyperlinkUpdate`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Parses comma-separated string fields to populate various sets and maps for Tibetan character processing.
- B 摘要: Handles hyperlink activation by fetching URL content and displaying it in a dialog.
- 静态失败原因: The model likely overfocused on common Java boilerplate patterns (IOException, StringWriter) and missed the vast semantic gap, possibly due to limited context or training bias towards I/O operations.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB would not label this as a clone because the functions are completely different in functionality and context, despite superficial similarities like IOException handling.
- 共享行为: Both involve reading input data (one from string variables, one from URL stream)
- 行为差异: Different purpose: character set initialization vs. hyperlink event handling；Different data sources: static strings vs. URL；Different outputs: sets/maps vs. dialog display；One has extensive string tokenization, the other has none
- 修正建议: Improve functional abstraction understanding；Incorporate data flow analysis to distinguish I/O operations；Add more diverse training examples for unrelated methods

### case_id=2133 FN partial_functionality

- 方法: `writeFileToFile` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Copies content from one file to another using FileChannel.transferTo.
- B 摘要: Handles an Eclipse launch configuration by checking project type, processing XML files, and conditionally copying a resource file to the project.
- 静态失败原因: Static BERT models heavily rely on token overlap and syntactic structure; the very low Jaccard similarity (0.061) and completely different vocabulary (file channels vs. Eclipse APIs) led the model to correctly identify them as non-clones, but it missed the deeper semantic commonality of file copying.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely labeled this as a Type-4 clone because both functions contain a file copy operation, and the partial similarity (file I/O) is sufficient under BCB's broad annotation guidelines.
- 共享行为: Both involve writing data to a file (file copy operation).
- 行为差异: Function A is a simple, unconditional file copy utility with no dependencies.；Function B is a complex launch handler with many conditions, Eclipse API calls, and a broader purpose beyond file copying.；The file copy in B is a small conditional substep, not the main functionality.
- 修正建议: Incorporate data augmentation that emphasizes partial functionality clones.；Use graph-based or flow-sensitive representations to capture I/O operations.；Add domain-specific knowledge of common operations (e.g., file copy) to the model.

### case_id=2134 FN partial_functionality

- 方法: `copyResource` vs `copy`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource from a URL or file to a destination file using byte-by-byte reading.
- B 摘要: Copies a file from one path to another with extensive validation and buffered I/O.
- 静态失败原因: Static BERT/GraphCodeBERT models may focus on lexical token overlap and structural similarity; here, token Jaccard is low (0.226), and the overall structure is different (A has conditional source selection, B has many validation checks). The model might miss the common core behavior of copying content due to the low token overlap and different control flow, leading to false negative.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB considers both as file copying operations with the core functionality of reading from a source and writing to a destination, despite differences in source type and validation; the partial functionality overlap is deemed sufficient for a clone.
- 共享行为: Copy content from a source to a destination file；Use input/output streams；Read and write bytes；Close streams after copying
- 行为差异: A supports URL sources; B only file sources；A reads byte-by-byte; B uses buffered reading；A has minimal validation; B has thorough error checking and validation；A throws Exception; B throws IOException with specific abort messages
- 修正建议: Improve models to recognize core functional equivalence despite lexical differences；Incorporate data flow analysis to trace the input-output copying pattern；Use example-driven learning for similar I/O operations；Add heuristics for resource copying patterns

### case_id=2135 FN benchmark_preference_bias

- 方法: `readAndRewrite` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Reads a DICOM image file, parses it, reads pixel data, and writes it to a new file in a different encoding.
- B 摘要: Downloads a KMZ file from a URL, extracts its entries (ZIP entries), and writes each entry to a local file.
- 静态失败原因: The static BERT model correctly identified non-clone behavior due to low token overlap (0.118) and distinct API usage; its 'failure' is only relative to a BCB label that seems incorrect.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled these as clones due to a very broad interpretation of 'read and rewrite' involving I/O stream handling, possibly as a Type-4 semantic clone where the high-level goal is similar, but the domain-specific details differ.
- 共享行为: Both involve reading input from a source and writing output to files；Both use Java I/O streams (e.g., BufferedInputStream, FileOutputStream)
- 行为差异: Code A processes DICOM medical image data with pixel manipulation, while Code B extracts ZIP entries from a KMZ file；Code A writes a single output file with specific encoding, Code B writes multiple files from ZIP entries；Code A uses DICOM-specific libraries (e.g., DcmParser, PixelDataReader), Code B uses standard Java ZIP and URL libraries；Code A has no loops, Code B has a while loop for iterating ZIP entries
- 修正建议: Re-evaluate the BCB annotation for this pair to confirm if it truly meets their criteria；If keeping the label, provide explicit rationale for the broad I/O pattern similarity；Use domain-aware model features to distinguish different file formats and processing logic

### case_id=2136 FP lexical_or_api_overlap

- 方法: `doVersionCheck` vs `readUNI`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Checks for new version by reading version info from a URL and comparing build numbers.
- B 摘要: Reads tab-separated entries from a URL and populates a vector with id and description.
- 静态失败原因: The model likely focused on surface-level API overlaps (URL, openStream, line reading, try-catch) and structural similarity, missing the deeper semantic difference in what data is parsed and how it is used.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this non-clone because the core functionality (version checking vs data extraction) is completely different, despite sharing a common I/O pattern.
- 共享行为: Both open a URL, read text input line by line, parse fields, and close the stream.
- 行为差异: Different parsing logic and field extraction (version check vs tab-separated data)；Different error handling (show error to view vs print stack trace)；Function A includes UI interaction (show/hide cursor, message dialogs) while B does not.
- 修正建议: Train the model to differentiate between data parsing for different purposes (e.g., version check vs data extraction) by including more diverse training examples.；Incorporate dataflow analysis to capture how parsed data is transformed and used.

### case_id=2137 FN benchmark_preference_bias

- 方法: `actionPerformed` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Reads a gzipped file, extracts rs IDs, and queries NCBI E-utils to fetch SNP data via HTTP.
- B 摘要: Launches an Eclipse plugin build configuration for a NexOpen project, processing pom.xml files and setting up Hibernate reverse engineering.
- 静态失败原因: Static BERT correctly predicted non-clone; the prediction error (FN) stems from BCB's benchmark label likely being a mislabel or based on superficial API overlap.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as a clone due to both functions involving file I/O, stream handling, and exception handling, leading to a broad Type-4 classification, but the actual semantics differ completely.
- 共享行为: Both use IOUtils.copy for stream copying；Both have try-catch blocks for IOException
- 行为差异: Function A makes HTTP requests to NCBI; Function B performs local file manipulation and Eclipse project configuration；Function A processes SNP IDs; Function B processes Maven project files；Function A is a GUI event handler; Function B is a launch method for Eclipse plugin
- 修正建议: Re-evaluate BCB label for this pair considering overall functionality domain；Use cross-domain detection or task-specific fine-tuning to avoid superficial API pattern matching

### case_id=2138 FP boilerplate_overlap

- 方法: `handleHandshake` vs `parse`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Handles Minecraft handshake packet, validates username and server session.
- B 摘要: Parses a data file (CSV-like) into a DataSet, handling headers, types, and scientific notation.
- 静态失败原因: Static BERT models may overemphasize shared API calls like BufferedReader and NumberFormat, and fail to capture the high-level semantic difference in domain and flow.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels as non-clone because the functions have entirely different domain purposes and no shared functionality beyond basic I/O boilerplate.
- 共享行为: Use BufferedReader for I/O；Handle NumberFormatException or use NumberFormat；Involve conditional logic and loops
- 行为差异: Function A is network session validation; B is data parsing；A sends packets and reads HTTP response; B reads local file or URL and tokenizes lines；A has specific Minecraft dependencies; B is generic data parsing
- 修正建议: Improve model's ability to recognize domain-specific context；Incorporate more structural or data-flow information to differentiate unrelated I/O patterns；Include function name and broader context to disambiguate purposes

### case_id=2139 FP boilerplate_overlap

- 方法: `main` vs `copyFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.98`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Parses a Prolog file, generates adapter classes and resources based on the parsed program, and writes output to a JAR file.
- B 摘要: Copies a file from source to destination using file channels.
- 静态失败原因: Static BERT/GraphCodeBERT may rely on surface-level token patterns and API usage. Both functions contain common Java keywords (e.g., File, try, IOException, close) leading to a false positive. The model lacks deep understanding of the overall program logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clones when functions implement entirely different functionalities, even if they share some common Java constructs (e.g., File I/O). The benchmark expects functional similarity, not just API overlap.
- 共享行为: Both use File objects and file I/O operations.
- 行为差异: Function A is a complex main method orchestrating multiple steps including parsing, code generation, and resource serialization.；Function B is a simple utility that performs a single file copy operation.；Function A handles command-line arguments and error messages; Function B has no argument handling.；Function A uses various libraries (Prolog parser, ASM, class loaders); Function B uses only basic Java I/O.
- 修正建议: Improve training with contrastive learning to distinguish boilerplate from semantic similarity.；Incorporate control-flow and data-flow analysis to capture actual behavior.；Use larger context or method-level embeddings that capture overall intent.

### case_id=2140 FP lexical_or_api_overlap

- 方法: `readData` vs `copy`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: readData parses comma-separated string tokens to populate sets and a map, likely initializing character classification data, and includes file reading.
- B 摘要: copy copies a file from source to destination using file streams.
- 静态失败原因: Likely due to lexical overlap of common API elements (IOException, File) and similar exception handling, misleading the model.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels as non-clone because functions perform entirely different tasks with no semantic overlap beyond basic I/O.
- 共享行为: Both involve file I/O (readData reads from a file, copy reads and writes files).；Both throw IOException.
- 行为差异: readData parses tokens and fills multiple data structures; copy simply copies bytes.；readData is initialization logic; copy is a utility function.；Different input parameters and return types.
- 修正建议: Improve training with more diverse negative samples.；Enhance model's ability to distinguish high-level semantics from low-level API usage.

### case_id=2141 FP boilerplate_overlap

- 方法: `main` vs `copyParseFileToCodeFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: A main method that parses a Prolog file, generates adapter classes, and writes them to a JAR file with associated resources.
- B 摘要: A private method that copies the contents of one file to another using a buffer.
- 静态失败原因: The static BERT model likely overemphasized the overlapping API tokens (e.g., FileInputStream, FileOutputStream, read, write) and boilerplate exception handling, missing the vast difference in scope and purpose. The very low token Jaccard (0.058) indicates minimal lexical overlap, but the model may have been misled by the presence of common I/O patterns in both methods, treating them as functionally similar.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels this as non-clone (0) because the overall functionality is completely different: one is a complex adapter generator, the other is a simple file copy. Even though both involve file I/O, the semantic intent and implementation are not similar enough for any clone type in BCB's taxonomy.
- 共享行为: Both involve file I/O operations (reading from a file, writing to a file).
- 行为差异: Function A uses many libraries (Prolog parser, ASM bytecode library) and performs complex generation, while B uses only basic Java I/O.；Function A processes command-line arguments and generates multiple output files; B copies a single file with fixed filenames.；Function A has nested logic and exception handling; B is a straightforward copy loop.
- 修正建议: Incorporate data-flow analysis to distinguish simple file copy from complex multi-step processing.；Add attention to method length and complexity as a signal of different functionality.；Train on more examples that contrast I/O-heavy but semantically different methods.

### case_id=2142 FN partial_functionality

- 方法: `testCopy_readerToOutputStream_Encoding` vs `copyResource`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Tests copying from a Reader to an OutputStream with encoding conversion and verifies content equality.
- B 摘要: Copies a resource (URL or file) to a destination file using raw byte stream copying.
- 静态失败原因: Static BERT/GraphCodeBERT likely focused on low token overlap (Jaccard 0.0895) and structural differences (test vs utility, different stream types), missing the broader functional similarity that BCB considers.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB labels this as a clone because both functions perform the high-level task of copying data from an input to an output using I/O streams, and the core copy functionality is similar despite differences in stream types and contexts.
- 共享行为: Both perform stream-based data copying from a source to a destination.；Both close streams after copying.
- 行为差异: A uses character streams with encoding; B uses byte streams without encoding.；A is a test method with assertions; B is a utility resource copy method.；A relies on IOUtils.copy; B implements a manual byte-by-byte loop.；A uses special test stream wrappers; B uses standard IO streams.
- 修正建议: Train model on broad functional categories (e.g., 'copy data') rather than exact API use.；Use data-flow or control-flow abstractions to capture common I/O patterns.；Incorporate context-aware embeddings that handle encoding variations.

### case_id=2143 FN partial_functionality

- 方法: `modifyApplicationMessage` vs `execute`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Modifies a locale-specific properties file by reading, updating, or adding a key-value pair.
- B 摘要: Saves a HomeMap object and copies an uploaded image file to a directory.
- 静态失败原因: Static BERT methods rely heavily on lexical token overlap and method name similarity. With very low Jaccard similarity (0.066) and different method names, the model predicted non-clone, missing the structural file read-modify-write pattern that BCB may consider.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB might classify this as a clone due to the common high-level pattern of reading from an input, processing, and writing to a file, both involving file I/O and exception handling. The broad Type-3/Type-4 acceptance may consider this partial functionality similarity despite different data types and application logic.
- 共享行为: Both perform file I/O operations (reading and writing files).；Both handle exceptions with try-catch and print stack traces.；Both write data to a file on disk.
- 行为差异: A deals with text properties files and string manipulation, while B handles binary image files via IOUtils.copy.；A includes logic for file existence check and default file copying, which B lacks.；A outputs a modified properties file, while B outputs an image file and persists a database object.；B returns a string from a separate method, while A returns void.
- 修正建议: Enhance model to recognize structural patterns like file read-write operations even with different APIs.；Incorporate reasoning about common operations (reading, processing, writing) rather than exact token matches.；Use dataflow or flow-based analysis to capture similar data transformations.

### case_id=2144 FN partial_functionality

- 方法: `copyResource` vs `doBody`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource (URL or file) to a destination file using byte-by-byte stream copy with no exception handling.
- B 摘要: Copies data from a file to an HTTP response output stream using buffered streams and IOUtils, with exception handling and logging.
- 静态失败原因: Low token Jaccard (0.095) indicates minimal lexical overlap. Static BERT models rely on token similarity and structural patterns; the functions use different APIs (IOUtils vs manual loop, different stream classes) and method names, leading to low embedding similarity and a non-clone prediction.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often considers functional similarity for Type-3/4 clones. Both functions implement the same core operation of copying data from input to output via streams, so they are labeled as clones despite lexical differences.
- 共享行为: Both read from an input source and write to an output stream, performing an I/O copy operation.
- 行为差异: A uses unbuffered streams and manual byte loop; B uses buffered streams and IOUtils.copy utility.；A has no exception handling; B catches and logs exceptions.；A writes to a file; B writes to HTTP response output stream.；A conditionally loads resource from URL or file; B loads data via a method call.
- 修正建议: Incorporate data flow analysis to capture stream copy patterns.；Use control flow abstraction to recognize similar I/O loops.；Train models on API-level semantics like InputStream/OutputStream copying.；Consider graph-based representations that highlight data dependencies.

### case_id=2145 FN lexical_or_api_overlap

- 方法: `doGet` vs `unJar`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Handles HTTP GET request to retrieve and display a web page with access control and caching.
- B 摘要: Extracts a specified entry from a JAR file to the filesystem.
- 静态失败原因: The model likely relied on overlapping keywords like 'IOException', 'File', 'catch', etc., or was confused by the method length and structure, despite low token Jaccard.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may have labeled as clone due to both containing try-catch blocks and I/O operations, but this seems like a mislabel as functionality is completely different.
- 共享行为: Both use try-catch exception handling；Both perform I/O operations
- 行为差异: doGet is a web servlet handler; unJar is a file extraction utility；doGet uses HttpServletRequest/Response; unJar uses JarFile and FileOutputStream；doGet involves complex logic with page retrieval, visibility checks, and caching; unJar simply copies a file
- 修正建议: Incorporate data flow analysis to capture functional semantics；Use program slicing to focus on core behavior；Train on more diverse negative examples to reduce false positives from common API usage

### case_id=2146 FN partial_functionality

- 方法: `runInternal` vs `run`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches and parses an OPDS catalog with pagination, handling HTTP connections, progress updates, and partial loading.
- B 摘要: Performs a simple HTTP GET request with Basic Authentication and reads the response into a string.
- 静态失败原因: Static BERT models like GraphCodeBERT rely on token-level and syntactic similarity. The low Jaccard similarity and significant differences in method length, control flow, and variable names cause the model to miss the shared high-level intent. The model does not capture the semantic equivalence of the core HTTP retrieval subtask.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely annotates this as a clone because both functions perform the core task of making an HTTP GET request and reading the response, which is a common high-level functionality. The additional features in Code_a (pagination, progress, OPDS parsing) are considered extensions of the base HTTP retrieval behavior, making them Type-4 functional clones.
- 共享行为: Both open an HTTP connection (HttpURLConnection) and set doInput to true.；Both obtain an input stream from the connection.；Both read data from the input stream.；Both disconnect the connection after use.
- 行为差异: Code_a uses a loop for pagination and may continue loading from next links, while Code_b does a single request.；Code_a checks HTTP response code and handles non-200 responses, while Code_b does not.；Code_a includes progress reporting and parsing of content (OPDS entries), while Code_b only reads raw data.；Code_b adds Basic Authentication header, which Code_a does not.
- 修正建议: Incorporate dataflow analysis to identify common sequences of API calls (e.g., openConnection, setDoInput, getInputStream, disconnect).；Use execution traces or dynamic analysis to compare runtime behavior.；Train models with more examples of partial functionality clones where one function subsumes another.；Enhance embeddings with domain-specific knowledge about HTTP operations.

### case_id=2147 FP boilerplate_overlap

- 方法: `getLinksFromURLFast` vs `read`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Extracts all hyperlinks and their text from a web page by parsing HTML anchor tags, converting relative URLs to absolute, and returns them as two vectors.
- B 摘要: Reads a skeleton resource file line by line, splits it into sections separated by lines starting with '---', and adds the sections to a list, throwing an exception if the section count does not match expected size.
- 静态失败原因: Static BERT/GraphCodeBERT likely overemphasized lexical and API overlap (URL, BufferedReader, readLine, StringBuilder, Exception) which are common boilerplate patterns, ignoring the distinct semantic intents.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clone because despite shared I/O boilerplate, the core functionality (link extraction vs. section splitting) is completely different and not even partial clones under Type-3/Type-4 criteria.
- 共享行为: Read text line by line from an input stream using BufferedReader.
- 行为差异: Function A parses HTML to extract links; Function B splits text into sections.；Function A works over network URL; Function B loads a classpath resource.；Function A returns extracted data via Vector; Function B populates an internal list and throws exceptions on mismatch.；Function A uses regular expressions for pattern matching; Function B uses simple string prefix checking.
- 修正建议: Incorporate data flow and control flow analysis to distinguish unique functional logic.；Use method name/context or broader program structure as additional features.；Apply clone-specific AST or graph-based representations that capture behavioral semantics beyond token sequences.

### case_id=2148 FP boilerplate_overlap

- 方法: `setMembers` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Parses Trac ticket HTML to extract component and priority option lists.
- B 摘要: Performs Google image search, extracts image URLs from HTML, and updates UI with the first image.
- 静态失败原因: Static BERT/GraphCodeBERT may have over-relied on common tokens and structural patterns (URL, BufferedReader, while loop, try-catch) shared by many web-scraping methods, while ignoring the domain-specific logic and different method names. The high proportion of boilerplate code relative to unique functionality caused a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BigCloneBench typically labels clones based on functional similarity. Here, the functions serve different purposes (Trac ticket configuration vs. Google image search), so BCB would likely consider them non-clones despite structural overlap in HTTP connection boilerplate.
- 共享行为: Both open a URL and read HTML content line by line.；Both parse HTML using string manipulation/pattern matching.；Both collect extracted data into collections (arrays/lists).；Both handle exceptions.
- 行为差异: Different target websites (Trac vs Google Images).；Different parsing logic: A extracts <select> option values; B extracts image URLs from href attributes.；Different output: A sets member arrays; B stores in googleImages and updates UI.；A uses regex via Pattern/Matcher; B uses split and substring.
- 修正建议: Enhance model sensitivity to method names and class context.；Use data-flow analysis to capture differences in how extracted data is used.；Augment training with examples that have similar boilerplate but different purposes.；Apply contrastive loss to penalize false positives on structural patterns.

### case_id=2149 FP long_range_semantics

- 方法: `SHA1` vs `perform`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `static_summary_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Computes SHA-1 hash of input text using MessageDigest.
- B 摘要: Processes a web request to classify a concept by building XML, sending it to a URL, parsing the response, and storing results in session.
- 静态失败原因: The static BERT model may have been misled by truncation of the long perform function, seeing only boilerplate start/end, causing it to overlook deep semantic differences.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely labeled non-clone because the functions have completely different semantics and minimal lexical similarity (Jaccard=0.05).
- 共享行为: Both involve string manipulation and exception handling.
- 行为差异: Different purpose: hashing vs. web request processing.；Different external dependencies: MessageDigest vs. Struts, HTTP connections, XML parsing.；Different control flow: simple sequential vs. complex conditionals and loops.
- 修正建议: Improve input representation to handle long functions without truncation.；Enhance model with dataflow or control flow features to capture semantics.

### case_id=2150 FP lexical_or_api_overlap

- 方法: `main` vs `copyToDir`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Generates adapter classes from a Prolog file and writes them to a JAR using a multi-step process.
- B 摘要: Copies a file to a specified directory, creating the directory if needed.
- 静态失败原因: The model likely overemphasized lexical and API overlaps (e.g., both use File, IOException, file streams) and common error-handling boilerplate, ignoring the vastly different overall logic and goals.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels 0 because the functions have entirely different purposes and only trivial token overlap; BCB requires at least partial semantic similarity for Type-3/4 clones, which is absent here.
- 共享行为: Both perform file existence checks.；Both read from and write to files.；Both handle IOException with try-catch.；Both use File and file streams.
- 行为差异: A is a main method with command-line parsing; B is an instance method.；A generates Java bytecode and serializes data; B simply copies a file.；A uses complex libraries (ASM, Prolog parser); B uses basic Java I/O.；A has a debug flag; B has no such option.
- 修正建议: Incorporate structural features like AST or control-flow graphs to capture higher-level semantics.；Train on more diverse examples that distinguish simple file utilities from complex processing tasks.；Use data-flow aware models to differentiate between file copying and multi-step code generation.

### case_id=2151 FN benchmark_preference_bias

- 方法: `doGet` vs `hyperlinkUpdate`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.1`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Handles HTTP GET requests to serve portal pages after checking permissions and logging statistics.
- B 摘要: Displays content of a hyperlink URL in a dialog window when the hyperlink is activated.
- 静态失败原因: Static BERT correctly predicted non-clone because the token overlap is very low (Jaccard 0.074) and the APIs and control flows are entirely different.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB likely mislabeled this pair as clone due to superficial similarity in event handling and I/O, but the functionality is entirely unrelated.
- 共享行为: Both handle an event (HTTP request vs hyperlink activation)；Both perform I/O operations to read data from a source；Both use try-catch blocks for exception handling
- 行为差异: A is server-side servlet processing; B is client-side GUI event handling；A involves complex page caching, permission checks, and response generation; B simply opens a URL and displays plain text；A writes to HTTP response object; B creates a JDialog with a JEditorPane；A has extensive logging and error handling; B has minimal error handling and no logging
- 修正建议: Re-evaluate the BCB annotation for this pair; likely a mislabel.

### case_id=2152 FP lexical_or_api_overlap

- 方法: `getLinksFromURLFast` vs `run`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Extracts hyperlinks from an HTML page returned by a URL using regex.
- B 摘要: Reads structured text lines from a URL, parsing version and URL fields, then notifies listeners.
- 静态失败原因: Static BERT models often over-rely on lexical and API-level similarity (e.g., BufferedReader + URL pattern) and fail to capture deep semantic differences in loop body logic, conditional structures, and return/event handling.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: Despite shared I/O boilerplate, the core functionality is completely different (web scraping vs. reading a configuration file), so BCB would label as non-clone (Type-4). Broad partial similarity is insufficient.
- 共享行为: Read lines from a URL using BufferedReader；Use URL.openStream() to get input stream；Iterate over lines with while loop
- 行为差异: Function A extracts HTML <a> links; Function B parses specific structured format with line index；Function A returns Vector array of links/texts; Function B writes to fields and fires ActionListener events；Function A uses regex for parsing; Function B uses switch/case on line index；Function A includes debug prints and timing; Function B has exception handling with error codes
- 修正建议: Incorporate data-flow analysis to distinguish parsing stages；Add negative examples with similar I/O but different business logic during training；Use structure-aware embeddings that capture control-flow divergence

### case_id=2153 FN partial_functionality

- 方法: `readURL` vs `register`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a URL and prints each line to standard output.
- B 摘要: Registers a user by encoding password, setting authorities, creating a hash, reading a forum URL line-by-line to set forum ID, persisting user, and sending confirmation email.
- 静态失败原因: Static BERT models rely on token-level similarity, but the token Jaccard is very low (0.116) due to very different surrounding code. The shared I/O pattern is semantically similar but lexically distinct from the rest, causing the model to miss the partial functional overlap.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely labels this as a clone because both functions share a non-trivial sequence of reading from a URL line-by-line, which is a distinctive functional component despite different overall purposes.
- 共享行为: Both open a URL and create a BufferedReader to read the content line by line；Both handle IOExceptions and close the input stream
- 行为差异: Function A only reads and prints lines; Function B processes lines to set a forum ID and performs many other setup operations；Function A uses a finally block to close resources; Function B closes the reader explicitly；Function B includes additional exception handling for NumberFormatException and more complex logic
- 修正建议: Include features capturing common I/O patterns (e.g., URL open, BufferedReader readLine) via data flow or control flow graphs；Use contrastive learning that treats functional similarity as positive even when lexical overlap is low；Train on a dataset with broad Type-3/Type-4 clones that emphasize shared subroutines

### case_id=2154 FP lexical_or_api_overlap

- 方法: `writeFileType` vs `SRWGuiClient`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads URIs from a file, fetches each URI, inspects the first 100 lines for specific RDF/OWL namespace declarations, and writes a classification (OWL, RDFS, RDF, UNKNOWN, or BROKEN) to an output file.
- B 摘要: Constructor for a Swing browser GUI that reads an initial URL, optionally applies XSLT transformation to the content, and displays the resulting HTML in a JEditorPane.
- 静态失败原因: The model likely relied on lexical cues such as 'URL', 'BufferedReader', 'try', 'catch', and 'Exception', which appear in both functions, and may have been misled by the similar structure of reading lines in a loop, while ignoring the completely different overall logic and output.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labeled 0 because these functions have no semantic overlap in purpose or behavior; they belong to entirely different domains (data classification vs GUI browser) and share only common Java I/O utilities.
- 共享行为: Both use java.net.URL and java.io.BufferedReader to read from a URL；Both use try-catch blocks for exception handling
- 行为差异: A reads from a local file to get multiple URIs, B uses a single initialURL passed to constructor；A parses HTTP response to check for RDF/OWL namespaces, B parses XML and applies XSLT transformation；A writes to an output file, B sets up GUI components and displays content；A is a static method, B is a constructor
- 修正建议: Train the model to emphasize functional semantics over token overlap；Incorporate data-flow or control-flow analysis to differentiate tasks；Use a larger context window to capture high-level purpose

### case_id=2155 FN benchmark_preference_bias

- 方法: `split` vs `getFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Splits a FASTA file into multiple smaller files based on maximum bases and entries.
- B 摘要: Downloads a WSDL file from a URL, modifies its endpoint, and saves it locally.
- 静态失败原因: Static BERT models rely on token-level similarity and may not capture the structural commonalities (e.g., file channel usage) that BCB annotators considered; low Jaccard similarity (0.129) further reduces prediction score.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB annotators may have considered both functions as broad file manipulation utilities with similar file I/O patterns (FileChannel, streams), leading to a Type-4 (semantic) clone annotation despite different overall purposes.
- 共享行为: Both perform file I/O operations using FileChannel.；Both check file existence before processing.；Both read from an input source and write to an output file.
- 行为差异: Function A splits a file based on size constraints; Function B downloads and modifies a file.；Function A handles FASTA format-specific parsing; Function B handles XML parsing and namespace manipulation.；Function A returns a count of partitions; Function B returns a file path.；Function A uses direct ByteBuffer and transferTo; Function B uses ReadableByteChannel and transferFrom.
- 修正建议: Incorporate structural or dataflow features to detect high-level I/O patterns.；Use contrastive learning to distinguish functional similarity from superficial I/O overlap.；Re-evaluate BCB annotations for consistency in broad Type-4 clone definitions.

### case_id=2156 FN benchmark_preference_bias

- 方法: `copy` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Recursively copies a file or directory to a destination using file channels.
- B 摘要: Retrieves a resource by URL, caches it locally, and returns an InputStream, with HTTP conditional GET and caching logic.
- 静态失败原因: The model correctly predicted non-clone because it focused on token overlap and structural differences, but BCB's label (clone) is likely a benchmark preference bias, making the model appear to fail.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled them as clones due to both being file I/O utility functions with similar low-level operations (mkdirs, stream usage, exception handling), despite different high-level purposes.
- 共享行为: Both create directories using mkdirs；Both use File and stream classes；Both print status messages to System.out；Both handle exceptions with printStackTrace
- 行为差异: A is a generic file copy; B is resource retrieval with caching；A uses FileChannel; B uses BufferedInputStream/OutputStream；B involves HTTP connection, URL, and caching logic；A is synchronous and static; B is synchronized and instance method
- 修正建议: Improve alignment with BCB annotation guidelines that may consider broad operational similarity；Incorporate domain or context to recognize utility function categories

### case_id=2157 FN partial_functionality

- 方法: `copyResource` vs `readAndRewrite`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies any resource (URL or local file) byte-by-byte to a destination file.
- B 摘要: Reads a DICOM image file, parses metadata, reads pixel data, and writes it out to another file.
- 静态失败原因: Low token Jaccard (0.1) and different API usage (simple Java I/O vs. DICOM-specific libraries) cause the model to miss the abstract I/O similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider this a clone because both functions share the high-level behavior of reading from an input source and writing to an output destination, ignoring the domain-specific DICOM processing as incidental.
- 共享行为: Both read from an input source and write to an output file.；Both use input and output streams and close them.；Both handle exceptions during I/O.
- 行为差异: A does simple byte-level copy; B performs DICOM-specific parsing and pixel data manipulation.；A can read from a URL or local file; B only from a local file.；A catches generic Exception; B throws specifically IOException.；B includes console output for progress; A does not.
- 修正建议: Incorporate data flow analysis to trace input-to-output relationships.；Use a model that can recognize high-level I/O patterns across different APIs.；Add more training examples of I/O operations with low token overlap.

### case_id=2158 FN partial_functionality

- 方法: `getContent` vs `lookupFutureEvents`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Performs an HTTP request and returns the response body as a string.
- B 摘要: Fetches event data from a specific API, parses JSON, and returns a list of Event objects.
- 静态失败原因: Low token overlap (Jaccard 0.1087) and different method names, plus the functions diverge significantly after the initial read loop, causing the model to miss the shared high-level pattern of HTTP response reading.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this a clone because both functions share the core operation of making an HTTP request and reading the response line by line into a string, which can be considered a Type-4 (similar functionality) clone despite different overall purposes and output types.
- 共享行为: Reads an HTTP response line by line using BufferedReader and accumulates into a StringBuilder/StringBuffer.
- 行为差异: Function A uses HttpUriRequest; function B constructs URL with groupIdentifier and API key.；Function A returns raw string; function B parses JSON to extract multiple fields and returns List<Event>.；Function B has error handling that throws custom exception; function A throws generic Exception.；Function B processes additional data like dates, addresses, and creates multiple objects.
- 修正建议: Enhance model with dataflow or API usage patterns to recognize common subroutines like HTTP GET + line-by-line reading.；Use graph-based representations that capture structural similarity in control flow (e.g., while-read-append pattern).；Consider functional similarity via analysis of input/output types and library calls.

### case_id=2159 FN benchmark_preference_bias

- 方法: `main` vs `fileCopy`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads KMZ file from a URL and extracts all entries to current directory.
- B 摘要: Copies a file from source to destination with extensive error checking.
- 静态失败原因: Static BERT/GraphCodeBERT correctly identified no clone due to low token overlap, different method signatures, and distinct functionality (download+unzip vs file copy with validation). The model's prediction aligns with strict semantic equivalence.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might consider them clones due to shared low-level I/O patterns (buffer read/write, stream handling) as Type-4, but this is an overly broad interpretation.
- 共享行为: Both perform byte-level I/O using InputStream and OutputStream；Both use a buffer to read/write data in chunks；Both close streams when done
- 行为差异: Function A downloads from a URL and unzips; Function B copies local files with validation；Function A handles HTTP protocol; Function B checks file permissions and existence；Function A uses ZipInputStream; Function B uses plain FileInputStream/FileOutputStream；Function A prints extraction info; Function B aborts on errors
- 修正建议: Train models to distinguish between similar low-level I/O patterns and higher-level semantic intentions；Incorporate understanding of API purpose (e.g., download vs local copy) beyond superficial code structure

### case_id=2160 FN benchmark_preference_bias

- 方法: `main` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a URL and extracts its zip entries to files.
- B 摘要: Writes library license information to a text file based on metadata and extra files in a directory.
- 静态失败原因: Static BERT likely correctly predicted non-clone due to low lexical overlap (Jaccard 0.152) and distinct API usage (URL, ZipInputStream vs File, JarFileFilter). From a BCB perspective, it failed because it didn't recognize the high-level structural similarity that BCB annotators might have valued.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have considered these clones due to both being main methods with similar structure (open stream, loop, write, close) and both involving file I/O, possibly classifying them as Type-4 (similar functionality) despite different domains.
- 共享行为: Both are public static void main methods that write to files using FileOutputStream and BufferedOutputStream.；Both iterate over a collection of items (zip entries or files in a directory).
- 行为差异: Different input sources: URL stream vs local file system.；Different output purposes: extracting archive vs generating license text.；Different data processing: unzipping vs reading metadata properties and extra files.
- 修正建议: Train with more diverse clone types to avoid overemphasizing lexical similarity.；Incorporate functional flow or dataflow analysis to capture high-level similarities even with different APIs.

### case_id=2161 FN benchmark_preference_bias

- 方法: `transferWSDL` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL with optional basic authentication and saves it to a temporary file, returning the file path.
- B 摘要: Launches a NexOpen project configuration by parsing Maven pom files, setting Hibernate dialect properties, copying reverse engineering files if needed, and running an install action.
- 静态失败原因: The static model predicted 0 (non-clone) correctly; the error is a false negative in the benchmark due to an overly lenient BCB label. The model likely recognized the low token overlap and domain-specific APIs as distinguishing factors.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might label this as a clone based on broad Type-4 (partial similarity) or because both functions perform file I/O with stream copying and use similar utility libraries, but the overall semantics are completely different.
- 共享行为: Both use IOUtils to copy streams (IOUtils.copyStream vs IOUtils.copy)；Both handle file I/O and exceptions
- 行为差异: Function A is a simple HTTP download and file save; Function B is a complex Eclipse launch configuration involving project setup, XML parsing, and job scheduling.；Function A deals with WSDL and HTTP; Function B deals with Maven projects, Hibernate, and Eclipse IDE APIs.；Function A is standalone; Function B is tightly coupled to Eclipse framework (ILaunchConfiguration, IProgressMonitor, etc.)
- 修正建议: Re-evaluate the BCB label for this pair; it should be non-clone.；Consider stricter criteria for Type-4 clones to avoid pairing unrelated functions with only superficial API overlaps.

### case_id=2162 FP boilerplate_overlap

- 方法: `readZoneIDs` vs `postRequest`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads integer zone IDs from a resource file and returns them as a set.
- B 摘要: Sends an HTTP POST request with key-value parameters and returns the response body as a string.
- 静态失败原因: Static BERT/GraphCodeBERT may have overemphasized the structural similarity of URL opening, try-catch, and readLine loops, while missing the semantic differences between local file reading and HTTP POST request.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this non-clone because the functions serve entirely different purposes (data parsing vs. network communication), and despite sharing some I/O boilerplate, the core functionality and output types are unrelated.
- 共享行为: Both use try-catch for exception handling；Both use URL to open a connection (A: getResource, B: new URL with openConnection)；Both read lines from an input stream until null；Both use printStackTrace on exception
- 行为差异: A reads from a local resource file; B sends an HTTP POST request to a remote URL；A parses integers; B sends URL-encoded form data and returns concatenated string；A uses LineNumberReader; B uses BufferedReader for reading and PrintWriter for writing；A does not write output; B writes form parameters to the connection output stream
- 修正建议: Train on more diverse I/O examples to distinguish between local reading and network communication；Incorporate dataflow analysis to differentiate input vs. output operations and data types；Use a model that captures longer-range semantic intent, e.g., by focusing on method names and return types

### case_id=2163 FP long_range_semantics

- 方法: `readData` vs `setPayload`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `static_summary_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Parses comma-separated token strings into various sets and maps for character processing, with file reading error handling.
- B 摘要: Appends a file's content to another file using file channels and updates state, then calls methods recursively.
- 静态失败原因: The model likely misidentified superficial similarities (e.g., both have IOException handling or file-related operations) or was confused by the length and truncation of code_a, failing to capture the distinct semantics.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB would label as non-clone because the functions have no shared functionality or similar control flow; they perform completely different tasks with different logic.
- 共享行为: Both are methods that perform I/O operations (reading/writing files)
- 行为差异: A tokenizes strings and populates data structures; B performs file channel transfer.；A uses StringTokenizer and HashSet/Maps; B uses FileChannel and FileOutputStream.；A has complex error handling; B throws IOException without catch.；A is static void; B is instance method returning boolean.
- 修正建议: Provide complete code to avoid truncation issues.；Increase context window or use hierarchical representations.；Train on more diverse negative examples of unrelated file I/O functions.

### case_id=2164 FN benchmark_preference_bias

- 方法: `modifyApplicationMessage` vs `run`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Modifies a property in a locale-specific properties file, creating the file if it doesn't exist by copying English defaults.
- B 摘要: Copies input file to output file, optionally with diagnostic counting of read/written bytes.
- 静态失败原因: Static BERT/GraphCodeBERT likely correctly predicted non-clone because the functions have low lexical overlap (Jaccard 0.155) and structurally different control flows and data manipulations. The model correctly identified they are not semantically equivalent.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as a clone due to the broad commonality of file reading and writing, which could be considered Type-4 (semantic) similarity under a very lenient interpretation of 'functionality' that includes any file-copying or configuration update task.
- 共享行为: Both perform file I/O operations (read and write).
- 行为差异: Function A specifically manipulates .properties files with key-value parsing and modification; Function B copies arbitrary binary/text files.；Function A handles locale-specific file creation and fallback; Function B has optional diagnostic mode with anonymous classes.；Function A uses Properties and StringBuilder; Function B uses streaming with Pump and custom Reader/Writer wrappers.；Function A modifies a single property or appends new; Function B copies entire content without modification.
- 修正建议: Re-evaluate the BCB ground truth for this pair, as the functionality appears dissimilar and likely a misannotation.；If BCB intends such pairs as clones, clarify annotation guidelines to prevent overly broad inclusion.

### case_id=2165 FP lexical_or_api_overlap

- 方法: `readUNI` vs `run`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a tab-separated file from a URL and extracts id and description into a vector.
- B 摘要: Performs an authenticated HTTP GET request and accumulates the response body into a string buffer.
- 静态失败原因: Static models like GraphCodeBERT may over-rely on lexical and API-level overlap (e.g., common patterns: try-catch, InputStream, URL), ignoring the distinct control flow and data handling that differentiate the functions.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would label this as non-clone because the functions perform fundamentally different tasks: one parsing structured file data, the other making an authenticated HTTP request and accumulating raw response.
- 共享行为: Both open an InputStream from a URL；Both read lines from the stream；Both handle exceptions and close resources
- 行为差异: A uses Scanner with delimiters to parse tab-separated fields; B uses BufferedReader and appends entire lines；A adds entries to a Vector; B stores result in a StringBuffer and sets a completion flag；B includes HTTP authentication and sets request method; A does not
- 修正建议: Incorporate dataflow analysis to track how data is processed after reading；Use program slicing or control flow graphs to capture the divergent purposes；Train on datasets with finer-grained functional similarity labels

### case_id=2166 FP long_range_semantics

- 方法: `addToArchive` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.98`
- 推荐路线: `static_summary_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Adds a file entry to a zip output stream from an input stream and returns the URL within the pod archive.
- B 摘要: Handles action events for a settings dialog, processing various configuration changes and updating the GUI accordingly.
- 静态失败原因: Due to the large size of function B (truncated but very long), the model may have relied on superficial token matches (e.g., 'filename', 'file') or been misled by the presence of I/O related terms, but more likely this is a misclassification because of insufficient context or overgeneralization from training data.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely labeled this as non-clone because the functions have completely different purposes and signatures—one is a static archiving method, the other is a GUI action listener—with no semantic overlap beyond basic I/O operations.
- 行为差异: Function A is a simple utility to archive a file; function B is a large event handler for UI settings.；A returns a URL; B does not return anything (void).；A does not involve any GUI or user interaction; B heavily interacts with UI components.；A uses ZipOutputStream and IOUtils; B uses JFileChooser, JOptionPane, etc.
- 修正建议: Improve model's ability to handle very long functions by using hierarchical attention or truncation strategies.；Increase training data for dissimilar long functions to reduce false positives.；Add post-processing to check method signature or type compatibility.

### case_id=2167 FN long_range_semantics

- 方法: `populateResources` vs `httpRequestByPOST`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Loads templates and images from classpath resources, reads their content, and saves them as database objects.
- B 摘要: Makes an HTTP POST request and reads the response body as a string.
- 静态失败原因: Static BERT/GraphCodeBERT likely focused on surface-level tokens (different method names, API calls) and missed the functional similarity of the I/O reading loop pattern.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely considered them clones due to the shared structural pattern of reading from an input stream line-by-line, which is a common I/O idiom, despite different overall functionality.
- 共享行为: Both read from an input stream line by line using BufferedReader and StringBuffer.；Both contain a loop that reads lines and appends them to a buffer.；Both handle IOExceptions.
- 行为差异: A iterates over multiple URLs, while B makes a single HTTP request.；A saves data to a database, B returns the response string.；A also processes images; B does not.；A uses URL.openStream, B uses HttpClient and HttpPost.
- 修正建议: Incorporate dataflow or control flow features to capture long-range structural patterns like I/O read loops.；Use AST-based graph models that can represent loop structures and stream handling.；Augment training data with more examples of similar boilerplate I/O code performing different tasks.

### case_id=2168 FP lexical_or_api_overlap

- 方法: `actionPerformed` vs `saveFileData`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Handles GUI action events for setting various application preferences via file chooser dialogs.
- B 摘要: Saves file data by copying file contents and handling image metadata and cleanup.
- 静态失败原因: The static model may have been misled by the presence of common file I/O API calls (e.g., FileInputStream, FileOutputStream, FileChannel) and the use of variables like 'filename' and 'file', leading to a false positive based on superficial lexical overlap.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels these as non-clones because they serve entirely different purposes: one is a preference settings event handler, the other is a file save utility. There is no functional similarity.
- 共享行为: Both use file I/O APIs such as FileInputStream and FileChannel
- 行为差异: Method A is a GUI event handler that sets preferences based on user interaction; Method B is a utility that copies file data.；Method A uses JFileChooser and updates UI components; Method B does not involve GUI.；Method A handles multiple action commands; Method B handles a single file save operation.；Method B includes thumbnail cleanup and image dimension setting; Method A does not.
- 修正建议: Include structural features like method type (event handler vs utility)；Incorporate data flow analysis to differentiate between GUI interaction and file processing；Use broader context like method signatures and class names to identify different roles

### case_id=2169 FN partial_functionality

- 方法: `makeBackup` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Backs up files from a source directory to a destination directory, copying local files byte-by-byte.
- B 摘要: Retrieves a resource by URL, caching it locally and returning a FileInputStream; uses HTTP conditional GET and buffered copying.
- 静态失败原因: Static BERT likely focused on function names (different), low token overlap (0.208), and distinct high-level structure, missing the shared low-level byte-copy pattern due to limited representation of loop bodies.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider the core file copy loop (read byte, write byte) and directory creation as Type-3/Type-4 similarity, accepting partial functionality overlap even if the overall context differs.
- 共享行为: Both copy bytes from an input stream to an output stream in a loop.；Both create directories if necessary.；Both handle exceptions with printStackTrace.；Both use File and file-related streams.
- 行为差异: makeBackup copies local files only; getResourceAsStream fetches from network resources.；getResourceAsStream implements caching and conditional HTTP requests; makeBackup does not.；makeBackup operates on a list of files in a directory; getResourceAsStream processes a single resource name.；makeBackup modifies file timestamps; getResourceAsStream checks and uses last modified times.
- 修正建议: Incorporate graph-based representations capturing data flow and control flow to recognize shared I/O patterns.；Use contrastive learning with fine-grained syntactic and semantic alignments.；Include program slicing to isolate core copy logic from surrounding context.

### case_id=2170 FN benchmark_preference_bias

- 方法: `downloadURLtoString` vs `invoke`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a URL's content and returns it as a string by reading lines via BufferedReader.
- B 摘要: Performs an HTTP POST invocation, reads the response line by line, parses JSON, and handles retries on timeout.
- 静态失败原因: The static BERT model likely relied on low token overlap (0.14) and clear structural differences, predicting no clone. It failed to align with BCB's broader interpretation that emphasizes a common sub-pattern (reading lines from a stream) even when overall functionality differs.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may label these as Type-4 clones due to partial functional similarity: both eventually read data from a remote source and return a string. However, the differences in protocol, error handling, and purpose make this a borderline case.
- 共享行为: Both read from an InputStream line by line using BufferedReader.；Both build a string by appending lines (A uses StringBuffer, B uses StringBuilder).
- 行为差异: A is a simple GET download; B is a POST RPC with JSON serialization/deserialization.；B includes retry logic, error handling, and method invocation reflection.；A appends lines without newline; B includes newline character then removes last character.；B has much longer and complex logic including URL construction, HTTP client execution, and status checking.
- 修正建议: Train the model to recognize partial functionality similarity at a finer granularity.；Incorporate information about common I/O patterns (e.g., BufferedReader loops) as features.；Adjust the decision threshold or use ensemble of strict and lenient criteria.

### case_id=2171 FN partial_functionality

- 方法: `readRemoteFile` vs `seeURLConnection`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a remote file from a predefined URL and returns its content as a single string.
- B 摘要: Opens a URL connection to a hardcoded URL, reads its content line by line, and logs the result.
- 静态失败原因: Low token overlap (0.237) and differences in method signatures (return type, name) lead the model to focus on surface-level disparities. The model may not capture the shared underlying algorithm of reading a URL line by line due to varied API usage and output handling.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels pairs as clones if they share the same core functionality, even with differences in API usage, error handling, or output destination. Both functions fetch a URL and assemble its text content, which is considered functionally similar.
- 共享行为: Both read from a URL using BufferedReader and InputStreamReader；Both read lines and concatenate them into a single string；Both handle I/O operations
- 行为差异: A returns the string, B logs it (void)；A uses URL.openStream(), B uses URLConnection.getInputStream()；A reads first line separately, B reads all in loop；A has specific exception handling (EOFException), B throws generic Exception
- 修正建议: Train with more diverse implementations of the same functionality；Incorporate structural or control-flow similarity metrics；Use contrastive learning to emphasize semantic equivalence over lexical overlap；Add code summarization models to capture intent

### case_id=2172 FP lexical_or_api_overlap

- 方法: `main` vs `save`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Parses a Prolog file to generate adapters and creates a jar file.
- B 摘要: Saves a byte array to a file.
- 静态失败原因: Static models like GraphCodeBERT may rely on overlapping API usage (File, IOException, streams) and fail to capture the overall program logic and context, causing false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB requires whole-function semantic equivalence for clones; these functions have entirely different purposes, so BCB correctly labels them as non-clone.
- 共享行为: Both involve file I/O operations (reading from or writing to files).
- 行为差异: Function A performs complex command-line parsing, Prolog parsing, adapter generation, and jar packaging.；Function B is a simple utility to copy bytes to a file.
- 修正建议: Improve training data with more diverse non-clone pairs that share APIs but different semantics.；Incorporate dataflow or control-flow analysis to distinguish high-level intention.

### case_id=2173 FP boilerplate_overlap

- 方法: `retrieveQ` vs `SRWGuiClient`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: retrieveQ fetches raw content from a URL and returns it as a string, also printing the HTTP response message.
- B 摘要: SRWGuiClient constructor sets up a Swing GUI, reads URL content, optionally applies XSLT transformation, and displays the result in a JEditorPane.
- 静态失败原因: The model likely overfitted on overlapping boilerplate tokens (e.g., 'URL', 'BufferedReader', 'readLine', 'append') and missed the broader semantic context due to lack of understanding of control flow and overall method purpose.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this non-clone because the functions serve entirely different purposes (utility vs GUI constructor) despite sharing a small code fragment for reading a URL. The overall functionality is too dissimilar.
- 共享行为: Both open a URL and read its content line by line using BufferedReader.
- 行为差异: A is a stateless utility returning a string; B initializes a complex GUI and performs optional XML/XSLT processing.；A uses HttpURLConnection and prints response message; B uses url.openStream() and prints debug info.；A builds output into a StringBuilder with newlines; B uses StringBuffer and may transform XML into HTML.；B has extensive UI setup and event handling; A has no UI.
- 修正建议: Incorporate data flow and control flow features to distinguish utility from UI code.；Use method-level context (e.g., surrounding class name, method name) to capture intent.；Train on more diverse examples of similar boilerplate but different semantics.

### case_id=2174 FP lexical_or_api_overlap

- 方法: `main` vs `getProjectTreeData`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Main method that generates adapter code from Prolog files and outputs a JAR.
- B 摘要: Method that retrieves project tree data from a remote XML file and parses it into a 2D array.
- 静态失败原因: The static model likely relied on lexical or API overlap (e.g., File, URL, XML parsing) and ignored the overall program semantics, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels these as non-clones because they perform completely different tasks with no shared functionality or structural similarity, despite some common API usage.
- 共享行为: Both perform file I/O operations；Both use exception handling (try-catch)
- 行为差异: Function A generates code and writes JAR; Function B reads data and returns a structure；Function A uses Prolog parsing and bytecode generation; Function B uses HTTP and XML parsing；Function A produces output files; Function B returns a string array；Function A has complex control flow with multiple conditional paths; Function B has a linear flow
- 修正建议: Incorporate data-flow and control-flow analysis；Use graph-based code representations to capture intent；Enhance training with more diverse negative examples

### case_id=2175 FN partial_functionality

- 方法: `runScript` vs `doVersionCheck`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches a script file from a URL and returns its content as a string.
- B 摘要: Checks for a newer version of jEdit by fetching a version file from a URL and displaying UI messages.
- 静态失败原因: Low token Jaccard (0.21) and surface-level differences (method names, return types, additional UI code) misled the model; it failed to recognize the shared structural pattern of URL creation, stream opening, and exception handling.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB considers broad Type-3/Type-4 clones where the core functionality (fetching data from a URL via stream reading) is similar, despite differences in purpose, output, and UI interaction.
- 共享行为: Both open a URL connection and read from an InputStream；Both handle exceptions during network I/O；Both perform network resource fetching
- 行为差异: A reads raw bytes into a string; B reads lines and extracts version/build numbers；A returns the fetched data; B updates the UI with version check results；A uses BufferedInputStream; B uses BufferedReader with InputStreamReader；A's error handling sets data to 'error!'; B's error handling shows an error dialog
- 修正建议: Train on more Type-3/Type-4 examples where the clone relation is based on common sub-patterns；Incorporate control-flow or data-flow features to capture the network I/O skeleton；Use a model that better abstracts token variations and focuses on structural similarity

### case_id=2176 FP lexical_or_api_overlap

- 方法: `run` vs `downloadModel`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Downloads a URL with basic auth, reads response line by line into a string, and updates a last interaction timestamp.
- B 摘要: Downloads an RDF model from a URL using Apache Jena, setting custom accept headers, and returns the model.
- 静态失败原因: Static BERT/GraphCodeBERT likely overemphasizes the common API calls (openConnection, getInputStream, setRequestProperty) and the structural pattern of try-catch, while missing the semantic differences in data processing and purpose.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the functionality is too different: one is generic HTTP string fetch, the other is RDF model download, despite both involving URL connection and input stream.
- 共享行为: Both open a URL connection and read from the input stream.
- 行为差异: Function A uses explicit HTTP basic authentication; Function B does not.；Function A reads response as raw text lines; Function B reads and parses RDF model.；Function A stores result in a field and sets a finish flag; Function B returns a Model object.；Function A handles exceptions by storing in a field; Function B throws RuntimeException.
- 修正建议: Use dataflow analysis to differentiate how the input stream is consumed (string vs model).；Consider the method signature and return type as strong signals.；Include more context about the surrounding class and method names.

### case_id=2177 FN partial_functionality

- 方法: `addDataFromURL` vs `testNetworkHTTP`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads content from a given URL line by line and appends each line to a text buffer.
- B 摘要: Performs multiple HTTP GET requests to hardcoded URLs for testing or data exfiltration, reading and discarding response lines.
- 静态失败原因: Low token Jaccard (0.215) and structural differences (simple loop vs. multiple connections) mislead static models. BERT/GraphCodeBERT may focus on local token overlaps and miss the overarching network I/O behavior, while also being thrown off by the hardcoded URLs and logging in B.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely labels this as a clone because both methods involve opening a URL, reading lines with a BufferedReader, and handling exceptions. The core pattern of network I/O and line-by-line reading is considered similar enough under broad Type-3/Type-4 definitions, even though specifics differ.
- 共享行为: Open URL/HTTP connections；Use BufferedReader to read lines from input streams；Handle exceptions with try-catch
- 行为差异: A takes a URL parameter, B uses hardcoded URLs；A appends lines to a buffer, B discards lines；A catches Exception broadly, B catches IOException specifically；A closes InputStream, B disconnects HttpURLConnection
- 修正建议: Train on more diverse Type-3/4 examples with low token overlap；Incorporate dataflow analysis to capture that both read from network streams；Use contrastive learning that rewards similar API call sequences

### case_id=2178 FN partial_functionality

- 方法: `getFile` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies its endpoint, and saves to a local file.
- B 摘要: Copies a file from one path to another using FileChannel.
- 静态失败原因: Low token overlap (0.168) and different APIs/control flow; model likely focused on high-level differences (method name, XML) and missed shared low-level channel transfer pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label as clone because both functions achieve file copying using FileChannel, despite one having additional XML processing; the core data transfer pattern is similar.
- 共享行为: Both use FileChannel for data transfer between I/O streams
- 行为差异: A downloads from network, B from local file；A performs XML manipulation, B does not；A returns file path, B returns void；A has complex error handling, B only IO
- 修正建议: Incorporate finer-grained structural similarity detection (e.g., common sub-patterns like FileChannel usage)；Use dataflow analysis to identify similar I/O operations；Train with contrastive examples of partial functionality clones

### case_id=2179 FN boilerplate_overlap

- 方法: `init` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Initializes a batch report file, including backup and resume logic for existing reports.
- B 摘要: Retrieves a resource as an input stream from a URL, with local caching.
- 静态失败原因: The static BERT model likely relied on token-level overlap and structural patterns; given the low Jaccard similarity (0.14), it correctly predicted non-clone, but BCB's broader annotation preference led to a false positive label.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may have labeled them as clones due to similar boilerplate patterns such as file copying loops, stream management, and exception handling, despite different high-level functionalities.
- 共享行为: Both use BufferedInputStream/BufferedOutputStream for file I/O；Both handle exceptions with try-catch-finally；Both create directories if needed
- 行为差异: A writes XML documents; B reads and caches HTTP resources；A has restart/resume logic; B has cache lookup and HTTP connection handling；A returns void; B returns an InputStream；A uses XMLStreamWriter; B uses URLConnection
- 修正建议: Improve functional semantic understanding by incorporating more context or task-specific representation；Use a more fine-grained clone detection that distinguishes between structural similarity and true semantic equivalence

### case_id=2180 FP lexical_or_api_overlap

- 方法: `getDatasetsList` vs `SRWGuiClient`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches a list of dataset names from a server URL, caching results in a map.
- B 摘要: Constructor for a Swing GUI browser that reads an XML URL, transforms it with XSLT, and displays HTML.
- 静态失败原因: The static model likely focused on lexical and API-level overlap (both use URL, BufferedReader, InputStreamReader, readLine, etc.) and ignored the overall semantic purpose and structure, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled non-clone because the core functionality differs; the only similarity is a common pattern of reading from a URL, which is insufficient for clone detection under BigCloneBench's functional similarity criteria.
- 共享行为: Both read from a URL using BufferedReader and InputStreamReader.；Both handle IOException.
- 行为差异: Function A returns a list of strings; Function B sets up a GUI and displays content.；Function A caches results; Function B does not cache.；Function A throws RuntimeException on error; Function B warns user.；Function B performs complex XML parsing and XSLT transformation, which A does not.
- 修正建议: Incorporate structural or semantic features that capture the overall task type (e.g., data retrieval vs. GUI construction).；Use program slicing to isolate core functionality and ignore boilerplate I/O code.

### case_id=2181 FP lexical_or_api_overlap

- 方法: `run` vs `read`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a tile from a URL, parses it into geometry, and adds it to a data loader.
- B 摘要: Reads a skeleton file from classpath, splits it into sections, and validates section count.
- 静态失败原因: Over-emphasized lexical and API overlaps (url.openStream, BufferedReader, readLine loop) while ignoring higher-level semantic differences.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB considers overall function purpose distinct despite shared I/O patterns, hence non-clone.
- 共享行为: Both read lines from a stream using BufferedReader；Both use URL to open a stream；Both concatenate lines into a string or StringBuilder
- 行为差异: A supports file and HTTP protocols, B only loads from classloader resource；A parses geometry objects, B splits text by delimiter；A has synchronization and writes to data structures, B does not；Different error handling and final usage of data
- 修正建议: Include broader context or class-level information to differentiate purposes.；Use contrastive learning with negative examples that share API usage but differ in semantics.

### case_id=2182 FP lexical_or_api_overlap

- 方法: `main` vs `copy`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Parses a Prolog file and generates adapter classes and serialized adapter layer, writing output to a JAR file.
- B 摘要: Copies the contents of a source file to a destination file using buffered file streams.
- 静态失败原因: The static BERT/GraphCodeBERT model likely overemphasized the lexical and API token overlap (e.g., File, IOException, try-catch, read, write) and similar control structures (if-statements, while-loop), leading to a false positive classification.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB considers these non-clones because they have completely different goals and implementations, with only superficial file-handling token overlap. BCB typically requires some meaningful functional similarity for Type-3/Type-4 clones.
- 共享行为: Both use File objects and check file existence/validity.；Both involve reading from files and handling IOException.；Both use try-catch-finally or similar error handling.
- 行为差异: Function A performs Prolog parsing, class generation, and serialization; Function B only copies bytes.；Function A has complex logic with multiple dependencies (Parser, FactVisitor, ClassWriter, etc.); Function B is a straightforward file copy.；Function A outputs to a JAR file with multiple resources; Function B writes to a single destination file.；Function A handles command-line arguments and debug mode; Function B takes two File parameters.
- 修正建议: Improve representation to capture high-level semantics or dataflow beyond token overlap.；Incorporate structural information such as method dependencies and output types.；Use contrastive learning to discriminate between tasks with overlapping APIs but different purposes.

### case_id=2183 FP lexical_or_api_overlap

- 方法: `save` vs `main`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Saves a list of byte arrays as files and prepends a package declaration to each file by reading and rewriting.
- B 摘要: Main method that parses a Prolog file and generates adapter classes and resources into a JAR file.
- 静态失败原因: Static BERT/GraphCodeBERT may have overemphasized the common file I/O vocabulary (File, FileOutputStream, write, etc.) and missed the entirely different algorithmic structure and purpose.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically marks clones only if functions perform similar tasks with similar logic; here the tasks are completely different despite some file I/O overlap.
- 共享行为: Both perform file I/O operations (reading/writing files)；Both handle directories and file paths；Both use File and IO streams
- 行为差异: Function A saves given byte contents and adds package lines; Function B is a complex code generator for Prolog adapters；Function A is a utility for saving files; Function B is a main entry point for a code generation tool；Function B involves parsing, visitor pattern, class writing, and JAR assembly; Function A does not
- 修正建议: Incorporate more structural information like control flow or data flow；Use more robust models that distinguish boilerplate from core logic

### case_id=2184 FP lexical_or_api_overlap

- 方法: `readTwitterFead` vs `postRequest`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a hardcoded Twitter feed URL via HTTP GET using Apache HttpClient and returns the response body as a string, logging errors.
- B 摘要: Sends an HTTP POST request with URL-encoded form data from a HashMap and returns the response body as a string, returning null on exception.
- 静态失败原因: Static BERT models may have been misled by high lexical overlap of common HTTP terms like 'BufferedReader', 'InputStreamReader', 'readLine', and similar try-catch structure, ignoring the critical differences in HTTP method and library usage.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels non-clones because the functions have different HTTP methods, different libraries, and different error handling strategies, despite both reading HTTP responses into strings. The functional intent is different (one is for reading a specific Twitter feed, the other for generic POST requests).
- 共享行为: Both perform an HTTP request and read the response line by line into a String.；Both use basic HTTP libraries and handle exceptions.
- 行为差异: HTTP method: GET vs POST.；Library: Apache HttpClient vs URLConnection.；URL: fixed vs parameterized.；Error handling: specific status check and logging vs generic exception and return null.
- 修正建议: Improve models to discriminate between GET and POST methods and different HTTP libraries.；Incorporate dataflow analysis to see that one writes data while the other does not.；Augment training with more diverse HTTP client examples.

### case_id=2185 FP boilerplate_overlap

- 方法: `run` vs `getWebByUrl`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Downloads a map tile from a URL, parses its content into vector tile geometry, and adds it to a map data store with duplicate detection.
- B 摘要: Downloads a web page from a URL, saves it to a file, and recursively extracts links for further crawling.
- 静态失败原因: The static BERT/GraphCodeBERT model likely focused on the common structural pattern of URL.openStream() and BufferedReader reading, ignoring the divergent post-processing logic and different high-level purposes.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled this as not a clone because the overall functionality differs greatly: one is a map tile loader, the other a web crawler. The common URL reading idiom is a generic pattern, not sufficient to deem them semantically similar.
- 共享行为: Both open a URL connection and read the input stream line by line.
- 行为差异: A converts content to geometry objects; B writes content to a file and recursively crawls links.；A has duplicate request detection using synchronization; B does not.；A handles file:// protocol; B does not.；B has depth-limited recursion; A does not.
- 修正建议: Train the model to be sensitive to the overall purpose and final output of the function, not just local patterns.；Use data augmentation with negative examples that share boilerplate but differ in semantics.；Incorporate data flow analysis to capture how the input is transformed into the output.

### case_id=2186 FP lexical_or_api_overlap

- 方法: `getJSONData` vs `readUNI`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches JSON data from a URL using HTTP GET and parses it into a JSONObject.
- B 摘要: Reads tab-separated data from a URL and populates a Vector with extracted fields.
- 静态失败原因: Static BERT/GraphCodeBERT may have focused on lexical overlap (URL, InputStream, reading lines, try-catch) and similar boilerplate structure, missing the semantic difference in data processing and output.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels as non-clone because the functions have completely different purposes (JSON parsing vs tab-delimited parsing) and different return types and side effects.
- 共享行为: Both open a URL and read character data line by line；Both handle exceptions
- 行为差异: A returns a JSONObject, B modifies an input Vector and returns void；A uses HttpClient, B uses URL.openStream；A reads entire response into a single string then parses JSON, B parses each line as tab-separated fields；A does not close the InputStream in finally, B does
- 修正建议: Use more discriminative features like return type, method signature, and data flow；Incorporate control flow and data transformation differences to avoid false positives due to common API usage

### case_id=2187 FP boilerplate_overlap

- 方法: `getJSONData` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches a JSON object from a given URL using HTTP GET with Apache HttpClient.
- B 摘要: Searches Google Images for the current artist and album, parses HTML to extract image URLs.
- 静态失败原因: Static BERT/GraphCodeBERT may overemphasize the overlapping boilerplate code (HTTP connection, reading lines) and ignore the distinct high-level semantics.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels these as non-clones because the overall functionality is completely different (JSON retrieval vs. image search) despite sharing similar I/O boilerplate.
- 共享行为: Both perform an HTTP GET request；Both read response line by line using BufferedReader；Both handle exceptions and close the reader
- 行为差异: A returns a JSONObject; B is void and populates a list；A uses Apache HttpClient; B uses HttpURLConnection；B has additional logic for constructing query and checking artist change；A parses JSON; B parses HTML to extract image links
- 修正建议: Incorporate data-flow analysis to track how the response is used；Add attention to method signatures and return types；Use graph-based representations that capture the overall computation flow

### case_id=2188 FP lexical_or_api_overlap

- 方法: `onlyFileCopy` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Copies a file using NIO FileChannel transferTo.
- B 摘要: Handles GUI actions for a settings dialog, processing multiple commands like GRAPHVIZ, IMAGEMAGICK, etc.
- 静态失败原因: Static BERT likely over-relied on lexical/API overlap (e.g., File, IOException, try-catch) while missing the huge semantic gap between a focused file copy utility and a broad GUI event handler.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels as non-clone because functions have entirely different purposes and no shared functionality beyond trivial API usage.
- 共享行为: Both use File and IOException；Both have try-catch-finally blocks
- 行为差异: A performs file I/O; B handles GUI events and writes preferences；A has a single-purpose algorithm; B has a long multi-branch event handler；A uses NIO channels; B uses Swing components and file choosers
- 修正建议: Incorporate control flow and long-range dependency awareness；Use dataflow or program graphs to better capture intent；Downweight surface-level API matches when overall structure differs drastically

### case_id=2189 FN partial_functionality

- 方法: `copyResource` vs `testTrainingBackprop`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource from a URL or file to a destination file.
- B 摘要: Creates a temp file, copies a classpath resource to it, then trains a neural network with that data and checks error.
- 静态失败原因: Low token overlap (0.075) and different structure/length; surface-level features did not capture the common sub-functionality of resource copying.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have annotated as clone because both functions involve copying a file resource to an output, which is a shared sub-functionality that aligns with broad Type-3/Type-4 clone criteria.
- 共享行为: Both copy a file resource to an output file.
- 行为差异: Function A reads from URL or existing file; B reads from classpath.；Function A writes to specific destination; B writes to temp file.；Function A only copies; B proceeds to train a neural network.；Function A uses manual byte-by-byte copy; B uses IOUtils.copy.
- 修正建议: Train with examples of partial clones where only part of functionality overlaps.；Incorporate structure-aware features like control flow for I/O operations.；Use models that handle long-range dependencies and different implementations.

### case_id=2190 FN partial_functionality

- 方法: `login` vs `issueCommandToServer`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Logs into LOLA by sending email and password via HTTP POST, extracts session ID from first response line.
- B 摘要: Issues a command to a server with a ChangeCapsule via HTTP POST, reads full response as string.
- 静态失败原因: The model relied on surface-level features like method names, variable names, and token Jaccard similarity (0.25), missing the common structural pattern of HTTP POST boilerplate. It was misled by different semantics (login vs command) and specific parameter handling.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often annotates functions with the same abstract functionality (e.g., 'make HTTP POST request') as clones, even if details differ. Both functions implement the same pattern of sending URL-encoded data over HTTP POST and reading a response, making them Type-4 functional clones.
- 共享行为: Both perform HTTP POST requests with URL-encoded parameters.；Both open a URL connection, set DoOutput to true, write data, flush, read response, and close streams.
- 行为差异: A reads only the first response line for session ID; B reads all lines into a StringBuffer.；A has exception handling that prints error and returns empty string; B throws IOException.；A does not set Content-Type header; B sets 'application/x-www-form-urlencoded'.；A uses hardcoded URLs; B uses a serverURL variable.
- 修正建议: Train model to recognize common structural patterns (e.g., HTTP POST sequence) despite different variable names.；Incorporate dataflow analysis to capture the same sequence of operations.；Use structural similarity metrics like tree edit distance or AST-based comparison.

### case_id=2191 FP boilerplate_overlap

- 方法: `read` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads camera log data from a URL, parses each line into structured CameraLogRecord objects, adds them to a list, sorts the list, and logs progress.
- B 摘要: Searches Google Images by constructing a URL, reads HTML response, extracts image URLs starting with http/https, stores them in a list, and displays the first image in a GUI.
- 静态失败原因: The static model may have been misled by high lexical overlap of common I/O tokens (e.g., URL, BufferedReader, readLine, close, try, catch) and similar control flow structures, failing to capture the distinct functional logic and different output/error handling.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels this as non-clone because the functions serve different high-level purposes (log processing vs image retrieval) and the shared code is generic I/O boilerplate, not indicative of semantic equivalence.
- 共享行为: Open a URL connection and create a BufferedReader；Read input line by line in a loop；Handle exceptions with catch blocks；Close the reader in a finally block
- 行为差异: Function A reads camera log data; B reads Google Images HTML；Function A parses each line as a CameraLogRecord; B parses HTML to extract image URLs；Function A sorts the records; B does not sort but updates a GUI；Function A uses logging; B uses error dialogs and GUI updates
- 修正建议: Incorporate dataflow analysis to track how input is parsed and output is used；Use a model that captures task-specific semantics (e.g., logging vs image extraction)；Include structural differencing of loop bodies and method call chains

### case_id=2192 FN partial_functionality

- 方法: `doGet` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Servlet doGet method that handles HTTP GET requests to display a page, with authentication, caching, and logging.
- B 摘要: Main method that reads a dataset from a zip file, evaluates rule lists, and prints performance metrics.
- 静态失败原因: Static models rely on token overlap and structure; these functions have low Jaccard similarity and use completely different APIs, so embeddings are far apart. The broad functional similarity is not captured by token-level or simple AST representations.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may view both as 'main entry points' that read input, process, and output results, fitting a broad Type-4 semantic clone pattern despite differing domains.
- 共享行为: Both read input (HTTP request vs. zip entries)；Both perform conditional logic and exception handling；Both produce output (HTTP response vs. console prints)；Both use file I/O and logging
- 行为差异: Completely different domain: web page serving vs. batch data evaluation；Different control flow: one serves a single request, the other iterates over multiple files；Different APIs and libraries used (Servlet vs. file I/O streams)；Different output formats and purposes
- 修正建议: Incorporate behavioral similarity metrics based on input-output transformations；Use cross-domain pre-training or contrastive learning to capture high-level semantic patterns；Focus on control flow and data flow abstraction rather than API tokens

### case_id=2193 FP boilerplate_overlap

- 方法: `getHash` vs `perform`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Computes MD5 hash of a URI string and returns hex string.
- B 摘要: Processes a web form request, interacts with session, builds XML, sends HTTP request, parses response, and returns an ActionForward.
- 静态失败原因: The model likely focused on surface-level similarities like loops and StringBuffer usage, ignoring the vast semantic differences and low lexical overlap.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels non-clones when functions have completely different functionality and minimal code overlap, as here.
- 共享行为: None
- 行为差异: Function A is a simple utility for hashing; function B is a complex web controller.；Function A has no side effects; function B modifies session and outputs.；Function A returns a String; function B returns an ActionForward.；Function A uses MessageDigest; function B uses URLConnection and XML parsing.
- 修正建议: Improve model sensitivity to overall function purpose and data flow.；Incorporate more structural and semantic similarity metrics.；Augment training data with contrasting examples of complex vs. simple methods.

### case_id=2194 FN partial_functionality

- 方法: `copyFile` vs `modifyApplicationMessage`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.75`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a file from input to output using FileChannel.
- B 摘要: Modifies a locale-specific properties file by reading, parsing, and writing lines; conditionally copies a base file if target does not exist.
- 静态失败原因: Static BERT likely relied on low token overlap (0.15) and different method names, missing the shallow file-copy similarity that BCB emphasizes.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label these as clones due to both containing file-copy logic (B includes a copy step), albeit in different contexts, possibly considered a Type-3 partial functionality overlap.
- 共享行为: Both perform file I/O operations；Both can copy a file (B conditionally)
- 行为差异: A is a straightforward binary copy; B involves text parsing, property replacement, and conditional file creation；A uses NIO transferTo; B uses character streams；A takes two File objects; B takes strings and manages multiple files；B modifies content based on parameters; A does no modification
- 修正建议: Incorporate data-flow or control-flow analysis to detect sub-task overlaps；Add heuristics to consider conditional file-copy within larger functions as relevant；Use hierarchical semantic matching to identify reuse of patterns

### case_id=2195 FN benchmark_preference_bias

- 方法: `sendExceptionToServer` vs `setMembers`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Encodes and sends exception details to a remote server via HTTP POST and awaits a response.
- B 摘要: Fetches an HTML page from a Trac URL and parses select element options to populate component and priority arrays.
- 静态失败原因: Static BERT/GraphCodeBERT correctly identified the low token overlap and different domain-specific terms (e.g., 'exception', 'secret' vs 'trac', 'component'), leading to a non-clone prediction that aligns with functional semantics but not with the likely erroneous BCB label.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled as clone due to shared patterns of network I/O and exception handling, which are common boilerplate but not indicative of semantic equivalence.
- 共享行为: Both perform HTTP requests using java.net.URL；Both read from an InputStream using BufferedReader；Both catch IOException for error handling
- 行为差异: Function A sends data (POST) while Function B only receives (GET)；Function A builds a complex URL-encoded string of parameters; Function B parses HTML select tags；Function A uses OutputStreamWriter to write request body; Function B only reads；Function A processes an exception stack trace; Function B uses regex to extract text from HTML
- 修正建议: Re-evaluate BCB annotations for false positives, especially those relying on boilerplate overlap；Use more precise functional similarity metrics that focus on input-output behavior rather than structural patterns

### case_id=2196 FN partial_functionality

- 方法: `httpRequestByPOST` vs `doVersionCheck`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends an HTTP POST request with parameters and returns the response body as a string or null on error.
- B 摘要: Opens a URL from jEdit property, reads lines to extract version info, and calls another method to handle version check with error dialog.
- 静态失败原因: Low token Jaccard and different method names/API calls led to high surface-level dissimilarity, masking the shared HTTP request-response structure.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB annotators may consider Type-4 clones as those sharing a common pattern of HTTP request and line-by-line reading, despite differences in input/output processing.
- 共享行为: Both open an HTTP connection and read the response line by line.；Both handle IOException with error handling.
- 行为差异: A returns the full response string; B extracts specific lines and calls another method.；A uses POST with params; B uses GET with a fixed URL.；A sets error fields; B shows error dialog.；A has an unused timeout parameter.
- 修正建议: Use graph-based models capturing data dependencies.；Train with contrastive learning on functional behavior rather than lexical overlap.

### case_id=2197 FN benchmark_preference_bias

- 方法: `getFile` vs `createOutputStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.8`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies the endpoint attribute, and saves it to a temporary file, returning the file path.
- B 摘要: Reads a zip file, copies all entries except content.xml, then adds a new content.xml entry, and returns a BufferedWriter for the output zip.
- 静态失败原因: Static BERT likely failed because it captured the low lexical overlap (Jaccard 0.094) and lack of common keywords, but missed the potential functional similarity at a very high level that BCB might have considered.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might have labeled them as clones due to broad Type-4 criteria, considering both as 'file transformation' tasks with similar boilerplate structures like try-catch, file creation, and stream handling, despite different domains.
- 共享行为: Both perform file I/O operations involving reading and writing files.；Both handle exceptions and use logging/error throwing.
- 行为差异: A downloads from a remote URL, while B reads a local zip file.；A modifies XML content, while B filters and rewrites zip entries.；A returns a file path, while B returns a BufferedWriter.；A uses NIO channels and XML parsing, while B uses character streams and zip processing.
- 修正建议: Enhance training with more diverse partial-functionality examples.；Incorporate task-level semantic understanding beyond local code structure.；Use cross-module context or API documentation to disambiguate file processing tasks.

### case_id=2198 FP boilerplate_overlap

- 方法: `run` vs `getFrameworkFactory`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Executes an HTTP GET request with basic authentication and reads the entire response into a string.
- B 摘要: Reads a service configuration file from the classpath to instantiate an OSGI FrameworkFactory.
- 静态失败原因: The model likely over-relied on common structural patterns (BufferedReader, InputStreamReader, URL, while loop) and API usage, mistaking them for similar functionality without understanding the distinct business logic or unique APIs (HttpURLConnection vs Class.forName).
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels these as non-clones because the overall functionality is completely different: HTTP client vs OSGI service loader. Despite sharing some I/O boilerplate, the semantic purpose and output are unrelated.
- 共享行为: Both open a connection to a URL resource.；Both read lines of text from an input stream using BufferedReader.；Both close the stream in a finally block or after use.；Both handle exceptions (one catches Throwable, the other throws Exception).
- 行为差异: Function A performs an HTTP GET with authentication; Function B reads a service descriptor file.；Function A stores the response in a member variable and sets a flag; Function B returns an object.；Function A uses BASE64Encoder for encoding; Function B uses Class.forName and newInstance.；Function A updates a timestamp; Function B does not.
- 修正建议: Incorporate intent-aware representations by focusing on function outcomes (e.g., return type, side effects).；Use contrastive learning with negative pairs that share I/O boilerplate but differ in purpose.；Emphasize distinctive API calls (e.g., setRequestMethod vs Class.forName) to reduce false positives.

### case_id=2199 FN partial_functionality

- 方法: `runInternal` vs `httpRequestByPOST`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches OPDS catalog or downloads a book via HTTP GET with pagination and progress callbacks.
- B 摘要: Performs an HTTP POST request with form parameters and returns the response body as a string.
- 静态失败原因: Static BERT models may rely on token overlap or structural similarity; since these functions have low token overlap and different control flow, the model predicted non-clone. The behavioral similarity (both HTTP) is not captured by surface features.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely labels as clone because both functions are HTTP client implementations that perform a request and handle the response, despite different HTTP methods and libraries.
- 共享行为: Both make HTTP requests and handle the response.
- 行为差异: A uses java.net.HttpURLConnection with GET; B uses Apache HttpClient with POST.；A includes OPDS parsing and book downloading; B returns response string.；A has progress updates and callback on finish; B sets error codes.
- 修正建议: Use data flow analysis to identify network I/O patterns.；Consider fine-tuning on BCB with more diverse HTTP functions.

### case_id=2200 FN partial_functionality

- 方法: `getButtonSonido` vs `doGet`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Creates a button that opens a file chooser to select and copy a sound file, then updates the button icon and plays the audio.
- B 摘要: Handles HTTP GET request to retrieve and serve a page, with permission checks, logging, and caching.
- 静态失败原因: Static BERT models may have relied on structural patterns (try-catch, file operations) and common keywords (file, IOException) while ignoring the high-level context (GUI vs web server). The low token Jaccard suggests they are not lexically similar, so the model might have underfitted to the correct distinction.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have considered both as 'file I/O with logging' patterns, but the actual functionality is fundamentally different. The label 1 is likely an annotation error or a very broad interpretation of Type-3/4 similarity.
- 共享行为: Both perform file I/O operations (copying/creating files).；Both include logging (System.out vs myLogger).；Both handle exceptions with try-catch blocks.
- 行为差异: A is a GUI component method for sound selection; B is a servlet method for page retrieval.；A uses Swing and Java NIO FileChannel; B uses HTTP request/response and JSP.；A is event-driven (action listener); B is request-driven (HTTP GET).；A returns a JButton; B is void.
- 修正建议: Improve training data to emphasize high-level program intent.；Incorporate data flow or call graph analysis to distinguish UI vs server contexts.；Use domain-specific features (e.g., Swing vs Servlet API usage).

### case_id=2201 FP lexical_or_api_overlap

- 方法: `handleHandshake` vs `import_hints`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Validates Minecraft server handshake by checking username and performing HTTP authentication.
- B 摘要: Imports hint pieces from a file/URL, parsing tokens and placing pieces on a board.
- 静态失败原因: The static model likely focused on the presence of similar API calls (URL, BufferedReader, try-catch) and overlooked the vast difference in control flow and domain logic, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled as non-clone because the functions are from completely different domains (network vs puzzle) with minimal syntactic overlap and no semantic similarity.
- 共享行为: Both use URL and BufferedReader to read data from a network resource.
- 行为差异: Different purpose (authentication vs puzzle setup)；Different input parsing；Different error handling；Different return types (void vs boolean)
- 修正建议: Include more context-aware embeddings that capture control flow and domain semantics；Use graph-based models that encode data dependencies

### case_id=2202 FN benchmark_preference_bias

- 方法: `copyResource` vs `convert`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Copies any resource (URL or file) to a destination file byte by byte.
- B 摘要: Converts an ACRNEMA DICOM file to standard DICOM with metadata injection and pixel data handling.
- 静态失败原因: The static BERT method correctly predicted non-clone because the token overlap is low (12.8%) and the semantic embeddings likely diverged due to very different domain-specific terms (e.g., DICOM tags, pixel data) vs. generic resource copy. The model did not fail; rather, the BCB label may be incorrect for strict clone detection.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled these as clones due to the broad structural similarity of reading from an input source and writing to an output file, ignoring the vast difference in domain-specific logic and method purpose.
- 共享行为: Both open an input stream and an output stream.；Both read bytes from input and write to output.；Both close streams in a finally block or after copying.
- 行为差异: A is generic byte copy; B involves DICOM parsing, tag detection, and conditional pixel data inflation.；A handles URL resource loading; B only handles FileInputStream from a File object.；B adds DICOM UIDs and other metadata; A has no such manipulation.；B contains extensive domain-specific error checking and logging; A only throws a generic exception if resource missing.
- 修正建议: Re-evaluate BCB annotations for broad structural clones; consider excluding generic IO patterns from clone labels.；Improve model to ignore trivial structural overlap when domain-specific logic differs significantly.

### case_id=2203 FN benchmark_preference_bias

- 方法: `readData` vs `executeHttpGet`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Parses multiple comma-separated token strings into sets and maps for character mapping initialization.
- B 摘要: Executes an HTTP GET request and parses the response into a JSONObject.
- 静态失败原因: Static model correctly identified non-clone; BCB label is questionable, so model didn't fail.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have considered both as 'reading data' operations, but this is overly broad and not standard for clone detection.
- 行为差异: Source of data: one reads from static strings, the other from HTTP responses.；Data processing: one tokenizes and stores in sets/maps, the other builds a string and parses JSON.；Return type: void vs JSONObject.；Exception handling: one catches IOException, the other throws Exception.
- 修正建议: Review BCB annotation for this pair; likely mislabeled.；Use more discriminative models or augment with type/return information.

### case_id=2204 FN partial_functionality

- 方法: `copyResource` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource from a URL or local file to a destination file using byte-by-byte stream copy.
- B 摘要: Launches an Eclipse launch configuration by validating project structure, processing XML files, copying a reverse engineering file from bundle if needed, and scheduling an install action.
- 静态失败原因: Static BERT likely failed due to low token overlap (Jaccard 0.07) and vastly different method names and domain-specific terms, causing the model to focus on the overall structural differences and miss the embedded copy sub-task.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considers both functions as clones because they share a core copy operation from an input resource to an output, despite the complex surrounding context in B. BCB annotation often tolerates Type-3/4 similarities based on partial functionality.
- 共享行为: Both involve reading from an input stream and writing to an output stream, effectively copying data from a source to a destination.
- 行为差异: Different sources and destinations: A copies from URL/local file to file; B copies from bundle resource to ByteArrayOutputStream then to file.；B includes extensive validation, XML processing, property setting, and job scheduling, while A is a simple copy without additional logic.
- 修正建议: Improve detection of sub-tasks and functional patterns like stream copy.；Incorporate dataflow analysis to capture input-output relationships.；Use contrastive learning to focus on core behavior rather than lexical context.

### case_id=2205 FP lexical_or_api_overlap

- 方法: `readVersion` vs `getTicketsForQueue`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads version information from a classpath resource file.
- B 摘要: Fetches ticket IDs for a queue from a remote REST API and retrieves full tickets.
- 静态失败原因: Static models over-emphasized lexical overlap (BufferedReader, readLine, startsWith) and missed the semantic context: one reads a local file, the other makes an HTTP request. The method names and surrounding class context were not fully leveraged.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BigCloneBench typically considers functions performing distinctly different tasks (local resource parsing vs. remote API ticket query) as non-clones despite shared IO boilerplate patterns.
- 共享行为: Use BufferedReader and InputStreamReader to read line-by-line；Parse lines using startsWith and split；Handle possible exceptions with try-catch-finally
- 行为差异: Source of data: local resource vs. HTTP response；Parsing patterns: Version=, Revision=, Date= vs. ticket/；Output: sets object fields (version, revision, compileDate) vs. returns List<RTTicket>；Complexity: simple file read vs. multi-step HTTP request and ticket retrieval
- 修正建议: Incorporate method name and class-level context as features；Use data flow analysis to distinguish local resource access from remote HTTP calls；Incorporate AST or token-type differences to penalize unrelated API usage

### case_id=2206 FN boilerplate_overlap

- 方法: `sendExceptionToServer` vs `populateResources`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.7`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends exception details to a server via HTTP POST, encoding various parameters.
- B 摘要: Populates application resources by loading template files and images from classpath and saving them.
- 静态失败原因: Static model correctly predicted non-clone based on low token overlap and different semantics; BCB label is overly broad.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB might have labeled them as Type-4 clones due to a broad pattern of I/O and exception handling, though functionality differs completely.
- 共享行为: Both use URLs and I/O streams with BufferedReader；Both have try-catch blocks for IOException
- 行为差异: A sends data over network; B reads from local classpath resources；A uses HTTP connection; B uses resource URLs from classpath；A's goal is error reporting; B's is application initialization
- 修正建议: Ensure training data distinguishes between functional and boilerplate similarity；Use more fine-grained functional tags or consider dataflow analysis

### case_id=2207 FP boilerplate_overlap

- 方法: `readAndRewrite` vs `main`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a DICOM file, parses it, reads pixel data, and writes the dataset to an output file.
- B 摘要: Parses a Prolog file, generates adapter classes, and creates a JAR file with serialized adapter layer.
- 静态失败原因: The model likely overemphasized superficial commonalities like file I/O (FileInputStream, FileOutputStream) and exception handling patterns, while ignoring the vastly different domain-specific APIs and logic. Low token Jaccard suggests the model's attention was misled by similar structural elements, but overall semantics are orthogonal.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels these as non-clones because they implement completely different algorithms and have no semantic similarity in functionality. Even under broad Type-4 clone definition, they are not considered clones as they serve entirely different purposes.
- 共享行为: Both perform file I/O operations；Both use exception handling with try-catch blocks；Both print status messages to console
- 行为差异: Function A processes DICOM medical images; Function B generates Java adapters from Prolog；Function A uses ImageIO and DICOM-specific libraries; Function B uses Prolog parser and class generation libraries；Function A is a helper method; Function B is the main entry point
- 修正建议: Improve model's ability to focus on core logic rather than surrounding boilerplate；Incorporate more structural or dataflow information to distinguish between different application domains；Use contrastive learning with harder negative samples that share boilerplate but differ in semantics

### case_id=2208 FP lexical_or_api_overlap

- 方法: `doVersionCheck` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads version information from a remote URL and calls another version check method.
- B 摘要: Searches Google Images for a query, extracts image URLs, and displays the first image.
- 静态失败原因: The static model likely overemphasized common API usage patterns (e.g., URL, openStream, BufferedReader, while loop) and ignored the domain-specific semantics and high-level purpose differences.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clones when functions implement entirely different functionalities despite sharing some structural patterns. Here, the core tasks are version checking vs. image search, which are semantically unrelated.
- 共享行为: Both open a URL and read data from the input stream using BufferedReader.；Both iterate over lines read from the stream.；Both handle exceptions and show error dialogs.；Both perform some UI-related operations (cursor change / button enable).
- 行为差异: Function A checks jEdit version by parsing specific line prefixes; Function B scrapes Google Images HTML to extract image URLs.；Function A calls another method with version strings; Function B populates a list and updates UI components.；Function A uses a property-based URL; Function B constructs a URL from parameters.；Function A handles IOException only; Function B catches generic Exception and also MalformedURLException separately.
- 修正建议: Incorporate dataflow or control-flow analysis to distinguish different computation goals.；Use task-specific fine-tuning with examples of boilerplate code vs. functional core.；Leverage AST-based models that capture structural differences beyond token sequences.；Add semantic role labeling to identify what the function accomplishes at a high level.

### case_id=2209 FP lexical_or_api_overlap

- 方法: `loadMFileViaWeb` vs `loadURL`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Loads an M-file from a web URL, reads its content as a string, parses it into a UserFunction, and returns it.
- B 摘要: Downloads a file from a URL with optional authentication, writes it to a temporary file, and updates a status label with download progress.
- 静态失败原因: The static BERT/GraphCodeBERT model likely overemphasized the lexical overlap of URL reading (openStream, BufferedReader, readLine) and missed the distinct output behaviors and contexts (parsing vs file writing + GUI update).
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the overall functionality is different: one is for loading M-files, the other for downloading files with progress tracking. The shared URL reading pattern is considered insufficient for clone labeling.
- 共享行为: Both open a URL connection and read the response line by line using BufferedReader.
- 行为差异: Function a returns a parsed UserFunction object; function b writes to a temp file and updates a GUI label.；Function a does not handle authentication; function b supports basic auth.；Function a throws a generic exception and logs; function b throws IOException and uses stdout.；Function a concatenates lines into a single string; function b writes each line to a file.
- 修正建议: Improve model sensitivity to structural differences beyond common I/O patterns.；Incorporate data-flow or program-dependence analysis to distinguish different uses of read data.

### case_id=2210 FP lexical_or_api_overlap

- 方法: `handleHandshake` vs `addQDInformation`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Processes a Minecraft handshake packet by validating the username and either sending a login packet or shutting down the connection based on server authentication.
- B 摘要: Updates project information by reading a local or remote QD info file and parsing date and value entries.
- 静态失败原因: The model over-relied on lexical and API-level similarities (e.g., URL, BufferedReader, parsing loops) while ignoring the distinct semantics and context of each function.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clone because the functions are from different domains and have no functional similarity; they serve entirely different purposes.
- 共享行为: Both use BufferedReader to read from an input stream；Both perform string parsing on read lines；Both use try-catch for exception handling
- 行为差异: Different purpose: handshake authentication vs. project data update；Different inputs: packet vs. no arguments (relying on internal state)；Different parsing formats: hex username vs. 'pg' and 'pt' lines；Different outcomes: sending packet vs. updating info objects
- 修正建议: Use dataflow or control-flow aware models；Incorporate method-level context such as class or package；Apply contrastive learning with more diverse non-clone pairs

### case_id=2211 FP boilerplate_overlap

- 方法: `getJSONData` vs `executePost`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches JSON data via HTTP GET using Apache HttpClient and parses to JSONObject.
- B 摘要: Sends HTTP POST request with parameters and returns response as string using HttpURLConnection.
- 静态失败原因: Static BERT likely overemphasized lexical overlap in boilerplate HTTP handling code (BufferedReader, InputStream, try-catch) and missed the key differences in HTTP method, library, and return type.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB emphasizes functional equivalence; the core tasks (GET+JSON parsing vs POST+raw response) are different, so labeled non-clone.
- 共享行为: Both perform HTTP requests and read response line by line；Both handle exceptions by printing stack trace and returning null
- 行为差异: HTTP method: GET vs POST；Library: Apache HttpClient vs java.net.HttpURLConnection；Return type: JSONObject vs String；Input: only URL vs URL and parameters
- 修正建议: Incorporate method signature and return type information；Use dataflow analysis to distinguish library usage and HTTP method；Add attention to input/output types

### case_id=2212 FN benchmark_preference_bias

- 方法: `testCopy_readerToOutputStream_Encoding` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: A test method that copies a reader to an output stream with a specified encoding and verifies the content matches the original input data.
- B 摘要: A method that retrieves a resource as an input stream by fetching from a URL, caching it locally, and returning the cached file stream, with HTTP handling and error recovery.
- 静态失败原因: Static BERT likely failed to detect this as a clone because the functions have very low token overlap (Jaccard=0.0776) and no shared identifiers or structural patterns, leading it to correctly predict non-clone in terms of strict equivalence, but BCB's broad preference considered them similar based on stream handling.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled these as clones due to a lenient interpretation of Type-4 (semantic similarity) where both functions handle stream copying or I/O operations, despite vastly different contexts and goals.
- 共享行为: Both involve input/output stream operations
- 行为差异: Function A is a test with hardcoded data and assertion; Function B is a production method with URL fetching, caching, and error handling；Function A copies data with encoding conversion; Function B downloads and caches resource files；Function A has no caching or network interaction; Function B has complex caching logic and HTTP connection management；Function A returns void; Function B returns an InputStream
- 修正建议: Include additional context-aware features that capture domain similarity (e.g., stream handling) beyond lexical overlap；Train with more diverse examples of BCB-style broad clones to adjust threshold；Use hierarchical or task-specific similarity measures that align with benchmark labeling criteria

### case_id=2213 FN partial_functionality

- 方法: `getFile` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies its endpoint attribute, and saves it to a temporary directory.
- B 摘要: Downloads a KMZ (zip) file from a URL, extracts its entries, and writes them to disk.
- 静态失败原因: Static BERT models rely on token and structural similarity, which is low here (Jaccard=0.15), and they miss the shared high-level behavior of downloading and saving files due to different method names and control flow.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely labels these as clones because both functions download a file from a URL and write it to disk, representing a high-level functional similarity (Type-4) despite different specific processing tasks.
- 共享行为: Both open an HTTP connection to download a file using URL.openStream()；Both write downloaded data to local files using FileOutputStream；Both handle potential IOExceptions
- 行为差异: A modifies the downloaded XML document (WSDL) before saving, while B extracts a zip archive；A returns the file location string, while B is void and prints progress；A uses NIO channels for efficient transfer, B uses buffered streams；A has specific error handling for AxisFault, B only throws generic Exception
- 修正建议: Enhance model to recognize I/O operations and external API patterns (e.g., URL.openStream, FileOutputStream) as indicators of similar functionality.；Incorporate program dependency graphs that highlight data flow across file operations.；Use contrastive learning on partial clone pairs to improve sensitivity to high-level task similarity.

### case_id=2214 FN partial_functionality

- 方法: `runInternal` vs `CheckUrl`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.5`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads and parses OPDS catalog entries, handling pagination and book downloads with progress reporting.
- B 摘要: Fetches the first line of an HTTP response from a URL and returns it as a string.
- 静态失败原因: Static BERT models often rely on token-level similarities and structural patterns. The low token Jaccard (0.075) and large difference in code length make it hard for them to recognize any deep functional similarity. Additionally, the common elements (HttpURLConnection, URL, etc.) are overshadowed by the different implementations and the long-range dependencies in code A.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB might have labeled this as a clone because both functions perform an HTTP GET request using HttpURLConnection, and they share a basic pattern of URL connection and input reading. However, the complexity and purpose differ greatly, so it is likely a false positive in BCB annotation.
- 共享行为: Both use HttpURLConnection to open a URL and handle input streams.；Both handle exceptions related to network operations.
- 行为差异: A is significantly more complex, handling redirects, headers, pagination, file downloads, and progress callbacks; B simply reads one line.；A manages state across multiple requests (loadNext loop) and handles OPDS-specific metadata; B is a one-off request.；A has a callback mechanism for results; B returns a string directly.
- 修正建议: Use dataflow analysis that tracks the use of HttpURLConnection and input streams across functions.；Incorporate more detailed API call patterns and context to distinguish simple use from complex orchestration.；Consider the overall purpose by analyzing method names and surrounding code semantics.

### case_id=2215 FP lexical_or_api_overlap

- 方法: `executeHttpGet` vs `loadURL`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Executes an HTTP GET request and returns the response body as a JSONObject.
- B 摘要: Loads a URL with optional basic auth, reads the response, writes it to a temporary file, and updates a status label.
- 静态失败原因: The static BERT model likely overemphasized the lexical overlap (e.g., 'BufferedReader', 'readLine', 'while') and the similar API call pattern (HTTP request and response reading), while ignoring the significant differences in return types, parameters, and side effects.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely marked this as non-clone because the functions serve entirely different purposes (fetching JSON vs downloading a file with UI feedback) despite sharing a common pattern of reading HTTP responses line by line.
- 共享行为: Both open an HTTP connection and read the response line by line using BufferedReader.
- 行为差异: Function A returns a JSONObject; Function B writes to a file and has no return value.；Function A uses HttpGet and DefaultHttpClient; Function B uses URLConnection.；Function B implements basic authentication, writes to a temporary file, updates a UI label, and prints debug messages.；Function A is a simple fetch; Function B has complex side effects including file I/O and UI updates.
- 修正建议: Improve the model's ability to distinguish between different types of I/O operations and side effects.；Train on more diverse examples where similar low-level patterns serve different high-level purposes.；Incorporate data-flow analysis to track return values and side effects.

### case_id=2216 FN partial_functionality

- 方法: `getWebPage` vs `readGeoParserResult`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a URL and returns its content as a single string, throwing an error on failure.
- B 摘要: Sends a structured XML request to a geoparser service, parses the XML response to extract place names and gazetteer IDs, with retry and error handling.
- 静态失败原因: Static BERT models like GraphCodeBERT may rely on token-level similarity and structural patterns; they might be deceived by the common 'while ((line = reader.readLine()) != null)' pattern and similar API usage, but the low token Jaccard (0.12) should have prevented that. Possibly the model overemphasized the common IOException handling or URL opening? Alternatively, the model might have correctly identified them as non-clones.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB might have considered the common pattern of reading from a URL and concatenating lines as sufficient for Type-4 clone, but the overall functional difference is large.
- 共享行为: Both functions read from a URL using InputStreamReader and BufferedReader in a while loop to concatenate lines.
- 行为差异: Function A simply fetches raw web page content; Function B constructs a custom XML request and parses the XML response.；Function A has no retry logic; Function B retries up to 3 times on failure.；Function A returns a String; Function B returns a Collection of Tuples.；Function B includes a testing branch that returns dummy data.
- 修正建议: Enhance model to consider overall program structure and data flow beyond token overlap.；Include more context-aware embeddings that capture the purpose of the function (e.g., including method names and return types).；Use control-flow and data-flow analysis to differentiate between simple fetch and complex transformation.

### case_id=2217 FP lexical_or_api_overlap

- 方法: `readZoneIDs` vs `getContent`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads zone IDs from a resource file, parsing each line as an integer, and returns a set of integers.
- B 摘要: Executes an HTTP request and returns the response body as a concatenated string.
- 静态失败原因: Static BERT likely overemphasized the shared lexical pattern (LineNumberReader/InputStreamReader, readLine loop) and ignored the fundamental differences in data flow and domain (file vs HTTP).
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clones when functions have different input sources, output types, and overall purpose despite superficial structural similarities like reading lines.
- 共享行为: Both read lines from an input stream using readLine() in a while loop.
- 行为差异: Function A reads from a file resource; function B reads from an HTTP response.；Function A parses lines as integers; function B concatenates lines as a string.；Function A returns a HashSet<Integer>; function B returns a String.；Function B sets HTTP connection and socket timeouts; function A does not.
- 修正建议: Enhance model with data-flow analysis to distinguish between different stream sources (file vs HTTP).；Include type information of inputs/outputs to differentiate integer set from string.；Add context about surrounding class/method purpose (e.g., zone ID parsing vs HTTP content retrieval).

### case_id=2218 FN partial_functionality

- 方法: `doTransfer` vs `run`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Proxies an HTTP request by forwarding headers and body from an incoming request to a target URL and echoing the response back.
- B 摘要: Performs a simple authenticated HTTP GET request using a URL object and reads the response into a string.
- 静态失败原因: Static BERT/GraphCodeBERT likely failed due to low token overlap (0.2288) and inability to recognize the partial functional similarity in HTTP connection handling, as the models are sensitive to surface-level syntactic differences.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as HTTP client operations that read a response, treating them as Type-4 clones despite significant behavioral differences because they share the core concept of establishing an HTTP connection and processing the response.
- 共享行为: Creates an HttpURLConnection to a given URL；Sets request method (GET) and enables input；Opens an InputStream from the connection；Reads the response data
- 行为差异: A copies request headers and body to the outgoing connection; B does not；A writes response to HttpServletResponse output stream; B stores response in a StringBuffer；A supports multiple HTTP methods via parameter; B only GET；A sets authentication header (hardcoded 'Basic'); B does not set any auth
- 修正建议: Incorporate data flow analysis to identify common API usage patterns (e.g., HttpURLConnection, getInputStream)；Use contrastive learning on partial functionality clones；Enhance model with information about HTTP protocol semantics

### case_id=2219 FP boilerplate_overlap

- 方法: `copyFile` vs `main`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Copies a file using FileChannel's transferFrom method.
- B 摘要: Main entry point for an AdapterGenerator that parses a Prolog file and generates adapter classes and resources.
- 静态失败原因: The model likely focused on common tokens like 'File', 'IOException', and 'static public' while ignoring the vast structural and semantic differences. The presence of boilerplate I/O patterns and similar method signatures may have caused a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would label this as non-clone because the functions are semantically unrelated despite superficial API overlap. The BCB annotation criteria favor Type-3/Type-4 clones with similar functionality, which is absent here.
- 共享行为: Both use the File class for file operations；Both involve IOException handling (declared or caught)；Both are public static methods
- 行为差异: copyFile performs a simple file copy; main performs complex argument parsing, Prolog parsing, code generation, and class writing；copyFile has no control flow beyond sequential statements; main has extensive conditional and error handling logic；copyFile is a utility method; main is an application entry point
- 修正建议: Increase weighting of structural and data-flow differences；Use more discriminative features like method length, cyclomatic complexity, and API call sequences；Improve training data to include such false positive examples

### case_id=2220 FN long_range_semantics

- 方法: `sendExceptionToServer` vs `writeFileType`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends an exception report to a server via HTTP POST with encoded parameters.
- B 摘要: Reads URIs from a file, fetches each URI's content, detects OWL/RDFS/RDF tags, and writes classification to an output file.
- 静态失败原因: Static models like CodeBERT rely on token-level similarity and structural overlap; this pair has low token Jaccard (0.205) and different method names and comments, leading to low similarity scores.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may consider these clones due to Type-4 semantic similarity: both involve network I/O, URL handling, stream reading/writing, and exception handling with similar code structure, despite different specific tasks.
- 共享行为: Both use URLConnection to communicate over network；Both use BufferedReader to read input streams；Both handle IOExceptions with try-catch blocks；Both construct strings and write to streams
- 行为差异: Function A sends a single POST request with exception data; Function B iterates over multiple URIs and fetches each；Function A writes to an HTTP output stream; Function B writes to a local file；Function A reads server response; Function B reads remote content and checks for specific tags；Different application domains: error reporting vs document classification
- 修正建议: Improve training data with more Type-4 clones；Incorporate data flow or control flow features；Use contrastive learning to focus on semantic analogies

### case_id=2221 FP partial_functionality

- 方法: `extractResourceToFile` vs `readData`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Copies a resource file from the classpath to a destination file, handling input and output stream closures.
- B 摘要: Parses multiple comma-separated string fields into sets and maps, and also reads a configuration file to populate additional data structures.
- 静态失败原因: The static model may have falsely flagged due to both methods using try-finally blocks for resource management and both performing read operations, but the overall semantics are unrelated.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB would not consider them clones because they perform entirely different functionalities with no overlap in purpose or behavior.
- 共享行为: Both use try-catch/finally for resource handling；Both involve reading data from some source
- 行为差异: Function A is a simple file copy; B is a complex data initialization with set construction and file parsing；Different parameters and return types；Different domain: file I/O vs data parsing
- 修正建议: Improve training with more diverse negative examples featuring structural but not semantic similarity；Use data flow analysis to distinguish resource management from data parsing；Incorporate method naming and context

### case_id=2222 FN partial_functionality

- 方法: `File2String` vs `load`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a file from local filesystem or classpath, concatenates lines into a string, exits on error.
- B 摘要: Reads text from a Pastebin URL via HTTP, concatenates lines into a string, shows error dialog on failure.
- 静态失败原因: Low token overlap (0.24) and different API calls (File vs URL) misled the model; it missed the high-level semantic equivalence of 'read all lines from source'. The model likely focused on surface-level differences rather than the shared loop structure.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often treats functions with the same core algorithm (reading all lines from an input source and concatenating) as clones, even when I/O sources differ, considering them Type-3 or Type-4 clones due to partial functional similarity.
- 共享行为: Read all text from an external source line by line；Concatenate lines into a single string；Return the resulting string
- 行为差异: Source type: local file/classpath vs remote HTTP URL；Error handling: System.exit vs JOptionPane dialog；Debug output present only in A；Working flag present only in B
- 修正建议: Train with positive examples where I/O source varies but core algorithm is the same；Incorporate control flow and data flow graphs to capture loop body similarity；Use abstract representations that normalize API calls to higher-level actions

### case_id=2223 FN partial_functionality

- 方法: `copyResource` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource from a URL or local file to a destination file using byte streams.
- B 摘要: Main method that parses command-line arguments, reads an input file with specified encoding, and writes to an output file with optional charset conversion.
- 静态失败原因: Static BERT/GraphCodeBERT models rely on token and structural patterns. The low token Jaccard (0.162791), different method signatures, and distinct API usage (URL vs CmdLineParser) led the model to miss the high-level functional similarity. The models are sensitive to surface-level differences.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB annotators may consider both as clones because they perform file copying functionality, despite differences in I/O APIs and additional logic. The core task of reading input and writing output is preserved, fitting Type-4 (functionally similar) clones.
- 共享行为: Both functions read data from a source and write to a destination file.
- 行为差异: copyResource uses byte streams (InputStream/OutputStream), while main uses character streams (Reader/Writer) with encoding.；copyResource copies from a resource (URL or local file) determined by source field, whereas main reads from command-line-specified file.；main includes command-line parsing, default encoding handling, and error printing, unlike copyResource.；copyResource uses a simple loop reading one byte at a time, while main uses a char buffer.
- 修正建议: Incorporate data-flow analysis to detect that both functions perform read-write loops.；Use contrastive learning with hard negatives that share core behavior but differ in API/control flow.；Include functional annotations or task labels (e.g., file copy) to guide similarity.

### case_id=2224 FP boilerplate_overlap

- 方法: `readData` vs `copy`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Parses a configuration file to populate various sets and maps with tokens and Unicode data.
- B 摘要: Copies a file from a source to a destination using byte streams.
- 静态失败原因: The model likely focused on the common I/O calls (FileInputStream, FileOutputStream) and try-catch blocks, ignoring the distinct high-level logic and data structures.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would label this as non-clone because the functions have completely different purposes and no significant code reuse or algorithmic similarity.
- 共享行为: Both perform I/O operations on files
- 行为差异: A is a complex parsing routine that reads structured data; B simply copies bytes；A populates multiple data structures; B writes to a new file；A handles line-level parsing and error checking; B focuses on streaming copy
- 修正建议: Increase training data with diverse I/O functions to reduce overemphasis on boilerplate；Incorporate control flow and data dependency analysis to distinguish specific transformations

### case_id=2225 FP lexical_or_api_overlap

- 方法: `doVersionCheck` vs `getTicketsForQueue`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Checks for a new version of jEdit by reading version and build strings from a remote URL.
- B 摘要: Retrieves a list of open tickets for a given queue from a Request Tracker system via HTTP API.
- 静态失败原因: The model may have been misled by superficial similarities in API usage (e.g., URL, BufferedReader, exception handling) and ignored the differing method names and overall purpose.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB annotators would likely consider these non-clones because the functions have entirely different business logic and are not even functionally similar at a high level.
- 共享行为: Both use HTTP to fetch data from a remote server.
- 行为差异: Different purposes: version checking vs. ticket retrieval.；Different data parsing: version/build strings vs. ticket IDs.；Different error handling: messages vs. returning null.；Different output types: void vs. List<RTTicket>.
- 修正建议: Incorporate method name and surrounding context into embedding.；Train on more diverse examples to avoid over-relying on common I/O patterns.；Use contrastive learning to better distinguish different functionalities.

### case_id=2226 FP boilerplate_overlap

- 方法: `main` vs `run`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Generates Java adapter classes from a Prolog file and writes them to a JAR.
- B 摘要: Copies multiple files from an HDFS directory to a local output file.
- 静态失败原因: The model likely overfit to overlapping tokens like 'args.length', 'if', 'File', 'return', and 'System.out.println', mistaking similar boilerplate for semantic equivalence.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels these as non-clones because their core functionality is entirely different, despite superficial similarities in argument handling and file I/O.
- 共享行为: Parse command-line arguments for input and output paths；Print error messages for missing or invalid files；Use file I/O operations；Handle exceptions with error messages
- 行为差异: A parses Prolog source, generates Java classes and serialization; B copies binary files from HDFS to local；A uses complex reflection, class generation, and JAR writing; B uses simple stream copying；A has a debug mode and multiple output steps; B is a straightforward file transfer
- 修正建议: Incorporate dataflow analysis to distinguish different operations on files；Use type-aware embeddings to capture domain-specific semantics (e.g., Prolog vs HDFS)；Train with contrastive examples of similar-looking but semantically different functions

### case_id=2227 FP lexical_or_api_overlap

- 方法: `main` vs `readAndRewrite`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Main method for generating Java adapter classes from a Prolog file using a framework.
- B 摘要: Method that reads a DICOM image file and rewrites it to another file.
- 静态失败原因: Static BERT/GraphCodeBERT may have focused on common tokens like 'File', 'IOException', 'System.out.println', and method boilerplate, ignoring the fundamentally different algorithmic logic and domain-specific libraries.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels this as non-clone because the two functions have completely different functionality and purpose, even if they share some superficial API usage.
- 共享行为: Both perform file I/O operations；Both print messages to standard output
- 行为差异: Function A parses a Prolog file and generates Java code; Function B reads and writes DICOM pixel data.；Function A involves class loading, reflection, and writing JAR entries; Function B deals with image streams and DICOM encoding.；Function A is a main entry point; Function B is a private helper method.；Function A handles command-line arguments and various IO exceptions; Function B declares IOException.
- 修正建议: Incorporate data-flow and control-flow features to better capture program semantics.；Use graph-based representations that highlight structural differences.；Increase training data diversity to reduce reliance on token-level similarities.

### case_id=2228 FN partial_functionality

- 方法: `getResourceAsStream` vs `transferWSDL`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a resource from a URL, caches it locally, and returns an InputStream.
- B 摘要: Downloads a WSDL from a URL with optional authentication, saves it to a temporary file, and returns the file path.
- 静态失败原因: Static BERT models rely on token overlap and local context. Despite shared API calls (URL, HttpURLConnection, etc.), the low token Jaccard (0.19) and differences in method names, caching, and error handling caused the model to miss the high-level semantic similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels Type-3/Type-4 clones where functions share high-level functionality. Both functions perform the core task of fetching remote content via HTTP and saving it locally, which is a common pattern.
- 共享行为: Open HTTP connection with GET method；Read input stream from URL connection；Write to a file output stream；Close streams after use
- 行为差异: A implements caching logic, B does not；A returns an InputStream, B returns a file path；B includes HTTP Basic Authentication；Different error handling strategies
- 修正建议: Use data-flow analysis to trace the core pattern of fetch and save；Incorporate AST or program dependency graph matching；Consider semantic role of function (e.g., download resource) rather than specifics

### case_id=2229 FP partial_functionality

- 方法: `readRemoteFile` vs `SRWGuiClient`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a remote file from a URL and returns its content as a string.
- B 摘要: Constructs a GUI browser that reads a URL, optionally transforms XML with XSLT, and displays the result.
- 静态失败原因: Static BERT likely focused on lexical and local API overlap (URL, BufferedReader, openStream) and the common pattern of reading lines, ignoring the broader context of GUI construction and XML transformation, leading to a false positive.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB prefers to label non-clones when the overall functionality differs significantly, even if there is partial overlap in code patterns. Here, the core purpose differs (utility reading vs GUI construction with XML processing), so BCB would likely label as non-clone.
- 共享行为: Both read content from a URL using URL.openStream() and BufferedReader.；Both handle IOException.
- 行为差异: Function A returns raw file content; Function B constructs a GUI and displays content (possibly transformed).；Function B includes XML parsing and XSLT transformation; Function A does not.；Function A is a stateless method; Function B is a constructor with side effects (GUI setup).
- 修正建议: Incorporate method-level context or surrounding code to capture overall purpose.；Use structural information (e.g., AST) to distinguish between utility methods and constructors with side effects.；Enhance training data with more examples of partial functionality overlap labeled as non-clones.

### case_id=2230 FN benchmark_preference_bias

- 方法: `doTransfer` vs `lookupFutureEvents`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Forwards an HTTP request to another URL by copying headers and body, then returns the response.
- B 摘要: Fetches events from a meetup API, parses JSON response, and returns a list of Event objects.
- 静态失败原因: Static model likely correctly identified low token overlap (Jaccard 0.11) and distinct functionality, hence predicted non-clone. It did not fail; the BCB label is likely a data noise.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB label may have considered both as implementing a 'network request' pattern, but the functionality is distinct (proxy vs. data retrieval). BCB typically requires stronger semantic equivalence.
- 共享行为: Both use URL and open streams for network I/O；Both handle IOException
- 行为差异: doTransfer proxies HTTP requests; lookupFutureEvents fetches and parses API data；doTransfer copies raw bytes; lookupFutureEvents parses JSON into domain objects；doTransfer modifies request/response headers; lookupFutureEvents processes external data；Different input/output types and exception handling
- 修正建议: Use semantic similarity models to better capture functional equivalence；Review and correct BCB annotations for such pairs；Incorporate data-flow and domain knowledge

### case_id=2231 FN benchmark_preference_bias

- 方法: `doGet` vs `execute`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Handles HTTP GET request to retrieve a page by parameter, checks visibility, logs, renders page with caching if applicable.
- B 摘要: Saves a HomeMap object with description and copies an uploaded image file to a directory, then returns a list result.
- 静态失败原因: Static BERT likely failed to capture this as a clone because it correctly identified the lack of semantic overlap and low token similarity, but BCB's annotation was overly broad or erroneous.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled as clone due to broad Type-4 partial functionality similarity such as both being web-related and involving I/O, but the actual semantics are entirely different.
- 共享行为: Both involve file output operations (caching vs image saving)；Both use I/O streams and exception handling
- 行为差异: Different application contexts (servlet vs action)；Different core functionalities (page display vs data persistence with image upload)；Different control flows and error handling specifics
- 修正建议: Improve BCB annotation consistency, avoid labeling such distinct functionalities as clones.；Or, if BCB label is intentional, then model needs better representation of broad behavioral patterns like 'web page handling' vs 'data persistence'.

### case_id=2232 FP lexical_or_api_overlap

- 方法: `doVersionCheck` vs `get`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Checks for new version of jEdit by fetching a version file from a URL and comparing build numbers.
- B 摘要: Fetches game records from a REST API by sending a GET request and parsing response lines into GameRecord objects.
- 静态失败原因: Static models like GraphCodeBERT may focus on token-level and structural overlap (e.g., common identifiers like URL, BufferedReader, readLine, while, IOException) and ignore the broader functional context and domain-specific logic, leading to false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the overall functionality differs significantly: one is a version checker for an editor, the other is a game record fetcher. The shared I/O pattern is too generic to indicate semantic similarity.
- 共享行为: Both open a URL connection and read lines from an input stream using BufferedReader.；Both parse each line based on a condition (startsWith) and process matched lines.；Both catch IOException for error handling.
- 行为差异: Function A uses URL.openStream directly, while B uses HttpURLConnection with custom headers and request method.；Function A parses version and build fields, B parses GameRecord objects skipping comment lines.；Function A displays GUI messages, B prints to stdout or stack trace.；Function A returns void, B returns an array or null.
- 修正建议: Incorporate semantic role labeling or dependency parsing to distinguish core logic from boilerplate I/O code.；Use dataflow analysis to trace how parsed data is used (comparison vs object creation).；Integrate domain-specific ontologies or task categorization.

### case_id=2233 FN benchmark_preference_bias

- 方法: `testAddLinkToImage` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Test method that copies image resources from classpath to a test folder and adds links to a report.
- B 摘要: Method that retrieves a resource as an InputStream, with caching and HTTP support.
- 静态失败原因: Low token Jaccard (0.088) and no overlapping method names or structure; static models rely on lexical and syntactic similarity which are absent here.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB likely labeled as clone due to both functions dealing with file I/O and resource loading, despite different contexts and purposes, possibly under broad Type-4 similarity.
- 共享行为: Both involve reading from InputStream and writing to file
- 行为差异: A is a specific test scenario for reporting; B is a generic resource retrieval utility；A copies multiple static images; B caches dynamic resources from URLs；A uses IOUtils.copy; B uses manual copy loop and handles HTTP caching
- 修正建议: Incorporate high-level semantic understanding beyond token overlap；Use models that capture functional intent, e.g., via control-flow or data-flow graphs；Consider domain-specific knowledge (test vs. utility) to differentiate

### case_id=2234 FP lexical_or_api_overlap

- 方法: `main` vs `readAndRewrite`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Generates Java adapter code from a Prolog file using command-line arguments.
- B 摘要: Reads a DICOM image file, processes pixel data, and writes a transformed DICOM file.
- 静态失败原因: Static BERT models may rely on lexical and structural similarities. Both functions contain common Java boilerplate (e.g., File, System.out.println, try-catch) and similar length/complexity, causing the model to overlook fundamentally different semantics.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels non-clones when functions have different purposes and domain-specific logic, even if they share trivial I/O patterns. Here, the core functionality is completely different.
- 共享行为: Both perform file I/O operations (reading input files and writing output).；Both print status messages to standard output.
- 行为差异: Function A parses Prolog source and generates Java bytecode; function B processes DICOM medical image data.；Function A uses command-line argument parsing; function B uses fixed File parameters.；Function A involves multiple steps (parsing, visitor pattern, class writing); function B is a straightforward read-rewrite pipeline.；Function A uses libraries like PrologParser, FactVisitor, ClassWriter; function B uses DICOM-specific libraries (ImageInputStream, DcmParser, etc.).
- 修正建议: Enhance the model with data flow analysis to distinguish domain-specific API calls (e.g., Prolog vs. DICOM).；Use contrastive learning to better separate functions with different high-level purposes.；Incorporate task-type classification as an auxiliary objective.

### case_id=2235 FN boilerplate_overlap

- 方法: `scrapeForIsbns` vs `httpRequestByPOST`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Scrapes a URL for ISBN-10 patterns and counts matches, with retries on connection errors.
- B 摘要: Sends an HTTP POST request with parameters and returns the response body as a string, handling HTTP status codes and I/O errors.
- 静态失败原因: Static models like GraphCodeBERT likely focused on the distinct tokens (regex, retries, status codes) and low token overlap, failing to recognize the underlying similar stream reading pattern and thus predicting non-clone.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may label this as a clone because both functions perform network I/O and read response content line by line, which is considered a common high-level pattern, even though the specific tasks differ.
- 共享行为: Both read data from an HTTP response line by line using BufferedReader.
- 行为差异: A uses regex to extract ISBNs; B appends entire lines to a buffer.；A retries on connection errors up to a limit; B handles status codes and returns null on error.；A updates a shared collection (outputIsbns); B sets error fields.；A returns count; B returns response string.
- 修正建议: Enhance models to abstract common patterns like network I/O reading.；Use contrastive learning with examples of partial functional similarity.

### case_id=2236 FN partial_functionality

- 方法: `runInternal` vs `sendRequest`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches OPDS catalog from a URL with pagination and progress reporting.
- B 摘要: Sends an XML request to a servlet via HTTP and parses the compressed response.
- 静态失败原因: Low token Jaccard (0.11) indicates little lexical overlap; the model likely relies on surface tokens and missed the abstract HTTP client pattern shared by both methods.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considers them clones because both are HTTP client methods that open connections, set headers, handle responses, and perform XML-related processing, fitting a broad Type-3/Type-4 clone category.
- 共享行为: Both open HTTP connections using java.net.URLConnection；Both set request properties and handle network errors；Both involve reading/writing data over HTTP
- 行为差异: A is a GET-like operation for catalog retrieval; B is a POST-like operation sending XML；A handles pagination and progress; B uses compression and returns an empty string；A uses callbacks; B uses dialog for configuration
- 修正建议: Enhance representation to capture abstract behavior patterns like HTTP request handling；Use finer-grained structural features such as API call sequences；Incorporate data flow or control flow graphs

### case_id=2237 FN partial_functionality

- 方法: `copyResource` vs `split`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource (URL or file) to a destination file byte by byte using streams.
- B 摘要: Splits a FASTA file into multiple smaller files based on size or entry limits using NIO channels and buffers.
- 静态失败原因: Static BERT models rely primarily on token sequences and miss the abstract functional similarity of file copying; low token Jaccard (0.137) and long/complex code in split lead to poor semantic capture.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled this as a clone due to a broad interpretation of file I/O operations, or due to annotation error given the low lexical similarity and different functionalities.
- 共享行为: Both read from an input source and write to an output file.
- 行为差异: copyResource is a simple, unconditional copy of a single resource; split conditionally splits a FASTA file into multiple parts.；copyResource uses InputStream/OutputStream and copies byte-by-byte; split uses FileChannel, ByteBuffer, and transferTo for efficient I/O.；split includes FASTA tokenization logic (defline vs sequenceline) and tracks counts; copyResource does not parse file contents.；split creates multiple output files and returns a count; copyResource writes to a single destination and returns void.
- 修正建议: Incorporate data flow and control flow graphs (e.g., GraphCodeBERT) to capture I/O patterns.；Use code summarization or function-level embeddings that focus on input-output behavior.；Apply domain-specific knowledge for file operations when available.

### case_id=2238 FN benchmark_preference_bias

- 方法: `copyFile` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Copies a file from source to destination using FileChannel.transferFrom.
- B 摘要: Launches a NexOpen project configuration by checking project files, processing pom.xml, and setting properties.
- 静态失败原因: The model correctly predicted non-clone based on low token overlap and structural differences; the BCB label is likely a benchmark error.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB likely mislabeled this as a clone due to superficial file I/O overlap, but the functions are semantically unrelated.
- 共享行为: Both involve file system operations and resource cleanup.；Both use try-finally blocks for proper resource handling.
- 行为差异: copyFile is a simple file copy; launch performs complex project configuration and launch tasks.；launch includes assertions, reading XML, handling properties, and interacting with Eclipse resources.；copyFile works on any File objects; launch is specific to NexOpen projects and Eclipse APIs.
- 修正建议: Re-evaluate the clone label for this pair in the benchmark.；Improve consistency in BCB annotation criteria to avoid such mismatches.

### case_id=2239 FN benchmark_preference_bias

- 方法: `convert` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Converts an ACRNEMA file to DICOM format, adding UIDs and handling pixel data.
- B 摘要: Launches a Maven-based build for a NexOpen project, processing pom.xml files and setting Hibernate properties.
- 静态失败原因: Static model (e.g., GraphCodeBERT) likely predicted non-clone correctly because the code is semantically and lexically dissimilar. The model did not fail; rather, the BCB label appears to be an error or based on overly broad criteria.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled as clone due to both being functions that read input, process, and write output, with similar structural patterns like condition checks and resource handling, but the functional semantics are completely different.
- 共享行为: Both perform file I/O；Both check conditions and may return early；Both use try-finally for resource management
- 行为差异: Function A is specific to DICOM medical image conversion；Function B is specific to Eclipse IDE project building and Maven；Function A writes binary pixel data; Function B sets project properties and runs an action；They operate on entirely different domain objects
- 修正建议: Re-evaluate BCB labeling criteria for this pair；Ensure that clone pairs require meaningful semantic overlap beyond generic structural patterns

### case_id=2240 FP lexical_or_api_overlap

- 方法: `readData` vs `copyFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: readData initializes multiple sets and maps by tokenizing static strings and parsing a configuration file, handling errors.
- B 摘要: copyFile copies a file from source to destination using NIO FileChannel transferTo.
- 静态失败原因: The model likely overgeneralized from the presence of file I/O (IOException, FileChannel) and the structured parsing pattern in readData, misclassifying due to domain similarity in file handling rather than functional equivalence.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB annotates non-clones because the functions have completely different purposes (data initialization vs. file copying), no shared functionality, and only superficial lexical overlap in file I/O exception handling.
- 行为差异: readData populates data structures from string tokens and a file, while copyFile transfers bytes between file channels.；readData is private static with no arguments, copyFile has two File parameters and throws IOException.；readData has complex control flow with multiple loops and error handling, copyFile is a simple try-finally block.
- 修正建议: Include more non-clone pairs with low token similarity but shared API usage to teach the model to distinguish.；Emphasize semantic role of I/O operations (reading vs. transferring) in training.；Use contrastive learning on functions with similar surface patterns but different intents.

### case_id=2241 FP lexical_or_api_overlap

- 方法: `executePost` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Executes an HTTP POST request to a given URL with URL-encoded parameters and returns the response body.
- B 摘要: Performs a Google image search by constructing a query URL, making an HTTP GET request, and parsing the response to extract image URLs.
- 静态失败原因: The model was misled by the common HTTP-related API calls (URL, HttpURLConnection, BufferedReader) and similar try-catch structure. The token overlap is low (0.15), but the sequence of API calls and control flow (open connection, read line, close) created a false positive. The model lacks understanding of the different input/output roles and the domain-specific post-processing in B.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the functions have distinct purposes and contexts (generic POST vs. specific image search), despite sharing boilerplate HTTP code. The similarity is only superficial and does not constitute a Type-3 or Type-4 clone.
- 共享行为: Both open an HTTP connection using URL and HttpURLConnection；Both send a request and read the response via BufferedReader；Both handle exceptions with a catch block
- 行为差异: HTTP method: A uses POST, B uses GET；A takes parameters and returns a String; B has no parameters and returns void；A sets Content-Type and Content-Length headers; B sets User-Agent header；A writes data to the connection output stream; B does not
- 修正建议: Incorporate data-flow analysis to track how input parameters and output values are used；Add context-aware training that distinguishes utility functions from specific application logic；Use higher-level semantic matching that considers the overall goal (e.g., generic HTTP vs. web scraping)

### case_id=2242 FP other

- 方法: `actionPerformed` vs `convert`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Handles UI events to set various application preferences (e.g., paths for Graphviz, ImageMagick, font size, look and feel) and displays restart dialog.
- B 摘要: Converts an ACRNEMA stream file to DICOM format, adding necessary UIDs and handling pixel data compression.
- 静态失败原因: The static model likely relied on superficial token overlaps (e.g., 'File', 'return', 'if', 'null') and the presence of try-finally or similar control structures, but the overall semantics and domain are completely different. The low Jaccard similarity (0.082) suggests that the model may have overfitted to some common patterns in long methods, misclassifying this pair.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB typically considers two functions clones only if they share significant functional logic. Here, one is a UI event handler and the other is a DICOM converter, so BCB would label them as non-clones (Type-0/Type-1).
- 共享行为: Both use File objects and handle null checks or conditional returns.
- 行为差异: Function A is a GUI event handler that updates UI and preferences; function B is a file format converter.；Function A uses Swing components and external controller; function B uses DICOM parsing and byte-level I/O.；Function A has many command branches; function B has a single conversion pipeline.
- 修正建议: Improve model's ability to capture high-level purpose using AST-based or dataflow features.；Increase training data diversity to reduce false positives on unrelated long methods.；Apply a functional similarity measure based on API calls and task taxonomy.

### case_id=2243 FP boilerplate_overlap

- 方法: `main` vs `unzipEntry`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Main method that generates adapter code from a Prolog file and writes it to a JAR.
- B 摘要: Unzips a single entry from a zip file to an output directory.
- 静态失败原因: The static model likely overgeneralized based on the presence of I/O-related tokens (File, IOException, stream) and similar structural elements (try-catch, conditionals), ignoring the substantial difference in core functionality.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clones when functions have entirely different purposes despite both performing file I/O; they require similar algorithmic intent for Type-3/Type-4.
- 共享行为: Both involve file I/O operations；Both have conditional checks for directory/file existence
- 行为差异: Function A is a complex main method with multiple steps (parsing, code generation, writing multiple resources); Function B is a simple utility to extract one zip entry；Function A writes to a JAR file; Function B extracts from a zip file；Function A uses many custom classes; Function B uses standard Java I/O
- 修正建议: Improve understanding of high-level program semantics beyond token-level patterns；Use graph or flow-based representations to capture data flow differences

### case_id=2244 FP lexical_or_api_overlap

- 方法: `populateResources` vs `SRWGuiClient`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Loads template resources from classpath, processes XML/TXT files, and saves default images as properties.
- B 摘要: Constructs a Swing browser GUI, reads XML from a URL, optionally transforms it with XSLT, and displays the result.
- 静态失败原因: Static BERT/GraphCodeBERT likely overemphasized the superficial syntactic overlap (BufferedReader, StringBuffer, URL, etc.) and missed the distinct high-level goals, control flows, and domain objects.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels non-clones when the methods have completely different purposes even if they share some API usage patterns. Here, the intents are entirely different (resource initialization vs GUI construction), so it is correctly labeled as non-clone.
- 共享行为: Both use BufferedReader to read text line by line；Both use StringBuffer to accumulate text；Both catch IOException and log/print errors；Both instantiate URL objects
- 行为差异: A processes local resources from classpath; B fetches remote URL content；A saves Resource and Property objects; B builds a GUI with JEditorPane；A iterates over a list of URLs; B handles a single URL and optionally applies XSLT transformation；A uses Image and Property persistence; B uses XML parsing and transformation
- 修正建议: Incorporate structural or dataflow features that capture the overall method purpose；Add contrastive training on methods with shared APIs but different semantics；Use control-flow or call-graph analysis to distinguish resource loading from GUI setup

### case_id=2245 FN benchmark_preference_bias

- 方法: `retrieveQ` vs `register`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Fetches the content of a given URL and returns it as a string, printing the response message.
- B 摘要: Registers a User object by validating, encoding password, setting attributes, making a URL request to phpBB forum to set forum ID, persisting the user, and sending a confirmation email; returns success flag.
- 静态失败原因: Static BERT models tend to capture high-level semantic similarity and may underestimate partial functionality clones; here the model correctly identified the overall semantic difference but failed to align with BCB's preference for shared code patterns.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB annotators may have focused on the common URL-reading code segment and considered it a Type-3 clone based on partial functionality or implementation similarity, despite the overall functional difference.
- 共享行为: Both open a URL connection and read lines from the input stream.；Both use BufferedReader to read lines.
- 行为差异: A is a simple utility function with no side effects; B performs complex user registration with multiple side effects.；A prints to stderr; B uses logger for debugging and error handling.；B includes exception handling for IOException and NumberFormatException; A throws declared exceptions.；B constructs a URL with query parameters; A takes a URL string directly.
- 修正建议: Include training examples with partial functionality clones where only a sub-computation is shared.；Incorporate annotation guidelines emphasizing code fragment overlap as a clone criterion.

### case_id=2246 FN benchmark_preference_bias

- 方法: `doGet` vs `readAndRewrite`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Handles HTTP GET requests for portal pages, resolving page names, checking visibility, logging, and caching.
- B 摘要: Reads a DICOM image file and writes it to another file, handling pixel data and DICOM encoding.
- 静态失败原因: Static BERT did not fail; it correctly predicted non-clone. The BCB label is likely erroneous, so the model's false negative against BCB label is actually correct.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have incorrectly labeled these as clones due to a mistaken annotation or a very broad interpretation of 'read and rewrite' that is not supported by the actual code. There is no functional similarity.
- 行为差异: Different input/output types: HTTP request/response vs. file I/O；Different domains: web portal vs. medical imaging；Different functionality: page retrieval and caching vs. DICOM read/write；No overlap in APIs used (HttpServletRequest/Response vs. DICOM libraries)
- 修正建议: Re-annotate this pair in BCB to correct the label to non-clone.；Use static model predictions as a check for potential annotation errors.

### case_id=2247 FN partial_functionality

- 方法: `copyResource` vs `execute`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.75`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Copies a resource from a URL or file to a destination file using a byte-by-byte read-write loop.
- B 摘要: Saves a HomeMap to a database, then copies an uploaded image file to a file named by the database ID using IOUtils.copy.
- 静态失败原因: Static BERT/GraphCodeBERT likely failed due to low lexical token overlap (Jaccard=0.045) and lack of explicit structural similarity. The manual loop in A versus library call in B are syntactically distinct, and the model may not capture the shared 'copy' semantic without explicit dataflow or API knowledge.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider them clones because both implement the core intent of copying data from an input source to an output file, despite differences in source resolution, library usage, and additional logic. This fits Type-3/Type-4 broad similarity.
- 共享行为: Both perform file copy operations from an input stream to an output file stream.
- 行为差异: A reads from a URL or file based on existence; B reads from a specific FileInputStream (imageFile).；A writes to destinationFile(); B writes to a file named with a database-generated ID.；A uses manual byte-by-byte copying; B uses IOUtils.copy (Apache Commons).；A throws Exception; B catches FileNotFoundException and IOException.
- 修正建议: Integrate dataflow analysis to track data movement from input to output.；Include training examples with diverse implementations of the same core operation.；Use dynamic analysis or execution traces to confirm shared behavior.

### case_id=2248 FN partial_functionality

- 方法: `copyResource` vs `extractImage`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource from a URL or file to a destination file byte by byte.
- B 摘要: Extracts an image from input, applies scaling/transforms, and writes it to output file using a specific writer.
- 静态失败原因: Static BERT models rely on token-level overlap and structure; these functions have low Jaccard similarity (0.172), different library calls, and different control flows. The model likely focused on the specific method names and API calls (e.g., 'URL', 'ImageIO' vs 'FileInputStream') and did not capture the high-level common pattern of reading-writing.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as 'file copying' or 'resource manipulation' tasks because both read from an input and write to an output, albeit with different processing steps. The broad functional similarity of data transfer could lead to a Type-4 clone annotation.
- 共享行为: Both read from an input source and write to an output file using streams.；Both handle resource cleanup (closing streams, deleting temp file).
- 行为差异: Function A does generic byte-level copy; function B performs image-specific processing (scaling, transforms) before writing.；Function A supports URL as source; function B supports STDIN as special input.；Function B uses a separate writer interface to write the image; function A writes raw bytes.；Function B uses exception handling with logging; function A throws generic Exception.
- 修正建议: Improve model to capture abstract data-flow patterns such as read-process-write.；Use data-flow or program dependency features to identify common I/O patterns.；Train on more examples of Type-4 clones with low token overlap but similar high-level behavior.

### case_id=2249 FP boilerplate_overlap

- 方法: `googleImageSearch` vs `readURL`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Performs a Google image search for the current track and parses the result to extract image URLs.
- B 摘要: Reads lines from a given URL and prints them to standard output.
- 静态失败原因: Static BERT/GraphCodeBERT likely overemphasized the common boilerplate of URL opening and line reading, ignoring the differing processing logic and output destinations.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically requires functional similarity; here the core functionality (image search vs. generic reading) is too different despite shared low-level I/O pattern.
- 共享行为: Opens a URL connection；Reads lines from the connection；Handles exceptions
- 行为差异: A constructs the URL with query parameters; B takes a preconstructed URL；A parses HTML to extract image URLs; B prints each line as-is；A stores results in a list; B outputs to console；A has a condition to skip if artist unchanged; B has no condition
- 修正建议: Incorporate data-flow analysis to track how read data is used；Add features capturing function purpose (e.g., specific string patterns like 'images.google' vs 'System.out')；Adjust similarity threshold for API-heavy patterns

### case_id=2250 FN partial_functionality

- 方法: `modifyApplicationMessage` vs `fileCopy`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Modifies a properties file for a given locale, optionally copying an English default file if the locale file does not exist.
- B 摘要: Copies a binary file from source to destination with thorough error checking.
- 静态失败原因: Static models like CodeBERT or GraphCodeBERT rely on token-level patterns and may focus on the overall method signature and the majority of tokens. The first function has many tokens related to properties parsing (readLine, split, StringBuilder), while the second is a pure copy. The low Jaccard (0.2) and different method names mislead the model to predict non-clone. The model fails to recognize the shared file-copy subbehavior because it is embedded within a larger context.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as implementing file copy functionality, even if only part of the first function. The conditional file copy in modifyApplicationMessage is structurally similar to a generic file copy, so annotators may label it as a clone under broad Type-4 (partial functionality).
- 共享行为: Reads from one file and writes to another file using a buffer.；Involves file I/O with error handling.
- 行为差异: modifyApplicationMessage reads and parses properties file content, while fileCopy does a raw byte copy.；modifyApplicationMessage only copies a file conditionally (if locale file missing), fileCopy always copies.；modifyApplicationMessage modifies specific key-value pairs, fileCopy preserves exact content.；modifyApplicationMessage handles properties file encoding and comments, fileCopy is generic.
- 修正建议: Train on examples that explicitly annotate partial functional clones where a portion of code matches another function.；Use techniques to identify code fragments that perform similar I/O patterns, e.g., through dataflow analysis or clone detection on subgraphs.；Consider using a model that can capture hierarchical or compositional semantics, such as tree-based models or graph neural networks that can isolate subroutines.

### case_id=2251 FP lexical_or_api_overlap

- 方法: `getFrameworkFactory` vs `startScript`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Loads an OSGi framework factory by reading a service configuration file and instantiating the class.
- B 摘要: Reads a script from a URL and appends its content to a dialog object.
- 静态失败原因: Lexical/API overlap (URL, BufferedReader, readLine) and similar syntactic structure (while loop) caused the model to overlook different intent, method names, and variable types.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled non-clones because overall purpose and context differ significantly (OSGi vs dialog script), and the shared I/O pattern is common boilerplate not considered clone-worthy.
- 共享行为: Open a URL and read lines using BufferedReader；Process each line until null
- 行为差异: A throws an exception on failure; B prints error and exits；A returns a FrameworkFactory; B returns void and updates dialog.script；A skips comment lines; B does not；A uses try-finally; B closes in try block
- 修正建议: Incorporate method name and class context embeddings；Use dataflow analysis to capture different variable uses；Train to distinguish boilerplate I/O from unique business logic

### case_id=2252 FP boilerplate_overlap

- 方法: `getMD5` vs `perform`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Computes MD5 hash of a given string and returns the digest as a byte array.
- B 摘要: Executes a Struts action to classify a concept, involving session checking, XML building, HTTP POST, and parsing.
- 静态失败原因: The static model likely over-relied on surface-level common tokens like 'try', 'catch', 'Exception', and similar method signatures, while ignoring the vast differences in overall structure and purpose.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clone because the functions have no meaningful functional overlap; one is a utility hash function, the other is a Struts action with extensive control flow and I/O.
- 共享行为: Both use try-catch for exception handling
- 行为差异: Function A is a simple cryptographic hash; Function B is a complex web request handler with multiple business logic steps；Function A has no HTTP, XML, or session operations; Function B heavily uses them；Function A returns a byte array; Function B returns an ActionForward
- 修正建议: Enhance the model to capture broader program context and control flow；Incorporate dataflow analysis to distinguish between different computational tasks；Use graph-based representations that capture the call graph and data dependencies

### case_id=2253 FP lexical_or_api_overlap

- 方法: `testCopy_readerToOutputStream_Encoding` vs `main`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Test method that copies a reader to an output stream using a specified encoding and asserts content equality.
- B 摘要: Main method that generates adapter classes from a Prolog file, processes them, and writes them to a JAR file.
- 静态失败原因: Static BERT/GraphCodeBERT may have been misled by lexical overlap of common Java library class names (e.g., ByteArrayOutputStream, OutputStream) and similar tokens like 'out', 'bytes', 'IOException', despite low overall Jaccard similarity.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clones here because the functions have entirely different functionality and structure; they are not even partial clones.
- 共享行为: Both involve I/O operations.
- 行为差异: Different purposes: testing vs. code generation.；Different input sources: byte array vs. Prolog file.；Different output targets: in-memory stream vs. JAR file.；Different control flow complexity; B has extensive logic for parsing and adapter generation while A is a simple copy test.
- 修正建议: Incorporate structural information such as control flow and data flow to differentiate unrelated methods.；Use contrastive learning that penalizes false positives from API name overlap.；Enhance model with understanding of method purpose via method name and context.

### case_id=2254 FN partial_functionality

- 方法: `fileDownload` vs `startScript`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a file from a URL and saves it to a specified directory.
- B 摘要: Reads a script from a URL and appends it to a dialog buffer.
- 静态失败原因: Static methods relying on token overlap (Jaccard 0.14) miss the abstract pattern of URL fetching; GraphCodeBERT may not capture dataflow divergence across output types.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often considers structural similarity in URL reading patterns as sufficient for Type-3/4 clones, despite differing output destinations.
- 共享行为: Both open a URL and read its content via BufferedReader；Both handle IOExceptions；Both close the input stream after reading
- 行为差异: fileDownload writes output to a file; startScript appends to a string；fileDownload reads character by character; startScript reads line by line；fileDownload uses FileOutputStream and BufferedWriter; startScript uses string concatenation
- 修正建议: Train on clone pairs with varying output handling but shared core logic；Incorporate dataflow analysis to detect common subroutines like URL reading；Use contrastive learning to emphasize structural similarity over token overlap

### case_id=2255 FN boilerplate_overlap

- 方法: `encodeFileToFile` vs `modifyApplicationMessage`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Encodes a file to Base64 and writes to output file.
- B 摘要: Modifies a localized properties file by replacing or adding a property key-value pair.
- 静态失败原因: Static BERT likely relied on token overlap and method name similarity, which are low, and failed to recognize the structural file-I/O pattern that BCB considered.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may have labeled this as clone due to a broad Type-3 interpretation: both functions exhibit a common structural pattern of opening a file, transforming its content, and writing to another file, despite very different transformations.
- 共享行为: Both perform file I/O with input and output streams.；Both use buffered reading/writing.；Both handle exceptions and close streams in finally block.
- 行为差异: Core transformation is completely different: Base64 encoding vs. property key-value modification.；Function B includes file existence check and fallback copy from English file, absent in A.；Function A returns a boolean, B does not return anything.；Function B reads line-by-line with string manipulation, A reads byte-by-byte with buffer.
- 修正建议: Incorporate structural similarity heuristics for common I/O patterns beyond lexical tokens.；Use program dependence graph or control-flow graph features to capture high-level similarities.

### case_id=2256 FP lexical_or_api_overlap

- 方法: `getFrameworkFactory` vs `doVersionCheck`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Loads an OSGi framework factory by reading a service configuration file from the classpath and instantiating the class.
- B 摘要: Performs a version check by fetching a URL, parsing lines for development and stable build strings, and then calling another version check method.
- 静态失败原因: The model likely focused on token-level overlap (URL, BufferedReader, readLine, trim) and missed the higher-level semantic differences. The structural similarity of reading from a URL and parsing lines caused a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled as non-clone because the overall functionality differs (loading a framework vs version checking) despite superficial similarity in reading from a URL.
- 共享行为: Both open a URL and read lines using BufferedReader.；Both parse lines by trimming and checking prefixes.
- 行为差异: A uses getResource from classloader, B uses new URL.；A instantiates a class from the parsed line, B calls another method (doVersionCheck).；A throws an exception on failure, B handles IOException and shows an error dialog.
- 修正建议: Include method names and surrounding context to differentiate purposes.；Incorporate dataflow analysis to track how parsed data is used (instantiation vs. method call).；Use domain-specific knowledge (e.g., OSGi vs. version checking).

### case_id=2257 FN partial_functionality

- 方法: `getEncoding` vs `getPagina`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Opens a URL connection, reads HTTP headers and page content to extract charset/encoding information, returns the encoding string or a default.
- B 摘要: Opens a URL, reads all lines from the page content, concatenates them into a single string, and returns the page content or an exception message.
- 静态失败原因: Static models like CodeBERT or GraphCodeBERT rely on lexical and structural similarities. The token Jaccard is low (0.22), and the code structures differ significantly (header processing vs simple read-line). The models may not capture the high-level semantic similarity of 'URL reading and line processing' due to lack of explicit API call patterns alignment. Also, differences in method signatures (private vs public static) and variable usage reduce similarity scores.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as 'fetching and processing data from a URL', a broad Type-4 semantic clone category. Despite different outputs, the core pattern of opening a URL, reading lines, and handling I/O is shared. The functions are from similar domains (web page processing) and both involve extracting information from HTTP responses.
- 共享行为: Both open a URL and read its content line by line.；Both use BufferedReader and InputStreamReader for I/O.；Both handle potential IOException.
- 行为差异: A returns a single encoding string; B returns the entire page content.；A first checks HTTP headers for charset; B does not.；A parses lines for charset/encoding keywords; B simply concatenates all lines.；A closes the reader in a finally block; B closes in the try block.
- 修正建议: Incorporate data flow analysis to identify common API usage patterns (URL opening, BufferedReader).；Use graph-based representations that capture control flow for I/O operations.；Augment training with more examples of Type-4 clones with similar functional skeletons but different outputs.；Employ contrastive learning to focus on semantic similarity beyond lexical overlap.

### case_id=2258 FN partial_functionality

- 方法: `handler` vs `register`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a web page and extracts values from lines based on patterns, updating a result map.
- B 摘要: Registers a new user by encoding password, creating hash, calling a phpBB forum API, persisting user, and sending confirmation email.
- 静态失败原因: Static BERT models rely on token overlap and surface features; despite low token Jaccard, there is some API overlap. The model likely missed the broader BCB preference for partial functional similarity, focusing instead on the overall difference in purpose and logic.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled these as clones based on the shared pattern of opening a URL and reading lines, considering this as partial functionality similarity (Type-4). The functions also share API usage (URL, BufferedReader, IOException) and both involve network I/O.
- 共享行为: Both open a URL and read lines using BufferedReader；Both catch IOException
- 行为差异: A extracts substrings from lines to update a map; B validates input, encodes password, calls external service, persists to database, and sends email；A has no logging; B uses extensive logging；A silently catches exceptions; B throws RuntimeException on failure
- 修正建议: Use models that capture hierarchical structure or data flow；Incorporate domain knowledge about common programming patterns (e.g., 'reading from URL')；Train with contrastive learning on BCB-style labels to capture broader notions of similarity

### case_id=2259 FP lexical_or_api_overlap

- 方法: `lookupFutureEvents` vs `getFullScreenUrl`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches and parses meetup.com events JSON to return a list of Event objects.
- B 摘要: Fetches a YouTube page, extracts video parameters, and returns a fullscreen URL string.
- 静态失败原因: Static BERT overfits on lexical/API token overlap (URL, BufferedReader, readLine) and ignores the distinct domain-specific logic and output types.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels as non-clone because the functions have completely different purposes and only share generic I/O boilerplate.
- 共享行为: Both use URL, BufferedReader, and while loop to read HTTP response lines；Both perform string parsing to extract data；Both handle IOException/Exception
- 行为差异: Function A parses JSON, Function B parses HTML/URL parameters；Different domains: meetup vs YouTube；Different output types: List<Event> vs String URL；Different parsing logic and data extraction targets
- 修正建议: Incorporate data flow analysis or API call sequences；Use fine-grained structural embeddings that capture different control flow and data transformation；Include output type and method name context in the representation

### case_id=2260 FN benchmark_preference_bias

- 方法: `copyFile` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Copies a file from source to destination using FileChannel, returning success status.
- B 摘要: Launches a NexOpen project configuration by processing XML files, setting properties, and potentially creating a reverse engineering file.
- 静态失败原因: Static BERT correctly predicted non-clone due to low token and structural similarity; the 'failure' is that the ground truth label is incorrect.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB likely mislabeled this pair; there is no meaningful semantic overlap. Possibly due to a benchmark error or overly broad criterion.
- 行为差异: Function A performs file copy; Function B does project launch configuration.；Function A uses FileChannel for transfer; Function B uses I/O streams and DOM parsing.；Function A is short and straightforward; Function B is long and complex with multiple steps.；Function A returns boolean; Function B does not return a value (void) and throws CoreException.
- 修正建议: Re-annotate the pair as non-clone.；Review BCB annotation guidelines for potential errors.

### case_id=2261 FP lexical_or_api_overlap

- 方法: `sendRequest` vs `loadURL`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Sends an XML request to a servlet using GZIP compression and parses the XML response, returning an empty string.
- B 摘要: Loads a URL with optional Basic Authentication and writes the raw response content to a temporary file, updating a status label.
- 静态失败原因: Model likely relied on lexical/API overlap (URLConnection, openConnection, setRequestProperty, getInputStream) and similar boilerplate, missing the semantic differences in data flow and overall task.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled non-clone because the functions have different purposes (one sends data, one downloads) and produce different outputs, even though they share common networking boilerplate.
- 共享行为: Both open a URLConnection；Both read from the connection's input stream；Both use System.out for debugging；Both handle network exceptions
- 行为差异: sendRequest sends data (POST-like) with GZIP compression; loadURL only reads (GET-like)；sendRequest uses GZIP compression for both output and input; loadURL does not；sendRequest parses response as XML; loadURL writes raw lines to a file；sendRequest uses dialog for server configuration; loadURL uses Basic Auth
- 修正建议: Incorporate data-flow analysis to distinguish between writing to output stream vs. only reading；Use control-flow analysis to capture different branches and exception handling；Include return type and side-effect information；Train with more negative examples that have high API overlap but different semantics

### case_id=2262 FP other

- 方法: `MotixFileItem` vs `readData`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Constructor that copies an InputStream into a ByteArrayOutputStream, optionally reads an image, and stores the stream.
- B 摘要: Static method that parses comma-separated string lists into HashSets and processes a file to populate various data structures.
- 静态失败原因: The low token Jaccard suggests the model likely predicted false positive based on spurious similarities like both having IOException or use of streams, but the actual semantics diverge drastically.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB labels non-clones due to completely different functionalities; no meaningful similarity in output or logic.
- 共享行为: Both involve some form of data processing
- 行为差异: Function A handles a single InputStream and constructs an object; Function B parses multiple static strings and a file into collections；Function A uses try-finally; Function B uses try-catch；Function A deals with images; Function B deals with text tokenization and mapping
- 修正建议: Incorporate structural and semantic awareness beyond lexical overlap；Use contrastive learning with hard negative mining

### case_id=2263 FN benchmark_preference_bias

- 方法: `getResourceAsStream` vs `sendErrorMessage`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Retrieves a resource via URL with caching and returns an InputStream.
- B 摘要: Zips a log file and sends it as an email attachment to technical recipients.
- 静态失败原因: The model correctly recognized the high-level semantic difference, but BCB considered them clones for the boilerplate overlap. Thus, the model failed to meet BCB's lenient standard.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled them as clones due to the presence of similar I/O boilerplate code (file streams, buffered streams, loops) and exception handling patterns, which can be considered partial functionality similarity under a very broad interpretation.
- 共享行为: Both read from files and write to files.；Both use try-catch blocks with printStackTrace.；Both have loops for reading/writing byte buffers.
- 行为差异: A deals with HTTP caching and URL connections, B deals with email sending and zip creation.；A returns an InputStream, B returns void.；A uses a cache hashtable, B does not.；The overall purpose is completely different: resource retrieval vs. error notification.
- 修正建议: Revisit BCB annotation guidelines for consistency; consider removing such pairs if they are not semantically similar.；If retaining, train the model with more emphasis on structural I/O patterns as clone signals, but this may increase false positives.

### case_id=2264 FN benchmark_preference_bias

- 方法: `sendExceptionToServer` vs `doVersionCheck`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `preference_memory_with_manual_audit`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Sends exception details to a server via HTTP POST with URL-encoded parameters.
- B 摘要: Checks for a new version by fetching a version file from a URL and parsing specific lines.
- 静态失败原因: The model likely relied on high-level semantic understanding and lexical overlap (0.218), missing the structural similarity in URL handling and I/O boilerplate, leading to a false negative under BCB's broad criteria.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB often annotates pairs with similar I/O patterns and exception handling as clones, even if the core business logic differs, because they share the same 'pattern' of network communication and error handling.
- 共享行为: Open a URL and establish a network connection；Read lines using BufferedReader from the input stream；Handle IOException with a catch block；Involve URL fetching and I/O operations
- 行为差异: A uses HTTP POST with output stream; B uses HTTP GET with input stream only；A sends exception data; B retrieves and checks version information；A has multiple URL-encoded parameters; B parses lines with specific prefixes；A reads response and prints success/failure; B shows dialogs based on version comparison
- 修正建议: Incorporate structural features like API call sequences or control flow patterns；Use a model that captures partial function similarity or clone type hierarchies；Tune threshold to be more lenient for structural clones

### case_id=2265 FN benchmark_preference_bias

- 方法: `main` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Main method that parses command line flags, loads or creates an Experiment, displays a Swing GUI, optionally saves the experiment on window close, and exits after a nap.
- B 摘要: Method that fetches a resource by URL, caches it locally in a directory structure, and returns an InputStream from cache or network.
- 静态失败原因: Static BERT/GraphCodeBERT likely focused on lexical overlap, which is very low (Jaccard 0.14), and recognized the semantic differences in method names, control flow details, and domain-specific operations (GUI vs HTTP), correctly predicting non-clone.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: None
- 共享行为: Both handle exceptions with try-catch and print stack traces；Both use file I/O streams；Both are public methods in a Weka-related class
- 行为差异: A is a main entry point with GUI interaction and experiment serialization; B is a resource retrieval method with caching logic；A involves user interaction (window closing event); B involves network connections and HTTP status codes；A sleeps and exits; B returns an InputStream or null
- 修正建议: Re-evaluate BCB labeling for such pairs；Consider manual verification of clone labels；Incorporate more semantic features or domain-specific knowledge into models

### case_id=2266 FP lexical_or_api_overlap

- 方法: `getLinksFromURLFast` vs `getWebByUrl`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Extracts all hyperlinks and their text from a given URL and returns them as two vectors.
- B 摘要: Downloads the content of a URL to a file and recursively processes embedded links.
- 静态失败原因: Static models may over-rely on lexical and API-level overlap (URL, URLConnection, BufferedReader) and similar while-readLine structure, ignoring the different purposes and outputs.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels these as non-clones because they have different outputs (returning links vs saving to file) and different secondary behaviors (recursive call, depth control). The shared I/O pattern is not enough for Type-3/4 under BCB strictness.
- 共享行为: Both open an HTTP connection to a URL and read the HTML content using BufferedReader.；Both use similar I/O classes: URL, URLConnection, InputStreamReader, BufferedReader.
- 行为差异: Function A extracts links using regex and returns them; function B writes content to a file and calls another method for link processing.；Function A returns a vector array; function B has void return type.；Function B includes depth control and file I/O; function A does not.；Function A has timing logs; function B has success/failure logging.
- 修正建议: Inject negative examples with high API overlap but different semantics.；Use dataflow or control-flow awareness to distinguish output behaviors.；Consider task-specific fine-tuning with BCB-style annotations.

### case_id=2267 FP boilerplate_overlap

- 方法: `execute` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Processes class files, analyzes bytecode, and injects method calls to instrument code.
- B 摘要: Handles GUI action events to set user preferences and update UI components.
- 静态失败原因: The model likely focused on common structural patterns (try-catch, loops, file I/O) while ignoring the semantic context, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would not label these as clones because they belong to entirely different domains (bytecode instrumentation vs. GUI event handling) with no functional overlap.
- 行为差异: A works on bytecode/class files; B handles GUI events；A reads and writes files via ClassReader/Writer; B uses JFileChooser and preferences；A performs batch processing of multiple resources; B responds to single user actions；A logs injection statistics; B updates UI and stores preferences
- 修正建议: Increase training data diversity to reduce reliance on boilerplate patterns；Incorporate semantic role labeling or domain-specific context

### case_id=2268 FN benchmark_preference_bias

- 方法: `copyFile` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Copies a file from source to destination with a configurable buffer size and optional overwrite.
- B 摘要: Retrieves a resource as an InputStream, caching the content locally and checking for updates via HTTP.
- 静态失败原因: Static BERT models likely rely on token overlap and structural patterns. Low Jaccard (0.198) and different method names/signatures pushed the prediction toward non-clone. The model may miss the deep semantic difference in overall purpose versus surface-level stream operations.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BigCloneBench may label this as a clone (Type-4, functional) because both methods perform file I/O with stream copying, despite different contexts and additional functionality in B.
- 共享行为: Both read from an InputStream and write to an OutputStream in a buffer loop.；Both handle resource closing in try-finally blocks.；Both deal with files: A copies files, B caches resources to files.
- 行为差异: A copies file content directly; B fetches remote resources with caching logic.；B includes network operations (HTTP requests, URL handling) and conditional caching; A does not.；A requires a destination file and overwrite flag; B returns an InputStream and manages cache directory.；B has extensive logging; A does not.
- 修正建议: Improve modeling of functional intent beyond shared boilerplate (e.g., I/O loops).；Use contrastive learning on BigCloneBench to penalize coincidental structural similarities.；Incorporate data flow analysis to differentiate simple copy from caching+network logic.

### case_id=2269 FP partial_functionality

- 方法: `get` vs `executeHttpGet`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Performs an HTTP GET with additional headers and returns an array of GameRecord parsed from non-comment lines.
- B 摘要: Performs an HTTP GET using Apache HttpClient and returns a JSONObject constructed from the response.
- 静态失败原因: The static model may have focused on the shared pattern of HTTP GET, line-by-line reading, and similar keywords (HttpGet, BufferedReader, etc.) without capturing the fundamental differences in data processing and output types.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely labels as non-clone because the functions have distinct purposes and output types despite both being HTTP GET implementations. The specialized headers and parsing in A make it a specific query, while B is a generic utility.
- 共享行为: Both make HTTP GET requests to a URL；Both read the response line by line
- 行为差异: Different HTTP client libraries (HttpURLConnection vs Apache HttpClient)；Different input parameters and headers；Different output types (GameRecord[] vs JSONObject)；Different error handling (returns null vs throws exception)
- 修正建议: Incorporate structured typing information (output type, headers) into the representation；Use data flow analysis to track how the response is processed；Add contrastive training on pairs with high lexical overlap but different semantics

### case_id=2270 FN benchmark_preference_bias

- 方法: `copyFile` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.1`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Copies a file from input to output using file channels.
- B 摘要: Builds a web site for editing by processing XML, reading multiple files, transforming content, and writing output files.
- 静态失败原因: Static BERT/GraphCodeBERT correctly predicted non-clone due to very low token overlap (0.08) and entirely different structure and purpose; the model's reliance on lexical and syntactic similarity led to correct rejection of a false BCB clone label.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB likely labeled this as a clone due to the presence of file I/O in both functions, possibly considering them as Type-4 (similar functionality) clones based on broad file manipulation behavior.
- 共享行为: Both functions involve file I/O operations (reading and writing files).
- 行为差异: Function A is a simple, single-purpose file copy utility.；Function B is a complex, multi-step site builder with XML processing, string manipulation, and looping over pages.；Function A uses NIO FileChannel for efficient transfer; Function B uses traditional streams and file writers.；Function A has minimal error handling; Function B has extensive error handling and debug tracing.
- 修正建议: Re-evaluate the BCB label for this pair; it may be a labeling error.；If retaining the label, update the model to recognize very broad functional similarity based solely on file I/O, which is likely undesirable.

### case_id=2271 FP boilerplate_overlap

- 方法: `readTwitterFead` vs `sendRequest`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a specific Twitter feed via HTTP GET and returns the response body as a string.
- B 摘要: Sends an XML request to a configurable servlet via HTTP POST-like method with GZIP compression and returns an empty string.
- 静态失败原因: The static model likely overemphasized lexical and API-level overlaps (e.g., URL, InputStream, BufferedReader, try-catch) and the common pattern of making an HTTP connection, ignoring the significant differences in HTTP methods, data handling, and return values. The low token Jaccard suggests limited surface similarity, but embeddings may have captured the broad 'HTTP request' category, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB aims for functional similarity. Although both involve HTTP communication, the specific tasks (reading Twitter feed vs. sending XML request) and overall structures differ too much. The overlap is limited to boilerplate I/O and exception handling, which BCB typically does not consider sufficient for a clone.
- 共享行为: Both perform HTTP network requests；Both handle exceptions with catch blocks；Both use I/O streams to read response data；Both construct URLs and open connections
- 行为差异: A uses Apache HttpClient with GET; B uses java.net.URLConnection with output (POST-like)；A has a hardcoded URL; B constructs URL from parameters and preferences；A reads plain text; B uses GZIP compression for both sending and receiving；A returns the full response body; B always returns an empty string
- 修正建议: Incorporate more detailed structural matching that distinguishes HTTP methods (GET vs POST) and input/output signatures；Use dataflow analysis to compare how response data is processed and returned；Add negative mining for pairs with similar boilerplate but different core functionality；Consider functional signatures (return type, parameters) more explicitly

### case_id=2272 FN benchmark_preference_bias

- 方法: `doGet` vs `copyFileTo`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Handles HTTP GET request to retrieve and serve a portal page with permission checks, logging, and caching.
- B 摘要: Copies a file from source path to destination path using a byte buffer.
- 静态失败原因: The static model did not fail; it correctly predicted non-clone. The BCB label itself is erroneous, so the model's prediction aligns with ground truth.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: This pair appears to be a misannotation in BCB; the two functions share no meaningful common functionality beyond basic I/O, which is too broad to justify any clone type.
- 共享行为: Both perform I/O operations (reading/writing)；Both handle exceptions related to I/O
- 行为差异: Function A is an HTTP servlet handler; Function B is a file utility method；Function A has complex control flow with multiple try-catch blocks and conditional logic; Function B is a straightforward sequential stream copy；Function A deals with page objects, user permissions, and caching; Function B only deals with file paths and streams；Function A uses HttpServletRequest/Response; Function B uses FileInputStream/FileOutputStream
- 修正建议: Review and correct the BCB annotation for this pair to non-clone；Alternatively, if the dataset considers any I/O operation as broad clone, then the annotation reflects a lenient criteria, but that seems unlikely

### case_id=2273 FN other

- 方法: `getFile` vs `readAndRewrite`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.2`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file, optionally modifies the endpoint URL in the XML, and returns the file path.
- B 摘要: Reads a DICOM image file, parses it, and writes it to another file.
- 静态失败原因: Static BERT likely correctly identified non-clone due to low token overlap and distinct API usage; the model did not fail.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may have mislabeled due to superficial similarity in file reading/writing patterns, or due to benchmark annotation noise.
- 共享行为: Both involve file I/O operations.
- 行为差异: Function A downloads from a URL and modifies XML; Function B reads DICOM and re-encodes.；Different libraries: AxisFault vs. DICOM libraries.；Function A returns a String; Function B is void.；Different exception handling.
- 修正建议: Review BCB annotation for this pair; likely a false positive in the benchmark.

### case_id=2274 FP lexical_or_api_overlap

- 方法: `actionPerformed` vs `gzip`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Handles various UI action commands by opening file choosers and saving application preferences.
- B 摘要: Compresses a directory into a gzip file using file input/output streams.
- 静态失败原因: The static BERT model likely misclassified due to shallow lexical overlap (both mention 'File' and 'IOException'?) or because it failed to capture the high-level semantic difference due to the large size and complexity of function A, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would not consider these clones because they have completely different purposes and functionality, with no significant code sharing or similar logic beyond basic file I/O.
- 共享行为: Both involve file I/O operations using Java standard library classes.
- 行为差异: Function A is a large event handler with multiple conditional branches; Function B is a simple static method.；Function A interacts with UI components and saves user preferences; Function B performs file compression.；Function A uses JFileChooser and reads file paths; Function B directly writes to a fixed zip file path.；Function A has complex control flow with many nested conditions; Function B has a simple sequential flow.
- 修正建议: Improve training data to include more diverse non-clone pairs with superficial token overlap.；Enhance model capability to understand task-level semantics and control flow.；Integrate code structure or data flow analysis to distinguish different purposes.

### case_id=2275 FP lexical_or_api_overlap

- 方法: `main` vs `readData`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Tests StraightStreamReader by writing bytes to a file and reading them back in various ways.
- B 摘要: Parses a configuration file using StringTokenizers to populate multiple sets and a hash map.
- 静态失败原因: The model likely overemphasized shared API elements like 'IOException', 'File', 'read', and 'while' loops, overlooking the distinct high-level goals.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would not label as clone because the functional purposes are entirely different: one tests a custom stream reader, the other loads configuration data for text processing.
- 共享行为: Both involve file I/O and exception handling
- 行为差异: A is a test for byte-level stream reading; B builds data structures from string tokens；A writes then reads; B only reads；Different output: A prints errors, B populates sets/hash
- 修正建议: Incorporate method name and signature features；Use data flow analysis to capture output differences；Balance lexical overlap with functional context

### case_id=2276 FN benchmark_preference_bias

- 方法: `readIntoList` vs `read`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Reads HTML content from a URL, parses anchor tags to create JMenuItems with action commands and listeners, and populates a map.
- B 摘要: Opens a file or URL stream and reads its contents into an internal buffer, returning a status code.
- 静态失败原因: The static model correctly identified them as non-clones due to low lexical overlap and different purposes; the false negative is due to benchmark preference bias, not model error.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might consider them clones due to superficial similarity of both reading from a URL and using streams, but this is too broad; likely a labeling error.
- 共享行为: Both open a stream from a URL using url.openStream()；Both handle IOException
- 行为差异: Function A parses HTML and creates GUI components; Function B reads raw data and returns a status；Function A has GUI-related actions; Function B is purely I/O
- 修正建议: Re-evaluate BCB annotations for this pair using stricter semantic criteria；Improve benchmark to avoid labeling based on shallow syntactic similarity

### case_id=2277 FN partial_functionality

- 方法: `copyFile` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a file from source to destination, with user confirmation for overwrite and a progress bar.
- B 摘要: Launches a NexOpen project configuration by processing Maven POM files and setting up Hibernate dialect, including copying a reverse engineering file.
- 静态失败原因: Static BERT/GraphCodeBERT models likely focus on token-level and structural features, and the low Jaccard similarity (0.106) and distinct method names ('copyFile' vs. 'launch') made it predict non-clone. The model failed to recognize the shared subfunctionality of file copying.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider these as Type-4 clones due to both methods containing file copying logic (reading from a source and writing to a destination), despite different overall purposes. The shared I/O pattern and resource handling might be seen as functionally similar.
- 共享行为: Both read and write files using Java I/O streams；Both check file existence and handle permissions；Both use try-finally to close resources；Both involve file copying operations (copyFile directly, launch copies a reverse engineering file)
- 行为差异: copyFile is a standalone file copy utility; launch is part of an Eclipse plugin launch framework；copyFile interacts with user via console; launch uses Eclipse progress monitor；copyFile copies a single file; launch processes multiple XML files and project configurations；copyFile displays progress as '#' characters; launch has no progress display
- 修正建议: Incorporate subgraph matching to detect shared I/O patterns；Use contrastive learning with partial functional similarity labels；Add heuristics for file manipulation common substructures

### case_id=2278 FP partial_functionality

- 方法: `readTwitterFead` vs `getWebByUrl`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches a fixed Twitter timeline URL and returns the response body as a string.
- B 摘要: Downloads a web page from a given URL, saves it to a file, and recursively follows links for web crawling.
- 静态失败原因: The static model likely overemphasized the common structural pattern of HTTP GET followed by line-by-line reading in a try-catch block, while ignoring the different return types, additional functionality (file writing, recursive calls), and overall intent.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB labels it as non-clone (0) because the functions differ in purpose, output, and control flow; one is a simple data fetcher, the other is a web crawler. Even though they share some syntactical patterns, the semantic gap is large.
- 共享行为: Both perform HTTP GET requests to retrieve content from a URL；Both read the response line by line using a BufferedReader；Both use try-catch blocks to handle IO exceptions
- 行为差异: Function A returns the content as a String, while function B writes it to a file and does not return；Function A uses a fixed URL, function B accepts a URL parameter；Function A uses HttpClient, function B uses URLConnection；Function B recursively calls getUrlByString to follow links, function A does not
- 修正建议: Incorporate dataflow analysis to track variable usage and side effects；Consider the method signature (return type, parameters) as a strong signal；Use whole-method embedding that captures control flow and I/O operations

### case_id=2279 FN partial_functionality

- 方法: `sendExceptionToServer` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends exception details to a server via HTTP POST, constructing a query string with various encoded parameters.
- B 摘要: Sends a POST request to a social network API with predefined parameters and prints the response.
- 静态失败原因: Static models like CodeBERT may rely heavily on token overlap and method names, overlooking structural similarities in the HTTP request flow due to different API calls and low Jaccard similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considers the common pattern of HTTP POST request construction and execution as sufficient functional similarity, despite different parameter purposes and endpoints.
- 共享行为: Both build URL-encoded parameter strings for an HTTP POST request；Both open a URL connection, set doOutput(true), write the data, and read the response line by line；Both print server responses or error messages to stdout
- 行为差异: Code_a sends exception data (stack trace, OS info) to an error server, while Code_b sends hardcoded social network API parameters；Code_a uses URLConnection (generic), Code_b uses HttpURLConnection and sets request method explicitly；Code_a checks for 'success' response and prints accordingly, Code_b prints response code and message unconditionally
- 修正建议: Incorporate structural similarity measures like AST-based or flow-based features；Train on more varied examples of common design patterns (e.g., HTTP request boilerplate) to recognize non-literal similarity；Use contrastive learning to align representations of functionally similar code with different surface forms

### case_id=2280 FN benchmark_preference_bias

- 方法: `doGet` vs `testCopy_readerToWriter_nullIn`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Servlet doGet method handling HTTP GET requests, retrieving a page parameter, checking user permissions, caching, and error handling.
- B 摘要: JUnit test method testing IOUtils.copy with null reader, expecting NullPointerException.
- 静态失败原因: The static model correctly predicted non-clone; the BCB label appears incorrect, so the model did not fail but was penalized by the benchmark.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: This pair likely should not be considered a clone even under BCB's broad Type-3/Type-4 criteria due to zero functional overlap. The BCB label may be an annotation error.
- 共享行为: None
- 行为差异: One is a web request handler, the other is a unit test.；Different input/output types and operations.；Completely different logic and purpose.
- 修正建议: Review and correct the BCB label for this pair. The model's prediction is sound.

### case_id=2281 FP boilerplate_overlap

- 方法: `truncate` vs `readData`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Truncates a file by compressing it to a zip archive and deleting the original if it is older than the JVM start time.
- B 摘要: Reads and parses configuration data from static strings and a file to populate data structures for Tibetan transliteration.
- 静态失败原因: The model likely relied on surface-level similarities such as both using I/O, exception handling, and loops, without capturing the distinct semantic contexts.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels as non-clone because the functions have completely different purposes and no functional similarity beyond generic Java constructs.
- 共享行为: Both use Java I/O operations (FileInputStream in A, BufferedReader in B)；Both handle exceptions with try-catch-finally blocks
- 行为差异: A compresses a file into a zip archive; B parses tokens and builds sets/maps；A operates on a single file with date-based backup; B reads from multiple string sources and a file with complex parsing logic；A deletes the source file; B does not delete any files；A uses logging; B uses System.out for output
- 修正建议: Incorporate structural matching or control-flow analysis to differentiate I/O patterns；Use data flow analysis to track the actual data transformations；Train with more diverse negative examples to reduce false positives on boilerplate-heavy code

### case_id=2282 FN benchmark_preference_bias

- 方法: `doTransfer` vs `testNetworkHTTP`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Transfers an HTTP request and response by forwarding headers and body between a client and a target server.
- B 摘要: Tests network connectivity by making multiple HTTP GET requests to predetermined URLs and discarding the responses.
- 静态失败原因: Static BERT relies on token overlap and local syntax; low token Jaccard (0.1349) and differing structures led to a non-clone prediction. However, BCB's label suggests a functional similarity that the model missed, but we judge BCB's label is likely erroneous.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled these as clones due to superficial similarity in using HttpURLConnection and reading streams, overlooking significant differences in purpose and behavior.
- 共享行为: Both open HTTP connections using HttpURLConnection；Both read from input streams and handle IOException
- 行为差异: A copies request headers and body from incoming request; B does not；A sets request method based on parameter; B only uses GET；A outputs response to servlet response; B discards all response data；A handles response status and sends errors; B does not
- 修正建议: Improve training data by filtering out false positive annotations from BCB；Use more robust functional similarity measures beyond surface tokens

### case_id=2283 FN partial_functionality

- 方法: `copyResource` vs `readAndRewrite`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource (URL or file) to a destination file using byte-by-byte read and write.
- B 摘要: Reads a DICOM image file, parses it, reads pixel data, and writes it to an output file using DICOM-specific APIs.
- 静态失败原因: Static BERT methods rely on token overlap and code structure; the low Jaccard (0.1) and different library APIs (java.io vs. DICOM-specific) cause the model to miss the high-level functional similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considers both as 'copy' operations at a high level, despite different implementations and domains, fitting a Type-4 clone category.
- 共享行为: Both involve reading from an input source and writing to an output destination.；Both handle I/O resources and may throw exceptions.
- 行为差异: A uses simple byte stream copy; B uses complex DICOM parsing and pixel data handling.；A is generic (any resource); B is specific to DICOM medical image format.；A writes raw bytes; B writes structured DICOM dataset with headers.
- 修正建议: Improve model's ability to recognize high-level semantic similarity beyond lexical tokens.；Use graph-based or dataflow-based representations to capture I/O operations.；Incorporate domain-specific knowledge or functional abstraction.

### case_id=2284 FN dataflow_blindspot

- 方法: `copyResource` vs `copyFromTo`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `dynamic_equivalence_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Copies a resource from URL or local file to a destination file using streams
- B 摘要: Copies a file to another file using NIO channels, with error messages and timestamp preservation
- 静态失败原因: Static methods like GraphCodeBERT rely on token overlap and surface structure; low Jaccard (0.119) and different API usage (NIO vs IO) lead to low similarity, missing the underlying functional equivalence.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行价值高：该样本可能是 API 写法不同但行为等价的漏报。建议测试目标为 input_output_equivalence。
- BCB 偏好解释: BCB often annotates based on functional similarity in file copying, ignoring specific I/O APIs and error handling details, considering both as Type-4 clones (broadly equivalent).
- 共享行为: Copy bytes from a source to a destination file
- 行为差异: Source type: URL or file vs only file；Error handling: throws exception vs prints messages and exits；I/O method: InputStream/OutputStream vs FileChannel.transferTo；Extra timestamp preservation in code_b
- 修正建议: Train model to recognize high-level semantic equivalence across different I/O APIs；Use data flow analysis that abstracts stream operations

### case_id=2285 FP lexical_or_api_overlap

- 方法: `copyFile` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Copies a file from source to destination using FileChannel.
- B 摘要: Handles UI action events by setting preferences, opening file choosers, and updating UI components.
- 静态失败原因: The model likely over-relied on overlapping file-related API tokens (e.g., File, getAbsolutePath) and ignored the drastically different control flow and purpose, due to limited long-range context understanding.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would label non-clone because the functions have entirely different functionality and structure; one is a file copy utility, the other is a GUI event handler.
- 共享行为: Both involve file handling but at different levels (file copy vs file selection).
- 行为差异: Function A is a utility that copies file contents; Function B is a GUI event handler with multiple conditional branches.；Function A has simple linear control flow; Function B has complex branching and UI interactions.；Function A does not interact with UI; Function B updates UI components and shows dialogs.
- 修正建议: Train with more diverse non-clones that share lexical tokens but differ in semantics.；Incorporate dataflow or structural analysis to capture control flow differences.；Use contrastive learning to distinguish similar API usage from actual semantic similarity.

### case_id=2286 FN partial_functionality

- 方法: `importRoles` vs `read`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Parses XML-like role name data from a URL and returns a list of RoleName objects.
- B 摘要: Opens an input stream from a URL or file and reads it via another method, returning a status code.
- 静态失败原因: The static model likely focused on structural and semantic differences (different return types, different loop/logic) and low token overlap, correctly predicting non-clone; but BCB labeled as clone based on partial I/O pattern similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider these as clones because they share a common pattern of opening a URL stream and handling I/O exceptions, which is a broad Type-4 similarity.
- 共享行为: Both functions create a URL object from a string parameter.；Both open an input stream from the URL.；Both handle IOException with try-catch.
- 行为差异: A parses multiple lines looking for XML tags to extract RoleName objects; B delegates reading to a separate 'read' method and returns an integer status.；A returns an ArrayList<RoleName>; B returns an int.；A only handles URLs; B handles both URLs and local files.
- 修正建议: Improve detection of partial functionality by considering high-level I/O patterns.；Re-evaluate BCB label for consistency with typical clone definitions.

### case_id=2287 FN boilerplate_overlap

- 方法: `DialogHelper` vs `getFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Constructor that creates a dialog with an image and a save button, handling file copying via FileChannel.
- B 摘要: Static method that downloads a WSDL file from a URL, modifies its endpoint, and saves it to a temp directory.
- 静态失败原因: GraphCodeBERT likely correctly identified low lexical similarity and different overall tasks, but the model's strict definition correctly predicts non-clone; the BCB label is an outlier.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may have labeled these as clones due to the similar FileChannel-based file copying pattern and the structural similarity in exception handling, considering it a Type-3 clone with partial functionality overlap.
- 共享行为: Both use FileChannel to copy file data.；Both check if a file exists before overwriting.；Both handle IOException and close streams in finally blocks.
- 行为差异: Function A is a GUI constructor; Function B is a service method.；Function A saves an image from a URL; Function B downloads and modifies an XML file.；Error handling: A shows dialog warnings; B throws AxisFault exceptions.；Function A uses JFileChooser for user interaction; Function B has no GUI.
- 修正建议: Exclude common boilerplate patterns (e.g., FileChannel copy) from clone detection.；Incorporate task-level semantics via function name or context embeddings.

### case_id=2288 FP long_range_semantics

- 方法: `actionPerformed` vs `forBundle`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `static_summary_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Handles user UI actions to set application preferences like Graphviz path, ImageMagick path, date format, look-and-feel, etc.
- B 摘要: Manipulates an OSGi bundle by zipping its template files, updating the manifest, and reinstalling the plugin.
- 静态失败原因: The model may have been misled by shared structural patterns like conditionals and loops, or by common words like 'file', 'name', 'set', but the long-range semantic differences (UI event handling vs bundle packaging) were not captured due to attention limitations.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely labels this as non-clone because the functions have completely different purposes, inputs, outputs, and domains (UI settings vs OSGi bundle manipulation). The low token overlap and distinct APIs further support non-cloneness.
- 共享行为: Both involve file handling (file chooser vs zip streams)；Both update some configuration or plugin state
- 行为差异: A is UI event-driven; B is a private utility method；A writes preferences using Suku.kontroller; B writes to a temporary JAR file；A has many conditional branches for different commands; B has a fixed pipeline；A interacts with Swing components; B interacts with OSGi framework
- 修正建议: Train with better contrastive examples to distinguish UI logic from backend logic；Use structure-based features (e.g., AST) to capture functional roles；Increase dataset diversity across programming domains

### case_id=2289 FN benchmark_preference_bias

- 方法: `copyFile` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Copies a source file to a destination file with overwrite confirmation and a progress bar using '#' characters.
- B 摘要: Builds a site for editing by reading and transforming XML files, then writing the output to multiple files with various parameter configurations.
- 静态失败原因: The static model correctly identified them as non-clones due to low lexical overlap (Jaccard 0.123) and clearly different semantics, but BCB's label indicates a false positive in the benchmark, so the model's failure is actually a success in avoiding a false negative.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this pair as clones based on the loose criterion of both involving file I/O and exception handling, which is a very broad Type-4 similarity not typically considered a valid clone.
- 共享行为: Both perform file I/O operations (reading and writing files).；Both handle IOExceptions.
- 行为差异: Function A is a simple file copy with user interaction for overwrite; Function B is a complex site generation with XML transformation and string replacement.；Function A copies a single file; Function B processes multiple pages and writes transformed content.；Function A uses a progress indicator; Function B does not.
- 修正建议: Improve benchmark annotation to reject such functionally unrelated pairs.；Enhance clone detection to focus on specific functional behavior rather than generic I/O patterns.

### case_id=2290 FN boilerplate_overlap

- 方法: `convert` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.75`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Converts an ACRNEMA file to DICOM format, handling pixel data and validation.
- B 摘要: Downloads a KMZ file and extracts its entries to local files.
- 静态失败原因: Static BERT models rely on token overlap and method name similarity; low Jaccard (0.152) and different method signatures cause a non-clone prediction.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may label them as clones due to the broad structural similarity of reading from an input stream and writing to an output stream, despite different domain-specific logic.
- 共享行为: Both use InputStream and OutputStream for reading and writing data.
- 行为差异: Input source: file vs URL.；Processing logic: DICOM conversion (format validation, pixel data handling) vs zip extraction.；Output: single DICOM file vs multiple extracted files.；Error handling and validation are specific to each task.
- 修正建议: Add features capturing control flow and data dependencies.；Incorporate high-level functional purpose via documentation or comments.

### case_id=2291 FP lexical_or_api_overlap

- 方法: `importRoles` vs `downloadFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Parses role names from XML data fetched from a URL.
- B 摘要: Downloads a file from a URL and saves it to disk with progress tracking.
- 静态失败原因: Likely due to lexical/API overlap: both use URL, openStream, BufferedReader/BufferedInputStream, and a reading loop, which may have misled the model to ignore the high-level purpose.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clone because the core functionality (parsing vs downloading) is entirely different despite similar I/O patterns.
- 共享行为: Both open a URL connection and read data from it.
- 行为差异: A reads line by line and parses XML; B downloads binary file chunks.；A returns ArrayList of RoleName; B returns boolean and saves to file.；B has progress updates and handles file creation/deletion.
- 修正建议: Incorporate dataflow or program dependency graphs to distinguish parsing logic from binary I/O.；Use contrastive learning or more diverse negative samples to reduce sensitivity to boilerplate patterns.；Enhance modeling of return types and library-specific calls like MessageFrame.

### case_id=2292 FP partial_functionality

- 方法: `callService` vs `executePost`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Private void method performs a GET request to a pre-configured URL, reads response line by line, and stores result in instance variable 'answer', handling MalformedURLException and IOException.
- B 摘要: Private String method performs a POST request with URL parameters using HttpURLConnection, writes parameters, reads response appending carriage returns, returns response string, and handles generic Exception with stack trace.
- 静态失败原因: The static BERT model likely overemphasized shared API calls (URL, BufferedReader, StringBuffer, try-catch) and general structure, missing the critical semantic difference between GET and POST, as well as the different data flow and error handling patterns.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely labels these as non-clones because they are not functionally equivalent even at a broad Type-3 level; the differences in HTTP method, signature, and error handling mean they are not interchangeable for the same task.
- 共享行为: Both create a URL and open an input stream to read the response.；Both use BufferedReader and StringBuffer to read and accumulate lines.；Both handle exceptions (though differently) and close the reader.；Both ultimately obtain the HTTP response content as a string.
- 行为差异: Method A is a GET request without parameters; Method B is a POST request with URL parameters.；Method A is void and stores result in a field; Method B returns the response string.；Method B uses explicit HttpURLConnection, sets request method and properties, writes data with DataOutputStream, and disconnects in finally.；Method B appends '\r' after each line; Method A does not.
- 修正建议: Train the model to distinguish different HTTP methods by paying attention to HttpURLConnection setup and DataOutputStream.；Incorporate type and return type awareness (void vs String).；Use control-flow and data-flow analysis to capture differences in how parameters are passed and responses are returned.；Augment training data with more varied HTTP request implementations.

### case_id=2293 FP boilerplate_overlap

- 方法: `readRemoteFile` vs `getUser`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a remote file line by line and returns its content as a single string.
- B 摘要: Retrieves a User object from a DAO, or falls back to parsing a config file to create and save the User.
- 静态失败原因: The model likely over-relied on the similar structure (URL, BufferedReader, while loop, exception handling) and token overlap, missing the higher-level semantic difference.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would likely label these as non-clones because their overall functionality and output are completely different; only some boilerplate code overlaps.
- 共享行为: Both use BufferedReader to read lines from a stream；Both handle IOException with try-catch；Both check for null to determine end of stream
- 行为差异: A returns a String (file content), B returns a User object；A reads from a remote URL, B reads from a classpath resource；B involves DAO interaction and conditional logic (only reads config if user not found)；B parses lines with StringTokenizer to extract fields, A simply concatenates
- 修正建议: Incorporate dataflow analysis to distinguish return type and external calls；Use method name and signature as features；Train with more examples that share boilerplate but differ in purpose

### case_id=2294 FN partial_functionality

- 方法: `modifyApplicationMessage` vs `hyperlinkUpdate`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Modifies a localized properties file by updating or adding a key-value pair for a given locale.
- B 摘要: Handles a hyperlink activation event by fetching the URL content and displaying it in a dialog.
- 静态失败原因: A static model might fail to distinguish the high-level purpose due to limited reasoning about the overall program logic; it might focus on the presence of common I/O patterns and exception handling.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled these as clones due to a broad interpretation of Type-4 (semantic equivalence) where both methods involve I/O and exception handling, or due to an annotation error.
- 共享行为: Both use try-catch for exception handling；Both perform I/O operations (reading/writing streams)
- 行为差异: Method A modifies a file on disk, Method B reads from a URL and displays in UI；Method A deals with properties file format, Method B deals with arbitrary text content；Method A has specific key-value replacement logic, Method B has UI dialog creation
- 修正建议: Train model to better capture overall semantic goal beyond low-level operations；Incorporate code structure to distinguish between file modification and UI event handling

### case_id=2295 FN lexical_or_api_overlap

- 方法: `doVersionCheck` vs `invoke`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Checks for software version by reading version numbers from a remote URL and calling another method.
- B 摘要: Invokes a remote service method via HTTP POST, reads response, handles retries on timeout.
- 静态失败原因: The model likely relied heavily on lexical token overlap, which is low (Jaccard 0.14). It also may have been misled by different method names ('doVersionCheck' vs 'invoke'), different APIs (java.net.URL vs Apache HttpClient), and different control structures (UI cursor, retry). It failed to capture the common underlying semantic pattern of HTTP communication and line-by-line reading.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BigCloneBench may consider these clones because both involve a common pattern of opening a network connection to a URL, reading lines from the response, and processing them. The higher-level behavior of 'fetch and parse data from remote server' is similar, even though the specific data and error handling differ.
- 共享行为: Both perform an HTTP request to a URL；Both read response line by line using BufferedReader；Both handle IO-related exceptions
- 行为差异: A uses HTTP GET for version check; B uses HTTP POST for RPC；A shows/hides wait cursor on view; B implements retry logic with service discovery；A looks for specific line prefixes; B parses entire response as JSON；A calls another method after reading; B returns deserialized object
- 修正建议: Enhance model with data-flow or control-flow abstractions that capture network I/O patterns；Include synonym or API mapping between java.net.URL and HttpClient；Use a clone detector that focuses on behavioral similarity rather than exact API；Train on more diverse Type-4 examples with low lexical overlap

### case_id=2296 FN partial_functionality

- 方法: `File2String` vs `doVersionCheck`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a file from filesystem or classpath and returns its contents as a string.
- B 摘要: Fetches a version check URL, reads lines to extract build versions, and performs version check.
- 静态失败原因: The static model likely relied on token overlap and structural similarity; low Jaccard similarity (0.2289) and different method names/purposes led to a non-clone prediction, missing the shared sub-routine that BCB considered significant.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled these as clones due to the shared code pattern of reading lines from an input stream using BufferedReader, which qualifies as a Type-3 clone (partial functional similarity) under a broad interpretation of clone types.
- 共享行为: Both open an InputStream；Both create a BufferedReader from the InputStream；Both read lines in a while loop using readLine()
- 行为差异: A reads from a File or classpath resource; B reads from a URL；A aggregates all lines into a StringBuffer and returns the string; B parses lines for version info and calls another method；A handles file not found with System.exit; B shows wait cursor and error dialog；B has UI-related operations (show/hide wait cursor) absent in A
- 修正建议: Incorporate sub-graph matching to detect common code fragments like input reading loops；Use a hierarchical embedding that captures nested functionality；Augment training data with partial clones that share common sub-routines

### case_id=2297 FN partial_functionality

- 方法: `copyFileTo` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.95`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a local file to another local file using file streams.
- B 摘要: Retrieves a resource by name, either from a local cache or by downloading from a URL, and returns an InputStream.
- 静态失败原因: Static BERT models rely on token and structural overlap, which is low (Jaccard=0.147). The functions have different APIs, lengths, and contexts, so the model missed the algorithmic IO copy pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often annotates Type-3/Type-4 clones based on shared sub-functionality. Here, both methods implement an IO copy loop (read from input, write to output) which is a common pattern, despite different overall purposes.
- 共享行为: Both involve reading from an InputStream and writing to an OutputStream using a buffer loop.
- 行为差异: Function A copies a local file to another local file with fixed paths; Function B retrieves a resource from a URL or cache, with HTTP handling and caching.；Function A returns void; Function B returns an InputStream.；Function B includes error handling, caching logic, and HTTP protocol specifics.；Function A uses FileInputStream/FileOutputStream directly; Function B uses Buffered streams and URL connections.
- 修正建议: Use data-flow aware models that capture control and data dependencies.；Train with contrastive learning on sub-graphs to identify shared algorithmic patterns.；Incorporate higher-level semantic features like I/O operations and stream handling.

### case_id=2298 FN partial_functionality

- 方法: `testNetworkHTTP` vs `invoke`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: A test method that performs multiple HTTP GET requests to hardcoded URLs, reading and discarding the response lines.
- B 摘要: A generic RPC method that sends an HTTP POST request to a service endpoint, reads the response, parses JSON, and retries on timeout.
- 静态失败原因: Low token Jaccard similarity (0.1136) and different method names, API calls, and overall control flow caused the static BERT model to miss the shared HTTP reading pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label these as clones due to both sharing the common pattern of opening an HTTP connection, wrapping the input stream in a BufferedReader, and reading lines, which is a functionally similar substructure even though overall purposes differ.
- 共享行为: Both establish HTTP connections and read response streams line by line using BufferedReader.
- 行为差异: A uses GET requests; B uses POST requests.；A discards all response content; B parses JSON and returns deserialized object.；A makes multiple sequential requests; B makes a single request with retry logic.；A uses java.net.HttpURLConnection; B uses Apache HttpClient.
- 修正建议: Enhance models to recognize common substructures like HTTP stream reading even when embedded in different larger tasks.；Incorporate graph-based representations that capture data flow and API usage patterns.；Use contrastive learning with carefully curated partial functionality positives.

### case_id=2299 FP boilerplate_overlap

- 方法: `main` vs `copyFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Generates adapter classes from a Prolog file, parsing, visiting, and writing JAR output.
- B 摘要: Copies a file using NIO FileChannel with proper resource management.
- 静态失败原因: Static BERT may have overestimated similarity due to overlapping tokens like 'File', 'IOException', 'try', 'catch', and 'close()', which are common in I/O operations, leading to a false positive despite low Jaccard and differing semantics.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels as non-clone because the functions have entirely different purposes (code generation vs. file copy) and share only trivial boilerplate I/O and exception handling, which is insufficient for Type-3/4 similarity.
- 共享行为: Both handle files (reading/writing)；Both use try-catch for exception handling；Both involve file I/O operations
- 行为差异: A is a complex code generation pipeline; B is a simple file copy；A interacts with Prolog parser, visitors, class loaders; B only uses NIO channels；A produces multiple outputs (JAR, resources); B produces a single output file；A uses command-line arguments; B takes two File parameters
- 修正建议: Improve attention to domain-specific APIs and structural differences；Include program dependency or data flow information；Use contrastive learning to distinguish boilerplate-heavy non-clones

### case_id=2300 FN partial_functionality

- 方法: `read` vs `lookupFutureEvents`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a file or URL and returns a status code.
- B 摘要: Fetches future events from a Meetup API, parses JSON, and returns a list of Event objects.
- 静态失败原因: The static BERT model relies on lexical and syntactic features with low token Jaccard (0.1465), and the functions differ significantly in method names, parameters, return types, and internal logic, causing it to miss the semantic overlap of the URL-reading sub-pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this as a clone because both functions share a core pattern of opening a URL, reading input, and handling IOExceptions, which fits their broad Type-4 partial functionality similarity criteria.
- 共享行为: Both open a URL connection and read input from a stream.；Both handle IOException (one sets status, one throws custom exception).
- 行为差异: Function A reads from a file or URL based on input name; Function B always calls a hard-coded API URL.；Function A returns an integer status; Function B returns a list of Event objects after JSON parsing.；Function B has extensive data extraction and object creation; Function A delegates to another read method and only returns status.；Function B uses BufferedInputStream vs BufferedReader (different reading patterns).
- 修正建议: Enhance model with data-flow analysis to detect common sub-patterns like URL opening.；Use contrastive learning on pairs sharing partial functionality.；Include AST-based similarity that captures structural templates.

### case_id=2301 FP boilerplate_overlap

- 方法: `run` vs `checkForUpgrade`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Opens a URL to a local JSP and reads/discards all lines, catching exceptions.
- B 摘要: Checks for software upgrade by querying a remote server, processing license and upgrade records, updating database, and showing UI messages.
- 静态失败原因: The model likely overemphasized the shared I/O boilerplate (URL, BufferedReader, readLine) while ignoring vast differences in processing logic and side effects. The disparity in code length and structure was not sufficiently captured.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels this as non-clone because the token overlap is very low (0.09) and the functionality is completely different. BCB requires significant functional similarity, which is absent here.
- 共享行为: Both open a URL and read lines using BufferedReader
- 行为差异: Function A discards all read data; Function B processes data for license and upgrade info.；Function A has no side effects; Function B modifies UI and database.；Function A is a simple fire-and-forget; Function B involves complex conditional logic and multiple branches.；Function A has no parameters; Function B takes an Event and uses helper methods.
- 修正建议: Enhance model's ability to distinguish boilerplate from core logic.；Incorporate structural features like method length and AST depth to penalize size mismatches.；Focus attention on the processing steps after I/O to detect semantic divergence.

### case_id=2302 FP partial_functionality

- 方法: `readURL` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a URL line by line and prints each line to standard output.
- B 摘要: Searches Google images, parses HTML to extract image URLs, and updates a GUI with the first image.
- 静态失败原因: The model may have been misled by the common structural pattern of opening a URL, reading with BufferedReader, and exception handling, ignoring the distinct post-processing and purpose.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely labels this as non-clone because the overall functionality differs significantly despite sharing generic I/O patterns; the methods serve entirely different purposes (simple url printing vs. image search with GUI).
- 共享行为: Both open a network connection to a URL；Both use BufferedReader to read data；Both handle I/O exceptions
- 行为差异: A prints lines to console, B extracts specific URLs from HTML；B constructs a search URL and sets HTTP headers；B updates GUI components after processing；A uses finally block for resource cleanup, B closes reader inside try
- 修正建议: Train models to consider the full dataflow and ultimate usage of read data；Use contrastive learning with functional labels；Incorporate method name semantics more heavily

### case_id=2303 FN partial_functionality

- 方法: `sendExceptionToServer` vs `addDataFromURL`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.5`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends exception details to a server via HTTP POST with encoded parameters and reads the response.
- B 摘要: Reads data from a URL via HTTP GET and appends lines to a StringBuilder, with fallback on error.
- 静态失败原因: Static BERT/GraphCodeBERT models rely on lexical overlap and exact structural patterns; the low token Jaccard (0.22) and different method names/signatures led the model to predict non-clone, missing the high-level similarity in network communication that BCB might consider.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this as a clone due to both functions performing network I/O operations with similar structural patterns (try-catch, stream handling), considering them as Type-3/Type-4 partial functionality clones.
- 共享行为: Uses Java networking (URL, streams) to communicate with a server；Handles exceptions with try-catch blocks；Uses BufferedReader and InputStreamReader for reading data
- 行为差异: Function A writes data to the server (POST), while Function B reads data from the server (GET)；Function A constructs a complex query string with multiple encoded parameters, while Function B only reads raw response；Function A processes the server response and prints based on success, while Function B appends data to a global object and has minimal output
- 修正建议: Enhance models with functional semantics understanding beyond lexical overlap；Incorporate global contexts such as surrounding code or documentation to infer high-level tasks；Use contrastive learning to differentiate between shared patterns and core behaviors

### case_id=2304 FN benchmark_preference_bias

- 方法: `main` vs `convert`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.5`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Extracts a ZIP file from a URL and writes its entries to individual files using Java I/O streams.
- B 摘要: Converts an ACRNEMA stream file to DICOM format by adding UIDs and handling pixel data with inflation and verification.
- 静态失败原因: The model correctly predicted non-clone due to low token overlap and distinct API usage; BCB's label likely reflects a high-level functional similarity not captured by token-based models.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as a clone due to both methods performing file I/O operations and data transformation, interpreting them as broad Type-4 clones under a 'file processing' category, despite differing semantics.
- 共享行为: Both involve reading input streams and writing output streams；Both use BufferedOutputStream for output；Both handle IOException
- 行为差异: A processes ZIP entries from a URL; B processes raw pixel data from a local file；A writes multiple output files; B writes a single output file with additional metadata tags；B includes complex logic for DICOM-specific tasks like UID generation, group length writing, and pixel data inflation；A is a main method; B is an instance method with multiple parameters
- 修正建议: Re-evaluate BCB label for correctness; consider removing or reclassifying this pair；If retaining clone label, use models that incorporate high-level program semantics or task categories；Include functional similarity metrics beyond token overlap, such as data flow or I/O pattern analysis

### case_id=2305 FN partial_functionality

- 方法: `getResourceAsStream` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Retrieves a resource via URL with caching, eventually returning an InputStream from the local cache or network.
- B 摘要: Copies a file from source to destination using FileChannel.transferTo.
- 静态失败原因: Low token overlap (Jaccard 0.066) and differing method signatures/lengths likely prevented the model from recognizing the underlying shared I/O behavior. The model focused on surface-level differences.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider this a clone because both functions perform a core file copy operation (reading bytes from a source and writing to a destination) albeit in different contexts and with different additional functionalities.
- 共享行为: Both involve reading from an input source and writing to an output destination (I/O operation).；Both handle file streams (FileInputStream, FileOutputStream) or equivalent.
- 行为差异: A is a resource retrieval method with caching logic and HTTP handling; B is a straightforward file copy.；A returns an InputStream; B is void and throws IOException.；A uses buffered streams and prints debug info; B uses NIO channels.；A handles exceptions broadly and cleans up; B lets exceptions propagate.
- 修正建议: Enhance model with capability to detect shared sub-structures or data flow patterns.；Use hybrid approaches combining lexical and semantic methods (e.g., graph-based code understanding).

### case_id=2306 FP lexical_or_api_overlap

- 方法: `run` vs `checkForUpgrade`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `1.0`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Downloads a tile from a URL (file or http), parses it as GeoJSON, constructs vector geometries, and adds them to a display data source.
- B 摘要: Checks for software upgrades by querying a remote server with client version and MAC list, parses the XML-like response, updates a local database with installation records, and shows UI components accordingly.
- 静态失败原因: The static model likely overfit on common API sequences (URL, openConnection, BufferedReader, readLine, IOException handling) present in both functions, ignoring the drastically different overall functionality and domain context.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically does not treat two functions as clones if their high-level purpose and domain are different, even if they share low-level I/O patterns. Here, one is a tile renderer and the other is a software updater, which are semantically unrelated.
- 共享行为: Both use HTTP connections to fetch data from URLs；Both read lines from a BufferedReader and concatenate into a string；Both handle IOException and MalformedURLException
- 行为差异: A fetches tile data for rendering; B fetches upgrade metadata for software management；A parses GeoJSON and creates geometry objects; B parses an XML-like response and processes database rows；A updates a display cache and data loader; B writes to a database table and manipulates UI visibility；A uses synchronized blocks for thread safety; B is a static utility method without synchronization
- 修正建议: Incorporate data flow and control flow analysis to differentiate similar API usage in different semantic contexts；Use contrastive learning to penalize superficial similarity when high-level intent diverges；Add domain-specific features (e.g., import statements, class hierarchy) to disambiguate

### case_id=2307 FP long_range_semantics

- 方法: `getMessageDigest` vs `perform`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `static_summary_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Computes SHA-1 hash of input string and returns BASE64 encoded hash.
- B 摘要: Handles a web request to classify a concept, involving session management, parameter parsing, XML construction, HTTP communication, and result processing.
- 静态失败原因: The static model may have been misled by common boilerplate patterns (e.g., try-catch, string encoding) or failed to capture the long-range semantics of Function B's complex flow, leading to a false positive.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely labels as non-clone because the functions have entirely different purposes and no meaningful functional overlap, even at a broad Type-3/4 level.
- 共享行为: Both use exception handling (try-catch blocks).；Both involve encoding/decoding (BASE64 in A, URL encoding in B).
- 行为差异: Function A is a simple utility method for hashing; Function B is a complex web action handling multiple business logic steps.；Function A takes a single string input and returns a string; Function B takes multiple objects (mapping, form, request, response) and returns an ActionForward.；Function A has no side effects; Function B modifies session attributes and performs I/O operations.；Function A's logic is straightforward and short; Function B contains conditional branching, loops, and external API calls.
- 修正建议: Improve model's ability to capture long-range dependencies in large functions.；Incorporate task-specific structural cues (e.g., method signatures, type information).；Use cross-function attention or context-aware embeddings to distinguish utility methods from business logic actions.

### case_id=2308 FN partial_functionality

- 方法: `copy` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a file from source path to destination path using FileChannel.
- B 摘要: Retrieves a resource (possibly from network) and caches it locally, returning an InputStream.
- 静态失败原因: Low token Jaccard (0.097) and different method names, control flow, and I/O types led the static model to focus on surface-level differences, missing the abstract similarity of data copying.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as 'copying data from a source to a destination', abstracting away the specific source/destination types and focusing on the data transfer pattern.
- 共享行为: Both involve reading data from an input source；Both write data to a file (destination or cache)
- 行为差异: A copies between local files; B retrieves from network or cache；A returns void; B returns InputStream；A uses FileChannel for transfer; B uses BufferedStream for writing；B includes caching logic and HTTP handling; A does not
- 修正建议: Use data-flow analysis to capture abstract operations like 'read' and 'write'；Train on semantic equivalence pairs with diverse I/O patterns；Incorporate API call semantics to recognize similar operations across different libraries

### case_id=2309 FN benchmark_preference_bias

- 方法: `modifyApplicationMessage` vs `copyFileTo`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Modifies a locale-specific properties file by updating or adding a key-value pair, possibly copying a default English file first.
- B 摘要: Copies a file from the current object's path to a destination using NIO FileChannel.
- 静态失败原因: Static BERT likely correctly recognized the significant semantic difference, but BCB label is considered ground truth; the model did not adopt an overly broad interpretation.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have considered both as 'file copying' or 'file writing' operations at a very high level, or misclassified due to overgeneralization of file manipulation tasks.
- 共享行为: Both perform file I/O operations；Both write to files
- 行为差异: A reads/modifies text properties; B copies binary file content；A uses character streams and BufferedReader; B uses FileChannel；A handles locale-specific files and may copy a default file; B copies a single file；A can update or append new key-value pairs; B overwrites destination
- 修正建议: Re-evaluate BCB label; likely a false positive in the benchmark.；If BCB preference is to accept partial functionality, clarify annotation guidelines to avoid such mismatches.

### case_id=2310 FN benchmark_preference_bias

- 方法: `moveFile` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Copies a file by reading from the original and writing to a target, then deletes the original.
- B 摘要: Launches a NexOpen project configuration by validating project files, processing XML, setting properties, and optionally creating reverse engineering files.
- 静态失败原因: The model correctly detected low token overlap and structural dissimilarity, leading to a non-clone prediction. However, BCB's broad interpretation considers even tangential file I/O as sufficient similarity, causing a false negative from the benchmark's perspective.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have considered both as 'file manipulation' tasks, ignoring the vast difference in complexity and purpose, possibly due to a lenient Type-4 definition that includes any I/O-centric function.
- 共享行为: Both involve file I/O operations (reading and writing files).
- 行为差异: A is a simple file copy with no conditional logic; B is a complex, multi-step launch with many conditionals and API calls.；A deletes the original file; B does not delete any files.；A uses low-level Java streams; B uses Eclipse platform APIs and XML processing.；A has no external dependencies; B depends on Eclipse and Hibernate libraries.
- 修正建议: Re-evaluate BCB annotation for consistency; this pair likely should not be a clone.；If retaining as clone, incorporate task-level semantic embeddings to capture abstract file-handling patterns.

### case_id=2311 FP lexical_or_api_overlap

- 方法: `getDatasetsList` vs `get`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Synchronized method to fetch and cache a list of strings from a URL with parameter '?server=list', handling IO errors by logging and throwing RuntimeException.
- B 摘要: Static method to fetch game records from a URL with custom headers, filtering comment lines, and returning null on IO error.
- 静态失败原因: Static BERT/GraphCodeBERT likely overemphasized the lexical and API overlap (URL, BufferedReader, readLine, while loop) and ignored the different method names, comments, and overall purpose, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clone because the methods have different signatures, return types, caching behavior, error handling, and are used for completely different domains (dataset list vs game records). The only commonality is basic HTTP reading, which is too trivial for a clone.
- 共享行为: Both open a URL connection and read lines using BufferedReader.；Both parse text input line by line.；Both handle IOException (differently).
- 行为差异: A uses caching (datasetsList HashMap), B does not.；A appends query parameter '?server=list', B sets custom headers (latitude, longitude, count).；A returns List<String>, B returns GameRecord[].；A throws RuntimeException on error, B prints stack trace and returns null.
- 修正建议: Improve model to consider method names and comments as strong semantic signals.；Incorporate data flow analysis to distinguish caching and processing logic.；Use contrastive learning on examples with high lexical but low semantic overlap.

### case_id=2312 FN partial_functionality

- 方法: `main` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a URL, extracts all ZIP entries, and writes each entry to a file.
- B 摘要: Copies a single file from source to destination with existence and overwrite checks, and prints a progress bar.
- 静态失败原因: The model likely focused on token-level and structural differences, such as method name, control flow, and external library usage, missing the underlying I/O pattern. Low Jaccard similarity also contributed to a non-clone prediction.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider them clones due to the common core of reading bytes and writing to a file, which is a typical Type-4 partial similarity. However, the overall functionality differs significantly.
- 共享行为: Both read bytes from an input stream and write to a file output stream.；Both close streams in a finally block or implicitly.
- 行为差异: A downloads from a URL and extracts multiple ZIP entries; B copies a local single file.；B includes overwrite confirmation and progress reporting; A has no user interaction.；A uses hardcoded URL; B takes source and destination paths as parameters.；A uses ZipInputStream; B uses FileInputStream directly.
- 修正建议: Incorporate data flow analysis to capture input-output transformations.；Use clone detection methods that can handle partial overlap with different contexts.；Consider higher-level semantic embeddings that abstract common I/O patterns.

### case_id=2313 FP lexical_or_api_overlap

- 方法: `actionPerformed` vs `copyFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Handles action events for setting various preferences (Graphviz, ImageMagick, scale, country, date format, look-and-feel) and may prompt restart.
- B 摘要: Copies a source file to a destination file using FileChannel.
- 静态失败原因: Static BERT/GraphCodeBERT might have been misled by the presence of file-related keywords (File, filename, chooser) in Code A, along with some boilerplate code, and the high-level name 'actionPerformed' could be generic, but the overall token overlap is very low (Jaccard 0.0256). However, the model may have overgeneralized from training data where file handling appears in both.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled non-clone because the two functions have completely different semantics: one is a GUI action listener, the other is a file copy utility.
- 共享行为: Both use File objects；Both involve file operations (chooser vs copy)；Both use Java I/O classes
- 行为差异: Code A is a large GUI event handler with many settings; Code B is a simple file copy utility；Code A uses JFileChooser and file filtering; Code B uses FileInputStream/FileOutputStream；Code A sets preferences and UI state; Code B just copies bytes；Code A has conditional logic and user interaction; Code B is straightforward I/O
- 修正建议: Improve handling of long-range dependencies and global structure；Use dataflow analysis to distinguish between file selection and file copying；Incorporate method name semantics more strongly；Add negative sampling for such contrasting pairs

### case_id=2314 FN partial_functionality

- 方法: `readVersion` vs `seeURLConnection`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.75`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a version resource file from classpath, parses fields like Version, Revision, Date, and sets instance variables.
- B 摘要: Connects to a fixed HTTP URL, reads the entire response, and logs it.
- 静态失败原因: The static BERT model likely relied on token-level similarity and method names, which are quite different (low Jaccard similarity). It failed to capture the abstract structural pattern of URL reading and line processing that makes them clones under a broader interpretation.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider these as clones because they both implement a common pattern: reading from a URL source and processing lines in a loop. The structural similarity in control flow and I/O handling is sufficient for a broad Type-3/Type-4 clone annotation, ignoring differences in specific parsing logic.
- 共享行为: Open a URL connection；Create BufferedReader from input stream；Read lines in a while loop；Close the reader after use
- 行为差异: A reads from ClassLoader resource, B from HTTP URL；A parses specific key-value pairs, B appends all lines；A sets instance fields, B logs the output；A handles IOException locally, B throws Exception
- 修正建议: Incorporate dataflow or graph-based features to capture structural patterns like URL reading loops；Use contrastive learning to focus on functional similarity rather than lexical overlap；Augment training data with examples of partial functionality clones

### case_id=2315 FN lexical_or_api_overlap

- 方法: `doGet` vs `loadBinaryStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.3`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Handles HTTP GET request to retrieve and display a portal page, including authentication, property retrieval, caching, and logging.
- B 摘要: Loads a binary stream from an InputStream and writes it to the HTTP response with appropriate headers.
- 静态失败原因: The static model likely failed due to very low token overlap (Jaccard=0.05) and completely different method names and structures, leading it to judge them as non-clones. It did not capture the possible latent semantic similarity that BCB might have used (e.g., both are 'response-writing' methods).
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may consider them clones under a broad Type-4 category because both are HTTP response handlers that write to the output stream, sharing a common high-level purpose of servicing a request by writing to the response.
- 共享行为: Both operate on HttpServletRequest and HttpServletResponse objects.；Both write output to HttpServletResponse's OutputStream.
- 行为差异: A retrieves a page object and renders it as HTML; B simply copies bytes from an input stream to the response.；A involves complex logic for page lookup, user permissions, and caching; B is a straightforward streaming utility.；A may output HTML headers and scripts; B sets Content-Type, Content-Disposition, and Content-Length headers.
- 修正建议: Enrich the representation with cross-function context, such as class-level or project-level information, to recognize common roles.；Use dataflow or control-flow analysis to identify structural patterns (e.g., setting response headers and writing output).；Reconsider the BCB label: if the annotation is in error, the model may be correct.

### case_id=2316 FN lexical_or_api_overlap

- 方法: `login` vs `doVersionCheck`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Logs into LOLA by sending credentials via HTTP POST and extracting session ID.
- B 摘要: Checks for latest software version by fetching and parsing a version file from a URL.
- 静态失败原因: Static BERT/GraphCodeBERT models rely heavily on lexical and structural overlap; these functions have low token Jaccard (0.16), different method names, different APIs (URLConnection vs URL.openStream), and different exception handling, so the semantic similarity is not captured.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely considers both as network-based data retrieval functions that fetch and parse textual data from a server, thus labeling them as Type-4 clones despite different specific purposes.
- 共享行为: Both open a URL connection and read lines from an input stream.；Both parse a specific line from the response to extract information.；Both handle potential network errors through exception handling.
- 行为差异: Function A uses HTTP POST with encoded parameters, while B uses HTTP GET.；A processes only the first line for session ID; B reads multiple lines looking for specific prefixes.；A returns a string session ID; B calls another method and returns void.；A catches general Exception; B catches IOException specifically.
- 修正建议: Train on more Type-4 clone pairs with low lexical similarity.；Incorporate docstring/comment embeddings for semantic cues.；Use contrastive learning to focus on behavioral patterns.；Add data-flow analysis to capture common I/O patterns.

### case_id=2317 FN benchmark_preference_bias

- 方法: `extractZipFile` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.2`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Extracts a zip file entry by entry to the current directory, with optional progress updates.
- B 摘要: Builds a website for editing by transforming XML pages and writing output files, involving complex file I/O and XSL transformations.
- 静态失败原因: Static BERT did not fail; it correctly predicted non-clone. The BCB label appears overly generous, so the static model's prediction was accurate under reasonable semantic comparison.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might have labeled as clone due to both methods involving file reading/writing loops and being considered boilerplate I/O code, but the actual functionality is too distinct.
- 共享行为: Both methods perform file I/O operations, reading from input streams and writing to output streams.
- 行为差异: A extracts zip archives; B performs XSL transformations on XML and generates HTML.；A has a simple loop over zip entries; B has complex loops over pages with multiple file reads and transforms.；A uses ZipInputStream; B uses various streams and transformers.；A has minimal error handling; B has extensive error handling and debugging.
- 修正建议: Re-evaluate BCB annotation for this pair to ensure consistency.；Use more precise functional similarity metrics to avoid over-generalizing file I/O patterns.

### case_id=2318 FN lexical_or_api_overlap

- 方法: `main` vs `callApiPost`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Main method that constructs fixed POST parameters for RenRen API, sends an HTTP POST request, and prints the response.
- B 摘要: Generic method that sends an HTTP POST request with given parameters and headers, checks response code against expected, and returns the input stream.
- 静态失败原因: The static model likely failed due to low lexical overlap (Jaccard 0.162) and different method names and signatures. The model may have been misled by the many distinct API-specific classes (PostParameter, RenRenPostParameters) in A and the different control flow (loops, conditionals) in B, causing it to miss the semantic similarity.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may consider both as semantic clones (Type-4) because they both implement the core functionality of making an HTTP POST request with parameter passing and response handling. The high-level task is identical, and the structural skeleton (URL connection, POST, doOutput, connect, read response) is similar despite different parameterization and output.
- 共享行为: Both perform HTTP POST requests；Both set request method to POST and enable output；Both open a URL connection and connect；Both handle the response after connection
- 行为差异: A uses hardcoded parameters via PostParameter objects, B uses a parameter map；A prints response to console, B returns an InputStream；A does not handle timeouts, custom headers, or response code checking; B does；A is a static main method, B is an instance method with parameters
- 修正建议: Use dataflow analysis to capture common subsequence of API calls；Incorporate type-4 clone detection with attentive models that focus on semantic roles；Train on more diverse examples of functionally similar methods with different lexical content

### case_id=2319 FN partial_functionality

- 方法: `getResourceAsStream` vs `getResponse`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a resource from a URL with caching and returns an InputStream.
- B 摘要: Parses an HTTP GET request, retrieves a resource from the classpath, and returns the HTTP response as a byte array.
- 静态失败原因: Low lexical overlap and different syntactic structure; the static BERT model likely could not capture the broad functional similarity (if any) due to lack of shared API calls and distinct control flow.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely labeled this as a clone (Type-4) because both functions involve 'resource retrieval' and I/O operations, but the functionality is fundamentally different.
- 共享行为: Both use InputStream and OutputStream for I/O operations；Both involve HTTP-related processing (one client-side, one server-side)；Both handle exceptions and have fallback logic
- 行为差异: A returns an InputStream after caching; B returns a byte array representing an HTTP response；A accesses external URLs with caching; B accesses local classpath resources；A implements a client-side cache; B implements a server-side request handler
- 修正建议: Improve model's ability to recognize broader functional categories beyond exact API sequences；Incorporate control flow and data flow information to understand different implementations of similar high-level tasks

### case_id=2320 FP boilerplate_overlap

- 方法: `readData` vs `decodeFileToFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Initializes multiple hash sets and parses file input to build transliteration mappings for Tibetan script.
- B 摘要: Decodes a Base64-encoded file and writes the decoded content to an output file.
- 静态失败原因: Static models may have overgeneralized based on superficial similarities such as file streams, try-catch blocks, and loop structures, ignoring the distinct semantics of the two functions.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB annotators regard these as non-clones because their high-level purposes are completely different: one builds linguistic data structures, the other decodes files. No common functionality beyond generic file handling.
- 共享行为: Both perform file I/O operations (reading and writing).
- 行为差异: Function A is complex data initialization for Tibetan transliteration; Function B is simple Base64 decoding.；Function A modifies many global static collections; Function B uses local variables.；Function A uses StringTokenizer and custom parsing; Function B uses streams and buffers.；Function A throws multiple custom errors; Function B returns a boolean success flag.
- 修正建议: Include function name embeddings or documentation to capture purpose.；Incorporate data flow analysis to distinguish between initialization and I/O transformation.；Use contrastive learning on functions with similar boilerplate but different semantics.

### case_id=2321 FN benchmark_preference_bias

- 方法: `addIDs` vs `postRequest`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.85`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Parses HTML from a GET request to a metabolite database, extracts IDs and weights, and updates a PeakListRow object.
- B 摘要: Performs a generic HTTP POST request with form data and returns the raw response string.
- 静态失败原因: The static model correctly predicted non-clone due to low lexical overlap and different control flow; it did not recognize the broad network functionality similarity that BCB emphasized.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have considered both as 'HTTP client' functions, ignoring the specific purpose and parsing logic, thus labeling them as broad Type-4 clones.
- 共享行为: Both perform HTTP network requests；Both read response line by line；Both handle exceptions with try-catch
- 行为差异: A uses GET request; B uses POST request；A parses HTML response to extract structured data; B returns raw response string；A updates a PeakListRow object; B returns a String or null；A returns an integer score; B returns a String or null
- 修正建议: Consider using a more fine-grained functional similarity taxonomy that separates generic utilities from specific business logic.

### case_id=2322 FN benchmark_preference_bias

- 方法: `modifyApplicationMessage` vs `readFixString`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Modifies a properties file for a given locale by replacing or adding a key-value pair.
- B 摘要: Reads a fixed-length string from a limited input stream using IOUtils.copy.
- 静态失败原因: The model correctly predicted non-clone based on low token overlap and clear functional difference; the error type FN indicates BCB's label is likely a false positive.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled them as clones due to a broad interpretation of 'string manipulation' or 'resource handling' common in the same project, despite different specific functionalities.
- 行为差异: Handles file system and properties files vs. handles input streams.；Modifies existing content vs. reads and returns.；Uses character-based reading and writing vs. uses IOUtils.copy.；Handles exceptions with printStackTrace vs. wraps in runtime exception.
- 修正建议: Re-evaluate BCB annotation for possible overbroad cloning criteria.；Incorporate project-level context to understand if functions share a higher-level goal.

### case_id=2323 FP boilerplate_overlap

- 方法: `readTwitterFead` vs `doVersionCheck`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Downloads a JSON feed from a fixed Twitter URL and returns the entire content as a string.
- B 摘要: Checks for software version updates by reading a remote file and parsing version strings, then calls another method if updates are found.
- 静态失败原因: The model likely overemphasized the common I/O boilerplate (BufferedReader, InputStream, readLine) and control flow while failing to capture the distinct data processing logic and overall goals.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels this as non-clone because the high-level functionality (read Twitter feed vs. version check) and output (return string vs. void calling another method) are different, despite shared I/O boilerplate.
- 共享行为: Read data from a URL over HTTP；Use BufferedReader and InputStreamReader to read line by line；Handle IOException；Use a while loop with readLine()
- 行为差异: A uses HttpClient/HttpGet; B uses URL.openStream()；A checks HTTP status code 200; B does not；A appends all lines to StringBuilder; B parses lines for version info；A returns the entire content as String; B is void and calls another method
- 修正建议: Incorporate data-flow analysis to understand how read data is used；Use method names and comments to infer high-level purpose；Apply contrastive learning to separate similar structural patterns with different semantics；Include context from surrounding code (e.g., method calls, constant strings)

### case_id=2324 FN partial_functionality

- 方法: `getFile` vs `copyExternalResource`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies its endpoint, and saves to a temporary file, returning the file path.
- B 摘要: Copies a source file to a destination file using FileChannel transfer.
- 静态失败原因: Low token Jaccard (0.137) and different method signatures (return type, parameters) led the model to miss the shared I/O pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may view both as performing a file copy operation using the same low-level API, thus considering them functionally similar (Type-4 clone).
- 共享行为: Both use FileChannel.transferFrom to copy data from an input channel to an output channel；Both create output files if they do not already exist
- 行为差异: Function A downloads from a URL; function B copies from an existing file；Function A parses XML and modifies content; function B does no XML processing；Function A returns a String; function B is void；Function A handles multiple exception types; function B only handles IOException
- 修正建议: Incorporate API usage patterns or data flow to capture partial semantic overlap；Use graph-based representations to highlight shared file channel operations

### case_id=2325 FN partial_functionality

- 方法: `readGeoParserResult` vs `invoke`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Parses geo parser results from an XML web service with retries.
- B 摘要: Invokes a remote service method via HTTP with retries.
- 静态失败原因: Static BERT/GraphCodeBERT rely on token overlap and surface-level AST patterns, which are low (Jaccard=0.13) and miss the structural similarity in the retry-loop and HTTP request patterns across different libraries.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider these clones because both implement a retry-based web service client pattern with similar control flow and exception handling, despite different specific parsing tasks.
- 共享行为: Both perform HTTP requests with retries；Both read response line by line；Both parse response (XML vs JSON)；Both return a result after processing
- 行为差异: Different HTTP client APIs (URLConnection vs HttpClient)；Different data formats (XML vs JSON)；Different return types (collection of tuples vs generic object)；Different error handling (generic Exception vs specific ConnectTimeoutException)
- 修正建议: Use program dependence graphs or dataflow analysis to capture structural similarity despite different APIs；Incorporate control flow and exception handling patterns into the model

### case_id=2326 FP boilerplate_overlap

- 方法: `doVersionCheck` vs `getRequestContent`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Gets version information from a remote URL, parsing specific lines, and updates UI accordingly.
- B 摘要: Gets the first line of content from a URL as a string.
- 静态失败原因: Static BERT models may have been misled by the similar boilerplate code of opening a URL and reading with BufferedReader, ignoring the distinct processing loops, UI calls, and exception handling.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely considered the significant differences in functionality (version checking vs. single-line retrieval) and the presence of UI in A as enough to label non-clone.
- 共享行为: Both open a URL and read from its input stream using BufferedReader.
- 行为差异: A reads multiple lines to extract version info; B reads only the first line.；A includes UI operations (show/hide wait cursor, error dialog); B is purely data retrieval.；A uses generic URL and InputStream; B uses HttpURLConnection and returns first line.；A handles IOException with error display; B throws Exception.
- 修正建议: Better attention to the loop and conditional logic in A.；Incorporate structural matching that distinguishes high-level purpose (e.g., version check vs. generic fetch).

### case_id=2327 FN benchmark_preference_bias

- 方法: `main` vs `doUpload`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Downloads a KMZ file from a URL and extracts its contents to the local filesystem.
- B 摘要: Handles multipart file upload in a servlet, processing uploaded files and managing session and redirects.
- 静态失败原因: The static BERT model correctly identified the low token similarity and divergent semantics, resulting in a non-clone prediction.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have considered both as file I/O operations, but the functionality and structure are too distinct to be a clone.
- 共享行为: Both involve reading from input streams and writing to files
- 行为差异: Different input sources: URL vs HTTP request；Different output handling: direct file extraction vs upload processing and redirect；Different control flow: simple loop vs complex conditional logic with error handling and session management
- 修正建议: Re-evaluate BCB annotations for loose functional similarity criteria；Focus on functional equivalence and structural similarity rather than broad I/O operations

### case_id=2328 FN partial_functionality

- 方法: `testNetworkHTTP` vs `seeURLConnection`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Performs multiple HTTP GET requests to different URLs, reads and discards lines, catches IOException.
- B 摘要: Performs one HTTP GET request, reads response into StringBuffer, logs it, throws Exception.
- 静态失败原因: Static BERT relies on token-level similarity; low Jaccard (0.22) and different URLs, log statements, and method names cause misclassification.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB considers them clones because both implement the core pattern of HTTP GET, read, and log, despite differences in details and number of requests.
- 共享行为: Open HTTP connection；Read lines from input stream；Log output
- 行为差异: Number of requests (multiple vs one)；Error handling (catch vs throw)；Whether read data is used or discarded；Specific URL and logging target
- 修正建议: Use control-flow or data-flow analysis to capture common pattern；Leverage structural similarity of API calls；Apply cross-method pattern matching

### case_id=2329 FP lexical_or_api_overlap

- 方法: `actionPerformed` vs `testCopy_inputStreamToOutputStream`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Handles various GUI actions to set application preferences like file paths, image scaling, date format, and look and feel.
- B 摘要: Tests copying an input stream to an output stream using IOUtils.copy and verifies correctness via assertions.
- 静态失败原因: The model likely relied on superficial lexical overlaps (e.g., common tokens like 'return', 'null', 'if') or API names (e.g., 'InputStream', 'OutputStream', 'File') and failed to understand the high-level semantic difference. The long length of function A may also have caused the model to focus on local patterns rather than overall intent.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would not consider these clones because they are completely different in functionality: one is a complex GUI configuration handler, the other is a simple stream copy test.
- 行为差异: A is a GUI event handler; B is a unit test method.；A modifies persistent preferences and GUI components; B only performs I/O operations in memory.；A involves multiple conditional branches based on action command; B has a single linear flow.；A uses file choosers and Swing components; B uses byte arrays and streams.
- 修正建议: Enhance training with more diverse negative pairs to reduce false positives from common API tokens.；Incorporate structural information like control flow graphs or data flow analysis.；Use a more discriminative model that better captures global semantics, e.g., larger context windows or graph-based methods.

### case_id=2330 FP boilerplate_overlap

- 方法: `actionPerformed` vs `decodeFileToFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Handles UI actions for setting preferences like GraphViz path, ImageMagick path, and other settings, saving them and updating the UI.
- B 摘要: Decodes a Base64-encoded input file and writes the decoded data to an output file.
- 静态失败原因: The static model likely over-weighted the common boilerplate (file streams, try-catch-finally, and similar variable names like 'in' and 'out') and failed to capture the different overall semantics, perhaps due to long-range dependencies in the longer function A.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would likely label this as non-clone because the functions have completely different purposes (UI settings vs file decoding) and only share boilerplate patterns.
- 共享行为: Both involve file I/O (using streams) and try-catch-finally blocks.
- 行为差异: A is a UI event handler for a preferences dialog; B is a static utility for file decoding.；A reads a file path from a chooser and saves it as a preference; B reads and writes actual file content.；A uses multiple conditional branches for different actions; B has a single straightforward flow.；A updates UI components and shows dialogs; B has no UI interaction.
- 修正建议: Increase sensitivity to functional purpose by incorporating data flow analysis.；Use more robust representation learning that focuses on core logic rather than I/O boilerplate.；Consider hierarchical or graph-based models that capture high-level structure.

### case_id=2331 FN partial_functionality

- 方法: `loadDefaultSettings` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Loads default configuration settings by copying a resource from classpath to a file using IOUtils.copy.
- B 摘要: Launches a Maven-based project configuration, which includes copying a default reverse engineering file from a bundle to the project if missing, among many other tasks.
- 静态失败原因: Static BERT models rely on token and structural similarity; the low Jaccard similarity (0.0737) and different method names, parameters, and overall control flow likely caused the model to predict non-clone. The model may not capture the deep semantic similarity of common sub-operations like copying resources.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB's guidelines often consider partial functional similarity as Type-4 clones, especially when a common utility pattern (like copying default resources with IOUtils.copy) appears in both functions, even if the overall functionality differs. The shared I/O pattern and exception handling may have led BCB annotators to deem them clones.
- 共享行为: Both functions copy a default resource from an input stream to an output stream using IOUtils.copy.；Both functions handle exceptions and close streams in a finally block.；Both functions use IOUtils.closeQuietly to close streams.
- 行为差异: Function A is a simple, static utility that only copies one file; Function B is a complex, non-static launch procedure with many domain-specific operations (XML parsing, property setting, job scheduling).；Function A targets a config file; Function B targets multiple project files (pom.xml, business/pom.xml) and involves conditional logic based on project properties.；Function A is private and static; Function B is public and part of a launch delegate interface.
- 修正建议: Incorporate subgraph matching or program slicing to detect shared behavioral patterns.；Use a broader context or code summarization to identify common utility operations.；Consider training on more partial-clone examples with similar I/O patterns.

### case_id=2332 FN partial_functionality

- 方法: `modifyApplicationMessage` vs `testCopy_inputStreamToOutputStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Modifies an application message in a locale-specific properties file, copying from an English default if needed.
- B 摘要: Tests the IOUtils.copy method by copying an input stream to an output stream and verifying correctness.
- 静态失败原因: The static model likely focused on method signatures and overall structure, which are very different, and missed the low-level stream copy pattern due to low token overlap and the presence of many unrelated operations in A.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider these clones because both functions implement the same core functionality of copying bytes from an input stream to an output stream, which is a Type-3 or Type-4 clone despite different overall contexts.
- 共享行为: Both contain a stream copy operation: reading bytes from an input source and writing to an output sink.
- 行为差异: A is a full i18n method with file existence checks, properties parsing, and message replacement; B is a unit test with only stream copy and assertions.；A uses FileReader/FileWriter for file I/O; B uses ByteArrayInputStream/ByteArrayOutputStream with mocking wrappers.；A includes error handling and logging; B uses JUnit assertions.；A modifies a specific property key-value; B verifies byte-by-byte equality of copied data.
- 修正建议: Train the model to recognize partial functional similarity by using data-flow graphs or execution traces.；Add more positive examples where a sub-computation is shared between otherwise different methods.；Incorporate bytecode or AST-based analysis to detect common I/O patterns.

### case_id=2333 FP partial_functionality

- 方法: `readTwitterFead` vs `downloadFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads Twitter timeline JSON from a fixed URL using Apache HttpClient and returns it as a string.
- B 摘要: Downloads a file from a given URL to a given destination path using URLConnection, with progress tracking, and returns a boolean success indicator.
- 静态失败原因: Static BERT/GraphCodeBERT may have over-relied on the shared pattern of opening an HTTP connection, reading a stream, and using try-catch blocks, ignoring the significant differences in method signatures, return types, and overall functionality.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely considers these non-clones because they serve fundamentally different purposes: one is a specific Twitter feed reader, the other a generic file download utility. The dissimilarities in input/output, error handling, and progress reporting outweigh the superficial similarity in downloading data.
- 共享行为: Both perform an HTTP GET request to a URL；Both read the response stream
- 行为差异: Function A uses Apache HttpClient, B uses URLConnection；Function A has a hardcoded URL, B takes URL as parameter；Function A returns content as string, B saves to file and returns boolean；Function B includes progress reporting, A does not
- 修正建议: Incorporate structural features like method signature (return type, parameters)；Use finer-grained semantic matching that distinguishes between data consumption patterns (return vs. file write)；Enhance training data with more negative examples that share API calls but differ in purpose

### case_id=2334 FP partial_functionality

- 方法: `sendPost` vs `handledRun`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends an HTTP POST request with parameters and returns the response as a string.
- B 摘要: Handles downloading and updating game data from a remote XML file, checking version and writing to disk.
- 静态失败原因: Static BERT/GraphCodeBERT may have been misled by overlapping API usage (URL, BufferedReader) and try-catch structures, missing the overall semantic difference in purpose and data flow.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB would not consider these clones because they serve completely different purposes despite superficial I/O similarities.
- 共享行为: Both open a URL connection；Both read from an input stream using BufferedReader；Both have try-catch for exception handling
- 行为差异: sendPost is an HTTP POST utility; handledRun downloads and updates a game data file；sendPost outputs to the connection and reads response; handledRun reads from URL and writes to a local file；handledRun includes version checking and file deletion; sendPost does not；handledRun has a finally block to load game data; sendPost does not
- 修正建议: Improve models to consider higher-level purpose beyond local API patterns；Incorporate data flow and call context to distinguish utility functions from specific tasks

### case_id=2335 FN partial_functionality

- 方法: `getJSONData` vs `runScript`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches JSON data from a URL using HttpClient and returns a JSONObject.
- B 摘要: Fetches data from a URL using URL.openStream and returns the raw string.
- 静态失败原因: Low token overlap and different API usage caused the model to miss the semantic similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels functions with similar core functionality (fetching from URL) as clones despite implementation differences.
- 共享行为: Both retrieve data from a URL and return the content
- 行为差异: One returns a JSONObject, the other returns a raw string；One uses Apache HttpClient, the other uses URL.openStream；Error handling differs: prints stack trace vs returns 'error!'
- 修正建议: Add structural hints like URL/networking patterns；Incorporate data flow or function call graph to capture I/O operations

### case_id=2336 FP lexical_or_api_overlap

- 方法: `getUser` vs `getPagina`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Retrieves a user by login from a database or local config file, saving to DB if found in file.
- B 摘要: Fetches and returns the entire content of a web page as a string, including error messages.
- 静态失败原因: Static BERT/GraphCodeBERT likely overgeneralized from shared API usage (URL, BufferedReader, InputStreamReader) and similar exception handling structure, missing the semantic disparity in the loop body and return types.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled non-clone because the functions perform distinct tasks (user retrieval vs page fetching) and have different core logic despite similar I/O patterns.
- 共享行为: Both use URL and BufferedReader with InputStreamReader to read lines from a resource；Both have try-catch blocks handling exceptions；Both contain a while loop reading lines until null
- 行为差异: Different return types: User vs String；Different resource sources: classpath file vs arbitrary URL；Different line processing: tokenization with StringTokenizer vs string concatenation；Different error handling: printStackTrace vs returning error string
- 修正建议: Incorporate dataflow analysis to distinguish variable transformations；Use type information to differentiate return types and method signatures；Train on more diverse examples where API overlap exists but functionality differs

### case_id=2337 FN partial_functionality

- 方法: `main` vs `doVersionCheck`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Constructs and sends an HTTP POST request with multiple parameters to RenRen API and prints the response.
- B 摘要: Reads a version check file from a URL, parses version and build info, and shows appropriate dialogs.
- 静态失败原因: Static BERT models often rely on token overlap and method names; low token Jaccard (0.139) and different method names led to predicting non-clone, missing the structural similarity of URL reading patterns.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider them clones due to similar overall structure of fetching remote data over HTTP and reading response lines, despite different specific tasks.
- 共享行为: Open a URL and read lines from the input stream using BufferedReader；Handle IOException
- 行为差异: A uses POST with parameters; B uses GET；A prints response lines; B parses specific version and build fields and displays dialogs；A is a main entry point; B is a utility method called with a view parameter
- 修正建议: Enhance the model to recognize abstract patterns like 'open URL, read lines' even with low lexical overlap；Incorporate structural or flow-based features to capture shared subroutines

### case_id=2338 FN partial_functionality

- 方法: `testNetworkHTTP` vs `readGeoParserResult`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: A test method that sends multiple HTTP GET requests to predefined URLs for network testing, discarding all response content.
- B 摘要: Reads a record string, constructs an XML request, sends it to a geo-parser service, parses the XML response to extract place names and gazetteer IDs, and returns a collection of tuples with retry logic.
- 静态失败原因: The static BERT/GraphCodeBERT model likely recognized the low token overlap and different method names, classifying them as non-clones because lexical and structural similarity is low, missing the superficial I/O pattern similarity that BCB considered.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled these as clones based on the broad category of 'both perform HTTP I/O and read lines', considering them as Type-3 clones with similar structure and API usage, despite different purposes.
- 共享行为: Both use URL and BufferedReader to perform network I/O and read lines from a stream.
- 行为差异: Function A is a test method that sends multiple HTTP requests to specific URLs and discards the response; Function B constructs an XML query, processes the response, and returns parsed results.；Function A has no retry logic; Function B retries up to 3 times on failure.；Function A does not return a value; Function B returns a Collection of Tuples.；Function A's requests are to static URLs; Function B's URL is dynamically constructed from parameters.
- 修正建议: Improve detection of functional similarity beyond token overlap by capturing intent and data flow.；Use more fine-grained analysis of API call patterns and their purposes.；Consider incorporating domain knowledge about common test patterns.

### case_id=2339 FN benchmark_preference_bias

- 方法: `modifyApplicationMessage` vs `copy`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Modifies a properties file for a given locale by updating or appending a message value, creating the locale file from an English template if it does not exist.
- B 摘要: Copies a file from source to destination using NIO FileChannel transfer.
- 静态失败原因: Static BERT/GraphCodeBERT correctly predicted non-clone due to low token overlap (0.1) and distinct code structures; the model did not fail, but BCB annotation is likely incorrect.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled these as clones based on broad file I/O functionality or a false annotation; the two methods share no meaningful functional similarity beyond file operations.
- 共享行为: Both perform file I/O operations (reading and writing files).；Both are public void methods.；Both handle exceptions (A catches Exception, B throws IOException).
- 行为差异: A reads, modifies, and writes a properties file with locale-specific logic; B copies entire file content directly.；A creates a file if it does not exist; B expects both source and destination to exist.；A uses BufferedReader, FileReader/Writer; B uses FileChannel and streams.
- 修正建议: Review BCB annotation for this pair; it may be mislabeled.；Improve benchmark guidelines to avoid over-broad Type-4 classification purely based on file I/O.；Use more precise semantic matching beyond token overlap.

### case_id=2340 FP lexical_or_api_overlap

- 方法: `main` vs `copyFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Generates adapter classes from a Prolog file, involving file reading, parsing, and writing a JAR with generated code.
- B 摘要: Copies a file from source to destination using FileChannel for efficient transfer.
- 静态失败原因: The model likely overemphasized superficial lexical similarities (e.g., 'File', 'IOException', 'close') and general boilerplate pattern, overlooking the vast difference in program logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels as non-clone because the two functions have completely different purposes and no shared algorithmic core beyond generic file I/O.
- 共享行为: Both involve file I/O operations；Both use exception handling
- 行为差异: Function A performs complex code generation, while B is a simple file copy；A processes Prolog files and produces JAR artifacts; B transfers bytes between files；A uses many external libraries and APIs; B uses only standard Java NIO；A has command-line argument parsing; B has no such logic
- 修正建议: Enhance model with structure-aware representations like data flow or control flow graphs；Use contrastive learning to separate dissimilar functions with overlapping keywords；Increase weight on functional semantics over API usage

### case_id=2341 FN partial_functionality

- 方法: `getResourceAsStream` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Retrieves a resource from a URL with caching to a local file, returning an InputStream.
- B 摘要: Copies a file from source to destination using FileChannel.
- 静态失败原因: Static BERT models rely heavily on token overlap and local syntactic patterns; the low token Jaccard (0.107) and different API usage (URLConnection vs FileChannel) led to no similarity detection. The model failed to capture the high-level read-write semantic similarity because it lacks global structural or dataflow awareness.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label them as clones because both functions perform a similar read-write pattern (reading from a source and writing to a file), share structural elements like try-catch and resource closing, and can be seen as variants of data transfer operations, which fits BCB's broad Type-3/Type-4 criteria.
- 共享行为: Both read from a source and write to a destination file；Both handle IOException with try-catch；Both close resources (streams/channels)；Both involve file output
- 行为差异: A uses URL/HTTP connection; B uses direct file input；A implements caching logic; B does not；A returns InputStream; B returns boolean；A uses BufferedInputStream/OutputStream; B uses FileChannel
- 修正建议: Incorporate AST or control-flow graph features to capture structural patterns；Use dataflow analysis to identify input-output relations；Train on partial clone pairs explicitly；Add method-level context (e.g., comments, parameters) to infer intent

### case_id=2342 FP long_range_semantics

- 方法: `hyperlinkUpdate` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `static_summary_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Opens a URL from a hyperlink event, reads its content, and displays it in a dialog.
- B 摘要: Handles various action commands to configure settings, select files, and update preferences.
- 静态失败原因: The model likely focused on surface-level similarities (both are event handlers with UI interactions and exception handling) and missed the deep semantic differences in control flow and purpose.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB considers these non-clones because they have completely different functionality and no shared task logic; they are not even partial clones.
- 共享行为: Both are event handlers (HyperlinkEvent and ActionEvent).；Both use try-catch for exception handling.；Both involve UI components (JEditorPane, JFileChooser).
- 行为差异: Code A retrieves URL content and displays it; Code B shows file choosers and updates preferences.；Code A has no branching based on command strings; Code B has multiple command checks.；Code A deals with a single event type; Code B handles a complex settings dialog with many options.；The overall functionality and purpose are entirely different.
- 修正建议: Train models to capture high-level task intent rather than just local patterns.；Use graph-based or dataflow representations to distinguish different program logic.；Incorporate longer context or attention mechanisms to handle long methods.

### case_id=2343 FN partial_functionality

- 方法: `copyFile` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: A utility method that copies a file from one location to another using FileChannel transferTo.
- B 摘要: A complex launch method that validates a project configuration, processes XML files, and copies a resource file to the project with modifications.
- 静态失败原因: Static BERT models rely on lexical and structural overlap; the low Jaccard similarity (0.033) and different method names and contexts suggest no clone, missing the deeper semantic of file copying within the larger function.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled these as clones because launch contains a file copying subfunction that is functionally similar to the entire copyFile method, reflecting a broad Type-4 partial functionality similarity.
- 共享行为: Both involve copying file content from a source to a destination.
- 行为差异: copyFile is a simple, focused file copy; launch is a multi-step launch configuration process.；copyFile uses FileChannel; launch uses IOUtils.copy and string substitution.；copyFile does not modify content; launch modifies the copied content.；launch includes many unrelated operations such as XML handling and project setup.
- 修正建议: Incorporate call graph analysis to detect subfunction clones.；Use hierarchical embeddings that capture part-whole relationships.；Consider data-flow analysis to identify common I/O operations.

### case_id=2344 FP partial_functionality

- 方法: `main` vs `extractFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Parses command-line arguments, reads a Prolog file, generates adapter classes and writes them to a JAR file.
- B 摘要: Reads an input file (from a ZipEntry) and copies its contents to an output file.
- 静态失败原因: The static model likely overfitted to common API calls (File, InputStream, OutputStream) and the general 'read-write' pattern, ignoring the drastic difference in overall program structure, length, and purpose.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely labeled as non-clone because the two functions have vastly different purposes and complexity, despite both using file I/O. BCB's partial functionality criterion still requires a significant overlap in underlying logic, which is absent here.
- 共享行为: Both involve reading from a file and writing to another file using Java I/O streams.
- 行为差异: Function A performs complex parsing of Prolog source, generates Java classes, and writes multiple resources to a JAR file.；Function B is a simple binary copy from one file to another with a fixed 512-byte buffer.；Function A includes extensive error handling and debug output; Function B throws exceptions directly.；Function A uses reflection, class loaders, and bytecode generation; Function B does not.
- 修正建议: Increase training data diversity with single-file-IO tasks to reduce false positives.；Incorporate structural or semantic similarity measures (e.g., control-flow graphs) to capture the significant complexity gap.；Use contrastive learning to distinguish trivial I/O from sophisticated file-based processing.

### case_id=2345 FP long_range_semantics

- 方法: `readData` vs `testReadPerMemberSixSmall`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `static_summary_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Parses multiple comma-separated static strings into various sets and a hashmap, processing Tibetan transliteration data.
- B 摘要: Tests reading a GZIP stream with multiple members, verifying byte counts for each member and end-of-stream.
- 静态失败原因: Static BERT models may have been misled by the presence of common API elements (e.g., IOException, while loops) or the overall 'data reading' theme, failing to capture the fundamentally different semantics and data flow due to limited context and lack of structural understanding.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB labels 0 because the functions have no shared functionality, even under broad Type-4 partial similarity criteria.
- 行为差异: Function A parses string tokens into collections; function B reads binary data from a decompression stream.；Function A involves static fields and complex data structures; function B is a unit test with assertions.；Function A has extensive error handling for file parsing; function B has no error handling beyond declared exception.；Function A is very long (hundreds of lines); function B is short (~20 lines).
- 修正建议: Improve context handling to capture long-range dependencies in very long functions.；Incorporate control flow and data flow graphs to distinguish data processing from stream I/O.；Enhance tokenization to reduce lexical overlap from generic API tokens.

### case_id=2346 FN partial_functionality

- 方法: `addIDs` vs `importRoles`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches metabolite data from a web service by parsing HTML, extracts various IDs and properties, and stores them in a row object, returning a score.
- B 摘要: Imports role names from an XML-like URL by parsing RoleName tags, creating RoleName objects, and returning a list.
- 静态失败原因: Static BERT/GraphCodeBERT likely focused on token-level similarity (low Jaccard) and did not capture the shared structural pattern of URL-reading and tag-based parsing due to different domain-specific tokens and method names.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label as clone because both functions follow the same high-level pattern of fetching data from a URL, parsing line-by-line for specific tags, and accumulating results, despite different output types and parsing details.
- 共享行为: Both open a URL and read lines using BufferedReader.；Both use a while loop to read lines and parse specific tags.；Both collect data based on tag patterns and store results.；Both handle IO exceptions similarly.
- 行为差异: Different input parameters (PeakListRow+name vs URL string).；Different output type (int score vs ArrayList<RoleName>).；Different tag parsing targets (metabolite IDs vs RoleName).；Different data storage (row properties vs list of RoleName).
- 修正建议: Use dataflow analysis to track the common pattern of URL open, read, parse, collect.；Incorporate structural similarity that captures repeated code skeleton despite different domain vocabulary.

### case_id=2347 FP lexical_or_api_overlap

- 方法: `setMembers` vs `getFrameworkFactory`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads an HTML page from a Trac URL, parses component and priority select elements, and populates static arrays.
- B 摘要: Reads a service configuration file from classpath, finds a non-comment line, loads the class, and returns a new instance.
- 静态失败原因: The model overfitted on the lexical and structural pattern of opening a URL, creating BufferedReader, and looping readLine(), ignoring the distinct post-processing and overall purpose.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically requires at least partial functional similarity beyond boilerplate; here the core intent (UI vs. OSGi service loading) is entirely different, so not a clone even under broad Type-4.
- 共享行为: Both open a URL and read lines using BufferedReader.；Both iterate line-by-line with readLine() in a while loop.
- 行为差异: Function A sets static fields (void); Function B returns a FrameworkFactory object.；Function A parses HTML with regex for specific select elements; Function B checks for comment lines and loads classes.；Function A uses getTracUrl() to construct URL; Function B uses classloader resource.；Function A does not close the reader; Function B closes in a finally block.
- 修正建议: Include more negative examples with shared IO boilerplate but disparate logic.；Add dataflow or type information to distinguish output behavior (void vs. return type).；Use AST-based models that better capture structural differences beyond surface patterns.

### case_id=2348 FN boilerplate_overlap

- 方法: `addIDs` vs `startScript`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Adds metabolite IDs and scores to a peak list row by parsing HTML from a web service.
- B 摘要: Loads a script from a URL and appends it to a dialog buffer.
- 静态失败原因: The static BERT model likely focused on the distinct method names, return types, and divergent parsing logic, leading to a low similarity score (token Jaccard 0.15) and missing the shallow I/O pattern overlap that BCB considered.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may have labeled this as a clone due to the shared pattern of reading from a URL line by line with BufferedReader and catching IOException, considering it a Type-3 clone with structural similarity despite different functionality.
- 共享行为: Both open a URL and create a BufferedReader to read it line by line.；Both handle IOException in a catch block.
- 行为差异: Function A parses HTML to extract metabolite IDs, scores, and sets multiple row properties; Function B simply concatenates lines as plain text.；Function A returns an integer score; Function B returns void.；Function A has complex conditional logic based on content; Function B has a simple read-and-append loop.；Function A uses external constants like GCGCColumnName; Function B uses dialog.script.
- 修正建议: Enhance model sensitivity to common API usage patterns (e.g., URL reading) even when high-level semantics differ.；Incorporate dataflow analysis to highlight shared I/O operations.；Use fine-grained token matching with weighted API calls.

### case_id=2349 FN partial_functionality

- 方法: `runScript` vs `doVersionCheck`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a script file from a URL and returns its content as a string.
- B 摘要: Checks for a new version by reading a version file from a URL and displaying messages.
- 静态失败原因: Static BERT/GraphCodeBERT models rely heavily on token overlap and local syntactic patterns, which are low (Jaccard=0.214) due to different method names, loop structures, and API calls. They miss the shared semantic pattern of URL reading.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as Type-4 clones because they share the core functionality of reading from a URL and processing input, which is a common pattern in jEdit plugins.
- 共享行为: Both open a URL and read input from it；Both handle IOException (or generic Exception)
- 行为差异: A reads byte by byte into a string; B reads line by line parsing version/build；A returns the file content; B updates UI with version check results；A's URL is parameterized; B's URL is from a property；A handles generic Exception; B handles IOException specifically
- 修正建议: Incorporate data-flow or control-flow features to capture shared API usage sequences (URL, InputStream).；Train on more Type-4 examples that have low lexical overlap but similar underlying functionality.；Use contrastive learning to pull together code snippets that share high-level operations like 'download and process'.

### case_id=2350 FN partial_functionality

- 方法: `main` vs `decodeFileToFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a ZIP from a URL (HTTP or file) and extracts its entries to files.
- B 摘要: Decodes a base64-encoded file and writes the decoded content to another file.
- 静态失败原因: The model focused on lexical tokens and low overlap (Jaccard 0.226), missing the structural similarity of the buffered read-write loop and different domain operations.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB considers them clones because both perform a common I/O pattern (read from stream, write to file) and the high-level operation of transforming an input stream to an output file, aligning with Type-3/4 clone criteria.
- 共享行为: Both read from an input source and write bytes to an output file using a buffer.
- 行为差异: A handles ZIP extraction from a URL, B handles base64 decoding of a local file.；A prints entry names, B returns a success flag.；A throws Exception, B catches IOException.；A does no base64 processing, B does not handle compression.
- 修正建议: Enhance model to capture structural patterns of I/O, use graph-based representations for data flow, or augment with type information.

### case_id=2351 FN partial_functionality

- 方法: `copyResource` vs `logging`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource from a URL or file to a destination file using stream I/O.
- B 摘要: Logs inbound message content by copying the input stream to a cached output stream and extracting encoding/headers.
- 静态失败原因: Static BERT methods rely on token and structural similarity; here token Jaccard is very low (0.099), method names and contexts differ, and different API calls (FileOutputStream vs CachedOutputStream) lead to a non-clone prediction. The abstract I/O copy pattern is not captured.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider this a clone because the core pattern of reading from an input stream and writing to an output stream with error handling is similar, and the additional logging in function_b could be viewed as peripheral. This is a borderline Type-4 clone based on partial functional similarity.
- 共享行为: Both read from an InputStream and write to an OutputStream (or similar)；Both close streams after use；Both handle exceptions
- 行为差异: Function_a writes to a file; Function_b writes to a logging buffer；Function_b extracts metadata (encoding, headers) and logs additional information；Function_a uses a simple loop; Function_b uses IOUtils.copy；Error handling differs: Exception vs Fault
- 修正建议: Incorporate program analysis to detect I/O copy patterns regardless of specific output type；Use data flow analysis to identify stream copy operations；Better handle type-4 clones with abstract semantic matching

### case_id=2352 FP lexical_or_api_overlap

- 方法: `actionPerformed` vs `createNew`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Handles GUI action events to set various preferences (e.g., Graphviz, ImageMagick paths) and update UI components.
- B 摘要: Creates a new file resource by copying an input stream to a file, subject to ownership check.
- 静态失败原因: The static model likely over-relied on superficial lexical similarities such as common tokens (File, name, out, try) and similar control structures (try-finally, conditionals), ignoring the vast semantic disparity.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would annotate as non-clone because the functions have no shared functionality: one is a GUI configuration handler, the other is a file resource creator.
- 行为差异: Function A is a GUI event handler that processes different commands and updates UI; Function B performs file I/O to create a resource.；Function A interacts with UI components and preference storage; Function B writes data to a file and resolves a resource.；Function A has complex conditional branching based on action commands; Function B has simple conditional on ownership.；No overlap in functionality or purpose.
- 修正建议: Improve training with more diverse negative examples that have low semantic similarity but moderate token overlap.；Incorporate a deeper understanding of method context (e.g., class name, field accesses) to distinguish GUI handling from file operations.；Use dataflow or program dependence graphs to capture actual data and control dependencies.

### case_id=2353 FP lexical_or_api_overlap

- 方法: `getTicketsForQueue` vs `sendRequestObjectResponse`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Sends an HTTP GET request to search for tickets by queue, parses response lines for ticket IDs, retrieves each ticket, returns list of RTTicket objects.
- B 摘要: Sends an HTTP request to a servlet with compressed XML, saves the response to a file based on content type, displays the file, returns the file path.
- 静态失败原因: Static BERT may have focused on overlapping tokens/structures like 'Http', 'get', 'URL', 'Exception', and similar boilerplate error handling, missing the distinct semantic purposes and the way data is processed.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled as non-clone because the core functionality (querying tickets vs. submitting compressed request to a servlet) is completely different; they share only superficial common patterns like HTTP and exception handling.
- 共享行为: Both make an HTTP request to a server；Both handle HTTP responses and exceptions
- 行为差异: Function A performs GET request with query parameters; Function B sends compressed XML output；Function A reads text lines and extracts ticket IDs; Function B saves response to file and returns file path；Function A returns a list of domain objects; Function B returns a file name string；Function A uses Apache HttpClient; Function B uses java.net.URLConnection
- 修正建议: Improve model's ability to differentiate between HTTP GET and POST/send patterns；Use more context-aware embeddings that can capture the overall data flow and output type；Incorporate type information or return type matching

### case_id=2354 FN partial_functionality

- 方法: `unJarStart` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Extracts all jar entries with a given prefix from a JAR file and copies them to a target directory.
- B 摘要: Launches a NexOpen configuration by processing POM files, setting Hibernate properties, and conditionally copying a reverse engineering file from a plugin bundle to the project.
- 静态失败原因: Static BERT models rely on token overlap and local context; the low Jaccard similarity (0.048) and highly different surrounding code cause the model to miss the shared I/O pattern, which is only a small part of each function.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider this a Type-4 clone because both functions perform a file copy operation using the same API (IOUtils.copy) and handle exceptions, indicating a shared subfunctionality despite different contexts.
- 共享行为: Both use IOUtils.copy to write an input stream to a file on disk；Both handle exceptions (printStackTrace vs logging)
- 行为差异: Function A iterates over multiple jar entries; Function B copies only a single specific file；A's input is a JAR file; B's input is a bundle resource；A's output path is derived from jar path; B's output is to a specific project file；A has no configuration logic; B involves extensive project setup and attribute handling
- 修正建议: Enhance models with data flow analysis to capture shared API call patterns；Use graph-based representations that abstract control and data flow to identify subgraph similarities；Augment training data with Type-4 clones sharing partial functionality

### case_id=2355 FN partial_functionality

- 方法: `getFile` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.65`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies the soap endpoint, and saves it to a temp directory.
- B 摘要: Copies a file from a source to a destination using a byte buffer.
- 静态失败原因: Low token similarity (0.12) and different method names ('getFile' vs 'copyFile') led the model to focus on surface-level features, ignoring the underlying common I/O pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as file copy operations (Type-4 functional similarity), as they both transfer data from a source to a destination, with similar error handling patterns.
- 共享行为: Both read from an input stream and write to an output stream；Both handle IOException and use try-catch blocks；Both involve file I/O operations
- 行为差异: A downloads from a URL, B copies from a local file；A parses and modifies XML, B does not；A uses temp files and renaming, B does not；A returns a file path, B is void
- 修正建议: Enhance model with data flow analysis to detect input-to-output data transfer patterns；Include structural similarity measures for exception handling blocks

### case_id=2356 FP lexical_or_api_overlap

- 方法: `testSimpleQuery` vs `readData`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: A test method that writes XML content to JCR sources, executes a query, and verifies the result.
- B 摘要: A private method that reads a configuration file and populates multiple sets and maps with parsed tokens.
- 静态失败原因: Static BERT models may have been misled by overlapping boilerplate code (e.g., 'throws Exception', while-loops, HashSet usage) and ignored the distinct domain-specific operations.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would label this non-clone because the methods have entirely different purposes: one is a unit test for a content repository, the other is a data initialization routine for a linguistic tool.
- 共享行为: Both methods involve reading data from some source and storing it in collections (though source types differ).
- 行为差异: Method A is a test with assertions and query logic; Method B is a parser for a config file.；Method A deals with JCR content repositories and XML; Method B processes Tibetan-related token strings.；Method A writes to sources before reading; Method B only reads and populates static data structures.
- 修正建议: Enhance model to focus on semantic purpose rather than surface-level API or control flow patterns.；Incorporate data flow or call graph analysis to distinguish test logic from configuration parsing.

### case_id=2357 FP boilerplate_overlap

- 方法: `run` vs `doVersionCheck`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Loads and processes vector tile data from a URL, extracting geometries and adding them to a data loader.
- B 摘要: Checks for software version updates by reading a remote file and extracting build numbers.
- 静态失败原因: The static model overemphasized the shared lexical patterns (URL opening, BufferedReader, readLine) and ignored the distinct post-processing logic, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clone because the functions have entirely different purposes and the similarity is limited to boilerplate I/O code, which does not indicate functional equivalence.
- 共享行为: Open URL and input stream；Read lines using BufferedReader；Handle IOException
- 行为差异: A processes tile geometries; B parses version strings；A supports file and http protocols; B only http；A has synchronization to deduplicate requests; B does not；A builds a GeometryCollection; B calls another version check method
- 修正建议: Incorporate control-flow and data-flow analysis to capture differences in output transformation.；Add attention to method name and class context to distinguish unrelated tasks.；Use graph-based models that follow data dependencies beyond initial I/O.

### case_id=2358 FN benchmark_preference_bias

- 方法: `getFile` vs `testCopyUnknownSize`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Downloads a WSDL file from a URL, modifies its endpoint attribute, and saves it locally; returns the file path.
- B 摘要: Unit test that verifies ExtraIOUtils.copy correctly copies data from an input stream to an output stream when the size is unknown.
- 静态失败原因: In this case, the static BERT/GraphCodeBERT model did not fail; it correctly predicted non-clone (0). The mismatch is due to a likely erroneous BCB positive label (1), possibly from benchmark preference bias.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might have considered both functions as involving 'copy' operations on streams, but this is a very loose interpretation. The primary functionalities are completely different: one is a WSDL downloader/configurator, the other is a test for an IO utility. The partial overlap in stream copying is superficial.
- 共享行为: Both involve reading from an input stream and writing to an output stream (function A copies from URL stream to file; function B tests copying from ByteArrayInputStream to ByteArrayOutputStream).
- 行为差异: Function A performs network download, XML parsing, and file management; function B is a unit test with assertions.；Function A modifies XML attributes; function B does not.；Function A uses NIO channels; function B uses a utility method.；Function A has extensive error handling and logging; function B does not.
- 修正建议: Re-evaluate BCB label for this pair; likely should be 0.；Consider using task-specific or semantic similarity metrics to avoid superficial API overlap.

### case_id=2359 FN benchmark_preference_bias

- 方法: `fileDownload` vs `parse`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Downloads a file from a URL and saves it to a local directory.
- B 摘要: Parses a data file or URL into a DataSet object with headers and types.
- 静态失败原因: The static model correctly predicted non-clone because token overlap is very low; the BCB label is likely an annotation error.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have incorrectly labeled these as clones due to both involving URL/file I/O, overlooking the vastly different processing logic.
- 共享行为: Open a URL or file for reading；Use BufferedReader and InputStream；Catch IOExceptions
- 行为差异: A writes raw bytes to an output file; B tokenizes and parses structured data；A ignores file format; B respects column headers and data types；A is void; B returns a DataSet；B has complex parsing with scientific notation handling; A does simple read-write
- 修正建议: Review BCB annotation guidelines for clarity on partial functionality；Re-annotate this pair or remove from benchmark

### case_id=2360 FN partial_functionality

- 方法: `runScript` vs `run`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a script from a URL constructed from a parameter and returns its content as a string, with error handling returning 'error!'.
- B 摘要: Connects to a fixed URL and reads lines without processing them, silently catching exceptions and returning void.
- 静态失败原因: The model likely focused on syntactic differences (return type, empty loop body, different exception handling) and low token overlap, missing the shared high-level task of URL reading.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider them clones because both perform URL reading with similar Java I/O patterns, and BCB often accepts partial functionality similarity.
- 共享行为: Both open a URL and read data from the stream.
- 行为差异: A returns the content; B discards it.；A uses parameterized URL; B uses hardcoded URL.；A uses InputStream; B uses BufferedReader.；A returns error string on exception; B silently catches exceptions.
- 修正建议: Enhance model to recognize similar algorithmic intents despite structural differences.；Use data flow analysis to capture common I/O operations.；Train on incomplete or diverse implementations of the same task.

### case_id=2361 FP lexical_or_api_overlap

- 方法: `getLinksFromURLFast` vs `getFullScreenUrl`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Extracts all hyperlinks and their anchor text from a given URL's HTML page.
- B 摘要: Extracts the video ID and timestamp from a YouTube page to construct a fullscreen video URL.
- 静态失败原因: The static BERT model likely focused on overlapping API calls (URL, openConnection, BufferedReader, println) and similar control structures (while loop, try-catch), leading to a false positive due to lexical and API overlap.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled non-clone because the functions have distinct purposes (generic link extraction vs. YouTube-specific URL construction) and different output formats, despite both involving URL reading and parsing.
- 共享行为: Open a URL connection and read HTML content line by line；Use BufferedReader and InputStreamReader for I/O；Parse string data to extract specific information；Handle exceptions with try-catch
- 行为差异: A extracts all links; B extracts only YouTube-specific parameters；A returns a Vector[] of links and texts; B returns a single String；A uses regular expressions; B uses split and startsWith；A includes time logging and absolute URL conversion; B includes GUI progress updates
- 修正建议: Incorporate dataflow analysis to capture differences in output and purpose；Use models that emphasize functional semantics over token sequences；Fine-tune on natural language descriptions of function behavior

### case_id=2362 FP lexical_or_api_overlap

- 方法: `PageLoader` vs `getFrameworkFactory`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Constructor that reads all lines from a URL and concatenates them into a single string.
- B 摘要: Method that reads a service configuration file from a classpath URL, parses lines to find a non-comment, non-empty class name, and instantiates that class as a FrameworkFactory.
- 静态失败原因: The token-level overlap (e.g., 'URL', 'BufferedReader', 'readLine', 'close') and similar syntactic structure may have caused the static model to overestimate similarity, ignoring the divergent data processing logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels these as non-clones because the core functionality is completely different (reading arbitrary web content vs. loading a specific OSGi factory service), even though the I/O boilerplate is similar.
- 共享行为: Open a URL and create a BufferedReader from its input stream；Read lines from the stream using readLine()；Close the reader after use
- 行为差异: Function A concatenates all lines into one string (inputLine); Function B processes each line to skip comments and empty lines, then loads and instantiates a class；Function A uses in.ready() as loop condition; Function B uses a for loop until s == null；Function B includes error handling and throws an exception if no valid line is found; Function A does not handle errors；Function B returns a FrameworkFactory object; Function A is a constructor that sets an instance variable
- 修正建议: Incorporate dataflow analysis to capture how lines are used after reading；Add attention to the overall method signature and return type differences；Train on more diverse examples where I/O boilerplate is shared but purpose differs

### case_id=2363 FN benchmark_preference_bias

- 方法: `doGet` vs `doUpload`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `preference_memory_with_manual_audit`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Handles GET request to retrieve and display a web page, with page lookup, user permission checks, caching, and HTML generation.
- B 摘要: Handles file upload via HTTP multipart request, managing temporary directories, parsing parameters, and responding with XML or redirecting.
- 静态失败原因: Static BERT models may have been misled by low token overlap (Jaccard 0.168) and failed to recognize the high-level structural similarity of servlet handling, or they may have focused on lexical differences and missed the BCB annotation preference for broad functional categories.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may label them as clones because they are both servlet methods that process HTTP requests and produce responses, falling under broad Type-3/Type-4 similarity in BigCloneBench, which accepts partial functional overlap.
- 共享行为: Both are servlet methods handling HTTP requests and responses；Both use logging and error handling；Both check request parameters and write response output
- 行为差异: Function A retrieves and displays a page; Function B handles file uploads；Function A involves page permission and caching logic; Function B involves file handling and multipart parsing；Function A outputs HTML; Function B outputs XML or redirects
- 修正建议: Avoid relying solely on token overlap; incorporate structural or control-flow features；Train models with BCB's specific clone definitions and tolerance for partial functionality；Use high-level task labels (e.g., 'servlet handler') to improve clone detection in such cases

### case_id=2364 FN partial_functionality

- 方法: `testNetworkHTTP` vs `doVersionCheck`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: A test method that makes multiple HTTP GET requests to hardcoded URLs and discards all response data.
- B 摘要: A version check method that fetches and parses a version file from a URL to extract build version strings.
- 静态失败原因: Static BERT models like GraphCodeBERT rely on token-level similarity and structure; here the token Jaccard is low (0.207), and the methods have different lengths and different control flow (multiple connections vs. one). The model likely focused on the differing parts and missed the common boilerplate.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider these as Type-3 clones because they share the same pattern of opening a URL, reading lines with a while loop, and handling IO exceptions, despite different purposes and URL targets.
- 共享行为: Both open a URL, create a BufferedReader from the input stream, and read lines in a while loop.；Both catch IOException and perform error handling.
- 行为差异: A makes six sequential connections; B makes one.；A discards all read lines; B parses lines for specific prefixes.；A uses hardcoded URLs; B uses a property.；A does not process data; B calls another method with extracted versions.
- 修正建议: Increase representation of high-level I/O patterns.；Use data flow to capture the common reading loop structure.；Consider that methods may be clones if they share a common API usage skeleton even if surrounding logic differs.

### case_id=2365 FN benchmark_preference_bias

- 方法: `sendExceptionToServer` vs `loadMFileViaWeb`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Sends exception details to a remote server via HTTP POST, building a query string with encoded parameters and reading the response.
- B 摘要: Loads a .m file from a web URL, reads its content line by line, and parses it into a UserFunction object.
- 静态失败原因: The static model correctly identified low token overlap (0.14) and different method names/purposes, leading to a non-clone prediction. It failed to align with BCB's preference for broader functional similarity.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider them clones because both involve network I/O, reading from URLs, and share similar boilerplate code (URL creation, BufferedReader, exception handling), fitting a broad Type-3/4 pattern.
- 共享行为: Both open a URL and read lines of text using BufferedReader.；Both handle exceptions with try-catch blocks.
- 行为差异: Function A writes data to the connection (POST), while B only reads.；Function A builds a complex query string with encoded parameters; B simply concatenates lines.；Function A returns void; B returns a UserFunction.；Function A logs to console; B uses ErrorLogger and returns the parsed function.
- 修正建议: Incorporate task-level or domain-level similarity features.；Adjust thresholds or use ensemble methods to better match BCB annotation style.

### case_id=2366 FN partial_functionality

- 方法: `copyResource` vs `decodeFileToFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource from a URL or local file to a destination file byte by byte.
- B 摘要: Decodes a Base64-encoded file and writes the decoded output to another file using a buffered stream.
- 静态失败原因: The models likely focus on token-level overlap and structural similarity, but the low Jaccard similarity and the presence of Base64 decoding in function B created a semantic gap that was not captured by static embeddings.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled them as clones because both are stream copy operations with similar structural patterns (stream opening, loop, closing), and it may tolerate differences in input source handling (URL vs file) and decoding as a minor transformation.
- 共享行为: Both read from an input stream and write to an output stream.；Both use a while loop to transfer bytes from input to output.；Both close streams in a finally block (B explicitly, A implicitly at end).
- 行为差异: A reads raw bytes; B decodes Base64 during reading.；A uses single-byte read/write; B uses a 65536-byte buffer for efficiency.；A throws an exception on error; B returns a boolean and prints stack trace.；A determines input from a 'source' field and destination via a method; B takes explicit file paths as parameters.
- 修正建议: Incorporate data-flow analysis to detect the transformation applied to the data (e.g., Base64 decoder).；Use semantic-aware features like API call signatures for input/output stream types.

### case_id=2367 FP lexical_or_api_overlap

- 方法: `run` vs `handledRun`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Downloads a map tile from a URL, parses it into vector geometries, and adds them to a data layer.
- B 摘要: Downloads a game data XML from a URL, checks version, and updates local file if newer.
- 静态失败原因: Static BERT models overemphasize API token overlap (URL, openStream, BufferedReader, etc.) and ignore the wider semantic context
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels as non-clones because the functions perform entirely different tasks despite similar I/O patterns
- 共享行为: Both open a URL and read from an input stream；Both handle IO exceptions；Both use BufferedReader and URL classes
- 行为差异: Different URLs and data formats (GeoJSON vs XML)；Different post-processing: vector tile geometry vs file version check and write；Different error handling and logging
- 修正建议: Incorporate data flow or program dependence analysis；Train on more diverse non-clone pairs with shared APIs but different semantics；Use contrastive learning to distinguish common utility patterns

### case_id=2368 FN partial_functionality

- 方法: `readAndRewrite` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.4`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a DICOM image from a file, parses it, reads pixel data, and writes it to another file with DICOM encoding.
- B 摘要: Downloads a KMZ file from a URL, reads it as a zip archive, and extracts all entries to files.
- 静态失败原因: The static BERT model likely relied on token-level similarities (Jaccard = 0.118) and different method names, missing the abstract structural pattern of reading and writing streams. It failed to generalize across different domain-specific libraries.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label these as clones because both functions follow a common high-level template of 'read from input, process, write to output', which aligns with broad Type-3/Type-4 clones where partial functionality similarity is accepted, especially when I/O boilerplate dominates the code.
- 共享行为: Both open an input stream from a source (file or URL)；Both process data and write output to files；Both use buffered streams and close resources in a similar pattern
- 行为差异: Function A deals with DICOM medical image format; Function B deals with KMZ/ZIP archive format；Function A uses specialized DICOM libraries (DcmParser, PixelDataReader); Function B uses standard Java ZIP libraries；Function A writes the entire dataset with encoding; Function B extracts individual zip entries
- 修正建议: Incorporate dataflow analysis to capture 'input-to-output' transformations regardless of library specifics；Use graph-based representations that generalize I/O operations (e.g., open, read, write, close)；Train with more examples of cross-domain read-write patterns

### case_id=2369 FP lexical_or_api_overlap

- 方法: `doVersionCheck` vs `getTicketsForQueue`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Performs a version check by reading a remote URL and comparing build versions.
- B 摘要: Retrieves open tickets for a given queue from a REST API and returns a list of ticket objects.
- 静态失败原因: The model likely over-relied on lexical overlap (e.g., 'BufferedReader', 'line', 'URL', 'try-catch') and common I/O boilerplate, missing the fundamentally different functionality and control flow.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically requires semantic equivalence or near-equivalence for positive clones. These functions have completely different purposes and outputs, so BCB correctly labeled them as non-clones.
- 共享行为: Both use HTTP/URL connections to fetch data from a remote server.；Both read lines from an input stream using BufferedReader.；Both parse lines to extract specific information (build versions or ticket IDs).；Both handle IOExceptions and other exceptions with logging or error messages.
- 行为差异: Function A returns void and updates a view; Function B returns a List<RTTicket>.；Function A reads a version check URL; Function B constructs a REST API query with parameters.；Function A extracts version strings; Function B extracts ticket IDs and retrieves full ticket objects.；Error handling differs: A shows an error dialog; B throws custom exceptions or logs errors.
- 修正建议: Incorporate data flow or AST-based structural features to differentiate I/O boilerplate from core logic.；Use type information or method signatures to detect output type mismatches.；Train on more diverse examples with high lexical overlap but semantic difference.

### case_id=2370 FP boilerplate_overlap

- 方法: `readTwitterFead` vs `main`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads Twitter timeline JSON from a URL using HttpClient, returns the content as a string.
- B 摘要: Reads a webpage from a URL using URL.openStream() and prints each line to the console.
- 静态失败原因: The model likely over-relied on lexical and structural similarities (common I/O boilerplate) and failed to differentiate the distinct output handling and error management.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically requires functional equivalence; here the tasks differ (retrieve JSON vs. print webpage), so it is not a clone.
- 共享行为: Both open an HTTP connection to a URL；Both use BufferedReader and InputStreamReader to read lines；Both iterate over lines in a while loop
- 行为差异: A uses HttpClient, B uses URL.openStream()；A checks HTTP status code (200), B does not；A handles exceptions with try-catch, B throws IOException；A returns the concatenated lines as a String, B prints lines to stdout
- 修正建议: Incorporate dataflow analysis to track how the read content is used；Enhance training with hard negatives that share I/O patterns but differ in core logic

### case_id=2371 FN benchmark_preference_bias

- 方法: `DialogHelper` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.3`
- 推荐路线: `preference_memory_with_manual_audit`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Constructs a dialog to save an image from a URL to a file, with user confirmation and file channel copy.
- B 摘要: Builds a website for editing by processing pages, transforming XML, and writing output files.
- 静态失败原因: Static BERT/GraphCodeBERT fail due to low token overlap (0.085), long code length, and lack of shared API usage; they rely on lexical and structural features which are too distinct. The high-level semantic similarity (file I/O and error handling) is not captured by these models.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB likely labeled as Type-4 clone because both methods involve file I/O operations with similar patterns of file existence checks, error handling, and output file generation, despite different application contexts.
- 共享行为: Both perform file output operations (write to file).；Both handle IOException and file path/extension checks.；Both involve some form of UI/console interaction (A uses dialogs, B writes debug messages).
- 行为差异: Function A is a UI constructor for a single image save; B is a complex method for generating multiple website pages.；A uses JFileChooser and JOptionPane for user interaction; B uses no UI, only file system operations.；A copies file using FileChannel; B uses custom FileSystem to write strings.；B involves XML transformation, DOM traversal, and FTP integration; A does not.
- 修正建议: Incorporate training examples of Type-4 clones (semantic clones) with low lexical overlap.；Use pre-training on API call sequences and control flow to capture functional intent.；Apply data augmentation to emphasize high-level behavior over surface forms.

### case_id=2372 FP other

- 方法: `actionPerformed` vs `fileCopy`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Handles UI action events to set various application preferences (e.g., file paths for external tools, scale image options, date format, look and feel) and updates the UI accordingly.
- B 摘要: Copies a file from a source path to a destination path with error checking and stream handling.
- 静态失败原因: The static BERT model likely failed due to lexical or API overlap (e.g., both use File, InputStream/OutputStream in A? Actually A uses File only in the file chooser branch, not streams) or common Java idioms (null checks, try-catch). More probably, the model made a spurious positive error due to the long length of function A and insufficient semantic understanding, leading to a false match.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB would not consider these clones because their functionality is entirely different: one is a UI preference setter, the other is a file copy routine. There is no overlap in the core behavior or domain.
- 共享行为: Both are Java methods that perform some I/O operations (file chooser in A, file copy in B)
- 行为差异: Different purpose: event handler vs utility file copy；Different inputs: ActionEvent vs file paths；Different outputs/side effects: updates UI preferences vs creates a file copy；Different error handling: silent returns vs exceptions and abort calls
- 修正建议: Improve training data to include more diverse non-clone pairs with low token similarity；Enhance model with control flow and data flow analysis to capture semantic purpose；Use contrastive learning to better separate unrelated functions

### case_id=2373 FP boilerplate_overlap

- 方法: `readData` vs `copyFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Parses several comma-separated string fields into sets and maps of characters or tokens.
- B 摘要: Copies a file from source to destination using buffered streams.
- 静态失败原因: Static BERT may have been misled by the presence of common Java I/O and collection classes (e.g., IOException, StringTokenizer, HashSet) and similar control flow (while loops with try-catch), despite low token overlap, causing an overgeneralization to 'both read and process data'.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clone because the functions have completely different logic and purpose, despite some shared I/O exception handling patterns.
- 共享行为: Both use try-catch blocks for IOException；Both use while loops to process data
- 行为差异: readData splits strings into tokens and populates data structures; copyFile reads bytes from one file and writes to another；readData has no file I/O; copyFile is purely file I/O；readData is about initialization; copyFile is about file duplication
- 修正建议: Improve model to focus on core semantics rather than common API usage；Incorporate dataflow or structure-aware features to differentiate between parsing configuration and file copying

### case_id=2374 FN partial_functionality

- 方法: `runInternal` vs `callApiPost`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Opens an HTTP connection, reads an OPDS catalog in a loop with support for pagination, downloads books, and updates UI progress.
- B 摘要: Sends an HTTP POST request with parameters, checks response code, and returns the response input stream.
- 静态失败原因: Static BERT models rely on token overlap and local syntactic patterns; the low Jaccard similarity and disjoint method structures (loop vs. linear) mislead it to predict non-clone despite shared HTTP semantics.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels Type-4 clones where functions share a common core behavior (HTTP request/response handling) even if overall purpose differs, tolerating added or different logic.
- 共享行为: Both create an HTTP connection and set headers/timeouts.；Both handle response codes and retrieve input streams.；Both use HttpURLConnection and manage exceptions.
- 行为差异: A uses GET (implicit) and loops to handle pagination and download; B uses POST and is single-shot.；A parses XML catalog data and manages UI updates; B returns a raw stream.；A has complex error handling with callbacks; B throws exceptions.
- 修正建议: Use a model that captures task-level intent, such as GraphCodeBERT with dataflow.；Include API usage patterns and control flow abstraction.；Augment training with more diverse Type-4 clone pairs.

### case_id=2375 FN lexical_or_api_overlap

- 方法: `main` vs `copy`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Extracts all entries from a remote zip file to local files.
- B 摘要: Copies the entire content of a local file to another local file.
- 静态失败原因: Static BERT models rely on token similarity and may have been misled by the low Jaccard score (0.197) or missed the abstract I/O pattern, predicting non-clone. Alternatively, the model might have correctly identified the semantic difference but BCB's labeling is broad.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely considers both as I/O copy operations at a high level, accepting broad Type-3/Type-4 similarity despite different data types and sources.
- 共享行为: Both read data from a source and write to a destination using a loop.；Both use I/O streams to transfer data.
- 行为差异: A reads a zip file from a URL and extracts multiple entries; B copies a single file.；A uses byte arrays and ZipInputStream; B uses character streams (FileReader/Writer).；A handles different protocols (file/http); B only handles local files.；A outputs to files named after zip entries; B outputs to a specified file path.
- 修正建议: Improve model's ability to distinguish data types (byte vs char) and stream sources.；Incorporate structural or dataflow analysis to capture I/O differences.；Train on more diverse I/O patterns to recognize when operations are fundamentally different.

### case_id=2376 FP boilerplate_overlap

- 方法: `main` vs `doImageProcess`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Main method parsing Prolog files and generating adapter classes.
- B 摘要: Private method processing an image request and writing bytes to an HTTP response.
- 静态失败原因: Static BERT models often rely on lexical and syntactic overlap; both functions contain common boilerplate (try-catch, I/O operations, method calls like IOUtils.copy) that could be mistaken for similar functionality.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels clones only if functions share significant semantic behavior; these functions are entirely unrelated in purpose.
- 共享行为: Use of I/O streams (input/output streams)；Exception handling (throws IOException, catch blocks)；Resource handling (closing streams)
- 行为差异: Function A is a main entry point; B is a private method invoked by servlet container.；A parses Prolog files and generates Java classes; B processes image data and writes to HTTP response.；A involves complex framework-specific logic (class generation, adapters); B is straightforward image processing.
- 修正建议: Incorporate control flow or data flow analysis to distinguish different business logic.；Use function-level embeddings that capture core semantics rather than surface-level API calls.；Apply a weighted attention mechanism to focus on unique identifiers and method-specific structures.

### case_id=2377 FP lexical_or_api_overlap

- 方法: `getDatasetsList` vs `getFrameworkFactory`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Caches and returns a list of dataset names fetched from a server URL.
- B 摘要: Loads and returns a FrameworkFactory instance from a service configuration file.
- 静态失败原因: Static BERT over-relied on lexical and API-level overlap (BufferedReader, URL, readLine) without capturing the distinct semantic goals and data flow.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clone because the methods serve entirely different purposes and produce different outputs, despite sharing a common read-loop pattern.
- 共享行为: Both use BufferedReader to read lines from an input stream；Both iterate over lines using readLine() in a loop
- 行为差异: Different return types (List<String> vs FrameworkFactory)；Different input sources (URL parameter vs classpath resource)；Different caching strategies (cached HashMap vs no cache)；Different exception handling (RuntimeException vs throws Exception)
- 修正建议: Incorporate data-flow analysis to track how read data is used；Add method-level context or type information to distinguish purposes

### case_id=2378 FP lexical_or_api_overlap

- 方法: `getLinksFromURLFast` vs `callService`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Opens a URL, reads HTML content, extracts hyperlinks using regex, and returns vectors of links and anchor texts.
- B 摘要: Constructs a URL from components, opens a connection, reads the response into a string buffer, and stores it in a field, with error handling.
- 静态失败原因: Static models like BERT may be misled by overlapping API usage (URL, BufferedReader, readLine, StringBuffer) and similar control flow, ignoring the distinct post-processing steps that define the functions' purposes.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels based on overall functionality. Despite shared boilerplate (URL reading), the core intents differ (link extraction vs service call), so it would likely be considered a non-clone.
- 共享行为: Both open a URL and read its content line by line into a StringBuffer.
- 行为差异: Function A parses HTML to extract links and texts; Function B simply stores the raw response.；Function A uses regex for pattern matching; Function B does not parse content.；Function A returns an array of vectors; Function B sets a field and handles exceptions internally.；Function A throws Exception; Function B catches MalformedURLException and IOException.
- 修正建议: Incorporate semantic analysis of variable usage and dataflow beyond surface-level tokens.；Consider method signatures and return types to differentiate functionality.；Use structural features like method length or unique API calls (e.g., regex in A) to distinguish.

### case_id=2379 FN benchmark_preference_bias

- 方法: `copyLogic` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Copies a class file from source to destination using file channels with state management.
- B 摘要: Builds a website for editing by transforming XML templates and writing HTML pages.
- 静态失败原因: Static BERT/GraphCodeBERT relied on low token Jaccard (0.069) and distinct method signatures, predicting non-clone. It failed to recognize the broad file I/O similarity that BCB considered.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB likely labeled these as clone due to both involving file I/O operations, exception handling, and use of properties, under a broad Type-4 (similar functionality) interpretation. However, the actual functionality differs significantly.
- 共享行为: Both use FileInputStream/FileOutputStream for file I/O.；Both catch IOException.；Both use properties files for configuration.
- 行为差异: A performs a simple binary file copy; B performs complex text transformation and HTML generation.；A has explicit state machine (Idle, Synchronizing); B has no state machine.；B uses many parameters and external libraries (FTP, DOM, Transformer); A uses only standard Java NIO.；B is much longer and involves loops; A is short and sequential.
- 修正建议: Enhance models with higher-level semantic understanding of file operations.；Use AST or flow-sensitive features to capture structural patterns beyond token overlap.；Incorporate task-specific heuristics for BCB-style annotations.

### case_id=2380 FP boilerplate_overlap

- 方法: `perform` vs `scramble`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Handles HTTP request to classify a concept and forwards to appropriate page.
- B 摘要: Computes SHA-1 hash of input string.
- 静态失败原因: Static BERT may have been misled by superficial similarities such as common library usage (e.g., StringBuffer, try-catch, byte operations) and ignored the overall semantic mismatch due to lack of long-range understanding.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB does not consider these clones because they perform completely different operations, one being a web action and the other a hashing utility, with no functional overlap.
- 共享行为: Both use try-catch blocks；Both manipulate strings
- 行为差异: Function A is a web action handler with session, request, and response; Function B is a utility hashing method；Function A performs complex classification logic; Function B only computes hash；Function A has side effects on session; Function B is pure computation
- 修正建议: Improve training data with more diverse non-clone pairs that share boilerplate but differ in semantics；Incorporate control-flow and data-flow analysis to distinguish high-level purpose；Use graph-based models that capture structural differences

### case_id=2381 FN partial_functionality

- 方法: `addDataFromURL` vs `runScript`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a URL line by line and appends each line plus a newline to a class-level variable 'thetext'; on exception, appends the URL string.
- B 摘要: Constructs a URL from a base code and script name, reads byte by byte into a string, and returns it; on exception, returns 'error!'.
- 静态失败原因: Static BERT models rely heavily on lexical and syntactic surface similarity. The token Jaccard is low (0.27), method names differ, and control structures (while vs do-while, line vs byte reading) are distinct. The model likely missed the underlying semantic similarity of URL reading due to lack of data flow or long-range dependency capture.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB annotations in BigCloneBench often consider Type-3/Type-4 clones where two methods perform the same high-level task (reading from a URL) even if implementation details differ. Both functions exhibit the same core pattern: open URL, read data, handle exceptions. This aligns with BCB's broad clone labeling.
- 共享行为: Both open a network connection via URL and read content from it.；Both handle IO exceptions by setting a fallback value (appending URL or returning 'error!').；Both use InputStream to read data from the URL.
- 行为差异: A reads line-by-line using BufferedReader; B reads byte-by-byte using BufferedInputStream.；A appends content to a field and does not return a value; B builds and returns a string.；Error handling: A appends the URL string to thetext; B returns 'error!' string.；A explicitly closes the stream in a separate try-catch; B does not explicitly close the stream.
- 修正建议: Augment training data with positive examples of URL-reading clones despite different reading granularities.；Incorporate data flow information or abstract syntax trees to capture the common sequence of operations (open stream, read, handle exception).；Use contrastive learning to focus on functional similarity rather than exact token overlap.

### case_id=2382 FN benchmark_preference_bias

- 方法: `modifyApplicationMessage` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Modifies a localized properties file by reading an English fallback, copying if missing, then updating or appending a key-value pair.
- B 摘要: Demonstrates file I/O using FileChannel, ByteBuffer, and different character encodings, writing and reading a text file multiple times.
- 静态失败原因: The static model correctly predicted non-clone; the 'failure' is relative to a potentially erroneous BCB label, so the model did not fail in semantic understanding.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might have labeled this as a broad Type-4 clone due to both involving file reading/writing, but the functionality is completely different; likely a labeling error in the dataset.
- 共享行为: Both perform file I/O operations (write/read) using Java I/O classes.
- 行为差异: A targets properties files for localization; B works with a generic text file.；A modifies existing content; B only writes and reads static or repeated content.；A uses Properties and BufferedReader; B uses FileChannel and ByteBuffer.；A has conditional logic for file existence and key matching; B is linear without decision.
- 修正建议: Exclude this pair from evaluation or correct the BCB label.

### case_id=2383 FP boilerplate_overlap

- 方法: `readUNI` vs `getPagina`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `9.0`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads tab-separated data from a URL, skips header, parses id and description pairs, and adds them to a vector.
- B 摘要: Fetches entire content of a URL as a single string, optionally setting an authenticator, and returns concatenated lines.
- 静态失败原因: High token overlap from common URL-reading boilerplate (30% Jaccard) misled the model into thinking they are clones, overlooking different parsing and return logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clones when functions perform distinct tasks despite sharing boilerplate; here the data processing logic is fundamentally different.
- 共享行为: Both open a URL stream for reading；Both handle MalformedURLException and IOException；Both use try-catch-finally to close resources
- 行为差异: Function A parses tab-delimited fields ignoring the second field, while B concatenates all lines；Function A returns void and fills a provided vector, B returns a concatenated string；Function A skips first line, B reads all lines；Function A uses Scanner, B uses BufferedReader
- 修正建议: Incorporate AST or dataflow analysis to detect differences in processing structure；Use contrastive learning to distinguish between similar boilerplate and actual functional equivalence；Add features like method signature (return type, parameters) to embeddings

### case_id=2384 FP lexical_or_api_overlap

- 方法: `getWebPage` vs `readUNI`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads entire content from a URL and returns it as a string.
- B 摘要: Reads a tab-separated file from a URL, parses specific fields, and populates a vector.
- 静态失败原因: Static BERT/GraphCodeBERT likely overemphasized lexical/API overlap (e.g., URL, openStream, BufferedReader/Scanner, while-read loop) and missed the critical differences in data flow and output semantics.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels these as non-clones because they perform distinct operations (one returns raw content, the other parses structured data) despite using similar I/O patterns.
- 共享行为: Both open a URL stream；Both read input line by line
- 行为差异: Function A returns concatenated page content; Function B extracts specific tab-delimited fields；Function A on error throws an Error; Function B catches exceptions and prints stack trace；Function A does not close the stream; Function B closes stream in finally block
- 修正建议: Train model to distinguish data transformation steps beyond API sequence；Incorporate data flow analysis to track how input is processed and what output is produced；Use contrastive learning on examples with high API overlap but different functionalities

### case_id=2385 FN lexical_or_api_overlap

- 方法: `doVersionCheck` vs `httpRequestByPOST`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Performs a version check by reading a version file from a URL and updates the UI accordingly.
- B 摘要: Sends an HTTP POST request with parameters and returns the response body as a string.
- 静态失败原因: Static BERT relies on token-level similarity; low Jaccard score and different method names, library calls (URL vs HttpClient), and return types cause it to miss the high-level behavioral pattern.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB often labels similar structural patterns (e.g., network I/O with line-by-line reading and exception handling) as Type-3/4 clones, even with different specific APIs or domain logic.
- 共享行为: Both functions perform network I/O operations (connecting to a URL).；Both read data line by line from an input stream.；Both handle IOException with error reporting.
- 行为差异: Function A uses URLConnection and reads a specific version file format; Function B uses HttpClient and HTTP POST.；Function A updates a View object (UI); Function B returns a String and sets error codes.；Function A checks version and build numbers; Function B checks HTTP status code.
- 修正建议: Enhance model with structural or graph-based representations (e.g., AST, CFG) to capture I/O patterns.；Use data flow analysis to recognize similar operations like opening streams and reading lines.

### case_id=2386 FN partial_functionality

- 方法: `doVersionCheck` vs `register`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Opens a URL to check version information and displays result or error.
- B 摘要: Registers a user by encoding password, creating hash, calling a forum URL to create phpBB user, persisting, and sending confirmation email.
- 静态失败原因: Static BERT models likely focused on high lexical/API overlap (URL, BufferedReader, IOException) but lacked understanding of the divergent overall logic and method names, leading to false positive removal.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled this as clone due to the shared pattern of URL opening, stream reading, and IOException handling, considering it broad Type-4 partial functionality similarity despite differing overall purpose.
- 共享行为: Opens a URL connection and reads lines from an InputStream using BufferedReader
- 行为差异: Function A checks software version lines; Function B registers a user with multiple additional steps (password encoding, hash creation, database persistence, email sending).；Function A has simple error handling; Function B has complex error handling and logging.；Function A calls another overload; Function B returns boolean based on email sending success.
- 修正建议: Incorporate method name semantics or docstrings to capture overall intent.；Use graph-based representations that model control and data flow beyond token sequences.

### case_id=2387 FP lexical_or_api_overlap

- 方法: `getVersion` vs `load`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches the latest version string from a hardcoded URL, returns it or null on error.
- B 摘要: Loads and returns concatenated XML content from a pastebin URL based on input ID, with error dialog and working flag.
- 静态失败原因: High lexical overlap (URL, BufferedReader, try-catch, while-read loop) led to false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely considers these non-clones because they perform different semantic tasks (version check vs XML load) with different error handling and output semantics.
- 共享行为: Both connect to a URL and read lines using BufferedReader；Both return a String
- 行为差异: A has fixed URL, B constructs URL from parameter；A returns single line, B concatenates all lines；A returns null on error, B returns empty string on error and shows dialog；B has length check and early return, A has debug print and working flag
- 修正建议: Incorporate data flow analysis to differentiate URL construction and return handling；Use AST-based structural differencing to capture control flow differences (early return, dialog)

### case_id=2388 FN benchmark_preference_bias

- 方法: `setPayload` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Copies content from a static data file to a target file using FileChannel, then updates internal array index.
- B 摘要: Validates and processes a Maven-based NexOpen project for launch, including XML profile handling, property setting, and resource management.
- 静态失败原因: Static BERT model correctly predicted non-clone (0), so it did not fail; the BCB label is questionable.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: Possible annotation error: BCB may have incorrectly labeled them as clones due to superficial similarity like both involving file I/O, but the semantics are completely different.
- 行为差异: A performs a simple file copy; B involves complex configuration and XML parsing.；A returns boolean; B returns void.；A uses low-level FileChannel; B uses Eclipse/Java APIs like IProject, IFile, Properties.；A modifies internal index; B sets persistent properties on resources.
- 修正建议: Re-evaluate the BCB annotation for this pair; likely remove the clone label.；Improve benchmark consistency by requiring more functional overlap for clone labeling.

### case_id=2389 FP lexical_or_api_overlap

- 方法: `googleImageSearch` vs `doVersionCheck`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Searches Google Images using HTTP GET, parses HTML to extract image URLs, and updates UI with an album art icon.
- B 摘要: Checks for software version by fetching a URL, reading lines to extract build numbers, and delegates to another method.
- 静态失败原因: Static BERT/GraphCodeBERT may have been misled by the strong lexical overlap in common patterns like URL opening, BufferedReader usage, and exception handling, failing to capture the distinct high-level semantics and control flow.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would label this as non-clone because the two functions have different purposes (image search vs version check), different output (UI update vs method call), and only share a common boilerplate of opening an HTTP connection and reading lines.
- 共享行为: Both use URL and HttpURLConnection/InputStream to fetch data from the web；Both read lines from a BufferedReader；Both handle exceptions using try-catch blocks；Both manipulate strings (replace, split, trim, substring)
- 行为差异: Function A fetches images from Google Images, while B fetches version info from a jEdit property URL；Function A parses HTML with regex to extract image URLs, B parses lines with prefix matching (.build, .stablebuild)；Function A updates UI components (albumArtLabel, button), B calls doVersionCheck(view, ...) and shows/hides wait cursor；Function A clears a list and populates it, B assigns values to local variables and invokes another method
- 修正建议: Include data flow analysis to distinguish variable usage and output destinations；Add type-based heuristics for method return/parameter usage；Use control flow graph or program dependency graph for structural matching；Augment training data with harder non-clone pairs that share API sequences but differ in purpose

### case_id=2390 FP partial_functionality

- 方法: `executeHttpGet` vs `getVersion`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Executes HTTP GET on given URI and returns response body as JSONObject.
- B 摘要: Fetches version string from a hardcoded URL, returns first line as String, with exception handling returning null.
- 静态失败原因: Static BERT/GraphCodeBERT models may over-rely on structural similarities (both have while loop reading BufferedReader, similar control flow, HTTP connection) and miss differences in return types, error handling, and library usage, leading to false positive.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely labels as non-clone because functions have different return types and error handling semantics; overall functionality is not equivalent (generic HTTP GET returning JSON vs specific version fetcher returning string), and token overlap is low.
- 共享行为: Both perform HTTP GET requests；Both read response line by line using BufferedReader
- 行为差异: Return type differs: JSONObject vs String；Error handling: A throws Exception, B catches Exception and returns null；API usage: A uses Apache HttpClient, B uses URLConnection；Parameterization: A takes URI, B uses hardcoded URL
- 修正建议: Incorporate data flow analysis to track return types and exception propagation；Use finer-grained semantic matching considering API usage and return type；Add training examples with similar structure but different semantics

### case_id=2391 FN partial_functionality

- 方法: `getFile` vs `copy`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, optionally modifies an endpoint attribute, and returns the local file path.
- B 摘要: Copies a source file to a destination file using NIO FileChannel, creating parent directories if needed.
- 静态失败原因: Static BERT or GraphCodeBERT likely focused on overall semantics and structural differences, missing the fine-grained similarity of the FileChannel.transferFrom pattern. The low token overlap and different method names also contributed to the misclassification.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB's annotation may consider both as file I/O operations using NIO channels, focusing on the common sub-functionality of data transfer, which is a distinct pattern despite the overall different contexts.
- 共享行为: Both use FileChannel.transferFrom to copy bytes from an input stream to an output file.
- 行为差异: Function A involves network download, XML parsing, file existence check, and endpoint modification; function B is a straightforward local file copy.；Function A returns a String; function B returns void.；Function A has extensive error handling for multiple exception types; function B handles only FileNotFoundException and IOException.；Function A copies from a URL input stream; function B copies from a FileInputStream.
- 修正建议: Incorporate AST-based or data-flow analysis to detect reusable sub-patterns like NIO channel copying.；Use contrastive learning to emphasize common subroutines in long functions.

### case_id=2392 FP other

- 方法: `main` vs `copy`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Parses a Prolog file, generates adapter classes and writes them to a JAR file.
- B 摘要: Recursively copies a file or directory, skipping .svn folders and checking timestamps.
- 静态失败原因: Static BERT models may over-rely on superficial token overlap (e.g., File, IOException, return) or common structural patterns (try-catch, loops) while missing the overall semantic context. The high-level task difference is not captured.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely labeled this as non-clone because the two functions have completely different purposes and implementations, with no meaningful semantic similarity.
- 共享行为: Both operate on files and directories；Both use File objects and handle exceptions
- 行为差异: Function A performs complex code generation from Prolog input; Function B performs simple file copying.；Function A outputs a JAR file; Function B replicates directory structure.；Function A involves parsing, visiting, class writing; Function B uses streams for binary copy.；Function A has command-line argument parsing; Function B is a utility method.
- 修正建议: Improve training data with more diverse negative examples；Incorporate structural or semantic features like method names and control flow；Use code summarization to capture high-level intent

### case_id=2393 FP lexical_or_api_overlap

- 方法: `import_hints` vs `loadURL`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a file (local or URL) containing puzzle piece hints, parses each line, and places the pieces on a board with rotation and hint marking.
- B 摘要: Downloads content from a URL (with basic authentication) and writes it to a temporary VRML file, updating a status label with the file size.
- 静态失败原因: Static BERT may have focused on overlapping tokens like 'URL', 'BufferedReader', 'IOException', and 'openStream', missing the semantic gap between puzzle hint loading and file downloading.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled these as non-clones because they perform completely different tasks with different outputs and domain-specific operations, even though they share some I/O patterns.
- 共享行为: Both open a URL or file input stream；Both use BufferedReader to read lines；Both handle IOException
- 行为差异: A parses tokens and calls board manipulation methods; B writes to a temp file and updates UI；A is puzzle-specific; B is for downloading VRML data；A returns boolean; B returns void and has different parameters
- 修正建议: Train on more diverse data to reduce reliance on surface-level API usage；Incorporate program analysis features (e.g., data flow, control flow) to capture functional semantics；Use contrastive learning to distinguish different high-level tasks

### case_id=2394 FP long_range_semantics

- 方法: `readData` vs `copyDeleting`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `static_summary_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Parses multiple string fields and a configuration file to populate hash sets and a map for Tibetan transliteration.
- B 摘要: Copies the contents of a file to a destination file using a buffered stream.
- 静态失败原因: The static BERT/GraphCodeBERT model likely overfitted on shallow features such as method signature (static void) and the presence of I/O and exception handling, failing to capture the vast difference in logic and data flow.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB labels these as non-clones because their functionalities are entirely different and the code structure shows no meaningful similarity beyond trivial syntactic patterns like static void methods.
- 共享行为: Both are static void methods.；Both involve I/O operations (file reading in A, file copying in B).；Both handle exceptions (catching IOException in A, declaring throws IOException in B).
- 行为差异: Function A reads and initializes data structures from string tokens and a file; function B copies a file byte by byte.；Function A is long and complex with multiple inner loops; function B is short and straightforward.；Function A uses StringTokenizer and HashSets; function B uses FileInputStream and FileOutputStream.
- 修正建议: Incorporate data flow analysis to distinguish reading vs. copying.；Use structural similarity metrics beyond token overlap.；Train on larger diverse examples to avoid overfitting on boilerplate patterns.

### case_id=2395 FP boilerplate_overlap

- 方法: `main` vs `readAndRewrite`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Generates adapter classes from a Prolog file and writes them to a JAR.
- B 摘要: Reads a DICOM image file, parses its header, and rewrites the pixel data to another file.
- 静态失败原因: The static BERT/GraphCodeBERT model likely overemphasized structural AST similarities (e.g., both have a sequence of method calls, file operations, and exception handling) while ignoring the critical API-level and domain-specific distinctions, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB non-clone label is consistent because the functions address completely different problem domains (Prolog adapter generation vs. DICOM file conversion) and share no meaningful functional similarity beyond generic file I/O patterns.
- 共享行为: Both involve file I/O: reading input, processing, writing output.；Both use parsing (Prolog vs. DICOM).；Both contain control flow with try-catch or exception handling.
- 行为差异: Input format and domain: Prolog file vs. DICOM image.；Output: JAR with generated adapter classes vs. DICOM file with processed pixel data.；Processing logic: adapter generation using ClassWriter vs. pixel data manipulation.；Library dependencies: PrologParser, ClassWriter vs. ImageIO, DcmParser.
- 修正建议: Incorporate API call embeddings to capture domain-specific libraries.；Apply attention to identifiers and method names for functional context.；Use data-flow or type information to distinguish different processing pipelines.

### case_id=2396 FN benchmark_preference_bias

- 方法: `doGet` vs `run`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Handles HTTP GET request to retrieve and render a page with permission checks and caching.
- B 摘要: Processes files for pseudolocalization by reading, transforming, and writing messages.
- 静态失败原因: The static model correctly identified the lack of semantic and lexical similarity, but the BCB benchmark label conflicts with this, leading to a false negative classification in evaluation.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: The BCB annotation likely incorrectly labeled this pair as clones due to overgeneralization (e.g., both being methods with loops and error handling) or annotation error.
- 共享行为: Both methods take input parameters and produce output, but the nature of input/output and processing are completely different.
- 行为差异: A is a servlet handler; B is a command-line file processor.；A deals with HTTP requests, session, and caching; B deals with file I/O and message catalogs.；A has complex permission logic and exception handling; B has simple file existence checks and extension handling.；A logs and updates statistics; B prints processing status.
- 修正建议: Re-verify BCB annotation for this pair; consider correcting the label to 0.；Improve annotation guidelines to avoid overly broad clone definitions.

### case_id=2397 FN partial_functionality

- 方法: `testNetworkHTTP` vs `GetResponse`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: A test method that makes multiple HTTP GET requests to various URLs, discarding all responses, to send device information.
- B 摘要: A helper method that performs a single HTTP GET request and returns the concatenated response content.
- 静态失败原因: Static models like CodeBERT rely heavily on token overlap and syntactic similarity. Here, token Jaccard is low (0.268) because function A is much longer with many unique URL strings and repeated blocks. The method signatures also differ (void vs String). The model likely failed to recognize the shared API usage pattern due to low lexical overlap and focus on surface-level differences.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels Type-3/4 clones based on high-level functional similarity. Both functions implement the core pattern of making an HTTP GET request and reading the response line by line, using the same API. The differences in number of requests, return value, and error handling are considered acceptable variations for Type-3/4 clones.
- 共享行为: Both use HttpURLConnection to open a connection and set GET method.；Both read the response line by line using BufferedReader from the input stream.
- 行为差异: Function A makes multiple requests; function B makes one.；Function A discards responses; function B returns the response content.；Function A explicitly disconnects the connection; function B does not.；Error handling differs: A uses printStackTrace, B uses getStackTrace.
- 修正建议: Enhance model with structural AST embeddings to capture high-level API patterns.；Incorporate data flow analysis to track whether the response is used.；Use cross-function context or longer-range dependencies to see the repeated pattern.；Train with more examples of API-based partial functionality clones.

### case_id=2398 FP boilerplate_overlap

- 方法: `googleImageSearch` vs `getNetworkServersIPs`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches image URLs from Google Images based on artist/album info.
- B 摘要: Retrieves server IPs from a network server list file.
- 静态失败原因: Static BERT models overemphasize structural and token overlap (e.g., URL, BufferedReader) while missing semantic differences in parsing and output.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically requires functional similarity; these functions serve very different purposes despite similar boilerplate.
- 共享行为: Open a URL and read content line by line.；Use BufferedReader and URLConnection.；Parse lines and collect data into a collection.
- 行为差异: A builds a Google search URL; B takes a server list URL as parameter.；A parses href attributes for image URLs; B parses lines with specific markers for IPs.；A adds to a list; B returns a Vector.
- 修正建议: Incorporate data flow analysis to distinguish variable usage and transformations.；Use API-specific embeddings or identifiers to capture domain semantics.；Improve attention on method names and string constants.

### case_id=2399 FN benchmark_preference_bias

- 方法: `copyFile` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.2`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Copies the content of a source file to a target file using FileChannel transferTo.
- B 摘要: Launches a NexOpen project configuration by validating project structure, processing pom.xml files, setting Hibernate properties, and executing a build job.
- 静态失败原因: Static BERT models rely heavily on token overlap (Jaccard 0.038) and method name similarity; the lack of lexical and structural similarity led to a non-clone prediction, failing to capture any potential semantic similarity BCB might have intended.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as a clone due to Type-4 semantic similarity based on shared file I/O and stream manipulation patterns, but such a broad interpretation likely overestimates functional equivalence, indicating a possible annotation error.
- 共享行为: Both involve file I/O operations；Both handle streams (input/output)；Both throw or catch I/O-related exceptions
- 行为差异: copyFile is a simple file copy utility, launch is a complex Eclipse launch configuration handler；copyFile uses FileChannel for zero-copy transfer, launch uses ByteArrayOutputStream, Properties, and iterative file creation；copyFile has two File parameters, launch has ILaunchConfiguration, String, ILaunch, IProgressMonitor；copyFile throws IOException directly, launch catches exceptions and rethrows as RuntimeException
- 修正建议: Re-annotate the pair to reflect functional dissimilarity, if BCB label is erroneous；Enhance clone detection with semantic analysis of dataflow and control flow rather than surface tokens；Incorporate domain-specific knowledge to avoid overgeneralizing file I/O operations

### case_id=2400 FN partial_functionality

- 方法: `getHTML` vs `runScript`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches HTML from a URL using HTTP connection, optionally saves to file, and returns the page content as a string.
- B 摘要: Fetches a script from a URL relative to a codebase and returns its content as a string, with error handling returning 'error!'.
- 静态失败原因: Static BERT models rely on token overlap and syntactic similarity; the low Jaccard (0.169) indicates low lexical overlap. The functions have different method names, variable names, and structures (e.g., file writing block, different exception handling). The model may not recognize the shared core behavior due to insufficient training on varied syntactic forms.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often considers clones with similar core behavior despite syntactic differences; both are URL-fetching utilities, so they'd be considered Type-3 or Type-4 clones.
- 共享行为: Both retrieve data from a URL via HTTP and return the content as a string.
- 行为差异: A uses HttpURLConnection with user-agent header; B uses URL.openStream().；A reads line-by-line; B reads byte-by-byte.；A appends line separators; B uses direct char concatenation.；A optionally writes to a file; B does not.
- 修正建议: Train on more diverse syntactic variations of the same semantic behavior.；Incorporate data flow or control flow features.；Use contrastive learning with positive pairs that have low token overlap.

### case_id=2401 FN partial_functionality

- 方法: `getFile` vs `createNew`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies an endpoint attribute in the XML, and saves it to a temporary directory, returning the file path.
- B 摘要: Creates a new file in a specific directory from an input stream, subject to permission checks and specific file names, and returns a Resource object.
- 静态失败原因: Static BERT models rely on token overlap and structural embeddings, which are low here (Jaccard 0.13), causing them to miss the underlying partial functional similarity in file handling.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider these clones due to the shared file I/O subfunctionality (creating a file and writing data), which aligns with Type-3/Type-4 clone patterns where partial functionality similarity is accepted.
- 共享行为: Both create a File object and write data to it using FileOutputStream.；Both close streams after writing (via explicit close or IOUtils.closeQuietly).
- 行为差异: Function A downloads from a URL and processes XML; Function B receives an InputStream directly.；Function A returns a String file path; Function B returns a Resource object.；Function A involves XML manipulation and temporary file handling; Function B includes permission checks and specific file naming logic.
- 修正建议: Use a clone detector that recognizes subfunctional patterns (e.g., file I/O operations) rather than relying solely on token similarity.；Incorporate dataflow or syntactic structures that capture common I/O idioms (like open-write-close).

### case_id=2402 FP lexical_or_api_overlap

- 方法: `readData` vs `copy`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Parses multiple string tokens and file data to initialize character sets and mappings for Tibetan transliteration.
- B 摘要: Copies a file or directory recursively using Java NIO channels.
- 静态失败原因: The static model likely over-relied on common API elements like File and IOException, or misinterpreted similar loop/conditional structures, despite low token Jaccard similarity.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would likely label as non-clones because the functions have completely different functionality and no significant structural overlap.
- 行为差异: Purpose: initialization vs. file copying；Input: string fields vs. File objects；Output: fills data structures vs. copies file content；Algorithms: string tokenization vs. NIO channel transfer
- 修正建议: Improve context understanding of high-level purpose；Incorporate data flow and control flow analysis；Use program dependence graphs to distinguish operations

### case_id=2403 FN partial_functionality

- 方法: `runScript` vs `fetchUrl`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a script file from applet code base byte by byte via URL, returns content or 'error!' on failure.
- B 摘要: Reads a URL content line by line via BufferedReader, returns concatenated lines or empty string on failure.
- 静态失败原因: Static BERT models rely heavily on token overlap and surface syntax; low Jaccard similarity (0.229) and API differences obscure the shared functional pattern of URL-to-string conversion.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB considers Type-4 clones where both functions achieve the same goal (fetching URL content as string) despite minor API and I/O differences, aligning with the benchmark's broad functional similarity annotation.
- 共享行为: Both retrieve text content from a URL；Both return the content as a string；Both handle exceptions gracefully with a fallback string
- 行为差异: runScript reads bytes preserving newlines; fetchUrl reads lines stripping newlines；runScript returns 'error!' on exception; fetchUrl returns empty string；runScript constructs URL from code base + scriptName; fetchUrl takes arbitrary URL string；runScript uses InputStream/BufferedInputStream; fetchUrl uses InputStreamReader/BufferedReader
- 修正建议: Incorporate program analysis features (e.g., data flow graphs) to capture input-output behavior；Train on more diverse Type-4 clone examples to generalize beyond exact API matching；Use contrastive learning with functional equivalence labels

### case_id=2404 FN partial_functionality

- 方法: `run` vs `seeURLConnection`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches a URL with HTTP Basic authentication, reads the response line by line into a StringBuffer, records last interaction time, and sets a completion flag.
- B 摘要: Opens a URL connection, reads the response line by line into a StringBuffer, and logs the result.
- 静态失败原因: Low lexical overlap and differences in method signatures, authentication code, and error handling led the model to treat them as non-clones; the model missed the functional similarity due to fragmented patterns.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considers both as performing the core task of reading a URL's content into a string, which is a common pattern; auxiliary details like authentication and error handling are considered secondary.
- 共享行为: Both open a URL connection and read the input stream line by line；Accumulate lines into a StringBuffer；Close the reader
- 行为差异: A uses HttpURLConnection with GET method and sets Basic authentication header; B uses URLConnection without authentication；A includes error handling (catch Throwable); B throws Exception；A records last interaction time and sets a finish flag; B logs the result；A has a different method signature (Runnable.run() vs void seeURLConnection())
- 修正建议: Improve abstraction over implementation details like authentication and error handling；Focus on core data flow of reading URL content；Use dataflow analysis or graph-based models to capture sequences of operations

### case_id=2405 FN benchmark_preference_bias

- 方法: `test` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.6`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: A test method that loads an XML resource, initializes a traffic simulation, and runs simulation steps printing vehicle positions.
- B 摘要: A method that retrieves a resource as an InputStream with caching, using URL connection and file caching.
- 静态失败原因: The static model likely relied on low token overlap and structural differences, missing the broad functional similarity that BCB may accept, but we consider the model correct.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might consider them clones because both pertain to resource input streams, but the functions are at different levels of abstraction and do different things.
- 共享行为: Both involve obtaining an InputStream from a resource.
- 行为差异: A is a test that uses resource loading as a small step; B is a full caching implementation.；A uses ClassLoader.getResourceAsStream; B uses URL connection and caching.；A processes the stream further; B returns it or saves to cache.
- 修正建议: Improve label consistency in BCB to avoid overly broad clone annotations.；Use dataflow analysis to distinguish test code from utility code.

### case_id=2406 FP lexical_or_api_overlap

- 方法: `readZoneIDs` vs `getWebByUrl`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads integer IDs from a resource file and returns them as a HashSet.
- B 摘要: Fetches a web page from a URL, saves its content to a file, and recursively processes links.
- 静态失败原因: Static models may rely on lexical overlap (e.g., 'URL', 'openStream', 'readLine', 'catch Exception') and structural similarity (try-catch loop), ignoring deep semantic differences.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB focuses on overall functionality; these functions perform entirely different tasks despite sharing I/O patterns.
- 共享行为: Both open a URL connection and read line by line from an InputStream；Both use try-catch for exception handling
- 行为差异: Different inputs and outputs: A takes a file name and returns a set; B takes a URL, charset, and index, and has side effects；Different purpose: A parses numbers; B fetches and saves web pages, recursing on links；Different resource types: A reads from classpath resource; B reads from arbitrary URL
- 修正建议: Incorporate data-flow analysis to track variable types and return types；Add type information (e.g., return type HashSet vs void) as a feature；Use models that capture long-range semantic intent, such as structural or control-flow graphs

### case_id=2407 FN benchmark_preference_bias

- 方法: `main` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.6`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Demonstrates file encoding techniques by writing and reading text with different charsets using FileChannel and ByteBuffer.
- B 摘要: Builds an editable website from XML configuration by reading files, transforming them with XSLT, and writing output pages.
- 静态失败原因: Static BERT/GraphCodeBERT likely focused on surface-level syntax and token similarity, which is low (0.056). It may have missed the deep semantic difference because of the shared I/O operations, but the low token overlap made it predict non-clone.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might have considered both as performing file I/O operations with buffers and encoding, which could be seen as similar functionality at a high abstraction level, especially if the annotation was lenient towards Type-4 clones.
- 共享行为: Both perform file I/O (reading/writing files)；Both use buffers (ByteBuffer in A, char[] in B)；Both handle character encoding (UTF-8, UTF-16BE)
- 行为差异: Function A is a simple self-contained demo; Function B is a complex multi-step site builder；Function A uses FileChannel and ByteBuffer; Function B uses FileInputStream, FileWriter, and char arrays；Function B involves DOM parsing, XSLT transformations, and FTP, which are absent in A；Different method signatures and names
- 修正建议: Ensure that clone definitions are consistently applied; consider that trivial I/O operations alone should not constitute a clone；Provide more explicit criteria for Type-4 clones to avoid over-labeling

### case_id=2408 FN partial_functionality

- 方法: `run` vs `register`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a resource file from the classpath and sets its content as text in a GUI component.
- B 摘要: Registers a user by encoding password, setting hash, creating a phpBB forum user via HTTP, persisting to database, and sending confirmation email.
- 静态失败原因: Static BERT models often rely heavily on token overlap and structural similarity. The low token Jaccard (0.125) and lack of common API sequences (one uses classpath, other uses HTTP) would lead the model to correctly predict non-clone. The BCB label seems incorrect, so the model did not fail; rather, the ground truth may be erroneous.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have considered the common pattern of reading from a stream (both use URL and BufferedReader) as a partial functionality clone, despite the completely different surrounding logic. However, this is a weak similarity and likely a mislabel.
- 共享行为: Both use BufferedReader and InputStreamReader to read text from an input stream.；Both have try-catch blocks handling exceptions.
- 行为差异: A reads from a classpath resource file; B reads from an HTTP URL connection.；A updates a GUI component; B performs user registration and database persistence.；A is a simple read operation; B involves multiple steps including password encoding, hash generation, SQL injection prevention, and email sending.；A is a Runnable executing in a thread; B is a method returning boolean.
- 修正建议: Re-annotate this pair as non-clone following standard clone detection semantics.；Improve annotation guidelines to avoid overgeneralizing common I/O patterns as clones.

### case_id=2409 FN partial_functionality

- 方法: `readGeoParserResult` vs `postData`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Builds an XML request, sends it to a geo-parser service, parses the XML response to extract place names and gazetteer IDs, with retry logic.
- B 摘要: Sends data via HTTP POST to a given URL with specified content type and reads the response without processing it.
- 静态失败原因: Static models like GraphCodeBERT rely heavily on token-level similarity and structural AST patterns. These functions have very low token Jaccard (0.09) and distinct control flow (one has retry loops and XML parsing, the other has simple sequential steps). The model likely focused on syntactic differences and missed the conceptual shared behavior of HTTP communication, leading to a false negative.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label these as clones because both functions perform HTTP requests to external services, read responses, and involve similar I/O patterns (URL, BufferedReader, InputStreamReader). Under the broad Type-4 category, such high-level similarity in purpose (sending/receiving data over HTTP) may be considered a clone despite differences in request construction and response parsing.
- 共享行为: Both open a URL connection to a remote service；Both use BufferedReader to read the HTTP response line by line；Both handle HTTP communication and stream I/O
- 行为差异: Function A constructs an XML document as part of the request; Function B sends raw string data；Function A parses the XML response to extract structured data; Function B discards the response；Function A includes retry logic on exceptions; Function B does not retry；Function A has a testing mode that returns dummy data; Function B does not
- 修正建议: Use data-flow analysis to capture that both functions open a URL and read from an InputStream；Incorporate high-level semantic abstractions like 'HTTP request' and 'response reading' into the model；Consider task-specific fine-tuning on clone detection benchmarks that include Type-4 clones with low token overlap

### case_id=2410 FN benchmark_preference_bias

- 方法: `encodeFileToFile` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.2`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Encodes a file to Base64 and writes the encoded data to another file.
- B 摘要: Builds a website for editing by reading XML, transforming with XSLT, and writing output files with complex string processing.
- 静态失败原因: The static model correctly predicted non-clone due to low token similarity and structural differences, but the BCB label (1) suggests the model missed a clone that BCB claims exists, likely because the model relies on local patterns and does not capture high-level file I/O similarity that BCB might have used.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as a clone due to both methods performing file I/O operations (read/write), possibly considered a Type-4 semantic clone for the generic 'file copy' pattern, but this is an extremely broad interpretation.
- 共享行为: Both read from an input stream and write to an output stream；Both handle exceptions and close streams in a finally block
- 行为差异: encodeFileToFile is a simple file encoding utility; buildSiteForEdit is a complex site-building method with many parameters；buildSiteForEdit includes XML processing, XSLT transformations, and multiple file operations per page；buildSiteForEdit uses StringBuffer and character arrays for string manipulation, while encodeFileToFile only copies bytes；buildSiteForEdit has extensive debugging and property handling; encodeFileToFile has none
- 修正建议: Re-evaluate the BCB annotation for this pair; it may be a labeling error；If BCB intends such broad similarity, include a filtering step to avoid such extreme false positives；Consider using functional similarity beyond file I/O patterns

### case_id=2411 FN benchmark_preference_bias

- 方法: `main` vs `trainClassifier`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a URL and extracts its contents to disk.
- B 摘要: Trains a classifier by executing an external command with arguments and streaming output.
- 静态失败原因: The static BERT/GraphCodeBERT model correctly predicted non-clone because the semantic functionality differs vastly despite surface-level I/O boilerplate, and the token overlap is very low (0.14). The model was not misled by similar API usage.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled them as clones due to both involving I/O stream operations (reading/writing bytes) and handling external resources, but this interpretation is overly broad and likely erroneous.
- 共享行为: Both use Java I/O streams (InputStream, OutputStream) and handle byte data.；Both methods throw Exception.
- 行为差异: Function A performs network I/O and zip extraction; Function B spawns a subprocess.；Function A reads from a URL stream; Function B reads from process stdout/stderr.；Function A writes files to disk; Function B writes to System.out/err.；Function A uses ZipInputStream for decompression; Function B uses ProcessBuilder/exec.
- 修正建议: Verify BCB ground truth labels for this pair to ensure correctness.；Focus on semantic functionality rather than general I/O patterns.

### case_id=2412 FN boilerplate_overlap

- 方法: `main` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.35`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a file, applies line wrapping and title casing, writes to another file.
- B 摘要: Builds an editable site by processing XML templates, performing XSLT transformations, and writing multiple output files with control path injection.
- 静态失败原因: Static BERT models likely failed due to low lexical overlap (token Jaccard 0.07) and inability to capture the high-level structural and semantic differences between a trivial filter and a complex site builder; the models may have been misled by overlapping boilerplate I/O code.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may have considered both as 'text processing' tasks involving I/O and transformations, but this is a very loose interpretation; likely they annotated based on broad functional similarity.
- 共享行为: File I/O operations (reading and writing)；String manipulation and transformation
- 行为差异: Function A is a simple main method with two filters; Function B is a complex multi-stage site generation process；Function A processes a single file; Function B loops over multiple pages with many parameters；Function B includes XML parsing, XSLT transformation, and error handling lacking in A
- 修正建议: Improve context representation for long methods；Incorporate dataflow analysis；Use hierarchical embeddings to distinguish core logic from boilerplate

### case_id=2413 FN partial_functionality

- 方法: `httpRequestByPOST` vs `lookupFutureEvents`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.95`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Makes an HTTP POST request with parameters and returns the response body as a string, handling errors by setting error fields.
- B 摘要: Makes an HTTP GET request to the Meetup API, parses the JSON response into a list of Event objects, throwing an exception on I/O error.
- 静态失败原因: Static BERT models rely on lexical and structural token overlap, which is low (Jaccard 0.15). They miss the higher-level semantic similarity of HTTP request-response handling because the APIs and variable names differ significantly.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels as clone functions that share the same core operation (making an HTTP request and reading response) even if details differ, as this is a common pattern in Type-3/Type-4 clones.
- 共享行为: Both perform an HTTP request over the network.；Both read the response line by line using BufferedReader.；Both handle IOException.
- 行为差异: HTTP method: POST vs GET.；Input handling: A takes URL and params; B constructs URL from group identifier.；Output: A returns raw string; B returns parsed list of Event objects.；Error handling: A returns null and sets error fields; B throws custom exception.
- 修正建议: Use models that capture API call sequences or data-flow patterns.；Incorporate semantic role labeling for method invocations.；Train on cross-project clone detection with more diverse vocabulary.

### case_id=2414 FN partial_functionality

- 方法: `copyResource` vs `unzip`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource from a URL or file to a destination file using a byte-by-byte stream copy.
- B 摘要: Unzips a zip file to a target directory, creating subdirectories and extracting each entry using buffered stream copy.
- 静态失败原因: Low token overlap (Jaccard 0.222) and large syntactic differences (simple loop vs. complex zip handling) cause models like GraphCodeBERT to miss the abstract semantic similarity of stream copying.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels Type-4 semantic clones where functions share core I/O transfer logic despite different high-level tasks. Both methods copy data from input to output, which is considered functionally similar.
- 共享行为: Both read from an input source (stream or zip entry) and write to an output file using byte-level loops.；Both close streams after use.；Both throw exceptions on failure.
- 行为差异: copyResource copies a single file; unzip extracts multiple entries from an archive.；unzip creates directories and handles nested paths; copyResource does not.；unzip uses buffered reads (byte array); copyResource reads byte by byte.；unzip has logging and assertions; copyResource does not.
- 修正建议: Enhance training data with diverse I/O patterns (e.g., copy, unzip, download).；Use dataflow analysis to detect common read-write cycles.；Design contrastive objectives that align functions with shared subfunctionalities like stream copying.

### case_id=2415 FN long_range_semantics

- 方法: `modifyApplicationMessage` vs `readAndRewrite`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Modifies a localized properties file by replacing a message value for a given key or appending it.
- B 摘要: Reads a DICOM image file, parses it, reads pixel data, and writes the processed image to another file.
- 静态失败原因: Static BERT/GraphCodeBERT focused on token-level similarity and API usage, which are completely different. It likely failed to capture the high-level algorithmic pattern of read-modify-write due to lack of abstract reasoning. The low token Jaccard (0.05) contributed to its decision.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: None
- 共享行为: Both implement a read-process-write pipeline on a file.；Both parse the input file, modify it based on some parameters, and write output to another file.
- 行为差异: Different file formats and parsing libraries (properties vs DICOM).；Different processing logic (string replacement vs pixel data manipulation).；Different error handling strategies (catch Exception vs throws IOException).
- 修正建议: Use abstract syntax tree (AST) based methods to capture structural patterns.；Incorporate program flow analysis to recognize read-modify-write pipelines.；Train on more diverse clone pairs to learn Type-4 clones with low lexical overlap.

### case_id=2416 FN partial_functionality

- 方法: `doGet` vs `byReference`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Handles HTTP GET request to retrieve and render a portal page with logging, caching, and error handling.
- B 摘要: Copies an InputStream to a temporary file and returns an ImmutableContent wrapper.
- 静态失败原因: The functions have very low token overlap and are structurally different; the shared temp file pattern is a small fragment that may be missed by static BERT models focusing on whole-function semantic embeddings.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled as clone because both functions contain a common code fragment for creating a temporary file and writing data, which could be considered a reusable pattern despite different overall purposes.
- 共享行为: Both create a temporary file using File.createTempFile and write data to it.；Both handle IOException by printing stack trace or logging.
- 行为差异: Function A is a servlet doGet with complex request/response handling; function B is a simple static utility.；A includes page visibility checks, caching, and response writing; B only copies stream to file.
- 修正建议: Incorporate local pattern or subgraph matching to detect partial clones.；Use data augmentation to train on partial functionality clones.

### case_id=2417 FN benchmark_preference_bias

- 方法: `doRawRequest` vs `readData`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Sends an HTTP POST request with provided data and returns the response body as a string.
- B 摘要: Parses comma-separated string constants to populate multiple sets and maps used for Tibetan transliteration configuration.
- 静态失败原因: Static BERT/GraphCodeBERT correctly predicted non-clone because the code structures and tokens are entirely different; it did not fail in this case.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB likely labeled them as clones due to over-broad criteria, possibly considering both as 'data reading/processing' functions, but this ignores the fundamentally different operations and I/O behavior.
- 行为差异: doRawRequest performs network I/O and returns a string; readData performs local string parsing and populates global data structures.；doRawRequest writes to an OutputStream and reads from an InputStream; readData uses StringTokenizer to iterate through tokens.；doRawRequest is a simple HTTP client method; readData is a complex initialization method with many cases and error handling.；doRawRequest has no side effects on static state; readData modifies many static collections and maps.
- 修正建议: Review BCB annotation for this pair to correct the label to non-clone.；If the model is considered to have failed, it did not; the ground truth is likely incorrect.

### case_id=2418 FP boilerplate_overlap

- 方法: `readData` vs `unzip`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Reads configuration data from a file and populates hash sets and maps for Tibetan transliteration.
- B 摘要: Unzips a ZIP file to a target directory, extracting all entries.
- 静态失败原因: High lexical overlap in common Java API elements (File, IOException, try-catch) and similar control structures (loops, conditionals) misled the model into false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would likely label as non-clone because the functionalities are completely different; the only commonality is basic I/O and exception handling, which is not sufficient for Type-3/4 similarity.
- 共享行为: Both perform file I/O operations and handle exceptions
- 行为差异: Function A parses structured configuration data and builds in-memory lookup structures; Function B extracts files from a zip archive and writes them to disk；Function A uses HashSet and HashMap for storing parsed tokens; Function B uses ZipInputStream and FileOutputStream for binary stream copying；Function A has complex column parsing logic; Function B has simple entry iteration and file creation
- 修正建议: Improve model's ability to differentiate between boilerplate and core functionality；Incorporate deeper semantic understanding, e.g., via data flow or program dependence graphs；Train on more diverse negative samples with high syntactic but low semantic similarity

### case_id=2419 FP boilerplate_overlap

- 方法: `sendPost` vs `createHTML`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Sends an HTTP POST request to a given URL with parameters and returns the response body as a string.
- B 摘要: Generates an HTML string by reading a CSS resource and constructing content based on a page type enumeration.
- 静态失败原因: The model likely over-emphasized shared structural patterns (BufferedReader, while loop, string concatenation) and overlooked the divergent API usage (HttpURLConnection vs. ClassLoader) and the extensive HTML-specific logic in function B. The long code of B may have caused the model to focus on local commonalities rather than global semantics.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels this as non-clone because the functions have completely different purposes (network communication vs. HTML generation) despite some boilerplate I/O patterns. BCB prioritizes semantic equivalence over structural similarity.
- 共享行为: Both use BufferedReader to read input line by line and accumulate lines into a result string.；Both handle exceptions with try-catch blocks.；Both return a String result.
- 行为差异: Function A performs network I/O via HttpURLConnection; Function B reads a local resource via ClassLoader.；Function A uses PrintWriter to send data; Function B does not send any data.；Function B has a switch statement to handle different page types and includes complex HTML generation logic; Function A has no such branching.；Function A's result is raw HTTP response; Function B's result is a crafted HTML document.
- 修正建议: Improve the model's ability to distinguish different I/O domains (network vs. file/resource).；Incorporate more training examples with diverse API usage to reduce bias towards generic patterns.；Use methods that capture long-range semantic dependencies and whole-function context, such as graph-based representations that include API call sequences.

### case_id=2420 FP boilerplate_overlap

- 方法: `readUNI` vs `getFullScreenUrl`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a tab-separated file from a URL and stores concatenated id and description into a vector.
- B 摘要: Fetches a YouTube page, extracts the fullscreen URL by parsing query parameters, and returns it.
- 静态失败原因: Static BERT/GraphCodeBERT likely overemphasized the shared URL-reading boilerplate (URL creation, stream opening, line-by-line reading, exception handling) while ignoring the high-level semantic difference in data extraction and output. The model may also be insensitive to the method name and context.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB annotators focus on functional equivalence. Both methods are too different in purpose (generic file reader vs. specific YouTube URL extractor) and output. The low token overlap and distinct method names reinforce a non-clone label.
- 共享行为: Open a URL for reading；Read input line by line；Parse/extract data from each line；Handle I/O exceptions
- 行为差异: A reads tab-separated fields; B searches for a line containing 'fullscreenUrl'；A fills a passed vector; B returns a constructed URL string；A uses Scanner; B uses BufferedReader and InputStreamReader；A silently catches MalformedURLException; B prints error messages
- 修正建议: Include method name or surrounding class context as a feature；Incorporate data flow analysis to track how input is transformed to output；Train on more diverse examples to distinguish generic I/O patterns from domain-specific extraction；Use AST-based or control-flow features to capture the distinct parsing logic

### case_id=2421 FP partial_functionality

- 方法: `readUNI` vs `readURL`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `1.0`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a URL source, parses tab-separated lines to extract id and description, and adds them to a vector.
- B 摘要: Reads a URL and prints each line to standard output.
- 静态失败原因: Static model over-relied on lexical overlap (URL, InputStream, loop structure) and common boilerplate, missing the different semantic purposes of the loop bodies.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB annotators likely considered the distinct data processing (parsing vs printing) as non-clone even though both read from a URL.
- 共享行为: Both open an InputStream from a URL；Both read lines in a loop；Both close streams in finally block
- 行为差异: Function A parses tab-separated fields and stores in a Vector; Function B prints lines to console；Function A uses Scanner with delimiter; Function B uses BufferedReader；Function A ignores the first line (header); Function B does not；Function A only adds id+desc to vector; Function B prints every line
- 修正建议: Incorporate dataflow or control flow analysis to differentiate output destinations；Train on more diverse examples where boilerplate is shared but intent differs

### case_id=2422 FP lexical_or_api_overlap

- 方法: `getUser` vs `CheckUrl`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Loads or creates a User from a config file based on login string.
- B 摘要: Fetches the first line of an HTTP response from a given URL.
- 静态失败原因: Model likely overemphasized token overlap (Jaccard 0.25) and similar API usage (URL, BufferedReader) while missing high-level semantic differences.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because core functionality is entirely different (user management vs. HTTP fetch) despite shared I/O boilerplate.
- 共享行为: Both use URL, BufferedReader, InputStreamReader for I/O；Both have try-catch for exceptions
- 行为差异: Function A reads from a local file; Function B reads from HTTP connection；Function A parses lines and creates User object; Function B returns raw first line；Function A loops through lines; Function B reads only one line
- 修正建议: Incorporate dataflow analysis to distinguish local vs. network resource access；Use function-call context or method-level embeddings capturing domain semantics；Add attention to method names and overall control flow

### case_id=2423 FP boilerplate_overlap

- 方法: `readRemoteFile` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a remote file from a given URL and returns its entire content as a single concatenated string.
- B 摘要: Performs a Google image search, parses the HTML response to extract image URLs, and updates a UI album art component.
- 静态失败原因: The static model likely focused on the shared structural pattern of URL opening and BufferedReader usage, discounting the significant differences in purpose, return type, and output behavior.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BigCloneBench typically requires functions to implement the same functionality to be considered clones. These functions have different purposes and outputs, so BCB would label them as non-clones (Type-0 or Type-1).
- 共享行为: Both create a URL object and open an InputStream via URL.openStream() or HttpURLConnection.；Both use BufferedReader to read lines from the input stream and concatenate them into a string.；Both handle exceptions (though differently).
- 行为差异: Function A returns a string; Function B is void and updates UI components.；Function A reads a single remote file; Function B constructs a query URL for Google image search.；Function B parses HTML to extract image URLs and populates a list; Function A does no parsing.；Different URL construction: A uses a static URL, B builds a query string with search terms.
- 修正建议: Incorporate features capturing the overall goal (e.g., return type, method name semantics).；Use dataflow analysis to distinguish between functions that produce different outputs or side effects.；Leverage call graph context to see how the function is used.

### case_id=2424 FP boilerplate_overlap

- 方法: `importSequences` vs `lookupFutureEvents`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Imports FASTA-like sequences from a URL and stores names and sequences in lists.
- B 摘要: Fetches events from a Meetup API, parses JSON response, and returns a list of Event objects.
- 静态失败原因: Static BERT based on token overlap was misled by the shared I/O boilerplate tokens (URL, BufferedReader, InputStreamReader, IOException) and the similar try-catch structure. It failed to recognize the completely different data parsing logic and return types.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this non-clone because the functions have entirely different domain purposes (genomic sequence import vs. event lookup), despite sharing a common I/O pattern. The trivial token-level overlap from boilerplate does not imply semantic similarity.
- 共享行为: Both open a URL and read input using BufferedReader/InputStreamReader.；Both handle IOException with printStackTrace or custom exception.；Both use similar loop structure to read until end of input.
- 行为差异: Method A parses a FASTA-like format (lines starting with '>'), while method B parses JSON.；Method A stores data in class fields; method B returns a List<Event>.；Method A uses a custom ImportHelper class; method B uses JSONValue and JSONObject from external library.；Method A handles EOFException; method B does not.
- 修正建议: Introduce data-flow features to capture how input is processed and what output is produced.；Use AST-based or graph-based representations to differentiate syntactic structures.；Apply domain-specific or API usage patterns to distinguish general I/O from specialized logic.

### case_id=2425 FP boilerplate_overlap

- 方法: `issueCommandToServer` vs `checkForUpgrade`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Sends a command and change capsule to a server via HTTP POST and returns the response.
- B 摘要: Checks for software upgrades by querying a remote license server, updating a local database, and updating UI components.
- 静态失败原因: The static model may have overemphasized the common API usage (URLConnection, BufferedReader) and missed the drastically different structure and intent, leading to a false positive despite low token overlap.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels as non-clone because the functions have entirely different purposes, control flow, and system interactions; they are not semantically equivalent nor share partial functionality beyond basic HTTP boilerplate.
- 共享行为: Both make HTTP requests using URLConnection；Both read response from server using BufferedReader
- 行为差异: A uses POST and writes data; B uses GET and does not write；A only communicates with server; B also performs database operations and UI updates；A returns a string; B is void and shows messages；B has complex conditional logic for parsing response; A just returns raw response
- 修正建议: Incorporate dataflow and control flow analysis to distinguish different API usage patterns；Use graph-based models that capture dependencies beyond surface syntax；Add task-level or intent understanding to differentiate between simple HTTP client calls and complex upgrade orchestration

### case_id=2426 FP partial_functionality

- 方法: `doVersionCheck` vs `executePost`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Performs a version check by reading a URL (GET) and parsing version/build strings, then displays a message to the user.
- B 摘要: Executes an HTTP POST request with given parameters and returns the response body as a string.
- 静态失败原因: Static BERT/GraphCodeBERT likely over-relied on the shared lexical tokens (URL, url, openStream, BufferedReader, while, readLine, null) and API calls (new URL, url.openStream, new BufferedReader, new InputStreamReader, while, line = rd.readLine, bin.close, catch Exception). The high token similarity (0.18 is moderate but perhaps the model misweighted overlapping API usage). Additionally, both methods have similar structure: open connection, read loop, exception handling. Static models may fail to capture the semantic difference in the HTTP method (GET vs POST), the parsing logic, and overall purpose (version check vs data retrieval). The long-range dependency of differing logic may be missed.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB typically annotates as non-clones when functions have different overall purposes (version check vs. generic POST), despite sharing low-level HTTP reading patterns. The behavioral differences are significant: one is UI-facing with specific parsing, the other is a utility function. Thus BCB labels 0 (non-clone).
- 共享行为: Both open a network connection to a URL；Read input stream using BufferedReader；Read lines and process them；Handle exceptions
- 行为差异: doVersionCheck uses GET, executePost uses POST；doVersionCheck parses specific key-value lines (.version, .build), executePost appends all lines to response；doVersionCheck interacts with UI (show/hide cursor, show messages), executePost is a pure utility method；doVersionCheck uses jEdit properties for URL, executePost takes URL and parameters as arguments
- 修正建议: Focus on high-level goal: version check vs. generic POST retrieval；Train on distinguishing GET vs POST usage；Incorporate variable naming and comments if available；Use graph-based context to capture control flow differences, especially the specific parsing vs generic line accumulation

### case_id=2427 FP boilerplate_overlap

- 方法: `importSequences` vs `doVersionCheck`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads sequences from a URL in FASTA format and stores them in lists.
- B 摘要: Checks for version updates by reading a version file from a URL.
- 静态失败原因: The static model focused on overlapping tokens like 'url.openStream()', 'BufferedReader', 'InputStreamReader', 'readLine', 'IOException', missing the distinct high-level semantics.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB considered them non-clones because the functional purpose is entirely different despite similar I/O boilerplate.
- 共享行为: Both open a URL and read text line by line.；Both handle IOException with try-catch.；Both parse lines for specific patterns.
- 行为差异: Different parsing logic: ImportHelper vs manual startsWith.；Different output: storing sequences vs calling another method.；Different exception handling: multiple catches vs single IOException.；Different method context: non-static vs static.
- 修正建议: Incorporate method name or overall purpose into representation.；Use data-flow analysis to distinguish how parsed data is used.；Improve representation to capture program logic beyond lexical tokens.

### case_id=2428 FP boilerplate_overlap

- 方法: `readData` vs `testLoadSource`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Initializes multiple character sets and parses configuration data for Tibetan transliteration.
- B 摘要: Tests loading an arXiv article metadata source and verifying its content.
- 静态失败原因: The model likely over-relied on superficial lexical overlap (common Java keywords like 'String', 'while', 'if', 'throw') and similar control flow structures, ignoring the distinct semantic purposes and different domain contexts.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB correctly labels this as non-clone because the functions have no functional similarity; one is a data initialization routine and the other is a unit test for a web service.
- 行为差异: Function A populates static data structures from tokenized strings and a configuration file; function B performs a unit test on a data access object.；Function A has side effects on global sets and maps; function B asserts and closes an input stream.；Function A handles multiple categories of character sets; function B deals with a single arXiv article.；Function A includes file I/O and parsing; function B uses IOUtils to copy stream to string.
- 修正建议: Incorporate method-level and class-level context embeddings；Use data-flow analysis to capture variable dependencies and side effects；Add a training objective that penalizes false positives on structurally similar but semantically different functions

### case_id=2429 FP boilerplate_overlap

- 方法: `sendPost` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Sends an HTTP POST request with parameters and returns the response body.
- B 摘要: Searches Google Images for the current track's artist and album, parses the HTML to extract image URLs, and adds them to a list.
- 静态失败原因: The model may have been misled by the common pattern of opening an HTTP connection and reading input, which is a frequent template. The token overlap, though low, includes keywords like URL, HttpURLConnection, BufferedReader, InputStreamReader, while loop, etc. The model overemphasized these structural similarities and ignored the differing logic and purpose.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels as non-clone because the functions are not even Type-3 (modified copy) due to significant structural and functional differences. They share only boilerplate HTTP reading code, which is common in many Java programs.
- 共享行为: Both open an HTTP connection and read the response line by line.；Both use BufferedReader and InputStreamReader.；Both catch exceptions and show error messages.
- 行为差异: A uses POST method; B uses GET.；A sends parameters via output stream; B does not send any data.；A returns the response string; B processes the response to extract URLs and stores them in a list.；B has condition on artist name change and additional string manipulation.
- 修正建议: Improve training data to better distinguish generic utility functions from task-specific ones.；Incorporate data flow or control flow features to capture functional intent.；Use context-aware models that consider method arguments, return types, and class fields.

### case_id=2430 FP boilerplate_overlap

- 方法: `callService` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a URL and stores the entire response in a field.
- B 摘要: Searches Google Images, parses image URLs, populates a list, and updates UI with an image.
- 静态失败原因: Static BERT/GraphCodeBERT may have over-emphasized the lexical overlap of the URL reading pattern (URL, BufferedReader, readLine) while ignoring the distinct post-processing and side effects.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the functions have different high-level purposes and outputs, despite sharing a common HTTP reading boilerplate.
- 共享行为: Both open a URL connection and read lines into a string using BufferedReader.
- 行为差异: Function A only reads and stores raw text; function B parses HTML for image links, updates UI, and handles multiple exceptions.；Function A returns void and sets an answer field; function B modifies a UI component and a list.；Function B adds HTTP headers (User-Agent) and casts to HttpURLConnection.
- 修正建议: Incorporate dataflow or control flow analysis to distinguish side effects.；Use larger context including return type and method name semantics.；Train on more diverse negative pairs that share boilerplate but differ in purpose.

### case_id=2431 FP boilerplate_overlap

- 方法: `getUser` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Loads a user from a DAO or parses a config file to create a user by login credentials.
- B 摘要: Performs a Google image search, parses HTML to extract image URLs, and displays an image in a GUI.
- 静态失败原因: The model likely overemphasized common boilerplate patterns (URL, BufferedReader, try-catch) and ignored the distinct functional contexts and outputs, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels clones based on functional equivalence or strong similarity. These functions serve entirely different purposes (user authentication vs. image search display), so they are non-clones even under broad Type-4 criteria.
- 共享行为: Both use URL, BufferedReader, and InputStreamReader for reading data.；Both have try-catch blocks for exception handling.；Both read input line by line and parse strings.
- 行为差异: Function A returns a User object; Function B is void and updates a GUI component.；Function A reads from a local config file; Function B accesses an external web API.；Function A parses colon-separated tokens; Function B parses HTML for image URLs.；Function A conditionally saves a new user; Function B has no persistence.
- 修正建议: Incorporate data flow analysis to trace how inputs produce outputs.；Train with more examples of non-clone pairs that share common I/O patterns but differ in domain.；Use AST-based features to capture structural differences beyond the token sequence.

### case_id=2432 FN benchmark_preference_bias

- 方法: `addDataFromURL` vs `login`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `preference_memory_with_manual_audit`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Reads data from a URL and appends it to a text buffer, handling exceptions and closing stream.
- B 摘要: Performs an HTTP login to LOLA by sending email and password, retrieves a session ID, sets it, and returns it.
- 静态失败原因: Static BERT relied on surface-level features like tokens and structure, which showed low overlap and different method names, missing the broader I/O pattern similarity that BCB acknowledged.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider these as Type-4 clones because both involve network I/O, stream reading, and exception handling, even though the specific functionalities differ.
- 共享行为: Both open a URL connection and read input using BufferedReader；Both handle exceptions with try-catch and print error messages
- 行为差异: A only reads data (GET-like) and appends to a class variable；B sends POST data and processes login response to extract session ID；B sets session and returns the ID, while A does not return anything
- 修正建议: Incorporate task-level semantics, e.g., detect I/O operations；Use data flow analysis to track URL connections；Train with BCB's annotation criteria including Type-4 clones

### case_id=2433 FN partial_functionality

- 方法: `read` vs `postRequest`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a file or URL and returns a status code.
- B 摘要: Performs an HTTP POST request with form data and returns the response string.
- 静态失败原因: The static model likely focused on low token overlap (Jaccard 0.21) and detected significant semantic differences (read vs. post, different return types, different operations). It correctly identified them as non-clones from a strict perspective, but failed to capture the lenient BCB labeling that considers partial functionality overlap.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled these as clones due to both being network I/O operations that open a URL and read input, ignoring the fact that one writes data (POST) and the other does not (GET/read). BCB often accepts broad Type-3/4 similarity based on shared functionality like 'reading from a URL'.
- 共享行为: Both open a URL connection and read from its input stream.
- 行为差异: Function A reads from a file or URL and does not write any data; Function B writes form data to the connection before reading.；Function A returns an integer status code; Function B returns the response body as a string.；Function A handles file and URL inputs; Function B only handles HTTP POST with parameters.
- 修正建议: Incorporate features that capture the type of HTTP request (GET vs POST) and the presence of data writing.；Use graph-based representations that model data flow and control dependencies to distinguish read-only from read-write operations.

### case_id=2434 FN partial_functionality

- 方法: `addDataFromURL` vs `register`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.65`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads content from a URL and appends all lines to a text buffer.
- B 摘要: Registers a new user, including making a URL call to a phpBB forum to set the forum ID.
- 静态失败原因: Low lexical overlap (Jaccard ~0.126) and different overall structure; static methods cannot capture the shared sub-pattern embedded in larger dissimilar code.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label these as clones because both contain a common pattern of opening a URL, reading lines, and handling exceptions, which is considered a Type-3/Type-4 clone for similar I/O operations.
- 共享行为: Both open a URL and read lines from it using BufferedReader；Both catch IOException during URL reading
- 行为差异: A appends all lines to a text buffer; B reads only the first line to set a forum ID；B includes validation, password encoding, database persistence, and email sending；Different exception handling: A appends URL string, B logs and throws RuntimeException
- 修正建议: Use subgraph matching or frequent subsequence mining to detect common code patterns；Combine static analysis with dynamic traces to highlight similar I/O operations

### case_id=2435 FN benchmark_preference_bias

- 方法: `doGet` vs `decodeFileToFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Handles HTTP GET requests to retrieve and serve a page, with access control and caching.
- B 摘要: Decodes a Base64-encoded file and writes the decoded content to an output file.
- 静态失败原因: The static model correctly predicted non-clone due to low token overlap and distinct method names; it did not fail in our view.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have considered both functions as performing file-like I/O operations with stream handling, but the functional contexts are entirely different.
- 共享行为: Both perform I/O operations using streams；Both handle exceptions with try-catch-finally
- 行为差异: Function A processes HTTP requests and involves page retrieval, user authorization, and logging; Function B simply decodes a file；Function A has complex caching logic and response handling; Function B is a straightforward file transformation；Function A writes to HTTP response; Function B writes to a file
- 修正建议: Review BCB annotation for this pair to ensure consistency with functional semantics

### case_id=2436 FP long_range_semantics

- 方法: `addToArchive` vs `readData`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `static_summary_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Adds a file to a zip archive using a ZipOutputStream.
- B 摘要: Reads and parses configuration data from a file into multiple sets and mappings.
- 静态失败原因: The model likely got confused by the length of readData, losing track of overall semantics, and may have overfit to common tokens like 'HashSet' or 'IOException' appearing in both, despite the token Jaccard being very low.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB annotators consider these non-clones because they perform completely different tasks with no code reuse, structural similarity, or overlapping functionality, even under relaxed Type-4 criteria.
- 共享行为: Both involve I/O operations (reading/writing data)
- 行为差异: addToArchive writes a single entry to a zip archive; readData reads and parses a large configuration file into multiple data structures；addToArchive is simple and linear; readData is complex with multiple parsing stages and error handling；addToArchive returns a URL; readData is void and populates global sets
- 修正建议: Use graph-based models capturing data and control flow；Apply code summarization to capture global purpose；Incorporate function-level similarity based on API calls and data transformation patterns

### case_id=2437 FN lexical_or_api_overlap

- 方法: `getFile` vs `clonarFichero`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies the soap:address endpoint in the XML, and returns the local file path.
- B 摘要: Copies a file from a FileInputStream to a destination path using NIO channels, returning success status.
- 静态失败原因: Static BERT models rely heavily on token overlap and structural similarity; the low Jaccard similarity (0.119) and different surrounding code (logging vs print, different exception handling, XML processing) caused the model to miss the underlying channel transfer pattern.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may consider them clones because both involve transferring bytes from a source to a destination using java.nio.channels, a common pattern. The core file transfer logic is similar, and BCB's type-4 annotations often accept partial functionality overlap.
- 共享行为: Both use FileChannel to transfer data between an input stream and an output stream.；Both handle IO exceptions.
- 行为差异: Function A performs XML modification after download, while B only copies bytes.；Function A involves network I/O (URL open), B is purely local file copy.；Function A returns a file path string, B returns a boolean.；Function A uses logging and handles multiple exception types, B uses print statements and handles only IOException.
- 修正建议: Enhance model with dataflow analysis to capture core I/O operations.；Augment training data with low-token-overlap clones that share control flow patterns.；Use graph-based representations focusing on channel operations.

### case_id=2438 FN benchmark_preference_bias

- 方法: `fetchUrl` vs `register`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.6`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Fetches a URL and returns its entire content as a string, ignoring errors.
- B 摘要: Registers a User object by validating, encoding password, setting properties, calling a PHP forum URL to create a forum user, reading the response to set the forum ID, persisting the user, and sending a confirmation email, returning success or failure.
- 静态失败原因: The static BERT model likely detected low lexical overlap (token Jaccard 0.17) and large structural and semantic differences, correctly predicting non-clone. It failed to align with BCB's generous labeling because it does not weigh small shared fragments heavily enough to override the dominant dissimilarities.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider these clones because both contain the common code pattern of opening a URL, wrapping in BufferedReader, and reading lines. Under a broad Type-3/Type-4 definition, sharing this I/O operation snippet might be deemed as partial functionality similarity, despite vastly different overall purposes.
- 共享行为: Both open a URL connection and read lines from it using a BufferedReader.
- 行为差异: Function A is a generic utility that returns the fetched string; Function B performs registration with multiple steps and side effects.；Function A handles only MalformedURLException and IOException silently; Function B has extensive error handling and logging.；Function A returns an empty string on error; Function B throws RuntimeException or returns false.；Function A has no input validation or transformation; Function B validates input, encodes password, sets date, adds authority, creates hash, and persists to database.
- 修正建议: Align training data with BCB's annotation guidelines that consider shared sub-patterns as clones even if overall semantics differ.；Incorporate fragment-level similarity measures (e.g., subgraph matching) into the model to capture local code reuse.；Adjust threshold for broad clone detection to match BCB's lenient standards.

### case_id=2439 FN partial_functionality

- 方法: `copyResource` vs `sendErrorMessage`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.75`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource from a URL or file to a destination file using a byte-by-byte read-write loop.
- B 摘要: Sends an error message by reading a log file, compressing it into a zip, and emailing the zip file.
- 静态失败原因: Static BERT/GraphCodeBERT likely focused on the distinct method names, exception handling, and high-level functional differences (copy vs. send error), while the similar IO loop was overshadowed by low token overlap and different API calls.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely annotated this as a clone due to the shared low-level IO pattern (read-write loop), considering it a Type-3 clone with minor structural differences despite different high-level purposes.
- 共享行为: Both read from an input stream and write to an output stream using a loop.
- 行为差异: Function A copies a generic resource; Function B sends an error email with zip compression.；Function A uses single-byte reads; Function B uses buffered reads with buffer size 8192.；Function A throws an exception if source not found; Function B catches and prints exceptions.；Function B includes zip entry management and email sending, absent in A.
- 修正建议: Incorporate functional purpose analysis beyond lexical or API overlap.；Use flow-aware models that capture the overall task (e.g., file copy vs. email sending) rather than just local code patterns.；Train with more examples of non-clone pairs that share common snippets but differ in goal.

### case_id=2440 FP boilerplate_overlap

- 方法: `main` vs `getFullScreenUrl`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a hardcoded URL and prints its entire content to console.
- B 摘要: Extracts video parameters from a YouTube page URL and constructs a download link.
- 静态失败原因: Static BERT models may over-rely on lexical and structural overlap such as the common pattern of URL openStream/BufferedReader.readline, ignoring the different control flow and purpose.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely considers these non-clones because they have different input sources, different output types, and the common reading pattern is just boilerplate; the core functionality differs significantly.
- 共享行为: Open a URL connection；Read lines from an InputStream using BufferedReader；Print some output to System.out
- 行为差异: Function A prints all lines; Function B parses specific line for 'fullscreenUrl'；Function A has no return value; Function B returns a constructed URL string；Function A uses hardcoded URL; Function B uses instance variable ytUrl；Function B sets progress bar and handles exceptions differently
- 修正建议: Use type information (return type, parameter types) as a filter；Incorporate dataflow analysis to distinguish how read lines are processed；Require matching of semantic roles beyond API sequences

### case_id=2441 FP lexical_or_api_overlap

- 方法: `get` vs `parse`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Fetches game records from a URL via HTTP GET request, reads lines, filters comments, decodes each line into a GameRecord, and returns an array.
- B 摘要: Parses a data file (from URL or local file) using a StreamTokenizer, handling headers, types, scientific notation, and returns a DataSet object.
- 静态失败原因: The static model likely focused on the common use of HttpURLConnection/URL, BufferedReader, and line-based reading, overlooking the vastly different downstream processing and overall semantics. The model may have been misled by API-level overlap.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this non-clone because the two methods have entirely different purposes and logic, even though they both involve reading input. BCB generally requires functional similarity beyond just using similar I/O patterns.
- 共享行为: Both read data from a source (URL or file) using BufferedReader；Both perform line-by-line reading
- 行为差异: Method A only reads from URL with HTTP GET; Method B supports URL and local file；Method A filters lines starting with '#'; Method B uses complex tokenization with StreamTokenizer；Method A decodes lines into GameRecord objects; Method B parses structured data into a DataSet；Method B handles headers, types, scientific notation, and multiple delimiters; Method A does not
- 修正建议: Improve model's ability to distinguish between high-level functional purpose vs. low-level API usage；Incorporate more structural or control-flow analysis to capture differences in data processing logic；Use data augmentation with negative examples that share API patterns but differ in functionality

### case_id=2442 FN partial_functionality

- 方法: `main` vs `invoke`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: A main method that constructs a hardcoded RenRen API call with specific parameters, sends it via HTTP POST, and prints the response.
- B 摘要: A generic service invocation method that constructs a URL from the method name, sends an HTTP POST with arguments, handles timeout retries, and returns deserialized result.
- 静态失败原因: The static model relied on lexical and structural similarity, which is low (0.0875 token Jaccard). It missed the underlying functional similarity due to different method signatures, library usage, and control flow.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label them as clones because the core functionality of making an HTTP POST and reading the response line by line is common, even though the context and details differ. This aligns with BCB's acceptance of Type-3/Type-4 clones with partial functionality similarity.
- 共享行为: Both perform HTTP POST requests；Both read the response using BufferedReader；Both process the response line by line
- 行为差异: A is a main method with hardcoded parameters and no retries; B is a generic method with dynamic parameters and retry logic；A prints the response; B deserializes JSON and returns it；A uses HttpURLConnection; B uses HttpClient
- 修正建议: Use functional abstraction to normalize API calls (e.g., represent HTTP POST as a common operation)；Incorporate data flow analysis to identify similar I/O patterns

### case_id=2443 FN partial_functionality

- 方法: `updateFile` vs `getFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a file to a destination path using FileChannel transferTo.
- B 摘要: Downloads a WSDL file from a URL, modifies the endpoint address in XML, and saves the result locally.
- 静态失败原因: GraphCodeBERT likely focused on low token overlap and differing method signatures, missing the abstract commonality of file channel operations.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider them clones because both involve reading/writing files and share the use of FileChannel for data transfer, despite different overall purposes.
- 共享行为: Both perform file I/O operations using FileChannel and streams
- 行为差异: updateFile copies a local file to another path; getFile downloads from a URL；getFile additionally parses and modifies XML content；getFile handles multiple exceptions and logs extensively; updateFile only throws IOException
- 修正建议: Increase training data with varied file I/O operations；Incorporate data-flow analysis to capture channel usage patterns

### case_id=2444 FN boilerplate_overlap

- 方法: `encodeFileToFile` vs `modifyApplicationMessage`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Encodes a file to Base64 and writes it to another file.
- B 摘要: Modifies a locale-specific properties file by updating or adding a key-value pair.
- 静态失败原因: Static BERT models likely rely on lexical and API overlap (e.g., FileInputStream, FileOutputStream, while loop) and ignore the distinct semantic operations inside the loop, leading to a false positive (though here it's false negative, but model predicted non-clone? Wait, prediction was 0, meaning non-clone, so model correctly said non-clone? Actually error_type is FN, so model predicted 0 but BCB label is 1. So model said non-clone, which aligns with our strict judgment. The failure is that model may have been too conservative or missed the subtle shared boilerplate? But the instruction says 'why static BERT failed' in the case study where it misclassified. Since model predicted non-clone (0) and BCB said clone (1), the model failed to recognize the clone. But we think it's not a clone, so model didn't fail? However, we must follow case: model prediction is 0, BCB label 1, so model was false negative according to BCB. But in our analysis, we think BCB label might be questionable. Nonetheless, we need to explain why static BERT might have been misled. Actually, since model predicted non-clone, it might have been too strict or missed the shared boilerplate. But given low token Jaccard, it's likely model correctly ignored similarity. So perhaps the failure is from BCB's perspective. Let's adjust: The model failed because it did not consider the broad clone definition used by BCB, which accepts partial functional similarity. However, we think BCB label may be lenient. So we can say the model failed due to not recognizing the high-level file transformation pattern.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may label this as a clone due to common file processing boilerplate (try-catch-finally, stream opening/closing) and the presence of a read-write loop, which could be considered Type-3 or Type-4 similarity under broad annotation guidelines, especially if they emphasize functional patterns like 'file transformation'.
- 共享行为: Both read from a file and write to a file；Both use try-catch-finally to handle IOExceptions and close streams；Both use a while loop to read/write data
- 行为差异: A performs Base64 encoding; B modifies properties file；A uses byte streams; B uses character streams；A copies entire file content; B conditionally copies a default file and then edits a specific key；A returns boolean success; B is void
- 修正建议: Incorporate data flow analysis to distinguish between different data transformations；Use abstract syntax tree (AST) based features to capture non-boilerplate logic；Fine-tune on BCB's specific annotation guidelines to better align with Type-3/Type-4 preferences

### case_id=2445 FP lexical_or_api_overlap

- 方法: `main` vs `uploadFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Main method that generates Java adapter classes from a Prolog file using code analysis and class generation.
- B 摘要: Uploads a file to a target path by renaming or copying bytes.
- 静态失败原因: Static BERT models may over-rely on lexical cues such as 'File', 'InputStream', 'OutputStream', and 'IOException', ignoring the overall control flow and domain-specific operations.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB expects clones to have substantial behavioral overlap. These functions have entirely different purposes and logic, so BCB labels them as non-clones.
- 共享行为: Both involve file I/O operations.；Both check file existence or handle file paths.
- 行为差异: Function A is a complex pipeline parsing Prolog, generating classes, and writing multiple files; Function B simply copies or renames one file.；A uses URLClassLoader, ClassWriter, ObjectOutputStream; B uses FileInputStream/FileOutputStream.；A has error handling with prints and returns; B throws IOException.；A performs many distinct steps (parsing, visiting, generating); B is a single-purpose utility.
- 修正建议: Incorporate structural features like AST or dataflow graphs to capture high-level intent.；Train on more diverse non-clone pairs with similar API usage but different behavior.；Use larger context windows or hierarchical models to understand method-level semantics.

### case_id=2446 FN partial_functionality

- 方法: `main` vs `setImg`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a URL and extracts its contents to the current directory.
- B 摘要: Opens a file chooser dialog, copies a selected image file to an images subdirectory, and sets it as a background image.
- 静态失败原因: Low token overlap (0.17) and different syntactic structures led the static BERT model to focus on the small common tokens (e.g., FileInputStream, FileOutputStream) and miss the broad functional similarity that BCB may use.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB might consider both as data transfer functions with similar stream processing logic (while loop reading and writing bytes) and exception handling, thus a broad Type-4 clone.
- 共享行为: Both perform file I/O operations using streams (reading from input stream and writing to output stream in a loop).
- 行为差异: A downloads from a URL, B reads from a local file.；A processes a zip archive, B copies a single file.；A is a static main method, B is an instance method with GUI interaction.；A writes multiple files from zip entries, B writes one file.
- 修正建议: Incorporate dataflow or control flow analysis to capture higher-level functional similarity.；Train with richer semantic representations that abstract away specific details like source type.；Use contrastive learning to distinguish between genuine partial clones and coincidental I/O patterns.

### case_id=2447 FN benchmark_preference_bias

- 方法: `copyResource` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Copies a resource (URL or file) to a destination file via byte stream copying.
- B 摘要: Builds a site for edit by reading XML, transforming with XSLT, and writing multiple output files.
- 静态失败原因: Static BERT/GraphCodeBERT models typically rely on token-level and structural patterns; the low token Jaccard (0.0688) and different syntactic structure correctly led to a non-clone prediction. The BCB label might be an outlier or error in the benchmark.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as a clone due to a very broad interpretation of Type-4 (semantic similarity) where both methods involve reading and writing files via streams, despite vastly different overall functionality. The I/O pattern is a weak commonality.
- 共享行为: Both read from an input stream and write to an output stream.；Both handle file I/O operations.
- 行为差异: copyResource is a simple byte copy; buildSiteForEdit performs complex XML transformation and site generation.；buildSiteForEdit has many parameters and iterates over pages; copyResource has no iteration.；buildSiteForEdit deals with DOM, XSLT, and string manipulation; copyResource does not.
- 修正建议: Re-evaluate BCB annotation for this pair; consider if I/O-only similarity is sufficient for Type-4 cloning.；Improve model calibration to handle cases where benchmark labels are inconsistent with typical definitions.

### case_id=2448 FP lexical_or_api_overlap

- 方法: `handleHandshake` vs `loadSourceCode`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Handles network handshake by validating username and performing HTTP session verification.
- B 摘要: Loads source code from a file, applies syntax highlighting, and returns HTML.
- 静态失败原因: The model likely overfitted to shared API usage patterns (URL.openStream, BufferedReader) and exception handling, ignoring the different control flow and output behavior.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clone because these functions have entirely different purposes and no meaningful semantic overlap.
- 共享行为: Both use URL.openStream() and BufferedReader to read data.；Both handle exceptions with try-catch blocks.；Both manipulate string data.
- 行为差异: handleHandshake performs network authentication and sends packets; loadSourceCode reads local files and generates HTML.；handleHandshake uses HTTP request to external server; loadSourceCode reads from classpath resource.；Different output: one modifies network state, the other returns a string.
- 修正建议: Include dataflow analysis to distinguish between input/output types.；Use methods that capture program purpose rather than just lexical tokens.；Add context-aware training that penalizes high similarity for unrelated tasks.

### case_id=2449 FP partial_functionality

- 方法: `GetResponse` vs `getFrameworkFactory`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends an HTTP GET request and concatenates the response body into a string, returning null if an exception occurs.
- B 摘要: Reads a service configuration file from the classpath and instantiates a FrameworkFactory via reflection, throwing an exception if not found.
- 静态失败原因: The static model likely relied on overlapping API usage (URL, BufferedReader, IOException) and similar control flow (try-catch, while loop) to incorrectly predict a clone, overlooking the entirely distinct semantics and data flow (one returns a string, the other returns an object via reflection).
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB labels this as non-clone because the functions have completely different purposes (HTTP client vs. service loader) despite superficial structural similarities in reading lines from a stream. BCB emphasizes high-level functional equivalence.
- 共享行为: Both use BufferedReader to read lines from an input stream.；Both have try-catch blocks for IOException.；Both use a while loop to read lines until null.
- 行为差异: Function A makes an HTTP GET request; Function B reads a local resource file.；Function A accumulates lines into a string; Function B returns an object instance.；Function A does not close the BufferedReader; Function B closes it in a finally block.；Function A handles MalformedURLException separately; Function B propagates exceptions.
- 修正建议: Incorporate deeper data-flow analysis to track how input streams are obtained and used.；Use type-based reasoning to distinguish between network I/O and local resource loading.；Add training examples that contrast similar API usage with different high-level purposes.

### case_id=2450 FP boilerplate_overlap

- 方法: `handleHandshake` vs `PageLoader`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Handles a handshake packet by validating a username and optionally making an HTTP request to a session server.
- B 摘要: Constructs a PageLoader by fetching and storing the entire content of a given URL.
- 静态失败原因: The static BERT model likely overemphasized the lexical and structural overlap of URL opening and BufferedReader usage, while missing the semantic difference in purpose and context.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically requires similar high-level functionality; these functions perform entirely different tasks despite sharing a common URL-reading pattern.
- 共享行为: Both open a URL and read from it using BufferedReader.
- 行为差异: A has complex logic with conditionals and error handling, while B is straightforward.；A sends network packets, B does not.；A reads a single line, B reads all lines.；A uses URL for authentication, B uses URL for content retrieval.
- 修正建议: Incorporate more semantic features like method names, class context, or data flow analysis.；Distinguish between constructors and regular methods.；Use control flow and call graph information to separate authentication logic from simple content fetching.

### case_id=2451 FN partial_functionality

- 方法: `copyFile` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a file from source to destination with overwrite prompt and progress indication.
- B 摘要: Retrieves a resource by name, caching it locally and returning a FileInputStream.
- 静态失败原因: Static models may have relied on lexical patterns like file handling and stream operations, missing the distinct overall purpose and low token overlap.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider them clones if focusing on file I/O and stream handling as a broad functional category, but the core functionality is different.
- 共享行为: File I/O operations；Exception handling for streams
- 行为差异: A copies a local file; B downloads from URL and caches；A prompts user for overwrite; B silently checks cache；A returns void; B returns InputStream；A uses progress indicator; B does not
- 修正建议: Incorporate control flow and data flow analysis to distinguish file copying from resource caching；Use more robust code summarization to capture high-level intent

### case_id=2452 FN benchmark_preference_bias

- 方法: `doRequest` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Serves a static resource by mapping a path alias to an internal resource and copying its content to the HTTP response.
- B 摘要: Generates an editable version of a website by transforming XML pages using XSLT and writing the output to files.
- 静态失败原因: The model correctly predicted non-clone based on low lexical overlap and distinct method signatures. Its 'failure' relative to the BCB label is due to the BCB annotation being potentially incorrect or based on broader project context not evident from the code.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled them as clones due to superficial similarities in I/O operations and stream usage, or perhaps they belong to the same project and share common boilerplate code such as debug tracing. However, the core functionality is entirely different.
- 共享行为: Both perform file I/O operations (reading from input streams and writing to output streams).；Both handle exceptions related to I/O.
- 行为差异: a serves a single resource per request, while b processes multiple pages with complex transformations.；a works in HTTP context, b works with filesystem and XML.；a returns a boolean, b is void and throws multiple exception types.
- 修正建议: Re-evaluate BCB annotation for this pair; consider if they truly represent a clone under the defined criteria.；If retaining BCB label, provide additional context or use a different similarity measure for evaluation.

### case_id=2453 FN benchmark_preference_bias

- 方法: `main` vs `convert`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a URL and extracts its ZIP entries to files.
- B 摘要: Converts an ACRNEMA medical image file to DICOM format with pixel data handling and metadata injection.
- 静态失败原因: The static model likely relied on low token Jaccard similarity (0.152) and surface structure, missing any broad functional category overlap that BCB might consider; alternatively, the model correctly identified non-clone but BCB label is noise.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as a clone due to both functions involving file reading, processing, and writing with streams, perhaps viewed as generic data transfer tasks, or due to annotation error.
- 共享行为: Both perform file I/O with stream copy operations；Both use BufferedOutputStream for writing；Both throw IOException
- 行为差异: Code_a extracts multiple files from a ZIP archive; code_b processes a single file；Code_a handles HTTP/file URL protocols; code_b parses DICOM-specific metadata；Code_b has complex pixel data inflation and tag writing; code_a only copies bytes；Code_b performs UID generation and file format detection; code_a does not
- 修正建议: Incorporate more comprehensive functional categorization in training data；Use semantic role labeling to capture high-level intent beyond token overlap；Improve handling of low token overlap by considering behavioral patterns and resource usage

### case_id=2454 FN benchmark_preference_bias

- 方法: `getFile` vs `readFixString`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies the endpoint location in the XML, and returns the local file path.
- B 摘要: Reads a fixed-length string from an input stream using a limited input stream and returns the string.
- 静态失败原因: Static BERT correctly predicted non-clone because token Jaccard is very low (0.0846) and code structures are completely different; the model did not fall into the trap of considering broad I/O similarity as clone.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as a clone due to both functions involving I/O operations, exception handling, and returning a String, possibly considering them as 'service methods' that read data from a source, despite very different actual logic.
- 共享行为: Both handle exceptions (IOException) and return a String
- 行为差异: A downloads from network, B reads from a local stream；A modifies XML, B does not；A returns file path, B returns string content；A uses channels, B uses IOUtils.copy
- 修正建议: Include data flow analysis to distinguish different I/O sources and sinks；Require matching of specific input/output transformations；Reduce acceptance of overly broad Type-4 clones in benchmark

### case_id=2455 FP boilerplate_overlap

- 方法: `writeFileType` vs `loadURL`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads URIs from a file, fetches web pages, classifies them by checking for OWL/RDFS/RDF namespaces in the first 100 lines, and writes classification results to an output file.
- B 摘要: Downloads a VRML file from a URL with basic authentication, saves it to a temporary file, and updates a status label with download progress.
- 静态失败原因: Static BERT/GraphCodeBERT may over-attend to common API tokens like 'URLConnection', 'BufferedReader', 'FileWriter', and loop patterns, ignoring the different data flow and high-level purpose.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels as non-clone because the core functionality differs: one classifies web documents, the other downloads files. The shared I/O pattern is boilerplate, not sufficient for clone detection.
- 共享行为: Open a URL connection and read lines using BufferedReader；Write output to a file using FileWriter；Handle IO exceptions with basic error printing
- 行为差异: A skips initial lines from a URI file; B does not；A reads only first 100 lines per URL; B reads entire response；A checks for specific XML namespace strings; B does not；A writes classification labels; B writes raw content to a temp file
- 修正建议: Incorporate data flow analysis to distinguish different processing logic；Use call graph or task-specific features (e.g., name embeddings of called methods)；Train with more diverse negative examples that share boilerplate but differ in semantics

### case_id=2456 FP lexical_or_api_overlap

- 方法: `CopyTo` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Copies a file to a destination using FileReader and FileWriter.
- B 摘要: Handles various UI action commands for setting paths, preferences, and restarting the application.
- 静态失败原因: A static BERT model might have been misled by the presence of common tokens like 'File', 'if', 'null', 'return', and 'catch' in both snippets, despite the overall semantics being unrelated. The model may rely on superficial lexical overlap or co-occurrence patterns from training data that associate these tokens with file operations, but fails to understand the global context and control flow.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels as non-clone because the functions have completely different purposes and structures; the only overlap is very abstract file handling, which is not sufficient for even Type-4 similarity.
- 共享行为: Both involve file handling (reading/writing files, or selecting files via chooser)；Both use try-catch or exception handling
- 行为差异: Function A is a simple file copy; Function B is a complex event handler with many conditional branches；Function A uses FileReader/FileWriter; Function B uses JFileChooser and preference storage；Function A has no UI interaction; Function B interacts with UI components；Function B is much longer and has many different operations
- 修正建议: Improve training data to include more diverse pairs with low token overlap but similar semantics (or vice versa)；Incorporate control flow and data flow analysis to distinguish simple copy from complex event handling；Use a larger context window or hierarchical modeling to capture the overall function structure

### case_id=2457 FP lexical_or_api_overlap

- 方法: `fetchUrl` vs `checkForUpgrade`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.85`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches the content of a given URL as a string, returning empty string on error.
- B 摘要: Checks for software upgrades by querying a remote server, updating a local database, and updating UI components accordingly.
- 静态失败原因: Static BERT may have been misled by the common API pattern (URL, BufferedReader, readLine) and ignored the vastly different high-level semantics and function purposes.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled as non-clone because the overall functionality is completely different; the shared IO pattern is incidental and not sufficient for clone classification.
- 共享行为: Both open a URL connection and read lines using BufferedReader
- 行为差异: fetchUrl is a simple utility with no side effects, returning a string; checkForUpgrade has complex business logic with UI, database, and exception-throwing side effects, returning void
- 修正建议: Incorporate structural features like control flow graphs or data flow analysis to capture overall intent.；Include function name and return type as indicators.；Use contrastive learning to separate utility functions from complex business logic.

### case_id=2458 FP lexical_or_api_overlap

- 方法: `compressWithZip` vs `main`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Compresses a list of files into a zip archive.
- B 摘要: Main method for an AdapterGenerator that processes a Prolog file and generates adapter code.
- 静态失败原因: The static model likely over-relied on lexical and API-level similarities (e.g., both use File, IOException, Iterator, loops) without capturing the high-level purpose difference. The token overlap, though low, may still contain common Java boilerplate that misled the model.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clone because the functions perform entirely different tasks: file compression vs. code generation. There is no semantic overlap in functionality.
- 共享行为: Both use file I/O and iteration over a collection.
- 行为差异: compressWithZip creates a zip file; main generates Java classes and resources.；compressWithZip has a simple loop; main has complex control flow with multiple branches.；compressWithZip does not parse or generate code; main parses Prolog and writes adapters.；compressWithZip uses ZipOutputStream; main uses various file and class manipulation APIs.
- 修正建议: Incorporate task-level semantic understanding via control-flow and data-flow analysis.；Use code summarization or documentation features.

### case_id=2459 FP library_context_missing

- 方法: `readTwitterFead` vs `downloadURLtoString`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.75`
- 推荐路线: `context_recovery_then_dynamic`；动态可解性: `low`；执行优先级: `medium`
- A 摘要: Reads a hardcoded Twitter feed URL using HttpClient, checks for HTTP 200, logs error on failure, and returns the response body as a string.
- B 摘要: Downloads content from a given URL using URL.openStream() and returns it as a string, throwing IOException on failure.
- 静态失败原因: The model likely overemphasized shared structural patterns (BufferedReader, while loop, StringBuilder) and missed the different HTTP client libraries and error handling approaches, leading to a false positive.
- 静态 case study: 该类错误缺少关键上下文或需要深层语义，纯静态方法不可靠。
- 动态 case study: 动态执行价值较低：样本可能依赖库、框架、网络、GUI、数据库或项目上下文，需要先恢复环境或 mock 依赖。
- BCB 偏好解释: BCB typically treats functions with different I/O strategies and error handling as non-clones, even if they achieve similar end functionality.
- 共享行为: Reads content from a URL line by line；Appends lines to a buffer (StringBuilder/StringBuffer)；Returns the accumulated string
- 行为差异: Function A uses Apache HttpClient with explicit status code checking; Function B uses java.net.URL.openStream()；Function A has a hardcoded URL; Function B takes a URL parameter；Function A catches exceptions internally and logs; Function B throws IOException；Function A has logging for non-200 status; Function B has no such handling
- 修正建议: Include features that capture the HTTP client library used (e.g., HttpClient vs URL.openStream)；Incorporate error handling patterns (logging vs throwing exceptions)；Consider parameterization of the URL (hardcoded vs passed as argument)

### case_id=2460 FN lexical_or_api_overlap

- 方法: `main` vs `copyTextFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a URL and extracts its zip entries to files.
- B 摘要: Copies a source file to a destination file with error handling.
- 静态失败原因: Static BERT models rely on token-level and AST-level features; the token Jaccard is very low (0.19) due to different API calls (ZipInputStream vs FileInputStream, URL vs File). The models fail to generalize the shared read-write loop pattern because the surrounding code and method signatures differ significantly.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB often marks Type-3 clones based on structural similarity in the I/O loop pattern, even when input sources and error handling differ. Both implement a buffered copy loop, which is a common clone pattern.
- 共享行为: Both read binary data from an input stream and write it to an output stream using a buffered byte array loop.；Both use BufferedInputStream/BufferedOutputStream for I/O.；Both close streams after writing.
- 行为差异: A uses ZipInputStream to iterate over multiple entries; B reads a single file via FileInputStream.；A writes multiple files (entry names); B writes a single destination file.；A has no error handling (throws Exception); B catches IOException and returns boolean.；A reads from a URL; B reads from a File object.
- 修正建议: Use data flow or program dependency graphs to capture the read-write loop pattern.；Augment training data with more diverse I/O clone pairs.；Consider abstracting specific API names to highlight behavioral similarities.

### case_id=2461 FN partial_functionality

- 方法: `main` vs `readAndRewrite`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a URL and extracts its entries to files using ZipInputStream.
- B 摘要: Reads a DICOM image file, parses it, and rewrites it to another file using DICOM-specific APIs.
- 静态失败原因: Static BERT models rely heavily on token/lexical similarity and API names; here the token Jaccard is low (0.118) and APIs differ completely (ZipInputStream vs ImageIO), causing the model to miss the underlying behavioral similarity of stream-based I/O operations.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely classifies these as clones because both are I/O-centric functions that read from an input, process data (though different formats), and write to an output using streaming APIs, fitting the broad Type-3/Type-4 clone definition of similar structural patterns despite different domains.
- 共享行为: Both open input streams from files or URLs.；Both process data in loops (while loops).；Both write output to file streams.；Both include print statements for logging progress.
- 行为差异: Function A downloads from URL and extracts ZIP entries; Function B reads local DICOM files.；Function A uses ZipInputStream/FileOutputStream; Function B uses ImageIO/DcmParser/DcmEncodeParam.；Function A is a main method with hardcoded URL; Function B is a private method with File parameters.；Function A has no DICOM-specific logic; Function B involves pixel data reading and writing.
- 修正建议: Enhance model with dataflow or graph-based representations to capture IO patterns.；Include input/output type information to recognize stream-based transformations.；Train on more diverse examples of broad I/O clones to reduce dependency on specific API tokens.

### case_id=2462 FP lexical_or_api_overlap

- 方法: `handleHandshake` vs `setMembers`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Handles Minecraft handshake by validating username and authenticating via session server.
- B 摘要: Parses Trac HTML to extract component and priority dropdown values.
- 静态失败原因: The model likely overemphasized lexical and API overlap (URL, BufferedReader, try-catch) while missing the distinct semantic intents (handshake vs. scraping).
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clone because the functions serve entirely different purposes (network authentication vs. web scraping) with no shared functionality beyond generic API usage.
- 共享行为: Both use URL.openStream() and BufferedReader to read from a URL
- 行为差异: A validates a handshake packet and sends login or shutdown; B parses HTML for dropdown options.；A uses authentication logic; B extracts specific HTML patterns.；A has multiple failure paths; B simply catches exceptions and prints.
- 修正建议: Incorporate dataflow or control-flow analysis to differentiate API usage contexts.；Use contrastive learning with more diverse non-clone pairs sharing superficial patterns.；Annotate functional purpose or intent to reduce reliance on lexical similarity.

### case_id=2463 FN partial_functionality

- 方法: `doTransfer` vs `retrieveQ`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Forwards an HTTP request to a specified URL, copying headers and body, then returns the response to the original client.
- B 摘要: Retrieves the content of a given URL as a string using an HTTP connection.
- 静态失败原因: Low token Jaccard (0.20354) and high lexical divergence misled the model. The model focused on method names, signatures, and control flow differences, failing to capture the semantic similarity of the core URL-fetching pattern buried in the longer code of A.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB labels it as a clone because both functions perform the core task of fetching content from a URL via HTTP, with similar underlying I/O operations (open connection, read stream). The additional proxy logic in A is treated as extra detail; the shared core functionality aligns with BCB's broad Type-3/Type-4 annotation.
- 共享行为: Open a URL connection (HttpURLConnection)；Read input stream from the connection；Handle IOException
- 行为差异: A handles both request and response (proxy), while B only reads the response；A sets request headers and forwards request body; B does not；A writes response to output stream; B returns a string；A checks response code and sends error if not OK; B returns content regardless
- 修正建议: Use data augmentation with pairs sharing core functionality but different wrappers；Incorporate data flow analysis to identify shared operations like 'open URL connection' and 'read input stream'；Train with contrastive learning on functional similarity labels；Consider a model that handles partial functionality matching

### case_id=2464 FP lexical_or_api_overlap

- 方法: `actionPerformed` vs `copyFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: ActionPerformed method handling various UI commands to set configuration preferences.
- B 摘要: Utility method to copy a file from input to output using streams.
- 静态失败原因: Static embedding models may overemphasize superficial lexical matches (e.g., 'File', 'IOException') and miss the overall semantic difference, especially with long functions where local snippets are weighted.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clones when functions have different high-level purposes despite minor lexical overlap.
- 共享行为: Both involve file handling using java.io.File
- 行为差异: Function A is a UI event handler setting preferences; function B is a file copy utility.；Function A has complex logic for multiple commands; function B is a single-purpose method.；Function A uses JFileChooser and Swing components; function B uses FileInputStream/FileOutputStream.
- 修正建议: Improve handling of long functions by focusing on control flow and data dependencies.；Incorporate structure-aware features or graph-based representations to capture semantics.；Use curriculum learning or contrastive objectives to distinguish event handling from utility functions.

### case_id=2465 FN boilerplate_overlap

- 方法: `modifyApplicationMessage` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.3`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Modifies a locale-specific properties file by updating or adding a message key-value pair.
- B 摘要: Configures and launches a Maven-based NexOpen project build, setting Hibernate dialect and processing XML profiles.
- 静态失败原因: The token Jaccard similarity is very low (0.1169), so lexical overlap is minimal. Static models like BERT rely on token-level patterns and may miss the abstract structural similarity when domain-specific vocabulary differs drastically (e.g., 'TranubeConstants' vs 'NexOpen'). The model likely focused on surface features and failed to generalize to the broader functional similarity.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may have labeled them as Type-3/Type-4 clones due to similar high-level structure: both are configuration management methods that check file existence, read input, process content, and write output. The partial functionality of 'updating configuration values' is shared, even though the specific contexts differ.
- 共享行为: Both methods work with configuration files (properties files and XML/POM files).；Both use file existence checks and file reading/writing operations.；Both utilize java.util.Properties for handling key-value pairs.；Both implement error handling with try-catch blocks and logging.
- 行为差异: Function A modifies a single properties file; Function B orchestrates an entire project build.；Function A deals with internationalization; Function B deals with Hibernate dialect and Maven profiles.；Function B involves Eclipse/IDE-specific interfaces and callbacks; Function A does not.；Function B is significantly longer and more complex with nested anonym classes.
- 修正建议: Improve representation of abstract code patterns (e.g., file I/O, configuration updates) beyond lexical tokens.；Incorporate structural AST-based features or data flow graphs to capture common control flow skeletons.；Use contrastive learning to emphasize functional intent over specific API calls.

### case_id=2466 FP lexical_or_api_overlap

- 方法: `get` vs `run`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Sends HTTP GET with location headers and returns an array of GameRecord objects parsed from non-comment lines.
- B 摘要: Reads URL content line by line, assigns first two lines to version and url, accumulates rest into info string, sets error flags, and notifies listeners.
- 静态失败原因: Static BERT models rely on lexical and structural overlap; both functions share many common tokens (BufferedReader, InputStreamReader, URL, readLine, IOException) and similar control flow, causing a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels these as non-clones because the core functionality (querying game records vs. populating a configuration) is dissimilar, despite sharing HTTP reading boilerplate.
- 共享行为: Reads from a URL via HTTP；Parses lines from input stream；Handles IOException
- 行为差异: Function A returns GameRecord[] filtered by header; B returns void and stores in instance variables.；Function A uses specific request headers; B just opens stream.；Function A filters lines starting with '#'; B uses switch on line index.；Function A prints errors; B sets error flags and notifies listeners.
- 修正建议: Incorporate dataflow or semantic role analysis to distinguish API usage patterns.；Train with hard negative examples where boilerplate is similar but semantics differ.；Use contrastive learning to emphasize output/return type differences.

### case_id=2467 FN partial_functionality

- 方法: `httpRequestByPOST` vs `readVersion`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Makes an HTTP POST request and reads the response line by line, returning the concatenated string or null on error.
- B 摘要: Reads a version file from the classpath, parses specific key-value lines to set version, revision, and date fields.
- 静态失败原因: The static model focuses on token overlap and overall structure, which are low (Jaccard 0.23) and different APIs, so it correctly identified them as non-clones under strict semantic equivalence. However, BCB's broader criteria caused a false negative (model predicted non-clone but BCB says clone).
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled them as clones due to the common sub-pattern of reading from an InputStream line by line, which is a Type-3/Type-4 partial functionality similarity.
- 共享行为: Both use BufferedReader to read line by line from an InputStream；Both handle IOException with try-catch；Both close a stream/reader (one directly, one in finally)
- 行为差异: A makes an HTTP request, B reads a local classpath resource；A returns a String, B sets object fields；A checks HTTP status code, B checks line prefixes；Error handling differs: A sets error fields, B prints stack trace
- 修正建议: Incorporate subgraph or subpattern matching to detect shared functionality；Use a hybrid model that can trade off strictness against BCB-style preferences

### case_id=2468 FP lexical_or_api_overlap

- 方法: `main` vs `copyFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Parses a Prolog file, generates adapter classes, and writes them to a JAR file.
- B 摘要: Copies a file to a destination directory using a buffer.
- 静态失败原因: Static models may be misled by lexical overlap (e.g., File, IOException, try-catch) and boilerplate code common in Java file operations, even though the functional semantics are entirely different.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the functions have completely different purposes despite sharing some low-level I/O patterns; the clone annotation tends to require similar high-level functionality.
- 共享行为: Both perform file I/O operations；Both handle exceptions related to IO
- 行为差异: Function A involves parsing, code generation, and writing multiple files; Function B only copies a single file；Function A is a main method with complex generation logic; Function B is a simple utility method；Function A produces output artifacts (JAR, serialized data); Function B only copies the input file unchanged；Error handling differs: Function A prints messages and returns; Function B prints to stderr and catches IOException
- 修正建议: Improve model to focus on high-level functional semantics rather than API usage patterns；Incorporate syntactic or structural matching to distinguish domain-specific logic from boilerplate；Use dataflow or call-graph information to differentiate simple file copy from complex generation pipeline

### case_id=2469 FP lexical_or_api_overlap

- 方法: `readURL` vs `checkForUpgrade`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a URL and prints its content line by line to standard output.
- B 摘要: Checks for software upgrades by querying a remote server, parsing license data, and updating database/UI accordingly.
- 静态失败原因: The model likely overfitted on common Java API sequences (e.g., URL.openStream, BufferedReader) and ignored the distinct control flow, method names, and domain-specific logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels these as non-clones because the overall functionality is completely different—one is a trivial URL reader, the other is a complex upgrade procedure—despite minor API overlap.
- 共享行为: Both use BufferedReader to read from a URL connection.
- 行为差异: Function A prints lines to console; Function B performs database operations and UI manipulation.；Function A is simple and generic; Function B involves complex conditional logic and business rules.；Function A has no side effects beyond printing; Function B modifies database and UI state.
- 修正建议: Incorporate method name semantics via embedding or token alignment.；Use graph-based representations that capture dataflow and structural differences.；Weight API calls based on their role (core logic vs. boilerplate).

### case_id=2470 FN benchmark_preference_bias

- 方法: `getFile` vs `addRecord`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.3`
- 推荐路线: `preference_memory_with_manual_audit`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies the endpoint location in the XML, and saves it to a temporary directory.
- B 摘要: Reads an input stream, computes a message digest, writes to a temporary file, and renames it to a permanent file based on the digest.
- 静态失败原因: Static BERT/GraphCodeBERT models rely on lexical overlap and structural similarity; here token overlap is low (0.136), and control flow differs, causing the model to miss the high-level file I/O pattern that BCB considered.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider both functions as performing file writing and renaming operations, a common pattern, thus labeling them as Type-3 clones despite different data sources and processing.
- 共享行为: Create temporary files；Write data to temporary files；Rename/move files to final destination；Handle I/O exceptions
- 行为差异: Function A downloads over HTTP and parses XML; Function B computes a hash；Function A modifies XML content before saving; Function B does not；Function A returns a file path string; Function B returns a DataRecord object；Function A uses channel-based transfer; Function B uses copyLarge
- 修正建议: Improve modeling of file I/O patterns beyond token overlap；Incorporate data flow analysis to capture common file operations

### case_id=2471 FP lexical_or_api_overlap

- 方法: `lookupFutureEvents` vs `getFrameworkFactory`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches and parses event data from a Meetup API, populating a list of Event objects.
- B 摘要: Reads a service configuration file to instantiate and return a FrameworkFactory.
- 静态失败原因: The static BERT model likely over-focused on the lexical overlap (URL, BufferedReader, readLine) and boilerplate structure, ignoring the distinct domain-specific operations and output types. It may have misclassified due to surface-level API usage similarity.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled non-clone because the high-level functionality is unrelated: one is a data retrieval/parsing method, the other is a service loader. The shared I/O boilerplate does not constitute a clone under BCB guidelines.
- 共享行为: Both use URL to open a stream and read lines with BufferedReader.；Both involve parsing (JSON parsing vs. service file parsing).
- 行为差异: Function A's output is a list of Event objects from a web API; Function B returns a single FrameworkFactory instance from a local resource.；Function A handles JSON and date parsing; Function B uses reflection to instantiate a class.；Function A throws GtugsException; Function B throws generic Exception.
- 修正建议: Train with more diverse examples that include shared API usage but different semantics.；Incorporate structure-aware guidance to distinguish boilerplate from core logic.；Use data flow analysis to trace how inputs/outputs differ.

### case_id=2472 FN partial_functionality

- 方法: `setImg` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.2`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Opens a file chooser to select an image, copies it to an 'images' subdirectory, and sets the path as an ImageIcon.
- B 摘要: Reads an XML source, performs XSL transformations, and writes output files for each page in a site, handling multiple file paths and properties.
- 静态失败原因: Static BERT models rely on token matching and structural overlap; the low Jaccard (0.0898) and dissimilar vocabulary caused the model to predict non-clone, despite some shared file I/O patterns.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have considered these clones due to overlapping file I/O boilerplate, but the overall functionality is too different for a Type-4 clone.
- 共享行为: Both perform file reading and writing operations (FileInputStream, FileOutputStream, FileWriter).；Both handle file paths using system-dependent separators.；Both include exception handling and logging.
- 行为差异: setImg is a simple GUI-based image copy; buildSiteForEdit is a complex server-side site generation with XSL transformation.；setImg copies a single file; buildSiteForEdit processes multiple pages and writes multiple output files.；setImg uses JFileChooser for user interaction; buildSiteForEdit takes all parameters as arguments.；buildSiteForEdit involves DOM, FTP, and properties handling; setImg does not.
- 修正建议: Incorporate data flow and control flow graphs to capture semantic similarities beyond token overlap.；Use models that learn from execution traces or dynamic analysis to identify functional equivalence.；Enhance training data with more diverse Type-4 clones to improve recognition of partial functionality similarity.

### case_id=2473 FP long_range_semantics

- 方法: `perform` vs `getSystemStateHash`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `static_summary_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: A web action handler that processes a classification request by setting concept properties, building XML, sending it to a remote URL, parsing the result, and storing it in the session.
- B 摘要: A utility that computes a SHA1 hash from a combination of system runtime metrics, stack traces, system properties, and network information to produce a unique system state hash.
- 静态失败原因: The static model likely relied on surface-level features such as similar method length, use of common Java keywords (try, catch, byte, new), and API mentions (Runtime, System), failing to capture the vast semantic gap between a web controller and a hash utility. The truncation of code_a may have further confused the model.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB typically labels non-clones when functions have completely different purposes and minimal code overlap; here, one is a web request handler and the other is a system hash generator – no functional similarity.
- 共享行为: Both use try-catch blocks for exception handling；Both call methods on Java core classes (e.g., Runtime, System, InetAddress)
- 行为差异: A handles HTTP requests and web session management, while B is a stateless hash computation；A involves XML parsing, URL connections, and framework-specific objects (ActionMapping, ActionForm), B uses only standard Java libraries；A has complex conditional logic and multiple failure paths, B is a straightforward sequential computation；A modifies session attributes and forwards to different views, B returns a byte array
- 修正建议: Enhance model with dataflow analysis to distinguish between HTTP-request-driven flows and static computation flows；Use structured code summarization to capture high-level intent before comparison；Improve handling of truncated code by marking incomplete functions or using whole-method parsing；Incorporate type and method-call context to differentiate framework-specific vs. generic utility code

### case_id=2474 FP lexical_or_api_overlap

- 方法: `getUser` vs `importSequences`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Loads a user from DAO or parses a config file to create and save a user based on login.
- B 摘要: Imports DNA/protein sequences from a URL and stores names and sequences in lists.
- 静态失败原因: High lexical overlap (InputStream, BufferedReader, StringTokenizer, printStackTrace) and similar loop structures caused the model to overestimate similarity, ignoring the distinct overall logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels clones as functionally similar. These functions have entirely different purposes (user management vs. sequence parsing), so they are not considered clones even under broad Type-4.
- 共享行为: Reads from an input stream；Uses StringTokenizer to parse delimited tokens；Handles exceptions with printStackTrace；Uses try-catch blocks
- 行为差异: Different domains: user authentication vs. biological sequence import；Different outputs: returns a User object vs. populates class-level lists；Different file formats: colon-separated users.cfg vs. FASTA-like sequence format；Different control flow: matching a specific login vs. reading multiple sequences until '>'
- 修正建议: Improve model to focus on high-level intent by analysing method names and return types.；Incorporate data flow analysis to differentiate control and data transformations.；Train on more diverse non-clone pairs with partial API overlap.

### case_id=2475 FN partial_functionality

- 方法: `copyFile` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a local file to another local file using NIO FileChannel transfer.
- B 摘要: Downloads a KMZ file from a URL, decompresses ZIP entries, and writes them to files.
- 静态失败原因: Low lexical overlap (Jaccard 0.1447) and different API calls make it hard for static BERT models to capture any underlying I/O commonality.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled it as clone due to broad file I/O similarity, but the functions have fundamentally different semantics and low structural overlap.
- 共享行为: Both perform file I/O operations with input and output streams/channels.
- 行为差异: Source is local file vs URL；Destination is single file vs multiple extracted files；Data is directly transferred vs decompressed from ZIP；Uses channel transfer vs stream read/write loop
- 修正建议: Incorporate dataflow analysis to recognize I/O patterns across different APIs.；Use contrastive learning to distinguish different I/O scenarios.

### case_id=2476 FN benchmark_preference_bias

- 方法: `doGet` vs `copyFiles`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Processes HTTP GET requests to display a web page, handling page retrieval, caching, logging, and security checks.
- B 摘要: Recursively copies files or directories from a source path to a destination path using file channels.
- 静态失败原因: The static BERT model correctly predicted non-clone (0) because the token Jaccard similarity is only 0.06, and the functions have no meaningful semantic overlap beyond trivial file I/O statements. The model was not misled by any substantial lexical or structural similarity.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as a clone due to superficial overlap in file I/O operations (both write to a file), but the overall functionality and context are entirely different, making this likely a false positive in BCB.
- 共享行为: Both involve file I/O operations (A writes to a temp file; B copies files).
- 行为差异: A is a web request handler with complex logic for page rendering, user permissions, caching, and logging.；B is a simple file copy utility with no web or user interaction.；A uses HttpServletRequest/Response and servlet context; B uses File and FileChannel.；A has error handling specific to missing pages and forbidden access; B propagates exceptions.
- 修正建议: Re-evaluate the BCB annotation for this pair to confirm if it truly meets clone criteria.；If BCB label is correct, consider that the model may need to capture deeper functional analogies, but here it is unlikely.

### case_id=2477 FP boilerplate_overlap

- 方法: `main` vs `convert`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Generates adapter classes for Prolog-to-Java integration from a Prolog file.
- B 摘要: Converts an ACRNEMA image file to DICOM format with validation.
- 静态失败原因: The model likely latched onto common structural patterns (exception handling, conditional returns, file reading) and length, ignoring the distinct domain-specific logic, leading to a false positive despite low token overlap.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically annotates clones only when there is significant functional overlap; these two functions serve entirely different purposes and share only generic boilerplate patterns, so they would be marked non-clone.
- 共享行为: Both perform file I/O (read/write)；Both print messages to stdout；Both use try-catch for exception handling；Both have conditional early returns based on error checks
- 行为差异: Function A is a code generator; Function B is a format converter；Different domain: Prolog vs medical imaging；Different libraries and APIs used；Different output: JAR file vs DICOM file
- 修正建议: Incorporate more training examples with similar boilerplate but different semantics；Improve model's ability to distinguish core logic from supporting scaffolding；Use data flow or control flow graphs to capture functional differences

### case_id=2478 FP long_range_semantics

- 方法: `perform` vs `SHA1`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `static_summary_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: A Struts action that classifies a concept by sending an HTTP POST request with XML data and parsing the result.
- B 摘要: A utility function that computes the SHA-1 hash of a given string and returns it in hexadecimal format.
- 静态失败原因: The static model likely missed the long-range semantic structure of function A and was misled by superficial similarities such as common method names or library usage, or the model suffered from attention dilution over the long code sequence.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BigCloneBench typically requires significant functional overlap; these functions have no common purpose, so BCB correctly labels them as non-clones.
- 行为差异: Different functionality: web request handling vs. cryptographic hashing.；Different I/O: interacts with session, request, response objects vs. takes a string and returns a string.；Different complexity: long multi-step process with external calls vs. single algorithm invocation.
- 修正建议: Use structure-aware models that capture control flow and data dependencies.；Incorporate negative sampling with functionally dissimilar pairs.；Apply contrastive learning to distinguish different operational intents.

### case_id=2479 FN lexical_or_api_overlap

- 方法: `invoke` vs `postXml`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Invokes a service method via HTTP POST with JSON serialization, response parsing, and retry on timeout.
- B 摘要: Posts XML to a URL with SOAP headers and returns the raw response string.
- 静态失败原因: Low lexical overlap (Jaccard 0.17) due to different API calls (HttpPost vs URLConnection, HttpClientUtils vs openConnection) and variable names, causing the model to focus on surface-level differences rather than the shared high-level behavior.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely annotated as clone because both functions implement the core functionality of performing an HTTP POST to send data and receive a response, viewing differences in libraries, serialization, and error handling as implementation details.
- 共享行为: Both perform HTTP POST requests；Both set a request body and read the response；Both use BufferedReader to read lines
- 行为差异: Different HTTP libraries (Apache HttpClient vs URLConnection)；Different input types (MethodInvocation vs xml string)；Different output handling (JSON deserialization vs raw string)；Error handling: status code check and retry vs IOException only
- 修正建议: Normalize API calls to abstract operations (e.g., 'send_http_post')；Use control flow graphs or data flow analysis；Train with contrastive learning on functionally similar pairs

### case_id=2480 FN partial_functionality

- 方法: `fileDownload` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a file from a given URL and writes it to a specified directory as 'download.pdf'.
- B 摘要: Fetches a web page from a hardcoded URL and prints its content line by line to the console.
- 静态失败原因: Static models rely heavily on token overlap (Jaccard 0.246) and method signatures, which differ significantly (fileDownload vs main, different parameters). The semantic similarity in core HTTP reading logic is not captured by surface tokens.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often marks pairs as clones if they share the same high-level operation (HTTP download) using common API patterns (URL, BufferedReader, reading loop), even if output differs (file vs console). The underlying functionality of reading web content is similar.
- 共享行为: Both create a URL object and open a connection to it.；Both read input from the URL's input stream in a loop until EOF.；Both use BufferedReader/InputStreamReader for reading.；Both close the input stream after processing.
- 行为差异: Function A writes data to a file; function B prints data to console.；Function A reads byte-by-byte (in.read()); function B reads line-by-line (readLine()).；Function A has a fixed output filename; function B has no file output.；Function A handles exceptions internally; function B throws IOException.
- 修正建议: Incorporate graph-based or dataflow representations to capture the common pattern of reading an HTTP input stream.；Enhance training data with pairs that have low token overlap but similar core functionality (e.g., file download vs console download).；Use contrastive learning to align embeddings of functionally similar code snippets.

### case_id=2481 FP other

- 方法: `readAndRewrite` vs `readData`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Reads a DICOM file and rewrites it to another file using DICOM libraries.
- B 摘要: Parses a configuration file to populate sets and maps for Tibetan transliteration.
- 静态失败原因: The static model may have been misled by the superficial similarity of method names ('read' prefix) and the presence of file I/O and exception handling, ignoring the vast difference in domain-specific logic.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB annotators likely considered these non-clones because they have completely different functionality and API usage, despite both involving file reading.
- 行为差异: Function A performs DICOM image I/O and pixel data manipulation; Function B parses a text file to build character sets and lookup tables.；Function A uses DICOM-specific classes (ImageInputStream, DcmParser, etc.); Function B uses StringTokenizer and custom data structures.；Function A writes output to a file; Function B only reads input and stores data in memory.
- 修正建议: Incorporate AST-based structural features to capture API and control flow differences.；Use type or domain-aware embedding to distinguish between different application domains.；Increase training data diversity to reduce overgeneralization based on common keywords.

### case_id=2482 FN partial_functionality

- 方法: `copyFile` vs `copyResource`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.95`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a file to another file using buffered I/O.
- B 摘要: Copies a resource (URL or file) to a destination file using unbuffered I/O.
- 静态失败原因: Static BERT/GraphCodeBERT likely relied on token-level overlap (Jaccard 0.27) and structural patterns, but the differing source acquisition logic (URL vs File) and error types caused it to miss the higher-level semantic similarity of stream copying.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels as clones functions that perform the same high-level operation (e.g., copying a file) even if the source input types and error handling differ, as they share the core stream-copy loop structure.
- 共享行为: Both read from an input stream and write to an output stream.；Both use a loop to transfer bytes.；Both close streams after copying.；Both throw exceptions on I/O errors.
- 行为差异: Source type: A uses File directly; B supports URL or file path string.；Buffer size: A uses 1024-byte buffer; B reads one byte at a time.；Error handling: A throws IOException; B throws Exception.；Destination determination: A takes File parameter; B calls a method destinationFile().
- 修正建议: Enhance model to recognize common I/O patterns independent of source type.；Incorporate dataflow analysis to track the stream operations.；Use contrastive learning on similar I/O utility functions.；Add features for identifying 'copy' semantics across different APIs.

### case_id=2483 FN partial_functionality

- 方法: `main` vs `unzip`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a fixed URL and extracts all entries to the current directory, printing each entry name.
- B 摘要: Extracts a local zip file into a dedicated subdirectory, handling directory entries and creating necessary folders.
- 静态失败原因: Static BERT/GraphCodeBERT models may have focused on the low token overlap (0.29) and the surface-level differences (different method names, URL vs File, additional conditional logic in B), failing to abstract the common zip extraction pattern. The dataflow of reading from a stream and writing to files is not well captured by static attention.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely labeled these as clones because the core extraction algorithm (while loop with getNextEntry, buffer read/write) is nearly identical, and the differences in source/target and directory handling are considered secondary or Type-4 partial functionality similarity.
- 共享行为: Both use ZipInputStream to iterate over zip entries；Both read entry data in a buffer and write to a FileOutputStream wrapped in BufferedOutputStream；Both handle the extraction loop with similar byte array and buffer size
- 行为差异: Input source: A uses a hardcoded HTTP URL; B uses a local File parameter；Output directory: A extracts directly to current directory; B creates a subdirectory named after the zip file；Directory handling: A ignores directory entries; B explicitly creates directories for directory entries and ensures parent directories exist；First entry special case: B has special logic for the first entry to set up the subdirectory; A does not
- 修正建议: Enhance models with dataflow analysis to identify common read-write patterns；Use AST or control flow graph matching to detect the core iteration and I/O structure；Train on more tasks that require abstracting away input/output specifics and directory handling variations

### case_id=2484 FP lexical_or_api_overlap

- 方法: `readData` vs `main`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Parses multiple comma-separated string variables to populate sets and maps, and reads a file line by line to build a hash table for character mapping.
- B 摘要: Command-line tool that parses arguments, detects format, and converts an input file to output with specified encoding using an HtmlEntityDecoderReader.
- 静态失败原因: Static BERT models may focus on overlapping token patterns (e.g., 'FileReader', 'BufferedReader', 'try', 'while') and miss the high-level purpose difference. The truncated code A contains file reading lines similar to code B's main loop.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels non-clones when functions have completely different overall functionality despite some shared low-level API calls. Token Jaccard is very low (0.1155), indicating little lexical overlap.
- 共享行为: Both involve file I/O (reading a file)；Both use try-catch for exception handling；Both use loops to process data
- 行为差异: Function A populates internal data structures (sets, maps) from static strings and a file; Function B performs file format conversion；Function A is about initialization; Function B is about processing user-provided input/output files；Function A uses StringTokenizer; Function B uses command-line parser and Readers/Writers
- 修正建议: Incorporate data flow analysis to distinguish initialization from transformation；Use structure-aware models that capture method-level semantics rather than token-level；Add contrastive learning on pairs with high API overlap but different purposes

### case_id=2485 FN partial_functionality

- 方法: `copyResource` vs `updateFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource (URL or file) to a destination file using byte-by-byte stream read/write.
- B 摘要: Copies a file to a new location after modifying its path, using FileChannel transferTo and ensuring parent directories exist.
- 静态失败原因: The low token Jaccard similarity (0.21) and different API usage (InputStream vs FileChannel) likely caused the static BERT model to focus on surface-level features, missing the semantic equivalence of file copying. The model may not capture that different I/O methods achieve the same effect.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB typically labels pairs with partial functionality similarity as clones, especially for broad Type-3/Type-4 clones. Both functions perform file copying, which is a common core behavior, so BCB would consider them clones despite differences in source type and copy implementation.
- 共享行为: Both functions copy file content from a source to a destination file.；Both involve reading from an input source and writing to an output file.；Both handle closing of I/O resources.
- 行为差异: Function A supports URL sources; Function B only supports file sources.；Function A uses InputStream/OutputStream and byte-by-byte copying; Function B uses FileChannel.transferTo for efficient copying.；Function B creates parent directories if the destination does not exist; Function A assumes the destination file's parent exists.
- 修正建议: Train on more diverse I/O operation examples to learn equivalence of different copy implementations.；Incorporate structure-aware features like data flow to capture the overall intent of copying content.

### case_id=2486 FN benchmark_preference_bias

- 方法: `persist` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Persists a FreeFormConfigurable object to a file by copying its input stream to an output stream.
- B 摘要: Retrieves a remote resource as an InputStream, caching it locally from a URL with conditional fetching.
- 静态失败原因: Static BERT/GraphCodeBERT correctly predicted non-clone (0) because the functions have very different structure and semantics; it did not fail but disagreed with an erroneous BCB label.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB likely mislabeled this pair as a clone due to superficial stream-copying resemblance, overlooking fundamental semantic differences.
- 共享行为: Both perform file I/O operations involving input and output streams.
- 行为差异: Function A writes to a file; Function B reads from a resource (remote or cached).；Function A uses a provided relative path and configurable; Function B resolves URLs and caches.；Function A has no caching logic; Function B has extensive caching and HTTP handling.；Function A returns void; Function B returns an InputStream.
- 修正建议: Re-evaluate BCB annotations for this pair to correct the label.；Focus static models on deeper semantic understanding beyond token overlap.

### case_id=2487 FP boilerplate_overlap

- 方法: `unzipModel` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Unzips a zip file from a given filename to a temporary directory, throwing an EDITSException on failure.
- B 摘要: Handles multiple GUI action commands (e.g., GRAPHVIZ, IMAGEMAGICK) to open file choosers and save preferences, and performs UI updates.
- 静态失败原因: The model may have been misled by common structural patterns (try-catch, variable declarations, loops) or token co-occurrences (e.g., 'filename', 'File', 'IOException') without capturing the distinct semantic intents.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BigCloneBench labels these as non-clones because they perform completely different high-level functions (file extraction vs. UI event handling) with no semantic overlap, despite some shared boilerplate.
- 共享行为: Both use try-catch for exception handling；Both involve file-related operations (A reads zip, B opens file choosers)
- 行为差异: A is a static utility for file extraction; B is an instance method for event handling；A has a single purpose; B handles many different commands with conditional branches；A throws a custom exception; B catches exceptions and logs or shows messages；A uses ZipInputStream; B uses JFileChooser and Swing components
- 修正建议: Incorporate more robust semantic representations that distinguish utility functions from GUI controllers；Use graph-based models that capture control flow and data dependencies beyond simple token sequences；Add negative samples with similar boilerplate but different semantics during training

### case_id=2488 FN benchmark_preference_bias

- 方法: `fileDownload` vs `lookupFutureEvents`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a file from a given URL to a local directory by reading raw bytes and writing to a file.
- B 摘要: Fetches event data from the Meetup API via HTTP, parses JSON response, and constructs Event objects with multiple fields.
- 静态失败原因: The model correctly predicted non-clone (0) because the functions have low lexical overlap, different method names, return types, and distinct subsequent operations after reading the URL. The shared boilerplate of URL reading is a minor commonality that does not outweigh the fundamental semantic difference.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might label this positive due to the shared 'download from URL' pattern, but the overall functionality differs significantly. The low token Jaccard (0.134) suggests limited lexical similarity, so the BCB label may be an error or a very broad Type-4 interpretation.
- 共享行为: Open a URL and create a BufferedReader to read input；Read input in a loop until end of stream；Close the input stream in a finally or after the loop；Handle IOException with try-catch
- 行为差异: A writes raw bytes to a file; B parses JSON and builds objects；A uses FileOutputStream; B uses StringBuilder to accumulate JSON text；A reads byte-by-byte; B reads line-by-line；B includes extensive field mapping, date parsing, and returns a list; A is void
- 修正建议: Re-evaluate the BCB annotation for this pair to ensure consistency with clone definitions；If BCB intends to include such broad patterns, adjust model training to better capture partial functionality overlap while avoiding false positives；Consider adding a test for structural divergence after the common pattern

### case_id=2489 FN benchmark_preference_bias

- 方法: `populateResources` vs `register`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.2`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Loads template files and images from classpath resources and persists them to a data store.
- B 摘要: Registers a User object by encoding password, setting registration date, adding default authority, generating hash, creating a phpBB forum user via HTTP, persisting the user, and sending a confirmation email.
- 静态失败原因: GraphCodeBERT likely correctly predicted non-clone because of low token overlap and no semantic similarity; the BCB label appears to be an annotation error.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may label this as clone due to superficial similarity in URL/stream reading patterns and error logging, but the core functionality is completely different.
- 共享行为: Both read from URLs using BufferedReader and InputStreamReader.；Both use logging for errors and handle exceptions.
- 行为差异: populateResources initializes static resources (templates, images) with no input; register processes a user object and returns a boolean.；populateResources saves resource objects; register persists a User entity and interacts with external forum via HTTP.；populateResources has no side effects beyond data store; register changes user state and sends email.
- 修正建议: Remove or correct the BCB annotation for this pair.；Improve clone detection benchmarks to avoid labeling pairs with no functional overlap as clones.

### case_id=2490 FP partial_functionality

- 方法: `read` vs `downloadModel`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a camera log from a URL line by line, parses each line into CameraLogRecord, adds to list, sorts by order.
- B 摘要: Downloads an RDF model from a URL by opening an HTTP connection, setting headers, reading RDF XML into a Model object, returns it.
- 静态失败原因: Static BERT/GraphCodeBERT models may have been misled by surface similarities such as both using URL.openStream(), BufferedReader/InputStream, try-catch blocks, logging statements, and similar control flow. The models may have overgeneralized the 'reading from a URL' concept as a clone, ignoring the fundamentally different data processing and output types.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely labels as non-clone because the core functionality is domain-specific and different: one is for camera log parsing, the other for RDF model download. Despite both involving URL reading, the purpose, data structures, and processing pipeline are distinct, which BCB considers insufficient for a clone.
- 共享行为: Both read data from a URL using standard Java IO/URL classes.；Both include logging or debug output.；Both handle IOException and close input streams properly.
- 行为差异: Function a parses text lines into camera log records; function b parses RDF/XML into a semantic model.；Function a accumulates records into a list and sorts them; function b returns a Model object directly.；Function a is an instance method; function b is a static method.；Function b sets HTTP headers like Accept and Accept-Language; function a does not.
- 修正建议: Incorporate method names more strongly into the representation (read vs downloadModel).；Use data flow analysis to capture the types of objects being created and methods called on them (e.g., CameraLogRecord vs Model.read).；Add attention to the return type and subsequent operations (sorting vs returning model).；Leverage documentation or comments if available to disambiguate domain-specific tasks.

### case_id=2491 FN benchmark_preference_bias

- 方法: `main` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Copies all files from a source directory to a destination directory using file channels.
- B 摘要: Transforms and writes page-based output files for a site editing process, involving XML and string manipulation.
- 静态失败原因: Static BERT likely correctly predicted non-clone due to very low token overlap (0.088) and no deep semantic similarity, but BCB label disagrees.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled these as clones due to both involving file copying/writing and similar low-level I/O patterns, overlooking the vast functional disparity.
- 共享行为: Both perform file I/O operations (reading and writing files)；Both use buffered I/O mechanisms；Both handle file paths with system file separator
- 行为差异: A is a simple directory copy; B involves complex per-page XML transformation and string replacement；A uses FileChannel for copying; B uses FileInputStream and FileWriter；A takes no parameters; B takes many configuration parameters；A is a main method; B is a regular method with heavy dependencies
- 修正建议: Refine BCB clone definition to avoid overgeneralizing file I/O operations；Incorporate task-level semantics rather than low-level patterns；Use hierarchical abstractions to capture intent

### case_id=2492 FP lexical_or_api_overlap

- 方法: `moveFile` vs `readData`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Copies a file from one location to another using a byte buffer and deletes the original file.
- B 摘要: Parses a configuration file, populating multiple sets and hash maps with tokenized data, with extensive error handling.
- 静态失败原因: The static BERT/GraphCodeBERT model likely over-emphasized the presence of file I/O operations (FileInputStream/FileOutputStream in A, and file reading in B) and the structural pattern of loops with try-catch. The low token Jaccard suggests the embedding captured some superficial similarity like 'file handling' while ignoring the distinct overall logic. Additionally, the extreme length of B may have caused the model to focus on local patterns rather than global semantics.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels these as non-clones because they have completely different functionality. Even though both involve file I/O, the purpose and outcome are entirely different. BCB typically requires significant semantic overlap for a positive label.
- 共享行为: Both functions involve file I/O operations.；Both use loops (while loop in A, many while loops in B).；Both handle exceptions (throws IOException in A, try-catch in B).
- 行为差异: A performs a simple file copy and delete; B parses a structured file and builds data structures.；A has minimal error handling; B has extensive error handling and logic.；A uses FileInputStream and FileOutputStream; B uses BufferedReader and StringTokenizer (and possibly other readers).；A is short (17 lines); B is very long (over 200 lines).
- 修正建议: Improve the model's ability to capture long-range dependencies and overall program semantics beyond local API usage.；Train on more diverse examples of file I/O functions with different purposes.；Use program slicing or decomposition to compare high-level intent rather than surface structure.

### case_id=2493 FN partial_functionality

- 方法: `getHTML` vs `scrapeForIsbns`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches the entire HTML content from a URL, optionally writes it to a file, and returns the HTML as a string.
- B 摘要: Scrapes a URL for ISBN-10 patterns, counting matches and collecting them, with retry logic on connection failures.
- 静态失败原因: The low token overlap (0.16) and different method names, return types, and specific operations caused the static model to perceive them as dissimilar, missing the abstract common pattern of downloading and line-by-line reading.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label these as clones because both are web scraping utilities that fetch a URL and process its content line-by-line, representing a similar high-level task even if specific outputs differ.
- 共享行为: Both open a URL and read its content line by line using a BufferedReader
- 行为差异: Function A returns the full HTML string; function B returns a count of regex matches and populates a collection.；Function A optionally writes HTML to a file; function B uses retry logic and pattern matching.；Function A sets a User-Agent header; function B does not.；Function A uses HttpURLConnection; function B uses URL.openStream().
- 修正建议: Train models on code property graphs or ASTs to capture structural similarities beyond token sequences.；Use contrastive learning with functional equivalence examples.；Incorporate data flow analysis to recognize common patterns like URL reading loops.

### case_id=2494 FP lexical_or_api_overlap

- 方法: `encodePassword` vs `perform`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Encodes a password using SHA-1 and base64 encoding.
- B 摘要: Processes a web form request, validates session, and performs classification logic involving XML and HTTP connections.
- 静态失败原因: The static BERT model likely over-generalized from trivial lexical overlaps (e.g., 'getBytes', 'MessageDigest') or was misled by the presence of common Java library calls, failing to capture the profound semantic difference.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clone because the functions have entirely different functionalities, no shared logic beyond basic Java API usage.
- 行为差异: Different input types: String vs HttpServletRequest and multiple objects；Different output: encoded String vs ActionForward；Different purpose: password encoding vs web request handling and classification
- 修正建议: Improve training data with more diverse non-clone pairs；Enhance model with better understanding of method purpose via data flow and call graph features；Apply post-hoc filtering based on Jaccard similarity or length difference

### case_id=2495 FP boilerplate_overlap

- 方法: `main` vs `unzip`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Generates adapter classes from a Prolog file using a parser and class writer.
- B 摘要: Extracts the contents of a zip file to a directory.
- 静态失败原因: Static BERT likely relied on overlapping boilerplate tokens like 'File', 'IOException', 'try', 'catch', and stream handling, leading to a false positive due to lexical surface similarity.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would not consider these clones because they have entirely different functionality and structure, despite some shared low-level file handling patterns.
- 共享行为: Both involve file I/O and handle exceptions.
- 行为差异: Function A parses Prolog and generates Java classes; Function B decompresses a zip archive.；Function A uses a complex pipeline with multiple visitors and writers; Function B uses a simple streaming loop.；Function A produces output files and resources; Function B writes extracted files to disk.
- 修正建议: Improve semantic understanding by training on more diverse clone pairs.；Incorporate structural analysis to differentiate high-level purpose from low-level plumbing.

### case_id=2496 FN lexical_or_api_overlap

- 方法: `readRemoteFile` vs `readGeoParserResult`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a remote file line by line and returns concatenated content as a string.
- B 摘要: Sends an XML request to a geocoding service, reads and parses the XML response to extract place names and IDs, returning a collection of tuples.
- 静态失败原因: Static BERT/GraphCodeBERT models rely on token overlap and structural similarity; here they are very low, so the model correctly predicted non-clone, but BCB's annotation is inconsistent.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: Despite low Jaccard similarity, BCB may consider them Type-3 clones because both read from URL using BufferedReader and handle IOException, but the overall functionality is too different for a meaningful clone.
- 共享行为: Both open a URL and read from it using BufferedReader；Both handle IO exceptions；Both return results after reading input
- 行为差异: Different input parameters (none vs recordContent and getGazeteerIds)；Different output types (String vs Collection of Tuples)；B performs XML request construction and parsing, A does simple string concatenation；B includes retry logic and complex XML iteration, A does not
- 修正建议: Incorporate more semantic analysis like data flow and API call patterns.；Use fine-tuning with functional task labels to distinguish different high-level goals.

### case_id=2497 FN partial_functionality

- 方法: `runScript` vs `createHTML`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a script file from a URL based on script name and returns its content as a string.
- B 摘要: Constructs an HTML page by reading a CSS file, querying a database, and assembling HTML based on a page type.
- 静态失败原因: Static BERT/GraphCodeBERT models rely heavily on token overlap and local context; low Jaccard similarity and large structural differences caused the model to miss the abstract shared behavior of resource loading and string construction.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled these as clones because both functions involve reading a resource from a URL and returning a string, which is a Type-4 semantic similarity (both perform resource loading and string building). The overall goal of returning a string built from external input is shared.
- 共享行为: Both open a URL stream to read data；Both concatenate strings to build a result；Both return a String
- 行为差异: runScript reads raw bytes from a single file; createHTML reads a CSS file and then builds HTML with database results；createHTML has complex logic with switch-case, database queries, and HTML structure; runScript has simple loop；runScript returns the raw file content; createHTML returns generated HTML
- 修正建议: Improve representation of data flow to capture that both functions read from a stream and build a string.；Use more abstract semantic features, e.g., detecting common patterns like 'resource loading' and 'string building'.；Increase training data with Type-4 clones that have low token similarity but similar high-level behavior.

### case_id=2498 FP partial_functionality

- 方法: `setContenu` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.99`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Sets content of an electronic file by copying input stream, validating file existence, and updating metadata.
- B 摘要: Handles various action commands for a settings dialog, updating UI components and saving preferences.
- 静态失败原因: The static model likely over-relied on superficial similarities such as the presence of if-else blocks, file-related operations, and exception handling, missing the fundamental difference in domain and purpose.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB annotators would consider these non-clones because they perform entirely different tasks (file content vs UI actions) with no functional overlap.
- 共享行为: Both involve conditional logic and file-related operations (stream copy vs file chooser).
- 行为差异: Function A focuses on file content and metadata management; Function B focuses on UI interaction and preferences.；Function A uses I/O streams; Function B uses file choosers and preference storage.；Function A handles exceptions like IOException and DocumentVideException; Function B handles user interface events.
- 修正建议: Improve model's ability to distinguish between UI event handling and business logic by incorporating more diverse training data or using contrastive learning.；Enhance representation to capture high-level purpose via task-specific embeddings or hierarchical attention.

### case_id=2499 FP long_range_semantics

- 方法: `readData` vs `copyFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `static_summary_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Reads multiple comma-separated strings into HashSets and processes a file to populate lookup tables.
- B 摘要: Copies a file from source to destination using FileChannel.
- 静态失败原因: Static BERT models may rely on token overlap or shallow patterns; despite low Jaccard, the model might have been misled by common Java idioms like try-catch or loops, lacking understanding of the overall task.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB typically labels clones when functions share significant functional similarity; here there is no overlap in purpose or behavior.
- 行为差异: readData parses strings and populates data structures; copyFile transfers file content.；readData has complex logic with error handling for file parsing; copyFile has simple I/O.；readData modifies multiple global sets; copyFile has no side effects beyond file copy.
- 修正建议: Incorporate dataflow analysis to capture variable usage and dependencies.；Train on more diverse examples to avoid spurious correlations with boilerplate code.

### case_id=2500 FN benchmark_preference_bias

- 方法: `getEncoding` vs `CheckUrl`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Extracts character encoding from a URL response by checking headers and then the response body.
- B 摘要: Reads and returns the first line of a URL response.
- 静态失败原因: The static BERT model correctly predicted non-clone because of low lexical overlap and different high-level behavior; the BCB label appears to be an annotation inconsistency.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled these as clones due to both being URL-reading utilities that open connections and read lines, but their outputs and purposes are functionally distinct.
- 共享行为: Both open a URL connection and read from an InputStream；Both use BufferedReader to read data
- 行为差异: A extracts encoding from headers and body, B returns the first line；A returns a default encoding if none found, B returns empty string on exception；A checks header fields for content-type, B does not；A closes the reader in finally, B does not close resources
- 修正建议: Re-examine BCB annotations for consistency；Use models that capture intent and output types to avoid overgeneralizing to domain similarity
