import zlib
import tqdm
import copy
import traceback


def repair_idat_data(
    broken_file: bytes,
    idat_data_start: int,
    idat_data_end: int,
    width: int,
    height: int,
    bit_depth: int,  # unused
    wrong: list[(int, list[bytes])] = {},
    color_min: int = 0,
    color_max: int = 0xFF,
    selected: list[int] = [],
    max_m=2,
    best_filename: str = "tmp.png",
) -> bytes:
    """
    zlib解凍結果とフィルタリング解除結果を用いてIDATデータの修復を試みる。
    wrong: [(ファイルにおける開始アドレス, [候補1, 候補2, ...])]
    wrongに指定されない箇所は合っているとみなす。
    wrongはアドレスでソート済みで無ければならない。
    現状パレットモードでビット深度が8のみ動作を確認している。
    best_filenameに最もスコアが良いファイルが保存される。
    (候補数)^Mの全探索して最もスコアが良いものを採用
    """

    class DecompressionTemporaryData:
        """
        解凍中のデータ保存。途中から再開できるように。
        """

        def __init__(self, decompressobj=None):
            if decompressobj:
                self.decompressobj = decompressobj
            else:
                self.decompressobj = zlib.decompressobj()
            self.decompressed_idat_data: bytes = b""
            self.filter: int = None
            self.pixels: list[int] = []

    def next(decompression: DecompressionTemporaryData, data_b: int):
        """
        filterが0,1,2に対応。
        """
        decompressed_fragment = decompression.decompressobj.decompress(bytes([data_b]))
        new_decompressed_idat_data = decompression.decompressed_idat_data

        for fragment_byte in decompressed_fragment:
            idat_data_i = len(new_decompressed_idat_data)
            pixel_i_in_line = idat_data_i % (1 + width) - 1

            if idat_data_i % (1 + width) == 0:
                decompression.filter = fragment_byte
                assert 0 <= decompression.filter <= 4
            else:
                # filter 0はそのままfragment_byteを使う。1,2はsignedしたものを使う（差分なので負がある）。
                if fragment_byte >= 0x80:
                    signed_fragment_byte = -(0x100 - fragment_byte)
                else:
                    signed_fragment_byte = fragment_byte
                if decompression.filter == 0:
                    pixel = fragment_byte
                elif decompression.filter == 1:
                    # 左のピクセルとの差分
                    if pixel_i_in_line == 0:
                        pixel = signed_fragment_byte
                    else:
                        pixel = decompression.pixels[-1] + signed_fragment_byte
                elif decompression.filter == 2:
                    # 上のピクセルとの差分
                    pixel = decompression.pixels[-width] + signed_fragment_byte
                assert color_min <= pixel <= color_max
                decompression.pixels.append(pixel)

            new_decompressed_idat_data += bytes([fragment_byte])

        decompression.decompressed_idat_data = new_decompressed_idat_data

    selected = selected.copy()

    while True:
        best_len = 0
        best_mask = 0

        n_mask = 1
        m = min(max_m, len(wrong) - len(selected))
        for i in range(m):
            candidates_num = len(wrong[len(selected) + i][1])
            n_mask *= candidates_num
        file_byte_list = list(broken_file)

        for i, can_i in enumerate(selected):
            start_address, candidates = wrong[i]
            candidate = candidates[can_i]
            end_address = start_address + len(candidate)
            file_byte_list[start_address:end_address] = list(candidate)

        if m == 0:
            return bytes(file_byte_list)

        # 全てのマスクで共通して確定decompressできる部分
        base_decompression = DecompressionTemporaryData()
        correct_end_address = wrong[len(selected)][0]

        for address in range(idat_data_start, correct_end_address):
            data_b = file_byte_list[address]
            next(base_decompression, data_b)

        # 全探索
        for mask in tqdm.tqdm(range(n_mask)):
            tmp_mask = mask

            for i in range(m):
                start_address, candidates = wrong[len(selected) + i]
                can_i = tmp_mask % len(candidates)
                candidate = candidates[can_i]
                end_address = start_address + len(candidate)
                assert idat_data_start <= start_address < idat_data_end
                assert idat_data_start < end_address <= idat_data_end
                file_byte_list[start_address:end_address] = list(candidate)
                tmp_mask //= len(candidates)

            file = bytes(file_byte_list)
            decompression = copy.deepcopy(base_decompression)
            error = False

            for address in range(correct_end_address, idat_data_end):
                data_b = file[address]
                try:
                    next(decompression, data_b)
                except Exception:
                    if best_len < len(decompression.decompressed_idat_data):
                        print("best is updated:", len(decompression.decompressed_idat_data), bin(mask)[2:])
                        print("selected:", selected)
                        best_len = len(decompression.decompressed_idat_data)
                        best_mask = mask
                        for h in range(max(0, len(decompression.decompressed_idat_data) // (1 + width) - 5), height):
                            start = (1 + width) * h
                            if len(decompression.decompressed_idat_data) < start:
                                break
                            end = start + 16
                            # print(img[start:(1+width)*(h+1)].hex())
                            print(
                                f"{h}:",
                                decompression.decompressed_idat_data[start:end].hex(),
                                decompression.decompressed_idat_data[(1 + width) * (h + 1) - 16 : (1 + width) * (h + 1)].hex(),
                            )
                        with open(best_filename, "wb") as f:
                            f.write(file)

                    # traceback.print_exc()
                    error = True
                    break

            if not error and len(decompression.decompressed_idat_data) > 0:
                print("no error")
                return file

        selected.append(best_mask % 2)


def repair_png_helper(file: bytes, repair=False) -> bytes:
    """
    壊れたPNGを修正するヘルパー。各チャンクごとにCRCをチェック。
    """
    file_len = len(file)
    SIGNATURE = bytes.fromhex("89504E470D0A1A0A")
    if repair and file[: len(SIGNATURE)] != SIGNATURE:
        print("signature is broken")
        file[: len(SIGNATURE)] = SIGNATURE
    chunk_i = 0
    byte_i = len(SIGNATURE)
    CHUNK_TYPES = [b"IHDR", b"PLTE", b"tRNS", b"IDAT", b"IEND"]
    while byte_i < file_len:
        print("chunk start at", byte_i)
        # chunk_len = len(length) + len(type) + len(data) + len(crc)
        chunk_data_len = int.from_bytes(file[byte_i : byte_i + 4], "big")
        chunk_len = 4 + 4 + chunk_data_len + 4
        chunk_type = file[byte_i + 4 : byte_i + 8]
        chunk_data_start = byte_i + 8
        chunk_data_end = chunk_data_start + chunk_data_len
        print(f"chuck data is [{chunk_data_start}:{chunk_data_end}]")
        assert byte_i + chunk_len <= file_len, "length is broken"
        chunk_data = file[chunk_data_start:chunk_data_end]
        chunk_crc = file[chunk_data_end : byte_i + chunk_len]

        print(f"chunk type is {chunk_type}")
        if chunk_type not in CHUNK_TYPES:
            print("not supported chunk type or broken chunk type")

        crc_input = chunk_type + chunk_data
        calculated_crc = zlib.crc32(crc_input).to_bytes(4, "big")
        print(f"CRC: {chunk_crc == calculated_crc}")

        if chunk_type == b"IHDR":
            if chunk_data_len != 13:
                print("IHDR chunk len is broken")
            i = 0
            width = int.from_bytes(chunk_data[i : i + 4], "big")
            i += 4
            height = int.from_bytes(chunk_data[i : i + 4], "big")
            i += 4
            bit_depth = int.from_bytes(chunk_data[i : i + 1], "big")
            i += 1
            color_space = int.from_bytes(chunk_data[i : i + 1], "big")
            i += 1
            compression_method = int.from_bytes(chunk_data[i : i + 1], "big")
            i += 1
            filter_method = int.from_bytes(chunk_data[i : i + 1], "big")
            i += 1
            interlace_method = int.from_bytes(chunk_data[i : i + 1], "big")
            print("Details:")
            print(f"  width: {width}")
            print(f"  height: {height}")
            print(f"  bit depth: {bit_depth}")
            print(f"  color space: {color_space}")
            print(f"  compression method: {compression_method}")
            print(f"  filter method: {filter_method}")
            print(f"  interlace method: {interlace_method}")

        chunk_i += 1
        byte_i += chunk_len
        print()
    return file
