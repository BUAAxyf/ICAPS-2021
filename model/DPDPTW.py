import copy

from algorithm.GreedyAlgorithm import GreedyAlgorithm
from algorithm.SolomonInsertionAlgorithm import SolomonInsertAlgorithm
from model import Routes
from reader.Read import Read


class DPDPTW:
    """
    A class to find the local optimal solution of a DPDPTW model.\n
    Steps:
        - Instantiate a DPDPTW object.
        - \*Call read_data() function read the route, vehicle and factory files.
        - Call add_order() or add_order_list() function to add a list of orders to the order list.
        - Call distribute_orders() function to initialize the solution of the DPDPTW model.
        - Call update() function to update the DPDPTW model to the next time step.
        - Repeat steps 3, 4 and 5 until there is no more order to be served.
        - Call output() function to output the solution.
    """
    def __init__(self, route: Routes = None,
                 vehicle_dict: dict = None,
                 factory_dict: dict = None,
                 order_list: list = None):
        self.route: Routes = route
        # self.total_cost = 0
        self.now = 0
        if vehicle_dict is None: self.vehicle_dict = {} # car_num: Vehicle
        else: self.vehicle_dict = vehicle_dict

        if factory_dict is None: self.factory_dict = {} # factory_id: Factory
        else: self.factory_dict = factory_dict

        if order_list is None: self.order_list = [] # list of Order to be distributed
        else: self.order_list = order_list

    def read_route(self, route_file: str) -> Routes:
        """
        Read the route file and initialize the DPDPTW model
        :param route_file: file path of the route file
        :return: True if the initialization is successful, False otherwise
        """
        self.route = Read.route(route_file)
        # for car_num, vehicle in self.vehicle_dict.items():
        #     vehicle.route = self.route
        return self.route

    def read_vehicle(self, vehicle_file: str) -> dict:
        """
        Read the vehicle file and initialize the vehicle list
        :param vehicle_file: file path of the vehicle file
        :return: True if the initialization is successful, False otherwise
        """
        vehicle_list = Read.vehicle(vehicle_file)
        for vehicle in vehicle_list:
            self.vehicle_dict[vehicle.car_num] = vehicle
            vehicle.route = self.route
        return self.vehicle_dict

    def read_factory(self, factory_file: str) -> dict:
        """
        Read the factory file and initialize the factory list
        :param factory_file: file path of the factory file
        :return: True if the initialization is successful, False otherwise
        """
        factory_list = Read.factory(factory_file)
        for factory in factory_list:
            self.factory_dict[factory.factory_id] = factory
        return self.factory_dict

    def read_data(self, vehicle_file: str = 'D:\\Project\\ICAPS-2021\\data\\test\\vehicle_info_5.csv',
                  factory_file: str = 'D:\\Project\\ICAPS-2021\\data\\test\\factory_info.csv',
                  route_file: str = 'D:\\Project\\ICAPS-2021\\data\\test\\50_1.csv') -> bool:
        """
        Read the data files and initialize the DPDPTW model
        :param vehicle_file: file path of the vehicle file
        :param factory_file: file path of the factory file
        :param route_file: file path of the route file
        :return: True if the initialization is successful, False otherwise
        """
        self.read_route(route_file)
        self.read_vehicle(vehicle_file)
        self.read_factory(factory_file)
        return True

    def add_order_list(self, order_list: list) -> bool:
        """
        Add a list of orders to be served
        :param order_list: list of Order objects
        :return: True if the addition is successful, False otherwise
        """
        self.order_list.extend(order_list)
        return True

    def distribute_orders(self, algorithm: str = "GreedyAlgorithm",
                          parameters: dict = None,
                          seed: int = 0):
        """
        Distribute the orders in the self.order_list to the vehicles
        :param seed:
        :param parameters:
        :param algorithm: the algorithm to distribute the orders, either "GreedyAlgorithm" or "SolomonInsertionAlgorithm"
        :return: None
        """
        if algorithm == "GreedyAlgorithm":
            # GreedyAlgorithm.dispatch(self.order_list, self.vehicle_dict, self.factory_dict, self.route)
            GreedyAlgorithm.dispatch(self, self.order_list)
            # print(f"after distribute{self.vehicle_dict['V_1'].assignment_list}")

        elif algorithm == "SolomonInsertionAlgorithm":
            SolomonInsertAlgorithm.dispatch(self, self.order_list, parameters, seed)
            # TODO: implement SolomonInsertionAlgorithm
            pass
        else:
            raise ValueError("Invalid algorithm name")
        self.order_list = []

    def total_cost(self):
        """
        Calculate the total cost of the DPDPTW model
        :return: (the total distance, the total delay)
        """
        model = copy.deepcopy(self)
        # step to the end of all orders
        model.update(1000000)
        total_cost = 0
        total_delay = 0
        for car_num, vehicle in model.vehicle_dict.items():
            total_cost += vehicle.distance
            total_delay += vehicle.delay
        return total_cost, total_delay

    def can_add_order(self, car_num, order, pick_up_position, delivery_position):
        """
        Check if the order can be added to the vehicle
        which picks up the order at the pick_up_position and delivers the order at the delivery_position of the assignmen_list
        """
        # check if the positions are valid
        if pick_up_position > delivery_position:
            raise ValueError("The pick-up position should be less than or equal to the delivery position")
        # If the vehicle is idle
        if self.vehicle_dict[car_num].status == 'IDLE':
            # print("can_add_order: vehicle is idle")
            return True
        elif not self.vehicle_dict[car_num].assignment_list:
            return True
        # If the vehicle is working
        elif self.vehicle_dict[car_num].status in ['PICKING_UP', 'DELIVERING', 'LOADING','UNLOADING', 'WAITING']:
            # check capacity
            # if self.vehicle_dict[car_num].capacity < order.demand:
            if not self.vehicle_dict[car_num].check_capacity(order):
                # print("can_add_order: vehicle capacity is not enough")
                return False
            # check the sequence of pick-up and delivery
            if not self.vehicle_dict[car_num].check_assignment_list(order, pick_up_position, delivery_position):
                # print("can_add_order: the sequence of pick-up and delivery is correct")
                return False
            return True

    def init_solution(self, solution_type: str, parameters: dict = None, seed: int = 0):
        """
        Initialize the solution of the DPDPTW model
        :param solution_type: type of the solution, "GreedyAlgorithm"
        :param parameters: parameters for the solution, including mu, alpha, lmbda, ...
        :param seed: random seed for the initialization
        :return: True if the initialization is successful, False otherwise
        """
        if solution_type == "SolomonInsertionAlgorithm":
            if parameters is None:
                parameters = {'mu': 1.0, 'alpha': 0.5, 'lmbda': 1.0}
            # TODO: implement SolomonInsertionAlgorithm

        elif solution_type == "GreedyAlgorithm":
            for order in self.order_list:
                GreedyAlgorithm.dispatch(self, self.order_list)
                self.order_list = []

    def _find_least_time_step(self):
        """
        Find the min{vehicle.next_status_time} for all vehicles
        :return: the least time step and the corresponding vehicle, or None if there is no vehicle available
        """
        min_time = float('inf')
        min_vehicle = None
        for car_num, vehicle in self.vehicle_dict.items():
            # 当前无任务, 之后有任务
            if vehicle.next_status_time is None and vehicle.assignment_list:
                return 0.1, None
            #
            if vehicle.status == 'IDLE' or vehicle.next_status_time is None:
                continue
            elif vehicle.next_status_time < min_time:
                min_vehicle = vehicle
                min_time = vehicle.next_status_time
        if min_vehicle is None:
            return None, None
        return min_time, min_vehicle

    def get_vehicle_capacity(self):
        return self.vehicle_dict

    def update(self, time_step:int):
        """
        Update the DPDPTW model from now to now+time_step
        :param time_step: current time step
        :return: None
        """
        time = time_step # 剩余时间
        while time > 0:
            # Find the vehicle & the least time step
            least_step, first_vehicle = self._find_least_time_step()
            if least_step is None:
                step = time
            elif least_step == 0.1:
                step = 0
            else:
                step = min(least_step, time) # 本次循环移动的步长
            # Update vehicles
            for car_num, vehicle in self.vehicle_dict.items():
                vehicle.print_information()
                # 下一状态时间为None, (初始状态)
                if vehicle.next_status_time is None:
                    # 1. 车辆没有任务
                    if vehicle.current_assignment is None and not vehicle.assignment_list:
                        vehicle.status = 'IDLE'
                        vehicle.now += step
                        # print("+++++")
                        continue
                    # 2. 当前无任务, 以后有任务, 进行下一个任务
                    elif vehicle.current_assignment is None and vehicle.assignment_list:
                        vehicle.current_assignment = vehicle.assignment_list.pop(0)
                        vehicle.status = 'PICKING_UP' if vehicle.current_assignment[2] == 'PICK_UP' else 'DELIVERING'
                        vehicle.next_status_time = vehicle.current_assignment[1].load_time if vehicle.status == 'PICKING_UP' else vehicle.current_assignment[1].unload_time
                        vehicle.history_info.append(
                            (vehicle.now, 'begin', vehicle.current_assignment[0], 'condition 2', vehicle.status, vehicle.assignment_list))
                    # 当前有任务, 报错
                    else:
                        print("Error: current_assignment is not None but assignment_list is empty")
                        raise ValueError("Error: current_assignment is not None but assignment_list is not empty")

                # 3. 还没到下一个状态变化的时间
                elif vehicle.next_status_time > step:
                    vehicle.next_status_time -= step
                    vehicle.now += step
                    continue
                # 4. 车辆空闲且没有任务
                elif vehicle.status == 'IDLE' and not vehicle.assignment_list:
                    vehicle.next_status_time = None
                    vehicle.now += step
                    continue
                # 5. 车辆空闲但有任务, 执行最早任务
                elif vehicle.status == 'IDLE' and vehicle.assignment_list:
                    vehicle.current_assignment = vehicle.assignment_list.pop(0)
                    vehicle.status = 'PICKING_UP' if vehicle.current_assignment[2] == 'PICK_UP' else 'DELIVERING'
                    vehicle.next_status_time = vehicle.current_assignment[1].load_time if vehicle.status == 'PICKING_UP' else vehicle.current_assignment[1].unload_time
                    vehicle.history_info.append(
                        (vehicle.now, 'begin', vehicle.current_assignment[0], 'condition 5', vehicle.status, vehicle.assignment_list))
                # 到达下一个状态变化的时间
                else:
                    # 6. 到达
                    if vehicle.status in ['PICKING_UP', 'DELIVERING']:
                        # 下一状态信息
                        next_location_id = vehicle.current_assignment[0]
                        # distribute port, update status
                        vehicle.status, port = self.factory_dict[vehicle.current_assignment[0]].add_vehicle(vehicle,
                                                                                         vehicle.current_assignment[2])
                        # record
                        vehicle.history_info.append(
                            (vehicle.now, 'arrive', next_location_id, 'condition 6', vehicle.status, vehicle.assignment_list))
                        # update time
                        # time -= vehicle.next_status_time
                        # vehicle.now += vehicle.next_status_time
                        if port.finish_time <= vehicle.next_status_time:  # 没到就空了
                            vehicle.next_status_time = vehicle.current_assignment[1].load_time if vehicle.status == 'PICKING_UP' else vehicle.current_assignment[1].unload_time
                        else:  # 到时还没空
                            vehicle.next_status_time = port.finish_time - vehicle.next_status_time + \
                                                       vehicle.current_assignment[1].load_time if vehicle.status == 'PICKING_UP' else vehicle.current_assignment[1].unload_time
                    # 7-1. 离开, 再无任务(完成卸货)
                    elif vehicle.status in ['LOADING', 'UNLOADING'] and not vehicle.assignment_list:
                        # record
                        vehicle.history_info.append(
                            (vehicle.now, 'unload', vehicle.current_assignment[0], 'condition 7-1', 'IDLE', vehicle.assignment_list))
                        # update status
                        vehicle.status = 'IDLE'
                        vehicle.next_status_time = None
                        # update cargo
                        if vehicle.status == 'UNLOADING':
                            cargo_order = vehicle.cargo.pop()
                            # calculate postpone
                            if cargo_order.committed_completion_time < vehicle.now:
                                vehicle.delay += max(0, cargo_order.committed_completion_time - vehicle.now)
                        else:
                            cargo_order = vehicle.current_assignment[1]
                            vehicle.cargo.append(cargo_order)
                            # calculate postpone
                            if cargo_order.committed_completion_time < vehicle.now:
                                vehicle.delay += max(0, cargo_order.committed_completion_time - vehicle.now)
                        # update assignment
                        vehicle.current_assignment = None
                        # update time
                        vehicle.now += step
                        continue
                    # 7-2. 离开, 还有任务
                    elif vehicle.status in ['LOADING', 'UNLOADING'] and vehicle.assignment_list:
                        # update cargo
                        if vehicle.status == 'UNLOADING':
                            cargo_order = vehicle.cargo.pop()
                            # calculate postpone
                            if cargo_order.committed_completion_time < vehicle.now:
                                vehicle.delay += max(0, cargo_order.committed_completion_time - vehicle.now)
                        else:
                            cargo_order = vehicle.current_assignment[1]
                            vehicle.cargo.append(vehicle.current_assignment[1])
                        # update assignment
                        old_location_id = vehicle.current_assignment[0]
                        vehicle.current_assignment = vehicle.assignment_list.pop(0)
                        # update status
                        old_status = vehicle.status
                        vehicle.status = 'PICKING_UP' if vehicle.current_assignment[2] == 'PICK_UP' else 'DELIVERING'
                        # record
                        vehicle.distance += vehicle.route.distance(vehicle.current_assignment[0],
                                                                   old_location_id)
                        if old_status == 'LOADING':
                            vehicle.history_info.append(
                                (vehicle.now, 'load', vehicle.current_assignment[0], "condition 7-2", vehicle.status, vehicle.assignment_list))
                        else:
                            vehicle.history_info.append(
                                (vehicle.now, 'unload', vehicle.current_assignment[0], "condition 7-2", vehicle.status, vehicle.assignment_list))
                        # update time
                        # time -= vehicle.next_status_time
                        # vehicle.now += vehicle.next_status_time
                        vehicle.next_status_time = vehicle.route.time(old_location_id,
                                                                      vehicle.current_assignment[0])
                    # 8. 排到
                    elif vehicle.status == 'WAITING':
                        # update status
                        vehicle.status = 'LOADING' if vehicle.current_assignment[2] == 'PICK_UP' else 'UNLOADING'
                        # record
                        vehicle.history_info.append(
                            (vehicle.now, 'begin', vehicle.current_assignment[0], 'condition 8', vehicle.status, vehicle.assignment_list))
                        # update time
                        # time -= vehicle.next_status_time
                        # vehicle.now += vehicle.next_status_time

                # update time
                vehicle.now += step

            for car_num, vehicle in self.vehicle_dict.items():
                vehicle.print_information()

            # Update factories
            for factory_id, factory in self.factory_dict.items():
                # factory.update(least_step)
                for port in factory.port_list:
                    port.finish_time -= step if port.finish_time >= step else 0
            time -= step
        self.now += time_step

