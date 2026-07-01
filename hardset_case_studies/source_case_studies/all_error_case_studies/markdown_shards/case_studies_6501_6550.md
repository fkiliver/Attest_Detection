# Error Case Studies 6501-6550

- Source model: `configured-llm`
- Cases: `6501` to `6550`

### case_id=6501 FP partial_functionality

- 方法: `googleImageSearch` vs `startScript`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Performs a Google image search, parses HTML to extract image URLs, and updates the UI with the first image.
- B 摘要: Loads a script from a given URL and appends it to a dialog script object.
- 静态失败原因: Static BERT models may overemphasize the common I/O boilerplate (URL opening, BufferedReader, while loop) and ignore the divergent semantics of parsing and output, leading to false positive.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely labeled 0 because the high-level functionality differs significantly (image search vs. script loading), despite sharing a common pattern of reading from a URL. BCB broad criteria still require some degree of functional similarity, which is absent here.
- 共享行为: Both open a URL and read lines via BufferedReader；Both handle exceptions (IOException or Exception)
- 行为差异: A uses HttpURLConnection with custom User-Agent; B uses URL.openStream()；A parses HTML to extract image URLs; B concatenates lines into a script string；A updates UI components; B appends to dialog script and calls begin/endScript；A catches Exception; B catches IOException and uses System.exit(0)
- 修正建议: Add training data emphasizing task-level semantics beyond common patterns；Incorporate data flow or call graph analysis to capture differences in API usage and output handling

### case_id=6502 FN partial_functionality

- 方法: `populateResources` vs `File2String`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Populates resource templates and image properties from bundled resources, reading them via URL and saving to storage.
- B 摘要: Reads a file or classpath resource into a string, printing error and exiting on failure.
- 静态失败原因: Static BERT/GraphCodeBERT methods rely heavily on token-level overlap and surface form; the low Jaccard similarity (0.17) and different method names, parameters, and return types overshadow the structural similarity in the reading-and-buffering portion.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely annotates this as a clone because both functions share a core pattern of reading from a URL/classpath stream into a string buffer, which is considered a recognizably similar subtask, even though the surrounding logic and side effects differ.
- 共享行为: Both use BufferedReader and InputStreamReader to read from an InputStream obtained from a URL.；Both iterate over lines and build a StringBuffer from the content.
- 行为差异: Function A processes multiple templates and images, saving them via domain-specific objects; Function B reads a single file and returns its content as a string.；Function A logs errors and continues; Function B prints errors and terminates the program (System.exit).；Function A has no return value; Function B returns a String.；Function A uses custom classes like Resource, Image, Property; Function B uses only standard Java I/O.
- 修正建议: Enhance models to recognize common API usage patterns (e.g., BufferedReader + InputStreamReader + URL.openStream).；Use graph-based encoding that abstracts away variable names and focuses on control and data flow.；Incorporate program slicing to isolate functionally similar subtasks.

### case_id=6503 FP lexical_or_api_overlap

- 方法: `getLinksFromURLFast` vs `executeHttpGet`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Opens a URL, reads the HTML page, and extracts all hyperlinks and their text using regular expressions, returning two vectors.
- B 摘要: Executes an HTTP GET request using Apache HttpClient, reads the JSON response, and parses it into a JSONObject.
- 静态失败原因: The static BERT model likely overemphasized the common patterns: both methods open a URL, read lines in a while loop, and use StringBuilder. This lexical and structural overlap misled the model into classifying them as clones despite different semantic purposes.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely considers these non-clones because the core functionality (link extraction vs JSON parsing) and return types differ significantly, despite shared boilerplate of reading a response.
- 共享行为: Both perform an HTTP GET request and read the response line by line using a BufferedReader.
- 行为差异: Different HTTP client used (URLConnection vs HttpClient)；A extracts links and text from HTML; B returns a JSON object；A returns two vectors; B returns a single JSONObject；A uses regex parsing; B uses JSON parser
- 修正建议: Improve the model's ability to distinguish post-processing steps (regex vs JSON parsing) after reading the response.；Incorporate data flow analysis to track how the read content is transformed and what is returned.

### case_id=6504 FN partial_functionality

- 方法: `populateResources` vs `fileDownload`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Loads templates and images from classpath resources and saves them to a database.
- B 摘要: Downloads a file from a URL and saves it to the local filesystem.
- 静态失败原因: The functions have low lexical overlap (Jaccard=0.153), different method names, parameters, and variable names. Static models like CodeBERT may rely heavily on token overlap and miss the abstract similarity in control flow and data flow. Additionally, the classpath resource loading vs external URL download may appear different but are conceptually similar I/O operations.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels functions as clones if they perform similar high-level tasks, such as downloading content from a URL and saving it, even if the details differ. Both functions involve opening a URL, reading data, and persisting it, which BCB might consider Type-4 (similar functionality) clone.
- 共享行为: Both open a URL connection and read data using BufferedReader；Both save the read data to a persistent storage (database or file)；Both handle IO exceptions with logging
- 行为差异: Function A reads multiple templates and images from classpath resources based on locale; Function B downloads a single PDF from an arbitrary URL；Function A saves to database using Resource.save() and Image.save(); Function B saves to a file using FileOutputStream；Function A has no parameters; Function B takes URL and destination directory；Function A also processes file names and creates Property objects
- 修正建议: Improve representation of I/O operations and persistent storage patterns, e.g., by adding data-flow analysis to capture read-write cycles；Use code summarization or AST-based features to capture high-level purpose

### case_id=6505 FN benchmark_preference_bias

