#!/usr/bin/env python
# encoding: utf-8

#  pip3 install exifread
import exifread
from position_utils import *
import requests
import json
from PIL import Image
# pip3 install piexif
import piexif
from gps_utils import *


class PIC_INFO(object):


    def __init__(self, image_path):

        # 照片路径
        self.img_path = image_path
        # 高德开放平台申请到的api key
        self.api_key = "xxxxxxxxx"
        # 请求链接：逆地理编码（经纬度转为地址）
        self.url_get_position = 'https://restapi.amap.com/v3/geocode/regeo?key={}&location={}'
        # 请求链接：地理编码（地址转为经纬度）
        self.url_geo = 'https://restapi.amap.com/v3/geocode/geo'

    def get_pic_info(self):

        # 读取照片的基本属性
        coordinate = self.__get_image_ability()

        print(f'照片的经度、纬度是: {coordinate}')

        if not coordinate:
            return

        # 根据经度和纬度，获取到详细地址
        address = self.__get_address(coordinate)

        print(f'照片拍摄位置在：{address}')

    # 根据经纬度坐标值得到详细地址
    def __get_address(self, location):

        resp = requests.get(self.url_get_position.format(self.api_key, location))

        location_data = json.loads(resp.text)

        address = location_data.get('regeocode').get('formatted_address')

        return address

    def __format_lati_long_data(self, data):
        """
        对经度和纬度数据做处理，保留6位小数
        :param data: 原始经度和纬度值
        :return:
        """
        # 删除左右括号和空格
        data_list_tmp = str(data).replace('[', '').replace(']', '').split(',')
        data_list = [data.strip() for data in data_list_tmp]

        # 替换秒的值
        data_tmp = data_list[-1].split('/')

        # 秒的值
        data_sec = int(data_tmp[0]) / int(data_tmp[1]) / 3600

        # 替换分的值
        data_tmp = data_list[-2]

        # 分的值
        data_minute = int(data_tmp) / 60

        # 度的值
        data_degree = int(data_list[0])

        # 由于高德API只能识别到小数点后的6位
        # 需要转换为浮点数，并保留为6位小数
        result = "%.6f" % (data_degree + data_minute + data_sec)
        return float(result)

    # 获取照片的属性值，包含：经纬度、拍摄时间等
    def __get_image_ability(self):

        # 利用exifread库，读取照片的基本属性
        img_exif = exifread.process_file(open(self.img_path, 'rb'))

        # 能够读取到属性
        if img_exif:

            # 打印照片的关键一些信息
            print('拍摄时间：', img_exif['EXIF DateTimeOriginal'])
            print('相机制造商：', img_exif['Image Make'])
            print('相机型号：', img_exif['Image Model'])
            # print('照片尺寸：', img_exif['EXIF ExifImageWidth'],
            #                   img_exif['EXIF ExifImageLength'])

            # 纬度数
            latitude_gps = img_exif['GPS GPSLatitude']
            # 经度数
            longitude_gps = img_exif['GPS GPSLongitude']

            # 纬度、经度有效
            if latitude_gps and longitude_gps :

                # 对纬度、经度值原始值作进一步的处理
                latitude = self.__format_lati_long_data(latitude_gps)
                longitude = self.__format_lati_long_data(longitude_gps)

                # print(f'{longitude},{latitude}')

                # 注意：由于gps获取的坐标在国内高德等主流地图上逆编码不够精确，这里需要转换为火星坐标系
                location = wgs84togcj02(longitude, latitude)

                return f'{location[0]},{location[1]}'

            else:
                print(f'获取的图片数据属性不完整')
                return ''
        else:
            print('抱歉，图片不是原图，没法获取到图片属性。')
            return ''

    # 通过地理位置到拿到经纬度
    def get_location_by_address(self, city, address):
        params = {
            'key': self.api_key,
            'city': city,
            'address': address,
            'sig': "not need"
        }

        resp = json.loads(requests.get(url=self.url_geo, params=params).text)

        # 获取坐标地址
        if resp and len(resp.get('geocodes')) >= 1 and resp.get('geocodes')[0].get('location'):
            location = resp.get('geocodes')[0].get('location')
            gps_data = location.split(',')

            # 得到经度和纬度
            gps_long = float(gps_data[0])
            gps_lati = float(gps_data[1])

            return gps_long, gps_lati
        else:
            print('api解析地址出错，请检查ak！')
            return None

    def write_image(self, image_path, gps_long, gps_lati):
        # 读取图片
        img = Image.open(image_path)

        try:
            exif_dict = piexif.load(img.info['exif'])
        except:
            print('加载文件地理位置异常！')
            return

        # 修改地理位置
        # GPS GPSLatitudeRef:N
        # GPS GPSLatitude:[22, 32, 189/20]
        # GPS GPSLongitudeRef:E
        # GPS GPSLongitude:[114, 1, 689/20]
        exif_dict['GPS'][2] = gps_to_dms(gps_lati)
        exif_dict['GPS'][4] = gps_to_dms(gps_long)

        exif_bytes = piexif.dump(exif_dict)

        # 写入到新的图片中去
        img.save(image_path, 'jpeg', exif=exif_bytes)

    def modify_pic_info(self):
        # 输入地址（市+目的地，例如：武汉 武汉大学）
        city = input('请输入定位城市(例如：武汉)：')
        address = input('请输入具体的定位地址(例如：武汉大学)：')

        if address:
            # 通过地址拿到坐标地址
            location = self.get_location_by_address(city, address)
            if location:
                # 4、修改图片属性,写入经度和纬度
                self.write_image(self.img_path, location[0], location[1])
                print('修改图片地理成功！')
        else:
            print('请先输入具体地址！')
        return

if __name__ == '__main__':
    # 输入照片路径，注意要求是原图
    pic_info = PIC_INFO('./test.jpg')

    # 分析照片，获取照片相关信息并打印
    pic_info.get_pic_info()

    # 修改照片位置信息
    pic_info.modify_pic_info()
