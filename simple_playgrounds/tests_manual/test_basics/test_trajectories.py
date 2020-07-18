from simple_playgrounds.utils.position_utils import Trajectory

# t = Trajectory('waypoints', 100, 4, waypoints=[[0,0], [10,10]], counter_clockwise=True, index_start=10)
t = Trajectory('shape', 100, 4, shape='square', radius = 10, center=[10,10], counter_clockwise=True, index_start=10)

for i in range(300):
    print(t.current_index, next(t))
