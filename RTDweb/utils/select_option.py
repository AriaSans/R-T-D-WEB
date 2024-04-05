from django.utils.safestring import mark_safe
from RTDweb import models

# 输出选择框内容
class SelectOption(object):
    def __init__(self, request, folder_type, to_user_id):
        self.set_obj_list = models.DetectSet.objects.filter(type=folder_type, to_user_id=to_user_id)
        self.option_list = []
        if not self.set_obj_list:
            coding = '<option selected>空</option>'
            self.option_list.append(coding)

    def html(self):
        if self.set_obj_list:
            for obj in self.set_obj_list:
                coding = "<option value='{}'>{}</option>".format(obj.id, obj.folder_name)
                self.option_list.append(coding)
        option_code = mark_safe("".join(self.option_list))
        return option_code
