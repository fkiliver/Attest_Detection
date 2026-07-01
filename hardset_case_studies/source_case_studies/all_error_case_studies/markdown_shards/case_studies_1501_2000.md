# Error Case Studies 1501-2000

- Source model: `configured-llm`
- Cases: `1501` to `2000`

### case_id=1501 FP boilerplate_overlap

- 方法: `main` vs `testStandardTee`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Main method that generates adapter classes from a Prolog file, involving parsing, class writing, and resource serialization.
- B 摘要: Test method that verifies TeeWriter correctly copies a string to two destinations and reports byte count.
- 静态失败原因: The model likely over-generalized on superficial similarities such as the presence of try-catch blocks, file operations, or common Java keywords, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB non-clone label is correct because the two functions are completely unrelated in functionality and context, despite both being Java methods.
- 共享行为: none meaningful
- 行为差异: Complete difference in purpose: A is a code generator, B is a unit test；Different domain: Prolog/adapter generation vs. I/O utility testing；Different APIs and control flow: A involves complex library interactions, B is straightforward
- 修正建议: Improve model to better distinguish boilerplate code from core functionality；Incorporate functional semantics via data flow or more advanced structural analysis；Use contrastive learning with hard negatives that share structural patterns but differ in purpose

### case_id=1502 FP lexical_or_api_overlap

- 方法: `init` vs `importSequences`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Initializes the servlet by loading controller classes from a registry file using the class loader.
- B 摘要: Imports sequences from a URL resource, parsing lines to extract names and sequences.
- 静态失败原因: Static BERT models may rely on lexical and structural overlap (e.g., both have try-catch, loops, and stream reading) and may miss the semantic difference in the actual operations (loading classes vs. parsing sequences). The token Jaccard is only 0.18, but perhaps the pre-trained embeddings capture some similarity due to common control flow.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as not clone because the functions have entirely different purposes and logic, despite superficial structural similarities.
- 共享行为: Both read data from input streams and handle exceptions.
- 行为差异: Function A loads Java classes from a classpath resource, function B parses sequence data from a URL.；Function A reads lines and loads classes, function B tokenizes and builds sequence strings.；Different data structures and outputs.
- 修正建议: Improve training data diversity for non-clone pairs with structural similarity.；Incorporate data-flow analysis or more contextual embeddings that capture the purpose beyond surface patterns.

### case_id=1503 FN benchmark_preference_bias

- 方法: `main` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Reads multiple input files specified as arguments and writes their concatenated lines to an output file.
- B 摘要: Launches a NexOpen project in Eclipse, validates Maven POM files, handles Hibernate configuration, and sets project properties.
- 静态失败原因: Static BERT methods often rely on token overlap and structural similarity; the low token Jaccard (0.065) and vastly different structures make it correctly predict non-clone, so the 'failure' is due to BCB label being inconsistent with semantic equivalence.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as clone due to a broad interpretation of 'partial functionality' where both methods involve file handling and some form of output generation, but this is likely an erroneous label.
- 共享行为: Both methods perform file I/O operations (reading/writing) and handle exceptions.
- 行为差异: Code A is a simple file concatenation; Code B is a complex Eclipse launch configuration.；Code A operates on command-line arguments; Code B operates on Eclipse platform objects and projects.；Code A has no branching logic; Code B has multiple conditional checks and nested structures.；Code A does not modify project state; Code B modifies persistent properties and creates files.
- 修正建议: Re-evaluate BCB annotation for this pair to ensure consistency.；Use clone detection methods that incorporate deeper semantic understanding beyond token overlap.；Consider domain-specific features or program dependency graphs for such heterogeneous methods.

### case_id=1504 FP boilerplate_overlap

- 方法: `doVersionCheck` vs `loadURL`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Checks for software version updates by reading a remote version file and calling another version check method.
- B 摘要: Loads a VRML file from a URL, optionally with authentication, and writes it to a temporary file while updating a status label.
- 静态失败原因: Static BERT models may rely on token-level similarity and common API usage (URLConnection, BufferedReader, readLine) and ignore the overall program structure and specific logic (extracting vs writing).
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically requires substantial functional overlap for Type-3/Type-4 clones; here the core functionality (version checking vs file download) is different, so BCB would likely label as non-clone.
- 共享行为: Both open a URL connection and read lines from the input stream.
- 行为差异: doVersionCheck reads lines to extract version strings; loadURL writes all lines to a file.；doVersionCheck does not write to files; loadURL writes to a temporary file.；doVersionCheck shows wait cursor and error dialog; loadURL updates status label and prints to stdout.；loadURL supports HTTP basic authentication; doVersionCheck does not.
- 修正建议: Improve model's ability to distinguish between different data processing logic within similar boilerplate patterns.；Use structure-aware encodings (e.g., AST-based) to capture control flow and data transformations.

### case_id=1505 FP lexical_or_api_overlap

- 方法: `callApiPost` vs `downloadModel`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Sends a POST request with parameters and returns the response input stream after checking expected status code.
- B 摘要: Downloads an RDF model from a URL via HTTP GET and returns the parsed Model object.
- 静态失败原因: Static BERT likely over-relied on lexical overlaps (URL, openConnection, InputStream, IOException) and similar control flow patterns, missing the semantic difference in HTTP method and return type.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels non-clones when functions have distinct core purposes despite similar boilerplate; here one is a generic HTTP POST caller, the other is a model downloader, so BCB correctly assigned 0.
- 共享行为: Both open a URL connection and obtain an input stream.；Both handle I/O exceptions with try-catch blocks.；Both set some request headers.
- 行为差异: callApiPost uses POST method with parameters; downloadModel uses GET without parameters.；callApiPost validates response code and conditionally returns stream; downloadModel always reads stream into Model.；Different return types (InputStream vs Model).；Different error handling (custom BingMapsException vs RuntimeException).
- 修正建议: Incorporate deeper semantic analysis of HTTP method, parameter handling, and return type.；Use graph-based representations that capture data flow differences (e.g., output usage).

### case_id=1506 FN partial_functionality

- 方法: `copyResource` vs `copyExternalResource`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource (URL or file) to a destination file using byte-by-byte stream.
- B 摘要: Copies a source file to a destination file using NIO FileChannel transferFrom.
- 静态失败原因: Low token Jaccard (0.192) and different method signatures, parameters, and I/O APIs (byte stream vs NIO) caused the model to miss semantic similarity due to syntactic dissimilarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considers them clones because both perform the core functionality of file copying, accepting broad Type-3/Type-4 similarity despite different APIs and parameter structures.
- 共享行为: Both copy data from a source to a destination file.；Both close resources after use.
- 行为差异: Source: A can read from URL or file; B only from file.；I/O method: A uses InputStream/OutputStream byte-by-byte; B uses FileChannel.；Exception handling: A throws generic Exception; B throws IOException.；Resource closing: A closes directly; B uses closeQuietly helper.
- 修正建议: Train on more diverse code patterns with varying APIs but equivalent behavior.；Incorporate data-flow or control-flow graphs to capture semantic equivalence.；Use graph-based models (e.g., CodeBERT with AST) to better handle structural differences.

### case_id=1507 FP boilerplate_overlap

- 方法: `lookupFutureEvents` vs `SRWGuiClient`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Retrieves future events from Meetup API, parsing JSON response into a list of Event objects.
- B 摘要: Constructor for a simple Swing browser that loads and displays an initial URL, handling XML/XSL transformations.
- 静态失败原因: The static BERT/GraphCodeBERT model likely overemphasized the shared boilerplate (URL, BufferedReader, while loop reading lines) and structural patterns, while missing the high-level semantic difference in method purpose and domain-specific logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would not label these as clones because the overall functionality is completely different despite some low-level I/O boilerplate overlap. The intended purpose (API data retrieval vs. GUI browser) is distinct.
- 共享行为: Both use URL and BufferedReader to read data from a URL stream；Both handle IOException in a try-catch block
- 行为差异: A focuses on parsing JSON and building Event objects; B builds a GUI with JPanel, JEditorPane, and applies XSL transformations；A returns a list of events; B sets up a JFrame and makes it visible；A uses specific Meetup API fields; B processes XML with potential XSLT styling
- 修正建议: Incorporate method signature and context (class name, parameters, return type) into the model；Use dataflow or dependency analysis to distinguish between I/O as a utility vs. core logic；Train on more diverse examples to recognize when boilerplate is incidental

### case_id=1508 FN benchmark_preference_bias

- 方法: `copyFile` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.1`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: copyFile copies a file from one location to another using FileChannel.transferTo.
- B 摘要: buildSiteForEdit processes a website for editing, reading XML configuration and page files, applying transformations, and writing the edited content to output files.
- 静态失败原因: Static BERT correctly predicted non-clone due to low token overlap and clear semantic differences; the model did not fail.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as clone due to both methods reading and writing files, but this is an overly broad interpretation of Type-4 similarity; likely an annotation error.
- 共享行为: Both involve file I/O operations
- 行为差异: copyFile is a simple, single-purpose method for copying a single file；buildSiteForEdit is a complex method performing multi-step site generation；copyFile uses FileChannel for efficient binary copy；buildSiteForEdit uses character streams and string manipulation
- 修正建议: Verify annotation correctness; if BCB label is correct, document rationale for file I/O as clone criterion；Otherwise, correct BCB label to non-clone

### case_id=1509 FN partial_functionality

- 方法: `fileDownload` vs `doVersionCheck`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a file from a URL to a local directory, writing all bytes to a file named 'download.pdf'.
- B 摘要: Connects to a URL to fetch version check data, parses lines for build numbers, and triggers further version check if found.
- 静态失败原因: Static BERT models rely heavily on token similarity and surface-level structure. With low Jaccard similarity (0.2168) and differing method names, parameters, and overall purpose, the model predicted non-clone, missing the underlying shared URL reading pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely labels this as a clone because both functions implement the common pattern 'open URL, read contents, process them', despite different processing. This is typical Type-3 with overlapping structure and similar control flow.
- 共享行为: Both open a URL connection and read content using InputStream/BufferedReader.；Both have a try-catch block handling exceptions.；Both read until end of stream and close the reader.
- 行为差异: A writes all read bytes to a file; B parses lines for specific prefixes.；A uses FileOutputStream to write; B calls another method with parsed data.；A handles generic Exception; B handles IOException only.；B shows/hides wait cursor and shows error dialogs; A has no UI feedback.
- 修正建议: Enhance training data with examples that share sub-patterns but differ in overall task.；Incorporate AST-based features to capture structural similarities in control flow and API usage.；Use dataflow analysis to differentiate between writing to file and parsing for data.

### case_id=1510 FN partial_functionality

- 方法: `register` vs `seeURLConnection`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Registers a new user by encoding password, setting default authority, creating a forum user via HTTP URL, and sending confirmation email.
- B 摘要: Opens an HTTP URL connection to a fixed address and reads the response into a string buffer for logging.
- 静态失败原因: Static model like GraphCodeBERT likely focused on overall semantic meaning and high-level functionality (user registration vs. simple URL read), and the low token overlap made it deem them non-clones. It may have missed the shared sub-pattern due to attention focusing on the broader context or because the pattern is embedded in a longer function.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider this a Type-4 clone because both functions contain the essential pattern of opening a URLConnection and reading its content line by line, even though the surrounding functionality differs. The shared subroutine is a common reusable pattern.
- 共享行为: Both open a URL connection, create a BufferedReader from the input stream, read lines, and close the reader.
- 行为差异: Function A performs many additional operations (password encoding, authority setting, email sending, exception handling for registration).；Function B only reads a fixed URL and logs the output.；The URL construction and the purpose of reading the URL are different.
- 修正建议: Train model to detect partial functional similarity, perhaps by using hierarchical representations or focusing on subroutines.；Use data augmentation to create pairs where only a sub-task is shared.

### case_id=1511 FP lexical_or_api_overlap

- 方法: `doVersionCheck` vs `loadURL`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Checks for new version by reading a version file from a URL and comparing build numbers.
- B 摘要: Downloads a file from a URL, optionally with authentication, writes to a temporary file, and updates a status label with file size.
- 静态失败原因: Static BERT over-emphasized lexical and API overlaps (URL, BufferedReader, readLine) and structural similarities, missing the difference in high-level intent and output behavior.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely deems them non-clones because the overall functionality is distinct (version check vs. file download), despite sharing some I/O patterns.
- 共享行为: Both open a URL and read lines using BufferedReader.
- 行为差异: Function A compares version/build strings; Function B writes content to a file.；Function A shows a wait cursor and messages; Function B updates a label with file size.；Function B includes optional HTTP Basic Authentication; Function A does not.；Function A uses InputStream; Function B uses URLConnection and FileWriter.
- 修正建议: Incorporate task-level semantic understanding or add contrastive learning on intent differences.；Use dataflow or dependency analysis to capture the full effect of operations (e.g., writing to file vs. conditional checks).

### case_id=1512 FN partial_functionality

- 方法: `sendExceptionToServer` vs `init`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends exception details as HTTP POST to an error server.
- B 摘要: Loads controller classes from a registry file using class loader.
- 静态失败原因: Static BERT likely focused on low token overlap (0.15 Jaccard) and different method names/structures, missing the broad I/O pattern similarity that BCB prioritized.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled these as clones due to both performing I/O operations on a URL resource and reading lines with BufferedReader, combined with similar exception handling patterns, despite different overall goals.
- 共享行为: Both use URL to open a connection/stream；Both use BufferedReader to read lines；Both handle IOException
- 行为差异: Different primary purpose (error reporting vs class loading)；Function A writes data to the URL output stream before reading response, Function B only reads；Different data being processed (exception details vs class names)；Different output actions (printing result vs loading classes)
- 修正建议: Incorporate dataflow analysis to differentiate write vs read operations；Use larger context including method signatures and class hierarchy；Improve training data to reduce false negatives from BCB's broad annotations

### case_id=1513 FN benchmark_preference_bias

- 方法: `testTrainingBackprop` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Unit test that trains a neural network on XOR data using FANN and asserts that the mean squared error is below a threshold.
- B 摘要: Complex method that builds an HTML page for editing by reading XML templates, processing pages, and writing output files, involving file I/O, DOM manipulation, and string transformations.
- 静态失败原因: Static model correctly predicted non-clone (0) due to large structural and semantic differences, low token Jaccard (0.025), and distinct method names/logic. The 'failure' is from the BCB label perspective.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: Possible misinterpretation: BCB annotators may have considered both as 'file processing' methods due to superficial I/O similarity, but actual functionality differs completely. This pair likely represents a benchmark annotation error or an overly broad interpretation of Type-4 clones.
- 共享行为: Both involve file I/O operations (reading/writing files)；Both handle exceptions (throws IOException)
- 行为差异: Function A is a unit test for neural network training with fixed XOR dataset; Function B builds an HTML editing site with complex XML and string processing；Function A has short, simple logic; Function B has lengthy, complex logic with many parameters and conditional branches；Function A's output is a boolean assertion; Function B's output is writing files to disk
- 修正建议: Re-evaluate BCB annotation for this pair; likely should be non-clone；Establish clearer criteria for Type-4 clones to avoid false positives based on trivial I/O similarity

### case_id=1514 FN partial_functionality

- 方法: `main` vs `copyResourceToFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.4`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a URL, unzips it, and writes each entry to a file.
- B 摘要: Copies a resource file from the classpath to a destination file using IOUtils.copyStream.
- 静态失败原因: Low token overlap (0.128) and use of different APIs (URL, ZipInputStream vs MatsimResource, IOUtils) caused the model to focus on surface differences, missing the high-level stream copying abstraction.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as stream copy operations, viewing the URL handling and unzipping as minor variations, thus labeling as Type-4 clone.
- 共享行为: Both involve reading from an input stream and writing to an output stream.
- 行为差异: A downloads from a specific URL and unzips, extracting multiple files; B copies a single file without unzipping.；A uses ZipInputStream and BufferedOutputStream; B uses IOUtils.copyStream and MatsimResource.；A has a while loop for multiple entries; B has a simple try-finally block.
- 修正建议: Enhance representation to capture common I/O patterns across different APIs.；Incorporate data flow analysis to identify stream copying operations.；Use graph-based models that abstract away specific method names and focus on control flow and data flow similarities.

### case_id=1515 FP lexical_or_api_overlap

- 方法: `doRawRequest` vs `run`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Sends an HTTP POST request with given data and returns the response body as a string.
- B 摘要: Loads a tile from a URL or file, reads its content, parses it into geometries, and adds it to the data source.
- 静态失败原因: The model likely overemphasized the lexical overlap of common API calls (URL, BufferedReader, readLine) and the similar control flow of reading lines, while ignoring the larger context and different overall goals of the functions.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically considers overall functional similarity. Despite a shared low-level pattern of reading from a URL, the two functions have completely different purposes and complexity levels, so BCB would likely label them as non-clones.
- 共享行为: Open a URL connection；Read lines from an input stream into a string；Handle IOException
- 行为差异: Function A is a simple synchronous HTTP POST helper; Function B is a complex tile loader that handles multiple protocols, file I/O, geometry parsing, and data structure updates.；Function B includes synchronization and checks for duplicate requests; Function A does not.；Function B parses geometries and updates a data source; Function A simply returns the response string.
- 修正建议: Include structural features that capture the overall function purpose and complexity, such as method name, class context, and data flow.；Use abstract syntax tree (AST) based comparison to differentiate high-level structure and logic.；Consider the presence of additional logic (e.g., geometry parsing, synchronization) that distinguishes the functions.

### case_id=1516 FP long_range_semantics

- 方法: `actionPerformed` vs `compress`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `static_summary_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: An actionPerformed method that handles various GUI commands to set preferences for Graphviz, ImageMagick, and other settings, updating UI components.
- B 摘要: A private method that concatenates multiple input files into one output file, and optionally compresses it using an external tool (YUI Compressor), logging the process.
- 静态失败原因: The long length of Function A (truncated in the case) may have caused the model to focus on local token overlaps like 'File', 'chooser', 'filename', 'path', missing the global semantic difference. Additionally, both functions involve file I/O patterns that might have been misaligned with the model's learned representations.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB labels as non-clone because the two functions have entirely different purposes: one is a GUI event handler for setting preferences, the other is a file concatenation and compression utility. There is no significant overlap in functionality or structure.
- 共享行为: Both interact with files；Both involve setting or using file paths
- 行为差异: Function A is a GUI event handler; Function B is a file processing utility；Function A updates UI elements and stores preferences; Function B performs I/O and compression；Function A handles many different commands; Function B has a single specific task；Function A uses JFileChooser and sets text fields; Function B uses FileInputStream/FileOutputStream
- 修正建议: Improve handling of long functions by using hierarchical or sliding window attention；Enhance training with more diverse long-range examples to prevent over-reliance on local token matches

### case_id=1517 FN partial_functionality

- 方法: `sendExceptionToServer` vs `executeHttpGet`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends exception details to a server via HTTP POST, reads response, and prints status.
- B 摘要: Executes an HTTP GET request to a URI and returns the response as a JSONObject.
- 静态失败原因: Low token overlap (0.13) and different API structures misled the model to ignore the common HTTP communication pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB considers both as HTTP client operations handling request/response, a broad functional similarity (Type-4 clone) often annotated in projects.
- 共享行为: Perform HTTP request to a remote server；Read response line by line using BufferedReader
- 行为差异: HTTP method: POST (A) vs GET (B)；Library: java.net (A) vs Apache HttpClient (B)；Parameters: multiple form fields (A) vs single URI (B)；Return type: void (A) vs JSONObject (B)
- 修正建议: Improve tokenization to include API class names (e.g., HttpURLConnection, HttpClient) in similarity.；Use graph-based representations capturing data flow of HTTP operations.；Add heuristic to detect network communication stubs across different libraries.

### case_id=1518 FP boilerplate_overlap

- 方法: `main` vs `decodeBody`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.85`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Parses a Prolog file, generates adapter classes, and writes them into a JAR file.
- B 摘要: Decodes an input stream's body based on content transfer encoding and writes it to a temporary file body.
- 静态失败原因: Likely misled by common Java boilerplate (try-catch, I/O classes) and structural patterns despite very low lexical overlap.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clone because functions have no meaningful behavioral overlap; they solve completely different problems.
- 共享行为: Both involve file/stream I/O and exception handling.
- 行为差异: Different overall purpose: adapter generation vs. body decoding.；Different input types and processing logic.；Different output: JAR file vs. Body object.
- 修正建议: Incorporate more detailed data-flow analysis.；Use graph-based representations that capture functional semantics.；Train on more diverse data to reduce overreliance on surface patterns.

### case_id=1519 FP lexical_or_api_overlap

- 方法: `main` vs `extractUninstallFiles`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Generates Java adapter classes from a Prolog file based on command-line arguments.
- B 摘要: Extracts uninstall files and handles upgrade logic for a software installer.
- 静态失败原因: The static BERT/GraphCodeBERT model likely over-relied on surface-level commonalities such as try-catch blocks, file operations, and loops, leading to a false positive prediction.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone due to completely different functionality and lack of any significant code reuse or structural similarity beyond basic Java constructs.
- 共享行为: Both perform file I/O operations；Both use exception handling with try-catch blocks；Both involve directory and file manipulation
- 行为差异: Function A is a command-line driver for code generation, while B is a private method for installer file extraction；A reads and parses Prolog files, B reads and writes JAR entries and class files；A generates adapter classes and serialized data, B manages uninstall scripts and versioned paths；A has no concept of upgrade or old version handling, B does
- 修正建议: Incorporate more context-aware training that captures program intent beyond token overlap；Use contrastive learning with hard negative pairs that have similar tokens but different semantics；Add structural features like control flow graph or data flow analysis

### case_id=1520 FN partial_functionality

- 方法: `process` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Processes a template to generate output files based on destination and template type, with error handling.
- B 摘要: Launches an Eclipse configuration to set up a NexOpen project by parsing POM files and copying resources.
- 静态失败原因: Low token similarity (Jaccard=0.106) and long code length cause static BERT to miss the superficial file I/O overlap, leading to a non-clone prediction.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB might consider both as involving file generation from templates, but the similarity is superficial; likely a mislabeling.
- 共享行为: Both perform file I/O operations and use InputStream/OutputStream.；Both include exception handling with try-catch-finally blocks.；Both use IOUtils for closing or copying streams.
- 行为差异: Different overall purpose: code generation vs. IDE project setup.；Different input parameters and output artifacts.；One uses Freemarker/XSLT templates, the other uses Maven POM and Hibernate configuration.
- 修正建议: Enhance model to recognize high-level functional patterns beyond token overlap.；Incorporate data flow or structure-aware features to distinguish genuine functional similarity from boilerplate.；Use larger context windows or hierarchical representations.

### case_id=1521 FN lexical_or_api_overlap

- 方法: `import_hints` vs `seeURLConnection`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Opens a file or URL to read puzzle hints, parsing tokens to place pieces on a board with rotation and hint setting.
- B 摘要: Opens a URL connection, reads the entire response into a string buffer, and logs it.
- 静态失败原因: GraphCodeBERT likely relied on code structure and data flow. The functions share only a small common pattern (URL opening), but the overall logic and purpose are different. The token overlap is low (10.8%), and the semantic graphs likely diverge after the initial URL opening. The model correctly identified them as non-clones, but BCB annotation may disagree due to broad clone definition.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB might consider the common URL-reading boilerplate as sufficient for a Type-3 clone (similar code with modifications). However, the core functionality differs significantly, so this seems like a borderline case.
- 共享行为: Both open a URL and read lines using BufferedReader and InputStreamReader.
- 行为差异: import_hints parses tokenized lines to extract piece data and manipulates a board; seeURLConnection simply appends lines to a StringBuffer.；import_hints returns boolean; seeURLConnection returns void and throws Exception.；import_hints has additional logic for piece placement and rotation; seeURLConnection does not.；import_hints includes conditional branch for file vs URL (but hardcoded to URL); seeURLConnection always uses URL.
- 修正建议: Improve detection of broader functionality similarity beyond exact token matching.；Consider control flow and data flow that includes common I/O patterns.；Use hierarchical or semantic grouping of input/output types.

### case_id=1522 FN boilerplate_overlap

- 方法: `modifyApplicationMessage` vs `createNew`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Modifies a property in a localized properties file, copying English file if missing.
- B 摘要: Creates a new file in a directory from an input stream, with special handling for '.request' files.
- 静态失败原因: Static models rely on token overlap and syntactic structure; low Jaccard (0.12) and different method names/logic lead to non-clone prediction. They miss the underlying shared file I/O boilerplate.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may label this as a clone because both methods involve writing to files with similar exception handling and resource management patterns, which is considered a functional similarity at a high level (Type-4 weak clone).
- 共享行为: Both perform file I/O operations using File and streams.；Both check file existence or conditions before writing.；Both handle exceptions during file operations.；Both involve writing data to a file.
- 行为差异: A reads and parses a properties file line by line to modify a specific entry; B copies an entire input stream without parsing.；A has logic to copy a default English file if locale file does not exist; B lacks that.；B has access control check and special handling for '.request' files; A does not.；A returns void; B returns a Resource object.
- 修正建议: Use dataflow graphs to capture file stream and resource handling patterns.；Incorporate function-level intent classification (e.g., file write, property manipulation).；Apply contrastive learning on pairs with similar API usage but different surface forms.

### case_id=1523 FP boilerplate_overlap

- 方法: `generateToken` vs `perform`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Computes SHA1 hash of input string and returns hex string.
- B 摘要: Processes a web request for concept classification, including session management, XML building, HTTP POST, response parsing, and forwarding.
- 静态失败原因: Possible boilerplate overlap (try-catch, return) and method signature patterns misled the model into ignoring semantic differences.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB requires at least partial functional similarity for Type-3/4; these functions have no common purpose or behavior.
- 行为差异: A is a simple cryptographic hash function; B is a complex web action with I/O and business logic.；A has no I/O or web dependencies; B extensively uses HTTP, sessions, and XML processing.；A returns a hex string; B returns an ActionForward for Struts navigation.；A uses only standard Java security library; B uses multiple custom and framework classes.
- 修正建议: Improve training data with more diverse non-clone pairs having low token overlap but similar structural patterns.；Incorporate data flow or API call sequence analysis to distinguish simple utilities from complex actions.；Use graph-based representations that capture control flow and data dependencies beyond lexical similarity.

### case_id=1524 FN lexical_or_api_overlap

- 方法: `invoke` vs `CheckUrl`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Performs an HTTP POST request with retry logic and deserializes JSON response to a generic type.
- B 摘要: Reads the first line from an HTTP GET response using URLConnection.
- 静态失败原因: The functions have very low lexical overlap (token Jaccard 0.11) and use completely different HTTP libraries (Apache vs standard), so static models relying on token/syntax similarity miss the underlying functional similarity.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB often labels Type-3/4 clones where both functions perform HTTP client operations despite different APIs and details, focusing on the shared high-level behavior of making a web request and reading a response.
- 共享行为: Both perform HTTP requests and read the response content.
- 行为差异: A uses HTTP POST, B uses HTTP GET.；A has retry logic on timeout, B does not.；A handles generic return types and JSON deserialization, B returns raw first line as string.；A uses Apache HttpClient, B uses standard Java URLConnection.
- 修正建议: Incorporate higher-level semantic representations capturing intent (e.g., HTTP request/response).；Use data-flow or control-flow graphs to identify common patterns (e.g., open connection, read input).；Train on more diverse functional transformations to recognize API-agnostic behaviors.

### case_id=1525 FN partial_functionality

- 方法: `runScript` vs `startScript`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a script from a URL derived from codebase and script name, returns its content as a string, with error fallback.
- B 摘要: Fetches a script from a URL attribute, reads it line by line, appends to a dialog object, with error causing system exit.
- 静态失败原因: The model likely weighted syntax and token overlap heavily, which are low (0.19), and ignored the high-level semantic similarity of the core script-fetching behavior.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels as clone when two functions perform the same core task (fetching and reading a remote script) even if the surrounding context differs, considering them functional clones.
- 共享行为: Both open a URL connection to a remote script file and read its entire content into a string buffer.
- 行为差异: A returns the string, B appends to dialog; A uses BufferedInputStream byte-by-byte, B uses BufferedReader line-by-line; A catches generic Exception and returns 'error!', B catches IOException and exits; A uses getCodeBase()+scriptName, B uses prop.getValue('src').
- 修正建议: Use data-flow analysis to detect that both functions open a URL stream and read content.；Train a model to recognize high-level task patterns (e.g., URL-to-string reading).；Apply program slicing to extract the common behavior.

### case_id=1526 FN partial_functionality

- 方法: `run` vs `CheckUrl`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Opens an HTTP GET connection with basic authentication, reads entire response line by line, updates timestamp and flags, stores result or error.
- B 摘要: Opens an HTTP GET connection to a given URL, reads only first line of response, returns it as string, prints stack trace on exception.
- 静态失败原因: Low token Jaccard similarity (0.2258) and structural differences (method signature, authentication code, loop vs single read) cause the model to predict non-clone; static BERT models lack the capacity to recognize high-level semantic similarity in partial functionality.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label these as clones because both implement 'download content from URL' functionality, overlooking differences in authentication and extent of reading, consistent with broad Type-3/Type-4 annotation guidelines.
- 共享行为: Both open an HTTP connection using HttpURLConnection and read the response content.
- 行为差异: Function A includes basic authentication header; function B does not.；Function A reads the entire response line by line; function B reads only the first line.；Function A has side effects (updates lastIteraction, sets finish, stores result); function B returns a value without side effects.；Function A stores exceptions in a field; function B prints stack trace.
- 修正建议: Incorporate API usage patterns (e.g., HttpURLConnection) as semantic features.；Use graph-based code representations to capture control and data flow similarities.；Train on partial function clones where core functionality is preserved but details vary.

### case_id=1527 FN partial_functionality

- 方法: `runInternal` vs `GetResponse`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: This function performs an HTTP GET request to fetch an OPDS catalog, handling redirects, progress display, content-type detection, and pagination.
- B 摘要: This function performs a simple HTTP GET request and returns the response content as a string.
- 静态失败原因: Static BERT-based models rely heavily on token overlap and structural similarity; the low Jaccard similarity and significant differences in length and control flow likely led to the negative prediction. The model may not have captured the underlying shared HTTP GET semantics.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider them clones because both implement the core pattern of making an HTTP GET request and reading the response, which constitutes partial functionality similarity, especially in the context of a benchmark that tolerates Type-4 clones with different implementations if the output behavior is similar (both retrieve data from URL). However, the specific purposes differ.
- 共享行为: Both open an HTTP URL connection and set request properties.；Both read the response input stream.；Both handle HTTP response codes and exceptions.
- 行为差异: Function a handles redirects, OPDS-specific parsing, content-disposition, progress updates, and pagination; function b does not.；Function a returns void and uses callbacks; function b returns the concatenated response string.；Function a has significantly more complex control flow with loops and error handling for partial loading.
- 修正建议: Improve model's ability to recognize functional patterns despite low token overlap, e.g., by using control flow graphs or data flow analysis to identify common API usage patterns.；Train on more diverse Type-4 examples to learn semantic equivalence at a higher abstraction level.

### case_id=1528 FN partial_functionality

- 方法: `readIntoList` vs `seeURLConnection`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads HTML lines from a URL, extracts command names, and populates a menu with action listeners.
- B 摘要: Reads all lines from a URL connection and logs the concatenated result.
- 静态失败原因: The static BERT model likely relied on token overlap (Jaccard=0.2) and missed the common I/O pattern due to differing method names, constants, and output operations.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider them clones because they share the core task of reading from a URL line by line, and differences are in the subsequent processing, which is often disregarded in Type-4 functional similarity.
- 共享行为: Both open a URL connection and read lines using BufferedReader.
- 行为差异: A parses each line to extract substrings and creates JMenuItems; B simply concatenates all lines.；A uses parameterized URL and map; B uses a hardcoded URL.；A adds action listeners; B just logs.
- 修正建议: Train on more diverse pairs that share a core operation but differ in post-processing.；Use data-flow or graph-based models to capture shared I/O structure.

### case_id=1529 FN benchmark_preference_bias

- 方法: `handler` vs `File2String`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.8`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Reads a URL line by line, extracts a substring between delimiters, and stores it into a map.
- B 摘要: Reads a file or classpath resource line by line, concatenates all lines into a single string, and returns it.
- 静态失败原因: The static model correctly identified the lack of functional equivalence due to low token overlap (0.23) and different core logic, thus predicting non-clone; it did not fail, but rather disagreed with the broad BCB annotation.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may label these as clones due to shared boilerplate of reading line by line from an input stream, considering them Type-4 clones where the high-level task is 'reading input and processing lines'.
- 共享行为: Open an InputStream from a source；Wrap in BufferedReader；Read lines in a while loop；Close the reader
- 行为差异: A extracts a substring using target delimiters; B concatenates entire lines；A modifies an input map; B returns a string；A reads from a URL; B reads from file or classpath resource；A has no fallback; B falls back to classpath if file not found
- 修正建议: Refine BCB annotation guidelines to exclude pairs with different core processing logic；Train models with more nuanced Type-4 examples that require similar output behavior；Use dataflow or structural analysis to capture functional differences beyond IO boilerplate

### case_id=1530 FN benchmark_preference_bias

- 方法: `doGet` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Handles HTTP GET request, retrieves a page by parameter or default, checks visibility, logs, and optionally caches the response to a temporary file.
- B 摘要: Copies a file from source to destination using FileChannel with synchronization and exception handling.
- 静态失败原因: The static model correctly predicted non-clone (0) as the functions are semantically very different; the BCB label of 1 appears to be an annotation error or overly broad interpretation.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as clone due to both methods performing file writing/copying operations and handling IOExceptions, but this is a superficial similarity not indicating semantic equivalence.
- 共享行为: Both involve file I/O operations (writing a temporary cache vs. copying a file)；Both handle IOException and use try-catch blocks
- 行为差异: Function A is a servlet method processing HTTP requests, while B is a utility method for file copying；A deals with web concepts (request, response, page visibility), B is purely file system；A has complex logic for page retrieval, caching, and user permissions; B is straightforward copy
- 修正建议: Remove this pair from the clone set or re-annotate as non-clone；Use stricter criteria for clone annotation to avoid such mismatches

### case_id=1531 FN benchmark_preference_bias

- 方法: `doGet` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Handles HTTP GET requests to retrieve and serve a portal page, with logging, caching, and access control.
- B 摘要: Copies a source file to a destination file using Java NIO FileChannel.
- 静态失败原因: Static BERT correctly predicted non-clone (0), but since the BCB label is 1, it is considered a false negative. The model succeeded in detecting dissimilarity.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: The BCB label (1) is likely an error in the dataset; these functions have no meaningful functional similarity and low token overlap.
- 共享行为: Both contain logging statements；Both handle exceptions
- 行为差异: Function A is a web request handler; Function B is a file utility.；Function A deals with HTTP parameters, session, and page rendering; Function B only copies bytes.；Function A writes to HTTP response; Function B writes to a file.；Function A has complex control flow; Function B is straightforward.
- 修正建议: Re-evaluate the BCB label for this pair; they are clearly not clones.；Consider excluding pairs with very low token similarity from positive clone annotations.

### case_id=1532 FN benchmark_preference_bias

- 方法: `main` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Main method that reads a dataset, iterates over zip entries containing rule parsing and evaluation, and prints average performance.
- B 摘要: Method that builds website pages by iterating over a list of pages, applying XML transformations, and writing output files.
- 静态失败原因: Low token overlap (Jaccard 0.08), different method names and libraries, and reliance on surface-level features caused failure to capture the high-level structural pattern of iterative input-output processing.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider these clones because both are batch processing methods that perform a loop over input items, read, process, and write output, representing a Type-4 semantic clone of 'data I/O pipeline'.
- 共享行为: Iterates over a collection of items (zip entries or pages)；Reads input streams and writes output streams；Uses loops and buffer mechanisms for I/O；Includes error handling and optional debug tracing
- 行为差异: Different domains: rule evaluation vs website generation；Different libraries: ZipFile/BufferedInputStream vs FileSystem/StreamSource；A uses temp files and console output; B directly writes to output files；A aggregates performance metrics; B transforms XML content
- 修正建议: Incorporate control flow graph features；Use dataflow analysis to detect I/O patterns；Train on broader clone definitions including Type-4 semantic clones

### case_id=1533 FN benchmark_preference_bias

- 方法: `getFile` vs `createOutputStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, optionally modifies an XML attribute, and returns the local file path.
- B 摘要: Reads a zip file, skips content.xml, copies all other entries to a new zip, then adds a new content.xml entry, returning a BufferedWriter to the output zip.
- 静态失败原因: The static BERT model likely relied on token overlap and method signatures, correctly identifying low similarity (Jaccard=0.0949) and different functionality, predicting non-clone. However, BCB's annotation considered them clones, possibly due to a lenient interpretation of functional similarity, causing a false negative from the model's perspective.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: Under BCB's Type-4 broad functional similarity, annotators might see both as 'file transformation' tasks involving reading, processing, and writing files, despite different domains (WSDL vs zip). However, the token Jaccard is very low, and the semantics differ significantly.
- 共享行为: Both perform file I/O operations with streams.；Both handle exceptions with try-catch blocks.；Both use File objects and FileOutputStream/FileInputStream.
- 行为差异: Function A downloads from a URL; Function B reads from a local file.；Function A modifies an XML document; Function B processes zip entries.；Function A returns a String file path; Function B returns a BufferedWriter.；Function A involves network and XML parsing; Function B involves zip compression and character encoding.
- 修正建议: Re-evaluate BCB annotation for this pair; consider it non-clone.；Train models with more nuanced functional similarity labels rather than binary clone/non-clone.；Incorporate domain-specific knowledge to distinguish file I/O patterns from actual functional equivalence.

### case_id=1534 FN boilerplate_overlap

- 方法: `File2String` vs `startScript`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a file or classpath resource line by line and returns its content as a string; exits on error.
- B 摘要: Reads a URL resource line by line and appends its content to a dialog object's script field; exits on error.
- 静态失败原因: Static models rely on token similarity (Jaccard 0.24) and syntactic structure. The methods have different names, classes, API calls (FileInputStream vs URL.openStream), and control flow. The model likely missed the underlying behavioral similarity due to these surface differences.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB considers both as 'read resource line by line' operations, a common boilerplate pattern. The core similarity in I/O reading and line accumulation outweighs the differences in source and destination, leading to a clone label.
- 共享行为: Reads text input line by line using BufferedReader；Accumulates lines into a string buffer；Handles IOException by printing error and calling System.exit
- 行为差异: Source: file/classpath resource vs. URL；Destination: returns String vs. modifies dialog.script；B has beginScript/endScript wrapper；Different error messages and conditional logic
- 修正建议: Expand training data with more I/O boilerplate clones；Incorporate dataflow or control flow features；Use code summarization to capture functional similarity

### case_id=1535 FN partial_functionality

- 方法: `copyResource` vs `test`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource from a URL or local file to a destination file using byte-by-byte reading and writing.
- B 摘要: Reads an XML resource, converts it to a byte array, then runs a traffic simulation loop for 10 minutes printing vehicle positions.
- 静态失败原因: Static BERT models rely on token and syntactic similarity; the low Jaccard (0.09) and different structures caused it to miss the weak partial-functional clone that BCB annotators considered.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB might label this as a Type-4 clone based on the high-level concept of 'copying a resource to an output stream', ignoring that B has much more behavior and different purpose.
- 共享行为: Both involve opening an InputStream from a resource；Both write data to an OutputStream (A: FileOutputStream, B: ByteArrayOutputStream)
- 行为差异: A copies to a file; B copies to a byte array and then uses it for simulation；A has error handling for missing resource; B assumes resource exists；B performs extensive additional processing (simulation, printing) that A does not；A is a private helper; B is a public test method
- 修正建议: Incorporate code summarization to capture high-level functional intent；Use control-flow and data-flow analysis to detect input-output patterns like resource copying；Consider API-level similarity (e.g., both use InputStream/OutputStream) as a soft signal

### case_id=1536 FN partial_functionality

- 方法: `copyResource` vs `write`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a single resource (URL or file) to a destination file using byte-by-byte I/O.
- B 摘要: Creates a JAR file by copying entries from multiple included JARs, excluding manifest and zero-size entries.
- 静态失败原因: The static model likely focused on structural and API differences (e.g., JAR-specific calls, loops, conditionals) and correctly identified they are not semantically equivalent, but missed the coarse functional similarity that BCB considers.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled these as clones due to the broad Type-4 category, where both functions share the core behavior of copying data from an input stream to an output stream, despite different high-level purposes.
- 共享行为: Both involve reading from an InputStream and writing to an OutputStream.；Both perform byte-level data copying.
- 行为差异: A copies a single source; B copies multiple sources from JAR files.；A uses explicit byte-loop; B uses IOUtils.copy utility.；B writes to JarOutputStream; A writes to FileOutputStream.；B filters out specific entries (manifest, zero-size); A does no filtering.
- 修正建议: Incorporate more abstract functional patterns, e.g., 'stream copy'.；Use higher-level representation like API call sequences with I/O roles.；Consider code semantics via data flow analysis of stream operations.

### case_id=1537 FN partial_functionality

- 方法: `login` vs `doVersionCheck`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Logs into LOLA by sending POST request with email and password, extracts session ID from response.
- B 摘要: Performs version check by reading a URL content and parsing build numbers from lines.
- 静态失败原因: Static BERT/GraphCodeBERT likely focused on the high-level API calls (URL, BufferedReader, try-catch) but failed to capture the domain-specific differences and the overall purpose (login vs version check). The low Jaccard score indicates low lexical overlap, but the structural similarity in I/O pattern may have been overshadowed by different strings and method calls.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as network I/O utilities that fetch data from a URL and process its content, thus representing a Type-4 functional clone.
- 共享行为: Opens a URL connection；Reads from a BufferedReader；Handles IOException/Exception；Uses URL.openStream or URLConnection
- 行为差异: A sends POST data (email/pw), B only reads GET；A returns session ID, B calls another method with parsed build numbers；A uses URLConnection with doOutput true, B uses URL.openStream；A uses OutputStreamWriter to write data, B does not write
- 修正建议: Enhance model with better representation of program purpose, e.g., using method names and comment analysis；Use dataflow analysis to track how data is produced and consumed；Incorporate context from surrounding classes or packages

### case_id=1538 FP lexical_or_api_overlap

- 方法: `googleImageSearch` vs `checkForUpgrade`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Searches Google Images for artist/album combinations and collects image URLs.
- B 摘要: Checks for software upgrades by querying a remote server, parses license/upgrade data, and updates the local database.
- 静态失败原因: The static BERT/GraphCodeBERT model likely relied on token-level similarity and overemphasized the shared API usage patterns (URL, HttpURLConnection, BufferedReader) while ignoring the distinct functional intents. The low token Jaccard (0.1133) should have indicated non-clone, but the model might have been misled by the sequential pattern similarity.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically only labels as clones if there is significant functional overlap (Type-1 to Type-4). Here, the only commonality is using HTTP, which is too generic. BCB correctly labels as non-clones.
- 共享行为: Both open an HTTP connection to a URL；Both read HTTP response using BufferedReader
- 行为差异: A searches for images; B checks for software upgrades；A parses HTML; B parses XML-like response；A adds URLs to a list; B updates database and UI；A is instance method; B is static method
- 修正建议: Improve training to distinguish between generic API usage and actual functional logic；Incorporate data-flow analysis or control-flow graphs to capture functional intent；Use more negative examples with similar API usage but different semantics

### case_id=1539 FN benchmark_preference_bias

- 方法: `modifyApplicationMessage` vs `unzipEntry`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Modifies a properties file by reading an existing file or copying a default, then updating or adding a key-value pair for a specific locale.
- B 摘要: Extracts a single entry from a zip file to an output directory, creating parent directories as needed.
- 静态失败原因: Static BERT/GraphCodeBERT likely failed because it correctly identified no semantic similarity, but BCB label is questionable.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might consider them clones due to superficial similarity in file handling boilerplate (File, FileReader, FileWriter vs ZipFile, ZipEntry), but the core functionality is completely different.
- 共享行为: Both perform file I/O operations；Both handle file existence and creation
- 行为差异: Function A modifies text content of a properties file；Function B extracts binary data from a zip archive；Function A handles locale-specific files；Function B deals with directory structure and zip entries
- 修正建议: Improve BCB annotation consistency；Add more diverse non-clone pairs

### case_id=1540 FP lexical_or_api_overlap

- 方法: `getWebByUrl` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches a web page by URL and saves its HTML content to a local file, optionally recursively fetching linked URLs.
- B 摘要: Searches Google Images for the current artist and album, fetches the result page, and extracts image URLs into a list.
- 静态失败原因: The model overfitted on common API usage patterns (URL, URLConnection, BufferedReader, while readLine) and exception handling structure, missing the semantic difference in the purpose and output.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled this as non-clone because the two functions perform fundamentally different tasks (download web page vs. parse image search results) despite sharing common boilerplate code for HTTP fetching.
- 共享行为: Both open a URL connection and read from an input stream.；Both use BufferedReader to read lines of text.；Both have try-catch exception handling.
- 行为差异: A writes the entire web page to a file; B extracts only image URLs from the response.；A recursively processes URLs found on the page; B does not.；A uses specific parameters (url, charset, fileIndex); B uses instance variables.；B checks a condition (artist change) before executing; A does not.
- 修正建议: Train with more diverse non-clone pairs that share API calls but have different intents.；Incorporate data flow analysis to distinguish different output behaviors.

### case_id=1541 FN partial_functionality

- 方法: `copyResource` vs `CopyTo`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource (URL or file) to a destination file using byte streams.
- B 摘要: Copies an image file to a destination file using character streams.
- 静态失败原因: Static model likely focuses on token-level differences (e.g., FileReader vs InputStream, URL handling) and low Jaccard similarity, missing the shared copying algorithm pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels Type-3/4 clones as similar if they perform the same high-level file copying task, even with different I/O streams and resource resolution.
- 共享行为: Both copy data from a source to a destination file using a read-write loop.
- 行为差异: copyResource handles URL and file existence, uses byte streams; CopyTo uses character streams and assumes a field 'image' as source.；Error handling differs: copyResource throws generic Exception, CopyTo catches exceptions in finally block.
- 修正建议: Abstract I/O stream types to focus on the copying loop structure.；Use dataflow analysis to identify read-write loops.

### case_id=1542 FP lexical_or_api_overlap

- 方法: `doFinishLoadAttachment` vs `readData`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Handles the completion of loading an attachment, either saving it to external storage or opening it with an intent.
- B 摘要: Reads configuration data by parsing comma-separated strings and a file into sets and maps.
- 静态失败原因: The model likely made a false positive due to low-level lexical or API overlaps (e.g., both use File, try-catch blocks) and failed to capture the completely different overall purposes and control flows.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would not consider these clones because they are functionally unrelated with no code reuse or similar algorithm.
- 共享行为: No meaningful shared behavior
- 行为差异: One deals with attachment handling while the other initializes data structures；A uses Android-specific APIs (Attachment, ContentResolver, Intent) while B uses file parsing and tokenization；A involves user interaction (Toast, startActivity) while B is purely internal setup
- 修正建议: Use models that capture long-range dependencies and overall program semantics；Incorporate structural features like AST or CFG；Train with more negative examples of superficially similar but semantically different functions

### case_id=1543 FP lexical_or_api_overlap

- 方法: `getPagina` vs `getTicketsForQueue`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: getPagina fetches a web page content as a string using URL and BufferedReader.
- B 摘要: getTicketsForQueue retrieves a list of tickets from a REST API by making an HTTP GET request with query parameters and parsing the response.
- 静态失败原因: Static BERT models may have been misled by lexical and API usage similarities (e.g., both use BufferedReader, readLine, HTTP response handling), overlooking the differences in overall logic and return types.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the functions have distinct high-level purposes and low token similarity (0.114). Even with broad Type-3/4 tolerance, the functional overlap is minimal.
- 共享行为: Both perform HTTP requests and read the response line by line using BufferedReader.
- 行为差异: Different return types: String vs List<RTTicket>.；Different URL construction: simple URL from string vs complex query parameters.；Different response parsing: entire content concatenated vs parsing ticket IDs.；Different error handling: simple error messages vs custom exceptions and logging.
- 修正建议: Incorporate method signatures and return types into the representation.；Use graph-based or flow-based models to capture data dependencies and control flow differences.；Train on more diverse examples to distinguish between generic HTTP fetching and domain-specific API clients.；Leverage function-level contextual embeddings from pretrained code models like CodeBERT with contrastive learning.

### case_id=1544 FN boilerplate_overlap

- 方法: `postData` vs `File2String`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends an HTTP POST request with given parameters and reads the response without using it.
- B 摘要: Reads a file from disk or classpath into a string, printing debug info and exiting on failure.
- 静态失败原因: The static model did not fail—it correctly predicted non-clone. The BCB label is likely incorrect due to overemphasis on common I/O patterns.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB might have labeled these as clones due to both reading from an InputStream and using BufferedReader, but that is a low-level boilerplate similarity, not functional equivalence.
- 共享行为: Both perform I/O operations using streams；Both use BufferedReader and InputStreamReader；Both close resources after use；Both handle exceptions (though differently)
- 行为差异: Function A writes data to an HTTP connection then reads response; Function B only reads from a file or URL；Function A discards the response; Function B returns the content；Function A uses PrintStream for output; Function B uses StringBuffer；Function A throws Exception; Function B prints messages and calls System.exit on errors
- 修正建议: Improve annotation guidelines to focus on high-level semantics rather than low-level stream usage；Use dataset filtering to remove pairs that only share generic I/O patterns without functional similarity

### case_id=1545 FP lexical_or_api_overlap

- 方法: `get` vs `lookupFutureEvents`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches game records from a URL using HTTP GET with custom headers for latitude, longitude, and count, parsing lines into GameRecord objects.
- B 摘要: Fetches future events from the Meetup API using an HTTP GET request, parses JSON response, and maps results to Event objects with multiple fields.
- 静态失败原因: The static model likely captured high-level syntactic patterns common to many HTTP GET/parse functions (URL creation, BufferedReader, while loop, collection append) but failed to recognize the completely different data processing logic (line-based vs JSON) and different output types.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically considers functions that perform different API calls and data transformations as non-clones, even if both involve HTTP GET and parsing. The overall functionality and data handling differ significantly.
- 共享行为: Both perform an HTTP GET request to a URL；Both read response line by line；Both parse the response into a collection of objects
- 行为差异: Function A uses custom request headers for location/count; function B appends parameters to URL；Function A filters out lines starting with '#' and decodes them; function B parses JSON array；Function A returns an array or null; function B returns a list or throws exception；Function A is static; function B is instance method
- 修正建议: Improve model's ability to differentiate between line-oriented and structured parsing；Incorporate semantic understanding of data flow and transformation；Add attention to method signatures and return types

### case_id=1546 FN partial_functionality

- 方法: `main` vs `transferWSDL`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a fixed URL and extracts all entries from the zip archive to the current directory.
- B 摘要: Downloads a WSDL file from a given URL with optional basic authentication and saves it to a temporary file, returning the file path.
- 静态失败原因: Static BERT/GraphCodeBERT models rely on lexical and structural overlap, which is low (token Jaccard 0.1458). They fail to capture the high-level semantic similarity of URL-to-file download due to different API usage and control flow.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely labels this as a clone because both functions perform a download from a URL to a file, a common functional pattern, despite differences in authentication, zip extraction, and output handling.
- 共享行为: Both open a connection to a URL；Both read an input stream from the connection；Both write data to a file on the local filesystem
- 行为差异: A extracts a zip archive while B writes a single file；A uses a hardcoded URL; B takes a URL parameter；A outputs to current directory; B outputs to a temporary directory；B includes HTTP authentication and custom headers; A does not
- 修正建议: Improve dataflow and I/O operation representation；Use graph-based models capturing control and data dependencies；Include more training data with diverse implementations of similar tasks；Apply function renaming or abstraction to generalize patterns

### case_id=1547 FN benchmark_preference_bias

- 方法: `main` vs `copyFromTo`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Extracts all entries from a KMZ (ZIP) file downloaded from a fixed URL and saves each entry to the current directory.
- B 摘要: Copies a single source file to a destination file using NIO FileChannel, preserving the last modified timestamp.
- 静态失败原因: Static BERT correctly identified the low token overlap (0.165) and different operations, but the BCB label is a false positive, so the model 'failed' to match an erroneous annotation.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB likely labeled this as a clone due to overgeneralizing 'file copy' or 'file I/O' behavior, or an annotation error.
- 共享行为: Both perform file I/O operations.；Both read from a source and write to a destination.；Both use file streams and buffers.
- 行为差异: A downloads from a network URL and extracts multiple ZIP entries; B copies a single local file.；A writes each ZIP entry to a new file; B writes the entire source to one destination.；A does not handle file existence errors; B checks for FileNotFoundException and exits.；A does not set file timestamps; B sets the destination's last modified time to match source.
- 修正建议: Re-evaluate BCB annotation for this pair; consider removing or correcting the label.；Improve model robustness by incorporating functional semantics beyond token overlap.

### case_id=1548 FN partial_functionality

- 方法: `getFile` vs `testCodingEmptyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies its endpoint attribute, and saves it to a temporary directory.
- B 摘要: Tests the transfer method of LengthDelimitedEncoder by writing data to a ByteArrayOutputStream and transferring from an empty file.
- 静态失败原因: Low token overlap and distinct domain-specific code overshadow the common file handling boilerplate; static models may miss structural similarity in I/O operations.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider this a clone due to shared file I/O patterns (create file, open channel, transfer, close) which constitute partial functionality similarity, despite different overall purposes.
- 共享行为: Use of File and FileOutputStream to create and write to files；Use of FileChannel and transferFrom/transfer methods；Creation and cleanup of temporary files
- 行为差异: A involves network download and XML modification; B is a unit test for an encoder；A has multiple exception handlers; B throws Exception；A manipulates WSDL address; B performs assertions on encoding output
- 修正建议: Enhance model to recognize common I/O patterns via data-flow or program slicing；Use graph-based representations that capture channel and stream operations；Include heuristics for boilerplate code overlap in file handling

### case_id=1549 FN benchmark_preference_bias

- 方法: `testNetworkHTTP` vs `loadSourceCode`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.5`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Makes multiple HTTP GET requests to hardcoded URLs and discards the response.
- B 摘要: Reads a text file from classpath, applies syntax highlighting line by line, and builds an HTML string.
- 静态失败原因: The static BERT/GraphCodeBERT method likely predicted non-clone because of low token overlap (Jaccard=0.205), different method names, and clearly distinct overall functionality. The model may not have captured the broad similarity that BCB's lenient annotation expects, leading to a false negative.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have annotated this pair as a clone due to the shared use of URL, BufferedReader, and the pattern of reading lines in a loop, considering both as 'reading from a URL and processing input' despite different processing and purposes.
- 共享行为: Both use URL, BufferedReader, and InputStreamReader to read data from an input stream.；Both read lines in a while loop until null.；Both handle exceptions with try-catch blocks.
- 行为差异: Function A reads from multiple HTTP URLs, while B reads from a local classpath resource.；A discards the read data, while B processes each line with syntax highlighting and concatenates into a string.；A has side effects (network requests, logging), B modifies a field and has no network I/O.；A uses HttpURLConnection and explicitly disconnects, B uses getResource().openStream() and no explicit disconnect.
- 修正建议: Incorporate training examples of broad Type-3/Type-4 clones with low token overlap.；Use contrastive learning to push apart distinct functionalities while pulling together similar structural patterns.；Fine-tune with BCB's annotation guidelines to account for subjective preferences.

### case_id=1550 FP boilerplate_overlap

- 方法: `getmd5` vs `perform`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Computes MD5 hash of a password string and returns hex string.
- B 摘要: Struts action handler processes request, updates session beans, and forwards to result.
- 静态失败原因: Likely due to boilerplate overlap (try-catch, loops, string concatenation) misleading the model into thinking they are clones.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB expects functional similarity; these functions are semantically unrelated with no shared core behavior.
- 共享行为: both involve string manipulation；both have loops (for loop, while loop)
- 行为差异: different tasks: hashing vs web request handling；different inputs and outputs；different control flow and error handling
- 修正建议: Train model to focus on task-specific semantics rather than generic patterns；Use dataflow or control flow analysis to differentiate

### case_id=1551 FN boilerplate_overlap

- 方法: `doVersionCheck` vs `register`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Checks for software version updates by reading a URL and parsing build version strings.
- B 摘要: Registers a user by encoding password, creating hash, and calling an external forum URL to create a phpBB user, then persists the user and sends confirmation email.
- 静态失败原因: Static BERT models often rely on lexical overlap and local context, missing the abstract structural pattern of URL reading loops that spans multiple tokens; low Jaccard similarity (0.14) also contributed to the non-clone prediction.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may label these as clones due to high structural similarity: both perform a URL connection, read lines in a loop, and handle exceptions, which is a common pattern in Type-3/Type-4 clones where the skeleton is similar despite different semantics.
- 共享行为: Both open a URL and read lines using BufferedReader；Both use try-catch blocks to handle IOException；Both perform a network I/O operation with a loop that reads lines
- 行为差异: Different purpose: version check vs user registration；Different data parsed: build version strings vs forum ID from input；Different error handling: error dialog vs throwing RuntimeException or returning boolean；Register function has additional steps like password encoding, hash creation, persistence, email sending
- 修正建议: Add feature that captures structural patterns like 'URL open -> BufferedReader readLine loop'；Use AST-based features to identify common I/O patterns；Incorporate data flow or control flow graphs to recognize similar exception handling structures

### case_id=1552 FP lexical_or_api_overlap

- 方法: `handleHandshake` vs `postData`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Validates a handshake packet by checking username format and then either sends a login packet or performs an HTTP GET to session server to verify the session.
- B 摘要: Posts form data to a URL using HTTP POST, setting headers and reading the response without processing it.
- 静态失败原因: The model overemphasized lexical and structural similarities (e.g., URL, BufferedReader, InputStreamReader) and failed to capture the semantic difference in HTTP method and domain-specific logic, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB annotators consider high-level functionality and domain context. These functions have different goals (Minecraft handshake vs generic HTTP POST), so they are not clones despite some overlapping I/O boilerplate.
- 共享行为: Both open a URL connection and read a line from the input stream.；Both use BufferedReader and InputStreamReader.；Both involve network I/O with error handling (try-catch or throws).
- 行为差异: HTTP method: A uses GET via URL.openStream(), B uses POST via URLConnection with doOutput.；URL construction: A builds a fixed URL with user/session parameters; B takes protocol, host, form as arguments.；Response handling: A checks if response equals 'ok'; B ignores read data.；Purpose: A is specific to Minecraft session handshake; B is a generic data posting utility.
- 修正建议: Incorporate data flow analysis to distinguish GET vs POST.；Add domain-specific features (e.g., method name, constants).；Use more granular semantic role representations to differentiate core logic from boilerplate.

### case_id=1553 FN benchmark_preference_bias

- 方法: `fileDownload` vs `PhoneSetImpl`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `preference_memory_with_manual_audit`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a file from a URL and saves it as a PDF to a destination directory.
- B 摘要: Constructs a PhoneSetImpl by reading a URL, parsing each line, and populating a map, skipping lines starting with '***'.
- 静态失败原因: Static BERT models (e.g., GraphCodeBERT) likely focused on overall functionality differences (download vs. parsing) and missed the broad structural similarity that BCB accepts, leading to a false negative.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB considers broad functional similarity such as 'reading from URL and processing input', accepting Type-3/4 clones even when detailed logic differs, focusing on structural patterns like URL connection and line reading.
- 共享行为: Both open a URL connection and read input using BufferedReader；Both process input line by line (though A reads bytes, it effectively reads lines via read() and write())
- 行为差异: A writes raw bytes to a file, B parses lines and adds to a map；A treats all content as binary, B treats content as text；A saves as 'download.pdf', B skips lines starting with '***'；A uses int read() and write, B uses readLine() and parseAndAdd()
- 修正建议: Incorporate training data with more diverse partial-functionality clone pairs；Use data augmentation to emphasize structural patterns common across different tasks；Adjust threshold to accept lower similarity scores for broad Type-3/4 clones

### case_id=1554 FN benchmark_preference_bias

- 方法: `doGet` vs `copy`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Handles HTTP GET request to retrieve and render a portal page with caching and logging.
- B 摘要: Copies a file from source to destination character by character.
- 静态失败原因: Static model correctly predicted non-clone due to low lexical overlap and different API usage.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might have considered both as data transfer operations? But they are fundamentally different; likely an annotation error.
- 共享行为: Both involve reading and writing data；Both use file I/O (but A uses response wrapper, B uses FileReader/Writer)
- 行为差异: A processes HTTP requests and portal pages, B simply copies files；A has complex logic for page visibility, caching, logging, error handling；B is a straightforward file copy without any business logic；A uses servlet API, B uses standard Java I/O
- 修正建议: Review BCB annotation for this pair; it may be a mislabel.

### case_id=1555 FP boilerplate_overlap

- 方法: `main` vs `copyFiles`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Main method that reads a Prolog file, parses it, generates adapter classes and resources, and writes them to a JAR file.
- B 摘要: Recursively copies files or directories from source to destination using FileChannel for efficient I/O.
- 静态失败原因: The static BERT model may have been misled by overlapping boilerplate code such as 'File', 'throws Exception', 'catch', and 'FileChannel' usage, and the generally similar structure of a long method handling I/O, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BigCloneBench likely labels these as non-clones because they perform entirely different tasks despite both involving file manipulation. The core functionality and output are unrelated.
- 共享行为: Both involve file I/O operations.；Both use File objects and handle potential exceptions.；Both are public/private static methods.
- 行为差异: Function A is an entry point for a complex code generation tool; Function B is a utility for simple file copying.；Function A parses Prolog, generates multiple classes, and writes a JAR; Function B only copies files.；Function A has extensive logic for adapter generation and class loading; Function B has recursive directory traversal.；Function A writes structured outputs (JAR, resources); Function B writes exact copies of files.
- 修正建议: Include more negative examples with similar API usage but different semantics.；Use contrastive learning to emphasize functional differences.；Incorporate task-specific features like method name and context.

### case_id=1556 FN benchmark_preference_bias

- 方法: `ExternalDecoder` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.85`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Constructs an ExternalDecoder that copies an input stream to a process's stdin in a background thread.
- B 摘要: Launches a NexOpen project configuration by reading and modifying Maven pom files and setting up Hibernate properties.
- 静态失败原因: Static BERT likely correctly identified the low lexical similarity and different domains; BCB label appears to be a false positive, so model did not fail but accurately predicted non-clone.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled as clone due to both involving I/O operations and threading, but the overall functionality is completely different.
- 共享行为: Both use IOUtils for stream copying；Both create anonymous inner classes (Thread vs ContentHandlerCallback)；Both handle exceptions with try-catch blocks
- 行为差异: Function A only copies input stream to process stdin, while B involves complex project configuration；Function A uses a Thread, B uses callback handlers；Function B interacts with Eclipse workspace, Maven, and Hibernate; A has no such dependencies；Function A is a constructor; B is a method of a different class
- 修正建议: Review BCB annotation for this pair; likely noise in ground truth；Improve model to handle cases where BCB labels are inconsistent

### case_id=1557 FN partial_functionality

- 方法: `populateResources` vs `readGeoParserResult`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.4`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Loads default template files and images from resources and saves them to a database.
- B 摘要: Queries a geo-parsing web service to extract place names and gazetteer IDs from an input record.
- 静态失败原因: Static BERT models may have low token overlap and no identifier alignment, plus the high-level semantic similarity is not captured by lexical or structural features alone. The model likely focused on method names and API differences and saw them as unrelated.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB annotators may have considered both functions as 'resource loading' tasks due to the common pattern of opening streams, reading content, and handling errors, which is a high-level type-4 semantic similarity.
- 共享行为: Both use URL objects to access resources；Both read line-by-line using BufferedReader and StringBuffer；Both include error handling with try-catch blocks
- 行为差异: Purpose: initialization vs geo-parsing；Data source: local classpath vs remote web service；Output: void (saves to DB) vs collection of tuples；Processing: simple file reading vs XML parsing and retry logic
- 修正建议: Incorporate program dependency graphs or data flow analysis to capture common I/O patterns.；Use code summarization or task classification to learn high-level semantics.；Augment training data with more diverse pairs that share behavioral patterns despite different domains.

### case_id=1558 FP boilerplate_overlap

- 方法: `read` vs `executePost`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads camera log data from a URL, parses each line into CameraLogRecord objects, adds them to a list, sorts, and logs.
- B 摘要: Sends an HTTP POST request with parameters to a target URL, reads the response line by line, concatenates with carriage returns, and returns the response string or null on error.
- 静态失败原因: The static BERT/GraphCodeBERT model likely misclassified this pair as a clone (1) because it overemphasized the lexical and structural similarities in the boilerplate code: both functions open a URL, create a BufferedReader, read lines in a while loop, and handle exceptions. The model may have failed to capture the different data flow and domain-specific processing, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels these as non-clones (0) because the core functionality differs significantly: one is a data ingestion routine for camera logs, the other is an HTTP client for sending POST requests. While they share boilerplate I/O patterns, the high-level purpose and data processing are distinct, which BCB likely considers insufficient for a Type-3 clone.
- 共享行为: Open URL connection and obtain InputStream；Wrap InputStream with InputStreamReader and BufferedReader；Read input line by line in a while loop；Handle exceptions using try-catch-finally
- 行为差异: Function A reads from a URL (likely GET) while B performs a POST request with parameters；Function A parses each line into a specific object (CameraLogRecord) and adds to a list; B builds a string response；Function A sorts the records after reading; B does not sort；Function A ignores bad lines (catches LogParseException); B catches generic Exception and returns null
- 修正建议: Incorporate representations of method signatures and return types to distinguish void vs non-void；Add attention to the data transformation logic beyond I/O (e.g., parsing vs string building)；Use AST-based features that capture the specific API calls and their context (e.g., setRequestMethod('POST') vs no such call)；Train with more diverse negative examples that share boilerplate but differ in purpose

### case_id=1559 FP boilerplate_overlap

- 方法: `setMembers` vs `getVersion`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Parses HTML from a Trac ticket URL to populate static arrays for components and priorities.
- B 摘要: Retrieves and returns a version string from a remote URL, returning null on failure.
- 静态失败原因: The static BERT/GraphCodeBERT model likely overemphasized the common structural patterns (URL opening, BufferedReader, try-catch) and ignored the semantic differences in parsing logic, return types, and side effects. This leads to a false positive due to lexical/API overlap and boilerplate confusion.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels pairs as non-clones when the functions have distinct purposes and outputs, even if they share similar I/O boilerplate. Here, the methods perform entirely different tasks (parsing HTML vs. reading a version string), so BCB correctly marks them as non-clones.
- 共享行为: Both use URL, InputStreamReader, and BufferedReader to read from a remote resource.；Both employ try-catch blocks to handle network exceptions.；Both are private static methods with no parameters.
- 行为差异: setMembers returns void and has side effects (populating static arrays); getVersion returns a String and has no side effects.；setMembers parses HTML to extract options; getVersion reads a single line as the version.；setMembers uses Pattern/Matcher for regex parsing; getVersion simply reads the first line.；setMembers accesses a different URL (trac with 'newticket') compared to getVersion ('version' file).
- 修正建议: Incorporate data flow analysis to differentiate side effects and return values.；Use models that capture the semantic roles of library calls (e.g., HTML parsing vs. plain text reading).；Augment training data with more examples of non-clone pairs that share common I/O patterns but differ in purpose.

### case_id=1560 FP boilerplate_overlap

- 方法: `main` vs `main`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Main method that generates adapter classes from a Prolog file using a framework.
- B 摘要: Main method that copies a file from one location to another starting at a given byte offset.
- 静态失败原因: The model may have been misled by the common structural pattern of a main method (static, void, arguments, try-catch blocks, print statements) despite low token overlap. Static BERT/GraphCodeBERT models often rely on surface-level features and may over-generalize on boilerplate code, ignoring the distinct semantic cores.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled as non-clone because the functions have no meaningful functional similarity beyond being 'main' methods. The core tasks (adapter generation vs. file copy) are completely different, and the shared boilerplate (argument checking, exception handling) is insufficient for clone classification under BCB's relaxed Type-3/4 criteria.
- 共享行为: Both are entry points (main methods) that parse command-line arguments and perform I/O operations.
- 行为差异: Function A parses Prolog, generates adapters, and writes class files; Function B copies a file with a skip offset.；Function A involves complex framework interactions (Parser, FactVisitor, ClassWriter); Function B only uses basic Java I/O streams.；Function A handles multiple options like debug output; Function B has fixed positional arguments.
- 修正建议: Train models to distinguish core logic from boilerplate using techniques like dataflow analysis or AST-based contrastive learning.；Incorporate a mechanism to detect and downweight common entry-point patterns.；Use graph-based representations that capture long-range dependencies and different control flows.

### case_id=1561 FN partial_functionality

- 方法: `PageLoader` vs `File2String`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Constructor that reads all lines from a URL and stores concatenated result in an instance variable.
- B 摘要: Method that reads all lines from a file (or classpath resource) and returns concatenated result as a string.
- 静态失败原因: Low token overlap (0.16), different method signatures, and different variable names. Static BERT may rely heavily on lexical matches and cannot abstract the common pattern of reading lines.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB annotation guidelines often consider functions that perform 'read all lines from a source and concatenate' as clones even if source type and error handling differ, because the core semantic is similar.
- 共享行为: Both open an input stream；Read lines until end；Concatenate lines into a single string (or StringBuilder)；Close the stream
- 行为差异: PageLoader stores result in field inputLine; File2String returns the string；PageLoader only reads from URL; File2String tries file then resource；File2String has extensive error handling and prints; PageLoader throws Exception；PageLoader uses while (in.ready()) which may not read all data; File2String uses standard readLine loop
- 修正建议: Increase training with data that covers broad functional similarity despite lexical differences；Improve model's ability to recognize abstract patterns like reading all lines

### case_id=1562 FP boilerplate_overlap

- 方法: `readTwitterFead` vs `getUser`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a Twitter user timeline from a hardcoded URL and returns it as a string.
- B 摘要: Loads a user from a DAO or parses a config file to create a User object based on a login.
- 静态失败原因: Static BERT models may have overemphasized common Java boilerplate (BufferedReader, InputStreamReader, try-catch) and underestimated the distinct application logic, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the overall functionality is completely different: one retrieves a remote resource, the other looks up user data locally.
- 共享行为: Both use BufferedReader to read text from an input stream；Both have try-catch blocks for exceptions；Both return a result after processing input
- 行为差异: Function A performs an HTTP GET request; Function B reads from a local config file or DAO；Function A appends all lines to a StringBuilder; Function B tokenizes lines and creates a User object；Function A has no conditional parsing; Function B has token counting and comparison；Function A uses a hardcoded URL; Function B takes a parameter userlogin
- 修正建议: Enhance the model with data flow or call graph information to distinguish different API usages；Use more context-aware embeddings that capture higher-level semantics beyond token sequences；Incorporate task-specific features like URL strings or database operations

### case_id=1563 FN lexical_or_api_overlap

- 方法: `encodeFileToFile` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Encodes a file to another file using Base64 encoding.
- B 摘要: Launches a NexOpen project configuration by setting up Maven pom files, properties, and scheduling an install job.
- 静态失败原因: Static BERT/GraphCodeBERT models rely heavily on token overlap and local context. The token Jaccard similarity is very low (0.0667), and the functions have different method names, parameter types, and domain-specific APIs. The model failed to detect any semantic similarity because there is almost no lexical overlap and the functional similarity is superficial.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may have considered both functions as Type-4 semantic clones because they involve file I/O operations and use similar low-level stream patterns, despite vastly different overall purposes.
- 共享行为: Both functions use Java I/O streams for file reading/writing.；Both contain try-catch blocks for IOException handling.
- 行为差异: Function A is a simple file encoding utility; Function B is a complex Eclipse launch configuration handler.；Function A returns a boolean success flag; Function B returns void and throws CoreException.；Function A operates on file paths; Function B operates on Eclipse workspace resources and launch configuration objects.；Function A has a loop to copy data; Function B uses higher-level XML handling and project management APIs.
- 修正建议: Incorporate structural similarity features like control flow patterns or data flow graphs.；Use contrastive learning to better separate distinct clones from non-clones.；Augment training data with more examples of partial functional similarity.

### case_id=1564 FP dataflow_blindspot

- 方法: `write` vs `readData`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_with_trace`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Encrypts a series of ByteBuffers using an SSL/TLS engine, handling handshake state.
- B 摘要: Reads and parses comma-separated token strings to populate various sets and a hash map for Tibetan transliteration data.
- 静态失败原因: The model likely focused on surface-level patterns like nested loops or conditionals without understanding the overall semantic intent, leading to a false positive.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 dataflow_trace_and_outputs。
- BCB 偏好解释: BCB annotates as non-clone because the two functions have completely different purposes and no functional overlap, even under broad Type-3/4 similarity.
- 行为差异: A uses SSL engine for encryption; B parses tokenized strings with StringTokenizer.；A returns encrypted ByteBuffer array; B populates static sets and hash maps.；A handles SSL handshake states; B reads from a file and processes lines.；A deals with NIO buffers; B uses HashSet and HashMap for data storage.
- 修正建议: Incorporate control-flow and data-flow awareness to differentiate high-level behavior.；Use contrastive learning on hard negative pairs with low token overlap but similar structural patterns.；Add task-specific features such as API usage patterns or domain keywords.

### case_id=1565 FN partial_functionality

- 方法: `sendExceptionToServer` vs `seeURLConnection`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends exception details to a remote server via HTTP POST using URLConnection.
- B 摘要: Reads content from a URL using HTTP GET via URLConnection and logs it.
- 静态失败原因: Low token overlap (0.19) and different method names/control flow; static models rely on lexical similarity and miss the conceptual similarity of common URLConnection usage patterns.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as network communication functions that perform HTTP requests and read responses, thus semantically similar in a broad Type-4 sense.
- 共享行为: Both open a URLConnection and read the response using BufferedReader.
- 行为差异: sendExceptionToServer performs HTTP POST with encoded parameters, while seeURLConnection performs a simple GET.；sendExceptionToServer sends exception data and checks for a 'success' response, whereas seeURLConnection just logs the response content.；sendExceptionToServer handles multiple request parameters and exception handling, while seeURLConnection has minimal logic.
- 修正建议: Enhance model to recognize common API usage patterns (e.g., URL connection opening, reading response) even with varying surrounding logic.；Incorporate data flow or structural information to capture the sequence of network I/O operations.

### case_id=1566 FN partial_functionality

- 方法: `copy` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a local file to another local file using a buffered byte copy.
- B 摘要: Retrieves a resource via URL with caching, downloads and caches the file if needed, and returns an InputStream; includes byte copying loop similar to A.
- 静态失败原因: The token Jaccard is very low (0.1485) due to large differences in length and overall structure; the model likely missed the shared byte-copying subroutines.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider them Type-4 (semantic) clones because both contain the core behavior of copying bytes from an input to output stream, even though the contexts differ significantly.
- 共享行为: Both read bytes from an input stream and write to an output stream in a loop.
- 行为差异: A is a simple file copy; B handles URL resolution, HTTP connection, caching, and conditional returns.；A has no exception handling beyond finally; B has extensive try-catch and logging.；B is much larger and includes file caching logic and multiple return paths.
- 修正建议: Improve detection of partial clones by focusing on shared subroutines or common code patterns.；Use graph-based representations that can capture dataflow in local regions.；Train with more examples of type-4 clones with low syntactic overlap.

### case_id=1567 FP partial_functionality

- 方法: `setBundleInfoName` vs `downloadFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a configuration file from a URL and updates bundle names in a list based on key-value pairs.
- B 摘要: Downloads a file from a URL to a local file with progress reporting.
- 静态失败原因: Overemphasized structural similarity in URL and I/O operations, ignoring semantic divergence in output processing.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB considers functional equivalence at a high level; these functions have entirely different purposes despite sharing URL reading steps.
- 共享行为: Both open a URL connection and read data from it
- 行为差异: Different output: in-memory list update vs file download；Different processing: line parsing vs raw byte reading；Error handling: returns false vs throws exception；Additional progress reporting in function B
- 修正建议: Include dataflow analysis to track how read data is used (parsing vs file output)；Consider return types and subsequent program behavior

### case_id=1568 FN benchmark_preference_bias

- 方法: `testAddLinkToImage` vs `doGet`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Copies multiple image files from classpath resources to a report folder and adds hyperlinks to them in a report.
- B 摘要: Handles an HTTP GET request to retrieve a page by name or ID, checks user visibility, logs the request, and outputs the page content with caching.
- 静态失败原因: The static model correctly predicted non-clone (0). The failure is in the benchmark label, not the model prediction.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have erroneously labeled this as a clone due to surface-level I/O operations and similar method length, or due to a benchmark annotation mistake.
- 共享行为: Both perform file I/O operations (copying/writing files)；Both use String operations and handle exceptions
- 行为差异: Function A is a unit test for adding image links; Function B is a servlet processing user requests；Function A copies static resources; Function B dynamically retrieves and renders pages；Control flow: A is sequential copying; B has complex conditional logic for page lookup and caching
- 修正建议: Review BCB annotation for this pair; likely mislabeled；Remove or correct this pair in the benchmark if it is an outlier

### case_id=1569 FN partial_functionality

- 方法: `getURLContent` vs `httpRequestByPOST`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads the entire content of a URL using GET request and returns it as a string with newlines, throwing IOException on failure.
- B 摘要: Performs an HTTP POST request with parameters, reads the response body if successful, otherwise returns null with error details.
- 静态失败原因: The model likely focused on low token overlap and syntactic differences (different method names, import statements, control flow) and missed the high-level semantic similarity of reading an HTTP response into a string.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often treats functions that perform the same high-level I/O operation (e.g., fetch content from a URL over HTTP) as clones, ignoring differences in HTTP method, library, or error handling.
- 共享行为: Both make an HTTP request and read the response content line by line.；Both use BufferedReader and StringBuilder/StringBuffer to accumulate the response.；Both handle character encoding for reading the response.
- 行为差异: HTTP method: GET vs POST.；Libraries: java.net.URL/URLConnection vs Apache HttpClient.；Error handling: throws IOException vs catches exceptions and sets error fields.；Output format: includes newlines between lines vs concatenates lines without newlines.
- 修正建议: Train on more Type-3/4 examples where high-level purpose is similar despite syntactic differences.；Incorporate documentation or API usage context to infer intent.；Use graph-based representations that abstract over specific library calls.

### case_id=1570 FP lexical_or_api_overlap

- 方法: `actionPerformed` vs `CopyFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: GUI action listener that handles multiple command strings to configure application preferences and update UI components.
- B 摘要: Utility method that copies a file from source to destination using FileChannel.
- 静态失败原因: Despite low token overlap (Jaccard=0.0425), the model might have been misled by common Java keywords (e.g., 'File', 'Exception') or structural patterns (e.g., if-else chains), causing a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels as non-clone because functions have completely different semantics: one is a GUI configuration handler, the other is a file utility. No Type-1,2,3,4 similarity.
- 共享行为: Both involve file operations (A uses JFileChooser, B copies files).
- 行为差异: A is a large event handler with multiple conditional branches; B is a simple single-purpose function.；A interacts with GUI components and preference storage; B only performs file I/O.；A has complex control flow with many UI updates; B has straightforward sequential file copying.
- 修正建议: Improve model's ability to capture semantic roles (e.g., GUI vs I/O) beyond token matching.；Use dataflow or control flow analysis to differentiate high-level behavior.

### case_id=1571 FP lexical_or_api_overlap

- 方法: `readData` vs `copy`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Reads and parses multiple string tokens to populate various hash sets and a hash map, and also reads a file line by line to process wylie transliteration data.
- B 摘要: Copies the content of one file to another character by character.
- 静态失败原因: The static BERT model likely relied on lexical overlap of common API tokens (e.g., FileReader, IOException) and the presence of loops, ignoring the fundamental difference in intent and data manipulation.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would label this as non-clone (Type-0) because the two functions perform completely different high-level functionalities: data initialization and parsing vs file copying.
- 共享行为: Both involve file I/O operations (reading/writing characters).
- 行为差异: Function A parses data into multiple data structures (sets, maps), while Function B simply copies bytes.；Function A has complex conditional logic and error handling specific to transliteration, Function B has a straightforward loop.；Function A processes multiple string variables and tokenization, Function B only deals with file paths.
- 修正建议: Incorporate data-flow analysis to distinguish different high-level tasks.；Use control flow structure to separate simple copy loops from complex parsing loops.；Include semantic role labeling of method parameters and return types.

### case_id=1572 FN partial_functionality

- 方法: `truncate` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Compresses a file into a ZIP archive in a backup directory, then deletes the original file if it is older than the JVM start time.
- B 摘要: Retrieves a resource from a URL, caches it locally, and returns an InputStream, with conditional caching based on modification times.
- 静态失败原因: The static model relied on low token Jaccard similarity (0.153) and different method names/APIs, missing the underlying structural dataflow pattern of resource caching. It failed to recognize that both functions share a general 'cache or backup' semantics despite different implementations.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider these clones because both functions exhibit a common pattern of resource caching: they read from an input source (file or URL), optionally condition on timestamps, write to an output file, and handle cleanup. This abstract behavior is categorized as Type-4 similarity in BigCloneBench.
- 共享行为: Both perform file I/O using streams (FileInputStream, FileOutputStream/ZipOutputStream/BufferedStreams)；Both check file existence and create directories if needed；Both have try-catch-finally blocks for resource cleanup and error handling；Both involve conditional logic based on file age or modification time
- 行为差异: A compresses a local file into a zip archive; B downloads a remote resource and caches it to a local file；A uses ZipOutputStream with DEFLATED mode; B uses URLConnection and BufferedOutputStream for caching；A deletes the original file after compression; B does not delete the source (remote resource remains)；A returns void; B returns an InputStream
- 修正建议: Incorporate dataflow analysis to detect abstract patterns like resource caching；Train on more diverse pairs with low lexical but high functional similarity；Use program slicing to focus on core I/O operations

### case_id=1573 FP lexical_or_api_overlap

- 方法: `readZoneIDs` vs `getFullScreenUrl`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads integers from a resource file and returns them as a HashSet.
- B 摘要: Fetches a YouTube video URL by parsing HTML for fullscreenUrl and extracting parameters.
- 静态失败原因: Static BERT likely overemphasized the high lexical overlap of API calls (URL, BufferedReader, InputStreamReader, readLine, catch) and ignored the distinct overall functionality and data types.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clone because the functions clearly serve different purposes and are not semantically similar; they only share generic I/O patterns.
- 共享行为: Both use URL/URLConnection to read from a stream；Both use BufferedReader/InputStreamReader to read line by line；Both catch exceptions generically
- 行为差异: readZoneIDs reads from a class resource; getFullScreenUrl reads from a web URL；readZoneIDs parses integers; getFullScreenUrl parses HTML and query parameters；readZoneIDs returns a set of integers; getFullScreenUrl returns a constructed URL string；getFullScreenUrl has additional UI updates (progress bar) and prints debugging info
- 修正建议: Incorporate data flow or type information to distinguish different transformations；Use function names and return types as global features；Train with contrastive examples that have overlapping API but different semantics

### case_id=1574 FP lexical_or_api_overlap

- 方法: `main` vs `getFileContentAsString`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Main method that generates adapter classes from a Prolog file by parsing, visiting, and writing classes to a JAR.
- B 摘要: Utility method that reads the content of a file from classpath or filesystem into a string.
- 静态失败原因: Static models may have been misled by lexical and API overlap (e.g., IOException, File, InputStream, try-catch patterns) despite low Jaccard similarity, and they may lack understanding of overall program purpose and context.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels these as non-clones because they perform entirely different tasks; the only superficial similarity is file reading, which is too generic and minor to constitute a clone.
- 共享行为: Both involve reading a file (A reads a Prolog file using FileUtils, B reads a file from classpath or filesystem).
- 行为差异: A is a main method with command-line argument parsing, B is a protected method with parameters.；A generates JAR files and adapter classes, B returns a string.；A uses a Prolog parser and multiple visitors/generators, B uses IOUtils.copy.；A has extensive control flow with multiple steps, B is a simple utility.
- 修正建议: Incorporate method name and signature information to distinguish main vs utility methods.；Use dataflow analysis to capture that file reading in A is a small part of a larger workflow.；Enhance training with more examples of diverse tasks that share low-level API calls but differ semantically.；Consider function length and complexity as features.

### case_id=1575 FN benchmark_preference_bias

- 方法: `copyFile` vs `modifyApplicationMessage`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Copies a file from source to destination using FileChannel.
- B 摘要: Modifies a key-value pair in a locale-specific properties file, copying the English file if needed.
- 静态失败原因: The model correctly predicted non-clone based on low token overlap and semantic dissimilarity; the BCB label is likely erroneous.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have incorrectly labeled due to superficial file-operation similarity or annotation mistake; the functions share no meaningful behavioral overlap.
- 共享行为: Both perform file I/O operations.；Both handle exceptions (one throws, one catches).
- 行为差异: A is a straightforward file copy, B is a complex properties manipulation with locale handling.；A copies entire file content; B reads, modifies, and writes a properties file line by line.；B includes conditional file creation and fallback, A does not.；Different input/output: A takes two File objects, B takes strings and uses resource loading.
- 修正建议: Review BCB annotation for this pair; likely a false positive in the benchmark.；Add more discriminative features to models, but in this case the model is correct.

### case_id=1576 FP partial_functionality

- 方法: `executePost` vs `postData`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Executes an HTTP POST request to a given URL with parameters, returns the response body as a string, and handles exceptions internally.
- B 摘要: Sends data via HTTP POST to a URL constructed from parts, discards the response, and throws exceptions to the caller.
- 静态失败原因: The model likely over-relied on lexical and API-level similarities (e.g., both use URLConnection, setDoOutput, setDoInput, etc.) and missed the fundamental difference in response handling and return type. The token Jaccard of 0.33 and similar code structure may have triggered a false positive.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB typically labels non-clones when functions have significant semantic differences like different return types and exception handling, even if they share similar POST logic. The void return and ignored response in B contrast with the returned response in A, making them different tasks.
- 共享行为: Both send data over HTTP POST using similar headers (Content-Type, Content-Length) and set doOutput/doInput.；Both create a URL and open a connection.；Both write data to the output stream and read from the input stream.
- 行为差异: A returns the response string; B discards it (void).；A uses HttpURLConnection with explicit POST method; B uses generic URLConnection (implicit POST via doOutput).；A computes content length using byte array length; B uses string length.；A handles exceptions internally (prints and returns null); B throws Exception to the caller.
- 修正建议: Incorporate dataflow analysis to track the usage of the response object.；Add attention to return type and exception handling patterns.；Use AST-based differencing to highlight structural differences in response processing and error handling.

### case_id=1577 FP lexical_or_api_overlap

- 方法: `split` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `1.0`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Splits a FASTA file into smaller partitions based on size limits.
- B 摘要: Handles GUI actions to set file paths for external tools and save application preferences.
- 静态失败原因: Static BERT/GraphCodeBERT likely over-relied on surface tokens like 'File', 'Exception', 'if', 'byte', etc., which appear in both functions, ignoring the high-level semantic context and domain difference.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clones when functions have completely different purposes, even if they share some low-level API usage. The functions here are from entirely different domains (bioinformatics vs. GUI configuration).
- 共享行为: Both use file I/O operations (File, FileInputStream, etc.)；Both have conditional branching and loops
- 行为差异: Function A processes biological sequence files; Function B manages GUI preferences.；Function A uses file channels and buffers for performance; Function B uses JFileChooser and property storage.；Function A returns a count of files created; Function B returns void and updates UI components.
- 修正建议: Improve model's ability to capture high-level purpose via better attention to method names and overall structure.；Enhance training data with more diverse non-clone pairs that share low-level tokens but differ in intent.；Use program dependency graphs or data flow analysis to distinguish file processing from GUI event handling.

### case_id=1578 FP lexical_or_api_overlap

- 方法: `init` vs `getVersion`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Loads controller classes from a registry file by reading class names from resources and adding them via addClass.
- B 摘要: Fetches a version string from a remote URL by reading a single line from the HTTP response.
- 静态失败原因: Static BERT likely focused on lexical overlap (common tokens like BufferedReader, URL, openStream, readLine) and structural similarity of the while loop, missing the semantic context that the methods serve completely different purposes.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would not consider these clones because they perform fundamentally different tasks (initialization vs version retrieval) despite sharing a common I/O pattern; the high-level functionality is entirely different, so they are non-clones even under lenient Type-4 criteria.
- 共享行为: Both use BufferedReader to read lines from an input stream obtained from a URL or URL-like resource
- 行为差异: Source of input: local classpath resource vs remote HTTP URL；Purpose: loading multiple classes for initialization vs retrieving a version string；Error handling: catching IOException and ClassNotFoundException vs catching generic Exception；Loop structure: reading multiple lines until null vs reading a single line
- 修正建议: Include method names and surrounding class context in the representation；Use data-flow-aware models that track how variables are used (e.g., versions vs. class loading)；Encode the overall goal of the method using additional features like comments or invocations

### case_id=1579 FP lexical_or_api_overlap

- 方法: `readTwitterFead` vs `fetchUrl`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Downloads a hardcoded Twitter timeline JSON using HttpClient, returns string or empty on failure with logging.
- B 摘要: Fetches any URL using URL.openStream() and returns its content as string, returns empty on exception.
- 静态失败原因: High lexical overlap in common patterns (BufferedReader, StringBuilder, readLine, try-catch) caused the model to overestimate similarity, ignoring crucial semantic differences.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely considered the different HTTP libraries and the hardcoded URL as significant behavioral differences, making them non-clones despite similar core purpose.
- 共享行为: Both read text from a URL line by line into a StringBuilder；Both return the built string or empty on failure
- 行为差异: A uses Apache HttpClient, B uses java.net.URL.openStream()；A checks HTTP status code 200, B relies on exceptions for errors；A has hardcoded URL, B takes URL as parameter；A logs errors, B catches and returns empty silently
- 修正建议: Incorporate dataflow analysis to distinguish library calls；Train with contrastive examples of different HTTP client usage；Consider method inputs and outputs explicitly

### case_id=1580 FN lexical_or_api_overlap

- 方法: `simulate` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Simulates a test scenario by reading simulation data from a file, making remote SOAP calls to rate users and obtain reputations, and writing results to an output file.
- B 摘要: Retrieves a resource from a URL with caching, reading from HTTP connection and writing to local file system, then returns a FileInputStream.
- 静态失败原因: The static BERT model correctly predicted non-clone due to low token overlap (0.109) and distinct method names. If BCB considered it a clone, the model failed to recognize broad I/O patterns that BCB overvalued.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may have considered the common I/O and exception handling patterns as sufficient for Type-3/4 similarity, but the core functionality diverges significantly, so likely a false positive in BCB.
- 共享行为: File I/O operations using Buffered streams；Exception handling with try-catch；Printing status messages to console；Looping over input data
- 行为差异: Core purpose: simulation test vs. resource caching；Type of remote calls: SOAP vs HTTP；Data processing: parsing CSV lines vs. byte stream copying；Output: writing formatted results vs. caching file
- 修正建议: Improve representation to capture higher-level semantic similarity beyond token overlap；Consider graph-based representations to model control flow and data flow patterns；Use contrastive learning to distinguish boilerplate-only similarity from true clone

### case_id=1581 FP boilerplate_overlap

- 方法: `setBundleInfoName` vs `getTicketsForQueue`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.98`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a URL, parses key-value lines, and sets bundle names in a list.
- B 摘要: Queries a REST API for open tickets in a queue, extracts ticket IDs, and retrieves each ticket.
- 静态失败原因: Static BERT models like GraphCodeBERT may over-rely on superficial token matches (e.g., 'BufferedReader', 'readLine', 'try', 'catch', 'IOException') and common structural patterns (loops, conditionals), ignoring the distinct high-level semantics (one updates bundle info, the other retrieves tickets). The model may have been biased by the presence of similar boilerplate code for network I/O.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would likely label this as non-clone because the two functions have completely different purposes and output types, even though they share some low-level I/O patterns. BCB annotations emphasize semantic similarity over lexical or structural overlap.
- 共享行为: Both use BufferedReader to read lines from an input stream.；Both have try-catch blocks for exception handling.；Both use loops to process lines.
- 行为差异: Function A updates bundle names; function B retrieves and collects ticket objects.；Function A parses 'key=value' lines; function B parses lines starting with 'ticket/'.；Function A returns a boolean; function B returns a list of RTTicket or null.；Function A does not make HTTP requests itself (reads from a URL stream); function B makes an HTTP GET request and handles response codes.
- 修正建议: Train the model with more negative examples that have shared boilerplate but different semantics.；Incorporate data-flow or type information to distinguish the purpose (e.g., one returns boolean vs list of tickets).；Use contrastive learning to push apart functions with different high-level intents despite similar low-level code.

### case_id=1582 FN benchmark_preference_bias

- 方法: `login` vs `invoke`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.6`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Log in to a specific system (LOLA) by sending an HTTP POST with URL-encoded email and password, then extract and return the session ID.
- B 摘要: Invoke a remote method via HTTP POST with JSON serialization, handle connection timeouts with retry logic, and return the deserialized response.
- 静态失败原因: Static BERT/GraphCodeBERT typically relies on token overlap and local structural patterns; the low Jaccard similarity (0.10) and distinct libraries (URLConnection vs HttpClient) led it to correctly predict non-clone, but it fails to capture the broader functional similarity that BCB recognizes.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might annotate these as clones due to the high-level similarity of 'client-side HTTP request/response handling' despite completely different business logic and data formats, which is a weak functional correspondence.
- 共享行为: Both send HTTP POST requests to a URL；Both read the HTTP response line by line using BufferedReader
- 行为差异: Different intent: authentication vs remote method invocation；Different data format: URL-encoded form data vs JSON；Different error handling: simple exception logging vs retry on ConnectTimeoutException；Different return types: String session ID vs generic Object deserialized from JSON
- 修正建议: Incorporate high-level API call patterns (e.g., HTTP client usage) as features；Use data flow analysis to abstract the 'send request, receive response' pattern；Include task-level semantics via documentation or method names

### case_id=1583 FN lexical_or_api_overlap

- 方法: `getFile` vs `encodeFileToFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies a specific XML attribute, and saves it locally, returning the file path.
- B 摘要: Encodes a file using Base64 and writes the encoded content to another file, returning success status.
- 静态失败原因: Static BERT models rely heavily on lexical matching; here, the token overlap is low (14.5%), and the APIs used (URL, XML vs Base64) are dissimilar, causing the model to miss the underlying structural similarity.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely annotated these as clones due to the similar structural pattern of opening input/output streams, performing a transformation, and closing resources, considering them Type-3 clones with differing method names and specific operations.
- 共享行为: Both perform file I/O operations: reading from an input source and writing to an output file.；Both use try-catch exception handling and cleanup (close streams) in finally block.
- 行为差异: A involves network download and XML parsing/modification; B is a local file encoding.；A returns a file path (String); B returns a boolean success flag.；A handles multiple exception types (MalformedURLException, IOException, ParserConfigurationException, SAXException); B only catches IOException.；A uses NIO channels and conditional logic to check file existence; B uses simple byte buffer loop with Base64 encoding.
- 修正建议: Use code structure-aware models (e.g., AST-based or CFG-based) to capture abstract patterns.；Incorporate data flow information to detect the common read-process-write pattern.；Normalize API names to high-level operations (e.g., 'read', 'write', 'encode') to reduce lexical mismatch.

### case_id=1584 FP partial_functionality

- 方法: `readTwitterFead` vs `postData`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads Twitter timeline JSON via HTTP GET and returns the content as a string.
- B 摘要: Sends data via HTTP POST to a configurable endpoint and ignores the response.
- 静态失败原因: The model may have focused on the common pattern of opening connections and reading lines, missing the critical difference in HTTP method (GET vs POST) and the fact that one sends data and discards the response while the other retrieves data and returns it.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely labeled non-clone because the functions have fundamentally different purposes (read vs write), different APIs, different signatures (return type, parameters), and low token overlap, despite both involving network communication.
- 共享行为: Both perform HTTP network I/O using streams；Both involve reading from an input stream using BufferedReader；Both handle exceptions
- 行为差异: Function A uses HttpClient (Apache) for GET, B uses URLConnection for POST；A returns data, B returns void；A has hardcoded URL, B has configurable parameters；A explicitly checks HTTP status code (200), B does not
- 修正建议: Train model to distinguish between read and write operations in network I/O；Incorporate method signature features (return type, parameters) explicitly；Use data flow analysis to track whether output is from network or to network

### case_id=1585 FP lexical_or_api_overlap

- 方法: `getDatasetsList` vs `downloadFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Caches and retrieves a list of dataset names from a server URL by reading lines from an HTTP response.
- B 摘要: Downloads a file from a URL to a local destination with progress reporting, using buffered streams and file I/O.
- 静态失败原因: The model likely over-emphasized shared lexical tokens like 'URL', 'BufferedReader', 'InputStream', 'IOException', and the try-catch pattern, while missing the semantic difference in output and side effects. The similarity in API usage led to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels non-clones when functions have entirely different functionality, even if they share some API usage patterns. Here the tasks (retrieving a list vs. downloading a file) are fundamentally different, so BCB correctly marked them as non-clone.
- 共享行为: Both open network connections to URLs and read data from input streams.；Both use try-catch-finally for IOException handling.
- 行为差异: Function A returns a List<String> after reading lines from the stream, while Function B writes bytes to a file and returns a boolean.；Function A caches results in a HashMap, while Function B does not cache.；Function B includes progress reporting via MessageFrame, which Function A lacks.；Function A is synchronized, Function B is static.
- 修正建议: Enhance training data with negative pairs that share API patterns but have different semantics.；Incorporate data-flow or control-flow analysis to distinguish between reading data for processing vs. writing to file.；Use models that can better capture functional intent, such as those integrating abstract syntax trees or program dependence graphs.

### case_id=1586 FP lexical_or_api_overlap

- 方法: `doVersionCheck` vs `readZoneIDs`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Checks for a newer version of jEdit by reading a version file from a URL.
- B 摘要: Reads zone IDs from a resource file into a set of integers.
- 静态失败原因: The model likely over-emphasized the lexical and API overlap (URL, BufferedReader, while loop reading lines) and the common try-catch pattern, ignoring the differing core semantics and return types.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would label these as non-clones because they perform distinct functionality (version checking vs. ID parsing) with different return types and side effects, despite sharing some I/O boilerplate.
- 共享行为: Both open a URL/input stream；Both read lines from the stream；Both use try-catch for exception handling
- 行为差异: A shows wait cursor and hides it; B does not；A parses version and build strings; B parses integers；A compares versions and shows messages; B returns a set of integers；A returns void; B returns HashSet<Integer>
- 修正建议: Enhance model to focus on functional behavior beyond API usage；Incorporate dataflow analysis to distinguish how data is processed；Use contrastive learning on pairs with similar API but different intent

### case_id=1587 FN partial_functionality

- 方法: `main` vs `readAndRewrite`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a URL and extracts its zip entries to the current directory.
- B 摘要: Reads a DICOM file, parses it, and rewrites it to another file.
- 静态失败原因: Static BERT models rely on token-level similarity; the low Jaccard similarity (0.118) and different API calls led to a non-clone prediction. The functional similarity is not captured by surface forms.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider these clones as Type-4 (functionally similar) because both follow a high-level pattern of reading, processing, and writing data, even though the specific formats and algorithms differ.
- 共享行为: Both perform file I/O operations using streams；Both read input data, process it, and write output to files
- 行为差异: Function A handles ZIP extraction of KMZ files; Function B handles DICOM parsing and rewriting；Different input sources: URL vs local file；Different output: raw entry files vs rewritten DICOM file；Different libraries and domain-specific processing
- 修正建议: Use graph-based representations that capture high-level data flow and control structure；Incorporate semantic role labeling to identify abstract I/O operations；Leverage program summarization techniques to compare functional intent

### case_id=1588 FN benchmark_preference_bias

- 方法: `copyFile` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Copies a file to another file using FileChannel, returns boolean success.
- B 摘要: Retrieves a resource via URL, caches it locally, and returns an InputStream, with extensive error handling.
- 静态失败原因: Static model likely correctly predicted non-clone due to low lexical overlap (Jaccard=0.096) and different semantics; BCB label may be erroneous or based on overly broad criteria.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB label may be due to both functions using FileInputStream/FileOutputStream, but overall functionality is not similar; possibly a mislabel in the benchmark.
- 共享行为: Both involve file I/O using streams；Both may write to file (copyFile writes output, getResourceAsStream writes cache)
- 行为差异: A is a simple file copy; B involves URL connection, caching, and conditional retrieval；Different return types: boolean vs InputStream；B has complex exception handling with multiple close attempts
- 修正建议: Verify BCB label; if correct, re-evaluate clone definition for this pair；Improve model to handle cases where low lexical overlap aligns with non-clone

### case_id=1589 FN benchmark_preference_bias

- 方法: `compressWithZip` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Compresses a list of files into a zip archive.
- B 摘要: Retrieves a resource via URL, caches it locally, and returns an InputStream.
- 静态失败原因: Static models rely on surface form and structure; these functions are too different in their API usage and control flow, so the model correctly predicted non-clone.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have considered both as 'reading and writing data operations', but this is overly broad and likely a misannotation.
- 共享行为: Both involve reading from an InputStream and writing to an OutputStream
- 行为差异: Function A creates a zip archive from local files; Function B downloads from a URL and caches；Function A has no caching or network logic; Function B handles HTTP connections and caching；Function A writes to a ZipOutputStream; Function B writes to a FileOutputStream for caching and returns an InputStream
- 修正建议: Re-evaluate BCB annotations for this pair；Train on more diverse negative examples to avoid over-generalizing；Incorporate semantic understanding of high-level purpose

### case_id=1590 FN partial_functionality

- 方法: `main` vs `readGeoParserResult`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Main method that builds a RenRen API feed publish request with hardcoded parameters, sends it as HTTP POST, and prints the response.
- B 摘要: Method that reads geographical parser results by constructing an XML request, sending it to a GeoParser service, parsing the response XML, and returning a collection of place names and gazetteer IDs.
- 静态失败原因: Static BERT models rely heavily on lexical and syntactic overlap, which is very low (token Jaccard 0.103). The functions share only boilerplate IO code and differ in domain-specific logic, libraries, and control flow, making them appear dissimilar to a static model.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label these as clones because both functions follow a common pattern of preparing an HTTP request, sending it, and processing the response. Despite different domains and specific implementations, the high-level structure is similar enough to be considered a Type-3 or Type-4 clone.
- 共享行为: Both functions construct a URL and open an HTTP connection；Both read response line by line using BufferedReader；Both handle IOException；Both output or process the response content
- 行为差异: Function A uses PostParameter and RenRenPostParameters for request building; function B uses XML document building；Function A sends a POST request with output; function B sends a GET request with query parameters；Function A prints the response directly; function B parses the response as XML and extracts structured data；Function B includes retry logic and error handling; function A has none
- 修正建议: Incorporate high-level API usage patterns as features；Use models that capture semantic similarity via code summarization or documentation；Fine-tune on a dataset that includes broad Type-4 clones with low lexical overlap

### case_id=1591 FN partial_functionality

- 方法: `sendExceptionToServer` vs `read`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Encodes exception details into a URL-encoded string and sends it to a server via HTTP POST, then prints the response.
- B 摘要: Opens a stream from a URL or file path, reads data via another method, and returns a status code.
- 静态失败原因: Static embedding methods may over-rely on lexical overlap (URL, IOException, BufferedStream) and miss the semantic difference in purpose (send vs read), leading to a false negative.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider them clones due to similar structural patterns (URL creation, try-catch, stream handling) and both being I/O related, fitting a broad Type-3 or Type-4 partial similarity.
- 共享行为: Both use URL class to connect to a resource；Both handle IOException with try-catch；Both involve I/O operations with streams
- 行为差异: Function A sends data (POST request) while Function B reads data (GET-like)；Function A builds a complex payload; Function B simply opens a stream；Different parameter signatures and return types
- 修正建议: Incorporate data flow analysis to distinguish send vs read operations；Use task-specific fine-tuning on clone detection with more emphasis on higher-level semantics

### case_id=1592 FN lexical_or_api_overlap

- 方法: `getFile` vs `test`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.2`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Downloads a WSDL file from a URL, modifies the endpoint address in the XML, and saves it locally.
- B 摘要: Reads an XML resource file, sets up a traffic simulation engine, and runs a simulation stepping over time, printing vehicle states.
- 静态失败原因: Static BERT likely predicted non-clone because of extremely low token overlap (0.06) and no structural similarity in control flow or API usage, leading to a correct non-clone prediction under strict semantics.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely labeled as clone due to superficial similarities like XML parsing and file I/O, but the actual functionality is completely different.
- 共享行为: Both involve reading input data (network stream vs resource file) and performing some iteration over data
- 行为差异: Different input sources: remote URL vs classpath resource；Different processing: XML manipulation for WSDL vs traffic simulation；Different output: file save vs console output；Different error handling: exception throwing vs test assertion (none)
- 修正建议: Use more fine-grained semantic analysis that can recognize broad functionality similarities even when token overlap is low；Incorporate character-level or subword-level embeddings to capture partial functionality

### case_id=1593 FN benchmark_preference_bias

- 方法: `doGet` vs `copyResourceToFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Handles HTTP GET request, retrieves a page, checks visibility and editing permissions, logs requests, and writes response with optional caching.
- B 摘要: Copies a resource file from the classpath to a destination file using I/O streams.
- 静态失败原因: The static model correctly predicted non-clone; BCB label is likely erroneous, so the model did not fail.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have mislabeled due to both containing I/O and error handling patterns, or because of an annotation error in the benchmark.
- 共享行为: Both perform file I/O operations；Both handle exceptions with try-catch-finally
- 行为差异: doGet processes HTTP requests and page retrieval; copyResourceToFile copies a file；doGet involves user permissions, logging, and caching; copyResourceToFile is a simple file copy；doGet is a servlet method with request/response; copyResourceToFile is a private utility method
- 修正建议: Verify BCB annotation for this pair; consider removing from clone set；Use more precise semantic analysis to avoid false positive BCB labels

### case_id=1594 FN benchmark_preference_bias

- 方法: `getWebPage` vs `register`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Fetches the entire content of a web page as a string.
- B 摘要: Registers a user by encoding password, setting date, assigning authority, creating hash, calling phpBB forum via URL, persisting user, and sending confirmation email, returning success flag.
- 静态失败原因: Static BERT/GraphCodeBERT likely correctly identified the low token overlap (0.159) and divergent control flow, missing the partial subfunction similarity due to strict semantic focus; it failed to recognize the clone according to BCB's broader definition.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have considered the shared pattern of reading from a URL as partial functionality similarity, accepting broad Type-3/Type-4 clones, but given the overall semantic difference, this likely represents an annotation error or overly broad interpretation.
- 共享行为: Both open a URL connection and read lines from the input stream.；Both handle IOException.
- 行为差异: A returns page content as string; B returns boolean success.；A does not modify any state; B modifies User object, database, and sends email.；B includes many additional steps (password encoding, hash, database persist, email) not present in A.
- 修正建议: For strict detection, no change needed; model correctly predicted non-clone.；To align with BCB, incorporate partial functional similarity detection by learning subgraph or API sequence matching.；Consider re-annotating BCB for such cases to reduce noise.

### case_id=1595 FN partial_functionality

- 方法: `getHTML` vs `init`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads HTML from a URL and optionally writes it to a file.
- B 摘要: Loads controller class names from a registry file and registers them.
- 静态失败原因: Static BERT likely underestimated similarity due to low token overlap and different method names, while missing the shared abstract pattern of reading from a URL and line-by-line processing.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider these clones because both follow a common pattern of reading lines from a URL resource and processing them, ignoring the specific business logic. The structural similarity (open URL, read lines, handle exceptions) qualifies as Type-3/Type-4 under broad BCB criteria.
- 共享行为: Both open a URL connection and read data using BufferedReader；Both loop through lines and process them；Both handle exceptions with printStackTrace
- 行为差异: getHTML builds a string of HTML content; init loads classes from class names；getHTML may write to a file; init adds classes to a registry；getHTML returns the HTML string; init has no return value；getHTML uses HttpURLConnection; init uses ClassLoader.getResources
- 修正建议: Incorporate higher-level pattern recognition beyond lexical tokens；Use structure-based features like control flow or data flow graphs；Consider functional purpose summarization

### case_id=1596 FP lexical_or_api_overlap

- 方法: `copyFile` vs `main`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Copies a file using FileChannel.
- B 摘要: Main method of an adapter generator that reads a Prolog file, parses it, generates adapters, and writes output.
- 静态失败原因: The static model may have been misled by common keywords like 'File', 'IOException', and 'catch', or by similar structural patterns like try-finally, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled non-clone because the functions perform completely different tasks despite both involving files.
- 共享行为: Both involve file handling；Both handle IOException
- 行为差异: copyFile is a simple file copy; main is a complex workflow；main has command-line argument parsing, Prolog parsing, class generation；main outputs a Jar file; copyFile writes to a given output file
- 修正建议: Improve model's ability to capture high-level semantics beyond token overlap；Incorporate control flow and data flow features；Use larger context or program dependency graphs

### case_id=1597 FN partial_functionality

- 方法: `getResourceAsStream` vs `createNew`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a remote resource via HTTP, caches it locally, and returns a FileInputStream for the cached file.
- B 摘要: Creates a new file in a directory from an input stream, with ownership checks, and returns a Resource object.
- 静态失败原因: Low token overlap (0.12) and different method names suggest the model relied on surface features, missing the deeper structural similarity of stream-to-file writing.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider them clones due to the common pattern of reading an input stream and writing to a file, and both functions handle file creation and stream management, despite the differing high-level purposes.
- 共享行为: Both involve reading from an input stream and writing to a file using FileOutputStream.；Both perform file I/O and handle exceptions.
- 行为差异: A downloads from a network URL and implements caching; B writes locally to a predetermined directory.；A returns an InputStream; B returns a Resource object.；A has complex conditional logic for cache validation and HTTP response handling; B has an ownership check and no caching.；A uses a hashtable to cache remote name-to-local file mappings; B does not use caching.
- 修正建议: Improve model training with more examples of partial functionality clones.；Enhance representation to capture common I/O patterns across different contexts.；Use AST or data flow features to identify stream copying patterns.

### case_id=1598 FN partial_functionality

- 方法: `sendRequestObjectResponse` vs `register`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends an HTTP POST request with XML to a servlet, receives a response, saves it to a file based on content type, and returns the file path.
- B 摘要: Registers a user by encoding password, setting date, adding default authority, making an HTTP GET request to a phpBB forum, persisting user, and sending confirmation email.
- 静态失败原因: A static BERT/GraphCodeBERT model likely failed due to very low token overlap (Jaccard=0.107), different method names, library calls, and control flows. The model could not detect the high-level HTTP communication pattern and thus predicted non-clone.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled these as clones because both functions involve making an HTTP request and processing the response, which is a broad semantic pattern. However, the specific operations and contexts differ significantly, making this a borderline Type-4 clone.
- 共享行为: Both establish an HTTP connection using URL.openConnection and handle input/output streams.；Both use try-catch blocks for exception handling.；Both perform null or type checks (e.g., null check for serverURL, null and instance check for o).
- 行为差异: Function A sends a POST request with XML body; Function B sends a GET request with parameters in the URL.；Function A writes to output stream and reads response to save a file; Function B only reads response to set a forum ID.；Function A is a generic utility returning a filename; Function B is a specific registration workflow involving user object manipulation and database persistence.；Function A interacts with GUI (dialog, browser); Function B uses logging and throws runtime exceptions.
- 修正建议: Enhance model's ability to recognize high-level semantic patterns like network communication across diverse implementations.；Incorporate data flow analysis to identify shared I/O operations.；Use contrastive learning with more examples of Type-4 semantic clones.

### case_id=1599 FP long_range_semantics

- 方法: `readData` vs `copyFileTo`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `static_summary_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Reads comma-separated strings from static variables and populates multiple sets and a hash map.
- B 摘要: Copies the current file to a destination using NIO file channels.
- 静态失败原因: The static model likely struggled with the long and complex structure of readData, possibly focusing on superficial patterns like try-catch blocks or variable declarations that are also present in copyFileTo, leading to a false positive.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB label 0 because the two functions have completely different purposes and implementations, with no shared functionality even at a high level.
- 行为差异: Function A parses configuration strings into collections; Function B performs file I/O copy.；Function A has complex conditional logic and multiple collection initializations; Function B is a straightforward channel transfer.；Function A does not return anything; Function B does not return anything but writes to a file.；Function A uses StringTokenizer extensively; Function B uses FileInputStream, FileOutputStream, and FileChannel.
- 修正建议: Use data flow analysis to trace actual dependencies and distinguish between parsing and file I/O.；Train models to handle long-range dependencies by using hierarchical attention or summarization techniques.；Incorporate token-level similarity metrics more heavily to avoid false positives when Jaccard similarity is very low.

### case_id=1600 FP lexical_or_api_overlap

- 方法: `getLinksFromURLFast` vs `wordFrequency`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Extracts all links and their anchor text from a web page URL using regex.
- B 摘要: Calculates the frequency of a given word by fetching and parsing a web page using a pattern.
- 静态失败原因: The static BERT/GraphCodeBERT model likely overemphasized the lexical and API overlap (e.g., URL, BufferedReader, regex, while loops) and mistook the similar boilerplate for functional similarity, ignoring the fundamentally different output and logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels as non-clone because the functions have different input/output and purpose: one extracts link structures, the other counts word occurrences. Only superficial API overlap exists.
- 共享行为: Both open a URL connection and read the page content；Both use BufferedReader to read lines；Both apply regex patterns to extract information；Both handle IO exceptions
- 行为差异: Function A returns all links and text, Function B returns an integer frequency；Function A uses multiple regex patterns and absolute URL conversion, Function B uses a single pattern for frequency；Function A loops through all matches, Function B returns on first match；Function A has debugging time checks, Function B does not
- 修正建议: Include more training examples with similar API usage but distinct functionality；Improve representation of control flow and data dependencies to differentiate output types；Add contrastive learning on pairs with high API overlap but different semantics

### case_id=1601 FN boilerplate_overlap

- 方法: `runScript` vs `import_hints`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a script file from a URL and returns its entire content as a string, returning 'error!' on failure.
- B 摘要: Reads a hints file from a URL or file system, parses puzzle pieces, places them on a board, and returns true on success or false on IOException.
- 静态失败原因: Static BERT/GraphCodeBERT predicted 0 correctly because token overlap is low (0.21) and functional semantics differ. The model was not misled by the shared I/O boilerplate, so this is not a model error but a likely BCB misannotation.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may consider these as clones because both methods perform I/O to read external data from a URL, a common boilerplate pattern. However, the functionalities diverge significantly (raw text vs. puzzle processing), so this would be a weak Type-3 or Type-4 annotation at best, likely a mislabel.
- 共享行为: Both open a URL and read data from an input stream；Both use try-catch to handle exceptions；Both involve fetching external data
- 行为差异: Function A returns the entire content as a string; Function B returns a boolean；Function A reads byte by byte; Function B reads line by line using BufferedReader；Function B parses structured data and calls other methods; Function A does no parsing；Function B handles both URL and file input; Function A only uses URL
- 修正建议: Remove false positive clones in BCB that are only similar due to shared I/O boilerplate；Incorporate higher-level functional semantics (e.g., return type, data processing) to avoid such false positives

### case_id=1602 FN benchmark_preference_bias

- 方法: `doGet` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Handles HTTP GET requests by retrieving a page, checking permissions, and rendering it with optional caching.
- B 摘要: Copies a file from source to destination using FileChannel.
- 静态失败原因: Static BERT/GraphCodeBERT correctly predicted non-clone (low token similarity, different domains). From BCB perspective, it appears as a false negative due to the BCB label being a likely mislabel.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: The BCB label may be erroneous or based on a very broad interpretation of Type-4 clone (both perform I/O and handle exceptions), but the functions are semantically unrelated.
- 共享行为: Both involve I/O operations；Both use try-catch or try-finally for resource management
- 行为差异: Different purpose: web request handling vs. file copying；Different inputs: HttpServletRequest/Response vs. File objects；Different complexity: doGet is a long servlet method, copyFile is a short utility；Different APIs: uses servlet, Page, Property vs. FileInputStream, FileOutputStream, FileChannel
- 修正建议: Re-examine the BCB ground truth for this pair; likely mislabeled；If retaining, consider that both functions share only general programming patterns, not clone-worthy

### case_id=1603 FP boilerplate_overlap

- 方法: `main` vs `main`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: A complex main method that generates adapter classes from a Prolog file using command-line options and multiple library components.
- B 摘要: A simple main method that concatenates all input files into a single output file specified as the last argument.
- 静态失败原因: Static BERT/GraphCodeBERT likely focused on surface-level similarities: both are main methods, use File, and parse arguments. It failed to capture the deep semantic divergence due to lack of long-range dependency modeling and reliance on local lexical patterns.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB annotators would label this as non-clone because the functionality is entirely different (code generation vs file concatenation). The only similarity is the method signature pattern.
- 共享行为: Both are public static void main methods；Both process command-line arguments；Both use File class
- 行为差异: Function A generates code and writes a JAR; Function B concatenates text files；Function A uses numerous specific libraries (PrologParser, FactVisitor, ClassWriter); Function B uses Scanner and PrintWriter；Function A has complex error handling and debug output; Function B throws IllegalArgumentException；Function A produces a JAR file and serialized object; Function B writes plain text
- 修正建议: Include more diverse negative examples in training that share method signatures but differ in body logic.；Use dataflow or control-flow features to distinguish different program behaviors.；Incorporate API call sequences and their semantics to better differentiate functionality.

### case_id=1604 FN boilerplate_overlap

- 方法: `main` vs `importRoles`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Constructs and sends a POST request to RenRen API with predefined parameters and prints the response.
- B 摘要: Reads XML from a URL, parses RoleName elements, and returns a list of RoleName objects.
- 静态失败原因: Static BERT models often rely on token overlap and local structure; low Jaccard and different method names, parameter names, and control flow lead to low similarity score, missing the broad network I/O theme.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may consider them clones because both involve common boilerplate for HTTP connections and reading input streams, possibly under broad Type-4 (semantic similarity) for network I/O tasks.
- 共享行为: Both make HTTP requests using URL and HttpURLConnection；Both read response line by line using BufferedReader
- 行为差异: Function A sends a POST request with multiple parameters; Function B performs a GET request (no output set)；Function A prints response to console; Function B parses XML into structured objects；Function A is a static main method for testing; Function B is a utility returning ArrayList
- 修正建议: Use dataflow-aware models to capture shared use of URL, BufferedReader, etc.；Add features for external API usage patterns；Use code summarization to capture overall intent

### case_id=1605 FN partial_functionality

- 方法: `loadSourceCode` vs `runScript`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a file resource, applies syntax highlighting, and returns HTML content.
- B 摘要: Reads a URL resource and returns raw data as a string, handling errors with a fallback.
- 静态失败原因: Low token overlap (Jaccard 0.209) and different APIs (e.g., BufferedReader vs BufferedInputStream, syntaxHighlight) cause static methods to miss the structural similarity of the read loop and exception handling.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider these clones because both are methods that load data from a remote or classpath resource, iterate over the stream, handle exceptions, and return a string, which fits a common pattern of resource reading.
- 共享行为: Open a stream from a URL-like resource；Read data in a loop；Handle exceptions with a fallback string；Build and return a string from the read data
- 行为差异: A uses BufferedReader to read lines and applies syntax highlighting; B uses BufferedInputStream to read bytes raw.；A produces HTML with <pre> tags; B returns raw escaped? data.；A obtains URL via getClass().getResource; B uses getCodeBase() + scriptName.
- 修正建议: Incorporate control-flow and data-flow features to detect similar structures (e.g., open stream, read loop, exception handling).；Use data augmentation or contrastive learning to make models robust to token-level differences in resource reading patterns.

### case_id=1606 FN partial_functionality

- 方法: `doTransfer` vs `doVersionCheck`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Acts as an HTTP proxy by forwarding a request from the servlet to a remote URL and returning the response.
- B 摘要: Checks for a new version of jEdit by reading a version file from a URL and comparing builds.
- 静态失败原因: The static BERT/GraphCodeBERT model likely focused on token-level and structural differences (low Jaccard similarity 0.157) and the distinct overall logic, failing to recognize the partial overlap in URL stream reading that BCB considered sufficient for a clone.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considered both as involving network I/O (opening a URL, reading a stream) and similar exception handling, leading to a broad Type-3/Type-4 clone label despite different high-level functionality.
- 共享行为: Both open a URL and read from an input stream.；Both handle IOException with try-catch.
- 行为差异: A forwards complete HTTP request/response including headers and body, while B only reads a specific file.；A writes to an output stream (servlet response), B does not write to any output stream.；A uses HttpURLConnection and sets request properties, B uses simple URL.openStream().；A contains loops to copy data, B reads lines and parses version/build info.
- 修正建议: Incorporate broader semantic similarity measures that capture partial functional overlap.；Use a clone detection model that accounts for shared subroutines or I/O patterns.；Augment training data with more Type-4/clone pairs that have divergent logic but common atomic steps.

### case_id=1607 FP boilerplate_overlap

- 方法: `simulate` vs `main`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Simulates reputation and rating transactions by reading input file, making SOAP calls, printing results, and asserting outcomes.
- B 摘要: Main method for generating adapters from Prolog files, parsing, generating classes, and writing output JAR.
- 静态失败原因: Static BERT models often rely on lexical and structural patterns; common keywords (File, BufferedReader, try, catch) and similar control structures (while loop, try-catch) led to overestimation of similarity, ignoring semantic differences.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB label 0 indicates non-clone, likely because despite shared boilerplate (file I/O, loops), the core functionality is entirely unrelated and only superficial patterns overlap.
- 共享行为: Both perform file I/O and use while loops；Both contain try-catch blocks for exception handling；Both print to console using System.out.println
- 行为差异: Different domain: reputation simulation vs adapter generation；Different libraries: SOAP web services vs Prolog parsing and class generation；Different outputs: console prints and assertions vs JAR file creation；Different control flow: while loop reading lines vs for loop over adapter layers
- 修正建议: Increase negative training examples with similar boilerplate but different semantics；Incorporate data flow or call graph analysis to differentiate；Use contrastive learning to emphasize semantic differences over surface patterns

### case_id=1608 FN benchmark_preference_bias

- 方法: `copyFile` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Copies a file from source to destination using NIO FileChannel.
- B 摘要: Launches a NexOpen project configuration, involving POM parsing, Hibernate setup, and resource copying.
- 静态失败原因: The model correctly predicted non-clone due to low lexical overlap and different method names; the BCB label appears to be a false positive.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider both functions as involving file copying operations (launch uses IOUtils.copy), but the overall functionality and context are vastly different, making a clone label unlikely under even broad Type-3/4 preferences.
- 共享行为: Both perform I/O operations on files
- 行为差异: copyFile is a simple file copy; launch is a complex multi-step launch process；launch involves project validation, XML parsing, property handling, and job scheduling；copyFile does not handle project configuration or Eclipse API
- 修正建议: Review BCB annotations for potential mislabels, especially when token Jaccard is very low (<0.1)；Ensure that clone labels in benchmarks are validated manually for complex, long functions with minimal lexical similarity

### case_id=1609 FN partial_functionality

- 方法: `readGeoParserResult` vs `wordFrequency`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads geographic parser results from a web service, extracting place names and gazetteer IDs.
- B 摘要: Computes word frequency by querying a web service and parsing the result.
- 静态失败原因: Static BERT/GraphCodeBERT models rely on lexical and API-level similarity, which is low here. They miss the high-level semantic pattern of 'query and parse' due to lack of contextual understanding.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label them as clones because both implement a common pattern: web service query and response parsing, which is a high-level semantic similarity despite different domains.
- 共享行为: Both construct a URL from input parameters.；Both open an HTTP connection and read the response.；Both parse the response to extract specific information.
- 行为差异: A returns a collection of tuples; B returns an integer frequency.；A has retry logic; B has simple error handling.；A uses XML parsing; B uses regex matching.
- 修正建议: Enhance models to recognize abstract patterns like URL construction + HTTP request + response parsing.；Incorporate data flow or control flow analysis to capture shared behavior across different APIs.

### case_id=1610 FN partial_functionality

- 方法: `main` vs `doVersionCheck`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Constructs and sends a POST request to the RenRen API with predefined parameters for 'feed.publishTemplatizedAction'.
- B 摘要: Connects to a version-check URL, reads a configuration file line by line, and extracts build numbers for version comparison.
- 静态失败原因: Static BERT/GraphCodeBERT likely failed due to lexical and structural differences, low token overlap, and focus on method names and local variable names that are unrelated. The model did not capture the high-level semantic similarity of network operations.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label these as clones because both functions perform network I/O operations, opening a URL, reading input streams, and handling exceptions, representing a common pattern of accessing remote resources over HTTP.
- 共享行为: Make an HTTP request to a URL；Read response line by line；Handle IOException
- 行为差异: One uses POST method with parameters; one uses implicit GET；One constructs and sends encoded parameters; one parses response lines for build numbers；One prints response; one calls another method with parsed data；One has specific API constants; one uses jEdit properties
- 修正建议: Improve model's ability to abstract common patterns like network I/O；Incorporate program slicing to extract relevant API subsequences；Use data flow analysis to identify common control structures for URL operations

### case_id=1611 FN long_range_semantics

- 方法: `getFile` vs `logging`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, updates the SOAP address endpoint in the XML, and returns the local file path.
- B 摘要: Logs the contents of an inbound web service message, including headers and payload, with optional truncation and temporary file caching.
- 静态失败原因: The model likely relied on surface-level similarities such as logging, file operations, and exception handling, while missing the fundamental semantic difference in purpose and data flow.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may label this as clone due to both being web service infrastructure methods with similar I/O and error handling patterns, despite very different core functionality.
- 共享行为: Both use logging frameworks.；Both involve file I/O (creating temporary files, reading/writing streams).；Both handle exceptions and rethrow as web-service-specific faults.；Both are part of web service frameworks (Axis vs CXF).
- 行为差异: A's main purpose is to fetch and modify WSDL files; B's purpose is to log message contents.；A modifies XML; B does not.；A returns a string file path; B returns void and logs output.；A uses NIO channels; B uses traditional streams and CachedOutputStream.
- 修正建议: Improve representation of program structure and control flow.；Incorporate type information and data dependencies.；Use more fine-grained semantic analysis to distinguish between different web service operations.

### case_id=1612 FN benchmark_preference_bias

- 方法: `doBody` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Reads a file from request and copies its contents to the HTTP response output stream.
- B 摘要: Handles Eclipse launch configuration by validating project structure, processing Maven POM files, and setting up Hibernate reverse engineering.
- 静态失败原因: Model correctly predicted non-clone (0) for this pair; the BCB label appears to be erroneous or overly broad.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: The BCB label of 1 might result from partial overlap in IOUtils.copy usage or file I/O patterns, but the functions are semantically distinct.
- 共享行为: Both use IOUtils.copy for file-to-stream copying in one part.；Both involve file I/O operations.
- 行为差异: Function A is a simple file-to-response copy; function B is a multi-step configuration with many conditions and external tool invocations.；Function A uses a single file input; function B processes multiple files including POMs and reverse engineering resources.；Function A has no project or configuration logic; function B is tightly coupled to Eclipse workspace and launch configuration.；Function B contains error handling, resource management, and persistent property setting absent in A.
- 修正建议: Review BCB labeling for this pair to confirm it is not a false positive.；Consider that BCB may have mislabeled due to token-level similarity in exception handling or IOUtils usage.

### case_id=1613 FN partial_functionality

- 方法: `doGet` vs `copy`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.65`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Handles HTTP GET requests by retrieving a page, checking user permissions, logging, and optionally caching the page output to a file.
- B 摘要: Copies the contents of a source file to a destination file using byte streams.
- 静态失败原因: Static BERT models likely relied on token-level similarity or structural similarity, and the low Jaccard similarity (0.069) and vastly different API usage caused it to miss the partial functional overlap in I/O behavior.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider the file-writing subsection of doGet (the caching part) as functionally equivalent to the entire copy function, thus deeming them clones under partial functionality similarity (Type-3/4).
- 共享行为: Both involve reading data and writing data to an output destination (file in B, file in part of A)；Both handle IOException and close streams；Both perform file I/O operations
- 行为差异: A is an HTTP request handler with control flow for page retrieval and user permissions, while B is a simple file copy utility；A uses many external dependencies (HttpServletRequest, Page, Property, etc.) while B only uses standard Java I/O；A has logging, error handling for different scenarios, and caching logic, whereas B has straightforward exception propagation
- 修正建议: Improve representation to capture sub-functional components；Use techniques that decompose functions into segments and detect similarity at sub-function level；Incorporate control-flow and data-flow analysis to identify code segments that perform similar operations despite different overall context

### case_id=1614 FN benchmark_preference_bias

- 方法: `modifyApplicationMessage` vs `readAndRewrite`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Modifies a locale-specific properties file by reading, updating a message, and writing.
- B 摘要: Reads a DICOM image file and rewrites it to another file with pixel data processing.
- 静态失败原因: The static BERT model correctly predicted non-clone (0) due to low lexical overlap and dissimilar APIs, so it did not fail.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB likely mislabeled this pair as clone due to an overly broad notion of file I/O similarity, which is not a meaningful semantic clone.
- 共享行为: Both read from a file/resource and write to a file；Both involve file I/O operations
- 行为差异: Different domains: properties file manipulation vs DICOM image processing；Different data types: text vs binary image data；Different libraries and APIs used；Different control flow and exception handling
- 修正建议: Re-evaluate the BCB label for this pair; it appears to be a false positive in the benchmark.；Consider filtering out pairs with extremely low token similarity (e.g., Jaccard < 0.1) if they are not known semantic clones.

### case_id=1615 FP lexical_or_api_overlap

- 方法: `loadSourceCode` vs `getFrameworkFactory`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a source file, applies syntax highlighting, and returns an HTML representation.
- B 摘要: Reads a service configuration file and instantiates the first non-comment class as a FrameworkFactory.
- 静态失败原因: Static BERT models (e.g., CodeBERT) rely heavily on token-level and structural similarity. The high overlap in Java I/O patterns (URL, InputStream, BufferedReader, readLine) and similar control flow (try, catch, while loop) misled the model into predicting a clone despite entirely different semantics.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels non-clones if the functional purpose is entirely different despite similar I/O boilerplate. Here, one is for source code display, the other for OSGi service loading, so BCB correctly assigns non-clone.
- 共享行为: Both open a resource from the classpath using URL and InputStream.；Both read lines from a BufferedReader in a while loop.
- 行为差异: Function A performs syntax highlighting and constructs an HTML string; Function B performs reflection to instantiate a class.；Function A handles missing file gracefully by catching exceptions and returning an error string; Function B throws an exception if the factory is not found.；Function A uses a CodeViewer class for line transformation; Function B ignores comment lines and uses Class.forName().
- 修正建议: Incorporate data flow or type dependency analysis to distinguish different usage of loaded data.；Use contrastive learning to better separate boilerplate code from core functionality.；Add training examples with similar I/O patterns but different purposes.

### case_id=1616 FP lexical_or_api_overlap

- 方法: `addQDInformation` vs `getRequestContent`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Updates internal project information by reading a local file or remote URL and parsing lines with specific prefixes.
- B 摘要: Retrieves the first line of content from a given URL via HTTP connection.
- 静态失败原因: Static models like GraphCodeBERT may rely on overlapping API calls (URL, BufferedReader) and control flow (try-catch, while loop in A versus simple sequential in B) without deeply understanding the data flow and semantic intent, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB may label as non-clone because the overall functionality and purpose are different: one is a complex data load and update routine, the other is a simple web request helper. Even though both involve URL reading, they are not semantically equivalent.
- 共享行为: Both read data from a URL (remote source)；Both use BufferedReader to read line(s)
- 行为差异: Function A has conditional logic for local vs. remote, extensive parsing, and updates multiple internal state variables；Function B simply returns the first line, no parsing or state modification；Function A handles multiple lines and specific formats; B handles only one line；Function A includes error handling for FileNotFoundException and IOException; B throws Exception
- 修正建议: Improve model to differentiate between data processing complexity and simple retrieval patterns；Incorporate control flow structure differences and data flow analysis to distinguish partial vs. complete functionality matches

### case_id=1617 FN boilerplate_overlap

- 方法: `modifyApplicationMessage` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.3`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Modifies a properties file by updating or adding a key-value pair for a given locale and message name.
- B 摘要: Filters a log file by extracting every nth line that starts with a given token and writes them to a new file.
- 静态失败原因: Static BERT/GraphCodeBERT models often overemphasize token-level overlap on API calls (e.g., FileReader, BufferedReader) and control flow, but fail to capture the distinct semantic purpose and data transformations.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may consider the shared file I/O loop structure and exception handling as sufficient for a Type-3 (near-miss) clone, overlooking the vastly different application logic.
- 共享行为: Read a file line by line using BufferedReader；Write processed lines to a new file using FileWriter；Use try-catch with IOException and print stack trace
- 行为差异: Core logic: property file modification vs line filtering based on index and token prefix；Different file formats: .properties vs .log；Different output: modified properties file vs trimmed log file
- 修正建议: Include structural comparison that differentiates data processing logic inside loops；Use data flow analysis to capture variable transformations；Incorporate method names and contextual information to disambiguate tasks

### case_id=1618 FN partial_functionality

- 方法: `importRoles` vs `invoke`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches XML from a URL and parses a list of RoleName objects.
- B 摘要: Invokes a remote method via HTTP POST, reads JSON response, deserializes it, and handles retries on connection timeout.
- 静态失败原因: Static models likely failed due to low token overlap (0.162) and different vocabulary (XML vs JSON, RoleName vs HttpPost), missing the structural similarity of network I/O and line-by-line reading.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as 'URL I/O with parsing' clones, focusing on the common pattern of reading from a URL and processing lines, despite different parsing targets.
- 共享行为: Both perform network I/O to fetch data from a URL.；Both use BufferedReader to read line by line.；Both build strings from the read lines.
- 行为差异: A parses XML for RoleName tags, while B parses JSON for generic return types.；A returns a list of RoleName objects; B returns an Object of the invoked method's return type.；B includes retry logic on ConnectTimeoutException, while A simply catches and ignores exceptions.；B uses Apache HttpClient for POST requests; A uses URL.openStream() for GET requests.
- 修正建议: Enhance model with structured representations like data flow or control flow to capture common I/O patterns.；Incorporate pre-training on tasks that emphasize functional similarity over lexical overlap.

### case_id=1619 FN partial_functionality

- 方法: `login` vs `retrieveQ`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Logs into a service and returns a session ID using HTTP POST.
- B 摘要: Retrieves the entire content of a given URL as a string.
- 静态失败原因: Low token Jaccard (0.218) and different key terms (login vs retrieveQ) mislead static models into focusing on lexical differences rather than the shared networking boilerplate.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider them clones due to the shared structure of HTTP client interactions (URL, URLConnection, BufferedReader) despite different purposes, aligning with broad Type-3/Type-4 similarity.
- 共享行为: Both open a URL connection and obtain an InputStream.；Both read lines from the InputStream using BufferedReader.；Both use similar exception handling (though different details).
- 行为差异: Function A sends POST data (email and password) and extracts a session ID from the first line; Function B simply reads all lines and concatenates them.；Function A has side effects (sets session variable); Function B is static with no side effects.；Function A returns only the session ID; Function B returns the full content.；Function A prints debug messages; Function B prints response message to error stream.
- 修正建议: Incorporate control-flow and data-flow graphs to capture the common pattern of URL opening and stream reading.；Use models that are sensitive to API call structures and can generalize across different domain-specific terms.

### case_id=1620 FP lexical_or_api_overlap

- 方法: `get` vs `callApiPost`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Performs an HTTP GET request to retrieve game records, reading line-by-line and decoding into an array, returning null on failure.
- B 摘要: Performs an HTTP POST request with parameters and headers, returning an InputStream, throwing an exception on failure.
- 静态失败原因: Static BERT methods may over-rely on surface-level similarities like both using HttpURLConnection, setting request properties, and handling streams, while missing the fundamental differences in HTTP method, input parameters, and return types.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely annotates these as non-clones because they implement different HTTP methods, have different input/output contracts, and serve distinct purposes, despite both involving HTTP connections.
- 共享行为: Both open an HTTP connection and set request properties；Both handle response streams
- 行为差异: Function a uses GET method; function b uses POST method；Function a returns an array of GameRecord; function b returns an InputStream；Function a has specific game-related headers; function b uses a generic header map；Function a handles failure by printing and returning null; function b throws an exception
- 修正建议: Incorporate structural features like method signature and control flow；Use data flow analysis to detect differences in how connections are used；Train on examples that emphasize return type and error handling differences

### case_id=1621 FN benchmark_preference_bias

- 方法: `httpRequestByPOST` vs `parse`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.6`
- 推荐路线: `preference_memory_with_manual_audit`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Sends an HTTP POST request and returns the response body as a string, handling errors by returning null.
- B 摘要: Parses a data file (or URL) into a DataSet object using configurable delimiters and type conversions, with extensive error handling.
- 静态失败原因: The model relied on token-level overlap (0.094 Jaccard) and semantic embeddings, which highlighted differences in method names, parameters, and core functionality (HTTP vs file parsing), missing the high-level similarity in I/O patterns that BCB emphasized.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider both as general data-acquisition functions that read from a source and process input sequentially, focusing on the shared boilerplate of stream reading and error handling rather than the specific domain logic.
- 共享行为: Both read input from a data source using BufferedReader.；Both handle IOExceptions and return null or throw exceptions on failure.；Both involve reading lines of text in a loop.
- 行为差异: A performs an HTTP POST request; B reads from a local file or URL without HTTP.；A returns the raw response string; B constructs a structured DataSet with column headers and typed data.；B uses StreamTokenizer for complex parsing; A simply appends lines to a buffer.；B employs reflection and type conversion; A does not.
- 修正建议: Incorporate more training examples of Type-4 clones with different domain logic but shared I/O patterns.；Use representations that capture stream-handling and error-control structures.；Fine-tune with contrastive learning on broad functional similarity.

### case_id=1622 FP lexical_or_api_overlap

- 方法: `doVersionCheck` vs `importSequences`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Checks for a newer version of JEdit by reading a version URL and comparing build numbers.
- B 摘要: Imports biological sequences from a URL in FASTA format, extracting names and sequences.
- 静态失败原因: The model was misled by overlapping API tokens like 'openStream()', 'InputStream', 'IOException', 'URL', and 'readLine', ignoring the distinct domain logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB annotators consider functional semantics; these functions have completely different purposes despite sharing I/O patterns, so they are marked non-clones.
- 共享行为: Both open a URL stream and read from it.；Both use try-catch for IOException.；Both parse lines from the stream using reading and tokenization.
- 行为差异: Function A compares build versions and shows GUI messages; Function B stores sequence data.；Function A uses BufferedReader; Function B uses a custom ImportHelper.；Function A handles UI cursor; Function B does not.；Function A only catches IOException; Function B catches MalformedURLException, EOFException, and IOException.
- 修正建议: Train with hard negatives that share boilerplate but differ in core logic.；Incorporate data flow analysis to capture different operations on parsed data.；Use contrastive learning to emphasize semantic differences despite lexical overlap.

### case_id=1623 FP lexical_or_api_overlap

- 方法: `doVersionCheck` vs `getFrameworkFactory`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Checks for new version by reading version and build information from a remote URL.
- B 摘要: Loads an OSGi FrameworkFactory by reading a service file from the classpath.
- 静态失败原因: Static BERT/GraphCodeBERT may have overemphasized the lexical similarity of common I/O API calls (URL, BufferedReader, readLine) and missed the semantic differences in data handling and overall purpose.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled non-clone because the functionality is entirely different: one is a version check UI operation, the other is a service loader. The shared I/O pattern is too generic to warrant clone annotation.
- 共享行为: Both open a URL/input stream；Both read lines using BufferedReader；Both close the stream after reading
- 行为差异: doVersionCheck shows UI messages and waits cursor; getFrameworkFactory returns an object；doVersionCheck handles IOException; getFrameworkFactory throws Exception；Different parsing logic: version/build labels vs comment skipping；Different data sources: remote URL vs classpath resource
- 修正建议: Incorporate data flow analysis to distinguish reading from different sources and different parsing logic.；Add attention to method names and parameter types to capture domain differences.；Use type-dependent embedding to differentiate between UI-related operations and service loading.

### case_id=1624 FN partial_functionality

- 方法: `addDataFromURL` vs `seeURLConnection`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads from a given URL, appends lines with newlines to a text buffer, and handles exceptions by printing and appending the URL.
- B 摘要: Reads from a hardcoded URL, appends lines without newlines to a StringBuffer, and logs the result, propagating exceptions.
- 静态失败原因: The token Jaccard is low (0.30) and the APIs differ (openStream vs URLConnection). BERT models tend to rely on surface token overlap, missing the structural similarity of reading from a URL line by line.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels functions as clones if they perform the same core task (reading URL content into a buffer) even if details like error handling or line separator differ. This pair matches as Type-3/Type-4.
- 共享行为: Both open a URL connection and read lines using BufferedReader/InputStreamReader；Both accumulate the lines into a string buffer
- 行为差异: Function A gets URL as parameter, B hardcodes it；Function A uses openStream(), B uses URLConnection.getInputStream()；Function A appends newline, B does not；Function A catches exceptions, B throws them
- 修正建议: Use data flow or AST-based features to capture the similar control flow；Include negative examples of similar token but different semantics to reduce false negatives

### case_id=1625 FN benchmark_preference_bias

- 方法: `copyTextFile` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.65`
- 推荐路线: `preference_memory_with_manual_audit`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Copies a text file from source to destination using buffered streams.
- B 摘要: Builds a website for editing by reading XML and template files, transforming them, and writing output files.
- 静态失败原因: Static BERT models rely heavily on token and structural overlap. The low Jaccard similarity (0.0679) and different method names, parameter lists, and control flow caused the model to miss the broad functional similarity of file I/O operations.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider both as file I/O operations that read and write files, even though the purposes and complexities differ. The presence of similar buffer-based read/write loops may be seen as Type-4 semantic similarity.
- 共享行为: Both methods read input from files using streams.；Both methods write output to files using streams.；Both use a buffer to read and write data in chunks.；Both handle I/O exceptions.
- 行为差异: Method A is a simple file copy; B performs complex XML transformations and string replacements.；Method A returns boolean success; B throws exceptions and returns void.；Method A uses BufferedInputStream/OutputStream; B uses plain FileInputStream and oFS.writefilestr.；Method B processes multiple files in a loop, while A copies a single file.
- 修正建议: Incorporate more abstract semantic features like I/O operations or data flow.；Use graph-based representations that capture high-level functionality.；Augment training data with diverse examples of file I/O functions.

### case_id=1626 FN benchmark_preference_bias

- 方法: `modifyApplicationMessage` vs `convert`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Modifies or adds a key-value pair in a locale-specific properties file, with fallback copy from English file if missing.
- B 摘要: Converts an ACRNEMA medical image file to DICOM format by parsing, adding UIDs, and handling pixel data.
- 静态失败原因: Static models like GraphCodeBERT rely on token/structural similarity; the low Jaccard and different API calls correctly indicate non-clone, but the model failed to match the (potentially erroneous) BCB label.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB likely mislabeled or applied an overly broad Type-4 criterion (e.g., both perform file-to-file transformation with I/O), but typical BCB guidelines would not consider these clones due to distinct functionality.
- 共享行为: Both read from a source file, process data conditionally, and write to a destination file.
- 行为差异: Different domains: internationalization vs. medical imaging.；Different data formats: properties vs. DICOM with pixel manipulation.；Different logic: key-value replacement vs. format conversion and pixel inflation.；Different error handling: generic catch vs. IOException.
- 修正建议: Review BCB annotation for this pair to confirm correctness; if false clone, adjust label.；If true clone, incorporate higher-level semantic features like file I/O patterns or dataflow analysis.

### case_id=1627 FP partial_functionality

- 方法: `getLinksFromURLFast` vs `getJSONData`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches an HTML page and extracts all hyperlinks using regex, returning two vectors of links and anchor texts.
- B 摘要: Fetches JSON data from a URL and parses it into a JSONObject.
- 静态失败原因: The static BERT model likely focused on shared lexical tokens like 'URL', 'InputStream', 'BufferedReader', 'readLine()', and the overall structure (opening connection, reading lines, building string). It may have missed the fundamental difference in parsing logic and output types.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB labels typically require both syntactic and functional similarity; these two share a common high-level pattern (fetch and parse) but differ significantly in the parsing target and output structure, so they are not considered clones.
- 共享行为: Both open an HTTP connection to a URL；Both read the response line by line using BufferedReader；Both build a string from the content；Both return parsed data from the content
- 行为差异: Method A parses HTML with regex to extract links, method B parses JSON with JSONTokener；Method A uses custom regex patterns and conditionally skips mailto links, method B has exception handling for general parsing；Method A returns two vectors, method B returns a single JSONObject；Method A includes timing checks, method B includes explicit cleanup like reader.close()
- 修正建议: Train with more examples that distinguish parsing tasks；Incorporate data flow analysis to capture the transformation of data (HTML vs JSON)；Add attention to the return type and method name

### case_id=1628 FN benchmark_preference_bias

- 方法: `main` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Copies a file using FileChannel and ByteBuffer.
- B 摘要: Configures and launches a NexOpen project build, processing Maven POM files and generating Hibernate artifacts.
- 静态失败原因: The static model correctly predicted non-clone; the BCB label is likely erroneous.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB likely mislabeled this pair, possibly due to superficial file I/O presence or annotation error.
- 共享行为: Both involve file I/O operations；Both check conditions and throw exceptions
- 行为差异: Code A is a simple file copy utility；Code B is a complex Eclipse launch handler with multiple project settings, XML processing, and external tool invocation
- 修正建议: Re-annotate BCB to correct label；Improve annotation guidelines to avoid false clones based on trivial I/O overlap

### case_id=1629 FP lexical_or_api_overlap

- 方法: `fetchUrl` vs `SRWGuiClient`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: A static utility method that fetches the content of a URL and returns it as a string.
- B 摘要: A constructor for a GUI browser that sets up a window, reads a URL, optionally processes XML/stylesheet, and displays HTML content.
- 静态失败原因: The static model likely focused on the overlapping API calls (URL, BufferedReader, InputStreamReader, readLine) and ignored the larger structural and semantic differences, especially since the Jaccard similarity is low but the overlapping tokens are common in such code.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely considered these non-clones because they have different method types (constructor vs static utility), different lengths, and different overall purposes despite sharing a small pattern of reading a URL.
- 共享行为: Both create a URL object from a string；Both open a BufferedReader on the URL's input stream；Both read lines from the input stream
- 行为差异: fetchUrl returns the entire content as a string; SRWGuiClient does not return a value and instead builds a GUI；SRWGuiClient includes XML processing, XSLT transformation, and window setup; fetchUrl has none of that；SRWGuiClient is a constructor with side effects; fetchUrl is a static utility with no side effects；SRWGuiClient handles more complex IO and parsing logic; fetchUrl simply reads all lines
- 修正建议: Use features capturing method type and class context；Incorporate control flow graph or data flow analysis to distinguish utility vs. GUI construction；Train on more diverse pairs to reduce over-reliance on shared library calls

### case_id=1630 FP lexical_or_api_overlap

- 方法: `getRequestContent` vs `getXML`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Connects to a URL and returns the first line of the response as a String.
- B 摘要: Connects to a URL (with encoded parameters) and returns the entire response body as a String.
- 静态失败原因: The model likely overemphasized the lexical and API overlap (URL, BufferedReader, InputStreamReader) and common boilerplate of HTTP fetching, while missing the critical control-flow difference between reading one line vs. reading all lines.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled 0 because the functions differ in output (first line vs. entire content) and parameter handling, which are semantically significant differences even under broad Type-3/4 criteria.
- 共享行为: Both open an HTTP connection to a URL；Both read the response using BufferedReader and InputStreamReader；Both return a String representation of the fetched content
- 行为差异: Function A returns only the first line; Function B reads all lines and concatenates them；Function A takes a single URL string; Function B takes a servlet URL and a request string and encodes the request；Function A uses explicit HttpURLConnection; Function B uses url.openStream()；Function A has no exception handling; Function B catches and returns null on three exceptions
- 修正建议: Incorporate dataflow analysis to track how many lines are read from the BufferedReader；Use structural and token-level attention on control-flow constructs (e.g., while loop vs. no loop)；Leverage type inference on return values to distinguish first line vs. entire content

### case_id=1631 FP partial_functionality

- 方法: `getUser` vs `PhoneSetImpl`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Loads a user by login from database; if missing, parses a config file to create and persist user.
- B 摘要: Constructor that reads a URL and parses lines, skipping those starting with '***', to build a phone set map.
- 静态失败原因: The model likely over-relied on lexical overlap (BufferedReader, InputStreamReader, readLine, URL) and the common pattern of reading a file line by line, ignoring the distinct high-level goals, output types, and data processing logic.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely labeled non-clone because the functions have different overall purposes (user lookup vs. phone set initialization), different output types, and only share a superficial file-reading pattern, which does not constitute functional similarity even under broad Type-4 criteria.
- 共享行为: Both read lines from a BufferedReader obtained from an InputStream of a URL.；Both iterate line by line using readLine() in a while loop.
- 行为差异: A returns a User object; B is a void constructor.；A uses a DAO for persistence; B builds a HashMap internal map.；A tokenizes lines with ':' delimiter and creates a User; B calls parseAndAdd on lines not starting with '***'.；A catches Exception broadly; B throws IOException.
- 修正建议: Incorporate method signature information (return type, parameters) into representation.；Use dataflow analysis to distinguish how each line is processed.；Add attention to the output type and the presence of method calls like userDAO.save() vs. parseAndAdd().

### case_id=1632 FP lexical_or_api_overlap

- 方法: `doVersionCheck` vs `getFullScreenUrl`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Checks for a new version of jEdit by reading a version-check URL and comparing build strings.
- B 摘要: Extracts a YouTube fullscreen URL by parsing HTML response from a video URL.
- 静态失败原因: Static BERT models may over-rely on surface-level token overlap and common API usage (URL, BufferedReader) without capturing deep semantic intent.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically requires more than just structural I/O similarity; the core functionality differs significantly, so it is labeled as non-clone.
- 共享行为: Both open a URL connection and read data line by line using BufferedReader.；Both parse the lines for specific substring patterns.；Both handle IOException or Exception generically.
- 行为差异: Different parsing logic: version-check vs extracting video parameters.；Different output: updates UI vs returning a constructed URL.；Different purpose: software update check vs video URL retrieval.
- 修正建议: Incorporate control-flow and data-dependency analysis to distinguish distinct algorithms.；Use contrastive learning with negative samples that share APIs but differ in logic.；Add task-specific or domain-aware features during training.

### case_id=1633 FN partial_functionality

- 方法: `testNetworkHTTP` vs `createDialogArea`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Test method that makes multiple HTTP connections to send device data to remote servers and reads response lines.
- B 摘要: Creates a dialog area with a browser or text widget to display license text read from a bundle resource.
- 静态失败原因: Low token Jaccard (0.153) and different API usage (HttpURLConnection vs. URL.openStream) caused the static model to miss the underlying I/O pattern, leading to a false negative.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this as a clone because both functions share a common structural pattern of opening a URL, reading lines via BufferedReader, and handling I/O exceptions, which aligns with Type-3/Type-4 clones despite different high-level contexts.
- 共享行为: Both use URL, InputStream, and BufferedReader to read lines from a source.；Both handle IOException with try-catch-finally and print stack trace.
- 行为差异: Function A uses HttpURLConnection for remote HTTP requests with query parameters; Function B reads a local bundle resource via URL.openStream() for UI display.；Function A does not explicitly close the BufferedReader; Function B closes both InputStream and BufferedReader in finally blocks.；Function A is a void test method; Function B returns a Composite dialog control.；Function A makes multiple connections; Function B reads a single resource.
- 修正建议: Train models with examples that share functional patterns but differ in API details.；Incorporate structural similarity measures like AST or data flow.；Use contrastive learning to focus on behavioral similarity rather than exact tokens.

### case_id=1634 FN boilerplate_overlap

- 方法: `main` vs `fileDownload`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.3`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: main method constructs RenRen API parameters, sends POST request, and prints response.
- B 摘要: fileDownload method downloads a file from a URL and saves it to a destination directory.
- 静态失败原因: Static BERT models rely on token overlap and structure; low Jaccard (0.14) and different method names lead to predicting non-clone, missing higher-level pattern of network I/O.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may consider them clones due to shared boilerplate for URL connection and stream reading, typical of Type-3/4 partial functionality similarity.
- 共享行为: Both open a URL connection and read input stream
- 行为差异: A sends a POST request with parameters; B performs a GET download；A prints response to console; B writes to file；A uses specific API constants and parameter objects; B works with generic URLs
- 修正建议: Incorporate control flow and data flow analysis beyond token matching；Use language models that capture semantic intent beyond surface syntax

### case_id=1635 FN partial_functionality

- 方法: `modifyApplicationMessage` vs `descargarArchivo`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Modifies or adds a message in a locale-specific properties file.
- B 摘要: Copies a file from a source path to a destination path using FileChannel.
- 静态失败原因: Low lexical overlap (Jaccard 0.07) and domain-specific terms (locale, message, descargarArchivo) cause poor embedding similarity; static models lack deep semantic understanding of file operations.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this as a clone based on a broad Type-4 criterion: both are utility methods performing file I/O, despite different specific purposes.
- 共享行为: Both perform file I/O operations；Both read from a source and write to a destination
- 行为差异: Different file types (properties vs arbitrary)；Different operations (modify properties vs copy bytes)；Different error handling (Exception vs IOException)；Different classes and methods used
- 修正建议: Improve capture of data flow and file operation patterns；Include function-level semantic roles；Adjust clone threshold to reduce false negatives from BCB-style annotations

### case_id=1636 FP lexical_or_api_overlap

- 方法: `readUNI` vs `getRequestContent`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a URL, parses tab-separated lines, and adds 'id desc' pairs to a provided vector.
- B 摘要: Opens a URL connection, reads the first line, and returns it as a string.
- 静态失败原因: Static BERT likely relied on overlapping tokens (URL, openStream, etc.) and similar method naming, missing the structural and semantic differences.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels these as non-clones because they serve different purposes (data extraction vs simple fetch) and have distinct control flows and side effects.
- 共享行为: Both read from a URL；Both open an input stream
- 行为差异: A parses multiple tab-separated fields, B reads only one line；A adds to an output vector, B returns a string；A catches exceptions silently, B throws Exception；A uses Scanner with delimiter, B uses BufferedReader
- 修正建议: Enhance models with control flow and data flow awareness；Use method-level embeddings that capture loops vs linear sequences；Incorporate return type and parameter usage information

### case_id=1637 FN lexical_or_api_overlap

- 方法: `callService` vs `runScript`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads data from a constructed URL line by line and stores result in a field, handling MalformedURLException and IOException.
- B 摘要: Reads data from a constructed URL character by character and returns the result, handling any exception with a generic error message.
- 静态失败原因: The token Jaccard similarity is low (0.21) due to different variable names, API calls (BufferedReader vs BufferedInputStream), and loop structures (while vs do-while). Static BERT models may rely heavily on token overlap and miss the high-level data flow similarity.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may consider these clones because both implement the core task of retrieving the entire content from a URL into a string, and the differences in reading granularity and output storage are acceptable within Type-3/Type-4 clone definitions.
- 共享行为: Construct a URL from base and path；Open an input stream to the URL；Read all content until end；Store content in a string
- 行为差异: A uses BufferedReader.readLine (line-by-line); B uses BufferedInputStream.read (char-by-char)；A stores result in field 'answer'; B returns the string directly；A has separate catch blocks for MalformedURLException and IOException; B catches generic Exception；A closes the input stream explicitly; B does not close the stream
- 修正建议: Use data-flow or program-dependence graph representations to capture the common pattern of reading from URL to string.；Abstract API calls into semantic roles (e.g., 'read from input stream') to generalize across similar operations.；Train on more type-3/4 clone pairs with low token overlap but similar semantics to improve generalization.

### case_id=1638 FN partial_functionality

- 方法: `login` vs `retrieveTemplate`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Logs into LOLA by sending HTTP POST with email and password, extracts session ID from response, and returns it.
- B 摘要: Retrieves a blog template from a given URL via HTTP GET, concatenates lines, caches it, and returns the cached content.
- 静态失败原因: Static BERT models (e.g., GraphCodeBERT) rely heavily on token and structure similarity; the low token Jaccard (0.17) and different method names likely caused the model to predict non-clone. The model may not capture the high-level functional similarity of 'network read' tasks, especially when the specific APIs differ (URLEncoder vs plain URL, etc.)
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider them clones because both are 'URL fetching' functions that open an HTTP connection, read response, and return a string; they share the pattern of URL construction, BufferedReader usage, and string handling, despite different HTTP methods and purposes. BCB's annotation guidelines often accept Type-3/Type-4 similarities.
- 共享行为: Both open HTTP connections to URLs；Both read response line by line using BufferedReader；Both return String results from network I/O
- 行为差异: A uses POST with encoded parameters for authentication; B uses GET to fetch template content；A extracts session ID from response; B concatenates whole response content；A handles exception by printing error and returning empty string; B throws exception (no internal catch)；A sets a session variable; B caches the template
- 修正建议: Improve model's ability to recognize similar I/O patterns despite different verb names and parameter handling；Incorporate task-level semantic embeddings (e.g., using text descriptions of function purpose) to complement structural signals

### case_id=1639 FP lexical_or_api_overlap

- 方法: `readData` vs `handle`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Parses comma-separated class-level strings to populate sets and maps with tokens, tracking maximum length of vowel tokens.
- B 摘要: Handles log file rotation, optionally compressing the log, archiving old logs, and cleaning up expired files.
- 静态失败原因: The static predictor may have been misled by both methods being long, having nested loops and conditionals, and using common API keywords like 'IOException', 'throw', 'new File', etc., despite low token Jaccard. It may have over-generalized from similar structural patterns.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels these as non-clones because they perform entirely different tasks: one is parsing initialization data, the other is log rotation. There is no syntactic or structural similarity beyond generic Java boilerplate.
- 行为差异: Function A reads from class fields and populates data structures; Function B performs file I/O and file management.；Function A has no file operations; Function B reads, writes, compresses, and deletes files.；Function A uses StringTokenizer loops; Function B uses FileChannel, GZIPOutputStream, and Archive.；Function A's logic depends on global configuration strings; Function B's logic depends on system time and file lastModified.
- 修正建议: Incorporate dataflow analysis to distinguish read-only data processing from file I/O operations.；Use functional similarity metrics that capture the goal of the method rather than just lexical structure.；Train with more diverse examples of non-clones that share only boilerplate but not semantics.

### case_id=1640 FP partial_functionality

- 方法: `loadSourceCode` vs `loadURL`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Loads source code from a file, applies syntax highlighting, and generates an HTML string.
- B 摘要: Downloads a VRML file from a URL with optional authentication, writes it to a temporary file, and reports progress.
- 静态失败原因: The model likely relied on overlapping API calls (URL, BufferedReader, InputStreamReader) and similar control flow (while loop reading lines), ignoring the different contexts, error handling, and output destinations. Low token Jaccard was overridden by semantic similarity in the embedding space for these common IO operations.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely considers these non-clones because the core functionality differs: one is for code viewing with syntax highlighting, the other for downloading and saving a file. The shared IO pattern is generic and not sufficient to deem them clones.
- 共享行为: Both use URL to open a stream and read lines with BufferedReader；Both use InputStreamReader and handle reading line by line；Both involve file-related operations (getting file length or creating temp file)
- 行为差异: A reads from a local resource file, B reads from a remote URL with optional authentication；A builds an HTML string for display, B writes to a temporary file；A performs syntax highlighting on each line, B does not；A handles exceptions generally, B throws IOException explicitly
- 修正建议: Incorporate data-flow analysis to track how read data is used (e.g., assigned to field vs. written to file)；Consider method name and surrounding class context to differentiate purposes；Use control-flow or program dependency graphs to capture functional behavior beyond statement sequence；Augment training with more diverse examples that distinguish similar API usage but different intents

### case_id=1641 FN benchmark_preference_bias

- 方法: `copy` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Copies a file from source to destination using byte buffer.
- B 摘要: Launches a Maven-based project configuration for a NexOpen project in Eclipse, handling XML profiles and properties.
- 静态失败原因: The static model correctly predicted non-clone due to very low token Jaccard similarity (0.061) and no shared structural patterns; the prediction aligns with semantic judgment.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: The BCB label of 1 is likely an annotation error or a very broad interpretation of partial functionality (e.g., both involve file I/O), but the mismatch in purpose and structure is too large for a meaningful clone.
- 行为差异: Function A performs simple file copy; Function B handles Eclipse launch configuration with multiple steps.；Function A uses only FileInputStream/FileOutputStream; Function B uses XML parsing, properties, and project resource management.；Function A is generic; Function B is domain-specific to NexOpen and Hibernate tools.；Function A has no dependencies; Function B depends on Eclipse, Maven, and custom libraries.
- 修正建议: Review and correct the BCB annotation for this pair.；Remove this pair from training data if it is an outlier.；Implement stricter filtering for low-similarity pairs in benchmark curation.

### case_id=1642 FN benchmark_preference_bias

- 方法: `main` vs `uncaughtException`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.2`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Downloads a KMZ file from a URL, unzips it, and extracts all entries to files.
- B 摘要: Handles an uncaught exception by displaying an error dialog with an option to open the issue tracker in a browser.
- 静态失败原因: Static BERT/GraphCodeBERT likely failed to detect similarity because the functions have very low token overlap (Jaccard 0.048) and operate on completely different domains (file extraction vs. GUI error handling), so the model correctly predicted non-clone; however, BCB's annotation might consider a broader semantic similarity that static models miss.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled these as clones due to both using URL, I/O streams, and exception handling, considering them as broad Type-4 semantic clones under some utility or top-level entry point category.
- 共享行为: Both involve some form of I/O operations (network/browser launch) and exception handling.
- 行为差异: Function A is a main method performing file download and extraction, while B is an exception handler with GUI interaction.；Function A uses streams for file I/O; B uses SWT widgets and clipboard.；Function A has no user interaction; B shows a dialog and waits for user input.；Function A writes to files; B writes to clipboard and launches a browser.
- 修正建议: Use dynamic analysis or flow-aware models to capture deep I/O behavior; reconsider BCB label for this pair as it may be a mislabel.

### case_id=1643 FP lexical_or_api_overlap

- 方法: `run` vs `getTicketsForQueue`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a URL line by line, extracts version, url, and additional info into fields, then notifies listeners; handles IOExceptions with error codes.
- B 摘要: Queries a request tracker for open tickets in a given queue by sending an HTTP GET request, parses response for ticket IDs, retrieves each ticket, and returns the list; handles exceptions with logging.
- 静态失败原因: The static BERT/GraphCodeBERT model likely overemphasized lexical and API overlap (BufferedReader, readLine, try-catch structure) and ignored the larger structural and semantic differences, such as the parsing logic, output types, and HTTP client usage. The model was misled by common patterns in reading HTTP responses.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labeled non-clone (0) because despite both reading lines from a network stream, the overall functionality is entirely different: one is a generic URL reader updating internal state, the other is a domain-specific ticket retrieval method. BCB emphasizes functional semantic similarity over boilerplate code overlap.
- 共享行为: Both use BufferedReader and InputStreamReader to read lines from a network input stream；Both use try-catch-finally blocks for exception handling；Both process lines in a loop and handle I/O errors
- 行为差异: Function A updates internal fields (version, url, informations) and notifies listeners; Function B returns a List<RTTicket>；Function A uses a switch statement on line index; Function B checks for specific prefixes and conditionals；Function A uses simple URL.openStream(); Function B uses Apache HttpClient with query parameters；Error handling: A sets error flags and French error messages; B throws RequestTrackerException or returns null
- 修正建议: Enhance training with hard negatives that share API usage but differ in logic；Incorporate control flow and data flow analysis to distinguish variable use；Use contrastive learning to separate classes with similar boilerplate but different intents

### case_id=1644 FP other

- 方法: `generateTopicId` vs `perform`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Generates a unique ID from a topic name using SHA hashing.
- B 摘要: Handles an HTTP request to classify a concept by sending data to a remote service and processing the response.
- 静态失败原因: The low token Jaccard (0.05) suggests minimal lexical overlap, so the model likely made an error due to misinterpreting high-level structure or a bias toward predicting clones for functions that both involve 'generation' or 'processing' of data. The model may have been confused by the presence of similar terms like 'topicName' and 'conceptName' despite different contexts.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB annotations typically mark non-clones when functions have entirely different purposes and no significant shared behavior. Here, the first is a utility hash function and the second is a Struts action controller; they do not perform similar tasks.
- 共享行为: Both involve string manipulation；Both have error handling via try-catch
- 行为差异: generateTopicId performs a one-way hash; perform executes a multi-step web request handling；generateTopicId returns a NodeId; perform returns an ActionForward；generateTopicId does no external I/O; perform sends HTTP requests and reads responses；generateTopicId is stateless; perform manages session state and multiple beans
- 修正建议: Increase training data diversity to reduce domain-agnostic false positives；Apply a confidence threshold based on token similarity or structural similarity；Incorporate a contrastive learning objective to better distinguish unrelated functions

### case_id=1645 FP lexical_or_api_overlap

- 方法: `doVersionCheck` vs `importSequences`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: This function performs a version check by reading a remote file, extracting build numbers, and calling another method to display the result.
- B 摘要: This function imports DNA/protein sequences from a remote file in FASTA format, extracting names and sequences into lists.
- 静态失败原因: The model likely relied on lexical and API overlap (common use of URL, openStream, BufferedReader, IOException) and similar control flow (try-catch, while loops), leading to a false positive prediction despite divergent semantics.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clone because the two functions have completely different semantic purposes (version checking vs sequence import) and only share superficial I/O boilerplate, which is not considered Type-3/4 similarity.
- 共享行为: Both open a URL stream and read text data line by line；Both handle IOException via try-catch blocks；Both use InputStream and InputStreamReader/BufferedReader patterns
- 行为差异: Function A parses specific keys (.build, .stablebuild) for version detection; Function B parses FASTA headers and sequence data.；Function A calls another method to perform further version checking; Function B populates lists of names and sequences.；Function A shows and hides a wait cursor; Function B does not have any UI interaction.；Function B uses a specialized ImportHelper class; Function A uses standard Java I/O classes.
- 修正建议: Increase sensitivity to semantic differences by focusing on the data being processed and the core algorithmic operations.；Incorporate more robust structural matching that goes beyond common I/O patterns.；Train on more negative examples that share API usage but differ in intent.

### case_id=1646 FN benchmark_preference_bias

- 方法: `encodeFileToFile` vs `doGet`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Encodes a file to Base64 and writes to another file, returning success status.
- B 摘要: Handles an HTTP GET request by retrieving a page, checking permissions, and rendering or caching HTML.
- 静态失败原因: Static model correctly predicted non-clone due to very low token overlap (0.083) and distinct API usage, aligning with the functional differences.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have considered both as 'input-process-output' patterns with file/stream handling, but the functional intent and complexity are vastly different.
- 共享行为: Both perform I/O operations using streams；Both use try-catch-finally blocks for resource management
- 行为差异: Function A is a simple file encoding utility; Function B is a complex web request handler；Function B involves database lookups, permission checks, caching, and logging, absent in A；Function A returns a boolean; Function B returns void and handles HTTP response
- 修正建议: Re-evaluate BCB annotation consistency for such pairs；Use fine-grained clone types to distinguish structural from functional similarity

### case_id=1647 FP lexical_or_api_overlap

- 方法: `importSequences` vs `getFullScreenUrl`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads sequences from a URL and stores names and sequences in lists.
- B 摘要: Fetches YouTube video page, extracts video ID and time, and constructs full screen URL.
- 静态失败原因: The model likely over-emphasized overlapping tokens like 'URL', 'openStream', 'InputStreamReader', 'BufferedReader', 'readLine', 'try-catch', etc., and similar control flow structures, leading to a false positive despite different functionalities.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB annotates non-clones when methods perform entirely different tasks, even if they share some common low-level API calls or structural patterns. Here, the high-level semantics are completely distinct.
- 共享行为: Both use URL connections to read data from remote URLs.；Both read input streams line by line and process the content.；Both use try-catch blocks to handle IO exceptions.；Both involve string parsing using tokenization or splitting.
- 行为差异: Different purposes: importing sequences vs. extracting video info.；Different output: void vs. String.；Different parsing logic: FASTA-like format vs. YouTube page parameters.；Different data structures and fields accessed.
- 修正建议: Incorporate more robust semantic representations, e.g., using graph-of-thought or data flow analysis.；Train on more diverse negative samples with API overlap but different purposes.；Use contrastive learning to distinguish between similar low-level patterns with different high-level intents.

### case_id=1648 FN partial_functionality

- 方法: `issueCommandToServer` vs `register`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends a command and a serialized capsule to a server URL and returns the response string.
- B 摘要: Registers a user by encoding password, setting authorities, creating a hash, making an HTTP request to a forum registration URL to obtain a forum ID, persisting user entity, and sending a confirmation email, returning success/failure.
- 静态失败原因: Static BERT models rely on token-level similarity and may miss the common I/O pattern due to low lexical overlap (Jaccard=0.113) and surrounding code differences. The model likely focuses on the overall method structure and named entities, failing to recognize the shared subroutine.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this as a clone because both functions contain a substantial common code fragment for HTTP request-response handling, which is a distinct functionality. BigCloneBench often considers such partial similarity as Type-3/Type-4 clones, especially when the shared pattern is non-trivial.
- 共享行为: Both open an HTTP connection to a server using URLConnection.；Both write data to the connection output stream.；Both read the server response line by line using BufferedReader.；Both close the input stream after reading.
- 行为差异: A only performs HTTP communication; B also performs user manipulation (password encoding, setting authorities, hashing, persisting, email sending).；A returns the response string; B returns a boolean indicating email success.；A declares IOException; B catches exceptions and wraps them as RuntimeException or handles specific exceptions.
- 修正建议: Incorporate dataflow analysis to detect shared subgraphs like HTTP request/response patterns.；Use models that compare functions based on control-flow and I/O operations rather than token overlap.；Consider fine-tuning on examples of partial functionality clones to improve recognition.

### case_id=1649 FN partial_functionality

- 方法: `doGet` vs `decodeFileToFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Handles HTTP GET request to retrieve and render a web page, with logging, caching, and permission checks.
- B 摘要: Decodes a Base64-encoded input file and writes the decoded bytes to an output file.
- 静态失败原因: Static BERT methods like GraphCodeBERT rely on token overlap and overall semantic embedding, which are very low here (Jaccard 0.08). They fail to detect partial functional similarity because the overlapping sub-behavior (file writing) is a small part of A and is masked by the dominant web-handling context. Additionally, the truncated code may obscure the similar segment.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider these clones because both methods contain a file-writing operation, and despite different contexts, the partial overlap in functionality (writing to a file as a sub-behavior of A) qualifies as a Type-4 partial clone under BCB's broad annotation guidelines.
- 共享行为: Both can write data to a file；Both use try-catch-finally for resource management；Both perform I/O operations
- 行为差异: Function A is a servlet method with complex request handling, while B is a simple static utility；A involves user authentication and page visibility, B has no such logic；A writes HTML content for caching, B writes decoded binary data；A is significantly longer with many more branches and calls
- 修正建议: Use dataflow analysis to identify subroutines within methods；Incorporate partial clone detection by comparing method segments or using similarity at the block level；Enhance model with knowledge of common I/O patterns and library usage (e.g., FileWriter, InputStream)

### case_id=1650 FN partial_functionality

- 方法: `getURLContent` vs `File2String`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads content from a URL, appends newlines, returns string.
- B 摘要: Reads content from a file or classpath resource, does not append newlines, exits on error.
- 静态失败原因: Low token overlap (0.26), different method names, API calls, and error handling patterns obscured the common 'read lines and return' pattern in static analysis.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often clones functions with the same core functionality (reading text into a string) despite differences in I/O source, error handling, or formatting, classifying them as Type-3/Type-4 clones.
- 共享行为: Reads text line by line using BufferedReader；Returns the concatenated string
- 行为差异: Input source: URL vs file/classpath；Newline handling: appends newline vs no newline；Error handling: throws IOException vs prints message and System.exit
- 修正建议: Use abstract syntax tree (AST) matching to identify the common loop structure；Incorporate semantic similarity of I/O APIs；Normalize error handling differences during comparison

### case_id=1651 FN partial_functionality

- 方法: `doTransfer` vs `doVersionCheck`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Forwards an HTTP request to another server, copying headers and body, and returning the response.
- B 摘要: Checks for a new version by reading a version file from a URL and comparing versions.
- 静态失败原因: The model's static representation likely focused on syntactic structures (method body, statements) and missed the high-level functional similarity that BCB considers, leading to a false negative (predicting non-clone).
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB might consider these clones under a broad 'network I/O' category where both involve opening a URL and reading data, ignoring differences in purpose and structure.
- 共享行为: Both open a URL connection and read input stream.；Both use java.net.URL and handle IOExceptions.
- 行为差异: doTransfer acts as a full HTTP proxy, forwarding request and response; doVersionCheck only downloads and parses a text file.；doTransfer uses HttpURLConnection with complex request/response handling; doVersionCheck uses URL.openStream() and simple line reading.；doTransfer writes to output stream; doVersionCheck displays messages via GUI utilities.
- 修正建议: Incorporate higher-level functional semantics, e.g., using API call graphs or task-specific embeddings.；Use external knowledge of common network operations to recognize partial overlap.

### case_id=1652 FN benchmark_preference_bias

- 方法: `process` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Processes a template (freemarker, xslt, or copy) and writes the result to a file based on destination configuration.
- B 摘要: Downloads a KMZ file from a URL and extracts its entries to files using unzipping.
- 静态失败原因: Static BERT correctly predicted non-clone; the BCB label appears to be an annotation error or overly aggressive Type-4 classification.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have considered both as file I/O operations with stream handling and error management, but this is too broad and does not indicate functional similarity.
- 共享行为: Both involve reading from an input source and writing to output files.
- 行为差异: A uses template processing engines; B uses zip extraction.；A's output is derived from a model and template; B's output is extracted archive entries.；Different input sources: A uses a model and template object; B uses a URL.；Different error handling contexts.
- 修正建议: Re-evaluate the BCB label for this pair; clarify Type-4 guidelines to avoid over-generalization.；Improve dataset quality by filtering pairs with low token similarity.

### case_id=1653 FN benchmark_preference_bias

- 方法: `copyResource` vs `genCustRatingFileAndMovieIndexFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Copies a resource from a URL or file to a destination file by streaming bytes.
- B 摘要: Parses a binary master file of movie ratings and generates two separate output files: an index file mapping movie names to ranges and a rating file with customer-rating pairs.
- 静态失败原因: The static model correctly identified the significant behavioral differences and low token overlap, so it predicted non-clone. It 'failed' only relative to the BCB label, which appears to be an outlier; the model's strict semantic focus was actually accurate for this pair.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled these as clones based on a very broad interpretation of Type-4 semantic similarity, where both essentially 'read data and write data to files', ignoring the specific processing. However, this is a stretch and likely a misannotation.
- 共享行为: Both perform file I/O operations (read from input, write to output).；Both use Java I/O streams and handle exceptions.
- 行为差异: A is a simple byte-by-byte copy; B involves structured binary parsing and data transformation.；B processes records with fields of fixed size (7 bytes) and groups them by movie name, writing to two output files; A writes to a single file.；B uses FileChannel and ByteBuffer for efficient I/O; A uses basic InputStream/OutputStream.；B includes loop logic to detect changes in movie name and write index records; A has no such logic.
- 修正建议: Re-evaluate the BCB label for this pair; if indeed a clone, refine the definition to avoid such broad categorizations.；Improve model robustness to handle benchmark-specific biases, possibly by incorporating more nuanced clone type distinctions.

### case_id=1654 FN benchmark_preference_bias

- 方法: `readGeoParserResult` vs `sendRequest`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.7`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Parses a record content by constructing an XML query, sending it to a geo parser service, and extracting place name entries with associated gazetteer IDs, with retry on failure.
- B 摘要: Sends a user-provided XML request to a servlet with GZIP compression, reads a compressed XML response, builds a JDOM document, but returns an empty string.
- 静态失败原因: Static BERT models rely on lexical token overlap and AST structure. The low Jaccard similarity (0.11) and different XML processing APIs (dom4j vs. JDOM) lead to low similarity scores, causing the model to miss the coarse functional similarity that BCB expects.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might label these as clones because both functions follow the same high-level pattern: send an XML request over HTTP, parse the XML response, and handle exceptions. The specific differences in XML processing details and return types could be considered minor variations in a broader clone category.
- 共享行为: Both perform HTTP requests to send XML data and receive XML responses.；Both read the response from an input stream and parse the XML.；Both catch exceptions and print stack traces or log messages.
- 行为差异: Function A returns a meaningful collection of tuples; Function B returns an empty string, ignoring the parsed document.；Function A constructs its own XML request based on parameters; Function B takes the request as a parameter.；Function A uses plain HTTP without compression; Function B uses GZIP compression for both request and response.；Function A uses dom4j for XML parsing; Function B uses JDOM.
- 修正建议: Train models to recognize high-level semantic patterns (e.g., 'send HTTP request with XML and parse response') rather than focusing on exact API calls.；Incorporate data flow analysis to capture the broader I/O behavior.；Use larger granularity of clone detection (e.g., method-level tasks) with softer similarity thresholds.

### case_id=1655 FN benchmark_preference_bias

- 方法: `doGet` vs `copy`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Handles HTTP GET request to retrieve and display a portal page, including parameter parsing, page lookup, visibility checks, logging, and rendering.
- B 摘要: Copies a file from a source path to a destination path after validating file existence and permissions, using byte buffer streaming.
- 静态失败原因: Static models like GraphCodeBERT might have failed due to long code truncation (code_a truncated) causing loss of context, or because they focused on similar API usage patterns (e.g., both use File, Exception handling) and missed the overall semantic difference.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: Possibly an annotation error, as the functions are unrelated. BCB might have labeled them as clone due to very broad Type-4 (functionality similarity) but that seems unlikely. Alternatively, both involve some form of 'copy'? But doGet does not copy files, it renders pages.
- 共享行为: Both use try-catch blocks for exception handling；Both check conditions and abort/return on failure
- 行为差异: Function A processes HTTP servlet requests and responses; function B manipulates file I/O streams；Function A involves page caching, user permissions, and logging config; function B only copies file content；Function A reads from servlet request parameters; function B reads from FileInputStream
- 修正建议: Re-annotate the pair as non-clone in the dataset；Use dataflow and control-flow analysis to detect semantic differences；Improve long-range dependency modeling for static models

### case_id=1656 FN benchmark_preference_bias

- 方法: `doVersionCheck` vs `readData`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Downloads a version check URL, reads lines looking for build version strings, and calls another version check method with extracted versions.
- B 摘要: Initializes multiple sets (topSet, leftSet, etc.) by tokenizing comma-separated string fields, then reads a file line by line to populate hash maps and sets for Tibetan transliteration mapping.
- 静态失败原因: The model correctly predicted non-clone due to low lexical overlap and different control flow; it did not fail from a semantic standpoint. The false negative arises from BCB's overly permissive annotation, not model error.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as a clone based on a broad Type-4 interpretation of 'both read data and store in data structures', overlooking the distinct purposes and input sources.
- 共享行为: Both methods read input and populate collections (strings or sets).；Both use while loops to iterate over lines or tokens.；Both handle exceptions (IOException).
- 行为差异: Function A reads from a URL, Function B reads from static string variables and a file.；A extracts version numbers, B builds character mapping sets.；A manages UI cursor (show/hide wait cursor), B has no UI interaction.；B has complex parsing with multiple columns and error handling for column count.
- 修正建议: Improve model to better capture high-level functional similarity beyond lexical overlap, but note that BCB label may be inaccurate.；Use dataflow analysis to distinguish between different types of data ingestion.；Re-evaluate BCB annotation for consistency with strict functional equivalence.

### case_id=1657 FN library_context_missing

- 方法: `copyResource` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `context_recovery_then_expert`；动态可解性: `low`；执行优先级: `medium`
- A 摘要: Copies a resource (URL or file) to a destination file using byte-by-byte stream I/O.
- B 摘要: Copies a file to another file using NIO FileChannel with transferTo.
- 静态失败原因: Low token similarity (Jaccard 0.1667) due to different APIs (InputStream vs FileChannel) and additional URL handling in copyResource, causing the model to miss the shared functionality.
- 静态 case study: 该类错误缺少关键上下文或需要深层语义，纯静态方法不可靠。
- 动态 case study: 动态执行价值较低：样本可能依赖库、框架、网络、GUI、数据库或项目上下文，需要先恢复环境或 mock 依赖。
- BCB 偏好解释: BCB often labels functions performing the same high-level task (file copy) as clones, even with different implementations and APIs, as they are Type-3/Type-4 clones.
- 共享行为: Both copy data from a source to a destination file；Both close streams/channels after copying；Both throw Exception on failure
- 行为差异: copyResource can copy from URL or file path; copyFile only from File objects；copyResource uses InputStream/OutputStream byte-by-byte read/write; copyFile uses FileChannel.transferTo；copyResource is an instance method; copyFile is static
- 修正建议: Train on diverse implementations of common tasks like file copy；Incorporate dataflow or IR-level representations to capture I/O semantics；Use contrastive learning with pairs of functionally similar but syntactically different code

### case_id=1658 FN partial_functionality

- 方法: `testNetworkHTTP` vs `getURLContent`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: A test method that performs multiple HTTP GET requests to hardcoded URLs without processing the response body.
- B 摘要: A utility method that fetches the content of a given URL and returns it as a string with proper encoding handling.
- 静态失败原因: Static BERT failed due to low token overlap (Jaccard 0.24) and large structural differences: A has hardcoded URLs, no return, logging, and test annotation; B is a generic utility with encoding and StringBuilder.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label as clone because both implement the core pattern of opening an HTTP connection, reading input line by line, which is a shared functionality despite differences in return value and number of requests.
- 共享行为: Open HTTP connection and read lines using BufferedReader
- 行为差异: A performs multiple sequential requests; B performs a single request.；A discards all response lines (empty while loop); B accumulates and returns content.；A logs and catches IOException; B declares throws IOException and handles encoding.；A disconnects in finally; B closes reader in finally.
- 修正建议: Incorporate dataflow analysis to recognize that both functions perform HTTP GET and read lines.；Use lightweight semantic abstraction to normalize constants and disregard test-specific annotations.；Train on more diverse clones with partial functional overlap.

### case_id=1659 FN partial_functionality

- 方法: `getFile` vs `copyFromTo`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies a SOAP address endpoint in the XML, and saves the file locally.
- B 摘要: Copies a source file to a destination file using FileChannel and preserves the last-modified timestamp.
- 静态失败原因: Low token overlap and different method names likely caused the model to miss the common FileChannel pattern; the model may focus on surface-level tokens rather than structural similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB might consider the shared use of FileChannel for data transfer and file I/O as sufficient partial functionality similarity to label them as clones.
- 共享行为: Both use FileChannel to transfer data between streams/files.；Both handle I/O exceptions.
- 行为差异: Function A involves network I/O (downloading from URL), while Function B copies local files.；Function A parses and modifies XML content, Function B does not.；Function A returns a file location string, Function B returns void and exits on errors.
- 修正建议: Include feature that captures usage of specific Java NIO APIs like FileChannel.；Use graph-based representations to model data flow through streams and channels.；Explicitly recognize file copying operations as a common subtask.

### case_id=1660 FN partial_functionality

- 方法: `doFinishLoadAttachment` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Handles post-download attachment actions: either saves to external storage or opens with ACTION_VIEW intent.
- B 摘要: Retrieves a resource by name, caching it from a URL to a local file system, and returns an InputStream.
- 静态失败原因: Static BERT may have overemphasized common tokens like 'InputStream', 'File', 'close', 'catch' while missing the distinct high-level purposes.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have considered both as file/stream I/O operations, but this is too broad and not functionally similar.
- 共享行为: Both perform I/O operations with streams；Both involve file creation and exception handling
- 行为差异: A saves or views an attachment; B caches a web resource；A uses content provider and intents; B uses URL connections and caching；Different return types and overall logic
- 修正建议: Incorporate control flow and data flow analysis to distinguish high-level intent；Use functional similarity based on program dependencies

### case_id=1661 FP lexical_or_api_overlap

- 方法: `SRWGuiClient` vs `downloadModel`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Constructor for a GUI browser that loads an XML URL, optionally applies XSLT, and displays HTML.
- B 摘要: Downloads an RDF model from a URL using HTTP and returns a Model object.
- 静态失败原因: The model likely focused on common API calls (URL, InputStream, IOException) and control flow (try-catch) while ignoring the divergent functionality.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels as non-clone because the functions have very different purposes (GUI construction vs. data download) and only share superficial API usage.
- 共享行为: Both open a URL connection and read input stream；Both handle IOException and MalformedURLException
- 行为差异: Code A is a GUI constructor that sets up a window and displays content; Code B is a static utility method that returns a Model；Code A involves XSLT transformation and GUI components; Code B only reads RDF data and closes stream；Code A has a complex interactive UI; Code B is purely data retrieval
- 修正建议: Incorporate method signature and return type matching；Use abstract syntax tree (AST) representation to capture structural differences；Enhance training data with more diverse non-clone pairs that share API usage but differ in logic

### case_id=1662 FN partial_functionality

- 方法: `CheckUrl` vs `doVersionCheck`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.75`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches and returns the first line of a web page given a URL string.
- B 摘要: Fetches version information from a remote resource, optionally showing a wait cursor and handling errors.
- 静态失败原因: Static BERT methods rely heavily on token overlap and syntactic structure, which here is low (0.237 Jaccard) and different. The model likely did not capture the underlying shared pattern of URL reading because of divergent method signatures, parameters, and control flow (e.g., while loop, conditionals in doVersionCheck).
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label these as clones because both involve reading from a URL, which is a core common functionality despite different end purposes. The broad Type-4 or partial functionality similarity criterion accepts such shared suboperations.
- 共享行为: Both open an HTTP connection to a URL and read content using BufferedReader.
- 行为差异: CheckUrl returns the first line as a String; doVersionCheck is void and parses multiple lines for version strings.；CheckUrl uses HttpURLConnection explicitly; doVersionCheck uses URL.openStream().；doVersionCheck shows/hides a wait cursor on a View and calls another method; CheckUrl does not.；doVersionCheck uses a specific URL from jEdit properties and handles specific line prefixes.
- 修正建议: Train models to recognize shared suboperations even when high-level functionality differs.；Incorporate data augmentation with partial functional clones.；Use cross-function attention to capture common I/O patterns.

### case_id=1663 FP boilerplate_overlap

- 方法: `loadMFileViaWeb` vs `getRequestContent`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Loads a .m file from a web URL, reads all lines, concatenates them, parses into a UserFunction, and returns it after setting its name.
- B 摘要: Opens a URL, reads only the first line of the response, and returns that line as a string.
- 静态失败原因: The static BERT model likely overemphasized the lexical overlap (URL, BufferedReader, try-catch) and missed the semantic difference in the number of lines read and the output type (UserFunction vs. String).
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels non-clone because the functions have different inputs, outputs, and overall purpose despite sharing some boilerplate for URL reading. The partial functionality similarity is insufficient for Type-3/4 in BCB.
- 共享行为: Both use URL to open a connection and read via BufferedReader.；Both handle exceptions (A catches, B throws).；Both involve reading from a web resource.
- 行为差异: A reads entire file (multiple lines), B reads only first line.；A concatenates lines and parses into a UserFunction, B returns raw string.；A sets function name, B does not.；A uses URL from codeBase+directory, B uses full URL text.
- 修正建议: Incorporate structural features like loop pattern (while vs. single read), return type, and number of I/O operations.；Use data flow analysis to track how the input is transformed into output.；Train model to distinguish fine-grained differences in reading patterns (e.g., single line vs. full file).

### case_id=1664 FN benchmark_preference_bias

- 方法: `readAndRewrite` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `None`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Reads a DICOM file, parses pixel data, and writes the modified dataset to another file.
- B 摘要: Generates HTML pages for a website by reading XML templates, transforming them with XSLT, and writing output files.
- 静态失败原因: Static BERT/GraphCodeBERT correctly predicted non-clone due to low lexical overlap and no structural similarity; the model did not fail.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB label may be an annotation error, as the functions share only trivial file I/O behavior, which is insufficient for Type-4 clone under standard BCB guidelines.
- 共享行为: Both perform file I/O (read input, write output)；Both use streams and buffers
- 行为差异: Different domains: medical image vs web page generation；Different data formats: DICOM vs XML/HTML；Different processing logic: pixel data manipulation vs XSLT transformation and string replacement；Different method signatures and parameter lists
- 修正建议: Review BCB annotation for this pair; likely false positive；Improve benchmark curation to avoid such dissimilar pairs

### case_id=1665 FP lexical_or_api_overlap

- 方法: `createDialogArea` vs `getRequestContent`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Creates a dialog area in SWT, loading a license file from a resource and displaying it in a Browser or Text widget.
- B 摘要: Opens a URL connection, reads the first line of the response, and returns it as a String.
- 静态失败原因: The static model likely overemphasized the lexical and API overlap (URL, BufferedReader, InputStreamReader) and similar structural patterns (try-finally for closing resources), ignoring the broader context and purpose of the methods.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically requires functional similarity. These two methods have different core purposes (UI setup vs. data retrieval) and different return types, so they are likely labeled as non-clones.
- 共享行为: Both read text content from a URL or resource using BufferedReader and InputStreamReader.
- 行为差异: Function A involves UI creation (Composite, Browser/Text) and reads multiple lines, while B is a simple non-UI method that returns a single line.；A reads from a local resource (bundle), B makes an HTTP connection to a remote URL.；A handles two different widgets depending on browser availability, B has no such branching.；The return types are different: Control vs String.
- 修正建议: Incorporate method name and class context as features.；Use data flow analysis to distinguish UI-related operations from pure data retrieval.；Consider the return type and the overall method signature more explicitly.

### case_id=1666 FP lexical_or_api_overlap

- 方法: `dump` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Copies a source file to a target file using buffered streams and returns success status.
- B 摘要: Handles various action commands in a settings dialog, opening file choosers and updating UI and preferences.
- 静态失败原因: The model likely overemphasized the presence of file-related APIs (File, InputStream, OutputStream vs. JFileChooser, File) and exception handling patterns, leading to a false positive despite low token overlap.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would consider these non-clones because they have fundamentally different functionality and structure; one is a low-level I/O utility, the other is a high-level GUI event handler.
- 共享行为: Both involve file-related operations (File objects and stream handling in A, file chooser in B).；Both handle exceptions (IOException in A, broader exceptions in B).
- 行为差异: Function A is a simple file copy utility; function B is a complex event handler with multiple conditional branches.；Function A performs actual I/O data transfer; function B only selects file paths and stores preferences.；Function A has a straightforward control flow; function B has nested conditionals and GUI interactions.
- 修正建议: Improve sensitivity to control flow differences and API usage context.；Incorporate structural features like AST paths or data flow to distinguish file copying from file selection.

### case_id=1667 FP lexical_or_api_overlap

- 方法: `handleHandshake` vs `loadExistingAntlibs`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Handles Minecraft server handshake authentication by validating a server key and making an HTTP request to session.minecraft.net.
- B 摘要: Loads antlib definitions from classpath resources by reading lines from a resource file and loading each as an antlib.
- 静态失败原因: Static BERT models may over-rely on surface-level API usage patterns (URL, BufferedReader, try-catch) and ignore the domain-specific context, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BigCloneBench treats these as non-clones because they perform completely different tasks (network handshake vs. resource loading) with no shared functionality beyond basic I/O boilerplate.
- 共享行为: None - the functions have no semantic overlap.
- 行为差异: Function A handles network protocol (Minecraft handshake) and server authentication.；Function B loads antlib libraries from classpath resources for build tool configuration.；Function A uses HTTP URL connection to an external server, while B reads local classpath resources.；Function A contains logic for parsing hexadecimal server IDs, B contains URI resolution for antlib loading.
- 修正建议: Train or fine-tune models on larger, semantically diverse datasets to reduce sensitivity to common boilerplate patterns.；Incorporate program dependency graphs or dataflow analysis to distinguish different semantic roles of similar API calls.；Use contrastive learning to penalize false positives from overlapping but unrelated code segments.

### case_id=1668 FN partial_functionality

- 方法: `main` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.65`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Concatenates multiple input files into a single output file, reading from command line arguments.
- B 摘要: Retrieves a resource by name with caching, downloading from a URL if not cached, and returns an InputStream.
- 静态失败原因: Low token Jaccard (0.12) and significant syntactic differences caused static models relying on lexical overlap to miss the functional similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may categorize both as 'File I/O' functionality, considering them clones due to shared high-level behavior of reading input and writing output, despite differing implementations.
- 共享行为: Both read data from an external source (files or URL) and produce output (file or InputStream).
- 行为差异: Function A is a main method with no return value, writing to a file; Function B returns an InputStream and includes caching and HTTP support.；Function A uses Scanner and PrintWriter; Function B uses Buffered streams and handles network connections.；Function A has no caching; Function B implements a cache directory and hashtable.
- 修正建议: Incorporate program dependency or dataflow analysis to capture high-level I/O patterns.；Use contrastive learning on diverse implementations of same functionality.

### case_id=1669 FP lexical_or_api_overlap

- 方法: `readUNI` vs `postData`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Downloads and parses tab-separated data from a URL, extracting id and description pairs into a vector.
- B 摘要: Sends an HTTP POST request with specified data and reads (discards) the response.
- 静态失败原因: The model likely overemphasized the shared boilerplate (URL connection, stream handling, try-finally) and ignored the fundamentally different data processing logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels as non-clone because the core functionality (parsing vs HTTP POST) is entirely different despite shared boilerplate.
- 共享行为: Both open a URL connection；Both handle I/O streams；Both close resources in a finally block
- 行为差异: A reads and parses tab-separated lines; B writes data via POST then reads response；A uses Scanner with tab delimiter; B uses PrintStream and BufferedReader；A adds parsed data to a vector; B discards response content；A catches exceptions silently; B throws Exception
- 修正建议: Add dataflow analysis to track whether data is read, written, or transformed；Incorporate method names and parameter semantics；Explicitly model HTTP-specific behavior vs generic URL reading

### case_id=1670 FP boilerplate_overlap

- 方法: `testTrainingBackprop` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Tests neural network backpropagation training on XOR data using FannJ library.
- B 摘要: Handles GUI action events to configure file paths and application settings.
- 静态失败原因: Likely due to superficial pattern matching on common Java constructs (File, IOException, loops) or misinterpreting the long function B as containing multiple sub-tasks that may appear similar to training setup in A.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clone because functions are from entirely different application domains with no syntactic or semantic similarity beyond basic Java boilerplate.
- 行为差异: Different domains: neural network training vs. GUI event handling；No overlapping functionality or shared logic
- 修正建议: Improve training data diversity to distinguish domain-specific APIs；Use AST-based or dataflow analysis to capture distinct library usage patterns

### case_id=1671 FN partial_functionality

- 方法: `main` vs `encodeFileToFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a hardcoded URL, extracts its entries, and writes each entry to a separate file.
- B 摘要: Reads a source file, Base64-encodes its content, and writes the encoded data to a destination file.
- 静态失败原因: The model likely overemphasized the functional differences (URL vs file, zip vs base64) and did not recognize the structural pattern of reading and writing bytes. Token overlap is low, and method names differ, leading the model to think they are unrelated.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels as clone when two functions share a common I/O skeleton (open, read, write, close) and perform related streaming operations, even if the specific transformation differs. Here, both are streaming bytes with buffering, so under Type-4 (functional similarity) they may be considered clones.
- 共享行为: Both use a buffer to read bytes from an input stream and write them to an output stream in a loop.
- 行为差异: A extracts zip entries from a URL; B encodes a file.；A does not handle exceptions; B does.；A produces multiple output files; B produces a single output file.；A uses a hardcoded URL; B takes input and output file parameters.
- 修正建议: Incorporate data-flow analysis to capture the stream read/write pattern.；Use graph-based representations to encode common control flow structures.；Train on a broader definition of clones that includes structural similarity.

### case_id=1672 FP lexical_or_api_overlap

- 方法: `readData` vs `run`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Reads and parses multiple comma-separated string fields and a file to initialize various sets and maps for Tibetan/Sanskrit character processing.
- B 摘要: Parses an XML file and creates a ZIP archive containing XUL extension files for a Firefox extension.
- 静态失败原因: Static BERT models may rely on overlapping API usage (e.g., StringTokenizer, HashSet, while loops) or boilerplate patterns (common Java idioms) and miss high-level semantic differences. They may get confused by the similar structural patterns of looping and adding to collections, ignoring the different contexts and outputs.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels clones only if functions share significant functionality, e.g., same operation on different data or same algorithm. Here, one is data loading, the other is archive creation; no functional overlap.
- 共享行为: Both use standard Java I/O and collection APIs；Both involve loops and conditional logic
- 行为差异: A reads and processes string tokens and a file to populate static data structures; B reads XML and writes a ZIP archive；A is data initialization; B is output generation；A operates on global/instance variables; B operates on local variables and writes to stream；A uses StringTokenizer; B uses DocumentBuilder and ZipOutputStream
- 修正建议: Improve training data to include more diverse non-clone pairs with overlapping API usage but different semantics；Incorporate data-flow or control-flow analysis to distinguish between reading input and writing output；Use contrastive learning to separate functions based on overall purpose

### case_id=1673 FP partial_functionality

- 方法: `get` vs `postData`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `None`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: HTTP GET request with custom headers to retrieve GameRecord objects, parsing response lines into an array.
- B 摘要: HTTP POST request to send data to a URL, ignoring the response body.
- 静态失败原因: Static BERT likely over-relied on overlapping API calls (URL, openConnection, BufferedReader) and loop structure, missing the critical semantic difference between GET with response parsing and POST with response discard.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely considers non-clone because the functions serve distinct purposes (retrieving vs sending data) despite shared network I/O patterns, falling outside Type-3/Type-4 partial functionality similarity.
- 共享行为: Both open a URL connection；Both set request properties；Both read from an input stream
- 行为差异: Different HTTP method (GET vs POST)；A parses response into GameRecord objects; B discards response；A returns array; B returns void；Different error handling (catch vs throws)
- 修正建议: Encode HTTP method explicitly in representation；Train to distinguish response-processing patterns vs ignoring

### case_id=1674 FN partial_functionality

- 方法: `read` vs `getPagina`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads from a URL or file path and returns an integer status code indicating success or open error.
- B 摘要: Fetches a web page as a string, returning the page content or an error message.
- 静态失败原因: Low token Jaccard (0.279), different return types (int vs String), different control flow (if-else vs while loop), and focus on lexical differences rather than high-level functional overlap.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB annotators may have considered both as 'reading from a URL' and overlooked the different return types and purposes, accepting partial functionality similarity as Type-4 clone.
- 共享行为: Both methods accept a string parameter (name/strurl) to identify a resource.；Both open a URL stream when the input resembles a URL.；Both handle IOException.
- 行为差异: Method A returns an int status code; Method B returns a String of page content.；Method A also handles local file paths; Method B only handles URLs.；Method A delegates actual reading to another method; Method B reads line-by-line and concatenates.；Method B sets an Authenticator; Method A does not.
- 修正建议: Use dataflow or program dependency graphs to capture high-level I/O operations.；Incorporate type information to distinguish return types.；Train a model to recognize partial functionality as clones when the core behavior (e.g., reading from URL) aligns.

### case_id=1675 FN benchmark_preference_bias

- 方法: `doGet` vs `genCustRatingFileAndMovieIndexFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Handles HTTP GET requests to display a portal page with caching and access control.
- B 摘要: Reads a binary file of movie ratings and generates separate index and rating files.
- 静态失败原因: Static BERT correctly predicted non-clone; the BCB label is likely erroneous or based on criteria that are too broad.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as a clone due to superficial structural similarities (e.g., both have try-catch blocks, I/O loops) or due to a labeling error in the benchmark.
- 共享行为: Both use try-catch blocks for error handling；Both perform file I/O operations
- 行为差异: Function A processes HTTP request/response, manages user sessions, and renders a page；Function B reads binary data, parses movie ratings, and writes binary output files；Function A is a servlet method, function B is a static helper for data preprocessing；Function A has complex conditional logic for caching and user permissions
- 修正建议: Re-evaluate BCB label for this pair; consider removing or correcting the clone annotation.；Ensure that clone detection benchmarks use consistent and meaningful semantic criteria.

### case_id=1676 FN benchmark_preference_bias

- 方法: `doGet` vs `copyLogic`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Handles HTTP GET requests to retrieve and display a web page, including page lookup, visibility checks, logging, and optional caching.
- B 摘要: Copies a class file from a source to destination path using file channels, with state management and error handling.
- 静态失败原因: The static model correctly predicted non-clone based on low lexical overlap and different functionality; the BCB label appears incorrect, so the model did not fail but rather disagreed with a potentially flawed ground truth.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might label these as clone due to both involving file I/O and property-based configuration, but the core functionality differs significantly; the label may be an error or based on a very broad Type-4 interpretation.
- 共享行为: Both use try-catch for exception handling；Both access properties via a Property-like class；Both perform I/O operations (HTTP response vs file copy)；Both include logging statements
- 行为差异: Code_a handles web requests and page rendering; code_b copies a file；Code_a involves user authentication and page visibility; code_b only checks state；Code_a has complex output caching logic; code_b is a simple file transfer；Code_a uses Servlet API; code_b uses Java NIO FileChannel
- 修正建议: Re-evaluate ground truth labels for consistency；Incorporate deeper semantic analysis to avoid over-reliance on lexical cues；Consider domain-specific semantics for I/O operations

### case_id=1677 FP lexical_or_api_overlap

- 方法: `actionPerformed` vs `extractZipFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Handles UI action events to configure application settings such as file paths for Graphviz/ImageMagick, font size, look-and-feel, and updates preferences via a controller.
- B 摘要: Extracts a ZIP file by iterating over its entries, creating directories or writing files to the filesystem, with optional progress updates.
- 静态失败原因: Static models may have been misled by overlapping tokens like 'File', 'filename', 'null', 'return', 'if', and exception handling patterns, while ignoring the distinct high-level purpose and control flow.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels these as non-clones because they perform completely different tasks (UI configuration vs. file extraction) with no shared semantics beyond basic Java I/O usage.
- 共享行为: Both use File and other java.io classes；Both check for null references；Both involve conditional logic with if-statements
- 行为差异: Function_a updates UI components and application preferences; Function_b extracts archive contents；Function_a is an event handler for ActionEvent; Function_b is a utility method for file extraction；Function_a uses JFileChooser and multiple preference settings; Function_b uses ZipInputStream and file output streams；Function_a has a long multi-branch structure; Function_b has a single loop over zip entries
- 修正建议: Train with hard negative examples where token overlap is high but semantics differ；Incorporate data flow or program dependency graphs to capture functional intent；Use contrastive learning to push apart embeddings of functionally different code

### case_id=1678 FN boilerplate_overlap

- 方法: `main` vs `init`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.7`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a URL and extracts its ZIP entries to local files.
- B 摘要: Initializes a report file with backup handling and writes XML header elements.
- 静态失败原因: Static BERT likely focused on overlapping tokens like 'BufferedOutputStream' and 'byte[]' but missed the differing control flows and overall purpose.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may consider both as instances of file I/O with stream processing, ignoring high-level task differences.
- 共享行为: Both use buffered input and output streams for file I/O.；Both allocate byte arrays for reading and writing data.；Both handle file existence and directory creation.
- 行为差异: Function A handles network download and ZIP extraction while B manages XML report initialization.；Function B includes complex backup and restart logic whereas A does not.；Error handling differs significantly (A throws Exception, B throws GateException and logs).
- 修正建议: Incorporate control-flow and data-dependency analysis.；Use graph-based representations to capture program semantics beyond token overlap.；Train on tasks requiring understanding of high-level functionality.

### case_id=1679 FN long_range_semantics

- 方法: `getFile` vs `EncodeReturn`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies its endpoint location, and saves it to a temporary file.
- B 摘要: Encrypts and encodes data, appends to a route file, and returns the resulting file.
- 静态失败原因: Static BERT models like GraphCodeBERT rely on token-level and AST-level patterns. The low token Jaccard (0.088) indicates few common tokens, so lexical overlap is minimal. The model may have focused on the specific API calls (e.g., XMLUtils, URL, CryptoClient) which are different, and missed the abstract file-processing pattern. Also, the long length of function A (over 60 lines) may cause the model to lose attention on the shared structure.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may consider them clones due to the high-level similarity: both are file-processing methods that take some input, create temporary files, perform transformations using file channels, and return a file. The structural pattern of creating temp files, reading/writing, and cleanup is common. BCB's Type-4 annotation often accepts such structural similarities even if domain-specific operations differ.
- 共享行为: Both create and manipulate temporary files using FileChannel；Both involve reading from an input source and writing to an output file；Both delete intermediate temporary files；Both use file streams and channels for I/O
- 行为差异: Function A downloads from a URL over network; Function B reads from internal data (DownloadData)；Function A parses XML and modifies attribute; Function B performs encryption (RawEncode, EncodeData)；Function A returns a String path; Function B returns a File object；Function A includes error logging and throws AxisFault; Function B throws EncodeFailedException, IOException
- 修正建议: Enhance model with data flow or control flow representations beyond AST；Use contrastive learning on file-processing patterns；Incorporate more training examples of similar structural clones with different APIs

### case_id=1680 FN partial_functionality

- 方法: `readGeoParserResult` vs `sendRequestObjectResponse`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads XML from a geo parser service, parses place names and IDs, and returns a collection of tuples.
- B 摘要: Sends an XML request to a servlet, saves the response to a file based on content type, and returns the file path.
- 静态失败原因: Static BERT/GraphCodeBERT models often rely on token overlap and local context. Here token Jaccard is very low (0.106), so the model correctly found no surface similarity. However, BCB's annotation may capture broader structural or functional similarity that token-level methods miss, leading to a false negative from the BCB perspective.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider them clones due to shared structural patterns: both use URL connections, XML handling, and exception handling. The overall 'communication with external service' functionality could be seen as a Type-4 semantic clone, despite different specific outcomes.
- 共享行为: Both perform HTTP requests to a remote server；Both handle exceptions with try-catch blocks；Both use URL, URL connection, and I/O streams
- 行为差异: A returns parsed data; B saves response to a file and returns filename；A has a retry loop (up to 3 attempts); B has no retry logic；A parses XML using DocumentHelper; B sends XML but does not parse the response；A includes a testing mode that returns early; B does not
- 修正建议: Incorporate AST or control-flow graph features to capture structural patterns beyond token overlap；Use clone detection methods that consider call graphs or data flow for functional similarity；Train with more examples of Type-4 clones to recognize partial functionality overlap

### case_id=1681 FP lexical_or_api_overlap

- 方法: `PageLoader` vs `getTicketsForQueue`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Constructor that fetches the content of a web page and stores it in an instance variable.
- B 摘要: Method that queries a ticket queue via HTTP, parses ticket IDs, retrieves each ticket, and returns a list.
- 静态失败原因: Static BERT/GraphCodeBERT models can be misled by overlapping API usage (e.g., BufferedReader, InputStreamReader, HTTP-related classes) and may incorrectly generalize from surface-level lexical similarity.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled as non-clone because the functions have fundamentally different purposes and outputs, despite sharing low-level I/O constructs.
- 共享行为: Both perform HTTP GET requests to retrieve data from a remote server.；Both use BufferedReader to read response line by line.
- 行为差异: Function A stores all lines into a single string; Function B parses lines to extract ticket IDs and processes each ticket.；Function A is a constructor with no return value; Function B returns a list of RTTicket objects.；Function B includes error handling, retries, and multiple API calls; Function A is a simple fetch.；Function A uses java.net.URL; Function B uses Apache HttpClient.
- 修正建议: Increase context sensitivity to differentiate between reading raw content and structured API responses.；Incorporate data flow analysis to capture different usage patterns of shared APIs.；Use more fine-grained tokenization or abstract API calls to avoid superficial overlap.

### case_id=1682 FP long_range_semantics

- 方法: `readData` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `static_summary_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Parses comma-separated strings into sets and maps, and reads a configuration file to populate data structures for Tibetan transliteration.
- B 摘要: Handles GUI action events to set file paths and preferences for Graphviz and ImageMagick tools, and updates UI settings.
- 静态失败原因: The model likely made a false positive due to the lengthy and truncated code, causing loss of context and inability to distinguish different high-level goals.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB labeled non-clone because the two functions have completely different purposes and no shared functionality beyond generic programming constructs.
- 共享行为: Both use conditionals and loops；Both manipulate String objects
- 行为差异: Function A is data initialization from configuration; Function B is event-driven UI logic；Function A builds lookup tables; Function B saves user preferences；Function A uses file I/O; Function B uses Swing components
- 修正建议: Improve model's ability to capture long-range dependencies；Use summarization or chunking to preserve overall semantics；Incorporate control flow and data flow analysis

### case_id=1683 FN partial_functionality

- 方法: `GetResponse` vs `register`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Makes an HTTP GET request and returns the concatenated response body as a string, or null on failure.
- B 摘要: Registers a User object by encoding password, setting default authority, generating hash, creating a phpBB forum user via HTTP request, persisting to database, and sending confirmation email, returning boolean success.
- 静态失败原因: Static BERT likely failed because it focused on the overall semantic divergence and large size difference, missing the shared HTTP reading idiom due to insufficient granularity or lack of subgraph awareness.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled this as a clone because both functions share the common substructure of opening an HTTP connection and reading lines, which could be considered a Type-3 or Type-4 partial functionality match under broad annotation rules.
- 共享行为: Both open an HTTP connection and read the response line by line using BufferedReader.
- 行为差异: Different overall purpose: getting raw HTTP response vs. user registration with multiple side effects.；Different return types (String vs boolean) and different exception handling.；Function B has many additional operations (password encoding, persistence, email) not present in A.
- 修正建议: Use graph-based methods (e.g., AST or CFG) to detect shared subgraphs rather than whole-function embedding.；Incorporate fine-grained token alignment focusing on critical API calls (e.g., URL.openConnection, BufferedReader, InputStreamReader).；Apply threshold relaxation for partial matches in functionally diverse functions.

### case_id=1684 FN lexical_or_api_overlap

- 方法: `copy` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies data from an InputStream to an OutputStream, handling exceptions and closing streams.
- B 摘要: Retrieves a resource by name from a URL, caches it locally, and returns an InputStream, with extensive error handling.
- 静态失败原因: Static Bert may have overemphasized lexical overlap of stream-related keywords (InputStream, close, try-catch) and IOUtils usage, ignoring the fundamentally different core purposes.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may have labeled these as clones due to shared stream manipulation patterns and error handling, considering Type-4 semantic similarity based on 'stream-related operations'.
- 共享行为: Both involve InputStream handling and stream closing in finally blocks.；Both have try-catch blocks for IOException.
- 行为差异: Function A copies data from source to sink; function B retrieves a resource and returns an InputStream.；Function B includes caching logic, HTTP connection handling, and file system operations absent in A.；Function B returns an InputStream; function A returns a long (the number of bytes copied).
- 修正建议: Incorporate dataflow analysis to distinguish stream copying from resource retrieval.；Train on more diverse examples of stream operations with different intents.；Use structure-aware embeddings that capture method-level semantics beyond API calls.

### case_id=1685 FN partial_functionality

- 方法: `doGet` vs `copyTextFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Handles HTTP GET request, retrieves a page by parameter or home, caches its output to a temporary file if not editable.
- B 摘要: Copies a source text file to a destination file using buffered streams.
- 静态失败原因: Static BERT/GraphCodeBERT likely focused on the overall semantic difference (servlet vs. file copy) and missed the partial functionality overlap of file writing, due to low token overlap and high-level structural differences.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label these as clones based on broad Type-4 similarity: both perform file output operations (write to a file), even though the overall contexts differ significantly.
- 共享行为: Both functions write data to a file (function_a writes cached page to temp file, function_b writes to destination file)
- 行为差异: Function_a is a servlet handler with complex control flow and multiple responsibilities; function_b is a simple file copy utility；Function_a involves HTTP request/response, user permissions, and page retrieval; function_b only copies bytes；Function_a's file write is conditional and not the primary purpose
- 修正建议: Train model to recognize sub-functionality similarity and partial clones；Use hierarchical or multi-level embeddings to capture nested operations；Incorporate data-flow analysis to identify shared I/O patterns

### case_id=1686 FP boilerplate_overlap

- 方法: `readTwitterFead` vs `loadExistingAntlibs`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `1.0`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a Twitter timeline via HTTP and returns the JSON response as a string.
- B 摘要: Loads antlib definitions from classpath resources and processes each antlib package.
- 静态失败原因: Static BERT/GraphCodeBERT models may over-rely on lexical and structural patterns common in Java I/O code (BufferedReader, readLine, IOException handling) and fail to capture the distinct functional intents represented by different method names, API calls, and data processing logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB considers functional semantics paramount; these functions serve entirely different purposes (HTTP fetching vs. resource loading) and would not be considered clones despite shared I/O boilerplate.
- 共享行为: Both use BufferedReader and InputStreamReader to read lines from input streams；Both handle IOException in catch blocks；Both iterate over lines using readLine() in a loop
- 行为差异: Function A performs an HTTP GET request to a specific URL, while Function B reads from classpath resources；Function A logs errors, while Function B wraps exceptions in RuntimeException；Function A appends lines to a StringBuilder, while Function B processes each line by loading antlib XML files；Function A returns a String, Function B returns void
- 修正建议: Incorporate data-flow analysis to distinguish input sources (HTTP vs. classpath)；Train with more negative examples that share I/O patterns but have different functional semantics；Use method name and API call embeddings to capture intent differences

### case_id=1687 FP lexical_or_api_overlap

- 方法: `readZoneIDs` vs `getNetworkServersIPs`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads zone IDs from a resource file and returns a set of integers.
- B 摘要: Retrieves network server IPs from a URL by parsing a specific format and returns a vector of strings.
- 静态失败原因: The static model likely overemphasized lexical and structural overlaps (e.g., while loop, readLine, try-catch, printStackTrace) and underestimated the semantic differences in parsing logic and return types, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would likely label these as non-clones because despite both reading and parsing lines, the domain logic and output types are entirely different, making them functionally unrelated (Type-4 similarity requires semantic equivalence, which is absent).
- 共享行为: Both open an input stream and read lines；Both parse each line and add results to a collection；Both use try-catch for error handling
- 行为差异: A reads from a class resource file; B reads from a URL；A returns HashSet<Integer>; B returns Vector<String>；A parses each line as an integer; B uses conditional flags to parse server IPs；A catches Exception generically; B catches specific exceptions (MalformedURLException, IOException)
- 修正建议: Train the model to focus on variable types and return types.；Incorporate data flow analysis to understand how values are transformed.；Use contrastive examples highlighting different parsing logic within similar IO patterns.

### case_id=1688 FP lexical_or_api_overlap

- 方法: `doExecute` vs `main`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: A Struts action that processes multipart form data, extracts fields and attachments, and sends an email.
- B 摘要: A main method that reads a Prolog file, parses it, and generates adapter classes into a JAR file.
- 静态失败原因: The static model likely over-relied on shared API calls (e.g., File, ByteArrayOutputStream, IOUtils) and common control structures (try-catch, loops), ignoring the distinct application logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would label as non-clone because the functions have no semantic similarity and perform completely different tasks, not even meeting Type-4 (semantic) clone criteria.
- 共享行为: Both use standard Java I/O (e.g., File, ByteArrayOutputStream, IOUtils) and handle exceptions.
- 行为差异: Different domains: email sending vs code generation.；Different input types: HTTP request vs command-line arguments and Prolog file.；Different output: ActionForward vs JAR file.；Different libraries: Struts/Apache Commons vs Prolog parser/ASM.
- 修正建议: Incorporate dataflow or control-flow analysis to distinguish different business logic.；Use domain-specific embeddings or task-aware fine-tuning to reduce false positives from generic API usage.

### case_id=1689 FN benchmark_preference_bias

- 方法: `login` vs `PhoneSetImpl`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Performs HTTP POST login to LOLA service, retrieves session ID.
- B 摘要: Constructs a PhoneSet by reading and parsing lines from a URL, skipping comment lines.
- 静态失败原因: Static BERT correctly identified semantic dissimilarity from low token overlap and distinct control flow, but the benchmark annotation was likely erroneous or overly broad, causing a false negative relative to the benchmark.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled them as clones due to broad Type-4 similarity (both perform network I/O and line parsing from URLs), ignoring the distinct functional purposes.
- 共享行为: Both use BufferedReader and InputStreamReader to read from a URL (A writes first, then reads; B only reads).；Both involve URL objects and network I/O.
- 行为差异: A sends HTTP POST with credentials; B only reads from a URL.；A returns a session ID string; B populates a HashMap.；Error handling differs: A uses try-catch, B throws IOException.；A uses OutputStreamWriter and URLEncoder; B does not.
- 修正建议: Re-annotate this pair in the benchmark to reflect true functional difference.；Consider using multiple clone-type labels to distinguish strict vs. broad similarity.

### case_id=1690 FP boilerplate_overlap

- 方法: `generateHash` vs `perform`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Generates an MD5 hash of a key string with a salt and returns the hex representation.
- B 摘要: Performs a Struts action handling form data, session attributes, and sends an HTTP request to classify concepts.
- 静态失败原因: Static BERT-like models may focus on overlapping syntactic patterns (e.g., StringBuffer, try-catch, loops) and ignore the distinct application-level semantics, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: None
- 共享行为: Both use StringBuffer for string concatenation；Both have try-catch blocks for exception handling；Both return a String value
- 行为差异: Function A is a pure hash function; Function B involves HTTP I/O and XML parsing；Function A operates on a single string; Function B processes multiple request parameters and session beans；Function A returns null on exception; Function B returns an ActionForward outcome
- 修正建议: Incorporate task-specific context or API knowledge；Use control-flow or data-flow analysis to distinguish trivial patterns；Add more negative examples of boilerplate-heavy code

### case_id=1691 FN partial_functionality

- 方法: `DecodeMapFile` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Decodes a map file by XORing each byte with an incrementing key and writes to output file.
- B 摘要: Downloads a KMZ file from a URL, extracts zip entries, and writes each entry to a file.
- 静态失败原因: Static BERT models rely on lexical and syntactic patterns, which differ significantly (low Jaccard, different APIs, different loop structures). The model correctly detected these differences, but BCB's broader semantic similarity is not captured.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as 'file processing' tasks with similar high-level structure (open stream, read buffer, process, write), labeling them as Type-4 clones despite different specific transformations.
- 共享行为: Both read binary data from an input stream into a buffer.；Both process bytes in a loop and write to an output stream.；Both handle file I/O operations.
- 行为差异: A applies XOR transformation with a mutable key; B performs zip decompression.；A writes a single output file; B writes multiple files from zip entries.；A uses FileInputStream/FileOutputStream; B uses URL connection and ZipInputStream.；A has a bug in the loop condition (reads until 0 instead of -1); B uses correct condition.
- 修正建议: Incorporate higher-level semantic features (e.g., function purpose classification).；Use dataflow analysis to abstract the transformation applied.；Train on Type-4 clone examples with diverse syntax to capture functional equivalence.

### case_id=1692 FN library_context_missing

- 方法: `readGeoParserResult` vs `createDialogArea`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.3`
- 推荐路线: `context_recovery_then_expert`；动态可解性: `low`；执行优先级: `medium`
- A 摘要: Reads a geo-parser result by constructing XML, sending HTTP request, parsing response to extract place names and ids.
- B 摘要: Creates a SWT dialog area, reads a license file from a resource bundle, and displays its text in a browser or text widget.
- 静态失败原因: The static model likely focused on low-level token overlap (low Jaccard) and different APIs (XML parsing vs SWT), missing the high-level task similarity of resource loading and text processing. It may have been deceived by the distinct domain-specific code.
- 静态 case study: 该类错误缺少关键上下文或需要深层语义，纯静态方法不可靠。
- 动态 case study: 动态执行价值较低：样本可能依赖库、框架、网络、GUI、数据库或项目上下文，需要先恢复环境或 mock 依赖。
- BCB 偏好解释: BCB may label them as clones under a broad Type-4/partial functionality view because both functions perform resource fetching and processing (reading data from a URL or bundle, parsing/displaying) and share similar I/O boilerplate.
- 共享行为: Open a URL/InputStream and use BufferedReader to read lines；Accumulate lines into a StringBuffer；Handle exceptions with try-catch or try-finally；Use standard Java I/O classes (InputStreamReader, BufferedReader)
- 行为差异: Function A constructs an XML request and sends HTTP request; Function B creates UI components；Function A parses XML response to extract structured data; Function B displays raw text；Function A includes retries on failure; Function B has no retry logic；Function A uses HashSet to deduplicate; Function B does not
- 修正建议: Incorporate task-level abstraction or function call graph information；Use data flow analysis to capture common I/O patterns；Train on more diverse examples of resource loading tasks

### case_id=1693 FN partial_functionality

- 方法: `copyResource` vs `copy`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource (URL or file) to a destination file using byte-by-byte I/O.
- B 摘要: Copies a source file to a destination file using NIO FileChannel.transferTo.
- 静态失败原因: Low token overlap (0.1887) and different API usage (InputStream vs FileChannel) misled the model; GraphCodeBERT likely focused on structural differences rather than shared functionality.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels broad Type-3/Type-4 clones based on high-level functionality, and both functions share the core purpose of copying data from a source to a destination, despite implementation differences.
- 共享行为: Both copy data from a source to a destination file.；Both handle opening and closing of streams/channels.；Both throw exceptions on I/O errors.
- 行为差异: A reads byte-by-byte; B uses channel transfer for efficiency.；A supports URL sources; B only handles File sources.；A returns void; B returns the output File.；A throws generic Exception; B throws IOException with try-catch-finally.
- 修正建议: Enhance the model to recognize functional similarity via dataflow or program dependence graphs.；Incorporate abstract representations of I/O operations (e.g., 'read from source, write to destination').；Use contrastive learning on semantically similar but syntactically different code pairs.

### case_id=1694 FN benchmark_preference_bias

- 方法: `handler` vs `readGeoParserResult`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Reads lines from a URL, extracts substrings between delimiters for lines containing a specific include string, and updates all entries in a given map.
- B 摘要: Constructs an XML request to a geolocation service, reads the response, parses XML to extract place names and optional gazetteer IDs, and returns a collection of tuples.
- 静态失败原因: Static BERT/GraphCodeBERT models rely heavily on token overlap and structural similarity. These functions have low Jaccard similarity (0.139) and different method signatures, return types, and control flow, leading the model to predict non-clone. The model failed to recognize the high-level functional pattern that BCB values.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider these clones due to both implementing the high-level pattern of 'reading from a URL and processing lines', despite different specifics. The lenient BCB style sometimes accepts broad Type-4 clones based on shared I/O and parsing behavior.
- 共享行为: Both read from URLs using BufferedReader.；Both process line-by-line input.；Both include exception handling for I/O errors.
- 行为差异: Function A updates a provided map; Function B returns a new collection.；Function A uses simple substring extraction; Function B uses XML parsing.；Function A has no output parameters; Function B has a return value.；Function B includes XML construction and a retry loop; Function A does not.
- 修正建议: Incorporate dataflow and dependency analysis to capture I/O behavior.；Use models that learn high-level functional patterns beyond lexical similarity.；Include bytecode or runtime analysis to detect common operations like URL reading and text processing.

### case_id=1695 FN partial_functionality

- 方法: `getJSONData` vs `fileDownload`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches JSON data from a URL using Apache HttpClient, parses the response into a JSONObject, and returns it, with error printing.
- B 摘要: Downloads a file from a URL using URLConnection, saves it to a destination directory as download.pdf, and logs errors.
- 静态失败原因: Static BERT/GraphCodeBERT relies on token overlap and surface-level similarity; the low Jaccard similarity (0.1687) and different method names, APIs, and variable names cause the model to miss the semantic similarity in the shared HTTP fetch pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label these as Type-4 clones because both functions achieve the high-level goal of retrieving data from a remote URL and processing it, despite differences in output format and API choices.
- 共享行为: Both perform HTTP GET requests to a given URL；Both read the response content using input streams；Both use try-catch to handle exceptions
- 行为差异: Function A returns a JSONObject, while B returns void；Function A uses Apache HttpClient, B uses URLConnection；Function A processes the response as JSON, B writes raw bytes to a file；Error handling: A prints stack trace, B uses logger
- 修正建议: Add data-flow analysis to recognize both methods as HTTP GET + response processing；Use AST-based features that capture control flow and API call sequences；Incorporate named entity recognition for standard libraries (e.g., HttpClient, URLConnection)

### case_id=1696 FN benchmark_preference_bias

- 方法: `modifyApplicationMessage` vs `gzip`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Modifies a localized properties file by replacing or appending a message key-value pair.
- B 摘要: Compresses a directory's contents into a GZIP file using byte streams.
- 静态失败原因: The static BERT model correctly predicted non-clone, so it did not fail. The BCB label appears to be a false positive.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB likely labeled as clone due to superficial structural similarity (file I/O loops and stream handling), despite completely different functionalities.
- 共享行为: Both perform file I/O operations with read and write loops.；Both handle streams and close resources.
- 行为差异: Function A operates on text properties with locale-specific files, while B compresses binary data.；A modifies/updates existing content; B creates a compressed archive.；A uses character streams (Reader/Writer), B uses byte streams (InputStream/OutputStream).
- 修正建议: Re-annotate the pair as non-clone in the benchmark.；Use functional semantics rather than structural heuristics for clone detection.

### case_id=1697 FP lexical_or_api_overlap

- 方法: `readTwitterFead` vs `PageLoader`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Downloads a Twitter timeline feed via HTTP GET using Apache HttpClient, handling errors and logging.
- B 摘要: Opens a URL connection and reads all lines into a string using BufferedReader, throwing exceptions.
- 静态失败原因: Static BERT likely overfitted on shared tokens like 'BufferedReader', 'readLine', 'url', and while-loop pattern, ignoring differences in HTTP client usage and error handling.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clone because the implementations differ significantly in API usage, error handling, and structure, despite similar I/O goal.
- 共享行为: Both retrieve data from a remote URL and read line by line；Both build a single string from the lines read
- 行为差异: A uses Apache HttpClient and HttpGet; B uses URL.openStream()；A has detailed error handling with try-catch and logging; B throws Exception；A is a method returning the string; B is a constructor setting a field；A uses Android Log; B does not
- 修正建议: Enhance model to distinguish between different HTTP client libraries；Include data flow analysis to differentiate method vs constructor；Use AST-based structural comparison to capture API call differences

### case_id=1698 FN partial_functionality

- 方法: `copyFile` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a file from source to destination using FileChannel.transferTo.
- B 摘要: Retrieves a resource as an InputStream with caching logic, downloading from URL if not cached.
- 静态失败原因: Static BERT models rely on token overlap and may fail to recognize the shared byte-copying pattern due to low Jaccard similarity (0.08) and different surface forms (FileChannel vs BufferedStream). The model likely sees no clone because of low token similarity, but BCB favors semantic similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: None
- 共享行为: Both involve reading bytes from a source and writing to a destination file.
- 行为差异: Function A is a straightforward file copy; Function B includes URL connection, caching, HTTP status checks, and returns an InputStream.；Function B has complex control flow with conditional caching; Function A is linear.
- 修正建议: Improve model's ability to detect shared subfunctionalities even when overall method differs.；Incorporate dataflow analysis to identify common byte-copying patterns.；Train on more examples of Type-4 clones with low token overlap.

### case_id=1699 FN partial_functionality

- 方法: `runInternal` vs `issueCommandToServer`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.95`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads and parses OPDS catalog from a URL using HTTP, handling pagination and partial loading of entries.
- B 摘要: Sends a command to a server via HTTP POST and returns the response as a string.
- 静态失败原因: Low token overlap and structural differences misled the static model, which relies on lexical and syntactic similarities.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as Type-4 semantic clones due to shared underlying pattern of HTTP communication, despite different high-level intents.
- 共享行为: Both establish HTTP connections and read server responses using InputStream.
- 行为差异: A handles pagination, redirects, error codes, and partial loading; B sends a single POST command.；A reads from a URL (GET-like); B writes and reads (POST).；A performs complex parsing of catalog entries; B simply returns the raw response string.；A includes progress reporting and error handling for network issues; B has minimal error handling.
- 修正建议: Incorporate more context-aware embeddings that capture high-level intent.；Use data augmentation with contrastive learning to distinguish similar I/O patterns with different semantics.；Combine token-level features with structural features like control flow graphs.

### case_id=1700 FN boilerplate_overlap

- 方法: `main` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.4`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: A test method that verifies correct reading of a file using StraightStreamReader.
- B 摘要: A method that builds a site for editing by transforming XML pages and writing output files.
- 静态失败原因: The model likely focused on the high-level functional difference (test vs. production) and low token overlap, missing the common I/O idioms that BCB considers as behavioral similarity.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may label it as a clone due to shared core I/O patterns (file reading into char buffers with loops) and broad criteria accepting partial functionality similarity.
- 共享行为: Use FileInputStream to read file content；Utilize char buffer and loops for reading；Handle IOException
- 行为差异: Function A is a test for stream reading correctness; Function B is part of web page generation.；Function A writes a test file and deletes it; Function B reads from configuration paths and writes to output paths.；Function A is standalone; Function B uses many parameters and external libraries.
- 修正建议: Incorporate structural or dataflow analysis to detect common I/O patterns.；Train with more type-4 clones to recognize partial functionality similarity.

### case_id=1701 FP lexical_or_api_overlap

- 方法: `handleHandshake` vs `run`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Validates Minecraft handshake by checking username and optionally making HTTP request to session server; sends login packet or disconnects.
- B 摘要: Loads a text resource from classpath, reads it line by line, and sets it as text on a Swing component via invokeLater.
- 静态失败原因: Model may have over-relied on superficial similarities like both having URL, BufferedReader, try-catch, and exception handling, missing the completely different purposes.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically requires some shared functionality beyond common API usage; these functions have no semantic overlap relevant to type-3/4 clones.
- 共享行为: Both use URL and BufferedReader for I/O；Both catch and handle exceptions generically
- 行为差异: A is networking protocol handling; B is UI resource loading；A has complex conditional logic; B reads sequentially from a file；A sends packets over network; B updates Swing component；A writes to network output; B reads from classpath
- 修正建议: Train model to consider control flow and data dependencies as evidence of functionality, not just token overlap.；Use graph-based representations to capture program logic and distinguish I/O direction (read vs write).

### case_id=1702 FN benchmark_preference_bias

- 方法: `modifyApplicationMessage` vs `processAddByURLSubmit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Modifies a locale-specific properties file by updating or adding a key-value pair.
- B 摘要: Processes a URL by fetching its content as a string and passing it to a DOAP submission function.
- 静态失败原因: Static BERT likely relied on low token overlap and differing structural patterns, correctly identifying non-clone; it did not fail as it predicted non-clone.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as clone due to being in the same project module or both involving file/stream handling, but the functionality is vastly different; this is likely a mislabel.
- 共享行为: Both involve I/O operations with streams；Both use try-catch for exception handling
- 行为差异: Function A modifies local properties files; Function B fetches remote content；Function A writes to a file; Function B only reads and processes；Function A deals with text properties; Function B deals with XML/DOAP data；Function A has a specific goal of updating a key-value pair; Function B submits fetched data to another processing function
- 修正建议: Re-evaluate BCB labels for such pairs to ensure consistency；Enhance static models with project-level context or functional role embeddings to avoid over-reliance on lexical cues

### case_id=1703 FN partial_functionality

- 方法: `copy` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Copies a file from source to destination using NIO channels with proper resource cleanup.
- B 摘要: Launches a NexOpen project configuration, involving XML processing, file operations, and copying a resource to a temporary file.
- 静态失败原因: Static models like GraphCodeBERT rely heavily on lexical token overlap and structural similarity. The low Jaccard similarity (0.057) and very different method lengths/complexity caused the model to miss the shared I/O behavior. The common functionality is hidden within a larger, context-rich method, and the model did not recognize the underlying copy pattern due to lack of data flow understanding.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider this a clone because both functions perform a core data transfer operation (copying bytes from input to output) and exhibit similar resource management patterns (nested try-finally for closing streams/channels). Despite differences in complexity and domain, the partial functional overlap in file I/O aligns with BCB's broad Type-4 annotation criteria.
- 共享行为: Both perform file I/O operations that copy data from an input source to an output destination；Both use try-finally blocks to ensure proper closure of streams and channels；Both handle byte-level data transfer (FileChannel.transferTo and IOUtils.copy)
- 行为差异: Function A is a simple file copy utility; Function B is a complex method with multiple steps including XML parsing and project setup；Function A copies the entire file using zero-copy transfer; Function B copies a string resource to a ByteArrayOutputStream and then creates a file；Function B includes conditional logic and exception handling specific to Eclipse launch configurations；Function A has no domain-specific dependencies; Function B depends on Eclipse, Hibernate, and NexOpen framework
- 修正建议: Incorporate data flow analysis to identify common I/O operations across differently structured methods；Add training examples that highlight partial functional overlap in file copy operations；Use code summarization techniques to focus on actual data transformations rather than full method semantics；Improve representation of resource management patterns to capture similar exception handling structures

### case_id=1704 FP boilerplate_overlap

- 方法: `main` vs `transferWSDL`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a Prolog file, parses it, generates adapter classes, and writes them to a JAR file.
- B 摘要: Downloads a WSDL from a URL, optionally with authentication, and saves it to a temporary file.
- 静态失败原因: The model likely over-relied on superficial API similarities (URL, File, IOException, streams) and did not capture the drastically different control flows and purposes. The low Jaccard score (0.074) suggests that lexical overlap is minimal, but the model may have been misled by the presence of common Java I/O patterns or mis-embedded representations.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels clones only when there is significant functional overlap, even if partial. These two functions have no common business logic; they are from completely different domains. The only similarities are generic boilerplate (file I/O, exception handling) which BCB does not consider clone-worthy.
- 共享行为: Both perform file I/O operations；Both handle exceptions with try-catch blocks；Both use URL and URLConnection classes
- 行为差异: Function A generates Java classes from Prolog; function B downloads and saves an XML file.；Function A processes local files and uses a complex adapter generation pipeline; function B only downloads and saves a remote resource.；Function A has a main method with command-line parsing; function B is a private method with no user interaction.；Function A outputs a JAR file; function B outputs an XML file.
- 修正建议: Incorporate higher-level structural or dataflow features to distinguish different application logic.；Use contrastive learning to reduce the impact of common API sequences that appear in unrelated tasks.；Add more training examples that explicitly show non-clones with similar boilerplate but different semantics.

### case_id=1705 FN partial_functionality

- 方法: `writeFileType` vs `register`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a file of URIs, connects to each URI, checks its content for ontology keywords (OWL, RDFS, RDF), and writes the URI with a classification tag to an output file.
- B 摘要: Registers a user by encoding password, setting date, adding default authority, creating hash, calling a phpBB forum URL to get a forum ID, persisting the user, and sending a confirmation email, returning success status.
- 静态失败原因: The static BERT/GraphCodeBERT model likely failed because it relied on token-level similarity and syntactic structure, which are low (Jaccard=0.1445). It did not capture the high-level structural pattern of URL fetching and line reading, leading to a false negative prediction.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider these clones due to broad structural similarity: both are methods that open a URL connection, read lines, and handle exceptions, which is a common type-4 pattern in BigCloneBench where human annotators accepted partial functional similarity.
- 共享行为: Both functions use URLConnection to connect to external URLs and read lines from the input stream.；Both functions handle I/O exceptions with try-catch blocks.；Both functions involve reading data line by line from a BufferedReader.
- 行为差异: Function A processes multiple URIs from an input file; Function B processes a single User object parameter.；Function A writes classification results to a file; Function B persists to a database and calls an external forum API.；Function A is static and returns void; Function B is an instance method that returns boolean.；Function A checks for specific ontology keywords; Function B sets various user properties and sends email.
- 修正建议: Train with data augmentation that emphasizes higher-level structural patterns.；Incorporate dataflow or control flow analysis to detect common I/O patterns.；Use contrastive learning to distinguish between true semantic clones and mere lexical overlap.

### case_id=1706 FP lexical_or_api_overlap

- 方法: `readTwitterFead` vs `executePost`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a fixed Twitter JSON feed using HTTP GET with Apache HttpClient and returns the response as a string.
- B 摘要: Executes an HTTP POST to a specified URL with parameters using HttpURLConnection and returns the response as a string.
- 静态失败原因: The model over-relied on common tokens like 'Http', 'response', 'BufferedReader', and the generic try-catch structure, ignoring specific method signatures and library classes.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: None
- 共享行为: Both make HTTP requests and read response line by line into a string using BufferedReader and InputStream.
- 行为差异: HTTP method: GET vs POST；Client library: Apache HttpClient vs java.net.HttpURLConnection；URL handling: hardcoded vs parameterized；Error handling: logs error vs returns null
- 修正建议: Incorporate method name and parameter analysis；Use data flow to track HTTP method and client type；Add graph-based features to capture library differences

### case_id=1707 FN partial_functionality

- 方法: `getFile` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies the endpoint, and saves it to a temporary file, returning the file path.
- B 摘要: Copies a file from one File object to another using FileChannel.
- 静态失败原因: Static BERT methods like GraphCodeBERT rely on token similarity and syntactic patterns. The low token Jaccard (0.15) and different method signatures likely caused the model to miss the semantic similarity in data transfer. The model may not recognize that FileChannel operations are functionally similar despite different method names (transferFrom vs transferTo) and additional logic in getFile.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider this a Type-4 clone because both functions share the core behavior of copying data via FileChannel, and partial functionality similarity is accepted in BCB's broad annotation. The WSDL-specific parts are seen as additional but not negating the clone relationship.
- 共享行为: Both use FileChannel to transfer bytes from an input source to an output destination.
- 行为差异: getFile downloads from a URL, copyFile reads from a local file.；getFile performs XML parsing and modification, copyFile does not.；getFile returns a String, copyFile returns void.；getFile handles multiple exception types, copyFile only throws IOException.
- 修正建议: Improve model's ability to recognize shared sub-functionality even when embedded in larger functions.；Use fine-grained data flow analysis to detect common operations like channel-based data transfer.；Incorporate API usage patterns to identify similar I/O operations.

### case_id=1708 FN partial_functionality

- 方法: `doGet` vs `init`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Handles HTTP GET to display a portal page with caching and access control.
- B 摘要: Initializes a batch report by backing up the existing file and parsing old results.
- 静态失败原因: Static BERT relies heavily on lexical and API token overlap, which is low (0.14 Jaccard), and the different method names and contexts mask the underlying structural similarities in control flow and common library usage.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider them clones due to shared patterns of file handling, logging, and error recovery, typical of broad Type-3/4 partial functionality similarity.
- 共享行为: File I/O operations (create, write, read)；Error handling with try-catch blocks；Logging messages via logger；Conditional checks on file existence
- 行为差异: Function A operates in HTTP servlet context, B is standalone initialization；A deals with page visibility and user permissions, B with XML report parsing；A caches page output to temp files, B processes old report for completed documents；A sends HTTP errors, B throws exceptions
- 修正建议: Use structural features like control flow graph or data flow similarity；Incorporate API call sequences (e.g., File I/O, logging) as features；Apply code summarization to capture high-level intent

### case_id=1709 FP boilerplate_overlap

- 方法: `doBody` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a file based on request data and copies its content to the HTTP response output stream.
- B 摘要: Handles GUI action events by showing file choosers and saving user preferences for various settings.
- 静态失败原因: Likely due to lexical overlap of common Java constructs (if, return, try, catch, etc.) and method signatures with parameters, despite low Jaccard similarity. The model may have been confused by the length and structure of function B.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would label as non-clone because the functionalities are completely different: one is a file-to-response copy, the other is a GUI preferences manager.
- 共享行为: Both are void methods that perform I/O operations (file reading vs file chooser) and handle exceptions.
- 行为差异: Function A is a web request handler; B is a GUI event listener.；A reads file content; B only selects file paths.；B has complex branching logic for multiple commands; A is linear.；A uses try-catch-finally; B has no global exception handling.
- 修正建议: Incorporate data flow analysis to differentiate between file content and file path operations.；Use semantic role labeling or domain classification (web vs GUI).；Improve handling of long methods with truncation to avoid misleading patterns.

### case_id=1710 FN benchmark_preference_bias

- 方法: `updateFile` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Copies a file to a new location using FileChannel, ensuring parent directories exist.
- B 摘要: Builds a website for editing by transforming XML pages with XSLT and writing output files.
- 静态失败原因: The model correctly predicted non-clone; it did not fail. The BCB label appears to be an annotation error or over-broad interpretation.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled these as clones due to both engaging in file writing, but the functions are semantically unrelated beyond basic file I/O, which is too broad for a meaningful clone.
- 共享行为: Both involve file I/O operations (reading/writing files).
- 行为差异: updateFile is a single file copy with channel transfer; buildSiteForEdit is a multi-step site generation with XML parsing, XSLT transformation, and string manipulation.；updateFile has no loops or conditional logic beyond existence check; buildSiteForEdit iterates over pages, handles multiple exceptions, and uses extensive string processing.；updateFile is a private utility method; buildSiteForEdit is a public method with many parameters and complex workflows.
- 修正建议: Review BCB annotations for this pair to confirm correctness; consider stricter definition of functional similarity.；Improve model robustness to ignore trivial I/O overlap.

### case_id=1711 FP lexical_or_api_overlap

- 方法: `main` vs `downloadFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads from a URL and prints each line to standard output.
- B 摘要: Downloads a file from a URL to a local destination with progress tracking.
- 静态失败原因: The static model likely focused on lexical and API overlap (e.g., 'URL', 'InputStream', 'BufferedReader'/'BufferedInputStream', 'readLine'/'read') and missed the structural and behavioral differences in control flow and output.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely considers these non-clones because the functionalities differ significantly: one is a simple web page printer, the other is a file downloader with progress updates. Although they share some API calls, the overall semantic purpose is distinct.
- 共享行为: Both open a URL connection and read data from an input stream.；Both close the input stream after reading.
- 行为差异: A prints data to console; B writes data to a local file.；A has no progress tracking; B tracks download progress and updates a MessageFrame.；A returns void; B returns boolean true after completion.；A uses BufferedReader and InputStreamReader; B uses BufferedInputStream and URLConnection.
- 修正建议: Incorporate data flow and control flow information into the model.；Use contrastive learning to distinguish similar API usage patterns with different behaviors.；Add features capturing output direction (console vs file) and progress tracking.

### case_id=1712 FP lexical_or_api_overlap

- 方法: `PhoneSetImpl` vs `getFullScreenUrl`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Constructor that reads a URL, parses lines into a phone set map, ignoring lines starting with "***".
- B 摘要: Private method that fetches a YouTube URL, extracts video parameters, and returns a full screen URL.
- 静态失败原因: The model likely overemphasized the superficial lexical and API overlap (URL, BufferedReader, while loop) and missed the semantic difference in the purpose and output.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this non-clone because the overall functionality is fundamentally different despite shared I/O patterns; they are domain-specific and not semantically equivalent.
- 共享行为: Both read from a URL using BufferedReader；Both iterate over lines in a loop；Both perform string manipulations on lines
- 行为差异: A populates a map, B extracts specific parameters；A ignores lines with '***', B searches for 'fullscreenUrl'；B has complex string splitting and constructs a new URL, A simple line parsing；A is a constructor, B is a method with return value
- 修正建议: Incorporate data-flow or control-flow features that capture the input-output transformation；Use task-specific fine-tuning to distinguish different domain functionalities；Add a module that compares overall method purpose beyond local patterns

### case_id=1713 FP lexical_or_api_overlap

- 方法: `wordFrequency` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Counts word frequency by querying a web service and parsing the response for a number.
- B 摘要: Searches Google Images, extracts image URLs, and updates a GUI component.
- 静态失败原因: Static BERT/GraphCodeBERT likely overfitted on lexical and API-level similarities (URL, BufferedReader, IOException) without capturing the divergent program logic and output behavior.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely considers these non-clones because the functionality is entirely different: one counts word frequency, the other performs image search and GUI updates. Token overlap is low, and the intent differs.
- 共享行为: Both make HTTP requests to external URLs；Both read from URL streams using BufferedReader；Both handle IOException and MalformedURLException
- 行为差异: wordFrequency returns an int; googleImageSearch returns void and modifies a UI；Different URL construction and query parameters；Different parsing strategies: regex matching vs splitting on a pattern；Error handling: printStackTrace vs showing error dialog
- 修正建议: Incorporate data-flow and type-based features to distinguish output types；Use control-flow abstraction to differentiate return vs void methods；Add training examples with similar API usage but different semantics

### case_id=1714 FP library_context_missing

- 方法: `process` vs `readData`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `context_recovery_then_dynamic`；动态可解性: `low`；执行优先级: `low`
- A 摘要: Processes templates by generating output files based on template type and destination.
- B 摘要: Parses comma-separated token strings and a file to populate character sets and lookup tables.
- 静态失败原因: Static BERT models may rely on surface-level features like method name 'process' and 'readData' both being common data processing verbs, and both functions contain try-catch blocks and I/O operations, leading to overgeneralization. However, the token Jaccard is low, so it might have been a case of model overfitting or relying on structural patterns (e.g., switch statements vs. loops) but misclassifying due to limited context.
- 静态 case study: 该类错误缺少关键上下文或需要深层语义，纯静态方法不可靠。
- 动态 case study: 动态执行价值较低：样本可能依赖库、框架、网络、GUI、数据库或项目上下文，需要先恢复环境或 mock 依赖。
- BCB 偏好解释: BCB typically treats functions with completely different purposes as non-clones, even if they share common elements like file reading or exception handling. Here, the functionalities are entirely distinct.
- 行为差异: Function A performs file I/O and template processing; Function B parses strings and files into collection structures.；Function A uses switch on destination and type; Function B uses tokenization and file line parsing.；Function A outputs files; Function B builds in-memory data structures.
- 修正建议: Improve model understanding of domain-specific APIs (e.g., Freemarker templates vs. StringTokenizer).；Add more negative examples where functions share structural patterns but differ in core logic.；Incorporate data flow analysis to distinguish between output generation and data initialization.

### case_id=1715 FP lexical_or_api_overlap

- 方法: `handler` vs `getFullScreenUrl`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Generic handler that opens a URL, reads lines, and for each map entry, extracts a substring between target delimiters and updates the map.
- B 摘要: Specific method to extract video_id and t from a YouTube page line containing 'fullscreenUrl', then construct a full video URL and update GUI.
- 静态失败原因: The static model likely over-relied on the lexical overlap of common Java I/O patterns (URL, BufferedReader, while loop, substring, etc.) and did not capture the distinct data flow and purpose differences.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels these as non-clones because the overall functionality is different: one is a generic substring extraction handler, the other is a YouTube-specific URL builder. The structural similarity is low (token Jaccard 0.23) and the shared API usage is incidental.
- 共享行为: Open a URL and read lines with BufferedReader；Iterate over lines and perform substring searching and extraction；Use try-catch for IO exceptions
- 行为差异: Function A takes a Map and TargetPage as parameters and returns void; Function B takes no parameters and returns a String；Function A updates an existing map; Function B constructs a new URL string；Function A uses target.getInclude() to filter lines; Function B looks for a specific string 'fullscreenUrl'；Function B includes GUI updates and debug printing; Function A does not
- 修正建议: Enhance model with data flow analysis to track how input/output variables are used；Incorporate structural code embeddings that distinguish between generic and specific logic；Add contrastive training to separate similar API usage but different semantics

### case_id=1716 FP boilerplate_overlap

- 方法: `getLinksFromURLFast` vs `checkForUpgrade`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Parses a URL's HTML content to extract all hyperlinks and link text, returning them as two vectors.
- B 摘要: Connects to a remote server to check for software upgrades, processes license information, and updates a database with available upgrades.
- 静态失败原因: Static BERT models often rely on surface-level syntactic patterns and may be misled by the common boilerplate of opening a URL, reading lines, and using loops. The high overlap in token sequences like 'new URL', 'openConnection', 'BufferedReader', 'readLine' contributed to false positive prediction.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically requires functional similarity beyond shared API usage. Here the functions serve entirely different business purposes (link extraction vs. software upgrade check), so BCB correctly labels them as non-clones despite similar networking boilerplate.
- 共享行为: Both open a URL connection and read from an InputStream using BufferedReader.；Both perform string manipulation on the read content.；Both use a loop to read lines from the input stream.
- 行为差异: Function A extracts links and texts from HTML using regex; Function B parses XML-like server responses and updates a database.；Function A returns two Vectors; Function B is void and performs UI updates and database operations.；Function A is a one-time scraping task; Function B involves license validation and upgrade logic.；Function A uses the RE library for pattern matching; Function B uses string splitting and conditionals.
- 修正建议: Incorporate data-flow analysis to distinguish different data transformations.；Use method name or broader context (e.g., return type, called methods) to disambiguate purpose.；Add attention to semantic roles of variables (e.g., link vs. license).

### case_id=1717 FP boilerplate_overlap

- 方法: `createOutputStream` vs `readData`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Creates a BufferedWriter that re-packages a ZIP file, skipping 'content.xml' initially and then adding it as the last entry with UTF-8 encoding.
- B 摘要: Reads configuration data from static strings, tokenizes them to populate various sets and a lookup table, and also reads a file to populate a hash map.
- 静态失败原因: The model likely overfit on superficial similarities such as both methods containing loops, file handling imports, and try-catch blocks, despite very low token overlap. The truncation in function B may have misled the model into seeing a similar code structure.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would not consider these clones because the functions serve entirely different purposes (stream creation vs. data parsing) and share no meaningful functional overlap.
- 共享行为: Both involve file I/O operations (reading/writing).；Both use loops to process data.
- 行为差异: Function A is about ZIP file manipulation; function B is about parsing configuration and populating data structures.；Function A uses ZipInputStream/OutputStream; function B uses StringTokenizer and BufferedReader.；Function A returns a BufferedWriter; function B is void and modifies static fields.；Function A processes only one file; function B reads a file line by line and also parses multiple token lists.
- 修正建议: Improve training data to include more negative examples with low token overlap but similar structural patterns.；Enhance the model's ability to recognize high-level functional intent beyond surface API usage.；Use data flow analysis to distinguish between different data processing patterns.

### case_id=1718 FN benchmark_preference_bias

- 方法: `getEncoding` vs `callApiPost`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Extracts character encoding from HTTP response headers or content.
- B 摘要: Makes an HTTP POST request with parameters and returns an InputStream.
- 静态失败原因: The model correctly rejected strict semantic equivalence based on low token overlap and differing method names, but it missed the broad structural similarity that BCB considered.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled as clone due to surface-level similarities in using HttpURLConnection, handling headers, and stream operations, despite entirely different core functionality.
- 共享行为: Open URL connections；Handle HTTP headers；Perform I/O operations
- 行为差异: A only reads and extracts encoding without sending data; B writes POST data and reads response.；A returns a String; B returns an InputStream.；A handles 'Content-Type' and 'charset' detection; B sends parameters and handles errors.；A uses BufferedReader; B uses PrintStream and BufferedOutputStream.
- 修正建议: Incorporate structural similarity metrics beyond token overlap.；Use data augmentation to include examples with low token overlap but similar high-level patterns.；Train with BCB-style annotations that allow partial functionality clones.

### case_id=1719 FN partial_functionality

- 方法: `main` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a URL and extracts its entries to the current directory.
- B 摘要: Copies a file from source to destination using buffered streams.
- 静态失败原因: Static BERT models rely heavily on token overlap and shallow syntactic patterns; the low token Jaccard (0.189) and different method names, structures, and comments led to false negative. The model missed the semantic similarity in the I/O pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this as a clone due to similarity in the core I/O loop (reading from an input stream and writing to an output stream with buffering), which is considered a Type-4 (semantic) clone despite different high-level functionality.
- 共享行为: Reads bytes from an input stream and writes them to an output stream using buffered streams；Uses BufferedInputStream and BufferedOutputStream with similar buffer sizes；Handles file I/O operations
- 行为差异: Function A downloads from a remote URL and processes a ZIP file; Function B copies a local file；Function A extracts multiple entries from a ZIP; Function B copies a single file；Function A is a main method with hardcoded URL; Function B is a reusable method with parameters
- 修正建议: Use a model that captures functional semantics, e.g., via data flow graphs or program dependence graphs；Incorporate byte-level I/O pattern detection as a feature；Train on more diverse semantic clones with low syntactic overlap

### case_id=1720 FP partial_functionality

- 方法: `getPagina` vs `loadURL`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches the content of a URL and returns it as a string, catching exceptions.
- B 摘要: Downloads a URL's content to a temporary file with optional basic authentication and UI progress updates, throwing IOException.
- 静态失败原因: Static models like BERT/GraphCodeBERT may over-rely on lexical and API-level overlap (URL, BufferedReader, InputStreamReader, readLine loop) and miss the overall functional context and differences in side effects and output. The high lexical similarity in the core reading pattern might cause a false positive.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely labels this as non-clone because the functions have different return types, different error handling strategies, different inputs, and B has substantial additional functionality (authentication, file writing, UI update) that goes beyond simple code similarity.
- 共享行为: Both open a URL connection and read lines via BufferedReader；Both use InputStreamReader；Both read line by line until null
- 行为差异: A returns the accumulated content as a string; B writes content to a file and updates a UI label；A catches and returns exceptions as a string; B throws IOException；B supports HTTP basic authentication; A does not；B has additional side effects: creating a temp file, printing to console, refreshing UI
- 修正建议: Incorporate data flow analysis to track how the read content is used (returned vs written to file)；Consider return type and exception handling as part of semantics；Add contrastive training examples that differ in output usage but share IO patterns；Use code summarization to capture high-level intent

### case_id=1721 FP lexical_or_api_overlap

- 方法: `main` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a fixed URL and prints each line to standard output.
- B 摘要: Performs a Google image search, parses HTML for image URLs, populates a list, and sets a UI icon.
- 静态失败原因: The model likely overfitted on the common pattern of URL opening and line reading, ignoring the divergent data usage and overall goal.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this non-clone because the functions have entirely different purposes and outputs; only superficial API usage is similar.
- 共享行为: Both open a URL connection and read lines using BufferedReader and InputStreamReader.
- 行为差异: Code A prints lines to console; Code B concatenates lines and parses HTML.；Code A uses a fixed URL; Code B constructs a dynamic search query.；Code B modifies global state (googleImages list, UI components) and handles exceptions with dialogs.；Code B has additional UI-related functionality (setting an icon).
- 修正建议: Incorporate data flow analysis to track how the read data is used.；Use method name and overall context to disambiguate purposes.；Increase weight on identifier semantics (e.g., 'googleImages', 'MusicBoxView' vs. 'System.out').

### case_id=1722 FN partial_functionality

- 方法: `copyResource` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource from a URL or local file to a destination file using byte-by-byte streams.
- B 摘要: Copies a file to another file using NIO FileChannel transferTo with synchronization.
- 静态失败原因: Static models like GraphCodeBERT rely on token and structural similarity, which is low (Jaccard=0.125). They may not capture the high-level semantic equivalence due to different API usage and control flow. The model might have learned to distinguish based on APIs rather than intent.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: None
- 共享行为: Both copy content from a source to a destination file
- 行为差异: Source types: A supports URL and File; B only File；Copy method: A uses byte-by-byte InputStream/OutputStream; B uses FileChannel.transferTo；Error handling: A throws Exception; B returns boolean and swallows IOExceptions；Resource management: A closes in main flow; B closes in finally with nested try-catch
- 修正建议: Train with more Type-3 and Type-4 clone examples that have different implementations but same intent；Use code summarization or docstring matching to capture functional similarity；Incorporate data-flow analysis to highlight that both perform file copy operations

### case_id=1723 FN boilerplate_overlap

- 方法: `importRoles` vs `File2String`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.6`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads roles from a URL by parsing XML-like lines and collecting RoleName objects.
- B 摘要: Reads a file or classpath resource and returns its entire content as a single string.
- 静态失败原因: Static BERT/GraphCodeBERT likely focused on semantic differences (e.g., return type, parsing logic) and low token overlap (Jaccard=0.28), missing the shared boilerplate pattern that BCB annotators considered sufficient for a clone label.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may consider this a Type-3 clone due to high structural similarity in the I/O loop and buffer usage, despite different domain-specific logic and return types.
- 共享行为: Both use BufferedReader and InputStreamReader to read lines from an input stream.；Both accumulate lines in a StringBuffer.；Both handle IOException with try-catch blocks.；Both have a while loop reading lines until null.
- 行为差异: Input source: URL vs file/classpath.；Purpose: Parse XML tags to collect RoleName objects versus concatenate all lines into one string.；Error handling: Silent catches vs printing error and calling System.exit().；Return type: ArrayList<RoleName> vs String.
- 修正建议: Enhance model with structural similarity features (e.g., AST subtree matching).；Incorporate dataflow analysis to capture common I/O patterns.；Use contrastive learning to distinguish between functional and boilerplate clones.

### case_id=1724 FN partial_functionality

- 方法: `updateFile` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Copies a file from a source to a destination using file channels, creating parent directories if needed.
- B 摘要: Launches a NexOpen project configuration, including copying a template resource file to a project location after placeholder replacement.
- 静态失败原因: Static BERT/GraphCodeBERT likely failed due to low token overlap (0.06), different method names, and large structural differences; the shared sub-task of file copying is not captured by surface-level features.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider this a Type-4 semantic clone because both functions perform a file copy operation, albeit with different implementations and contexts.
- 共享行为: Both involve copying or creating a file with content from another source.
- 行为差异: updateFile copies any file directly using FileChannel; launch copies a specific resource file after string manipulation and uses IOUtils and ByteArray streams.；launch performs many other tasks like XML processing, setting properties, and scheduling jobs, whereas updateFile is solely a file copy.
- 修正建议: Train on finer-grained semantic similarity that recognizes partial functionality overlap, e.g., by decomposing functions into subtasks and comparing subtask embeddings.

### case_id=1725 FP lexical_or_api_overlap

- 方法: `init` vs `loadURL`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Load controller classes from a registry file using class loader.
- B 摘要: Download a URL to a temporary file with optional authentication and progress display.
- 静态失败原因: Static BERT likely overemphasized the overlapping API calls (BufferedReader, InputStreamReader, readLine loop) and failed to capture the high-level semantic purpose due to limited context awareness.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clone because the functionality is entirely different despite sharing low-level I/O boilerplate; they are not even partial functionality clones.
- 共享行为: Both read lines from an input stream using BufferedReader and InputStreamReader in a loop.
- 行为差异: Different input sources: classpath resource vs URL.；Different output: adds classes to a list vs writes file content.；Error handling: A catches exceptions, B throws IOException.；B includes authentication and progress UI update.
- 修正建议: Incorporate control flow and data dependency analysis to distinguish purpose.；Use models that consider method-level semantics beyond token overlap.；Add explicit feature for task type (e.g., class loading vs. file download).

### case_id=1726 FN partial_functionality

- 方法: `getEncoding` vs `getNetworkServersIPs`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Extracts the character encoding from an HTTP response by checking headers and content for charset/encoding declarations.
- B 摘要: Parses a text file from a URL to retrieve a list of server IPs by looking for lines starting with '!SERVERS' and then extracting colon-separated values.
- 静态失败原因: Static BERT/GraphCodeBERT models rely heavily on token patterns and syntactic overlap. The low token Jaccard (0.294) and different method names (getEncoding vs getNetworkServersIPs) and distinct variable names and patterns likely caused the model to miss the underlying functional similarity. The model may have been confused by the different keywords like 'charset' vs '!SERVERS'.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this pair as clone because both functions follow the same high-level algorithm of opening a URL, reading lines, and extracting specific information based on pattern matching, which constitutes a Type-4 (functionally similar) clone despite different details.
- 共享行为: Both open a URL and read lines from the input stream using BufferedReader.；Both iterate over lines to find specific patterns and extract data.；Both use URLConnection and handle IOException.
- 行为差异: Function A extracts encoding string; Function B extracts IP addresses.；Function A checks HTTP header fields first; Function B does not use headers.；Function A uses a default encoding if not found; Function B returns an empty vector.；Function A closes the reader in a finally block; Function B does not explicitly close.
- 修正建议: Improve model's ability to recognize similar algorithmic structures, e.g., by training on more diverse Type-4 clones.；Incorporate control flow graph similarities or data flow analysis.；Use contrastive learning with high-level functional annotations.

### case_id=1727 FP lexical_or_api_overlap

- 方法: `sendPost` vs `lookupFutureEvents`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Sends an HTTP POST request with parameters and returns the response body as a string.
- B 摘要: Fetches future events from the Meetup API via HTTP GET, parses JSON, and returns a list of Event objects.
- 静态失败原因: Static BERT/GraphCodeBERT likely over-relied on lexical and API overlap (URL, BufferedReader, InputStreamReader, readLine, StringBuilder) and missed the semantic divergence in HTTP method and data transformation.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB requires at least some functional similarity; here the common I/O boilerplate is insufficient given the completely different HTTP methods and output processing.
- 共享行为: Both functions connect to a URL over HTTP；Both read the response line by line and accumulate it into a buffer
- 行为差异: A uses POST with parameters; B uses GET without parameters；A returns raw string; B parses JSON and maps to domain objects；A handles exceptions with logging; B throws a custom exception；A uses HttpURLConnection with output; B uses URL.openStream() directly
- 修正建议: Train with negative examples that share API calls but differ in logic；Incorporate structural analysis like data flow and control flow；Use models sensitive to HTTP method and output type

### case_id=1728 FP lexical_or_api_overlap

- 方法: `readAndRewrite` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a DICOM file and rewrites it to another file using ImageIO and DcmParser.
- B 摘要: Handles GUI action events to set file paths and application preferences with JFileChooser and preference storage.
- 静态失败原因: Static BERT likely overemphasized the common API elements (FileInputStream, FileOutputStream, exception handling) and generic I/O patterns, failing to capture the domain-specific context and control flow differences.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would label this as non-clone because the functions have entirely different purposes and semantics, despite both performing I/O. BCB's annotation guidelines prioritize functional similarity over superficial API overlap.
- 共享行为: Both use file I/O operations and write output
- 行为差异: Function A processes medical image data; Function B updates GUI settings and preferences.；Function A is a straightforward utility; Function B is a complex event handler with multiple conditional branches.；Function A has no user interaction; Function B relies on user input through file choosers and UI components.
- 修正建议: Enhance model training with more diverse negative examples that share APIs but differ in semantics.；Incorporate structural features like control flow graphs to distinguish utility methods from event handlers.；Use larger context windows to capture method-level purpose and class relationships.

### case_id=1729 FP lexical_or_api_overlap

- 方法: `SRWGuiClient` vs `loadURL`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Constructor initializing a Swing browser GUI, loading an XML/HTML URL, optionally transforming it with XSLT, and displaying the result.
- B 摘要: Private method downloading a file from a URL with optional HTTP basic authentication, writing to a temporary file while updating a status label.
- 静态失败原因: Static BERT models may over-rely on token overlap (URL, BufferedReader, readLine, IOException) and miss the different semantic goals, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels as non-clone because the overall functionalities are distinct: a web browser constructor vs. a file downloader, despite both using URL reading.
- 共享行为: Both open a URL connection and read lines via BufferedReader；Both use readLine() in a while loop；Both handle IOException
- 行为差异: A is a constructor setting up a GUI; B is a utility method for file download；A may parse XML/XSLT; B writes to a file with progress display；A involves GUI components (JEditorPane, JScrollPane); B writes to a temp file；A requires transformer; B requires authentication
- 修正建议: Use graph-based or flow-aware models to capture data and control flow differences；Incorporate hierarchical context like method signatures and class-level info；Use code summarization to capture intent

### case_id=1730 FN benchmark_preference_bias

- 方法: `modifyApplicationMessage` vs `unzip`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Modifies a localized properties file by updating or adding a message key-value pair.
- B 摘要: Unzips a ZIP file to a specified directory, handling directory creation and file extraction.
- 静态失败原因: The model correctly predicted no clone (0), but the BCB label is 1; thus the model did not fail in terms of reasonable semantic understanding. The misclassification arises from a possibly erroneous BCB annotation rather than a model shortcoming.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have considered both as file manipulation utilities with loops over input streams, but the functionalities are entirely different and not semantically similar even under broad Type-3/Type-4 definitions.
- 共享行为: Both perform file I/O operations using streams and readers/writers
- 行为差异: modifyApplicationMessage reads/writes properties files with specific key-value replacement logic；unzip extracts multiple files from a zip archive, creating directories and handling binary streams
- 修正建议: Review BCB annotation for this pair to confirm if it was incorrectly labeled as clone；If BCB label is indeed a false positive, exclude this pair from evaluation

### case_id=1731 FN partial_functionality

- 方法: `copyResource` vs `moveFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource (URL or file) to a destination file using byte-by-byte streaming.
- B 摘要: Moves a file to a target location by copying it using a buffer and then deleting the original.
- 静态失败原因: The static BERT model may have been misled by low token overlap (0.3125), different method names, and structural differences like buffer usage vs byte-by-byte reading. The deletion step in moveFile may have also contributed to the false negative prediction.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considers these clones because the core copying functionality is present in both, and the additional delete in moveFile is seen as a minor extension. Both are private helper methods performing I/O tasks.
- 共享行为: Both open an InputStream from a source and an OutputStream to a target file；Both read data from input and write to output in a loop；Both close the streams after copying
- 行为差异: copyResource can read from a URL, moveFile only from a file；copyResource reads byte-by-byte, moveFile uses a buffer；moveFile deletes the original file after copying, copyResource does not；Exception handling differs: Exception vs IOException
- 修正建议: Enhance semantic understanding to recognize that the deletion in moveFile is an additional operation beyond the shared copy logic；Use data flow analysis to capture the common read-write-close pattern；Consider that BCB annotations sometimes accept partial functionality similarity as clones

### case_id=1732 FN benchmark_preference_bias

- 方法: `combineJs` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.2`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Downloads JavaScript files from URLs, optionally minifies them using JavaScriptCompressor, combines them into a single file, and updates a link element's src attribute.
- B 摘要: Configures and launches a NexOpen project by processing Maven pom.xml files, setting Hibernate dialect, possibly copying a reverse engineering file, and scheduling an install action.
- 静态失败原因: Static BERT likely correctly identified non-clone due to low token overlap and divergent semantic domains; it did not fail but the BCB label is likely erroneous.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled these as clones due to both containing boilerplate I/O and file operations, and possibly a mistaken notion of both being 'configuration' or 'processing' functions, but this is a very loose interpretation.
- 共享行为: Both use IOUtils.copy for stream copying；Both involve file creation and directory setup；Both have try-catch-finally error handling patterns
- 行为差异: combineJs operates on web resources (JS files) while launch deals with Eclipse project configuration；combineJs minifies and merges JS files; launch handles Maven pom and Hibernate settings；combineJs returns a modified HTML element; launch modifies project persistent properties
- 修正建议: Improve clone definition consistency in benchmarks to avoid labeling such dissimilar functions as clones；Ensure static models are not penalized for correct non-clone predictions when benchmarks are noisy

### case_id=1733 FN partial_functionality

- 方法: `doVersionCheck` vs `runInternal`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Checks for newer version of jEdit by reading a version file from a URL and comparing build numbers.
- B 摘要: Loads and parses an OPDS catalog from a URL, handling pagination and optionally downloading books, while providing progress feedback.
- 静态失败原因: Static BERT/GraphCodeBERT likely failed because the lexical overlap is low (token Jaccard 0.1165) and the syntactic structures differ (one is simple sequential, the other has complex loops). The models may not capture the high-level semantic pattern of URL I/O that the BCB annotators might have used.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB might consider these as Type-4 clones because both perform a network request and then process the response with user feedback, but the actual functionality and logic are entirely different. The annotators may have focused on the high-level pattern of open-URL-read-feedback.
- 共享行为: Both open a URL connection and read input；Both handle exceptions related to I/O；Both provide user feedback (wait cursor vs progress)
- 行为差异: doVersionCheck performs simple line-by-line parsing for version/build info; runInternal performs complex XML parsing and pagination；doVersionCheck has straightforward sequential flow; runInternal has a do-while loop for pagination；Error handling differs: doVersionCheck shows error dialog; runInternal calls onError and breaks；doVersionCheck only reads; runInternal may download books as well
- 修正建议: Improve representation of high-level I/O patterns；Incorporate control flow abstraction that captures purpose rather than just syntax；Use data flow analysis to identify shared operations like openStream/read/disconnect

### case_id=1734 FP lexical_or_api_overlap

- 方法: `sendPost` vs `retrieveTemplate`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Sends HTTP POST request with parameters and returns response body as string.
- B 摘要: Retrieves template from blog URL via HTTP GET and caches it, returning cached string.
- 静态失败原因: The static BERT/GraphCodeBERT model likely focused on common boilerplate (URL, BufferedReader, while loop reading lines, string append) and missed the critical difference in HTTP method and parameter handling due to surface-level API overlap.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels as non-clone when functions have different I/O patterns or algorithmic steps; here the HTTP method difference and caching are significant enough to consider them functionally distinct.
- 共享行为: Reads from a URL via HTTP；Reads line by line using BufferedReader；Accumulates lines into a string/ StringBuilder；Returns the accumulated string
- 行为差异: A uses POST with parameter, B uses GET without parameter；A does not cache, B caches the result；A handles exceptions by printing, B throws Exception；A sets HTTP headers and writes to output stream, B does not
- 修正建议: Incorporate structural information about method calls (POST vs GET) and output stream usage；Add attention to method signatures and I/O patterns；Include caching detection as a differentiating feature

### case_id=1735 FN benchmark_preference_bias

- 方法: `main` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: A main method that signs a PDF using iText, involving keystore, certificates, and signature appearances.
- B 摘要: A launch method that configures and runs a NexOpen project build, handling Maven POM files, Hibernate dialect, and reverse engineering files.
- 静态失败原因: Static BERT models rely on token and structural similarities; the extremely low token Jaccard (0.069) and different domain-specific APIs made it impossible to detect any conceptual overlap, leading to a false negative relative to BCB's lenient clone definition.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this pair as clone due to both being 'entry-point' methods that perform resource loading, configuration setup, and file I/O, despite differing domains, accepting broad Type-4 partial functionality.
- 行为差异: Different problem domains: PDF signing vs Eclipse/Hibernate project launch.；Different APIs and libraries used (iText vs Eclipse/Hibernate).；Different control flow and exception handling patterns.；One is a static main method, the other an instance method with parameters.
- 修正建议: If target is BCB-style, incorporate domain-agnostic structural patterns (e.g., 'load config -> process -> produce output') or use cross-project embeddings.；Use contrastive learning to recognize abstract functional similarity across domains.；Manually verify BCB annotations to avoid noisy labels.

### case_id=1736 FP lexical_or_api_overlap

- 方法: `readTwitterFead` vs `run`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a fixed Twitter JSON feed using HttpClient and returns the entire response content as a string.
- B 摘要: Reads a URL stored in a field using URL.openStream, parses lines into version, url, and additional info, sets error flags, and notifies listeners.
- 静态失败原因: The static BERT/GraphCodeBERT model likely overemphasized the lexical and API overlap (BufferedReader, InputStream, readLine) and the try-catch structure, causing a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the functions have different output behavior (one returns a string, the other sets fields and triggers actions) and process the input data differently, despite sharing the pattern of reading lines from a URL.
- 共享行为: Both read from an HTTP URL；Both iterate over lines using BufferedReader
- 行为差异: Function A returns a concatenated string of all lines; Function B extracts specific fields using a switch statement；Function A uses Apache HttpClient with HTTP GET; Function B uses URL.openStream；Function A logs errors to LogCat; Function B sets error flags and notifies listeners；Function A has a fixed URL; Function B uses a variable urlInfo
- 修正建议: Incorporate data-flow analysis to capture how the data is processed (e.g., string concatenation vs. parsing into fields)；Consider output/return types and state changes (e.g., listener notifications)；Use graph-based models that distinguish between different API usages

### case_id=1737 FN benchmark_preference_bias

- 方法: `doGet` vs `convert`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Handles HTTP GET request to retrieve and render a portal page with user permission checks and logging.
- B 摘要: Converts an ACRNEMA stream file to DICOM format by parsing and writing pixel data.
- 静态失败原因: Static BERT correctly predicted non-clone due to very low token overlap and distinct structural patterns; from BCB perspective it is a false negative, but our analysis suggests the model was correct.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have considered both as 'processing' functions with input/output, but the domains are entirely different; probable labeling error in the benchmark.
- 共享行为: Both perform file I/O operations (reading/writing streams)；Both use try-catch-finally for resource management
- 行为差异: Function A is a web servlet handling HTTP requests; Function B is a file format converter；A involves user authentication and page caching; B involves DICOM metadata and pixel data manipulation；A uses Servlet API and HTTP response; B uses file streams and DICOM libraries；A has logging and error handling specific to web portal; B has console output and format-specific checks
- 修正建议: Review BCB annotation for this pair; if label is incorrect, correct it；Consider removing or re-annotating the pair in the dataset

### case_id=1738 FP lexical_or_api_overlap

- 方法: `handleHandshake` vs `SRWGuiClient`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Handles Minecraft handshake by validating server key and initiating login or session join via HTTP.
- B 摘要: Constructs a Swing browser GUI that fetches and displays XML/HTML content from a URL with XSL transformation.
- 静态失败原因: The static model likely focused on the shared lexical elements (URL, BufferedReader, try-catch) and structural patterns, ignoring the overall semantic context and domain-specific differences.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would label this as non-clone because the functions are from completely different domains (Minecraft client vs. Swing browser) and perform entirely different tasks, despite sharing superficial code patterns like URL reading.
- 共享行为: Both use URL and BufferedReader to read data from a network source.；Both have try-catch blocks for exception handling.；Both involve conditional logic based on input content.
- 行为差异: Function A validates a handshake packet and sends login packets; Function B builds a GUI and renders web content.；Function A interacts with Minecraft network protocol; Function B is a standalone browser application.；Function A has a specific session authentication flow; Function B has XML parsing and XSL transformation.；Input and output types differ: A takes a Packet2Handshake and outputs network packets; B takes a URL string and outputs a GUI window.
- 修正建议: Incorporate function names and method signatures into the model input for better context.；Use data flow analysis to distinguish different usages of shared API calls.；Train on dataset with more diverse cross-domain examples to reduce API-overlap false positives.；Add attention to the overall control flow and purpose beyond local token matches.

### case_id=1739 FP boilerplate_overlap

- 方法: `googleImageSearch` vs `PhoneSetImpl`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Perform Google image search by constructing a URL, reading HTML, extracting image URLs, and updating GUI with album art.
- B 摘要: Constructor that reads phone set data from a URL, parses lines ignoring those starting with '***', and populates a map.
- 静态失败原因: Static BERT/GraphCodeBERT may have focused on the shared structural pattern of opening a URL, reading lines, and using BufferedReader, ignoring the higher-level semantic differences. It might also have been misled by the common method signature pattern (taking a URL, returning void, etc.)
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely annotated these as non-clones because the overall functionality and domain are entirely different; one is a GUI-driven image search utility, the other is a data parser for phone sets. Even though both read from a URL, the similarity is only in boilerplate I/O code, which BCB typically does not consider as a clone.
- 共享行为: Both open a URL and read lines via BufferedReader；Both parse the input line by line；Both close the reader after processing
- 行为差异: Function A performs HTTP connection with User-Agent header, Function B uses url.openStream()；Function A parses HTML to extract image URLs, Function B parses custom format (phoneset) to populate a map；Function A updates GUI components, Function B does not；Function A handles exceptions and shows error dialogs, Function B throws IOException
- 修正建议: Enhance model to consider the full method body beyond I/O patterns；Incorporate data flow analysis to distinguish different data processing pipelines；Improve tokenization or add attention to distinguish API usage context

### case_id=1740 FP boilerplate_overlap

- 方法: `downloadURLtoString` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Generic utility to download content from a URL and return as a string.
- B 摘要: Fetches Google image search results and extracts image URLs into a list, with UI error handling and conditional on artist change.
- 静态失败原因: The model likely over-relied on overlapping API tokens (BufferedReader, InputStreamReader, readLine, close) and the URL opening pattern, ignoring the significant differences in control flow, data processing, and purpose. The lexical overlap in the common boilerplate code misled the classifier.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically considers overall functional equivalence. These functions have different purposes (generic download vs. specific image search), different return types, and different control structures. The shared code is boilerplate for reading from a URL, which is a common pattern but does not make them clones.
- 共享行为: Open a URL connection using java.net.URL；Read from the input stream line by line using BufferedReader；Close the BufferedReader after reading
- 行为差异: Function A returns the entire content as a String; Function B extracts only image URLs and stores them in a list, returning void.；Function B has a conditional on artist change, constructs a query URL, sets User-Agent header, splits response, and handles exceptions with a dialog.；Function A uses URL.openStream() directly; Function B uses HttpURLConnection with additional headers.；Function A uses StringBuffer for efficiency; Function B uses string concatenation (less efficient).
- 修正建议: Enhance model to capture overall method purpose, not just token overlap.；Include data flow and control flow features to distinguish different post-processing steps.；Use a method-level embedding that captures return type, exception handling, and side effects.

### case_id=1741 FN benchmark_preference_bias

- 方法: `doExecute` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Handles an HTTP request to parse multipart form data, collect fields and file attachments, and send an email using a Mail object.
- B 摘要: Downloads a KMZ file from a hardcoded HTTP URL, opens a ZIP input stream, and extracts each entry to a local file.
- 静态失败原因: Static BERT models rely on lexical and structural similarities; these functions share very low token overlap (Jaccard ~0.07) and use completely different APIs and control flow, so the model correctly identified them as non-clones. The BCB label is questionable.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled as clone based on a broad interpretation of 'file I/O and stream processing' or 'handling attachments', but this seems too general; likely a labeling error.
- 共享行为: Both read from input streams and process items in a loop；Both handle exceptions (though error handling differs)
- 行为差异: A is a web controller method dealing with HTTP request/response and form validation; B is a standalone utility main method；A sends an email with attachments; B extracts files from a ZIP archive；A uses framework-specific classes (ActionMapping, ActionForm, ActionMessages); B uses standard Java I/O and networking classes；A has complex logic for multipart parsing and error reporting; B is straightforward decompression
- 修正建议: Re-evaluate BCB annotations for consistency; consider that these functions are not functionally similar；Improve model to capture high-level semantic similarity if such broad clones are desired, but that may be unrealistic for this pair

### case_id=1742 FN partial_functionality

- 方法: `copyResource` vs `setup`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a single resource from a URL or file to a destination file using byte-by-byte stream copy.
- B 摘要: Extracts native library files from a jar archive to a temporary directory and adds the library path based on system architecture.
- 静态失败原因: Static BERT/GraphCodeBERT methods rely heavily on token overlap and structural similarity; the low Jaccard similarity (0.158) and different control flows (one simple loop vs zip iteration with conditions) led to a non-clone prediction. The models failed to recognize the shallow stream-copy pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB annotators may have considered both functions as 'copying' resources because they both involve reading from a stream and writing to another, ignoring the broader context and purpose.
- 共享行为: Both perform file I/O operations using input and output streams.；Both read bytes from an input stream and write them to an output stream.
- 行为差异: copyResource copies exactly one resource; setup extracts multiple zip entries from a jar.；setup includes directory creation, buffer-based reading, and architecture detection; copyResource does not.；setup modifies system library path; copyResource does not.；Different error handling: copyResource throws generic Exception; setup throws from file operations.
- 修正建议: Incorporate program slicing to isolate core file copy behavior.；Use contrastive learning on pairs with partial functional overlap.；Enhance models with dataflow analysis to distinguish between single-file copy and multi-file extraction with additional operations.

### case_id=1743 FP lexical_or_api_overlap

- 方法: `perform` vs `generateDeviceUUID`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Handles HTTP request to classify a concept, involving session management, parameter extraction, XML serialization, HTTP POST, XML parsing, and result building.
- B 摘要: Generates a device UUID by computing MD5 hash of device type, internal ID, and host name, converting to uppercase hex string.
- 静态失败原因: The model likely over-emphasized common lexical patterns (e.g., StringBuffer, loops, exception handling) while missing the vast semantic difference.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB does not consider them clones because they have no functional overlap; one is a web action handler, the other is a UUID generator.
- 共享行为: Both use StringBuffer to build strings.；Both have exception handling with try-catch.
- 行为差异: Function A performs HTTP request handling and classification logic; Function B performs cryptographic hashing for UUID generation.；Function A has complex session and parameter management; Function B has no session or external communication.；Function A builds XML and communicates over network; Function B is purely local computation.
- 修正建议: Include more negative examples with similar boilerplate but different functionality.；Use dataflow or control-flow information to distinguish different computation goals.

### case_id=1744 FN partial_functionality

- 方法: `copyFile` vs `getFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a local file to another local file using NIO FileChannel transfer.
- B 摘要: Downloads a WSDL file from a URL, optionally modifies its endpoint, and saves it to a local file with logging and exception handling.
- 静态失败原因: Static BERT models rely heavily on token and syntactic similarity, but these functions have low Jaccard similarity (0.107), different method names, and vastly different lengths. The model likely missed the shared channel-based copying due to the overwhelming lexical differences.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may classify this as a Type-4 clone because both functions share the core file-copying behavior using NIO channels, even though getFile has additional functionality. BCB's annotation guidelines sometimes accept partial functionality similarity as clone.
- 共享行为: Uses FileChannel to transfer data from a source to a destination
- 行为差异: copyFile operates on local files only; getFile downloads from a remote URL；getFile includes XML parsing and manipulation, file renaming, and extensive error handling；copyFile is a simple utility function; getFile is a complex method with multiple side effects；Method names and overall purpose differ significantly
- 修正建议: Enhance model to identify sub-functional similarities via semantic parsing or program slicing；Incorporate knowledge of standard library APIs (e.g., FileChannel) to recognize common operations；Use contrastive learning to train on partial-functionality clones

### case_id=1745 FN benchmark_preference_bias

- 方法: `Converter` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Converts a file from SJIS encoding to UTF-8 encoding using buffered streams.
- B 摘要: Launches an Eclipse IDE launch configuration for a NexOpen project, processing Maven POM files and setting up Hibernate mapping.
- 静态失败原因: The static BERT method correctly predicted non-clone. However, if BCB considers this a clone, the model might have missed it due to the extreme lexical and structural differences (low token Jaccard) and lack of shared API usage. The model may rely on token or structural overlap, which is minimal here.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: The BCB annotation may be an error, as there is no clear similarity. Possibly due to both methods involving file input/output or streams, but that is too broad.
- 共享行为: None; the two functions perform completely different tasks.
- 行为差异: Function A is a simple file encoding converter; Function B is a complex Eclipse launch configuration method.；Function A uses FileInputStream/FileOutputStream and BufferedReader/BufferedWriter; Function B uses Eclipse APIs, IProject, IFile, Document, etc.；Function A handles a single pair of files; Function B handles multiple files, properties, and persistent project settings.；Function A has minimal error handling; Function B has extensive error handling with logging and rethrowing.
- 修正建议: Review BCB annotations for this pair to confirm if clone label is valid.；If BCB label is correct, improve model to recognize very broad Type-4 clones that share only abstract behavior like 'file processing'.

### case_id=1746 FN lexical_or_api_overlap

- 方法: `copyResource` vs `buildDeb`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource from a URL or local file to a destination file using a byte-by-byte read-write loop.
- B 摘要: Builds a Debian package by writing control and data files into an ar archive with headers and footers.
- 静态失败原因: Low token overlap (0.2059) and different domain-specific terms (URL, deb) caused the static model to focus on lexical differences rather than the shared stream-copying structure.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely considered the core byte-copying loop as semantically similar, classifying it as a Type-3 clone (near-miss) due to structural commonality despite different contexts.
- 共享行为: Both open input and output file streams.；Both copy bytes from input to output using a while loop.；Both close streams after copying.
- 行为差异: copyResource handles both URL and local file sources, while buildDeb only reads from local files.；buildDeb writes archive headers ('!<arch>\n', file entries) before and after data, whereas copyResource does not.；buildDeb copies multiple files (control and data), while copyResource copies a single resource.；copyResource reads byte by byte, whereas buildDeb reads in chunks of 1024 bytes.
- 修正建议: Incorporate control-flow or data-flow features to capture structural similarity.；Train on more examples of byte-copying patterns with varying domain terminology.；Use graph-based representations to factor out method names and highlight I/O structure.

### case_id=1747 FN benchmark_preference_bias

- 方法: `getResourceAsStream` vs `runDynusT`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.4`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Downloads a resource from a URL, caches it locally, and returns an InputStream.
- B 摘要: Copies executable and model files to a temporary directory, runs an external simulation program, and optionally cleans up.
- 静态失败原因: The static BERT model likely relied on lexical and structural overlap, which is very low, so it correctly predicted non-clone; the BCB label appears inconsistent with typical clone definitions.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have considered both as 'resource management' functions involving file operations and system interactions, leading to a lenient Type-4 annotation, but the semantic gap is large.
- 共享行为: Both perform file I/O operations；Both use loops and conditionals；Both have logging/printing statements
- 行为差异: Different overall purpose (resource retrieval vs simulation execution)；Different file operations (download and cache vs copy and delete)；Different control flow (try-catch vs throw exception)；Different data structures and external dependencies
- 修正建议: Improve understanding of semantic similarity beyond lexical overlap；Incorporate task-level semantics or higher-level abstractions；Re-evaluate BCB labels for consistency with strict clone definitions

### case_id=1748 FP boilerplate_overlap

- 方法: `handleHandshake` vs `load`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Handles handshake by validating username and optionally verifying session via HTTP request.
- B 摘要: Loads XML data from a pastebin URL and returns it as a string.
- 静态失败原因: Static BERT/GraphCodeBERT likely focused on the shared structural patterns (URL creation, BufferedReader, try-catch) and overlooked the semantic differences in the surrounding logic and different use of the data.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled non-clone because the functions have different inputs, outputs, and overall intent despite sharing a similar I/O pattern.
- 共享行为: Create URL and open connection；Read from BufferedReader line by line；Handle IOException/Exception
- 行为差异: Different purposes: login handshake vs XML download；Different validation logic；Different output: sends packets vs returns string；Different error handling: disconnect vs dialog
- 修正建议: Incorporate more context about method signatures and return types；Use dataflow analysis to track how the read data is used；Train on more diverse clones to avoid overweighing common I/O patterns

### case_id=1749 FP partial_functionality

- 方法: `executeHttpGet` vs `downloadModel`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Executes an HTTP GET request and parses the response as JSON.
- B 摘要: Downloads an RDF model from a URL using HTTP or other protocols.
- 静态失败原因: Static BERT/GraphCodeBERT might have focused on the lexical overlap of HTTP GET, reading streams, and similar code structure (try-catch, reading lines/streams) and missed the difference in return types and data processing. The token Jaccard is low but the model might have captured functional similarity from the sequence of API calls.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely labeled as non-clone because the functions have different return types and process different data formats (JSON vs RDF), even though they share the HTTP GET pattern. BCB prefers Type-3/Type-4 but still requires the core functionality to be similar.
- 共享行为: Both perform an HTTP GET request to retrieve data from a URL.
- 行为差异: executeHttpGet returns a JSONObject after parsing JSON; downloadModel returns an RDF Model.；executeHttpGet uses HttpClient; downloadModel uses URLConnection.；downloadModel sets custom request properties; executeHttpGet does not.；downloadModel handles specific exceptions and wraps them in RuntimeException; executeHttpGet throws Exception.
- 修正建议: Incorporate return type information into the model.；Train on examples that differentiate between different data format processing.；Use data flow analysis to capture the transformation of the response.

### case_id=1750 FP lexical_or_api_overlap

- 方法: `getVersion` vs `doVersionCheck`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches version string from a hardcoded URL and returns it, returning null on exception.
- B 摘要: Fetches version and build info from a configurable URL, compares build numbers, and displays UI dialogs for update availability or errors.
- 静态失败原因: Static BERT may over-rely on lexical and API-level similarities (URL, BufferedReader, while loop, exception handling) and miss semantic differences like data usage, side effects, and control flow.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels these as non-clones because the functions have fundamentally different purposes: one is a simple getter, the other is a complex UI-driven version check. The differences in inputs, outputs, side effects, and control flow are significant.
- 共享行为: Both retrieve version information from a remote URL using HTTP；Both use BufferedReader to read lines from the stream
- 行为差异: A returns a string; B performs UI interactions and shows messages；A uses a hardcoded URL; B uses a configurable property；A reads all lines and returns the last; B parses lines for specific prefixes；A has no side effects; B shows/hides wait cursor, displays dialogs
- 修正建议: Incorporate dataflow analysis to track variable usage and output transformations；Consider side effects and input/output differences more explicitly；Use fine-grained statement alignment to compare logic beyond API calls

### case_id=1751 FN benchmark_preference_bias

- 方法: `doGet` vs `uploadFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Handles HTTP GET request to serve a portal page, with authentication, logging, caching, and error handling.
- B 摘要: Uploads a file to a target location by renaming or copying the input file.
- 静态失败原因: Static BERT/GraphCodeBERT likely correctly predicted non-clone because the token Jaccard is very low (0.092) and the semantic contexts are dissimilar; the failure is actually a BCB labeling noise rather than a model error.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled them as clones due to superficial overlap in file I/O operations (FileInputStream, FileOutputStream, renameTo) and perhaps the presence of file paths, but the overall functionality and context are entirely different.
- 共享行为: Both involve file system operations (caching page output vs. uploading file)；Both use file I/O streams
- 行为差异: Function A is a web servlet handler with complex control flow and multiple conditions; B is a simple file utility；A manipulates HTTP request/response objects; B has no web context；A deals with user permissions and page visibility; B has no authentication logic；A includes logging, caching, and statistics; B only prints to stdout
- 修正建议: Re-examine the BCB annotation for this pair; likely mislabeled as clone；Improve benchmark consistency by removing overly broad Type-4 pairs with minimal shared behavior

### case_id=1752 FN partial_functionality

- 方法: `sendExceptionToServer` vs `run`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.4`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends exception details to a server via HTTP POST and reads the response.
- B 摘要: Reads a configuration URL, parses lines into fields, and notifies listeners upon completion.
- 静态失败原因: Low token Jaccard similarity (0.17) and different method names; static models likely focused on lexical differences and missed the structural overlap of network I/O.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled as clone due to both performing network I/O (URL connection, reading lines) and exception handling, seeing them as similar boilerplate patterns despite different intents.
- 共享行为: Both use URL and BufferedReader to read lines from a network stream；Both handle IOException in a try-catch block
- 行为差异: A sends a POST request with constructed data; B only reads a GET response；A parses response lines with a while loop; B uses a switch-case on line index；A outputs to console; B stores data in fields and notifies listeners via finally block
- 修正建议: Incorporate control-flow and data-flow features to abstract patterns like network communication；Use models that capture structural schemas (e.g., GraphCodeBERT) to recognize common idioms

### case_id=1753 FN partial_functionality

- 方法: `main` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a URL or local file, opens it as a zip archive, and extracts each entry to a file.
- B 摘要: Copies a file from one location to another using FileChannel.transferTo.
- 静态失败原因: The model likely focused on token-level and structural differences (low Jaccard similarity, different method names, different APIs) and missed the high-level semantic similarity of performing file I/O operations.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as file I/O operations that copy data from an input source to output files, falling under a broad 'file copy' category (Type-4 or partial functionality).
- 共享行为: Both read from a source and write to a destination；Both involve file output operations；Both use FileInputStream and/or FileOutputStream
- 行为差异: A reads from a zip archive and extracts multiple files; B copies a single file as-is；A handles HTTP URLs; B only local files；A uses ZipInputStream and BufferedOutputStream; B uses FileChannel；A extracts multiple entries; B copies entire file
- 修正建议: Enhance model to recognize abstract I/O patterns across different APIs；Incorporate code summarization or natural language descriptions of functionality；Use contrastive learning with broader semantic clone examples

### case_id=1754 FP other

- 方法: `unzipModel` vs `main`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Unzips a given ZIP file into a temporary directory.
- B 摘要: Parses a Prolog file, generates adapter classes, and packages them into a JAR file.
- 静态失败原因: The static BERT model likely overemphasized superficial similarities like the presence of try-catch blocks, file streams, and loop structures, ignoring the stark difference in overall purpose.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB would not label these as clones because they have no shared functionality, no similar control flow, and the only commonality is that both involve file I/O, which is too generic.
- 行为差异: Function A is a simple file decompression utility; Function B is a complex code generation and packaging tool.；Function A reads a ZIP file and writes extracted entries; Function B reads a Prolog source, parses it, generates bytecode, and creates a JAR.；Function A has no conditional logic beyond file I/O; Function B has extensive command-line argument parsing and multiple processing steps.
- 修正建议: Improve the model's ability to capture high-level program semantics beyond local syntax.；Incorporate data flow and control flow analysis to distinguish between I/O utilities and complex application logic.

### case_id=1755 FP lexical_or_api_overlap

- 方法: `PhoneSetImpl` vs `checkForUpgrade`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: A constructor that reads a URL, parses each line (skipping those starting with '***'), and populates a phone set map.
- B 摘要: A static method that checks for software upgrade by querying a database and a remote server, then updates UI visibility and database records accordingly.
- 静态失败原因: Static BERT may have over-weighted the shared use of BufferedReader, InputStreamReader, and URL/URLConnection, which are common boilerplate patterns. The model likely focused on lexical/API overlaps and missed the vast differences in overall logic and purpose.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labeled this as non-clone because the methods have entirely different purposes: one is a constructor for data parsing, the other is a business-logic upgrade checker. Even under broad Type-3/4 similarity, they share no meaningful functional overlap beyond basic I/O patterns.
- 共享行为: Both use BufferedReader and InputStreamReader to read from a URL/URLConnection
- 行为差异: Function A is a simple constructor for parsing a phone set file; Function B is a complex upgrade procedure involving database queries, network communication, UI updates, and business logic；Function A has no database or UI interactions; Function B heavily uses database commands and UI components；Function A's output is a populated HashMap; Function B's output is UI state changes and database updates
- 修正建议: Improve training to prioritize structural and semantic alignment over lexical API co-occurrence；Incorporate data flow and call graph features to distinguish simple I/O from complex business logic；Add negative examples with similar boilerplate but different business intent to increase discrimination

### case_id=1756 FN partial_functionality

- 方法: `makeBackup` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.2`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: makes a backup of files from source to destination directory, setting last modified timestamps.
- B 摘要: launches a NexOpen project by processing Maven pom files and configuring Hibernate reverse engineering.
- 静态失败原因: low token overlap (0.058), different vocabulary and domain, model likely captured no significant semantic similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled as clone due to partial functionality overlap (both involve file I/O operations, though in very different contexts) or due to annotation error.
- 共享行为: both involve file operations (reading/writing files) and use streams
- 行为差异: different overall purpose (backup vs project launch)；different domains (simple file copy vs Eclipse plugin launch)；different complexity and dependencies
- 修正建议: improve handling of long-range semantic dependencies；use code structure or AST-based features to capture common patterns

### case_id=1757 FP boilerplate_overlap

- 方法: `main` vs `readData`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Compresses a specified file using GZIPOutputStream.
- B 摘要: Reads and parses configuration data to initialize character sets and lookup tables for Tibetan transliteration.
- 静态失败原因: Static BERT/GraphCodeBERT likely overemphasized lexical overlaps (e.g., IOException, System.out.println, try-catch, while loops) and boilerplate code, while missing the overall semantic difference due to limited context understanding.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels as non-clone because the two functions have completely different purposes and implementations, even though they share some boilerplate patterns like file I/O and error handling.
- 共享行为: Both involve file I/O operations.；Both use try-catch blocks for IOException handling.；Both use while loops for reading/processing data.
- 行为差异: Function A compresses a file; Function B parses tokenized string constants and file data for mapping characters.；Function A is a main method with command-line argument handling; Function B is a private helper method with no arguments.；Function B uses multiple HashSets and HashMaps for data storage; Function A uses byte buffers and streams.；Function B has extensive logic for handling multiple data columns and error cases; Function A has simple compression logic.
- 修正建议: Incorporate dataflow analysis to differentiate distinct operations.；Use more representative training data with varied functional intents.；Apply attention mechanisms that capture long-range dependencies and overall structure.

### case_id=1758 FN partial_functionality

- 方法: `main` vs `execute`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a URL, extracts its ZIP entries, and writes each entry to a file.
- B 摘要: Saves a HomeMap entity to a database, then copies an image file to a directory using IOUtils.copy, and returns a list.
- 静态失败原因: Static models rely on token matching and structural patterns; low Jaccard and different method signatures cause it to miss the underlying I/O similarity. The model may not generalize to different APIs and control flows.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB annotators may consider both as file I/O utilities with similar structural pattern of reading and writing streams, thus a Type-4 clone (functionally similar but not identical).
- 共享行为: Both involve reading from an InputStream and writing to an OutputStream.；Both perform file I/O operations.；Both handle IOException (though A throws, B catches).
- 行为差异: A involves HTTP download and ZIP extraction; B involves database persistence and simple file copy.；A uses buffered streams and byte arrays; B uses IOUtils.copy.；A writes multiple files; B writes one file.
- 修正建议: Improve model to recognize high-level I/O operations despite different libraries.；Use dataflow analysis to identify read-write patterns.；Augment training with functional similarity examples.

### case_id=1759 FP boilerplate_overlap

- 方法: `readIntoList` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads HTML from a URL, parses anchor tags to extract command names, and populates a map of JMenuItem objects.
- B 摘要: Performs a Google image search by constructing a URL, fetches the page, extracts image URLs, stores them, and displays the first image in a UI label.
- 静态失败原因: Static BERT models may overemphasize common API tokens (e.g., URL, BufferedReader) and structural patterns (try-catch, while loop), ignoring the distinct high-level purpose.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clone because the overall functionality and outputs are completely different; the shared URL reading and parsing boilerplate is insufficient for clone classification.
- 共享行为: Open a URL connection and read lines using BufferedReader；Parse HTML content using string operations；Handle exceptions with try-catch blocks
- 行为差异: Method A builds a menu from extracted links; Method B searches and displays images；Method A populates a map; Method B updates a global list and UI component；Method B includes additional HTTP header and UI update after parsing
- 修正建议: Enhance training with more functional intent or data-flow features；Use contrastive learning to distinguish boilerplate from core logic；Incorporate more context about variable usage and final output

### case_id=1760 FN benchmark_preference_bias

- 方法: `modifyApplicationMessage` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Modifies a specific message in a localized properties file by reading, editing, and writing properties files.
- B 摘要: Builds a site for editing by transforming XML files with XSLT, processing pages, and writing output files.
- 静态失败原因: Static BERT/GraphCodeBERT correctly identified the lack of semantic and structural similarity, so it did not fail; the error is in the BCB label, which is likely a misannotation.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled these as clones under a very broad type-4 interpretation of 'file modification functionality', but this seems inconsistent with typical BCB annotation standards which require more substantial similarity.
- 共享行为: Both read from files and write to files；Both handle exceptions with try-catch；Both use string manipulation and file I/O
- 行为差异: A performs simple property modification; B performs complex multi-step site generation with DOM and XSLT；A deals with a single properties file; B processes multiple pages and files；A uses Properties and BufferedReader; B uses Transformer, FileSystem, and Gadgets
- 修正建议: Re-evaluate BCB annotations for pairs with very low token overlap；Establish clearer guidelines for type-4 clone identification to avoid overly broad categorizations；Consider using automated metrics like token Jaccard to flag potential misannotations

### case_id=1761 FN benchmark_preference_bias

- 方法: `copyResource` vs `testStandardTee`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.6`
- 推荐路线: `preference_memory_with_manual_audit`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Copies a resource from a URL or file to a destination file using a manual byte-by-byte read-write loop.
- B 摘要: Tests the TeeWriter by copying a string from a StringReader to two StringWriters using Apache Commons IOUtils.copy and verifying results.
- 静态失败原因: Low lexical overlap and structural differences (test vs utility) misled the model; it lacks high-level task understanding.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB likely considers any function that performs a 'copy' operation as a clone, regardless of implementation details or context.
- 共享行为: Both involve reading from a source and writing to a sink
- 行为差异: Different source types (URL/file vs StringReader)；Different sink types (FileOutputStream vs two StringWriters)；One is a utility method, the other is a test with assertions；One uses manual byte loop, the other uses a library method
- 修正建议: Incorporate program analysis to detect abstract data flow patterns；Add training examples of broadly similar tasks with different implementations

### case_id=1762 FN benchmark_preference_bias

- 方法: `persist` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Persists a FreeFormConfigurable's InputStream to a file at a given relative path, throwing ConfigurationException on failure.
- B 摘要: Launches a build process for a NexOpen project by handling Maven POM files and configuring Hibernate properties, with various file operations and exception handling.
- 静态失败原因: The static model correctly predicted non-clone due to very low token overlap (0.063) and different AST structures. However, it failed to align with the BCB label, which likely adopted a more lenient semantic similarity criterion. The model's reliance on syntactic features caused it to miss this possible semantic clone.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as a clone if they considered both methods as 'file-based configuration management' or if they grouped methods that involve copying streams to files, despite the significant differences in context and purpose. Possibly a labeling error or a broad Type-4 annotation.
- 共享行为: Both perform file I/O operations (reading/writing).；Both can result in exceptions when I/O fails.
- 行为差异: Code_a writes a single input stream to a file; Code_b reads multiple XML files, creates files, sets properties, and schedules a job.；Code_a deals with FreeFormConfigurable; Code_b deals with ILaunchConfiguration and project resources.；Code_a throws ConfigurationException; Code_b throws CoreException and IllegalStateException.；Code_b has complex logic involving Maven profiles and Hibernate dialect configuration.
- 修正建议: Re-evaluate BCB annotation for this pair; maybe it is a false positive.；Incorporate semantic similarity models that capture broader functionality beyond exact API usage.；Add context-aware features that understand method purpose from method name and surrounding code.

### case_id=1763 FN partial_functionality

- 方法: `getFile` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies the soap address endpoint attribute, and saves the file to a temporary directory.
- B 摘要: Copies a source file to a destination file using file channels.
- 静态失败原因: Static models like GraphCodeBERT may fail due to low token overlap (0.154) and focus on method names and high-level purpose, missing the structural commonality of the file copy sub-task.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider this a clone because they share a core file copying operation (Type-4 partial functionality similarity), and the additional XML processing in A is seen as a modification to the same basic copy task.
- 共享行为: Both use FileChannel.transferFrom to copy bytes from input to output；Both involve file creation and stream closing in finally blocks
- 行为差异: A performs network download, XML parsing, and attribute modification; B only copies an existing local file；A returns a String file path; B returns void；A handles multiple exception types (MalformedURLException, IOException, ParserConfigurationException, SAXException); B handles only IOException
- 修正建议: Use models that capture both high-level semantics and low-level structural patterns；Incorporate data flow analysis to detect shared sub-tasks like file copying；Train on clone pairs with partial functionality overlap (Type-4) to improve recall

### case_id=1764 FN partial_functionality

- 方法: `copyResource` vs `createSettingsIfNecessary`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource from a URL or file path to a destination file using a byte-by-byte loop.
- B 摘要: Conditionally creates a settings file if it doesn't exist, copying from a bundled resource using IOUtils.copy.
- 静态失败原因: The model focused on different method names, conditional logic, and error handling tokens, missing the underlying stream copying pattern. Low token Jaccard and structural differences misled it.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely sees both as 'copy input stream to output stream' operations, considering the core data copying pattern as functionally similar despite differences in control flow and error handling.
- 共享行为: Both open an input stream and write its content to a file output stream.
- 行为差异: A always copies unconditionally; B only copies if the file does not exist.；A uses a simple byte-reading loop; B uses IOUtils.copy (buffered).；A throws Exception on missing resource; B uses FileLocator.openStream which may throw IOException.；A's destination is dynamic; B's destination is fixed to a settings file.
- 修正建议: Incorporate data flow analysis to identify stream copying patterns.；Use graph-based models that capture control and data dependencies.；Augment training data with more Type-3/Type-4 examples emphasizing shared core functionality.

### case_id=1765 FN benchmark_preference_bias

- 方法: `setContenu` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Sets content of an electronic file by copying input stream to output stream and updating metadata like name, MIME type, size, and last modification date.
- B 摘要: Launches a NexOpen project by validating configuration, processing pom.xml files, setting Hibernate dialect properties, and scheduling install actions.
- 静态失败原因: Static BERT/GraphCodeBERT likely correctly predicted non-clone due to low token overlap (Jaccard 0.073), different method names, and distinct code structures, indicating no semantic similarity.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have considered these clones due to both involving I/O operations, stream copying via IOUtils.copy, and setting properties on objects, but the overall functionality is completely different, so this label seems too broad.
- 行为差异: Different domain: file management vs. Eclipse plugin launch configuration；Different input/output: A operates on file streams and metadata; B manipulates project files and XML documents；Different control flow: A has conditionals based on file extension; B has conditionals based on project type and dialect；Different exception handling: A throws IOException and DocumentVideException; B throws CoreException and RuntimeException
- 修正建议: Re-evaluate BCB annotation for this pair to confirm if it is truly a clone or an annotation error；Use dataset filtering to remove pairs with very low token similarity and no clear semantic overlap

### case_id=1766 FN benchmark_preference_bias

- 方法: `copyFile` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Copy a file or directory recursively to a destination.
- B 摘要: Build an editable version of a website by transforming XML files and writing output files.
- 静态失败原因: Low token overlap (Jaccard 0.072) and extremely different structures and lengths, making it hard for a static model to capture any underlying similarity.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might have considered both as involving file copying at a high level, or due to a broad Type-4 interpretation where any file I/O utility could be considered a clone. However, the functionality is quite different, so this label is questionable.
- 共享行为: Both perform file I/O operations using streams.；Both read from a source and write to a destination.
- 行为差异: copyFile is a simple recursive file/directory copier; buildSiteForEdit is a complex site generation process with XML transformation and multiple file operations.；copyFile handles only files and directories; buildSiteForEdit handles XML, HTML, and properties files with transformation and string manipulation.；copyFile has no dependencies on external libraries; buildSiteForEdit uses DOM, XSLT, FTP, etc.
- 修正建议: Improve training data with more precise clone labels to avoid overly broad Type-4 annotations.；Use dynamic analysis or graph-based models that capture data flow and API usage patterns.

### case_id=1767 FP boilerplate_overlap

- 方法: `readTwitterFead` vs `readScalarpvviewerDocument`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Downloads Twitter timeline JSON from a fixed URL and returns the raw string content.
- B 摘要: Reads an XML configuration file from a given URL, parses it, and sets up multiple UI components and data structures.
- 静态失败原因: The model likely overemphasized common boilerplate patterns (BufferedReader, readLine, try-catch) and superficial structural similarity, while missing the drastically different data processing logic, return types, and side effects.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would label as non-clone because the functions have fundamentally different purposes (simple feed download vs. complex XML configuration and UI setup) and no significant functional overlap.
- 共享行为: Both read lines from an HTTP URL using BufferedReader.
- 行为差异: A returns a String; B is void and updates UI state.；A uses HttpClient and HttpGet; B uses URL.openStream().；A handles JSON (unparsed) on a fixed URL; B handles XML with custom line filtering and extensive attribute extraction.；A's error handling logs and prints stack traces; B's error handling sets a text message and stops.
- 修正建议: Incorporate data flow and control flow analysis to distinguish simple I/O from complex parsing.；Add training examples that emphasize functional purpose over syntactic patterns.；Use model architectures that capture long-range dependencies and external API usage context.

### case_id=1768 FN partial_functionality

- 方法: `serialize` vs `copyResource`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Serializes a content package to an output stream via a temporary file using a parser.
- B 摘要: Copies a resource from a URL or file to a destination file.
- 静态失败原因: Low token Jaccard similarity (0.1636), different method names, and dissimilar surface syntax caused the static model to focus on lexical differences rather than the underlying shared copy pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considers the core I/O copy operation as the primary functional similarity, overlooking the higher-level serialization context and treating them as broad Type-3 or Type-4 clones.
- 共享行为: Both copy bytes from an input stream to an output stream.
- 行为差异: Function A involves a multi-step serialization process using a parser and temporary file before copying; Function B directly opens a resource and copies to a file.；Function A deletes an existing temporary file on disk; Function B writes to a specific destination file.；Error handling differs: A throws IOException and BadIMSCPException; B throws a generic Exception.；Context: A is part of a larger package management system; B is a private utility method.
- 修正建议: Use data-flow-aware representations to capture I/O operations.；Include control-flow and byte-level copying patterns in training.；Apply contrastive learning on pairs with low lexical but high functional similarity.

### case_id=1769 FP boilerplate_overlap

- 方法: `run` vs `SRWGuiClient`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches and parses URL content into metadata fields, with error handling and listener notification.
- B 摘要: Constructs a GUI browser window, reads and transforms XML from a URL, and displays the result as HTML.
- 静态失败原因: The model likely overemphasized the common I/O pattern (URL, BufferedReader, readLine, IOException) and ignored the structural and contextual differences, treating it as boilerplate overlap.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would not consider these clones because their overall functionality and purpose are completely different; the shared I/O code is incidental and not indicative of semantic equivalence.
- 共享行为: Both open a URL and read lines using BufferedReader；Both handle IOException
- 行为差异: Function A stores parsed data into fields; Function B builds a GUI and displays HTML；Function A uses a switch to parse lines; Function B processes XML and XSLT；Function A notifies listeners after completion; Function B sets up a visible window；Function A has no GUI elements; Function B is a constructor for a Swing application
- 修正建议: Include structural features like method signatures and class context；Use contrastive training to distinguish common I/O patterns from true semantic clones；Incorporate data flow analysis to trace how inputs are used and outputs are produced

### case_id=1770 FP lexical_or_api_overlap

- 方法: `handler` vs `getRequestContent`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a URL, iterates over lines, for each line extracts a substring between delimiters and updates a map entry.
- B 摘要: Opens a URL, reads the first line, and returns it as a string.
- 静态失败原因: The model likely overemphasized the common API calls (URL, BufferedReader, InputStreamReader) leading to a false positive, while ignoring the drastically different control flow and data manipulation.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the overall behavior and output are fundamentally different despite some shared API usage. The functions serve distinct purposes (data extraction vs. simple retrieval).
- 共享行为: Both create a URL from a string.；Both open a connection and read input lines using BufferedReader.
- 行为差异: Function A iterates over all lines, processes each line to extract substrings and modifies a map; Function B reads only the first line and returns it.；Function A uses URL.openStream() while Function B uses HttpURLConnection.；Function A catches exceptions silently; Function B throws Exception.
- 修正建议: Incorporate data flow analysis to track variable usage and transformations.；Increase sensitivity to control flow patterns such as loops and conditional branches.；Use program slicing to compare the essential behaviors.

### case_id=1771 FN partial_functionality

- 方法: `doGet` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.2`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Handles HTTP GET request to retrieve a page, check visibility, render it with caching, and handle errors.
- B 摘要: Builds a site for editing by iterating over pages, transforming XML, and writing output files with file I/O and debugging.
- 静态失败原因: Low token overlap and distinct structural patterns caused the static BERT model to miss any abstract similarity in page handling behavior.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider them clones due to both involving page processing and output, even though the context and implementation differ significantly.
- 共享行为: Both process Page objects and check user visibility or permissions；Both involve logging for debugging；Both output content (HTTP response vs file output)
- 行为差异: Function A is a web request handler using HttpServletRequest/Response; Function B is a file-based batch builder；Function A has single page focus with dynamic rendering; Function B iterates over multiple pages for static file generation；Different input parameters and error handling mechanisms
- 修正建议: Improve model's ability to capture conceptual similarity beyond surface tokens by training on cross-context clone pairs.；Incorporate structural information like AST or control-flow graphs.

### case_id=1772 FN partial_functionality

- 方法: `copyFile` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Copies a file using FileChannel transfer.
- B 摘要: Builds a site for editing by processing multiple files, XML transformation, and writing output.
- 静态失败原因: Static models like GraphCodeBERT rely heavily on token similarity and structural patterns; the low token overlap and different control flow structures make it see them as different. Additionally, the long and complex nature of buildSiteForEdit may overshadow the file I/O commonality.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have considered these as Type-4 clones because both involve reading from a source and writing to a destination using file channels/streams, despite vast differences in complexity and purpose.
- 共享行为: Both perform file I/O operations (read/write files)；Both use FileInputStream to read files；Both handle exceptions and logging (though buildSiteForEdit does not show logging in snippet but has DebugFile)
- 行为差异: copyFile is a simple, single-purpose utility function; buildSiteForEdit is a complex multi-step process involving XML transformation and string manipulation；copyFile copies entire file at once; buildSiteForEdit reads and writes parts and processes content；copyFile returns boolean success; buildSiteForEdit throws exceptions and does not return a value；buildSiteForEdit has extensive state and loops; copyFile is linear
- 修正建议: Improve model ability to recognize partial functional overlap despite low token similarity；Incorporate functional semantics through dataflow or API usage patterns

### case_id=1773 FP lexical_or_api_overlap

- 方法: `actionPerformed` vs `readAndRewrite`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Handles user menu actions to set application preferences for various tools like Graphviz and ImageMagick.
- B 摘要: Reads a DICOM image file and rewrites it to another file using pixel data reading and writing.
- 静态失败原因: The model likely overemphasized superficial commonalities like File and String usage, or was misled by the presence of boilerplate constructs (if-statements, try-catch) despite minimal token overlap.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels these as non-clones because they perform entirely different functions with no shared purpose or logic.
- 行为差异: A is a GUI event handler for preference settings, while B is a static file conversion method.；A interacts with Swing components and application preferences, B deals with DICOM data and image I/O.；A has multiple conditional branches for different commands, B has a sequential pipeline for reading and writing.；A uses JFileChooser for file selection, B uses ImageInputStream and ImageOutputStream.
- 修正建议: Incorporate deeper semantic analysis using data flow or control flow graphs.；Use contrastive learning to better distinguish between unrelated API usage patterns.；Increase training data diversity to reduce sensitivity to common keywords.

### case_id=1774 FP lexical_or_api_overlap

- 方法: `get` vs `getVersion`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches game records from a URL based on latitude, longitude, and count, parses each non-comment line into GameRecord objects, and returns an array.
- B 摘要: Fetches a version string from a fixed URL by reading the last line of the response.
- 静态失败原因: Static BERT/GraphCodeBERT models may over-rely on surface-level patterns (e.g., HTTP connection, BufferedReader, while loop) and miss the semantic differences in purpose and data types, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB annotators likely considered these non-clones because they implement different functions: one retrieves game records with geographic parameters, the other retrieves a version string from a fixed URL, despite sharing the common HTTP GET pattern.
- 共享行为: Both perform an HTTP GET request；Both read the response line by line using BufferedReader；Both return null on failure
- 行为差异: A takes parameters (url, lat, lon, count) while B has no parameters；A uses specific headers for location and query count, B does not；A returns an array of GameRecord, B returns a single String；A filters out lines starting with '#', B does not filter
- 修正建议: Train model on more diverse negative examples that share boilerplate but differ in functionality；Incorporate type information and method signatures；Use dataflow analysis to distinguish different API configurations

### case_id=1775 FN partial_functionality

- 方法: `main` vs `readReferenceText`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Main method that sets up and sends a POST request to the RenRen API with hardcoded parameters, then prints the response line by line.
- B 摘要: Reads and returns the content of a file from a bundle resource URL, handling various IO exceptions.
- 静态失败原因: Static BERT/GraphCodeBERT likely failed due to low token overlap (0.111) and different method signatures, method names, and overall logic (one is a main method with HTTP POST, the other a utility for reading files). The model may not capture the similar substructure of URL reading because it is overwhelmed by the surrounding divergent code.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this as a clone because both functions involve opening a URL, reading lines via BufferedReader, and processing IO in a loop, which is a common pattern (Type-3 or Type-4 clone). The annotation often accepts partial functionality similarity even if the overall purpose differs.
- 共享行为: Both open a URL connection or stream；Both read content line by line using BufferedReader；Both handle IOException
- 行为差异: A sends an HTTP POST request with parameters; B reads a local resource file；A prints response to console; B returns the content as a string；A has hardcoded API details; B uses a dynamic identifier to construct the filename；A has no exception throwing; B throws NoContentException on failure
- 修正建议: Improve model to recognize common sub-patterns like 'URL->BufferedReader->readLine' despite different contexts；Incorporate data flow analysis to track similarities in I/O operations；Use subgraph matching or pattern-based features to detect partial functionality clones

### case_id=1776 FN benchmark_preference_bias

- 方法: `byReference` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.4`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Converts an InputStream to a DigitalObjectContent by copying it to a temporary file and returning an ImmutableContent wrapping that file.
- B 摘要: Retrieves a resource from a URL, caches it locally if not already cached, and returns an InputStream of the cached file; includes HTTP headers and conditional caching.
- 静态失败原因: Static BERT/GraphCodeBERT models rely on token overlap and syntactic structure, which are low (Jaccard 0.108). They fail to recognize the superficial structural similarity of 'create file, copy stream, close' because the overall contexts differ significantly. The model likely correctly identifies they are not semantically equivalent but misses the broad Type-4 similarity BCB accepts.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may label this as a clone because both functions involve reading from an InputStream and writing to a file, which is a common pattern (Type-4 semantic similarity). The annotation likely considers the high-level goal of 'write stream to file' as similar, ignoring differences in source, caching, and return type.
- 共享行为: Both create a new file and write data from an InputStream to it；Both handle IOException by printing stack trace；Both close output streams after writing
- 行为差异: Function A always creates a temporary file and copies entire stream; Function B has caching logic, checks cache, and may return cached InputStream without copying；Function A returns a DigitalObjectContent object; Function B returns an InputStream；Function B handles HTTP connections and URL parsing; Function A does not；Function B prints status messages; Function A does not
- 修正建议: Train or fine-tune models on BCB-style annotations that accept partial/Type-4 clones；Incorporate semantic role labeling to capture shared patterns like 'InputStream to file copy'

### case_id=1777 FP lexical_or_api_overlap

- 方法: `uploadFile` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Uploads a file to a target path, using rename or copy if rename fails.
- B 摘要: Handles GUI action events to set preferences for external tools and update UI components.
- 静态失败原因: The model likely overemphasized shared keywords like 'File', 'filename', and 'getAbsolutePath' in both functions, leading to a false positive despite different contexts.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clone because the functions have no semantic overlap: one is a utility for file upload, the other is an action listener for settings configuration.
- 行为差异: Function A performs file I/O only; function B is an event handler managing UI state.；Function A has no GUI interaction; function B heavily depends on Swing components.；Function A uses streams for copying; function B does not perform file copy operations.
- 修正建议: Incorporate control flow and data dependency analysis to distinguish file I/O from UI event handling.；Use graph-based representations that capture the structure of user interaction vs. file manipulation.；Improve training data to include more diverse non-clone pairs with API overlap.

### case_id=1778 FP lexical_or_api_overlap

- 方法: `readData` vs `convert`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Parses comma-separated string fields into sets and maps, initializing static data structures for Tibetan transliteration.
- B 摘要: Converts an ACRNEMA stream file to DICOM format, handling pixel data and UIDs.
- 静态失败原因: The model might have been misled by common tokens like 'HashSet', 'StringTokenizer', 'while', 'try', 'IOException' appearing in both, but the overall logic is distinct. Static models may over-rely on overlapping API calls or control flow keywords.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: None
- 共享行为: Both involve reading/processing input data
- 行为差异: A uses StringTokenizers to populate HashSets and a HashMap; B reads binary files and writes DICOM；A has no I/O parameters; B takes File src and dest；A is for initialization; B is for file format conversion；A is Tibetan transliteration; B is medical image conversion
- 修正建议: Improve model's understanding of overall program semantics beyond surface tokens；Use data flow or control flow graphs to capture deeper structure；Add negative mining for contrasting pairs with lexical overlap but different semantics

### case_id=1779 FP partial_functionality

- 方法: `postRequest` vs `getFullScreenUrl`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends an HTTP POST request with form parameters and returns the response body as a string.
- B 摘要: Extracts the full screen video URL from a YouTube page by parsing the HTML response.
- 静态失败原因: The static model likely focused on surface-level similarities such as URLConnection usage, BufferedReader, and try-catch structure, missing the fundamental difference in overall functionality.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB typically expects non-clones when the functions have different overall purposes despite sharing some common HTTP operations.
- 共享行为: Both open a URL connection with doOutput set to true；Both read the input stream line by line；Both handle exceptions with print statements
- 行为差异: Function A is a generic POST request while B is a specific YouTube URL extraction；A sends data (POST) whereas B does not send data (only reads)；B includes UI progress updates and debug prints；B parses specific HTML content to extract parameters
- 修正建议: Train on more diverse examples to distinguish generic HTTP utilities from specific application logic；Incorporate semantic understanding of input/output roles and data processing beyond token matching

### case_id=1780 FP partial_functionality

- 方法: `actionPerformed` vs `parseContent`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Handles GUI events to open file choosers for GRAPHVIZ/IMAGEMAGICK and update various preferences and UI components.
- B 摘要: Parses HTML content from a stream, extracting charset, metadata, language, and links, and stores parsed fields.
- 静态失败原因: The model likely focused on the superficial similarity of storing key-value pairs (putPref vs addField) and common control structures, ignoring the entirely different contexts and purposes.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB typically labels non-clones when functions have different overall purposes and operate in different domains, despite sharing some generic patterns like null checks or property storage.
- 共享行为: Both involve checking for null values and conditionally setting configuration or fields.
- 行为差异: Function A handles user-triggered GUI events and updates UI components; function B processes HTML content programmatically.；Function A sets application preferences via kontroller.putPref; function B adds parsed fields via addField.；Function A involves JFileChooser and dialogs; function B involves stream I/O and HTML parsing.；Function A is an action listener; function B is a content parser overriding a method.
- 修正建议: Add training examples that emphasize domain-specific functionality over generic property-setting patterns.；Use contrastive learning to distinguish between similar-looking operations in different contexts.；Incorporate broader context or method signatures to infer overall purpose.

### case_id=1781 FN partial_functionality

- 方法: `main` vs `run`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.75`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends a POST request with predefined parameters to RenRen API and prints the response.
- B 摘要: Sends a GET request with Basic Authentication and stores the response.
- 静态失败原因: Static BERT/GraphCodeBERT likely failed due to low token overlap and different method names, focusing on lexical similarity rather than high-level behavioral abstraction.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label as Type-4 clone because both functions perform HTTP request-response operations, a common pattern. The low lexical overlap is overlooked in favor of conceptual similarity.
- 共享行为: Both open an HTTP connection, send request, read response line by line.
- 行为差异: A uses POST with many parameters; B uses GET with Basic Auth.；A prints response to console; B stores response in variable and sets finish flag.；A is a main method; B is a run method in a thread.；A uses specific RenRen API constants; B uses generic fields for URL and credentials.
- 修正建议: Improve model's ability to abstract common patterns such as HTTP communication.；Incorporate control-flow or data-flow features to recognize similar I/O operations.；Use contrastive learning on pairs with low lexical but high behavioral similarity.

### case_id=1782 FP boilerplate_overlap

- 方法: `createFile` vs `readData`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Copies content from a source file to a resource managed by a file resource manager.
- B 摘要: Initializes multiple sets and maps by tokenizing string constants and parsing a data file to populate lookup tables for linguistic processing.
- 静态失败原因: The static BERT model likely overemphasized superficial similarities like try-catch patterns and I/O related keywords (e.g., IOException, FileInputStream) while ignoring the overall logic and data flow differences. The low token Jaccard indicates little lexical overlap, so the model might have been misled by the structural pattern of exception handling.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled non-clone because the functions have completely different purposes and logic; no functional similarity.
- 共享行为: Both have a try-catch block for exception handling.
- 行为差异: A performs file copy; B performs data parsing and initialization.；A uses IOUtils.copy; B uses StringTokenizer and manual parsing.；A has single exception handling; B has multiple error conditions and complex data structures.
- 修正建议: Include dataflow analysis to capture the actual operations.；Increase weight on semantic similarity rather than lexical or structural patterns.；Use code summarization to capture high-level intent.

### case_id=1783 FP lexical_or_api_overlap

- 方法: `lookupFutureEvents` vs `loadURL`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches events from Meetup API and parses JSON into a list of Event objects.
- B 摘要: Downloads a file from a URL with optional basic authentication and writes it to a temporary file while updating a UI label with progress.
- 静态失败原因: The functions share boilerplate code for URL opening and reading, leading the model to overestimate similarity despite completely different processing logic and output types.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels based on functional category; A is event retrieval/parsing, B is file download with UI, which are distinct categories.
- 共享行为: Both open an HTTP connection and read line by line using BufferedReader/InputStreamReader
- 行为差异: A parses JSON into Event objects; B writes raw response to a temporary file；B handles basic authentication; A does not；B updates a UI label; A does not；A returns a List<Event>; B is void and has side effect of file creation
- 修正建议: Incorporate features like return type, side effects, and downstream processing into the model；Augment training data with non-clone pairs that share URL reading boilerplate

### case_id=1784 FN partial_functionality

- 方法: `addIDs` vs `run`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches metabolite data from a remote database given a name, parses the HTML response to extract identifiers and metadata, and stores them into a PeakListRow object.
- B 摘要: Opens a connection to a local URL and reads all lines of the response, discarding them, with no side effects.
- 静态失败原因: Static BERT/GraphCodeBERT methods may rely heavily on token-level similarity and structural features. The token Jaccard is low, and the large number of unique tokens in function_a (like GCGCColumnName, metaboliteID, etc.) are absent in function_b, leading to low similarity scores. The model correctly identified them as different under strict semantics, but failed to recognize the broad clone label according to BCB because it doesn't account for very partial functionality overlap.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: Since BCB labeled this as a clone, they may have considered the common pattern of opening a URL and reading lines as sufficient for Type-3 similarity, ignoring the significant differences in data processing and return values. Alternatively, the truncated part of function_a may contain similar code to function_b, but based on the visible portions, the functional overlap is minimal.
- 共享行为: Both open a URL and read lines using BufferedReader.；Both use try-catch for IOException.
- 行为差异: Function_a extracts and processes specific data (metabolite IDs, molecular weight, synonyms) and stores them in a row object, while Function_b discards all data.；Function_a returns an integer score, Function_b returns void.；Function_a has complex parsing logic for HTML, Function_b has no processing.；Function_a connects to an external database, Function_b connects to a local server.
- 修正建议: Improve the model to capture high-level semantic similarity even when token overlap is low, perhaps by focusing on the intent of network I/O operations.；Enhance the representation to be more tolerant to size differences and missing details.；Use dataflow or control flow analysis to identify similar patterns (e.g., both have a while loop reading lines from a URL).；Include more context about the purpose of the functions, such as method names and surrounding code.

### case_id=1785 FN lexical_or_api_overlap

- 方法: `File2String` vs `CheckUrl`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.3`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a file from either file system or classpath and returns its entire content as a string.
- B 摘要: Reads the first line from an HTTP URL and returns it as a string.
- 静态失败原因: The low token Jaccard (0.18) and distinct API calls (FileInputStream vs HttpURLConnection) likely dominated the model's attention, obscuring the shared high-level pattern of reading text via stream.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may consider both as 'reading from a source and returning a string', treating them as semantically similar (Type-4) despite different sources and amounts of data.
- 共享行为: Both open an input stream and wrap it in a BufferedReader and InputStreamReader.；Both read text from the stream and return a string.
- 行为差异: A reads from a file or classpath resource; B reads from an HTTP URL.；A returns the entire file content; B returns only the first line.；A prints debug information and exits on failure; B prints exception stack trace and returns empty string.
- 修正建议: Incorporate dataflow analysis to recognize both functions as 'read from input stream'.；Use abstract representations like 'resource access' to detect partial functionality clones.

### case_id=1786 FN partial_functionality

- 方法: `read` vs `getEncoding`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a skeleton file from classpath, splits it into sections at lines starting with '---', and validates the number of sections.
- B 摘要: Determines the character encoding of a URL resource by inspecting HTTP headers and then scanning the content for charset/encoding declarations.
- 静态失败原因: Static BERT models likely focused on the different keywords and logic (e.g., '---' vs 'charset'), missing the broad commonality of 'read and parse lines' that BCB might value.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have considered both functions as Type-4 clones because they both involve reading input line by line and performing pattern-based extraction, which can be seen as a high-level semantic similarity despite different specific purposes.
- 共享行为: Both read from a stream by lines using BufferedReader.
- 行为差异: A reads from a local classpath resource; B reads from a URL.；A splits sections based on a delimiter; B looks for charset/encoding keywords.；A throws exceptions on missing file or wrong section count; B returns a default encoding if not found.；A takes a filename as input; B uses a stored URL object.
- 修正建议: Train models with more focus on high-level intent rather than exact lexical/syntactic patterns.；Incorporate program analysis or data-flow information to infer abstract behavior.

### case_id=1787 FP partial_functionality

- 方法: `GetResponse` vs `downloadFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads HTTP response from a URL and returns the content as a string.
- B 摘要: Downloads a file from a URL to a local destination with progress tracking.
- 静态失败原因: Static BERT/GraphCodeBERT may have focused on the overlap of API calls like openConnection, getInputStream, and BufferedReader/BufferedInputStream, and missed the overall difference in functionality. The token Jaccard is low (0.162), but model may have been misled by the common pattern of reading from a URL.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely labeled non-clone because the functions have different purposes: one retrieves a response string, the other downloads a file with progress. They are not semantically equivalent even under a broad definition.
- 共享行为: Both open a URL connection and read from its input stream.
- 行为差异: Return type: String vs boolean.；Output: returns content as string vs writes to file.；Progress tracking: only B has it.；Error handling: A catches exceptions, B throws.
- 修正建议: Improve model to capture high-level intent using dataflow analysis or sequence of API calls and their output usage.；Incorporate control flow and data flow to distinguish between string accumulation vs file writing.

### case_id=1788 FN benchmark_preference_bias

- 方法: `run` vs `login`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Reads a resource file from classpath and sets it as text on a GUI component.
- B 摘要: Performs HTTP login to a remote service and returns a session ID.
- 静态失败原因: Static model correctly identified non-clone; BCB label is likely a false positive due to superficial API overlap.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may label as clone due to shared boilerplate I/O pattern (URL.openStream/openConnection, BufferedReader, try-catch) and similar structural skeleton.
- 共享行为: Both use Java I/O classes (BufferedReader, InputStreamReader, URL)；Both catch exceptions with generic Exception handling
- 行为差异: A reads a local resource; B makes an HTTP POST to a remote server；A updates a GUI component; B returns a string；A builds a string from file content; B extracts session ID from response；A uses SwingUtilities.invokeLater; B does not
- 修正建议: Discourage matching on common I/O boilerplate code without semantic alignment；Use program dependence graphs to capture data flow and intent

### case_id=1789 FN partial_functionality

- 方法: `setContenu` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sets content of a file in a document management system, copying input stream to output stream and updating metadata.
- B 摘要: Downloads a KMZ file from a URL, unzips it, and extracts entries to local files.
- 静态失败原因: Static BERT models like GraphCodeBERT focus on code structure and data flow. The functions have very different method signatures, control flow, and domain-specific API calls, so the model correctly identifies them as different. However, BCB's broad labeling includes partial semantic overlap in stream copying.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this as clone because both functions fundamentally copy data from an input stream to an output stream. Under broad Type-4/partial functionality criteria, sharing the stream copying pattern and I/O handling might be considered similar enough.
- 共享行为: Both use InputStream and OutputStream for data transfer.；Both handle I/O operations and stream closing.
- 行为差异: Function A is part of a larger document workflow, checking for duplicate files, handling email metadata, while Function B is a simple extraction of a single ZIP from URL.；Function A manipulates file metadata (name, MIME type, size, dates), while Function B just writes extracted files.；Function A has complex conditional logic for duplicate detection and email handling; Function B has none.；Function B unzips a single archive; Function A copies a single file stream.
- 修正建议: Train with more diverse examples of stream copying clones to recognize broad functional similarity.；Incorporate weak labeling or data augmentation to capture partial functionality.

### case_id=1790 FN benchmark_preference_bias

- 方法: `readData` vs `httpRequestByPOST`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.1`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Parses static string tokens to populate multiple sets and maps for Tibetan transliteration data.
- B 摘要: Makes an HTTP POST request and returns the response body as a string.
- 静态失败原因: Static BERT models rely on token overlap and semantic embedding similarity; these functions have negligible lexical overlap and entirely different domains, so the model correctly predicted non-clone, but BCB label is likely a misannotation.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider both as 'reading data' functions despite different sources, but this is extremely broad and unlikely to be a typical clone.
- 共享行为: Both iterate over input data (StringTokenizer vs readLine) and build data structures (sets/maps vs StringBuffer).
- 行为差异: Function A is private void, no parameters, no return value, modifies global state.；Function B is public String, takes parameters, returns response string or null, handles HTTP errors.
- 修正建议: Review BCB annotation for this pair; likely a labeling error.；If BCB intends such broad clones, the model would need to capture higher-level functional categories beyond token-level similarity.

### case_id=1791 FN partial_functionality

- 方法: `testNetworkHTTP` vs `fetchUrl`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: A test method that makes multiple HTTP GET requests to different URLs and reads the response streams without using the content.
- B 摘要: A utility method that fetches the content of a given URL by reading its response stream into a string.
- 静态失败原因: The lexical overlap is low (0.258), and the functions differ in structure (void vs return, multiple vs single URL, unused variable vs string building). Static models like GraphCodeBERT may focus on local patterns and miss the shared HTTP reading pattern, but also the high-level semantic difference might cause false negative.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: Although they share low-level HTTP reading patterns, the overall functionality differs significantly – one is a test with side effects, the other is a reusable data retrieval function – so BCB likely would not consider them clones under their typical annotations, but the dataset label may have been influenced by broad API similarity.
- 共享行为: Both establish HTTP connections and read the response via BufferedReader over InputStreamReader.
- 行为差异: A ignores the response content; B returns it as a string.；A handles multiple URLs; B handles a single parameterized URL.；A is void; B returns String.；A catches only IOException; B also catches MalformedURLException.
- 修正建议: Use data-flow-aware models that capture the common pattern of opening an HTTP connection and reading stream.；Incorporate API-level semantics or usage patterns.；Train with more negative examples of similar but non-clone pairs.

### case_id=1792 FN partial_functionality

- 方法: `copyResource` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource from a URL or file path to a file by reading byte by byte.
- B 摘要: Copies a file to another file using NIO FileChannel transferTo.
- 静态失败原因: The model likely relied on lexical overlap (low token Jaccard of 0.2) and different API usage (InputStream vs FileChannel) and control structures, missing the semantic similarity of the copying behavior.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely labels this as a clone because both functions have the same high-level purpose (copying data to a file) and the differences are in implementation details, which is typical for Type-4 clones in BigCloneBench.
- 共享行为: Both copy data from a source to a destination file.；Both close streams/channels after copying.
- 行为差异: A supports URL sources; B only files.；A uses byte-by-byte stream I/O; B uses NIO channel transferTo.；A throws Exception; B throws IOException and handles FileNotFoundException.；A writes to a method-defined destination; B takes dest as parameter.
- 修正建议: Include more diverse copying examples in training data.；Use graph-based models that capture data flow (e.g., source read to destination write).；Incorporate AST structural matching to recognize similar high-level patterns.

### case_id=1793 FN partial_functionality

- 方法: `decodeFileToFile` vs `doGet`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Decodes a Base64 encoded input file and writes the decoded bytes to an output file, returning success status.
- B 摘要: Handles a GET request to display a portal page, including page lookup, access control, rendering, and optional caching to a file.
- 静态失败原因: The static BERT/GraphCodeBERT method relied on token-level similarity and structural overlap, which is very low (Jaccard 0.083), causing it to correctly predict non-clone under strict semantic equivalence; however, it failed to recognize the broad behavioral pattern that BCB considers.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider these clones because both implement a broad 'read-transform-write' pattern with similar stream handling, buffering, and error management, despite different application domains.
- 共享行为: Both involve reading data from an input source and writing to an output destination；Both use try-catch-finally for I/O and resource cleanup
- 行为差异: Function A is a simple file-to-file Base64 decoder；Function B is a complex web request handler with page retrieval, user authentication, logging, statistics, and conditional caching
- 修正建议: Include features capturing higher-level I/O patterns like 'read from source, write to sink'；Train on a dataset with broader clone definitions；Incorporate functional similarity beyond token overlap

### case_id=1794 FN partial_functionality

- 方法: `fileDownload` vs `sendRequestObjectResponse`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a file from a given URL and saves it as 'download.pdf' in a specified directory without returning anything.
- B 摘要: Sends an XML request to a servlet, receives a response, determines its content type, saves it to a timestamped file in a specific directory, displays the file in a browser, and returns its path.
- 静态失败原因: The functions have low token overlap (0.14), different method signatures, variable names, and control flow structures; static models often miss the deeper semantic similarity of the core download routine due to reliance on surface-level features.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this as a clone because both functions perform a core file download from a URL using similar I/O patterns, and the additional features in B are seen as extensions of the same underlying download functionality.
- 共享行为: Both open a URL connection to a remote resource；Both read from an input stream using a while loop with (c = read()) != -1；Both write the read data to a FileOutputStream；Both use try-catch for exception handling
- 行为差异: B sends an XML request via an OutputStream, while A only downloads；B handles different content types and renames files accordingly, A uses a fixed name 'download.pdf'；B includes additional steps like logging, compression, and showing a browser；B returns the file path, A returns void
- 修正建议: Enhance models with dataflow analysis to identify shared I/O patterns；Use statement-level matching to detect common subroutines despite structural differences；Incorporate long-range attention to capture similarities across the entire function

### case_id=1795 FN lexical_or_api_overlap

- 方法: `runScript` vs `readVersion`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.75`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a script file from a URL character by character and returns its content as a string, returning 'error!' on exception.
- B 摘要: Reads a version file from the classpath, parses lines to extract version, revision, and date fields, and sets corresponding member variables.
- 静态失败原因: Static BERT models like GraphCodeBERT rely on token overlap and structural patterns; low token similarity (0.22) and different API usage (URL vs ClassLoader) likely caused misclassification.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may view both as type-3/4 clones due to similar high-level task of reading from a URL/resource and processing input, despite differences in input/output and parsing logic.
- 共享行为: Both open a URL or resource and read input stream.；Both read until end of input and handle exceptions.
- 行为差异: A takes scriptName argument; B has no parameters.；A returns concatenated data string; B populates class fields.；A reads bytes; B reads lines and parses key-value pairs.；A uses getCodeBase() for URL; B uses ClassLoader.getSystemResource.
- 修正建议: Enhance model with dataflow analysis to capture I/O patterns.；Train on more diverse examples of URL/resource reading operations.；Incorporate control flow and exception handling similarity.

### case_id=1796 FN partial_functionality

- 方法: `fileDownload` vs `retrieveQ`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads content from a URL and writes it to a hardcoded file name 'download.pdf' in a given directory, catching all exceptions.
- B 摘要: Retrieves content from a URL as a string by reading lines, and prints the HTTP response message to stderr, throwing exceptions.
- 静态失败原因: Static BERT/GraphCodeBERT may have been misled by low token Jaccard (0.2179), different method names and signatures, and divergent output handling. The model likely focused on lexical differences (e.g., file write vs. string return) rather than the shared high-level goal of URL content retrieval.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely labels as clone because both functions perform the core task of downloading data from a URL using Java's URLConnection and reading the response, despite differences in output format and error handling. The functional similarity (retrieving URL content) is high.
- 共享行为: Opens a URL connection and gets an InputStream；Wraps InputStream in InputStreamReader and BufferedReader；Reads data from the URL
- 行为差异: A writes to a file using FileOutputStream and BufferedWriter; B returns a String using StringBuilder；A reads byte by byte (read() returns int); B reads line by line (readLine())；A uses try-catch for all exceptions; B throws MalformedURLException and IOException；A uses a hardcoded filename 'download.pdf'; B returns the entire content
- 修正建议: Incorporate structural features like control flow or data flow graphs；Use API-based embedding to capture common URL connection patterns；Train with more examples of Type-4 clones to recognize partial functionality similarity

### case_id=1797 FN partial_functionality

- 方法: `getFile` vs `copyIconFiles`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a given URL, modifies an endpoint attribute in XML, and saves it to a temporary location.
- B 摘要: Copies icon files (16x16 and 32x32) from annotated paths to a destination directory using file channel transfer.
- 静态失败原因: Static BERT likely failed because of low token overlap (Jaccard 0.08) and different vocabulary, overlooking the deeper structural similarity in the file I/O pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled this as a clone due to the shared pattern of file copying via FileChannel.transferFrom, which is a distinctive structural similarity despite different high-level purposes.
- 共享行为: Both perform file I/O operations using FileChannel and stream APIs；Both conditionally copy files based on existence or annotation presence；Both open input and output streams, transfer data, and close resources
- 行为差异: Function A involves network download and XML parsing, while B only copies local files；Function A modifies XML content and handles multiple exceptions, B only prints stack trace；Function A uses a fixed content length, B uses src.size()；Different error propagation strategies (throws vs. printStackTrace)
- 修正建议: Incorporate data flow analysis to detect similar I/O patterns across different APIs；Use graph-based models that capture control and data dependencies；Augment training data with more type-4 clone examples showing structural similarity

### case_id=1798 FP lexical_or_api_overlap

- 方法: `getLinksFromURLFast` vs `handler`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a URL, extracts all hyperlink URLs and anchor texts using regex, returns two vectors.
- B 摘要: Reads a URL, searches lines for a specific include string, then extracts substrings between fromStr and toStr to update a map.
- 静态失败原因: The model likely over-relied on lexical and API overlap (URL, BufferedReader, regex) and missed the divergent semantics of the loops and output structures.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels non-clones due to distinct functional purposes; despite shared I/O patterns, the outputs and transformation logic differ significantly.
- 共享行为: Open a URL and read its content line by line using BufferedReader；Use regex patterns to extract substrings from the HTML content
- 行为差异: Function A extracts all links and texts from HTML anchor tags; Function B extracts specific substrings based on target patterns；Function A returns vectors of all links and texts; Function B updates a map entry with the extracted substring；Function A uses multiple regex patterns for URL manipulation; Function B uses fixed fromStr and toStr for extraction
- 修正建议: Incorporate dataflow or control-flow features to distinguish different processing logic；Use contrastive learning on pairs with similar I/O but different internal transformations；Improve handling of long-range dependencies in regex-based loops

### case_id=1799 FP lexical_or_api_overlap

- 方法: `PageLoader` vs `downloadFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads entire web page content into a string variable.
- B 摘要: Downloads a file from a URL to a local file with progress reporting.
- 静态失败原因: Static BERT models may over-rely on overlapping tokens (URL, Buffered, read, close) and control flow patterns, missing the crucial differences in return type, side effects, and output destinations.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels non-clones when functions have different overall functionality despite sharing some low-level API steps. Here, one loads a page into a string and the other downloads a file with progress, so BCB correctly annotates as non-clone.
- 共享行为: Both open a URL connection and read data from it.
- 行为差异: Function A reads text and concatenates lines into a string; Function B reads binary data and writes to a file.；Function B reports download progress via MessageFrame; Function A does not.；Function A is a constructor with no return value; Function B is a static method returning boolean.；Function A closes the reader; Function B closes both input and output streams.
- 修正建议: Include data augmentation with non-clone pairs that share API usage but differ in purpose.；Integrate feature extraction for return types and side-effect analysis.；Use graph-based models that capture data flow and output dependencies.

### case_id=1800 FN other

- 方法: `doGet` vs `internalCopy`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Handles HTTP GET request for a portal page, including parameter parsing, access control, logging, rendering, and caching.
- B 摘要: Copies a file from source to destination using buffered byte streams.
- 静态失败原因: The static model correctly identified no semantic similarity due to low token overlap and entirely different contexts; it did not fail but the BCB label is wrong.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB label appears erroneous; the two functions share no meaningful functional similarity. Possibly a labeling artifact or overly broad Type-4 criteria.
- 行为差异: Different purposes: HTTP request handling vs file copy.；Different inputs/outputs: HTTP request/response vs file streams.；Complex logic in A (page lookup, permissions, caching) vs simple I/O in B.
- 修正建议: Re-evaluate BCB label for this pair; consider removing from clone set.；If static model is expected to match BCB labels, improve training data quality.

### case_id=1801 FN partial_functionality

- 方法: `decodeFileToFile` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Decodes a Base64-encoded file and writes the decoded content to an output file, returning a boolean success indicator.
- B 摘要: Retrieves a resource by name from a local cache or downloads it from a URL with caching, returning an InputStream.
- 静态失败原因: Static BERT models rely on token-level overlap and have limited sensitivity to structural patterns; the low token Jaccard (0.224) and different API calls (Base64 vs. URL handling) led the model to classify as non-clone, missing the shared I/O template.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: None
- 共享行为: Both read from an InputStream and write to an OutputStream using a buffer loop.；Both use try-catch-finally blocks to handle exceptions and ensure stream closure.
- 行为差异: A decodes Base64 data, while B does no decoding.；A returns a boolean, while B returns an InputStream.；B implements a caching mechanism with HTTP conditional GET, while A does not.；B uses a cacheHashtable to store file mappings, while A does not.
- 修正建议: Incorporate control-flow or data-flow features to capture structural I/O patterns.；Use a model trained to recognize common boilerplate patterns in I/O operations.；Increase attention to syntactic structure rather than just token overlap.

### case_id=1802 FP boilerplate_overlap

- 方法: `run` vs `readUNI`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Downloads a vector tile from a URL, processes geometry, and adds it to a data layer with duplicate request prevention.
- B 摘要: Reads a tab-separated Unicode file from a URL and extracts IDs and descriptions into a provided vector.
- 静态失败原因: The static model likely overemphasized the shared URL reading and line-by-line processing pattern (boilerplate overlap) while ignoring the distinct domain-specific operations and output types.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels as non-clone because the core functionality differs completely: one is for tile/geometry processing, the other for tabular data extraction. The shared URL-reading boilerplate is insufficient to deem them similar.
- 共享行为: Both open a URL and read line-by-line using an input stream；Both handle IO exceptions with try-catch blocks；Both close the input stream in a finally block or after use
- 行为差异: Function A prevents duplicate HTTP requests via a synchronized set; Function B does not；Function A parses geometry data into VectorTile and GeometryCollection; Function B parses tab-separated strings into a vector；Function A supports both file and http protocols; Function B only http；Function A builds a geoJSON string from lines; Function B directly processes each line with Scanner
- 修正建议: Incorporate type information of objects being manipulated (e.g., VectorTile vs Vector<String>)；Use dataflow analysis to track how the read data is transformed and used；Add weight to method names and overall context (e.g., run vs readUNI)

### case_id=1803 FN partial_functionality

- 方法: `modifyApplicationMessage` vs `readAndRewrite`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.2`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Modifies a localized properties file by replacing or appending a message entry.
- B 摘要: Reads a DICOM image file and rewrites it to another file with pixel data processing.
- 静态失败原因: Static BERT/GraphCodeBERT rely on lexical and structural overlap, which is very low here; they miss the high-level functional similarity of file transformation.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considered both as file transformation tasks (read-modify-write), a broad Type-4 clone, despite different domains and implementations.
- 共享行为: Both read from an input file, transform the content, and write to an output file.
- 行为差异: Different domains (properties vs DICOM)；Different file formats and APIs；Different transformation logic
- 修正建议: Incorporate data/control flow analysis to capture abstract IO patterns；Use models trained on high-level intent or behavior

### case_id=1804 FN benchmark_preference_bias

- 方法: `getResourceAsStream` vs `patch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Caches and retrieves resources from remote URLs via HTTP, with local file caching.
- B 摘要: Backs up the Minecraft jar file by copying it to a backup path.
- 静态失败原因: Static BERT models rely heavily on token similarity and code structure. The low token Jaccard (0.069) and different method names/parameters led to a strong non-clone prediction. The model missed the broad functional overlap that BCB annotators might have seen.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB annotators may have considered both as 'file copy' operations, despite differing sources (network vs local). The common pattern of opening streams and copying data might have been deemed sufficient for a Type-4 clone.
- 共享行为: Both use FileInputStream and FileOutputStream for file I/O.；Both involve reading from a source and writing to a destination.
- 行为差异: Function A handles HTTP connections, caching headers, and conditional GET; function B does not.；Function A returns an InputStream; function B returns void.；Function A performs complex caching logic; function B simply copies a file.；Function A uses URL and URLConnection; function B uses direct file paths.
- 修正建议: Improve model sensitivity to high-level semantic patterns like 'copy stream' across different contexts.；Incorporate data-flow analysis to recognize that both functions perform a similar core operation (reading from input and writing to output).；Use contrastive learning with BCB-style labels to learn broader clone definitions.

### case_id=1805 FN partial_functionality

- 方法: `writeConfiguration` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.65`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Writes configuration resource content from a URL to a Writer.
- B 摘要: Downloads a KMZ file from a URL and extracts its entries to local files.
- 静态失败原因: Low token Jaccard (0.15) and different method names (writeConfiguration vs main) led the model to focus on lexical differences; the common high-level I/O pattern was missed.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as performing 'URL input stream to output' operations, a broad Type-4 semantic clone based on shared I/O pattern.
- 共享行为: Both open a URL, get an input stream, and perform read-write operations on the stream data.
- 行为差异: A copies a single stream to a writer using IOUtils.copy; B iterates over zip entries and writes each to a separate file.；A writes to a Writer object; B writes to multiple FileOutputStreams.；A includes error handling for null resource; B does not handle missing resource.；A does not close the input stream in case of exception (only in finally); B closes the ZipInputStream at the end.
- 修正建议: Enrich training with abstract I/O sequence patterns (open, read, write, close).；Use data flow or control flow graphs to capture structural similarities beyond tokens.；Incorporate method name normalization or semantic role analysis.

### case_id=1806 FP lexical_or_api_overlap

- 方法: `executeHttpGet` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Executes an HTTP GET request and returns the response body as a JSONObject.
- B 摘要: Constructs a Google Images search URL, performs an HTTP GET, and extracts image URLs from the HTML response.
- 静态失败原因: The model may have overemphasized the common pattern of opening an HTTP connection, reading lines with BufferedReader, and using similar API names (e.g., HttpURLConnection, InputStreamReader), while ignoring the different high-level purposes and post-processing.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely considered the overall functionality different (HTTP GET for JSON vs image search) and the low token overlap (0.105) supports a non-clone annotation despite shared low-level I/O pattern.
- 共享行为: Both perform an HTTP GET request and read the response line by line into a string buffer.
- 行为差异: Different HTTP client libraries (Apache HttpClient vs java.net HttpURLConnection)；Different input: A takes a URI parameter, B uses instance fields and constructs a URL；Different output: A returns a JSONObject, B is void and populates a list；Different response processing: A parses JSON, B extracts image URLs from HTML
- 修正建议: Incorporate method signature and return type information；Use data flow analysis to distinguish different processing after reading the stream；Consider the overall goal of the function (e.g., JSON parsing vs image URL extraction)

### case_id=1807 FP lexical_or_api_overlap

- 方法: `populateResources` vs `getRequestContent`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Loads and saves template resources and image properties from classpath and URLs.
- B 摘要: Fetches and returns the first line from an HTTP URL.
- 静态失败原因: Static BERT/GraphCodeBERT likely overemphasized the common API sequence (URL, openStream, BufferedReader, readLine) and ignored the broader context, such as return type, side effects, and overall workflow.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically requires more functional similarity than mere I/O pattern overlap; the distinct objectives (resource saving vs. HTTP fetching) and different outputs lead to a non-clone label.
- 共享行为: Both use URL objects to open streams；Both use BufferedReader to read text
- 行为差异: A processes multiple files and saves to persistent storage; B returns a single line from an HTTP response；A uses classpath resources and predefined image list; B operates on a given URL；A has specific error handling for MalformedURLException and IOException; B throws generic Exception；A is static void with side effects; B is protected String returning a value
- 修正建议: Incorporate return type and method modifier information；Use data flow analysis to track how read content is used (saved vs. returned)；Consider the call graph and dependencies to differentiate utility patterns；Use contrastive learning to separate methods with similar I/O but different purposes

### case_id=1808 FN partial_functionality

- 方法: `copyFiles` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Recursively copies files and directories from source to destination using file channels.
- B 摘要: Builds a site for editing by transforming XML pages and writing output files with various configurations.
- 静态失败原因: Static BERT/GraphCodeBERT models rely heavily on token and structure overlap, which is very low (Jaccard 0.069) due to different method names, parameter lists, and control flow. The shared file I/O patterns are buried in long code (B is very long) and not recognized as semantically similar.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this as a clone because both methods involve file copying functionality (B writes processed files to output, which can be seen as copying transformed content) and share similar iterative structure over items, even though the overall semantics differ significantly.
- 共享行为: Both involve file I/O operations (reading/writing files).；Both iterate over a collection of items (files/directories in A, pages in B).
- 行为差异: A performs simple recursive file copy; B performs complex XML transformation and string manipulation.；A handles arbitrary directory structures; B processes a fixed set of pages with detailed control flow.；A uses FileChannel for efficient copying; B uses FileWriter and custom FileSystem methods.
- 修正建议: Use a model that captures partial functional overlap, e.g., by decomposing functions into subroutines.；Incorporate dataflow analysis to identify common I/O patterns.；Train with more diverse clone types including broad functional similarity.

### case_id=1809 FP lexical_or_api_overlap

- 方法: `wordFrequency` vs `checkForUpgrade`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Searches a web query for a word's frequency by replacing a placeholder, fetching URL content, and parsing lines for a pattern.
- B 摘要: Checks for software upgrades by querying a license server, parsing XML-like response, processing upgrade records, and updating UI state.
- 静态失败原因: Static models like GraphCodeBERT may focus on token-level overlap (e.g., both use 'URL', 'BufferedReader', 'in.readLine()') and miss the semantic gap. The code structure also shares boilerplate pattern (try-catch, while loop) that inflates similarity.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels clones only when functions share similar behavior, often ignoring trivial API use overlap. These functions have completely different purposes and control flow, so BCB likely considers them non-clones.
- 共享行为: Both use URL and BufferedReader to read remote data line by line.
- 行为差异: Function A replaces a placeholder in a query; Function B constructs a URL with multiple parameters.；Function A matches lines against a regex pattern and returns a count; Function B splits lines into fields and processes upgrade records.；Function A returns an integer; Function B manipulates UI components and executes SQL commands.；Function A has simple exception handling; Function B handles complex logic with database and UI updates.
- 修正建议: Incorporate method-level context (e.g., name, surrounding class) to distinguish purpose.；Use data flow analysis to highlight different variable purposes.；Apply contrastive learning on diverse non-clone pairs with similar API usage.；Add attention to return types and side effects (UI/database vs simple computation).

### case_id=1810 FP boilerplate_overlap

- 方法: `getWebPage` vs `getFullScreenUrl`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a URL and returns the entire page content as a string, throwing an Error on IOException.
- B 摘要: Connects to a YouTube URL, parses the response to extract video parameters, and returns a constructed video download URL.
- 静态失败原因: The model might have been misled by the common boilerplate code (URL, openStream, BufferedReader, while loop) and overlooked the distinct parsing logic and different purpose. Low token overlap but similar API usage can cause false positives.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely considers these non-clones because the overall functionality is different: one is a generic web page fetcher, the other is a YouTube-specific URL extractor. Even though both use similar I/O patterns, the core logic and output differ significantly.
- 共享行为: Both open a URL connection and read lines using BufferedReader and InputStreamReader.；Both loop through lines until null.；Both handle exceptions (IOException for A, Exception for B).
- 行为差异: A returns full content; B returns a constructed URL after parsing.；A throws Error on failure; B prints error and continues.；B updates a field (ytTitle) and prints debug info; A does not.；B specifically searches for 'fullscreenUrl' and parses key-value pairs; A only concatenates lines.
- 修正建议: Incorporate dataflow analysis to track how inputs and outputs are used.；Add contrastive learning with examples where API usage is similar but semantics differ.；Use language models that better capture long-range dependencies and overall intent.

### case_id=1811 FN partial_functionality

- 方法: `PageLoader` vs `seeURLConnection`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.95`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Constructor that takes a page address, creates a URL, reads all lines into a field inputLine, and closes the reader.
- B 摘要: Method that creates a URL to a hardcoded address, opens a URLConnection, reads all lines into a StringBuffer, logs the result, and closes the reader.
- 静态失败原因: Static BERT models rely on token-level representations and may not capture the high-level semantic similarity due to differences in method signatures, variable names, and the presence of logging. The low token Jaccard (0.315) indicates limited lexical overlap, leading the model to classify them as non-clones.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB considers these clones because both functions perform the essential task of reading all lines from a URL, which is the primary functionality. The differences in method type, parameterization, and output handling are considered minor variations.
- 共享行为: Both create a URL object；Both open an input stream from the URL；Both read all lines from the stream and concatenate them；Both close the reader after reading
- 行为差异: Function A is a constructor, while Function B is a regular method；Function A takes a URL as a parameter, while Function B uses a hardcoded URL；Function A stores the result in a field (inputLine), while Function B logs the result；Function B uses URLConnection and getInputStream(), whereas Function A directly uses url.openStream()
- 修正建议: Use a data-flow-aware model like GraphCodeBERT that captures variable dependencies and structural similarity；Apply clone detection techniques that focus on control flow and data flow rather than exact token matching；Include training examples that emphasize partial functionality similarity

### case_id=1812 FP boilerplate_overlap

- 方法: `send` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Sends an email with attachments, headers, and priority using JavaMail, with session handling and quota control.
- B 摘要: Handles GUI action events for setting preferences like file paths, date format, and look-and-feel in a genealogy application.
- 静态失败原因: The static model likely focused on overlapping syntactic patterns like exception handling, null checks, and method calls (e.g., 'addHeader', 'setText'), but missed the semantic context. The token Jaccard is low (0.08), so overlap is minimal; however, the model may have been misled by similar control structures or common API sequences.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels this as non-clone because the two functions perform completely different tasks: one is an email sender, the other is a GUI event handler for preferences. The high-level purpose and domain are entirely distinct.
- 共享行为: Both handle user input or configuration but for entirely different domains；Both contain try-catch blocks for exception handling
- 行为差异: Function A constructs and sends an email message; Function B updates UI components and stores preferences；Function A deals with email addresses, MIME types, and session management; Function B deals with file choosers, combo boxes, and UI updates；Function A has email-specific logic (HTML vs plain text, headers, priority); Function B has application-specific logic (setting paths for external tools, date formats, look-and-feel)
- 修正建议: Improve training data with more diverse non-clone pairs that share common boilerplate but differ in functionality；Incorporate higher-level structure or data flow analysis to differentiate email sending from GUI event handling；Use contrastive learning to emphasize domain-specific keywords and discourage reliance on generic patterns

### case_id=1813 FP lexical_or_api_overlap

- 方法: `doVersionCheck` vs `downloadModel`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Checks for a new version of jEdit by reading version info from a URL and comparing with current build.
- B 摘要: Downloads an RDF model from a URL by opening an HTTP connection, reading the input stream, and parsing it into a Model object.
- 静态失败原因: The model likely over-relied on surface-level token overlap (URL, InputStream, IOException) and similar control flow (try-catch, reading from stream), missing the semantic difference in what the data is used for. This is a classic case of lexical/API overlap outweighing deeper understanding.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels non-clones for pairs with different high-level purposes despite similar low-level API usage. The functions have distinct inputs/outputs and belong to different domains (UI version check vs. model download), so BCB rightly marks them as non-clones.
- 共享行为: Both open a URL connection and read from an input stream.；Both handle IOException in a try-catch block.
- 行为差异: Function A reads text lines to extract version strings; Function B reads and parses RDF model data.；Function A shows UI messages (wait cursor, dialogs) and uses jEdit-specific properties; Function B returns a Model and has no UI.；Function A catches only IOException and does not rethrow; Function B catches MalformedURLException and IOException and throws RuntimeException.；Function A does not return a value; Function B returns a Model object.
- 修正建议: Incorporate method name and comment semantics via code summarization or docstring embeddings.；Enhance representation with data flow or program dependency graphs to capture output/use of variables.；Include contrastive learning on pairs with similar API but different intent.

### case_id=1814 FP boilerplate_overlap

- 方法: `main` vs `execute`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Generates adapter code from a Prolog file, handling command-line arguments, file parsing, and JAR writing.
- B 摘要: Converts a Java source file to HTML with file reading, writing, and resource cleanup.
- 静态失败原因: The static model likely overemphasized lexical overlap in exception handling (printStackTrace, close) and file I/O patterns, ignoring overall semantic context.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would label non-clone because the functions have no significant code reuse and serve entirely different domains.
- 共享行为: Both perform file I/O operations with try-catch blocks and closing resources in finally.
- 行为差异: Different purposes: code generation vs. file conversion.；Different error handling: A prints messages and returns; B prints stack trace and continues.；Different control flow and dependencies: A uses multiple libraries; B is simpler.
- 修正建议: Train on more diverse data to reduce weight of boilerplate patterns.；Incorporate dataflow or structural differencing to capture high-level semantics.

### case_id=1815 FN partial_functionality

- 方法: `copyResource` vs `truncate`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource from a URL or file to a destination file by reading byte-by-byte and writing to an output stream.
- B 摘要: Compresses a log file into a zip archive if it is older than JVM start time, then deletes the original file.
- 静态失败原因: Static BERT models rely on token and structural overlap; these functions have low Jaccard similarity (0.163), different method names, and different control flow (simple loop vs. complex conditional with try-catch-finally). The model could not capture the abstract functional commonality.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considers these clones under Type-4 (functionally similar) because both involve reading from an input source and writing to an output destination, a core file I/O operation, despite differences in compression and extra steps.
- 共享行为: Both open an input stream to read data and an output stream to write data.
- 行为差异: copyResource performs raw byte copying without buffering; truncate uses buffered reading (1024 bytes) and writes to a ZipOutputStream.；truncate includes file age check, backup directory creation, zip compression, CRC calculation, and file deletion; copyResource has no such logic.；truncate has extensive error handling and resource cleanup; copyResource only closes streams in the main flow.
- 修正建议: Incorporate functional similarity metrics that recognize common I/O patterns (e.g., read-write loops).；Use dataflow analysis to identify shared stream handling operations.；Consider program simplification or summarization to highlight core behavior.

### case_id=1816 FN benchmark_preference_bias

- 方法: `modifyApplicationMessage` vs `testStandardTee`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Modifies a localized properties file by replacing or adding a key-value pair, creating the file if missing based on an English template.
- B 摘要: Tests that a TeeWriter correctly copies input to multiple destinations by reading from a StringReader and writing to two StringWriters.
- 静态失败原因: The model correctly predicted non-clone (token Jaccard 0.083) and recognized the structural differences: one is a void method with file I/O and loop, the other is a test method with assertions and specific IO classes.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as clone due to surface-level similarity: both perform read and write operations involving strings and streams, despite different intents.
- 共享行为: Both involve reading from a source and writing to a destination using I/O streams
- 行为差异: A handles file I/O and property file format with locale-specific paths; B uses in-memory streams with no file operations；A modifies a configuration file; B tests a utility class；A creates files if not existing; B uses predefined StringReader/StringWriter；A uses BufferedReader/FileWriter; B uses IOUtils.copy and TeeWriter with assertions
- 修正建议: Re-evaluate BCB annotation for this pair as likely mislabeled

### case_id=1817 FN boilerplate_overlap

- 方法: `getFile` vs `execute`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.4`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies its endpoint attribute, and saves to a temporary file, returning the file path.
- B 摘要: Reads a source file and writes to a destination file after creating parent directories, using an overloaded method with conversion config.
- 静态失败原因: The model likely focused on low token overlap and different method names/return types, missing the broad structural similarity in file I/O patterns that BCB may accept.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may consider them clones due to shared boilerplate of file handling, resource management, and exception handling patterns, despite different core tasks.
- 共享行为: Both use file I/O with opening, processing, and closing streams；Both include logging/information messages；Both handle exceptions with try-catch-finally
- 行为差异: A downloads from network and modifies XML; B copies/transforms local file；A returns file path; B is void；A uses NIO channels and URLConnection; B uses Reader/Writer；A checks for existing file and creates new ones conditionally; B creates directories unconditionally
- 修正建议: Train model to recognize higher-level structural patterns beyond lexical overlap；Incorporate program flow or API usage similarity to capture boilerplate clones

### case_id=1818 FN benchmark_preference_bias

- 方法: `storeImage` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Stores an image from an input stream to a server-specified folder, optionally creating resized copies.
- B 摘要: Generates an entire website for editing by applying XML transformations and writing multiple output files.
- 静态失败原因: The static model correctly identified the lack of semantic and syntactic similarity and predicted non-clone, but the BCB label is erroneous, causing a false-negative evaluation.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB likely mislabeled this pair as clones due to superficial commonalities like file I/O and stream usage, but the functions serve entirely different purposes with no shared logic.
- 共享行为: Both perform file I/O operations and use input/output streams.
- 行为差异: storeImage handles a single image file and returns a path; buildSiteForEdit generates multiple HTML pages and returns void.；storeImage's core is a file copy with optional image resizing; buildSiteForEdit involves XML parsing, string manipulation, and page iteration.；storeImage uses a static naming convention based on date; buildSiteForEdit relies on external properties and complex templates.
- 修正建议: Re-evaluate and correct the BCB label for this pair; it is likely a labeling error.；Consider using a threshold for functional overlap rather than accepting superficial I/O operations as clones.

### case_id=1819 FN benchmark_preference_bias

- 方法: `doGet` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.1`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: doGet handles an HTTP GET request for a portal page, involving permission checks, logging, and optional caching with file generation.
- B 摘要: copyFile copies a file from one location to another using FileChannel transfer.
- 静态失败原因: The static BERT model correctly predicted non-clone because the token overlap is very low (0.0625) and the functions have completely different APIs and purpose.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as a clone due to both functions performing file-related I/O operations (copyFile directly; doGet indirectly via caching to temp file), but the functional similarity is extremely broad and likely an annotation error.
- 共享行为: Both involve I/O operations (reading/writing data from/to files or streams).
- 行为差异: doGet is a servlet method processing HTTP requests with complex logic including user authentication, page retrieval, and response handling.；copyFile is a simple utility function that directly copies a file using NIO channels with no external dependencies.；doGet writes to an HTTP response and optionally creates temporary files; copyFile only copies between files.；doGet has extensive error handling and logging; copyFile uses try-finally for resource cleanup.
- 修正建议: Review BCB ground truth for this pair to ensure annotation consistency.；Consider removing this pair from the training set if it represents a false positive in the ground truth.

### case_id=1820 FN benchmark_preference_bias

- 方法: `setContenu` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Sets the content of a file electronique by copying an input stream to an output stream and updating metadata.
- B 摘要: Returns an InputStream for a resource, using a local cache to avoid repeated network fetches.
- 静态失败原因: Static BERT correctly predicted non-clone; the BCB label appears to be a false positive in the benchmark.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: The BCB label 1 may be due to both functions having stream copying and metadata handling, but the overall purpose and context are entirely different. It might be a mislabel.
- 共享行为: Both involve handling of InputStream and OutputStream for data transfer.；Both have try-catch-finally blocks for stream closing.
- 行为差异: A sets file content and metadata; B retrieves a resource and caches it.；A operates on local file system; B accesses remote URLs and uses a cache directory.；A has logic for duplicate file detection; B has HTTP request handling and caching.；A performs metadata extraction; B does not.
- 修正建议: Re-evaluate BCB label for this pair; they are not clones.；Improve benchmark consistency by requiring stronger semantic equivalence.

### case_id=1821 FN benchmark_preference_bias

- 方法: `getHTML` vs `readData`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Fetches a web page via HTTP and optionally writes it to a file, returning the HTML content.
- B 摘要: Initializes multiple sets and maps by parsing static string fields and reading a configuration file, populating data structures for Tibetan transliteration.
- 静态失败原因: The model correctly predicted non-clone due to low lexical overlap (token Jaccard 0.08) and distinct control flows. From a BCB bias perspective, it 'failed' to match the BCB label, but semantically it is correct.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have considered both as 'reading and processing data' functions, overlooking the completely different data sources, outputs, and purposes. Possibly a labeling error or overly broad interpretation of Type-3/Type-4.
- 共享行为: Both involve reading textual data and appending to collections (StringBuilder vs Sets/Maps).
- 行为差异: getHTML fetches from URL, readData parses static strings and reads a file.；getHTML returns a String, readData is void and modifies global state.；getHTML handles HTTP connection and file writing, readData handles tokenization and hash table population.
- 修正建议: Re-evaluate BCB annotation for this pair; they are semantically unrelated.；Improve BCB consistency by requiring at least some shared functionality or common behavior.

### case_id=1822 FN benchmark_preference_bias

- 方法: `copyFile` vs `doGet`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Copies a file from source to destination using NIO FileChannel.
- B 摘要: Handles an HTTP GET request to retrieve and render a portal page, with caching and error handling.
- 静态失败原因: The static BERT model correctly identified the lack of behavioral overlap given low token Jaccard (0.037). It did not fail; the BCB label is likely incorrect. Under the assumption that BCB is correct, the model might have failed due to insufficient handling of long-range dependencies and diverse domains, causing it to miss superficial file-I/O similarity.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB likely considered both functions perform file operations and handle I/O exceptions, but this is insufficient for clone labeling. The annotation may be erroneous or reflect a very broad Type-4 semantic similarity (e.g., both involve file manipulation).
- 共享行为: Both involve file I/O operations (FileChannel vs FileWriter).；Both handle IOException.；Both are Java methods with throws clauses.
- 行为差异: Function A is a simple utility for file copying; Function B is a complex servlet processing HTTP requests.；Function B includes page retrieval, user authorization, logging, caching, and HTML output generation.；Function B has multiple conditional branches and error scenarios (e.g., page not found, forbidden).；Function A has no control flow beyond basic channel operations.
- 修正建议: Improve benchmark annotation consistency: verify clones with functional semantics.；Use cross-function similarity measures beyond lexical overlap (e.g., API call graphs, control flow patterns).；Incorporate domain-specific knowledge to distinguish generic I/O from application-specific logic.

### case_id=1823 FN boilerplate_overlap

- 方法: `getResourceAsStream` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Retrieves a resource from a URL with caching and returns an InputStream to the cached file.
- B 摘要: Copies a file from source to destination using FileChannel and returns success status.
- 静态失败原因: Static BERT models rely on token similarity and may miss functional similarity due to low lexical overlap and different method names; they lack understanding of control/data flow patterns common in IO operations.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB might consider them clones due to shared boilerplate IO operations (open, transfer, close) and exception handling, overlooking the distinct high-level purposes.
- 共享行为: Both open input and output streams；Both transfer data from input to output；Both close streams in finally blocks；Both handle IO exceptions
- 行为差异: A uses HTTP, caching, and a hash table; B is a simple file copy；A returns an InputStream; B returns a boolean；A reads from URL and writes to local file; B reads from source file and writes to destination file；A has print statements and conditional cache logic; B does not
- 修正建议: Incorporate dataflow analysis to identify IO patterns；Use structure-based features like AST or CFG；Train on more diverse IO clone pairs to capture partial functionality similarity

### case_id=1824 FN benchmark_preference_bias

- 方法: `doGet` vs `writeData`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Handles HTTP GET request by retrieving a page, checking user permissions, and rendering the page to the response.
- B 摘要: Writes a formatted table of time-series data to a text file, generating date and peak values.
- 静态失败原因: The static model correctly predicted non-clone; it did not fail. The apparent failure is due to an erroneous BCB label.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: None
- 共享行为: Both involve outputting data (HTTP response vs file write)
- 行为差异: Different domains: HTTP request handling vs file I/O；Different control flows: permission checking and error handling vs loop-based data generation；Different data structures: HttpServletRequest/Response vs primitive arrays and file streams
- 修正建议: Re-evaluate BCB label for this pair；Improve dataset quality to remove false positive clones

### case_id=1825 FN partial_functionality

- 方法: `getFile` vs `setup`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies its endpoint address in the XML, and returns the file path.
- B 摘要: Extracts native library files from a JAR archive to a temporary directory and sets the library path based on the operating system architecture.
- 静态失败原因: Static BERT models rely on lexical and structural overlap, which is low (Jaccard 0.112). They fail to capture abstract functional similarity of resource setup due to different APIs (URLConnection vs ZipInputStream, XML vs System.getProperty) and long-range dependencies (XML manipulation vs arch detection).
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as utility methods for initializing external resources (WSDL vs native libraries) with similar structural patterns (check file existence, create temp files, read/write streams, handle exceptions), leading to a Type-3/Type-4 annotation despite low lexical overlap.
- 共享行为: Both involve file I/O and temporary file creation；Both perform resource setup (download/extract) for a service
- 行为差异: A involves network download and XML parsing; B involves JAR extraction and system property checks；A modifies XML content; B does not modify file content；A returns a file path; B does not return a value but sets a system property
- 修正建议: Increase training data with diverse resource setup functions；Incorporate semantic role labeling or API usage patterns；Use contrastive learning to recognize broad functional similarity

### case_id=1826 FN lexical_or_api_overlap

- 方法: `runScript` vs `GetResponse`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.95`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches content from a URL constructed from the applet code base and script name, returns the content as a string or "error!" on failure.
- B 摘要: Sends an HTTP GET request to a given URL and returns the response body as a string, or null on failure.
- 静态失败原因: Low token Jaccard (0.2) and different API usage (InputStream vs HttpURLConnection) cause static models to miss semantic similarity; they focus on surface-level tokens.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: In BCB, tasks retrieving content from a URL and returning it as a string are considered functionally similar (Type-3/4), despite differences in protocol and reading method.
- 共享行为: Both fetch content from a URL and return it as a string.
- 行为差异: runScript uses generic InputStream and reads byte-by-byte; GetResponse uses HttpURLConnection, checks response code, and reads line-by-line.；Error handling: runScript catches all exceptions and returns "error!"; GetResponse catches specific exceptions and returns null.
- 修正建议: Incorporate control-flow and data-flow features；Use code normalization for similar API patterns；Train on more diverse Type-3/4 examples

### case_id=1827 FP lexical_or_api_overlap

- 方法: `setMembers` vs `getRequestContent`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: setMembers reads a URL, parses HTML for select elements, and populates class member arrays m_strComponents and m_strPriorities.
- B 摘要: getRequestContent takes a URL string, opens a connection, reads the first line, closes resources, and returns that line.
- 静态失败原因: Static BERT/GraphCodeBERT likely over-relied on lexical and API overlaps (e.g., 'URL url = new URL(...)', 'BufferedReader', 'readLine()') and ignored the divergent control flow and data operations, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the functions have fundamentally different purposes and outputs, despite sharing some API calls. The similarity in URL handling is superficial compared to the distinct overall functionality.
- 共享行为: Both open a URL and read lines using BufferedReader
- 行为差异: A is void, B returns a String；A parses HTML and extracts multiple values, B returns the first line only；A modifies class members, B returns a value；A uses pattern matching, B does not
- 修正建议: Incorporate structural information (e.g., CFG, DFG) to distinguish between different data flows；Use AST-based or graph-based models that capture the full logic beyond surface-level text；Apply contrastive learning to emphasize functional equivalence over textual similarity

### case_id=1828 FP boilerplate_overlap

- 方法: `main` vs `sendErrorMessage`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Parses a Prolog file to generate adapter classes and a lookup.
- B 摘要: Sends an error message by zipping a log file and mailing it.
- 静态失败原因: The model may have been misled by overlapping boilerplate code (e.g., File, exception handling, catch blocks) despite low token Jaccard.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: The functions are unrelated; BCB labels non-clones for such diverged semantics.
- 共享行为: Both use I/O operations；Both have exception handling
- 行为差异: Completely different purposes；Different control flow and data processing
- 修正建议: Enhance model with high-level semantic understanding；Incorporate data flow and control flow analysis

### case_id=1829 FN library_context_missing

- 方法: `copyFile` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `context_recovery_then_expert`；动态可解性: `low`；执行优先级: `low`
- A 摘要: Copies a file from source to destination using buffered stream I/O.
- B 摘要: Launches an Eclipse NexOpen project configuration, handling XML files, Hibernate dialect, and reverse engineering.
- 静态失败原因: The low token overlap (0.066) and highly different contexts (simple utility vs. complex IDE plugin) likely caused the model to miss any subtle structural or semantic similarity.
- 静态 case study: 该类错误缺少关键上下文或需要深层语义，纯静态方法不可靠。
- 动态 case study: 动态执行价值较低：样本可能依赖库、框架、网络、GUI、数据库或项目上下文，需要先恢复环境或 mock 依赖。
- BCB 偏好解释: BCB may have labeled as clone due to both methods involving file reading/writing with byte buffers and stream handling, which could be seen as broad Type-4 partial functionality similarity.
- 共享行为: Both perform file I/O operations (reading/writing streams).；Both handle exceptions with try-finally or try-catch-finally.
- 行为差异: Function A is a simple file copy utility; function B is a complex IDE launch sequence.；Function A has no external dependencies; function B uses Eclipse, Maven, and Hibernate APIs.；Function A is deterministic; function B interacts with workspace resources and assumes a specific project structure.
- 修正建议: Incorporate project-level or module-level context to distinguish utility functions from framework-specific code.；Use code summarization techniques to capture high-level intent and compare method purposes.

### case_id=1830 FP lexical_or_api_overlap

- 方法: `modifyProperty` vs `perform`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.98`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Modifies a property value, hashing it with MD5 if the property name is 'Password'.
- B 摘要: Handles a web request to classify a concept, building XML, making an HTTP call, parsing the response, and setting session attributes.
- 静态失败原因: Static model likely overemphasized common keywords (e.g., 'property', 'session', 'throws') and syntactic patterns (try-catch, loops) while ignoring deep semantic and structural differences.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would not label these as clones because they serve completely different business purposes and have no significant functional overlap beyond generic Java patterns.
- 共享行为: Both throw exceptions.；Both use try-catch blocks.；Both involve string manipulation.
- 行为差异: Code A performs a simple property update with optional password hashing; Code B executes a complex web service interaction for concept classification.；Code A has no HTTP or session handling; Code B heavily relies on HTTP, session, and XML parsing.；Code A's output is a property value change; Code B's output is an ActionForward string and session state changes.
- 修正建议: Enhance model with dataflow analysis to understand variable manipulations.；Use domain-specific embeddings to differentiate application contexts.；Increase training diversity to avoid overfitting on boilerplate structures.

### case_id=1831 FP lexical_or_api_overlap

- 方法: `read` vs `getFullScreenUrl`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a camera log from a URL, parses each line into CameraLogRecord, and stores sorted records.
- B 摘要: Fetches a YouTube URL to extract video metadata (video_id, t, title) and constructs a full video URL.
- 静态失败原因: Static BERT/GraphCodeBERT likely overemphasized the lexical overlap of URL connection and BufferedReader usage, ignoring the larger semantic differences in purpose and data processing.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely considers these non-clones because the overall functionality differs: one is a generic log reader, the other is a YouTube-specific URL extractor.
- 共享行为: Both open a URL connection and read data line by line using BufferedReader
- 行为差异: A parses each line into CameraLogRecord; B searches for a specific line containing 'fullscreenUrl'；A collects all records; B extracts only video_id, t, and title；A sorts records; B builds a new URL string；A uses logging; B uses System.out.println
- 修正建议: Increase sensitivity to method-level semantics beyond shared API usage；Incorporate structural differencing or data-flow analysis to capture different post-processing steps

### case_id=1832 FP other

- 方法: `MotixFileItem` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Constructor that initializes a file item from an input stream, copying data and optionally reading an image.
- B 摘要: Action event handler that manages GUI settings, file choosers, and preference saving based on command.
- 静态失败原因: Low token overlap (0.05) suggests the model may have been misled by common Java API usage patterns (e.g., JFileChooser, InputStream) or overgeneralized from long-range dependencies in code structure, but the false positive is unusual given the dissimilarity.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB correctly labels non-clone because functions have completely different purposes and no shared functionality.
- 共享行为: Both involve conditional execution based on a boolean flag or command string
- 行为差异: Function A is a constructor for data processing; Function B is an event handler for UI configuration；A deals with InputStream and image reading; B deals with JFileChooser, preferences, and UI updates；A has resource cleanup in finally block; B has multiple if-else blocks and UI component updates；A has no user interaction; B involves dialogs and user choices
- 修正建议: Increase training data diversity to reduce overgeneralization；Incorporate structural or dataflow analysis to distinguish constructors from event handlers；Use threshold tuning or ensemble methods to reduce false positives

### case_id=1833 FP lexical_or_api_overlap

- 方法: `actionPerformed` vs `copy`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Handles various GUI preference actions (e.g., setting file paths for Graphviz, ImageMagick, and other settings) in an actionPerformed method.
- B 摘要: Copies a file from source to destination with validation and error handling.
- 静态失败原因: The model likely overfitted to lexical cues such as 'File', 'IOException', or common Java structure, leading to a false positive despite vastly different semantics.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labeled 0 because the two functions have no semantic similarity: one is a GUI action listener, the other is a file copy utility. There is no shared intent or behavior.
- 行为差异: Function A is an event handler for GUI preferences, involving file choosers and saving settings.；Function B is a utility that copies file contents using streams.；No overlap in core functionality.
- 修正建议: Improve training data diversity to reduce reliance on superficial token matches.；Incorporate structural or dataflow analysis to distinguish event handlers from utilities.

### case_id=1834 FP long_range_semantics

- 方法: `readData` vs `copyFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `static_summary_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Parses a configuration file to populate multiple sets and maps used for Tibetan transliteration.
- B 摘要: Copies a file from source to destination using FileChannel.
- 静态失败原因: The model likely overfocused on superficial similarities like file-related keywords (e.g., 'file', 'IOException') and common boilerplate patterns (try-catch, error handling), while failing to capture the distinct dataflow and algorithmic structure, especially given the large disparity in code length and token overlap.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB annotation typically requires semantic equivalence or strong similarity; these functions have completely different purposes and behavior, so they are correctly labeled as non-clones.
- 共享行为: Both perform file I/O operations；Both use try-catch blocks for exception handling
- 行为差异: A parses textual data and builds data structures; B copies bytes from one file to another；A involves tokenization and multiple lookup table initializations; B is a simple data transfer；A has complex conditional logic and error handling for parsing; B has straightforward channel transfer；A operates on predefined string fields; B operates on arbitrary files
- 修正建议: Enhance the model's ability to capture long-range dependencies and overall program logic；Use dataflow analysis or graph-based representations to distinguish between parsing and I/O operations；Include more diverse training pairs with low lexical overlap but different semantics

### case_id=1835 FP lexical_or_api_overlap

- 方法: `readPage` vs `run`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a URL page line by line, optionally skipping lines starting with '#', and returns the concatenated HTML.
- B 摘要: Loads a tile from a data source by reading a URL (supporting file and HTTP protocols), concatenates lines into geoJSON, processes the tile geometry, and adds features to a data layer with synchronization.
- 静态失败原因: The static BERT/GraphCodeBERT model likely overemphasized the lexical overlap of common API calls (BufferedReader, InputStreamReader, openStream, readLine) and the while loop structure, ignoring the broader context and purpose of the functions.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labeled non-clone because the overall functionality is entirely different: one is a generic URL reader, the other is a specific tile loader with complex processing. The common code snippet is a minor shared pattern, not indicative of clone by BCB standards.
- 共享行为: Both read from a URL using BufferedReader and InputStreamReader；Both concatenate lines read from the stream
- 行为差异: Function A has optional comment filtering; B does not；Function B includes synchronization, multiple protocol handling, geometry processing, and side effects; A only returns a string；Function B is a Runnable with no return value; A returns String；Function B handles exceptions (MalformedURLException, FileNotFoundException, IOException); A only throws Exception
- 修正建议: Incorporate structural or dataflow analysis to differentiate functions with similar API usage but different overall logic；Use attention mechanisms that focus on high-level semantics rather than local token matches；Add training examples with similar API patterns but different functionality to reduce false positives

### case_id=1836 FP lexical_or_api_overlap

- 方法: `getLinksFromURLFast` vs `importSequences`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Extracts hyperlinks and anchor texts from HTML content of a URL using regex.
- B 摘要: Parses FASTA-like sequence data from a URL, extracting sequence names and sequences.
- 静态失败原因: Static BERT/GraphCodeBERT may have focused on lexical overlaps (URL, InputStream, BufferedReader) and the general pattern of reading from URL, missing the domain-specific semantics (HTML vs. sequence data).
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB may label as non-clone because the overall purpose and output data structures are completely different, despite both involving URL reading.
- 共享行为: Both read data from a URL using InputStream/URLConnection；Both parse line-by-line and store results in collections
- 行为差异: A extracts HTML links and anchor texts; B extracts biological sequence names and sequences.；A uses multiple regex patterns; B uses a custom ImportHelper with tokenization.；A returns a Vector array; B populates class-level lists.；A has time-check logging; B has exception handling for EOF and MalformedURL.
- 修正建议: Improve training data diversity to reduce false positives on different domains.；Incorporate type information (e.g., output types) to distinguish data processing purposes.；Use control-flow and data-flow analysis to differentiate high-level functionality.

### case_id=1837 FP lexical_or_api_overlap

- 方法: `getTicketsForQueue` vs `getFullScreenUrl`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches a list of RT tickets for a given queue by querying a REST API.
- B 摘要: Extracts a full-screen YouTube video URL from an HTML page.
- 静态失败原因: The model likely overemphasized lexical and structural overlap (e.g., URL, BufferedReader, try-catch) while missing the semantic difference in the overall task. The high Jaccard similarity of 0.15 further suggests token-level commonality misled the classifier.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically annotates clones based on substantial functional similarity, not just shared boilerplate. The two functions have entirely different domains and outcomes, so BCB would not label them as clones.
- 共享行为: Both perform HTTP requests to fetch external resources.；Both parse response content line by line using BufferedReader.；Both use try-catch blocks for exception handling.
- 行为差异: Function A interacts with a specific ticket tracking API; Function B scrapes a YouTube page.；Function A returns a list of ticket objects; Function B returns a single URL string.；Function A includes progress indication via external fields; Function B does not.；Error handling differs: A throws custom exceptions, B prints errors.
- 修正建议: Incorporate dataflow or control-flow analysis to distinguish different functionality.；Use contrastive learning with negative examples that share vocabulary but differ in intent.；Add domain-specific features like method name and return type.

### case_id=1838 FP boilerplate_overlap

- 方法: `main` vs `createTempFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Parses a Prolog file, generates adapter classes, and writes them to a JAR file.
- B 摘要: Copies a classpath resource into a temporary file.
- 静态失败原因: The static model likely overfitted to common API usage patterns (File, InputStream, etc.) and ignored the drastically different control flow and intent.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels as non-clone because the functions have entirely different purposes and no meaningful semantic overlap.
- 共享行为: Both use file I/O and exception handling
- 行为差异: Different input sources (Prolog file vs classpath resource)；Different outputs (JAR file vs temp file)；Different logic (adapter generation vs simple copy)；Different methods (main vs createTempFile)
- 修正建议: Incorporate data-flow analysis；Use contrastive learning to separate distinct intents；Increase sensitivity to method signatures and object types

### case_id=1839 FN benchmark_preference_bias

- 方法: `init` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Initializes a report file by handling backup, restarting from previous run, and writing XML header.
- B 摘要: Builds a site for editing by transforming pages with XSLT and writing output files.
- 静态失败原因: Low token Jaccard and different method names/syntax likely led to non-clone prediction; model lacks deep semantic understanding.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled as clone due to broad Type-4 similarity: both involve XML and file processing, though functionality differs.
- 共享行为: Both perform file I/O and XML stream operations.；Both handle exceptions with try-catch blocks.；Both check for file existence and create directories.
- 行为差异: Function A is about report initialization and restart logic; Function B processes multiple pages with XSLT.；Different input parameters and output formats.；Core logic differs: resumption vs. transformation.
- 修正建议: Use dataflow or program dependence graph analysis.；Incorporate functional role detection (e.g., initialization vs. transformation).；Apply dynamic analysis to capture runtime behavior.

### case_id=1840 FP lexical_or_api_overlap

- 方法: `addDataFromURL` vs `getFullScreenUrl`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads all lines from a URL and appends them to a text buffer, with fallback to append URL on error.
- B 摘要: Connects to a YouTube video page, extracts parameters from a line containing 'fullscreenUrl', constructs a video download URL, and returns it.
- 静态失败原因: The model likely over-relied on shared I/O patterns (BufferedReader, readLine, try-catch) and method length, missing the distinct domain-specific logic and output behavior.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB requires functional similarity or identical goal; these two have different high-level purposes (generic URL content fetching vs. YouTube video URL extraction), so they are considered non-clones.
- 共享行为: Both open a URL connection and read lines using BufferedReader.；Both use try-catch for exception handling.；Both involve string processing (appending or parsing).
- 行为差异: A appends all lines to a buffer; B searches for a specific line and parses it.；A modifies an external StringBuilder; B returns a String and updates a field.；B has progress bar updates; A does not.；Different error handling: A appends URL on exception; B prints error and returns empty string.
- 修正建议: Train with more diverse examples to differentiate generic I/O from specific tasks.；Incorporate dataflow analysis to capture output dependencies and side effects.；Leverage method name semantics and domain context.；Use contrastive learning to reduce sensitivity to common API patterns.

### case_id=1841 FP lexical_or_api_overlap

- 方法: `getVersion` vs `getXML`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads version string from a hardcoded URL, returns the last line read or null on failure.
- B 摘要: Reads XML content from a parameterized URL with request encoding, concatenates all lines, returns the full content or null on various exceptions.
- 静态失败原因: The high token overlap (Jaccard 0.3269) from common boilerplate (URL, BufferedReader, readLine, close, return) causes static embeddings to overestimate similarity, ignoring the semantic differences in parameterization, encoding, and data aggregation.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels these as non-clones because they perform different tasks (getVersion vs getXML) with different signatures, inputs, and outputs; the similarity in boilerplate code is not enough for BCB's functional similarity criteria.
- 共享行为: Both open a URL connection；Both read lines using BufferedReader；Both close the reader；Both return a string or null
- 行为差异: Method A has no parameters; Method B takes two String parameters；Method A uses a hardcoded URL; Method B constructs URL dynamically with encoding；Method A only keeps the last line read; Method B appends all lines；Method B handles multiple specific exceptions; Method A catches generic Exception
- 修正建议: Incorporate method signature and parameter usage into the representation；Use contrastive learning with negative samples that have similar boilerplate but different functionality；Leverage data flow analysis or type information to capture how inputs and outputs differ

### case_id=1842 FP lexical_or_api_overlap

- 方法: `handledRun` vs `loadURL`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Downloads gamedata.xml from a hardcoded URL, checks version, and conditionally overwrites the local gamedata file, updating game database.
- B 摘要: Downloads content from a given URL with optional Basic Authentication, writes it to a temporary file, and updates a status label with file size.
- 静态失败原因: Static BERT/GraphCodeBERT may have been misled by overlapping tokens like 'URL', 'BufferedReader', 'InputStreamReader', 'File', 'write', and similar API usage patterns, while missing the differences in control flow and purpose.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely considered these non-clones because the overall functionality differs (version update vs. generic file loading), and the method signatures, exception handling, and side effects are very different.
- 共享行为: Both open an HTTP connection, read data line by line, and write to a local file.
- 行为差异: Function A conditionally downloads based on version check; Function B always downloads.；Function A writes to a specific game data file; Function B writes to a temporary file.；Function A updates game database; Function B updates a UI label.；Function B uses optional Basic Authentication; Function A does not.
- 修正建议: Use data flow and control flow features to capture differences in logic.；Incorporate method signature and context information.；Train on finer-grained semantic distinctions or use contrastive learning.

### case_id=1843 FN benchmark_preference_bias

- 方法: `main` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `preference_memory_with_manual_audit`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a URL and extracts its entries to the local filesystem.
- B 摘要: Copies a file from source to destination using FileChannel.
- 静态失败原因: Static BERT models rely on token-level and structural similarity, which is low here; they miss high-level semantic categories like file I/O tasks that BCB uses for cloning.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB likely considers both as 'file copy' operations broadly, focusing on the shared I/O pattern rather than specific functionality.
- 共享行为: Both perform file I/O (read from source, write to destination)；Both handle IOException
- 行为差异: A downloads from URL and unzips; B copies a local file；A uses ZipInputStream and BufferedOutputStream; B uses FileChannel.transferTo；A extracts multiple entries; B copies a single file
- 修正建议: Incorporate task-level semantics (e.g., file I/O operations) into representation；Use data flow or API usage patterns to capture broader functional similarity

### case_id=1844 FN partial_functionality

- 方法: `getResourceAsStream` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.2`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Retrieves a resource from a URL with local caching, returning an InputStream.
- B 摘要: Copies a file from source to destination using FileChannel.
- 静态失败原因: Low token Jaccard (0.13) and different method names, combined with distinct control flow and API usage, make it hard for static models to detect the weak I/O pattern similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as file I/O operations that read from a source and write to a destination, fitting a broad Type-3/Type-4 similarity category.
- 共享行为: Both involve opening an input source and writing to an output destination.；Both close resources in a try-finally or try-catch block.；Both handle file I/O operations.
- 行为差异: A fetches from a URL with HTTP caching logic; B copies local files directly.；A returns an InputStream; B returns void.；A uses BufferedInputStream/OutputStream; B uses FileChannel.transferTo.；A includes extensive error handling and logging; B throws IOException.
- 修正建议: Incorporate dataflow analysis to identify I/O operations independent of high-level method names.；Use contrastive learning with positive pairs that share only I/O patterns.；Include API usage embeddings to capture common I/O idioms.

### case_id=1845 FN partial_functionality

- 方法: `doVersionCheck` vs `read`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads version information from a URL by parsing lines for .build and .stablebuild prefixes.
- B 摘要: Opens an InputStream from a URL or file and reads data using an internal read method, returning a status code.
- 静态失败原因: Static BERT likely failed due to low token-level similarity (Jaccard 0.254) and focus on distinct method names and literal strings, missing the structural similarity of the I/O operations.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label these as clones because they share a common pattern of opening a URL input stream, reading, and catching IOException, which could be considered Type-4 (similar functionality) despite different high-level purposes.
- 共享行为: Both open a URL connection and obtain an InputStream.；Both handle IOException with a catch block.；Both perform reading from the input stream.
- 行为差异: Function A reads text lines to extract specific version strings; Function B reads binary data (via BufferedInputStream).；Function A uses BufferedReader; Function B uses BufferedInputStream.；Function A performs a version check and calls another method; Function B returns a status code.；Function B can also read from a local file, not just URL.
- 修正建议: Use API call sequence embeddings (e.g., sequence of InputStream creation, read, close).；Incorporate data-flow analysis to capture the I/O pattern.；Consider subgraph matching for exception handling blocks.

### case_id=1846 FN benchmark_preference_bias

- 方法: `copyFile` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Copies a file using NIO FileChannel transferTo.
- B 摘要: Launches a NexOpen project configuration, involving XML handling, file operations, and property setting.
- 静态失败原因: Static BERT models rely on token overlap and structural patterns; the two functions have very low token Jaccard (0.05), different method names, and completely different control flow and API usage, making them easily distinguishable as non-clones.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as clone due to both methods using file operations and possibly being related to file handling, but this is a stretch and likely an annotation error considering the vast functional difference.
- 共享行为: Both involve file I/O operations
- 行为差异: A is a simple file copy; B is a complex multi-step project launch；A uses FileChannel; B uses various streams and file operations；B involves Eclipse/IDE specific APIs and XML parsing; A does not
- 修正建议: Review BCB annotation for possible error；Improve dataset consistency by removing such unlikely positive pairs

### case_id=1847 FN benchmark_preference_bias

- 方法: `getButtonSonido` vs `modifyApplicationMessage`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Creates a JButton with an action listener that opens a file chooser to select a sound file, copies it to a local directory, sets a sound URL, changes button icon, and plays audio.
- B 摘要: Modifies an internationalization properties file by reading an existing file for a given locale, replacing or appending a message key-value pair, and writing the changes back.
- 静态失败原因: Static BERT/GraphCodeBERT correctly predicted non-clone (0) because it recognized the distinct semantic contexts (GUI sound selection vs. properties file editing) and low lexical overlap (token Jaccard 0.14). It did not fail; this is a BCB annotation error.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider them Type-4 clones due to both involving file-related operations and resource path handling, despite different domains. The annotation could be lenient towards broad functional similarity in resource management.
- 共享行为: Both use file I/O operations (FileInputStream, FileOutputStream, FileReader, FileWriter).；Both handle exceptions with printStackTrace.；Both work with resource paths using getClass().getResource() or similar.
- 行为差异: A is a GUI method setting up a button for sound selection; B is a service method for editing configuration files.；A copies a binary file (sound); B reads and writes text properties files.；A uses JFileChooser and Swing components; B uses BufferedReader and StringBuilder for line-by-line text processing.；A has no parameters; B takes locale, messageName, messageValue as input.
- 修正建议: Re-evaluate BCB label for this pair; consider it a non-clone due to different functionality.；Improve BCB annotation guidelines to avoid overbroad inclusion of file I/O as clone evidence.；Use more stringent semantic similarity criteria in benchmarks.

### case_id=1848 FP partial_functionality

- 方法: `loadMFileViaWeb` vs `getTicketsForQueue`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Loads a MATLAB .m file from a web URL, reads its content line by line, parses it into a UserFunction, and returns it.
- B 摘要: Fetches open tickets for a given queue from a Request Tracker service via HTTP, parses ticket IDs from the response, retrieves each ticket, and returns a list of RTTicket objects.
- 静态失败原因: Static BERT/GraphCodeBERT likely relied on surface-level token overlap: both functions contain tokens like 'BufferedReader', 'line', 'readLine', 'InputStream', 'URL', 'try', 'catch', 'Exception', 'return', 'null', 'while', 'add', 'List', 'new', 'String', 'parse', 'get', 'Http*' etc. The high Jaccard similarity (0.122) combined with similar control flow patterns (read loop, conditional parsing) may have misled the model into predicting clone. The model lacks understanding of domain-specific semantics (MATLAB parsing vs. ticket retrieval).
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB typically labels pairs as non-clone when the core functionality differs, even if there is syntactic overlap in I/O boilerplate. The functions serve entirely different purposes (loading math functions vs. fetching tickets), so BCB correctly labels them as non-clone.
- 共享行为: Both read input line by line using BufferedReader and InputStreamReader.；Both use try-catch blocks for exception handling and close streams in finally or after use.；Both involve creating a URL and opening an input stream from an HTTP connection.；Both return a collection or object that is built from the parsed content.
- 行为差异: loadMFileViaWeb loads a MATLAB script and parses it into a UserFunction; getTicketsForQueue fetches ticket data from a REST API and parses ticket IDs.；loadMFileViaWeb constructs a FunctionParser and calls parseFunction; getTicketsForQueue makes multiple HTTP GET requests and uses JSON? (actually text parsing).；The output types are completely different: UserFunction vs List<RTTicket>.；Error handling differs: one throws MathLibException, the other throws RequestTrackerException and logs errors.
- 修正建议: Incorporate program dependence analysis to distinguish core computation from boilerplate I/O.；Use hierarchical representation that isolates method signatures and return types.；Train with more contrastive examples where syntactic overlap exists but semantic purpose differs.；Add reasoning about external library calls (e.g., FunctionParser vs. HttpGet).

### case_id=1849 FN benchmark_preference_bias

- 方法: `getProjectTreeData` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Fetches project tree data by downloading an XML from a DMS server, parsing it, and extracting project IDs and names.
- B 摘要: Launches an Eclipse launch configuration for a NexOpen project by reading Maven POM files, handling Hibernate dialect, and setting up reverse engineering.
- 静态失败原因: The static model likely correctly identified low lexical and structural overlap, but BCB's annotation may reflect a broader functional similarity that the model missed due to insufficient understanding of project-level context or API usage patterns.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider both as 'XML-driven processing' methods that orchestrate reading and parsing XML, thus labeling them as Type-4 clones despite different domains and purposes.
- 共享行为: Both use DOM parsing to process XML files.；Both involve file I/O operations (reading/writing).
- 行为差异: Function A downloads from a URL and saves to file; Function B reads local project files.；Function A primarily extracts simple data into a 2D array; Function B manages complex Eclipse project configurations and multiple XML files.；Function A is a standalone data retrieval method; Function B is an Eclipse plugin launch handler with side effects on workspace resources.
- 修正建议: Incorporate project-level or task-level semantics to recognize when two functions serve similar roles in different systems.；Use fine-tuning with BCB-specific clone labels that include broad Type-4 similarities.

### case_id=1850 FP boilerplate_overlap

- 方法: `handleHandshake` vs `getNetworkServersIPs`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.98`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Handles Minecraft handshake authentication: validates username, optionally sends login packet or shuts down connection after contacting session server.
- B 摘要: Parses a network server list from a URL: reads lines, extracts IPs after '!SERVERS' marker, returns vector of IP strings.
- 静态失败原因: Static BERT/GraphCodeBERT likely overemphasized lexical and structural overlaps (both use URL, BufferedReader, try-catch) and ignored the distinct semantics and method names, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB considers these non-clones because their overall functionality is entirely different despite some shared I/O boilerplate. The methods belong to different domains (client authentication vs server list retrieval).
- 共享行为: Both use URL to open HTTP connections；Both use BufferedReader to read lines；Both catch exceptions (Exception, MalformedURLException, IOException)
- 行为差异: Different purpose: authentication vs server list parsing；Different input parameters: Packet2Handshake vs String netaddress；Different output: void vs Vector<String>；Different logic: validation and conditional login vs line-by-line parsing with state machine
- 修正建议: Incorporate method name and class context into embeddings；Add dataflow analysis to capture different I/O semantics；Train on more diverse examples to reduce boilerplate sensitivity

### case_id=1851 FP lexical_or_api_overlap

- 方法: `getVersion` vs `checkForUpgrade`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Downloads a version string from a fixed URL and returns it.
- B 摘要: Checks for upgrades by querying a remote server, processing license info, updating database, and updating UI accordingly.
- 静态失败原因: The model was misled by the identical boilerplate code for opening a URL, reading lines, and closing the BufferedReader, which appears in both methods. It overlooked the rest of the method bodies that have entirely different logic and side effects.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely considered these non-clones because the overall functionality (one is a simple version getter, the other is a complex upgrade check with database and UI) is vastly different, despite sharing a token-level URL reading pattern.
- 共享行为: Both open a URL, read lines from the input stream, and close the reader.
- 行为差异: Function A returns a string; Function B is void and performs UI updates.；Function A has no database, license, or UI interactions; Function B heavily uses DB, UI, and complex error handling.；Function A simply reads a single line as version; Function B parses XML-like response, processes arrays, and inserts DB records.
- 修正建议: Train on larger context or incorporate structural information beyond API call sequences.；Use data-flow analysis to detect that the URL reading in one method is the entire behavior, while in the other it is just a small part.；Include method-level documentation or purpose embedding.

### case_id=1852 FN partial_functionality

- 方法: `download` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a resource from classpath to a file after showing a save dialog.
- B 摘要: Provides a cached input stream for a resource, downloading it from a URL if not cached.
- 静态失败原因: Low lexical overlap (Jaccard 0.12) and different method names/signatures likely caused the static model to miss the semantic connection. The model may not capture the abstract resource stream pattern shared between methods.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider them as clones due to shared pattern of reading a resource stream and writing to a file, even though the overall functionality differs significantly. The methods both involve resource acquisition and IO handling, which could be seen as a Type-4 clone.
- 共享行为: Both involve obtaining an input stream from a resource；Both handle closing streams；Both may write to a file
- 行为差异: Method a shows a save dialog; method b does not；Method a writes to a user-specified file; method b caches to a directory；Method b has HTTP conditional GET and caching logic；Method b returns an InputStream; method a returns void
- 修正建议: Include more global context about resource stream handling；Use dataflow analysis to capture stream operations

### case_id=1853 FP lexical_or_api_overlap

- 方法: `readTwitterFead` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.85`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads Twitter user timeline JSON via HTTP GET and returns the raw string.
- B 摘要: Searches Google Images for album art via HTTP GET, parses HTML for image URLs, and adds them to a list.
- 静态失败原因: The static BERT model may have overemphasized the common structural pattern (try-catch, while-readLine) and API tokens (BufferedReader, InputStream), ignoring the different URL destinations, response processing, and method signatures.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the actual functionality (Twitter feed retrieval vs. Google image search) differs significantly, despite similar boilerplate network code. The different outputs and processing logic outweigh the shared HTTP reading pattern.
- 共享行为: Both perform HTTP GET requests.；Both read the response line by line using BufferedReader and InputStreamReader.；Both use try-catch for exception handling.
- 行为差异: A returns the entire response as a string; B extracts specific image URLs from HTML and stores them.；A uses HttpClient (Apache); B uses HttpURLConnection.；A checks for status code 200; B does not check status code.；A has a fixed URL; B constructs a dynamic URL with query parameters.
- 修正建议: Include features like URL domain or method name to distinguish service endpoints.；Incorporate data flow analysis to capture differences in how the response is processed.；Use call graph information to differentiate APIs used (HttpClient vs. HttpURLConnection).；Employ contrastive learning to reduce sensitivity to boilerplate code.

### case_id=1854 FP lexical_or_api_overlap

- 方法: `extractImage` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Extracts an image from an input file (or temporary file if STDIN), applies scaling and transforms, and writes the result to a destination file using a writer.
- B 摘要: Handles GUI action events by opening file choosers for various settings (GRAPHVIZ, IMAGEMAGICK, etc.), storing preferences, and updating UI components.
- 静态失败原因: Static BERT may have been misled by the presence of common keywords like 'File', 'String', 'null', 'if', 'return', 'IOException', and the general structure of file handling and error messages. The model might have overgeneralized based on overlapping syntactic patterns without understanding the domain logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would label these as non-clones (label 0) because they have different purposes, different data structures, and only trivial overlaps like null checks. Even under broad Type-3/4, they are not semantically similar.
- 共享行为: Both use file paths and write to files or store settings.；Both check for null or empty conditions.
- 行为差异: Function A is a single-purpose image extraction method; Function B is a multi-purpose GUI event handler.；Function A uses image processing libraries and writer; Function B uses JFileChooser, preferences, and UI updates.；Function A's flow is sequential with image processing; Function B's flow is event-driven with many conditional branches based on command strings.
- 修正建议: Improve training data to include more diverse examples of GUI vs. file-processing methods.；Enhance model to recognize domain-specific context (e.g., image processing vs. preference management).；Use call-graph or dataflow analysis to differentiate file I/O patterns from event-driven patterns.

### case_id=1855 FN partial_functionality

- 方法: `copyResource` vs `Converter`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource (URL or file) to a destination file using byte streams, throws exception on failure.
- B 摘要: Copies a file with SJIS encoding to a file with UTF-8 encoding using char buffers, catches IOException and prints error.
- 静态失败原因: Static BERT models rely on token overlap and surface form; here token Jaccard is low (0.215), and the APIs differ significantly (URL vs File, byte vs char streams, different exception handling), masking the underlying copy semantics.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB considers both as file copy operations, accepting variations in encoding, error handling, and API usage, treating the overall functionality as similar (Type-4 clone).
- 共享行为: Both copy data from a source to a destination using streams；Both have a read-write loop
- 行为差异: Encoding: binary vs character conversion (SJIS to UTF-8)；Error handling: throws exception vs catches and prints；Buffer: single byte vs char array；Source type: resource (URL or file) vs file paths
- 修正建议: Train on more diverse file copy examples with different encodings and error handling；Use AST or dataflow analysis to capture common copy patterns；Incorporate knowledge of I/O stream hierarchies

### case_id=1856 FN benchmark_preference_bias

- 方法: `main` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Reads a log file and writes filtered lines to a trimmed file based on extraction interval and prefix token.
- B 摘要: Configures and launches a NexOpen project in Eclipse, processing pom.xml files and generating Hibernate reverse engineering files.
- 静态失败原因: The static model correctly predicted non-clone because the token overlap is extremely low (0.071) and the APIs and control flow are entirely different, so it did not consider them similar.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might have labeled them as clones due to both involving file I/O and exception handling, but this is a very shallow similarity and likely an annotation error or overly broad criteria.
- 行为差异: Function A is a simple standalone main method for log filtering; function B is a complex Eclipse launch configuration method.；Function A reads and writes flat text files; function B manipulates XML and project resources with content handlers and callbacks.；Function A uses a basic loop and condition; function B involves assertions, project model access, and external library calls.；Function A has no external dependencies beyond standard Java I/O; function B depends on Eclipse, Hibernate, and NexOpen APIs.
- 修正建议: Improve BCB annotation guidelines to reject such pairs with minimal real similarity.；Alternatively, exclude such pairs from training or evaluation to avoid noise.

### case_id=1857 FP lexical_or_api_overlap

- 方法: `main` vs `copyLogic`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Main method that parses command line, reads a Prolog file, generates adapter classes, and writes them to a JAR file.
- B 摘要: Method that copies a class file from one location to another while managing a state machine.
- 静态失败原因: Static BERT models may rely on surface-level features like file I/O-related tokens (FileInputStream, FileOutputStream, IOException) and possibly similar exception handling patterns despite low token overlap.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would not consider these clones because they have no overlapping functionality. Function A is a main entry for a code generator, while B is a utility method for file copying. No shared intention.
- 共享行为: Both perform file I/O operations
- 行为差异: Function A is a complex multi-step code generation process；Function B is a simple file copy with state management；Function A handles command line arguments and parsing；Function B does not handle any arguments
- 修正建议: Incorporate structural analysis such as program dependency graphs or control flow to differentiate high-level purpose；Improve model's ability to distinguish program purpose from low-level operations

### case_id=1858 FN benchmark_preference_bias

- 方法: `decodeFileToFile` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Decode a Base64 file and write decoded content to another file.
- B 摘要: Launch Eclipse launch configuration for a NexOpen project, setting up Maven profiles and performing reverse engineering.
- 静态失败原因: Static BERT/GraphCodeBERT models rely on token-level representations and may miss the overall semantic mismatch due to long-range dependencies and domain-specific APIs. The low token Jaccard already suggests low similarity, but the model correctly predicted non-clone; the error is in the BCB label.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might have labeled this as clone due to both functions having a common pattern of reading from input, processing, and writing to output, along with similar exception handling and stream closing boilerplate. However, this is a very broad interpretation and likely a mislabel.
- 共享行为: Both involve file I/O operations；Both handle exceptions and use finally blocks for cleanup；Both use input and output streams
- 行为差异: decodeFileToFile is a straightforward file decode/copy; launch performs complex project configuration and profile management；launch interacts with Eclipse workspace, Maven, and external bundles; decodeFileToFile has no such dependencies；launch has conditional logic based on project type; decodeFileToFile is unconditional；launch uses many external library calls; decodeFileToFile only uses standard Java I/O and Base64
- 修正建议: Improve benchmark annotation consistency；For static models, incorporate more robust structural semantics to avoid being misled by boilerplate similarity

### case_id=1859 FN partial_functionality

- 方法: `readIntoList` vs `CheckUrl`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.75`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a URL, parses HTML to extract command names, creates JMenuItem objects, and populates a map with action listeners.
- B 摘要: Opens a URL, reads the first line of the response, and returns it as a string.
- 静态失败原因: Static models like BERT rely heavily on token overlap and structural similarity. Here, the token Jaccard is low (0.2459), and the methods have different names and distinct post-processing code, causing the model to miss the shared boilerplate and functional sub-task.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: None
- 共享行为: Open a URL connection and read data using BufferedReader；Wrap network I/O in try-catch and print stack trace on exception
- 行为差异: Function A parses multiple HTML lines to build UI components, while Function B reads only the first line and returns raw text；Function A modifies a map parameter and sets up action listeners; Function B has no side effects and returns a value
- 修正建议: Use dataflow analysis to detect common sub-patterns like URL opening and reading；Train on clone pairs where only partial functionality (e.g., I/O boilerplate) is shared；Incorporate API sequence embeddings to recognize common I/O patterns

### case_id=1860 FN partial_functionality

- 方法: `getHTML` vs `downloadURLtoString`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads HTML from a URL using HttpURLConnection with custom User-Agent and encoding, optionally writes to file, returns content with line breaks.
- B 摘要: Downloads content from a URL using URL.openStream() and returns content without line breaks.
- 静态失败原因: Low token overlap (Jaccard=0.26) and different API usage (HttpURLConnection vs openStream) and additional file-writing logic in A may have led the model to miss the functional similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often considers Type-3/Type-4 clones where core functionality is similar despite API or detail differences; both functions aim to download a URL to a string.
- 共享行为: Both fetch textual content from a URL；Both use BufferedReader and InputStreamReader；Both read lines and append to a string builder
- 行为差异: A appends "\r\n" after each line, B does not；A optionally writes to file, B does not；A catches and prints exceptions, B throws IOException；A uses specified encoding, B uses default
- 修正建议: Incorporate higher-level semantic embeddings (e.g., API call intent)；Use data-flow analysis to match core read-append loop

### case_id=1861 FN partial_functionality

- 方法: `main` vs `forBundle`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a URL and extracts its zip entries to files.
- B 摘要: Reads template files from an OSGi bundle, creates a new zip archive, and reinstalls the modified bundle.
- 静态失败原因: Static models rely on explicit token overlap and structure; the low Jaccard similarity (0.137) and different method signatures (main vs. forBundle) led to a non-clone prediction, missing the broad zip-processing functionality.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider the common zip traversal and stream copying pattern as functionally similar, labeling it a Type-4 clone despite differing overall goals.
- 共享行为: Both process zip entries using standard Java zip APIs；Both iterate over entries in a zip input/output stream；Both use URL.openStream() to read data
- 行为差异: A extracts zip entries to disk; B creates a new zip archive from bundle contents；A uses ZipInputStream; B uses ZipOutputStream；B includes complex bundle management (uninstall, install, refresh) not present in A；A has no condition for entry inclusion; B applies a manipulator filter
- 修正建议: Incorporate structural abstraction of zip/file I/O patterns；Use a model that captures partial functional overlap (e.g., long-range dependencies for common algorithms)；Add context about the surrounding system (e.g., OSGi bundle manipulation) to disambiguate

### case_id=1862 FP dataflow_blindspot

- 方法: `str2md5` vs `perform`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_with_trace`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Computes MD5 hash of input string and returns hex representation.
- B 摘要: Processes an HTTP request to classify a concept and forwards to success or failure page.
- 静态失败原因: The static BERT model likely overfit to superficial patterns like try-catch and string manipulation, misinterpreting common Java idioms as evidence of similarity despite fundamentally different high-level tasks.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 dataflow_trace_and_outputs。
- BCB 偏好解释: BCB labels as non-clones because there is no functional overlap: one is a cryptographic utility, the other is a Struts action with complex business logic.
- 共享行为: Both use strings and exception handling
- 行为差异: Function A is a pure hash function with no side effects; Function B is a web request handler with session and I/O；Function A returns a string; Function B returns an ActionForward object
- 修正建议: Improve model with dataflow-sensitive features；Use contrastive learning to distinguish functions with similar APIs but different intents；Incorporate task-specific fine-tuning on method bodies

### case_id=1863 FN partial_functionality

- 方法: `process` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Processes a template (FreeMarker, XSLT, or copy) to generate an output file in a destination directory based on template destination type.
- B 摘要: Builds an editable website by applying XSLT transformation to pages from a site model and writing transformed HTML files.
- 静态失败原因: Static BERT models rely on token overlap and structure, which is low (Jaccard=0.102), and miss the higher-level functional pattern of 'read-transform-write'. Different method names, parameter lists, and control flow (switch vs loop) further reduce similarity in learned embeddings.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considers both as belonging to the 'code generation' or 'template processing' category, where the core functionality of reading input, transforming, and writing output is similar despite different specific steps, thus a Type-3/Type-4 clone.
- 共享行为: Both read input from files (templates or XML).；Both perform transformation (template engine or XSLT).；Both write output files to a specified directory.；Both handle file path construction and error handling.
- 行为差异: Function A supports multiple template types (FreeMarker, XSLT, copy), while B only uses XSLT.；A processes a single template per call, while B iterates over multiple pages.；A determines output path based on template destination, while B constructs path from page title.；B includes complex post-processing (e.g., gadget replacement) not present in A.
- 修正建议: Incorporate dataflow analysis to identify common patterns like FileInputStream, Transformer, FileWriter.；Use API-based clustering to detect shared high-level operations.；Enhance model with source code summarization or graph representations that capture overall purpose.

### case_id=1864 FN partial_functionality

- 方法: `checkInputStream` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads an InputStream and compares its bytes to a given byte array.
- B 摘要: Fetches a remote resource via URL, caches it locally, and returns a FileInputStream to the cached file.
- 静态失败原因: Static BERT/GraphCodeBERT often rely on lexical overlap and structural similarity; here token Jaccard is low (0.076) and control flow differs greatly, causing the model to miss the high-level I/O pattern similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider these clone since both perform stream copying/reading, a common I/O pattern that fits broad Type-4 (functionally similar) annotations despite different overall purposes.
- 共享行为: Both involve reading from an InputStream.；Both copy stream data to a destination (ByteArrayOutputStream or file).
- 行为差异: Function A is a simple test helper that compares stream content; function B is a complex resource caching method.；Function A returns void; function B returns an InputStream.；Function B includes HTTP connection, caching logic, and extensive error handling; function A does not.；Function A compares byte arrays; function B only copies and returns a stream.
- 修正建议: Enhance model with data-flow analysis to detect common I/O patterns.；Include more diverse training pairs that cover broad Type-4 clones with low token overlap.；Use abstract syntax tree (AST) or program dependency graph (PDG) to capture functional similarities unrelated to token overlap.

### case_id=1865 FN partial_functionality

- 方法: `addDataFromURL` vs `addIDs`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads all lines from a URL and appends them to a text buffer.
- B 摘要: Fetches metabolite data from a web service by name, parses HTML to extract IDs and scores, and populates a PeakListRow object with multiple fields.
- 静态失败原因: The token Jaccard similarity is low (0.132), and the model likely focused on the larger dissimilar portions, leading to a non-clone prediction. It did not recognize the trivial shared reading pattern as sufficient for cloning.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as 'read from URL' patterns, but the functional difference is too large. Possibly the annotators over-emphasized the shared boilerplate pattern.
- 共享行为: Both open a URL stream using BufferedReader and read lines until null.
- 行为差异: Function A simply appends raw text to a buffer; Function B parses HTML to extract structured data and sets multiple fields on a PeakListRow object.；Function A returns void; Function B returns an integer score.；Function A has minimal exception handling (print and append); Function B logs IOException and returns 0.；Function B contains complex conditional logic for different ID types; Function A has none.
- 修正建议: Use code structure analysis to capture the overall task; incorporate dataset-specific clone criteria training.

### case_id=1866 FN benchmark_preference_bias

- 方法: `addQDInformation` vs `invoke`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Reads a QD information file (local or remote) to update internal project information dates and values.
- B 摘要: Sends an HTTP POST request to invoke a remote service method, reads JSON response, and returns deserialized result.
- 静态失败原因: Low token overlap (0.1585) and distinct domains led static BERT to correctly predict non-clone.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: The BCB label of 1 is likely a misclassification; no clear Type-3/Type-4 similarity beyond generic I/O boilerplate.
- 共享行为: Both use BufferedReader to read lines from an input stream；Both have try-catch blocks for IOException handling；Both parse string data from the read lines
- 行为差异: Data source: local file vs HTTP remote service；Output: updates internal state vs returns deserialized object；Error handling: one swallows exceptions, the other may retry on timeout；One uses file I/O, the other uses HTTP POST with JSON
- 修正建议: Re-label this pair as non-clone in BCB if it is indeed a misannotation.；Ensure annotation guidelines for semantic clones are strictly followed.

### case_id=1867 FP boilerplate_overlap

- 方法: `readTwitterFead` vs `doRawRequest`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a fixed Twitter timeline URL via HTTP GET using Apache HttpClient and returns the response body as a string, with error logging.
- B 摘要: Performs an HTTP POST request with given data using java.net URLConnection and returns the response body as a string, throwing IOException.
- 静态失败原因: Static BERT methods rely on token overlap; both functions share boilerplate code like BufferedReader, StringBuilder, and while loop, causing false positive despite low Jaccard.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels as non-clone because functions differ in HTTP method, library usage, and error handling, which are considered distinct functionalities.
- 共享行为: Both make an HTTP request and return the response body as a string.
- 行为差异: Function A uses HTTP GET, while B uses HTTP POST.；A uses Apache HttpClient, B uses java.net URLConnection.；A handles HTTP status codes and logs errors; B throws exceptions.；A has no request body; B writes postData to the request.
- 修正建议: Add semantic understanding of HTTP methods and error handling.；Incorporate type-aware information about libraries used.

### case_id=1868 FN boilerplate_overlap

- 方法: `storeImage` vs `modifyApplicationMessage`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Stores an uploaded image file to a date-based directory, optionally resizing and returning the relative path.
- B 摘要: Modifies a properties file for a given locale by updating or adding a key-value pair, copying the English file if the locale file doesn't exist.
- 静态失败原因: Static BERT models (e.g., CodeBERT, GraphCodeBERT) primarily rely on token overlap and surface-level lexical features; the low Jaccard similarity (0.11) and different method names/domains led to a non-clone prediction, missing the structural commonality in file handling.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may have labeled this as a clone due to the high-level similarity in file I/O patterns (existence check, stream copying, exception handling) even though the domain logic differs, reflecting a broad Type-3/Type-4 annotation preference.
- 共享行为: Both check if a file exists and create it if not.；Both read from an InputStream and write to an OutputStream.；Both handle exceptions with try-catch.；Both use java.io.File and file I/O utilities.
- 行为差异: A stores an image file and performs optional resizing; B modifies a properties file by parsing and updating key-value pairs.；A returns a String path; B is void.；A uses calendar-based folder naming and image resizing; B handles locale-specific property file management.；A relies on configuration properties; B copies an English file as a template.
- 修正建议: Incorporate structure-aware features (e.g., AST paths, control flow graphs) to capture boilerplate patterns.；Use contrastive learning or data augmentation to improve generalization to cross-domain I/O patterns.；Consider functional similarity at higher granularity (e.g., entire method-level vs. subgraph-level).

### case_id=1869 FP lexical_or_api_overlap

- 方法: `hash` vs `perform`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Computes SHA-1 hash of a string and returns hex representation.
- B 摘要: Handles an HTTP request to classify a concept, interacts with a web service, and manages session attributes.
- 静态失败原因: The static model may have overgeneralized from common API usage or been misled by the presence of similar keywords, despite very low token overlap.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB correctly identifies these as non-clones due to entirely different functionalities: one is a utility method, the other is an action handler.
- 共享行为: Both use exception handling；Both involve string manipulation
- 行为差异: Function A is a pure hashing function; Function B is a complex web controller；Different inputs and outputs；Different algorithms and purposes
- 修正建议: Improve model's ability to distinguish based on functional purpose rather than superficial features；Increase training data with diverse non-clone pairs；Incorporate control flow and data flow analysis

### case_id=1870 FN partial_functionality

- 方法: `getFile` vs `save`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies SOAP address location, and saves to a temporary file.
- B 摘要: Writes a byte array to a file, creating parent directories if needed.
- 静态失败原因: The model likely focused on low lexical overlap and differences in structure (length, exception handling), missing the abstract shared I/O behavior.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider these clones because both perform file output operations and handle streams, falling under a broad category of 'file output' or 'stream I/O'.
- 共享行为: Both write binary data to a file using output streams.；Both handle stream closure.
- 行为差异: getFile downloads from network, parses XML, and modifies elements; save just writes predefined bytes.；getFile has complex error handling and file existence check; save is simpler.；getFile returns the file path; save returns the number of bytes copied.
- 修正建议: Incorporate data flow analysis to capture stream handling patterns.；Use higher-level API call embeddings (e.g., IOUtils, FileOutputStream).

### case_id=1871 FP long_range_semantics

- 方法: `perform` vs `getPrefsKey`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `static_summary_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Processes an HTTP request to classify a concept by sending XML data to a URL and parsing the response.
- B 摘要: Computes an MD5 hash of a given string and returns the hex-encoded result.
- 静态失败原因: The static model likely did not understand the overall semantics due to the large length of function A (truncation) and relied on superficial patterns like try-catch and string manipulation, leading to a false positive.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB typically treats functions with completely different functionality and structure as non-clones; there is no semantic similarity even at a high level.
- 共享行为: Both are Java methods with try-catch blocks.
- 行为差异: Function A handles HTTP requests and session management; function B is a pure utility for hashing.；Function A has extensive logic for role handling and XML building; function B is simple and deterministic.；Function A returns an ActionForward; function B returns a String.
- 修正建议: Handle long code sequences better, e.g., by chunking or using hierarchical representations.；Incorporate structural features like control flow graphs to differentiate methods.

### case_id=1872 FN benchmark_preference_bias

- 方法: `modifyApplicationMessage` vs `trainClassifier`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Modifies a key-value pair in a locale-specific properties file, creating the file if necessary by copying from an English file.
- B 摘要: Trains a classifier by executing an external command with arguments and file paths, copying output streams.
- 静态失败原因: Low token overlap (Jaccard 0.113) and different API usage, but BCB label suggests a higher-level similarity that static models miss.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider them clones based on broad Type-4 semantic similarity, viewing both as 'modifying resources through external interactions', but this is tenuous.
- 共享行为: Both involve file I/O operations；Both use try-catch for exception handling
- 行为差异: Function A reads and writes a properties file, while B executes an external process；Function A updates key-value mappings, B trains an ML model；Different domains: localization vs. machine learning
- 修正建议: Improve model to capture high-level semantic intent beyond lexical overlap；Consider task-specific behavior such as data modification vs. external command execution

### case_id=1873 FP partial_functionality

- 方法: `readTwitterFead` vs `importRoles`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Retrieves a Twitter feed from a fixed URL and returns the raw JSON response as a string.
- B 摘要: Imports roles by downloading XML from a given URL, parsing each role element, and returning a list of RoleName objects.
- 静态失败原因: Static BERT models may overemphasize lexical and structural overlaps (e.g., try-catch, BufferedReader, while loop, StringBuilder) while missing semantic differences in types, purpose, and data processing.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB typically does not consider functions as clones if they have different return types, different input parameters, and distinct processing logic despite sharing a common boilerplate pattern.
- 共享行为: Establish HTTP connection to a URL；Read response line by line using BufferedReader；Build a string buffer from the lines；Handle IOException
- 行为差异: A uses HttpClient; B uses URL.openStream()；A returns a String; B returns ArrayList<RoleName>；A has fixed URL; B takes URL as parameter；B parses specific XML tags (</RoleName>); A does no parsing
- 修正建议: Include negative examples with similar boilerplate but different semantics in training；Incorporate type information and method signatures into the model；Use AST-based features to capture structural differences beyond token sequences

### case_id=1874 FP lexical_or_api_overlap

- 方法: `scrapeForIsbns` vs `importSequences`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Scrapes a URL for ISBN-10 patterns using regex, with retry logic on connection failures, and stores found ISBNs.
- B 摘要: Imports genetic sequences from a URL by parsing FASTA-like format, extracting names and sequences into lists.
- 静态失败原因: The static BERT/GraphCodeBERT model likely overfitted on surface-level API usage (e.g., opening URL streams, reading lines, handling IOExceptions) and boilerplate patterns, ignoring the distinct domain-specific logic (regex vs. FASTA parsing). The token Jaccard similarity is low, but the lexical overlap of common Java I/O patterns may have misled the model.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels these as non-clones because the overall functionality is completely different: one scrapes book ISBNs, the other imports genetic sequences. Even under broad Type-3/Type-4 similarity, the core purpose and logic diverge significantly.
- 共享行为: Both open an InputStream from a URL and read data line-by-line or character-by-character；Both handle I/O exceptions (IOException, MalformedURLException)；Both use loops to process input data
- 行为差异: Function A extracts ISBNs using regex; Function B parses genetic sequences using a custom ImportHelper；Function A has retry logic for ConnectException; Function B does not；Function A returns an integer count; Function B is void and stores results in lists；The input parsing logic is entirely different (regex vs. tokenizer and helper methods)
- 修正建议: Train with more negative examples that share API patterns but have different core semantics；Incorporate structural differencing or control-flow analysis to distinguish dissimilar logic；Use contrastive learning to push representations apart when high-level functionality differs；Augment models with domain-specific embeddings or task-focused attention

### case_id=1875 FP boilerplate_overlap

- 方法: `setBundleInfoName` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a URL containing key-value pairs and updates bundle names in a list based on matching symbolic names.
- B 摘要: Performs a Google image search by fetching HTML, extracting image URLs, and displaying the first image in a GUI.
- 静态失败原因: The model likely over-fitted to lexical overlap of common Java boilerplate (URL, BufferedReader, try-catch) and failed to capture the distinct semantic purposes indicated by method names, return types, and processing logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would not consider these clones because the core functionality is entirely different (bundle info update vs. image search) despite sharing trivial I/O patterns.
- 共享行为: Both open a URL and read from it using BufferedReader.；Both handle exceptions from I/O operations.；Both use a try-catch block.
- 行为差异: Function A parses lines with key=value format; Function B parses HTML for image URLs.；Function A updates a list of BundleInfo objects; Function B populates a global list and updates a GUI.；Function A returns a boolean; Function B is void.；Function A uses printStackTrace; Function B shows a dialog for errors.
- 修正建议: Incorporate method name embeddings and return type information.；Use dataflow analysis to distinguish variable usage patterns.；Train on more diverse examples of non-clones with similar I/O structures.

### case_id=1876 FN benchmark_preference_bias

- 方法: `extractFile` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Copies a file from input path to output path using a buffer.
- B 摘要: Launches a NexOpen project configuration, processing multiple XML files and setting up Hibernate reverse engineering.
- 静态失败原因: The static BERT model likely learned from low token overlap and distinct semantic contexts, correctly predicting non-clone. The model did not find any shared behavior beyond generic I/O, which is insufficient for clone detection. The BCB label appears to be a false positive in this case.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: The BCB annotation may have considered the presence of similar stream I/O operations, or it may be an annotator error. Given the low Jaccard similarity and distinct purposes, the clone label seems incorrect.
- 共享行为: Both involve reading from an InputStream and writing to an OutputStream at some point.
- 行为差异: Function A is a simple file copy utility; Function B is a complex project launch configuration handler with many steps including XML processing, property setting, and job scheduling.；Function A has no dependencies on Eclipse or Hibernate; Function B heavily depends on Eclipse IDE and Hibernate APIs.；Function A operates on two file paths; Function B operates on ILaunchConfiguration, IProject, and involves multiple resources.
- 修正建议: Review BCB annotations for this pair to confirm if it should be a clone. Increase threshold for partial similarity when only generic I/O operations are shared.；Use dataflow analysis to identify that the I/O operations in Function B are only a small part of its overall behavior, not the main functionality.

### case_id=1877 FN benchmark_preference_bias

- 方法: `cpFile` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Copy a file to a target directory with options for replacing and buffer size, automatically handling name collisions.
- B 摘要: Launch a NexOpen project configuration for Hibernate reverse engineering, involving POM file processing and property setting.
- 静态失败原因: Static model likely correctly predicted non-clone; the BCB label is probably noise or annotation error.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB likely mislabeled due to superficial similarity in using InputStream/OutputStream and exception handling, which are common boilerplate patterns.
- 共享行为: Both involve file I/O operations
- 行为差异: Function A is a simple file copy utility；Function B is a complex Eclipse launch configuration setup；Function A has no dependency on Eclipse or project structure；Function B is tightly coupled with Eclipse workspace and NexOpen framework
- 修正建议: Review and correct BCB annotation for this pair；Consider removing pair if annotation is clearly erroneous

### case_id=1878 FN benchmark_preference_bias

- 方法: `getButtonSonido` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Creates a GUI button that opens a file chooser to select a sound file, copies it to a local directory, and updates the button icon.
- B 摘要: Launches a NexOpen project configuration by processing Maven POM files, setting Hibernate dialect, and installing the project in an Eclipse environment.
- 静态失败原因: Static BERT correctly identified non-clone due to very low token overlap (Jaccard 0.052) and completely different API usage and domain, leading to high representation distance.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled these as clones due to the presence of anonymous inner classes and file handling patterns, or due to benchmark annotation noise.
- 共享行为: Both involve file I/O operations (file copying vs. file existence checks and resource copying).
- 行为差异: Function A is a GUI event handler for sound file selection; Function B is a project launch configuration handler.；Function A uses Swing components (JButton, JFileChooser); Function B uses Eclipse/EMF APIs (ILaunchConfiguration, IProject, IFile).；Function A copies a file to a local directory; Function B processes XML documents and sets persistent properties.；Function A deals with audio files; Function B deals with Maven and Hibernate configuration.
- 修正建议: Re-evaluate BCB annotation for this pair; consider removing or correcting the clone label.；Improve benchmark quality by ensuring functional equivalence or strong similarity before labeling as clone.

### case_id=1879 FP boilerplate_overlap

- 方法: `getRequestContent` vs `run`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads the first line from a URL and returns it as a string.
- B 摘要: Reads all lines from a URL, parses them into instance variables, handles errors, and notifies listeners.
- 静态失败原因: The static BERT model likely over-relied on the overlapping API calls (URL, BufferedReader, InputStreamReader) and the general structure of opening a connection and reading lines, while ignoring the different control flow (single line vs. loop), error handling, and side effects. The low token Jaccard (0.1039) suggests the similarity is mainly in boilerplate code.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would likely label this as non-clone because the functions have distinct purposes: one is a simple one-line fetcher, the other is a multi-line parser with error handling and event notification. Despite common I/O patterns, the core functionality differs significantly.
- 共享行为: Both open a URL connection and read lines using BufferedReader.；Both close the reader after reading.
- 行为差异: A reads only the first line; B reads all lines.；A returns the line; B updates instance variables (version, url, information).；A throws Exception, B catches IOException and sets error flags.；A explicitly disconnects; B does not.
- 修正建议: Incorporate structural features like control flow graphs or data flow to distinguish between simple reads and loops.；Enhance training data to include more negative pairs with similar boilerplate but different logic.；Use models that can capture exception handling and side effects.

### case_id=1880 FN partial_functionality

- 方法: `downloadURLtoString` vs `testNetworkHTTP`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a URL's content as a string by reading lines into a StringBuffer.
- B 摘要: Performs a network test by connecting to multiple hardcoded URLs and reading response lines, discarding them.
- 静态失败原因: The static model likely failed due to low token overlap (Jaccard 0.1719), different method names, and contextual differences (A is a utility, B is a test with multiple URLs and logging), causing the model to overlook the shared IO pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely labels this as a clone because the core pattern of opening a URL and reading lines is semantically similar, representing a Type-3 near-miss clone despite different purposes and minor structural changes.
- 共享行为: Both open a URL connection and read lines using BufferedReader；Both use while loops to iterate through lines；Both involve HTTP communication
- 行为差异: A returns the concatenated string; B discards all lines and returns nothing；A takes a URL parameter; B uses hardcoded URLs；B includes logging, multiple connections, and exception handling; A does not
- 修正建议: Enhance model to recognize common code patterns (e.g., URL reading loop) irrespective of surrounding context；Incorporate data-flow analysis to capture shared functionality despite different variable names；Train on more diverse clone pairs that include partial functional similarity

### case_id=1881 FN partial_functionality

- 方法: `main` vs `unzip`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a KMZ from a URL and extracts all entries to current directory.
- B 摘要: Unzips a given File to a target directory with logging and error handling.
- 静态失败原因: Low token Jaccard similarity (0.207) due to different method names, parameter lists, and added logging/error handling in B. Static models rely on surface form overlap.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels pairs as clones if they share the same core algorithm (zip extraction), despite differences in I/O sources, error handling, and auxiliary code.
- 共享行为: Iterate over zip entries；Write each entry's contents to a file
- 行为差异: A reads from URL; B reads from File；A outputs to current directory; B outputs to target directory and creates parent directories；A has minimal error handling; B has extensive error handling and logging；A uses ZipInputStream; B uses ZipFile.getInputStream for each entry
- 修正建议: Include dataflow analysis to capture shared zip extraction logic.；Use a clone detector that focuses on structural or behavioral similarity rather than lexical overlap.；Train with more examples of partial functionality clones.

### case_id=1882 FP lexical_or_api_overlap

- 方法: `readVersion` vs `loadURL`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a version resource from classpath and parses version, revision, and date fields.
- B 摘要: Connects to a URL with optional authentication, downloads content to a temporary file, and updates a status label.
- 静态失败原因: The model likely relied on overlapping API usage (BufferedReader, InputStreamReader, readLine) and similar control flow, missing the semantic differences in data source, processing, and output.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely annotated as non-clone because the functions serve different purposes (config parsing vs. file downloading) and have different inputs, outputs, and side effects, with no partial functionality overlap.
- 共享行为: Both use BufferedReader and InputStreamReader to read lines from an input stream；Both handle IOException via printStackTrace or throws；Both use openStream or openConnection to obtain an input stream
- 行为差异: readVersion reads from a static classpath resource; loadURL connects to a remote URL with optional authentication；readVersion parses key-value lines and updates instance variables; loadURL writes all content to a temp file and updates a UI label；loadURL has additional logic for authentication, file size calculation, and status updates; readVersion does not
- 修正建议: Include more context features such as variable types and method signatures；Incorporate data flow analysis to distinguish different data sources and sinks；Train on more negative examples with similar API patterns but different semantics

### case_id=1883 FN benchmark_preference_bias

- 方法: `bootKernel` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Boots a kernel on Android by loading assets, reading configuration properties, copying asset files to sdcard, and invoking a kernel boot sequence.
- B 摘要: Launches a NexOpen project in Eclipse by verifying project structure, parsing pom.xml files, setting Hibernate dialect, and scheduling an install action.
- 静态失败原因: Static BERT likely relied on surface-level code patterns like try-catch, logging, and Properties usage, missing domain-specific APIs and semantic differences. The model correctly predicted non-clone, but BCB label is questionable.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have considered both as 'initialization or configuration loading' functions that involve reading properties and handling resources, but the context and intent differ completely.
- 共享行为: Both read properties from files (Properties.load, configuration attributes)；Both handle exceptions with logging；Both use try-catch blocks
- 行为差异: BootKernel copies asset files to sdcard using FileChannels; Launch processes XML and generates reverse engineering files；BootKernel dynamically loads a kernel class; Launch uses Eclipse/EMF APIs for project configuration；BootKernel is Android-specific; Launch is Eclipse-plugin-specific for Maven projects
- 修正建议: Re-evaluate BCB annotation for this pair to correct potentially erroneous clone label；Incorporate domain-aware features or API context in clone detection models；Use higher-level semantic representations from code summarization or documentation

### case_id=1884 FN benchmark_preference_bias

- 方法: `sendErrorMessage` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Sends an error message by zipping a log file and emailing it to technical recipients.
- B 摘要: Builds a site for editing by reading XML, transforming content, and writing output files.
- 静态失败原因: The static model correctly captured low token overlap and different method names/purposes, predicting non-clone; the BCB label appears to be an outlier or too broad.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may label them as clones due to superficial structural similarities (file I/O, loops, buffer usage, exception handling) under a very broad Type-4 (semantic) interpretation, even though their core functionalities are unrelated.
- 共享行为: Both read from files using InputStream/Reader and write to files.；Both use buffers of size 8192 for reading data.；Both handle exceptions with try-catch blocks.
- 行为差异: Function A sends an email with a zipped attachment; Function B writes transformed HTML/XML pages to the filesystem.；Function A is a simple error-reporting method; Function B is a complex multi-step website generation method.；Their input parameters and return types are entirely different.
- 修正建议: Increase threshold for semantic similarity beyond surface I/O patterns.；Focus on functional intent and data flow rather than generic structural patterns.；Re-evaluate BCB annotations to remove overly broad Type-4 clones.

### case_id=1885 FP long_range_semantics

- 方法: `readData` vs `copyFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.99`
- 推荐路线: `static_summary_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Parses comma-separated strings into multiple sets and a map, likely initializing internal data structures.
- B 摘要: Copies a file from source to destination, creating parent directories if needed.
- 静态失败原因: The model likely focused on common boilerplate (try-catch, file paths) and missed the larger semantic difference due to long code with truncation.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB expects semantically similar functions; here, the core functionality differs entirely (data structure initialization vs. file copying), so they are non-clones.
- 共享行为: Both involve I/O operations (file reading in A, file copying in B)；Both use try-catch for exception handling
- 行为差异: A builds data structures from tokenized strings; B transfers bytes between files；A involves complex parsing logic and validation; B is a straightforward copy；A uses StringTokenizer; B uses FileInputStream/FileOutputStream
- 修正建议: Use whole-function embeddings to capture global semantics；Incorporate dataflow analysis to distinguish between data parsing and file copying；Train with contrastive examples that share boilerplate but differ in purpose

### case_id=1886 FP lexical_or_api_overlap

- 方法: `getWebByUrl` vs `executePost`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Downloads a web page from a URL, saves it to a file, and recursively processes embedded URLs.
- B 摘要: Sends an HTTP POST request with parameters and returns the response body as a string.
- 静态失败原因: Static BERT-like models may over-rely on token overlap and API sequence similarity. Both functions use common APIs (URL, URLConnection, BufferedReader) and have a similar control flow (open connection, read lines, handle exceptions), leading the model to ignore the fundamental semantic differences in method signature, return type, and core logic (file writing vs. POST request).
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels functions that have different input/output signatures and different core tasks as non-clones, even if they share some low-level I/O patterns.
- 共享行为: Open a URL connection；Read from an InputStream via BufferedReader；Accumulate lines in a StringBuffer；Handle exceptions with try-catch
- 行为差异: A writes output to a file, B returns the response as a string；A recursively crawls embedded URLs, B does not；A uses URLConnection, B uses HttpURLConnection with POST method and headers；B sends POST parameters, A does not
- 修正建议: Incorporate method name and signature (return type, parameters) as features；Use dataflow analysis to track different sinks (file vs. return) and operation types；Apply contrastive learning to distinguish similar-looking but semantically different methods

### case_id=1887 FN partial_functionality

- 方法: `decodeFileToFile` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Decodes a Base64-encoded file and writes the decoded data to an output file.
- B 摘要: Builds a website for editing by processing XML pages, applying transformations, and writing the output to files.
- 静态失败原因: Static BERT/GraphCodeBERT likely relied on lexical and high-level semantic similarity, which is low due to different methods and parameter lists, missing the shared structural I/O pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider the common pattern of stream-based buffered I/O with exception handling as sufficient for a Type-3/4 clone, despite differences in overall functionality.
- 共享行为: Both involve reading from an InputStream and writing to an OutputStream using a buffered loop；Both use try-catch-finally for resource management and exception handling
- 行为差异: A performs simple Base64 decoding; B performs complex XML transformation and site generation；A writes to a single output file; B writes multiple files based on page processing；A returns a boolean success flag; B is void and throws various exceptions
- 修正建议: Incorporate dataflow analysis to detect streaming patterns；Use graph-based models that capture structural similarities like read-write loops；Include training examples where similar boilerplate indicates partial clones

### case_id=1888 FP long_range_semantics

- 方法: `copy` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `static_summary_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: A utility method that copies a file using FileChannel transferTo.
- B 摘要: An action listener that handles several GUI commands (e.g., GRAPHVIZ, IMAGEMAGICK) by opening file choosers and updating preferences.
- 静态失败原因: The model likely over-predicted due to superficial API overlap (e.g., both use File, IOException) or a pattern of try-catch, but token Jaccard is low; the model may have missed the overall semantics because of the length of function b.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB labels this as non-clone because the functions have completely different purposes (file copy vs. GUI action handling) and no overlapping functionality, even under broad Type-4 similarity.
- 行为差异: Function a performs file I/O copying; function b handles GUI events and preference saving.；Function a is a static utility with no side effects besides file copy; function b modifies UI and preferences.；Function a uses FileChannel; function b uses JFileChooser and Swing components.；Function a is concise; function b is lengthy with multiple conditional branches.
- 修正建议: Improve long-range dependency modeling in the model.；Incorporate structural information (e.g., control flow graphs) to better distinguish file I/O from GUI event handling.；Use token-level cross-attention with more focused context windows.

### case_id=1889 FN boilerplate_overlap

- 方法: `testNetworkHTTP` vs `retrieveTemplate`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.65`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Makes multiple HTTP GET requests to various URLs and discards the response content, logging and disconnecting.
- B 摘要: Retrieves a web page from a blog URL, reading all lines into a string, caches it, and returns it.
- 静态失败原因: Static methods like GraphCodeBERT rely heavily on token-level similarity and Jaccard coefficient; low token overlap (0.159) led to non-clone prediction, failing to capture the high-level structural pattern that BCB considers clone-worthy.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may consider this a clone due to shared boilerplate pattern of opening a URL, reading lines with BufferedReader, even though overall functionality differs. The label indicates broad Type-3/4 partial similarity.
- 共享行为: Both use URL objects to open HTTP connections and read lines via BufferedReader.
- 行为差异: A makes multiple requests and discards data; B makes a single request, accumulates data into a string, caches, and returns.；A is void; B returns a string.；A uses HttpURLConnection explicitly; B uses URL.openStream().
- 修正建议: Incorporate structural similarity features that capture common patterns like URL fetching and line reading.；Use graph-based or program flow analysis to identify functional similarity in I/O operations.

### case_id=1890 FN lexical_or_api_overlap

- 方法: `login` vs `doVersionCheck`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.7`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends HTTP POST with credentials to login to LOLA service and returns session ID.
- B 摘要: Performs a version check by reading a version file from URL, parsing version and build numbers, and notifying user about updates.
- 静态失败原因: High lexical overlap (URL, BufferedReader, readLine, try-catch) masked the semantic difference in purpose; the model over-relied on shared API tokens and ignored distinct data flow and intent.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB might consider both as network I/O tasks with similar code structure, but the functional difference is large; labeling as clone is inconsistent with typical BCB standards.
- 共享行为: Open a URL connection；Read input stream with BufferedReader；Parse lines from response
- 行为差异: Different HTTP methods (POST vs GET)；Different data sent (credentials vs none)；Different output (session ID vs notification)；Different exception handling (print vs GUI error)
- 修正建议: Incorporate data flow analysis to distinguish different action sequences；Use context-aware embeddings that capture the purpose (e.g., login vs version check)；Add supervision on method name and comment semantics

### case_id=1891 FP other

- 方法: `getSHADigest` vs `perform`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.99`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Computes SHA-1 hash of a password and returns it as a base64-encoded string with '{SHA}' prefix.
- B 摘要: Handles an HTTP request for classifying concepts in a web application, involving session validation, form parameter extraction, XML data construction, and communication with external service.
- 静态失败原因: Static BERT/GraphCodeBERT models may rely on token-level patterns or API usage. Here, despite low token Jaccard similarity (0.044), the model may have been misled by common constructs like String manipulation or try-catch blocks that appear in both, leading to a false positive.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB labels this as non-clone because the two functions have entirely different purposes and code structure. Even under broad Type-3/Type-4 allowance, there is no functional overlap.
- 共享行为: No significant shared behavior beyond being Java methods.
- 行为差异: Function A performs cryptographic hashing; Function B handles HTTP request processing.；Function A is a static utility with simple control flow; Function B is an action method with complex control flow including multiple conditionals and loops.；Function A returns a String; Function B returns an ActionForward.；Function A uses MessageDigest and Base64; Function B uses HttpSession, ActionMapping, URLConnection, etc.
- 修正建议: Improve model to focus on overall functionality rather than superficial lexical patterns.；Incorporate dataflow or program dependency information to distinguish different computational tasks.

### case_id=1892 FP other

- 方法: `main` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.98`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: The main method writes and reads text to/from a file using FileChannel and ByteBuffer with different encodings, demonstrating file I/O operations.
- B 摘要: The actionPerformed method handles GUI events to set configuration preferences, such as selecting file paths for Graphviz and ImageMagick executables, and updating UI settings.
- 静态失败原因: The static BERT model likely overgeneralized from the presence of common Java API keywords (e.g., File, getChannel, write, read, close) and boilerplate patterns (e.g., if blocks, exception handling), despite low token overlap (Jaccard 0.037). It may have misclassified due to similar length and file-related vocabulary.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB labels this as non-clone because the functions serve entirely different purposes (file I/O vs. GUI event handling), with no overlap in functionality or logic.
- 行为差异: Function A is a static main method performing low-level file I/O; Function B is an instance method handling GUI events and user preferences.；Function A uses FileChannel and ByteBuffer for binary/byte-level file operations; Function B uses JFileChooser and utility classes for UI configuration.；Function A has no user interaction or GUI; Function B is event-driven and modifies UI components.；Function A is self-contained and writes/reads fixed content; Function B depends on external state and saves preferences via a controller.
- 修正建议: Enhance training with negative pairs that share common keywords but differ in semantics.；Incorporate program flow analysis or type information to distinguish low-level I/O from GUI operations.；Use methods capturing higher-level functional semantics (e.g., API calls, domain-specific concepts).

### case_id=1893 FN benchmark_preference_bias

- 方法: `getButtonSonido` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.1`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Creates a JButton that opens a file chooser to select a sound file, copies it, and plays audio.
- B 摘要: Downloads a KMZ file from a URL and extracts its entries to the local filesystem.
- 静态失败原因: The model correctly predicted 0 (non-clone) given the low token overlap and distinct semantics, but BCB labeled as clone, causing a false negative. The model's static analysis could not capture any hidden similarity BCB might have assumed.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: The BCB label of 1 may be an annotation error, as the functions have low syntactic similarity and semantically distinct purposes. Possibly BCB considered both as 'file I/O' methods, which is overly broad.
- 共享行为: Both perform file I/O operations (reading and writing files) and handle IOException.
- 行为差异: Function A is a GUI event handler for selecting and copying a sound file; Function B is a main method for downloading and unzipping a KMZ file.；Function A involves user interaction via file chooser; Function B is fully automated.；Function A copies a single file; Function B extracts multiple zip entries.
- 修正建议: Review and correct BCB annotation for this pair；Improve model to consider BCB labeling biases, or use a more consistent clone definition.

### case_id=1894 FN partial_functionality

- 方法: `copy` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a file using NIO FileChannel and MappedByteBuffer.
- B 摘要: Builds an editable site by transforming XML and writing HTML files.
- 静态失败原因: Static models rely on token/structural similarity; these functions have low token overlap (0.07) and different method names, failing to capture the deep semantic similarity of I/O operations.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider them Type-4 semantic clones because both functions perform file-to-file transfer with resource management, even though the transformation logic differs.
- 共享行为: Both read from a source and write to a destination using file I/O；Both close streams/resources in a finally-like block
- 行为差异: A is a simple file copy; B involves complex XML transformation and string processing；B takes many more parameters and has extensive error handling；A uses NIO channels; B uses traditional FileInputStream/FileWriter；B writes multiple output files; A writes a single file
- 修正建议: Improve models to recognize common I/O patterns via data-flow graphs；Incorporate type information and resource usage signatures；Use dataset augmentation with semantic clones

### case_id=1895 FN partial_functionality

- 方法: `doVersionCheck` vs `invoke`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Retrieves version information from a remote URL by reading lines and extracting build numbers.
- B 摘要: Invokes a remote service method via HTTP POST, parses JSON response, and supports retry on timeout.
- 静态失败原因: Static BERT models rely heavily on lexical and syntactic overlap; the low token Jaccard (0.14) and different method names, libraries (jEdit vs HttpClient), and task-specific logic obscured the shared network I/O pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB annotators may consider both as Type-4 clones because they share a high-level pattern of network I/O: open URL, read stream, parse lines, close resources. Despite different specific tasks, the structural skeleton is similar.
- 共享行为: Both open an HTTP connection to a URL；Both read response line-by-line using BufferedReader；Both parse content from the response；Both close streams and handle I/O exceptions
- 行为差异: Function A uses HTTP GET (implicitly) for version check; Function B uses HTTP POST for RPC；Function A reads plain text lines; Function B reads JSON and deserializes to Java types；Function A calls another method after parsing; Function B returns a deserialized object；Function B has retry logic on ConnectTimeoutException; Function A does not
- 修正建议: Enhance models with control-flow or data-flow analysis to capture abstract patterns like 'acquire resource, process, release'；Use program slicing or coarse-grained AST paths to identify similar structures despite different APIs；Incorporate domain knowledge about common I/O patterns

### case_id=1896 FN partial_functionality

- 方法: `addIDs` vs `CheckUrl`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches metabolite data from a web service by constructing a URL from a name, parses HTML to extract score and IDs, and populates a PeakListRow with various columns.
- B 摘要: Reads the first line of a URL's response and returns it as a string, with basic error handling.
- 静态失败原因: Static BERT/GraphCodeBERT models likely relied on low token overlap (Jaccard=0.1) and differing method signatures/return types, missing the shared pattern of HTTP GET and BufferedReader usage that BCB considered.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled this as clone because both functions perform a web request and read the response line by line, which is a common pattern, and BCB's broad Type-3/4 criteria sometimes accept such structural similarity despite different domain logic.
- 共享行为: Both open an HTTP connection using URL and read from a BufferedReader
- 行为差异: Function A constructs a URL based on input name and parses multiple lines for specific patterns, while Function B takes a pre-formed URL and only reads a single line.；Function A returns an integer score after complex parsing and sets multiple fields on a row object, whereas Function B returns a string with no side effects.；Function A has extensive error handling and uses multiple try-catch blocks, while Function B catches generic Exception and prints stack trace.；Function A has a large block of code handling different identifier types (PubChem, ChEBI, KEGG, etc.), absent in Function B.
- 修正建议: Improve detection of common I/O patterns even when surrounding logic differs.；Incorporate data flow analysis to recognize that both functions ultimately read from a URL through BufferedReader.；Use code summarization or API-level matching to identify HTTP client utilities as clones.

### case_id=1897 FP lexical_or_api_overlap

- 方法: `test` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: A test method that initializes a traffic simulation and runs a loop to simulate steps, printing vehicle positions and speeds.
- B 摘要: An actionPerformed handler that processes various GUI commands (e.g., GRAPHVIZ, IMAGEMAGICK) to configure application settings and update preferences.
- 静态失败原因: Static BERT likely misclassified due to superficial lexical or structural overlaps (e.g., both use loops, conditionals, variables) or because the model was not robust to domain differences and low token similarity, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would label these as not clones because they have completely different purposes, domains, and logic; no functional overlap even under broad Type-4 similarity.
- 行为差异: A simulates traffic, B handles GUI events；A uses simulation classes, B uses Swing and file choosers；A loops over time steps, B branches on action commands；A prints debug output, B updates UI components and persists preferences
- 修正建议: Train the model with more diverse non-clone pairs to reduce false positives；Incorporate dataflow or AST-based features to capture semantic intent；Use contrastive learning to better separate dissimilar functions

### case_id=1898 FN benchmark_preference_bias

- 方法: `doGet` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.2`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Handles HTTP GET requests for a portal page, retrieves page by ID or name, checks visibility and edit permissions, and writes page output with optional caching to a file.
- B 摘要: Copies a file from source to destination using FileChannel transfer.
- 静态失败原因: The static BERT model correctly identified no clone due to very low token Jaccard (0.049) and fundamentally different APIs, domains, and control flow. It did not fail; the BCB label appears erroneous.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might have labeled these as clones due to a broad interpretation of 'file copying' functionality, or a mistake in the dataset. The functions share no structural or semantic similarity beyond trivial file operations.
- 共享行为: Both involve file I/O operations (function_a writes to a temp file during caching; function_b copies a file)；Both use try-finally or similar resource handling
- 行为差异: Function_a is an HTTP servlet handler with complex business logic (page lookup, permissions, logging, caching); Function_b is a simple utility function；Function_a writes HTML output to response and conditionally to a file; Function_b transfers bytes between channels；Function_a depends on a web framework (HttpServletRequest/Response); Function_b uses only standard Java I/O；Function_a has multiple error paths and logging; Function_b has minimal error handling
- 修正建议: Review and correct BCB labels for this pair；If BCB intended a broad Type-4 clone, clarify annotation guidelines to avoid such mismatches；Improve model to handle noisy labels

### case_id=1899 FN partial_functionality

- 方法: `testAddLinkToImage` vs `getFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Test method that copies image files from classpath to report folder and adds links.
- B 摘要: Downloads a WSDL file from a URL, modifies its endpoint, and saves locally.
- 静态失败原因: Low token overlap (0.079) and different method names; static models rely on lexical similarity and miss the functional abstraction of file stream operations.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider them Type-3 clones due to similar file I/O structure (open stream, copy, close) and resource management idioms, despite different high-level purposes.
- 共享行为: Both read from an input stream and write to a file.
- 行为差异: A copies static resources; B downloads from dynamic URL.；A only writes; B also modifies XML and renames files.；A is a test; B is a production utility with error handling.；A does not handle network or XML; B does.
- 修正建议: Use data-flow analysis to capture stream operations.；Incorporate contextual information like method purpose or related API calls.；Employ graph-based representations to model control and data flow.

### case_id=1900 FN benchmark_preference_bias

- 方法: `saveFileData` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.6`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Saves file data by copying from source to destination and optionally replacing with new data, handling image metadata and cleaning up thumbnails.
- B 摘要: Launches a NexOpen project configuration in Eclipse, processing Maven POM files, setting Hibernate properties, and performing reverse engineering setup.
- 静态失败原因: The static model likely correctly identified non-clone due to low lexical overlap (Jaccard 0.06) and distinct API calls, but BCB's annotation suggests a broader interpretation that the model missed.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled these as clones due to both involving file operations and setup tasks, despite lacking semantic equivalence, possibly under a broad Type-4 interpretation of 'similar functionality' in resource handling.
- 共享行为: Both perform file I/O operations (e.g., FileInputStream, FileOutputStream)
- 行为差异: Different domains: file management vs Eclipse launch；Different control flow: saveFileData is linear, launch has conditional logic；Different outputs: saveFileData writes files, launch configures and runs a project
- 修正建议: Clarify annotation guidelines to avoid overly broad Type-4 clones；Improve model capacity to detect domain-specific similarities that might indicate partial functionality

### case_id=1901 FN benchmark_preference_bias

- 方法: `doGet` vs `copyFileByNIO`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Handles HTTP GET request, retrieves and renders a page, includes caching and logging.
- B 摘要: Copies a file from source to destination using NIO channels.
- 静态失败原因: The model correctly predicted non-clone; from BCB perspective it failed due to BCB labeling error, not model deficiency.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have mislabeled due to broad interpretation of semantic similarity or annotation error; both methods involve file I/O in one branch of A, but core functionality differs.
- 行为差异: Different overall purpose (servlet vs file copy)；No common I/O operations or data processing；Different control flow and error handling
- 修正建议: Revisit BCB annotation for this pair；Correct label to non-clone

### case_id=1902 FN partial_functionality

- 方法: `getWebByUrl` vs `invoke`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.65`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a web page from a URL, saves content to a local file, and recursively processes embedded URLs.
- B 摘要: Invokes a remote method via HTTP POST with JSON serialization, handles retries on connection timeout.
- 静态失败原因: Static BERT models often rely on token overlap and API name similarity; here token Jaccard is low (0.16) and APIs differ (URLConnection vs HttpClient), causing the model to miss the structural similarity in HTTP request-response handling.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label as clone due to both being web client operations that open HTTP connections, read input streams, and process text lines, sharing a common pattern of network I/O and text processing despite different high-level purposes.
- 共享行为: Both perform HTTP requests and read the response line by line.
- 行为差异: A saves to file and crawls recursively; B deserializes JSON and includes retry logic.；A uses URLConnection and file I/O; B uses HttpClient and serialization libraries.；A prints logs and calls helper methods; B returns a Java object.
- 修正建议: Train models with contrastive examples of cross-API Web client patterns.；Use data flow analysis to capture common I/O sequences.；Augment with more Type-3/Type-4 clone pairs that differ in API but similar in control flow.

### case_id=1903 FN benchmark_preference_bias

- 方法: `testStandardTee` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.0`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Unit test that copies a reference string to two StringWriters using TeeWriter and verifies equality.
- B 摘要: Complex method that builds a website for editing by processing XML, applying XSLT, reading/writing files, and performing string replacements.
- 静态失败原因: Static BERT correctly predicted non-clone; the model did not fail. The BCB label is erroneous.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: The BCB annotation is likely erroneous; there is no reasonable partial functionality or Type-3/4 similarity between these functions.
- 行为差异: Completely different functionality；Different input/output and parameters；Different complexity and length
- 修正建议: Review and correct BCB annotation for this pair；Consider removing or re-labeling misannotated pairs

### case_id=1904 FP lexical_or_api_overlap

- 方法: `doRawRequest` vs `getFullScreenUrl`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Sends POST data to a service URL and returns the raw response string.
- B 摘要: Fetches a YouTube page, extracts video parameters, and constructs a full screen URL.
- 静态失败原因: Static BERT-based models may over-rely on lexical and API-level similarities, such as 'URLConnection', 'BufferedReader', and 'readLine', and ignore the larger context and control flow that differentiate the functions.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled non-clone because the overall functionality differs significantly: one is a generic HTTP POST helper, the other is a specific YouTube URL builder. The overlapping code (URL opening, reading lines) is a common boilerplate pattern that does not imply semantic equivalence.
- 共享行为: Open a URL connection；Set doOutput to true；Read lines from the input stream via BufferedReader；Close the reader
- 行为差异: Function A writes POST data to the output stream; function B does not.；Function A returns the entire response; function B parses lines to find specific parameters and constructs a new URL.；Function B updates a progress bar and prints debug information; function A does not.；Function B has exception handling; function A throws IOException.
- 修正建议: Incorporate structure-based features like control flow graphs or data dependency analysis；Train on more diverse examples to learn that boilerplate patterns do not imply semantic equivalence；Use models that capture long-range dependencies and purpose-level semantics

### case_id=1905 FN partial_functionality

- 方法: `copyResource` vs `addRecord`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource (URL or file) to a destination file using byte-by-byte streaming.
- B 摘要: Adds a data record from an InputStream by copying to a temporary file while computing a digest, then storing in a data store with collision detection and synchronization.
- 静态失败原因: Static BERT models like GraphCodeBERT rely heavily on token-level overlap and API call patterns. Here, token Jaccard is low (0.189), method names differ, and B contains many unique API calls (MessageDigest, DataIdentifier, IOUtils). The model failed to recognize the shared InputStream-to-OutputStream core due to these surface-level differences.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considers this a Type-4 semantic clone because both functions involve the core operation of copying data from an InputStream to a file output, which is a common pattern. The additional logic in B (digest, renaming) may be viewed as extensions rather than a completely different functionality.
- 共享行为: Reads from an InputStream and writes to an OutputStream (file).
- 行为差异: Function A uses a simple byte-by-byte copy loop; Function B uses IOUtils.copyLarge for bulk copy.；Function B computes a MessageDigest during copy, renames temporary files, handles collisions, and synchronizes access.；Function A directly writes to a predetermined file; Function B computes a hash-based identifier and manages file storage in a data store.
- 修正建议: Train with contrastive examples that highlight shared substructures (e.g., input-output stream pairs).；Use code representation that abstracts over common I/O patterns, such as data flow or taint analysis.；Incorporate data augmentation by obfuscating implementation details while preserving core semantics.

### case_id=1906 FP lexical_or_api_overlap

- 方法: `main` vs `compress`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.98`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Generates adapter classes from a Prolog file specification.
- B 摘要: Concatenates multiple input files into one output file and optionally compresses it.
- 静态失败原因: Static BERT/GraphCodeBERT may have focused on overlapping API calls (FileInputStream, FileOutputStream) and sequential structure, ignoring the overall semantic intent.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels as non-clone because functions have distinct high-level functionalities despite some low-level I/O similarities; they solve different problems.
- 共享行为: Both perform file I/O operations.；Both use streams (InputStream/OutputStream).；Both handle exceptions.；Both involve reading/writing files.
- 行为差异: Different core purpose: code generation vs file concatenation/compression.；A generates Java classes and serializes data; B concatenates binary/text files.；A uses parser and visitor patterns; B uses simple file copy and external compression.；A has complex logic for adapter generation; B has straightforward file concatenation.
- 修正建议: Incorporate dataflow or control-flow analysis.；Use call-graph or type-system information.；Train with more contrastive examples of non-clones with high token overlap.

### case_id=1907 FP lexical_or_api_overlap

- 方法: `main` vs `persist`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.98`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Parses a Prolog file to generate adapter classes and writes them to a JAR file.
- B 摘要: Persists a free-form configuration to a properties file.
- 静态失败原因: The static BERT model likely overemphasized lexical overlap of common API classes (File, IOException) and the try-catch structure, ignoring the fundamentally different business logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB annotates non-clone because the functions serve completely different purposes and have no shared functionality beyond basic file I/O.
- 共享行为: Both involve file output operations.
- 行为差异: Different input types (Prolog file vs config stream)；Different output types (JAR file vs properties file)；Different core algorithms (adapter generation vs file copy)；Different error handling (prints stack trace vs throws exception)
- 修正建议: Incorporate more training examples of functions with similar APIs but different semantics；Use contrastive learning to distinguish dissimilar functions with surface-level similarities；Integrate data-flow analysis to capture program semantics beyond token sequences

### case_id=1908 FP lexical_or_api_overlap

- 方法: `doVersionCheck` vs `checkForUpgrade`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Checks for a new version of jEdit by reading a version and build string from a remote URL, then displays an update message or up-to-date message.
- B 摘要: Performs a complex upgrade process: queries database for applied version, validates license via a remote URL, parses XML-like response, inserts new upgrade records into database, and updates UI components accordingly.
- 静态失败原因: Static BERT models like GraphCodeBERT rely on token-level patterns and might have been misled by overlapping tokens such as 'URL', 'openStream', 'BufferedReader', 'while ((line = ...) != null)', and general update-related words. The model failed to capture the distinct data flows and specific business logic, thus overgeneralizing to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the functions have fundamentally different logic, side effects, and contexts. Although both are related to 'checking for updates', the implementations diverge significantly in data sources, parsed structures, and actions taken. BigCloneBench typically requires more direct functional equivalence or near-miss Type-3 similarity.
- 共享行为: Both open a URL connection and read lines from the input stream.；Both use a BufferedReader to parse the response.；Both check for some condition (new version or license status) and display a message to the user.；Both are public static void methods that may involve UI interaction.
- 行为差异: Function A uses a simple version comparison (build string), while function B involves license validation and database operations.；Function A only shows a message, while function B updates database tables and manipulates UI components (visibility changes).；Function A reads from a URL defined by jEdit property; function B constructs a URL with client-specific parameters (version, unit ID, MAC).；Function A has minimal error handling (catch IOException); function B has multiple error conditions (FAIL, NOVALIDLICENSE, etc.) and returns early.
- 修正建议: Improve training with contrastive examples that have similar API usage but different semantics.；Incorporate dataflow analysis or program dependence graphs to differentiate control and data flows.；Use statement-level or structural differencing to highlight the substantial logic differences.；Enhance model capacity to reason about long-range dependencies and distinct business contexts.

### case_id=1909 FP lexical_or_api_overlap

- 方法: `issueCommandToServer` vs `downloadFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Sends a command to a server via HTTP POST and reads the response as a string.
- B 摘要: Downloads a file from a URL and saves it to disk with progress reporting.
- 静态失败原因: Static BERT likely focused on lexical overlap (URLConnection, InputStream, read loop) and missed the distinct functional intents due to lack of deep semantic understanding.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB considers them non-clones because they perform different high-level tasks (command execution vs file download) despite sharing low-level I/O operations.
- 共享行为: Both open a URL connection and read from its input stream in a loop
- 行为差异: Function A writes output to the server before reading; Function B only reads；Function A returns the response string; Function B returns boolean and saves to file；Function B implements progress reporting using MessageFrame
- 修正建议: Incorporate control flow and data flow analysis to distinguish input/output patterns；Use a model that captures higher-level intent or task context

### case_id=1910 FN benchmark_preference_bias

- 方法: `main` vs `testCopy_readerToWriter_nullIn`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a URL and extracts its zip entries to files.
- B 摘要: Tests that IOUtils.copy throws NullPointerException when given a null Reader.
- 静态失败原因: Static BERT correctly identified low token overlap and dissimilar method names, leading to non-clone prediction; it failed to match BCB's broad functional category.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled based on broad I/O stream manipulation, but the specific functionalities differ significantly; this is likely an annotation error or overly broad Type-4 clone.
- 共享行为: Both involve I/O stream operations；Both are related to data transfer or its testing
- 行为差异: A performs actual file extraction; B tests exception handling；A uses URL and ZipInputStream; B uses ByteArrayOutputStream and Writer；A has a loop to read and write; B has a single call；A produces output files; B has no output
- 修正建议: Improve training data with more examples of I/O stream operations；Incorporate high-level operation type embeddings；Add library usage context

### case_id=1911 FN benchmark_preference_bias

- 方法: `modifyApplicationMessage` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Modifies a properties file for a given locale by copying a default file if missing and then updating or appending a specific message.
- B 摘要: Copies a source file to a destination file using FileChannel.
- 静态失败原因: The static model correctly identified non-clone; this is a false positive annotation in BCB.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB likely mislabeled this pair due to superficial similarity of file copy operations within A, or an annotation error.
- 共享行为: Both functions perform file I/O operations
- 行为差异: A has complex logic for locale-specific properties file management, B is a simple file copy；A includes conditional file copy, reading, parsing, modifying, and writing properties; B only copies bytes between channels；A does not return success status; B returns boolean
- 修正建议: Review BCB annotation for this pair to confirm correct label；Train models with more robust semantic understanding to avoid false negatives from benchmark noise

### case_id=1912 FP boilerplate_overlap

- 方法: `getLinksFromURLFast` vs `retrieveTemplate`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Parses a URL's HTML content to extract all hyperlinks and their display texts, returning them as two separate vectors.
- B 摘要: Reads the content of a blog's URL and caches the entire page content as a string for template retrieval.
- 静态失败原因: Static models may over-rely on surface-level token overlap (e.g., 'URL', 'BufferedReader', 'readLine') and similar structural patterns, missing the semantic divergence in post-processing and return types.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically treats functions with identical core behavior as clones. Here the core behavior differs fundamentally (link extraction vs. template retrieval). The shared I/O boilerplate is insufficient to consider them clones under BCB's preference for broad Type-3/4, which still requires significant functional overlap.
- 共享行为: Both open a URL connection；Both read lines of content into a buffer；Both use BufferedReader and InputStreamReader；Both handle exceptions with throws
- 行为差异: A uses multiple regular expressions to extract links and root directory; B simply concatenates all lines without parsing；A returns a Vector array of extracted links and texts; B returns a single cached string；A has time-check logging statements; B has caching logic (if cachedTemplate != null)；A converts relative URLs to absolute using toAbsolute; B does no URL transformation
- 修正建议: Incorporate data flow analysis to distinguish output structures (Vector[] vs String)；Train on examples with shared boilerplate but different core logic to reduce false positives；Weight functional API usage (e.g., Regex) more heavily than I/O setup

### case_id=1913 FP other

- 方法: `readAndRewrite` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Reads and rewrites a DICOM file, parsing pixel data and writing it to an output file.
- B 摘要: Handles action commands in a GUI settings dialog, updating preferences for various tools and UI settings.
- 静态失败原因: The model may have been misled by minor lexical similarities (e.g., 'File', 'IOException', 'System.out.println'), but these are coincidental and the semantic gap is vast.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB labels these as non-clones because they have completely different functionality: one is a low-level DICOM file operation, the other is a high-level GUI event handler for settings.
- 共享行为: Both perform file I/O operations
- 行为差异: Function A is a DICOM image processing utility; function B is a GUI event handler for configuration.；Function A handles medical image data; function B manages application preferences and UI state.；Function A is synchronous file processing; function B is event-driven with user interaction.；Function A has no GUI elements; function B creates file choosers and updates UI components.
- 修正建议: Improve training data diversity to reduce false positives from unrelated functions.；Incorporate structural information like method signatures and class context.；Use contrastive learning to better separate distinct functionalities.

### case_id=1914 FN partial_functionality

- 方法: `postRequest` vs `seeURLConnection`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends an HTTP POST request with form data to a given URL and returns the response body as a string.
- B 摘要: Opens an HTTP connection to a hardcoded URL, reads the response line by line, and logs it.
- 静态失败原因: The static model likely focused on the low token overlap (0.24) and significant differences in method signature, error handling, and the presence of output operations in one function, leading it to classify them as non-clones. It missed the common URL connection and reading pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this as a clone because both functions perform an HTTP request and read the response line by line, which is the core functionality. The differences in HTTP method and error handling are considered secondary under broad Type-3/Type-4 clone criteria.
- 共享行为: Both open a URL and read the response using BufferedReader line by line.
- 行为差异: Code A sends a POST request with form data; Code B sends a GET request without payload.；Code A returns the response string or null on error; Code B logs the response and does not return anything.；Code A handles exceptions internally with printStackTrace; Code B throws Exception.；Code A is a static method with parameters; Code B is an instance method with no parameters.
- 修正建议: Improve model sensitivity to partial behavioral overlap.；Enhance representation to capture functional intent such as 'HTTP response reading'.

### case_id=1915 FN lexical_or_api_overlap

- 方法: `readData` vs `retrieveTemplate`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Parses comma-separated strings and reads a configuration file to populate various character sets and hash maps for Tibetan transliteration.
- B 摘要: Retrieves a blog template from a URL, caches it, and returns it as a string.
- 静态失败原因: Low token Jaccard (0.07) and different domain-specific vocabulary led to low embedding similarity, causing the model to miss any potential semantic similarity that BCB might have perceived.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: None
- 共享行为: Both perform I/O operations to read data from an external source.；Both involve processing the read data in some way.
- 行为差异: readData initializes multiple static collections and validates input; retrieveTemplate fetches and caches a single URL content.；Data sources differ: one reads from string tokens and a local file, the other from a URL.；readData has complex parsing logic for multiple columns; retrieveTemplate simply concatenates lines.；readData is void and modifies static state; retrieveTemplate returns a cached string.
- 修正建议: Incorporate structural or dependency analysis to capture broader I/O semantics.；Use abstract syntax tree or data flow information to generalize data reading patterns.

### case_id=1916 FN partial_functionality

- 方法: `getEncoding` vs `register`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Opens a URL connection, reads HTTP headers and body to extract charset encoding, returns encoding or default.
- B 摘要: Registers a user by encoding password, creating hash, calling a phpBB URL to get forum ID, persisting user, and sending confirmation email.
- 静态失败原因: Static BERT/GraphCodeBERT models rely on token overlap and structural similarity; the low Jaccard (0.125) and different method names/token sequences likely led to a non-clone prediction. The models may also fail to recognize the broad 'URL-reading' pattern as a clone criterion, especially without explicit training for such partial functionality.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider these clones because both involve opening a URL connection, reading lines, and performing some text processing; this common I/O pattern could be seen as a Type-4 clone (similar functionality despite different purposes).
- 共享行为: Both open a URL connection and use BufferedReader to read lines from the input stream
- 行为差异: Different purposes: encoding detection vs. user registration；Different inputs: URL object vs. User object；Different outputs: encoding string vs. boolean；Different logic: header parsing and content scanning vs. password encoding, hash creation, database persistence, email sending
- 修正建议: Incorporate structural or semantic role labels for I/O patterns (e.g., URLConnection operations) to capture partial functionality clones.；Use data-flow analysis to identify common sub-patterns like 'open connection, read lines, process line'.；Fine-tune on BCB-style annotations to learn their broad clone definition, including Type-4 partial functionality.

### case_id=1917 FP boilerplate_overlap

- 方法: `sendPost` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Sends an HTTP POST request with parameters and returns the response body as a string.
- B 摘要: Performs a Google image search, parses the HTML response to extract image URLs, and updates a UI component with the first image.
- 静态失败原因: Static BERT models may over-rely on the shared boilerplate code for HTTP connection and reading, overlooking the different method names, return types, and additional processing in Code B.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled non-clone because the functions have different overall purposes (generic HTTP POST vs. specific image search with UI updates) and the additional domain-specific logic in Code B is substantial, making them not semantically equivalent in the BCB sense.
- 共享行为: Open an HTTP connection to a URL；Read the response line by line into a string；Handle exceptions by showing an error message
- 行为差异: Code A uses POST method and sends a parameter; Code B uses GET (implied) with query parameters；Code B does additional HTML parsing to extract image URLs；Code B updates a UI component (albumArtLabel) and modifies a static list (googleImages)；Code A returns the response string; Code B has void return and performs UI actions
- 修正建议: Incorporate data flow analysis to capture the broader context and side effects of functions；Use method-level embeddings that consider the overall purpose or domain；Add attention mechanisms that focus on distinguishing tokens like 'sendPost' vs. 'googleImageSearch'

### case_id=1918 FN benchmark_preference_bias

- 方法: `doGet` vs `write`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.2`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Handles HTTP GET request to retrieve and render a portal page, performing access control and caching.
- B 摘要: Writes ByteBuffer data through an SSL engine, performing handshake and encryption.
- 静态失败原因: The static BERT model correctly predicted non-clone; the BCB label appears erroneous.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: Likely a mislabel; both functions have 'write' in method names or output operations, but BCB annotation may be overbroad.
- 行为差异: Different input/output types (HttpServletRequest/Response vs ByteBuffer arrays)；One involves HTTP request handling, the other involves SSL/TLS encryption；One writes to a response stream, the other returns encrypted buffers；Different control flow and error handling
- 修正建议: Re-evaluate BCB annotation for this pair；Use better semantic matching beyond lexical overlap

### case_id=1919 FN lexical_or_api_overlap

- 方法: `httpRequestByPOST` vs `postXml`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.95`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends HTTP POST with URL-encoded form parameters using HttpClient, returns response body string or null on error.
- B 摘要: Sends HTTP POST with XML/SOAP payload using HttpURLConnection, returns response body string or throws RuntimeException.
- 静态失败原因: Static BERT models rely on token-level similarity; the low Jaccard similarity (0.202) and different API usage (HttpClient vs HttpURLConnection), parameter types, and error handling led the model to view them as non-clones, missing the common intent.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB considers these clones because both are methods that send HTTP POST requests and retrieve the response content, representing high-level functional similarity (Type-3/Type-4).
- 共享行为: Both perform HTTP POST requests；Both read the response body line by line and concatenate into a string；Both return the response body as a String
- 行为差异: A uses Apache HttpClient, B uses java.net.HttpURLConnection；A sends URL-encoded form data (NameValuePair list), B sends raw XML string；A handles HTTP errors by setting error fields and returning null, B throws RuntimeException on IOException；B sets SOAP-specific headers like Content-Type and SOAPAction
- 修正建议: Use semantic features like API call graphs or data flow；Incorporate task-level intent understanding；Train on more diverse Type-3/Type-4 examples

### case_id=1920 FN partial_functionality

- 方法: `modifyApplicationMessage` vs `streamContains`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Reads and modifies a locale-specific properties file, adding or updating a key-value pair.
- B 摘要: Asserts that an InputStream's contents contain a given substring.
- 静态失败原因: The low token overlap (Jaccard 0.06) and different method names/contexts likely caused a static model like GraphCodeBERT to miss the vague I/O-level similarity, which is semantically weak.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled this as a clone due to both methods involving I/O operations and string processing, accepting broad Type-4 partial functionality similarity, though the actual functionalities differ significantly.
- 共享行为: Both read text from an I/O source (file or stream) and process it.
- 行为差异: Method A writes modified properties back to a file; Method B only performs an assertion.；Method A handles file existence and comments; Method B does not.；Method A uses key-value parsing; Method B uses simple substring containment.
- 修正建议: Improve training data to include more diverse Type-3/Type-4 clones with low lexical overlap.；Enhance models with dataflow or I/O structure awareness to capture broad textual processing patterns.

### case_id=1921 FN partial_functionality

- 方法: `downloadURLtoString` vs `httpRequestByPOST`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a URL and returns its content as a string by reading line by line.
- B 摘要: Performs an HTTP POST request with parameters and returns the response body as a string, handling errors and returning null on failure.
- 静态失败原因: The models likely failed due to significant lexical differences (different method signatures, API classes like URL vs HttpClient) and control flow (error handling branches). They may not capture the common pattern of reading from a stream decoupled from the specific protocol.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels functions as clones if they share a core functional purpose, such as 'retrieve web content as string', even if the protocols or error handling differ. The high-level similarity in reading and accumulating lines from an HTTP response justifies a Type-4 clone.
- 共享行为: Reads input from an HTTP response stream line by line；Appends each line to a StringBuffer；Returns the accumulated string as the result
- 行为差异: A uses URL.openStream (GET), B uses HttpClient.execute (POST)；A throws IOException on failure, B catches exceptions and returns null；B includes additional logic for status code checking and error handling；B accepts parameters and timeout, A takes only a URL
- 修正建议: Incorporate dataflow analysis to identify shared subgraph of reading and accumulation；Use abstract representations that capture the essence of 'downloading and concatenating lines'；Train on fine-grained functional similarity annotations beyond token overlap

### case_id=1922 FN partial_functionality

- 方法: `getFile` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads WSDL file from URL, modifies XML endpoint, and saves to temp directory, returning the file path.
- B 摘要: Copies a file from source to destination using FileChannel transfer.
- 静态失败原因: Static BERT/CodeBERT models often rely on token overlap and surface-level structure; low Jaccard similarity (0.15) and different method signatures/exception handling cause it to miss the deeper semantic similarity of the file copy core.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider the core file copy operation using NIO channels as a functionally similar sub-task, and despite different surrounding context, this shared logic qualifies it as a Type-3 or Type-4 clone.
- 共享行为: Both use java.nio.channels.FileChannel for efficient file data transfer.
- 行为差异: Function A involves network download, XML parsing, and multiple exception handling; function B is a simple file copy with minimal error handling.；Function A modifies the WSDL content before saving; function B performs a direct copy without transformation.；Function A handles multiple exception types; function B only catches FileNotFoundException and closes channels in finally block.
- 修正建议: Use graph-based models (e.g., AST or dataflow) to detect shared sub-patterns like FileChannel usage.；Incorporate contrastive learning with positive pairs that have low token overlap but share functional subroutines.；Include code summarization or multi-grained similarity approaches to capture partial functional overlap.

### case_id=1923 FN benchmark_preference_bias

- 方法: `decodeFileToFile` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Decodes a Base64-encoded input file and writes the decoded content to an output file, returning success status.
- B 摘要: Builds a transformed site for editing by processing pages, reading XML, applying XSLT, and writing output files, with extensive error handling and debugging.
- 静态失败原因: The static BERT method likely focused on lexical and structural similarity, which are very low, but missed any potential high-level functional similarity that BCB might have considered. Given the minimal overlap, the model correctly predicted non-clone under standard semantic interpretation.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled them as clones under a broad interpretation of Type-4 where any file transformation method that reads input and writes output is considered functionally similar, despite vastly different transformation logic.
- 共享行为: Both involve file I/O using java.io streams；Both have try-catch-finally for resource management
- 行为差异: decodeFileToFile is a simple two-step decode operation; buildSiteForEdit is a multi-step site generator with many parameters and transformations；decodeFileToFile returns a boolean; buildSiteForEdit has void return and throws multiple exceptions；decodeFileToFile uses Base64 decoding; buildSiteForEdit uses XSLT, DOM, and file merging；decodeFileToFile has a simple read-write loop; buildSiteForEdit loops over pages and performs complex string processing
- 修正建议: Re-evaluate BCB labeling for this pair; likely a false positive；Improve training to handle cases with low lexical overlap but high-level functional similarity if that is desired

### case_id=1924 FN long_range_semantics

- 方法: `main` vs `test`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.3`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a URL and extracts its entries to files.
- B 摘要: Reads an XML resource, initializes a traffic simulation engine, and runs a simulation printing vehicle positions.
- 静态失败原因: The static BERT/GraphCodeBERT model relied on lexical and syntactic features; the low token overlap (0.12) and different APIs led it to predict non-clone, failing to capture the abstract semantic similarity that BCB annotators recognized.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely considers both as Type-4 clones because they share the high-level behavior of reading data from a stream, processing it in a loop, and printing results, despite different domains and detailed implementations.
- 共享行为: Both read data from an InputStream；Both have a loop that iterates and prints output to console
- 行为差异: Code A processes zip entries and writes to files; Code B processes a traffic model and runs simulation steps；Code A uses URL connection; Code B reads from classpath；Code A uses ZipInputStream; Code B uses IOUtils and ByteArrayOutputStream；Code A is a main method; Code B is a test method
- 修正建议: Incorporate higher-level semantic features such as dataflow patterns and I/O operations；Use larger context or graph representations to capture intent；Include more diverse training examples of Type-4 clones from different domains

### case_id=1925 FN partial_functionality

- 方法: `doVersionCheck` vs `register`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Checks software version by reading a remote resource and comparing build numbers.
- B 摘要: Registers a user by encoding password, setting properties, creating a forum account via HTTP, persisting, and sending email.
- 静态失败原因: The model likely relied on low token overlap and different method signatures, failing to capture the abstract URL reading pattern that BCB considered as clone.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider the similar structural pattern of URL reading and line parsing as a broad Type-3 clone, despite different overall functionality.
- 共享行为: Both open a URL connection and read lines using BufferedReader.；Both handle IOException.
- 行为差异: Different input and output: A takes View and returns void; B takes Object and returns boolean.；Different logic after reading lines: A parses version/build strings; B extracts forumID and sets it.；Different side effects: A shows messages; B modifies user object, persists, and sends email.；Different exception handling: A only catches IOException; B catches IOException and NumberFormatException, throws RuntimeException.
- 修正建议: Train models to recognize abstract structural patterns beyond token-level similarity.；Re-annotate BCB to remove noisy labels with only partial functionality overlap.

### case_id=1926 FP lexical_or_api_overlap

- 方法: `get` vs `SRWGuiClient`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches game records from a given URL via HTTP GET, returning an array of GameRecord objects.
- B 摘要: Constructor of SRWGuiClient that sets up a browser GUI, reads XML/HTML from a URL, optionally transforms XSLT, and displays content.
- 静态失败原因: Static BERT/GraphCodeBERT may have overgeneralized the presence of similar I/O operations (URL, BufferedReader, readLine, try-catch) and ignored the high-level semantic context (method signature, GUI setup, transformation). The token-level Jaccard is low but the model attended to common code structure of reading from a URL.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would label this non-clone because despite shared I/O API usage, the overall functionality and output are completely different — one is data retrieval, the other is GUI construction.
- 共享行为: Both open a URL and read text lines via BufferedReader
- 行为差异: A returns an array of GameRecord; B sets up a GUI and processes XML/HTML；A is a static utility method; B is a constructor that builds a window；A uses HTTP headers and specific decoding; B uses XSLT transformation and JEditorPane；A ignores comments; B handles XML stylesheets
- 修正建议: Train on more diverse examples of non-clones with overlapping API usage but different goals；Incorporate method signatures and class context more effectively；Use contrastive learning to distinguish such patterns

### case_id=1927 FN partial_functionality

- 方法: `getProjectTreeData` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.45`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Retrieves admin project list from a URL, parses XML, and returns a 2D array of project data.
- B 摘要: Retrieves a resource from a URL with caching, returns an InputStream of the local cached file.
- 静态失败原因: Low token overlap (0.16), different method names and return types, and the presence of distinct logic (caching vs XML parsing) mislead the model; it missed the underlying structural similarity in the download-and-file-I/O pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may view both as clones due to the shared pattern of downloading from a URL, saving to a file, and reading back, considering the specific output type and caching as superficial differences in a broader Type-4 clone category.
- 共享行为: Both open a URL connection and read input stream.；Both write data to a local file and then read from that file.；Both handle exceptions during I/O operations.
- 行为差异: A returns a String[][]; B returns an InputStream.；A does not implement caching; B caches resources.；A uses fixed-size buffer; B reads byte-by-byte.；A parses XML for project data; B uses HTTP caching headers.
- 修正建议: Enhance model with dataflow analysis to capture shared I/O patterns.；Use method-level semantic abstraction that ignores specific return types and caching details.

### case_id=1928 FN partial_functionality

- 方法: `readGeoParserResult` vs `seeURLConnection`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a record content, builds an XML request, sends it to a geo-parser service, parses the XML response to extract place names and their gazetteer IDs, with retry logic.
- B 摘要: Opens a URL connection to a hardcoded address, reads the response line by line, and logs the result.
- 静态失败原因: Static models rely on lexical or structural overlaps, but the token Jaccard is low (0.134). While there are common tokens like 'URL', 'BufferedReader', etc., the overall structure differs significantly: method A has a large XML building section and parsing loops, method B is short. The model may have been misled by the low lexical overlap and different signatures, and long-range dependencies in method A may not be captured well.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considers this a Type-4 (semantic) clone because both methods involve connecting to a URL and reading lines, which is a common high-level behavior. The benchmark may be lenient on partial functionality similarity, especially since the core reading loop is nearly identical in structure.
- 共享行为: Both open a URL and read the response line by line using BufferedReader；Both accumulate lines into a StringBuffer
- 行为差异: Method A builds and sends an XML request; method B uses a fixed URL without request body；Method A parses XML response to extract structured data; method B just logs raw text；Method A has retry logic (up to 3 attempts); method B no retries；Method A returns a Collection; method B returns void
- 修正建议: Improve representation of data flow and control flow to capture common subgraphs like the URL reading loop；Use techniques that can abstract away differing overhead and focus on core behavior；Incorporate type-based or API usage patterns to recognize similar operations

### case_id=1929 FP lexical_or_api_overlap

- 方法: `main` vs `getFrameworkFactory`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a URL from a string and prints each line to standard output.
- B 摘要: Reads a service configuration file from the classpath and returns a FrameworkFactory instance.
- 静态失败原因: Static BERT models rely heavily on token overlap and API sequences. Both functions use URL, BufferedReader, readLine, etc., causing high lexical similarity. The model likely ignored the different return types and exception handling, focusing on the common boilerplate.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the functions have different overall purposes: one is a main method that prints output, the other is a utility method that returns an object after processing. The shared boilerplate code is not sufficient to consider them functionally similar.
- 共享行为: Both open a URL and read lines using a BufferedReader
- 行为差异: A prints lines to console; B returns a FrameworkFactory object；A reads from a fixed hardcoded URL; B reads from a classpath resource；A does not handle exceptions beyond IOException; B handles exceptions and throws Exception；B has conditional logic to check for null URL and throw exception if not found
- 修正建议: Incorporate data-flow analysis to track how read lines are used；Add features capturing method return type and purpose；Train on negative examples with high token overlap but different semantics

### case_id=1930 FP lexical_or_api_overlap

- 方法: `run` vs `doVersionCheck`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches a tile from a data source by constructing a URL, reading GeoJSON data, converting it to vector tile geometry, and adding features to the data loader.
- B 摘要: Fetches a version check URL, reads properties from the response, and calls a version comparison method if both development and stable build versions are present.
- 静态失败原因: Static models like BERT may overemphasize overlapping API tokens (URL, openStream, BufferedReader, readLine) and ignore the differing high-level semantics and data flow.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically marks functions as clones only if they exhibit significant behavioral similarity beyond common API usage. Here, the shared pattern (read URL, parse lines) is too generic and the specific tasks differ, so BCB would label as non-clone.
- 共享行为: Both open a URL and read lines from an input stream using BufferedReader；Both handle IOException with error handling；Both use a while loop to read lines until null
- 行为差异: Different purpose: tile loading vs version checking；Different data processing: parsing GeoJSON and extracting geometries vs parsing version strings；Different output: adding to data loader vs calling a helper method；One uses synchronization on lauchedHTTPRequests, the other does not
- 修正建议: Incorporate dataflow-aware features to distinguish different processing logic on read data；Add negative examples combining similar boilerplate with disparate functionality；Use graph-based representations that capture structural differences in control flow and data dependencies

### case_id=1931 FP boilerplate_overlap

- 方法: `main` vs `readAndRewrite`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.98`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Main method that reads a Prolog file, parses it, generates adapter code, and writes a JAR file with adapters.
- B 摘要: Method that reads a DICOM image file, processes pixel data, and writes the image out to another file.
- 静态失败原因: The static predictor likely overemphasized superficial similarities such as file I/O operations, exception handling, and console output, while missing the completely different domain logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels these as non-clones because they perform entirely different tasks with no shared functionality.
- 行为差异: Different domains: adapter generation vs DICOM image processing；Different input/output formats and processing steps；No overlap in core functionality or algorithms
- 修正建议: Improve training to focus on domain-specific semantics rather than boilerplate patterns；Use dataflow analysis to capture core operations；Incorporate method name and context information

### case_id=1932 FP lexical_or_api_overlap

- 方法: `main` vs `getFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: A main method that processes command-line arguments, reads a Prolog file, parses it, generates adapters, and writes output to a JAR file.
- B 摘要: A method that retrieves a file, either from the local directory or by copying a classpath resource to the local directory.
- 静态失败原因: Static BERT models may be misled by lexical overlap (e.g., File, URL, IOException) and similar exception handling patterns, ignoring the radically different overall logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clones when functions have completely different purposes and control flows despite sharing some API calls.
- 共享行为: Both use File and URL objects；Both may throw IOException；Both involve reading/writing files
- 行为差异: Function A is a complex main entry point with multiple steps; Function B is a simple utility method；A generates code and writes JAR; B copies a resource to local file；A uses command-line arguments; B uses system property for current directory；A has extensive error handling and output; B returns a File or throws exception
- 修正建议: Improve training to emphasize high-level control flow differences；Use structural or dataflow-based representations；Incorporate more negative examples with partial API overlap

### case_id=1933 FN benchmark_preference_bias

- 方法: `copy` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.1`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Copies a file from input to output using FileChannel transfer.
- B 摘要: Builds an edited version of a website by transforming XML and writing output files.
- 静态失败原因: Static BERT models likely underpredicted because the code structures and semantics are vastly different; the low token overlap made it easy to classify as non-clone, but BCB considered them similar probably due to annotation bias.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled these as clones due to both involving file I/O operations, but the functional intent is entirely different.
- 共享行为: Both use FileInputStream for reading file content.
- 行为差异: Code A is a simple file copy utility; Code B is a complex site generation method.；Code B involves many parameters, DOM operations, string manipulation, and multi-file processing; Code A has none.；Code B handles exceptions and debugging; Code A just rethrows IOException.；Code B writes multiple output files; Code A writes only one output file.
- 修正建议: Re-evaluate BCB annotation guidelines to ensure consistency in labeling partial functionality as non-clone.；Improve model sensitivity to distinguish low-level I/O operations from high-level business logic.

### case_id=1934 FP boilerplate_overlap

- 方法: `doVersionCheck` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Checks for a new version of jEdit by reading a version file from a URL.
- B 摘要: Searches Google Images, parses image URLs, and displays the first image on a UI component.
- 静态失败原因: The model likely over-relied on the common pattern of URL opening, reading lines, and exception handling, missing the semantic differences in the specific data processing and UI updates.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels non-clones when functions perform entirely different high-level tasks despite sharing some boilerplate I/O code.
- 共享行为: Both open a URL and read lines from the input stream.；Both use try-catch for exception handling.；Both have some form of UI interaction (showing messages/updating icons).
- 行为差异: Function A checks version/build strings from a property file; Function B parses image URLs from HTML.；Function A compares version numbers; Function B updates UI with an image icon.；Function A uses jEdit-specific classes (GUIUtilities, jEdit.getProperty); Function B uses MusicBoxView and ImageIcon.；Function A takes a View parameter; Function B takes search strings and uses global state (googleImages).
- 修正建议: Incorporate method name embeddings or topic modeling to capture purpose.；Use a more granular read of the I/O operations to distinguish data types parsed.；Add structural enforcement that API usage must be accompanied by matching data flow.

### case_id=1935 FP lexical_or_api_overlap

- 方法: `getRequestContent` vs `postData`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Opens an HTTP GET connection to a given URL and returns the first line of the response.
- B 摘要: Sends HTTP POST data to a given host and discards the entire response.
- 静态失败原因: The model likely overemphasized lexical and API overlap (e.g., URL, openConnection, BufferedReader) and the common structural pattern of opening a connection and reading, ignoring differences in HTTP method, return type, and side effects.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would label this as non-clone because functions have different HTTP methods, return types, and parameter handling; they serve distinct purposes (one is a simple getter, the other is a poster that ignores response).
- 共享行为: Both use URL and URLConnection to communicate over HTTP.；Both involve opening a connection and reading from an input stream.
- 行为差异: A uses GET method implicitly, B uses POST.；A returns the first line of response; B returns void and discards all response data.；A takes a single URL string; B takes protocol, host, form, and data separately.；A does not set request properties; B sets Content-type and Content-length.
- 修正建议: Incorporate API call sequences (e.g., setDoOutput vs not).；Use flow-sensitive analysis to distinguish return values and side effects.；Consider method signatures (return type, parameters) as features.

### case_id=1936 FN partial_functionality

- 方法: `main` vs `uploadFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a URL, extracts its zip entries, and writes each entry to a file.
- B 摘要: Uploads/copies a file to a target location, using rename if possible, otherwise byte-by-byte copy.
- 静态失败原因: Models focused on different method names, signatures, and zip-specific vs. file-rename code, missing the high-level semantic similarity of the stream copy pattern due to limited long-range dependency capture or overemphasis on lexical differences.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB considers methods performing a core stream copy operation as clones even with surrounding logic differences, especially when the core loop is structurally similar.
- 共享行为: Both methods read bytes from an InputStream and write them to an OutputStream, effectively copying data.
- 行为差异: A handles zip extraction and URL protocols; B handles file renaming and directory creation.；A's output is multiple files from zip entries; B's output is a single file.；A uses BufferedOutputStream; B does not.；A reads in BUFFER-sized chunks; B reads in 16384-byte chunks.
- 修正建议: Improve sensitivity to structural patterns like stream copy.；Incorporate dataflow analysis to capture input-output stream relationships.；Use representation learning focusing on core functionality rather than peripheral code.

### case_id=1937 FP lexical_or_api_overlap

- 方法: `main` vs `setImg`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: AdapterGenerator main method that parses a Prolog file, generates adapter classes and lookup resources.
- B 摘要: setImg method that opens a file chooser, copies an image file to an images directory, and sets the image icon.
- 静态失败原因: The static model may have over-relied on overlapping tokens like 'File', 'new File', 'IOException', 'catch', 'System.out.println', etc., without capturing the high-level semantic difference.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels non-clones when functions have different intents, even if they share some low-level patterns like file I/O or exception handling.
- 共享行为: Both perform file I/O operations (reading/writing files)；Both use try-catch for exception handling；Both have some string manipulation
- 行为差异: A generates code from Prolog; B copies an image file and sets a UI icon；A uses complex class loading and bytecode writing; B uses file streams and UI components；A is a static main method; B is an instance method for image setup
- 修正建议: Incorporate control flow and data flow analysis；Use graph-based representations that capture the overall task；Increase training data with such cross-domain false positive examples

### case_id=1938 FN partial_functionality

- 方法: `run` vs `fileDownload`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a classpath resource as text using a URL stream and updates a Swing text area.
- B 摘要: Downloads a file from a given URL to a local directory, reading bytes and writing to a file.
- 静态失败原因: Static BERT likely failed due to low token overlap (0.19), different method names and structure, and missing the conceptual similarity in stream I/O pattern, focusing instead on surface-level syntax.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label these as clones because both involve reading from a URL stream and processing data, representing a common pattern of downloading or reading resource content despite differences in source and destination.
- 共享行为: Both obtain a URL and open a stream.；Both read data in a loop and close resources.；Both handle exceptions silently or with logging.
- 行为差异: A reads from classpath resource, B from external URL.；A reads character data with UTF-8, B reads raw bytes.；A appends lines with newlines to StringBuilder, B writes bytes directly to file.；A updates a Swing component via invokeLater, B writes to FileOutputStream.
- 修正建议: Enhance model with data-flow or control-flow analysis to capture stream-reading patterns.；Add more training examples of partial functionality clones with varying I/O contexts.；Incorporate bytecode or AST-based features for functional similarity.

### case_id=1939 FN partial_functionality

- 方法: `DialogHelper` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Creates a GUI dialog to save an image from a URL to a user-specified file.
- B 摘要: Downloads a KMZ archive from HTTP and extracts its entries to local files.
- 静态失败原因: Low token overlap (Jaccard 0.122) and different method names, lack of structural alignment; static models fail to capture high-level functional similarity in file I/O operations across different patterns.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB might label this as a clone due to both functions performing file input/output and copying data from a source to a destination, considering them Type-4 functionally similar despite different contexts.
- 共享行为: Both perform file I/O operations writing to local files；Both handle input from a URL or file path
- 行为差异: A is a GUI dialog with user interaction; B is a command-line main method；A copies a single file; B unzips multiple entries；A uses FileChannel; B uses ZipInputStream；A handles file overwrite confirmation; B overwrites without prompt
- 修正建议: Incorporate graph-based data flow analysis to detect common I/O patterns；Use code contrastive learning with functional labels；Add training examples of diverse implementations of file copying/extraction

### case_id=1940 FN partial_functionality

- 方法: `run` vs `register`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Performs an HTTP GET request with basic authentication, reads the response line by line, and stores the result.
- B 摘要: Registers a user by encoding password, setting up user details, making an HTTP GET request to a forum to set forum ID, persisting the user, and sending confirmation email.
- 静态失败原因: Low token Jaccard (0.15) and different method names/tasks led the model to focus on high-level semantics, missing the partial functional overlap in HTTP I/O patterns that BCB recognizes.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider these clones due to the shared HTTP request-response pattern, which is a significant functional similarity under their broad Type-3/Type-4 criteria, even though the overall purpose differs.
- 共享行为: Both make HTTP GET requests by opening a URLConnection.；Both read the response line by line using BufferedReader.；Both handle input streams and close resources.
- 行为差异: Function A is a standalone HTTP GET with authentication; B is part of a registration workflow.；Function B includes password encoding, database persistence, email sending, and error handling.；Different URL construction and response processing (B parses a forum ID from response).；Different method signatures (run vs register with Object parameter).
- 修正建议: Train model to recognize partial functional clones by focusing on subgraph patterns like HTTP request handling.；Use contrastive learning with positive examples that share I/O patterns but differ in overall logic.；Incorporate fragment-level matching or API usage graphs.

### case_id=1941 FN partial_functionality

- 方法: `testNetworkHTTP` vs `doRawRequest`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: A test method that performs multiple HTTP GET requests to various URLs, discarding the response lines.
- B 摘要: A method that performs a single HTTP POST request with provided data and returns the response body.
- 静态失败原因: Static BERT/GraphCodeBERT methods may rely on lexical overlap (token Jaccard similarity is low at 0.2143) and be misled by differences in method signature, control flow (multiple vs single request), and return type, leading to a false negative.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this as a clone because both functions share the core pattern of establishing an HTTP connection, reading response lines, and are both simple HTTP request wrappers. BCB often accepts broad Type-3/4 similarity where the overall functionality (making HTTP requests) is partially aligned.
- 共享行为: Both perform HTTP requests using URLConnection；Both read response via BufferedReader in a while loop
- 行为差异: A uses GET, B uses POST；A makes multiple requests, B makes one；A discards response lines, B collects and returns them；A handles exceptions internally, B throws IOException
- 修正建议: Use graph-based representations like code property graphs to capture control and data flow similarities；Incorporate models that recognize partial functional similarity (Type-3/4 clones)；Train with diverse examples of similar but not identical HTTP request patterns

### case_id=1942 FP lexical_or_api_overlap

- 方法: `getRequestContent` vs `doVersionCheck`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads and returns the first line from a URL.
- B 摘要: Parses version information from a URL and performs a version check.
- 静态失败原因: Likely due to lexical and API overlap (URL, BufferedReader, readLine) causing the model to overlook differing control flow and purpose.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clone because the functions have different purposes and outputs; broad functional similarity is insufficient.
- 共享行为: Both open a URL and read lines using BufferedReader.
- 行为差异: A returns the first line; B parses multiple lines for specific patterns.；A does not handle exceptions or show UI; B shows wait cursor and error dialogs.
- 修正建议: Incorporate method signatures and return types.；Use dataflow analysis to differentiate output behaviors.

### case_id=1943 FN benchmark_preference_bias

- 方法: `copyResource` vs `doGet`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Copies a resource from a URL or file to a destination file using byte streams.
- B 摘要: Handles an HTTP GET request to retrieve and display a page, with access control and caching.
- 静态失败原因: Static BERT/GraphCodeBERT likely correctly predicted non-clone due to low token overlap and different control flow; the error is actually a false positive in BCB.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: The original BCB annotation likely considered the presence of I/O operations in both as partial functionality similarity, but this is too broad and not a typical clone.
- 共享行为: Both involve reading from some source and writing to an output stream.
- 行为差异: Purpose: copy vs. serve web page；Input source: file/URL vs. database；Output target: local file vs. HTTP response；Complexity: simple I/O vs. business logic and logging
- 修正建议: Re-examine BCB ground truth for this pair to correct mislabel.

### case_id=1944 FP lexical_or_api_overlap

- 方法: `readAndRewrite` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `1.0`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a DICOM file, parses pixel data, and writes the dataset to an output file.
- B 摘要: Handles UI action events to set various preferences (e.g., Graphviz path, image magick path, date format, look and feel) and possibly restart the application.
- 静态失败原因: The low token Jaccard suggests minimal lexical overlap, but the model may have been misled by both methods containing keywords like 'File', 'IOException', or 'set...' leading to a false positive, possibly due to overgeneralization in the embedding space.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB label 0 indicates no functional similarity; these methods operate in entirely different domains (image processing vs UI configuration) with no overlapping purpose.
- 共享行为: No shared functionality beyond general input/output operations.
- 行为差异: Function A processes medical image data using DICOM libraries; Function B handles UI preferences and file selection.；Function A is purely data transformation; Function B modifies application state and UI components.；Function A writes to a file; Function B stores preferences and changes UI settings.
- 修正建议: Improve model discrimination by focusing on high-level semantics rather than low-level token co-occurrence.；Use contrastive learning with harder negative pairs.；Incorporate structural or data-flow analysis to distinguish unrelated functions.

### case_id=1945 FP boilerplate_overlap

- 方法: `perform` vs `new2Password`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Performs HTTP request handling, session validation, XML construction, and classification result processing.
- B 摘要: Computes SHA-1 hash of a password string and returns it as a string.
- 静态失败原因: The model likely over-relied on superficial common patterns like try-catch, string manipulation, and method length, misinterpreting boilerplate as semantic similarity despite low token overlap.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB annotates based on substantial functional overlap. These functions are completely unrelated in purpose and implementation, so BCB correctly labels as non-clone.
- 共享行为: Both use try-catch blocks for exception handling.；Both manipulate strings.
- 行为差异: Function A handles web request/response, session, and complex XML/HTTP operations; Function B only hashes a password.；Function A has multiple conditional branches and external calls; Function B is linear and isolated.；Function A writes to HTTP connection and parses XML; Function B only performs digest.
- 修正建议: Enhance training with examples where boilerplate (e.g., try-catch) is misleading.；Incorporate structural or dataflow analysis to distinguish different tasks.；Use contrastive learning to push apart semantically different functions.

### case_id=1946 FN partial_functionality

- 方法: `sendExceptionToServer` vs `readURL`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends an exception report to a server via HTTP POST and prints the response.
- B 摘要: Reads content from a URL and prints each line to stdout.
- 静态失败原因: Low token overlap (0.222) and different method names caused the model to miss the shared URL-reading behavior. The model likely focused on syntactic differences (e.g., POST vs GET, encoding logic) and did not capture the semantic commonality of reading and printing URL content.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB annotators often consider functions that share a core behavior (reading from a URL and printing content) as clones, even if one function has additional pre-processing or different I/O patterns. Both functions achieve the goal of reading URL content and outputting it, so they are likely labeled as Type-4 clones.
- 共享行为: Both open a URL connection, read text data line by line, and print lines to the console.
- 行为差异: Function A sends data via POST before reading; Function B only reads.；Function A encodes multiple parameters; Function B has no parameters.；Function A handles specific error reporting logic; Function B is a generic URL reader.；Function A uses URLConnection with setDoOutput; Function B uses openStream.
- 修正建议: Enhance the model to recognize common I/O patterns despite low lexical overlap.；Use data-flow analysis to identify that both functions involve opening a URL and reading lines.；Incorporate control-flow and structural similarity that abstracts away parameter encoding details.；Train on more diverse examples of partial functionality clones.

### case_id=1947 FN boilerplate_overlap

- 方法: `run` vs `createPartControl`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sets up a graphical viewer and prints its contents after user selects print options.
- B 摘要: Sets up a graphical viewer as an editor part with a palette and undo/redo support.
- 静态失败原因: Static BERT models rely on token-level similarity and lexical overlap, which is very low (Jaccard 0.089). Additionally, method names differ, and the control flow is distinct, leading to a false negative prediction.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB often labels functions as clones when they share the same domain-specific API usage patterns and structural similarity, even if high-level functionality differs. Both functions are GEF viewer setup routines.
- 共享行为: Both create a ScrollingGraphicalViewer and set its root edit part, edit part factory, and edit domain.；Both create the viewer's control on a parent composite/shell.
- 行为差异: Function A opens print dialogs and executes a print operation; function B sets up a palette viewer, key handler, context menu, and listeners for selection and commands.；Function A uses ScalableFreeformRootEditPart and TableEditPartFactory; function B uses ScalableRootEditPart and BlockEditPartFactory.
- 修正建议: Use structural or AST-based similarity to capture common subroutines.；Incorporate domain-specific knowledge about GEF viewer setup patterns.；Apply graph neural networks on code property graphs to better model long-range semantic dependencies.

### case_id=1948 FP partial_functionality

- 方法: `readPage` vs `getRequestContent`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads entire content of a URL, optionally ignoring lines starting with '#', and returns it as a single string with newlines.
- B 摘要: Opens an HTTP connection to a URL and returns only the first line of the response.
- 静态失败原因: Static BERT models might have relied on lexical and API overlap: both use URL, BufferedReader, InputStreamReader, etc. The token Jaccard is 0.24, but the model might have been misled by similar API usage patterns. They might not capture that the loop structure and return statements differ significantly.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB typically does not consider functions as clones if their output or purpose is clearly different. Here, one reads the entire page and one reads just the first line, so they have distinct functionality. Even though both involve fetching from a URL, the core behavior is different.
- 共享行为: Both fetch content from a URL via HTTP；Both use BufferedReader to read；Both return a String
- 行为差异: readPage returns the full content, getRequestContent returns only the first line；readPage has optional comment filtering, getRequestContent does not；readPage uses url.openStream(), getRequestContent uses HttpURLConnection explicitly；readPage closes the reader only, getRequestContent also disconnects the connection
- 修正建议: Include richer contextual embeddings that capture control flow and data flow.；Focus on the difference in loop structure and return value.；Use graph-based representations to model the full execution semantics.

### case_id=1949 FN lexical_or_api_overlap

- 方法: `import_hints` vs `httpRequestByPOST`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads hint pieces from a file or URL and places them on a board.
- B 摘要: Sends an HTTP POST request and returns the response body as a string.
- 静态失败原因: Static models rely on lexical and structural overlap; common APIs (BufferedReader, IOException) dominate and obscure the semantic divergence.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may have labeled as clone due to shared pattern of reading lines from stream with error handling, ignoring the distinct high-level functionalities.
- 共享行为: Both use BufferedReader and InputStreamReader to read input line by line.；Both handle IOException with try-catch blocks.
- 行为差异: Different purpose: game hint placement vs HTTP communication.；Different output: boolean/piece placement vs string response.；Different error handling: returns false vs sets error codes and returns null.
- 修正建议: Use context-aware embeddings that capture high-level purpose.；Train on more diverse examples to distinguish different domains.；Incorporate dataflow or API call sequences to differentiate behavior.

### case_id=1950 FP long_range_semantics

- 方法: `actionPerformed` vs `transport`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `static_summary_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Handles GUI action events to set various preferences (graphviz, imagemagick, scaling, look&feel, etc.) and updates corresponding UI components.
- B 摘要: Recursively copies files from a source to a destination directory using FileChannel transfer.
- 静态失败原因: Static BERT likely misled by a short snippet of file-handling code in A (JFileChooser) that resembles file operations in B, or by the truncated long code causing loss of global context.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB labels non-clones when functions have no semantic overlap; A and B are completely unrelated in purpose and behavior.
- 行为差异: A is a GUI event handler for preferences; B is a file copying method.；A updates UI components and stores preferences; B performs file I/O only.；A is triggered by user actions; B is invoked programmatically with a file.
- 修正建议: Use hierarchical or modular decomposition for long functions.；Incorporate method name and surrounding class context.；Train on whole-function representations with attention mechanisms that handle long sequences.

### case_id=1951 FP lexical_or_api_overlap

- 方法: `readTwitterFead` vs `startScript`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.85`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a Twitter feed from a fixed URL using HttpClient, builds a string from the response, and returns it, with Android logging on failure.
- B 摘要: Reads a script from a URL specified in attributes, appends lines to dialog.script, and exits on IOException.
- 静态失败原因: Static BERT (e.g., GraphCodeBERT) likely over-relied on lexical overlap of common tokens like 'BufferedReader', 'readLine', 'StringBuilder', and the try-catch structure, while missing the differences in HTTP client, error handling, and return type.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the methods have different return types, error handling strategies, and semantic purposes (data retrieval vs script loading), despite sharing a common URL-reading pattern.
- 共享行为: Both open a URL and read lines of text using BufferedReader；Both iterate over lines with readLine() until null；Both concatenate lines into a string-like structure；Both handle IOException with error output
- 行为差异: Function A uses HttpClient to fetch, B uses URL.openStream()；Function A returns the built string, B modifies dialog.script and ends script；Function A logs errors, B prints to System.err and exits the program；Function A declares no exceptions, B throws SAXException
- 修正建议: Incorporate return type and exception signature into embeddings；Use dataflow analysis to distinguish side effects (e.g., modifying dialog.script vs returning a string)；Add structural features like method return type and thrown exceptions

### case_id=1952 FN partial_functionality

- 方法: `copyFile` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Copies a file from source to destination using NIO FileChannel.
- B 摘要: Builds a website for editing by transforming XML files and writing output files.
- 静态失败原因: Static BERT/GraphCodeBERT models rely heavily on token overlap and code structure similarity. The very low token Jaccard (0.067) and vastly different lengths and control flows cause the model to classify them as non-clones, missing the high-level semantic similarity recognized by BCB.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label them as clones because both functions perform file copy operations as part of their behavior, and BCB's Type-4 (semantic) clone definition often accepts partial functionality overlap, especially when one function's behavior is a subset of another.
- 共享行为: Both involve reading from a file and writing to another file or output.
- 行为差异: Function A is a simple, generic file copy.；Function B is a complex process involving XML transformation, string replacement, and multiple file operations.；Function B uses DOM and XSLT, while A uses only NIO channels.；Function B has extensive error handling and logging, A has minimal.
- 修正建议: Incorporate semantic similarity metrics that capture high-level functionality even with low token overlap.；Use graph-based models that can abstract away specific API calls and focus on data flow patterns (e.g., read-from-source and write-to-destination).；Train on datasets with more Type-4 examples to learn partial functionality matching.

### case_id=1953 FP lexical_or_api_overlap

- 方法: `loadSourceCode` vs `readUNI`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Loads source code from a file URL, applies syntax highlighting, and builds an HTML string.
- B 摘要: Reads a tab-separated file from a URL and extracts descriptions into a vector.
- 静态失败原因: High lexical overlap (URL, InputStream, readLine, exception handling) and similar boilerplate caused model to overestimate similarity.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB requires substantial functional overlap; only generic I/O pattern matches, not enough for clone label.
- 共享行为: Both open a URL stream and read lines of text
- 行为差异: Different parsing: BufferedReader vs Scanner with tab delimiter；Different output: HTML string vs vector of descriptions；Different exception handling: no explicit close in A, close in B；Different purpose: source code display vs data extraction
- 修正建议: Incorporate data flow analysis to distinguish output transformations；Fine-tune with contrastive learning to penalize superficial similarity

### case_id=1954 FP lexical_or_api_overlap

- 方法: `main` vs `processAddByURLSubmit`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Main method that parses command line arguments, reads a Prolog file, generates adapters, and writes output to a JAR file.
- B 摘要: Method that processes a URL submission by fetching XML content and handling FileNotFoundException or IOException with different error responses.
- 静态失败原因: Static BERT/GraphCodeBERT may have overemphasized shared lexical tokens (e.g., 'IOException', 'error', 'return') and similar control flow structures (try-catch, if-else), ignoring the distinct domain semantics.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels them as non-clones because their high-level functionality (adapter generation vs URL form submission) is entirely different, despite both having I/O and exception handling patterns.
- 共享行为: Both perform I/O operations (file reading vs URL streaming).；Both have conditional checks (args length vs hasError()).；Both use try-catch blocks for exception handling.
- 行为差异: Function A is a command-line tool for adapter generation; Function B is a web form submission handler.；Function A reads from a local file; Function B reads from a remote URL.；Function A writes a JAR file; Function B processes XML content.；Error handling: A prints messages and returns; B uses Session error or sets response page.
- 修正建议: Incorporate data flow or control flow graph features to capture semantic intent.；Use a model trained on diverse tasks to avoid overfitting to generic I/O patterns.；Consider API call contexts (e.g., File vs URL) to differentiate I/O sources.

### case_id=1955 FN partial_functionality

- 方法: `doGet` vs `EncodeReturn`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Handles HTTP GET request to retrieve and render a portal page with permission checks, logging, and caching.
- B 摘要: Encodes a data file using a cryptographic client and returns a combined piggybacked route file.
- 静态失败原因: The static model likely correctly identified the lack of semantic and lexical overlap, but BCB's label may be considered an outlier or mislabel. The low Jaccard similarity (0.0377) and distinct method signatures (doGet vs EncodeReturn) lead the model to predict non-clone.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled this as a clone due to both functions involving similar file output patterns (e.g., writing to a file, using FileOutputStream) and exception handling, or because of a broad interpretation of Type-4 (functionally similar) despite different domains.
- 共享行为: Both involve writing data to an output (HTTP response vs file), but with different targets and formats.；Both may involve file operations (code_a writes cache file, code_b writes multiple files).
- 行为差异: Code_a handles HTTP request/response, user permissions, page retrieval, and logging; code_b performs cryptographic encoding and channel-based file concatenation.；Code_a uses HttpServletResponse and various portal-specific classes; code_b uses CryptoClient and file channel transfer.；Code_a has extensive error handling for page not found, forbidden, etc.; code_b throws specific EncodeFailedException.；Code_a is stateful and interacts with session and portal context; code_b is a self-contained encoding routine.
- 修正建议: Improve handling of long-range semantics to ignore superficial I/O similarities.；Incorporate domain-specific knowledge to differentiate between web request handling and cryptographic encoding.；Use cross-function context, such as method name and class type, to better judge dissimilarity.

### case_id=1956 FN benchmark_preference_bias

- 方法: `readPage` vs `doTransfer`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Reads a URL's content line by line, optionally ignoring lines starting with '#', and returns the concatenated HTML as a string.
- B 摘要: Forwards an HTTP request by reading the request body and headers, making a new HTTP connection to a target URL, and writing the response back to the original response.
- 静态失败原因: The static model likely focused on low token overlap (Jaccard=0.119) and distinct control flows, missing the high-level similarity of network I/O that BCB considered.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider them clones under broad Type-4 semantic similarity as both are network I/O functions that read from a URL and process the response, even though the functionality is different.
- 共享行为: Both open a URL and read from an input stream；Both handle I/O exceptions
- 行为差异: Function A only reads and returns text; Function B performs a full HTTP proxy with request/response handling；Function A has optional comment filtering; Function B sets headers, method, and writes to output streams；Function B interacts with HttpServletRequest/Response objects; Function A does not
- 修正建议: Use a more sophisticated model that captures high-level functional patterns；Incorporate knowledge of common I/O operations to recognize partial similarity

### case_id=1957 FN partial_functionality

- 方法: `runInternal` vs `postXml`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads an OPDS catalog with pagination, handling redirects, errors, and partial loading via HTTP.
- B 摘要: Sends an XML SOAP POST request and returns the response string.
- 静态失败原因: Static BERT likely focused on token-level differences (low Jaccard similarity) and missed the structural pattern of HTTP request setup shared between the functions.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider them clones because both involve core HTTP connection boilerplate and response reading, aligning with broad Type-3/Type-4 semantic similarity.
- 共享行为: Both open HTTP connections and set request properties.；Both set connect and read timeouts.；Both handle the response input stream.
- 行为差异: runInternal uses GET-like behavior with pagination; postXml uses POST for SOAP.；runInternal has complex error handling and progress tracking; postXml throws RuntimeException on error.；runInternal parses OPDS-specific header fields; postXml sets SOAPAction header.；runInternal supports redirect following and partial loading; postXml is straightforward.
- 修正建议: Incorporate API usage pattern matching (e.g., sequence of HTTP calls) to detect common subtasks.；Use dataflow analysis to recognize similar I/O operations despite different surrounding logic.；Train on clone pairs with low lexical but high structural similarity.

### case_id=1958 FP lexical_or_api_overlap

- 方法: `issueCommandToServer` vs `getTicketsForQueue`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Sends an HTTP POST request with command and serialized change capsule, reads and returns the response.
- B 摘要: Sends an HTTP GET request to query tickets for a queue, parses ticket IDs, fetches each ticket, and returns the list.
- 静态失败原因: The static BERT likely overemphasized lexical and API-level overlaps (e.g., 'BufferedReader', 'readLine', 'URL', 'IOException') and boilerplate HTTP request patterns, while missing the semantic divergence in overall functionality.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would label these as non-clone because they perform distinct high-level operations (issuing a command vs. querying tickets) and the code structure, while both involving HTTP and line reading, serves entirely different purposes.
- 共享行为: Both use HTTP requests to communicate with a server；Both read the response line by line using BufferedReader
- 行为差异: A uses POST, B uses GET；A sends command and capsule parameters, B sends query parameters；A returns a single string, B returns a list of ticket objects；B includes error handling for non-200 responses and specific response lines, A has minimal error handling
- 修正建议: Incorporate data flow and call graph information to distinguish high-level intent；Use contrastive learning with examples that share boilerplate but differ in semantics；Introduce task-specific pre-training on code understanding benchmarks that penalize such surface-level matches

### case_id=1959 FP lexical_or_api_overlap

- 方法: `readPage` vs `checkForUpgrade`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a webpage line by line, optionally filtering lines starting with '#', and returns the concatenated content.
- B 摘要: Checks for software upgrade by querying a license server, parsing the response, updating database records and UI components.
- 静态失败原因: Static BERT/GraphCodeBERT likely overweighed the overlapping tokens (BufferedReader, InputStreamReader, readLine) and loop structure, misinterpreting them as semantic similarity while ignoring the divergent surrounding context.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically requires functional similarity beyond shared low-level IO patterns. The completely different purposes and side effects lead to a non-clone label.
- 共享行为: Both use BufferedReader to read lines from a URL stream.
- 行为差异: Function A is a simple page reader with optional comment filtering; Function B involves database operations, UI updates, and complex parsing.；Function A returns a string; Function B is void and performs side effects.；Function A has no error handling beyond exception; Function B handles various server response statuses.；Function A uses a parameter to ignore comments; Function B has no such parameter and uses many external utilities.
- 修正建议: Incorporate dataflow or control-flow analysis to differentiate utility IO from business logic.；Use function-level summarization to capture overall intent before comparing pairwise.

### case_id=1960 FP long_range_semantics

- 方法: `actionPerformed` vs `readAndRewrite`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `static_summary_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Handles GUI action events to set various application preferences (e.g., Graphviz path, ImageMagick path, date format, look-and-feel) and may restart the application.
- B 摘要: Reads a DICOM image file and rewrites it to another file using DICOM parsing and pixel data handling.
- 静态失败原因: Function A is very long with many branches, causing the model to lose sight of the overall semantics. The model might have focused on superficial similarities like file I/O or preference saving, but these are contextually different.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB annotators would deem these non-clones because they serve entirely different purposes, have no common algorithm or output, and share minimal code patterns.
- 行为差异: Completely different functionality: GUI event handling vs. DICOM image processing；No shared data flow or control flow；Different domain concepts and libraries
- 修正建议: Improve handling of long-range dependencies in code representation；Use attention mechanisms that better capture global structure；Train on more diverse pairs to avoid overfitting to boilerplate patterns

### case_id=1961 FP boilerplate_overlap

- 方法: `main` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Compresses a file using GZIPOutputStream.
- B 摘要: Handles UI actions for setting preferences like GraphViz path.
- 静态失败原因: The model likely focused on superficial similarities like try-catch blocks and return statements, ignoring the vastly different APIs and purposes.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would label as non-clone because the functionality and data flow are completely unrelated.
- 行为差异: One is a main method for file compression, the other is an event handler for UI interactions.；Code A uses FileInputStream and GZIPOutputStream; Code B uses JFileChooser and sets preferences.；Code A has a simple sequential flow; Code B has multiple conditional branches based on action commands.
- 修正建议: Incorporate AST or dataflow analysis to capture actual computation.；Use contrastive learning with hard negatives that share boilerplate but differ semantically.

### case_id=1962 FP lexical_or_api_overlap

- 方法: `copyFile` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Copies a file from source to destination with overwrite confirmation and progress display.
- B 摘要: Handles GUI action events to update application settings (e.g., Graphviz, ImageMagick path) and restart.
- 静态失败原因: Static model likely relied on lexical overlap of common terms (e.g., 'File', 'IOException', 'null', 'return') and structural patterns (e.g., conditional checks) ignoring semantics.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clones for methods with entirely different functionality despite minor API overlaps.
- 共享行为: Both involve file operations (File class usage but different purposes).
- 行为差异: copyFile performs file I/O and progress indicator; actionPerformed configures GUI settings.；copyFile is a utility method; actionPerformed is an event listener.；Different control structures: while loop vs. if-else chain.
- 修正建议: Increase focus on high-level behavior using data flow or program dependence graphs.；Use contrastive learning to distinguish methods with different intents despite token overlaps.

### case_id=1963 FN partial_functionality

- 方法: `getWebPage` vs `read`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads content from a URL and returns it as a String, throwing an Error on IOException.
- B 摘要: Reads data from a URL or file, returning a status code, with IO errors handled by setting a status variable.
- 静态失败原因: Low token Jaccard similarity (0.12) and structural differences in return type, error handling, and auxiliary file-reading branch made the model miss the shared URL reading pattern. The model likely relies on surface-level similarity and does not capture partial functionality overlaps.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as performing the core operation of reading from a URL, ignoring differences in return type and error handling, as they represent partial functionality similarity typical of Type-4 clones.
- 共享行为: Both open a URL stream and handle IOException
- 行为差异: Return type: String vs int；Function A only reads URLs, B can also read local files；Error handling: A throws Error, B sets status variable；A uses BufferedReader.readLine, B delegates to another read method
- 修正建议: Incorporate lightweight type/flow analysis to detect common IO operations (e.g., URL.openStream) despite different surrounding code.；Use graph-based representations that highlight shared API calls.

### case_id=1964 FP long_range_semantics

- 方法: `actionPerformed` vs `copyTextFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `static_summary_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Handles various GUI actions to save preferences for Graphviz, ImageMagick, and other settings.
- B 摘要: Copies a text file from source to destination using buffered streams.
- 静态失败原因: The large size and boilerplate structure of function A may have caused the model to lose semantic context, or it erroneously associated common keywords like 'File' and 'filename' with file copying logic.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB labels non-clones when functions have completely different purposes and logic, even if they both involve files.
- 行为差异: A is an event handler for multiple GUI preference settings; B is a file copy utility.；A uses JFileChooser and saves preferences; B performs I/O with BufferedInputStream/OutputStream.；A modifies UI components; B has no UI interaction.；A is long and complex with many conditional branches; B is short and linear.
- 修正建议: Improve handling of long functions by chunking or focusing on control flow.；Add more negative examples with long, multi-purpose functions to reduce false positives.；Incorporate structural information (e.g., AST paths) to differentiate event handlers from utilities.

### case_id=1965 FP lexical_or_api_overlap

- 方法: `perform` vs `getRandomGUID`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Handles HTTP request, builds XML, sends it via URL connection, parses result, and returns an ActionForward.
- B 摘要: Generates a random GUID using MD5 hashing of timestamp and random numbers.
- 静态失败原因: Likely due to token overlap from common Java boilerplate (try-catch, string buffers, method calls) and perhaps some shared keywords like 'errorMessages' or 'System.out.println' but not enough to indicate real similarity.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would not consider them clones because they have no functional overlap and perform entirely different tasks.
- 共享行为: Both use try-catch for exception handling；Both involve string manipulation
- 行为差异: A performs web request handling and XML processing; B generates a GUID；A uses Struts Action framework; B is a utility method；A has conditional logic based on session attributes; B has no such logic；A involves I/O with URLConnection; B uses MessageDigest for hashing
- 修正建议: Improve model to capture control flow and data dependencies；Use graph-based representations to differentiate web handling from hashing logic；Incorporate domain-specific knowledge about frameworks (Struts vs utility functions)

### case_id=1966 FP lexical_or_api_overlap

- 方法: `handleHandshake` vs `main`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Handles Minecraft handshake by validating username and optionally contacting session server.
- B 摘要: Reads and prints content from a fixed URL.
- 静态失败原因: Static BERT/GraphCodeBERT models may rely heavily on token-level similarity or API sequence patterns. Here both functions share common API calls (URL, BufferedReader, InputStreamReader, readLine, close), which could lead the model to overestimate similarity and ignore the divergent contexts and logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically does not consider two functions as clones when they belong to completely different domains (Minecraft client vs. simple HTTP fetch) and have different overall functionality, despite some shared API usage patterns.
- 共享行为: Both create a URL object；Both open an InputStream and wrap with BufferedReader；Both read lines from the stream；Both close the reader
- 行为差异: Function A has authentication logic and error handling for invalid usernames; Function B has none.；Function A sends network packets (addToSendQueue, networkShutdown); Function B only prints to console.；Function A's URL is constructed dynamically with session parameters; Function B uses a fixed URL.；Function A processes a handshake packet; Function B is a main entry point with no arguments used.
- 修正建议: Incorporate broader context or control flow analysis to differentiate authentication vs. simple IO.；Use function-level documentation or method name semantics as additional signals.；Apply contrastive learning to distinguish IO-heavy but semantically different functions.

### case_id=1967 FN benchmark_preference_bias

- 方法: `getFile` vs `extractUninstallFiles`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, optionally modifies its endpoint, and saves it to a temporary directory.
- B 摘要: Extracts uninstall files to a destination directory, handling upgrades by copying old setup classes and processing jar entries.
- 静态失败原因: Static BERT models likely failed because they rely on token-level and structural overlap, and while the functions share some generic patterns (file I/O, streams), the high-level semantics diverge significantly. The model may have been misled by common API calls like File, InputStream, FileOutputStream, and exception blocks.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as a clone due to superficial similarities in structure (e.g., both have loops, file channel usage, and exception handling) or a mistaken annotation in the benchmark.
- 共享行为: Both perform file I/O operations with exception handling.；Both use try-catch blocks for IOException and others.；Both involve writing to files using streams.
- 行为差异: Function A downloads a network resource (WSDL) and modifies XML; Function B manages local installer files and jar entries.；Function A is focused on a single file download and XML manipulation; Function B handles directory creation, file deletion, and zip/jar processing.；Function A has a simple return of a file path; Function B returns a File object (oldlog) and has complex upgrade logic.
- 修正建议: Improve training data by removing noisy annotations that pair unrelated functions.；Enhance model with better semantic understanding, e.g., using finer-grained AST or data flow analysis to capture intent.；Perform manual re-annotation of BCB pairs to ensure consistency.

### case_id=1968 FP boilerplate_overlap

- 方法: `sendPost` vs `issueCommandToServer`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Sends an HTTP POST request with a parameter string to a given URL and returns the response, catching exceptions and showing a message.
- B 摘要: Sends a command encapsulated in a ChangeCapsule object to a server via HTTP POST, constructing a query string with encoded parameters, and returns the response string, throwing IOException on failure.
- 静态失败原因: Static BERT models likely over-relied on token overlap (e.g., 'setDoOutput(true)', 'BufferedReader', 'readLine') and common HTTP boilerplate, ignoring differences in error handling and data construction.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB may annotate this as a non-clone because of differing error handling and parameter construction, but under broad Type-4 criteria, the core functionality of HTTP POST with response reading is similar, so BCB style could accept it as a clone.
- 共享行为: Both perform HTTP POST with data written to output stream and read response line by line.
- 行为差异: A catches exceptions and prints a message; B throws IOException.；A takes a full URL; B uses a field serverURL.；A writes raw param; B encodes parameters and constructs a query string.；A uses PrintWriter; B uses OutputStreamWriter.
- 修正建议: Train with more varied non-clone examples that share common boilerplate.；Incorporate error handling signatures and data flow analysis into the model.；Use contrastive learning to distinguish similar but semantically different code.

### case_id=1969 FN boilerplate_overlap

- 方法: `compressWithZip` vs `doGet`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Compresses multiple files into a single zip archive using ZipOutputStream.
- B 摘要: Processes an HTTP GET request to retrieve and display a web page with security checks and caching.
- 静态失败原因: The model likely focused on lexical similarities such as common keywords (IOException, FileInputStream, while loops) and structural patterns (try-catch, variable declarations), missing the vast semantic differences in the overall program behavior.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB might have labeled this as a clone due to shared boilerplate (e.g., IOException, InputStream/OutputStream usage) or a Type-4 partial similarity (both output to a stream), but the actual functionality is completely different, making it likely a false positive in the benchmark.
- 共享行为: Both involve I/O operations；Both use exception handling with try-catch
- 行为差异: Function A creates a zip file; Function B handles HTTP requests；Function A operates on file names; Function B operates on HTTP parameters and page objects；Function A writes binary data; Function B writes HTML and manages page caching；Function A has no security logic; Function B has user permission checks
- 修正建议: Incorporate data-flow analysis to distinguish different I/O targets (file vs HTTP response)；Use API-specific embeddings to differentiate file operations from web operations；Perform control-flow analysis to identify the distinct high-level purposes (archiving vs page rendering)

### case_id=1970 FN partial_functionality

- 方法: `main` vs `_checkLanguagesFiles`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a URL and extracts all entries to local files using ZipInputStream.
- B 摘要: For each language in a list, checks existence of two property files and copies content from one to the other if missing.
- 静态失败原因: Static BERT models may focus on lexical and structural similarity, which is low (token Jaccard 0.094). The two functions have different method names, significantly different control flows (while loop vs for loop with conditionals), and different exception handling. The model correctly predicted non-clone based on lack of surface similarity and different overall logic, which aligns with our analysis.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider this as a Type-4 clone because both functions perform file management tasks: opening streams, creating files, and writing data, despite different sources and structures. The similarity in using FileInputStream/FileOutputStream and the general pattern of iterating over entities (zip entries vs language list) might be considered sufficiently similar for a broad clone definition.
- 共享行为: Both involve file I/O operations using FileInputStream and FileOutputStream；Both create new files and write data to them；Both handle file streams with closing
- 行为差异: Function A downloads from a URL and unzips; B reads from existing files；A processes multiple zip entries; B processes multiple languages with conditional copy；A does not check file existence; B does；A uses ZipInputStream; B uses FileChannel for copying
- 修正建议: Improve semantic understanding: recognize that file I/O operations alone do not imply clone if the data source and processing logic differ；Use more fine-grained semantic analysis to distinguish between different types of file manipulations；Incorporate context of method invocation and external dependencies to capture overall behavior

### case_id=1971 FN partial_functionality

- 方法: `addQDInformation` vs `read`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a specific data file (qdinfo.dat) from local or URL, parses lines with 'pg ' and 'pt ' prefixes to update internal QD date and project information.
- B 摘要: Opens a file or URL by name, wraps it in a BufferedInputStream, and delegates reading to another method, returning a status code.
- 静态失败原因: GraphCodeBERT likely relied on token overlap and syntactic structure, which is low (Jaccard 0.156). It missed the high-level similarity of both performing file/URL reading operations, and may not capture partial functional overlap without explicit data flow or API call reasoning.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label them as clones because both involve reading from a file or URL, which is a common functional category (Type-4 clone). The broader annotation preference might accept such similarity as a clone despite syntactic differences.
- 共享行为: Both functions open and read from a file or URL.；Both handle IOException by catching and either ignoring or setting error status.
- 行为差异: addQDInformation parses specific formatted data; read is generic and does not parse content.；addQDInformation conditionally updates based on file modification time; read does not.；addQDInformation updates internal state (_qdDate, info._qdValue); read returns a status integer.；addQDInformation uses BufferedReader and LineNumberReader; read uses BufferedInputStream.
- 修正建议: Enhance model to recognize functional categories like file/URL reading despite different specific behaviors.；Incorporate data flow information to capture similarity in input sources and basic read operations.；Use contrastive learning with broader clone definitions from BCB to handle Type-4 clones.

### case_id=1972 FN benchmark_preference_bias

- 方法: `execute` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Executes file conversion from source to destination using a reader and writer with error handling.
- B 摘要: Launches a NexOpen project configuration by processing pom files and setting up reverse engineering.
- 静态失败原因: Static models like GraphCodeBERT rely on token overlap and structural similarity; here the token Jaccard is very low (0.068) and data flows are completely different, so the model correctly predicted non-clone. The mismatch is due to BCB label being incorrect.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as a clone due to superficial structural similarities (both are void methods with similar parameter count, both perform I/O and error handling). However, the functional domains are entirely different, suggesting a likely annotation error in BCB.
- 共享行为: Both use try-catch-finally for resource management and exception handling；Both perform I/O operations (reading/writing files or streams)；Both include logging or informational output
- 行为差异: Function A converts a source file to a destination file using a specified conversion type and configuration；Function B handles Eclipse launch configuration, validates project existence, processes multiple XML files, and manages project build；Function A is a simple file-to-file conversion; Function B involves complex Eclipse RPC, Maven project structure, and persistent properties；Function B uses assertions and throws CoreException, while Function A uses FileNotFoundException and IOException
- 修正建议: Re-evaluate the BCB label for this pair; it appears to be a false positive in the benchmark.；Alternatively, train models to better capture domain-specific semantics rather than relying on token similarity alone.

### case_id=1973 FP lexical_or_api_overlap

- 方法: `readUNI` vs `getXML`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a tab-separated file from a URL and populates a vector with concatenated ID and description.
- B 摘要: Fetches text content from a URL and returns it as a single concatenated string.
- 静态失败原因: The model likely over-relied on surface-level lexical and API overlap (URL, openStream, MalformedURLException, try-catch, stream closing) while neglecting the critical differences in data processing logic. The high token similarity in boilerplate code overshadowed the distinct semantic operations.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB annotations typically consider non-clones if the core functionality differs significantly. Here, despite both reading from URLs, the data extraction logic (parsing vs. raw concatenation) and output forms are distinct, likely leading to a non-clone label.
- 共享行为: Open a URL and read its content line by line；Handle MalformedURLException and other IOExceptions；Close the input stream in a finally block (A) or after reading (B)
- 行为差异: A expects tab-separated fields and skips first line; B reads all lines indiscriminately；A outputs via side effect on a Vector; B returns a String；A uses Scanner with delimiter; B uses BufferedReader.readLine()；A ignores the second token in each line; B appends each line directly
- 修正建议: Enhance training with contrastive examples that emphasize I/O logic over common boilerplate；Incorporate data-flow analysis to distinguish different transformations of input data；Use structure-aware models that differentiate between distinct parsing patterns (e.g., Scanner with delimiter vs. BufferedReader.readLine)

### case_id=1974 FP lexical_or_api_overlap

- 方法: `loadExistingAntlibs` vs `downloadModel`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Loads ant library definitions from classpath resources by iterating over URLs and reading lines to resolve antlib URIs.
- B 摘要: Downloads an RDF model from a given URL using HTTP connection and reads it into a Model object.
- 静态失败原因: The model likely relied on lexical and API overlap (e.g., URL, InputStream, IOException, RuntimeException, try-catch) and similar control flow structures (looping vs. conditional), which led to a false positive clone detection. It failed to capture the distinct high-level intentions.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels this non-clone because the functions have fundamentally different purposes (loading ant library definitions vs. downloading an RDF model) despite similar low-level I/O patterns. The annotation preference tolerates partial similarity but not fully unrelated functionality.
- 共享行为: Both open an InputStream from a URL/connection and read data.；Both handle IOException and wrap it in RuntimeException.；Both use try-catch blocks and close streams in the normal flow.
- 行为差异: A iterates over multiple resources and lines, resolving URIs for each antlib; B makes a single HTTP request and reads a model.；A uses ClassLoader and system resources; B uses URLConnection with HTTP headers.；A calls loadAntLib for each package; B returns a Model object.
- 修正建议: Incorporate AST or data-flow features to distinguish high-level purpose.；Add context-aware training with more examples of semantically different functions that share API usage.；Use contrastive learning to penalize shallow API matches without semantic alignment.

### case_id=1975 FP lexical_or_api_overlap

- 方法: `md5` vs `perform`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Computes MD5 hash of a string and returns its hex representation.
- B 摘要: Handles a web action for classifying concepts, including session validation, role processing, and remote service communication.
- 静态失败原因: The model may have been misled by superficial lexical overlaps (e.g., 'StringBuffer', 'for', byte operations, exception handling) and boilerplate patterns common in many Java methods, without understanding the overall semantics.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled non-clone because the functions have entirely different purposes, no shared algorithmic logic, and no significant code reuse; BCB typically requires some functional similarity for positive clones.
- 共享行为: Both use StringBuffer to build strings；Both handle exceptions；Both contain loops
- 行为差异: A is a cryptographic hash function; B is a web action handler with side effects；A has no side effects; B modifies session and communicates with external URL；A returns a string; B returns an ActionForward object；A is short and focused; B is long and complex with multiple concerns
- 修正建议: Incorporate structural or control flow analysis to differentiate between hash computation and web request handling.；Train on more diverse negative examples that share local patterns but differ in global semantics.；Use graph-based representations (e.g., AST or CFG) to better capture method intent.

### case_id=1976 FN benchmark_preference_bias

- 方法: `getEncoding` vs `handledRun`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Retrieves the character encoding from a URL by checking HTTP headers and HTML meta tags.
- B 摘要: Downloads and updates gamedata XML file from an online source, comparing versions.
- 静态失败原因: Static BERT likely correctly identified they are different due to low token overlap and different method names/purposes; it predicted non-clone, which aligns with semantic analysis.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might have considered both as involving URL reading and buffered input, but this is a very broad criterion; likely an error in BCB annotation or an outlier.
- 共享行为: Both open a URL and read data using BufferedReader.
- 行为差异: Function A extracts encoding from headers and content; function B downloads and saves a file based on version check.；Function A returns a String; function B writes to a file and updates game database.；Function A handles URL connection and header parsing; function B handles version comparison and file output.
- 修正建议: Improve classifier to be more sensitive to shared I/O patterns?；But careful: this pair is likely not a clone, so classifier should not be changed; instead, benchmark annotation may be noisy.

### case_id=1977 FP lexical_or_api_overlap

- 方法: `executePost` vs `SRWGuiClient`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Executes an HTTP POST request with given URL and parameters, returns response string or null on error.
- B 摘要: Constructs a Swing browser GUI, reads content from a URL, optionally applies XSLT transformation, and displays HTML.
- 静态失败原因: Static BERT may have been misled by lexical overlap (e.g., 'url', 'BufferedReader', 'StringBuffer', 'try-catch') and common API usage patterns (URL, InputStreamReader, IOException). It might have overgeneralized the presence of these tokens as evidence of similarity while ignoring the divergent structure and purpose.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this non-clone because the functions have completely different intents and outputs: one is a low-level network utility, the other is a high-level GUI constructor. Even if they share some boilerplate (URL, BufferedReader), the core functionality is distinct, and BCB tends to treat such cases as non-clones.
- 共享行为: Both use URL and BufferedReader to read network data.；Both use StringBuffer to accumulate content line by line.；Both handle exceptions with try-catch and have IO-related code.
- 行为差异: A is a stateless utility method for HTTP POST; B is a constructor that builds a full GUI with buttons, scroll panes, and editor panes.；A writes POST data and explicitly returns the response string; B reads data, optionally transforms XML, and displays content in a JEditorPane.；B performs complex operations like XSLT transformation and hyperlink handling, which A does not.
- 修正建议: Incorporate control-flow and data-flow features to distinguish I/O patterns.；Use type information (e.g., HttpURLConnection vs. URL, GUI components) to differentiate.；Include method name and class context as additional features.；Apply contrastive learning to penalize similarity from common boilerplate.

### case_id=1978 FN long_range_semantics

- 方法: `sendExceptionToServer` vs `doVersionCheck`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends exception details to a remote server via HTTP POST and prints the response.
- B 摘要: Checks for software version updates by reading a remote version file and parsing build numbers.
- 静态失败原因: Static models like GraphCodeBERT focus on token-level similarity and miss the high-level structural pattern of URL reading. Low Jaccard (0.2056) indicates low lexical overlap, but the functional similarity in terms of 'read from URL' pattern is not captured.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB often labels Type-3 clones where control flow structure and overall I/O pattern match, even if purpose differs. Both functions perform network communication with similar boilerplate (URL opening, buffered reading, exception handling).
- 共享行为: Both open a URL and read lines from input stream.；Both handle IOException with error messages.；Both use BufferedReader to read response.
- 行为差异: A sends data via POST, B only reads via GET.；A constructs a complex query string with encoded parameters, B reads lines and parses specific prefixes.；A handles multiple optional parameters, B calls a helper function after parsing.；A prints responses to console, B shows error dialogs.
- 修正建议: Use graph-based representations that capture control flow and data flow independently of variable names.；Add structural features like number of loops and I/O operations.；Use pre-training on code clone tasks with contrastive learning on function-level patterns.

### case_id=1979 FN partial_functionality

- 方法: `modifyApplicationMessage` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Modifies a property value in a locale-specific properties file, optionally copying from a default English file if the locale file does not exist.
- B 摘要: Copies a file from source to destination using FileChannel.
- 静态失败原因: Static BERT/GraphCodeBERT likely overemphasized method names and overall structure, missing the partial file copy substructure. Low token Jaccard (0.168) and divergent API usage (FileChannel vs FileReader/FileWriter) obscured the common snippet.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider the file copy snippet in A when the locale file is missing as functionally equivalent to B's copyFile, thus classifying them as Type-4 clones due to shared file copying behavior despite different overall purposes.
- 共享行为: Both copy content from one file to another (conditional in A).；Both use file I/O operations with streams/channels.
- 行为差异: A's primary goal is to modify a property; B solely copies files.；A's copy is byte-by-byte with FileReader/FileWriter; B uses NIO FileChannel for efficient copying.；A includes parsing and modifying properties lines; B has no such logic.
- 修正建议: Enhance models to detect subgraph-level or skeleton-level similarities.；Incorporate more robust dataflow or structural alignment to capture reused functionality across different contexts.；Use contrastive learning to emphasize functional snippets over global method semantics.

### case_id=1980 FP boilerplate_overlap

- 方法: `main` vs `encodeFileToFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.99`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Main method that generates adapter classes and JAR from a Prolog file.
- B 摘要: Encodes a file to Base64 and writes to another file.
- 静态失败原因: The model was misled by lexical and structural overlaps such as try-catch-finally blocks, file I/O, and exception handling, which are common boilerplate but not indicative of semantic similarity.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels as non-clones because the functions have completely different high-level purposes (adapter generation vs. file encoding), even though they share boilerplate I/O patterns.
- 共享行为: Both use file I/O streams；Both handle exceptions with try-catch-finally；Both have printStackTrace calls
- 行为差异: Function A parses Prolog and generates adapter metadata; Function B only encodes binary data；Function A writes multiple artifacts (JAR, serialized map); Function B writes a single encoded file；Function A involves reflection and class loading; Function B does not
- 修正建议: Incorporate dataflow and control-flow analysis to distinguish core logic from boilerplate；Use long-range dependency modeling to capture overall program purpose；Add fine-grained type and API usage features

### case_id=1981 FN partial_functionality

- 方法: `login` vs `PageLoader`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.4`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Logs into a web service by sending email and password, extracts session ID from response.
- B 摘要: Loads a web page content by reading all lines from a URL into a string.
- 静态失败原因: Static BERT models often rely on token-level similarities and global context; here the token Jaccard is low (0.186). They may be misled by the low lexical overlap and fail to recognize the structural pattern of URL handling due to the differences in method name, parameters, and error handling. The model might not have learned to treat open-URL/read-close as a reusable clone pattern when surrounded by different code.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider this a Type-3 near-miss clone because both functions share the core pattern of URL opening, stream reading, and closing, even though one additionally writes data and has different input/output handling. The partial functionality overlap (network I/O) is sufficient for BCB's broad criteria.
- 共享行为: Both create a URL and open a connection；Both read from a BufferedReader wrapping an InputStream；Both close the stream after reading
- 行为差异: Function A sends POST data (URL-encoded credentials) while Function B only reads (GET)；Function A extracts only the first line for session ID; Function B concatenates all lines；Function A returns a String; Function B is a constructor that sets a member variable；Function A catches exceptions and prints error; Function B throws exception
- 修正建议: Improve representation of API call patterns (e.g., URL open, stream read) beyond token overlap；Incorporate structural embedding that captures common I/O patterns；Use dataflow to identify that both functions create a URL, open a stream, read, and close, despite different operations

### case_id=1982 FN benchmark_preference_bias

- 方法: `main` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.2`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Creates a signed PDF, then verifies signatures and extracts revisions.
- B 摘要: Downloads a KMZ file from a URL, unzips and extracts its contents to disk.
- 静态失败原因: The static model likely relied on token similarity and control-flow structure, which are very different; it correctly identified them as non-clones but was overridden by BCB's broad similarity preference.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have considered both as 'file I/O examples' and labeled them as Type-4 clones due to similar high-level task of processing a file, despite completely different low-level operations.
- 共享行为: Both use System.out.println for progress messages；Both involve reading from an input source and writing to disk
- 行为差异: Function A deals with PDF signing and certificate verification；Function B downloads and extracts a ZIP archive from a URL；Function A uses complex iText APIs, function B uses basic Java ZIP/IO APIs；Function A has extensive exception handling, function B throws Exception
- 修正建议: Use domain-aware embeddings；Incorporate task-level semantics；Improve benchmark annotation consistency

### case_id=1983 FN benchmark_preference_bias

- 方法: `runInternal` vs `loadExistingAntlibs`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads and parses OPDS catalog from an HTTP URL, handling redirects and content types, then either loads next page or downloads book.
- B 摘要: Loads existing antlib definitions by reading antlib resource files from classpath, resolving URIs, and calling loadAntLib for each.
- 静态失败原因: Static BERT/GraphCodeBERT likely learned to reject the clone due to low token overlap and different method names/domains, despite BCB's broad similarity criteria. The model correctly identified them as non-clones, but BCB annotation is questionable.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have considered both as 'reading input from a URL and processing lines', which is a very broad Type-4 similarity often accepted in BigCloneBench, but the specific domains and logic are entirely different.
- 共享行为: Both operate on URLs by opening streams and reading data；Both handle IOException and may use BufferedReader to read lines；Both involve iterating over multiple URLs or resources
- 行为差异: Function A uses HTTP connection with timeout, headers, redirect handling, response code checking; function B does not use HTTP at all；Function A parses OPDS XML and handles book downloads; function B reads antlib package names and resolves antlib.xml URIs；Function A has a loop with partial loading and next-page logic; function B simply iterates over resources；Function A includes UI progress updates and callbacks; function B does not
- 修正建议: Review BCB annotation guidelines to ensure such broad Type-4 similarities are not over-labeled as clones；Include more diverse negative examples in training to reduce benchmark bias；Use fine-grained semantic analysis to distinguish different domains

### case_id=1984 FP lexical_or_api_overlap

- 方法: `getContent` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Utility function that executes an HTTP request and returns the response body as a string.
- B 摘要: Function that performs a Google image search, parses image URLs from the response, updates a global list, and modifies UI components.
- 静态失败原因: Static model likely relied on lexical and API overlap (e.g., BufferedReader, InputStreamReader, while loops) without capturing the different high-level intents and additional logic in function B.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as not clone because the functions have different purposes (generic utility vs. specific search with UI side effects) and only share common boilerplate for HTTP requests.
- 共享行为: Make an HTTP GET request；Read response line by line into a string；Handle exceptions
- 行为差异: getContent returns the response string; googleImageSearch parses and stores image URLs；getContent uses HttpClient; googleImageSearch uses HttpURLConnection；googleImageSearch updates UI and disables/enables buttons; getContent has no UI interaction；googleImageSearch has specific parsing for Google image results; getContent is generic
- 修正建议: Train with more negative examples that share common APIs but differ in intent；Incorporate control flow and data flow analysis to distinguish utility vs. specific tasks；Use documentation or method names to inform about differing purposes

### case_id=1985 FN benchmark_preference_bias

- 方法: `doImageProcess` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Processes an image request, optionally resizing, and writes the image bytes to the HTTP response output stream.
- B 摘要: Downloads a KMZ file from a URL, reads it as a ZipInputStream, and extracts each entry to a file.
- 静态失败原因: GraphCodeBERT or similar models may have been misled by the low token Jaccard and lack of structural similarity, leading to a correct non-clone prediction. Alternatively, if the model was overly reliant on API usage patterns, it might have missed the true semantic divergence.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled these as clones due to a superficial similarity in using URL.openStream() and writing to output streams, considering both as 'downloading and processing data from a URL'. However, the actual functionality is entirely different.
- 共享行为: Both open an InputStream from a URL using url.openStream().；Both read from an InputStream and write to an OutputStream.
- 行为差异: A writes to an HTTP response OutputStream; B writes to file-based OutputStreams for each zip entry.；A resizes images based on parameters; B extracts zip entries without any image processing.；A uses image-specific format and type handling; B uses zip-specific entry iteration.；A has conditional logic for image size, while B has a loop over zip entries.
- 修正建议: Re-evaluate BCB label; these functions are semantically unrelated.；If aiming for BCB consistency, consider adding pattern-based rules to capture shallow I/O similarities.

### case_id=1986 FP boilerplate_overlap

- 方法: `sendPost` vs `readReferenceText`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Sends an HTTP POST request to a given URL with parameters and returns the response body as a string.
- B 摘要: Reads a text file from a plugin resource directory given an identifier and returns its content as a string.
- 静态失败原因: High lexical overlap from common stream-reading boilerplate (URL, BufferedReader, InputStreamReader, readLine, string concatenation) misled the model into classifying them as similar, ignoring the distinct semantics of HTTP vs file I/O.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels non-clones when the core functionality differs significantly despite shared boilerplate; here one is HTTP POST and the other is file read, so non-clone is expected.
- 共享行为: Both use BufferedReader and InputStreamReader to read text line by line；Both handle exceptions；Both build a string from the read lines
- 行为差异: Function A uses HttpURLConnection to send POST data and read response; Function B uses URL.openStream() to read a local file resource；Function A is static; Function B is an instance method；Function A catches Exception generically; Function B catches specific IO exceptions and throws a custom NoContentException；Function A sets HTTP request properties and writes parameters; Function B does not perform network I/O
- 修正建议: Incorporate method-level context such as method name, parameter types, and class type to distinguish static vs instance and network vs file operations；Add attention to exception handling patterns and I/O resource types

### case_id=1987 FN benchmark_preference_bias

- 方法: `encodeFileToFile` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Base64 encodes an input file and writes to output file, returning success boolean.
- B 摘要: Builds a website for editing by processing multiple pages, transforming XML/control files, and writing output files.
- 静态失败原因: The static BERT/GraphCodeBERT model likely correctly predicted non-clone because of very low token overlap and entirely different method signatures and logic. The model failed to match BCB's possibly erroneous label.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have considered the broad file I/O pattern and buffering as a Type-3/Type-4 clone, despite very different domain purposes. However, this seems unlikely given low similarity.
- 共享行为: Both perform file I/O operations: reading from input streams and writing to output streams.；Both use buffer arrays for reading/writing data.
- 行为差异: Function A is a simple one-to-one file encoding; Function B is a complex multi-page site generation with DOM/XSLT transformations.；Function A returns boolean; Function B returns void and throws multiple exceptions.；Function A uses Base64 encoding; Function B uses XSLT transformers and string replacements.
- 修正建议: Improve benchmark consistency by reviewing this pair; likely BCB label is incorrect.

### case_id=1988 FP lexical_or_api_overlap

- 方法: `GetResponse` vs `checkForUpgrade`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Makes an HTTP GET request to a URL and returns the response body as a string.
- B 摘要: Performs an upgrade check by querying a server, parsing license information, updating a database, and updating the UI accordingly.
- 静态失败原因: Static BERT or GraphCodeBERT likely relied on lexical and API token overlap (e.g., 'URL', 'openConnection', 'BufferedReader', 'readLine') and ignored the vast differences in control flow, data flow, and overall purpose, causing a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels these as non-clones because they have completely different overall functionality and only share superficial API usage (URL, BufferedReader). The annotation style in BCB favors whole-function semantic equivalence, which is clearly absent here.
- 共享行为: Both use URL and BufferedReader to read an HTTP response line by line.
- 行为差异: Function A is a simple HTTP GET returning content; function B involves database operations, UI updates, license parsing, and upgrade logic.；Function A has minimal error handling with empty catch blocks; function B has extensive control flow and data processing.；Function A's purpose is to fetch a web page; function B's purpose is to manage software upgrades.
- 修正建议: Incorporate control flow and data flow analysis to distinguish functions with similar API patterns but different logic.；Use program slicing or structural embeddings that capture the overall function behavior rather than just token sequences.；Train on more diverse negative pairs to reduce sensitivity to common API usage.

### case_id=1989 FP partial_functionality

- 方法: `perform` vs `hash`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Handles a web request to classify a concept by building XML, sending it via HTTP, and parsing the response.
- B 摘要: Computes MD5 hash of input strings and prints the hexadecimal result.
- 静态失败原因: The model likely over-fitted to superficial structural patterns like try-catch blocks, loops, and StringBuffer usage, ignoring the overall functionality and method context.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB labels non-clones because functions have completely different purposes and outputs, even if they share some low-level string manipulation patterns.
- 共享行为: Both use StringBuffer for string building；Both have loops (while or for) for processing data
- 行为差异: Different functionality: web request handling vs. hash computation；Different return types: ActionForward vs. void；Different input types: multiple parameters vs. varargs strings；Different I/O: HTTP connection vs. console output
- 修正建议: Incorporate data flow analysis to distinguish different processing pipelines；Use method name and class context as additional features；Train on more diverse negative examples with similar boilerplate

### case_id=1990 FP lexical_or_api_overlap

- 方法: `combineJs` vs `readData`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Downloads JavaScript files from URLs, optionally minifies them, concatenates them, and saves to a target file.
- B 摘要: Parses comma-separated string fields to populate various character set collections used in a transliteration/character mapping context.
- 静态失败原因: Likely due to superficial lexical/API overlap (e.g., both use FileReader, IOUtils, try-catch for IOException) and boilerplate patterns (file I/O, loop structures). The model may have been misled by these common Java idioms into predicting clone despite very low token Jaccard.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would not label these as clones because they have no functional similarity; even Type-4 (semantic) clones require some shared functionality, which is absent here.
- 行为差异: Entirely different purpose (JS file combination vs. character set initialization).；Different input/output: combineJs takes URL, list of Nodes, and list of Files; readData uses static class fields and initializes sets.；Different internal logic: combineJs uses I/O streams, file copying, minification; readData uses StringTokenizer and populates HashSets.；No overlap in domain-specific operations (JavaScriptMinification vs. character classification).
- 修正建议: Incorporate data-flow analysis to capture actual data transformations.；Use program dependency graphs or abstract syntax tree differences.；Train on more diverse negative samples with high API overlap but different semantics.

### case_id=1991 FN lexical_or_api_overlap

- 方法: `copyResource` vs `copyFromFileToFileUsingNIO`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.95`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource from a URL or local file to a destination file using byte-by-byte stream I/O.
- B 摘要: Copies a local file to another file using NIO FileChannel transferTo.
- 静态失败原因: Low token Jaccard (0.20) and distinct API keywords (URL, FileChannel, transferTo) lead the model to miss the semantic overlap; it relies on surface-level similarity.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB often labels functions with similar core behavior (e.g., file copying) as clones despite different I/O mechanisms, as they are functionally interchangeable in many contexts.
- 共享行为: Both copy data from a source to a destination file；Both close streams/channels after copying；Both throw IO-related exceptions
- 行为差异: A can read from URL or local file; B only reads from local file；A uses byte-by-byte loop; B uses bulk transfer via transferTo；A throws generic Exception; B throws FileNotFoundException and IOException
- 修正建议: Train with diverse implementations of same functionality (e.g., stream vs. NIO copy)；Incorporate data flow or operation sequence embeddings (read, write, close)；Use contrastive learning to pull together functions with similar high-level actions

### case_id=1992 FN partial_functionality

- 方法: `copyResource` vs `encodeFileToFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource (URL or file) to a destination file byte by byte.
- B 摘要: Encodes a file to Base64 and writes the result to another file using buffered I/O.
- 静态失败原因: The low token Jaccard (0.197) due to different method names, API calls (URL vs FileInputStream, Base64), and error handling patterns likely caused the static model to miss the high-level similarity of copying data.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as file copy/transformation operations where the core loop structure is similar, and the difference in encoding is a minor functional variation acceptable for Type-3/4 clones.
- 共享行为: Reads from an input source and writes to an output file；Uses a while loop to transfer data
- 行为差异: Function A copies bytes without transformation; function B applies Base64 encoding；Function A uses byte-by-byte read/write; function B uses buffered reads of 64KB chunks；Function A throws exceptions; function B catches exceptions and returns success flag；Function A can read from a URL; function B only reads from a file
- 修正建议: Incorporate data flow analysis to recognize that both functions perform a read-write loop regardless of the specific I/O classes；Use structure-based matching that ignores minor variations in buffer size and error handling；Train on more examples where one function adds a transformation (encoding/decoding) to still be considered similar

### case_id=1993 FP boilerplate_overlap

- 方法: `run` vs `downloadModel`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads from a hardcoded URL and discards all data, performing no operation on the content.
- B 摘要: Downloads an RDF model from a given URL by opening an HTTP connection, setting headers, parsing the input stream into a Model, and returning it.
- 静态失败原因: The static model likely overemphasized the structural similarity of the try-catch blocks with URL opening, input reading, and exception handling, while ignoring the crucial semantic difference in the loop body and the subsequent model processing. The model may have matched the API call sequence without understanding the purpose.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB considers these non-clones because the core functionality is entirely different (discarding vs. parsing and returning RDF data). The similarity in boilerplate I/O code is not sufficient for clone annotation, as BCB focuses on functional behavior rather than structural patterns.
- 共享行为: Open a URL connection and read from its input stream；Catch MalformedURLException and IOException；Close the input stream in the try block
- 行为差异: Function A discards read data; Function B parses data into an RDF Model；Function A returns void; Function B returns a Model object；Function A uses BufferedReader; Function B uses InputStream directly；Function A has empty catch blocks; Function B logs and throws RuntimeException
- 修正建议: Incorporate data-flow analysis to track how the read data is used；Train on more diverse examples to reduce sensitivity to common I/O patterns；Add attention to return types and method signatures

### case_id=1994 FP lexical_or_api_overlap

- 方法: `get` vs `doVersionCheck`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches game records from an HTTP server using GET with latitude, longitude, and count headers, parses lines into GameRecord objects, and returns an array or null on failure.
- B 摘要: Checks for a newer version of jEdit by reading a version file from a URL, extracting version and build strings, and displaying a UI dialog if a newer version is available.
- 静态失败原因: Static BERT models rely on token overlap and surface patterns, and may be misled by the similar boilerplate of URL opening, reading, and parsing, which are common in many Java methods.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels non-clones when methods have different purposes and outputs, even if they share a common structure of reading from URL and parsing lines.
- 共享行为: Both open a URL and read lines from an input stream；Both parse lines to extract information；Both handle IOException
- 行为差异: A uses HttpURLConnection with custom headers; B uses URL.openStream()；A parses lines not starting with '#' into GameRecord objects; B parses lines starting with '.version' or '.build'；A returns an array of GameRecord or null; B returns void and shows UI dialogs；A prints error to stdout; B shows error dialog
- 修正建议: Incorporate dataflow analysis to distinguish different parsing logic and output types；Use type information and method signatures to differentiate the semantic roles；Train on more diverse examples to reduce reliance on boilerplate patterns

### case_id=1995 FN benchmark_preference_bias

- 方法: `send` vs `doGet`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Sends an email with attachments, headers, and priority, handling quota and persistence.
- B 摘要: Handles HTTP GET request to render a portal page, with caching and access control.
- 静态失败原因: Static BERT/GraphCodeBERT likely correctly predicted non-clone (0) due to low lexical overlap and clear semantic differences; the BCB label is likely incorrect.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB label 1 may be a labeling error, as the functions perform entirely different tasks with no semantic similarity beyond generic exception handling and property retrieval.
- 共享行为: Both use try-catch blocks for exception handling；Both retrieve configuration properties；Both involve some form of response output
- 行为差异: Function A constructs and sends email messages; Function B handles HTTP requests and renders web pages；Function A deals with MIME email headers and attachments; Function B deals with HTTP request parameters and page rendering；Function A has quota checking and saving sent messages; Function B has caching and user permission checks
- 修正建议: Re-evaluate the BCB label for this pair to correct mislabeling；Improve training data quality to avoid such false negatives

### case_id=1996 FP boilerplate_overlap

- 方法: `executePost` vs `callApiPost`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Makes HTTP POST request with fixed headers and returns response as a string, or null on exception.
- B 摘要: Makes HTTP POST request with configurable headers and returns response as an InputStream, validating response code and throwing custom exception on error or status mismatch.
- 静态失败原因: The model may have focused on lexical/API overlap (both use HttpURLConnection, setRequestMethod('POST'), write to output stream, read response) and missed the differences in error handling, return type, and parameter handling due to boilerplate overlap.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB annotators likely mark as non-clone because the functions differ in return type, error handling, and overall API behavior, making them functionally different despite both doing HTTP POST.
- 共享行为: Both perform HTTP POST using HttpURLConnection；Both write parameters to output stream；Both handle connection and read response
- 行为差异: Return type: String vs InputStream；Error handling: returns null vs throws exception；Parameter format: raw string vs Map；Headers: fixed vs configurable from map
- 修正建议: Increase attention to return type and error handling；Use structure-aware representations to differentiate similar boilerplate code；Include dataflow analysis to track exception propagation and return values

### case_id=1997 FP lexical_or_api_overlap

- 方法: `doVersionCheck` vs `getFrameworkFactory`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a version check URL, parses version and build lines, and notifies user of updates or errors.
- B 摘要: Reads a service configuration file to instantiate and return an OSGi FrameworkFactory, throwing an exception if not found.
- 静态失败原因: Static embedding models like GraphCodeBERT may overemphasize surface-level API usage (URL, BufferedReader, readLine) and miss the semantic context and overall purpose.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB recognizes these as functionally distinct despite similar I/O boilerplate, so labels non-clone.
- 共享行为: Both open a resource (URL or classpath) and read lines via BufferedReader；Both check lines for condition (startsWith vs comment check)
- 行为差异: A performs UI operations (show/hide wait cursor, show messages), B does not；A catches IOException and shows error dialog; B throws Exception on failure；A reads a version/build lines for comparison; B reads a class name to instantiate；A has no return value; B returns an instance of FrameworkFactory
- 修正建议: Incorporate data flow analysis to capture different return types and side effects；Train with more diverse pairs where I/O patterns are not indicative of semantic equivalence；Use contrastive learning to distinguish boilerplate from core logic

### case_id=1998 FN partial_functionality

- 方法: `copyResource` vs `addToArchive`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource from a URL or file to a destination file using byte-by-byte streaming.
- B 摘要: Adds an input stream as an entry to a zip archive using IOUtils.copy.
- 静态失败原因: Low lexical overlap (token Jaccard 0.09) and different method structure/method names caused the model to miss the semantic similarity in the stream-copy pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB considers the core functionality of copying from an input stream to an output stream sufficient for Type-3/4 cloning, despite differences in output target and implementation details.
- 共享行为: Both read from an input stream and write to an output stream；Both handle I/O streams and involve data copying
- 行为差异: A resolves the input source dynamically (URL or file), while B receives an InputStream directly；A writes to a FileOutputStream, while B writes to a ZipOutputStream (compression)；A uses a manual byte-by-byte loop, while B uses IOUtils.copy (buffered)；A returns void, while B returns a URL and also creates ZipEntry metadata
- 修正建议: Incorporate data-flow analysis to capture stream connections；Use program slicing to isolate the copy logic；Augment training with examples of stream copy in varying contexts

### case_id=1999 FP lexical_or_api_overlap

- 方法: `copyFile` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Copies a file from source to destination using NIO FileChannel, ensuring parent directories exist and handling resource cleanup.
- B 摘要: Handles action events in a settings GUI, updating various preferences and UI components based on user input.
- 静态失败原因: Static BERT likely focused on lexical overlap (e.g., 'File', 'getAbsolutePath', 'file') and ignored the vast difference in control flow and semantics, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would correctly label as non-clones because they share no meaningful functionality or structural similarity; the token Jaccard is very low (0.056), and the methods have entirely different purposes.
- 共享行为: Both involve file operations (A directly copies files; B uses a file chooser to select files).
- 行为差异: A is a focused I/O utility; B is a long GUI event handler with many conditional branches.；A performs file copying via channels; B updates preferences and UI state.；A has no user interaction; B relies on user input via file chooser and other components.；A is ~50 lines; B is ~200+ lines with multiple unrelated sub-tasks.
- 修正建议: Improve model to incorporate program dependency graphs or control flow features.；Add more negative examples with similar API usage but divergent behavior.

### case_id=2000 FN lexical_or_api_overlap

- 方法: `modifyApplicationMessage` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.2`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Modifies a properties file by updating or adding a key-value pair for localization.
- B 摘要: Decompresses a gzip file by reading it and writing uncompressed content to a destination file.
- 静态失败原因: Static BERT models rely on token and structural embeddings; low token Jaccard (0.196) leads to low similarity. The model failed to recognize any deep functional similarity because none exists.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may have labeled as clone due to superficial structural similarity in file processing patterns (open, read, write, close), but this is too broad and likely an annotation bias.
- 共享行为: Both involve file I/O with reading and writing streams.；Both use try-catch blocks for exception handling.；Both close resources in finally blocks.
- 行为差异: Different input/output formats: properties file vs gzip file.；Different transformations: editing key-value pairs vs decompression.；Different error handling: print stack trace vs print error message.；Different resource types and path handling.
- 修正建议: Use task-specific fine-tuning or incorporate domain knowledge to differentiate unrelated file I/O operations.；Leverage control flow and data dependence graphs to capture actual transformations rather than surface patterns.
