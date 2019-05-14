# 数据综合分析
import os
import codecs
from aip import AipNlp
import random

root = "Data"

# # 单元函数
# 读取文件列表
def readFileList():
    for dirpath, dirnames, fileList in os.walk(root):
        pass
    return fileList

# 读取文件列表中的弹幕数
def numSta():
    fileList = readFileList()
    num = 0
    for name in fileList:
        path = root + '\\' + name
        f = codecs.open(path, 'r', 'utf-8')
        num += int(f.readlines()[3].split('：')[1])
    return num

# 随机数生成器
def randomList(total, rate):
    need = int(total*rate)
    randomNum = []
    for n in range(need):
        randomNum.append(random.randint(0, total-1))
    randomNum.sort()
    return randomNum

# 按排名分四档
def classByNum():
    fl = readFileList()
    totalNum = numSta()
    averNum = totalNum // len(fl)
    quarter = averNum // 2
    c1 = []
    c2 = []
    c3 = []
    c4 = []
    for name in fl:
        path = root + '\\' + name
        f = codecs.open(path, 'r', 'utf-8')
        num = int(f.readlines()[3].split('：')[1])
        if num >= averNum + quarter:
            c1.append(name)
        elif averNum <= num < (averNum + quarter):
            c2.append(name)
        elif (averNum - quarter) <= num < averNum:
            c3.append(name)
        else:
            c4.append(name)
    f.close()
    return c1, c2, c3, c4

# # 弹幕时间分布
# 总体分布
def totalRead(fileList, file = 'timeCount.txt'):
    time = []

    for name in fileList:
        #print(name)
        path = root + '\\' + name
        f = codecs.open(path, 'r', 'utf-8')
        timeList = []
        for line in f.readlines()[5:]:
            timeList.append(float(line.split()[0]))
        totalTime = timeList[-1]
        for n in range(len(timeList)):
            timeList[n] = timeList[n] / totalTime
        time.extend(timeList)
        f.close()

    time.sort()

    size = 0.001
    plus = size/2

    f = open(file, 'w')

    num = 0
    for n in time:
        if n >= 0 and n < plus:
            num += 1
    ws = str(num) + '\n'
    f.write(ws)

    front = size - plus
    later = size + plus
    while later <= 1 - plus:
        num = 0
        for n in time:
            if n >= front and n < later:
                num += 1
        ws = str(num) + '\n'
        f.write(ws)
        front += size
        later += size

    num = 0
    for n in time:
        if n >= 1 - plus and n <= 1:
            num += 1
    ws = str(num) + '\n'
    f.write(ws)
    f.close()

# 分类分布
def classDistri():
    c1, c2, c3, c4 = classByNum()
    totalRead(c1, 'timeCount1.txt')
    totalRead(c2, 'timeCount2.txt')
    totalRead(c3, 'timeCount3.txt')
    totalRead(c4, 'timeCount4.txt')

# # 视频开头部分
# 实际占比
def front():
    c1, c2, c3, c4 = classByNum()
    def ana(c, rate):
        total = 0
        num = 0
        for name in c:
            path = root + '\\' + name
            f = codecs.open(path, 'r', 'utf-8')
            total += int(f.readlines()[3].split('：')[1])
            f.seek(0)
            timeList = []
            for line in f.readlines()[5:]:
                timeList.append(float(line.split()[0]))
            f.close()
            finalTime = float(timeList[-1])
            divTime = finalTime*rate
            for time in timeList:
                num += 1
                if float(time)>divTime:
                    break
        percent = num/total
        print(percent)
        return percent
    f = open('front.txt', 'w')
    for rate in 0.025, 0.05, 0.1:
        for c in c1, c2, c3, c4:
            percent = ana(c, rate)
            ws = str(percent)+' '
            f.write(ws)
        ws = '\n'
        f.write(ws)
    f.close()

