from gymnasium.envs.registration import register

register(
    id="2048-v0",
    entry_point="env_2048:Env2048",
)

from .env_2048 import Env2048