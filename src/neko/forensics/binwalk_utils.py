import binwalk
from pathlib import Path


def extract(path: str):
    signature_obj = binwalk.scan(path, signature=True, quiet=True)[0]
    offsets = []
    descriptions = []
    for res in signature_obj.results:
        offsets.append(res.offset)
        descriptions.append(res.description)

    dir_extracted = Path("extracted")
    dir_extracted.mkdir(exist_ok=True)

    file = Path(path).open("rb").read()
    n = len(offsets)
    offsets.append(1 << 32)
    for i in range(n):
        offset = offsets[i]
        # description = descriptions[i]
        next_offset = offsets[i + 1]
        (dir_extracted / str(offset)).open("wb").write(file[offset:next_offset])
