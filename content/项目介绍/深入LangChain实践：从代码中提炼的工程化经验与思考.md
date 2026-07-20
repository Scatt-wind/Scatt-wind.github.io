---
title: 深入 LangChain 实践：从代码中提炼的工程化经验与思考
date: 2026-07-20
excerpt: 从基础 LLM 调用一路写到完整的 RAG 问答系统
tags: [LangChain, Python, RAG]
---
## 一、引言

用了几个月 LangChain 之后，我最大的感受是：它真正有用的地方不是帮你封装了多少 API，而是给了一套可以随意拼装的零件。Prompt、Chain、Agent、Memory、Retriever 各管各的，通过 LCEL 管道接在一起就行。

我的项目用的是本地 Ollama 模型（Qwen3.5:4b、DeepSeek-R1:7b）加上阿里云 DashScope 的 qwen3.7-plus，两套模型换着用。最终做出来的东西是一个基于 FAISS 的物流知识 RAG 问答系统，前端用 Streamlit。

项目结构：

```
LangChain_stu/
├── Chains.py                     # LCEL 链组合与流式输出
├── chat_models.py                # ChatOllama 基础调用
├── embedding_models.py           # 嵌入模型使用
├── few_shot.py                   # FewShotPromptTemplate
├── zero_shot.py                  # 零样本 PromptTemplate
├── Agents/                       # Agent + 工具 + 记忆
├── Indexes/                      # 文档加载、分块、向量存储、检索
├── Memory/                       # 对话历史持久化 + LangGraph 短期记忆
├── output_parsers/               # 5 种输出解析器（含自定义）
└── rag-qa-bot/                   # 完整 RAG 问答系统（离线建库 + 在线检索 + Streamlit UI）
```

---

## 二、核心模块与实现分析

### 2.1 Prompt 工程：从零样本到少样本

零样本模板（`zero_shot.py`）没什么好说的，就是最基础的字符串格式化：

```python
template = "我的领居姓{last_name}, 他生了个儿子, 给他儿子起个名字"
prompt = PromptTemplate(template=template, input_variables=["last_name"])
prompt_text = prompt.format(last_name="王")
```

有意思的是 FewShotPromptTemplate（`few_shot.py`），它把"教模型怎么做"和"让模型做"拆开了：

```python
examples = [
    {"word": "开心", "antonum": "难过"},
    {"word": "高", "antonum": "低"}
]
example_prompt = PromptTemplate(
    template=example_template,
    input_variables=["word", "antonum"]
)
few_shot_prompt = FewShotPromptTemplate(
    examples=examples,
    example_prompt=example_prompt,
    prefix="给出每个单词的反义词",
    suffix="词语: {input}\n反义词:",
    input_variables=["input"],
    example_separator="\n\n",
)
```

`prefix/suffix` 控制指令框架，`example_separator` 控制示例间距。这个思路后来在 RAG 的 Prompt 里也用了：先塞上下文（相当于 examples），再提问题（相当于 suffix）。

### 2.2 LCEL 链组合

项目里全部用的 LCEL 管道语法，没碰过 legacy `LLMChain`。单链很简单：

```python
# Chains.py
chain = prompt | model  # PromptTemplate → OllamaLLM
```

但多链组合的时候踩了个坑：chain01 输出 `str`，chain02 的 PromptTemplate 期望收到 `{"joke": str}` 字典，直接接上就报错。解决办法是加个 lambda 做类型转换：

```python
# 方案一：显式 lambda 桥接
all_chain = chain01 | (lambda joke: {"joke": joke}) | chain02

# 方案二：字典映射（更 LCEL 风格）
all_chain = {"joke": chain01} | prompt2 | model
```

说白了，LCEL 管道每个连接点都有隐式的类型契约，上下游数据结构必须对得上。lambda 适配器就是胶水代码，干的是类型转换的脏活。

带解析器的完整管道长这样：

```python
chain = prompt_template | model | StrOutputParser()
```

Prompt → LLM → Parser，项目里最常见的链就这三段。

### 2.3 输出解析器：中文适配的坑

LangChain 内置的 `CommaSeparatedListOutputParser` 只认英文逗号。但中文模型经常输出 `，` 和 `、`，解析出来就变成一个元素的列表。所以我写了个子类：

```python
# output_parsers/CommaSeparatedListOutputParser.py
class CnFriendlyCommaListParser(CommaSeparatedListOutputParser):
    """先把中文逗号/顿号换成英文逗号，再交给父类解析。"""
    def parse(self, text: str) -> list[str]:
        if not isinstance(text, str):
            raise TypeError(f"期望 str，收到 {type(__name__)}")
        normalized = text.replace("，", ",").replace("、", ",")
        return super().parse(normalized)
```