- 方法: `testSimpleQuery` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.2`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: A test method that sets up JCR node sources with XML content, executes an XPath query, and asserts the query returns exactly one result matching the expected content.
- B 摘要: A method that builds a site for editing by transforming XML pages using XSLT, reading control files, and writing output, with extensive error handling and debugging.
- 静态失败原因: Static BERT predicted non-clone correctly; thus it did not fail but was misaligned with BCB label. The model likely relied on lexical similarity and structure, which are very low.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB likely labeled as clone due to partial functionality overlap (both read/write XML data) or benchmark preference for broad Type-4 clones, but the tasks are fundamentally different.
- 共享行为: Both involve XML manipulation and I/O operations.
- 行为差异: A is a unit test focused on querying; B is a complex site builder with numerous file operations and string buffers.；A is short and specific; B is long and processes multiple pages.；A uses JCR API; B uses custom XML transformation and file system utilities.
- 修正建议: Re-evaluate BCB label for this pair; consider if it is a false positive.；Improve benchmark consistency by requiring stronger functional equivalence for Type-4 clones.

### case_id=6506 FP partial_functionality

- 方法: `readZoneIDs` vs `getFrameworkFactory`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a resource file containing zone IDs (integers), parses each line as integer, and returns a set of those integers.
- B 摘要: Reads a service configuration file, skips comments and empty lines, loads the class named on each non-comment line, instantiates it, and returns the first successfully created FrameworkFactory instance.
- 静态失败原因: The static BERT/GraphCodeBERT model likely overfocused on the shared I/O pattern (URL, InputStreamReader, readLine) and missed the completely different processing logic and return types, leading to a false positive.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely labels this as non-clone because the core semantics are completely different despite similar I/O boilerplate; Type-4 clones require semantic equivalence, not just shared infrastructure.
- 共享行为: Both obtain a URL to a classpath resource and open a stream to read it；Both use InputStreamReader and BufferedReader/LineNumberReader to read lines；Both iterate over lines using a while loop
- 行为差异: A parses each line as an integer; B trims lines, skips empty/comment lines, and uses Class.forName to load and instantiate a class；A catches Exception and prints stack trace, returning empty set; B throws Exception if not found and uses try-finally to close the reader；A returns a HashSet<Integer>; B returns a FrameworkFactory；A does not close the stream (potential resource leak); B explicitly closes the BufferedReader
- 修正建议: Incorporate data flow analysis to distinguish how line content is used；Train on more examples with similar I/O but divergent processing；Use attention mechanisms that focus on the computational core beyond boilerplate

### case_id=6507 FP lexical_or_api_overlap

- 方法: `copyOverWarFile` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Copies .war files from a directory to the application data directory, unzips and extracts them.
- B 摘要: Handles GUI action events to set preferences for various settings like file paths, look and feel, and date formats.
- 静态失败原因: The static BERT model likely overemphasized lexical similarities such as usage of JFileChooser, File, getAbsolutePath, and similar control structures (if-else, try-catch), while missing the distinct semantic goals.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels non-clones because the two methods have entirely different purposes and contexts, despite some API overlap. Functional cloning would require similar logic for similar tasks.
- 共享行为: Both use JFileChooser to select files；Both perform file operations with try-catch；Both involve conditional logic
- 行为差异: copyOverWarFile is a static utility for file copying; actionPerformed is an instance method for GUI event handling；copyOverWarFile focuses on war files; actionPerformed handles multiple unrelated commands；actionPerformed updates UI components and preferences; copyOverWarFile does not interact with UI
- 修正建议: Improve training data to include more negative pairs with API overlap but different intent；Incorporate data flow or control flow analysis to distinguish overall purpose；Use models that capture long-range semantics and ignore boilerplate code

### case_id=6508 FP boilerplate_overlap

- 方法: `readData` vs `run`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Initializes multiple sets and maps by parsing comma-separated tokens from static strings, then reads a file line by line to populate Tibetan character mappings.
- B 摘要: Reads files for pseudolocalization, processes messages through a pipeline, and writes transformed output to new files.
- 静态失败原因: Static BERT likely over-relied on token-level similarities (StringTokenizer, HashSet, while loops) and ignored the global context and data flow differences, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB annotates non-clones when functions have completely different purposes even if they share trivial patterns like loops or API calls. The domain difference and lack of structural similarity rule out Type-3/Type-4.
- 共享行为: Both read from some input (strings or files) and populate data structures (sets, maps, lists).
- 行为差异: A focuses on Tibetan character processing with specific static token strings, while B handles generic file pseudolocalization.；A is a static method with no parameters, B is an instance method taking PseudolocalizerArguments.；A populates global static sets and maps, B writes output to files via streams.
- 修正建议: Include more negative examples with similar boilerplate but different semantics.；Use graph-based or dataflow models to capture long-range dependencies.；Fine-tune with domain-specific data.

### case_id=6509 FP lexical_or_api_overlap

- 方法: `getLinksFromURLFast` vs `getPagina`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Extracts hyperlinks and their visible text from a web page, returning them as two vectors.
- B 摘要: Retrieves the entire content of a web page as a single string.
- 静态失败原因: The static BERT/GraphCodeBERT model likely overemphasized the lexical and API overlap (URL, BufferedReader, InputStreamReader) and missed the core functional difference in output and processing logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the overall functionality differs significantly: one extracts links, the other retrieves raw content. The shared IO boilerplate is insufficient for functional similarity.
- 共享行为: Open a URL connection；Read the page content line by line using BufferedReader
- 行为差异: Function A returns a vector of links and texts; Function B returns the whole page content as a string.；Function A uses regex to parse links and resolve relative URLs; Function B concatenates lines without parsing.；Function A includes debugging prints and time checks; Function B has exception handling returning error messages.；Function B sets an authenticator; Function A does not.
- 修正建议: Train with more diverse negative examples that share API patterns but differ in task.；Incorporate dataflow analysis to track how outputs are constructed.；Use contrastive learning to better separate functionally distinct code.

### case_id=6510 FN boilerplate_overlap

- 方法: `main` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Main method for RenRen API feed publishing, constructs a POST request with multiple encoded parameters and authentication, then prints the response.
- B 摘要: Main method for simple HTTP GET request to a static URL, reads and prints the response.
- 静态失败原因: Static BERT likely failed due to low token overlap (Jaccard 0.23) and heavy presence of domain-specific tokens (RenRen API, parameter names) that overshadow the shared structural pattern, causing the embedding to focus on differences rather than the common loop/IO structure.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely labeled these as clones because of the highly similar boilerplate pattern of opening a connection, reading input line by line, and printing output, which is the core functionality of both methods despite different HTTP details.
- 共享行为: Both create a URL object；Both open an HTTP connection or stream；Both read response line by line；Both print each line to console
- 行为差异: Method A uses POST method; Method B uses GET；Method A includes extensive parameter encoding and signing; Method B has no parameters；Method A uses HttpURLConnection with explicit settings; Method B uses URL.openStream()；Method A has additional print statements for request status
- 修正建议: Incorporate structure-aware features like AST or control-flow graphs to capture the shared reading loop pattern；Weight common idioms (e.g., while readLine pattern) more heavily in representation；Use dataflow analysis to highlight that both methods perform an HTTP request and consume its response

### case_id=6511 FP lexical_or_api_overlap

- 方法: `getUser` vs `doVersionCheck`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Loads a user from database or config file, returning the user object.
- B 摘要: Checks for software version by reading a URL and parsing build numbers, then calls another method.
- 静态失败原因: The model likely relied on surface-level similarity (URL reading, line parsing, exception handling) and token overlap, ignoring the semantic purpose of the methods.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB annotators focus on functional similarity; these functions have completely different purposes despite similar control flow, so they are not clones.
- 共享行为: Both read from a URL using BufferedReader and parse lines
- 行为差异: A returns a User object; B performs version check and does not return a value；A persists user to database; B calls another method；Different exception handling: A catches Exception and prints stack trace; B catches IOException and shows error dialog
- 修正建议: Incorporate deeper semantic analysis, such as considering method names and return types, or using dataflow analysis to distinguish functionality.

### case_id=6512 FN partial_functionality

- 方法: `main` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Extracts all entries from a zip file obtained from a URL and writes them to disk.
- B 摘要: Copies a single file from source to destination using file channels.
- 静态失败原因: Low token similarity (0.127) and different method structures caused the static model to not detect any semantic or lexical overlap.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled this as a clone due to both functions involving file output operations, possibly considering them as 'data transfer' functions under a broad Type-4 interpretation.
- 共享行为: Both perform file I/O operations (read from a source and write to a destination).
- 行为差异: A handles zip archive and network URL; B handles local files.；A extracts multiple files; B copies one file.；A uses ZipInputStream; B uses FileChannel.transferFrom.
- 修正建议: Improve model's ability to distinguish between file copy and zip extraction.；Incorporate more structural or semantic features to differentiate specific I/O patterns.

### case_id=6513 FP lexical_or_api_overlap

- 方法: `getLinksFromURLFast` vs `doVersionCheck`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Parses a URL to extract all hyperlinks and their text, returning them as vectors.
- B 摘要: Checks for new version information by reading a version-check URL and calling another method with the retrieved build numbers.
- 静态失败原因: The static model overemphasized lexical and API-level overlaps (URL, BufferedReader, readLine while loop) without capturing high-level functional intent.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this non-clone because the functions serve completely different purposes: one performs web scraping, the other performs version checking, despite low-level API overlaps.
- 共享行为: Both open a URL connection and read lines using BufferedReader
- 行为差异: Function A extracts and returns hyperlinks; Function B extracts version strings and calls another method；Function A uses regex to parse HTML; Function B uses simple line prefix matching；Function A returns a Vector array; Function B is void and shows/hides wait cursor
- 修正建议: Incorporate data flow analysis to distinguish output purposes；Use semantic similarity based on task descriptions or method names；Train on more diverse examples to reduce reliance on surface-level patterns

### case_id=6514 FP boilerplate_overlap

- 方法: `main` vs `resolvePlugins`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: A main method that parses a Prolog file and generates adapter classes into a JAR.
- B 摘要: A method that downloads/caches a plugins.xml file and resolves plugins.
- 静态失败原因: Likely due to overlapping API usage (File, URL, streams, try-catch) and similar exception handling patterns, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically requires high behavioral similarity; these two are completely unrelated in functionality, so BCB correctly labeled non-clone.
- 共享行为: Both perform file I/O and exception handling；Both use try-catch blocks and print stack traces
- 行为差异: Different tasks: code generation vs plugin resolution；Different file formats and processing logic；Different control flow and output
- 修正建议: Improve the model to better distinguish between different high-level tasks；Incorporate more structural or semantic features beyond surface-level API usage

### case_id=6515 FP lexical_or_api_overlap

- 方法: `sha1` vs `perform`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Computes SHA-1 hash of a string and returns hex representation.
- B 摘要: Handles HTTP request to classify a concept by sending XML to a server and forwarding to appropriate view.
- 静态失败原因: Static BERT might have been misled by common method signature elements (throws declarations, return types like String vs ActionForward) or by overlapping exception types, but lacks understanding of semantic difference.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels as non-clone because functions have no common functionality; one is pure utility, the other is a Struts action with extensive business logic.
- 共享行为: Both handle exceptions；Both use String manipulation
- 行为差异: A is a simple hashing function; B is a complex web action with session management, HTTP communication, XML parsing, and forwarding.
- 修正建议: Improve model to focus on action flow rather than peripheral API uses；Incorporate data flow analysis；Use better representation of method body structure

### case_id=6516 FN partial_functionality

- 方法: `getResourceAsStream` vs `upload`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a resource from a URL, caches it locally, and returns an InputStream to the cached file.
- B 摘要: Uploads an image file by copying it from a source to a fixed destination.
- 静态失败原因: Low token overlap (0.12) and differing method names caused the model to miss the abstract similarity of data transfer from source to destination.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as 'file copy' operations at a high abstraction level, thus labeling them as Type-4 clones despite different implementations and contexts.
- 共享行为: Both perform file I/O with reading from a source and writing to a destination file.；Both use exception handling for I/O errors.
- 行为差异: Source type differs: network URL vs. local file.；Function A includes caching logic and HTTP handling; Function B is a simple copy.；Return types differ: InputStream vs. String.
- 修正建议: Incorporate data flow analysis to capture source-to-destination patterns.；Use program dependence graphs to identify similar I/O structures.

### case_id=6517 FN partial_functionality

- 方法: `createSettingsIfNecessary` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Creates default settings file if missing by copying from a bundled resource.
- B 摘要: Downloads a KMZ zip file from a URL and extracts its entries to files.
- 静态失败原因: Low token Jaccard (0.14) and different method names/tasks led the model to focus on surface differences, missing the underlying stream-copying pattern that BCB considers similar.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely labeled this as a clone because both functions implement the high-level pattern of 'copying bytes from an input source to one or more file outputs,' which is considered a Type-4 functional similarity.
- 共享行为: Both read from an input stream and write to output streams.；Both handle IO exceptions via throws or try-catch.
- 行为差异: A only writes to one file conditionally (if settings file does not exist); B always writes multiple files.；A's source is a resource inside the bundle; B's source is a remote URL.；A involves no zip decompression; B decompresses a zip archive.
- 修正建议: Use AST or data-flow representations to capture the common stream-copying structure.；Incorporate task-level semantic analysis to recognize broader functional categories.

### case_id=6518 FP boilerplate_overlap

- 方法: `executePost` vs `loadURL`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Executes an HTTP POST request with parameters and returns the response as a string.
- B 摘要: Loads a URL (with optional authentication) and writes the response to a temporary file, updating a status label.
- 静态失败原因: Static BERT/GraphCodeBERT likely overemphasized the shared boilerplate of opening an HTTP connection and reading lines with BufferedReader, while ignoring the different method signatures, HTTP methods, and control flows.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels non-clone because the functions have different HTTP methods (POST vs GET), different output handling (return vs file write), and different error handling, making them functionally distinct.
- 共享行为: Both open an HTTP connection and read the response line by line.
- 行为差异: A uses POST method, B uses GET (default).；A sends URL parameters, B optionally sends basic auth header.；A returns the response string, B writes to a file and updates a UI label.；A handles exceptions internally, B throws IOException.
- 修正建议: Incorporate dataflow analysis to distinguish sending data vs only reading.；Train with more examples that differentiate POST and GET methods.；Use method-level context like name and signature to capture intent.

### case_id=6519 FP lexical_or_api_overlap

- 方法: `trainClassifier` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Executes an external command to train a classifier using a training data file and model file.
- B 摘要: Handles various action commands in a GUI settings dialog to configure paths and preferences.
- 静态失败原因: The model may have over-relied on superficial lexical overlaps like 'File', 'String', and general control flow patterns, ignoring the distinct API calls and overall purpose.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled as non-clone due to completely different domains (ML training vs. GUI settings) and no meaningful semantic overlap despite low token similarity.
- 共享行为: Both involve file path manipulation
- 行为差异: Function A executes an external process; Function B updates UI components and stores preferences.；Function A is short and focused on one task; Function B is lengthy with many conditional branches.；Function A is part of a machine learning pipeline; Function B is a GUI event handler.
- 修正建议: Incorporate structure-aware features like API call sequences and data dependencies.；Use method names and class context to disambiguate functionality.；Train on more diverse examples to avoid capturing irrelevant boilerplate.

### case_id=6520 FN partial_functionality

- 方法: `main` vs `getFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a hardcoded HTTP URL, then extracts all zip entries to files in the current directory, printing progress.
- B 摘要: Retrieves a file from either the local user directory or a classpath resource; if the resource needs to be copied locally, it does so using stream copying.
- 静态失败原因: Static BERT models rely on lexical overlap and structural similarity, but here the token Jaccard is low (0.19) and method signatures differ. The model may miss the higher-level IO pattern due to surface differences like URL handling vs. classpath lookup and the extra zip loop, leading to a false negative.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely labels this as a clone because both functions share the core IO pattern of opening a stream from a remote or packaged resource and writing its contents to a file. Despite different contexts and extra zip extraction in A, the central data-transfer behavior is considered similar under BCB's broad Type-3/Type-4 criteria.
- 共享行为: Both read data from a resource (URL or classpath) via InputStream and write to a file using buffered streams.
- 行为差异: A handles only a fixed HTTP URL and expects a zip file, extracting multiple entries; B generates filename dynamically and handles local file existence or classpath resource.；A uses ZipInputStream to extract multiple files, while B copies a single stream to a single file.；A is a main method with side effects (printing), B is a protected method returning a File object.
- 修正建议: Train models to recognize common IO patterns (read-stream-write) across different abstractions.；Incorporate dataflow analysis to track stream opening and writing operations regardless of surface details.；Use contrastive learning with positive pairs that have low lexical similarity but high behavioral overlap.

