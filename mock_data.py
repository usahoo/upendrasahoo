#!/usr/bin/env python3
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, User, Category, Item

engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

baseball = Category(name='Baseball')
basketball = Category(name='Basketball')
foosball = Category(name='Foosball')
frisbee = Category(name='Frisbee')
hockey = Category(name='Hockey')
rock_climbing = Category(name='Rock Climbing')
skating = Category(name='Skating')
snowboarding = Category(name='Snowboarding')
soccer = Category(name='Soccer')

session.add_all([baseball, basketball, foosball, frisbee, hockey,
                 rock_climbing, skating, snowboarding, soccer])
session.commit()

user = User(name='Upendra Sahoo', email='upendra.sahoo68@gmail.com')

session.add(user)
session.commit()

baseballs = Item(name='Baseball',
                 description=('Baseball is a bat-and-ball game played between '
                              'two opposing teams who take turns batting and '
                              'fielding. The game proceeds when a player on '
                              'the fielding team, called the pitcher, throws '
                              'a ball which a player on the batting team '
                              'tries to hit with a bat.'),
                 category_id=baseball.id,
                 user_id=user.id)

basketballs = Item(name='Basketball',
                   description=('Basketball is a team sport in which two '
                                'teams of five players, opposing one another '
                                'on a rectangular court, compete with the '
                                'primary objective of shooting a basketball '
                                'through the defenders hoop while preventing '
                                'the opposing team from shooting through '
                                'their own hoop.'),
                   category_id=basketball.id,
                   user_id=user.id)

foosballs = Item(name='Foosball',
                 description=('Table football or table soccer, foosball in '
                              'North America, is a table-top game that '
                              'is loosely based on football. The aim of the '
                              'game is to use the control knobs to '
                              'move the ball into the opponents goal.'),
                 category_id=foosball.id,
                 user_id=user.id)

frisbees = Item(name='Frisbee',
                description=('A frisbee is a gliding toy or sporting item '
                             'that is generally plastic and roughly 20 to '
                             '25 centimetres in diameter with a pronounced '
                             'lip. It is used recreationally and '
                             'competitively for throwing and catching, as in '
                             'flying disc games.'),
                category_id=frisbee.id,
                user_id=user.id)

hockeys = Item(name='Hockey',
               description=('Hockey is a sport in which two teams play '
                            'against each other by trying to maneuver a ball '
                            'or a puck into the opponents goal using a '
                            'hockey stick. There are many types of hockey '
                            'such as bandy, field hockey and ice hockey.'),
               category_id=hockey.id,
               user_id=user.id)

rockClimbing = Item(name='Rock Climbing',
                    description=('Rock climbing is an activity in which '
                                 'participants climb up, down or across '
                                 'natural rock formations or artificial rock '
                                 'walls. The goal is to reach the summit of '
                                 'a formation or the endpoint of a usually '
                                 'pre-defined route without falling.'),
                    category_id=rock_climbing.id,
                    user_id=user.id)

skates = Item(name='Skates',
              description=('A skateboard is a type of sports equipment used '
                           'primarily for the sport of skateboarding. It '
                           'usually consists of a specially designed '
                           'maplewood board combined with a polyurethane '
                           'coating used for making smoother slides and '
                           'stronger durability. Most skateboards are made '
                           'with 7 plies of this wood.'),
              category_id=skating.id,
              user_id=user.id)

snowboard = Item(name='Snowboard',
                 description=('Snowboarding is a recreational activity and '
                              'Olympic and Paralympic sport that involves '
                              'descending a snow-covered slope while '
                              'standing on a snowboard attached to a riders '
                              'feet. The development of snowboarding was '
                              'inspired by skateboarding, sledding, surfing '
                              'and skiing.'),
                 category_id=snowboarding.id,
                 user_id=user.id)

soccers = Item(name='Soccer',
               description=('Association football, more commonly known as '
                            'football or soccer, is a team sport played '
                            'between two teams of eleven players with a '
                            'spherical ball. It is played by 250 million '
                            'players in over 200 countries and dependencies '
                            'making it the worlds most popular sport.'),
               category_id=soccer.id,
               user_id=user.id)

session.add_all([baseballs, basketballs, foosballs, frisbees, hockeys,
                 rockClimbing, skates, snowboard, soccers])
session.commit()
