from peewee import *

db = SqliteDatabase('my_app.db')


class Base(Model):
    class Meta:
        database = db


class SiteData(Base):
    unique_id = PrimaryKeyField()
    url = CharField()
    data_site = TextField()
    name = CharField()
    date_upload = DateTimeField()


class SiteFiles(Base):
    unique_id = PrimaryKeyField()
    images_path = CharField()
    video_path = CharField()
    key = ForeignKeyField(SiteData, to_field="unique_id", on_delete='CASCADE')
