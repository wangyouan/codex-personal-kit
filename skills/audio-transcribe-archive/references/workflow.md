# 录音转录与归档：给其他 Codex 对话的操作说明

流程整理日期：2026-10-23。适用于本地 Windows 转录；每台设备需分别确认环境。

## 1. 已有方案，先复用，不要因缺少音频专用工具就停止

已有录音使用本地 **faster-whisper + large-v3-turbo + CUDA** 完成转录。直接读取 MP3，无需先转换 WAV，也不需要上传到第三方服务。

运行时分别配置，技能文件不携带以下依赖、模型或本机工作资料：

- Python：兼容的 Python 3.12，优先 Anaconda `codex`；`CODEX_AUDIO_PYTHON` 可指定其他已核验解释器。
- 依赖目录：默认取当前用户临时目录下的 `lv-audio-libs`，可用 `--libs` 指定。
- 模型目录：默认取当前用户临时目录下的 `lv-whisper-turbo`，可用 `--model` 指定。
- 任务脚本：本技能的 `scripts/transcribe.py`；通过参数传入音频、归档目录及提示词。

原设备在 2026-10-23 核验过 Python 3.12.14、faster-whisper 1.2.1、PyAV 16.1.0 和一个 CUDA 设备。模型目录有约 1.62 GB 的 model.bin，以及 config/tokenizer/vocabulary 等文件。这是历史设备记录；其他解释器、设备或清理缓存后须重新执行 `--check`，不能据此宣称已完成新的录音转录。

**不要直接假定系统默认 `python` 可用。** 原设备曾因 Python 3.13 加载 Python 3.12 音频依赖而报 `No module named av._core`；应核对解释器和扩展模块的兼容性。默认环境查不到 whisper/torch，不代表此电脑不能转录。faster-whisper 使用 CTranslate2，不要求先安装 PyTorch。

临时目录可能被清理，运行前检查。缺失时才考虑重建依赖及下载模型，不能假定临时路径永久有效。

## 2. 确认归档对象并保全原始录音

1. 根据用户明确提供的学生个人目录和日期定位，先读适用的 AGENTS.md 及已有目录规范。
2. 通常归入：`学生个人目录/02_沟通记录/面谈_YYYYMMDD/`。
3. 将录音复制到 `原始录音/`，保留源文件，不移动或覆盖。
4. 计算源文件及归档副本的 SHA256，核对相等。将源路径、归档路径、哈希、核验结果和日期写入 `录音来源与校验.json`。多个录音逐个记录。
5. 文件名时间不是设备时钟准确的证明；日期优先依据用户说明。各录音时间戳以本段起点计算。

## 3. 运行转录

用最新 pwsh 调用本技能脚本，通过 `--input`、`--output-dir`、`--prompt` 明确指定本次录音、面谈归档目录及正确姓名、已知主题术语。同时检查输出重名情况。

技能脚本包含以下必要设置：

```python
sys.path.insert(0, str(libs))
dll_handles = []
for p in libs.glob('nvidia/**/bin'):
    os.environ['PATH'] = str(p) + os.pathsep + os.environ.get('PATH', '')
    dll_handles.append(os.add_dll_directory(str(p)))

model = WhisperModel(model_path, device='cuda', compute_type='float16')
segments, info = model.transcribe(
    audio_path, language='zh', beam_size=5,
    vad_filter=True, condition_on_previous_text=False,
    initial_prompt='使用正确姓名及已知研究术语的简短提示；请使用简体中文。'
)
```

不要给提示词塞入预期结论。保留 DLL 句柄直至识别结束。`segments` 是惰性迭代器，必须遍历才会真正完成识别。

调用方式（先指定本机已核验的 Python 3.12 路径）：

```powershell
$audioPython = $env:CODEX_AUDIO_PYTHON
if (-not $audioPython) {
    $audioPython = Join-Path $env:USERPROFILE 'anaconda3/envs/codex/python.exe'
}
$audioScript = Join-Path $env:USERPROFILE '.codex/skills/audio-transcribe-archive/scripts/transcribe.py'
& $audioPython $audioScript --check
if ($LASTEXITCODE -ne 0) { throw '环境检查未通过。' }
& $audioPython $audioScript --input '<录音绝对路径.MP3>' --output-dir '<本次归档目录>' --prompt '已知术语；请使用简体中文。'
```

输出每段起止秒数及文本至 JSON，同时输出带时间戳的 UTF-8 TXT；可保留 avg_logprob、no_speech_prob 供排查，但它们不等于文字正确率。长录音持续报告进度，检查进程完成和输出完整性；已有半成品不能当作已完成。

若读取依赖目录报 PermissionError，可能是沙箱权限，不能误报“没有安装”。按工具流程申请完成本任务所需的最小执行权限；此前授权执行后成功导入。若 CUDA 不可用，可考虑 CPU/int8，但先说明速度会降低。不要绕过审批或关闭安全设置。

## 4. 校对与疑点处理

第一轮输出明确标注“自动转录，未逐句人工听校”。整理为易读 Markdown，但保留原始 JSON/TXT。

- 修正有充分上下文支持的术语、人名同音误识别，保留修改说明。
- 对不通顺、重复、数字、姓名和关键事实重点核对；必要时用不同识别参数复跑或切取前后有余量的音频片段再识别。
- 同一模型多轮结果一致也不是独立证实。自动识别交叉核对不得写成“逐句人工听校完成”。
- 无法确定写“听不清/待核实”，附时间戳；不凭常识补写原话。
- 未做可靠说话人识别，不强行给混合段落分配发言人。
- 静音或噪声可能产生重复幻觉，可在校对稿标记省略，原始识别底稿仍保留。
- 专题提取区分学生转述、老师提问、推测、现场决定与后续待核事项。摘要不能反过来替代录音证据。

## 5. 交付与归档检查

建议目录：

```text
面谈_YYYYMMDD/
  原始录音/原文件名.MP3
  录音来源与校验.json
  原文件名_transcript.json
  原文件名_转录.txt
  面谈转录_YYYYMMDD.md
  面谈转录_YYYYMMDD_文字校对版.md   # 实际进行了文字校对才创建
  校对说明或修改记录
  专题整理_YYYYMMDD.txt             # 按用户要求
```

检查音频可读取、复制哈希一致、识别正常结束、时间戳单调且不超时长、开头结尾和长空白无明显漏段。VAD 会跳过静音，最后一个语音时间戳无需等于音频总长。

将归档链接加入已有沟通索引；涉及导师接收、候选级别或新任务的状态变更须有明确依据，不能从讨论自行推导。原始转录、校对稿、事实总结、内部评价分开。最终告知用户文件位置及仍待核实的内容。

## 6. 跨设备准备

仅同步技能说明和脚本。其他电脑需要单独准备兼容的 Python 3.12、faster-whisper/PyAV/CTranslate2 依赖、本地模型，以及所需的 CUDA 库；也可以明确使用 CPU/int8。先检查已有缓存及模型文件，再按当前任务需要安装或下载。

学生姓名、个人档案路径、源录音、转录和历史任务脚本均保留在任务授权的本机归档位置，不随技能提交。校对范例使用匿名记录，并保留“非逐句人工听校定稿”的准确说明。
