s = 'あいうえお'

# unicode-escapeはPython特有のエンコーディング。
b = s.encode('unicode-escape')
# b'\\u3042\\u3044\\u3046\\u3048\\u304a'

# バイト列から文字列への変換（デコード）はバイト列（bytes型）のメソッドdecode()を使う。
s_from_b = b.decode('unicode-escape')

# Unicodeエスケープされたバイト列をutf-8でデコードすると、Unicodeエスケープのまま文字列に変換される。
s_from_b_error = b.decode('utf-8')
print(s_from_b_error)
print(type(s_from_b_error))  # str型

# このような文字列は、encode()でバイト列に変換してから再度decode()で文字列に変換すると、Unicodeエスケープされていない文字列に戻る。
s_from_s = s_from_b_error.encode().decode('unicode-escape')

print(s_from_s)
# あいうえお

# 標準ライブラリのcodecsモジュールを使って直接変換することも可能。
import codecs
s_from_s_codecs = codecs.decode(s_from_b_error, 'unicode-escape')
print(s_from_s_codecs)
# あいうえお

print(type(s_from_s_codecs))