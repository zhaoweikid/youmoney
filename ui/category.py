# coding: utf-8
import os, sys
import datetime
import pprint, types
import logfile

class TreeNode:
    def __init__(self, parent, name, id):
        self.parent = parent 
        self.name = name
        self.id   = id
        self.childs = []
        self.count  = 0
        #self.num    = 0.0
        self.month_num    = 0.0
        self.day_num = 0.0

    def add_child(self, child):
        self.childs.append(child)
    
    def add_child_name(self, name, id):
        self.childs.append(TreeNode(self, name, id))

    def find(self, name):
        for ch in self.childs:
            if ch.name == name:
                return ch
        return None

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    def echo(self):
        print '--------------------' 
        print self.name, self.month_num, self.day_num
        for ch in self.childs:
            print '  '+ch.name, ch.month_num, ch.day_month
            for ch2 in ch.childs:
                print '    '+ch2.name, ch2.month_num, ch2.day_month
        print '--------------------' 

def treenode_find(treenode, name):
    #print 'node name:', treenode.name, 'name:', name
    if treenode.name == name:
        return treenode

    for ch in treenode.childs:
        ret = treenode_find(ch, name)
        if ret:
            return ret
    
    return None 

class Category:
    def __init__(self, caterec, rec):
        self.category_rec = caterec
        self.data_rec = rec
       

        # parent and children map , [xx->xx: 1, xx2->xx2: 2...]
        self.payout_catemap = {}
        self.income_catemap = {}
        
        # id: name
        self.idmap = {}
       
        # parent id: parent name, all category 
        self.payout_parent_catemap = {}
        self.income_parent_catemap = {}
        # cate's parent id, child id to parent id
        self.payout_parent = {}
        self.income_parent = {}
        
        # parent and children text list, [xx->xx, ...]
        self.payout_catelist = []
        self.income_catelist = []
        
        # only parent text list, [xx, ...]
        self.payout_parentlist = []
        self.income_parentlist = []
        
        # parent children relation. eg: {parent1: set([child1, child2,...]), parent2:set(), ...}
        self.payout_rela = {}
        self.income_rela = {}

        self.payout_tree = TreeNode(None, _('payout'), 0)
        self.income_tree = TreeNode(None, _('income'), 0)
   
        self.types = {0: 'payout', 1: 'income', 'payout': 'payout', 'income': 'income'}

        self.init()

    def init(self):
        # count, month_num, day_num
        cates = [{}, {}]
        tday = datetime.date.today()
        # 统计出分类映射表
        for row in self.category_rec:
            self.idmap[row['id']] = row['name']

            if row['type'] == 0:
                #self.payout_catemap[row['name']] = row['id']
                #self.payout_catemap[row['id']]   = row['name']
                self.payout_parent[row['id']]    = row['parent']        
                #self.payout_parent[row['name']]  = row['parent']        

                #cates[0][row['name']] = [0, 0, 0]

                if row['parent'] == 0:
                    self.payout_parent_catemap[row['id']]   = row['name']
                    self.payout_parent_catemap[row['name']] = row['id']

            elif row['type'] == 1:
                #self.income_catemap[row['name']] = row['id']
                #self.income_catemap[row['id']]   = row['name']
                self.income_parent[row['id']]    = row['parent']        
                #self.income_parent[row['name']]  = row['parent']        

                #cates[1][row['name']]  = [0, 0, 0]

                if row['parent'] == 0:
                    self.income_parent_catemap[row['id']]   = row['name']
                    self.income_parent_catemap[row['name']] = row['id']


        #print 'payout_catemap:', self.payout_catemap
        #print 'income_catemap:', self.income_catemap
        #print 'payout_parent:', self.payout_parent
        #print 'income_parent:', self.income_parent
        
        parentitem = [set(), set()]
        for row in self.category_rec:
            if row['type'] == 0:
                if row['parent'] == 0: 
                    self.payout_catelist.append(row['name'])
                    self.payout_catemap[row['name']] = row['id']
                    self.payout_catemap[row['id']] = row['name']

                    self.payout_rela[row['name']] = set()
                    self.payout_tree.add_child(TreeNode(self.payout_tree, row['name'], row['id']))

                    self.payout_parentlist.append(row['name'])

                    cates[0][row['name']] = [0, 0, 0]
                else:
                    parentstr = self.payout_parent_catemap[row['parent']]
                    s = '%s->%s' % (parentstr, row['name'])
                    self.payout_catelist.append(s)
                    self.payout_catemap[s] = row['id']
                    self.payout_catemap[row['id']] = s

                    parentitem[0].add(parentstr)
                        
                    cates[0][s] = [0, 0, 0]

                    self.payout_rela[parentstr].add(row['name'])
                    node = self.payout_tree.find(parentstr)
                    if node:
                        node.add_child_name(row['name'], row['id'])

            elif row['type'] == 1:
                if row['parent'] == 0: 
                    self.income_catelist.append(row['name'])
                    self.income_catemap[row['name']] = row['id']
                    self.income_catemap[row['id']] = row['name']
  
                    self.income_rela[row['name']] = set()
                    self.income_tree.add_child_name(row['name'], row['id'])
                    self.income_parentlist.append(row['name'])
                    cates[1][row['name']]  = [0, 0, 0]
                else:
                    parentstr = self.income_parent_catemap[row['parent']]
                    s = '%s->%s' % (parentstr, row['name'])
                    self.income_catelist.append(s)
                    self.income_catemap[s] = row['id']
                    self.income_catemap[row['id']] = s

                    parentitem[1].add(parentstr)

                    cates[1][s]  = [0, 0, 0]

                    self.income_rela[parentstr].add(row['name'])
                    node = self.income_tree.find(parentstr)
                    if node:
                        node.add_child_name(row['name'], row['id'])

        #print 'payout_rela:', self.payout_rela
        #print 'income_rela:', self.income_rela
        
        for k in parentitem[0]:
            self.payout_catelist.remove(k)

        for k in parentitem[1]:
            self.income_catelist.remove(k)
        
        # compute num
        #print 'data:', self.data_rec
        #pprint.pprint(self.payout_rela)
        for row in self.data_rec:
            cateid = row['category']
            if row['type'] == 0:
                catestr = self.payout_catemap[cateid]
            else:
                catestr = self.income_catemap[cateid]
            #print 'catestr:', catestr
            x = cates[row['type']][catestr] 
            x[0] += 1
            x[1] += row['num']
            if row['day'] == tday.day:
                x[2] += row['num']

        #pprint.pprint(cates)

        for k in cates[0]: 
            pos = k.find('->')
            #p = self.payout_parent[k]
            #print 'parent:', k, p
            if pos > 0:
                p = k[:pos]
                v1 = cates[0][k]
                vv = cates[0][p]
                vv[0] += v1[0]
                vv[1] += v1[1]
                vv[2] += v1[2]

        #pprint.pprint(cates)

        for k in cates[1]: 
            pos = k.find('->')
            #p = self.income_parent[k]
            if pos > 0:
                p = k[:pos]
                v1 = cates[1][k]
                vv = cates[1][p]
                vv[0] += v1[0]
                vv[1] += v1[1]
                vv[2] += v1[2]
        
        #pprint.pprint(cates)
       
        mtotal = 0
        dtotal = 0
        for k in cates[0]:
            v = cates[0][k]
            node = treenode_find(self.payout_tree, k)
            if node:
                node.count = v[0]
                node.month_num = v[1]
                node.day_num   = v[2]
                if not node.childs:
                    mtotal += v[1]
                    dtotal += v[2]
            #self.payout_tree.echo()
        self.payout_tree.month_num = mtotal
        self.payout_tree.day_num = dtotal

        #self.payout_tree.echo()
        
        mtotal = 0
        dtotal = 0
        for k in cates[1]:
            node = None
            v = cates[1][k]
            node = treenode_find(self.income_tree, k)
            if node:
                node.count = v[0]
                node.month_num = v[1]
                node.day_num   = v[2]
                if not node.childs:
                    mtotal += v[1]
                    dtotal += v[2]
        self.income_tree.month_num = mtotal
        self.income_tree.day_num = dtotal
        #self.income_tree.echo()


    def catelist(self, ctype=None):
        '''所有类别的列表, 每项为 parent->child'''
        if ctype is None:
            return {_('Payout'):self.payout_catelist, _('Income'):self.income_catelist}
        elif ctype == 'payout' or ctype == 0:
            return self.payout_catelist
        elif ctype == 'income' or ctype == 1:
            return self.income_catelist
        return None
   
    def catelist_parent(self):
        '''所有一级类别列表'''
        return {_('Payout'):self.payout_parentlist, _('Income'):self.income_parentlist}

    
    def parent_cate_id(self, catype, name):
        '''查询某项类别的父类id'''
        castr = self.types[catype]
        parent_dict  = getattr(self, castr + '_parent')

        if type(name) != types.IntType:
            catemap_dict  = getattr(self, castr + '_catemap')
            return parent_dict[catemap_dict[name]]
        return parent_dict[name]


    def parent_cate_name(self, catype, name):
        '''查询某项类别的父类名'''
        castr = self.types[catype]
        parent_dict  = getattr(self, castr + '_parent')
        catemap_dict = getattr(self, castr + '_catemap')
 
        if type(name) != types.IntType:
            cid = parent_dict[catemap_dict[name]]
        else:
            cid = name
         
        p = parent_dict[cid]
        if p == 0:
            return ''
        else:
            return catemap_dict[p]

    def catestr_by_id(self, catype, cid):
        '''根据id查询名字，名字形式为 parent->child'''
        castr = self.types[catype]
        catemap_dict = getattr(self, castr + '_catemap')
        return catemap_dict[cid]

    def catemap(self, catype, name):
        '''根据id或parent->child互查'''
        castr = self.types[catype]
        catemap_dict = getattr(self, castr + '_catemap')
        return catemap_dict[name]

    def catemap_by_id(self, catype, cid):
        return catestr_by_id(catype, cid)

    def cate_subs_id(self, catype, name):
        castr = self.types[catype]
        catemap_dict = getattr(self, castr + '_catemap')
        if type(name) == types.IntType:
            namestr = self.idmap[name]
        else:
            namestr = name
        rela_dict  = getattr(self, castr + '_rela')
        ret = rela_dict[namestr]

        if ret:
            return [ catemap_dict[namestr + '->' + k] for k in ret ]
        return [catemap_dict[namestr]]



