import sqlalchemy as sqla
import json #only used for user import feature, please remove once that's done
from datetime import datetime, timedelta

import config

meta = sqla.MetaData()

class AlreadyAdded(Exception):
    pass

class MyDatabase:
    """Wrapper around sqlalchemy, to bundle objects together."""

    def __init__(self, filename):
        self.engine = sqla.create_engine('sqlite:///'+filename, echo = True, connect_args={"check_same_thread":False})
        
        #autoload=true in the table definition might save me from defining them every time
        #source: https://campus.datacamp.com/courses/introduction-to-relational-databases-in-python/basics-of-relational-databases?ex=9

        self.help_users = sqla.Table('help_users', meta, 
                            sqla.Column('id', sqla.Integer, primary_key = True), 
                            sqla.Column('user_id', sqla.Integer), 
                            )
        
        self.users = sqla.Table('users', meta,
                        sqla.Column('id', sqla.Integer, primary_key=True),
                        sqla.Column('user_id', sqla.Integer),
                        sqla.Column('is_admin',sqla.Integer),
                        sqla.Column('name', sqla.String),
                        sqla.Column('workweek_start', sqla.String),
                        )
        
        self.ponche = sqla.Table('ponche', meta,
                        sqla.Column('id', sqla.Integer, primary_key=True),
                        sqla.Column('user_id', sqla.Integer),
                        sqla.Column('timestamp', sqla.Integer),
                        )
        
        self.breaks = sqla.Table('breaks', meta,
                        sqla.Column('id', sqla.Integer, primary_key=True),
                        sqla.Column('user_id', sqla.Integer),
                        sqla.Column('start_time', sqla.Integer),
                        sqla.Column('expected_length', sqla.Integer),
                        sqla.Column('end_time', sqla.Integer),
                        sqla.Column('alarm_channel',sqla.Integer),
                        )

        self.scheduled_breaks = sqla.Table('scheduled_breaks', meta,
                        sqla.Column('id', sqla.Integer, primary_key=True),
                        sqla.Column('user_id', sqla.Integer),
                        sqla.Column('start_time', sqla.Integer),
                        sqla.Column('expected_length', sqla.Integer),
                        sqla.Column('weekday', sqla.Integer),
                        )
        
        meta.create_all(self.engine)
        self.conn=self.engine.connect()

    def unzip_results(self, result):
        # takes a result object, returns a list of dictionaries with each row and column
        d, a = {}, []
        for row in result:
            for column, value in row.items():
                d={**d, **{column:value}}
            a.append(d)
        return(a)

    def add_help_user(self, user_id):
        ins=self.help_users.insert().values(user_id=user_id)
        output=self.conn.execute(ins)
        return(output.inserted_primary_key)
        
    def remove_help_user(self, user_id):
        remove=self.help_users.delete().where(self.help_users.c.user_id==user_id)
        output=self.conn.execute(remove)
        return()

    def check_help_user(self, user_id):
        fetch=self.help_users.select().where(self.help_users.c.user_id==user_id)
        result=self.conn.execute(fetch)
        a=self.unzip_results(result)
        return(a)

    def get_help_users(self):
        fetch=self.help_users.select()
        result=self.conn.execute(fetch)
        a=self.unzip_results(result)
        return(a)




    def get_user(self, user_id, mention=False): #TODO: add check for only one result back
        fetch=self.users.select().where(self.users.c.user_id==user_id)
        result=self.conn.execute(fetch)
        a=self.unzip_results(result)
        return(a)

    def get_all_users(self):
        fetch=self.users.select()
        result=self.conn.execute(fetch)
        a=self.unzip_results(result)
        return(a)




    def register_user(self,input):
        input=json.loads(input)
        ins=self.users.insert().values(**input)
        output=self.conn.execute(ins)
        check=self.users.select().where(self.users.c.id==output.inserted_primary_key[0])
        result=self.conn.execute(check)
        a=self.unzip_results(result)
        return(a)


    def get_scheduled_breaks(self,user_id):
        raise Exception("function not yet implemented")
        return()

    def add_ponched_user(self, user_id, timestamp):
        #set the bounds for a complete day
        start_time=timestamp-(timestamp%86400)
        end_time=start_time+86400
        check_duplicate = self.ponche.select()\
                            .where(self.ponche.c.user_id == user_id)\
                            .where(self.ponche.c.timestamp > start_time)\
                            .where(self.ponche.c.timestamp < end_time)
        duplicate_result = self.conn.execute(check_duplicate)
        duplicate_result_list = self.unzip_results(duplicate_result)
        if duplicate_result_list:
            raise(AlreadyAdded("user is already added"))

        ins=self.ponche.insert().values(user_id=user_id, timestamp=timestamp)
        output=self.conn.execute(ins)
        return(output)


    def get_ponched_users(self, timestamp):
        #set the bounds for a complete day
        start_time=timestamp-(timestamp%86400)
        end_time=start_time+86400

        if config.verbose:
            print(str(start_time), " - ", str(end_time))
        
        check=self.ponche.select()\
                .where(self.ponche.c.timestamp > start_time)\
                .where(self.ponche.c.timestamp < end_time)
        result=self.conn.execute(check)
        a=self.unzip_results(result)
        return(a)


    def send_user_away(self, user_id, timestamp, expected_length, alarm_channel):
        ins=self.breaks.insert().values(user_id=user_id,
                                        start_time=timestamp,
                                        expected_length=expected_length,
                                        alarm_channel=alarm_channel
                                        )
        output=self.conn.execute(ins)

        check=self.breaks.select().where(self.breaks.c.id==output.inserted_primary_key[0])
        result=self.conn.execute(check)
        a=self.unzip_results(result)

        return(a)

    def bring_user_back(self, break_id, timestamp):
        update=self.breaks.update().values(end_time=timestamp).where(self.breaks.c.id==break_id)
        output=self.conn.execute(update)


        check=self.breaks.select().where(self.breaks.c.id==output.lastrowid)
        result=self.conn.execute(check)
        a=self.unzip_results(result)


        return(a)

    def get_breaks_from_today(self, timestamp):
        #set the bounds for a complete day
        start_time=timestamp-(timestamp%86400)
        end_time=start_time+86400

        if config.verbose:
            print(str(start_time), " - ", str(end_time))
        
        check=self.breaks.select()\
                .where(self.breaks.c.start_time > start_time)\
                .where(self.breaks.c.start_time < end_time)
        result=self.conn.execute(check)
        a=self.unzip_results(result)
        return(a)

    def get_current_breaks(self):
        if config.verbose:
            print(str(start_time), " - ", str(end_time))
        
        check=self.breaks.select().where(self.breaks.c.end_time == None)
        result=self.conn.execute(check)
        a=self.unzip_results(result)
        return(a)



db=MyDatabase('beta.db')
