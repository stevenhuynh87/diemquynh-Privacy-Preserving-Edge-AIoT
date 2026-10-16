import io
import math
from pathlib import Path
from zipfile import ZipFile

ROOT = Path(
    r"C:\Q\NCKH\Privacy-Preserving Edge AIoT Fall Detection via Cross-Modal Knowledge Distillation from RGB to Low-Resolution"
    r"\phykd_datasets\NTU_RGBD_120"
)

logs = []


def log(text):
    logs.append(text)
    print(text)


def read_line(stream):
    line = stream.readline()
    if line == "":
        raise ValueError("Unexpected end of skeleton file")
    return line.strip()


def check_skeleton(stream):
    frames = int(read_line(stream))
    if frames <= 0:
        raise ValueError("No frames")

    bodies_total = 0
    joints_total = 0

    for frame in range(frames):
        bodies = int(read_line(stream))
        if bodies < 0:
            raise ValueError("Invalid body count")

        for body in range(bodies):
            read_line(stream)  # Body metadata
            joints = int(read_line(stream))
            if joints != 25:
                raise ValueError(f"Expected 25 joints, got {joints}")

            for joint in range(joints):
                values = read_line(stream).split()
                if len(values) < 3:
                    raise ValueError("Missing XYZ coordinates")
                xyz = [float(x) for x in values[:3]]
                if not all(math.isfinite(x) for x in xyz):
                    raise ValueError("Non-finite XYZ coordinates")

            bodies_total += 1
            joints_total += joints

    if bodies_total == 0:
        raise ValueError("No bodies in this sample")

    return frames, bodies_total, joints_total


for name in [
    "nturgbd_skeletons_s001_to_s017.zip",
    "nturgbd_skeletons_s018_to_s032.zip",
]:
    log(f"\nArchive: {name}")

    try:
        with ZipFile(ROOT / name) as archive:
            files = sorted(
                n for n in archive.namelist()
                if n.lower().endswith(".skeleton")
            )
            log(f"Skeleton files listed: {len(files)}")
            if not files:
                raise ValueError("No skeleton files in archive")

            sample = next(
                (n for n in files if n.endswith("A043.skeleton")),
                files[0],
            )
            log(f"Sample: {sample}")

            with archive.open(sample) as raw:
                with io.TextIOWrapper(
                    raw, encoding="utf-8-sig"
                ) as stream:
                    frames, bodies, joints = check_skeleton(stream)

            log(f"Frames: {frames}")
            log(f"Body instances across frames: {bodies}")
            log(f"Joint instances checked: {joints}")
            log("Joints per body: 25")
            log("Finite XYZ: True")
            log("Sample read: PASS")

    except Exception as error:
        log(f"Sample read: FAIL — {error}")

output = Path("reports/ntu_sample_check.txt")
output.parent.mkdir(parents=True, exist_ok=True)
output.write_text("\n".join(logs), encoding="utf-8")
print(f"\nSaved: {output}")