### case_id=6521 FP boilerplate_overlap

- 方法: `readData` vs `createTar`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Parses configuration strings and a file to populate HashSets and a HashMap for Tibetan/linguistic character processing.
- B 摘要: Creates a tar archive from a directory by iterating files and writing them with TarOutputStream.
- 静态失败原因: The model likely overfitted on common I/O boilerplate (e.g., FileInputStream, buffer reading, stream closing) and error handling patterns, mistaking them for semantic similarity.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labeled non-clone because functions have entirely different purposes and low token overlap (Jaccard=0.085), and partial functionality similarity is absent.
- 共享行为: Both involve file I/O operations；Both use try-finally for resource cleanup；Both handle exceptions
- 行为差异: readData reads and parses textual data into in-memory structures; createTar compresses files into an archive；readData modifies static fields; createTar is stateless；Different input/output types: strings and a file vs. directory and tar file
- 修正建议: Increase training data with diverse I/O patterns；Incorporate structural features like control flow graphs or data dependencies；Add negative examples with similar boilerplate but different semantics

### case_id=6522 FP lexical_or_api_overlap

- 方法: `importSequences` vs `wordFrequency`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Imports biological sequences from a URL by reading lines and parsing tokens until a '>' delimiter, storing names and sequences.
- B 摘要: Retrieves word frequency from a web service by replacing a placeholder in a query URL, reading the response, and extracting frequency using a regex pattern.
- 静态失败原因: Static BERT overemphasized lexical and API overlap (URL, BufferedReader, InputStreamReader, exception handling) while ignoring the distinct semantic goals and data processing logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels non-clones when functions perform different domain-specific tasks despite similar API usage. The structural similarity is insufficient for Type-3/4 clones.
- 共享行为: Both open a URL and read text lines via BufferedReader；Both handle MalformedURLException and IOException similarly；Both use try-catch blocks with similar structure
- 行为差异: Different purpose: import sequences vs. word frequency；Different parsing logic: tokenizer vs. regex pattern matching；Different output types: void vs. int；Different input parameters: none vs. String word
- 修正建议: Incorporate dataflow analysis to distinguish variable roles；Use contrastive learning with pairs that share APIs but differ in functionality；Add attention to method-level semantics beyond token overlap