# 整体弹幕情绪占比
def baiduAPI(fileList, filename):
    # 210条/分钟
    """ 你的 APPID AK SK """
    APP_ID = '11524387'
    API_KEY = 'Zt01mRgDfR1fNLMy2l1ej9W2'
    SECRET_KEY = 'tIdOYOUFIsBj65VFtnz5K9x2crv2AFbc'

    client = AipNlp(APP_ID, API_KEY, SECRET_KEY)  # 生成端口

    expectTime = 60  # 期望运行时间（分钟）

    commentNum = numSta()
    rate = (expectTime*210)/commentNum  # 调节速率
    negative = 0
    neutral = 0
    positive = 0
    fileNum = 1
    fileTot = len(fileList)
    for name in fileList:
        try:
            print("{}/{}".format(fileNum, fileTot))
            fileNum += 1
            path = root + '\\' + name
            f = codecs.open(path, 'r', 'utf-8')
            comSum = int(f.readlines()[3].split('：')[1][:-2])
            f.seek(0)
            time = 1
            err = 0
            randomNum = randomList(comSum, rate)
            comSum = int(comSum*rate)
            commentList = []
        except:
            continue
        # 读取弹幕目录
        for line in f.readlines()[5:]:
            try:
                comment = line.split()[2]
                commentList.append(comment)
            except:
                continue
        # 随机判断弹幕情绪
        for n in randomNum:
            comment = commentList[n]
            try:
                print("\t{}/{}".format(time, comSum))
                result = client.sentimentClassify(comment)
                sentiment = result['items'][0]['sentiment']
                if sentiment == 0:
                    negative += 1
                elif sentiment == 1:
                    neutral += 1
                else:
                    positive += 1
                time += 1
            except:
                err += 1
                comSum -= 1
                continue  # 特殊字符直接跳过
        f.close()
    total = negative + neutral + positive
    # 输出三种情绪所占百分比
    f = open(filename, 'w')
    ws = "negative {}\nneutral {}\npositive {}\nerror {}".format(negative/total, neutral/total, positive/total, err)
    f.write(ws)
    f.close()

# 开头和后部部分情绪占比
def fbPer():
    APP_ID = '11524387'
    API_KEY = 'Zt01mRgDfR1fNLMy2l1ej9W2'
    SECRET_KEY = 'tIdOYOUFIsBj65VFtnz5K9x2crv2AFbc'

    client = AipNlp(APP_ID, API_KEY, SECRET_KEY)  # 生成端口

    expectTime = 60  # 期望运行时间（分钟）

    negF = 0
    negB = 0
    neuF = 0
    neuB = 0
    posF = 0
    posB = 0
    frontRate = 0.1

    fileList = readFileList()
    commentNum = numSta()
    rate = (expectTime * 220) / commentNum  # 调节速率
    fileNum = 1
    fileTot = len(fileList)

    fro = 0
    b = 0

    for name in fileList:
        print("{}/{}".format(fileNum, fileTot))
        fileNum += 1
        path = root + '\\' + name
        f = codecs.open(path, 'r', 'utf-8')
        timeList = []
        try:
            for line in f.readlines()[5:]:
                timeList.append(float(line.split()[0]))
        except:
            continue
        f.seek(0)
        finalTime = float(timeList[-1])
        divTime = finalTime * frontRate  # 前后部分割时间点
        frontNum = 0  # 分割点的弹幕数
        for time in timeList:
            frontNum += 1
            if float(time) > divTime:
                break
        comSum = int(f.readlines()[3].split('：')[1])
        f.seek(0)
        time = 1
        randomNum = randomList(comSum, rate)
        comSum = int(comSum * rate)
        commentList = []
        # 读取弹幕目录
        try:
            for line in f.readlines()[5:]:
                comment = line.split()[2]
                commentList.append(comment)
        except:
            continue
        # 随机判断弹幕情绪
        flag = False
        negative = 0
        neutral = 0
        positive = 0

        for n in randomNum:
            comment = commentList[n]
            if n > frontNum and flag is False:
                flag = True
                negF += negative
                neuF += neutral
                posF += positive
                negative = 0
                neutral = 0
                positive = 0
                fro += 1
            try:
                print("\t{}/{}".format(time, comSum))
                result = client.sentimentClassify(comment)
                sentiment = result['items'][0]['sentiment']
                if sentiment == 0:
                    negative += 1
                elif sentiment == 1:
                    neutral += 1
                else:
                    positive += 1
                time += 1
            except:
                comSum -= 1
                continue  # 特殊字符直接跳过
        f.close()
        if flag is False:
            negF = 0
            neuF = 0
            posF = 0

        negB += negative
        neuB += neutral
        posB += positive

    f = open('fbper.txt', 'w')
    fTotal = negF + neuF + posF
    bTotal = negB + neuB + posB
    if fTotal == 0:
        fTotal = 1
    if bTotal == 0:
        bTotal = 1
    ws = "{} {} {}\n".format(negF/fTotal, neuF/fTotal, posF/fTotal)
    f.write(ws)
    ws = "{} {} {}\n".format(negB / bTotal, neuB / bTotal, posB / bTotal)
    f.write(ws)
    f.close()

