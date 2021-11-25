from pprint import pprint
import os

with open('u-law.wav', mode='rb') as f:
    riff_header = {
        # 全体はRIFF形式となっている。[fmt ]チャンクと[data]チャンクは必須。
        # その他のチャンクはオプショナルであり、アプリケーションは未知のチャンクは無視しなくてはならない。
        # 数値はリトルエンディアンで扱われる。
        "01 RIFF_RiffID": f.read(4).decode('ascii'),  # Riffファイルである事を示すID。"RIFF"固定バイト
        "02 RIFF_FileSize": int.from_bytes(f.read(4), "little"),  # RiffID+FileSizeを除くファイル全体の長さ。リトルエンディアン
        "03 RIFF_Format": f.read(4).decode('ascii')  # Wavファイルである事を示すID。"WAVE"に固定
    }
    fmt_header = {
        "01 FMT_ChunkID": f.read(4).decode('ascii'),  # fmtチャンクヘッダー。"fmt "
        "02 FMT_ChunkSize": int.from_bytes(f.read(4), "little"),  # ChunkID+ChunkSizeを除くチャンクのサイズ。PCMの場合は通常16。μLawは18？
        "03 FMT_wFormatTag(2byte)": int.from_bytes(f.read(2), "little"),  # 0: Unknown
        # 1: PCM
        # 2: Microsoft-ADPCM
        # 3: IEEE Float
        # 6: G.711 A-law
        # 7: G.711 µ-law
        # 0x11: IMA-ADPCM
        # 0x16: G.723 ADPCM(Yamaha)
        # 0x31: GSM 6.10
        # 0x40: G.721 ADPCM
        # 0x50: MPEG
        # 0xFFFF: Experimental
        "04 FMT_nChannels(2byte)": int.from_bytes(f.read(2), "little"),  # モノラル ならば 1(01 00) ステレオ ならば 2(02 00)
        "05 FMT_nSamplesPerSec": int.from_bytes(f.read(4), "little"),  # サンプリングレート。0xac44=44.1KHz
        "06 FMT_nAvgBytesPerSec": int.from_bytes(f.read(4), "little"),
        # 平均バイトレート (Byte/sec) 44.1kHz 16bit ステレオ ならば 44100×2×2 = 176400(10 B1 02 00)
        "07 FMT_nBlockAlign(2byte)": int.from_bytes(f.read(2), "little"),
        # 1ブロックのバイト数。 (Byte/sample×チャンネル数) 16bit ステレオ ならば 2×2 = 4(04 00)
        "08 FMT_wBitsPerSample(2byte)": int.from_bytes(f.read(2), "little"),
        # サンプルあたりのビット数 (bit/sample) 16bit ならば 16(10 00)
        "09 FMT_cbSize(2byte)": int.from_bytes(f.read(2), "little")  # 追加情報のサイズ。PCMフォーマットではcbSizeおよび追加情報はなくても良い。
    }
    # fact_header = {
    #     "01 FACT_ChunkID": f.read(4).decode('ascii'),  # factチャンクヘッダー。"fact"。リニアPCMでは存在しない？
    #     "02 FACT_ChunkSize": int.from_bytes(f.read(4), "little"),  # ChunkID+ChunkSizeを除くチャンクのサイズ
    #     "03 FACT_dwSampleLength": int.from_bytes(f.read(4), "little")  # dataチャンクに記録されている1チャンネル当たりのサンプル数
    # }
    # data_header = {
    #     "01 DATA_ChunkID": f.read(4).decode('ascii'),  # dataチャンクヘッダー。"data"
    #     "02 DATA_ChunkSize": int.from_bytes(f.read(4), "little"),  # ChunkID+ChunkSize+パディングを除くチャンクのサイズ。
    # "03 DATA_SampleData":                                               # 音声データ部
    # "04 DATA_Padding(1byte)":       int.from_bytes(f.read(1), "little") # ChunkSizeが奇数の場合のみ追加される
    # }
pprint(riff_header)
pprint(fmt_header)

print(riff_header['02 RIFF_FileSize'] / fmt_header['06 FMT_nAvgBytesPerSec'])
