# tooltips.py
# -*- coding: utf-8 -*-

tooltips = {
    "api_key": "在这里填写你的API Key。\n\n支持的接口：\n- 智谱AI (GLM): https://open.bigmodel.cn/usercenter/apikeys\n- 火山引擎: https://console.volcengine.com/ark/region:ark+cn-beijing/apiKey\n- DeepSeek: https://platform.deepseek.com/api_keys\n- 阿里云百炼: https://bailian.console.aliyun.com\n- 硅基流动: https://cloud.siliconflow.cn/account/ak\n- Ollama (本地): 无需API Key",
    "base_url": "模型的接口地址。\n\n常用地址：\n- 智谱AI: https://open.bigmodel.cn/api/paas/v4/\n- 火山引擎: https://ark.cn-beijing.volces.com/api/v3/\n- DeepSeek: https://api.deepseek.com\n- 阿里云百炼: https://dashscope.aliyuncs.com/compatible-mode/v1\n- 硅基流动: https://api.siliconflow.cn/v1\n- Ollama (本地): http://localhost:11434/v1",
    "interface_format": "指定LLM接口兼容格式，可选：\n\n- 智谱AI (ZhipuAI): GLM-5/4.7系列\n- 火山引擎: 豆包1.5系列\n- DeepSeek: V3.2系列\n- 阿里云百炼: 通义千问系列\n- 硅基流动: 多模型代理\n- Ollama (本地部署)\n\n所有接口均兼容OpenAI标准格式。",
    "model_name": "要使用的模型名称。\n\n推荐模型：\n- 智谱AI: GLM-5, GLM-5-Turbo, GLM-4.7-Flash, GLM-4-Plus\n- 火山引擎: doubao-1.5-pro-128k, doubao-1.5-pro-32k\n- DeepSeek: deepseek-chat, deepseek-reasoner\n- 阿里云百炼: qwen-max, qwen-plus, qwen-turbo\n- 硅基流动: DeepSeek-V3, Qwen2.5系列\n\nOllama用户请填写本地下载的模型名。",
    "temperature": "生成文本的随机度。数值越大越具有发散性，越小越严谨。\n\n建议值：\n- 0.7~0.9: 创意写作\n- 0.3~0.5: 严谨问答\n- 0.1~0.2: 代码生成",
    "max_tokens": "限制单次生成的最大Token数。\n\n推荐值：\n- 智谱AI GLM-5: 200K上下文，最大输出128K\n- 火山引擎 doubao-1.5: 128K上下文\n- DeepSeek V3.2: 128K上下文\n- 阿里云百炼: 根据模型4K~128K\n\n注意：此参数为单次生成上限，实际可能更短。",
    "embedding_api_key": "调用Embedding模型时所需的API Key。\n\n支持的接口：\n- 智谱AI: 使用与LLM相同的Key\n- 火山引擎: 使用与LLM相同的Key\n- 硅基流动: 使用硅基流动API Key\n- Ollama (本地): 无需API Key",
    "embedding_interface_format": "Embedding模型接口风格：\n\n- 智谱AI (ZhipuAI)\n- 火山引擎\n- 硅基流动 (SiliconFlow)\n- Ollama (本地部署)\n\n所有接口均兼容OpenAI标准格式。",
    "embedding_url": "Embedding模型接口地址。\n\n常用地址：\n- 智谱AI: https://open.bigmodel.cn/api/paas/v4/\n- 火山引擎: https://ark.cn-beijing.volces.com/api/v3/\n- 硅基流动: https://api.siliconflow.cn/v1\n- Ollama (本地): http://localhost:11434",
    "embedding_model_name": "Embedding模型名称。\n\n推荐模型：\n- 智谱AI: embedding-3, embedding-2\n- 火山引擎: Doubao-embedding\n- 硅基流动: BAAI/bge-m3, Qwen3-Embedding-8B\n- Ollama: nomic-embed-text, bge-m3",
    "embedding_retrieval_k": "向量检索时返回的Top-K结果数量。\n\n建议值：\n- 3~5: 短文本检索\n- 5~10: 小说章节检索\n- 10~20: 大量候选时",
    "topic": "小说的大致主题或主要故事背景描述。",
    "genre": "小说的题材类型，如玄幻、都市、科幻等。",
    "num_chapters": "小说期望的章节总数。",
    "word_number": "每章的目标字数。",
    "filepath": "生成文件存储的根目录路径。所有txt文件、向量库等放在该目录下。",
    "chapter_num": "当前正在处理的章节号，用于生成草稿或定稿操作。",
    "user_guidance": "为本章提供的一些额外指令或写作引导。",
    "characters_involved": "本章需要重点描写或影响剧情的角色名单。",
    "key_items": "在本章中出现的重要道具、线索或物品。",
    "scene_location": "本章主要发生的地点或场景描述。",
    "time_constraint": "本章剧情中涉及的时间压力或时限设置。"
}