10 行代码，不改源码，不加依赖，问题就解决了。

另一个自定义解析器处理键值对输出：

```python
# output_parsers/CustomizeOutputParser.py
class CustomOutputParser(BaseOutputParser[Dict[str, Any]]):
    def parse(self, text: str) -> Dict[str, Any]:
        result = {}
        for line in text.strip().split("\n"):
            if ':' in line:
                key, value = line.split(':', 1)
                result[key.strip()] = value.strip()
        return result

    def get_format_instructions(self) -> str:
        return """请以'键: 值'的格式返回信息，每行一个键值对。"""
```

为什么不用 PydanticOutputParser？对于简单键值对，Pydantic 会往 Prompt 里注入一大段 JSON Schema，白白多花 token。自己写一个反而更灵活，对中文冒号也兼容。

### 2.4 向量数据库：Chroma 和 FAISS 我都用了

学习模块用 Chroma，RAG 问答用 FAISS。选 Chroma 是因为 API 简单，几行代码就能跑起来：

```python
chroma = Chroma.from_documents(
    documents=chunks,
    embedding=embed_model,
    persist_directory="Indexes/data/chroma_db",
)
result = chroma.similarity_search(query, k=1)
```

选 FAISS 是因为 RAG 系统对检索速度有要求，FAISS 在单机场景下更快：

```python
# 离线建库
vector_db = FAISS.from_documents(chunks, embeddings)
vector_db.save_local("rag-qa-bot/data/vector_db")

# 在线加载
vector_db = FAISS.load_local(
    "rag-qa-bot/data/vector_db",
    embeddings=embed_model,
    allow_dangerous_deserialization=True,  # pickle 反序列化需显式授权
)
docs = vector_db.similarity_search(question, k=2)
```

注意 `allow_dangerous_deserialization=True` 这个参数。FAISS 的 `load_local` 底层是 pickle 反序列化，理论上可以执行任意代码。所以 LangChain 默认拒绝加载，必须你手动确认。我在代码里加了注释提醒自己：只加载自己生成的索引文件。

### 2.5 文本分块：试了四种 Splitter

`Indexes/CharacterTextSplitter.py` 里把四种分块器都跑了一遍：

```python
# 1. 固定字符分块
CharacterTextSplitter(chunk_size=5, chunk_overlap=1, separator=" ")

# 2. 递归分块（层次化分隔符）
RecursiveCharacterTextSplitter(
    chunk_size=20, chunk_overlap=2,
    separators=["\n\n", "\n", " ", ""],
    length_function=len,
)

# 3. 语义分块（基于嵌入相似度）
SemanticChunker(
    embeddings=embed_model,
    breakpoint_threshold_type="percentile",
    breakpoint_threshold_amount=20,
    sentence_split_regex=r'(?<=[。！？.!?])\s*',
    min_chunk_size=10
)

# 4. Markdown 结构感知分块
MarkdownHeaderTextSplitter(
    headers_to_split_on=[("#", "H1"), ("##", "H2"), ("###", "H3")]
)
```

最后 RAG 系统选了 `RecursiveCharacterTextSplitter`。语义分块效果确实好，但每次分块都要调嵌入模型，成本直接翻倍。Markdown 分块只能处理有标题结构的文档。递归分块算是通用性和效果之间比较务实的选择。

### 2.6 Agent：用的 LangGraph，不是老版 initialize_agent

```python
# Agents/Agent模块的使用.py
from langchain.agents import create_agent
from langgraph.checkpoint.memory import MemorySaver

@tool
def calculator(expression: str) -> str:
    """执行数学计算"""
    try:
        result = eval(expression)
        return f"结果: {result}"
    except Exception as e:
        return f"计算错误: {str(e)}"

@tool
def wikipedia_search(query: str) -> str:
    """搜索维基百科"""
    from langchain_community.tools import WikipediaQueryRun
    from langchain_community.utilities import WikipediaAPIWrapper
    wikipedia = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())
    return wikipedia.run(query) or "未找到相关信息"

memory = MemorySaver()
agent = create_agent(model=model, tools=tools, checkpointer=memory)
```

这里有两个我刻意做的设计：

第一，工具里面用 try/except 捕获异常然后返回错误字符串，而不是让异常往上抛。因为 Agent 框架遇到异常会直接终止执行，但如果返回一段错误文本，LLM 还有机会自己修正（比如重新构造一个合法的表达式）。

第二，Wikipedia 工具的 import 放在函数体里面。这样即使没装 `wikipedia` 包，整个模块也能正常导入，只有真正调用到这个工具时才会报错。

