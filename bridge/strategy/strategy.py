"""High-level strategy code"""

# !v DEBUG ONLY
import math  # type: ignore  # noqa: F401
from time import time  # type: ignore  # noqa: F401
from typing import Optional
import random
from bridge import const
from bridge.auxiliary import aux, fld, rbt  # type: ignore  # noqa: F401
from bridge.const import State as GameStates
from bridge.router.actions import (  # type: ignore  # noqa: F401
    Action,
    Actions,
    KickActions,
    StrategyActions,
)


class Strategy:
    """Main class of strategy"""

    def __init__(
        self,
    ) -> None:
        self.we_active = False
        self.is_target_set = False

    def process(self, field: fld.Field) -> list[Optional[Action]]:
        """Game State Management"""
        if field.game_state not in [GameStates.KICKOFF, GameStates.PENALTY]:
            if field.active_team in [const.Color.ALL, field.ally_color]:
                self.we_active = True
            else:
                self.we_active = False

        actions: list[Optional[Action]] = []
        for _ in range(const.TEAM_ROBOTS_MAX_COUNT):
            actions.append(None)

        match field.game_state:
            case GameStates.RUN:
                self.run(field, actions)
            case GameStates.TIMEOUT:
                pass
            case GameStates.HALT:
                return [None] * const.TEAM_ROBOTS_MAX_COUNT
            case GameStates.PREPARE_PENALTY:
                pass
            case GameStates.PENALTY:
                pass
            case GameStates.PREPARE_KICKOFF:
                pass
            case GameStates.KICKOFF:
                pass
            case GameStates.FREE_KICK:
                pass
            case GameStates.STOP:
                # The router will automatically prevent robots from getting too close to the ball
                self.run(field, actions)
            case GameStates.BALL_PLACEMENT:
                pass
            case GameStates.DEBUG:
                pass

        return actions

    def run(self, field: fld.Field, actions: list[Optional[Action]]) -> None:
        """
        ONE ITERATION of strategy
        NOTE: robots will not start acting until this function returns an array of actions,
              if an action is overwritten during the process, only the last one will be executed)

        Examples of getting coordinates:
        - field.allies[8].get_pos(): aux.Point -   coordinates  of the 8th  robot from the allies
        - field.enemies[14].get_angle(): float - rotation angle of the 14th robot from the opponents

        - field.ally_goal.center: Point - center of the ally goal
        - field.enemy_goal.hull: list[Point] - polygon around the enemy goal area


        Examples of robot control:
        - actions[2] = Actions.GoToPoint(aux.Point(1000, 500), math.pi / 2)
                The robot number 2 will go to the point (1000, 500), looking in the direction π/2 (up, along the OY axis)

        - actions[3] = Actions.Kick(field.enemy_goal.center)
                The robot number 3 will hit the ball to 'field.enemy_goal.center' (to the center of the enemy goal)

        - actions[9] = Actions.BallGrab(0.0)
                The robot number 9 grabs the ball at an angle of 0.0 (it looks to the right, along the OX axis)
        """
        
        v3 = field.ball.get_pos() - field.allies[0].get_pos() 
        v1 = field.ball.get_pos() - field.enemy_goal.center 
        v4 = v1 + v1/v1.mag()*50
        # actions[1] = Actions.GoToPoint(field.enemy_goal.center+v4,v3.arg())
        p1 = [(field.enemy_goal.center + field.enemy_goal.down + field.enemy_goal.down + field.enemy_goal.down) / 4,
              (field.enemy_goal.center + field.enemy_goal.up + field.enemy_goal.up + field.enemy_goal.up) / 4,
              field.enemy_goal.center]
        p2 = [p1[0]-field.enemies[0].get_pos(),p1[1]-field.enemies[0].get_pos(),p1[2]-field.enemies[0].get_pos()]
        p_mag= [p2[0].mag(),p2[1].mag(),p2[2].mag()]

        # print(p1[0].x, p1[0].y, p1[1].x, p1[1].y)


        actions[0] = KickActions.Straight(p1[p_mag.index(max(p_mag))])                                      

       

        v5 = field.enemies[1].get_pos() - field.ball.get_pos() 
        v6 = field.enemies[1].get_pos() - v5.unity()*200
        v7 = v6 - field.enemies[1].get_pos()
        actions[0] = Actions.GoToPoint(v6,v7.arg())
        field.strategy_image.draw_line(v5, v6 )
        field.strategy_image.draw_line(field.ball.get_pos() - field.enemy_goal.center, field.allies[1].get_pos() )
        v8 = aux.get_line_intersection(aux.Point(field.polarity*2050,-1800),aux.Point(field.polarity*2050,1800),field.ally_goal.center,field.enemies[0].get_pos())
        v10 = field.enemies[0].get_pos() - field.ally_goal.center
        if v8 != None:
            actions[2] = Actions.GoToPoint(v8,v10.arg())
        field.strategy_image.draw_line(aux.Point(-2050,-1800),aux.Point(-2050,1800))
        field.strategy_image.draw_line(field.ally_goal.center,field.enemies[0].get_pos())
        field.strategy_image.draw_line(aux.Point(2050,-1800),aux.Point(2050,1800))
        kick(field,actions,0,1)

