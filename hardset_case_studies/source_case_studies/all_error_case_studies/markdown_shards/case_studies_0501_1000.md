# Error Case Studies 501-1000

- Source model: `configured-llm`
- Cases: `501` to `1000`

### case_id=501 FN partial_functionality

- 方法: `doCopyFile` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Copies a file from source to destination, verifying completeness and preserving modification date if requested.
- B 摘要: Launches a NexOpen project configuration by processing Maven pom files, setting Hibernate properties, and optionally copying a reverse engineering resource file, then scheduling an install action.
- 静态失败原因: The static BERT model likely relied on token embedding similarity and structural features. These two functions have very low lexical overlap (Jaccard 0.0569) and different control flow (A is simple linear, B has nested conditionals and callbacks). The model could not capture the high-level semantic similarity of file copy due to the large structural differences and different domain contexts.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: Under a broad interpretation of functional similarity, both methods involve copying files (A entirely, B partially when copying the reverse engineering resource). BCB may consider them Type-4 clones because they share the concept of file copying as a sub-task, even though the overall functionality differs.
- 共享行为: Both methods perform file I/O operations including reading and writing files.；Both use try-finally blocks to ensure resource cleanup.；Both involve file existence checks.
- 行为差异: Method A is solely a file copy utility; Method B is a complex project launch procedure with multiple steps unrelated to file copy.；Method A uses FileChannel for efficient transfer; Method B uses ByteArrayOutputStream and IOUtils.copy for resource copying.；Method A's core functionality is file copy; Method B's file copy is only a small sub-task.
- 修正建议: Use dataflow-aware or graph-based models to capture sub-method similarities.；Incorporate program slicing to focus on relevant parts.

### case_id=502 FP lexical_or_api_overlap

- 方法: `init` vs `getFrameworkFactory`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Loads all controller classes from a registry file in classpath.
- B 摘要: Returns the first OSGi FrameworkFactory instance from a service file in classpath.
- 静态失败原因: Static models rely heavily on token and structural overlap. The similar usage of getResource, BufferedReader, readLine, trim, and comment-skipping created a strong lexical signal, overshadowing the semantic differences in iteration vs. single return, error handling, and class loading.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely considers these non-clones because their purposes differ (initializing multiple controllers vs. obtaining a single factory) and the shared reading boilerplate is incidental, not indicative of semantic equivalence.
- 共享行为: Both read a classpath resource line by line.；Both skip empty lines and comment lines starting with '#'.；Both load classes based on the line content.
- 行为差异: A loads all classes into a collection; B returns an instance of the first class.；A uses classLoader.loadClass; B uses Class.forName and newInstance.；A logs errors and continues; B throws an exception on failure.；A does not close the BufferedReader; B closes it in a finally block.
- 修正建议: Incorporate dataflow analysis to distinguish between linear iteration and early return.；Include negative examples with similar boilerplate but different high-level behavior.；Attend to differences in resource management (e.g., closing vs. not closing readers).

### case_id=503 FP lexical_or_api_overlap

- 方法: `fetchUrl` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches the entire content of a given URL as a string, returning empty on failure.
- B 摘要: Performs a Google image search, parses the response to extract image URLs, updates a global list and UI components.
- 静态失败原因: The model likely over-weighted the lexical and structural overlap (URL, BufferedReader, while loop) and missed the significant semantic gap caused by additional logic, side effects, and different output types.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels as clone only if functions perform the same high-level task with moderate to high similarity. Here, despite some API overlap, the overall functionality is entirely different (generic URL reader vs specialized image search with side effects), so BCB marks as non-clone.
- 共享行为: Both open a URL and read its content line by line using BufferedReader and InputStreamReader.；Both use try-catch blocks to handle exceptions.
- 行为差异: Function A is a pure function with no side effects; B modifies global state and UI.；Function B constructs a query URL, adds HTTP headers, parses HTML, and extracts image URLs; A simply returns raw content.；Function B handles exceptions broadly with error dialogs; A returns empty string for specific exceptions.；Function B has post-processing steps (splitting, filtering, adding to list, setting icon) completely absent in A.
- 修正建议: Incorporate dataflow analysis to detect side effects and broader context.；Use representation that captures the full abstract syntax tree and control flow, not just token sequences.；Train on more diverse examples where similar API usage leads to different high-level tasks.

### case_id=504 FN benchmark_preference_bias

- 方法: `copyFile` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.2`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Copies a file from source to destination using I/O streams.
- B 摘要: Launches an Eclipse project configuration by managing Maven POM files and setting project properties.
- 静态失败原因: Static BERT/GraphCodeBERT likely failed to recognize the clone because it focused on the low token Jaccard similarity and the overall difference in structure and API usage, but it possibly missed the shared file I/O pattern that BCB considered relevant.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled these as clones due to superficial lexical overlap (both use InputStream, FileInputStream, etc.) or due to a broad interpretation of Type-4 clone where both perform file I/O, though semantically they are unrelated.
- 共享行为: Both use I/O streams (InputStream/OutputStream) for file reading/writing.
- 行为差异: copyFile is a simple utility method with a single purpose; launch is a complex method with multiple steps including XML parsing, resource management, and project configuration.；copyFile handles no exceptions beyond IOException; launch handles CoreException, IOException, and uses try-finally blocks.；copyFile has no dependencies on IDE-specific APIs; launch heavily uses Eclipse and JavaCore APIs.；copyFile directly copies bytes; launch processes POM files and generates resources based on configuration attributes.
- 修正建议: Improve static models to better distinguish between incidental API overlap and true functional similarity.；Train on more balanced datasets where simple utility functions are not paired with complex orchestration methods.；Incorporate domain-specific knowledge to avoid false positives from trivial I/O usage.

### case_id=505 FP lexical_or_api_overlap

- 方法: `readScalarpvviewerDocument` vs `loadExistingAntlibs`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a specialized XML document from a URL and updates UI components (title, font, panels, PVs) based on its content.
- B 摘要: Loads ant library definitions from classpath resources by reading lines and resolving URIs.
- 静态失败原因: The model likely overfit to shared API tokens (BufferedReader, InputStreamReader, URL, readLine, trim, catch IOException) and the loop structure, ignoring the distinct high-level logic and data transformations.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB annotators label clones based on semantic equivalence; these functions have entirely different purposes and outputs, so they are non-clones.
- 共享行为: Both open a stream from a URL/resource；Both use BufferedReader to read lines；Both trim lines and handle IOException
- 行为差异: A parses XML to set UI properties; B resolves URIs and loads antlibs；A skips comment lines (starting with '%'); B does not；A uses XmlDataAdaptor for structured data; B uses URI construction and loadAntLib
- 修正建议: Incorporate dataflow or control-flow analysis to distinguish boilerplate I/O from core logic；Use contrastive learning on examples where API usage is shared but semantics differ；Add attention to method names and structural differences

### case_id=506 FN boilerplate_overlap

- 方法: `invoke` vs `PhoneSetImpl`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Invokes a remote method via HTTP POST with retry on timeout and returns the deserialized response.
- B 摘要: Constructs a PhoneSetImpl by reading a URL, parsing lines that do not start with '***', and populating a map.
- 静态失败原因: The model correctly identified the semantic mismatch between an HTTP invocation with JSON handling and a simple file parsing constructor. It likely did not consider the trivial I/O boilerplate as sufficient for a clone relation, leading to a false negative under the BCB label.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: The only possible justification for a clone label is the shared use of BufferedReader and InputStreamReader for line-by-line input reading, which is a very broad Type-4 match. However, this is likely an annotation error.
- 共享行为: Both read from an InputStream using BufferedReader and close the stream.
- 行为差异: Function A performs HTTP POST and JSON deserialization; B parses custom text lines.；Function A has retry logic; B does not.；Function A returns an Object; B initializes an object.
- 修正建议: Include a filtering mechanism to ignore trivial I/O boilerplate when it is the only commonality.；Enhance the model's ability to differentiate between core functionality and peripheral code patterns.

### case_id=507 FN benchmark_preference_bias

- 方法: `decodeBody` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Decodes an input stream by applying content transfer encoding decoding (quoted-printable or base64), then copies it to a temporary file body and returns it.
- B 摘要: Launches a specific Eclipse IDE configuration for a NexOpen project, involving validation, XML profile handling, property setting, and file copying for reverse engineering.
- 静态失败原因: The static BERT model likely failed to recognize this as a clone because it relies on token similarity and syntactic structure, which are extremely low (Jaccard=0.06), and it lacks the ability to infer abstract semantic similarity that BCB might consider for partial functionality.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as a clone due to a very broad notion of Type-4 or partial functionality similarity, focusing on the common use of IOUtils.copy and stream handling, ignoring the vast difference in overall purpose and complexity.
- 共享行为: Both use IOUtils.copy to copy data from an InputStream to an OutputStream；Both handle IOException
- 行为差异: Function A is a simple stream decoding and file writing; Function B involves complex IDE launch logic, project configuration, XML parsing, and multiple file operations；Function A returns a BinaryTempFileBody; Function B returns void and interacts with Eclipse workspace resources；Function A is stateless; Function B has side effects and dependencies on external framework classes
- 修正建议: Re-evaluate BCB annotation guidelines to ensure consistency with strict semantic equivalence；Improve model training with more examples of non-obvious non-clones and refine partial functionality detection；Use a hybrid approach combining structural and semantic analysis to capture both strict and broad clone definitions

### case_id=508 FP boilerplate_overlap

- 方法: `downloadModel` vs `parse`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Downloads an RDF model from a URL using HTTP connection and reads it into a Jena Model.
- B 摘要: Parses a delimited data set from a file or URL, handling headers, types, and complex tokenization.
- 静态失败原因: Both functions contain boilerplate code for URL connection and try-catch blocks, and the static model might have been misled by the presence of similar I/O patterns (URL, InputStream, IOException) and common method names like 'read' and 'openStream'.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB annotates as non-clone because the two functions serve entirely different purposes (model download vs. data parsing) and share no significant algorithmic or functional overlap beyond basic I/O.
- 共享行为: Both open input streams from URLs and handle IOExceptions.
- 行为差异: Function A specifically handles HTTP connections and RDF model reading, while B uses StreamTokenizer for parsing structured data.；Function B has extensive logic for headers, types, delimiter configuration, and scientific notation, absent in A.；Function A is short and focused on downloading a model; B is long with multiple stages (reading headers, columns, error handling).
- 修正建议: Incorporate method name similarity or domain-specific embeddings to distinguish different tasks.；Use structural differencing (e.g., AST diff) to ignore common exception handling and I/O boilerplate.；Focus on the core logic rather than peripheral code when computing similarity.

### case_id=509 FN partial_functionality

- 方法: `testNetworkHTTP` vs `login`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.75`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: A test method that performs multiple HTTP GET requests to various URLs, discarding responses, likely for exfiltration of device data.
- B 摘要: A login method that sends a POST request with credentials, reads the response to extract a session ID, and returns it.
- 静态失败原因: Static BERT models rely on lexical and syntactic similarity, which is low (token Jaccard 0.172). They struggle to capture high-level functional similarity when control flow, variable names, and string literals differ significantly. The model likely focused on the different code structure and missed the shared API usage pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considers both as clones under a broad Type-4 functional category: both are network communication functions that follow a common pattern (open connection, read/write data, handle exceptions), despite differing specifics like GET vs POST and parameter handling.
- 共享行为: Both use Java networking (URL, URLConnection) to make HTTP requests；Both read from the input stream using BufferedReader；Both handle exceptions with try-catch blocks
- 行为差异: Function A performs multiple GET requests; Function B performs a single POST request；Function A discards all response data; Function B processes the response to extract a session ID；Function A returns void; Function B returns a String；Function A uses HttpURLConnection; Function B uses URLConnection with output enabled
- 修正建议: Train models on abstracted API sequences (e.g., replacing specific URLs and variable names with placeholders) to capture functional patterns.；Incorporate data flow analysis to recognize similar I/O operations.；Use contrastive learning with functional labels or code summarization to align embeddings of semantically similar methods.

### case_id=510 FP other

- 方法: `perform` vs `digest`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.1`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: A Struts action that validates session, processes request parameters, builds XML, sends HTTP request, and parses classification result.
- B 摘要: A utility method that computes MD5 hash of an input string and returns its hexadecimal representation.
- 静态失败原因: The model likely relied on shallow patterns like method length or presence of common keywords (e.g., 'digest' in B vs. variable names in A), leading to a false positive despite low token overlap.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB would not label these as clones because they have no functional similarity; they are from entirely different domains and tasks.
- 共享行为: Both take input and produce output
- 行为差异: Function A performs complex business logic with multiple steps; Function B is a simple hash computation.；Function A interacts with HTTP and session; Function B is a pure function.；Function A has error handling and conditional logic; Function B has none.；Function A returns an ActionForward; Function B returns a String.
- 修正建议: Improve training data diversity to avoid spurious correlations.；Incorporate structural information like AST or data flow to distinguish different functionalities.

### case_id=511 FP lexical_or_api_overlap

- 方法: `copyFile` vs `readData`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Copies a file from source to destination using FileChannel.
- B 摘要: Reads a configuration file and populates various sets and maps for Tibetan transliteration.
- 静态失败原因: The model likely overfitted to superficial similarities such as try-catch blocks, file-related API names (FileInputStream, FileOutputStream), or generic keywords, while ignoring the distinct program logic and purposes.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would not consider these clones because they perform entirely different tasks; the only commonality is file I/O, which is too generic and insufficient for clone classification.
- 共享行为: Both involve file I/O operations
- 行为差异: copyFile copies a file using NIO channels; readData parses tokenized strings and builds data structures；copyFile returns boolean indicating success; readData is void and modifies static collections；copyFile is short and simple; readData is very long and complex
- 修正建议: Train with more discriminative features that capture high-level program semantics；Use contrastive learning to better separate functions with different intents；Incorporate control flow and data flow analysis to understand actual behavior

### case_id=512 FP boilerplate_overlap

- 方法: `getLinksFromURLFast` vs `lookupFutureEvents`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches HTML from a URL and extracts all hyperlinks and their anchor texts using regex.
- B 摘要: Fetches JSON from the Meetup API for a group and parses it into a list of Event objects.
- 静态失败原因: The static BERT/GraphCodeBERT model likely relied on surface-level similarities such as both functions having URL connection setup, BufferedReader reading, while loops, and string building. The model may have been biased by the overlapping keywords (URL, BufferedReader, while, readLine, append) and pattern of opening a connection, reading lines, and building a string. However, it missed the deeper semantic differences in the purpose and output structure. The model's self-attention may not have sufficiently captured the functional intent differences.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels this as non-clone because the two functions perform fundamentally different tasks: one is a generic link extractor, the other is a Meetup event fetcher. Even though both involve HTTP and parsing, the output types and data manipulations are distinct, and they are not considered similar under BCB's taxonomy of Type-1/2/3/4 clones. Type-4 (functionally different) is labeled 0.
- 共享行为: Both open a URL connection and read data line by line.；Both parse the retrieved content (HTML vs JSON) to extract structured information.；Both use string building (StringBuffer/StringBuilder) to accumulate input.
- 行为差异: Function A extracts links from HTML using regex; Function B parses JSON to create Event objects.；Function A returns a Vector array of links and texts; Function B returns a List of Event objects.；Function A uses time checks and prints debug output; Function B does not.；Function A handles mailto: links by skipping them; Function B handles date parsing and timezone conversion.
- 修正建议: Enhance training with more diverse examples where boilerplate code is reused across different tasks.；Use contrastive learning to emphasize functional differences even when lexical overlap exists.；Incorporate structure-based features like output type and method signatures.；Fine-tune on a dataset with explicit negative examples of Type-4 (non-clones) that share boilerplate but differ in functionality.

### case_id=513 FP boilerplate_overlap

- 方法: `getFrameworkFactory` vs `wordFrequency`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Loads OSGi framework factory by reading a service configuration resource from classpath and instantiating the first valid class found.
- B 摘要: Queries word frequency from a web service by constructing a URL, reading lines, and extracting a number from a matching pattern.
- 静态失败原因: Static models like BERT/GraphCodeBERT may overemphasize the shared structural pattern (URL opening, buffered reading, line iteration) while missing the semantic mismatch in return types, exception handling, and domain-specific logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: Even under broad BCB style, these functions are not considered clones because their core functionality is entirely different despite sharing a common I/O pattern; BCB typically requires partial functionality similarity or significant algorithmic overlap, which is absent here.
- 共享行为: Both open a URL and read lines from an input stream；Both iterate over lines and check a condition on each line；Both return after the first matching line
- 行为差异: Different return types (FrameworkFactory vs int)；Different exception handling (throws Exception vs catch and return 0)；A is private static, B is public final instance method；Different purpose: service loading vs web scraping
- 修正建议: Improve model to distinguish domain-specific logic from boilerplate I/O；Incorporate function names and class context as additional features；Add training examples where similar reading loops serve different purposes

### case_id=514 FP boilerplate_overlap

- 方法: `executePost` vs `readVersion`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Sends an HTTP POST request and returns the response body.
- B 摘要: Reads a version file from classpath and sets version, revision, and compile date fields.
- 静态失败原因: Static BERT likely over-weighted the common API usage (URL, BufferedReader, InputStream) and structural pattern, missing the high-level semantic difference.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB expects functional similarity; these perform fundamentally different tasks (HTTP client vs. local file parser) despite sharing boilerplate.
- 共享行为: Both open a URL connection (one HTTP, one classpath resource)；Both read lines from an input stream using BufferedReader；Both use try-catch-finally to handle exceptions and close resources
- 行为差异: A performs network I/O with POST parameters, B reads local resource；A returns a String, B sets instance variables and returns void；A writes data to output stream, B does not；A appends all lines to response, B parses specific prefixes
- 修正建议: Incorporate method name and documentation into the representation；Use data-flow or control-flow analysis to distinguish core logic from boilerplate；Fine-tune on pairs that differentiate I/O patterns

### case_id=515 FN partial_functionality

- 方法: `unJarStart` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Extracts entries from a local jar file that start with a given prefix and saves them to disk.
- B 摘要: Retrieves a resource from a remote URL or local file, caches it locally, and returns an InputStream.
- 静态失败原因: Static models like GraphCodeBERT rely heavily on lexical and syntactic overlap. The token Jaccard is low (0.11), method names and signatures differ, and the code structures are distinct (iteration over jar entries vs. HTTP request with caching). The model likely missed the abstract shared behavior.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often annotates Type-4 clones based on high-level functional similarity. Both functions serve to obtain a resource and save it locally; the differences in source and caching are secondary.
- 共享行为: Both access a resource from a container (jar or remote URL).；Both create directories as needed.；Both save data to local files using I/O streams.
- 行为差异: A only works with local jar files; B works with remote URLs and local files.；A filters entries by prefix; B uses caching and HTTP conditional GET.；A returns void; B returns an InputStream.；A has no caching logic; B has extensive caching.
- 修正建议: Incorporate dataflow analysis to capture resource retrieval and saving patterns.；Use AST-based or control-flow-based models that abstract higher-level operations.；Train on more examples of partial clones with low syntactic but high semantic similarity.；Consider using a model that combines structural and semantic embeddings.

### case_id=516 FP lexical_or_api_overlap

- 方法: `get` vs `loadURL`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Makes an HTTP GET request to retrieve game records based on location and count, parses response lines into GameRecord array, skipping comment lines.
- B 摘要: Downloads a file from a URL with optional basic authentication, writes it to a temporary file while updating a status label with download progress.
- 静态失败原因: Static BERT models rely heavily on token overlap and common API usage (e.g., URLConnection, BufferedReader, readLine), which are abundant in both snippets, causing a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the overall purpose and output differ significantly despite sharing the low-level HTTP reading pattern.
- 共享行为: Both open an HTTP(S) URL connection；Both read the response line by line using BufferedReader
- 行为差异: Function A returns an array of GameRecord, while B is void and writes to a file；Function A includes specific headers for latitude, longitude, and count; B adds basic auth header；Function A skips lines starting with '#' and decodes lines into GameRecord; B writes all lines to a file and updates a UI label；Function A handles HTTP response codes and prints error if not OK; B throws IOException
- 修正建议: Incorporate function signature (return type, parameter list) into representation；Use dataflow analysis to distinguish between parsing records vs. writing to file；Include structural information like control-flow and call graph differences

### case_id=517 FN benchmark_preference_bias

- 方法: `copy` vs `doGet`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.2`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Copies files or directories from a Hadoop FileSystem to local disk, optionally deleting the source.
- B 摘要: Handles HTTP GET requests to serve a web page, checking permissions and rendering with caching.
- 静态失败原因: The model correctly identified no semantic equivalence given low token overlap and completely different APIs and logic.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: Possibly BCB considered them as both performing data retrieval or resource handling, or due to a labeling error in the benchmark.
- 共享行为: Both handle resources (files/pages) and check existence or permissions.
- 行为差异: A copies data; B serves web pages.；A operates on file system paths; B operates on HTTP requests and portal objects.；A has no user authentication; B checks user visibility.；A is static; B is an instance method.
- 修正建议: Review BCB label for correctness; if intentional, incorporate broader semantic groupings.

### case_id=518 FN benchmark_preference_bias

- 方法: `main` vs `Converter`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `preference_memory_with_manual_audit`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a URL and extracts its zip entries to files.
- B 摘要: Reads a file with SJIS encoding and writes it with UTF8 encoding.
- 静态失败原因: Static BERT models rely on lexical and API token overlap (Jaccard=0.226) and exact semantic matching, missing the high-level I/O pattern similarity that BCB accepts.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB often counts broad Type-3/Type-4 clones where the structural pattern of reading and writing in a loop is shared, even if the specific data transformations differ.
- 共享行为: Both read from an input source and write to an output destination using buffered I/O and a loop.
- 行为差异: Function A uses HTTP and zip decompression; Function B does character encoding conversion.；Function A operates on byte streams (InputStream/OutputStream); Function B operates on character streams (Reader/Writer).；Function A extracts multiple files; Function B processes a single file.
- 修正建议: Incorporate structural patterns like buffered I/O loops as clone features.；Use dataflow analysis to recognize transformation-agnostic copy operations.

### case_id=519 FN partial_functionality

- 方法: `copyResource` vs `dump`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource (URL or file) to a destination file using unbuffered streams, throwing an exception on failure or missing resource.
- B 摘要: Copies a file source to a file target using buffered streams, returning a boolean indicating success and catching IOExceptions internally.
- 静态失败原因: The static model likely focused on surface-level differences: different method names, access modifiers, exception handling, and stream types. The low token Jaccard (0.196) indicates little lexical overlap, causing the model to miss the underlying semantic similarity of the copy operation.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BigCloneBench often labels pairs as clones if they perform the same core functionality (e.g., file copying) despite differences in input type, error handling, or stream buffering. The high-level behavior of copying bytes from input to output is considered semantically similar.
- 共享行为: Both copy bytes from an input source to an output file.；Both use a loop to read and write bytes until the source is exhausted.；Both close input and output streams after copying.
- 行为差异: A handles URLs and file existence checks; B only accepts File sources.；A uses unbuffered streams and reads byte-by-byte; B uses buffered streams and checks available().；A throws Exception on error; B returns false and swallows IOException.；A flushes output implicitly? Actually no flush; B explicitly flushes.
- 修正建议: Train on more diverse examples of input-output stream copying patterns.；Incorporate data-flow analysis to recognize read-write loops as a core operation.；Abstract away method names and exception handling to focus on the sequence of stream operations.

### case_id=520 FN partial_functionality

- 方法: `dump` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a file by reading byte-by-byte from a source file and writing to a target file, returning success boolean.
- B 摘要: Downloads a KMZ file from a URL, decompresses it as a ZIP, and extracts each entry to a file with buffered writing.
- 静态失败原因: The static BERT model likely focused on token-level and structural differences (low Jaccard similarity, different control flow with try-catch vs throws, different loop conditions) and failed to capture the abstract semantic pattern of I/O stream copying.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may view both as implementing a generic 'stream copy' pattern (read from input, write to output), which is a common semantic clone despite different contexts and additional processing in function b.
- 共享行为: Both open an input stream to read data；Both read data in a loop and write to an output stream；Both flush and close the output stream；Both handle stream I/O
- 行为差异: Function a reads a local file; function b reads from a URL and a ZIP archive；Function a copies a single file; function b extracts multiple files from a ZIP；Function a uses byte-by-byte reading; function b uses buffered array reading；Function a returns boolean; function b is void and throws exception
- 修正建议: Enhance model to recognize high-level I/O patterns regardless of specific APIs；Include more training examples of varied stream copy operations；Use program slicing to isolate core copy loop and compare at a higher abstraction

### case_id=521 FN partial_functionality

- 方法: `addIDs` vs `retrieveQ`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.65`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches metabolite data from a web service by querying with a name, parses the response, and populates a PeakListRow with various identifiers and molecular weight.
- B 摘要: Fetches the entire content of a URL as a string, with minimal processing.
- 静态失败原因: Static BERT/GraphCodeBERT models rely heavily on token overlap and structural similarity. Here, the token Jaccard is low (0.11), and the control flows differ significantly—A has nested conditionals and variable assignments, while B has a simple loop. The models likely failed to recognize the underlying shared 'URL reading' skeleton due to lack of lexical and structural cues.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both functions as clones under broad Type-4 similarity because both involve 'fetching data from a URL via HTTP and reading it line by line'. The additional processing in A might be overlooked as extended functionality, and the core behavior of URL access and BufferedReader usage is shared.
- 共享行为: Both open an HTTP connection to a URL；Both use BufferedReader to read lines from the connection；Both close the BufferedReader after reading
- 行为差异: A extracts specific data fields (e.g., metaboliteID, molecularWeight, PubChem, ChEBI) and sets them on a PeakListRow object, while B simply concatenates all lines into a single string without parsing.；A returns an integer score, while B returns the full content as a String.；A has complex branching logic based on the content of each line, whereas B reads all lines uniformly.；A accesses a specific URL pattern with a query parameter, while B uses a generic URL passed as argument.
- 修正建议: Incorporate dataflow analysis to trace the flow of data from URL opening to reading, capturing the shared I/O pattern.；Use graph-based representations that abstract away specific variable names and highlight structural motifs like 'open connection, read loop, close'.；Augment training data with examples of broad Type-4 clones where the core algorithm is similar despite different elaboration.

### case_id=522 FP boilerplate_overlap

- 方法: `handleHandshake` vs `doVersionCheck`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Handles a handshake packet by validating username and optionally performing a session server check to decide login or disconnect.
- B 摘要: Performs a version check by reading a version file from a URL and comparing build numbers to notify the user.
- 静态失败原因: Static models like BERT or GraphCodeBERT may over-rely on overlapping tokens (URL, BufferedReader, InputStreamReader) and structural patterns (try-catch, while loop) without capturing the distinct domain logic and different intended behaviors.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels these as non-clones because the functional purpose is entirely different despite sharing common IO boilerplate; BCB prefers semantic similarity over syntactic or API overlap.
- 共享行为: Both open a URL and read lines via BufferedReader；Both have try-catch for IOException；Both use URL and InputStreamReader
- 行为差异: Function A validates a server key and handles Minecraft session login, while Function B checks for software version updates；Function A uses different logic for parsing (hex validation, response equals 'ok'), Function B parses lines starting with '.version' and '.build'；Function A interacts with network and sends packets, Function B displays UI messages
- 修正建议: Incorporate data flow analysis to differentiate variable usage；Use program slicing to isolate core logic from boilerplate；Train on diverse examples to reduce overemphasis on common API patterns

### case_id=523 FP lexical_or_api_overlap

- 方法: `main` vs `copyFileTo`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a Prolog file, generates adapter classes and lookup resources, and writes them to a JAR file.
- B 摘要: Copies the content of the current file to a specified destination file using file channels.
- 静态失败原因: Static BERT may have been misled by superficial similarities like both containing 'File', 'IOException', and 'try-catch' blocks, despite dramatically different high-level behaviors.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: None
- 共享行为: Both involve file I/O operations；Both use 'throws IOException'
- 行为差异: Function A performs complex parsing, class generation, and JAR writing; Function B only copies a file；Function A has multiple fallbacks and prints messages; Function B is straightforward；Function A uses many external classes like Parser, ClassWriter; Function B uses only basic Java I/O classes
- 修正建议: Include more negative examples with overlapping APIs but different purposes；Use contrastive learning that penalizes embedding proximity for such pairs；Incorporate task-oriented features (e.g., function name, context) to disambiguate

### case_id=524 FP lexical_or_api_overlap

- 方法: `getLinksFromURLFast` vs `parse`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Extracts hyperlinks and their text from HTML content of a given URL using regex.
- B 摘要: Parses a structured data file (from file or URL) into a DataSet object based on configured headers and types.
- 静态失败原因: The static model likely over-relied on superficial lexical and API overlaps (e.g., URL, BufferedReader, regex usage) while missing the deep semantic differences in data processing logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB considers these non-clones because they perform fundamentally different tasks despite sharing some common I/O and URL reading boilerplate.
- 共享行为: Both use I/O to read from a URL or file；Both use BufferedReader for reading text
- 行为差异: Function A extracts links from HTML; Function B parses tabular data with type conversion；Function A uses regex on the entire page; Function B uses a StreamTokenizer line by line；Function A returns a vector of links and texts; Function B returns a DataSet object；Function B handles headers, types, and scientific notation; Function A does not
- 修正建议: Incorporate method name and return type as strong signals；Use contrastive learning to penalize shallow structural similarity；Enhance model with dataflow or semantic roles of variables

### case_id=525 FP boilerplate_overlap

- 方法: `encryptPassword` vs `perform`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Computes MD5 hash of a password and returns it as a hex string.
- B 摘要: Processes a web request to classify a concept, involving session management, parameter parsing, XML communication, and forwarding to an appropriate view.
- 静态失败原因: The model likely overfitted to common boilerplate patterns (e.g., StringBuffer, for loops) and ignored the distinct functional semantics, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB requires functional similarity for clones; these two functions have completely different purposes and no shared functionality, so BCB correctly labels them as non-clones.
- 共享行为: Both use StringBuffer to build strings.
- 行为差异: A computes a cryptographic hash; B handles web requests and performs classification logic.；A has no external dependencies; B uses many external classes (e.g., HttpServletRequest, URLConnection).；A returns a simple string; B returns an ActionForward.
- 修正建议: Incorporate task-specific information or dataflow analysis to distinguish different functionalities.；Enhance training with diverse examples to reduce reliance on boilerplate patterns.

### case_id=526 FP boilerplate_overlap

- 方法: `addDataFromURL` vs `readZoneIDs`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads lines from a URL and appends them to a StringBuilder, appending the URL itself on error.
- B 摘要: Reads integers from a resource file and returns them as a set.
- 静态失败原因: Static BERT models may be misled by high lexical overlap (e.g., 'while ((line = ...) != null)', exception handling pattern) and overemphasize the common line-reading loop as a clone indicator, ignoring the semantic differences in data processing.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB considers the overall functionality: one accumulates raw text, the other parses numbers for ID collection, which are distinct tasks despite similar IO boilerplate.
- 共享行为: Both read external data line by line；Both handle IO exceptions with printStackTrace；Both use a buffered reader pattern
- 行为差异: Function A accepts a URL; Function B accepts a resource path string；Function A accumulates text; Function B parses integers and returns a set；Error handling differs: A appends URL on error, B only prints stack trace；Function A is void; Function B returns a HashSet<Integer>
- 修正建议: Incorporate data flow analysis to track how each line is used (append vs parseInt)；Consider return types and variable types as features；Use semantic similarity of method names and comments

### case_id=527 FP boilerplate_overlap

- 方法: `actionPerformed` vs `copyFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Handles action events for a settings dialog, processing commands like GRAPHVIZ and IMAGEMAGICK by opening file choosers and saving preferences.
- B 摘要: Copies a file from source to destination using FileChannel with error handling.
- 静态失败原因: The static model likely overfitted to common boilerplate (e.g., try-catch, File, IOException) and ignored the overall functional context, misled by the long and complex code in A.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clone because the functions have completely different overall purposes and behavior, despite sharing some low-level file-related API calls.
- 共享行为: Both involve file operations (A uses file chooser, B copies file)；Both use try-catch for exception handling
- 行为差异: A is a complex event handler with many UI updates and preference saves, B is a simple file copy；A has multiple conditional branches, B is linear；A uses JFileChooser, B uses FileChannel
- 修正建议: Train with more diverse long functions to reduce boilerplate bias；Incorporate better structural or flow analysis to distinguish different functionalities

### case_id=528 FN partial_functionality

- 方法: `getHTML` vs `addIDs`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches an HTML page from a URL, reads it line by line, optionally writes to a file, and returns the HTML string.
- B 摘要: Queries a metabolite database by name, parses the HTML response to extract metabolite IDs and properties, sets them on a PeakListRow object, and returns a score.
- 静态失败原因: The static BERT model likely failed to detect the clone because the token Jaccard similarity is low (0.1347) and the method names and overall flow differ significantly. The model may have overemphasized the structural differences (different return types, side effects, and parsing logic) while underestimating the common underlying pattern of performing an HTTP GET and reading the response line-by-line.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this as a clone because both functions share the core pattern of fetching HTML from a URL via HTTP GET and reading it line-by-line, which is considered a Type-3 or partial functionality similarity. The additional parsing and object modification in function B can be seen as extensions, not changing the fundamental 'web page fetcher' behavior.
- 共享行为: Both functions open an HTTP connection to a URL and read the response line by line using BufferedReader and InputStreamReader.
- 行为差异: Function A returns the entire HTML content as a String; function B returns an integer score and modifies a PeakListRow object with parsed data.；Function A optionally writes the HTML to a file; function B does not write to a file.；Function B includes extensive HTML parsing logic to extract metabolite IDs, molecular weight, and other fields; function A does no parsing.；Function A uses HttpURLConnection with a User-Agent header; function B uses URL.openStream() directly.
- 修正建议: Incorporate more abstract representations of I/O operations, such as detecting HTTP fetch loops.；Use long-range dependency modeling to capture the overall structure of reading from a URL.；Consider data flow analysis to recognize that both functions create a URL, open a stream, and consume it line-by-line.

### case_id=529 FP boilerplate_overlap

- 方法: `simulate` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Simulates user reputation by reading action calls from a file and making remote service calls with assertions.
- B 摘要: Handles GUI action events for setting file paths for external tools and saving user preferences.
- 静态失败原因: Static BERT/GraphCodeBERT may have been misled by overlapping boilerplate patterns (file I/O, try-catch, loops) and common API usage (File, BufferedWriter), while missing the high-level semantic difference between a simulation test and a GUI event handler.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would consider these non-clones because they implement entirely different business logic and have no shared functionality beyond generic I/O and control structures.
- 共享行为: Both use file I/O (A: read/write files, B: file chooser dialog)；Both contain conditional logic (if-else, while loop in A, if-else chain in B)；Both have try-catch blocks for exception handling
- 行为差异: A performs a repeated simulation loop with remote service calls and JUnit assertions；B handles multiple GUI commands, updates UI components, and saves preferences；A focuses on testing a trust/reputation system, B focuses on application configuration；A reads from a predefined file, B responds to user interaction
- 修正建议: Incorporate structural features like method call sequences and domain-specific API usage；Use program dependence graphs or data flow analysis to capture semantic intent；Train with more diverse examples to reduce bias towards generic I/O patterns

### case_id=530 FN benchmark_preference_bias

- 方法: `copyFile` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.2`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Copies a file from source to destination using a buffer, handling IO exceptions.
- B 摘要: Launches a Eclipse launch configuration by processing Maven pom files, handling Hibernate dialect, and running an install project job.
- 静态失败原因: Static BERT/GraphCodeBERT did not fail; it correctly predicted non-clone. The error is in the BCB label. However, if the model had predicted clone, it might have been misled by common API usage (FileInputStream, FileOutputStream) and exception handling patterns.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might have labeled this as clone due to superficial similarities like both using InputStream/OutputStream and file operations, and both having exception handling, but functionally they are completely different. BCB's annotation may have been made by a human who considered them as having partial functional similarity (e.g., both deal with files) or it could be an error.
- 共享行为: Both involve file I/O operations；Both have try-catch blocks for exception handling
- 行为差异: Function A is a simple file copy; Function B is a complex Eclipse launch configuration handler；Function A has no project/configuration logic; Function B has extensive project and configuration handling；Function A's error handling logs via MLUtil; Function B uses different logging and exception propagation；Function B involves multiple file reads, property setting, and resource management beyond simple copy
- 修正建议: Re-evaluate BCB annotation for this pair；Improve benchmark consistency by ensuring that only semantically similar functions are labeled as clones

### case_id=531 FN partial_functionality

- 方法: `copyResource` vs `getProjectTreeData`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.75`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource from a URL or local file to a destination file by reading and writing bytes.
- B 摘要: Downloads an XML file from a server, saves it locally, parses it to extract project tree data into a 2D array.
- 静态失败原因: The token Jaccard similarity is very low (0.13) and the model likely relies on surface-level token overlap and structural similarity. The presence of XML-specific tokens, different method names, and extensive exception handling in B masked the shared I/O pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often includes Type-3/Type-4 clones where a common sub-functionality is shared. Here, both functions perform a file download/copy from a URL to a local file, which is a distinct sub-task.
- 共享行为: Both open an input stream from a URL or file；Both read binary data from the stream；Both write the data to an output file using a loop
- 行为差异: Function A only copies bytes; Function B additionally parses XML and returns structured data；Function A throws exceptions; Function B catches and prints them；Function A uses simple byte-by-byte read; Function B uses a large buffer；Function A's output is a file; Function B's output is a 2D string array
- 修正建议: Enhance training with more examples of partial-functionality clones where a small but essential sub-behavior is shared.；Incorporate data flow analysis to recognize I/O copying loops as a distinct pattern.；Use contrastive learning to focus on shared sub-tasks rather than overall functionality.

### case_id=532 FN benchmark_preference_bias

- 方法: `getResourceAsStream` vs `copyExternalResource`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Retrieves a resource by name, caching it locally from a URL, and returns an InputStream.
- B 摘要: Copies the contents of a source file to a destination file using FileChannel.
- 静态失败原因: Static BERT/GraphCodeBERT correctly predicted non-clone due to low lexical overlap and different control flow, aligning with strict semantics.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider both as examples of 'resource copying' or 'stream I/O' tasks, but this is a stretch and likely an annotation error, as the purposes and implementations differ significantly.
- 共享行为: Both involve file I/O and stream operations.；Both open and close resources.
- 行为差异: Function A retrieves from remote URL with caching logic; Function B is a local file copy.；Function A returns an InputStream; Function B returns void.；Function A has explicit HTTP handling and caching; Function B does not.；Function A uses buffered streams; Function B uses FileChannel.
- 修正建议: Ensure BCB annotations are consistent with more precise functional equivalence criteria.；Consider using stricter thresholds for Type-4 clones.

### case_id=533 FP lexical_or_api_overlap

- 方法: `readPage` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a web page from a URL, optionally skipping lines starting with '#', and returns the HTML as a string.
- B 摘要: Performs a Google image search, extracts image URLs from the HTML, stores them in a list, and updates a GUI with the first image.
- 静态失败原因: Static BERT models often rely on lexical and API overlap. Both functions use similar boilerplate code (URL, BufferedReader, while-read loop), misleading the model into thinking they are clones despite divergent semantics and side effects.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely considers non-clone because the functions have different purposes (utility vs. specific task), different return types, and low token overlap (0.168). BCB's broad criteria still require some functional similarity, which is lacking here.
- 共享行为: Both open an HTTP connection and use BufferedReader to read the response line by line.
- 行为差异: readPage returns the entire HTML string, while googleImageSearch parses HTML to extract image URLs and updates a GUI state.；readPage optionally ignores comment lines (starting with '#'), googleImageSearch does not but later removes newlines.；googleImageSearch has GUI side effects and specific URL construction, readPage is a generic reader without side effects.；Exception handling differs: readPage throws Exception, googleImageSearch shows error dialogs and disables/enables buttons.
- 修正建议: Train with more negative examples that share API usage but differ in overall task (e.g., one returns data, one updates GUI).；Incorporate dataflow or control-flow analysis to detect differences in output and side effects.；Use method-level features like return type, parameters, and class context.

### case_id=534 FP boilerplate_overlap

- 方法: `decodeFileToFile` vs `main`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Base64 decodes an input file and writes the decoded content to an output file, returning success status.
- B 摘要: Main entry point for an adapter generator that parses a Prolog file, generates adapters, and writes them into a JAR file.
- 静态失败原因: The static model overemphasized lexical overlap of common I/O patterns (File, InputStream, OutputStream, catch, etc.) and ignored the high-level semantic difference, likely due to bias towards code structure similarities.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labeled as non-clone because the functions have completely different purposes and only share trivial boilerplate patterns; even under broad Type-4 semantic similarity, the overall functionality is not similar.
- 共享行为: Both perform file I/O (reading and writing files)；Both use buffered streams；Both catch and print IOException；Both have try-catch-finally blocks
- 行为差异: A performs Base64 decoding; B does not；B has complex logic for parsing Prolog, generating adapters, and writing JAR files; A is a straightforward file copy with decoding；A returns a boolean; B returns void and prints output；B uses many external classes; A is self-contained
- 修正建议: Incorporate semantic understanding by considering method signatures and class contexts；Use data flow analysis to differentiate core logic from boilerplate；Train with more diverse negative examples to reduce bias towards common I/O patterns

### case_id=535 FP lexical_or_api_overlap

- 方法: `genCustRatingFileAndMovieIndexFile` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a binary master file containing movie ratings and generates separate index and rating files.
- B 摘要: Handles action events in a GUI to set various preferences and file paths for external tools.
- 静态失败原因: The model might have been misled by superficial lexical overlap such as common words like 'File', 'putPref', or 'owner', and failed to capture the high-level semantic difference.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would label as non-clone because the functions have completely different purposes (file processing vs. GUI event handling) and no overlapping functionality beyond general Java constructs.
- 共享行为: Both use Java I/O classes (File, FileChannel, etc.) in a general sense
- 行为差异: Function A performs binary file parsing and data transformation; Function B handles GUI event dispatching and preference configuration.；Function A returns a boolean; Function B returns void.；Function A is a private static utility; Function B is an event listener (actionPerformed).；Function A uses low-level NIO buffers; Function B uses Swing components and JFileChooser.
- 修正建议: Improve model sensitivity to structural differences and control flow.；Incorporate more diverse training examples that distinguish between file I/O and GUI event handling.；Use dataflow analysis to capture the different roles of variables.

### case_id=536 FN partial_functionality

- 方法: `getResourceAsStream` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Retrieves a resource from a URL with caching, managing HTTP caching headers and returning a FileInputStream.
- B 摘要: Copies a file to a destination directory using a byte buffer.
- 静态失败原因: Static BERT/GraphCodeBERT methods rely on token and structural overlap; the token Jaccard is low (0.17), and the AST structures differ significantly due to A's additional HTTP and caching logic. The shared substring of file copying is overshadowed by the surrounding complexity, leading to a false negative.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label them clones because both functions implement a file copy operation (reading bytes from a source and writing to a destination), and function A's caching step includes copying from a network stream to a file, which is functionally similar to B's copy. BCB accepts broad Type-4 clones where a common subtask is shared.
- 共享行为: Both open input and output streams；Both read bytes in a loop and write to output；Both close streams after copying；Both handle exceptions with try-catch
- 行为差异: Function A uses HTTP connection and caching logic; B does not；Function A creates directories and handles HTTP status codes; B does not；Function A uses BufferedInputStream/OutputStream; B uses provided buffer array；Function A returns InputStream; B returns void
- 修正建议: Use dataflow-aware models to detect common subcomputations；Apply code summarization to capture high-level intent；Train on examples of partial functionality clones

### case_id=537 FN benchmark_preference_bias

- 方法: `doBody` vs `getFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.35`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Reads a file from disk and writes its contents to the HTTP response output stream.
- B 摘要: Downloads a WSDL file from a URL, modifies its endpoint address, saves it to a temporary file, and returns the file path.
- 静态失败原因: Low lexical overlap (token Jaccard 0.057) and different API usage misled the model to focus on surface differences, missing the potential high-level I/O behavior similarity that BCB might emphasize.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider both as 'file transfer' or 'data streaming' operations, accepting broad Type-4 semantic similarity due to common I/O pattern.
- 共享行为: Both involve reading data from a source and writing to a destination；Both use I/O streams and handle exceptions
- 行为差异: Function A is void and writes to an HTTP response; Function B returns a file path；Function A reads a local file; Function B downloads from a URL and performs XML manipulation；Function A uses IOUtils.copy; Function B uses NIO channels and manual XML parsing
- 修正建议: Incorporate more abstract functional signatures to capture high-level I/O operations；Use transfer learning with task-specific data to recognize broad clone types；Train on datasets with semantic clone annotations like BigCloneBench to adjust model bias

### case_id=538 FN lexical_or_api_overlap

- 方法: `getFile` vs `readAndRewrite`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a given URL, optionally modifies the endpoint in the XML, and saves it to the temporary directory with a .wsdl extension.
- B 摘要: Reads a DICOM medical image file, processes pixel data, and rewrites it to another file using DICOM libraries.
- 静态失败原因: Static models like BERT/GraphCodeBERT rely on lexical and structural similarity (token Jaccard = 0.07), which is too low to detect any commonality. They lack understanding of high-level functional purpose and domain context, causing them to correctly predict non-clone but contradict the BCB label.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may have labeled these as clones based on a broad 'file transformation' pattern where both functions read input, transform it, and write output. However, the transformation and domains are completely different, suggesting a likely annotation error or overly broad Type-4 category.
- 共享行为: Both functions perform file I/O operations: reading from an input source (URL stream or file) and writing to an output file.；Both log or print progress messages (via mLog.debug or System.out.println).
- 行为差异: Function A downloads a WSDL file from a network URL, modifies XML content (wsdlsoap:address), and handles HTTP connections; Function B reads a local DICOM file, processes pixel data, and writes back a DICOM file.；Function A uses Apache Axis and XML parsing libraries (SAX, DOM); Function B uses DICOM-specific libraries (DcmParser, PixelDataReader/Writer).；The file formats, processing logic (XML modification vs. DICOM pixel data handling), and exception handling are entirely different.
- 修正建议: Incorporate data flow and API usage patterns to distinguish different domain-specific tasks.；Improve representation of program semantics through documentation or code comments to capture overall functionality.

### case_id=539 FP lexical_or_api_overlap

- 方法: `doVersionCheck` vs `getFullScreenUrl`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Opens a URL from a configuration property, reads lines to extract version build strings, and delegates to an overloaded method.
- B 摘要: Connects to a YouTube URL, reads the response to find the fullscreenUrl, parses it for video parameters, and constructs a download URL.
- 静态失败原因: Static BERT/GraphCodeBERT may have overemphasized the structural and lexical overlap (URL, BufferedReader, while loop, try-catch) while ignoring the high-level intent and output differences. The similar control flow and API calls could mislead the model into thinking they are related.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the overall functionality and purpose are completely different, despite sharing boilerplate URL reading code. BCB focuses on semantic similarity, not just API usage patterns.
- 共享行为: Open a URL connection using java.net.URL；Read lines from the connection with BufferedReader；Parse lines for specific prefixes or substrings；Close the reader in a try/catch block
- 行为差异: Function A is for version checking; Function B is for constructing a video URL.；A reads from a property-defined URL; B uses a private field 'ytUrl'.；A looks for .build and .stablebuild lines; B looks for 'fullscreenUrl' and parses video_id, t, title.；A delegates to another doVersionCheck method; B returns a String and sets ytTitle.
- 修正建议: Incorporate data flow analysis to track how inputs and outputs are used.；Add features capturing method purpose (e.g., return type, called methods, exception types).；Use contrastive learning to distinguish between boilerplate and core logic.；Train on diverse datasets that penalize high lexical but low semantic similarity.

### case_id=540 FP lexical_or_api_overlap

- 方法: `fetchUrl` vs `loadURL`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches a URL and returns its content as a string, ignoring newlines.
- B 摘要: Opens a URL connection with optional basic authentication, reads lines, writes to a temporary file with progress updates, and does not return the content.
- 静态失败原因: Static models may over-rely on lexical and API-level similarities (URL, BufferedReader, while read loop) without capturing differences in purpose, side effects, and control flow, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would likely consider them non-clones because the overall functionality and output differ significantly: one is a simple URL-to-string utility, the other is a file-downloader with authentication and progress monitoring.
- 共享行为: Both open a URL and read lines using BufferedReader
- 行为差异: A returns the content as a string; B writes to a file and does not return a string.；A has no authentication; B supports basic auth.；A has no progress reporting; B updates a status label.；A catches exceptions and returns empty string; B throws IOException.
- 修正建议: Incorporate structural or flow analysis to distinguish simple retrieval from complex file-writing with progress updates.；Add attention to method parameters, return types, and exception handling as discriminators.

### case_id=541 FP boilerplate_overlap

- 方法: `init` vs `getTicketsForQueue`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: The init method loads controller classes from a registry file by reading class names from resources, loading them with ClassLoader, and adding them via addClass().
- B 摘要: The getTicketsForQueue method retrieves tickets for a given queue from a REST API, parses the response, and returns a list of RTTicket objects.
- 静态失败原因: The static BERT model may have been misled by the shared boilerplate code (BufferedReader, while loop, try-catch) and similar control flow, ignoring the different method names, return types, and high-level semantics.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled this as non-clone because the two functions have drastically different purposes (initialization vs ticket retrieval) and different overall behavior, despite sharing some boilerplate I/O patterns.
- 共享行为: Both use BufferedReader to read lines from a stream.；Both have try-catch blocks handling exceptions (IOException, Exception).；Both loop over input lines.；Both log errors.
- 行为差异: A is initializing the servlet context by loading classes; B is fetching data from an external service.；A reads from local jar resources; B makes HTTP requests to a remote server.；A calls addClass() on each loaded class; B builds a list of RTTicket objects.；Different method signatures and return types (void vs List<RTTicket>).
- 修正建议: Train on more diverse negative examples that share boilerplate but differ in purpose.；Incorporate data flow or method call sequence features to distinguish initialization from retrieval.；Use method-level semantic embeddings that capture overall goal, not just token patterns.

### case_id=542 FN boilerplate_overlap

- 方法: `readGeoParserResult` vs `runInternal`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Constructs XML request to a geo-parser URL, sends HTTP request, parses response to extract place names and gazetteer IDs, with retry logic on failure.
- B 摘要: Opens an OPDS catalog URL, sets up HTTP connection, downloads and parses content, handles pagination and book downloads, with error handling in a loop.
- 静态失败原因: Static BERT models rely on token similarity and structural embeddings; the low token Jaccard (0.106) and different domain-specific vocabulary cause the model to perceive these as non-clones. The models fail to abstract the common control flow pattern due to low lexical overlap.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may consider them clones due to shared high-level structure: a loop with try-catch, network connection, XML parsing, and returning results. The general pattern of 'retry loop -> open URL -> read -> parse -> return' is common, even if the specific data and domain differ.
- 共享行为: Both perform network I/O over HTTP；Both parse XML responses；Both use retry/error-handling loops；Both return collections after processing
- 行为差异: A constructs specific XML request for geo-parsing; B uses generic HTTP with headers and redirects；A retries up to 3 times; B uses a do-while loop with a loadNext flag for pagination；A extracts place names and IDs; B processes OPDS entries and may download books；A handles dummy test mode; B does not
- 修正建议: Incorporate control-flow and data-flow features；Use AST-based matching with structural abstraction；Train with clone pairs that have high semantic similarity but low lexical overlap；Apply learning that focuses on API usage patterns (URL, XML, loop-with-exception)

### case_id=543 FN boilerplate_overlap

- 方法: `downloadURLtoString` vs `login`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.85`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads the entire content of a given URL as a string.
- B 摘要: Performs a login by sending POST parameters to a URL and returns the session ID.
- 静态失败原因: Static BERT/GraphCodeBERT models likely focused on low token similarity and different method names, missing the shared I/O patterns due to high structural divergence.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may label this as a clone due to shared boilerplate of network I/O and string processing, but the specific tasks (download vs. login) are functionally distinct, making it a dubious Type-4 clone.
- 共享行为: Both open a URL connection and read from an InputStream via BufferedReader.；Both process strings (appending, extracting).
- 行为差异: A performs a simple GET and returns all lines; B performs a POST with data writing and reads only the first line to extract a session ID.；A throws IOException; B catches Exception and prints messages.；A returns the full content; B returns a session ID extracted from the response.
- 修正建议: Incorporate method-level context or documentation embeddings.；Use dataflow analysis to compare output variable usage.；Focus on the overall purpose rather than low-level API calls.

### case_id=544 FP other

- 方法: `readData` vs `readAndRewrite`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Parses comma-separated string constants to populate character sets and a mapping for valid input sequences, then reads a structured file to build additional mappings.
- B 摘要: Reads a DICOM image file, parses its dataset, reads pixel data, and writes it to an output file.
- 静态失败原因: The static BERT model likely overemphasized the method names both containing 'read' and the superficial similarity of reading data, ignoring the vastly different contexts and APIs (e.g., DICOM vs. string parsing).
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely labels this as non-clone because the functions serve completely different purposes (character set configuration vs DICOM file I/O) with negligible semantic overlap, despite both involving reading.
- 共享行为: Both involve reading and processing data from external sources.；Both use standard I/O operations (though code_a's file reading is truncated).
- 行为差异: code_a processes string constants and a configuration file; code_b processes DICOM medical images.；code_a builds in-memory sets and maps; code_b writes to an output file.；code_a uses StringTokenizer and manual parsing; code_b uses DICOM-specific libraries.；code_a handles multiple domain-specific sets; code_b handles pixel data and metadata.
- 修正建议: Improve training data to include more diverse data processing patterns.；Enhance model sensitivity to domain-specific APIs and library calls.；Incorporate program slicing or data-flow analysis to distinguish different read/write patterns.

### case_id=545 FN benchmark_preference_bias

- 方法: `compressWithZip` vs `getFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Compresses a list of files into a zip archive.
- B 摘要: Downloads a WSDL file, modifies its endpoint, and saves it locally.
- 静态失败原因: The model correctly predicted non-clone due to low lexical overlap and different method names, but the BCB label suggests a false positive in the benchmark.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled them as clones due to both being file I/O utilities that read and write data, which is a broad Type-4 similarity, but the specific functionalities differ significantly.
- 共享行为: Both read from an input source and write to an output file using byte streams
- 行为差异: compressWithZip creates a zip archive from multiple files；getFile downloads, parses XML, modifies attributes, and saves a single file
- 修正建议: Review BCB annotation guidelines to ensure consistency；Increase threshold for Type-4 clone detection to avoid overly broad semantic similarity

### case_id=546 FN partial_functionality

- 方法: `setBundleInfoName` vs `login`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads bundle name mappings from a remote file and updates a local list of BundleInfo objects.
- B 摘要: Performs a login to a service by sending a POST request with credentials and extracts a session ID.
- 静态失败原因: Static BERT/GraphCodeBERT models rely on token-level similarity and structural patterns; the low token Jaccard (0.18) and differing variable names, control flow, and input/output signatures led the model to miss the underlying common sub-behavior of network I/O and line reading.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considered these clones due to the shared pattern of network I/O (URL connection, reading lines) and line processing, which is a common functional fragment; they may have applied a broad Type-3/Type-4 criterion where partial functional similarity is accepted.
- 共享行为: Both open a URL and read lines from the response；Both use BufferedReader and InputStreamReader with UTF-8 encoding；Both handle I/O exceptions via try-catch；Both involve processing of response lines
- 行为差异: Function A reads only, Function B writes then reads；Different purpose: update bundle names vs login；Different inputs: A takes location and list, B takes no explicit parameters；Different return types: boolean vs String
- 修正建议: Incorporate data flow edges to capture common sub-patterns like network I/O；Use a model that recognizes functional fragments (e.g., API call sequences)；Augment training with negative samples that have low lexical but high functional similarity

### case_id=547 FN partial_functionality

- 方法: `main` vs `copyDeleting`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a URL and extracts all zip entries to files.
- B 摘要: Copies a single file from source to destination using buffered streams.
- 静态失败原因: The model focused on surface-level differences (method names, parameters, URL/zip handling) and low lexical overlap, missing the shared I/O loop structure due to its sensitivity to exact token matches and lack of understanding of abstract patterns.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely labeled this as a clone because both functions share the core I/O loop pattern (reading chunks and writing) which is a common functional pattern, and BCB often accepts such structural similarity even when the surrounding context differs.
- 共享行为: Reads bytes from an input stream into a buffer and writes them to an output stream in a loop.
- 行为差异: Function A handles URL protocols and extracts zip entries; Function B only copies a single file.；Function A uses ZipInputStream and extracts multiple entries; Function B uses FileInputStream/FileOutputStream.；Function A prints extraction progress; Function B does not.
- 修正建议: Incorporate syntactic or structural similarity measures (e.g., AST-based matching) to capture common I/O patterns.；Use contrastive learning with pairs that share core logic despite different contexts.；Increase weight of loop structures and data flow in the representation.

### case_id=548 FN boilerplate_overlap

- 方法: `execute` vs `getFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Injects bytecode into class files using ASM library.
- B 摘要: Downloads a WSDL file from a URL, modifies an endpoint attribute, and saves it locally.
- 静态失败原因: Static BERT/GraphCodeBERT presumably correctly predicted 0 (non-clone) because it captures enough semantic differences to distinguish these unrelated functions.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may have labeled this pair as clone due to superficial similarities in file I/O and exception handling patterns, or due to annotation errors in the benchmark.
- 共享行为: Both involve file I/O operations (reading/writing files).；Both use try-catch blocks to handle exceptions.；Both manage input/output streams.
- 行为差异: Function A processes class files for bytecode instrumentation; Function B downloads and modifies WSDL files.；Function A uses ASM library (ClassReader, ClassWriter); Function B uses XML and URL handling libraries.；Function A modifies bytecode and counts injections; Function B downloads, parses XML, modifies attribute, and saves file.；Function A has no return value; Function B returns a String file location.
- 修正建议: Refine BCB annotations to reduce false positives from generic boilerplate patterns.；Use semantic features beyond token overlap to identify true clones.

### case_id=549 FN boilerplate_overlap

- 方法: `createSettingsIfNecessary` vs `doGet`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Creates a settings file if it does not exist by copying from a resource bundle.
- B 摘要: Handles HTTP GET request for page display, including page lookup, permission checks, response writing, and caching.
- 静态失败原因: Static BERT likely over-emphasized overlapping API calls (File, FileOutputStream, IOUtils.copy in A vs. File.createTempFile, FileWriter in B) and try-finally structures, ignoring the semantic context difference.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may label this as clone due to shared file I/O boilerplate and exception handling patterns, despite vastly different semantics.
- 共享行为: Both involve file operations (creating/writing files).；Both use try-finally for resource cleanup.；Both throw IOException.
- 行为差异: Different core functionality: file initialization vs. HTTP request handling.；Different input parameters and control flow complexity.；Different external dependencies and error scenarios.
- 修正建议: Incorporate program dependency graphs to distinguish core functionality from boilerplate.；Use functional clustering to group methods by their primary purpose.；Include broader context (e.g., class-level info) to disambiguate.

### case_id=550 FP lexical_or_api_overlap

- 方法: `getUser` vs `main`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Loads a user from a DAO or parses a local config file to create and save a user by login.
- B 摘要: Fetches a web page and prints its lines to standard output.
- 静态失败原因: Static BERT/GraphCodeBERT might have overemphasized the lexical and API overlap (URL, BufferedReader, readLine, StringTokenizer) and missed the high-level semantic mismatch due to insufficient reasoning about data flow and overall purpose.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled non-clone because the overall functionality (user management vs web page printing) is completely different, despite overlapping I/O patterns.
- 共享行为: Both use URL and BufferedReader to read text line by line；Both involve tokenizing or processing lines (though differently)
- 行为差异: Function A reads a local config file, while B reads a web page；Function A does user lookup and saves data, while B prints to console；Function A returns a User object, B has no return type (void)
- 修正建议: Improve training data to include more diverse non-clone pairs with API overlaps；Incorporate data-flow analysis to differentiate source and destination of read data；Use larger context or task-specific embeddings to capture overall functionality

### case_id=551 FN benchmark_preference_bias

- 方法: `MotixFileItem` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Constructor that copies an InputStream to a byte array and optionally reads an image, storing the result.
- B 摘要: Method that retrieves a resource (possibly remote) with caching, returning an InputStream.
- 静态失败原因: Static BERT/GraphCodeBERT predicted non-clone because of low token overlap (0.108) and lack of structural similarity; the model correctly identified them as different.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have considered them clones due to broad Type-4 partial functionality similarity (both deal with InputStream reading), but this is a stretch and likely an annotation error.
- 共享行为: Both involve reading from an InputStream；Both use Buffered streams
- 行为差异: Different purpose: constructor vs getter；Complex caching and HTTP handling in B absent in A；A outputs void (sets field), B returns InputStream；B handles exceptions with retries, A uses try-finally
- 修正建议: Review BCB annotation for possible mislabel；Improve model with context-aware embeddings that capture functional purpose

### case_id=552 FP lexical_or_api_overlap

- 方法: `importSequences` vs `parse`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Reads FASTA sequences from a URL, extracting names and sequences into lists.
- B 摘要: Parses tabular data from file or URL with configurable delimiters, headers, and type conversion, returning a DataSet.
- 静态失败原因: Static BERT/GraphCodeBERT models may be misled by lexical overlap ('URL', 'openStream', 'InputStream', 'tokenizer', 'readLine') and similar control flow (try-catch, while loops), failing to capture the semantic difference in data formats and output structures.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels non-clone because these functions perform fundamentally different data parsing tasks (bioinformatics sequence import vs. general tabular data parsing) despite both involving URL reading and I/O handling.
- 共享行为: Both read data from a URL or file input stream；Both use try-catch for I/O exceptions；Both involve looping over input lines or tokens
- 行为差异: A expects FASTA format (lines starting with '>'), B expects delimited tabular data；A extracts sequence names and sequences into lists, B constructs a DataSet object with columns and rows；B has extensive configuration for delimiters, headers, types, scientific notation, and dry-run mode；B uses StreamTokenizer, while A uses custom ImportHelper and StringTokenizer
- 修正建议: Use AST-based structural matching to detect differences in parsing logic；Incorporate domain-specific knowledge about data formats (FASTA vs. tabular)；Employ semantic similarity measures that consider the entire data flow and output type

### case_id=553 FN benchmark_preference_bias

- 方法: `main` vs `clonarFichero`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.2`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a URL, extracts each entry using ZipInputStream, and writes each entry to a file.
- B 摘要: Copies the contents of a file from a FileInputStream to a destination file using FileChannel.transferTo.
- 静态失败原因: Low token overlap (0.117) and focus on surface-level features; static models miss the underlying data flow and API usage patterns.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider both as file transfer operations (input to output), judging them as Type-4 weakly similar, but the functionality is quite different.
- 共享行为: Both read from an input stream and write to an output stream
- 行为差异: A reads from a URL and extracts ZIP entries; B uses direct file copy with FileChannel.；A processes multiple entries; B copies a single file.；A decompresses; B does not.
- 修正建议: Use models that capture I/O patterns and data flow graphs.；Incorporate API usage semantics (e.g., ZipInputStream vs FileChannel).；Consider structural similarity beyond token overlap.

### case_id=554 FN benchmark_preference_bias

- 方法: `doGet` vs `actionPerformed`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Handles HTTP GET requests for a portal page, involving property lookups, page retrieval, visibility checks, logging, caching, and response writing.
- B 摘要: Action listener that reads a gzip file, extracts SNP IDs, queries NCBI E-utilities via HTTP POST, and outputs the XML response to stderr.
- 静态失败原因: Static BERT/GraphCodeBERT correctly identified the high semantic dissimilarity due to diverse APIs, domain logic, and control flow, thus predicting non-clone. However, it disagreed with the BCB label, which is likely a false positive in the benchmark.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as a clone based on a very broad interpretation of 'request handling' or 'I/O with error handling', but this seems inconsistent with typical Type-3/4 criteria. Possibly an annotation error.
- 共享行为: Both use try-catch blocks for IOException；Both perform some form of I/O operation
- 行为差异: Function A is a servlet handling page rendering with complex business logic; Function B is a simple data fetch from a web service.；Function A uses multiple property lookups and page caching; Function B only reads a file and outputs stream.；Function A handles user permissions and multiple error conditions; Function B has minimal error handling.；The overall purpose and domain are completely different.
- 修正建议: Improve BCB annotation consistency by requiring higher behavioral similarity.；For models, incorporate task-specific attention to domain-specific tokens to avoid over-generalization.

### case_id=555 FP lexical_or_api_overlap

- 方法: `read` vs `loadURL`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a camera log from a URL, parses each line into CameraLogRecord objects, adds them to a list, and sorts the list.
- B 摘要: Loads a VRML file from a URL with optional authentication, writes the content to a temporary file, and updates a status label with download progress.
- 静态失败原因: Static models like CodeBERT may over-rely on lexical and API-level overlap (e.g., both use URL, BufferedReader, while loop pattern) and miss the semantic differences in data processing and purpose.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels as non-clone because the overall functionality is different: one is parsing log data, the other is downloading a VRML file. BCB style annotation does not consider this as clone.
- 共享行为: Both open a URL and read data line by line using BufferedReader；Both handle IOExceptions and close resources in finally block；Both use logging (log.info or System.out) for progress
- 行为差异: A parses each line into structured log records, B writes raw lines to a file；A uses URL.openStream(), B uses URLConnection with authentication；A sorts the records after reading, B does not sort；B updates a JLabel with download size, A does not have UI interaction
- 修正建议: Incorporate data-flow analysis to distinguish reading vs writing patterns；Use structural matching to identify output-producing operations；Train on more diverse examples of URL reading vs file downloading

### case_id=556 FP lexical_or_api_overlap

- 方法: `addDataFromURL` vs `downloadFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads text from a URL line by line and appends to internal text buffer.
- B 摘要: Downloads binary content from a URL and writes to a local file with progress tracking.
- 静态失败原因: The model likely relied on lexical and structural similarities: both use URL, InputStream, read loops, and exception handling patterns. The high-level API overlap (URL, stream reading) misled the model into thinking they are semantically similar when they perform different tasks.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely considers these non-clones because the output behavior and purpose differ: one accumulates textual content in memory, the other persists binary data to disk. While both involve reading from a URL, the core functionality is distinct.
- 共享行为: Both open a connection to a URL and read data from it using streams.
- 行为差异: A reads text line-by-line, B reads binary in chunks.；A appends to an in-memory string, B writes to a file.；A returns void, B returns boolean.；A has exception handling that prints and appends URL, B throws Exception.
- 修正建议: Improve representation of output side effects (writing to file vs. appending to string).；Incorporate data flow analysis to distinguish between in-memory accumulation and disk storage.；Add training examples that differentiate URL reading for text processing vs. file download.

### case_id=557 FP boilerplate_overlap

- 方法: `createDialogArea` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Creates a dialog area with a browser or text widget displaying license content read from a local bundle resource.
- B 摘要: Performs a Google Images search for an artist and album, parsing the HTML response to extract image URLs.
- 静态失败原因: Static BERT/GraphCodeBERT models may overemphasize token-level overlap and structural patterns (e.g., URL opening, buffered reading, try-catch-finally) while ignoring semantic context. The shared boilerplate code triggers a high similarity score even though the core tasks are unrelated.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the functions serve entirely different purposes despite sharing a common code pattern (reading lines from a URL). The overall functionality and intent differ, so BCB's broad Type-3/Type-4 criteria would not consider them clones.
- 共享行为: Both open a URL, read lines into a buffer, and close resources in a finally block.
- 行为差异: A creates UI components and sets dialog properties; B performs a web search and parses HTML.；A reads from a local bundle resource; B makes an HTTP connection to an external service.；A displays content in a widget; B stores parsed URLs in a list.；A handles license display; B handles image search.
- 修正建议: Incorporate data flow analysis to distinguish local resource access from network I/O.；Add context-aware features such as method names and type information to differentiate UI vs. search operations.；Use contrastive training to penalize matches based solely on common I/O patterns without functional alignment.

### case_id=558 FN boilerplate_overlap

- 方法: `readGeoParserResult` vs `read`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.3`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a record content, sends it to a geo parser service via HTTP XML request, parses the response XML, and returns a collection of place names with associated gazetteer IDs.
- B 摘要: Reads a skeleton file from the classpath, splits its content into sections based on '---' markers, and stores them in a list, throwing exceptions if the file is not found or section count mismatches.
- 静态失败原因: Low token Jaccard (0.137) and distinct API calls (URL vs ClassLoader, XML vs plain text) cause the model to focus on differences rather than the superficial reading-loop similarity, which is a small portion of the code.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB annotators may consider both functions as 'read and parse' operations (Type-4 functional clone), despite different domains and output types, due to the common pattern of reading lines into a buffer and then processing the content.
- 共享行为: Both read from an input stream using BufferedReader and readLine()；Both accumulate lines into a string buffer；Both handle I/O resources and close them implicitly；Both perform some form of text processing on the read content
- 行为差异: Function A sends an HTTP request to a remote service; B reads a local resource file；Function A parses XML with DocumentHelper; B splits text on '---' markers；Function A has retry logic (3 attempts) and catches exceptions; B throws exceptions；Function A returns a collection of tuples; B populates a list of sections
- 修正建议: Incorporate data-flow or control-flow awareness to capture common structural patterns like stream reading loops；Use graph-based models that can match similar AST subtrees regardless of API specifics；Add training examples of boilerplate-heavy functions to reduce false negatives

### case_id=559 FP lexical_or_api_overlap

- 方法: `main` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Generates Java adapter classes from a Prolog file by parsing it, building adapter layers, and packaging them into a JAR file with associated classes.
- B 摘要: Reads a gzipped text file containing SNP IDs and sends them as HTTP POST parameters to an NCBI E-utils URL, copying the response to stderr.
- 静态失败原因: Static BERT/GraphCodeBERT likely focused on shared tokens like 'URL', 'try', 'catch', 'IOException', 'InputStream', etc., and the presence of file/network I/O patterns, leading to a false positive. The model may not have captured the distinct high-level intent or the deep semantic structure of these complex functions.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels these as non-clones because the overall functionality and purpose are completely different; the only overlap is low-level boilerplate (exception handling, resource management), which BCB does not consider sufficient for functional similarity.
- 共享行为: Both use try-catch blocks to handle IOExceptions and print stack traces；Both involve reading from a file and making a URL connection；Both use InputStream handling and close resources
- 行为差异: Function A parses Prolog, generates adapter classes, and writes to a JAR; Function B reads SNP IDs and sends them to a web service；Function A uses complex class generation and assembly; Function B uses simple text processing and HTTP POST；Function A writes output to a file; Function B writes to stderr；Function A handles multiple command-line arguments; Function B is triggered by a GUI action
- 修正建议: Increase reliance on structural information (e.g., data flow, control flow) to distinguish different algorithms；Improve training with more non-clone pairs that share API usage but differ in purpose；Use contrastive learning to penalize false positives based on API overlap without semantic alignment

### case_id=560 FN benchmark_preference_bias

- 方法: `decodeFileToFile` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.85`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Decodes a Base64-encoded input file to an output file using buffered streams.
- B 摘要: Builds an edited version of a website from XML, properties, and file resources, writing output HTML files.
- 静态失败原因: Static BERT likely correctly identified non-clone due to low token overlap and distinct purposes; the BCB label 1 is likely a false positive in the benchmark.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider both as 'file processing' functions due to shared low-level I/O patterns and buffer usage, despite vastly different high-level semantics.
- 共享行为: Both use file I/O with buffered streams.；Both read input from files and write output to files.；Both employ try-catch-finally blocks for error handling and resource cleanup.
- 行为差异: Function A decodes Base64 data; Function B performs XML transformations and string replacements.；Function A is a simple utility with a single input/output; Function B is complex with multiple parameters and iterative processing.；Function A returns a boolean success flag; Function B throws exceptions and has no return value.
- 修正建议: Re-evaluate BCB annotation for this pair to correct the label.；Ensure that clone detection benchmarks use strict semantic equivalence criteria to avoid false positives from boilerplate overlap.

### case_id=561 FP other

- 方法: `processAddByURLSubmit` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Process a URL submission by reading its content and calling processSubmittedDoap.
- B 摘要: Handle various GUI action commands to change settings and update UI.
- 静态失败原因: The model might have been misled by common patterns like try-catch blocks or the use of 'url' in the method name, but actually the code structures are unrelated.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely labels this as non-clone because the functions perform completely different tasks with no syntactic or semantic overlap beyond generic language constructs.
- 行为差异: Function A reads from a URL and handles I/O errors; Function B handles GUI events and saves preferences.；Function A is a single-purpose method; Function B is a multi-command event handler with extensive if-else branches.；Function A uses IOUtils and StringWriter; Function B uses JFileChooser, Suku.kontroller, and UI components.
- 修正建议: Improve training data to include more diverse negative examples.；Use better representation learning to capture method-level semantics.；Consider hierarchical attention to focus on overall functionality rather than local patterns.

### case_id=562 FN benchmark_preference_bias

- 方法: `modifyApplicationMessage` vs `readAndRewrite`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Modifies a locale-specific properties file by updating or adding a key-value pair.
- B 摘要: Reads a DICOM file and rewrites it to another file, preserving pixel data.
- 静态失败原因: Static BERT (or GraphCodeBERT) likely correctly predicted non-clone because the code tokens, APIs, and data structures are almost completely disjoint (low Jaccard similarity). The model failed to align with BCB's broad semantic interpretation, possibly because it relies on surface-level features and does not capture high-level abstract patterns like 'file I/O with modification' that BCB might consider.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as a clone due to a very broad interpretation of 'file rewriting' or 'modification' functionality, possibly considering both as Type-4 semantic clones that involve reading a file, modifying/transforming its content, and writing output. However, the domains and data formats are entirely different, so this seems like an annotation error.
- 共享行为: Both perform file I/O operations (read and write).；Both handle file existence checks and error handling via exceptions.；Both use Java I/O streams and buffers.
- 行为差异: A handles text-based properties files; B handles binary DICOM medical images.；A modifies a specific message in a key-value store; B rewrites entire pixel data.；A uses plain Java I/O; B uses DICOM-specific libraries (DcmParser, Dataset).；A's logic includes conditional copy of default file; B has no such copy.
- 修正建议: Ensure benchmark annotations are consistent and avoid overly broad semantic clones.；Incorporate task-level or domain-level context into the model, e.g., by training on broader semantic labels or using program dependency graphs that capture I/O patterns.

### case_id=563 FP boilerplate_overlap

- 方法: `load` vs `getTicketsForQueue`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Downloads a pastebin paste by ID and returns the content as a string, with error handling via JOptionPane.
- B 摘要: Retrieves open tickets for a given queue name from RequestTracker API, parses ticket IDs, fetches full tickets, and returns a list, with error logging.
- 静态失败原因: The static model likely overemphasized the common boilerplate code (opening connections, reading lines, exception handling) while ignoring the distinct purpose and logic of each function.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB annotators considered these non-clones because the overall functionality (loading a paste vs. querying a ticket system) is completely different, despite some structural similarities in network I/O.
- 共享行为: Both make HTTP requests over the network；Both use BufferedReader to read line-by-line；Both have try-catch blocks for exception handling
- 行为差异: Function A downloads a single resource; Function B queries a REST API with parameters；Function A returns a plain string; Function B returns a list of complex objects (RTTicket)；Function A uses JOptionPane for error display; Function B uses logging and custom exceptions；Function B involves parsing ticket IDs and iterative fetching of tickets
- 修正建议: Enhance training data with more negative pairs that share boilerplate but differ in semantics；Incorporate structural or flow analysis to differentiate between utility functions and domain-specific logic

### case_id=564 FP lexical_or_api_overlap

- 方法: `doVersionCheck` vs `getTicketsForQueue`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Checks for a new version of jEdit by reading a version file from a URL and comparing build numbers.
- B 摘要: Retrieves open tickets for a specific queue from a Request Tracker REST API by parsing ticket IDs from HTTP response.
- 静态失败原因: Static BERT/GraphCodeBERT likely overfitted on overlapping tokens and API usage patterns (URL, BufferedReader, line.startsWith, IOException) while missing the overall semantic intent.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clone because the functionality is completely different: one checks for software updates, the other queries a bug tracking system.
- 共享行为: Both read line-by-line from an input stream (HTTP connection) and parse lines for specific prefixes.；Both use BufferedReader and handle IOException with error messages.
- 行为差异: Different purpose: version checking vs. ticket retrieval.；Different URL construction and query parameters.；Different parsing logic (looking for .version/.build vs ticket/ID).；Different exception handling and return types.
- 修正建议: Incorporate dataflow analysis to distinguish variable origins and destinations.；Use method names and docstrings as additional context.；Train on a dataset with higher diversity to avoid overfitting on superficial patterns.

### case_id=565 FP lexical_or_api_overlap

- 方法: `getPagina` vs `downloadFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches webpage content as a string from a URL, using authentication and reading lines.
- B 摘要: Downloads a file from a URL to a local destination with progress tracking, returning a boolean success indicator.
- 静态失败原因: Static BERT/GraphCodeBERT may have overemphasized the lexical overlap of URL opening and buffered reading, ignoring the different return types, side effects, and overall functionality, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels as non-clone because the functions have different return types (String vs boolean) and different intended purposes (text retrieval vs file download), with distinct side effects and control flow, despite sharing basic URL access patterns.
- 共享行为: Both open a URL connection and read data from it；Both use buffered I/O streams；Both handle network I/O operations
- 行为差异: A returns concatenated string content; B writes binary data to a file；A uses Authenticator for authentication; B does not；B has progress reporting via MessageFrame; A does not
- 修正建议: Incorporate return type and side-effect analysis into the model；Use dataflow graphs to distinguish between reading-to-string vs reading-to-file；Add training examples that differentiate similar API usage with different high-level goals

### case_id=566 FN benchmark_preference_bias

- 方法: `send` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Sends an email with given parameters using Apache Commons Email library, including setting headers, body, attachments, and sending via a thread.
- B 摘要: Launches a configuration for a NexOpen project in Eclipse, handling Maven pom files and Hibernate reverse engineering files.
- 静态失败原因: Static BERT/GraphCodeBERT correctly predicted non-clone because the token overlap is very low (0.068) and code structures are entirely different; the model likely identified the semantic gap correctly, so it did not actually fail from a semantic perspective.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled as clone due to a very broad interpretation of 'sending/launching' or due to a misannotation in the dataset; there is no meaningful functional overlap.
- 共享行为: Both use try-catch-finally blocks for error handling.；Both involve configuration-like parameters (email headers vs. project attributes).
- 行为差异: Function A sends email; function B launches an Eclipse launch configuration.；Function A uses JavaMail/Commons Email; function B uses Eclipse platform APIs and Maven.；Function A creates threads for sending; function B manipulates Eclipse resources and persistent properties.；Function A handles email-specific data (to, cc, subject, body); function B handles project-specific data (pom files, Hibernate dialect).
- 修正建议: Review BCB annotation: these functions are not clones under any standard definition.；Improve dataset curation to avoid labeling unrelated functions as clones.

### case_id=567 FN partial_functionality

- 方法: `doTransfer` vs `issueCommandToServer`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Proxies an HTTP request by copying headers and forwarding body from incoming servlet request to target URL and returning response.
- B 摘要: Sends a command to a server via HTTP POST with URL-encoded parameters and returns the response string.
- 静态失败原因: Low lexical overlap (token Jaccard 0.187) and differing API usage patterns caused the model to miss the underlying common behavior of HTTP request/response handling.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this as a clone because both functions perform HTTP communication with similar I/O stream operations, fitting a broad Type-3/Type-4 functional similarity despite differences in purpose and complexity.
- 共享行为: Both open an HTTP connection, set DoOutput/DoInput, write data to output stream, read data from input stream, and close streams.
- 行为差异: A is a full proxy with header forwarding and body streaming; B is a specific client with fixed parameter encoding.；A uses HttpURLConnection, B uses URLConnection.；A writes request body from input stream, B writes manually constructed query string.；A reads response as bytes and writes to servlet output stream, B reads as lines and returns String.
- 修正建议: Enhance model to recognize functional similarity from structural patterns of HTTP I/O, not just lexical token overlap.；Incorporate dataflow analysis to capture common sequence of network operations.；Use contrastive learning on pairs with low lexical but high functional similarity.

### case_id=568 FN partial_functionality

- 方法: `getFile` vs `persist`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies an XML attribute, and saves to a temporary file, returning the file path.
- B 摘要: Copies an input config stream to a file to persist a configuration object.
- 静态失败原因: The low token overlap (0.09) and very different high-level purposes (WSDL download vs config persist) likely led the static model to classify them as non-clones, missing the abstract commonality of stream-to-file copying.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider them clones because both functions core behavior is copying an input stream to a file output stream, a common low-level I/O pattern, and they appear in similar configuration/server contexts.
- 共享行为: Both copy an input stream to a file output stream
- 行为差异: A involves downloading, XML parsing, modification, and multiple file operations; B is a straightforward stream copy；A has extensive error handling and logging; B has minimal error handling；A returns a file path; B returns void
- 修正建议: Incorporate dataflow analysis to detect shared I/O patterns；Use code summarization to identify high-level common operations；Balance lexical features with structural similarity

### case_id=569 FN partial_functionality

- 方法: `readData` vs `retrieveQ`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Initializes multiple sets and maps from static tokenized strings and a configuration file for Tibetan transliteration.
- B 摘要: Retrieves and returns the entire content of a given URL as a string.
- 静态失败原因: Low token overlap and different vocabulary; the model likely failed to capture the functional essence due to sparse lexical similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB might consider both as 'data loading' functions that read input and populate structures, overlooking the vastly different domains and outputs.
- 共享行为: Both read data from an external source (static strings/file vs. URL) and produce output.
- 行为差异: A builds several specialized sets and maps for transliteration; B simply returns the raw content.；A's input is fixed from static fields and a file; B's input is a dynamic URL parameter.；A includes complex conditional logic and error handling; B is straightforward and linear.；A outputs to internal data structures; B returns a String.
- 修正建议: Incorporate data-flow analysis to distinguish input sources and output destinations.；Use graph-based representations that capture data dependencies and operations.；Add functional role classification features.

### case_id=570 FP lexical_or_api_overlap

- 方法: `readData` vs `extractFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Parses comma-separated strings from predefined fields into various sets and a map for input validation.
- B 摘要: Copies the content of a file (input) to another file (output) using a buffer.
- 静态失败原因: Static BERT/GraphCodeBERT might have been misled by the presence of common Java API calls like StringTokenizer, HashSet, and FileReader/FileOutputStream, leading to overestimation of similarity based on lexical tokens. The token Jaccard similarity is very low (0.03663) but the model might have been sensitive to shared API usage or the long code of function A caused poor representation.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the two functions perform entirely different tasks: data parsing vs file copy. No overlap in functionality or purpose.
- 共享行为: Both use standard Java I/O and collections (HashSet, StringTokenizer, FileReader)
- 行为差异: Function A initializes multiple sets and maps from string tokens, while Function B copies file contents byte by byte.；Function A has no file I/O; Function B deals exclusively with file I/O.；Function A involves complex parsing and condition checks; Function B is a simple loop.
- 修正建议: Improve model's ability to understand overall program flow beyond token overlap.；Use control flow and data flow analysis to distinguish parsing from I/O.；Train on more diverse examples to avoid reliance on API keywords.

### case_id=571 FP boilerplate_overlap

- 方法: `readTwitterFead` vs `readReferenceText`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.85`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a Twitter user timeline from a hardcoded URL using HTTP client and returns the response body as a string, logging errors if status code is not 200.
- B 摘要: Reads a text file from a plugin bundle path based on an identifier and returns its content as a string, throwing an exception if any error occurs.
- 静态失败原因: Static BERT models often rely on structural patterns and may overgeneralize boilerplate I/O code (read-line loop) while ignoring key semantic differences like the source of the stream and error handling semantics.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled as non-clone because the functions have fundamentally different input sources (network vs local file), different error handling behaviors, and different overall purpose despite sharing a similar reading loop structure.
- 共享行为: Both read text line by line from an input stream；Both append lines to a string buffer；Both handle I/O exceptions
- 行为差异: A makes an HTTP GET request to a specific URL, B opens a local file；A returns empty string on error, B throws NoContentException；A logs errors, B logs and then throws；A uses HttpClient, B uses URL.openStream
- 修正建议: Incorporate data flow analysis to distinguish input source types；Add negative examples where only the reading loop structure is similar but sources differ；Use type information (e.g., HttpEntity vs InputStream) to inform the model

### case_id=572 FN partial_functionality

- 方法: `main` vs `copy`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a KMZ (ZIP) file from a URL and extracts all its entries to the local file system.
- B 摘要: Copies a file from source to destination using FileChannel, creating parent directories as needed.
- 静态失败原因: Static BERT/GraphCodeBERT might have failed because it relied on surface-level lexical or syntactic similarities, such as the presence of common stream classes (FileInputStream, FileOutputStream) and loops reading data blocks. The model might have been misled by the similar I/O boilerplate (try-catch, stream closing) and not captured the overall purpose difference (ZIP extraction vs file copy).
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB might have labeled these as clones due to a very broad interpretation of 'copying' or 'file transfer', or because both involve reading and writing binary data. However, the functional difference is significant.
- 共享行为: Both perform file I/O operations involving reading from an input stream and writing to output streams.；Both handle exceptions.
- 行为差异: A downloads from a URL and extracts ZIP entries; B copies a single file locally.；A uses ZipInputStream and ZipEntry; B uses FileChannel.；A does not handle null checks; B does.；A writes multiple files; B writes one.
- 修正建议: Improve training to emphasize high-level semantic purpose over low-level I/O patterns.；Incorporate task-specific features like method name, parameter types, and overall algorithm structure.；Use more data with fine-grained functional annotations.

### case_id=573 FP boilerplate_overlap

- 方法: `getUser` vs `read`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Loads a user from a DAO by login, falling back to parsing a config file and saving the user if found.
- B 摘要: Reads a skeleton file, accumulates lines into sections separated by '---' markers, and validates the section count.
- 静态失败原因: Static BERT/GraphCodeBERT models may over-rely on lexical and API-level overlap (e.g., ClassLoader, BufferedReader, while loop) and fail to capture the deeper semantic difference in file processing logic and output behavior.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically requires at least partial functional similarity. Here, the overall purpose and data processing logic are unrelated despite some shared I/O boilerplate, so BCB correctly labels as non-clone.
- 共享行为: Both use ClassLoader.getResource() to open a URL and BufferedReader to read lines from a file.
- 行为差异: Function A returns a User object; Function B returns void and modifies internal state.；Function A parses lines by ':' delimiter and looks for a matching login; Function B delimits sections by '---' and collects them.；Function A saves a User to DAO if found; Function B throws exceptions for missing file or unexpected section count.；Function A handles a specific user lookup; Function B processes the entire file into sections.
- 修正建议: Include training examples that contrast similar boilerplate with different core functionality.；Use data-flow or control-flow features to distinguish operations on the read data.；Employ contrastive learning to penalize reliance on superficial patterns.

### case_id=574 FN partial_functionality

- 方法: `getResourceAsStream` vs `decodeFileToFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Retrieves a resource via URL with caching and returns an InputStream.
- B 摘要: Decodes a Base64-encoded file and writes the decoded content to another file, returning success flag.
- 静态失败原因: Static BERT likely focused on distinct high-level semantics (resource caching vs file decoding) and low token overlap, missing the underlying stream processing pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label as clone due to shared I/O boilerplate and stream copying pattern, despite different high-level purpose.
- 共享行为: Open input and output streams；Use buffered streams for I/O；Read data in a loop and write to output；Handle exceptions with printStackTrace
- 行为差异: A involves URL and HTTP connection with caching logic; B does Base64 decoding；A returns an InputStream; B returns a boolean；A has conditional caching based on last modified; B always decodes；B uses Base64.InputStream for decoding; A uses standard InputStream
- 修正建议: Incorporate structural or control flow similarity to capture boilerplate patterns；Use data flow analysis to recognize common I/O idioms；Add training examples of diverse I/O functions sharing stream copy logic

### case_id=575 FN partial_functionality

- 方法: `setMembers` vs `File2String`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Parses HTML from a Trac URL to extract component and priority options and stores them in arrays.
- B 摘要: Reads a file or classpath resource and returns its content as a single string, with error handling and exit on failure.
- 静态失败原因: The static model likely focused on the distinct operations (regex parsing vs concatenation) and different outputs (side effect vs return value), missing the underlying common IO reading pattern that BCB considered.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as 'reading text input and processing it line by line', accepting partial functionality similarity as a broad Type-3 clone, ignoring the different post-processing tasks.
- 共享行为: Use BufferedReader to read lines from an input stream；Handle IO exceptions with try-catch blocks
- 行为差异: A parses HTML using regex to extract option values; B simply concatenates all lines；A writes results to member arrays; B returns a string；A reads from a URL; B reads from a file or classpath resource；Error handling: A prints messages; B may call System.exit(-1)
- 修正建议: Incorporate sub-structure matching to recognize common IO patterns even when subsequent operations differ；Use dataflow analysis to identify input/output similarities at a higher level

### case_id=576 FN partial_functionality

- 方法: `readData` vs `read`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Reads hardcoded string fields containing comma-separated tokens, populates multiple sets and maps, and parses a file line-by-line to build key mappings.
- B 摘要: Reads a skeleton file from the classpath, splits it into sections delimited by '---', and validates the number of sections against an expected size.
- 静态失败原因: Static BERT models rely on surface-level tokens and AST structure; low Jaccard similarity and different control flow led to non-clone prediction, missing the high-level partial functionality similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as initialization/configuration reading functions that parse data and fill structures, accepting broad type-3/4 similarity despite low token overlap.
- 共享行为: Both involve reading and parsing input data to populate data structures.
- 行为差异: Data source: hardcoded strings vs file input；Parsing logic: tokenization vs section splitting；Output structures: many sets and maps vs list of sections；Error handling: different exceptions and conditions
- 修正建议: Use models that capture high-level intent, e.g., via documentation or data flow analysis；Incorporate task-specific knowledge about common initialization patterns

### case_id=577 FN partial_functionality

- 方法: `wordFrequency` vs `register`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.65`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches word frequency by making a web request to a query URL and parsing the response for a pattern.
- B 摘要: Registers a user by encoding password, setting authorities, calling a forum web service, persisting the user, and sending confirmation email.
- 静态失败原因: Static BERT/GraphCodeBERT models rely heavily on lexical and syntactic patterns. The low token Jaccard similarity (0.15) and different domain-specific terms (e.g., 'word', 'frequency' vs 'user', 'password') cause the model to perceive them as non-clones. The model fails to capture the abstract common pattern of network I/O with line-by-line processing due to lack of deep semantic reasoning about program flow and intent.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider these clones based on the high-level similarity of both being functions that make an HTTP request to a web service, read the response line by line, and process it while handling IOExceptions. This broad structural similarity fits the Type-3/Type-4 acceptance in BCB's annotation guidelines.
- 共享行为: Both functions open a URL connection and read lines using BufferedReader.；Both use try-catch for IOException and handle errors.；Both perform string manipulation to construct a URL before opening it.
- 行为差异: Function A searches for a specific pattern in each line and extracts a frequency integer; Function B reads the entire response line to set a forum ID.；Function A returns an integer frequency or 0; Function B returns a boolean indicating email sending success.；Function B involves object casting, password encoding, database persistence, and email sending, which are absent in Function A.；Function A's URL is constructed by replacing a placeholder; Function B's URL is built from multiple parameters including user credentials.
- 修正建议: Incorporate data flow or control flow features that highlight similar interaction patterns (e.g., URL.openStream, BufferedReader).；Use a model that can learn abstract high-level actions from API call sequences.；Enhance training data with pairs that have low token overlap but similar structural patterns.

### case_id=578 FP boilerplate_overlap

- 方法: `main` vs `copyTo`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Generates adapter classes from a Prolog file by parsing, visiting facts, and writing output to a JAR file.
- B 摘要: Recursively copies a file or directory to a destination using file channels.
- 静态失败原因: The model likely over-weighted shared low-level patterns (file handling, try-catch, recursion) and missed the high-level semantic divergence due to a lack of sensitivity to method purpose.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB annotators prioritize functional equivalence; these functions have completely different purposes despite both using file I/O, so they are correctly labeled non-clones.
- 共享行为: Both use File objects and handle file system operations.；Both have exception handling for I/O errors.；Both may iterate over files in a directory.
- 行为差异: Function A is a complex pipeline for adapter generation, while B is a simple copy utility.；A involves parsing, visiting, serialization, class writing, and resource assembly.；B only copies file content and directory structure recursively.；A's output is a JAR file with generated classes; B's output is a copied filesystem subtree.
- 修正建议: Incorporate method names and documentation into the representation.；Use data-flow or control-flow graphs to capture program logic.；Train with contrastive examples that have similar API usage but different functionality.；Add a module to detect long-range dependencies and task context.

### case_id=579 FP boilerplate_overlap

- 方法: `loadMFileViaWeb` vs `checkForUpgrade`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Loads a .m file from a web URL, parses it, and returns a UserFunction.
- B 摘要: Checks for software upgrades by querying a database and a remote server, managing UI and database updates.
- 静态失败原因: The static model likely focused on the structural overlap of URL reading and line-by-line string building, ignoring the entirely different context and purpose. The low token Jaccard suggests lexical difference, but the model may have been misled by the common I/O boilerplate.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the core functionality is completely different (file loading vs upgrade checking), despite sharing generic I/O patterns. The Broad Clone Detection style of BCB still requires similar intent, which is absent here.
- 共享行为: Both open a URL and read lines into a string using BufferedReader.；Both handle exceptions with try-catch blocks.
- 行为差异: A loads a specific file type and returns a parsed function; B performs upgrade management with database and UI operations.；A has simple I/O and parsing; B has complex logic including database queries, UI manipulation, and license validation.；A is for loading mathematical functions; B is for software upgrade checking.
- 修正建议: Incorporate data flow analysis to differentiate how read data is used (e.g., parsed vs used for DB operations).；Use method name and surrounding class context to refine semantic understanding.；Add features that capture the overall goal of the function beyond I/O patterns.

### case_id=580 FP lexical_or_api_overlap

- 方法: `perform` vs `encrypt`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Performs HTTP request handling to classify a concept by building XML, sending it to a URL, and parsing the result.
- B 摘要: Computes the MD5 hash of a string and returns the hexadecimal representation.
- 静态失败原因: The static model likely relied on overlapping tokens like 'StringBuffer', 'for', 'int', 'i', 'getBytes' and similar control flow structures, mistaking these for semantic similarity.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clones when functions have no shared functionality beyond basic syntax or structural patterns; here, the domains are completely different despite some lexical overlap.
- 共享行为: Both use loops to iterate over arrays；Both use StringBuffer to build strings；Both convert between strings and bytes
- 行为差异: Function A is a web controller handling session, parameters, and HTTP connections; Function B is a standalone utility for hashing；Function A writes to and reads from a URL connection; Function B uses MessageDigest；Function A sets session attributes and returns an ActionForward; Function B returns a hex string；Function A has extensive error handling and conditional logic; Function B simply catches an exception
- 修正建议: Improve model to capture global program semantics；Use richer representations like data flow or control flow graphs；Incorporate function-level understanding of purpose

### case_id=581 FN benchmark_preference_bias

- 方法: `doTransfer` vs `readData`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.99`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Transfers an HTTP request to a given URL, acting as a proxy.
- B 摘要: Reads a configuration file and initializes data structures for Tibetan transliteration.
- 静态失败原因: The static model correctly predicted non-clone based on low lexical overlap and distinct semantic purposes, but the BCB label is incorrect, creating a false negative.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have mislabeled this pair, possibly due to over-broad interpretation of Type-4 clones (similar functionality) or an annotation error.
- 行为差异: Function A handles HTTP request forwarding; B parses a file.；Function A uses networking classes; B uses file I/O and StringTokenizer.；Function A returns response to client; B populates internal sets and maps.
- 修正建议: Re-evaluate the BCB label for this pair; it likely should be non-clone.；Improve dataset quality by cross-checking annotations with semantic analysis.

### case_id=582 FN partial_functionality

- 方法: `sendExceptionToServer` vs `run`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends an exception report to a remote server via HTTP POST with URL-encoded parameters and processes the response.
- B 摘要: Fetches a daily trend page from a local web server via HTTP GET and reads the response without processing.
- 静态失败原因: The low token Jaccard (0.15) and limited overlapping API sequences caused the model to miss the abstract similarity in HTTP I/O behavior.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: Both functions involve network I/O and reading from a URL, which BCB may consider a Type-4 semantic clone despite differences in request construction and output handling.
- 共享行为: Both perform HTTP requests using java.net.URL；Both read the server response line by line with a BufferedReader
- 行为差异: Function A uses HTTP POST and sends complex URL-encoded data; function B uses HTTP GET with a fixed URL.；Function A processes the response to check for success; function B discards the response content.；Function A prints output based on server response; function B performs no output.
- 修正建议: Incorporate control and data flow analysis to detect similar I/O patterns.；Use code summarization to capture high-level purpose (e.g., network communication).；Consider functional similarity metrics that emphasize I/O behavior over token overlap.

### case_id=583 FN partial_functionality

- 方法: `readAndRewrite` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a DICOM file, parses it, and rewrites pixel data to another file.
- B 摘要: Retrieves a resource from a URL, caches it locally, and returns an InputStream from the cache.
- 静态失败原因: Low token Jaccard (0.078) and very different code structure; static models lack semantic understanding to match the abstract I/O pattern that BCB might consider.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled them as Type-4 because both involve reading an input stream and writing to an output stream, a common I/O pattern, despite different domains and algorithms.
- 共享行为: Both perform file I/O: reading from a source and writing to a destination using buffered streams.
- 行为差异: Different domains: medical DICOM vs HTTP caching.；Different data processing: DICOM parsing vs simple byte copying.；Different control flow: sequential rewrite vs conditional caching logic.；Different inputs: File vs String (resource name).
- 修正建议: Use flow-aware analysis to detect shared I/O operations.；Incorporate domain-specific knowledge or align abstract operations (read/write).；Train on broader functional similarity with data flow graphs.

### case_id=584 FP lexical_or_api_overlap

- 方法: `SRWGuiClient` vs `sendRequestObjectResponse`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Constructor for a simple browser that loads a URL, optionally transforms XML with XSLT, and displays HTML content.
- B 摘要: Method that sends an XML request to a servlet via HTTP, compresses it, saves the response to a file, and opens it in a browser.
- 静态失败原因: The model likely overemphasized lexical overlap (e.g., URL, InputStream, etc.) and missed the high-level semantic divergence due to limited context understanding.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clones because the functions serve entirely different roles in different systems; they are not even partially similar in functionality.
- 共享行为: Both handle URLs and perform I/O operations (reading/writing streams).
- 行为差异: Different overall purpose (GUI initialization vs. remote request-response).；Function A parses XML/XSLT and renders HTML; function B sends compressed data and saves responses to files.；Different control flow and exception handling contexts.
- 修正建议: Use control-flow or data-flow aware representations.；Include more contrastive training on pairs with high lexical but low semantic similarity.；Incorporate method-level intent or domain information.

### case_id=585 FP lexical_or_api_overlap

- 方法: `run` vs `get`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a file from classpath and sets the content to a Swing text component.
- B 摘要: Performs an HTTP GET request with custom headers and returns an array of GameRecord objects parsed from the response.
- 静态失败原因: Static BERT models rely heavily on token overlap and structural similarity. Both functions share tokens like 'URL', 'BufferedReader', 'openStream', 'readLine', and similar loop structure, which likely caused the model to overestimate their similarity while missing the distinct semantic contexts (classpath resource vs. HTTP connection).
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BigCloneBench typically requires whole-function semantic equivalence or near-identical behavior. These functions have different types of I/O, different error handling, and produce completely different outputs (UI side effect vs. data array). Thus BCB labels them as non-clones.
- 共享行为: Both open a URL-like connection and read lines using BufferedReader.；Both use a while loop to read until null.；Both process each line in some way.
- 行为差异: Function A reads from classpath resource (URL via class loader); function B makes an HTTP request.；Function A updates UI (Swing); function B returns a data array.；Function A silently catches exceptions; function B prints stack trace and returns null.；Function B filters out lines starting with '#' and decodes GameRecord; function A simply appends all lines.
- 修正建议: Incorporate data-flow and type information (e.g., which classes are used, method signatures).；Use graph-based representations that capture variable dependencies and control flow.；Train on more diverse examples where API usage differs despite similar tokens.；Consider including error handling patterns and output types as distinguishing features.

### case_id=586 FN benchmark_preference_bias

- 方法: `doGet` vs `convert`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Handles HTTP GET requests to retrieve and display a portal page with user authentication and caching.
- B 摘要: Converts ACRNEMA format files to DICOM format with pixel data handling and UID assignment.
- 静态失败原因: Given the very low token Jaccard and distinct domain-specific vocabularies, GraphCodeBERT likely correctly identified the lack of semantic overlap. The static prediction of 0 aligns with the true non-clone nature, suggesting the BCB annotation is the error.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have erroneously labeled these as clones due to a broad interpretation of 'data processing' or because both involve input/output and error handling, but the core functionality is entirely different.
- 共享行为: Both perform I/O operations with error handling
- 行为差异: Function A is a web servlet method; Function B is a file conversion method；A uses HTTP request/response objects; B uses file streams；A involves user authentication and session handling; B does not；A writes to HTTP response; B writes to output file
- 修正建议: Re-evaluate BCB annotation for this pair; consider removing from clone set；Use stricter semantic criteria in benchmark

### case_id=587 FP partial_functionality

- 方法: `getLinksFromURLFast` vs `readURL`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Parses HTML from a URL to extract links and their text, returning two vectors.
- B 摘要: Reads a URL and prints each line to console, no data returned.
- 静态失败原因: The models likely over-relied on surface-level similarities (URL opening, BufferedReader, InputStreamReader) and missed the critical difference in final data processing (link extraction vs. print). The token-level overlap in I/O patterns may dominate the representation.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely labeled non-clone because the overall functionality differs significantly: one is a link extractor, the other is a simple URL printer. The shared I/O boilerplate does not override the distinct purpose.
- 共享行为: Both open a URL and read its content line by line using BufferedReader.
- 行为差异: A extracts links via regex and returns them, B prints lines to console and returns void.；A builds a Vector[] for links and texts, B does not.；A uses timeCheck for profiling, B has try-catch-finally for resource cleanup.；A takes a String URL, B takes a URL object.
- 修正建议: Incorporate control flow and data flow features to distinguish return-structure building from simple printing.；Use method name semantics or embedding to capture intent.；Add explicit checks for return types and output operations.

### case_id=588 FN partial_functionality

- 方法: `login` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Logs in to a service via HTTP POST, sends encoded credentials, reads response, extracts and returns session ID.
- B 摘要: Fetches a webpage via HTTP GET, reads lines and prints them, closes connection.
- 静态失败原因: Static BERT or GraphCodeBERT likely relied on token-level similarity (Jaccard 0.19) and method names ('login' vs 'main'), missing the underlying functional pattern. The models may be sensitive to surface differences like try-catch vs throws, and lack understanding of broader I/O roles, causing a false negative.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB's broad Type-3/Type-4 criteria often accept functions that share a common high-level pattern, such as 'HTTP client reading response from URL'. Despite different application details, both demonstrate the same core sequence: open URL, get input stream, read lines, close. This structural and semantic overlap may justify a clone label.
- 共享行为: Both open a URL connection and read from it using BufferedReader；Both close the reader after reading；Both use standard Java I/O and networking classes
- 行为差异: A writes form data to the output stream (POST request); B only reads (GET request)；A extracts and returns a session ID; B prints all response content；A uses try-catch for exception handling; B throws IOException；A uses URLEncoder for parameter encoding; B does not
- 修正建议: Incorporate data-flow analysis to capture shared I/O patterns；Use contrastive learning on examples with similar high-level tasks (e.g., 'URL reading' functions)；Enhance the model with type or API usage embeddings (e.g., distinguish GET vs POST but recognize common stream usage)

### case_id=589 FP boilerplate_overlap

- 方法: `main` vs `download`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Parses a Prolog file, generates adapter classes, and writes them to a JAR file.
- B 摘要: Downloads a resource file from the classpath to a user-specified file location using a save dialog.
- 静态失败原因: Static BERT/GraphCodeBERT may have been misled by the shared I/O boilerplate (try-catch-finally, stream copy, close) and exception handling patterns, which are common in Java code but not indicative of semantic similarity. The model may over-rely on syntactic patterns without understanding high-level intent.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels as non-clone because the functions have completely different high-level purposes and no shared functionality beyond generic I/O patterns. Token Jaccard is very low (0.056), and BCB emphasizes semantic equivalence over structural overlap.
- 共享行为: Both use file I/O operations with streams.；Both handle IOExceptions in try-catch-finally blocks.；Both close streams in finally blocks.
- 行为差异: A is a complex multi-step code generation pipeline; B is a simple file copy utility.；A involves Prolog parsing, class generation, and JAR writing; B involves resource loading and file dialogs.；A is a static main method with command-line arguments; B is a private instance method with a String parameter.；A has far more dependencies and logic; B is straightforward.
- 修正建议: Incorporate dataflow analysis to differentiate the high-level operations (e.g., code generation vs. file copy).；Train with more non-clone pairs that share boilerplate but differ in purpose.；Use type information and method dependencies to capture the broader context.

### case_id=590 FN partial_functionality

- 方法: `main` vs `read`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: A main method that constructs a POST request with parameters and sends it to a RenRen API, printing the response.
- B 摘要: A method that reads a file resource, splits it into sections delimited by '---', and stores them in a list.
- 静态失败原因: Static BERT models rely heavily on token overlap and lexical similarity; low Jaccard (0.14) and different method names/contexts cause the model to miss the abstract I/O reading pattern shared.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as performing I/O operations involving URL and BufferedReader, thus accepting broad Type-3/4 similarity despite different domains.
- 共享行为: Both use BufferedReader to read line by line from an InputStream；Both use URL and openConnection/openStream；Both handle IOException
- 行为差异: A sends a network POST request; B reads a local resource file；A prints output; B builds a list of sections；A uses specific API constants; B uses class loader；A has no section parsing; B splits on '---' delimiter
- 修正建议: Incorporate control flow and data flow features via graph-based models (e.g., CodeGraph)；Use contrastive learning on I/O patterns to recognize common stream reading；Add training samples of diverse I/O operations sharing similar loop structure

### case_id=591 FN lexical_or_api_overlap

- 方法: `getDatasetsList` vs `getHTML`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads lines from a URL that returns a list of dataset names, caches them, and returns the list.
- B 摘要: Reads HTML content from a URL, optionally writes to a file, and returns the HTML string.
- 静态失败原因: Static BERT is sensitive to surface-level differences like method names, parameters, return types, and string literals, leading to low token Jaccard (0.2125) and failing to capture the underlying common I/O structure.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB often labels clones based on structural similarity and common I/O patterns; both functions exhibit the same 'read from URL line by line' pattern, which is considered a clone in BCB's annotation.
- 共享行为: Both open a URL connection and read lines via BufferedReader；Both handle exceptions and cleanup resources in finally block
- 行为差异: Return type differs (List<String> vs String)；A caches results in a HashMap; B does not cache；A appends query parameter '?server=list'; B sets User-Agent header；B optionally writes to a file; A does not
- 修正建议: Use data flow or control flow features to detect common I/O patterns；Incorporate structural similarity beyond token overlap；Train models on broader clone types like Type-3/Type-4

### case_id=592 FP lexical_or_api_overlap

- 方法: `readZoneIDs` vs `checkForUpgrade`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads zone IDs from a resource file and returns them as a set of integers.
- B 摘要: Checks for software upgrades by querying a database and a remote server, then updates UI components and database records accordingly.
- 静态失败原因: The static model likely focused on overlapping API usage patterns (URL, InputStream, readLine) and boilerplate code, ignoring the vast semantic differences. The low token Jaccard (0.077) suggests the model might have been misled by the presence of identical or similar keywords like 'URL', 'InputStreamReader', 'line', etc., without understanding context.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB correctly labels this as non-clone because the functions have entirely different purposes and only superficial API similarities. The BCB preference for broad similarity (Type-3/4) still requires some functional overlap, which is absent here.
- 共享行为: Both use URL and InputStreamReader/BufferedReader to read data from a URL or resource.；Both have try-catch or exception handling (code_a catches Exception, code_b throws Exception).
- 行为差异: Code_a reads from a local resource file, code_b reads from a remote URL via HTTP.；Code_a simply parses integers and stores in a HashSet; code_b performs complex upgrade logic, database operations, UI updates, and license validation.；Code_a is static and stateless; code_b modifies UI and database state.；Code_a has no loops other than reading lines; code_b has multiple loops and conditionals for parsing XML-like data.
- 修正建议: Incorporate structural information like abstract syntax trees (AST) or data flow graphs.；Add semantic features such as method name and comment analysis.；Use contrastive learning to penalize superficial API overlap without semantic alignment.

### case_id=593 FP boilerplate_overlap

- 方法: `readIntoList` vs `getFullScreenUrl`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads HTML from a URL and populates a map with JMenuItem entries, each with an action command and listener.
- B 摘要: Reads HTML from a YouTube URL, extracts fullscreen URL parameters, and returns a full video URL.
- 静态失败原因: Static BERT/GraphCodeBERT models may have been misled by high lexical overlap: both use URL, BufferedReader, while loop, try-catch, and string parsing operations. They lack understanding of the overall intent and output type.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically requires functional similarity; these two methods serve entirely different purposes (GUI building vs. video URL extraction). The shared boilerplate (URL reading) is insufficient for a clone annotation.
- 共享行为: Both open a URL connection and read lines with BufferedReader；Both use a while loop to iterate over lines；Both parse strings using indexOf or contains；Both catch exceptions generically
- 行为差异: Function A creates and populates a GUI menu with JMenuItems; function B extracts video metadata and constructs a URL string；Function A adds action listeners to menu items; function B prints debug info and updates a progress bar；Function A writes to a Map parameter; function B returns a String；Function A's parsing extracts command names from HTML links; function B's parsing extracts video_id and t from a specific line containing 'fullscreenUrl'
- 修正建议: Add a type-check on return values or parameters to distinguish side-effect vs. pure return；Include method signature context (name, return type) more explicitly in the model；Train on more diverse negative pairs that share API usage but differ in purpose；Use a contrastive loss that penalizes similarity for methods with different output domains

### case_id=594 FP partial_functionality

- 方法: `getTicketsForQueue` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Connects to a REST API to search for open tickets in a queue, parses response to extract ticket IDs, retrieves each ticket, and returns a list of RTTicket objects.
- B 摘要: Searches Google Images via HTTP, parses HTML to extract image URLs, stores them in a global list, and updates a GUI component with an image.
- 静态失败原因: The model likely overemphasized the shared structural patterns (HTTP request, try-catch, BufferedReader/InputStreamReader) and ignored the domain-specific semantics and different return types/global state modifications.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely labels this as non-clone because the two functions have different purposes (ticket management vs. image search) and different output behavior (return list vs. void with GUI update), despite sharing some boilerplate HTTP reading patterns.
- 共享行为: Both perform HTTP requests；Both use BufferedReader/InputStreamReader to read response；Both have exception handling with try-catch
- 行为差异: Function A returns a list of ticket objects; Function B is void and modifies global state/GUI；Function A uses a specific REST API (RT); Function B scrapes Google Images；Function A processes structured text (ticket IDs); Function B parses HTML for image URLs；Function A uses a helper method to retrieve individual tickets; Function B directly manipulates GUI components
- 修正建议: Incorporate data-flow analysis to distinguish between different API endpoints and data processing；Use type information and method signature to disambiguate different functionalities；Train on more diverse examples to reduce bias toward common I/O patterns

### case_id=595 FP lexical_or_api_overlap

- 方法: `readUNI` vs `GetResponse`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a TSV file from a URL and extracts ID and description pairs into a vector.
- B 摘要: Sends an HTTP GET request to a URL and returns the concatenated response content.
- 静态失败原因: The static BERT model likely over-relied on overlapping tokens like 'URL', 'openStream', 'readLine', and exception types, which are common boilerplate, ignoring the different data processing logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically considers functions with different input processing and output semantics as non-clones, even if they share some technical details like URL opening and exception handling.
- 共享行为: Both open a URL and read stream data line by line.；Both handle MalformedURLException and IOException.
- 行为差异: A parses tab-separated lines into structured data; B simply concatenates all lines.；A uses Scanner with delimiter; B uses BufferedReader with readLine.；A writes to an output vector; B returns a string.；A explicitly uses URL.openStream(); B uses HttpURLConnection with GET method.
- 修正建议: Include dataflow or control flow analysis to distinguish parsing vs. raw reading.；Use program dependence graphs to capture variable transformations.；Consider output types and post-processing steps.

### case_id=596 FN long_range_semantics

- 方法: `getResourceAsStream` vs `saveFileData`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.6`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Retrieves a resource as an InputStream, with caching, HTTP handling, and local file storage.
- B 摘要: Saves file data by copying a working file to a destination and optionally writing new data, with image metadata extraction and thumbnail cleanup.
- 静态失败原因: The static BERT/GraphCodeBERT model relied on lexical and syntactic similarity (token Jaccard=0.1) and method name difference, missing the deeper functional similarity in file handling and data flow. It failed to capture the long-range semantic commonality of reading from a source and writing to a destination.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB annotators likely considered both as 'file resource management' functions that involve data transfer from a source to a destination, and both implement caching-like behavior (A caches, B overwrites). They may have focused on the shared lower-level pattern of reading from a source and writing to a file, ignoring the high-level purpose differences.
- 共享行为: Both perform file I/O operations (reading/writing bytes).；Both check for file existence and create directories as needed.；Both use buffered streams/channels for efficient data transfer.
- 行为差异: Function A is for resource retrieval with caching; B is for saving file data with optional overwrite.；Function A includes HTTP-specific logic; B includes image dimension processing and thumbnail deletion.；Function A returns an InputStream; B returns void.；Function A has extensive exception handling with multiple close attempts; B throws Exception externally.
- 修正建议: Incorporate data flow analysis to detect common patterns of reading and writing.；Use code summarization or topic modeling to capture high-level purpose.；Augment training data with pairs that share low-level operations but differ in goal.

### case_id=597 FN partial_functionality

- 方法: `getResourceAsStream` vs `copyLogic`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.65`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Retrieves a resource from a URL, caches it locally, and returns an InputStream with HTTP and caching logic.
- B 摘要: Copies a .class file from a source to a destination path using FileChannel.transferTo with state management.
- 静态失败原因: Static BERT/GraphCodeBERT likely failed because it relied on lexical overlap of file I/O tokens (e.g., FileInputStream, try-catch) and missed the distinct high-level semantics and different control flow patterns.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider them clones due to partial functionality overlap (both copy data from source to destination) and similar boilerplate code for resource handling and exception management.
- 共享行为: Both involve file I/O operations.；Both use try-catch blocks with exception printing.；Both close streams/channels in finally or catch blocks.；Both involve reading from a source and writing to a destination.
- 行为差异: A handles remote resources via HTTP and caching; B copies local files with channel transfer.；A uses InputStream and caching logic; B uses FileChannel and state machine.；A has conditional logic based on cache existence and HTTP response; B has a simple copy with state transitions.；A returns an InputStream; B is void.
- 修正建议: Incorporate data-flow analysis to distinguish file copying from caching.；Add more training examples with varied I/O patterns to avoid overfitting on boilerplate.；Use contrastive learning to emphasize intent differences even with similar surfaces.

### case_id=598 FP lexical_or_api_overlap

- 方法: `main` vs `copy`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.98`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a Prolog file, parses it, generates adapter classes, and writes them to a JAR file with error handling and optional debug output.
- B 摘要: Copies a file from source to destination using a 1024-byte buffer, throwing an IOException if the source does not exist.
- 静态失败原因: The static model likely over-relied on lexical and API-level overlap (e.g., 'File', 'IOException', 'while', 'fis.read', 'fos.write' in B vs similar patterns in A's file reading/writing) and missed the vast difference in overall control flow and semantic intent.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels as non-clone because the functions have entirely different purposes and implementations; no partial functionality match even under lenient Type-3/4 definitions.
- 共享行为: Both operate on files；Both handle I/O exceptions
- 行为差异: Complex adapter generation vs simple byte copying；A uses multiple libraries and steps, B is straightforward；A outputs a JAR and resources, B outputs an exact file copy；A has extensive error handling and logging, B throws exceptions
- 修正建议: Incorporate data-flow analysis to distinguish simple copy from multi-step generation；Use code summarization to capture high-level purpose；Increase weight on structural differences like number of classes/methods used

### case_id=599 FN benchmark_preference_bias

- 方法: `run` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Parses XML menu and generates a ZIP archive containing XUL overlay files and resources.
- B 摘要: Implements a caching mechanism for retrieving resources as streams, downloading from URLs if not cached.
- 静态失败原因: Static BERT failed to recognize the broad I/O similarity because it focused on the low token overlap and different method names, missing the overarching pattern of resource fetching and writing.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider them clones due to both being involved in resource handling and stream I/O, though the functionalities are at different abstraction levels.
- 共享行为: Both perform I/O operations involving streams and files.
- 行为差异: Function A generates a specific ZIP archive from XML input, while B is a generic caching resource fetcher.；A uses getResourceAsStream, B defines it.；A writes to ZipOutputStream, B writes to local file cache.；A has no caching logic, B implements caching.
- 修正建议: Include training examples that highlight functional similarity despite different method names and code structures.；Incorporate higher-level semantic representations that capture I/O operations and resource management.

### case_id=600 FN partial_functionality

- 方法: `getHTML` vs `postRequest`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetch HTML from a URL with optional file saving.
- B 摘要: Send POST request with data and return response.
- 静态失败原因: Low token overlap (0.275) and different API calls (HttpURLConnection vs URLConnection, PrintWriter vs BufferedReader) led the model to focus on surface-level differences, missing the shared higher-level functionality of fetching web content.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels as clone pairs that share the core task of making an HTTP request and reading the response, considering differences like GET vs POST or additional file writing as minor variations.
- 共享行为: Both make an HTTP connection to fetch data from a URL.；Both read the response line by line and accumulate into a string.；Both catch exceptions and print stack trace.；Both return the response content as a string.
- 行为差异: A uses GET (no explicit POST) while B explicitly performs a POST request.；A optionally writes response to a file, B does not.；A sets User-Agent header, B does not.；A allows specifying encoding, B uses default.
- 修正建议: Incorporate more structural representations like AST or data-flow graphs to capture common patterns (open connection, read, return).；Train on more examples of HTTP client functions with varying implementations.；Use contrastive learning to emphasize behavioral similarity over lexical similarity.

### case_id=601 FN partial_functionality

- 方法: `runInternal` vs `getXML`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Fetches an OPDS catalog from a URL with full HTTP handling, parsing XML entries, pagination, and optional book download.
- B 摘要: Performs a simple HTTP GET request and returns the response body as a string, with minimal error handling.
- 静态失败原因: Low token overlap and structural differences caused the model to predict non-clone. The model likely missed the high-level similarity in the URL fetching operation, as it focuses on exact syntax and control flow.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider the common pattern of URL connection and stream reading as a Type-4 semantic clone, but the actual functionality differs significantly beyond that shared step.
- 共享行为: Both open a URL and read data from it via an input stream.
- 行为差异: Function A sets up HTTP connection properties (User-Agent, timeouts, redirects) while B uses default settings.；Function A parses XML and processes entries, including pagination and book download; B only reads raw text.；Function A has complex error handling with callbacks and progress reporting; B returns null on exceptions.；Function A checks response codes and content types; B does not.
- 修正建议: Enhance the model to recognize core API usage patterns (e.g., URL openConnection, InputStream) regardless of surrounding logic.；Include a semantic role labeling of library calls to identify shared functional tasks.

### case_id=602 FN partial_functionality

- 方法: `copyResource` vs `copyDeleting`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource (URL or file) to a destination file byte by byte, with explicit resource existence checks.
- B 摘要: Copies a file to another file using a buffered stream with proper resource management.
- 静态失败原因: Static BERT/GraphCodeBERT methods may have focused on token-level differences (e.g., different method names, different buffer usage, URL handling) and the low Jaccard similarity, leading to a non-clone prediction. They may not capture the higher-level semantic intent of copying data.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider them clones because the core functionality of copying data from an input to an output is the same, despite differences in source type, buffer size, and error handling. BCB often accepts partial functionality similarity and broad Type-3/4 clones.
- 共享行为: Both copy data from a source to a destination file.；Both read from an input stream and write to an output stream.
- 行为差异: A uses byte-by-byte copying, B uses buffered copying.；A handles both URL and local file sources, B only local files.；A does not use try-finally for resource closing, B does.；A throws generic Exception, B throws IOException.
- 修正建议: Train on more diverse Type-3/4 clones with low token overlap.；Incorporate structural features like control flow and data flow to recognize similar IO patterns.；Use contrastive learning to emphasize semantic similarity over lexical similarity.

### case_id=603 FN benchmark_preference_bias

- 方法: `readAndRewrite` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Reads a DICOM image file, parses pixel data, and writes to an output file.
- B 摘要: Launches a NexOpen project configuration by reading pom.xml files, setting Hibernate properties, and installing the project.
- 静态失败原因: Static BERT likely correctly predicted non-clone due to very low token overlap (Jaccard 0.0317) and distinct APIs. The model did not fail; the BCB label appears to be an outlier or misannotated.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as a clone due to both methods performing file reading and writing, albeit in completely different domains, reflecting a very broad Type-4 interpretation.
- 共享行为: Both involve file I/O operations using streams.
- 行为差异: Function A is a DICOM image conversion; function B is an Eclipse project setup.；Function A uses DICOM-specific APIs; function B uses Eclipse/Java development APIs.；Function A has a linear flow; function B has conditional checks and nested callbacks.
- 修正建议: Re-evaluate this pair in BCB; likely should be relabeled as non-clone.；Use domain-specific filtering to avoid unrelated pairs.

### case_id=604 FP boilerplate_overlap

- 方法: `executeHttpGet` vs `importSequences`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Makes an HTTP GET request and returns the response body as a JSONObject.
- B 摘要: Imports sequences from a FASTA-format URL and stores names and sequences in lists.
- 静态失败原因: The static model likely overemphasized common programming patterns like reading input, building strings, and exception handling, ignoring the distinct domain-specific logic and data transformations.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would label as non-clone because the overall functionality of HTTP GET and JSON parsing is completely different from importing FASTA sequences; no shared intent.
- 共享行为: Both read from an input stream and build a string or accumulate data；Both handle IOException
- 行为差异: Different data sources (HTTP vs URL stream)；Different parsing logic (JSON vs FASTA)；Different return types (JSONObject vs void with side effects)
- 修正建议: Add training examples that distinguish between generic I/O patterns and domain-specific processing；Incorporate method name and context encoding to differentiate purpose；Use dataflow analysis to capture transformation differences

### case_id=605 FP lexical_or_api_overlap

- 方法: `run` vs `importSequences`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a URL line by line, parsing the first two lines as version and URL, and appending the rest to an information string, with error handling and listener notification.
- B 摘要: Reads a URL stream using ImportHelper to parse biological sequences in FASTA-like format, extracting sequence names and sequences into lists.
- 静态失败原因: Static BERT models may over-rely on shared API tokens like 'openStream', 'readLine', and 'IOException', ignoring the fundamentally different control flow and data usage.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels non-clone because the high-level purpose and detailed parsing logic are entirely different, even though both involve reading from a URL.
- 共享行为: Both open an InputStream from a URL；Both use try-catch for IOException；Both read input line by line or character by character
- 行为差异: Different parsing logic: first two lines vs. FASTA delimiter '>'；Different output: one sets version/url/informations, the other populates names and sequences lists；Different error handling: one sets error flags and translates messages, the other catches multiple exception types without action
- 修正建议: Use dataflow analysis to compare the actual data manipulation beyond API calls；Incorporate program structure representation (e.g., AST subtree matching) to detect differing parsing patterns；Train on more diverse non-clone pairs sharing common I/O patterns

### case_id=606 FN benchmark_preference_bias

- 方法: `populateResources` vs `readData`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Loads template files and image resources from classpath, reads file contents, and persists them as Resource and Image objects.
- B 摘要: Tokenizes comma-separated strings and reads a configuration file to populate character sets and mapping tables for Tibetan transliteration.
- 静态失败原因: Static BERT models correctly identified low token overlap and distinct logic, predicting non-clone; they did not fail in this context, but the BCB label is questionable.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB likely considered both as 'initialization/loading' functions, ignoring the different domains and specific operations, leading to a Type-4 (semantically similar) annotation, though the semantics diverge significantly.
- 共享行为: Both read from external inputs (classpath resources vs string tokens and file).；Both perform loops and populate data structures.；Both involve string processing and conditional checks.
- 行为差异: Function A focuses on saving resources to a database; Function B builds in-memory sets and maps.；Input sources differ: classpath URLs vs static string fields and a text file.；Function A handles image property creation; Function B handles character encoding tables.；Overall purpose is completely different: resource loading vs transliteration data initialization.
- 修正建议: Re-evaluate BCB annotation for this pair; consider stricter semantic criteria.；Train classifiers to focus on specific behavioral patterns rather than broad task categories.；Use domain-aware tokenization or structural features to differentiate loading from different domains.

### case_id=607 FN partial_functionality

- 方法: `getWebByUrl` vs `seeURLConnection`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Opens a URL, reads content line by line, writes to file, optionally recurses for links, logs and reports success/failure.
- B 摘要: Opens a hardcoded URL, reads content line by line, logs the concatenated string.
- 静态失败原因: Low lexical overlap (token Jaccard 0.2375) due to different variable names and additional functionality in A; static BERT models rely on surface-level similarity and fail to capture the shared URL-reading API calls across long functions.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: None
- 共享行为: Both open a URL connection.；Both read lines from the input stream using BufferedReader.；Both use StringBuffer to accumulate the content.
- 行为差异: A writes the content to a file; B only logs.；A recursively processes links from the page; B does not.；A has custom error handling with logging and reporting; B throws Exception.；A takes parameters for URL, charset, and file index; B hardcodes the URL.
- 修正建议: Use API call sequence features to match core I/O operations.；Normalize variable names and remove peripheral code (file I/O, recursion) before comparison.；Incorporate dataflow analysis to identify shared structure (open, read, close).

### case_id=608 FP lexical_or_api_overlap

- 方法: `get` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Makes an HTTP GET request with location headers to retrieve game records, parses lines not starting with '#' into GameRecord array.
- B 摘要: Constructs a Google Images search URL, fetches HTML, extracts image URLs from href attributes, adds them to a list.
- 静态失败原因: Static BERT-based models often rely heavily on lexical and structural overlap. The functions share common API usage patterns (HttpURLConnection, BufferedReader, reading lines), which inflate similarity scores despite different semantic intents. This leads to a false positive prediction.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this non-clone because the core functionality is different: one retrieves game records with location-based queries, the other searches Google Images for album art. The overlap in HTTP setup is considered boilerplate, not sufficient for a positive clone label, especially given the low token Jaccard similarity.
- 共享行为: Both use HttpURLConnection to perform HTTP GET requests.；Both read the response line by line using BufferedReader.；Both handle exceptions (IOException/Exception) and print stack traces or show error dialogs.
- 行为差异: Function A uses custom request headers for latitude, longitude, and count; function B sets a User-Agent header.；Function A filters lines starting with '#' and decodes them to GameRecord; function B concatenates all lines and parses HTML for image URLs.；Function A returns an array of GameRecord; function B updates a list of image URLs and returns void.；Function A is static; function B is an instance method that depends on object state (artist, previousArtist, currentTrack).
- 修正建议: Incorporate data flow analysis to trace how the response is processed beyond the connection setup.；Use contrastive learning to penalize similarity from common boilerplate code.；Include type and method signature differences (return type, parameters) as strong signals.；Employ program slicing to isolate the core logic from infrastructure code.

### case_id=609 FN partial_functionality

- 方法: `addIDs` vs `getXML`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Parses a GMD web page for metabolite IDs and scores, updating a PeakListRow.
- B 摘要: Performs an HTTP GET request and returns the response body as a string.
- 静态失败原因: Static BERT likely focused on token-level overlap, which is low, and missed the high-level functional similarity of HTTP communication. The model may not capture long-range control flow and data dependencies that differentiate the specialized parsing from generic retrieval.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider them clones due to shared structural pattern of HTTP GET and line-by-line reading, common in data retrieval tasks, and both are related to web service interaction.
- 共享行为: Both open an HTTP URL and read lines from the input stream；Both handle IOException；Both use BufferedReader and InputStreamReader
- 行为差异: addIDs parses HTML for specific metabolite identifiers and updates a data structure; getXML simply concatenates raw response lines；addIDs returns an integer score parsed from the page; getXML returns the full response string；addIDs has complex conditional logic for different ID types and multiple setVar calls; getXML is a straightforward loop
- 修正建议: Incorporate structural information like AST or CFG to capture program logic beyond tokens；Use models that learn from API call sequences and data flow, e.g., GraphCodeBERT with semantic edges；Augment training data with examples of similar structure but different semantics

### case_id=610 FN boilerplate_overlap

- 方法: `readGeoParserResult` vs `load`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a record content, constructs an XML request for a geolocation parser, sends it via HTTP, parses the response XML, and returns a collection of tuples each containing a place name and associated gazetteer IDs.
- B 摘要: Downloads the content of a pastebin entry given an ID by constructing a URL, reading the response line by line, and returns the concatenated XML string.
- 静态失败原因: Static BERT or GraphCodeBERT likely focused on token-level and structural similarities from common API calls (URL, BufferedReader, etc.) and the overall try-catch pattern, but missed the deeper semantic differences in data processing and return types. The model may have been confused by the overlapping boilerplate code, leading to a false negative prediction.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may consider these clones due to the high-level similarity in the pattern of opening a URL, reading data, and handling exceptions, even though the detailed functionality and return types differ. The broad Type-3/Type-4 definition in BigCloneBench often accepts partial functionality similarity, especially when both methods involve I/O operations with similar control flow structures.
- 共享行为: Both open a URL and read the response line by line using BufferedReader.；Both handle exceptions (print error messages) and return a default value on failure.；Both involve network I/O operations that may fail.；Both construct a URL string with a parameter.
- 行为差异: Function A uses a retry loop (up to 3 times) on failure, while Function B does not retry.；Function A constructs an XML request body and sends it as part of the URL query parameter, while Function B directly accesses a download URL.；Function A parses the response XML to extract specific elements and builds a collection of tuples, while Function B simply concatenates all lines and returns the raw XML string.；Function A has a testing mode that returns a fixed dummy result, while Function B does not have such a mode.
- 修正建议: Incorporate data flow analysis to capture how inputs are transformed and what specific operations are performed on the data.；Use a more fine-grained semantic representation that distinguishes between different XML processing tasks.；Introduce context about the overall purpose of the method (e.g., using docstrings or additional structural annotations).

### case_id=611 FP boilerplate_overlap

- 方法: `downloadURLtoString` vs `getLinksFromURLFast`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Downloads the content of a URL and returns it as a single string.
- B 摘要: Downloads a web page from a URL, extracts all hyperlinks and their text, and returns them as two vectors.
- 静态失败原因: The static model focused on the shared boilerplate (BufferedReader, StringBuffer, while loop) and common API usage (URL, InputStreamReader), but missed the divergent final transformations and overall functionality.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels as non-clone because the functions have fundamentally different purposes (download vs. link extraction), different return types, and the shared boilerplate code is not sufficient to deem them clones.
- 共享行为: Both open a URL and read lines from the response into a StringBuffer.
- 行为差异: Function A returns the raw page content as a String; Function B parses links from the content and returns two Vectors.；Function A has simple I/O error handling; Function B includes timing checks and regular expression parsing.；Function B converts relative URLs to absolute and filters mailto links.
- 修正建议: Train on more diverse examples where boilerplate differs from core logic.；Incorporate dataflow or graph-based analysis to track output transformations.

### case_id=612 FP lexical_or_api_overlap

- 方法: `read` vs `readUNI`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a skeleton file from a URL, splits it into sections separated by '---', and validates section count.
- B 摘要: Reads a tab-separated file from a URL, parses each line to extract ID and description, and adds them to a vector.
- 静态失败原因: The model likely relied on lexical overlap (e.g., URL, InputStream, reader) and the void return type, ignoring the distinct parsing logic. The token Jaccard similarity is low (0.18), suggesting the model may have been misled by structural patterns like loop and control flow.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would likely label these as non-clones because despite both reading from URLs, their core functionality (parsing and output) is entirely different. The shared behavior is merely boilerplate I/O.
- 共享行为: Both open a URL and read lines；Both use InputStream and handle I/O；Both ignore certain lines (first line in B, '---' lines in A)
- 行为差异: Different parsing logic: A splits by '---', B splits by tab；Different output: A accumulates sections in a list, B adds parsed strings to a vector；Different error handling: A throws exceptions, B catches and prints stack trace；Different file format expectations: A expects a skeleton with predefined sections, B expects TSV with specific column order
- 修正建议: Increase negative examples with similar I/O boilerplate but different core logic；Incorporate dataflow analysis to distinguish output structures；Use contrastive learning with hard negatives

### case_id=613 FP lexical_or_api_overlap

- 方法: `readPage` vs `getTicketsForQueue`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a URL and returns its content, optionally skipping comment lines starting with '#'.
- B 摘要: Queries a ticket system for open tickets in a queue, parses ticket IDs from response, then fetches each ticket and returns a list.
- 静态失败原因: The static model likely focused on the shared syntactic pattern of opening a BufferedReader over an HTTP response and reading lines in a loop, ignoring the different loop body logic and the broader context of the functions.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels as non-clone because the functions have entirely different purposes and outputs, despite both involving HTTP I/O. The core functionality (page reading vs ticket querying) is not similar.
- 共享行为: Both read lines from an HTTP response using BufferedReader and handle I/O exceptions.
- 行为差异: Different input parameters and output types (String vs List<RTTicket>).；Different data processing: one concatenates lines, the other extracts IDs and fetches additional data.；Different error handling and exception propagation.；One is a simple read operation, the other involves multiple HTTP requests (fetching individual tickets).
- 修正建议: Train models to be sensitive to differences in data flow and control flow within loops.；Incorporate structural information like method signatures and call graphs to distinguish similar API usage patterns.；Use dataflow analysis to track how input/output types interact with processing logic.

### case_id=614 FP lexical_or_api_overlap

- 方法: `run` vs `issueCommandToServer`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches a geospatial tile from a URL, reads it as GeoJSON, processes it into geometry objects, and adds them to a map layer with deduplication logic.
- B 摘要: Sends a command and data to a server via HTTP POST, reads the response, and returns it as a string.
- 静态失败原因: Static BERT/GraphCodeBERT may have misclassified due to overlapping API calls (URL, BufferedReader, readLine) and the common while-loop pattern, ignoring the overall business logic and different return types/uses. The model likely over-generalized from training data where such I/O patterns were associated with clones.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the functions have different high-level purposes and domain contexts, despite sharing a common I/O reading pattern. The low lexical similarity (Jaccard=0.0889) and distinct semantics argue against a Type-4 functional equivalence.
- 共享行为: Both use URL/URLConnection to access a network resource.；Both read input using BufferedReader and readLine() in a loop.；Both accumulate lines into a string buffer.；Both handle I/O operations and may throw IOException.
- 行为差异: Function A is a run() method without return; B returns the response string.；A has synchronization and deduplication of requests; B does not.；A can read from file or HTTP; B only does HTTP POST.；A processes the response into complex geometry objects; B returns raw response.
- 修正建议: Incorporate data-flow analysis that tracks how the read data is used (e.g., processed into geometries vs. returned directly).；Add features capturing the method's return type and side effects (e.g., synchronization).；Use larger context windows or graph representations that include method signatures and surrounding class structure.

### case_id=615 FP lexical_or_api_overlap

- 方法: `readTwitterFead` vs `loadSourceCode`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a Twitter timeline from a hardcoded URL and returns the JSON response as a string.
- B 摘要: Loads source code from a class resource file, applies syntax highlighting, and stores it as an HTML string.
- 静态失败原因: Static BERT models like GraphCodeBERT rely heavily on token overlap and structural patterns. The two functions share common API calls (BufferedReader, InputStreamReader, readLine) and loop structures, leading the model to overemphasize syntactic similarity and ignore the different contexts (HTTP vs file, output processing).
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels clones based on functional equivalence. Despite sharing a line-reading loop, the functions have different purposes (fetching Twitter JSON vs loading and highlighting source code), different I/O sources, and different output formats. Therefore, BCB likely considered them non-clones.
- 共享行为: Both use BufferedReader to read lines from an input stream；Both accumulate lines into a string buffer (StringBuilder in A, String concatenation in B)
- 行为差异: A fetches data from a remote HTTP service; B reads from a local file/resource；A returns raw text; B builds HTML with syntax highlighting；A uses specific HTTP client and status code check; B uses URL.openStream and includes file length probing；A logs errors to Android's Log.e; B catches Exception broadly and assigns an error string to a field
- 修正建议: Incorporate data flow analysis to differentiate I/O sources and output destinations；Add checks for API usage patterns specific to HTTP vs local file access；Use control-flow and data-flow graphs to capture semantic differences beyond token overlap

### case_id=616 FN benchmark_preference_bias

- 方法: `getFile` vs `copy`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, optionally modifies the SOAP address location, and saves it locally.
- B 摘要: Copies a local file to a destination path using buffered I/O.
- 静态失败原因: The low token Jaccard (0.124) and clear differences in structure and logic led the model to correctly predict non-clone, but BCB's broader definition considered them clones.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as a Type-4 clone based on the shared file-copying functionality, but the additional XML processing and network download in A significantly change the semantics.
- 共享行为: Both read from an input source and write to a file output stream.
- 行为差异: A involves network I/O and XML parsing/modification; B is purely local file I/O.；A uses NIO channels for transfer; B uses byte buffer loop.；A has conditional logic based on file existence; B always overwrites.；A handles multiple exception types and throws AxisFault; B only throws IOException.
- 修正建议: Reconsider the clone definition to exclude pairs where only a minor sub-task overlaps.；Use hierarchical or multi-level clone detection that separates simple I/O from complex workflows.；Increase model sensitivity to high-level semantic roles beyond token overlap.

### case_id=617 FN partial_functionality

- 方法: `init` vs `File2String`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Loads controller classes from classpath resource files by reading lines and loading each class.
- B 摘要: Reads a file from filesystem or classpath and returns its content as a single string, exiting on failure.
- 静态失败原因: The static BERT model likely learned to distinguish based on low token overlap (0.1956), different method names, and different overall goals, correctly predicting non-clone.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this as a clone because both functions involve reading from a resource (classpath or filesystem) using similar I/O patterns, considering high-level functional similarity (Type-4).
- 共享行为: Both use BufferedReader to read lines from an InputStream obtained from a URL or file.；Both handle IOException and FileNotFoundException.
- 行为差异: Function A loads multiple classes from multiple resource files; Function B reads a single file and concatenates lines.；Function B exits the program on file-not-found errors; Function A only logs errors.；Function A adds classes to a registry; Function B returns a string.；Function A uses ClassLoader.getResources(); Function B uses ClassLoader.getSystemResource() or FileInputStream.
- 修正建议: Use fine-grained functional decomposition to separate I/O reading from business logic.；Improve training data to distinguish similar I/O patterns with different final purposes.

### case_id=618 FN benchmark_preference_bias

- 方法: `modifyApplicationMessage` vs `clonarFichero`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Modifies a properties file for a given locale, copying a default file if missing, then updating or adding a key-value pair.
- B 摘要: Copies a file from an input stream to a destination path using FileChannel.
- 静态失败原因: Static model correctly identified the low token overlap and different method signatures, but was overridden by BCB's broad clone annotation. The model's prediction aligns with strict semantics.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider file copying as shared behavior, and both functions follow a similar pattern of file reading/writing with exception handling, which could be deemed as Type-4 clone under broad semantic similarity.
- 共享行为: Both perform file I/O operations with exception handling.；Both involve reading from a source and writing to a destination in a try-catch block.
- 行为差异: Function A modifies property key-value pairs and handles multiple cases (copy, read, modify, write); function B only copies file content.；Function A uses FileReader/FileWriter for textual files; function B uses FileInputStream/FileOutputStream and FileChannel for binary copy.；Function A handles missing file by copying default; function B assumes source exists.
- 修正建议: Improve clone detection by combining structural similarity with semantic understanding to avoid over-penalizing different intents.；Use better function summarization to capture high-level purpose difference.

### case_id=619 FP boilerplate_overlap

- 方法: `setMembers` vs `downloadFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Parses a Trac newticket HTML page to extract component and priority options and stores them in static arrays.
- B 摘要: Downloads a file from a URL to a local destination, updating progress via a message frame.
- 静态失败原因: Both functions share boilerplate patterns (URL opening, try-catch, loops) leading the model to overestimate similarity despite differing semantics.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clone because the functions have entirely different purposes and minimal syntactic overlap; even with broad Type-4 tolerance, functional similarity is lacking.
- 共享行为: Both open a URL and read from an input stream；Both handle exceptions and print messages
- 行为差异: Function A parses HTML text via regex; Function B writes binary data to a file；Function A has no return value; Function B returns boolean；Function A updates static fields; Function B updates download progress and closes streams；Function A uses BufferedReader; Function B uses BufferedInputStream
- 修正建议: Incorporate dataflow analysis to distinguish I/O direction and processing；Use method-level semantic embeddings that capture purpose；Train with contrastive examples of similar boilerplate but different functionality

### case_id=620 FN benchmark_preference_bias

- 方法: `getFile` vs `patch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies the SOAP address endpoint, and saves it to a temporary directory.
- B 摘要: Copies the Minecraft jar file to a backup and opens the original jar for patching.
- 静态失败原因: Static BERT models rely heavily on token overlap and code structure; the low Jaccard similarity (0.071) and different method names/operations caused the model to predict non-clone, missing the broad functional similarity that BCB might have annotated.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled these as clones because both involve copying or transferring file data, which could be considered a shared high-level functionality (e.g., file handling utilities), even though the specific tasks differ.
- 共享行为: Both perform file I/O operations involving reading and writing files.
- 行为差异: A downloads from a remote URL, B copies a local file.；A modifies XML content and saves changes, B does no content modification.；A handles network and parsing exceptions, B only handles IOException.；A returns a file path, B returns void.
- 修正建议: Incorporate functional similarity metrics that capture high-level I/O operations.；Use models that understand broader context and file manipulation patterns.；Adjust training data to include such weakly similar pairs as clones per BCB guidelines.

### case_id=621 FN partial_functionality

- 方法: `doGet` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Handles HTTP GET request, retrieves a page by ID or name, checks user visibility, logs the request, and may cache the page output to a temporary file.
- B 摘要: Copies a file from source to destination with a specified buffer size, optionally overwriting an existing destination file, using standard stream I/O.
- 静态失败原因: Static BERT/GraphCodeBERT models rely on token overlap and syntactic structure; the low Jaccard similarity (0.101) and different high-level context likely caused the model to miss any functional similarity, especially since the file writing part in doGet is a small section of a larger, distinct function.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label them as clones because both functions perform file output operations and share a similar structure (check conditions, open files, write, close), possibly considering them as Type-4 functional clones with partial functionality similarity.
- 共享行为: Both involve file writing operations (write to temp file vs copy file).；Both use logging (myLogger.info vs logger.info).；Both perform input validation and handle exceptions.
- 行为差异: Main purpose: HTTP request handling versus file copying.；Control flow: complex web logic with multiple conditions versus straightforward copy loop.；Error handling: specific web errors (SC_NOT_FOUND) versus generic IOException.；Resource management: nested resources with caching versus simple stream close.
- 修正建议: Incorporate functional similarity detection beyond syntactic overlap, e.g., by recognizing common sub-patterns like file I/O with logging.；Use dataflow analysis to capture shared operations even if spread across different control flows.

### case_id=622 FN partial_functionality

- 方法: `callService` vs `read`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads data from a constructed URL and stores the result as a string in an instance variable.
- B 摘要: Reads data from a URL or file and returns a status code, delegating actual reading to another method.
- 静态失败原因: The static BERT model likely focused on low token overlap (Jaccard = 0.2156) and surface-level differences (different method names, return types, variable names, and control flow). It failed to capture the underlying functional similarity of reading from a URL with error handling because of insufficient abstraction of I/O patterns.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considers these clones because both perform a similar high-level operation: opening a URL, reading data, and handling I/O exceptions. The differences in return type and specific reading method are considered implementation details in Type-3/Type-4 clone classification.
- 共享行为: Both open a URL and read data from it；Both catch IOException and handle errors by setting a status or error message
- 行为差异: A only reads from a URL constructed from base URL plus path; B can read from any URL or a file；A returns void and stores result in an instance variable; B returns an int status；A reads line-by-line using BufferedReader; B delegates reading to another method read(InputStream)；Error handling: A sets answer to error message; B sets STATUS_OPEN_ERROR
- 修正建议: Use code abstraction techniques to normalize I/O operations (e.g., represent 'open URL and read' as a high-level pattern)；Incorporate data flow or program dependency graphs to capture the sequence of operations rather than exact tokens；Train on a dataset that includes partial clones with different return types and reading methods

### case_id=623 FP lexical_or_api_overlap

- 方法: `createHTML` vs `importSequences`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Creates an HTML page string based on the request page type, reading a CSS file and optionally querying a database for dashboard content.
- B 摘要: Imports sequences from a file URL by parsing lines starting with '>' and extracting names and sequences into lists.
- 静态失败原因: The model likely over-relied on lexical and API-level similarities (e.g., 'openStream', 'InputStreamReader', 'BufferedReader', while loops, try-catch) while ignoring the overall program structure and domain-specific logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels these as non-clones because the functions serve entirely different purposes (HTML generation vs sequence import) with no overlapping functionality.
- 共享行为: Both read from an InputStream；Both use buffered reading；Both catch IOException
- 行为差异: A generates HTML output for a dashboard UI; B parses FASTA-like sequence data；A uses database queries and complex HTML construction; B uses simple tokenization and sequence reading；A has multiple cases based on page type; B follows a fixed sequential parsing logic
- 修正建议: Train models on more diverse examples that distinguish similar API usage from semantic similarity；Incorporate control flow and data dependency graphs that highlight different output behaviors；Use method names and return types as additional signals for functional purpose

### case_id=624 FN partial_functionality

- 方法: `doTransfer` vs `runScript`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Transfers an HTTP request and response by proxying to a specified URL.
- B 摘要: Reads a script file from the server and returns its content as a string.
- 静态失败原因: Static models rely on lexical and structural similarity; the low token overlap (0.16) and different control flow (e.g., HttpURLConnection vs. simple openStream) cause under-estimation of semantic similarity, especially when one function is an extended version of the other.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider the core functionality of reading data from a URL as a sufficient commonality, and the broader transfer logic as a superset of the simple download, thus labeling as a clone.
- 共享行为: Both open a URL and read from an input stream；Both use try-catch for IOException；Both process byte/char data from a remote resource
- 行为差异: Function A performs full HTTP request/response proxying, while B only downloads content；Function A sets request properties, reads request body, and writes response; B does not handle request/response；Function A returns void and writes to response; B returns a String；Function A handles multiple streams (input/output, request/response); B uses only one input stream
- 修正建议: Use context-aware embeddings that capture method purpose and surrounding class；Incorporate data flow or API call patterns to recognize shared subroutines；Fine-tune on pairs where one function is a fragment of another

### case_id=625 FN lexical_or_api_overlap

- 方法: `parseContent` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `1.0`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Parses HTML content from a StreamLimiter, detects charset, extracts metadata, links, and body text.
- B 摘要: Generates static HTML pages for site editing by iterating over pages, applying XSLT transformations, and writing output files.
- 静态失败原因: The static model correctly identified non-clone (0). The BCB label of 1 appears erroneous; the model did not fail.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely mislabeled this pair; the functions are too different in purpose and structure to be considered clones even under broad criteria.
- 共享行为: Both involve reading input data and writing output；Both use string/stream manipulation
- 行为差异: A focuses on parsing HTML and extracting fields; B focuses on XSLT transformation and file generation；A uses a StreamLimiter and HtmlDocumentProvider; B uses FileSystem, Transformer, and multiple path/property parameters；A's output is internal fields (addField); B's output is files on disk；A has specific logic for charset detection and link classification; B has iterative page processing and error handling
- 修正建议: Review BCB annotation for this pair; likely an annotation error；Clarify clone criteria to avoid labeling such disparate functions as clones

### case_id=626 FN partial_functionality

- 方法: `addDataFromURL` vs `read`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads text from a URL and appends it to an internal text buffer with exception handling.
- B 摘要: Opens a URL or file input stream and delegates reading to another method, returning a status code.
- 静态失败原因: Low token Jaccard similarity (0.1739) and different overall structures (BufferedReader vs BufferedInputStream, different post-processing) caused the model to miss the shared URL-reading pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considers them clones because they share the core functionality of reading from a URL using openStream() and handling exceptions, which is a common pattern in Type-4 clones.
- 共享行为: Both open a URL stream using openStream()；Both handle exceptions during I/O
- 行为差异: A only handles URL; B handles both URL and file；A appends lines to a buffer; B delegates reading and returns status；A prints exception to console; B sets a status variable；A is void; B returns an int
- 修正建议: Use dataflow-aware models that track API usage patterns；Augment training with diverse examples of URL reading without requiring full semantic equivalence；Incorporate structural or graph information to capture shared subtasks

### case_id=627 FP lexical_or_api_overlap

- 方法: `actionPerformed` vs `sendErrorMessage`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Handles user actions in a settings dialog to set file paths for external tools and update UI preferences.
- B 摘要: Sends an error message by zipping a log file and emailing it to technical recipients.
- 静态失败原因: The model likely overfitted on common tokens like 'File', 'filename', 'owner', and similar API usage patterns, ignoring the overall semantic difference.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would not consider these clones because they have completely different functionality and purpose, despite minor lexical overlap.
- 共享行为: Both use file I/O (File, FileInputStream, FileOutputStream) and handle file paths.
- 行为差异: A is an event listener for GUI settings; B is a method for error reporting via email.；A interacts with UI components and preferences; B compresses logs and uses a Mail object.；A has conditional logic for multiple commands; B has a single linear flow.；A does not throw custom exceptions; B throws multiple custom exceptions.
- 修正建议: Train on more diverse negative examples.；Incorporate call-graph or data-flow information to differentiate control flow and side effects.；Use contrastive learning to emphasize semantic differences.

### case_id=628 FP lexical_or_api_overlap

- 方法: `downloadURLtoString` vs `readUNI`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads entire URL content line by line and returns it as a single concatenated string.
- B 摘要: Reads URL content, skips first line, parses tab-separated lines, and adds extracted id and desc pairs to a Vector.
- 静态失败原因: Static models like CodeBERT rely on token and structural overlaps. Both functions share common API calls (URL, openStream, while-loop, close) which can mislead the model into predicting clone despite different logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically requires substantial functional similarity for Type-3/Type-4 clones. Here, the high-level operation (reading from a URL) is shared, but the purpose and output are entirely different. Thus BCB considers them non-clones.
- 共享行为: Open a URL and obtain an InputStream；Read input line by line；Close the stream in a finally block
- 行为差异: Function A returns a concatenated string of all lines; Function B populates a Vector with parsed fields.；Function B skips the first line and uses a specific delimiter (tab) to parse fields.；Function B includes extensive exception handling and error printing; Function A only throws IOException.；Function A uses BufferedReader and StringBuffer; Function B uses Scanner with custom delimiters.
- 修正建议: Incorporate dataflow analysis to track how input is transformed into output.；Use contrastive learning that emphasizes functional equivalence over lexical similarity.；Include more negative examples with similar API usage but different semantics.

### case_id=629 FN benchmark_preference_bias

- 方法: `run` vs `readGeoParserResult`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.6`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Reads a resource file from classpath and sets the text in a Swing text component.
- B 摘要: Sends an XML request to a geo-parser service, parses the XML response, and returns a collection of place names with associated gazetteer IDs.
- 静态失败原因: The model likely focused on the semantic differences (UI update vs. XML parsing) and low token overlap (0.16), thus predicting non-clone.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have considered both as performing I/O reading and string building, possibly treating them as Type-4 (semantic) clones due to similar structure of reading lines from an input stream.
- 共享行为: Both read text data from an InputStream using BufferedReader and build a String.；Both handle exceptions with try-catch.
- 行为差异: A reads a local resource and updates UI; B sends HTTP request, retries on failure, parses XML, and returns a collection.；A is IO-bound to local resource; B is network-bound.
- 修正建议: Include ability to recognize structural I/O patterns as partial clones.；Adjust similarity threshold for broad clones.

### case_id=630 FP partial_functionality

- 方法: `get` vs `readUNI`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads game records from a URL via HTTP GET, parsing lines that don't start with '#' into GameRecord objects and returning an array.
- B 摘要: Reads tab-separated data from a URL, skipping the first line, and populates a vector with concatenated id and description.
- 静态失败原因: Static BERT/GraphCodeBERT may have overemphasized the shared boilerplate of URL opening, line reading, and exception handling, while missing the semantic differences in data parsing, output, and API usage. The low token Jaccard (0.195) indicates limited lexical similarity, but the model might still be misled by the structural skeleton.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely sees these as unrelated tasks: one is a game-specific API call with headers and custom decoding, the other is a generic TSV reader. Despite shared I/O pattern, the functionality is distinct, so BCB labels as non-clone.
- 共享行为: Both open a URL stream and read line-by-line；Both parse data from lines and skip certain lines；Both handle IO exceptions with printStackTrace
- 行为差异: Function A uses HttpURLConnection with custom headers; Function B uses URL.openStream and Scanner；Function A returns a GameRecord array; Function B populates an input vector；Function A checks HTTP response code; Function B does not；Function A skips lines starting with '#'; Function B skips only the first line
- 修正建议: Incorporate data flow analysis to distinguish different output types and transformations；Use contrastive learning with more diverse negative examples that share I/O structure but differ in semantics；Consider method signatures (return type, parameters) as additional features

### case_id=631 FP lexical_or_api_overlap

- 方法: `doVersionCheck` vs `getTicketsForQueue`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Connects to a version-check URL, reads response lines to extract version and build numbers, compares with current build, and displays appropriate message.
- B 摘要: Connects to a Request Tracker REST API, sends query for open tickets in a queue, parses ticket IDs from response, and retrieves each ticket.
- 静态失败原因: Static BERT models often rely on lexical and structural patterns; the high similarity in I/O boilerplate (BufferedReader, readLine, try-catch) misled the model to ignore the semantic differences in data processing and method intent.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would label this as non-clone because the functions have entirely different purposes and output behaviors, even though they share common I/O boilerplate. BCB typically requires substantial functional overlap, which is absent here.
- 共享行为: Both perform HTTP requests；Both read response line-by-line using BufferedReader；Both parse substrings from lines；Both handle exceptions and resource cleanup
- 行为差异: Different input parameters and output types (void vs List<RTTicket>)；Different URL and query construction；Different parsing logic (version/build vs ticket IDs)；Different error reporting (GUI message vs logging and returning null)
- 修正建议: Incorporate method name/context embeddings；Focus on data flow and transformation logic；Use control-flow or program dependency graphs

### case_id=632 FN partial_functionality

- 方法: `downloadURLtoString` vs `seeURLConnection`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: downloads content from a given URL and returns it as a string
- B 摘要: reads content from a hardcoded URL and logs the resulting string
- 静态失败原因: Static BERT models rely heavily on token overlap (Jaccard 0.39) and method signatures; they miss the identical loop structure and treat different return types as non-clones
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels Type-3 clones where core functionality (reading URL content into a string) is identical despite minor syntactic and output differences
- 共享行为: opens a URL connection；reads lines using BufferedReader into a StringBuffer；closes the reader
- 行为差异: A returns the string, B logs it；A takes URL as parameter, B hardcodes URL；A uses openStream(), B uses openConnection().getInputStream()
- 修正建议: Train model on examples where core behavior is similar despite signature differences；Incorporate dataflow or structure-aware features to capture the read-loop pattern

### case_id=633 FP lexical_or_api_overlap

- 方法: `getJSONData` vs `getVersion`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.75`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches JSON data from a given URL using HttpClient, reads all lines, and parses into JSONObject.
- B 摘要: Fetches version string from a hardcoded URL using URLConnection, reads lines and returns the last line.
- 静态失败原因: Static models may over-rely on common tokens like 'BufferedReader', 'InputStreamReader', 'while ((line = in.readLine()) != null)', and similar try-catch blocks, ignoring differences in URL handling and return types.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled 0 due to different return types, different HTTP APIs, and distinct purposes (generic JSON fetch vs. specific version check), despite superficial structural similarity.
- 共享行为: Both perform HTTP GET request to a URL；Read response line by line using BufferedReader；Return a value derived from the response
- 行为差异: A uses DefaultHttpClient/HttpGet; B uses URL/URLConnection；A returns JSONObject; B returns String；A builds full response string; B overwrites variable with each line (keeps last)；A parses JSON; B does not
- 修正建议: Incorporate return type analysis into the model；Distinguish between different HTTP client APIs (HttpClient vs URLConnection)；Train on more diverse examples with different I/O patterns

### case_id=634 FP boilerplate_overlap

- 方法: `perform` vs `hash`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Struts action that processes a web request to classify a concept by sending XML to a URL and handling the response.
- B 摘要: Utility method that computes MD5 hash of a string and returns the hex string.
- 静态失败原因: Overlap of common Java keywords (String, try, catch, IOException, ServletException) and similar token patterns (e.g., getBytes, getInstance) may have caused a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels as non-clone because the two methods have entirely different functionality: one is a web request handler, the other is a simple hash utility.
- 共享行为: Both return a String result (indirectly)
- 行为差异: A performs HTTP call, session management, XML parsing; B does cryptographic hashing.；A has complex control flow with conditional logic; B is a single try-catch block.
- 修正建议: Use graph-based representations to capture control and data flow structure.；Incorporate method signatures and imported libraries to distinguish domain.

### case_id=635 FP lexical_or_api_overlap

- 方法: `getWebPage` vs `sendPost`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches web page content via GET request using a URL object and returns the concatenated response as a string, throwing an Error on IOException.
- B 摘要: Sends an HTTP POST request with parameters to a given URL and returns the concatenated response as a string, printing an error message on exception.
- 静态失败原因: Static models like BERT may over-rely on lexical overlap (e.g., BufferedReader, readLine, URL, openStream) and similar boilerplate code for reading streams, ignoring the semantic differences in HTTP method and parameter handling.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled this as non-clone because the two functions represent different HTTP methods (GET vs POST) with distinct parameter handling and error strategies, which are considered different functionalities even though both retrieve web content.
- 共享行为: Both read content from a URL and return it as a concatenated string.；Both use BufferedReader and InputStreamReader to read line by line.
- 行为差异: Function A performs a GET request with no parameters; Function B performs a POST request with parameters.；Function A uses a URL object directly; Function B constructs URL from string and uses HttpURLConnection.；Function A throws a custom Error on IOException; Function B prints error message and does not rethrow.；Function B sets HTTP headers and handles output stream for POST data.
- 修正建议: Include data flow analysis to distinguish between GET and POST operations.；Encode HTTP method information in the representation.；Use structural comparison to differentiate connection setup details.

### case_id=636 FP long_range_semantics

- 方法: `createPasswordDigest` vs `perform`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `static_summary_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Computes an MD5 digest of a password concatenated with salt.
- B 摘要: Processes a web action request, handles form parameters, communicates with an external service, and returns an ActionForward.
- 静态失败原因: The model likely failed due to long-range semantics and dataflow blindspot, as both functions are long but have completely different purposes and data flows. The model may have been misled by common keywords like 'password' or 'digest' in one and 'XML' in the other, but overall there is no meaningful overlap.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB would not consider these clones because there is no similarity in functionality, control flow, or data manipulation.
- 行为差异: One performs cryptographic hashing, the other handles web request lifecycle.；Different return types: byte array vs. ActionForward.；Different external dependencies: MessageDigest vs. HTTP and XML parsing.；Different control flow: simple linear vs. complex branching and networking.
- 修正建议: Incorporate data flow analysis to capture variable dependencies and transformations.；Use contrastive learning to emphasize semantic dissimilarity over lexical overlap.；Increase diversity of pre-training data to cover more web application patterns.

### case_id=637 FN partial_functionality

- 方法: `writeFileType` vs `run`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.65`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads URIs from a file, fetches each URL's first 100 lines to detect RDF/OWL/RDFS namespaces, and writes the URI with its detected type to an output file.
- B 摘要: Opens an HTTP connection with basic authentication, reads the entire response, and stores it in a string result variable.
- 静态失败原因: Static BERT/GraphCodeBERT likely failed due to low token overlap (Jaccard 0.162) and inability to recognize the high-level similarity of HTTP reading patterns, being distracted by the many unrelated operations in function A.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB might consider them clones because both involve network I/O (opening a URL, reading lines) and basic error handling, fitting a broad Type-4 definition of similar functionality despite different purposes.
- 共享行为: Both open a URL connection and read lines via BufferedReader；Both handle exceptions with try-catch
- 行为差异: A reads multiple URIs from a file, skips initial lines, only reads up to 100 lines per URL; B reads a single URL completely；A writes results to a file; B stores in internal variable；A checks for specific namespace keywords; B concatenates all lines
- 修正建议: Enhance model to recognize common API usage patterns (e.g., URL.openConnection, BufferedReader) as a signature；Use data flow analysis to isolate core I/O sequences from peripheral logic；Incorporate method-level context to understand the purpose beyond surface tokens

### case_id=638 FP lexical_or_api_overlap

- 方法: `getLinksFromURLFast` vs `GetResponse`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Extracts all hyperlinks and their text from an HTML page accessible via a URL, using regex, and returns them as two vectors.
- B 摘要: Fetches the raw content of a web page via HTTP GET and returns it as a single string.
- 静态失败原因: The model likely focused on the lexical overlap of common Java I/O patterns (BufferedReader, InputStreamReader, URL, while loop) and the similar connection setup, ignoring the semantic difference in the output type and the post-processing steps.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB considers these non-clones because they serve fundamentally different purposes: link extraction vs. content retrieval. The shared I/O boilerplate does not make them functionally similar.
- 共享行为: Both open a URL connection；read response line by line using BufferedReader
- 行为差异: A returns structured link data; B returns raw content；A uses regex to parse HTML; B does no parsing；A includes debug prints and time checks; B does not
- 修正建议: Incorporate data flow analysis to track output transformations；Use contrastive learning to distinguish similar API sequences with different purposes

### case_id=639 FN boilerplate_overlap

- 方法: `createHTML` vs `httpRequestByPOST`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Builds an HTML page by reading a CSS file and appending content based on page type.
- B 摘要: Sends an HTTP POST request, reads the response, and returns the response body as a string.
- 静态失败原因: A static model like GraphCodeBERT might focus on the overall structure and API usage, and the high-level purpose difference (HTML generation vs HTTP request) would lead it to predict non-clone. The token overlap is very low, so the model correctly identified them as different.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB might label this as a clone because both functions read lines from an input stream and build a string, a common pattern. Under Type-3 (modified) or Type-4 (semantic) similarity, the boilerplate of reading and building a string could be considered similar.
- 共享行为: Reads input from a stream line by line using BufferedReader；Handles IOException；Returns a String
- 行为差异: Different input sources (CSS file vs HTTP response)；Different output construction (HTML vs raw response text)；Presence of HTTP request logic vs HTML generation logic
- 修正建议: Incorporate task-level semantic understanding beyond token overlap；Use dynamic execution traces to differentiate purposes；Add domain knowledge about HTTP vs HTML generation

### case_id=640 FN partial_functionality

- 方法: `_checkLanguagesFiles` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Iterates over languages, checking and copying language property files from a global path to a temp directory if missing.
- B 摘要: Launches a NexOpen project configuration, handling pom files and copying a default reverse-engineering file to the project if missing.
- 静态失败原因: Static models like GraphCodeBERT rely heavily on lexical overlap and overall structure. The low token Jaccard (0.086) and different method names/contexts lead them to predict non-clone. They fail to detect the small but important shared pattern due to the dominance of dissimilar code.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels clones based on partial functionality similarity. The common pattern of 'copy default file if missing' is a shared sub-task, even though the functions have different overall purposes and domains. This pattern is non-trivial and specific enough to be considered a clone under broad Type-3/Type-4 criteria.
- 共享行为: Both check if a target file exists and create it if missing.；Both copy content from a default source file to the target file.；Both use exception handling with logging for I/O errors.
- 行为差异: Function A processes multiple languages in a loop, while Function B handles a single file within a larger launch process.；Function A uses FileChannel for copying, Function B uses IOUtils.；Function B involves XML parsing, property setting, and project actions, which A lacks.
- 修正建议: Incorporate subgraph matching or data-flow analysis to identify shared code patterns even when embedded in large, unrelated contexts.；Use long-range semantic attention mechanisms that can capture similarity in small code fragments.；Train on pairs where only a sub-function is similar, or use contrastive learning to emphasize partial similarity.

### case_id=641 FN partial_functionality

- 方法: `readRemoteFile` vs `testNetworkHTTP`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads the content of a remote file from a fixed URL and returns it as a concatenated string.
- B 摘要: Conducts a series of HTTP GET requests to send device-specific data to remote servers, discarding the response content.
- 静态失败原因: Low token Jaccard similarity (0.1818) and different overall structure (different numbers of loops, URLs, return types) caused the static model to focus on surface differences rather than the shared API usage pattern. The model likely missed the underlying semantic equivalence of the HTTP reading operations.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB labels clones based on functional similarity. Both methods share the core sub-task of reading lines from an HTTP response using the same API pattern (openConnection, BufferedReader, readLine). Despite differences in purpose and return type, this shared functionality makes them a clone under BCB's broad Type-3/Type-4 criteria.
- 共享行为: Both open an HTTP connection to a URL；Both read lines from the response using BufferedReader and readLine；Both use similar Java networking classes (URL, HttpURLConnection, BufferedReader, InputStreamReader)
- 行为差异: A returns the concatenated response; B discards all responses；A reads from a single URL; B reads from multiple URLs；A uses URL.openStream() and does not explicitly disconnect; B uses HttpURLConnection and disconnects in finally；A handles EOFException and IOException inside a loop; B catches IOException at outer level
- 修正建议: Incorporate API usage graphs or data flow analysis to capture common sub-patterns；Use contrastive learning with harder negatives that have similar API usage but different overall goals；Include method name and context information to reduce false negatives for partial functionality clones

### case_id=642 FN lexical_or_api_overlap

- 方法: `getFile` vs `copyFileChannel`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies its endpoint, and saves it to a temporary location.
- B 摘要: Copies a local file to another location using FileChannel, optionally preserving modification time.
- 静态失败原因: Static BERT likely recognized low lexical similarity and correctly predicted non-clone, but BCB label is inconsistent.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may consider both as performing file I/O operations using NIO channels, but overall functionality differs significantly, suggesting a possible annotation error or overbroad interpretation.
- 共享行为: Both use FileChannel for data transfer；Both handle file I/O with channel close in finally
- 行为差异: A downloads over network and parses XML; B is local file copy；A returns a String; B is void；A has extensive error handling; B has simple try-finally
- 修正建议: Re-evaluate BCB annotation for this pair；Consider adding more contextual features to distinguish file copy from download+modify

### case_id=643 FN partial_functionality

- 方法: `copyFile` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a file using FileChannel transferFrom.
- B 摘要: Downloads a KMZ file from a URL, extracts its zip entries, and writes each entry to a file.
- 静态失败原因: The static BERT model likely focused on the low token overlap (0.14) and the structural differences (e.g., loops, conditionals, different method signatures), and failed to recognize the abstract I/O pattern as similar. The model may have learned to map semantically equivalent functions but this pair's token similarity is too low.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this as a clone because both methods perform I/O operations that involve reading from a source and writing to a destination, which is a common abstract pattern. The benchmark sometimes includes Type-4 clones where the functionality is 'file copying' at a high level, even if the specific implementations differ. However, the actual tasks (file copy vs. zip extraction) are distinct.
- 共享行为: Both read from an input source and write to an output destination.；Both handle file I/O operations.
- 行为差异: Function A directly copies a file using channel-based transfer; function B downloads from a URL and extracts a zip archive.；Function A has no conditionals or loops; function B has a while loop and conditional for protocol.；Function A is a utility method; function B is a main method with hardcoded URL.
- 修正建议: Incorporate more abstract representations of I/O operations, such as encoding the pattern of opening resources, transferring data, and closing them.；Use code structure similarity measures that ignore specific data sources or destinations.；Train with more examples of Type-4 clones that share only high-level functionality.

### case_id=644 FP lexical_or_api_overlap

- 方法: `SRWGuiClient` vs `getXML`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Constructor that builds a GUI browser, fetches XML from a URL, optionally applies XSLT transformation, and displays the resulting HTML.
- B 摘要: Utility method that fetches text from a URL and returns it as a string.
- 静态失败原因: The model likely over-relied on the structural overlap of the URL reading loop (BufferedReader, while readLine, append) and ignored the significant differences in context, purpose, and surrounding code.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clones for functions with entirely different purposes and minimal semantic overlap. Despite sharing a common pattern of reading from a URL, the overall functionality (GUI construction vs. data fetching) is dissimilar enough for BCB to consider them non-clones.
- 共享行为: Both read from a URL using BufferedReader and InputStreamReader.；Both append lines to a StringBuffer/StringBuilder.
- 行为差异: Function A sets up a GUI, while Function B is a pure utility method.；Function A performs XSLT transformation on XML, Function B does not.；Function A handles errors by warning the user, Function B returns null or throws exceptions.；Function A uses URLEncoder, Function B does not (in the shown code, but B's method name suggests it might, though not used).
- 修正建议: Train model to prioritize higher-level semantic understanding over shared API usage.；Incorporate class context or method purpose classification to disambiguate shared patterns.；Use contrastive learning to penalize pairs with only boilerplate overlap.

### case_id=645 FP boilerplate_overlap

- 方法: `main` vs `copy`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Main method that parses a Prolog file, generates adapter classes, and writes them to a JAR file.
- B 摘要: Utility method that copies an InputStream to an OutputStream, logging errors and throwing a custom exception.
- 静态失败原因: The static model likely over-emphasized common boilerplate code (try-catch-IOException, IOUtils) and generic structure, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels as non-clone because the functions have entirely different purposes and behavior; no partial functionality overlap.
- 共享行为: Both handle IOException with try-catch blocks
- 行为差异: Function A is a long main method for adapter generation; Function B is a short I/O copy utility；A reads files and performs complex logic; B simply copies stream data；A uses many custom classes; B uses Apache Commons IOUtils
- 修正建议: Improve training to recognize task-level semantics beyond syntactic patterns；Incorporate data flow or call graph information to distinguish utility functions from complex workflows

### case_id=646 FP boilerplate_overlap

- 方法: `getUser` vs `readIntoList`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Get a user by login from DAO or parse a config file and persist the user.
- B 摘要: Read HTML from a URL, extract command names, and populate a menu map with JMenuItem components.
- 静态失败原因: Static BERT models often over-rely on lexical and API-level overlap. Here, both functions share signature patterns like BufferedReader, InputStreamReader, url.openStream(), and e.printStackTrace(), causing a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled this as non-clone because the functions have entirely different business logic and purposes despite sharing common I/O boilerplate.
- 共享行为: Both read from a URL using BufferedReader and InputStreamReader.；Both use a while loop to read lines.；Both catch exceptions and print stack traces.
- 行为差异: Function A parses lines with colon delimiter to extract user credentials; Function B parses HTML tags for command names.；Function A creates and saves a User object; Function B creates JMenuItem objects and adds action listeners.；Function A has a fallback mechanism if user not found in DAO; Function B builds a UI menu structure.；Function A returns a User; Function B returns void and populates a map.
- 修正建议: Use data-flow analysis to capture the actual data transformations and dependencies.；Incorporate control-flow graph or abstract syntax tree features to distinguish core logic from boilerplate.；Employ code summarization techniques to capture functional intent.

### case_id=647 FN benchmark_preference_bias

- 方法: `copyFile` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.6`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Copies a file from source to destination using NIO FileChannel.
- B 摘要: Retrieves a resource as an InputStream, with local caching and HTTP conditional GET support.
- 静态失败原因: The functions have very low token overlap (Jaccard 0.069) but share some keywords (FileInputStream, File), which may have caused the model to miss the semantic distance; the long length of function B may also have led to attention dilution.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have considered both as 'file input/output' operations, but this is a very broad interpretation beyond typical Type-3/4 clones.
- 共享行为: Both involve file I/O operations (FileInputStream, FileOutputStream).；Both handle IOException.
- 行为差异: A performs a direct file copy; B retrieves a remote resource, caches it locally, and returns an InputStream.；B includes HTTP connection handling, caching logic, and conditional GET; A has none of that.；B is significantly longer and more complex.
- 修正建议: Increase sensitivity to structural differences via AST or control flow graph features.；Use a more robust threshold for semantic similarity that ignores common library classes.

### case_id=648 FN benchmark_preference_bias

- 方法: `read` vs `invoke`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Reads a resource file, splits into sections delimited by '---', and validates section count.
- B 摘要: Invokes a remote service via HTTP POST, reads JSON response, deserializes it, and retries on timeout.
- 静态失败原因: The model correctly predicted non-clone based on semantic differences; BCB's label is likely a false positive due to superficial structural similarity, so the model did not fail but disagreed with the benchmark annotation.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled them as clones due to the shared pattern of reading lines from an input stream, building a string, and some structural similarity (e.g., both use BufferedReader and StringBuilder).
- 共享行为: Both read text line-by-line using BufferedReader；Both use StringBuilder to accumulate lines；Both handle exceptions
- 行为差异: A reads from a local resource URL; B makes HTTP requests；A splits sections; B parses JSON；A throws generic Exception; B handles ConnectTimeoutException with retry；B involves service discovery and parameter types
- 修正建议: Clarify BCB annotation guidelines to avoid labeling purely structural similarity as clones；Use more semantically aware metrics that go beyond token overlap and line-reading patterns

### case_id=649 FP lexical_or_api_overlap

- 方法: `main` vs `main`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Parses command-line arguments, reads a Prolog file, generates adapter classes and resources based on the parsed program and a classpath.
- B 摘要: Reads an input file, applies line wrapping and title case filters, writes the transformed content to an output file.
- 静态失败原因: Static BERT models may have over-emphasized common tokens like 'main', 'String[]', 'args', 'File', 'out', 'in', ignoring the vast difference in the rest of the code. Both are main methods with similar I/O patterns, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels non-clones when functions have completely different logic and purpose, even if they share superficial similarities like being main methods. The low token similarity reinforces this.
- 共享行为: Both are public static void main methods that read command-line arguments；Both use file I/O operations
- 行为差异: A has extensive error handling, argument validation, and multiple steps involving parsing and code generation; B is a simple two-file transformation with no error handling；A uses many external libraries (Prolog parser, ASM); B uses standard Java I/O and custom filter classes；A outputs a JAR file with generated adapters; B outputs a filtered text file
- 修正建议: Incorporate more structural or dataflow analysis to distinguish high-level behavior；Use longer-range context to capture the different workflows；Consider functional similarity based on input-output transformations

### case_id=650 FN partial_functionality

- 方法: `copyFile` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a file from source to destination using a buffered stream in a loop.
- B 摘要: Retrieves an InputStream for a resource, with HTTP download and local caching, returning a FileInputStream.
- 静态失败原因: Static BERT/GraphCodeBERT models rely on token overlap and structural similarity; the low Jaccard (0.14) and different method signatures/names led to predicting non-clone. The model missed the shared stream-copying pattern because it is a small part of Function B.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels Type-3/Type-4 clones where core functionality (e.g., stream copying) is shared, even if the overall task differs. Here, the copying loop is a strong commonality.
- 共享行为: Both involve reading from an InputStream and writing to an OutputStream in a byte loop.
- 行为差异: Function A writes directly to a specified destination file; Function B may download from URL and cache locally.；Function B includes HTTP connection handling, cache checking, and error recovery; Function A does not.；Function A returns void; Function B returns an InputStream.；Function B uses System.out.println for logging; Function A has no side effects besides file copying.
- 修正建议: Use a model that can detect common sub-routines or data flow patterns (e.g., by aligning I/O operations).；Incorporate contrastive learning that rewards partial functional similarity.；Preprocess functions to extract only I/O-related blocks or use skeleton-based matching.

### case_id=651 FN benchmark_preference_bias

- 方法: `copyIconFiles` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `1.0`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Copies icon files (16x16 and 32x32) from class annotations to a destination directory using file channels.
- B 摘要: Launches a NexOpen Eclipse project configuration, including XML profile handling, property setup, reverse engineering file creation, and job scheduling.
- 静态失败原因: Static model did not fail; it correctly predicted non-clone (0), indicating it recognized the lack of semantic similarity. The prediction aligns with our analysis.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB likely labeled these as clones due to both methods performing file-related operations and using similar try-catch patterns, but the actual functionalities are completely different. The low token overlap suggests BCB annotation is likely a mistake.
- 共享行为: Both perform file I/O operations (file copying in A, file creation/reading in B).；Both handle strings and file paths.；Both use try-catch for exception handling.
- 行为差异: A copies static icon files; B manages Eclipse project configuration and launch.；A uses FileChannel and annotation values; B uses Eclipse resources, XML documents, properties, and job scheduling.；A has simple deterministic logic; B involves complex conditional logic based on project state.；A is a private method; B is a public method with multiple parameters.
- 修正建议: Correct the BCB annotation to non-clone (0) for this pair.；Ensure benchmark annotations are cross-verified to avoid false positives.

### case_id=652 FP lexical_or_api_overlap

- 方法: `createDialogArea` vs `SRWGuiClient`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Creates a SWT dialog composite for displaying license text from a bundled resource using a Browser or Text widget.
- B 摘要: Constructs a Swing browser window that fetches a URL, optionally transforms XML with XSLT, and displays HTML or plain text.
- 静态失败原因: Static BERT models rely heavily on token overlap (e.g., 'BufferedReader', 'InputStreamReader', 'StringBuffer', 'readLine') and common structural patterns (try-catch-finally, reading loop), leading to high embedding similarity. The model fails to capture the deep semantic differences in GUI framework, control flow, and overall functionality.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the functions are from entirely different domains (SWT dialog vs. Swing browser) with distinct high-level tasks. The superficial similarity in reading a stream is insufficient to overcome the fundamental differences in framework, purpose, and processing logic.
- 共享行为: Open a stream from a URL/resource；Read text line by line into a StringBuffer；Set the text to a GUI component；Handle IO exceptions with try-catch-finally
- 行为差异: Different GUI frameworks: SWT vs. Swing；Different purpose: static license display vs. interactive browser；Different data source: bundled resource vs. arbitrary URL；Different processing: no transformation vs. XML/XSLT
- 修正建议: Incorporate graph-based representations (e.g., code property graphs) to capture control and data flow differences；Use models that attend to framework-specific APIs (SWT vs. Swing) as distinguishing features；Increase contextual window size to capture overall method purpose and structure；Add training examples that require distinguishing UI framework and domain

### case_id=653 FN partial_functionality

- 方法: `main` vs `File2String`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a URL line by line and prints each line to console.
- B 摘要: Reads a file from filesystem or classpath line by line, concatenates lines into a string, and returns it.
- 静态失败原因: The model focused on lexical differences (low token Jaccard, different method names, API calls) and missed the structural similarity of the reading loop and I/O pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often marks functions that share a core read-loop pattern as clones, even if output or error handling differs, due to similar partial functionality.
- 共享行为: Both read text line by line from an input source using BufferedReader.；Both iterate over lines until end of input.
- 行为差异: Function A prints lines immediately; B accumulates into a StringBuffer and returns the result.；A uses URL input; B uses file or classpath resource.；A throws IOException; B catches exceptions and may call System.exit.；B has fallback logic (if file not found, try classpath); A does not.
- 修正建议: Train with more examples of functionally similar but lexically different clones.；Use graph-based models capturing dataflow and control flow.；Include I/O patterns as a distinct feature.

### case_id=654 FP lexical_or_api_overlap

- 方法: `readZoneIDs` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads zone IDs from a resource file, parsing each line as an integer.
- B 摘要: Performs a Google image search by constructing a URL, fetching HTML, and extracting image URLs.
- 静态失败原因: The model likely overemphasized the common API usage (URL, openStream, BufferedReader, readLine, try-catch) and boilerplate structure, ignoring the distinct high-level functionality.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB annotations typically reject clones that only share generic I/O patterns and exception handling, requiring functional similarity. Here, the core logic (parsing integers vs. scraping images) is completely different.
- 共享行为: Both use URL and open a connection to read data；Both read input line by line using BufferedReader/LineNumberReader；Both catch exceptions generically and print/show error
- 行为差异: A parses integers from file lines; B parses image URLs from HTML；A reads from a classpath resource; B makes an HTTP request to Google；B includes URL construction, character replacement, and HTTP headers; A does not；B has conditionally skipped logic based on artist comparison; A is unconditional
- 修正建议: Incorporate dataflow analysis to trace how variables are used；Add attention to the URL construction and string parsing details；Use contrastive training with negative examples that share API calls but differ in purpose

### case_id=655 FN benchmark_preference_bias

- 方法: `main` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Command-line utility that parses arguments, reads an input file with specified encoding, optionally decodes HTML entities, and writes the output to a file.
- B 摘要: Method that builds a website for editing by transforming XML pages using XSLT, processing multiple pages, and writing output files with optional string replacements.
- 静态失败原因: The static model likely focused on low token overlap (Jaccard=0.1147) and dissimilar control flows, failing to capture the vague functional similarity that BCB might have considered.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this pair as clone due to a coarse-grained view of both as 'file processing' functions that read and write text with encoding, despite significant differences in logic and purpose.
- 共享行为: Both perform file I/O operations；Both use char buffers to read/write data；Both handle character encoding explicitly
- 行为差异: Function A is a standalone main method for a simple file conversion; Function B is part of a larger framework for website generation；Function A does not involve XML parsing or XSLT transformation; Function B heavily uses XML and XSLT；Function B processes multiple pages in a loop and performs complex string manipulation; Function A processes a single file
- 修正建议: Incorporate more fine-grained functional similarity metrics beyond lexical overlap；Use control flow and data flow abstraction to recognize patterns like file I/O and buffer usage

### case_id=656 FN partial_functionality

- 方法: `doGet` vs `doRequest`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Handles HTTP GET request for a portal page, retrieving the page by ID or name, checking user visibility, logging requests, and optionally caching the response.
- B 摘要: Handles HTTP request by forwarding to a resource (e.g., file) based on path mapping, setting MIME type, and streaming the content.
- 静态失败原因: The model likely focused on low token overlap and different API calls, missing the high-level structural similarity in request handling. Also, the long length of method A may have caused the model to overlook the core pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as handling HTTP GET requests and serving content, thus type-4 functional similarity, despite differences in specific business logic.
- 共享行为: Both methods handle HTTP requests and write content to the response.；Both use HttpServletRequest and HttpServletResponse parameters.；Both may handle errors and send error responses (A sends errors, B returns false).
- 行为差异: A serves portal pages with user authentication and caching; B serves static resources without authentication.；A handles page not found and forbidden errors; B returns false on missing resource.；A logs requests and updates statistics; B does not.；A has complex control flow for page retrieval by ID or name; B simply maps path to resource.
- 修正建议: Train model with more examples of diverse request handlers to learn high-level patterns.；Include abstraction over framework-specific code (e.g., servlet handlers) as features.；Use graph-based representation to capture control flow and data flow similarities.

### case_id=657 FP partial_functionality

- 方法: `postRequest` vs `SRWGuiClient`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends an HTTP POST request with form data and returns the response body.
- B 摘要: Constructs a Swing browser window that fetches an XML/XHTML document from a URL, optionally transforms it with XSLT, and displays the rendered HTML.
- 静态失败原因: The model likely overfocused on the common API calls (URL, BufferedReader, try-catch) and the sequential reading pattern, ignoring the broader context of GUI construction and XML transformation. The low token Jaccard suggests the model relied on structural similarity rather than semantic understanding.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB focuses on functional similarity; these functions have entirely different purposes (HTTP POST utility vs GUI browser constructor) and interfaces, so BCB would not consider them clones.
- 共享行为: Both open a URL connection and read input using BufferedReader.；Both use the URL class to create a URL object.；Both handle exceptions with try-catch blocks.
- 行为差异: A is a static utility method for POST requests; B is a constructor setting up a GUI.；A sends data via an output stream; B only reads data.；A encodes key-value pairs; B parses XML and applies XSLT transformations.；A returns a string; B sets up GUI components and does not return a value.
- 修正建议: Incorporate method signatures and return types to distinguish utilities from constructors.；Use contrastive learning with hard negatives that have similar API calls but different semantics.；Train with program slicing to focus on core functionality rather than boilerplate code.

### case_id=658 FP lexical_or_api_overlap

- 方法: `doVersionCheck` vs `readUNI`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Performs a version check by reading a remote URL and comparing build numbers.
- B 摘要: Reads a tab-separated UNI data file from a URL and populates a vector with descriptions.
- 静态失败原因: Static BERT models like GraphCodeBERT rely heavily on lexical and structural overlaps; the high token Jaccard (0.26) and shared API calls (URL, openStream) caused false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically requires semantic equivalence or near-equivalence; although both read from URLs, the logic and output differ significantly, so they are not considered clones.
- 共享行为: Open a URL and read lines from the input stream；Use try-catch for exception handling；Close resources after processing
- 行为差异: Purpose: version checking vs. data extraction；Parsing: line-by-line prefix matching vs. tab-delimited tokenization；UI interaction: shows/hides wait cursor and calls downstream method vs. collects results into a vector；Exception handling: specific IOException vs. generic Exception with printStackTrace
- 修正建议: Incorporate data-flow analysis to distinguish variable usage patterns；Add training examples with similar API usage but different semantics；Focus on operation semantics rather than surface-level token similarity

### case_id=659 FP boilerplate_overlap

- 方法: `doVersionCheck` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Downloads version check info from a URL and parses build numbers.
- B 摘要: Searches Google Images, downloads HTML, extracts image URLs, and updates a UI with the first image.
- 静态失败原因: The static BERT/GraphCodeBERT model may have been misled by the overlapping API calls (URL, BufferedReader, InputStreamReader, while readLine) and the structural similarity of reading from a URL and processing lines, considering them as a general 'download and parse' pattern, which is a common boilerplate.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the functions serve entirely different purposes (version checking vs image search) with different parsing logic and output, despite sharing a common pattern of URL reading.
- 共享行为: Both open a URL connection；Both read lines from the input stream；Both use try-catch for exceptions
- 行为差异: One parses version build numbers, the other extracts image URLs from HTML；One updates a UI element (album art label), the other shows error dialog；One uses a specific URL property, the other constructs a URL from parameters；One has additional UI cursor manipulation (show/hide wait cursor)
- 修正建议: Improve model to focus on the specific parsing and output behavior；Include more context about the purpose (e.g., method name, surrounding code)；Use dataflow analysis to distinguish different processing of read data

### case_id=660 FN partial_functionality

- 方法: `read` vs `GetResponse`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.75`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Opens a stream from a URL or file path, reads data into a buffer, and returns a status code.
- B 摘要: Opens an HTTP connection to a URL, reads the response line by line into a string, and returns that string.
- 静态失败原因: The low token Jaccard (0.224) and different method signatures likely caused the model to focus on surface-level differences (e.g., 'read' vs 'GetResponse', different parameter types). Static models often miss functional similarity when APIs and control flow differ, leading to a false negative.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider these Type-3/Type-4 clones because both functions perform network I/O to retrieve data from a URL, despite differences in input/output types and specific protocol handling. The core task of fetching data from a URL is similar enough under BCB's broad annotation guidelines.
- 共享行为: Both use a URL to fetch data from a network resource；Both handle IOExceptions and return a result；Both involve reading input streams
- 行为差异: A takes a String name as input; B takes a URL object；A returns an int status code; B returns a String content；A can also read local files; B is strictly HTTP GET；A delegates reading to another method; B reads inline
- 修正建议: Incorporate functional role tagging (e.g., 'fetch data from URL')；Train on more Type-4 clone examples with different APIs but similar intent；Use graph representations that capture data flow and I/O operations

### case_id=661 FN lexical_or_api_overlap

- 方法: `buildSiteForEdit` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Builds a website for editing by processing XML pages, applying transformations, and writing output files.
- B 摘要: Reads a log file, filters lines containing 'P0' at configurable intervals, and writes them to a new file.
- 静态失败原因: Static BERT methods likely relied on token overlap (e.g., 'File', 'IOException', 'BufferedReader', 'FileWriter') while missing the entirely different program logic and context.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may have labeled this as a clone due to a broad Type-4 interpretation of 'file processing' or an annotation error.
- 共享行为: Both perform file I/O operations
- 行为差异: A handles complex XML transformations and multiple parameters; B is a simple log line filter；A is a large method with many local variables and loops; B is a short main method；A outputs HTML-like pages with embedded content; B outputs a filtered text file
- 修正建议: Use graph-based or flow-sensitive models that capture control and data dependencies；Incorporate structural similarity metrics like AST or CFG matching；Train on pairs with low token similarity but high semantic distance to avoid false negatives

### case_id=662 FN dataflow_blindspot

- 方法: `copy` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `dynamic_equivalence_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Copies a file from a source path to a destination path with error checks and buffered byte stream copy.
- B 摘要: Downloads a KMZ file from a hardcoded URL, reads it as a zip stream, and extracts each entry to a file using buffered byte streams.
- 静态失败原因: Static models like GraphCodeBERT rely on token overlap and lexical similarity, which is low (Jaccard=0.221). They may not capture the shared high-level data flow pattern of buffered byte copying and instead focus on the different APIs (FileInputStream vs. ZipInputStream, URL.openStream) and method names, leading to a false negative.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行价值高：该样本可能是 API 写法不同但行为等价的漏报。建议测试目标为 input_output_equivalence。
- BCB 偏好解释: BCB likely considers this a Type-3 clone because both functions perform bulk data transfer from an input to output using byte buffers and streams, and the core I/O pattern is similar despite different source/target types and additional logic in b.
- 共享行为: Both read data from an input source into a byte buffer and write it to an output file using loops and stream operations.；Both handle stream lifecycle (open/close) with resource cleanup.
- 行为差异: Input source: file path (a) vs. URL for a zip file (b).；Output: single file (a) vs. multiple files from zip entries (b).；Function a includes extensive file existence/permission checks; function b does not.；Function b adds zip streaming and relies on an undefined constant BUFFER.
- 修正建议: Improve model with data flow graph representations to capture stream copy patterns abstractly.；Include more training examples of diverse I/O operations (copy, download, extract) with similar buffer-and-loop structure.；Add syntactic clues like buffer size and while-loop structure to enhance similarity detection.

### case_id=663 FP lexical_or_api_overlap

- 方法: `getUser` vs `downloadFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Loads a User by login, falling back to reading from a configuration file if not found in DAO.
- B 摘要: Downloads a file from a URL to a local destination, updating a UI progress bar.
- 静态失败原因: The model was likely deceived by lexical overlap in API calls (e.g., URL, InputStream, BufferedReader) and the presence of a loop reading data, despite the completely different underlying semantics.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels them as non-clones because their functional domains are entirely unrelated; the only commonality is generic I/O, which is insufficient for clone annotation.
- 共享行为: Both perform I/O operations over a network URL；Both use buffered streams to read data
- 行为差异: Different return types (User vs boolean)；Different core functionality (user authentication vs file download)；Different error handling (catching Exception vs throwing)；Different use of external resources (DAO vs file system)
- 修正建议: Enhance model with dataflow or control-flow information；Incorporate type and method signature awareness；Use more comprehensive context including method names and surrounding class structure

### case_id=664 FN benchmark_preference_bias

- 方法: `read` vs `runInternal`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.85`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Reads camera log from a URL, parses lines into records, sorts, and logs.
- B 摘要: Downloads OPDS catalog pages from HTTP/HTTPS URLs, parses entries, handles pagination and errors, and invokes callback.
- 静态失败原因: The low token overlap (Jaccard 0.0995) and distinct vocabulary (camera log vs. OPDS, HTTP headers) likely caused a static BERT model to predict non-clone due to insufficient lexical and syntactic matching.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might consider both as typical examples of 'reading from a URL' with similar API usage (openConnection, BufferedReader), albeit very different in complexity. The annotation bias may favor broad functional similarity over detail.
- 共享行为: Both read data from a URL；Both use URLConnection to open streams；Both perform line-by-line processing of input
- 行为差异: A is a simple log parser; B manages complex HTTP connection lifecycle, redirects, and content types；A sorts records; B handles pagination and partial loading；B includes error handling with callbacks and user-visible progress; A logs errors and continues；B deals with HTTPS certificate issues, content-disposition, encoding, and download logic
- 修正建议: Incorporate control-flow or data-flow graph features to capture deeper semantics beyond surface tokens；Use contrastive learning with more representative negative pairs that share API usage but differ in logic；Adjust clone detection threshold to accept broader functional similarity when high-level behavior aligns

### case_id=665 FP lexical_or_api_overlap

- 方法: `retrieveQ` vs `importSequences`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads entire content from a URL and returns as a string, printing HTTP response message.
- B 摘要: Parses FASTA-formatted sequences from a URL into lists of names and sequences.
- 静态失败原因: Static BERT likely focused on lexical overlap (e.g., 'InputStream', 'url', 'readLine', 'IOException') and the common reading loop, ignoring the distinct post-processing logic and data structures.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clone because the functions have entirely different output types and domain-specific logic, despite sharing generic IO patterns.
- 共享行为: Both open a URL connection to read data；Both read input line by line；Both handle IO exceptions
- 行为差异: A returns raw text content; B parses structured biological data；A appends newlines to preserve line breaks; B searches for '>' delimiters for FASTA headers；A uses HttpURLConnection to print response message; B uses a custom ImportHelper for parsing
- 修正建议: Include more negative examples with shared boilerplate but divergent logic；Use structural or dataflow analysis to distinguish reading loops from downstream processing

### case_id=666 FN benchmark_preference_bias

- 方法: `copyFile` vs `doGet`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Copies a file from one location to another using FileChannel.
- B 摘要: Handles an HTTP GET request for a page, including user authentication, logging, and caching.
- 静态失败原因: The static BERT model correctly predicted non-clone (0), aligning with our analysis. It did not fail; instead, the BCB label is likely incorrect.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB likely labeled this as a clone due to the superficial similarity of both functions involving file I/O operations (File, FileInputStream, FileOutputStream), but this ignores the vast difference in overall functionality. This may be an annotation error or a case where BCB tolerates broad functionality overlap, but I believe it is a mislabel.
- 共享行为: Both functions use file I/O classes like File, FileInputStream, FileOutputStream, FileWriter, but the context and purpose are completely different.
- 行为差异: copyFile performs a straightforward file copy operation; doGet is a complex servlet handler with multiple conditional branches and side effects.；copyFile returns a boolean indicating success; doGet does not return a value but writes to the HTTP response.；copyFile handles only file I/O exceptions; doGet handles various exceptions including PersistentModelException, PresentationException, and sends HTTP error codes.
- 修正建议: Review BCB annotations for file I/O related functions to ensure consistency and correctness.；Consider removing this pair from evaluation if the label is erroneous.

### case_id=667 FN partial_functionality

- 方法: `sendExceptionToServer` vs `run`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Builds and sends a POST request with exception details to a server, reads response, and prints status.
- B 摘要: Makes a GET request with basic authentication, reads the response, stores it, and sets a completion flag.
- 静态失败原因: Low token overlap (0.22) and different method names led the model to predict non-clone; it likely missed the high-level network communication pattern due to lack of training on Type-4 clones.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled these as clones because both functions perform HTTP communication and handle response reading, ignoring differences in request method and data content.
- 共享行为: Open a URL connection；Read response using BufferedReader；Close streams and connection
- 行为差异: HTTP method: POST vs GET；Data sent: URL-encoded parameters vs basic auth header；Output: prints to console vs stores in fields
- 修正建议: Train model on more Type-4 clones；Incorporate structural similarity of common API usage (HttpURLConnection, BufferedReader)；Use dataflow analysis to capture shared read/write patterns

### case_id=668 FN partial_functionality

- 方法: `readIntoList` vs `register`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads HTML from a URL and parses link labels to populate a menu with action listeners.
- B 摘要: Registers a user by encoding password, setting date, creating hash, and calling an external forum URL to obtain a forum ID, then persisting the user and sending confirmation email.
- 静态失败原因: Static BERT models like GraphCodeBERT rely heavily on token-level similarity and may miss the structural overlap due to low token Jaccard (0.1448) and different domain-specific vocabulary (UI vs user registration). The long-range dependencies and different method signatures further confuse the model.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels pairs as clones if they share significant structural patterns, such as the URL reading loop with line-by-line parsing, even if the overall functionality differs. The common I/O pattern is considered a functional clone.
- 共享行为: Both open a URL and read lines using BufferedReader and InputStreamReader；Both process each line in a while loop；Both handle IOException with try-catch
- 行为差异: Function A creates JMenuItem components and populates a map; Function B persists a User entity；Function A extracts substrings between specific HTML tags; Function B parses a single integer from the response；Function A returns void; Function B returns boolean based on email sending success；Function B includes database persistence and external forum registration, missing in A
- 修正建议: Incorporate data-flow or control-flow graph alignment to detect shared subgraphs；Pre-train on tasks that emphasize functional similarity over token overlap；Use graph-based transformers that can capture structural patterns like I/O loops

### case_id=669 FN partial_functionality

- 方法: `fileDownload` vs `doVersionCheck`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a file from a URL to a local file by reading bytes from the stream and writing to a FileOutputStream.
- B 摘要: Checks for newer version by reading a URL, parsing lines for build versions, and calling another method if versions are found.
- 静态失败原因: Low token Jaccard (0.217) and different key terms (download vs version) caused the static model to miss the structural similarity in the common URL-reading pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB's broad clone definition includes Type-3/4 where shared common functionality like reading a URL stream until end is considered similar enough despite different purposes.
- 共享行为: Open a URL connection；Read from the input stream until exhaustion；Close the input stream
- 行为差异: A writes bytes to a file; B parses lines for version strings；A uses byte-level reading; B uses line-level reading with BufferedReader；A has no conditional logic based on content; B filters lines with specific prefixes；A writes to a hardcoded filename; B does not write to any file
- 修正建议: Use AST-based or graph-based models that capture control flow commonality；Incorporate data flow analysis to identify shared I/O operations；Train with contrastive examples of partial functional similarity

### case_id=670 FP lexical_or_api_overlap

- 方法: `getVersion` vs `postXml`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches a version string from a fixed URL via HTTP GET, returning null on failure.
- B 摘要: Sends an HTTP POST request with XML data to a given URL and returns the response, throwing RuntimeException on failure.
- 静态失败原因: The model likely over-relied on lexical and API overlap (URL, URLConnection, BufferedReader, etc.) and similar control flow (try-catch, while-read), missing semantic differences in HTTP method, headers, error handling, and overall intent.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clone because the methods have different signatures, HTTP methods, error handling, and purpose (version retrieval vs. XML posting). Only superficial API usage is similar, not enough for Type-3/4 in BCB's view.
- 共享行为: Both open a URLConnection to an HTTP endpoint；Both read the response line-by-line using BufferedReader；Both return a String representing the response body
- 行为差异: Method A uses GET (default) to a fixed URL; Method B uses POST with configurable URL；Method A returns null on exception; Method B throws RuntimeException；Method B sets multiple request headers, enables output, and writes request body; Method A does not；Method A is static; Method B is instance method
- 修正建议: Incorporate dataflow analysis to distinguish between GET and POST operations；Add contrastive examples where same APIs lead to different semantics；Use argument-level type and role information to differentiate input vs. output behavior

### case_id=671 FP boilerplate_overlap

- 方法: `encrypt` vs `perform`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Computes SHA hash of input string and returns base64-encoded hash value.
- B 摘要: Processes HTTP request to classify a concept, interacts with session, makes HTTP POST, parses XML response, and returns ActionForward.
- 静态失败原因: The model likely focused on superficial patterns like method signature (public synchronized String in A, public ActionForward in B), exception handling, or common keywords (e.g., 'try', 'catch'), while missing the vast difference in domain and semantics.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB expects semantic similarity for a clone pair; these functions share no common purpose or behavior, so they are non-clones.
- 共享行为: Both use exception handling (try-catch blocks).
- 行为差异: Function A performs a cryptographic hash; Function B handles a Struts web action.；Function A is a simple utility method; Function B has complex workflow with multiple components.；Input and output types are completely different (String vs HttpServletRequest/ActionForward).；Function A uses MessageDigest and BASE64Encoder; Function B uses many web-specific classes.
- 修正建议: Improve attention to domain-specific libraries and data flow across long code spans.；Incorporate structural information (e.g., AST or control flow) to distinguish generic patterns from core functionality.；Use contrastive learning with hard negative examples that share boilerplate but differ semantically.

### case_id=672 FP lexical_or_api_overlap

- 方法: `getFrameworkFactory` vs `doVersionCheck`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads META-INF/services file to load and instantiate FrameworkFactory class.
- B 摘要: Reads version check URL and extracts build versions, then calls another method to perform version check.
- 静态失败原因: Static BERT/GraphCodeBERT models may over-rely on surface-level token overlaps and API sequences (URL, BufferedReader, readLine, etc.) without grasping the high-level intent and control flow differences.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels as non-clone because the functions serve entirely different purposes (OSGi framework loading vs version checking) despite similar low-level I/O patterns.
- 共享行为: Both open a URL and read lines using BufferedReader；Both parse lines by checking prefixes and trimming
- 行为差异: Function A returns a FrameworkFactory instance, Function B is void；Function A throws an Exception if not found, Function B handles IOException and shows error dialog；Function A reads a fixed resource path, Function B reads a configurable URL；Function A processes only the first non-comment line, Function B reads all lines for specific tags
- 修正建议: Improve model to focus on semantic intent and data flow, not just API calls；Incorporate structural differences like return type and exception handling；Use program dependency graphs or higher-level semantics

### case_id=673 FN boilerplate_overlap

- 方法: `decodeFileToFile` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.3`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Decodes a Base64-encoded file and writes the decoded content to an output file, returning success status.
- B 摘要: Retrieves a resource URL, caches it locally if needed, and returns an InputStream to the local file, handling HTTP caching.
- 静态失败原因: The static BERT/GraphCodeBERT method correctly predicted non-clone (0) based on strict semantic differences and low token overlap (0.224). However, BCB's annotation considers a broader notion of clone, so the static method appears to have 'failed' by not aligning with BCB's lenient criteria.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may label these as clones (Type-3 or Type-4) due to the shared pattern of reading from an InputStream and writing to an OutputStream, along with similar exception handling and stream closing boilerplate, which could be seen as partial functionality similarity despite different high-level purposes.
- 共享行为: Both involve reading from an InputStream and writing to an OutputStream (or returning a stream).；Both use try-catch-finally blocks for resource management and stream closing.；Both write byte arrays or individual bytes to an output stream.
- 行为差异: Function A specifically decodes Base64 data; Function B does HTTP resource caching with conditional GET.；Function A returns boolean; Function B returns InputStream.；Function B has extensive caching logic, URL handling, and prints debug messages; Function A is simpler.；Function A uses a fixed-size buffer (65536); Function B reads byte by byte.
- 修正建议: Incorporate higher-level semantic understanding to differentiate between file decoding and resource caching.；Consider functional purpose beyond low-level stream operations.；Use more discriminative features like method signatures, return types, and domain-specific keywords.

### case_id=674 FN benchmark_preference_bias

- 方法: `compressWithZip` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Compresses a list of files into a ZIP archive using ZipOutputStream.
- B 摘要: Launches a NexOpen project configuration, processing pom.xml files and setting up Hibernate properties.
- 静态失败原因: Static BERT likely relied on token and structure similarity, which are very low (Jaccard=0.046). The model correctly identified non-clone based on low surface similarity, but BCB's label considered weak I/O similarity as sufficient for clone.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might label this as clone due to the presence of similar I/O boilerplate patterns (e.g., reading files using InputStream, copying streams) even though the overall functionality is completely different.
- 共享行为: Both handle file and stream I/O operations.
- 行为差异: Different purposes: compression vs. project launch.；Different data structures: vector of file names vs. XML DOM documents.；Different error handling: throws IOException vs. CoreException.
- 修正建议: Increase threshold for considering I/O boilerplate as evidence of cloning.；Incorporate high-level semantic understanding to distinguish different application domains.

### case_id=675 FP lexical_or_api_overlap

- 方法: `readPage` vs `readUNI`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a webpage line by line, optionally skipping comment lines starting with '#', and returns the concatenated string.
- B 摘要: Reads a TSV file from a URL, skips the header line, extracts the first and third fields (id and description), and adds them to a vector.
- 静态失败原因: The model likely overemphasized lexical and structural overlap (common API calls like URL, openStream, while loop, readLine/Scanner, close) while ignoring fundamental semantic differences in output and data processing logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels clones only when functions are semantically equivalent or near-equivalent. Here, the purposes are distinct: one reads an entire page with optional comment filtering, the other parses a specific structured format. Thus, not a clone under BCB annotation preference.
- 共享行为: Both read from a URL using openStream；Both process lines from the stream；Both close the stream after reading
- 行为差异: Method A returns a String; Method B modifies a Vector；A filters lines by comment prefix; B parses tab-separated fields；A uses BufferedReader; B uses Scanner；A has a parameter ignoreComments; B skips first line unconditionally
- 修正建议: Enhance model to focus on output types and data transformations；Incorporate dataflow analysis to distinguish different processing logic；Use graph-based representations that capture control and data dependencies beyond API sequences

### case_id=676 FP lexical_or_api_overlap

- 方法: `startScript` vs `getFullScreenUrl`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Opens a URL and reads lines to append to a script buffer.
- B 摘要: Opens a YouTube page URL, searches for fullscreenUrl line, parses parameters, constructs a video URL.
- 静态失败原因: Static BERT/GraphCodeBERT models may rely heavily on token similarity and structural overlap. Here, both have similar tokens like 'URL', 'BufferedReader', 'readLine', 'IOException', etc. The model might overfit on these API calls and miss the semantic difference in control flow and purpose.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled as non-clone because although both use URL reading boilerplate, the core logic and purpose are different: one loads a script, the other extracts video URL. The similarity is only in the opening and reading pattern, not in the overall functionality.
- 共享行为: Both open a URL and read lines using BufferedReader
- 行为差异: Function A appends all lines to a script string; Function B searches for a specific line containing 'fullscreenUrl'；Function A uses a parameter for URL; Function B uses an instance variable；Function A exits on IOException; Function B catches Exception and continues；Function A modifies dialog.script; Function B returns a string and sets instance variable
- 修正建议: Improve model sensitivity to high-level semantics by incorporating data flow and control flow differences；Use contrastive learning to distinguish between boilerplate-sharing but functionally different functions；Consider function-level embeddings that capture output/input behavior

### case_id=677 FP lexical_or_api_overlap

- 方法: `getFrameworkFactory` vs `PhoneSetImpl`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads an OSGi service configuration file from a URL and returns a FrameworkFactory instance, throwing an exception if not found.
- B 摘要: Reads a phone set definition file from a URL, parses lines not starting with '***', and populates a map while counting lines.
- 静态失败原因: Static BERT/GraphCodeBERT models overemphasize lexical and API token overlap (URL, BufferedReader, readLine) while missing the semantic intent difference between returning a factory and populating a map.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels these as non-clones because they perform fundamentally different tasks (service loading vs. data initialization) despite sharing an I/O pattern.
- 共享行为: Both read from a URL using BufferedReader；Both iterate over lines and skip comment-like lines；Both use similar boilerplate for stream handling
- 行为差异: A returns a single FrameworkFactory object; B populates an internal map in a constructor；A skips lines starting with '#'; B skips lines starting with '***'；A throws an exception if no valid line found; B does not throw, only processes lines
- 修正建议: Incorporate data flow and output type analysis；Use contrastive learning to distinguish different tasks with similar API sequences；Focus on high-level semantic role (return vs. state mutation)

### case_id=678 FN benchmark_preference_bias

- 方法: `main` vs `download`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a hardcoded URL, extracts its zip entries to files.
- B 摘要: Downloads a resource file from the classpath to a user-selected file path.
- 静态失败原因: Static BERT correctly predicted non-clone based on low lexical overlap and semantic differences; the BCB label is overly broad, causing the 'failure' due to benchmark preference bias.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider both as 'file download/write' operations, leading to a broad Type-4 clone label despite different sources and processing.
- 共享行为: Both read from an input stream and write to an output stream.
- 行为差异: CodeA extracts zip entries; CodeB copies a single file.；CodeA uses hardcoded URL; CodeB uses classpath resource.；CodeA lacks error handling; CodeB has try-catch-finally with exception dialogs.
- 修正建议: Improve detection of broader functional categories like 'file download/write', but beware of false positives.

### case_id=679 FN partial_functionality

- 方法: `sendExceptionToServer` vs `readReferenceText`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends an exception report to a server by encoding parameters into a URL query string and performing an HTTP POST, then reads and logs the response.
- B 摘要: Reads the content of a text file referenced by an identifier from a plugin bundle using a URL stream, and returns it as a string.
- 静态失败原因: Static BERT/GraphCodeBERT models rely heavily on token-level similarity and local context; the low Jaccard similarity (0.1875) and different method names caused the model to miss the broader functional overlap. The model likely focused on the distinct API call sequences (e.g., URLEncoder, OutputStreamWriter in A vs. getFilename, getEntry in B) and missed the abstract pattern of URL-based I/O operations.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considers these clones because both functions perform network I/O operations involving URL handling, stream reading/writing, and exception handling, which are functionally similar at a high level (Type-4 clone). The shared structure of opening a URL, reading lines, and handling I/O exceptions outweighs the differences in direction (read vs. write) and purpose.
- 共享行为: Both open a URL and use streams (InputStreamReader, BufferedReader) for I/O；Both handle IOException in a try-catch block；Both read line-by-line from a buffered reader
- 行为差异: Function A sends data via HTTP POST (writes to OutputStreamWriter), while function B only reads data；Function A builds a complex query string with URL-encoded parameters; function B simply reads lines and appends newline characters；Function A prints output to console; function B returns the string content；Function A uses URLConnection with setDoOutput(true); function B uses URL.openStream()
- 修正建议: Incorporate abstract syntax tree (AST) or control flow based features to capture structural similarity beyond tokens；Use dataflow analysis to identify common I/O patterns (e.g., open URL, stream read/write, exception handling)；Augment training data with more diverse examples of Type-4 clones (semantic equivalents with low token overlap)；Employ contrastive learning methods that emphasize functional similarity over lexical overlap

### case_id=680 FN partial_functionality

- 方法: `createTar` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Creates a tar archive from all files in a given directory.
- B 摘要: Retrieves a resource as an InputStream, with caching to a local file.
- 静态失败原因: Static BERT models rely on token overlap and syntactic structure, which are low (Jaccard 0.11). The different method names ('createTar' vs 'getResourceAsStream') and distinct API calls lead to a non-clone prediction, missing the underlying I/O pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may accept these as clones because both functions share a core behavioral pattern of reading from an input source and writing to an output destination using buffered streams, which constitutes partial functionality similarity (Type-4).
- 共享行为: Both functions perform file I/O operations with buffered streams.；Both functions read from a source and write to a destination in a loop.；Both functions handle resource cleanup in try-finally blocks.
- 行为差异: Function A creates a tar archive; Function B retrieves a resource and caches it.；Function A processes multiple files; Function B handles a single resource with HTTP and caching.；Function A uses TarOutputStream specialized for tar; Function B uses generic FileOutputStream.；Function B includes HTTP connection handling and cache management absent in A.
- 修正建议: Use data-flow or graph-based representations to capture behavioral similarities.；Train on function-level embeddings that abstract away specific API names.；Employ contrastive learning to focus on functional similarity over lexical overlap.

### case_id=681 FP boilerplate_overlap

- 方法: `main` vs `readData`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Decompresses a GZIP file given a command-line argument.
- B 摘要: Reads configuration strings and a file to populate data structures for Tibetan transliteration.
- 静态失败原因: Static BERT/GraphCodeBERT may have been misled by superficial lexical overlap (e.g., common keywords like 'try', 'catch', 'IOException', 'new', 'String') and similar structural patterns (static method, loops, try-catch), ignoring the distinct application logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels as non-clone because the functions have completely different purposes (file I/O vs. data initialization) with no shared functionality beyond basic Java boilerplate.
- 共享行为: Both are static methods.；Both use try-catch blocks for exception handling.；Both use standard Java I/O and collections.
- 行为差异: Function A performs file decompression; B builds lookup tables from config data.；Function A uses command-line arguments; B uses class fields for input.；Function A has simple byte copying; B has complex token parsing and conditional logic.
- 修正建议: Incorporate data flow and control flow analysis to distinguish behaviors.；Use finer-grained tokenization that highlights variable roles and I/O operations.；Train with more discriminative negative examples that share boilerplate but differ in semantics.

### case_id=682 FN boilerplate_overlap

- 方法: `scrapeForIsbns` vs `File2String`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.6`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Scrapes ISBN-10 numbers from a URL with retry logic, counting matches and storing them.
- B 摘要: Reads a file (or classpath resource) into a single string, exiting on failure.
- 静态失败原因: The model likely focused on the different high-level goals and operations, missing the structural similarity that BCB considered as a clone, leading to a false negative against the benchmark.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may have annotated this as a clone due to the shared boilerplate pattern of reading from a stream line-by-line, considering it a Type-3 near-miss clone despite different functional purposes.
- 共享行为: Both open an input stream；Both use BufferedReader to read lines in a loop；Both handle IOException
- 行为差异: Input source: URL vs file；Operation on lines: regex matching vs string concatenation；Output: integer count vs full string；Error handling: retry vs exit
- 修正建议: Incorporate control flow graph similarity；Use structural clone detection techniques；Adjust threshold to account for Type-3 clones

### case_id=683 FN lexical_or_api_overlap

- 方法: `getResourceAsStream` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Retrieves a resource by name, with HTTP caching and local file caching, returning an InputStream.
- B 摘要: Writes license information for all jars in a directory to a text file.
- 静态失败原因: Static BERT models rely on token and local pattern similarity; they may see common API tokens like FileInputStream/FileOutputStream and loops, missing the high-level semantic difference.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB might consider them clones due to shared file I/O operations, but this is a very broad Type-4 similarity that does not reflect meaningful semantic equivalence.
- 共享行为: Both perform file I/O using streams
- 行为差异: Different purpose: resource retrieval vs. license file generation；Function A involves HTTP connections and caching; B does not；Function A returns an InputStream; B writes to a file；Function A handles caching logic; B does not
- 修正建议: Incorporate data flow and control flow analysis to distinguish different high-level tasks.；Use larger context or documentation embeddings to capture intent.

### case_id=684 FP lexical_or_api_overlap

- 方法: `getVersion` vs `readURL`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Retrieves the latest version string from a hardcoded remote URL.
- B 摘要: Reads and prints all lines from a given URL to standard output.
- 静态失败原因: The model likely overemphasized lexical overlap and common API calls (URL, BufferedReader) while ignoring differences in return type, side effects, and resource management.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels non-clones when functions have similar boilerplate but different purposes, outputs, and error handling, as in this case.
- 共享行为: Open a URL；Read lines using BufferedReader
- 行为差异: A returns the last line, B prints all lines；A returns null on exception, B prints stack trace；A does not close resources, B closes in finally block；A uses a hardcoded URL, B takes URL as parameter
- 修正建议: Incorporate return type and exception handling patterns；Use data flow analysis to distinguish output behavior；Train on more diverse examples of similar API usage with different semantics

### case_id=685 FP lexical_or_api_overlap

- 方法: `importSequences` vs `postXml`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads sequences from a URL in FASTA-like format, parsing names and sequences.
- B 摘要: Sends an XML payload via HTTP POST and returns the response as a string.
- 静态失败原因: The model may have been misled by lexical similarity (URL, openStream, read, while loop with readLine) and boilerplate for network I/O, ignoring the distinct control flow and data processing logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels these as non-clones because they perform completely different tasks: one imports sequence data, the other posts XML. Despite both using URLs, the functionality is unrelated.
- 共享行为: Both open a URL connection and handle IOException.；Both read data from an input stream.
- 行为差异: A reads from a URL and parses a specific text format; B posts data to a URL and reads the response.；A uses readLine and tokenization to extract fields; B uses XML and SOAP headers.；A stores results in lists; B returns a concatenated response string.；A handles multiple records in a loop; B sends a single request and returns the response.
- 修正建议: Incorporate control flow and data flow analysis to distinguish parsing from posting.；Use program slicing to focus on core functional logic beyond common I/O patterns.；Train on more diverse examples to reduce reliance on surface-level API matches.

### case_id=686 FP lexical_or_api_overlap

- 方法: `readUNI` vs `callApiPost`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a TSV file from a URL, parses lines, and adds id and description to a vector.
- B 摘要: Makes an HTTP POST request to an API with parameters, checks response code, and returns an InputStream.
- 静态失败原因: Static BERT models may overemphasize lexical overlap (URL, IOException, Scanner/PrintStream) and structural similarity (try-catch-finally) while missing the distinct data flow and functional goals.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels non-clones when functions have clearly different purposes despite some API-level similarities, as here one is file parsing and the other is HTTP API invocation.
- 共享行为: Both open a URL connection and handle IO exceptions.；Both use InputStream to read data from a URL.
- 行为差异: A parses tab-separated lines into a vector; B sends POST data and processes response based on HTTP status.；A returns void; B returns an InputStream.；A catches MalformedURLException silently; B throws a custom BingMapsException on failure.
- 修正建议: Incorporate semantic features like method name, return type, and specific operations (parsing vs. HTTP)；Use data-flow analysis to distinguish between reading-as-stream vs. reading-parse-and-collect；Add negative sampling of similar-looking but different functions

### case_id=687 FN benchmark_preference_bias

- 方法: `doGet` vs `unzip`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Handles HTTP GET request to retrieve and render a page with permission checks and optional caching.
- B 摘要: Extracts contents of a zip file into a directory, handling nested directories and files.
- 静态失败原因: Static BERT/GraphCodeBERT likely correctly predicted non-clone due to low lexical overlap (Jaccard 0.096) and clear semantic difference; the BCB label appears to be an outlier, so the model did not actually fail.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this pair as clone due to broad interpretation of partial functionality similarity, such as both performing file I/O (A writes to temp file, B reads zip) and exception handling, but this is too generic for meaningful clone detection.
- 共享行为: Both involve I/O operations (network vs file) and exception handling.
- 行为差异: Function A is an HTTP request handler with database queries, permission checks, and page rendering; Function B is a file extraction utility.；They use completely different libraries and control flows.；No common algorithmic steps or data processing patterns.
- 修正建议: Re-evaluate BCB annotations for this pair to ensure consistency with standard clone definitions.；Improve benchmark by filtering out pairs with only superficial I/O overlap.

### case_id=688 FN benchmark_preference_bias

- 方法: `init` vs `fileDownload`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `preference_memory_with_manual_audit`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Loads classes from a registry file specified by a constant filename, reading lines from URL resources.
- B 摘要: Downloads a file from a given URL and saves it to a destination directory.
- 静态失败原因: Static BERT/GraphCodeBERT likely predicted non-clone because the token Jaccard is low (0.17) and there is no syntactic similarity. The model may have been misled by the shared API calls (URL, BufferedReader, InputStreamReader) but still distinguished the different core logic. However, BCB's broader clone definition considered it a clone, so the model's strict semantic understanding actually aligned with strict definition but not BCB's broader definition.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider this a Type-4 clone because both functions follow the same pattern of opening a URL, reading its contents line by line, and processing the data. Even though the processing logic differs, the high-level semantics of 'retrieve and process data from a URL' are similar, which BCB sometimes accepts as partial functionality clones.
- 共享行为: Both read data from a URL using BufferedReader and InputStreamReader；Both use try-catch for exception handling；Both involve loops reading from the input stream
- 行为差异: Function A loads classes by reading class names and calling loadClass/addClass; Function B writes bytes to a file.；Function A uses classLoader.getResources to find multiple URLs; Function B uses a single URL parameter.；Function A filters lines (ignoring empty/comment); Function B writes all characters to a file.；Function B creates and writes to a FileOutputStream; Function A does not write to files.
- 修正建议: Incorporate high-level semantic patterns like 'read from URL and process' into clone detection by using code summarization or abstract representations.；Train on BCB's specific annotation guidelines to better capture Type-4 clones based on overall functionality rather than exact implementation.；Use lightweight semantic similarity from API call sequences to detect clones with different low-level logic but similar high-level intent.

### case_id=689 FP boilerplate_overlap

- 方法: `main` vs `convert`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Generates adapter JAR files from Prolog source files using specific libraries.
- B 摘要: Converts ACRNEMA image files to DICOM format with pixel data handling.
- 静态失败原因: Static BERT might have overgeneralized common patterns like file I/O, try-catch, and print statements, or focused on superficial structural similarities.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels as non-clone because the functions have completely different domains and implementations, with only generic boilerplate overlap.
- 共享行为: Both read input files and write output files.；Both use System.out.println for user messages.；Both perform conditional checks and return early on failures.
- 行为差异: Function A processes Prolog code and generates Java classes; Function B processes image data and converts formats.；Function A uses complex library-specific classes (e.g., PrologParser, FactVisitor, ClassWriter); Function B uses DICOM-specific classes (e.g., DcmParser, Dataset).；Function A writes a JAR file; Function B writes a DICOM file.；Function A has a complex pipeline with multiple visitors and generators; Function B has straightforward pixel data manipulation.
- 修正建议: Improve training with more diverse negative examples that share boilerplate.；Incorporate domain-specific features to distinguish library usage.

### case_id=690 FP lexical_or_api_overlap

- 方法: `readData` vs `copyExternalResource`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Parses comma-separated tokens from multiple string fields into sets and maps, with additional logic for handling a file-based configuration (e.g., tibwn.ini).
- B 摘要: Copies a file from source to destination using NIO FileChannel, ensuring the destination file exists and closing channels properly.
- 静态失败原因: Static BERT/GraphCodeBERT likely over-relied on overlapping API tokens like 'IOException' and 'File' (though not explicit in code_a) and common control structures (try-catch, if-else), ignoring the fundamental difference in behavior.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels these as non-clones because they perform completely different tasks with no semantic overlap; both are standalone utilities, not variants of the same functionality.
- 行为差异: Function A reads and processes string tokens to populate data structures; function B copies a file byte-by-byte.；Function A involves complex parsing and multiple mappings; function B is a straightforward file copy.；Function A includes error handling specific to file parsing; function B handles file existence and channel closing.；Function A uses StringTokenizer and HashSet; function B uses FileInputStream/FileOutputStream and FileChannel.
- 修正建议: Incorporate dataflow or control-flow analysis to distinguish between file parsing and file copying.；Use contrastive learning with hard negative examples that share I/O APIs but different semantics.；Increase token-level sensitivity by penalizing high jaccard but low semantic similarity.

### case_id=691 FN partial_functionality

- 方法: `runScript` vs `handledRun`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a script file from a URL and returns its content as a string, with error handling.
- B 摘要: Downloads a specific XML file from a URL, checks version, and updates local data with file writing and database loading.
- 静态失败原因: Static BERT models rely on token overlap and structural similarity. The low Jaccard similarity (0.137) and different method signatures, control flow (A simple, B conditional with file I/O), and API usage (BufferedInputStream vs BufferedReader) led the model to miss the broad semantic similarity of URL fetching.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels clones based on broad functional similarity, accepting Type-3/Type-4 clones. Both methods perform a network fetch operation with similar byte-reading loops and exception handling, so the partial overlap in core behavior qualifies as a clone under BCB's lenient criteria.
- 共享行为: Both open a URL and read data from the stream；Both use a while loop to read bytes until end of stream；Both handle I/O exceptions
- 行为差异: A returns the data as a string; B writes to a file and also performs version comparison；A is generic (takes script name); B is fixed to a specific URL and file；B includes additional logic for database loading and version check；B has more complex error handling with specific exceptions and user dialog
- 修正建议: Use models that capture data flow and control flow graphs to identify common substructures；Train with more examples of partial clones where only a subset of behavior is shared；Incorporate type information and library knowledge to recognize similar I/O patterns

### case_id=692 FN partial_functionality

- 方法: `cpFile` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a local file to a target location, with options for overwriting and buffer size, handling naming conflicts.
- B 摘要: Retrieves a resource from a URL, caches it locally with HTTP conditional logic, and returns an InputStream to the cached file.
- 静态失败原因: Low token overlap (Jaccard 0.17), different method names, APIs, and control flow caused the model to miss the abstract similarity of stream copying, leading to a false negative.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider them Type-4 clones because both functions achieve the abstract goal of copying data from a source to a destination file, despite differences in source type and additional logic.
- 共享行为: Reads from an InputStream and writes to a FileOutputStream until the end of the stream
- 行为差异: cpFile copies a local file to a specified target with conflict resolution; getResourceAsStream retrieves a remote resource and caches it；cpFile does not handle URLs or caching; getResourceAsStream includes HTTP handling and cache management；cpFile reads in buffer chunks; getResourceAsStream reads byte by byte；cpFile throws IOException; getResourceAsStream catches exceptions and returns null
- 修正建议: Enhance model ability to recognize core data transfer patterns even with divergent surrounding code；Incorporate data flow analysis to detect input/output stream operations as a shared semantic feature

### case_id=693 FP other

- 方法: `actionPerformed` vs `addRecord`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Handles UI action events for setting various application preferences via file choosers, including Graphviz path, ImageMagick path, scaling options, date format, look-and-feel, etc.
- B 摘要: Stores an input stream as a file in a hash-based data store, using a temporary file and digest to generate a unique identifier, with collision handling.
- 静态失败原因: Despite very low token Jaccard similarity (0.086%), the model may have been misled by common Java boilerplate constructs (try-catch, file I/O, method structure) or by the long, truncated nature of function A causing confusion. The false positive could also result from training data bias or overgeneralization of partial patterns.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely rejected this pair because there is no common functionality; they belong to completely different application domains (UI preferences vs. data storage).
- 行为差异: Function A is a UI event handler for preference settings; function B is a data storage method.；Function A interacts with file choosers and preference storage; function B reads an input stream, computes hash, and manages file renaming.；No overlap in domain, logic, or purpose.
- 修正建议: Enhance model sensitivity to structural and semantic differences, e.g., by incorporating control flow or data dependency graphs.；Improve handling of long functions with truncation to avoid losing critical context.；Use domain-specific embeddings or contrastive learning to separate unrelated tasks.

### case_id=694 FN lexical_or_api_overlap

- 方法: `modifyApplicationMessage` vs `encodeFileToFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Modify a properties file by replacing or appending a message value for a given locale.
- B 摘要: Encode a file to Base64 and write it to another file.
- 静态失败原因: The low lexical overlap (Jaccard 0.206) caused the model to classify as non-clone, missing the structural similarity that BCB possibly valued.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB's broad Type-3/Type-4 criteria might consider both as file transformation routines with similar control flow (read-process-write), despite different core logic.
- 共享行为: Both read from an input source and write to an output file.；Both use try-catch blocks to handle exceptions.；Both close input/output streams in a finally-like manner.
- 行为差异: Function A processes properties files with key-value parsing, while B performs Base64 encoding.；Function A may copy a default file if target missing; B always encodes.；Function A returns void; B returns boolean success flag.
- 修正建议: Train with clone examples that have low lexical overlap but structural similarity.；Incorporate graph-based or control-flow features to capture common I/O patterns.

### case_id=695 FN benchmark_preference_bias

- 方法: `genCustRatingFileAndMovieIndexFile` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Reads binary movie ratings file and generates index and rating output files using NIO channels.
- B 摘要: Launches Eclipse configuration by processing POM files, setting Hibernate dialect, and managing project resources.
- 静态失败原因: Static model correctly predicted non-clone, aligning with low token overlap; BCB label appears erroneous
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: Likely a misannotation in BCB dataset; no justification for clone label
- 共享行为: No meaningful shared behavior beyond generic file I/O
- 行为差异: Entirely different domain (movie ratings vs Eclipse launch configuration)；Different data types and file formats；Different control flow and return types
- 修正建议: Verify BCB annotation; consider removing this pair from clone set

### case_id=696 FP partial_functionality

- 方法: `readUNI` vs `lookupFutureEvents`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a tab-separated file from a URL and adds id-description pairs to a vector.
- B 摘要: Fetches event data from the Meetup API, parses JSON, and returns a list of Event objects.
- 静态失败原因: Static BERT models might overemphasize the similarity of opening URLs and reading lines (lexical overlap) and miss the vast difference in subsequent processing and output semantics.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB would not consider them clones because they have distinct functionality and output, despite both involving URL reading.
- 共享行为: Both open a URL and read data from it line by line.
- 行为差异: Different data format: TSV vs JSON；Different outputs: modifies input vector vs returns List<Event>；Different error handling: silent catch vs throwing exception；Different processing: simple tokenization vs complex field mapping
- 修正建议: Train model with more diverse examples to learn that common API usage does not imply semantic equivalence.；Incorporate control flow and data flow analysis to distinguish different processing after reading.

### case_id=697 FN partial_functionality

- 方法: `main` vs `copyFileTo`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a URL, extracts its ZIP entries, and writes each entry to a separate file.
- B 摘要: Copies a source file to a destination file byte by byte.
- 静态失败原因: Static BERT models may rely on syntactic token overlap and structural patterns; the while loop and IO operations create surface similarity, leading to a false negative when the model fails to capture the functional difference.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB might label this as a clone due to the similar IO loop pattern (reading bytes and writing in a while loop), but the overall functionality is different; this is a case of broad Type-4 partial similarity.
- 共享行为: Both read data from an input stream；Both write data to an output stream in a loop；Both use a byte buffer
- 行为差异: Function A downloads from URL; function B reads from local file；Function A processes a ZIP archive with multiple entries; function B copies a single file；Function A writes to multiple output files (one per entry); function B writes to one file；Function A uses ZipInputStream; function B uses FileInputStream
- 修正建议: Improve detection of structural differences such as different input sources and loop contexts；Incorporate understanding of the overall goal of functions beyond low-level operations

### case_id=698 FP boilerplate_overlap

- 方法: `createSettingsIfNecessary` vs `main`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Creates a settings file by copying from a bundled resource if it does not already exist.
- B 摘要: Main method that parses command line arguments, reads a Prolog file, and generates adapter classes and a JAR file.
- 静态失败原因: Static BERT models may have been misled by boilerplate code (e.g., file existence checks, output streams) and similar variable names ('out'), ignoring the vast difference in overall logic and domain.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would not label these as clones because they implement completely different functionalities with no semantic overlap beyond basic I/O patterns.
- 共享行为: Both involve file I/O operations (checking existence, reading/writing).；Both use try-catch or try-finally blocks for resource management.；Both have variables named 'out' representing output streams.
- 行为差异: A is a simple file copy for a single settings file; B is a complex code generation pipeline for Prolog adapters.；A is a protected instance method; B is a public static main method with command-line parsing.；A uses a bundled resource as input; B reads a user-specified Prolog file and requires class paths.；B involves parsing, visiting, generating annotations, assembling JARs, and serialization; A has none of that.
- 修正建议: Train on more diverse data to reduce sensitivity to common I/O patterns.；Incorporate control flow and data flow analysis to capture semantic intent.；Use whole-method embedding that emphasizes unique library calls and logic structure.

### case_id=699 FN benchmark_preference_bias

- 方法: `doVersionCheck` vs `runInternal`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Checks for a newer version of jEdit by downloading a version file from a URL and comparing build numbers.
- B 摘要: Loads OPDS catalog items from a URL by handling HTTP connections, parsing XML, downloading books, and managing pagination.
- 静态失败原因: Static BERT/GraphCodeBERT likely failed because the functions have low lexical overlap and different control flow, and the model correctly identified them as non-clones based on structural differences; thus it actually got it right, contradicting BCB.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have considered both as 'fetching data from URL and parsing', but this is too broad; likely an annotation error or a case of benchmark bias toward partial functionality similarity.
- 共享行为: Both open a URL to fetch remote data
- 行为差异: Function A is a simple version check, while Function B is a complex multi-step OPDS catalog loader；Function A uses basic URL connection, while Function B handles HTTPS, redirects, content types, authentication；Function B includes pagination, multiple pages, and book downloading, which A does not；Error handling differs: A shows messages, B shows errors and calls callback onError
- 修正建议: Re-evaluate BCB annotation for this pair; possibly it is a false positive in BCB；Use more fine-grained clone detection that distinguishes between different types of network operations.

### case_id=700 FN partial_functionality

- 方法: `getEncoding` vs `doVersionCheck`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Extracts character encoding from a URL's HTTP headers or content by searching for 'charset' or 'encoding' patterns.
- B 摘要: Checks for a new version of jEdit by reading a remote version file and comparing build numbers, showing UI messages.
- 静态失败原因: Low token overlap (Jaccard 0.186) leads to different embeddings; function names and domain-specific tokens ('charset' vs '.version') are dissimilar, so the model fails to capture the abstract 'read-parse' pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may annotate as clone because both methods follow a similar algorithmic pattern: open URL, read lines, parse for specific patterns, and handle IO. This is a Type-4 semantic clone where the control flow and I/O structure are analogous despite different domain-specific logic.
- 共享行为: Open a URL and read lines via BufferedReader；Parse each line for specific string prefixes；Contain try-catch for IOException；Use a loop to iterate over lines
- 行为差异: A looks for charset/encoding in headers and body; B looks for .version and .build tags；A returns a String encoding; B is void and displays UI dialogs；A has a fallback default encoding; B compares build numbers and shows version info
- 修正建议: Incorporate data-flow analysis to detect similar I/O patterns regardless of domain vocabulary；Use code summarization techniques to identify high-level intent similarity；Train on pairs with similar structural patterns but different application domains

### case_id=701 FN benchmark_preference_bias

- 方法: `testCopy_inputStreamToOutputStream` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `1.0`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: A JUnit test that copies an InputStream to an OutputStream and asserts correct byte counts and content.
- B 摘要: A method that builds a website for editing by reading XML, transforming it, and writing output files.
- 静态失败原因: The static method correctly predicted non-clone; it did not fail.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: The BCB label of 1 appears to be an annotation error; there is no functional overlap.
- 行为差异: Function A is a simple test; Function B is a complex site builder.；Function A uses IOUtils.copy; Function B uses custom file and XML processing.；Function A has no external dependencies; Function B relies on multiple libraries.；Function A is 10 lines; Function B is over 100 lines.
- 修正建议: Correct the BCB label to 0 for this pair.；Implement manual verification for such low-similarity pairs.

### case_id=702 FP boilerplate_overlap

- 方法: `readIntoList` vs `downloadModel`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads HTML from a URL and populates a map of JMenuItems with action listeners.
- B 摘要: Downloads an RDF model from a URL and returns it as a Model object.
- 静态失败原因: The model likely overemphasized the shared structural pattern of URL reading and try-catch, ignoring the distinct semantic contexts and functionality.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels as non-clone because the functions have entirely different purposes and core logic; the only similarity is boilerplate I/O code, which is insufficient for Type-3/4 in BCB.
- 共享行为: Both open a URL connection and read from an input stream；Both close the input stream after reading
- 行为差异: Different processing: HTML parsing for menu items vs. RDF model reading；Different return types: void vs. Model；Different exception handling: printStackTrace vs. throw RuntimeException；Different input: Map parameter vs. no extra parameter
- 修正建议: Focus on core logic beyond I/O boilerplate；Incorporate data flow and output type analysis；Use contrastive learning to distinguish similar boilerplate with different semantics

### case_id=703 FN partial_functionality

- 方法: `copyTo` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Recursively copies files and directories from source to destination, skipping hidden files and using FileChannel for efficient transfer.
- B 摘要: Launches a NexOpen project by processing XML configuration files, setting up Hibernate dialect, creating a reverse engineering file, and triggering an installation action.
- 静态失败原因: Static BERT correctly identified low token overlap and different method names/contexts, predicting non-clone. However, BCB label is 1, so from BCB perspective, the model failed because it did not capture the underlying file I/O commonality that BCB annotators considered as clone.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider them clones due to broad Type-4 criteria: both functions involve reading from a source (file/configuration) and writing to a destination (file/project), and both include error handling and logging. The annotator might have focused on the file manipulation aspect.
- 共享行为: Both perform file I/O operations；Both handle exceptions and log errors
- 行为差异: A is a general-purpose file copy utility; B is a specific Eclipse launch configuration for NexOpen projects；A uses FileChannel for copying; B uses XML parsing, property setting, and project manipulation；A is recursive for directories; B processes multiple files sequentially but not recursively
- 修正建议: Train with examples that distinguish between true functional equivalence and tangential file I/O similarities；Use contrastive learning to focus on core logic rather than peripheral operations

### case_id=704 FP lexical_or_api_overlap

- 方法: `sendRequest` vs `getTicketsForQueue`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Sends an XML request to a servlet via HTTP with compression, using a dialog to configure server URL and port.
- B 摘要: Queries a Request Tracker system for open tickets in a queue via REST API, parses ticket IDs, and retrieves each ticket.
- 静态失败原因: Likely due to lexical or API overlap: both use HTTP-related classes (URL, HttpGet) and I/O streams, leading the model to focus on common structural patterns while missing the semantic difference in purpose and data handling. The low Jaccard similarity (0.08867) suggests the model may have been misled by the boilerplate code of network communication.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels as non-clone because the functions have entirely different business logic and only superficial similarity in using HTTP and I/O. BCB's broad Type-4 requires similar functionality, which is absent here.
- 共享行为: Both make HTTP requests；Both handle responses with error handling；Both use I/O streams for reading/writing
- 行为差异: Different HTTP methods: POST vs GET；Different request formats: XML body vs URL query parameters；Different purposes: generic request sending vs ticket retrieval；Different outputs: empty string vs list of tickets
- 修正建议: Incorporate method name or context to capture intent；Use dataflow analysis to distinguish different I/O operations；Train with more diverse examples of network functions with different semantics

### case_id=705 FP boilerplate_overlap

- 方法: `byReference` vs `readData`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Creates a temporary file from input stream and returns an immutable content object.
- B 摘要: Parses multiple comma-separated string fields to populate character sets and mapping tables for Tibetan Wylie transliteration.
- 静态失败原因: The low token similarity (0.0359) suggests the model may have been misled by common structural patterns like try-catch blocks and loop structures, leading to a false positive due to boilerplate overlap.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would not consider them clones because they have completely different functionality and purpose.
- 行为差异: Function A writes stream to file; B parses string tokens into data structures.；Function A returns a DigitalObjectContent; B returns void and populates static sets/maps.；Function A has simple IO; B has complex conditional logic and multiple loops.；Function A only handles one input; B handles multiple string fields and file reading.
- 修正建议: Improve model to distinguish boilerplate from core logic.；Use larger context or entire method embedding to capture functionality.；Apply data-flow analysis to differentiate IO operations from string tokenization.

### case_id=706 FN lexical_or_api_overlap

- 方法: `addIDs` vs `doVersionCheck`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.65`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches metabolite data from a remote GMD database URL using the given name, parses HTML to extract molecular weight and various IDs, and updates a PeakListRow with those values, returning a score.
- B 摘要: Checks for a newer version of jEdit by reading a version file from a URL, compares build numbers, and shows a dialog to the user indicating new version availability or up-to-date status.
- 静态失败原因: Static BERT models (e.g., GraphCodeBERT) rely on token-level similarity and learn domain-specific identifiers. The low token Jaccard (0.17) and distinct domain-specific terms (e.g., 'Metabolites', 'jEdit') cause the model to focus on lexical differences, missing the common higher-level pattern of URL reading and line parsing. The model lacks understanding of control-flow and data-flow structures that are shared.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may consider these clones due to the high-level structural similarity: both functions fetch data from a URL, parse lines with conditional logic, and use the parsed results. This falls under BCB's Type-3/Type-4 clone category where functionally similar behaviors (network-based data retrieval and processing) are considered clones despite different specific domains.
- 共享行为: Both open a URL and read lines from the response using BufferedReader；Both parse each line to extract specific substrings or key-value pairs；Both handle IOException with error logging or user messages；Both return or side-effect based on parsed data
- 行为差异: Different URLs and data sources (GMD metabolite database vs jEdit version file)；Different parsing logic (HTML tag extraction vs prefix-based line matching)；Different return types (int score vs void with side effects on View)；Different parameter types (PeakListRow and String vs View)
- 修正建议: Use data-flow/control-flow graph-based models (e.g., code2vec or AST-based) to capture structural patterns independent of identifiers.；Augment training with synthetic clones that share only high-level patterns but differ in domain-specific vocabulary.；Incorporate type or API usage embeddings to abstract away from literal strings and domain-specific classes.

### case_id=707 FN partial_functionality

- 方法: `lookupFutureEvents` vs `seeURLConnection`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches event data from a Meetup API by constructing a URL, reading JSON, and parsing detailed event information into Event objects.
- B 摘要: Opens a URL connection to a static website, reads the entire response content into a string, and logs it.
- 静态失败原因: Static BERT models rely on token overlap and syntactic structure. The low Jaccard (0.129) and divergent method signatures, combined with the extensive JSON and date parsing code in A, obscured the shared URL reading pattern. The model likely focused on the larger, unique parts of A.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BigCloneBench often considers functions with the same underlying I/O pattern as clones (Type-3/Type-4), especially when they share a non-trivial sequence like URL.openStream() read loop. The core algorithmic behavior of fetching URL content is identical.
- 共享行为: Both create a URL object and open an input stream；Both read input line by line using BufferedReader and append to a StringBuilder；Both close the reader in a finally-like pattern (not shown but implied)
- 行为差异: A parses complex JSON structure and creates multiple Event objects; B only logs raw content；A includes error handling for IOException and ParseException; B does not handle exceptions aside from generic throws；A uses HTTP GET with a query parameter and API key; B uses a constant URL；A returns a List<Event>; B returns void
- 修正建议: Use a graph-based model that captures control flow and data flow to identify shared subgraphs (e.g., URL open and read loop)；Incorporate token-level attention with weighted focus on I/O primitives；Train with positive examples that have low lexical overlap but share core algorithmic steps

### case_id=708 FP boilerplate_overlap

- 方法: `read` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a camera log from a URL, parses each line into CameraLogRecord objects, collects them, sorts, and logs progress.
- B 摘要: Searches Google Images for a track's artist and album, parses HTML to extract image URLs, and accumulates them in a list with error dialog.
- 静态失败原因: The static BERT model likely over-weighted the common structural pattern of URL reading and line-by-line iteration, ignoring the distinct domain-specific processing and output goals.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB annotators likely considered these non-clones because the core functionality (parsing camera logs vs. extracting image search results) is fundamentally different, despite similar I/O boilerplate.
- 共享行为: Both open a URL connection and read lines with BufferedReader；Both use a while loop to read line by line；Both close the reader in a finally block or after reading
- 行为差异: Different URL sources and query construction；Output is CameraLogRecord vs. image URLs；Error handling: LogParseException vs. generic Exception with dialog；Sorting of records only in function A
- 修正建议: Incorporate dataflow analysis to track how read lines are used；Focus on the semantics of post-loop operations (sorting vs. text splitting)；Use a larger context window to capture function name and comments

### case_id=709 FP boilerplate_overlap

- 方法: `getContent` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads an HTTP response from an HttpUriRequest using Apache HttpClient and returns the response body as a string.
- B 摘要: Connects to a Google Images search URL, reads the HTML response, and extracts image URLs, adding them to a list.
- 静态失败原因: Static BERT/GraphCodeBERT may have over-relied on the common subpattern of reading HTTP response lines (BufferedReader, InputStreamReader, etc.), and perhaps the token sharing (e.g., 'readLine', 'close') led to a false positive. The model likely missed the overall functional context and treated the shared I/O code as evidence of clone.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels these as non-clone because they have entirely different objectives (generic HTTP body retrieval vs. specific image search parsing). The shared HTTP reading pattern is considered boilerplate and not indicative of semantic equivalence. BCB focuses on broader functional similarity and this pair is considered functionally unrelated.
- 共享行为: Both functions connect to a web server, read the HTTP response line by line using a BufferedReader, and close the reader.
- 行为差异: Function A returns the entire response body as a string; Function B parses HTML to extract image URLs and does not return anything (void).；Function A uses Apache HttpClient while Function B uses HttpURLConnection.；Function A has timeout settings; Function B has user-agent setting.；Function B has conditional logic to skip if artist hasn't changed; Function A has no such condition.
- 修正建议: Improve model's ability to distinguish boilerplate from core logic, e.g., by downweighting common library usage patterns or incorporating higher-level semantic understanding of method purpose.

### case_id=710 FN benchmark_preference_bias

- 方法: `copy` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Copies a file or directory recursively using NIO FileChannel.
- B 摘要: Launches a NexOpen project configuration by checking project type, processing POM files, and setting Hibernate dialect.
- 静态失败原因: The static BERT model correctly predicted non-clone (0) because the semantic gap is large and token overlap is low; this is not a failure, the BCB label is likely incorrect.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB likely labeled this as clone erroneously due to some unrelated common patterns like file existence checks or exception handling, but there is no meaningful similarity.
- 行为差异: A performs file copying, B performs project launch configuration.；A deals with filesystem I/O, B deals with Eclipse workspace and Maven POMs.；A is a generic utility, B is Eclipse plugin specific.
- 修正建议: Re-evaluate BCB ground truth for this pair.；Improve BCB annotation guidelines to avoid false positives.

### case_id=711 FP lexical_or_api_overlap

- 方法: `executePost` vs `startScript`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Sends a POST HTTP request with parameters and returns the response string.
- B 摘要: Fetches a script from a URL and appends its content to a dialog's script buffer.
- 静态失败原因: The model may have been misled by lexical/API overlap (URL, BufferedReader, InputStreamReader) and similar control flow patterns, ignoring crucial differences in HTTP method, output handling, and error management.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: None
- 共享行为: Open a URL connection；Read text line by line；Close the reader
- 行为差异: A uses POST method and writes parameters; B uses GET (openStream) with no parameters；A returns the response string; B modifies dialog's script buffer with side effects；A handles exceptions by printing stack trace and returning null; B exits the program on IOException
- 修正建议: Incorporate data flow analysis to distinguish HTTP methods and output sinks；Add method signature context (return type, parameters)；Use more fine-grained semantic features like error handling patterns

### case_id=712 FN benchmark_preference_bias

- 方法: `saveFile` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Saves current UI window state and settings to an XML configuration file.
- B 摘要: Launches a NexOpen project by configuring Maven POM files and Hibernate dialect.
- 静态失败原因: Static BERT model correctly identified non-clone because it captured the distinct semantics, but BCB label was likely a misannotation.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled as clone due to superficial structural similarities like XML handling and IOUtils usage, ignoring semantic differences.
- 共享行为: Both involve reading or writing XML files；Both use IOUtils for stream copying；Both have try-catch-finally error handling
- 行为差异: Different domains: UI configuration vs Maven project launch；Different input parameters and output side effects；Different XML structures and operations
- 修正建议: Improve benchmark annotations to avoid labeling semantically different functions as clones；Enhance model to ignore common boilerplate and focus on core functionality

### case_id=713 FN partial_functionality

- 方法: `login` vs `run`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Performs HTTP POST login to LOLA by sending URL-encoded email and password, extracts session ID from response, and returns it, printing status messages.
- B 摘要: Performs HTTP GET request with Basic Authentication (Base64 encoded username:password), reads entire response into a string buffer, stores result and sets completion flag, handling exceptions silently.
- 静态失败原因: Static BERT/GraphCodeBERT models rely on token-level patterns and may have focused on the low token overlap (Jaccard 0.22) and different method names, while failing to recognize the high-level semantic similarity of performing authenticated HTTP requests, partially due to limited understanding of API usage sequences and dataflow.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as 'HTTP authentication login' operations where a client sends credentials and receives a server response, viewing the difference in HTTP method and response parsing as implementation variation within Type-4 semantic clone category.
- 共享行为: Both establish HTTP connections to remote servers；Both use authentication credentials；Both read response via BufferedReader；Both handle I/O exceptions
- 行为差异: HTTP method: POST vs GET；Authentication: form-based (email+pw) vs Basic Auth (username:password)；Response processing: extracts session ID vs reads full response；Error handling: returns empty string vs stores exception in field
- 修正建议: Use code property graphs or dataflow analysis to abstract high-level intent；Incorporate API call sequences and dependency analysis；Train on more diverse examples of HTTP client operations

### case_id=714 FN partial_functionality

- 方法: `testNetworkHTTP` vs `httpRequestByPOST`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends multiple hardcoded HTTP GET requests to specific URLs and discards the response, for testing purposes.
- B 摘要: Sends an HTTP POST request with given parameters to a specified URL and returns the response as a string, with error handling.
- 静态失败原因: The token Jaccard similarity is low (0.1579). The model may have focused on API usage differences (HttpURLConnection vs HttpClient, GET vs POST) and structural differences (hardcoded vs parameterized, void vs return), missing the higher-level similarity in network communication.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB considers both as 'HTTP network communication' functions that establish a connection, send a request, and read the response. The differences in HTTP method, parameter handling, and return type are considered minor variations in the broader category.
- 共享行为: Both perform HTTP requests (GET/POST) and read the response line by line using BufferedReader.
- 行为差异: A uses GET, hardcoded URLs, discards output, no parameters; B uses POST, takes URL and params, returns response string, has error handling with status codes.
- 修正建议: Use graph-based models that capture control/data flow to recognize common patterns like 'perform HTTP request and read response'.；Incorporate external knowledge about API equivalences (e.g., different libraries for HTTP).；Augment training data with more diverse API usage for the same high-level task.

### case_id=715 FP lexical_or_api_overlap

- 方法: `actionPerformed` vs `copyFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Handles various UI action commands like setting Graphviz and ImageMagick paths, and updates preferences and UI components.
- B 摘要: Copies a file using buffered I/O streams, handling exceptions and returning the copied file or null.
- 静态失败原因: The model likely overfitted on lexical overlaps like 'File', 'IOException', and common Java I/O classes, ignoring the overall semantic mismatch and the dominance of UI logic in function A.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clone because there is no shared functionality; even when considering relaxed Type-3/4 clones, the functions perform entirely different tasks with no overlapping logic.
- 共享行为: None; functions are unrelated in behavior.
- 行为差异: Function A is a large event handler with multiple conditional branches; Function B is a simple file copy utility.；A interacts with UI components and preferences; B performs file I/O only.；A has complex control flow with many putPref calls; B has linear flow with try-catch for IOException.
- 修正建议: Improve training data to include more diverse non-clone pairs with overlapping API calls.；Use semantic graph representations that capture high-level intent beyond token similarity.；Apply threshold tuning to reject low Jaccard similarity pairs.

### case_id=716 FN partial_functionality

- 方法: `copyFile` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Recursively copies a file or directory.
- B 摘要: Launches an Eclipse configuration, which includes copying a resource file.
- 静态失败原因: The model focused on high-level purpose and method name (copyFile vs launch), had low token overlap, and missed the common file copy sub-routine due to different contexts and APIs.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely annotates as clone because both involve file copying as a sub-operation, and BCB's broad criteria accept partial functionality similarity (Type-4).
- 共享行为: Both functions include file copying operations.
- 行为差异: A copies entire directory structure recursively; B copies a single resource file.；A uses FileInputStream/FileOutputStream; B uses IOUtils.copy.；A is a utility for general file copying; B is an Eclipse launch handler with many additional steps.
- 修正建议: Use AST-based clone detection that can identify shared subroutines.；Incorporate semantic similarity of sub-operations via graph-based representations.；Allow larger syntactic variation for Type-4 clones.

### case_id=717 FP lexical_or_api_overlap

- 方法: `issueCommandToServer` vs `getFullScreenUrl`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Sends a command and capsule data to a server via HTTP POST and returns the response string.
- B 摘要: Fetches a YouTube page, extracts video parameters from the response, and constructs a fullscreen URL.
- 静态失败原因: Static BERT likely relied on lexical and API-level overlap (e.g., URLConnection, BufferedReader) and structural similarity (while loop reading lines) while missing the fundamentally different purposes and data flows.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically does not consider two functions as clones if their core logic and output are different, despite sharing some API usage patterns.
- 共享行为: Both use java.net.URLConnection to open HTTP connections.；Both set doOutput(true) and read input streams line by line.
- 行为差异: Function A sends a command to a server; Function B fetches a YouTube page.；Function A writes POST parameters; Function B reads and parses HTML content.；Function A returns the raw response; Function B extracts specific fields to build a new URL.；Function A uses OutputStreamWriter; Function B does not write to output.
- 修正建议: Incorporate data flow analysis to distinguish input/output behavior.；Train the model to differentiate between common boilerplate code and actual business logic.；Use control flow and data dependency information to capture program semantics.

### case_id=718 FP boilerplate_overlap

- 方法: `getRequestContent` vs `PhoneSetImpl`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads the first line from a URL and returns it.
- B 摘要: Reads all lines from a URL, skips comment lines, parses and adds them to a map.
- 静态失败原因: Static BERT/GraphCodeBERT may have been misled by high lexical overlap in the URL opening boilerplate and similar method structure, failing to capture the critical difference in loop vs single-read.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as not clone because the functions have significantly different logic: one is a simple getter, the other is a constructor that builds a data structure from all lines.
- 共享行为: Both open a URL and read lines using BufferedReader and InputStreamReader.；Both close the reader after reading.
- 行为差异: A reads only the first line; B reads all lines until null.；A returns the line; B populates a map after parsing each line.；B increments a counter and filters lines starting with '***'; A does not.
- 修正建议: Incorporate control flow structure (e.g., presence of loop) into representation.；Use data flow analysis to capture that A returns a single value while B builds a collection.

### case_id=719 FP boilerplate_overlap

- 方法: `getTicketsForQueue` vs `SRWGuiClient`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Retrieves a list of ticket IDs by querying a REST API for a given queue and then fetches each ticket individually.
- B 摘要: Constructor for a Swing browser that initializes GUI, reads XML/HTML from a URL, optionally applies XSLT transformation, and displays content.
- 静态失败原因: The model likely over-relied on overlapping tokens and syntactic patterns (e.g., BufferedReader, InputStreamReader, try-catch) common in network I/O, ignoring the fundamentally different business logic and control flow.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically marks such pairs as non-clones because they perform entirely different tasks despite sharing some common I/O boilerplate; the domain and purpose are distinct.
- 共享行为: Both use BufferedReader/InputStreamReader to read data from a network source；Both contain try-catch-finally blocks for exception handling；Both perform I/O operations and parse text input
- 行为差异: Function A queries a REST API for ticket management; Function B constructs a GUI component；Function A returns a list of RTTicket objects; Function B is a constructor with no return value；Function A uses HTTP GET via HttpGet; Function B uses URL.openStream()；Function A iterates over ticket IDs and fetches each; Function B processes XML/HTML content
- 修正建议: Enhance training with more negative examples that share I/O boilerplate but have different semantics；Incorporate data flow analysis to capture function-specific operations beyond just token sequences；Use function-level embeddings that encode overall intent, e.g., through docstring or method name

### case_id=720 FP boilerplate_overlap

- 方法: `handleHandshake` vs `run`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Handles Minecraft handshake by validating server key and performing session authentication via HTTP.
- B 摘要: Reads and discards content from a local URL.
- 静态失败原因: The static BERT/GraphCodeBERT model likely overemphasized the shared API call pattern (URL, openStream, BufferedReader) and missed the critical differences in control flow, conditionals, and actual functionality. The low token Jaccard suggests lexical overlap is minimal, but the model may still be biased by the common subroutine structure.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled non-clone because the functions have completely different purposes and outcomes despite sharing some I/O boilerplate. The overall functionality, control flow, and external behavior are distinct.
- 共享行为: Both create a URL object and open an InputStream via URL.openStream().；Both use BufferedReader to read lines from the stream.
- 行为差异: Function A performs complex validation of the handshake packet and conditional logic based on username.；Function A sends a Packet1Login or shuts down the network based on HTTP response.；Function B simply reads all lines and discards them without any side effects.；Function A interacts with a remote session server; function B reads from a localhost URL.
- 修正建议: Incorporate control flow and data flow analysis to distinguish different usage patterns of common APIs.；Use graph-based representations that capture semantic structure, not just token sequences.；Train with more diverse examples to reduce reliance on surface-level I/O patterns.

### case_id=721 FN benchmark_preference_bias

- 方法: `readAndRewrite` vs `doGet`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Reads a DICOM file, parses it, reads pixel data, and writes the dataset to an output file.
- B 摘要: Handles HTTP GET request to retrieve and serve a web page, including authorization checks, logging, and caching.
- 静态失败原因: Static BERT/GraphCodeBERT methods rely heavily on token overlap and syntactic similarity. Since the token Jaccard is very low (0.039), the model correctly identified them as different. The model did not fail; it predicted non-clone, which aligns with strict semantics. The BCB label might be anomalous.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled these as clones because both methods perform a read-process-write pattern, and BCB sometimes considers high-level algorithmic similarity as Type-4 clones, though this is a very broad interpretation.
- 共享行为: Both involve I/O operations (reading and writing data)；Both use logging to output status messages
- 行为差异: readAndRewrite focuses on DICOM image processing with specific library calls; doGet handles web requests with HTTP servlet API；readAndRewrite is a static utility method; doGet is a servlet method with request/response objects；doGet has complex control flow with user authorization and page caching; readAndRewrite is linear
- 修正建议: Improve BCB annotation guidelines to avoid over-broad clone definitions that consider methods with different domains and logic as clones

### case_id=722 FN benchmark_preference_bias

- 方法: `compress` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.6`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Compresses a set of input files into a single output file, optionally minifying with YUI Compressor.
- B 摘要: Builds a website for editing by processing each page: reading XML, applying XSLT transformation, and inserting control paths, then writing output files.
- 静态失败原因: Static BERT/GraphCodeBERT predicted non-clone likely because the lexical and structural overlap is very low (token Jaccard 0.079) and the functionality is fundamentally different. The model correctly identified no clone, consistent with strict semantic equivalence, but conflicts with the BCB label.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled these as clones based on an overly broad interpretation of 'file processing' utilities within the same project, or due to an annotation error.
- 共享行为: Both perform file I/O operations (reading input files and writing output files)；Both use logging to report progress；Both iterate over a collection of inputs
- 行为差异: Function A concatenates files and optionally compresses them; Function B transforms XML pages with XSLT and assembles HTML files；Function A uses YUI Compressor for minification; Function B uses XSLT transformers and custom string replacements；Function A operates on a list of file paths; Function B operates on a vector of Page objects；Function A has no DOM or XML processing; Function B extensively uses DOM and XSLT
- 修正建议: Re-evaluate BCB annotation for this pair; consider if it should be non-clone；If BCB label is correct, provide additional context (e.g., project-level documentation) to static models；Use data augmentation to teach models that trivial file I/O similarity does not imply clone

### case_id=723 FN benchmark_preference_bias

- 方法: `doGet` vs `copy`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Handles HTTP GET request to retrieve and render a portal page, managing permissions, logging, and caching.
- B 摘要: Recursively copies a file or directory from source to destination using NIO file channels.
- 静态失败原因: Static BERT methods rely on token similarity and low Jaccard, missing the high-level semantic concept of copying.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider these clones under a broad Type-4 semantic category of 'copying' operations, despite low syntactic similarity.
- 共享行为: Both involve copying data from a source to a destination；Both include error handling and logging
- 行为差异: Different data types (page vs file)；Different I/O mechanisms (HTTP response vs file channels)；Different error handling (sendError vs System.exit)；Different execution context (servlet vs standalone)
- 修正建议: Incorporate data flow analysis to capture high-level semantics；Use program dependence graphs to identify structural similarities in data copying patterns

### case_id=724 FN partial_functionality

- 方法: `copyExternalResource` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Copies a file from source to destination using FileChannel.
- B 摘要: Launches a NexOpen project configuration, including copying a reverse engineering file from a bundle resource.
- 静态失败原因: Static BERT methods rely on token and structure similarity, which are low here. They miss the high-level semantic similarity of 'copying a resource' because the implementations differ and the copy operation is embedded in a larger context.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label it a clone because both functions involve copying a file from one location to another, and the broad Type-4 definition accepts partial functional similarity where a common operation is present.
- 共享行为: Both perform file copy operations (copying external resources).
- 行为差异: A is a simple file copy function; B is a multi-step launch process with XML handling, property settings, and project management, where file copy is only a small part.
- 修正建议: Improve semantic understanding of sub-operations.；Use dataflow analysis to identify common I/O patterns.；Train on examples where functionality is shared despite different implementations.

### case_id=725 FN benchmark_preference_bias

- 方法: `addFileToTarGz` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.4`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Recursively adds a file or directory to a TAR.GZ archive using TarArchiveOutputStream.
- B 摘要: Builds an HTML site for editing by reading XML, applying XSLT transformations, and writing output files.
- 静态失败原因: Static BERT methods likely rely on token and API overlap, which is minimal (Jaccard 0.054). The model correctly predicted non-clone, failing only to match a potentially erroneous BCB label.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might consider both as 'file processing' functions that read input files and write output files, but the specific tasks are too different to be considered a clone under standard Type-3/Type-4 definitions.
- 共享行为: Both involve file I/O using FileInputStream and potentially writing to output streams.
- 行为差异: Function A specifically handles tar archive creation with recursion for directories; Function B handles XML/XSLT transformation and HTML output for multiple pages.；Function A has simple control flow; Function B has complex control flow with loops, conditions, and error handling.；Function A uses TarArchiveEntry and IOUtils; Function B uses Transformer, StreamResult, and custom file system operations.
- 修正建议: Improve benchmark consistency by reviewing labels for false positives.

### case_id=726 FP lexical_or_api_overlap

- 方法: `getRequestContent` vs `retrieveTemplate`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads the first line from a given URL via HTTP connection and returns it.
- B 摘要: Reads the entire content from a blog URL (with caching) and returns it as a concatenated string.
- 静态失败原因: The model likely focused on common API elements (URL, BufferedReader, readLine, Exception) and similar structure (open, read, close), missing the key difference in the loop vs single read and the caching logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the functions differ in output (first line vs full content) and have different parameters and side effects (caching).
- 共享行为: Both create a URL object and open an input stream/connection.；Both use BufferedReader to read text from the stream.；Both close the reader after reading.；Both throw an Exception.
- 行为差异: A returns only the first line; B returns all lines concatenated.；A uses HttpURLConnection with explicit connect and disconnect; B uses URL.openStream() and no explicit disconnect.；A takes the URL as a parameter; B retrieves the URL from an object (blogEditor).；B implements caching by storing the result in a field (cachedTemplate); A has no caching.
- 修正建议: Incorporate data-flow analysis to track how the return value is constructed (single read vs loop).；Consider context of class fields (cachedTemplate).；Use finer-grained differentiation of statement sequences (e.g., while loop vs single readLine).

### case_id=727 FN partial_functionality

- 方法: `getFile` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, optionally modifies XML attribute, saves to temp file.
- B 摘要: Copies a local file to another location using a byte buffer.
- 静态失败原因: Static models like BERT rely heavily on lexical and structural similarity; the low token Jaccard (0.1357) and different method signatures make it hard to detect the shared file I/O pattern. The complex API calls and long code in A also distract from the core copying logic.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider these clones as Type-4 (semantic similarity) because both involve file copying operations despite different sources and additional transformations. The broad concept of 'reading from an input and writing to an output' might be seen as functionally similar.
- 共享行为: Both perform file I/O operations: reading from a source and writing to a destination.；Both use input/output streams (FileInputStream/FileOutputStream or URL streams).
- 行为差异: Source type: URL vs File; destination is local file in A, B copies local to local.；A includes XML parsing and modification; B is pure file copy.；A uses NIO channels (FileChannel, ReadableByteChannel); B uses traditional byte stream.；Exception handling: A catches multiple specific exceptions (MalformedURL, IO, Parser, SAX), B throws IOException.
- 修正建议: Use a model that identifies dataflow and control-flow similarities, such as graph-based or sequence-based models with explicit I/O dependencies.；Augment training data with more diverse Type-4 clones where functions share core behavior but differ in implementation details.

### case_id=728 FP lexical_or_api_overlap

- 方法: `doVersionCheck` vs `downloadModel`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Opens a URL to fetch version information and calls another method with the results.
- B 摘要: Downloads an RDF model from a URL by opening a connection and reading it into a model object.
- 静态失败原因: Static BERT models likely overemphasized common API tokens (URL, InputStream, IOException) and structural patterns like try-catch, ignoring the different task contexts and return types.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels this as non-clone because the overall semantics differ: one is for version checking, the other for model download. Even though both use URL/IO, the functional purpose and output are distinct.
- 共享行为: Both open a URL/URLConnection and read from an InputStream；Both handle IOException；Both involve network I/O
- 行为差异: Function A reads text lines to extract build versions; function B reads binary RDF data into a model；Function A does not return a value; function B returns a Model object；Exception handling differs: A shows error dialog, B throws RuntimeException
- 修正建议: Incorporate dataflow analysis to distinguish output types；Use context-aware embeddings that capture method purpose；Add type or return-type features to the model

### case_id=729 FP lexical_or_api_overlap

- 方法: `getLinksFromURLFast` vs `loadExistingAntlibs`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Extracts hyperlinks from a given URL by reading the HTML page and parsing anchor tags.
- B 摘要: Loads antlib definitions by scanning classpath resources for antlib descriptor files.
- 静态失败原因: The model likely overemphasized lexical overlap (URL, BufferedReader, InputStream, while-loop reading lines) and ignored high-level semantic differences.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels these as non-clones because the overall functionality and output are entirely different (link scraping vs. antlib loading), even though they share low-level I/O patterns.
- 共享行为: Both open a URL connection and read textual data using BufferedReader.；Both use while loops to read lines from an input stream.
- 行为差异: Function A extracts HTML links; Function B loads antlib package definitions.；Function A returns a vector array; Function B returns void and calls loadAntLib.；Function A uses regular expressions extensively; Function B uses URI manipulation.；Function A operates on a single user-provided URL; Function B iterates over multiple resources from a classloader.
- 修正建议: Incorporate control-flow and data-flow analysis to distinguish different function purposes.；Use representation learning that better captures long-range semantics and variable roles.

### case_id=730 FN partial_functionality

- 方法: `runScript` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a script from a URL (appended to codebase) and returns its content as a string, catching exceptions.
- B 摘要: Reads a fixed URL and prints its content line-by-line to console, throwing IOException.
- 静态失败原因: Low token overlap (0.132) and different method signatures, return types, and I/O patterns cause static models to focus on surface syntax, missing the abstract I/O pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB considers functional similarity: both download content from a URL and process it. They likely view this as a Type-3 clone with structural modifications but same essence.
- 共享行为: Both open a URL and read data from it；Both process the stream content (though differently)
- 行为差异: A returns the content as a String; B prints lines to console；A reads byte-by-byte; B reads line-by-line using BufferedReader；A uses parameter for URL suffix; B uses a hardcoded URL；A catches exceptions and returns 'error!'; B throws IOException
- 修正建议: Use dataflow-aware models that capture read-write operations on streams；Include structural similarity on control flow around I/O initialization；Add features like API call sequence similarity for URL handling

### case_id=731 FP boilerplate_overlap

- 方法: `actionPerformed` vs `saveProject`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Handles UI action commands by opening file choosers and saving user preferences.
- B 摘要: Saves a project to disk, creating directory structure, copying databases, and writing XML files.
- 静态失败原因: The static BERT model likely relied on surface-level lexical or structural similarities (e.g., common keywords like 'File', 'IOException', conditional blocks, loops) and failed to capture the distinct semantic contexts and overall goal of each method.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels non-clones when functions serve completely different purposes with no shared functionality, even if they share some boilerplate patterns.
- 共享行为: Both involve file-related operations (selecting paths vs. writing files).；Both contain conditional logic and loops.；Both handle exceptions.
- 行为差异: A is a UI event handler for configuring settings; B is a data export/save method.；A primarily reads file paths and updates UI components; B creates directories, copies database files, writes version and XML files, and creates a zip archive.；A modifies application preferences; B writes project data to disk for later retrieval.；The core logic and purpose are entirely different.
- 修正建议: Incorporate data-flow and control-flow analysis to distinguish different program intents.；Use contrastive learning with negative pairs that have similar boilerplate but different semantics.；Increase model capacity to handle long-range dependencies and overall function purpose.

### case_id=732 FN benchmark_preference_bias

- 方法: `doGet` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Handles HTTP GET request to retrieve and render a page, with access control and optional caching to a temporary file.
- B 摘要: Copies a file from source to destination using a buffered stream, with input validation.
- 静态失败原因: Static BERT correctly predicted non-clone (0) based on low lexical and semantic similarity; the failure is actually a BCB annotation issue where a non-clone was labeled as clone.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled as clone due to the presence of file writing code in A (caching to a temp file) which overlaps with B's file copying, but this is a minor part; the overall functionalities are unrelated.
- 共享行为: Both involve file I/O operations (writing to a file in A, copying file in B).
- 行为差异: A is a complex servlet handler with multiple stages (parameter parsing, user validation, page rendering, logging, caching); B is a straightforward file copy utility.；A operates on HTTP request/response objects; B operates on File objects.；A has extensive error handling and security checks; B has simple precondition checks.；A has side effects like logging, statistics, and caching; B has no side effects beyond file copy.
- 修正建议: Review BCB annotations for false positives where only tangential API overlap exists.；Emphasize functional equivalence over minor common code snippets.

### case_id=733 FN partial_functionality

- 方法: `testNetworkHTTP` vs `CheckUrl`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Makes multiple HTTP GET requests to hardcoded URLs, reading and discarding responses, presumably to exfiltrate device data.
- B 摘要: Takes a URL string, makes an HTTP GET request, and returns the first line of the response.
- 静态失败原因: Static models like GraphCodeBERT may focus on exact structural and token matching; they might have detected low token Jaccard similarity (0.276) and significant differences in control flow, number of statements, and return types, leading them to classify as non-clone. They may lack the broader semantic understanding that both functions are HTTP GET wrappers.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider them clones because both perform the essential operation of connecting to a URL via HTTP and reading the response, which is the core functionality. The differences in specifics (number of requests, parameterization, return value) are considered variations within Type-3/Type-4 similarity.
- 共享行为: Both use HttpURLConnection to open a connection to a URL；Both read from the connection using BufferedReader；Both handle exceptions with printStackTrace；Both perform an HTTP GET request
- 行为差异: Function A makes multiple requests to specific hardcoded URLs; Function B makes a single request to a parameterized URL；Function A discards all response data; Function B returns the first line；Function A has a finally block to disconnect; Function B does not disconnect explicitly；Function A is void; Function B returns String
- 修正建议: Improve training data with more partial functionality clone pairs；Incorporate API usage similarity as a feature；Use data-flow analysis to capture common patterns like URL connection opening and reading

### case_id=734 FN partial_functionality

- 方法: `CopyTo` vs `getFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a local file to a destination using FileReader/FileWriter.
- B 摘要: Downloads a WSDL file from a URL, modifies its endpoint, and saves to a temporary file.
- 静态失败原因: Static BERT or GraphCodeBERT models rely on token-level patterns and may have recognized the common file I/O API calls but missed the significant structural and semantic differences, leading to a false negative.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label as clone because both functions implement a form of data copying from a source to a destination using input/output streams, which is a broad functionality category. The annotators might have overlooked the additional complexity in B.
- 共享行为: Both involve opening an input stream and an output stream to copy data.；Both close streams in a finally block or after use.；Both use file I/O operations.
- 行为差异: A copies from a local file; B downloads from a remote URL.；A only copies bytes; B also parses and modifies XML.；A returns void; B returns a String (file path).；A has minimal exception handling; B has extensive error handling and logging.
- 修正建议: Use dataflow analysis to trace the actual data flow and side effects.；Incorporate structural matching to differentiate simple copy from complex download and modification.；Include more fine-grained AST-based features to capture control flow and nested operations.

### case_id=735 FN partial_functionality

- 方法: `handler` vs `runInternal`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a web page and updates a map with extracted values based on target parameters.
- B 摘要: Downloads or parses an HTTP resource (book or OPDS catalog) with connection handling, progress tracking, and error reporting.
- 静态失败原因: Static BERT/GraphCodeBERT models rely heavily on lexical and syntactic overlap, which is very low (token Jaccard 0.1). The long-range control flow in B and the truncation in the code prevented the model from recognizing the high-level functional similarity of reading a URL and parsing content.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider these as Type-4 clones because both functions perform network I/O and parse the response, sharing a common high-level purpose of fetching and processing data from a URL, which is a broad behavior considered similar in benchmark annotations.
- 共享行为: Both open a URL and read its contents；Both perform parsing of the response data；Both handle I/O exceptions
- 行为差异: B handles HTTP-specific features (redirects, headers, content-type) while A uses simple URL.openStream()；A focuses on extracting substrings into a map, while B either downloads a book or parses a catalog with multiple entries；B includes progress tracking and error callbacks, A does not；B can handle multiple pages via a loop, A processes a single page
- 修正建议: Train models on a diverse set of semantic clones that include low lexical similarity but high functional overlap；Incorporate data-flow analysis or graph-based representations to capture structural dependencies across long ranges；Use models that can handle incomplete code snippets and focus on intent rather than exact token matches

### case_id=736 FP lexical_or_api_overlap

- 方法: `CopyTo` vs `readData`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Copies a file from source to destination character by character.
- B 摘要: Reads a configuration file to initialize various sets and mappings for Tibetan transliteration.
- 静态失败原因: The static model likely focused on the common file I/O and exception handling patterns, mistaking them for semantic similarity, while ignoring the vastly different logic and purpose.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels as non-clones when functions have different functionality despite similar API usage.
- 共享行为: Both perform file I/O；Both use loops to process data；Both handle exceptions with try-catch-finally
- 行为差异: Function A copies file content; Function B parses configuration lines；Function A uses FileReader/FileWriter; Function B uses BufferedReader and StringTokenizer；Function B populates multiple data structures (sets, maps); Function A only writes to output file
- 修正建议: Use contrastive learning to emphasize functional differences over API patterns；Incorporate data flow or call graph information to distinguish file copy from configuration parsing；Apply hard negative mining with semantically different but syntactically similar pairs

### case_id=737 FP boilerplate_overlap

- 方法: `getLinksFromURLFast` vs `getURLContent`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Connects to a URL, reads the entire page, and extracts all hyperlinks and their text using regex, returning a pair of Vectors.
- B 摘要: Connects to a URL, reads the entire page line by line, and returns the concatenated content as a String, handling encoding.
- 静态失败原因: The static BERT/GraphCodeBERT model likely overfitted on the overlapping boilerplate code (URL, URLConnection, BufferedReader, while loop) and missed the critical differences in processing and return types, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels it non-clone because although they share boilerplate URL-reading code, the core functionality (extracting links vs returning content) is fundamentally different and produce different output types.
- 共享行为: Open URL and create URLConnection；Create BufferedReader from input stream；Read lines in a while loop into a buffer (StringBuilder/StringBuffer)；Both are static methods taking a URL string
- 行为差异: Return type: Vector[] (links + texts) vs String (raw content)；Processing: regex-based link extraction vs simple content retrieval；Encoding handling: only B handles encoding explicitly；Error handling: A throws Exception, B throws IOException
- 修正建议: Incorporate data-flow analysis to track how the read content is used differently；Use type-aware embeddings to distinguish different return types；Augment training data with more negative examples that share boilerplate but have divergent logic

### case_id=738 FN benchmark_preference_bias

- 方法: `modifyApplicationMessage` vs `copyFileByNIO`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Modifies a localized properties file, creating a copy from an English default if missing, then reads, updates or appends a message key-value pair, and writes back.
- B 摘要: Copies a file from one File object to another using NIO FileChannel transfer.
- 静态失败原因: The static model correctly predicted non-clone because the functions are semantically different. The BCB label likely reflects a labeling error or overly broad interpretation.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have considered both as file manipulation utilities, possibly labeling as Type-4 clone due to shared file copying sub-task, but this is too broad and not typical BCB practice.
- 共享行为: Both perform file I/O operations；Both involve copying a file (A copies a default file if locale file missing)
- 行为差异: A reads and modifies properties file content; B only copies bytes；A uses traditional streams (FileReader/FileWriter); B uses NIO channels；A has complex logic for locale handling and message editing; B is simple copy；A handles exceptions with printStackTrace; B throws IOException
- 修正建议: Refine BCB annotation guidelines to avoid labeling dissimilar functions as clones；Train models to recognize high-level task specificity beyond file I/O

### case_id=739 FP lexical_or_api_overlap

- 方法: `sendRequest` vs `getVersion`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Sends an XML request to a configurable server via HTTP with GZIP compression and parses the response XML.
- B 摘要: Fetches the latest version string from a fixed URL by reading a single line.
- 静态失败原因: The model likely overgeneralized from the structural overlap of common API calls (URL, URLConnection, getInputStream, etc.) and the try-catch pattern, ignoring the critical semantic differences in data flow (write vs. read-only), XML parsing, and side effects.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB annotators likely considered these as non-clones because the core functionalities are entirely different: one is a generic request sender with two-way communication, the other is a simple one-way version fetcher. The only commonality is basic networking boilerplate, which BCB typically excludes.
- 共享行为: Both open an HTTP connection and read input from a URL.；Both use similar Java networking APIs (URL, URLConnection, BufferedReader/InputStreamReader).；Both catch generic exceptions and return a String.
- 行为差异: Code_a writes data (GZIP compressed XML) to the connection, while code_b only reads.；Code_a parses XML using SAXBuilder; code_b reads plain text line by line.；Code_a has complex configuration (preferences dialog, serverURL state); code_b has hardcoded URL.；Code_a always returns an empty string; code_b returns the version string (or null on failure).
- 修正建议: Incorporate data flow analysis to differentiate write vs. read operations on the connection.；Enhance model sensitivity to purpose-specific patterns like XML parsing vs. plain text reading.；Use method name semantics or comment embedding to capture distinct intentions (sendRequest vs. getVersion).；Augment training data with more examples of boilerplate-heavy non-clones.

### case_id=740 FP lexical_or_api_overlap

- 方法: `copy` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Recursively copies a file or directory to a destination, skipping .svn directories and checking modification times.
- B 摘要: Handles various action commands in a GUI settings dialog to update preferences and UI components.
- 静态失败原因: The static BERT/GraphCodeBERT method may have been misled by the presence of common programming constructs (e.g., file handling, loops, conditionals) or shared vocabulary like 'File', but the overall logic is completely different.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled this as non-clone because the functions have entirely different purposes and no structural similarity, even though both involve loops and conditionals.
- 行为差异: Function A performs file copying; Function B is a GUI event handler.；Function A deals with files and directories; Function B deals with UI actions and preferences.
- 修正建议: Improve model's ability to distinguish high-level intent beyond low-level API usage.；Incorporate control flow and data flow analysis to differentiate between file copying and event handling.；Use longer context to understand the overall structure (e.g., recursive copy vs. switch-like event handling).

### case_id=741 FP boilerplate_overlap

- 方法: `main` vs `copyJar`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Generates Java adapter classes from a Prolog file by parsing, analyzing facts, and writing class files and resources.
- B 摘要: Copies a file from source to destination using NIO file channels.
- 静态失败原因: The static model likely focused on superficial similarities such as both containing try-catch blocks, file handling, and IOException, leading to a false positive despite low token overlap. The model may have been misled by common boilerplate structures.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels based on functional similarity; these functions have entirely different purposes and outputs, so they are correctly labeled as non-clones.
- 共享行为: Both use file I/O (read/write).；Both handle IOException.
- 行为差异: Function A is a complex adapter generation pipeline; Function B is a simple file copy.；Function A parses Prolog, creates classes, and writes JAR entries; Function B only transfers bytes.；Function A has multiple exception handling and conditional logic; Function B has straightforward try-catch-finally.；Function A uses many library-specific classes (Parser, FactVisitor, ClassWriter, etc.); Function B uses standard NIO.
- 修正建议: Train model to distinguish method-level semantics versus syntactically similar I/O patterns.；Incorporate more context about method purpose (e.g., role in application).；Use contrastive learning to separate file-copy operations from complex generation tasks.

### case_id=742 FN partial_functionality

- 方法: `doGet` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.5`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: A servlet doGet method that processes an HTTP request to display a page, handling parameter parsing, user permissions, logging, and caching.
- B 摘要: A main method that reads a log file, filters lines by a token and line interval, and writes the result to a new file.
- 静态失败原因: Static BERT/GraphCodeBERT likely failed due to low token overlap (Jaccard = 0.118) and lack of structural or semantic similarity at the function level. The models focus on local context and may miss the abstract common pattern of 'input-process-output with error handling'.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled these as clones due to broad Type-4 similarity: both functions involve reading input, performing conditional processing, writing output, and handling exceptions. The presence of I/O operations and logging could be seen as a high-level behavioral pattern.
- 共享行为: Both read some input (request parameter vs file) and produce output (HTTP response vs file).；Both use try-catch blocks for exception handling and logging (info/printStackTrace).；Both involve conditional logic for processing.
- 行为差异: Function A handles HTTP servlet context with page retrieval, user visibility checks, and caching; Function B performs simple file I/O with string filtering.；Function A has complex nested control flow and multiple external dependencies; Function B is straightforward line-by-line processing.；The core functionality differs fundamentally: web page serving vs log file trimming.
- 修正建议: Incorporate data flow analysis to trace inputs and outputs.；Use higher-level semantic representations that capture intent (e.g., API calls, I/O patterns).；Train with more diverse examples of partial functionality clones.

### case_id=743 FN partial_functionality

- 方法: `copyResource` vs `testCodingEmptyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies data from a resource (URL or file) to a destination file using byte-by-byte stream copy.
- B 摘要: Tests a LengthDelimitedEncoder by writing data and transferring from a temporary file channel, then verifying the encoded output.
- 静态失败原因: The model relied on token similarity (low Jaccard) and structural cues, but the different method names and test-specific code in B masked the underlying I/O pattern, leading to a non-clone prediction.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB annotators may have considered the high-level similarity of reading from an input and writing to an output, treating both as instances of data copying despite different implementations and contexts.
- 共享行为: Both involve reading from an input source and writing to an output stream.；Both use FileOutputStream to write data.
- 行为差异: A reads one byte at a time in a loop; B uses channel transfer and write(byte[]).；A throws an exception if resource not found; B creates temporary files and asserts results.；A is a utility method for generic copying; B is a unit test with specific encoding logic.
- 修正建议: Incorporate structural patterns of input-output streams and copy loops.；Use models that capture high-level intent rather than token overlap.；Include method-level features like I/O operations and resource handling.

### case_id=744 FP lexical_or_api_overlap

- 方法: `doVersionCheck` vs `loadURL`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches version information from a remote URL by reading lines and parsing build numbers.
- B 摘要: Downloads a file from a URL (with optional basic authentication) to a temporary file while updating a status label.
- 静态失败原因: The model likely over-relied on common boilerplate API calls (URL, InputStream, BufferedReader, readLine) and the similar loop structure, ignoring the divergent data processing and overall purpose.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels as non-clone because the overall tasks are fundamentally different despite superficial API overlap.
- 共享行为: Both open a URL and read lines using BufferedReader.
- 行为差异: A parses version strings from lines; B writes lines to a file.；A shows an error dialog on IOException; B throws IOException and updates a status label with file size.；A is static with a View parameter; B is an instance method with multiple parameters including credentials and status label.
- 修正建议: Incorporate semantic understanding of data flow and output generation.；Differentiate based on method signatures and context.；Use structural analysis to capture different processing after reading lines.

### case_id=745 FN partial_functionality

- 方法: `main` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a ZIP file from a hardcoded URL and extracts its entries to the current directory.
- B 摘要: Concatenates multiple text files given as command-line arguments into a single output file.
- 静态失败原因: Static BERT models rely on token overlap (0.197) and surface syntax; they fail to capture the high-level abstract pattern of I/O processing that BCB considers.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: None
- 共享行为: Both are public static void main methods；Both perform file I/O: reading from a source and writing to disk；Both use exception handling
- 行为差异: Code A reads from a remote URL, Code B reads from local files；Code A extracts a ZIP archive, Code B concatenates plain text；Code A ignores command-line arguments, Code B requires them；Code A writes multiple output files, Code B writes a single output file
- 修正建议: Incorporate dataflow analysis to detect read/write patterns；Use API-level abstraction (e.g., InputStream/OutputStream) to generalize I/O operations；Augment training with examples of diverse I/O tasks labeled as clones

### case_id=746 FP lexical_or_api_overlap

- 方法: `actionPerformed` vs `setImg`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Handles various user preference settings by opening file choosers for external tool paths and updating UI components.
- B 摘要: Opens a file chooser to select an image, copies it to a local directory, and sets it as a background image.
- 静态失败原因: The model may have overemphasized the lexical overlap of JFileChooser usage and file selection patterns, neglecting the broader contextual and functional differences between a multi-purpose settings handler and a specific image setter.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled as non-clone because the functions have distinct purposes and only share a superficial similarity in using JFileChooser; the overall functionality is not considered similar enough for clone detection.
- 共享行为: Both use JFileChooser to select a file and perform actions based on the selection.
- 行为差异: Function A handles multiple commands (GRAPHVIZ, IMAGEMAGICK) and updates many UI elements; Function B only sets an image and copies the file.；Function A uses the file chooser to set paths and enable/disable components; Function B copies the file to a new location and sets an ImageIcon.；Function A's truncated part includes additional settings (date format, look and feel, etc.) not present in B.
- 修正建议: Improve model attention to overall function semantics and intent, not just local patterns.；Incorporate more training examples that distinguish general-purpose dialogs from specific tasks.；Use longer context windows to capture the full scope of function behavior.

### case_id=747 FN benchmark_preference_bias

- 方法: `main` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.75`
- 推荐路线: `preference_memory_with_manual_audit`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Main method that writes library license information by reading .meta and .extra files from a directory and formatting their contents into a text file.
- B 摘要: Method that builds a site for editing by processing page XML files, replacing gadgets with actual values, and writing transformed content to output files.
- 静态失败原因: Static BERT/GraphCodeBERT methods often rely on token overlap and local syntax, missing the high-level semantic pattern of property reading and output writing. The low token Jaccard (0.087) and truncated code of function B further hinder recognition.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider this a Type-4 clone because both functions share a common pattern of reading file-based metadata and writing formatted output, despite differing domains and complexity.
- 共享行为: Both iterate over a collection of files and read metadata or properties from them.；Both write formatted text output to file streams.；Both handle file I/O and use system properties like line separator.
- 行为差异: Function A reads from .meta and .extra files with specific structure; Function B reads XML pages and control files.；Function A writes a static header and then license entries; Function B performs complex transformations including gadget replacement and string manipulation.；Function B handles many more parameters and uses DOM parsing, while Function A uses simple property reading and file copying.
- 修正建议: Train models to recognize structural patterns like iteration over resources and formatted output generation.；Use dataflow or graph representations to capture I/O dependencies.；Adjust benchmark labeling to reflect strict semantics vs. broad Type-4 similarity.

### case_id=748 FN benchmark_preference_bias

- 方法: `fileDownload` vs `readGeoParserResult`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.85`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a file from a URL and saves it to a destination directory.
- B 摘要: Sends an XML request to a geo-parser service and parses the response into a collection of tuples.
- 静态失败原因: The low token Jaccard (0.105) and different method names helped the model distinguish, but BCB's annotation may rely on structural patterns that the model deems insufficient for clone detection.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled them as clones due to common I/O boilerplate (URL, BufferedReader, while loop, try-catch) despite different functionality.
- 共享行为: Both use URL connections and BufferedReaders to read data from a URL
- 行为差异: A writes raw bytes to a file; B parses XML and collects specific data；A has no retry logic; B retries up to 3 times；A saves to a fixed filename 'download.pdf'; B builds a complex XML request and processes response
- 修正建议: Add more functional context to embeddings；Use AST-based similarity to capture structural commonality；Re-evaluate BCB labels for structural-only clones

### case_id=749 FN partial_functionality

- 方法: `readData` vs `read`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Reads and parses a configuration file for Tibetan transliteration, populating various sets and maps from comma-separated tokens.
- B 摘要: Opens a file (local or URL) and reads its content via a delegated method, returning a status code.
- 静态失败原因: Static models like GraphCodeBERT rely on token overlap and structural patterns, which are low (Jaccard=0.05). They miss high-level semantic similarity in file reading behavior due to different APIs and control flow.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB's broad Type-4 similarity may consider both as 'read data' operations, despite implementation differences. The shared file I/O and initialization purpose likely lead to a clone annotation.
- 共享行为: Both methods involve reading input data from an external source (file).；Both handle I/O exceptions.
- 行为差异: Function A parses the file content into multiple data structures (sets, maps), while Function B only opens the stream and relies on another method for actual parsing.；Function A uses StringTokenizer and complex parsing logic; Function B is a simple wrapper.
- 修正建议: Incorporate method dependency information (e.g., calls to other read methods).；Use code summarization or docstring embeddings to capture intent.；Apply cross-function contextual embeddings from call graphs.

### case_id=750 FP boilerplate_overlap

- 方法: `main` vs `main`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.5`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Parses a Prolog file and generates adapter classes into a JAR.
- B 摘要: Reads a dataset, evaluates rule files from a zip, and outputs performance measures.
- 静态失败原因: Static BERT/GraphCodeBERT may have over-relied on the structural pattern common to main methods (argument checking, file I/O, try-catch, loops) and missed the deep semantic difference in the specific processing logic, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would not consider these clones because they implement entirely different domain-specific functionalities, despite both being main methods.
- 共享行为: Both are Java main methods with command-line argument parsing.；Both read input files and produce output.；Both use loops and conditional logic for processing.
- 行为差异: Function A processes Prolog source files and generates Java bytecode; Function B processes rule files and evaluates predictive performance.；Function A writes a JAR file with adapter classes; Function B reads a zip and outputs numerical performance metrics.；Function A uses a Prolog parser and class generation; Function B uses a rule parser and evaluation measure.
- 修正建议: Incorporate data flow analysis to capture domain-specific dependencies.；Use contrastive learning to distinguish between structurally similar but semantically different functions.；Include more contextual information about library calls and output types.

### case_id=751 FN benchmark_preference_bias

- 方法: `main` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Compresses a file specified as command-line argument using GZIP and writes output to a .gz file.
- B 摘要: Retrieves a resource as an InputStream, with caching to local file system, handling HTTP connections and file-based cache.
- 静态失败原因: The static model correctly predicted non-clone (0) because the functions have low lexical overlap and semantically distinct operations. The model did not fail; it correctly identified the difference.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have considered both as 'I/O with streams' or 'file manipulation', but the core functionality and purpose are entirely different. The label is likely a false positive in BCB.
- 共享行为: Both use FileInputStream for reading；Both handle IOException with try-catch；Both perform byte-level I/O operations
- 行为差异: A compresses data with GZIP; B does not compress but caches；A reads from local file; B reads from URL and may cache locally；A writes to GZIPOutputStream; B writes to BufferedOutputStream for cache file；A has no caching logic; B maintains a cache hashtable
- 修正建议: Re-evaluate BCB annotation for this pair; it may be a mislabel.；If using this dataset for training, consider filtering out such pairs with low semantic similarity despite syntactic overlap.

### case_id=752 FN benchmark_preference_bias

- 方法: `main` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Reads a file specified as a command-line argument, applies WrapFilter and TitleCaseFilter, and writes the output to another file.
- B 摘要: Launches an Eclipse launch configuration for a NexOpen project, processing Maven pom.xml files, setting Hibernate dialect, and managing project resources.
- 静态失败原因: The static BERT model correctly predicted non-clone due to low token Jaccard (0.056) and lack of structural/lexical overlap. From BCB's perspective, the model failed because it did not recognize the broad Type-4 similarity of file I/O operations.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as a clone due to both functions performing file reading/writing and using similar Java I/O classes (e.g., InputStream, FileWriter), overlooking the vastly different contexts and purposes.
- 共享行为: Both involve file I/O operations (reading and writing files).
- 行为差异: code_a is a simple standalone file transformation utility; code_b is a complex Eclipse plugin launch method with project, Maven, and Hibernate configuration.；code_a uses BufferedReader/FileWriter; code_b uses various Eclipse and Hibernate APIs, XML parsing, and progress monitoring.；code_a has no error handling beyond IOException; code_b has extensive error handling and logging.；code_a operates on generic files; code_b operates on Eclipse workspace projects and specific XML files.
- 修正建议: Improve BCB annotation consistency to avoid labeling semantically different functions as clones.；Train models to distinguish between superficial I/O patterns and actual semantic functionality.

### case_id=753 FN partial_functionality

- 方法: `getHTML` vs `PhoneSetImpl`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.65`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads HTML from a URL and returns it as a string, optionally writing to a file.
- B 摘要: Reads a phone set definition from a URL and parses it to populate a map.
- 静态失败原因: Static BERT models may overlook high-level semantic differences due to token overlap and similar surface patterns, focusing on common I/O operations while missing divergent overall purposes.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely views both as 'read from URL and process input line by line' tasks, considering them functionally similar in a broad sense.
- 共享行为: Both open a URL and read lines using BufferedReader；Both process input line by line
- 行为差异: Function A returns the HTML string; Function B builds a map；Function A can write to a file; Function B does no file I/O；Function A uses HttpURLConnection with User-Agent; Function B uses URL.openStream()；Function A catches exceptions; Function B does not
- 修正建议: Enhance model with data flow analysis to distinguish output usage；Incorporate larger context including variable type and return type

### case_id=754 FN benchmark_preference_bias

- 方法: `copy` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.6`
- 推荐路线: `preference_memory_with_manual_audit`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Copies a local file or directory to another local path using NIO FileChannel or recursion.
- B 摘要: Downloads a remote resource using HTTP URL connection, caches it to a local file, and returns an InputStream.
- 静态失败原因: Low token overlap (0.13), different method names and control structures; static models lack high-level functional abstraction to see similarity.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider both as 'data transfer' operations from an input source to an output destination, involving file system and streams, thus broad Type-4 clone.
- 共享行为: Perform file I/O operations；Create directories if needed；Use streams for data transfer；Handle IOExceptions
- 行为差异: Source is local file vs remote URL；Type: copy vs download and cache；Return type: void vs InputStream；Includes HTTP handling and caching logic in B
- 修正建议: Train with abstract functional summaries or data flow graphs；Incorporate task-level similarity (e.g., both involve file copying/downloading)；Use contrastive learning with broad clone pairs

### case_id=755 FP lexical_or_api_overlap

- 方法: `readTwitterFead` vs `executeHttpGet`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a specific Twitter timeline (hardcoded URL) and returns the raw JSON string, with detailed error logging and status code check.
- B 摘要: Executes an HTTP GET request to a given URI and parses the response into a JSONObject, throwing exceptions on failure without status check.
- 静态失败原因: Static BERT/GraphCodeBERT may have been misled by high token overlap (Jaccard 0.29) and common API patterns (HttpClient, HttpGet, readLine, StringBuilder), while overlooking differences in URL handling, error checking, return types, and exception management. The model likely overestimated similarity due to lexical and API surface similarity.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the functions differ significantly in abstraction level (specific vs generic), error handling strategy (checked vs unchecked), and return types (raw string vs parsed JSON). The partial similarity in HTTP GET pattern is not enough for BCB to consider them clones given the functional differences.
- 共享行为: Both perform HTTP GET requests using HttpClient and HttpGet.；Both read the response line by line into a StringBuilder.；Both return the content as a string (A returns String, B builds String then converts to JSONObject).
- 行为差异: A uses a hardcoded URL, B takes a URI parameter.；A checks status code (200) and logs error on failure, B does not check status and throws exceptions.；A catches exceptions internally (ClientProtocolException, IOException), B declares throws Exception.；A returns String, B returns JSONObject.
- 修正建议: Train models to be sensitive to error handling patterns (e.g., status code checks, exception handling vs. throwing).；Incorporate data flow analysis to distinguish hardcoded vs parameterized inputs.；Consider return type and domain-specific constants as discriminative features.；Use contrastive learning on pairs with high token overlap but different functionality.

### case_id=756 FN partial_functionality

- 方法: `copyResource` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource identified by a source string (URL or file path) to a destination file using byte-by-byte stream copying.
- B 摘要: Copies a file from a source File to a destination File using NIO FileChannel transfer.
- 静态失败原因: The low token Jaccard similarity (0.22) and different API usage (InputStream vs FileChannel, while-loop vs transferTo) likely caused the static model to miss the functional equivalence.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels function pairs as clones if they perform the same high-level task (file copying) despite differences in input handling and implementation details, which aligns with Type-4 (semantic) clones.
- 共享行为: Both functions copy the entire content of a source to a destination file.
- 行为差异: Input types differ: source string (URL or file path) vs explicit File objects.；Copy technique differs: byte-by-byte stream reading/writing vs NIO FileChannel transfer.；Error handling differs: throws generic Exception vs IOException.；copyResource uses a helper method destinationFile() to determine output path, while copyFile takes destination as parameter.
- 修正建议: Enhance training data with more Type-3/Type-4 clone examples (same behavior, different APIs).；Incorporate dataflow analysis to capture that both functions ultimately copy a stream of bytes from source to destination.

### case_id=757 FP boilerplate_overlap

- 方法: `readData` vs `resolvePlugins`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Reads configuration data from strings and a file to populate sets and maps for Tibetan transliteration.
- B 摘要: Downloads a plugins.xml file from a URL if not cached locally, then resolves plugins from that file.
- 静态失败原因: The model likely over-relied on superficial lexical similarities such as shared library classes (File, IOException, etc.) and the try-catch pattern, ignoring the vastly different core logic and data structures.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would label as non-clone because the functions are semantically unrelated: one is data initialization for a transliteration system, the other is plugin resolution for an editor. No meaningful overlap in goals or behavior.
- 共享行为: Both perform file I/O operations.；Both use try-catch for exception handling.
- 行为差异: A initializes multiple data structures (HashSets, HashMaps) while B downloads a file and calls another method.；A reads from embedded string tokens and a file; B solely downloads from a URL.；A has complex parsing logic; B simply copies an InputStream to a FileOutputStream.；A is a large monolithic function; B is short and delegates to another method.
- 修正建议: Incorporate dataflow or control-flow analysis to distinguish actual behavior from common boilerplate.；Train on a more diverse set of non-clone pairs to reduce false positives from shared patterns.；Use representation learning that captures long-range semantic dependencies beyond local tokens.

### case_id=758 FP boilerplate_overlap

- 方法: `readData` vs `convert`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Parses comma-separated token strings into sets and a map for validation of input sequences.
- B 摘要: Converts an ACRNEMA stream file to DICOM format with UID assignment and pixel data handling.
- 静态失败原因: Static BERT models may over-rely on common programming patterns (try-catch, loops, exceptions) and the length of the functions, leading to false positive despite minimal token overlap.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would not consider these as clones because they have completely different purposes and implementations, with low token similarity (Jaccard 0.079) and no functional overlap.
- 共享行为: Both use Java standard library APIs for I/O and collections, but the specific functionality is entirely different.
- 行为差异: Function A initializes data structures by parsing static string tokens; Function B performs file format detection, conversion, and pixel data manipulation.；Function A is a private static initialization method; Function B is a public file conversion method with multiple file I/O operations.
- 修正建议: Improve token similarity thresholds,；Incorporate semantic analysis (e.g., dataflow, control flow) to distinguish different operations,；Use domain-specific embeddings to capture function intent.

### case_id=759 FN partial_functionality

- 方法: `copyFromTo` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a source file to a destination file using FileChannel, preserving last modified timestamp.
- B 摘要: Retrieves a resource by URL, caches it locally, and returns an InputStream, handling HTTP connections and caching.
- 静态失败原因: The static model likely focused on low token overlap (0.1567 Jaccard) and different control flow patterns, missing the high-level file I/O similarity that BCB considers as clone.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this as a clone because both methods perform file I/O operations (reading and writing streams), which falls under the broad Type-4 category of functional similarity despite different implementations and purposes.
- 共享行为: Both involve file I/O operations (FileInputStream, FileOutputStream).；Both use buffered streams indirectly.；Both include error handling and printing messages.
- 行为差异: copyFromTo copies file content from one path to another; getResourceAsStream retrieves and caches a remote resource.；copyFromTo uses FileChannel.transferTo; getResourceAsStream uses manual buffered read/write loop.；getResourceAsStream includes URL handling, HTTP connection, and caching logic; copyFromTo does not.；getResourceAsStream returns an InputStream; copyFromTo is void.
- 修正建议: Incorporate high-level semantic features like method purpose or domain (e.g., file I/O).；Use models with better understanding of long-range dependencies and I/O patterns.；Include training data with more Type-4 clone examples where functionality is similar but implementation differs.

### case_id=760 FP long_range_semantics

- 方法: `readData` vs `runDynusT`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `static_summary_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Parses comma-separated strings into character sets and reads a configuration file to build mapping tables for Tibetan transliteration.
- B 摘要: Copies executable and model files to a temporary directory, runs a traffic simulation executable, and optionally cleans up.
- 静态失败原因: The static BERT-based model likely overemphasized surface-level similarities (loops, conditionals, file I/O) and failed to capture the high-level semantic dissimilarity, possibly due to the long and truncated nature of code_a causing attention to focus on local patterns.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB would not consider these clones because they perform entirely different tasks (text processing vs. simulation execution) with no functional overlap, despite some superficial structural similarities.
- 共享行为: Both involve loops over collections of strings.；Both handle exceptions (IOException in A, RuntimeException in B).
- 行为差异: Function A parses input strings and file contents to build data structures for text processing; Function B orchestrates file copying and external process execution.；Function A uses StringTokenizer and builds HashMaps; Function B uses IOUtils.copyFile and ExeRunner.；Function A is long and complex with many nested conditionals; Function B is short and linear.
- 修正建议: Incorporate global control flow and data flow analysis.；Use method name and API call semantics to better differentiate purposes.；Train on more diverse long functions to avoid attention bias.

### case_id=761 FN benchmark_preference_bias

- 方法: `getFile` vs `trainClassifier`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Downloads a WSDL file from a URL, modifies the endpoint attribute, and saves it to a temporary directory, returning the file path.
- B 摘要: Executes an external command to train a classifier using a directory and arguments, writing training data and model files.
- 静态失败原因: Static BERT models rely on lexical and structural similarity; the low token Jaccard and dissimilar AST patterns led to a correct non-clone prediction, but BCB's coarse preference for high-level file-processing similarity was missed.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled these as clones based on a broad Type-4 (semantic) similarity, considering both functions perform file I/O and external resource access, despite different domains.
- 共享行为: Both functions involve file I/O operations (writing files).；Both functions handle exceptions (getFile catches specific exceptions, trainClassifier throws Exception).
- 行为差异: getFile downloads and parses XML; trainClassifier runs an external process.；getFile uses extensive logging; trainClassifier has no logging.；getFile returns a String; trainClassifier returns void.；getFile is a static utility; trainClassifier is an instance method overriding an interface.
- 修正建议: Use dataflow analysis to differentiate I/O patterns.；Incorporate domain-specific knowledge to avoid overgeneralization.；Adjust threshold to require stronger behavioral evidence for clones.

### case_id=762 FN partial_functionality

- 方法: `readRemoteFile` vs `login`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads the content of a remote file by opening a URL stream and reading lines until EOF.
- B 摘要: Logs into a service by sending credentials via HTTP POST, reads the response to extract a session ID, and stores it.
- 静态失败原因: Static BERT/GraphCodeBERT models rely on token overlap and structural similarity. The token Jaccard is low (0.24), and the specific operations (GET vs POST, different variable names, different exception handling) cause the model to focus on surface-level differences, missing the high-level functional similarity that BCB values.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considers these clones because both functions implement network I/O to fetch data from a URL, following a common pattern of opening a connection, reading lines, and returning a string, with similar error handling.
- 共享行为: Both open a URL connection to a remote resource；Both use BufferedReader to read lines from an input stream；Both handle exceptions during network I/O；Both return a String as the result
- 行为差异: readRemoteFile performs a GET-like operation; login performs an HTTP POST with form data；login writes to the output stream before reading; readRemoteFile only reads；readRemoteFile reads and concatenates all lines; login reads only the first line to extract session ID；login performs URL encoding and sets session state; readRemoteFile does not
- 修正建议: Train with BCB-style labels to capture high-level functional similarity；Use dataflow analysis to detect common I/O patterns (e.g., URL.openConnection, BufferedReader)；Incorporate contrastive learning with positive pairs that share partial functionality

### case_id=763 FP lexical_or_api_overlap

- 方法: `handleHandshake` vs `readReferenceText`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Handles Minecraft client handshake by validating server key and performing HTTP login verification.
- B 摘要: Reads reference text resource from a bundle file using URL and returns its content as a string.
- 静态失败原因: The model may have over-relied on overlapping API sequences (URL, BufferedReader, readLine) and lexical similarity, missing the semantic divergence in control flow and domain logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would likely consider these non-clones because the functionality is entirely different (Minecraft login vs. file reading) and the shared I/O code is generic boilerplate not indicative of clone behavior.
- 共享行为: Both open URL streams and read line-by-line using BufferedReader.
- 行为差异: handleHandshake performs Minecraft protocol logic, sends packets, and handles authentication; readReferenceText simply reads a text file.；handleHandshake has complex conditional flow based on username; readReferenceText has straightforward sequential read.；Error handling differs: handleHandshake shuts down network connection; readReferenceText logs and throws a custom exception.
- 修正建议: Incorporate dataflow analysis to distinguish high-level purpose.；Use context-aware embeddings that capture method-level semantics beyond token overlap.；Apply a threshold on structural similarity or incorporate API usage patterns as part of a broader feature set.

### case_id=764 FP partial_functionality

- 方法: `readTwitterFead` vs `retrieveQ`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a fixed Twitter JSON feed using Apache HttpClient and returns the content.
- B 摘要: Reads a given URL using Java URLConnection and returns the content.
- 静态失败原因: Static BERT may have focused on the shared boilerplate (HttpClient, URL, BufferedReader, StringBuilder) and overall structure, overlooking differences in error handling and specific API calls.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely considers them non-clones due to significant differences in error handling, URL source, and library usage, despite shared high-level functionality.
- 共享行为: Both perform HTTP GET to retrieve text content from a URL and return it as a string.
- 行为差异: Different HTTP client libraries (Apache HttpClient vs. URLConnection)；A uses hard-coded URL, B takes a parameter；A checks status code 200, B does not；A catches exceptions internally, B declares throws
- 修正建议: Train with more diverse examples emphasizing error handling differences；Incorporate data flow analysis to distinguish between different HTTP libraries

### case_id=765 FN benchmark_preference_bias

- 方法: `readAndRewrite` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Reads a DICOM file, parses it to retrieve pixel data, and writes it to another file.
- B 摘要: Builds a website by processing pages, reading XML streams, applying XSL transformations, and writing output files.
- 静态失败原因: Static BERT/GraphCodeBERT likely did not fail; it correctly predicted non-clone due to low token Jaccard (0.0359) and clear semantic mismatch. The error type is FN meaning BCB said clone but model said non-clone, so the model correctly identified the difference.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might have labeled as clone due to very broad Type-4 (similar functionality) if they considered both as 'read from input, transform, write to output' tasks, but that is overly generic and not typical BCB annotation.
- 共享行为: Both perform file I/O operations；Both handle exceptions
- 行为差异: Different domains: medical imaging vs web building；Different libraries: DICOM vs XML/Transformer；Different output formats；Function A is simpler and focused on single image
- 修正建议: Re-evaluate BCB annotation for this pair; likely a mislabel.；Include more specific semantic constraints in clone definition to avoid overly broad Type-4 classifications.

### case_id=766 FP lexical_or_api_overlap

- 方法: `readZoneIDs` vs `setMembers`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads integer IDs from a resource file and returns them as a HashSet.
- B 摘要: Fetches an HTML page from a Trac URL, parses select elements for components and priorities, and populates class-level arrays.
- 静态失败原因: Static models like GraphCodeBERT may over-rely on surface-level lexical and API usage overlap (e.g., URL, BufferedReader, readLine, while loop, try-catch) and miss the semantic intent difference due to limited representation of long-range dependencies and external context.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels Type-4 (functionally unrelated) as non-clone. Despite boilerplate similarity, the core functionality differs: one reads numeric IDs, the other parses HTML for web scraping.
- 共享行为: Both use URL and InputStreamReader/BufferedReader to read data from a resource (file or URL).；Both read lines in a loop and process each line.；Both handle exceptions with printStackTrace or print statements.
- 行为差异: readZoneIDs reads from a classpath resource; setMembers reads from a remote URL with a specific path.；readZoneIDs parses each line as an Integer and adds to a HashSet; setMembers searches for specific HTML patterns and populates class-level string arrays.；readZoneIDs returns a HashSet; setMembers is void and modifies instance variables.；setMembers involves regex pattern matching and encoding conversion, absent in readZoneIDs.
- 修正建议: Enhance model with finer-grained structural matching (e.g., data flow analysis, return types).；Incorporate method signature and class-level context to distinguish IO patterns from actual logic.；Use more negative examples with overlapping APIs but different semantics during training.

### case_id=767 FP long_range_semantics

- 方法: `readData` vs `transport`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `static_summary_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Parses multiple comma-separated token strings into various sets and maps, populating data structures for Tibetan character processing.
- B 摘要: Recursively copies files from a source directory to a destination using FileChannel.
- 静态失败原因: The static BERT model likely relied on superficial lexical or structural similarities (e.g., common Java keywords, loop patterns) and may have been confused by the truncated version of code_a, losing the overall semantic context.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB would label this as non-clone because the methods perform completely different tasks with no functional overlap; one is data initialization and the other is file copying.
- 共享行为: Both methods use loops and conditionals to process data.；Both methods involve Java standard library classes (StringTokenizer, HashSet, File, etc.)
- 行为差异: Code_a processes string tokens and populates sets and maps; Code_b copies files.；Code_a has no file I/O; Code_b relies on FileInputStream/FileOutputStream and FileChannel.；Code_a is significantly longer and more complex with multiple tokenization steps.；Code_b includes recursion and error handling for file transfer.
- 修正建议: Ensure models can handle long methods without truncation, e.g., by using sliding windows or hierarchical embeddings.；Incorporate control flow and data dependency analysis to distinguish between different I/O behaviors.；Add more semantic features such as method name, comments, and class context.

### case_id=768 FN partial_functionality

- 方法: `testNetworkHTTP` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.75`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends multiple HTTP GET requests to exfiltrate device data (IMEI, phone, messages, file content, installed apps) to remote servers.
- B 摘要: Sends an HTTP POST request to RenRen API with predefined parameters and prints the request URL and response.
- 静态失败原因: Static BERT/GraphCodeBERT rely on token and graph representations that are sensitive to lexical differences (URLs, variable names, literals) and low token overlap (0.1545). The model likely missed the high-level structural and behavioral similarity due to surface-level divergence.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels as clones when both functions perform similar HTTP communication tasks (open connection, read response) even if the specifics (GET vs POST, different parameters) differ. The core functionality of sending/receiving data over HTTP is considered a clone under broad Type-3/Type-4 criteria.
- 共享行为: Both open an HttpURLConnection to a URL；Both read the input stream line by line；Both use BufferedReader to read the response
- 行为差异: A uses HTTP GET, B uses HTTP POST；A sends multiple requests, B sends one request；A does not output result, B prints request URL and response；A catches IOException, B throws IOException
- 修正建议: Incorporate data-flow analysis to detect common API usage patterns (e.g., HttpURLConnection + BufferedReader read loop).；Use contrastive learning with pairs that share structural patterns but differ in details.；Add a feature for 'HTTP request pattern' to reduce sensitivity to argument differences.

### case_id=769 FN benchmark_preference_bias

- 方法: `doGet` vs `extractImage`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Handles HTTP GET request to retrieve and render a web page with access control and logging.
- B 摘要: Extracts an image from input using Djatoka decode parameters and writes output to file.
- 静态失败原因: The model correctly identified them as non-clones based on semantic and lexical dissimilarity, so from a strict functional perspective it did not fail; the misclassification arises from a benchmark label inconsistency.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: Given the low token overlap and entirely different domains, BCB likely would not consider these clones; the BCB label of 1 may be an annotation error or due to extremely broad Type-4 structural similarity.
- 行为差异: Function A is a servlet handler for web page requests, while B is an image extraction utility.；A uses HTTP request/response objects and page management APIs; B uses image processing and file I/O.；A has complex logic for page lookup, visibility checks, and caching; B applies scaling and transformations to images.
- 修正建议: Review and verify the BCB annotation for this pair to ensure consistency.；If BCB intends broader clone types, adjust the model training to include more diverse Type-3/4 examples.

### case_id=770 FN benchmark_preference_bias

- 方法: `modifyApplicationMessage` vs `copy`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Modifies a localized properties file by reading or creating it from an English template, then updating or appending a message.
- B 摘要: Copies a file from source to destination using FileChannel transfer.
- 静态失败原因: Static model correctly predicted non-clone because it captured the low lexical overlap and distinct high-level semantics, but BCB label is considered reference, making it a false negative in evaluation.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might have labeled as clone due to both functions performing file copying and using similar resource management patterns, even though overall semantics differ.
- 共享行为: Perform file I/O operations；Use try-finally resource management；Close streams/channels
- 行为差异: A involves conditional file creation and property parsing; B is a direct byte-level copy；A modifies file content; B does not change content；A uses character streams and BufferedReader; B uses NIO channels
- 修正建议: Use functional-level clone criteria emphasizing program purpose；Re-annotate BCB to exclude broad I/O utility clones

### case_id=771 FP lexical_or_api_overlap

- 方法: `testAddLinkToImage` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Test method that copies image files from classpath resources to a report folder and adds links to them in the report.
- B 摘要: Action event handler that processes various commands (GRAPHVIZ, IMAGEMAGICK, etc.) to set file paths and preferences, and updates UI components accordingly.
- 静态失败原因: The static BERT model likely focused on common lexical tokens (e.g., 'File', 'JFileChooser', 'if', 'null', 'getAbsolutePath') and structural patterns (if-else chain) due to limited context understanding, ignoring the overall semantics and method purposes.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BigCloneBench typically requires at least Type-3 similarity (similar functionality with modifications). These functions perform completely different tasks, so BCB would label them as non-clones.
- 共享行为: Both methods involve file operations (copying or selecting files).；Both methods use conditional logic based on string comparisons.；Both methods update configuration or report state.
- 行为差异: Function A is a unit test with sequential file copying and link addition; function B is a complex event handler responding to multiple actions.；Function A uses IOUtils.copy and report.addLink; function B uses JFileChooser and preference storing.；Function A has no user interaction; function B relies on GUI components and user selections.；The scope and purpose are entirely different: testing report linking vs. configuring application settings.
- 修正建议: Enhance model with dataflow or control-flow aware embeddings to distinguish different contexts.；Incorporate method-level summarization to capture high-level intent.；Use contrastive learning with negative samples that have lexical overlap but different semantics.

### case_id=772 FN benchmark_preference_bias

- 方法: `modifyApplicationMessage` vs `downLoadZippedFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Modifies a properties file for a given locale by replacing or adding a key-value pair.
- B 摘要: Downloads a zipped file from a URL, extracts it to a directory, and returns the directory URL.
- 静态失败原因: The static BERT model correctly identified no clone due to low lexical overlap and different semantics; the BCB label is likely a false positive.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have considered both functions as having similar control flow patterns (try-catch-finally, stream I/O) and labeled them as Type-3/Type-4 clones based on partial functionality similarity, but this is a weak match.
- 共享行为: Both read from an input stream and write to an output stream with explicit stream closure and exception handling.
- 行为差异: A modifies existing configuration files; B downloads and extracts a zip archive.；A processes text files line by line; B copies binary data and unzips.；A uses locale-specific file management; B uses a temporary file and deletes it after unzipping.
- 修正建议: Review BCB annotation for this pair; consider removing it as a false positive.；If keeping, augment training data with such examples to teach models to ignore boilerplate-only similarity.

### case_id=773 FN partial_functionality

- 方法: `readRemoteFile` vs `addIDs`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a remote file line by line and concatenates all lines into a single string.
- B 摘要: Queries a web service for a metabolite name, parses HTML to extract and store various IDs into a row object, and returns a score.
- 静态失败原因: The static BERT/GraphCodeBERT model likely focused on lexical and syntactic similarity, which is very low (token Jaccard 0.137), and failed to recognize the shared behavior of URL reading as a basis for clone classification under BCB's broad criteria.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled this pair as a clone due to the shared pattern of opening a URL and reading lines, considering it a partial functionality similarity under a lenient Type-4 clone definition.
- 共享行为: Both open a URL and read lines from it using BufferedReader.
- 行为差异: Function A simply concatenates all lines without processing; Function B selectively processes lines based on HTML content and sets multiple fields.；Function A returns the concatenated string; Function B returns an integer score and modifies the input row object.；Function A catches EOFException and IOException; Function B only catches IOException and logs it.
- 修正建议: Incorporate functional similarity measures that capture common sub-behaviors (e.g., URL reading patterns) even when overall semantics differ.；Use contrastive learning that emphasizes shared execution paths or data flow beyond lexical overlap.

### case_id=774 FN boilerplate_overlap

- 方法: `main` vs `setMembers`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sets up parameters for RenRen API and sends a POST request, printing response.
- B 摘要: Fetches HTML from a Trac URL, parses select elements for component and priority, and stores them in member arrays.
- 静态失败原因: Low token Jaccard (0.16) and different method names caused the model to miss the shared network I/O boilerplate pattern that BCB emphasizes.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may consider both as network I/O with line-by-line reading, viewing them as Type-4 (similar functionality) despite different domain specifics.
- 共享行为: Open a URL connection；Read lines from an input stream；Handle IOException
- 行为差异: Function A constructs a custom POST request with many parameters; Function B performs HTML parsing with regex；Different data flow and output；Function A prints response; Function B stores results in member variables
- 修正建议: Train with more emphasis on structural vs. lexical similarity; include examples of broad I/O patterns.

### case_id=775 FN partial_functionality

- 方法: `addIDs` vs `fetchUrl`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.75`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches a URL constructed from a metabolite name, parses HTML to extract metabolite IDs and scores, and sets multiple properties on a PeakListRow object.
- B 摘要: Fetches a URL and returns its entire content as a string.
- 静态失败原因: The static BERT/GraphCodeBERT model likely failed due to low token Jaccard similarity (0.142857) and the large amount of additional code in A overshadowing the shared URL-fetching pattern. The model may not have captured the structural similarity in the URL handling portion because it appears early in A and then diverges significantly.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely labels this as a clone because both functions share the core functionality of fetching a URL and reading its content via BufferedReader, even though A has additional processing. This is common for Type-3/Type-4 clones where the same IO pattern is present.
- 共享行为: Both use URL and BufferedReader to fetch and read a web resource line by line；Both handle IOException through catch blocks
- 行为差异: A performs complex HTML parsing to extract specific data fields, while B simply concatenates all lines；A sets multiple properties on a row object and returns an integer score, whereas B returns the raw webpage content
- 修正建议: Incorporate subgraph matching or common API usage patterns；Use clone detection that focuses on data flow and control flow for I/O operations；Increase sensitivity to partial functional similarity

### case_id=776 FN partial_functionality

- 方法: `getWebPage` vs `invoke`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches the entire content of a web page as a string via HTTP GET.
- B 摘要: Invokes a remote method via HTTP POST, reads the JSON response, and deserializes it, with retry on timeout.
- 静态失败原因: Static BERT likely focused on low token overlap (Jaccard=0.138) and deep structural differences (exception handling, retry, JSON parsing), missing the shared HTTP response reading pattern that BCB considered significant.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may annotate as clone because both functions involve reading an HTTP response using similar boilerplate code (BufferedReader, while loop). The annotators might consider this a Type-4 clone where overall functionality of fetching remote data is similar.
- 共享行为: Both read HTTP response line by line and build a string.；Both use BufferedReader and InputStreamReader.；Both handle IOException/HTTP errors.
- 行为差异: A uses GET; B uses POST.；A returns raw string; B deserializes JSON.；B includes retry logic; A does not.；B constructs URL dynamically; A uses given URL.
- 修正建议: Improve detection to recognize shared components like HTTP response reading even when overall semantics differ.；Incorporate structural similarity measures that capture common I/O patterns.；Use learning to rank or ensemble methods that combine lexical and semantic features.

### case_id=777 FP boilerplate_overlap

- 方法: `loadSourceCode` vs `getUser`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Loads a source file, applies syntax highlighting, and returns an HTML string.
- B 摘要: Retrieves a user by login from a database or a config file, creating a User object.
- 静态失败原因: Static BERT/GraphCodeBERT models often overemphasize syntactic patterns (e.g., try-catch, BufferedReader, while loop) and miss semantic differences, leading to false positives when boilerplate code is similar.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: The functions share only a common file-reading boilerplate pattern; their core purposes (source code highlighting vs user retrieval) are completely different, so BCB annotators would not consider them clones.
- 共享行为: Both use BufferedReader to read lines from an input stream.；Both have try-catch blocks for exception handling.；Both read lines in a while loop.
- 行为差异: Function A returns void and sets a field, while B returns a User object.；Function A reads a single file for source code display, while B may read from a database first or parse a config file.；Function A applies syntax highlighting via CodeViewer, while B parses tokens and creates a User.；Function A generates HTML output, while B saves the user to a DAO.
- 修正建议: Train on more diverse data to reduce sensitivity to common I/O patterns.；Incorporate data flow analysis to capture variable use and output differences.；Use contrastive learning to distinguish similar syntactic structures with different semantics.

### case_id=778 FP boilerplate_overlap

- 方法: `getFrameworkFactory` vs `run`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Get a FrameworkFactory by reading a service file from classpath and instantiating the specified class.
- B 摘要: Connect to a local web server and read all lines from its response, discarding them, with empty error handling.
- 静态失败原因: The static BERT/GraphCodeBERT likely over-relied on lexical and API sequence overlap: both use URL, BufferedReader, InputStreamReader, openStream, readLine, close. The model may have missed the deeper semantic differences in data usage, return values, and exception handling, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB expects semantic equivalence or near-equivalence. These functions have entirely different purposes: one is a factory loader that returns an object, the other is a void network read. Even though they share I/O boilerplate, the core functionality and outcomes differ, so BCB would label non-clone.
- 共享行为: Both open a URL and read lines using BufferedReader；Both use InputStreamReader and close the stream
- 行为差异: A loads a class and returns an instance; B does nothing with the read data；A throws an exception on failure; B silently catches exceptions；A reads from a classpath resource; B reads from an HTTP URL；A has conditional logic to skip comments; B does not
- 修正建议: Incorporate data flow analysis to track how read data is used (returned vs discarded).；Consider return types and method signatures more explicitly.；Use finer-grained tokenization that distinguishes between different API calls in context.；Add training examples with similar boilerplate but different semantics.

### case_id=779 FP boilerplate_overlap

- 方法: `createTar` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Creates a tar archive from a directory, handling file collection and writing to a TarOutputStream.
- B 摘要: Handles action commands from UI events, opening file choosers and updating preferences.
- 静态失败原因: Static BERT may rely on token overlap (e.g., 'File', 'null', 'if', 'return') and similar structural patterns like null checks and file existence checks, leading to false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clone because functions have completely different purposes and functionality despite both using File objects.
- 共享行为: Both involve file-related operations and conditional logic.
- 行为差异: Function A creates a tar archive, function B handles GUI events.；A uses TarOutputStream, B uses JFileChooser and Suku.kontroller preferences.；A is static utility method, B is an action listener override.；A writes binary data, B updates UI components.
- 修正建议: Improve model to distinguish between specific API usage (TarOutputStream vs JFileChooser) and overall purpose.；Incorporate control flow and data flow analysis.

### case_id=780 FN benchmark_preference_bias

- 方法: `modifyApplicationMessage` vs `convert`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Modifies a localized properties file by updating or adding a key-value pair for a given locale.
- B 摘要: Converts an ACRNEMA medical image file to DICOM format, handling pixel data and metadata.
- 静态失败原因: Static BERT/GraphCodeBERT models rely on lexical overlap and structural patterns. Given the low token Jaccard (0.13), the model correctly predicted non-clone. The model failed to match the BCB label because the BCB annotation appears inconsistent with typical BCB criteria.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB's broad Type-4 criteria might consider any file-conversion or modification as similar, but here the functionality differs significantly. The high token Jaccard distance (0.1279) indicates low lexical similarity, so BCB likely would not label this as a clone. The given label of 1 might be an annotation error.
- 共享行为: Both read from an input file and write to an output file.；Both involve I/O operations and handle exceptions.
- 行为差异: Function A operates on text properties files with key-value pairs; Function B operates on binary DICOM/ACRNEMA image files.；Function A modifies a single message entry; Function B performs a complete format conversion with pixel data manipulation.；Function A uses character streams and property parsing; Function B uses binary streams and DICOM tag processing.
- 修正建议: Verify the BCB label for this pair; it may be mislabeled. If correct, the model should learn to recognize extremely broad Type-4 clones based on generic I/O pattern, which is not recommended.

### case_id=781 FP lexical_or_api_overlap

- 方法: `main` vs `doFinishLoadAttachment`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Main method that parses Prolog file, generates adapter classes, and writes them to a JAR.
- B 摘要: Method that either saves an attachment to external storage or opens it in a viewer based on download completion.
- 静态失败原因: Static model likely overweighed superficial lexical overlaps (e.g., 'File', 'InputStream', 'OutputStream', 'try') and missed the lack of semantically equivalent behavior.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB considers them non-clones due to vastly different domain and purpose despite some shared low-level I/O patterns.
- 共享行为: Both perform file I/O operations；Both use try-catch for exception handling；Both have conditional logic based on input parameters
- 行为差异: Function A is a top-level entry point for code generation; Function B is a callback for attachment download；Function A manipulates bytecode and JAR files; Function B works with content URIs and external storage；Function A has complex object serialization and class writing; Function B has simple file copy or intent launch
- 修正建议: Train on more diverse data with emphasis on semantic similarity over token overlap.；Incorporate data-flow analysis to distinguish different use of shared APIs.；Add negative examples of methods that share common I/O but are unrelated.

### case_id=782 FN boilerplate_overlap

- 方法: `readIntoList` vs `invoke`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads HTML from a URL and populates a menu map with JMenuItem objects, parsing anchor tags.
- B 摘要: Invokes a remote service via HTTP POST, reads JSON response, and deserializes it to the return type, with retry logic.
- 静态失败原因: Static models like BERT/GraphCodeBERT rely on token overlap and structural similarity. These functions share only generic I/O boilerplate (BufferedReader, readLine), have low token Jaccard (0.137), and different method names, so the model correctly identified non-clone. The BCB label expects the model to abstract away the specific purpose and recognize the shared 'read from URL' pattern, which current static models struggle with due to lack of semantic understanding.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may consider any two functions that read from a URL and process line-by-line as having partial functionality similarity (Type-4 or broad Type-3), even if the outputs and purposes are completely different. This is a very lenient interpretation of functional equivalence.
- 共享行为: Both read from a URL using BufferedReader and InputStreamReader；Both loop over lines using while ((line = reader.readLine()) != null)；Both use try-catch for exception handling
- 行为差异: Function A parses HTML to extract command names and builds UI components, while B parses JSON for remote method invocation；Function A adds action listeners and populates a map, B handles HTTP status codes, retries, and returns deserialized object；Function A is for building a menu, B is for remote procedure call
- 修正建议: Incorporate dataflow analysis to detect common I/O patterns even when different APIs are used downstream；Use pre-training objectives that capture high-level semantic intent beyond token overlap；Consider partially matched functions as clones if they share a critical sub-computation (e.g., URL reading) despite different overall purposes

### case_id=783 FP lexical_or_api_overlap

- 方法: `readZoneIDs` vs `readVersion`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a file containing zone IDs as integer values, parses each line, and returns a HashSet of those integers.
- B 摘要: Reads a version file with key-value pairs (Version, Revision, Date), extracts the values, and sets corresponding instance fields.
- 静态失败原因: The static BERT-based model likely overemphasized the high lexical overlap in I/O patterns (URL.openStream, readLine, InputStreamReader, try-catch), and missed the semantic differences in parsing logic and output.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels these as non-clones because they have different purposes, input expectations, and output behaviors; they only share a common boilerplate pattern of reading a resource file.
- 共享行为: Both read a resource file via a URL and open stream.；Both use a loop to read lines of text from the file.；Both have exception handling that prints stack traces.
- 行为差异: Function A parses every line as an integer and collects them into a HashSet; Function B only processes lines with specific prefixes (Version=, Revision=, Date=).；Function A returns a collection of integers; Function B is void and sets object fields.；Function B includes null-check for URL and explicit resource cleanup (close reader in finally), which Function A lacks.；The input file formats and expected content are entirely different.
- 修正建议: Incorporate dataflow or program dependence features to distinguish different uses of read values.；Add negative samples with similar boilerplate but different core logic during training.；Use graph-based representations that capture variable usage and control flow differences.

### case_id=784 FP lexical_or_api_overlap

- 方法: `getJSONData` vs `getTicketsForQueue`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches JSON data from a given URL via HTTP GET and returns a JSONObject.
- B 摘要: Queries a ticket tracker for open tickets in a queue, parses ticket IDs, retrieves each ticket, and returns a list of RTTicket objects.
- 静态失败原因: The models likely overemphasized the common HTTP GET pattern (HttpGet, HttpResponse, BufferedReader) and boilerplate error handling, while missing the distinct semantic goals and data flows (e.g., building query parameters, parsing 'ticket/' lines, calling getTicket).
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels non-clones when functions have distinct purposes and outputs, despite shared HTTP boilerplate. The core functionality differs fundamentally (generic JSON download vs. specific ticket query with multiple steps).
- 共享行为: Both perform HTTP GET requests using HttpClient/HttpGet.；Both read response line-by-line using BufferedReader.；Both handle exceptions with try-catch blocks.
- 行为差异: Function A returns a JSONObject from the raw response; Function B parses response for ticket IDs and then fetches each ticket separately.；Function A has no limit parameter; Function B uses queue name and limit.；Function B includes additional error handling and logging, and closes streams with IOUtils.
- 修正建议: Incorporate data-flow analysis to track how the response is transformed.；Use type information (return type, method signature) as a discriminator.；Leverage method name and parameter semantics to disambiguate purpose.

### case_id=785 FN partial_functionality

- 方法: `invoke` vs `seeURLConnection`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Invokes a remote service via HTTP POST, retries on timeout with service discovery, parses JSON response, and returns the deserialized result.
- B 摘要: Opens a URL connection to a fixed site, reads the input stream line by line, and logs the result.
- 静态失败原因: Static BERT models rely heavily on token overlap and structural patterns; the low Jaccard similarity (0.14) and significant syntactic differences (retry, JSON parsing) overshadow the shared I/O pattern, leading to a false negative.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: None
- 共享行为: Both establish HTTP connections；Both read the response line by line using BufferedReader；Both use StringBuilder to accumulate lines
- 行为差异: Function A uses POST, Function B uses GET；Function A has retry logic and service discovery; B has none；Function A parses JSON and returns typed object; B only logs；Function A handles generic return types and exceptions; B does not
- 修正建议: Incorporate API call sequence similarity to capture shared I/O operations；Use code summarization or program intent embedding to recognize high-level functional similarity；Train with contrastive learning on partial functionality clones to improve robustness

### case_id=786 FN lexical_or_api_overlap

- 方法: `doVersionCheck` vs `invoke`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.85`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Checks for a newer version of jEdit by reading a remote properties file and comparing build numbers.
- B 摘要: Invokes a remote HTTP method with retry logic, parsing JSON response and returning the result.
- 静态失败原因: Static BERT/GraphCodeBERT models rely heavily on lexical and structural overlap; low token Jaccard (0.16) and different API usage (URL.openStream vs HttpPost) led to a non-clone prediction, missing the underlying structural similarity of the read-loop pattern.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may label these as clones due to both involving the common pattern of reading from a URL line by line and processing the data, considering them as partial functional similarity (Type-4) despite different specific purposes.
- 共享行为: Both read from a URL using InputStream and BufferedReader；Both parse lines read from the stream；Both handle IOException in a try-catch block
- 行为差异: A is a static void method for version checking; B returns Object and may throw Throwable；A uses jEdit-specific properties and UI messaging; B uses generic HTTP client and JSON utilities；A performs a single read and compares build numbers; B reads an HTTP response, parses JSON, and handles retries on timeout；A shows UI messages (up-to-date or new version); B returns the deserialized object or null
- 修正建议: Incorporate data flow analysis to capture common I/O patterns beyond token overlap；Use contrastive learning with hard negatives that share structure but differ in purpose；Enhance model with functional annotations or program logic summarization

### case_id=787 FN partial_functionality

- 方法: `getHTML` vs `doVersionCheck`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads HTML from a URL and optionally saves it to a file, returning the HTML string.
- B 摘要: Checks for version updates by reading a version file from a URL, parsing specific build numbers, and then performing the version check.
- 静态失败原因: Static BERT/GraphCodeBERT models rely heavily on lexical and syntactic overlap, which is low (token Jaccard 0.216). The models fail to capture the underlying semantic pattern of network I/O and line reading, instead focusing on dissimilar method names, variable names, and structural details. The absence of high-level dataflow information prevents recognizing the common abstract behavior.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider this a Type-4 semantic clone because both functions share the common high-level behavior of downloading and processing text from a URL line by line, even though the specific processing logic differs. The BCB benchmark includes pairs where the overall task (e.g., reading from a network resource and parsing) is similar, aligning with broad Type-4 annotations.
- 共享行为: Open URL connection and read lines using BufferedReader；Loop over lines read from the URL stream；Handle IOException (though in different ways)；Close the input stream in a finally-like pattern
- 行为差异: Function A returns HTML content and can write to a file; function B is void and calls another method for version comparison；Function A uses HttpURLConnection with custom User-Agent; function B uses URL.openStream()；Function A handles exceptions by printing stack trace; function B shows an error dialog；Function A processes all lines equally; function B only processes lines starting with specific prefixes
- 修正建议: Enhance training with Type-4 clone pairs that share high-level goals but differ in implementation details；Use dataflow analysis or program graphs to expose the I/O and control-flow patterns (e.g., reading from URL, looping over lines)；Incorporate attention over API call sequences to detect repeated patterns like 'openStream => BufferedReader.readLine'；Leverage contrastive learning to push representations of functionally similar methods closer

### case_id=788 FN partial_functionality

- 方法: `copyResource` vs `copyJar`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource (URL or file) byte-by-byte to a destination file, throwing an exception if resource not found.
- B 摘要: Copies a source file to a destination file using FileChannel.transferFrom, logging any IOException.
- 静态失败原因: Static BERT focused on lexical and structural differences (low token overlap, different APIs like FileChannel vs InputStream, different exception handling), missing the overarching functional similarity of copying between sources.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider them clones because both implement the high-level functionality of copying a resource to a file, accepting broad Type-4 similarity despite different I/O mechanisms and exception handling.
- 共享行为: Both copy data from a source to a destination file.；Both handle exceptions and close streams.
- 行为差异: copyResource reads from URL or file via InputStream; copyJar uses FileChannel.；copyResource uses byte-by-byte copy; copyJar uses transferFrom for efficient transfer.；copyResource throws generic Exception; copyJar catches IOException and logs it.；copyResource takes no direct parameters (uses fields); copyJar takes src and dst Files.
- 修正建议: Train on pairs with low lexical overlap but same high-level purpose (e.g., copy, move, filter).；Incorporate dataflow analysis to detect copy semantics (e.g., reading from source and writing to destination).；Use contrastive learning to emphasize functional intention over surface form.

### case_id=789 FP boilerplate_overlap

- 方法: `encodeFileToFile` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Encodes a file to another file using Base64 encoding with buffered I/O.
- B 摘要: Handles GUI action events to set file paths and preferences for a Suku application.
- 静态失败原因: Despite low token Jaccard similarity, the static BERT model may have been misled by overlapping boilerplate patterns (e.g., try-catch, null checks, file-related variables) or API tokens like 'File', 'InputStream', 'OutputStream' that appear in both, though used differently. The model likely lacked the semantic understanding to distinguish between file I/O utility code and GUI event handling.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would label this as non-clone because the functions have entirely different purposes: one is a utility for file encoding, the other is a GUI event handler. Even with relaxed Type-4 criteria, there is no meaningful functional overlap.
- 共享行为: Both involve file handling in a broad sense, but with different goals.
- 行为差异: A performs actual file reading/writing and Base64 encoding; B only retrieves file paths via JFileChooser.；A has a simple loop reading and writing bytes; B has complex conditional logic for multiple commands and settings.；A uses low-level I/O streams; B uses Swing components and preferences API.；A returns a boolean success flag; B returns void and updates GUI state.
- 修正建议: Improve training data to include more diverse functional contexts.；Incorporate dataflow or control-flow analysis to differentiate I/O loops from GUI event dispatch.；Use a model that captures long-range dependencies and method-level intent.

### case_id=790 FP lexical_or_api_overlap

- 方法: `downloadURLtoString` vs `getTicketsForQueue`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Downloads a URL and returns its content as a string.
- B 摘要: Retrieves a list of open tickets for a queue from a REST API and returns them as a list.
- 静态失败原因: Static BERT models may have been misled by common tokens such as 'BufferedReader', 'InputStreamReader', 'readLine', and 'close', which appear in both code snippets. The models may have overemphasized lexical overlap and missed the semantic differences in the overall logic and purpose.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels as non-clone because the two functions have entirely different purposes and outputs. Even though they share low-level I/O patterns, the high-level functionality is unrelated.
- 共享行为: Both use BufferedReader and InputStreamReader to read streams of text.；Both involve reading lines from an input stream.；Both use try-catch blocks for exception handling (though in different styles).
- 行为差异: Function A simply reads all lines from a URL stream, appends them, and returns the concatenated string; function B constructs a query, executes an HTTP GET, parses the response for ticket IDs, fetches each ticket, and returns a list of tickets.；Function A returns a String; function B returns a List<RTTicket>.；Function A does not handle HTTP status codes or query parameters; function B does extensive HTTP interaction and parsing.；Function A has no loop over parsed IDs; function B iterates over ticket IDs and calls another method.
- 修正建议: Improve the model's ability to distinguish boilerplate I/O patterns from core logic by using control-flow or dataflow representations.；Incorporate higher-level structural matching (e.g., function signatures, return types, external calls) to reduce false positives from low-level token similarity.

### case_id=791 FN partial_functionality

- 方法: `doTransfer` vs `loadMFileViaWeb`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Forwards an HTTP request to another URL by copying headers and body, then returns the response.
- B 摘要: Loads a .m file from a URL over HTTP, reads its content, and parses it into a UserFunction object.
- 静态失败原因: Static BERT models often rely on token-level overlap and syntactic patterns; the low token Jaccard (0.1) and different method names/structures likely caused it to miss the overarching thematic similarity of 'loading from web', categorizing them as distinct tasks.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider these clones because both involve fetching data from a URL over HTTP and reading stream content, aligning with Type-3/Type-4 broad similarity in functionality (web resource retrieval).
- 共享行为: Both open a URL connection and read input streams.
- 行为差异: doTransfer acts as an HTTP proxy, forwarding requests and responses; loadMFileViaWeb only downloads a file.；doTransfer sets multiple HTTP headers and handles request/response cycles; loadMFileViaWeb only reads content.；doTransfer writes data to the response output stream; loadMFileViaWeb returns a parsed object.；doTransfer handles error codes by sending an error response; loadMFileViaWeb throws an exception on error.
- 修正建议: Incorporate program dependence graphs or control-flow analysis to capture high-level intent.；Use a model with better understanding of API usage patterns and common functionalities like URL stream reading.；Train on clone examples that share common library usage even when tokens differ.

### case_id=792 FN benchmark_preference_bias

- 方法: `main` vs `modifyApplicationMessage`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: main method demonstrating PDF signing and verification using iText library.
- B 摘要: method modifying a properties file for internationalization, replacing or adding a key-value pair.
- 静态失败原因: The static BERT model correctly predicted non-clone; the misclassification is due to BCB's overly broad annotation preference, not a model error.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB likely considered them clones due to superficial similarities such as file I/O, try-catch structure, and exception printing, but the core semantics are completely unrelated.
- 共享行为: general file I/O operations；exception handling with printStackTrace；use of streams and readers
- 行为差异: different domains: PDF signing vs properties modification；different libraries: iText vs java.util.Properties；different control flow and data manipulation；different input/output purposes
- 修正建议: Ensure benchmark annotations reflect true semantic equivalence；Use more precise criteria for Type-3/Type-4 classification

### case_id=793 FP lexical_or_api_overlap

- 方法: `readZoneIDs` vs `run`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads integer IDs from a resource file into a HashSet.
- B 摘要: Reads a formatted URL content, extracts version and url fields, accumulates additional info, and notifies listeners.
- 静态失败原因: Static BERT over-relied on lexical and API overlap (e.g., InputStreamReader, readLine, openStream, catch, Exception) while ignoring the distinct data processing logic and output behavior.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels 0 because the core functionality differs entirely; the common I/O pattern is just boilerplate, not functional equivalence.
- 共享行为: Both read lines from an InputStream using a buffered reader；Both catch exceptions and print stack trace
- 行为差异: Data source: resource file vs. URL；Return type: HashSet<Integer> vs. void；Parsing logic: simple integer parsing vs. multi-field extraction based on line index；Error handling: B has more specific error messages and a finally block with listener notification
- 修正建议: Include dataflow and program structure features to distinguish boilerplate from core logic.；Enhance training with more examples that share I/O patterns but differ in semantics.；Use graph-based models (e.g., AST or CFG) to capture structural differences.

### case_id=794 FP lexical_or_api_overlap

- 方法: `storeImage` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Stores an uploaded image to a date-based folder, optionally creating resized copies, and returns the relative path.
- B 摘要: Handles action events to manage application settings like file paths for external tools, look-and-feel, and UI components.
- 静态失败原因: Static BERT may have focused on lexical similarities (e.g., 'File', 'getAbsolutePath', 'fileName', 'extension') and the general pattern of file path construction, ignoring the vastly different overall logic and purpose.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled non-clone because the functions are semantically unrelated; one is a file storage utility, the other is an event-driven settings handler. No partial functional overlap beyond trivial API usage.
- 共享行为: Both use File and getAbsolutePath for file path operations.；Both involve file I/O concepts (InputStream/OutputStream vs JFileChooser).
- 行为差异: A stores binary image data; B handles UI events and configuration updates.；A performs image resizing; B has no image processing.；A returns a path string; B updates UI components and saves preferences.；A's control flow is sequential with conditional resizing; B's is a long event handler with multiple command branches.
- 修正建议: Incorporate control-flow and data-flow analysis to capture function semantics.；Use longer-range context or hierarchical embeddings to distinguish event handlers from data processing functions.；Train on more diverse examples to reduce reliance on surface-level API matches.

### case_id=795 FP boilerplate_overlap

- 方法: `readTwitterFead` vs `doVersionCheck`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.85`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a Twitter timeline JSON feed from a hardcoded URL using HttpClient and returns the entire content as a string.
- B 摘要: Checks for version updates by reading a version file from a URL obtained from a property, parses lines to extract version numbers, and invokes another version check method.
- 静态失败原因: The model likely over-relied on structural similarities such as the common pattern of opening a stream, creating a BufferedReader, reading lines, and handling IOException. The sequence of API calls is similar despite different intents.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely views these as non-clones because the overall functionality differs: one is a feed fetcher, the other is a version checker. Although both involve reading a URL, the specific processing, error handling, and return types are distinct.
- 共享行为: Retrieve text content from a URL over HTTP；Read the content line by line using BufferedReader
- 行为差异: A uses Apache HttpClient and checks HTTP status; B uses URL.openStream() with no status check；A returns the entire response body; B parses specific lines and calls another method；Error handling differs: A logs and prints stack trace; B shows error dialog and hides wait cursor
- 修正建议: Use more semantic-aware features like method name, comments, or overall purpose；Consider including type information (return type) and distinguishing between functions that consume vs produce data；Train models to ignore common boilerplate and focus on core logic

### case_id=796 FN partial_functionality

- 方法: `testNetworkHTTP` vs `retrieveQ`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.75`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: A test method that performs multiple HTTP GET requests to hardcoded URLs, discarding the response lines for side effects.
- B 摘要: A utility method that retrieves the content of a single URL and returns it as a string.
- 静态失败原因: Low token Jaccard (0.19) and different method structure (test vs utility) overshadow the shared HTTP read pattern, causing a false negative.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label these as Type-4 clones because both perform HTTP GET operations and read response lines, sharing core functionality despite different contexts.
- 共享行为: Open HTTP/URL connections；Read input stream via BufferedReader；Use while loop with readLine()
- 行为差异: Function A executes multiple requests sequentially; B does one；Function A discards response; B builds and returns a string；Different signatures and error handling
- 修正建议: Incorporate data-flow and control-flow features；Use API usage embeddings to capture HTTP pattern similarity；Add graph-based representations to model structural commonalities

### case_id=797 FN lexical_or_api_overlap

- 方法: `copyResource` vs `createFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource from a URL or local file to a destination file using byte-by-byte stream copying.
- B 摘要: Copies a source file to a managed resource using FileInputStream and IOUtils.copy with error logging.
- 静态失败原因: Low token overlap (0.125) and different method names, control structures, and library usage (URL vs File, IOUtils) lead BERT-based models to assign low similarity, missing the semantic equivalence of the core copying functionality.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB often labels Type-4 clones as clones when they perform the same high-level task (copying data from source to destination) despite differences in API usage, control flow, or error handling.
- 共享行为: Both open an input stream and output stream；Both copy bytes from input to output；Both close the streams after copying
- 行为差异: Function A supports both URL and file input; B only file input；Function A writes to a local FileOutputStream; B writes to a resource manager output stream；Function A uses manual byte-by-byte copying; B uses IOUtils.copy (Apache Commons)；Function A throws Exception; B throws IOException and catches ResourceManagerException
- 修正建议: Use data-flow analysis to compare input/output stream operations；Incorporate API call semantics (e.g., IOUtils.copy vs manual loop)；Consider higher-level functional similarity based on resource manipulation patterns

### case_id=798 FN partial_functionality

- 方法: `httpRequestByPOST` vs `read`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends an HTTP POST request with parameters and reads the response line by line into a string, returning the string or null on error.
- B 摘要: Reads content from a URL or file path by opening a stream and delegating to another read method, returning a status integer.
- 静态失败原因: Low token overlap (0.16) and different control structures; BERT-based models may rely on superficial lexical or structural similarity, which is low here.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB might have labeled as clone due to both functions involving network I/O and reading input, but they differ significantly in purpose and implementation.
- 共享行为: Both involve opening a stream and reading from it；Both handle IOException and set error status codes；Both return a result (string or status) after reading
- 行为差异: A performs HTTP POST with form parameters; B reads from URL or file without HTTP method；A reads line by line into a StringBuffer; B delegates to another method for reading；A returns a String or null; B returns an int status code；A handles HTTP status codes (<400); B does not check HTTP status
- 修正建议: Incorporate data flow analysis to distinguish HTTP request construction from file/URL reading；Use API-level semantics to differentiate HTTP client operations from generic stream I/O；Add training examples with low token similarity but different high-level tasks

### case_id=799 FN partial_functionality

- 方法: `File2String` vs `getPagina`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a local file (or classpath resource) line by line and returns its content as a string, exits on errors.
- B 摘要: Reads a web page from a URL line by line and returns its content as a string, returns error string on exceptions.
- 静态失败原因: Static BERT methods rely on token overlap and structural similarity. The token Jaccard is low (0.26), and they have different method names and vocabulary (file vs. url). The model likely focused on API differences (FileInputStream vs. URL) and error handling (exit vs. return error) and missed the high-level semantic similarity of resource reading.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as 'read resource and return string' clones due to similar control flow and I/O pattern, despite different sources, and may overlook error handling differences as minor.
- 共享行为: Both read input (file or URL) line by line and concatenate lines into a single string.；Both use BufferedReader and InputStreamReader to read text.；Both handle I/O exceptions (though differently).
- 行为差异: Source of input: local file vs. URL.；Error handling: function A calls System.exit on error; function B returns error string.；Function A includes fallback to classpath resource; function B does not.；Function B sets an Authenticator (Autenticador) which A does not.
- 修正建议: Increase representation of overall I/O pattern beyond specific API calls.；Use graph-based methods that capture control flow and data flow similarity.；Include pre-training on code with semantic similarity tasks like code summarization.

### case_id=800 FP partial_functionality

- 方法: `getContent` vs `downloadModel`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Executes an HTTP request and returns the full response content as a string by reading lines.
- B 摘要: Downloads an RDF model from a URL by opening an HttpURLConnection, setting headers, and reading the input stream into a Model object.
- 静态失败原因: The model likely over-relied on shared lexical tokens (HttpURLConnection, InputStream, etc.) and structural patterns (try-catch, open connection, read stream), missing the semantic divergence in purpose and return type.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB typically labels as non-clone (Type 0) because the high-level functionality differs significantly (fetching raw content vs. loading a semantic model). Even under broad Type-3/4, the difference in data processing and purpose outweighs the shared HTTP usage.
- 共享行为: Both perform HTTP connections and read input streams；Both use standard Java I/O patterns
- 行为差异: Different return types: String vs Model；Different input: HttpUriRequest vs String URL；A reads lines into a string buffer; B reads into an RDF model；Different exception handling: A throws Exception; B catches specific exceptions and wraps in RuntimeException
- 修正建议: Improve negative sampling with pairs that share API usage but differ in high-level goal；Incorporate return type and input type into the representation；Use contrastive learning to distinguish similar API sequences with different semantics

### case_id=801 FN benchmark_preference_bias

- 方法: `MotixFileItem` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Constructor that reads an InputStream into a byte array, extracts file metadata (name, contentType, extension, image flag), and optionally reads a BufferedImage from the stream.
- B 摘要: Method that builds a site for editing by reading XML files, performing XSLT transformations, and writing output files for each page, with extensive debugging and error handling.
- 静态失败原因: Static BERT correctly predicted non-clone due to very low token Jaccard similarity (0.059) and completely different structural patterns; it did not fail but matched our analysis.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled these as clones due to both involving I/O operations (InputStream vs FileInputStream), but the similarity is too superficial and likely a benchmark annotation error.
- 行为差异: Function A is a short constructor; function B is a long method with complex control flow.；Function A reads a single InputStream; function B reads multiple files and performs XML transformations.；Function A deals with image processing; function B deals with web page generation.；Function A uses Apache Commons IO; function B uses custom file system and FTP exception handling.
- 修正建议: Re-evaluate the BCB label for this pair; it may be a false positive in the benchmark.；Improve training data quality to remove such noisy annotations.；Use more robust semantic matching techniques beyond token overlap.

### case_id=802 FN partial_functionality

- 方法: `main` vs `createNew`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a URL and extracts its zip entries to individual files.
- B 摘要: Creates a new file in a directory with access control, writing an input stream to it.
- 静态失败原因: The static model correctly predicted non-clone; it did not fail relative to our analysis. If considered against BCB label, the model missed due to low token overlap and different control flow, but that aligns with semantic differences.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled these as clones due to the shared file writing pattern and use of similar API calls (FileOutputStream, etc.), considering them as partial functionality similarity under broad Type-4.
- 共享行为: Both write data from an input stream to a file using FileOutputStream.
- 行为差异: Function A reads from a ZipInputStream and extracts multiple entries; Function B writes a single input stream.；Function B includes access control and conditional file naming; Function A does not.；Function A outputs to current directory; Function B outputs to a specific folder.；Function A uses BufferedOutputStream; Function B uses IOUtils.copy.
- 修正建议: Improve representation to capture high-level task semantics rather than surface API similarity.；Incorporate control flow and data flow analysis to distinguish different purposes.

### case_id=803 FP boilerplate_overlap

- 方法: `run` vs `downloadModel`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a resource file from classpath and displays its content in a GUI text area on the Swing event thread.
- B 摘要: Downloads an RDF model from a URL and returns it.
- 静态失败原因: The static model may have been misled by similar boilerplate patterns (try-catch with stream reading) and the presence of common I/O classes (InputStream, BufferedReader), while failing to capture the distinct functional contexts and data flows.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the functions serve completely different purposes and have different inputs, outputs, and error handling; they are not functionally similar at all.
- 共享行为: Both use InputStream to read data；Both handle exceptions
- 行为差异: Input source: classpath vs URL；Output: string for GUI vs Model object；Error handling: silent catch vs logging and rethrow；Threading: uses SwingUtilities.invokeLater vs direct execution
- 修正建议: Incorporate method-level purpose or domain knowledge via embeddings；Use dataflow analysis to distinguish between local file access and remote HTTP downloads；Add training examples with diverse I/O operations to reduce boilerplate-induced false positives

### case_id=804 FN partial_functionality

- 方法: `addIDs` vs `init`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Retrieves metabolite information from the GMD web service for a given name, parses HTML, and populates multiple fields of a PeakListRow object with database identifiers and molecular weight.
- B 摘要: Initializes a servlet context by loading controller classes from registry files found on the classpath.
- 静态失败原因: Static BERT models may have been misled by the shared high-level pattern of opening a URL, reading lines, and handling exceptions, while failing to capture the domain-specific processing logic and output types.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have considered these clones due to superficial structural similarity: both methods open a stream, read lines, and process them within a try-catch. However, the core functionality (metabolite data retrieval vs. controller class loading) is entirely different, so BCB likely made an error or used an overly broad definition of functional similarity.
- 共享行为: Both open an external resource (URL or resource file) using URL.openStream()；Both read lines using BufferedReader in a loop；Both handle IOException in a try-catch block
- 行为差异: A accesses a specific web service URL based on input name; B loads classpath resources with a fixed filename；A parses HTML to extract metabolite data; B reads class names and loads them via ClassLoader；A sets multiple fields on a row object; B adds classes to a servlet context；A returns an integer score; B returns void
- 修正建议: Incorporate domain-specific embeddings to distinguish different kinds of data processing；Use contrastive learning with examples of similar I/O patterns but different semantics；Improve long-range semantic understanding to focus on the transformation of input to output

### case_id=805 FP lexical_or_api_overlap

- 方法: `fetchURLData` vs `readData`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Downloads data from a URL (HTTP or file) and returns it as a byte array.
- B 摘要: Parses comma-separated string fields into sets and maps for initializing Tibetan transliteration data.
- 静态失败原因: The model likely over-relied on superficial similarities like both having 'data' in method name, both using I/O patterns (streams vs tokenizers), and similar error handling constructs, despite radically different high-level purpose.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels them non-clone because they have completely different functionality and no shared semantics beyond trivial I/O patterns.
- 共享行为: Both read input data；Both use similar error handling patterns (try-catch, close resources)
- 行为差异: A is network I/O, B is string parsing；A returns byte array, B modifies global sets/maps；A uses HttpURLConnection, B uses StringTokenizer；A is public static, B is private static
- 修正建议: Improve model's ability to distinguish between different types of data processing (network vs string parsing)；Add more negative examples with similar I/O constructs but different semantics；Enhance representation of method purpose via data flow analysis

### case_id=806 FN benchmark_preference_bias

- 方法: `fileDownload` vs `createHTML`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a file from a URL to a fixed local path using Java I/O streams.
- B 摘要: Generates an HTML page string based on a request page type, reading CSS from resources and building dynamic content.
- 静态失败原因: Static BERT/GraphCodeBERT models typically rely on token overlap and syntactic structure, which is low here. They fail to capture the high-level abstract similarity of 'reading from a source and processing line-by-line' that BCB might use for Type-4 annotation.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider these as clones due to shared API usage patterns (URL, streams, buffered reading) and exception handling, despite different ultimate purposes, reflecting a broad Type-4 semantic clone interpretation.
- 共享行为: Both use URL to access external resources；Both use BufferedReader and InputStreamReader to read data；Both handle exceptions with logging
- 行为差异: A writes binary data to a file; B builds and returns an HTML string；A has no conditional logic based on input; B uses a switch on requestPage；A has a fixed output filename; B generates content dynamically from database；A reads raw bytes; B reads lines and appends strings
- 修正建议: Incorporate program analysis to identify abstract I/O patterns；Use data-flow analysis to track how inputs are processed；Train with broader semantic similarity annotations beyond token overlap

### case_id=807 FN partial_functionality

- 方法: `getFile` vs `doGet`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies its endpoint, and saves locally.
- B 摘要: Proxies an HTTP request to a Fedora URL by forwarding headers and copying the response stream.
- 静态失败原因: The functions have very low token overlap (Jaccard 0.077) and different structural patterns; the model captures these differences and predicts non-clone, but misses the potential semantic similarity in network I/O usage.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as 'HTTP connection handling' tasks, focusing on the common pattern of URL.openConnection() and stream copying, despite different high-level purposes.
- 共享行为: Both open HTTP URL connections；Both copy data from an input stream to an output stream；Both use logging statements
- 行为差异: A modifies XML and writes to a local file; B forwards HTTP request/response；A has error handling with AxisFault; B throws ServletException/IOException；A does file existence check; B does not；A uses NIO channels; B uses IOUtils.copy
- 修正建议: Enhance model to recognize shared API usage patterns (e.g., URL.openConnection, IOUtils.copy) even with different function signatures.

### case_id=808 FN benchmark_preference_bias

- 方法: `updateFile` vs `doGet`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Copies a file from a source to a destination using FileChannel.
- B 摘要: Handles HTTP GET request to retrieve and render a page with authorization and caching logic.
- 静态失败原因: The static model correctly predicted non-clone due to very low token overlap (0.0648) and no clear semantic similarity.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have mislabeled due to both functions involving file I/O operations (copy vs. write) and exception handling, but overall semantics are unrelated.
- 行为差异: Function A performs simple file copy; Function B is a complex servlet handler.；Function A uses FileChannel; Function B uses PrintWriter and HttpServletResponse.；Function A has no user interaction; Function B processes HTTP parameters and user permissions.；Function A is a private utility; Function B is a public HTTP endpoint.
- 修正建议: Re-evaluate BCB annotation for this pair to correct potential mislabeling.；Focus on functional equivalence rather than superficial structural similarities.

### case_id=809 FN partial_functionality

- 方法: `fileDownload` vs `sendRequest`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a file from a URL and saves it to a local file.
- B 摘要: Sends an XML request to a servlet with GZIP compression and parses the XML response.
- 静态失败原因: Low token overlap (0.12) and different method names and control flow led the model to treat them as unrelated, missing the high-level functional similarity of network streaming.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider these clones because both involve network communication via URLConnection, streaming data, and exception handling, aligning with Type-4 broad semantic similarity of 'network I/O operations'.
- 共享行为: Both open a URLConnection to a remote server.；Both use I/O streams (InputStream, OutputStream) for data transfer.；Both handle network-related exceptions (catch Exception).
- 行为差异: A reads data from the URL and writes to a local file; B writes request data to the URL and reads the response.；B uses GZIP compression on the output and input streams; A does not.；B parses the response into a JDOM document; A writes raw bytes/characters to a file.；A takes a destination path; B returns an empty string and relies on Preferences for server configuration.
- 修正建议: Enhance model with API usage patterns (URLConnection, streams).；Incorporate data flow analysis to detect common I/O patterns.；Train on examples of broad Type-4 clones that share subtask but differ in overall goal.

### case_id=810 FP dataflow_blindspot

- 方法: `getRequestContent` vs `CheckUrl`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_with_trace`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Opens a URL connection, reads the first line, closes resources, throws exception on failure.
- B 摘要: Tries to open a URL connection, reads the first line, returns empty string on any exception, does not close resources.
- 静态失败原因: Static BERT/GraphCodeBERT likely focused on lexical and structural similarity (e.g., URL, HttpURLConnection, readLine) and overlooked the dataflow differences from exception handling and resource management, leading to a false positive.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 dataflow_trace_and_outputs。
- BCB 偏好解释: BCB labels this non-clone because significant behavioral differences in exception handling (throws vs. return empty) and resource cleanup change the function contract, preventing semantic equivalence.
- 共享行为: Both take a URL string as input；Both create URL and open HttpURLConnection；Both read the first line via BufferedReader；Both return the first line as String
- 行为差异: A throws Exception on failure; B catches Exception and returns empty string；A explicitly closes resources; B does not；A is instance method; B is static；B uses toString() on read line (redundant)
- 修正建议: Train with examples highlighting exception handling and resource management differences；Incorporate data flow analysis to track exception paths；Use contrastive learning to distinguish silent failure from exception propagation

### case_id=811 FN benchmark_preference_bias

- 方法: `readAndRewrite` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Reads a DICOM image file, parses it, extracts pixel data, and writes it to an output file.
- B 摘要: Launches a NexOpen project configuration, processes Maven POM files, sets Hibernate dialect, and runs an install action.
- 静态失败原因: The model correctly predicted non-clone; it did not fail. The BCB label is likely a false positive due to overly broad interpretation of functional similarity.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled as clone due to both functions involving file reading/writing and XML-like processing (A reads DICOM which is binary, B reads pom.xml which is XML), but the domains and actual operations are fundamentally different.
- 行为差异: Function A involves medical image processing (DICOM), while B involves IDE project configuration (Eclipse/ NexOpen).；A performs file I/O with ImageInputStream/ImageOutputStream; B uses IProject, IFile, and ByteArrayOutputStream for project resources.；A uses DICOM-specific APIs (DcmParser, PixelDataReader); B uses Maven and Hibernate configuration APIs.；A has no error handling beyond IOException; B has multiple try-catch and exception types (CoreException, IOException).
- 修正建议: Improve BCB annotation guidelines to exclude pairs with no functional similarity.；Use domain-aware features to avoid matching unrelated file I/O operations.

### case_id=812 FN lexical_or_api_overlap

- 方法: `doGet` vs `unzipEntry`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Handles HTTP GET request to retrieve and display a portal page with logging and caching.
- B 摘要: Extracts a zip entry to a file, creating directories as needed.
- 静态失败原因: The static model predicts non-clone correctly due to extremely low lexical overlap (token Jaccard=0.048) and no shared APIs or control flow. From BCB's perspective, the model fails because it cannot recognize abstract similarity beyond surface tokens.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may label this as a Type-4 clone because both functions implement a generic 'read-process-write' pattern at a very high abstraction level, though the concrete functionality is entirely different.
- 共享行为: Both involve reading from an input source and writing to an output sink.
- 行为差异: A is a web request handler with complex business logic; B is a file extraction utility.；A uses HttpServletRequest/Response; B uses ZipFile and File streams.；A has extensive exception handling and property retrieval; B has simple try-finally stream cleanup.；A includes caching and statistics; B has no such features.
- 修正建议: Incorporate abstract pattern recognition for generic I/O operations.；Use semantic role labeling to identify common high-level intents.；Combine structural analysis with domain-specific knowledge.

### case_id=813 FP lexical_or_api_overlap

- 方法: `sendPost` vs `SRWGuiClient`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Sends an HTTP POST request to a URL with parameters and returns the response body as a string.
- B 摘要: Constructor of a Swing GUI browser that reads a URL, optionally processes XML/XSLT, and displays HTML content.
- 静态失败原因: The static BERT/GraphCodeBERT model likely overemphasized lexical similarities in I/O patterns (e.g., 'URL', 'BufferedReader', 'InputStreamReader') and the try-catch structure, while missing the divergent high-level semantics (network utility vs. GUI constructor). Low token Jaccard suggests the model may have relied on subsequence matching or API co-occurrence.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically considers clones as functionally similar code fragments, often in terms of I/O patterns or common API usage. This pair only shares trivial I/O boilerplate, not meaningful functional overlap, so BCB labels as non-clone.
- 共享行为: Both use BufferedReader and InputStreamReader to read from a URL.；Both use try-catch blocks for error handling.
- 行为差异: Function A performs HTTP POST request; function B initializes a GUI and reads content for display.；Function A uses HttpURLConnection and PrintWriter; function B uses URL.openStream() and Swing components.；Function A returns a string result; function B sets up a JEditorPane and frame visibility.；Function B includes complex XML/XSLT processing; function A does not.
- 修正建议: Increase training data diversity to reduce reliance on common API sequences.；Incorporate global control flow or data flow information to distinguish different usage contexts.；Use contrastive learning to push apart functions with different purposes but similar low-level APIs.

### case_id=814 FN boilerplate_overlap

- 方法: `modifyApplicationMessage` vs `convert`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Modify a localization properties file by adding or updating a message key-value pair for a given locale.
- B 摘要: Convert a medical image file from ACRNEMA to DICOM format, handling pixel data and UID assignment.
- 静态失败原因: Static BERT/GraphCodeBERT models rely on token overlap and structural patterns. Both functions share common Java API tokens (File, InputStream, OutputStream, Buffered*), and both have similar control flow (try blocks, while loops). This lexical and structural overlap can mislead the model into predicting a clone, despite vastly different semantics.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB typically considers Type-3/Type-4 clones with partial functionality similarity. Here, the only commonality is low-level file I/O, which is too broad. The BCB label of 1 may be an annotation error or based on a different interpretation.
- 共享行为: Both perform file I/O operations (reading and writing).；Both use try-finally or try-catch for resource management.
- 行为差异: Function A works with text properties files; Function B works with binary DICOM files.；Function A modifies key-value pairs; Function B restructures file format metadata.；Function A has no pixel data handling; Function B deals with pixel data inflation.；Function A catches generic Exception; Function B throws IOException.
- 修正建议: Incorporate dataflow analysis to capture variable dependencies on specific domain objects.；Use type-aware embeddings that differentiate between text and binary file processing.；Add contrastive training examples with high API overlap but different semantics.

### case_id=815 FN partial_functionality

- 方法: `testReadHelloWorldTxt` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.5`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Tests file content resolution using FSContentResolver with various path formats, verifying correct content retrieval and null handling.
- B 摘要: Launches a NexOpen project configuration by validating project, processing Maven POM files, setting Hibernate dialect, and scheduling an install job.
- 静态失败原因: BERT focused on low token overlap and distinct method names/structures, missing the subtle API-level similarity. The large difference in length and control flow likely dominated the representation.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB might have considered the common use of IOUtils.copy for file resource manipulation as shared functionality, deeming them as Type-4 clones despite different contexts.
- 共享行为: Both methods copy data from an InputStream to an OutputStream using IOUtils.copy；Both handle file system resources
- 行为差异: Function A is a JUnit test with assertions; Function B is a complex configuration method with XML processing, property settings, and project operations；Overall purposes are entirely different: testing vs. launch configuration
- 修正建议: Increase sensitivity to shared API usage patterns；Incorporate finer-grained structural matching for resource handling methods

### case_id=816 FP lexical_or_api_overlap

- 方法: `actionPerformed` vs `copyParseFileToCodeFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Handles user commands in a settings dialog, opening file choosers and saving preferences.
- B 摘要: Copies a file from one path to another using byte streams.
- 静态失败原因: The static model may have been misled by superficial lexical similarities such as common tokens like 'File', 'IOException', or the presence of file-related operations in both methods, despite the vast difference in context and overall behavior.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the two methods have fundamentally different purposes and functionality, with no significant overlap in behavior or logic.
- 行为差异: Method A is a large event handler with multiple conditional branches, GUI interactions, and preference storage.；Method B is a simple file I/O utility with no GUI involvement.；Method A does not perform file content copying; it only selects and records file paths.；Method B does not handle any GUI or user interaction.
- 修正建议: Improve model's ability to capture long-range dependencies and overall control flow.；Incorporate structural information like function call graphs or data flow to distinguish simple utility from complex event handlers.；Increase training data variety to reduce bias towards API token overlap.

### case_id=817 FN benchmark_preference_bias

- 方法: `setup` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Extracts native libraries from a JAR file and adds the native library path.
- B 摘要: Builds HTML pages for editing by processing XML, performing transformations, and writing output files.
- 静态失败原因: The static BERT model correctly predicted non-clone due to low token overlap and clearly distinct semantics.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: The BCB label 1 is likely an annotation error or an overly broad interpretation of 'file processing' tasks.
- 共享行为: Both use file I/O operations.；Both access system properties.；Both contain loops.
- 行为差异: Function A extracts and deploys native libraries; Function B generates HTML pages from XML.；Input/output differ: A reads JAR and writes native libs; B reads XML/config files and writes HTML.；No overlap in core logic or purpose.
- 修正建议: Review BCB annotation for this pair to ensure correct labeling.；Consider refining clone criteria to avoid matching unrelated file-IO functions.

### case_id=818 FP lexical_or_api_overlap

- 方法: `moveFile` vs `main`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Moves a file by copying its contents and deleting the original.
- B 摘要: Main method that generates adapter classes and resources from a Prolog file.
- 静态失败原因: The model might have been misled by common tokens such as 'File', 'IOException', 'read', 'write', and 'close', and failed to capture the vast structural and semantic differences.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clones when functions have entirely different purposes, despite sharing generic file I/O operations.
- 共享行为: Both involve reading and writing files
- 行为差异: moveFile performs simple file copy and deletion；main involves parsing, code generation, serialization, and multiple file operations
- 修正建议: Improve training with more contrastive examples where low token overlap but high API usage similarity are non-clones；Enhance model to focus on high-level program structure rather than local token patterns

### case_id=819 FN benchmark_preference_bias

- 方法: `copyFileChannel` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Copies a file from source to destination using FileChannel, optionally preserving modification time.
- B 摘要: Builds a site for editing by transforming XML pages and writing output files based on given paths and properties.
- 静态失败原因: Static BERT models like GraphCodeBERT rely on lexical overlap and structural similarity. The token Jaccard is very low (0.07), and the methods have different names, parameters, and control flow. The model correctly predicted non-clone; the misclassification is due to the BCB label being 1, which is likely an annotation error.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as a clone if the annotator focused on the shared file I/O pattern or considered both as 'file manipulation' utilities, but the functionality is quite different, so the annotation is likely an error.
- 共享行为: Both involve file I/O operations (reading and writing files).；Both use FileInputStream and FileOutputStream.；Both handle exceptions and clean up resources.
- 行为差异: A is a simple file copy using NIO FileChannel; B is a complex site builder with XML transformation and string processing.；A takes only two files and a boolean; B takes many parameters (paths, properties).；A's output is an exact copy; B's output is transformed and post-processed.；B uses multiple utilities (FileSystem, Gadgets, DebugFile) not present in A.
- 修正建议: Review the BCB annotation for this pair; it should likely be relabeled as non-clone.；Consider filtering or correcting mislabeled pairs in the benchmark.

### case_id=820 FN partial_functionality

- 方法: `getResourceAsStream` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches a resource by name, possibly caching it from a URL, and returns an InputStream.
- B 摘要: Copies a file to a destination file using buffered streams.
- 静态失败原因: Static BERT models rely on token overlap (Jaccard 0.22 low) and may miss the structural similarity of the copy loop due to different method signatures, variable names, and surrounding context.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considers the core stream-copy algorithm as the main functionality, deeming the surrounding differences (network vs file, caching) as secondary, thus labeling them as Type-4 clones.
- 共享行为: Both use BufferedInputStream and BufferedOutputStream to copy data byte-by-byte in a loop.；Both handle IOExceptions and close streams in try-catch-finally fashion.；Both return null on failure.
- 行为差异: Function A involves network resources, HTTP connections, and caching; Function B copies local files.；Function A returns an InputStream; Function B returns a File.；Function A has conditional logic for caching based on last-modified timestamps.
- 修正建议: Train models to recognize common I/O patterns (e.g., read-write loops) across different contexts.；Use graph-based representations to capture control/data flow of stream copying.；Incorporate AST subtree matching for core functionality.

### case_id=821 FN partial_functionality

- 方法: `loadSourceCode` vs `fileDownload`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Loads a source code file from classpath, applies syntax highlighting, and builds an HTML string.
- B 摘要: Downloads a file from a URL and saves it to a local directory with a fixed filename.
- 静态失败原因: Static BERT models may over-rely on lexical overlap and miss the shared URL-reading behavior, leading to false negative.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this as clone due to shared high-level pattern of reading from a URL via streams, despite different functional purposes.
- 共享行为: Both open a URL and read content using streams
- 行为差异: Function A reads text lines and applies syntax highlighting; function B reads bytes and writes to file；Function A reads from class resource; function B reads from any URL；Different output: HTML string vs file download
- 修正建议: Incorporate data flow analysis to capture shared I/O patterns；Use code summarization to identify high-level operations

### case_id=822 FP lexical_or_api_overlap

- 方法: `readTwitterFead` vs `doVersionCheck`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a Twitter timeline from a fixed URL and returns the content as a string.
- B 摘要: Checks for a software update by reading a version file from a configurable URL and displays a message.
- 静态失败原因: The model likely focused on lexical overlap (e.g., 'BufferedReader', 'readLine', 'IOException') and ignored the distinct task semantics.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB considers functions clones only if they are functionally similar; these have different purposes despite similar I/O patterns.
- 共享行为: Both open a URL and read lines using BufferedReader；Both handle IOException
- 行为差异: A returns the content; B is void；A uses HttpClient; B uses URL.openStream；A checks HTTP status code; B does not；B has version comparison and GUI interaction; A does not
- 修正建议: Enhance training with task-specific labels；Use contrastive learning to distinguish functional roles；Incorporate data flow analysis to capture different outputs

### case_id=823 FN benchmark_preference_bias

- 方法: `modifyApplicationMessage` vs `actionPerformed`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Reads a properties file for a given locale, replaces or adds a key-value pair, and writes back.
- B 摘要: Reads a gzipped file of SNP IDs, constructs an HTTP POST request to NCBI with those IDs, and prints the response to stderr.
- 静态失败原因: The static model likely correctly identified the semantic difference and predicted non-clone. The BCB label of 1 may be a misannotation or an overly broad interpretation of Type-3/4 similarity.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have considered both as 'reading a file and processing each line with some output' due to high-level structural similarity, but this is a stretch as the functionalities are fundamentally different.
- 共享行为: Both read input line by line using BufferedReader.；Both use try-catch blocks and print stack traces on exceptions.；Both perform string tokenization and manipulation on each line.
- 行为差异: Function A modifies a local properties file; function B sends data over HTTP to a remote server.；Function A handles missing files and copies default; function B handles gzipped input and URL connections.；Function A writes output to a file; function B writes output to System.err.；The line processing logic is entirely different: one searches for a key to replace; the other extracts IDs to build a query.
- 修正建议: Re-evaluate the BCB label for this pair; likely it should be 0 (non-clone).；If maintaining BCB label, model needs to recognize common boilerplate patterns across different domains.

### case_id=824 FP boilerplate_overlap

- 方法: `run` vs `getFullScreenUrl`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Read a resource from classpath and display its text in a Swing component.
- B 摘要: Parse a YouTube video page to extract parameters and construct a download URL.
- 静态失败原因: The model likely over-relied on overlapping API tokens (URL, BufferedReader, readLine, try-catch) and the presence of a 'run' method (though B is not a Runnable), ignoring the vastly different control flow and final output.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled non-clone because the functions perform entirely different tasks (text display vs. URL extraction) and share only generic I/O boilerplate, not sufficient for even broad Type-4 similarity.
- 共享行为: Both read input stream line by line using BufferedReader；Both handle exceptions with try-catch；Both use URL-related classes
- 行为差异: A reads from classpath resource; B reads from network URL；A appends all lines with line separator; B filters for a specific line；A updates a Swing text component; B constructs and returns a URL string；A uses SwingUtilities.invokeLater; B manipulates a progress bar
- 修正建议: Incorporate dataflow or program dependence graphs to capture high-level purpose；Train on more diverse examples to avoid trivial API-level false positives；Use contrastive learning that emphasizes semantic divergence despite syntactic overlap

### case_id=825 FN benchmark_preference_bias

- 方法: `readAndRewrite` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.2`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Reads a DICOM file and copies it to another file, handling pixel data.
- B 摘要: Handles Eclipse launch configuration for a NexOpen project, modifying Maven POM and Hibernate settings.
- 静态失败原因: Static model correctly predicted non-clone (as per our analysis); the error_type 'FN' suggests BCB considered it clone, so static model did not fail but disagreed with BCB's labeling.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: Despite low token overlap, BCB may have labeled as clone due to both performing sequences of file operations with error handling and logging, treating them as Type-4 (semantically similar) under a very broad interpretation.
- 共享行为: Both use file I/O and stream processing.；Both handle exceptions (IOException/CoreException) and log messages.
- 行为差异: Function A is for DICOM image reprocessing; function B is for Eclipse project build configuration.；A deals with pixel data; B deals with XML POM files and Hibernate properties.；Different libraries and domain objects (DcmParser vs. ILaunchConfiguration).
- 修正建议: Re-evaluate BCB labels for this pair to ensure functional similarity is genuine.；Consider using domain-specific models or larger context to capture semantic differences.；Improve tokenization to handle low Jaccard cases better.

### case_id=826 FP lexical_or_api_overlap

- 方法: `doRawRequest` vs `getUser`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Sends an HTTP POST request with given data and returns the response body as a string.
- B 摘要: Loads a User object from a database or parses a configuration file to create and save a User.
- 静态失败原因: Static BERT/GraphCodeBERT likely overemphasized the overlapping API calls (URL, BufferedReader, InputStreamReader) and basic I/O structure, ignoring the distinct control flow and data semantics.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BigCloneBench labels this non-clone because the functions have entirely different purposes (HTTP client vs user lookup) despite sharing boilerplate I/O code.
- 共享行为: Both use URL and BufferedReader/InputStreamReader to read from a stream.；Both read lines in a loop and append to a buffer.
- 行为差异: A performs network I/O (POST), B performs file I/O and database operations.；A sends data via OutputStreamWriter, B does not.；A returns raw string, B returns a User object.；A throws IOException, B catches exceptions.
- 修正建议: Use data flow analysis to distinguish network vs file I/O patterns.；Incorporate functional role detection (e.g., POST vs read).；Train with contrastive examples that separate boilerplate from core logic.

### case_id=827 FN partial_functionality

- 方法: `loadSourceCode` vs `read`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a source file line by line, applies syntax highlighting, and stores the result as an HTML string.
- B 摘要: Opens a file or URL, reads its contents into a BufferedInputStream, and returns an integer status code.
- 静态失败原因: Static BERT models rely on token overlap and surface-level similarity. The low Jaccard index (0.15) and different method signatures/names likely caused the model to miss the structural similarity in the reading-with-error-handling pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels pairs as clones if they share a common I/O reading pattern with error handling, even if outputs differ. The underlying operation of opening a stream and reading is considered a clone at a Type-3/Type-4 level.
- 共享行为: Both open an InputStream from a resource (file or URL) with exception handling.；Both involve reading from a stream and handling I/O exceptions.
- 行为差异: Function A outputs a formatted HTML string with syntax highlighting; Function B returns a status code and stores stream in a field.；Function A reads line-by-line with BufferedReader; Function B uses BufferedInputStream.；Function A only reads local files from classpath; Function B handles both files and URLs.
- 修正建议: Incorporate AST-based structural similarity to capture common I/O patterns.；Use data flow analysis to identify shared operations like opening streams and handling exceptions.

### case_id=828 FP lexical_or_api_overlap

- 方法: `handleHandshake` vs `retrieveTemplate`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Validates a handshake packet and optionally performs session authentication via HTTP to Minecraft server.
- B 摘要: Fetches a blog template from a URL, caching it for subsequent calls.
- 静态失败原因: The static BERT/GraphCodeBERT model likely focused on lexical and API-level overlap, seeing similar patterns (URL, BufferedReader, InputStream). It may have missed the broader semantic context, such as the validation logic and packet handling in FunctionA vs simple template retrieval in FunctionB.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled non-clone because the overall functionality is completely different: one is a network handshake handler, the other is a template retriever. Despite sharing some I/O boilerplate, the core logic and purpose are distinct.
- 共享行为: Both use URL and BufferedReader/InputStreamReader to read from a URL；Both have exception handling (A catches Exception, B throws Exception)；Both use similar I/O patterns
- 行为差异: FunctionA validates server key and performs session login, while FunctionB simply reads a template；FunctionA has conditional logic based on validation, FunctionB only fetches text；FunctionA interacts with network manager and sends packets, FunctionB caches and returns a string；FunctionA uses parsing and validation; FunctionB does not
- 修正建议: Incorporate more structural analysis to differentiate boilerplate from core functionality；Use flow-sensitive features to capture the different data flows and control structures；Add training examples that distinguish similar API usage with different semantics

### case_id=829 FN partial_functionality

- 方法: `copyResource` vs `encodeFileToFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource (URL or file) to a destination file as raw bytes.
- B 摘要: Reads a file, encodes it to Base64, and writes the encoded data to another file.
- 静态失败原因: The low token Jaccard (0.19697) and significant differences in method signature, source types, and the presence of Base64 encoding likely caused the static model to miss the functional similarity in stream copying behavior.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as 'file copy' operations with similar control flow and stream handling, despite the encoding transformation, so they are labeled as clones under broad Type-4 semantic similarity.
- 共享行为: Both read from an input source and write to an output file.；Both use InputStream and OutputStream and close them in finally block.；Both handle exceptions (though differently).
- 行为差异: Function A copies raw bytes; Function B applies Base64 encoding.；Function A supports URL and local file sources; Function B only local file.；Function A returns void; Function B returns boolean indicating success.；Function A uses byte-by-byte copy; Function B uses buffered chunk copy with a 64KB buffer.
- 修正建议: Augment training data with more pairs that share common stream handling patterns but differ in data transformation (e.g., encoding/decoding).；Incorporate dataflow analysis to capture transformations applied to data streams.；Use contrastive learning to focus on structural/control flow similarity over lexical overlap.

### case_id=830 FP partial_functionality

- 方法: `loadSourceCode` vs `SRWGuiClient`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Loads a source file and highlights its syntax into an HTML string.
- B 摘要: Constructs a Swing browser GUI that reads XML from a URL and optionally applies XSLT transformation to display HTML.
- 静态失败原因: Static BERT or GraphCodeBERT might have focused on structural similarities like try-catch blocks, stream opening, and while loops, ignoring the overall semantic context and different API usages (CodeViewer vs. Transformer).
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB labeled non-clone because the functions have fundamentally different purposes and behavior; only superficial I/O patterns overlap.
- 共享行为: Both open an input stream to read data；Both read lines in a loop；Both build a string result；Both handle exceptions
- 行为差异: One reads a local file, the other reads from a URL；One does syntax highlighting, the other does XSLT transformation and GUI setup；One returns an HTML string stored in a field, the other sets up a browser window；Different class contexts: one is a method in a class, the other a constructor
- 修正建议: Improve handling of long-range dependencies and overall program semantics.；Use more context-aware embeddings that capture method-level purpose.；Incorporate data flow analysis to distinguish different data transformations.

### case_id=831 FN partial_functionality

- 方法: `readGeoParserResult` vs `getURLContent`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a record content, sends it to a geo-parser service via HTTP, parses the XML response to extract place names and gazetteer IDs, with retry logic.
- B 摘要: Opens a URL, reads its text content, and returns it as a string.
- 静态失败原因: The static BERT model focuses on lexical and syntactic similarity; the low token Jaccard (0.135) and large differences in code structure (XML building, parsing, retry loops) led it to predict non-clone, missing the underlying shared pattern of URL reading.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as functions that 'get content from a URL' at a high level, ignoring additional processing like XML parsing, thus accepting partial functionality similarity as a Type-4 clone.
- 共享行为: Both open a URL and read lines from the response using BufferedReader into a StringBuilder
- 行为差异: A constructs an XML request and parses XML response; B simply returns raw text；A has retry and error handling; B throws IOException；A returns a collection of tuples; B returns a single string
- 修正建议: Use dataflow-aware models to capture common sub-tasks across different implementations；Augment training data with examples of functions that have embedded URL reading functionality

### case_id=832 FN partial_functionality

- 方法: `sendExceptionToServer` vs `getHTML`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends exception details as a POST request to a server and prints the server response.
- B 摘要: Retrieves HTML content from a URL via HTTP GET and optionally writes it to a file.
- 静态失败原因: Static BERT/GraphCodeBERT likely relied on token-level similarity (low Jaccard) and method signatures, missing the structural overlap of the HTTP I/O pattern. The models are weak at capturing abstract control flow or partial functional similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label these as Type-3/Type-4 clones because they share a common structural pattern: opening a URL, reading lines with BufferedReader, handling exceptions, and resource cleanup. Despite different specific functionality, the high-level I/O template is similar.
- 共享行为: Both open a URL connection；Both read from an InputStream line by line using BufferedReader；Both use try-catch for exception handling；Both involve I/O operations with URLs
- 行为差异: A sends data (POST) while B receives data (GET)；A encodes multiple parameters in the request body; B does not；A writes to output stream; B reads from input stream；A prints the server response; B returns the HTML string and optionally writes to file
- 修正建议: Incorporate AST-based features to capture structural similarity beyond token overlap；Use data flow analysis to identify common I/O patterns；Augment training data with more examples of functionally different but structurally similar clones

### case_id=833 FP boilerplate_overlap

- 方法: `handler` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Extracts substring values from a URL's content for each entry in a map based on include, from, and to strings.
- B 摘要: Performs a Google image search for the current track's artist and album, extracting image URLs from the HTML response.
- 静态失败原因: The model may have been misled by the high structural similarity in the boilerplate code for URL opening and reading (BufferedReader, while loop, try-catch) and overlooked the completely different core logic (map update vs. URL extraction).
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled this as non-clone because the two functions serve distinct purposes: one is a generic URL content parser for parameter extraction, the other is a specialized image search; they do not share enough functional similarity to be considered a Type-3 or Type-4 clone.
- 共享行为: Both open a URL and read its content using BufferedReader and InputStreamReader.；Both handle IOException (or Exception) with try-catch blocks.
- 行为差异: Function A processes each line individually and updates a map, while Function B concatenates all lines and splits the entire text to extract URLs.；Function A uses a target object to specify parameters, while Function B uses predefined instance variables for search query.；Function A extracts substrings based on specific delimiters (fromStr, toStr), while Function B extracts URLs from HTML split by a pattern.；Function A modifies an input map, Function B populates a list field.
- 修正建议: Train models to distinguish between boilerplate and core functionality.；Incorporate data flow analysis to trace how variables are used and modified.；Use contrastive learning to emphasize semantic differences over syntactic similarities.

### case_id=834 FN partial_functionality

- 方法: `main` vs `save`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a URL, unzips it, and extracts each entry to a file.
- B 摘要: Saves a byte array to a file using Apache Commons IO utility methods.
- 静态失败原因: Static BERT/GraphCodeBERT likely focused on the overlapping I/O-related tokens and ignored the structural and semantic differences in the overall workflow, causing false negative.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this as clone due to both being file-saving operations, but the differences in input source (ZIP archive vs byte array) and overall logic make it a borderline Type-4 at best.
- 共享行为: Both read from an InputStream and write to an OutputStream to produce a file.；Both handle file I/O and stream closing.
- 行为差异: Code A processes a ZIP archive from a URL, while Code B writes a raw byte array.；Code A is a void main method with hardcoded URL, Code B is a reusable save method returning byte count.；Code A manually buffers and writes, Code B uses IOUtils.copy.；Code A prints extracted entries, Code B does not.
- 修正建议: Improve models to distinguish between file generation from archives vs raw bytes.；Enhance training with more diverse partial-functional similarity examples.

### case_id=835 FN partial_functionality

- 方法: `getHTML` vs `handler`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches an HTML page from a URL and optionally saves it to a file.
- B 摘要: Reads a URL and extracts specific substrings from lines to update a map.
- 静态失败原因: The model likely over-weighted the structural overlap (URL opening, BufferedReader, line-by-line loop) but failed to capture the significantly different operations on the lines (simple concatenation vs. pattern-based extraction), leading to a false negative.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as web content retrieval and processing functions, where the common pattern of opening a URL and iterating lines constitutes a similar functionality, especially in a broad web scraping context.
- 共享行为: Open a URL and read its content line by line using BufferedReader；Use while loop with readLine() to process lines；Required IO exception handling
- 行为差异: Function A returns entire HTML content as string; B updates a map with extracted substrings；A uses HttpURLConnection with User-Agent; B uses URL.openStream()；A optionally writes to file; B performs substring extraction based on target parameters；Error handling: A prints stack trace; B silently catches exceptions
- 修正建议: Train with more examples that distinguish generic reading from specific processing；Incorporate dataflow information to capture output differences；Use contrastive learning to emphasize functional purpose over syntactic similarity

### case_id=836 FP partial_functionality

- 方法: `readRemoteFile` vs `getFullScreenUrl`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a remote file line by line and returns its entire content as a string.
- B 摘要: Fetches a YouTube page, extracts the fullscreen URL by parsing a specific line, and returns the constructed video URL.
- 静态失败原因: Static BERT models may overestimate similarity due to shared API calls and reading loop, ignoring the distinct post-processing logic.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB labels non-clones for functionally different code; here the purpose and output differ significantly despite similar boilerplate.
- 共享行为: Both read from a URL using BufferedReader
- 行为差异: Different final output: full file content vs extracted URL；Different error handling: readRemoteFile catches EOFException and IOException, getFullScreenUrl catches generic Exception
- 修正建议: Use dataflow analysis to track how the read data is transformed；Incorporate AST or control-flow features to distinguish different conditional and loop structures

### case_id=837 FN benchmark_preference_bias

- 方法: `send` vs `modifyApplicationMessage`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Sends an email with various headers, attachments, and priority using JavaMail.
- B 摘要: Modifies a value in a locale-specific properties file by key, adding if not found.
- 静态失败原因: Static BERT models rely on token and structural similarity, which is low here (Jaccard 0.107). The model likely focused on generic patterns (try-catch, method signatures) and missed the entirely different semantics.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled these as clones due to broad Type-4 criteria such as both performing I/O operations and having similar exception handling structures, but this is a stretch.
- 共享行为: Both use try-catch-finally exception handling；Both involve reading/writing data (email vs file)
- 行为差异: A constructs and sends an email via SMTP; B modifies a properties file on disk；A uses JavaMail API (MimeMessage, HtmlEmail); B uses file I/O and Properties；A handles multiple recipients, attachments, and HTML; B handles a single key-value pair；A spawns a thread to send; B writes synchronously
- 修正建议: Train with more diverse negative examples to avoid overgeneralizing exception handling patterns；Incorporate domain-specific knowledge or API usage embeddings；Use data-flow or call-graph features to distinguish different operation domains

### case_id=838 FP boilerplate_overlap

- 方法: `readUNI` vs `getTicketsForQueue`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a tab-separated file from a URL and populates a vector with id and description.
- B 摘要: Fetches open tickets for a queue from a REST API and returns a list of ticket objects.
- 静态失败原因: Static embedding (e.g., codebert) may focus on overlapping lexical tokens (e.g., 'line', 'InputStream', 'try', 'catch', 'finally') and structural patterns (I/O loop), missing the distinct functional intent due to insufficient understanding of method-level semantics and dependencies.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely marked this as non-clone because the methods implement entirely different business logic (generic file parsing vs. specific ticket retrieval API interaction) despite some low-level I/O boilerplate.
- 共享行为: Both open an input stream from a URL/HTTP response.；Both read lines of text in a loop.；Both parse each line to extract fields.；Both handle exceptions (catch/finally) and close streams.
- 行为差异: readUNI parses tab-delimited lines; getTicketsForQueue parses lines starting with 'ticket/'.；readUNI adds parsed data to an external Vector; getTicketsForQueue builds an internal list and returns it.；getTicketsForQueue constructs HTTP request and calls getTicket for each ID; readUNI does not perform further API calls.；getTicketsForQueue has complex error handling (throws custom exception); readUNI silently catches exceptions.
- 修正建议: Incorporate data flow analysis to distinguish core logic from boilerplate.；Use graph-based models that capture method call dependencies (e.g., getTicket) and type information.；Train with contrastive objectives that penalize similarity based only on I/O patterns.；Leverage program slicing to focus on semantic units.

### case_id=839 FP boilerplate_overlap

- 方法: `readReferenceText` vs `getVersion`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a text file from a plugin bundle for a given identifier and returns its entire content as a string, or throws NoContentException on error.
- B 摘要: Fetches a version string from a hardcoded URL and returns the first line read, or null on exception.
- 静态失败原因: The model likely over-relied on lexical overlap (e.g., URL, BufferedReader, InputStreamReader, readLine) and similar try-catch control flow, failing to capture the differences in input/output behavior and exception handling.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled this as non-clone because the functions serve different purposes (generic reader vs. version fetcher), have different method signatures, and different error handling semantics, despite sharing URL reading boilerplate.
- 共享行为: Both open a URL connection and read from it using BufferedReader.；Both handle IOExceptions within try-catch blocks.；Both return a String value representing the read content.
- 行为差异: Function A takes an identifier parameter to construct the URL; B uses a hardcoded URL.；Function A concatenates all lines with newline; B only captures the last line read.；Function A throws a custom NoContentException; B returns null on failure.；Function A logs errors; B ignores exceptions silently.
- 修正建议: Include dataflow analysis to track how inputs and outputs differ.；Consider method signature and exception handling patterns.；Use fine-tuned models on functional semantics rather than token overlap.

### case_id=840 FP lexical_or_api_overlap

- 方法: `scrapeForIsbns` vs `downloadFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Scrapes ISBN-10 codes from a web page's HTML, retrying on connection failures.
- B 摘要: Downloads a file from a URL to a local file, reporting progress.
- 静态失败原因: The model may have been misled by overlapping API calls (URL.openStream, BufferedReader) and similar loop structures, focusing on surface-level I/O patterns rather than overall semantics.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled non-clone because the functions have distinct goals and logic, despite both using URL streams; they are not functionally similar.
- 共享行为: Both open a URL connection and read from an input stream.
- 行为差异: Different purposes: ISBN extraction vs file download.；Different output: count of matches vs boolean success.；Different data handling: regex text parsing vs binary write to file.；Different error handling: retries with sleep vs throwing exceptions.
- 修正建议: Incorporate dataflow or control-flow analysis to distinguish extraction vs download.；Use method name and return type as additional signals.；Improve training data with more diverse non-clone pairs sharing API usage.

### case_id=841 FN partial_functionality

- 方法: `addDataFromURL` vs `httpRequestByPOST`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads data from a URL line by line and appends with newlines to a text field, printing errors to stdout.
- B 摘要: Performs an HTTP POST request, reads the response line by line, and returns the concatenated string, with error handling via status codes and exceptions.
- 静态失败原因: Static BERT/GraphCodeBERT models rely on token and structure overlap, which is low (Jaccard 0.219). They may miss the high-level semantic similarity of network line-reading due to different APIs (URL.openStream vs HttpClient) and control flow structures.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels clones based on partial functional similarity, especially common patterns like reading from a network stream line by line, despite differing HTTP methods, error handling, and return mechanisms.
- 共享行为: Both open a network connection to a URL；Both read lines using BufferedReader；Both handle exceptions during I/O
- 行为差异: Function A uses a simple GET via URL.openStream(); B uses Apache HttpClient POST with parameters；Function A appends lines with a newline separator; B concatenates without newlines；Function A returns void and stores in a field; B returns a String or null；Function A catches general Exception; B catches IOException and checks HTTP status codes
- 修正建议: Incorporate data-flow analysis to recognize common I/O patterns；Use contrastive learning on pairs with similar I/O semantics but different API implementations；Augment training data with broad Type-3/Type-4 clones that share partial functionality

### case_id=842 FN benchmark_preference_bias

- 方法: `doGet` vs `encodeFileToFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Handles HTTP GET requests by retrieving a page, checking permissions, rendering HTML, and optionally caching the output to a file.
- B 摘要: Reads a file, Base64-encodes its contents, and writes the encoded data to another file.
- 静态失败原因: The model correctly identified the low token overlap (0.083) and distinct method names/functionality, predicting non-clone. It failed to align with the erroneous BCB label, which may be an outlier or annotation error.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled these as clones due to both performing file I/O operations and using exception handling patterns, but this is a very broad interpretation and likely a mislabel in the dataset.
- 共享行为: Both involve reading and writing data using streams；Both use try-catch-finally for exception handling；Both close streams in finally blocks
- 行为差异: One is an HTTP servlet handler, the other is a file encoding utility；One handles user authentication and page visibility, the other does not；One writes to an HTTP response, the other writes to a file output stream；One uses Base64 encoding, the other does not
- 修正建议: Improve dataset quality by reviewing and correcting potentially mislabeled pairs；Train models to be robust to label noise, but in this case the model's prediction is semantically sound

### case_id=843 FP boilerplate_overlap

- 方法: `setMembers` vs `downloadModel`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Parse HTML from a Trac ticket page to extract component and priority dropdown options into static arrays.
- B 摘要: Download an RDF model from a given URL and return it as a Jena Model object.
- 静态失败原因: Model overemphasized lexical overlap in error handling (both catch MalformedURLException and IOException) and URL opening patterns, despite low token Jaccard. Boilerplate code misled the classifier.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels as non-clone because core functionality differs entirely: extracting HTML options vs. downloading RDF model. Shared I/O boilerplate is insufficient for Type-3/4 similarity.
- 共享行为: Open a URL connection and read input；Handle MalformedURLException and IOException
- 行为差异: A is void and populates class fields; B returns a Model；A parses HTML using regex; B reads RDF data using model.read；A uses BufferedReader and lines; B uses InputStream；A prints error messages; B logs and throws RuntimeException
- 修正建议: Use dataflow analysis to distinguish core logic (parsing vs. model reading)；Incorporate API-specific patterns (HTML select elements vs. RDF model.read)；Downweight common try-catch and URL connection patterns

### case_id=844 FP lexical_or_api_overlap

- 方法: `doRawRequest` vs `executePost`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Sends POST data to a fixed URL and returns response as string without any error handling.
- B 摘要: Sends POST data to a parameterized URL with headers and error handling, returning response with carriage returns or null on failure.
- 静态失败原因: The model likely focused on shared boilerplate code (URL opening, reading with BufferedReader, writing with OutputStreamWriter) and similar control flow, missing the semantic differences in error handling, headers, and output formatting.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels these as non-clones because they differ in method signature, error handling, output format, and configurability, which are considered significant behavioral differences.
- 共享行为: Both send HTTP POST-like requests and read the response line by line.
- 行为差异: Function A uses a fixed URL, while B uses a parameterized URL.；Function A lacks HTTP method setting and headers; B sets POST method and headers.；Function B has error handling and returns null on exception; A does not.；Function B appends carriage returns to response lines; A does not.
- 修正建议: Incorporate analysis of method signatures and error handling patterns.；Distinguish between parameterized and fixed URLs.；Consider differences in output format (e.g., carriage returns).

### case_id=845 FN lexical_or_api_overlap

- 方法: `main` vs `import_hints`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.4`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Builds and sends a POST request to RenRen API with encoded parameters and prints the response.
- B 摘要: Reads hints data from a file or URL and places puzzle pieces on a board with given parameters.
- 静态失败原因: Static models like CodeBERT rely on token overlap and structural similarity, which are low (Jaccard=0.13) and differ in method signatures, variable names, and control flow, causing it to miss the abstract I/O and boilerplate similarity that BCB annotators deem sufficient.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may consider both as 'top-level' methods that perform I/O and data processing with similar boilerplate (URL, BufferedReader, IOException), thus labeling them as a broad Type-4 clone based on abstract functionality.
- 共享行为: Both use URL and BufferedReader for network or file I/O；Both handle IOException with try-catch；Both parse or iterate over input data
- 行为差异: Function A sends a POST request and reads the response; function B only reads data from a URL or file；Function A constructs multiple PostParameter objects; function B tokenizes lines of integers；Function A focuses on API interaction; function B focuses on game state mutation；Function A has no return value; function B returns a boolean
- 修正建议: Incorporate higher-level semantic features such as API usage patterns and data flow；Use larger context or hierarchical embeddings to capture abstract functionality；Combine lexical matching with dependency parsing for I/O operation patterns

### case_id=846 FP boilerplate_overlap

- 方法: `doVersionCheck` vs `SRWGuiClient`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Static method that checks for a new version of jEdit by fetching a remote version file and comparing build numbers.
- B 摘要: Constructor for a Swing browser GUI that loads a URL, optionally applies XSLT transformation, and displays the content in a JEditorPane.
- 静态失败原因: The model likely focused on lexical and API-level overlap (URL, BufferedReader, InputStreamReader, IOException) common in many network I/O tasks, ignoring the divergent core functionality.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the functions have entirely different purposes and logic. Even with broad Type-3/Type-4 criteria, the high-level intent is disparate.
- 共享行为: Both read from a URL using BufferedReader and InputStreamReader
- 行为差异: Code A is a static utility for version checking; Code B is a constructor for a GUI browser.；Code A only reads version/build info; Code B reads XML/HTML and may transform it.；Code A displays dialogs; Code B sets up a complex GUI layout.；Code A has no GUI elements; Code B extensively uses Swing components.
- 修正建议: Train with more negative examples that share common I/O patterns but have different semantics.；Incorporate structural or dataflow features to distinguish high-level tasks.

### case_id=847 FN benchmark_preference_bias

- 方法: `createNew` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Creates a new resource by writing an input stream to a file, checking ownership and specific filenames.
- B 摘要: Launches a configuration by validating project structure, processing XML files, and scheduling a project installation job.
- 静态失败原因: The static model correctly predicted non-clone based on low lexical overlap and distinct semantics, but this is a false negative relative to BCB's label, indicating the model failed to align with BCB's (potentially erroneous) annotation.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled these as clones due to both involving IOUtils.copy and conditional structures, but the overall functional purpose is entirely different, suggesting a possible annotation error or overly broad interpretation of type-4 similarity.
- 共享行为: Both use IOUtils.copy to copy input streams to output streams.；Both include conditional checks before main operations.；Both utilize logging for error or info messages.
- 行为差异: A returns a Resource object; B returns void.；A focuses on file I/O for resource creation; B focuses on Eclipse launch configuration with XML parsing and project scheduling.；A checks ownership and file names; B checks project type and existence of specific pom files.；B involves handling of external files and properties; A does not.
- 修正建议: Review and refine BCB annotations to ensure clones have meaningful semantic similarity beyond trivial utility usage.；Use more rigorous criteria for labeling type-4 clones to avoid false positives.

### case_id=848 FN long_range_semantics

- 方法: `sendRequest` vs `seeURLConnection`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.6`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends an XML request via HTTP, compresses output, and reads compressed XML response, returning an empty string.
- B 摘要: Performs a simple HTTP GET request, reads the response line by line, and logs the content.
- 静态失败原因: Static BERT relies heavily on token overlap and surface syntax, which are low (Jaccard 0.122). It failed to recognize the high-level semantic similarity in HTTP connection and reading behavior due to limited representation of API call chains and program flow.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may have focused on the common URLConnection usage and considered both as HTTP communication functions, accepting broad Type-4 similarity despite significant differences in input/output and detail.
- 共享行为: both open an HTTP URLConnection；both read the input stream from the connection
- 行为差异: sendRequest writes XML data with compression and checksum; seeURLConnection does not write；sendRequest parses XML with JDOM; seeURLConnection reads plain text；sendRequest uses dynamic URL from preferences; seeURLConnection uses hardcoded URL；sendRequest has error handling with dialog; seeURLConnection throws exception
- 修正建议: Train models with data flow graphs to capture API interaction patterns；Use contrastive learning on Type-4 clone pairs to improve semantic understanding；Incorporate AST-based features that abstract over variable names and literals

### case_id=849 FP lexical_or_api_overlap

- 方法: `testStandardTee` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Tests copying a string through a TeeWriter to two StringReaders and verifying content and byte count.
- B 摘要: Handles action events for a settings dialog, processing commands like GRAPHVIZ, IMAGEMAGICK, etc., showing file choosers, and updating preferences.
- 静态失败原因: Despite low token overlap, the model may have been misled by common Java constructs (e.g., 'String', 'final', 'new') or boilerplate patterns, failing to capture the overall semantic difference between a simple test and a complex GUI event handler.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled non-clone due to completely different functionality, structure, and low token overlap, which aligns with the strict non-clone definition.
- 共享行为: None
- 行为差异: A is a unit test; B is an event handler.；A uses IOUtils.copy with StringReader and StringWriter; B uses JFileChooser and file I/O.；A has no control flow beyond a single copy; B has multiple command branches and UI updates.；A has no exception handling; B has try-catch blocks.
- 修正建议: Increase context window or use hierarchical models.；Incorporate control flow and data flow analysis.；Train on more diverse examples with explicit non-clone pairs.

### case_id=850 FP boilerplate_overlap

- 方法: `readData` vs `copyFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Reads configuration data from string tokens and a file, populating various hash sets and maps for a Tibetan transliteration system.
- B 摘要: Copies a file from source to destination using buffered byte streams.
- 静态失败原因: GraphCodeBERT may have been misled by the shared use of file I/O classes (FileInputStream, IOException) and basic try-catch structure, treating these as evidence of similarity while ignoring the vastly different logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would label this as non-clone because the functions have entirely different purposes and no meaningful functional overlap; the low token Jaccard (0.068) supports this.
- 行为差异: Function A parses and processes text data, building multiple data structures; function B performs a straightforward file copy.；A involves reading and interpreting many string tokens; B only reads and writes raw bytes.；A has complex conditional logic for parsing different columns; B has none.；A updates several static collections; B has no side effects beyond the file copy.
- 修正建议: Train the model to distinguish between shared infrastructure (like file I/O) and actual functional behavior.；Incorporate data-flow analysis to separate reading/writing of raw bytes from text parsing and set insertion.；Use contrastive learning examples where functions share low-level APIs but differ semantically.

### case_id=851 FN lexical_or_api_overlap

- 方法: `getFile` vs `copyTextFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a given URL, optionally modifies the endpoint address in the WSDL, and returns the local file path.
- B 摘要: Copies a source text file to a destination file using buffered streams and returns a boolean indicating success.
- 静态失败原因: Low token overlap (Jaccard=0.116) and distinct domain-specific vocabulary (e.g., 'WSDL', 'URL', 'XML' vs 'BufferedInputStream', 'File') cause embedding dissimilarity; the model misses the abstract file I/O behavior.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may consider these Type-4 clones because both are file manipulation utilities that read from a source and write to a destination, sharing a common high-level I/O pattern despite different specific tasks.
- 共享行为: Both perform file I/O operations, including opening input and output streams.；Both handle exceptions with try-catch blocks.；Both involve transferring data from a source to a destination.
- 行为差异: getFile downloads from a network URL and processes XML, while copyTextFile copies a local file bytewise.；getFile performs XML parsing and attribute modification, copyTextFile does not.；getFile returns a file path string, copyTextFile returns a boolean.；getFile uses NIO channels and URL connections, copyTextFile uses buffered streams.
- 修正建议: Incorporate data-flow or control-flow graphs to capture structural I/O patterns.；Use code summarization or AST-based pretraining to recognize high-level operations like file copying.；Augment training with more diverse file I/O examples to bridge domain-specific gaps.

### case_id=852 FN partial_functionality

- 方法: `copyResource` vs `encodeFileToFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copy a resource (URL or file) to a destination file without transformation.
- B 摘要: Base64-encode a file and write to an output file, returning success status.
- 静态失败原因: Static BERT models rely on token overlap and surface-level patterns; low Jaccard similarity (0.19697) and differing method names/calls lead to low similarity score; the models may miss the underlying I/O structure shared across the functions.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as file copy/transform utilities with similar structure (input->while->output->close) even though one adds encoding, accepting Type-4 partial functionality similarity.
- 共享行为: Both use input stream to read bytes and output stream to write bytes.；Both have a while loop that reads and writes bytes.；Both close input and output streams after operation.
- 行为差异: Function A reads from a URL or file source; function B only reads from a file.；Function A copies raw bytes; function B performs Base64 encoding during reading.；Function A throws an exception on failure; function B returns a boolean and prints stack trace.；Function A reads one byte at a time; function B reads into a buffer of 65536 bytes.
- 修正建议: Incorporate structural similarity of the common I/O loop pattern.；Use data flow analysis to recognize that both involve reading and writing byte streams.；Consider abstract representations that capture high-level operations like 'copy' or 'transform'.；Train on broad Type-3/Type-4 clones to recognize partial functional similarity.

### case_id=853 FP lexical_or_api_overlap

- 方法: `get` vs `readReferenceText`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches game records via HTTP GET with custom headers and filters lines starting with '#'.
- B 摘要: Reads reference text from a plugin bundle resource file and returns it as a string.
- 静态失败原因: The static BERT/GraphCodeBERT model likely overfitted on the common code pattern of opening a stream, reading lines, and catching exceptions. It may have missed the semantic differences in the data processing logic and return types, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels these as non-clones because they serve entirely different purposes: A is a network service client for game records, B is a local file reader for plugin reference text. The superficial structural similarity (BufferedReader loop) is not enough for true clone relationship in BCB's view, which requires some degree of functional or behavioral overlap.
- 共享行为: Open a URL or stream；Use BufferedReader to read lines；Handle IOExceptions
- 行为差异: A uses HTTP connection with custom headers; B reads local resource；A returns array of GameRecord; B returns String；A filters lines with '#'; B does not；A returns null on failure; B throws NoContentException
- 修正建议: Improve model to capture context beyond local token sequences, e.g., using data flow or control flow analysis；Add negative examples with high lexical overlap but different functionality；Incorporate API call semantics and domain knowledge

### case_id=854 FN boilerplate_overlap

- 方法: `copyResource` vs `downLoadZippedFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource from a URL or local file to a destination file byte-by-byte.
- B 摘要: Downloads a zipped file from a URL, unzips it to a destination directory, and returns the URL of the extracted directory.
- 静态失败原因: Static models like BERT may be misled by the overlapping tokens (URL, InputStream, FileOutputStream, close) and structural similarities (try-finally, stream management) while missing the critical semantic differences (unzip, return value, temporary file).
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely labeled as clone due to the shared boilerplate pattern of opening a URL connection, reading an input stream, and writing to a file output stream, emphasizing the common streaming behavior over the distinct post-processing logic.
- 共享行为: Both read from a URL and write to a file output stream.
- 行为差异: Function A copies arbitrary resources; function B specifically downloads and extracts a zip file.；Function A uses byte-by-byte copying; function B uses IOUtils.copy.；Function B creates a temporary file, unzips it, deletes the temp file, and returns a URL; Function A does not.；Function B includes exception handling with finally blocks; Function A has simpler error handling.
- 修正建议: Incorporate domain knowledge about common operations like unzip.；Use control-flow analysis to differentiate the post-processing steps.；Enhance training data with examples that distinguish copy from download-and-extract patterns.

### case_id=855 FN boilerplate_overlap

- 方法: `sendExceptionToServer` vs `loadExistingAntlibs`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends exception details to a server via HTTP POST with URL-encoded parameters.
- B 摘要: Loads Ant library definitions from classpath resources by reading URLs and processing lines.
- 静态失败原因: Static BERT/GraphCodeBERT models often rely on token-level similarities and high-level semantic embeddings. The low token Jaccard (0.178862) and different domain vocabularies (server vs. antlibs) caused the model to miss the underlying I/O structural pattern, which BCB considers clone-worthy.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may consider these as Type-3 clones due to the strong structural overlap in network I/O boilerplate: opening a URL, reading/writing lines via BufferedReader, and closing resources. The core control flow and resource handling pattern is similar despite different business logic.
- 共享行为: Both open a URL or URLConnection and read from an InputStream using BufferedReader；Both use a while loop to read lines from the input stream；Both handle IOException and close streams；Both utilize URL encoding for data transmission (A encodes parameters, B uses UTF-8 encoding for reader)
- 行为差异: A sends data via HTTP POST (writes to output stream), B only reads data from input stream；A constructs a query string with multiple parameters, B reads resource filenames from lines；A sends the data to a server and processes a response, B loads antlib resources using a classLoader；A uses URLConnection with doOutput=true, B uses URL.openStream() directly
- 修正建议: Incorporate structural features like control flow graphs or data flow patterns to detect similar I/O skeletons；Use API-level abstraction to recognize common resource handling patterns (URL, InputStream, BufferedReader)；Enhance token embedding with positional encoding to better capture repeated patterns like readLine loops

### case_id=856 FP lexical_or_api_overlap

- 方法: `setMembers` vs `executePost`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Parses HTML from a Trac URL to extract options for components and priorities into class-level arrays.
- B 摘要: Sends an HTTP POST request to a given URL with parameters and returns the response body.
- 静态失败原因: The model may have been misled by overlapping API elements (URL, BufferedReader, InputStreamReader) and similar exception handling structure. Despite low token Jaccard (0.136), these common subpatterns can trigger false positives.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically treats clones as functionally similar code, even if syntactically different. Here, the functions share only generic networking patterns, but their core tasks (HTML parsing vs HTTP POST) are unrelated. Thus BCB would not consider them clones.
- 共享行为: Both use URL and open HTTP connections.；Both read from input streams using BufferedReader.；Both handle exceptions with try-catch blocks.
- 行为差异: Function A performs a GET request to fetch a page; function B performs a POST request to submit data.；Function A parses HTML to extract select options; function B writes request parameters and reads the response.；Function A modifies class-level state (m_strComponents, m_strPriorities); function B returns a string.；Function A uses regex to parse HTML; function B does not parse HTML.
- 修正建议: Incorporate dataflow analysis to distinguish between methods that set class variables vs those that return values.；Add detection of HTTP method (GET vs POST) as a distinguishing feature.；Use abstract syntax tree (AST) differences to capture divergent control flow patterns.

### case_id=857 FN partial_functionality

- 方法: `httpRequestByPOST` vs `GetResponse`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.95`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends an HTTP POST request with parameters and returns the response body as a string, handling errors by setting error fields and returning null.
- B 摘要: Sends an HTTP GET request to a URL and returns the response body as a string, returning null on failure but without meaningful error handling.
- 静态失败原因: Static BERT models rely on token-level patterns and may miss functional similarity when lexical overlap is low (Jaccard = 0.217) and libraries/method signatures differ. The model likely focused on the different HTTP client usage and method names rather than the semantic goal.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB annotations often treat functions with the same high-level intent (e.g., 'get HTTP response as string') as clones even if the implementation details differ (Type-3/Type-4). The differences in HTTP method and error handling are considered secondary to the core purpose.
- 共享行为: Both perform an HTTP request and read the response line by line；Both return the response body as a string or null on failure；Both use standard Java networking libraries
- 行为差异: HTTP method: POST vs GET；Library: Apache HttpClient vs java.net.HttpURLConnection；Error handling: A sets error fields and handles status codes < 400; B has minimal error handling (calls getStackTrace())；Parameter handling: A takes a list of NameValuePair; B uses URL only
- 修正建议: Incorporate graph-based representations (e.g., AST, CFG) to capture control and data flow；Use contrastive learning or functional fine-tuning to align embeddings of methods with similar intent；Increase training data with more diverse implementations of the same functionality

### case_id=858 FN partial_functionality

- 方法: `main` vs `extractZipFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Extracts a ZIP file from a URL to the current directory, printing extracted entry names to stdout.
- B 摘要: Extracts a local ZIP file to a specified destination, creating directories as needed and updating a JTextPane with progress.
- 静态失败原因: Static BERT models rely on token similarity and structural overlap; low token Jaccard (0.253) and differences in API calls (URL vs FileInputStream), variable names, and added features (directory handling, progress) caused the model to miss the shared extraction logic.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels Type-4 clones as 1 if they share core functionality and significant code structure despite minor syntactic differences. Both functions perform ZIP extraction with similar loop logic, making them functionally similar.
- 共享行为: Both use ZipInputStream to iterate over ZIP entries；Both read and write entry data using a byte buffer；Both extract non-directory entries to files
- 行为差异: Input source: URL (HTTP or file) vs. local file path；Directory handling: none (A) vs. creates directories (B)；Progress reporting: stdout (A) vs. JTextPane (B)；Buffer size: BUFFER constant vs. 1024
- 修正建议: Incorporate dataflow or control-flow abstraction to capture shared functional patterns；Augment training data with more diverse Type-3 and Type-4 clones；Use contrastive learning to emphasize functional similarity over surface syntax

### case_id=859 FP boilerplate_overlap

- 方法: `getDatasetsList` vs `downloadModel`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Synchronized method that retrieves a list of dataset names from a remote server via HTTP, caching results per URL.
- B 摘要: Static method that downloads an RDF model from a remote URL, setting HTTP headers for content negotiation.
- 静态失败原因: The static model over-relied on the common pattern of URL opening, exception handling, and I/O processing. It likely ignored the semantic details of what is being read and returned, treating the structural boilerplate as indicative of a clone. The model's attention may have been drawn to similar keywords (URL, reader, IOException, RuntimeException) while missing the divergent caching, headers, and return type logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels as non-clone because the two functions serve fundamentally different purposes (list retrieval vs model download) with distinct return types and business logic. The shared URL-opening and exception-handling boilerplate is insufficient to deem them functionally similar under BCB's guidelines, which require more than superficial structural overlap.
- 共享行为: Both open an HTTP connection to a given URL and read input from the stream.；Both catch IO exceptions and rethrow as RuntimeException with logging.；Both involve network I/O and return a value based on the data read.
- 行为差异: Function A caches results in a HashMap; B does not cache.；A reads lines into a list of strings; B reads RDF data into a Model object.；A appends query parameter '?server=list' to URL; B sets Accept and Accept-Language headers.；A is synchronized instance method; B is static method.
- 修正建议: Incorporate dataflow analysis to track how the input stream is processed (e.g., line-by-line vs RDF parsing).；Use method name and return type as additional features to distinguish purpose.；Train on examples where boilerplate code appears in non-clone pairs to reduce false positives.；Add attention to method-level semantics beyond token overlap.

### case_id=860 FN benchmark_preference_bias

- 方法: `decodeFileToFile` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Decodes a Base64-encoded input file and writes the decoded bytes to an output file.
- B 摘要: Builds a site for editing by reading XML pages, transforming them, and writing output files with string replacements.
- 静态失败原因: The static BERT model likely failed because of low lexical overlap (token Jaccard 0.0667) and because it did not capture the high-level semantic similarity of file-to-file transformation with buffered I/O; the model may have been misled by the highly different method names and contexts.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider these clones because both implement a file-to-file copy with a transformation step (Base64 decode vs. XSLT/string replacement) using buffered I/O, which fits Type-4 semantic similarity at a high level of abstraction.
- 共享行为: Both functions read from an input file and write to an output file using buffered streams.；Both handle IOExceptions and close streams in finally blocks.
- 行为差异: Function A only decodes Base64, whereas Function B performs complex page transformation and string replacement.；Function A uses a fixed buffer size of 65536, while Function B reads characters with a char array of 8192 and does XSLT transformations.；Function B has many parameters and additional logic for debugging, container checking, and error handling.
- 修正建议: Improve model sensitivity to common I/O patterns even with different application logic.；Use data-flow analysis to detect similar stream operations.；Incorporate more examples of Type-4 clones with low lexical overlap.

### case_id=861 FN boilerplate_overlap

- 方法: `doTransfer` vs `read`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.3`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Proxies an HTTP request to a target URL, copying headers and body, then returning the response.
- B 摘要: Reads a properties skeleton file from the classpath and splits it into sections based on '---' separators.
- 静态失败原因: Static BERT models rely on token overlap and syntactic similarity, which are low (Jaccard=0.12). They fail to capture the broad I/O pattern similarity that BCB might consider.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may have tagged these as clones due to both involving reading from a URL-based input stream, using while loops, and handling IO exceptions, despite vastly different overall functionality.
- 共享行为: Both open a URL to obtain an input stream；Both use while loops to read from a stream；Both handle IO exceptions；Both use URL objects
- 行为差异: Function A acts as an HTTP proxy, transferring full request/response data; Function B parses a file into sections；A uses HttpServletRequest/Response, B uses ClassLoader and BufferedReader；A performs network I/O, B performs file I/O；A modifies request properties, B does not
- 修正建议: Incorporate dataflow analysis to distinguish actual data processing logic from boilerplate I/O；Use AST-based differencing to identify structural similarities beyond tokens；Include task-level intent classification to differentiate proxy vs. parsing

### case_id=862 FN partial_functionality

- 方法: `copyFile` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a file from one path to another using NIO FileChannel.
- B 摘要: Downloads a KMZ file from a URL, unzips it, and extracts entries to the current directory.
- 静态失败原因: Low token overlap (Jaccard 0.1667) and different control flow structures caused the model to rely on surface-level similarity, leading to a non-clone prediction.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB might consider them clones because both perform file I/O operations that read from a source and write to a destination, treating them as similar utility functions for data transfer.
- 共享行为: Both read from an input source and write to output destinations using byte streams
- 行为差异: Source type: local file vs URL；Processing: direct copy vs zip decompression；Output: single file vs multiple files；Error handling: wraps exception in RuntimeException vs throws Exception
- 修正建议: Improve model to capture functional similarity beyond token overlap via AST or data flow analysis；Use sequence-to-sequence models that understand program intent；Incorporate byte-level I/O patterns as features

### case_id=863 FP lexical_or_api_overlap

- 方法: `main` vs `forBundle`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Main method for an AdapterGenerator tool that parses a Prolog file, generates adapters, and writes them to a JAR.
- B 摘要: Private method that processes a bundle by finding VM templates, copying selected entries into a zip, and installing the result as a plugin.
- 静态失败原因: Static BERT models may over-rely on token overlap (e.g., 'ByteArrayOutputStream', 'IOException', 'e.printStackTrace', 'URL') and boilerplate patterns, missing the high-level semantic divergence. The model likely picked up on shared Java I/O idioms and assumed similarity.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels non-clones when functions serve entirely different purposes despite superficial I/O similarities. These two functions are from different domains (code generation vs. bundle plugin management) and share no common business logic.
- 共享行为: Both perform file I/O (reading, writing, temp file creation)；Both use ByteArrayOutputStream and catch IOException with e.printStackTrace()；Both involve JAR/ZIP file manipulation
- 行为差异: Function A is an entry point (main) for a code generation tool; Function B is a private helper for bundle manipulation；A focuses on Prolog parsing and adapter generation; B focuses on OSGi bundle processing and plugin installation；A writes to a JAR file, B creates a temp JAR and installs it as a plugin；A uses a class loader and assembles shared classes; B does not
- 修正建议: Enhance training data with more diverse non-clone pairs that share common libraries but differ in intent；Incorporate control flow or data flow features to capture higher-level semantics；Use contrastive learning to penalize reliance on shallow token matches

### case_id=864 FN benchmark_preference_bias

- 方法: `getFile` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies the soap address endpoint, and saves it to a temporary directory, returning the file path.
- B 摘要: Main method for Weka experiment setup that reads or writes a serialized Experiment object, displays a GUI, and saves on close.
- 静态失败原因: Static BERT/GraphCodeBERT failed to detect the clone because it relied on surface-level API overlap and ignored the deep semantic divergence, but here static model correctly predicted non-clone, disagreeing with BCB.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled these as clones due to both involving file downloading and configuration logic, but the functional overlap is too generic and likely a mislabel.
- 共享行为: Both perform file I/O operations；Both use try-catch blocks for exception handling；Both include logging or debug output
- 行为差异: A downloads from network and modifies XML; B reads/writes serialized objects locally；A returns a file path; B is void and manages a GUI lifecycle；A involves XML parsing and channel transfers; B uses object serialization and swing；A has multiple specific exception types; B catches generic Exception
- 修正建议: Re-evaluate BCB label for this pair；Incorporate task-specific semantic understanding beyond boilerplate patterns

### case_id=865 FP boilerplate_overlap

- 方法: `executePost` vs `importSequences`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Executes an HTTP POST request with URL parameters and returns the response as a string.
- B 摘要: Imports DNA/protein sequences from a URL, parsing FASTA-like format and storing names and sequences in lists.
- 静态失败原因: The model likely over-relied on lexical and structural overlaps such as 'URL', 'InputStream', 'try', 'catch', and similar boilerplate patterns for opening connections and reading streams, ignoring the distinct semantic intents.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the functions have completely different purposes (HTTP client vs sequence import) despite superficial I/O similarities.
- 共享行为: Both use a URL to open an input stream；Both read from the input stream；Both use try-catch for exception handling
- 行为差异: A sends POST data; B only reads data；A outputs a string; B populates lists and returns void；A catches Exception broadly; B catches specific exceptions (MalformedURLException, EOFException, IOException)；A has a finally block to disconnect; B does not
- 修正建议: Incorporate data flow analysis to distinguish between writing (POST) and reading (GET/import)；Use domain-specific embeddings to capture different application contexts；Add training examples that contrast similar-looking I/O code with different high-level purposes

### case_id=866 FN benchmark_preference_bias

- 方法: `getFile` vs `readAndRewrite`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.0`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies an endpoint if needed, and saves it to a temporary directory, returning the file path.
- B 摘要: Reads a DICOM image file, extracts pixel data, and writes it to an output file.
- 静态失败原因: Static BERT likely correctly identified low lexical overlap and different domain-specific APIs, but BCB's annotation overrides with a broad clone definition that the model may not capture.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might label them as clones based on a very broad interpretation of Type-3/Type-4 similarity, such as both being 'file transformation utilities' despite completely different semantics and library usage.
- 共享行为: Both perform file I/O operations: reading from a source and writing to a destination file.
- 行为差异: Different data formats and domains: WSDL vs. DICOM.；Function A includes XML manipulation and conditional download; Function B uses DICOM-specific libraries.；Distinct exception handling and logging.；Different return types: String file path vs. void.
- 修正建议: Re-evaluate BCB annotation for this pair; consider excluding such diverging functions.；Add more domain-specific features to the model to recognize functional differences beyond surface I/O patterns.

### case_id=867 FN partial_functionality

- 方法: `getDatasetsList` vs `readData`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Retrieves a list of dataset names from a URL by reading lines, with caching.
- B 摘要: Parses comma-separated strings and a file to populate multiple sets and hash structures for Tibetan transliteration.
- 静态失败原因: Static BERT models rely on token similarity; the Jaccard similarity is very low (0.0797), so the model predicted non-clone. It failed to capture the broad functional similarity that BCB annotated, possibly due to lack of semantic understanding beyond token overlap.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have considered both as 'data reading and population' methods, focusing on the high-level similarity of reading input and storing in collections, ignoring differences in source and purpose.
- 共享行为: Both read input line by line (URL vs file) and populate collections.
- 行为差异: Different source: URL vs static strings/file；Different purpose: dataset list retrieval vs Tibetan character mapping setup；Different data structures: HashMap with URL key vs multiple HashSets and HashMaps；Different error handling: RuntimeException vs error messages and System.out
- 修正建议: Improve model's ability to recognize high-level functional similarity even with low token overlap；Use semantic parsing to identify common patterns like 'read input, store in collection'；Incorporate data flow analysis to see that both eventually populate data structures

### case_id=868 FP boilerplate_overlap

- 方法: `handleHandshake` vs `getEncoding`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Handles a Minecraft handshake packet by validating the server key and optionally authenticating via an HTTP request to session.minecraft.net.
- B 摘要: Extracts the character encoding from a URL by checking HTTP headers and then parsing the response content.
- 静态失败原因: Static BERT/GraphCodeBERT likely overemphasized the shared API calls (BufferedReader, URL, InputStream, try-catch) and structural patterns, while missing the distinct semantic contexts and final outcomes.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels as non-clones because the functions have entirely different high-level purposes (handshake processing vs. encoding extraction) and only share superficial API usage patterns.
- 共享行为: Both use BufferedReader and InputStreamReader for reading from a URL stream.；Both handle exceptions (NumberFormatException, general Exception) with try-catch blocks.；Both involve network I/O operations (URL connection, reading input).
- 行为差异: Function A is a handshake handler that validates a server key and sends a login packet; Function B is a utility to extract encoding from HTTP headers or content.；Function A calls netManager.networkShutdown or addToSendQueue; Function B returns a String encoding.；The logic and control flow are entirely different: A checks username validity and makes a specific HTTP request; B iterates over headers and lines to find charset.
- 修正建议: Improve model training with more diverse examples to distinguish high-level intent.；Incorporate dataflow analysis to differentiate control flow and output usage.；Use method name and class context as additional features.

### case_id=869 FN boilerplate_overlap

- 方法: `byReference` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Converts an InputStream to a DigitalObjectContent by copying to a temporary file.
- B 摘要: Launches a NexOpen project by configuring Maven POMs and Hibernate settings, then runs an install action.
- 静态失败原因: Static BERT correctly predicted non-clone (0), aligning with the lack of semantic equivalence. The BCB annotation appears to be a false positive, so the model did not fail; it correctly rejected the pair.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may have considered them clones due to shared use of IOUtils, file creation, and exception handling, despite fundamentally different purposes. This likely reflects a Type-4 annotation based on superficial API overlap.
- 共享行为: Both perform file and stream operations.；Both catch and handle IOException/CoreException.；Both use IOUtils to copy streams.
- 行为差异: A is a simple utility to persist an InputStream to a temp file and return a DigitalObjectContent.；B is a complex Eclipse launch handler with multiple configuration steps, project validation, and resource management.；A has no external dependencies on Eclipse or Maven, while B heavily relies on Eclipse/plugin framework and Maven concepts.；A returns a DigitalObjectContent; B is void and modifies project state.
- 修正建议: Refine annotation guidelines to exclude methods that only share generic I/O patterns but no core functionality.；Use semantic similarity measures that go beyond token-level overlap.；Consider adding context of method purpose (e.g., method name, class hierarchy) to distinguish such pairs.

### case_id=870 FP long_range_semantics

- 方法: `digest` vs `perform`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.2`
- 推荐路线: `static_summary_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Computes a cryptographic hash of a string using MessageDigest and returns the base64-encoded digest.
- B 摘要: Handles a Struts ActionForward request for classifying a concept, involving session management, HTTP communication, XML parsing, and forward determination.
- 静态失败原因: The static model likely missed the vast difference in functionality due to the large size and complexity of Code B, leading to a false positive based on superficial common elements (e.g., both have try-catch blocks and use standard Java APIs) or due to attention mechanism failing to capture the overall semantic divergence.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB labeled non-clone because the functions have no meaningful functional similarity; they belong to completely different domains (cryptographic utility vs. web action handler) and share no common high-level behavior.
- 共享行为: Both use standard Java libraries and exception handling
- 行为差异: Code A performs a simple hash computation; Code B implements a complex web request processing pipeline；Code A has no side effects; Code B modifies session attributes and makes network calls；Code A returns a String; Code B returns an ActionForward；Code A's logic is self-contained; Code B interacts with multiple external objects and services
- 修正建议: Improve handling of long code sequences through better attention mechanisms or hierarchical representations；Incorporate structural or control-flow features to distinguish between simple utilities and complex request handlers；Use external knowledge or task-specific fine-tuning to reduce false positives from boilerplate overlap

### case_id=871 FP lexical_or_api_overlap

- 方法: `importSequences` vs `readURL`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads sequences from a URL in FASTA format, parsing headers and sequences into lists.
- B 摘要: Reads lines from a URL and prints them to the console.
- 静态失败原因: Likely overemphasized shared API tokens (URL, InputStream, InputStreamReader, IOException, printStackTrace) and ignored the structural and semantic differences in the loop and data handling logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB prefers non-clone because the functions have distinct high-level purposes (biological data parser vs. simple URL printer) and no meaningful partial overlap in core logic.
- 共享行为: Both open a URL stream and read data；Both handle IO exceptions with printStackTrace
- 行为差异: A parses FASTA format and stores data; B prints lines and has no parsing；A uses ImportHelper for reading; B uses standard BufferedReader；A has no cleanup; B closes streams in finally block；A loops until '>' delimiter; B loops until null line
- 修正建议: Improve model to distinguish trivial I/O boilerplate from actual data processing logic；Incorporate structure-aware features (e.g., AST subtree comparison) to detect different control flow patterns

### case_id=872 FN partial_functionality

- 方法: `getHTML` vs `httpRequestByPOST`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Gets HTML content from a URL via HTTP GET, optionally writes to a file, and returns the HTML string.
- B 摘要: Sends an HTTP POST request with parameters, retrieves the response body as a string, and returns null on error.
- 静态失败原因: Static BERT models rely on token overlap and surface-level similarity. Low Jaccard similarity, different HTTP libraries and method names (GET vs POST), and the presence/absence of file output likely caused the model to consider them non-clones, missing the shared high-level functionality.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels as clone if both functions serve the same core purpose (HTTP content retrieval) despite differences in HTTP method, library, and error handling, treating them as Type-3/Type-4 clones.
- 共享行为: Both perform an HTTP request to retrieve content from a URL.；Both read the response line by line and accumulate into a string.；Both return the retrieved content as a string.
- 行为差异: HTTP method differs: GET vs POST.；A uses HttpURLConnection; B uses Apache HttpClient.；A may write content to a file as a side effect.；B returns null on error with error code/message; A prints stack trace and returns potentially incomplete string.
- 修正建议: Incorporate semantic features like HTTP method, library usage, and output type.；Use data-flow analysis to capture input-output transformations.；Train with more diverse examples of functionally similar but syntactically different HTTP request functions.；Consider hierarchical representations that abstract away library-specific details.

### case_id=873 FN benchmark_preference_bias

- 方法: `WebmillDeploy` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Constructor that reads a WAR file, parses XML configuration (web.xml, portlet.xml, context.xml), rewrites web application, and creates a new WAR file for portlet deployment.
- B 摘要: Method that launches a Hibernate reverse engineering configuration in an Eclipse plugin, checks Maven project structure, modifies pom.xml, sets Hibernate dialect, copies resource files, and runs an install action.
- 静态失败原因: Static BERT model likely relied on lexical overlap and token similarity, which is low (Jaccard 0.093), and failed to capture the high-level functional similarity that BCB may have considered, or conversely, the static model correctly identified them as non-clones but BCB label may be erroneous.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled them as clones due to the broad Type-3/Type-4 criteria, considering both methods perform a 'deployment/launch' task involving XML parsing, file manipulation, and resource cleanup, with similar boilerplate structures.
- 共享行为: Both involve reading and processing XML documents；Both perform file I/O and resource copying；Both have extensive resource cleanup in finally blocks；Both output informational messages
- 行为差异: Different domains: web deployment vs. Hibernate tooling；Different XML schemas: portlet vs. Maven；Different resource handling: WAR entries vs. Eclipse resources；Different end goals: produce WAR file vs. set up project for Hibernate
- 修正建议: Improve model to recognize that boilerplate similarity does not imply semantic equivalence；Incorporate domain-specific knowledge to distinguish between different types of deployment tasks

### case_id=874 FP boilerplate_overlap

- 方法: `createHTML` vs `checkForUpgrade`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Builds an HTML string for logo or home page by reading CSS file and querying dashboard content from database.
- B 摘要: Checks for available software upgrades by contacting a remote server, parsing license/upgrade data, and updating installation records.
- 静态失败原因: Static BERT may over-rely on surface-level similarities like common API calls (URL, BufferedReader), exception handling structure, and loop patterns, while missing the deep semantic mismatch in method names, comments, and overall business logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would label non-clone because these functions perform completely different tasks with no semantic overlap; the shared boilerplate patterns (reading from URL, catch blocks) are incidental and do not indicate functional similarity.
- 共享行为: Both use URL and BufferedReader to read text line by line；Both handle exceptions with try-catch；Both perform string concatenation in loops；Both have conditional logic based on string comparisons
- 行为差异: Different overall purpose: HTML generation vs. upgrade check；Different data sources: local CSS/database vs. remote HTTP response；Different output: returns HTML string vs. modifies UI components and database；Different domain: dashboard rendering vs. software update management
- 修正建议: Incorporate data flow analysis to track input-output transformations；Leverage method names and comments as semantic signals；Use contrastive learning with hard negative examples that share structural patterns but differ in functionality；Include context from surrounding code (class, imports, comments) to disambiguate intent

### case_id=875 FN benchmark_preference_bias

- 方法: `test` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: A test method that sets up a traffic simulation engine from an XML file and runs a simulation loop printing vehicle positions.
- B 摘要: A launch method for an Eclipse plugin that configures Maven project files and sets Hibernate properties.
- 静态失败原因: The static BERT model correctly predicted non-clone because it captured the low token overlap and distinct contexts; however, it failed to agree with the BCB label, which is likely erroneous.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled them as clones due to superficial similarity in using ByteArrayOutputStream and IOUtils.copy, or due to a misannotation in the benchmark.
- 共享行为: Both use ByteArrayOutputStream and IOUtils.copy for I/O operations.
- 行为差异: Function A is a simulation test; Function B is a project configuration and launch routine.；Function A operates on traffic simulation objects; Function B operates on Eclipse resources and Maven POM files.；Function A has a time-stepped loop; Function B has conditional file existence checks and property setting.
- 修正建议: Re-evaluate BCB label for this pair; if mislabeled, correct the benchmark.；Improve model robustness to ignore trivial API-level overlaps.

### case_id=876 FN partial_functionality

- 方法: `run` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads from a file and writes to another file, optionally counting bytes with diagnostic readers/writers.
- B 摘要: Retrieves a resource by URL, caches it locally after downloading with HTTP conditional GET, and returns a FileInputStream.
- 静态失败原因: Low lexical overlap (Jaccard 0.16), different method names and signatures, and domain-specific details (diagnostic vs caching) misled the model, which relied on surface features rather than high-level functional similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as performing a core data copy operation (pump/copy from one stream to another), thus labeling them as Type-4 clones despite different contexts and additional logic.
- 共享行为: Both perform I/O operations involving reading from a source and writing to a destination.；Both handle stream closing and exceptions.
- 行为差异: A uses command-line arguments for input/output files; B uses a resource name and caching.；A has optional diagnostic mode; B has HTTP conditional GET and caching logic.；A uses a Pump abstraction; B manually copies bytes.；A's output is a file with '.out' extension; B's output is a cache file in a directory structure.
- 修正建议: Incorporate dataflow analysis to capture stream copying patterns.；Use structural similarity measures that abstract away domain-specific details.

### case_id=877 FP boilerplate_overlap

- 方法: `loadDefaultSettings` vs `main`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Copies a default config resource from classpath to a file, with logging and exception handling.
- B 摘要: Main method of a Prolog-to-Java adapter generator that parses command line, reads a Prolog file, and generates adapter classes.
- 静态失败原因: Static BERT might have focused on surface-level similarities like try-catch-finally pattern and IOUtils usage, ignoring the vastly different functionality.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels non-clones when functions have different purposes and minimal structural overlap, as here.
- 共享行为: Both use IOUtils for stream operations? Actually only A uses IOUtils, B does not.；Both have try-catch blocks (though B uses catch(Throwable) and prints stack trace).；Both involve file I/O (A: FileOutputStream, B: FileUtils, JarEntryWriter, etc.).
- 行为差异: A loads a default configuration; B generates adapters from Prolog files.；A is a utility method; B is the program entry point with complex logic.；A uses IOUtils.copy; B uses many custom classes (Parser, FactVisitor, etc.).；A handles exceptions by wrapping in RuntimeException; B prints stack trace and returns.
- 修正建议: Increase penalty for common boilerplate patterns (try-catch, stream close).；Use more abstract representations capturing high-level intent.；Inject more negative examples with similar boilerplate but different logic.

### case_id=878 FN benchmark_preference_bias

- 方法: `register` vs `startScript`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Register a new user by encoding password, setting authorities, creating hash, persisting to DB, and optionally sending confirmation email.
- B 摘要: Load a script from a URL and append lines to a dialog script.
- 静态失败原因: Static BERT/GraphCodeBERT models rely heavily on token-level similarity and structure. Here, tokens are very different (register vs startScript, User vs Attributes), and the control flow differs significantly. The model correctly predicted non-clone (0), but BCB label is 1, so the model 'failed' to match the BCB label.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might consider the shared URL-reading pattern as a core functional similarity, overlooking the different contexts and additional logic. Possibly they categorized this as Type-4 based on the I/O operation.
- 共享行为: Both read data from a URL using BufferedReader and InputStreamReader；Both handle IOException
- 行为差异: A validates input and performs many security and business logic steps; B simply reads and concatenates lines.；A interacts with database and external services; B only updates a local dialog object.；A returns boolean; B returns void and can throw SAXException.
- 修正建议: Improve benchmark annotation to exclude pairs that only share low-level library calls without functional equivalence.；Use semantic similarity measures that consider overall purpose rather than isolated patterns.

### case_id=879 FN partial_functionality

- 方法: `copyResource` vs `readAndRewrite`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource from a URL or file to a destination file by reading byte by byte and writing to an output stream.
- B 摘要: Reads a DICOM file, parses it, extracts pixel data using DICOM-specific libraries, and writes the modified dataset to an output file.
- 静态失败原因: The static BERT/GraphCodeBERT model likely failed due to low token overlap (0.1) and the presence of domain-specific API calls in function B. The model may have focused on the surface-level differences rather than the high-level I/O purpose. Additionally, the length and complexity of function B could have caused the model to treat them as unrelated.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as clones because they share the high-level functionality of reading from an input resource and writing to an output file, which is a common Type-4 clone pattern. The specific implementations differ, but the core task is similar.
- 共享行为: Both read data from an input source and write data to an output file.；Both use input and output streams for I/O.
- 行为差异: Function A performs a simple byte-by-byte copy; Function B performs DICOM-specific parsing and pixel data handling.；Function A uses generic Java I/O classes; Function B uses DICOM-specific libraries (ImageIO, DcmParser, etc.).；Function B includes logging (println) and additional steps like parsing headers.
- 修正建议: Improve model's ability to recognize high-level I/O patterns across different domains.；Incorporate semantic role labeling or functional abstraction to capture core purpose.；Use contrastive learning with positive examples of broad Type-4 clones.

### case_id=880 FN boilerplate_overlap

- 方法: `doGet` vs `addRecord`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.2`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Handles HTTP GET request to display a page with access control and caching.
- B 摘要: Adds a data record by storing an input stream to a file with content-addressable storage.
- 静态失败原因: Static BERT models rely heavily on lexical and token-level similarity. The low Jaccard similarity (0.12) and different API usage (HttpServletRequest vs InputStream) led to a non-clone prediction. The model correctly identified they are different, but BCB label suggests otherwise.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may have labeled this as clone due to shared boilerplate patterns (file I/O, exception handling) and both being part of a larger system, but the core functionality is unrelated. Alternatively, it might be a labeling error.
- 共享行为: Both involve file I/O operations (creating temporary files, writing to files).；Both use try-catch-finally for resource management.
- 行为差异: Function A is a web request handler; Function B is a data storage operation.；Function A interacts with HTTP request/response and user sessions; Function B does not.；Function A has extensive page rendering logic; Function B computes digests and manages file renaming.
- 修正建议: Improve model's ability to recognize semantic clones by incorporating broader context or functional similarity.；Use more robust clone detection that considers shared functionality beyond lexical overlap.

### case_id=881 FP lexical_or_api_overlap

- 方法: `run` vs `doVersionCheck`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.85`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Loads a map tile from a URL, parses GeoJSON into vector geometries, and adds them to a data layer.
- B 摘要: Checks for a new version of jEdit by reading a version file from a URL and comparing version strings.
- 静态失败原因: Static BERT/GraphCodeBERT may rely heavily on lexical and structural overlaps, such as the common pattern of URL opening, BufferedReader, and try-catch, ignoring the distinct semantic purposes and different operations on the read data.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because despite shared boilerplate (URL reading), the core functionality and data processing are completely different, targeting different domains (map rendering vs. version checking).
- 共享行为: Both open a URL and read lines from an InputStream using BufferedReader
- 行为差异: Function A processes GeoJSON data to create geometry collections for map rendering; Function B reads version/build strings and prompts user if update available；Function A uses synchronization and manages a list of launched HTTP requests; Function B does not；Function A handles multiple protocols (file/http) and builds a URL string from data source; Function B uses a fixed property URL
- 修正建议: Incorporate more global context or semantic embeddings that distinguish data processing logic；Fine-tune on clone detection tasks that require differentiating common I/O boilerplate from core functionality

### case_id=882 FN benchmark_preference_bias

- 方法: `readPage` vs `runInternal`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.8`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Reads a web page line by line, optionally skipping comment lines (starting with '#'), and returns the concatenated HTML.
- B 摘要: Runs an internal operation to browse an OPDS catalog, handling HTTP connections, pagination, progress updates, downloading files or parsing entries.
- 静态失败原因: The static model likely focused on the structural and semantic differences, correctly identifying them as non-clones under strict equivalence. However, it failed to align with BCB's broader annotation, which may have considered the shared 'read from URL' aspect as sufficient for a clone label.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled them as clones due to both being 'URL reading' functions, despite vast differences in complexity and purpose. The annotation preference for Type-3/Type-4 often accepts partial functionality overlap, but here the overlap is minimal and superficial.
- 共享行为: Both functions open and read from a URL
- 行为差异: Code A simply returns the concatenated HTML; Code B manages complex state like pagination, progress, and error handling；Code A ignores lines starting with '#' when ignoreComments is true; Code B has no such logic；Code B handles HTTP headers, cookies, redirects, and content types; Code A does not；Code B involves downloading books and parsing OPDS entries; Code A only reads raw HTML
- 修正建议: Improve training data to include more nuanced partial-functionality clones with low lexical similarity；Use additional heuristics to capture high-level similarity in dataflow or API usage patterns

### case_id=883 FN partial_functionality

- 方法: `copyResource` vs `doPost`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource from a URL or file to a destination file by reading and writing bytes.
- B 摘要: Handles an HTTP POST request to parse multipart form data, extract a webpage, and write a mailer output to the response.
- 静态失败原因: The static BERT model likely relied on low lexical and structural similarity (Jaccard=0.115) and predicted non-clone, but BCB's annotation accepts broad partial functionality similarity such as shared I/O patterns, which the model failed to capture.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider them similar because both perform low-level I/O operations (reading input and writing output) and are categorized under 'I/O Stream Handling' despite different high-level purposes.
- 共享行为: Both involve reading from an InputStream and writing to an OutputStream.；Both close streams in a finally block or after use.；Both handle IOException.
- 行为差异: A is a simple resource copy to a file; B is a complex servlet processing multipart form data and generating a mailer.；A uses byte-by-byte copy; B uses IOUtils.copy and ByteArrayOutputStream for buffering.；B has multiple branches for different form fields and error forwarding; A has a simple source type check.；A writes to a file; B writes to an HTTP response stream.
- 修正建议: Enhance model with high-level functional semantics beyond token overlap.；Incorporate data flow analysis to recognize common I/O patterns across different contexts.；Train with broader clone categories that include partial functionality similarity.

### case_id=884 FN partial_functionality

- 方法: `copyResource` vs `testLoadSource`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource from a URL or file to a destination file by manually reading bytes and writing to a file output stream.
- B 摘要: Tests loading a source as an input stream and copies it to a string writer using IOUtils.copy, then checks content.
- 静态失败原因: The model likely focused on lexical tokens and method names, which are very different ('copyResource' vs 'testLoadSource', manual copy vs IOUtils.copy, different variable names). The token Jaccard is low (0.07), so the model did not detect semantic similarity. The model may lack understanding of the high-level stream copy pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considers this a clone because both implement the fundamental pattern of reading from an input stream and writing to an output stream until exhaustion, which is a core shared behavior despite differing contexts and output destinations.
- 共享行为: Both methods open an input stream, copy all its contents to an output stream, and close the input stream.
- 行为差异: The source and destination of the streams differ (URL/file vs DAO facade; file output vs string writer).；Method A uses manual byte copying, while method B uses IOUtils.copy.；Method B includes assertions and is a test, while A is a utility.
- 修正建议: Train on more diverse functional patterns, especially stream copy patterns.；Use code structure information like control flow and data flow to detect high-level similarities.；Incorporate knowledge of I/O patterns, such as input-output stream copy idioms.

### case_id=885 FP lexical_or_api_overlap

- 方法: `createDialogArea` vs `loadURL`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Creates a dialog area, loads a license resource, reads its content line by line, and sets it into a browser or text widget.
- B 摘要: Opens a URL with optional authentication, reads content line by line, writes it to a temporary file, and updates a status label with file size.
- 静态失败原因: The model likely relied on superficial similarities like both using URL, BufferedReader, line-by-line reading, and try-catch blocks, ignoring the overarching semantic intent.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled this as non-clone because the overall functionality and context differ significantly: one is a UI initialization method for a license dialog, the other is a network file downloader with authentication.
- 共享行为: Both open a connection to a resource (URL or bundle resource) and read line by line using BufferedReader.
- 行为差异: A creates UI components and displays the content; B writes content to a file and updates UI externally.；A uses local resource from bundle; B uses network URL with authentication.；A has fallback between browser and text widget; B has no fallback.；A does not handle credentials; B handles username/password.
- 修正建议: Incorporate structural context like method callers or surrounding class to understand purpose.；Use data flow analysis to distinguish between UI setup and file I/O operations.；Train on function-level summaries or docstrings to capture intent.

### case_id=886 FP lexical_or_api_overlap

- 方法: `doRawRequest` vs `SRWGuiClient`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Performs an HTTP POST request, sends raw data, and returns the response string.
- B 摘要: Constructs a GUI browser window that fetches XML/XHTML content from a URL, optionally transforming it with XSLT, and displays it.
- 静态失败原因: Static BERT/GraphCodeBERT may have overfitted to overlapping API tokens like 'URL', 'BufferedReader', 'url.openStream', 'StringBuffer', and 'IOException', ignoring the larger structural and functional differences. The truncated code in B may have left out distinguishing details, making the initial part look similar to A.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled these as non-clones because they share only trivial use of URL and BufferedReader (common in many Java programs), while overall functionality is completely different (HTTP POST vs GUI browser construction). The low token Jaccard (0.084) supports this.
- 共享行为: Open a URL and read data using BufferedReader
- 行为差异: doRawRequest performs POST (writes data), SRWGuiClient only reads；doRawRequest returns a string, SRWGuiClient builds a GUI and sets it visible；doRawRequest handles only I/O, SRWGuiClient involves GUI components, XSLT transformation, and event handling；doRawRequest is a utility method, SRWGuiClient is a constructor
- 修正建议: Incorporate AST or CFG-based features to capture overall function structure；Use dataflow analysis to distinguish input/output roles；Consider method signature (constructor vs method) and class context；Enforce longer input sequences or hierarchical representations to avoid truncation-related issues

### case_id=887 FN partial_functionality

- 方法: `doVersionCheck` vs `getHTML`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches version build numbers from a remote URL and triggers a version check dialog.
- B 摘要: Downloads HTML content from a URL, optionally writes it to a file, and returns the content as a string.
- 静态失败原因: Static BERT/GraphCodeBERT models focus on token-level matching and semantic embeddings. The low token Jaccard (0.216) and different method names/purposes cause a low similarity score, missing the broader structural clone. They fail to abstract the common 'download-and-parse' pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considers this a Type-4 clone because both functions implement the abstract pattern 'open URL, read lines, process line-by-line'. Despite different purposes, the structural similarity in the core I/O loop and exception handling qualifies as a weak functional clone in BigCloneBench.
- 共享行为: Both open a URL and read lines using BufferedReader；Both handle IOException via try-catch；Both use a while loop to iterate over lines
- 行为差异: A shows/hides a wait cursor on the View, B does not；A extracts specific lines starting with '.build' or '.stablebuild', B concatenates all lines with CRLF；B optionally writes the content to a file, A does not write to any file；A calls another overloaded method doVersionCheck, B returns the built string
- 修正建议: Incorporate program analysis to detect abstract I/O patterns like URL reading；Use contrastive learning on pairs with shared high-level behavior but different tokens；Augment training data with broader clone types (Type-3/4) to capture partial functionality similarity

### case_id=888 FP lexical_or_api_overlap

- 方法: `handleHandshake` vs `loadMFileViaWeb`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Handles a handshake packet from a Minecraft server, validating a username and optionally performing session authentication via HTTP.
- B 摘要: Loads a MATLAB/Octave function file from a web URL, reads its content line by line, and parses it into a UserFunction object.
- 静态失败原因: The model likely focused on the lexical overlap of URL opening and BufferedReader reading, which are common boilerplate patterns. It failed to capture the different semantic purposes and higher-level logic, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the functions have completely different functionality despite sharing a common I/O pattern. BCB annotations typically require similar high-level functionality or algorithmic intent.
- 共享行为: Both open a URL and read from it using BufferedReader；Both have try-catch blocks for handling exceptions during network I/O；Both use similar boilerplate code for stream handling
- 行为差异: Different overall purpose: session authentication vs file loading；Different input parameters and return types；Different error handling messages and recovery actions；After reading, handleHandshake checks response for 'ok', while loadMFileViaWeb parses the entire content as code
- 修正建议: Use data augmentation with more hard negatives that share API usage but differ in functionality；Incorporate method-level context (e.g., method name, surrounding class) to disambiguate；Improve representation learning to capture long-range semantic intent beyond local token patterns

### case_id=889 FN partial_functionality

- 方法: `getContent` vs `invoke`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Executes an HTTP request and returns the response body as a string with UTF-8 encoding.
- B 摘要: Invokes a remote method via HTTP POST, handles status codes and timeouts with retry, and deserializes JSON response.
- 静态失败原因: Static models like GraphCodeBERT rely on token overlap and overall semantic similarity; low Jaccard (0.23) and different method names/parameters led to non-clone prediction, ignoring the shared response-reading pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider them clones because both share a significant fragment of reading HTTP response line-by-line, a common partial functionality. Under BCB's broad Type-3/Type-4 criteria, similar subroutines can be treated as clones.
- 共享行为: Both execute HTTP requests and read the response entity.；Both use BufferedReader and InputStreamReader to read lines from the entity content.；Both accumulate lines into a StringBuilder/StringBuffer with newlines.
- 行为差异: A uses DefaultHttpClient and sets timeouts; B uses HttpClientUtils.getDefaultInstance() without timeout.；B constructs a POST URL and sets request body with JSON serialization of arguments.；B checks status code and throws RuntimeException on >=300.；B handles ConnectTimeoutException with retry logic and dynamic service URL relocation.
- 修正建议: Train models to recognize hierarchical or fragment-level similarity, not just whole-function semantics.；Incorporate AST sub-tree or data-flow graph matching for common patterns like HTTP response reading.；Use contrastive learning with positive pairs that share sub-tasks but differ in overall logic.

### case_id=890 FN benchmark_preference_bias

- 方法: `doTransfer` vs `createHTML`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Forwards an HTTP request to a remote URL and relays the response back.
- B 摘要: Generates an HTML string by loading a CSS file and optionally querying a database based on the page type.
- 静态失败原因: The static model correctly predicted non-clone because the functions have low lexical overlap (Jaccard 0.077) and distinct control flows and APIs, so it did not pick up any clone-like pattern. The model failed only relative to the questionable BCB label.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled these as clones due to very broad shared I/O patterns (reading streams, writing output) and exception handling, considering them both as data transformation routines. However, this interpretation is too loose and likely an annotation error, as the core functionality is completely different.
- 共享行为: Both use InputStream and InputStreamReader to read data.；Both include while loops reading until end of stream.；Both handle IOException.；Both use URL objects to locate resources.
- 行为差异: A acts as a network proxy; B builds an HTML page.；A writes to an HTTP response stream; B returns a String.；A reads request body and sets headers; B reads from a CSS file and queries a database.；A has complex HTTP connection handling; B has switch-case for page types.
- 修正建议: Re-evaluate BCB label for this pair to ensure it aligns with common sense.；If the label is kept, consider adding a broad I/O pattern clone type in training, but that risks false positives.；Alternatively, accept that the model's prediction is correct and adjust the benchmark.

### case_id=891 FP other

- 方法: `actionPerformed` vs `copyFileByNIO`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Event handler that processes various UI commands (e.g., setting file paths for Graphviz, ImageMagick, etc.) and updates preferences.
- B 摘要: Utility method that copies a file from source to destination using FileChannel (NIO).
- 静态失败原因: The model likely overfit on irrelevant lexical features or suffered from the truncated long code_a, producing a false positive without understanding the semantic mismatch.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB labels non-clones when functions have completely different purposes and minimal code overlap, even if both are Java methods.
- 行为差异: Function A is a complex UI event handler with multiple branches; function B is a simple file I/O utility.；A operates on GUI components and stores preferences; B only performs file copy.；A involves user interaction through file chooser dialogs; B has no interaction.；A is an instance method modifying state; B is static and stateless.
- 修正建议: Improve model's ability to distinguish control flow and domain differences.；Use data flow or call graph analysis to capture semantics.；Ensure training data includes diverse negative pairs with low token overlap.

### case_id=892 FN benchmark_preference_bias

- 方法: `setBundleInfoName` vs `readGeoParserResult`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Reads a properties file from a URL and updates bundle names in a list.
- B 摘要: Reads XML from a geo parser service and returns place names with gazetteer IDs.
- 静态失败原因: The static model correctly predicted non-clone (0), but BCB label is 1, so the model did not 'fail' in the usual sense. If anything, it missed a clone that is not semantically equivalent. The model's low token Jaccard and focus on structure likely led to correct non-clone prediction.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider them clones due to superficial structural overlap: both use URL, BufferedReader, readLine loop, and error handling. However, this is extremely broad and likely a mislabeling.
- 共享行为: Both open a URL connection and read input line by line.；Both handle IOException with try-catch.；Both return a boolean or collection indicating success/failure.
- 行为差异: A parses key-value pairs separated by '=', while B parses XML documents.；A updates existing objects in a list, B builds a new collection of tuples.；B includes retry logic and uses XML parsing libraries.；A returns boolean, B returns a collection.
- 修正建议: Provide clearer clone definitions in the benchmark to avoid overly broad Type-4 inclusions.；Use semantic-aware models that can differentiate shared infrastructure from actual functional similarity.

### case_id=893 FN benchmark_preference_bias

- 方法: `copy` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `1.0`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Recursively copies a file or directory to a destination.
- B 摘要: Launches a NexOpen/Hibernate project configuration by processing Maven POM files and setting up resources.
- 静态失败原因: The static BERT/GraphCodeBERT model correctly predicted non-clone because the token overlap is minimal and the semantic roles are distinct.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might have labeled this as clone due to both functions performing file operations and using logging, but the high-level purpose and structure are completely different.
- 共享行为: Both involve file I/O operations
- 行为差异: Function A is a simple recursive copy utility for files/directories；Function B is a complex Eclipse launch configuration that handles Maven POM, properties, and resource files
- 修正建议: Review this BCB annotation for potential mislabeling；Improve BCB annotation guidelines to avoid over-broad functional similarity

### case_id=894 FN benchmark_preference_bias

- 方法: `getFile` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.6`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, optionally modifies the endpoint address in the XML, and saves it to a temporary directory, returning the file path.
- B 摘要: Copies a local file to a destination file using buffered streams, creating the destination if it doesn't exist, and returns the destination file.
- 静态失败原因: Static BERT models like GraphCodeBERT rely on token similarity and structural patterns; with a Jaccard similarity of 0.128, the model likely saw low lexical overlap and predicted non-clone. It failed to recognize the abstract file I/O pattern that BCB might consider a clone.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may label these as clones due to both involving file I/O operations, stream handling, and exception handling patterns, which could be considered Type-4 (semantic) clones under a very broad interpretation of functionality, though the specific purposes differ significantly.
- 共享行为: Both involve reading from an input source and writing to an output file.；Both handle IO exceptions with try-catch blocks.；Both create new files if needed.
- 行为差异: A downloads from a network URL; B copies a local file.；A modifies XML content; B performs a binary copy without modification.；A returns a String file path; B returns a File object.；A includes complex logic with temporary files and deletion; B is straightforward.
- 修正建议: Incorporate data flow and control flow analysis to capture abstract I/O operations.；Use fine-tuning with more diverse examples of file handling patterns.；Consider domain-specific knowledge or API usage patterns to generalize across different file operations.

### case_id=895 FN partial_functionality

- 方法: `doTransfer` vs `read`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: This method performs an HTTP proxy transfer by reading a request, forwarding it to another URL, and writing the response back.
- B 摘要: This method reads data from either a URL or a file, opens an input stream, and returns a status code.
- 静态失败原因: Static BERT methods rely on lexical and structural similarity; the low token Jaccard (0.12) and different API sequences led to a non-clone prediction, missing the shared sub-functionality.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as implementing 'read from a URL' functionality, ignoring the additional proxy logic in A, thus labeling them as Type-4 or partial clones.
- 共享行为: Both open a URL connection and read an InputStream.；Both handle IOExceptions.
- 行为差异: Function A copies request headers, sets request method, writes request body, and streams response back to the client.；Function B only opens an input stream (URL or file) and does not perform any HTTP proxy or response writing.；Function A is tied to servlet context; Function B is a generic reader returning an integer status.
- 修正建议: Incorporate functionality-aware matching, e.g., detect common API usage patterns like URL.openStream() and InputStream.read().；Use data-flow analysis to identify shared sub-behaviors even when overall structure differs.

### case_id=896 FN benchmark_preference_bias

- 方法: `doGet` vs `testCopyUnknownSize`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Handles HTTP GET requests for a portal page, performing page lookup, visibility checks, logging, and output caching.
- B 摘要: Tests a utility method that copies all bytes from an input stream to an output stream and asserts the copy size.
- 静态失败原因: The model correctly predicted non-clone; it failed because the BCB label is erroneous. The lexical and structural differences are vast.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB likely mislabeled this pair; there is no functional similarity even under broad Type-4 criteria. Possibly an annotation error in the BigCloneBench dataset.
- 共享行为: No shared behavior identified
- 行为差异: Function A is a servlet handler with complex web page processing; Function B is a simple unit test for stream copying；Function A involves HTTP requests, parameter parsing, and caching; Function B involves only byte array streams；Function A has side effects like logging and response writing; Function B has no side effects beyond assertions
- 修正建议: Re-annotate this pair as non-clone in the benchmark；Improve quality control in benchmark annotation

### case_id=897 FN partial_functionality

- 方法: `doTransfer` vs `doVersionCheck`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Transfers HTTP requests/responses to/from a target URL acting as a proxy.
- B 摘要: Checks for a new version of jEdit by reading a version file from a URL and comparing builds.
- 静态失败原因: The static model likely focused on low token overlap and syntactic dissimilarity, predicting non-clone, but BCB's annotation considers broader functional similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB might consider both as network I/O operations that involve creating a URL, opening a stream, reading data, and catching exceptions, thus viewing them as clones under a broad Type-4 category.
- 共享行为: Both open a URL connection；Both read from an input stream；Both handle IOException
- 行为差异: A forwards complete HTTP request/response; B only reads a version file；A supports multiple HTTP methods; B uses GET only；A writes to response output stream; B shows a message dialog
- 修正建议: Incorporate high-level functional concepts (e.g., 'HTTP client' operation) into the model；Use execution trace or dataflow to capture shared behavior beyond syntax

### case_id=898 FP lexical_or_api_overlap

- 方法: `getUser` vs `run`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Loads a user from a database or parses a local config file to create a User object.
- B 摘要: Performs an authenticated HTTP GET request and reads the response into a string.
- 静态失败原因: Static models may over-rely on overlapping API calls (e.g., BufferedReader, InputStreamReader, readLine) and structural patterns (while loop) without understanding the distinct semantics and data flow.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clone because these functions perform fundamentally different tasks with different inputs and outputs, despite sharing some I/O patterns.
- 共享行为: Both use BufferedReader to read from an InputStream；Both have while loops reading lines；Both handle exceptions
- 行为差异: Different purposes: user lookup vs HTTP request；Different data sources: local config file vs remote HTTP server；Different output: returns User vs sets instance variables
- 修正建议: Incorporate data flow analysis to differentiate between local file access and network I/O；Use function names and return types as features；Add control flow to capture different exception handling styles

### case_id=899 FN partial_functionality

- 方法: `sendExceptionToServer` vs `doVersionCheck`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.65`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends exception details to a server via HTTP POST with encoded parameters.
- B 摘要: Checks for a new version by fetching and parsing a version file from a URL.
- 静态失败原因: Static models like GraphCodeBERT rely on token and AST overlap. Despite shared API tokens (URL, BufferedReader, InputStreamReader), the low Jaccard similarity (0.2056) and different method names/purpose led to a non-clone prediction. The model missed the coarse-grained functional similarity of network communication.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as network I/O operations that read a response from a URL, ignoring the direction of data flow (write vs read) and the specific payload, thus labeling them as Type-3/4 clones with partial functional similarity.
- 共享行为: Both use URL and open a connection/stream to a remote server；Both read lines from the server response using BufferedReader；Both handle IOException with error reporting
- 行为差异: Function A writes a payload to the connection (POST-like), while B only reads (GET-like)；Function A constructs a complex query string with multiple encoded parameters; B parses lines for specific prefixes；Function A prints success/failure messages; B calls another method or shows an error dialog
- 修正建议: Incorporate data flow analysis to distinguish write vs read network operations；Enhance with method name semantics or domain-specific knowledge about error reporting vs version checking；Use cross-function context to identify common network I/O patterns

### case_id=900 FP lexical_or_api_overlap

- 方法: `doVersionCheck` vs `getFullScreenUrl`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Checks for new version of jEdit by reading a remote version file and comparing build numbers.
- B 摘要: Extracts video ID and timestamp from a YouTube page to construct a full-screen video URL.
- 静态失败原因: Static BERT/GraphCodeBERT models may overweigh common API tokens and control flow patterns (URL, BufferedReader, while loop) while neglecting the different method names, return types, and domain-specific logic (version numbers vs. video parsing).
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically annotates non-clones when the overall functionality differs significantly, even if some structural or API patterns overlap. The version-checking and video URL extraction are distinct tasks.
- 共享行为: Both open a URL and read lines using BufferedReader.；Both use try-catch for IOException/Exception.；Both perform string processing on each line.
- 行为差异: Method A shows/hides wait cursor and displays GUI messages; method B sets progress bar indeterminate.；Method A compares build numbers; method B parses key-value pairs and constructs a URL.；Method A uses a static property for URL; method B uses an instance variable ytUrl.；Method A returns void; method B returns a String.
- 修正建议: Incorporate dataflow analysis to track specific variables and their uses (e.g., build vs. video_id/t).；Pay more attention to method signatures, return types, and method-level semantics.；Use contrastive learning to distinguish boilerplate code from functionally equivalent logic.

### case_id=901 FP lexical_or_api_overlap

- 方法: `main` vs `main`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Tests a StraightStreamReader by reading a file in various ways and verifying correctness.
- B 摘要: Generates Java adapter classes and resources from a Prolog file using a framework.
- 静态失败原因: Static BERT likely over-relied on lexical and API surface overlap (e.g., 'File', 'IOException', 'main', try-catch blocks) and common boilerplate patterns, ignoring the distinct algorithm and purpose.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clones because the overall functionality is entirely different: one is a test routine, the other is a generator. BCB looks at high-level semantic equivalence, not just shared API usage.
- 共享行为: Both are main methods.；Both handle files (create, read, check existence).；Both use try-catch for IOException.；Both use FileOutputStream and FileInputStream.
- 行为差异: Code A is a unit test for a custom stream reader; Code B is a code generation tool.；Code A writes and reads raw bytes; Code B parses Prolog and writes Java classes.；Code A performs multiple read operations with different buffer offsets; Code B uses visitors and class writers.；Code A has no command-line argument parsing; Code B parses arguments for input file and debug mode.
- 修正建议: Incorporate dataflow or control flow analysis to differentiate algorithms.；Use higher-level semantic features like method purpose or domain context.；Enhance training with more negative examples that share APIs but diverge in functionality.

### case_id=902 FP lexical_or_api_overlap

- 方法: `run` vs `postXml`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Loads and processes vector tile data from a URL, parsing geometries and adding to a data loader.
- B 摘要: Posts XML to a URL with SOAP action and returns the response as a string.
- 静态失败原因: Static BERT models may have been misled by high lexical overlap in API calls (e.g., URLConnection, BufferedReader, IOException) and similar control flow patterns (open stream, read loop), ignoring the distinct protocols (GET vs POST) and entirely different data processing logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the overall functionality is completely different: one loads map tiles, the other performs a SOAP XML post. The shared API usage does not create functional similarity.
- 共享行为: Both functions open URL connections and handle input streams.；Both read data line by line from a BufferedReader.；Both handle IOException and have error return paths.
- 行为差异: Function A uses GET or file protocol; B uses POST with XML body and SOAP headers.；Function A parses tile coordinates and processes geometries; B simply returns the response string.；Function A involves synchronization and caching logic; B does not.；Function B sets connection timeouts and request properties; A does not.
- 修正建议: Incorporate syntax-aware or data-flow features to distinguish different types of I/O operations.；Use contrastive learning to penalize pairs that share only boilerplate API usage.；Add a classifier that checks for semantic similarity of input/output structures.

### case_id=903 FN partial_functionality

- 方法: `main` vs `decodeBody`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a URL and extracts its zip entries to files.
- B 摘要: Decodes an input stream based on content transfer encoding and returns a BinaryTempFileBody.
- 静态失败原因: The static BERT model likely focused on the low token overlap (Jaccard=0.15) and structural differences, failing to recognize the high-level stream-copying pattern that BCB considered similar.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as stream processing with transformation (zip extraction vs encoding decoding) and I/O handling, fitting broad Type-4 clone based on partial functionality similarity.
- 共享行为: Both read from an input stream and write to an output stream.
- 行为差异: A downloads a file and extracts a zip archive; B decodes a MIME body.；A writes to multiple output files; B returns a single temporary file body.；A uses ZipInputStream; B uses QuotedPrintableInputStream or Base64InputStream.；A is a main method with URL handling; B is a utility method without URL logic.
- 修正建议: Incorporate method-level semantics and external knowledge about common I/O patterns.；Use dataflow analysis to capture the transformation stages (read, process, write).；Train on clone benchmarks with broader Type-4 definitions.

### case_id=904 FN benchmark_preference_bias

- 方法: `readData` vs `addQDInformation`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Reads comma-separated tokens from predefined class variables and populates various sets and lookup maps for Tibetan transliteration.
- B 摘要: Reads a configuration file from local file or URL, parses lines with specific prefixes, and updates project information objects with date and value.
- 静态失败原因: Static embedding models likely rely on lexical similarity and structural overlap; the low token Jaccard (0.127) and different method names lead to large embedding distance, causing a non-clone prediction even though BCB might consider functional similarity.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider both as 'data initialization' methods that read and populate data, despite different specifics, possibly as a broad Type-4 clone.
- 共享行为: Both parse input (tokens or lines) and populate internal data structures.
- 行为差异: Different input sources: hardcoded strings vs. file/URL.；Different target data structures: sets/maps of strings vs. project info objects with numbers.；Different parsing logic: tokenization vs. line prefix checking.；Different domains: Tibetan transliteration setup vs. project info update.
- 修正建议: Incorporate control-flow or data-flow features to capture high-level functional patterns.；Use a model that is explicitly trained on BCB-style annotations to recognize partial functionality clones.；Combine lexical features with structural similarity metrics.

### case_id=905 FN partial_functionality

- 方法: `doVersionCheck` vs `seeURLConnection`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.65`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Opens a URL specified by jEdit property, reads lines, extracts build version strings, and calls another method, with wait cursor and error handling.
- B 摘要: Opens a hardcoded URL, reads all lines into a buffer, and logs the concatenated result.
- 静态失败原因: The static BERT model likely relied on token-level similarity and API patterns. While both use similar API calls (URL, BufferedReader), the overall structure and context differ significantly (method signatures, constants, error handling), causing the model to focus on differences rather than the shared URL-reading core.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider the core behavior of reading from a URL and processing text lines as functionally similar, despite differences in specific processing, because both are Type-4 semantic clones under a broad interpretation of 'retrieving and processing remote content'.
- 共享行为: Both open a URL and create a BufferedReader to read lines；Both read until end of stream using readLine() loop；Both close the BufferedReader after reading
- 行为差异: A shows and hides a wait cursor on a View; B does not handle any UI；A catches IOException and shows error dialog; B throws Exception to caller；A parses specific lines starting with '.build' and '.stablebuild'; B concatenates all lines；A calls another overloaded method; B logs the result
- 修正建议: Incorporate data-flow analysis to detect that both functions perform a read operation on a URL stream；Train on examples of semantic clones where only a subset of functionality is shared；Use a model that abstracts away method names and specific constants to focus on structural patterns

### case_id=906 FP lexical_or_api_overlap

- 方法: `createOutputStream` vs `readData`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Creates a BufferedWriter by copying all entries from a zip file except 'content.xml', then opening a new entry for 'content.xml'.
- B 摘要: Reads a configuration file and populates multiple sets (topSet, leftSet, etc.) and hash tables based on parsed tokens.
- 静态失败原因: The model likely overemphasized lexical and API-level overlap (e.g., both use 'File', 'InputStreamReader', 'BufferedReader' and loop structures), failing to capture the stark semantic difference in what the functions accomplish.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels non-clones when functions have completely different purposes and outputs, even if they share superficial I/O patterns.
- 共享行为: Both perform file I/O operations；Both use loops to process data；Both involve reading from files
- 行为差异: A writes to a new zip output stream; B only reads and populates in-memory data structures；A deals with zip entries and character streams; B deals with StringTokenizer and text file parsing；A returns a BufferedWriter; B has void return and modifies global state
- 修正建议: Incorporate dataflow analysis to distinguish between reading and writing operations；Use graph-based representations that capture control and data dependencies more explicitly；Train on larger and more diverse non-clone pairs to reduce false positives from common API usage

### case_id=907 FP lexical_or_api_overlap

- 方法: `sendPost` vs `postData`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Sends HTTP POST request to a given URL with a parameter and returns the response body as a string, handling exceptions by showing a message.
- B 摘要: Sends HTTP POST request to a constructed URL with given data, discards the response, and throws exceptions if any.
- 静态失败原因: Static BERT models likely focused on the high lexical and structural overlap (both use URL, HttpURLConnection/URLConnection, PrintWriter/PrintStream, BufferedReader) and missed the semantic differences in return value, exception handling, and header usage. The common HTTP POST pattern dominated the representation.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled these as non-clones because the differences in return type, exception handling, and specific headers indicate distinct functional roles—one is a utility that returns the response, the other is a void method that discards it. BCB tends to treat such varied HTTP client patterns as not functionally equivalent.
- 共享行为: Both perform HTTP POST operations using standard Java networking classes.；Both set DoOutput and DoInput to true.；Both write data to the output stream and read the input stream.
- 行为差异: Function A returns the response body; Function B does not return anything.；Function A catches exceptions and shows a message; Function B throws exceptions.；Function A uses HttpURLConnection and sets Accept-Language header; Function B uses URLConnection and sets Content-type and Content-length headers.；Function B has default parameters and null-checking; Function A does not.
- 修正建议: Incorporate return type and exception handling features explicitly.；Use dataflow analysis to track whether response is used or discarded.；Train with more diverse HTTP client examples to distinguish utility vs. fire-and-forget patterns.

### case_id=908 FN benchmark_preference_bias

- 方法: `setContenu` vs `doGet`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Sets the content of a fichier electronique by copying input stream to output stream and updating metadata, with checks for existing files and special handling for email attachments.
- B 摘要: Handles HTTP GET request to serve a page, looking up page by ID or name, checking user visibility, logging, rendering HTML, and optionally caching the page.
- 静态失败原因: Static BERT correctly predicted non-clone (0) due to very low token Jaccard similarity (0.061) and no overlapping API calls. It did not fail; the BCB label is the outlier.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as a clone due to both methods performing some form of 'content setting' (A sets file content, B sets page content in response), but the mechanisms and contexts are entirely different, making this likely an annotation error.
- 共享行为: Both functions involve exception handling and logging；Both use InputStream/OutputStream? But B does not use stream copying.
- 行为差异: A copies file content; B processes HTTP requests and renders web pages；A deals with file metadata; B deals with page visibility and caching；A is a static utility method; B is a servlet method；A uses IOUtils.copy; B uses response.getWriter and output stream for HTML
- 修正建议: Re-evaluate BCB annotation for this pair; likely a false positive clone label；If retaining as clone, add explicit note that it requires partial functional similarity interpretation

### case_id=909 FN partial_functionality

- 方法: `main` vs `retrieveQ`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: main method that sends a hardcoded POST request to RenRen API with multiple parameters and prints the response.
- B 摘要: Utility method that retrieves content from a given URL via HTTP (default GET) and returns it as a string, printing response message to stderr.
- 静态失败原因: Static models like BERT rely on token overlap and surface structure; low Jaccard similarity (0.212) and different method names/parameter lists caused it to miss the shared HTTP reading pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often considers methods that perform the same core task (HTTP response reading) as clones, even if parameterization and output differ, as long as the core logic is functionally similar (Type-3/4).
- 共享行为: Open URL connection and read response content；Use BufferedReader to read lines；Handle HTTP response
- 行为差异: Method A is POST with specific parameters; Method B is GET (implied) with generic URL；Method A prints output to stdout; Method B returns string and prints to stderr；Method A hardcodes request details; Method B takes URL as argument
- 修正建议: Incorporate dataflow analysis to detect I/O operations；Train on more examples of utility wrappers and API invocations sharing core logic；Use abstract syntax tree (AST) based features to capture control flow structure

### case_id=910 FP lexical_or_api_overlap

- 方法: `getVersion` vs `retrieveTemplate`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches and returns the version string from a hardcoded URL, returning null on failure.
- B 摘要: Fetches and caches a blog template from a configurable URL, throwing an exception on failure.
- 静态失败原因: High lexical and API overlap (URL, BufferedReader, InputStreamReader, readLine, close) and similar control flow caused the model to overlook semantic differences like overwriting vs concatenation, static vs instance context, and caching logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled non-clone because methods serve distinct purposes (version check vs template retrieval) with different error handling and output semantics, making them functionally dissimilar despite shared I/O patterns.
- 共享行为: Both read text content from a URL using BufferedReader and InputStreamReader.
- 行为差异: Different source URL (hardcoded vs dynamic).；Different output processing (overwrites variable vs concatenates lines).；Different error handling (returns null vs throws exception).；Caching only in method B.
- 修正建议: Incorporate dataflow analysis to track variable assignments and detect overwriting vs appending.；Use contrastive training with pairs that have similar I/O but different data manipulation.

### case_id=911 FN partial_functionality

- 方法: `getNetworkServersIPs` vs `register`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.4`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Parses a network resource to extract server IP addresses from lines following a specific marker.
- B 摘要: Registers a user by setting properties, creating a forum user via HTTP request, persisting to database, and sending confirmation email.
- 静态失败原因: Static BERT/GraphCodeBERT likely focused on low token overlap (0.19) and structural differences in control flow and data dependencies, missing the high-level similarity in network I/O API usage patterns.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have considered both functions as 'network communication' tasks involving URL reading and line processing, thus labeling them as functionally related despite different specific behaviors.
- 共享行为: Both use URL, URLConnection, and BufferedReader to read lines from a remote source；Both handle IOExceptions
- 行为差异: Different return types and purposes: one returns a Vector of IPs, the other returns a boolean after user registration；Different input types and validation: one takes a URL string, the other takes an Object and checks for User type；Different data processing logic: one parses lines for server IPs, the other reads forum ID and sets entity fields；Different side effects: one has no side effects, the other persists to database and sends email
- 修正建议: Incorporate API-level usage patterns as features；Use data-flow analysis to detect shared network I/O structure

### case_id=912 FP lexical_or_api_overlap

- 方法: `sendPost` vs `run`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Sends an HTTP POST request with a parameter string and returns the response body.
- B 摘要: Sends an HTTP GET request with basic authentication and stores the response in a field, also updating a timestamp.
- 静态失败原因: GraphCodeBERT likely relied on surface-level API token overlap (HttpURLConnection, BufferedReader, while loop) and missed the semantic distinction between POST and GET methods, as well as differences in side effects and output handling.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the functions have different HTTP methods (POST vs GET), different input/output handling, and different side effects, which are considered significant functional differences even though the code structure is similar.
- 共享行为: Both use HttpURLConnection to make HTTP requests；Both read the response line by line into a buffer；Both close the input stream and reader
- 行为差异: Function A uses POST method while B uses GET；Function A sends data in the request body (param), B uses URL and adds authorization header；Function A returns the response as a String, B stores it in a field and sets a finish flag；Function B records lastInteraction timestamp, A does not
- 修正建议: Add dataflow analysis to differentiate HTTP method；Incorporate control flow to detect side effects like field assignments and timestamp updates；Use method name or annotation to infer semantics

### case_id=913 FN partial_functionality

- 方法: `getFile` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from URL, modifies XML to set endpoint, and returns local file path.
- B 摘要: Retrieves a resource via URL with caching, returns InputStream of local cached copy.
- 静态失败原因: Static BERT/GraphCodeBERT may have low token overlap (Jaccard 0.15) and different method signatures, leading to classification as non-clone. Also, the models may not capture high-level semantic similarity of 'download and cache' across different implementations.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as 'download file from URL and store locally' functions, ignoring the specific XML manipulation and caching differences, labeling them as Type-4 semantic clones.
- 共享行为: Both retrieve a resource from a URL.；Both involve saving the resource locally.；Both use URLConnection to open connection.
- 行为差异: A specifically handles WSDL XML and modifies it; B does not modify but caches and checks modification time.；A returns file path (String); B returns InputStream.；A uses NIO channels for copying; B uses buffered streams with single-byte read.；A does not cache; B maintains a cache hashtable and conditional GET.
- 修正建议: Include more training examples of semantic clones with different API usages.；Incorporate data flow or control flow features to capture shared sub-tasks.

### case_id=914 FN partial_functionality

- 方法: `doTransfer` vs `run`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Forwards an HTTP request to a new URL by copying headers and request body, then writes the response back.
- B 摘要: Reads a classpath resource as text and sets it into a JTextArea using SwingUtilities.invokeLater.
- 静态失败原因: Low token overlap (Jaccard 0.137) and different method signatures mislead static BERT; it lacks the ability to infer high-level I/O pattern commonality across different APIs.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considered both as involving reading from a URL and writing the content to an output, which is a Type-4 functional similarity despite different specific destinations.
- 共享行为: Read input from a URL/stream；Write output to a destination (HTTP response or UI text area)；Handle IO exceptions
- 行为差异: Source of stream: HTTP request vs classpath resource；Output target: HTTP response vs JTextArea；Handling of headers and request method present only in A；Output encoding and content type handling only in A
- 修正建议: Enhance model with data flow analysis to identify read-write patterns；Use contrastive learning on I/O roles；Incorporate context of stream handling

### case_id=915 FN partial_functionality

- 方法: `getFile` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies the SOAP address endpoint in the XML, and saves it to a temporary file, returning the file path.
- B 摘要: Copies a file from a source to a destination using NIO FileChannel.
- 静态失败原因: Static BERT/GraphCodeBERT models rely heavily on lexical tokens and overall function structure. The low token Jaccard (0.104), different method names, parameter types, and high-level control flow led to a non-clone prediction, missing the shared use of FileChannel for file copying.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label these as clones because they share the core algorithmic pattern of copying data via NIO channels, and BCB's broad Type-4/Type-3 acceptance includes partial functionality similarity where one function contains a subtask similar to the other.
- 共享行为: Both use NIO FileChannel for file I/O operations.；Both involve reading from one input source and writing to an output file.
- 行为差异: Function A includes network download, XML parsing and manipulation, and multiple file operations.；Function B is a simple file copy with no network or XML processing.；Function A has extensive error handling for various exceptions; function B only throws IOException.；Function A modifies the file content (XML) before writing; function B performs a direct copy.
- 修正建议: Enhance models with dataflow analysis to detect shared subroutines like NIO channel operations.；Incorporate subgraph matching to identify embedded functionality even when overall structure differs.；Train on more examples of partial-functional clones to improve recognition of shared algorithmic patterns.

### case_id=916 FN boilerplate_overlap

- 方法: `doVersionCheck` vs `File2String`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.75`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads version and build information from a remote URL and performs a version check, updating the UI accordingly.
- B 摘要: Reads the entire content of a file or classpath resource into a string, with error handling that exits the program on failure.
- 静态失败原因: Low token overlap, different API calls (URL vs File, jEdit vs ClassLoader), and different control flow caused the model to focus on surface differences rather than the shared buffered read loop.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely considered both as instances of 'reading a text resource line by line', a common utility pattern, thus labeling them as clones despite different purposes.
- 共享行为: Open an input stream；Create a BufferedReader；Iterate over lines using readLine()；Close the reader
- 行为差异: A reads from a URL; B reads from a local file or classpath resource；A parses lines for specific prefixes (version, build); B concatenates all lines into one string；A returns void and shows UI messages; B returns String and uses System.out/exit；Error handling: A catches IOException and shows error dialog; B catches FileNotFoundException/IOException and calls System.exit
- 修正建议: Incorporate high-level semantic features like 'stream reading loop' recognition；Use data flow analysis to abstract from specific library calls；Train with contrastive learning on pairs sharing algorithmic structure despite low token overlap

### case_id=917 FN partial_functionality

- 方法: `readPage` vs `fileDownload`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a web page optionally skipping lines starting with '#' and returns the content as a string.
- B 摘要: Downloads a file from a URL and saves it to a local file, with error logging.
- 静态失败原因: Static models like GraphCodeBERT rely on lexical overlap and structural similarity. The token Jaccard is low (0.227), method names differ, return types differ, and control flows diverge significantly (one has conditional comment filtering, the other has file writing). The model likely missed the shared URL reading subprocess.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this as a clone because both functions perform the core task of retrieving data from a URL using similar I/O patterns (URL, InputStreamReader, BufferedReader), despite differences in how the data is processed after reading. The structural and conceptual similarity in downloading content from a URL dominates.
- 共享行为: Open a URL connection and obtain an InputStream；Use BufferedReader to read data from the stream；Read until end of stream and close the reader
- 行为差异: A returns the read content as a string; B writes to a file and returns void；A filters lines starting with '#' when ignoreComments is true; B has no filtering；A reads lines; B reads character by character；A throws Exception; B catches and logs exceptions
- 修正建议: Incorporate data flow analysis to capture common API usage patterns；Use program slicing to isolate the URL reading portion and measure similarity on that subgraph；Enhance attention to functional roles of methods rather than exact token matching

### case_id=918 FN partial_functionality

- 方法: `main` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: A main method that decompresses a .gz file by reading with GZIPInputStream and writing to a new file using a buffer of 8192 bytes.
- B 摘要: A method that builds a site for editing by reading XML files, performing XSLT transformations, and writing the output pages using a char buffer of 8192 bytes.
- 静态失败原因: The static BERT/GraphCodeBERT model likely relied on low token overlap (Jaccard=0.11) and could not capture the deep semantic similarity in the buffer usage pattern, while being misled by the long and complex structure of function B.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: The BCB annotator may have considered the common pattern of using a 8192-byte buffer for file I/O and resource management as sufficient for a Type-3 or Type-4 clone, despite the significant difference in overall functionality.
- 共享行为: Both use a buffer of size 8192 for reading from an input stream.；Both perform file I/O with input and output streams.；Both close streams in a finally block.
- 行为差异: Function A is a simple decompression utility with a single task; function B is a complex CMS page builder with many sub-steps.；Function A reads from a GZIPInputStream; function B reads from FileInputStream and performs XSLT transformations.；Function A writes to a single output file; function B writes to multiple output files with string processing.；Function A has no parameters; function B has many parameters including properties and paths.
- 修正建议: Improve model's ability to recognize partial functionality similarities, e.g., by focusing on common I/O idioms.；Incorporate structural information like buffer size constants and resource management patterns.；Use data-flow analysis to highlight similar variable usages across functions.；Augment training with examples of broad Type-3/Type-4 clones that share only a portion of behavior.

### case_id=919 FP boilerplate_overlap

- 方法: `updateFile` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Copies a file from source to destination using FileChannel, with error handling.
- B 摘要: Handles various user action commands (e.g., GRAPHVIZ, IMAGEMAGICK) in a settings UI, updating preferences and UI components.
- 静态失败原因: The static model likely overfitted on superficial lexical clues such as both methods containing 'File', 'IOException', and try-finally patterns, despite the low Jaccard similarity (0.05). The model may have been biased by common boilerplate code without understanding the distinct semantics.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clone because the two functions perform entirely different tasks: one is a file copy utility, the other is a complex user interface event handler. Even under a broad Type-4 definition, they do not share core functionality.
- 共享行为: Both involve file operations (reading/writing file paths or content).；Both use exception handling patterns.
- 行为差异: Function A copies file content; Function B handles several distinct UI actions.；Function A uses NIO FileChannel for efficient transfer; Function B uses JFileChooser for file selection.；Function A is focused on a single file operation; Function B has branching logic for multiple commands.；Function B updates many UI elements and preferences; Function A only creates directories and copies file.
- 修正建议: Incorporate control-flow and data-flow analysis to distinguish core logic from boilerplate.；Use larger token windows with attention mechanisms that capture long-range semantics.；Train on more diverse non-clone pairs with similar boilerplate but different functionality.；Include API call sequence embeddings to differentiate file I/O patterns.

### case_id=920 FN partial_functionality

- 方法: `readData` vs `readReferenceText`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Reads and processes multiple CSV strings and a configuration file to populate various data structures (sets, maps, arrays) for Tibetan and Sanskrit character handling.
- B 摘要: Reads a reference text file from a URL and returns its contents as a string, with error handling.
- 静态失败原因: The token Jaccard similarity is very low (0.088), and the code structures are vastly different (long static void vs concise method with try-catch), leading the model to focus on lexical/structural mismatch and predict non-clone.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as 'reading data' methods in a Tibetan text processing plugin, deeming them functionally similar (Type-4) despite structural differences.
- 共享行为: Both involve reading textual data from an external source.
- 行为差异: A is a complex initialization with multiple parsing steps and state modification; B is a simple file read and return.；A has no return value; B returns a string.；A has no explicit input parameter; B takes an identifier.
- 修正建议: Incorporate data-flow or high-level goal detection (e.g., both perform I/O reading).；Use semantic role labeling to capture 'read data' pattern.

### case_id=921 FN partial_functionality

- 方法: `main` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Extracts files from a ZIP file downloaded from a hardcoded URL.
- B 摘要: Copies a file from one location to another using buffered streams.
- 静态失败原因: The static model likely relied on surface tokens (method names, literal strings, APIs) and Jaccard overlap (0.22). The core functional similarity of the streaming copy loop was overshadowed by differences in ZIP handling, error management, and protocol branching, leading to a low similarity score and false negative.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB classifies this as a clone because both functions implement the core pattern of reading from a byte stream and writing to another, which qualifies as Type-4 (similar functionality) in BigCloneBench, even though the contexts (ZIP extraction vs file copy) differ.
- 共享行为: Both read bytes from an InputStream into a buffer；Both write those bytes to an OutputStream
- 行为差异: A processes ZIP entries and handles URL/file protocols; B copies a single file；A uses fixed buffer size (BUFFER constant) and BufferedOutputStream; B uses 0xFFFF and plain FileOutputStream；A has no error handling except throws Exception; B includes try-catch-finally and returns boolean；A outputs progress (extracting entry) and does not close streams in finally; B closes streams in finally
- 修正建议: Incorporate dataflow analysis to identify read-write loop patterns independent of surrounding context；Use AST-based or graph-based models (e.g., CodeBERT, GraphCodeBERT) to capture structural similarities at a finer granularity；Add attention to common I/O idioms (read()/write() in loop) as strong clone indicators；Include partial functionality annotations or fragment-level clone detection

### case_id=922 FP lexical_or_api_overlap

- 方法: `readTwitterFead` vs `readRemoteFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads Twitter user timeline JSON using Apache HttpClient with status code check.
- B 摘要: Reads a remote file using java.net.URL.openStream() without status code check.
- 静态失败原因: The model likely over-relied on lexical overlap (common tokens like 'BufferedReader', 'InputStream', 'readLine', 'IOException') and high-level similarity (both fetch remote content) without capturing the distinct API usage patterns and control flow differences.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically requires significant functional similarity with implementation correspondence. Although both read remote text, the use of completely different HTTP libraries, different control flow for reading lines, and different error handling make them Type-4 (functional) but not Type-3 clones; BCB likely considered them non-clones due to these structural differences.
- 共享行为: Both fetch content from a remote HTTP URL and return it as a string.；Both use BufferedReader and InputStreamReader to read line by line.；Both handle IOException.
- 行为差异: A uses Apache HttpClient (DefaultHttpClient, HttpGet), B uses java.net.URL.openStream().；A checks HTTP status code (200) and logs error on failure; B does not.；A uses a simple while loop; B uses a more complex loop with eof flag and handles EOFException.；A catches ClientProtocolException separately; B catches EOFException.
- 修正建议: Incorporate control flow graph or data flow analysis to distinguish different HTTP client patterns.；Use API-specific token embeddings or attention to library calls.；Add more examples of non-clones with similar high-level tasks but different implementations.

### case_id=923 FP lexical_or_api_overlap

- 方法: `loadExistingAntlibs` vs `SRWGuiClient`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Loads antlib definitions from classpath resources using ClassLoader and iterates over them.
- B 摘要: Constructs a Swing browser GUI that loads an XML URL, applies XSLT transformation, and displays HTML content.
- 静态失败原因: Static BERT/GraphCodeBERT likely relied on token overlap (e.g., URL, BufferedReader, InputStreamReader, try-catch) and missed the vast structural and semantic differences in the control flow, method purpose, and class context.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clones because the functions serve entirely different purposes: one is a build-tool resource loader, the other is a GUI browser constructor with XML processing. Any token overlap is coincidental boilerplate.
- 共享行为: Both use URL, BufferedReader, InputStreamReader for reading input streams.
- 行为差异: Function A is a utility method for loading antlibs; Function B is a GUI constructor with complex UI setup.；Function A reads resources from classpath; Function B reads from a URL input by user.；Function B includes XSLT transformation and Swing component initialization; Function A does not.；Function A has error handling wrapped in try-catch for IOException and URISyntaxException; Function B has IOException and TransformerException.
- 修正建议: Include data-flow and control-flow features to distinguish different use of common I/O patterns.；Incorporate method name and class context embedding.；Use clone detection thresholds that penalize large differences in function length and complexity.

### case_id=924 FP lexical_or_api_overlap

- 方法: `readZoneIDs` vs `getRequestContent`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads all integer IDs from a classpath resource file into a HashSet.
- B 摘要: Fetches the first line from an HTTP response as a String.
- 静态失败原因: Static models like BERT over-relied on lexical and API-level overlaps (URL, openStream, readLine, etc.) without capturing the divergent data flow, output types, and iteration logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would consider these non-clones because the core functionality (reading all integers from a resource vs fetching one line from HTTP) is entirely different, despite similar I/O boilerplate.
- 共享行为: Both use URL objects to access remote or local resources.；Both open input streams and read textual data line by line.；Both use BufferedReader/LineNumberReader for reading.
- 行为差异: Function A reads all lines until end-of-file; Function B reads only one line.；Function A parses lines as integers and collects them in a set; Function B returns the raw string.；Function A catches and prints exceptions; Function B throws exceptions.；Function A uses classpath resource; Function B uses an arbitrary URL string.
- 修正建议: Introduce structural features like number of loop iterations or output data type.；Use data-flow analysis to distinguish single-line vs. multi-line reading.；Incorporate semantic role labeling of API calls (e.g., 'read all' vs. 'read one').

### case_id=925 FP boilerplate_overlap

- 方法: `readData` vs `convert`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Parses comma-separated configuration strings into sets and reads a Tibetan.ini file to populate data structures for Tibetan text processing.
- B 摘要: Converts an ACRNEMA stream DICOM file to a proper DICOM format by parsing, verifying, and writing pixel data with optional bit inflation.
- 静态失败原因: The static model likely overgeneralized from common boilerplate patterns (e.g., try-catch, loops, stream handling) and failed to capture the specific semantics and domain differences. The low token Jaccard indicates little lexical overlap, but the model may have been misled by structural similarities in control flow.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would not label these as clones because they solve entirely different problems with no overlap in functionality, structure, or domain. BCB annotation preference requires at least partial functional similarity, which is absent here.
- 共享行为: Both involve reading from an input source and writing to an output source.；Both use try-catch for exception handling.；Both perform iterative processing of data (loops).
- 行为差异: Completely different domains: Tibetan text processing vs. medical image conversion.；A uses StringTokenizer and sets; B uses DICOM parsing and pixel data manipulation.；A reads configuration data; B converts DICOM files with UID assignment and pixel handling.；A outputs to internal data structures; B writes to a FileOutputStream.
- 修正建议: Incorporate domain-specific embeddings or task-level features.；Use dataflow analysis to distinguish different I/O operations.；Train with more negative pairs from diverse domains.；Apply contrastive learning with harder negatives.

### case_id=926 FN partial_functionality

- 方法: `copyResource` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a file from a generic resource (URL or path) to a destination file, byte-by-byte.
- B 摘要: Recursively copies files and directories from a source to a destination, using buffered streams.
- 静态失败原因: Static models (e.g., GraphCodeBERT) rely on token sequences and structural patterns. Low Jaccard similarity (0.22) and different APIs (URL.openStream vs FileInputStream) cause the model to miss the semantic overlap. The recursive nature and varying control flow obscure the shared purpose.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB considers broad Type-3/Type-4 clones; both functions perform file copying, a common functionality. The structural differences (buffer vs byte, recursion vs single) are tolerated under partial functionality similarity.
- 共享行为: Both functions copy file content from a source to a destination.
- 行为差异: Function A only copies single files; Function B handles directories recursively.；Function A uses unbuffered byte-by-byte reading; Function B uses a buffer.；Function A reads from a URL or file path; Function B always reads from a File object.；Function B creates directories if needed; Function A does not.
- 修正建议: Enhance training with more diverse file copy examples to capture high-level purpose.；Use dataflow analysis to track that both functions ultimately read and write bytes.；Incorporate hierarchical or recursive structure awareness for directory-copy patterns.

### case_id=927 FN partial_functionality

- 方法: `main` vs `copyFromFileToFileUsingNIO`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.5`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a URL and extracts its ZIP entries to local files using ZipInputStream.
- B 摘要: Copies a file from one File to another using NIO FileChannel transfer.
- 静态失败原因: Low token Jaccard (0.156) and different structural patterns; static BERT likely lacked high-level semantic understanding to see the abstract file I/O similarity that BCB might consider.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB might label them as clones due to broad similarity in file copying behavior, or because both involve reading and writing file data, even though the mechanisms and scope differ.
- 共享行为: Both perform file I/O operations reading from a source and writing to a destination.
- 行为差异: Function A handles multiple zip entries, uses streams and buffering, and prints progress; Function B transfers a single file using NIO channels.
- 修正建议: Improve representation of file I/O operations, incorporate data flow or functional equivalence at a higher abstraction level.

### case_id=928 FN partial_functionality

- 方法: `copyResource` vs `convert`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies any resource (URL or file) to a destination file by reading bytes and writing them one by one.
- B 摘要: Converts a DICOM file: reads DICOM metadata, validates conditions, and writes a modified DICOM file including pixel data copying.
- 静态失败原因: Static models like BERT rely on token overlap and structural similarity; the low Jaccard (0.13) and the dominating DICOM-specific tokens obscure the common byte-copying pattern. The models fail to recognize that the pixel data loop in convert is functionally equivalent to the entire copyResource function.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider these clones because both contain a core byte-copying loop (in convert, the pixel data writing loop exactly mirrors copyResource's main loop). Under broad Type-4 partial functionality similarity, the shared sub-behavior suffices for clone classification.
- 共享行为: Both read from an InputStream and write to an OutputStream.；Both perform byte-by-byte copying in a loop.；Both close the streams after writing.
- 行为差异: copyResource handles both URL and file sources; convert only handles file sources.；convert includes complex DICOM-specific logic: parsing, metadata checks, tag writing, pixel data inflation.；convert prints diagnostic messages and has multiple early return conditions; copyResource throws an exception on missing resource.
- 修正建议: Incorporate subgraph or dataflow analysis to detect shared I/O patterns.；Use techniques like program slicing to isolate common sub-behaviors.；Train models to focus on core computational loops rather than auxiliary metadata handling.

### case_id=929 FN benchmark_preference_bias

- 方法: `main` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Main method that creates signed PDF documents using iText library, involving keystore loading, certificate chains, and PDF signing/verification.
- B 摘要: Method to retrieve a resource as an InputStream with caching, handling HTTP connections and file system caching.
- 静态失败原因: Static BERT models may have correctly identified low token overlap and no strong semantic similarity, leading to a non-clone prediction. The BCB label might be an anomaly or based on broader functional similarity that the model did not capture.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled these as clones due to both being part of the same project (iText) and sharing superficial similarities like exception handling patterns and I/O operations, or due to annotator leniency for Type-4 similarity.
- 共享行为: Both use try-catch blocks with exception handling and stack trace printing.；Both involve file I/O operations (FileInputStream, FileOutputStream).；Both contain System.out.println for logging.
- 行为差异: Function A performs PDF signing and verification; Function B performs resource retrieval with caching.；Function A uses iText PDF library classes; Function B uses URL/HTTP connections and file caching.；Function A has a complex sequence of cryptographic and PDF-specific operations; Function B is focused on network and file caching logic.
- 修正建议: Improve annotation guidelines to reduce false positives in BCB.；Use models that better capture high-level semantic intent rather than superficial patterns.；Incorporate domain knowledge or project context to differentiate between unrelated auxiliary methods.

### case_id=930 FP lexical_or_api_overlap

- 方法: `getFullScreenUrl` vs `parse`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Extracts YouTube video ID and timestamp from a webpage and constructs a download URL.
- B 摘要: Parses a delimited data file or URL into a DataSet with type conversion and header handling.
- 静态失败原因: The model likely focused on surface-level similarities such as reading from a URL, using BufferedReader, and exception handling, while missing the domain-specific context and differing output logic. The long length of the functions may also cause attention to focus on common tokens.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled non-clone because the functions perform entirely different tasks (YouTube scraping vs generic data parsing). Even though both I/O patterns are similar, the core functionality and output types differ significantly.
- 共享行为: Both read from a URL or file using BufferedReader.；Both use try-catch for exception handling.；Both parse lines of text in a loop.
- 行为差异: Function A extracts specific YouTube video parameters; Function B parses arbitrary delimited data into a DataSet.；Function A outputs a String URL; Function B outputs a DataSet object.；Function A uses simple string splitting; Function B uses StreamTokenizer with configurable delimiters and type conversion.；Function A has UI progress indicators; Function B does not.
- 修正建议: Incorporate more context-aware embeddings that capture domain-specific semantics.；Use dataflow analysis to distinguish different data transformations.；Train on more diverse clones to reduce bias towards boilerplate I/O sequences.

### case_id=931 FP boilerplate_overlap

- 方法: `encodeFileToFile` vs `readData`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.75`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Encodes a file to Base64 and writes to another file, returning success status.
- B 摘要: Reads and parses a configuration file to populate multiple sets and hash maps for Tibetan transliteration data.
- 静态失败原因: The static model may have been misled by common structural patterns such as file I/O boilerplate (InputStream, OutputStream, try-catch-finally) and similar loop constructs, despite low token Jaccard similarity. The truncated nature of code_b might also cause the model to miss key differences.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the functions have completely different purposes and implementations; they are not even type-4 (similar functionality) as the core goals are unrelated.
- 共享行为: Both involve file I/O operations；Both use exception handling with try-catch-finally
- 行为差异: encodeFileToFile performs Base64 encoding, readData parses structured configuration data；encodeFileToFile writes output to a file, readData populates in-memory data structures；encodeFileToFile returns boolean success, readData is void and modifies global collections；encodeFileToFile uses a simple buffer copy loop, readData has complex tokenization and conditional parsing
- 修正建议: Incorporate semantic similarity measures that go beyond token overlap and API usage；Use dataflow analysis to differentiate core logic from boilerplate code；Train models on more diverse negative examples with low token similarity but high structural similarity

### case_id=932 FN benchmark_preference_bias

- 方法: `doGet` vs `copy`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Handles HTTP GET requests for a portal page, including user authentication, page retrieval, logging, caching, and response rendering.
- B 摘要: Copies a file from source path to destination path using input/output streams.
- 静态失败原因: The model correctly identified the low lexical overlap and distinct contexts (web servlet vs. file copy), but according to BCB's label, it failed because it did not recognize the superficial I/O similarity that BCB considered as clone-worthy.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as a clone due to a very broad interpretation of Type-4 (functional similarity) where both functions involve reading from an input source and writing to an output source, despite drastically different domains and complexity.
- 共享行为: Both perform I/O operations (reading/writing streams)
- 行为差异: Function A is a servlet method handling HTTP requests and responses, while B is a utility function for file copy.；A involves complex logic like user permissions, caching, and page rendering; B has simple stream copy.；A writes to an HTTP response and optionally to a file cache; B writes to a file output stream.；A uses multiple external dependencies (PortalRequest, Property, Page, etc.); B uses only standard Java I/O.
- 修正建议: Improve benchmark consistency by enforcing stricter functional equivalence criteria.；Re-evaluate BCB labels for pairs with low lexical overlap and high semantic discrepancy.；Train models with more diverse negative examples to avoid over-sensitivity to common I/O patterns.

### case_id=933 FN lexical_or_api_overlap

- 方法: `readPage` vs `File2String`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a web page line by line, optionally skipping lines starting with '#', and returns the content with newlines.
- B 摘要: Reads a file (or classpath resource) line by line, concatenating lines without newlines, with debug output and exit on error.
- 静态失败原因: Low lexical token overlap (Jaccard 0.206) and different API calls (URL vs File) cause static models to miss the high-level similarity in the pattern of reading lines and building a string.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB often considers functions that perform similar core operations (reading from an external source, line-by-line processing, string building) as clones, even with differing details like source type and error handling.
- 共享行为: Both read text line-by-line from an input stream and return a concatenated string.
- 行为差异: Input source: URL vs file/resource；Line processing: optional comment skip and newline addition vs no skip and no newlines；Error handling: throws exception vs prints and exits；Debug output present only in B
- 修正建议: Incorporate AST or CFG features to capture structural similarities；Use data flow analysis to identify the read-and-append pattern；Train on examples with partial functionality overlap

### case_id=934 FP lexical_or_api_overlap

- 方法: `getWebPage` vs `SRWGuiClient`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: A utility method that fetches a web page from a URL and returns its content as a single string.
- B 摘要: Constructor for a simple web browser GUI that reads XML from a URL, optionally applies XSLT transformation, and displays the result in a JEditorPane.
- 静态失败原因: The static model likely focused on the overlapping lexical tokens related to opening a URL and reading lines, ignoring the broader context of the methods (one is a standalone utility, the other is a constructor with GUI setup). This lexical overlap triggered a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB annotation likely considers these non-clones because their overall functionality and purpose are completely different despite a shared low-level I/O pattern. BCB emphasizes semantic equivalence in terms of what the functions achieve, not just structural similarity.
- 共享行为: Both open a URL and create a BufferedReader from an InputStreamReader to read the content line by line.
- 行为差异: Function A returns the concatenated content as a string; function B processes XML, applies stylesheets, and displays content in a GUI.；Function A uses simple string concatenation in a loop; function B uses StringBuffer and handles XML.；Function A throws an Error on IOException; function B catches IOException and warns user.；Function B initializes a full GUI with panels, buttons, and layout; function A has no GUI.
- 修正建议: Incorporate method-level context such as method name, return type, and class membership.；Use data-flow analysis to understand how the read data is used (returned vs. displayed in GUI).；Apply a threshold that penalizes partial overlap if the rest of the method differs significantly.

### case_id=935 FN partial_functionality

- 方法: `copyResource` vs `run`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource from a URL or file path to a destination file byte by byte.
- B 摘要: Pseudolocalizes a list of files by reading messages, applying a pipeline, and writing output files.
- 静态失败原因: Static BERT models rely on token overlap and syntactic structure; low Jaccard (0.172) and different method names caused the model to miss the high-level I/O pattern. The model likely focused on lexical differences rather than the abstract functional similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this as a clone because both functions follow the broad pattern of reading from an input source, transforming data (even if trivially in A), and writing to an output destination, which is considered Type-4 semantic similarity.
- 共享行为: Both open an input stream from a file or resource and an output stream to a file；Both perform a loop reading input and writing to output；Both close streams after processing
- 行为差异: A copies raw bytes; B processes structured messages through a pipeline；A handles only one input; B handles multiple files and also stdin；A generates output filename implicitly; B constructs output filenames with a suffix
- 修正建议: Incorporate control-flow and data-flow features to capture abstract patterns like I/O loops；Train on more semantic clone examples with low token overlap；Use graph-based code representations to model structural similarity

### case_id=936 FN partial_functionality

- 方法: `doCopyFile` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a file from source to destination, preserving file date optionally, using FileChannel.
- B 摘要: Retrieves a resource as an InputStream, caching it locally with HTTP support and conditional updates.
- 静态失败原因: Static BERT models may fail due to low lexical overlap (Jaccard 0.09) and focus on token-level similarity, but they might miss high-level functional commonality that BCB annotators consider.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this as clone due to both methods involving file input/output operations and stream handling, which could be considered partial functional similarity at a high level, especially if the context of the framework (e.g., Apache Commons IO) categorizes file utilities similarly.
- 共享行为: Both perform file I/O operations；Both use InputStream/OutputStream；Both handle exceptions
- 行为差异: A copies a local file to another local file; B downloads a remote resource and caches it locally；A uses FileChannel for efficient transfer; B uses BufferedInputStream and BufferedOutputStream；A checks destination directory and file sizes; B manages a cache with HTTP headers and conditional requests；B has complex caching logic and HTTP handling; A is straightforward copy
- 修正建议: Improve model to capture broader functional semantics beyond token overlap；Incorporate control flow and data flow analysis to distinguish different I/O patterns

### case_id=937 FN benchmark_preference_bias

- 方法: `transport` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Recursively copies files from a source directory to a destination directory using NIO FileChannel.
- B 摘要: Configures and launches a NexOpen project in Eclipse by processing Maven POM files and setting up Hibernate properties, then scheduling an install action.
- 静态失败原因: The static method did not fail; it correctly predicted non-clone with high confidence due to low token overlap and distinct structural patterns. The BCB label is erroneous, causing a false negative from the BCB perspective.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB annotators may have mistakenly considered both methods as involving file operations or resource handling, but their actual functionalities are completely unrelated. The annotation likely reflects a human error or overly broad interpretation of clone types.
- 行为差异: Function A operates on file and directory copying; Function B handles Eclipse project configuration and launch.；Function A uses FileChannel.transferTo for I/O; Function B uses XML parsing, property handling, and project resource management.；Function A is a simple recursive traversal; Function B involves multiple complex steps including template handling and reverse engineering file creation.
- 修正建议: Review and correct the BCB annotation for this pair.；Ensure that similarity metrics used by static models align with functional semantic equivalence, not accidental token matches.

### case_id=938 FP lexical_or_api_overlap

- 方法: `postData` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Sends an HTTP POST request with optional default parameters and discards the response.
- B 摘要: Performs a Google image search, extracts image URLs from the response, and updates a GUI component with the first image.
- 静态失败原因: Static models like GraphCodeBERT may rely heavily on token overlap and structural patterns. Both functions share common boilerplate like URL opening, BufferedReader reading, and closing. The model may have been misled by these overlapping patterns while missing the semantic differences in parameters, return types, and overall purpose.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels non-clones when functions have different purposes despite some common boilerplate code. Here, one is a generic POST utility and the other is a specific image search with UI interaction, so they are likely labeled 0 (non-clone).
- 共享行为: Both open an HTTP connection to a constructed URL using URL and URLConnection classes.；Both read the response line by line using BufferedReader and close the reader.
- 行为差异: Function A uses HTTP POST and sends data via an output stream; Function B uses HTTP GET and does not send data.；Function B parses the response to extract image URLs and stores them in a list.；Function B updates a GUI element (JLabel) and sets a button enabled; Function A does not modify UI.；Function B has error handling that shows dialog; Function A throws exceptions.
- 修正建议: Incorporate method name and parameter names/meanings into the input representation.；Add features that capture data flow and API usage semantics.；Use dynamic analysis or consider method call context beyond the function body.

### case_id=939 FP lexical_or_api_overlap

- 方法: `handler` vs `executePost`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a web page line by line, extracts substrings based on delimiters from a TargetPage, and updates a result map.
- B 摘要: Sends an HTTP POST request with parameters to a given URL, reads the response, and returns it as a string.
- 静态失败原因: The model over-relied on superficial API similarities (e.g., URL, BufferedReader, readLine) and control flow patterns, ignoring the critical differences in I/O direction and data transformation.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely considered them non-clones due to fundamentally different purposes: one is a response parser, the other is a generic HTTP client. Despite structural overlap, the behavior and output differ significantly.
- 共享行为: Both use URL and BufferedReader to read from a network stream；Both have readLine loops to process response
- 行为差异: A only reads from a given URL; B actively sends a POST request；A modifies a map in place; B returns a string；A uses custom delimiters; B uses HTTP headers and POST data；A does not handle output streams or request methods
- 修正建议: Incorporate dataflow analysis to differentiate read-only vs. read-write operations；Emphasize input/output types and method signatures；Train on more diverse examples where API overlap does not imply clone

### case_id=940 FN long_range_semantics

- 方法: `sendExceptionToServer` vs `testNetworkHTTP`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends exception details to a server via HTTP POST with encoded parameters and prints the server response.
- B 摘要: Tests multiple HTTP GET requests to various hardcoded URLs, reading and discarding response lines.
- 静态失败原因: Low token overlap (Jaccard 0.18) and different function signatures caused the static model to miss structural similarity; the model is not sensitive to the common API usage pattern (URL, BufferedReader, while readLine) across different variable names and string literals.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely labeled as clone because both functions follow the same general pattern of making HTTP requests: create URL, open connection, read response with BufferedReader, handle IOException, and they both serve a network communication purpose.
- 共享行为: Both open HTTP connections using URL and URLConnection；Both read response lines with BufferedReader in a while loop；Both catch IOException for error handling
- 行为差异: A uses POST method (setDoOutput(true)), B uses GET；A sends specific encoded parameters; B does not send data；A checks response for 'success' and prints accordingly; B just reads lines without processing；A uses URLConnection, B uses HttpURLConnection and disconnects in finally
- 修正建议: Use graph-based or tree-based models that capture API call sequences and control flow；Add more training examples that are structurally similar but lexically different；Leverage data flow analysis to understand common patterns like HTTP communication

### case_id=941 FN benchmark_preference_bias

- 方法: `run` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: A method that copies data from an input file to an output file using a pump, with an optional diagnostic mode that counts bytes.
- B 摘要: A method that builds a website for editing by applying XSLT transformations to XML and writing output pages, with extensive file and property handling.
- 静态失败原因: Static BERT likely relied on token overlap (very low Jaccard similarity 0.068) and did not detect any deeper semantic similarity, correctly predicting non-clone.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this pair as clone due to very broad notion of file I/O and debugging, but the overall functionality is entirely different, making it an unlikely Type-3/Type-4 clone.
- 共享行为: Both methods involve file input/output operations and have optional debug/trace output.
- 行为差异: Function A performs simple data pumping from one file to another, while B performs complex XML transformation and multi-step site generation.；A uses dependency injection framework; B uses direct file streams and XSLT.；A conditionally adds diagnostic counters; B conditionally writes trace statements to a debug file.；A operates on a single input; B processes multiple pages from a vector parameter.
- 修正建议: Improve BCB annotation guidelines to exclude pairs with only incidental similarities like generic I/O and debug patterns.；Use a more fine-grained clone taxonomy that distinguishes between data-flow similarity and structural similarity.

### case_id=942 FP lexical_or_api_overlap

- 方法: `googleImageSearch` vs `CheckUrl`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Searches Google Images by constructing a URL, fetching and parsing HTML, extracting image URLs, and updating the UI with an image.
- B 摘要: Fetches the first line of a given URL and returns it as a string.
- 静态失败原因: The static model overemphasized lexical and API overlap (URL, HttpURLConnection, BufferedReader, try-catch) and missed the high-level semantic differences in purpose, side effects, and data flow.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled as non-clone because the functions have different overall purposes (UI-oriented image search vs. simple URL checker) and significant behavioral differences, despite sharing a low-level HTTP reading pattern.
- 共享行为: Open an HTTP connection to a URL；Read text from the response using BufferedReader
- 行为差异: Input: A takes two strings (search and start), B takes one URL string；Output: A returns void and updates global state and UI; B returns a String；Processing: A parses HTML to extract image URLs; B simply reads the first line；Error handling: A shows error dialog; B prints stack trace
- 修正建议: Incorporate method name and input/output type information；Use data flow analysis to track how read data is used；Train on more diverse examples distinguishing simple utility from complex processing

### case_id=943 FP lexical_or_api_overlap

- 方法: `readZoneIDs` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads zone IDs from a class resource file, parsing each line as an integer into a set.
- B 摘要: Searches Google images via HTTP, parses HTML for image URLs, and updates a GUI with an album art image.
- 静态失败原因: Static BERT models may overemphasize overlapping API sequences (URL, InputStreamReader, readLine, exception handling) and ignore contextual differences like resource vs HTTP, missing the distinct functional semantics.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels these as non-clones because they belong to different functional categories: one is simple file I/O parsing and the other is web scraping with UI interaction, with no shared high-level intent.
- 共享行为: Both use URL and InputStreamReader to read data line by line；Both catch exceptions and print stack traces
- 行为差异: A reads from a local class resource; B makes an HTTP request to an external service；A parses integers from each line; B parses HTML to extract image URLs and updates UI components；A returns a HashSet; B has void return and modifies global state；B uses HttpURLConnection with custom headers; A uses a simple URL from class resource
- 修正建议: Incorporate data-flow and control-flow analysis to distinguish between local resource access and network communication；Use contrastive learning with functional labels to separate I/O operations from web scraping；Add attention to method name and class context to capture high-level purpose

### case_id=944 FP partial_functionality

- 方法: `executeHttpGet` vs `executePost`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Send HTTP GET request via Apache HttpClient and return response as JSONObject.
- B 摘要: Send HTTP POST request with URL parameters via HttpURLConnection and return response as String, with error handling.
- 静态失败原因: The static model likely learned a general pattern of HTTP response reading (BufferedReader and while loop) and overlooked the distinguishing contexts: HTTP method, parameter handling, client library, and return type. Token-level similarity is low, but AST subtree similarity may be high for the reading loop, causing false positive.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB typically labels clones only if the core functionality is semantically equivalent. Here, one method is for GET and the other for POST, and return types differ, so they are not considered clones.
- 共享行为: Both methods send an HTTP request and read the response line-by-line.；Both build a string from the response lines.；Both are private helper methods in a Java class.
- 行为差异: Different HTTP methods: GET vs POST.；Different client libraries: Apache HttpClient vs core java.net.；Different return types: JSONObject vs String.；Different error handling: method A throws Exception, method B catches exceptions and returns null.
- 修正建议: Incorporate explicit feature extraction for HTTP method and parameter handling.；Use control-flow analysis to differentiate between GET and POST configurations.；Train on more diverse examples to reduce reliance on boilerplate patterns.

### case_id=945 FN partial_functionality

- 方法: `runScript` vs `postData`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches a script from a URL and returns its content as a string.
- B 摘要: Sends POST data to a URL and reads the response (discarding it).
- 静态失败原因: Static BERT models like GraphCodeBERT may rely on token-level overlap and control flow structure. Here, token Jaccard is low (0.15), but more importantly, the model might be misled by common I/O patterns (URL, InputStream) while missing the functional difference of read vs write.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as web resource communication functions that involve URL, streams, and I/O, thus labeling them as clones under broad Type-4 definition.
- 共享行为: Both create a URL object and open a connection；Both use input streams to read from the connection；Both handle I/O operations with try-catch or throws
- 行为差异: runScript returns the fetched data; postData returns void；runScript performs a GET-like request; postData performs a POST request；runScript reads character by character; postData writes data and reads line by line discarding；runScript handles errors by returning 'error!'; postData throws exceptions
- 修正建议: Incorporate data-flow analysis to distinguish read vs write operations；Use API call graphs to differentiate GET-like vs POST-like behavior；Add training examples that distinguish similar structures but opposite semantics

### case_id=946 FN benchmark_preference_bias

- 方法: `getFile` vs `DecodeMapFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies the XML to update the SOAP address, and saves it to a temporary file, returning the file path.
- B 摘要: Reads a map file, XOR-decrypts each byte with an incrementing key, and writes the result to an output file.
- 静态失败原因: The static model likely relied on token overlap and syntactic similarity, which are very low (0.133), causing it to miss the abstract 'file processing' pattern that BCB might consider a clone.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: The BCB annotation may have considered both as file transformation routines with I/O, but the functionalities are too diverse; the low Jaccard similarity suggests this is likely a misannotation.
- 共享行为: Both functions open input and output streams；Both functions use exception handling with try-catch blocks；Both functions perform file I/O operations
- 行为差异: Function A downloads from a URL and manipulates XML; Function B performs simple XOR encryption on a local file；Function A returns a String; Function B returns void；Function A uses XML parsing and channel I/O; Function B uses basic byte array reading and writing
- 修正建议: Increase sensitivity to abstract patterns like 'file read-write with transformation' in training；Add negative examples with high I/O overlap but different purposes to reduce false negatives from such bias

### case_id=947 FN partial_functionality

- 方法: `getResourceAsStream` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Caches a network resource locally and returns an InputStream.
- B 摘要: Recursively copies a file or directory to a destination.
- 静态失败原因: Static BERT models rely on token overlap; low Jaccard similarity (0.15) and differing function names lead to false negative.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as file I/O operations with similar low-level byte copying and stream management, labeling as Type-4 clone.
- 共享行为: Both use FileInputStream and FileOutputStream；Both read and write bytes in a loop；Both handle stream closing
- 行为差异: Function A involves HTTP connection, URL handling, and caching logic；Function B handles directory recursion and file path manipulation
- 修正建议: Enhance models to recognize common I/O patterns beyond token overlap；Use data flow analysis to identify similar read-write loops；Incorporate higher-level representation of stream operations

### case_id=948 FP lexical_or_api_overlap

- 方法: `postData` vs `getFrameworkFactory`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Sends an HTTP POST request with data to a specified URL.
- B 摘要: Loads a FrameworkFactory instance from a service file using reflection.
- 静态失败原因: Static BERT models may over-rely on token overlap (URL, BufferedReader, readLine, close) and boilerplate exception handling, missing the distinct semantic intents.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clones when functions have different high-level purposes despite sharing low-level boilerplate I/O patterns.
- 共享行为: Both create a URL object；Both use BufferedReader to read input；Both close I/O streams in a loop or try-finally
- 行为差异: Function A performs network I/O for HTTP POST; Function B performs class loading from file；Function A writes data via OutputStream; Function B does not write；Function B uses reflection to load a class; Function A does not
- 修正建议: Incorporate structure-aware embeddings that capture method call sequences and control flow；Use dataflow analysis to distinguish between input/output operations；Train on more diverse examples to reduce sensitivity to common boilerplate

### case_id=949 FN partial_functionality

- 方法: `doGet` vs `bootKernel`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.2`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Handles an HTTP GET request to retrieve and serve a page with access control, logging, and caching.
- B 摘要: Boots a kernel by loading configuration from Android assets, copying files, and instantiating a kernel class.
- 静态失败原因: The static model (e.g., GraphCodeBERT) relies on token overlap and data flow within local contexts. The token Jaccard similarity is extremely low (0.0687), and the functions have no shared API calls or identifiers. The behavioral similarity is abstract and not captured by surface-level features.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider this a Type-4 semantic clone because both functions follow a similar high-level pattern of resource acquisition, processing, and error handling with logging, despite different domains. The annotators may have prioritized structural similarity over functional equivalence.
- 共享行为: Both use try-catch for error handling；Both perform logging (myLogger.info/Log.d) on progress and errors；Both involve loading/reading resources (page properties vs asset configuration)；Both have a sequence of obtaining a resource, processing, and handling exceptions
- 行为差异: Function A is an HTTP servlet method (doGet) managing page requests; function B is a private Android method (bootKernel) for system boot；Function A deals with HTTP request/response objects, user permissions, and page caching; function B deals with asset files, properties, class loading, and kernel boot；The core logic and domain are completely different: web page serving vs kernel initialization；The resource types and data flow are distinct
- 修正建议: Incorporate language-agnostic structural patterns like try-catch-log sequences；Use more global context or description-based similarity (e.g., code comments or method names)；Apply transfer learning from large-scale code that captures high-level intentions

### case_id=950 FN benchmark_preference_bias

- 方法: `genCustRatingFileAndMovieIndexFile` vs `modifyApplicationMessage`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `preference_memory_with_manual_audit`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Reads a binary file of movie ratings and generates two output files: a movie index file and a customer rating file.
- B 摘要: Modifies or adds a property in a localized properties file by reading, editing, and writing the file.
- 静态失败原因: Static BERT models focus on token-level embeddings and may miss high-level semantic differences; here, it correctly saw distinct logic but failed to recognize the broad file-processing pattern that BCB annotators considered similar.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB annotators may consider both functions as 'file processing' tasks that read, transform, and write data, despite different domains and algorithms, thus labeling them as Type-4 clones based on broad functional similarity.
- 共享行为: Both functions read input files and write output files.；Both involve looping over input data and conditional logic to transform data.；Both use file I/O APIs and handle exceptions.
- 行为差异: A processes binary data using ByteBuffer and FileChannel; B processes text properties using character streams.；A writes multiple output files with different structures; B writes a single output file.；A's logic tracks movie changes; B's logic searches for a property name to update or add.；A uses fixed-size records; B uses line-by-line parsing.
- 修正建议: Incorporate task-specific features like I/O operation types and data flow.；Use contrastive learning to better capture broad functional similarity.；Ensure training data covers a wider range of partial functional similarities.

### case_id=951 FP boilerplate_overlap

- 方法: `process` vs `main`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Processes a template to generate an output file, handling different template destinations and types.
- B 摘要: Entry point for generating adapters from a Prolog file, parsing it, and writing a jar.
- 静态失败原因: Static BERT/GraphCodeBERT likely overfitted on lexical and API overlap (e.g., File, IOException, System.out) and structural patterns like switch and try-catch, ignoring the high-level semantic differences.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely marks as non-clone because the two functions perform entirely different tasks despite sharing some common boilerplate code.
- 共享行为: File I/O operations；System.out.println statements；Exception handling with try-catch blocks
- 行为差异: Different core functionality: template processing vs adapter generation；Different input/output types and structures；Different algorithms and library usage
- 修正建议: Enhance model with better semantic understanding of code purpose；Incorporate data flow or call graph analysis to distinguish different tasks；Use contrastive learning to differentiate clones with shared boilerplate but different semantics

### case_id=952 FN benchmark_preference_bias

- 方法: `doGet` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Handles an HTTP GET request to retrieve a page, checks permissions, logs requests, and optionally caches the page output to a temporary file.
- B 摘要: Copies a file from a source path to a destination path, creating parent directories if needed.
- 静态失败原因: The static model correctly predicted non-clone (0) due to low token overlap and distinct API usage. The BCB label appears to be an outlier or reflects a very liberal clone definition, which the model appropriately ignored.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as a broad Type-4 semantic clone because both functions perform file writing operations with similar steps (checking conditions, creating files, handling exceptions). However, the overall intent and context are entirely different.
- 共享行为: Both involve writing data to a file in the filesystem.
- 行为差异: A is a web request handler with complex control flow and dependencies; B is a straightforward file utility.；A includes user authentication, page lookup, and caching logic; B only copies file bytes.；A uses javax.servlet, custom Page/Property classes; B uses only java.io.；A conditionally writes to a temp file based on editability; B always writes to the specified destination.
- 修正建议: Improve BCB annotation consistency for Type-4 clones; provide clearer guidelines for partial functionality similarity.；Static models could be enhanced with high-level intent recognition, but in this case the model is already correct.

### case_id=953 FN partial_functionality

- 方法: `copy` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a file by reading characters from a FileReader and writing to a FileWriter.
- B 摘要: Retrieves an InputStream from a resource via URL, with caching and HTTP handling, and copies the stream to a local cache file.
- 静态失败原因: Low lexical overlap (token Jaccard 0.12) and large difference in method length/complexity caused the model to miss the shared copy behavior.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considered the copy loop as the core functionality, and both methods perform that operation, making them Type-4 (functionally similar) clones.
- 共享行为: Both read data from an input source and write it to an output source in a loop.
- 行为差异: A is a simple file copy; B involves URL fetching, HTTP connections, caching, and returns an InputStream.；A writes to a specified output file; B writes to a cache file and returns a FileInputStream.；B includes exception handling and cleanup that A lacks.
- 修正建议: Use dataflow-aware models that capture shared substructures.；Incorporate clone detection techniques that focus on subgraph matching or long-range dependencies.

### case_id=954 FN partial_functionality

- 方法: `getFile` vs `_checkLanguagesFiles`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies XML attribute, and returns file path.
- B 摘要: For each language, ensures a properties file exists and copies it to temp directory if needed.
- 静态失败原因: The model likely relied on low lexical overlap (token Jaccard 0.1656) and different APIs (URLConnection vs ActionRequest), missing the conceptual similarity in file copying.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider the core file I/O pattern (check existence, create, copy) as sufficient functional similarity, ignoring differences in data source and modification.
- 共享行为: Both check if a file exists and create it if missing.；Both copy file content using FileChannel.
- 行为差异: A downloads from URL; B reads from local filesystem.；A modifies XML content; B does not modify content.；A processes a single file; B iterates over multiple files.；A returns file path; B returns void.
- 修正建议: Incorporate control flow and I/O operation patterns into features.；Use structure-based embeddings that capture sequences of file operations.；Train on more examples of file-based clones with different domains.

### case_id=955 FN benchmark_preference_bias

- 方法: `getFile` vs `doGet`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies its endpoint address, and saves it to a temporary file.
- B 摘要: Handles an HTTP GET request to retrieve and render a portal page with visibility checks and caching.
- 静态失败原因: The static model correctly predicted non-clone based on low token overlap and distinct semantics; the benchmark annotation appears to be an error.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as a clone due to superficial similarities like file I/O and exception handling, despite completely different purposes.
- 共享行为: Both perform file I/O operations and use logging.
- 行为差异: Core functionality is entirely different: WSDL downloading vs. page serving.；Different input parameters and output types.；Different domain and context: web services vs. portal framework.
- 修正建议: Re-annotate this pair as non-clone in BCB.

### case_id=956 FN lexical_or_api_overlap

- 方法: `sendExceptionToServer` vs `File2String`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.3`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends exception details to a server via HTTP POST.
- B 摘要: Reads a file from disk or classpath into a string.
- 静态失败原因: A static BERT model likely over-relies on token overlap (e.g., 'BufferedReader', 'URL', 'IOException') and cannot detect that the overall goal (network error reporting vs file reading) is completely different.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may label this as a clone due to overlapping I/O boilerplate and similar control flow (try-catch, BufferedReader), but the actual functionality differs significantly.
- 共享行为: Both use try-catch blocks for IOException；Both involve reading/writing data using streams
- 行为差异: A sends data over network; B reads from local file；A uses URLConnection and OutputStreamWriter; B uses FileInputStream or URL.openStream；A returns void; B returns String；A prints response; B exits on failure
- 修正建议: Incorporate dataflow analysis to track variable usage and output；Use contrastive learning with negative samples that have high token overlap but different semantics；Enhance understanding of API call sequences and their purpose

### case_id=957 FN benchmark_preference_bias

- 方法: `MotixFileItem` vs `modifyApplicationMessage`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Constructs a MotixFileItem by reading an input stream into memory and optionally extracting a BufferedImage.
- B 摘要: Modifies a localized properties file by reading, editing, and writing back content.
- 静态失败原因: Static BERT/GraphCodeBERT likely focused on semantic differences (method names, operations) leading to non-clone prediction, disagreeing with BCB's broad annotation based on I/O patterns.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider them clones under broad Type-3/Type-4 because both perform I/O operations, stream copying, and file handling, even though the functional purpose differs.
- 共享行为: Both involve reading from input streams or files and writing to output (byte array or file).
- 行为差异: Different domains (file item vs. properties editing)；Different data structures and processing logic；Different overall goals (storage vs. modification)
- 修正建议: Refine BCB annotation to exclude overly broad clones；Adjust model sensitivity to I/O patterns if matching BCB preference is desired

### case_id=958 FP lexical_or_api_overlap

- 方法: `getVersion` vs `issueCommandToServer`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches a version string from a remote URL by reading the first line.
- B 摘要: Sends a POST command with parameters to a server URL and returns the combined response.
- 静态失败原因: Static BERT models (e.g., GraphCodeBERT) rely heavily on token-level patterns and may overemphasize common lexical elements like 'URL', 'URLConnection', 'BufferedReader', 'readLine', leading to a false positive. They miss the structural and semantic differences such as write operations, parameter handling, and different return semantics.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels as non-clone because the functions serve different purposes (version retrieval vs command execution), have different method signatures, and different control flow patterns. Despite superficial similarity in using URLConnection and BufferedReader, the core functionality (one simple GET, one complex POST with writing) differs significantly.
- 共享行为: Both open a URL connection and read lines from the input stream.
- 行为差异: A is a static GET method for a single value; B is an instance method that writes to the output stream (POST) and reads multiple lines.；A returns null on exception; B throws IOException.；A does not send any data; B sends encoded parameters.；A reads only the first line; B reads all lines into a StringBuffer.
- 修正建议: Include more context about method signatures and data flow (output vs input only).；Train with contrastive examples that distinguish GET vs POST patterns.；Incorporate structural features like sequence of operations (e.g., detection of write before read).

### case_id=959 FN benchmark_preference_bias

- 方法: `main` vs `copy`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.85`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Extracts all entries from a ZIP file retrieved from a URL and writes each entry to a separate file.
- B 摘要: Copies a single file from one path to another using NIO FileChannel.
- 静态失败原因: The static model likely relied on lexical/syntactic overlap and structural differences, which were low (token Jaccard 0.1486), and correctly identified the semantic gap between ZIP extraction and file copying, leading to a non-clone prediction. However, this did not align with the BCB annotation that accepted broader similarity.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider both as performing a 'copy' operation (extracting archive entries to disk vs copying a file), thus viewing them as functionally similar under a broad Type-4 clone classification, or the annotation may be an error.
- 共享行为: Both involve reading from an input source and writing to an output file.
- 行为差异: Different input sources: URL with ZIP vs local file path.；A handles multiple entries, B copies a single file.；A uses ZipInputStream and BufferedOutputStream, B uses FileChannel.transferTo.；A throws Exception broadly, B uses nested finally blocks for resource cleanup.
- 修正建议: Increase training data with broad functional similarity examples.；Incorporate task-level embeddings to recognize common I/O patterns.；Adapt model to match BCB annotation guidelines by considering partial functionality similarity as clone.

### case_id=960 FN partial_functionality

- 方法: `getResourceAsStream` vs `internalCopy`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Retrieves a resource as an InputStream, with caching and HTTP handling.
- B 摘要: Copies a source file to a destination file, skipping 'Thumbs.db'.
- 静态失败原因: The static model likely relied on token-level similarity and structural features, which are low (token Jaccard 0.1869). It may have been misled by the different method names, the length disparity, and the unique URL/caching code in A, missing the shared I/O pattern due to lack of dataflow awareness.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider this a clone because both functions perform the core common operation of copying data from an input stream to an output stream using buffered I/O, which is the essential functionality of internalCopy and a significant part of getResourceAsStream. The additional logic in getResourceAsStream is seen as surrounding infrastructure, not changing the core cloning behavior.
- 共享行为: Both use buffered streams to copy data from an InputStream to an OutputStream.；Both close streams after copying.
- 行为差异: A includes URL retrieval, caching logic, HTTP connection handling, and conditional checks; B is a straightforward file copy.；A returns an InputStream (or null); B is void.；A reads byte-by-byte; B reads in chunks using a buffer.；A has extensive error handling with multiple catch blocks; B throws exceptions.
- 修正建议: Use dataflow or graph-based models that can identify the common I/O pattern despite surrounding differences.；Incorporate broader context and focus on behavioral rather than lexical similarity.

### case_id=961 FP lexical_or_api_overlap

- 方法: `handleHandshake` vs `startScript`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Handles Minecraft handshake packet by validating server key via HTTP request.
- B 摘要: Loads a script from a URL into a dialog.
- 静态失败原因: Static BERT may have focused on overlapping API tokens (BufferedReader, URL, openStream) and overlooked different control flow and semantics.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled non-clone because the functions have different purposes and logic, despite similar API usage.
- 共享行为: Both read from a URL using BufferedReader
- 行为差异: A has complex validation logic, B simply reads all lines；A uses HTTP response to decide next actions, B accumulates script；A includes network shutdown calls, B ends script
- 修正建议: Train with more diverse examples emphasizing semantic equivalence over token similarity；Incorporate control flow and data flow features

### case_id=962 FP lexical_or_api_overlap

- 方法: `doVersionCheck` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Downloads a version check file from a URL, parses lines prefixed with .version and .build, and compares the build number to determine if a new version is available.
- B 摘要: Performs a Google image search for the current track's artist and album, downloads the HTML response, extracts image URLs from href attributes containing '/imgres?imgurl=', and adds them to a list.
- 静态失败原因: The static BERT model likely overemphasized the lexical and API overlap (URL, openStream, BufferedReader, while readLine) and ignored the distinct domain-specific logic and method names, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would label these as non-clones because their core functionalities are entirely different (version checking vs. image searching); the structural similarity in URL reading is incidental boilerplate.
- 共享行为: Both open a URL connection and read lines from an input stream using BufferedReader.
- 行为差异: A parses specific key-value pairs (.version, .build) and compares build numbers; B constructs a search query, handles spaces, sets user-agent, concatenates the entire HTML, then splits and extracts URLs.；A has error handling for IOException; B catches a general Exception and shows an error dialog.；A shows a cursor wait indicator; B does not.；A uses properties from jEdit; B uses fields like artist, previousArtist, currentTrack.
- 修正建议: Incorporate method name semantics or task-context embeddings.；Use dataflow analysis to capture the different transformations applied to the read data.；Include features that discriminate between different types of URL-based data fetching (e.g., version check vs. image search).

### case_id=963 FN partial_functionality

- 方法: `copyResource` vs `doFinishLoadAttachment`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource from a URL or file to a destination file using byte-wise streaming.
- B 摘要: Handles loading an attachment; if saving is requested, copies the attachment content from a content URI to a file, otherwise launches an intent to view it.
- 静态失败原因: Low lexical overlap (Jaccard 0.115) and different method names; static embedding models rely on token matching and may miss the structural similarity of the stream copy pattern, especially due to conditional branches in B.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as implementing a 'stream copy' pattern, which is a common functionality. Despite different contexts, the core copying logic is similar enough for a Type-3 clone (with some modifications).
- 共享行为: Both involve reading an input stream and writing to an output stream (data copying).
- 行为差异: A is a generic copy utility; B is specific to attachments with conditional logic (save vs. view).；B includes error handling with toasts, media scanning, and intent launching; A has none.；A uses a while loop; B uses IOUtils.copy.
- 修正建议: Use a model that focuses on subgraph semantics, e.g., compare data-flow subgraphs related to stream I/O.；Incorporate control-flow and data-flow analysis to detect partial functionality clones.

### case_id=964 FN partial_functionality

- 方法: `getHTML` vs `fetchUrl`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches HTML from a URL with specified encoding and User-Agent, optionally writes to a file, and returns the content with line separators.
- B 摘要: Fetches URL content as a string without additional headers or encoding, returning empty string on error.
- 静态失败原因: The model likely focused on structural and lexical differences (e.g., presence of file writing, different error handling, newline appending) and the low token Jaccard (0.33) may have led it to predict non-clone. The model may not capture that the additional file-writing is optional and that the main functionality is similar.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often classifies functions as clones if they share a common high-level purpose, even with minor variations in parameters or additional optional behavior. The core operation of fetching and returning URL content is identical, so BCB likely considers this a clone.
- 共享行为: Both retrieve textual content from a URL via HTTP and return it as a String.
- 行为差异: Function A adds "\r\n" after each line, while B does not.；Function A optionally writes the content to a file if a directory path is provided.；Function A uses a specific User-Agent header and allows encoding configuration; B uses default settings.；Error handling differs: A prints stack trace and disconnects, B returns empty string silently.
- 修正建议: The model could benefit from distinguishing core behavior from auxiliary features, e.g., by considering optional branches.；Use structural alignment techniques that ignore extra conditional blocks or parameter handling.；Incorporate API usage patterns (e.g., URL.openStream vs HttpURLConnection) similarity.

### case_id=965 FN lexical_or_api_overlap

- 方法: `fileDownload` vs `httpRequestByPOST`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a file from a URL and saves it to a local directory, with hardcoded filename 'download.pdf'.
- B 摘要: Performs an HTTP POST request with parameters, returns the response body as a string, handling errors with return null and storing error codes.
- 静态失败原因: Low token overlap (Jaccard=0.14) and different API usage (URLConnection vs HttpClient) mislead lexical- and structure-based models to classify as non-clone.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB might have labeled this as clone due to both functions involving HTTP network communication and reading response content, possibly under a broad 'URL fetching' category, despite different methods and output handling.
- 共享行为: Both open an HTTP connection and read data from an input stream using BufferedReader
- 行为差异: A uses URLConnection (implicit GET) and writes bytes to a file; B uses HttpClient with POST and returns string；A ignores HTTP status and always writes output; B checks status and returns null on error or non-2xx；A reads character-by-character; B reads line-by-line；A does not return anything; B returns response string
- 修正建议: Incorporate dataflow analysis to track I/O operations across different libraries；Use graph-based models that capture semantic similarity of network operations；Augment training data with diverse API implementations of similar tasks

### case_id=966 FN benchmark_preference_bias

- 方法: `doGet` vs `copy`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Handles HTTP GET requests for displaying pages with permission checks and caching.
- B 摘要: Copies a file using NIO FileChannel and MappedByteBuffer.
- 静态失败原因: If BCB considers this a clone, a static BERT model likely failed due to the extremely low token overlap and different domain vocabulary, making it correctly predict non-clone; the model did not find any semantic similarity.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB label might be an error, or possibly they considered both methods involve writing to files (A writes cache files), but that is a minor part of A; the core functionalities are entirely different.
- 共享行为: No significant shared behavior
- 行为差异: A is an HTTP servlet method handling page requests; B is a file copy utility；A involves complex page retrieval, user permissions, logging, caching; B is a straightforward I/O operation；A uses many external classes (Page, Property, PortalRequest); B uses only java.nio and File
- 修正建议: Verify annotation correctness; if label is wrong, correct it；Otherwise, train models to recognize very broad behavioral similarities like 'writing to file' which might be considered clone under BCB guidelines

### case_id=967 FP boilerplate_overlap

- 方法: `readReferenceText` vs `importSequences`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a reference text file from a URL and returns its entire content as a string.
- B 摘要: Imports sequences from a URL in FASTA format, parsing names and sequences into lists.
- 静态失败原因: The static BERT method likely focused on high-level structural patterns (try-catch, URL openStream, BufferedReader, while loop) and overlooked the deeper semantic differences in the loop body and data processing, leading to overconfidence from boilerplate overlap.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely considered these non-clones because the core functionality differs significantly: one is a generic file reader, the other is a domain-specific sequence parser. Despite common I/O patterns, the intent and data handling are distinct.
- 共享行为: Both open an InputStream from a URL and read text line by line.；Both handle IO exceptions with catch blocks.
- 行为差异: A returns a single concatenated string of the entire file; B parses structured FASTA data into two lists.；A reads all lines until EOF; B reads until no more '>' delimiters and uses a custom ImportHelper.；A throws a custom NoContentException on failure; B catches and ignores EOFException silently.
- 修正建议: Incorporate dataflow analysis to distinguish between simple file reading and structured parsing.；Use finer-grained AST or control-flow comparison to differentiate loop logic and exception handling behavior.

### case_id=968 FN benchmark_preference_bias

- 方法: `logging` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Logs inbound message by copying input stream to a cached output stream and writing to buffer.
- B 摘要: Retrieves a resource from a URL, caches it locally, and returns an input stream.
- 静态失败原因: GraphCodeBERT likely focused on low token overlap (0.094), different method names and overall structure, leading to a non-clone prediction; it did not capture any broad behavioral similarity that BCB might assume.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider both as utility functions that read and process input streams with error handling, but they serve fundamentally different purposes.
- 共享行为: Both handle InputStream objects；Both involve exception handling for I/O operations
- 行为差异: Function a logs message; function b downloads and caches files；Function a uses CachedOutputStream; function b uses HTTP connection and file cache；Function a is purely logging; function b returns an InputStream from cache or network
- 修正建议: Re-evaluate BCB annotation for this pair；Consider stricter clone criteria to avoid over-generalizing stream handling patterns

### case_id=969 FN long_range_semantics

- 方法: `actionPerformed` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads SNP IDs from a gzipped file and sends them to NCBI via HTTP POST, outputting the response to stderr.
- B 摘要: Transforms a set of pages by reading XML files, applying XSLT, performing string replacements, and writing the result to output files.
- 静态失败原因: The low token overlap and long-range semantics of these complex functions likely caused the static model to miss the claimed behavioral similarity, as it relies heavily on local syntactic patterns.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB might consider broad Type-4 similarity due to both functions processing data from external sources and performing I/O, but the functional purposes are too disparate to be considered clones even under relaxed criteria.
- 共享行为: Both contain I/O operations with file and HTTP streams；Both use exception handling for IOException；Both involve looping over input data
- 行为差异: Code_a is a simple HTTP client for SNP retrieval; code_b is a complex site-building pipeline；Code_a reads from a local gzip file; code_b reads XML from various sources；Code_a writes to System.err; code_b writes to output files via a FileSystem utility；Code_b performs XML transformation and string replacement; code_a does not transform data
- 修正建议: Incorporate data-flow and control-flow analysis to capture high-level behavior；Use graph-based code representations to model long-range dependencies；Augment training data with diverse Type-4 clone examples

### case_id=970 FN partial_functionality

- 方法: `httpRequestByPOST` vs `issueCommandToServer`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends an HTTP POST request using HttpClient, reads response if status <400, else sets error fields and returns null.
- B 摘要: Sends an HTTP POST request using URLConnection, writes command and capsule data, reads response, throws IOException on error.
- 静态失败原因: The static model likely relied on lexical and surface-level features, which differ significantly (low token Jaccard, different APIs), missing the semantic similarity in the overall HTTP POST pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels Type-4 clones where the core functionality (HTTP POST and response reading) is similar despite different implementations and error handling.
- 共享行为: Both perform HTTP POST requests；Both read the response into a String；Both use URL encoding for parameters；Both return the response string on success
- 行为差异: Function A uses HttpClient, B uses URLConnection；Function A checks HTTP status code, B does not；Function A catches IOException and sets error fields, B throws IOException；Function A takes a list of params, B constructs content manually
- 修正建议: Use dataflow or graph-based models that capture the core behavior；Augment training with more Type-4 examples；Incorporate API usage patterns

### case_id=971 FN partial_functionality

- 方法: `modifyApplicationMessage` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Modifies or adds a key-value pair in a locale-specific properties file, copying the English file if needed.
- B 摘要: Copies a file from source to destination using NIO FileChannels.
- 静态失败原因: Static BERT models rely on token overlap (Jaccard=0.0957) and method name similarity; they missed the shared file I/O sub-task due to different APIs (Properties vs FileChannel) and low textual similarity, failing to recognize the partial functional equivalence.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB's annotation guidelines consider broad functional similarity, including Type-3/Type-4 clones where one function's sub-behavior (file copy) matches the other's entire behavior, thus labeling as clone despite different primary purposes.
- 共享行为: Both perform file I/O operations (reading and writing).；Both handle file copying as part of their logic (function A copies a properties file if missing, function B is purely a file copy).
- 行为差异: Function A is specific to properties files and involves parsing lines, matching keys, and modifying text; function B is a generic byte-level file copy.；Function A includes conditional logic to create a locale file by copying an English template; function B always copies from explicit source to destination.；Function A uses character streams and string processing; function B uses NIO channels for efficient binary transfer.
- 修正建议: Incorporate dataflow analysis to capture that both functions perform file write operations.；Use contrastive learning examples where one function is a sub-task of another.；Enhance representation with control-flow and data-dependency graphs to see common I/O patterns.

### case_id=972 FP lexical_or_api_overlap

- 方法: `getLinksFromURLFast` vs `writeFileType`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Extracts all hyperlinks and anchor texts from a given URL using regex and returns them as a pair of vectors.
- B 摘要: Reads URIs from a file, fetches each web page, checks for RDF/OWL/RDFS tags, and writes the URI and its type to an output file.
- 静态失败原因: The model likely over-emphasized the lexical overlap of common Java I/O and URL classes (URLConnection, BufferedReader, readLine, while loops) and ignored the different processing logic inside loops and the different outputs, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: None
- 共享行为: Open URL connections and read HTML content line by line；Use while loops to process lines from a reader；Involve string matching (regex or indexOf) on lines；Handle exceptions with try-catch blocks
- 行为差异: Function a returns extracted links and texts; function b writes classification results to a file；Function a processes a single URL; function b processes multiple URLs from a file；Function a uses regex extensively for link extraction; function b uses simple indexOf for ontology keyword detection；Function a outputs two vectors; function b has no return value and writes to a file
- 修正建议: Incorporate data-flow analysis to track how input is transformed across the function；Add training examples that distinguish between boilerplate code and core logic；Use structure-aware attention that focuses on the inner loop logic rather than outer scaffolding

### case_id=973 FP boilerplate_overlap

- 方法: `downloadURLtoString` vs `checkForUpgrade`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Downloads a URL's content and returns it as a string by reading lines into a buffer.
- B 摘要: Checks for software upgrades by querying a server, validating license, updating database, and managing UI components.
- 静态失败原因: The model likely focused on the overlapping lexical tokens related to URL reading (BufferedReader, readLine, openConnection) and missed the surrounding distinct business logic, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically requires significant similarity in core functionality; here only a trivial I/O pattern overlaps, and the overall purposes are distinct.
- 共享行为: Open a URLConnection and read lines via BufferedReader
- 行为差异: Function A returns a simple string; Function B has void return with complex side effects；Function A has no database or UI interaction; Function B performs SQL queries and UI visibility changes；Function B includes license validation and upgrade processing logic absent in A
- 修正建议: Incorporate data flow analysis to distinguish primary computations from boilerplate；Use attention masking to de-emphasize common I/O patterns；Train on finer-grained semantic labels that differentiate overall purpose

### case_id=974 FN partial_functionality

- 方法: `loadDefaultSettings` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Loads default configuration properties from a classpath resource to a file output stream.
- B 摘要: Builds a website for editing by iterating over pages, transforming XML, and writing to output files.
- 静态失败原因: The static model likely focused on the low token overlap and distinct method names, concluding they are semantically different, while BCB considered them clones based on partial functionality similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled as clone due to both methods performing file I/O operations with similar resource management patterns (try-catch-finally with streams), even though the overall functionality differs.
- 共享行为: Both involve reading from an input stream and writing to an output stream (file I/O).
- 行为差异: A is a simple file copy utility; B is a complex site builder with XML transformation, FTP, and page processing.；A has a single try-catch; B has many exception handling blocks and conditional logic.；A uses IOUtils.copy; B uses custom file system methods.
- 修正建议: Improve model to consider broader functional equivalence beyond exact token overlap.；Incorporate more context about resource management patterns.

### case_id=975 FN benchmark_preference_bias

- 方法: `createOutputStream` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Creates a BufferedWriter that re-zips an input file, skipping and then replacing a content.xml entry with UTF-8 encoding.
- B 摘要: Launches a NexOpen project configuration by checking project files, processing pom.xml configurations, setting Hibernate dialect, and triggering an install action.
- 静态失败原因: The static BERT model likely correctly identified these as non-clones due to low token overlap and clear semantic differences, but the BCB label indicates a false negative. The model's failure is due to the unexpected BCB annotation rather than a model limitation.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled these as clones based on very broad functional similarity, such as both methods 'processing' resources (a zip file vs. a project), or due to annotator error. BCB's annotation guidelines sometimes accept Type-4 clones with minimal shared behavior.
- 共享行为: Both methods involve file I/O operations and use streams.
- 行为差异: Function A is a utility for manipulating zip files; Function B is an Eclipse launch handler for project configuration.；Function A returns a BufferedWriter; Function B returns void and has side effects on the workspace.；Function A uses ZipInputStream/OutputStream; Function B uses XML parsers and Eclipse resources API.；Function A has a loop over zip entries; Function B has conditional checks and callback processing.
- 修正建议: Review the BCB annotation for this pair to verify if it is indeed a clone; if not, correct the dataset label.；If BCB intended a broad clone, the model may need to incorporate higher-level functional similarity features beyond token overlap.

### case_id=976 FP lexical_or_api_overlap

- 方法: `callService` vs `readUNI`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads entire content from a constructed URL and stores it in an instance variable, with error handling.
- B 摘要: Parses tab-separated lines from a given URL and populates a vector with id and description pairs.
- 静态失败原因: The static model likely focused on the common API sequence (URL, openStream, while-read-line, close, try-catch) and structural patterns, ignoring the divergent data processing logic and output storage. This lexical and API overlap led to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the functions serve different purposes: one is a generic URL reader returning full text, the other is a specific tabular data parser. The low token overlap and distinct output semantics make them functionally dissimilar even under broad Type-4 criteria.
- 共享行为: Both open a URL connection and read data line by line；Both handle IO and MalformedURL exceptions；Both close the opened stream
- 行为差异: A constructs URL from instance variables, B uses a parameter；A reads entire file as a single string, B parses specific fields from each line；A stores result in an instance variable, B populates a passed vector；A sets error messages, B has empty catch and prints stack trace
- 修正建议: Incorporate data flow analysis to distinguish output types and storage patterns；Add features capturing parameter and return type semantics；Use contrastive learning to penalize high API overlap when local processing differs

### case_id=977 FP boilerplate_overlap

- 方法: `getFileContentAsString` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a file from classpath or file system and returns its content as a string.
- B 摘要: Handles UI action events, opening file choosers and updating application preferences.
- 静态失败原因: The static model might have been fooled by common structural elements like try-catch blocks, I/O operations, or method length, leading to a false positive due to high-level structural similarity in some parts (e.g., both have file handling patterns) but ignoring the core logic differences.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clone because the functions have entirely different purposes (file reading vs UI event handling) and no significant structural or behavioral similarity.
- 共享行为: Both use try-finally blocks；Both handle exceptions；Both perform string operations
- 行为差异: Function A reads file content; function B handles UI events；Function A is a utility method; function B is an event handler manipulating UI state；Function A uses IOUtils.copy; function B uses JFileChooser and setting preferences
- 修正建议: Improve model ability to distinguish utility I/O methods from event handlers；Include more context such as method names and surrounding class context；Use dataflow analysis to capture the actual behavior beyond structural patterns

### case_id=978 FN benchmark_preference_bias

- 方法: `readAndRewrite` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Reads a DICOM image file, decodes pixel data, and writes it to another DICOM file.
- B 摘要: Builds a website by transforming XML pages with XSLT, processing templates, and writing HTML files.
- 静态失败原因: Static BERT models correctly identified no semantic equivalence due to very low token Jaccard similarity (0.036) and completely different domain-specific terms and API calls.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled these as clones due to broad structural similarity (both are long, perform I/O transformations, and follow a read-process-write pattern), but this is a very loose interpretation that likely overgeneralizes.
- 共享行为: Both perform file I/O (reading input and writing output).；Both throw IOException.；Both use print statements for debugging/tracing.
- 行为差异: Different domains: medical imaging vs web publishing.；Different data formats: DICOM vs XML/HTML.；Different processing logic: pixel data decoding vs XSLT transformation and string manipulation.；Different class hierarchies and APIs used.
- 修正建议: Improve clone annotation guidelines to require more specific functional similarity beyond generic I/O patterns.；Use more fine-grained clone types (e.g., Type-1/2/3/4) and ensure Type-4 clones have clear semantic overlap.

### case_id=979 FP lexical_or_api_overlap

- 方法: `init` vs `getRequestContent`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Initializes controllers by loading class names from a registry file resource.
- B 摘要: Reads the first line from an HTTP URL response.
- 静态失败原因: The model likely overemphasized the common API tokens (URL, BufferedReader, InputStreamReader, readLine) and syntactic structure, ignoring the distinct method names and overall functionality.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would label them as non-clones because their high-level purposes (initialization vs HTTP request) are completely different, despite low-level API overlap.
- 共享行为: Both use BufferedReader and InputStreamReader to read from an input stream；Both handle exceptions
- 行为差异: A loads classes from classpath resources, B fetches HTTP content；A iterates over multiple URLs, B handles a single URL；A modifies servlet context, B returns a string
- 修正建议: Incorporate method name and context information into the representation；Use data flow analysis to capture transformation of data；Train with more negative examples that share common APIs but have different intents

### case_id=980 FP lexical_or_api_overlap

- 方法: `copyFile` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Copies a file from source to destination using a buffered stream.
- B 摘要: Handles action events for a settings dialog, updating preferences and GUI components.
- 静态失败原因: Likely due to lexical overlap of common tokens like 'File', 'getAbsolutePath', and 'IOException' (though B does not have IOException), leading the model to incorrectly perceive similarity despite divergent semantics.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clone because the two methods have completely different purposes (file copy vs. GUI event handling) with no significant functional overlap, even under broad Type-3/Type-4 criteria.
- 共享行为: Both involve the use of File objects and file paths, but in entirely different contexts (file I/O vs. GUI preferences).
- 行为差异: Function A performs file copy with stream I/O; Function B handles GUI events and updates application settings.；Function A is a pure utility method; Function B is a long event handler with many conditional branches.；Function A uses try-finally for stream cleanup; Function B uses try-catch for exception handling.
- 修正建议: Enhance model with program flow analysis or data-flow graphs to capture actual operations.；Use contrastive learning with hard negative examples that share tokens but differ in behavior.；Incorporate method-level summarization or API call sequences to distinguish utility from GUI code.

### case_id=981 FN partial_functionality

- 方法: `copyResource` vs `transport`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource (URL or file) to a destination file with byte-by-byte stream reading.
- B 摘要: Recursively copies files and directories to a destination directory using NIO FileChannel.
- 静态失败原因: Low token Jaccard (0.15873) and very different syntactic structure, method names, and APIs (InputStream vs FileChannel) led the model to miss the underlying functional similarity of file copying.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels Type-4 clones with partial functional similarity, and both functions perform the core task of copying file content from source to destination, despite differences in APIs, error handling, and directory handling.
- 共享行为: Both copy file content from a source to a destination.；Both check for file existence before copying.；Both use output file streams to write data.
- 行为差异: copyResource handles URLs and local files; transport handles only local files.；copyResource does not handle directories; transport recursively copies directories.；copyResource throws exceptions; transport logs errors.；copyResource uses InputStream/OutputStream byte copies; transport uses FileChannel.transferTo.
- 修正建议: Augment training data with cross-API file copy examples.；Incorporate data flow or program dependence analysis to capture I/O equivalence.；Use code summarization models to compare high-level intent.

### case_id=982 FN partial_functionality

- 方法: `runScript` vs `CheckUrl`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads entire content of a script file from a URL byte by byte and returns it as a string, returning 'error!' on failure.
- B 摘要: Opens a URL connection and returns the first line of the response as a string, returning an empty string on failure after printing stack trace.
- 静态失败原因: Static models rely on surface features like token overlap (Jaccard=0.25) and method names, which differ significantly; they miss the shared high-level purpose.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels clones based on high-level functional similarity (Type-4), such as fetching URL content as a string, despite differences in implementation details.
- 共享行为: Both fetch data from a URL and return it as a string
- 行为差异: runScript reads all bytes; CheckUrl reads only first line；runScript returns 'error!' on exception; CheckUrl returns empty string and prints stack trace
- 修正建议: Include more diverse URL-fetching implementations in training data；Use data flow analysis to recognize similar data transformations across different I/O patterns

### case_id=983 FN partial_functionality

- 方法: `doGet` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Handles HTTP GET request to retrieve and serve a web page with visibility checks, logging, and caching.
- B 摘要: Command-line tool that parses arguments, reads input file with specified encoding, and writes converted content to output file.
- 静态失败原因: Static models like CodeBERT rely on token overlap and structural similarity, which are low between these functions (0.128 Jaccard). They fail to recognize abstract functional patterns that require understanding the overall control flow and purpose.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label them as clones due to a shared abstract pattern of input parsing, default value handling, conditional branching, error handling, and output generation, fitting a Type-4 (functionally similar) classification.
- 共享行为: Parse input to determine action (parameter vs command-line args)；Set default values when input is missing or invalid；Perform conditional checks and error handling；Produce output (HTTP response vs file write)
- 行为差异: Input source: HTTP request parameter vs command-line arguments；Output target: HTTP response vs file system；Core logic: page lookup, visibility, caching vs character encoding conversion；APIs used: Servlet, PortalRequest, Page vs CmdLineParser, File I/O
- 修正建议: Use dynamic analysis or execution traces to capture behavioral equivalence.；Train models on abstract syntax trees or control flow graphs with node embedding.；Incorporate functional annotations or API usage patterns to detect high-level similarity.

### case_id=984 FP lexical_or_api_overlap

- 方法: `doVersionCheck` vs `downloadModel`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Performs a version check by reading a URL and parsing build numbers, then showing error dialogs on failure.
- B 摘要: Downloads an RDF model from a URL by setting HTTP headers and reading the response into a model object, throwing runtime exceptions on failure.
- 静态失败原因: The model likely over-relied on lexical/API overlap (e.g., URL, InputStream, try-catch, close) and structural similarity of the try-catch pattern, ignoring the distinct core logic and method names.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels non-clones when functions have distinct functional purposes despite similar I/O boilerplate; here one is a version checker and the other a model downloader, so they are considered functionally different.
- 共享行为: Both open a URL and obtain an InputStream；Both handle IOException with custom error handling；Both close the input stream after reading
- 行为差异: A reads line-by-line and checks for specific prefixes; B reads the entire stream into a model object；A shows/hides a wait cursor and calls GUIUtilities.error on failure; B logs and throws RuntimeException；A returns void; B returns a Model object；A sets no HTTP headers; B sets Accept and Accept-Language headers
- 修正建议: Incorporate method name and context (e.g., version check vs download) into the representation；Use dataflow analysis to capture what operations are performed on the read data；Train on functional similarity beyond API sequence, e.g., by abstracting I/O boilerplate

### case_id=985 FP lexical_or_api_overlap

- 方法: `writeFileToFile` vs `readData`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Copies content from one file to another using FileChannel transferTo.
- B 摘要: Reads configuration strings and populates multiple sets and hash maps for Tibetan transliteration.
- 静态失败原因: Static BERT models may have over-relied on surface-level similarities such as both containing 'File' and 'IOException', or both having try-catch blocks, while missing the distinct functional contexts.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely would not consider these clones because they accomplish entirely different tasks (file copy vs. data initialization) despite both involving file I/O.
- 共享行为: Both involve file I/O operations and exception handling.
- 行为差异: writeFileToFile copies bytes from one file to another; readData parses string tokens and populates data structures.；writeFileToFile uses NIO channels; readData uses StringTokenizer and file reading.；writeFileToFile appends or overwrites; readData only reads.；readData has extensive data structure initialization, while writeFileToFile has none.
- 修正建议: Improve models to focus on function-level data flow and call structure rather than token overlap.；Incorporate structural information like control flow and data dependencies to distinguish between distinct operations.

### case_id=986 FP lexical_or_api_overlap

- 方法: `sendPost` vs `loadMFileViaWeb`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Sends an HTTP POST request with parameters and returns the response body as a string.
- B 摘要: Loads a MATLAB .m file from a web URL, reads its content line by line, parses it into a UserFunction object, and returns it.
- 静态失败原因: Static BERT/GraphCodeBERT may have been misled by the lexical overlap of common I/O tokens (URL, BufferedReader, readLine, try-catch, etc.) and the similar control flow structure. The model likely failed to capture the semantic distinction between sending data (POST) vs. receiving data (GET) and the subsequent parsing logic in function B.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the high-level functionality is completely different: one is sending data via POST, the other is fetching a file for parsing. Even though both involve reading from a URL, the purpose and output types differ significantly, which aligns with BCB's broad but functional-level annotation preferences.
- 共享行为: Open a URL and read its content line by line using BufferedReader.；Use try-catch to handle exceptions during network I/O.；Close the input stream after reading.
- 行为差异: Function A sends POST data via PrintWriter; Function B only reads (GET).；Function A returns the raw response string; Function B parses the content into a UserFunction.；Function A sets HTTP headers (Accept-Language); Function B does not.；Function B adds newlines when concatenating lines; Function A does not.
- 修正建议: Enhance training data with more contrasting examples of send vs. receive operations.；Incorporate data flow analysis to track usage of streams (output vs. input).；Use code summarization or method name embeddings to capture high-level intent.

### case_id=987 FN benchmark_preference_bias

- 方法: `getFile` vs `testStandardTee`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Downloads a WSDL file from a URL, modifies the endpoint in the XML, and saves it to a temporary file.
- B 摘要: Tests that a TeeWriter copies input from a StringReader to two StringWriters correctly.
- 静态失败原因: Static BERT correctly predicted non-clone (0), but BCB expected clone; the model did not fail in terms of semantic similarity detection, but rather disagreed with the benchmark label.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: The BCB label of 1 is likely a misannotation; possibly annotator considered both as involving I/O streaming, but this is too broad for Type-4 clone.
- 共享行为: Both involve I/O operations on streams
- 行为差异: Different purpose: file download vs unit test；Different APIs: AxisFault, URL, FileChannel vs TeeWriter, StringWriter；No common data flow or logic
- 修正建议: Re-annotate this pair as non-clone in the benchmark；Improve BCB annotation guidelines to avoid overly broad Type-4 criteria

### case_id=988 FP lexical_or_api_overlap

- 方法: `createDialogArea` vs `getFrameworkFactory`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Creates a dialog area for a license agreement, reading and displaying a license file in a Browser or Text widget.
- B 摘要: Reads a service configuration file to dynamically load and instantiate an OSGi FrameworkFactory.
- 静态失败原因: Static BERT likely overfitted on the common API sequence (URL.openStream, BufferedReader.readLine) and the structural similarity of reading loop, ignoring the surrounding context and method signatures.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB correctly labels non-clones because the functions have completely different purposes and outputs, despite sharing a common I/O pattern.
- 共享行为: Both open a URL and read from it using BufferedReader
- 行为差异: Function A is a UI method that sets up a dialog layout and displays static content; Function B is a factory method that loads a class and returns an instance.；Function A uses try-catch for Browser instantiation and fallback to Text; Function B throws an exception if factory not found.；Function A returns a Composite; Function B returns a FrameworkFactory.
- 修正建议: Incorporate method-level and class-level context (e.g., parent class, method name).；Use data-flow analysis to track how read data is used (display vs. reflection).；Add semantic role labeling for parameters and return types.

### case_id=989 FN benchmark_preference_bias

- 方法: `getFile` vs `genCustRatingFileAndMovieIndexFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies its 'location' attribute, and saves it to a temporary directory, returning the file path.
- B 摘要: Reads a binary file of 7-byte records, processes them to generate movie index and customer rating files, and returns a boolean success flag.
- 静态失败原因: Static BERT likely failed because it relied on token similarity, which is low (Jaccard=0.1059), and the high-level semantics differ completely; however, the BCB label is based on broad API usage patterns that the model is not trained to recognize as clones.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may label this as a clone because both functions perform file I/O with FileChannel and ByteBuffer, and both involve processing input to produce output files, fitting a broad Type-4 (semantic) clone category where any file processing task is considered similar.
- 共享行为: Both use FileChannel and ByteBuffer for file I/O operations.；Both read from an input file and write to output files using streams and channels.；Both handle IOException with logging or error output.
- 行为差异: Function A downloads a file over HTTP and parses XML; Function B reads a local binary file with fixed-size records.；Function A returns a file path string; Function B returns a boolean.；Function A modifies XML attributes using DOM parsing; Function B performs binary record reorganization.；Function A handles multiple exception types; Function B only handles IOException.
- 修正建议: Incorporate data flow analysis to capture task-level behavior beyond API calls.；Use graph-based representations that model program logic and data transformations.；Train with more diverse clone types to avoid overvaluing low-level token overlap.

### case_id=990 FP lexical_or_api_overlap

- 方法: `handleHandshake` vs `downloadModel`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Handles a Minecraft handshake packet by validating a server key and optionally joining a session server.
- B 摘要: Downloads an RDF model from a URL using HTTP and reads it into a Model object.
- 静态失败原因: Static BERT likely over-relied on lexical and API-level cues (e.g., URL, InputStream, try-catch) without capturing the distinct domain contexts and control flows, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels as non-clone because the functions serve entirely different purposes in separate domains (Minecraft networking vs. RDF model download), with no shared functionality beyond basic I/O patterns.
- 共享行为: Both open a URL and read input from the connection.；Both use try-catch for exception handling.
- 行为差异: Function A validates a handshake packet and interacts with Minecraft session server; Function B downloads a model and reads RDF data.；Function A includes conditional logic for username validation; Function B has no such logic.；Function A has multiple failure paths with specific shutdown messages; Function B logs and throws RuntimeException.；Function A writes to a network queue; Function B returns a Model object.
- 修正建议: Include more training data with diverse tasks sharing only low-level I/O patterns to reduce API-based false positives.；Incorporate dataflow analysis or call-graph context to distinguish differing semantic intents.

### case_id=991 FN partial_functionality

- 方法: `main` vs `copy`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a hardcoded URL and extracts its zip entries to the current directory.
- B 摘要: Recursively copies a file or directory to a destination, handling subdirectories and files.
- 静态失败原因: Low token Jaccard (0.194) and different API calls (ZipInputStream/URL vs File streams/mkdirs) caused the model to miss the abstract semantic similarity of file copying.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this as a clone because both functions perform the abstract operation of copying data from an input source to output files, which can be considered Type-4 (semantic) similarity under a broad interpretation of functionality.
- 共享行为: Both involve reading data from a source (URL/network vs local file) and writing to files.；Both use while loops to read/write byte data.
- 行为差异: A is a fixed main method with no parameters; B is a generic method taking source and destination File objects.；A only handles a zip input stream from a URL; B handles both directories and regular files.；A lacks error handling; B includes try-catch-finally with logging.；A writes extracted entries to filenames from the zip; B writes to a specified destination path.
- 修正建议: Use models that capture program flow or data dependencies (e.g., GraphCodeBERT).；Increase training data with diverse implementations of file copying to learn abstract patterns.；Incorporate structural information like control flow graphs.

### case_id=992 FN partial_functionality

- 方法: `main` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a URL and extracts its zip entries to files.
- B 摘要: Copies files from one directory to another using NIO FileChannel.
- 静态失败原因: Static BERT/GraphCodeBERT likely correctly identified the semantic difference (download+unzip vs local copy) and thus predicted non-clone, aligning with strict equivalence. It did not fail in the strict sense but may lack sensitivity to high-level functional similarity that BCB uses.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB might consider both as file I/O operations with similar loop structures (reading/writing chunks), possibly labeling them as Type-4 (similar functionality despite different implementations) or broad Type-3 (syntactically similar due to common I/O patterns).
- 共享行为: Both read binary data from input sources and write to output files；Both involve loops processing multiple files/entries；Both use buffered I/O
- 行为差异: A involves network download and ZIP decompression; B is local file copy；A iterates over ZIP entries; B iterates over files in a directory；A writes entries to current directory; B writes to a specified destination directory
- 修正建议: Incorporate abstract I/O operation categories (e.g., compressed vs uncompressed) to capture broader clones；Use contrastive learning to recognize high-level functional similarity despite different APIs

### case_id=993 FN partial_functionality

- 方法: `modifyApplicationMessage` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Modifies a locale-specific properties file by updating or appending a message key-value pair, creating the file if necessary by copying a default English file.
- B 摘要: Copies a source file to a destination file using NIO FileChannel.
- 静态失败原因: Static BERT method likely focused on overall purpose and token overlap, which is low (0.14). It missed the implicit file copy sub-task due to different implementations (streams vs channels) and the conditional nature of the copy in A.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely annotated these as clones because both functions perform a file copy operation, a partial functional similarity. Even though the copy is a minor part of A, it is a recognizable common sub-task.
- 共享行为: Both involve copying file contents from an input to an output
- 行为差异: A's main purpose is message modification with conditional copy; B is solely file copy；A uses character streams (FileReader/FileWriter), B uses NIO FileChannel；A includes parsing and writing properties format, B does pure binary copy
- 修正建议: Enhance model to recognize sub-task composition and common I/O patterns；Incorporate dataflow analysis to identify file read/write operations；Consider function decomposition to isolate shared behaviors

### case_id=994 FN partial_functionality

- 方法: `copyResource` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource (URL or local file) to a destination file, using raw streams and throwing an exception on failure.
- B 摘要: Copies a file to another file, using buffered streams, creating the destination if necessary, and handling exceptions by printing stack traces and returning null.
- 静态失败原因: The low token Jaccard (0.25) and different method names, coupled with divergent API usage (URL vs File, buffered vs unbuffered) and error handling patterns, likely caused the static BERT model to miss the underlying algorithmic similarity. It may have overemphasized surface form differences.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB considers methods clones if they share the core algorithm (byte-by-byte copy), despite differences in error handling, buffering, return type, or source type. The essential behavior of copying content from one location to another is identical.
- 共享行为: Both read bytes from a source and write them to a destination file until end-of-stream.；Both use a loop reading one byte at a time and writing that byte.；Both close input and output streams after the copy operation.
- 行为差异: Source type: A can be a URL or local file; B only local file.；Buffering: A uses unbuffered streams; B uses buffered streams with 4KB buffer size.；Error handling: A throws an Exception; B catches FileNotFoundException and IOException, prints stack trace, and returns null.；Return type: A is void; B returns the destination File.
- 修正建议: Train models to recognize core algorithmic patterns (e.g., byte-by-byte copy loops) even when surrounding setup differs.；Use dataflow or control-flow features to capture the essential data transfer operation.；Include training examples with varied error handling, buffering, and input sources but same core copy logic.；Consider structure-based methods that align loops and stream operations.

### case_id=995 FN partial_functionality

- 方法: `doVersionCheck` vs `read`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Checks for a new version by reading a version file from a URL and comparing build numbers.
- B 摘要: Reads data from a file or URL and returns a status code after processing via another read method.
- 静态失败原因: The static BERT model likely failed due to low lexical overlap (token Jaccard 0.25) and different method signatures, return types, and control flows. The semantic similarity in URL reading pattern is not captured by shallow token embeddings, especially when the rest of the code differs significantly.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider them clones because both involve opening a URL stream and reading input with error handling, which is a common pattern. Additionally, both are part of file/resource reading operations, and the annotation guidelines might accept structural similarity at a high level.
- 共享行为: Both open a URL to read input；both handle IOException
- 行为差异: Function A parses version information and updates UI, while Function B reads raw data and returns status；Function A is static and takes a View parameter, Function B returns an int and takes a String；Function B handles both file and URL, while Function A only opens URL
- 修正建议: Augment training data with more diverse examples of URL reading patterns；Use structural features like AST or control flow graphs；Incorporate functional similarity based on I/O operations

### case_id=996 FN boilerplate_overlap

- 方法: `testNetworkHTTP` vs `writeFileType`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.75`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: A test method that makes multiple HTTP connections to various URLs and reads response lines without further processing.
- B 摘要: A utility method that reads a list of URIs from a file, fetches each URI's content, detects ontology language types, and writes results to an output file.
- 静态失败原因: The low token Jaccard (0.175) and different method names likely caused the static model to focus on lexical dissimilarity. The model may not capture the structural similarity in the boilerplate code patterns due to lack of AST/CFG information.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may label this as a clone due to the heavy structural similarity in the network I/O pattern (URL opening, stream reading, exception handling) which is a common boilerplate in Java. Even though the high-level purpose differs, the code follows a very similar template, which is a typical case for Type-3/Type-4 clones under BCB's broader criteria.
- 共享行为: Both open URL connections and read input streams line by line.；Both use BufferedReader and InputStreamReader for reading.；Both handle IOException via try-catch blocks.；Both involve reading data from HTTP sources.
- 行为差异: Method A is a test with hardcoded URLs; B reads URIs from a file.；Method A does not write any output; B writes classification results to a file.；Method A processes a fixed set of URLs; B processes a variable number of URIs based on input.；Method B classifies content based on specific markers (OWL, RDFS, RDF); A only reads lines without classification.
- 修正建议: Incorporate structural features from AST or data flow graphs.；Use model architectures that capture common programming patterns like try-catch and I/O idioms.；Augment training data with pairs that have low token overlap but high structural similarity.

### case_id=997 FP lexical_or_api_overlap

- 方法: `readUNI` vs `run`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a tab-separated file from a URL and populates a vector with id and description pairs.
- B 摘要: Reads lines from a URL and parses them into version, url, and informations fields with error handling and listener notification.
- 静态失败原因: Static BERT/GraphCodeBERT over-relied on lexical and API-level overlap (URL, openStream, try-catch) and missed semantic differences in parsing logic and output behavior.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels based on functional equivalence; these functions perform different tasks despite both reading URLs, so they are non-clones.
- 共享行为: Both read from a URL using InputStream；Both parse lines from the input；Both handle exceptions with try-catch-finally
- 行为差异: Different parsing logic: tab-separated vs. line-based state machine；Different outputs: vector vs. object fields；Different error handling: silent vs. error flags and listener notification；Different inputs: parameter vs. field
- 修正建议: Incorporate structural matching (e.g., AST or PDG) to capture control flow and data flow differences.；Use program slicing to isolate functional behavior beyond common I/O patterns.

### case_id=998 FN lexical_or_api_overlap

- 方法: `doTransfer` vs `addQDInformation`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Forwards an incoming HTTP request to another URL, copying headers and request body, then streaming the response back.
- B 摘要: Reads a local or remote file containing QD information, parses lines with 'pg ' and 'pt ' prefixes, and updates project info structures.
- 静态失败原因: GraphCodeBERT likely over-relied on overlapping API calls (URL, InputStream, IOException) and boilerplate try-catch structure, missing the distinct high-level purposes and data flows.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may have considered both as 'network data retrieval and processing' tasks, but the functionality is too different. Possibly a mislabel in BCB due to broad Type-4 similarity.
- 共享行为: Both use URL and URLConnection/InputStream to read data from a network source；Both handle IOException and catch exceptions；Both involve reading lines or streams of text
- 行为差异: Function A is an HTTP proxy that forwards requests and responses; Function B reads a specific data file format；Function A writes output to an HTTP response; Function B updates internal project info structures；Function A uses HttpURLConnection for full HTTP interaction; Function B uses simple URL.openStream() for one-directional reading；Function B has additional logic for local file fallback and parsing of key-value pairs
- 修正建议: Train model with more emphasis on program purpose and control flow, not just API usage.；Use task-specific data augmentation to distinguish between proxy and data-loading patterns.；Incorporate more context from method name and surrounding class.

### case_id=999 FN partial_functionality

- 方法: `getResourceAsStream` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Retrieves a resource by name, optionally caching it locally, and returns an InputStream.
- B 摘要: Copies a file from source path to destination path using FileChannel, returns success status.
- 静态失败原因: Static model likely focused on surface tokens and AST structure, which have low overlap (Jaccard 0.1468), leading to non-clone prediction. It missed the broader functional similarity that BCB perceives.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label these as clones due to both being I/O utility functions that manage streams and file operations, even though the specific functionalities differ.
- 共享行为: Open input and output streams；Read and write data between streams；Close resources in finally block；Handle exceptions with try-catch
- 行为差异: A returns InputStream, B returns boolean；A involves network and HTTP handling, B is purely local file copy；A reads from URL connection, B reads from FileInputStream；A writes to a cache file, B writes to a destination file
- 修正建议: Incorporate data flow and control flow into the model；Add contrastive training on partial functionality clones；Use method-level context including signature and documentation

### case_id=1000 FP boilerplate_overlap

- 方法: `googleImageSearch` vs `retrieveTemplate`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches Google image search results for a music track and extracts image URLs.
- B 摘要: Fetches a blog's HTML template and caches it.
- 静态失败原因: The model was likely misled by the common web-scraping boilerplate (open URL, read lines, append) and ignored the distinct post-processing and purpose.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels as non-clone because the overall functionality differs (image search vs. template retrieval), despite shared I/O boilerplate.
- 共享行为: Both open a URL and read the response line by line into a string；Both use BufferedReader and InputStreamReader；Both have a conditional guard before fetching
- 行为差异: Different URL construction (Google Images vs. blog URL)；Different post-processing: A parses for image URLs, B caches raw string；Different return types (void vs String) and error handling (try-catch vs throws)；Different context: A uses music track info, B uses blog editor info
- 修正建议: Enhance models to capture overall functionality via method names or comments；Use contrastive learning on pairs with similar boilerplate but different semantics
