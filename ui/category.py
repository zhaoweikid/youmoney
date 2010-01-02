# coding: utf-8
import os, sys
import pprint, types
import logfile

class TreeNode:
    def __init__(self, parent, name, id):
        self.parent = parent 
        self.name = name
        self.id   = id
        self.childs = []
        self.count  = 0
        self.num    = 0.0

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
        print self.name, self.num
        for ch in self.childs:
            print '  '+ch.name, ch.num
            for ch2 in ch.childs:
                print '    '+ch2.name, ch2.num
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
        
        self.payout_catemap = {}
        self.income_catemap = {}
        
        self.payout_parent = {}
        self.income_parent = {}
        
        # parent and children text list
        self.payout_catelist = []
        self.income_catelist = []
        
        # only parent text list
        self.payout_parentlist = []
        self.income_parentlist = []
        
        # parent children relation. eg: {parent1: set([child1, child2,...]), parent2:set(), ...}
        self.payout_rela = {}
        self.income_rela = {}

        self.payout_tree = TreeNode(None, _('payout'), 0)
        self.income_tree = TreeNode(None, _('income'), 0)

        self.init()

    def init(self):
        cates = [{}, {}]
        # 统计出分类映射表
        for row in self.category_rec:
            if row['type'] == 0:
                self.payout_catemap[row['name']] = row['id']
                self.payout_catemap[row['id']]   = row['name']
                self.payout_parent[row['id']]    = row['parent']        
                self.payout_parent[row['name']]  = row['parent']        

                cates[0][row['name']] = [0, 0]
            elif row['type'] == 1:
                self.income_catemap[row['name']] = row['id']
                self.income_catemap[row['id']]   = row['name']
                self.income_parent[row['id']]    = row['parent']        
                self.income_parent[row['name']]  = row['parent']        

                cates[1][row['name']]  = [0, 0]

        #print 'payout_catemap:', self.payout_catemap
        #print 'income_catemap:', self.income_catemap
        #print 'payout_parent:', self.payout_parent
        #print 'income_parent:', self.income_parent
        
        parentitem = [set(), set()]
        for row in self.category_rec:
            if row['type'] == 0:
                if row['parent'] == 0: 
                    self.payout_catelist.append(row['name'])

                    self.payout_rela[row['name']] = set()
                    self.payout_tree.add_child(TreeNode(self.payout_tree, row['name'], row['id']))

                    self.payout_parentlist.append(row['name'])
                else:
                    parentstr = self.payout_catemap[row['parent']]
                    self.payout_catelist.append('%s->%s' % (parentstr, row['name']))
                    parentitem[0].add(parentstr)
                        
                    self.payout_rela[parentstr].add(row['name'])
                    node = self.payout_tree.find(parentstr)
                    if node:
                        node.add_child_name(row['name'], row['id'])

            elif row['type'] == 1:
                if row['parent'] == 0: 
                    self.income_catelist.append(row['name'])
                    
                    self.income_rela[row['name']] = set()
                    self.income_tree.add_child_name(row['name'], row['id'])
                    self.income_parentlist.append(row['name'])
                else:
                    parentstr = self.income_catemap[row['parent']]
                    self.income_catelist.append('%s->%s' % (parentstr, row['name']))
                    parentitem[1].add(parentstr)

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
            cate = row['category']
            if row['type'] == 0:
                catestr = self.payout_catemap[cate]
            else:
                catestr = self.income_catemap[cate]
            x = cates[row['type']][catestr] 
            x[0] += 1
            x[1] += row['num']

        #pprint.pprint(cates)

        for k in cates[0]: 
            p = self.payout_parent[k]
            #print 'parent:', k, p
            if p > 0:
                v1 = cates[0][k]
                vv = cates[0][self.payout_catemap[p]]
                vv[0] += v1[0]
                vv[1] += v1[1]

        #pprint.pprint(cates)

        for k in cates[1]: 
            p = self.income_parent[k]
            if p > 0:
                v1 = cates[1][k]
                vv = cates[1][self.income_catemap[p]]
                vv[0] += v1[0]
                vv[1] += v1[1]
        
        #pprint.pprint(cates)
       
        total = 0
        for k in cates[0]:
            v = cates[0][k]
            node = treenode_find(self.payout_tree, k)
            if node:
                node.count = v[0]
                node.num   = v[1]
                if not node.childs:
                    total += v[1]
            #self.payout_tree.echo()
        self.payout_tree.num = total

        #self.payout_tree.echo()
        
        total = 0
        for k in cates[1]:
            node = None
            v = cates[1][k]
            node = treenode_find(self.income_tree, k)
            if node:
                node.count = v[0]
                node.num   = v[1]
                if not node.childs:
                    total += v[1]
        self.income_tree.num = total
        #self.income_tree.echo()


    def catelist(self, ctype=None):
        if ctype is None:
            return {_('payout'):self.payout_catelist, _('income'):self.income_catelist}
        elif ctype == 'payout':
            return self.payout_catelist
        elif ctype == 'income':
            return self.income_catelist
        return None


   
    def catelist_parent(self):
        return {_('payout'):self.payout_parentlist, _('income'):self.income_parentlist}

    def parentcate(self, catype):
        if type(catype) == types.IntType:
            if catype == 0:
                castr = 'payout'
            else:
                castr = 'income'


    def catestr_by_id(self, catype, name):
        if type(catype) == types.IntType:
            if catype == 0:
                castr = 'payout'
            else:
                castr = 'income'
        else:
            castr = catype
        
        parent_dict  = getattr(self, castr + '_parent')
        catemap_dict = getattr(self, castr + '_catemap')
        p = parent_dict[name]
        if p == 0:
            return catemap_dict[name]
        else:
            return catemap_dict[p] + '->' + catemap_dict[name] 
    
    def catemap(self, catype, name):
        if type(catype) == types.IntType:
            if catype == 0:
                castr = 'payout'
            else:
                castr = 'income'
        else:
            castr = catype
 
        catemap_dict = getattr(self, castr + '_catemap')
        return catemap_dict[name]
        

    def cate_subs(self, catype, name):
        if type(catype) == types.IntType:
            if catype == 0:
                castr = 'payout'
            else:
                castr = 'income'
        else:
            castr = catype
        catemap_dict = getattr(self, castr + '_catemap')
        if type(name) == types.IntType:
            logfile.info('cate subs, name:', name)
            namestr = catemap_dict[name]
        else:
            namestr = name
        rela_dict  = getattr(self, castr + '_rela')
        logfile.info('cate subs, namestr:', namestr)
        ret = rela_dict[namestr]
        if rela_dict:
            return [ str(catemap_dict[k]) for k in ret ]
        return [namestr]



