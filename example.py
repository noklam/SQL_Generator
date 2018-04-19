# Brian Ray <brianhray@gmail.com>
# @brianray
# https://medium.com/@brianray_7981/
# parser for POSH Syntax http://brianray.github.io/posh-syntax/
import re


def transition_skip(fsm_obj):
    pass


def transition_new_group(fsm_obj):
    fsm_obj.group_current_level += 1
    fsm_obj.current_group = RuleGroup(fsm_obj.current_group,
                                      fsm_obj.group_current_level,
                                      None)


def transition_append_pre(fsm_obj):
    rule_count = fsm_obj.current_group.rule_count
    fsm_obj.current_group.rules[rule_count - 1].prefix += fsm_obj.current_char


def transition_add_op(fsm_obj):
    rule_count = fsm_obj.current_group.rule_count
    fsm_obj.current_group.rules[rule_count - 1].op = fsm_obj.current_char


def transition_end_group(fsm_obj):
    fsm_obj.group_current_level += 1
    fsm_obj.current_group = RuleGroup(fsm_obj.current_group,
                                      fsm_obj.group_current_level,
                                      None)


def transition_end_rule(fsm_obj):
    pass


def transition_add_op_new_rule(fsm_obj):
    fsm_obj.current_group.rule_count += 1
    fsm_obj.current_group.rules.append(Rule())
    rule_count = fsm_obj.current_group.rule_count
    fsm_obj.current_group.rules[rule_count - 1].op = fsm_obj.current_char


def transition_append_subj(fsm_obj):
    rule_count = fsm_obj.current_group.rule_count
    fsm_obj.current_group.rules[rule_count - 1].subject += fsm_obj.current_char


def transition_add_op_new_group(fsm_obj):
    fsm_obj.current_group.op = fsm_obj.current_char


T_SKIP = transition_skip
T_NEW_GROUP = transition_new_group
T_APPEND_CHAR_PRE = transition_append_pre
T_ADD_OP = transition_add_op
T_ADD_OP_NEW_RULE = transition_add_op_new_rule
T_END_GROUP = transition_end_group
T_END_RULE = transition_end_rule
T_APPEND_CHAR_SUBJ = transition_append_subj
T_ADD_GROUP_OP = transition_add_op_new_group

S_NEW_GROUP = "STATE: NEW_GROUP"
S_END_GROUP = "STATE: END_GROUP"
S_PRE = "STATE: PREFIX"
S_OP = "STATE: OPERATOR"
S_END_RULE = "STATE: END_RULE"
S_SUBJ = "STATE: SUBJECT"


FSM_MAP = (
    #  {'src':, 'dst':, 'condition':, 'callback': },
    {'src': S_NEW_GROUP,
        'dst': S_PRE,
        'condition': "[A-Za-z|+|-|\d]",
        'callback': T_APPEND_CHAR_PRE},  # 1
    {'src': S_PRE,
        'dst': S_PRE,
        'condition': "[A-Za-z|+|-|\d]",
        'callback': T_APPEND_CHAR_PRE},  # 2
    {'src': S_PRE,
        'dst': S_SUBJ,
        'condition': "\(",
        'callback': T_SKIP},  # 3
    {'src': S_SUBJ,
        'dst': S_SUBJ,
        'condition': "[^\)]",
        'callback': T_APPEND_CHAR_SUBJ},  # 4
    {'src': S_SUBJ,
        'dst': S_END_RULE,
        'condition': "\)",
        'callback': T_END_RULE},  # 5
    {'src': S_END_RULE,
        'dst': S_END_GROUP,
        'condition': "\)",
        'callback': T_END_GROUP},  # 6
    {'src': S_END_RULE,
        'dst': S_OP,
        'condition': "[\&|\|]",
        'callback': T_ADD_OP_NEW_RULE},  # 7
    {'src': S_END_GROUP,
        'dst': S_OP,
        'condition': "[\&|\|]",
        'callback': T_ADD_GROUP_OP},  # 8
    {'src': S_OP,
        'dst': S_NEW_GROUP,
        'condition': "\(",
        'callback': T_NEW_GROUP},  # 9
    {'src': S_OP,
        'dst': S_PRE,
        'condition': "[A-Za-z|+|-|\d]",
        'callback': T_APPEND_CHAR_PRE},  # 10
    {'src': S_SUBJ,
        'dst': S_END_RULE,
        'condition': "\)",
        'callback': T_END_RULE})  # 11


for map_item in FSM_MAP:
    map_item['condition_re_compiled'] = re.compile(map_item['condition'])


class Rule:
    def __init__(self):
        self.prefix = ""
        self.subject = ""
        self.op = None

    def __repr__(self):
        op = self.op
        if not op:
            op = ''
        return "<Rule: {} {}({})>".format(op, self.prefix, self.subject)

class RuleGroup:
    def __init__(self, parent, level, op):
        self.op = op
        self.parent = parent
        self.level = level
        self.rule_count = 1
        self.rules = [Rule(), ]

    def __repr__(self):
        return "<RuleGroup: {}>".format(self.__dict__)


class Rule_Parse_FSM:

    def __init__(self, input_str):
        self.input_str = input_str
        self.current_state = S_NEW_GROUP
        self.group_current_level = 0
        self.current_group = RuleGroup(None, self.group_current_level, None)
        self.current_char = ''

    def run(self):
        for c in self.input_str:
            if not self.process_next(c):
                print("skip '{}' in {}".format(c, self.current_state))

    def process_next(self, achar):
        self.current_char = achar
        frozen_state = self.current_state
        for transition in FSM_MAP:
            if transition['src'] == frozen_state:
                if self.iterate_re_evaluators(achar, transition):
                    return True
        return False

    def iterate_re_evaluators(self, achar, transition):
        condition = transition['condition_re_compiled']
        if condition.match(achar):
            self.update_state(
                transition['dst'], transition['callback'])
            return True
        return False

    def update_state(self, new_state, callback):
        print("{} -> {} : {}".format(self.current_char,
                                     self.current_state,
                                     new_state))
        self.current_state = new_state
        callback(self)


example = "!AN(hellod) & AN(world )  "
fsm = Rule_Parse_FSM(example)
fsm.run()
print(fsm.current_group)
