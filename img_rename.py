
import os, re, random, shutil
import configparser
from sqlite import SqliteDB



# 重命名类
class Rimg:

    def __init__(self):
        self.cur_path = os.getcwd()
        self.cf = configparser.ConfigParser()
        self.cf.read(self.cur_path+"/config.ini", encoding='utf-8')

        # 获取要重命名的字段
        self.fields = self.getConfig('fields')
        self.fields = self.fields.split(',')

        self.cndhost = self.getConfig('cdnhost')
        self.imgprefix = self.getConfig('imgprefix')

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

        if not os.path.exists('article/'):
            os.mkdir('article')

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

        if not os.path.exists(f'article/{fd}/'):
            os.mkdir(f'article/{fd}/')

        for art in cs:
            id = art['ID']
            for field in self.fields:
                if field in art.keys():
                    content = art[field]
                    print(content)
                    pattern = re.compile('src="([^"]*)"')
                    matchObj = pattern.findall(content)

                    for f in matchObj:
                        print('f===>')
                        # print(os.path.exists(f'{self.cur_path}/{f}'))
                        print(os.path.exists(f))
                        if os.path.exists(f):
                            name = os.path.splitext(f)[0]
                            suffix= os.path.splitext(f)[1]
                            newfilename = random.randint(1000000000, 9999999999)
                            # 内容和图片重命名
                            os.rename(f, f"{newfilename}{suffix}")
                            print(f'src="{f}"')
                            # self.cndhost = self.getConfig('cdnhost')
                            # self.imgprefix = self.getConfig('imgprefix')

                            # 移动文件
                            shutil.move(f"{newfilename}{suffix}", f'article/{fd}/')

                            newpath = f'src="https://{self.cndhost}/article/{imgprefix}{newfilename}{suffix}"'

                            art[field] = art[field].replace(f'src="{f}"', newpath)
                            print(f'ID:{id}')

                    if len(matchObj)>0: # 有匹配到图片才更新数据库
                        contmp = art[field].replace("'", "''")
                        self.db.update(table='Content',setstring=f"{field}='{contmp}'", where=f"ID={id}")






if __name__ == '__main__':
    rimg = Rimg()

    rimg.rename()
