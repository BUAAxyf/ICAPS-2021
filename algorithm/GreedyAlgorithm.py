from algorithm.BasicMethod import find_best_insert_vehicle_position
import random

class GreedyAlgorithm:
    """
    GreedyAlgorithm: \n
    For each new order, distribute it to minimize the total cost.
    """
    def __init__(self):
        pass

    @classmethod
    def dispatch(cls, model, order_list):
        """
        Dispatch every order in the order_dict into the model.
        :param model:
        :param order_list:
        :return:
        """
        for order in order_list:
            # Find the best vehicle for the order
            best_vehicle_num, best_position = find_best_insert_vehicle_position(model, order)
            # print(f"best_vehicle_num: {best_vehicle_num}, best_position: {best_position}")
            # Insert the order into the best vehicle
            if best_vehicle_num is None:
                random_car_num = random.choice(list(model.vehicle_dict.keys()))
                model.vehicle_dict[random_car_num].add_order(order, 0, 0)
            else:
                model.vehicle_dict[best_vehicle_num].add_order(order, best_position[0], best_position[1])
            # print(f"best_vehicle.assignment_list{model.vehicle_dict[best_vehicle_num].assignment_list}")