### case_id=6523 FP lexical_or_api_overlap

- 方法: `getRequestContent` vs `downloadModel`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Opens an HTTP URL and returns the first line of the response.
- B 摘要: Downloads an RDF model from a URL with HTTP headers and returns the model.
- 静态失败原因: Static BERT likely overfit to lexical keywords like URL, HttpURLConnection, InputStream, and openConnection, ignoring the overall semantic difference.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels non-clone because the functions have different purposes and outputs, even though they share some API usage.
- 共享行为: Both open a URL connection；Both read from an InputStream；Both use HttpURLConnection
- 行为差异: Different return types: String vs Model；Different number of lines read；Error handling present only in B；HTTP headers set only in B
- 修正建议: Incorporate data flow analysis to detect differences in return types and control flow；Use more structured representations capturing program output

### case_id=6524 FN partial_functionality

- 方法: `httpRequestByPOST` vs `run`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Performs an HTTP POST request with parameters, reads response, returns response string or null on error.
- B 摘要: Performs an HTTP GET request with basic authentication, reads response, stores result in instance variable.
- 静态失败原因: Static BERT models often rely on token overlap and API call similarity; low Jaccard (0.23) and different APIs (HttpClient vs HttpURLConnection) lead to low similarity, missing the high-level semantic commonality.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considers both as clones because they share the essential functionality of making an HTTP request and processing the response, viewing structural differences (library, method, parameter handling) as superficial.
- 共享行为: Both make an HTTP request；Both read response line by line using BufferedReader；Both build response string from lines
- 行为差异: HTTP method: POST vs GET；Library: Apache HttpClient vs HttpURLConnection；Error handling: sets error fields and returns null vs catches Throwable and sets exception field；Return mechanism: returns response string vs stores in instance field
- 修正建议: Train on diverse clones with different API implementations；Incorporate abstract data flow representing HTTP request-response pattern；Use dynamic analysis or type-aware features to generalize HTTP operations

### case_id=6525 FN partial_functionality

- 方法: `copyFile` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Copies a file from source to destination using FileChannel.
- B 摘要: Launches a NexOpen project configuration, performing various file operations, property handling, and invoking a build action.
- 静态失败原因: Static BERT models rely heavily on token and structure similarity; the low token Jaccard (0.042) and vastly different code structures cause the model to miss the high-level common behavior of file copying. The model does not capture cross-context functional similarities well.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this as a clone because both methods involve copying file content and handling IOExceptions, viewing code_b as an extended version of the file copy pattern. The partial functionality overlap in file copying is considered sufficient for a broad Type-3/Type-4 clone.
- 共享行为: Both perform file I/O operations with exception handling.；Both copy file content from one location to another (code_a directly, code_b indirectly via copying pom.xml and reverse engineering files).
- 行为差异: code_a is a simple, generic file copy utility; code_b is a complex, domain-specific launch method with many additional steps.；code_b involves project validation, configuration attributes, multiple file manipulations, and Eclipse resource management.；code_b has significantly more lines and logic beyond file copying.
- 修正建议: Incorporate control flow and data flow graphs to detect similar suboperations.；Use program slicing to extract common patterns like file copy idioms.；Train on Type-4 (semantic) clone examples with low token overlap.

### case_id=6526 FP partial_functionality

