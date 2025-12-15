### 已知问题 (Known Issues)

### 1、中文文本渲染与光标对齐问题(Chinese text rendering and cursor alignment)
在涉及中文(CJK)输入的某些场景下，文本的视觉渲染(字符宽度，字符位置)可能与光标位置不完全对齐，导致输入体验不佳。

该问题主要与底层文本渲染部分处理有关，将在下一个版本解决。

In some scenarios involving Chinese (CJK) input, the visual rendering of text (character width and position) may not be fully aligned with the cursor position, which can negatively impact the input experience.

This issue is mainly related to the handling of the underlying text rendering logic and will be fixed in the next version.


### 2、Windows 平台在个别特定场景下会出现输入延迟(Input latency on Windows in certain scenarios)
在 Windows 平台上，当出现大量需要渲染文本的场景下，此时键盘输入会出现可察觉但轻微的时延。MacOS 平台不会出现类似问题。

该问题主要是由于界面刷新策略导致，将在下一个版本解决。

On the Windows platform, in scenarios where a large amount of text needs to be rendered, keyboard input may experience noticeable but slight latency. This issue does not occur on macOS.

This problem is mainly caused by the current UI refresh strategy and will be addressed in the next version.


### 3、大模型对话显示为 Markdown 原始文本形式展示(LLM conversation shown as raw Markdown text)
在与大模型进行对话时，大模型原始文本尚未进行 Markdown 解析和渲染，会部分影响用户体验。

目前还未找到令人满意的方案对大模型进行增量解析和显示，将在下一个版本解决。

When interacting with the large language model, the returned raw Markdown text is not yet parsed and rendered, which may partially affect the user experience.

A satisfying solution for incremental parsing and displaying of the model output has not yet been found, and this issue is planned to be resolved in the next version.
