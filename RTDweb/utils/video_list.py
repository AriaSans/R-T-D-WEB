from django.utils.safestring import mark_safe


class VideoList(object):
    def __init__(self, request, queryset):
        self.request = request
        self.queryset = queryset

        self.img_count = self.queryset.count()
        row_count, div = divmod(int(self.img_count), 4)
        if div:
            row_count += 1
        self.row_count = row_count
        self.div = div

    def html(self):
        self.coding_list = []
        for_num = 0
        start_html = '<div class="row mb-2"><div class="col"><div class="card-group" style="display: flex;">'
        end_html = '</div></div></div>'
        for row in range(0, self.row_count):
            self.coding_list.append(start_html)
            for col in range(0, 4):
                if not for_num < self.img_count:
                    col_hidden = '<div class="card" style="flex: 1; visibility: hidden;"></div>'
                    self.coding_list.append(col_hidden)
                else:
                    img_obj = self.queryset[for_num]
                    img_id = img_obj.id
                    img_path = '/media/' + img_obj.cover_img_path
                    video_path = '/media/' + img_obj.img_path

                    col_card_html = '<div class="card" style="flex: 1;">'
                    col_img_html = (
                        '<a class="a_img" href="{}"><img src="{}"class="card-img-top img-fluid edit_opacity"style="object-fit: cover;'
                        ' height: 200px;" alt="..." id="cover_img_{}"></a>').format(video_path, img_path, img_id)
                    if img_obj.is_detect == 0:
                        small_color = 'orange'
                        small_info = '未监测'
                    else:
                        small_color = 'green'
                        small_info = '已监测'
                    col_body_html = (
                        '<div class="card-body" style="position: relative">'
                        '<p class="card-text text-center edit_opacity">{}</p>'
                        '<p class="card-text text-center" '
                        'style="position: absolute; bottom: 3px;left: 41%;margin-bottom: 0">'
                        '<small class="edit_opacity" style="color: {}">{}</small>'
                        '</p><input class="form-check-input video_radio" type="radio" '
                        'name="inlineRadioOptions" id="inlineRadio{}" value="option{}" data-video-id="{}">'
                        '<input type="checkbox" class="form-check-input img_checkbox" data-img-id="{}">'
                        '</div></div>').format(img_obj.name, small_color, small_info, img_obj.id, img_obj.id, img_obj.id, img_obj.id)
                    self.coding_list.append(col_card_html)
                    self.coding_list.append(col_img_html)
                    self.coding_list.append(col_body_html)
                for_num += 1

            self.coding_list.append(end_html)

        img_list_code = mark_safe("".join(self.coding_list))
        return img_list_code