- 方法: `getDatasetsList` vs `sendPost`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Retrieves a list of dataset names from a remote server using a cached GET request with '?server=list' parameter.
- B 摘要: Sends an HTTP POST request with a parameter string and returns the response body as a single concatenated string.
- 静态失败原因: Static BERT/GraphCodeBERT likely over-relied on lexical and API overlap (e.g., URL, BufferedReader, readLine, exception handling) and the similar control flow (open, loop, read, close). It missed the critical differences in HTTP method, caching presence, return type, and overall intent because it lacks deep understanding of state and data flow.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB typically labels non-clones when functions have distinct high-level purposes, even if they share low-level I/O patterns. Here, one is a cached GET to list datasets and the other is a parameterized POST to send data, which are semantically different tasks.
- 共享行为: Both open a URL connection and read line-by-line using BufferedReader.；Both handle exceptions (IO or generic exceptions).；Both have a similar try-catch-finally structure with resource cleanup.
- 行为差异: A uses GET request with caching, B uses POST request without caching.；A returns a List<String>, B returns a String.；A is synchronized and instance method, B is static.；A appends '?server=list' to URL, B uses URL as-is.
- 修正建议: Enhance training with more examples that distinguish GET vs POST and caching vs non-caching.；Incorporate type information and method signatures.；Use data flow analysis to track return types and side effects.；Add features for HTTP method detection and caching state.

### case_id=6527 FP lexical_or_api_overlap

- 方法: `read` vs `sendPost`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads camera log from a URL, parses each line into CameraLogRecord objects, sorts them, and logs progress.
- B 摘要: Sends an HTTP POST request to a URL with parameters and returns the response body as a string.
- 静态失败原因: Static BERT models may over-rely on lexical overlap of common patterns like URL, BufferedReader, while(readLine), leading to false positive when the actual logic diverges.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would likely label as non-clone because the functions have different high-level purposes (reading vs. posting) and different data handling logic, despite sharing some boilerplate network I/O code.
- 共享行为: Open a URL connection using java.net.URL；Read data line by line using BufferedReader
- 行为差异: Function A only reads (GET implicitly) while B sends POST with parameters；A parses lines into custom objects and sorts; B concatenates lines into a result string；A writes to a list; B returns the result string；A uses logging extensively; B uses a message popup on error
- 修正建议: Incorporate data flow analysis to distinguish input vs. output operations；Use type-aware features to detect different function signatures (e.g., return type, parameters)；Add control flow patterns to capture different exception handling and post-processing

### case_id=6528 FP lexical_or_api_overlap

- 方法: `actionPerformed` vs `doUpload`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Handles GUI action events to set application preferences for Graphviz, ImageMagick, and various settings using file choosers and preference storage.
- B 摘要: Handles HTTP upload requests, parsing multipart content, managing temporary directories, and responding with XML or forwarding to a view.
- 静态失败原因: The static model likely overemphasized superficial lexical overlaps (e.g., 'File', 'chooser', 'temp', 'encoding') and common control flow patterns (e.g., null checks, try-catch) while ignoring the vastly different API contexts and functional goals.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BigCloneBench typically annotates as non-clones when functions have completely different purposes and domain contexts, even if they share low-level API usage.
- 共享行为: Both involve file-related operations (selection/creation) and some form of configuration storage or response generation.
- 行为差异: Function A is event-driven GUI code; Function B is HTTP request handling in a servlet.；Function A manages application preferences; Function B manages file upload and storage.；Function A interacts with UI components (JFileChooser, text fields); Function B deals with HTTP session, request/response, and file system.；Function A uses Suku.kontroller for preferences; Function B uses adapter and PairList for parameters.
- 修正建议: Incorporate structural AST differences or data flow analysis to distinguish GUI event handlers from servlet request handlers.；Use contrastive learning with hard negatives that share API usage but have different semantics.；Enhance training data with more diverse negative examples spanning different application domains.

### case_id=6529 FN partial_functionality

- 方法: `login` vs `importRoles`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Logs into LOLA by sending email and password via HTTP POST and retrieving a session ID.
- B 摘要: Imports RoleName objects from an XML/HTML source at a URL via HTTP GET and parsing.
- 静态失败原因: The low lexical overlap (Jaccard=0.18) and distinct method names caused the model to predict non-clone, while BCB's lenient criteria accept such partial similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider them clones due to broad Type-4 semantic similarity of making a network call and processing text data, ignoring specific domain differences.
- 共享行为: Both use URL connections and BufferedReader for I/O
- 行为差异: A sends POST data, B only reads GET；A returns session ID string, B returns list of RoleName objects；Error handling differs: A prints error and returns empty string, B catches multiple exceptions silently
- 修正建议: Incorporate higher-level semantic features like API call patterns；Use contrastive learning with diverse clone types

### case_id=6530 FP lexical_or_api_overlap

- 方法: `main` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Copies a file using FileChannel and ByteBuffer.
- B 摘要: Handles multiple GUI action commands (e.g., GRAPHVIZ, IMAGEMAGICK) and updates preferences.
- 静态失败原因: The model likely made a false positive due to over-reliance on superficial syntactic patterns (e.g., common tokens like 'if', 'return', 'null') or because the long function B contains many if-statements that coincidentally match some patterns in A, but there is no semantic equivalence.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would not consider these clones because they have entirely different functionality and no structural similarity; the low token Jaccard (0.06) supports this.
- 行为差异: Function A performs a simple file copy; Function B handles complex GUI event processing with multiple command branches.；Function A is a short main method; Function B is a lengthy actionPerformed method with many state updates.；Function A uses low-level I/O; Function B uses Swing components and preference management.
- 修正建议: Improve model training with more diverse non-clone pairs that have overlapping tokens but no semantic similarity.；Incorporate control-flow and data-flow analysis to differentiate trivial file copy from complex event handling.；Use function-level embeddings that capture overall behavior rather than local token matches.

### case_id=6531 FN benchmark_preference_bias

