import math
import os
from functools import reduce
import pandas as pd

from model.Factory import Factory
from model.Order import Order
from model.Routes import Routes
from model.Vehicle import Vehicle


class Read:
    def __init__(self, file_path):
        self.file_path = file_path

    @classmethod
    def all(cls, path: str) -> list[str]:
        """
        读取path目录下的所有文件名及目录名
        :param path:
        :return:所有绝对路径构成的列表
        """
        try:
            # 获取文件夹中的所有文件名
            file_names = os.listdir(path)
            # 过滤出文件名，排除目录
            files = [path + '\\' + f for f in file_names]
            return files

        except FileNotFoundError:
            print(f"Error: The directory '{path}' does not exist.")
        except Exception as e:
            print(f"An error occurred: {e}")

    @classmethod
    def folder(cls, path: str) -> list[str]:
        """
        读取path目录下的所有目录名
        :param path:
        :return:所有目录的绝对路径构成的列表
        """
        try:
            # 获取文件夹中的所有文件名
            file_names = os.listdir(path)
            # 过滤出文件名，排除目录
            files = [path + '\\' + f for f in file_names if os.path.isdir(os.path.join(path, f))]
            return files

        except FileNotFoundError:
            print(f"Error: The directory '{path}' does not exist.")
        except Exception as e:
            print(f"An error occurred: {e}")

    @classmethod
    def files(cls, path: str) -> list[str]:
        """
        读取path目录下的所有文件名
        :param path:
        :return:所有文件的绝对路径构成的列表
        """
        try:
            # 获取文件夹中的所有文件名
            file_names = os.listdir(path)
            # 过滤出文件名，排除目录
            files = [path + '\\' + f for f in file_names if os.path.isfile(os.path.join(path, f))]
            return files

        except FileNotFoundError:
            print(f"Error: The path '{path}' does not exist.")
        except Exception as e:
            print(f"An error occurred: {e}")

    @classmethod
    def order_to_slices(cls, path: str,
                        vehicle_capacity: int = 15,
                        slice_size: int = 0) -> dict:
        """
        读取path路径下的csv文件, 将其按照时间顺序分割成多个slice, 如果单个订单超载, 则拆分订单至最小单位
        :param vehicle_capacity:
        :param path:
        :param slice_size: 每个slice的大小, 默认为0, 表示按 load_time 的最大公约数切分
        :return: 一个字典, key为切分的时间, value为该时间段内的订单列表
        """
        df = pd.read_csv(path)
        # 将时间转换为秒数
        df['creation_time'] = pd.to_datetime(df['creation_time'], format='%H:%M:%S')
        df['creation_time'] = df['creation_time'].apply(lambda x: x.hour * 3600 + x.minute * 60 + x.second)
        df['committed_completion_time'] = pd.to_datetime(df['committed_completion_time'], format='%H:%M:%S')
        df['committed_completion_time'] = df['committed_completion_time'].apply(lambda x: x.hour * 3600 + x.minute * 60 + x.second)
        # 按 creation_time 排序
        df = df.sort_values(by='creation_time')

        # slice_size 默认为 load_time 的最大公约数
        if not slice_size:
            load_times = df['load_time']
            slice_size = reduce(math.gcd, load_times)
        # print(f"slice_size: {slice_size}")

        # 按照 slice_size 分割
        slice_dict = {}
        slice_end = 0
        for row in df.itertuples():
            # 如果单个订单已经超载, 则拆分订单
            if row.demand > vehicle_capacity:
                order_list = []
                # 按 q_standard, q_small, q_box 拆分订单
                for i in range(row.q_standard):
                    order = Order(row.order_id, row.q_standard, 0, 0, row.q_standard * 1,
                                  row.creation_time, row.committed_completion_time, row.load_time, row.unload_time,
                                  row.pickup_id, row.delivery_id)
                    order_list.append(order)
                for i in range(row.q_small):
                    order = Order(row.order_id, 0, row.q_small, 0, row.q_small * 0.5,
                                  row.creation_time, row.committed_completion_time, row.load_time, row.unload_time,
                                  row.pickup_id, row.delivery_id)
                    order_list.append(order)
                for i in range(row.q_box):
                    order = Order(row.order_id, 0, 0, row.q_box, row.q_box * 0.25,
                                  row.creation_time, row.committed_completion_time, row.load_time, row.unload_time,
                                  row.pickup_id, row.delivery_id)
                    order_list.append(order)

            # 如果单个订单未超载, 生成单个订单
            else:
                order = Order(row.order_id, row.q_standard, row.q_small, row.q_box, row.demand,
                              row.creation_time, row.committed_completion_time, row.load_time, row.unload_time,
                              row.pickup_id, row.delivery_id)
                order_list = [order]

            # 按照订单的创建时间分割订单
            for order in order_list:
                # new slice
                if order.creation_time > slice_end:
                    slice_end = order.creation_time - order.creation_time % slice_size
                    slice_dict[slice_end] = []
                slice_dict[slice_end].append(order)
        return slice_dict

    @classmethod
    def route(cls, path: str) -> Routes:
        """
        读取path路径下的csv文件, 读取路线信息
        :param path:
        :return: Routes类实例
        """
        df = pd.read_csv(path)

        # Create pivot tables
        d_matrix = df.pivot(index='start_factory_id', columns='end_factory_id', values='distance')
        t_matrix = df.pivot(index='start_factory_id', columns='end_factory_id', values='time')
        return Routes(d_matrix, t_matrix)

    @classmethod
    def vehicle(cls, path: str) -> list[Vehicle]:
        """
        读取path路径下的csv文件, 读取车辆信息
        :param path:
        :return: Vehicle类实例构成的list
        """
        vehicle_list = []
        df = pd.read_csv(path)
        for row in df.itertuples():
            vehicle_list.append(Vehicle(row.car_num, row.capacity, row.operation_time, row.gps_id))
        return vehicle_list

    @classmethod
    def factory(cls, path: str) -> list[Factory]:
        """
        读取path路径下的csv文件, 读取工厂信息
        :param path:
        :return:
        """
        factory_list = []
        df = pd.read_csv(path)
        for row in df.itertuples():
            factory_list.append(Factory(row.factory_id, row.longitude, row.latitude, row.port_num))
        return factory_list



