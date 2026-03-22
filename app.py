import os
os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"
import streamlit as st
import math
from collections import Counter
import pandas as pd
import altair as alt

# Configure page
st.set_page_config(
    page_title="D&D Damage Calculator",
    page_icon="⚔️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================
# CALCULATOR FUNCTIONS
# ============================================

def ability_modifier(score: int) -> int:
    return (score - 10) // 2

def parse_dice(dice_str: str):
    dice_str = dice_str.lower().strip().replace(' ', '')
    if '+' in dice_str:
        parts = dice_str.split('+')
        bonus = int(parts[1])
        dice_part = parts[0]
    elif '-' in dice_str[1:]:
        idx = dice_str[1:].index('-') + 1
        bonus = -int(dice_str[idx+1:])
        dice_part = dice_str[:idx]
    else:
        dice_part = dice_str
        bonus = 0
    if 'd' not in dice_part:
        raise ValueError('Invalid dice expression')
    num, sides = dice_part.split('d')
    return [(int(num), int(sides))], bonus

def dice_distribution(num_dice: int, sides: int) -> Counter:
    dist = Counter({i: 1/sides for i in range(1, sides+1)})
    for _ in range(num_dice - 1):
        new_dist = Counter()
        for total1, prob1 in dist.items():
            for roll in range(1, sides+1):
                new_dist[total1 + roll] += prob1 * (1/sides)
        dist = new_dist
    return dist

def sum_distributions(dists: list, bonus: int = 0) -> Counter:
    if not dists:
        return Counter()
    total_dist = dists[0]
    for d in dists[1:]:
        new_total = Counter()
        for s1, p1 in total_dist.items():
            for s2, p2 in d.items():
                new_total[s1 + s2] += p1 * p2
        total_dist = new_total
    if bonus != 0:
        total_dist = Counter({k + bonus: v for k, v in total_dist.items()})
    return total_dist

def halved_distribution(dist: Counter) -> Counter:
    half = Counter()
    for total, prob in dist.items():
        half[total // 2] += prob
    return half

def saving_throw_failure_probability(save_modifier: int, dc: int, advantage: str = 'normal') -> float:
    threshold = dc - save_modifier - 1
    if threshold <= 0:
        single_p = 0.0
    elif threshold >= 20:
        single_p = 1.0
    else:
        single_p = threshold / 20.0
    
    if advantage == 'advantage':
        return single_p ** 2
    elif advantage == 'disadvantage':
        return 1.0 - (1.0 - single_p) ** 2
    else:
        return single_p

def compute_damage_distribution(dice_expr: str, save_modifier: int, dc: int, advantage: str = 'normal') -> Counter:
    dice_list, bonus = parse_dice(dice_expr)
    dists = [dice_distribution(num, sides) for num, sides in dice_list]
    full_dist = sum_distributions(dists, bonus)
    half_dist = halved_distribution(full_dist)
    p_fail = saving_throw_failure_probability(save_modifier, dc, advantage)
    p_success = 1 - p_fail
    combined = Counter()
    for dmg, prob in full_dist.items():
        combined[dmg] += prob * p_fail
    for dmg, prob in half_dist.items():
        combined[dmg] += prob * p_success
    return combined

def calculate_stats(dist: Counter) -> tuple:
    total_prob = sum(dist.values())
    if total_prob == 0:
        return 0, 0
    mean = sum(dmg * prob for dmg, prob in dist.items()) / total_prob
    variance = sum((dmg - mean) ** 2 * prob for dmg, prob in dist.items()) / total_prob
    std_dev = math.sqrt(variance)
    return mean, std_dev

def plot_distribution(dist: Counter, title: str = ''):
    xs = sorted(dist.keys())
    ys = [dist[x] for x in xs]
    mean, std_dev = calculate_stats(dist)
    
    df = pd.DataFrame({
        'Damage': xs,
        'Probability': ys
    })
    
    bars = alt.Chart(df).mark_bar(color='#4472C4').encode(
        x='Damage:Q',
        y='Probability:Q'
    )
    
    mean_line = alt.Chart(pd.DataFrame({'Mean': [mean]})).mark_vline(
        color='#FF6B6B', strokeDash=[5, 5]
    ).encode(x='Mean:Q')
    
    chart = (bars + mean_line).properties(
        width=600,
        height=300,
        title=title
    ).interactive()
    
    return chart

def compute_attack_damage_distribution(dice_expr: str, attack_bonus: int, ac: int, advantage: str = 'normal', crit_type: str = 'normal') -> tuple:
    dice_list, bonus = parse_dice(dice_expr)
    dists_normal = [dice_distribution(num, sides) for num, sides in dice_list]
    damage_normal = sum_distributions(dists_normal, bonus)
    
    if crit_type == 'crunchy':
        max_roll_bonus = sum(num * sides for num, sides in dice_list)
        damage_crit = sum_distributions(dists_normal, bonus + max_roll_bonus)
    else:
        dists_crit = [dice_distribution(2*num, sides) for num, sides in dice_list]
        damage_crit = sum_distributions(dists_crit, bonus)
    
    combined_on_hit = Counter()
    total_hit_prob = 0.0
    
    if advantage == 'normal':
        for roll in range(1, 21):
            if roll == 1:
                continue
            elif roll == 20:
                for dmg, prob in damage_crit.items():
                    combined_on_hit[dmg] += prob * (1 / 20.0)
                total_hit_prob += 1 / 20.0
            elif roll + attack_bonus >= ac:
                for dmg, prob in damage_normal.items():
                    combined_on_hit[dmg] += prob * (1 / 20.0)
                total_hit_prob += 1 / 20.0
                
    elif advantage == 'advantage':
        for roll1 in range(1, 21):
            for roll2 in range(1, 21):
                roll = max(roll1, roll2)
                if roll == 1:
                    continue
                elif roll == 20:
                    for dmg, prob in damage_crit.items():
                        combined_on_hit[dmg] += prob * (1 / 400.0)
                    total_hit_prob += 1 / 400.0
                elif roll + attack_bonus >= ac:
                    for dmg, prob in damage_normal.items():
                        combined_on_hit[dmg] += prob * (1 / 400.0)
                    total_hit_prob += 1 / 400.0
                    
    elif advantage == 'disadvantage':
        for roll1 in range(1, 21):
            for roll2 in range(1, 21):
                roll = min(roll1, roll2)
                if roll == 1:
                    continue
                elif roll == 20:
                    for dmg, prob in damage_crit.items():
                        combined_on_hit[dmg] += prob * (1 / 400.0)
                    total_hit_prob += 1 / 400.0
                elif roll + attack_bonus >= ac:
                    for dmg, prob in damage_normal.items():
                        combined_on_hit[dmg] += prob * (1 / 400.0)
                    total_hit_prob += 1 / 400.0
    
    if total_hit_prob > 0:
        avg_damage_on_hit, _ = calculate_stats(combined_on_hit)
        avg_damage_overall = total_hit_prob * avg_damage_on_hit
    else:
        avg_damage_on_hit = 0
        avg_damage_overall = 0
    
    return combined_on_hit, total_hit_prob, avg_damage_on_hit, avg_damage_overall

# ============================================
# UI LAYOUT
# ============================================

st.title("⚔️ D&D 5e Damage Calculator")
st.markdown("Calculate probability distributions for spell damage and attack roll damage")

tab1, tab2 = st.tabs(["🪄 Spell Damage (Saving Throw)", "⚔️ Attack Roll Damage"])

# ============================================
# SPELL TAB
# ============================================
with tab1:
    st.header("Spell Damage Calculator")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Enemy Ability Scores")
        abilities = ['Strength', 'Dexterity', 'Constitution', 'Intelligence', 'Wisdom', 'Charisma']
        ability_cols = st.columns(3)
        
        ability_scores = {}
        for i, ability in enumerate(abilities):
            col = ability_cols[i % 3]
            ability_scores[ability] = col.number_input(
                ability[:3], 
                value=10, 
                min_value=1, 
                max_value=30,
                key=f"spell_ability_{ability}"
            )
    
    with col2:
        st.subheader("Spell Parameters")
        selected_ability = st.selectbox(
            "Saving Throw Ability",
            abilities,
            index=1,
            key="spell_ability_select"
        )
        
        spell_dc = st.number_input("Spell DC", value=14, min_value=1, max_value=30, key="spell_dc")
        spell_bonus = st.number_input("Save Bonus", value=0, min_value=-5, max_value=10, key="spell_bonus")
        spell_dice = st.text_input("Damage Dice (e.g., 8d6)", value="8d6", key="spell_dice")
        spell_advantage = st.selectbox(
            "Saving Throw",
            ["Normal", "Advantage", "Disadvantage"],
            index=0,
            key="spell_advantage"
        )
    
    if st.button("Calculate Spell Damage", key="spell_calc_btn"):
        try:
            score = ability_scores[selected_ability]
            mod = ability_modifier(score) + spell_bonus
            dist = compute_damage_distribution(spell_dice, mod, spell_dc, spell_advantage.lower())
            mean, std_dev = calculate_stats(dist)
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Mean Damage", f"{mean:.2f}")
            with col2:
                st.metric("Std Deviation", f"{std_dev:.2f}")
            
            chart = plot_distribution(dist, f"Damage distribution for {spell_dice} vs DC {spell_dc} (save bonus {mod}, {spell_advantage})")
            st.altair_chart(chart, use_container_width=True)
            
        except ValueError as e:
            st.error(f"Error: {e}")

# ============================================
# ATTACK TAB
# ============================================
with tab2:
    st.header("Attack Roll Damage Calculator")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Attack Parameters")
        attack_ac = st.number_input("Enemy AC", value=15, min_value=1, max_value=30, key="attack_ac")
        attack_bonus = st.number_input("Attack Bonus", value=5, min_value=-5, max_value=15, key="attack_bonus")
    
    with col2:
        st.subheader("Damage Formula")
        attack_dice = st.text_input("Damage Dice (e.g., 1d8+5)", value="1d8+5", key="attack_dice")
        attack_advantage = st.selectbox(
            "Attack Roll",
            ["Normal", "Advantage", "Disadvantage"],
            index=0,
            key="attack_advantage"
        )
    
    col1, col2 = st.columns(2)
    with col1:
        crunchy_crits = st.checkbox("Crunchy Crits (add max roll instead of doubling)", value=False, key="crunchy")
    
    if st.button("Calculate Attack Damage", key="attack_calc_btn"):
        try:
            crit_type = 'crunchy' if crunchy_crits else 'normal'
            dist, p_hit, avg_on_hit, avg_overall = compute_attack_damage_distribution(
                attack_dice, attack_bonus, attack_ac, attack_advantage.lower(), crit_type
            )
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Hit Chance", f"{p_hit * 100:.1f}%")
            with col2:
                st.metric("Avg Damage (on hit)", f"{avg_on_hit:.2f}")
            with col3:
                st.metric("Avg Damage (overall)", f"{avg_overall:.2f}")
            
            chart = plot_distribution(dist, f"Damage distribution for {attack_dice} vs AC {attack_ac}")
            st.altair_chart(chart, use_container_width=True)
            
        except ValueError as e:
            st.error(f"Error: {e}")

st.markdown("---")
st.markdown("Built for D&D 5th Edition | [GitHub](https://github.com/yourusername/dnd-damage-calculator)")

