"""
Определение необходимых констант
"""

# pylint: disable=invalid-name
import math
from enum import Enum

from environment.setup_environment import get_from_env, get_from_env_specific_type


class State(Enum):
    """Класс с состояниями игры"""

    HALT = 0
    TIMEOUT = 1
    STOP = 2
    PREPARE_KICKOFF = 3
    BALL_PLACEMENT = 4
    PREPARE_PENALTY = 5
    KICKOFF = 6
    FREE_KICK = 7
    PENALTY = 8
    RUN = 9
    DEBUG = 10


class Color(Enum):
    """Класс с цветами"""

    ALL = 0
    BLUE = 1
    YELLOW = 2

    def reverse(self) -> "Color":
        """Returns another color"""
        if self == Color.BLUE:
            return Color.YELLOW
        if self == Color.YELLOW:
            return Color.BLUE
        return Color.ALL


class Div(Enum):
    """Класс с разными дивизионами"""

    A = 0  # XD
    B = 1
    C = 2


IS_SIMULATOR_USED: bool = get_from_env("IS_SIMULATOR_USED", bool)

DIV: Div = get_from_env_specific_type("DIVISION", Div)
COLOR: Color = get_from_env_specific_type("COLOR", Color)
POLARITY: int = get_from_env("POLARITY", int)
if POLARITY not in [1, -1]:
    RED_BOLD = "\033[91m\033[1m"
    RESET = "\033[0m"
    raise RuntimeError(f"{RED_BOLD}POLARITY must be 1 or -1, got: {POLARITY}{RESET}")

GK: int = get_from_env("GK", int)
ENEMY_GK: int = get_from_env("ENEMY_GK", int)
DEBUG_HALF: int = get_from_env("DEBUG_HALF", int)


SELF_PLAY = False

ROBOTS_MAX_COUNT: int = 32
TEAM_ROBOTS_MAX_COUNT: int = ROBOTS_MAX_COUNT // 2
GEOMETRY_PACKET_SIZE: int = 2

CONTROL_MAPPING: dict[int, int] = {
    # vision_id: control_id,
    # 0: 8,
    # 1: 9,
    # 2: 10,
    # 3: 11,
    # 4: 12,
    # 5: 13,
    # 6: 14,
    # 7: 15,
    # 8: 0,
    # 9: 1,
    # 10: 2,
    # 11: 3,
    # 12: 4,
    # 13: 5,
    # 14: 6,
    # 15: 7,
    0: 0,
    1: 1,
    2: 2,
    3: 3,
    4: 4,
    5: 5,
    6: 6,
    7: 7,
    8: 8,
    9: 9,
    10: 10,
    11: 11,
    12: 12,
    13: 13,
    14: 14,
    15: 15,
}
REVERSED_KICK: list[int] = []

for i in range(TEAM_ROBOTS_MAX_COUNT):
    try:
        CONTROL_MAPPING[i]
    except KeyError:
        CONTROL_MAPPING[i] = -1

CONTROL_TOPIC = "control-topic"
FIELD_TOPIC = "field-topic"
IMAGE_TOPIC = "image-topic"
##################################################

##################################################
# CONTROL CONST
Ts = 0.02  # s

# ROBOT SETTING CONSTS
MAX_SPEED = 1000 if not IS_SIMULATOR_USED else 1000
MAX_ACCELERATION = 4000
MAX_SPEED_R = 30

STOP_SPEED = 800

INTERCEPT_SPEED = 50
##################################################
# GEOMETRY CONSTS

BALL_R = 22
ROBOT_R = 100
GRAVEYARD_POS_X = -10000

BALL_MAX_VISION_SPEED = 10000  # for filter random balls
ROBOT_MAX_VISION_SPEED = 10000  # for filter random robots
TIME_TO_BORN = 0.1  # time to add robot to field
TIME_TO_DIE = 0.3  # time to remove robot from field


match DIV:
    case Div.A:
        GOAL_DX = 1 / 0  # не дорос ещё

    case Div.B:
        GOAL_DX = 4500
        GOAL_DY = 1000
        GOAL_PEN_DX = 1000
        GOAL_PEN_DY = 2000

        PEN_DIST = 6000

        FIELD_DX = GOAL_DX
        FIELD_DY = 3000

        GK_FORW = 200 + ROBOT_R

    case Div.C:
        GOAL_DX = 2250
        GOAL_DY = 800
        GOAL_PEN_DX = 500
        GOAL_PEN_DY = 1350

        PEN_DIST = GOAL_DX

        FIELD_DX = GOAL_DX
        FIELD_DY = 1500

        GK_FORW = 100 + ROBOT_R

# ROUTE CONSTS
VIEW_DIST = 2500
if DIV == Div.C:
    KEEP_BALL_DIST = 300 + ROBOT_R
else:
    KEEP_BALL_DIST = 500 + ROBOT_R

# is_ball_in
GRAB_ALIGN_DIST = ROBOT_R + BALL_R
BALL_GRABBED_DIST = 110
BALL_GRABBED_ANGLE = 0.8

# is_kick_aligned
KICK_ALIGN_DIST_MULT = 1.5
KICK_ALIGN_ANGLE = 0.15
KICK_ALIGN_DIST = 200
KICK_ALIGN_OFFSET = 40

# for grabbing ball
GRAB_DIST = 80
GRAB_MULT = 4  # speed = dist * mult
GRAB_OFFSET_ANGLE = 0.4
# #careful grab
GRAB_CAREFUL_DIST = 100
GRAB_CAREFUL_MULT = 4  # speed = dist * mult
GRAB_CAREFUL_OFFSET_ANGLE = 0.3

FAST_GRAB_DIST = 88
FAST_GRAB_MULT = 4  # angle_to_turn / angle_to_grab; >2!!!
MAX_ERR_ANGLE = math.pi / 18
if IS_SIMULATOR_USED:

    GRAB_OFFSET_ANGLE = 0.35

    GRAB_DIST = 85
# VOLTAGES
if DIV == Div.C:
    VOLTAGE_SHOOT = 6
    if IS_SIMULATOR_USED:
        VOLTAGE_SHOOT = 10
    VOLTAGE_UP = 10
    VOLTAGE_ZERO = 10
else:
    VOLTAGE_SHOOT = 15
    VOLTAGE_UP = 15
    VOLTAGE_ZERO = 15