# 方差分析
def frontBackAI():
    APP_ID = '11524387'
    API_KEY = 'Zt01mRgDfR1fNLMy2l1ej9W2'
    SECRET_KEY = 'tIdOYOUFIsBj65VFtnz5K9x2crv2AFbc'

    client = AipNlp(APP_ID, API_KEY, SECRET_KEY)  # 生成端口

    expectTime = 120  # 期望运行时间（分钟）

    negF = []
    negB = []
    neuF = []
    neuB = []
    posF = []
    posB = []
    frontRate = 0.1

    fileList = readFileList()
    commentNum = numSta()
    rate = (expectTime * 220) / commentNum  # 调节速率
    fileNum = 1
    fileTot = len(fileList)

    fro = 0
    b = 0

    for name in fileList:
        print("{}/{}".format(fileNum, fileTot))
        fileNum += 1
        path = root + '\\' + name
        f = codecs.open(path, 'r', 'utf-8')
        timeList = []
        try:
            for line in f.readlines()[5:]:
                timeList.append(float(line.split()[0]))
        except:
            continue
        f.seek(0)
        finalTime = float(timeList[-1])
        divTime = finalTime * frontRate  # 前后部分割时间点
        frontNum = 0  # 分割点的弹幕数
        for time in timeList:
            frontNum += 1
            if float(time) > divTime:
                break
        comSum = int(f.readlines()[3].split('：')[1])
        f.seek(0)
        time = 1
        randomNum = randomList(comSum, rate)
        comSum = int(comSum * rate)
        commentList = []
        # 读取弹幕目录
        try:
            for line in f.readlines()[5:]:
                comment = line.split()[2]
                commentList.append(comment)
        except:
            continue
        # 随机判断弹幕情绪
        flag = False
        negative = 0
        neutral = 0
        positive = 0

        for n in randomNum:
            comment = commentList[n]
            if n > frontNum and flag is False:
                flag = True
                total = negative + neutral + positive
                if total == 0:
                    total = 1
                negF.append(negative / total)
                neuF.append(neutral / total)
                posF.append(positive / total)
                negative = 0
                neutral = 0
                positive = 0
                fro += 1
            try:
                print("\t{}/{}".format(time, comSum))
                result = client.sentimentClassify(comment)
                sentiment = result['items'][0]['sentiment']
                if sentiment == 0:
                    negative += 1
                elif sentiment == 1:
                    neutral += 1
                else:
                    positive += 1
                time += 1
            except:
                comSum -= 1
                continue  # 特殊字符直接跳过
        f.close()
        if flag is False:
            negF.append(0.0)
            neuF.append(0.0)
            posF.append(0.0)
            fro += 1
        total = negative + neutral + positive
        if total == 0:
            total = 1
        negB.append(negative / total)
        neuB.append(neutral / total)
        posB.append(positive / total)
        b += 1
    def putOut(file, f, b):
        for n in f:
            ws = '{} '.format(n)
            file.write(ws)
        file.write('\n\n')
        for n in b:
            ws = '{} '.format(n)
            file.write(ws)


    negativeF = open('negative.txt', 'w')
    neutralF = open('neutral.txt', 'w')
    positiveF = open('positive.txt', 'w')
    putOut(negativeF, negF, negB)
    putOut(neutralF, neuF, neuB)
    putOut(positiveF, posF, posB)
    positiveF.close()
    neutralF.close()
    negativeF.close()
    print(fro, b)
"""
MATLAB代码
a = [...];  % 开头数据，列向量
b = [...];  % 后部数据，列向量
x = [a b];
p = anova1(x)
"""

# # 视频内容类别
# 一档和其他档情绪占比
def firstToThreeOther():
    c1, c2, c3, c4 = classByNum()
    c2 += c3 + c4
    baiduAPI(c1, "first.txt")
    baiduAPI(c2, "other.txt")

