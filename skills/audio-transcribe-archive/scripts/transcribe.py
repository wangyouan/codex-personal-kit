"""Local transcription, immutable source copy and per-recording provenance."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
from datetime import datetime, timezone


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def save(path, data):
    temp = path.with_suffix(path.suffix + '.tmp')
    temp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    temp.replace(path)


def stamp(seconds):
    t = int(seconds)
    return f'{t // 3600:02}:{t // 60 % 60:02}:{t % 60:02}'


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--check', action='store_true')
    p.add_argument('--libs', type=Path, default=Path(tempfile.gettempdir()) / 'lv-audio-libs')
    p.add_argument('--model', type=Path, default=Path(tempfile.gettempdir()) / 'lv-whisper-turbo')
    p.add_argument('--input', type=Path)
    p.add_argument('--output-dir', type=Path)
    p.add_argument('--prompt', default='请使用简体中文。')
    p.add_argument('--device', choices=['cuda', 'cpu'], default='cuda')
    a = p.parse_args()
    if not a.libs.is_dir():
        p.error(f'音频依赖目录不存在：{a.libs}')
    for name in ['model.bin', 'config.json', 'tokenizer.json', 'vocabulary.json']:
        if not (a.model / name).is_file():
            p.error(f'模型文件缺失：{a.model / name}')
    sys.path.insert(0, str(a.libs))
    handles = []
    for folder in a.libs.glob('nvidia/**/bin'):
        os.environ['PATH'] = str(folder) + os.pathsep + os.environ.get('PATH', '')
        if hasattr(os, 'add_dll_directory'):
            handles.append(os.add_dll_directory(str(folder)))
    import av
    import ctranslate2
    import faster_whisper
    gpu_count = ctranslate2.get_cuda_device_count()
    print(json.dumps({'python': sys.version, 'faster_whisper': faster_whisper.__version__,
                      'av': av.__version__, 'cuda_devices': gpu_count,
                      'model': str(a.model)}, ensure_ascii=False), flush=True)
    if a.check:
        return
    if not a.input or not a.output_dir:
        p.error('--input and --output-dir are required')
    source = a.input.resolve(strict=True)
    if a.device == 'cuda' and not gpu_count:
        p.error('无可用 CUDA 设备；如需 CPU，明确指定 --device cpu')
    base = a.output_dir.resolve()
    base.mkdir(parents=True, exist_ok=True)
    prefix = base / source.stem
    out = Path(str(prefix) + '_transcript.json')
    txt = Path(str(prefix) + '_转录.txt')
    done = Path(str(prefix) + '_完成.json')
    provenance = Path(str(prefix) + '_来源与校验.json')
    source_hash = digest(source)
    if done.exists():
        prior = json.loads(done.read_text(encoding='utf-8'))
        if prior['source_sha256'] != source_hash or not out.exists() or not txt.exists():
            raise RuntimeError('已完成标记与输入或输出不一致，请人工核查')
        print('SKIP: 已完成，保留现有文件', flush=True)
        return
    if out.exists() or txt.exists() or provenance.exists():
        raise RuntimeError('已有未完成输出；为避免覆盖，停止。请核查或另选输出目录。')
    archive = base / '原始录音' / source.name
    archive.parent.mkdir(exist_ok=True)
    if archive.exists():
        if digest(archive) != source_hash:
            raise RuntimeError('归档目录有同名但内容不同的录音，停止')
    else:
        shutil.copy2(source, archive)
    if digest(archive) != source_hash:
        raise RuntimeError('复制后哈希不一致')
    save(provenance, {'source': str(source), 'archive': str(archive),
                     'sha256': source_hash, 'copy_verified': True,
                     'archived_at_utc': datetime.now(timezone.utc).isoformat()})
    with av.open(str(archive)) as container:
        duration = container.duration / av.time_base if container.duration else None
    model = faster_whisper.WhisperModel(str(a.model), device=a.device,
                                        compute_type='float16' if a.device == 'cuda' else 'int8')
    segments, info = model.transcribe(str(archive), language='zh', beam_size=5,
                                      vad_filter=True, condition_on_previous_text=False,
                                      initial_prompt=a.prompt)
    rows = []
    with txt.open('x', encoding='utf-8') as f:
        f.write(f'录音：{source.name}\n自动转录，未逐句人工听校；未识别说话人；时间戳相对本段录音。\n\n')
        for segment in segments:
            if segment.end < segment.start or (rows and segment.start < rows[-1]['start']):
                raise RuntimeError('时间戳异常，请核查输出')
            rows.append({k: getattr(segment, k) for k in
                         ['start', 'end', 'text', 'avg_logprob', 'no_speech_prob']})
            f.write(f'[{stamp(segment.start)}–{stamp(segment.end)}] {segment.text.strip()}\n')
            f.flush()
            if len(rows) % 40 == 0:
                print('PROGRESS', stamp(segment.end), flush=True)
    save(out, {'source': str(archive), 'duration': duration, 'model': str(a.model),
               'language': info.language, 'prompt': a.prompt, 'segments': rows})
    save(done, {'source_sha256': source_hash, 'segments': len(rows),
                'finished_at_utc': datetime.now(timezone.utc).isoformat(),
                'review_required': True})
    print('DONE', len(rows), 'segments; 仍需文字核查', flush=True)


if __name__ == '__main__':
    main()
