
import os, re, random, shutil
import configparser
from sqlite import SqliteDB

# 重命名类
class Rimg:

    def __init__(self):
        # 读取配置文件信息
        self.cur_path = os.getcwd()
        self.cf = configparser.ConfigParser()
        self.cf.read(self.cur_path+"/config.ini", encoding='utf-8')

        # 获取要重命名的字段
        self.fields = self.getConfig('fields')
        self.fields = self.fields.split(',')

        # 获取cdn的域名 和 图片子文件夹名
        self.cndhost = self.getConfig('cdnhost')
        self.imgprefix = self.getConfig('imgprefix')

        # 获得数据库文件并链接数据库
        dbname = self.getDbName()
        self.db = SqliteDB(database=dbname)


    # 获取当前目录下 sqlite 数据库文件名称
    def getDbName(self):
        for file in os.listdir(self.cur_path):
            if file[-4:] == '.db3':
                return file

        return 'SpiderResult.db3'

    # 获取配置文件中的键值
    def getConfig(self, key='fields'):
        return self.cf.get("default", key)

    # 重命名
    def rename(self):

        # 获取数据库中的数据
        cs = self.db.getAll(table="Content", where="1")

        # 默认将图片收在article目录下
        if not os.path.exists('article/'):
            os.mkdir('article')
        # 如果子文件夹是随机的
        if self.imgprefix == 'random':
            fd = random.randint(1000000, 9999999)
            imgprefix = f'{fd}/'
        else:
            if self.imgprefix == '':
                fd = ''
                imgprefix = ''
            else:
                fd = self.imgprefix
                imgprefix = f'{fd}/'
        # 创建子文件夹
        if not os.path.exists(f'article/{fd}/'):
            os.mkdir(f'article/{fd}/')

        for art in cs:
            id = art['ID']
            for field in self.fields:
                # 只有字段存在才处理
                if field in art.keys():
                    content = art[field]
                    # 用正则筛选出所有的图片, 存入match_arr
                    pattern = re.compile('src="([^"]*)"')
                    match_arr = pattern.findall(content)

                    for f in match_arr:
                        # 图片文件存在的时候
                        if os.path.exists(f):
                            # 获得文件名 和 文件后缀
                            name = os.path.splitext(f)[0]
                            suffix= os.path.splitext(f)[1]
                            newfilename = random.randint(1000000000, 9999999999)

                            # 内容和图片重命名
                            os.rename(f, f"{newfilename}{suffix}")

                            # 移动文件
                            shutil.move(f"{newfilename}{suffix}", f'article/{fd}/')

                            newpath = f'src="https://{self.cndhost}/article/{imgprefix}{newfilename}{suffix}"'
                            art[field] = art[field].replace(f'src="{f}"', newpath)

                    if len(match_arr)>0: # 有匹配到图片才更新数据库
                        contmp = art[field].replace("'", "''") # 入库时需处理单引号
                        self.db.update(table='Content',setstring=f"{field}='{contmp}'", where=f"ID={id}")






if __name__ == '__main__':
    rimg = Rimg()

    # 图片批量重命名
    rimg.rename()