- 方法: `getFile` vs `extractZipFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies an XML attribute, and saves to temporary directory.
- B 摘要: Extracts all entries from a zip file to the current directory, optionally updating a progress text pane.
- 静态失败原因: Static BERT correctly predicted non-clone; it did not fail. The BCB label appears erroneous for this pair.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled as clone based on high-level similarity of handling input streams and producing local files, but the specific operations differ significantly.
- 共享行为: Both involve reading from an input stream and writing to file output streams.
- 行为差异: Function A reads from a network URL and parses XML; Function B reads from a local zip file and extracts entries.；Function A modifies XML content before saving; Function B creates directories and writes raw file contents.；Function A updates file only if not exists or empty; Function B always extracts all entries.；Function A uses NIO channels; Function B uses traditional IO streams.
- 修正建议: Re-evaluate BCB annotation for this pair; consider correcting label to non-clone.

### case_id=6532 FN partial_functionality

- 方法: `getJSONData` vs `httpRequestByPOST`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Performs an HTTP GET request to a URL, reads the response, and parses it into a JSONObject.
- B 摘要: Performs an HTTP POST request with form parameters, reads the response as a string, and handles errors with status codes.
- 静态失败原因: Static models like CodeBERT may rely on token overlap and structure. Here method names, parameters, and return types differ, and the boilerplate code (reading lines, building string) is common but not sufficient with low Jaccard similarity (0.329). The model didn't abstract to the shared HTTP request pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels functions as clones if they share the same high-level intent (HTTP request-response), even if method, parameters, or return processing differ, considering them Type-3/Type-4 clones.
- 共享行为: Both use Apache DefaultHttpClient to execute HTTP requests；Both read response line by line using BufferedReader；Both return the result of the request
- 行为差异: HTTP method: GET vs POST；Return type: JSONObject vs String；Error handling: B checks status code and sets error fields, A prints stack trace；Parameters: B accepts timeout and form params, A only URL
- 修正建议: Enhance model to recognize abstract patterns like HTTP request-response regardless of method；Incorporate data flow and graph-based representations to capture common operations；Use contrastive learning with fine-grained similarity labels

### case_id=6533 FP boilerplate_overlap

- 方法: `getTicketsForQueue` vs `getFrameworkFactory`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches tickets from a queue by making an HTTP request, parsing ticket IDs from the response, and retrieving each ticket.
- B 摘要: Reads a service file from the classpath to instantiate and return an OSGi FrameworkFactory.
- 静态失败原因: The model may have been misled by overlapping boilerplate code patterns (e.g., BufferedReader, try-finally, exception handling) and token-level similarities (e.g., 'url', 'readLine') despite different semantics.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely annotates these as non-clones due to completely different functionality and lack of meaningful similarity beyond superficial code patterns.
- 共享行为: Both use BufferedReader and InputStreamReader to read text.；Both handle exceptions and use try-finally for resource management.；Both throw or return null on failure.
- 行为差异: Function A performs an HTTP GET request to a remote server; function B reads a local file from classpath.；Function A parses ticket IDs from lines starting with 'ticket/'; function B reads a service name and instantiates a class via reflection.；Function A returns a list of RTTicket objects; function B returns a FrameworkFactory instance.；The overall purpose and domain are completely different.
- 修正建议: Incorporate data-flow or control-flow analysis to capture semantic differences.；Enhance training data with more diverse non-clone pairs that share boilerplate but differ in purpose.；Use contrastive learning to focus on functional similarity rather than lexical overlap.

### case_id=6534 FP lexical_or_api_overlap

- 方法: `loadSourceCode` vs `getFullScreenUrl`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Loads a source file, applies syntax highlighting, and returns HTML.
- B 摘要: Downloads a YouTube page, parses video metadata, and returns a full video URL.
- 静态失败原因: Static BERT models rely on lexical overlap, and both functions share common API tokens like BufferedReader, InputStream, url.openStream(), and readLine(), which can mislead the model into overestimating similarity.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB considers semantic equivalence or strong functional similarity; these functions have completely different high-level purposes.
- 共享行为: Both open an input stream and use BufferedReader to read lines.；Both have try-catch blocks for exception handling.；Both read until end of stream or null line.
- 行为差异: Function A loads local source code; Function B fetches a remote YouTube page.；Function A applies syntax highlighting; Function B parses URL parameters.；Function A returns an HTML string; Function B returns a constructed video URL.
- 修正建议: Incorporate control and data flow analysis to capture actual program behavior.；Use task-specific embeddings or domain-aware pre-training.；Increase weight on high-level semantic differences rather than low-level API usage.

### case_id=6535 FP boilerplate_overlap

- 方法: `createHTML` vs `loadURL`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Creates an HTML string for different page types by reading a CSS file and appending HTML content based on a PAGE_TYPE enum.
- B 摘要: Downloads content from a URL with optional authentication and writes it to a temporary file while updating a status label.
- 静态失败原因: The static BERT model likely over-relied on lexical overlap of common Java IO patterns (BufferedReader, InputStreamReader, readLine) and missed the high-level functional differences.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB annotators would label these as non-clones because they perform completely different tasks with different inputs, outputs, and purposes.
- 共享行为: Both read from an input stream using BufferedReader and handle IOException；Both use InputStreamReader
- 行为差异: a constructs an HTML string for internal use; b writes data to a file and updates a UI label；a uses a switch statement based on request page type; b handles authentication and file writing；a reads a CSS file from classpath; b reads from a URL connection；a returns a String; b is void and writes to file
- 修正建议: Incorporate method name embeddings or high-level purpose abstractions；Use data flow analysis to distinguish between constructing a string and writing to a file；Add attention to control flow structures like switch vs if-else

### case_id=6536 FN partial_functionality

- 方法: `copyResource` vs `createOutputStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource from a URL or local file to a destination file using byte-by-byte streaming.
- B 摘要: Reads entries from a zip file, copies most except 'content.xml', then adds a new 'content.xml' entry, returning a BufferedWriter.
- 静态失败原因: Low token overlap (Jaccard 0.16) and different method names; static models may miss the conceptual similarity in stream copying due to structural differences like loops and I/O handling.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB might consider both as 'copying data from input to output' with I/O streaming, accepting partial similarity in resource copying.
- 共享行为: Both open input and output streams and copy data；Both handle I/O exceptions
- 行为差异: B operates on zip entries and filters specific entry；B uses char buffers and specifies charsets；A copies raw bytes；B returns a BufferedWriter while A returns void
- 修正建议: Use dataflow analysis to detect stream copying patterns；Incorporate inter-procedural context；Train on I/O-related clone pairs

### case_id=6537 FP lexical_or_api_overlap

- 方法: `executePost` vs `readURL`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Sends an HTTP POST request with parameters and returns the response body as a string.
- B 摘要: Opens a URL via HTTP GET and prints its content line by line to standard output.
- 静态失败原因: The static model likely over-relied on lexical overlap of common URL/stream handling boilerplate (e.g., 'BufferedReader', 'readLine', 'e.printStackTrace()') and missed the fundamental differences in HTTP method and I/O direction.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically considers clones as functions with high structural or semantic similarity. Here, despite both dealing with URL reading, the overall task differs significantly (POST with output vs GET without), so BCB labels it non-clone.
- 共享行为: Both open a URL connection and read text input line by line.；Both use try-catch-finally for exception handling and stream cleanup.；Both print stack traces on exceptions.
- 行为差异: Function A uses POST method and writes parameters; function B uses GET method and reads only.；Function A returns the response string; function B is void and prints to console.；Function A handles HTTP headers and output stream; function B does not.；Different stream closing patterns (explicit disconnect vs utility close).
- 修正建议: Incorporate data flow analysis to distinguish write vs read operations.；Add contrastive training examples that contrast similar-looking but semantically different functions.；Use method name and return type as additional features to disambiguate.

### case_id=6538 FP lexical_or_api_overlap

