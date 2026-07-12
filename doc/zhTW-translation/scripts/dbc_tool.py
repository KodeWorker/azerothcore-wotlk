# Requires `mpyq` (pure-python MPQ reader): pip install --target=./pylibs mpyq
# (not installed system-wide in this session; --target avoids the externally-managed-env error)
import struct, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "pylibs"))
import mpyq

# Point at a local WotLK 3.3.5a zhTW client install's Data/zhTW dir. Use the LATEST
# patch-zhTW-N.MPQ (highest N) -- it has the most complete/current DBC data.
MPQ_PATH = os.environ.get(
    "ZHTW_CLIENT_MPQ",
    os.path.expanduser("~/WOW_Client_zhTW/Data/zhTW/patch-zhTW-3.MPQ"),
)
_archive = None

def archive():
    global _archive
    if _archive is None:
        _archive = mpyq.MPQArchive(MPQ_PATH)
    return _archive

def load_dbc(name):
    data = archive().read_file(('DBFilesClient\\' + name).encode())
    magic, record_count, field_count, record_size, string_block_size = struct.unpack('<4sIIII', data[:20])
    assert magic == b'WDBC', magic
    records_start = 20
    records_end = 20 + record_count * record_size
    string_block = data[records_end:records_end + string_block_size]
    def get_string(offset):
        end = string_block.find(b'\x00', offset)
        return string_block[offset:end].decode('utf-8', errors='replace')
    records = []
    for i in range(record_count):
        off = records_start + i * record_size
        rec = data[off:off + record_size]
        fields = struct.unpack('<' + 'I' * field_count, rec)
        records.append(fields)
    return {
        'record_count': record_count, 'field_count': field_count,
        'records': records, 'get_string': get_string, 'string_block_size': string_block_size,
    }

def probe(name, sample_ids, max_fields=None, clean_only=True, min_len=1, max_len=40):
    """Print all candidate string fields for given IDs, to identify the Name field index."""
    dbc = load_dbc(name)
    get_string = dbc['get_string']
    sbs = dbc['string_block_size']
    fc = dbc['field_count'] if not max_fields else min(max_fields, dbc['field_count'])
    print(f"{name}: {dbc['record_count']} records, {dbc['field_count']} fields")
    for rec in dbc['records']:
        if rec[0] in sample_ids:
            print(f"-- id={rec[0]} --")
            for idx in range(fc):
                val = rec[idx]
                if 0 < val < sbs:
                    s = get_string(val)
                    if not s:
                        continue
                    if clean_only and ('�' in s):
                        continue
                    if not (min_len <= len(s) <= max_len):
                        continue
                    print(f"  [{idx}] {val} -> {s!r}")

def dump_names(name, name_field_idx, out_path, id_field_idx=0):
    dbc = load_dbc(name)
    get_string = dbc['get_string']
    sbs = dbc['string_block_size']
    out = {}
    for rec in dbc['records']:
        rid = rec[id_field_idx]
        noff = rec[name_field_idx]
        nm = get_string(noff) if 0 < noff < sbs else ''
        if nm:
            out[rid] = nm
    with open(out_path, 'w', encoding='utf-8') as f:
        for rid in sorted(out):
            f.write(f"{rid}\t{out[rid]}\n")
    print(f"{name}: wrote {len(out)} entries -> {out_path}")
    return out

if __name__ == '__main__':
    pass