if __name__ == '__main__':
    # Example usage
    dpdptw = DPDPTW()
    instance_name = 'D:\\Project\\ICAPS-2021\\data\\benchmark\\instance_1'
    dpdptw.read_data(vehicle_file= instance_name + '\\vehicle_info_5.csv',
                  factory_file = 'D:\\Project\\ICAPS-2021\\data\\test\\factory_info.csv',
                  route_file = 'D:\\Project\\ICAPS-2021\\data\\test\\route_info.csv')
    # print(dpdptw.route)
    paths = [
        r"D:\Project\ICAPS-2021\data\benchmark\instance_11\100_3.csv",
        r"D:\Project\ICAPS-2021\data\benchmark\instance_12\100_4.csv",
        r"D:\Project\ICAPS-2021\data\benchmark\instance_10\100_2.csv",
        r"D:\Project\ICAPS-2021\data\benchmark\instance_9\100_1.csv",
        r"D:\Project\ICAPS-2021\data\benchmark\instance_8\50_8.csv",
        r"D:\Project\ICAPS-2021\data\benchmark\instance_7\50_7.csv",
        r"D:\Project\ICAPS-2021\data\benchmark\instance_6\50_6.csv",
        r"D:\Project\ICAPS-2021\data\benchmark\instance_5\50_5.csv",
        r"D:\Project\ICAPS-2021\data\benchmark\instance_4\50_4.csv",
        r"D:\Project\ICAPS-2021\data\benchmark\instance_3\50_3.csv",
        r"D:\Project\ICAPS-2021\data\benchmark\instance_2\50_2.csv",
        r"D:\Project\ICAPS-2021\data\benchmark\instance_1\50_1.csv",
    ]
    # paths = [
    #     r"D:\Project\ICAPS-2021\data\benchmark\instance_13\100_5.csv",
    #     r"D:\Project\ICAPS-2021\data\benchmark\instance_14\100_6.csv",
    #     r"D:\Project\ICAPS-2021\data\benchmark\instance_15\100_7.csv",
    #     r"D:\Project\ICAPS-2021\data\benchmark\instance_16\100_8.csv",
    #     r"D:\Project\ICAPS-2021\data\benchmark\instance_17\300_1.csv",
    #     r"D:\Project\ICAPS-2021\data\benchmark\instance_18\300_2.csv",
    #     r"D:\Project\ICAPS-2021\data\benchmark\instance_19\300_3.csv",
    #     r"D:\Project\ICAPS-2021\data\benchmark\instance_20\300_4.csv"
    # ]

    order_slices = Read.order_to_slices(paths[-3])
    print(order_slices)

    # # 单次插入
    # order_slice = order_slices[180]
    # print(order_slice)
    # dpdptw.add_order_list(order_slice)
    # dpdptw.distribute_orders(algorithm='GreedyAlgorithm')
    # print(dpdptw.vehicle_dict['V_1'].assignment_list)
    # # print(dpdptw.factory_dict['b6dd694ae05541dba369a2a759d2c2b9'])
    # dpdptw.update(180)
    # # print(dpdptw.total_cost())

    # 多次插入
    start_time = 0
    for end_time, order_slice in order_slices.items():
        dpdptw.add_order_list(order_slice)
        dpdptw.distribute_orders(algorithm='GreedyAlgorithm')
        time_step = end_time - start_time
        dpdptw.update(time_step)
        start_time = end_time
    # print(dpdptw.total_cost())
    dpdptw.update(1000000)
    distance, delay = 0, 0
    for car_num, vehicle in dpdptw.vehicle_dict.items():
        distance += vehicle.distance
        delay += vehicle.delay
    print(f"distance: {distance}, delay: {delay}")