# 关键词搜索法
def classify():
    # 分类标准
    classDic = {
        "高兴": 0,
        "内容与操作": 0,
        "画面感": 0,
        "关联性": 0,
        "出乎意料": 0,
        "感谢": 0,
        "其他": 0,
        "主动性": 0,
        "负面情绪": 0,
        "B站特色": 0,
    }

    # 关键词
    # 高兴
    humourList = ['233', '哈哈', 'h', '笑', '噗', '真香']
    # 内容与操作
    act6List = ['66', '不错', '赞', '投币', '硬币', '收藏', '!', '！', 'yeah', '强', '帅', '人才', '牛', '厉害', '稳']
    # 画面感
    text6List = ['福利', '良心', '打call', '喜欢', '可爱', '萌', '好看', '棒', 'dalao', '大佬', '燃', '美', '火', '哇',
                 '漂亮', '啊啊啊', 'cool', '酷']
    # 关联性
    seriesList = ['终于', 'leile', '来了', 'lei了', '期待', '失踪人口', '好久不见', '系列', '更了', '高产', '失踪人口回归',
                  '来晚了', '生日快乐']
    # 出乎意料
    surpriseList = ['意外', '惊', '没想到', '卧槽', '妈耶', 'woc', '巧了', '心脏', '吓', '高能', '社会', '妙']
    # 感谢
    thanksList = ['感谢', '辛苦', '心疼', '泪', '谢', '爱', '支持', '哭']
    # 主动性
    positiveList = ['干', '肝', '？', '?', '了解一下', 'emm', 'BGM', 'bgm', '额', '想', '感觉', '嘤']
    # 负面情绪
    negativeList = ['夭寿', '难受', '骂', '完了', '…', '别', '麻烦', '。。', 'gg', 'GG', '恶', '活该', '死']
    # B站特色
    biliList = ['♂', 'up', 'Up', 'UP', '基佬', '空降', '字幕', '计数', '1.25', '1.5', '0.5',  '开头', '火钳刘明', '每日', '哲学',
                'Van', '自由', '兄贵', '那个男人', '欢迎回来', 'gay', '弹幕', '鬼畜']

    fileList = readFileList()
    fileSum = len(fileList)
    fileCount = 0
    for name in fileList:
        fileCount += 1
        path = root + '\\' + name
        f = codecs.open(path, 'r', 'utf-8')
        comSum = int(f.readlines()[3].split('：')[1][:-2])
        comCount = 0
        f.seek(0)  # 文件读取后要复位
        for line in f.readlines()[5:]:
            try:
                comment = line.split()[2]
            except:
                continue
            hasSel = False

            # 判断
            for n in humourList:
                if n in comment:
                    classDic["高兴"] += 1
                    comCount += 1
                    hasSel = True
            if not hasSel:
                for n in act6List:
                    if n in comment:
                        classDic["内容与操作"] += 1
                        comCount += 1
                        hasSel = True
            if not hasSel:
                for n in text6List:
                    if n in comment:
                        classDic["画面感"] += 1
                        comCount += 1
                        hasSel = True
            if not hasSel:
                for n in seriesList:
                    if n in comment:
                        classDic["关联性"] += 1
                        comCount += 1
                        hasSel = True
            if not hasSel:
                for n in surpriseList:
                    if n in comment:
                        classDic["出乎意料"] += 1
                        comCount += 1
                        hasSel = True
            if not hasSel:
                for n in thanksList:
                    if n in comment:
                        classDic["感谢"] += 1
                        comCount += 1
                        hasSel = True
            if not hasSel:
                for n in positiveList:
                    if n in comment:
                        classDic["主动性"] += 1
                        comCount += 1
                        hasSel = True
            if not hasSel:
                for n in negativeList:
                    if n in comment:
                        classDic["负面情绪"] += 1
                        comCount += 1
                        hasSel = True
            if not hasSel:
                for n in biliList:
                    if n in comment:
                        classDic["B站特色"] += 1
                        comCount += 1
        classDic["其他"] += comSum-comCount
        f.close()

    # 计算每部分的比例
    sum = 0
    for key in classDic:
        sum += classDic[key]
    for key in classDic:
        classDic[key] /= sum
    f = open('classify.txt', 'w')
    for key in classDic:
        ws = '{} {}\n'.format(key, classDic[key])
        f.write(ws)
    f.close()

