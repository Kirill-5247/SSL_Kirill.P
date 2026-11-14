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
        self.ball_ago = None
        self.ball_ago_list = [None,None,None,None,None]
        self.speed = None
        self.coef1 = 0.3
        self.etr = 0

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


       # actions[0] = KickActions.Straight(p1[p_mag.index(max(p_mag))])                                      

       

        
        at = None
        df = None
        gk = None
        m =  math.inf
        for i in field.active_allies(False):
            dst = aux.dist(i.get_pos(),field.enemy_goal.center)
            if m >=  dst:
                m = dst
                at = i
        if field.allies[field.gk_id].is_used:
            gk = field.gk_id
        if len(field.active_allies(False)) > 1:
            id = 1 - field.active_allies(False).index(at)
            df = field.active_allies(False)[id].r_id
            
        if gk != None and at != None:
            ps = self.defen(field,actions,gk,at.r_id)
            tel = f'Goalkeeper: {gk},Defense: {df},Passing: {ps},Attaker: {at.r_id},Active allies{field.active_allies(False)}'
            field.strategy_image.send_telemetry('Telemetry',tel)
        if at != None:   
            self.kick(field,actions,field.enemy_gk_id,at.r_id,ps)

        

        if len(field.active_allies(False)) > 1:
            id = 1 - field.active_allies(False).index(at) # finding id in LIST!!!
            self.defen_wall(field,actions,df) # finding id of ROBOT!!!
  
        self.ball_ago = self.ball_ago_list[self.etr%5]
        if self.speed != None:
            self.speed = self.speed * self.coef1 + field.ball.get_vel() * (1-self.coef1)
            field.strategy_image.draw_line(field.ball.get_pos(),self.speed + field.ball.get_pos())
        else:
            self.speed = field.ball.get_vel()
        print("===")
        print(self.etr%5)
        if self.ball_ago in self.ball_ago_list:
            print(self.ball_ago_list.index(self.ball_ago))
        if not None in self.ball_ago_list:
            print(self.ball_ago_list.index(max(self.ball_ago_list, key = lambda x: aux.dist(x, field.ball.get_pos()))))
        print("---")
        self.ball_ago_list[self.etr%5] = field.ball.get_pos()
        self.etr += 1
        
        
    def defen_wall(self,field: fld.Field, actions: list[Optional[Action]],df) -> None:
            hullbig = aux.offset_polygon(field.ally_goal.hull,200)
            def cls_2 ():
                p_cls = aux.nearest_point_on_poly(field.ball.get_pos(),hullbig)
                v10 = field.ball.get_pos() - field.allies[df].get_pos()
                if aux.is_point_inside_poly(field.ball.get_pos(),hullbig):
                    actions[df] = KickActions.Straight(field.allies[1].get_pos())
                else:
                    actions[df] = Actions.GoToPoint(p_cls,v10.arg(),ignore_ball=True)

            if self.ball_ago != None and self.ball_ago != field.ball.get_pos():
                v8_1= aux.get_line_intersection(hullbig[0],hullbig[1],self.ball_ago,field.ball.get_pos(),'SL')
                v8_2= aux.get_line_intersection(hullbig[1],hullbig[2],self.ball_ago,field.ball.get_pos(),'SL')
                v8_3= aux.get_line_intersection(hullbig[2],hullbig[3],self.ball_ago,field.ball.get_pos(),'SL')
                intersections = []
                if v8_1 != None:
                    intersections.append(v8_1)
                if v8_2 != None:
                    intersections.append(v8_2)
                if v8_3 != None:
                    intersections.append(v8_3)
                # distances = [aux.dist(v8_1),aux.dist(v8_2),aux.dist(v8_3)]
                # v8 = intersections[distances.index(min(distances))]
                if intersections != []:
                    v8 = min(intersections, key = lambda x: aux.dist(x, field.ball.get_pos()))
                    v10 = field.ball.get_pos() - field.allies[df].get_pos()
                    actions[df] = Actions.GoToPoint(v8,v10.arg(),ball_catch=True)
                else:
                    cls_2()
                field.strategy_image.draw_line(aux.Point(2050,-675),aux.Point(2050,-675))
                field.strategy_image.draw_line(field.allies[2].get_pos(),field.ball.get_pos())
                field.strategy_image.draw_line(aux.Point(-2050,675),aux.Point(-2050,-675))
            else:
                cls_2()
            
                
            

    def no_pass (self,field: fld.Field, actions: list[Optional[Action]],dfa,ate) -> None:
        v5 = field.enemies[ate].get_pos() - field.ball.get_pos() 
        v6 = field.enemies[ate].get_pos() - v5.unity()*200
        v7 = v6 - field.enemies[ate].get_pos()
        actions[dfa] = Actions.GoToPoint(v6,v7.arg())
        field.strategy_image.draw_line(v5, v6 )
        field.strategy_image.draw_line(field.ball.get_pos() - field.enemy_goal.center, field.allies[ate].get_pos() )
        print('No pass')

    def defen(self,field: fld.Field, actions: list[Optional[Action]],gk,at) -> None:
        hullbig = aux.offset_polygon(field.ally_goal.hull,150)
        ps = False
        def cls ():       
            p_cls = aux.nearest_point_in_poly(field.ball.get_pos(),field.ally_goal.hull)
            v10 = field.ball.get_pos() - field.allies[gk].get_pos()
            v8_1= aux.get_line_intersection(field.ally_goal.hull[0],field.ally_goal.hull[1],field.ally_goal.center,field.ball.get_pos(),'SL')
            v8_2= aux.get_line_intersection(field.ally_goal.hull[1],field.ally_goal.hull[2],field.ally_goal.center,field.ball.get_pos(),'SL')
            v8_3= aux.get_line_intersection(field.ally_goal.hull[2],field.ally_goal.hull[3],field.ally_goal.center,field.ball.get_pos(),'SL')
            intersections = []
            if v8_1 != None:
                intersections.append(v8_1)
            if v8_2 != None:
                intersections.append(v8_2)
            if v8_3 != None:
                intersections.append(v8_3)
            # distances = [aux.dist(v8_1),aux.dist(v8_2),aux.dist(v8_3)]
            # v8 = intersections[distances.index(min(distances))]
            if intersections != []:
                v8 = min(intersections, key = lambda x: aux.dist(x, field.ball.get_pos()))
                v10 = field.ball.get_pos() - field.allies[gk].get_pos()
                actions[gk] = Actions.GoToPoint(v8,v10.arg(),ball_catch=True)
               
            if aux.is_point_inside_poly(field.ball.get_pos(),hullbig):
                if aux.dist(field.ball.get_pos(),field.allies[at].get_pos()) >= 800:
                    actions[gk] = KickActions.Straight(field.allies[at].get_pos(),5)
                elif aux.dist(field.ball.get_pos(),field.allies[at].get_pos()) >= 400:
                    actions[gk] = KickActions.Straight(field.allies[at].get_pos(),3)
                else:
                    actions[gk] = KickActions.Straight(field.allies[at].get_pos(),2)
                return  True
            else:
                return False
            
        if self.ball_ago != None and (field.ball.get_pos() - self.ball_ago).mag() > 10 :
            v8 = aux.get_line_intersection(aux.Point(field.polarity*2050,-675),aux.Point(field.polarity*2050,675),self.ball_ago,field.ball.get_pos(),'SL')
            v10 = field.ball.get_pos() - field.allies[gk].get_pos()
            if v8 != None:
                actions[gk] = Actions.GoToPoint(v8,v10.arg(),ball_catch=True)
            else:
                ps = cls()
            field.strategy_image.draw_line(aux.Point(2050,-675),aux.Point(2050,-675))
            field.strategy_image.draw_line(field.allies[2].get_pos(),field.ball.get_pos())
            field.strategy_image.draw_line(aux.Point(-2050,675),aux.Point(-2050,-675))
        else:
            ps = cls()
        return ps
        



    def kick(self,field: fld.Field, actions: list[Optional[Action]],gk: int,at: int,ps: bool) -> None:
        def catching_of_ball():
            v19n =  field.ball.get_pos() - field.allies[at].get_pos()
            field.strategy_image.draw_line(field.ball.get_pos(),v19n*5)
            if self.ball_ago!= None and (field.ball.get_pos() - self.ball_ago).mag() > 10 :
                v20 = aux.closest_point_on_line(self.ball_ago,field.ball.get_pos(),field.allies[at].get_pos(),'L') 
                actions[at] = Actions.GoToPoint(v20,v19n.arg(),ignore_ball=True)
            else:
                actions[at] = Actions.GoToPoint(field.allies[at].get_pos(),v19n.arg(),ignore_ball=True)
        if ps:
            catching_of_ball()
        elif self.ball_ago != None:
            field.strategy_image.draw_circle(field.allies[at].get_pos(),[255,0,0],200)
            
            #field.strategy_image.draw_line(field.ball.get_pos()+(self.ball_ago-field.ball.get_pos())*(10**10),field.allies[at].get_pos(),(255,0,0),10)
            #field.strategy_image.draw_line(self.ball_ago,field.ball.get_pos()+(self.ball_ago-field.ball.get_pos())*1000,(255,0,0),10)
            if aux.line_circle_intersect(self.ball_ago,field.ball.get_pos(),field.allies[at].get_pos(),200,'R') and (field.ball.get_pos() - self.ball_ago).mag() > 10 :
                catching_of_ball()
                
            else:
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
            
    
        
    
        
        
        
        



