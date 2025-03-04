import mongoengine

from StockManager_Backendcode.settings import db


#创建类
#user包含的属性
# userid(用户id)，username(用户名),userpassword(用户密码)，userphone(用户手机号)，useremail(用户邮箱)


class User(mongoengine.Document):
    _id=mongoengine.StringField(required=True)#id
    userid = mongoengine.StringField(required=True)  # 用户id
    username = mongoengine.StringField(required=True)  # (用户名)
    nick_name = mongoengine.StringField(required=True)  # (真实名)
    password= mongoengine.StringField(required=True)  # (用户密码)
    create_time= mongoengine.StringField(required=True)  # (创建时间)
    update_time= mongoengine.StringField(required=True)  # (更新时间)

    collection = db['User']  # 替换为你的集合名

