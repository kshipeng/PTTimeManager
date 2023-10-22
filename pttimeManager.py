
import requests, os, brotli, time, datetime
from bs4 import BeautifulSoup

def log(strs, file=None):
    if file: 
        print(strs, file=file);
        index1 = strs.find('免费')
        index1 = strs.find('类型:') if index1 != -1 else -1
        index2 = strs.find('; 做种') if index1 != -1 else -1
        strs = strs[:index1+3] + '\033[32m' + strs[index1+3:index2] + '\033[0m' + strs[index2:] if index1 != -1 and index2 != -1 else strs
        print(strs)
    else: print(strs)

class PTTimeRequest:
    """构造请求"""
    page = None
    url = None
    referer = None
    areaDic = {'1':'综合','2':'9KG'}
    typesDic = {'0':'全部','1':'普通','2':'免费','3':'2x上传','4':'50%免费','5':'2x上传&50%免费','6':'30%免费','7':'0流量'}
    def __init__(self, cookie, ua, page, url, referer, header, area, types):
        self.cookie = cookie
        self.ua = ua
        self.page = page
        self.url = url
        self.referer = referer
        self.header = header
        self.area = area
        self.types = types

    def getArea(self):
        return PTTimeRequest.areaDic[self.area]


    def getType(self):
        return PTTimeRequest.typesDic[self.types]

    @staticmethod
    def create(cookie=None, ua=None, page=0, url=None, referer=None, area=None, types=None):
        page = int(page)
        cookie = cookie if cookie else {print('缺少cookie'), exit()}
        ua = ua if ua else {print('缺少User-Agent'), exit()}
        referer = referer if referer else url
        url = url if url else {print('缺少URL'), exit()}
        page = PTTimeRequest.page if not page and page != 0 else page
        PTTimeRequest.page = page
        url = f"{url}{page}" if url else f"{PTTimeRequest.url}{page}"
        referer = f"{referer}{page+1}" if referer else f"{PTTimeRequest.referer}{page+1}"
        PTTimeRequest.url = url
        PTTimeRequest.referer = referer
        header = {
            'Accept' : r'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Encoding' : r'gzip, deflate',
            'Cookie' : cookie,
            'Connection' : r'keep-alive',
            'Sec-Fetch-Mode' : r'navigate',
            'Host' : r'www.pttime.org',
            'User-Agent' : ua,
            'Sec-Fetch-Site' : r'same-origin',
            'Referer' : referer,
            'Sec-Fetch-Dest' : r'document',
            'Accept-Language' : r'zh-CN,zh-Hans;q=0.9'
        }
        return PTTimeRequest(cookie, ua, page, url, referer, header, area, types)

    def get_html(self):
        session = requests.Session()
        session.timeout = 60
        response = session.get(self.url, headers=self.header)
        if response.status_code == 200:
            key = 'Content-Encoding'
            if(key in response.headers and response.headers['Content-Encoding'] == 'br'):
                return response.content
            return response.text
        return None

class PTTimeTorrents:
    """获取内容"""
    def __init__(self):
        ...
        
    @staticmethod
    def getLinks(request: PTTimeRequest, logPath=None):
        logFile = None
        if logPath and logPath.isspace() != True: logFile = open(logPath, 'a', encoding='utf-8')

        html = request.get_html()

        if not html: 
            log("请求数据失败", file=logFile)
            exit()
        soup = BeautifulSoup(html, 'lxml')
        table = soup.select('table.torrents#torrenttable > tr')[1:]
        linkArr = []
        for tr_tag in table:
            seeders = tr_tag.select("a[href$='seeders']") #做种
            
            if len(seeders) :

                td_tagArr = [x for x in tr_tag.contents if x != '\n']

                title = tr_tag.select("a[class='torrentname_title']")

                subTitle = title[0].parent.select("font[title]")
                subTitle = subTitle[0].text if len(subTitle) else ''

                title = title[0].get('title', 'No title attribute') if len(title) else ''
                log(f"标题: {title}", file=logFile)
                log(f"副标题: {subTitle}", file=logFile)

                freeType = tr_tag.select("font[class^='promotion']") #类型
    
                freeTime = freeType[0].parent.select("span[title]") if len(freeType) else '' #免费时间
                freeTime = freeTime[0].text if len(freeTime) else ''

                freeType = freeType[0].text if len(freeType) else '普通'

                leechers = tr_tag.select("a[href$='leechers']") #正在下载
                leechers = leechers[0].string if len(leechers) else '0'

                size = td_tagArr[5].text if len(td_tagArr) > 5 else ''

                log(f"种子id: {tr_tag['data']}; 类型: {freeType} {freeTime}; 做种: {seeders[0].string}; 正在下载: {leechers}; 大小: {size}", file=logFile)
                
                down_url = tr_tag.select("a[href^='download.php?id=']")[0]['href']
                down_url = f"https://www.pttime.org/{down_url}"
                log(down_url, file=logFile)
                linkArr.append(down_url)
                log("*".center(50,"*"), file=logFile)
        log(f"本次获取（{len(linkArr)}）个; {request.getArea()}, {request.getType()}, 第{request.page}页", file=logFile)
        log("#".center(50,'#'), file=logFile)
        if logPath and logPath.isspace() != True: logFile.close()     
        return linkArr

    @staticmethod
    def write(arr, filePath):
        if filePath and filePath.isspace() != True:
            with open(filePath, 'a', encoding='utf-8') as file:
                file.writelines([line+'\n' for line in arr])

