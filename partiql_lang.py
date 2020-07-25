from lark import Lark
import lark

class Build_AST():
    def __default__(self, tree):
        raise

    def visit(self, tree):
        f = getattr(self, tree.data, self.__default__)
        return f(tree)

    def select(self, tree) :
        ret_expr = ["select"]
        # project
        prj_expr = self.visit(tree.children[0])
        list_expr = ["list"]
        # flattening project list
        for s in prj_expr :
            list_expr.append(s)
        ret_expr.append(["project", list_expr])
        # from
        ret_expr.append(self.visit(tree.children[1]))
        # where
        if len(tree.children) == 3 :
            ret_expr.append(self.visit(tree.children[2]))
            
        return ret_expr
    
    def project(self, tree) :
        ret_expr = []
        for c in tree.children :
            s = self.visit(c)
            # project case: flatten
            if c.data == "project" :
                for ss in s :
                    ret_expr.append(ss)
            # column case
            else :
                ret_expr.append(s)
        return ret_expr

    def column(self, tree) :
        return  self.visit(tree.children[0])

    def path(self, tree) :
        # now only 2 step path is supported (pattern: id.id)
        return ['path', self.visit(tree.children[0]), self.visit(tree.children[1])]

    def call(self, tree) :
        # flattening parameter list
        list_expr = ["list"]
        for s in self.visit(tree.children[1]) :
            list_expr.append(s)
        return ['call', self.visit(tree.children[0]), list_expr]
    
    def name_symbol(self, tree) :
        ret_str = ""
        for c in tree.children :
            if type(c) == lark.lexer.Token :
                ret_str = ret_str + c
            elif type(c) == lark.tree.Tree :
                ret_str = ret_str + self.visit(c)
        return ret_str

    def parameters(self, tree) :
        ret = []
        for c in tree.children :
            s = self.visit(c)
            # project case: flatten
            if c.data == "parameters" :
                for ss in s :
                    ret.append(ss)
            # column case
            else :
                ret.append(s)
        return ret

    def from_(self, tree) :
        return ['from', self.visit(tree.children[0])]
    
    def source_exprs(self, tree) :
        if len(tree.children) == 1 :
            ret = self.visit(tree.children[0])
        # JOIN case : only inner join supported
        else :
            ret = ['inner_join', self.visit(tree.children[0]), self.visit(tree.children[1])]
        return ret

    def source_expr(self, tree) :
        # no as clause
        if len(tree.children) == 1 :
            ret = ['as', self.visit(tree.children[0])[1], self.visit(tree.children[0])]
        # with as clause
        else :
            ret =['as', self.visit(tree.children[1]), self.visit(tree.children[0])]
        return ret
    
    def as_(self, tree) :
        return self.visit(tree.children[0])
    
    def where(self, tree) :
        return ['where', self.visit(tree.children[0])]
    
    def cond_expr(self, tree) :
        ret = []
        left = self.visit(tree.children[0])
        op =  self.visit(tree.children[1])
        # right may be token
        if type(tree.children[2]) == lark.lexer.Token :
            right = tree.children[2]
        elif type(tree.children[2]) == lark.tree.Tree :
            right = self.visit(tree.children[2])
        return [op, left, right]

    def cond_exprs(self, tree) :
        ret = []
        # con conjunction(and, or)
        if len(tree.children) == 1:
            ret = self.visit(tree.children[0])
        # 'and' or 'or' case
        else :
            left = self.visit(tree.children[0])
            con =  self.visit(tree.children[1])
            right = self.visit(tree.children[2])
            ret = [con, left, right]
        return ret

    def lit(self, tree) :
        return ['lit', self.visit(tree.children[0])]

    def const_str(self, tree) :
        ret_str = ""
        for c in tree.children :
            if type(c) == lark.lexer.Token :
                ret_str = ret_str + c
            elif type(c) == lark.tree.Tree :
                ret_str = ret_str + self.visit(c)
        return "'" + ret_str + "'"

    def number(self, tree) :
        return int(tree.children[0] + "")

    # operators and digits
    def op(self, tree) :
        return self.visit(tree.children[0])
    def eq(self, tree) :
        return "="
    def gt(self, tree) :
        return ">"
    def lt(self, tree) :
        return "<"
    def ge(self, tree) :
        return ">="
    def le(self, tree) :
        return "<="
    def u_bar(self, tree) :
        return "_"

    # conjunctions
    def and_(self, tree) :
        return "and"
    def or_(self, tree) :
        return "or"

    # identifiers
    def id(self, tree) :
        return ["id", self.visit(tree.children[0])]

