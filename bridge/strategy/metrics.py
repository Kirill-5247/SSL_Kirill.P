import math  # type: ignore  # noqa: F401
from time import time  # type: ignore  # noqa: F401
from typing import Optional
import random
from bridge import const
from bridge.auxiliary import aux, fld, rbt  # type: ignore  # noqa: F401
from bridge.const import State as GameStates
from bridge.router.actions import (# type: ignore  # noqa: F401
    Action,
    Actions,
    KickActions,
    StrategyActions
)



def clean_goal(field: fld.Field,gk,point):
    v11 = field.enemies[gk].get_pos() - point
    v12 = aux.rotate(v11, math.pi / 2).unity()*100+field.enemies[gk].get_pos()
    v13 = aux.rotate(v11, math.pi / 2 * 3).unity()*100+field.enemies[gk].get_pos()
    field.strategy_image.draw_line(field.enemies[gk].get_pos(),v12,(0,0,0))
    field.strategy_image.draw_line(field.enemies[gk].get_pos(),v13,(255,0,0))
    v14 = aux.get_line_intersection(field.enemy_goal.up,field.enemy_goal.down,point,v12,'SR' )
    v15 = aux.get_line_intersection(field.enemy_goal.up,field.enemy_goal.down,point,v13,'SR' )
    if v14 != None:
        field.strategy_image.draw_circle(v14,(255,0,0),10)
    if v15 != None:
        field.strategy_image.draw_circle(v15,(0,0,255),10)

    if v15 == None and v14 != None:  #kust red dot
        v16 = (v14 + field.enemy_goal.up) / 2
        field.strategy_image.draw_line(field.enemy_goal.up,v14)
        return True 
    elif v15 != None and v14 == None: #just blue dot
        v16 = (v15 + field.enemy_goal.down) / 2
        field.strategy_image.draw_line(field.enemy_goal.down,v15)
        return True
    elif v15 != None and v14 != None:
        v16 = (v14 + field.enemy_goal.up) /2
        v17 = (v15 + field.enemy_goal.down) /2
        if (v16-field.enemy_goal.up).mag() > (v17-field.enemy_goal.down).mag():
            return True
        else:   
            return True
    else:
        v14 = aux.get_line_intersection(field.enemy_goal.up,field.enemy_goal.down,point,v12,'LR' )
        v15 = aux.get_line_intersection(field.enemy_goal.up,field.enemy_goal.down,point,v13,'LR' )
        if v14 == None or v15 == None or (v14.y <= -400 and v15.y <= -400) or (v14.y >= 400 and v15.y >= 400):
            return True
        else:
            return False

        
def closest_point(field: fld.Field,at,enemy,point):
    b = 0
    for i in range(0,len(field.active_enemies(True))):
        if aux.dist(field.allies[at].get_pos(),point) < 1200 and aux.dist(field.active_enemies(True)[i].get_pos(),point) > 400:
            b = b
        else:
            b+=1
    if b >=1 :
        return False
    else:
        return True

    
def heatmap(field: fld.Field,at,enemy_df,enemy_gk):
    m_p = None
    m = 1000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
    for x in range(-const.FIELD_DX,const.FIELD_DX,50):
        for y in range(-const.FIELD_DY,const.FIELD_DY,50):
            if aux.is_point_inside_circle(aux.Point(x,y),field.allies[at].get_pos(),1200):      
                if clean_goal(field,enemy_gk,aux.Point(x,y)) and closest_point(field,at,enemy_df,aux.Point(x,y)):
                    field.strategy_image.draw_circle(aux.Point(x,y),(0,255,0),10)
                    if aux.dist(aux.Point(x,y),field.allies[at].get_pos()) < m:
                        m_p = aux.Point(x,y)
                        m = aux.dist(aux.Point(x,y),field.allies[at].get_pos())
                elif closest_point(field,at,enemy_df,aux.Point(x,y)):
                    field.strategy_image.draw_circle(aux.Point(x,y),(200,55,0),10)
                else:
                    field.strategy_image.draw_circle(aux.Point(x,y),(255,0,0),10)
            else:
                continue
    field.strategy_image.draw_circle(m_p,(0,0,255),20)
    return m_p


