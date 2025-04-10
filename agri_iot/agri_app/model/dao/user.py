from agri_app.models import User

class UserDao(User):
    class Meta:
        proxy = True

    @classmethod
    def add_user(cls, first_name, family, email=None):
        """
        userのレコードを作成し、userオブジェクトを返却する
        :param first_name
        :param last_name
        :param email
        return userオブジェクト
        """
        # userを登録
        print('add_user')
        user_obj = User(username=first_name, family=family, email=email)
        user_obj.save()
        print('save')
        return user_obj

    @classmethod
    def get_all_user(cls):
        """
        idを基にuserオブジェクトをidを基に取得する
        :param user_id
        return userオブジェクト
        """
        return cls.objects.all()

    @classmethod
    def get_user_by_id(cls, user_id):
        """
        idを基にuserオブジェクトをidを基に取得する
        :param user_id
        return userオブジェクト
        """
        return cls.objects.get(id=user_id)

    @classmethod
    def get_user_by_family(cls, family_id):
        """
        idを基にuserオブジェクトをidを基に取得する
        :param user_id
        return userオブジェクト
        """
        print(cls.objects.filter(family__id=family_id).query)

        return cls.objects.filter(family__id=family_id).values()