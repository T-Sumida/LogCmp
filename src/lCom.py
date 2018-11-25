# -*- coding:utf-8 -*-
import sys
import threading
import os
import re

# 差分箇所から前後何行出力するかを決める変数
OUTPUT_LINE_NUM = 10

# アノテート時の変換元を設定するワード（正規表現）
OMMIT_WORD = r'\[M.+0\]'

# アノテート時の変換後を設定するワード
REPLACE_WORD = '[OMMIT]'

# エラーID
(
    ARGERROR,
    NOENT,
) = range(0, 2)


def printError(errorID, arg):
    """
    エラーメッセージを出力する.

    Parameters
    ----------
    errorID : int
        エラー識別子
    arg : 
        エラー出力時に必要な情報
    """
    if errorID == ARGERROR:
        print("引数の数が合いません")
        print("python lComp.py 【比較元ファイルパス】 【比較対象ファイルパス】")
    elif errorID == NOENT:
        print('No such file : ' + arg)
    exit()


def checkArgs():
    """
    引数の数をチェックする.
    """
    if len(sys.argv) <= 2:
        printError(ARGERROR, 1)


def checkFile():
    """
    引数で渡されたファイルパスのファイルが存在するかチェックする.

    Returns
    -------
    args[1] : str
        比較元ファイルのパス
    args[2] : str
        比較対象ファイルのパス
    """
    args = sys.argv
    if not os.path.isfile(args[1]):
        printError(NOENT, args[1])
    if not os.path.isfile(args[2]):
        printError(NOENT, args[2])
    return (args[1], args[2])


def anotate(filePath):
    """
    引数で渡されたファイルのバックアップを作り、
    そのファイル内のOMMIT_WORDをREPLACE_WORDに変換し、ファイルに書き出す.

    Parameters
    ----------
    filePath : str
        対象ファイルのパス
    """
    os.rename(filePath, filePath+".tmp")
    writeObj = open(filePath, 'w')
    with open(filePath+".tmp", 'r') as fileobject:
        for line in fileobject:
            writeObj.write(re.sub(OMMIT_WORD, REPLACE_WORD, line))
    writeObj.close()


def controlThread(filePath1, filePath2):
    """
    引数で渡される2つのファイルに対して、マルチスレッドでアノテートを行う.

    Parameters
    ----------
    filePath1 : str
        比較元ファイルのパス
    filePath2 : str
        比較対象ファイルのパス
    """
    thread1 = threading.Thread(target=anotate, args=([filePath1]))
    thread2 = threading.Thread(target=anotate, args=([filePath2]))
    thread1.start()
    thread2.start()
    thread1.join()
    thread2.join()


def outputDiff(filePath1, filePath2):
    """
    引数で渡される2つのファイルに対して、diffコマンドを実行し結果を出力する.

    Parameters
    ----------
    filePath1 : str
        比較元ファイルのパス
    filePath2 : str
        比較対象ファイルのパス
    """
    commandStr = "diff " + filePath1 + " " + filePath2 + " -U" + str(OUTPUT_LINE_NUM)
    os.system(commandStr)


def cleanUp(filePath1, filePath2):
    """
    アノテート後のファイルを削除し、
    アノテート時に作成したバックアップファイルを元のファイル名に直す.

    Parameters
    ----------
    filePath1 : str
        比較元ファイルのパス
    filePath2 : str
        比較対象ファイルのパス
    """
    os.remove(filePath1)
    os.remove(filePath2)
    os.rename(filePath1+".tmp", filePath1)
    os.rename(filePath2+".tmp", filePath2)


if __name__ == "__main__":
    checkArgs()  # 引数の数をチェック
    filePath1, filePath2 = checkFile()  # 引数のファイルパスが存在するかチェック
    controlThread(filePath1, filePath2)  # マルチスレッドで引数ファイルの中身のアノテートを実施
    outputDiff(filePath1, filePath2)  # アノテート後の両ファイルのDIFF差分を出力
    cleanUp(filePath1, filePath2)  # アノテート時のファイル変更をもとに戻す