流式输出的 chunk 解析也写了个适配函数：

```python
def print_agent_chunk(chunk):
    # 区分 "model"（LLM 决策）和 "tools"（工具执行结果）
    for key, value in chunk.items():
        if key == "model":
            # 打印 LLM 的思考和工具选择
        elif key == "tools":
            # 打印工具返回结果
```

### 2.7 Memory：两种方案各有适用场景

方案一是 ChatMessageHistory 加 JSON 文件持久化（`Memory/ChatMessageHistory.py`）：

```python
history = ChatMessageHistory()
history.add_user_message("你好，我是孙悟空")
history.add_ai_message("你好，我是猪八戒")

# 持久化
dicts = messages_to_dict(history.messages)
with open("chat_history.json", "w") as f:
    json.dump(dicts, f)

# 恢复
with open("chat_history.json", "r") as f:
    loaded = messages_from_dict(json.load(f))
```

方案二是 LangGraph 的 InMemorySaver，靠 thread_id 做会话隔离（`Memory/Shor-term_Memory.py`）：

```python
from langgraph.checkpoint.memory import InMemorySaver

memory = InMemorySaver()
config1 = {"configurable": {"thread_id": str(time.time())}}
agent = create_agent(model=model, tools=[], checkpointer=memory)

# 同一 thread_id → 跨轮次记忆保持
# 不同 thread_id → 完全隔离的会话
```

方案一适合需要长期保存用户历史的场景，方案二适合多会话并发的服务。RAG 问答的 Streamlit 前端用 `st.session_state` 管理消息列表，本质上就是方案一的变体。

---

## 三、踩过的坑和解决办法

### 3.1 LCEL 管道类型不匹配

`chain01 | chain02` 直接报错，上游输出 `str`，下游 PromptTemplate 需要 `dict`。没有编译期检查，只能运行时才发现。解决办法就是前面说的 lambda 适配器。后来我养成了一个习惯：复杂管道里给每个节点写类型注释，省得调试的时候猜来猜去。

### 3.2 中文标点把解析器搞崩了

`CommaSeparatedListOutputParser` 遇到 `苹果，香蕉、橘子` 只切出一个元素。继承重写 `parse`，先做标点归一化就行。改动很小，不动源码，不加依赖。

### 3.3 FAISS 加载时的安全警告

`FAISS.load_local()` 默认拒绝加载，因为 pickle 反序列化可以执行任意代码。传入 `allow_dangerous_deserialization=True` 才能用。生产环境要么只加载自己生成的索引，要么干脆换 Chroma（基于 SQLite，没有 pickle 的问题）。

### 3.4 RAG 响应太慢

每次提问都要走"嵌入查询 → 向量检索 → LLM 生成"全流程，体感 3-5 秒。我用了几个办法叠加：

```python
# 1. 流式输出，让用户看到字在往外蹦
for chunk in chain.stream({"question": q, "related_content": context}):
    st.write(chunk, end="")

# 2. 关掉本地模型的思维链
model = OllamaLLM(model="qwen3.5:4b", reasoning=False)

# 3. 向量库懒加载，第一次访问时初始化，之后复用
db_loaded = False
def ensure_default_db_loaded():
    global db_loaded, vector_db
    if not db_loaded:
        vector_db = FAISS.load_local(...)
        db_loaded = True

# 4. 计时，搞清楚到底慢在哪一步
start = time.time()
# ... RAG 流程 ...
elapsed = time.time() - start
```

流式输出不减少实际等待时间，但用户感知完全不同。盯着空白等 3 秒和看着字一个个出来，后者明显好受。

### 3.5 Streamlit 上传文件的临时文件清理

```python
# rag-qa-bot/构建RAG前后端交互.py
uploaded_file = st.file_uploader("上传文档", type=["pdf", "txt", "docx"])
if uploaded_file:
    temp_path = f"temp_{uploaded_file.name}"
    try:
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        if temp_path.endswith(".pdf"):
            loader = PyPDFLoader(temp_path)
        elif temp_path.endswith(".docx"):
            loader = Docx2txtLoader(temp_path)
        # ... 建库流程 ...
    finally:
        os.remove(temp_path)  # 不管成功失败都清理
```

`finally` 块保证临时文件不会残留在磁盘上。

---

## 四、一些做法和还能改进的地方

### 4.1 我觉得做得还行的几个点

双模型策略。本地 Ollama 和云端 DashScope 通过 `.env` 切换：

```python
# 云端：确定性输出，适合结构化任务
cloud_model = ChatOpenAI(
    model="qwen3.7-plus",
    temperature=0,
    max_tokens=1000,
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    openai_api_key=os.getenv("openai_api_key")
)

# 本地：低延迟，适合交互式场景
local_model = OllamaLLM(model="qwen3.5:4b", reasoning=False)
```

