"""Check one local NPY/NPZ/image/CSV/NTU skeleton sample without changing it."""
import argparse
import csv
import math
from pathlib import Path


def check_skeleton(path):
    def line(handle):
        value = handle.readline()
        if not value:
            raise ValueError('Unexpected end of skeleton file')
        return value.strip()
    with path.open(encoding='utf-8-sig') as handle:
        frames = int(line(handle))
        if frames < 1:
            raise ValueError('No skeleton frames')
        body_frames, joint_total, nonempty_frames = 0, 0, 0
        for _ in range(frames):
            bodies = int(line(handle))
            if bodies < 0:
                raise ValueError('Negative body count')
            nonempty_frames += bodies > 0
            for _ in range(bodies):
                line(handle)  # NTU body information
                joints = int(line(handle))
                if joints != 25:
                    raise ValueError(f'Expected 25 NTU joints, got {joints}')
                for _ in range(joints):
                    xyz = line(handle).split()
                    if len(xyz) < 3 or not all(math.isfinite(float(v)) for v in xyz[:3]):
                        raise ValueError('Invalid 3D joint coordinates')
                joint_total += joints
                body_frames += 1
        if not body_frames:
            raise ValueError('All frames have zero detected bodies; try another sample and log this issue.')
    return f'frames={frames}; frames_with_body={nonempty_frames}; body_frames={body_frames}; joints={joint_total}'


def check(path):
    if not path.is_file() or path.stat().st_size == 0:
        raise ValueError('File missing or empty')
    suffix = path.suffix.lower()
    if suffix == '.skeleton':
        return check_skeleton(path)
    if suffix in ('.npy', '.npz'):
        import numpy as np
        value = np.load(path, allow_pickle=False)
        if suffix == '.npz':
            with value as archive:
                if not archive.files or any(archive[k].size == 0 for k in archive.files):
                    raise ValueError('Empty array/archive')
                return '; '.join(f'{k}: shape={archive[k].shape}, dtype={archive[k].dtype}' for k in archive.files)
        if value.size == 0:
            raise ValueError('Empty array')
        return f'shape={value.shape}; dtype={value.dtype}; nonempty={value.size > 0}'
    if suffix in ('.png', '.jpg', '.jpeg'):
        from PIL import Image
        with Image.open(path) as image:
            image.load()
            return f'format={image.format}; size={image.size}; mode={image.mode}'
    if suffix == '.csv':
        with path.open(encoding='utf-8-sig', newline='') as handle:
            rows = []
            for _, row in zip(range(5), csv.reader(handle)):
                rows.append(f'fields={len(row)}, first_5={row[:5]}')
        return '\n'.join(rows)
    raise ValueError('Unsupported format. For MM-Fi .bin/.mat use the official loader; this checker does not guess their schema.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('path', type=Path)
    args = parser.parse_args()
    try:
        print('FILE:', args.path.resolve())
        print(check(args.path))
    except (OSError, ValueError, ImportError) as error:
        parser.exit(1, 'CHECK FAILED: ' + str(error) + '\n')
    print('Read succeeded for this sample only. It does not certify the whole dataset or action labels.')


if __name__ == '__main__':
    main()