- 方法: `perform` vs `getMD5Hash`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.98`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Performs a Struts action that handles classification of a concept by managing session state, extracting parameters, building XML data, sending HTTP request, and parsing response.
- B 摘要: Computes the MD5 hash of an input string and returns its hexadecimal representation.
- 静态失败原因: The model likely over-relied on lexical overlaps such as common method names ('perform'), shared API classes (StringReader, IOException, BufferedReader), and similar structural patterns (try-catch, loops, StringBuffer). It failed to capture the deep semantic difference in purpose and data flow.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB annotation typically requires semantic equivalence or substantial syntactic similarity. These functions perform entirely different tasks (web action vs. hash computation), so they are non-clones.
- 共享行为: Both use StringBuffer/StringBuilder；Both have try-catch blocks；Both read input data
- 行为差异: A handles HTTP requests and session management; B is a pure data transformation；A depends on multiple external beans and a classifier service; B uses only java.security.MessageDigest；A has complex control flow with conditional error handling; B is linear with simple catch-all
- 修正建议: Incorporate dataflow analysis to track variable usage and dependencies；Include type information and external method calls to distinguish side effects；Use code summarization or documentation to capture intent；Increase training data with contrasting pairs of unrelated utility vs. business logic functions

### case_id=6539 FP lexical_or_api_overlap

- 方法: `handleHandshake` vs `run`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Handles a Minecraft handshake packet by validating username and optionally authenticating via session server.
- B 摘要: Executes an HTTP GET request with Basic Authentication and stores the response.
- 静态失败原因: Static BERT models may over-rely on lexical and API-level overlap (e.g., 'BufferedReader', 'URL', 'readLine') present in both functions, ignoring the different control flow and semantics.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would likely not consider them clones because despite shared API usage, the overall functional purpose and logic are distinct; annotation preference tolerates only partial similarity but here the difference in core behavior is substantial.
- 共享行为: Both perform HTTP network operations；Both use BufferedReader to read responses；Both handle exceptions
- 行为差异: A validates username format and session authentication; B uses Basic Auth；A sends packets or shuts down network; B stores response and sets a flag；A has multiple conditional branches; B is a single sequential flow
- 修正建议: Incorporate control-flow or data-flow analysis；Use structure-aware models like GraphCodeBERT with AST；Include semantic similarity measures beyond token overlap

### case_id=6540 FP lexical_or_api_overlap

- 方法: `readData` vs `convert`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Initializes sets and maps with tokenized string data for Tibetan transliteration.
- B 摘要: Converts ACRNEMA/DICOM medical image files to DICOM format with UID assignment.
- 静态失败原因: The static BERT model may have been misled by common structural patterns (e.g., loops, conditionals, exception handling) or overlapping tokens like 'HashSet', 'IOException', 'throw new Error' etc., but missed the semantic divergence.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled as non-clone because the functions have entirely different domains and logic; partial functionality is not present.
- 行为差异: Function A loads linguistic data structures; Function B converts medical image files.；Function A has no file I/O (except possibly the truncated part); Function B reads and writes files.；Function A uses StringTokenizer; Function B uses DICOM parsers and streams.
- 修正建议: Improve model to capture high-level intent and domain context.；Use more robust contrastive learning or data flow analysis.

### case_id=6541 FN partial_functionality

- 方法: `runInternal` vs `doVersionCheck`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.75`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Function A downloads an OPDS catalog or book from a URL using HTTP, handling pagination and progress updates.
- B 摘要: Function B checks for software version by reading a specific URL and parsing version strings.
- 静态失败原因: Static BERT models rely on token-level similarity and exact code structure; the low Jaccard (0.108) and different purposes caused the model to miss the shared network IO pattern, especially given A's length and complexity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as 'network read' operations with similar exception handling, fitting a broad Type-4 functional clone under partial functionality similarity.
- 共享行为: Both open a URL and read input stream；Both handle IO exceptions and close resources；Both perform network I/O operations
- 行为差异: A uses HTTP-specific headers and connection configuration; B does not；A supports pagination and complex content parsing; B only reads lines and extracts version strings；A updates progress and handles different content types; B is simpler
- 修正建议: Enhance model to recognize high-level semantic patterns like 'open URL, read input, handle errors' via API sequence learning；Use dataflow analysis to abstract away specific details and focus on I/O operations；Incorporate task-level embeddings (e.g., network operations) to group similar functions

### case_id=6542 FP lexical_or_api_overlap

- 方法: `getRequestContent` vs `doVersionCheck`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads the first line from a URL and returns it.
- B 摘要: Reads version information from a URL and performs a version check, with UI feedback.
- 静态失败原因: The model likely overemphasized overlapping API calls (URL, BufferedReader) and variable names, ignoring the different control flow and output behavior.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clone because the functions have distinct purposes and logic, despite both involving URL reading.
- 共享行为: Both open a URL and read lines using BufferedReader
- 行为差异: A returns the first line; B processes multiple lines to extract version strings；B shows wait cursor and handles errors with UI dialogs; A does not；B calls another method doVersionCheck; A simply returns a line
- 修正建议: Incorporate control flow and data flow features；Use graph-based representations to capture structural differences；Add training examples with similar APIs but different logic

### case_id=6543 FP lexical_or_api_overlap

- 方法: `setBundleInfoName` vs `get`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a remote properties file and updates BundleInfo names based on key-value pairs.
- B 摘要: Sends an HTTP GET request and parses lines to decode GameRecord objects, returning an array.
- 静态失败原因: The static model likely overemphasized the lexical overlap (URL, BufferedReader, IOException) and missed the semantic gap in purpose and data flow.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels as non-clone because the functions perform entirely different tasks (updating bundle info vs retrieving game records), despite similar I/O patterns.
- 共享行为: Both open a URL connection and use BufferedReader to read lines.；Both handle IOException by printing stack trace and returning a default value (false/null).
- 行为差异: Function A modifies a list of BundleInfo objects; function B creates and returns a GameRecord array.；Function A parses lines as 'key=value'; function B decodes lines using GameRecord.decode and skips comments.；Function A uses URL.openStream(); function B uses HttpURLConnection with GET method and custom headers.；Function A returns boolean; function B returns GameRecord[] or null.
- 修正建议: Incorporate structure-aware embeddings to distinguish object manipulation patterns.；Add context about method signatures and return types.；Use data-flow analysis to track how inputs and outputs are used.

### case_id=6544 FN benchmark_preference_bias

- 方法: `modifyApplicationMessage` vs `decodeFileToFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.6`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Modifies a locale-specific properties file by updating or adding a message key-value pair.
- B 摘要: Decodes a Base64-encoded file and writes the decoded data to an output file.
- 静态失败原因: Static BERT correctly predicted non-clone due to low token overlap and distinct functional purposes; the BCB label is likely a benchmark bias or annotation error.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as a clone due to both functions performing file I/O with similar error-handling boilerplate, accepting broad Type-4 similarity based on 'file processing' as a shared high-level purpose.
- 共享行为: Both perform file input and output operations using streams.；Both handle exceptions with printStackTrace.；Both close streams after use.
- 行为差异: A processes text properties files line-by-line to replace or add a key-value; B decodes binary Base64 data.；A may copy a default file if the target file does not exist; B always writes decoded output.；A modifies content based on a given message name; B transforms encoding from Base64 to raw bytes.
- 修正建议: Focus training on functional semantics rather than boilerplate patterns.；Use dataflow analysis to capture the transformation logic of each function.；Incorporate domain-specific knowledge (e.g., properties file vs. Base64 decoding) to reject superficial overlaps.

### case_id=6545 FP lexical_or_api_overlap