def kick(field: fld.Field, actions: list[Optional[Action]],gk,at) -> None:
    v11 = field.enemies[gk].get_pos() - field.ball.get_pos()
    v12 = aux.rotate(v11, math.pi / 2).unity()*100+field.enemies[gk].get_pos()
    v13 = aux.rotate(v11, math.pi / 2 * 3).unity()*100+field.enemies[gk].get_pos()
    field.strategy_image.draw_line(field.enemies[gk].get_pos(),v12,(0,0,0))
    field.strategy_image.draw_line(field.enemies[gk].get_pos(),v13,(255,0,0))
    v14 = aux.get_line_intersection(field.enemy_goal.up,field.enemy_goal.down,field.ball.get_pos(),v12,'SR' )
    v15 = aux.get_line_intersection(field.enemy_goal.up,field.enemy_goal.down,field.ball.get_pos(),v13,'SR' )
    if v14 != None:
        field.strategy_image.draw_circle(v14,(255,0,0),10)
    if v15 != None:
        field.strategy_image.draw_circle(v15,(0,0,255),10)

    if v15 == None and v14 != None:  #kust red dot
        v16 = (v14 + field.enemy_goal.up) / 2
        field.strategy_image.draw_line(field.enemy_goal.up,v14)
        actions[at] = KickActions.Straight(v16) 
    elif v15 != None and v14 == None: #just blue dot
        v16 = (v15 + field.enemy_goal.down) / 2
        field.strategy_image.draw_line(field.enemy_goal.down,v15)
        actions[at] = KickActions.Straight(v16)
    elif v15 != None and v14 != None:
        v16 = (v14 + field.enemy_goal.up) /2
        v17 = (v15 + field.enemy_goal.down) /2
        if (v16-field.enemy_goal.up).mag() > (v17-field.enemy_goal.down).mag():
            actions[at] = KickActions.Straight(v16)
        else:   
            actions[at] = KickActions.Straight(v17)
    else:
        v14 = aux.get_line_intersection(field.enemy_goal.up,field.enemy_goal.down,field.ball.get_pos(),v12,'LR' )
        v15 = aux.get_line_intersection(field.enemy_goal.up,field.enemy_goal.down,field.ball.get_pos(),v13,'LR' )
        if v14 == None or v15 == None or (v14.y <= -400 and v15.y <= -400) or (v14.y >= 400 and v15.y >= 400):
            actions[at] = KickActions.Straight(field.enemy_goal.center)
        else:
            actions[at] = Actions.Stop()
        
        
        
        
        
        
        



