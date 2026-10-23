---
name: audio-transcribe-archive
description: Transcribe local meeting or interview recordings and archive them in the appropriate student or project folder. Use for 录音转录、面谈转录、录音归档、转录校对 and extracting topics from recordings. Reuses the verified Windows faster-whisper environment and preserves timestamped source evidence.
---

# 录音转录与归档

使用本机 faster-whisper / large-v3-turbo，不需要上传录音。尊重用户指定的个人或项目目录；未指定时先结合现有档案定位。只需转录时不要额外作人员评价或修改候选状态。

## 环境与运行

使用最新 pwsh，并明确指定兼容的 Python 3.12 解释器，优先使用 Anaconda `codex` 环境；不要假定系统默认 `python` 的版本及依赖匹配。也可以通过 `CODEX_AUDIO_PYTHON` 指向本机已核验的解释器，或复用已有的 Codex Python 3.12 运行时。每台电脑分别运行依赖检查。

先运行本技能 `scripts/transcribe.py --check`，验证依赖、模型文件和 CUDA。脚本默认复用：

- 依赖：当前用户临时目录下的 `lv-audio-libs`
- 模型：当前用户临时目录下的 `lv-whisper-turbo`

支持 `--libs`、`--model` 覆盖路径。临时目录可能被清理；缺失时明确报告，不要因默认环境没有 whisper/torch 就断言无法转录。权限错误与缺包分开处理，遵循工具权限流程。确需重建时，在 Python 3.12 环境安装 faster-whisper 及其兼容依赖，下载 CTranslate2 格式 large-v3-turbo；先检查已有缓存，不静默下载大模型。不得使用未完整下载的模型。

```powershell
$audioPython = $env:CODEX_AUDIO_PYTHON
if (-not $audioPython) {
    $audioPython = Join-Path $env:USERPROFILE 'anaconda3/envs/codex/python.exe'
}
if (-not (Test-Path -LiteralPath $audioPython)) {
    throw '请通过 CODEX_AUDIO_PYTHON 指定已核验的 Python 3.12 解释器。'
}
$audioScript = Join-Path $env:USERPROFILE '.codex/skills/audio-transcribe-archive/scripts/transcribe.py'
& $audioPython $audioScript --check
if ($LASTEXITCODE -ne 0) { throw '音频环境检查未通过，请先处理报告的问题。' }
& $audioPython $audioScript --input '<录音绝对路径.MP3>' --output-dir '<个人目录>/02_沟通记录/面谈_YYYYMMDD' --prompt '双方讨论公司金融。请使用简体中文。'
```

每个录音运行一次。默认 CUDA/float16；无可用 GPU 时可明确改用 `--device cpu`（int8，较慢）。提示词只放已知姓名和术语，不暗示预期结论。脚本复制原音频、校验哈希，生成每个录音独立的来源记录、带时间戳 TXT 和 JSON，最后生成完成标记。已完成任务不会被重跑覆盖；半成品存在时停止，另建输出目录或查明原因后处理，不能把半成品当完成。

## 校对与归档

通常归入 `个人目录/02_沟通记录/面谈_YYYYMMDD/`，但遵循现有规范和用户指定位置。保留源文件，日期以用户说明或已核实记录为准，文件名不能证明设备时钟准确。

- 保留原始 JSON/TXT，另写易读 Markdown 或文字校对版。未逐句听校须注明“自动转录/文字校对，非逐句人工听校定稿”。
- 关键数字、姓名、事实和不通顺段落按时间戳核对；可另目录复跑或截取带上下文的片段交叉识别。同一模型多次一致不等于独立证实。
- 不确定内容标“听不清/待核实”，不凭常识补写。未可靠区分说话人，不给混合段落强行标注身份。
- 录音中的提议、推测、学生转述不等于已确认事实或决定。专题提取附时间范围，区分原话转述和整理者判断。
- 检查识别正常结束、时间戳合理以及开头结尾和长空白；VAD 跳过静音，最后语音时间戳可以早于音频终点。
- 按任务需要更新沟通索引；人员状态变化须有明确依据。最终给用户归档链接及待核实项。

需要更完整的校对步骤及历史案例时读 [归档参考](references/workflow.md)。
