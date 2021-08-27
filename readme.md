# Robot Open Autonomous Racing (ROAR)

### To Contribute
- Please click the [Fork](https://docs.github.com/en/free-pro-team@latest/github/getting-started-with-github/fork-a-repo) button on the upper right corner and submit a pull request to master branch.
    - For a more in-depth tutorial on recommended setup [video](https://youtu.be/VA13dAZ9iAw)
- Please follow suggested guidelines on Pull Request. 

### Quick start
For quick start documentation, please visit our documentation site: [https://augcog.github.io/ROAR/quickstart/](https://augcog.github.io/ROAR/quickstart/)


### Enter the Competition
Visit [https://augcog.github.io/ROAR/competition_instruction/](https://augcog.github.io/ROAR/competition_instruction/)

### How to run my code
There should not be any new dependencies, so if the conda environment used has already been set up like [this](https://augcog.github.io/ROAR/quickstart/), then that will be sufficient.
`ROAR_Sim/configurations/carla_version.txt` will need to be modified to be `0.9.10` instead `0.9.9`.
This should be as simple as running `runner_competition_evaluator.py` after starting the Berkeley minor server.
There seems to be a bug with the competition evaluator where the car will start at the starting position, teleport to [0,0,0], then go back to the start position when the simulator is first started.
I was able to fix this in `carla_runner.py` (the code is [here](https://gist.github.com/Camshaft54/f02343f82288d4de32f751016299cdef)), but since we are not allowed to modify this for the code for the competition, I have not included it in this submission.
In order to have the car actually race for 10 laps, I modified num_laps in `runner_competition_evaluator.py` to be 11 (to account for skipping the first lap).