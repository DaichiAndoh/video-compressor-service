# video-compressor-service &middot; ![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white)

TCPとカスタムアプリケーションレベルプロトコルを使用して動画ファイルの圧縮処理を行います。
クラアントから圧縮したい動画ファイルとcrf値をサーバに送信します。
サーバはその動画ファイルを指定されたcrf値で圧縮し、圧縮したファイルをクライアントに送り返します。

## Usage

### サーバ起動

```
$ python server.py
[*] server is listening...
```

### クライアント起動, 実行

```
$ python client.py
[*] connected to the server

[-] enter file type to upload (mp4, mp3, json, avi...): mp4
[-] enter path to the file: sample.mp4
[*] file size: 805610 bytes
[-] enter crf value (0-51): 35
[*] request data send success
[*] compressed file size: 206482 bytes
[*] response data reception success
```

### サーバログ

```
$ python server.py
[*] server is listening...

[*] connected
[*] received file size: 805610 bytes
[*] compressing file...
[*] compressed file size: 206482 bytes
[*] disconnected
```
