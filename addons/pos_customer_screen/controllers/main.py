# -*- coding: utf-8 -*-
import logging
import simplejson
import os
import openerp
import re
import time
import datetime
import random
import werkzeug.utils
import sys
import jinja2
import hashlib
from openerp import http
from openerp.http import request
import json
_logger = logging.getLogger(__name__)
from openerp import SUPERUSER_ID
from openerp.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT
class PosMirrorController(http.Controller):

    @http.route('/pos/mirror_data', type='http', auth='user',website=True)
    def mirror_data(self,**k):
        cr, uid, context, session = request.cr, request.uid, request.context, request.session
        mirror_img = request.registry['mirror.image.order']
        notif_obj = request.registry['screen.notification.msg']
        notification_id = notif_obj.search(cr,uid,[('create_note','=',uid)])
        if notification_id:
            notif_obj.write(cr,uid,notification_id,{'msg':True})
        session_name = []
        
        if session.has_key('session_link'):
            session_name = session['session_link']
            try:
                product_name = mirror_img.read(cr, uid,session_name,['order_line','currency','payment_line'])
                return json.dumps({'name':eval(product_name['order_line']),'currency':product_name['currency'],'payment_line':eval(product_name['payment_line'])})
            except:
                return request.redirect("/pos/latest_mirror_url")
        return request.redirect("/pos/latest_mirror_url")

    # def longPooling(self, cr, uid, session_name,database_name):
    #     registry = openerp.registry(database_name)
    #     timeout_ago = datetime.datetime.utcnow()-datetime.timedelta(seconds=TIMEOUT)
    #     notif_obj = request.registry['screen.notification.msg']
    #     notification_id = notif_obj.search(cr,uid,[('create_note','=',uid)])
    #     cr.execute("SELECT ac_token,write_date FROM mirror_image_order where id = %s" %(session_name))
    #     result = cr.dictfetchall()
    #     check_date = result[0]['write_date'] > timeout_ago.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
    #     while not check_date:
    #         time.sleep(2)
    #         notif_obj.write(cr,uid,notification_id,{'msg':True})
    #         with registry.cursor() as cr:
    #             timeout_ago = datetime.datetime.utcnow()-datetime.timedelta(seconds=TIMEOUT)
    #             cr.execute("SELECT ac_token,write_date FROM mirror_image_order where id = %s"%(session_name))
    #             result = cr.dictfetchall()
    #             check_date = result[0]['write_date'] > timeout_ago.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
    #     if check_date:
    #         notif_obj.write(cr,uid,notification_id,{'msg':True})

    @http.route('/pos/latest_mirror_url', type='http', auth='user',website=True)
    def mirror(self, debug=False, **k):
        cr, uid, context, session = request.cr, request.uid, request.context, request.session
        mirror_img = request.registry['mirror.image.order']
        pos_config = request.registry['pos.config']
        ad_image = request.registry['advertisement.images']
        # website_obj = request.registry['website']
        mirror_img_ids = mirror_img.search(cr, SUPERUSER_ID, [['session_name', '=', str(uid)]], context=context)
        if mirror_img_ids:
            session_id = mirror_img.read(cr, SUPERUSER_ID,mirror_img_ids[0],['session_id'])['session_id']
            image_data = []
            first_img = {}
            if session_id:
                pos_config_data = pos_config.read(cr, SUPERUSER_ID, session_id, ['advertisement_image','marquee_text','marque_color','marque_bg_color','marque_font_size','mute_video_sound','ac_width','ac_height'], context)
                image_ids = pos_config_data['advertisement_image']
                # image_duration = pos_config_data['image_duration']*1000
                if image_ids:
                    top_image_id = image_ids[0]
                    del image_ids[0]
                    image_obj = ad_image.browse(cr, uid, top_image_id, context)
                    first_img['file_type'] = image_obj.file_type
                    first_img['is_youtube_url']=image_obj.is_youtube_url
                    if image_obj.file_type == "image":
                        if(image_obj.image_type == 'url'):
                            first_img['img_link'] = image_obj.url
                        else:
                            first_img['img_link'] = self.image_url(cr, uid, image_obj, 'ad_image')

                    if image_obj.file_type == "video":
                        if(image_obj.video_type == 'url'):
                            first_img['img_link'] = image_obj.video_url
                            url_value = (image_obj.video_url).split('/')
                            name_of_url = url_value[len(url_value)-1]
                            first_img['name_of_url'] = name_of_url
                        else:
                            args = {
                                'id': image_obj.id,
                                'model': image_obj._name,
                                'filename_field': 'ad_video_fname',
                                'field': 'ad_video',
                                }

                            first_img['img_link'] = '/web/content?%s' % werkzeug.url_encode(args)

                    first_img['name'] = image_obj.name
                    first_img['description'] = image_obj.description
                    first_img['image_duration']= image_obj.image_duration*1000
                    for image_id in image_ids:
                        temp_file_dict = {}
                        ad_obj = ad_image.browse(cr,uid,image_id,context)
                        temp_file_dict['file_type'] = ad_obj.file_type
                        temp_file_dict['is_youtube_url']=ad_obj.is_youtube_url
                        if ad_obj.file_type == "image":
                            if(ad_obj.image_type == 'url'):
                                temp_file_dict['img_link'] = ad_obj.url
                            else:
                                temp_file_dict['img_link'] = self.image_url(cr, uid, ad_obj, 'ad_image')

                        if ad_obj.file_type == "video":
                            if(ad_obj.video_type == 'url'):
                                temp_file_dict['img_link'] = ad_obj.video_url
                                url_value = (ad_obj.video_url).split('/')
                                name_of_url = url_value[len(url_value)-1]
                                temp_file_dict['name_of_url'] = name_of_url
                            else:
                                args = {
                                    'id': ad_obj.id,
                                    'model': ad_obj._name,
                                    'filename_field': 'ad_video_fname',
                                    'field': 'ad_video',
                                    }
                                temp_file_dict['img_link'] = '/web/content?%s' % werkzeug.url_encode(args)


                        temp_file_dict['name'] = ad_obj.name
                        temp_file_dict['description'] = ad_obj.description
                        temp_file_dict['image_duration'] = ad_obj.image_duration*1000
                        image_data.append(temp_file_dict)

            session['session_link'] = mirror_img_ids[0]
            vals = {
                        "first_img":first_img,"image_link":image_data,
                        "marquee_text": pos_config_data['marquee_text'],
                        "marque_color":pos_config_data['marque_color'],
                        "marque_bg_color":pos_config_data['marque_bg_color'],
                        "marque_font_size":"font-size:"+str(pos_config_data['marque_font_size'])+"px",
                        "ac_mute_video":pos_config_data['mute_video_sound'],
                        "ac_width":pos_config_data['ac_width'],
                        "ac_height":pos_config_data['ac_height'],
                        "ac_height_style":"height:"+str(pos_config_data['ac_height'])+"px",
                    }
            html = request.registry.get('ir.ui.view').render(cr, SUPERUSER_ID,'pos_customer_screen.index1',vals)
            return html
        else:
            return "<h1>Link is Not valid.....</h1>"

    def image_url(self, cr, uid, record, field, size=None, context=None):
        """Returns a local url that points to the image field of a given browse record."""
        sudo_record = record.sudo()
        sha = hashlib.sha1(getattr(sudo_record, '__last_update')).hexdigest()[0:7]
        size = '' if size is None else '/%s' % size
        return '/web/image/%s/%s/%s%s?unique=%s' % (record._name, record.id, field, size, sha)