if __name__ == '__main__':
    # test all()
    # file_list = Read.all("D:\\Project\\ICAPS-2021\\data\\benchmark")
    # print(file_list[0])
    # for path in file_list: print(path)
    # print(Read.all(file_list[1]))

    # test files()
    # for folder in Read.files("D:\\Project\\ICAPS-2021\\data\\benchmark"):
    #     print(Read.files(folder))

    # test order_to_slices()
    slices = Read.order_to_slices("D:\\Project\\ICAPS-2021\\data\\test\\50_1.csv", 1000)
    for k, v in slices.items(): print(k); print(i.creation_time for i in v)
    print(slices[70000][0].creation_time)
    print(slices[71000][0].creation_time)
    print(slices[72000][0].creation_time)

    # test route()
    # routes = Read.route("D:\\Project\\ICAPS-2021\\data\\test\\route_info.csv")
    # start_factory = '9829a9e1f6874f28b33b57a7a42bb49f'
    # end_factory = 'c1e1e4250f63479ca9261967f84b6719'
    # distance = routes.distance_matrix[start_factory][end_factory]
    # distance = routes.distance_matrix.loc[start_factory, end_factory]
    # print(f"Distance from {start_factory} to {end_factory}: {distance}")
    # time = routes.time_matrix.loc[start_factory, end_factory]
    # print(f"Time from {start_factory} to {end_factory}: {time}")

    # test vehicle()
    # vehicles = Read.vehicle("D:\\Project\\ICAPS-2021\\data\\test\\vehicle_info_5.csv")
    # print(vehicles[0].car_num)

    # test factory()
    pass