def printInfo(area, types, page, logPath, torrentsPath):
    logFile = None
    time_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    if not logPath.isspace() and os.path.isabs(logPath) == False:
        logPath = os.getcwd() + '/' + os.path.basename(logPath)
    if logPath and logPath.isspace() != True: logFile = open(logPath, 'a', encoding='utf-8')
    if not torrentsPath.isspace() and os.path.isabs(torrentsPath) == False:
        torrentsPath = os.getcwd() + '/' + os.path.basename(torrentsPath)
    log(" 开始 ".center(50,'#'), file=logFile)
    log(f" {time_str} ".center(50, '='), file=logFile)
    log(f"区域: {PTTimeRequest.areaDic[area]}, 类型: {PTTimeRequest.typesDic[types]}, page: {page}", file=logFile)
    log(f"日志文件路径: {logPath}", file=logFile) if logPath and logPath.isspace() != True else print('日志记录关闭')
    log(f"种子文件路径: {torrentsPath}", file=logFile) if torrentsPath and torrentsPath.isspace() != True else print('种子记录关闭')
    log("#".center(50, '#'), file=logFile)
    if logPath and logPath.isspace() != True: logFile.close()

class Manager:
    def __init__(self):
        ...
        
    @staticmethod
    def getTorrents(cookie, UA, page=0, free=0, logPath=None, torrentsPath=None):
        url = f"https://www.pttime.org/torrents.php?inclbookmarked=0&incldead=1&spstate={free}&sort=5&type=desc&page="
        trRquset = PTTimeRequest.create(cookie, UA, page=page, url=url, area='1', types=free)
        trArr = PTTimeTorrents.getLinks(trRquset, logPath)
        PTTimeTorrents.write(trArr, torrentsPath)

    @staticmethod
    def getTorrentsPorn(cookie, UA, page=0, free=0, logPath=None, torrentsPath=None):
        url = f"https://www.pttime.org/adults.php?inclbookmarked=0&incldead=1&spstate={free}&sort=5&type=desc&page="
        trRquset = PTTimeRequest.create(cookie, UA, page=page, url=url, area='2', types=free)
        trArr = PTTimeTorrents.getLinks(trRquset, logPath)
        PTTimeTorrents.write(trArr, torrentsPath)

if __name__ == "__main__":

    logPath_ = './pttimeLogs.txt' #日志记录文件路径；None则不记录
    torrentsPath_ = './pttimeTorrents.text' #种子链接记录文件；None

    #设置你的cookie和UA（User-Agent）。把xxx替换成你自己的
    cookie = r'xxx'
    UA = r'xxx'
    
    if cookie == 'xxx' or UA == 'xxx': {print('须设置cookie和UA'), exit()}
    print("\033[31m***不获取做种数为0的数据***\033[0m")
    type_str = ''.join([f'{key}=>{value}; ' for key, value in PTTimeRequest.typesDic.items()])[:-1]

    getArea = input('获取哪个分区？1=>综合区；2=>9KG区:')
    getType = input(f"获取哪种类型？{type_str}:")
    getPage = input('获取第几页(0开始)？:')

    if getArea == '1':
        printInfo(getArea, getType, getPage, logPath_, torrentsPath_)
        Manager.getTorrents(cookie, UA, getPage, getType, logPath_, torrentsPath_)
    elif getArea == '2':
        printInfo(getArea, getType, getPage, logPath_, torrentsPath_)
        Manager.getTorrentsPorn(cookie, UA, getPage, getType, logPath_, torrentsPath_)
    else:
        print('输入错误。退出')
    
   
    
    #打开文件
    #os.system(f"open {logPath}")
    #os.system(f"open {torrentsPath}")
    





