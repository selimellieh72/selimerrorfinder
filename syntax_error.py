class SyntaxError:
    def __init__(self, error_type, fix_func = lambda : False, is_fixable = True):
        self.error_type = error_type
        self.fix = fix_func
        self.is_fixable = is_fixable