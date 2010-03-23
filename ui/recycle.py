# coding: utf-8
import os, sys
import storage
import datetime, time

class RecordCycle:
    def __init__(self, db):
        self.db = db
        self.checkfunc = {1:self.check_weekday, 2:self.check_weekend, 3:self.check_everyday,
                          4:self.check_weekly, 5:self.check_monthly}
        self.addfunc = {1:self.add_weekday, 2:self.add_weekend, 3:self.add_everyday,
                        4:self.add_weekly, 5:self.add_monthly}


           
    def cycle(self, cid=None):
        if cid:
            sql = "select * from recycle where id=" + str(cid)
        else:
            sql = "select * from recycle"
        datas = self.db.query(sql, True)
        if not datas:
            return 0

        changes = 0
        daynow = datetime.date.today()
    
        for data in datas:
            lasttime = data['lasttime']
            if lasttime == 0:
                lasttime = data['ctime']
            datestart = datetime.date.fromtimestamp(lasttime) 
            #dateck = datestart + datetime.timedelta(1)
            dateck = datestart
            addtime = data['addtime']

            cycleitems = {} 
            tm = int(time.mktime(datestart.timetuple()))
            sql = "select id,cycle,ctime from capital where cycle>0 and ctime>%d" % (tm)
            ret = self.db.query(sql, False)
            if ret:
                for row in ret:
                    x = datetime.date.fromtimestamp(row[2])
                    k = str(x) + '_' + str(row[1])
                    cycleitems[k] = row[0]

            while True:
                if dateck > daynow:
                    break
                #print 'check:', data['id'], addtime, dateck, daynow
                k = str(dateck)
                ck = k + '_' + str(data['id'])
                if not self.checkfunc[addtime](dateck):
                    dateck = self.addfunc[addtime](dateck)
                    continue

                if ck not in  cycleitems:
                    #print 'cycle add:', ck
                    sql = "insert into capital(category,num,ctime,year,month,day,payway,type,cycle,explain) values (?,?,?,?,?,?,?,?,?,?)"
                    self.db.execute_param(sql, (data['category'], data['num'], int(time.time()), 
                            dateck.year, dateck.month, dateck.day,
                            data['payway'], data['type'], data['id'], data['explain'],))
                    sql = "update recycle set lasttime=%d" % (int(time.time()))
                    self.db.execute(sql)
                    changes += 1

                dateck = self.addfunc[addtime](dateck)
        
        return changes

    def check_weekday(self, datenow):
        if datenow.weekday() < 5:
            return True
        return False

    def add_weekday(self, datenow):
        if datenow.weekday() < 4:
            return datenow + datetime.timedelta(1)
        return datenow + datetime.timedelta(7 - datenow.weekday())

    def check_weekend(self, datenow):
        if datenow.weekday() >= 5:
            return True
        return False

    def add_weekend(self, datenow):
        wd = datenow.weekday()
        if wd == 5:
            return datenow + datetime.timedelta(1)
        if wd == 6:
            return datenow + datetime.timedelta(6)

        i = 5 - wd
        return datenow + datetime.timedelta(i)
    
    def check_everyday(self, datenow):
        return True

    def add_everyday(self, datenow):
        return datenow + datetime.timedelta(1)

    def check_weekly(self, datenow):
        if datenow.weekday() == 0:
            return True
        return False

    def add_weekly(self, datenow):
        return datenow + datetime.timedelta(7 - datenow.weekday())

    def check_monthly(self, datenow):
        if datenow.day == 1:
            return True
        return False

    def add_monthly(self, datenow):
        y = datenow.year
        m = datenow.month
        
        m += 1
        if m > 12:
            y += 1
            m = 1
        return datetime.date(y, m, 1) 


if __name__ == '__main__':
    rc = RecordCycle(None)