`temperature=0` 给需要确定性输出的场景用（比如结构化解析），`reasoning=False` 关掉 DeepSeek-R1 的思维链换速度。两个模型各干各擅长的事。

代码组织上，每个文件开头的 docstring 列出了用到的 API，内联注释解释了 LCEL 机制、余弦相似度公式、pickle 的安全问题。写的时候想着的是"三个月后回来看还能不能看懂"。

另外全项目统一用 `mxbai-embed-large` 做嵌入，保证不同模块的向量在同一个空间里，不会出现 Chroma 里存的向量和 FAISS 里的对不上的情况。

### 4.2 还能改的地方

| 现在 | 可以改成 | 好处 |
|------|---------|------|
| FAISS 本地存储 | Milvus/Weaviate | 分布式、过滤检索、动态更新 |
| 纯向量检索 | BM25 + 向量混合 | 关键词精确匹配能力 |
| `eval()` 计算器 | `numexpr` 或 AST 解析 | 消除代码注入风险 |
| InMemorySaver | Redis/PostgreSQL checkpointer | 服务重启后记忆不丢 |
| 同步流式 | async + SSE | 多用户并发 |
| Prompt 硬编码 | LangSmith 版本管理 | A/B 测试、迭代优化 |
| 没有评估 | RAGAS 框架 | 量化检索质量和答案忠实度 |

`eval()` 那个其实挺危险的，用户输入 `__import__('os').system('rm -rf /')` 就完蛋了。当时图省事没改，后面应该换成 AST 解析。

---

## 五、RAG 系统全链路

`rag-qa-bot/` 是整个项目里最完整的部分，从建库到问答到前端都做了。

离线建库（`构建向量数据库.py`）：

```
PDF → PyMuPDFLoader → RecursiveCharacterTextSplitter → OllamaEmbeddings → FAISS.save_local()
```

在线问答（`构建RAG主逻辑.py`）：

```
用户问题 → FAISS.similarity_search(k=2) → PromptTemplate.format() → LLM → 答案
```

Prompt 是这么写的：

```python
prompt_template = """
基于已知信息，简洁专业的回答用户问题，不允许在答案中添加编造成分。
已知信息为：
{related_content}。
用户问题为：
{question}。
"""
```

"不允许添加编造成分"是防幻觉的第一道防线。`k=2` 的检索窗口比较小，我试过 k=5，发现检索回来的噪声多了，答案质量反而下降。2 个文档对物流知识这个领域够用了。

前端用 Streamlit 做的，支持上传 PDF/TXT/DOCX 文件建库，`st.session_state` 管会话消息，`st.expander` 展开看检索命中了哪些文档，还加了响应耗时统计方便自己观察性能。

---

## 六、总结

几个月写下来，几条比较深的体会：

LCEL 用习惯之后真的回不去。`prompt | model | parser` 这种写法让数据流向一目了然，legacy `LLMChain` 现在看觉得绕了一大圈。

中文场景下自定义解析器几乎是必须的。LangChain 的内置解析器都是按英文设计的，中文标点、中文键名随时可能把解析搞崩。好在继承重写 `parse` 方法成本很低。

向量数据库别纠结，先跑起来再说。我一开始在 Chroma 和 FAISS 之间犹豫了很久，后来发现学习阶段用 Chroma 快速验证想法，确定方案了再换 FAISS 优化性能，这个节奏挺对的。

Agent 工具里的错误处理，返回错误文本比抛异常好。让 LLM 看到"计算错误: invalid syntax"，它有机会自己改；直接抛异常整个 Agent 就停了。

流式输出早点加。技术上不复杂，`chain.stream()` 一行的事，但用户体验差距很大。

关于 LangChain 接下来的走向，我观察到的趋势是它在从"大而全"往"可组合"转。LCEL 替代老 Chain，LangGraph 替代 AgentExecutor，LangSmith 补可观测性。我比较期待的是：管道级别的类型检查（现在类型不匹配只能运行时炸）、原生混合检索支持、以及 `langchain-community` 那个越来越膨胀的依赖包能瘦一瘦。

---

## 参考文献

1. LangChain 官方文档 - LCEL: https://python.langchain.com/docs/concepts/lcel/
2. LangGraph 文档 - Persistence: https://langchain-ai.github.io/langgraph/concepts/persistence/
3. FAISS 文档: https://github.com/facebookresearch/faiss
4. Chroma 文档: https://docs.trychroma.com/
5. RAGAS 评估框架: https://docs.ragas.io/
6. Streamlit 文档: https://docs.streamlit.io/


