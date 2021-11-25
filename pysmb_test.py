import platform
from smb.SMBConnection import SMBConnection


class Smb(object):
    def __init__(self, *args, **kwargs):
        print(kwargs)
        self.conn = SMBConnection(*args, **kwargs)
        self.ip = ip

    def __enter__(self):
        self.conn.connect(self.ip, 139)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.conn.close()

    def echo(self, data):
        return self.conn.echo(data)


params = {
    'username': 'user',
    'password': 'pass',
    'remote_name': 'remote_name',
    'ip': '192.168.0.0',
    'is_direct_tcp': True
}
with Smb(**params) as smb:
    print(smb.echo("echo !!"))


if __name__ == "__main__":
    conn = SMBConnection(
        username='user',  # User
        password='pass',  # Password
        my_name=platform.uname().node,  # my_name: クライアントのNetBIOS名です。platform.node()から取得すると楽
        remote_name='remote_name',  # remote_name:サーバーのNetBIOS名
        is_direct_tcp=True
    )
    conn.connect(ip='192.168.0.0', port=445)

    print(conn.echo('echo success'))  # 疎通確認

    with open('source.txt', 'rb') as file:
        conn.storeFile('y\\autosave', 'dst.txt', file)

    # conn.createDirectory("autosave", path)

    conn.close()
    pass
