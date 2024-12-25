import copy


def find_best_insert_vehicle_position(model, order, lmbda = 1):
    """
    寻找 model 中最适合插入 order 的车辆和任务位置
    :param model:
    :param order:
    :return:
    """
    min_cost = float('inf')
    best_position = (None, None)
    best_vehicle = None
    model = copy.deepcopy(model)
    # 优先插入空车
    for car_num, vehicle in model.vehicle_dict.items():
        if vehicle.status == 'IDLE' or not vehicle.assignment_list:
            return vehicle.car_num, (0, 0)
    # 尝试在每辆车的每个位置尝试插入
    for car_num, vehicle in model.vehicle_dict.items():
        for pick_up_i in range(len(vehicle.assignment_list)+1):
            for delivery_j in range(pick_up_i, len(vehicle.assignment_list)+1):
                # print("try insert order", order.order_id, "to car", car_num, "at position", pick_up_i, delivery_j)
                if not model.can_add_order(car_num, order, pick_up_i, delivery_j):
                    # print("insert position not feasible")
                    continue
                vehicle.add_order(order, pick_up_i, delivery_j)
                distance, delay = model.total_cost()
                cost = distance + lmbda * delay
                # print(f"distance({distance}) + lmbda * delay({delay}) = {cost}")
                if cost < min_cost:
                    min_cost = cost
                    best_position = (pick_up_i, delivery_j)
                    best_vehicle = vehicle
                vehicle.remove_order(order)
    if best_vehicle is None:
        # print("No feasible position found for order", order.order_id)
        return None, (None, None)
    else:
        # print("best insert position:", best_vehicle.car_num, best_position)
        return best_vehicle.car_num, best_position

