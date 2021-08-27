import logging
from pathlib import Path
import time
import os

import runner_competition_evaluator
from ROAR_Sim.configurations.configuration import Configuration as CarlaConfig
from ROAR_Sim.carla_client.carla_runner import CarlaRunner

from ROAR.configurations.configuration import Configuration as AgentConfig
from ROAR.agent_module.pure_pursuit_agent import PurePursuitAgent
from ROAR.agent_module.special_agents.recording_agent import RecordingAgent
from ROAR_Sim.carla_client.util.utilities import CarlaCarColor, CarlaCarColors

# Agents
from ROAR.agent_module.special_agents.waypoint_generating_agent import \
    WaypointGeneratigAgent  # agent for new waypoints generation
from ROAR.agent_module.forward_only_agent import ForwardOnlyAgent
from ROAR.agent_module.pid_agent import PIDAgent
from ROAR.agent_module.occu_map_demo_driving_agent import \
    OccuMapDemoDrivingAgent  # Occupancy Map Demo agent. Autonomous driving not supported yet.
from ROAR.agent_module.occupancy_map_agent import OccupancyMapAgent
from ROAR.agent_module.rl_pid_agent import RLPIDAgent  # for rl agent training using Gym and Stable baseline.
# from ROAR.agent_module.rl_testing_pid_agent import RLTestingAgent # rl pid agent demo, requires stable_baselines


from pit_stop import PitStop as PitStop


def main():
    """Starts game loop"""
    carla_config = CarlaConfig.parse_file(Path("./ROAR_Sim/configurations/configuration.json"))
    agent_config = AgentConfig.parse_file(Path("./ROAR_Sim/configurations/agent_configuration.json"))

    runner_competition_evaluator.set_up_pitstop(agent_config, carla_config)

    """Passing configurations to Carla and Agent"""
    carla_runner = CarlaRunner(carla_settings=carla_config,
                               agent_settings=agent_config,
                               npc_agent_class=PurePursuitAgent)
    try:
        my_vehicle = carla_runner.set_carla_world()

        agent = PIDAgent(vehicle=my_vehicle, agent_settings=agent_config)
        # agent = WaypointGeneratigAgent(vehicle=my_vehicle, agent_settings=agent_config)

        carla_runner.start_game_loop(agent=agent, use_manual_control=False)  # for PIDAgent
        # carla_runner.start_game_loop(agent=agent, use_manual_control=True) # for WaypointGeneratingAgent

    except Exception as e:
        logging.error(f"Something bad happened during initialization: {e}")
        carla_runner.on_finish()
        logging.error(f"{e}. Might be a good idea to restart Server")


if __name__ == "__main__":
    logging.basicConfig(format='%(levelname)s - %(asctime)s - %(name)s '
                               '- %(message)s',
                        datefmt="%H:%M:%S",
                        level=logging.DEBUG)
    import warnings

    warnings.filterwarnings("ignore", module="carla")
    main()
