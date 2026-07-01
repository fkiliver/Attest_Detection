# Error Case Studies 4001-4500

- Source model: `configured-llm`
- Cases: `4001` to `4500`

### case_id=4001 FN benchmark_preference_bias

- 方法: `doExecute` vs `getFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Handles multipart form submission, extracts email fields and attachments, and sends an email via a mail instance.
- B 摘要: Downloads a WSDL file from a given URL, modifies the endpoint in the XML, and saves it to a temporary directory.
- 静态失败原因: Static BERT correctly predicted non-clone (prediction 0) for this pair; it did not fail. The BCB annotation (1) appears to be a false positive.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have considered both functions as performing file-related I/O and network operations, but this interpretation is overly broad and not aligned with typical clone detection semantics.
- 行为差异: Function A processes HTTP multipart requests and sends emails; function B downloads and modifies WSDL files.；Function A uses Struts Action classes; function B is a static utility method for WSDL handling.；Function A involves complex form field parsing, file upload, and email sending; function B involves URL streaming, XML parsing, and file system operations.；Exception handling styles differ: A accumulates ActionMessages, B logs and throws AxisFault.
- 修正建议: Reevaluate BCB annotation for this pair; likely should be non-clone.；Ensure benchmark labels align with semantic equivalence rather than superficial API usage.

### case_id=4002 FP partial_functionality

- 方法: `readTwitterFead` vs `callService`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a Twitter timeline using Apache HttpClient and returns the response as a String.
- B 摘要: Calls a web service using URL.openStream() and stores the response in a field.
- 静态失败原因: The model likely overfitted on the common loop pattern (while ((line = in.readLine()) != null) append) and underestimated the differences in API usage (HttpClient vs URL) and return/value semantics.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB typically requires functional equivalence including return type and side effects; here one returns a String, the other sets a field, so they are not equivalent. Also the error handling and libraries differ significantly.
- 共享行为: Both perform an HTTP GET request to retrieve text data；Both read the response line by line using BufferedReader；Both handle IOException
- 行为差异: A returns the result, B stores it in an instance variable；A uses HttpClient library, B uses built-in URL；A has different error handling (logging vs. setting answer field)；A has a specific hardcoded URL, B builds URL from fields
- 修正建议: Include output type and side-effect analysis；Weight API signatures more heavily；Use dataflow analysis to distinguish return vs field assignment

### case_id=4003 FN partial_functionality

- 方法: `login` vs `callService`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Performs HTTP POST login to LOLA, sends email and password, reads response to extract session ID, returns session ID or empty string on error.
- B 摘要: Performs HTTP GET to a service endpoint, reads full response into a field, sets error message on exception.
- 静态失败原因: Static BERT models rely heavily on token and surface-level similarity; the low Jaccard index and different method names/operations led to false negative. They lack understanding of broader functional patterns like HTTP client calls.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB considers these clones likely because both are HTTP client routines that read a response, representing Type-4 (semantic) similarity in BigCloneBench, which often groups methods with similar high-level functionality despite syntactic differences.
- 共享行为: Both create a URL object and open a connection；Both read response data from an input stream；Both handle exceptions (though specifics differ)；Both close the stream after reading
- 行为差异: A uses POST with output data; B uses GET without output；A extracts a session ID from first line; B accumulates entire response；A returns a String; B sets a field and returns void；A prints debug messages; B does not
- 修正建议: Incorporate data-flow analysis to detect shared I/O patterns；Use graph-based representations capturing control and data flow of web requests；Train on more diverse Type-3/Type-4 examples from BCB；Consider domain-specific embeddings for common library operations

### case_id=4004 FN benchmark_preference_bias

- 方法: `copy` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.2`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Copies files or directories recursively, using NIO channels for file content and recursive calls for subdirectories.
- B 摘要: Builds a site for editing by reading XML and control files, applying XSLT transformations, and generating output HTML files.
- 静态失败原因: Static BERT models rely on lexical and structural patterns; low token overlap (0.08) and distinct method names and bodies led to a correct non-clone prediction, which is actually accurate.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have mislabeled this pair due to both methods involving file I/O, but the actual functionality is completely different; this appears to be a false positive in the BCB annotation.
- 共享行为: Both perform file I/O operations (reading and writing files).；Both handle IOException.
- 行为差异: copy focuses on duplication of files/directories; buildSiteForEdit generates transformed HTML from XML templates.；copy uses simple file channel transfer; buildSiteForEdit uses XSLT, string manipulation, and custom file system operations.；copy is generic utility with no parameters; buildSiteForEdit has 8 parameters and complex control flow.；copy handles directory structure; buildSiteForEdit processes a set of pages with XML transformations.
- 修正建议: Reevaluate this pair in BCB; it is likely a false positive annotation.；For static models, no fix needed as prediction is correct.

### case_id=4005 FN partial_functionality

- 方法: `combineJs` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Combines multiple JavaScript files into one, with optional minification, and updates a script tag.
- B 摘要: Builds an editable website by transforming XML/HTML pages, applying gadgets, and writing output files.
- 静态失败原因: Static BERT/GraphCodeBERT likely relied on token-level similarity and structure, which are low (Jaccard=0.128). It correctly identified lexical and semantic differences, but BCB's broader criteria may have labeled this as clone, causing a false negative for the static model.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may view both as similar due to the overarching pattern of processing a list of files, performing conditional file operations, and writing results. The presence of loops, I/O streams, and error handling could be interpreted as Type-4 similarity, though the domain-specific details differ significantly.
- 共享行为: Both iterate over a collection of items (JS links or pages).；Both perform file I/O operations (read/write).；Both use temporary or output file paths.；Both handle exceptions and logging.
- 行为差异: combineJs specifically compresses and concatenates JavaScript; buildSiteForEdit transforms XML/HTML with XSLT.；combineJs uses JavaScriptCompressor; buildSiteForEdit uses Transformer and Gadgets.；combineJs has a fallback to unminified version; buildSiteForEdit handles page rendering errors.；Different output structures: combined script vs. individual page files.
- 修正建议: Incorporate functional role detection (e.g., minification vs. transformation).；Use a model that separates boilerplate from core logic.；Consider adding a graph-based representation of data flow to highlight domain-specific operations.

### case_id=4006 FP lexical_or_api_overlap

- 方法: `PageLoader` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Loads entire content from a URL into a string.
- B 摘要: Performs Google image search by constructing query, downloading HTML, and extracting image URLs.
- 静态失败原因: Static BERT/GraphCodeBERT may overemphasize lexical and API-level similarities (e.g., URL, BufferedReader, readLine) while missing the distinct functional intent and control flow.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the overall functionality and output are completely different, despite shared low-level I/O patterns.
- 共享行为: Both open a URL connection and read lines into a string.；Both use BufferedReader and InputStreamReader.；Both close the reader.
- 行为差异: A reads raw content entirely; B parses HTML for image URLs.；A is a generic page loader; B is specific to Google image search.；B includes HTTP header, condition check, and string replacement logic.；B extracts and collects substrings; A does not.
- 修正建议: Incorporate dataflow or control flow analysis to distinguish different functional purposes.；Use models that capture higher-level semantics or domain-specific knowledge.；Enhance training with more discriminative examples of similar I/O but different functionality.

### case_id=4007 FP partial_functionality

- 方法: `setContenu` vs `readData`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Sets file content by copying input stream to output stream and updating metadata with various checks.
- B 摘要: Reads a configuration file to initialize multiple character sets and mappings for Tibetan transliteration.
- 静态失败原因: The static BERT model likely over-relied on superficial structural patterns like nested blocks and variable declarations, missing the semantic divergence due to limited understanding of library-specific operations and domain context.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB would not consider these clones because they perform entirely different tasks with no shared functionality beyond basic Java constructs.
- 行为差异: completely different domains (file management vs. configuration parsing)；different I/O operations (stream copy vs. file reading with StringTokenizer)；different data structures and purposes (metadata setting vs. set/map population)
- 修正建议: Enhance training data with diverse function pairs to reduce bias towards common control flow patterns.；Incorporate data-flow analysis to distinguish between different input/output transformations.；Use contrastive learning to emphasize semantic differences even when syntactic structures overlap.

### case_id=4008 FP lexical_or_api_overlap

- 方法: `handleHandshake` vs `sendRequest`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Handles Minecraft handshake by validating username and either sending login packet or making an HTTP request to session server for authentication.
- B 摘要: Sends an XML request to a servlet via HTTP with GZIP compression and builds a JDOM document from the response.
- 静态失败原因: Static BERT may have been misled by common tokens like 'java.net.URL', 'Exception', 'printStackTrace', and similar exception handling boilerplate, despite low Jaccard similarity.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels these as non-clones because they are functionally unrelated despite superficial networking API overlap.
- 共享行为: Both make HTTP requests using URL and URLConnection；Both handle exceptions and print stack traces
- 行为差异: Different input/output types and purposes (authentication vs generic request)；Different logic flow: validation vs direct request；Different response handling: shutdown vs document parsing；Different HTTP methods: GET vs POST with compression
- 修正建议: Improve structural awareness to differentiate core logic from boilerplate；Incorporate data-flow or control-flow analysis；Use domain-specific features like protocol, compression, and return type

### case_id=4009 FN lexical_or_api_overlap

- 方法: `main` vs `testCodingEmptyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a URL and extracts its zip entries to files.
- B 摘要: Tests a LengthDelimitedEncoder by writing data and transferring from a file channel, then asserts the output.
- 静态失败原因: Low token Jaccard (0.1165) and different method names (main vs. test) led to low lexical overlap, causing static BERT to miss the potential structural or semantic similarity that BCB identified.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB might consider them clones due to shared use of file and stream APIs (e.g., FileOutputStream, channels) and similar patterns of reading/writing data, reflecting a broad Type-4 or partial functionality similarity.
- 共享行为: Both involve file I/O and stream operations (FileOutputStream, channels)
- 行为差异: Different purposes: extraction vs. testing encoder；Different data sources: URL vs. in-memory and temp file；Different operations: zip handling vs. encoding/assertion
- 修正建议: Incorporate graph-based or dataflow features to capture structural similarities in stream handling；Use contrastive learning to focus on functional rather than lexical overlap

### case_id=4010 FP partial_functionality

- 方法: `readReferenceText` vs `readUNI`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a text file from a URL and returns its entire content as a string.
- B 摘要: Reads a TSV file from a URL, parses tab-separated values, and populates a vector with concatenated id and description.
- 静态失败原因: Static BERT/GraphCodeBERT may have overemphasized common API calls (URL, openStream, IOException) and overlooked the distinct data transformation logic and return types, leading to a false positive.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely labels this as non-clone because the functions have fundamentally different purposes (whole file read vs. structured data parsing) despite sharing the generic pattern of reading from a URL.
- 共享行为: Both open a URL and read from an input stream.；Both handle exceptions with try-catch blocks.；Both use standard Java I/O classes.
- 行为差异: Function A returns a String; function B returns void and populates a Vector.；Function A reads raw lines and appends newline characters; function B parses tab-separated values using Scanner.；Exception handling differs: A logs and throws a custom exception; B silently catches exceptions and prints stack trace.；Input source: A derives filename from an identifier; B takes a direct URL as parameter.
- 修正建议: Incorporate dataflow analysis to track how input is transformed to output.；Improve token-level attention to differentiate between reading raw content and parsing structured data.；Include more training examples with similar I/O patterns but different business logic.

### case_id=4011 FN benchmark_preference_bias

- 方法: `copyFile` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Copies a file from one File to another using FileChannel.
- B 摘要: Launches a NexOpen project build, processing XML files and setting properties.
- 静态失败原因: Static BERT correctly predicted non-clone due to very low token overlap (0.033) and entirely different code structures and contexts.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled as clone due to both methods performing file operations, but the overall functionality is vastly different; likely a labeling error.
- 共享行为: Both involve file I/O operations.
- 行为差异: Code A performs a simple file copy; code B orchestrates a complex build involving multiple files and XML processing.；Code A is generic; code B is specific to a project type.；Code A has no XML or project configuration; code B extensively processes XML and project properties.；Code A is short and focused; code B is long with many steps and error handling.
- 修正建议: Consider whether BCB annotation is correct; if not, relabel as non-clone.；Ensure clone detection benchmarks are carefully curated to avoid false positives from coarse functional similarity.

### case_id=4012 FN benchmark_preference_bias

- 方法: `read` vs `parse`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Opens a file or URL and delegates to an internal read method, returning a status code.
- B 摘要: Parses a structured data file (local or URL) into a DataSet object, handling headers, types, delimiters, and scientific notation.
- 静态失败原因: The static model likely relied on low token Jaccard (0.082) and large structural differences, thus predicting non-clone. It did not capture the abstract similarity of performing a read operation from an external source, which BCB might consider sufficient for a clone label.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled them as clones because both functions perform I/O operations (reading from a URL/file) and return a result, which could be considered a Type-4 clone under a very broad 'same task' criterion. However, the actual data processing is vastly different.
- 共享行为: Both can open an input stream from a URL or local file.；Both return a result related to the input (status or DataSet).
- 行为差异: Function A is a simple wrapper that reads raw bytes; Function B is a complex parser with tokenization, type conversion, and data structure building.；Function A returns an integer status; Function B returns a DataSet object.；Function A catches IOException and sets a status; Function B throws custom exceptions on errors.；Function A has no parsing logic; Function B handles headers, delimiters, and scientific notation.
- 修正建议: Use more abstract semantic representations that capture I/O and error-handling patterns.；Consider clone types that match the granularity of BCB annotations, which may include high-level functional similarity even if implementation details differ greatly.

### case_id=4013 FP lexical_or_api_overlap

- 方法: `addDataFromURL` vs `executePost`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads content from a URL and appends it to an internal text buffer, handling errors by appending the URL string.
- B 摘要: Sends an HTTP POST request with parameters and returns the response string, handling errors by printing stack trace and returning null.
- 静态失败原因: High lexical and API overlap (URL, BufferedReader, readLine, exception handling) may have misled the model into thinking they are similar, ignoring the fundamental behavioral differences.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels as non-clone because the core functionality differs significantly (GET vs POST, buffer vs return), despite both performing URL I/O.
- 共享行为: Both open a URL connection；Both use BufferedReader to read lines；Both handle exceptions
- 行为差异: A uses default GET method, B uses POST with headers and parameters；A appends lines to an internal buffer, B returns the response string；B includes request writing and connection disconnect; A only closes input stream
- 修正建议: Incorporate data-flow analysis to distinguish GET vs POST；Add control-flow patterns to detect header setup and request writing；Use method naming and parameter count as additional signals

### case_id=4014 FN partial_functionality

- 方法: `getHTML` vs `PageLoader`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches HTML from a URL using HttpURLConnection, reads lines with line break appending, optionally writes to a file, and returns the content.
- B 摘要: Constructor that fetches content from a URL using URL.openStream(), reads lines while available, concatenates without newlines, and stores in an instance variable.
- 静态失败原因: Low token Jaccard (0.186) and different method signatures/control flow (file writing, connection handling) caused the model to focus on surface-level differences, missing the underlying semantic similarity of URL reading.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often marks as clone when functions share core functionality (retrieving URL content) despite differences in connection handling, reading logic, and additional operations, considering them Type-3/4 clones.
- 共享行为: Both open a URL and read text content from the input stream；Both accumulate the read lines into a string variable
- 行为差异: Function A uses HttpURLConnection with User-Agent header; Function B uses URL.openStream()；Function A reads until null; Function B reads while in.ready() (potentially incomplete)；Function A appends "\r\n" after each line; Function B does not add newlines；Function A optionally writes to a file; Function B does not
- 修正建议: Include training examples of partial clones where core functionality matches but I/O details differ；Use dataflow analysis to highlight shared operations like opening a stream and reading lines；Apply contrastive learning to emphasize functional similarity over exact token matching

### case_id=4015 FP boilerplate_overlap

- 方法: `getFrameworkFactory` vs `handledRun`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Loads a framework factory class from a service file via classpath.
- B 摘要: Downloads and updates game data from an online XML file.
- 静态失败原因: Static model over-emphasized lexical overlap of common I/O patterns (URL, BufferedReader, InputStreamReader) and failed to capture divergent long-range semantics.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB requires semantic similarity beyond common boilerplate; these functions have entirely different business logic and goals.
- 共享行为: Read from a URL using BufferedReader and InputStreamReader；Close the BufferedReader in a finally block；Handle potential IOExceptions
- 行为差异: Purpose: framework loading vs. game data download；Output: return FrameworkFactory instance vs. write to file and reload database；Control flow: service file parsing vs. version comparison and file writing；Error handling: throws generic exception vs. specific catch blocks and UI messages
- 修正建议: Add control-flow or data-flow features to distinguish I/O boilerplate from core logic；Train with more negative examples that share boilerplate but differ semantically；Use graph-based models that capture call dependencies and data flows

### case_id=4016 FN long_range_semantics

- 方法: `loadSourceCode` vs `readData`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Loads a source code file and applies syntax highlighting to generate an HTML representation.
- B 摘要: Reads a configuration file and parses tokenized data to populate various HashSets and maps.
- 静态失败原因: The low token overlap and different syntactic structures caused the static model to miss the broad functional similarity; it required understanding that both methods read files and process lines, which is not captured by local patterns.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may consider both as 'data loading' functions that read and process file content line by line, viewing them as Type-4 clones with common high-level behavior despite different specific tasks.
- 共享行为: Both read input from a file line by line using BufferedReader.；Both handle IOException with try-catch blocks.；Both perform string manipulation and processing on each line.
- 行为差异: A outputs an HTML string after syntax highlighting; B has void return and modifies static data structures.；A uses CodeViewer for highlighting; B uses StringTokenizer and column parsing.；A reads a single source code file; B reads a structured ini-like config with delimiters and multiple fields.；A's output is used for display; B populates internal data for further processing.
- 修正建议: Incorporate data flow analysis to track file I/O and line processing.；Use models that leverage method names or class context to infer high-level purpose.；Add documentation-aware features to capture intent.

### case_id=4017 FP lexical_or_api_overlap

- 方法: `getUser` vs `parse`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Loads a user from a DAO or parses a config file to find and save a user.
- B 摘要: Parses a data file (or URL) with headers and types into a DataSet object.
- 静态失败原因: The static model may have been misled by surface-level similarities such as BufferedReader, try-catch, tokenization loops, and file reading patterns, ignoring the deep semantic differences in purpose and output.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB annotation likely considered these non-clones because they implement completely different domain-specific logic despite both reading text files. The tokenization and file reading are incidental common patterns.
- 共享行为: Both read from a data source (file/URL) line by line；Both use tokenization to parse delimited data；Both handle exceptions
- 行为差异: Function A retrieves a single user by login; Function B parses an entire dataset with columns and rows；Function A uses simple StringTokenizer; Function B uses complex StreamTokenizer with number parsing, scientific notation, etc.；Function A saves data via DAO; Function B returns a DataSet object；Function A has a single-purpose lookup; Function B has configurable parsing with headers, types, pre/post header lines
- 修正建议: Add more negative training examples with similar I/O patterns but different semantics；Incorporate data flow analysis to track variable types and method calls' context；Use long-range dependency modeling to capture overall function purpose

### case_id=4018 FN partial_functionality

- 方法: `transformSingleFile` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.4`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Compresses an X3D file to a .x3dv.gz file using GZip compression.
- B 摘要: Launches a Maven-based project configuration by processing pom files and setting up Hibernate reverse engineering.
- 静态失败原因: Static BERT models rely on token-level similarities and syntactic patterns; the low token Jaccard and different domain-specific vocabulary caused it to miss the abstract functional similarity that BCB annotators may have seen.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as data transformation operations that read input and generate output, potentially viewing them as Type-4 clones based on high-level functionality.
- 共享行为: Both perform file I/O operations to read and write files after processing.
- 行为差异: Different domains: X3D editor vs Eclipse Maven project.；Different processing logic: GZip compression vs XML/Hibernate configuration.；Different output: compressed file path vs project configuration state.
- 修正建议: Improve model sensitivity to abstract behavioral patterns by incorporating dataflow analysis.；Train on more diverse examples of Type-4 clones.

### case_id=4019 FN partial_functionality

- 方法: `modifyApplicationMessage` vs `readAndRewrite`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.35`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Modify a property value in a locale-specific .properties file, copying from an English default if the file does not exist.
- B 摘要: Read a DICOM image file, parse it, and rewrite it to a new file with possibly different encoding.
- 静态失败原因: The token Jaccard similarity is extremely low (0.05), providing very little lexical or syntactic overlap for static embeddings to capture; the model likely failed to recognize the abstract 'file read-modify-write' pattern shared across different domains and APIs.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB might label this as a clone due to both functions implementing a high-level 'read, modify, write' pattern at the file I/O level, which could be considered a Type-4 (functionally similar) clone despite vastly different domain logic and low token overlap.
- 共享行为: Read an input file into memory；Perform some transformation or modification on the data；Write the result to an output file；Use Java I/O streams and handle exceptions
- 行为差异: Function A works with text-based properties files; Function B works with binary DICOM medical image files；A modifies a specific key-value pair or appends it; B converts the entire DICOM dataset to a new encoding；A uses standard Java Properties class and file reading/writing; B uses domain-specific DICOM libraries (ImageIO, DcmParser, etc.)；A handles the non-existence of files by copying defaults; B assumes input exists
- 修正建议: Enhance model with abstract control-flow or data-flow features that capture high-level I/O patterns；Incorporate domain-agnostic operation sequences (read, transform, write) into training；Use graph-based representations that abstract away specific library calls

### case_id=4020 FN partial_functionality

- 方法: `callService` vs `register`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.4`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Makes an HTTP GET request to a constructed URL and stores the entire response as a string, returning nothing.
- B 摘要: Registers a user by encoding password, setting attributes, making an HTTP request to a forum to set a forum ID, persisting user, sending confirmation email, and returning boolean success.
- 静态失败原因: Static BERT models like GraphCodeBERT rely on token-level and structural similarity; the low token Jaccard (0.16) and different control flow (one is simple, the other complex) likely caused the model to deem them dissimilar, missing the shared URL reading pattern that BCB considered clone-worthy.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider these clones because both contain a core pattern of constructing a URL, opening a connection, and reading the response, which is a functionally similar sub-task, and BCB sometimes labels such partial functionality overlaps as Type-3 or Type-4 clones.
- 共享行为: Both functions make an HTTP request by constructing a URL, opening a connection, and reading the response line by line with BufferedReader.
- 行为差异: Function A is a generic HTTP call that stores the full response; Function B is a specific registration process with multiple steps beyond the HTTP call.；Function A sets an instance variable 'answer'; Function B returns a boolean and throws exceptions.；Function A only catches network errors; Function B catches network errors and number format errors, and also handles mail exception.；Function B includes validation, password encoding, logging, database persistence, and email sending.
- 修正建议: Improve model's ability to detect sub-function-level clones by focusing on graph or data-flow similarity of common patterns.；Use code summarization or embedding that captures intent beyond exact tokens.

### case_id=4021 FN boilerplate_overlap

- 方法: `createJAR` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Creates a JAR file or directory and serializes a document object into it.
- B 摘要: Builds a website for editing by transforming XML pages and writing output files.
- 静态失败原因: The static model likely relied on token overlap and method name differences, resulting in a low similarity score and incorrect non-clone prediction.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may have labeled as clone because both functions involve file writing and manipulate documents, but the specific logic is entirely different; this is likely a false positive in BCB due to broad partial functionality similarity.
- 共享行为: Both write files to the filesystem.；Both handle file paths and directory creation.；Both use try-catch for exception handling.
- 行为差异: A handles a single file; B processes multiple pages in a loop.；A copies a JAR resource and serializes an object; B transforms XML with XSLT.；A uses ObjectOutputStream; B uses Transformer and StreamResult.；A has a simple structure; B has complex transformation and multiple I/O operations.
- 修正建议: Focus on semantic similarity rather than just token overlap.；Incorporate code structure and data flow embeddings.；Use function purpose classification to distinguish different operations.

### case_id=4022 FN benchmark_preference_bias

- 方法: `main` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a URL and extracts its zip entries to local files.
- B 摘要: Copies a file from one location to another using NIO FileChannel.
- 静态失败原因: Static BERT/GraphCodeBERT likely correctly rejected this pair due to low token overlap and distinct control flow, but BCB label is erroneous.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled as clone due to superficial similarity in file I/O operations (both open input/output streams), even though the actual tasks differ significantly.
- 共享行为: Both involve reading from an input source and writing to an output destination
- 行为差异: Code A handles network URL and zip extraction, Code B handles local file copy；Code A uses ZipInputStream and BufferedOutputStream, Code B uses FileChannel.transferTo；Code A has console output, Code B has exception handling
- 修正建议: Re-annotate BCB label for this pair as non-clone；Improve guidelines to avoid labeling based on generic I/O operations

### case_id=4023 FP lexical_or_api_overlap

- 方法: `getURLContent` vs `importSequences`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads content from a URL and returns it as a string.
- B 摘要: Parses FASTA-like sequence data from a URL and stores names and sequences in lists.
- 静态失败原因: The model likely over-relied on lexical overlap (URL, openStream/Connection, readLine, IOException) and missed the distinct control flow and data structures.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the overall functionality (retrieving a web page vs parsing sequence data) is very different despite shared I/O operations.
- 共享行为: Both open a connection to a URL and read text data.；Both use line reading (readLine) and string building (StringBuilder/StringBuffer).
- 行为差异: getURLContent returns the entire content as a single string; importSequences parses a specific format and stores multiple entries.；getURLContent uses a simple while loop; importSequences uses a do-while loop with delimiter checking for '>'.；importSequences uses an ImportHelper class and handles tokens; getURLContent does not.；Error handling differs: getURLContent throws IOException; importSequences catches and prints stack traces.
- 修正建议: Train on more negative examples with similar API usage but different semantics.；Incorporate dataflow or control flow features to distinguish simple reads from complex parsing.

### case_id=4024 FP lexical_or_api_overlap

- 方法: `doVersionCheck` vs `sendPost`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Opens a URL to fetch version check data, parses version and build strings, and displays a message to the user.
- B 摘要: Sends an HTTP POST request with parameters to a URL, reads the response, and returns it as a string.
- 静态失败原因: Static BERT/GraphCodeBERT likely over-relied on surface-level token overlap (URL, BufferedReader, IOException) and control-flow similarity (try-catch, while loop), ignoring semantic purpose differences.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels as non-clone because the functions have distinct purposes (version checking vs. HTTP POST), despite sharing superficial IO patterns.
- 共享行为: Both create a URL object and open a connection/stream；Both use BufferedReader to read input from the stream；Both handle exceptions and close streams
- 行为差异: A uses URL.openStream() (GET-like), B uses HttpURLConnection with POST method；A parses specific lines starting with .version and .build, B concatenates all lines into result string；A displays GUI messages and hides wait cursor, B returns the result string；A uses jEdit specific properties, B uses generic URL and parameters
- 修正建议: Incorporate API call sequences (e.g., openStream vs setDoOutput) to distinguish GET vs POST；Add data-flow analysis to track how read data is used (e.g., parsing vs concatenation)；Use context from method names and surrounding code

### case_id=4025 FN benchmark_preference_bias

- 方法: `unzip` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Unzips a zip file to a target directory, handling directory creation and file extraction.
- B 摘要: Builds a site for editing by processing pages, transforming XML, and writing output files.
- 静态失败原因: The static model correctly predicted non-clone because of low token overlap (Jaccard=0.09) and no shared structural patterns; the false negative arises from BCB's lenient annotation.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled these as clones due to a broad interpretation of 'file processing' or 'I/O operations', but the specific functionalities are completely different.
- 共享行为: Both involve file I/O operations (reading/writing files).；Both use buffered streams for data transfer.
- 行为差异: Function A specifically extracts zip archives; Function B processes site pages with XML transformations.；Function A handles zip entries and directories; Function B processes a list of page objects and applies string replacements.；Function B includes extensive debugging output and exception handling specific to DOM and transformer errors, while Function A focuses on file existence and creation exceptions.
- 修正建议: Use stricter clone definition requiring more specific functional similarity.；Re-annotate BCB pairs with higher confidence or filter out overly broad partial clones.；Incorporate task-specific features or API usage patterns to distinguish unrelated file-processing functions.

### case_id=4026 FN partial_functionality

- 方法: `getContent` vs `readIntoList`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Executes an HTTP request and returns the response body as a string by reading it line by line.
- B 摘要: Reads a URL, parses HTML to extract link text, builds JMenuItems with action listeners, and populates a map; also updates a GUI text field on action.
- 静态失败原因: Static BERT/GraphCodeBERT likely focused on the different output types (String vs void), different APIs (HttpClient vs URL), and the extra GUI code in B, failing to capture the shared high-level pattern of network stream reading and line iteration due to low token overlap and lexical differences.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considered the core functionality of 'reading from a network stream line by line' as sufficient for a Type-3 or Type-4 clone, accepting the additional parsing and UI code in B as extensions of the same base pattern.
- 共享行为: Both open a connection to a network resource (HTTP request or URL) and read lines using BufferedReader.；Both iterate over lines until null, processing each line inside the loop.；Both close the reader after the loop.
- 行为差异: Function A returns a concatenated string; Function B returns void and modifies a map and GUI components.；Function A uses Apache HttpClient; Function B uses URL.openStream().；Function A sets connection and socket timeouts; Function B does not.；Function B performs HTML parsing and creates JMenuItem objects with action listeners; Function A simply appends lines.
- 修正建议: Use models that better capture functional semantics, such as graph-based models that follow data flow from network source to line reading loop.；Train with contrastive learning on functional labels from BigCloneBench to emphasize partial similarity.；Incorporate attention on common patterns like 'BufferedReader' and 'readLine' loops to recognize reused subroutines.

### case_id=4027 FP lexical_or_api_overlap

- 方法: `sendPost` vs `createDialogArea`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Send an HTTP POST request with parameters and return the response body.
- B 摘要: Create a dialog area displaying license text from a resource file, with fallback to text widget if browser fails.
- 静态失败原因: Static BERT models may over-rely on common syntactic patterns (try-catch, BufferedReader, while readLine), missing the high-level semantic context that one function is a network client and the other is a UI builder. The shared I/O boilerplate triggered a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clones when functions have different overall functionality (network I/O vs. UI construction), despite sharing some boilerplate I/O patterns. The token overlap is low (0.159), and the methods serve different purposes.
- 共享行为: Both read from an InputStream line by line using BufferedReader；Both close streams in finally-like blocks (sendPost uses inline, createDialogArea uses explicit finally)
- 行为差异: sendPost performs network communication; createDialogArea builds a UI composite；sendPost writes to output stream; createDialogArea sets text in browser/text widget；sendPost returns a String; createDialogArea returns a Control (Composite)；sendPost has no UI components; createDialogArea handles SWT and Browser widgets
- 修正建议: Incorporate named entity recognition for method names (sendPost vs. createDialogArea) and parameter types (String vs. Composite parent)；Use control flow analysis to differentiate UI event handling from network calls；Add deeper representation of library-specific semantics (SWT vs. HTTPURLConnection)；Train with more diverse examples to reduce sensitivity to common subroutines

### case_id=4028 FN partial_functionality

- 方法: `readData` vs `doVersionCheck`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Initializes multiple data structures (sets, maps) by parsing tokenized strings and reading configuration from a file.
- B 摘要: Fetches version information from a remote URL, parses version strings, and triggers version comparison.
- 静态失败原因: Static BERT likely focused on low token overlap (0.098) and different method names, missing the structural pattern of reading and parsing input that BCB considered.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB might have considered both as 'data reading' routines with similar control flow (while loops, try-catch), despite different concrete functionality, possibly due to broad Type-3 or partial functionality overlap.
- 共享行为: Both read input line by line or token by token；Both handle IOException with error reporting；Both use while loops to iterate over input
- 行为差异: readData uses StringTokenizer and file I/O; doVersionCheck uses URL.openStream() and BufferedReader；readData populates various sets and maps; doVersionCheck extracts version strings and calls another method；readData is data initialization; doVersionCheck is network-dependent version checking；readData is private static; doVersionCheck is public static with a View parameter
- 修正建议: Incorporate control flow and data flow analysis to capture structural similarities；Use graph-based representations that abstract away specific variable and method names

### case_id=4029 FN partial_functionality

- 方法: `encodeFileToFile` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.4`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Encodes a file to Base64 and writes to another file.
- B 摘要: Builds a website for editing by reading multiple files, applying XML transformations and string replacements, and writing output files.
- 静态失败原因: Static BERT models rely on lexical and structural similarity; the low token Jaccard (0.0667) and differing code patterns caused the model to miss the abstract shared behavior of file transformation.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB's broad Type-4 definition considers functions with similar high-level dataflow (read-transform-write) as clones, even if the specific transformations differ significantly.
- 共享行为: Both read data from a file.；Both apply a transformation to the data (Base64 encoding vs XML/site transformation).；Both write the transformed data to an output file.；Both use buffered I/O for efficiency.
- 行为差异: Function A performs a single, simple file encoding; Function B performs complex multi-step site generation with loops and multiple file operations.；Function A uses Base64 encoding; Function B uses XSLT transformations, string replacements, and property handling.；Function A handles a single input-output pair; Function B processes multiple pages and files.；Function A returns a boolean success flag; Function B is void and throws exceptions.
- 修正建议: Incorporate dataflow analysis to capture high-level I/O patterns.；Use models that consider abstract syntax trees or control flow graphs for functional similarity.；Train on pairs with broad Type-4 clones to improve recognition of partial functionality.

### case_id=4030 FP lexical_or_api_overlap

- 方法: `readRemoteFile` vs `getVersion`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads entire content of a remote file line by line and concatenates.
- B 摘要: Reads a remote version URL and returns only the last line read.
- 静态失败原因: Static BERT methods often rely on overlapping token/API sequences; both functions share URL, BufferedReader, InputStreamReader, and a while-read loop, leading to high embedding similarity despite functional differences.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels as non-clone because the methods have different purposes (reading arbitrary file vs retrieving version) and different output semantics (full content vs single line), despite similar boilerplate.
- 共享行为: Both open a URL connection and use BufferedReader to read lines；Both return a String
- 行为差异: Different URLs: StaticData.remoteFile vs hardcoded version URL；readRemoteFile concatenates all lines, getVersion overwrites and returns last line；Different error handling: readRemoteFile catches EOFException and IOException separately, getVersion catches Exception broadly；readRemoteFile uses a boolean eof flag, getVersion uses while loop directly
- 修正建议: Incorporate dataflow analysis to distinguish full concatenation from single assignment；Add training examples with similar boilerplate but different output semantics；Use structural differencing or graph-based features beyond token sequences

### case_id=4031 FP lexical_or_api_overlap

- 方法: `run` vs `run`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a resource file from the classpath and sets it as text in a Swing text area.
- B 摘要: Loads a vector tile from a URL, parses it, and adds the geometries to a data layer.
- 静态失败原因: The model likely overemphasized lexical overlap (common API calls like URL, InputStream, BufferedReader) and the same method name 'run', while missing the semantic difference in overall functionality.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clones because the functions have entirely different purposes and outputs, despite sharing some I/O boilerplate.
- 共享行为: Both are Runnable implementations that override run()；Both perform I/O operations using URL, InputStream, and BufferedReader；Both read lines from a stream and concatenate them
- 行为差异: Function A reads from a classpath resource, while B reads from a URL with multiple protocol handling；A sets text in a Swing component using invokeLater, B processes tile data into geometry collections；A catches all exceptions silently, B handles specific exceptions with logging and early returns；B includes synchronization and data structure manipulation not present in A
- 修正建议: Incorporate control flow and data flow analysis to distinguish overall purpose；Use models that capture long-range semantics beyond local patterns；Add training examples that differentiate boilerplate code from true clones

### case_id=4032 FP lexical_or_api_overlap

- 方法: `main` vs `copyFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Main method that parses a Prolog file, generates adapter classes, and writes them to a JAR.
- B 摘要: Utility that copies a file from source to destination using NIO channels.
- 静态失败原因: The model likely over-relied on superficial lexical cues like 'File', 'IOException', and 'static void' signature, ignoring the vast difference in logic and length.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB annotators would see no functional overlap: one is a generation pipeline, the other a file copy. They are clearly non-clones.
- 行为差异: Function A is a complex multi-step workflow for adapter generation; Function B is a simple file copy.；A reads and parses a Prolog file; B only transfers bytes.；A writes multiple classes and resources; B writes a single output file.；A handles command-line arguments and errors; B throws IOException.
- 修正建议: Add training examples that penalize matches based only on common library usage (e.g., File, IOException).；Incorporate control-flow or data-flow abstractions to differentiate simple I/O from complex business logic.

### case_id=4033 FN partial_functionality

- 方法: `login` vs `getEncoding`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Logs into LOLA service by sending POST request with email/password and returns session ID.
- B 摘要: Extracts character encoding from HTTP response headers or body, returning encoding string or default.
- 静态失败原因: Static BERT models rely heavily on token overlap and method name similarity. With token Jaccard of only 0.15 and different method names ('login' vs 'getEncoding'), the model failed to capture the vague structural similarity. The models lack understanding of high-level intent and data flow differences.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled these as clones due to both being network I/O functions with similar structure (open connection, read input, error handling). Given low token overlap and different method names, it is unlikely to be considered a true clone even in broad Type-4 sense.
- 共享行为: Both involve opening a URLConnection and using BufferedReader to read data.；Both implement error handling (one with catch, one with finally).；Both use standard Java I/O and networking classes.；Both return a string result from HTTP communication.
- 行为差异: Function A sends data (POST) via OutputStreamWriter; Function B only reads.；Function A returns session ID extracted from response; Function B returns encoding from headers or body.；Function A closes both Writer and Reader; Function B only closes Reader in finally.；Function A has no fallback; Function B defaults to STANDARDENCODING if not found.
- 修正建议: Incorporate data flow and control flow analysis to distinguish write vs read operations.；Use task-specific contextual embeddings or domain adaptation to differentiate login vs encoding extraction.；Train on contrastive examples with similar structure but different semantics.

### case_id=4034 FP lexical_or_api_overlap

- 方法: `perform` vs `md5`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Handles HTTP request to classify concepts in DTS tree browser, involving session, XML, and URL connections.
- B 摘要: Computes MD5 hash of a given string using MessageDigest.
- 静态失败原因: Static BERT likely overfitted on common keywords like 'String', 'new', 'return', 'getBytes', and 'catch', ignoring the deeper structural and semantic differences.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clone because the functions have entirely different functionality and no meaningful semantic overlap.
- 行为差异: Different signatures and overall purposes.；A interacts with HTTP session, request/response, and external URLs; B is a pure hash function.；A uses many libraries (Struts, XML, etc.); B only uses MessageDigest.；A has complex error handling and session management; B has simple exception handling.
- 修正建议: Include method name and signature context in the input.；Use control flow and data flow features.；Augment training with more diverse negative pairs of unrelated functions.

### case_id=4035 FN partial_functionality

- 方法: `main` vs `postData`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: A main method that performs an HTTP POST request with hardcoded parameters to a specific API and prints the response.
- B 摘要: A method that performs an HTTP POST request with given parameters and reads the response without printing.
- 静态失败原因: Static BERT methods like GraphCodeBERT rely on token overlap and structural similarity. Here token Jaccard is 0.16, very low. Also, the functions use different APIs (PostParameter vs. simple data, HttpURLConnection vs. URLConnection). The model likely focused on these surface differences and missed the shared high-level behavior. Additionally, function A is a main method with no parameters, while B is a method with parameters, leading to different syntactic structures.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often marks as clones functions that implement the same high-level functionality (HTTP POST) even with different parameterization, output, or exception handling. The core data flow (open connection, write data, read response) is identical.
- 共享行为: Both open an HTTP connection with output enabled；Both send data via POST；Both read the response stream
- 行为差异: Function A uses explicit POST method and sets headers differently；Function A prints debug info and response, while function B discards response；Function A has hardcoded parameters, function B takes parameters；Function A uses specific classes (PostParameter, RenRenPostParameters) for parameters, function B uses a simple string
- 修正建议: Improve representation of data flow and control flow to capture underlying operations like URL creation, connection, output, input.；Use graph-based models that abstract away specific API calls.；Add contrastive learning examples where functions with different implementations but same high-level behavior are considered positive pairs.

### case_id=4036 FN boilerplate_overlap

- 方法: `copyFile` vs `modifyApplicationMessage`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.6`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a file from source to destination using FileChannel.
- B 摘要: Modifies a properties file for a given locale by reading, updating, or adding a key-value pair.
- 静态失败原因: Static models likely predicted non-clone due to low token overlap and different method names; they did not capture the shared file I/O aspect that BCB might have considered.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may have labeled as clone due to both functions dealing with file writing, but the core functionality differs significantly.
- 共享行为: Both perform file I/O operations
- 行为差异: copyFile is a pure file copy with no parsing or modification；modifyApplicationMessage reads and writes a properties file with specific format；copyFile uses NIO channels for efficient transfer；modifyApplicationMessage uses traditional IO and string manipulation
- 修正建议: Improve understanding of file manipulation tasks as potentially similar in BCB context；Consider that BCB might label based on broader functional category like 'file manipulation'

### case_id=4037 FP boilerplate_overlap

- 方法: `readReferenceText` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a text resource from a URL and returns its content as a string.
- B 摘要: Performs a Google image search, parses the HTML response to extract image URLs, and updates the UI with the first image.
- 静态失败原因: The static model likely focused on the lexical overlap of URL, BufferedReader, readLine, and try-catch blocks, which are common boilerplate patterns for I/O operations. It may have missed the larger semantic context of the different purposes and data transformations.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the functions have different purposes (reading a reference text vs. web image search), different I/O (internal resource vs. HTTP), and different outputs (string vs. void with UI updates). The only similarity is the boilerplate of reading line by line from a URL, which is a common pattern across many unrelated functions.
- 共享行为: Both open a URL connection and read data line by line using BufferedReader.
- 行为差异: A returns the file content as a string; B returns void and updates UI.；A reads from a local resource bundle; B performs an HTTP GET to Google Images.；A uses multiple specific exception catches; B catches generic Exception and shows error dialog.；A does not parse the response; B parses HTML to extract image URLs.
- 修正建议: Train on more diverse examples where URL reading is not a distinguishing feature.；Use dataflow analysis to capture the different data usage after reading.；Add attention to the overall method signature and return type.

### case_id=4038 FP boilerplate_overlap

- 方法: `readUNI` vs `PhoneSetImpl`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a UNI description file from a URL, parses tab-delimited lines, and populates a vector with formatted id/desc strings.
- B 摘要: Constructor that initializes a phone set from a URL by reading lines, skipping comment lines, and parsing others via a separate method.
- 静态失败原因: The static model likely overemphasized lexical and structural similarities (URL, openStream, while loop, readLine, stream closure) and missed the semantic differences in data processing and output.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels this non-clone because the two functions have different high-level purposes (populating a vector vs. constructing a phone set) and different parsing logic, despite both reading from URLs.
- 共享行为: Both open a URL and read lines sequentially；Both skip the first line or comment lines；Both close the input stream after processing
- 行为差异: Function A outputs to an existing vector; Function B initializes a PhoneSetImpl object；Function A parses tab-separated fields; Function B has custom parsing logic in parseAndAdd；Function A uses Scanner; Function B uses BufferedReader；Function A handles exceptions and closes stream in finally; Function B throws IOException
- 修正建议: Incorporate method-level context (e.g., method name, class name) into the model；Use dataflow analysis to capture how data is transformed, not just read；Train with more attention on the core logic beyond I/O boilerplate

### case_id=4039 FN benchmark_preference_bias

- 方法: `genCustRatingFileAndMovieIndexFile` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Reads binary movie rating data, generates customer rating file and movie index file with start indices.
- B 摘要: Downloads a KMZ file from a URL, extracts its zip entries to local files.
- 静态失败原因: The static model correctly predicted non-clone (0); it did not fail. The BCB annotation is likely a false positive.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB likely labeled as clone due to superficial similarity in using FileChannels/streams and loops, ignoring entirely different high-level semantics.
- 共享行为: Both perform file I/O operations；Both use buffered streams and loops
- 行为差异: Different input sources: local binary file vs. remote URL；Different output: custom binary format vs. extracted files；Different data processing logic: movie/customer aggregation vs. zip extraction；Different control flow: one processes fixed-size records, the other reads zip entries
- 修正建议: Re-annotate this pair as non-clone based on semantic dissimilarity；Consider using higher-level semantic features beyond token sequences

### case_id=4040 FN boilerplate_overlap

- 方法: `encodeFileToFile` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.4`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Encodes an input file to Base64 and writes the encoded data to an output file, returning success boolean.
- B 摘要: Builds a website for editing by transforming XML pages, writing output files, and handling multiple configuration parameters.
- 静态失败原因: The static model likely focused on low token overlap (0.0667) and surface-level differences, failing to recognize the abstract I/O boilerplate pattern that BCB may have considered as clone.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB might have considered the shared pattern of file I/O with buffer loop and resource management as a Type-3 or Type-4 clone, despite the completely different business logic.
- 共享行为: Both read data from an input source and write processed data to an output destination.；Both use try-catch-finally blocks for I/O exception handling and resource cleanup.；Both involve file output operations.
- 行为差异: Function A performs simple Base64 encoding; Function B performs complex XML transformation and string substitution.；Function A is a static utility method with two string parameters; Function B is an instance method with many parameters including Properties and throws multiple exception types.；Function B has extensive debugging and logging; Function A has minimal error output.；Function B involves DOM parsing, XSLT transformation, and file system operations via a custom FileSystem class.
- 修正建议: Incorporate higher-level structural patterns like I/O stream handling into clone detection features.；Use data-flow analysis to distinguish trivial I/O wrappers from complex business logic.；Train on a wider variety of clone types to penalize boilerplate-only similarities.

### case_id=4041 FP boilerplate_overlap

- 方法: `main` vs `encodeFileToFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Main method for generating adapter JAR from Prolog file.
- B 摘要: Encodes a file using Base64 and writes to output file.
- 静态失败原因: Model likely overfit on common I/O boilerplate (e.g., FileInputStream, IOException) and ignored the distinct high-level purposes.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels as non-clone because functions have entirely different purposes and no shared semantic functionality.
- 共享行为: Both involve file I/O operations；Both have error handling with try-catch；Both use InputStream/OutputStream
- 行为差异: A is a complex adapter generation pipeline; B is a simple Base64 encoding；A parses Prolog and generates Java classes; B only copies bytes；A uses many external libraries; B uses only standard Java I/O
- 修正建议: Increase weight of method-level semantics vs. token overlap；Incorporate structural or dataflow analysis to distinguish I/O utility from complex logic；Use contrastive learning on diverse, non-clone pairs with similar boilerplate

### case_id=4042 FN partial_functionality

- 方法: `readAndRewrite` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.75`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Reads a DICOM image file, parses its dataset up to pixel data, reads pixel data, and writes the dataset back to a new file.
- B 摘要: Builds an HTML site by processing XML, transforming with XSLT, and writing files, with extensive debugging output.
- 静态失败原因: Token Jaccard similarity is extremely low (0.036), and the functions have different method names, parameter lists, and library dependencies. Static BERT/GraphCodeBERT models rely heavily on lexical and structural overlap, so they fail to recognize the high-level semantic pattern shared by these two functions.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considered these as Type-4 semantic clones because both implement a read-process-write pattern with similar I/O scaffolding and debugging, even though the domain and processing logic differ completely.
- 共享行为: Both perform file I/O operations (read from a file, write to a file).；Both use streams (ImageInputStream/ImageOutputStream vs InputStream/Writer).；Both include conditional or debugging output via System.out or DebugFile.；Both follow a pipeline of reading, processing, and writing data.
- 行为差异: Input and output formats: DICOM medical images vs. HTML/XML web content.；Processing logic: pixel data handling vs. XSLT transformation and string replacement.；Control flow: simple sequential in A vs. loop over multiple pages in B.；Error handling: different exceptions (IOException vs. DOMException, TransformerException).
- 修正建议: Incorporate abstract syntax tree (AST) or control flow graph (CFG) features to capture structural pipelines.；Use graph neural networks that model data flow and I/O operations.；Train on contrastive learning objectives that emphasize functional similarity over lexical overlap.；Augment training data with pairs having low token similarity but high-level I/O pattern similarity.

### case_id=4043 FP lexical_or_api_overlap

- 方法: `fetchUrl` vs `getFrameworkFactory`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches the content of a URL as a string.
- B 摘要: Loads an OSGi FrameworkFactory from a service configuration file.
- 静态失败原因: The static model likely focused on the high lexical overlap (URL, BufferedReader, InputStreamReader, readLine, close) and similar control flow, causing a false positive. It did not capture the semantic divergence in the loop body and return type.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the functions serve entirely different semantic purposes (fetching URL content vs. loading a framework factory) and produce different types, despite sharing boilerplate I/O code.
- 共享行为: Both use BufferedReader to read from a URL/openStream.；Both loop over lines using readLine.；Both close the reader in a finally or after use.
- 行为差异: fetchUrl returns the concatenated string of all lines; getFrameworkFactory returns a FrameworkFactory instance.；fetchUrl catches MalformedURLException and IOException; getFrameworkFactory throws Exception.；fetchUrl reads all lines; getFrameworkFactory reads until finding a valid non-comment line.；fetchUrl returns empty string on failure; getFrameworkFactory throws an exception on failure.
- 修正建议: Incorporate dataflow analysis to differentiate how the read lines are processed.；Add attention to output types and exception signatures.；Use method name context or type resolution.

### case_id=4044 FN partial_functionality

- 方法: `readData` vs `getPagina`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Parses a configuration file and populates multiple HashSet and HashMap structures with tokenized data.
- B 摘要: Fetches the content of a URL and returns it as a single string.
- 静态失败原因: Low token overlap (Jaccard 0.07) and long, truncated code in function A make it hard for BERT-based models to capture the overall semantic similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB might consider both as 'data reading' operations, albeit with different sources and purposes, under a very loose Type-4 interpretation.
- 共享行为: Both involve reading input data line by line in a loop
- 行为差异: Function A reads from a local file, function B reads from a URL；Function A has no return value, function B returns the fetched string；Function A parses and categorizes data into sets, function B does no parsing；Function A has complex error detection, function B simply returns error strings
- 修正建议: Improve representation of data flow and global program purpose；Use longer context or hierarchical representations；Consider high-level functional annotation

### case_id=4045 FN partial_functionality

- 方法: `main` vs `copyTo`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a URL and extracts its ZIP entries to the current directory.
- B 摘要: Recursively copies a file or directory from source to destination using FileChannel.
- 静态失败原因: Static BERT/GraphCodeBERT models likely overemphasized lexical overlap of common I/O terms (e.g., FileInputStream, FileOutputStream, buffer, close) and structural patterns (try-catch, loop), while missing the semantic difference between ZIP extraction and directory copy. The low token Jaccard (0.1444) indicates limited lexical overlap, but the model may have been misled by the boilerplate I/O code rather than the core functionality.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BigCloneBench may consider these clones due to both performing a similar high-level operation: copying data from an input source to an output destination, even though the specifics differ. The use of common Java I/O classes (FileInputStream, FileOutputStream) and the overall pattern of opening streams, transferring data, and closing them contribute to broad Type-4 similarity.
- 共享行为: Both perform file I/O operations that involve reading from an input source and writing to an output file.；Both handle resource cleanup by closing streams/channels.；Both involve transferring data from an input stream to an output stream in chunks.
- 行为差异: Function A specifically handles ZIP entry extraction from a remote URL, while Function B copies local files/directories recursively.；Function A uses ZipInputStream and BufferedOutputStream, Function B uses FileChannel.transferTo.；Function A does not handle directories; Function B explicitly handles directories by recursively copying contents.；Function A writes extracted files using entry.getName() as filename, FunctionB constructs destination path using source.getName().
- 修正建议: Incorporate data-flow analysis to track the source and destination of file operations, distinguishing between remote vs. local sources.；Use a model that captures the purpose of the function (e.g., extracting vs. copying) via functional signatures or API usage patterns.；Train with more diverse examples of I/O operations to reduce sensitivity to boilerplate code.

### case_id=4046 FN benchmark_preference_bias

- 方法: `copyFile` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.2`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Copies a file using NIO FileChannel.
- B 摘要: Launches a NexOpen project configuration, setting up Maven pom files and Hibernate settings.
- 静态失败原因: Low lexical overlap and clear semantic mismatch; static BERT correctly identified them as non-clones.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled as clone due to both involving file I/O and resource handling, but this is a very generic similarity and likely an erroneous label.
- 共享行为: Both perform file operations (copying/creating files) and handle exceptions.
- 行为差异: Entirely different purposes; copyFile is a simple utility, launch is a complex Eclipse plugin launch sequence.
- 修正建议: Use stricter clone criteria to avoid overly broad functional similarity.；Incorporate domain-specific knowledge to distinguish utility functions from complex launch sequences.

### case_id=4047 FP boilerplate_overlap

- 方法: `getJSONData` vs `readScalarpvviewerDocument`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches JSON data from a given URL using HTTP client and returns parsed JSONObject.
- B 摘要: Reads a configuration file from a URL, parses XML, and updates UI components of a ScalarPV viewer application.
- 静态失败原因: The model over-relied on surface-level boilerplate (BufferedReader, while reading lines) and possibly similar variable names, ignoring the vast difference in downstream operations. The low token Jaccard indicates little overlap, but the model may have been misled by the common pattern of reading from a URL.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clone because the functions have completely different purposes (data retrieval vs UI configuration), different input/output types, and different parsing logic. The boilerplate I/O pattern is insufficient for Type-3/4 similarity.
- 共享行为: Both read data from a URL using HTTP GET；Both use BufferedReader to read line by line；Both build a string by appending lines；Both involve parsing structured data (JSON vs XML)
- 行为差异: A returns a JSONObject; B returns void and updates UI state；A uses Apache HttpClient; B uses URL.openStream()；A does not filter lines; B filters lines starting with '%'；A parses JSON; B parses XML with custom adaptors
- 修正建议: Enhance model to consider functional purpose and output type；Incorporate dataflow analysis to differentiate return value vs side effects；Train on more examples where boilerplate I/O is shared but semantics diverge；Use larger context (e.g., entire method body) to capture the extensive UI code in B

### case_id=4048 FN benchmark_preference_bias

- 方法: `modifyApplicationMessage` vs `readAndRewrite`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Modifies a locale-specific .properties file by reading, updating or adding a key-value pair, and writing back.
- B 摘要: Reads a DICOM image file, parses it, and rewrites the pixel data to another file.
- 静态失败原因: Static BERT likely relied on token overlap (Jaccard 0.05) and common structures like loops and file handling, but missed the deeper functional difference; however the model's prediction (0) is actually correct for this pair.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled as clone due to very broad Type-4 criteria (functionally similar if both involve reading and rewriting a file), but the domain and details are entirely different.
- 共享行为: Both perform file I/O operations (read, process, write).；Both handle exceptions during I/O (one with try-catch, one throws IOException).
- 行为差异: Different file formats: .properties text vs. DICOM binary images.；Different processing logic: line-by-line property substitution vs. pixel data manipulation.；Different input/output: function A creates a new file if missing; function B requires specific DICOM library objects.
- 修正建议: Review BCB annotation for this pair to correct potential over-generalization.；Use domain-aware features or semantic role labeling to distinguish disparate domains.

### case_id=4049 FN boilerplate_overlap

- 方法: `getFile` vs `logging`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies the endpoint in the XML, and saves it to a temporary file, returning the file path; handles various exceptions.
- B 摘要: Logs an inbound message by extracting headers, encoding, and content, copying the input stream to a cached output stream, and writing the cache to a logging buffer; handles IOException.
- 静态失败原因: Static BERT models rely heavily on token overlap and syntactic structure; the low Jaccard similarity (0.1125) and different control flows led it to miss the shared I/O and error-handling patterns.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may label it as a clone due to shared boilerplate patterns (stream I/O, exception handling, logging) within the same web service framework, accepting partial functionality similarity.
- 共享行为: Both involve reading from an InputStream and writing to an OutputStream；Both handle exceptions with logging and throwing a custom fault；Both potentially use temporary files (A for WSDL, B for cached stream)
- 行为差异: Core purpose: A downloads and modifies a WSDL file; B logs a message；A returns a String; B is void；A uses XML parsing and multiple exception types; B only catches IOException
- 修正建议: Incorporate graph-based representations capturing control/data flow；Train on tasks that reward structural pattern matching over token overlap

### case_id=4050 FN benchmark_preference_bias

- 方法: `testCopy_readerToOutputStream_Encoding` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: A unit test that copies a reader to an output stream with a specified encoding and verifies content equality.
- B 摘要: A method that builds a site for editing by processing XML files, performing string replacements, and writing output files.
- 静态失败原因: Static BERT models may correctly reject this pair as non-clones, but the benchmark label itself may be erroneous, making the model appear to fail. Alternatively, the model may have been misled by low token overlap and distinct method names, leading to a correct non-clone prediction that conflicts with a mistaken benchmark label.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB likely annotated this as a false positive clone due to superficial overlap in I/O and encoding usage, or due to annotation error. The extreme dissimilarity in purpose and structure suggests it should not be a clone, even under broad BCB criteria.
- 共享行为: Both involve Java I/O streams (InputStream, OutputStream, Reader, Writer).；Both use character encoding specifications (UTF-16, US-ASCII, UTF-8).
- 行为差异: Function A is a simple test with a single copy operation; Function B is a complex multi-step process with XML parsing, file system operations, and string manipulation.；Function A uses IOUtils.copy; Function B uses custom file reading/writing and transformers.；Function A has a focus on encoding conversion during copy; Function B focuses on website generation with multiple files and paths.
- 修正建议: Re-evaluate the BCB label for this pair to correct potential annotation error.；Use more robust clone detection criteria that incorporate semantic understanding to avoid such false negatives.；Consider using models that can capture deep semantic similarity rather than surface-level token patterns.

### case_id=4051 FN partial_functionality

- 方法: `doTransfer` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.75`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Acts as an HTTP proxy, forwarding request to another URL and returning the response.
- B 摘要: Sends a specific POST request to a RenRen API endpoint and prints the response.
- 静态失败原因: Static BERT models rely on lexical and structural similarity; low token Jaccard (0.18) and different method signatures led to miss of underlying semantic similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BigCloneBench likely labeled this as a clone due to shared HTTP request-response handling pattern, considered functionally similar in Type-4 category.
- 共享行为: Both open an HTTP connection using HttpURLConnection；Both set request method and headers；Both send request body and read response；Both print response status and body
- 行为差异: A dynamically reads request URL from parameter; B has hardcoded URL；A copies all request headers; B only sets specific headers；A forwards response back to original client; B only prints response；A handles input and output streams; B only sends output and reads input
- 修正建议: Improve model to recognize shared sub-structures like HTTP connection pattern；Incorporate data flow analysis to capture common API usage；Use contrastive learning to focus on functional similarity over lexical overlap

### case_id=4052 FP boilerplate_overlap

- 方法: `getUser` vs `sendRequestObjectResponse`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.99`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Loads a user from a DAO; if not found, reads a configuration file to create and save a User object matching the given login.
- B 摘要: Sends an HTTP POST request with compressed XML data to a servlet, saves the response to a file, and returns the file path.
- 静态失败原因: The model likely relied on superficial token/API overlaps (e.g., URL, BufferedReader, try-catch) and structural patterns common in Java I/O code, ignoring the distinct high-level logic and method signatures.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clone because the functions have different purposes, different return types (User vs Object), different parameters, and no meaningful functional overlap; they are not semantically similar even under broad Type-3/Type-4 criteria.
- 共享行为: Both use try-catch blocks with exception printing.；Both read from an input stream (URL.openStream or URLConnection.getInputStream).；Both use java.net.URL and file I/O operations.；Both contain System.out.println statements for debugging.
- 行为差异: Function A retrieves a user by login; Function B sends an HTTP request and saves the response.；Function A parses text lines with StringTokenizer; Function B uses GZIP compression and writes XML.；Function A interacts with a database (UserDAO); Function B interacts with a remote servlet and writes files.；Function B has GUI components (IP dialog, browser) not present in Function A.
- 修正建议: Incorporate method signature and return type information.；Use dataflow or AST-based representations to capture semantic intent.；Train with more discriminative negative pairs that share common boilerplate but differ in core functionality.；Apply contrastive learning to emphasize semantic differences over lexical overlap.

### case_id=4053 FP lexical_or_api_overlap

- 方法: `run` vs `readUNI`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a resource file from classpath and sets its content as text in a GUI panel.
- B 摘要: Reads a TSV file from a URL and parses it into a vector of concatenated id and desc strings.
- 静态失败原因: Static BERT may have overfitted to common I/O boilerplate (URL, openStream, close) and sequential read loop, ignoring high-level semantics.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clone because the methods serve entirely different purposes (GUI display vs data parsing) despite sharing low-level I/O patterns.
- 共享行为: Both open a URL stream and read lines of text；Both close the input stream after reading
- 行为差异: A reads from classpath resource, B from arbitrary URL；A appends all lines with CRLF, B parses tab-separated fields；A updates GUI, B accumulates data into a vector；Exception handling differs: A silently swallows, B prints stack trace
- 修正建议: Integrate control flow analysis to distinguish GUI vs data-processing logic；Incorporate semantic role labeling for method parameters and return types

### case_id=4054 FN partial_functionality

- 方法: `createFile` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Creates a file by copying the content of a source File to a resource manager output stream using IOUtils.copy.
- B 摘要: Downloads a KMZ file from a URL, extracts its zip entries, and writes them to local files using manual buffer copying.
- 静态失败原因: Static BERT models rely on token overlap, which is low (0.115), and fail to capture the high-level semantic similarity of data copying due to lack of understanding of I/O patterns and utility functions.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label as clone because both functions implement a generic data transfer pattern from an input source to an output destination, which is considered semantically similar under Type-4 lenient criteria.
- 共享行为: Both read from an InputStream and write to an OutputStream；Both perform a data copy operation；Both handle input/output resources
- 行为差异: A copies a single file to a managed resource; B downloads from URL, decompresses zip, and writes multiple entries；A uses IOUtils.copy utility; B uses explicit while loop with buffer；A handles ResourceManagerException; B throws Exception；A uses FileInputStream from local file; B determines stream source based on URL protocol
- 修正建议: Use data flow analysis to detect generic copy operations；Incorporate structural similarity of I/O stream usage；Leverage a model that captures program intent via larger context or intermediate representations

### case_id=4055 FN partial_functionality

- 方法: `getHTML` vs `readIntoList`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.65`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads HTML from a URL, optionally writes to file, and returns the content as a string.
- B 摘要: Reads HTML from a URL, parses anchor tags to extract command names, and populates a map of JMenuItem objects with action listeners.
- 静态失败原因: Static BERT likely focused on lexical tokens like 'BufferedReader', 'readLine', and 'URL', failing to capture the divergent high-level purposes and output behaviors.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label them as clones due to superficial similarities: both use URL, BufferedReader, read lines in a loop, and handle exceptions; the partial overlap in reading HTML from a URL might be considered Type-3/Type-4 in BigCloneBench's broad annotation style.
- 共享行为: Both read lines from a URL using BufferedReader and InputStreamReader
- 行为差异: Function A returns the entire HTML content as a string; Function B returns void and modifies a map；Function A optionally writes to a file; Function B creates UI components and sets action commands；Function A appends lines to a StringBuilder; Function B parses each line for specific HTML tags
- 修正建议: Incorporate dataflow analysis to distinguish functions with different outputs；Enhance representation of overall function purpose beyond token overlap；Use control flow structure to differentiate simple retrieval from parsing and UI construction

### case_id=4056 FP partial_functionality

- 方法: `SRWGuiClient` vs `handledRun`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.85`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sets up a Swing browser GUI, reads XML from a URL, optionally applies XSLT transformation, and displays HTML.
- B 摘要: Downloads a gamedata XML file from a URL, checks version, and updates local file if newer.
- 静态失败原因: Static BERT models may focus on token similarity (e.g., 'URL', 'BufferedReader') and miss the overall semantic context and control flow, leading to a false positive.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB typically labels clones based on functional similarity; these functions have different purposes (GUI vs data download) and different data processing, so they are not considered clones.
- 共享行为: Both open a URL and read data using BufferedReader；Both handle IOException and other exceptions
- 行为差异: Function A is a constructor for a GUI browser; Function B runs a background update；Function A optionally applies XSLT transformation; Function B checks version and writes to a file；Function A displays HTML in a JEditorPane; Function B updates a local game database
- 修正建议: Train on more varied examples to distinguish similar API usage in different contexts；Incorporate global structure or control flow information

### case_id=4057 FP boilerplate_overlap

- 方法: `callApiPost` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Sends an HTTP POST request with parameters, checks response code, and returns response input stream, throwing exception on mismatch.
- B 摘要: Builds a Google image search URL, performs HTTP GET request, parses HTML for image links, and collects them into a list.
- 静态失败原因: Static BERT models may overemphasize overlapping API sequences (URL, HttpURLConnection, exception handling) and miss the deeper semantic differences such as HTTP method, data flow, and overall goal.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels non-clones when functions have different purposes and application contexts, despite sharing some API usage patterns.
- 共享行为: Both set up HTTP connections using URL and HttpURLConnection.；Both handle exceptions with try-catch blocks.；Both read from input streams.
- 行为差异: A uses POST method, B uses GET.；A sends parameters in request body, B appends query string to URL.；A expects specific response code, B does not check response code.；A returns InputStream, B populates a list of image URLs.
- 修正建议: Incorporate data flow and control flow analysis to distinguish POST vs GET and return type.；Use task-oriented abstraction to capture function purpose.；Train on more diverse examples with similar boilerplate but different semantics.

### case_id=4058 FN partial_functionality

- 方法: `copyResource` vs `readAndRewrite`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.4`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource from a URL or file to a destination file using byte-by-byte streaming.
- B 摘要: Reads a DICOM file, parses it, reads pixel data, and writes it back to a new file.
- 静态失败原因: The static BERT model likely relies on token similarity and structural patterns. The token Jaccard is very low (0.1), and the code structures are different (one simple loop, one complex sequence of DICOM API calls). The model correctly predicted non-clone based on surface features, but BCB's label suggests deeper semantic similarity that the model missed.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB might treat these as clones because both are about copying data from one place to another, which is a common semantic pattern, even though the implementation details differ greatly.
- 共享行为: Both involve reading from an input source and writing to an output file using streams.
- 行为差异: Code A uses simple byte reading/writing; Code B uses complex DICOM-specific parsing and pixel data handling.；Code A handles both URL and file input; Code B only file input.；Code B has many more steps and outputs debug messages.
- 修正建议: Incorporate data flow or abstract representations to capture high-level intent.；Use domain adaptation or contrastive learning to recognize broader semantic patterns.

### case_id=4059 FP long_range_semantics

- 方法: `readZoneIDs` vs `handledRun`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `static_summary_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads zone IDs from a resource file and returns a set of integers.
- B 摘要: Handles the run of a download task to update game data from an online XML file, with version checking and file writing.
- 静态失败原因: Static BERT/GraphCodeBERT models might have been misled by the shared structural pattern of opening a URL, try-catch blocks, and reading lines, leading them to overestimate similarity despite radically different semantic intents and I/O behavior.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely labels this as non-clone because the functions have entirely different purposes and output. The only overlapping pattern is generic URL reading, which is not sufficient for functional similarity in BigCloneBench's standard.
- 共享行为: Both open a URL stream and read data from it.；Both use try-catch for exception handling.；Both involve reading lines from an input stream.
- 行为差异: Function A returns a HashSet of integers; Function B is void and performs side effects.；Function A is a simple file reader; Function B involves conditional version checking and file writing.；Function A reads from a class resource; Function B reads from a hardcoded URL.；Function B has complex error handling with user dialog and logging; A only prints stack trace.
- 修正建议: Improve modeling of function return types and side effects.；Incorporate more robust understanding of the overall task (e.g., reading IDs vs. version update).；Use dataflow analysis to distinguish reading from writing operations.

### case_id=4060 FP lexical_or_api_overlap

- 方法: `main` vs `copy`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: A main method that parses a Prolog file, generates adapters, and writes them to a JAR.
- B 摘要: A private method that copies the contents of one file to another.
- 静态失败原因: Static BERT likely over-relied on shared lexical items (e.g., 'File', 'IOException', 'read', 'write', 'close') despite low overall token overlap.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would label this non-clone because the two functions perform entirely different tasks with no overlap in core functionality.
- 共享行为: Both involve file I/O operations (reading/writing).
- 行为差异: Function A is a complex adapter generation pipeline; Function B is a simple file copy.；Function A handles multiple file formats, JAR writing, serialization; Function B only copies text content.；Function A has CLI argument parsing and error handling; Function B has minimal error handling.
- 修正建议: Enhance negative sampling with pairs that share API keywords but differ semantically.；Incorporate structural or control-flow differencing to detect misalignment in functionality.

### case_id=4061 FN benchmark_preference_bias

- 方法: `main` vs `readAndRewrite`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.6`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Extracts files from a zip archive downloaded from a URL.
- B 摘要: Reads and rewrites a DICOM medical image file, converting pixel data.
- 静态失败原因: The static model likely failed because it relies on token-level similarity or structural patterns, and the low Jaccard similarity (0.118) indicates little lexical overlap. It may not capture deep semantic differences despite both being I/O routines, as the core logic (zip extraction vs. DICOM processing) is distinct and requires domain-specific knowledge.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB considers these as clones possibly because both involve reading from an input, processing, and writing to an output, which fits a broad 'file manipulation' category. However, the specific operations are entirely different, and this label likely reflects a false positive in BCB annotation due to overly broad interpretation of partial functionality similarity.
- 共享行为: Both perform file I/O operations using streams.；Both read from an input source and write to an output.；Both handle binary data and use buffered streams.
- 行为差异: Function A processes a zip archive, extracting multiple entries; Function B processes a single DICOM file, handling metadata and pixel data.；Function A uses ZipInputStream and ZipEntry; Function B uses DICOM-specific classes like DcmParser, Dataset, PixelDataReader.；Function A writes to files named after zip entries; Function B writes to a specified output file with DICOM encoding.；Function A deals with network protocols (http, file); Function B deals only with local files.
- 修正建议: Incorporate data-flow and control-flow analysis to capture functional differences.；Use domain-specific heuristics to distinguish I/O patterns (e.g., zip vs. DICOM APIs).；Train on benchmark with stricter clone definitions to avoid overly broad labeling.；Encourage models to focus on method-level semantics rather than peripheral stream handling.

### case_id=4062 FP lexical_or_api_overlap

- 方法: `sendPost` vs `downloadModel`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Sends an HTTP POST request with parameters and returns the response as a string.
- B 摘要: Downloads an RDF model from a URL via HTTP GET and returns a Model object.
- 静态失败原因: Static BERT/GraphCodeBERT may rely on token overlap and structural similarity. Both functions have similar boilerplate for opening HTTP connections and reading input streams, leading to high token overlap. The model may have focused on these common patterns rather than the distinct semantic purpose (POST vs. GET) and different return handling.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels functions as non-clones when they perform different high-level tasks, even if they share some common HTTP connection code. The semantic purpose and return type differ, so BCB likely considers them non-clones.
- 共享行为: Both open URL connections；Both set HTTP request properties；Both handle exceptions
- 行为差异: A sends POST data with parameters, B does not send data；A returns a String, B returns a Model object；A reads response line by line, B reads model using model.read()；Error handling differs: A catches generic Exception and shows message, B catches specific IO exceptions and throws RuntimeException
- 修正建议: Improve handling of long-range semantic differences by incorporating control flow and data dependencies；Focus on distinguishing between POST and GET operations and the final return type；Use graph-based representations that capture data flow and method call sequences more deeply

### case_id=4063 FN partial_functionality

- 方法: `doGet` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Handles HTTP GET request to display a portal page, with caching and logging.
- B 摘要: Copies a file from source to destination using FileChannel.
- 静态失败原因: The static model correctly predicted no clone based on low lexical overlap (Jaccard=0.0656) and clearly different control flow and domain; it was not misled by any superficial similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have considered the file I/O sub-task in code A (writing to a temporary cache file) as similar to code B's file copy, leading to a broad Type-4 clone label despite overall functional difference.
- 共享行为: Both perform file I/O operations (code A writes a cache file, code B copies a file)
- 行为差异: Code A processes HTTP request, manages page retrieval, permissions, and caching; Code B is a simple file copy utility.；Code A has complex logic with multiple conditionals and external dependencies; Code B is straightforward.
- 修正建议: Refine BCB annotation guidelines to require stronger overall semantic equivalence, avoiding labeling based on minor sub-function overlap.；Use multiple clone-type categories to distinguish full clones from partial ones.

### case_id=4064 FP boilerplate_overlap

- 方法: `run` vs `main`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches a tile from a data source via URL, synchronizes to avoid duplicate requests, reads the content, parses it into a VectorTile, extracts geometries, and adds them to a data loader while updating a display cache.
- B 摘要: Reads the content of a fixed URL line by line and prints each line to the console.
- 静态失败原因: The static model was misled by high lexical overlap of common boilerplate patterns (URL creation, BufferedReader, while loop) and ignored the large surrounding code that differs in higher-level semantics.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as not a clone because the overall functionality is completely different; the common URL reading is a standard library usage, not indicative of clone, and BCB focuses on functional similarity rather than shared code snippets.
- 共享行为: Both open a URL and read its content using BufferedReader and InputStreamReader.
- 行为差异: A does duplicate request checking via synchronization; B does not.；A parses the content into VectorTile and geometry objects; B just prints lines.；A adds data to a data loader and updates display cache; B has no side effects beyond printing.；A handles file and http protocols; B only http.
- 修正建议: Incorporate data flow and control flow graphs to differentiate boilerplate from core logic.；Use contrastive learning to distinguish common idioms from truly similar functionality.；Augment training with pairs having high boilerplate overlap but different semantics.；Consider larger context windows or attention to capture overall method purpose beyond local patterns.

### case_id=4065 FP lexical_or_api_overlap

- 方法: `importSequences` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads sequence data from an input stream, parses names and sequences, and stores them in lists.
- B 摘要: Performs a Google image search, parses image URLs, and updates a UI component.
- 静态失败原因: The model likely overemphasized lexical overlap in API calls (URL, InputStream, BufferedReader, readLine, replace, catch blocks) and structural similarity (try-catch, reading lines), ignoring the semantic differences in purpose and data processing.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would not label these as clones because their core functionality is entirely different; one is data import, the other is web image search with GUI update. The only similarity is generic I/O pattern, which is insufficient for clone labeling.
- 共享行为: Both use Java I/O to read from a URL or stream；Both handle exceptions with try-catch blocks；Both use string manipulation (replace, tokenization)
- 行为差异: A imports biological sequences into data structures; B searches for images and updates GUI；A uses ImportHelper for parsing; B uses HttpURLConnection and HTML parsing；A catches specific exceptions; B catches generic Exception；A modifies instance variables; B also updates UI components
- 修正建议: Improve model to focus on high-level semantics rather than surface-level API usage；Incorporate dataflow or control-flow analysis；Use domain-specific knowledge to differentiate unrelated tasks

### case_id=4066 FP lexical_or_api_overlap

- 方法: `readReferenceText` vs `getRequestContent`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads entire text file from plugin bundle as string, with exception handling.
- B 摘要: Reads first line from an HTTP URL response, throwing Exception.
- 静态失败原因: Overlap in URL handling and BufferedReader usage misled the model; it missed the control flow difference between loop and single read.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely annotates as non-clone because the functional output differs (all content vs first line) and the error handling approach is distinct.
- 共享行为: Both open a URL connection and read a line using BufferedReader；Both return a String
- 行为差异: A reads all lines; B reads only the first line；A handles specific exceptions and logs; B declares generic Exception；A uses plugin bundle context; B uses direct HTTP connection；A appends newlines; B does not
- 修正建议: Incorporate control flow awareness to distinguish all-line reading from single-line reading；Consider output behavior (full content vs first line) in similarity measurement

### case_id=4067 FN partial_functionality

- 方法: `readGeoParserResult` vs `addQDInformation`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads geographic parser results by sending an XML request to a remote service, parsing the response to extract place names and gazetteer IDs, with retry on failure.
- B 摘要: Reads QD information from a local file or remote URL, parses lines to update internal state based on date and value entries.
- 静态失败原因: Static BERT/GraphCodeBERT relies heavily on token overlap (Jaccard 0.144) and lexical patterns; the differing APIs (XML vs line parsing), variable names, and overall structure result in low similarity score. The model failed to recognize the abstract shared behavior pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this as clone due to broad Type-3/Type-4 interpretation: both functions read external data, parse it, and update data structures, sharing common boilerplate (URL, BufferedReader, line reading, exception handling). The annotation guidelines accept partial functional similarity.
- 共享行为: Both use URL or file I/O to read external data；Both use BufferedReader and while loop to read lines；Both parse the input content (XML or custom line format)；Both handle exceptions (IOException, etc.)
- 行为差异: A sends an HTTP request with XML payload; B reads directly from file/URL；A parses XML; B parses lines with prefixes 'pg ' and 'pt '；A returns a collection; B modifies instance fields and project info objects；A has retry logic; B does not
- 修正建议: Incorporate AST or data-flow features to capture structural similarity beyond tokens；Use contrastive learning with BCB Type-3/Type-4 examples to learn abstract patterns；Augment training data with pairs having low lexical but high structural overlap

### case_id=4068 FN partial_functionality

- 方法: `executeHttpGet` vs `getEncoding`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Executes an HTTP GET request and returns the response body as a JSONObject.
- B 摘要: Extracts character encoding from an HTTP response by searching headers and content.
- 静态失败原因: Static BERT models may over-rely on token overlap (e.g., HttpClient, BufferedReader, readLine) and miss the distinct functional goals and dataflow differences.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled as clone due to both being HTTP client utilities that read data from responses, despite different specific outputs.
- 共享行为: Both use HTTP connections；Both read from input streams using BufferedReader；Both parse data from the response
- 行为差异: A returns JSONObject, B returns String (encoding)；A uses HttpClient, B uses URLConnection；A only reads from response entity, B searches headers and content for charset；A does not extract encoding, B explicitly does
- 修正建议: Integrate dataflow analysis to track output types and transformation chains；Train with contrastive examples that differ in purpose despite similar token sets；Use functional categorization to distinguish retrieval vs parsing

### case_id=4069 FP lexical_or_api_overlap

- 方法: `importSequences` vs `SRWGuiClient`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Imports sequence data from a selected URL by parsing FASTA-like format into names and sequences.
- B 摘要: Constructor that builds a Swing GUI browser, fetches XML from a URL, optionally applies XSLT transformation, and displays the resulting HTML.
- 静态失败原因: Static BERT/GraphCodeBERT likely over-counted lexical tokens like 'URL', 'InputStream', 'BufferedReader', 'catch', and 'try' which are common in many Java I/O operations, leading it to overestimate similarity.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the two functions serve completely different purposes (data import vs. GUI construction) and share only trivial API usage patterns.
- 共享行为: Both open a URL and read content using InputStreamReader and BufferedReader.；Both catch IOException and perform exception handling.
- 行为差异: Function A parses sequence data (FASTA-like) into lists; Function B displays a GUI and does XML/XSLT processing.；Function A uses ImportHelper for reading; Function B uses manual BufferedReader and JEditorPane for display.；Function A has no GUI or transformation logic; Function B is entirely GUI-centric.
- 修正建议: Train with more diverse negative examples that have overlapping API but different semantics.；Include long-range semantic features or dataflow information to distinguish high-level intent.

### case_id=4070 FN benchmark_preference_bias

- 方法: `storeImage` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Stores an image from an input stream to a file, optionally resizing it and returning the relative path.
- B 摘要: Handles Eclipse launch configuration validation, processes Maven pom files, and sets up reverse engineering resources.
- 静态失败原因: Static BERT correctly identified low semantic similarity and predicted non-clone, which is likely the correct judgment; the BCB label appears to be erroneous.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have incorrectly labeled this as clone due to superficial similarities like file I/O, property reading, and logging, but the overall functionality is completely different.
- 共享行为: Both use IOUtils.copy for stream copying.；Both create new files (createNewFile, revengFile.create).；Both use logging via Logger.info.
- 行为差异: A writes image data and returns a path; B modifies Eclipse project configuration and returns void.；A deals with image resizing logic; B deals with Maven pom.xml and Hibernate dialect configuration.；A uses Calendar for date-based directory naming; B uses Eclipse workspace resources and persistent properties.；A has a simple conditional for resizing; B has nested callbacks and exception handling for CoreException.
- 修正建议: Re-evaluate BCB annotation for this pair to correct the label to non-clone.；Improve dataset consistency by ensuring clones require clear functional overlap beyond basic I/O operations.

### case_id=4071 FN boilerplate_overlap

- 方法: `getResourceAsStream` vs `convert`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.4`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a resource from a URL, caches it locally, and returns an input stream for the cached file.
- B 摘要: Converts an ACRNEMA medical image file to DICOM format, handling pixel data inflation and metadata.
- 静态失败原因: Low token overlap (0.13) and distinct vocabulary; static BERT embeddings likely focus on surface-level tokens (e.g., 'DcmParser', 'cache') rather than abstract stream-manipulation structure.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may view both as 'stream-copy' operations with additional conditional logic, considering them Type-4 clones due to similar I/O patterns despite different domains.
- 共享行为: Read from input stream and write to output stream；Use buffered streams；Print debug messages to console；Handle exceptions and close streams in finally blocks
- 行为差异: A involves HTTP caching and resource retrieval; B involves medical image format conversion；A has conditional logic for HTTP response codes; B has domain-specific pixel data manipulation；A returns an InputStream; B writes to a file and does not return a value
- 修正建议: Use dataflow-aware models like GraphCodeBERT to capture variable dependencies and control flow.；Augment training data with diverse I/O-intensive functions to emphasize boilerplate overlap.；Incorporate syntactic structure features (e.g., AST patterns) to identify common stream-handling idioms.

### case_id=4072 FP partial_functionality

- 方法: `loadURL` vs `getXML`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Loads a URL with optional basic auth, reads response line by line, writes to a temporary file, and optionally updates a status label with file size.
- B 摘要: Fetches XML from a servlet URL by encoding a request, reading the response lines, and concatenating them into a String, returning null on error.
- 静态失败原因: Static BERT/GraphCodeBERT may have overemphasized the structural similarity (both read from URL, use BufferedReader, loop) and missed the semantic differences. The low token Jaccard suggests limited lexical overlap, but the model might have focused on common tokens like 'BufferedReader', 'readLine', 'URL'.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely considered these non-clones because the overall functionality (downloading and saving to file vs fetching XML string) is different, and the API usage patterns differ significantly.
- 共享行为: Both open a URL connection and read lines using BufferedReader.
- 行为差异: A writes to file, B returns string.；A handles basic auth, B encodes request.；A updates status label, B does not.；A throws IOException, B catches and returns null.
- 修正建议: Incorporate more global context such as control flow and data dependencies.；Use contrastive learning to distinguish file writing vs string building.；Include output type and side-effect information in the representation.

### case_id=4073 FN boilerplate_overlap

- 方法: `modifyApplicationMessage` vs `copyLogic`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Modifies a localized properties file by updating or adding a message key-value pair.
- B 摘要: Copies a class file from source to destination using file channels, with state management.
- 静态失败原因: Low token Jaccard (0.1287) and different method names, plus distinct API calls (Properties vs FileChannel), cause static models to focus on surface differences rather than the shared file I/O pattern.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: Both methods perform file I/O with similar boilerplate (open, read/write, close, exception handling). BCB's broad annotation includes Type-3 clones where syntactic structure is similar despite different specific operations, especially when both are file manipulation routines.
- 共享行为: Perform file I/O operations (reading and writing files)；Handle exceptions by printing stack trace；Close resources after use
- 行为差异: A operates on text properties files with locale-specific paths; B operates on binary class files with fixed paths；A reads line by line and modifies content; B transfers bytes entirely using FileChannel；A may conditionally create a new file; B does not create files；B manages execution state (setState/Idle/Synchronizing); A has no state management
- 修正建议: Enhance models with data flow analysis to distinguish core logic from boilerplate；Use contrastive learning to learn representations that capture file I/O patterns across different domains；Incorporate method-level context (e.g., class name, surrounding methods) to infer purpose

### case_id=4074 FN partial_functionality

- 方法: `modifyApplicationMessage` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Modifies an internationalization properties file for a given locale, optionally copying the English file if missing.
- B 摘要: Copies a file from source to destination using NIO FileChannel, creating parent directories.
- 静态失败原因: The model over-relied on lexical and syntactic features (low token Jaccard) and failed to capture the abstract common file copy operation due to different API usage and additional logic in A.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considered the core file copying functionality as the main semantic similarity, treating A as a specialized variant that includes copy as a subtask, thus labeling it a Type-4 (semantic) clone.
- 共享行为: Both perform file copying operations；Both handle file I/O exceptions
- 行为差异: Function A includes properties parsing and modification; B does not；A uses Reader/Writer for copy; B uses FileChannel and transferFrom；A has logic for creating locale-specific file if missing; B simply copies
- 修正建议: Incorporate dataflow analysis to detect common sub-patterns like file copy；Use hierarchical or modular clone detection that identifies shared functionality；Train models on aligned sub-sequence representations of I/O operations

### case_id=4075 FP lexical_or_api_overlap

- 方法: `main` vs `copyFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: main method that generates adapter classes from a Prolog file, handling I/O and parsing.
- B 摘要: utility method that copies a file from source to destination with a buffer.
- 静态失败原因: The model likely overemphasized token surface similarity, such as shared keywords (File, IOException, try, catch, InputStream, OutputStream, logger) and general structure (method signature, I/O operations), ignoring deep semantic differences.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the functions perform completely different tasks with no overlapping functionality.
- 行为差异: Function A generates code and manipulates JAR files; Function B simply copies a file.；Function A has complex control flow with multiple stages; Function B has straightforward read-write loop.；Function A uses reflection, class loading, and serialization; Function B uses basic file streams.
- 修正建议: Incorporate structure-based features like abstract syntax tree or control flow graph to capture method intent.；Use contrastive learning on clone pairs with high token overlap but different semantics.；Add a dataflow analysis module to differentiate file copy from complex multi-step generation.

### case_id=4076 FP lexical_or_api_overlap

- 方法: `executePost` vs `wordFrequency`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Performs an HTTP POST request with parameters and returns the full response body as a string.
- B 摘要: Fetches a web page, searches for a regular expression pattern indicating word frequency, and returns the matched integer (or 0 if not found).
- 静态失败原因: The static BERT model likely relied on token overlap (e.g., URL, BufferedReader, readLine, catch, printStackTrace) and didn't capture the high-level semantic difference in the overall task (POST with parameter sending vs. GET and frequency extraction). The model may have been fooled by the common 'boilerplate' of Java I/O and network code.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BigCloneBench typically labels non-clones when functions have different inputs, outputs, and algorithmic purposes, even if they share common I/O patterns. Here, the functions are functionally unrelated (one is a generic HTTP client utility, the other is a web scraping parser for a specific task), so BCB correctly marks them as non-clones.
- 共享行为: Both open an HTTP connection to a URL；Both read the response line-by-line using BufferedReader；Both handle exceptions with printStackTrace；Both close resources in some manner
- 行为差异: Function A sends parameters via POST; Function B uses a GET request with a word inserted into a URL template；Function A returns the entire response body; Function B parses the response to extract an integer frequency；Function A has explicit connection management (HttpURLConnection), while Function B uses URL.openStream()；Function A manages request properties (Content-Type, Content-Length) and output stream; Function B does not send output
- 修正建议: Enhance model with dataflow analysis to distinguish different return types and loop purposes；Use AST-based features to capture method signatures and control flow differences；Train with more negative examples of similar-boilerplate but different-semantics pairs；Incorporate information about the function's overall I/O (e.g., input/output types, side effects)

### case_id=4077 FP boilerplate_overlap

- 方法: `hash` vs `perform`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Hashes input string using specified algorithm and returns hex string.
- B 摘要: Processes a web request for concept classification, managing session, beans, and making HTTP connection to get XML result.
- 静态失败原因: Likely due to lexical overlap in common Java boilerplate (StringBuffer, try-catch, loops, byte arrays) causing false positive similarity.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would not consider them clones because they have no common functionality or structural similarity; one is a general-purpose hash utility, the other is a domain-specific web action.
- 共享行为: Both use StringBuffer for string building
- 行为差异: One is a simple utility hash function, the other is a complex web action controller；Different inputs/outputs: String vs HTTP request/response；Different libraries: MessageDigest vs Struts/XML/Servlet
- 修正建议: Enhance model to ignore boilerplate patterns；Incorporate functional role detection or API usage semantics；Use data flow analysis to distinguish core logic from generic constructs

### case_id=4078 FN benchmark_preference_bias

- 方法: `modifyApplicationMessage` vs `runDynusT`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Modifies a key-value pair in a locale-specific properties file, creating it from an English template if missing.
- B 摘要: Copies executable and model files to a temporary directory, runs an external simulation executable (DynusT.exe) with a timeout, and optionally cleans up executable files.
- 静态失败原因: The static model correctly predicted 0 (non-clone) as the functions are semantically distinct; it failed relative to the BCB label, suggesting the BCB annotation may be erroneous.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as a clone due to both involving file I/O and copying, possibly considering it a broad Type-4 clone for 'file setup' operations, but the functional purposes are entirely different.
- 共享行为: Both functions check file existence and copy files between directories.
- 行为差异: Function A edits text (properties) while Function B runs an external binary.；Function A is for localization configuration; Function B is for launching a simulation.；Function A reads/writes properties; Function B copies files and executes a process.
- 修正建议: Re-examine BCB annotation for this pair to verify correctness.；Do not penalize the model for disagreeing with a potentially incorrect ground truth.

### case_id=4079 FN partial_functionality

- 方法: `run` vs `File2String`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Performs an HTTP GET request with Basic authentication, reads response line by line with newlines appended, stores result and updates timestamp.
- B 摘要: Reads a file from filesystem or classpath, concatenates lines without newlines, returns content as string, exits on failure.
- 静态失败原因: Low token overlap (0.193) and different API surface (HttpURLConnection vs FileInputStream/URL) caused the model to miss the underlying functional similarity of reading lines from an InputStream into a StringBuffer.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB considers both functions as reading text line by line from an input stream and concatenating into a string, which is a common Type-4 pattern (partial functionality similarity) despite differences in source, error handling, and line formatting.
- 共享行为: Reads lines from an input stream into a StringBuffer；Returns the accumulated string
- 行为差异: Source: HTTP URL vs file (local or classpath)；Line handling: includes newlines vs no newlines；Authentication: sets Authorization header vs none；Error handling: stores exception and continues vs print and System.exit(-1)
- 修正建议: Train on data-level or flow-level representations that capture I/O reading patterns；Use clone detection that focuses on control flow and data flow rather than surface tokens；Incorporate heuristics for input-stream-to-string transformation patterns

### case_id=4080 FN boilerplate_overlap

- 方法: `extractUninstallFiles` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.85`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Extracts uninstall files during upgrade or fresh install, handling backup and file copying.
- B 摘要: Retrieves a resource as an InputStream with caching from a URL, using HTTP conditional GET.
- 静态失败原因: Low token Jaccard (0.16) and high-level semantic divergence led the model to classify them as non-clones, missing potential boilerplate overlap.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may consider them clones due to structural similarity in stream handling and exception patterns, despite different high-level purposes.
- 共享行为: Both perform file I/O and use BufferedInputStream/BufferedOutputStream
- 行为差异: A deals with local file system and jar entries; B deals with remote resources and caching
- 修正建议: Incorporate control-flow and data-flow features；Use graph-based representations to capture structural similarity beyond lexical tokens

### case_id=4081 FN partial_functionality

- 方法: `modifyApplicationMessage` vs `setup`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.1`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Modifies a properties file by replacing or adding a message value for a given locale.
- B 摘要: Extracts native libraries from a JAR file to a temporary directory and configures the library path.
- 静态失败原因: Static BERT/GraphCodeBERT models may have failed to distinguish because they rely on token-level patterns and API usage, which overlap significantly (File, InputStream, FileWriter, etc.). The model might not capture the higher-level semantic difference in application logic.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled these as clones due to broad functional similarity in file manipulation and resource management, or due to annotation bias in the benchmark (e.g., both involve reading and writing files in a loop). However, their purposes are entirely different.
- 共享行为: Both perform file I/O operations (reading, writing, checking existence)；Both handle exceptions and use try-catch blocks
- 行为差异: A modifies a properties file for internationalization; B extracts native libraries for JNI；A uses Properties, BufferedReader, and StringBuilder; B uses ZipInputStream, FileOutputStream, and system property checks；A is public and takes parameters; B is private static and takes no parameters；A may create or copy files; B creates temporary directories and unzips entries
- 修正建议: Incorporate data-flow analysis to understand variable dependencies and output；Use control-flow and call-graph information to differentiate utility functions；Train on more diverse negative examples with similar API usage but different semantics

### case_id=4082 FN partial_functionality

- 方法: `testNetworkHTTP` vs `doVersionCheck`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Makes multiple HTTP GET requests to external URLs, reading response lines without processing, likely for testing data exfiltration.
- B 摘要: Opens a version check URL, reads response lines to extract development and stable build numbers, then invokes an update check method.
- 静态失败原因: Static BERT/GraphCodeBERT models rely heavily on token overlap and semantic embeddings; the low Jaccard similarity (0.207) and different method names, plus the distinct functional objectives (data exfiltration test vs version check) likely pushed the embedding to consider them dissimilar. The model also may not capture the high-level structural pattern of HTTP reading routine.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label these as clones because both functions share the same underlying pattern of opening a URL, reading line by line, and handling exceptions. The structural similarity and common API usage (URL, HttpURLConnection, BufferedReader, InputStreamReader) outweigh the differences in what they do with the data. BCB Type-3/4 clones often accept such superficial similarity.
- 共享行为: Both open HTTP connections using URL objects；Both read from input streams using BufferedReader line by line；Both handle IOException with exception handling；Both close the connection (disconnect or close stream)
- 行为差异: Function A sends personal data (IMEI, phone, etc.) as query parameters, while Function B reads a static version-check URL；Function A does not process the response data; Function B parses lines for .build and .stablebuild prefixes；Function A is a test method (void, no parameters); Function B is a static utility method that takes a View and updates UI (show/hide cursor)；Function A has multiple sequential connections; Function B makes one connection
- 修正建议: Train with more emphasis on structural patterns like HTTP connection sequences；Incorporate data flow analysis to detect that both read from HTTP streams；Use contrastive learning with pairs that share API usage but different semantics

### case_id=4083 FP boilerplate_overlap

- 方法: `readUNI` vs `executeHttpGet`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.85`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads tab-separated data from a URL and populates a Vector with concatenated id and description.
- B 摘要: Performs an HTTP GET request and returns the response as a JSONObject.
- 静态失败原因: The model likely over-relied on shared boilerplate patterns (try-catch-finally, stream handling) and the general structure of reading lines from a network source, ignoring the significantly different core logic and data types.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB considers this non-clone because the functions have fundamentally different purposes and outputs despite a superficial similarity in network I/O.
- 共享行为: Both fetch content from a URL/URI；Both read content line by line
- 行为差异: A parses tab-separated fields while B returns raw JSON；A uses Scanner and accumulates into Vector, B uses BufferedReader and returns JSONObject；A handles exceptions internally, B throws Exception；A is void, B returns JSONObject
- 修正建议: Incorporate data flow analysis to track output types and transformations；Focus on functional signatures (return type, parameters) and domain-specific operations like parsing

### case_id=4084 FP boilerplate_overlap

- 方法: `readZoneIDs` vs `run`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a file containing integer zone IDs and returns them as a set.
- B 摘要: Downloads tile geometry data from a URL, processes it into vector tiles, and loads it into a data source.
- 静态失败原因: The model likely overemphasized lexical overlaps such as 'URL', 'InputStreamReader', 'readLine', and 'try-catch', while ignoring the vastly different semantics and context. The high-level tasks (reading integers vs. downloading/processing tile geometries) are distinct, but the surface token patterns are common in Java I/O, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would label as non-clone because the methods have entirely different purposes and outputs; the only similarity is generic I/O boilerplate, which does not constitute functional or structural clone under BCB guidelines.
- 共享行为: Both open a URL and read lines from an input stream.；Both use try-catch blocks for exception handling.
- 行为差异: Function A parses integers into a HashSet; Function B reads JSON and creates geometry objects.；Function B includes synchronization and duplicate request prevention; Function A does not.；The output type and purpose are completely different: a set of integers vs. loading tile data into a data loader.
- 修正建议: Incorporate more structural features like method signatures and class context.；Increase weighting on unique keywords relevant to specific functionality (e.g., HashSet, VectorTile, GeometryCollection).；Use data flow analysis to differentiate input/output types.

### case_id=4085 FN lexical_or_api_overlap

- 方法: `doRawRequest` vs `login`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends HTTP POST with raw data and returns full response body.
- B 摘要: Encodes login credentials, sends HTTP POST, extracts session ID from response, and sets session.
- 静态失败原因: The model likely relied on low token Jaccard (0.338) and focused on lexical differences such as method names, URL strings, encoding methods, and error handling. It failed to recognize the shared structural pattern of HTTP request handling.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may consider them as Type-3 or Type-4 clones because both implement the core pattern of an HTTP POST request with output and input, which is a common functionality. The differences in data preparation and response parsing are viewed as variations on the same template.
- 共享行为: Both open a URL connection with setDoOutput(true)；Both write data to the output stream；Both read the response from the input stream；Both close the writer and reader
- 行为差异: Function A takes raw postData; Function B constructs data from email/pw with URL encoding；Function A returns the entire response; Function B reads only the first line and extracts session ID；Function B has error handling and prints messages; Function A throws IOException；Function B has side effect (set_session); Function A has none
- 修正建议: Incorporate graph-based representations to capture control and data flow of HTTP request sequences；Normalize or abstract away specific URL strings and encoding details；Train on more examples of clone pairs with similar skeleton but different parameters

### case_id=4086 FP partial_functionality

- 方法: `actionPerformed` vs `main`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.85`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Handles GUI action events and saves/updates application preferences.
- B 摘要: Copies a file from a specified byte offset using command-line arguments.
- 静态失败原因: The model likely focused on superficial syntactic similarities (e.g., conditional branching, try-catch blocks, null checks) or overgeneralized based on method length, missing the semantic gap between GUI event handling and file I/O.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB correctly labels them as non-clones because they have entirely different functionality and structure.
- 行为差异: A handles GUI events and preferences; B copies a file.；A is an event-driven method; B is a main method.；A uses Swing components and preference storage; B uses I/O streams.；A has complex conditional logic; B has simple sequential flow.
- 修正建议: Improve handling of long-range semantics；Incorporate data flow analysis to distinguish I/O vs GUI；Use AST-based structural matching to detect different control flow patterns；Increase weight on method signatures and external dependencies

### case_id=4087 FN partial_functionality

- 方法: `fileDownload` vs `readReferenceText`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a file from a URL and saves it to a local file
- B 摘要: Reads a text resource from a URL and returns its content as a string
- 静态失败原因: Static BERT models rely heavily on token overlap and surface-level features. Here, token Jaccard is low (0.15), method names differ ('fileDownload' vs 'readReferenceText'), and return types are different, leading the model to predict non-clone despite similar structure.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels as clone when two functions share a core algorithmic pattern, even if input/output differ. Both functions involve downloading/reading from a URL using a similar sequence of Java I/O classes, which qualifies as a Type-3 clone.
- 共享行为: Open a URL and create an input stream；Wrap input stream with InputStreamReader and BufferedReader；Read data in a loop until end of stream；Handle IO exceptions
- 行为差异: Function A writes bytes to a file; Function B concatenates lines into a StringBuffer；Function A does not return a value; Function B returns the accumulated string；Function A reads byte-by-byte; Function B reads line-by-line；Exception handling: A catches general Exception; B catches specific IO exceptions and throws custom exception
- 修正建议: Incorporate data flow and control flow abstractions to recognize shared stream-reading patterns；Use graph-based representations that capture I/O operations and exception handling structure；Enhance training with more examples of functions that share algorithmic steps but differ in final output；Consider structural similarity over token overlap

### case_id=4088 FN partial_functionality

- 方法: `getFile` vs `copyFileTo`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies its soap:address endpoint, and saves to temp directory.
- B 摘要: Copies a file from source path to destination path using byte buffer.
- 静态失败原因: Static BERT/GraphCodeBERT likely relied on token overlap (12%) and API-level differences (URL, XML parsing vs plain file copy) to predict non-clone. It failed to recognize the abstract file-copying pattern due to a lack of high-level intent analysis and data flow understanding.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled this as a clone under a broad Type-4 or partial functionality interpretation, considering both functions as file copying operations despite different sources (URL vs file) and additional processing (XML modification). The annotation guidelines sometimes accept such high-level functional similarity.
- 共享行为: Both perform file I/O operations to transfer data from an input source to a file output；Both use FileInputStream/FileOutputStream；Both handle IOException
- 行为差异: Function A downloads from a network URL, Function B reads from a local file；Function A modifies XML content (changing endpoint), Function B does not modify content；Function A uses NIO channels for transfer, Function B uses a byte buffer；Function A handles multiple exception types (MalformedURLException, ParserConfigurationException, SAXException), Function B only handles FileNotFoundException and IOException
- 修正建议: Enhance models with program summarization to capture intent；Incorporate control and data flow graphs to abstract away syntactic differences；Use contrastive learning on pairs with low lexical but high semantic similarity

### case_id=4089 FP boilerplate_overlap

- 方法: `doGet` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: A servlet doGet method that reads a file from disk and writes it to the HTTP response.
- B 摘要: An actionPerformed method that handles various GUI commands (e.g., setting executable paths) and updates application preferences.
- 静态失败原因: A static model may have been misled by common API usage (File, InputStream, null checks) and similar structural patterns (if-return, try-catch?), or by embedding-based similarity capturing general 'event handler with file I/O' without deeper understanding.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clone because the functions have completely different semantics (HTTP file serving vs. GUI event handling) and only share trivial boilerplate patterns like null checks and I/O operations.
- 共享行为: Both override a Listener method (doGet/actionPerformed) with a condition check and early return.；Both perform file-related I/O operations (reading a file vs. opening a file chooser).
- 行为差异: Function A serves file content over HTTP; Function B handles UI events and updates configuration.；Function A uses servlet API; Function B uses Swing and custom controller classes.；Function B has multiple branches for different commands; Function A is linear.；Function B involves heavy user interaction (dialog boxes) while Function A is automatic.
- 修正建议: Incorporate structural information like method signature and class context.；Use control-flow and data-flow analysis to distinguish different behavioral patterns.；Train on larger datasets with emphasis on semantic differences despite lexical overlap.

### case_id=4090 FP partial_functionality

- 方法: `innerProcess` vs `perform`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Processes a CrawlURI by checking HTTP transaction, content type, size, then computing SHA1 digest on content optionally stripped by regex.
- B 摘要: Handles a Struts action by processing form data, session beans, roles, then sending XML to a URL and parsing the classification result.
- 静态失败原因: Static BERT/GraphCodeBERT likely over-relied on common Java constructs (try-catch, logging, getAttribute calls) and the presence of HTTP-related terms, ignoring the fundamentally different purposes and data flows.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB label 0 indicates non-clone, which aligns with the clear semantic and domain differences despite some superficial structural similarities.
- 共享行为: Both functions involve reading input data and performing some processing.；Both use try-catch blocks for error handling.；Both interact with external resources (HTTP recorder, URL connection).
- 行为差异: Function A is specific to web crawling and content digest computation; Function B is a Struts action for concept classification.；Function A operates on CrawlURI objects; Function B operates on HttpServletRequest/Response and session beans.；Function A computes a SHA1 digest and updates the crawl data; Function B builds XML, sends it via HTTP POST, and parses the result.；Function A uses regex stripping; Function B uses form parameters and role processing.
- 修正建议: Incorporate data flow and control flow features to distinguish different business logic.；Use fine-grained API call sequences and domain-specific context (e.g., crawl vs. Struts action) to reduce false positives.；Increase training data diversity to include more negative examples with similar boilerplate but different semantics.

### case_id=4091 FN partial_functionality

- 方法: `getHTML` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches HTML from a URL using HttpURLConnection with specified encoding, builds a string, optionally writes to file, and returns the string.
- B 摘要: Fetches HTML from a hardcoded URL using URL.openStream() and prints each line to standard output.
- 静态失败原因: Low token Jaccard (0.19) and different API calls (HttpURLConnection vs URL.openStream) cause static models to miss functional similarity; they rely on lexical overlap and miss the shared semantic intent.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels pairs as clones if they share the same core algorithm (read URL lines) even if output and API details differ, treating them as Type-3/Type-4 clones.
- 共享行为: Both connect to a URL and read HTML content line by line.；Both handle IOException (one throws, one catches).；Both use BufferedReader to read lines.
- 行为差异: A uses HttpURLConnection with custom User-Agent and explicit connect/disconnect; B uses simpler URL.openStream().；A returns the HTML as a string; B prints lines to stdout with no return.；A optionally writes the content to a file; B does not write to file.；A specifies encoding; B uses default encoding.
- 修正建议: Incorporate task-level semantics (e.g., 'read web content') through dataflow or program graphs.；Use models that abstract over API choices and focus on input-output behavior.；Train with pairs that have low lexical overlap but high functional similarity.

### case_id=4092 FP boilerplate_overlap

- 方法: `importSequences` vs `getNetworkServersIPs`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads sequences from a URL using ImportHelper and stores names and sequences.
- B 摘要: Parses network server IPs from a URL by looking for "!SERVERS" marker and extracting IP after colon.
- 静态失败原因: Static model may have been misled by superficial similarities: both use URL, InputStreamReader, try-catch with same exception types, and tokenize/parse input. The model likely focused on these common API patterns and overlooked the entirely different purpose and output.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels non-clones when semantic purpose differs significantly even if some structural patterns overlap. These functions have distinct business logic (sequence import vs server IP extraction) so BCB would label not clone.
- 共享行为: Both open a URL and read input stream；Both parse lines/tokens from input；Both handle MalformedURLException and IOException
- 行为差异: Function A reads FASTA-like sequences, Function B reads server IP configuration；Function A uses ImportHelper wrapper, Function B uses BufferedReader directly；Function A populates member fields, Function B returns a Vector<String>；Function A uses a combo box index to select URL, Function B takes URL as parameter
- 修正建议: Incorporate method signature and return type into representation；Add dataflow analysis to capture variable usage differences；Consider call-graph context or class-level information to distinguish unrelated helpers

### case_id=4093 FN partial_functionality

- 方法: `fileDownload` vs `readIntoList`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a file from a given URL and saves it to a specified directory as 'download.pdf'.
- B 摘要: Reads HTML-like content from a URL and populates a map of menu items with action commands.
- 静态失败原因: Static methods like BERT or GraphCodeBERT may have failed because they rely on token-level or syntactic features, and while there is some overlap (e.g., 'BufferedReader', 'URL', 'catch'), the overall semantics differ significantly. The model might have missed the functional similarity due to low token Jaccard (0.238) and focus on different APIs (FileOutputStream vs JMenuItem).
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider these as clones due to shared code structure (BufferedReader, URL, exception handling) and possibly because both involve reading from a URL, fitting a broad Type-3 or Type-4 pattern.
- 共享行为: Both read from a URL using BufferedReader and InputStreamReader.；Both handle exceptions (though differently).；Both use URL connection (openStream/openConnection).
- 行为差异: Output: writes to a file vs populates a map.；Reading granularity: character-by-character vs line-by-line.；Processing: writes raw bytes vs parses HTML tags and creates UI components.；Error handling: logger vs printStackTrace.
- 修正建议: Incorporate more global semantic awareness, e.g., using dataflow analysis or abstract syntax trees to capture real I/O behavior.；Consider broader clone definitions if the goal is to catch functional snippets.；Use models that can handle long-range dependencies and different levels of abstraction.

### case_id=4094 FN benchmark_preference_bias

- 方法: `copyResource` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.95`
- 推荐路线: `preference_memory_with_manual_audit`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Copies a resource (URL or file) to a destination file using byte-by-byte streaming.
- B 摘要: Copies a file to another file using FileChannel transfer.
- 静态失败原因: Static BERT models rely on token overlap and surface-level similarity, which is low here (Jaccard=0.17). They fail to capture the shared functional semantics due to different APIs (InputStream vs FileChannel) and code structure, and are not trained to recognize high-level similarity across different I/O patterns.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB often labels pairs as clones when they perform the same high-level function (file copying) despite different implementations, considering them Type-3 or Type-4 clones.
- 共享行为: Both copy data from a source to a destination file；Both open input and output streams/channels；Both close the streams/channels after copying
- 行为差异: Source type: URL or file path (a) vs File object (b)；Copy method: byte-by-byte read/write (a) vs channel transfer (b)；Exception handling: generic Exception (a) vs IOExcepiton (b)；Method signature: non-static with no parameters (a) vs static with two File parameters (b)
- 修正建议: Train models on functional similarity tasks, e.g., by using code summaries or dataflow graphs；Incorporate structural information like control flow and data dependencies；Augment training data with more varied implementations of the same functionality

### case_id=4095 FN benchmark_preference_bias

- 方法: `setup` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Extracts native library files from a JAR and adds them to the library path.
- B 摘要: Launches a NexOpen project by processing pom.xml files and setting Hibernate dialect properties.
- 静态失败原因: The static model correctly detected low semantic similarity and token overlap, but BCB's annotation was inconsistent with strict semantics, leading to a false negative from the model's perspective.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB likely labeled this as a clone due to a broad interpretation of 'initialization' tasks, possibly overlooking domain-specific differences, or it's a labeling error.
- 共享行为: Both involve reading files and processing resources.
- 行为差异: Different goals: native library extraction vs. project launch configuration.；Different file types: JAR native entries vs. Maven pom.xml and resource files.；Different API usage: ZipInputStream vs. ContentHandlerTemplate and IFile.；One is standalone, the other is Eclipse RCP launch delegate.
- 修正建议: Re-evaluate BCB annotation for consistency with functional equivalence.；Use domain-specific clone detection or stricter semantic criteria.

### case_id=4096 FP boilerplate_overlap

- 方法: `setBundleInfoName` vs `sendPost`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a URL to parse key-value pairs and update a list of BundleInfo objects.
- B 摘要: Sends an HTTP POST request with a parameter string and returns the response body.
- 静态失败原因: Static BERT models rely heavily on token-level overlap. Both functions share common I/O idioms (URL, BufferedReader, exception handling) causing high lexical similarity, while neglecting the divergent data flows and method semantics.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB prioritizes functional meaning over syntactic boilerplate. These functions serve entirely different purposes (one is a configuration updater, the other is an HTTP client), so they are correctly labeled as non-clones.
- 共享行为: Both create a URL object from a string.；Both open a connection and read input line by line using BufferedReader.；Both handle IOExceptions with error output.
- 行为差异: A performs a GET-like read-only operation; B writes to an output stream (HTTP POST).；A parses lines with '=' and updates list entries; B concatenates all response lines into a string.；A returns a boolean; B returns a string.；A takes a List parameter; B takes a param string and sends it.
- 修正建议: Incorporate data-flow analysis to distinguish write operations (output streams) from read-only accesses.；Use graph-based representations (e.g., AST with data-dependency edges) to capture structural differences.；Augment training data with more negative pairs that share I/O boilerplate but differ in core logic.

### case_id=4097 FN lexical_or_api_overlap

- 方法: `readData` vs `invoke`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Initializes multiple sets and maps by parsing comma-separated strings and reading from a file to populate data structures for Tibetan transliteration.
- B 摘要: Invokes a remote service via HTTP POST, sends JSON arguments, reads response, and deserializes it back to the expected return type with retry on timeout.
- 静态失败原因: Very low token Jaccard similarity (0.1006) and domain-specific vocabulary (Tibetan vs HTTP) lead to dissimilar embeddings, causing the detector to miss the (likely erroneous) clone label.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may have considered these clones due to a broad interpretation of 'data processing' or 'input-output' functions, but the functional domains are completely different.
- 共享行为: Both use try-catch for exception handling；Both read input and process it (tokens vs HTTP response)；Both perform string manipulations and build collections
- 行为差异: Function A reads and tokenizes local strings and file data; Function B performs HTTP networking and JSON serialization/deserialization；Function A populates multiple sets and maps; Function B handles retries and URL discovery；Function A is static and has no parameters; Function B is an instance method with invocation and retry count
- 修正建议: Use semantic role labeling or API usage patterns to distinguish between data processing and networking tasks；Incorporate control-flow and data-flow analysis to identify deeper functional similarities

### case_id=4098 FP lexical_or_api_overlap

- 方法: `callService` vs `checkForUpgrade`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches content from a constructed URL and stores it in an answer string, handling MalformedURLException and IOException.
- B 摘要: Checks for software upgrades by querying a remote server with client information, processing the XML-like response, updating a database table, and toggling UI components based on the availability of updates.
- 静态失败原因: Static BERT methods like GraphCodeBERT might rely too much on surface-level token overlap (e.g., URL, BufferedReader) and not enough on global semantics and control flow. The model may have been misled by the presence of URL.openStream and BufferedReader pattern, ignoring the vastly different overall logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels non-clones when functions have different overall purposes, even if they share some low-level patterns. Here, the shared pattern (URL reading) is a common library usage, not indicative of semantic similarity.
- 共享行为: Both open a URL connection and read response line by line using BufferedReader.
- 行为差异: Function a only fetches content and stores it; function b performs database operations, UI manipulation, and complex response parsing.；Function a has minimal error handling; function b has multiple conditional branches and status checks.；Function a is private and void; function b is public static void and throws Exception.；Function a is much shorter; function b is long and complex.
- 修正建议: Incorporate richer structural representations, e.g., control flow graphs or data flow analysis to capture the purpose beyond API sequences.；Use models that can handle long-range dependencies to differentiate small common subroutines from main logic.；Add training data with examples of API-sharing non-clones.

### case_id=4099 FN partial_functionality

- 方法: `fileDownload` vs `runScript`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads file from URL to local file system.
- B 摘要: Fetches script content from URL and returns as string.
- 静态失败原因: Static BERT/GraphCodeBERT likely focused on method names and overall structural differences (file I/O vs string building), and low token overlap led to misclassification.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB considers them clones because both read data from a URL via byte-by-byte streaming, which is the core behavior, and differences in output destination or error handling are typical for Type-4 clones.
- 共享行为: Both read from a URL using InputStream；Both read bytes one by one until -1；Both use try-catch for exception handling
- 行为差异: A writes to a file, B returns a string；A uses BufferedReader/OutputStreamWriter, B uses BufferedInputStream；A logs errors, B returns error string；A is void, B returns String
- 修正建议: Incorporate structural clone detection that captures similar loop patterns；Use dataflow analysis to recognize I/O streams；Train on more examples with diverse method names but similar core logic

### case_id=4100 FN partial_functionality

- 方法: `onlyFileCopy` vs `getFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a local file using FileChannel.transferTo.
- B 摘要: Downloads a WSDL file from a URL, modifies XML, and saves to a local file using FileChannel.transferFrom.
- 静态失败原因: Low token overlap (0.136) and different method structure caused the model to miss the shared FileChannel pattern; static models often struggle with long-range semantic dependencies and partial functionality matching.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considered both as file copy operations using FileChannel, focusing on the core I/O pattern rather than the overall function, which is common in Type-4 clone annotation.
- 共享行为: Both use Java NIO FileChannel for file I/O；Both handle IOException and close channels in finally
- 行为差异: Source and destination: local file to local file (a) vs URL to local file (b)；Additional XML processing and file management in (b)；Return type: void (a) vs String (b)；Error handling: only IOException (a) vs multiple exceptions (b)
- 修正建议: Incorporate dataflow analysis to identify I/O channel usage patterns；Use token-level alignment focusing on method calls like FileChannel operations；Train on examples with partial functionality clones from BCB

### case_id=4101 FP partial_functionality

- 方法: `testCopy_readerToOutputStream_Encoding` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Unit test that copies data from a reader to an output stream using UTF-16 encoding and verifies content equality.
- B 摘要: Handles action events in a GUI, setting various preferences like file paths for external tools, image scaling, date format, and look and feel.
- 静态失败原因: Static BERT models may have been misled by superficial similarities like both using I/O streams or file operations, but failed to capture the different semantic contexts and lack of shared logic.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB labeling as non-clone (0) because the functions have completely different purposes and no shared functionality, even at a partial or broad level.
- 共享行为: Both are Java methods.
- 行为差异: A is a unit test with fixed input/output streams; B is an event handler with complex GUI interactions.；A performs a single copy operation; B handles multiple commands with conditional logic.；A uses IOUtils.copy; B uses JFileChooser and preference storage.
- 修正建议: Improve training data with negative examples of methods with low Jaccard similarity but different semantics.；Incorporate control flow and data dependency analysis to distinguish test methods from event handlers.

### case_id=4102 FP lexical_or_api_overlap

- 方法: `sendPost` vs `callApiPost`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.85`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Sends HTTP POST with a string parameter and returns the response body as a string; displays error message on failure.
- B 摘要: Sends HTTP POST with a map of parameters, configurable timeouts and headers, checks response status, and returns an InputStream (potentially GZIP-wrapped); throws custom exception on failure.
- 静态失败原因: Static BERT models may over-rely on local lexical and API token overlap (e.g., 'HttpURLConnection', 'setDoOutput', 'getOutputStream') and the general pattern of opening a connection and writing data, while missing the functional differences in return type, error handling, and additional configuration. The model may also have been biased by the common 'send POST' intent.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically annotates as non-clone when functions have different interfaces and levels of abstraction, despite sharing core API calls. The additional complexity and different error handling in B likely push this toward a Type-4 (functionally similar but not equivalent), but BCB tends to require more structural and behavioral similarity for a clone label. Given the low token overlap and clear differences, BCB annotators likely considered these non-clones.
- 共享行为: Both perform HTTP POST requests；Both open an HttpURLConnection；Both set DoOutput to true；Both write parameters to the output stream
- 行为差异: Return type: function A returns String, function B returns InputStream；Error handling: A catches Exception and shows message, B throws custom exception；Configuration: B sets timeouts, custom headers, expected status code, while A does not；Parameter input: A takes a raw String, B takes a Map processed via getParametersString
- 修正建议: Incorporate structural information about control flow and data dependencies to capture differences in error handling paths and return types.；Use contrastive training with hard negatives that share API calls but differ in behavior and signature.；Enhance representation with type information (e.g., return type, parameter types) to distinguish similar-looking functions.

### case_id=4103 FN partial_functionality

- 方法: `addIDs` vs `readVersion`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Retrieves metabolite information from a remote web service by constructing a URL with a query name, parsing the HTML response, and populating a PeakListRow object with various IDs and molecular weight.
- B 摘要: Reads a version file from the classpath and extracts version, revision, and compile date from its contents.
- 静态失败原因: Static BERT/GraphCodeBERT likely focused on token overlap and syntax, which is low (Jaccard 0.173), and missed the abstract I/O and data-extraction pattern shared by both functions.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label as clone because both functions follow a common pattern of connecting to a URL, reading lines, and extracting information to populate data structures, which is typical of Type-3/Type-4 clones despite differences in specific parsing logic.
- 共享行为: Both use BufferedReader to read from an input stream (URL.openStream())；Both parse lines using readLine()；Both handle IOException；Both set values to some object (row or member variables)
- 行为差异: Different input sources: remote URL vs local classpath resource；Different parsing logic: HTML pattern matching vs simple key-value splitting；A returns an integer score; B is void；A sets many fields on a row; B sets only three member variables
- 修正建议: Enhance model to capture abstract data-flow patterns like 'read from URL, parse lines, extract values'；Incorporate structural or control-flow similarity measures beyond token overlap；Use graph-based representations to highlight common I/O and parsing structures

### case_id=4104 FP lexical_or_api_overlap

- 方法: `readTwitterFead` vs `init`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a Twitter feed from a fixed URL using HTTP client and returns the response as a string.
- B 摘要: Initializes a servlet by loading controller classes from a registry file using class loader.
- 静态失败原因: Static BERT overemphasized lexical and structural similarities like BufferedReader, try-catch, and while loop, ignoring differences in domain-specific APIs (HttpClient vs ClassLoader).
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB often labels non-clone when functions perform different tasks despite sharing common I/O patterns and exception handling, as the core functionality differs.
- 共享行为: Both use BufferedReader to read lines from a stream；Both catch IOException and print stack trace
- 行为差异: A performs HTTP GET request; B reads local resources via class loader；A builds a JSON string; B loads and registers classes；A has fixed URL; B iterates over multiple URLs from classpath
- 修正建议: Use dataflow analysis to differentiate between HTTP reading and class loading；Incorporate task-specific information (e.g., method names, Imports) to reduce false positives

### case_id=4105 FN benchmark_preference_bias

- 方法: `decodeFileToFile` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Decode a base64-encoded input file and write the decoded bytes to an output file.
- B 摘要: Launch a NexOpen project configuration by checking project structures, processing Maven pom files, handling Hibernate dialect setups, and setting persistent properties.
- 静态失败原因: The static model correctly predicted non-clone (0) with low token Jaccard; the BCB label appears incorrect, so the model did not fail but the dataset annotation is likely wrong.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: The BCB label (1) may be a dataset error; these functions share only trivial boilerplate patterns (try-finally, stream usage) which might have been overcounted as Type-3/4 clones in the original annotation process, but they are functionally unrelated.
- 共享行为: Both use Java I/O streams (InputStream, OutputStream) for reading/writing data.；Both contain try-finally blocks to close resources.
- 行为差异: Function A performs Base64 decoding; Function B does not involve Base64.；Function A is a simple file copy with decoding; Function B is a complex Eclipse plugin launch routine with XML processing, property handling, and project modifications.；Function A returns a boolean indicating success; Function B returns void and may throw CoreException.；Function B uses multiple dependency objects (ILaunchConfiguration, IProgressMonitor, etc.) and interacts with Eclipse workspace, whereas A is a static utility method.
- 修正建议: Verify and correct the BCB label for this pair; it is likely a false positive clone annotation.；If dataset correction is not possible, consider filtering out pairs with very low token overlap and no clear functional similarity.

### case_id=4106 FN partial_functionality

- 方法: `decodeFileToFile` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Decodes a Base64-encoded input file and writes the decoded bytes to an output file, returning success status.
- B 摘要: Downloads a KMZ file from a URL, extracts its ZIP entries, and writes each entry to a file.
- 静态失败原因: Low token overlap (0.226) and different method names, APIs (Base64 vs ZipInputStream), and control flow structures (try-catch-finally vs throws) make it difficult for a static model relying on surface-level similarity to recognize the high-level I/O pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as variants of 'file copying with transformation' using standard Java I/O patterns, thus a Type-4 clone.
- 共享行为: Both read from an input source (file or URL) using streams；Both write byte data to output files using buffered streams；Both use a loop to read chunks of bytes and write them to the output
- 行为差异: A decodes Base64, B decompresses ZIP entries；A reads from a local file, B reads from a URL；A returns a boolean, B has void return and throws exceptions；A handles exceptions locally, B declares exceptions
- 修正建议: Enhance models to extract abstract data-flow and control-flow patterns beyond lexical tokens；Incorporate code summarization or docstring matching to capture functional intent；Use graph-based representations that highlight I/O operations and transformations

### case_id=4107 FP boilerplate_overlap

- 方法: `getLinksFromURLFast` vs `doVersionCheck`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Extracts hyperlinks and anchor texts from a web page via regex and returns them as vectors.
- B 摘要: Checks for a new software version by reading a version file from a URL and comparing build numbers.
- 静态失败原因: Static BERT models may rely on surface-level lexical overlap (e.g., URL, BufferedReader, readLine) and common structural patterns (try-catch around I/O), missing deeper semantic differences in data processing logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels as non-clone because the overall functionality is entirely different (link extraction vs. version checking) despite similar URL I/O boilerplate.
- 共享行为: Both open a URL connection and read line-by-line using BufferedReader and InputStreamReader.
- 行为差异: Function A extracts hyperlinks using regex; Function B parses version/build lines by prefix.；Function A returns extracted data; Function B shows UI messages about version status.；Function A throws Exception; Function B catches IOException and shows error dialog.
- 修正建议: Incorporate data flow analysis to distinguish how read data is processed.；Use program slicing to focus on output and side effects.；Train on more diverse downstream tasks to reduce bias toward API-heavy code.

### case_id=4108 FP boilerplate_overlap

- 方法: `main` vs `copyFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Main method that generates adapter classes from a Prolog file, involving parsing, class loading, and writing a JAR.
- B 摘要: Utility method that copies a file using FileChannel with transferFrom.
- 静态失败原因: The model may have overemphasized superficial similarities like both methods using File, IOException, and try-catch blocks, while ignoring the vastly different control flow and data dependencies. The low token Jaccard suggests the prediction is an anomaly, possibly due to noise in the static embedding matching.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled as non-clone because the two functions have completely different purposes and significantly different behavior; they share only trivial common patterns.
- 共享行为: Both are static methods；Both involve file I/O operations；Both use try-catch or try-finally for resource handling
- 行为差异: Function A performs complex code generation and class loading; B is a simple file copy.；Function A writes a JAR file; B copies any file.；Function A handles multiple files and uses many libraries; B uses only standard NIO channels.；Function A has conditional logic for debug mode; B has none.
- 修正建议: Improve training data to include more diverse negative examples.；Use models that capture long-range dataflow and control dependencies.；Apply more aggressive filtering of boilerplate code features.

### case_id=4109 FP boilerplate_overlap

- 方法: `readIntoList` vs `loadURL`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads HTML content from a URL to create and populate a map of JMenuItem objects with action listeners.
- B 摘要: Downloads content from a URL (with optional authentication) to a temporary file while displaying download progress.
- 静态失败原因: The static model overemphasized the syntactic and structural boilerplate of reading lines from a URL, ignoring the divergent high-level goals and data manipulations.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels non-clone because the functions produce completely different outputs (menu items vs. file download) and serve distinct purposes despite sharing low-level I/O patterns.
- 共享行为: Both open a URL and read lines using BufferedReader；Both use a while loop to read until null
- 行为差异: A parses HTML tags to extract command names and creates JMenuItem objects; B writes raw lines to a file.；A adds action listeners to menu items; B handles authentication and displays file size progress.；A populates a map; B creates a temporary file and does not return a collection.
- 修正建议: Incorporate dataflow analysis to distinguish different output types；Use models that capture overall function purpose, not just token sequences；Train on negative examples with similar I/O but different semantics

### case_id=4110 FN partial_functionality

- 方法: `copyResource` vs `compressWithZip`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.5`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a single resource (from URL or file) to a destination file using byte-by-byte streaming.
- B 摘要: Compresses a list of files into a ZIP archive by reading file data in chunks and writing to ZIP entries.
- 静态失败原因: Static BERT models rely on token-level similarity and structural features; low token Jaccard and different method names caused low similarity scores, and the model failed to capture the high-level I/O pattern as equivalent due to differences in API usage.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this as a clone due to similarity in I/O loop structure (read-write pattern) despite different specific functionalities, considering both as 'copying' data from source to destination.
- 共享行为: Both read data from input sources and write to output streams using byte-level I/O loops.
- 行为差异: A copies raw data; B compresses multiple files into a ZIP format.；A handles single file; B handles multiple files.；A reads one byte at a time; B reads in chunks.；A writes to a plain file; B writes to a zip output stream with entry management.
- 修正建议: Use data-flow analysis to identify I/O patterns.；Augment with semantics from method names or documentation.；Use contrastive learning to capture broader semantic similarity beyond exact token matches.

### case_id=4111 FP boilerplate_overlap

- 方法: `getLinksFromURLFast` vs `readZoneIDs`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Extracts hyperlinks and anchor texts from an HTML page retrieved from a URL.
- B 摘要: Reads zone IDs (integers) from a resource file and returns them as a set.
- 静态失败原因: The static model may have overfitted to the common I/O pattern (open stream, read lines, collect) and missed the distinct operations (regex vs parseInt) and output types.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels non-clone because the functionality is different (web link extraction vs zone ID reading) despite both involving I/O and parsing.
- 共享行为: Both read from an input source (URL or resource)；Both read lines in a loop；Both collect parsed data into a collection
- 行为差异: A uses regex to extract hyperlinks; B parses integers；A returns two Vectors; B returns a HashSet；A has multiple regex operations; B uses Integer.parseInt
- 修正建议: Improve model to distinguish data flow and output types；Use method name and return type as discriminative features；Incorporate token-level differences in library calls and expressions

### case_id=4112 FN benchmark_preference_bias

- 方法: `unzip` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Unzips a ZIP file, extracting its entries to a directory.
- B 摘要: Launches a NexOpen project by configuring Maven POM files and triggering an install action.
- 静态失败原因: The static model correctly identified the functions as non-clones due to low token overlap (Jaccard 0.063) and distinct API usage (ZipEntry vs. IProject). It failed to conform to the erroneous BCB label, which is actually correct from a semantic standpoint.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB likely labeled this as a clone due to a broad interpretation of file processing (both use streams and write to files), possibly considering them as Type-4 (semantic) clones. However, their actual functionalities are entirely different, so this labeling is likely an error.
- 共享行为: Both involve file I/O operations with streams.
- 行为差异: Method A extracts a compressed archive; Method B sets up project environment and runs Maven tasks.；Method A is a utility function; Method B is a launch delegate for Eclipse plugins.；Method A has no dependencies on Eclipse or build tools; Method B heavily relies on Eclipse workspace and project structure.
- 修正建议: The static model does not need fixing; the BCB label appears to be a false positive. If aiming to match BCB annotations, one could incorporate broader structural similarity heuristics, but that would reduce precision.

### case_id=4113 FP partial_functionality

- 方法: `getRequestContent` vs `doVersionCheck`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Opens a URL, reads the first line, and returns it as a string.
- B 摘要: Opens a version check URL, reads lines to find version and build, and updates the UI if a new version is available.
- 静态失败原因: Static BERT/GraphCodeBERT may have overemphasized the shared API usage (URL, BufferedReader) and overlooked the divergent control flow, output, and error handling, leading to a false positive.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely labels this as non-clone because the two methods have distinct high-level purposes: one fetches raw content, the other performs a version check with UI updates. Despite shared low-level I/O patterns, the functionality differs significantly, aligning with BCB's tendency to require functional similarity.
- 共享行为: Both create a URL object and open a connection or stream.；Both use BufferedReader to read lines from the input stream.；Both close the reader after reading.
- 行为差异: A returns the first line; B reads multiple lines searching for specific prefixes.；A does not handle exceptions; B catches IOException and shows error dialog.；A returns a String; B returns void and interacts with UI (showWaitCursor, messages).；A does not compare versions or update UI.
- 修正建议: Incorporate dataflow analysis to track how read data is used.；Distinguish between methods that return data vs. those that perform side effects (UI).；Consider method signatures and exception handling as discriminative features.

### case_id=4114 FN partial_functionality

- 方法: `readData` vs `handledRun`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Parses multiple comma-separated static strings into HashSets and a HashMap for Tibetan transliteration data.
- B 摘要: Downloads an XML file from a URL, checks version, updates a local file, and reloads game database.
- 静态失败原因: Low token similarity (0.083) and different API usage (StringTokenizer vs URL/IO) caused focus on surface differences; long code length obscured high-level common purpose of data ingestion.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as 'data initialization routines' that read and parse structured data (CSV-like vs XML) and store into data structures, despite different sources and detail logic.
- 共享行为: Both iterate over data tokens and store results into collections or files
- 行为差异: A reads from internal strings; B reads from external URL；A populates many small sets; B updates a single file and loads a database；A has complex switch-case parsing; B has simple header parsing
- 修正建议: Train model to recognize broader data-flow patterns beyond token overlap；Use structural matching that treats I/O operations as similar；Incorporate detection of initialization/configuration routines

### case_id=4115 FP long_range_semantics

- 方法: `save` vs `readData`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `static_summary_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Saves multiple files to a directory, adding package declaration.
- B 摘要: Parses multiple comma-separated string token lists into hash sets for character classification.
- 静态失败原因: The static model may have been confused by the truncated nature of code_b and the presence of some common Java constructs (like StringTokenizer loops) but the overall semantics are unrelated.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB prefers non-clone because the functions have completely different purpose and logic; no shared functionality.
- 行为差异: Function A writes file contents to disk; Function B parses string tokens into sets.；Function A deals with file I/O and directory creation; Function B deals with data initialization from configuration strings.；Function A has a loop over files; Function B has many repeat tokenization loops.
- 修正建议: Improve model's ability to distinguish between different high-level tasks like file saving vs data parsing.；Provide better negative sampling with more diverse non-clone pairs.

### case_id=4116 FN benchmark_preference_bias

- 方法: `gzip` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.2`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: A utility method that GZIP-compresses a file from a fixed directory.
- B 摘要: A method to generate HTML pages for editing from XML configuration by reading and transforming various files.
- 静态失败原因: Static BERT likely failed because it relied on lexical overlap and structural patterns, and the low token Jaccard indicated no significant similarity; it did not capture any high-level behavioral abstraction that BCB might have used.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have considered them clones based on very broad similarity in file I/O operations, perhaps treating both as 'file transformation' tasks, but this is an extremely weak match even for Type-4.
- 共享行为: Both use FileInputStream to read file data；Both write output to a file (GZIPOutputStream or FileWriter)
- 行为差异: Different overall purpose (compression vs. site generation)；Different output formats (binary GZIP vs. HTML text)；Different complexity and parameter count；Different error handling and exception declarations
- 修正建议: Implement more detailed semantic analysis that captures control flow and data flow beyond lexical tokens；Fine-tune on more consistent clone annotations to reduce noise；Use a larger context window to compare entire method bodies

### case_id=4117 FP boilerplate_overlap

- 方法: `retrieveQ` vs `getFrameworkFactory`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads the content of a URL as a string, printing the HTTP response message to error stream.
- B 摘要: Loads an OSGi FrameworkFactory by reading a service file from classpath and instantiating the specified class via reflection.
- 静态失败原因: The model likely over-relied on lexical and structural overlaps (URL, BufferedReader, readLine, exception handling) and failed to capture the divergent high-level goals. The I/O pattern is a common idiom that misleads models into false positives.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB considers these non-clones because they have entirely different purposes (retrieving web content vs. loading an OSGi service) and only share common I/O boilerplate, which does not imply functional similarity.
- 共享行为: Both use URL to access a resource.；Both use BufferedReader to read text line by line.；Both handle exceptions.
- 行为差异: A reads from an arbitrary URL passed as parameter; B reads from a fixed classpath resource.；A concatenates all lines into a single string; B processes lines to find a class name and instantiate an object.；A prints an HTTP response message; B throws an exception if no factory is found.；B has logic to skip comment lines and trim whitespace; A does not.
- 修正建议: Incorporate method-level semantics (e.g., method name embeddings or documentation).；Add dataflow analysis to distinguish what happens after reading.；Use a more fine-grained type system for API calls (e.g., distinguish URL.openConnection from ClassLoader.getResource).；Train with contrastive examples that have similar boilerplate but different intents.

### case_id=4118 FN partial_functionality

- 方法: `getResourceAsStream` vs `readAndRewrite`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Caches a remote resource locally and returns an InputStream.
- B 摘要: Reads a DICOM file, parses it, and writes the pixel data to another file.
- 静态失败原因: Static BERT models may have focused on lexical tokens and API calls, finding high overlap in common I/O classes (InputStream, BufferedInputStream, etc.) but missed the semantic gap due to different contexts.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider them clones due to structural similarity in stream reading/writing and caching patterns, despite different application domains.
- 共享行为: Both perform file I/O operations using streams；Both use buffered streams；Both include print statements for logging
- 行为差异: Different input sources: one from URL, one from file；Different output: one returns InputStream, one writes to a file；Different data formats: general resource vs DICOM medical image
- 修正建议: Incorporate higher-level semantic understanding of the overall task；Use graph-based representations to capture data flow differences

### case_id=4119 FP boilerplate_overlap

- 方法: `googleImageSearch` vs `retrieveTemplate`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Searches Google Images, parses result to extract image URLs, and updates UI with an image.
- B 摘要: Fetches blog template from URL, caches it, and returns the string.
- 静态失败原因: The static BERT/GraphCodeBERT method likely focused on structural similarities like URL reading, while ignoring the broader semantics and side effects. It may have been fooled by the common 'read lines from URL' pattern, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled this as non-clone because the functions have very different purposes and outputs, despite sharing a common I/O pattern. The shared pattern is too generic (reading from URL) to be considered a clone; it's boilerplate code.
- 共享行为: Both open a URL, read all lines into a string, and close the reader.
- 行为差异: A parses HTML to extract image URLs; B just stores raw text.；A updates UI components; B returns the string.；A handles exceptions with dialog; B throws exception.；A uses HttpURLConnection with User-Agent; B uses url.openStream().
- 修正建议: Improve model's ability to distinguish between core functionality and boilerplate code.；Use contrastive learning with hard negatives that share boilerplate but differ in purpose.；Incorporate dataflow analysis to capture variable usage and side effects.

### case_id=4120 FP lexical_or_api_overlap

- 方法: `getUser` vs `doVersionCheck`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Loads a user by login from DAO or reads a config file to create and save the user.
- B 摘要: Checks for new version by reading a version-check URL, parsing version and build info, and displaying appropriate message.
- 静态失败原因: Over-relied on lexical and API overlap (URL, BufferedReader, try-catch) without understanding the distinct semantics and data flow, treating boilerplate I/O as indicative of clone.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labeled non-clone because the functions have completely different purposes (user authentication vs. version checking) despite similar I/O boilerplate. BCB requires functional similarity beyond superficial API usage.
- 共享行为: Open a URL and read lines via BufferedReader；Use try-catch for exception handling；Parse token-delimited lines in a while loop
- 行为差异: A returns a User object; B shows dialogs；A reads from local config file; B reads from remote URL；A parses login:password:profile; B parses .version and .build；A saves user to DAO; B compares versions and updates UI
- 修正建议: Incorporate semantic features like data flow, variable/type names, and overall method goal；Use context-aware models that capture the purpose of the function；Apply contrastive learning to distinguish similar-looking but functionally different code

### case_id=4121 FP boilerplate_overlap

- 方法: `readTwitterFead` vs `PhoneSetImpl`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads Twitter JSON feed from a URL using HttpClient and returns it as a string.
- B 摘要: Reads a phone set definition file from a URL and populates a map by parsing lines, skipping those starting with '***'.
- 静态失败原因: The model likely overemphasized lexical overlap (URL, BufferedReader, readLine) and ignored high-level semantic differences due to lack of understanding of overall task context and data flow.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels as non-clone because the functions have entirely different purposes (Twitter feed retrieval vs phone set parsing), different output types, and different control flow despite similar boilerplate I/O patterns.
- 共享行为: Both read input from a URL line by line using BufferedReader and InputStreamReader.；Both iterate over lines until null.
- 行为差异: A uses HttpClient for HTTP GET, while B uses URL.openStream() directly.；A builds and returns a single String; B parses each line and populates a HashMap.；A handles HTTP status codes and logs errors; B throws IOException and has no error handling.；A ignores no lines; B skips lines starting with '***'.
- 修正建议: Incorporate method name and class context into embeddings.；Train on more diverse examples of URL reading with different business logic.；Use data flow analysis to differentiate between building a string and populating a map.

### case_id=4122 FN benchmark_preference_bias

- 方法: `main` vs `readAndRewrite`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `preference_memory_with_manual_audit`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file via HTTP and extracts its ZIP entries to files.
- B 摘要: Reads a DICOM image file, parses metadata, reads pixel data, and writes the dataset to a new file.
- 静态失败原因: The low token Jaccard similarity (0.118) and distinct domain-specific APIs (ZipInputStream vs DcmParser) led the model to correctly identify them as semantically different, but BCB's broader clone definition includes such structurally similar I/O patterns.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB annotators may consider these clones because both follow a generic 'read-process-write' template with I/O boilerplate and status messages, which is a common pattern accepted as Type-4 (semantic similarity) in BigCloneBench.
- 共享行为: Both perform file input/output operations with streams.；Both use buffered streams for efficiency.；Both have while loops to process data chunks.；Both print progress messages to standard output.
- 行为差异: Input source: URL (HTTP) vs local file for DICOM.；File format: ZIP extraction vs DICOM medical image parsing.；Processing logic: simple extraction of entries vs complex metadata handling and pixel data manipulation.；Output: extracted files vs rewritten DICOM file.
- 修正建议: If targeting BCB-style clones, incorporate high-level structural pattern matching (e.g., 'read-write loop with progress' as a feature).；Adjust clone detection threshold to accept Type-4 clones based on I/O template similarity.；Use dataset-specific annotation guidelines to refine model training.

### case_id=4123 FN benchmark_preference_bias

- 方法: `getFile` vs `copyFiles`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.2`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, optionally modifies its endpoint, and returns the local file path.
- B 摘要: Recursively copies files or directories from a source path to a destination path.
- 静态失败原因: The static BERT model correctly identified them as non-clones due to low token overlap and different control flow, but this conflicts with the BCB label, suggesting the BCB annotation may be erroneous.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB likely labeled this as a clone based on a broad interpretation of 'file manipulation' or a mistake due to both functions using FileChannel and file operations, but the semantic difference is substantial.
- 共享行为: Both perform file I/O operations using FileChannel.
- 行为差异: Function A downloads from a network URL; Function B copies local files.；Function A modifies XML content; Function B does not.；Function A returns the file path; Function B returns void.；Function A uses logging and specific exception handling; Function B uses generic Exception.
- 修正建议: Review BCB annotation for this pair; consider removing from clone set.；Use a more robust semantic understanding that captures intent beyond surface-level API usage.

### case_id=4124 FN benchmark_preference_bias

- 方法: `addIDs` vs `loadSourceCode`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.7`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Fetches metabolite data from a URL and populates a PeakListRow with extracted IDs and molecular weight.
- B 摘要: Reads a source code file from the classpath, applies syntax highlighting, and stores the result as an HTML string.
- 静态失败原因: The model correctly predicted non-clone due to low structural and semantic overlap; the BCB label may be incorrect.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled these as clone based on broad Type-4 similarity of both involving URL reading and stream processing, but this is questionable; possibly a labeling error.
- 共享行为: Both use BufferedReader and URL to read data from a stream.
- 行为差异: Function A parses HTML to extract metabolite IDs and scores, while Function B reads source code lines and applies syntax highlighting.；Function A modifies a PeakListRow object with multiple fields; Function B builds a single HTML string.；Function A returns an int (score); Function B returns void.；Function A takes parameters (row, name); Function B uses an instance variable filename.
- 修正建议: Verify BCB labeling for this pair; consider removing or correcting the label.

### case_id=4125 FN partial_functionality

- 方法: `copyFile` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a file from source to destination using file streams and a buffer.
- B 摘要: Downloads a KMZ file from a URL and extracts its zip entries to files.
- 静态失败原因: Static BERT models rely on token similarity (Jaccard = 0.23), which is low due to different method names, structure, and APIs. They miss the shared I/O loop substructure.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may annotate this as a Type-4 clone because both functions implement a common 'stream copy' pattern, ignoring the higher-level context differences.
- 共享行为: Reads data from an InputStream and writes to an OutputStream in a loop using a buffer.
- 行为差异: A copies a single file; B downloads from URL and extracts multiple zip entries.；A uses FileInputStream/FileOutputStream; B uses ZipInputStream and BufferedOutputStream.；A does not handle zip decompression; B does not handle plain file copy.
- 修正建议: Use program analysis to extract I/O loops as features.；Incorporate dataflow or graph representations to capture buffered copy patterns.；Train on more diverse partial functionality clones.

### case_id=4126 FN partial_functionality

- 方法: `getHTML` vs `run`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.95`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches HTML from a URL using HttpURLConnection, optionally writes to a file, and returns the HTML string.
- B 摘要: Fetches HTML from a URL using HttpURLConnection with basic authentication, stores result in a field, and sets a finish flag.
- 静态失败原因: Static BERT/GraphCodeBERT models rely on token overlap and surface-level patterns. The low token Jaccard (0.268), different method names, and different overall structure (e.g., file writing, authentication) cause the model to miss the shared core logic.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels pairs as clones if they share the core functionality (fetching URL content) even with peripheral differences like authentication or file writing. The main purpose is the same.
- 共享行为: Uses HttpURLConnection to fetch content from a URL；Sets request headers (User-Agent vs Authorization)；Reads response line-by-line and appends to a buffer；Disconnects the connection in the end
- 行为差异: Function A uses BufferedReader with explicit encoding, B uses default encoding；Function A optionally writes response to a file if dirPath is non-null；Function B includes basic authentication (username/password)；Function A returns the HTML string, B stores it in a field and sets a finish flag
- 修正建议: Enhance models to capture common subgraphs (e.g., HTTP request-response pattern) using AST-based or dataflow analysis.；Use token-level alignment with abstracted identifiers and literals to reveal structural similarity.；Incorporate code summarization or functional labeling to highlight overall purpose.

### case_id=4127 FN benchmark_preference_bias

- 方法: `modifyApplicationMessage` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.2`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Modify a specific message in a localized properties file, creating the file if missing by copying from an English template.
- B 摘要: Copy all files from a source directory to a destination directory using NIO channels.
- 静态失败原因: The static BERT model correctly focused on the lack of lexical or API overlap, leading to a non-clone prediction; the BCB label itself appears to be a benchmark annotation error.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB likely mislabeled this pair as Type-4 (semantic clone) due to the generic pattern of reading and writing files, but the actual functionality and data transformations are entirely different.
- 共享行为: Both read from a source and write to a destination.；Both handle file I/O and may create files.
- 行为差异: A modifies a single properties file; B copies multiple files.；A uses character-based streams and text processing; B uses byte-based NIO channels.；A conditionally creates the file; B assumes destination directory exists.；A edits a specific line; B copies entire files without modification.
- 修正建议: Re-evaluate the BCB ground truth for this pair; consider correcting the label to non-clone.；Train models on more fine-grained functional similarity rather than broad file I/O patterns.

### case_id=4128 FP boilerplate_overlap

- 方法: `sendPost` vs `PageLoader`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Sends an HTTP POST request with parameters and returns the response body as a string.
- B 摘要: Reads the entire content from a URL and stores it in a field.
- 静态失败原因: The model was misled by the common URL opening and reading boilerplate code (e.g., URL, BufferedReader, InputStream, line reading loop), causing a false positive due to lexical overlap.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels non-clone because the functional behavior differs significantly: one sends data via POST, the other merely reads. The partial similarity in reading is outweighed by the distinct purposes.
- 共享行为: Both connect to a URL and read the response line by line into a string.
- 行为差异: Function A sends POST data, function B does not.；Function A returns the result, function B assigns to a field (side effect).；Function A handles exceptions internally, function B throws exception.；Function A sets request property and output, function B does not.
- 修正建议: Incorporate data flow analysis to distinguish between writing to output stream and only reading.；Include method signature and purpose as features.；Train on more examples where boilerplate is shared but semantics differ.

### case_id=4129 FP lexical_or_api_overlap

- 方法: `getURLContent` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches the entire content of a given URL as a string, using generic URLConnection and handling encoding.
- B 摘要: Performs a Google image search for the current artist and album, downloads the HTML, parses image URLs, and adds them to a list, with error handling.
- 静态失败原因: The model likely focused on the overlapping API usage (URL, openConnection, BufferedReader, readLine) and ignored the broader context of return type, control flow, and additional operations, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely considers these non-clones because they implement different high-level functionalities: one is a generic utility to retrieve URL content, the other is a specific method for image search that includes parsing and list population.
- 共享行为: Both open a URL connection and read the input stream line by line using BufferedReader.
- 行为差异: getURLContent returns the full content as a string, while googleImageSearch populates a list of image URLs and does not return anything.；googleImageSearch has additional logic for URL construction, condition on artist change, and parsing HTML for image links.；getURLContent uses generic URLConnection and handles encoding; googleImageSearch uses HttpURLConnection with a custom User-Agent and no encoding handling.；getURLContent throws IOException; googleImageSearch catches exceptions and shows an error dialog.
- 修正建议: Train models to consider function signature (return type, parameters) and overall data flow, not just API sequences.；Include contrastive examples where similar API usage occurs but semantics differ.；Incorporate structural analysis like control flow graphs or program dependence graphs.

### case_id=4130 FP other

- 方法: `main` vs `doPost`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: A main method that generates adapter classes from a Prolog file using various utilities.
- B 摘要: A doPost method that handles a multipart HTTP request to produce an email from an uploaded webpage.
- 静态失败原因: The model likely misclassified due to superficial similarities like the use of try-catch blocks, I/O streams, and the presence of 'page' variable, but it failed to capture the entirely different domain and logic.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB labels this as non-clone (0) because the two functions have completely different purposes, inputs, and outputs; there is no functional similarity even under broad Type-4 criteria.
- 行为差异: Different method signatures and entry points (main vs doPost)；Different inputs: command-line arguments vs HTTP request；Different outputs: writes class files and resources vs writes response output stream；Different domain: Prolog-to-Java adapter generation vs web form processing and email generation
- 修正建议: Improve training with more diverse negative examples highlighting domain-specific differences；Incorporate structural or control-flow features to differentiate task types；Add explicit handling of method signatures and API usage patterns

### case_id=4131 FN partial_functionality

- 方法: `login` vs `fileDownload`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Logs into LOLA by sending POST request with email and password, extracts session ID from response.
- B 摘要: Downloads a file from a URL and writes it to a local file.
- 静态失败原因: Static BERT/GraphCodeBERT may have focused on method names ('login' vs 'fileDownload') and low token overlap (0.21), causing it to miss the underlying structural similarity in URL connection handling.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considers them clones because both share a common pattern of opening a URL connection, reading data, and closing resources, which may be classified as a broad Type-3/4 clone based on partial functionality overlap in network I/O.
- 共享行为: Both open a URL connection；Both read data from an InputStream via BufferedReader；Both handle exceptions with try-catch
- 行为差异: Function A sends form data (POST) while B does not send data；Function A returns a session string, B writes to file and returns void；Function A specifically targets LOLA login, B downloads generic file
- 修正建议: Improve training with more diverse examples of partial functional clones；Incorporate control-flow or data-flow information to recognize similar API usage patterns

### case_id=4132 FP lexical_or_api_overlap

- 方法: `googleImageSearch` vs `loadURL`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Performs Google image search by fetching HTML and parsing image URLs into a list.
- B 摘要: Loads a URL with optional authentication, writes content to a temporary file, and updates a progress label.
- 静态失败原因: The model likely over-relied on overlapping API tokens (URL, BufferedReader, etc.) and similar control flow patterns, missing the different domain purposes and different data sinks.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled non-clone because the core functionality differs (image search vs file download) despite shared I/O boilerplate; BCB emphasizes semantic equivalence or strong similarity.
- 共享行为: Both open an HTTP connection and read lines from the input stream using BufferedReader and InputStreamReader.
- 行为差异: Function A parses HTML for image URLs, while B writes raw content to a file.；Function A uses HttpURLConnection with a User-Agent header, B uses URLConnection with optional Basic Auth.；Function A catches and shows errors, B throws IOException.；Function A updates a list, B updates a GUI label and writes to a file.
- 修正建议: Incorporate data flow analysis to track how inputs are processed and where outputs go.；Use task-aware representations that capture the overall goal.；Train on more diverse pairs with boilerplate overlap but different semantics.

### case_id=4133 FP lexical_or_api_overlap

- 方法: `getLinksFromURLFast` vs `doVersionCheck`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.98`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Extracts all hyperlinks from a given URL, converts them to absolute URLs, and returns them in a vector alongside their text.
- B 摘要: Downloads a version-check file from a configured URL, parses build version strings, and triggers a version comparison.
- 静态失败原因: Static BERT likely overemphasized the shared boilerplate I/O code (URL, BufferedReader, readLine loop) and token overlap like 'URL', 'BufferedReader', 'readLine', leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels as non-clone because these methods serve entirely different functional purposes (link extraction vs version checking) despite sharing low-level I/O patterns.
- 共享行为: Both open a URL connection and read its content line by line.；Both use BufferedReader and InputStreamReader patterns.；Both perform string matching on each line (regex vs prefix check).
- 行为差异: Function A parses HTML anchor tags to extract links; Function B parses a properties-like file for version strings.；Function A returns a vector of links and texts; Function B triggers a UI-related version check and does not return data.；Function A has extensive use of regular expressions; Function B uses simple string startsWith checks.；Function A writes debug output; Function B shows and hides a wait cursor and handles errors with GUI messages.
- 修正建议: Incorporate semantic role labeling or functional classification of method purpose.；Use graph-based code representations (e.g., AST or CFG) to capture control/data flow differences.；Apply contrastive learning that penalizes pairs with same I/O patterns but distinct functionality.；Add attention to method signatures, return types, and external API calls to disambiguate.

### case_id=4134 FN partial_functionality

- 方法: `copyResource` vs `unzip`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copy a resource (URL or file) to a destination file using byte-wise streaming.
- B 摘要: Unzip a ZIP file to a directory, handling entries and directory creation.
- 静态失败原因: Low token overlap (0.246) and different method names likely caused the model to miss the high-level functional similarity of data copying.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels Type-4 clones where both methods perform data transfer from input to output, even with different implementations and source types (URL vs ZIP).
- 共享行为: Open an input stream from a source (URL/file or ZIP file)；Read byte data from the input stream；Write byte data to an output stream (FileOutputStream)；Close input and output streams after operation
- 行为差异: copyResource handles both URL and File sources; unzip only handles ZIP files；unzip iterates over ZIP entries and handles directories and buffered output；copyResource reads byte by byte; unzip reads in buffer chunks；unzip creates subdirectories; copyResource writes to a single destination file
- 修正建议: Incorporate data flow analysis to capture common patterns like read-write loops；Use contrastive learning with hard negatives that share I/O patterns；Include method name normalization or synonym handling

### case_id=4135 FP boilerplate_overlap

- 方法: `readTwitterFead` vs `doVersionCheck`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a fixed Twitter JSON feed via HTTP and returns the raw content as a string.
- B 摘要: Checks for software version updates by reading a remote file and comparing version/build numbers, displaying UI messages.
- 静态失败原因: The model likely overemphasized the shared boilerplate pattern (BufferedReader, InputStream, line reading) and common API usage (URL, HttpClient), while ignoring the distinct processing and output behavior.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels as non-clone because the functions serve distinct purposes and have significant behavioral differences beyond the shared I/O boilerplate.
- 共享行为: Both open a remote URL and read lines using BufferedReader.；Both handle IOException by logging or showing errors.
- 行为差异: Function A uses Android HttpClient and a fixed URL; Function B uses URL.openStream and a configurable URL.；Function A returns the entire response as a string; Function B parses lines, compares versions, and triggers UI dialogs.；Function B manages cursor visibility (show/hide wait cursor), which is absent in A.；Error handling differs: A logs errors, B shows GUI errors.
- 修正建议: Use dataflow analysis to differentiate the transformation of input to output.；Increase weight on function-level semantics beyond token overlap.；Mask or discount common I/O boilerplate patterns.

### case_id=4136 FN partial_functionality

- 方法: `getJSONData` vs `readGeoParserResult`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches JSON from a given URL via HTTP GET and returns parsed JSONObject.
- B 摘要: Sends an XML request to a geoparser URL, reads XML response, extracts place names and gazetteer IDs, and returns a collection.
- 静态失败原因: Low token Jaccard (0.123) and significant lexical differences (different APIs, imports, XML vs JSON) made static BERT models miss the functional similarity; they rely on surface-level overlap.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this as a clone because both functions share a common high-level pattern of 'fetch data from a URL via HTTP, read it line by line, and parse it into a structured object', which aligns with broad Type-3/Type-4 clone definitions.
- 共享行为: Both perform HTTP GET requests to retrieve data；Both read response line by line；Both parse response into structured objects
- 行为差异: URL construction differs (simple URL vs XML-based request)；Response format differs (JSON vs XML)；Parsing logic differs；Return type differs
- 修正建议: Enhance models with control flow or data flow graphs to capture common patterns；Train on function-level semantic embeddings that capture high-level intent；Use graph-based clone detection that considers API call sequences

### case_id=4137 FN benchmark_preference_bias

- 方法: `convert` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Converts an ACRNEMA stream file to DICOM format by parsing pixel data, adding UIDs, and writing output with optional bit inflation.
- B 摘要: Builds a website for editing by transforming XML pages with XSLT, handling file I/O, and replacing placeholders in the output.
- 静态失败原因: The static model correctly predicted non-clone; the BCB label is likely a false positive. The model likely recognized the low lexical and structural overlap (token Jaccard 0.09) and different APIs, so it did not fail but correctly identified dissimilarity.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have erroneously labeled this pair as clone due to both functions involving file conversion/transformation and heavy I/O, but the specific domains and logic are entirely different.
- 共享行为: Both use file I/O streams and write output to files.；Both involve some form of data transformation.
- 行为差异: Function A converts medical image data (ACRNEMA to DICOM) while B builds HTML pages from XML.；A works with binary pixel data and DICOM tags; B works with character strings, XML, and XSLT.；A has specific medical UID generation; B has web server URL replacement.；A processes a single file; B processes multiple pages in a loop.
- 修正建议: Review BCB annotations for this pair; likely a labeling error.；Consider adding domain-specific features to distinguish medical vs web processing.

### case_id=4138 FP boilerplate_overlap

- 方法: `readZoneIDs` vs `readUNI`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads integers from a resource file into a set.
- B 摘要: Reads tab-separated descriptions from a URL, skipping the header, and adds formatted strings to a list.
- 静态失败原因: The model likely overemphasized the common boilerplate of opening a stream, reading lines, and parsing, while missing the distinct data transformation logic and output structures.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels as non-clone because the functions have different signatures, different data processing, and different output semantics; they only share a generic file-reading loop pattern.
- 共享行为: Both read from a URL/input stream line by line；Both parse each line and extract data；Both handle exceptions with printStackTrace
- 行为差异: Different return types: HashSet<Integer> vs void with side-effect on Vector；Different parsing: integer vs three-column tab-separated；File access: getResource vs direct URL；Stream closing: not closed vs finally closed
- 修正建议: Train the model to focus more on the data flow and transformations rather than just API call sequences；Incorporate type information and return types into embeddings；Use program slicing to highlight core computational differences

### case_id=4139 FP partial_functionality

- 方法: `addDataFromURL` vs `getRequestContent`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads entire content from a URL and appends it to an internal text buffer, handling exceptions internally.
- B 摘要: Opens an HTTP connection to a URL, reads only the first line, and returns it, throwing exceptions on failure.
- 静态失败原因: Static BERT/GraphCodeBERT models may have overemphasized the lexical overlap of common URL reading APIs (URL, BufferedReader, InputStreamReader, openStream) and ignored the critical difference in control flow (loop vs single read) and return type. The partial functionality overlap (both read from URL) misled the model.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely labels this as non-clone because the functions differ significantly in their purpose (accumulating all content vs retrieving a single line) and in their signatures and exception handling. Although both read from a URL, the specific behavior is not semantically equivalent even under Type-4 (semantic clones).
- 共享行为: Both open a URL and use BufferedReader/InputStreamReader to read from it.；Both close resources after reading.
- 行为差异: A reads all lines and appends them to a buffer; B reads only the first line and returns it.；A handles exceptions internally (prints stack trace, appends URL); B throws exceptions to caller.；A returns void; B returns String.；A uses URL.openStream() (generic); B explicitly uses HttpURLConnection and disconnects.
- 修正建议: Incorporate dataflow analysis to track the number of lines read (loop vs single).；Consider method signature (return type, throws clause) as a distinguishing feature.；Use control flow (while loop presence) as an important semantic indicator.

### case_id=4140 FN partial_functionality

- 方法: `sendRequest` vs `read`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.15`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends an HTTP request with XML payload using GZIP compression, reads compressed response, and parses it as an XML document; also manages server URL/port preferences.
- B 摘要: Reads content from a URL or file path as a buffered input stream, delegating to an overloaded read method and returning a status code.
- 静态失败原因: The static BERT model likely relied on low token-level similarity (Jaccard=0.077) and did not capture the conceptual overlap of URL reading, leading to a non-clone prediction.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled these as Type-4 clones due to both involving network I/O (URL reading) and possibly being considered similar in a broad sense of data retrieval, but the overall functionality differs significantly.
- 共享行为: Both potentially read data from a URL
- 行为差异: Function A sends a request, writes XML, uses GZIP compression, parses XML, and manages preferences; Function B only opens a stream to read.；Function A returns a String (always empty); Function B returns an int status.；Function A handles connection exceptions with a dialog; Function B handles IOException by setting status.；Function A uses preferences system and dialog for server configuration; Function B does not.
- 修正建议: Improve training data to include more nuanced distinctions between functions that share only a small sub-behavior.；Use models that better capture structural or dataflow similarities beyond lexical overlap.

### case_id=4141 FN benchmark_preference_bias

- 方法: `copyFileByNIO` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Copies a file from input to output using NIO FileChannel.
- B 摘要: Launches a NexOpen project configuration by processing Maven pom files and setting up Hibernate and project properties.
- 静态失败原因: Static BERT/GraphCodeBERT correctly identified the lack of semantic similarity due to low lexical overlap and distinct function purposes, thus predicting non-clone. However, the BCB label indicates clone, so the model's prediction is considered a false negative from BCB's perspective, but actually it aligns with semantic understanding.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have incorrectly labeled this pair as a clone possibly due to both methods involving file I/O or resource handling, but the two methods share no common functionality and operate on entirely different domains (file copy vs. project configuration). The low token Jaccard (0.038) confirms minimal lexical overlap.
- 行为差异: copyFileByNIO performs a simple file copy; launch performs complex project configuration.；copyFileByNIO has no side effects besides file writing; launch modifies project resources and properties.；copyFileByNIO is synchronous and straightforward; launch involves XML parsing, property manipulation, and job scheduling.；copyFileByNIO uses NIO channels; launch uses Eclipse framework APIs.
- 修正建议: Re-evaluate the BCB annotation for this pair to ensure it is not a labeling error.；If BCB intends broad Type-4 similarity, clarify criteria to avoid false positives in annotation.

### case_id=4142 FP lexical_or_api_overlap

- 方法: `doGet` vs `main`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: An HTTP GET handler that acts as a reverse proxy, forwarding request to another URL and copying response headers and body.
- B 摘要: A command-line tool that parses a Prolog file, generates adapter classes, and writes a JAR file with compiled classes and serialized adapter information.
- 静态失败原因: Static BERT likely focused on overlapping API terms like 'URL', 'InputStream', 'IOException', ignoring context and overall program logic, causing a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB requires significant semantic similarity; these two unrelated tasks share only generic I/O patterns, which is insufficient for Type-3/4 annotation.
- 行为差异: Different domains: HTTP proxying vs code generation；Different I/O: HTTP request/response vs file/class generation；Different control flow: single HTTP response vs multi-step JAR creation；Different error handling: forwarding error codes vs printing messages and returning
- 修正建议: Incorporate data flow or control flow analysis to distinguish different operational contexts.；Use fine-tuning on a larger set of non-clone pairs that share common APIs but have different semantics.；Add attention to method-level structural patterns beyond token sequences.

### case_id=4143 FN boilerplate_overlap

- 方法: `main` vs `loadExistingAntlibs`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.7`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends an HTTP POST request to RenRen API with predefined parameters and prints the response.
- B 摘要: Loads Ant library definitions from classpath resources by reading lines and resolving URIs.
- 静态失败原因: Static model likely overfit on the common I/O structure (BufferedReader, readLine loop, URL) and missed the completely different application logic.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may consider this a clone due to shared boilerplate pattern of reading lines from a URL/stream using BufferedReader, despite different domain semantics.
- 共享行为: Both use BufferedReader to read lines from a URL-derived input stream；Both handle IOException and use try-catch blocks
- 行为差异: A sends an HTTP POST request; B reads antlib resource files；A uses specific parameter objects; B parses package names and creates URIs；A has a formal main method signature; B is an instance method；A outputs to console; B loads Ant libraries
- 修正建议: Improve model to distinguish between different application domains；Focus on method-level semantic purpose rather than structural patterns；Use data flow analysis to see that the read lines are used differently

### case_id=4144 FN lexical_or_api_overlap

- 方法: `getDatasetsList` vs `runScript`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads lines from a URL, caches them in a map, and returns the list of lines.
- B 摘要: Reads byte data from a URL and concatenates into a string, returns the string or error message.
- 静态失败原因: The model likely relied on lexical overlap and method names, which are low (Jaccard 0.169) and different. It failed to recognize the common pattern of URL data fetching due to token-level differences and absence of named APIs like 'readLine' in B.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may label this as clone because both functions perform the same high-level task: fetching data from a URL via HTTP and returning the content, despite differences in return type and caching. The structural similarity of URL opening, reading loop, and closing is considered a Type-3 clone.
- 共享行为: Both open a URL connection；Both read data from the input stream；Both return the data after reading
- 行为差异: A returns a list of strings (lines), B returns a single string；A caches results in a HashMap, B does not cache；A reads line by line using BufferedReader, B reads byte by byte using BufferedInputStream
- 修正建议: Augment training data with more diverse URL reading implementations；Incorporate data flow analysis to capture stream opening and reading patterns

### case_id=4145 FP boilerplate_overlap

- 方法: `innerProcess` vs `perform`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Computes SHA1 digest from a URI's replay content, optionally stripping regex patterns.
- B 摘要: Processes a web form request, validates session, builds classification XML, sends HTTP request to external service, and handles response to set session attributes and return forward.
- 静态失败原因: The model likely focused on boilerplate patterns like try-catch-finally blocks and resource closing, which are common in both functions, leading to a false positive despite low lexical similarity.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically annotates non-clones for functions with distinct semantics and low syntactic overlap; these functions are from different domains and share no significant functionality.
- 共享行为: Exception handling with try-catch-finally；String manipulation and conversion；Resource management (closing streams)
- 行为差异: Different input types (ProcessorURI vs HTTP request/session)；Different output (sets content digest vs returns ActionForward and modifies session)；Different libraries and APIs (java.security.MessageDigest vs javax.servlet.http, URL connection)；Different overall purpose (content digest computation vs web form processing and external service communication)
- 修正建议: Improve model sensitivity to domain-specific vocabulary and API usage；Incorporate structural abstractions like control flow graphs or data flow analysis；Use contrastive learning to penalize similarity based on generic patterns

### case_id=4146 FN benchmark_preference_bias

- 方法: `getResourceAsStream` vs `streamContains`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Retrieves a resource from a URL, caches it locally, and returns an InputStream.
- B 摘要: Asserts that a given string is contained within the content of an InputStream.
- 静态失败原因: The model correctly predicted non-clone due to low semantic similarity; the BCB label appears to be an anomaly or error.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: The BCB label may be erroneous or based on an extremely broad notion of stream handling, but no legitimate semantic similarity exists.
- 共享行为: Both involve InputStream objects.
- 行为差异: Different purpose: resource loading with caching vs test assertion.；Different input parameters: single String vs String and InputStream.；Different output: returns InputStream vs void with assert.；Different logic: complex HTTP and file I/O vs simple stream reading and string check.
- 修正建议: Review the BCB annotation for this pair; likely a false positive.；Improve benchmark consistency by filtering pairs with very low token overlap.

### case_id=4147 FN boilerplate_overlap

- 方法: `modifyApplicationMessage` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.6`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Modifies a properties file for a given locale by replacing or adding a key-value pair.
- B 摘要: Retrieves a resource as an InputStream with HTTP conditional GET and local caching.
- 静态失败原因: Static BERT models rely on token-level similarities and may overemphasize boilerplate code (e.g., file reading loops, try-catch) while missing the distinct functional intent captured by method names and control flow.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely labeled this as a clone due to both methods being part of the same project's resource-management infrastructure, involving common I/O patterns and exception handling, despite different high-level semantics.
- 共享行为: Both involve file I/O operations (reading/writing files).；Both use try-catch blocks for exception handling.；Both read byte/character streams in a loop.
- 行为差异: Different core purposes: A modifies a properties file; B downloads and caches remote resources.；A operates on locale-specific properties files; B uses URL connections and HTTP caching.；B is synchronized and handles cache lookup; A is not synchronized.；A writes properties in a specific format; B writes raw byte streams to cache files.
- 修正建议: Incorporate structural or dataflow information to distinguish between similar I/O patterns with different goals.；Use method-level embeddings that capture broader context, such as call graphs or API usage.；Consider fine-tuning on clone detection tasks with explicit negative samples of boilerplate-heavy non-clones.

### case_id=4148 FN partial_functionality

- 方法: `getHTML` vs `postXml`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads an HTML page via HTTP GET and optionally writes to a file.
- B 摘要: Sends an XML payload via HTTP POST and returns the response.
- 静态失败原因: Static BERT/GraphCodeBERT may overemphasize token-level differences (method, headers) and low Jaccard similarity, missing the high-level semantic equivalence of fetching HTTP content.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB broad Type-3/4 clones often accept similar core behavior despite differences in HTTP method, headers, and error handling. Both functions perform HTTP requests and return response body, sharing the essential dataflow pattern.
- 共享行为: Both open HTTP connections and set request properties.；Both read response line by line using BufferedReader.；Both build a StringBuilder from response lines and return the string.
- 行为差异: getHTML uses GET; postXml uses POST.；getHTML sets User-Agent header; postXml sets Content-Type, Accept, SOAPAction.；getHTML optionally writes to file; postXml writes request body.；getHTML catches Exception and prints stack trace; postXml catches IOException and throws RuntimeException.
- 修正建议: Train on more diverse Type-3/4 clones with partial functionality overlap.；Use graph-based models that capture API call sequences and dataflow.；Incorporate structural alignment to ignore irrelevant implementation details.

### case_id=4149 FP boilerplate_overlap

- 方法: `addQDInformation` vs `getTicketsForQueue`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a local or remote QD info file and parses lines to update project information objects with new QD values.
- B 摘要: Fetches open tickets for a queue from a REST API, parses ticket IDs from the response, and retrieves each ticket to return as a list.
- 静态失败原因: Static BERT/GraphCodeBERT likely overemphasized the common boilerplate code patterns (BufferedReader, while loop, try-catch) and similar variable names, while missing the divergent semantic intent and data dependencies.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels as non-clone because the two functions serve entirely different business purposes (project info update vs. ticket retrieval) and have distinct data flows and outputs, despite some boilerplate I/O overlap.
- 共享行为: Read text lines from a source using BufferedReader and InputStreamReader；Parse each line conditionally based on prefix patterns；Handle exceptions with try-catch blocks
- 行为差异: Function A reads from a file or URL; Function B makes an HTTP GET request；Function A updates internal state; Function B returns a list of tickets；Function A's parsing involves 'pg' and 'pt' prefixes; Function B parses 'ticket/' prefixed IDs
- 修正建议: Incorporate dataflow analysis to capture differences in input sources and output destinations；Enhance training with more diverse code samples to reduce sensitivity to common I/O patterns；Use contrastive learning to push apart functions with different high-level purposes

### case_id=4150 FN benchmark_preference_bias

- 方法: `getFile` vs `init`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, optionally modifies the endpoint address in the XML, and saves it to a temporary location.
- B 摘要: Initializes a report file handler by backing up an existing report file, writing a new XML report, and recovering unprocessed document IDs from a previous run.
- 静态失败原因: The static model correctly predicted non-clone (0) because the functions share only generic file I/O patterns and have different API usage and logic. The model did not fail; it disagreed with the BCB label, which may be erroneous.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have considered both as initialization routines involving file handling and XML processing, but the overall goals are distinct. The low token similarity suggests BCB might have mislabeled this pair, possibly due to an over-broad interpretation of partial functionality.
- 共享行为: Both perform file I/O operations (creating, reading, writing files).；Both check file existence and handle file creation accordingly.；Both handle exceptions related to file operations and I/O errors.
- 行为差异: Function A downloads a file from a URL, while Function B creates a local report file from scratch.；Function A uses DOM for XML manipulation, whereas Function B uses StAX streaming.；Function B has complex restart logic and recovery of previous state, which Function A lacks.
- 修正建议: Re-evaluate the BCB annotation for this pair to ensure it aligns with semantic equivalence standards.；Improve clone detection models to prioritize high-level semantic similarity over low-level structural overlaps.

### case_id=4151 FP lexical_or_api_overlap

- 方法: `importSequences` vs `getTicketsForQueue`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads biological sequences from a URL and parses them into lists of names and sequences.
- B 摘要: Fetches and parses ticket IDs from a REST API response, then retrieves each ticket and returns a list.
- 静态失败原因: Static BERT/GraphCodeBERT likely focused on token-level overlap (e.g., 'InputStream', 'BufferedReader', 'line', 'readLine') and structural pattern (do-while loop reading lines), mistaking boilerplate I/O for semantic similarity.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the functions have entirely different purpose and output; they only share generic I/O patterns.
- 共享行为: Both read data from a remote source via HTTP；Both parse text line-by-line；Both use input stream readers；Both handle exceptions
- 行为差异: Different domains: biological sequences vs. support tickets；Different data formats: FASTA vs. custom ticket response；Different return types: void populates fields vs. List<RTTicket>；Different error handling: printStackTrace vs. throw/catch/warn
- 修正建议: Enhance model with domain-specific embeddings to distinguish different data types；Incorporate larger context or comment analysis to infer purpose；Add negative sampling of boilerplate-heavy pairs

### case_id=4152 FN benchmark_preference_bias

- 方法: `readGeoParserResult` vs `read`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Reads geo parser results from a URL, parses XML, and returns a collection of place names with associated gazetteer IDs.
- B 摘要: Reads a file or URL specified by name and returns an integer status after reading input stream.
- 静态失败原因: Static BERT methods rely on lexical and syntactic patterns; they correctly identify low similarity and predict non-clone, but BCB label is anomalous.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might label it as clone due to both methods having URL opening and reading, but that is a tiny commonality; they are functionally different.
- 共享行为: Both involve opening a URL stream and reading data from it.
- 行为差异: Function A parses XML and processes geospatial data, while B just reads raw bytes.；Function A has retry logic and returns a collection of tuples, B returns status integer.；Function A has multiple nested loops and XML parsing, B is straightforward stream reading.
- 修正建议: Re-evaluate BCB label for this pair; likely a false positive.

### case_id=4153 FP lexical_or_api_overlap

- 方法: `getDatasetsList` vs `getVersion`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches a list of datasets from a server URL with caching and error handling.
- B 摘要: Retrieves a version string from a fixed URL, returning null on failure.
- 静态失败原因: The model was tricked by the high lexical overlap of common Java API patterns (URL, BufferedReader, InputStreamReader, readLine, try-catch) and similar control flow structure (while loop reading lines), leading to false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely considers these as non-clones due to clear differences in purpose (list vs version), different input/output, and only superficial similarity in using URL/IO boilerplate.
- 共享行为: Both open a URL and read text lines using BufferedReader；Both catch exceptions and handle errors；Both return a String or List from the read data
- 行为差异: A returns a list of multiple lines, B returns a single line (overwrites in loop)；A uses caching (HashMap), B does not；A is synchronized and takes a parameter URL, B is static and uses a fixed URL；A throws RuntimeException on error, B returns null on error
- 修正建议: Add more distinguishing features like method name and signature embedding；Incorporate dataflow analysis to capture variable usage (e.g., overwriting variable vs accumulating list)；Use deeper semantic similarity models that focus on functional intent rather than surface syntax

### case_id=4154 FN partial_functionality

- 方法: `copyResource` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource from a URL or file to a destination file using byte-by-byte I/O, throwing an exception if the resource cannot be found.
- B 摘要: Copies a file from one path to another, creating parent directories and skipping if source and destination are the same, with exception logging.
- 静态失败原因: Low token Jaccard (0.234) and differences in method signature, exception handling, and additional logic (URL handling, directory creation) likely caused the model to miss the shared core copying functionality.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considers them clones because the core byte-copying loop is identical, and differences in source retrieval and error handling are often considered minor in Type-3/Type-4 clone annotations.
- 共享行为: Both perform byte-by-byte copying from a source to a destination using InputStream/OutputStream
- 行为差异: A supports URL sources; B only file sources；A throws exceptions; B catches and logs；A does not check for same source/destination; B does；A uses instance variables; B takes parameters
- 修正建议: Focus on core I/O loop patterns beyond lexical overlap；Use data flow analysis to identify equivalent read-write sequences；Incorporate broader context to recognize similar functionality despite different error handling

### case_id=4155 FN partial_functionality

- 方法: `modifyApplicationMessage` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Modifies a message in a locale-specific properties file, creating the file by copying the English version if missing.
- B 摘要: Copies a source file to a destination with overwrite confirmation and progress display.
- 静态失败原因: Static BERT/GraphCodeBERT methods rely heavily on local token overlap and may overlook the shared file copy subtask due to low Jaccard similarity (0.24) and different high-level purposes. The model likely focused on the distinct task names and main logic, missing the common file I/O pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider these clones because both functions perform file copy as a core subtask (A copies English file to locale file when missing, then reads and writes the locale file again) and share similar boilerplate code for file I/O, streams, and error handling, aligning with broad Type-4 similarity.
- 共享行为: Both involve reading file content and writing to another file.；Both use file streams and buffered readers/writers.；Both handle exceptions during file operations.；Both conditionally create a destination file based on source file existence.
- 行为差异: A is for updating configuration values; B is for generic file copying.；A includes line-by-line replacement of a key-value pair; B copies raw bytes.；B has user interaction for overwrite confirmation; A does not.；B has progress indicator; A does not.
- 修正建议: Use techniques that capture hierarchical or sub-task structures, such as graph-based representations with data flow.；Incorporate API usage patterns and common utility function detection.；Augment training with more diverse Type-3/Type-4 clones that share partial functionality.；Consider fine-tuning on BCB with explicit partial functionality labels.

### case_id=4156 FN boilerplate_overlap

- 方法: `readIntoList` vs `run`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Parses HTML anchor tags from a URL to populate a map of JMenuItems with action listeners.
- B 摘要: Performs HTTP GET request with basic authentication and reads the response into a string.
- 静态失败原因: The static BERT/GraphCodeBERT model likely failed due to low token Jaccard (0.1685) and superficial structural differences (e.g., JMenuItem vs HttpURLConnection), leading to classification as non-clone while missing the higher-level I/O similarity.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may label them as clones because both involve reading from a URL and processing lines, a common I/O pattern, and they are likely from the same project, sharing similar boilerplate code.
- 共享行为: Both open a URL connection；Both read lines using BufferedReader；Both handle IOExceptions
- 行为差异: A parses HTML to extract command names and creates UI components; B does not parse HTML；B sends HTTP request with authentication; A does not；A populates a map with JMenuItems; B concatenates response lines into a string；A adds action listeners to menu items; B sets a finish flag and stores result
- 修正建议: Enhance model to recognize hierarchical functional similarity beyond token overlap；Incorporate data flow and control flow analysis for deeper semantic understanding；Use more abstract representations of I/O operations to capture shared patterns

### case_id=4157 FN benchmark_preference_bias

- 方法: `getFile` vs `readAndRewrite`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies the endpoint attribute in the XML, and saves it to a temporary directory, returning the file path.
- B 摘要: Reads a DICOM image file, parses it, reads pixel data, and writes it to an output file.
- 静态失败原因: Static model did not fail; it correctly predicted non-clone. The false negative arises because the BCB label is likely a false positive in the benchmark.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might have considered both as 'file processing' clones due to the common pattern of reading, transforming, and writing files, but this interpretation is overly broad and does not align with typical functional equivalence standards.
- 共享行为: Both perform file I/O operations (reading and writing files).
- 行为差异: Function A downloads from URL, modifies XML, and returns file path; Function B reads local DICOM file and writes to output file without returning.；Function A handles web service-specific tasks (WSDL, AxisFault); Function B handles medical image format (DICOM, DcmParser).；Function A checks for existing file and conditionally downloads; Function B always processes input.；Function A uses NIO channels and streams; Function B uses ImageIO and DICOM-specific APIs.
- 修正建议: Re-evaluate the ground truth label in BigCloneBench for this pair; it appears to be a false positive.；Improve clone detection models to better ignore superficial commonalities like file I/O when the core functionality differs.

### case_id=4158 FN partial_functionality

- 方法: `getFile` vs `copyJar`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, optionally modifies an XML element, and returns the local file path.
- B 摘要: Copies a file from source to destination using FileChannel.
- 静态失败原因: Low token overlap (0.116) and different method names/structures caused the model to miss the shared transferFrom pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as 'copy data from one source to another' and thus semantically similar, overlooking context differences.
- 共享行为: Both use FileChannel.transferFrom to copy data；Both handle IOException and close channels
- 行为差异: A involves downloading from URL, XML parsing, and modification; B is a simple file copy；A returns file path; B is void；A has extensive logging and throws AxisFault; B has minimal logging and throws IOException
- 修正建议: Enhance model to detect sub-functional similarities (e.g., common I/O patterns) beyond lexical overlap；Incorporate dataflow analysis to identify shared operations like file copying

### case_id=4159 FN boilerplate_overlap

- 方法: `modifyApplicationMessage` vs `decodeFileToFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Modifies a localized properties file by updating or adding a message key-value pair.
- B 摘要: Decodes a Base64-encoded input file to an output file.
- 静态失败原因: The static model correctly identified that the core logic (properties modification vs. Base64 decoding) is completely different, thus predicting non-clone. Its failure is from BCB's perspective only; it accurately captured semantic dissimilarity.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely considered these clones due to the shared boilerplate of file reading/writing and exception handling, possibly as a Type-3 or Type-4 clone under a lenient view of structural similarity.
- 共享行为: Both perform file I/O operations (read and write)；Both handle exceptions with try-catch-finally；Both close input/output streams
- 行为差异: A parses and modifies property entries; B decodes Base64 binary data；A uses character streams and properties; B uses byte streams with Base64 decoding；A may create a missing file by copying a default; B does not create files；A writes text with line breaks; B writes binary buffers
- 修正建议: Adjust BCB annotation guidelines to exclude pairs that only share common file I/O boilerplate without functional similarity；Static models should continue to differentiate based on semantic content; current prediction is reasonable

### case_id=4160 FN benchmark_preference_bias

- 方法: `downLoadZippedFile` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Downloads a ZIP file from a URL, extracts it to a destination directory, and returns a local URL pointing to that directory.
- B 摘要: Builds an entire site for editing by iterating over pages, reading XML and control files, applying XSLT transformations, and writing output files.
- 静态失败原因: The static model did not fail; it correctly predicted non-clone. The error is a false negative relative to the BCB label, which is likely incorrect.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as a clone due to broad criteria like both performing file operations and using similar exception handling patterns, or possibly due to annotator error given the low similarity.
- 共享行为: Both involve file I/O operations (reading/writing files).；Both handle exceptions and use try-finally blocks for resource cleanup.
- 行为差异: A is a simple download and unzip; B is a complex multi-step site generation with XML transformations, string manipulation, and FTP integration.；A returns a URL; B returns void and writes multiple output files.；A has very few lines and a single purpose; B has hundreds of lines and many sub-steps.
- 修正建议: Re-evaluate the BCB label for this pair; it may be a mislabel.；Improve BCB annotation guidelines to avoid over-broad cloning criteria.；Use more fine-grained clone types to distinguish between similar-only-in-boilerplate pairs.

### case_id=4161 FN benchmark_preference_bias

- 方法: `runScript` vs `callApiPost`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Fetches content of a script file from a URL by reading the entire stream into a string, with error handling returning 'error!'.
- B 摘要: Sends an HTTP POST request with parameters and headers, checks response code, and returns the response body as an InputStream with optional GZIP decoding, throwing an exception on failure.
- 静态失败原因: The model correctly detected the differences in low token overlap (0.1688) and distinct control flow, leading to a non-clone prediction, but BCB's lenient partial functionality criteria caused a mismatch.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider this a clone because both methods perform network I/O operations (fetching data from a URL) and share similar underlying structure (URL open, stream reading, exception handling), fitting a broad Type-3/4 definition.
- 共享行为: Both create a URL object and open a connection；Both read from an input stream；Both have try-catch exception handling
- 行为差异: A uses GET (openStream), B uses POST with request body；A returns a String, B returns an InputStream；A reads entire content into a single string, B returns stream for external reading；A's error handling returns a static string, B throws a custom exception
- 修正建议: Incorporate API-level semantic similarity (e.g., both are HTTP-based data retrieval) to align with BCB's lenient annotation；Adjust clone detection threshold to accept broader partial functionality

### case_id=4162 FN benchmark_preference_bias

- 方法: `sendExceptionToServer` vs `GetResponse`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `preference_memory_with_manual_audit`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Sends an exception report to a server by constructing a POST request with encoded parameters and reading the response to confirm success.
- B 摘要: Performs an HTTP GET request to a given URL and returns the response content as a string.
- 静态失败原因: Static BERT models like GraphCodeBERT focus on local token patterns and control flow but lack understanding of overall task semantics. The low lexical overlap (Jaccard=0.236) and differences in specific API calls led the model to predict non-clone, ignoring the broader similarity in network communication behavior that BCB considers.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may label this as a clone because both functions perform network I/O via URL connections and read responses, which is considered similar at a high level under broad Type-3/4 criteria, despite differences in HTTP method and data sending.
- 共享行为: Both open a URL connection.；Both read the response line by line using BufferedReader.；Both contain try-catch blocks for IOException.
- 行为差异: A sends data (POST-like) while B only reads (GET).；A expects a specific success message 'success', B returns the entire content.；A prints messages to stdout, B returns the content string.；A uses URLConnection, B uses HttpURLConnection with explicit GET method.
- 修正建议: Incorporate higher-level API usage patterns (e.g., URLConnection usage) as features.；Use pre-training objectives that capture task-level semantics.；Add a contrastive loss to distinguish between Type-3 and Type-4 clones.

### case_id=4163 FP lexical_or_api_overlap

- 方法: `main` vs `copyFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Parses a Prolog file and generates adapter classes and resources.
- B 摘要: Copies a file from source to target using FileChannel.
- 静态失败原因: Static BERT may have been misled by common file-handling keywords (File, IOException) and ignored the vast difference in overall logic and length.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels as non-clone because the functions have no functional similarity; one is a generative pipeline, the other a simple copy.
- 共享行为: Both perform file I/O operations
- 行为差异: Function A is a complex main method involving parsing, code generation, and class writing；Function B is a simple utility copying file contents
- 修正建议: Incorporate control flow and data dependency graphs；Use structural similarity measures beyond token overlap；Apply length normalization or complexity weighting

### case_id=4164 FN benchmark_preference_bias

- 方法: `patch` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.85`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Copies Minecraft jar to backup and opens it as JarFile if mods list is non-empty.
- B 摘要: Launches a NexOpen project in Eclipse, handling Maven POMs and Hibernate configuration, including reverse engineering file setup and project installation.
- 静态失败原因: The model likely detected low lexical overlap and distinct semantic contexts, correctly predicting non-clone. The BCB annotation may be erroneous or influenced by a broad interpretation of 'file patching' similarity.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: Possible overgeneralization of file manipulation tasks; both methods involve file I/O and exception handling, but overall functionality is unrelated.
- 共享行为: Both perform file I/O operations (copy, create, open files).
- 行为差异: Function A is a simple patch operation on a single file; function B is a complex project launch involving multiple files, properties, and Eclipse API.；Function A throws IOException; function B throws CoreException.；Function A has no parameters; function B has multiple parameters and uses them extensively.；Different domains: Minecraft modding vs. Eclipse plug-in for Hibernate/NexOpen.
- 修正建议: Re-annotate this pair to verify BCB label consistency.；Incorporate domain-specific context to avoid false positives from generic API overlap.；Use higher-level functional similarity measures beyond simple file I/O presence.

### case_id=4165 FN partial_functionality

- 方法: `File2String` vs `handledRun`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads file content from filesystem or classpath and returns as string.
- B 摘要: Downloads game data XML from URL, checks version, optionally writes to local file, and loads game database.
- 静态失败原因: Static BERT/GraphCodeBERT models rely on token overlap and structural similarity; the low Jaccard similarity and differing control flow (conditionals, error handling patterns) may have caused the model to miss the underlying partial functional similarity that BCB considers.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider them clones because both involve reading input streams with similar boilerplate code (BufferedReader, InputStreamReader, try-catch), and BCB's broad annotation guidelines often accept partial functionality or similar I/O patterns as Type-4 clones.
- 共享行为: Both use BufferedReader and InputStreamReader for reading input.；Both handle I/O exceptions with try-catch blocks.；Both read data from a source (file or URL).
- 行为差异: File2String returns the file content as a string; handledRun does not return a value and performs side effects.；handledRun includes version checking and conditional file writing; File2String does not.；handledRun involves complex error handling with dialogs and logging; File2String uses System.out and System.exit.；The input sources differ: file vs URL.
- 修正建议: Incorporate dataflow or control flow analysis to capture shared I/O patterns.；Use graph-based models sensitive to sequence of API calls and exception handling.；Include more diverse training examples of partial functionality clones.

### case_id=4166 FP lexical_or_api_overlap

- 方法: `getLinksFromURLFast` vs `doVersionCheck`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Extracts hyperlinks and their text from a given URL using regex, returns a vector array of links and texts.
- B 摘要: Checks for a new version of jEdit by reading a version file from a URL and comparing the build number, displaying a message to the user.
- 静态失败原因: The static model likely over-emphasized the common API usage (URL, BufferedReader, readLine) and the loop structure, leading to a false positive based on lexical and API overlap rather than semantic similarity.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would consider these as non-clones because they perform entirely different tasks (link extraction vs. version checking) despite sharing some boilerplate code for URL reading.
- 共享行为: Both open a URL connection and read data line by line using BufferedReader.；Both close the input stream after reading.
- 行为差异: Function A extracts links and texts from HTML; Function B parses version/build info from a plain text file.；Function A performs regex matching on page content; Function B checks line prefixes.；Function A returns a data structure; Function B updates UI and returns void.
- 修正建议: Incorporate control-flow and data-flow analysis to distinguish core logic.；Use a more fine-grained comparison that identifies the different tasks (e.g., regex extraction vs. conditional version parsing).；Train on more negative examples with similar boilerplate but different intent.

### case_id=4167 FP lexical_or_api_overlap

- 方法: `importRoles` vs `executePost`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Imports role names from XML at a given URL by reading lines and parsing XML fragments.
- B 摘要: Executes an HTTP POST request with parameters and returns the response body as a string.
- 静态失败原因: The static model likely overemphasized the common lexical tokens (URL, BufferedReader, readLine, StringBuffer) and control flow structure, overlooking the different method calls (openStream vs getOutputStream, parseRoleName vs writeBytes) and overall purpose.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically treats functions with different I/O intentions (GET vs POST, XML parsing vs raw response) as non-clones, as the core functionality differs significantly.
- 共享行为: Both create a URL object from a string parameter；Both open an input stream and wrap it in a BufferedReader；Both read lines in a while loop and append to a StringBuffer
- 行为差异: A parses XML to extract role names; B sends a POST request with URL parameters；A collects multiple results; B returns a single response string；A uses GET-like reading; B explicitly sets POST method and writes data；B handles connection cleanup in finally; A does not
- 修正建议: Incorporate method names and parameter types as features；Use call sequence or data-flow analysis to distinguish I/O patterns；Add attention to method invocations and exception handling differences

### case_id=4168 FN partial_functionality

- 方法: `modifyApplicationMessage` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Modifies a properties file by changing or adding a key-value pair for a given locale, copying a default file if needed.
- B 摘要: Copies a file from source to destination using NIO channels.
- 静态失败原因: Static models may rely on local API overlaps (e.g., File, FileInputStream/Reader) and miss the overall semantic difference due to lack of reasoning about the main modification logic vs. pure copy.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as file manipulation functions, and the file copy sub-task in A is similar to B's full task, leading to a Type-4 clone label.
- 共享行为: Both perform file I/O operations (reading and writing files).
- 行为差异: Function A modifies a properties file by replacing a specific key-value pair, while Function B copies an entire file without content modification.；Function A uses character-stream I/O and string processing, while Function B uses NIO channels for file copying.；Function A includes conditional logic to copy a default file if the target doesn't exist, while Function B always copies the source file.
- 修正建议: Incorporate data flow analysis to distinguish main functionality from sub-tasks.；Use contrastive learning on pairs that share some operations but differ in overall purpose.

### case_id=4169 FP lexical_or_api_overlap

- 方法: `readZoneIDs` vs `readURL`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads zone IDs from a file resource and returns them as a HashSet of integers.
- B 摘要: Reads content from a URL and prints each line to standard output.
- 静态失败原因: The static BERT model likely focused on structural similarities (e.g., both use try-catch, readLine, similar variable names) and high token overlap, while missing the critical semantic differences in input/output types and behavior.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB considers these non-clones because they perform fundamentally different operations: one reads a file of integers and returns a set, the other reads a URL and prints lines. They are not semantically equivalent.
- 共享行为: Both open an input stream from a URL-like source；Both read lines from the stream；Both catch exceptions and print stack trace
- 行为差异: Function A parses each line as integer and adds to a set; Function B prints each line to console；Function A returns a HashSet; Function B returns void；Function A does not close streams; Function B closes streams in finally；Function A takes a String; Function B takes a URL
- 修正建议: Improve model's ability to distinguish between returning data and side-effect operations；Incorporate dataflow analysis to capture differences in return types and variable usage；Augment training data with more non-clone pairs that have similar I/O patterns but different end goals

### case_id=4170 FP lexical_or_api_overlap

- 方法: `read` vs `loadURL`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a skeleton file from classpath, parses it into sections separated by '---', and validates the number of sections.
- B 摘要: Opens a URL connection with optional basic authentication, reads the response line by line, writes to a temporary file, and updates a status label with download progress.
- 静态失败原因: A static BERT/GraphCodeBERT model may have been misled by the overlapping tokens like 'BufferedReader', 'InputStreamReader', 'readLine', and the structural similarity of reading lines. Without understanding the broader context (purpose, error handling, output destination), it overemphasized lexical overlap.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely considers these non-clones because they have different high-level purposes: one is for reading structured skeleton files, the other for downloading and saving web content with authentication and progress tracking. The shared usage of BufferedReader is too generic to warrant clone label.
- 共享行为: Both read lines from an input stream using BufferedReader；Both handle IOExceptions (declared in method signature)
- 行为差异: Function A reads from a local classpath resource, while B reads from a remote URL；Function A parses sections and validates count, B writes to a tmp file and updates UI；Function A uses UTF-8 encoding, B does not specify encoding；Function A throws Exception for missing file or wrong section count, B writes to file and prints to console
- 修正建议: Incorporate data-flow analysis to track how input is obtained (local vs remote)；Add context-aware features like method name, surrounding class, and invoked methods on the stream；Use contrastive learning with harder negative examples that share API calls but differ in purpose

### case_id=4171 FP lexical_or_api_overlap

- 方法: `getUser` vs `callApiPost`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Loads a user from a DAO or reads from a config file if not found.
- B 摘要: Performs an HTTP POST request with parameters and returns the response InputStream.
- 静态失败原因: Static BERT may have overemphasized common API tokens like 'URL', 'BufferedReader', 'InputStream', and control flow structure, leading to a false positive match.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels as non-clone because the functions have completely different purposes (user lookup vs. API call) despite sharing some low-level I/O patterns.
- 共享行为: Both use URL and stream I/O operations；Both handle exceptions with try-catch
- 行为差异: Function A is about user authentication from a local file; Function B is about making a remote API call；Function A returns a User object; Function B returns an InputStream；Function A writes to a DAO; Function B sends HTTP POST and reads response
- 修正建议: Incorporate more semantic understanding of domain-specific operations；Use dataflow analysis to distinguish local file I/O from network I/O；Improve handling of method signatures and return types

### case_id=4172 FP lexical_or_api_overlap

- 方法: `executeHttpGet` vs `getTicketsForQueue`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Executes an HTTP GET request and returns the response body as a JSONObject.
- B 摘要: Queries a ticket queue via HTTP GET, parses ticket IDs from response, then fetches each ticket and returns a list of RTTicket objects.
- 静态失败原因: Static BERT may have focused on lexical overlap like 'HttpGet', 'BufferedReader', 'readLine' and missed the control flow differences and output types.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels non-clone because the functions have different purposes and outputs despite sharing HTTP GET.
- 共享行为: Send HTTP GET requests；Read response line by line
- 行为差异: A returns JSONObject of whole response; B returns list of tickets after additional processing；B builds URL with query params, handles error codes, checks for 'does not exist.', parses ticket IDs, then fetches each ticket；A does not handle error codes or parse specific content
- 修正建议: Incorporate structural differences (e.g., AST, data flow) to capture logic beyond API usage；Improve attention to return types and overall function purpose

### case_id=4173 FN benchmark_preference_bias

- 方法: `buildSiteForEdit` vs `patch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.6`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Builds a site for editing by processing pages, transforming XML with XSLT, and writing output files.
- B 摘要: Creates a backup of the Minecraft jar file and opens the original jar for patching.
- 静态失败原因: Static BERT likely failed because the methods have very low token overlap (Jaccard=0.033) and completely different control flows, so it correctly predicted non-clone; the error is due to BCB label being overly broad.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled as clone due to both methods involving file input/output and being part of larger systems, but the functionality and complexity differ greatly.
- 共享行为: Both perform file I/O operations (reading and writing files).；Both throw IOException.
- 行为差异: A is a complex method with many parameters, loops, and transformations; B is short and simple.；A writes transformed content for multiple pages; B copies a single file and opens a jar.；A involves DOM and Transformer; B uses simple file streams.
- 修正建议: Improve clone definition consistency; avoid classifying completely different methods as clones.；Use functional similarity analysis based on intent rather than API usage.

### case_id=4174 FN other

- 方法: `testCopy_readerToWriter_nullIn` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Tests that IOUtils.copy throws NullPointerException when reading from a null reader.
- B 摘要: Builds a site for editing by reading pages, applying XSLT transformations, and writing output files.
- 静态失败原因: Static BERT predicted non-clone correctly; it likely failed to override the erroneous BCB label.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely labeled this as a clone erroneously due to a benchmark data error, as the functions are semantically unrelated.
- 共享行为: Both involve writing to a writer or file output
- 行为差异: Function A is a unit test expecting an exception; Function B is a complex business logic method；Different input/output: A uses in-memory streams, B uses files and properties；Different exception handling: A expects NPE, B handles various IO and transformation exceptions；Different purpose and context
- 修正建议: Ensure benchmark labels are accurate; use better data curation

### case_id=4175 FP lexical_or_api_overlap

- 方法: `handleHandshake` vs `getUser`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Handles Minecraft handshake by validating server key and sending login packet or shutting down.
- B 摘要: Retrieves a user by login from a database or config file.
- 静态失败原因: Static BERT may have been misled by overlapping structural patterns (URL reading, BufferedReader, try-catch) and keyword overlap ('url', 'username', 'user') without understanding context.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled non-clone because functions have completely different behavior despite some shared structural patterns.
- 共享行为: Both read from a URL using BufferedReader and InputStreamReader；Both use try-catch blocks and print stack traces；Both have conditional logic based on string comparisons
- 行为差异: Different domain: Minecraft client vs user management；Different I/O: one sends a login packet, returns nothing; one returns a User object；Different error handling: one shuts down network, one returns null
- 修正建议: Incorporate deeper semantic understanding, e.g., by analyzing method purpose or using data flow.；Use control-flow and data-flow analysis to distinguish different operations.；Consider domain-specific context or method names.

### case_id=4176 FP lexical_or_api_overlap

- 方法: `getDatasetsList` vs `getFullScreenUrl`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a list of dataset names from a URL and caches it in a map.
- B 摘要: Extracts YouTube video metadata (video_id, t, title) from a URL to construct a fullscreen video URL.
- 静态失败原因: The static BERT model likely overfitted on the common I/O patterns (URL, BufferedReader, while readLine, try-catch-finally) and ignored the distinct method names and differing core logic, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would label these as non-clones because the overall functionality and output are completely different: one is about fetching a list of datasets, the other about extracting a YouTube video URL. The shared I/O boilerplate is not enough to warrant a clone label.
- 共享行为: Both open a URL and read lines from an HTTP response using BufferedReader.；Both use try-catch-finally blocks for exception handling and resource cleanup.；Both parse or process the read data in a loop.
- 行为差异: A caches results in a map; B does not cache.；A reads all lines and adds to a list; B searches for a specific line containing 'fullscreenUrl' and parses it.；A returns a list of strings; B returns a single URL string.；A uses a static synchronized method with a cache; B is an instance method with no synchronization.
- 修正建议: Train the model to better differentiate boilerplate code from core functionality, e.g., by masking or down-weighting common library calls.；Incorporate method-level context (name, return type, class) to capture intent.；Use data-flow or control-flow features to highlight differences in data manipulation.；Augment training data with more similar-appearing but semantically different pairs.

### case_id=4177 FN benchmark_preference_bias

- 方法: `testSimpleQuery` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.6`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Test method that writes XML data to a JCR source, executes a query, and verifies the result matches expected XML content.
- B 摘要: Launch configuration handler for a NexOpen project that reads and processes Maven pom.xml files, sets up Hibernate dialect, and schedules an install action.
- 静态失败原因: The static BERT/GraphCodeBERT model likely failed because it focused on the low lexical overlap (token Jaccard 0.07) and the stark difference in method names and overall structure, missing the high-level similarity in stream/XML handling that BCB annotators considered.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may label them as clones due to shared low-level I/O patterns (ByteArrayOutputStream, IOUtils.copy) and XML manipulation, which could be considered Type-4 semantic similarity in the context of data processing routines.
- 共享行为: Both use ByteArrayOutputStream and IOUtils.copy for stream operations；Both involve processing XML-like content (though in different contexts)
- 行为差异: Function A is a test for JCR query correctness; Function B is a project launch setup with multiple file operations；Function A writes XML to a source, then reads back via query; Function B reads existing XML files and modifies them；Function A has a simple assertion; Function B has complex conditional logic and error handling；Function A operates on a single query; Function B iterates over files and configurations
- 修正建议: Incorporate dataflow analysis to recognize similar I/O patterns across different domains；Use graph-based models that capture structural similarity in resource handling；Adjust threshold for Type-4 clones to require more specific behavioral similarity

### case_id=4178 FN partial_functionality

- 方法: `modifyApplicationMessage` vs `setImg`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Modifies a properties file for a given locale by replacing or appending a key-value pair.
- B 摘要: Copies a user-selected image file to an images directory and sets it as an image icon.
- 静态失败原因: The static model likely focused on distinct high-level APIs (Properties, JFileChooser, ImageIcon) and overall intent, missing the common file copy idiom and structure.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider these clones due to shared low-level file copy idiom (byte-by-byte loop) and similar file/directory creation pattern, despite different high-level purposes, fitting a broad Type-4 or partial functionality similarity.
- 共享行为: Both perform file existence checks and create files or directories if missing；Both use a byte-by-byte read-write loop (while ((c = in.read()) != -1) out.write(c))；Both handle exceptions with printStackTrace；Both operate on files with similar I/O stream management
- 行为差异: A modifies a properties file with specific key-value replacement; B copies an image file regardless of content；A takes parameters (locale, messageName, messageValue); B takes no parameters and uses a file chooser；A reads from a classpath resource and writes to a file; B copies from one file path to another；A handles property file formatting lines; B sets an ImageIcon and updates paths
- 修正建议: Incorporate detecting common low-level patterns (e.g., file copy loops) as similarity features；Use graph-based representations that capture data flow and control flow similarity；Balance local pattern matching with global semantic understanding

### case_id=4179 FP boilerplate_overlap

- 方法: `main` vs `copyFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Parses a Prolog file and generates adapter classes and serialized data.
- B 摘要: Copies a file from source to destination with error handling.
- 静态失败原因: The model likely over-emphasized common boilerplate tokens (e.g., try, catch, File, IOException) and ignored the low Jaccard similarity, treating both as similar due to shared structural patterns in code snippets.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels as non-clone because the functions have entirely different purposes and implementations, with only superficial shared patterns like exception handling.
- 共享行为: Both use file I/O operations and exception handling
- 行为差异: Function A performs complex code generation and manipulation, while B copies file contents；Function A handles command-line arguments, parsing, and class loading; B uses fixed file streams；Function A has multiple nested logic and output artifacts; B is a straightforward copy loop
- 修正建议: Incorporate syntactic structure or AST-based features to distinguish boilerplate from core logic；Use longer n-gram or sequence models to capture task-specific semantics

### case_id=4180 FN partial_functionality

- 方法: `read` vs `register`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a camera log from a URL, parsing each line into CameraLogRecord objects, adding them to a list, and sorting the list.
- B 摘要: Registers a user by encoding password, setting registration date, adding default authority, creating a hash, creating a phpBB forum user via URL connection, persisting the user, and sending a confirmation email.
- 静态失败原因: Static BERT models rely on token overlap and structural embeddings; low Jaccard similarity (0.1357) and divergent logic after the initial I/O setup correctly predicted non-clone, but failed to match BCB's broader criteria that accept partial functionality similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider the common I/O pattern (URL opening and BufferedReader usage) as a clone, even though the overall functionality differs, possibly labeling it as a Type-3 clone due to similar structure in that portion.
- 共享行为: Both open a URL connection and read lines using BufferedReader；Both handle IOException and log messages
- 行为差异: Function A only reads and parses log records; Function B additionally performs user registration, password encoding, database persistence, and email sending；Function A logs with log.info/log.isInfoEnabled; Function B uses logger.debug/error；Function A sorts records after reading; Function B uses the read line to set forum ID and has no sorting
- 修正建议: Use hierarchical similarity thresholds to distinguish core functionality from common boilerplate；Incorporate data flow analysis to identify which operations are central vs. auxiliary；Train or fine-tune on BCB-style annotations to capture broad clone definitions

### case_id=4181 FN benchmark_preference_bias

- 方法: `sendExceptionToServer` vs `parse`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Sends exception details to a server via HTTP POST.
- B 摘要: Parses a delimited data file or URL into a DataSet object.
- 静态失败原因: The model correctly predicted non-clone due to low token overlap and functional disparity; it succeeded in not being fooled by superficial I/O similarities.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as clone due to both functions involving reading from URLs and writing data, but this is a stretch; more likely an annotation error.
- 共享行为: Both perform I/O operations；Both use BufferedReader and InputStreamReader；Both handle exceptions with try-catch
- 行为差异: A sends data to server; B reads and parses local/remote data；A constructs URL-encoded parameters; B parses tokens and builds DataSet；A prints responses; B returns DataSet；B handles headers, types, delimiters; A does not
- 修正建议: Re-evaluate BCB annotation for this pair; it may be a false positive clone annotation.；Improve clone detection to not overgeneralize on I/O operations alone.

### case_id=4182 FP boilerplate_overlap

- 方法: `getLinksFromURLFast` vs `run`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Extracts hyperlinks and anchor texts from an HTML page given a URL.
- B 摘要: Reads a resource from classpath and displays its content in a Swing text component.
- 静态失败原因: The static model over-relied on token overlap (e.g., URL, BufferedReader, readLine, InputStreamReader, StringBuilder) and missed the semantic divergence in the final purpose and output.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels as non-clone because the core functionality differs: one extracts links, the other loads a resource into a GUI. The shared I/O boilerplate is incidental.
- 共享行为: Both open a URL/stream；Both use BufferedReader to read lines；Both build a string from the read lines
- 行为差异: A uses regex to parse HTML and extract links and texts, returns vectors; B reads entire resource and sets text in a GUI component.；A does not involve GUI; B uses SwingUtilities.invokeLater for thread safety.；A appends lines without newlines; B appends "\r\n" after each line.
- 修正建议: Train with more examples that share I/O setup but differ in final functionality.；Incorporate structural matching that accounts for the overall method goal, e.g., using data flow or call graph analysis.；Add negative examples with high token overlap but different semantics.

### case_id=4183 FP lexical_or_api_overlap

- 方法: `getFrameworkFactory` vs `getNetworkServersIPs`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a service resource file to instantiate an OSGi framework factory.
- B 摘要: Parses a network resource file to extract server IP addresses.
- 静态失败原因: Static model likely overfitted on the common API calls (URL, BufferedReader, readLine) and missed the distinct domain-specific processing inside the loops.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels non-clone because the two methods have entirely different business logic and output types, despite some structural overlap in I/O boilerplate.
- 共享行为: Both use URL, BufferedReader, InputStreamReader to read lines from a text resource.；Both iterate over lines with readLine() and perform conditional processing.
- 行为差异: Function A reads from classpath resource; B reads from arbitrary URL.；Function A throws exception on failure; B catches and prints stack traces.；Function A returns a single object; B returns a vector of strings.；Function A ignores comment lines; B looks for specific markers (!SERVERS and ;).
- 修正建议: Incorporate dataflow analysis to distinguish different loop semantics.；Use control flow graphs with richer node representations capturing API call arguments.

### case_id=4184 FN partial_functionality

- 方法: `copyFile` vs `getFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a local file to another local file using FileChannel transferTo.
- B 摘要: Downloads a WSDL file from a URL, optionally modifies its endpoint, saves locally, and returns the file path.
- 静态失败原因: Static BERT likely overweighed low token overlap (0.1496), different method names, and distinct control flow, missing the underlying common data-transfer pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often treats partial functional similarity, especially involving file copying via channels, as Type-4 clones. Here, both employ core file-transfer logic, even though getFile adds network and XML processing.
- 共享行为: Both perform file I/O operations involving reading and writing files.；Both use FileChannel for efficient data transfer.；Both handle IOExceptions.
- 行为差异: copyFile copies between local files; getFile downloads from a URL.；getFile includes XML modification and conditional download based on file existence.；getFile returns a file path; copyFile returns void.；getFile handles multiple exception types (AxisFault, SAXException, etc.).
- 修正建议: Incorporate heuristics for common I/O patterns like transferTo/transferFrom.；Use dataflow analysis to detect channel-based copy operations.；Include structural matching of try-with-resources or channel usage.

### case_id=4185 FP lexical_or_api_overlap

- 方法: `getLinksFromURLFast` vs `getNetworkServersIPs`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Extracts all hyperlinks and anchor text from an HTML page using regular expressions and returns them as two vectors.
- B 摘要: Parses a network server list from a text file format, extracting IP addresses after '!SERVERS' marker, and returns them as a vector of strings.
- 静态失败原因: Static BERT likely over-relied on shared lexical tokens (URL, BufferedReader, readLine, Vector) and the overall structure (open connection, read lines, return vector), missing the completely different parsing logic and output structures.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels non-clones when the core functionality differs despite similar boilerplate. Here, both functions read from a URL but perform entirely different parsing tasks, so they are not considered clones.
- 共享行为: Both open a URL, read its content line by line using BufferedReader, and return a Vector of extracted data.；Both use URL, URLConnection, InputStreamReader, and BufferedReader.；Both iterate over lines and apply conditional logic to filter lines.
- 行为差异: Function A uses regular expressions to match HTML anchor tags and extract href and text; Function B uses simple string startsWith and split to parse lines with a specific format.；Function A extracts both links and texts (two vectors); Function B extracts only IP addresses (single vector).；Function A includes debug prints and timing; Function B has exception handling for MalformedURLException and IOException.；The output types differ: Vector[] vs Vector<String>.
- 修正建议: Incorporate control flow and data flow analysis to differentiate parsing logic (e.g., regex vs. string splitting).；Use more robust tokenization that captures the specific strings used in conditions (e.g., 'mailto:', '!SERVERS').；Include return type information to distinguish Vector[] from Vector<String>.

### case_id=4186 FP boilerplate_overlap

- 方法: `decodeFileToFile` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Decodes a Base64-encoded input file and writes the decoded bytes to an output file.
- B 摘要: Handles GUI action events to set application preferences such as external tool paths and UI settings.
- 静态失败原因: Static BERT/GraphCodeBERT may have been misled by overlapping boilerplate code (try-catch, null checks) and common API tokens (File, InputStream, etc.) despite low overall token Jaccard similarity (0.101).
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would not consider these clones because they perform entirely different tasks (file decoding vs. GUI event handling) with no shared specific functionality.
- 行为差异: Function A performs file I/O for Base64 decoding; Function B handles GUI events and preferences.；Function A has a simple control flow; Function B has multiple conditional branches for different commands.；Function A returns a boolean success flag; Function B is void and updates UI components.
- 修正建议: Enhance models to differentiate between core logic and boilerplate code.；Use dataflow or control-flow graphs to capture program semantics more accurately.；Train on tasks that emphasize functional similarity over syntactic patterns.

### case_id=4187 FN partial_functionality

- 方法: `modifyApplicationMessage` vs `copy`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Modifies a specific message in a locale-specific properties file, creating the file if necessary by copying from an English default.
- B 摘要: Copies the contents of one file to another using character streams.
- 静态失败原因: Static BERT/GraphCodeBERT may miss this due to low token overlap and focus on overall structure, failing to recognize the partial functional similarity of the file copy sub-task within A.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this as a clone because the file copy operation in A is functionally a subset of B's behavior, accepting Type-4 partial similarity where one function includes the core operation of the other.
- 共享行为: Both use FileReader and FileWriter to read and write file contents character by character.
- 行为差异: Function A also handles locale selection, property parsing, and conditionally creates target files.；Function B is a simple file copy without any modification or localization logic.
- 修正建议: Train with more examples of partial functionality clones (Type-4).；Incorporate control flow and data flow information to detect subroutines that match other functions.

### case_id=4188 FP partial_functionality

- 方法: `genCustRatingFileAndMovieIndexFile` vs `readData`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Reads binary movie rating records and generates an index file and a customer rating file.
- B 摘要: Parses configuration strings and a file to populate various hash sets and mappings for Tibetan character processing.
- 静态失败原因: The static model likely overfitted on surface patterns like file reading loops and error handling, ignoring the distinct higher-level semantics and data types. The truncation of code_b may also have hidden the major functional difference.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BigCloneBench emphasizes semantic equivalence; these functions serve entirely different purposes despite both involving file reading, so they are correctly labeled non-clones.
- 共享行为: Both perform file I/O operations；Both use loops and conditional logic；Both handle exceptions with try-catch
- 行为差异: Function A processes binary data and writes structured output files; Function B processes text tokens and builds in-memory data structures.；Function A deals with numeric (short, int, byte) data; Function B deals with strings and sets.；Function A's output is file-based; Function B's output is heap-based for later use.
- 修正建议: Incorporate data-flow and control-flow analysis to distinguish different I/O tasks.；Use function-level summarization to capture overall purpose beyond local patterns.；Leverage method names as semantic hints (e.g., 'genCustRatingFile' vs 'readData').

### case_id=4189 FP partial_functionality

- 方法: `readTwitterFead` vs `wordFrequency`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a Twitter timeline JSON from a hardcoded URL using HttpClient and returns the entire response as a string.
- B 摘要: Sends an HTTP GET request to a constructed URL, searches the first line matching a regex pattern to extract a word frequency integer, and returns that integer or 0.
- 静态失败原因: The static model likely focused on lexical and API overlap (BufferedReader, InputStreamReader, IOException, while loop) and the general pattern of making an HTTP request and reading lines, ignoring domain-specific logic like URL construction, pattern matching, and return type.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely labels this as non-clone because the overall functionality (reading Twitter feed vs word frequency count) is semantically different, despite shared HTTP I/O boilerplate. BCB prioritizes high-level semantic equivalence over low-level structural similarity.
- 共享行为: Both perform an HTTP GET request and read the response line by line with a BufferedReader；Both catch IOException and print stack traces
- 行为差异: A uses Apache HttpClient; B uses java.net.URL；A returns the concatenated lines as a string; B returns an integer extracted from a matching line；A uses a fixed URL; B constructs a dynamic URL；A handles ClientProtocolException; B handles MalformedURLException
- 修正建议: Incorporate dataflow analysis to track how data is processed (e.g., URL construction, pattern matching)；Learn higher-level semantics through function naming or more context；Use structure-aware models that differentiate between distinct API usage patterns

### case_id=4190 FN partial_functionality

- 方法: `main` vs `fetchUrl`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Constructs a POST request to RenRen API with specific parameters and prints the response.
- B 摘要: Fetches content from a given URL and returns it as a string.
- 静态失败原因: Static BERT or GraphCodeBERT might have been misled by the low token overlap and different method signatures, failing to capture the underlying URL reading structure. They may rely heavily on surface tokens and control flow, and the significant differences in parameter building and printing could overshadow the shared loop pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may classify these as clones because they share the core pattern of reading from a URL line by line and outputting the content (one prints, one returns). The broader Type-4 category often accepts functional similarity even with different input/output styles.
- 共享行为: Both open a URL connection and read lines from the input stream；Both handle IO operations (one throws, one catches)
- 行为差异: Function_a builds a complex set of parameters and uses POST method, while function_b uses GET via openStream()；Function_a prints output to console, function_b returns the content as a string；Function_a is a main method with hardcoded values, function_b is a utility that takes a URL parameter；Function_a includes exception throws, function_b catches exceptions and returns empty string
- 修正建议: Use dataflow analysis to identify core I/O operations across methods；Incorporate structural similarity beyond token overlap；Focus on the common substring of reading lines from URL, which is present in both

### case_id=4191 FP lexical_or_api_overlap

- 方法: `executePost` vs `checkForUpgrade`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Executes an HTTP POST request to a given URL with parameters and returns the response as a string.
- B 摘要: Checks for available software upgrades by querying a license server, parsing the response, updating a database table, and updating UI component visibility.
- 静态失败原因: The static BERT model likely overfocused on the overlapping API usage (HttpURLConnection, BufferedReader) and ignored the distinct overall logic, data flows, and method signatures.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clone because the functions have completely different high-level functionality despite sharing low-level HTTP connection boilerplate. BCB prioritizes semantic equivalence over structural similarity.
- 共享行为: Both open an HTTP connection to a URL；Both read from an InputStream using BufferedReader
- 行为差异: HTTP method: A uses POST, B uses GET (default)；Purpose: A is a generic POST utility, B is a specific upgrade checker；Return type: A returns String, B returns void；Side effects: B updates database and UI, A has no side effects
- 修正建议: Incorporate structural and dataflow information into the model；Use method-level features like return type, parameters, and external calls；Fine-tune on a dataset that emphasizes functional semantics over boilerplate

### case_id=4192 FP boilerplate_overlap

- 方法: `generateStackHashKey` vs `perform`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Generates a unique hash key by throwing an exception to capture the stack trace, computing its MD5 digest, and base64 encoding the result, with collision handling.
- B 摘要: Processes a web form submission to classify a concept by sending XML data to a remote URL via HTTP POST and parsing the response, managing session and reporting beans.
- 静态失败原因: The static model likely over-generalized from the presence of similar exception handling patterns and the use of classes like MessageDigest/MessageResources, mistaking coincidental API name similarities for semantic equivalence while ignoring the overall task difference.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would label these as non-clones because they have no meaningful functional overlap beyond generic Java boilerplate; their purposes and domain objects are entirely different.
- 共享行为: Both use try-catch blocks for exception handling.；Both involve string manipulation and encoding.
- 行为差异: A computes a hash from a stack trace; B performs network I/O and session management.；A is a static utility; B is an instance method in a Struts action controller.；A is self-contained; B interacts with external services and multiple beans.
- 修正建议: Incorporate data flow analysis to trace the purpose of key objects.；Use more robust long-range dependency modeling to avoid being misled by generic exception handling.；Include task-specific metadata (e.g., class context, method signatures) in the model input.

### case_id=4193 FN partial_functionality

- 方法: `readGeoParserResult` vs `importRoles`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads geo-parser results by sending an XML request over HTTP and parsing the response into a collection of place-name tuples with associated IDs, with retry logic.
- B 摘要: Imports roles by fetching XML from a URL and parsing it line by line to extract RoleName objects using ProfileParser.
- 静态失败原因: Static BERT/GraphCodeBERT relies on token overlap and surface patterns; the low Jaccard similarity (0.16) and different method names, variable names, and specific implementation details (e.g., retries, testing flag, different parsing loops) lead the model to classify them as non-clones, missing the underlying semantic similarity of fetching and parsing XML.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this as a clone because both functions perform the same high-level task: fetch XML from a remote service over HTTP and parse it to extract structured data. The differences in parsing details, retries, and return types are considered partial functionality similarity, which fits BCB's broad Type-4 definition.
- 共享行为: Both fetch XML data from a URL over HTTP.；Both parse the fetched XML to extract domain objects.；Both return a collection of parsed objects.；Both use similar boilerplate for URL connection and buffered reading.
- 行为差异: Function A dynamically builds the request XML with condition for Gazetteer IDs; B simply reads the URL content.；Function A includes retry logic (up to 3 attempts) and a testing mode; B has no retry.；Function A parses XML elements with iterators and specific conditions; B uses line-by-line parsing and a dedicated parser class.；Return types differ: A returns Set<Tuple>; B returns ArrayList<RoleName>.
- 修正建议: Incorporate data flow analysis to capture the common pattern of URL opening and XML parsing.；Use a code representation that abstracts away specific variable names and highlights API calls (URL, BufferedReader, XML parsing).；Add training examples where functions share similar I/O patterns but differ in internal logic.

### case_id=4194 FP boilerplate_overlap

- 方法: `readData` vs `unJarStart`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Initializes lookup sets and maps from string constants and file input for character encoding.
- B 摘要: Extracts files from a JAR archive whose entry names start with a given prefix.
- 静态失败原因: The model may have been misled by superficial structural similarities such as both having try-catch blocks, loops, and private method signature, despite the low token Jaccard similarity. It likely failed to capture the distinct API usage and domain-specific logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB focuses on functional similarity; these functions perform entirely different tasks, so they are not clones.
- 行为差异: Different input sources (string constants vs JAR file)；Different output (populate data structures vs write files)；Completely different domain logic (character encoding vs JAR extraction)
- 修正建议: Improve the model's ability to distinguish domain-specific API usage by incorporating AST or data flow features that capture the intent of operations.；Use contrastive learning to penalize pairs with low semantic similarity despite structural parallels.

### case_id=4195 FP lexical_or_api_overlap

- 方法: `read` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a skeleton file from the classpath, splits it into sections delimited by '---', and validates the number of sections.
- B 摘要: Performs a Google image search by constructing a URL, parsing HTML to extract image URLs, and updating a UI component.
- 静态失败原因: The model over-relied on shallow lexical and structural patterns common to many I/O routines (e.g., BufferedReader, URL, openStream, readLine loop, try-catch), leading to a false positive despite no semantic similarity.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels non-clone because the functions have completely different high-level purposes (file parsing vs. web scraping with UI update) and share only generic I/O boilerplate, which BCB typically does not consider sufficient for clone annotation.
- 共享行为: Both use BufferedReader to read text line by line from a stream.；Both open a URL connection and read from an InputStream.；Both handle exceptions with try-catch blocks.；Both build strings from read lines.
- 行为差异: Function A reads a local resource file; function B fetches data from an external web service.；Function A parses lines into sections based on a delimiter; function B parses HTML to extract image links.；Function A validates against an expected section count; function B updates a GUI component and handles UI state.；Function A throws exceptions; function B shows error dialogs.
- 修正建议: Incorporate data flow analysis to distinguish handling of different data sources and destinations.；Use control-flow graph comparison that abstracts away common boilerplate.；Train with hard negative examples that share lexical patterns but differ in functionality.；Add functional signature analysis (e.g., input/output types, side effects).

### case_id=4196 FP lexical_or_api_overlap

- 方法: `addQDInformation` vs `downloadModel`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads QD information from a local file or remote URL, parsing lines to update project info and dates.
- B 摘要: Downloads an RDF model from a URL and returns it as a Model object.
- 静态失败原因: The static BERT model likely overemphasized lexical and structural overlaps such as URL, InputStream, IOException, and try-catch blocks, while missing the fundamental semantic difference in functionality.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels as non-clone because the functions have completely different purposes (updating QD info vs. downloading a model) and only share boilerplate I/O code, which is insufficient for clone identification.
- 共享行为: Both use URL.openStream() to read from a URL；Both handle IOException and MalformedURLException；Both use InputStream and close it
- 行为差异: Function A reads and parses specific line formats (pg, pt) to update internal state; Function B reads an RDF model and returns it；Function A conditionally reads from a local file; Function B always reads from a URL；Function A modifies internal project info; Function B is static and returns a model；Function B sets HTTP request properties; Function A does not
- 修正建议: Incorporate data flow analysis to track how input/output are used；Add a token-type embedding to differentiate API calls from domain-specific logic；Use a model that captures higher-level semantic intent, like a graph-based code representation

### case_id=4197 FN benchmark_preference_bias

- 方法: `fileDownload` vs `handler`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `preference_memory_with_manual_audit`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a file from a URL and saves it to a local directory.
- B 摘要: Reads a webpage, extracts substrings between markers, and updates a map.
- 静态失败原因: The static BERT model likely focused on the low lexical overlap and different output behaviors, missing the broader functional similarity recognized by BCB's annotation guidelines.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider both as clones because they share the common functionality of fetching data from a URL using BufferedReader, a typical web scraping or downloading template. Despite differences in output processing, the core task of opening a URL and reading its content is similar enough to be considered Type-3 or Type-4 clone.
- 共享行为: Both open a URL and read its content using BufferedReader；Both handle IO exceptions
- 行为差异: A writes output to a file; B modifies a map；A reads character by character; B reads lines and performs string parsing；A captures entire content; B selectively extracts based on conditions；Different exception handling styles (one logs, one empty catch)
- 修正建议: Incorporate more robust semantic understanding of sub-tasks like URL fetching；Use data augmentation with pairs sharing common sub-behaviors but differing in final output；Train with BCB-style annotations to align with their preferences

### case_id=4198 FN benchmark_preference_bias

- 方法: `bootKernel` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Loads a kernel configuration from Android assets, copies sdcard assets to external storage, and boots a kernel.
- B 摘要: Builds a site for editing by applying XSLT transformations to XML files, handling containers and menus, and writing output files.
- 静态失败原因: The static BERT model correctly identified this as a non-clone due to low token overlap, different method names, and distinct overall structure. It did not fail; the BCB label is likely an annotation error.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as a clone due to superficial similarities in file I/O patterns, use of Properties, and exception handling, despite completely different domain and purpose. The annotation might reflect a broad Type-4 (semantic) clone interpretation, but the core functionality is unrelated.
- 共享行为: Both perform file I/O operations (reading from assets or files, writing to files).；Both use Properties objects for configuration.；Both have loops processing multiple items (sdcard files or pages).
- 行为差异: Function A is about booting a kernel; function B is about generating HTML pages for a CMS.；Function A copies binary files via FileChannels; function B transforms XML using XSLT.；Function A uses Android-specific classes like AssetManager; function B uses DOM and XSLT APIs.；Function B has extensive string manipulation and logging; function A has simpler logging.
- 修正建议: Re-examine BCB annotation for this pair; consider it a non-clone.；If BCB intends broad Type-4 similarity, define clearer criteria to avoid false positives.；Improve training data to exclude such dissimilar pairs from clone labels.

### case_id=4199 FN partial_functionality

- 方法: `getFile` vs `copyFileTo`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, parses it to modify an endpoint attribute, and saves it to a temporary file, returning the file path.
- B 摘要: Copies the current file (by absolute path) to a given destination file using FileChannels.
- 静态失败原因: Static models like BERT rely on lexical and structural features; the low token Jaccard (0.09), different method names, and distinct control flow likely caused the model to predict non-clone, missing the partial semantic overlap of the data transfer operation.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled this as a clone due to the shared use of FileChannel.transferFrom for data transfer, which is a distinctive API pattern that could be considered Type-4 structural similarity, even though the overall functionalities are different.
- 共享行为: Both use FileChannel.transferFrom to transfer data between channels；Both involve file input/output operations
- 行为差异: A downloads from a URL; B copies from a local file；A performs XML parsing and modification; B does not；A has conditional download logic and multiple exception handling; B only handles IOException；A returns a file location string; B is void
- 修正建议: Incorporate API call sequence alignment to detect shared sub-operations；Use graph-based models (e.g., GNN) that capture data flow and channel usage patterns；Add training data with diverse implementations of core data transfer patterns

### case_id=4200 FN benchmark_preference_bias

- 方法: `main` vs `handledRun`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Sends a hardcoded API request to RenRen social network to publish a templatized action feed, prints the response.
- B 摘要: Downloads game data XML from a URL, checks version, and updates a local file if a newer version exists, handling network and other exceptions.
- 静态失败原因: The static model relies on lexical and syntactic overlap, which is minimal (token Jaccard 0.102). It fails to recognize the high-level functional similarity in network I/O patterns that BCB considers clone-worthy. The model likely focuses on method names and parameter details, which are completely different.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have annotated this pair as a clone because both functions share a common boilerplate structure for network resource access: opening a URL, reading lines, and processing. Under a broad Type-3/Type-4 interpretation, such I/O patterns are considered semantically similar, even though the domain-specific logic differs.
- 共享行为: Both perform network I/O using URL and BufferedReader to read data.；Both handle exceptions (though A throws IOException, B catches various exceptions).；Both involve reading lines of text from a URL stream.
- 行为差异: A sends a POST request with many parameters; B sends a GET request without parameters.；A prints response to console; B writes to a file and updates a game database.；A is a simple standalone script; B includes version checking and conditional file update.；A uses HttpURLConnection; B uses url.openStream() directly.
- 修正建议: Incorporate graph-based representations that capture control flow and data flow related to network I/O.；Use domain adaptation to learn broader functional categories like 'network fetch' or 'URL reading'.；Adjust training labels to better reflect BCB's annotation preferences for Type-4 clones based on functional purpose rather than implementation details.

### case_id=4201 FN partial_functionality

- 方法: `downloadURLtoString` vs `read`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a URL's content to a string by reading lines.
- B 摘要: Reads from a file or URL, sets status, and delegates reading to another method.
- 静态失败原因: Static BERT models rely heavily on token and surface-level features. The low Jaccard similarity (0.19) and differing return types, control flow, and error handling likely caused the model to miss the underlying URL-reading commonality.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels functionally similar code as clones even if signatures differ. Both functions perform URL reading, which is a core shared functionality, so BCB considers them clones under broad Type-3/Type-4 criteria.
- 共享行为: Both open a URL and read from it.；Both handle IOException (one throws, one catches).；Both use InputStream-based reading.
- 行为差异: A returns the content as a String; B returns an int status.；A only handles URL; B also handles local file paths.；A reads line-by-line using BufferedReader; B uses BufferedInputStream.；A explicitly closes the stream; B does not.
- 修正建议: Incorporate dataflow or program dependence analysis to identify core operations like URL opening.；Use functional similarity measures that abstract over I/O source types and return types.；Consider fusing AST paths that emphasize stream/reader operations.

### case_id=4202 FP lexical_or_api_overlap

- 方法: `handleHandshake` vs `CheckUrl`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Handles Minecraft server handshake by validating username and performing session server authentication via HTTP request to session.minecraft.net.
- B 摘要: Reads the first line from a given URL using an HTTP connection and returns it as a string.
- 静态失败原因: Static BERT models may overemphasize lexical and API-level similarities (e.g., URL, BufferedReader, readLine, try-catch) while missing the structural and semantic differences in the overall control flow and external dependencies, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the overall functionality and purpose are completely different; the shared URL-reading pattern is too generic and context-dependent to indicate clone-level similarity.
- 共享行为: Both open a URL and create a BufferedReader to read input.；Both use a try-catch block and print stack traces on exceptions.；Both call readLine() on a BufferedReader.
- 行为差异: Function A performs complex authentication logic with multiple conditions and network shutdown; Function B simply returns the first line.；Function A uses an external parameter Packet2Handshake and interacts with Minecraft session; Function B is a static utility with no side effects.；Function A has specific checks for username validity; Function B does not validate the URL content beyond reading.；Function A may send additional packets via addToSendQueue; Function B has no output beyond the returned string.
- 修正建议: Incorporate dataflow and control-flow analysis to distinguish different high-level purposes.；Use graph-based models like GraphCodeBERT or code property graphs that capture variable dependencies and function context.；Consider adding a global program representation that includes method signatures and class context.

### case_id=4203 FN partial_functionality

- 方法: `doTransfer` vs `getEncoding`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: forwards an HTTP request and response to a target URL, acting as a proxy by copying headers and streaming data.
- B 摘要: extracts the character encoding from an HTTP response by checking headers or parsing the response content.
- 静态失败原因: Static BERT/GraphCodeBERT models rely on token overlap and graph structure, which are low here (Jaccard 0.119) due to different method names and operations. They miss the high-level conceptual similarity of HTTP connection handling because the specific API calls and workflow differ significantly.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled these as clones because both methods are involved in HTTP communication, reading headers and streams, and could be considered broadly similar as 'URL connection handling' or 'HTTP header processing' utilities within the same project.
- 共享行为: Both open a URLConnection to communicate over HTTP；Both read HTTP headers from the connection；Both read from an input stream
- 行为差异: doTransfer handles full request/response proxying with multiple streams and writing to output streams, while getEncoding only reads headers and body to find encoding；doTransfer uses HttpURLConnection and sets request method, whereas getEncoding uses URLConnection and does not modify request；doTransfer has extensive error handling for MalformedURLException and IOException, while getEncoding has try-finally for stream cleanup
- 修正建议: Use a more semantic-aware model that captures high-level intent or domain context；Incorporate method-level documentation or comments to provide semantic cues；Augment with data-flow or control-flow analysis to identify common patterns in HTTP handling

### case_id=4204 FN partial_functionality

- 方法: `getHTML` vs `createHTML`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.5`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches HTML from a URL via HTTP and optionally writes it to a file.
- B 摘要: Builds an HTML page from a CSS resource and database content based on a request page type.
- 静态失败原因: Low token Jaccard (0.138) and lack of overlapping vocabulary/API calls misled the model into thinking they are unrelated.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both functions as producing HTML, thus accepting broad Type-4 similarity despite different implementations.
- 共享行为: Both return an HTML string；Both use BufferedReader and InputStreamReader for reading；Both handle exceptions and close resources
- 行为差异: getHTML retrieves from external URL; createHTML generates from internal resources and DB；getHTML has optional file writing; createHTML has conditional logic based on requestPage enum；getHTML uses HttpURLConnection; createHTML uses ClassLoader.getResource and JDBC
- 修正建议: Use a model that captures high-level intent or output type；Incorporate dataflow analysis to identify shared data format (HTML)；Augment training with examples of Type-4 clones with low lexical overlap

### case_id=4205 FN partial_functionality

- 方法: `writeConfiguration` vs `doGet`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Writes configuration resource content to a Writer, handling null resource.
- B 摘要: Handles HTTP GET request, loads a page, checks permissions, logs, caches, and writes page output to response.
- 静态失败原因: Static BERT models rely heavily on token overlap, which is very low; they miss the tiny semantic overlap of writing output.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider the commonality of writing output as sufficient for a Type-4 clone, though functionality is largely different.
- 共享行为: Both write output to a Writer/response stream
- 行为差异: Different inputs and output targets (resource vs HTTP response)；Different error handling and logic complexity；Presence of security and caching in doGet
- 修正建议: Incorporate data-flow analysis to capture output operations；Use method-level summarization to compare high-level intent

### case_id=4206 FN partial_functionality

- 方法: `runScript` vs `importRoles`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a script from a URL and returns its content as a string.
- B 摘要: Downloads an XML file from a URL, parses role names, and returns a list.
- 静态失败原因: Static BERT methods rely heavily on token overlap and method signatures; the low Jaccard similarity (0.23) and different method names caused it to miss the structural similarity in URL reading and data accumulation.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label these as clones because both functions perform network I/O from a URL, read data, and process it into a result. The high-level structure (open stream, read loop, build result) is similar, and the difference in output type is considered acceptable under Type-4 (functionally similar) clone criteria.
- 共享行为: Open a connection to a URL；Read data from the input stream；Build a result from the read data；Return the result
- 行为差异: A reads raw bytes; B reads lines；A concatenates characters to a string; B parses XML to create objects；A returns a String; B returns an ArrayList<RoleName>；A catches generic Exception; B catches specific exceptions including ParsingException
- 修正建议: Incorporate data-flow analysis to identify common I/O patterns；Use AST-based matching that abstract over type specifics；Consider control-flow structure similarity beyond token overlap

### case_id=4207 FP boilerplate_overlap

- 方法: `get` vs `doVersionCheck`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches game records from a remote server via HTTP GET with location and count headers, parsing lines into GameRecord objects.
- B 摘要: Checks for software version updates by reading a remote version file, extracting build numbers, and triggering an update check.
- 静态失败原因: Static BERT models may over-rely on lexical overlap and structural patterns, such as the common URL opening and line reading boilerplate, ignoring semantic differences in headers, parsing logic, and return types.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the overall functionality is entirely different: one is about fetching game data, the other about version checking. Despite similar boilerplate, the core logic and outputs diverge significantly.
- 共享行为: Both open URL connections and read lines using BufferedReader.；Both use startsWith to filter lines.；Both handle IOException.
- 行为差异: A uses custom HTTP headers for game location and count; B does not.；A parses lines into GameRecord objects; B extracts version strings.；A returns an array of GameRecord or null; B is void and shows/hides a wait cursor.；A includes error output to stdout; B shows error dialog via GUIUtilities.
- 修正建议: Incorporate method signature and return type analysis.；Use dataflow analysis to distinguish building a list of GameRecord vs extracting version strings.；Add training examples that contrast similar boilerplate with different semantics.

### case_id=4208 FN boilerplate_overlap

- 方法: `getEncoding` vs `issueCommandToServer`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Extracts character encoding from HTTP response headers or body.
- B 摘要: Sends a command with a serialized capsule to a server and returns the response.
- 静态失败原因: High lexical overlap in API usage (URLConnection, BufferedReader, readLine) and IO patterns misled the model to ignore the different intents.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may consider them clones due to shared boilerplate (URLConnection, BufferedReader) and both being I/O functions, but the core functionality differs significantly.
- 共享行为: Open a URL connection and handle IO；Use BufferedReader to read line-by-line；Work with InputStream
- 行为差异: Function A reads headers and body for charset; Function B writes to output stream and reads response；Function A returns encoding string; Function B returns full response string；Different purpose: encoding detection vs. command execution
- 修正建议: Incorporate dataflow analysis to distinguish read-only vs. read-write operations；Add structural embeddings that capture functional purpose beyond API tokens

### case_id=4209 FP partial_functionality

- 方法: `actionPerformed` vs `Converter`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Handles action commands to set file paths for Graphviz and ImageMagick and configure various application preferences.
- B 摘要: Reads a file with SJIS encoding and writes it with UTF-8 encoding.
- 静态失败原因: The model likely overemphasized the presence of file-related APIs (e.g., File) and ignored the vastly different control flow and purpose, leading to a false positive.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB labels this as non-clone because the functions have entirely different purposes and logic; even Type-4 clones require partial functional similarity.
- 共享行为: Both involve file operations；Both use File class
- 行为差异: Function A is an event handler with many conditional branches; B is a simple file conversion constructor；A uses GUI components (JFileChooser, JTextField); B uses I/O streams (FileInputStream, FileOutputStream)；A modifies application preferences; B performs encoding conversion；A relies on custom classes (Suku.kontroller); B is self-contained
- 修正建议: Enhance training data with diverse non-clone pairs that share superficial lexical similarities；Incorporate high-level semantic information such as method purpose or class context；Use graph-based representations that capture data flow and control dependencies

### case_id=4210 FN partial_functionality

- 方法: `getFile` vs `copy`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies the SOAP address endpoint, and returns the file path.
- B 摘要: Copies data from an InputStream to an OutputStream using IOUtils.copyLarge, with error handling and stream closing.
- 静态失败原因: Static BERT/GraphCodeBERT models often rely on token overlap and syntactic patterns; the extremely low Jaccard similarity (0.076) and lack of common API calls or structural similarity likely caused the model to miss this pair. Additionally, the model may not capture the high-level semantic similarity of stream copying.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB might consider both as involving stream copying from source to sink, a common partial functionality, and thus label them as Type-4 semantic clones, despite significant differences in complexity and purpose.
- 共享行为: Both perform I/O operations with input and output streams；Both handle exceptions and log errors；Both close streams after use
- 行为差异: Function A involves file existence check, XML parsing, and attribute modification; Function B only copies bytes；Function A uses NIO channels and URLConnection; Function B uses Apache Commons IO IOUtils；Function A returns a file path; Function B returns the number of bytes copied；Function A has complex control flow and multiple catch blocks; Function B has simple try-catch-finally
- 修正建议: Enhance model with data flow analysis to identify common I/O patterns；Incorporate hierarchical semantic embeddings that recognize abstract operations like 'copy stream'；Use a larger context or project-level information to detect clone pairs with low token overlap but shared intent

### case_id=4211 FP lexical_or_api_overlap

- 方法: `startScript` vs `loadURL`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a script from a URL and appends it to a dialog's script buffer, exiting on error.
- B 摘要: Downloads a URL's content to a temporary file with optional HTTP Basic Authentication and updates a status label with download progress.
- 静态失败原因: The model likely focused on the similar control flow (BufferedReader + while loop) and lexical overlap (url, readLine, etc.) but missed the distinct semantic contexts and differences in I/O and error handling.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely marked these as non-clones because they have different side effects, input/output structures, and error handling, despite sharing a common pattern of reading from a URL.
- 共享行为: Both open a URL (or URLConnection) and read lines using BufferedReader.
- 行为差异: Different inputs: A takes an Attributes object with URL; B takes URL, username, password, and JLabel.；Different outputs: A appends lines to a dialog script string; B writes lines to a temporary file.；Authentication: A does not handle authentication; B includes Basic Authentication.；UI update: A none; B updates a status label with file size.
- 修正建议: Enhance training data with pairs that have similar code structure but different functionalities.；Incorporate dataflow analysis to track state changes and side effects.；Use representation learning that captures high-level intent, such as method names and surrounding context.

### case_id=4212 FP lexical_or_api_overlap

- 方法: `sendPost` vs `retrieveQ`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Sends HTTP POST request with parameter and returns response body as concatenated string.
- B 摘要: Retrieves content from a URL (likely HTTP GET) and returns response body with newlines preserved.
- 静态失败原因: High lexical overlap (URL, HttpURLConnection, BufferedReader, etc.) and similar structural pattern likely misled the model to ignore the crucial difference in writing vs no-write data.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically requires functional equivalence or near equivalence for Type-1/2/3 clones. These functions differ in HTTP method and data flow, so they are not considered clones.
- 共享行为: Open URL connection；Read response line by line；Build and return response string；Use BufferedReader and InputStreamReader
- 行为差异: Function A writes parameter data (POST), Function B only reads (GET)；Function A sets request properties (Accept-Language), Function B does not；Function A catches exceptions and prints message, Function B throws them；Function A concatenates lines without newline, Function B adds newlines between lines
- 修正建议: Incorporate data flow analysis to detect whether data is written to the connection；Use contrastive examples of POST vs GET patterns during training；Add attention to method signatures and exception handling differences

### case_id=4213 FP boilerplate_overlap

- 方法: `getVersion` vs `doVersionCheck`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches a version string from a hardcoded URL and returns it, logging a debug message.
- B 摘要: Reads a version check file from a configurable URL, extracts build numbers, and initiates a version check with UI feedback.
- 静态失败原因: The model likely over-relied on lexical overlap of common I/O boilerplate (URL, BufferedReader, readLine) and the keyword 'version' in method names, missing the significant differences in control flow, side effects, and purpose.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB treats non-clones when functions have different overall purpose and side effects, despite overlapping I/O patterns. Here, one is a simple data retrieval and the other is a UI-driven version check, so BCB correctly labels non-clone.
- 共享行为: Both read from a URL using similar Java I/O pattern (URL, BufferedReader, readLine).；Both handle exceptions (catch block).
- 行为差异: A returns a string; B is void with UI side effects (show/hide cursor, error dialog).；A uses a hardcoded URL; B uses a configurable property.；A does not parse lines beyond reading; B parses lines for specific build prefixes.；A returns null on error; B shows an error dialog and does not return a value.
- 修正建议: Use a model that captures control flow and data dependencies, not just token overlap.；Incorporate functional semantics via documentation or graph-based representations.；Train on a dataset that penalizes boilerplate similarity more heavily.

### case_id=4214 FN boilerplate_overlap

- 方法: `testNetworkHTTP` vs `getNetworkServersIPs`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Function A performs multiple HTTP GET requests to various URLs, reads all response lines without processing, and disconnects, effectively testing network connectivity.
- B 摘要: Function B connects to a given URL, reads lines, and extracts IP addresses from lines following a '!SERVERS' header, returning them in a vector.
- 静态失败原因: The model likely overfocused on the different purposes (test vs. parse-and-return) and low token overlap (0.267), missing the shared structural pattern of HTTP connection and line reading that BCB considers clone-worthy.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may label them as clones because they share the fundamental pattern of opening a URL, getting an input stream, and reading lines with a BufferedReader. This common boilerplate is considered sufficient for Type-3/4 similarity in BCB, despite different specific logic.
- 共享行为: Both open an HTTP URL connection and read lines from the input stream using BufferedReader.
- 行为差异: Function A makes multiple separate connections to different URLs and does not return a value; Function B makes one connection, parses lines with specific conditions, and returns a Vector of IPs.
- 修正建议: Incorporate dataflow analysis to recognize common network access patterns.；Add training examples that specifically highlight partial functionality overlap with different side effects.

### case_id=4215 FN partial_functionality

- 方法: `readAndRewrite` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a DICOM image file and rewrites it to another file using DICOM libraries.
- B 摘要: Retrieves a resource by URL, caches it locally, and returns an InputStream to the cached file.
- 静态失败原因: Static BERT models rely on token and AST similarity. The token overlap is very low, and the code structures differ significantly. The model correctly rejected the pair as non-clones based on lack of similarity, but the BCB label considered them clones under a broader functional similarity, so the model produced a false negative according to BCB.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label these as clones under a very broad Type-4 interpretation, as both perform I/O operations: reading from a source and writing to a destination. The annotator might have considered the high-level functionality of 'read from input and write to output' as functionally similar.
- 共享行为: Both open input and output streams；Both perform some data reading and writing；Both use System.out.println for status messages
- 行为差异: A uses DICOM-specific parsers and writers; B uses generic URL connection and byte copying；A reads and writes in a block using PixelDataReader/Writer; B reads byte by byte；A does not handle caching; B implements caching logic with cacheHashtable；A writes to a specified outFile; B caches to a file in cacheDir and returns InputStream
- 修正建议: Improve model's ability to recognize high-level functional similarity beyond lexical and AST overlap；Use dataflow or dependency analysis to detect that both involve input/output streams；Incorporate knowledge of common I/O patterns

### case_id=4216 FP boilerplate_overlap

- 方法: `main` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.99`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Main method that copies files from a source directory to targets using FileChannel, deletes source files optionally with SVN support, and exits.
- B 摘要: ActionPerformed method that handles various GUI commands like setting Graphviz/ImageMagick paths, updating UI preferences, and restarting the application.
- 静态失败原因: The model likely overfitted to common structural patterns like loops, conditionals, and try-catch blocks, ignoring the semantic difference in the task domain (file system copy vs GUI event handling).
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clones because the functions have entirely different purposes and no shared functionality beyond basic Java structures.
- 共享行为: Both use file operations (A: file copy/delete; B: file chooser for executables)；Both have loops (A: for each source/target; B: for each LAF entry)；Both have try-catch blocks for exception handling
- 行为差异: A is a static main entry point; B is an instance method for event handling；A copies file content and deletes files; B opens file chooser dialogs and saves preferences；A uses FileChannel for direct transfer; B uses Swing components for GUI；A has SVN integration and system exit; B has UI updates and restart dialogs
- 修正建议: Enhance training with more diverse negative examples that share boilerplate but differ in domain；Incorporate intra-method dataflow or API usage patterns to distinguish file I/O from GUI operations；Use hierarchical representations to separate control flow from domain-specific operations

### case_id=4217 FP boilerplate_overlap

- 方法: `readRemoteFile` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a remote file from a fixed URL line by line and returns the concatenated content as a single string.
- B 摘要: Performs a Google image search by constructing a query URL, reading the HTML response, extracting image URLs, and adding them to a list.
- 静态失败原因: Static BERT/GraphCodeBERT focused on structural similarities like URL opening and line-by-line reading pattern, but ignored the distinct purposes and output transformations, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the core functionality differs significantly (file reading vs web scraping with parsing). The shared URL reading boilerplate is not sufficient for Type-3/4 clone categorization.
- 共享行为: Both open a URL connection and read input stream line by line using BufferedReader and InputStreamReader.
- 行为差异: A returns the concatenated file content; B extracts and stores image URLs from HTML.；B has condition checking for artist comparison and query construction; A does not.；B catches exceptions broadly; A catches specific EOFException and IOException.；A reads from a fixed remoteFile; B constructs dynamic query.
- 修正建议: Incorporate dataflow analysis to capture how the read data is processed.；Use abstract syntax tree matching to differentiate between concatenation of raw lines vs parsing for specific patterns.；Train on more diverse examples of web scraping vs file reading to avoid boilerplate confusion.

### case_id=4218 FN partial_functionality

- 方法: `getWebPage` vs `File2String`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a webpage from a URL and returns its content as a string, throwing an Error on failure.
- B 摘要: Reads a file from filesystem or classpath and returns its content as a string, exiting on failure.
- 静态失败原因: Static BERT models rely on lexical overlap and structural patterns; low token Jaccard (0.17) and differences in I/O handling cause underprediction, missing the abstract common behavior.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB values functional similarity in reading a textual resource and returning its content, even if the source and error handling differ; this pair is a typical Type-4 clone.
- 共享行为: Reads text input line by line；Concatenates lines into a single string；Returns the concatenated string
- 行为差异: Input source differs (URL vs file/resource)；Error handling differs (throw Error vs print and exit)；B includes debug prints and system exit on failure
- 修正建议: Use dataflow-aware models like GraphCodeBERT with dataflow edges；Train on more semantic clone pairs with low lexical overlap；Incorporate I/O operation abstraction

### case_id=4219 FP lexical_or_api_overlap

- 方法: `issueCommandToServer` vs `downloadModel`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Sends a command to a server via HTTP POST with URL-encoded parameters and returns the response as a string.
- B 摘要: Downloads an RDF model from a given URL via HTTP GET, handling content negotiation and returning a Model object.
- 静态失败原因: Static BERT may have been misled by the lexical overlap of common API calls (URLConnection, setRequestProperty, getInputStream, close) and similar structure of reading from a URL, failing to capture the distinct semantic intents.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the overall functionality (command dispatch vs. model download) is different, despite sharing a similar boilerplate pattern of opening a URL connection and reading input.
- 共享行为: Both use URLConnection to open HTTP connections；Both set request properties；Both get an InputStream and read data；Both close streams
- 行为差异: Function A uses POST, Function B uses GET；Function A sends command parameters, Function B only reads；Function A returns a String, Function B returns a Model；Function B has error handling with try-catch and logging, Function A throws IOException
- 修正建议: Focus on functional purpose rather than syntactic patterns；Incorporate data flow analysis to distinguish input/output types；Use semantic similarity that considers method names and overall goal

### case_id=4220 FP lexical_or_api_overlap

- 方法: `main` vs `decodeFileToFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Generates adapter classes from a Prolog file and outputs a JAR with adapter layer and lookup classes.
- B 摘要: Decodes a Base64 encoded file into an output file using Base64 input stream.
- 静态失败原因: The static BERT model likely predicted a clone due to lexical and API overlap: both functions contain common I/O boilerplate (FileInputStream, FileOutputStream, buffer reading, IOException handling, printStackTrace). The model may have focused on these surface-level similarities while ignoring the core semantic differences.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels this as non-clone because even under broad Type-4 criteria, the functions lack functional similarity. They perform entirely different tasks (adapter generation vs. Base64 decoding).
- 共享行为: Both perform file I/O operations (reading input file, writing output file).；Both use try-catch blocks to handle IOException and print stack traces.；Both use while loops to read from an input stream into a buffer and write to an output stream.
- 行为差异: Function A is a complex main method for adapter generation with multiple steps (parsing, visitor, class writing), while Function B is a simple Base64 decode utility.；Function A writes a JAR file and multiple resources, Function B writes a single decoded file.；Function A uses specific libraries (Prolog parser, ASM, etc.), Function B uses Base64 and standard I/O.；The overall purpose and output are completely different.
- 修正建议: Train the model to recognize that shared I/O patterns do not imply semantic equivalence.；Incorporate control flow and data flow analysis to capture the actual computation logic.；Add more negative examples where functions have similar API usage but different goals.

### case_id=4221 FP boilerplate_overlap

- 方法: `getPagina` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches the entire content of a given URL as a string, with authentication.
- B 摘要: Performs a Google Images search, parses HTML to extract image URLs, updates UI with the first image.
- 静态失败原因: The model likely overemphasized the common boilerplate pattern of opening a URL and reading lines, ignoring the distinct post-processing steps and method signatures.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB considers overall functional similarity; these functions have different purposes despite sharing boilerplate URL reading, so they are not clones.
- 共享行为: Both open a URL and read its content line by line using BufferedReader.；Both use try-catch for exception handling.
- 行为差异: A returns raw page content; B extracts image URLs from HTML.；B sets a custom User-Agent header and uses HttpURLConnection.；B interacts with global state (googleImages list) and UI components (MusicBoxView).；B has additional logic for handling spaces in the query and splitting response.
- 修正建议: Incorporate dataflow analysis to differentiate output usage.；Use semantic role labeling to capture task-specific operations after reading.；Increase weight on method signature differences (static void vs String return).

### case_id=4222 FP boilerplate_overlap

- 方法: `doRawRequest` vs `getVersion`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Sends an HTTP POST request with the given postData and returns the response body as a string.
- B 摘要: Fetches a version string from a remote URL via an HTTP GET request and returns it.
- 静态失败原因: The high token overlap in common HTTP boilerplate (URL, URLConnection, BufferedReader, InputStreamReader, readLine, close, return) misled the model into predicting a clone, ignoring the structural and functional differences.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels non-clones when method names and parameters differ significantly, and the core functionality (POST vs GET) is distinct despite boilerplate similarity.
- 共享行为: Both open a URL connection to a remote endpoint.；Both read the input stream line by line using BufferedReader.；Both close the reader and return a string.
- 行为差异: doRawRequest writes postData to the output stream (POST), getVersion does not (GET).；doRawRequest concatenates all lines of the response, getVersion only returns the last line read.；doRawRequest throws IOException, getVersion catches Exception and returns null on failure.；doRawRequest explicitly closes OutputStreamWriter, getVersion has no output stream.
- 修正建议: Incorporate method name and parameter information with higher weight.；Use dataflow analysis to detect write-to-output-stream before read.；Distinguish between HTTP methods (POST vs GET) by checking for OutputStream usage.

### case_id=4223 FP lexical_or_api_overlap

- 方法: `loadURL` vs `getFullScreenUrl`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Loads a URL with optional authentication, reads content, writes to a temporary file, and updates a status label with file size.
- B 摘要: Fetches a YouTube page, parses it to extract a fullscreen video URL, and returns it.
- 静态失败原因: Static BERT models may over-rely on lexical and API overlaps (URL.openConnection, BufferedReader, while loop) and ignore the overall semantic goal, leading to false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled it as not clone because the functions have distinct high-level purposes (generic file download vs. specific YouTube URL extraction), even though they share some low-level API usage patterns.
- 共享行为: Both open a URL connection；Both read lines from an input stream；Both process the read data
- 行为差异: Authentication handling: optional in A, absent in B；Output: A writes to a file, B returns a string；Parsing logic: A writes all lines to file, B searches for a specific line；Progress indication: A updates a status label, B uses a progress bar
- 修正建议: Incorporate data flow analysis to track how the read data is used；Use method signature and return type as additional context；Train on higher-level semantic representations (e.g., program purpose classification)

### case_id=4224 FP lexical_or_api_overlap

- 方法: `writeFileType` vs `readUNI`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a file of URIs, connects to each URL, checks for ontology keywords (OWL, RDFS, RDF) in the first 100 lines, and writes a classification to an output file.
- B 摘要: Reads a tab-separated file from a URL, skips header, parses each line to extract an ID and description, and adds them to a vector.
- 静态失败原因: The static model likely overemphasized shared lexical patterns (URL, BufferedReader/Scanner, try-catch) and structural similarities (line reading loops) while missing the fundamental difference in data flow and output semantics.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels based on functional similarity; despite overlapping use of URL and I/O, the tasks are distinct and share no substantial functional equivalence, so non-clone is appropriate.
- 共享行为: Both open a URL and read line-by-line from an input stream；Both handle exceptions with try-catch blocks
- 行为差异: Different purposes: A classifies URIs by ontology presence; B parses tab-separated data；Different outputs: A writes to a file; B populates a vector；Different input formats: A reads a file of URIs; B reads a tab-separated file from a URL；Different parsing logic: A checks for substring occurrences; B splits by tabs and extracts specific columns
- 修正建议: Incorporate data-flow analysis to capture the purpose and transformation of data；Train on more diverse non-clone pairs with similar I/O but different logic；Use graph-based representations to differentiate control flow and data dependencies

### case_id=4225 FN dataflow_blindspot

- 方法: `copyResource` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `dynamic_equivalence_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Copies a resource (from URL or local file) to a destination file, reading byte by byte, without buffering or error handling.
- B 摘要: Copies a local file to another file using a buffered stream, with try-catch-finally for error handling and resource cleanup, returning success status.
- 静态失败原因: Static models rely heavily on token overlap and syntactic similarity; these functions have low Jaccard similarity (0.2459) due to different structures (while vs for, different method names, exception handling). The model likely failed to capture the high-level semantic pattern of copying data between streams.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行价值高：该样本可能是 API 写法不同但行为等价的漏报。建议测试目标为 input_output_equivalence。
- BCB 偏好解释: BCB often labels such pairs as clones because both implement file copying, which is a core common behavior. The differences in source flexibility, buffering, and error handling are considered acceptable variations under Type-3/4 similarity.
- 共享行为: Both read from a source and write to a destination file.；Both use InputStream and OutputStream for byte-level copying.；Both close streams after copying.
- 行为差异: Source: A can read from URL or file; B only from File.；I/O pattern: A reads single bytes; B uses a buffer.；Error handling: A throws Exception; B catches IOException and returns boolean.；Resource management: A uses simple close; B uses try-finally.
- 修正建议: Enhance training or inference with dataflow analysis to recognize I/O operations like reading/writing streams.；Incorporate functional signatures or abstract representations of common utilities (e.g., copy operations).；Use contrastive learning on pairs that share abstract behavior but differ syntactically.

### case_id=4226 FP boilerplate_overlap

- 方法: `getUser` vs `doVersionCheck`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Loads a user from a database or a config file, falling back to reading a user configuration file from a resource URL.
- B 摘要: Checks for software version updates by reading a version-check URL and parsing build numbers.
- 静态失败原因: Static BERT likely relied on surface-level lexical and API similarities (URL, BufferedReader, line reading) and ignored the distinct business logic and data flow.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clones (Type-1/2/3/4) only if functions have significant functional overlap; these two are completely unrelated.
- 共享行为: Both open a URL and read lines using BufferedReader
- 行为差异: Function A retrieves or constructs a User object; Function B checks version strings and invokes another method；Function A has database interaction (UserDAO); Function B has no database；Function A returns a User; Function B is void and shows version check dialog
- 修正建议: Enhance model with semantics-aware training (e.g., contrastive learning on program dependence graphs)；Incorporate data flow and variable usage patterns to distinguish boilerplate from core logic

### case_id=4227 FN partial_functionality

- 方法: `getFile` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, optionally modifies the endpoint in the XML, and saves it to a temporary location.
- B 摘要: Copies all files from a source directory to a destination directory using FileChannel.
- 静态失败原因: Static BERT models rely on token-level similarity and structural patterns. The token Jaccard is low, so lexical overlap is minimal. The methods have different signatures and control flow, making it hard for static models to capture the high-level semantic similarity that BCB uses.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as examples of file transfer utilities using Java NIO FileChannel, thus functionally similar at a high level (Type-4).
- 共享行为: Both use FileChannel to transfer data between a source and a file output stream.
- 行为差异: A involves URL connection, XML parsing, and modification; B is a straightforward file copy.；A handles exceptions and throws AxisFault; B catches IOException silently.；A checks for existing file; B does not.
- 修正建议: Use dynamic analysis or dataflow analysis to understand the actual data flow.；Incorporate functional decomposition to capture shared high-level behavior despite different details.

### case_id=4228 FN boilerplate_overlap

- 方法: `createHTML` vs `read`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Generates an HTML page by reading CSS from a resource and optionally querying a database.
- B 摘要: Reads data from a file or URL stream and returns a status code.
- 静态失败原因: Static BERT/GraphCodeBERT relies heavily on token overlap and syntactic similarity; low token Jaccard and different method names/return types led to a non-clone prediction, missing the structural I/O pattern similarity.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely labels these as Type-3 clones due to the shared I/O stream reading pattern (URL.openStream, BufferedReader/BufferedInputStream, try-catch IOException) despite differing high-level functionality.
- 共享行为: Both open an input stream from a URL or file；Both handle IOException；Both use BufferedReader/BufferedInputStream to read data
- 行为差异: A builds an HTML string; B returns an integer status；A performs database queries and processes results; B only reads raw bytes；A has a switch statement for different page types; B has no such branching；A's primary output is a string; B's is a status code after reading into another method
- 修正建议: Incorporate data augmentation with diverse I/O patterns；Use contrastive learning to emphasize structural similarities over token overlap；Include additional context like resource handling patterns

### case_id=4229 FN partial_functionality

- 方法: `main` vs `doVersionCheck`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Main method that constructs a POST request to a RenRen API endpoint and prints the response.
- B 摘要: Method that fetches a version check file from a URL, parses it for build numbers, and triggers a version check.
- 静态失败原因: The model likely relied on surface-level token and API overlap, missing the abstract pattern because of low Jaccard similarity and different project-specific classes and method names.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider this a clone due to the shared abstract behavior of retrieving and processing text from a URL, which aligns with Type-3/Type-4 partial functionality similarity.
- 共享行为: Both open a URL and read its content line by line using BufferedReader.
- 行为差异: Code A uses HTTP POST with custom parameters; Code B uses HTTP GET.；Code A outputs each line; Code B parses lines for specific prefixes.；Code A lacks error handling; Code B has try-catch for IOException.；Code A is a standalone main; Code B is part of a UI component with cursor feedback.
- 修正建议: Incorporate data flow analysis to capture shared I/O patterns.；Train on examples that abstract common patterns like URL reading and line processing.；Use graph-based representations to match structural similarities despite different API calls.

### case_id=4230 FN partial_functionality

- 方法: `readVersion` vs `register`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads version/revision/date from a properties file via classpath URL.
- B 摘要: Registers a user by validating input, encoding password, setting metadata, calling a forum URL, and persisting to database.
- 静态失败原因: Static BERT models rely heavily on token overlap (Jaccard=0.1567) and structural similarity; the functions share very few tokens and have different method names and overall structure, leading to a low similarity score and a non-clone prediction.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may annotate this as a clone because both functions contain a similar boilerplate pattern of reading lines from a URL, which could be considered a partial functionality match under broad Type-3/Type-4 criteria.
- 共享行为: Both use BufferedReader to read lines from a URL connection into a while loop until null.
- 行为差异: Function A only reads and parses a local version file; Function B performs full user registration with multiple side effects.；Function A returns void; Function B returns boolean.；Function A handles only IOException; Function B handles IOException and NumberFormatException and rethrows RuntimeException.；Function A sets instance variables; Function B modifies a User object and persists it.
- 修正建议: Incorporate control-flow or data-flow analysis to detect shared I/O patterns beyond lexical matching.；Use code abstraction techniques (e.g., replacing identifiers with placeholders) to generalize API usage patterns.；Train on program-level tasks that capture subfunction similarity.

### case_id=4231 FN benchmark_preference_bias

- 方法: `modifyApplicationMessage` vs `createTempFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.7`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Modifies a locale-specific properties file by reading, updating or adding a key-value pair.
- B 摘要: Copies a resource stream into a temporary file.
- 静态失败原因: Low token overlap (0.1089) and different method names caused low similarity score; model failed to recognize high-level I/O similarity valued by BCB.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider them clones due to shared file I/O pattern (read resource, write file), classifying as broad Type-4 clone.
- 共享行为: Read from an InputStream obtained from a class resource；Write data to a file；Handle I/O exceptions；Close streams after use
- 行为差异: A processes properties key-value pairs; B copies raw bytes；A conditionally creates locale file; B always creates temp file；A uses character streams; B uses byte streams；A modifies existing content; B just copies
- 修正建议: Fine-tune on BCB annotations to learn broad semantic equivalence criteria；Incorporate hierarchical functional similarity (e.g., I/O operations)；Use models that abstract method purpose beyond token matching

### case_id=4232 FN benchmark_preference_bias

- 方法: `readData` vs `run`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Reads comma-separated tokens from static fields into sets and a map, then reads a configuration file to populate additional data structures.
- B 摘要: Downloads content from a URL, extracts first two lines as version and URL, concatenates rest, handles errors, and notifies listeners.
- 静态失败原因: Static BERT model likely relied on low token overlap and different method names/structures, missing the high-level similarity that BCB considered.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled as clone due to a broad interpretation of 'reading data for initialization', accepting partial functional similarity as Type-4.
- 共享行为: Both read line-oriented input from a source.；Both populate data structures (sets, strings, maps) during reading.；Both handle IOException.；Both are involved in initialization/configuration of a system.
- 行为差异: Data source: local strings and file (A) vs URL (B).；Output: populates global static collections (A) vs updates instance fields and fires events (B).；Error handling: throws errors (A) vs sets flags and prints stack trace (B).；Overall purpose: loading multiple categories of tokens and a configuration file (A) vs downloading version info (B).
- 修正建议: For strict cloning, improve handling of long-range dependencies and dataflow.；For BCB-style, incorporate task-level context (e.g., method name, class context) to detect broad functional similarity.

### case_id=4233 FP lexical_or_api_overlap

- 方法: `main` vs `copy`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Main method of an adapter generator that parses a Prolog file and generates adapter classes into a JAR.
- B 摘要: Copies a file from source to destination using buffered I/O streams.
- 静态失败原因: Static BERT/GraphCodeBERT likely overfitted on shallow API overlap (File, IOException, try-finally) and missed the vast functional difference due to lack of understanding of long-range dependencies and domain-specific logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would label this as non-clone because there is no semantic or syntactic similarity beyond trivial Java boilerplate.
- 共享行为: Both are public static void methods that handle I/O operations.
- 行为差异: Function A parses command-line arguments, performs complex adapter generation, and manages multiple files; Function B simply copies one file.；Function A uses a large set of libraries (ASM, Prolog parser, etc.); Function B uses only basic Java I/O.；Function A has extensive error handling and output messages; Function B throws exceptions.；Function A writes JAR files and serialized objects; Function B copies raw bytes.
- 修正建议: Incorporate more negative examples that share API elements but differ in intent.；Use representation learning that captures deeper structural features like control-flow and data-flow graphs.

### case_id=4234 FP lexical_or_api_overlap

- 方法: `readUNI` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a tab-separated file from a URL and populates a description vector.
- B 摘要: Performs a Google image search, parses image URLs from HTML, and updates a UI component.
- 静态失败原因: Static BERT may over-rely on common API tokens (URL, openStream, try-catch) and miss the semantic differences in parsing logic and output usage.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled not clone because the functions serve different purposes (data reading vs web scraping + UI update), even though both involve URL reading.
- 共享行为: Both open a URL and read input from it；Both use try-catch blocks for exception handling
- 行为差异: readUNI parses tab-separated lines; googleImageSearch parses HTML for image URLs；readUNI outputs to a parameter vector; googleImageSearch outputs to a global list and updates UI；googleImageSearch has UI interaction; readUNI does not
- 修正建议: Incorporate data flow analysis to track how data read from URL is used；Add features to distinguish UI-related code vs pure data processing；Train on more diverse examples highlighting different output behaviors

### case_id=4235 FN benchmark_preference_bias

- 方法: `modifyApplicationMessage` vs `doUpload`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Modifies a localized properties file by updating or adding a message key-value pair.
- B 摘要: Handles HTTP multipart file upload, saves files to a temporary directory, processes parameters, and redirects or responds with XML.
- 静态失败原因: Static BERT correctly predicted non-clone; this FN case shows BCB made a false positive.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have considered both functions as file manipulation utilities, but they lack semantic overlap; the label seems incorrect.
- 共享行为: Both involve file I/O operations (reading and writing files).
- 行为差异: Code A manipulates configuration properties for i18n; Code B handles HTTP file upload and session management.；Code A uses Properties, BufferedReader, FileReader/Writer; Code B uses ServletFileUpload, HttpSession, File manipulation for uploads.；Code A returns no response; Code B sends HTTP responses and forwards requests.；Code A reads and writes a single properties file; Code B manages multiple uploaded files and temporary directories.
- 修正建议: Improve BCB annotation guidelines to avoid false positives from superficial file I/O similarity.；Enhance static model to better distinguish unrelated file operations.

### case_id=4236 FN partial_functionality

- 方法: `createHTML` vs `File2String`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Generates an HTML page by reading a CSS file and optionally querying a database for dashboard content based on a page type.
- B 摘要: Reads a file from the file system or classpath and returns its entire content as a string, exiting on error.
- 静态失败原因: The low token Jaccard (0.11) and different method names/signatures likely led the model to treat them as unrelated, and the structural differences (e.g., complex switch/database in A) overshadowed the common I/O loop.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider them clones due to the shared low-level I/O pattern of reading lines and accumulating text, which is a common code fragment in many programs.
- 共享行为: Both read from an input stream using BufferedReader and accumulate lines into a StringBuilder/StringBuffer.
- 行为差异: createHTML builds a structured HTML document with dynamic database content, while File2String returns raw file content.；createHTML handles page-type selection and logs errors; File2String prints to System.out and calls System.exit on failure.；createHTML includes HTML tags and CSS; File2String does not modify the read content.
- 修正建议: Improve model sensitivity to common boilerplate patterns across different contexts.；Incorporate dataflow or control-flow analysis to recognize similar stream-reading idioms.

### case_id=4237 FP boilerplate_overlap

- 方法: `init` vs `getUser`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Loads class names from a registry file and registers them.
- B 摘要: Retrieves a user by login, loading from a configuration file if not in database.
- 静态失败原因: Static models like BERT may over-rely on token overlap and structural patterns, missing the semantic difference in purpose.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would not consider these clones because they perform entirely different tasks despite similar I/O boilerplate.
- 共享行为: Both read lines from a resource file using BufferedReader；Both use ClassLoader.getResource to locate the file；Both have try-catch for exceptions
- 行为差异: Function A loads classes, function B loads user data；Function A iterates over multiple URLs, function B reads a single file；Function A adds classes to a controller registry, function B returns a User object
- 修正建议: Include more context about method purpose；Train with more diverse negative samples that share boilerplate but differ in semantics；Use dataflow or control-flow analysis to distinguish different operations

### case_id=4238 FN benchmark_preference_bias

- 方法: `runInternal` vs `createDialogArea`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads and parses an OPDS catalog from a URL, handling HTTP connections, pagination, and downloading books.
- B 摘要: Creates a SWT dialog area to display a license agreement, reading from a resource file and showing it in a browser or text widget.
- 静态失败原因: The static model likely correctly identified the functions as non-clones based on low token overlap and different semantics, but BCB's label is a false positive, making the model's prediction appear as an error.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might have labeled it as a clone due to surface-level similarities in using URL.openStream() and handling streams, but the overall functionality is fundamentally different.
- 共享行为: Both open a URL connection and read input from a stream.；Both handle exceptions and close resources in finally blocks.
- 行为差异: Function A performs complex network I/O with retry logic and catalog parsing; function B is a one-time UI setup reading a static resource.；Function A uses HTTP headers and handles redirects; function B does not.；Function A accumulates data over multiple pages; function B reads a single file.；Function A downloads files; function B displays text in UI.
- 修正建议: Re-evaluate the BCB annotation for this pair; it may be a mislabel.；Incorporate task-specific domain knowledge to avoid overvaluing superficial I/O patterns.

### case_id=4239 FP boilerplate_overlap

- 方法: `execute` vs `readData`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Injects logging method calls into class files using ASM library.
- B 摘要: Parses configuration strings and a file to initialize character mapping data structures.
- 静态失败原因: Likely misled by boilerplate Java constructs (try-catch, loops, iterators, exception handling) combined with some common API tokens (InputStream, IOException), despite low Jaccard similarity.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would not label these as clones because they perform entirely different tasks with no overlap in functionality.
- 行为差异: Function A modifies bytecode of class files; Function B initializes static data structures from configuration.；Function A uses ASM library (ClassReader, ClassWriter); Function B uses StringTokenizer and file parsing.；Function A performs file I/O with class files; Function B performs multiple string tokenizations.；Function A has logging and counters; Function B has no output.
- 修正建议: Enhance model to capture high-level semantics beyond token overlap.；Incorporate data flow or control flow analysis to distinguish different program structures.；Ensure training data includes diverse non-clone pairs with boilerplate overlap.

### case_id=4240 FP partial_functionality

- 方法: `callService` vs `getTicketsForQueue`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.85`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Makes an HTTP GET request to a constructed URL and stores the entire response string in a field.
- B 摘要: Performs an HTTP GET request to query tickets for a queue, parses ticket IDs from the response, fetches each ticket, and returns a list.
- 静态失败原因: Static BERT models may over-rely on structural patterns (try-catch, BufferedReader while loop) and common APIs, missing the semantic gap in what the data is used for.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB labels non-clone because functions differ in overall functionality: one is generic HTTP fetch, the other is domain-specific ticket query with parsing and iterative fetching. Token similarity is low (0.1), supporting non-clone.
- 共享行为: Both perform HTTP GET requests；Both read the response line by line using BufferedReader；Both handle exceptions (IO/MalformedURLException or general Exception)
- 行为差异: Function A stores response in a field; Function B returns a List of tickets；Function B parses response content for ticket IDs and fetches each ticket; Function A does not parse；Function B has authentication (getSession) and complex error messages; Function A simple error strings；Function B uses HttpClient with params; Function A uses URL.openStream
- 修正建议: Use dataflow-aware models to distinguish storage vs. parsing actions；Include negative examples with similar boilerplate but different semantics；Incorporate functional purpose features (return type, field modifications)

### case_id=4241 FN partial_functionality

- 方法: `getHTML` vs `fileDownload`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches HTML from a URL, optionally writes it to a file, and returns the HTML string.
- B 摘要: Downloads a file from a URL and writes it to a destination directory with a fixed filename, without returning any value.
- 静态失败原因: The static BERT/GraphCodeBERT model likely focused on lexical tokens and surface-level features, resulting in low similarity due to different method names, return types, exception handling styles, and low token Jaccard index (0.2235). The model failed to recognize the shared URL-downloading pattern and the overall data flow.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels functions as clones if they perform the same high-level task (downloading content from a URL and saving it), even with differences in parameters, return types, and implementation details. The core functionality overlap is sufficient for a Type-3/Type-4 clone annotation.
- 共享行为: Both functions open a URL connection and read data from the input stream.；Both handle exceptions and perform file I/O (writing to a file).；Both use similar API patterns: URL, openConnection, getInputStream, BufferedReader/Reader.
- 行为差异: Function A returns the fetched HTML as a String; function B is void.；Function A accepts an encoding parameter; function B does not.；Function A optionally writes to a file based on dirPath; function B always writes to a file with a hardcoded name 'download.pdf'.；Function A reads line by line; function B reads character by character.
- 修正建议: Incorporate structural similarity metrics like API call sequence matching or data flow graphs.；Use contrastive learning to capture functional equivalence despite lexical differences.；Add more examples of functionally similar but lexically different pairs in training.

### case_id=4242 FP lexical_or_api_overlap

- 方法: `readScalarpvviewerDocument` vs `SRWGuiClient`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads XML configuration from a URL to set up a scalar PV viewer UI, parsing specific elements for fonts, panels, and PV settings.
- B 摘要: Constructor that reads XML/HTML from a URL to build a simple Swing browser GUI, optionally applying XSLT transformation to display HTML content.
- 静态失败原因: Static BERT may have been misled by lexical overlap of common API tokens (URL, BufferedReader, InputStreamReader) and similar structure (read URL, parse XML, catch IOException), ignoring the distinct higher-level semantics and task-specific logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels as non-clone because the core functionality differs significantly (domain-specific viewer vs. generic browser), and token overlap is low despite shared boilerplate of URL reading.
- 共享行为: Both read data from a URL using BufferedReader and InputStreamReader；Both handle IOException with try-catch blocks；Both involve parsing XML content
- 行为差异: A parses specific XML structure for a scientific viewer (fonts, panels, PVs), while B handles XML headers, may apply XSLT, and displays HTML via JEditorPane；A uses custom XmlDataAdaptor for parsing, B uses Transformer for XSLT；A configures UI components like spvs and view panels, B creates a generic browser UI with text field and scroll pane
- 修正建议: Enhance model with dataflow or control flow analysis to distinguish task-specific logic from boilerplate；Incorporate code summarization or contrastive learning to focus on high-level intent；Use more diverse training data to reduce over-reliance on lexical cues

### case_id=4243 FP boilerplate_overlap

- 方法: `setMembers` vs `getFullScreenUrl`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads HTML from a Trac URL to extract component and priority options into member arrays.
- B 摘要: Reads YouTube page to extract video parameters and construct a full screen download URL.
- 静态失败原因: Static BERT models may focus on token overlap or structural similarity; both methods share common boilerplate (URL, BufferedReader, readLine, pattern matching), leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels as non-clone because the methods serve distinct purposes despite similar I/O patterns and are not semantically equivalent.
- 共享行为: Both connect to a URL and read lines via BufferedReader；Both search for specific patterns in the response；Both extract substrings and store results
- 行为差异: setMembers uses a Trac URL; getFullScreenUrl uses a YouTube URL；setMembers searches for HTML select elements; getFullScreenUrl searches for 'fullscreenUrl'；setMembers updates member arrays; getFullScreenUrl returns a constructed URL and updates ytTitle；setMembers is void; getFullScreenUrl returns a string
- 修正建议: Incorporate data flow and purpose-aware embeddings；Use graph-based models to capture dependencies；Train with more diverse non-clone pairs that share boilerplate

### case_id=4244 FN benchmark_preference_bias

- 方法: `copyFile` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Copies a file from source to destination using NIO FileChannel.
- B 摘要: Launches an Eclipse launch configuration, processing project files and Hibernate settings.
- 静态失败原因: The static BERT model correctly identified no clone due to low lexical and structural overlap; it failed to match the BCB label because the benchmark annotation likely overgeneralized based on superficial API usage.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as a clone due to both functions containing file stream operations (FileInputStream, FileOutputStream) and using try-catch blocks, leading to a broad Type-3/4 classification based on API overlap rather than semantic equivalence.
- 共享行为: Both perform file I/O operations involving InputStream and OutputStream
- 行为差异: Different overall purpose (file copy vs. launch configuration)；Different parameters and return types；Different complexity and domain logic；Different exception handling approaches
- 修正建议: Re-evaluate the BCB annotation for this pair to confirm if it truly represents a clone；If annotation is correct, retrain model with better understanding of broad Type-4 clones

### case_id=4245 FP boilerplate_overlap

- 方法: `loadSourceCode` vs `readScalarpvviewerDocument`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Loads source code from a file, reads it line by line, applies syntax highlighting, and returns an HTML string.
- B 摘要: Reads an XML document from a URL, parses it to configure a scalar PV viewer application UI and parameters.
- 静态失败原因: The model may have been misled by the shared pattern of opening a stream, reading lines, and building a string, which are common in many file-reading functions, and thus over-predicted similarity due to superficial boilerplate overlap.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically does not consider two functions as clones if they only share common I/O boilerplate but have completely different domain-specific logic and purpose.
- 共享行为: Both use BufferedReader and InputStreamReader to read from a URL/stream；Both read lines in a while loop and build a string；Both have try-catch blocks for exception handling
- 行为差异: Function A produces an HTML string for display; Function B parses XML to configure UI components；Function A does simple line-by-line syntax highlighting; Function B has complex conditional parsing and XML adaptor usage；Function A handles a generic source code file; Function B assumes a specific XML format with custom tags；Function B has many more operations (setting fonts, updating panels, etc.)
- 修正建议: Include more context about the function's purpose or domain；Use structural matching that ignores common boilerplate；Leverage documentation or method name similarity more heavily

### case_id=4246 FP lexical_or_api_overlap

- 方法: `import_hints` vs `executePost`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Imports puzzle hint pieces from a file or URL by parsing tokens and placing them on a board.
- B 摘要: Executes an HTTP POST request with parameters and reads the response.
- 静态失败原因: The model may have been misled by the common use of URL, InputStream, and BufferedReader, which are typical boilerplate for network/IO operations, and ignored the completely different task context.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clones because the functions have entirely different purposes and logic, despite some superficial API overlap.
- 共享行为: Both open a URL stream and read input using BufferedReader.；Both handle IO exceptions with try-catch.
- 行为差异: import_hints is about reading and placing puzzle pieces; executePost is about sending an HTTP request and getting a response.；import_hints uses StringTokenizer to parse file data; executePost writes POST data and reads server response.；Different return types and logic: boolean vs String.；executePost has HTTP-specific setup (request method, headers, output stream) absent in import_hints.
- 修正建议: Incorporate more structural and dataflow analysis to distinguish different application logic.；Train on larger diverse datasets to learn that API usage alone is not sufficient for clone detection.；Use task-specific embeddings that capture high-level intent beyond token sequences.

### case_id=4247 FP boilerplate_overlap

- 方法: `readData` vs `EncodeReturn`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Reads configuration data from string tokens and a file, populating sets and maps for character processing.
- B 摘要: Encodes downloaded data using a crypto client, combines with route data, and returns a file.
- 静态失败原因: The model likely overfitted to superficial similarities like 'File', 'IOException', and 'HashSet' despite very low token Jaccard (0.0136). The long, truncated nature of code_a may have caused the model to miss the overall purpose.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically requires significant semantic similarity for a positive label; these functions share no meaningful functionality beyond generic I/O, so BCB correctly labels them as non-clones.
- 共享行为: Both perform file I/O operations；Both handle exceptions (IOException)
- 行为差异: readData populates many data structures; EncodeReturn does not；readData parses tokens and builds lookup tables; EncodeReturn does cryptographic encoding and file concatenation；readData is void and static; EncodeReturn returns a File and is an instance method；readData involves a complex loop reading a file line by line; EncodeReturn is a straightforward sequence
- 修正建议: Improve handling of long-range dependencies to capture overall function purpose；Use dataflow or control-flow features to differentiate between data initialization and file encoding；Reduce reliance on lexical overlap and emphasize task-specific semantics

### case_id=4248 FN benchmark_preference_bias

- 方法: `main` vs `doCopyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.85`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a URL, extracts each zip entry to a file in the local filesystem.
- B 摘要: Copies a single file from source to destination using NIO FileChannel, with optional preservation of last-modified date.
- 静态失败原因: The static model correctly predicted non-clone; the misclassification is due to BCB's broad annotation, not model failure. The model likely focused on low token overlap and distinct APIs (http vs FileChannel), missing any high-level functional similarity that BCB might have assumed.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider both as 'copying' operations at a high level (A extracts/writes files from a zip, B copies a file). Under broad Type-4 semantics, they could be deemed functionally similar despite different mechanisms.
- 共享行为: Both perform file I/O operations involving reading from a source and writing to a destination.；Both manage resources by closing streams or channels after use.
- 行为差异: A handles zip extraction, writing multiple entries; B copies a single file directly.；A reads from a network URL; B reads from a local file via FileChannel.；B uses transferFrom for zero-copy optimization; A uses standard I/O streaming.；B includes error checking for destination directory and file length, and preserves file dates; A does not.
- 修正建议: Improve annotation consistency in BCB by avoiding overly broad clone labels.；For models, incorporate high-level functional equivalence understanding (e.g., API calls for copying).；Adjust clone detection thresholds to favor precision when token similarity is very low.

### case_id=4249 FN partial_functionality

- 方法: `modifyApplicationMessage` vs `copy`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: modifies a properties file for a given locale and message key-value pair, including copying a default file if needed.
- B 摘要: recursively copies a file or directory from source to destination using FileChannel.
- 静态失败原因: Static models like GraphCodeBERT rely on token overlap and structural similarity; the low Jaccard (0.178) and different control flow (line-by-line vs. channel copy) led to correct non-clone prediction, but BCB's broad criteria might consider them clones.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB might have considered the shared file copy operation (a copies a default English file) as partial functionality overlap, and labeled it as a Type-4 clone (functionally similar) despite different primary behaviors.
- 共享行为: Both perform file I/O operations with try-catch exception handling.；Both can create new files (a copies default file, b creates destination).；Both involve reading from an input source and writing to an output destination.
- 行为差异: a manipulates text content line by line, while b performs a binary copy.；a's main purpose is modification of properties; b's sole purpose is duplication.；a's file copy is conditional and only for initialization; b's copy is recursive for directories.；a uses BufferedReader/FileReader/FileWriter; b uses FileChannel for efficient transfer.
- 修正建议: Refine training to distinguish primary functionality from auxiliary operations (e.g., a's copy is incidental).；Incorporate more fine-grained semantic annotations to avoid over-penalizing partial overlap.；Use contrastive learning with negative sampling focusing on high-level purpose rather than low-level I/O.

### case_id=4250 FN partial_functionality

- 方法: `copy` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Copies the contents of a source file to a destination file using a byte buffer.
- B 摘要: Builds a website for editing by reading XML configuration, transforming pages with XSLT, and writing output files for each page.
- 静态失败原因: Static BERT/GraphCodeBERT likely predicted non-clone (0) due to very low token Jaccard similarity (0.066) and no strong lexical overlap in method signatures or structure.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this as a clone due to a broad interpretation of functionality where both methods involve reading from a file and writing to another, despite the vastly different contexts and additional complexity in code B.
- 共享行为: Both perform file I/O operations using FileInputStream and FileOutputStream/FileWriter.；Both handle IOException.
- 行为差异: Code A is a generic file copy utility; code B is a complex site-building method with XML parsing, XSLT transformation, and multi-page processing.；Code A copies raw bytes; code B deals with strings, XML, and properties.；Code A is short and straightforward; code B is long and involves many steps and dependencies.；Code B includes error handling specific to DOM and FTP exceptions, which are absent in code A.
- 修正建议: Use a clone detector that accounts for partial functionality similarity with more robust semantic analysis.；Consider using a model that captures program semantics beyond token overlap, such as data flow or control flow graphs.

### case_id=4251 FP partial_functionality

- 方法: `copyFileTo` vs `readData`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Copies a file from source to destination using byte buffer.
- B 摘要: Reads a configuration file and populates multiple data structures for Tibetan character processing.
- 静态失败原因: The model may have been misled by lexical overlap of common Java constructs (e.g., while loops, File-related classes) or structural similarity in usage of set/hash operations, despite low token Jaccard.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB considers non-clones because the functions have entirely different purposes and code patterns.
- 共享行为: Both involve reading input and writing output.
- 行为差异: Function A performs a simple file copy; Function B parses a configuration file and populates sets and hashes.；Function A is short and generic; Function B is long and domain-specific.
- 修正建议: Train on more non-clone pairs with similar superficial patterns but different semantics.；Incorporate data-flow or control-flow analysis to capture semantic differences.

### case_id=4252 FP lexical_or_api_overlap

- 方法: `main` vs `readAndRewrite`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Main method that generates adapter classes from a Prolog file, involving parsing, class loading, and writing output to a JAR.
- B 摘要: Reads a DICOM image file, processes pixel data, and writes the result to another file.
- 静态失败原因: The model may have been misled by overlapping lexical tokens (e.g., 'File', 'System.out.println', 'IOException', 'out.close()') and the presence of I/O boilerplate, despite the low Jaccard similarity.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the functions solve entirely different problems (Prolog adapter generation vs. DICOM image processing), even though both perform file I/O.
- 共享行为: Both involve file I/O and reading/writing data.；Both use Java streams and handle exceptions.
- 行为差异: Function a processes Prolog files and generates Java adapter classes; function b processes DICOM medical images.；Function a is a command-line tool with argument parsing; function b is a private utility method.；Function a uses multiple external libraries (Parser, ClassWriter, etc.); function b uses DICOM-specific libraries.；Function a outputs a JAR file; function b outputs a DICOM file.
- 修正建议: Incorporate more task-level semantic features (e.g., imported libraries, class names) to disambiguate domains.；Use AST or data flow representations to capture structural differences.；Augment training data with more diverse file I/O examples to prevent boilerplate overfitting.

### case_id=4253 FP lexical_or_api_overlap

- 方法: `addDataFromURL` vs `readUNI`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads all lines from a URL and appends them with newlines to a text buffer, with basic error handling.
- B 摘要: Parses a tab-separated file from a URL, skipping the header, extracting ID and description, and adding them to a provided list.
- 静态失败原因: The model focused on common tokens (URL, openStream, line, while, catch) and API usage, but missed the crucial difference in data processing (append vs parse). The token Jaccard of 0.3077 and similar control flow misled the model into thinking they are clones.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically requires strong functional similarity; these functions have different output and parsing logic, so BCB would likely label non-clone.
- 共享行为: Both open a URL stream and read text line by line.；Both use try-catch for exception handling.；Both close the input stream after reading.
- 行为差异: A appends raw lines to a buffer; B parses tab-separated fields and adds to a vector.；A uses BufferedReader; B uses Scanner with delimiters.；A appends the URL string on exception; B catches MalformedURLException silently.；A closes stream in separate try-catch; B uses finally block.
- 修正建议: Incorporate dataflow analysis to track how read data is transformed.；Use models that capture structural differences in loop bodies.；Train on negative pairs with similar API calls but different processing logic.

### case_id=4254 FP lexical_or_api_overlap

- 方法: `getLinksFromURLFast` vs `fetchUrl`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Extracts hyperlinks and anchor texts from a web page given a URL, returning a vector of links and texts.
- B 摘要: Downloads the content of a web page as a string, returning the raw HTML.
- 静态失败原因: The model over-relied on lexical and API overlap (URL, BufferedReader, InputStreamReader, readLine) and ignored the critical differences in output types and post-processing logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels non-clones when functions have distinct purposes despite sharing boilerplate I/O code. Here, A is a link extractor, B is a raw page fetcher, so they are not considered clones even under broad Type-4 similarity.
- 共享行为: Both open a URL and read the input stream line by line.；Both accumulate lines in a buffer (StringBuffer/StringBuilder).
- 行为差异: A extracts link patterns using regex; B returns raw page content without parsing.；A returns two vectors (links and texts); B returns a single string.；A includes time checks and debug prints; B does not.；A throws Exception; B catches exceptions and returns empty string on error.
- 修正建议: Incorporate structural or dataflow analysis to distinguish output types and processing steps.；Add negative examples of similar boilerplate but different core functionality.；Use graph-based representations that capture data dependencies beyond token sequences.

### case_id=4255 FN dataflow_blindspot

- 方法: `copyResource` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.75`
- 推荐路线: `dynamic_equivalence_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Copies a resource (URL or file) to a destination file using byte-by-byte stream I/O.
- B 摘要: Copies a source file to a target file using FileChannel's transferTo method.
- 静态失败原因: Static BERT models rely on token overlap and syntactic patterns. The low Jaccard similarity and different APIs (stream I/O vs. FileChannel) make the functions appear lexically and structurally distinct, causing the model to miss the semantic equivalence in purpose.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行价值高：该样本可能是 API 写法不同但行为等价的漏报。建议测试目标为 input_output_equivalence。
- BCB 偏好解释: BCB often labels functionally similar code as clones (Type-4), even if implementations differ. Both functions perform the core task of copying data from a source to a destination file, which aligns with BCB's preference for functional similarity.
- 共享行为: Both copy data from an input source to an output file；Both close the input and output streams/channels after copying
- 行为差异: First handles both URL and file inputs; second only handles file inputs；First uses byte-by-byte copying via streams; second uses bulk transfer via FileChannel；First throws Exception; second throws IOException
- 修正建议: Incorporate data-flow analysis to capture that both read from source and write to destination；Use graph-based representations that model I/O operations as similar semantic actions；Add training examples with diverse API usage but identical high-level behavior

### case_id=4256 FP lexical_or_api_overlap

- 方法: `sendPost` vs `CheckUrl`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: sendPost sends an HTTP POST request with parameters and returns the full response body as a string.
- B 摘要: CheckUrl sends an HTTP GET request and returns the first line of the response body as a string.
- 静态失败原因: Static BERT/GraphCodeBERT likely focused on lexical and API-level similarities (URL, HttpURLConnection, BufferedReader) and overlooked the differences in HTTP method and response handling, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels these as non-clones because they have different HTTP methods and different response handling (full body vs first line), which are semantically different operations.
- 共享行为: Both use HttpURLConnection to make HTTP requests；Both return a String (response body)；Both handle exceptions
- 行为差异: sendPost uses POST method; CheckUrl uses GET method；sendPost sends parameters in request body; CheckUrl sends no parameters；sendPost returns entire response body (multiple lines); CheckUrl returns only first line；sendPost sets request properties (Accept-Language); CheckUrl does not
- 修正建议: Train with more diverse examples to learn distinguishing features like HTTP method and response processing；Incorporate data flow or control flow information to capture semantic differences

### case_id=4257 FP partial_functionality

- 方法: `readPage` vs `readTwitterFead`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads HTML from a URL, optionally ignoring lines starting with '#', returns concatenated string with newlines.
- B 摘要: Reads a Twitter JSON feed from a hardcoded URL using Apache HttpClient, checks HTTP 200, and returns response body as a string without newlines.
- 静态失败原因: The model may have focused on the common I/O pattern (BufferedReader, readLine, while loop) and returned string, overlooking the differences in API usage (URL vs HttpClient), presence of conditional logic (ignoreComments parameter), error handling, and output format (newlines vs no newlines).
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely considered them non-clones because despite both reading from URLs, the specific tasks differ (one reads HTML with optional filtering, the other reads a specific JSON feed with HTTP status handling), making them not functionally equivalent even under broad Type-4 criteria.
- 共享行为: Both read text content from a URL line by line；Both return the content as a string
- 行为差异: A uses java.net.URL, B uses Apache HttpClient；A has optional comment filtering, B does not；A returns with newlines, B without newlines；B checks HTTP status code and handles errors, A throws Exception
- 修正建议: Train with more examples that distinguish different HTTP libraries and error handling patterns；Incorporate structural differences like parameter usage and conditional branches；Use data flow analysis to capture differences in URL source and status code checks

### case_id=4258 FP other

- 方法: `main` vs `addToArchive`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.0`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Main method that validates arguments, parses a Prolog file, generates adapter layers, and writes a JAR file.
- B 摘要: Adds an entry to a ZIP archive by copying an input stream to a ZipOutputStream.
- 静态失败原因: Low token overlap suggests that the static model may have been misled by common Java API usage (e.g., IOException, File) or by both being public static methods, but the prediction is a clear false positive.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB would label as non-clone because the functions have no common functionality and very low token overlap.
- 行为差异: Different purpose: command-line tool vs utility method；Different input/output mechanisms；Different logic complexity
- 修正建议: Improve model sensitivity to functional structure；Use more sophisticated semantic matching techniques

### case_id=4259 FN benchmark_preference_bias

- 方法: `simulate` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.7`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Simulates user reputation updates by reading a file, making SOAP calls, and asserting results.
- B 摘要: Builds a site for editing by reading XML pages, applying XSLT transformations, and writing output files.
- 静态失败原因: Static BERT/GraphCodeBERT likely correctly predicted non-clone due to very low token overlap (Jaccard=0.07) and different APIs used (SOAP vs XSLT). The error is a false negative from BCB's perspective, but from a strict semantic viewpoint, the static prediction is correct.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have considered these clones due to broad Type-4 similarity: both are complex methods that perform file I/O in loops, involve exception handling, and have similar structural patterns (initialization, loop, processing, cleanup). The annotation guidelines sometimes accept non-semantic clones if the overall template is similar.
- 共享行为: Both read input from files using FileInputStream and BufferedReader.；Both write output to files using BufferedWriter or FileWriter.；Both loop over input data (lines or pages).；Both use try-catch blocks for exception handling.
- 行为差异: Function A makes SOAP remote calls (rateUser, obtainUserReputation); Function B performs XSLT transformations using Transformer.；Function A uses assertEquals for testing; Function B writes transformed content to files.；Function A processes a single input file line by line; Function B iterates over a vector of pages and processes XML for each.；Function A has multiple debug print statements; Function B uses a debug trace system.
- 修正建议: Re-evaluate BCB annotation: these functions serve entirely different purposes and should not be considered clones even under Type-4.；If the goal is semantic equivalence, use a stricter definition; if broad patterns, adjust training data accordingly.；Improve model by focusing on control-flow and data-flow differences rather than just lexical overlap.

### case_id=4260 FN partial_functionality

- 方法: `doTransfer` vs `startScript`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Forwards an incoming HTTP request to a backend URL and returns the response.
- B 摘要: Fetches a script from a URL and appends it to a dialog script.
- 静态失败原因: Static BERT models rely on lexical and syntactic similarities; with a low token Jaccard (0.17) and different method names, parameter types, and overall structure, the model failed to recognize the common 'URL open and read' pattern. The long-range semantic similarity was obscured by surface-level differences.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this as a clone because both functions share the high-level behavior of retrieving content from a URL via HTTP, despite different contexts. In BigCloneBench, many pairs involving URL reading are considered clones under Type-3/Type-4.
- 共享行为: Both open a URL connection and read data from it.；Both use InputStream or Reader to read content in a loop.；Both handle IOException.
- 行为差异: A is a full HTTP proxy handling headers, method, response code, and content type; B only reads text lines.；A writes to the servlet response output stream; B appends to dialog.script.；A uses both input and output streams; B only reads.；A has different error handling (printStackTrace) vs B (System.exit).
- 修正建议: Enhance the model with data flow or control flow representations to capture high-level I/O operations.；Include more training examples of URL reading tasks with varied contexts to learn abstract patterns.；Use contrastive learning to emphasize structural similarities despite different API surfaces.

### case_id=4261 FN benchmark_preference_bias

- 方法: `readGeoParserResult` vs `postRequest`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.5`
- 推荐路线: `preference_memory_with_manual_audit`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Sends an XML request to a geo parser service, parses the response XML to extract place names and gazetteer IDs, with retry logic.
- B 摘要: Sends an HTTP POST request with URL-encoded form data and returns the response body as a string.
- 静态失败原因: Static models like BERT rely on lexical and structural similarity; the low token Jaccard (0.154) and different control flow structures led the model to predict non-clone, missing the broad functional similarity that BCB considers.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider these as Type-4 clones because both are web service client methods that send a request and read a response, focusing on the high-level functionality of network communication.
- 共享行为: Both open a URL connection and read the response line by line；Both handle exceptions during network communication
- 行为差异: Different request types: custom XML vs. form data；Different output: collection of tuples vs. single string；Function A has retry logic; Function B does not；Function A parses XML response; Function B returns raw string
- 修正建议: Train models with more Type-4 clone pairs to recognize functional similarity beyond lexical overlap；Incorporate task-specific features like network I/O patterns

### case_id=4262 FP lexical_or_api_overlap

- 方法: `serialize` vs `readData`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.2`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Serializes a content package to an output stream via a temporary file.
- B 摘要: Reads configuration data from string fields into sets and maps using StringTokenizer.
- 静态失败原因: The static model likely overgeneralized due to both functions containing I/O-related keywords (e.g., 'IOException') and exception handling, despite low token Jaccard. The truncated code B may have misled the model into missing the overall structural difference.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clone because the two functions have completely different purposes (serialization vs. configuration parsing), no shared functionality, and low token overlap.
- 行为差异: Function A writes to an output stream; Function B populates in-memory data structures.；Function A uses file I/O and parser serialization; Function B uses string tokenization and hash set operations.；Function A has an output parameter; Function B has no parameters and reads from static fields.；Function A's logic is concise (10 lines); Function B's logic is extensive (hundreds of lines).
- 修正建议: Increase training data diversity to include non-clone pairs with low token overlap but shared I/O keywords.；Incorporate graph-based structural features to capture control flow differences.；Add length and complexity normalization to avoid bias towards long functions.

### case_id=4263 FN partial_functionality

- 方法: `getJSONData` vs `register`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.75`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches JSON data from a URL using HTTP GET and parses it into a JSONObject.
- B 摘要: Registers a User object by encoding password, setting authorities, making an HTTP GET request to a forum URL, reading the response to set forumID, persisting user, and sending confirmation email, returning boolean success.
- 静态失败原因: Static BERT methods rely on lexical and syntactic overlap, which is low (Jaccard=0.1277). The semantic similarity in the HTTP communication sub-task is overshadowed by surrounding unrelated code, leading to a non-clone prediction.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label these as clones due to the shared pattern of opening a URL, reading lines with BufferedReader, and processing the response, which is a common Type-3/Type-4 structural similarity even though the overall functionality differs.
- 共享行为: Both make an HTTP GET request to a URL and read the response line by line using BufferedReader and InputStreamReader.
- 行为差异: A returns a JSONObject parsed from the response; B returns a boolean indicating email sending success.；B includes additional operations: password encoding, database persistence, email sending, and extensive logging/error handling.；A has simpler error handling; B catches IOException and NumberFormatException specifically.
- 修正建议: Train model to recognize common subtasks (e.g., HTTP GET + stream reading) as clone indicators.；Use data flow analysis to capture similar I/O patterns.；Apply contrastive learning on function-level semantics to detect partial functionality similarity.

### case_id=4264 FN partial_functionality

- 方法: `runScript` vs `postXml`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a script file from a URL and returns its content as a string, or 'error!' on failure.
- B 摘要: Sends an HTTP POST request with XML payload and returns the response body, or throws RuntimeException on failure.
- 静态失败原因: Static BERT/GraphCodeBERT models rely on token and structural overlap; the Jaccard similarity is very low (0.15) and AST structures differ significantly (InputStream vs. HttpURLConnection with POST headers), leading the model to miss the high-level functional similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely labels these as clones because they both are network-based string retrieval functions that open a URL connection, read data, and return a string, representing a broad Type-3/Type-4 clone category for network communication utilities.
- 共享行为: Both perform network I/O to fetch or send data.；Both return a string representation of the response.；Both use URL and open a connection.
- 行为差异: A uses GET (no request body), B uses POST with XML payload.；A reads byte-by-byte with BufferedInputStream, B uses BufferedReader for line-by-line reading.；A returns 'error!' on exception, B throws RuntimeException.；A has no headers or timeout settings, B sets multiple headers and timeouts.
- 修正建议: Use data-flow-sensitive models that capture the network I/O pattern.；Incorporate functional semantics via docstring or method name embeddings.；Use contrastive learning on similar network utility functions.

### case_id=4265 FP lexical_or_api_overlap

- 方法: `executePost` vs `GetResponse`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Sends an HTTP POST request with URL-encoded parameters and returns the response body as a string.
- B 摘要: Sends an HTTP GET request to a URL and returns the response body if status is OK, otherwise returns null.
- 静态失败原因: High lexical overlap of API calls (HttpURLConnection, BufferedReader) and similar structure misled the model to ignore method type and parameter differences.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB requires functional similarity; different HTTP methods and parameter passing indicate distinct functionality, so not a clone.
- 共享行为: Both perform HTTP requests using HttpURLConnection；Both read the response line by line and append to a buffer
- 行为差异: HTTP method: POST vs GET；executePost sends data in the request body; GetResponse does not；executePost always returns response; GetResponse only returns if HTTP_OK；Different exception handling: executePost prints stack trace and returns null; GetResponse swallows exceptions
- 修正建议: Incorporate method name or HTTP method into the representation；Train on more nuanced semantic distinctions (e.g., POST vs GET)；Use data flow analysis to capture actual behavior differences

### case_id=4266 FP lexical_or_api_overlap

- 方法: `get` vs `executePost`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Sends HTTP GET request with location headers, reads lines, filters out comments, decodes GameRecord from each line, returns array of GameRecord or null.
- B 摘要: Sends HTTP POST request with URL-encoded parameters, reads response lines, appends them with carriage returns, returns response string or null.
- 静态失败原因: Static BERT/GraphCodeBERT models often rely on token-level similarity and API usage patterns. Both functions share boilerplate HTTP code (HttpURLConnection, BufferedReader, InputStreamReader) and similar control flow (try-catch, read loop), leading the model to overestimate semantic similarity despite different intents.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically requires identical or near-identical functionality (Type-1/2/3) for clones. Here, the core functionality differs fundamentally (GET vs POST, data extraction vs response accumulation), so BCB would not label them as clones.
- 共享行为: Both use HttpURLConnection to make HTTP requests；Both read response using BufferedReader and InputStreamReader；Both return null on exception
- 行为差异: HTTP method: A uses GET, B uses POST；Input parameters: A takes lat/lon/count as headers, B takes URL parameters as body；Response processing: A decodes lines into GameRecord objects, B concatenates lines into a string；Error handling: A prints response message on non-200 status, B disconnects in finally block
- 修正建议: Include data-flow analysis to distinguish GET vs POST and different output types；Use type-aware representations (e.g., method signature, return type) as additional input features；Train contrastive loss to penalize pairs with different input/output shapes despite API overlap

### case_id=4267 FP boilerplate_overlap

- 方法: `run` vs `importSequences`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Opens an HTTP connection with basic authentication and reads the response line by line.
- B 摘要: Imports biological sequences from a URL by parsing FASTA format using ImportHelper.
- 静态失败原因: Static BERT/GraphCodeBERT may have overemphasized common token patterns like 'InputStream', 'URL', 'readLine', 'StringBuffer', and try-catch structure, leading to a false positive due to boilerplate overlap.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely considered these non-clones because the overall task is fundamentally different: generic HTTP response retrieval vs. specialized biological sequence parsing. The overlapping IO boilerplate is not sufficient for clone classification.
- 共享行为: Both open a URL and read input stream；Both use try-catch for exception handling；Both read lines of text
- 行为差异: Function A performs HTTP GET with authentication; B just opens a stream；Function A appends all lines to a StringBuffer; B parses specific tokens and sequence data；Function A sets a completion flag; B populates ArrayLists；Function A encodes credentials; B does not
- 修正建议: Improve model to consider higher-level intent beyond API sequences；Use data flow analysis to track how data is processed；Incorporate more structural features like method call graphs and variable dependencies

### case_id=4268 FN partial_functionality

- 方法: `getFile` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, optionally modifies the endpoint location in the XML, and returns the file path.
- B 摘要: Copies a file from source to destination using NIO FileChannel.
- 静态失败原因: Static BERT models rely on token overlap and method name similarity; low Jaccard (0.106) and different method names led to non-clone prediction, missing the underlying similar channel transfer pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considered the shared use of FileChannel for file copy as sufficient functional similarity, aligning with Type-4 (similar output) or broad Type-3 annotation preferences in BigCloneBench.
- 共享行为: Both use FileChannel to transfer data between channels (transferFrom in A, transferTo in B)；Both involve reading and writing files with streams and channels
- 行为差异: A downloads from a network URL; B copies from a local File；A processes XML and modifies attributes; B has no such processing；A returns a String; B returns void；A has conditional logic (skip if file exists); B always copies
- 修正建议: Enhance model with API usage embeddings or data-flow graphs to recognize shared file I/O patterns；Use AST-based features to capture structural similarity in channel operations；Incorporate file I/O specific heuristics (e.g., FileChannel usage) into the clone detection model

### case_id=4269 FN partial_functionality

- 方法: `saveAttachmentBody` vs `doGet`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Saves an attachment's body stream to a file and updates the content provider with size and content URI.
- B 摘要: Handles an HTTP GET request to display a portal page, including authentication, caching, and logging.
- 静态失败原因: Static BERT models rely heavily on lexical overlap and structural similarity; the very different APIs (Part/AttachmentProvider vs HttpServletRequest/Page), low token Jaccard (0.055), and distinct vocabulary likely caused the model to predict non-clone. The model failed to capture the abstract I/O pattern that BCB considers.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both functions as clones under a broad Type-4 category because they both perform input/output operations with file handling and error management, despite different domains. The presence of file writing and exception handling in both might be seen as similar patterns.
- 共享行为: Both read input (part body stream vs request parameters) and write output (file stream vs response writer).；Both involve file I/O (FileOutputStream in a, FileWriter in b).；Both handle exceptions with try-catch blocks.
- 行为差异: a writes to a file and updates a ContentProvider; b writes to HTTP response and optionally caches page to file.；a has no authentication or user visibility checks; b performs user authentication and permission checks.；a is a simple sequential flow; b has complex conditional logic for page retrieval, caching, and error responses.；a operates in email attachment context; b operates in web portal context.
- 修正建议: Improve training to recognize abstract I/O patterns across different domains.；Use data-flow or graph-based representations to capture common operations like read-write-exception handling.；Include more diverse training examples of Type-4 clones with low lexical overlap.

### case_id=4270 FN benchmark_preference_bias

- 方法: `getFile` vs `createTar`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies the endpoint in the XML, and saves it to a local file, returning the file path.
- B 摘要: Creates a tar archive from files in a given directory, packing them into a single tar file.
- 静态失败原因: Static BERT/GraphCodeBERT correctly predicted non-clone because the token overlap is low (0.15), the method names differ significantly, and the code structures, while both using streams, serve completely different purposes. The model captured the semantic difference via self-attention on distinct API calls (URL, Document vs TarOutputStream, TarEntry) and control flow.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled these as clones due to both being file-utility functions with similar structure (try-catch, stream usage, logging), but the core functionality is semantically distinct.
- 共享行为: Both perform file I/O operations with streams；Both use logging for debugging and error reporting；Both handle exceptions and may throw custom exceptions
- 行为差异: getFile downloads a remote resource and modifies XML; createTar packs local files into an archive；getFile returns a file path; createTar returns void；Inputs and outputs are entirely different (URL/endpoint vs directory/tar file)；getFile manipulates XML content; createTar deals with directory traversal and tar entries
- 修正建议: Re-evaluate BCB annotation for this pair; likely a mislabel due to over-generalized Type-4 interpretation；Train models with more nuanced semantic labels or use contrastive learning to distinguish similar structural patterns with different intents

### case_id=4271 FP lexical_or_api_overlap

- 方法: `sendPost` vs `doVersionCheck`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Sends an HTTP POST request with parameters and returns the response body.
- B 摘要: Performs a version check by reading a version file from a URL and comparing builds.
- 静态失败原因: The model likely relied on overlapping tokens and structural patterns (URL, BufferedReader, readLine, while loop) without understanding the distinct business logic, return types, and usage context.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clones when overall functionality and purpose differ despite shared URL-reading API calls, as the tasks are semantically distinct (generic HTTP client vs specific version check).
- 共享行为: Open a URL connection and read lines via BufferedReader；Handle IO exceptions and display error messages；Use while loop to process lines
- 行为差异: A uses HttpURLConnection with POST semantics; B uses URL.openStream() (GET)；A returns a string; B is void and updates UI based on version comparison；A sends custom parameters; B reads a predefined version file format；Error handling: A uses MsgPrint.showMsg; B uses GUIUtilities methods and cursor management
- 修正建议: Incorporate function name and return type as semantic signals；Use dataflow analysis to distinguish data patterns (POST vs GET, parameter handling vs fixed URL)；Add context from calling classes or surrounding code to differentiate tasks

### case_id=4272 FN partial_functionality

- 方法: `doVersionCheck` vs `seeURLConnection`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Checks for jEdit version update by reading a version file from a URL and comparing builds.
- B 摘要: Reads the entire HTML content from a hardcoded URL into a string and logs it.
- 静态失败原因: Static BERT models likely missed the clone due to low token overlap (0.194) and presence of UI-specific tokens in A, causing focus on surface differences rather than shared control flow pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often considers methods that perform HTTP GET and read response line-by-line as clones, despite differences in data handling or error management, as they share the core algorithmic structure.
- 共享行为: Open a URL and establish a connection；Wrap input stream in BufferedReader；Read lines in a loop until null；Close the BufferedReader
- 行为差异: Method A has UI interaction (wait cursor, message dialogs); Method B has no UI；Method A parses specific lines (version/build); Method B concatenates all lines；Method A catches IOException; Method B throws Exception；URL is dynamic in A vs hardcoded in B
- 修正建议: Enhance model with control flow graph information；Use data-flow analysis to capture shared I/O patterns；Train on more partial functionality clones

### case_id=4273 FP long_range_semantics

- 方法: `readData` vs `copyFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `1.0`
- 推荐路线: `static_summary_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Parses CSV-like strings and a configuration file to populate several sets and hash maps.
- B 摘要: Copies the content of a file to another file using file channels.
- 静态失败原因: Static BERT/GraphCodeBERT likely failed due to focusing on the shared presence of file I/O operations (e.g., IOException, File) and overlooking the overall semantic purpose. The low token Jaccard suggests the error may stem from the model's inability to capture long-range semantics or from false correlation based on method signature (both static private void with throws IOException).
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB would not label as clone because they perform fundamentally different tasks with no overlapping functionality. The only commonality is file I/O, but the purpose differs entirely.
- 共享行为: Both involve file I/O (readData reads a file, copyFile copies a file).
- 行为差异: readData parses data and initializes data structures; copyFile does not parse data.；readData has complex branching and error handling; copyFile is a simple one-shot copy.；readData operates on global strings; copyFile operates on File arguments.；readData does not perform file copying; copyFile does not perform parsing.
- 修正建议: Improve model's ability to capture high-level semantic purpose beyond low-level API usage.；Incorporate more global context or use hierarchical embeddings for long methods.；Use code summarization or docstring to understand intent.

### case_id=4274 FN benchmark_preference_bias

- 方法: `DialogHelper` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.85`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Constructor that creates a JDialog displaying an image from a URL with a save-as button to copy the image file locally using FileChannel.
- B 摘要: Method that retrieves a resource by URL with caching, using HTTP conditional GET and returning an InputStream after buffered download.
- 静态失败原因: The static model likely failed to detect the clone because it focused on the low token overlap and disparate control flow structures, missing the broad functional similarity that BCB might consider. The long and complex code with nested anonymous classes and exception handling may have obscured the shared file I/O pattern.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled them as Type-4 clones due to shared low-level API usage (File streams, URL handling) and the common pattern of reading from a URL and writing to a file, despite fundamentally different overall purposes.
- 共享行为: Both involve opening a URL and performing file I/O with streams；Both handle exceptions with try-catch-finally blocks；Both create File objects and use mkdirs() for directory creation
- 行为差异: A is a GUI constructor with user interaction (showSaveDialog), B has no user interface；A copies a file using FileChannel, B downloads and caches using BufferedInputStream/OutputStream；A operates on a specific image URL passed as parameter, B resolves arbitrary resource names with caching logic and HTTP conditions；A's file copy is unconditional for a single file, B has conditional retrieval based on modification times and cache
- 修正建议: Improve models to distinguish between generic API usage and true semantic clones; incorporate higher-level intention recognition.；Train on more diverse Type-4 examples to reduce sensitivity to surface-level differences.；Use program analysis to capture data flow from URL to file output as a shared behavior pattern.

### case_id=4275 FP boilerplate_overlap

- 方法: `getUser` vs `createDialogArea`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.98`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Loads a user from a database or a configuration file by reading 'users.cfg' with a BufferedReader and StringTokenizer.
- B 摘要: Creates a SWT dialog area that reads a license file (HTML or TXT) with a BufferedReader and sets it to a Browser or Text widget.
- 静态失败原因: Static BERT/GraphCodeBERT likely overemphasized common API tokens (BufferedReader, URL, readLine, e.printStackTrace) and missed the distinct control flows and functional intents.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB annotates these as non-clones because only generic I/O boilerplate is shared; the overall functionality and data processing are entirely different.
- 共享行为: Both use URL and BufferedReader to read a text resource line by line.
- 行为差异: Function A reads a user configuration for authentication; Function B reads a license file for display.；Function A writes to a database (UserDAO.save); Function B sets UI widget content.；Function A uses StringTokenizer to parse lines; Function B appends lines to a StringBuffer.；Function A has incomplete resource cleanup; Function B properly closes streams in finally block.
- 修正建议: Enhance model with dataflow analysis to distinguish different uses of read data.；Increase weight on structural differences and functional purpose.；Use contrastive learning to penalize superficial API overlaps.

### case_id=4276 FN benchmark_preference_bias

- 方法: `main` vs `test`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a URL, unzips it, and extracts its entries to files.
- B 摘要: Tests a StorageStringWriter class by verifying string writing, reading, and expected IOException behaviors.
- 静态失败原因: Static BERT/GraphCodeBERT models likely correctly identified the low token overlap (Jaccard 0.08) and different method names, leading to a non-clone prediction, which aligns with strict semantic equivalence.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might consider them clones due to both performing I/O operations with streams and exception handling, possibly under a broad Type-4 (functional similarity) interpretation, but the core tasks are unrelated.
- 共享行为: Both involve stream I/O (InputStream, OutputStream).；Both handle exceptions (IOException).
- 行为差异: Function A extracts files from a ZIP archive; Function B tests a custom string storage class.；Function A uses FileOutputStream to write extracted data; Function B uses custom StorageStringWriter and asserts text content.；Function A demonstrates a complete download-and-extract workflow; Function B is a unit test with assertions.
- 修正建议: Review BCB annotation for this pair; it may be a false positive.；Improve dataset quality by requiring higher functional similarity for Type-4 clones.；Use dataflow or more semantic features to capture deeper behavioral differences.

### case_id=4277 FP lexical_or_api_overlap

- 方法: `setBundleInfoName` vs `readUNI`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a URL, splits lines at '=', and updates bundle names in a list.
- B 摘要: Reads a URL, parses tab-separated lines, and appends id-desc pairs to a vector.
- 静态失败原因: Overlap in common API tokens (URL, openStream, readLine, IOException) misled the model into assuming semantic similarity, ignoring differing loop logic and data transformations.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically requires functional equivalence for Type-3 clones; these methods have different goals (metadata update vs data extraction), so labeled non-clone.
- 共享行为: Both open a URL and read text line by line；Both extract substrings from each line；Both handle IO exceptions
- 行为差异: Different parsing format: key=value vs tab-separated；Different output: updates BundleInfo list vs adds to Vector<String>；Different error handling: catches only IOException vs catches Exception and has finally block
- 修正建议: Incorporate data flow analysis to distinguish different parsing patterns；Use graph-based models that capture control and data dependencies；Train on more negative pairs with similar API usage but different semantics

### case_id=4278 FP boilerplate_overlap

- 方法: `combineJs` vs `main`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.98`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Combines multiple JavaScript files into a single file, optionally minifying them, and updates a script element with the combined file path.
- B 摘要: Main method that reads a Prolog file, generates adapter classes and JAR file, and writes adapter lookup and serialized data.
- 静态失败原因: The static BERT model likely overemphasized the presence of common boilerplate code (e.g., file handling, try-catch blocks) and structural similarity in resource management, while failing to capture the deep semantic differences in domain-specific logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels this as non-clone because the functions have entirely different purposes and no significant shared functionality beyond generic programming patterns.
- 共享行为: Both use file I/O operations；Both handle exceptions with try-catch；Both use temporary file creation or resource management
- 行为差异: Function A deals with JavaScript file combination and minification；Function B deals with Prolog parsing and Java bytecode generation；Function A returns a Node element, Function B has void return；Function B uses class loading and object serialization, absent in A
- 修正建议: Improve training with more diverse negative examples that share boilerplate but differ in semantics；Incorporate dataflow analysis to differentiate distinct computation patterns；Use contrastive learning to penalize superficial lexical matches

### case_id=4279 FN partial_functionality

- 方法: `getFile` vs `decodeBody`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.4`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, possibly modifies the endpoint attribute, and saves to a temporary directory.
- B 摘要: Decodes an InputStream based on content transfer encoding and writes the result to a temporary file body.
- 静态失败原因: Low token Jaccard (0.105) and different method names/API calls (URL vs MimeUtility) misled the static model. It likely relied on surface-level lexical similarity, which is minimal, missing the abstract I/O pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider these Type-4 clones because both functions perform a 'stream-to-file copy' pattern despite different contexts (WSDL vs email body). The annotation guidelines sometimes accept similar functional behavior even if implementation details differ.
- 共享行为: Both involve reading from an input source and writing to a file；Both use I/O streams and exception handling；Both create temporary files or file outputs
- 行为差异: Function A specifically downloads from a URL and manipulates XML, while Function B only decodes an InputStream；Function A uses URLConnection, FileChannel, and XML parsing; Function B uses MimeUtility and specific input stream wrappers；Different error types: AxisFault vs IOException；Function A has file existence check and conditional download; Function B is unconditional
- 修正建议: Incorporate data-flow analysis to capture stream-to-file copy patterns；Add more Type-4 training examples with varying APIs but similar core behavior；Use graph-based representations to highlight structural similarities beyond tokens

### case_id=4280 FN benchmark_preference_bias

- 方法: `main` vs `File2String`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Sends an HTTP POST request to RenRen API with predefined parameters and prints the response line by line.
- B 摘要: Reads a file from filesystem or classpath resource and returns its content as a string, with error handling that exits the program.
- 静态失败原因: The static BERT model likely focused on token overlap and high-level semantic equivalence, missing the boilerplate similarity that BCB considers. The low Jaccard similarity and different overall purposes caused the model to predict non-clone.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may label this pair as a clone because both functions share a common structural pattern of opening a stream, reading lines in a loop, and handling I/O exceptions, which aligns with broad Type-3/Type-4 similarity criteria.
- 共享行为: Both use BufferedReader and InputStreamReader to read lines from an input stream；Both handle IOException and FileNotFoundException in try-catch blocks；Both print informational messages to System.out
- 行为差异: Function A constructs and sends an HTTP POST request; Function B reads a local file or classpath resource；Function A prints each response line; Function B appends lines to a StringBuffer and returns the result；Function B calls System.exit on errors; Function A does not；Function A uses multiple PostParameter objects; Function B does not
- 修正建议: Incorporate training examples with broad functional similarity based on I/O patterns and exception handling；Use features that capture common boilerplate code across different tasks；Adjust model to align with BCB's annotation guidelines that accept partial functionality clones

### case_id=4281 FP lexical_or_api_overlap

- 方法: `getVersion` vs `readVersion`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.85`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches version string from a remote URL and returns it.
- B 摘要: Reads a version resource file from classpath, extracts version, revision, and date, and sets corresponding fields.
- 静态失败原因: The model likely over-relied on lexical and API overlap (BufferedReader, URL, openStream/readLine, catch blocks) and structural similarity (try-catch-finally pattern), ignoring differences in data flow, side effects, and return types.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely considered them non-clones because the overall purpose and output differ significantly: one is a simple version fetcher returning a string, the other reads a multi-field configuration file and updates object state.
- 共享行为: Both read a version string from a textual source；Both use BufferedReader and URL connection/stream
- 行为差异: Different source: remote URL vs local classpath resource；Different parsing: simple line return vs key-value extraction for multiple fields；Different side effects: returns string vs sets multiple fields (version, revision, compileDate)；Different return type: static String vs void
- 修正建议: Incorporate data flow and control flow analysis to distinguish different I/O patterns and side effects.；Train on more examples with similar structure but different functionality.；Use graph-based representations (e.g., AST or CFG) to capture semantic differences.

### case_id=4282 FP lexical_or_api_overlap

- 方法: `readData` vs `encodeFileToFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Initializes character sets and mappings from static string tokens via StringTokenizer.
- B 摘要: Encodes a file to Base64 and writes to another file, returning success status.
- 静态失败原因: The model may have been misled by overlapping common Java keywords (e.g., 'while', 'new', 'String') and boilerplate patterns, despite very low Jaccard similarity.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels non-clone because the functions perform completely different tasks with no common functionality.
- 共享行为: Both are static methods；Both use while loops
- 行为差异: Different purpose: data parsing vs file encoding；Different parameters: none vs two filenames；Different I/O: no file I/O vs file I/O；Different return types: void vs boolean
- 修正建议: Incorporate dataflow or control flow analysis to capture actual semantics；Use graph-based representations to distinguish different I/O patterns；Train with more contrastive examples of non-clones with low lexical overlap but different functionality

### case_id=4283 FP lexical_or_api_overlap

- 方法: `doVersionCheck` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Checks for a new version of jEdit by reading a version file from a URL and comparing build numbers.
- B 摘要: Searches Google Images for album art by parsing HTML to extract image URLs.
- 静态失败原因: Static BERT may have been misled by lexical and structural similarities such as URL opening, BufferedReader usage, and while-loop patterns, despite low token Jaccard (0.185). It likely overfits to API-level commonalities.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels as non-clones because the functions have entirely different purposes (version checking vs. web scraping) with no meaningful shared logic beyond generic I/O patterns.
- 共享行为: Both open a URL and read input streams.；Both use BufferedReader and InputStreamReader.；Both handle exceptions with try-catch.；Both have a while loop to read lines.
- 行为差异: Function A downloads a version file; B downloads an HTML search results page.；Function A compares version strings; B parses HTML and extracts image URLs.；Function A updates UI with version check result; B populates a list of image URLs.；Exception handling differs: A uses GUIUtilities.error, B uses MusicBoxView.showErrorDialog.
- 修正建议: Incorporate semantic role labeling or task classification to distinguish intent.；Add attention to the specific data processing logic beyond generic I/O.；Train on more diverse examples that break API-level similarity.；Use graph-based representations that capture control and data flow differences.

### case_id=4284 FN lexical_or_api_overlap

- 方法: `doVersionCheck` vs `readData`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Reads a version file from a URL to check for jEdit updates.
- B 摘要: Parses a Tibetan transliteration configuration file to populate lookup data structures.
- 静态失败原因: Static BERT/GraphCodeBERT likely over-relied on lexical overlap (e.g., 'BufferedReader', 'while ((line = ...) readLine())') and API usage patterns, missing the distinct data-flow and application-domain semantics.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: The BCB annotation may have considered superficial structural similarity (both read lines, parse key-value patterns) as Type-3/4 clone, but the tasks are entirely different.
- 共享行为: Both use basic I/O to read text input.
- 行为差异: Function A reads from a URL; B reads from a local file.；Function A parses version and build numbers; B parses linguistic character mappings.；Function A displays GUI messages; B populates internal data structures.；Function A has a wait cursor UI; B has no UI interaction.
- 修正建议: Incorporate semantic understanding of library/domain-specific calls.；Use data-flow analysis or higher-level program summaries.；Train on more diverse data to distinguish generic I/O from specific business logic.

### case_id=4285 FP lexical_or_api_overlap

- 方法: `sendRequest` vs `downloadFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Sends an XML request to a servlet via HTTP and parses the response into a JDOM document.
- B 摘要: Downloads a file from a URL and saves it to a local file with progress tracking.
- 静态失败原因: Static models may over-rely on lexical overlap ('URL', 'openConnection', 'InputStream') and structural similarity, missing the distinct control flow and I/O purposes.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels non-clone because the high-level tasks differ (request/response vs file download) despite shared networking patterns.
- 共享行为: Both open an HTTP URL connection；Both use input and output streams；Both handle network I/O
- 行为差异: A sends XML data; B downloads raw bytes；A uses GZip compression; B does not；A returns empty string; B returns boolean；A shows error dialog on connect exception; B throws exception
- 修正建议: Incorporate data flow analysis to track the type of data written/read；Use method name semantics or call graph context to differentiate tasks

### case_id=4286 FN partial_functionality

- 方法: `getHTML` vs `CheckUrl`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches entire HTML content from a given URL with specified encoding, optionally writes to file, and returns the full page as string.
- B 摘要: Fetches the first line of the HTTP response from a given URL and returns it as string.
- 静态失败原因: Static BERT models like GraphCodeBERT likely focus on token overlap and structural similarity; the low Jaccard similarity (0.288) combined with different method names, parameter lists, and reading logic leads to a non-clone prediction. The model misses the underlying commonality of HTTP content fetching.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider them clones because both functions perform HTTP URL content retrieval, sharing the core pattern of opening a connection, reading input, and returning a string. Differences in reading full vs single line and optional file writing are considered minor variations typical of Type-3/Type-4 clones.
- 共享行为: Both open an HTTP connection to a URL；Both read the response stream using BufferedReader；Both return a string from the response；Both catch exceptions and print stack trace
- 行为差异: A reads all lines, B reads only first line；A supports encoding parameter, B uses default；A optionally writes to file, B does not；A disconnects connection in finally, B does not
- 修正建议: Enhance training data with more partial functionality clones；Incorporate data flow analysis to capture similar stream operations；Use task-level intent detection to recognize common patterns beyond token similarity

### case_id=4287 FN partial_functionality

- 方法: `split` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Splits a large FASTA file into multiple smaller files based on size limits.
- B 摘要: Downloads a KMZ file from a URL and extracts its zip entries to local files.
- 静态失败原因: The static model correctly identified low lexical and structural overlap, but BCB's broad clone definition might consider both as file-processing utilities, leading to the label 1. The model failed to capture this high-level similarity because it relies on token and syntax patterns.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB might have considered both as file-processing utilities that read some input and produce multiple output files, but the core logic and domain are very different.
- 共享行为: Both read from a source and write to multiple output files；Both use file streams and buffering
- 行为差异: A reads a local FASTA file and partitions it; B downloads a remote KMZ archive and extracts entries；A uses FileChannel and ByteBuffer for efficient I/O; B uses ZipInputStream and BufferedOutputStream；A has complex logic for checking size and splitting; B simply iterates over zip entries
- 修正建议: Incorporate higher-level representations such as API usage patterns；Leverage domain knowledge about file processing tasks；Use code structure embeddings that capture control flow and data flow at a more abstract level

### case_id=4288 FP boilerplate_overlap

- 方法: `getContent` vs `readUNI`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches HTTP response content by executing a request and reading lines into a string.
- B 摘要: Parses a tab-separated file from a URL, extracting ID and description, and adds them to a vector.
- 静态失败原因: The model likely focused on the shared I/O boilerplate (opening stream, reading lines, closing) and overlooked the different data processing within the loop, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically requires high syntactic or algorithmic similarity. These functions have low token overlap (0.15) and different core logic, so BCB labels non-clone.
- 共享行为: Both read from a network source；Both process text line by line；Both handle I/O and close resources
- 行为差异: Different input types (HttpUriRequest vs String URL)；Different output (returns String vs modifies Vector parameter)；Different parsing logic (generic line appending vs specific TSV parsing)；Different libraries (HttpClient vs URL/Scanner)
- 修正建议: Incorporate data-flow analysis to distinguish core transformations beyond I/O；Use type-aware embeddings for method signatures；Train on more diverse I/O patterns to reduce boilerplate sensitivity

### case_id=4289 FP long_range_semantics

- 方法: `hash` vs `perform`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `static_summary_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: A static method that computes the MD5 hash of a given string and returns the hex-encoded hash.
- B 摘要: A Struts action handler that processes a web request to classify a concept, involving session management, HTTP POST to an external service, and XML parsing.
- 静态失败原因: The model likely focused on superficial similarities such as the presence of if-null initialization, try-catch blocks, and string concatenation, without understanding the broader context. The long length and truncated middle of function B may have caused the model to miss the overall purpose, leading to a false positive based on weak lexical overlap.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB would not label these as clones because they implement completely different functionalities—MD5 hashing vs. web request processing. The high-level semantics are unrelated, even though both involve some common patterns like string manipulation and error handling.
- 共享行为: Both are public methods；Both involve string operations；Both have error handling (try-catch blocks)
- 行为差异: Function A performs a cryptographic hash; Function B handles a complex web workflow；Function A returns a hex string; Function B returns an ActionForward for view navigation；Function A is stateless and thread-safe; Function B heavily depends on session and request state；Function A calls MessageDigest; Function B performs HTTP I/O and XML parsing
- 修正建议: Improve model's ability to capture long-range dependencies via better attention mechanisms or hierarchical encoding；Incorporate more precise structural features (e.g., data flow, control flow) to distinguish cryptographic utilities from web controllers；Use contrastive learning with harder negative examples that share lexical patterns but differ semantically

### case_id=4290 FP lexical_or_api_overlap

- 方法: `startScript` vs `checkForUpgrade`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Loads a script from a URL and appends it to a dialog buffer.
- B 摘要: Checks for software upgrades by contacting a license server and processing upgrade data.
- 静态失败原因: The model likely overemphasized the lexical and API overlap (URL, BufferedReader, readLine) and ignored the differing core logic and overall context.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labelled this as non-clone because the functions have completely different high-level purposes and data transformations, despite sharing a trivial I/O pattern.
- 共享行为: Both use URL to open an HTTP connection；Both read lines from a BufferedReader
- 行为差异: A simply reads a script file and appends to a string; B performs complex license validation and upgrade logic；A has no database or UI operations; B manipulates database tables and UI components；A's URL is passed as parameter; B constructs a URL from multiple local variables
- 修正建议: Incorporate dataflow or control-flow analysis to distinguish different high-level behaviors；Use graph representations that capture the sequence of operations beyond local patterns

### case_id=4291 FN partial_functionality

- 方法: `copyResource` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource (URL or file) to a destination file using byte-by-byte stream copy.
- B 摘要: Copies a file to another file using NIO FileChannel transfer.
- 静态失败原因: Static BERT models rely on syntactic and token-level overlap, which is low (Jaccard 0.14). They fail to recognize the high-level functional equivalence due to different API usage and control flow patterns.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB considers these clones because both perform the core task of copying file contents, despite differences in source resolution and copy mechanism. The functional similarity outweighs syntactic differences.
- 共享行为: Both copy file content from source to destination.；Both handle file I/O and throw exceptions on failure.
- 行为差异: A supports both URL and file sources; B only file.；A uses InputStream/OutputStream with byte loop; B uses FileChannel.transferTo.；A throws generic Exception; B throws IOException.；A is private and uses implicit source/destination; B is static with explicit File parameters.
- 修正建议: Incorporate data-flow analysis to track that both functions read and write bytes.；Train on pairs with low syntactic but high functional similarity.；Use a model that can abstract over implementation details like URL vs file source.

### case_id=4292 FP lexical_or_api_overlap

- 方法: `postRequest` vs `checkForUpgrade`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Sends an HTTP POST request with form-encoded parameters from a HashMap and returns the response body as a string.
- B 摘要: Checks for software upgrades by querying a remote server, parsing XML-like responses, updating a database table, and manipulating UI components.
- 静态失败原因: Static BERT/GraphCodeBERT likely focused on shared API tokens (URL, URLConnection, BufferedReader) and similar control flow patterns (try-catch, loops), ignoring the vastly different business logic and side effects, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labeled non-clone because the functions have completely different purposes: one is a generic HTTP POST utility, the other is a specific upgrade checking method with database and UI operations. The token Jaccard is low (0.1477), and the semantic gap is large.
- 共享行为: Both use URL and URLConnection to make HTTP requests；Both read response line by line with BufferedReader
- 行为差异: A sends POST data; B sends a GET request with query parameters；A returns collected response string; B returns void and updates UI/database；A handles form encoding; B parses XML-like response and interacts with database and UI；A is generic HTTP utility; B is specific to upgrade checking with business logic
- 修正建议: Incorporate more robust structural or dataflow analysis to distinguish utility functions from business logic.；Use contrastive learning to penalize high similarity from boilerplate code.；Add context from method name or surrounding class to capture intent.

### case_id=4293 FP lexical_or_api_overlap

- 方法: `sendPost` vs `importRoles`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Sends an HTTP POST request and returns the response body as a string.
- B 摘要: Reads XML role data from a URL, parses specific tags into RoleName objects, and returns a list.
- 静态失败原因: Static models like BERT or GraphCodeBERT may rely on lexical/API overlap (URL, BufferedReader, readLine, try-catch) and similar control flow (while read line), ignoring semantic differences in I/O operations and data processing.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels only functionally equivalent or near-equivalent (Type-1/2/3) as clones; these functions have different purposes and outputs, thus not clones.
- 共享行为: Both use URL and BufferedReader to read line by line from an input stream；Both use try-catch for exception handling；Both return a result (String vs ArrayList)
- 行为差异: A uses POST (output stream, parameters) while B uses GET (openStream without output)；A returns raw string concatenation; B parses XML into structured objects；A handles one generic Exception; B handles three specific exceptions；A sets request properties; B does not
- 修正建议: Incorporate data flow analysis to track how input/output streams are used；Add awareness of method-level semantics (e.g., distinguishing HTTP clients from XML parsers)；Use contrastive learning to separate functions with similar API usage but different tasks

### case_id=4294 FN lexical_or_api_overlap

- 方法: `doGet` vs `download`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Serves an HTTP GET request by retrieving a page, checking permissions, logging, and rendering HTML.
- B 摘要: Downloads a file from classpath resources to a user-chosen file path using I/O streams.
- 静态失败原因: Very low lexical overlap (Jaccard 0.052) and static models lack the capacity to infer high-level semantic abstraction of 'data transfer' across entirely different API contexts and code lengths.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may label them as clones based on broad Type-4 similarity in data transfer operations, considering both as 'output data from a source' despite very different domains and complexity.
- 共享行为: Both perform I/O operations (read and write)；Both handle IOException with try-catch
- 行为差异: doGet processes HTTP request/response in a servlet context; download is a private utility method；doGet involves complex logic (page retrieval, permission checks, caching); download is a simple file copy；doGet writes to HTTP response; download writes to a local file via FileOutputStream；doGet uses many external APIs (HttpServletRequest, Page, Property); download uses classpath resources and SWT dialogs
- 修正建议: Use data-flow analysis to identify input-output patterns；Incorporate broader context like method signatures or class names；Augment training with program slicing or abstract representations

### case_id=4295 FN lexical_or_api_overlap

- 方法: `callApiPost` vs `seeURLConnection`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends an HTTP POST request with parameters, headers, timeouts, and returns the input stream, with error handling.
- B 摘要: Performs a simple HTTP GET request and reads the response into a StringBuffer for logging.
- 静态失败原因: Static BERT correctly identified as non-clone due to low token overlap (0.096) and differing control flow; the model was not misled by the lexical/API overlap.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may have considered them clones due to both performing URL connections and reading data, accepting broad Type-4 similarity based on common API usage.
- 共享行为: Both open a URL connection and read data from the stream
- 行为差异: HTTP method: POST vs GET；Function A sets headers, timeouts, and outputs parameters; B does not；Function A includes error checking on response code; B does not；Function A returns an InputStream; B logs and returns void
- 修正建议: Define stricter clone criteria for BCB to avoid labeling unrelated URL connection functions as clones；Consider adding more context about method purpose and HTTP method dissimilarity

### case_id=4296 FN partial_functionality

- 方法: `readAndRewrite` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Reads a DICOM file, parses it, and writes pixel data to another file.
- B 摘要: Builds a website for editing by reading XML templates, transforming them, and writing output files.
- 静态失败原因: Static BERT models rely heavily on token and structure overlap; the low token Jaccard (0.035857) and different API calls likely led to a non-clone prediction.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may annotate as clone because both functions follow a common pattern of reading, transforming, and writing data, which is considered a Type-4 (functionally similar) clone despite different domains.
- 共享行为: Both read from input files；Both perform data transformation；Both write output to files；Both use streams for I/O
- 行为差异: Different data formats (DICOM vs. HTML/XML)；Different transformation logic (pixel data vs. XML/XSLT)；Different complexity and number of parameters；Different error handling and output methods
- 修正建议: Incorporate data flow and control flow analysis to capture abstract behavior；Use models that understand high-level I/O operations rather than surface tokens；Add training examples of cross-domain functional similarity

### case_id=4297 FN partial_functionality

- 方法: `sendExceptionToServer` vs `setBundleInfoName`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends an exception report to a server via HTTP POST with URL-encoded parameters.
- B 摘要: Reads a properties file from a URL and updates bundle names in a list based on key-value pairs.
- 静态失败原因: Static BERT likely focused on the low lexical overlap and different overall logic (post vs. get, output vs. object manipulation), missing the broad I/O pattern that BCB might consider similar.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may annotate these as clones because both involve reading from a URL and handling I/O, which could be seen as structurally similar at a high level, despite different specific purposes.
- 共享行为: Both perform network I/O via URL and read input streams.；Both use try-catch to handle IOException.；Both process lines from a stream (though A also writes).
- 行为差异: A sends data via POST request; B only reads from the URL.；A constructs a complex URL-encoded payload; B parses simple key=value lines.；A outputs to console; B modifies object fields and returns boolean.；Different method names, parameters, and return types.
- 修正建议: Train with more data that distinguishes different I/O operations.；Incorporate task-specific features like method name, parameter types, and return type.；Use data augmentation to emphasize functional differences.

### case_id=4298 FP boilerplate_overlap

- 方法: `downloadModel` vs `getXML`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Downloads an RDF/XML model from a URL via HTTP, sets accept headers, reads into a Model object.
- B 摘要: Fetches XML response from a servlet URL by encoding a request and reading line by line into a String.
- 静态失败原因: The model likely focused on overlapping API usage (URL, InputStream, IOException) and the try-catch pattern, overlooking the semantic differences in return types and processing logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels non-clone because the functions serve different purposes (downloading a model vs fetching XML) and the code structures differ significantly despite common network I/O boilerplate.
- 共享行为: Both open a URL connection and read input stream.；Both handle MalformedURLException and IOException.；Both close the input stream/reader after reading.
- 行为差异: A returns a Model object, B returns a String.；A uses URLConnection and model.read(), B uses BufferedReader and StringBuilder.；A sets HTTP request properties, B URL-encodes the request string.；A throws RuntimeException on error, B returns null.
- 修正建议: Incorporate return type and method name context into representation.；Use more fine-grained dataflow analysis to distinguish between model parsing and raw text reading.；Include negative examples of network I/O operations with different purposes during training.

### case_id=4299 FP lexical_or_api_overlap

- 方法: `retrieveQ` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads content from a URL and returns it as a string, printing the HTTP response message.
- B 摘要: Searches Google Images, parses image URLs from the response, adds them to a list, and updates UI with the first image.
- 静态失败原因: The model likely relied on overlapping API tokens (URL, BufferedReader, InputStreamReader) and overlooked the higher-level functional divergence, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels non-clones when functions have different overall purposes despite sharing some IO boilerplate; these are functionally unrelated (Type-4).
- 共享行为: Both open a URL connection and read data using BufferedReader；Both handle IOException and MalformedURLException
- 行为差异: A returns the full content; B parses specific image URLs and updates a UI component；A uses generic URLConnection; B uses HttpURLConnection with custom User-Agent；A prints response message to stderr; B shows error dialogs via MusicBoxView；B modifies global state (googleImages, UI) while A is stateless
- 修正建议: Incorporate control-flow or data-flow features to distinguish reading vs. parsing behavior；Add a classification head that focuses on function signatures or return types；Use contrastive learning to emphasize semantic differences beyond token overlap

### case_id=4300 FP long_range_semantics

- 方法: `actionPerformed` vs `getFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `static_summary_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Event handler that processes various commands like GRAPHVIZ and IMAGEMAGICK to open file choosers and save preferences, and also handles a settings dialog that saves multiple configuration settings.
- B 摘要: Retrieves a file either from the current directory or copies a resource from classpath to that location and returns it.
- 静态失败原因: The static BERT model may have been misled by overlapping keywords like 'File' and 'IOException', and the presence of file-related operations in both. However, given the low token Jaccard (0.0676), the model likely failed due to inability to capture the long-range semantics and diverse control flow of function A, possibly due to input truncation or superficial similarity in API usage.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely labels this as non-clone because the functions are entirely different in purpose and structure; BCB emphasizes overall functionality equivalence, and these two are unrelated.
- 共享行为: Both involve file system operations using java.io.File.
- 行为差异: A is a large UI event handler with multiple conditional branches, while B is a simple file retrieval method.；A interacts with GUI components (JFileChooser, JTextField), whereas B has no UI.；A saves multiple preferences to a controller, while B only returns a File object.；B handles resource copying from classpath, which is absent in A.
- 修正建议: Use a model that handles long input sequences effectively, e.g., with sliding windows or hierarchical attention.；Incorporate AST or control-flow graph features to better distinguish UI event handlers from simple file operations.

### case_id=4301 FN benchmark_preference_bias

- 方法: `modifyApplicationMessage` vs `convert`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `1.0`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Modifies a properties file for a specific locale by updating or appending a message key-value pair.
- B 摘要: Converts an ACRNEMA stream file to DICOM format, adding UIDs and handling pixel data.
- 静态失败原因: Static BERT did not fail; it correctly predicted non-clone. The BCB label appears incorrect.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB likely labeled as clone erroneously, possibly due to both functions involving file I/O and configuration-like tasks, but the similarity is superficial.
- 行为差异: Different file formats (properties vs DICOM/ACRNEMA)；Different operations (string manipulation vs binary pixel data handling)；Different domain (internationalization vs medical imaging)；No common logic or data flow
- 修正建议: Review BCB annotation for this pair to correct label；Ensure benchmark includes diverse functional domains to avoid false positives

### case_id=4302 FP partial_functionality

- 方法: `getLinksFromURLFast` vs `populateResources`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Extracts links and anchor text from a URL using regex and returns them as vectors.
- B 摘要: Loads template files and image resources from classpath and saves them as database objects.
- 静态失败原因: Static BERT likely overemphasized lexical overlap (BufferedReader, StringBuffer, url/stream) and missed the high-level semantic difference.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely considered the overall functionality too different despite some I/O pattern overlap; the methods serve distinct semantic purposes.
- 共享行为: Both open a URL/stream and read lines using BufferedReader.；Both use StringBuffer to accumulate read lines.
- 行为差异: Different inputs: one takes a URL string, the other uses predefined resource paths.；Different outputs: one returns vectors of links and texts, the other saves resources to database.；Different error handling: A throws Exception, B catches specific exceptions and logs.；Different purposes: web scraping vs resource initialization.
- 修正建议: Enhance model with data flow analysis to distinguish input-to-output transformations.；Include method name and return type as features.；Train on more diverse examples of I/O patterns with different intents.

### case_id=4303 FN benchmark_preference_bias

- 方法: `createNew` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Creates a resource file (either ".request" or ".tokens") in a client-allowed folder, copies input stream to it, and returns a file object.
- B 摘要: Builds an entire site for editing by processing a list of pages, performing XSLT transformations, and writing output files with various properties and error handling.
- 静态失败原因: The static BERT model likely correctly predicted non-clone due to low lexical overlap (token Jaccard 0.064) and clear semantic differences; the model did not fail from a semantic perspective, but rather disagreed with the BCB label.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as a clone due to both functions performing file I/O and having some conditional logic, but the overall functionality is vastly different, so this seems like an annotation error or overly broad interpretation.
- 共享行为: Both involve file I/O operations (reading/writing files)；Both use InputStream and FileOutputStream in some capacity；Both have conditional logic and error logging
- 行为差异: A is a simple file creation with permission check; B is a complex multi-step site generation routine；A returns a Resource object; B returns void；A deals with specific file names (.request, .tokens); B processes multiple pages and media types；A uses IOUtils.copy; B uses FileInputStream, XSLT transformers, and custom FileSystem methods
- 修正建议: Review the BCB annotation to ensure it reflects actual functional similarity；If this is a false positive in the benchmark, consider removing or correcting the pair

### case_id=4304 FN partial_functionality

- 方法: `scrapeForIsbns` vs `readData`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Scrapes ISBN-10 codes from a URL by reading HTML lines using a regex pattern, with retry on connection errors.
- B 摘要: Reads multiple sets and maps from string tokens and a file, initializing data structures for a Tibetan transliteration system.
- 静态失败原因: Static BERT relied on low token similarity (0.087) and structural differences, failing to capture the abstract commonality of reading text and populating collections.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB might label this as a clone if they consider both as 'data extraction from text input into collections' at a high level of abstraction, but the domain and implementation details are very different.
- 共享行为: Both read input (URL stream vs. string tokens and file) and store extracted data in collections (Set/Map).；Both use loops to process lines/tokens.；Both handle rare exceptions (IO, etc.).
- 行为差异: A is a network-scraping function with retry logic; B is a file/configuration parser.；A returns an integer count; B is void.；A uses regex; B uses StringTokenizer and manual parsing.；A has sleep retry; B does not.
- 修正建议: Incorporate dataflow or functional equivalence via graph-based representations.；Use contrastive learning with functional labels to learn high-level intent.；Leverage documentation or method names for semantic clues.

### case_id=4305 FP boilerplate_overlap

- 方法: `CopyTo` vs `main`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Copies a file byte by byte using FileReader and FileWriter with resource cleanup.
- B 摘要: Parses command-line arguments and generates adapter JAR files from a Prolog file.
- 静态失败原因: The static model likely overfocused on shared API calls (File, IOException) and boilerplate patterns (try-finally close), ignoring the significant semantic difference in the overall algorithm.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels based on semantic similarity of core functionality; these two functions are entirely different in purpose, so they are non-clones despite some API overlap.
- 共享行为: Both involve file I/O operations using java.io classes.；Both have try-catch-finally blocks for exception handling.
- 行为差异: Function A is a simple file copy; Function B is a complex code generation pipeline.；Function B parses command-line arguments; Function A has no arguments.；Function B uses many external libraries (ASM, Prolog parser); Function A uses only basic I/O.；Function B outputs to console and writes to multiple files; Function A copies one file.
- 修正建议: Enhance model with control flow and data flow analysis.；Use hierarchical or graph-based representations to capture overall functionality.；Expand training data with more diverse non-clone pairs that have API overlap to reduce false positives.

### case_id=4306 FN benchmark_preference_bias

- 方法: `main` vs `EncodeReturn`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a URL and extracts its entries to the current directory.
- B 摘要: Encodes data using cryptographic methods and concatenates output files, then returns the final file.
- 静态失败原因: Static BERT models rely on token similarity and structural patterns. The token Jaccard similarity is very low (0.082), so the model correctly predicted non-clone. If the BCB label is correct, the model fails to capture the vague semantic similarity; more likely, the BCB label is incorrect.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: The BCB annotation likely considered both as file manipulation utilities with similar stream-handling patterns, despite the low token similarity. This may reflect a broad Type-4 interpretation or an annotation error.
- 共享行为: Both involve file I/O operations using FileInputStream and FileOutputStream.；Both handle streams and close resources.
- 行为差异: Code_a reads a zip file and extracts entries; Code_b performs encryption and file concatenation.；Code_a handles URL protocols; Code_b uses cryptographic operations.；Code_a is a main method; Code_b is a protected helper method.；Code_a outputs to multiple files; Code_b returns a single file.
- 修正建议: Re-evaluate BCB annotation for this pair; it may be a mislabel.；If genuine clone, use models that capture high-level functional similarity beyond lexical overlap.

### case_id=4307 FN benchmark_preference_bias

- 方法: `handler` vs `readData`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.7`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Parses a URL response to extract substrings and update a map based on target patterns.
- B 摘要: Parses multiple comma-separated strings and a file to populate various sets and maps for Tibetan character mapping.
- 静态失败原因: Low lexical token overlap (0.084) and use of entirely different APIs and control structures; static BERT/GraphCodeBERT models rely on surface form and may miss high-level semantic similarity.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: Both functions are data-initialization routines that populate collections from string sources, so BCB may annotate them as Type-4 clones based on similar high-level purpose.
- 共享行为: Both parse input strings and populate data structures (maps/sets).
- 行为差异: Different input sources (URL vs. static strings)；Different parsing logic；Different output structures
- 修正建议: Use functional role classification to group initialization routines.；Incorporate dataflow or call-graph context to capture semantic similarity beyond lexical tokens.

### case_id=4308 FP lexical_or_api_overlap

- 方法: `read` vs `SRWGuiClient`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads camera log from a URL, parses lines into objects, adds to list, sorts, and logs progress.
- B 摘要: Constructor for a Swing browser GUI that reads XML from a URL, optionally transforms with XSLT, and displays HTML content.
- 静态失败原因: Static BERT/GraphCodeBERT over-relied on lexical and API-level overlaps such as 'BufferedReader', 'InputStreamReader', 'url.openStream()', and 'readLine()', while ignoring the drastically different high-level semantics and control flow structures.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels Type-4 (semantically unrelated) as non-clones. Despite some API overlap, the two functions serve completely different purposes and have minimal shared behavior, so BCB marked them as non-clones.
- 共享行为: Both open a URL stream and read lines using BufferedReader.；Both handle I/O exceptions and close resources.；Both involve reading text data from a URL.
- 行为差异: Function A purely reads and parses log data; Function B builds a full GUI browser.；Function A focuses on extracting structured records; Function B handles XSLT transformation and HTML display.；Function A has no GUI components; Function B sets up Swing widgets and event listeners.；Function A sorts the records; Function B does not sort.
- 修正建议: Incorporate global context like class name and method name.；Use data flow analysis to distinguish different usage patterns of readLine and URL handling.；Enhance training with contrastive examples where API overlap misleads.；Consider graph-based representations that capture call graphs or control flow.

### case_id=4309 FP lexical_or_api_overlap

- 方法: `issueCommandToServer` vs `SRWGuiClient`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Sends an HTTP POST with command and JSON-encoded data to a server, returning the server's response string.
- B 摘要: Constructs a Swing GUI browser that reads an XML document from a URL, optionally applies XSLT transformation, and displays the result in a JEditorPane.
- 静态失败原因: The static model likely overfitted on overlapping API calls (URL, BufferedReader, InputStreamReader) and control structures, missing the overall purpose difference due to lack of deep semantic understanding.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clone because the high-level functionality (server command execution vs GUI browser constructor) is completely different; the shared I/O patterns are incidental and do not indicate semantic similarity.
- 共享行为: Both open a URL connection and read data using BufferedReader and InputStreamReader；Both accumulate read lines into a StringBuffer；Both handle IOException
- 行为差异: Method A sends data via HTTP POST with parameters; Method B uses HTTP GET to retrieve data；Method A outputs data to the server and reads the response; Method B only reads data and displays it in a GUI；Method B includes XML parsing, XSLT transformation, and GUI setup; Method A does none of these
- 修正建议: Incorporate method-level context such as class names and surrounding code；Use dataflow analysis to distinguish between writing and reading operations；Add training on broader program semantics to reduce reliance on API sequence patterns

### case_id=4310 FN benchmark_preference_bias

- 方法: `logging` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Logs inbound SOAP message details including headers and payload, handling potential truncation and file caching.
- B 摘要: Builds HTML pages for editing by transforming XML with XSLT, replacing paths, and writing output files per page.
- 静态失败原因: The model likely correctly predicted non-clone due to low token overlap and distinct method names, but the BCB label suggests a false negative in the benchmark's own annotation bias, not a model failure.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider them clones based on broad Type-4 criteria: both perform I/O operations, parse/extract data, and handle multiple exception types, despite different application logic.
- 共享行为: Both involve reading input data (InputStream) and writing output (log or file).；Both handle exceptions (IOException, etc.).；Both use String-related manipulation (StringBuffer, string replacement).
- 行为差异: Completely different domain: logging vs web page generation.；Different control flow: linear in A, loop over pages in B.；Different external dependencies: A uses CXF/WSS4J classes, B uses custom Page/FileSystem classes.；Different output: A writes to a logger, B writes to a file system.
- 修正建议: Re-evaluate BCB labeling for this pair to ensure functional similarity.；Incorporate domain/context features to distinguish operational semantics.；Use dynamic analysis or data-flow patterns to capture execution similarity.

### case_id=4311 FN benchmark_preference_bias

- 方法: `doGet` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Handles HTTP GET request to retrieve and render a page, with permission checks and optional file caching.
- B 摘要: Copies a file from source to destination using FileChannel.
- 静态失败原因: The static BERT model correctly identified the low lexical and structural similarity and predicted non-clone. It failed to detect any clone because there is none.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might have considered both as containing file writing operations (doGet writes to a temp file), but the overall functionality is completely different; possibly a labeling error.
- 共享行为: Both involve I/O operations；Both handle IOException；Both use try-catch-finally blocks
- 行为差异: Function A is a servlet method with complex business logic for page rendering; Function B is a simple utility for file copying；Function A deals with HTTP, user sessions, and page properties; Function B only deals with file channels
- 修正建议: Re-annotate the pair as non-clone；Improve BCB annotation guidelines to avoid such false positives

### case_id=4312 FP lexical_or_api_overlap

- 方法: `googleImageSearch` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches Google Images for current track if artist changed, builds URL from track info, parses HTML, stores image URLs in googleImages list.
- B 摘要: Fetches Google Images for given search and start parameters, clears googleImages list, parses HTML, stores URLs, then updates UI with the first image.
- 静态失败原因: High token Jaccard (0.696) and large common code block (HTTP fetch, parse) dominate, leading the model to overlook differences in method signature, condition, and additional UI code.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels non-clones when methods have different parameters, different logic flows (condition vs none), and different side effects (UI updates). Despite high token overlap, the behavioral differences make them functionally distinct.
- 共享行为: Both fetch web data from Google Images using HTTP GET with similar User-Agent header；Both parse HTML response for image URLs using same regex pattern；Both add extracted image URLs to the same googleImages list；Both handle exceptions with same error dialog method
- 行为差异: A uses internal state (currentTrack) to build query; B uses explicit parameters (search, start)；A has condition (artist changed) that gates execution; B has no such condition；A sets googleImageLocation to 0; B clears googleImages list；B updates UI components after fetching (enables button, sets album art); A does no UI update
- 修正建议: Incorporate method signature analysis (parameters, return type)；Use data flow analysis to track variable origins (internal vs parameter)；Detect side effects beyond common operations；Consider control flow differences (conditionals)

### case_id=4313 FN partial_functionality

- 方法: `main` vs `handler`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: A main method that constructs POST parameters, opens an HTTP connection, sends a POST request, and prints the response.
- B 摘要: A handler that takes a URL from target, reads its content line by line, and extracts substrings to populate a map.
- 静态失败原因: Static BERT models rely on lexical overlap (token Jaccard only 0.14) and surface syntax, and these functions have very different variable names, method signatures, and control flow. The shared pattern of URL reading is not captured without deeper dataflow or structural analysis.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider this a Type-4 clone because both functions contain the common pattern of opening a URL and reading lines, a distinct functional behavior. Annotators often accept broad semantic similarity even if the surrounding operations differ.
- 共享行为: Open a URL and read its content line by line using BufferedReader
- 行为差异: A uses HttpURLConnection with POST method; B uses URL.openStream (GET).；A constructs and sends a request; B directly reads from the URL.；A prints the response; B updates a map with extracted substrings.；A uses hardcoded parameters; B uses dynamic data from target object.
- 修正建议: Use graph-based or dataflow representations to capture common I/O patterns.；Include more diverse training examples of URL reading boilerplate.；Leverage code summarization or API sequence similarities.

### case_id=4314 FN benchmark_preference_bias

- 方法: `write` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Encrypts byte buffers using SSL/TLS, handling handshake and wrapping data.
- B 摘要: Builds a website by applying XSLT transformations to XML pages and writing output files.
- 静态失败原因: The low token Jaccard suggests no lexical overlap; the model correctly predicted non-clone (0), which aligns with the actual semantics, but BCB label is incorrect.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled as clone due to both functions processing input to produce an output, but the functionality is entirely different; likely an annotation error or overly permissive matching criteria.
- 行为差异: Function A deals with SSL encryption and byte buffers; Function B deals with web page generation and file I/O.；Function A returns encrypted ByteBuffer arrays; Function B returns void and writes files.；Function A handles SSL handshake statuses; Function B handles XML parsing and transformations.；Function A uses SSLEngine and NIO utilities; Function B uses Transformer, FileSystem, and StringBuffer.
- 修正建议: Verify BCB annotations for functions with low token similarity to correct false positives.；Use semantic similarity measures to adjust clone labels in the benchmark.

### case_id=4315 FP long_range_semantics

- 方法: `testCopy_readerToWriter_nullIn` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `static_summary_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Tests that IOUtils.copy throws NullPointerException when reader is null.
- B 摘要: Handles UI action events to configure settings like GraphViz path, image scaling, and look-and-feel.
- 静态失败原因: The model likely overfit on superficial features like null checks and file operations, or the long length of B made it difficult to capture full semantics, leading to false positive.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB labels non-clones when functions perform entirely different tasks and have no overlapping logic. Here, A is a unit test for an IO copy method, while B is a UI event handler for configuration settings.
- 共享行为: No meaningful shared behavior.
- 行为差异: A is a simple test for exception handling; B is a complex event handler with multiple conditionals.；A has no branching; B has many if-else blocks and UI updates.；A does not modify any state; B updates preferences and UI components.；A is short and focused; B is long and covers multiple unrelated commands.
- 修正建议: Improve model's ability to handle long methods by using better encoding or attention mechanisms.；Incorporate test method detection to separate test code from production code.

### case_id=4316 FN benchmark_preference_bias

- 方法: `decodeFileToFile` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Decodes a Base64-encoded input file to an output file using buffered I/O.
- B 摘要: Launches a NexOpen project configuration by validating project structure, processing XML files, setting Hibernate dialect, and performing project installation.
- 静态失败原因: Static BERT likely predicted non-clone correctly due to very low token overlap and different domains; the model accurately captures the semantic dissimilarity.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as a clone due to both functions involving file I/O with buffered streams, considering them as partial functionality clones (Type-4) under a broad interpretation of file processing.
- 共享行为: Both perform file reading and writing with buffered streams.；Both use try-catch-finally or resource management.；Both involve I/O operations with error handling.
- 行为差异: A is a simple file decoding utility; B is a complex Eclipse launch delegate.；A uses Base64 decoding; B does not.；A returns boolean success; B returns void and throws CoreException.；A operates on file paths; B operates on Eclipse workspace resources with XML processing and project management.
- 修正建议: Re-evaluate BCB label for this pair; likely a mislabeling.；If label is correct, incorporate functionality-level abstractions (e.g., recognize both as file I/O utilities) using semantic role labeling or program synthesis.

### case_id=4317 FN partial_functionality

- 方法: `getFile` vs `CopyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies the endpoint in the XML, and saves it to a local temp file.
- B 摘要: Copies a source file to a destination file, creating parent directories if needed.
- 静态失败原因: Static BERT likely focused on the shared FileChannel API and file I/O patterns, missing the high-level semantic difference between downloading and local copying.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as file copying routines because they both transfer data via FileChannel.transferFrom and return a file path, viewing the XML modification in A as an additional transformation.
- 共享行为: Use FileChannel.transferFrom for file data transfer；Return a file path string；Involve FileOutputStream and FileInputStream
- 行为差异: A involves network download and XML parsing/manipulation, B does not；A writes to a predetermined temp directory, B copies to user-specified destination；A handles multiple specific exceptions, B throws generic ones；A conditionally downloads based on file existence, B always copies
- 修正建议: Incorporate method naming and docstring semantics；Use data flow analysis to distinguish network vs local file sources；Add intermediate representation that captures overall task purpose

### case_id=4318 FN partial_functionality

- 方法: `runInternal` vs `startScript`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Opens an HTTP connection to load an OPDS catalog or download a book, parsing XML and handling pagination.
- B 摘要: Reads the content of a URL line by line and appends to a script string.
- 静态失败原因: The low token Jaccard similarity (0.0837) and large difference in length and API calls likely caused the model to focus on surface mismatches rather than the shared high-level behavior of URL reading.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label them as clones because both functions perform 'fetching content from a URL', a broad semantic pattern, and BCB tolerates partial functionality similarity for Type-4 clones.
- 共享行为: Both open a URL and read data from it；Both handle IOExceptions from network operations
- 行为差异: Function A uses HTTP-specific headers, redirect handling, and multiple data processing paths (XML parsing, book download) while Function B simply reads text lines；Function A has a loop for pagination and complex error reporting; Function B exits on error；Function A involves progress indication and background thread execution; Function B is synchronous and straightforward
- 修正建议: Enrich training with more examples of partial functionality clones；Incorporate data-flow or control-flow aware representations to capture core I/O patterns；Use contrastive learning to emphasize semantic similarity over lexical overlap

### case_id=4319 FN benchmark_preference_bias

- 方法: `doGet` vs `saveProject`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.4`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Handles HTTP GET request to retrieve and render a portal page with permission checks and caching.
- B 摘要: Saves a project to a zip file by creating directories and writing XML and binary data for types, databases, trajectories, and objects.
- 静态失败原因: Static BERT/GraphCodeBERT likely relied on low token Jaccard (0.10) and different method names, missing any subtle structural similarity that BCB might perceive; its attention over long code may not capture high-level functional overlap.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may label these as clones due to both being long methods with similar control flow patterns (if-else, loops), frequent I/O operations, and boilerplate code (logging, exception handling), fitting a broad Type-4 partial functionality similarity.
- 共享行为: Both involve writing output to a destination (HTTP response or file system).；Both include exception handling and logging.
- 行为差异: Different input parameters (HttpServletRequest vs File and Sets).；Different core logic: page retrieval and rendering vs project serialization.；Different error handling: HTTP error codes vs throwing IOException.；No overlap in domain-specific operations.
- 修正建议: Improve model sensitivity to control-flow and I/O patterns over long spans.；Incorporate domain-specific or role-based similarity metrics.；Re-annotate BCB data to reduce false positives from loose criteria.

### case_id=4320 FP lexical_or_api_overlap

- 方法: `getUser` vs `getRequestContent`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Loads a user from database or config file, parsing lines with colon-separated fields.
- B 摘要: Fetches the first line of content from a given URL via HTTP connection.
- 静态失败原因: The static model may have been misled by lexical overlap (URL, BufferedReader, readLine) and similar control flow (both have try-catch or exception handling patterns). Possibly the model saw both reading a line from a resource and considered them similar.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels as non-clone because the functionality is entirely different despite some shared API usage (BufferedReader, URL). The goal of getUser is authentication, while getRequestContent is fetching HTTP response.
- 共享行为: Both use BufferedReader to read line-oriented text input；Both use URL objects to open a connection to a resource
- 行为差异: Function A reads from a local config file or database, while B reads from a remote HTTP URL；Function A parses tokens and creates a User object, B simply returns the first line；Function A handles exceptions internally, B throws them to caller；Function A has a loop to read multiple lines, B reads only one line
- 修正建议: Improve the model's understanding of overall program intent rather than just local structure；Add more negative examples with similar API usage but different semantics；Use dataflow analysis to capture the different data transformations (User vs String line)

### case_id=4321 FN partial_functionality

- 方法: `copyResource` vs `decodeBody`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource from a URL or file path to a destination file using byte-by-byte I/O.
- B 摘要: Decodes an InputStream based on content transfer encoding and writes to a temporary file body, returning the body.
- 静态失败原因: The static BERT model likely relied on token overlap, method name similarity, and structural patterns. With low Jaccard similarity (0.15) and different method names, it missed the functional similarity in I/O copy operations. The model may not have captured data flow patterns across different contexts.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label these as clones because both functions share the core functionality of reading from an input stream and writing to an output stream, which is a common I/O pattern. Despite differences in source resolution and encoding, the fundamental data flow is similar, matching Type-4 partial clone criteria.
- 共享行为: Both read from an InputStream and write to an OutputStream.；Both handle I/O exceptions and close streams.；Both ultimately copy data from an input source to an output sink.
- 行为差异: copyResource resolves source from URL or local file; decodeBody receives InputStream directly.；decodeBody optionally applies content transfer decoding (quoted-printable or base64); copyResource does not transform data.；copyResource writes to a fixed destination file; decodeBody writes to a temporary file and returns a Body object.
- 修正建议: Train on more I/O copy examples with varying context.；Incorporate dataflow analysis to recognize read-write loops.；Use program slicing to focus on core behavioral patterns.

### case_id=4322 FP boilerplate_overlap

- 方法: `getLinksFromURLFast` vs `getXML`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Extracts links and link texts from an HTML page fetched from a URL using regex.
- B 摘要: Fetches XML content from a URL and returns it as a string, with URL encoding.
- 静态失败原因: The model likely over-weighted the common token patterns related to URL opening, BufferedReader, and while loop reading lines, which are typical boilerplate in network I/O functions. It failed to capture the semantic differences in the subsequent data processing steps.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: Despite some code overlap in the URL reading boilerplate, the core functionality is completely different (link extraction vs. XML retrieval). BCB annotators would recognize the distinct purposes and label as non-clone.
- 共享行为: Both open a URL connection, read lines using BufferedReader, and accumulate into a buffer.
- 行为差异: A parses HTML to extract links using regex; B performs URL encoding and returns raw content.；A returns two separate lists (links and texts); B returns a single concatenated string.；A prints debug messages and performs timing checks; B catches exceptions and returns null on failure.
- 修正建议: Incorporate more training examples that share I/O patterns but differ in core logic.；Use dataflow analysis or structural matching to differentiate post-processing steps.；Enhance model's ability to focus on function-specific logic rather than shared boilerplate.

### case_id=4323 FN partial_functionality

- 方法: `copyFromFileToFileUsingNIO` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Copies a file using NIO FileChannels with proper resource management.
- B 摘要: Launches a Hibernate configuration for a NexOpen project, handling Maven pom files and setting up reverse engineering files.
- 静态失败原因: The token Jaccard is very low (0.066), and the functions have few surface-level similarities. Static BERT models may rely heavily on token overlap and local patterns, missing the long-range structure and domain-specific semantics.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may incorrectly label as clone due to the presence of file I/O patterns in both, and the 'launch' method also contains file copying-like operations (e.g., copying resources from bundle). However, the overall functionality is vastly different.
- 共享行为: Both involve file I/O operations (streams and channels).；Both use try-catch-finally blocks to handle IOException.；Both close resources in finally blocks.
- 行为差异: Function A is a simple file copy; function B is a complex launch with project setup, annotation processing, and configuration management.；Function A uses NIO FileChannel; function B uses file streams, XML parsing, and property handling.；Function B has extensive branching and calls to Eclipse-specific APIs; function A is straightforward.
- 修正建议: Incorporate structure-aware embeddings or graph-based representations to capture control flow and data dependencies.；Use contrastive learning with negative examples that are syntactically similar but semantically different.；Improve handling of long sequences and domain-specific vocabulary.

### case_id=4324 FN lexical_or_api_overlap

- 方法: `readPage` vs `runScript`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.65`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a URL line by line, optionally skipping lines starting with '#', and returns the concatenated string.
- B 摘要: Reads a URL byte by byte using BufferedInputStream, concatenates characters into a string, and returns 'error!' on exception.
- 静态失败原因: Low token Jaccard (0.2) and different API usage (BufferedReader vs BufferedInputStream) cause static models to miss the semantic similarity in URL reading behavior.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB labels as clone because both functions fundamentally retrieve web content as a string, a common high-level pattern considered Type-4 or broad Type-3.
- 共享行为: Both read data from a URL and return it as a string
- 行为差异: readPage uses BufferedReader to read lines; runScript uses BufferedInputStream to read bytes；readPage can optionally skip comment lines (starting with '#'); runScript has no such filtering；runScript catches exceptions and returns 'error!'; readPage throws exceptions；readPage appends newline characters after each line; runScript does not
- 修正建议: Include data-flow analysis tracing input sources and output building；Use AST-based or graph-based representations to capture structural patterns of URL reading；Incorporate control-flow and exception handling abstraction for better generalization

### case_id=4325 FP dataflow_blindspot

- 方法: `readRemoteFile` vs `sendPost`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_with_trace`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a remote file via HTTP GET, returning the content as a string.
- B 摘要: Sends an HTTP POST request with parameters and returns the response as a string.
- 静态失败原因: The model over-relied on lexical and API overlap (URL, BufferedReader, InputStream, reading loop) and boilerplate, while missing the critical dataflow difference: the presence of PrintWriter and setDoOutput indicates a POST operation. This is a dataflow blindspot.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 dataflow_trace_and_outputs。
- BCB 偏好解释: BCB likely judges these as non-clones because the core functionality differs: one performs a read-only GET, the other performs a write-and-read POST. BCB typically requires significant functional overlap for Type-3/4 clones, and here the additional write operation is a key difference.
- 共享行为: Both open a URL connection and read the response line by line using BufferedReader.；Both return the concatenated response as a String.
- 行为差异: A uses a simple GET (no output data), B sends a POST with parameter data via output stream.；A catches EOFException and IOException separately; B catches all Exception broadly.；A reads first line outside loop; B reads all lines inside a while loop.
- 修正建议: Train the model to recognize differences in HTTP method (GET vs POST) by focusing on I/O operations like setDoOutput and PrintWriter.；Add more training examples where output stream usage distinguishes functionality.；Incorporate control flow and data dependency analysis to detect when a method writes to a stream vs only reads.

### case_id=4326 FP lexical_or_api_overlap

- 方法: `readZoneIDs` vs `retrieveQ`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a resource file line by line, parsing each line as an integer, and returns a set of integers.
- B 摘要: Fetches a URL and returns the entire response body as a single string, with error handling and output of response message.
- 静态失败原因: Static BERT/GraphCodeBERT likely overemphasized the lexical overlap of common API calls (URL, openConnection, readLine) and similar structural boilerplate, missing the deep semantic differences in how lines are processed and what is returned.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clone due to low functional similarity: different input/output types, different data transformations, and different error handling, despite a shared I/O pattern.
- 共享行为: Both open a URL-like resource and read it line by line.
- 行为差异: Input: zoneFileName (resource path) vs urlToRetrieve (full URL).；Output type: HashSet<Integer> vs String.；Line processing: Integer.parseInt vs string concatenation.；Error handling: catch-all printStackTrace vs throws specific exceptions.
- 修正建议: Incorporate data-flow analysis to track transformations of read lines (Integer vs String).；Focus on output type and purpose (collecting ints vs downloading content).；Use abstract syntax tree (AST) differences to highlight different loop bodies and return types.

### case_id=4327 FN partial_functionality

- 方法: `getFile` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies its endpoint attribute, and saves the modified file locally.
- B 摘要: Reads an input file, converts encoding and HTML entities based on command-line arguments, and writes to an output file.
- 静态失败原因: The static BERT/GraphCodeBERT model likely failed because it correctly identified the low token overlap and distinct specific semantics, but BCB's annotation preference for broad structural similarity caused a false negative. The model may have been too strict in requiring semantic equivalence rather than accepting partial functionality clones.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled these as clones due to both being 'file processing' utility methods with similar structural patterns: file existence check, file creation, stream handling, and exception handling. The partial functionality of downloading vs reading a file may be considered similar under broad Type-4 clone definitions that accept similar I/O operations.
- 共享行为: Both perform file I/O operations with File, InputStream, OutputStream classes.；Both check file existence before creating new files.；Both use try-catch blocks for exception handling.；Both contain loops for processing data.
- 行为差异: A downloads from a URL; B reads from a local file.；A modifies XML content; B does not modify content structurally.；A returns a string; B is void main method.；A uses custom exception AxisFault; B uses printUsage and generic Exception.
- 修正建议: Enhance the model to recognize structural I/O patterns (File, streams, existence checks) as a basis for clone detection even when domain logic differs.；Incorporate API usage patterns and control flow structure as features to capture broad functional similarity.

### case_id=4328 FN partial_functionality

- 方法: `postRequest` vs `register`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends an HTTP POST request with URL-encoded parameters and returns the response body as a string.
- B 摘要: Registers a User object by encoding password, setting default authority, creating a hash, making an HTTP GET request to a forum URL, persisting the user, and sending a confirmation email.
- 静态失败原因: Static BERT relies on token overlap and local syntax; here token Jaccard is low (0.188), and the common HTTP pattern is embedded within a much larger and different function in register, making it hard to capture the similarity. The model likely focused on overall semantics rather than the shared sub-task.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this as a clone because both functions perform an HTTP request (setup URLConnection, read input) which is a non-trivial common pattern, despite different overall purposes. BigCloneBench can accept broad Type-3/Type-4 similarity.
- 共享行为: Both functions open a URLConnection and read the response using BufferedReader.
- 行为差异: postRequest performs only an HTTP request and returns the response string; register involves many domain-specific steps beyond HTTP access.；postRequest uses POST method with output stream; register uses GET method with parameters in URL.；postRequest handles exceptions by printing stack trace; register logs errors and throws RuntimeException.；postRequest operates on generic HashMap; register operates on User object with specific fields.
- 修正建议: Incorporate program slicing to compare functional segments independently.；Use data-flow analysis to detect common API usage patterns such as URLConnection setup and reading.；Enhance representation with subgraph matching for partial functional overlap.

### case_id=4329 FP boilerplate_overlap

- 方法: `googleImageSearch` vs `parse`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Searches Google Images using a query string, downloads HTML, extracts image URLs, and updates a UI component with the first image.
- B 摘要: Parses a dataset from a file or URL using a tokenizer, handling headers, types, delimiters, and scientific notation, and returns a DataSet object.
- 静态失败原因: The model likely over-valued shared boilerplate patterns (e.g., opening streams, reading lines, exception handling) and ignored the distinct semantic purpose indicated by method names and core logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels non-clones when functions have fundamentally different purposes and only share generic I/O or error-handling patterns.
- 共享行为: Both use BufferedReader to read from a stream；Both handle exceptions with try-catch；Both perform string manipulation and parsing
- 行为差异: A performs an HTTP request to Google Images and extracts image URLs for UI display；B parses structured data with configurable delimiter, types, and headers；A updates UI components; B returns a DataSet object；A is specific to image search; B is a generic data parser
- 修正建议: Improve training to distinguish domain-specific logic from boilerplate；Incorporate method name semantics more strongly；Add negative examples with similar structure but different functionality

### case_id=4330 FN lexical_or_api_overlap

- 方法: `readGeoParserResult` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.98`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Parses geo-parser results by constructing an XML request, sending it via HTTP, parsing the XML response, and returning a collection of place-name tuples with optional gazetteer IDs.
- B 摘要: Reads a URL and prints each line of its content to standard output.
- 静态失败原因: A static BERT/GraphCodeBERT model may have been misled by the lexical overlap of common Java I/O patterns (URL, BufferedReader, while-read loop) and the same package imports. The model likely failed to capture the substantial structural and functional differences, especially the XML construction and parsing logic unique to function A.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB typically annotates Type-3/4 clones with partial functionality similarity. In this pair, the only overlap is generic URL reading infrastructure; the core logic and output behavior are entirely different. BCB would likely consider this a non-clone.
- 共享行为: Both use java.net.URL and BufferedReader to read from a URL.
- 行为差异: Function A constructs and sends an XML request, then parses an XML response; Function B simply reads raw text from a URL.；Function A retries on failure up to 3 times; Function B has no retry logic.；Function A returns a structured collection of tuples; Function B returns void and prints output to console.；Function A includes conditional logic for gazetteer IDs and handles XML namespaces; Function B has none of that.
- 修正建议: Train the model to focus on dataflow and control-flow dependencies rather than surface-level API usage.；Incorporate structural features like abstract syntax tree (AST) or program dependency graphs (PDG) to distinguish similar scaffold but different logic.；Use contrastive learning to penalize pairs that share only boilerplate I/O patterns.

### case_id=4331 FP boilerplate_overlap

- 方法: `actionPerformed` vs `test`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Handles GUI action events for setting file paths and preferences, updating UI state, and managing look-and-feel settings.
- B 摘要: Tests the StorageStringWriter class by writing, reading, and closing, verifying correct output and exception handling.
- 静态失败原因: The static model likely overfit to boilerplate patterns common in Java code, such as try-catch blocks, file chooser dialogs, string comparisons, and loops. Despite low token overlap, these superficial patterns triggered a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels this as non-clone because the functions have no meaningful semantic overlap: one is a complex GUI event handler, the other a focused unit test. Even under broad Type-4 partial similarity, they do not share core functionality.
- 行为差异: Function A is an event handler responding to multiple commands, involving file choosers and preference storage; Function B is a unit test exercising a storage class's methods.；Function A manipulates UI components and preferences; Function B validates stream and writer behavior.；No overlapping functionality; they belong to entirely different application layers.
- 修正建议: Incorporate data flow or control flow analysis to distinguish between event handling and testing logic.；Expand training data with more diverse examples to reduce reliance on generic structural templates.；Use method-level context such as class name or surrounding code to disambiguate purpose.

### case_id=4332 FP lexical_or_api_overlap

- 方法: `handler` vs `downloadFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a URL line by line, extracts substrings between given patterns, and updates a map for each line.
- B 摘要: Downloads a file from a URL to a local destination with progress reporting via MessageFrame.
- 静态失败原因: Likely due to lexical overlap of 'URL', 'openStream', 'Buffered', and similar while-loop structure, causing the model to overlook the distinct data processing logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels Type-3/Type-4 clones with partial similarity, but here the functionality is entirely different: one extracts substrings, the other downloads files. The only commonality is using URL and reading, which is too generic for a clone label.
- 共享行为: Both open a URL connection and read data from it.
- 行为差异: A reads lines and updates a map in memory; B writes raw bytes to a file.；A does string pattern matching; B does not.；B includes UI progress updates; A does not.；A returns void; B returns boolean.
- 修正建议: Enhance training to focus on functional intent rather than API usage.；Incorporate data flow and control flow analysis to differentiate in-memory vs file I/O.；Add contrastive examples with similar API structure but different semantics.

### case_id=4333 FN partial_functionality

- 方法: `fileDownload` vs `doVersionCheck`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a file from a given URL and saves it to a local directory.
- B 摘要: Reads a version check file from a URL and compares versions to notify user of updates.
- 静态失败原因: Static BERT model likely focused on the low token overlap and different method names and variable names, missing the abstract similarity of URL fetching and data reading. The model may have been misled by the different final purposes (file writing vs. version checking).
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both functions as clones because they share the core pattern of connecting to a URL, opening an input stream, and reading data, which is a significant functional similarity despite differences in what they do with the data.
- 共享行为: Open a URL and read from an input stream using BufferedReader
- 行为差异: A writes the downloaded content to a file; B parses lines for version and build info；A reads character-by-character; B reads line-by-line；A uses URLConnection; B uses URL.openStream() directly
- 修正建议: Incorporate high-level semantic categories or API usage patterns；Use dataflow analysis or control flow graph similarity；Enhance model with bytecode-level similarity

### case_id=4334 FP lexical_or_api_overlap

- 方法: `doVersionCheck` vs `getRequestContent`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Checks for a newer version of jEdit by reading a version file from a URL and parsing build numbers.
- B 摘要: Retrieves the first line of content from a given URL.
- 静态失败原因: The model likely overemphasized the shared API calls (URL, openStream, BufferedReader, InputStreamReader) and overlooked the significant differences in control flow, return type, and overall purpose.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the overall functionality is distinctly different despite shared URL reading; the core logic after reading diverges completely, and the context (UI, property loading) is specific to A.
- 共享行为: Both open a URL and read text input using BufferedReader and InputStreamReader.
- 行为差异: Different purpose: version check vs content retrieval.；A reads multiple lines and parses specific prefixes, B reads only the first line.；A returns void and has UI interaction (cursor), B returns a String.；Different exception handling: A catches IOException, B throws generic Exception.
- 修正建议: Train the model to differentiate between core functional similarity and incidental API overlap.；Incorporate structural features like control flow graphs and data dependencies.；Add negative examples where API usage is similar but semantics differ.

### case_id=4335 FP lexical_or_api_overlap

- 方法: `sendPost` vs `readUNI`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Sends an HTTP POST request with parameters and returns the response body as a string.
- B 摘要: Reads and parses a tab-separated file from a URL, extracting id and description pairs into a vector.
- 静态失败原因: Static BERT/GraphCodeBERT may have focused on high lexical and structural similarity (e.g., URL, InputStream, readLine, try-catch) and missed the semantic differences in data flow and method purpose, leading to a false positive clone prediction.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels non-clones when methods have different input/output behavior and purpose, even if they share common API usage patterns. Here, the functions serve distinct purposes (sending HTTP request vs parsing a file format) and produce different outputs, so BCB would consider them non-clones.
- 共享行为: Both open a URL connection and read text input line by line；Both handle exceptions with try-catch blocks
- 行为差异: A sends data via POST and reads response; B only reads (GET) and parses specific format；A returns a concatenated string; B populates a Vector；A uses HttpURLConnection with explicit IO streams; B uses URL.openStream() and Scanner；A uses BufferedReader; B uses Scanner with custom delimiter
- 修正建议: Incorporate method signature and return type as features to distinguish different input/output behaviors；Use data-flow analysis to differentiate POST vs GET operations and output destinations；Train on more diverse negative examples that share API usage but differ in functionality

### case_id=4336 FN benchmark_preference_bias

- 方法: `clonarFichero` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Copies a file from an input stream to a destination path using file channels.
- B 摘要: Builds a website for editing by reading XML, transforming with XSLT, and writing multiple output files per page.
- 静态失败原因: Static BERT models correctly predicted non-clone because of low token similarity and syntactic mismatch. The failure is in the BCB annotation, not the model.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might have incorrectly labeled this as a clone due to a focus on file I/O operations, but the functionalities are too different.
- 共享行为: Both involve reading from a FileInputStream；Both handle IOException；Both write to a file output stream/writer
- 行为差异: Function A is a straightforward file copy; Function B is complex with loops, XSLT, debugging；Function A writes a single file; Function B writes multiple files per page；Function B involves DOM parsing, string replacement, and properties
- 修正建议: Improve annotation consistency；Use stricter criteria for clones

### case_id=4337 FP partial_functionality

- 方法: `getWebByUrl` vs `loadURL`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a web page from a URL string, writes it to an indexed file, and recursively processes embedded URLs up to a depth limit.
- B 摘要: Downloads a URL with optional HTTP basic authentication, writes the content to a temporary file, and updates a status label with file size.
- 静态失败原因: Static BERT models may over-emphasize lexical overlap of common APIs (URLConnection, BufferedReader, while loop, file writing) and miss high-level semantic differences like authentication, recursion, and UI updates.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: Despite sharing the core pattern of fetching URL content and saving to file, the significant differences in authentication, recursion, output naming, and UI interaction likely led BCB to label as non-clone (Type-4 dissimilar).
- 共享行为: Both open a URL connection and read content line by line；Both write the read content to a local file using a Writer
- 行为差异: Function A downloads from a string URL, while B uses a URL object；A has no authentication; B supports basic authentication；A writes to a file named by an index; B writes to a temporary file；A recursively extracts and follows embedded URLs; B does not
- 修正建议: Use graph-based or data-flow-aware models to capture control flow and I/O dependencies；Incorporate functional similarity metrics that account for side effects and I/O patterns

### case_id=4338 FP lexical_or_api_overlap

- 方法: `readUNI` vs `checkForUpgrade`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a URL, parses tab-separated lines, and adds the id and description to a vector.
- B 摘要: Checks for software upgrades by querying a remote server, processing license information, and updating UI components.
- 静态失败原因: The static model likely overemphasized the shared lexical tokens (e.g., 'URL', 'openStream', 'close', 'Scanner', 'BufferedReader') and API usage patterns, ignoring the vastly different overall logic and domain.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would not consider these clones because they have completely different purposes, control flows, and outputs. The only superficial similarity is URL reading, which is insufficient for Type-3/Type-4 similarity.
- 共享行为: Both use URL and stream reading to fetch remote data.
- 行为差异: Function A parses local data from a URL and populates a vector; Function B handles upgrade logic including database, license validation, and UI updates.；Function A has no database or UI interactions; Function B extensively uses database commands and UI component manipulation.；Function A is a simple data reading method; Function B is a complex business logic method with multiple conditional branches.
- 修正建议: Incorporate data flow analysis to distinguish pure data reading from complex business logic.；Use graph-based models that capture structural dependencies beyond token overlap.；Add training examples with high API overlap but different semantics to reduce false positives.

### case_id=4339 FP lexical_or_api_overlap

- 方法: `addDataFromURL` vs `getLinksFromURLFast`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a URL line by line and appends each line to 'thetext', handling exceptions by appending the URL string.
- B 摘要: Fetches a web page from a URL, extracts all hyperlinks and anchor texts using regex, and returns them as two vectors.
- 静态失败原因: Static models like GraphCodeBERT may over-rely on lexical and structural patterns common to URL reading (e.g., URL, BufferedReader, readLine, try-catch) and miss high-level semantic divergence due to limited representation of data flow and long-range dependencies.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: Functions differ significantly in purpose (content aggregation vs. link extraction) and output structure, so BCB likely considers them non-clones despite shared URL reading boilerplate.
- 共享行为: Both open a URL and read its content line by line using BufferedReader and InputStreamReader
- 行为差异: Function A appends raw lines to a text buffer; Function B extracts links via regex and returns structured data；Function B performs URL parsing and absolute path conversion; Function A does not；Function B includes performance timing and debug output; Function A only has basic error handling；Function B returns a Vector array; Function A modifies an instance variable
- 修正建议: Augment training with contrastive examples that share API usage but have different intents；Incorporate flow-sensitive features to distinguish simple read vs. complex parsing；Use data flow analysis to capture output transformations and mitigate lexical false positives

### case_id=4340 FN benchmark_preference_bias

- 方法: `doTransfer` vs `doVersionCheck`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Forward HTTP request to another URL by copying headers and body, then returning the response.
- B 摘要: Read version information from a remote URL and trigger version check update.
- 静态失败原因: The model correctly identified non-clone, but BCB labeled as clone; model failed to align with BCB's broad clone definition.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider any functions with network I/O and stream handling as partial functionality clones, despite different purposes.
- 共享行为: Both open a URL and create an input stream；Both read from the input stream；Both handle IOException
- 行为差异: A writes to output stream and sets response headers; B extracts version strings and calls another method；A handles request headers and method; B shows/hides wait cursor；A uses HttpServletResponse; B uses View and GUIUtilities
- 修正建议: Adjust clone threshold to focus on functional equivalence rather than generic I/O patterns；Incorporate task-specific intent recognition

### case_id=4341 FP boilerplate_overlap

- 方法: `get` vs `getWebByUrl`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches game records from a URL using HTTP GET with location and count parameters, parses response into array of GameRecord objects.
- B 摘要: Downloads web page content to a file, recursively extracting URLs and reporting progress.
- 静态失败原因: Static BERT/GraphCodeBERT models may overemphasize lexical and structural overlap (e.g., URL.openConnection(), BufferedReader, try-catch) and miss the distinct output types and domain-specific processing, leading to false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely considered these non-clones because the core functionality differs: one is a structured data API client, the other is a generic web downloader with file output and recursion. The similarity in URL-reading boilerplate is not sufficient for clone label.
- 共享行为: Both open a URL connection and read lines from the input stream using BufferedReader.；Both handle exceptions with try-catch and print error messages.
- 行为差异: A returns an array of GameRecord; B writes raw HTML to a file and is void.；A sets custom HTTP headers (latitude, longitude, count); B does not use any headers.；B includes file output (PrintWriter), recursion (getUrlByString), and progress reporting (addReport); A does not.；A filters lines starting with '#' and decodes each line; B appends all lines to StringBuffer and writes to file.
- 修正建议: Incorporate data-flow analysis to distinguish between data retrieval and file storage.；Encode method signature, return type, and parameter usage into the representation.；Train on examples that differentiate similar boilerplate with different high-level tasks.

### case_id=4342 FN partial_functionality

- 方法: `main` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Demonstrates reading/writing a file with different encodings using Java NIO.
- B 摘要: Retrieves a resource as an InputStream, caching it locally if necessary, with HTTP handling.
- 静态失败原因: Static BERT models often rely on token overlap and local context. Here token overlap is low (0.106), but even if they had some overlap, the semantic intent differs. The model may have correctly identified them as non-clones.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have considered both as file I/O examples with similar boilerplate (opening files, reading/writing streams), but the core functionality is very different. Possibly the annotator saw overlapping API usage (FileInputStream, FileOutputStream, ByteBuffer) and labeled as Type-4 clone.
- 共享行为: Both involve file I/O operations；Both use ByteBuffer/InputStream/OutputStream；Both handle exceptions
- 行为差异: Function A is a self-contained main method for demonstration, while B is a utility method for resource retrieval；A writes and reads a fixed file, B retrieves a resource via URL and caches it；A focuses on encoding, B focuses on caching and HTTP
- 修正建议: Better training data with more diverse examples；Incorporate control flow and data flow analysis to distinguish different usage patterns

### case_id=4343 FP boilerplate_overlap

- 方法: `readZoneIDs` vs `doVersionCheck`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a file containing zone IDs, parsing each line as an integer, and returns a set of integers.
- B 摘要: Fetches a URL for version checking, parses lines for version and build strings, and displays update messages to the user.
- 静态失败原因: Static BERT models may have been misled by the common boilerplate pattern of opening a URL/stream and reading lines in a while loop, which is a frequent idiom in Java, causing a false positive despite different purposes.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels as non-clone because the overall functionality is completely different: one is a data extraction routine, the other is a UI-driven version check with conditional messaging. BCB favors semantic intent over structural similarity.
- 共享行为: Both open a URL or resource stream；Both read lines from the stream in a while loop；Both parse each line (though differently)
- 行为差异: Function A returns a set of integers; Function B updates UI and has no return value；Function A parses each line as integer; Function B checks for specific line prefixes (.version, .build)；Function B has conditional logic for version comparison and user notification；Exception handling differs: A prints stack trace; B shows error dialog
- 修正建议: Incorporate function name embeddings or broader context；Use dataflow analysis to capture different variable usage and return types；Include structural differences like method signature and control flow complexity

### case_id=4344 FN partial_functionality

- 方法: `getFile` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies its endpoint, and returns the local file path.
- B 摘要: Copies a file from source to destination, creating parent directories if needed.
- 静态失败原因: Static BERT models rely on token similarity and structural patterns; the low token Jaccard (0.13) and different method names made it focus on differences, missing the shared I/O pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB might label this as a clone (Type-4) because both functions involve file copying using the same NIO API (FileChannel.transferFrom), indicating a common sub-functionality.
- 共享行为: Both use FileChannel.transferFrom to copy data from an input channel to an output channel.
- 行为差异: getFile handles downloading from URL, XML parsing, and file renaming; copyFile is a straightforward file copy with exception wrapping.
- 修正建议: Use dataflow analysis to capture shared I/O operations.；Include call-graph information.；Augment training with examples of partial functional similarity.

### case_id=4345 FN lexical_or_api_overlap

- 方法: `main` vs `copy`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a URL and extracts its zip entries to files.
- B 摘要: Recursively copies files or directories using FileChannel.
- 静态失败原因: The static model likely over-relied on shared API tokens (e.g., FileInputStream, FileOutputStream, while loops) and generic I/O patterns, failing to capture the distinct control flow and purpose (unzipping vs. recursive file copy).
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB might have considered both as file copy operations because they both read from a source and write to a destination using I/O streams, but this overlooks the fundamentally different source types and extraction logic.
- 共享行为: Both involve file I/O operations using streams.；Both write data to output files.；Both use common Java I/O classes (FileInputStream, FileOutputStream).
- 行为差异: A reads from a remote HTTP URL and unzips archives; B copies local files directly.；A processes a single zip file containing multiple entries; B recursively copies a directory tree.；A uses ZipInputStream to extract; B uses FileChannel.transferFrom for efficient copying.；A writes entry names directly; B preserves directory structure and names.
- 修正建议: Incorporate data flow and control flow analysis to distinguish between reading from a URL/file vs. local file.；Use graph-based representations that capture the recursive vs. iterative nature of the loops.；Train on more diverse examples of file operations to avoid overgeneralization from shared API usage.

### case_id=4346 FP lexical_or_api_overlap

- 方法: `main` vs `extractZipFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Parses a Prolog file and generates adapter classes and a JAR file.
- B 摘要: Extracts entries from a zip file and updates a progress display.
- 静态失败原因: Static BERT models may have been misled by lexical overlap of common library classes (File, IOException, FileOutputStream) and boilerplate patterns (try-catch, file reading), ignoring the large structural and semantic differences.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would label this as non-clone because the two methods have completely different functionality and domain (Prolog adapter generation vs zip extraction) with no meaningful shared behavior beyond basic file I/O.
- 共享行为: Both methods read from files (Prolog file vs zip file)；Both use IOException handling
- 行为差异: Main method parses Prolog and generates Java classes; extractZipFile decompresses zip entries；Main method writes multiple output files (JAR, serialized data); extractZipFile writes only extracted files；Main method involves complex class generation and annotation processing; extractZipFile is a straightforward zip extraction
- 修正建议: Increase emphasis on method-level semantics rather than token overlap；Incorporate data flow analysis to distinguish different file processing pipelines；Train with more diverse negative examples to reduce false positives from common API usage

### case_id=4347 FN benchmark_preference_bias

- 方法: `readAndRewrite` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.2`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Reads a DICOM file, parses its dataset and pixel data, then writes the dataset and pixel data to an output file.
- B 摘要: Retrieves a resource by name from a URL, caches it locally if not already cached, and returns a FileInputStream to the cached resource, handling HTTP conditional requests.
- 静态失败原因: The static model predicted non-clone (0) correctly based on low token overlap (Jaccard 0.078) and distinct APIs. It failed to match the BCB label because BCB's annotation may have used a broader functional similarity (I/O pattern) that the model did not capture, leading to a false negative relative to the benchmark.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may label this as a clone due to both functions performing I/O operations that involve reading from an input source and writing to an output, with similar structural patterns (try-catch, stream handling). Under broad Type-3/Type-4 clone criteria, such similarity in task (I/O data transfer) albeit with different domains might be considered a clone, though this is a stretch.
- 共享行为: Both perform file I/O operations (opening, reading, writing streams).；Both use try-catch exception handling.；Both print debug messages.
- 行为差异: A processes DICOM-specific data structures; B handles HTTP caching and resource retrieval.；A writes to a specific output file; B returns an InputStream after local caching.；A uses DICOM libraries; B uses URL/HTTP classes.；A does not involve caching; B implements caching logic with conditional requests.
- 修正建议: Increase sensitivity to structural patterns like InputStream/OutputStream handling.；Use data flow similarity to capture I/O transformations.；Incorporate high-level task categorization from documentation or API usage patterns.

### case_id=4348 FN benchmark_preference_bias

- 方法: `setContenu` vs `modifyApplicationMessage`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Sets the content of a FichierElectronique from a ContenuFichierElectronique, copying bytes and updating metadata, with special handling for email files.
- B 摘要: Modifies a key-value pair in a localized properties file by reading, replacing or appending, and writing back.
- 静态失败原因: The static model (e.g., GraphCodeBERT) relies heavily on token overlap and semantic similarity of code snippets. The low token Jaccard (0.10) and completely different API calls (e.g., 'IOUtils.copy' vs. 'split("=")') likely led the model to predict non-clone. The model may fail to capture the abstract concept of 'file modification' that BCB might be using as a basis for clone labeling.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might consider these clones under a very broad Type-4 category of 'file processing functions' that both read from a source and write to a destination, despite the completely different domain and logic. However, this seems like a stretch and likely a false positive in the benchmark.
- 共享行为: Both involve file I/O (reading from a source and writing to a destination)；Both use try-catch-finally for resource management；Both check for null or existence before proceeding
- 行为差异: Function A copies the entire content of an input stream to an output stream, while Function B reads a properties file line by line and modifies one specific property.；Function A updates multiple metadata fields on the output file object, Function B does not update any metadata.；Function A handles special file extensions (.msg, .eml) to extract email metadata, Function B handles localization of properties files.；Function A uses InputStream/OutputStream, Function B uses FileReader/FileWriter and BufferedReader.
- 修正建议: Incorporate control-flow and data-flow graphs to capture structural similarities even when tokens differ.；Use function-level semantic embeddings that focus on purpose rather than implementation details.；Alternatively, reconsider the benchmark label as it may be a false positive, and train models to align with human judgment of strict semantic equivalence.

### case_id=4349 FN benchmark_preference_bias

- 方法: `writeFileType` vs `readData`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Reads a file of URIs, for each skips first num lines, then fetches the webpage and classifies it as OWL, RDFS, RDF, UNKNOWN, or BROKEN, writing results to an output file.
- B 摘要: Reads a configuration file for Tibetan transliteration, parses lines into tokens, and populates various sets and hashes (topSet, leftSet, vowelSet, etc.) with the parsed data.
- 静态失败原因: In this case, the static model correctly predicted non-clone (0) because the token overlap is very low (0.108) and the API usage differs significantly beyond basic I/O. The model did not fail; it correctly identified the lack of semantic similarity.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB likely labeled this pair as a clone due to a very broad interpretation of 'file processing' or 'data ingestion', but the functional semantics are entirely disjoint; this appears to be an annotation error or a case of benchmark preference bias towards type-4 clones that share only superficial structure.
- 共享行为: Both read from files using BufferedReader；Both iterate over lines of input；Both use String splitting/tokenization in some form
- 行为差异: writeFileType fetches webpages via URL; readData solely parses local configuration data；writeFileType writes output to a file; readData populates in-memory data structures；writeFileType performs HTTP I/O and content classification; readData builds lookup tables for Tibetan transliteration；writeFileType has explicit error handling for URL exceptions; readData throws errors for malformed config lines
- 修正建议: Re-annotate this pair as non-clone in BCB to avoid misleading benchmark results.；Use more rigorous functional criteria that require shared essential logic, not just file I/O.；Consider filtering pairs with very low token similarity and no common high-level operations.

### case_id=4350 FN benchmark_preference_bias

- 方法: `convert` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Converts an ACRNEMA image stream to DICOM format, including UID assignment and pixel data handling.
- B 摘要: Launches an Eclipse launch configuration for a NexOpen project, processing Maven POM files and Hibernate dialect settings.
- 静态失败原因: Static BERT did not fail; it correctly predicted non-clone due to low token overlap (Jaccard 0.058) and lack of semantic similarity. The BCB label appears incorrect from a functional equivalence standpoint.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled as clone due to both methods performing a 'conversion' task (image conversion vs. project configuration conversion) and both involving file reading/writing, but this is a stretch; likely a benchmark labeling error or overly broad Type-4 criterion.
- 共享行为: Both use file I/O streams and try-finally blocks for resource management
- 行为差异: Code A deals with medical image format conversion; Code B handles Eclipse project configuration and Maven builds；Code A generates and assigns UIDs; Code B does not；Code A manipulates pixel data; Code B manipulates XML documents and properties
- 修正建议: Re-evaluate BCB label for this pair; if truly non-clone, static model is correct；If BCB label is considered ground truth, model needs to capture abstract task similarity like 'conversion' across domains, but that may be undesirable

### case_id=4351 FN benchmark_preference_bias

- 方法: `descargarArchivo` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Copies a file from one location to another using FileChannels.
- B 摘要: Launches an Eclipse launch configuration for a NexOpen project, handling Maven pom files and setting up Hibernate reverse engineering.
- 静态失败原因: Static model correctly predicted non-clone; BCB label appears erroneous, so the model did not fail.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have incorrectly labeled this as a clone due to annotation noise or a mistaken partial functionality judgment, but there is no obvious shared behavior beyond generic file handling.
- 共享行为: Both involve file I/O operations, but the contexts and purposes are completely different.
- 行为差异: Function A is a simple file copy; function B is a complex Eclipse plugin launch configuration setup.；Function A has no parameters; function B has multiple parameters including ILaunchConfiguration and IProgressMonitor.；Function A uses FileInputStream/FileOutputStream; function B uses ByteArrayOutputStream, Properties, IFile, etc.；Function B deals with Maven projects, XML parsing, and persistent properties; function A does not.
- 修正建议: Re-evaluate the BCB label for this pair; likely a false positive in the benchmark.；If the model must be improved, ensure training data has finer-grained annotations to avoid such mismatches.

### case_id=4352 FN partial_functionality

- 方法: `readReferenceText` vs `read`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a reference text file from a URL using an identifier, returns content as a string, throws NoContentException on failure.
- B 摘要: Reads a file from a URL or local path, returns integer status code, updates internal stream and status.
- 静态失败原因: Static BERT/GraphCodeBERT likely relied on token overlap and method signatures, which are low (Jaccard=0.2) and different, missing the abstract functional similarity in reading from a URL due to lack of deep dataflow or semantic understanding.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled these as clones under Type-4 (functional similarity) because both functions perform reading from a URL/stream, demonstrating similar I/O patterns and exception handling, despite different return types and overall purpose.
- 共享行为: Both open a stream from a URL；Both read input data；Both use standard Java I/O classes (InputStreamReader, BufferedReader, etc.)
- 行为差异: Return type: String vs int；Error handling: exceptions vs status codes；First reads lines into a StringBuffer and returns the full text, second delegates to an overloaded read method and returns a status；First only handles URLs, second handles both URLs and local files
- 修正建议: Train models to recognize high-level I/O patterns independent of return type；Incorporate dataflow analysis to track stream opening and reading operations；Use code summarization to capture core intent (e.g., 'read from URL')

### case_id=4353 FP partial_functionality

- 方法: `readURL` vs `loadURL`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads lines from a URL and prints each line to standard output.
- B 摘要: Reads a URL with optional authentication, writes content to a temporary file, and updates a status label with file size.
- 静态失败原因: Static BERT likely focused on overlapping API usage (URL, BufferedReader, InputStreamReader, readLine, etc.) and similar control flow structure (try-catch, while loop), ignoring the larger differences in authentication, file writing, and UI updates. The overlapping tokens and structural similarity misled the model.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB labeled non-clone because the overall functionality diverges significantly: one is a simple URL reader that prints, the other is a file downloader with auth and UI feedback. The common pattern of reading lines from a URL is not enough to consider them clones given the distinct purposes and side effects.
- 共享行为: Both open a URL connection and read lines using BufferedReader
- 行为差异: Function A only prints lines to console; Function B writes to a file；Function B handles authentication (username/password); Function A does not；Function B updates a UI status label; Function A has no UI interaction；Function B throws IOException; Function A catches all exceptions and prints stack trace
- 修正建议: Include more features capturing functional side effects like file I/O and authentication；Use data-flow analysis to trace how content is consumed (e.g., print vs write to file)；Enhance training data with more varied non-clone pairs that share API calls but differ in overall behavior

### case_id=4354 FP lexical_or_api_overlap

- 方法: `googleImageSearch` vs `sendRequestObjectResponse`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Performs a Google image search by sending an HTTP GET request and parsing image URLs from the HTML response.
- B 摘要: Sends an XML request to a servlet via HTTP, receives a response, saves it to a file based on content type, and opens the file in a browser.
- 静态失败原因: Static BERT models may overemphasize common API tokens (URL, HttpURLConnection, BufferedReader) and exception handling patterns, ignoring the overall semantic difference.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels these as non-clones because they perform completely different tasks despite some superficial API overlap.
- 共享行为: Both use HTTP connections；Both handle exceptions with try-catch
- 行为差异: Different HTTP methods (GET vs POST with output)；Different response processing (parse HTML for image URLs vs save to file and show)；Different return types (void vs String)；Different configurations (User-Agent vs GZIP, content-type)
- 修正建议: Incorporate structural features like control flow and data flow；Use abstract syntax tree (AST) or code graph representations；Add attention to long-range dependencies and overall purpose

### case_id=4355 FN partial_functionality

- 方法: `retrieveTemplate` vs `seeURLConnection`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Retrieves a blog template from a dynamic URL, caches it, and returns the string.
- B 摘要: Reads a hardcoded URL, builds a string, and logs it.
- 静态失败原因: The static model likely relied on lexical overlap, which was low (0.319), and focused on differences in method name, return type, and caching logic, missing the common pattern of URL reading and string aggregation.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often considers Type-3/Type-4 clones where the core functionality (reading URL and building string) is similar, even if I/O targets and caching differ.
- 共享行为: Both read from a URL using BufferedReader and InputStreamReader；Both concatenate lines into a single string via append in a loop
- 行为差异: A returns the string, B logs it and returns void；A caches the result, B does not；A uses dynamic URL from blogEditor, B uses hardcoded URL；A is private, B is public
- 修正建议: Use higher-level semantic representations that capture I/O and string-building patterns；Incorporate dataflow analysis to identify similar loops and I/O operations；Train on BCB-style annotations that allow partial functionality clones

### case_id=4356 FN partial_functionality

- 方法: `main` vs `run`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a KMZ file (zip) from a URL or file and extracts all entries to local files.
- B 摘要: Parses XML, creates a XUL Firefox extension package by writing multiple zip entries with specific content (resources, menu script, icons).
- 静态失败原因: Static BERT relies heavily on token overlap, which is low (0.103). It fails to capture high-level functional similarity like 'zip manipulation' due to different APIs, method names, and string literals.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB values structural patterns: both methods involve zip stream creation, entry iteration, and buffer-based writing, so they are considered functionally similar (broad Type-4).
- 共享行为: Both handle zip archives (input or output).；Both iterate over zip entries.；Both perform file I/O operations.
- 行为差异: A extracts from an existing zip; B creates a new zip.；A reads from URL/file; B reads XML from a Reader.；A writes to individual files; B writes to a zip stream.；A has no XML or resource management; B has complex XML parsing and resource embedding.
- 修正建议: Use dataflow or graph-based representations to capture zip-related operations.；Include API call context and type information.；Augment training with pairs that have partial functional overlap.

### case_id=4357 FP partial_functionality

- 方法: `getButtonSonido` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Creates a button that opens a file chooser to select a sound file, copies it to a project directory, and updates the button icon.
- B 摘要: Handles various action commands for setting application preferences, including file choosers for selecting executable paths and a large block of settings.
- 静态失败原因: The model may have been misled by the shared use of JFileChooser, ActionListener, and similar GUI patterns despite low token overlap, failing to capture the divergent high-level purpose and control flow.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely considers these non-clones because the core functionality differs significantly; the shared file chooser usage is a common GUI idiom, not indicative of semantic equivalence.
- 共享行为: Both use JFileChooser to open a file selection dialog；Both are triggered by user action (button click or action command)
- 行为差异: Different domains: sound file setup vs application configuration；Different file operations: copy file vs store path only；Different number of handled cases: one vs many commands；Different GUI updates: change icon vs set text fields and enable/disable components
- 修正建议: Use graph-based code representations to capture control and data flow；Include method-level context like class and field information；Train on more diverse examples to reduce overreliance on common API calls

### case_id=4358 FN partial_functionality

- 方法: `loadSourceCode` vs `register`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Loads a source code file, applies syntax highlighting, and returns an HTML string.
- B 摘要: Registers a new user by encoding password, setting authorities, creating a forum user via HTTP, persisting to database, and sending confirmation email.
- 静态失败原因: Static BERT/GraphCodeBERT likely focused on the overall semantics and high-level method names, missing the partial overlap in I/O handling. The low token Jaccard and different method names caused the model to classify them as non-clones.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this as a clone due to the common pattern of opening a URL and reading lines with a BufferedReader, which is a non-trivial shared behavior, despite overall different functionality.
- 共享行为: Both open a URL and read lines via BufferedReader within try-catch blocks.；Both handle IOExceptions or general exceptions.
- 行为差异: Function A reads a local file via URL resource, while B creates an HTTP connection to a remote forum.；Function A only reads and highlights source code, whereas B performs complex user registration logic including database operations and email sending.；Function A returns void, B returns boolean indicating email send success.；Function A catches a general Exception, B catches IOException and NumberFormatException specifically.
- 修正建议: Train the model to recognize sub-task clones by leveraging data-flow or control-flow graphs.；Use techniques that capture partial functionality similarity, such as program slicing or graph matching.；Include more examples of Type-4 clones with partial functionality overlap in training data.

### case_id=4359 FP lexical_or_api_overlap

- 方法: `readReferenceText` vs `getFullScreenUrl`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a reference text file from a plugin resource by constructing a URL from a filename and returning its contents.
- B 摘要: Fetches a YouTube page, parses the response to extract video parameters, and constructs a full screen URL.
- 静态失败原因: The model likely overemphasized the lexical overlap in URL reading and buffering patterns, misinterpreting them as semantically equivalent.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels these as non-clones because their functionality is entirely different (reading a resource file vs. extracting a YouTube URL), despite sharing some boilerplate URL reading code.
- 共享行为: Both functions read from a URL using BufferedReader and handle IO exceptions.
- 行为差异: Function A reads all lines and appends them; Function B searches for a specific line containing 'fullscreenUrl'.；Function A throws NoContentException on failure; Function B catches Exception and returns an empty string.；Function A takes an identifier as input; Function B uses an instance variable ytUrl.
- 修正建议: Provide more negative examples with similar API usage but different semantics.；Use dataflow analysis to distinguish the purpose of reading (e.g., all lines vs. specific pattern).

### case_id=4360 FN lexical_or_api_overlap

- 方法: `addIDs` vs `GetResponse`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Parses HTML from a specific URL to extract metabolite IDs and molecular weight, setting row properties.
- B 摘要: Fetches text content from a generic URL via HTTP GET and returns it as a string.
- 静态失败原因: Static BERT models typically rely on token-level similarity and code structure features. The low Jaccard index (0.16) and different API usage (URL vs HttpURLConnection) lead to low token overlap. The model fails to recognize the high-level functional similarity of HTTP reading and line-by-line processing, which is not captured by local token patterns.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: None
- 共享行为: Both open an HTTP connection to a URL；Both read the response line by line using BufferedReader
- 行为差异: Function A constructs the URL from a name parameter and parses HTML for metabolite data; Function B takes a URL directly and returns raw content；Function A sets multiple row properties (e.g., molecular weight, PubChem ID); Function B only returns the concatenated response string；Function A has extensive parsing logic and multiple conditional branches; Function B is a simple read loop；Exception handling differs: A logs using Logger, B prints stack trace
- 修正建议: Incorporate API usage patterns and common data flow (e.g., URL opening, BufferedReader) as features；Use graph-based models that capture control and data flow independently of token overlap；Consider functional similarity via program embedding or natural language summaries

### case_id=4361 FN partial_functionality

- 方法: `runInternal` vs `wordFrequency`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads and parses an OPDS catalog from a URL, handling pagination and downloading books.
- B 摘要: Extracts word frequency from a web service by replacing a placeholder in a URL and parsing the response line by line.
- 静态失败原因: Static BERT models like GraphCodeBERT rely heavily on token overlap and structural similarity; since the Jaccard similarity is very low (0.097) and the code structure differs significantly, the model failed to capture the high-level functional similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label these as clones because both methods follow the pattern of fetching data from a URL and processing it, representing a Type-4 (semantic) clone where the overall intent is similar despite different implementations.
- 共享行为: Both perform HTTP GET requests to a URL；Both read the response stream line by line；Both extract information from the response (XML parsing vs regex matching)
- 行为差异: Function A handles complex OPDS catalog pagination and book downloading, while function B simply returns a frequency integer；Function A uses HTTP headers and connection setup extensively, function B uses default URLConnection；Function A includes error handling for various HTTP responses, function B only catches exceptions
- 修正建议: Improve the model to recognize common programming patterns like HTTP resource fetching, even when token overlap is low.；Incorporate behavioral signatures or API call sequences to detect semantic clones.

### case_id=4362 FN partial_functionality

- 方法: `readGeoParserResult` vs `readVersion`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends a record content to a geo-parser service via HTTP, parses XML response to extract place names and associated IDs, with retry mechanism.
- B 摘要: Reads a version resource file from classpath, parses lines for Version, Revision, and Date strings, and sets corresponding instance variables.
- 静态失败原因: The model likely relied on token-level similarity (low Jaccard = 0.13) and failed to capture the higher-level structural pattern of stream reading and parsing shared by both functions, leading to a false negative.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this as a clone because both functions follow a common pattern: open a stream, read text data, parse it to extract specific fields, and handle exceptions. This structural similarity qualifies as a broad Type-3 clone despite different domains.
- 共享行为: Both open a stream (URL.openStream vs ClassLoader.getSystemResource).；Both use BufferedReader to read lines from the stream.；Both parse the read data to extract specific information (XML elements vs key-value lines).；Both handle IOExceptions and perform cleanup (retry loop vs finally block).
- 行为差异: Input source: HTTP request vs classpath resource file.；Output: returns Collection of Tuples vs sets instance fields (version, revision, compileDate).；Parsing: XML DOM parsing vs line-by-line string splitting.；Error handling: retry loop up to 3 times vs single try-catch-finally.
- 修正建议: Use graph-based models that capture control and data flow structures.；Include negative examples with similar I/O patterns but different semantics to teach models to distinguish partial similarity as still a clone.；Augment training data with more broad clones that share common structural idioms.

### case_id=4363 FP boilerplate_overlap

- 方法: `get` vs `run`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Performs HTTP GET with custom headers to fetch and parse GameRecord objects from server response.
- B 摘要: Connects to a fixed URL and reads response line by line without any processing or return.
- 静态失败原因: The static model likely overemphasized the shared lexical and syntactic patterns (URL, BufferedReader, readLine, try-catch) and missed the semantic differences in header usage, data parsing, and return types.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels as non-clone because the methods have fundamentally different purposes: one is a data-fetching and parsing utility, the other is a simple read without processing.
- 共享行为: Both open HTTP connections and read response line by line；Both handle IOException
- 行为差异: A sets custom headers (latitude, longitude, count) while B does not；A parses lines to create GameRecord objects; B discards all lines；A returns an array or null; B returns void；A checks HTTP response code and prints message on failure; B does not check response code
- 修正建议: Incorporate dataflow analysis to track how parameters and headers affect behavior；Consider return types and method signatures as discriminative features；Use dependency-based features to capture the role of the method in the larger program context

### case_id=4364 FN partial_functionality

- 方法: `copyResource` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource from a URL or local file to a destination file byte by byte.
- B 摘要: Processes a zip file, extracts entries, writes them to temp files, parses them to create rule lists, and evaluates performance.
- 静态失败原因: The model likely relied on lexical and structural overlap, which is low (Jaccard 0.14), and the dissimilar method names and contexts led to non-clone prediction. It may not have recognized the common I/O pattern as significant.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled as clone because both contain a common byte-copying loop pattern, but this is too superficial and not sufficient for functional equivalence.
- 共享行为: Both use a while loop to read from an input stream and write to an output stream.
- 行为差异: Different overall purposes: copying vs. evaluation pipeline.；Different input sources: URL/file vs. zip entries.；Different output processing: direct file write vs. further parsing and evaluation.；Function A has error handling for missing resource; B has command-line argument handling and zip traversal.
- 修正建议: Improve model to consider overall semantic purpose rather than small shared sub-patterns.；Introduce better abstraction for common boilerplate patterns to avoid false positives.

### case_id=4365 FN partial_functionality

- 方法: `copy` vs `getFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.75`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a local file from source to destination with pre-checks and buffer I/O.
- B 摘要: Downloads a WSDL file from a URL, optionally modifies XML endpoint, and saves to temp directory.
- 静态失败原因: The semantic difference is large (local copy vs. network download + XML processing), and token overlap is low. The model likely focused on method names and overall control flow, which differ significantly, leading to a non-clone prediction.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider them clones due to shared file I/O patterns (open stream, read/write, close) and error handling structure, despite different high-level purposes. The annotation could reflect Type-3/Type-4 similarity where partial functionality (file writing) is considered sufficient for cloning.
- 共享行为: Both use FileOutputStream to write data to a local file.；Both perform file existence checks and handle errors.；Both use try-catch or finally blocks for stream management.
- 行为差异: Method A copies a local file; method B downloads from a URL.；Method B includes XML parsing and modification; method A does not.；Method B has extensive logging and exception handling for AxisFault; method A uses abort() and IOExceptions.；Method B returns a file path; method A is void.
- 修正建议: Include more context about the method's purpose (e.g., comments, class context) in training.；Use dataflow-sensitive models to capture that one method reads from a network link, not a local file.；Filter training data to ensure clones have not just structural but also high-level semantic alignment.

### case_id=4366 FP boilerplate_overlap

- 方法: `register` vs `perform`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Registers a player into a Minecraft server session after verifying name using MD5 hash and checking constraints.
- B 摘要: Processes a web request to classify a concept by building XML, calling an external service, and storing results in session.
- 静态失败原因: A static BERT/GraphCodeBERT model might have been misled by superficial structural similarities such as the use of common control flow patterns (if-return, try-catch, loops) and common identifiers like 'session', despite the low token Jaccard. The model may have overfit to boilerplate patterns rather than understanding the distinct domain semantics.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels as not clone because the two functions perform completely different domain tasks (Minecraft game session management vs web-based concept classification). Even though both involve session handling and validation, their core functionality is entirely different, so BCB's annotation preferences would not consider them Type-3/Type-4 clones.
- 共享行为: Both functions perform input validation and error handling；Both use a session object to manage state
- 行为差异: Function A registers a player in a Minecraft server, while function B classifies a concept in a web application；A uses MD5 hash verification; B uses XML and HTTP POST to an external service；A operates on a Minecraft session; B operates on an HTTP session；A sends login responses and gzips level; B sets session attributes and forwards to a result page
- 修正建议: Improve the model's ability to capture domain-specific semantics；Add more negative examples with similar structural patterns but different functionality；Consider using data flow or control flow graphs to differentiate unrelated tasks；Increase token-level discriminative features like method names and context

### case_id=4367 FP boilerplate_overlap

- 方法: `getRandomGUID` vs `perform`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Generates a random GUID using MD5 hashing with optional secure randomness.
- B 摘要: Handles a web request to classify a concept by interacting with a remote service and managing session attributes.
- 静态失败原因: Static BERT likely overfitted to boilerplate patterns (e.g., 'StringBuffer', 'try-catch') and missed the distinct task semantics due to low token overlap and lack of understanding of long-range dependencies.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels non-clones when functions have entirely different purposes and no semantic overlap; these two functions share no common functionality.
- 共享行为: Both use try-catch blocks for exception handling；Both utilize StringBuffer for string construction
- 行为差异: Code A performs cryptographic hashing for GUID generation; Code B processes HTTP requests and responses；Code A is a private utility method; Code B is a public Struts action handler；Code A has no external dependencies; Code B uses numerous web application classes (HttpSession, ActionMapping, etc.)；Code A produces a hash string; Code B produces an ActionForward result
- 修正建议: Incorporate dataflow or control-flow information to capture functional behavior；Use contrastive learning with harder negatives to reduce sensitivity to common boilerplate

### case_id=4368 FN boilerplate_overlap

- 方法: `addIDs` vs `createHTML`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.85`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Retrieves metabolite information from a web service for a given name and populates a PeakListRow object with various IDs and molecular weight, returning a score.
- B 摘要: Constructs an HTML page string by reading a CSS file and optionally including dynamic content from database queries based on a page type.
- 静态失败原因: The model likely focused on low lexical overlap (Jaccard=0.1449) and correctly identified the methods as non-clones, but the human annotation considered them clones based on broad structural similarity; the model did not align with the annotation preference.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB annotators might consider the boilerplate I/O patterns and string processing as sufficiently similar for a broad Type-3/Type-4 clone, despite the different functional domains.
- 共享行为: Use BufferedReader to read input line by line；Handle IOException with try-catch；Perform string manipulation and concatenation；Have a try-catch block
- 行为差异: A reads from a URL (network I/O), B reads from a classpath resource；A parses HTML to extract data, B builds HTML；A modifies a passed object (PeakListRow), B returns a string；A has complex conditional logic for different ID types, B uses a switch on page type
- 修正建议: Incorporate high-level task understanding to differentiate between data retrieval and HTML generation；Use data flow analysis to capture different output types and side effects

### case_id=4369 FP lexical_or_api_overlap

- 方法: `actionPerformed` vs `main`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: GUI event handler that processes various preference settings such as file paths for external tools and look-and-feel options.
- B 摘要: Main method that copies all files from a source directory to a destination directory using NIO file channels.
- 静态失败原因: Static models may over-rely on surface-level API overlap (e.g., both use File class) and boilerplate patterns (if-else checks) in the long code_a, missing the semantic differences.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would label these as non-clones because they have no functional similarity; one is a GUI action handler and the other is a file copy utility.
- 行为差异: Function A handles GUI events and updates UI components; Function B runs a file copy operation.；Function A has complex conditional logic for multiple commands; Function B has a simple loop over files.；Function A interacts with user preferences and settings; Function B has no user interaction.；Function A uses JFileChooser and Swing components; Function B uses FileInputStream/FileOutputStream and FileChannel.
- 修正建议: Use a model that captures longer-range semantic structure.；Incorporate program dependency graphs or data flow analysis.；Apply a similarity threshold to reject low Jaccard pairs.

### case_id=4370 FN lexical_or_api_overlap

- 方法: `logging` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Logs an inbound message by processing headers, encoding, and content stream, then writing to a buffer and logging.
- B 摘要: Downloads a KMZ file from a URL, extracts its zip entries, and writes each entry to a file.
- 静态失败原因: The token Jaccard similarity is very low (0.107), and the API calls (e.g., InterceptorWrapper vs ZipInputStream) are completely different. Static BERT models rely on lexical and syntactic overlap, failing to capture abstract semantic patterns like stream copying.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB annotators may have considered these as Type-4 (functionally similar) clones because both implement a common pattern: read from an input stream, process, and write to an output stream, with error handling. The high-level dataflow structure is similar despite different domains.
- 共享行为: Both read from an InputStream and write to an OutputStream；Both handle I/O exceptions；Both involve stream processing with buffering
- 行为差异: Different purpose: logging vs. file extraction；Different data sources: message object vs. URL；Different output: log message vs. file system；Different error handling: throws Fault vs. throws Exception
- 修正建议: Use data-flow or control-flow representations to capture stream processing patterns；Augment training data with pairs that share structural similarity but differ in domain-specific APIs；Incorporate program slicing or abstract syntax trees to generalize beyond surface tokens

### case_id=4371 FP lexical_or_api_overlap

- 方法: `importRoles` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Imports role names from an XML file retrieved via URL.
- B 摘要: Searches Google Images for album art and extracts image URLs.
- 静态失败原因: The model likely overemphasized the lexical overlap of common API calls (URL, BufferedReader, while loop), mistaking boilerplate for semantic similarity.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels non-clones when functions have different semantic intents, even if they share some boilerplate code. Here, the purposes are entirely different.
- 共享行为: Both open a URL and read lines using BufferedReader
- 行为差异: Different data extraction logic；Different output types (RoleName list vs. image URL list)；Different error handling；Function B has a state check (artist comparison) before execution
- 修正建议: Use models that focus on core logic transformation rather than API surface；Incorporate data flow and dependency analysis to differentiate actual processing

### case_id=4372 FN partial_functionality

- 方法: `copyFile` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Copies a file using NIO FileChannel.
- B 摘要: Builds a website for editing by transforming XML and writing output files.
- 静态失败原因: GraphCodeBERT likely relied on low token-level similarity (Jaccard 0.06) and did not capture the broad functional category of file I/O, leading to a false negative.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as file I/O utility methods within a broader system, accepting Type-4 semantic similarity due to shared file operations.
- 共享行为: Both involve reading from and writing to files (FileInputStream, FileOutputStream/FileWriter).；Both handle IOException.
- 行为差异: A is simple file copy; B is complex site generation with XML parsing and string manipulation.；A is static utility; B is instance method of PageSet with many parameters.；A uses FileChannel.transferFrom; B uses custom FileSystem and char buffers.；A has no loops; B has loops over pages and conditionals.
- 修正建议: Improve model's ability to capture partial functional overlap (e.g., via multi-label classification or soft matching).；Incorporate dataflow or API usage patterns beyond lexical similarity.

### case_id=4373 FP lexical_or_api_overlap

- 方法: `getUser` vs `readUNI`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Authenticates a user by loading from DAO or parsing a colon-delimited config file from the classpath.
- B 摘要: Reads tab-separated data from a URL and collects id-description pairs into a vector.
- 静态失败原因: Static BERT models may over-rely on lexical and API-level overlap (e.g., URL, openStream, parse loops) without capturing deeper functional differences, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically requires at least Type-3 similarity where code structures are mostly identical with minor changes; these methods have distinct functionalities and signatures, so they are labeled non-clone.
- 共享行为: Both read from a URL using openStream()；Both parse lines of text from the input；Both handle exceptions with try-catch
- 行为差异: Different parsing delimiters (colon vs tab)；Different outputs (User object vs vector of strings)；Different data sources (classpath resource vs arbitrary URL)；Different logic (matching a specific login vs collecting all entries)
- 修正建议: Incorporate data-flow and control-flow features to distinguish different usage patterns；Use contrastive learning with negative samples that have high API overlap but different semantics；Enforce signature and return type matching in clone detection

### case_id=4374 FP boilerplate_overlap

- 方法: `getFrameworkFactory` vs `postXml`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a service configuration file from classpath and dynamically loads an OSGi framework factory class.
- B 摘要: Sends an HTTP POST request with XML content and returns the response string.
- 静态失败原因: The model likely focused on common boilerplate code: both functions have try-catch, BufferedReader, InputStreamReader, and a while loop reading lines. The structural similarity of reading from a stream may have overshadowed the differing core logic. Additionally, both mention 'URL', which might have confused the model into thinking they are similar.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels these as non-clones because they implement completely different high-level functionalities. The shared low-level I/O patterns are insufficient for clone classification in BCB, which requires functional similarity.
- 共享行为: Both use BufferedReader and InputStreamReader to read text from an input stream line by line.；Both have a loop that reads lines until null.
- 行为差异: Function A loads a class from a configuration file; Function B sends an HTTP request and reads response.；Function A throws Exception if factory not found; Function B throws RuntimeException on IOException.；Function A uses Class.forName and newInstance; Function B uses URLConnection and sets HTTP headers.；Function A does not involve network I/O; Function B does.
- 修正建议: Train the model to distinguish between reading from a local resource versus a network connection.；Incorporate data flow analysis to track the source and destination of data.；Use contrastive learning with pairs that share API calls but differ in purpose.；Enrich input with method name and class context to disambiguate functionalities.

### case_id=4375 FP partial_functionality

- 方法: `readData` vs `copyToDir`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.75`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Parses comma-separated string constants and a file to populate multiple sets and lookup tables for Tibetan transliteration.
- B 摘要: Copies a source file to a target directory, creating the directory if needed, and updates the internal file reference.
- 静态失败原因: Static BERT/GraphCodeBERT might have overfitted to surface-level patterns like both methods containing 'File', 'InputStream', 'OutputStream', or 'IOException', or misinterpreted the truncated long method A as a data-reading routine similar to B's file reading, despite different semantics.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely labels these as non-clones because they perform entirely different tasks (data initialization vs. file copying) with no shared functionality beyond superficial I/O usage.
- 共享行为: Both perform file I/O operations and handle IOException
- 行为差异: Function A parses and initializes data structures; Function B copies a file byte by byte；Function A has complex control flow with error handling for column counts; Function B has simple sequential copy；Function A modifies multiple global sets; Function B modifies only the internal file reference
- 修正建议: Improve training with more contrastive examples of I/O-related but semantically distinct methods；Use data flow analysis to differentiate between file parsing and file copying；Handle long methods with better truncation or hierarchical representations

### case_id=4376 FP boilerplate_overlap

- 方法: `scrapeForIsbns` vs `getVersion`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Scrapes a web page for ISBN-10 matches with retry logic and counts matches.
- B 摘要: Retrieves a version string from a fixed URL with no retry.
- 静态失败原因: Static BERT/GraphCodeBERT likely overemphasized the common boilerplate (URL opening, BufferedReader loop) and missed the distinct operations (pattern matching vs simple assignment) and different parameters/return types.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels non-clone because the functions serve fundamentally different purposes (ISBN scraping vs version retrieval) despite both reading URLs. The partial behavior overlap (reading a URL) is not enough for BCB-style clone acceptance.
- 共享行为: Both open a URL and read its content line by line；Both use BufferedReader and InputStreamReader；Both handle exceptions (IOException, etc.)
- 行为差异: A takes a URL parameter, B uses a hardcoded URL；A matches a regex pattern, B just assigns the entire line；A has retry logic, B does not；A counts matches and stores in a map, B returns a string
- 修正建议: Add more focus on API calls beyond I/O boilerplate, like Pattern usage vs variable assignment；Incorporate structural differences in control flow (retry loop vs simple try-catch)；Use data-flow analysis to distinguish between counting vs returning a single value

### case_id=4377 FN partial_functionality

- 方法: `copyResource` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource from a URL or file to a destination file byte by byte.
- B 摘要: Reads a file from a given position and copies remaining bytes to another file, handling command-line arguments.
- 静态失败原因: The models likely focus on token sequences and missed the abstract similarity of copy loops due to low lexical overlap (0.168) and different structures (e.g., B has offset parsing).
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels pairs as clones if they share a common core behavior (copying bytes) despite different contexts, considering them as Type-3/4.
- 共享行为: Both copy bytes from an input stream to an output stream using a loop
- 行为差异: B handles a skip offset before copying; A does not；B uses command-line arguments for file names and offset; A uses instance variables；B prints progress messages; A does not；B uses buffered streams; A uses unbuffered streams
- 修正建议: Enhance model with dataflow analysis to identify common I/O patterns；Add training examples of partial functionality clones

### case_id=4378 FN partial_functionality

- 方法: `copyResource` vs `decodeFileToFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource (URL or file) to a destination file by reading single bytes.
- B 摘要: Decodes a Base64-encoded input file to an output file using buffered streams.
- 静态失败原因: Low token Jaccard (0.197) and different method names/signatures led to high lexical dissimilarity, obscuring the shared read-write loop structure.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often annotates broad Type-3/Type-4 clones based on overall file-copying functionality, accepting variations in buffering and transformation.
- 共享行为: Both open an input stream and an output stream to files.；Both read data from input and write to output until end-of-stream.；Both close streams in a finally-like pattern.
- 行为差异: A reads byte-by-byte; B reads into a buffer (65536 bytes).；A does not transform data; B applies Base64 decoding.；A throws an exception on resource failure; B returns a boolean success flag.；A handles both URL and local file as source; B only reads from a local file.
- 修正建议: Enhance representation to capture abstract syntax tree patterns of stream I/O loops.；Use data flow analysis to identify input-to-output copy operations.；Train on BCB's broad clone definition with contrastive learning on structural similarities.

### case_id=4379 FN partial_functionality

- 方法: `logging` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.4`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Logs inbound message details including encoding, headers, and payload, using an InterceptorWrapper and CachedOutputStream.
- B 摘要: Retrieves a resource as an InputStream with caching, handling HTTP connections and file I/O.
- 静态失败原因: Static BERT/GraphCodeBERT methods rely heavily on token and lexical overlap, which is very low (Jaccard 0.09). They fail to capture the functional similarity at a higher level of I/O stream copying and exception handling, which requires understanding of dataflow and API semantics beyond surface-level tokens.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled them as clones due to a broad interpretation of Type-3/4 clones, focusing on the common pattern of reading from an InputStream and writing to an OutputStream, along with similar exception handling and logging, despite different domain-specific purposes.
- 共享行为: Both functions handle reading from an InputStream and writing to some output (buffer or file).；Both contain exception handling with try-catch blocks and stream closing.；Both perform some form of logging or printing (logger vs System.out).
- 行为差异: Purpose: Function A logs messages; Function B downloads and caches resources.；Function A modifies the message content; Function B manages a cache directory and file timestamps.；Function A uses framework-specific classes (InterceptorWrapper, LoggingMessage); Function B uses standard Java IO and networking.；Function A writes to a String buffer; Function B writes to a file and returns a FileInputStream.
- 修正建议: Incorporate dataflow analysis to detect stream-copying patterns.；Use abstract syntax trees (AST) to capture structural similarity in exception handling.；Enhance training with examples of functional similarity despite low token overlap.

### case_id=4380 FN partial_functionality

- 方法: `read` vs `handledRun`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Opens an input stream from a given name (URL or file) and returns a status after reading.
- B 摘要: Connects to a remote server to check and download updated game data if needed, using URL.openStream and writing to a file.
- 静态失败原因: Static BERT/GraphCodeBERT methods likely failed due to low token overlap (Jaccard=0.134) and large structural differences. The model focused on exact token matches and control flow differences, missing the shared core functionality of reading from a URL.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label these as clone because both functions involve opening a URL input stream and handling I/O exceptions, which is a common pattern. In BigCloneBench, partial functionality similarity, especially for I/O operations, is often considered a clone.
- 共享行为: Both use URL.openStream() to fetch data from a network resource.；Both handle I/O exceptions.
- 行为差异: Function A is generic; B is specific to a fixed URL and filename.；A only reads; B conditionally writes to a file.；A returns an int status; B is void.；B has version checking logic; A does not.
- 修正建议: Train with more examples that have partial functional similarity but low token overlap.；Incorporate data flow analysis to capture common API usage patterns (e.g., URL.openStream).；Use graph-based representations that highlight shared subgraphs.

### case_id=4381 FP boilerplate_overlap

- 方法: `getJSONData` vs `checkForUpgrade`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches JSON data from a URL and returns it as a JSONObject.
- B 摘要: Checks for software upgrades by querying a remote server, updating UI visibility, and inserting upgrade records into a database.
- 静态失败原因: The model likely over-relied on overlapping lexical tokens such as 'BufferedReader', 'InputStreamReader', 'URL', 'while ((line = in.readLine())', leading to false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled these as non-clones because their core functionality is entirely different despite sharing boilerplate HTTP networking code.
- 共享行为: Both make HTTP connections and read response line by line using BufferedReader.；Both use try-catch for exception handling.
- 行为差异: Function A returns a JSONObject; Function B performs UI updates and database operations and returns void.；Function A parses JSON; Function B parses a custom XML-like response and processes upgrade information.；Function B contains complex conditional logic for status checks and database transactions, absent in A.
- 修正建议: Include data-flow analysis to distinguish core logic from boilerplate I/O.；Train with more negative examples that share common I/O patterns but differ in purpose.；Add features capturing function signature, return type, and exception signatures.

### case_id=4382 FP lexical_or_api_overlap

- 方法: `readPage` vs `getUser`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a web page from a URL, optionally ignoring comment lines starting with '#', and returns the entire content as a string.
- B 摘要: Retrieves a User object by login name, first checking a database; if not found, reads a configuration file from classpath to find matching credentials, creates and saves the User.
- 静态失败原因: The static model likely overemphasized common API tokens (URL, BufferedReader, readLine) and the loop structure, mistaking them for functional similarity. The low token Jaccard (0.25) suggests other features (e.g., graph embeddings) may have captured irrelevant structural commonalities.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clone because the overall functionality is vastly different (web page fetching vs user authentication), even though both share low-level I/O patterns. BCB typically requires semantic similarity in what the function does, not just how it does it.
- 共享行为: Both open a resource (URL in A, URL from classpath in B) and use BufferedReader to read line by line in a loop.
- 行为差异: A reads arbitrary web pages and returns raw HTML; B reads a specific config file, parses tokens separated by ':', and conditionally creates a User object.；A has optional comment filtering; B has error handling and saves the user.；A returns a String; B returns a User object (or null).
- 修正建议: Incorporate higher-level semantic features like method name, class context, or data flow.；Use type information and call graphs to distinguish purposes.；Include training examples where similar I/O patterns appear in unrelated tasks.

### case_id=4383 FN benchmark_preference_bias

- 方法: `getFile` vs `uncaughtException`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.98`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Downloads a WSDL file from a URL, modifies its endpoint, and saves it to a temporary directory.
- B 摘要: Handles an uncaught exception by showing an error dialog and optionally opening a bug report URL.
- 静态失败原因: The model correctly predicted non-clone. The BCB label appears to be an error or an overly broad annotation. Therefore, the model did not fail; the benchmark annotation is inconsistent.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled these as clones based on a very broad interpretation of 'error handling' or 'utility methods', but there is no functional similarity.
- 行为差异: Function A performs file I/O and XML manipulation; Function B shows a GUI message box.；Function A deals with WSDL service configuration; Function B handles uncaught exceptions in an SWT application.；Function A returns a file path; Function B has no return value.；Function A throws AxisFault; Function B does not throw exceptions.
- 修正建议: Re-evaluate the BCB annotation for this pair to correct the label.；Improve BCB annotation guidelines to avoid overly broad matches.；Consider filtering out pairs with very low token similarity.

### case_id=4384 FP boilerplate_overlap

- 方法: `MD5` vs `perform`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Computes MD5 hash of a string and returns hex representation.
- B 摘要: Performs Struts action processing including session validation, form handling, and external HTTP request response parsing.
- 静态失败原因: The model likely overemphasized common Java boilerplate (try-catch, throws, return statements) and missed the entirely different domain logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB focuses on functional similarity; these functions share no common functionality, so they correctly label as non-clones.
- 共享行为: Both use basic Java exception handling and return a value
- 行为差异: One is a stateless hash function, the other is a stateful web request handler；A uses MessageDigest; B uses Struts API and HTTP；A returns String; B returns ActionForward
- 修正建议: Enhance model to capture high-level semantic intent beyond syntax；Incorporate functional categorization or API usage patterns；Use more robust representation learning to distinguish utilities from complex business logic

### case_id=4385 FP boilerplate_overlap

- 方法: `main` vs `copyFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Main method that parses a Prolog file, generates adapter classes and resources, and writes them into a JAR file.
- B 摘要: Utility function that copies a file using NIO FileChannel and returns success status.
- 静态失败原因: Static BERT/GraphCodeBERT may have been misled by overlapping file-related keywords (File, IOException, try-catch) and boilerplate exception handling, overlooking the semantic difference.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled as non-clone because the functions have completely different functionality and structure, despite superficial file-handling similarities.
- 共享行为: Both perform file I/O operations；Both handle exceptions with try-catch blocks
- 行为差异: Different purposes: adapter generation vs. file copying；Different APIs: Prolog parser, ClassWriter vs. FileChannel；Different control flow: complex conditional logic vs. simple sequential；Different output: writes JAR vs. copies file
- 修正建议: Use more robust semantic embeddings that capture program purpose beyond API tokens；Incorporate structural analysis like data flow or call graphs；Increase training data with diverse examples of false positives from file-handling boilerplate

### case_id=4386 FN partial_functionality

- 方法: `readAndRewrite` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Reads a DICOM file, parses it, reads pixel data, and writes it to an output file with encoding.
- B 摘要: Builds a site for editing by reading XML files, transforming them with XSLT, and writing multiple output files with string replacements.
- 静态失败原因: The static BERT/GraphCodeBERT method correctly identified them as non-clones due to very low token overlap (Jaccard 0.036) and distinct API usage, but BCB label disagrees, so the model's prediction aligns with strict semantics.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BigCloneBench may have considered these as clones under Type-4 (semantic) due to both being file-processing routines that read, transform, and write data, despite vastly different domains and APIs.
- 共享行为: Both involve reading from input sources and writing to output destinations.；Both use file I/O and handle IOException.；Both perform some form of data transformation.
- 行为差异: Function A processes DICOM medical image data; Function B processes XML and HTML web pages.；Function A uses DICOM-specific APIs (DcmParser, Dataset, PixelDataReader/Writer); Function B uses XML transformers and string replacement utilities.；Function A has a single input file and single output file; Function B iterates over multiple pages and produces multiple output files.；Function A has a fixed encoding (IVR_LE); Function B uses UTF-8 and replaces URLs.
- 修正建议: Train on more diverse Type-4 clones that share only abstract behavior.；Incorporate data-flow analysis to differentiate domain-specific operations.；Use fine-tuned representations that capture high-level semantics beyond token overlap.

### case_id=4387 FP other

- 方法: `saveAttachmentBody` vs `readData`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Saves an email attachment body to a file and updates the database with file size and content URI.
- B 摘要: Reads configuration data from a file to initialize various character sets and mappings for Tibetan script processing.
- 静态失败原因: The model likely relied on superficial similarities like both being static methods with long bodies and having IOException handling (B has a catch), or it may have hallucinated due to low token Jaccard and no clear distinguishing cues, leading to a false positive.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB labels these as non-clones because they have entirely different functionality and no structural overlap; even under broad Type-4 they are unrelated.
- 共享行为: Both are static methods；Both use I/O operations (though B uses StringTokenizer and file reading)
- 行为差异: A performs file output and database update; B performs parsing and set population；A handles attachment data; B handles character encoding data；A uses Part and ContentValues; B uses StringTokenizer and HashSets
- 修正建议: Improve model sensitivity to high-level semantics by incorporating domain-specific features；Increase training data with contrasting pairs from different application domains

### case_id=4388 FN lexical_or_api_overlap

- 方法: `readGeoParserResult` vs `File2String`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.4`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a record content, sends an XML query to a geo-parsing service, parses the response XML to extract place names and associated gazetteer IDs, and returns a collection of tuples with retry logic.
- B 摘要: Reads a file from the filesystem or classpath into a string, with fallback to classpath and error handling that exits the program.
- 静态失败原因: Low token overlap (0.144), different domain-specific vocabulary, and different overall task (file I/O vs. network service call) lead the model to classify them as non-clones.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may consider the shared pattern of reading input from a stream line by line and accumulating into a buffer as a sign of partial functional similarity, despite different purposes.
- 共享行为: Both use BufferedReader to read input line by line and append to a StringBuffer；Both handle I/O exceptions
- 行为差异: A builds and sends an XML request to a remote service, parses XML to extract structured data, has retry logic, and returns a collection of tuples；B reads a local file, has fallback to classpath, and returns a plain string; also calls System.exit on failure
- 修正建议: Improve model's ability to recognize abstract I/O patterns；Use dataflow/code structure features (e.g., GraphCodeBERT) to capture control flow similarity；Use clone detection that focuses on high-level functional behavior (e.g., input-output transformations)

### case_id=4389 FP lexical_or_api_overlap

- 方法: `actionPerformed` vs `copyFromTo`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Handles action commands in a GUI settings panel, updating preferences and UI components.
- B 摘要: Copies a file from source to destination using FileChannel with error handling.
- 静态失败原因: Static BERT likely focused on overlapping API tokens (e.g., File, IOException) and common Java constructs, ignoring the overall context and control flow.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels as non-clone because the functions have completely different purposes and logic, with no semantic similarity.
- 共享行为: Both involve file operations (dialogs vs. copying)
- 行为差异: Function A is event-driven GUI logic; Function B is a file I/O utility.；A updates configuration and UI; B solely copies file content.；A involves user interaction; B is automated.；No overlap in core functionality.
- 修正建议: Enhance model with data flow or control flow analysis.；Use AST-based features to distinguish boilerplate patterns from core logic.；Incorporate function purpose classification as additional signal.

### case_id=4390 FN partial_functionality

- 方法: `copyFile` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Copies a file using FileChannel transfer with proper resource cleanup.
- B 摘要: Launches a NexOpen project configuration in Eclipse, performing XML handling, property setting, and reverse engineering file generation.
- 静态失败原因: Low token overlap (0.057) and very different method names/structures, with complex Eclipse-specific tokens in code_b that are out-of-distribution, causing the model to miss the trivial file copy similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label them as clone due to a single shared file copying step (IOUtils.copy in launch, FileChannel.transferTo in copyFile) and try-finally resource management, but the overall functionality is entirely different.
- 共享行为: Both involve file I/O operations；Both handle InputStream/OutputStream for data copying
- 行为差异: copyFile is a simple file copy utility with no dependencies; launch is a complex Eclipse launch delegate with many API calls；copyFile uses FileChannel.transferTo; launch uses IOUtils.copy and other streams；launch has extensive error handling, project setup, and configuration logic；copyFile has only source and destination parameters; launch has Eclipse-specific objects
- 修正建议: Improve detection of partial functionality similarities；Incorporate structural analysis to identify common sub-patterns like resource copying；Use semantic models that capture file I/O operations regardless of surrounding context

### case_id=4391 FP lexical_or_api_overlap

- 方法: `handleHandshake` vs `doVersionCheck`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Handles a Minecraft handshake packet by validating a server key and optionally making an HTTP request to join a session.
- B 摘要: Performs a version check by fetching a version file from a URL and comparing builds.
- 静态失败原因: Static BERT models may have focused on overlapping API usage (URL, BufferedReader, InputStreamReader) and control flow patterns, ignoring the domain-specific logic and different purposes.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would not consider them clones because they perform entirely different tasks in different domains, despite both using URL reading.
- 共享行为: Both open a URL and read lines from an input stream；Both handle exceptions with error messages
- 行为差异: Different input types (Packet2Handshake vs View)；Different core logic: validation/parsing of hex key vs parsing version strings；Different output actions: sending network packets vs showing UI messages；Different domain: Minecraft game vs jEdit editor
- 修正建议: Add attention to domain-specific tokens；Incorporate dataflow analysis to distinguish different variable usages；Use contrastive learning to emphasize semantic differences over syntactic overlap

### case_id=4392 FN benchmark_preference_bias

- 方法: `getFile` vs `unzipEntry`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.6`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, optionally modifies its endpoint attribute, and saves it to a temporary location.
- B 摘要: Extracts a single entry from a zip file to an output directory, creating directories as needed.
- 静态失败原因: Token overlap is very low (0.08) and functions differ in method names, control flow, and APIs; a static model relying on lexical and syntactic features would not detect the high-level semantic similarity of data copying.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: None
- 共享行为: Both read binary data from an input source and write it to an output file.；Both are static methods performing file I/O.；Both handle exceptions.
- 行为差异: getFile downloads from a network URL; unzipEntry reads from a local zip file.；getFile includes XML parsing and attribute modification; unzipEntry does not.；getFile uses NIO channels (FileChannel.transferFrom); unzipEntry uses buffered streams and IOUtils.copy.；getFile has conditional logic to skip download if file exists; unzipEntry always extracts.
- 修正建议: Incorporate data flow analysis to identify common I/O patterns.；Use a model that can abstract away from specific APIs to high-level operations like 'copy from input to output'.；Include structural similarity of try-catch patterns or resource handling.

### case_id=4393 FN benchmark_preference_bias

- 方法: `main` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Copies a file from input to output starting at a given offset via command-line arguments.
- B 摘要: Builds a site for editing by processing pages, transforming XML, and writing output files.
- 静态失败原因: The functions have low lexical overlap (Jaccard 0.07) and distinct contexts; static BERT correctly predicted non-clone, so the model did not fail; the BCB label is questionable.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have considered both as file I/O operations, but the functional intent and complexity are vastly different; the label likely reflects a broad Type-4 interpretation or annotation error.
- 共享行为: Both perform file reading and writing operations.
- 行为差异: Function A is a simple file copy utility; Function B is a complex site builder with XML transformations and multiple file interactions.；Function A has no loop over pages or XML handling; Function B processes a vector of pages and uses XSLT transformers.；Function A uses byte-level copying; Function B uses character buffers and String manipulation.
- 修正建议: Re-evaluate BCB annotation for this pair to ensure consistency with functional equivalence.；If aiming for strict clones, filter out pairs with high complexity mismatch.

### case_id=4394 FN benchmark_preference_bias

- 方法: `testCopy_readerToOutputStream_Encoding` vs `getFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: A test method that copies a Reader to an OutputStream with a specified encoding and verifies content equality.
- B 摘要: A utility method that downloads a WSDL file, modifies its endpoint location in the XML, and saves it to a temporary file.
- 静态失败原因: Static BERT correctly predicted non-clone; it did not fail. The mismatch is due to an erroneous BCB positive label, not model error.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled as clone due to very broad Type-4 similarity of both performing stream-based I/O, but this is too generic and likely a labeling error.
- 共享行为: Both involve I/O operations with streams for reading/writing data
- 行为差异: Completely different purposes: unit test vs. production download utility；Different operations: encoding conversion vs. file download and XML manipulation；Different exception handling: test throws Exception, utility throws AxisFault；Different output: test asserts equality, method returns file location
- 修正建议: Re-evaluate BCB ground truth for this pair；Exclude such dissimilar pairs from training or adjust clone definition

### case_id=4395 FP lexical_or_api_overlap

- 方法: `sendPost` vs `getFrameworkFactory`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Sends an HTTP POST request with parameters and returns the response body as a string.
- B 摘要: Reads a service configuration file from the classpath and instantiates the FrameworkFactory class.
- 静态失败原因: Static BERT/GraphCodeBERT likely over-emphasized the token overlap ('url', 'BufferedReader', 'readLine', etc.) and the common pattern of reading from a URL, while missing the critical semantic difference that one writes to the connection and the other does not, and they return entirely different types.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would label this as non-clone because the functions have completely different goals and outputs. The superficial similarity in reading lines from a URL is not sufficient for functional similarity under BCB's Type-3/4 criteria.
- 共享行为: Both open a URL and read lines using BufferedReader.；Both iterate through lines reading one by one.；Both use try/catch or throws for exception handling.
- 行为差异: sendPost writes data to the output stream, while getFrameworkFactory only reads from an input stream.；sendPost returns concatenated response string; getFrameworkFactory returns a FrameworkFactory instance or throws exception.；sendPost catches Exception and prints message; getFrameworkFactory declares throws Exception and uses try-finally.；sendPost uses HttpURLConnection with properties; getFrameworkFactory uses url.openStream() directly.
- 修正建议: Incorporate dataflow analysis to distinguish read vs write operations on streams.；Enhance model with type information to differentiate return types and parameter usage.；Introduce contrastive learning examples with high token overlap but different semantics.

### case_id=4396 FN lexical_or_api_overlap

- 方法: `login` vs `import_hints`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Login to LOLA by sending encoded credentials via HTTP POST and extracting session ID from response.
- B 摘要: Import puzzle hints from a file or URL by reading and parsing piece placement data.
- 静态失败原因: Static BERT models rely heavily on token-level lexical overlap and API patterns. Here token Jaccard is very low (0.167), and the domain-specific operations (login vs. puzzle piece parsing) appear distinct, causing the model to miss the structural I/O similarity.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may consider these as Type-4 clones because both involve retrieving data from a URL, parsing it, and handling I/O exceptions, sharing a high-level behavioral pattern of data acquisition and processing.
- 共享行为: Both use URL and BufferedReader to read data from a URL；Both have try-catch exception handling with return on failure；Both output messages via System.out.println；Both return a value indicating success or extracted data
- 行为差异: A sends HTTP POST with output stream; B only reads input stream；A encodes form data; B reads tokenized integer data；A extracts session ID; B places pieces on a board；A returns String; B returns boolean
- 修正建议: Incorporate structural features like I/O patterns (e.g., use of URLConnection, BufferedReader) in the model；Use data flow analysis to trace input/output operations and abstract away domain-specific details；Train on more diverse Type-3/Type-4 clones to recognize high-level behavioral similarity

### case_id=4397 FN benchmark_preference_bias

- 方法: `main` vs `writeData`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a KMZ from URL, unzips it, and extracts entries to files.
- B 摘要: Writes a formatted table of data (peaks, dates) to a text file using PrintWriter.
- 静态失败原因: The model likely relied on token overlap and structural similarity, which were low (Jaccard 0.147); it failed to recognize the broad behavioral overlap of file I/O that BCB may have considered sufficient for a partial clone.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have considered them clones due to both performing file output operations and using loops, despite very different domains and logic; possibly a misannotation or an overly broad interpretation of Type-3/Type-4 clones.
- 共享行为: Both involve file I/O operations (writing to files)；Both use loops to iterate over data
- 行为差异: Function A reads from a URL and extracts zip entries; Function B generates and writes structured tabular data；Function A creates multiple output files; Function B writes to a single file；Function A handles network and ZIP streams; Function B handles date formatting and peak matching；Function A prints entry names; Function B prints test content to stdout
- 修正建议: Clarify and tighten clone definition in the benchmark to exclude such disparate functionalities；Use semantic analysis that focuses on data flow and API usage patterns rather than surface-level syntax

### case_id=4398 FN partial_functionality

- 方法: `copyResource` vs `copy`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copy a resource (URL or file) to a destination file using byte-by-byte I/O.
- B 摘要: Copy a source file to a destination file using NIO FileChannel.transferFrom.
- 静态失败原因: Static BERT models rely on lexical and API similarity. The token Jaccard is low (0.19), and the APIs differ (InputStream vs FileChannel, byte-by-byte vs transferFrom). The model fails to capture the higher-level semantic equivalence of copying.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels similar functional behavior as clones, even with different implementations. Both functions serve the purpose of copying a source to a destination, which is the core functionality, so they are considered Type-3/Type-4 clones under BCB guidelines.
- 共享行为: Both copy data from a source to a destination file.；Both close input and output streams/channels after copying.；Both handle file existence checks (A checks file existence, B checks null).
- 行为差异: A accepts a resource (URL or file) as source; B only accepts File.；A uses byte-by-byte stream reading/writing; B uses NIO FileChannel.；A throws generic Exception; B throws specific FileNotFoundException and IOException.；B creates parent directories of destination; A does not.
- 修正建议: Train models on clone pairs with diverse implementations but same high-level purpose.；Incorporate data flow and control flow information to capture intent.；Use code summarization or docstring matching to align functional goals.

### case_id=4399 FP lexical_or_api_overlap

- 方法: `readData` vs `logging`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Parses comma-separated strings from static fields into various sets and validates input sequences, including reading a file to populate lookup tables for Tibetan transliteration.
- B 摘要: Logs the encoding, headers, and payload of an inbound message, with truncation if the payload exceeds a size limit.
- 静态失败原因: The static BERT model might have been misled by the presence of common Java constructs (try-catch, while loops, String operations) and a similar overall structure, despite low token Jaccard similarity.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled non-clone because these functions have no semantic or syntactic similarity; they serve entirely different purposes in different domains (Tibetan text processing vs. web service logging).
- 共享行为: Both methods perform data processing involving iteration over tokens or streams.；Both use error handling (IOException, throw clauses).；Both are void methods.
- 行为差异: A builds static data structures (HashSets) and reads from static fields and a file; B operates on a message object and logs to logger.；A is for configuration initialization; B is for logging at runtime.；A uses StringTokenizer and HashSet; B uses InputStream, CachedOutputStream, and IOUtils.
- 修正建议: Incorporate method name and context to better capture domain-specific semantics.；Use program analysis to differentiate between configuration parsing and logging.；Train on more diverse negative examples to avoid false positives from superficial API overlap.

### case_id=4400 FP boilerplate_overlap

- 方法: `run` vs `retrieveQ`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Downloads and processes a map tile from a URL, handling caching and converting to geometry objects, then updates internal data structures.
- B 摘要: Retrieves the content of a URL as a string, reading line by line and returning the concatenated result.
- 静态失败原因: Static BERT models like GraphCodeBERT may over-rely on lexical overlaps such as URL, InputStream, BufferedReader, readLine patterns, and ignore the structural and functional differences. The token Jaccard of 0.161 might trigger similarity, but the actual logic diverges significantly.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the functions have different core intents: code_a is a tile downloading and processing routine with caching, while code_b is a generic URL content fetcher. The shared reading of lines is incidental and not sufficient for semantic clone classification.
- 共享行为: Both read a URL and process the input stream line by line using BufferedReader；Both handle IO exceptions (code_a catches them, code_b throws)
- 行为差异: Code_a implements request deduplication via a synchronized set, code_b does not；Code_a handles file and HTTP protocols, code_b only uses URLConnection for any protocol；Code_a parses the content into VectorTile and extracts geometries, code_b returns raw text；Code_a updates external data loader and display cache, code_b just returns string
- 修正建议: Improve model's ability to understand dataflow and external dependencies；Incorporate structural AST comparison to detect differences in control flow and API usage；Use contrastive learning with hard negatives that share boilerplate but differ in purpose

### case_id=4401 FP partial_functionality

- 方法: `getTicketsForQueue` vs `PhoneSetImpl`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Retrieves a list of tickets for a given queue from a REST API by executing an HTTP GET request and parsing the response.
- B 摘要: Constructs a PhoneSetImpl object by reading lines from a URL and parsing each line into a map.
- 静态失败原因: The static model may have over-weighted the common syntactic pattern of reading lines with BufferedReader and missed the distinct semantic contexts (REST API vs. URL parsing).
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely considers them non-clones because the overall purpose and output are entirely different (ticket retrieval vs. phone set construction), despite some superficial structural overlap in reading lines.
- 共享行为: Both read lines from an input stream (HTTP response or URL stream) in a loop.
- 行为差异: Function A executes an HTTP GET request; Function B opens a URL stream.；Function A filters lines to extract ticket IDs; Function B parses all non-comment lines using parseAndAdd.；Function A includes error handling and logging; Function B does not handle exceptions beyond the constructor declaration.；Function A returns a List<RTTicket>; Function B populates a HashMap field and has no return value.
- 修正建议: Incorporate data flow analysis to track how input is used (e.g., HTTP vs. URL).；Use method-level context to distinguish API calls (HttpGet vs. url.openStream).；Include surrounding class and method names in the representation.

### case_id=4402 FN partial_functionality

- 方法: `getEncoding` vs `run`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Extracts character encoding from an HTTP response by checking headers and scanning the response body.
- B 摘要: Performs an authenticated HTTP GET request and returns the response body as a string.
- 静态失败原因: Static BERT/GraphCodeBERT may have focused on token-level overlap (Jaccard 0.176) and method name difference (getEncoding vs run), leading to a low similarity score. The model might not capture the high-level semantic similarity of both being URL reading routines, or it may be sensitive to the different control flows and variable usage.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as clones due to shared API usage (URLConnection, BufferedReader, reading lines loop) and both performing I/O from a URL, despite different specific purposes. BigCloneBench annotations often accept broad Type-3 clones with similar algorithmic patterns.
- 共享行为: Both open HTTP connections using URL.；Both use BufferedReader to read input streams line by line.；Both close resources (reader, stream, connection).
- 行为差异: A only reads headers and body for encoding; B reads entire body for content.；A does not use authentication; B uses Basic Auth.；A returns a string encoding; B returns void and stores result in a field.；A extracts encoding from headers and body; B simply appends all lines.
- 修正建议: Improve model's ability to recognize shared I/O patterns across different method names.；Add training examples of broad Type-3 clones with similar resource handling patterns.；Incorporate structural or flow-aware features beyond token overlap.

### case_id=4403 FP lexical_or_api_overlap

- 方法: `init` vs `readZoneIDs`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Initializes controllers by reading class names from a resource file and loading each class via reflection.
- B 摘要: Reads zone IDs from a resource file and returns a set of integers.
- 静态失败原因: Overemphasis on the boilerplate code of reading a resource file line-by-line, without understanding the distinct semantic purposes.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels as clone only if functions perform the same task or are near-identical. Here the tasks are distinct, so likely non-clone.
- 共享行为: Both read lines from a resource file opened via URL；Both use a buffered reader pattern and iterate over lines
- 行为差异: Different processing per line: class loading vs integer parsing；Different return types: void vs HashSet<Integer>；Different error handling: specific exceptions vs generic Exception；Different logging levels and messages
- 修正建议: Incorporate type information to differentiate processing logic；Use dataflow analysis to track how the read string is used；Train on more diverse examples with similar structure but different semantics

### case_id=4404 FN partial_functionality

- 方法: `doRawRequest` vs `File2String`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends an HTTP POST request and returns the response body as a string.
- B 摘要: Reads a file from the filesystem or classpath and returns its content as a string.
- 静态失败原因: Stateless models like BERT rely on lexical overlap and method names; here token Jaccard is low (0.222) and API terms (URL vs File) differ, causing it to miss the structural similarity of the read loop.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may annotate as clone because both functions share the core pattern of reading lines from a stream into a string, and the annotation guidelines often accept Type-4 clones that capture this common I/O idiom despite different sources and error handling.
- 共享行为: Reads from an InputStream via BufferedReader；Uses readLine loop to append lines to a StringBuffer；Returns accumulated string
- 行为差异: A writes data to the connection before reading; B only reads from a file；A uses URLConnection; B uses FileInputStream or URL.openStream；A has no error handling; B has extensive error handling and system exit；A takes one parameter; B takes two
- 修正建议: Use a model capturing control-flow or data-flow patterns；Increase weight on structural similarity over lexical overlap；Incorporate program analysis to detect common subpatterns

### case_id=4405 FN benchmark_preference_bias

- 方法: `modifyApplicationMessage` vs `upload`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.6`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Modifies a properties file by reading, copying if needed, then updating or appending a key-value pair.
- B 摘要: Uploads an image file by copying it to a fixed destination path.
- 静态失败原因: Static models like GraphCodeBERT rely on token and structural similarity; the low token Jaccard (0.088) and different control flow lead to correct non-clone prediction.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as a clone due to both involving file manipulation, possibly considering a broad Type-4 functional similarity, but the specific behaviors are too distinct to justify.
- 共享行为: Both perform file I/O operations like reading and writing files；Both handle exceptions with printStackTrace
- 行为差异: Function A edits textual properties files for internationalization; Function B copies binary image files；Function A parses and modifies file content; Function B does not interpret file content；Function A has conditional logic for file creation and lookup; Function B is a straightforward copy
- 修正建议: Improve benchmark labeling consistency；Use more fine-grained clone types to differentiate such pairs

### case_id=4406 FN partial_functionality

- 方法: `runInternal` vs `postData`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.65`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Opens an HTTP connection to load an OPDS catalog, handling pagination and downloading books or parsing entries.
- B 摘要: Sends an HTTP POST request with form data to a specified host and returns the response.
- 静态失败原因: Static BERT models rely on token-level representations and may miss high-level semantic abstraction of 'HTTP communication'. The low token overlap (Jaccard=0.12) and different structures (long loop vs. simple sequence) make it hard to capture the shared functional essence.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider them as Type-4 semantic clones because both implement core HTTP communication functionality (open connection, set properties, read/write), despite different HTTP methods and additional logic in A. The annotation may prioritize API usage similarity over overall purpose.
- 共享行为: Both use URLConnection to establish HTTP connections；Both set request properties (User-Agent, Content-type, etc.)；Both handle input/output streams
- 行为差异: Function A performs GET-like operations (reading content), while B performs POST (sending data)；Function A includes error handling, redirects, progress tracking, and pagination; B is simple and synchronous；Function A parses OPDS catalog entries; B only reads and discards response body
- 修正建议: Incorporate data flow analysis to identify shared API call sequences；Use graph-based models that capture control flow and data dependencies for high-level semantics；Train on a broader set of HTTP communication examples to learn abstract patterns

### case_id=4407 FN benchmark_preference_bias

- 方法: `modifyApplicationMessage` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Modifies a locale-specific properties file by updating or adding a key-value pair for a message.
- B 摘要: Compresses a given file using GZip and writes to .gz file.
- 静态失败原因: The static model correctly identified semantic differences, thus predicting non-clone; it disagreed with a likely erroneous BCB label.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled as clone due to broad functional similarity like 'file modification' or 'resource manipulation', but the tasks are fundamentally different.
- 共享行为: Both perform file I/O operations (read/write).
- 行为差异: A manipulates text properties files for internationalization; B compresses binary files.；A reads and parses properties format; B reads raw bytes and writes compressed output.；A has complex logic for handling missing files and appending; B is a straightforward compression tool.
- 修正建议: Re-evaluate BCB label for this pair; functions are not clones.；Improve training data consistency.

### case_id=4408 FN benchmark_preference_bias

- 方法: `main` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.85`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file via HTTP and extracts zip entries to local files.
- B 摘要: Copies a file using NIO FileChannel transfer.
- 静态失败原因: Low token overlap and distinct API usage (URL, ZipInputStream vs FileChannel) cause similarity scores to be low; model cannot abstract to high-level copying intent.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider both as 'file copying' in a broad sense (reading input, writing output), though mechanisms differ significantly.
- 共享行为: Both perform file I/O operations with exception handling
- 行为差异: Source type: URL vs local file；Operation: zip extraction vs direct copy；Data flow: multiple output files vs single output
- 修正建议: Incorporate semantic role labeling for I/O operations；Use code summarization or intent classification to match abstract functionality

### case_id=4409 FN boilerplate_overlap

- 方法: `getEncoding` vs `PhoneSetImpl`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Opens a URL connection, reads HTTP headers and response body to extract the charset encoding.
- B 摘要: Constructor that reads phone data from a URL line by line, skipping comment lines, and builds a phone set map.
- 静态失败原因: Static BERT models likely missed the broad functional similarity due to low token overlap and focused on the semantic differences, while BCB's annotation preference tolerates such structural similarity.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may consider these clones due to similar boilerplate: opening a URL, reading lines in a loop, and processing each line, despite the completely different semantic purpose.
- 共享行为: Both open a URL and read lines using BufferedReader and InputStreamReader
- 行为差异: Function A extracts encoding from HTTP headers and body; Function B parses phone entries into a map；Function A returns a string; Function B is a constructor that initializes internal state；Function A checks for charset/encoding keywords; Function B skips lines starting with '***' and calls parseAndAdd
- 修正建议: Incorporate data-flow analysis to distinguish processing logic；Use graph-based models that capture control flow and dependencies；Add training data with similar boilerplate but different semantics

### case_id=4410 FN partial_functionality

- 方法: `testNetworkHTTP` vs `doVersionCheck`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends multiple HTTP GET requests to various hardcoded URLs, ignores response content, and prints stack trace on IOException.
- B 摘要: Fetches version info from a configurable URL, parses specific lines to extract build numbers, and updates UI with wait cursor and error dialog.
- 静态失败原因: Low token Jacard overlap (0.207) and different method names, parameter lists, and domain-specific constants lead the model to focus on surface differences rather than the shared I/O pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considers the common pattern of opening a URL, reading lines, and handling IOException as sufficient Type-4 clone, ignoring the different purposes and details.
- 共享行为: Both open HTTP connections and read lines using BufferedReader.；Both handle IOException.；Both use URL and InputStream/HttpURLConnection.
- 行为差异: A makes multiple requests to different endpoints; B makes one request.；A ignores response content; B parses lines starting with '.build' or '.stablebuild'.；A uses HttpURLConnection with explicit disconnect; B uses URL.openStream and closes reader.；B has UI interaction (wait cursor, error dialog); A does not.
- 修正建议: Enhance model with dataflow analysis to capture sequences like open-read-close.；Train on abstract patterns of API usage (e.g., HTTP GET pattern) independent of specific URLs.；Use graph-based representations to align similar control and data flow subgraphs.

### case_id=4411 FN benchmark_preference_bias

- 方法: `convert` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.1`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Converts an ACRNEMA stream file to DICOM format, adding UIDs and handling pixel data.
- B 摘要: Builds a site for editing by processing pages, applying XSLT transformations, and writing output files.
- 静态失败原因: Static BERT/GraphCodeBERT correctly predicted non-clone due to low token Jaccard and dissimilar ASTs; the supposed clone is not actually a clone.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled these as clones due to both being file-processing routines with loops and conditionals, but this is too superficial; likely a mistake.
- 共享行为: Both involve reading files, processing data, and writing output.
- 行为差异: Complete difference in domain (medical imaging vs. web content management)；Different data structures and processing logic
- 修正建议: Use higher similarity thresholds；Incorporate domain-specific knowledge to avoid false positive annotations

### case_id=4412 FP lexical_or_api_overlap

- 方法: `get` vs `loadMFileViaWeb`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches game records from a URL by sending HTTP GET with latitude/longitude/count headers and parses response lines into GameRecord array.
- B 摘要: Loads a MATLAB m-file from a web URL by reading its content and parsing it into a UserFunction object.
- 静态失败原因: Static BERT/GraphCodeBERT likely over-relied on lexical and API token overlap (URL, BufferedReader, InputStreamReader, readLine) without capturing the semantic divergence in data processing and return types.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically requires functions to perform the same domain-specific task; mere sharing of generic I/O patterns is insufficient for clone labeling.
- 共享行为: Both open HTTP connections and read lines from an InputStream using BufferedReader
- 行为差异: Different input parameters and purpose；Different output types (GameRecord[] vs UserFunction)；Different line processing (skip '#' lines vs concatenate all)；Different error handling (print stack trace vs throw exception)
- 修正建议: Incorporate data flow or control flow analysis to distinguish processing logic；Use AST-based methods to compare structure beyond token sequence；Train on more diverse negative examples with high API overlap but different semantics

### case_id=4413 FN library_context_missing

- 方法: `read` vs `login`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `context_recovery_then_expert`；动态可解性: `low`；执行优先级: `medium`
- A 摘要: Reads a camera log from a URL, parses each line into a CameraLogRecord, and sorts the records.
- B 摘要: Performs a login by posting encoded email and password to a URL, reads the response to extract a session ID, and returns it.
- 静态失败原因: Static BERT models rely on token embeddings and may have been misled by low lexical overlap (token Jaccard 0.154) and different method names ('read' vs 'login'). The model likely failed to recognize the abstract control-flow similarity due to reliance on surface-level tokens.
- 静态 case study: 该类错误缺少关键上下文或需要深层语义，纯静态方法不可靠。
- 动态 case study: 动态执行价值较低：样本可能依赖库、框架、网络、GUI、数据库或项目上下文，需要先恢复环境或 mock 依赖。
- BCB 偏好解释: BCB likely considers this a Type-4 clone because both methods follow the same high-level pattern: connect to a URL, read lines, process each line, close resources, and log. The differences are in specific data handling but the core I/O loop is similar.
- 共享行为: Both open a network connection to a URL；Both use BufferedReader and InputStreamReader to read lines from the connection；Both handle exceptions and close streams；Both output diagnostic information (logging or printing)
- 行为差异: Function A only reads data; Function B sends POST data before reading；Function A accumulates and sorts records; Function B extracts and returns a session ID；Function A catches a specific LogParseException; Function B catches general Exception；Function B uses OutputStreamWriter to write POST data; Function A does not
- 修正建议: Incorporate data-flow analysis to capture the sequence of open-read-close operations；Use code representation that abstracts API calls (e.g., URL.openStream vs URLConnection)；Train on functional similarity rather than strict syntactic overlap

### case_id=4414 FP lexical_or_api_overlap

- 方法: `init` vs `checkForUpgrade`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Loads controller classes from a registry file using the class loader.
- B 摘要: Checks for software upgrades by querying a remote server, parsing response, and updating database and UI.
- 静态失败原因: The model likely over-emphasized lexical/API overlaps (BufferedReader, URL, classLoader) and the similar I/O loop pattern, ignoring the distinct semantic contexts.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clone because the functions have entirely different purposes and no functional similarity, despite some superficial API overlaps.
- 共享行为: Both use BufferedReader to read input (file/URL)；Both use URL class to open connections
- 行为差异: Function A loads classes; Function B checks upgrades；Function A is for initialization; Function B is for upgrade management；Function A handles class loading; Function B handles database and UI operations
- 修正建议: Enhance model with dataflow analysis to capture actual data transformations；Use more diverse negative sampling to reduce sensitivity to API-level similarities

### case_id=4415 FP other

- 方法: `main` vs `copyFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Main method that generates adapter code from a Prolog file.
- B 摘要: Utility method that copies a file using FileChannel.
- 静态失败原因: The model likely overgeneralized from common structural patterns (e.g., try-catch blocks, file I/O operations) present in both functions, ignoring the vast semantic difference.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB labels these as non-clones because they have completely different functionality and implementation, with no shared semantic intent.
- 共享行为: None
- 行为差异: Function A performs complex adapter generation from Prolog; B simply copies a file.；Function A has nested try-catch, file parsing, class loading; B has straightforward file copy.；Function A is a main method with CLI handling; B is a helper method with no I/O interaction except file copy.
- 修正建议: Enhance training with more diverse negative examples that share syntactic patterns but differ semantically.

### case_id=4416 FN benchmark_preference_bias

- 方法: `doGet` vs `runDynusT`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Handles HTTP GET request to retrieve and serve a page by ID or name, checking user visibility and caching output.
- B 摘要: Runs the DynusT traffic simulation by copying executable and model files to a temp directory, executing the binary, and optionally cleaning up.
- 静态失败原因: The functions have extremely low token overlap (0.078) and no shared API calls or structural similarity. A model like GraphCodeBERT would correctly predict non-clone; the error is likely due to an incorrect BCB label rather than a model failure.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB annotation may have considered both as 'file manipulation' or 'system interaction' clones at a very abstract level, but the actual semantics are entirely different. This looks like a mislabeling.
- 共享行为: Both involve file writing operations under certain conditions.；Both use logging for informational messages.；Both handle exceptions and errors (e.g., send error responses or throw runtime exceptions).
- 行为差异: Function A processes web requests and interacts with servlet API; function B executes a native simulation program.；Function A performs conditional caching of HTML output; function B primarily copies files and runs an external process.；Function A has complex user permission checks; function B has none.；Function A writes a temporary HTML file if caching conditions are met; function B copies multiple static files every time.
- 修正建议: Re-evaluate BCB annotation for this pair; likely should be non-clone.；If BCB intends broad Type-4, clarify annotation guidelines to avoid such divergent pairs.；For model improvement, use contrastive learning to emphasize semantic similarity over lexical overlap.

### case_id=4417 FN benchmark_preference_bias

- 方法: `doFinishLoadAttachment` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.2`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Handles loading an attachment in an Android email app by either saving it to external storage or opening it via an intent.
- B 摘要: Launches a NexOpen project configuration in Eclipse by validating project structure, processing pom.xml files, setting properties, and installing the project.
- 静态失败原因: Static BERT likely correctly identified this as non-clone due to very low token overlap (0.0595) and clear domain mismatch, but BCB's ground truth considered it a clone, making the model's correct prediction appear as a false negative.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled these as clones due to both containing file I/O and exception handling, or due to a broad interpretation of 'partial functionality' that includes common utility patterns, but this is a stretch.
- 共享行为: Both perform file I/O operations using IOUtils.copy；Both have conditional logic with try-catch blocks
- 行为差异: Different domains: Android vs Eclipse plugin；Different purposes: attachment handling vs project launch；Different APIs: ContentResolver, Intent vs IProject, IFile, Document；Different control flow: save vs open, vs multi-step Maven project setup
- 修正建议: Verify if BCB annotation is correct; this pair seems obviously non-clone.；If BCB annotation is valid, consider that the model needs to recognize broad similarity based on common operations, but this is unlikely to be correct.

### case_id=4418 FN benchmark_preference_bias

- 方法: `doGet` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Handles HTTP GET requests to display a portal page, including authentication, caching, logging, and error handling.
- B 摘要: Copies a file from source to destination using NIO FileChannel.
- 静态失败原因: The static model correctly predicted non-clone due to very low token overlap (0.07) and fundamentally different APIs and control flow. It did not fail; the BCB annotation is likely incorrect.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: The BCB label of 1 is likely an annotation error. There is no meaningful functional similarity. Possibly the annotator considered the presence of file I/O in both as partial functionality, but this is too weak to justify a clone label.
- 共享行为: Both catch and handle IOExceptions.；Both use try-catch-finally blocks for resource management.
- 行为差异: Function A is a complex web request handler with multiple business logic steps; function B is a simple utility for file I/O.；A involves HTTP request/response, user permissions, and caching; B has no HTTP or security context.；A writes to temporary file only as a minor sub-operation; B's sole purpose is file copying.；The overall purpose and context of the functions are completely unrelated.
- 修正建议: Re-evaluate the BCB annotation for this pair; consider correcting the label to 0.；Ensure that future annotations for Type-4 clones require a stronger functional overlap than mere file I/O presence.

### case_id=4419 FN partial_functionality

- 方法: `copy` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Recursively copies a file or directory, skipping .svn directories and files with same last modified time.
- B 摘要: Builds a site for editing by reading XML, transforming pages with XSLT, and writing results to files.
- 静态失败原因: Static BERT/GraphCodeBERT likely failed because the lexical overlap is very low (Jaccard 0.06) and the method names and parameter lists are completely different. The model relies heavily on local token patterns and may not capture the high-level I/O theme shared implicitly.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled these as clones due to both functions dealing with file copying/writing, using similar I/O patterns (FileInputStream, FileOutputStream, buffers), and both having loops. However, the overall functionality is very different; BCB's broad Type-3/Type-4 criteria might accept this as 'file manipulation' clones.
- 共享行为: Both involve file I/O operations (reading and writing files using streams).；Both have loops iterating over collections (children array, pages vector).
- 行为差异: Function A performs simple recursive copy; Function B performs complex site generation with XML parsing, XSLT transformation, and string manipulation.；Function A handles both files and directories; Function B only writes output files and reads input XML.；Function A skips .svn directories and avoids overwriting unchanged files; Function B has no such logic.；Function B has extensive error handling and debug tracing; Function A throws IOException only.
- 修正建议: Include dataflow analysis to capture common I/O operations beyond exact token matches.；Use program slicing to isolate file read/write behavior.；Consider adding features for method length and complexity to avoid false positives from very different methods.

### case_id=4420 FN partial_functionality

- 方法: `getResourceAsStream` vs `copyFromFileToFileUsingNIO`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Retrieves a resource by URL, optionally caches it locally, and returns a FileInputStream from the cached file.
- B 摘要: Copies the entire content of an input file to an output file using NIO FileChannel transferTo.
- 静态失败原因: Static BERT models rely on token-level overlap and structural similarity, which are low (Jaccard=0.114). The differing method signatures, API calls, and control flow led the model to see no semantic similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considers both as performing file I/O operations that copy data from an input to an output, sharing the abstract concept of data transfer despite different contexts, which qualifies as a broad Type-4 clone.
- 共享行为: Both involve reading data from an input source and writing to a file output；Both handle file output streams and close resources
- 行为差异: A reads from a network URL, B reads from a local file；A implements caching logic, B does not；A returns an InputStream, B returns void；A has HTTP handling and conditional logic, B is straightforward
- 修正建议: Incorporate dataflow analysis to capture abstract data transfer between input and output；Consider multi-modal training with API call sequences and I/O operations；Use contrastive learning for pairs with low token overlap but high functional similarity

### case_id=4421 FN partial_functionality

- 方法: `retrieveQ` vs `read`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads content from a URL and returns the full text as a string.
- B 摘要: Reads from a URL or file and returns a status code indicating success or failure.
- 静态失败原因: Static BERT models rely on token similarity and API usage patterns, but here token Jaccard is low (0.15) and the overall control flow differs significantly (one returns string, one returns status; one only URL, one URL/file). The model may have missed the partial functional overlap due to low lexical similarity and different code structure.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely labeled as clone because both functions involve opening a URL and reading data, which is considered a shared functional behavior despite different return types and additional file handling in B.
- 共享行为: Both open a URL connection and read data from it.
- 行为差异: A returns the content string; B returns an integer status.；A only reads from URLs; B also reads from files.；A appends newlines between lines; B does not.；A prints HTTP response message to stderr; B does not.
- 修正建议: Train models to recognize partial functional clones by focusing on common sub-behaviors like URL reading.；Use graph-based or dataflow models to capture shared API call sequences regardless of return type.；Incorporate return type analysis to distinguish between content retrieval and status reporting.

### case_id=4422 FN partial_functionality

- 方法: `getHTML` vs `File2String`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches HTML content from a URL, reads lines with newline preservation, optionally writes to file, and returns the string.
- B 摘要: Reads a file from file system or classpath, concatenates lines without newlines, exits on failure, and returns the string.
- 静态失败原因: Low token overlap and different API keywords misled the model to focus on surface differences rather than the underlying loop pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely views both as 'resource-to-string' conversion functions, accepting differences in source and error handling as they share the core loop of reading lines and concatenating.
- 共享行为: Both read lines from an input stream and append to a string buffer.；Both return the resulting string.
- 行为差异: A uses HTTP connection, B uses file/classpath.；A adds "\r\n" after each line, B does not.；A optionally writes to file, B does not.；B exits on error, A prints stack trace.
- 修正建议: Incorporate dataflow or program dependence graphs to capture abstract patterns.；Use contrastive learning with examples that share similar control flow despite different APIs.；Enhance token embeddings with API synonym awareness.

### case_id=4423 FP lexical_or_api_overlap

- 方法: `readAndRewrite` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.0`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a DICOM image file and rewrites it to another file, using DICOM library classes.
- B 摘要: Handles UI action commands for setting application preferences via file choosers and updating UI components.
- 静态失败原因: The static BERT/GraphCodeBERT model may have been misled by generic API names like 'File', 'IOException', or common control flow patterns (e.g., null checks, loops) that appear in both functions, despite no semantic similarity.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels these as non-clones because they implement entirely different domain logic and have no functional overlap; BCB annotations generally require some level of functional similarity beyond boilerplate.
- 行为差异: Function A performs file I/O with DICOM image processing; Function B handles UI events and preference management.；Function A has no user interaction; Function B involves file chooser dialogs and preference storage.；Function A is a single-purpose data transformation; Function B is a multi-command event handler.
- 修正建议: Incorporate more fine-grained structural or data-flow information beyond token-level embeddings.；Use contrastive learning that penalizes false positives with low semantic overlap.；Add task-specific heuristics to filter out UI event handlers from image processing methods.

### case_id=4424 FN partial_functionality

- 方法: `read` vs `seeURLConnection`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads content from a URL or file path, returning a status code.
- B 摘要: Reads content from a hardcoded URL and logs it, throwing exceptions.
- 静态失败原因: Low token overlap, different method signatures and control flow; the model may not capture the semantic equivalence of URL.openStream and URL.openConnection as similar I/O operations.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often marks broad Type-4 clones where both functions share the high-level purpose of reading URL content, despite differences in parameters, error handling, and output.
- 共享行为: Both open a URL connection and read input stream content
- 行为差异: A supports file paths as input; B only a specific URL；A returns a status code; B returns void and logs；A uses a separate read method; B uses BufferedReader directly
- 修正建议: Train with more examples of Type-4 clones that share high-level API usage；Incorporate API call graph or data flow to recognize similar I/O patterns；Use contrastive learning to pull embeddings of functions with similar semantic intent

### case_id=4425 FP lexical_or_api_overlap

- 方法: `main` vs `readAndRewrite`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Parses a Prolog file and generates adapter classes, writing them to a JAR along with a serialized adapter layer.
- B 摘要: Reads a DICOM image file, decodes pixel data, and writes the dataset to a new file.
- 静态失败原因: The static BERT model likely focused on lexical and API-level similarities (e.g., 'File', 'IOException', 'System.out.println', try-catch structure) and general workflow of reading/writing files, while missing the fundamental differences in domain-specific logic and data transformations.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB label is 0 (non-clone) because the functions have no meaningful semantic overlap beyond generic file I/O; they operate in entirely different domains with distinct inputs, outputs, and processing logic.
- 共享行为: Both read from an input file and write output to a file.；Both print progress messages to console (e.g., 'reading...', 'writing...').；Both handle file I/O exceptions (IOException).
- 行为差异: Function A is a main method for a Prolog-based adapter generator; Function B is a utility for DICOM image processing.；Function A produces a JAR file with generated classes and serialized data; Function B produces a rewritten DICOM file.；Function A involves parsing Prolog code, visiting AST, and generating bytecode; Function B involves DICOM parsing, pixel data reading/writing.；Function A uses libraries like PrologParser, FactVisitor, ClassWriter; Function B uses DICOM-specific libraries like ImageInputStream, DcmParser, PixelDataReader.
- 修正建议: Enhance model with dataflow analysis to capture domain-specific operations.；Use larger context or finer-grained token embeddings to distinguish boilerplate I/O from core functionality.；Incorporate type information or library-specific knowledge to differentiate frameworks (e.g., Prolog vs. DICOM).

### case_id=4426 FP lexical_or_api_overlap

- 方法: `readTwitterFead` vs `getContent`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a hardcoded Twitter user timeline feed via HTTP and returns the response body as a string, logging errors for non-200 status.
- B 摘要: A generic HTTP content fetcher that executes a request, optionally sets timeouts, and returns the response body as a string with newlines, throwing exceptions on failure.
- 静态失败原因: The static BERT model likely overfit to the high lexical overlap of common HTTP client boilerplate (HttpClient, HttpGet, HttpResponse, etc.) and the while-readline pattern, leading to a false positive despite significant behavioral differences.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would likely label this as a non-clone because the functions are not semantically equivalent: one is a specific Twitter feed reader with error logging, the other is a general-purpose utility with timeout handling. The structural overlap (HTTP client boilerplate) is insufficient for a positive clone label under BCB's strict functional equivalence criteria.
- 共享行为: Both use HttpClient to execute an HTTP request and read the response body line by line into a string.
- 行为差异: A uses a hardcoded URL while B takes a request parameter.；A does not set connection or socket timeouts; B does.；A logs an error when status code is not 200; B does not check status code.；B appends newlines to each line; A does not.
- 修正建议: Incorporate parameterization awareness (hardcoded vs parameterized input).；Consider error handling patterns (status code checks, exception types).；Account for timeout settings and resource management (closing reader).；Use dataflow analysis to track URL source and status code handling.

### case_id=4427 FN benchmark_preference_bias

- 方法: `getResourceAsStream` vs `compress`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Retrieves a resource as an InputStream with caching and HTTP conditional handling.
- B 摘要: Concatenates multiple input files into an output file and optionally compresses it with an external tool.
- 静态失败原因: The static model correctly identified non-clone under strict semantics; its failure to match BCB label is due to BCB's possibly overbroad annotation in this case, not a model deficiency.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might consider them clones due to the common byte-level read-write loop pattern, but the overall functionality and purpose are too different for a typical clone definition.
- 共享行为: Both perform file I/O using streams；Both read bytes in a loop and write to an output stream
- 行为差异: Function A handles URL resources with caching; Function B concatenates local files；Function A returns an InputStream; Function B is void；Function A has complex HTTP and cache logic; Function B has optional external compression
- 修正建议: No fix needed if strict semantic equivalence is desired; if aligning with BCB, the model would need to accept very broad functional similarities, which may degrade precision.

### case_id=4428 FN benchmark_preference_bias

- 方法: `copyFile` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Copies a file from source to destination using NIO FileChannel.
- B 摘要: Launches a NexOpen project build by processing Maven pom files and configuring Hibernate dialect.
- 静态失败原因: Static BERT did not fail; it correctly predicted non-clone. The BCB label is likely an annotation error.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled it a clone due to both involving file I/O operations, but such broad similarity is insufficient for clone annotation.
- 行为差异: File copying vs. complex project launch；Simple utility vs. Eclipse plugin lifecycle；No common functionality beyond file I/O
- 修正建议: Re-annotate the pair as non-clone in the BCB benchmark.；Consider removing the pair from the dataset or correcting the label.

### case_id=4429 FN benchmark_preference_bias

- 方法: `runScript` vs `lookupFutureEvents`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Reads a script file from the applet codebase URL and returns its content as a string, returning 'error!' on failure.
- B 摘要: Fetches a JSON response from the Meetup API for future events, parses it into a list of Event objects, and throws GtugsException on error.
- 静态失败原因: Static BERT method correctly leveraged low token overlap and clear functional differences to classify as non-clone; the model did not fail, but BCB annotation is inconsistent with functional semantics.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have considered both as 'performing input/output operations from a URL' at a high level, but the specific functionalities are distinct. The annotation likely overgeneralized the common IO pattern.
- 共享行为: Both open a URL connection and read data from an InputStream.
- 行为差异: runScript reads raw bytes into a string; lookupFutureEvents reads JSON lines and parses them into structured objects.；runScript returns error string on exception; lookupFutureEvents throws an exception.；runScript uses applet codebase; lookupFutureEvents uses a specific API URL with a key.；Output types differ: String vs List<Event>.
- 修正建议: Re-evaluate BCB annotation for this pair; consider functional semantics rather than common IO patterns.；Static model requires no fix; it correctly identified non-clone.

### case_id=4430 FN benchmark_preference_bias

- 方法: `copyFile` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Copies a file using FileChannel from source to destination.
- B 摘要: Downloads a KMZ file from an HTTP URL and extracts its entries to local files.
- 静态失败原因: Static BERT models rely on token overlap and local context; the low Jaccard similarity (0.14) and different method names lead to a non-clone prediction, missing the broad functional similarity that BCB annotators perceived.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider both functions as file I/O operations that read from a source and write to a destination, despite different sources and processes, possibly classifying as Type-4 (functionally similar).
- 共享行为: Both involve reading from an input stream and writing to an output stream.；Both use FileOutputStream to write to files.
- 行为差异: A copies a single file directly using FileChannel; B downloads from network and extracts a zip archive.；A does not handle network protocols or compression; B uses ZipInputStream and URL connections.；A is a utility method; B is a main method with specific URL and extraction logic.
- 修正建议: Use data-flow-aware models that can capture reading/writing operations.；Incorporate program slicing to isolate I/O behavior.；Train on diverse clone types including Type-4 with low token overlap.

### case_id=4431 FP other

- 方法: `split` vs `main`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Splits a FASTA file into multiple partitions based on size limits (maxUnitBases, maxUnitEntries), writing each partition to a new file.
- B 摘要: Main method that reads a Prolog file, parses it, generates adapter classes, and writes them to a JAR file.
- 静态失败原因: The static BERT model may have been misled by overlapping API keywords (e.g., File, InputStream, catch) and similar code length/complexity, causing a false positive. Alternatively, the model might have a bias towards long, I/O-heavy functions.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely labels this as non-clone because the functionalities are entirely different: one is a FASTA file splitter, the other is a Prolog-to-Java adapter generator. There is no meaningful behavioral similarity beyond generic file I/O.
- 共享行为: Both perform file I/O operations；Both use try-catch for error handling
- 行为差异: Function A splits a FASTA file based on size limits; Function B generates adapter classes from Prolog；Function A works on FASTA-format biological data; Function B works on Prolog code；Function A uses FileChannel and ByteBuffer for efficient file splitting; Function B uses URLClassLoader and ClassWriter for class generation；Function A returns a Long count of partitions; Function B has no return value
- 修正建议: Incorporate more fine-grained semantic features (e.g., data flow, call graphs) to distinguish different functional domains；Augment training data with diverse examples of file I/O to reduce false positives on unrelated code

### case_id=4432 FN library_context_missing

- 方法: `getFile` vs `convert`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `context_recovery_then_expert`；动态可解性: `low`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL if not already present, modifies its wsdlsoap:address location, and saves the modified file.
- B 摘要: Converts an ACRNEMA stream file to DICOM format by parsing metadata, handling pixel data, and adding unique identifiers.
- 静态失败原因: Static BERT/GraphCodeBERT likely overemphasized the shared file I/O API calls (File, InputStream, OutputStream) and structural patterns (try-catch), while ignoring the domain-specific processing logic and low token overlap.
- 静态 case study: 该类错误缺少关键上下文或需要深层语义，纯静态方法不可靠。
- 动态 case study: 动态执行价值较低：样本可能依赖库、框架、网络、GUI、数据库或项目上下文，需要先恢复环境或 mock 依赖。
- BCB 偏好解释: BCB may consider them clones due to a lenient Type-4 interpretation: both are file processing functions that read, modify, and write, with similar boilerplate code for file I/O and exception handling.
- 共享行为: Both read from an input source and write to an output destination.；Both perform conditional checks before processing.；Both use try-catch-finally exception handling.
- 行为差异: Different input/output types: A uses URL and string paths, B uses File objects.；Completely different domain-specific logic: WSDL modification vs. DICOM conversion.；Different error handling: A throws AxisFault, B throws IOException.；Different output formats: A writes modified WSDL XML, B writes binary DICOM.
- 修正建议: Incorporate domain-specific knowledge about library usage.；Improve training to distinguish between boilerplate file I/O and unique functionality.

### case_id=4433 FP lexical_or_api_overlap

- 方法: `get` vs `doVersionCheck`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.85`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Sends an HTTP GET request, parses lines not starting with '#', decodes them into GameRecord, and returns an array.
- B 摘要: Opens a URL for version checking, reads lines to extract version and build, compares build, and shows a dialog if newer version exists.
- 静态失败原因: Static BERT/GraphCodeBERT may rely on token overlap and structural patterns; both functions share API usage (URL, BufferedReader), try-catch, and while loop with startsWith, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically considers Type-4 clones as partial functionality similarity, but here the overall goal (game record retrieval vs. version check) differs significantly. The structural overlap is superficial, so BCB would likely label as non-clone.
- 共享行为: Both open a URL and read lines via BufferedReader.；Both iterate over lines and check line prefixes with startsWith.
- 行为差异: Function A returns an array of GameRecord; function B is void and shows a UI dialog.；Function A sets request properties and method (GET); function B uses URL.openStream.；Function A filters lines starting with '#'; function B looks for '.version' and '.build'.；Function A decodes lines into GameRecord objects; function B extracts version/build strings and compares build numbers.
- 修正建议: Use models that incorporate dataflow and semantic understanding of variable transformations.；Consider method names and documentation as additional signals.；Train on more diverse non-clone examples with similar structural patterns but different functionality.

### case_id=4434 FP lexical_or_api_overlap

- 方法: `run` vs `addQDInformation`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches a tile from a URL or file, parses JSON geometry, and adds it to a map layer.
- B 摘要: Reads QD information from a local file or HTTP URL, parses custom lines to update project info values.
- 静态失败原因: The static BERT model likely over-relied on lexical and API overlaps (URL, BufferedReader, FileNotFoundException, etc.) and similar control flow patterns, ignoring the critical semantic differences in data processing and output.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled it as non-clone because the functions serve entirely different purposes and perform distinct data transformations. Even under broad Type-4, the semantic intent differs significantly.
- 共享行为: Both use BufferedReader to read lines from an input stream.；Both handle FileNotFoundException and IOException with empty catch blocks.；Both check a condition (existence of key or file) early and return if not met.；Both use URL and openStream for remote data retrieval.
- 行为差异: Function A processes vector tile geometry; Function B processes project QD information lines.；Function A writes to a data loader and triggers display cache; Function B updates internal info objects and date.；Function A uses synchronized blocks; Function B does not.；Function A parses multiple geometry types; Function B parses lines starting with 'pg ' and 'pt '.
- 修正建议: Incorporate dataflow analysis to track variable usage and transformations.；Use contrastive learning to distinguish based on function-level semantics.；Add attention to method names and comments for context.

### case_id=4435 FP boilerplate_overlap

- 方法: `main` vs `makeBackup`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Parses a Prolog file, generates adapter classes, and assembles them into a JAR.
- B 摘要: Copies files from a source directory to a destination directory with timestamp preservation.
- 静态失败原因: The model likely focused on common boilerplate patterns (try-catch, File I/O, loops) and overlooked the complete divergence in core semantics.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels this as non-clone because the functions serve entirely different purposes despite sharing low-level file operations.
- 共享行为: File I/O operations；Exception handling with printStackTrace；Use of File and streams
- 行为差异: A generates code and serializes data; B copies files；A uses complex class generation and URL class loading; B uses simple file copy loop；A writes JAR resources; B only copies raw bytes
- 修正建议: Enhance model with dataflow analysis to distinguish I/O from generation logic；Add training examples that penalize boilerplate-only similarity；Incorporate method name and high-level intent features

### case_id=4436 FN partial_functionality

- 方法: `run` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Processes files for pseudolocalization by reading messages, applying a pipeline, and writing output.
- B 摘要: Builds a site for editing by processing pages through XSLT transformations and file system operations.
- 静态失败原因: Static BERT model likely focused on low token overlap, different method names, and distinct structural patterns, missing the broad functional similarity that BCB annotators might have perceived.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB annotators may have considered that both functions implement a 'read-transform-write' pattern for file processing, which could be considered Type-4 semantic clone despite different domains.
- 共享行为: Both read input data, perform transformations, and write output to files；Both handle multiple files/items in loops；Both use input streams and output streams
- 行为差异: Different input types (message catalogs vs. XML/HTML pages)；Different transformation logic (pseudolocalization pipeline vs. XSLT + string replacements)；Different error handling and debugging；Different number and types of parameters
- 修正建议: Train model to recognize abstract functional patterns beyond lexical overlap；Use data flow or program dependence analysis to identify common 'read-process-write' structures；Incorporate domain knowledge or higher-level semantic embeddings

### case_id=4437 FN partial_functionality

- 方法: `fileDownload` vs `import_hints`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a file from a URL and saves it to a local directory with a fixed name.
- B 摘要: Imports puzzle piece hints from a file (possibly remote) and places them on a game board.
- 静态失败原因: The models likely captured the shared code patterns (URL opening, BufferedReader, try-catch) as strong signals, while missing the divergent core logic after reading.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled them as clones because both involve reading from a URL using similar boilerplate code, leading to a partial functionality overlap. However, the overall purposes are quite different.
- 共享行为: Both open a URL connection and read from it using BufferedReader.
- 行为差异: A writes raw bytes to a file; B parses structured text and updates game state.；A has a fixed output file name; B processes multiple lines in a loop.；A returns void; B returns a boolean indicating success.
- 修正建议: Enhance training with negative examples that share boilerplate but differ in purpose.；Incorporate structural analysis focusing on the entire function rather than local windows.；Use contrastive learning to separate functions with similar API usage but different semantics.

### case_id=4438 FN partial_functionality

- 方法: `retrieveQ` vs `seeURLConnection`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Retrieves content from a given URL, reading lines with newline separators, prints HTTP response message to stderr, and returns the concatenated string.
- B 摘要: Reads content from a hardcoded URL, concatenates lines without newlines, logs the result, and does not return anything.
- 静态失败原因: Static BERT/GraphCodeBERT models may fail due to low token Jaccard similarity (0.34) and insufficient capture of functional similarity beyond surface syntax. Differences in method signatures, error handling, and output mechanisms mislead the model to classify as non-clone.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label these as clones because both implement the core functionality of reading web page content from a URL. Differences in line separators, return value, and output method are considered superficial variations (Type-3 clone) under BCB's annotation guidelines.
- 共享行为: Open a URL connection；Read lines from the input stream using BufferedReader；Append lines to a buffer；Close the reader
- 行为差异: URL source: parameter vs hardcoded string；Line separation: includes newline vs no newline；Return type: String vs void；Error handling: specific exceptions vs generic Exception
- 修正建议: Enhance model to recognize functional equivalence via API call sequences (e.g., URL, openConnection, getInputStream, BufferedReader) rather than exact token matches.；Incorporate data flow or program dependency graphs to capture core I/O behavior.；Use contrastive learning with Type-3/Type-4 clone examples to improve tolerance for superficial changes.

### case_id=4439 FN partial_functionality

- 方法: `getResourceAsStream` vs `resolvePlugins`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a remote resource from a URL, caches it locally with HTTP caching checks, and returns an InputStream.
- B 摘要: Downloads a specific plugins.xml file from a remote URL if not locally cached, saves it, then delegates to another method.
- 静态失败原因: Low token overlap (0.107) and different method names; GraphCodeBERT likely focused on syntactic structure and missed the higher-level shared behavior of HTTP download and caching.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label these as clones because both implement the pattern of fetching a remote resource and caching locally, considered a Type-4 clone under broad functional similarity.
- 共享行为: Both download remote files over HTTP and cache them on disk
- 行为差异: A is a general resource getter with complex caching and returns InputStream; B is specific to plugins.xml with simple existence check and is void；A uses timestamps for cache invalidation; B only checks file existence
- 修正建议: Enhance model with dataflow analysis to detect resource access patterns；Include contrastive training on partial functionality clones；Use IO-aware embeddings

### case_id=4440 FP lexical_or_api_overlap

- 方法: `read` vs `readScalarpvviewerDocument`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads camera log lines from a URL, parses each into CameraLogRecord, and collects sorted records.
- B 摘要: Reads a proprietary XML configuration file from a URL, extracts numerous UI and data parameters, and sets up the Scalarpvviewer display.
- 静态失败原因: The static model likely focused on lexical overlap in the reading pattern (BufferedReader, URL, readLine, try-finally/catch) and method name 'read', ignoring the long-range semantic differences in data processing that occur after reading the lines.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would label this as non-clone because the functional purpose is entirely different (log parsing vs UI configuration loading). The only commonality is trivial data reading boilerplate, which is insufficient for Type-3/4 similarity.
- 共享行为: Both open a URL, create a BufferedReader, read lines, and close the reader.；Both handle IOException (A throws, B catches).；Both iterate over lines using a while loop.
- 行为差异: A parses each line as a CameraLogRecord; B accumulates lines into an XML string and stops at a marker.；A sorts records after reading; B parses XML and sets many UI parameters.；A handles LogParseException per line; B catches IOException at the outer level.；B has complex processing using XmlDataAdaptor, updating fonts, panels, titles, and PVs.
- 修正建议: Use dataflow-aware models that track how variables are used after reading.；Include more context or use code structure differences to distinguish boilerplate from true semantic similarity.；Train on more diverse clones that require understanding of subsequent data processing.

### case_id=4441 FP boilerplate_overlap

- 方法: `readZoneIDs` vs `run`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads integers from a resource file and returns them as a HashSet.
- B 摘要: Reads from a URL without using the content, discarding all lines.
- 静态失败原因: High lexical overlap in common IO patterns (URL, InputStreamReader, readLine) and loop structure triggered false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically considers non-clones when the core functionality differs significantly despite similar boilerplate code.
- 共享行为: Open a URL/stream and read lines using BufferedReader/LineNumberReader
- 行为差异: A parses each line as integer and stores in set; B discards lines；A returns HashSet<Integer>; B returns void；A uses class.getResource; B uses new URL to HTTP；A prints stack trace on exception; B catches silently
- 修正建议: Incorporate data flow analysis to track whether read data is used；Check return types and side effects；Consider method name context

### case_id=4442 FP lexical_or_api_overlap

- 方法: `copyFile` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Copies a file from source to destination using NIO FileChannel.
- B 摘要: Handles ActionEvent commands to configure external tool paths (GRAPHVIZ, IMAGEMAGICK, etc.) via file chooser dialogs and update UI preferences.
- 静态失败原因: The static BERT model likely overemphasized superficial lexical similarities (both contain 'File', 'IOException', and 'close' references) and missed the fundamentally different control flows and intents.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clone because the two functions have completely different purposes and implementations; one is a file copy utility and the other is an event handler for UI preferences.
- 共享行为: Both involve File objects and file-related operations (copy vs. open dialog).
- 行为差异: Function A performs actual file I/O copying; Function B only selects file paths and stores preferences.；Function B has extensive UI update logic and configuration handling; Function A is a utility method.；Exception handling differs: A rethrows IOException, B catches exceptions and logs warnings.
- 修正建议: Train models to better distinguish between utility functions and event handlers.；Incorporate structural features like control flow graph differences.；Use larger context to capture overall method purpose (e.g., method name and surrounding class).

### case_id=4443 FN partial_functionality

- 方法: `getFile` vs `doUpload`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Downloads a WSDL file from a URL, modifies the soap:address location, and saves it locally.
- B 摘要: Handles HTTP file upload, saves files to a temporary directory, and processes the upload.
- 静态失败原因: Static BERT models rely on lexical and syntactic overlap; these functions have low token Jaccard (0.114) and different APIs, so the model missed the high-level conceptual similarity (both network file operations) that BCB annotators perceived.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB annotators may have considered both as 'file transfer over network' operations (download vs upload), thus accepting broad Type-4 similarity despite different specific functionality.
- 共享行为: Both involve file I/O and temporary file creation.；Both use logging for debugging.；Both handle exceptions (IOException, etc.).
- 行为差异: Purpose: getFile downloads and modifies a WSDL file; doUpload uploads files from HTTP requests.；Input/Output: getFile returns a file path; doUpload writes to response and does not return.；Core logic: getFile parses XML and modifies attributes; doUpload handles multipart requests and file saving.
- 修正建议: Incorporate functional role detection (e.g., download vs upload categorization).；Use graph-based representations capturing control and data flow at a higher abstraction level.；Add context-aware features like method purpose from names or comments.

### case_id=4444 FN boilerplate_overlap

- 方法: `doVersionCheck` vs `testNetworkHTTP`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Checks for new version of jEdit by reading a version URL and comparing build numbers.
- B 摘要: Performs multiple network requests to various URLs, likely for testing or data exfiltration.
- 静态失败原因: Static BERT models may overfocus on syntactic token overlap and fail to capture the distinct semantic goals; they might detect the common I/O pattern but miss the contrasting version-check vs. test purpose. The low token Jaccard (0.195) might indicate limited lexical overlap, but the structural pattern is still recognizable; model likely misclassified due to lack of deep understanding of the broader context (e.g., method names, surrounding code).
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may consider these clones due to high structural similarity in the network I/O pattern: both have try-catch-IOException, while loop reading lines, and similar variable names (url, line, BufferedReader). The differing business logic (version check vs. test) may be overlooked as Type-3/4 clone under broad functional similarity.
- 共享行为: Both open a URL connection and read lines via BufferedReader；Both handle IOException with a catch block
- 行为差异: A performs version comparison and shows UI messages; B makes multiple requests to different URLs and discards response data；A uses URL.openStream(); B uses HttpURLConnection and manages connection lifecycle；A has a specific protocol (lines starting with .version/.build); B reads lines without parsing
- 修正建议: Include method-level context (e.g., method name, doc comments) in feature representation；Train on more diverse clone types to distinguish boilerplate from core functionality；Use data flow analysis to trace the usage of read data, capturing differences in how data is processed

### case_id=4445 FN benchmark_preference_bias

- 方法: `transport` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.7`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Recursively copies files from a source directory to a destination directory, using FileChannel for transfer.
- B 摘要: Retrieves a resource as an InputStream from a URL, with local caching and HTTP connection handling.
- 静态失败原因: Static BERT likely focused on lexical and structural details, missing the high-level semantic abstraction of 'resource transfer'. The low token Jaccard and different API usage led the model to predict non-clone, but BCB considers the broad category of file/resource streaming as sufficient for clone labeling.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled them as clones due to broad Type-4 similarity: both transfer data from a source to a destination, involve file handling, and have error handling. The annotation standard often accepts partial functional similarity.
- 共享行为: Both involve file I/O operations；Both handle exceptions and use try-catch；Both read/write data through streams
- 行为差异: Function A is recursive and traverses directory tree; Function B is not recursive；Function A copies files locally; Function B downloads from network and caches；Function A uses FileChannel; Function B uses BufferedInputStream/OutputStream and URLConnection
- 修正建议: Train on more diverse Type-3/Type-4 examples with varying APIs but similar intent；Incorporate high-level semantic annotations or program dependency graphs to capture abstract behavior；Use contrastive learning with BCB-style labels to align model with broad clone definitions

### case_id=4446 FN benchmark_preference_bias

- 方法: `copyToDir` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Copies a file to a specified directory, creating the directory if necessary and handling potential self-copy by checking parent equality.
- B 摘要: Builds a website for editing by reading XML configuration, transforming it with XSLT, and writing output pages to filesystem using various I/O operations.
- 静态失败原因: The static BERT/GraphCodeBERT model correctly predicted non-clone. The failure from BCB perspective is that it disagreed with an overly broad or incorrect BCB label. The model likely learned from low token overlap and distinct signatures.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB annotations sometimes consider broad Type-4 clones where both functions write files, but this is too coarse. Alternatively, the annotation may be erroneous due to partial similarity in file I/O, but the overall functionality is vastly different.
- 共享行为: Both involve file I/O operations (reading and writing files).
- 行为差异: Function A is a simple file copy; function B is a complex website generation process.；Function A uses a 1024-byte buffer for copying; function B uses a 8192-character buffer and string transformations.；Function A creates directories; function B does not explicitly create directories.；Function A has no XML processing; function B heavily uses DOM, XSLT, and string manipulation.
- 修正建议: Verify and possibly correct BCB annotations for this pair.；For model improvement, emphasize structural and semantic diversity beyond token overlap.；Use fine-grained functional similarity criteria rather than broad file I/O presence.

### case_id=4447 FP lexical_or_api_overlap

- 方法: `main` vs `copy`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Main method that parses a Prolog file, generates adapter classes and serialized adapter layers, and packages them into a JAR.
- B 摘要: Copy method that uses FileChannel and MappedByteBuffer to copy a file from source to destination.
- 静态失败原因: The static BERT model likely focused on lexical and API overlap (e.g., File, IOException, try) and ignored structural and semantic differences, leading to a false positive clone prediction.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would label as non-clones because the functions are entirely different in purpose and complexity: one is a code generator, the other is a simple file copy.
- 共享行为: Both perform file I/O operations.
- 行为差异: Function A performs complex parsing, code generation, and uses reflection and class loading; Function B simply copies bytes between files.；Function A handles multiple files and has extensive error handling with try-catch; Function B uses try-finally to close channels and is error-free.；Function A has a complex control flow with multiple conditions and loops; Function B has straightforward sequential execution.
- 修正建议: Incorporate control-flow and data-flow information into the model.；Use a larger and more diverse set of negative examples during training to reduce over-reliance on API tokens.；Employ graph-based representations like AST or PDG to capture structural differences.

### case_id=4448 FN partial_functionality

- 方法: `doGet` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Forwards an HTTP GET request to another URL, copies headers and streams response back to the servlet output.
- B 摘要: Retrieves a resource via HTTP, caches it to a file, and returns an input stream with caching and conditional fetching logic.
- 静态失败原因: The static model likely focused on low token overlap and different method signatures, missing the shared HTTP connection and stream handling logic due to superficial structural differences.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely labels this as a clone because both functions involve establishing an HTTP connection, reading data, and producing an output, which is a common high-level pattern despite different detailed implementations.
- 共享行为: Open an HTTP URL connection；Read input stream from the connection；Handle HTTP response codes and headers
- 行为差异: A writes to servlet response output; B caches to file and returns input stream；A forwards headers; B does not forward headers；B has caching logic and file I/O; A has no caching；A disables redirect following; B enables it
- 修正建议: Enhance model to recognize common API usage patterns (e.g., HttpURLConnection, getInputStream)；Incorporate data flow analysis to identify functional similarity in network I/O；Use contrastive learning with pairs that share partial behaviors

### case_id=4449 FP lexical_or_api_overlap

- 方法: `createDialogArea` vs `getVersion`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Creates a SWT dialog area that reads license text from a bundle resource and displays it in a Browser or Text widget.
- B 摘要: Fetches a version string from a remote HTTP URL by reading the first line of the response.
- 静态失败原因: The static model likely over-focused on the lexical and API overlap (both use URL, BufferedReader, InputStreamReader, while loops, try-catch), ignoring the higher-level semantic context and different return types.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would likely label these as non-clones because their overall purposes are completely different (GUI creation vs. version fetching) and they produce different output types. The only similarity is the boilerplate code for URL reading, which does not imply functional equivalence.
- 共享行为: Both read text from a URL using BufferedReader and InputStreamReader.；Both use a while loop to read lines from the input stream.；Both handle IO exceptions with try-catch.
- 行为差异: Method A creates and returns a Composite GUI component; Method B returns a String.；Method A reads from a local bundle resource; Method B reads from an external HTTP URL.；Method A writes the read text to a UI component; Method B returns the read text as a version string.；Method A has complex exception handling with separate finally blocks; Method B has a simple catch-all that sets version to null.
- 修正建议: Incorporate method signatures and return types as input features.；Add dataflow analysis to distinguish local resource access from remote HTTP requests.；Use task-oriented embeddings that capture intent rather than just code structure.

### case_id=4450 FN partial_functionality

- 方法: `copyResource` vs `copyLogic`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource from a URL or file path to a destination file using InputStream and OutputStream.
- B 摘要: Copies a file from a specified binary path to an agent file location using FileChannel.transferTo, with state management.
- 静态失败原因: Static BERT/GraphCodeBERT likely focused on lexical overlap and token sequences, which are low (Jaccard=0.111) due to different APIs and control flow. It missed the shared file copying semantics.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels functions as clones if they perform the same high-level task (file copying), even with different implementations, due to their broad Type-3/Type-4 acceptance.
- 共享行为: Both functions perform file copying from a source to a destination.；Both involve opening input and output streams/channels and closing them after copying.；Both handle exceptions related to file operations.
- 行为差异: copyResource reads byte-by-byte from an InputStream, while copyLogic uses FileChannel.transferTo for potentially faster copying.；copyResource supports both URL and file sources, while copyLogic only supports file sources.；copyLogic includes state management (setting states to Idle and Synchronizing), which copyResource does not have.；Error handling differs: copyResource throws an Exception, while copyLogic catches FileNotFoundException and IOException and prints stack traces.
- 修正建议: Incorporate data flow analysis to identify that both functions read from a source and write to a destination.；Use semantic embeddings that capture functionality rather than exact token matches.；Include structural similarity of file I/O operations (e.g., open-close patterns).

### case_id=4451 FN partial_functionality

- 方法: `copyResource` vs `unJarStart`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `uncertain`；bcb_style_clone: `yes`；confidence: `0.75`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource (URL or file) to a destination file using byte-by-byte I/O.
- B 摘要: Extracts entries from a JAR file whose names start with a given prefix, copying them to a directory structure.
- 静态失败原因: Static BERT/GraphCodeBERT likely focused on low token overlap (Jaccard=0.128) and different API calls (URL, FileInputStream vs JarFile, IOUtils) and loop structures, missing the underlying semantic similarity of copying. The model may not generalize the concept of 'copy bytes' across different APIs and control flows.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this as clone because both functions perform the high-level task of copying file contents from a source to a destination, a semantic clone (Type-4) even though the implementation details differ. The shared core behavior of reading and writing bytes is considered significant functionality.
- 共享行为: Both copy data from an input source to file output(s)；Both use file I/O operations
- 行为差异: A copies a single resource to one file; B copies multiple JAR entries to multiple files；A reads and writes byte-by-byte; B uses IOUtils.copy for buffered transfer；A throws exceptions; B catches and prints stack trace；A uses URL or FileInputStream; B uses JarFile
- 修正建议: Train with more examples of file copying in different contexts to learn the abstract operation；Incorporate data flow or control flow graphs to capture similarities in I/O operations；Use code summarization techniques that highlight intent like 'copy'

### case_id=4452 FN partial_functionality

- 方法: `modifyApplicationMessage` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Modifies a message value in a locale-specific properties file, optionally copying the English file if the locale file does not exist.
- B 摘要: Copies a file from source to destination using FileChannel with synchronized lock.
- 静态失败原因: Low token overlap and different method names/purposes likely overshadowed the shared file copy logic; the model failed to recognize the embedded subtask of copying a file.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this as a clone because both functions contain a file copy operation (A's fallback copy of the English file), which is a partial functional similarity, and BCB often accepts Type-4 partial functionality clones.
- 共享行为: File copying (reading from one file and writing to another)
- 行为差异: A primarily reads/writes properties files with string manipulation; B only copies raw bytes.；A handles missing locale file by copying from English; B always copies.；A uses Reader/Writer streams; B uses FileChannel.；B has synchronization on a static lock; A does not.
- 修正建议: Train on examples of partial functionality clones where a subtask (e.g., file copy) is embedded in a larger method.；Use data flow or program slicing to extract sub-functional similarities.；Incorporate file I/O API usage patterns as features.

### case_id=4453 FP lexical_or_api_overlap

- 方法: `getVersion` vs `callApiPost`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches a version string from a remote URL via HTTP GET.
- B 摘要: Performs an HTTP POST API call with parameters, headers, timeouts, and error handling, returning an InputStream.
- 静态失败原因: The static model likely overemphasized lexical and API-level similarities (e.g., 'URL', 'openConnection', 'BufferedReader'/'InputStream', try-catch) while ignoring the semantic differences in method purpose, HTTP method, and data handling.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would label these as non-clones because the methods have different signatures, different HTTP methods, different return types, and distinct functionality (simple fetch vs. complex API call), thus not even partial functionality clones in BCB's view.
- 共享行为: Both open a URL connection to a remote server.；Both use try-catch for exception handling.；Both involve reading from an input stream (A reads line, B reads response).
- 行为差异: A performs HTTP GET, B performs HTTP POST.；A has no request headers, parameters, or output stream; B sets headers, sends parameters, and writes to output stream.；A returns a String version, B returns an InputStream (wrapped).；A has simple error handling (returns null), B throws a custom exception on failure.
- 修正建议: Incorporate method signature and return type into the representation.；Model the control flow and sequence of operations more comprehensively.；Use data flow and dependency analysis to distinguish different usage patterns.；Train on more diverse examples to reduce bias towards common API boilerplate.

### case_id=4454 FN partial_functionality

- 方法: `runScript` vs `File2String`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a file from a URL relative to the codebase and returns its content as a string, returning 'error!' on exception.
- B 摘要: Reads a file from local file system or classpath resource and returns its content as a string, exiting on error.
- 静态失败原因: Low token Jaccard (0.2) and structural differences (different signatures, control flow) caused static BERT to miss the semantic similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB considers broad Type-3/Type-4 clones where the core functionality (reading file content) is shared, despite differences in I/O mechanism and error handling.
- 共享行为: Reads a file and returns its content as a string；Both are utility methods for file reading
- 行为差异: Input source: A uses URL only; B tries local file then resource；Error handling: A returns 'error!'; B prints and exits；Reading method: A reads byte by byte; B reads line by line；Stream types: A uses BufferedInputStream; B uses BufferedReader
- 修正建议: Incorporate dataflow analysis to capture file reading intent；Use graph-based representations like AST or CFG；Fine-tune on BCB annotations to capture domain-specific clone definitions

### case_id=4455 FP boilerplate_overlap

- 方法: `main` vs `readAndRewrite`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Generates Java adapter classes from a Prolog file using command-line options.
- B 摘要: Reads a DICOM file, processes pixel data, and writes the result to a new DICOM file.
- 静态失败原因: The model may have been misled by similar structural patterns (e.g., reading a file, processing, writing output) and the presence of common boilerplate code like System.out.println and exception handling, even though token overlap is low.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB considers these as non-clones because the overall functionality (domain and purpose) is completely different, despite both using file I/O patterns.
- 共享行为: Both functions read input files and write output files；Both use standard I/O and print status messages；Both have structured error handling
- 行为差异: Function A processes Prolog files and generates Java adapter code; Function B processes DICOM medical images；Function A involves complex reflection and class generation; Function B involves pixel data reading and writing；Function A is a command-line entry point; Function B is a private helper method
- 修正建议: Incorporate data flow and type analysis to distinguish different domain operations；Use method-level embedding capturing semantic intent beyond surface syntax；Add negative mining on pairs with high boilerplate but different functionality

### case_id=4456 FP lexical_or_api_overlap

- 方法: `main` vs `copyFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Generates adapter classes from a Prolog file and writes to a JAR file.
- B 摘要: Copies a file using buffered streams.
- 静态失败原因: The model likely overemphasized common API elements (File, IOException, try-catch) and missed structural and semantic differences due to limited context understanding.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels non-clones when functions have entirely different purposes and implementations, despite superficial API overlap.
- 共享行为: Both use file I/O operations；Both handle IOException
- 行为差异: Function A is a complex adapter generation pipeline; B is a simple file copy；A uses Prolog parser, class writing, serialization; B only reads/writes bytes；A has command-line argument parsing; B takes two File parameters
- 修正建议: Include control-flow and data-flow features in the model；Improve training data with contrasting examples of file I/O utilities vs. complex processing

### case_id=4457 FP lexical_or_api_overlap

- 方法: `addDataFromURL` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads content from a given URL and appends it line by line to a string builder, with basic error handling.
- B 摘要: Performs a Google image search by constructing a query URL, fetching the HTML, parsing image links, and adding them to a list.
- 静态失败原因: Static BERT likely overfits to lexical and API-level overlap (e.g., 'URL', 'openStream', 'BufferedReader', 'readLine') and similar control flow (try-catch, while loop), missing the semantic divergence in goal and data processing.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels non-clones when functions have different overall purposes despite some API overlap; here the core tasks differ (generic download vs. web scraping with parsing).
- 共享行为: Both open a URL and read lines using BufferedReader
- 行为差异: Function A is a generic URL content downloader; B is a specific image search parser；B uses HttpURLConnection, sets User-Agent, constructs a specific search URL, and parses HTML；A appends raw text to a string; B extracts image URLs and stores them in a list
- 修正建议: Use data-flow and control-flow features to distinguish generic I/O from domain-specific logic；Incorporate code summarization or embedding that captures high-level intent；Train on more diverse non-clone pairs with partial API similarity

### case_id=4458 FP partial_functionality

- 方法: `readData` vs `copyFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Parses a set of comma-separated lists of strings, populates several sets and a map (e.g., topSet, leftSet, vowelSet) for use in Tibetan transliteration processing.
- B 摘要: Copies a file from source to destination using a buffer, with optional overwrite handling.
- 静态失败原因: Static BERT/GraphCodeBERT models may over-rely on local token patterns (e.g., multiple occurrences of 'HashSet', 'StringTokenizer') and structural similarities (loops, conditionals) while missing the high-level semantic purpose. The large size of Function A and truncation may also cause the model to focus on fragments that coincidentally look similar.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely labels this as non-clone because the functionalities are completely different: one is about initializing a character mapping system, the other is about copying a file. Even though both involve reading data, their inputs, outputs, and side effects are entirely different.
- 共享行为: Both perform some form of data reading (file reading vs token parsing).；Both use loops and basic I/O concepts.
- 行为差异: Function A builds data structures from configuration strings; Function B copies file bytes.；Function A has complex logic with multiple tokenizations; Function B is a standard file copy with streams.；Function A handles parsing errors and special cases; Function B only handles I/O and overwrite.；Function A does not use file I/O directly; Function B exclusively deals with file I/O.
- 修正建议: Increase training data diversity for non-clone pairs with low token overlap but some shared keywords.；Use contrastive learning with more negative mining to avoid false positives due to common API usage.；Incorporate function-level semantic embeddings (e.g., code summarization) to better distinguish purposes.

### case_id=4459 FN benchmark_preference_bias

- 方法: `main` vs `testLoadSource`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a URL and extracts its ZIP entries to files.
- B 摘要: Loads an article source from an arXiv DAO facade and asserts its content contains a specific substring.
- 静态失败原因: Static BERT/GraphCodeBERT likely relied on low token overlap and structural differences, correctly predicting non-clone. The FN error is due to BCB label being positive.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled them as clones due to superficial similarity in I/O pattern: both open streams, read, and close. However, the functional purpose is different.
- 共享行为: Both open an InputStream and read data；Both close the InputStream after use
- 行为差异: Function A extracts ZIP entries to files, Function B copies stream to string and asserts content；Function A uses URL directly, Function B uses a DAO facade；Function A is a main method, Function B is a test method
- 修正建议: Ensure BCB annotations are consistent with functional semantics；Consider using finer-grained clone types that distinguish generic I/O patterns from specific functionality

### case_id=4460 FP lexical_or_api_overlap

- 方法: `init` vs `readScalarpvviewerDocument`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Loads controller classes from a registry file by reading class names line by line.
- B 摘要: Reads and parses an XML configuration file to initialize a scalar PV viewer.
- 静态失败原因: The model likely focused on surface-level similarities such as the use of BufferedReader, InputStreamReader, try-catch blocks, and similar variable names (reader, in, line), leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB considers functional similarity; these functions perform entirely different tasks (class loading vs. XML configuration reading), so they are non-clones.
- 共享行为: Both read lines from an input stream using BufferedReader and InputStreamReader.
- 行为差异: Function A loads Java classes; function B parses XML and sets UI properties.；Different input types: ServletContext vs URL.；Function A catches ClassNotFoundException; function B only catches IOException.；Different final actions: adding classes vs. updating viewer panels.
- 修正建议: Include more context about the overall function purpose, such as method names and surrounding code.；Fine-tune with more diverse examples of non-clones with similar API usage but different semantics.

### case_id=4461 FP boilerplate_overlap

- 方法: `main` vs `handle`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Generates Java adapter classes from Prolog program definitions and writes them to a JAR file.
- B 摘要: Handles log file rotation by compressing and archiving old log files.
- 静态失败原因: Static BERT/GraphCodeBERT likely focused on overlapping boilerplate code (e.g., try-catch, File I/O, System.out.println) and ignored the high-level task context, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels as non-clone because the two functions have completely different purposes and no semantic overlap in their core functionality.
- 共享行为: Both perform file I/O operations and handle exceptions
- 行为差异: Function A parses Prolog files and generates adapters; Function B rotates log files；Function A uses PrologParserImpl and FactVisitor; Function B uses FileChannel and GZIPOutputStream；Function A writes JAR resources; Function B deletes old log files and archives them
- 修正建议: Incorporate method name and class context into the model；Use richer representations that capture program flow and data dependencies beyond surface tokens

### case_id=4462 FP lexical_or_api_overlap

- 方法: `readData` vs `saveProject`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Reads initialization data from static strings and files into HashSets and maps.
- B 摘要: Saves a project to a file system, including databases and XML representations of objects.
- 静态失败原因: Static BERT likely relied on superficial lexical and API overlaps (e.g., File, IOException, loops) and missed the entirely different high-level purpose due to lack of deep semantic understanding.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clone because the functions perform completely different tasks (initialization vs. project saving) with no semantic overlap, even under broad Type-3/4 criteria.
- 共享行为: Both use File and IOException；Both have loops and conditionals
- 行为差异: A reads and populates in-memory data structures; B writes data to disk and returns boolean；A has no parameters; B takes multiple parameters；A is a static void method; B is public instance method returning boolean；A uses StringTokenizer; B uses file channels, SQL, and XML serialization
- 修正建议: Incorporate data-flow and control-flow analysis；Use contrastive learning with hard negative examples of low Jaccard but similar API usage；Include function-level documentation or context

### case_id=4463 FP boilerplate_overlap

- 方法: `getVersion` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches the latest version string from a remote URL and returns it.
- B 摘要: Fetches Google image search results, parses image URLs, and updates a UI component with an image.
- 静态失败原因: The static model likely overemphasized the overlapping boilerplate (URL opening, BufferedReader, try-catch) while ignoring the distinct semantic intents and return types.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB requires functional similarity beyond common coding idioms; these methods serve completely different purposes (version retrieval vs. image search).
- 共享行为: Both open an HTTP connection to a URL；Both read input line by line using BufferedReader
- 行为差异: getVersion reads a single line and returns a version string; googleImageSearch reads all lines and parses HTML.；getVersion has no side effects; googleImageSearch populates a list and modifies UI.；googleImageSearch includes user-agent header and replaces spaces in URL.
- 修正建议: Incorporate task-specific context (e.g., method name and surrounding class) to disambiguate purpose.；Use dataflow analysis to track how inputs and outputs are used.

### case_id=4464 FP partial_functionality

- 方法: `get` vs `getPagina`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches game record data from a URL via HTTP GET, parses lines into GameRecord array, filters comment lines.
- B 摘要: Fetches the entire content of a URL as a single concatenated string, handling exceptions by returning error messages.
- 静态失败原因: The static model likely relied on lexical overlap (both use URL, BufferedReader, readLine, etc.) and common boilerplate for HTTP fetching, missing the semantic differences in data transformation and return type.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely labeled non-clone because the functions have different return types and distinct processing logic; they are not semantically equivalent despite sharing the common pattern of reading from a URL.
- 共享行为: Both open a URL connection and read input line by line；Both handle IOException and other exceptions
- 行为差异: A uses HttpURLConnection with custom headers; B uses URL.openStream；A decodes lines into GameRecord objects; B concatenates all lines into a single string；A returns array of GameRecord or null; B returns string or error string；A filters out lines starting with '#'; B does not filter
- 修正建议: Incorporate dataflow analysis to track how the input stream is processed (e.g., transform to GameRecord vs concatenation)；Use type information to differentiate return types；Consider the structure of output (array vs string) as a distinguishing feature

### case_id=4465 FN benchmark_preference_bias

- 方法: `main` vs `createButtonCopyToClipboard`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Downloads a KMZ file from a URL, extracts its zip entries, and writes them to local files.
- B 摘要: Creates a SWT button that copies an environment report to the clipboard when clicked.
- 静态失败原因: Static BERT correctly predicted non-clone due to low lexical overlap and distinct API usage; the failure is in benchmark label consistency.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: The BCB label is likely an annotation error; the functions are semantically unrelated even under broad Type-4 criteria.
- 共享行为: No shared behavior
- 行为差异: Different domains: file extraction vs GUI clipboard copy；Different APIs: ZipInputStream/FileOutputStream vs SWT/IOUtils；Different control flow: sequential extraction vs event-driven listener
- 修正建议: Re-annotate BCB label for this pair；Train model to rely more on semantic structure than possible spurious correlations

### case_id=4466 FP lexical_or_api_overlap

- 方法: `readData` vs `createJAR`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Parses string tokens to populate various sets and maps, and reads a configuration file.
- B 摘要: Creates a JAR file or directory and writes a serialized object to it.
- 静态失败原因: The model may have over-relied on superficial lexical overlap (e.g., both mention 'File', 'IOException', 'catch') or the presence of common API tokens like 'FileOutputStream' and 'file', leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels as non-clone because the functions have entirely different purposes and no shared functionality beyond boilerplate exception handling.
- 共享行为: Both perform file I/O operations；Both use try-catch for exception handling
- 行为差异: Function A parses configuration strings and builds data structures; Function B handles file system operations and JAR creation；Function A is about initialization of character sets; Function B is about packaging and exporting data
- 修正建议: Enhance model to better capture long-range semantic context and ignore boilerplate code；Incorporate data flow analysis to distinguish different use of similar APIs

### case_id=4467 FN benchmark_preference_bias

- 方法: `testCopy_readerToOutputStream_Encoding` vs `doGet`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Tests copying from a Reader to an OutputStream with UTF16 encoding and verifies the result.
- B 摘要: Handles an HTTP GET request to dynamically serve a web page with user authentication, caching, and logging.
- 静态失败原因: Static models like GraphCodeBERT rely on syntactic and structural patterns; these functions differ greatly in length, control flow, and API usage. The lack of overlapping tokens (Jaccard 0.047) and different method names leads the model to correctly predict non-clone, but BCB expects a clone based on partially similar I/O operations.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have considered them clones due to a broad interpretation that both involve streaming data with encoding or both perform input-output operations. Alternatively, the truncation may hide a code segment in B that resembles A's logic, but based on visible code, similarity is minimal.
- 共享行为: Both use Java I/O streams (InputStream, OutputStream, Reader, Writer).；Both involve writing to an output destination.
- 行为差异: Function A is a unit test; Function B is a servlet handler.；Function A performs a specific copy operation with encoding; Function B has complex control flow for page retrieval, permission checks, and caching.；Function A uses IOUtils.copy; Function B uses PrintWriter and manual output writing.；Function A has no networking or request handling; Function B depends on HttpServletRequest and HttpServletResponse.
- 修正建议: Re-evaluate BCB annotation for this pair to confirm if it should be considered clone.；If annotation is correct, static models need to capture high-level functional similarity beyond token overlap, such as dataflow patterns for I/O operations.

### case_id=4468 FN benchmark_preference_bias

- 方法: `copyFile` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Copies a local file from source to destination using FileChannel.transferTo.
- B 摘要: Fetches a resource from a URL or cache as an InputStream, with caching and HTTP handling.
- 静态失败原因: Static model correctly predicted non-clone (0) based on low token overlap and semantic difference; the error is a false negative relative to BCB label, but BCB label may be incorrect.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled as clone due to both dealing with file/stream operations, but that is overly broad, likely a labeling error.
- 共享行为: Both involve file I/O operations；Both handle input streams
- 行为差异: A is a simple local file copy; B involves URL connection, caching, and conditional logic；A writes to a file; B returns an InputStream；B has complex caching and HTTP logic absent in A
- 修正建议: Re-evaluate BCB label for this pair; consider removing if not truly a clone.；Improve benchmark consistency by filtering out broad I/O similarities.

### case_id=4469 FN partial_functionality

- 方法: `getHTML` vs `doVersionCheck`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Retrieves HTML content from a URL and optionally writes it to a file.
- B 摘要: Checks for software version updates by parsing a remote version file.
- 静态失败原因: Static BERT models focus on token-level similarity and may overlook the high-level structural pattern of URL reading due to low token Jaccard similarity (0.218), different method names, and different operations within the loop. The model likely considered them non-clones because the specific logic diverges significantly.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label these as clones because both share the same fundamental pattern of fetching data from a URL and reading it line by line, which is a common boilerplate structure in Java. The differences in the internal processing (all lines vs. selective, file writing vs. GUI) are considered secondary in BCB's broad Type-3/Type-4 clone annotation.
- 共享行为: Both open a URL and read data line by line using BufferedReader and InputStreamReader.；Both handle IOException with error handling.；Both use a while loop to read lines until null.
- 行为差异: Function A returns the entire HTML content as a String; function B is void and does not return anything.；Function A writes the content to a file if dirPath is provided; function B does not write any data.；Function A processes all lines; function B only processes lines starting with '.version' or '.build'.；Function A uses HttpURLConnection with a custom User-Agent; function B uses url.openStream().
- 修正建议: Enhance model with dataflow analysis to capture common API usage patterns like URL reading.；Include more training examples of partial functionality clones where core structure is similar but processing differs.；Use graph-based representations that abstract away specific string manipulations.

### case_id=4470 FN partial_functionality

- 方法: `getHTML` vs `issueCommandToServer`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches HTML from a URL using HttpURLConnection and returns the page content as a string, optionally saving to a file.
- B 摘要: Sends a command to a server via POST and returns the server response as a string.
- 静态失败原因: Static BERT/GraphCodeBERT relies heavily on token overlap (Jaccard=0.2069), which is low due to different method names, URL handling, and extra file writing, failing to recognize the shared abstract pattern of reading from a URL connection.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB considers Type-3/Type-4 clones, accepting functions that perform similar high-level functionality (network I/O string retrieval) despite differences in protocol, parameters, and error handling.
- 共享行为: Both open a URL connection.；Both read the response line by line, appending to a string buffer/builder.；Both return the concatenated response string.
- 行为差异: A uses HTTP GET (no output), B uses HTTP POST (writes form data).；A has optional file writing, B does not.；A has exception handling and disconnects, B throws IOException and closes streams.；A uses StringBuilder, B uses StringBuffer.
- 修正建议: Use dataflow analysis to capture the common pattern of opening a connection, reading lines, and concatenating.；Incorporate program dependency graphs to abstract away superficial differences.；Train on more diverse clone pairs with low token overlap but similar structure.

### case_id=4471 FP boilerplate_overlap

- 方法: `encrypt` vs `perform`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Encrypts a plaintext string using MD5 and Base64 encoding.
- B 摘要: Handles a Struts action request to classify a concept, involving session validation, parameter extraction, HTTP communication, and result parsing.
- 静态失败原因: The static BERT/GraphCodeBERT model likely overfit on superficial lexical patterns like 'try { ... } catch (Exception e)' and method return type 'String', missing the drastic semantic differences. The model may also struggle with long-range dependencies in code_b's lengthy implementation.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the two methods perform fundamentally different operations with no shared functionality or structural similarity beyond basic Java boilerplate.
- 共享行为: Both are public methods that may throw exceptions (though A catches internally, B declares).；Both use try-catch blocks for exception handling.
- 行为差异: Code A performs cryptographic hashing and encoding; Code B performs web request handling and business logic for classification.；Code A is short and single-purpose; Code B is long and complex with multiple sub-tasks.；Code A is synchronized; Code B is not.；Code A does not declare any exceptions; Code B declares IOException and ServletException.
- 修正建议: Incorporate control-flow and data-flow analysis to capture functional semantics.；Use graph-based representations that model dependencies between statements.；Train with more diverse negative examples that share boilerplate but have different purposes.

### case_id=4472 FN partial_functionality

- 方法: `getContent` vs `runScript`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches HTTP response content from an HttpUriRequest using HttpClient, reads line by line with BufferedReader, returns the concatenated string.
- B 摘要: Fetches remote script content by constructing a URL from the applet code base and script name, reads byte by byte with BufferedInputStream, returns the concatenated string or 'error!' on exception.
- 静态失败原因: Static BERT models rely heavily on token and syntactic overlap (Jaccard 0.101) and may miss the functional similarity due to different APIs (HttpClient vs URL.openStream) and I/O patterns (BufferedReader vs BufferedInputStream), failing to capture the shared intent of downloading content.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels functions that perform the same high-level task (e.g., fetching remote content) as Type-3 or Type-4 clones, even with low token overlap and different implementations.
- 共享行为: Both retrieve remote content over HTTP and return it as a string.
- 行为差异: Input: A takes an HttpUriRequest object, B takes a String script name.；Reading method: A reads lines, B reads individual bytes.；Error handling: A throws Exception, B catches and returns 'error!'.；Character encoding: A specifies UTF-8, B does not.
- 修正建议: Incorporate dataflow analysis to identify common patterns like 'open connection -> read all -> return'.；Use models that can abstract away API differences, e.g., via code summarization or higher-level intent recognition.；Augment training data with more diverse implementations of the same functionality.

### case_id=4473 FP lexical_or_api_overlap

- 方法: `getWebPage` vs `getUser`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a web page from a URL and returns its content as a string, throwing an Error on IOException.
- B 摘要: Retrieves a User by login, first checking a DAO, then falling back to parsing a config file from the classpath, returning the User or null.
- 静态失败原因: The static model likely over-fitted on the shared pattern (BufferedReader, readLine loop) and missed semantic divergence due to local attention, low token overlap, and lack of data flow awareness.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labeled as non-clone because the functions have distinct purposes, different I/O types, and only superficial syntactic overlap in reading lines, which is common boilerplate.
- 共享行为: Both use BufferedReader and InputStreamReader to read from an input stream.；Both read lines in a while loop and concatenate string content.；Both have try-catch blocks for exception handling.
- 行为差异: Different input types: URL object vs String userlogin.；Different output types: String vs User object.；Function B has conditional logic (null check, token parsing) and interacts with a DAO for saving.；Function A throws an Error; B prints stack trace and returns null.
- 修正建议: Incorporate method signatures and return types as features.；Use data flow or control flow graphs to capture semantic differences.；Include class-level context (e.g., DAO usage) to distinguish functionality.

### case_id=4474 FN partial_functionality

- 方法: `createSettingsIfNecessary` vs `modifyApplicationMessage`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Creates a settings file from a bundled resource if it does not exist.
- B 摘要: For a given locale, copies a default English properties file if locale-specific file does not exist, then modifies a specific message in that file.
- 静态失败原因: Low token Jaccard similarity and differences in method names, I/O classes, and exception handling caused the model to miss the structural pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB annotates as clone because both implement a common pattern of conditionally creating a file from a default template, despite domain and additional modification differences.
- 共享行为: Check if a file exists；If file does not exist, create it and copy content from a default source
- 行为差异: A only creates and copies; B additionally modifies a property value.；A uses a bundle resource stream; B uses a FileReader to copy from an English file.；A handles I/O with try-finally and OutputStream; B uses try-catch and FileWriter/Reader.；A is for settings.xml; B is for locale-specific properties files.
- 修正建议: Enhance model with structural pattern recognition for file creation/copying.；Use data flow analysis to capture the 'check-existence-then-copy' pattern.；Include more diverse examples of this pattern in training.

### case_id=4475 FN boilerplate_overlap

- 方法: `import_hints` vs `read`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a hints file or URL, parses integer tokens, and places puzzle pieces on a board.
- B 摘要: Reads a file or URL as a stream and delegates to another read method, returning a status code.
- 静态失败原因: Static BERT/GraphCodeBERT likely focused on the low token Jaccard (0.214) and different method names, missing the structurally identical file/URL opening boilerplate and exception handling pattern.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB often labels clones with high structural similarity and overlapping I/O patterns even if core logic differs, considering broad Type-3 or partial functionality similarity.
- 共享行为: Open input from a local file or URL based on the string argument；Handle IOException with a try-catch block returning an error indicator；Use similar if-else branching to decide between URL and file access
- 行为差异: Function A parses tokenized lines into piece ID, column, row, rotation and modifies board state；Function A returns boolean true on success, false on failure; Function B returns an integer status；Function B delegates actual reading to another 'read' method, while Function A performs all processing inline
- 修正建议: Use data flow analysis to capture that both methods have identical I/O setup and exception control flow；Incorporate structural similarity metrics based on AST or CFG that highlight shared control flow patterns

### case_id=4476 FP lexical_or_api_overlap

- 方法: `makeBackup` vs `readData`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Copies all files from a source directory to a destination directory, creating the destination if needed and preserving timestamps.
- B 摘要: Reads a configuration file (tibwn.ini) and populates multiple hash sets and mappings for Tibetan transliteration data.
- 静态失败原因: The model likely relied on superficial similarity (both use File, streams, loops) and ignored the completely different data flow and output.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clones when functions perform entirely different tasks, even if they share common API usage or loops.
- 共享行为: Both use file I/O and loops；Both handle exceptions with try-catch
- 行为差异: A copies files; B parses a config file and builds in-memory data structures；A uses FileInputStream/FileOutputStream; B uses BufferedReader and StringTokenizer；A's output is files on disk; B's output is hash sets and maps；A deals with directory creation and last-modified timestamps; B does not
- 修正建议: Increase training data diversity for file I/O functions with distinct purposes；Use contrastive learning to separate functions with similar APIs but different semantics；Incorporate data flow analysis to track the transformation of data

### case_id=4477 FP boilerplate_overlap

- 方法: `get` vs `readIntoList`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Makes an HTTP GET request with location headers, reads response lines, decodes game records, and returns them as an array.
- B 摘要: Reads an HTML page from a URL, extracts link labels between '>' and '</a>', creates JMenuItems for each, and populates a map.
- 静态失败原因: The model likely overemphasized overlapping boilerplate tokens (BufferedReader, readLine, URL, catch) and missed deeper semantic differences in the processing logic and return types.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clones because the functions have completely different purposes and outputs; only a common reading pattern exists, not functional similarity.
- 共享行为: Open a URL and read lines from its input stream；Use try-catch to handle exceptions
- 行为差异: A uses HttpURLConnection with custom headers and returns GameRecord array; B opens URL directly and populates a map of JMenuItems；A filters out lines starting with '#'; B parses HTML anchor tags；A returns null on failure; B is void and silently catches exceptions
- 修正建议: Incorporate structural features like method signature (return type, parameters) to distinguish patterns.；Use dataflow analysis to capture that A returns data while B mutates an input map.

### case_id=4478 FN partial_functionality

- 方法: `httpRequestByPOST` vs `CheckUrl`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Performs an HTTP POST request with parameters, reads the entire response, and returns it as a string, or returns null on error.
- B 摘要: Performs an HTTP GET request to a URL, reads the first line of the response, and returns it as a string, or returns empty string on error.
- 静态失败原因: Low token overlap (Jaccard 0.1667), different APIs (HttpClient vs URLConnection), different control flow, and different error handling.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label as clone because both functions perform an HTTP request and read the response text, considered a similar task despite different methods and response sizes.
- 共享行为: Both make an HTTP request and read the textual response, returning it as a string.
- 行为差异: HTTP method: POST vs GET；Parameter handling: sends list of NameValuePair vs none；Response reading: full body vs first line；Error handling: returns null and sets fields vs prints stack trace and returns empty string
- 修正建议: Incorporate semantic understanding of HTTP operations；Use graph-based similarity to recognize different library implementations of same task；Consider functionality equivalence at a higher abstraction level

### case_id=4479 FP partial_functionality

- 方法: `readTwitterFead` vs `CheckUrl`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads all lines from a fixed Twitter timeline URL using Apache HttpClient and returns the concatenated response as a string.
- B 摘要: Reads the first line from a given URL using java.net.HttpURLConnection and returns it as a string.
- 静态失败原因: A static embedding model may have focused on surface-level API similarities (e.g., use of HttpClient, HttpGet, BufferedReader) and overlooked the critical difference in loop structure (while loop vs single readLine). The model likely dismissed the URL difference as a minor parameterization issue, leading to a false positive.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely labeled this as non-clone because the core functionality differs: one reads the entire response, the other only the first line. This is a significant behavioral difference that outweighs the common HTTP GET pattern, even under broad Type-3/Type-4 definitions.
- 共享行为: Both perform an HTTP GET request to a URL.；Both read the response content using a BufferedReader.；Both return the read content as a String.；Both handle exceptions by printing stack traces.
- 行为差异: Function A uses a hardcoded URL; Function B takes a URL parameter.；Function A reads all lines of the response; Function B reads only the first line.；Function A uses Apache HttpClient; Function B uses java.net.HttpURLConnection.；Function A checks for HTTP status 200 and logs errors on failure; Function B does not check status.
- 修正建议: Incorporate dataflow analysis to distinguish loops from single calls.；Use structural differencing to capture loop semantics.；Add features like whether a method reads all lines or just one.；Consider parameterization and constant values in URL to differentiate fixed vs variable endpoints.

### case_id=4480 FP lexical_or_api_overlap

- 方法: `run` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a URL content line by line, extracting version, url, and additional information, and notifies listeners.
- B 摘要: Searches Google Images for an artist/album, parses HTML to extract image URLs, and stores them.
- 静态失败原因: Static models may rely on lexical and API-level overlap (e.g., both use URL, BufferedReader, read lines) and miss the semantic differences in parsing logic and purpose, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the core functionality is distinct: one is a generic URL reader for metadata, the other is a specific image search scraper.
- 共享行为: Both use URL connection to fetch web content；Both read content line by line using BufferedReader
- 行为差异: Different parsing logic: code_a extracts first two lines as metadata, code_b splits HTML to extract image URLs；Different error handling: code_a has specific network error messages, code_b shows generic error dialog；Code_a notifies listeners, code_b stores results in a list
- 修正建议: Train models to focus on the overall goal and data flow rather than just sequence of API calls；Add negative sampling with similar API but different intent；Incorporate task-specific context or output analysis

### case_id=4481 FN lexical_or_api_overlap

- 方法: `copyResource` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource (URL or local file) to a destination file using byte-by-byte stream I/O.
- B 摘要: Copies a file to another file using NIO FileChannel transfer for efficient bulk transfer.
- 静态失败原因: Low token overlap (0.207) and different APIs (InputStream vs FileChannel) cause the model to focus on surface-level token differences rather than the underlying semantic goal.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB often labels functions as clones if they share the same overall goal (file copying) despite differences in API usage or implementation details, as Type-3 or Type-4 clones.
- 共享行为: Both copy data from a source to a destination file；Both handle I/O resources with proper closing
- 行为差异: copyResource can read from URL or local file; copyFile only from File；copyResource uses byte-by-byte loop; copyFile uses channel transferTo；copyResource does not use try-with-resources; copyFile uses finally block
- 修正建议: Incorporate API-level knowledge or use alignment of similar functionalities across different APIs；Use data augmentation with diverse implementations of the same task

### case_id=4482 FN partial_functionality

- 方法: `DialogHelper` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Constructor that creates a dialog with an image and allows saving the image to a file via file copy.
- B 摘要: Method that launches a NexOpen project, handling Maven pom.xml files, Hibernate configuration, and reverse engineering file setup.
- 静态失败原因: Static BERT models like GraphCodeBERT rely on lexical and structural similarity, which is minimal here (low Jaccard). The two functions share very few tokens and have different API calls. Additionally, the semantic context (GUI vs. Eclipse plugin) is completely different, and the models may not capture the weak file-copy similarity at a high level.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as Type-4 clones because they both implement file copying functionality (copy from source to destination), despite the vast difference in surrounding code. The presence of file copy logic in both functions might lead BCB to label them as functionally similar in a broad sense.
- 共享行为: Both perform file I/O operations (reading a source and writing to a destination).；Both check existence of a destination file before writing.
- 行为差异: Function A is a GUI constructor; Function B is a launch configuration method.；Function A copies an image file using FileChannel; Function B manipulates XML documents and writes properties.；Function A uses Swing components; Function B uses Eclipse/Java EE APIs.；Function A includes user interaction (dialog confirmations); Function B is purely programmatic.
- 修正建议: Use pre-training on a diverse corpus covering multiple frameworks (Swing, Eclipse) to improve comprehension of different contexts.；Incorporate dataflow information to capture shared operations like file copying across different code structures.；Augment training data with examples of partial functionality similarity to teach models to recognize such broad clones.

### case_id=4483 FP other

- 方法: `actionPerformed` vs `copyFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Handles GUI action events to set Graphviz, ImageMagick, and other user preferences with file choosers and error handling.
- B 摘要: Copies a file from source to destination using NIO file channels with proper resource cleanup.
- 静态失败原因: Despite low token Jaccard (0.042), static BERT might have been misled by shared Java keywords (e.g., 'File', 'IOException', 'try-finally') or structural patterns like null checks, but lacking understanding of overall semantics.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB labels non-clone due to completely different functionality: one is a complex UI handler, the other a basic I/O operation.
- 行为差异: Function A is a GUI event handler with multiple conditions and preference updates; Function B is a simple file copy utility.；Function A interacts with UI components (JFileChooser, JTextField); Function B performs pure file I/O.；Function A has extensive state changes and conditional logic; Function B has a linear flow.
- 修正建议: Incorporate more negative examples with low lexical but distinct semantics.；Use function-level context or documentation embeddings.；Leverage dataflow analysis to distinguish different side effects.

### case_id=4484 FN partial_functionality

- 方法: `getResourceAsStream` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.75`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Retrieves a resource from a URL, caches it locally, and returns an InputStream to the cached file with HTTP and caching logic.
- B 摘要: Copies a source file to a destination file using NIO FileChannel with try-finally resource management.
- 静态失败原因: The static BERT model likely relies on token/lexical overlap, which is very low (Jaccard 0.099). It may not capture abstract functional similarity like 'reading from a source and writing to a destination', especially when one involves complex HTTP and caching and the other is a simple NIO copy. The model might focus on method names and specific API calls, which differ significantly.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as 'file copy' or 'stream copy' functions at a high level, ignoring the network and caching details. The core functionality of reading from a source and writing to a destination is similar, which could be seen as Type-4 (semantic) clone.
- 共享行为: Both perform file I/O that reads from a source and writes to a destination.；Both use try-catch-finally or try-with-resources for stream/channel management.；Both involve creating input and output streams/channels and closing them after use.
- 行为差异: Code_a reads from a URL (remote resource) while code_b reads from a local file.；Code_a includes HTTP connection handling, caching logic, and conditional cache updates.；Code_b is a straightforward copy without any caching or network operations.；Code_a uses BufferedInputStream/OutputStream with byte-by-byte copy; code_b uses NIO FileChannel transferTo.
- 修正建议: Include data flow analysis to identify abstract I/O patterns.；Use contrastive learning with functional flow graphs that represent source-destination relationships.；Develop models that can generalize beyond concrete API calls to high-level operations like 'copy stream'.

### case_id=4485 FN benchmark_preference_bias

- 方法: `main` vs `createDialogArea`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Main method that constructs HTTP POST parameters and sends a request to RenRen API, printing the response.
- B 摘要: Creates a dialog area with a browser or text widget, reads a license file from the bundle, and displays its content.
- 静态失败原因: The static model correctly predicted non-clone (0) due to low token overlap (0.084) and different APIs; it did not fail in this case.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as a clone due to the shared pattern of opening a URL and reading with BufferedReader, but the overall functionality is completely different.
- 共享行为: Use URL to open a connection or stream；Use BufferedReader to read lines；Handle IOException
- 行为差异: One is a network API call, the other is UI setup；Function A sends an HTTP POST request; Function B reads a local resource；Different return types (void vs Control)；Different exception handling (one prints stack trace, other ignores)
- 修正建议: Remove this pair from clone list if strict equivalence is required；If BCB wants partial functionality, clarify guidelines to avoid false positives

### case_id=4486 FN benchmark_preference_bias

- 方法: `copyFile` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Copies a file from source to destination using FileChannel transfer.
- B 摘要: Launches a NexOpen project configuration by processing pom.xml files, setting properties, and scheduling an install action.
- 静态失败原因: Static model correctly predicted non-clone because token overlap is low, code structures differ significantly, and semantic purposes are distinct; the model captured the mismatch.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled as clone due to both methods performing file I/O operations and checking file existence, but this is a weak similarity and likely an annotation error.
- 共享行为: Check if file exists and create if not；Use file streams and I/O operations
- 行为差异: Code A is a simple file copy; Code B involves complex launch logic；Code B includes XML handling, project configuration, and persistent property modifications；Code A is generic; Code B is domain-specific to NexOpen projects
- 修正建议: Verify BCB annotation for correctness; likely it is a false positive clone label；Improve BCB annotation guidelines to avoid such broad Type-4 classifications

### case_id=4487 FP lexical_or_api_overlap

- 方法: `loadURL` vs `postXml`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Loads a URL (GET) with optional basic authentication, writes response to a temporary file, and updates a status label.
- B 摘要: Sends an XML SOAP POST request with custom headers and returns the response as a string.
- 静态失败原因: Static BERT models often rely on lexical and API token overlap. Both functions share common API calls (URLConnection, BufferedReader) and similar control structures (while loop reading lines), causing the model to overestimate similarity despite different high-level semantics.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels non-clones when functions are functionally different (Type-4). Here, the purposes (file download vs. SOAP request) are distinct, so BCB labels 0 (non-clone).
- 共享行为: Both open a URL connection and read the response using BufferedReader.；Both handle IOException to some extent.
- 行为差异: A uses HTTP GET (default), B uses HTTP POST.；A writes response to a file, B returns response as a string.；A implements basic authentication, B sets SOAP-specific headers and timeout.；A updates a UI label during download, B does not.
- 修正建议: Incorporate data-flow analysis to track how input/output is used (e.g., file vs. string).；Add method-level context such as return type and method name to distinguish intentions.；Use graph-based models that capture structural differences (e.g., control-flow graphs).

### case_id=4488 FN partial_functionality

- 方法: `main` vs `copy`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Extracts all zip entries from a URL to local files using a buffer.
- B 摘要: Recursively copies a file or directory, skipping unchanged files and '.svn' directories.
- 静态失败原因: Low token overlap and syntactic differences caused the model to miss the abstract 'copy' pattern; static models struggle with high-level semantic equivalence.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels pairs as clones if they perform similar abstract operations like 'copy' regardless of input source or destination type, focusing on functional similarity.
- 共享行为: Both read from an input source and write to an output file using a byte buffer loop.
- 行为差异: A handles zip entries extraction; B handles recursive file/directory copy.；A reads from URL (http/file) and ZipInputStream; B reads from local file system.；A logs each entry; B does not.；B has skip logic for unchanged files; A does not.
- 修正建议: Train on more diverse copy operations to learn the abstraction.；Incorporate dataflow or program dependency features to identify read-write loops.；Use contrastive learning to align different implementations of the same high-level task.

### case_id=4489 FN benchmark_preference_bias

- 方法: `getDatasetsList` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: A synchronized method that caches and returns a list of strings fetched from a URL.
- B 摘要: A main method that constructs an HTTP POST request to a social media API and prints the response.
- 静态失败原因: The static BERT model correctly predicted non-clone (low token overlap), but BCB labeled as clone, so the model did not fail; the BCB label may be erroneous.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider these as Type-4 clones because both read from a URL line by line, but this is too broad; the overall functionality differs significantly.
- 共享行为: Both open a URL and read lines from an input stream using BufferedReader
- 行为差异: A is synchronized and uses caching; B is not synchronized and does not cache.；A returns a List; B prints output to console and does not return anything.；A makes a GET request; B makes a POST request with many parameters.；A handles IOException and throws RuntimeException; B throws IOException only.
- 修正建议: Review BCB annotation guidelines to avoid overly broad Type-4 labeling.；Use a model that captures long-range semantic intent rather than shallow API usage.；Incorporate dataflow analysis to distinguish caching vs. non-caching behavior.

### case_id=4490 FN benchmark_preference_bias

- 方法: `copyFile` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Copies a file using FileChannel.transferTo from source to destination, returns boolean success.
- B 摘要: Builds a website for editing by processing multiple pages with XML transformations and file writes.
- 静态失败原因: Static models like GraphCodeBERT likely correctly predicted non-clone (0) due to low token similarity (Jaccard=0.042) and distinct structural patterns. The model did not fail; rather, the BCB annotation is likely an outlier.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as clone due to both methods containing file I/O operations (FileInputStream) and possibly a misinterpretation of partial functionality overlap (both write to files). However, the functional similarity is minimal, and the annotation appears inconsistent with typical BCB guidelines.
- 共享行为: Both use FileInputStream to read files.；Both involve writing to files (FileOutputStream in A, FileWriter via FileSystem in B).
- 行为差异: A is a simple file copy; B is a complex multi-step website generation.；A has a boolean return; B returns void and throws multiple exceptions.；A has no loops or conditionals (except try-catch); B has loops over pages and multiple conditions.；A uses FileChannel.transferTo; B uses transformers and string buffers.
- 修正建议: Re-evaluate BCB annotation for this pair to ensure consistency.；Incorporate semantic similarity or functionality clustering to filter spurious clones.

### case_id=4491 FP lexical_or_api_overlap

- 方法: `createDialogArea` vs `executePost`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Creates a SWT dialog area with license content from a file.
- B 摘要: Executes an HTTP POST request and returns the response.
- 静态失败原因: The model likely focused on overlapping tokens such as 'BufferedReader', 'IOException', 'try', 'catch', 'finally', 'InputStream', and 'StringBuffer', which are common in many I/O routines, and missed the high-level semantic differences between UI creation and network requests.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels as non-clone because the functions have completely different purposes (UI vs network I/O), despite some overlapping API usage patterns like BufferedReader. The overall logic and context are distinct.
- 共享行为: Both use BufferedReader to read line by line；Both use try-catch-finally for stream handling；Both call e.printStackTrace() on exception；Both use StringBuffer to accumulate strings
- 行为差异: Function A is for UI dialog creation (SWT), Function B is for network communication (HTTP POST)；Function A opens a local resource (bundle), Function B opens a remote URL connection；Function A creates a Composite UI element, Function B does not have any UI；Function A handles Browser and Text widgets, Function B handles URL parameters and response
- 修正建议: Incorporate broader context like method signatures, class names, or package information to capture domain differences.；Use a model that better understands control flow and data flow differences, such as GraphCodeBERT with data flow edges.；Add a post-filter to ignore common I/O boilerplate patterns when they dominate similarity.

### case_id=4492 FN boilerplate_overlap

- 方法: `getFile` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, optionally modifies its endpoint XML attribute, and saves it to a temporary directory.
- B 摘要: Tests a custom StraightStreamReader by writing bytes to a file and reading them back using various read methods, verifying correctness.
- 静态失败原因: The static model likely over-relied on token overlap (e.g., File, FileOutputStream, IOException) and failed to capture the distinct high-level intents (downloading vs. testing) due to lack of global semantic understanding.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may have considered them clones due to shared boilerplate (file creation, reading, exception handling) and similar API usage, despite different high-level purposes.
- 共享行为: Both involve file I/O (creating, writing, reading, deleting files)；Both use File, FileInputStream, FileOutputStream, IOException
- 行为差异: A involves network download and XML parsing; B is purely local stream testing；A modifies XML content; B verifies byte-level correctness；A returns a file path; B produces console error messages；A has multiple exception types (MalformedURLException, ParserConfigurationException, SAXException); B only catches IOException
- 修正建议: Incorporate control flow and data dependency analysis；Use contrastive learning that penalizes mismatched high-level intents；Add code summarization features to capture functional purpose

### case_id=4493 FP boilerplate_overlap

- 方法: `PhoneSetImpl` vs `downloadModel`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a phone set file from a URL line by line, parsing entries into a map while skipping comment lines.
- B 摘要: Downloads an RDF/XML model from a URL using HTTP with custom headers, reads it into a Model object, and returns it.
- 静态失败原因: The static model likely overemphasized the common API usage pattern (URL, InputStream, exception handling) and structural similarity (open, read, close), treating boilerplate as evidence of clone.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels these as not clones because they perform vastly different domain-specific operations (phone set parsing vs. RDF model download) despite sharing a URL-reading pattern.
- 共享行为: Both open a URL connection and read from an InputStream；Both handle IOException
- 行为差异: First function reads line-by-line; second reads entire content at once via model.read；First processes text lines into a map; second parses RDF/XML into a Model object；First has no HTTP header customization; second sets Accept and Accept-Language headers；First returns void; second returns Model
- 修正建议: Improve model's ability to distinguish between shared infrastructure code and actual semantic behavior；Incorporate task-specific embeddings or read-retrieve-read mechanisms；Use dataflow analysis to differentiate diverse processing logic after data read

### case_id=4494 FP lexical_or_api_overlap

- 方法: `sendPost` vs `GetResponse`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Sends an HTTP POST request with parameters and returns the response body as a string.
- B 摘要: Sends an HTTP GET request and returns the response body as a string if status is OK.
- 静态失败原因: The static model likely over-indexed on common API tokens (HttpURLConnection, BufferedReader, readLine, etc.) and the structural pattern of reading an HTTP response, ignoring the crucial difference in request method and parameter sending.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically treats functions with different HTTP methods (POST vs GET) as non-clones because the core semantic differs despite shared boilerplate code for stream reading.
- 共享行为: Both open an HTTP connection；Both read the response line by line into a string；Both return the response string；Both use BufferedReader and InputStreamReader
- 行为差异: A uses POST method, B uses GET method；A sets request properties (Accept-Language) and sends parameters via output stream；B checks response code (HTTP_OK) before reading；A catches Exception broadly, B catches specific exceptions (MalformedURLException, IOException)
- 修正建议: Incorporate control-flow or data-flow features that capture the request method (GET vs POST)；Use static analysis to distinguish setting output streams vs not；Train with more negative examples that share API tokens but differ in core functionality

### case_id=4495 FN benchmark_preference_bias

- 方法: `doGet` vs `MotixFileItem`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Handles HTTP GET requests for page navigation, with logging, caching, and permission checks.
- B 摘要: Constructor for MotixFileItem that reads an InputStream, extracts metadata, and optionally processes an image.
- 静态失败原因: Static BERT/GraphCodeBERT produced a false negative because the functions have extremely low token overlap (Jaccard=0.047) and no structural similarity; the strict model correctly identifies them as non-clones, so in this case the model did not fail—the BCB label is likely erroneous.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled these as clones due to a broad interpretation of I/O-related functionality, possibly considering both as 'file handling' or 'stream processing', though the actual semantics are very different.
- 共享行为: Both involve I/O operations (reading streams/writing responses)；Both include exception handling
- 行为差异: A is a servlet method handling HTTP request/response lifecycle; B is a constructor initializing a file item object；A performs page lookup, user permission checks, and caching; B reads image data and stores it；A writes to HTTP response; B stores data in internal fields；A has extensive logging; B does not
- 修正建议: Re-evaluate the BCB annotation for this pair; it may be a false positive；Use a more rigorous clone definition that requires shared behavioral semantics；Filter out pairs with low token similarity to avoid noise in training data

### case_id=4496 FN partial_functionality

- 方法: `createDialogArea` vs `register`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Creates a dialog area with a browser or text widget to display license text from a resource file.
- B 摘要: Registers a user by encoding password, setting metadata, calling a PHP forum URL to create forum user, persisting entity, and sending confirmation email.
- 静态失败原因: The low token Jaccard (0.1429) and distinct method names led the model to focus on surface-level differences, missing the partial similarity in the I/O reading pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider the common I/O pattern (open stream, read lines, handle IOException) as a Type-3 clone, overlooking the entirely different application contexts.
- 共享行为: Both open a URL stream and read lines using BufferedReader；Both handle IOException by printing stack trace or logging
- 行为差异: One is UI generation, the other is user registration；Different widget usage (SWT vs JPA and URLConnection)；Different exception handling details
- 修正建议: Enhance models to capture partial functional similarity through API usage patterns or data flow analysis；Incorporate code summarization or semantic role labeling to compare high-level intent

### case_id=4497 FP lexical_or_api_overlap

- 方法: `handleHandshake` vs `executePost`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Handles a Minecraft handshake packet, validates the server key, and either logs in or shuts down the connection.
- B 摘要: Executes an HTTP POST request to a given URL with parameters and returns the response as a string.
- 静态失败原因: The model likely overemphasized lexical and API overlap (URL, BufferedReader, InputStreamReader, exception handling) and ignored the fundamentally different control flow and domain-specific logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clones when functions have different business logic and purpose, even if they share API calls. The handshake and HTTP post are unrelated tasks.
- 共享行为: Both perform network I/O using URL and streams；Both read lines from an HTTP response using BufferedReader；Both handle exceptions with printStackTrace
- 行为差异: Function A uses GET request for Minecraft session validation, function B uses POST for generic HTTP；Function A has specific logic for handshake (username checks), function B is a generic utility；Function A sends packets or shuts down network, function B returns a string or null；Function A has conditional branching on username value, function B does not
- 修正建议: Incorporate data flow and control flow analysis to distinguish different purposes；Use representation learning that captures method-level semantics beyond token sequences；Add context about method signatures and class names to disambiguate

### case_id=4498 FP lexical_or_api_overlap

- 方法: `importSequences` vs `downloadModel`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads FASTA sequences from a URL and populates internal lists of names and sequences.
- B 摘要: Downloads an RDF model from a URL using HTTP, parses it, and returns a Model object.
- 静态失败原因: Static BERT models often rely on lexical and structural patterns; both functions share URL opening, InputStream handling, and similar exception handling, leading to high similarity in token sequences despite different semantics.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically requires strong functional similarity; these are clearly different tasks (sequence import vs model download) so they are not labeled as clones.
- 共享行为: Both open a URL and read data from an InputStream；Both handle MalformedURLException and IOException；Both use try-catch blocks for error handling
- 行为差异: A imports sequences into collection fields; B returns a Model object；A parses FASTA format; B reads RDF/XML；A uses a custom ImportHelper; B uses model.read()；A handles EOFException; B does not
- 修正建议: Incorporate method names and return types into the embedding；Use dataflow analysis to distinguish different data transformations；Add contrastive learning on tasks with different semantics but similar API usage

### case_id=4499 FN partial_functionality

- 方法: `testNetworkHTTP` vs `import_hints`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: A test method that opens multiple HTTP connections, reads and discards responses, and logs operations.
- B 摘要: A method that reads puzzle hint data from a file or URL, parses piece positions and rotations, and places them on a board.
- 静态失败原因: Static models like BERT or GraphCodeBERT rely on token-level similarity and structural embeddings, which are low here (Jaccard 0.122). The models fail to capture the high-level functional similarity of network I/O operations due to different method names, control flow, and data processing logic.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label these as clones because they share the common pattern of network I/O using standard Java classes (URL, HttpURLConnection, BufferedReader), which is a typical Type-4 semantic clone in code that reads from a URL and processes lines, even if the specific processing differs.
- 共享行为: Both use URL and BufferedReader/InputStreamReader to read data from a network resource.；Both handle IOException with try-catch.；Both read lines in a loop using readLine().
- 行为差异: Function A reads from multiple URLs sequentially, while Function B reads from one source (URL or file).；Function A discards all read data, whereas Function B parses and uses the data to place puzzle pieces.；Function A is void and only logs errors, while Function B returns a boolean indicating success.；Function A does not parse the lines, just reads until null; Function B tokenizes lines and processes integers.
- 修正建议: Train models to recognize common API usage patterns even when business logic differs.；Incorporate data-flow analysis to detect shared I/O patterns.；Use contrastive learning with pairs that share only partial functional similarity.

### case_id=4500 FN partial_functionality

- 方法: `addIDs` vs `handler`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Scrapes a specific metabolite database web page to extract metabolite IDs and properties, populating a PeakListRow object.
- B 摘要: Generic web page scraper that extracts substrings between given markers and stores them in a map using the result parameter.
- 静态失败原因: The low token Jaccard (0.18) and different method signatures likely caused the model to focus on lexical/surface differences rather than the higher-level common pattern of HTTP reading and HTML parsing.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as 'web scraping to extract information' tasks, thus functionally similar despite different specific implementations, fitting Type-4 (semantic similarity) clone criteria.
- 共享行为: Both open a URL and read lines from an HTML page；Both parse strings from lines using conditional checks and substring operations；Both handle IOExceptions
- 行为差异: Function A has specific logic for different metabolite types (Metabolites, Analytes, PubChem, etc.)；Function B is generic and uses parameters (target) to determine parsing markers；Function A returns an integer score; Function B returns void；Function A updates a PeakListRow with multiple fields; Function B updates a Map<String,String>
- 修正建议: Train models to recognize common programming patterns like 'read from URL and parse lines' via dataflow or AST-based features；Use contrastive learning with examples that share structural patterns despite different APIs
