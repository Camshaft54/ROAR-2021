import logging, warnings
import numpy as np
from ROAR_Sim.configurations.configuration import Configuration as CarlaConfig
from ROAR.configurations.configuration import Configuration as AgentConfig
from pathlib import Path
from ROAR.agent_module.pure_pursuit_agent \
    import PurePursuitAgent
from ROAR_Sim.carla_client.carla_runner import CarlaRunner
from typing import Tuple
from prettytable import PrettyTable
from ROAR.agent_module.pid_agent import PIDAgent
from pit_stop import PitStop as PitStop
from ROAR_Sim.carla_client.util.utilities import CarlaCarColor, CarlaCarColors
import os
import time


def compute_score(carla_runner: CarlaRunner) -> Tuple[float, int, int]:
    """
    Calculates the score of the vehicle upon completion of the track based on certain metrics
    Args:
        carla_runner ():

    Returns:
        time_elapsed:
        num_collision: number of collisions during simulation
        laps_completed: Number of laps completed

    """
    time_elapsed: float = carla_runner.end_simulation_time - carla_runner.start_simulation_time
    num_collision: int = carla_runner.agent_collision_counter
    laps_completed = 0 if carla_runner.completed_lap_count < 0 else carla_runner.completed_lap_count

    return time_elapsed, num_collision, laps_completed


def run(agent_class, agent_config_file_path: Path, carla_config_file_path: Path,
        num_laps: int = 10) -> Tuple[float, int, int]:
    """
    Run the agent along the track and produce a score based on certain metrics
    Args:
        num_laps: int number of laps that the agent should run
        agent_class: the participant's agent
        agent_config_file_path: agent configuration path
        carla_config_file_path: carla configuration path
    Returns:
        float between 0 - 1 representing scores
    """

    agent_config: AgentConfig = AgentConfig.parse_file(agent_config_file_path)
    carla_config = CarlaConfig.parse_file(carla_config_file_path)

    set_up_pitstop(agent_config, carla_config)

    # hard code agent config such that it reflect competition requirements
    agent_config.num_laps = num_laps
    carla_runner = CarlaRunner(carla_settings=carla_config,
                               agent_settings=agent_config,
                               npc_agent_class=PurePursuitAgent,
                               competition_mode=True,
                               start_bbox=np.array([-815, 20, -760, -770, 120, -600]),
                               lap_count=num_laps)
    try:
        my_vehicle = carla_runner.set_carla_world()
        agent = agent_class(vehicle=my_vehicle, agent_settings=agent_config)
        carla_runner.start_game_loop(agent=agent, use_manual_control=False)
        return compute_score(carla_runner)
    except Exception as e:
        print(f"something bad happened during initialization: {e}")
        carla_runner.on_finish()
        logging.error(f"{e}. Might be a good idea to restart Server")
        return 0, 0, False


def suppress_warnings():
    logging.basicConfig(format='%(levelname)s - %(asctime)s - %(name)s '
                               '- %(message)s',
                        level=logging.INFO)
    logging.getLogger("matplotlib").setLevel(logging.WARNING)
    warnings.simplefilter("ignore")
    np.set_printoptions(suppress=True)


def main():
    suppress_warnings()
    agent_class = PIDAgent
    num_trials = 1
    total_score = 0
    num_laps = 10
    table = PrettyTable()
    table.field_names = ["time_elapsed (sec)", "num_collisions", "laps completed"]
    for i in range(num_trials):
        scores = run(agent_class=agent_class,
                     agent_config_file_path=Path("./config/agent_configuration.json"),
                     carla_config_file_path=Path("./config/configuration.json"),
                     num_laps=num_laps)
        table.add_row(scores)
    print(table)


def set_up_pitstop(agent_config, carla_config):
    pitstop = PitStop(carla_config, agent_config)
    pitstop.set_carla_sync_mode(synchronized=False)
    pitstop.set_autopilot_mode(enabled=True)
    pitstop.set_car_model(car_model="vehicle.nissan.micra")
    pitstop.set_car_color(color=CarlaCarColor(r=255, g=200, b=00, a=255))
    pitstop.set_num_laps(num=1)
    pitstop.set_waypoint_file_path(path=(Path(
        os.getcwd()) / "ROAR_Sim" / "data" / "berkeley_minor_waypoints.txt").as_posix())
    pitstop.set_output_data_folder_path(path="./data/output")
    pitstop.set_output_data_file_name(name=time.strftime("%Y%m%d-%H%M%S-") + "map-waypoints")
    pitstop.set_max_speed(speed=200)
    pitstop.set_target_speed(speed=100)
    pitstop.set_steering_boundary(boundary=(-1.0, 1.0))
    pitstop.set_throttle_boundary(boundary=(0, 1.0))
    pitstop.set_waypoints_look_ahead_values(values={
        "60": 5,
        "80": 10,
        "120": 20,
        "180": 50})
    pid_values = {
        "longitudinal_controller": {
            "40": {
                "Kp": 1.0,
                "Kd": 0.3,
                "Ki": 0
            },
            "60": {
                "Kp": 0.7,
                "Kd": 0.2,
                "Ki": 0
            },
            "80": {
                "Kp": 0.5,
                "Kd": 0.1,
                "Ki": 0
            },
            "100": {
                "Kp": 0.5,
                "Kd": 0.15,
                "Ki": 0.05
            },
            "150": {
                "Kp": 0.2,
                "Kd": 0.1,
                "Ki": 0.1
            }
        },
        "latitudinal_controller": {
            "60": {
                "Kp": 0.8,
                "Kd": 0.1,
                "Ki": 0.2
            },
            "100": {
                "Kp": 1.0,
                "Kd": 0.1,
                "Ki": 0.2
            },
            "150": {
                "Kp": 0.5,
                "Kd": 0.2,
                "Ki": 0.2
            }
        }
    }
    pitstop.set_pid_values(pid_values)


if __name__ == "__main__":
    main()
