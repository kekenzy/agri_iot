from agri_app.models import Family

class FamilyDao(Family):
    class Meta:
        proxy = True

    @classmethod
    def add_family(cls, name):
        """
        familyのレコードを作成し、familyオブジェクトを返却する
        :param name
        """
        # familyを登録
        family_obj = Family(name=name)
        family_obj.save()
        return family_obj

    @classmethod
    def get_all_family(cls):
        """
        idを基にfamilyオブジェクトをidを基に取得する
        :param family_id
        return familyオブジェクト
        """
        return cls.objects.all()

    @classmethod
    def get_family_by_id(cls, family_id):
        """
        idを基にfamilyオブジェクトをidを基に取得する
        :param family_id
        return familyオブジェクト
        """
        return cls.objects.get(id=family_id)