# # “其他”类研究
# “其他”占各视频比例的分布
def other(fileList, fout='other.txt'):

    # 关键词
    # 幽默
    humourList = ['233', '哈哈', 'h', '笑', '噗', '真香']
    # 操作赞叹
    act6List = ['66', '不错', '赞', '投币', '硬币', '收藏', '!', '！', 'yeah', '强', '帅', '人才', '牛', '厉害', '稳']
    # 内容赞叹
    text6List = ['福利', '良心', '打call', '喜欢', '可爱', '萌', '好看', '棒', 'dalao', '大佬', '燃', '美', '火', '哇',
                 '漂亮', '啊啊啊', 'cool', '酷']
    # 关联性
    seriesList = ['终于', 'leile', '来了', 'lei了', '期待', '失踪人口', '好久不见', '系列', '更了', '高产', '失踪人口回归',
                  '来晚了', '生日快乐']
    # 出乎意料
    surpriseList = ['意外', '惊', '没想到', '卧槽', '妈耶', 'woc', '巧了', '心脏', '吓', '高能', '社会', '妙']
    # 感谢
    thanksList = ['感谢', '辛苦', '心疼', '泪', '谢', '爱', '支持']
    # 主动性
    positiveList = ['干', '肝', '？', '?', '了解一下', 'emm', 'BGM', 'bgm', '额', '想', '感觉', '嘤']
    # 负面情绪
    negativeList = ['夭寿', '难受', '骂', '完了', '…', '别', '麻烦', '。。', 'gg', 'GG', '恶', '活该', '死']
    # B站特色
    biliList = ['♂', 'up', 'Up', 'UP', '基佬', '空降', '字幕', '计数', '1.25', '1.5', '0.5',  '开头', '火钳刘明', '每日', '哲学',
                'Van', '自由', '兄贵', '那个男人', '欢迎回来', 'gay', '弹幕', '鬼畜']

    fileSum = len(fileList)
    fileCount = 0
    otherList = []
    for name in fileList:
        # 分类标准
        classDic = {
            "高兴": 0,
            "操作赞叹": 0,
            "内容赞叹": 0,
            "关联性": 0,
            "出乎意料": 0,
            "感谢": 0,
            "其他": 0,
            "主动性": 0,
            "负面情绪": 0,
            "B站特色": 0,
        }
        fileCount += 1
        path = root + '\\' + name
        f = codecs.open(path, 'r', 'utf-8')
        comSum = int(f.readlines()[3].split('：')[1][:-2])
        comCount = 0
        f.seek(0)  # 文件读取后要复位
        for line in f.readlines()[5:]:
            try:
                comment = line.split()[2]
            except:
                continue
            hasSel = False

            # 判断
            for n in humourList:
                if n in comment:
                    classDic["高兴"] += 1
                    comCount += 1
                    hasSel = True
            if not hasSel:
                for n in act6List:
                    if n in comment:
                        classDic["操作赞叹"] += 1
                        comCount += 1
                        hasSel = True
            if not hasSel:
                for n in text6List:
                    if n in comment:
                        classDic["内容赞叹"] += 1
                        comCount += 1
                        hasSel = True
            if not hasSel:
                for n in seriesList:
                    if n in comment:
                        classDic["关联性"] += 1
                        comCount += 1
                        hasSel = True
            if not hasSel:
                for n in surpriseList:
                    if n in comment:
                        classDic["出乎意料"] += 1
                        comCount += 1
                        hasSel = True
            if not hasSel:
                for n in thanksList:
                    if n in comment:
                        classDic["感谢"] += 1
                        comCount += 1
                        hasSel = True
            if not hasSel:
                for n in positiveList:
                    if n in comment:
                        classDic["主动性"] += 1
                        comCount += 1
                        hasSel = True
            if not hasSel:
                for n in negativeList:
                    if n in comment:
                        classDic["负面情绪"] += 1
                        comCount += 1
                        hasSel = True
            if not hasSel:
                for n in biliList:
                    if n in comment:
                        classDic["B站特色"] += 1
                        comCount += 1
        classDic["其他"] += comSum-comCount
        f.close()
        classDic["其他"] /= comSum
        otherList.append(classDic["其他"])
    num = otherList
    num.sort()
    size = 0.01
    plus = size / 2
    f = open(fout, 'w')
    num1 = 0
    for n in num:
        if n >= 0 and n < plus:
            num1 += 1
    ws = str(num1) + '\n'
    f.write(ws)

    front = size - plus
    later = size + plus
    while later <= 1 - plus:
        num1 = 0
        for n in num:
            if n >= front and n < later:
                num1 += 1
        ws = str(num1) + '\n'
        f.write(ws)
        front += size
        later += size

    num1 = 0
    for n in num:
        if n >= 1 - plus and n <= 1:
            num1 += 1
    ws = str(num1) + '\n'
    f.write(ws)
    f.close()

# “其他”占各档视频比例的分布
def classOther():
    c1, c2, c3, c4 = classByNum()
    other(c1, 'other1.txt')
    other(c2, 'other2.txt')
    other(c3, 'other3.txt')
    other(c4, 'other4.txt')