import matplotlib.pyplot as plt
from PIL import Image
import numpy as np
import itertools
import random
import queue
import os

# Constans
TILES_PATH = 'tiles'
RULES_PATH = 'rules.csv'
WAVE_WIDTH = 4
WAVE_HEIGHT = 4
TILE_SIZE = 16

# Structures
class Superposition:
  def __init__(self, possible_states):
    self.possible_states = possible_states
    self.is_collapsed = False

class Rule:
  def __init__(self, img):
    self.img = img
    self.top_allowed = set()
    self.right_allowed = set()
    self.bottom_allowed = set()
    self.left_allowed = set()

# Read rules from file
rules = []

with open(RULES_PATH, encoding = 'utf-8') as f:
    rules_csv = [line.replace('\n','').split(';') for line in f.readlines()]
    
for rule_csv in rules_csv:
    rule = Rule(Image.open(TILES_PATH + '/' + rule_csv[0]))
    rule.top_allowed = set([idx for idx, rule_csv_2 in enumerate(rules_csv) if (rule_csv_2[3] == rule_csv[1])])
    rule.right_allowed = set([idx for idx, rule_csv_2 in enumerate(rules_csv) if (rule_csv_2[4] == rule_csv[2])])
    rule.bottom_allowed = set([idx for idx, rule_csv_2 in enumerate(rules_csv) if (rule_csv_2[1] == rule_csv[3])])
    rule.left_allowed = set([idx for idx, rule_csv_2 in enumerate(rules_csv) if (rule_csv_2[2] == rule_csv[4])])
    rules.append(rule)

# Create wave in superposition and start observing it
wave = [[Superposition(range(len(rules))) for j in range(WAVE_WIDTH)] for i in range(WAVE_HEIGHT)]

while True:
    # Find state to collapse
    not_collapsed = [
        superposition for superposition in sum(wave, [])
        if (not superposition.is_collapsed)
    ]
    
    least_entropy = min([len(superposition.possible_states) for superposition in not_collapsed])
    
    least_entropy_superpositions = [
        superposition for superposition in not_collapsed
        if (len(superposition.possible_states) == least_entropy)
    ]
    
    # Collapse
    superposition_to_collapse = random.choice(least_entropy_superpositions)
    random_state = random.choice(tuple(superposition_to_collapse.possible_states))
    superposition_to_collapse.possible_states = set([random_state])
    superposition_to_collapse.is_collapsed = True
    
    # Stop completely collapsed
    is_completely_collapsed = all(
        wave[y][x].is_collapsed
        for y, x in itertools.product(range(WAVE_HEIGHT), range(WAVE_WIDTH))
    )
    
    if is_completely_collapsed:
        break
    
    # Propagate
    _open = queue.Queue()
    _close = set()
    
    for y, row in enumerate(wave):
        if superposition_to_collapse in row:
            _open.put((y, row.index(superposition_to_collapse)))
    
    while not _open.empty():
        current_position = _open.get()
        _close.add(current_position)
        y = current_position[0]
        x = current_position[1]
        
        if not wave[y][x].is_collapsed:
            possible_states_from_top = [
                list(rules[possible_state].bottom_allowed) for possible_state in wave[y+1][x].possible_states
            ] if y + 1 < WAVE_HEIGHT else [[i] for i in range(len(rules))]
            possible_states_from_top = sum(possible_states_from_top, [])
            possible_states_from_top = set(possible_states_from_top)
            
            possible_states_from_right = [
                list(rules[possible_state].left_allowed) for possible_state in wave[y][x+1].possible_states
            ] if x + 1 < WAVE_WIDTH else [[i] for i in range(len(rules))]
            possible_states_from_right = sum(possible_states_from_right, [])
            possible_states_from_right = set(possible_states_from_right)
            
            possible_states_from_bottom = [
                list(rules[possible_state].top_allowed) for possible_state in wave[y-1][x].possible_states
            ] if y - 1 >= 0 else [[i] for i in range(len(rules))]
            possible_states_from_bottom = sum(possible_states_from_bottom, [])
            possible_states_from_bottom = set(possible_states_from_bottom)
            
            possible_states_from_left = [
                list(rules[possible_state].right_allowed) for possible_state in wave[y][x-1].possible_states
            ] if x - 1 >= 0 else [[i] for i in range(len(rules))]
            possible_states_from_left = sum(possible_states_from_left, [])
            possible_states_from_left = set(possible_states_from_left)

            wave[y][x].possible_states = set.intersection(
                possible_states_from_top,
                possible_states_from_right,
                possible_states_from_bottom,
                possible_states_from_left
            )
        
        if y + 1 < WAVE_HEIGHT and (y+1, x) not in _close:
            _open.put((y+1, x))
        if x + 1 < WAVE_WIDTH and (y, x+1) not in _close:
            _open.put((y, x+1))
        if y - 1 >= 0 and (y-1, x) not in _close:
            _open.put((y-1, x))
        if x - 1 >= 0 and (y, x-1) not in _close:
            _open.put((y, x-1))

# Display generated image
result_img = Image.new('RGB', (TILE_SIZE * WAVE_WIDTH, TILE_SIZE * WAVE_HEIGHT))

for y, x in itertools.product(range(WAVE_HEIGHT), range(WAVE_WIDTH)):
    tile_img = rules[wave[WAVE_HEIGHT - y - 1][x].possible_states.pop()].img
    result_img.paste(tile_img, (x * TILE_SIZE, y * TILE_SIZE))

plt.imshow(result_img)
plt.show()