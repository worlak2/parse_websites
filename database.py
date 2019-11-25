from peewee import *

db = SqliteDatabase('my_app.db')


class Base(Model):
    class Meta:
        database = db
        database.timeout = 5


class SiteData(Base):
    unique_id = PrimaryKeyField()
    url = CharField()
    title = CharField()
    data_site = TextField()
    date_upload = DateTimeField()


class SiteFiles(Base):
    unique_id = PrimaryKeyField()
    images_path = CharField(null=True)
    key = ForeignKeyField(SiteData, to_field="unique_id", on_delete='CASCADE')


def insert(url: str, title: str, data_site: str, date_upload, images_path):
    db.create_tables([SiteData, SiteFiles])
    site_data = SiteData.create(url=url, title=title, data_site=data_site, date_upload=date_upload)
    SiteFiles(images_path=images_path, key=site_data).save()


def check_data(url):
    db.create_tables([SiteData, SiteFiles])
    query = SiteData.select().where(SiteData.url == str(url))
    if not query.exists():
        return False
    else:
        return True