- 方法: `downloadURLtoString` vs `getRequestContent`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads entire content from a URL line by line and returns it as one string.
- B 摘要: Connects to a URL via HTTP, reads only the first line from the response, and returns that line.
- 静态失败原因: Static BERT models may have been misled by high lexical overlap: both use BufferedReader, InputStreamReader, readLine(), close(), and return a String. The structural similarity of opening a URL, reading, and closing might dominate over the semantic difference in loop vs single read. Also, method names both suggest 'download' and 'get content', which could confuse the model.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels as non-clone when the output behavior is entirely different (return all lines vs just first line) even if some low-level I/O patterns overlap. The functional purpose is not aligned.
- 共享行为: Both open a URL and read from it using BufferedReader；Both use InputStreamReader to read text；Both close the reader after reading；Both handle I/O exceptions
- 行为差异: Function A returns the entire content; Function B returns only the first line；Function A uses a generic URL stream; Function B uses HttpURLConnection with explicit connect/disconnect；Function A takes a URL object; Function B takes a String；Function A reads all lines in a loop; Function B reads exactly one line
- 修正建议: Incorporate data-flow analysis to track whether readLine is called once or in a loop, to capture the difference in output length.；Use structural comparison that distinguishes between sequential blocks and loops.；Include method signatures (parameter types) as features to differentiate URL vs String input.

### case_id=6546 FN partial_functionality

- 方法: `fileDownload` vs `invoke`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a file from a URL to a local directory, saving it as download.pdf.
- B 摘要: Invokes a remote procedure via HTTP POST, reads JSON response, and returns deserialized object with retry logic.
- 静态失败原因: Low token Jaccard (0.128) and different method names/signatures caused the model to miss the structural similarity in I/O handling. Static models lack understanding of abstract behavior.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider them clones due to shared HTTP I/O pattern (BufferedReader, InputStream, try-catch) even though high-level goals differ. This is typical of broad Type-3/Type-4 clones in BigCloneBench.
- 共享行为: Both open HTTP connections and read response using BufferedReader.；Both iterate over input (readLine or read) and handle I/O exceptions.
- 行为差异: A writes binary data to a local file; B parses JSON and returns an object.；B includes retry mechanism and status code checking; A does not.；A uses URLConnection; B uses Apache HttpClient.；A writes raw bytes; B uses character-based reading and JSON deserialization.
- 修正建议: Use dataflow analysis to capture common I/O patterns.；Incorporate API usage sequence similarity.；Train with contrastive learning on behavioral rather than lexical similarity.

### case_id=6547 FN partial_functionality

- 方法: `getHTML` vs `sendRequestObjectResponse`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches HTML content from a URL via HTTP GET and optionally writes it to a file.
- B 摘要: Connects to a servlet, sends a compressed XML request, saves the response to a file based on content type, and displays it in a browser.
- 静态失败原因: The static model likely failed due to low token Jaccard similarity (0.1189) and the significant structural and semantic differences between the functions, despite some shared low-level operations.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled this as a clone because both functions involve establishing an HTTP connection, reading a response, and writing to a file, which might be considered similar in a broad 'network I/O with file output' category.
- 共享行为: Both perform HTTP communication by opening a URL connection.；Both read data from an input stream obtained from the connection.；Both write data to a file using FileOutputStream or BufferedWriter.
- 行为差异: Function A uses HTTP GET; Function B uses HTTP POST with GZIP compression.；Function A optionally writes to a file only if a directory path is given; Function B always writes to a file and determines the file extension based on content type.；Function B includes UI interaction for configuring server URL and port, and displays the result in a browser.；Function B logs the request to a file and shows error dialogs; Function A only prints stack traces.
- 修正建议: Incorporate more fine-grained behavioral analysis beyond token overlap.；Use data-flow or control-flow graphs to capture higher-level semantic intent.；Consider domain-specific heuristics for HTTP-related tasks.

### case_id=6548 FN benchmark_preference_bias

- 方法: `doGet` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Handles an HTTP GET request by retrieving a page, checking permissions, logging, rendering, and optionally caching the output to a file.
- B 摘要: Copies a file from source to destination using NIO FileChannel.
- 静态失败原因: Static BERT models rely heavily on token overlap and structural similarity. The token Jaccard between these functions is extremely low (0.04), so the model correctly identified them as non-clones. However, BCB's label suggests a different similarity criterion that the model did not capture.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled these as clones based on a very broad interpretation of Type-4 similarity, possibly considering that both functions involve file writing operations and exception handling. Alternatively, this could be an annotation error.
- 共享行为: Both involve file I/O operations (writing to a file in A, copying a file in B).；Both handle IOException.
- 行为差异: Function A is a complex web request handler with many steps (parameter extraction, page lookup, user authentication, logging, rendering, caching), while function B is a simple file copy utility.；Function A writes string content to a file using FileWriter; function B copies binary data using FileChannel.；Function A's file writing is conditional and only occurs for non-editable pages; function B always copies the entire file.；Function A involves database lookups and property retrieval; function B does not.
- 修正建议: Improve training data quality to remove annotation errors.；Incorporate more diverse negative examples to teach models that low token overlap indicates non-clones.；Use functional similarity metrics beyond token overlap.

### case_id=6549 FN benchmark_preference_bias

- 方法: `MotixFileItem` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Constructor for MotixFileItem that copies an InputStream to a ByteArrayOutputStream and optionally reads the image data.
- B 摘要: Launch method for a NexOpen project that validates configuration, processes Maven pom files, and sets up Hibernate reverse engineering files.
- 静态失败原因: Static BERT methods rely on token overlap and structural similarity; the low Jaccard similarity and different contextual embeddings likely led to a non-clone prediction, which is actually correct.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled these as Type-4 clones due to both involving stream handling and file I/O, but given the vast differences in purpose and complexity, this label seems incorrect.
- 共享行为: Both use ByteArrayOutputStream and IOUtils.copy for stream copying.
- 行为差异: Code A is a constructor handling a single file item; Code B is a complex launch procedure with multiple steps.；Code A deals with image detection; Code B deals with XML parsing, property setting, and project configuration.；Code A has simple error handling; Code B has nested try-catch-finally and exception handling.
- 修正建议: Review BCB annotation for this pair; it may be a mislabel.；Improve benchmark diversity to avoid over-generalizing API usage as clones.

### case_id=6550 FP lexical_or_api_overlap

- 方法: `getTicketsForQueue` vs `downloadModel`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Queries a ticket tracking system for open tickets in a queue and returns their details.
- B 摘要: Downloads a model from a given URL and returns it as a Model object.
- 静态失败原因: The static model likely focused on surface-level similarities such as HTTP connection setup, try-catch blocks, and stream handling, missing the semantic differences in the purpose and structure of the two functions.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels as non-clone because the overall functionality is completely different despite sharing some generic programming patterns like HTTP requests and error handling.
- 共享行为: Both handle HTTP connections and parse responses；Both use try-catch for error handling；Both close I/O streams
- 行为差异: Function A makes multiple API calls (search then fetch each ticket), while B makes one call；Function A deals with ticket parsing and iterates over IDs, B reads model directly from stream；Function A returns a list of custom objects, B returns a Model object；Error handling: A logs and returns null, B throws RuntimeException
- 修正建议: Improve model's ability to distinguish intent by incorporating more semantic features beyond API calls；Add negative examples of non-clone pairs with high lexical overlap；Use control flow or data flow analysis to detect different processing logic
